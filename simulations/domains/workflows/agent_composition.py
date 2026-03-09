"""
Agent Composition Simulation for POLLN
Optimizes team composition for different task types
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class StrategyType(Enum):
    GENERALIST = "generalist"
    SPECIALIST = "specialist"
    HYBRID = "hybrid"


@dataclass
class TaskType:
    """Type of task with specific requirements"""
    name: str
    complexity: float  # 0-1
    diversity: float  # 0-1, how many different skills needed
    volume: float  # 0-1, total workload
    reliability_req: float  # 0-1


@dataclass
class AgentProfile:
    """Agent profile with capabilities"""
    id: str
    agent_type: str  # 'core', 'role', 'task'
    capabilities: List[str]  # List of skills
    proficiency: Dict[str, float]  # skill -> proficiency mapping
    processing_speed: float
    reliability: float
    communication_cost: float


@dataclass
class TeamConfig:
    """Team composition configuration"""
    strategy: StrategyType
    core_agents: int
    role_agents: int
    task_agents: int
    generalist_ratio: float = 0.5  # For hybrid strategy


@dataclass
class TeamMetrics:
    """Team performance metrics"""
    completion_time: float
    quality_score: float
    cost_efficiency: float  # work per unit cost
    redundancy: float  # backup capability
    adaptability: float  # ability to handle diverse tasks
    coordination_overhead: float
    total_cost: float


class AgentTeamSimulator:
    """Simulates different team compositions"""

    def __init__(self):
        self.agents = self._create_agent_pool()
        self.results = []

    def _create_agent_pool(self) -> List[AgentProfile]:
        """Create pool of available agents"""
        agents = []

        # Core agents (generalists)
        for i in range(10):
            agents.append(AgentProfile(
                id=f"core_{i}",
                agent_type="core",
                capabilities=["analysis", "processing", "coordination", "learning"],
                proficiency={
                    "analysis": 0.7 + np.random.normal(0, 0.1),
                    "processing": 0.7 + np.random.normal(0, 0.1),
                    "coordination": 0.8 + np.random.normal(0, 0.1),
                    "learning": 0.7 + np.random.normal(0, 0.1),
                },
                processing_speed=1.0,
                reliability=0.95,
                communication_cost=0.001
            ))

        # Role agents (specialists)
        specializations = [
            "data_processing", "analysis", "validation", "coordination",
            "monitoring", "optimization", "security", "quality_assurance"
        ]
        for spec in specializations:
            for i in range(5):
                agents.append(AgentProfile(
                    id=f"role_{spec}_{i}",
                    agent_type="role",
                    capabilities=[spec, "coordination"],
                    proficiency={
                        spec: 0.9 + np.random.normal(0, 0.05),
                        "coordination": 0.6 + np.random.normal(0, 0.1),
                    },
                    processing_speed=1.2,
                    reliability=0.90,
                    communication_cost=0.0015
                ))

        # Task agents (temporary, single-purpose)
        for i in range(20):
            task_type = np.random.choice(["simple", "moderate", "complex"])
            agents.append(AgentProfile(
                id=f"task_{i}",
                agent_type="task",
                capabilities=["execution"],
                proficiency={"execution": 0.8 + np.random.normal(0, 0.1)},
                processing_speed=0.8,
                reliability=0.85,
                communication_cost=0.002
            ))

        return agents

    def create_team(self, config: TeamConfig) -> List[AgentProfile]:
        """Create team based on configuration"""
        team = []

        if config.strategy == StrategyType.GENERALIST:
            # Mostly core agents
            core_pool = [a for a in self.agents if a.agent_type == "core"]
            team = list(np.random.choice(
                core_pool,
                min(config.core_agents, len(core_pool)),
                replace=False
            ))

        elif config.strategy == StrategyType.SPECIALIST:
            # Mostly role agents
            role_pool = [a for a in self.agents if a.agent_type == "role"]
            team = list(np.random.choice(
                role_pool,
                min(config.role_agents, len(role_pool)),
                replace=False
            ))

        elif config.strategy == StrategyType.HYBRID:
            # Mix of core and role agents
            core_pool = [a for a in self.agents if a.agent_type == "core"]
            role_pool = [a for a in self.agents if a.agent_type == "role"]

            num_core = int(config.core_agents * config.generalist_ratio)
            num_role = config.role_agents - num_core

            team = list(np.random.choice(
                core_pool,
                min(num_core, len(core_pool)),
                replace=False
            ))
            team.extend(list(np.random.choice(
                role_pool,
                min(num_role, len(role_pool)),
                replace=False
            )))

        return team

    def simulate_team_performance(
        self,
        team: List[AgentProfile],
        task_type: TaskType,
        num_tasks: int = 100
    ) -> TeamMetrics:
        """Simulate team performance on task type"""
        total_time = 0
        total_quality = 0
        total_coordination = 0
        completed_tasks = 0

        for _ in range(num_tasks):
            # Assign tasks to agents
            assignments = self._assign_tasks(team, task_type)

            # Simulate execution
            task_time, task_quality, coord_cost = self._execute_tasks(
                assignments, task_type
            )

            total_time += task_time
            total_quality += task_quality
            total_coordination += coord_cost

            if task_quality > 0.7:  # Quality threshold
                completed_tasks += 1

        # Compute metrics
        avg_time = total_time / num_tasks
        avg_quality = total_quality / num_tasks
        avg_coordination = total_coordination / num_tasks

        success_rate = completed_tasks / num_tasks
        cost_efficiency = (completed_tasks * task_type.volume) / (total_time * len(team))

        redundancy = self._compute_redundancy(team)
        adaptability = self._compute_adaptability(team, task_type)

        return TeamMetrics(
            completion_time=avg_time,
            quality_score=avg_quality,
            cost_efficiency=cost_efficiency,
            redundancy=redundancy,
            adaptability=adaptability,
            coordination_overhead=avg_coordination,
            total_cost=total_time
        )

    def _assign_tasks(self, team: List[AgentProfile], task_type: TaskType) -> Dict[str, AgentProfile]:
        """Assign tasks to agents based on capabilities"""
        assignments = {}
        team_copy = team.copy()

        for skill in self._get_required_skills(task_type):
            if not team_copy:
                break

            # Find best agent for skill
            best_agent = max(
                team_copy,
                key=lambda a: a.proficiency.get(skill, 0)
            )
            assignments[skill] = best_agent
            team_copy.remove(best_agent)

        return assignments

    def _get_required_skills(self, task_type: TaskType) -> List[str]:
        """Get required skills for task type"""
        base_skills = ["coordination"]

        if task_type.complexity > 0.7:
            base_skills.extend(["analysis", "processing", "validation"])
        elif task_type.complexity > 0.4:
            base_skills.extend(["analysis", "processing"])
        else:
            base_skills.append("execution")

        return base_skills

    def _execute_tasks(
        self,
        assignments: Dict[str, AgentProfile],
        task_type: TaskType
    ) -> Tuple[float, float, float]:
        """Execute assigned tasks and return metrics"""
        total_time = 0
        total_quality = 0
        coord_cost = 0

        for skill, agent in assignments.items():
            # Compute execution time
            base_time = task_type.complexity * 2.0
            execution_time = base_time / agent.processing_speed
            total_time += execution_time

            # Compute quality
            proficiency = agent.proficiency.get(skill, 0.5)
            quality = proficiency * agent.reliability
            total_quality += quality

            # Add coordination cost
            if len(assignments) > 1:
                coord_cost += agent.communication_cost

        return total_time / len(assignments), total_quality / len(assignments), coord_cost

    def _compute_redundancy(self, team: List[AgentProfile]) -> float:
        """Compute team redundancy (backup capability)"""
        if len(team) <= 1:
            return 0.0

        # Count agents with overlapping capabilities
        capability_counts = {}
        for agent in team:
            for cap in agent.capabilities:
                capability_counts[cap] = capability_counts.get(cap, 0) + 1

        # Average overlap
        overlaps = [count for count in capability_counts.values() if count > 1]
        return len(overlaps) / len(capability_counts) if capability_counts else 0.0

    def _compute_adaptability(self, team: List[AgentProfile], task_type: TaskType) -> float:
        """Compute team adaptability to diverse tasks"""
        # Diversity of capabilities
        unique_capabilities = set()
        for agent in team:
            unique_capabilities.update(agent.capabilities)

        diversity_score = len(unique_capabilities) / 10.0  # Normalize

        # Match to task requirements
        required_skills = set(self._get_required_skills(task_type))
        coverage = len(required_skills & unique_capabilities) / len(required_skills)

        return (diversity_score + coverage) / 2.0


class CompositionOptimizer:
    """Optimizes agent composition for task types"""

    def __init__(self, simulator: AgentTeamSimulator):
        self.simulator = simulator
        self.optimal_compositions = {}

    def optimize_for_task_type(
        self,
        task_type: TaskType,
        iterations: int = 50
    ) -> Tuple[TeamConfig, TeamMetrics]:
        """Find optimal team composition for task type"""
        best_config = None
        best_metrics = None
        best_score = float('inf')

        for _ in range(iterations):
            # Test different configurations
            for strategy in StrategyType:
                for team_size in range(3, 15):
                    config = self._generate_config(strategy, team_size)
                    team = self.simulator.create_team(config)
                    metrics = self.simulator.simulate_team_performance(team, task_type)

                    score = self._compute_score(metrics)
                    if score < best_score:
                        best_score = score
                        best_config = config
                        best_metrics = metrics

        return best_config, best_metrics

    def _generate_config(self, strategy: StrategyType, size: int) -> TeamConfig:
        """Generate team configuration"""
        if strategy == StrategyType.GENERALIST:
            return TeamConfig(strategy, size, 0, 0)
        elif strategy == StrategyType.SPECIALIST:
            return TeamConfig(strategy, 0, size, 0)
        else:  # HYBRID
            return TeamConfig(strategy, size//2, size//2, 0, generalist_ratio=0.3)

    def _compute_score(self, metrics: TeamMetrics) -> float:
        """Compute composite score (lower is better)"""
        time_weight = 1.0
        quality_weight = -2.0
        cost_weight = 0.5
        redundancy_weight = -0.3
        adaptability_weight = -0.2

        score = (
            time_weight * metrics.completion_time +
            quality_weight * metrics.quality_score +
            cost_weight / (metrics.cost_efficiency + 0.001) +
            redundancy_weight * metrics.redundancy +
            adaptability_weight * metrics.adaptability
        )
        return score


def run_composition_optimization():
    """Run agent composition optimization"""
    simulator = AgentTeamSimulator()
    optimizer = CompositionOptimizer(simulator)

    # Define task types
    task_types = [
        TaskType("simple_batch", 0.2, 0.1, 0.8, 0.7),  # High volume, simple
        TaskType("complex_analysis", 0.9, 0.8, 0.3, 0.95),  # Complex, diverse
        TaskType("mixed_workload", 0.5, 0.5, 0.6, 0.85),  # Mixed
        TaskType("critical_pipeline", 0.7, 0.4, 0.9, 0.98),  # Critical
        TaskType("research_tasks", 0.6, 0.9, 0.4, 0.8),  # Diverse skills
    ]

    results = {}

    for task_type in task_types:
        print(f"\n{'='*60}")
        print(f"Optimizing for: {task_type.name}")
        print(f"{'='*60}")
        print(f"Complexity: {task_type.complexity:.2f}")
        print(f"Diversity: {task_type.diversity:.2f}")
        print(f"Volume: {task_type.volume:.2f}")

        config, metrics = optimizer.optimize_for_task_type(task_type)

        print(f"\nOptimal configuration:")
        print(f"  Strategy: {config.strategy.value}")
        print(f"  Core agents: {config.core_agents}")
        print(f"  Role agents: {config.role_agents}")
        print(f"  Task agents: {config.task_agents}")

        print(f"\nPerformance:")
        print(f"  Completion time: {metrics.completion_time:.3f}s")
        print(f"  Quality score: {metrics.quality_score:.3f}")
        print(f"  Cost efficiency: {metrics.cost_efficiency:.3f}")
        print(f"  Redundancy: {metrics.redundancy:.3f}")
        print(f"  Adaptability: {metrics.adaptability:.3f}")

        results[task_type.name] = {
            'task_characteristics': {
                'complexity': task_type.complexity,
                'diversity': task_type.diversity,
                'volume': task_type.volume,
                'reliability_req': task_type.reliability_req,
            },
            'optimal_config': {
                'strategy': config.strategy.value,
                'core_agents': config.core_agents,
                'role_agents': config.role_agents,
                'task_agents': config.task_agents,
                'generalist_ratio': config.generalist_ratio,
            },
            'performance': {
                'completion_time': metrics.completion_time,
                'quality_score': metrics.quality_score,
                'cost_efficiency': metrics.cost_efficiency,
                'redundancy': metrics.redundancy,
                'adaptability': metrics.adaptability,
            }
        }

    return results


if __name__ == '__main__':
    results = run_composition_optimization()

    # Save results
    import os
    os.makedirs('simulation_results', exist_ok=True)
    with open('simulation_results/composition_optimization.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("Composition optimization complete!")
    print("Results saved to simulation_results/composition_optimization.json")
