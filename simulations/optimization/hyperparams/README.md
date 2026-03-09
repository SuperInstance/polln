# POLLN Hyperparameter Optimization

This directory contains Bayesian optimization and grid search simulations to find optimal hyperparameters for all POLLN components.

## Overview

The optimization system targets five core POLLN components:

1. **Plinko Temperature Scheduling** - Exploration vs exploitation balance
2. **TD(λ) Learning Parameters** - Value network convergence speed
3. **VAE World Model Architecture** - Dream quality and reconstruction
4. **Graph Evolution Thresholds** - Network efficiency and emergence
5. **META Tile Differentiation** - Specialization quality and stability

## Installation

```bash
# Install required Python packages
pip install numpy scipy scikit-optimize pandas matplotlib tqdm
```

## Quick Start

### Run All Optimizations

```bash
python run_all.py
```

This will:
1. Run all optimization simulations in parallel
2. Generate unified config file
3. Create TypeScript constants file
4. Generate optimization report

### Run Individual Optimizations

```bash
# Optimize Plinko temperature schedules
python plinko_temperature.py

# Optimize TD(λ) parameters
python td_lambda_optimization.py

# Optimize VAE architecture
python vae_architecture.py

# Optimize graph evolution thresholds
python graph_evolution_params.py

# Optimize META tile differentiation
python meta_differentiation.py
```

### Generate TypeScript Config

```bash
# Generate src/core/config/optimized.ts from results
python generate_config.py
```

## Optimization Methods

### Bayesian Optimization
Uses scikit-optimize (skopt) for efficient hyperparameter search with Gaussian Process models.

### Grid Search
Exhaustive search over discrete parameter spaces for small search spaces.

### Statistical Validation
All results are validated using:
- 5-fold cross-validation
- Bootstrap confidence intervals (1000 samples)
- Paired t-tests for significance testing

## Output Files

### Simulation Results
- `results/plinko_temperature_results.json`
- `results/td_lambda_results.json`
- `results/vae_architecture_results.json`
- `results/graph_evolution_results.json`
- `results/meta_differentiation_results.json`

### Generated Config
- `src/core/config/optimized.ts` - TypeScript constants file
- `src/core/config/optimized.json` - Raw JSON config

### Reports
- `results/OPTIMIZATION_REPORT.md` - Comprehensive optimization summary
- `results/parameter_sensitivity_analysis.png` - Sensitivity plots
- `results/convergence_comparison.png` - Convergence speed comparison

## Optimization Metrics

### Plinko Temperature
- **Convergence Speed** - Episodes to reach 90% of optimal performance
- **Final Performance** - Average reward at convergence
- **Exploration Efficiency** - Unique states visited per episode

### TD(λ) Parameters
- **Convergence Speed** - Episodes to reach <1% value change
- **Final MSE** - Mean squared error of value predictions
- **Stability** - Variance of value estimates over last 100 episodes

### VAE Architecture
- **Reconstruction Loss** - MSE of input reconstruction
- **KL Divergence** - Latent space regularity
- **Dream Quality** - Performance of policies trained on dreams
- **Training Speed** - Epochs to convergence

### Graph Evolution
- **Graph Efficiency** - Average path length vs optimal
- **Communication Cost** - Total messages per episode
- **Emergence Quality** - Novel behavior patterns discovered
- **Stability** - Rate of graph topology changes

### META Differentiation
- **Differentiation Speed** - Episodes to specialization
- **Specialization Quality** - Performance on specialized tasks
- **Stability** - Resistance to catastrophic forgetting

## Test Coverage

Run the test suite:

```bash
python test_optimization.py
```

Tests cover:
- Optimization convergence
- Parameter sensitivity
- Statistical validation
- Config generation
- Cross-validation

## Directory Structure

```
simulations/optimization/hyperparams/
├── README.md                          # This file
├── QUICKSTART.md                      # Quick start guide
├── plinko_temperature.py              # Plinko schedule optimization
├── td_lambda_optimization.py          # TD(λ) parameter optimization
├── vae_architecture.py                # VAE architecture optimization
├── graph_evolution_params.py          # Evolution threshold optimization
├── meta_differentiation.py            # META tile parameter optimization
├── run_all.py                         # Master optimization runner
├── generate_config.py                 # TypeScript config generator
├── test_optimization.py               # Test suite
├── RESULTS.md                         # Detailed optimization results
└── results/                           # Output directory
    ├── *.json                         # Individual optimization results
    ├── OPTIMIZATION_REPORT.md         # Comprehensive report
    └── *.png                          # Visualization plots
```

## Performance Expectations

On a standard laptop (4-core CPU):
- **Plinko Temperature**: ~5 minutes
- **TD(λ) Parameters**: ~15 minutes
- **VAE Architecture**: ~20 minutes
- **Graph Evolution**: ~10 minutes
- **META Differentiation**: ~10 minutes
- **Total**: ~1 hour for complete optimization

## Citation

If you use these optimized parameters in your research, please cite:

```bibtex
@misc{polln2024optimization,
  title={Hyperparameter Optimization for Pattern-Organized Large Language Networks},
  author={POLLN Contributors},
  year={2024},
  url={https://github.com/SuperInstance/polln}
}
```

## Contributing

To add new optimization targets:

1. Create a new optimization script following the pattern in existing files
2. Add it to `run_all.py`
3. Update this README with the new optimization target
4. Add tests to `test_optimization.py`

## License

MIT License - See LICENSE file in root directory
