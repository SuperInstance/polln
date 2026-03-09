"""
Profile Runner
Orchestrator for running comprehensive POLLN profiling across all tools.
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agent_profiler import AgentProfiler, AgentProfile
from colony_profiler import ColonyProfiler, ColonyProfile
from memory_profiler import MemoryProfiler, MemoryProfile
from trace_analyzer import TraceAnalyzer, TraceEvent, TraceAnalysis
from flame_graph_generator import FlameGraphGenerator
from optimization_recommender import (
    OptimizationRecommender,
    OptimizationReport
)
from utils.metrics import MetricsCollector
from utils.formatters import format_duration, format_bytes


class ProfileRunner:
    """
    Orchestrator for comprehensive POLLN profiling.

    Coordinates:
    - Agent profiling (CPU, memory, A2A)
    - Colony profiling (throughput, latency)
    - Memory profiling (leaks, fragmentation)
    - Trace analysis (bottlenecks, cascading delays)
    - Flame graph generation
    - Optimization recommendations

    Usage:
        runner = ProfileRunner()

        # Define workload
        async def workload(colony):
            # ... your workload here
            pass

        # Run comprehensive profiling
        report = await runner.run_profile(
            colony=colony,
            workload=workload,
            duration_seconds=60,
        )

        # Or via CLI
        # python profile_runner.py --duration 60 --workload my_workload
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        enable_all: bool = True
    ):
        """
        Initialize the profile runner.

        Args:
            output_dir: Directory for all profiling outputs
            enable_all: Enable all profilers by default
        """
        self.output_dir = output_dir or Path("reports/profiling")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize profilers
        self.agent_profiler = AgentProfiler(output_dir=self.output_dir)
        self.colony_profiler = ColonyProfiler(output_dir=self.output_dir)
        self.memory_profiler = MemoryProfiler(output_dir=self.output_dir)
        self.trace_analyzer = TraceAnalyzer(output_dir=self.output_dir)
        self.flame_generator = FlameGraphGenerator(output_dir=self.output_dir)
        self.recommender = OptimizationRecommender(output_dir=self.output_dir)

        # Metrics collector
        self.metrics = MetricsCollector()

        # Configuration
        self.enable_all = enable_all

        # Results storage
        self.results: Dict[str, Any] = {}

    async def run_profile(
        self,
        colony: Any,
        workload: Callable,
        duration_seconds: float = 60,
        warmup_seconds: float = 5,
        iterations: int = 10,
        agent_ids: Optional[List[str]] = None,
        generate_flame_graphs: bool = True,
        generate_recommendations: bool = True,
    ) -> Dict[str, str]:
        """
        Run comprehensive profiling.

        Args:
            colony: The POLLN colony to profile
            workload: Async workload function to execute
            duration_seconds: Duration to run workload
            warmup_seconds: Warmup time before profiling
            iterations: Number of iterations for agent profiling
            agent_ids: Specific agent IDs to profile (all if None)
            generate_flame_graphs: Whether to generate flame graphs
            generate_recommendations: Whether to generate optimization recommendations

        Returns:
            Dictionary mapping report type to file path
        """
        print(f"Starting comprehensive profiling...")
        print(f"  Duration: {format_duration(duration_seconds)}")
        print(f"  Warmup: {format_duration(warmup_seconds)}")
        print(f"  Iterations: {iterations}")
        print()

        report_paths = {}
        start_time = time.time()

        # Warmup
        print(f"Warming up for {format_duration(warmup_seconds)}...")
        try:
            await asyncio.wait_for(workload(colony), timeout=warmup_seconds)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"Warning during warmup: {e}")

        # Start all profilers
        print("Starting profilers...")

        # Colony profiler
        print("  - Colony profiler...")
        colony_task = asyncio.create_task(self.colony_profiler.start_profiling(colony))

        # Memory profiler
        print("  - Memory profiler...")
        memory_task = asyncio.create_task(self.memory_profiler.start_profiling())

        # Wait a moment for profilers to initialize
        await asyncio.sleep(0.5)

        # Run workload
        print(f"\nRunning workload for {format_duration(duration_seconds)}...")
        workload_start = time.time()

        try:
            await asyncio.wait_for(workload(colony), timeout=duration_seconds)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"Workload error: {e}")

        workload_duration = time.time() - workload_start
        print(f"Workload completed in {format_duration(workload_duration)}")

        # Profile specific agents
        if agent_ids is None and hasattr(colony, 'agents'):
            agent_ids = list(colony.agents.keys())[:5]  # Profile up to 5 agents

        agent_profiles = []
        if agent_ids:
            print(f"\nProfiling {len(agent_ids)} agents...")
            for agent_id in agent_ids:
                print(f"  - Agent: {agent_id}")
                agent = colony.agents.get(agent_id)
                if agent:
                    try:
                        profile = await self.agent_profiler.profile_agent(
                            agent,
                            workload,
                            iterations=iterations,
                        )
                        agent_profiles.append(profile)
                    except Exception as e:
                        print(f"    Error: {e}")

        # Stop profilers
        print("\nStopping profilers...")

        # Colony profiler
        print("  - Colony profiler...")
        colony_profile = await self.colony_profiler.stop_profiling()
        colony_path = self.colony_profiler.generate_report(format='html')
        report_paths['colony'] = colony_path
        print(f"    Saved: {colony_path}")

        # Memory profiler
        print("  - Memory profiler...")
        memory_profile = await self.memory_profiler.stop_profiling()
        memory_path = self.memory_profiler.generate_report(format='html')
        report_paths['memory'] = memory_path
        print(f"    Saved: {memory_path}")

        # Generate flame graphs
        if generate_flame_graphs and agent_profiles:
            print("\nGenerating flame graphs...")

            for agent_profile in agent_profiles[:3]:  # Up to 3 agents
                print(f"  - CPU flame graph for {agent_profile.agent_id}...")
                cpu_graph = self.flame_generator.generate_cpu_flame_graph(
                    asdict(agent_profile),
                    title=f"CPU Flame Graph - {agent_profile.agent_id}"
                )
                report_paths[f'flame_cpu_{agent_profile.agent_id}'] = cpu_graph

        # Generate recommendations
        if generate_recommendations:
            print("\nGenerating optimization recommendations...")

            # Add profiling data to recommender
            self.recommender.add_colony_profile(asdict(colony_profile))
            self.recommender.add_memory_profile(asdict(memory_profile))

            for agent_profile in agent_profiles:
                self.recommender.add_agent_profile(asdict(agent_profile))

            # Generate recommendations
            recommendations = self.recommender.generate_recommendations()
            rec_path = self.recommender.generate_report(format='html')
            report_paths['recommendations'] = rec_path
            print(f"    Saved: {rec_path}")

            print(f"\n  Summary:")
            print(f"    Total recommendations: {recommendations.total_recommendations}")
            print(f"    Critical: {recommendations.critical_count}")
            print(f"    High: {recommendations.high_count}")
            print(f"    Estimated speedup: {recommendations.estimated_total_speedup:.2f}x")
            print(f"    Estimated memory reduction: {format_bytes(int(recommendations.estimated_memory_reduction))}")

        # Generate combined dashboard
        print("\nGenerating combined dashboard...")
        dashboard_path = self._generate_dashboard(report_paths)
        report_paths['dashboard'] = dashboard_path
        print(f"    Saved: {dashboard_path}")

        # Summary
        total_duration = time.time() - start_time
        print(f"\n{'=' * 60}")
        print(f"Profiling completed in {format_duration(total_duration)}")
        print(f"{'=' * 60}")
        print("\nGenerated Reports:")
        for report_type, path in report_paths.items():
            print(f"  [{report_type}] {path}")

        print(f"\nOpen the dashboard to view all results:")
        print(f"  file://{Path(dashboard_path).absolute()}")

        return report_paths

    def _generate_dashboard(self, report_paths: Dict[str, str]) -> str:
        """Generate combined HTML dashboard."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"dashboard_{timestamp}.html"

        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>POLLN Profiling Dashboard</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .report-link {{
            display: inline-block;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            transition: background 0.3s;
        }}
        .report-link:hover {{
            background: #5568d3;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }}
        iframe {{
            width: 100%;
            height: 400px;
            border: none;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>POLLN Profiling Dashboard</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="summary">
            <h2>Profiling Summary</h2>
            <p>This dashboard contains comprehensive profiling results for your POLLN colony.</p>
            <p>Use the links below to view detailed reports for each profiling category.</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Colony Profile</h2>
                <p>Colony-level metrics: throughput, latency, agent counts, topology.</p>
                <a href="file://{Path(report_paths.get('colony', '')).absolute()}" target="_blank" class="report-link">View Report</a>
            </div>

            <div class="card">
                <h2>Memory Profile</h2>
                <p>Memory usage, leaks, fragmentation, KV-cache analysis.</p>
                <a href="file://{Path(report_paths.get('memory', '')).absolute()}" target="_blank" class="report-link">View Report</a>
            </div>

            <div class="card">
                <h2>Optimization Recommendations</h2>
                <p>AI-generated optimization suggestions with impact estimates.</p>
                <a href="file://{Path(report_paths.get('recommendations', '')).absolute()}" target="_blank" class="report-link">View Report</a>
            </div>

    """

        # Add flame graph cards if available
        for report_type, path in report_paths.items():
            if report_type.startswith('flame_cpu_'):
                agent_id = report_type.replace('flame_cpu_', '')
                html += f"""
            <div class="card">
                <h2>CPU Flame Graph - {agent_id}</h2>
                <p>Interactive flame graph showing CPU hotspots.</p>
                <a href="file://{Path(path).absolute()}" target="_blank" class="report-link">View Graph</a>
            </div>
    """

        html += """
        </div>
    </div>
</body>
</html>
        """

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)

    async def run_benchmark(
        self,
        colony: Any,
        workload: Callable,
        benchmark_name: str,
        iterations: int = 100,
    ) -> Dict[str, Any]:
        """
        Run a simple benchmark with timing and metrics.

        Args:
            colony: The POLLN colony
            workload: Workload function
            benchmark_name: Name of the benchmark
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        print(f"Running benchmark: {benchmark_name}")
        print(f"  Iterations: {iterations}")

        timings = []

        for i in range(iterations):
            start = time.time()
            try:
                await workload(colony)
                timings.append(time.time() - start)
            except Exception as e:
                print(f"    Iteration {i} failed: {e}")

        if not timings:
            return {'error': 'All iterations failed'}

        import statistics

        results = {
            'benchmark': benchmark_name,
            'iterations': iterations,
            'successful': len(timings),
            'total_time': sum(timings),
            'avg_time': statistics.mean(timings),
            'min_time': min(timings),
            'max_time': max(timings),
            'median_time': statistics.median(timings),
            'std_dev': statistics.stdev(timings) if len(timings) > 1 else 0,
        }

        print(f"\nResults:")
        print(f"  Average: {format_duration(results['avg_time'])}")
        print(f"  Median: {format_duration(results['median_time'])}")
        print(f"  Min: {format_duration(results['min_time'])}")
        print(f"  Max: {format_duration(results['max_time'])}")

        return results

    def clear(self) -> None:
        """Clear all profilers and collected data."""
        self.agent_profiler.clear()
        self.colony_profiler.clear()
        self.memory_profiler.clear()
        self.trace_analyzer.clear()
        self.recommender.clear()
        self.metrics.clear()


async def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='POLLN Profiler - Comprehensive profiling toolkit'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=60,
        help='Profiling duration in seconds'
    )
    parser.add_argument(
        '--warmup',
        type=float,
        default=5,
        help='Warmup duration in seconds'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Iterations for agent profiling'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports/profiling',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--no-flame-graphs',
        action='store_true',
        help='Disable flame graph generation'
    )
    parser.add_argument(
        '--no-recommendations',
        action='store_true',
        help='Disable optimization recommendations'
    )

    args = parser.parse_args()

    # This is a placeholder - in real usage, you would provide
    # actual colony and workload
    print("POLLN Profiler")
    print("=" * 60)
    print()
    print("To use the profiler programmatically:")
    print()
    print("  from profile_runner import ProfileRunner")
    print("  runner = ProfileRunner()")
    print("  await runner.run_profile(colony, workload, duration_seconds=60)")
    print()
    print("Or import individual profilers:")
    print()
    print("  from agent_profiler import AgentProfiler")
    print("  from colony_profiler import ColonyProfiler")
    print("  from memory_profiler import MemoryProfiler")
    print("  # ... etc")
    print()


if __name__ == '__main__':
    # Import dataclass
    from dataclasses import dataclass
    asyncio.run(main())
