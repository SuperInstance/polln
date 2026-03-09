"""
Memory Profiler
Profile memory usage, detect leaks, analyze fragmentation, and track KV-cache usage.
"""

import gc
import sys
import time
import tracemalloc
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import threading
from collections import defaultdict

import psutil

from utils.metrics import MetricsCollector
from utils.formatters import format_bytes, format_duration, format_table


@dataclass
class MemorySnapshot:
    """A snapshot of memory state at a point in time."""
    timestamp: float
    rss_bytes: int
    vms_bytes: int
    heap_bytes: int
    kv_cache_bytes: int
    model_memory_bytes: int
    fragmentation_ratio: float


@dataclass
class MemoryLeak:
    """A detected memory leak."""
    object_type: str
    allocation_count: int
    total_bytes: int
    growth_rate: float  # bytes per second
    confidence: float  # 0-1


@dataclass
class MemoryProfile:
    """Complete memory profiling results."""
    duration_seconds: float
    peak_rss_bytes: int
    peak_heap_bytes: int
    current_rss_bytes: int
    current_heap_bytes: int

    # KV-cache stats
    kv_cache_usage_bytes: int
    kv_cache_fragmentation: float

    # Model memory
    model_memory_bytes: int
    model_memory_mb: float

    # Leaks
    suspected_leaks: List[MemoryLeak]

    # Fragmentation
    fragmentation_ratio: float
    fragmentation_count: int

    # GC pressure
    gc_collections: Dict[str, int]
    gc_time_seconds: float

    # Snapshots timeline
    snapshots: List[MemorySnapshot]


