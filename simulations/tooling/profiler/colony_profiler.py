"""
Colony Profiler
Profile colony-level metrics: throughput, latency, queue depths, resource allocation.
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import threading
import statistics

from utils.metrics import MetricsCollector
from utils.formatters import (
    format_duration, format_bytes, format_metrics,
    format_table, format_percent
)


@dataclass
class ColonyProfile:
    """Profile data for a colony."""
    colony_id: str
    timestamp: float

    # Agent counts
    total_agents: int
    active_agents: int
    dormant_agents: int
    hibernating_agents: int
    error_agents: int

    # Resource usage
    total_compute: float
    total_memory: float
    total_network: float
    avg_compute_per_agent: float
    avg_memory_per_agent: float

    # Throughput metrics
    requests_per_second: float
    a2a_packages_per_second: float
    bytes_per_second: float

    # Latency metrics
    p50_latency: float
    p90_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float

    # Queue depths
    avg_queue_depth: float
    max_queue_depth: float
    queue_depth_percentiles: Dict[str, float]

    # Topology metrics
    shannon_diversity: float
    avg_connections_per_agent: float
    max_connections_per_agent: int

    # Evolution metrics
    agents_spawned: int
    agents_killed: int
    topology_changes: int

    # Timeline
    duration_seconds: float


class ColonyProfiler:
    """
    Profiles POLLN colonies at the system level.

    Tracks:
    - Throughput (requests/sec, A2A packages/sec)
    - Latency distributions (p50, p90, p95, p99)
    - Queue depths and congestion
    - Resource allocation and utilization
    - Topology changes and agent churn
    - Shannon diversity of agent types

    Usage:
        profiler = ColonyProfiler()
        await profiler.start_profiling(colony)

        # ... run workload ...

        profile = await profiler.stop_profiling()
        report = profiler.generate_report()
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        sample_interval: float = 0.1,
        history_size: int = 10000
    ):
        """
        Initialize the colony profiler.

        Args:
            output_dir: Directory to save profiling reports
            sample_interval: Sampling interval in seconds
            history_size: Maximum samples to keep in history
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.sample_interval = sample_interval
        self.history_size = history_size

        self._metrics = MetricsCollector()
        self._is_profiling = False
        self._profile_task = None

        # Time series data
        self._throughput_history: deque = deque(maxlen=history_size)
        self._latency_history: deque = deque(maxlen=history_size)
        self._queue_depth_history: deque = deque(maxlen=history_size)
        self._agent_count_history: deque = deque(maxlen=history_size)
        self._resource_history: deque = deque(maxlen=history_size)

        # Counters
        self._request_count = 0
        self._a2a_count = 0
        self._bytes_sent = 0
        self._agents_spawned = 0
        self._agents_killed = 0
        self._topology_changes = 0

        # Timing
        self._start_time = None
        self._stop_time = None

        # Lock
        self._lock = threading.RLock()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def start_profiling(self, colony: Any) -> None:
        """
        Start profiling a colony.

        Args:
            colony: The colony to profile
        """
        with self._lock:
            if self._is_profiling:
                raise RuntimeError("Profiling already in progress")

            self._is_profiling = True
            self._start_time = time.time()
            self._reset_counters()

        self._profile_task = asyncio.create_task(
            self._profiling_loop(colony)
        )

    async def stop_profiling(self) -> ColonyProfile:
        """
        Stop profiling and return collected data.

        Returns:
            ColonyProfile with all metrics
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

        self._stop_time = time.time()
        return self._build_profile()

    async def _profiling_loop(self, colony: Any) -> None:
        """Main profiling loop that samples colony metrics."""
        while self._is_profiling:
            try:
                # Sample colony state
                sample = await self._sample_colony(colony)
                self._record_sample(sample)

                await asyncio.sleep(self.sample_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in profiling loop: {e}")
                await asyncio.sleep(self.sample_interval)

    async def _sample_colony(self, colony: Any) -> Dict[str, Any]:
        """Sample current colony state."""
        sample = {
            'timestamp': time.time(),
        }

        # Agent counts
        if hasattr(colony, 'agents'):
            agents = colony.agents
            sample['total_agents'] = len(agents)

            status_counts = defaultdict(int)
            for agent_state in agents.values():
                status = agent_state.get('status', 'unknown')
                status_counts[status] += 1

            sample['active_agents'] = status_counts.get('active', 0)
            sample['dormant_agents'] = status_counts.get('dormant', 0)
            sample['hibernating_agents'] = status_counts.get('hibernating', 0)
            sample['error_agents'] = status_counts.get('error', 0)

        # Resource usage
        if hasattr(colony, 'config'):
            config = colony.config
            if hasattr(config, 'resourceBudget'):
                sample['total_compute'] = config.resourceBudget.totalCompute
                sample['total_memory'] = config.resourceBudget.totalMemory
                sample['total_network'] = config.resourceBudget.totalNetwork

        # Stats if available
        if hasattr(colony, 'getStats'):
            stats = await colony.getStats()
            sample.update(stats)

        return sample

    def _record_sample(self, sample: Dict[str, Any]) -> None:
        """Record a sampled data point."""
        with self._lock:
            self._agent_count_history.append(sample)

    def track_request(self) -> None:
        """Track a request completion."""
        with self._lock:
            self._request_count += 1

    def track_a2a_package(self, size_bytes: int = 0) -> None:
        """Track an A2A package."""
        with self._lock:
            self._a2a_count += 1
            self._bytes_sent += size_bytes

    def track_agent_spawn(self) -> None:
        """Track an agent spawn event."""
        with self._lock:
            self._agents_spawned += 1

    def track_agent_kill(self) -> None:
        """Track an agent kill event."""
        with self._lock:
            self._agents_killed += 1

    def track_topology_change(self) -> None:
        """Track a topology change event."""
        with self._lock:
            self._topology_changes += 1

    def record_latency(self, latency: float) -> None:
        """Record a latency measurement."""
        with self._lock:
            self._latency_history.append({
                'timestamp': time.time(),
                'latency': latency
            })

    def record_queue_depth(self, depth: int, agent_id: str = 'global') -> None:
        """Record a queue depth measurement."""
        with self._lock:
            self._queue_depth_history.append({
                'timestamp': time.time(),
                'depth': depth,
                'agent_id': agent_id
            })

    def _reset_counters(self) -> None:
        """Reset all counters."""
        self._request_count = 0
        self._a2a_count = 0
        self._bytes_sent = 0
        self._agents_spawned = 0
        self._agents_killed = 0
        self._topology_changes = 0

    def _calculate_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles from history."""
        latencies = [s['latency'] for s in self._latency_history]

        if not latencies:
            return {
                'p50': 0.0,
                'p90': 0.0,
                'p95': 0.0,
                'p99': 0.0,
                'max': 0.0,
            }

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        return {
            'p50': sorted_latencies[int(n * 0.50)],
            'p90': sorted_latencies[int(n * 0.90)],
            'p95': sorted_latencies[int(n * 0.95)],
            'p99': sorted_latencies[int(n * 0.99)] if n >= 100 else sorted_latencies[-1],
            'max': sorted_latencies[-1],
        }

    def _calculate_queue_stats(self) -> Dict[str, float]:
        """Calculate queue depth statistics."""
        depths = [s['depth'] for s in self._queue_depth_history]

        if not depths:
            return {
                'avg': 0.0,
                'max': 0.0,
                'p50': 0.0,
                'p90': 0.0,
                'p95': 0.0,
            }

        sorted_depths = sorted(depths)
        n = len(sorted_depths)

        return {
            'avg': statistics.mean(depths),
            'max': max(depths),
            'p50': sorted_depths[int(n * 0.50)],
            'p90': sorted_depths[int(n * 0.90)],
            'p95': sorted_depths[int(n * 0.95)],
        }

    def _build_profile(self) -> ColonyProfile:
        """Build a ColonyProfile from collected data."""
        duration = (self._stop_time or time.time()) - (self._start_time or time.time())

        # Get latest sample
        latest_sample = None
        if self._agent_count_history:
            latest_sample = self._agent_count_history[-1]

        if latest_sample is None:
            latest_sample = {}

        # Calculate throughput
        requests_per_sec = self._request_count / duration if duration > 0 else 0
        a2a_per_sec = self._a2a_count / duration if duration > 0 else 0
        bytes_per_sec = self._bytes_sent / duration if duration > 0 else 0

        # Calculate latency percentiles
        latency_p = self._calculate_latency_percentiles()

        # Calculate queue stats
        queue_stats = self._calculate_queue_stats()

        # Calculate resource per agent
        total_agents = latest_sample.get('total_agents', 0)
        if total_agents > 0:
            avg_compute = latest_sample.get('total_compute', 0) / total_agents
            avg_memory = latest_sample.get('total_memory', 0) / total_agents
        else:
            avg_compute = 0
            avg_memory = 0

        return ColonyProfile(
            colony_id=latest_sample.get('colony_id', 'unknown'),
            timestamp=self._start_time or time.time(),

            # Agent counts
            total_agents=latest_sample.get('total_agents', 0),
            active_agents=latest_sample.get('active_agents', 0),
            dormant_agents=latest_sample.get('dormant_agents', 0),
            hibernating_agents=latest_sample.get('hibernating_agents', 0),
            error_agents=latest_sample.get('error_agents', 0),

            # Resource usage
            total_compute=latest_sample.get('total_compute', 0),
            total_memory=latest_sample.get('total_memory', 0),
            total_network=latest_sample.get('total_network', 0),
            avg_compute_per_agent=avg_compute,
            avg_memory_per_agent=avg_memory,

            # Throughput
            requests_per_second=requests_per_sec,
            a2a_packages_per_second=a2a_per_sec,
            bytes_per_second=bytes_per_sec,

            # Latency
            p50_latency=latency_p['p50'],
            p90_latency=latency_p['p90'],
            p95_latency=latency_p['p95'],
            p99_latency=latency_p['p99'],
            max_latency=latency_p['max'],

            # Queue depths
            avg_queue_depth=queue_stats['avg'],
            max_queue_depth=queue_stats['max'],
            queue_depth_percentiles={
                'p50': queue_stats['p50'],
                'p90': queue_stats['p90'],
                'p95': queue_stats['p95'],
            },

            # Topology
            shannon_diversity=latest_sample.get('shannonDiversity', 0),
            avg_connections_per_agent=latest_sample.get('avgConnections', 0),
            max_connections_per_agent=latest_sample.get('maxConnections', 0),

            # Evolution
            agents_spawned=self._agents_spawned,
            agents_killed=self._agents_killed,
            topology_changes=self._topology_changes,

            # Timeline
            duration_seconds=duration,
        )

    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get current realtime metrics."""
        with self._lock:
            if not self._agent_count_history:
                return {}

            latest = self._agent_count_history[-1]
            duration = time.time() - (self._start_time or time.time())

            return {
                'timestamp': latest['timestamp'],
                'uptime_seconds': duration,
                'agents': {
                    'total': latest.get('total_agents', 0),
                    'active': latest.get('active_agents', 0),
                    'dormant': latest.get('dormant_agents', 0),
                },
                'throughput': {
                    'requests_per_sec': self._request_count / duration if duration > 0 else 0,
                    'a2a_per_sec': self._a2a_count / duration if duration > 0 else 0,
                },
                'latency': self._calculate_latency_percentiles(),
                'queues': self._calculate_queue_stats(),
            }

    def generate_report(
        self,
        profile: Optional[ColonyProfile] = None,
        format: str = 'json'
    ) -> str:
        """
        Generate a profiling report.

        Args:
            profile: Profile to report (uses latest if None)
            format: Report format ('json', 'text', 'html')

        Returns:
            Report file path
        """
        if profile is None:
            profile = self._build_profile()

        if format == 'json':
            return self._generate_json_report(profile)
        elif format == 'text':
            return self._generate_text_report(profile)
        elif format == 'html':
            return self._generate_html_report(profile)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_json_report(self, profile: ColonyProfile) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"colony_profile_{timestamp}.json"

        report_data = asdict(profile)

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def _generate_text_report(self, profile: ColonyProfile) -> str:
        """Generate human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"colony_profile_{timestamp}.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("COLONY PROFILING REPORT")
        lines.append("=" * 80)
        lines.append(f"Colony ID: {profile.colony_id}")
        lines.append(f"Duration: {format_duration(profile.duration_seconds)}")
        lines.append("")

        # Agent counts
        lines.append("Agent Counts:")
        lines.append(f"  Total: {profile.total_agents}")
        lines.append(f"  Active: {profile.active_agents} ({format_percent(profile.active_agents, profile.total_agents)})")
        lines.append(f"  Dormant: {profile.dormant_agents}")
        lines.append(f"  Hibernating: {profile.hibernating_agents}")
        lines.append(f"  Error: {profile.error_agents}")
        lines.append("")

        # Throughput
        lines.append("Throughput:")
        lines.append(f"  Requests: {profile.requests_per_second:.2f}/sec")
        lines.append(f"  A2A Packages: {profile.a2a_packages_per_second:.2f}/sec")
        lines.append(f"  Bandwidth: {format_bytes(int(profile.bytes_per_second))}/sec")
        lines.append("")

        # Latency
        lines.append("Latency:")
        lines.append(f"  p50: {format_duration(profile.p50_latency)}")
        lines.append(f"  p90: {format_duration(profile.p90_latency)}")
        lines.append(f"  p95: {format_duration(profile.p95_latency)}")
        lines.append(f"  p99: {format_duration(profile.p99_latency)}")
        lines.append(f"  Max: {format_duration(profile.max_latency)}")
        lines.append("")

        # Queues
        lines.append("Queue Depths:")
        lines.append(f"  Average: {profile.avg_queue_depth:.2f}")
        lines.append(f"  Maximum: {profile.max_queue_depth}")
        lines.append(f"  p90: {profile.queue_depth_percentiles['p90']:.2f}")
        lines.append("")

        # Topology
        lines.append("Topology:")
        lines.append(f"  Shannon Diversity: {profile.shannon_diversity:.3f}")
        lines.append(f"  Avg Connections: {profile.avg_connections_per_agent:.2f}")
        lines.append(f"  Max Connections: {profile.max_connections_per_agent}")
        lines.append("")

        # Evolution
        lines.append("Evolution:")
        lines.append(f"  Agents Spawned: {profile.agents_spawned}")
        lines.append(f"  Agents Killed: {profile.agents_killed}")
        lines.append(f"  Topology Changes: {profile.topology_changes}")
        lines.append("")

        lines.append("=" * 80)

        report_text = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def _generate_html_report(self, profile: ColonyProfile) -> str:
        """Generate interactive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"colony_profile_{timestamp}.html"

        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Colony Profiling Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; }}
        .metric {{ margin: 10px 0; }}
        .label {{ font-weight: bold; }}
        .value {{ color: #0066cc; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 800px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Colony Profiling Report</h1>
    <p><strong>Colony ID:</strong> {colony_id}</p>
    <p><strong>Duration:</strong> {duration}</p>

    <div class="section">
        <h2>Agent Counts</h2>
        <div class="metric"><span class="label">Total:</span> <span class="value">{total_agents}</span></div>
        <div class="metric"><span class="label">Active:</span> <span class="value">{active_agents} ({active_percent}%)</span></div>
        <div class="metric"><span class="label">Dormant:</span> <span class="value">{dormant_agents}</span></div>
        <div class="metric"><span class="label">Hibernating:</span> <span class="value">{hibernating_agents}</span></div>
        <div class="metric"><span class="label">Error:</span> <span class="value">{error_agents}</span></div>
    </div>

    <div class="section">
        <h2>Throughput</h2>
        <div class="metric"><span class="label">Requests:</span> <span class="value">{rps:.2f}/sec</span></div>
        <div class="metric"><span class="label">A2A Packages:</span> <span class="value">{a2a_ps:.2f}/sec</span></div>
        <div class="metric"><span class="label">Bandwidth:</span> <span class="value">{bw}/sec</span></div>
    </div>

    <div class="section">
        <h2>Latency</h2>
        <div class="metric"><span class="label">p50:</span> <span class="value">{p50}</span></div>
        <div class="metric"><span class="label">p90:</span> <span class="value">{p90}</span></div>
        <div class="metric"><span class="label">p95:</span> <span class="value">{p95}</span></div>
        <div class="metric"><span class="label">p99:</span> <span class="value">{p99}</span></div>
        <div class="metric"><span class="label">Max:</span> <span class="value">{max}</span></div>
    </div>

    <div class="section">
        <h2>Queue Depths</h2>
        <div class="metric"><span class="label">Average:</span> <span class="value">{avg_q:.2f}</span></div>
        <div class="metric"><span class="label">Maximum:</span> <span class="value">{max_q}</span></div>
        <div class="metric"><span class="label">p90:</span> <span class="value">{p90_q:.2f}</span></div>
    </div>

    <div class="section">
        <h2>Topology</h2>
        <div class="metric"><span class="label">Shannon Diversity:</span> <span class="value">{shannon:.3f}</span></div>
        <div class="metric"><span class="label">Avg Connections:</span> <span class="value">{avg_conn:.2f}</span></div>
        <div class="metric"><span class="label">Max Connections:</span> <span class="value">{max_conn}</span></div>
    </div>

    <div class="section">
        <h2>Evolution</h2>
        <div class="metric"><span class="label">Agents Spawned:</span> <span class="value">{spawned}</span></div>
        <div class="metric"><span class="label">Agents Killed:</span> <span class="value">{killed}</span></div>
        <div class="metric"><span class="label">Topology Changes:</span> <span class="value">{topo_changes}</span></div>
    </div>

</body>
</html>
        """

        html_content = html.format(
            colony_id=profile.colony_id,
            duration=format_duration(profile.duration_seconds),
            total_agents=profile.total_agents,
            active_agents=profile.active_agents,
            active_percent=format_percent(profile.active_agents, profile.total_agents),
            dormant_agents=profile.dormant_agents,
            hibernating_agents=profile.hibernating_agents,
            error_agents=profile.error_agents,
            rps=profile.requests_per_second,
            a2a_ps=profile.a2a_packages_per_second,
            bw=format_bytes(int(profile.bytes_per_second)),
            p50=format_duration(profile.p50_latency),
            p90=format_duration(profile.p90_latency),
            p95=format_duration(profile.p95_latency),
            p99=format_duration(profile.p99_latency),
            max=format_duration(profile.max_latency),
            avg_q=profile.avg_queue_depth,
            max_q=int(profile.max_queue_depth),
            p90_q=profile.queue_depth_percentiles['p90'],
            shannon=profile.shannon_diversity,
            avg_conn=profile.avg_connections_per_agent,
            max_conn=profile.max_connections_per_agent,
            spawned=profile.agents_spawned,
            killed=profile.agents_killed,
            topo_changes=profile.topology_changes,
        )

        with open(filepath, 'w') as f:
            f.write(html_content)

        return str(filepath)

    def clear(self) -> None:
        """Clear all collected data."""
        with self._lock:
            self._throughput_history.clear()
            self._latency_history.clear()
            self._queue_depth_history.clear()
            self._agent_count_history.clear()
            self._resource_history.clear()
            self._reset_counters()
            self._metrics.clear()
