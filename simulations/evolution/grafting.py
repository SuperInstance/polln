"""
POLLN Graph Evolution - Grafting Simulation
============================================

Simulates connection grafting (edge addition) to prove that
strategic connection formation improves network performance.

Compares different grafting heuristics:
- random: Random new connections
- similarity: Connect similar agents
- complementary: Connect complementary agents
- gradient: Follow performance gradient
- heuristic: Combined rule-based approach
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import json

from ..base import (
    AgentGraph, EvolutionConfig, EvolutionMetrics,
    GraftingStrategy
)


class GraftingSimulation:
    """
    Simulates connection grafting to discover optimal connection patterns.

    Implements grafting strategies from TypeScript evolution.ts
    to prove that intelligent grafting outperforms random addition.
    """

    def __init__(
        self,
        num_agents: int = 100,
        generations: int = 200,
        num_trials: int = 10
    ):
        self.num_agents = num_agents
        self.generations = generations
        self.num_trials = num_trials
        self.results: Dict[str, List[Dict]] = {}

    def run_experiment(self) -> Dict:
        """Run grafting experiment comparing all strategies."""
        print("=" * 70)
        print("GRAFTING SIMULATION - Discovering Optimal Connections")
        print("=" * 70)

        strategies = [
            GraftingStrategy.RANDOM,
            GraftingStrategy.SIMILARITY,
            GraftingStrategy.COMPLEMENTARY,
            GraftingStrategy.HEURISTIC,
        ]

        all_results = {}
        grafting_probs = [0.005, 0.01, 0.02, 0.05, 0.1]

        for strategy in strategies:
            print(f"\n{'='*70}")
            print(f"Testing Strategy: {strategy.value.upper()}")
            print(f"{'='*70}")

            strategy_results = {prob: [] for prob in grafting_probs}

            for trial in range(self.num_trials):
                print(f"\nTrial {trial + 1}/{self.num_trials}")

                for prob in grafting_probs:
                    config = EvolutionConfig(
                        grafting_strategy=strategy,
                        grafting_probability=prob,
                        max_new_connections=5,
                        connection_bias=0.3,
                    )

                    result = self._run_single_simulation(config, strategy)
                    strategy_results[prob].append(result)

            all_results[strategy.value] = strategy_results

        return self._analyze_results(all_results)

    def _run_single_simulation(
        self,
        config: EvolutionConfig,
        strategy: GraftingStrategy
    ) -> Dict:
        """Run single simulation with given grafting strategy."""
        # Start with sparse graph
        graph = AgentGraph(self.num_agents, config)

        # Remove some edges to start sparse
        initial_edges = list(graph.edges.keys())
        edges_to_remove = np.random.choice(
            len(initial_edges),
            size=int(len(initial_edges) * 0.6),
            replace=False
        )

        for idx in edges_to_remove:
            source, target = initial_edges[idx]
            graph._remove_edge(source, target)

        # Simulate evolution with grafting
        for t in range(self.generations):
            # Random activation
            num_active = int(self.num_agents * 0.3)
            active_agents = np.random.choice(
                [f"agent_{i}" for i in range(self.num_agents)],
                num_active,
                replace=False
            )

            # Activate edges
            for i, source in enumerate(active_agents):
                for target in active_agents[i+1:]:
                    if graph.has_edge(source, target):
                        graph.activate_edge(source, target)

            # Age edges
            graph.age_all_edges()

            # Graft new connections
            grafted = self._graft_edges(graph, config, strategy)

            # Record metrics
            if t % 5 == 0:
                metrics = graph.compute_metrics(t)
                metrics.grafted_this_cycle = grafted
                graph.metrics_history.append(metrics)

        final_metrics = graph.compute_metrics(self.generations)

        return {
            "final_edges": final_metrics.total_edges,
            "final_sparsity": final_metrics.sparsity,
            "final_performance": self._compute_performance(graph),
            "final_clustering": final_metrics.clustering_coefficient,
            "final_path_length": final_metrics.avg_path_length,
            "final_modularity": final_metrics.modularity,
            "small_world_sigma": final_metrics.small_world_sigma,
            "metrics_history": [m.to_dict() for m in graph.metrics_history],
        }

    def _graft_edges(
        self,
        graph: AgentGraph,
        config: EvolutionConfig,
        strategy: GraftingStrategy
    ) -> int:
        """Graft new edges based on strategy (matching TypeScript)."""
        if np.random.random() > config.grafting_probability:
            return 0

        new_connections = []
        node_ids = [f"agent_{i}" for i in range(self.num_agents)]

        for _ in range(config.max_new_connections):
            source = np.random.choice(node_ids)
            target: Optional[str] = None

            match strategy:
                case GraftingStrategy.RANDOM:
                    target = self._select_random_target(graph, source, node_ids)

                case GraftingStrategy.SIMILARITY:
                    target = self._select_similar_target(graph, source)

                case GraftingStrategy.COMPLEMENTARY:
                    target = self._select_complementary_target(graph, source)

                case GraftingStrategy.GRADIENT:
                    target = self._select_gradient_target(graph, source)

                case GraftingStrategy.HEURISTIC:
                    target = self._select_heuristic_target(
                        graph, source, node_ids, config.connection_bias
                    )

            if target and not graph.has_edge(source, target):
                new_connections.append((source, target))

        # Add new edges
        for source, target in new_connections:
            graph._add_edge(source, target, config.homeostatic_target)

        return len(new_connections)

    def _select_random_target(
        self,
        graph: AgentGraph,
        source: str,
        node_ids: List[str]
    ) -> Optional[str]:
        """Select random target for connection."""
        candidates = [n for n in node_ids if n != source]
        return np.random.choice(candidates) if candidates else None

    def _select_similar_target(
        self,
        graph: AgentGraph,
        source: str
    ) -> Optional[str]:
        """Select target with highest capability similarity."""
        source_node = graph.nodes.get(source)
        if not source_node:
            return None

        best_target = None
        best_similarity = -np.inf

        for agent_id, node in graph.nodes.items():
            if agent_id == source or graph.has_edge(source, agent_id):
                continue

            similarity = graph.compute_capability_similarity(source, agent_id)

            # Add some exploration
            adjusted = similarity + (np.random.random() - 0.5) * 0.3

            if adjusted > best_similarity:
                best_similarity = adjusted
                best_target = agent_id

        return best_target

    def _select_complementary_target(
        self,
        graph: AgentGraph,
        source: str
    ) -> Optional[str]:
        """Select target with complementary capabilities."""
        source_node = graph.nodes.get(source)
        if not source_node:
            return None

        best_target = None
        best_complementarity = -np.inf

        for agent_id, node in graph.nodes.items():
            if agent_id == source or graph.has_edge(source, agent_id):
                continue

            complementarity = graph.compute_complementarity(source, agent_id)

            if complementarity > best_complementarity:
                best_complementarity = complementarity
                best_target = agent_id

        return best_target

    def _select_gradient_target(
        self,
        graph: AgentGraph,
        source: str
    ) -> Optional[str]:
        """Select target following gradient of centrality."""
        # Compute centrality
        centrality = nx.degree_centrality(graph.graph.to_undirected())

        candidates = [
            n for n in graph.nodes.keys()
            if n != source and not graph.has_edge(source, n)
        ]

        if not candidates:
            return None

        # Sort by centrality
        candidates.sort(key=lambda x: centrality.get(x, 0), reverse=True)

        # Pick from top 3 with randomness
        top_n = min(3, len(candidates))
        return candidates[np.random.randint(0, top_n)]

    def _select_heuristic_target(
        self,
        graph: AgentGraph,
        source: str,
        node_ids: List[str],
        connection_bias: float
    ) -> Optional[str]:
        """Heuristic target selection combining multiple factors."""
        source_node = graph.nodes.get(source)
        if not source_node:
            return self._select_random_target(graph, source, node_ids)

        candidates = []
        centrality = nx.degree_centrality(graph.graph.to_undirected())

        for agent_id, node in graph.nodes.items():
            if agent_id == source or graph.has_edge(source, agent_id):
                continue

            similarity = graph.compute_capability_similarity(source, agent_id)
            complementarity = graph.compute_complementarity(source, agent_id)
            cent = centrality.get(agent_id, 0)

            # Combine factors
            score = (
                similarity * 0.3 +
                complementarity * 0.3 +
                cent * 0.2 +
                np.random.random() * 0.2
            )

            candidates.append((agent_id, score))

        if not candidates:
            return None

        # Pick highest score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _compute_performance(self, graph: AgentGraph) -> float:
        """Compute network performance score."""
        metrics = graph.compute_metrics(0)

        # Small-world optimization
        small_world_score = min(2.0, metrics.small_world_sigma)

        # Efficiency
        efficiency = 1.0 / max(0.001, metrics.avg_path_length)

        # Modularity (community structure)
        community_score = metrics.modularity

        # Combined performance
        performance = (
            small_world_score * 0.4 +
            efficiency * 0.3 +
            community_score * 0.3
        )

        return performance

    def _analyze_results(self, all_results: Dict) -> Dict:
        """Analyze results across strategies and probabilities."""
        analysis = {}

        for strategy, prob_results in all_results.items():
            print(f"\n{'='*70}")
            print(f"ANALYSIS: {strategy.upper()}")
            print(f"{'='*70}")

            prob_performance = []

            for prob, results in prob_results.items():
                performances = [r["final_performance"] for r in results]
                sparsities = [r["final_sparsity"] for r in results]
                small_worlds = [r["small_world_sigma"] for r in results]

                prob_performance.append({
                    "probability": prob,
                    "mean_performance": np.mean(performances),
                    "std_performance": np.std(performances),
                    "mean_sparsity": np.mean(sparsities),
                    "mean_small_world": np.mean(small_worlds),
                })

            # Find optimal probability
            optimal = max(prob_performance, key=lambda x: x["mean_performance"])

            analysis[strategy] = {
                "prob_performance": prob_performance,
                "optimal_probability": optimal["probability"],
                "optimal_performance": optimal["mean_performance"],
                "optimal_sparsity": optimal["mean_sparsity"],
            }

            print(f"\nOptimal Probability: {optimal['probability']:.4f}")
            print(f"Peak Performance: {optimal['mean_performance']:.4f}")
            print(f"Resulting Sparsity: {optimal['mean_sparsity']:.3f}")

        return analysis

    def plot_results(self, analysis: Dict, output_dir: Path):
        """Generate plots showing grafting dynamics."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Plot 1: Performance vs Grafting Probability
        fig, ax = plt.subplots(figsize=(12, 8))

        colors = {
            "random": "red",
            "similarity": "blue",
            "complementary": "green",
            "heuristic": "purple",
        }

        for strategy, data in analysis.items():
            prob_perf = data["prob_performance"]

            probs = [d["probability"] for d in prob_perf]
            performances = [d["mean_performance"] for d in prob_perf]
            errors = [d["std_performance"] for d in prob_perf]

            ax.errorbar(probs, performances, yerr=errors,
                       marker='o', linewidth=2, markersize=8,
                       color=colors.get(strategy, "gray"),
                       label=strategy.title())

            # Mark optimal
            optimal_prob = data["optimal_probability"]
            optimal_perf = data["optimal_performance"]
            ax.plot(optimal_prob, optimal_perf, '*',
                   color=colors.get(strategy, "gray"),
                   markersize=20, markeredgecolor='black',
                   markeredgewidth=2)

        ax.set_xlabel("Grafting Probability", fontsize=14)
        ax.set_ylabel("Performance Score", fontsize=14)
        ax.set_title("Grafting Strategy Comparison",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')

        plt.tight_layout()
        plt.savefig(output_dir / "grafting_performance.png", dpi=300)
        plt.close()

        # Plot 2: Performance gain over random
        fig, ax = plt.subplots(figsize=(12, 8))

        random_data = analysis.get("random", {})
        if random_data:
            random_baseline = np.mean([
                d["mean_performance"]
                for d in random_data["prob_performance"]
            ])

            strategies_gain = []
            for strategy, data in analysis.items():
                if strategy == "random":
                    continue

                best_performance = data["optimal_performance"]
                gain = (best_performance - random_baseline) / max(random_baseline, 0.001)
                strategies_gain.append((strategy, gain))

            strategies_gain.sort(key=lambda x: x[1], reverse=True)

            strategies = [s[0] for s in strategies_gain]
            gains = [s[1] * 100 for s in strategies_gain]

            colors_list = [colors.get(s, "gray") for s in strategies]
            ax.bar(strategies, gains, color=colors_list, alpha=0.7, edgecolor='black')

            ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
            ax.set_ylabel("Performance Gain over Random (%)", fontsize=14)
            ax.set_title("Grafting Strategy Effectiveness",
                        fontsize=16, fontweight='bold')
            ax.grid(True, axis='y', alpha=0.3)

            # Add value labels
            for i, (strategy, gain) in enumerate(strategies_gain):
                ax.text(i, gain + 1, f"{gain*100:.1f}%",
                       ha='center', va='bottom', fontsize=11,
                       fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / "grafting_gain.png", dpi=300)
        plt.close()

        # Plot 3: Small-world emergence
        fig, ax = plt.subplots(figsize=(12, 8))

        for strategy, data in analysis.items():
            prob_perf = data["prob_performance"]

            probs = [d["probability"] for d in prob_perf]
            small_worlds = [d["mean_small_world"] for d in prob_perf]

            ax.plot(probs, small_worlds, 'o-',
                   linewidth=2, markersize=8,
                   color=colors.get(strategy, "gray"),
                   label=strategy.title())

            # Mark sigma > 1 (small-world regime)
            ax.axhline(y=1.0, color='black', linestyle='--',
                      linewidth=1, alpha=0.5)

        ax.set_xlabel("Grafting Probability", fontsize=14)
        ax.set_ylabel("Small-World Sigma (σ)", fontsize=14)
        ax.set_title("Small-World Property Emergence",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')

        # Annotate small-world regime
        ax.annotate('Small-World\nRegime (σ > 1)',
                   xy=(0.02, 1.2), fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

        plt.tight_layout()
        plt.savefig(output_dir / "grafting_smallworld.png", dpi=300)
        plt.close()

        # Save analysis
        with open(output_dir / "grafting_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"\n{'='*70}")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*70}")


def main():
    """Run grafting simulation."""
    sim = GraftingSimulation(
        num_agents=100,
        generations=200,
        num_trials=5
    )

    analysis = sim.run_experiment()
    sim.plot_results(analysis, Path("simulations/results/grafting"))

    # Summary
    print("\n" + "=" * 70)
    print("GRAFTING SIMULATION SUMMARY")
    print("=" * 70)

    for strategy, data in analysis.items():
        print(f"\n{strategy.upper()}:")
        print(f"  Optimal Probability: {data['optimal_probability']:.4f}")
        print(f"  Peak Performance: {data['optimal_performance']:.4f}")


if __name__ == "__main__":
    main()
