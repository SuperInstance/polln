# Quick Start Guide - POLLN Multiobjective Optimization

Get started with Pareto-optimal POLLN configurations in 5 minutes.

## Installation

```bash
# Navigate to the multiobjective directory
cd simulations/advanced/multiobjective

# Install Python dependencies
pip install numpy matplotlib

# (Optional) Install all dependencies for enhanced features
pip install -r requirements.txt
```

## Option 1: Use Predefined Configurations (Fastest)

The fastest way - use pre-generated tier configurations:

```typescript
import { Colony } from '@polln/core';
import { CONFIG_TIERS } from '@polln/core/config/tiers';

// Use a predefined tier
const colony = new Colony({
  ...CONFIG_TIERS.ACCURACY_COST_STANDARD,
  colonySize: 100
});
```

Available tiers:
- `ACCURACY_COST_BUDGET` - Lowest cost, acceptable quality
- `ACCURACY_COST_STANDARD` - Balanced performance
- `ACCURACY_COST_PERFORMANCE` - High quality
- `SPEED_QUALITY_REALTIME` - Sub-100ms latency
- `SPEED_QUALITY_INTERACTIVE` - 100-500ms latency
- `ROBUSTNESS_EFFICIENCY_HIGH` - 99.9% availability
- `SCALABILITY_COMPLEXITY_MEDIUM` - 100-500 agents

## Option 2: Run Optimizations (Recommended)

Generate custom Pareto-optimal configurations:

```bash
# Run all optimizations (5-10 minutes)
python run_all.py

# Or run individual optimizations
python pareto_accuracy_cost.py        # Accuracy vs Cost
python pareto_speed_quality.py        # Speed vs Quality
python pareto_robustness_efficiency.py # Robustness vs Efficiency
python pareto_scalability_complexity.py # Scalability vs Complexity
```

This generates:
- Tier configuration JSON files
- TypeScript definitions
- Visualization plots
- Recommendation reports

## Option 3: Interactive Recommendations

Get personalized configuration recommendations:

```bash
python recommendation_engine.py
```

Follow the prompts to:
1. Select a scenario (Production, Edge, Research, etc.)
2. Or define custom priorities
3. Get recommended configuration with explanations

## Option 4: Python API

Use the recommendation engine programmatically:

```python
from recommendation_engine import Scenario, RecommendationEngine

engine = RecommendationEngine()

# Scenario-based recommendation
config_name, config, score = engine.recommend_by_scenario(Scenario.production())
print(f"Recommended: {config_name}")
print(f"Config: {config}")

# Custom priorities
from recommendation_engine import UserPriorities

priorities = UserPriorities(
    accuracy=0.5,
    cost=0.3,
    latency=0.2
).normalize()

config_name, config, score = engine.recommend_by_priorities(priorities)
```

## Common Scenarios

### Edge IoT Deployment
```python
config_name, config, score = engine.recommend_by_scenario(Scenario.edge())
# Result: <100ms latency, minimal cost, battery-efficient
```

### Production API Service
```python
config_name, config, score = engine.recommend_by_scenario(Scenario.production())
# Result: 99.9% availability, balanced performance
```

### Research Experimentation
```python
config_name, config, score = engine.recommend_by_scenario(Scenario.research())
# Result: Maximum quality, no latency constraints
```

### Real-time Application
```python
config_name, config, score = engine.recommend_by_scenario(Scenario.realtime())
# Result: <100ms latency, high availability
```

## Viewing Results

### Generated Files

After running `run_all.py`, check these locations:

**Configuration Files:**
```
src/core/config/tiers/
├── accuracy_cost_tiers.json
├── speed_quality_tiers.json
├── robustness_efficiency_tiers.json
├── scalability_complexity_tiers.json
└── scenarios.json
```

**Visualization Plots:**
```
outputs/
├── pareto_accuracy_cost.png
├── pareto_speed_quality.png
├── pareto_robustness_efficiency.png
└── pareto_scalability_complexity.png
```

**Reports:**
```
outputs/
├── pareto_optimization_report.md
└── recommendation_report.md
```

### Quick Reference

```bash
# View all available tiers
python -c "from recommendation_engine import ConfigurationDatabase; db = ConfigurationDatabase(); print(db.configs.keys())"

# View specific tier
python -c "from recommendation_engine import ConfigurationDatabase; db = ConfigurationDatabase(); import json; print(json.dumps(db.get_config('accuracy_cost', 'BUDGET'), indent=2))"

# Run examples
python example_usage.py
```

## Testing Your Configuration

```typescript
import { Colony } from '@polln/core';
import { CONFIG_TIERS, validateConfig } from '@polln/core/config/tiers';

// Get configuration
const config = CONFIG_TIRES.ACCURACY_COST_STANDARD;

// Validate against requirements
const isValid = validateConfig(config, {
  max_latency_ms: 500,
  min_availability: 0.99,
  max_cost_multiplier: 2.0
});

if (isValid) {
  // Create colony with config
  const colony = new Colony({
    ...config,
    colonySize: 100
  });

  // Monitor metrics
  colony.on('metrics', (metrics) => {
    console.log('Latency:', metrics.latency);
    console.log('Accuracy:', metrics.accuracy);
  });
}
```

## Next Steps

1. **Choose a tier** based on your primary constraint (latency, cost, availability, quality)
2. **Test locally** with your workload
3. **Monitor metrics** to validate expected performance
4. **Adjust as needed** by combining multiple tiers
5. **Scale up** by moving to higher tiers when needed

## Troubleshooting

**"Module not found" error:**
```bash
pip install numpy matplotlib
```

**"No configuration files found":**
```bash
python run_all.py  # Generate configurations first
```

**High memory usage:**
- Reduce population size in optimization scripts
- Run optimizations individually instead of all at once

**Slow optimization:**
- Reduce generations (default: 50, try: 25)
- Reduce population size (default: 100, try: 50)

## Getting Help

- **Full documentation**: See `README.md`
- **Pareto theory**: See `PARETO_GUIDE.md`
- **Tier selection**: See `TIER_SELECTION.md`
- **Examples**: Run `python example_usage.py`
- **Tests**: Run `python test_multiobjective.py`

## Quick Reference Card

| Need | Use | Command |
|------|-----|---------|
| Fast setup | Predefined tiers | Import `CONFIG_TIERS` |
| Custom configs | Run optimizations | `python run_all.py` |
| Recommendations | Interactive CLI | `python recommendation_engine.py` |
| Examples | See usage | `python example_usage.py` |
| Testing | Validate setup | `python test_multiobjective.py` |
| Understanding | Read guides | Check `*.md` files |

---

**Time to get started:**
- Option 1: 1 minute (use predefined)
- Option 2: 10 minutes (run optimizations)
- Option 3: 2 minutes (interactive recommendations)

**Recommended:** Start with Option 1 for immediate results, then run Option 2 for custom configurations.
