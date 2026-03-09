# Multiobjective Pareto Optimization for POLLN

This module provides comprehensive Pareto optimization for finding optimal POLLN configurations across competing objectives.

## Overview

The multiobjective optimization system discovers Pareto-optimal configurations that balance competing tradeoffs:

- **Accuracy vs Cost** - Quality vs resource expenditure
- **Speed vs Quality** - Latency vs response quality
- **Robustness vs Efficiency** - Availability vs cost overhead
- **Scalability vs Complexity** - Throughput vs management complexity

## Architecture

```
multiobjective/
├── pareto_accuracy_cost.py         # Accuracy vs Cost optimization
├── pareto_speed_quality.py         # Speed vs Quality optimization
├── pareto_robustness_efficiency.py # Robustness vs Efficiency
├── pareto_scalability_complexity.py # Scalability vs Complexity
├── recommendation_engine.py        # Scenario-based recommendations
├── run_all.py                      # Master orchestrator
├── generate_configs.py             # Tiered config generation
├── test_multiobjective.py          # Test suite
└── README.md                       # This file
```

## Installation

```bash
cd simulations/advanced/multiobjective
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- numpy
- matplotlib
- (Optional) jupyter for interactive exploration

## Quick Start

### Run All Optimizations

```bash
python run_all.py
```

This will:
1. Run all 4 Pareto optimizations (5-10 minutes)
2. Generate tiered configurations
3. Create visualization plots
4. Generate unified TypeScript config
5. Create recommendation report

### Run Individual Optimizations

```bash
# Accuracy vs Cost
python pareto_accuracy_cost.py

# Speed vs Quality
python pareto_speed_quality.py

# Robustness vs Efficiency
python pareto_robustness_efficiency.py

# Scalability vs Complexity
python pareto_scalability_complexity.py
```

### Interactive Recommendations

```bash
python recommendation_engine.py
```

Select a scenario or enter custom priorities to get recommended configurations.

### Generate Configuration Files

```bash
python generate_configs.py
```

## Pareto Optimization Algorithm

All optimizers use **NSGA-II** (Non-dominated Sorting Genetic Algorithm II):

1. **Population Initialization** - Random configurations
2. **Fast Non-dominated Sort** - Group into Pareto fronts
3. **Crowding Distance** - Preserve diversity
4. **Selection** - Tournament selection from best front
5. **Crossover & Mutation** - Generate offspring
6. **Elitism** - Keep best solutions
7. **Repeat** - For specified generations

### Key Parameters

```python
optimizer = NSGA2Optimizer(
    population_size=100,  # Number of configurations
    generations=50        # Evolution iterations
)
```

## Configuration Tiers

Each optimization generates tiered configurations:

### Accuracy vs Cost

| Tier | Description | Use Case |
|------|-------------|----------|
| BUDGET | Maximum cost efficiency | Development, testing |
| STANDARD | Balanced performance | General production |
| PERFORMANCE | High quality | Critical applications |
| PREMIUM | Near-maximum quality | Premium services |
| MAXIMUM | Best possible accuracy | Research, experimentation |

### Speed vs Quality

| Tier | Latency | Use Case |
|------|---------|----------|
| REALTIME | <100ms | Real-time systems, gaming |
| INTERACTIVE | 100-500ms | Chat, assistants |
| FAST | 500-1000ms | Web applications |
| STANDARD | 1-2s | General applications |
| BATCH | >2s | Batch processing, analytics |

### Robustness vs Efficiency

| Tier | Availability | Use Case |
|------|--------------|----------|
| BASIC | 99% | Development, internal tools |
| HIGH | 99.9% | Standard production |
| CRITICAL | 99.99% | Mission-critical systems |
| EXTREME | 99.999% | Life-critical, financial |

### Scalability vs Complexity

| Tier | Colony Size | Use Case |
|------|-------------|----------|
| SMALL | 10-100 agents | Edge, embedded |
| MEDIUM | 100-500 agents | Standard production |
| LARGE | 500-1000 agents | High-scale services |
| XLARGE | 1000+ agents | Distributed systems |

## Recommendation Engine

The recommendation engine suggests optimal configurations based on:

### Predefined Scenarios

```python
from recommendation_engine import Scenario, engine

# Production deployment
scenario = Scenario.production()
config_name, config, score = engine.recommend_by_scenario(scenario)

# Edge deployment
scenario = Scenario.edge()
config_name, config, score = engine.recommend_by_scenario(scenario)

# Research experimentation
scenario = Scenario.research()
config_name, config, score = engine.recommend_by_scenario(scenario)
```

### Custom Priorities

```python
from recommendation_engine import UserPriorities, RecommendationEngine

priorities = UserPriorities(
    accuracy=0.4,
    cost=0.2,
    latency=0.3,
    availability=0.1,
    scalability=0.0,
    complexity=0.0
).normalize()

