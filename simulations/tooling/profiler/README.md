# POLLN Profiler

Comprehensive Python profiling toolkit for analyzing and optimizing POLLN (Pattern-Organized Large Language Network) performance.

## Overview

The POLLN Profiler provides production-grade profiling tools to identify bottlenecks and optimize system performance across multiple dimensions:

- **Agent Profiling**: CPU usage, memory allocations, A2A communication patterns
- **Colony Profiling**: Throughput, latency, queue depths, resource allocation
- **Memory Profiling**: Heap allocations, KV-cache usage, leak detection
- **Trace Analysis**: Distributed tracing, bottleneck identification, cascading delays
- **Flame Graphs**: Interactive CPU, memory, and A2A flow visualizations
- **Optimization Recommendations**: AI-generated suggestions with impact estimates

## Installation

The profiler requires Python 3.8+ and the following dependencies:

```bash
pip install psutil
```

Optional dependencies for full functionality:

```bash
pip install pytest pytest-asyncio  # For testing
```

## Quick Start

### Programmatic Usage

```python
import asyncio
from profile_runner import ProfileRunner

async def main():
    # Create profiler
    runner = ProfileRunner(output_dir='reports/profiling')

    # Define your workload
    async def workload(colony):
        # Your POLLN colony operations here
        await colony.process_request()
        # ...

    # Run comprehensive profiling
    report_paths = await runner.run_profile(
        colony=colony,
        workload=workload,
        duration_seconds=60,
        warmup_seconds=5,
        iterations=10,
    )

    # View results
    print(f"Dashboard: {report_paths['dashboard']}")

asyncio.run(main())
```

### Individual Profilers

```python
from agent_profiler import AgentProfiler

# Profile a single agent
profiler = AgentProfiler()
profile = await profiler.profile_agent(agent, workload, iterations=10)

# Generate reports
profiler.generate_report(format='html')
profiler.generate_report(format='json')
profiler.generate_report(format='text')
```

## Components

### 1. Agent Profiler (`agent_profiler.py`)

Profiles individual POLLN agents for CPU, memory, and A2A communication.

**Features:**
- CPU usage and time profiling with cProfile
- Memory allocation tracking with tracemalloc
- A2A send/receive tracking
- Hotspot identification
- Value function tracking

**Usage:**
```python
from agent_profiler import AgentProfiler

profiler = AgentProfiler()
profile = await profiler.profile_agent(agent, workload, iterations=10)

print(f"CPU: {profile.cpu_percent}%")
print(f"Memory: {profile.memory_mb}MB")
print(f"A2A Sent: {profile.a2a_sent_count}")
print(f"Hotspots: {len(profile.hotspots)}")
```

### 2. Colony Profiler (`colony_profiler.py`)

Profiles colony-level metrics: throughput, latency, queue depths.

**Features:**
- Throughput measurements (requests/sec, A2A packages/sec)
- Latency percentiles (p50, p90, p95, p99)
- Queue depth tracking
- Agent count monitoring
- Topology change tracking

**Usage:**
```python
from colony_profiler import ColonyProfiler

profiler = ColonyProfiler(sample_interval=0.1)
await profiler.start_profiling(colony)

# ... run workload ...

profile = await profiler.stop_profiling()
print(f"Throughput: {profile.requests_per_second}/sec")
print(f"p99 Latency: {profile.p99_latency}s")
```

### 3. Memory Profiler (`memory_profiler.py`)

Profiles memory usage, detects leaks, analyzes fragmentation.

**Features:**
- Heap allocation tracking
- KV-cache usage estimation
- Memory leak detection
- Fragmentation analysis
- GC pressure monitoring

**Usage:**
```python
from memory_profiler import MemoryProfiler

profiler = MemoryProfiler(snapshot_interval=1.0)
await profiler.start_profiling()

# ... run workload ...

profile = await profiler.stop_profiling()
print(f"Peak RSS: {profile.peak_rss_bytes} bytes")
print(f"Leaks detected: {len(profile.suspected_leaks)}")
print(f"Fragmentation: {profile.fragmentation_ratio:.2%}")
```

