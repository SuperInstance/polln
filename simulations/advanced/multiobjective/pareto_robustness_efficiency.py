"""
Pareto Optimization: Robustness vs Efficiency Frontier

Finds optimal configurations balancing:
- Maximize robustness (availability, fault tolerance, recovery)
- Minimize cost (redundancy, monitoring, backup overhead)

Uses NSGA-II for multiobjective optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class RobustnessConfiguration:
    """Configuration for robustness/efficiency optimization."""
    replication_factor: int  # Number of replicas per agent
    checkpoint_interval_sec: int  # Checkpoint frequency
    backup_enabled: bool  # Enable backup system
    backup_frequency_hours: int  # Backup frequency
    monitoring_level: int  # 0-3, monitoring depth
    health_check_interval_sec: int  # Health check frequency
    circuit_breaker_threshold: int  # Failure threshold
    retry_policy: str  # 'none', 'exponential', 'fixed'
    max_retries: int  # Maximum retry attempts
    timeout_multiplier: float  # Timeout multiplier
    use_quorum: bool  # Require quorum for decisions
    disaster_recovery_enabled: bool  # Enable DR

    def to_dict(self) -> Dict[str, Any]:
        return {
            'replication_factor': self.replication_factor,
            'checkpoint_interval_sec': self.checkpoint_interval_sec,
            'backup_enabled': self.backup_enabled,
            'backup_frequency_hours': self.backup_frequency_hours,
            'monitoring_level': self.monitoring_level,
            'health_check_interval_sec': self.health_check_interval_sec,
            'circuit_breaker_threshold': self.circuit_breaker_threshold,
            'retry_policy': self.retry_policy,
            'max_retries': self.max_retries,
            'timeout_multiplier': self.timeout_multiplier,
            'use_quorum': self.use_quorum,
            'disaster_recovery_enabled': self.disaster_recovery_enabled
        }


class RobustnessEfficiencyEvaluator:
    """Evaluates robustness and efficiency for fault-tolerant configurations."""

    # Availability factors
    BASE_AVAILABILITY = 0.99  # 99% baseline
    PER_REPLICA_AVAILABILITY_BOOST = 0.005  # Each replica adds 0.5%
    QUORUM_AVAILABILITY_BOOST = 0.01  # Quorum adds 1%
    BACKUP_AVAILABILITY_BOOST = 0.02  # Backup adds 2%
    DR_AVAILABILITY_BOOST = 0.05  # DR adds 5%

    # Cost factors (multiplier)
    REPLICA_COST_MULTIPLIER = 1.2  # Each replica adds 20%
    CHECKPOINT_COST_MULTIPLIER = 1.05  # Checkpoints add 5% overhead
    BACKUP_COST_MULTIPLIER = 1.1  # Backup adds 10%
    MONITORING_COST_FACTOR = 0.02  # Each monitoring level adds 2%
    QUORUM_COST_MULTIPLIER = 1.3  # Quorum adds 30% overhead

    def __init__(self, base_cost: float = 1.0):
        self.base_cost = base_cost

    def estimate_availability(self, config: RobustnessConfiguration) -> float:
        """Estimate system availability (0-1)."""
        availability = self.BASE_AVAILABILITY

        # Replication boost (diminishing returns)
        availability += self.PER_REPLICA_AVAILABILITY_BOOST * np.log(config.replication_factor + 1)

        # Quorum boost
        if config.use_quorum and config.replication_factor >= 3:
            availability += self.QUORUM_AVAILABILITY_BOOST

        # Backup boost
        if config.backup_enabled:
            availability += self.BACKUP_AVAILABILITY_BOOST

        # Disaster recovery boost
        if config.disaster_recovery_enabled:
            availability += self.DR_AVAILABILITY_BOOST

        # Monitoring boost
        availability += 0.002 * config.monitoring_level

        # Circuit breaker boost
        availability += 0.001 * config.circuit_breaker_threshold

        # Retry boost
        if config.retry_policy != 'none':
            availability += 0.005 * config.max_retries

        # Health check boost
        availability += 0.0001 * (60 - config.health_check_interval_sec)

        # Frequent checkpoints improve recovery
        availability += 0.0005 * (60 - config.checkpoint_interval_sec)

        return min(0.9999, availability)

    def estimate_mttf_minutes(self, config: RobustnessConfiguration) -> float:
        """Estimate Mean Time To Failure in minutes."""
        base_mttf = 43200  # 30 days baseline

        # Replication increases MTTF
        mttf = base_mttf * np.sqrt(config.replication_factor)

        # Monitoring reduces failures
        mttf *= (1 + 0.1 * config.monitoring_level)

        # Health checks catch issues early
        mttf *= (1 + 0.05 * (60 / config.health_check_interval_sec))

        # Checkpoints reduce impact
        mttf *= (1 + 0.02 * (60 / config.checkpoint_interval_sec))

        return mttf

    def estimate_mttr_minutes(self, config: RobustnessConfiguration) -> float:
        """Estimate Mean Time To Recovery in minutes."""
        base_mttr = 30  # 30 minutes baseline

        # Replication reduces recovery time
        mttr = base_mttr / np.sqrt(config.replication_factor)

        # Frequent checkpoints speed recovery
        mttr *= (config.checkpoint_interval_sec / 60)

        # Backup speeds recovery
        if config.backup_enabled:
            mttr *= 0.5

        # DR speeds recovery but has lag
        if config.disaster_recovery_enabled:
            mttr *= 0.7

        # Retries add latency to recovery detection
        retry_penalty = {
            'none': 1.0,
            'fixed': 1.1,
            'exponential': 1.2
        }
        mttr *= retry_penalty.get(config.retry_policy, 1.0)

        return max(1, mttr)

    def estimate_cost_multiplier(self, config: RobustnessConfiguration) -> float:
        """Estimate cost multiplier relative to base."""
        multiplier = 1.0

        # Replication cost
        multiplier *= self.REPLICA_COST_MULTIPLIER ** (config.replication_factor - 1)

        # Checkpoint cost
        checkpoint_overhead = (60 / config.checkpoint_interval_sec) * 0.01
        multiplier *= (1 + checkpoint_overhead)

        # Backup cost
        if config.backup_enabled:
            multiplier *= self.BACKUP_COST_MULTIPLIER

        # Monitoring cost
        multiplier *= (1 + self.MONITORING_COST_FACTOR * config.monitoring_level)

        # Health check cost
        health_check_overhead = (60 / config.health_check_interval_sec) * 0.005
        multiplier *= (1 + health_check_overhead)

        # Quorum cost
        if config.use_quorum:
            multiplier *= self.QUORUM_COST_MULTIPLIER

        # Retry cost
        if config.retry_policy != 'none':
            multiplier *= (1 + 0.01 * config.max_retries)

        # Timeout multiplier increases resource usage
        multiplier *= config.timeout_multiplier

        # Disaster recovery cost
        if config.disaster_recovery_enabled:
            multiplier *= 1.15

        return multiplier

    def estimate_robustness_score(self, config: RobustnessConfiguration) -> float:
        """Composite robustness score (0-1)."""
        availability = self.estimate_availability(config)
        mttf = self.estimate_mttf_minutes(config)
        mttr = self.estimate_mttr_minutes(config)

        # Normalize: availability (weight 0.6), MTTF (weight 0.2), 1/MTTR (weight 0.2)
        mttf_normalized = min(1.0, mttf / 43200)  # Normalize to 30 days
        mttr_normalized = min(1.0, 30 / mttr)  # Inverse, normalize to 30 min

        robustness = 0.6 * availability + 0.2 * mttf_normalized + 0.2 * mttr_normalized
        return robustness


class NSGA2Optimizer:
    """NSGA-II optimizer for robustness/efficiency."""

    def __init__(self, population_size: int = 100, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.15
        self.crossover_rate = 0.8

    def dominates(self, obj1: Tuple[float, float], obj2: Tuple[float, float]) -> bool:
        """Check if obj1 dominates obj2 (max robustness, min cost)."""
        robust1, cost1 = obj1
        robust2, cost2 = obj2
        return (robust1 >= robust2 and cost1 <= cost2) and (robust1 > robust2 or cost1 < cost2)

    def fast_non_dominated_sort(self, population: List[RobustnessConfiguration],
                                evaluator: RobustnessEfficiencyEvaluator) -> List[List[RobustnessConfiguration]]:
        """Sort population into Pareto fronts."""
        objectives = [(evaluator.estimate_robustness_score(ind),
                      evaluator.estimate_cost_multiplier(ind))
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

    def crowding_distance(self, front: List[RobustnessConfiguration],
                         evaluator: RobustnessEfficiencyEvaluator) -> List[float]:
        """Calculate crowding distance."""
        if len(front) <= 2:
            return [float('inf')] * len(front)

        robustness = [evaluator.estimate_robustness_score(ind) for ind in front]
        costs = [evaluator.estimate_cost_multiplier(ind) for ind in front]

        distances = [0.0] * len(front)

        # Robustness distance
        robust_sorted = sorted(range(len(front)), key=lambda i: robustness[i])
        robust_range = robustness[robust_sorted[-1]] - robustness[robust_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = robust_sorted[i]
            distances[idx] += (robustness[robust_sorted[i + 1]] -
                             robustness[robust_sorted[i - 1]]) / robust_range

        # Cost distance
        cost_sorted = sorted(range(len(front)), key=lambda i: costs[i])
        cost_range = costs[cost_sorted[-1]] - costs[cost_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = cost_sorted[i]
            distances[idx] += (costs[cost_sorted[i + 1]] -
                             costs[cost_sorted[i - 1]]) / cost_range

        return distances

    def mutate(self, config: RobustnessConfiguration) -> RobustnessConfiguration:
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

        return RobustnessConfiguration(
            replication_factor=mutate_int(config.replication_factor, 1, 10),
            checkpoint_interval_sec=mutate_int(config.checkpoint_interval_sec, 10, 300),
            backup_enabled=mutate_bool(config.backup_enabled),
            backup_frequency_hours=mutate_int(config.backup_frequency_hours, 1, 24),
            monitoring_level=mutate_int(config.monitoring_level, 0, 3),
            health_check_interval_sec=mutate_int(config.health_check_interval_sec, 10, 300),
            circuit_breaker_threshold=mutate_int(config.circuit_breaker_threshold, 1, 20),
            retry_policy=mutate_choice(config.retry_policy, ['none', 'exponential', 'fixed']),
            max_retries=mutate_int(config.max_retries, 0, 10),
            timeout_multiplier=mutate_float(config.timeout_multiplier, 1.0, 3.0),
            use_quorum=mutate_bool(config.use_quorum),
            disaster_recovery_enabled=mutate_bool(config.disaster_recovery_enabled)
        )

    def crossover(self, parent1: RobustnessConfiguration, parent2: RobustnessConfiguration) -> RobustnessConfiguration:
        """Crossover between parents."""
        if np.random.random() > self.crossover_rate:
            return parent1

        return RobustnessConfiguration(
            replication_factor=parent1.replication_factor if np.random.random() < 0.5 else parent2.replication_factor,
            checkpoint_interval_sec=parent1.checkpoint_interval_sec if np.random.random() < 0.5 else parent2.checkpoint_interval_sec,
            backup_enabled=parent1.backup_enabled if np.random.random() < 0.5 else parent2.backup_enabled,
            backup_frequency_hours=parent1.backup_frequency_hours if np.random.random() < 0.5 else parent2.backup_frequency_hours,
            monitoring_level=parent1.monitoring_level if np.random.random() < 0.5 else parent2.monitoring_level,
            health_check_interval_sec=parent1.health_check_interval_sec if np.random.random() < 0.5 else parent2.health_check_interval_sec,
            circuit_breaker_threshold=parent1.circuit_breaker_threshold if np.random.random() < 0.5 else parent2.circuit_breaker_threshold,
            retry_policy=parent1.retry_policy if np.random.random() < 0.5 else parent2.retry_policy,
            max_retries=parent1.max_retries if np.random.random() < 0.5 else parent2.max_retries,
            timeout_multiplier=parent1.timeout_multiplier if np.random.random() < 0.5 else parent2.timeout_multiplier,
            use_quorum=parent1.use_quorum if np.random.random() < 0.5 else parent2.use_quorum,
            disaster_recovery_enabled=parent1.disaster_recovery_enabled if np.random.random() < 0.5 else parent2.disaster_recovery_enabled
        )

    def optimize(self, evaluator: RobustnessEfficiencyEvaluator) -> List[RobustnessConfiguration]:
        """Run NSGA-II optimization."""
        population = []
        for _ in range(self.population_size):
            population.append(RobustnessConfiguration(
                replication_factor=np.random.randint(1, 10),
                checkpoint_interval_sec=np.random.randint(10, 300),
                backup_enabled=np.random.choice([True, False]),
                backup_frequency_hours=np.random.randint(1, 24),
                monitoring_level=np.random.randint(0, 4),
                health_check_interval_sec=np.random.randint(10, 300),
                circuit_breaker_threshold=np.random.randint(1, 20),
                retry_policy=np.random.choice(['none', 'exponential', 'fixed']),
                max_retries=np.random.randint(0, 10),
                timeout_multiplier=np.random.uniform(1.0, 3.0),
                use_quorum=np.random.choice([True, False]),
                disaster_recovery_enabled=np.random.choice([True, False])
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


def plot_robustness_efficiency_frontier(pareto_front: List[RobustnessConfiguration],
                                       evaluator: RobustnessEfficiencyEvaluator,
                                       save_path: str = None):
    """Plot robustness vs efficiency frontier."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    robustness_scores = [evaluator.estimate_robustness_score(c) for c in pareto_front]
    cost_multipliers = [evaluator.estimate_cost_multiplier(c) for c in pareto_front]
    availabilities = [evaluator.estimate_availability(c) for c in pareto_front]
    mttfs = [evaluator.estimate_mttf_minutes(c) for c in pareto_front]

    # Plot 1: Robustness vs Cost
    scatter = ax1.scatter(cost_multipliers, robustness_scores, c=availabilities, cmap='RdYlGn', s=50, alpha=0.6)
    ax1.set_xlabel('Cost Multiplier')
    ax1.set_ylabel('Robustness Score')
    ax1.set_title('Pareto Frontier: Robustness vs Cost')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Availability')

    # Plot 2: Replication vs Monitoring
    replications = [c.replication_factor for c in pareto_front]
    monitoring_levels = [c.monitoring_level for c in pareto_front]
    ax2.scatter(replications, monitoring_levels, c=robustness_scores, cmap='viridis', s=50, alpha=0.6)
    ax2.set_xlabel('Replication Factor')
    ax2.set_ylabel('Monitoring Level')
    ax2.set_title('Configuration Space (colored by robustness)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(ax2.collections[0], ax=ax2, label='Robustness')

    # Plot 3: Availability tiers
    availability_tiers = {
        'Basic (<99%)': [a for a in availabilities if a < 0.99],
        'High (99-99.9%)': [a for a in availabilities if 0.99 <= a < 0.999],
        'Critical (>99.9%)': [a for a in availabilities if a >= 0.999]
    }
    ax3.bar(availability_tiers.keys(), [len(v) for v in availability_tiers.values()])
    ax3.set_ylabel('Number of Configurations')
    ax3.set_title('Configurations by Availability Tier')
    ax3.tick_params(axis='x', rotation=45)

    # Plot 4: MTTF vs Cost
    ax4.scatter(cost_multipliers, mttfs, c=availabilities, cmap='coolwarm', s=50, alpha=0.6)
    ax4.set_xlabel('Cost Multiplier')
    ax4.set_ylabel('MTTF (minutes)')
    ax4.set_title('MTTF vs Cost (colored by availability)')
    ax4.grid(True, alpha=0.3)
    ax4.set_yscale('log')
    plt.colorbar(ax4.collections[0], ax=ax4, label='Availability')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()


def generate_robustness_tier_configs(pareto_front: List[RobustnessConfiguration],
                                    evaluator: RobustnessEfficiencyEvaluator,
                                    output_dir: str) -> Dict[str, Dict]:
    """Generate configurations for different robustness tiers."""
    results = []
    for config in pareto_front:
        results.append({
            'config': config,
            'robustness': evaluator.estimate_robustness_score(config),
            'availability': evaluator.estimate_availability(config),
            'cost_multiplier': evaluator.estimate_cost_multiplier(config),
            'mttf_minutes': evaluator.estimate_mttf_minutes(config),
            'mttr_minutes': evaluator.estimate_mttr_minutes(config)
        })

    # Define availability tiers
    tiers = {
        'BASIC': None,      # 99% availability
        'HIGH': None,       # 99.9% availability
        'CRITICAL': None,   # 99.99% availability
        'EXTREME': None     # Maximum
    }

    # Find best cost-effective config in each tier
    for tier, min_availability in [
        ('BASIC', 0.99),
        ('HIGH', 0.999),
        ('CRITICAL', 0.9995),
        ('EXTREME', 0.9999)
    ]:
        tier_configs = [r for r in results if r['availability'] >= min_availability]
        if tier_configs:
            # Pick lowest cost
            best = min(tier_configs, key=lambda x: x['cost_multiplier'])
            tiers[tier] = best

    # Generate configs
    configs = {}
    for tier_name, tier_data in tiers.items():
        if tier_data is None:
            continue

        config = tier_data['config']
        configs[tier_name] = {
            'replication_factor': config.replication_factor,
            'checkpoint_interval_sec': config.checkpoint_interval_sec,
            'backup_enabled': config.backup_enabled,
            'backup_frequency_hours': config.backup_frequency_hours,
            'monitoring_level': config.monitoring_level,
            'health_check_interval_sec': config.health_check_interval_sec,
            'circuit_breaker_threshold': config.circuit_breaker_threshold,
            'retry_policy': config.retry_policy,
            'max_retries': config.max_retries,
            'timeout_multiplier': round(config.timeout_multiplier, 2),
            'use_quorum': config.use_quorum,
            'disaster_recovery_enabled': config.disaster_recovery_enabled,
            'expected_availability': f"{tier_data['availability'] * 100:.4f}%",
            'expected_mttf_hours': round(tier_data['mttf_minutes'] / 60, 1),
            'expected_mttr_minutes': round(tier_data['mttr_minutes'], 1),
            'expected_cost_multiplier': round(tier_data['cost_multiplier'], 2),
            'target': 'robustness_efficiency_balance'
        }

    # Save
    output_path = Path(output_dir) / 'robustness_efficiency_tiers.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)

    print(f"Generated {len(configs)} robustness tier configs")
    print(f"Saved to {output_path}")

    return configs


def main():
    """Main optimization pipeline."""
    print("=" * 60)
    print("Pareto Optimization: Robustness vs Efficiency")
    print("=" * 60)

    evaluator = RobustnessEfficiencyEvaluator(base_cost=1.0)
    optimizer = NSGA2Optimizer(population_size=100, generations=50)

    print("\nRunning NSGA-II optimization...")
    pareto_front = optimizer.optimize(evaluator)
    print(f"\nFound {len(pareto_front)} Pareto-optimal configurations")

    # Statistics
    robustness_scores = [evaluator.estimate_robustness_score(c) for c in pareto_front]
    cost_multipliers = [evaluator.estimate_cost_multiplier(c) for c in pareto_front]

    print(f"\nRobustness range: {min(robustness_scores):.3f} - {max(robustness_scores):.3f}")
    print(f"Cost range: {min(cost_multipliers):.2f}x - {max(cost_multipliers):.2f}x")

    # Plot
    output_dir = Path(__file__).parent.parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / 'pareto_robustness_efficiency.png'
    plot_robustness_efficiency_frontier(pareto_front, evaluator, str(plot_path))

    # Generate tier configs
    config_dir = Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
    tier_configs = generate_robustness_tier_configs(pareto_front, evaluator, str(config_dir))

    # Print summaries
    print("\n" + "=" * 60)
    print("Robustness Tier Summaries:")
    print("=" * 60)
    for tier, config in tier_configs.items():
        print(f"\n{tier}:")
        print(f"  Availability: {config['expected_availability']}")
        print(f"  Cost: {config['expected_cost_multiplier']}x base")
        print(f"  MTTF: {config['expected_mttf_hours']} hours")
        print(f"  Replication: {config['replication_factor']}x")

    return pareto_front, tier_configs


if __name__ == '__main__':
    main()
