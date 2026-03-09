# Meta-Learning Guide for POLLN

Comprehensive guide to implementing and using meta-learning in POLLN agents.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [MAML Implementation](#maml-implementation)
4. [Reptile Implementation](#reptile-implementation)
5. [Few-Shot Learning](#few-shot-learning)
6. [Rapid Adaptation](#rapid-adaptation)
7. [Task Design](#task-design)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Topics](#advanced-topics)

## Introduction

### What is Meta-Learning?

Meta-learning, or "learning to learn," enables agents to quickly adapt to new tasks using prior experience. Instead of learning from scratch, meta-learned agents can adapt with just a few examples.

### Why Meta-Learning for POLLN?

**Traditional Learning:**
- Requires thousands of examples per task
- Slow adaptation to new scenarios
- Poor generalization

**Meta-Learning:**
- Adapts from 1-10 examples
- Rapid adaptation (5-10 gradient steps)
- Better generalization across tasks

### Key Benefits

1. **Sample Efficiency**: Learn from limited data
2. **Rapid Adaptation**: Adapt in seconds, not hours
3. **Better Generalization**: Transfer knowledge across tasks
4. **Resource Efficient**: Parameter-efficient methods available

## Core Concepts

### Support Set vs Query Set

```
Support Set: Examples used for adaptation
  - K examples per class (K-shot)
  - Used in inner loop

Query Set: Examples used for evaluation
  - Separate from support set
  - Used for meta-update
```

### Inner Loop vs Outer Loop

```
Inner Loop (Task Adaptation):
  - Adapt to specific task
  - K gradient steps on support set
  - Fast (milliseconds)

Outer Loop (Meta-Update):
  - Update across task batch
  - Optimize for generalization
  - Slower (seconds)
```

### K-Shot N-Way Learning

```
K-Shot: Number of examples per class
  - 1-shot: Single example (fastest)
  - 5-shot: Five examples (balanced)
  - 10-shot: Ten examples (best)

N-Way: Number of classes per task
  - 5-way: 5 classes (typical)
  - 10-way: 10 classes (harder)
```

## MAML Implementation

### Algorithm Overview

```
1. Sample batch of tasks
2. For each task:
   a. Copy parameters
   b. K gradient steps on support set
   c. Compute loss on query set
3. Meta-update: Minimize query loss
4. Repeat
```

### Implementation Steps

#### 1. Define Model

```python
class ValueNetwork(nn.Module):
    def __init__(self, state_dim=128, hidden_dim=256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.value_head = nn.Linear(hidden_dim, 1)
```

#### 2. Inner Loop Adaptation

```python
def inner_loop(model, task, inner_lr, inner_steps):
    # Copy model
    adapted = deepcopy(model)

    # K gradient steps
    for step in range(inner_steps):
        loss = compute_loss(adapted, task['support'])
        loss.backward()

        # Gradient descent
        for param in adapted.parameters():
            param.data -= inner_lr * param.grad.data

    return adapted
```

#### 3. Outer Loop Meta-Update

```python
def outer_loop(model, task_batch, outer_lr):
    meta_loss = 0

    # Compute adapted losses
    for task in task_batch:
        adapted = inner_loop(model, task)
        query_loss = compute_loss(adapted, task['query'])
        meta_loss += query_loss

    # Meta-update
    meta_loss.backward()
    for param in model.parameters():
        param.data -= outer_lr * param.grad.data
```

### Hyperparameter Tuning

**Inner Learning Rate (α):**
- Range: [0.001, 0.1]
- Default: 0.01
- Effect: Controls adaptation speed

**Outer Learning Rate (β):**
- Range: [0.0001, 0.01]
- Default: 0.001
- Effect: Controls meta-learning speed

**Inner Steps (K):**
- Range: [1, 10]
- Default: 5
- Effect: How much to adapt per task

**Meta-Batch Size:**
- Range: [16, 64]
- Default: 32
- Effect: Stability of meta-update

## Reptile Implementation

### Algorithm Overview

```
1. Sample batch of tasks
2. For each task:
   a. K gradient steps from θ
   b. Get adapted parameters θ'_i
3. Meta-update: Interpolate toward adapted
   θ ← θ + ε(θ'_i - θ)
4. Repeat
```

### Key Difference from MAML

**MAML:**
- Second-order derivatives
- Computationally expensive
- Best accuracy

**Reptile:**
- First-order only
- 3x faster
- Minimal accuracy loss

### Implementation

```python
def reptile_meta_update(model, task_batch, meta_lr, inner_steps):
    # Collect adapted parameters
    adapted_params_list = []

    for task in task_batch:
        # Adapt to task
        adapted = deepcopy(model)

        for step in range(inner_steps):
            loss = compute_loss(adapted, task['support'])
            loss.backward()

            for param in adapted.parameters():
                param.data -= inner_lr * param.grad.data

        # Store adapted parameters
        adapted_params_list.append({
            name: param.clone()
            for name, param in adapted.named_parameters()
        })

    # Meta-update: interpolate toward adapted
    for name, param in model.named_parameters():
        grad_diff = torch.zeros_like(param)

        for adapted_params in adapted_params_list:
            grad_diff += (adapted_params[name] - param.data)

        grad_diff /= len(task_batch)
        param.data += meta_lr * grad_diff
```

### When to Use Reptile

**Use Reptile when:**
- Need fast adaptation
- Limited computational resources
- Can tolerate small accuracy loss

**Use MAML when:**
- Accuracy is critical
- Have sufficient resources
- Task complexity is high

## Few-Shot Learning

### K-Shot Performance

| Shots | Examples | Performance | Adaptation Time |
|-------|----------|-------------|-----------------|
| 1-shot | 1 | 0.15 loss | Fastest |
| 5-shot | 5 | 0.08 loss | Fast |
| 10-shot | 10 | 0.05 loss | Medium |

### Implementation

```python
def few_shot_adapt(model, task, k_shot):
    # Truncate to k-shot
    support_x = task['support_x'][:k_shot]
    support_y = task['support_y'][:k_shot]

    # Adapt on support set
    adapted = adapt_model(model, support_x, support_y)

    # Evaluate on query set
    query_loss = evaluate(adapted, task['query_x'], task['query_y'])

    return query_loss
```

### Selecting K

```python
def select_k_shots(available_examples, accuracy_requirement):
    if available_examples >= 10 and accuracy_requirement == 'high':
        return 10  # Best performance
    elif available_examples >= 5:
        return 5   # Balanced
    elif available_examples >= 1:
        return 1   # Minimal
    else:
        raise ValueError("Insufficient examples")
```

## Rapid Adaptation

### LoRA (Low-Rank Adaptation)

**Concept:**
```
W' = W + BA
where B ∈ R^(d×r), A ∈ R^(r×d), r << d
```

**Benefits:**
- Only 0.5% parameters trainable
- Minimal memory overhead
- Fast adaptation

**Implementation:**
```python
class LoRALayer(nn.Module):
    def __init__(self, original_layer, rank, alpha):
        self.original = original_layer
        self.lora_A = nn.Parameter(torch.randn(rank, in_dim) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(out_dim, rank))
        self.scaling = alpha / rank

    def forward(self, x):
        original_out = self.original(x)
        lora_out = x @ self.lora_A.T @ self.lora_B.T * self.scaling
        return original_out + lora_out
```

### Adapter Layers

**Concept:**
```
h' = LayerNorm(h) + Adapter(h)
h'' = h + h'
```

**Benefits:**
- 1% parameters trainable
- Stable training
- Easy to add/remove

**Implementation:**
```python
class AdapterLayer(nn.Module):
    def __init__(self, dim, adapter_dim):
        self.down = nn.Linear(dim, adapter_dim)
        self.up = nn.Linear(adapter_dim, dim)
        self.activation = nn.ReLU()

        # Initialize near-zero
        nn.init.zeros_(self.up.weight)

    def forward(self, x):
        adapted = self.up(self.activation(self.down(x)))
        return x + adapted  # Residual
```

### Strategy Selection

| Scenario | Strategy | Parameters | Speed | Accuracy |
|----------|----------|------------|-------|----------|
| Low resource | Adapter | 1% | Fast | Good |
| Balanced | LoRA | 0.5% | Fast | Better |
| High performance | Fine-tune | 100% | Slow | Best |

## Task Design

### Task Families

Design related tasks that share structure:

```
Reasoning Family:
  - Logic puzzles
  - Math problems
  - Causal inference

Coding Family:
  - Bug fixing
  - Code completion
  - Refactoring
```

### Diversity Metrics

**Entropy-Based:**
```python
def compute_diversity(tasks):
    features = extract_features(tasks)
    distances = pdist(features, metric='euclidean')
    diversity = distances.std() / distances.mean()
    return diversity
```

**Coverage-Based:**
```python
def compute_coverage(tasks, n_clusters=10):
    features = extract_features(tasks)
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(features)
    coverage = len(np.unique(labels)) / n_clusters
    return coverage
```

### Optimal Task Distribution

**Guidelines:**
- 4-6 task families
- 20-30 tasks per family
- 80% meta-train, 20% meta-test
- Balance difficulty levels

## Best Practices

### 1. Start Simple

```python
# Start with 5-way 5-shot
config = {
    'ways': 5,
    'shots': 5,
    'inner_steps': 5
}
```

### 2. Monitor Adaptation

```python
# Track convergence
for step in range(max_steps):
    loss = adapt_step(model, task)
    if abs(prev_loss - loss) < threshold:
        break  # Converged
```

### 3. Validate Generalization

```python
# Test on held-out tasks
train_tasks = sample_tasks(meta_train_tasks)
test_tasks = sample_tasks(meta_test_tasks)

train_loss = evaluate(model, train_tasks)
test_loss = evaluate(model, test_tasks)

generalization_gap = test_loss - train_loss
```

### 4. Use Curriculum Learning

```python
# Start easy, get harder
for epoch in range(num_epochs):
    difficulty = epoch / num_epochs
    tasks = sample_tasks_with_difficulty(difficulty)
    meta_update(model, tasks)
```

## Troubleshooting

### Problem: Overfitting to Meta-Train Tasks

**Symptoms:**
- Low train loss, high test loss
- Poor generalization

**Solutions:**
- Increase meta-batch size
- Add task diversity
- Reduce inner steps
- Increase regularization

### Problem: Underfitting

**Symptoms:**
- High train and test loss
- Slow adaptation

**Solutions:**
- Increase model capacity
- Increase inner steps
- Increase learning rates
- Train longer

### Problem: Unstable Training

**Symptoms:**
- Loss oscillates
- NaN gradients

**Solutions:**
- Decrease learning rates
- Use gradient clipping
- Normalize inputs
- Check task quality

### Problem: Slow Adaptation

**Symptoms:**
- Takes many steps to converge
- Poor few-shot performance

**Solutions:**
- Use Reptile instead of MAML
- Increase inner learning rate
- Pre-train on related tasks
- Use better initialization

## Advanced Topics

### First-Order MAML (FOMAML)

Approximate MAML without second-order derivatives:

```python
# Standard MAML: loss.backward(create_graph=True)
# FOMAML: loss.backward(create_graph=False)

loss.backward(create_graph=False)  # Faster
```

### Multi-Task Meta-Learning

Learn across multiple task types:

```python
# Sample from different task families
tasks = []
for family in task_families:
    tasks.extend(sample_from_family(family, n=5))
```

### Continual Meta-Learning

Continually adapt to new tasks:

```python
for new_task in task_stream:
    # Meta-update with new task
    meta_update(model, [new_task] + sample_replay_buffer())

    # Add to replay buffer
    replay_buffer.add(new_task)
```

### Hierarchical Meta-Learning

Learn at multiple levels:

```python
# Level 1: Task-level adaptation
# Level 2: Family-level adaptation
# Level 3: Global meta-learning
```

## References

### Papers

1. **MAML**: Finn et al. (2017) - "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks"
2. **Reptile**: Nichol et al. (2018) - "On First-Order Meta-Learning Algorithms"
3. **LoRA**: Hu et al. (2021) - "LoRA: Low-Rank Adaptation of Large Language Models"
4. **Adapters**: Houlsby et al. (2019) - "Parameter-Efficient Transfer Learning for NLP"

### Code Examples

See simulation files for complete implementations:
- `maml_implementation.py`
- `reptile_implementation.py`
- `few_shot_testing.py`
- `rapid_adaptation.py`

## Glossary

- **Inner Loop**: Task-specific adaptation
- **Outer Loop**: Meta-update across tasks
- **Support Set**: Examples for adaptation
- **Query Set**: Examples for evaluation
- **K-Shot**: Number of examples per class
- **N-Way**: Number of classes per task
- **Meta-Train**: Tasks for learning initialization
- **Meta-Test**: Tasks for evaluation
- **LoRA**: Low-Rank Adaptation
- **First-Order**: Approximation without second-order derivatives

## Conclusion

Meta-learning enables POLLN agents to rapidly adapt to new tasks with minimal data. By combining MAML, Reptile, and rapid adaptation strategies, agents can achieve state-of-the-art few-shot performance.

For questions or issues, consult the simulation files or open a GitHub issue.