### 4. Trace Analyzer (`trace_analyzer.py`)

Analyzes distributed A2A package traces for bottlenecks.

**Features:**
- Trace event collection and analysis
- Slow agent identification
- Bottleneck link detection
- Cascading delay detection
- Agent utilization calculation

**Usage:**
```python
from trace_analyzer import TraceAnalyzer, TraceEvent

analyzer = TraceAnalyzer()

# Add trace events
analyzer.add_event(TraceEvent(
    timestamp=time.time(),
    event_type='send',
    agent_id='agent-1',
    package_id='pkg-1',
    causal_chain_id='chain-1',
))

# Analyze
analysis = analyzer.analyze()
print(f"Total traces: {analysis.total_traces}")
print(f"p99 duration: {analysis.p99_duration}s")
print(f"Slowest agents: {analysis.slowest_agents}")
```

### 5. Flame Graph Generator (`flame_graph_generator.py`)

Generates interactive flame graphs for performance visualization.

**Features:**
- CPU flame graphs from profiling data
- Memory flame graphs from allocation data
- A2A flow graphs for communication patterns
- Interactive HTML with zoom and filter
- Side-by-side comparison graphs

**Usage:**
```python
from flame_graph_generator import FlameGraphGenerator

generator = FlameGraphGenerator()

# CPU flame graph
cpu_html = generator.generate_cpu_flame_graph(
    profile_data,
    title="CPU Flame Graph"
)

# Memory flame graph
mem_html = generator.generate_memory_flame_graph(
    memory_data,
    title="Memory Flame Graph"
)

# Comparison graph
comp_html = generator.generate_comparison_graph(
    [profile1_data, profile2_data],
    ['Before', 'After']
)
```

### 6. Optimization Recommender (`optimization_recommender.py`)

Generates actionable optimization recommendations from profiling data.

**Features:**
- Analyzes CPU bottlenecks
- Identifies memory issues
- Suggests A2A optimizations
- Recommends architectural changes
- Estimates speedup and memory reduction
- Prioritizes by impact and effort

**Usage:**
```python
from optimization_recommender import OptimizationRecommender

recommender = OptimizationRecommender()

# Add profiling data
recommender.add_agent_profile(agent_profile)
recommender.add_colony_profile(colony_profile)
recommender.add_memory_profile(memory_profile)

# Generate recommendations
report = recommender.generate_recommendations()

print(f"Total recommendations: {report.total_recommendations}")
print(f"Quick wins: {len(report.quick_wins)}")
print(f"Estimated speedup: {report.estimated_total_speedup:.2f}x")
```

### 7. Profile Runner (`profile_runner.py`)

Orchestrates all profilers for comprehensive analysis.

**Features:**
- Runs all profilers in parallel
- Generates combined dashboard
- Supports custom workloads
- Configurable duration and iterations
- Automatic report generation

**Usage:**
```python
from profile_runner import ProfileRunner

runner = ProfileRunner()

reports = await runner.run_profile(
    colony=colony,
    workload=workload,
    duration_seconds=60,
    warmup_seconds=5,
    iterations=10,
    generate_flame_graphs=True,
    generate_recommendations=True,
)

# reports contains paths to all generated files
dashboard_path = reports['dashboard']
```

## Output Format

Generated reports are saved to `reports/profiling/`:

```
reports/profiling/
├── agent_profile_20250307_120000.json    # Agent profiling data
├── colony_profile_20250307_120000.html   # Colony metrics dashboard
├── memory_profile_20250307_120000.html   # Memory analysis report
├── flame_graph_cpu_20250307_120000.html  # Interactive CPU flame graph
├── flame_graph_memory_20250307_120000.html # Memory flame graph
├── trace_analysis_20250307_120000.json   # Distributed trace analysis
├── recommendations_20250307_120000.html  # Optimization suggestions
└── dashboard_20250307_120000.html        # Combined dashboard
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest test_profiler.py -v

# Run specific test class
pytest test_profiler.py::TestAgentProfiler -v

# Run with coverage
pytest test_profiler.py --cov=. --cov-report=html
```

