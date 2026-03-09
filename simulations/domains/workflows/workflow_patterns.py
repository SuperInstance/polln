"""
Workflow Pattern Simulation for POLLN
Simulates different workflow patterns to optimize multi-agent coordination
"""

import time
import numpy as np
from typing import List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class PatternType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    MAP_REDUCE = "map_reduce"


@dataclass
class Task:
    """A task in a workflow"""
    id: str
    name: str
    duration: float  # Base duration in seconds
    complexity: float  # 0-1 scale
    dependencies: List[str] = field(default_factory=list)
    data_size: float = 1.0  # MB of data
    quality_requirement: float = 0.9  # 0-1 scale


@dataclass
class WorkflowMetrics:
    """Metrics collected from workflow execution"""
    completion_time: float
    total_cost: float
    quality_score: float
    success_rate: float
    agent_utilization: float
    communication_overhead: float
    memory_usage: float
    a2a_packages_sent: int


@dataclass
class AgentConfig:
    """Agent configuration"""
    agent_type: str  # 'core', 'role', 'task'
    processing_speed: float  # Multiplier
    reliability: float  # 0-1 scale
    communication_cost: float  # ms per A2A package
    memory_capacity: float  # MB


class WorkflowSimulator:
    """Simulates workflow patterns with configurable agents"""

    def __init__(self, agents: List[AgentConfig], a2a_overhead: float = 0.001):
        self.agents = agents
        self.a2a_overhead = a2a_overhead  # seconds per A2A package
        self.results = []

    def simulate_sequential(self, tasks: List[Task]) -> WorkflowMetrics:
        """
        Sequential pattern: Tasks execute one after another
        Good for: Simple pipelines, low-overhead workflows
        """
        start_time = time.time()
        total_cost = 0
        a2a_count = 0
        quality_scores = []

        for i, task in enumerate(tasks):
            # Select best agent
            agent = self._select_agent(task)

            # Execute task
            duration = task.duration / agent.processing_speed
            time.sleep(0)  # Simulated time

            # Add communication overhead for handoff
            if i > 0:
                duration += self.a2a_overhead
                a2a_count += 1

            total_cost += duration
            quality = self._compute_quality(agent, task)
            quality_scores.append(quality)

        completion_time = total_cost
        communication_overhead = a2a_count * self.a2a_overhead

        return WorkflowMetrics(
            completion_time=completion_time,
            total_cost=total_cost,
            quality_score=np.mean(quality_scores),
            success_rate=sum(1 for q in quality_scores if q >= task.quality_requirement) / len(quality_scores),
            agent_utilization=1.0 / len(self.agents),  # Only one agent active
            communication_overhead=communication_overhead,
            memory_usage=sum(task.data_size for task in tasks),
            a2a_packages_sent=a2a_count
        )

    def simulate_parallel(self, tasks: List[Task], aggregation: str = 'majority') -> WorkflowMetrics:
        """
        Parallel pattern: Tasks execute simultaneously
        Good for: Independent processing, redundancy
        """
        start_time = time.time()

        # Group tasks by independence (no dependencies)
        independent_groups = self._group_independent_tasks(tasks)

        max_duration = 0
        total_cost = 0
        a2a_count = 0
        quality_scores = []

        for group in independent_groups:
            group_duration = 0
            group_quality = []

            # Execute tasks in parallel (simulated)
            for task in group:
                agent = self._select_agent(task)
                duration = task.duration / agent.processing_speed
                group_duration = max(group_duration, duration)
                quality = self._compute_quality(agent, task)
                group_quality.append(quality)
                total_cost += duration
                a2a_count += 1

            max_duration += group_duration
            quality_scores.extend(group_quality)

        # Aggregation overhead
        aggregation_time = len(independent_groups) * self.a2a_overhead * 2
        max_duration += aggregation_time
        a2a_count += len(independent_groups) * 2

        return WorkflowMetrics(
            completion_time=max_duration,
            total_cost=total_cost,
            quality_score=self._aggregate_quality(quality_scores, aggregation),
            success_rate=sum(1 for q in quality_scores if q >= 0.9) / len(quality_scores),
            agent_utilization=len(tasks) / len(self.agents),
            communication_overhead=a2a_count * self.a2a_overhead,
            memory_usage=sum(task.data_size for task in tasks),
            a2a_packages_sent=a2a_count
        )

    def simulate_hierarchical(self, tasks: List[Task], levels: int = 3, fan_out: int = 5) -> WorkflowMetrics:
        """
        Hierarchical pattern: Tree-based coordination
        Good for: Large-scale workflows, clear authority structure
        """
        start_time = time.time()

        # Organize tasks into hierarchy
        hierarchy = self._build_hierarchy(tasks, levels, fan_out)

        total_time = 0
        total_cost = 0
        a2a_count = 0
        quality_scores = []

        # Simulate hierarchical processing
        def process_level(level_tasks, level):
            nonlocal total_time, total_cost, a2a_count
            level_time = 0
            level_quality = []

            if level == levels - 1:
                # Leaf level - execute tasks
                for task in level_tasks:
                    agent = self._select_agent(task)
                    duration = task.duration / agent.processing_speed
                    level_time = max(level_time, duration)
                    quality = self._compute_quality(agent, task)
                    level_quality.append(quality)
                    total_cost += duration
                    a2a_count += 1
            else:
                # Intermediate level - coordinate children
                num_children = min(fan_out, len(level_tasks))
                child_time = 0
                for i in range(0, len(level_tasks), fan_out):
                    child_tasks = level_tasks[i:i+fan_out]
                    child_duration, child_quality = process_level(child_tasks, level + 1)
                    child_time = max(child_time, child_duration)
                    level_quality.extend(child_quality)

                level_time = child_time + self.a2a_overhead  # Coordination overhead
                a2a_count += num_children

            return level_time, level_quality

        total_time, quality_scores = process_level(tasks, 0)

        return WorkflowMetrics(
            completion_time=total_time,
            total_cost=total_cost,
            quality_score=np.mean(quality_scores) if quality_scores else 0,
            success_rate=sum(1 for q in quality_scores if q >= 0.9) / len(quality_scores) if quality_scores else 0,
            agent_utilization=len(tasks) / (fan_out ** levels),
            communication_overhead=a2a_count * self.a2a_overhead,
            memory_usage=sum(task.data_size for task in tasks) * 0.7,  # Shared memory
            a2a_packages_sent=a2a_count
        )

    def simulate_map_reduce(self, tasks: List[Task], mappers: int = 5,
                           reducers: int = 3, chunk_size: int = 10) -> WorkflowMetrics:
        """
        Map-Reduce pattern: Distribute processing, then aggregate
        Good for: Data processing, batch operations
        """
        start_time = time.time()

        # Map phase: Distribute tasks to mappers
        chunks = [tasks[i:i+chunk_size] for i in range(0, len(tasks), chunk_size)]

        map_times = []
        map_quality = []
        a2a_count = 0

        # Simulate map phase
        for chunk in chunks:
            chunk_time = 0
            for task in chunk:
                agent = self._select_agent(task)
                duration = task.duration / agent.processing_speed
                chunk_time = max(chunk_time, duration)
                quality = self._compute_quality(agent, task)
                map_quality.append(quality)
                a2a_count += 1

            map_times.append(chunk_time)

        map_phase_time = max(map_times) if map_times else 0

        # Shuffle phase: Redistribute data
        shuffle_time = len(chunks) * self.a2a_overhead
        a2a_count += len(chunks)

        # Reduce phase: Aggregate results
        reduce_time = len(chunks) * self.a2a_overhead / reducers
        reduce_quality = [np.mean(map_quality[i::reducers]) for i in range(reducers)]
        a2a_count += reducers

        total_time = map_phase_time + shuffle_time + reduce_time

        return WorkflowMetrics(
            completion_time=total_time,
            total_cost=sum(map_times) + reduce_time,
            quality_score=np.mean(map_quality) if map_quality else 0,
            success_rate=sum(1 for q in map_quality if q >= 0.9) / len(map_quality) if map_quality else 0,
            agent_utilization=len(tasks) / mappers,
            communication_overhead=a2a_count * self.a2a_overhead,
            memory_usage=sum(task.data_size for task in tasks) * 1.5,  # Duplication
            a2a_packages_sent=a2a_count
        )

    def _select_agent(self, task: Task) -> AgentConfig:
        """Select best agent for task based on complexity"""
        # Higher complexity requires specialized agents
        if task.complexity > 0.7:
            candidates = [a for a in self.agents if a.agent_type == 'role']
        elif task.complexity > 0.4:
            candidates = [a for a in self.agents if a.agent_type in ['core', 'role']]
        else:
            candidates = self.agents

        # Select fastest available
        return max(candidates, key=lambda a: a.processing_speed)

    def _compute_quality(self, agent: AgentConfig, task: Task) -> float:
        """Compute task quality score based on agent and task"""
        base_quality = agent.reliability

        # Complexity penalty
        complexity_penalty = task.complexity * 0.1

        # Quality requirement penalty
        requirement_penalty = abs(task.quality_requirement - base_quality) * 0.2

        quality = base_quality - complexity_penalty - requirement_penalty
        return max(0, min(1, quality))

    def _aggregate_quality(self, qualities: List[float], method: str) -> float:
        """Aggregate quality scores from parallel executions"""
        if not qualities:
            return 0.0

        if method == 'majority':
            return np.median(qualities)
        elif method == 'mean':
            return np.mean(qualities)
        elif method == 'max':
            return max(qualities)
        elif method == 'min':
            return min(qualities)
        else:
            return np.mean(qualities)

    def _group_independent_tasks(self, tasks: List[Task]) -> List[List[Task]]:
        """Group tasks that can be executed in parallel"""
        # Simple approach: group tasks with no dependencies
        independent = []
        current_group = []
        seen = set()

        for task in tasks:
            if not any(dep in seen for dep in task.dependencies):
                current_group.append(task)
                seen.add(task.id)
            else:
                if current_group:
                    independent.append(current_group)
                current_group = [task]
                seen = {task.id}

        if current_group:
            independent.append(current_group)

        return independent if independent else [tasks]

    def _build_hierarchy(self, tasks: List[Task], levels: int, fan_out: int) -> Dict:
        """Build hierarchical task structure"""
        return {
            'levels': levels,
            'fan_out': fan_out,
            'tasks': tasks
        }