engine = RecommendationEngine()
config_name, config, score = engine.recommend_by_priorities(priorities)
```

### Multi-objective Search

```python
# Get top 5 configurations
top_5 = engine.recommend_multi_objective(
    priorities=priorities,
    constraints={
        'min_availability': 0.99,
        'max_latency_ms': 1000,
        'max_cost_multiplier': 2.0
    },
    top_k=5
)
```

## Output Files

### Generated Files

```
outputs/
├── pareto_accuracy_cost.png              # Accuracy/Cost frontier plot
├── pareto_speed_quality.png              # Speed/Quality frontier plot
├── pareto_robustness_efficiency.png      # Robustness/Efficiency plot
├── pareto_scalability_complexity.png     # Scalability/Complexity plot
├── pareto_optimization_report.md         # Comprehensive report
└── recommendation_report.md              # Scenario recommendations

src/core/config/tiers/
├── accuracy_cost_tiers.json             # Accuracy/Cost tiers
├── speed_quality_tiers.json             # Speed/Quality tiers
├── robustness_efficiency_tiers.json     # Robustness tiers
├── scalability_complexity_tiers.json    # Scalability tiers
├── index.json                           # Master index
├── scenarios.json                       # Scenario configs
├── types.ts                             # TypeScript definitions
└── QUICK_REFERENCE.md                   # Quick reference guide
```

## Using Generated Configurations

### In TypeScript

```typescript
import { CONFIG_TIERS } from '@polln/core/config/tiers';

// Use budget tier
const budgetConfig = CONFIG_TIERS.ACCURACY_COST_BUDGET;

// Use production scenario
import scenarioConfigs from '@polln/core/config/tiers/scenarios.json';
const productionConfig = scenarioConfigs['production'];
```

### In Python

```python
import json

with open('src/core/config/tiers/accuracy_cost_tiers.json', 'r') as f:
    tiers = json.load(f)

budget_config = tiers['BUDGET']
```

## Testing

```bash
# Run all tests
python test_multiobjective.py

# Run specific test class
python -m unittest test_multiobjective.TestAccuracyCostOptimization

# Run with coverage
python -m coverage run test_multiobjective.py
python -m coverage report
```

## Advanced Usage

### Custom Optimization

```python
from pareto_accuracy_cost import Configuration, AccuracyCostEvaluator, NSGA2Optimizer

# Define custom configuration space
class CustomConfiguration(Configuration):
    # Extend with custom parameters
    pass

# Create custom evaluator
class CustomEvaluator(AccuracyCostEvaluator):
    def estimate_accuracy(self, config):
        # Custom accuracy model
        pass

    def estimate_cost(self, config):
        # Custom cost model
        pass

# Run optimization
optimizer = NSGA2Optimizer(population_size=200, generations=100)
pareto_front = optimizer.optimize(CustomEvaluator())
```

### Custom Scenarios

```python
from recommendation_engine import Scenario, UserPriorities

# Define custom scenario
custom_scenario = Scenario(
    name="CUSTOM_EDGE_IOT",
    description="Edge IoT deployment with battery constraints",
    priorities=UserPriorities(
        accuracy=0.2,
        cost=0.4,
        latency=0.3,
        availability=0.05,
        scalability=0.03,
        complexity=0.02
    ).normalize(),
    constraints={
        'min_availability': 0.98,
        'max_latency_ms': 500,
        'max_cost_multiplier': 1.3,
        'max_model_size': 50  # Battery constraints
    }
)
```

## Performance Considerations

### Optimization Time

| Population | Generations | Time (approx) |
|------------|-------------|---------------|
| 50 | 25 | 1-2 min |
| 100 | 50 | 5-10 min |
| 200 | 100 | 20-40 min |

### Memory Usage

- Population of 100: ~50-100 MB
- Population of 200: ~100-200 MB

### Parallelization

For faster optimization, modify `run_all.py` to run optimizers in parallel:

```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(run_optimizer, ['pareto_accuracy_cost.py', ...])
```

## Extending the System

### Adding New Objectives

1. Create new configuration dataclass
2. Implement evaluator with objective functions
3. Modify NSGA2Optimizer for new dominance relation
4. Add visualization

Example:

```python
@dataclass
class EnergyLatencyConfiguration:
    """Configuration for energy vs latency optimization."""
    voltage: float
    frequency: float
    # ... other parameters

class EnergyLatencyEvaluator:
    """Evaluate energy consumption and latency."""

    def estimate_energy_joules(self, config):
        # Energy model
        pass

    def estimate_latency_ms(self, config):
        # Latency model
        pass
```

## Troubleshooting

### No Pareto Solutions Found

- Increase population size
- Increase generations
- Check parameter bounds

### Poor Quality Solutions

- Verify objective functions
- Check mutation/crossover rates
- Ensure diverse initial population

### Out of Memory

- Reduce population size
- Process generations in batches
- Use disk-based storage

## References

- **NSGA-II**: Deb, K. et al. "A fast and elitist multiobjective genetic algorithm: NSGA-II" (2002)
- **Pareto Optimality**: Pareto, V. "Manual of Political Economy" (1906)
- **Multiobjective Optimization**: Miettinen, K. "Nonlinear Multiobjective Optimization" (1999)

## Contributing

To add new optimization frontiers:

1. Create `pareto_new_objective.py`
2. Follow existing patterns
3. Add to `run_all.py`
4. Update documentation
5. Add tests

## License

MIT License - See LICENSE file for details
