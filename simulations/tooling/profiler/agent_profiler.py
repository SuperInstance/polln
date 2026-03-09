"""
Agent Profiler
Profile individual agents for CPU, memory, and A2A communication patterns.
"""

import asyncio
import cProfile
import io
import json
import pstats
import sys
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import psutil
import threading

from utils.metrics import MetricsCollector, MetricSample
from utils.formatters import (
    format_duration, format_bytes, format_metrics,
    format_table, format_speedup
)


@dataclass
class AgentProfile:
    """Profile data for a single agent."""
    agent_id: str
    agent_type: str
    timestamp: float

    # CPU metrics
    cpu_percent: float
    cpu_time_user: float
    cpu_time_system: float

    # Memory metrics
    memory_rss_bytes: int
    memory_vms_bytes: int
    memory_mb: float
    memory_peak_mb: float

    # A2A communication
    a2a_sent_count: int
    a2a_received_count: int
    a2a_sent_bytes: int
    a2a_received_bytes: int

    # Execution metrics
    process_count: int
    total_process_time: float
    avg_process_time: float
    max_process_time: float

    # Value function
    value_function: float
    success_count: int
    failure_count: int

    # Hotspots (from cProfile)
    hotspots: List[Dict[str, Any]] = field(default_factory=list)

    # Memory allocations (from tracemalloc)
    memory_allocations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentHotspot:
    """A performance hotspot identified in profiling."""
    function: str
    call_count: int
    total_time: float
    per_call_time: float
    cumulative_time: float
    percentage: float


