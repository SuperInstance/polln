# POLLN Performance Simulation Quick Start

Get up and running with POLLN performance simulations in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 6 minutes of runtime for full validation

## Installation

```bash
# Navigate to performance simulations
cd simulations/performance

# Install dependencies
pip install -r requirements.txt
```

## Quick Start (5 Minutes)

### Option 1: Run Everything

```bash
# Run all simulations and generate comprehensive report
python run_all.py
```

This will:
1. Run all 4 performance simulations
2. Generate analysis files
3. Create publication-quality plots
4. Produce comprehensive performance report

**Expected runtime:** ~6 minutes
**Output:** `results/PERFORMANCE_REPORT.md`

### Option 2: Run Individual Simulations

```bash
# H1: Load Testing (2 min)
python load_testing.py

# H2: Cold Start Analysis (1 min)
python cold_start_analysis.py

# H3: Degradation Modeling (1 min)
python degradation_modeling.py

# H4: Fault Injection (2 min)
python fault_injection.py
```

## Understanding Results

### Quick Status Check

After running simulations, check the summary:

```bash
# View comprehensive report
cat results/PERFORMANCE_REPORT.md

# Or open in browser
open results/PERFORMANCE_REPORT.md  # macOS
xdg-open results/PERFORMANCE_REPORT.md  # Linux
start results/PERFORMANCE_REPORT.md  # Windows
```

### Key Metrics to Check

Look for these in the report:

1. **Executive Summary**: All hypotheses should show ✓ PASS
2. **Results Summary Table**: All 4 hypotheses validated
3. **Industry Benchmark Comparison**: POLLN vs OpenAI/Anthropic

### Individual Simulation Results

Each simulation generates:

- **CSV file**: Raw data for analysis
- **JSON file**: Detailed analysis results
- **Text report**: Human-readable summary
- **PNG plots**: Publication-quality visualizations

## Validation

### Run Tests

```bash
# Run all performance validation tests
pytest test_performance.py -v
```

Expected output: All tests pass ✓

### Quick Validation

Check if all hypotheses passed:

```bash
# Should see "ALL HYPOTHESES VALIDATED"
grep "ALL HYPOTHESES" results/PERFORMANCE_REPORT.md
```

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Simulation Errors

```bash
# Check Python version (must be 3.9+)
python --version

# Increase timeout for slow machines
# Edit run_all.py and change timeout=600 to timeout=1200
```

### Missing Results

```bash
# Check results directory exists
ls -la results/

# If empty, run simulations again
python run_all.py
```

## Common Workflows

### Fast Validation (Reduced Trials)

Edit simulation files to reduce `num_trials` from 100 to 10:

```python
# In load_testing.py, change:
num_trials=100  # to  num_trials=10
```

This reduces runtime from 6 minutes to ~1 minute (less accurate).

### Single Hypothesis Validation

```bash
# Only validate H1 (load testing)
python load_testing.py
pytest test_performance.py::TestLoadTesting -v
```

### Generate Plots Only

If CSV files exist but plots don't:

```bash
# Regenerate plots (edit script to skip simulation)
# In each simulation file, comment out the simulation section
# and only run the plotting section
```

## Next Steps

After successful validation:

1. **Review Results**: Examine `results/PERFORMANCE_REPORT.md`
2. **Check Plots**: View PNG files in `results/`
3. **Compare Benchmarks**: See how POLLN compares to industry
4. **Integrate**: Map results to POLLN TypeScript codebase
5. **Deploy**: Use simulations to validate production readiness

## Getting Help

- Full documentation: `README.md`
- Benchmark details: `BENCHMARKS.md`
- POLLN architecture: `../../docs/ARCHITECTURE.md`
- GitHub issues: https://github.com/SuperInstance/polln/issues

## Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run simulations: `python run_all.py`
- [ ] Check results: `cat results/PERFORMANCE_REPORT.md`
- [ ] Run tests: `pytest test_performance.py -v`
- [ ] Validate all 4 hypotheses: ✓ PASS
- [ ] Review plots: Open PNG files in `results/`
- [ ] Compare with benchmarks: Check industry comparison
- [ ] Document findings: Update production readiness assessment

---

**Expected Result**: All 4 hypotheses validated, POLLN production ready!

**Time to Complete**: 5-10 minutes

**Questions?** See `README.md` for detailed documentation
