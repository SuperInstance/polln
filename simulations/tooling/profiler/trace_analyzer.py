"""
Trace Analyzer
Analyze distributed A2A package traces to identify bottlenecks and cascading delays.
"""

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import statistics


@dataclass
class TraceEvent:
    """A single event in a trace."""
    timestamp: float
    event_type: str  # 'send', 'receive', 'process_start', 'process_end'
    agent_id: str
    package_id: str
    causal_chain_id: str
    parent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceAnalysis:
    """Results of trace analysis."""
    total_traces: int
    total_duration: float
    avg_trace_duration: float
    p50_duration: float
    p90_duration: float
    p95_duration: float
    p99_duration: float

    # Bottlenecks
    slowest_agents: List[Dict[str, Any]]
    bottleneck_links: List[Dict[str, Any]]
    cascading_delays: List[Dict[str, Any]]

    # Communication patterns
    most_active_links: List[Dict[str, Any]]
    package_sizes: Dict[str, float]
    agent_utilization: Dict[str, float]

    # Trace timeline
    trace_timeline: List[Dict[str, Any]]


class TraceAnalyzer:
    """
    Analyze distributed A2A package traces.

    Identifies:
    - Slow agents (high processing time)
    - Communication bottlenecks (high latency links)
    - Cascading delays (chain reactions)
    - Most active communication links
    - Package size distribution
    - Agent utilization

    Usage:
        analyzer = TraceAnalyzer()

        # Add trace events
        for event in trace_events:
            analyzer.add_event(event)

        # Analyze traces
        analysis = analyzer.analyze()

        # Generate report
        report_path = analyzer.generate_report(analysis)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the trace analyzer.

        Args:
            output_dir: Directory to save analysis reports
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Trace storage
        self._traces: Dict[str, List[TraceEvent]] = defaultdict(list)
        self._events_by_agent: Dict[str, List[TraceEvent]] = defaultdict(list)
        self._events_by_chain: Dict[str, List[TraceEvent]] = defaultdict(list)

        # Package tracking
        self._package_sizes: Dict[str, int] = {}
        self._package_senders: Dict[str, str] = {}
        self._package_receivers: Dict[str, str] = {}

    def add_event(self, event: TraceEvent) -> None:
        """
        Add a trace event.

        Args:
            event: TraceEvent to add
        """
        # Add to traces
        self._traces[event.package_id].append(event)

        # Add to agent index
        self._events_by_agent[event.agent_id].append(event)

        # Add to causal chain index
        self._events_by_chain[event.causal_chain_id].append(event)

        # Track package metadata
        if event.event_type == 'send':
            self._package_senders[event.package_id] = event.agent_id
            if 'size' in event.metadata:
                self._package_sizes[event.package_id] = event.metadata['size']
        elif event.event_type == 'receive':
            self._package_receivers[event.package_id] = event.agent_id

    def add_events(self, events: List[TraceEvent]) -> None:
        """
        Add multiple trace events.

        Args:
            events: List of TraceEvents
        """
        for event in events:
            self.add_event(event)

    def load_from_file(self, filepath: str) -> None:
        """
        Load trace events from a JSON file.

        Args:
            filepath: Path to JSON file with trace events
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        for event_data in data.get('events', []):
            event = TraceEvent(**event_data)
            self.add_event(event)

    def save_to_file(self, filepath: str) -> None:
        """
        Save trace events to a JSON file.

        Args:
            filepath: Path to save JSON file
        """
        events = []
        for trace_events in self._traces.values():
            events.extend([asdict(e) for e in trace_events])

        with open(filepath, 'w') as f:
            json.dump({'events': events}, f, indent=2, default=str)

    def analyze(self) -> TraceAnalysis:
        """
        Analyze all collected traces.

        Returns:
            TraceAnalysis with findings
        """
        # Calculate trace durations
        trace_durations = []
        trace_timelines = []

        for package_id, events in self._traces.items():
            if not events:
                continue

            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda e: e.timestamp)

            # Calculate duration
            duration = sorted_events[-1].timestamp - sorted_events[0].timestamp
            trace_durations.append(duration)

            # Build timeline
            timeline = {
                'package_id': package_id,
                'duration': duration,
                'hop_count': len(sorted_events),
                'start_time': sorted_events[0].timestamp,
                'end_time': sorted_events[-1].timestamp,
                'causal_chain_id': sorted_events[0].causal_chain_id,
            }
            trace_timelines.append(timeline)

        # Calculate percentiles
        if trace_durations:
            sorted_durations = sorted(trace_durations)
            n = len(sorted_durations)

            p50 = sorted_durations[int(n * 0.50)]
            p90 = sorted_durations[int(n * 0.90)]
            p95 = sorted_durations[int(n * 0.95)]
            p99 = sorted_durations[int(n * 0.99)] if n >= 100 else sorted_durations[-1]
        else:
            p50 = p90 = p95 = p99 = 0.0

        # Find slowest agents
        slowest_agents = self._find_slowest_agents()

        # Find bottleneck links
        bottleneck_links = self._find_bottleneck_links()

        # Find cascading delays
        cascading_delays = self._find_cascading_delays()

        # Find most active links
        most_active_links = self._find_most_active_links()

        # Calculate package size stats
        package_sizes = self._calculate_package_size_stats()

        # Calculate agent utilization
        agent_utilization = self._calculate_agent_utilization()

        return TraceAnalysis(
            total_traces=len(self._traces),
            total_duration=sum(trace_durations),
            avg_trace_duration=statistics.mean(trace_durations) if trace_durations else 0,
            p50_duration=p50,
            p90_duration=p90,
            p95_duration=p95,
            p99_duration=p99,
            slowest_agents=slowest_agents,
            bottleneck_links=bottleneck_links,
            cascading_delays=cascading_delays,
            most_active_links=most_active_links,
            package_sizes=package_sizes,
            agent_utilization=agent_utilization,
            trace_timeline=trace_timelines,
        )

    def _find_slowest_agents(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find agents with highest processing times."""
        agent_times: Dict[str, List[float]] = defaultdict(list)

        for agent_id, events in self._events_by_agent.items():
            for event in events:
                if event.event_type == 'process_end':
                    # Find matching process_start
                    for start_event in events:
                        if (start_event.event_type == 'process_start' and
                            start_event.package_id == event.package_id):
                            duration = event.timestamp - start_event.timestamp
                            agent_times[agent_id].append(duration)
                            break

        # Calculate statistics per agent
        agent_stats = []
        for agent_id, times in agent_times.items():
            if times:
                agent_stats.append({
                    'agent_id': agent_id,
                    'avg_time': statistics.mean(times),
                    'max_time': max(times),
                    'total_time': sum(times),
                    'process_count': len(times),
                })

        # Sort by average time
        agent_stats.sort(key=lambda x: x['avg_time'], reverse=True)

        return agent_stats[:top_n]

    def _find_bottleneck_links(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find communication links with highest latency."""
        link_times: Dict[Tuple[str, str], List[float]] = defaultdict(list)

        for package_id, events in self._traces.items():
            sender = self._package_senders.get(package_id)
            receiver = self._package_receivers.get(package_id)

            if sender and receiver:
                # Find send and receive events
                send_event = None
                recv_event = None

                for event in events:
                    if event.event_type == 'send' and event.agent_id == sender:
                        send_event = event
                    elif event.event_type == 'receive' and event.agent_id == receiver:
                        recv_event = event

                if send_event and recv_event:
                    latency = recv_event.timestamp - send_event.timestamp
                    link_times[(sender, receiver)].append(latency)

        # Calculate statistics per link
        link_stats = []
        for (sender, receiver), times in link_times.items():
            if times:
                link_stats.append({
                    'sender': sender,
                    'receiver': receiver,
                    'avg_latency': statistics.mean(times),
                    'max_latency': max(times),
                    'package_count': len(times),
                })

        # Sort by average latency
        link_stats.sort(key=lambda x: x['avg_latency'], reverse=True)

        return link_stats[:top_n]

    def _find_cascading_delays(
        self,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Find cascading delays in causal chains.

        A cascading delay is when a delay in an early step
        causes delays in subsequent steps.
        """
        cascading = []

        for chain_id, events in self._events_by_chain.items():
            # Group events by package
            packages: Dict[str, List[TraceEvent]] = defaultdict(list)
            for event in events:
                packages[event.package_id].append(event)

            # Analyze each package in the chain
            for package_id, pkg_events in packages.items():
                sorted_events = sorted(pkg_events, key=lambda e: e.timestamp)

                # Calculate inter-hop delays
                for i in range(len(sorted_events) - 1):
                    current = sorted_events[i]
                    next_event = sorted_events[i + 1]

                    delay = next_event.timestamp - current.timestamp

                    # Check if this is a cascading delay
                    # (delay is significantly higher than previous hop)
                    if i > 0:
                        prev_delay = sorted_events[i].timestamp - sorted_events[i-1].timestamp
                        if delay > prev_delay * threshold_multiplier:
                            cascading.append({
                                'chain_id': chain_id,
                                'package_id': package_id,
                                'from_agent': current.agent_id,
                                'to_agent': next_event.agent_id,
                                'delay': delay,
                                'previous_delay': prev_delay,
                                'multiplier': delay / prev_delay if prev_delay > 0 else 0,
                            })

        # Sort by multiplier
        cascading.sort(key=lambda x: x['multiplier'], reverse=True)

        return cascading[:10]

    def _find_most_active_links(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find communication links with most traffic."""
        link_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        link_bytes: Dict[Tuple[str, str], int] = defaultdict(int)

        for package_id in self._traces.keys():
            sender = self._package_senders.get(package_id)
            receiver = self._package_receivers.get(package_id)

            if sender and receiver:
                link = (sender, receiver)
                link_counts[link] += 1
                link_bytes[link] += self._package_sizes.get(package_id, 0)

        # Build stats
        link_stats = []
        for (sender, receiver), count in link_counts.items():
            link_stats.append({
                'sender': sender,
                'receiver': receiver,
                'package_count': count,
                'total_bytes': link_bytes[(sender, receiver)],
            })

        # Sort by package count
        link_stats.sort(key=lambda x: x['package_count'], reverse=True)

        return link_stats[:top_n]

    def _calculate_package_size_stats(self) -> Dict[str, float]:
        """Calculate package size statistics."""
        sizes = list(self._package_sizes.values())

        if not sizes:
            return {
                'min': 0,
                'max': 0,
                'avg': 0,
                'median': 0,
                'p90': 0,
                'p99': 0,
            }

        sorted_sizes = sorted(sizes)
        n = len(sorted_sizes)

        return {
            'min': min(sizes),
            'max': max(sizes),
            'avg': statistics.mean(sizes),
            'median': statistics.median(sizes),
            'p90': sorted_sizes[int(n * 0.90)],
            'p99': sorted_sizes[int(n * 0.99)] if n >= 100 else sorted_sizes[-1],
        }

    def _calculate_agent_utilization(self) -> Dict[str, float]:
        """
        Calculate agent utilization based on time spent processing.

        Returns a mapping from agent_id to utilization ratio (0-1).
        """
        utilization = {}

        for agent_id, events in self._events_by_agent.items():
            # Find all process_start and process_end pairs
            process_times = []

            for event in events:
                if event.event_type == 'process_end':
                    # Find matching start
                    for start_event in events:
                        if (start_event.event_type == 'process_start' and
                            start_event.package_id == event.package_id):
                            duration = event.timestamp - start_event.timestamp
                            process_times.append((start_event.timestamp, event.timestamp))
                            break

            if not process_times:
                utilization[agent_id] = 0.0
                continue

            # Calculate total time range
            all_timestamps = [e.timestamp for e in events]
            time_range = max(all_timestamps) - min(all_timestamps)

            if time_range == 0:
                utilization[agent_id] = 0.0
                continue

            # Sum processing time
            total_process_time = sum(end - start for start, end in process_times)

            # Utilization is processing time / total time
            utilization[agent_id] = total_process_time / time_range

        return utilization

    def generate_report(
        self,
        analysis: Optional[TraceAnalysis] = None,
        format: str = 'json'
    ) -> str:
        """
        Generate analysis report.

        Args:
            analysis: TraceAnalysis (runs analyze() if None)
            format: Report format ('json', 'text', 'html')

        Returns:
            Path to generated report
        """
        if analysis is None:
            analysis = self.analyze()

        if format == 'json':
            return self._generate_json_report(analysis)
        elif format == 'text':
            return self._generate_text_report(analysis)
        elif format == 'html':
            return self._generate_html_report(analysis)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_json_report(self, analysis: TraceAnalysis) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"trace_analysis_{timestamp}.json"

        with open(filepath, 'w') as f:
            json.dump(asdict(analysis), f, indent=2, default=str)

        return str(filepath)

    def _generate_text_report(self, analysis: TraceAnalysis) -> str:
        """Generate human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"trace_analysis_{timestamp}.txt"

        from utils.formatters import format_duration, format_bytes, format_table

        lines = []
        lines.append("=" * 80)
        lines.append("DISTRIBUTED TRACE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Traces: {analysis.total_traces}")
        lines.append("")

        # Duration stats
        lines.append("Trace Durations:")
        lines.append(f"  Average: {format_duration(analysis.avg_trace_duration)}")
        lines.append(f"  p50: {format_duration(analysis.p50_duration)}")
        lines.append(f"  p90: {format_duration(analysis.p90_duration)}")
        lines.append(f"  p95: {format_duration(analysis.p95_duration)}")
        lines.append(f"  p99: {format_duration(analysis.p99_duration)}")
        lines.append("")

        # Slowest agents
        if analysis.slowest_agents:
            lines.append("Slowest Agents (by processing time):")
            for i, agent in enumerate(analysis.slowest_agents[:5], 1):
                lines.append(f"  {i}. {agent['agent_id']}")
                lines.append(f"     Avg: {format_duration(agent['avg_time'])}, "
                           f"Max: {format_duration(agent['max_time'])}, "
                           f"Count: {agent['process_count']}")
            lines.append("")

        # Bottleneck links
        if analysis.bottleneck_links:
            lines.append("Bottleneck Links (by latency):")
            for i, link in enumerate(analysis.bottleneck_links[:5], 1):
                lines.append(f"  {i}. {link['sender']} -> {link['receiver']}")
                lines.append(f"     Avg: {format_duration(link['avg_latency'])}, "
                           f"Max: {format_duration(link['max_latency'])}, "
                           f"Packages: {link['package_count']}")
            lines.append("")

        # Cascading delays
        if analysis.cascading_delays:
            lines.append("Cascading Delays:")
            for i, delay in enumerate(analysis.cascading_delays[:5], 1):
                lines.append(f"  {i}. Chain: {delay['chain_id']}")
                lines.append(f"     {delay['from_agent']} -> {delay['to_agent']}")
                lines.append(f"     Delay: {format_duration(delay['delay'])}, "
                           f"Multiplier: {delay['multiplier']:.2f}x")
            lines.append("")

        # Most active links
        if analysis.most_active_links:
            lines.append("Most Active Links:")
            for i, link in enumerate(analysis.most_active_links[:5], 1):
                lines.append(f"  {i}. {link['sender']} -> {link['receiver']}")
                lines.append(f"     Packages: {link['package_count']}, "
                           f"Bytes: {format_bytes(link['total_bytes'])}")
            lines.append("")

        # Package sizes
        lines.append("Package Sizes:")
        lines.append(f"  Min: {format_bytes(int(analysis.package_sizes['min']))}")
        lines.append(f"  Max: {format_bytes(int(analysis.package_sizes['max']))}")
        lines.append(f"  Avg: {format_bytes(int(analysis.package_sizes['avg']))}")
        lines.append(f"  Median: {format_bytes(int(analysis.package_sizes['median']))}")
        lines.append("")

        lines.append("=" * 80)

        report_text = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def _generate_html_report(self, analysis: TraceAnalysis) -> str:
        """Generate interactive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"trace_analysis_{timestamp}.html"

        from utils.formatters import format_duration, format_bytes

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trace Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; }}
        .metric {{ margin: 10px 0; }}
        .label {{ font-weight: bold; }}
        .value {{ color: #0066cc; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Distributed Trace Analysis Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Traces: {analysis.total_traces}</p>

    <div class="section">
        <h2>Trace Durations</h2>
        <div class="metric"><span class="label">Average:</span> <span class="value">{format_duration(analysis.avg_trace_duration)}</span></div>
        <div class="metric"><span class="label">p50:</span> <span class="value">{format_duration(analysis.p50_duration)}</span></div>
        <div class="metric"><span class="label">p90:</span> <span class="value">{format_duration(analysis.p90_duration)}</span></div>
        <div class="metric"><span class="label">p95:</span> <span class="value">{format_duration(analysis.p95_duration)}</span></div>
        <div class="metric"><span class="label">p99:</span> <span class="value">{format_duration(analysis.p99_duration)}</span></div>
    </div>

    <div class="section">
        <h2>Slowest Agents</h2>
        <table>
            <tr><th>Agent</th><th>Avg Time</th><th>Max Time</th><th>Count</th></tr>
            {self._generate_slowest_agents_rows(analysis.slowest_agents)}
        </table>
    </div>

    <div class="section">
        <h2>Bottleneck Links</h2>
        <table>
            <tr><th>Link</th><th>Avg Latency</th><th>Max Latency</th><th>Packages</th></tr>
            {self._generate_bottleneck_links_rows(analysis.bottleneck_links)}
        </table>
    </div>

    <div class="section">
        <h2>Package Sizes</h2>
        <div class="metric"><span class="label">Min:</span> <span class="value">{format_bytes(int(analysis.package_sizes['min']))}</span></div>
        <div class="metric"><span class="label">Max:</span> <span class="value">{format_bytes(int(analysis.package_sizes['max']))}</span></div>
        <div class="metric"><span class="label">Average:</span> <span class="value">{format_bytes(int(analysis.package_sizes['avg']))}</span></div>
        <div class="metric"><span class="label">Median:</span> <span class="value">{format_bytes(int(analysis.package_sizes['median']))}</span></div>
    </div>

</body>
</html>
        """

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)

    def _generate_slowest_agents_rows(self, agents: List[Dict]) -> str:
        """Generate HTML table rows for slowest agents."""
        rows = []
        for agent in agents[:10]:
            rows.append(f"<tr><td>{agent['agent_id']}</td>"
                       f"<td>{format_duration(agent['avg_time'])}</td>"
                       f"<td>{format_duration(agent['max_time'])}</td>"
                       f"<td>{agent['process_count']}</td></tr>")
        return "\n".join(rows)

    def _generate_bottleneck_links_rows(self, links: List[Dict]) -> str:
        """Generate HTML table rows for bottleneck links."""
        rows = []
        for link in links[:10]:
            rows.append(f"<tr><td>{link['sender']} &rarr; {link['receiver']}</td>"
                       f"<td>{format_duration(link['avg_latency'])}</td>"
                       f"<td>{format_duration(link['max_latency'])}</td>"
                       f"<td>{link['package_count']}</td></tr>")
        return "\n".join(rows)

    def clear(self) -> None:
        """Clear all collected trace data."""
        self._traces.clear()
        self._events_by_agent.clear()
        self._events_by_chain.clear()
        self._package_sizes.clear()
        self._package_senders.clear()
        self._package_receivers.clear()
