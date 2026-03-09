# POLLN Schedule Optimization

## Overview

This simulation framework discovers optimal learning schedules for all POLLN learning mechanisms through systematic empirical testing across multiple schedule strategies.

## Goal

Find optimal schedules for:
- **Learning Rate Annealing**: TD(λ), VAE, Hebbian, Oja's rule
- **Exploration-Exploitation**: Temperature/epsilon schedules for Plinko
- **Dream-to-Real Ratio**: Dream optimization scheduling
- **Plasticity Modulation**: META tile differentiation timing
- **Federated Synchronization**: Multi-colony sync cadence

## Directory Structure

```
simulations/optimization/schedules/
├── lr_schedule_search.py          # Learning rate optimization
├── exploration_schedule.py        # Exploration optimization
├── dream_ratio_optimization.py    # Dream ratio optimization
├── plasticity_schedule.py         # Plasticity optimization
├── federated_sync_schedule.py     # Federated sync optimization
├── schedule_generator.py          # TypeScript generator
├── run_all.py                     # Master optimizer
├── test_schedules.py              # Unit tests
├── results/                       # Optimization results (auto-generated)
│   ├── lr_schedule_comparison.png
│   ├── exploration_schedule_comparison.png
│   ├── dream_ratio_comparison.png
│   ├── plasticity_schedule_comparison.png
│   ├── federated_sync_comparison.png
│   └── *.json                     # Optimal schedule parameters
└── README.md                      # This file
```

## Installation

### Requirements

```bash
pip install numpy matplotlib seaborn
```

### Optional

For generating TypeScript schedules:
```bash
# TypeScript schedules will be generated to src/core/schedules/
```

## Usage

### Quick Start: Run All Optimizations

```bash
# Run all schedule optimizations (30-60 minutes)
python run_all.py

# Skip optimization, use existing results
python run_all.py --skip-optimization

# Skip TypeScript generation
python run_all.py --skip-generation
```

### Individual Optimizations

#### 1. Learning Rate Optimization

```bash
python lr_schedule_search.py
```

**Tests**: 8 schedules across 4 algorithms (TD(λ), VAE, Hebbian, Oja)

**Schedules**:
- Constant
- Step Decay
- Exponential Decay
- Cosine Annealing
- Warmup + Cosine
- Cyclical (SGDR)
- One-Cycle Policy
- Adaptive

**Output**:
- `results/td_lambda_schedule_comparison.png`
- `results/vae_schedule_comparison.png`
- `results/hebbian_schedule_comparison.png`
- `results/oja_schedule_comparison.png`
- `results/schedule_optimization_summary.json`

#### 2. Exploration Schedule Optimization

```bash
python exploration_schedule.py
```

**Tests**: 10 strategies on multi-armed bandit

**Strategies**:
- Epsilon-greedy (8 variants)
- Boltzmann/Softmax (7 variants)
- UCB
- Thompson Sampling

**Output**:
- `results/exploration_schedule_comparison.png`
- `results/exploration_learning_curves.png`
- `results/exploration_optimal_schedule.json`

#### 3. Dream Ratio Optimization

```bash
python dream_ratio_optimization.py
```

**Tests**: 12 dream scheduling strategies

**Strategies**:
- Constant ratios (0.3, 0.5, 0.7)
- Increasing/Decreasing
- High-early-low-late
- Low-early-high-late
- Adaptive (performance & prediction error)
- Cyclical, One-cycle, Curriculum

**Output**:
- `results/dream_ratio_comparison.png`
- `results/dream_ratio_schedules.png`
- `results/dream_ratio_optimal.json`

#### 4. Plasticity Schedule Optimization

```bash
python plasticity_schedule.py
```

**Tests**: 12 plasticity modulation strategies

**Strategies**:
- Constant (3 levels)
- Linear & Exponential decay
- Step decay (developmental stages)
- Adaptive (performance & environment)
- U-shaped & Inverse U-shaped
- Cyclical & Homeostatic

**Output**:
- `results/plasticity_schedule_comparison.png`
- `results/plasticity_schedule_curves.png`
- `results/plasticity_optimal_schedule.json`

#### 5. Federated Sync Schedule Optimization

```bash
python federated_sync_schedule.py
```

**Tests**: 12 federated synchronization strategies

**Strategies**:
- Fixed frequency (3 intervals)
- Exponential backoff
- Adaptive (divergence & performance gap)
- Event-driven, Hierarchical, Gossip-style
- Elastic, Learning rate dependent, Hybrid

**Output**:
- `results/federated_sync_comparison.png`
- `results/federated_sync_patterns.png`
- `results/federated_sync_optimal.json`

### Generate TypeScript Schedules

After optimization completes, generate production-ready TypeScript classes:

```bash
python schedule_generator.py
```

**Output**:
- `src/core/schedules/learning-rate.ts`
- `src/core/schedules/temperature.ts`
- `src/core/schedules/dream-ratio.ts`
- `src/core/schedules/plasticity.ts`
- `src/core/schedules/federated-sync.ts`
- `src/core/schedules/index.ts`

## Testing

Run unit tests to validate schedule generation and simulations:

```bash
python test_schedules.py
```

**Test Coverage**:
- Schedule generation correctness
- Boundary conditions
- Simulation convergence
- Edge cases

## Results Interpretation

### Key Metrics

Each optimization produces the following metrics:

1. **Final Performance/Loss**: How well the algorithm performs at the end
2. **Convergence Speed**: How quickly the algorithm reaches peak performance
3. **Stability**: Variance in final performance
4. **Combined Score**: Weighted combination of all metrics

### Visualization

Each optimization generates:

