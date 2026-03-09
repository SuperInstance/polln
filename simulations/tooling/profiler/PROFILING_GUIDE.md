# POLLN Profiling Guide

Comprehensive guide to profiling POLLN systems for performance analysis and optimization.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Profiling Agents](#profiling-agents)
3. [Profiling Colonies](#profiling-colonies)
4. [Memory Profiling](#memory-profiling)
5. [Distributed Tracing](#distributed-tracing)
6. [Flame Graphs](#flame-graphs)
7. [Optimization](#optimization)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

The profiler is part of the POLLN simulations toolkit:

```bash
cd simulations/tooling/profiler
```

### Your First Profile

```python
import asyncio
from profile_runner import ProfileRunner

async def main():
    # Setup
    runner = ProfileRunner(output_dir='reports/profiling')

    # Define workload
    async def workload(colony):
        await colony.process_batch([
            {'input': f'request-{i}'}
            for i in range(100)
        ])

    # Profile
    reports = await runner.run_profile(
        colony=my_colony,
        workload=workload,
        duration_seconds=30,
    )

    # View results
    print(f"Open: {reports['dashboard']}")

asyncio.run(main())
```

## Profiling Agents

### When to Profile Agents

Profile individual agents when:
- An agent is slower than expected
- Memory usage is high
- A2A communication is frequent
- You need to optimize specific agents

### Basic Agent Profiling

```python
from agent_profiler import AgentProfiler

profiler = AgentProfiler()

# Profile a single agent
profile = await profiler.profile_agent(
    agent=my_agent,
    workload=agent_workload,
    iterations=50,
    warmup_iterations=5,
)

# Analyze results
print(f"CPU: {profile.cpu_percent}%")
print(f"Memory: {profile.memory_mb:.2f}MB")
print(f"Avg Process Time: {profile.avg_process_time:.4f}s")

# Check hotspots
for hotspot in profile.hotspots[:5]:
    print(f"  {hotspot['function']}: {hotspot['total_time']:.2f}s")
```

### Comparing Agents

```python
# Profile multiple agents
profiles = {}
for agent_id in ['agent-1', 'agent-2', 'agent-3']:
    agent = colony.agents[agent_id]
    profile = await profiler.profile_agent(agent, workload)
    profiles[agent_id] = profile

# Compare
comparison = profiler.compare_agents(list(profiles.keys()))
print("CPU Comparison:")
for agent in comparison['cpu_comparison']:
    print(f"  {agent['agent_id']}: {agent['value']:.2f}%")
```

### Tracking A2A Communication

```python
profiler = AgentProfiler()

# A2A tracking is automatic when profiling
profile = await profiler.profile_agent(agent, workload)

print(f"A2A Sent: {profile.a2a_sent_count}")
print(f"A2A Received: {profile.a2a_received_count}")
print(f"A2A Sent Bytes: {profile.a2a_sent_bytes}")
print(f"A2A Received Bytes: {profile.a2a_received_bytes}")
```

## Profiling Colonies

### When to Profile Colonies

Profile at the colony level when:
- You need overall system metrics
- Analyzing throughput and latency
- Monitoring resource utilization
- Investigating queue depths

### Basic Colony Profiling

```python
from colony_profiler import ColonyProfiler

profiler = ColonyProfiler(sample_interval=0.1)

# Start profiling
await profiler.start_profiling(colony)

# Run your workload
await run_workload(colony, duration=60)

# Stop and get results
profile = await profiler.stop_profiling()

# Analyze
print(f"Throughput: {profile.requests_per_second:.2f}/sec")
print(f"p99 Latency: {profile.p99_latency:.4f}s")
print(f"Active Agents: {profile.active_agents}/{profile.total_agents}")
```

### Real-time Monitoring

```python
profiler = ColonyProfiler()
await profiler.start_profiling(colony)

# Monitor in real-time
while True:
    metrics = profiler.get_realtime_metrics()
    print(f"Requests/sec: {metrics['throughput']['requests_per_sec']:.1f}")
    print(f"Active agents: {metrics['agents']['active']}")
    print(f"p99 latency: {metrics['latency']['p99']:.4f}s")
    await asyncio.sleep(5)
```

### Tracking Custom Metrics

```python
# Track agent lifecycle
profiler.track_agent_spawn()
profiler.track_agent_kill()

# Track topology changes
profiler.track_topology_change()

# Record queue depths
profiler.record_queue_depth(queue_len, agent_id='agent-1')
profiler.record_queue_depth(queue_len, agent_id='agent-2')

# Record latencies
profiler.record_latency(latency_seconds)
```

## Memory Profiling

### When to Use Memory Profiling

Profile memory when:
- Memory usage is growing unexpectedly
- You suspect memory leaks
- Analyzing KV-cache efficiency
- Investigating GC pressure

### Basic Memory Profiling

```python
from memory_profiler import MemoryProfiler

profiler = MemoryProfiler(snapshot_interval=1.0)

# Start profiling
await profiler.start_profiling(track_allocations=True)

# Run workload
await run_workload(colony)

# Stop and analyze
profile = await profiler.stop_profiling()

# Check for issues
print(f"Peak RSS: {format_bytes(profile.peak_rss_bytes)}")
print(f"Fragmentation: {profile.fragmentation_ratio:.2%}")
print(f"Suspected leaks: {len(profile.suspected_leaks)}")

# Examine leaks
for leak in profile.suspected_leaks[:5]:
    print(f"  {leak.object_type}:")
    print(f"    Growth: {leak.growth_rate:.0f} bytes/sec")
    print(f"    Total: {format_bytes(leak.total_bytes)}")
```

### KV-Cache Analysis

```python
# The profiler tracks KV-cache automatically
profile = await profiler.stop_profiling()

print(f"KV-Cache Usage: {format_bytes(profile.kv_cache_usage_bytes)}")
print(f"KV-Cache Fragmentation: {profile.kv_cache_fragmentation:.2%}")
```

### Heap Histogram

```python
# Generate a detailed heap histogram
histogram_path = profiler.generate_heap_histogram(limit=50)
print(f"Heap histogram: {histogram_path}")
```

## Distributed Tracing

### When to Use Tracing

Use distributed tracing when:
- Investigating cascading delays
- Finding bottlenecks in agent chains
- Analyzing A2A communication patterns
- Optimizing causal chains

### Basic Tracing

```python
from trace_analyzer import TraceAnalyzer, TraceEvent

analyzer = TraceAnalyzer()

# Add trace events
event = TraceEvent(
    timestamp=time.time(),
    event_type='send',  # 'send', 'receive', 'process_start', 'process_end'
    agent_id='agent-1',
    package_id='pkg-123',
    causal_chain_id='chain-456',
    parent_ids=['parent-pkg-789'],
    metadata={'size': 1024},
)
analyzer.add_event(event)

# Analyze
analysis = analyzer.analyze()

# Find bottlenecks
print("Slowest Agents:")
for agent in analysis.slowest_agents[:5]:
    print(f"  {agent['agent_id']}: {format_duration(agent['avg_time'])}")

print("\nBottleneck Links:")
for link in analysis.bottleneck_links[:5]:
    print(f"  {link['sender']} -> {link['receiver']}: {format_duration(link['avg_latency'])}")

print("\nCascading Delays:")
for delay in analysis.cascading_delays[:5]:
    print(f"  {delay['from_agent']} -> {delay['to_agent']}: {delay['multiplier']:.2f}x")
```

### Loading/Saving Traces

```python
# Save traces
analyzer.save_to_file('traces/my_trace.json')

# Load traces
analyzer = TraceAnalyzer()
analyzer.load_from_file('traces/my_trace.json')
analysis = analyzer.analyze()
```

## Flame Graphs

### CPU Flame Graphs

```python
from flame_graph_generator import FlameGraphGenerator

generator = FlameGraphGenerator()

# Generate from agent profile
html_path = generator.generate_cpu_flame_graph(
    profile_data={
        'hotspots': agent_profile.hotspots
    },
    title="CPU Flame Graph - Agent X",
)

# Open in browser
import webbrowser
webbrowser.open(f'file://{Path(html_path).absolute()}')
```

### Memory Flame Graphs

```python
# Generate from memory profiling data
html_path = generator.generate_memory_flame_graph(
    memory_data=memory_profile.suspected_leaks,
    title="Memory Flame Graph - Allocations",
)
```

### Comparison Graphs

```python
# Compare before/after optimization
html_path = generator.generate_comparison_graph(
    profiles=[before_profile, after_profile],
    labels=['Before Optimization', 'After Optimization'],
    title="Optimization Impact",
)
```

## Optimization

### Generating Recommendations

```python
from optimization_recommender import OptimizationRecommender

recommender = OptimizationRecommender()

# Add profiling data
recommender.add_agent_profile(agent_profile_data)
recommender.add_colony_profile(colony_profile_data)
recommender.add_memory_profile(memory_profile_data)
recommender.add_trace_analysis(trace_analysis_data)

# Generate recommendations
report = recommender.generate_recommendations()

# Review
print(f"Total recommendations: {report.total_recommendations}")
print(f"Critical: {report.critical_count}")
print(f"High priority: {report.high_count}")

# Quick wins (high impact, low effort)
print("\nQuick Wins:")
for rec in report.quick_wins:
    print(f"  [{rec.priority.value.upper()}] {rec.title}")
    print(f"    {rec.description}")
    print(f"    Speedup: {rec.estimated_speedup:.2f}x, Effort: {rec.implementation_effort}")
```

### Applying Recommendations

Common optimization patterns:

#### 1. Agent Batching

```python
# Before: Process one at a time
for item in items:
    await agent.process(item)

# After: Batch processing
batch_size = 10
for i in range(0, len(items), batch_size):
    batch = items[i:i+batch_size]
    await agent.process_batch(batch)
```

#### 2. A2A Compression

```python
# Compress large A2A packages
if len(payload) > 1024:  # > 1KB
    payload = compress(payload)

await agent.send_a2a(target_id, payload)
```

#### 3. Connection Pooling

```python
# Reuse connections instead of creating new ones
class AgentPool:
    def __init__(self, agent_type, pool_size=5):
        self.pool = asyncio.Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put_nowait(create_agent(agent_type))

    async def with_agent(self, func):
        agent = await self.pool.get()
        try:
            return await func(agent)
        finally:
            self.pool.put_nowait(agent)
```

#### 4. KV-Cache Offloading

```python
# Offload KV-cache to shared storage
async def offload_kv_cache(agent):
    if agent.kv_cache_size() > threshold:
        await shared_cache.store(agent.id, agent.kv_cache)
        agent.kv_cache_clear()
```

## Best Practices

### 1. Always Warm Up

```python
# Warm up before profiling
for _ in range(warmup_iterations):
    await workload(agent)

# Now profile
profiler = AgentProfiler()
profile = await profiler.profile_agent(agent, workload)
```

### 2. Use Representative Workloads

```python
# Use realistic workloads, not synthetic ones
async def realistic_workload(colony):
    # Mix of operations
    await colony.spawn_agent(config)
    await colony.process_request(data)
    await agent.send_a2a(target, payload)
    # ...
```

### 3. Profile in Isolation

```python
# Profile one component at a time
# Don't profile agent + colony + memory simultaneously
# unless using the orchestrator
```

### 4. Monitor Overhead

```python
# Profiling adds overhead
# Account for it in your analysis
base_time = time.time()
await workload(agent)
unprofiled_time = time.time() - base_time

profile = await profiler.profile_agent(agent, workload)
profiled_time = profile.total_process_time

overhead = (profiled_time - unprofiled_time) / unprofiled_time
print(f"Profiling overhead: {overhead:.2%}")
```

### 5. Save and Compare

```python
# Save profiles for comparison
profiler.generate_report(profile, format='json')

# Load and compare later
baseline = load_profile('baseline.json')
optimized = load_profile('optimized.json')

speedup = baseline.avg_process_time / optimized.avg_process_time
print(f"Speedup: {speedup:.2f}x")
```

## Troubleshooting

### No Data Collected

**Problem**: Profiler returns empty results.

**Solutions**:
- Ensure workload actually runs
- Check that agents are active
- Verify instrumentation is working
- Increase profiling duration

### Memory Profiler Shows No Leaks

**Problem**: Suspected leak but not detected.

**Solutions**:
- Increase profiling duration
- Lower growth rate threshold
- Check if objects are actually being leaked
- Review object type tracking

### Flame Graphs Are Empty

**Problem**: Flame graph has no data.

**Solutions**:
- Ensure CPU profiling is enabled
- Check that workload runs long enough
- Verify hotspots are being captured
- Check profile data format

### High Overhead

**Problem**: Profiling slows down system too much.

**Solutions**:
- Increase sample interval
- Reduce number of profiled agents
- Use sampling instead of full profiling
- Profile specific components only

## Additional Resources

- [README.md](README.md) - Quick reference and API overview
- [OPTIMIZATION.md](OPTIMIZATION.md) - Deep dive into optimization strategies
- [test_profiler.py](test_profiler.py) - Example usage in tests