class WorkflowPatternOptimizer:
    """Optimizes workflow pattern selection based on task characteristics"""

    def __init__(self, simulator: WorkflowSimulator):
        self.simulator = simulator
        self.pattern_performance = {}

    def find_optimal_pattern(self, tasks: List[Task], iterations: int = 10) -> Tuple[PatternType, WorkflowMetrics]:
        """Test all patterns and return best performing"""
        results = {}

        for _ in range(iterations):
            # Test sequential
            results[PatternType.SEQUENTIAL] = self.simulator.simulate_sequential(tasks)

            # Test parallel
            results[PatternType.PARALLEL] = self.simulator.simulate_parallel(tasks)

            # Test hierarchical
            results[PatternType.HIERARCHICAL] = self.simulator.simulate_hierarchical(tasks)

            # Test map-reduce
            results[PatternType.MAP_REDUCE] = self.simulator.simulate_map_reduce(tasks)

        # Select best based on weighted score
        best_pattern = min(results.items(), key=lambda x: self._compute_score(x[1]))
        return best_pattern

    def _compute_score(self, metrics: WorkflowMetrics) -> float:
        """Compute composite score (lower is better)"""
        # Weight factors
        time_weight = 1.0
        cost_weight = 0.5
        quality_weight = -2.0  # Negative because higher is better
        reliability_weight = -1.0

        score = (
            time_weight * metrics.completion_time +
            cost_weight * metrics.total_cost +
            quality_weight * metrics.quality_score +
            reliability_weight * metrics.success_rate
        )
        return score