## Utilities

### Metrics Collector (`utils/metrics.py`)

Thread-safe metrics collection infrastructure:

```python
from utils.metrics import MetricsCollector

collector = MetricsCollector()

# Register metrics
collector.register_counter('requests')
collector.register_histogram('latency', buckets=[0.001, 0.01, 0.1, 1.0])

# Record metrics
collector.increment_counter('requests')
collector.observe_histogram('latency', 0.05)

# Get statistics
stats = collector.get_histogram_stats('latency')
print(f"p99: {stats['p99']}")
```

### Decorators (`utils/decorators.py`)

Profiling decorators for automatic instrumentation:

```python
from utils.decorators import profile_agent, time_execution

@profile_agent(metric_name="my_process")
async def process(self, input_data):
    # Automatically profiled
    return await self._do_work(input_data)

@time_execution()
def my_function():
    # Execution time tracked
    pass
```

### Formatters (`utils/formatters.py`)

Helper functions for formatting profiling data:

```python
from utils.formatters import (
    format_duration,
    format_bytes,
    format_table,
    format_speedup,
)

print(format_duration(123.456))  # "2m 3.46s"
print(format_bytes(1048576))     # "1.00 MB"
print(format_speedup(10.0, 5.0)) # "2.00x faster"
```

## Advanced Usage

### Custom Workloads

Define custom workloads for profiling:

```python
async def custom_workload(colony):
    """Custom workload for profiling."""
    for i in range(100):
        # Spawn agents
        await colony.spawn_agent(config)

        # Process requests
        await colony.process_request(data)

        # Send A2A packages
        await agent.send_a2a(target_id, payload)

reports = await runner.run_profile(
    colony,
    custom_workload,
    duration_seconds=120,
)
```

### Filtered Agent Profiling

Profile specific agents:

```python
reports = await runner.run_profile(
    colony,
    workload,
    agent_ids=['agent-1', 'agent-2', 'agent-3'],  # Only these agents
)
```

### Real-time Metrics

Access real-time metrics during profiling:

```python
profiler = ColonyProfiler()
await profiler.start_profiling(colony)

# Get real-time stats
while True:
    metrics = profiler.get_realtime_metrics()
    print(f"Active agents: {metrics['agents']['active']}")
    print(f"Throughput: {metrics['throughput']['requests_per_sec']}/sec")
    await asyncio.sleep(1)
```

## Architecture

```
profiler/
├── agent_profiler.py          # Agent-level profiling
├── colony_profiler.py         # Colony-level profiling
├── memory_profiler.py         # Memory analysis
├── trace_analyzer.py          # Distributed tracing
├── flame_graph_generator.py   # Visualization
├── optimization_recommender.py # Recommendations
├── profile_runner.py          # Orchestrator
├── test_profiler.py           # Test suite
├── utils/
│   ├── __init__.py
│   ├── metrics.py             # Metrics collection
│   ├── decorators.py          # Profiling decorators
│   └── formatters.py          # Output formatting
└── README.md                  # This file
```

## Contributing

When adding new profiling capabilities:

1. Create a new profiler class following the existing pattern
2. Add corresponding tests in `test_profiler.py`
3. Update this README with usage examples
4. Ensure integration with `ProfileRunner`

## License

Part of the POLLN project. See main repository for license details.

## Related Documentation

- [PROFILING_GUIDE.md](PROFILING_GUIDE.md) - Detailed profiling guide
- [OPTIMIZATION.md](OPTIMIZATION.md) - Optimization strategies and patterns
