# POLLN Benchmark Guide

Comprehensive guide for using and extending the POLLN benchmark system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Running Benchmarks](#running-benchmarks)
3. [Understanding Results](#understanding-results)
4. [Regression Detection](#regression-detection)
5. [Trend Analysis](#trend-analysis)
6. [Baseline Management](#baseline-management)
7. [CI/CD Integration](#cicd-integration)
8. [Custom Benchmarks](#custom-benchmarks)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Required Python packages
pip install numpy scipy matplotlib psutil
```

### Initial Setup

```bash
# 1. Install POLLN
npm install
npm run build

# 2. Create directory structure
mkdir -p reports/benchmarks/{current,trends,comparisons,baselines,history,cache}

# 3. Run initial benchmarks
python simulations/tooling/benchmarks/benchmark_suite.py --scale small

# 4. Create baseline
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name initial \
    --results reports/benchmarks/current/benchmarks_*.json \
    --description "Initial baseline"
```

---

## Running Benchmarks

### Basic Usage

```bash
# Run all benchmarks (default: small scale)
python simulations/tooling/benchmarks/benchmark_suite.py

# Run with medium scale
python simulations/tooling/benchmarks/benchmark_suite.py --scale medium

# Run specific category
python simulations/tooling/benchmarks/benchmark_suite.py --category agents

# Run with custom output directory
python simulations/tooling/benchmarks/benchmark_suite.py \
    --output /custom/output/path
```

### Parallel Execution

```bash
# Run benchmarks in parallel (faster)
python simulations/tooling/benchmarks/benchmark_runner.py --parallel

# Control number of workers
python simulations/tooling/benchmarks/benchmark_runner.py --workers 4

# Sequential execution (slower but more predictable)
python simulations/tooling/benchmarks/benchmark_runner.py --sequential
```

### Benchmark Categories

| Category | Benchmarks | Description |
|----------|-----------|-------------|
| `agents` | creation, activation, decision | Individual agent performance |
| `colony` | coordination, communication | Multi-agent coordination |
| `learning` | hebbian, dreaming | Learning system performance |
| `kv_cache` | anchor, ann | KV-cache system performance |

### Understanding Scales

**Small Scale** - Fast, suitable for CI/CD:
- Colony: 50 agents
- Messages: 25
- Synapses: 500
- Index: 5K items
- Runtime: ~30 seconds

**Medium Scale** - Standard benchmarks:
- Colony: 100 agents
- Messages: 50
- Synapses: 1K
- Index: 10K items
- Runtime: ~2 minutes

**Large Scale** - Stress testing:
- Colony: 500 agents
- Messages: 200
- Synapses: 5K
- Index: 50K items
- Runtime: ~10 minutes

---

## Understanding Results

### Benchmark Result Structure

Each benchmark produces:

```json
{
  "name": "agent_creation",
  "iterations": 100,
  "total_time": 1.234,
  "avg_latency_ms": 12.34,
  "min_latency_ms": 8.5,
  "max_latency_ms": 25.6,
  "p50_latency_ms": 11.8,
  "p95_latency_ms": 18.2,
  "p99_latency_ms": 22.1,
  "throughput_ops": 81.04,
  "memory_mb": 45.6,
  "cpu_percent": 25.3,
  "success_rate": 1.0
}
```

### Key Metrics

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| `throughput_ops` | Operations per second | Higher | Lower |
| `p50_latency_ms` | Median latency | Lower | Higher |
| `p95_latency_ms` | 95th percentile latency | Lower | Higher |
| `p99_latency_ms` | 99th percentile latency | Lower | Higher |
| `memory_mb` | Memory usage | Lower | Higher |
| `success_rate` | Success rate (0-1) | 1.0 | <0.95 |

### Interpreting Percentiles

- **P50 (Median)** - Typical user experience
- **P95** - 95% of users see this performance or better
- **P99** - Worst-case performance for 99% of users

Example: If P95 latency is 100ms, then 95% of operations complete within 100ms.

---

## Regression Detection

### How It Works

The regression detector:

1. **Loads baseline** - Previous benchmark results
2. **Compares metrics** - Current vs baseline
3. **Calculates change** - Percentage difference
4. **Determines severity** - Based on threshold
5. **Generates alerts** - For significant regressions

### Severity Levels

| Severity | Threshold | Action |
|----------|-----------|--------|
| **CRITICAL** | >50% worse | Must fix before merging |
| **HIGH** | 20-50% worse | Should fix before merging |
| **MEDIUM** | 10-20% worse | Monitor, consider fixing |
| **LOW** | 5-10% worse | Note, may accumulate |

### Running Regression Detection

```bash
# Basic regression check
python simulations/tooling/benchmarks/regression_detector.py

# Custom confidence level
python simulations/tooling/benchmarks/regression_detector.py --confidence 0.99

# Specify files
python simulations/tooling/benchmarks/regression_detector.py \
    --baseline baseline_v1.0.json \
    --current benchmarks_latest.json
```

### Interpreting Regression Alerts

```
🔴 CRITICAL: P95 Latency
   Baseline: 100.00
   Current:  180.00
   Change:   +80.00%
   Confidence: 95%

   💡 CRITICAL: P95 Latency degraded significantly.
   This change MUST be reverted or fixed before merging.
```

**Action Steps:**

1. **Verify** - Is regression real or noise?
2. **Investigate** - What changed in the commit?
3. **Fix** - Optimize the code or revert changes
4. **Re-test** - Run benchmarks again
5. **Document** - Add comment explaining fix

---

## Trend Analysis

### Purpose

Trend tracking helps identify:

- **Gradual degradation** - Slow performance decline over time
- **Improvements** - Positive performance trends
- **Anomalies** - Unusual data points
- **Predictions** - Future performance trajectory

### Running Trend Analysis

```bash
# Analyze all trends
python simulations/tooling/benchmarks/trend_tracker.py

# Generate visualizations
python simulations/tooling/benchmarks/trend_tracker.py --visualize

# Specific metrics only
python simulations/tooling/benchmarks/trend_tracker.py \
    --metrics agent_creation_avg_latency colony_coordination_throughput

# Specific branch
python simulations/tooling/benchmarks/trend_tracker.py --branch develop
```

### Understanding Trend Reports

```
Performance Trend Summary
==================================================
✅ Improving: 5 metric(s)
⚠️  Degrading: 2 metric(s)
➡️  Stable: 8 metric(s)

✨ 3 anomaly/ies detected
```

### Trend Metrics

| Metric | Description |
|--------|-------------|
| `slope` | Rate of change per day |
| `correlation` | Correlation coefficient (-1 to 1) |
| `is_significant` | Statistically significant trend |
| `trend_direction` | improving, degrading, stable |
| `confidence` | Confidence in trend (0-1) |
| `predictions` | Future values (1, 7, 30 days) |

### Reading Trend Charts

- **Blue line** - Actual data points
- **Red dashed line** - Smoothed trend
- **Red X marks** - Detected anomalies

---

## Baseline Management

### What is a Baseline?

A baseline is a reference point for performance comparisons. It represents "good" performance that subsequent changes are measured against.

### Creating Baselines

```bash
# Create from current results
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name v1.0 \
    --results reports/benchmarks/current/benchmarks_*.json \
    --description "Version 1.0 baseline"

# List all baselines
python simulations/tooling/benchmarks/baseline_manager.py list
```

### Updating Baselines

```bash
# Update with improvements (automatic verification)
python simulations/tooling/benchmarks/baseline_manager.py update \
    --results reports/benchmarks/current/benchmarks_*.json \
    --name v1.0

# Approve pending baseline
python simulations/tooling/benchmarks/baseline_manager.py approve \
    --name v1.0
```

### When to Update Baselines

**Update when:**
- Genuine improvement verified
- Architecture change (new normal)
- System configuration changed
- Previous baseline outdated

**Don't update when:**
- Noise/fluctuation
- Only slight improvement (<5%)
- Regression detected

### Baseline Lifecycle

```
PENDING (new baseline)
    ↓
[Verification]
    ↓
ACTIVE (current reference) ← REGRESSION CHECKS
    ↓
[New baseline created]
    ↓
ARCHIVED (historical reference)
```

---

## CI/CD Integration

### GitHub Actions Setup

The benchmark system includes a ready-to-use GitHub Actions workflow:

```yaml
# .github/workflows/benchmarks.yml
name: Benchmarks
on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run benchmarks
        run: python simulations/tooling/benchmarks/benchmark_ci.py
```

### CI Pipeline Stages

1. **Setup** - Install dependencies
2. **Execute** - Run benchmarks
3. **Compare** - Check against baseline
4. **Report** - Generate results
5. **Fail** - Exit on critical regressions

### PR Comments

The system automatically posts comments on PRs:

```markdown
## 📊 Benchmark Results

✅ **Status:** All benchmarks passed, no regressions detected

**Commit:** `abc12345`
**Branch:** `feature/new-feature`

### Summary

✅ No critical regressions detected
```

### Nightly Benchmarks

Configure scheduled runs for full-scale benchmarks:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

---

## Custom Benchmarks

### Creating a New Benchmark

```python
# In benchmark_suite.py

def benchmark_custom_operation(
    self,
    config: Optional[BenchmarkConfig] = None
) -> BenchmarkResult:
    """Benchmark custom operation"""

    if config is None:
        config = BenchmarkConfig(
            name="custom_operation",
            warmup_iterations=5,
            benchmark_iterations=50
        )

    def custom_operation():
        # Your operation here
        result = perform_operation()
        return result

    result = self._run_benchmark(
        "custom_operation",
        custom_operation,
        config
    )
    self.results.append(result)
    return result
```

### Adding to Categories

```python
# In benchmark_runner.py

def create_default_jobs(self, scale: str = "small") -> List[BenchmarkJob]:
    jobs = super().create_default_jobs(scale)

    # Add custom job
    jobs.append(BenchmarkJob(
        name="custom_operation",
        category="custom",
        scale=scale,
        script="benchmark_suite.py",
        args={},
        priority=5
    ))

    return jobs
```

### Testing Custom Benchmarks

```python
# In test_benchmarks.py

class TestCustomBenchmarks(unittest.TestCase):
    def test_custom_benchmark(self):
        suite = BenchmarkSuite()
        result = suite.benchmark_custom_operation()

        self.assertIsNotNone(result)
        self.assertGreater(result.throughput_ops, 0)
        self.assertEqual(result.success_rate, 1.0)
```

---

## Performance Optimization

### Common Bottlenecks

| Area | Symptoms | Solutions |
|------|----------|-----------|
| **Agent Creation** | High creation latency | Object pooling, lazy init |
| **Decision Making** | Slow Plinko selection | Cache proposals, reduce candidates |
| **Communication** | Low throughput | Batch messages, async send |
| **Learning** | Slow Hebbian updates | Vectorized operations |
| **KV-Cache** | Slow ANN search | Better indexing, reduce dimensions |

### Optimization Techniques

1. **Profiling** - Identify hotspots
   ```python
   import cProfile
   cProfile.run('benchmark_function()', 'output.prof')
   ```

2. **Vectorization** - Use NumPy operations
   ```python
   # Slow
   for i in range(len(weights)):
       weights[i] += delta[i]

   # Fast
   weights += delta  # NumPy vectorized operation
   ```

3. **Caching** - Memoize expensive computations
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def expensive_computation(x):
       # ...
   ```

4. **Parallelization** - Use multiprocessing
   ```python
   from multiprocessing import Pool

   with Pool(4) as p:
       results = p.map(benchmark_function, inputs)
   ```

---

## Troubleshooting

### Common Issues

#### Issue: "No baseline found"

**Cause:** Baseline file missing or not in correct location

**Solution:**
```bash
# Create baseline
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name main \
    --results reports/benchmarks/current/benchmarks_*.json

# Verify location
ls reports/benchmarks/baselines/
```

#### Issue: "All iterations failed"

**Cause:** Benchmark function throwing exceptions

**Solution:**
1. Check benchmark implementation
2. Verify dependencies installed
3. Check for race conditions in parallel execution
4. Run with `--sequential` flag

#### Issue: "False positive regression"

**Cause:** Statistical noise in measurements

**Solution:**
1. Increase `benchmark_iterations`
2. Run multiple times and average
3. Check for system load/background processes
4. Adjust confidence level

#### Issue: "CI fails locally but not in CI"

**Cause:** Environment differences

**Solution:**
1. Check Python version mismatch
2. Verify all dependencies installed
3. Check for platform-specific code
4. Use Docker for consistency

### Debug Mode

Enable verbose output:

```bash
# Verbose benchmark execution
PYTHONUNBUFFERED=1 python simulations/tooling/benchmarks/benchmark_suite.py

# Debug regression detection
python simulations/tooling/benchmarks/regression_detector.py --verbose
```

### Getting Help

1. Check logs in `reports/benchmarks/current/`
2. Review GitHub Actions logs
3. Open issue with benchmark output
4. Include system information (OS, Python version, etc.)

---

## Best Practices

1. **Run Regularly** - Every commit in CI, nightly full runs
2. **Monitor Trends** - Look for gradual degradation
3. **Update Baselines** - When improvements verified
4. **Investigate Regressions** - Don't ignore warnings
5. **Optimize Incrementally** - Small improvements add up
6. **Document Changes** - Comment performance optimizations
7. **Use Appropriate Scale** - Small for CI, large for analysis
8. **Track Correlations** - Relate performance to features

---

## Resources

- [Main README](README.md)
- [CI Integration Guide](CI_INTEGRATION.md)
- [API Documentation](../../docs/ARCHITECTURE.md)
- [Performance Tuning](../../docs/ROADMAP.md)