# Example usage and testing
def create_sample_workflows() -> Dict[str, List[Task]]:
    """Create sample workflow scenarios"""
    return {
        'data_pipeline': [
            Task('t1', 'Extract', 2.0, 0.3, data_size=10),
            Task('t2', 'Transform', 3.0, 0.6, ['t1'], data_size=8),
            Task('t3', 'Validate', 1.0, 0.4, ['t2'], data_size=8),
            Task('t4', 'Load', 2.5, 0.5, ['t3'], data_size=6),
        ],
        'code_review': [
            Task('t1', 'Static Analysis', 1.5, 0.4),
            Task('t2', 'Security Check', 2.0, 0.7),
            Task('t3', 'Performance Review', 1.8, 0.6),
            Task('t4', 'Style Check', 1.0, 0.3),
            Task('t5', 'Documentation Review', 2.5, 0.5),
        ],
        'research_task': [
            Task(f't{i}', f'Search Query {i}', 1.0 + i*0.2, 0.4)
            for i in range(20)
        ],
        'complex_workflow': [
            Task('t1', 'Initialize', 1.0, 0.2),
            Task('t2', 'Fetch Data', 3.0, 0.5, ['t1']),
            Task('t3', 'Process A', 2.0, 0.6, ['t2']),
            Task('t4', 'Process B', 2.5, 0.7, ['t2']),
            Task('t5', 'Process C', 1.8, 0.5, ['t2']),
            Task('t6', 'Merge Results', 1.5, 0.4, ['t3', 't4', 't5']),
            Task('t7', 'Validate', 2.0, 0.6, ['t6']),
            Task('t8', 'Deploy', 1.0, 0.3, ['t7']),
        ]
    }


