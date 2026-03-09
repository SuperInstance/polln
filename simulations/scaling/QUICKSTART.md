# POLLN Scaling Simulations - Quick Start Guide

Get up and running with POLLN scaling simulations in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Navigate to the scaling directory:**
   ```bash
   cd simulations/scaling
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - numpy (numerical computing)
   - matplotlib (plotting)
   - scipy (scientific computing)
   - pandas (data analysis)
   - networkx (graph algorithms)
   - pytest (testing)

## Running Simulations

### Option 1: Run All Simulations (Recommended)

Run the complete simulation suite:

```bash
python run_all.py
```

This will:
- Run all 4 scaling simulations
- Generate all plots
- Create comprehensive reports
- Save results to CSV files

**Time:** ~5-10 minutes
**Outputs:** Check `plots/`, `results/`, and `reports/` directories

### Option 2: Run Individual Simulations

#### Scaling Laws (H1)
```bash
python scaling_laws.py
```
Validates that POLLN scales sublinearly (O(log N)).

#### Communication Bottleneck (H2)
```bash
python communication_bottleneck.py
```
Identifies where communication becomes a bottleneck.

#### Horizontal vs Vertical (H3)
```bash
python horizontal_vs_vertical.py
```
Compares scaling strategies for cost-effectiveness.

#### Topology Optimization (H4)
```bash
python topology_optimization.py
```
Finds the optimal network topology for large colonies.

### Option 3: Run Tests

Validate all simulations with tests:

```bash
pytest test_scaling.py -v
```

## Understanding the Output

### Plots

After running simulations, check the `plots/` directory:

- **scaling_laws.png** - Throughput and latency vs colony size
- **bottleneck_analysis.png** - Communication saturation curves
- **horizontal_vs_vertical.png** - Cost-performance comparison
- **topology_comparison.png** - Network topology rankings

### Results

Check the `results/` directory for CSV files:

- **scaling_metrics.csv** - Raw scaling data
- **bottleneck_metrics.csv** - Communication data
- **scaling_comparison.csv** - Cost comparison data
- **topology_metrics.csv** - Topology metrics

### Reports

Check the `reports/` directory:

- **SCALING_REPORT.md** - Full analysis in markdown
- **comprehensive_report.json** - Machine-readable results
- **executive_summary.png** - Visual dashboard

## Common Use Cases

### Use Case 1: Validate Production Deployment

You want to deploy POLLN to production and need to know optimal colony size.

```bash
python run_all.py
```

Then check `reports/SCALING_REPORT.md` for the recommendation:
- **Optimal colony size: 500-1000 agents**
- **Reasoning:** Balances performance with communication overhead

### Use Case 2: Debug Scaling Issues

Your POLLN deployment is slow at scale. Identify the bottleneck.

```bash
python communication_bottleneck.py
```

Check the output to see if you're above the bottleneck threshold.
- **If N > 1000:** Communication is saturated, use federation
- **If N < 1000:** Check other factors (CPU, memory, etc.)

### Use Case 3: Compare Infrastructure Options

You're deciding between many small servers vs few large servers.

```bash
python horizontal_vs_vertical.py
```

The results show horizontal scaling is 3-5x more cost-effective.

### Use Case 4: Optimize Network Topology

You want to minimize communication overhead in your colony.

```bash
python topology_optimization.py
```

The results recommend small-world topology with k=6, p=0.1.

## Troubleshooting

### Issue: Import errors

**Problem:** `ModuleNotFoundError: No module named 'numpy'`

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Plots not displaying

**Problem:** Plots are generated but not visible.

**Solution:** Plots are saved to `plots/` directory. Open them manually:
```bash
# On Linux/Mac
open plots/scaling_laws.png

# On Windows
start plots/scaling_laws.png
```

### Issue: Simulations are slow

**Problem:** Simulations take too long.

**Solution:** Reduce trials or colony sizes. Edit the script:

```python
# In scaling_laws.py, change:
metrics, analysis = simulator.run_scaling_experiment(
    colony_sizes=[10, 50, 100, 500, 1000],  # Remove 5000, 10000
    n_trials=5  # Reduce from 10 to 5
)
```

### Issue: Out of memory

**Problem:** Large simulations cause memory errors.

**Solution:** Run smaller simulations individually:

```bash
# Instead of run_all.py, run individually:
python scaling_laws.py
python communication_bottleneck.py
# etc.
```

## Next Steps

1. **Review the results** in `reports/SCALING_REPORT.md`
2. **Check the plots** in `plots/` directory
3. **Read the integration guide** in `INTEGRATION.md` to map to TypeScript
4. **Run tests** to validate: `pytest test_scaling.py -v`

## Getting Help

- **Documentation:** See `README.md` for full details
- **Integration:** See `INTEGRATION.md` for TypeScript mapping
- **Issues:** Open a GitHub issue

## Quick Reference

| Command | Purpose | Time |
|---------|---------|------|
| `python run_all.py` | Run all simulations | 5-10 min |
| `python scaling_laws.py` | Test H1: Scaling laws | 2-3 min |
| `python communication_bottleneck.py` | Test H2: Bottleneck | 2-3 min |
| `python horizontal_vs_vertical.py` | Test H3: Scaling strategy | 2-3 min |
| `python topology_optimization.py` | Test H4: Topology | 3-4 min |
| `pytest test_scaling.py` | Run all tests | 1-2 min |

## Key Findings (TL;DR)

1. **H1 ✓:** POLLN scales as O(log N) - sublinear degradation
2. **H2 ✓:** Bottleneck at N ≈ 1000 agents
3. **H3 ✓:** Horizontal scaling is 3-5x more cost-effective
4. **H4 ✓:** Small-world topology is optimal

**Recommendation:** Deploy colonies of 500-1000 agents using horizontal scaling with small-world topology.

Happy simulating! 🚀
