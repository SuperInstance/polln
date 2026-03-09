# LoRA Composition Validation - Quick Start Guide

## 5-Minute Quick Start

### 1. Install Dependencies
```bash
cd simulations/lora
pip install -r requirements.txt
```

### 2. Run Quick Test
```bash
python run_all.py --quick
```
*Takes ~5-10 minutes with smaller dimensions*

### 3. View Results
```bash
# Check summary
cat results/quick/summary_report.json

# View visualizations
ls results/quick/*.png
```

## Common Commands

### Run Specific Modules
```bash
# Rank analysis only
python run_all.py --modules rank

# Interference + Composition
python run_all.py --modules interference composition

# All modules
python run_all.py
```

### Using Makefile
```bash
make test      # Quick single-module test
make quick     # All modules, fast
make full      # Comprehensive analysis
make clean     # Remove results
```

## Programmatic Usage

### Rank Analysis
```python
from rank_analysis import RankSufficiencyAnalyzer

analyzer = RankSufficiencyAnalyzer(base_dim=1024, max_rank=256)
results = analyzer.run_full_analysis()
r_min = analyzer.find_sufficient_rank("code", threshold=0.95)
```

### Interference Detection
```python
from interference import InterferenceDetector

detector = InterferenceDetector(base_dim=1024)
detector.generate_lora_pairs()
metrics = detector.compute_all_metrics()
```

### Composition Optimization
```python
from composition import CompositionOptimizer

optimizer = CompositionOptimizer(base_dim=1024)
results = optimizer.compare_strategies()
```

### Scaling Laws
```python
from scaling_laws import ScalingLawAnalyzer

analyzer = ScalingLawAnalyzer()
analyzer.fit_scaling_law(data)
config = analyzer.find_optimal_configuration(target_accuracy=0.8)
```

## Key Files

| File | Purpose |
|------|---------|
| `run_all.py` | Main execution script |
| `example_usage.py` | Usage examples |
| `test_simulations.py` | Test suite |
| `README.md` | Full documentation |
| `MATHEMATICAL_FOUNDATIONS.md` | Theory and proofs |

## Understanding Results

### Rank Analysis
- **r_95**: Minimum rank for 95% variance
- **reconstruction_error**: Lower is better
- **compression_ratio**: How much smaller than full model

### Interference
- **subspace_overlap < 0.3**: Compatible
- **subspace_overlap > 0.6**: Incompatible
- **weight_correlation**: -1 to 1 (opposite to identical)

### Composition
- **inverse_sqrt**: Usually best (1/√N weighting)
- **learned**: Most flexible, needs validation data
- **linearity_error < 0.01**: Highly linear

### Scaling Laws
- **accuracy = a + b·log(params) + c·n_loras - d·interference**
- **b**: Returns to scale (usually ~0.05-0.10)
- **c**: LoRA benefit (usually ~0.02-0.05)
- **d**: Interference penalty (usually ~0.01-0.03)

## Troubleshooting

### Out of Memory
```bash
# Use smaller dimensions
python run_all.py --quick --base-dim 256
```

### Slow Execution
```bash
# Use quick mode
python run_all.py --quick

# Or run fewer scenarios
# Edit run_all.py: n_scenarios=10
```

### Import Errors
```bash
# Ensure all dependencies installed
pip install --upgrade -r requirements.txt

# Check Python version (needs 3.8+)
python --version
```

## Expected Outputs

After running, you'll have:

```
results/
├── rank_analysis_results.json
├── interference_results.json
├── composition_results.json
├── scaling_law_results.json
├── summary_report.json
├── phase_diagram.png
├── interference_matrix.png
├── strategy_comparison.png
├── linearity_analysis.png
├── break_even_curves.png
├── accuracy_surface.png
├── diminishing_returns.png
└── simulation_log_*.txt
```

## Key Findings to Look For

### ✓ Hypothesis H1 Validated?
Check: `summary_report.json > key_findings > rank_sufficiency > hypothesis_h1_validated`
- Should be `true` for most domains

### ✓ Best Composition Strategy?
Check: `summary_report.json > key_findings > composition > best_strategy`
- Usually `inverse_sqrt` or `learned`

### ✓ 1/√N Works?
Check: `summary_report.json > key_findings > composition > linearity_error`
- Should be < 0.05 for linearity

### ✓ LoRA More Efficient?
Check: `summary_report.json > key_findings > scaling > optimal_configurations`
- Compare params vs single model

## Next Steps

1. **Validate Results**
   - Check `summary_report.json`
   - Review visualizations
   - Run `python test_simulations.py`

2. **Customize**
   - Add your own domains
   - Adjust ranks and parameters
   - Test with real model weights

3. **Integrate**
   - Import modules into your code
   - Use predictions for LoRA selection
   - Optimize your LoRA library

## Getting Help

- **Full docs**: `README.md`
- **Theory**: `MATHEMATICAL_FOUNDATIONS.md`
- **Architecture**: `ARCHITECTURE.md`
- **Examples**: `example_usage.py`

## Performance Tips

- **Quick testing**: Use `--quick` flag
- **Production**: Run without flags (full mode)
- **Parallel**: Run different modules on different machines
- **Caching**: Results are saved, can resume

## Success Criteria

The simulation is successful if:

1. ✓ **H1 (Rank)**: r ≈ 64 sufficient for 95% variance
2. ✓ **H2 (Linearity)**: Can predict compatible pairs
3. ✓ **H3 (Efficiency)**: LoRA library more efficient than single model
4. ✓ **Composition**: 1/√N or better weighting validated
5. ✓ **Scaling**: Law coefficients statistically significant

---

**Ready to validate POLLN's LoRA Library mathematically!**

Run: `python run_all.py --quick`