def run_pattern_optimization():
    """Run workflow pattern optimization"""
    # Create agents
    agents = [
        AgentConfig('core', 1.0, 0.95, 0.001, 100),
        AgentConfig('role', 1.2, 0.90, 0.0015, 150),
        AgentConfig('task', 0.8, 0.85, 0.002, 50),
        AgentConfig('role', 1.3, 0.88, 0.0015, 120),
    ]

    simulator = WorkflowSimulator(agents)
    optimizer = WorkflowPatternOptimizer(simulator)

    workflows = create_sample_workflows()
    results = {}

    for name, tasks in workflows.items():
        print(f"\n{'='*60}")
        print(f"Optimizing workflow: {name}")
        print(f"{'='*60}")
        print(f"Tasks: {len(tasks)}")

        best_pattern, metrics = optimizer.find_optimal_pattern(tasks)

        print(f"\nOptimal pattern: {best_pattern.value}")
        print(f"Completion time: {metrics.completion_time:.2f}s")
        print(f"Quality score: {metrics.quality_score:.3f}")
        print(f"Success rate: {metrics.success_rate:.3f}")
        print(f"Agent utilization: {metrics.agent_utilization:.2f}")
        print(f"A2A packages: {metrics.a2a_packages_sent}")

        results[name] = {
            'pattern': best_pattern.value,
            'metrics': {
                'completion_time': metrics.completion_time,
                'quality_score': metrics.quality_score,
                'success_rate': metrics.success_rate,
                'agent_utilization': metrics.agent_utilization,
                'a2a_packages_sent': metrics.a2a_packages_sent,
            }
        }

    return results


if __name__ == '__main__':
    results = run_pattern_optimization()

    # Save results
    with open('simulation_results/pattern_optimization.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Pattern optimization complete!")
    print("Results saved to simulation_results/pattern_optimization.json")
