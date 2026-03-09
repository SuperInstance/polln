"""
Pareto Optimization: Scalability vs Complexity Frontier

Finds optimal configurations balancing:
- Maximize scalability (throughput, agent capacity, growth)
- Minimize complexity (coordination overhead, management cost)

Uses NSGA-II for multiobjective optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ScalabilityConfiguration:
    """Configuration for scalability/complexity optimization."""
    colony_size: int  # Number of agents
    topology_depth: int  # Depth of agent hierarchy
    agent_types: int  # Number of specialized agent types
    decentralization_level: float  # 0-1, how decentralized
    horizontal_scaling: bool  # Enable horizontal scaling
    auto_scaling: bool  # Enable auto-scaling
    load_balancing_strategy: str  # 'round_robin', 'least_loaded', 'hash'
    cache_sharding: bool  # Enable cache sharding
    federation_enabled: bool  # Enable federated learning
    meta_tile_ratio: float  # Ratio of META tiles to specialized
    communication_pattern: str  # 'star', 'mesh', 'hierarchical'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'colony_size': self.colony_size,
            'topology_depth': self.topology_depth,
            'agent_types': self.agent_types,
            'decentralization_level': self.decentralization_level,
            'horizontal_scaling': self.horizontal_scaling,
            'auto_scaling': self.auto_scaling,
            'load_balancing_strategy': self.load_balancing_strategy,
            'cache_sharding': self.cache_sharding,
            'federation_enabled': self.federation_enabled,
            'meta_tile_ratio': self.meta_tile_ratio,
            'communication_pattern': self.communication_pattern
        }


class ScalabilityComplexityEvaluator:
    """Evaluates scalability and complexity for colony configurations."""

    # Throughput factors
    BASE_THROUGHPUT = 100  # Base requests per second
    PER_AGENT_THROUGHPUT = 10  # Each agent adds 10 req/s
    HORIZONTAL_SCALING_MULTIPLIER = 1.5  # Horizontal scaling boost
    META_TILE_EFFICIENCY = 1.2  # META tiles are more flexible

    # Complexity factors
    COORDINATION_OVERHEAD_PER_AGENT = 0.01
    TOPOLOGY_OVERHEAD_PER_LEVEL = 0.05
    TYPE_OVERHEAD_PER_TYPE = 0.02
    FEDERATION_OVERHEAD = 0.1
    SHARDING_OVERHEAD = 0.08

    def estimate_throughput(self, config: ScalabilityConfiguration) -> float:
        """Estimate system throughput (requests/second)."""
        throughput = self.BASE_THROUGHPUT

        # Agent contribution (diminishing returns after 100 agents)
        agent_efficiency = 1 - np.exp(-config.colony_size / 100)
        throughput += self.PER_AGENT_THROUGHPUT * config.colony_size * agent_efficiency

        # Horizontal scaling boost
        if config.horizontal_scaling:
            throughput *= self.HORIZONTAL_SCALING_MULTIPLIER

        # META tiles improve throughput
        throughput *= (1 + 0.1 * config.meta_tile_ratio)

        # Cache sharding improves throughput
        if config.cache_sharding:
            throughput *= 1.15

        # Load balancing efficiency
        lb_efficiency = {
            'round_robin': 1.0,
            'least_loaded': 1.15,
            'hash': 1.1
        }
        throughput *= lb_efficiency.get(config.load_balancing_strategy, 1.0)

        # Communication pattern efficiency
        comm_efficiency = {
            'star': 0.8,
            'mesh': 1.2,
            'hierarchical': 1.0
        }
        throughput *= comm_efficiency.get(config.communication_pattern, 1.0)

        # Decentralization improves throughput up to a point
        decentralization_boost = 1 + 0.2 * config.decentralization_level * (1 - config.decentralization_level)
        throughput *= decentralization_boost

        return throughput

    def estimate_max_colony_size(self, config: ScalabilityConfiguration) -> int:
        """Estimate maximum sustainable colony size."""
        base_max = 1000

        # Topology depth limits scalability
        depth_penalty = 0.8 ** config.topology_depth
        max_size = base_max * depth_penalty

        # Horizontal scaling increases max size
        if config.horizontal_scaling:
            max_size *= 2

        # Auto-scaling increases max size
        if config.auto_scaling:
            max_size *= 1.5

        # Federation increases max size
        if config.federation_enabled:
            max_size *= 1.3

        # Decentralization increases max size
        max_size *= (1 + config.decentralization_level)

        return int(max_size)

    def estimate_complexity_score(self, config: ScalabilityConfiguration) -> float:
        """Estimate complexity score (0-1, higher is more complex)."""
        complexity = 0.0

        # Colony size complexity (logarithmic)
        complexity += 0.2 * np.log(config.colony_size + 1) / np.log(1000)

        # Topology depth complexity
        complexity += 0.15 * config.topology_depth

        # Agent type complexity
        complexity += 0.05 * config.agent_types

        # Decentralization complexity (more decentralized = more complex)
        complexity += 0.1 * config.decentralization_level

        # Horizontal scaling complexity
        if config.horizontal_scaling:
            complexity += 0.15

        # Auto-scaling complexity
        if config.auto_scaling:
            complexity += 0.2

        # Cache sharding complexity
        if config.cache_sharding:
            complexity += 0.1

        # Federation complexity
        if config.federation_enabled:
            complexity += self.FEDERATION_OVERHEAD

        # META tile ratio complexity
        complexity += 0.05 * config.meta_tile_ratio

        # Communication pattern complexity
        comm_complexity = {
            'star': 0.05,
            'hierarchical': 0.15,
            'mesh': 0.25
        }
        complexity += comm_complexity.get(config.communication_pattern, 0.1)

        return min(1.0, complexity)

    def estimate_coordination_overhead(self, config: ScalabilityConfiguration) -> float:
        """Estimate coordination overhead (0-1, fraction of time)."""
        overhead = 0.0

        # Per-agent coordination
        overhead += self.COORDINATION_OVERHEAD_PER_AGENT * config.colony_size

        # Topology overhead
        overhead += self.TOPOLOGY_OVERHEAD_PER_LEVEL * config.topology_depth

        # Type overhead
        overhead += self.TYPE_OVERHEAD_PER_TYPE * config.agent_types

        # Decentralization increases coordination overhead
        overhead *= (1 + 0.5 * config.decentralization_level)

        # Communication pattern overhead
        comm_overhead = {
            'star': 0.05,
            'hierarchical': 0.1,
            'mesh': 0.2
        }
        overhead += comm_overhead.get(config.communication_pattern, 0.1)

        return min(0.5, overhead)  # Cap at 50% overhead

    def estimate_management_cost(self, config: ScalabilityConfiguration) -> float:
        """Estimate management cost (arbitrary units)."""
        base_cost = 1.0

        # Colony size cost
        cost = base_cost * (1 + config.colony_size / 100)

        # Topology cost
        cost *= (1 + 0.1 * config.topology_depth)

        # Agent type cost
        cost *= (1 + 0.05 * config.agent_types)

        # Auto-scaling adds management overhead
        if config.auto_scaling:
            cost *= 1.2

        # Federation adds management overhead
        if config.federation_enabled:
            cost *= 1.15

        # Decentralization adds management overhead
        cost *= (1 + 0.1 * config.decentralization_level)

        return cost


class NSGA2Optimizer:
    """NSGA-II optimizer for scalability/complexity."""

    def __init__(self, population_size: int = 100, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.15
        self.crossover_rate = 0.8

    def dominates(self, obj1: Tuple[float, float], obj2: Tuple[float, float]) -> bool:
        """Check if obj1 dominates obj2 (max throughput, min complexity)."""
        throughput1, complexity1 = obj1
        throughput2, complexity2 = obj2
        return (throughput1 >= throughput2 and complexity1 <= complexity2) and \
               (throughput1 > throughput2 or complexity1 < complexity2)

    def fast_non_dominated_sort(self, population: List[ScalabilityConfiguration],
                                evaluator: ScalabilityComplexityEvaluator) -> List[List[ScalabilityConfiguration]]:
        """Sort population into Pareto fronts."""
        objectives = [(evaluator.estimate_throughput(ind),
                      evaluator.estimate_complexity_score(ind))
                     for ind in population]

        domination_count = [0] * len(population)
        dominated_solutions = [[] for _ in range(len(population))]

        for i in range(len(population)):
            for j in range(len(population)):
                if i != j:
                    if self.dominates(objectives[i], objectives[j]):
                        dominated_solutions[i].append(j)
                    elif self.dominates(objectives[j], objectives[i]):
                        domination_count[i] += 1

        fronts = []
        current_front = [i for i in range(len(population)) if domination_count[i] == 0]

        fronts.append([population[i] for i in current_front])

        while current_front:
            next_front = []
            for i in current_front:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)

            if next_front:
                fronts.append([population[i] for i in next_front])
            current_front = next_front

        return fronts

    def crowding_distance(self, front: List[ScalabilityConfiguration],
                         evaluator: ScalabilityComplexityEvaluator) -> List[float]:
        """Calculate crowding distance."""
        if len(front) <= 2:
            return [float('inf')] * len(front)

        throughputs = [evaluator.estimate_throughput(ind) for ind in front]
        complexities = [evaluator.estimate_complexity_score(ind) for ind in front]

        distances = [0.0] * len(front)

        # Throughput distance
        throughput_sorted = sorted(range(len(front)), key=lambda i: throughputs[i])
        throughput_range = throughputs[throughput_sorted[-1]] - throughputs[throughput_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = throughput_sorted[i]
            distances[idx] += (throughputs[throughput_sorted[i + 1]] -
                             throughputs[throughput_sorted[i - 1]]) / throughput_range

        # Complexity distance
        complexity_sorted = sorted(range(len(front)), key=lambda i: complexities[i])
        complexity_range = complexities[complexity_sorted[-1]] - complexities[complexity_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = complexity_sorted[i]
            distances[idx] += (complexities[complexity_sorted[i + 1]] -
                             complexities[complexity_sorted[i - 1]]) / complexity_range

        return distances

    def mutate(self, config: ScalabilityConfiguration) -> ScalabilityConfiguration:
        """Apply mutation."""
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

        def mutate_choice(value: str, choices: List[str]) -> str:
            if np.random.random() < self.mutation_rate:
                return np.random.choice(choices)
            return value

        return ScalabilityConfiguration(
            colony_size=mutate_int(config.colony_size, 10, 1000),
            topology_depth=mutate_int(config.topology_depth, 1, 10),
            agent_types=mutate_int(config.agent_types, 1, 20),
            decentralization_level=mutate_float(config.decentralization_level, 0.0, 1.0),
            horizontal_scaling=mutate_bool(config.horizontal_scaling),
            auto_scaling=mutate_bool(config.auto_scaling),
            load_balancing_strategy=mutate_choice(config.load_balancing_strategy,
                                                  ['round_robin', 'least_loaded', 'hash']),
            cache_sharding=mutate_bool(config.cache_sharding),
            federation_enabled=mutate_bool(config.federation_enabled),
            meta_tile_ratio=mutate_float(config.meta_tile_ratio, 0.0, 1.0),
            communication_pattern=mutate_choice(config.communication_pattern,
                                               ['star', 'mesh', 'hierarchical'])
        )

    def crossover(self, parent1: ScalabilityConfiguration, parent2: ScalabilityConfiguration) -> ScalabilityConfiguration:
        """Crossover between parents."""
        if np.random.random() > self.crossover_rate:
            return parent1

        return ScalabilityConfiguration(
            colony_size=parent1.colony_size if np.random.random() < 0.5 else parent2.colony_size,
            topology_depth=parent1.topology_depth if np.random.random() < 0.5 else parent2.topology_depth,
            agent_types=parent1.agent_types if np.random.random() < 0.5 else parent2.agent_types,
            decentralization_level=parent1.decentralization_level if np.random.random() < 0.5 else parent2.decentralization_level,
            horizontal_scaling=parent1.horizontal_scaling if np.random.random() < 0.5 else parent2.horizontal_scaling,
            auto_scaling=parent1.auto_scaling if np.random.random() < 0.5 else parent2.auto_scaling,
            load_balancing_strategy=parent1.load_balancing_strategy if np.random.random() < 0.5 else parent2.load_balancing_strategy,
            cache_sharding=parent1.cache_sharding if np.random.random() < 0.5 else parent2.cache_sharding,
            federation_enabled=parent1.federation_enabled if np.random.random() < 0.5 else parent2.federation_enabled,
            meta_tile_ratio=parent1.meta_tile_ratio if np.random.random() < 0.5 else parent2.meta_tile_ratio,
            communication_pattern=parent1.communication_pattern if np.random.random() < 0.5 else parent2.communication_pattern
        )

    def optimize(self, evaluator: ScalabilityComplexityEvaluator) -> List[ScalabilityConfiguration]:
        """Run NSGA-II optimization."""
        population = []
        for _ in range(self.population_size):
            population.append(ScalabilityConfiguration(
                colony_size=np.random.randint(10, 1000),
                topology_depth=np.random.randint(1, 10),
                agent_types=np.random.randint(1, 20),
                decentralization_level=np.random.uniform(0.0, 1.0),
                horizontal_scaling=np.random.choice([True, False]),
                auto_scaling=np.random.choice([True, False]),
                load_balancing_strategy=np.random.choice(['round_robin', 'least_loaded', 'hash']),
                cache_sharding=np.random.choice([True, False]),
                federation_enabled=np.random.choice([True, False]),
                meta_tile_ratio=np.random.uniform(0.0, 1.0),
                communication_pattern=np.random.choice(['star', 'mesh', 'hierarchical'])
            ))

        for generation in range(self.generations):
            fronts = self.fast_non_dominated_sort(population, evaluator)

            offspring = []
            while len(offspring) < self.population_size:
                parent1 = population[np.random.randint(0, len(fronts[0]))]
                parent2 = population[np.random.randint(0, len(fronts[0]))]
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                offspring.append(child)

            population += offspring
            fronts = self.fast_non_dominated_sort(population, evaluator)

            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend(front)
                else:
                    distances = self.crowding_distance(front, evaluator)
                    sorted_by_distance = sorted(zip(front, distances),
                                              key=lambda x: x[1], reverse=True)
                    remaining = self.population_size - len(new_population)
                    new_population.extend([x[0] for x in sorted_by_distance[:remaining]])
                    break

            population = new_population[:self.population_size]

            if (generation + 1) % 10 == 0:
                print(f"Generation {generation + 1}/{self.generations}")

        fronts = self.fast_non_dominated_sort(population, evaluator)
        return fronts[0]


def plot_scalability_complexity_frontier(pareto_front: List[ScalabilityConfiguration],
                                        evaluator: ScalabilityComplexityEvaluator,
                                        save_path: str = None):
    """Plot scalability vs complexity frontier."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    throughputs = [evaluator.estimate_throughput(c) for c in pareto_front]
    complexities = [evaluator.estimate_complexity_score(c) for c in pareto_front]
    max_sizes = [evaluator.estimate_max_colony_size(c) for c in pareto_front]
    overheads = [evaluator.estimate_coordination_overhead(c) for c in pareto_front]

    # Plot 1: Throughput vs Complexity
    scatter = ax1.scatter(complexities, throughputs, c=max_sizes, cmap='viridis', s=50, alpha=0.6)
    ax1.set_xlabel('Complexity Score')
    ax1.set_ylabel('Throughput (req/s)')
    ax1.set_title('Pareto Frontier: Throughput vs Complexity')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Max Colony Size')

    # Plot 2: Colony Size vs Topology Depth
    colony_sizes = [c.colony_size for c in pareto_front]
    topologies = [c.topology_depth for c in pareto_front]
    ax2.scatter(colony_sizes, topologies, c=throughputs, cmap='RdYlGn', s=50, alpha=0.6)
    ax2.set_xlabel('Colony Size')
    ax2.set_ylabel('Topology Depth')
    ax2.set_title('Configuration Space (colored by throughput)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(ax2.collections[0], ax=ax2, label='Throughput')

    # Plot 3: Size tiers
    size_tiers = {
        'Small (<100)': [s for s in colony_sizes if s < 100],
        'Medium (100-500)': [s for s in colony_sizes if 100 <= s < 500],
        'Large (500-1000)': [s for s in colony_sizes if 500 <= s < 1000],
        'X-Large (>1000)': [s for s in colony_sizes if s >= 1000]
    }
    ax3.bar(size_tiers.keys(), [len(v) for v in size_tiers.values()])
    ax3.set_ylabel('Number of Configurations')
    ax3.set_title('Configurations by Colony Size Tier')
    ax3.tick_params(axis='x', rotation=45)

    # Plot 4: Coordination Overhead vs Throughput
    ax4.scatter(overheads, throughputs, c=complexities, cmap='coolwarm', s=50, alpha=0.6)
    ax4.set_xlabel('Coordination Overhead')
    ax4.set_ylabel('Throughput (req/s)')
    ax4.set_title('Overhead vs Throughput (colored by complexity)')
    ax4.grid(True, alpha=0.3)
    plt.colorbar(ax4.collections[0], ax=ax4, label='Complexity')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()


def generate_scalability_tier_configs(pareto_front: List[ScalabilityConfiguration],
                                     evaluator: ScalabilityComplexityEvaluator,
                                     output_dir: str) -> Dict[str, Dict]:
    """Generate configurations for different scalability tiers."""
    results = []
    for config in pareto_front:
        results.append({
            'config': config,
            'throughput': evaluator.estimate_throughput(config),
            'complexity': evaluator.estimate_complexity_score(config),
            'max_colony_size': evaluator.estimate_max_colony_size(config),
            'coordination_overhead': evaluator.estimate_coordination_overhead(config)
        })

    # Define size tiers
    tiers = {
        'SMALL': None,
        'MEDIUM': None,
        'LARGE': None,
        'XLARGE': None
    }

    # Find best config in each tier
    for tier, (min_size, max_size) in [
        ('SMALL', (0, 100)),
        ('MEDIUM', (100, 500)),
        ('LARGE', (500, 1000)),
        ('XLARGE', (1000, float('inf')))
    ]:
        tier_configs = [r for r in results if min_size <= r['config'].colony_size < max_size]
        if tier_configs:
            # Pick best throughput/complexity ratio
            best = max(tier_configs, key=lambda x: x['throughput'] / (x['complexity'] + 0.01))
            tiers[tier] = best

    # Generate configs
    configs = {}
    for tier_name, tier_data in tiers.items():
        if tier_data is None:
            continue

        config = tier_data['config']
        configs[tier_name] = {
            'colony_size': config.colony_size,
            'topology_depth': config.topology_depth,
            'agent_types': config.agent_types,
            'decentralization_level': round(config.decentralization_level, 2),
            'horizontal_scaling': config.horizontal_scaling,
            'auto_scaling': config.auto_scaling,
            'load_balancing_strategy': config.load_balancing_strategy,
            'cache_sharding': config.cache_sharding,
            'federation_enabled': config.federation_enabled,
            'meta_tile_ratio': round(config.meta_tile_ratio, 2),
            'communication_pattern': config.communication_pattern,
            'expected_throughput': round(tier_data['throughput'], 1),
            'expected_complexity': round(tier_data['complexity'], 3),
            'max_colony_size': tier_data['max_colony_size'],
            'coordination_overhead': round(tier_data['coordination_overhead'], 3),
            'target': 'scalability_complexity_balance'
        }

    # Save
    output_path = Path(output_dir) / 'scalability_complexity_tiers.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)

    print(f"Generated {len(configs)} scalability tier configs")
    print(f"Saved to {output_path}")

    return configs


def main():
    """Main optimization pipeline."""
    print("=" * 60)
    print("Pareto Optimization: Scalability vs Complexity")
    print("=" * 60)

    evaluator = ScalabilityComplexityEvaluator()
    optimizer = NSGA2Optimizer(population_size=100, generations=50)

    print("\nRunning NSGA-II optimization...")
    pareto_front = optimizer.optimize(evaluator)
    print(f"\nFound {len(pareto_front)} Pareto-optimal configurations")

    # Statistics
    throughputs = [evaluator.estimate_throughput(c) for c in pareto_front]
    complexities = [evaluator.estimate_complexity_score(c) for c in pareto_front]

    print(f"\nThroughput range: {min(throughputs):.1f} - {max(throughputs):.1f} req/s")
    print(f"Complexity range: {min(complexities):.3f} - {max(complexities):.3f}")

    # Plot
    output_dir = Path(__file__).parent.parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / 'pareto_scalability_complexity.png'
    plot_scalability_complexity_frontier(pareto_front, evaluator, str(plot_path))

    # Generate tier configs
    config_dir = Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
    tier_configs = generate_scalability_tier_configs(pareto_front, evaluator, str(config_dir))

    # Print summaries
    print("\n" + "=" * 60)
    print("Scalability Tier Summaries:")
    print("=" * 60)
    for tier, config in tier_configs.items():
        print(f"\n{tier}:")
        print(f"  Throughput: {config['expected_throughput']:.1f} req/s")
        print(f"  Complexity: {config['expected_complexity']:.3f}")
        print(f"  Colony Size: {config['colony_size']}")
        print(f"  Topology: {config['topology_depth']} levels")

    return pareto_front, tier_configs


if __name__ == '__main__':
    main()
