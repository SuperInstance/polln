"""
Topology Optimizer for POLLN Agent Colonies

Finds optimal topologies for specific colony sizes and workloads
using simulated annealing and Pareto optimization.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from topology_generator import TopologyGenerator, TopologyType, TopologyParams
from topology_evaluator import TopologyEvaluator, TopologyMetrics
from workload_modeling import WorkloadGenerator, WorkloadConfig, MessageRequest


@dataclass
class OptimizationObjective:
    """Objective for topology optimization."""
    name: str
    weight: float
    minimize: bool


@dataclass
class OptimizationResult:
    """Result of topology optimization."""
    topology_type: TopologyType
    params: TopologyParams
    metrics: TopologyMetrics
    objectives: Dict[str, float]
    pareto_rank: int
    score: float


class TopologyOptimizer:
    """Optimize topologies for specific scenarios."""

    def __init__(self,
                 colony_size: int,
                 workload_config: WorkloadConfig,
                 objectives: Optional[List[OptimizationObjective]] = None,
                 seed: Optional[int] = None):
        """Initialize optimizer."""
        self.colony_size = colony_size
        self.workload_config = workload_config
        self.seed = seed

        self.generator = TopologyGenerator(seed=seed)
        self.evaluator = TopologyEvaluator(parallel=True)

        # Default objectives
        if objectives is None:
            self.objectives = [
                OptimizationObjective('avg_path_length', 0.25, True),
                OptimizationObjective('clustering_coefficient', 0.15, False),
                OptimizationObjective('global_efficiency', 0.15, False),
                OptimizationObjective('attack_tolerance', 0.15, False),
                OptimizationObjective('failure_tolerance', 0.10, False),
                OptimizationObjective('edge_cost', 0.10, True),
                OptimizationObjective('degree_cost', 0.10, True),
            ]
        else:
            self.objectives = objectives

    def optimize(self, iterations: int = 100) -> List[OptimizationResult]:
        """Run topology optimization."""
        results = []

        # Generate candidate topologies
        candidates = self._generate_candidates(iterations)

        # Evaluate all candidates
        print(f"Evaluating {len(candidates)} candidates...")
        for i, (topo_type, params, G) in enumerate(candidates):
            print(f"  Evaluating candidate {i+1}/{len(candidates)}: {topo_type.value}")

            try:
                metrics = self.evaluator.evaluate(G)
                objectives = self._calculate_objectives(metrics)

                result = OptimizationResult(
                    topology_type=topo_type,
                    params=params,
                    metrics=metrics,
                    objectives=objectives,
                    pareto_rank=0,
                    score=0.0
                )

                results.append(result)
            except Exception as e:
                print(f"    Error: {e}")

        # Calculate Pareto ranks
        results = self._calculate_pareto_ranks(results)

        # Calculate scores
        for result in results:
            result.score = self._calculate_score(result)

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        return results

    def _generate_candidates(self, iterations: int) -> List[Tuple[TopologyType, TopologyParams, nx.Graph]]:
        """Generate candidate topologies."""
        candidates = []

        # Parameter ranges for each topology type
        param_ranges = {
            TopologyType.ERDOS_RENYI: {'p': [0.01, 0.05, 0.1, 0.2]},
            TopologyType.WATTS_STROGATZ: {
                'k': [4, 6, 8, 10],
                'p': [0.01, 0.05, 0.1, 0.2, 0.3]
            },
            TopologyType.BARABASI_ALBERT: {'m': [2, 3, 4, 5]},
            TopologyType.MODULAR: {
                'modules': [3, 5, 7, 10],
                'module_size': [None]
            },
            TopologyType.TWO_TIER: {'k': [2, 4, 6, 8]},
            TopologyType.THREE_TIER: {},
            TopologyType.HIERARCHICAL: {'levels': [2, 3, 4]},
            TopologyType.HYBRID_SMALL_WORLD_SF: {
                'k': [4, 6, 8],
                'p': [0.1, 0.2, 0.3]
            },
        }

        # Generate candidates for each topology type
        for topo_type, ranges in param_ranges.items():
            # Generate parameter combinations
            combinations = self._generate_param_combinations(ranges)

            # Sample if too many combinations
            if len(combinations) > iterations // len(param_ranges):
                indices = np.random.choice(len(combinations),
                                          iterations // len(param_ranges),
                                          replace=False)
                combinations = [combinations[i] for i in indices]

            for params_dict in combinations:
                params = TopologyParams(n=self.colony_size, **params_dict)

                try:
                    G = self.generator.generate(topo_type, params)
                    candidates.append((topo_type, params, G))
                except Exception as e:
                    print(f"Failed to generate {topo_type.value}: {e}")

        return candidates

    def _generate_param_combinations(self, ranges: Dict[str, List]) -> List[Dict]:
        """Generate all parameter combinations."""
        if not ranges:
            return [{}]

        keys = list(ranges.keys())
        values = list(ranges.values())

        combinations = []
        for combination in self._cartesian_product(values):
            combinations.append(dict(zip(keys, combination)))

        return combinations

    def _cartesian_product(self, lists):
        """Generate Cartesian product of lists."""
        if not lists:
            yield ()
        else:
            for item in lists[0]:
                for rest in self._cartesian_product(lists[1:]):
                    yield (item,) + rest

    def _calculate_objectives(self, metrics: TopologyMetrics) -> Dict[str, float]:
        """Calculate objective values."""
        objectives = {}

        for obj in self.objectives:
            value = getattr(metrics, obj.name)

            # Normalize to [0, 1]
            if obj.name == 'avg_path_length':
                normalized = min(value / 10, 1.0)
            elif obj.name == 'clustering_coefficient':
                normalized = value
            elif obj.name == 'global_efficiency':
                normalized = value
            elif obj.name == 'attack_tolerance':
                normalized = value
            elif obj.name == 'failure_tolerance':
                normalized = value
            elif obj.name == 'edge_cost':
                normalized = value
            elif obj.name == 'degree_cost':
                normalized = value
            else:
                normalized = value

            objectives[obj.name] = normalized

        return objectives

    def _calculate_pareto_ranks(self, results: List[OptimizationResult]) -> List[OptimizationResult]:
        """Calculate Pareto ranks for results."""
        ranked = results.copy()
        rank = 0

        while ranked:
            # Find non-dominated solutions
            non_dominated = []
            dominated = []

            for i, result in enumerate(ranked):
                is_dominated = False

                for other in ranked:
                    if other == result:
                        continue

                    if self._dominates(other, result):
                        is_dominated = True
                        break

                if is_dominated:
                    dominated.append(result)
                else:
                    non_dominated.append(result)

            # Assign rank
            for result in non_dominated:
                result.pareto_rank = rank

            ranked = dominated
            rank += 1

        return results

    def _dominates(self, a: OptimizationResult, b: OptimizationResult) -> bool:
        """Check if solution a dominates solution b."""
        a_wins = False

        for obj in self.objectives:
            a_val = a.objectives[obj.name]
            b_val = b.objectives[obj.name]

            if obj.minimize:
                if a_val > b_val:
                    return False
                elif a_val < b_val:
                    a_wins = True
            else:
                if a_val < b_val:
                    return False
                elif a_val > b_val:
                    a_wins = True

        return a_wins

    def _calculate_score(self, result: OptimizationResult) -> float:
        """Calculate weighted score."""
        score = 0.0

        for obj in self.objectives:
            value = result.objectives[obj.name]

            if obj.minimize:
                score += obj.weight * (1 - value)
            else:
                score += obj.weight * value

        # Penalty for higher Pareto rank
        score *= (1.0 - result.pareto_rank * 0.1)

        return max(0, score)

    def find_pareto_frontier(self, results: List[OptimizationResult]) -> List[OptimizationResult]:
        """Extract Pareto frontier."""
        return [r for r in results if r.pareto_rank == 0]

    def recommend_topology(self, results: List[OptimizationResult]) -> OptimizationResult:
        """Recommend best topology."""
        if not results:
            raise ValueError("No results to recommend from")

        # Return highest scoring result
        return results[0]


class ScenarioOptimizer:
    """Optimize topologies across multiple scenarios."""

    def __init__(self, colony_sizes: List[int],
                 workload_configs: Dict[str, WorkloadConfig],
                 seed: Optional[int] = None):
        """Initialize scenario optimizer."""
        self.colony_sizes = colony_sizes
        self.workload_configs = workload_configs
        self.seed = seed

    def optimize_all_scenarios(self, iterations_per_scenario: int = 50) -> Dict[str, List[OptimizationResult]]:
        """Optimize all colony size × workload combinations."""
        results = {}

        total_scenarios = len(self.colony_sizes) * len(self.workload_configs)
        current = 0

        for size in self.colony_sizes:
            for workload_name, workload_config in self.workload_configs.items():
                current += 1
                scenario_key = f"{size}_{workload_name}"
                print(f"\n[{current}/{total_scenarios}] Optimizing: {scenario_key}")

                try:
                    optimizer = TopologyOptimizer(
                        colony_size=size,
                        workload_config=workload_config,
                        seed=self.seed
                    )

                    scenario_results = optimizer.optimize(iterations=iterations_per_scenario)
                    results[scenario_key] = scenario_results

                    print(f"  Best score: {scenario_results[0].score:.3f}")
                    print(f"  Topology: {scenario_results[0].topology_type.value}")

                except Exception as e:
                    print(f"  Error: {e}")
                    results[scenario_key] = []

        return results

    def generate_recommendations(self, results: Dict[str, List[OptimizationResult]]) -> Dict[str, OptimizationResult]:
        """Generate recommendations for each scenario."""
        recommendations = {}

        for scenario_key, scenario_results in results.items():
            if scenario_results:
                recommendations[scenario_key] = scenario_results[0]

        return recommendations


def optimize_for_colony_sizes(colony_sizes: List[int] = [10, 50, 100, 500, 1000],
                               iterations: int = 50) -> Dict[str, OptimizationResult]:
    """Optimize topologies for standard colony sizes."""
    from workload_modeling import generate_benchmark_workloads

    workload_configs = generate_benchmark_workloads()

    scenario_optimizer = ScenarioOptimizer(
        colony_sizes=colony_sizes,
        workload_configs=workload_configs,
        seed=42
    )

    results = scenario_optimizer.optimize_all_scenarios(iterations_per_scenario=iterations)
    recommendations = scenario_optimizer.generate_recommendations(results)

    return recommendations


if __name__ == "__main__":
    # Run optimization for colony sizes
    print("Running topology optimization...")
    recommendations = optimize_for_colony_sizes(colony_sizes=[10, 50, 100], iterations=20)

    # Print recommendations
    print("\n" + "="*60)
    print("TOPOLOGY RECOMMENDATIONS")
    print("="*60)

    for scenario, result in recommendations.items():
        print(f"\n{scenario}:")
        print(f"  Topology: {result.topology_type.value}")
        print(f"  Score: {result.score:.3f}")
        print(f"  Pareto Rank: {result.pareto_rank}")
        print(f"  Metrics:")
        print(f"    Avg Path Length: {result.metrics.avg_path_length:.3f}")
        print(f"    Clustering: {result.metrics.clustering_coefficient:.3f}")
        print(f"    Global Efficiency: {result.metrics.global_efficiency:.3f}")
        print(f"    Attack Tolerance: {result.metrics.attack_tolerance:.3f}")
        print(f"    Edge Cost: {result.metrics.edge_cost:.3f}")
