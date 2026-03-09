# Task Design for Meta-Learning

Comprehensive guide to designing task distributions for effective meta-learning.

## Overview

Task design is critical for meta-learning success. Well-designed task distributions enable:
- Better generalization
- Faster adaptation
- More robust performance

This guide covers task families, diversity metrics, and best practices.

## Table of Contents

1. [Task Families](#task-families)
2. [Diversity Metrics](#diversity-metrics)
3. [Sampling Strategies](#sampling-strategies)
4. [Generalization Analysis](#generalization-analysis)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

## Task Families

### What are Task Families?

Task families are groups of related tasks that share structure but differ in specifics. This shared structure enables knowledge transfer.

### Designing Task Families

#### 1. Identify Common Structure

```
Good: Related tasks with shared patterns
  - Reasoning: Logic, math, causal inference
  - Coding: Bug fixing, completion, refactoring

Bad: Unrelated tasks
  - Cooking, coding, dancing (no shared structure)
```

#### 2. Define Variation Space

```python
class TaskFamily:
    def __init__(self, name, base_params, variation_range):
        self.name = name
        self.base_params = base_params  # Shared structure
        self.variation_range = variation_range  # Task-specific variation

    def generate_task(self):
        # Sample task-specific parameters
        task_params = self.sample_variation()

        # Generate task data
        return self.create_task(task_params)
```

#### 3. Example Task Families

**Reasoning Family:**
```python
reasoning_family = TaskFamily(
    name='reasoning',
    base_params={
        'requires_logic': True,
        'multi_step': True,
        'abstract': True
    },
    variation_range=0.2  # 20% variation
)

# Tasks: Logic puzzles, math problems, causal inference
tasks = reasoning_family.generate_tasks(num_tasks=25)
```

**Coding Family:**
```python
coding_family = TaskFamily(
    name='coding',
    base_params={
        'syntax_sensitive': True,
        'structure_aware': True,
        'executable': True
    },
    variation_range=0.15
)

# Tasks: Bug fixing, code completion, refactoring
tasks = coding_family.generate_tasks(num_tasks=25)
```

### Optimal Number of Families

**Too Few (1-2):**
- Pros: Focused learning
- Cons: Poor generalization

**Optimal (4-6):**
- Pros: Good balance
- Cons: More computation

**Too Many (10+):**
- Pros: High diversity
- Cons: Hard to learn shared structure

**Recommendation:** 4-6 task families

### Tasks Per Family

**Guideline:** 20-30 tasks per family

```python
config = {
    'num_families': 4,
    'tasks_per_family': 25,
    'total_tasks': 100
}
```

## Diversity Metrics

### Why Diversity Matters

**Low Diversity:**
- Tasks too similar
- Poor generalization
- Overfitting risk

**High Diversity:**
- Better generalization
- Robust learning
- Slower convergence

**Optimal Diversity:**
- Balance similarity and variety
- Target diversity score: 0.4-0.6

### Entropy-Based Diversity

```python
def compute_entropy_diversity(tasks):
    """
    Measures spread of task features
    """
    # Extract features
    features = extract_task_features(tasks)

    # Normalize
    features = normalize(features)

    # Pairwise distances
    distances = pdist(features, metric='euclidean')

    # Diversity = coefficient of variation
    diversity = distances.std() / distances.mean()

    return diversity
```

**Interpretation:**
- < 0.3: Too similar
- 0.3-0.6: Good range
- > 0.6: Too diverse

### Coverage-Based Diversity

```python
def compute_coverage(tasks, n_clusters=10):
    """
    Measures how well tasks span the space
    """
    # Extract features
    features = extract_task_features(tasks)

    # Cluster tasks
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(features)

    # Coverage = ratio of filled clusters
    coverage = len(np.unique(labels)) / n_clusters

    return coverage
```

**Interpretation:**
- < 0.5: Poor coverage
- 0.5-0.8: Good coverage
- > 0.8: Excellent coverage

### Task Difficulty

```python
def compute_difficulty(task):
    """
    Measures task difficulty (0-1 scale)
    """
    factors = {
        'noise': task.noise_level * 5,
        'complexity': task.steps_required / 100,
        'ambiguity': task.ambiguity_score * 3
    }

    difficulty = min(1.0, sum(factors.values()))
    return difficulty
```

**Distribution:**
- Aim for uniform difficulty distribution
- Avoid all easy or all hard tasks

## Sampling Strategies

### Uniform Sampling

```python
def sample_uniform(tasks, batch_size):
    """
    Sample tasks uniformly at random
    """
    indices = np.random.choice(len(tasks), size=batch_size)
    return [tasks[i] for i in indices]
```

**Pros:** Simple, unbiased
**Cons:** May sample easy tasks too often

### Weighted Sampling

```python
def sample_weighted(tasks, batch_size):
    """
    Sample with probability proportional to difficulty
    """
    difficulties = [compute_difficulty(t) for t in tasks]
    probs = normalize(difficultities)

    indices = np.random.choice(
        len(tasks),
        size=batch_size,
        p=probs
    )
    return [tasks[i] for i in indices]
```

**Pros:** Focus on hard tasks
**Cons:** May ignore easy tasks

### Curriculum Sampling

```python
def sample_curriculum(tasks, batch_size, epoch, total_epochs):
    """
    Start with easy, progress to hard
    """
    # Compute curriculum position
    position = epoch / total_epochs

    # Filter tasks by difficulty
    max_difficulty = 0.3 + 0.7 * position  # 0.3 to 1.0
    filtered = [t for t in tasks if compute_difficulty(t) <= max_difficulty]

    # Sample from filtered
    return sample_uniform(filtered, batch_size)
```

**Pros:** Stable training
**Cons:** May slow convergence

### Stratified Sampling

```python
def sample_stratified(tasks, batch_size):
    """
    Sample evenly from task families
    """
    families = group_by_family(tasks)
    samples_per_family = batch_size // len(families)

    batch = []
    for family_tasks in families.values():
        batch.extend(sample_uniform(family_tasks, samples_per_family))

    return batch
```

**Pros:** Balanced representation
**Cons:** Requires task families

**Recommendation:** Stratified sampling for most cases

## Generalization Analysis

### In-Distribution (IID) Generalization

Testing on same family, different tasks:

```python
def evaluate_iid(model, train_family, test_family):
    """
    Test on same family, held-out tasks
    """
    train_tasks = sample_tasks(train_family, n=20)
    test_tasks = sample_tasks(test_family, n=5)

    # Meta-train
    meta_train(model, train_tasks)

    # Evaluate
    loss = evaluate(model, test_tasks)

    return loss
```

### Out-of-Distribution (OOD) Generalization

Testing on different family:

```python
def evaluate_ood(model, train_family, test_family):
    """
    Test on different family
    """
    train_tasks = sample_tasks(train_family, n=20)
    test_tasks = sample_tasks(test_family, n=5)

    # Meta-train
    meta_train(model, train_tasks)

    # Evaluate
    loss = evaluate(model, test_tasks)

    return loss
```

### Transfer Distance

```python
def compute_transfer_distance(tasks_a, tasks_b):
    """
    Measure distance between task families
    """
    features_a = extract_features(tasks_a)
    features_b = extract_features(tasks_b)

    # Average pairwise distance
    distances = cdist(features_a, features_b, metric='euclidean')
    return distances.mean()
```

**Interpretation:**
- Small distance: Easy transfer
- Medium distance: Moderate transfer
- Large distance: Hard transfer

## Best Practices

### 1. Balance Diversity

```python
# Target diversity
target_diversity = 0.5

while True:
    tasks = generate_tasks()
    diversity = compute_diversity(tasks)

    if abs(diversity - target_diversity) < 0.1:
        break  # Good diversity
```

### 2. Stratified Split

```python
# Split train/test by family
for family in task_families:
    family_tasks = get_family_tasks(family)

    # 80-20 split
    n_train = int(len(family_tasks) * 0.8)

    train.extend(family_tasks[:n_train])
    test.extend(family_tasks[n_train:])
```

### 3. Monitor Generalization

```python
# Track IID vs OOD
iid_loss = evaluate_iid(model, train_family, test_family)
ood_loss = evaluate_ood(model, train_family, other_family)

generalization_gap = ood_loss - iid_loss

if generalization_gap > threshold:
    # Improve task diversity
    add_more_tasks()
```

### 4. Curriculum Learning

```python
# Start easy, get harder
for epoch in range(num_epochs):
    difficulty = epoch / num_epochs
    tasks = sample_with_difficulty(difficulty)
    meta_update(model, tasks)
```

### 5. Quality Over Quantity

```python
# Filter bad tasks
def is_good_task(task):
    checks = {
        'has_solution': task.solution is not None,
        'not_too_hard': compute_difficulty(task) < 0.9,
        'not_too_easy': compute_difficulty(task) > 0.1,
        'well_formed': validate_task(task)
    }
    return all(checks.values())

good_tasks = [t for t in tasks if is_good_task(t)]
```

## Examples

### Example 1: Simple Task Distribution

```python
# Define families
families = ['reasoning', 'coding', 'dialogue', 'creative']

# Generate tasks
tasks = []
for family in families:
    family_tasks = generate_family_tasks(
        family_name=family,
        num_tasks=25
    )
    tasks.extend(family_tasks)

# Split train/test
train_tasks, test_tasks = stratified_split(tasks, ratio=0.8)

# Check diversity
diversity = compute_diversity(train_tasks)
coverage = compute_coverage(train_tasks)

print(f"Diversity: {diversity:.3f}")
print(f"Coverage: {coverage:.3f}")
```

### Example 2: Adaptive Task Sampling

```python
class AdaptiveTaskSampler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.performance_history = []

    def sample(self, batch_size):
        # Sample hard tasks if performance is good
        if self.is_performing_well():
            return self.sample_hard(batch_size)
        else:
            return self.sample_mixed(batch_size)

    def is_performing_well(self):
        return len(self.performance_history) > 10 and \
               np.mean(self.performance_history[-10:]) > 0.8
```

### Example 3: Multi-Objective Task Design

```python
def optimize_task_design(tasks):
    """
    Optimize for multiple objectives:
    1. Diversity
    2. Coverage
    3. Difficulty distribution
    """
    objectives = {
        'diversity': compute_diversity(tasks),
        'coverage': compute_coverage(tasks),
        'difficulty_balance': compute_difficulty_balance(tasks)
    }

    # Weighted sum
    score = (
        0.4 * objectives['diversity'] +
        0.3 * objectives['coverage'] +
        0.3 * objectives['difficulty_balance']
    )

    return score, objectives
```

## Task Templates

### Template 1: Classification

```python
def create_classification_task(
    num_classes: int,
    samples_per_class: int,
    feature_dim: int
):
    """Create K-way N-shot classification task"""

    # Generate class prototypes
    prototypes = torch.randn(num_classes, feature_dim)

    # Generate samples around prototypes
    support_x = []
    support_y = []
    query_x = []
    query_y = []

    for class_id in range(num_classes):
        # Support samples
        support_samples = prototypes[class_id] + \
                         0.1 * torch.randn(samples_per_class, feature_dim)
        support_x.append(support_samples)
        support_y.extend([class_id] * samples_per_class)

        # Query samples
        query_samples = prototypes[class_id] + \
                       0.1 * torch.randn(samples_per_class, feature_dim)
        query_x.append(query_samples)
        query_y.extend([class_id] * samples_per_class)

    return {
        'support_x': torch.cat(support_x),
        'support_y': torch.tensor(support_y),
        'query_x': torch.cat(query_x),
        'query_y': torch.tensor(query_y)
    }
```

### Template 2: Regression

```python
def create_regression_task(
    num_samples: int,
    input_dim: int,
    function_type: str
):
    """Create regression task"""

    # Sample inputs
    support_x = torch.randn(num_samples, input_dim)

    # Apply function
    if function_type == 'linear':
        support_y = support_x.sum(dim=1)
    elif function_type == 'quadratic':
        support_y = support_x.pow(2).sum(dim=1)
    else:
        support_y = torch.randn(num_samples)

    # Query set
    query_x = torch.randn(num_samples // 2, input_dim)
    query_y = apply_function(query_x, function_type)

    return {
        'support_x': support_x,
        'support_y': support_y,
        'query_x': query_x,
        'query_y': query_y
    }
```

### Template 3: Reinforcement Learning

```python
def create_rl_task(
    env_name: str,
    num_episodes: int,
    episode_length: int
):
    """Create RL task"""

    # Create environment
    env = gym.make(env_name)

    # Collect episodes
    support_trajectories = []
    for _ in range(num_episodes // 2):
        trajectory = collect_episode(env, episode_length)
        support_trajectories.append(trajectory)

    query_trajectories = []
    for _ in range(num_episodes // 2):
        trajectory = collect_episode(env, episode_length)
        query_trajectories.append(trajectory)

    return {
        'support': support_trajectories,
        'query': query_trajectories,
        'env': env
    }
```

## Conclusion

Well-designed task distributions are critical for meta-learning success. By carefully designing task families, measuring diversity, and using appropriate sampling strategies, you can create task distributions that enable rapid adaptation and robust generalization.

**Key Takeaways:**
1. Design 4-6 related task families
2. Aim for diversity score of 0.4-0.6
3. Use stratified sampling
4. Monitor IID and OOD generalization
5. Balance quality over quantity

For implementation details, see `task_distribution.py`.
