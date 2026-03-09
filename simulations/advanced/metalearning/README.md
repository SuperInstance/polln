# POLLN Meta-Learning System

Complete meta-learning framework for POLLN agents, enabling rapid adaptation to new tasks with minimal data.

## Overview

This system implements state-of-the-art meta-learning algorithms for POLLN:

- **MAML**: Model-Agnostic Meta-Learning (best accuracy)
- **Reptile**: First-order meta-learning (3x faster)
- **Few-Shot Learning**: Learn from 1, 5, or 10 examples
- **Rapid Adaptation**: LoRA, Adapters, Prompts
- **Task Distribution**: Optimized task families

## Quick Start

```bash
# Run all simulations
python simulations/advanced/metalearning/run_all.py

# Run individual components
python simulations/advanced/metalearning/maml_implementation.py
python simulations/advanced/metalearning/reptile_implementation.py
python simulations/advanced/metalearning/few_shot_testing.py

# Run tests
python simulations/advanced/metalearning/test_metalearning.py
```

## Generated Files

### TypeScript Implementation
- `src/core/meta/learning.ts` - Production meta-learning config

### Configuration Files
- `maml_config.json` - MAML hyperparameters
- `reptile_config.json` - Reptile hyperparameters
- `few_shot_config.json` - Few-shot settings
- `task_config.json` - Task distribution
- `rapid_adaptation_config.json` - Adaptation strategies
- `meta_learning_config.json` - Unified config

### Visualizations
- `maml_hyperparameters.png` - Hyperparameter analysis
- `maml_reptile_comparison.png` - MAML vs Reptile
- `few_shot_sample_efficiency.png` - Sample efficiency
- `task_distribution.png` - Task distribution visualization
- `rapid_adaptation_comparison.png` - Strategy comparison

## Architecture

### MAML (Model-Agnostic Meta-Learning)

Bi-level optimization for rapid adaptation:

```
Inner Loop (Task Adaptation):
  θ'_i = θ - α∇_θ L_Ti(f_θ)

Outer Loop (Meta-Update):
  θ = θ - β∇_θ Σ L_Ti(f_θ'_i)
```

**Configuration:**
```typescript
maml: {
  innerLoop: {
    learningRate: 0.01,
    steps: 5,
    frozenLayers: ['embedding']
  },
  outerLoop: {
    learningRate: 0.001,
    metaBatchSize: 32
  }
}
```

### Reptile (First-Order Meta-Learning)

Faster alternative using gradient differences:

```
Adapt: θ'_i = θ - α∇_θ L_Ti(f_θ)
Meta-update: θ ← θ + ε(θ'_i - θ)
```

**Configuration:**
```typescript
reptile: {
  metaLearningRate: 0.1,
  innerSteps: 10,
  metaBatchSize: 32
}
```

**Advantages:**
- 3x faster than MAML
- Lower memory usage
- Minimal performance loss

### Few-Shot Learning

K-shot N-way learning:

- **1-shot**: Learn from single example (fastest)
- **5-shot**: Learn from five examples (recommended)
- **10-shot**: Learn from ten examples (best performance)

**Configuration:**
```typescript
fewShot: {
  k: 5,  // 5-shot learning
  ways: 5,  // 5-way classification
  querySet: 15,
  supportSet: 25
}
```

### Rapid Adaptation

Parameter-efficient fine-tuning:

**LoRA (Recommended):**
```typescript
lora: {
  rank: 16,
  alpha: 32,
  dropout: 0.1,
  targetLayers: ['attention', 'mlp']
}
```

**Adapters:**
```typescript
adapter: {
  dim: 64,
  layers: 2
}
```

### Task Distribution

Optimized task families for meta-training:

```typescript
taskDistribution: {
  metaTrainTasks: 80,
  metaTestTasks: 20,
  taskFamilies: ['reasoning', 'coding', 'dialogue', 'creative'],
  sampling: 'uniform'
}
```

## Usage in POLLN

### Basic Usage