1. **Comparison Charts**: Bar charts comparing all schedules
2. **Learning Curves**: Performance over training time
3. **Schedule Plots**: Visualization of schedule shapes

### Example Results

After running `run_all.py`, check `results/optimization_summary.json`:

```json
{
  "learning_rates": {
    "td_lambda": "warmup_cosine",
    "vae": "cosine_annealing",
    "hebbian": "exponential_decay",
    "oja": "constant"
  },
  "exploration": {
    "optimal_strategy": "boltzmann",
    "optimal_schedule": "temperature_exponential",
    "final_reward": 0.8234
  },
  "dream_ratio": {
    "optimal_schedule": "high_early_low_late",
    "final_performance": 0.7891
  },
  "plasticity": {
    "optimal_schedule": "exponential_decay",
    "final_accuracy": 0.8543
  },
  "federated_sync": {
    "optimal_schedule": "adaptive_divergence",
    "final_performance": 0.7654
  }
}
```

## Integration with POLLN

### 1. Install Dependencies

The generated TypeScript schedules are automatically integrated into POLLN:

```typescript
import { ScheduleManager } from './schedules';

// Create schedule manager
const schedules = new ScheduleManager();

// Use in learning algorithms
const lr = schedules.getLearningRate('td_lambda');
const temp = schedules.getTemperature();
const dreamRatio = schedules.getDreamRatio();
```

### 2. Core Integration Points

- **`src/core/valuenetwork.ts`**: Uses `TDLambdaSchedule`
- **`src/core/worldmodel.ts`**: Uses `VAESchedule`
- **`src/core/learning.ts`**: Uses `HebbianSchedule`, `OjaSchedule`
- **`src/core/decision.ts`**: Uses `TemperatureSchedule` for Plinko
- **`src/core/dreaming.ts`**: Uses `DreamRatioSchedule`
- **`src/core/meta.ts`**: Uses `PlasticitySchedule`
- **`src/core/federated.ts`**: Uses `FederatedSyncSchedule`

### 3. Custom Schedules

To create custom schedules, extend the base classes:

```typescript
import { LearningRateSchedule } from './schedules';

export class CustomSchedule extends LearningRateSchedule {
  constructor() {
    super();
    this.schedule = this.generateSchedule(1000);
  }

  private generateSchedule(totalSteps: number): number[] {
    // Your custom schedule logic
    return [];
  }
}
```

## Configuration

### Simulation Parameters

Each optimization script has configurable parameters:

```python
# In lr_schedule_search.py
optimizer = ScheduleOptimizer()

results = optimizer.optimize_for_algorithm(
    algorithm="td_lambda",
    num_steps=1000,      # Training steps
    num_runs=5           # Statistical runs
)
```

### Schedule Parameters

Adjust schedule ranges in each optimizer:

```python
# Example: Learning rate schedules
schedule_configs = [
    ("constant", {"lr": 0.01}),
    ("exponential_decay", {
        "initial_lr": 0.01,
        "gamma": 0.995
    }),
    # ... more configs
]
```

## Performance

### Runtime Estimates

| Optimization | Duration | Runs | Configurations |
|-------------|----------|------|---------------|
| Learning Rates | 10-15 min | 5 per schedule | 8 × 4 = 32 |
| Exploration | 8-10 min | 10 per schedule | 20 |
| Dream Ratio | 5-8 min | 5 per schedule | 12 |
| Plasticity | 5-8 min | 5 per schedule | 12 |
| Federated Sync | 3-5 min | 3 per schedule | 12 |
| **Total** | **30-60 min** | - | **88** |

### Hardware Requirements

- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4+ CPU cores, 8GB+ RAM
- **Parallelization**: Each optimization can be parallelized independently

## Troubleshooting

### Issues

1. **Slow execution**: Reduce `num_runs` or `num_steps`
2. **Memory errors**: Reduce simulation size or batch processing
3. **NaN losses**: Lower learning rates or improve numerical stability
4. **No convergence**: Check simulation parameters, increase training steps

### Debugging

Enable verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Research Background

### Learning Rate Schedules

- **Smith (2018)**: "Super-Convergence: Very Fast Training..."
- **Loshchilov & Hutter (2017)**: "SGDR: Stochastic Gradient Descent with Warm Restarts"
- **Losler (2019)**: "A disciplined approach to neural network hyper-parameters"

### Exploration Schedules

- **Sutton & Barto (2018)**: "Reinforcement Learning: An Introduction"
- **Kaufmann et al. (2012)**: "Bayesian Optimization for..."

### Dream Optimization

- **Ha & Schmidhuber (2018)**: "World Models"
- **Finn et al. (2017)**: "Model-Agnostic Meta-Learning"

### Plasticity

- **Yang et al. (2020)**: "L2L: Learning to Learn"
- **Kirkpatrick et al. (2017)**: "Overcoming catastrophic forgetting..."

## Citation

If you use these optimal schedules in research:

```bibtex
@software{polln_schedules,
  title={POLLN Learning Schedule Optimization},
  author={POLLN Contributors},
  year={2025},
  url={https://github.com/SuperInstance/polln}
}
```

## License

MIT License - see LICENSE file in root directory.

## Contributing

To add new schedule types:

1. Create new optimizer in `schedule_name.py`
2. Follow existing pattern (Results dataclass, Schedule class, Optimizer class)
3. Add tests in `test_schedules.py`
4. Update `run_all.py` to include new optimizer
5. Add generator method in `schedule_generator.py`

## Contact

For questions or issues:
- GitHub: https://github.com/SuperInstance/polln
- Documentation: See `/docs` directory
