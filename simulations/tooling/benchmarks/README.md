# POLLN Benchmark System

Comprehensive automated benchmarking system for tracking POLLN performance over time with regression detection and trend analysis.

## Overview

The POLLN Benchmark System provides:

- **Automated Benchmark Suite** - Measure latency, throughput, memory, and accuracy
- **Regression Detection** - Statistical analysis to catch performance degradations
- **Trend Tracking** - Monitor performance over commits and branches
- **CI/CD Integration** - Automated checks in GitHub Actions
- **Comprehensive Reporting** - HTML, JSON, and Markdown reports

## Directory Structure

```
simulations/tooling/benchmarks/
├── benchmark_suite.py         # Core benchmark suite
├── regression_detector.py     # Performance regression detection
├── trend_tracker.py          # Performance trend tracking
├── benchmark_runner.py       # Automated benchmark execution
├── report_generator.py       # Report generation
├── baseline_manager.py       # Baseline management
├── benchmark_ci.py           # CI/CD integration
├── test_benchmarks.py        # Test suite
└── README.md                 # This file

reports/benchmarks/
├── current/                  # Latest benchmark results
├── trends/                   # Historical trend charts
├── comparisons/              # Performance comparisons
├── baselines/                # Baseline benchmarks
└── history/                  # Historical benchmark data
```

## Quick Start

### Installation

```bash
# Install Python dependencies
pip install numpy scipy matplotlib psutil

# Install POLLN
npm install
npm run build
```

### Running Benchmarks

```bash
# Run all benchmarks (small scale)
python simulations/tooling/benchmarks/benchmark_suite.py

# Run specific scale
python simulations/tooling/benchmarks/benchmark_suite.py --scale medium

# Run specific category
python simulations/tooling/benchmarks/benchmark_suite.py --category agents
```

### Checking Regressions

```bash
# Compare against baseline
python simulations/tooling/benchmarks/regression_detector.py

# Specify baseline file
python simulations/tooling/benchmarks/regression_detector.py --baseline baseline.json

# Adjust confidence level
python simulations/tooling/benchmarks/regression_detector.py --confidence 0.99
```

### Managing Baselines

```bash
# Create new baseline
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name main --results benchmarks_20250101_120000.json

# List all baselines
python simulations/tooling/benchmarks/baseline_manager.py list

# Set active baseline
python simulations/tooling/benchmarks/baseline_manager.py set-active --name main

# Update baseline with improvements
python simulations/tooling/benchmarks/baseline_manager.py update \
    --results benchmarks_20250102_120000.json
```

## Benchmark Categories

### Agent Benchmarks

- **Agent Creation** - Time to create new agents
- **Agent Activation** - Time to activate agents
- **Decision Making** - Plinko layer selection performance

### Colony Benchmarks

- **Colony Coordination** - Multi-agent coordination overhead
- **Colony Communication** - A2A message throughput

### Learning Benchmarks

- **Hebbian Learning** - Synaptic weight update performance
- **Dreaming Cycle** - VAE-based policy optimization

### KV-Cache Benchmarks

- **KV Anchor Creation** - Compression performance
- **ANN Matching** - Approximate nearest neighbor search

## Benchmark Scales

| Scale | Colony Size | Message Count | Synapse Count | Index Size |
|-------|-------------|---------------|---------------|------------|
| Small | 50          | 25            | 500           | 5,000      |
| Medium | 100         | 50            | 1,000         | 10,000     |
| Large | 500         | 200           | 5,000         | 50,000     |

## CI/CD Integration

The benchmark system integrates with GitHub Actions:

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

### CI Features

- **Automated Execution** - Runs on every push and PR
- **Regression Detection** - Fails CI on critical regressions
- **PR Comments** - Posts results as PR comments
- **Artifact Upload** - Stores benchmark results
- **Trend Analysis** - Tracks performance over time

## Reports

### HTML Reports

```bash
python simulations/tooling/benchmarks/report_generator.py
```

Generates `benchmark_report.html` with:
- Executive summary
- Performance metrics table
- Regression details
- Recommendations
- Overall score (0-100)

### JSON Reports

```bash
python simulations/tooling/benchmarks/report_generator.py --format json
```

### Markdown Reports

```bash
python simulations/tooling/benchmarks/report_generator.py --format markdown
```

## Trend Analysis

```bash
# Analyze trends over time
python simulations/tooling/benchmarks/trend_tracker.py

# Generate visualizations
python simulations/tooling/benchmarks/trend_tracker.py --visualize

# Analyze specific metrics
python simulations/tooling/benchmarks/trend_tracker.py --metrics agent_creation_avg_latency

# Analyze specific branch
python simulations/tooling/benchmarks/trend_tracker.py --branch develop
```

## Configuration

### Regression Thresholds

Adjust severity thresholds in `regression_detector.py`:

```python
self.thresholds = {
    RegressionSeverity.CRITICAL: 0.50,   # 50% worse
    RegressionSeverity.HIGH: 0.20,       # 20% worse
    RegressionSeverity.MEDIUM: 0.10,     # 10% worse
    RegressionSeverity.LOW: 0.05         # 5% worse
}
```

### Benchmark Configuration

Customize in `benchmark_suite.py`:

```python
config = BenchmarkConfig(
    name="custom_benchmark",
    warmup_iterations=10,
    benchmark_iterations=100,
    timeout_seconds=300,
    memory_threshold_mb=1024,
    cpu_threshold_percent=90
)
```

## Testing

```bash
# Run all tests
python simulations/tooling/benchmarks/test_benchmarks.py

# Run specific test class
python -m unittest test_benchmarks.TestBenchmarkSuite

# Run with coverage
python -m pytest test_benchmarks.py --cov=. --cov-report=html
```

## Troubleshooting

### Benchmarks fail to run

1. Check Python dependencies are installed
2. Ensure POLLN is built (`npm run build`)
3. Verify output directories exist

### Regression detector finds no baseline

1. Create a baseline with `baseline_manager.py create`
2. Ensure baseline file is in `reports/benchmarks/baselines/`
3. Set active baseline with `baseline_manager.py set-active`

### CI fails on benchmarks

1. Check benchmark logs in GitHub Actions
2. Verify dependencies are installed in CI
3. Check if regressions are actual or noise

## Best Practices

1. **Run Regularly** - Execute benchmarks on every commit
2. **Update Baselines** - When genuine improvements are verified
3. **Monitor Trends** - Look for gradual degradation over time
4. **Investigate Regressions** - Don't ignore performance warnings
5. **Use Appropriate Scale** - Small for CI, large for nightly runs

## Contributing

When adding new benchmarks:

1. Add benchmark method to `benchmark_suite.py`
2. Follow naming convention: `benchmark_<category>_<operation>`
3. Return `BenchmarkResult` with all metrics
4. Add test in `test_benchmarks.py`
5. Update documentation

## License

MIT License - See LICENSE file for details