```typescript
import { META_LEARNING_CONFIG } from './core/meta/learning';

// Access configuration
const config = META_LEARNING_CONFIG;

// Use MAML for high accuracy
if (config.maml.enabled) {
  const maml = new MAMLLearner(config.maml);
  await maml.metaTrain(tasks);
}
```

### Method Selection

```typescript
import { selectMetaLearningMethod } from './core/meta/learning';

// Auto-select based on constraints
const method = selectMetaLearningMethod({
  accuracy: 'high',
  speed: 'fast'
});

// Returns: 'maml' | 'reptile' | 'lora'
```

### Few-Shot Learning

```typescript
import { selectFewShotSetting } from './core/meta/learning';

// Select optimal shot setting
const k = selectFewShotSetting(availableExamples);

// Adapt with K examples
const adapted = await metaLearner.adapt(task, k);
```

### Adaptation Strategies

```typescript
import { selectAdaptationStrategy } from './core/meta/learning';

// Select strategy for scenario
const strategy = selectAdaptationStrategy('low_resource');

// Apply adaptation
await agent.adapt(task, { strategy });
```

## Performance Benchmarks

### Adaptation Speed
- **MAML**: 5-10 gradient steps
- **Reptile**: 10-15 gradient steps
- **From Scratch**: 50-100 gradient steps

### Sample Efficiency
- **1-shot**: 3-5x better than scratch
- **5-shot**: 5-8x better than scratch
- **10-shot**: 8-10x better than scratch

### Parameter Efficiency
- **LoRA**: 0.5% of parameters trainable
- **Adapter**: 1% of parameters trainable
- **Fine-tune**: 100% of parameters trainable

## Recommendations

### Scenario-Based Selection

**High Accuracy Requirement:**
```typescript
// Use MAML
const method = 'maml';
const config = META_LEARNING_CONFIG.maml;
```

**Fast Adaptation:**
```typescript
// Use Reptile (3x faster)
const method = 'reptile';
const config = META_LEARNING_CONFIG.reptile;
```

**Low Resource:**
```typescript
// Use LoRA (most efficient)
const strategy = 'lora';
const config = META_LEARNING_CONFIG.adaptation.lora;
```

### Hyperparameter Tuning

1. **Inner Learning Rate** (α): Controls adaptation speed
   - Too low: Slow adaptation
   - Too high: Unstable
   - Optimal: 0.01 (MAML), 0.01 (Reptile)

2. **Outer Learning Rate** (β): Controls meta-update
   - Too low: Slow meta-learning
   - Too high: Unstable
   - Optimal: 0.001 (MAML), 0.1 (Reptile)

3. **Inner Steps** (K): How much to adapt per task
   - Too few: Underfitting
   - Too many: Overfitting, slow
   - Optimal: 5 (MAML), 10 (Reptile)

## Research Foundations

### MAML
- **Paper**: "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks" (Finn et al., 2017)
- **Key Innovation**: Learn initialization that adapts with few gradients
- **Use Case**: Best accuracy, complex tasks

### Reptile
- **Paper**: "On First-Order Meta-Learning Algorithms" (Nichol et al., 2018)
- **Key Innovation**: First-order approximation of MAML
- **Use Case**: Fast adaptation, resource-constrained

### LoRA
- **Paper**: "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021)
- **Key Innovation**: Low-rank decomposition for efficient adaptation
- **Use Case**: Parameter-efficient fine-tuning

## Citation

If you use this meta-learning system in your research:

```bibtex
@misc{polln_metalearning,
  title={POLLN Meta-Learning System},
  author={POLLN Contributors},
  year={2026},
  url={https://github.com/SuperInstance/polln}
}
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## References

1. Finn, C., et al. (2017). "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks"
2. Nichol, A., et al. (2018). "On First-Order Meta-Learning Algorithms"
3. Hu, E. J., et al. (2021). "LoRA: Low-Rank Adaptation of Large Language Models"
4. Brown, T., et al. (2020). "Language Models are Few-Shot Learners"
5. Houlsby, N., et al. (2019). "Parameter-Efficient Transfer Learning for NLP"

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.
