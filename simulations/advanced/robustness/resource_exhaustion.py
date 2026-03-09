"""
POLLN Robustness Simulation: Resource Exhaustion
===============================================

This simulation tests POLLN's behavior under resource exhaustion scenarios
and validates graceful degradation and recovery mechanisms.

Resource Types:
1. CPU exhaustion: High computational load
2. Memory exhaustion: Large allocation patterns
3. Network exhaustion: Bandwidth saturation
4. Cache exhaustion: KV-cache overflow
5. Disk I/O exhaustion: High storage load

Degradation Patterns:
1. Linear degradation: Proportional to load
2. Threshold-based: Sudden drop at limit
3. Cascading: One resource affects others
4. Intermittent: Burst patterns

Mitigation Strategies:
1. Throttling: Limit resource usage
2. Load shedding: Drop low-priority tasks
3. Caching: Reduce computational load
4. Autoscaling: Add resources dynamically
5. Queue management: Prioritize requests

Metrics:
- Performance degradation rate
- Recovery time after overload
- Resource utilization efficiency
- Task completion rate under stress
- System stability index
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import defaultdict, deque
import time


class ResourceType(Enum):
    """Types of system resources"""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    CACHE = "cache"
    DISK_IO = "disk_io"


class DegradationPattern(Enum):
    """Patterns of performance degradation"""
    LINEAR = "linear"                      # Gradual degradation
    THRESHOLD = "threshold"                # Sudden drop at limit
    CASCADING = "cascading"                # One resource affects others
    INTERMITTENT = "intermittent"          # Burst patterns


class MitigationStrategy(Enum):
    """Strategies to mitigate resource exhaustion"""
    THROTTLING = "throttling"              # Limit resource usage
    LOAD_SHEDDING = "load_shedding"        # Drop low-priority tasks
    CACHING = "caching"                    # Reduce computational load
    AUTOSCALING = "autoscaling"            # Add resources dynamically
    QUEUE_MANAGEMENT = "queue_management"  # Prioritize requests
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Reduce quality


@dataclass
class ResourceState:
    """State of a system resource"""
    resource_type: ResourceType
    capacity: float           # Maximum capacity
    current_usage: float      # Current usage (0-1 scale)
    allocation: float         # Allocated amount
    queue_length: int = 0     # Length of request queue
    throttle_active: bool = False


@dataclass
class Task:
    """A computational task"""
    id: str
    priority: int            # 1-10, 10 being highest
    cpu_required: float      # CPU units required
    memory_required: float   # Memory units required
    network_required: float  # Network units required
    execution_time: float    # Estimated execution time
    deadline: Optional[float] = None


@dataclass
class ResourceExhaustionEvent:
    """A resource exhaustion event"""
    timestamp: float
    resource_type: ResourceType
    exhaustion_level: float    # 0-1 scale
    mitigation_triggered: bool
    recovery_time_ms: Optional[float] = None


@dataclass
class ResourceMetrics:
    """Metrics for resource exhaustion simulation"""
    total_tasks: int = 0
    completed_tasks: int = 0
    dropped_tasks: int = 0
    task_completion_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    peak_resource_usage: Dict[str, float] = field(default_factory=dict)
    degradation_rate: float = 0.0
    recovery_time_ms: float = 0.0
    system_stability_index: float = 0.0


class ResourceExhaustionSimulator:
    """
    Simulates resource exhaustion in POLLN

    Features:
    - Multiple resource types
    - Various degradation patterns
    - Mitigation strategies
    - Task scheduling
    - Load balancing
    - Performance monitoring
    """

    def __init__(
        self,
        num_agents: int = 50,
        base_load: float = 0.5,
        peak_load: float = 1.5,
        degradation_pattern: DegradationPattern = DegradationPattern.LINEAR,
        mitigation_strategies: List[MitigationStrategy] = None,
        seed: int = 42
    ):
        """
        Initialize the resource exhaustion simulator

        Args:
            num_agents: Number of agents in the system
            base_load: Base system load (0-1 scale)
            peak_load: Peak system load during surge (0-2 scale)
            degradation_pattern: Pattern of performance degradation
            mitigation_strategies: List of mitigation strategies to employ
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)

        self.num_agents = num_agents
        self.base_load = base_load
        self.peak_load = peak_load
        self.degradation_pattern = degradation_pattern
        self.mitigation_strategies = mitigation_strategies or [
            MitigationStrategy.THROTTLING,
            MitigationStrategy.LOAD_SHEDDING,
        ]

        # Initialize resources
        self.resources = self._initialize_resources()

        # Task queues
        self.task_queue: deque[Task] = deque()
        self.completed_tasks: List[Task] = []
        self.dropped_tasks: List[Task] = []

        # Exhaustion events
        self.exhaustion_events: List[ResourceExhaustionEvent] = []
        self.metrics = ResourceMetrics()

        # Current time
        self.current_time = 0.0

        # Performance baseline
        self.baseline_performance = 1.0

    def _initialize_resources(self) -> Dict[ResourceType, ResourceState]:
        """Initialize system resources"""
        return {
            ResourceType.CPU: ResourceState(
                resource_type=ResourceType.CPU,
                capacity=100.0,  # 100 CPU units
                current_usage=self.base_load,
                allocation=0.0,
            ),
            ResourceType.MEMORY: ResourceState(
                resource_type=ResourceType.MEMORY,
                capacity=16.0,   # 16 GB
                current_usage=self.base_load,
                allocation=0.0,
            ),
            ResourceType.NETWORK: ResourceState(
                resource_type=ResourceType.NETWORK,
                capacity=10.0,   # 10 Gbps
                current_usage=self.base_load * 0.5,
                allocation=0.0,
            ),
            ResourceType.CACHE: ResourceState(
                resource_type=ResourceType.CACHE,
                capacity=4.0,    # 4 GB
                current_usage=self.base_load * 0.3,
                allocation=0.0,
            ),
            ResourceType.DISK_IO: ResourceState(
                resource_type=ResourceType.DISK_IO,
                capacity=500.0,  # 500 MB/s
                current_usage=self.base_load * 0.2,
                allocation=0.0,
            ),
        }

    def _generate_task(self, priority: int = None) -> Task:
        """Generate a random task"""
        task_id = f"task_{len(self.task_queue) + len(self.completed_tasks) + len(self.dropped_tasks)}"

        return Task(
            id=task_id,
            priority=priority or random.randint(1, 10),
            cpu_required=random.uniform(1, 10),
            memory_required=random.uniform(0.5, 2),
            network_required=random.uniform(0.1, 1),
            execution_time=random.uniform(10, 100),
        )

    def _calculate_degradation_factor(self, resource: ResourceState) -> float:
        """
        Calculate performance degradation factor based on resource usage

        Returns:
            Degradation factor (1.0 = no degradation, 0.0 = complete failure)
        """
        usage = resource.current_usage / resource.capacity

        if self.degradation_pattern == DegradationPattern.LINEAR:
            # Linear degradation: performance decreases linearly with usage
            return max(0.0, 1.0 - usage)

        elif self.degradation_pattern == DegradationPattern.THRESHOLD:
            # Threshold-based: sudden drop at 80% capacity
            threshold = 0.8
            if usage < threshold:
                return 1.0
            else:
                return max(0.0, 1.0 - (usage - threshold) * 5)

        elif self.degradation_pattern == DegradationPattern.CASCADING:
            # Cascading: one resource affects others
            # If this resource is exhausted, reduce efficiency of others
            if usage > 0.9:
                return max(0.0, 1.0 - (usage - 0.9) * 10)
            return 1.0

        elif self.degradation_pattern == DegradationPattern.INTERMITTENT:
            # Intermittent: random drops in performance
            if random.random() < 0.1:
                return 0.5
            return 1.0

        return 1.0

    def _apply_throttling(self, resource: ResourceState) -> None:
        """Apply throttling to resource"""
        if resource.current_usage > resource.capacity * 0.8:
            # Throttle new allocations
            resource.throttle_active = True
            resource.current_usage = resource.capacity * 0.8
        else:
            resource.throttle_active = False

    def _apply_load_shedding(self) -> None:
        """Drop low-priority tasks when resources are exhausted"""
        # Check if any resource is exhausted
        exhausted = any(
            r.current_usage > r.capacity * 0.9
            for r in self.resources.values()
        )

        if exhausted and self.task_queue:
            # Sort tasks by priority
            sorted_tasks = sorted(
                list(self.task_queue),
                key=lambda t: t.priority
            )

            # Drop lowest priority tasks
            num_to_drop = len(sorted_tasks) // 4  # Drop 25%

            for _ in range(num_to_drop):
                if self.task_queue:
                    task = self.task_queue.popleft()
                    self.dropped_tasks.append(task)

    def _apply_caching(self) -> None:
        """Apply caching to reduce CPU load"""
        # Simulate cache hits reducing CPU usage
        cache_hit_rate = 0.3  # 30% cache hit rate

        cpu_resource = self.resources[ResourceType.CPU]
        if cpu_resource.current_usage > cpu_resource.capacity * 0.7:
            # Cache hits reduce effective CPU usage
            cpu_resource.current_usage *= (1 - cache_hit_rate * 0.5)

    def _apply_queue_management(self) -> None:
        """Manage task queue based on priorities"""
        if not self.task_queue:
            return

        # Sort by priority (highest first)
        sorted_tasks = sorted(
            list(self.task_queue),
            key=lambda t: t.priority,
            reverse=True
        )

        # Rebuild queue with priority ordering
        self.task_queue.clear()
        self.task_queue.extend(sorted_tasks)

    def _execute_task(self, task: Task) -> bool:
        """
        Attempt to execute a task

        Returns:
            True if task was executed, False if dropped
        """
        # Check if resources are available
        cpu_available = (
            self.resources[ResourceType.CPU].current_usage +
            task.cpu_required <= self.resources[ResourceType.CPU].capacity
        )

        memory_available = (
            self.resources[ResourceType.MEMORY].current_usage +
            task.memory_required <= self.resources[ResourceType.MEMORY].capacity
        )

        if not (cpu_available and memory_available):
            # Resources not available
            if MitigationStrategy.LOAD_SHEDDING in self.mitigation_strategies:
                if task.priority < 5:  # Low priority
                    self.dropped_tasks.append(task)
                    return False

        # Allocate resources
        self.resources[ResourceType.CPU].current_usage += task.cpu_required
        self.resources[ResourceType.MEMORY].current_usage += task.memory_required

        # Simulate execution
        execution_time = task.execution_time

        # Apply degradation factors
        degradation_factors = [
            self._calculate_degradation_factor(r)
            for r in self.resources.values()
        ]

        avg_degradation = np.mean(degradation_factors)
        execution_time /= max(0.1, avg_degradation)  # Slower with degradation

        # Release resources
        self.resources[ResourceType.CPU].current_usage -= task.cpu_required
        self.resources[ResourceType.MEMORY].current_usage -= task.memory_required

        self.completed_tasks.append(task)
        return True

    def _check_exhaustion(self) -> None:
        """Check for resource exhaustion and record events"""
        for resource in self.resources.values():
            exhaustion_level = resource.current_usage / resource.capacity

            if exhaustion_level > 0.9:
                # Resource exhausted
                mitigation_triggered = False

                # Apply mitigation strategies
                if MitigationStrategy.THROTTLING in self.mitigation_strategies:
                    self._apply_throttling(resource)
                    mitigation_triggered = True

                if MitigationStrategy.LOAD_SHEDDING in self.mitigation_strategies:
                    self._apply_load_shedding()
                    mitigation_triggered = True

                if MitigationStrategy.CACHING in self.mitigation_strategies:
                    self._apply_caching()
                    mitigation_triggered = True

                if MitigationStrategy.QUEUE_MANAGEMENT in self.mitigation_strategies:
                    self._apply_queue_management()
                    mitigation_triggered = True

                # Record event
                event = ResourceExhaustionEvent(
                    timestamp=self.current_time,
                    resource_type=resource.resource_type,
                    exhaustion_level=exhaustion_level,
                    mitigation_triggered=mitigation_triggered,
                )

                self.exhaustion_events.append(event)

    def _simulate_load_surge(self) -> None:
        """Simulate a load surge"""
        # Increase task arrival rate
        surge_tasks = int(self.num_agents * (self.peak_load - self.base_load))

        for _ in range(surge_tasks):
            task = self._generate_task(priority=random.randint(1, 10))
            self.task_queue.append(task)

    def _simulate_step(self) -> None:
        """Simulate one time step"""
        # Add base load tasks
        base_tasks = int(self.num_agents * self.base_load)
        for _ in range(base_tasks):
            task = self._generate_task(priority=random.randint(1, 10))
            self.task_queue.append(task)

        # Execute tasks
        max_executions = 10  # Max tasks per step
        executions = 0

        while self.task_queue and executions < max_executions:
            task = self.task_queue.popleft()
            self._execute_task(task)
            executions += 1

        # Check for exhaustion
        self._check_exhaustion()

        # Update time
        self.current_time += 1.0

    def run_simulation(self, num_steps: int = 100, surge_at_step: int = 30) -> ResourceMetrics:
        """
        Run complete resource exhaustion simulation

        Args:
            num_steps: Number of simulation steps
            surge_at_step: Step at which to trigger load surge

        Returns:
            ResourceMetrics with aggregated results
        """
        print("Starting Resource Exhaustion Simulation...")
        print(f"Agents: {self.num_agents}")
        print(f"Base load: {self.base_load:.1%}")
        print(f"Peak load: {self.peak_load:.1%}")
        print(f"Degradation pattern: {self.degradation_pattern.value}")
        print(f"Mitigation strategies: {[s.value for s in self.mitigation_strategies]}")
        print()

        for step in range(num_steps):
            # Trigger load surge at specified step
            if step == surge_at_step:
                print(f"Step {step}: Triggering load surge...")
                self._simulate_load_surge()

            # Simulate normal operation
            self._simulate_step()

            # Print periodic status
            if step % 10 == 0:
                cpu_usage = self.resources[ResourceType.CPU].current_usage
                cpu_capacity = self.resources[ResourceType.CPU].capacity
                print(f"Step {step}: CPU usage {cpu_usage:.1f}/{cpu_capacity:.1f} "
                      f"({cpu_usage/cpu_capacity*100:.1f}%), "
                      f"Queue: {len(self.task_queue)} tasks")

        # Calculate metrics
        self._calculate_metrics()

        return self.metrics

    def _calculate_metrics(self) -> None:
        """Calculate aggregated metrics"""
        self.metrics.total_tasks = len(self.completed_tasks) + len(self.dropped_tasks)
        self.metrics.completed_tasks = len(self.completed_tasks)
        self.metrics.dropped_tasks = len(self.dropped_tasks)

        if self.metrics.total_tasks > 0:
            self.metrics.task_completion_rate = self.metrics.completed_tasks / self.metrics.total_tasks

        # Peak resource usage
        for resource_type, resource in self.resources.items():
            peak = max(
                resource.current_usage,
                self.metrics.peak_resource_usage.get(resource_type.value, 0)
            )
            self.metrics.peak_resource_usage[resource_type.value] = peak

        # Degradation rate (1 - completion rate under stress)
        if self.peak_load > 1.0:
            self.metrics.degradation_rate = 1.0 - self.metrics.task_completion_rate

        # System stability index (inverse of variance in performance)
        if self.completed_tasks:
            # Calculate variance in task completion times
            completion_times = [task.execution_time for task in self.completed_tasks]
            variance = np.var(completion_times) if len(completion_times) > 1 else 0
            self.metrics.system_stability_index = 1.0 / (1.0 + variance)

    def print_metrics(self) -> None:
        """Print formatted metrics"""
        print("\n" + "="*60)
        print("RESOURCE EXHAUSTION SIMULATION RESULTS")
        print("="*60)
        print(f"\nTotal Tasks:           {self.metrics.total_tasks}")
        print(f"Completed:              {self.metrics.completed_tasks} ({self.metrics.task_completion_rate*100:.1f}%)")
        print(f"Dropped:                {self.metrics.dropped_tasks}")
        print(f"\nDegradation Rate:       {self.metrics.degradation_rate*100:.1f}%")
        print(f"System Stability:       {self.metrics.system_stability_index:.3f}")
        print(f"\nPeak Resource Usage:")
        for resource_type, peak_usage in self.metrics.peak_resource_usage.items():
            capacity = self.resources[ResourceType(resource_type)].capacity
            print(f"  {resource_type:<15} {peak_usage:.1f}/{capacity:.1f} ({peak_usage/capacity*100:.1f}%)")
        print("="*60 + "\n")

    def generate_resource_config(self) -> Dict:
        """
        Generate resource protection configuration

        Returns:
            Dictionary with configuration recommendations
        """
        recommendations = {
            'resource_limits': {
                'max_cpu_per_agent': self.resources[ResourceType.CPU].capacity / self.num_agents * 0.8,
                'max_memory_per_agent': self.resources[ResourceType.MEMORY].capacity / self.num_agents * 0.8,
                'max_network_per_agent': self.resources[ResourceType.NETWORK].capacity / self.num_agents * 0.8,
                'emergency_throttle': 0.5,
            },
            'mitigation': {
                'throttling_enabled': MitigationStrategy.THROTTLING in self.mitigation_strategies,
                'load_shedding_enabled': MitigationStrategy.LOAD_SHEDDING in self.mitigation_strategies,
                'caching_enabled': MitigationStrategy.CACHING in self.mitigation_strategies,
                'queue_management_enabled': MitigationStrategy.QUEUE_MANAGEMENT in self.mitigation_strategies,
            },
            'thresholds': {
                'cpu_warning': 0.7,
                'cpu_critical': 0.9,
                'memory_warning': 0.7,
                'memory_critical': 0.9,
                'network_warning': 0.7,
                'network_critical': 0.9,
            },
            'recommendations': []
        }

        # Add specific recommendations
        if self.metrics.task_completion_rate < 0.8:
            recommendations['recommendations'].append(
                "Task completion rate below 80%. Implement load shedding or autoscaling."
            )

        if self.metrics.degradation_rate > 0.3:
            recommendations['recommendations'].append(
                "High degradation rate. Strengthen throttling and caching mechanisms."
            )

        if self.metrics.system_stability_index < 0.5:
            recommendations['recommendations'].append(
                "Low system stability. Implement better queue management and priority scheduling."
            )

        # Check peak usage
        for resource_type, peak_usage in self.metrics.peak_resource_usage.items():
            capacity = self.resources[ResourceType(resource_type)].capacity
            if peak_usage / capacity > 0.9:
                recommendations['recommendations'].append(
                    f"{resource_type} consistently near capacity. Consider scaling resources."
                )

        return recommendations

    def save_results(self, filepath: str) -> None:
        """Save simulation results to JSON file"""
        results_data = {
            'configuration': {
                'num_agents': self.num_agents,
                'base_load': self.base_load,
                'peak_load': self.peak_load,
                'degradation_pattern': self.degradation_pattern.value,
                'mitigation_strategies': [s.value for s in self.mitigation_strategies],
            },
            'metrics': {
                'total_tasks': self.metrics.total_tasks,
                'completed_tasks': self.metrics.completed_tasks,
                'dropped_tasks': self.metrics.dropped_tasks,
                'task_completion_rate': self.metrics.task_completion_rate,
                'degradation_rate': self.metrics.degradation_rate,
                'system_stability_index': self.metrics.system_stability_index,
                'peak_resource_usage': self.metrics.peak_resource_usage,
            },
            'exhaustion_events': [
                {
                    'timestamp': e.timestamp,
                    'resource_type': e.resource_type.value,
                    'exhaustion_level': e.exhaustion_level,
                    'mitigation_triggered': e.mitigation_triggered,
                }
                for e in self.exhaustion_events
            ],
            'resource_config': self.generate_resource_config(),
        }

        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to {filepath}")


