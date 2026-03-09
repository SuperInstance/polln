"""
POLLN Graph Evolution - Co-evolution Simulation
================================================

Simulates co-evolutionary dynamics between agent networks and
their environments to prove stable equilibrium conditions.

Agent graph ↔ Environment co-evolution:
- Agents adapt to tasks
- Tasks adapt to agents
- Red Queen effects
- Arms races

Hypothesis: Co-evolution converges to stable equilibrium
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple
import json
from dataclasses import dataclass
from enum import Enum

from ..base import AgentGraph, EvolutionConfig, EvolutionMetrics


class EnvironmentType(Enum):
    """Types of task environments."""
    STATIC = "static"              # Tasks don't change
    GRADUAL = "gradual"            # Slow changes
    DYNAMIC = "dynamic"            # Fast changes
    ADVERSARIAL = "adversarial"    # Counter-adapts to agents


@dataclass
class EnvironmentConfig:
    """Configuration for co-evolution environment."""
    env_type: EnvironmentType = EnvironmentType.GRADUAL
    num_tasks: int = 20
    adaptation_rate: float = 0.05  # How fast tasks adapt
    coupling_strength: float = 0.5  # How strongly env affects agents


class TaskEnvironment:
    """
    Simulates a task environment that co-evolves with agents.

    Tasks have requirements and difficulty.
    """

    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.tasks: Dict[str, Dict] = {}
        self.generation = 0

        # Initialize tasks
        for i in range(config.num_tasks):
            task_id = f"task_{i}"
            self.tasks[task_id] = {
                "requirements": np.random.random(8),  # 8 capability dimensions
                "difficulty": np.random.uniform(0.2, 0.8),
                "success_count": 0,
                "failure_count": 0,
            }

    def get_task_fitness(self, agent_capabilities: Dict[str, float]) -> float:
        """Compute how well an agent matches task requirements."""
        total_fitness = 0.0

        for task in self.tasks.values():
            req = task["requirements"]
            cap = np.array(list(agent_capabilities.values()))

            # Align dimensions
            if len(req) < len(cap):
                req = np.pad(req, (0, len(cap) - len(req)))
            elif len(req) > len(cap):
                cap = np.pad(cap, (0, len(req) - len(cap)))

            # Fitness = cosine similarity
            dot = np.dot(req, cap)
            norm_req = np.linalg.norm(req)
            norm_cap = np.linalg.norm(cap)

            if norm_req > 0 and norm_cap > 0:
                fitness = dot / (norm_req * norm_cap)
            else:
                fitness = 0.0

            # Modulate by difficulty
            fitness *= (1 - task["difficulty"] * 0.5)

            total_fitness += fitness

        return total_fitness / len(self.tasks)

    def adapt(self, agent_capabilities: Dict[str, float]):
        """
        Adapt tasks based on agent performance.

        This creates the co-evolutionary dynamic.
        """
        self.generation += 1

        match self.config.env_type:
            case EnvironmentType.STATIC:
                # No adaptation
                return

            case EnvironmentType.GRADUAL:
                # Slow drift
                for task in self.tasks.values():
                    noise = np.random.normal(0, self.config.adaptation_rate * 0.1,
                                           len(task["requirements"]))
                    task["requirements"] = np.clip(
                        task["requirements"] + noise, 0, 1
                    )

            case EnvironmentType.DYNAMIC:
                # Fast changes
                for task in self.tasks.values():
                    noise = np.random.normal(0, self.config.adaptation_rate * 0.3,
                                           len(task["requirements"]))
                    task["requirements"] = np.clip(
                        task["requirements"] + noise, 0, 1
                    )

            case EnvironmentType.ADVERSARIAL:
                # Move away from agent capabilities (Red Queen)
                caps_array = np.array(list(agent_capabilities.values()))

                for task in self.tasks.values():
                    # Compute distance from agent
                    req = task["requirements"]
                    if len(req) < len(caps_array):
                        caps_array = caps_array[:len(req)]
                    elif len(req) > len(caps_array):
                        caps_array = np.pad(caps_array, (0, len(req) - len(caps_array)))

                    # Move requirements away from agent (negative feedback)
                    direction = req - caps_array
                    direction = direction / (np.linalg.norm(direction) + 0.001)

                    task["requirements"] = np.clip(
                        req + direction * self.config.adaptation_rate,
                        0, 1
                    )


class CoevolutionSimulation:
    """
    Simulates co-evolution between agent networks and environments.

    Proves:
    - Stable equilibrium conditions
    - Red Queen effects (running to stay in place)
    - Arms race dynamics
    - Adaptive coupling benefits
    """

    def __init__(
        self,
        num_agents: int = 100,
        generations: int = 500,
        num_trials: int = 10
    ):
        self.num_agents = num_agents
        self.generations = generations
        self.num_trials = num_trials
        self.results: Dict[str, List[Dict]] = {}

    def run_experiment(self) -> Dict:
        """Run co-evolution experiment across environment types."""
        print("=" * 70)
        print("CO-EVOLUTION SIMULATION - Agent-Environment Dynamics")
        print("=" * 70)

        env_types = [
            EnvironmentType.STATIC,
            EnvironmentType.GRADUAL,
            EnvironmentType.DYNAMIC,
            EnvironmentType.ADVERSARIAL,
        ]

        all_results = {}

        for env_type in env_types:
            print(f"\n{'='*70}")
            print(f"Testing Environment: {env_type.value.upper()}")
            print(f"{'='*70}")

            env_results = []

            for trial in range(self.num_trials):
                print(f"\nTrial {trial + 1}/{self.num_trials}")

                result = self._run_single_simulation(env_type)
                env_results.append(result)

            all_results[env_type.value] = env_results

        return self._analyze_results(all_results)

    def _run_single_simulation(
        self,
        env_type: EnvironmentType
    ) -> Dict:
        """Run single co-evolution simulation."""
        # Initialize
        env_config = EnvironmentConfig(
            env_type=env_type,
            num_tasks=20,
            adaptation_rate=0.05,
            coupling_strength=0.5,
        )

        env = TaskEnvironment(env_config)
        graph = AgentGraph(self.num_agents, EvolutionConfig())

        # Track co-evolution metrics
        agent_fitness_history = []
        task_difficulty_history = []
        diversity_history = []
        coupling_history = []

        # Evolution loop
        for t in range(self.generations):
            # Compute average agent fitness
            agent_fitnesses = []
            for agent_id, node in graph.nodes.items():
                fitness = env.get_task_fitness(node.capabilities)
                agent_fitnesses.append(fitness)

            avg_fitness = np.mean(agent_fitnesses)

            # Agents adapt to environment (selection)
            if t % 10 == 0:
                self._adapt_agents(graph, env)

            # Environment adapts to agents
            if t % 5 == 0:
                # Use average agent capabilities for environment adaptation
                avg_caps = self._compute_average_capabilities(graph)
                env.adapt(avg_caps)

            # Record metrics
            if t % 5 == 0:
                agent_fitness_history.append(avg_fitness)

                avg_difficulty = np.mean([
                    t["difficulty"] for t in env.tasks.values()
                ])
                task_difficulty_history.append(avg_difficulty)

                diversity = self._compute_diversity(graph)
                diversity_history.append(diversity)

                coupling = self._compute_coupling(graph, env)
                coupling_history.append(coupling)

        # Compute final metrics
        final_metrics = {
            "avg_fitness": np.mean(agent_fitness_history[-50:]),
            "fitness_variance": np.var(agent_fitness_history[-50:]),
            "avg_difficulty": np.mean(task_difficulty_history[-50:]),
            "final_diversity": diversity_history[-1],
            "final_coupling": coupling_history[-1],
            "fitness_history": agent_fitness_history,
            "difficulty_history": task_difficulty_history,
            "diversity_history": diversity_history,
            "coupling_history": coupling_history,
            "converged": self._check_convergence(agent_fitness_history),
            "equilibrium_stability": self._compute_stability(agent_fitness_history),
        }

        return final_metrics

    def _adapt_agents(self, graph: AgentGraph, env: TaskEnvironment):
        """Adapt agent capabilities to environment (Hebbian-inspired)."""
        for agent_id, node in graph.nodes.items():
            current_fitness = env.get_task_fitness(node.capabilities)

            # Find direction of improvement
            gradient = {}
            learning_rate = 0.05

            for capability_name in node.capabilities.keys():
                # Test small perturbation
                original = node.capabilities[capability_name]

                node.capabilities[capability_name] = min(1.0, original + 0.1)
                fitness_plus = env.get_task_fitness(node.capabilities)

                node.capabilities[capability_name] = max(0.0, original - 0.1)
                fitness_minus = env.get_task_fitness(node.capabilities)

                # Restore
                node.capabilities[capability_name] = original

                # Numerical gradient
                grad = (fitness_plus - fitness_minus) / 0.2
                gradient[capability_name] = grad

            # Apply gradient
            for name, grad in gradient.items():
                node.capabilities[name] = np.clip(
                    node.capabilities[name] + learning_rate * grad,
                    0, 1
                )

    def _compute_average_capabilities(self, graph: AgentGraph) -> Dict[str, float]:
        """Compute average capabilities across all agents."""
        all_names = set()
        for node in graph.nodes.values():
            all_names.update(node.capabilities.keys())

        avg_caps = {}
        for name in all_names:
            values = [node.capabilities.get(name, 0) for node in graph.nodes.values()]
            avg_caps[name] = np.mean(values)

        return avg_caps

    def _compute_diversity(self, graph: AgentGraph) -> float:
        """Compute diversity of agent capabilities."""
        if len(graph.nodes) < 2:
            return 0.0

        # Compute pairwise distances
        distances = []
        agents = list(graph.nodes.values())

        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                caps1 = np.array(list(agents[i].capabilities.values()))
                caps2 = np.array(list(agents[j].capabilities.values()))

                # Euclidean distance
                dist = np.linalg.norm(caps1 - caps2)
                distances.append(dist)

        return np.mean(distances) if distances else 0.0

    def _compute_coupling(self, graph: AgentGraph, env: TaskEnvironment) -> float:
        """Compute coupling strength between agents and environment."""
        # High coupling = agents are well-matched to tasks
        fitnesses = []
        for node in graph.nodes.values():
            fitness = env.get_task_fitness(node.capabilities)
            fitnesses.append(fitness)

        return np.mean(fitnesses)

    def _check_convergence(self, history: List[float], window: int = 50) -> bool:
        """Check if system has converged."""
        if len(history) < window:
            return False

        recent = history[-window:]
        variance = np.var(recent)

        return variance < 0.01  # Low variance = converged

    def _compute_stability(self, history: List[float]) -> float:
        """Compute stability metric (inverse of recent variance)."""
        if len(history) < 50:
            return 0.0

        recent = history[-50:]
        variance = np.var(recent)

        return 1.0 / (1.0 + variance)

    def _analyze_results(self, all_results: Dict) -> Dict:
        """Analyze co-evolution results."""
        analysis = {}

        for env_type, results in all_results.items():
            print(f"\n{'='*70}")
            print(f"ANALYSIS: {env_type.upper()}")
            print(f"{'='*70}")

            # Aggregate metrics
            avg_fitness = np.mean([r["avg_fitness"] for r in results])
            avg_diversity = np.mean([r["final_diversity"] for r in results])
            avg_stability = np.mean([r["equilibrium_stability"] for r in results])
            convergence_rate = np.mean([r["converged"] for r in results])

            print(f"  Average Fitness: {avg_fitness:.4f}")
            print(f"  Diversity: {avg_diversity:.4f}")
            print(f"  Stability: {avg_stability:.4f}")
            print(f"  Convergence Rate: {convergence_rate:.2%}")

            # Analyze dynamics
            fitness_changes = []
            for r in results:
                if len(r["fitness_history"]) > 100:
                    early = np.mean(r["fitness_history"][:50])
                    late = np.mean(r["fitness_history"][-50:])
                    change = (late - early) / max(abs(early), 0.001)
                    fitness_changes.append(change)

            avg_improvement = np.mean(fitness_changes) if fitness_changes else 0.0

            analysis[env_type] = {
                "avg_fitness": avg_fitness,
                "avg_diversity": avg_diversity,
                "avg_stability": avg_stability,
                "convergence_rate": convergence_rate,
                "avg_improvement": avg_improvement,
                "individual_results": results,
            }

        return analysis

    def plot_results(self, analysis: Dict, output_dir: Path):
        """Generate plots showing co-evolution dynamics."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        env_types = list(analysis.keys())
        colors = {
            "static": "green",
            "gradual": "blue",
            "dynamic": "orange",
            "adversarial": "red",
        }

        # Plot 1: Fitness evolution over time (averaged)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Co-evolution Dynamics: Fitness Evolution",
                    fontsize=16, fontweight='bold')

        for idx, env_type in enumerate(env_types):
            ax = axes[idx // 2, idx % 2]

            # Average fitness histories across trials
            results = analysis[env_type]["individual_results"]

            # Find max length
            max_len = max(len(r["fitness_history"]) for r in results)

            # Pad and average
            summed = np.zeros(max_len)
            count = np.zeros(max_len)

            for r in results:
                hist = np.array(r["fitness_history"])
                summed[:len(hist)] += hist
                count[:len(hist)] += 1

            avg_history = summed / np.maximum(count, 1)

            generations = np.arange(len(avg_history))
            ax.plot(generations, avg_history,
                   color=colors.get(env_type, "gray"),
                   linewidth=2, label=env_type.title())

            # Add convergence marker
            converged_trials = sum(1 for r in results if r["converged"])
            total_trials = len(results)
            convergence_rate = converged_trials / total_trials

            ax.set_xlabel("Generation", fontsize=12)
            ax.set_ylabel("Average Fitness", fontsize=12)
            ax.set_title(f"{env_type.title()} Environment\n"
                        f"Convergence: {convergence_rate:.1%}",
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()

        plt.tight_layout()
        plt.savefig(output_dir / "coevolution_fitness.png", dpi=300)
        plt.close()

        # Plot 2: Diversity evolution
        fig, ax = plt.subplots(figsize=(12, 8))

        for env_type in env_types:
            results = analysis[env_type]["individual_results"]

            max_len = max(len(r["diversity_history"]) for r in results)

            summed = np.zeros(max_len)
            count = np.zeros(max_len)

            for r in results:
                hist = np.array(r["diversity_history"])
                summed[:len(hist)] += hist
                count[:len(hist)] += 1

            avg_history = summed / np.maximum(count, 1)

            generations = np.arange(len(avg_history))
            ax.plot(generations, avg_history,
                   color=colors.get(env_type, "gray"),
                   linewidth=2, label=env_type.title())

        ax.set_xlabel("Generation", fontsize=14)
        ax.set_ylabel("Agent Diversity", fontsize=14)
        ax.set_title("Diversity Evolution (Robustness Indicator)",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "coevolution_diversity.png", dpi=300)
        plt.close()

        # Plot 3: Stability and convergence comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        stabilities = [analysis[env]["avg_stability"] for env in env_types]
        convergence_rates = [analysis[env]["convergence_rate"] for env in env_types]

        bars1 = ax1.bar(env_types, stabilities,
                       color=[colors.get(e, "gray") for e in env_types],
                       alpha=0.8, edgecolor='black')
        ax1.set_ylabel("Equilibrium Stability", fontsize=14)
        ax1.set_title("Stability Comparison", fontsize=14, fontweight='bold')
        ax1.grid(True, axis='y', alpha=0.3)
        ax1.set_xticklabels([e.title() for e in env_types], rotation=45)

        for bar, stab in zip(bars1, stabilities):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f"{stab:.3f}", ha='center', va='bottom',
                    fontsize=11, fontweight='bold')

        bars2 = ax2.bar(env_types, [c * 100 for c in convergence_rates],
                       color=[colors.get(e, "gray") for e in env_types],
                       alpha=0.8, edgecolor='black')
        ax2.set_ylabel("Convergence Rate (%)", fontsize=14)
        ax2.set_title("Convergence Comparison", fontsize=14, fontweight='bold')
        ax2.grid(True, axis='y', alpha=0.3)
        ax2.set_xticklabels([e.title() for e in env_types], rotation=45)
        ax2.set_ylim(0, 100)

        for bar, rate in zip(bars2, convergence_rates):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f"{rate*100:.1f}%", ha='center', va='bottom',
                    fontsize=11, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / "coevolution_stability.png", dpi=300)
        plt.close()

        # Plot 4: Phase space (Diversity vs Fitness)
        fig, ax = plt.subplots(figsize=(12, 8))

        for env_type in env_types:
            results = analysis[env_type]["individual_results"]

            # Scatter points for each trial
            final_diversities = [r["final_diversity"] for r in results]
            final_fitnesses = [r["avg_fitness"] for r in results]

            ax.scatter(final_diversities, final_fitnesses,
                      color=colors.get(env_type, "gray"),
                      label=env_type.title(),
                      s=100, alpha=0.6, edgecolors='black')

            # Add mean marker
            mean_div = np.mean(final_diversities)
            mean_fit = np.mean(final_fitnesses)
            ax.plot(mean_div, mean_fit, '*',
                   color=colors.get(env_type, "gray"),
                   markersize=20, markeredgecolor='black',
                   markeredgewidth=2)

        ax.set_xlabel("Agent Diversity", fontsize=14)
        ax.set_ylabel("Average Fitness", fontsize=14)
        ax.set_title("Phase Space: Diversity vs Fitness",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add optimal region annotation
        ax.annotate('Optimal Region\n(High Diversity,\nHigh Fitness)',
                   xy=(0.4, 0.6), fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

        plt.tight_layout()
        plt.savefig(output_dir / "coevolution_phasespace.png", dpi=300)
        plt.close()

        # Save analysis
        with open(output_dir / "coevolution_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*70}")


def main():
    """Run co-evolution simulation."""
    sim = CoevolutionSimulation(
        num_agents=100,
        generations=500,
        num_trials=10
    )

    analysis = sim.run_experiment()
    sim.plot_results(analysis, Path("simulations/results/coevolution"))

    # Summary
    print("\n" + "=" * 70)
    print("CO-EVOLUTION SIMULATION SUMMARY")
    print("=" * 70)

    for env_type, data in analysis.items():
        print(f"\n{env_type.upper()}:")
        print(f"  Average Fitness: {data['avg_fitness']:.4f}")
        print(f"  Diversity: {data['avg_diversity']:.4f}")
        print(f"  Stability: {data['avg_stability']:.4f}")
        print(f"  Convergence Rate: {data['convergence_rate']:.2%}")
        print(f"  Improvement: {data['avg_improvement']:.2%}")


if __name__ == "__main__":
    main()