class AgentProfiler:
    """
    Profiles individual POLLN agents.

    Tracks:
    - CPU usage and time
    - Memory allocations and leaks
    - A2A communication patterns
    - Method call hotspots
    - Value function evolution

    Usage:
        profiler = AgentProfiler()
        profile = await profiler.profile_agent(agent, workload)

        # Or with context manager
        async with profiler.profile_context(agent) as profile:
            # Agent runs here
            pass
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        enable_cpu_profiling: bool = True,
        enable_memory_profiling: bool = True,
        enable_a2a_tracking: bool = True
    ):
        """
        Initialize the agent profiler.

        Args:
            output_dir: Directory to save profiling reports
            enable_cpu_profiling: Enable cProfile-based CPU profiling
            enable_memory_profiling: Enable tracemalloc memory profiling
            enable_a2a_tracking: Enable A2A communication tracking
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.enable_cpu_profiling = enable_cpu_profiling
        self.enable_memory_profiling = enable_memory_profiling
        self.enable_a2a_tracking = enable_a2a_tracking

        self._profiles: Dict[str, AgentProfile] = {}
        self._metrics = MetricsCollector()

        # A2A tracking
        self._a2a_sent: Dict[str, int] = {}
        self._a2a_received: Dict[str, int] = {}
        self._a2a_sent_bytes: Dict[str, int] = {}
        self._a2a_received_bytes: Dict[str, int] = {}

        # Process tracking
        self._process_times: Dict[str, List[float]] = {}

        # Lock for thread safety
        self._lock = threading.RLock()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def profile_agent(
        self,
        agent: Any,
        workload: Callable,
        iterations: int = 10,
        warmup_iterations: int = 2
    ) -> AgentProfile:
        """
        Profile an agent with a given workload.

        Args:
            agent: The agent to profile
            workload: Async function to run on the agent
            iterations: Number of iterations to run
            warmup_iterations: Warmup iterations (not profiled)

        Returns:
            AgentProfile with profiling results
        """
        agent_id = getattr(agent, 'id', 'unknown')
        agent_type = getattr(agent, 'typeId', type(agent).__name__)

        # Warmup
        for _ in range(warmup_iterations):
            try:
                await workload(agent)
            except Exception:
                pass

        # Start profiling
        if self.enable_memory_profiling:
            tracemalloc.start()

        profiler = cProfile.Profile() if self.enable_cpu_profiling else None
        if profiler:
            profiler.enable()

        # Reset tracking
        with self._lock:
            self._process_times[agent_id] = []
            self._a2a_sent[agent_id] = 0
            self._a2a_received[agent_id] = 0

        # Track process
        process = psutil.Process()
        start_time = time.time()
        start_cpu_user = process.cpu_times().user
        start_cpu_system = process.cpu_times().system
        start_memory = process.memory_info().rss

        # Run iterations
        for i in range(iterations):
            iter_start = time.time()
            try:
                await workload(agent)
            except Exception as e:
                print(f"Error in iteration {i}: {e}", file=sys.stderr)
            iter_time = time.time() - iter_start

            with self._lock:
                self._process_times[agent_id].append(iter_time)

        end_time = time.time()
        end_cpu_user = process.cpu_times().user
        end_cpu_system = process.cpu_times().system
        end_memory = process.memory_info().rss

        # Stop profiling
        if profiler:
            profiler.disable()

        # Collect profile data
        profile = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            timestamp=start_time,

            # CPU metrics
            cpu_percent=process.cpu_percent(),
            cpu_time_user=end_cpu_user - start_cpu_user,
            cpu_time_system=end_cpu_system - start_cpu_system,

            # Memory metrics
            memory_rss_bytes=end_memory,
            memory_vms_bytes=process.memory_info().vms,
            memory_mb=end_memory / 1024 / 1024,
            memory_peak_mb=end_memory / 1024 / 1024,  # Will be updated if tracemalloc enabled

            # A2A communication
            a2a_sent_count=self._a2a_sent.get(agent_id, 0),
            a2a_received_count=self._a2a_received.get(agent_id, 0),
            a2a_sent_bytes=self._a2a_sent_bytes.get(agent_id, 0),
            a2a_received_bytes=self._a2a_received_bytes.get(agent_id, 0),

            # Execution metrics
            process_count=iterations,
            total_process_time=end_time - start_time,
            avg_process_time=sum(self._process_times[agent_id]) / len(self._process_times[agent_id]),
            max_process_time=max(self._process_times[agent_id]),

            # Value function
            value_function=getattr(agent, 'valueFunction', 0.5),
            success_count=getattr(agent, 'successCount', 0),
            failure_count=getattr(agent, 'failureCount', 0),
        )

        # Process CPU profile
        if profiler:
            profile.hotspots = self._extract_hotspots(profiler)

        # Process memory profile
        if self.enable_memory_profiling:
            current, peak = tracemalloc.get_traced_memory()
            profile.memory_peak_mb = peak / 1024 / 1024
            profile.memory_allocations = self._extract_memory_allocations()
            tracemalloc.stop()

        # Store profile
        with self._lock:
            self._profiles[agent_id] = profile

        return profile

    def _extract_hotspots(
        self,
        profiler: cProfile.Profile,
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """Extract top hotspots from cProfile data."""
        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats('cumulative')

        output = io.StringIO()
        stats.print_stats(top_n)
        hotspot_text = output.getvalue()

        hotspots = []
        for line in hotspot_text.split('\n')[1:top_n + 1]:
            if line.strip() and not line.startswith('  '):
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        hotspots.append({
                            'calls': int(parts[1]),
                            'total_time': float(parts[2]),
                            'per_call': float(parts[3]),
                            'cumulative_time': float(parts[4]),
                            'function': ' '.join(parts[5:])
                        })
                    except (ValueError, IndexError):
                        continue

        return hotspots

    def _extract_memory_allocations(
        self,
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """Extract top memory allocations from tracemalloc."""
        if not tracemalloc.is_tracing():
            return []

        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics('lineno')

        allocations = []
        for stat in stats[:top_n]:
            allocations.append({
                'trace': str(stat.traceback),
                'size_bytes': stat.size,
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count,
                'average': stat.size / stat.count if stat.count > 0 else 0
            })

        return allocations

    def track_a2a_send(
        self,
        agent_id: str,
        package_size: int = 0
    ) -> None:
        """Track an A2A package send."""
        if self.enable_a2a_tracking:
            with self._lock:
                self._a2a_sent[agent_id] = self._a2a_sent.get(agent_id, 0) + 1
                self._a2a_sent_bytes[agent_id] = self._a2a_sent_bytes.get(agent_id, 0) + package_size

    def track_a2a_receive(
        self,
        agent_id: str,
        package_size: int = 0
    ) -> None:
        """Track an A2A package receive."""
        if self.enable_a2a_tracking:
            with self._lock:
                self._a2a_received[agent_id] = self._a2a_received.get(agent_id, 0) + 1
                self._a2a_received_bytes[agent_id] = self._a2a_received_bytes.get(agent_id, 0) + package_size

    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get profile for a specific agent."""
        return self._profiles.get(agent_id)

    def get_all_profiles(self) -> Dict[str, AgentProfile]:
        """Get all collected profiles."""
        return self._profiles.copy()

    def compare_agents(
        self,
        agent_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare profiles of multiple agents.

        Returns comparison metrics including:
        - Relative CPU usage
        - Relative memory usage
        - A2A communication comparison
        """
        profiles = [self._profiles.get(aid) for aid in agent_ids]
        profiles = [p for p in profiles if p is not None]

        if len(profiles) < 2:
            return {"error": "Need at least 2 profiles to compare"}

        comparison = {
            'timestamp': time.time(),
            'agents': agent_ids,
            'cpu_comparison': self._compare_metric(profiles, 'cpu_percent'),
            'memory_comparison': self._compare_metric(profiles, 'memory_mb'),
            'process_time_comparison': self._compare_metric(profiles, 'avg_process_time'),
            'a2a_sent_comparison': self._compare_metric(profiles, 'a2a_sent_count'),
            'a2a_received_comparison': self._compare_metric(profiles, 'a2a_received_count'),
        }

        return comparison

    def _compare_metric(
        self,
        profiles: List[AgentProfile],
        metric: str
    ) -> List[Dict[str, Any]]:
        """Compare a specific metric across profiles."""
        values = [(p.agent_id, getattr(p, metric, 0)) for p in profiles]
        max_val = max(v for _, v in values) if values else 0

        return [
            {
                'agent_id': aid,
                'value': val,
                'relative_to_max': val / max_val if max_val > 0 else 0
            }
            for aid, val in values
        ]

    def generate_report(
        self,
        agent_id: Optional[str] = None,
        format: str = 'json'
    ) -> str:
        """
        Generate a profiling report.

        Args:
            agent_id: Specific agent to report (all if None)
            format: Report format ('json', 'text', 'html')

        Returns:
            Report file path
        """
        if agent_id:
            profiles = {agent_id: self._profiles.get(agent_id)}
        else:
            profiles = self._profiles

        if format == 'json':
            return self._generate_json_report(profiles)
        elif format == 'text':
            return self._generate_text_report(profiles)
        elif format == 'html':
            return self._generate_html_report(profiles)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_json_report(
        self,
        profiles: Dict[str, Optional[AgentProfile]]
    ) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"agent_profile_{timestamp}.json"

        report_data = {
            'timestamp': time.time(),
            'profiles': {
                aid: asdict(profile) if profile else None
                for aid, profile in profiles.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def _generate_text_report(
        self,
        profiles: Dict[str, Optional[AgentProfile]]
    ) -> str:
        """Generate human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"agent_profile_{timestamp}.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("AGENT PROFILING REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Agents Profiled: {len([p for p in profiles.values() if p])}")
        lines.append("")

        for agent_id, profile in profiles.items():
            if not profile:
                continue

            lines.append(f"Agent: {profile.agent_id}")
            lines.append(f"Type: {profile.agent_type}")
            lines.append("-" * 80)

            # CPU
            lines.append("\nCPU Usage:")
            lines.append(f"  Percent: {profile.cpu_percent:.2f}%")
            lines.append(f"  User Time: {format_duration(profile.cpu_time_user)}")
            lines.append(f"  System Time: {format_duration(profile.cpu_time_system)}")

            # Memory
            lines.append("\nMemory Usage:")
            lines.append(f"  RSS: {format_bytes(profile.memory_rss_bytes)}")
            lines.append(f"  VMS: {format_bytes(profile.memory_vms_bytes)}")
            lines.append(f"  Current: {profile.memory_mb:.2f} MB")
            lines.append(f"  Peak: {profile.memory_peak_mb:.2f} MB")

            # A2A
            lines.append("\nA2A Communication:")
            lines.append(f"  Sent: {profile.a2a_sent_count} ({format_bytes(profile.a2a_sent_bytes)})")
            lines.append(f"  Received: {profile.a2a_received_count} ({format_bytes(profile.a2a_received_bytes)})")

            # Execution
            lines.append("\nExecution:")
            lines.append(f"  Process Count: {profile.process_count}")
            lines.append(f"  Total Time: {format_duration(profile.total_process_time)}")
            lines.append(f"  Avg Time: {format_duration(profile.avg_process_time)}")
            lines.append(f"  Max Time: {format_duration(profile.max_process_time)}")

            # Value Function
            lines.append("\nValue Function:")
            lines.append(f"  Value: {profile.value_function:.3f}")
            lines.append(f"  Successes: {profile.success_count}")
            lines.append(f"  Failures: {profile.failure_count}")

            # Hotspots
            if profile.hotspots:
                lines.append("\nCPU Hotspots:")
                for i, hotspot in enumerate(profile.hotspots[:10], 1):
                    lines.append(f"  {i}. {hotspot['function']}")
                    lines.append(f"     Calls: {hotspot['calls']}, Time: {format_duration(hotspot['total_time'])}")

            lines.append("\n" + "=" * 80 + "\n")

        report_text = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def _generate_html_report(
        self,
        profiles: Dict[str, Optional[AgentProfile]]
    ) -> str:
        """Generate interactive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"agent_profile_{timestamp}.html"

        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Agent Profiling Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .agent { border: 1px solid #ccc; margin: 20px 0; padding: 15px; border-radius: 5px; }
        .metric { margin: 10px 0; }
        .label { font-weight: bold; }
        .value { color: #0066cc; }
        .hotspot { background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 3px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Agent Profiling Report</h1>
    <p>Generated: {timestamp}</p>
    <p>Agents Profiled: {count}</p>

    {profiles_html}

</body>
</html>
        """

        profiles_html = ""

        for agent_id, profile in profiles.items():
            if not profile:
                continue

            agent_html = f"""
    <div class="agent">
        <h2>{profile.agent_id}</h2>
        <p><strong>Type:</strong> {profile.agent_type}</p>

        <h3>CPU Usage</h3>
        <div class="metric"><span class="label">Percent:</span> <span class="value">{profile.cpu_percent:.2f}%</span></div>
        <div class="metric"><span class="label">User Time:</span> <span class="value">{format_duration(profile.cpu_time_user)}</span></div>
        <div class="metric"><span class="label">System Time:</span> <span class="value">{format_duration(profile.cpu_time_system)}</span></div>

        <h3>Memory Usage</h3>
        <div class="metric"><span class="label">RSS:</span> <span class="value">{format_bytes(profile.memory_rss_bytes)}</span></div>
        <div class="metric"><span class="label">VMS:</span> <span class="value">{format_bytes(profile.memory_vms_bytes)}</span></div>
        <div class="metric"><span class="label">Current:</span> <span class="value">{profile.memory_mb:.2f} MB</span></div>
        <div class="metric"><span class="label">Peak:</span> <span class="value">{profile.memory_peak_mb:.2f} MB</span></div>

        <h3>A2A Communication</h3>
        <div class="metric"><span class="label">Sent:</span> <span class="value">{profile.a2a_sent_count} ({format_bytes(profile.a2a_sent_bytes)})</span></div>
        <div class="metric"><span class="label">Received:</span> <span class="value">{profile.a2a_received_count} ({format_bytes(profile.a2a_received_bytes)})</span></div>

        <h3>Execution</h3>
        <div class="metric"><span class="label">Process Count:</span> <span class="value">{profile.process_count}</span></div>
        <div class="metric"><span class="label">Total Time:</span> <span class="value">{format_duration(profile.total_process_time)}</span></div>
        <div class="metric"><span class="label">Avg Time:</span> <span class="value">{format_duration(profile.avg_process_time)}</span></div>
        <div class="metric"><span class="label">Max Time:</span> <span class="value">{format_duration(profile.max_process_time)}</span></div>

        <h3>Value Function</h3>
        <div class="metric"><span class="label">Value:</span> <span class="value">{profile.value_function:.3f}</span></div>
        <div class="metric"><span class="label">Successes:</span> <span class="value">{profile.success_count}</span></div>
        <div class="metric"><span class="label">Failures:</span> <span class="value">{profile.failure_count}</span></div>
"""

            if profile.hotspots:
                agent_html += "\n        <h3>CPU Hotspots</h3>\n"
                for hotspot in profile.hotspots[:10]:
                    agent_html += f"""
        <div class="hotspot">
            <strong>{hotspot['function']}</strong><br>
            Calls: {hotspot['calls']}, Time: {format_duration(hotspot['total_time'])}
        </div>
"""

            agent_html += "\n    </div>\n"
            profiles_html += agent_html

        html_content = html.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            count=len([p for p in profiles.values() if p]),
            profiles_html=profiles_html
        )

        with open(filepath, 'w') as f:
            f.write(html_content)

        return str(filepath)

    def clear(self) -> None:
        """Clear all collected profiles."""
        with self._lock:
            self._profiles.clear()
            self._a2a_sent.clear()
            self._a2a_received.clear()
            self._a2a_sent_bytes.clear()
            self._a2a_received_bytes.clear()
            self._process_times.clear()
            self._metrics.clear()