class MemoryProfiler:
    """
    Profile memory usage in POLLN systems.

    Tracks:
    - Heap allocations and deallocations
    - KV-cache usage patterns
    - Model memory footprint
    - Memory leaks (growing allocations)
    - Fragmentation and GC pressure

    Usage:
        profiler = MemoryProfiler()
        await profiler.start_profiling()

        # ... run workload ...

        profile = await profiler.stop_profiling()
        report = profiler.generate_report(profile)
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        snapshot_interval: float = 1.0,
        track_gc: bool = True
    ):
        """
        Initialize the memory profiler.

        Args:
            output_dir: Directory to save profiling reports
            snapshot_interval: Seconds between memory snapshots
            track_gc: Whether to track garbage collection
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.snapshot_interval = snapshot_interval
        self.track_gc = track_gc

        self._is_profiling = False
        self._profile_task = None
        self._process = psutil.Process()

        # Tracking
        self._snapshots: List[MemorySnapshot] = []
        self._gc_stats: Dict[str, int] = defaultdict(int)
        self._gc_start_time: Optional[float] = None

        # Allocation tracking
        self._allocations: Dict[str, List[Tuple[float, int]]] = defaultdict(list)
        self._object_counts: Dict[str, List[Tuple[float, int]]] = defaultdict(list)

        # KV-cache tracking
        self._kv_cache_sizes: List[Tuple[float, int]] = []

        # Lock
        self._lock = threading.RLock()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def start_profiling(self, track_allocations: bool = True) -> None:
        """
        Start memory profiling.

        Args:
            track_allocations: Whether to track individual allocations
        """
        with self._lock:
            if self._is_profiling:
                raise RuntimeError("Profiling already in progress")

            self._is_profiling = True
            self._snapshots.clear()
            self._allocations.clear()
            self._object_counts.clear()
            self._kv_cache_sizes.clear()

            if track_allocations:
                tracemalloc.start()

            if self.track_gc:
                gc.set_debug(gc.DEBUG_STATS)
                self._gc_start_time = time.time()
                # Reset GC counters
                for gen in range(3):
                    self._gc_stats[f'gen_{gen}'] = 0

        self._profile_task = asyncio.create_task(
            self._profiling_loop()
        )

    async def stop_profiling(self) -> MemoryProfile:
        """
        Stop profiling and analyze results.

        Returns:
            MemoryProfile with analysis
        """
        with self._lock:
            if not self._is_profiling:
                raise RuntimeError("No profiling in progress")

            self._is_profiling = False

        if self._profile_task:
            self._profile_task.cancel()
            try:
                await self._profile_task
            except asyncio.CancelledError:
                pass

        # Stop tracking
        if tracemalloc.is_tracing():
            tracemalloc.stop()

        # Analyze results
        return self._analyze_profile()

    async def _profiling_loop(self) -> None:
        """Main profiling loop that takes snapshots."""
        while self._is_profiling:
            try:
                snapshot = self._take_snapshot()
                with self._lock:
                    self._snapshots.append(snapshot)

                await asyncio.sleep(self.snapshot_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in memory profiling loop: {e}")
                await asyncio.sleep(self.snapshot_interval)

    def _take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        memory_info = self._process.memory_info()

        # Get heap size if tracing
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            heap_bytes = current
        else:
            heap_bytes = 0

        return MemorySnapshot(
            timestamp=time.time(),
            rss_bytes=memory_info.rss,
            vms_bytes=memory_info.vms,
            heap_bytes=heap_bytes,
            kv_cache_bytes=self._estimate_kv_cache_size(),
            model_memory_bytes=self._estimate_model_memory(),
            fragmentation_ratio=self._calculate_fragmentation_ratio(),
        )

    def _estimate_kv_cache_size(self) -> int:
        """
        Estimate KV-cache memory usage.

        This is a heuristic estimation. For accurate measurements,
        integrate with the actual KV-cache implementation.
        """
        # Look for common KV-cache patterns in memory
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            kv_cache_size = 0

            for stat in snapshot.statistics('traceback'):
                # Look for KV-cache related allocations
                trace_str = str(stat.traceback)
                if any(keyword in trace_str.lower() for keyword in
                       ['kv', 'cache', 'anchor', 'attention', 'key', 'value']):
                    kv_cache_size += stat.size

            return kv_cache_size

        return 0

    def _estimate_model_memory(self) -> int:
        """
        Estimate model memory usage.

        This looks for common ML framework allocations.
        """
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            model_memory = 0

            for stat in snapshot.statistics('traceback'):
                trace_str = str(stat.traceback)
                if any(keyword in trace_str.lower() for keyword in
                       ['torch', 'tensor', 'parameter', 'model', 'layer']):
                    model_memory += stat.size

            return model_memory

        return 0

    def _calculate_fragmentation_ratio(self) -> float:
        """
        Calculate memory fragmentation ratio.

        Higher values indicate more fragmentation.
        """
        if not tracemalloc.is_tracing():
            return 0.0

        current, peak = tracemalloc.get_traced_memory()
        if peak == 0:
            return 0.0

        # Fragmentation is the gap between peak and current
        return (peak - current) / peak

    def track_kv_cache_allocation(self, size_bytes: int) -> None:
        """Track a KV-cache allocation."""
        with self._lock:
            self._kv_cache_sizes.append((time.time(), size_bytes))

    def track_allocation(
        self,
        object_type: str,
        size_bytes: int,
        count: int = 1
    ) -> None:
        """
        Track an object allocation.

        Args:
            object_type: Type of object allocated
            size_bytes: Size in bytes
            count: Number of objects
        """
        with self._lock:
            self._allocations[object_type].append((time.time(), size_bytes))
            self._object_counts[object_type].append((time.time(), count))

    def _analyze_profile(self) -> MemoryProfile:
        """Analyze collected profiling data."""
        if not self._snapshots:
            raise ValueError("No snapshots collected")

        # Calculate duration
        duration = self._snapshots[-1].timestamp - self._snapshots[0].timestamp

        # Calculate peaks
        peak_rss = max(s.rss_bytes for s in self._snapshots)
        peak_heap = max(s.heap_bytes for s in self._snapshots)

        # Current values
        current = self._snapshots[-1]

        # Detect leaks
        suspected_leaks = self._detect_leaks()

        # Calculate fragmentation
        fragmentation_ratios = [s.fragmentation_ratio for s in self._snapshots]
        avg_fragmentation = sum(fragmentation_ratios) / len(fragmentation_ratios)
        high_fragmentation_count = sum(1 for r in fragmentation_ratios if r > 0.3)

        # GC stats
        gc_time = 0
        if self.track_gc and self._gc_start_time:
            gc_time = time.time() - self._gc_start_time

        # KV-cache stats
        kv_cache_sizes = [s.kv_cache_bytes for s in self._snapshots]
        kv_cache_usage = kv_cache_sizes[-1] if kv_cache_sizes else 0

        # Model memory
        model_memory = current.model_memory_bytes

        return MemoryProfile(
            duration_seconds=duration,
            peak_rss_bytes=peak_rss,
            peak_heap_bytes=peak_heap,
            current_rss_bytes=current.rss_bytes,
            current_heap_bytes=current.heap_bytes,
            kv_cache_usage_bytes=kv_cache_usage,
            kv_cache_fragmentation=current.fragmentation_ratio,
            model_memory_bytes=model_memory,
            model_memory_mb=model_memory / 1024 / 1024,
            suspected_leaks=suspected_leaks,
            fragmentation_ratio=avg_fragmentation,
            fragmentation_count=high_fragmentation_count,
            gc_collections=dict(self._gc_stats),
            gc_time_seconds=gc_time,
            snapshots=self._snapshots.copy(),
        )

    def _detect_leaks(
        self,
        min_samples: int = 5,
        growth_threshold: float = 1000  # bytes per second
    ) -> List[MemoryLeak]:
        """
        Detect memory leaks from allocation patterns.

        A leak is suspected when:
        1. An object type shows consistent growth
        2. Growth rate is significant
        """
        leaks = []

        for obj_type, allocations in self._allocations.items():
            if len(allocations) < min_samples:
                continue

            # Calculate growth rate
            # Group allocations by time windows
            time_windows: Dict[float, int] = defaultdict(int)
            window_size = 1.0  # 1 second windows

            for timestamp, size in allocations:
                window = int(timestamp // window_size)
                time_windows[window] += size

            if len(time_windows) < 2:
                continue

            # Calculate linear growth rate
            windows_sorted = sorted(time_windows.items())
            times = [w for w, _ in windows_sorted]
            sizes = [s for _, s in windows_sorted]

            # Simple linear regression
            n = len(times)
            sum_x = sum(times)
            sum_y = sum(sizes)
            sum_xy = sum(t * s for t, s in zip(times, sizes))
            sum_x2 = sum(t * t for t in times)

            if n * sum_x2 - sum_x * sum_x == 0:
                continue

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            # Calculate R-squared for confidence
            mean_y = sum_y / n
            ss_tot = sum((y - mean_y) ** 2 for y in sizes)
            ss_res = sum((sizes[i] - (slope * times[i] + (sum_y - slope * sum_x) / n)) ** 2
                        for i in range(n))

            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Check if this is a suspected leak
            if slope > growth_threshold and r_squared > 0.5:
                total_bytes = sum(sizes)

                leaks.append(MemoryLeak(
                    object_type=obj_type,
                    allocation_count=len(allocations),
                    total_bytes=total_bytes,
                    growth_rate=slope,
                    confidence=r_squared,
                ))

        # Sort by growth rate
        leaks.sort(key=lambda l: l.growth_rate, reverse=True)

        return leaks[:20]

    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        memory_info = self._process.memory_info()

        stats = {
            'rss_bytes': memory_info.rss,
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_bytes': memory_info.vms,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self._process.memory_percent(),
        }

        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            stats['heap_current_mb'] = current / 1024 / 1024
            stats['heap_peak_mb'] = peak / 1024 / 1024

        return stats

    def generate_report(
        self,
        profile: Optional[MemoryProfile] = None,
        format: str = 'json'
    ) -> str:
        """
        Generate profiling report.

        Args:
            profile: MemoryProfile (runs analysis if None)
            format: Report format ('json', 'text', 'html')

        Returns:
            Path to generated report
        """
        if profile is None:
            profile = self._analyze_profile()

        if format == 'json':
            return self._generate_json_report(profile)
        elif format == 'text':
            return self._generate_text_report(profile)
        elif format == 'html':
            return self._generate_html_report(profile)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_json_report(self, profile: MemoryProfile) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"memory_profile_{timestamp}.json"

        report_data = asdict(profile)

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def _generate_text_report(self, profile: MemoryProfile) -> str:
        """Generate human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"memory_profile_{timestamp}.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("MEMORY PROFILING REPORT")
        lines.append("=" * 80)
        lines.append(f"Duration: {format_duration(profile.duration_seconds)}")
        lines.append("")

        # General stats
        lines.append("Memory Usage:")
        lines.append(f"  Peak RSS: {format_bytes(profile.peak_rss_bytes)}")
        lines.append(f"  Current RSS: {format_bytes(profile.current_rss_bytes)}")
        lines.append(f"  Peak Heap: {format_bytes(profile.peak_heap_bytes)}")
        lines.append(f"  Current Heap: {format_bytes(profile.current_heap_bytes)}")
        lines.append("")

        # KV-cache
        lines.append("KV-Cache:")
        lines.append(f"  Usage: {format_bytes(profile.kv_cache_usage_bytes)}")
        lines.append(f"  Fragmentation: {profile.kv_cache_fragmentation:.2%}")
        lines.append("")

        # Model memory
        lines.append("Model Memory:")
        lines.append(f"  Usage: {format_bytes(profile.model_memory_bytes)}")
        lines.append(f"  ({profile.model_memory_mb:.2f} MB)")
        lines.append("")

        # Fragmentation
        lines.append("Fragmentation:")
        lines.append(f"  Ratio: {profile.fragmentation_ratio:.2%}")
        lines.append(f"  High Frag Events: {profile.fragmentation_count}")
        lines.append("")

        # GC
        lines.append("Garbage Collection:")
        lines.append(f"  Time: {format_duration(profile.gc_time_seconds)}")
        for gen, count in profile.gc_collections.items():
            lines.append(f"  {gen}: {count} collections")
        lines.append("")

        # Leaks
        if profile.suspected_leaks:
            lines.append("Suspected Memory Leaks:")
            for i, leak in enumerate(profile.suspected_leaks[:10], 1):
                lines.append(f"  {i}. {leak.object_type}")
                lines.append(f"     Growth: {leak.growth_rate:.0f} bytes/sec")
                lines.append(f"     Total: {format_bytes(leak.total_bytes)}")
                lines.append(f"     Confidence: {leak.confidence:.0%}")
            lines.append("")

        lines.append("=" * 80)

        report_text = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def _generate_html_report(self, profile: MemoryProfile) -> str:
        """Generate interactive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"memory_profile_{timestamp}.html"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Memory Profiling Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; }}
        .metric {{ margin: 10px 0; }}
        .label {{ font-weight: bold; }}
        .value {{ color: #0066cc; }}
        .warning {{ color: #ff6600; }}
        .danger {{ color: #cc0000; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Memory Profiling Report</h1>
    <p>Duration: {format_duration(profile.duration_seconds)}</p>

    <div class="section">
        <h2>Memory Usage</h2>
        <div class="metric"><span class="label">Peak RSS:</span> <span class="value">{format_bytes(profile.peak_rss_bytes)}</span></div>
        <div class="metric"><span class="label">Current RSS:</span> <span class="value">{format_bytes(profile.current_rss_bytes)}</span></div>
        <div class="metric"><span class="label">Peak Heap:</span> <span class="value">{format_bytes(profile.peak_heap_bytes)}</span></div>
        <div class="metric"><span class="label">Current Heap:</span> <span class="value">{format_bytes(profile.current_heap_bytes)}</span></div>
    </div>

    <div class="section">
        <h2>KV-Cache</h2>
        <div class="metric"><span class="label">Usage:</span> <span class="value">{format_bytes(profile.kv_cache_usage_bytes)}</span></div>
        <div class="metric"><span class="label">Fragmentation:</span>
            <span class="value {'warning' if profile.kv_cache_fragmentation > 0.2 else ''}">
                {profile.kv_cache_fragmentation:.2%}
            </span>
        </div>
    </div>

    <div class="section">
        <h2>Model Memory</h2>
        <div class="metric"><span class="label">Usage:</span> <span class="value">{format_bytes(profile.model_memory_bytes)}</span></div>
        <div class="metric"><span class="label">Size:</span> <span class="value">{profile.model_memory_mb:.2f} MB</span></div>
    </div>

    <div class="section">
        <h2>Fragmentation</h2>
        <div class="metric"><span class="label">Ratio:</span>
            <span class="value {'warning' if profile.fragmentation_ratio > 0.3 else 'danger' if profile.fragmentation_ratio > 0.5 else ''}">
                {profile.fragmentation_ratio:.2%}
            </span>
        </div>
        <div class="metric"><span class="label">High Frag Events:</span> <span class="value">{profile.fragmentation_count}</span></div>
    </div>

    <div class="section">
        <h2>Garbage Collection</h2>
        <div class="metric"><span class="label">Time:</span> <span class="value">{format_duration(profile.gc_time_seconds)}</span></div>
        {self._generate_gc_rows(profile.gc_collections)}
    </div>

    {self._generate_leaks_section(profile.suspected_leaks)}

</body>
</html>
        """

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)

    def _generate_gc_rows(self, gc_collections: Dict[str, int]) -> str:
        """Generate HTML for GC stats."""
        rows = []
        for gen, count in gc_collections.items():
            rows.append(f'<div class="metric"><span class="label">{gen}:</span> <span class="value">{count} collections</span></div>')
        return "\n".join(rows)

    def _generate_leaks_section(self, leaks: List[MemoryLeak]) -> str:
        """Generate HTML for leaks section."""
        if not leaks:
            return '<div class="section"><h2>Suspected Leaks</h2><p>No suspected leaks detected.</p></div>'

        rows = []
        for leak in leaks[:10]:
            rows.append(f"<tr><td>{leak.object_type}</td>"
                       f"<td>{leak.growth_rate:.0f} bytes/sec</td>"
                       f"<td>{format_bytes(leak.total_bytes)}</td>"
                       f"<td>{leak.confidence:.0%}</td></tr>")

        return f'''
    <div class="section">
        <h2>Suspected Memory Leaks</h2>
        <table>
            <tr><th>Type</th><th>Growth Rate</th><th>Total</th><th>Confidence</th></tr>
            {''.join(rows)}
        </table>
    </div>
    '''

    def generate_heap_histogram(
        self,
        limit: int = 50,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a heap histogram showing allocation by type.

        Args:
            limit: Maximum number of types to show
            output_path: Output file path

        Returns:
            Path to generated file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"heap_histogram_{timestamp}.txt")

        if not tracemalloc.is_tracing():
            raise RuntimeError("Memory tracing not enabled")

        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics('traceback')

        # Group by file/line
        by_location: Dict[str, int] = defaultdict(int)
        for stat in stats:
            by_location[str(stat.traceback)] += stat.size

        # Sort by size
        sorted_locations = sorted(by_location.items(), key=lambda x: x[1], reverse=True)

        lines = []
        lines.append("Heap Histogram (Top Allocations)")
        lines.append("=" * 80)
        lines.append("")

        for i, (location, size) in enumerate(sorted_locations[:limit], 1):
            lines.append(f"{i:3}. {format_bytes(size)}")
            lines.append(f"     {location}")
            lines.append("")

        with open(output_path, 'w') as f:
            f.write("\n".join(lines))

        return output_path

    def clear(self) -> None:
        """Clear all collected data."""
        with self._lock:
            self._snapshots.clear()
            self._gc_stats.clear()
            self._allocations.clear()
            self._object_counts.clear()
            self._kv_cache_sizes.clear()


# Import asyncio for async support
import asyncio
import json
