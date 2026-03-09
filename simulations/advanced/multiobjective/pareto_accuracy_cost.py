"""
Pareto Optimization: Accuracy vs Cost Frontier

Finds optimal configurations balancing:
- Maximize accuracy (through cache hits, model quality, checkpoint frequency)
- Minimize cost (compute, storage, API calls)

Uses NSGA-II algorithm for multiobjective optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Configuration:
    """A POLLN configuration with tunable parameters."""
    model_size: int  # Parameter count (millions)
    checkpoint_frequency: int  # Checkpoints per 1000 tokens
    cache_size_mb: int  # KV-cache size in MB
    batch_size: int  # Batch size for processing
    compression_level: float  # 0-1, KV-anchor compression
    temperature: float  # Sampling temperature
    use_federated: bool  # Enable federated learning
    replication_factor: int  # Agent replication for reliability

    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_size': self.model_size,
            'checkpoint_frequency': self.checkpoint_frequency,
            'cache_size_mb': self.cache_size_mb,
            'batch_size': self.batch_size,
            'compression_level': self.compression_level,
            'temperature': self.temperature,
            'use_federated': self.use_federated,
            'replication_factor': self.replication_factor
        }


class AccuracyCostEvaluator:
    """Evaluates accuracy and cost for a given configuration."""

    # Empirical cost factors (in arbitrary units)
    COMPUTE_COST_PER_1M_PARAMS = 0.001  # Per token
    STORAGE_COST_PER_MB = 0.0001  # Per hour
    API_COST_PER_CALL = 0.0001

    # Accuracy impact factors (empirical)
    MODEL_SIZE_ACCURACY_EXPONENT = 0.15  # Diminishing returns
    CACHE_HIT_ACCURACY_BOOST = 0.05
    CHECKPOINT_ACCURACY_BOOST = 0.02
    FEDERATED_ACCURACY_BOOST = 0.03

    def __init__(self, tokens_per_request: int = 1000, requests_per_hour: int = 100):
        self.tokens_per_request = tokens_per_request
        self.requests_per_hour = requests_per_hour

    def estimate_accuracy(self, config: Configuration) -> float:
        """Estimate accuracy score (0-1) for configuration."""
        # Base accuracy from model size (diminishing returns)
        base_accuracy = 1 - np.exp(-0.1 * config.model_size ** 0.3)

        # Cache hit accuracy boost
        cache_factor = min(1.0, config.cache_size_mb / 1024)  # Normalize to GB
        accuracy = base_accuracy + self.CACHE_HIT_ACCURACY_BOOST * cache_factor

        # Checkpoint accuracy boost
        checkpoint_boost = self.CHECKPOINT_ACCURACY_BOOST * (config.checkpoint_frequency / 20)
        accuracy += checkpoint_boost

        # Federated learning boost
        if config.use_federated:
            accuracy += self.FEDERATED_ACCURACY_BOOST

        # Compression penalty (small accuracy loss)
        accuracy *= (1 - 0.02 * config.compression_level)

        # Temperature penalty (higher temp = less consistent)
        accuracy *= (1 - 0.1 * config.temperature)

        return min(0.98, accuracy)  # Cap at 98%

    def estimate_hourly_cost(self, config: Configuration) -> float:
        """Estimate hourly cost in arbitrary units."""
        cost = 0.0

        # Compute cost (model size × tokens)
        compute = (config.model_size * self.COMPUTE_COST_PER_1M_PARAMS *
                  self.tokens_per_request * self.requests_per_hour)
        cost += compute

        # Storage cost (cache + model storage)
        storage_mb = config.cache_size_mb + (config.model_size * 4)  # ~4MB per 1M params
        storage = storage_mb * self.STORAGE_COST_PER_MB
        cost += storage

        # Replication cost
        cost *= config.replication_factor

        # Federated learning adds communication cost
        if config.use_federated:
            cost *= 1.2

        # Compression reduces cost
        cost *= (1 - 0.1 * config.compression_level)

        # Batch efficiency (larger batches = more efficient)
        batch_efficiency = min(1.0, config.batch_size / 32)
        cost *= (2 - batch_efficiency)  # 2x to 1x multiplier

        return cost


class NSGA2Optimizer:
    """NSGA-II multiobjective optimizer."""

    def __init__(self, population_size: int = 100, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8

    def dominates(self, obj1: Tuple[float, float], obj2: Tuple[float, float]) -> bool:
        """Check if obj1 dominates obj2 (both better, at least one strictly)."""
        acc1, cost1 = obj1
        acc2, cost2 = obj2
        return (acc1 >= acc2 and cost1 <= cost2) and (acc1 > acc2 or cost1 < cost2)

    def fast_non_dominated_sort(self, population: List[Configuration],
                                evaluator: AccuracyCostEvaluator) -> List[List[Configuration]]:
        """Sort population into Pareto fronts."""
        # Evaluate all
        objectives = [(evaluator.estimate_accuracy(ind),
                      evaluator.estimate_hourly_cost(ind))
                     for ind in population]

        # Count dominances
        domination_count = [0] * len(population)
        dominated_solutions = [[] for _ in range(len(population))]

        for i in range(len(population)):
            for j in range(len(population)):
                if i != j:
                    if self.dominates(objectives[i], objectives[j]):
                        dominated_solutions[i].append(j)
                    elif self.dominates(objectives[j], objectives[i]):
                        domination_count[i] += 1

        # Build fronts
        fronts = []
        current_front = []

        for i in range(len(population)):
            if domination_count[i] == 0:
                current_front.append(population[i])

        fronts.append(current_front)

        while current_front:
            next_front = []
            for i in current_front:
                for j in dominated_solutions[population.index(i)]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(population[population.index(i)])

            if next_front:
                fronts.append(next_front)
            current_front = next_front

        return fronts

    def crowding_distance(self, front: List[Configuration],
                         evaluator: AccuracyCostEvaluator) -> List[float]:
        """Calculate crowding distance for diversity preservation."""
        if len(front) <= 2:
            return [float('inf')] * len(front)

        # Get objectives
        accuracies = [evaluator.estimate_accuracy(ind) for ind in front]
        costs = [evaluator.estimate_hourly_cost(ind) for ind in front]

        distances = [0.0] * len(front)

        # Accuracy distance
        acc_sorted = sorted(range(len(front)), key=lambda i: accuracies[i])
        acc_range = accuracies[acc_sorted[-1]] - accuracies[acc_sorted[0]]

        for i in range(1, len(front) - 1):
            idx = acc_sorted[i]
            distances[idx] += (accuracies[acc_sorted[i + 1]] -
                             accuracies[acc_sorted[i - 1]]) / (acc_range + 1e-10)

        # Cost distance
        cost_sorted = sorted(range(len(front)), key=lambda i: costs[i])
        cost_range = costs[cost_sorted[-1]] - costs[cost_sorted[0]]

        for i in range(1, len(front) - 1):
            idx = cost_sorted[i]
            distances[idx] += (costs[cost_sorted[i + 1]] -
                             costs[cost_sorted[i - 1]]) / (cost_range + 1e-10)

        return distances

    def mutate(self, config: Configuration) -> Configuration:
        """Apply random mutation to configuration."""
        def mutate_int(value: int, min_val: int, max_val: int) -> int:
            if np.random.random() < self.mutation_rate:
                delta = np.random.randint(-max_val // 10, max_val // 10 + 1)
                return np.clip(value + delta, min_val, max_val)
            return value

        def mutate_float(value: float, min_val: float, max_val: float) -> float:
            if np.random.random() < self.mutation_rate:
                delta = np.random.uniform(-0.1, 0.1)
                return np.clip(value + delta, min_val, max_val)
            return value

        def mutate_bool(value: bool) -> bool:
            if np.random.random() < self.mutation_rate:
                return not value
            return value

        return Configuration(
            model_size=mutate_int(config.model_size, 10, 1000),
            checkpoint_frequency=mutate_int(config.checkpoint_frequency, 1, 50),
            cache_size_mb=mutate_int(config.cache_size_mb, 64, 4096),
            batch_size=mutate_int(config.batch_size, 1, 64),
            compression_level=mutate_float(config.compression_level, 0.0, 1.0),
            temperature=mutate_float(config.temperature, 0.1, 2.0),
            use_federated=mutate_bool(config.use_federated),
            replication_factor=mutate_int(config.replication_factor, 1, 5)
        )

    def crossover(self, parent1: Configuration, parent2: Configuration) -> Configuration:
        """Single-point crossover between two configurations."""
        if np.random.random() > self.crossover_rate:
            return parent1

        # Random crossover point
        crossover_point = np.random.randint(0, 8)

        if crossover_point < 4:
            return Configuration(
                model_size=parent1.model_size if np.random.random() < 0.5 else parent2.model_size,
                checkpoint_frequency=parent1.checkpoint_frequency if np.random.random() < 0.5 else parent2.checkpoint_frequency,
                cache_size_mb=parent1.cache_size_mb if np.random.random() < 0.5 else parent2.cache_size_mb,
                batch_size=parent1.batch_size if np.random.random() < 0.5 else parent2.batch_size,
                compression_level=parent1.compression_level if np.random.random() < 0.5 else parent2.compression_level,
                temperature=parent1.temperature if np.random.random() < 0.5 else parent2.temperature,
                use_federated=parent1.use_federated if np.random.random() < 0.5 else parent2.use_federated,
                replication_factor=parent1.replication_factor if np.random.random() < 0.5 else parent2.replication_factor
            )
        else:
            return Configuration(
                model_size=parent2.model_size,
                checkpoint_frequency=parent2.checkpoint_frequency,
                cache_size_mb=parent2.cache_size_mb,
                batch_size=parent2.batch_size,
                compression_level=parent2.compression_level,
                temperature=parent2.temperature,
                use_federated=parent2.use_federated,
                replication_factor=parent2.replication_factor
            )

    def optimize(self, evaluator: AccuracyCostEvaluator) -> List[Configuration]:
        """Run NSGA-II optimization."""
        # Initialize random population
        population = []
        for _ in range(self.population_size):
            population.append(Configuration(
                model_size=np.random.randint(10, 1000),
                checkpoint_frequency=np.random.randint(1, 50),
                cache_size_mb=np.random.randint(64, 4096),
                batch_size=np.random.randint(1, 64),
                compression_level=np.random.uniform(0.0, 1.0),
                temperature=np.random.uniform(0.1, 2.0),
                use_federated=np.random.choice([True, False]),
                replication_factor=np.random.randint(1, 5)
            ))

        # Evolution
        for generation in range(self.generations):
            # Non-dominated sort
            fronts = self.fast_non_dominated_sort(population, evaluator)

            # Create offspring
            offspring = []
            while len(offspring) < self.population_size:
                # Tournament selection from first front
                parent1 = population[np.random.randint(0, len(fronts[0]))]
                parent2 = population[np.random.randint(0, len(fronts[0]))]

                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                offspring.append(child)

            # Merge and select
            population += offspring
            fronts = self.fast_non_dominated_sort(population, evaluator)

            # Fill next population
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend(front)
                else:
                    # Add most diverse from this front
                    distances = self.crowding_distance(front, evaluator)
                    sorted_by_distance = sorted(zip(front, distances),
                                              key=lambda x: x[1], reverse=True)
                    remaining = self.population_size - len(new_population)
                    new_population.extend([x[0] for x in sorted_by_distance[:remaining]])
                    break

            population = new_population[:self.population_size]

            if (generation + 1) % 10 == 0:
                print(f"Generation {generation + 1}/{self.generations}")

        # Return Pareto front
        fronts = self.fast_non_dominated_sort(population, evaluator)
        return fronts[0]


def analyze_pareto_front(pareto_front: List[Configuration],
                        evaluator: AccuracyCostEvaluator) -> Dict[str, Any]:
    """Analyze Pareto front and extract key insights."""
    # Evaluate all solutions
    results = []
    for config in pareto_front:
        results.append({
            'config': config,
            'accuracy': evaluator.estimate_accuracy(config),
            'cost': evaluator.estimate_hourly_cost(config)
        })

    # Sort by accuracy
    results.sort(key=lambda x: x['accuracy'])

    # Extract tiers
    n = len(results)
    tiers = {
        'budget': results[0],
        'standard': results[n // 3],
        'performance': results[2 * n // 3],
        'premium': results[-1]
    }

    # Statistics
    accuracies = [r['accuracy'] for r in results]
    costs = [r['cost'] for r in results]

    stats = {
        'accuracy_range': (min(accuracies), max(accuracies)),
        'cost_range': (min(costs), max(costs)),
        'pareto_size': len(pareto_front),
        'tiers': tiers
    }

    return stats


def plot_pareto_front(pareto_front: List[Configuration],
                     evaluator: AccuracyCostEvaluator,
                     save_path: str = None):
    """Plot Pareto frontier."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Evaluate all solutions
    accuracies = [evaluator.estimate_accuracy(c) for c in pareto_front]
    costs = [evaluator.estimate_hourly_cost(c) for c in pareto_front]

    # Sort by cost for plotting
    sorted_data = sorted(zip(costs, accuracies), key=lambda x: x[0])
    costs_sorted = [x[0] for x in sorted_data]
    accuracies_sorted = [x[1] for x in sorted_data]

    # Plot 1: Pareto frontier
    ax1.scatter(costs, accuracies, alpha=0.6, s=50)
    ax1.plot(costs_sorted, accuracies_sorted, 'b--', alpha=0.5, label='Pareto Front')
    ax1.set_xlabel('Hourly Cost (arbitrary units)')
    ax1.set_ylabel('Accuracy Score')
    ax1.set_title('Pareto Frontier: Accuracy vs Cost')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Plot 2: Configuration parameters
    model_sizes = [c.model_size for c in pareto_front]
    cache_sizes = [c.cache_size_mb for c in pareto_front]

    ax2.scatter(model_sizes, cache_sizes, c=accuracies, cmap='viridis', alpha=0.6, s=50)
    ax2.set_xlabel('Model Size (M parameters)')
    ax2.set_ylabel('Cache Size (MB)')
    ax2.set_title('Configuration Space (colored by accuracy)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(ax2.collections[0], ax=ax2, label='Accuracy')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()


def generate_tier_configs(pareto_front: List[Configuration],
                         evaluator: AccuracyCostEvaluator,
                         output_dir: str) -> Dict[str, Dict]:
    """Generate tiered configurations from Pareto front."""
    # Analyze front
    results = []
    for config in pareto_front:
        results.append({
            'config': config,
            'accuracy': evaluator.estimate_accuracy(config),
            'cost': evaluator.estimate_hourly_cost(config)
        })

    results.sort(key=lambda x: x['accuracy'])
    n = len(results)

    # Define tiers
    tiers = {
        'BUDGET': results[0],
        'STANDARD': results[n // 4],
        'PERFORMANCE': results[n // 2],
        'PREMIUM': results[3 * n // 4],
        'MAXIMUM': results[-1]
    }

    # Generate configs
    configs = {}
    for tier_name, tier_data in tiers.items():
        config = tier_data['config']
        configs[tier_name] = {
            'model_size': f"{config.model_size}M",
            'checkpoint_frequency': config.checkpoint_frequency,
            'cache_size': f"{config.cache_size_mb}MB",
            'batch_size': config.batch_size,
            'compression_level': round(config.compression_level, 2),
            'temperature': round(config.temperature, 2),
            'use_federated': config.use_federated,
            'replication_factor': config.replication_factor,
            'expected_accuracy': round(tier_data['accuracy'], 3),
            'expected_hourly_cost': round(tier_data['cost'], 3),
            'target': 'accuracy_cost_balance'
        }

    # Save to file
    output_path = Path(output_dir) / 'accuracy_cost_tiers.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)

    print(f"Generated {len(configs)} tiered configs")
    print(f"Saved to {output_path}")

    return configs


def main():
    """Main optimization pipeline."""
    print("=" * 60)
    print("Pareto Optimization: Accuracy vs Cost")
    print("=" * 60)

    # Setup
    evaluator = AccuracyCostEvaluator(tokens_per_request=1000, requests_per_hour=100)
    optimizer = NSGA2Optimizer(population_size=100, generations=50)

    # Run optimization
    print("\nRunning NSGA-II optimization...")
    pareto_front = optimizer.optimize(evaluator)
    print(f"\nFound {len(pareto_front)} Pareto-optimal configurations")

    # Analyze
    print("\nAnalyzing Pareto front...")
    stats = analyze_pareto_front(pareto_front, evaluator)
    print(f"\nAccuracy range: {stats['accuracy_range'][0]:.3f} - {stats['accuracy_range'][1]:.3f}")
    print(f"Cost range: {stats['cost_range'][0]:.3f} - {stats['cost_range'][1]:.3f}")

    # Plot
    output_dir = Path(__file__).parent.parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / 'pareto_accuracy_cost.png'
    plot_pareto_front(pareto_front, evaluator, str(plot_path))

    # Generate tier configs
    config_dir = Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
    tier_configs = generate_tier_configs(pareto_front, evaluator, str(config_dir))

    # Print tier summaries
    print("\n" + "=" * 60)
    print("Tier Summaries:")
    print("=" * 60)
    for tier, config in tier_configs.items():
        print(f"\n{tier}:")
        print(f"  Accuracy: {config['expected_accuracy']:.3f}")
        print(f"  Cost: {config['expected_hourly_cost']:.3f}/hour")
        print(f"  Model: {config['model_size']}, Cache: {config['cache_size']}")

    return pareto_front, tier_configs


if __name__ == '__main__':
    main()
