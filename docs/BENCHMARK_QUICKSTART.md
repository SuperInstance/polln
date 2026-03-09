# POLLN Benchmark System - Quick Reference

## Essential Commands

### Running Benchmarks

```bash
# Run all benchmarks (small scale - fast)
python simulations/tooling/benchmarks/benchmark_suite.py

# Run with specific scale
python simulations/tooling/benchmarks/benchmark_suite.py --scale medium

# Run specific category
python simulations/tooling/benchmarks/benchmark_suite.py --category agents

# Run in parallel
python simulations/tooling/benchmarks/benchmark_runner.py --parallel
```

### Checking Regressions

```bash
# Check against baseline
python simulations/tooling/benchmarks/regression_detector.py

# With specific baseline
python simulations/tooling/benchmarks/regression_detector.py --baseline baseline.json

# Adjust confidence level
python simulations/tooling/benchmarks/regression_detector.py --confidence 0.99
```

### Managing Baselines

```bash
# Create baseline
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name main --results benchmarks_*.json

# List baselines
python simulations/tooling/benchmarks/baseline_manager.py list

# Set active baseline
python simulations/tooling/benchmarks/baseline_manager.py set-active --name main

# Update baseline
python simulations/tooling/benchmarks/baseline_manager.py update \
    --results benchmarks_*.json --name main
```

### Generating Reports

```bash
# Generate all formats
python simulations/tooling/benchmarks/report_generator.py

# Specific format
python simulations/tooling/benchmarks/report_generator.py --format html
python simulations/tooling/benchmarks/report_generator.py --format json
python simulations/tooling/benchmarks/report_generator.py --format markdown
```

### Trend Analysis

```bash
# Analyze trends
python simulations/tooling/benchmarks/trend_tracker.py

# Generate visualizations
python simulations/tooling/benchmarks/trend_tracker.py --visualize

# Specific metrics
python simulations/tooling/benchmarks/trend_tracker.py \
    --metrics agent_creation_avg_latency colony_coordination_throughput
```

### CI/CD Integration

```bash
# Run in CI mode
python simulations/tooling/benchmarks/benchmark_ci.py \
    --scale small --fail-on-regression
```

## File Structure

```
reports/benchmarks/
├── current/                  # Latest benchmark results
│   ├── benchmarks_*.json    # Raw benchmark data
│   ├── regression_report.json
│   └── benchmark_report.html
├── trends/                   # Trend visualizations
│   └── *_trend.png
├── comparisons/              # Performance comparisons
│   └── vs_baseline.json
├── baselines/                # Baseline benchmarks
│   └── *_*.json
├── history/                  # Historical data
│   └── <commit_hash>/
└── cache/                    # Result cache
    └── *.json
```

## Benchmark Scales

| Scale | Colony | Messages | Synapses | Index | Time |
|-------|--------|----------|----------|-------|------|
| Small | 50 | 25 | 500 | 5K | ~30s |
| Medium | 100 | 50 | 1K | 10K | ~2m |
| Large | 500 | 200 | 5K | 50K | ~10m |

## Regression Thresholds

| Severity | Threshold | Action |
|----------|-----------|--------|
| CRITICAL | >50% | Must fix |
| HIGH | 20-50% | Should fix |
| MEDIUM | 10-20% | Monitor |
| LOW | 5-10% | Note |

## Key Metrics

| Metric | Good | Bad |
|--------|------|-----|
| throughput_ops | High | Low |
| p50_latency_ms | Low | High |
| p95_latency_ms | Low | High |
| p99_latency_ms | Low | High |
| memory_mb | Low | High |

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No baseline found | Run `baseline_manager.py create` |
| False regression | Increase iterations, run multiple times |
| CI fails locally | Check Python version, dependencies |
| Slow execution | Use small scale, parallel execution |

## Common Workflows

### First-Time Setup

```bash
# 1. Install dependencies
pip install numpy scipy matplotlib psutil

# 2. Build POLLN
npm install
npm run build

# 3. Run initial benchmarks
python simulations/tooling/benchmarks/benchmark_suite.py --scale small

# 4. Create baseline
python simulations/tooling/benchmarks/baseline_manager.py create \
    --name initial --results reports/benchmarks/current/benchmarks_*.json
```

### Daily Development

```bash
# 1. Make changes
# 2. Run benchmarks
python simulations/tooling/benchmarks/benchmark_suite.py

# 3. Check for regressions
python simulations/tooling/benchmarks/regression_detector.py

# 4. Generate report
python simulations/tooling/benchmarks/report_generator.py
```

### Before Release

```bash
# 1. Run full-scale benchmarks
python simulations/tooling/benchmarks/benchmark_runner.py --scale medium

# 2. Analyze trends
python simulations/tooling/benchmarks/trend_tracker.py --visualize

# 3. Update baseline if improved
python simulations/tooling/benchmarks/baseline_manager.py update \
    --results reports/benchmarks/current/benchmarks_*.json
```

## CI/CD Quick Setup

```yaml
# .github/workflows/benchmarks.yml
name: Benchmarks
on: [push, pull_request]
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: |
          pip install numpy scipy matplotlib psutil
          npm install && npm run build
      - name: Run benchmarks
        run: |
          python simulations/tooling/benchmarks/benchmark_ci.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCALE` | Benchmark scale | small |
| `CONFIDENCE` | Regression confidence | 0.95 |
| `FAIL_ON_REGRESSION` | Fail CI on regression | true |
| `PYTHONUNBUFFERED` | Unbuffered output | - |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, no critical regressions |
| 1 | Critical regressions detected |
| 2 | Error executing benchmarks |

## Further Reading

- [Full README](simulations/tooling/benchmarks/README.md)
- [Benchmark Guide](simulations/tooling/benchmarks/BENCHMARK_GUIDE.md)
- [CI Integration](simulations/tooling/benchmarks/CI_INTEGRATION.md)