def compare_mitigation_strategies():
    """Compare different mitigation strategies"""
    print("\n" + "="*60)
    print("COMPARING MITIGATION STRATEGIES")
    print("="*60 + "\n")

    strategy_combinations = [
        [],  # No mitigation
        [MitigationStrategy.THROTTLING],
        [MitigationStrategy.LOAD_SHEDDING],
        [MitigationStrategy.CACHING],
        [MitigationStrategy.QUEUE_MANAGEMENT],
        [MitigationStrategy.THROTTLING, MitigationStrategy.LOAD_SHEDDING],
        [MitigationStrategy.THROTTLING, MitigationStrategy.CACHING, MitigationStrategy.QUEUE_MANAGEMENT],
        [MitigationStrategy.THROTTLING, MitigationStrategy.LOAD_SHEDDING, MitigationStrategy.CACHING, MitigationStrategy.QUEUE_MANAGEMENT],
    ]

    results = {}

    for strategies in strategy_combinations:
        strategy_name = "+".join([s.value for s in strategies]) if strategies else "none"
        print(f"\nTesting {strategy_name}...")

        simulator = ResourceExhaustionSimulator(
            num_agents=50,
            base_load=0.5,
            peak_load=1.5,
            mitigation_strategies=strategies,
        )

        metrics = simulator.run_simulation(num_steps=100, surge_at_step=30)
        results[strategy_name] = {
            'task_completion_rate': metrics.task_completion_rate,
            'degradation_rate': metrics.degradation_rate,
            'system_stability_index': metrics.system_stability_index,
        }

        simulator.print_metrics()

    # Print comparison
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    print(f"{'Strategy':<60} {'Completion':<12} {'Degradation':<12} {'Stability':<12}")
    print("-"*96)

    for strategy, metrics in results.items():
        print(f"{strategy:<60} {metrics['task_completion_rate']:<12.1%} "
              f"{metrics['degradation_rate']:<12.1%} {metrics['system_stability_index']:<12.3f}")

    print("="*96 + "\n")

    return results


def main():
    """Main entry point for the simulation"""
    print("POLLN Resource Exhaustion Simulation")
    print("="*60)

    # Create simulator with multiple mitigation strategies
    simulator = ResourceExhaustionSimulator(
        num_agents=50,
        base_load=0.5,
        peak_load=1.5,
        degradation_pattern=DegradationPattern.LINEAR,
        mitigation_strategies=[
            MitigationStrategy.THROTTLING,
            MitigationStrategy.LOAD_SHEDDING,
            MitigationStrategy.CACHING,
            MitigationStrategy.QUEUE_MANAGEMENT,
        ],
    )

    # Run simulation
    metrics = simulator.run_simulation(num_steps=100, surge_at_step=30)

    # Print results
    simulator.print_metrics()

    # Generate config
    config = simulator.generate_resource_config()
    print("\nResource Protection Configuration:")
    print(json.dumps(config, indent=2))

    # Save results
    simulator.save_results('simulations/advanced/robustness/results/resource_exhaustion_results.json')

    return metrics


if __name__ == '__main__':
    main()
