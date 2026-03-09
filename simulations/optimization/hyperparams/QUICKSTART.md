# Quick Start Guide - POLLN Hyperparameter Optimization

## Prerequisites

1. Python 3.8 or higher
2. NumPy, SciPy, scikit-optimize, pandas, matplotlib, tqdm

## Installation

```bash
pip install numpy scipy scikit-optimize pandas matplotlib tqdm
```

## 5-Minute Quick Start

### Step 1: Run All Optimizations

```bash
cd simulations/optimization/hyperparams
python run_all.py
```

This will:
- Run all 5 optimization simulations
- Generate results in `results/` directory
- Create TypeScript config file
- Generate comprehensive report

### Step 2: View Results

```bash
# View optimization report
cat results/OPTIMIZATION_REPORT.md

# View individual results
cat results/plinko_temperature_results.json
cat results/td_lambda_results.json
```

### Step 3: Use Optimized Config

The optimized config is now available in TypeScript:

```typescript
import { OPTIMIZED_CONFIG } from './config/optimized';

// Use in your code
const temperature = OPTIMIZED_CONFIG.plinko.initialTemperature;
const lambda = OPTIMIZED_CONFIG.tdLambda.lambda;
```

## Running Individual Optimizations

If you only want to optimize specific components:

```bash
# Optimize only Plinko temperature
python plinko_temperature.py

# Optimize only TD(λ) parameters
python td_lambda_optimization.py

# Optimize only VAE architecture
python vae_architecture.py

# Optimize only graph evolution
python graph_evolution_params.py

# Optimize only META differentiation
python meta_differentiation.py
```

## Regenerating TypeScript Config

After running optimizations, generate the TypeScript config:

```bash
python generate_config.py
```

This creates `src/core/config/optimized.ts` with all optimal parameters.

## Running Tests

Validate the optimization framework:

```bash
python test_optimization.py
```

## Custom Optimization Ranges

Edit individual optimization files to customize parameter ranges:

```python
# Example: In plinko_temperature.py
TEMPERATURE_RANGES = {
    'initial': (1.0, 5.0),      # Min, max initial temperature
    'decay_rate': (0.990, 0.999),  # Min, max decay rate
    'min_temp': (0.01, 0.5)      # Min, max minimum temperature
}
```

## Understanding Results

Each optimization generates:
1. **Best Parameters**: Optimal hyperparameter values
2. **Convergence Plot**: Optimization over iterations
3. **Sensitivity Analysis**: Parameter importance ranking
4. **Cross-Validation Scores**: 5-fold CV performance

## Troubleshooting

### Issue: Slow Optimization

**Solution**: Reduce `N_CALLS` in optimization files

```python
# In any optimization file
N_CALLS = 50  # Default is 100, reduce to 50 for faster runs
```

### Issue: Memory Error

**Solution**: Reduce `N_SPLITS` for cross-validation

```python
# In any optimization file
N_SPLITS = 3  # Default is 5, reduce to 3 for less memory
```

### Issue: Poor Results

**Solution**: Check parameter ranges are reasonable

```python
# Ensure ranges are not too narrow or too wide
TEMPERATURE_RANGES = {
    'initial': (1.0, 5.0),  # Good range
    'initial': (2.0, 2.1),  # Too narrow
    'initial': (0.0, 1000.0)  # Too wide
}
```

## Next Steps

1. Review `RESULTS.md` for detailed optimization results
2. Check `results/OPTIMIZATION_REPORT.md` for comprehensive analysis
3. Integrate optimized parameters into your POLLN implementation
4. Re-run optimizations periodically as your system evolves

## Support

For issues or questions:
1. Check the main README.md
2. Review optimization script comments
3. Run test suite to validate installation
