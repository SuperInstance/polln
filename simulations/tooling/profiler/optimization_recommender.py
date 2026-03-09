"""
Optimization Recommender
Analyze profiling data and generate actionable optimization recommendations.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import statistics

from utils.formatters import format_duration, format_bytes


class OptimizationPriority(Enum):
    """Priority level for optimizations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation."""
    title: str
    description: str
    category: str  # 'cpu', 'memory', 'a2a', 'architecture'
    priority: OptimizationPriority
    estimated_speedup: float  # multiplier (e.g., 1.5 = 50% faster)
    estimated_memory_reduction: float  # bytes
    implementation_effort: str  # 'easy', 'medium', 'hard'
    code_references: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationReport:
    """Complete optimization recommendations report."""
    timestamp: float

    # Summary
    total_recommendations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    # Potential improvements
    estimated_total_speedup: float
    estimated_memory_reduction: float

    # Recommendations
    recommendations: List[OptimizationRecommendation]

    # Quick wins (high impact, low effort)
    quick_wins: List[OptimizationRecommendation]

    # Strategic changes (high impact, high effort)
    strategic_changes: List[OptimizationRecommendation]


class OptimizationRecommender:
    """
    Generate optimization recommendations from profiling data.

    Analyzes:
    - CPU bottlenecks and hotspots
    - Memory leaks and fragmentation
    - A2A communication patterns
    - Agent topology and allocation
    - KV-cache efficiency

    Generates prioritized recommendations with:
    - Estimated speedup/improvement
    - Implementation effort
    - Code references

    Usage:
        recommender = OptimizationRecommender()

        # Add profiling data
        recommender.add_agent_profile(agent_profile)
        recommender.add_colony_profile(colony_profile)
        recommender.add_memory_profile(memory_profile)
        recommender.add_trace_analysis(trace_analysis)

        # Generate recommendations
        report = recommender.generate_recommendations()
        report_path = recommender.generate_report(report)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the optimization recommender.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Profiling data storage
        self._agent_profiles: List[Dict[str, Any]] = []
        self._colony_profiles: List[Dict[str, Any]] = []
        self._memory_profiles: List[Dict[str, Any]] = []
        self._trace_analyses: List[Dict[str, Any]] = []

    def add_agent_profile(self, profile: Dict[str, Any]) -> None:
        """Add agent profiling data."""
        self._agent_profiles.append(profile)

    def add_colony_profile(self, profile: Dict[str, Any]) -> None:
        """Add colony profiling data."""
        self._colony_profiles.append(profile)

    def add_memory_profile(self, profile: Dict[str, Any]) -> None:
        """Add memory profiling data."""
        self._memory_profiles.append(profile)

    def add_trace_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add trace analysis data."""
        self._trace_analyses.append(analysis)

    def generate_recommendations(self) -> OptimizationReport:
        """
        Generate optimization recommendations from all collected data.

        Returns:
            OptimizationReport with all recommendations
        """
        recommendations = []

        # Analyze CPU bottlenecks
        recommendations.extend(self._analyze_cpu_bottlenecks())

        # Analyze memory issues
        recommendations.extend(self._analyze_memory_issues())

        # Analyze A2A communication
        recommendations.extend(self._analyze_a2a_communication())

        # Analyze topology
        recommendations.extend(self._analyze_topology())

        # Analyze KV-cache usage
        recommendations.extend(self._analyze_kv_cache())

        # Prioritize
        recommendations = self._prioritize_recommendations(recommendations)

        # Categorize
        quick_wins = [
            r for r in recommendations
            if r.priority in [OptimizationPriority.CRITICAL, OptimizationPriority.HIGH]
            and r.implementation_effort == 'easy'
        ]

        strategic = [
            r for r in recommendations
            if r.priority in [OptimizationPriority.CRITICAL, OptimizationPriority.HIGH]
            and r.implementation_effort == 'hard'
        ]

        # Count by priority
        priority_counts = {
            OptimizationPriority.CRITICAL: 0,
            OptimizationPriority.HIGH: 0,
            OptimizationPriority.MEDIUM: 0,
            OptimizationPriority.LOW: 0,
        }

        for rec in recommendations:
            priority_counts[rec.priority] += 1

        # Calculate total potential improvement
        total_speedup = 1.0
        for rec in recommendations:
            if rec.estimated_speedup > 1:
                total_speedup *= rec.estimated_speedup

        total_memory_reduction = sum(r.estimated_memory_reduction for r in recommendations)

        return OptimizationReport(
            timestamp=time.time(),
            total_recommendations=len(recommendations),
            critical_count=priority_counts[OptimizationPriority.CRITICAL],
            high_count=priority_counts[OptimizationPriority.HIGH],
            medium_count=priority_counts[OptimizationPriority.MEDIUM],
            low_count=priority_counts[OptimizationPriority.LOW],
            estimated_total_speedup=total_speedup,
            estimated_memory_reduction=total_memory_reduction,
            recommendations=recommendations,
            quick_wins=quick_wins,
            strategic_changes=strategic,
        )

    def _analyze_cpu_bottlenecks(self) -> List[OptimizationRecommendation]:
        """Analyze CPU profiling data for bottlenecks."""
        recommendations = []

        for profile in self._agent_profiles:
            hotspots = profile.get('hotspots', [])

            for hotspot in hotspots[:5]:  # Top 5
                func = hotspot.get('function', 'unknown')
                total_time = hotspot.get('total_time', 0)
                calls = hotspot.get('calls', 0)

                if total_time > 0.1:  # > 100ms is significant
                    # Determine priority based on time
                    if total_time > 1.0:
                        priority = OptimizationPriority.CRITICAL
                        speedup = 2.0
                    elif total_time > 0.5:
                        priority = OptimizationPriority.HIGH
                        speedup = 1.5
                    else:
                        priority = OptimizationPriority.MEDIUM
                        speedup = 1.2

                    recommendations.append(OptimizationRecommendation(
                        title=f"Optimize CPU hotspot: {func}",
                        description=f"Function {func} is consuming {total_time:.2f}s across {calls} calls. "
                                   f"Consider caching, algorithmic improvements, or delegation.",
                        category='cpu',
                        priority=priority,
                        estimated_speedup=speedup,
                        estimated_memory_reduction=0,
                        implementation_effort='medium',
                        code_references=[func],
                        metrics={
                            'function': func,
                            'total_time': total_time,
                            'calls': calls,
                        },
                    ))

        return recommendations

    def _analyze_memory_issues(self) -> List[OptimizationRecommendation]:
        """Analyze memory profiling data for issues."""
        recommendations = []

        for profile in self._memory_profiles:
            # Check for memory leaks
            leaks = profile.get('suspected_leaks', [])

            for leak in leaks[:5]:  # Top 5 leaks
                obj_type = leak.get('object_type', 'unknown')
                growth_rate = leak.get('growth_rate', 0)
                total = leak.get('total_bytes', 0)

                if growth_rate > 1000:  # > 1KB/sec growth
                    recommendations.append(OptimizationRecommendation(
                        title=f"Fix memory leak: {obj_type}",
                        description=f"Object type {obj_type} is growing at {growth_rate:.0f} bytes/sec. "
                                   f"Total leaked: {format_bytes(total)}. "
                                   f"Ensure proper cleanup and object pooling.",
                        category='memory',
                        priority=OptimizationPriority.CRITICAL,
                        estimated_speedup=1.0,
                        estimated_memory_reduction=total,
                        implementation_effort='medium',
                        code_references=[obj_type],
                        metrics=leak,
                    ))

            # Check for fragmentation
            frag_ratio = profile.get('fragmentation_ratio', 0)
            if frag_ratio > 0.3:
                recommendations.append(OptimizationRecommendation(
                    title="Reduce memory fragmentation",
                    description=f"Memory fragmentation is at {frag_ratio:.0%}. "
                               f"Use object pools, pre-allocate buffers, or enable compaction.",
                    category='memory',
                    priority=OptimizationPriority.HIGH if frag_ratio > 0.5 else OptimizationPriority.MEDIUM,
                    estimated_speedup=1.1,
                    estimated_memory_reduction=int(profile.get('peak_rss_bytes', 0) * frag_ratio * 0.5),
                    implementation_effort='medium',
                    metrics={'fragmentation_ratio': frag_ratio},
                ))

            # Check KV-cache efficiency
            kv_frag = profile.get('kv_cache_fragmentation', 0)
            if kv_frag > 0.2:
                recommendations.append(OptimizationRecommendation(
                    title="Optimize KV-cache memory layout",
                    description=f"KV-cache fragmentation is at {kv_frag:.0%}. "
                               f"Use contiguous allocation or enable anchor compression.",
                    category='memory',
                    priority=OptimizationPriority.HIGH,
                    estimated_speedup=1.2,
                    estimated_memory_reduction=int(profile.get('kv_cache_usage_bytes', 0) * kv_frag * 0.3),
                    implementation_effort='hard',
                    metrics={'kv_cache_fragmentation': kv_frag},
                ))

        return recommendations

    def _analyze_a2a_communication(self) -> List[OptimizationRecommendation]:
        """Analyze A2A communication patterns."""
        recommendations = []

        for analysis in self._trace_analyses:
            # Check for slow agents
            slowest = analysis.get('slowest_agents', [])

            for agent in slowest[:3]:
                agent_id = agent.get('agent_id', 'unknown')
                avg_time = agent.get('avg_time', 0)

                if avg_time > 0.1:  # > 100ms
                    recommendations.append(OptimizationRecommendation(
                        title=f"Optimize slow agent: {agent_id}",
                        description=f"Agent {agent_id} has average processing time of {format_duration(avg_time)}. "
                                   f"Consider batching, caching, or model optimization.",
                        category='a2a',
                        priority=OptimizationPriority.HIGH,
                        estimated_speedup=1.5,
                        estimated_memory_reduction=0,
                        implementation_effort='medium',
                        code_references=[agent_id],
                        metrics=agent,
                    ))

            # Check for bottleneck links
            bottlenecks = analysis.get('bottleneck_links', [])

            for link in bottlenecks[:3]:
                sender = link.get('sender', 'unknown')
                receiver = link.get('receiver', 'unknown')
                avg_latency = link.get('avg_latency', 0)

                if avg_latency > 0.05:  # > 50ms
                    recommendations.append(OptimizationRecommendation(
                        title=f"Optimize communication link: {sender} -> {receiver}",
                        description=f"Communication link has average latency of {format_duration(avg_latency)}. "
                                   f"Consider message batching, compression, or direct connection.",
                        category='a2a',
                        priority=OptimizationPriority.MEDIUM,
                        estimated_speedup=1.3,
                        estimated_memory_reduction=0,
                        implementation_effort='easy',
                        code_references=[sender, receiver],
                        metrics=link,
                    ))

            # Check for cascading delays
            cascading = analysis.get('cascading_delays', [])

            if len(cascading) > 5:
                recommendations.append(OptimizationRecommendation(
                    title="Reduce cascading delays",
                    description=f"Found {len(cascading)} cascading delays in causal chains. "
                               f"Implement timeout policies, async processing, or load balancing.",
                    category='a2a',
                    priority=OptimizationPriority.HIGH,
                    estimated_speedup=1.4,
                    estimated_memory_reduction=0,
                    implementation_effort='hard',
                    metrics={'cascading_delay_count': len(cascading)},
                ))

        return recommendations

    def _analyze_topology(self) -> List[OptimizationRecommendation]:
        """Analyze agent topology."""
        recommendations = []

        for profile in self._colony_profiles:
            # Check agent count vs active
            total = profile.get('total_agents', 0)
            active = profile.get('active_agents', 0)

            if total > 0:
                active_ratio = active / total

                if active_ratio < 0.5:
                    recommendations.append(OptimizationRecommendation(
                        title="Reduce dormant agent overhead",
                        description=f"Only {active_ratio:.0%} of agents are active. "
                                   f"Consider hibernating or removing dormant agents.",
                        category='architecture',
                        priority=OptimizationPriority.MEDIUM,
                        estimated_speedup=1.1,
                        estimated_memory_reduction=int((total - active) * 10_000_000),  # Estimate 10MB per agent
                        implementation_effort='easy',
                        metrics={
                            'total_agents': total,
                            'active_agents': active,
                            'active_ratio': active_ratio,
                        },
                    ))

            # Check for churn
            spawned = profile.get('agents_spawned', 0)
            killed = profile.get('agents_killed', 0)
            duration = profile.get('duration_seconds', 1)

            churn_rate = (spawned + killed) / duration if duration > 0 else 0

            if churn_rate > 10:  # More than 10 agents/sec churn
                recommendations.append(OptimizationRecommendation(
                    title="Reduce agent churn",
                    description=f"Agent churn rate is {churn_rate:.1f} agents/sec. "
                               f"Use agent pooling or reuse existing agents.",
                    category='architecture',
                    priority=OptimizationPriority.MEDIUM,
                    estimated_speedup=1.2,
                    estimated_memory_reduction=0,
                    implementation_effort='medium',
                    metrics={'churn_rate': churn_rate},
                ))

        return recommendations

    def _analyze_kv_cache(self) -> List[OptimizationRecommendation]:
        """Analyze KV-cache usage patterns."""
        recommendations = []

        for profile in self._agent_profiles:
            # Check for high memory usage in agents
            memory_mb = profile.get('memory_mb', 0)

            if memory_mb > 1000:  # > 1GB
                recommendations.append(OptimizationRecommendation(
                    title="Implement KV-cache offloading",
                    description=f"Agent memory usage is {memory_mb:.0f}MB. "
                               f"Implement KV-cache offloading to shared cache or disk.",
                    category='memory',
                    priority=OptimizationPriority.HIGH,
                    estimated_speedup=1.3,
                    estimated_memory_reduction=int(memory_mb * 0.3 * 1024 * 1024),
                    implementation_effort='hard',
                    metrics={'memory_mb': memory_mb},
                ))

        return recommendations

    def _prioritize_recommendations(
        self,
        recommendations: List[OptimizationRecommendation]
    ) -> List[OptimizationRecommendation]:
        """
        Prioritize recommendations by impact and effort.

        Uses a simple scoring system:
        - Critical issues get highest priority
        - High impact + low effort (quick wins) get boosted
        """
        # Sort by priority first
        priority_order = {
            OptimizationPriority.CRITICAL: 0,
            OptimizationPriority.HIGH: 1,
            OptimizationPriority.MEDIUM: 2,
            OptimizationPriority.LOW: 3,
        }

        def score(rec: OptimizationRecommendation) -> Tuple[int, float]:
            # Priority score (lower is better)
            priority_score = priority_order[rec.priority]

            # Impact score (higher is better)
            impact_score = rec.estimated_speedup * rec.estimated_memory_reduction / 1_000_000

            # Quick wins get boosted
            if rec.implementation_effort == 'easy' and impact_score > 10:
                priority_score = max(0, priority_score - 1)

            return (priority_score, -impact_score)  # Negative for descending sort

        return sorted(recommendations, key=score)

    def generate_report(
        self,
        report: Optional[OptimizationReport] = None,
        format: str = 'json'
    ) -> str:
        """
        Generate recommendations report.

        Args:
            report: OptimizationReport (generates if None)
            format: Report format ('json', 'text', 'html')

        Returns:
            Path to generated report
        """
        if report is None:
            report = self.generate_recommendations()

        if format == 'json':
            return self._generate_json_report(report)
        elif format == 'text':
            return self._generate_text_report(report)
        elif format == 'html':
            return self._generate_html_report(report)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_json_report(self, report: OptimizationReport) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"recommendations_{timestamp}.json"

        # Convert enums to strings
        report_data = asdict(report)
        for rec in report_data['recommendations']:
            rec['priority'] = rec['priority'].value if isinstance(rec['priority'], OptimizationPriority) else rec['priority']
        for rec in report_data['quick_wins']:
            rec['priority'] = rec['priority'].value if isinstance(rec['priority'], OptimizationPriority) else rec['priority']
        for rec in report_data['strategic_changes']:
            rec['priority'] = rec['priority'].value if isinstance(rec['priority'], OptimizationPriority) else rec['priority']

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def _generate_text_report(self, report: OptimizationReport) -> str:
        """Generate human-readable text report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"recommendations_{timestamp}.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("OPTIMIZATION RECOMMENDATIONS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        lines.append("Summary:")
        lines.append(f"  Total Recommendations: {report.total_recommendations}")
        lines.append(f"  Critical: {report.critical_count}")
        lines.append(f"  High: {report.high_count}")
        lines.append(f"  Medium: {report.medium_count}")
        lines.append(f"  Low: {report.low_count}")
        lines.append("")

        lines.append(f"  Estimated Total Speedup: {report.estimated_total_speedup:.2f}x")
        lines.append(f"  Estimated Memory Reduction: {format_bytes(int(report.estimated_memory_reduction))}")
        lines.append("")

        # Quick wins
        if report.quick_wins:
            lines.append("Quick Wins (High Impact, Low Effort):")
            lines.append("-" * 80)
            for i, rec in enumerate(report.quick_wins, 1):
                lines.append(f"{i}. [{rec.priority.value.upper()}] {rec.title}")
                lines.append(f"   {rec.description}")
                lines.append(f"   Speedup: {rec.estimated_speedup:.2f}x, "
                           f"Effort: {rec.implementation_effort}")
                lines.append("")
            lines.append("")

        # Strategic changes
        if report.strategic_changes:
            lines.append("Strategic Changes (High Impact, High Effort):")
            lines.append("-" * 80)
            for i, rec in enumerate(report.strategic_changes, 1):
                lines.append(f"{i}. [{rec.priority.value.upper()}] {rec.title}")
                lines.append(f"   {rec.description}")
                lines.append(f"   Speedup: {rec.estimated_speedup:.2f}x, "
                           f"Effort: {rec.implementation_effort}")
                lines.append("")
            lines.append("")

        # All recommendations
        lines.append("All Recommendations (Prioritized):")
        lines.append("-" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. [{rec.priority.value.upper()}] {rec.title}")
            lines.append(f"   Category: {rec.category}")
            lines.append(f"   {rec.description}")
            lines.append(f"   Speedup: {rec.estimated_speedup:.2f}x, "
                       f"Memory: {format_bytes(int(rec.estimated_memory_reduction))}, "
                       f"Effort: {rec.implementation_effort}")
            if rec.code_references:
                lines.append(f"   References: {', '.join(rec.code_references)}")
            lines.append("")

        lines.append("=" * 80)

        report_text = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(report_text)

        return str(filepath)

    def _generate_html_report(self, report: OptimizationReport) -> str:
        """Generate interactive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"recommendations_{timestamp}.html"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Optimization Recommendations Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .recommendation {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ddd;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .recommendation.critical {{ border-left-color: #d32f2f; }}
        .recommendation.high {{ border-left-color: #f57c00; }}
        .recommendation.medium {{ border-left-color: #fbc02d; }}
        .recommendation.low {{ border-left-color: #388e3c; }}
        .priority {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            color: white;
            margin-right: 8px;
        }}
        .priority.critical {{ background: #d32f2f; }}
        .priority.high {{ background: #f57c00; }}
        .priority.medium {{ background: #fbc02d; }}
        .priority.low {{ background: #388e3c; }}
        .metric {{ display: inline-block; margin-right: 15px; }}
        .quick-wins {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .strategic {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Optimization Recommendations Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Recommendations:</strong> {report.total_recommendations}</p>
        <p><strong>Priority Breakdown:</strong>
           Critical: {report.critical_count} |
           High: {report.high_count} |
           Medium: {report.medium_count} |
           Low: {report.low_count}
        </p>
        <p><strong>Estimated Total Speedup:</strong> {report.estimated_total_speedup:.2f}x</p>
        <p><strong>Estimated Memory Reduction:</strong> {format_bytes(int(report.estimated_memory_reduction))}</p>
    </div>

    {self._generate_quick_wins_html(report.quick_wins)}
    {self._generate_strategic_html(report.strategic_changes)}
    {self._generate_recommendations_html(report.recommendations)}

</body>
</html>
        """

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)

    def _generate_quick_wins_html(self, wins: List[OptimizationRecommendation]) -> str:
        """Generate HTML for quick wins section."""
        if not wins:
            return ""

        items = "\n".join(
            f'<div class="recommendation {w.priority.value}">'
            f'<span class="priority {w.priority.value}">{w.priority.value.upper()}</span>'
            f'<strong>{w.title}</strong><br>{w.description}<br>'
            f'<span class="metric">Speedup: {w.estimated_speedup:.2f}x</span>'
            f'<span class="metric">Memory: {format_bytes(int(w.estimated_memory_reduction))}</span>'
            f'<span class="metric">Effort: {w.implementation_effort}</span>'
            f'</div>'
            for w in wins
        )

        return f'''
    <div class="quick-wins">
        <h2>Quick Wins (High Impact, Low Effort)</h2>
        {items}
    </div>
    '''

    def _generate_strategic_html(self, strategic: List[OptimizationRecommendation]) -> str:
        """Generate HTML for strategic changes section."""
        if not strategic:
            return ""

        items = "\n".join(
            f'<div class="recommendation {s.priority.value}">'
            f'<span class="priority {s.priority.value}">{s.priority.value.upper()}</span>'
            f'<strong>{s.title}</strong><br>{s.description}<br>'
            f'<span class="metric">Speedup: {s.estimated_speedup:.2f}x</span>'
            f'<span class="metric">Memory: {format_bytes(int(s.estimated_memory_reduction))}</span>'
            f'<span class="metric">Effort: {s.implementation_effort}</span>'
            f'</div>'
            for s in strategic
        )

        return f'''
    <div class="strategic">
        <h2>Strategic Changes (High Impact, High Effort)</h2>
        {items}
    </div>
    '''

    def _generate_recommendations_html(self, recs: List[OptimizationRecommendation]) -> str:
        """Generate HTML for all recommendations."""
        items = "\n".join(
            f'<div class="recommendation {r.priority.value}">'
            f'<span class="priority {r.priority.value}">{r.priority.value.upper()}</span>'
            f'<strong>{r.title}</strong><br>'
            f'Category: {r.category}<br>{r.description}<br>'
            f'<span class="metric">Speedup: {r.estimated_speedup:.2f}x</span>'
            f'<span class="metric">Memory: {format_bytes(int(r.estimated_memory_reduction))}</span>'
            f'<span class="metric">Effort: {r.implementation_effort}</span>'
            f'</div>'
            for r in recs
        )

        return f'''
    <div>
        <h2>All Recommendations (Prioritized)</h2>
        {items}
    </div>
    '''

    def clear(self) -> None:
        """Clear all collected data."""
        self._agent_profiles.clear()
        self._colony_profiles.clear()
        self._memory_profiles.clear()
        self._trace_analyses.clear()


# Import time for timestamps
import time
