"""
Coordination Overhead Simulation for POLLN
Analyzes the cost-benefit tradeoffs of different coordination strategies
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class Granularity(Enum):
    FINE = "fine"  # Small, frequent tasks
    MEDIUM = "medium"  # Moderate task size
    COARSE = "coarse"  # Large, infrequent tasks


class SyncStrategy(Enum):
    ASYNC = "async"
    SYNC = "sync"
    HYBRID = "hybrid"


@dataclass
class TaskDecomposition:
    """Task decomposition with granularity level"""
    granularity: Granularity
    num_tasks: int
    avg_task_duration: float  # seconds
    dependencies: int  # Average dependencies per task
    data_transfer: float  # MB per task


@dataclass
class CoordinationMetrics:
    """Metrics for coordination overhead analysis"""
    execution_time: float
    coordination_time: float
    total_overhead: float
    overhead_ratio: float  # coordination / total time
    parallelism_benefit: float
    net_benefit: float
    throughput: float  # tasks per second
    scalability_score: float


@dataclass
class CommunicationCost:
    """Communication cost model"""
    a2a_package_cost: float  # seconds per package
    serialization_cost: float  # seconds per MB
    network_latency: float  # seconds
    sync_overhead: float  # seconds per sync point


class CoordinationSimulator:
    """Simulates coordination overhead at different granularities"""

    def __init__(self, num_agents: int = 10, comm_cost: CommunicationCost = None):
        self.num_agents = num_agents
        self.comm_cost = comm_cost or CommunicationCost(
            a2a_package_cost=0.001,
            serialization_cost=0.01,
            network_latency=0.005,
            sync_overhead=0.01
        )

    def simulate_fine_grained(
        self,
        decomposition: TaskDecomposition,
        strategy: SyncStrategy
    ) -> CoordinationMetrics:
        """Simulate fine-grained task decomposition"""
        # Many small tasks
        num_tasks = decomposition.num_tasks
        task_duration = decomposition.avg_task_duration

        # Compute coordination costs
        a2a_packages = num_tasks * (1 + decomposition.dependencies)
        comm_time = self._compute_communication_cost(
            a2a_packages,
            decomposition.data_transfer
        )

        # Sync overhead
        if strategy == SyncStrategy.SYNC:
            sync_points = num_tasks
            sync_time = sync_points * self.comm_cost.sync_overhead * self.num_agents
        elif strategy == SyncStrategy.HYBRID:
            sync_points = num_tasks // 10  # Sync every 10 tasks
            sync_time = sync_points * self.comm_cost.sync_overhead * self.num_agents
        else:  # ASYNC
            sync_time = 0

        # Execution time (with parallelism)
        parallelism = min(self.num_agents, num_tasks)
        execution_time = (num_tasks * task_duration) / parallelism

        total_time = execution_time + comm_time + sync_time
        overhead = comm_time + sync_time

        # Compute benefits
        sequential_time = num_tasks * task_duration
        parallelism_benefit = sequential_time - execution_time
        net_benefit = parallelism_benefit - overhead

        return CoordinationMetrics(
            execution_time=execution_time,
            coordination_time=overhead,
            total_overhead=overhead,
            overhead_ratio=overhead / total_time,
            parallelism_benefit=parallelism_benefit,
            net_benefit=net_benefit,
            throughput=num_tasks / total_time,
            scalability_score=self._compute_scalability(fine_grained=True)
        )

    def simulate_medium_grained(
        self,
        decomposition: TaskDecomposition,
        strategy: SyncStrategy
    ) -> CoordinationMetrics:
        """Simulate medium-grained task decomposition"""
        # Moderate number of tasks
        num_tasks = decomposition.num_tasks
        task_duration = decomposition.avg_task_duration

        # Communication costs
        a2a_packages = num_tasks * (1 + decomposition.dependencies * 0.5)
        comm_time = self._compute_communication_cost(
            a2a_packages,
            decomposition.data_transfer
        )

        # Sync overhead
        if strategy == SyncStrategy.SYNC:
            sync_points = num_tasks // 2
            sync_time = sync_points * self.comm_cost.sync_overhead * self.num_agents
        elif strategy == SyncStrategy.HYBRID:
            sync_points = num_tasks // 5
            sync_time = sync_points * self.comm_cost.sync_overhead * self.num_agents
        else:  # ASYNC
            sync_time = 0

        # Execution time
        parallelism = min(self.num_agents, num_tasks)
        execution_time = (num_tasks * task_duration) / parallelism

        total_time = execution_time + comm_time + sync_time
        overhead = comm_time + sync_time

        sequential_time = num_tasks * task_duration
        parallelism_benefit = sequential_time - execution_time
        net_benefit = parallelism_benefit - overhead

        return CoordinationMetrics(
            execution_time=execution_time,
            coordination_time=overhead,
            total_overhead=overhead,
            overhead_ratio=overhead / total_time,
            parallelism_benefit=parallelism_benefit,
            net_benefit=net_benefit,
            throughput=num_tasks / total_time,
            scalability_score=self._compute_scalability(fine_grained=False)
        )

    def simulate_coarse_grained(
        self,
        decomposition: TaskDecomposition,
        strategy: SyncStrategy
    ) -> CoordinationMetrics:
        """Simulate coarse-grained task decomposition"""
        # Few large tasks
        num_tasks = decomposition.num_tasks
        task_duration = decomposition.avg_task_duration

        # Communication costs
        a2a_packages = num_tasks * (1 + decomposition.dependencies * 0.2)
        comm_time = self._compute_communication_cost(
            a2a_packages,
            decomposition.data_transfer
        )

        # Sync overhead
        if strategy in [SyncStrategy.SYNC, SyncStrategy.HYBRID]:
            sync_points = num_tasks // 10
            sync_time = sync_points * self.comm_cost.sync_overhead * self.num_agents
        else:  # ASYNC
            sync_time = 0

        # Execution time
        parallelism = min(self.num_agents, num_tasks)
        execution_time = (num_tasks * task_duration) / parallelism

        total_time = execution_time + comm_time + sync_time
        overhead = comm_time + sync_time

        sequential_time = num_tasks * task_duration
        parallelism_benefit = sequential_time - execution_time
        net_benefit = parallelism_benefit - overhead

        return CoordinationMetrics(
            execution_time=execution_time,
            coordination_time=overhead,
            total_overhead=overhead,
            overhead_ratio=overhead / total_time,
            parallelism_benefit=parallelism_benefit,
            net_benefit=net_benefit,
            throughput=num_tasks / total_time,
            scalability_score=self._compute_scalability(fine_grained=False)
        )

    def _compute_communication_cost(
        self,
        num_packages: int,
        data_size: float
    ) -> float:
        """Compute total communication cost"""
        package_cost = num_packages * self.comm_cost.a2a_package_cost
        serialization_cost = data_size * self.comm_cost.serialization_cost
        latency = num_packages * self.comm_cost.network_latency
        return package_cost + serialization_cost + latency

    def _compute_scalability(self, fine_grained: bool) -> float:
        """Compute scalability score"""
        if fine_grained:
            # Fine-grained scales well but has overhead
            return 0.7 + (0.2 * self.num_agents / 20)
        else:
            # Coarse-grained has less overhead but limits parallelism
            return 0.5 + (0.3 * self.num_agents / 20)


class GranularityOptimizer:
    """Optimizes task granularity for maximum efficiency"""

    def __init__(self, simulator: CoordinationSimulator):
        self.simulator = simulator
        self.results = {}

    def find_optimal_granularity(
        self,
        total_work: float,
        data_per_unit: float,
        dependency_ratio: float = 0.1
    ) -> Tuple[Granularity, SyncStrategy, CoordinationMetrics]:
        """Find optimal granularity and sync strategy"""
        best_granularity = None
        best_strategy = None
        best_metrics = None
        best_score = float('inf')

        # Test all combinations
        granularities = [
            (Granularity.FINE, 1000, 0.1),  # Many small tasks
            (Granularity.MEDIUM, 100, 1.0),  # Moderate tasks
            (Granularity.COARSE, 10, 10.0),  # Few large tasks
        ]

        for granularity, num_tasks, task_duration in granularities:
            for strategy in SyncStrategy:
                decomposition = TaskDecomposition(
                    granularity=granularity,
                    num_tasks=num_tasks,
                    avg_task_duration=task_duration,
                    dependencies=int(num_tasks * dependency_ratio),
                    data_transfer=data_per_unit / num_tasks
                )

                metrics = self._simulate_with_granularity(
                    decomposition, strategy
                )

                score = self._compute_score(metrics)
                if score < best_score:
                    best_score = score
                    best_granularity = granularity
                    best_strategy = strategy
                    best_metrics = metrics

        return best_granularity, best_strategy, best_metrics

    def _simulate_with_granularity(
        self,
        decomposition: TaskDecomposition,
        strategy: SyncStrategy
    ) -> CoordinationMetrics:
        """Route to appropriate simulation based on granularity"""
        if decomposition.granularity == Granularity.FINE:
            return self.simulator.simulate_fine_grained(decomposition, strategy)
        elif decomposition.granularity == Granularity.MEDIUM:
            return self.simulator.simulate_medium_grained(decomposition, strategy)
        else:
            return self.simulator.simulate_coarse_grained(decomposition, strategy)

    def _compute_score(self, metrics: CoordinationMetrics) -> float:
        """Compute score (lower is better)"""
        time_weight = 1.0
        overhead_weight = 2.0
        throughput_weight = -1.0
        scalability_weight = -0.5

        score = (
            time_weight * metrics.execution_time +
            overhead_weight * metrics.total_overhead +
            throughput_weight * metrics.throughput +
            scalability_weight * metrics.scalability_score
        )
        return score


def run_coordination_analysis():
    """Run comprehensive coordination overhead analysis"""
    results = {}

    # Test different scenarios
    scenarios = [
        ("data_processing", 100.0, 10.0, 0.05),  # High data, low dependencies
        ("workflow_orchestration", 50.0, 1.0, 0.2),  # Medium data, high dependencies
        ("batch_computation", 200.0, 5.0, 0.02),  # High work, low dependencies
        ("real_time_processing", 20.0, 0.5, 0.1),  # Low work, low data
    ]

    for scenario_name, total_work, data_per_unit, dep_ratio in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*60}")
        print(f"Total work: {total_work}s")
        print(f"Data per unit: {data_per_unit}MB")
        print(f"Dependency ratio: {dep_ratio}")

        # Test with different agent counts
        for num_agents in [5, 10, 20, 50]:
            print(f"\n--- Testing with {num_agents} agents ---")

            simulator = CoordinationSimulator(num_agents)
            optimizer = GranularityOptimizer(simulator)

            granularity, strategy, metrics = optimizer.find_optimal_granularity(
                total_work, data_per_unit, dep_ratio
            )

            print(f"\nOptimal configuration:")
            print(f"  Granularity: {granularity.value}")
            print(f"  Sync strategy: {strategy.value}")

            print(f"\nMetrics:")
            print(f"  Execution time: {metrics.execution_time:.3f}s")
            print(f"  Overhead ratio: {metrics.overhead_ratio:.3f}")
            print(f"  Net benefit: {metrics.net_benefit:.3f}s")
            print(f"  Throughput: {metrics.throughput:.2f} tasks/s")
            print(f"  Scalability: {metrics.scalability_score:.3f}")

            scenario_key = f"{scenario_name}_{num_agents}_agents"
            results[scenario_key] = {
                'scenario': scenario_name,
                'num_agents': num_agents,
                'total_work': total_work,
                'data_per_unit': data_per_unit,
                'dependency_ratio': dep_ratio,
                'optimal': {
                    'granularity': granularity.value,
                    'sync_strategy': strategy.value,
                },
                'metrics': {
                    'execution_time': metrics.execution_time,
                    'overhead_ratio': metrics.overhead_ratio,
                    'net_benefit': metrics.net_benefit,
                    'throughput': metrics.throughput,
                    'scalability_score': metrics.scalability_score,
                }
            }

    # Generate overhead curves
    print(f"\n{'='*60}")
    print("Generating overhead curves...")

    overhead_curves = generate_overhead_curves()
    results['overhead_curves'] = overhead_curves

    return results


def generate_overhead_curves() -> Dict[str, Any]:
    """Generate overhead vs granularity curves"""
    curves = {
        'fine_grained': [],
        'medium_grained': [],
        'coarse_grained': [],
    }

    agent_counts = [2, 5, 10, 20, 50, 100]

    for num_agents in agent_counts:
        simulator = CoordinationSimulator(num_agents)

        # Fine-grained
        fine_decomp = TaskDecomposition(
            Granularity.FINE, 1000, 0.1, 100, 0.001
        )
        fine_async = simulator.simulate_fine_grained(fine_decomp, SyncStrategy.ASYNC)
        curves['fine_grained'].append({
            'agents': num_agents,
            'overhead_ratio': fine_async.overhead_ratio,
            'throughput': fine_async.throughput,
        })

        # Medium-grained
        medium_decomp = TaskDecomposition(
            Granularity.MEDIUM, 100, 1.0, 20, 0.01
        )
        medium_async = simulator.simulate_medium_grained(medium_decomp, SyncStrategy.ASYNC)
        curves['medium_grained'].append({
            'agents': num_agents,
            'overhead_ratio': medium_async.overhead_ratio,
            'throughput': medium_async.throughput,
        })

        # Coarse-grained
        coarse_decomp = TaskDecomposition(
            Granularity.COARSE, 10, 10.0, 2, 0.1
        )
        coarse_async = simulator.simulate_coarse_grained(coarse_decomp, SyncStrategy.ASYNC)
        curves['coarse_grained'].append({
            'agents': num_agents,
            'overhead_ratio': coarse_async.overhead_ratio,
            'throughput': coarse_async.throughput,
        })

    return curves


if __name__ == '__main__':
    results = run_coordination_analysis()

    # Save results
    import os
    os.makedirs('simulation_results', exist_ok=True)
    with open('simulation_results/coordination_overhead.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Coordination overhead analysis complete!")
    print("Results saved to simulation_results/coordination_overhead.json")
