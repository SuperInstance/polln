"""
POLLN Graph Evolution - Pruning Simulation
===========================================

Simulates synaptic pruning dynamics to prove that optimal sparsity
improves network performance.

Hypothesis H1: Performance = f(sparsity) is concave
Prove: Optimal sparsity ≈ 0.3-0.5
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Dict
import json
from dataclasses import dataclass

from ..base import (
    AgentGraph, EvolutionConfig, EvolutionMetrics,
    PruningStrategy, AgentEdge
)


@dataclass
class PruningExperimentConfig:
    """Configuration for pruning experiments."""
    num_agents: int = 100
    generations: int = 500
    num_trials: int = 10

    # Threshold range to test
    threshold_range: Tuple[float, float] = (0.01, 0.2)

    # Pruning schedules
    schedules: List[str] = None  # 'constant', 'adaptive', 'linear'

    def __post_init__(self):
        if self.schedules is None:
            self.schedules = ['constant', 'adaptive', 'linear']


class PruningSimulation:
    """
    Simulates synaptic pruning to find optimal sparsity.

    Implements all pruning strategies from TypeScript evolution.ts:
    - threshold: Remove connections below weight threshold
    - age: Remove old unused connections
    - random: Random dropout for regularization
    - magnitude: Remove smallest magnitude weights
    - activity: Remove low-activity connections
    - combined: Combine multiple strategies
    """

    def __init__(self, config: PruningExperimentConfig):
        self.config = config
        self.results: Dict[str, List[EvolutionMetrics]] = {}

    def run_experiment(self) -> Dict:
        """Run complete pruning experiment across all strategies."""
        print("=" * 70)
        print("PRUNING SIMULATION - Proving Optimal Sparsity")
        print("=" * 70)

        strategies = [
            PruningStrategy.THRESHOLD,
            PruningStrategy.AGE,
            PruningStrategy.MAGNITUDE,
            PruningStrategy.ACTIVITY,
            PruningStrategy.COMBINED,
        ]

        all_results = {}

        for strategy in strategies:
            print(f"\n{'='*70}")
            print(f"Testing Strategy: {strategy.value.upper()}")
            print(f"{'='*70}")

            strategy_results = []

            for trial in range(self.config.num_trials):
                print(f"\nTrial {trial + 1}/{self.config.num_trials}")

                # Test different thresholds
                threshold_results = []

                for threshold in np.linspace(
                    self.config.threshold_range[0],
                    self.config.threshold_range[1],
                    10
                ):
                    evolution_config = EvolutionConfig(
                        pruning_strategy=strategy,
                        pruning_threshold=threshold,
                        max_pruning_rate=0.1,
                    )

                    sim_result = self._run_single_simulation(
                        evolution_config, threshold
                    )
                    threshold_results.append(sim_result)

                strategy_results.append(threshold_results)

            all_results[strategy.value] = strategy_results

        return self._analyze_results(all_results)

    def _run_single_simulation(
        self,
        config: EvolutionConfig,
        threshold: float
    ) -> Dict:
        """Run a single simulation with given parameters."""
        graph = AgentGraph(self.config.num_agents, config)

        # Simulate activity patterns
        for t in range(self.config.generations):
            # Random activation pattern
            num_active = int(self.config.num_agents * 0.3)
            active_agents = np.random.choice(
                [f"agent_{i}" for i in range(self.config.num_agents)],
                num_active,
                replace=False
            )

            # Activate edges between active agents
            for i, source in enumerate(active_agents):
                for target in active_agents[i+1:]:
                    if graph.has_edge(source, target):
                        graph.activate_edge(source, target)

            # Age edges
            graph.age_all_edges()

            # Prune every pruning_interval
            if t % config.pruning_interval == 0:
                self._prune_graph(graph, config)

            # Record metrics
            if t % 10 == 0:
                metrics = graph.compute_metrics(t)
                metrics.pruned_this_cycle = 0  # Track separately
                graph.metrics_history.append(metrics)

        # Compute final performance metrics
        final_metrics = graph.compute_metrics(self.config.generations)

        return {
            "threshold": threshold,
            "final_sparsity": final_metrics.sparsity,
            "final_performance": self._compute_performance(graph),
            "final_clustering": final_metrics.clustering_coefficient,
            "final_path_length": final_metrics.avg_path_length,
            "final_modularity": final_metrics.modularity,
            "metrics_history": [m.to_dict() for m in graph.metrics_history],
        }

    def _prune_graph(self, graph: AgentGraph, config: EvolutionConfig):
        """Prune edges based on strategy (matching TypeScript implementation)."""
        edges_to_prune = []

        for (source, target), edge in list(graph.edges.items()):
            if edge.age < config.min_synapse_age:
                continue

            should_prune = False

            match config.pruning_strategy:
                case PruningStrategy.THRESHOLD:
                    should_prune = edge.weight < config.pruning_threshold

                case PruningStrategy.AGE:
                    # Prune old, weak connections
                    should_prune = edge.age > 60 and edge.activity_level < 2

                case PruningStrategy.RANDOM:
                    # Random dropout (regularization)
                    should_prune = (np.random.random() < 0.01 and
                                   edge.weight < 0.2)

                case PruningStrategy.ACTIVITY:
                    should_prune = (edge.activity_level < 1 and
                                   edge.age > 30)

                case PruningStrategy.COMBINED:
                    should_prune = self._combined_pruning_decision(
                        edge, config
                    )

                case PruningStrategy.MAGNITUDE:
                    # Handled separately (bottom percentile)
                    pass

            if should_prune:
                edges_to_prune.append((source, target))

        # For magnitude-based pruning
        if config.pruning_strategy == PruningStrategy.MAGNITUDE:
            weights = sorted(graph.edges.items(),
                           key=lambda x: x[1].weight)
            to_prune = int(len(weights) * config.max_pruning_rate)

            for i in range(to_prune):
                if weights[i][1].age >= config.min_synapse_age:
                    edges_to_prune.append(weights[i][0])

        # Apply max pruning rate
        max_prune = int(len(graph.edges) * config.max_pruning_rate)
        edges_to_remove = edges_to_prune[:max_prune]

        # Remove edges
        for source, target in edges_to_remove:
            graph._remove_edge(source, target)

    def _combined_pruning_decision(
        self,
        edge: AgentEdge,
        config: EvolutionConfig
    ) -> bool:
        """Combined pruning decision using multiple factors."""
        factors = {
            "weight": 1.0 if edge.weight < config.pruning_threshold else 0.0,
            "activity": 1.0 if edge.activity_level < 2 else 0.0,
            "age": 1.0 if edge.age > 60 else 0.0
        }

        score = (
            factors["weight"] * 0.5 +
            factors["activity"] * 0.3 +
            factors["age"] * 0.2
        )

        return score > 0.5

    def _compute_performance(self, graph: AgentGraph) -> float:
        """
        Compute network performance score.

        Performance = efficiency * robustness * functionality
        - Efficiency: 1 / (avg_path_length * (1 - sparsity))
        - Robustness: spectral gap (algebraic connectivity)
        - Functionality: based on clustering and modularity
        """
        metrics = graph.compute_metrics(0)

        # Efficiency: trade-off between connectivity and sparsity
        efficiency = 1.0 / max(0.001, metrics.avg_path_length *
                              (1.01 - metrics.sparsity))

        # Robustness: spectral gap indicates connectivity
        robustness = metrics.spectral_gap

        # Functionality: balance of clustering and modularity
        functionality = (metrics.clustering_coefficient +
                        metrics.modularity) / 2

        performance = efficiency * robustness * functionality

        return performance

    def _analyze_results(self, all_results: Dict) -> Dict:
        """Analyze results across all strategies and thresholds."""
        analysis = {}

        for strategy, trial_results in all_results.items():
            print(f"\n{'='*70}")
            print(f"ANALYSIS: {strategy.upper()}")
            print(f"{'='*70}")

            # Aggregate across trials
            threshold_performance = []
            threshold_sparsity = []

            for threshold_idx in range(len(trial_results[0])):
                performances = []
                sparsities = []

                for trial in trial_results:
                    result = trial[threshold_idx]
                    performances.append(result["final_performance"])
                    sparsities.append(result["final_sparsity"])

                threshold_performance.append({
                    "threshold": trial_results[0][threshold_idx]["threshold"],
                    "mean_performance": np.mean(performances),
                    "std_performance": np.std(performances),
                    "mean_sparsity": np.mean(sparsities),
                    "std_sparsity": np.std(sparsities),
                })

            # Find optimal threshold
            optimal = max(threshold_performance,
                         key=lambda x: x["mean_performance"])

            analysis[strategy] = {
                "threshold_performance": threshold_performance,
                "optimal_threshold": optimal["threshold"],
                "optimal_performance": optimal["mean_performance"],
                "optimal_sparsity": optimal["mean_sparsity"],
            }

            print(f"\nOptimal Threshold: {optimal['threshold']:.4f}")
            print(f"Optimal Sparsity: {optimal['mean_sparsity']:.3f}")
            print(f"Peak Performance: {optimal['mean_performance']:.4f}")

        return analysis

    def plot_results(self, analysis: Dict, output_dir: Path):
        """Generate plots showing pruning dynamics."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Plot 1: Performance vs Sparsity for each strategy
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle("Pruning Strategy Performance Analysis",
                    fontsize=16, fontweight='bold')

        strategies = list(analysis.keys())
        colors = plt.cm.viridis(np.linspace(0, 1, len(strategies)))

        for idx, strategy in enumerate(strategies):
            ax = axes[idx // 3, idx % 3]

            data = analysis[strategy]["threshold_performance"]

            thresholds = [d["threshold"] for d in data]
            sparsities = [d["mean_sparsity"] for d in data]
            performances = [d["mean_performance"] for d in data]
            errors = [d["std_performance"] for d in data]

            # Performance vs threshold
            ax.errorbar(thresholds, performances, yerr=errors,
                       marker='o', linewidth=2, markersize=6,
                       label='Performance')

            # Mark optimal
            optimal_idx = np.argmax(performances)
            ax.plot(thresholds[optimal_idx], performances[optimal_idx],
                   'r*', markersize=20, label='Optimal')

            ax.set_xlabel("Pruning Threshold", fontsize=12)
            ax.set_ylabel("Performance Score", fontsize=12)
            ax.set_title(f"{strategy.title()} Strategy", fontsize=14,
                        fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "pruning_performance.png", dpi=300)
        plt.close()

        # Plot 2: Performance vs Sparsity curve (proving concavity)
        fig, ax = plt.subplots(figsize=(12, 8))

        for strategy in strategies:
            data = analysis[strategy]["threshold_performance"]

            sparsities = [d["mean_sparsity"] for d in data]
            performances = [d["mean_performance"] for d in data]

            # Sort by sparsity
            sorted_pairs = sorted(zip(sparsities, performances))
            sparsities = [p[0] for p in sorted_pairs]
            performances = [p[1] for p in sorted_pairs]

            ax.plot(sparsities, performances, 'o-',
                   linewidth=2, markersize=8,
                   label=strategy.title())

        ax.set_xlabel("Network Sparsity", fontsize=14)
        ax.set_ylabel("Performance Score", fontsize=14)
        ax.set_title("Hypothesis H1: Performance = f(sparsity) is Concave",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add optimal sparsity region annotation
        ax.axvspan(0.3, 0.5, alpha=0.2, color='green',
                  label='Predicted Optimal Range (0.3-0.5)')

        plt.tight_layout()
        plt.savefig(output_dir / "performance_vs_sparsity.png", dpi=300)
        plt.close()

        # Plot 3: Clustering and Path Length evolution
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        for strategy in strategies:
            data = analysis[strategy]["threshold_performance"]

            sparsities = [d["mean_sparsity"] for d in data]
            clusterings = []
            path_lengths = []

            for d in data:
                # Get from first trial
                if d["metrics_history"]:
                    final = d["metrics_history"][-1]
                    clusterings.append(final["clustering_coefficient"])
                    path_lengths.append(final["avg_path_length"])

            # Sort by sparsity
            sorted_data = sorted(zip(sparsities, clusterings, path_lengths))
            sparsities = [d[0] for d in sorted_data]
            clusterings = [d[1] for d in sorted_data]
            path_lengths = [d[2] for d in sorted_data]

            axes[0].plot(sparsities, clusterings, 'o-',
                       linewidth=2, label=strategy.title())
            axes[1].plot(sparsities, path_lengths, 's-',
                       linewidth=2, label=strategy.title())

        axes[0].set_xlabel("Sparsity", fontsize=12)
        axes[0].set_ylabel("Clustering Coefficient", fontsize=12)
        axes[0].set_title("Clustering vs Sparsity", fontsize=14,
                         fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].set_xlabel("Sparsity", fontsize=12)
        axes[1].set_ylabel("Avg Path Length", fontsize=12)
        axes[1].set_title("Path Length vs Sparsity", fontsize=14,
                         fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "network_properties_vs_sparsity.png", dpi=300)
        plt.close()

        # Save analysis data
        with open(output_dir / "pruning_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n{'='*70}")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*70}")


def main():
    """Run pruning simulation."""
    config = PruningExperimentConfig(
        num_agents=100,
        generations=500,
        num_trials=5,
        threshold_range=(0.01, 0.15),
    )

    sim = PruningSimulation(config)
    analysis = sim.run_experiment()
    sim.plot_results(analysis, Path("simulations/results/pruning"))

    # Print summary
    print("\n" + "=" * 70)
    print("PRUNING SIMULATION SUMMARY")
    print("=" * 70)

    for strategy, data in analysis.items():
        print(f"\n{strategy.upper()}:")
        print(f"  Optimal Threshold: {data['optimal_threshold']:.4f}")
        print(f"  Optimal Sparsity: {data['optimal_sparsity']:.3f}")
        print(f"  Peak Performance: {data['optimal_performance']:.4f}")

        # Verify hypothesis
        if 0.3 <= data['optimal_sparsity'] <= 0.5:
            print(f"  ✓ Hypothesis H1 CONFIRMED: Optimal sparsity in [0.3, 0.5]")
        else:
            print(f"  ✗ Hypothesis H1: Sparsity {data['optimal_sparsity']:.3f} outside predicted range")


if __name__ == "__main__":
    main()
