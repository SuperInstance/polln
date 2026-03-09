# POLLN Configuration Module

This directory contains configuration files for POLLN components.

## Files

### `optimized.ts`
Auto-generated optimized hyperparameters from the optimization framework.

**DO NOT EDIT MANUALLY** - Regenerate with:
```bash
cd simulations/optimization/hyperparams
python run_all.py
```

### Usage

```typescript
import { OPTIMIZED_CONFIG } from './config/optimized';

// Use in your code
const temperature = OPTIMIZED_CONFIG.plinko.initialTemperature;
const lambda = OPTIMIZED_CONFIG.tdLambda.lambda;
```

## Configuration Structure

```typescript
{
  plinko: {
    initialTemperature: number,    // Starting temperature for exploration
    schedule: string,              // 'constant' | 'linear' | 'exponential' | 'cyclical'
    decayRate: number,             // Temperature decay per step
    minTemperature: number         // Minimum temperature floor
  },
  tdLambda: {
    lambda: number,                // Eligibility trace decay [0, 1]
    alpha: number,                 // Learning rate [0, 1]
    gamma: number                  // Discount factor [0, 1]
  },
  vae: {
    latentDim: number,             // VAE latent space dimension
    beta: number,                  // β-VAE parameter
    capacity: number | null        // KL capacity limit
  },
  evolution: {
    pruningThreshold: number,      // Edge pruning threshold
    graftingRate: number,          // New connection rate
    clusteringResolution: number   // Community detection resolution
  },
  meta: {
    signalResponseRate: number,    // Response speed to signals
    differentiationThreshold: number, // Differentiation trigger
    plasticityRule: string         // 'hebbian' | 'oja' | 'bcm'
  }
}
```

## Regenerating Configuration

To re-run optimization and generate new configuration:

```bash
# Run all optimizations
cd simulations/optimization/hyperparams
python run_all.py

# Or run individual optimizations
python plinko_temperature.py
python td_lambda_optimization.py
python vae_architecture.py
python graph_evolution_params.py
python meta_differentiation.py

# Then generate config
python generate_config.py
```

## Adding New Configuration

To add new configuration parameters:

1. Add optimization to appropriate file in `simulations/optimization/hyperparams/`
2. Update `generate_config.py` to include new parameters
3. Regenerate configuration with `run_all.py`
