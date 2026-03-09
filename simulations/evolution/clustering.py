"""
POLLN Graph Evolution - Clustering Simulation
==============================================

Simulates community detection algorithms to prove that clustering
organizes agents optimally for efficient communication.

Compares clustering algorithms:
- Spectral: k eigenvectors of Laplacian
- Louvain: Modularity optimization
- Hierarchical: Agglomerative clustering
- Label Propagation: Distributed algorithm

Hypothesis: Good clustering improves communication efficiency
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
import json
from collections import defaultdict
from sklearn.cluster import SpectralClustering, AgglomerativeClustering
from sklearn.metrics import silhouette_score

from ..base import AgentGraph, EvolutionConfig, EvolutionMetrics


class ClusteringSimulation:
    """
    Simulates different clustering algorithms to find optimal
    community structure in agent networks.

    Proves that proper clustering improves:
    - Communication efficiency
    - Community cohesion
    - Inter-cluster separation
    """

    def __init__(
        self,
        num_agents: int = 200,
        num_communities: int = 5,
        num_trials: int = 10
    ):
        self.num_agents = num_agents
        self.num_communities = num_communities
        self.num_trials = num_trials
        self.results: Dict[str, List[Dict]] = {}

    def run_experiment(self) -> Dict:
        """Run clustering experiment comparing all algorithms."""
        print("=" * 70)
        print("CLUSTERING SIMULATION - Optimal Community Detection")
        print("=" * 70)

        algorithms = [
            "louvain",
            "spectral",
            "hierarchical",
            "label_propagation",
        ]

        all_results = {alg: [] for alg in algorithms}

        for trial in range(self.num_trials):
            print(f"\nTrial {trial + 1}/{self.num_trials}")

            # Generate graph with ground-truth communities
            graph = self._generate_community_graph()

            # Run each algorithm
            for algorithm in algorithms:
                print(f"  Running {algorithm}...")

                result = self._run_clustering(graph, algorithm)
                all_results[algorithm].append(result)

        return self._analyze_results(all_results)

    def _generate_community_graph(self) -> AgentGraph:
        """Generate graph with embedded community structure."""
        config = EvolutionConfig()
        graph = AgentGraph(self.num_agents, config)

        # Clear existing edges
        for source, target in list(graph.edges.keys()):
            graph._remove_edge(source, target)

        # Create communities
        community_size = self.num_agents // self.num_communities
        communities = []

        for i in range(self.num_communities):
            start_idx = i * community_size
            end_idx = start_idx + community_size if i < self.num_communities - 1 else self.num_agents

            community_members = [f"agent_{j}" for j in range(start_idx, end_idx)]
            communities.append(community_members)

            # Add intra-community edges (high density)
            intra_density = 0.4
            num_edges = int(len(community_members) * (len(community_members) - 1) * intra_density / 2)

            for _ in range(num_edges):
                source, target = np.random.choice(community_members, 2, replace=False)
                if not graph.has_edge(source, target):
                    weight = np.random.uniform(0.6, 1.0)  # Strong intra-community
                    graph._add_edge(source, target, weight)

        # Add inter-community edges (low density)
        inter_density = 0.02
        for i in range(len(communities)):
            for j in range(i + 1, len(communities)):
                num_edges = int(len(communities[i]) * len(communities[j]) * inter_density)

                for _ in range(num_edges):
                    source = np.random.choice(communities[i])
                    target = np.random.choice(communities[j])
                    weight = np.random.uniform(0.1, 0.3)  # Weak inter-community
                    graph._add_edge(source, target, weight)

        # Store ground truth
        graph.ground_truth_communities = {
            i: set(members) for i, members in enumerate(communities)
        }

        return graph

    def _run_clustering(
        self,
        graph: AgentGraph,
        algorithm: str
    ) -> Dict:
        """Run clustering algorithm and evaluate results."""
        start_time = time.time()

        match algorithm:
            case "louvain":
                partition = self._louvain_clustering(graph)
            case "spectral":
                partition = self._spectral_clustering(graph)
            case "hierarchical":
                partition = self._hierarchical_clustering(graph)
            case "label_propagation":
                partition = self._label_propagation_clustering(graph)
            case _:
                partition = {}

        runtime = time.time() - start_time

        # Evaluate clustering
        metrics = self._evaluate_clustering(graph, partition)

        return {
            "runtime": runtime,
            "num_clusters": len(partition),
            "partition": partition,
            **metrics
        }

    def _louvain_clustering(self, graph: AgentGraph) -> Dict[int, Set[str]]:
        """Louvain modularity optimization."""
        G_undirected = graph.graph.to_undirected()

        try:
            import networkx.algorithms.community as nx_community
            communities = nx_community.louvain_communities(G_undirected)

            partition = {}
            for i, community in enumerate(communities):
                partition[i] = set(community)

            return partition
        except Exception as e:
            print(f"    Louvain failed: {e}")
            return {}

    def _spectral_clustering(self, graph: AgentGraph) -> Dict[int, Set[str]]:
        """Spectral clustering using Laplacian eigenvectors."""
        try:
            # Get adjacency matrix
            adj_matrix = nx.to_numpy_array(graph.graph)

            # Spectral clustering
            n_clusters = self.num_communities
            clustering = SpectralClustering(
                n_clusters=n_clusters,
                affinity='precomputed',
                random_state=42
            )

            labels = clustering.fit_predict(adj_matrix)

            # Build partition
            partition = defaultdict(set)
            for node_id, label in zip(graph.nodes.keys(), labels):
                partition[label].add(node_id)

            return dict(partition)

        except Exception as e:
            print(f"    Spectral failed: {e}")
            return {}

    def _hierarchical_clustering(self, graph: AgentGraph) -> Dict[int, Set[str]]:
        """Hierarchical agglomerative clustering."""
        try:
            # Get adjacency matrix
            adj_matrix = nx.to_numpy_array(graph.graph)

            # Hierarchical clustering
            n_clusters = self.num_communities
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward',
                metric='euclidean'
            )

            labels = clustering.fit_predict(1 - adj_matrix)  # Distance = 1 - similarity

            # Build partition
            partition = defaultdict(set)
            for node_id, label in zip(graph.nodes.keys(), labels):
                partition[label].add(node_id)

            return dict(partition)

        except Exception as e:
            print(f"    Hierarchical failed: {e}")
            return {}

    def _label_propagation_clustering(self, graph: AgentGraph) -> Dict[int, Set[str]]:
        """Label propagation algorithm."""
        try:
            import networkx.algorithms.community as nx_community
            communities = nx_community.label_propagation_communities(graph.graph.to_undirected())

            partition = {}
            for i, community in enumerate(communities):
                partition[i] = set(community)

            return partition

        except Exception as e:
            print(f"    Label propagation failed: {e}")
            return {}

    def _evaluate_clustering(
        self,
        graph: AgentGraph,
        partition: Dict[int, Set[str]]
    ) -> Dict:
        """Evaluate clustering quality."""
        if not partition:
            return {
                "modularity": 0.0,
                "coverage": 0.0,
                "performance": 0.0,
                "conductance": 1.0,
                "silhouette": 0.0,
                "nmi": 0.0,
                "ari": 0.0,
            }

        # Convert to list format for NetworkX
        communities_list = list(partition.values())

        try:
            # Modularity
            G_undirected = graph.graph.to_undirected()
            modularity = nx.community.modularity(G_undirected, communities_list)

            # Coverage (fraction of intra-community edges)
            coverage = nx.community.coverage(G_undirected, communities_list)

            # Performance (fraction of correctly classified edges)
            performance = nx.community.performance(G_undirected, communities_list)

            # Average conductance
            conductances = []
            for community in communities_list:
                subgraph = G_undirected.subgraph(community)
                if subgraph.number_of_edges() > 0:
                    conductance = nx.conductance(G_undirected, community)
                    conductances.append(conductance)

            avg_conductance = np.mean(conductances) if conductances else 1.0

            # Silhouette score
            try:
                adj_matrix = nx.to_numpy_array(graph.graph)

                # Create labels array
                labels = np.zeros(len(graph.nodes), dtype=int)
                for cluster_id, members in partition.items():
                    for member in members:
                        idx = int(member.split("_")[1])
                        labels[idx] = cluster_id

                silhouette = silhouette_score(adj_matrix, labels, metric='precomputed')
            except:
                silhouette = 0.0

            # Compare to ground truth if available
            nmi = 0.0
            ari = 0.0

            if hasattr(graph, 'ground_truth_communities'):
                try:
                    from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

                    # Create label arrays
                    pred_labels = np.zeros(len(graph.nodes), dtype=int)
                    true_labels = np.zeros(len(graph.nodes), dtype=int)

                    for cluster_id, members in partition.items():
                        for member in members:
                            idx = int(member.split("_")[1])
                            pred_labels[idx] = cluster_id

                    for comm_id, members in graph.ground_truth_communities.items():
                        for member in members:
                            idx = int(member.split("_")[1])
                            true_labels[idx] = comm_id

                    nmi = normalized_mutual_info_score(true_labels, pred_labels)
                    ari = adjusted_rand_score(true_labels, pred_labels)

                except:
                    pass

            return {
                "modularity": modularity,
                "coverage": coverage,
                "performance": performance,
                "conductance": avg_conductance,
                "silhouette": silhouette,
                "nmi": nmi,
                "ari": ari,
            }

        except Exception as e:
            print(f"    Evaluation failed: {e}")
            return {
                "modularity": 0.0,
                "coverage": 0.0,
                "performance": 0.0,
                "conductance": 1.0,
                "silhouette": 0.0,
                "nmi": 0.0,
                "ari": 0.0,
            }

    def _analyze_results(self, all_results: Dict) -> Dict:
        """Analyze results across all algorithms."""
        analysis = {}

        for algorithm, results in all_results.items():
            print(f"\n{'='*70}")
            print(f"ANALYSIS: {algorithm.upper()}")
            print(f"{'='*70}")

            metrics = ["modularity", "coverage", "performance",
                      "conductance", "silhouette", "nmi", "ari", "runtime"]

            summary = {}
            for metric in metrics:
                values = [r.get(metric, 0) for r in results]
                summary[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                }

                print(f"  {metric}: {summary[metric]['mean']:.4f} ± {summary[metric]['std']:.4f}")

            # Overall score (higher is better for most metrics)
            # For conductance, lower is better
            overall_scores = []
            for r in results:
                score = (
                    r.get("modularity", 0) * 0.3 +
                    r.get("coverage", 0) * 0.2 +
                    r.get("performance", 0) * 0.2 +
                    (1 - r.get("conductance", 1)) * 0.1 +
                    r.get("silhouette", 0) * 0.1 +
                    r.get("nmi", 0) * 0.05 +
                    r.get("ari", 0) * 0.05
                )
                overall_scores.append(score)

            summary["overall_score"] = {
                "mean": np.mean(overall_scores),
                "std": np.std(overall_scores),
            }

            print(f"\n  Overall Score: {summary['overall_score']['mean']:.4f} ± {summary['overall_score']['std']:.4f}")

            analysis[algorithm] = {
                "summary": summary,
                "individual_results": results
            }

        return analysis

    def plot_results(self, analysis: Dict, output_dir: Path):
        """Generate plots showing clustering comparisons."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        algorithms = list(analysis.keys())
        metrics = ["modularity", "coverage", "performance",
                  "silhouette", "nmi", "ari"]

        # Plot 1: Metric comparison
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle("Clustering Algorithm Comparison",
                    fontsize=16, fontweight='bold')

        colors = plt.cm.Set2(np.linspace(0, 1, len(algorithms)))

        for idx, metric in enumerate(metrics):
            ax = axes[idx // 3, idx % 3]

            means = []
            stds = []

            for alg in algorithms:
                means.append(analysis[alg]["summary"][metric]["mean"])
                stds.append(analysis[alg]["summary"][metric]["std"])

            x = np.arange(len(algorithms))
            width = 0.6

            bars = ax.bar(x, means, width, yerr=stds,
                         color=colors, alpha=0.8,
                         capsize=5, edgecolor='black')

            ax.set_ylabel(metric.capitalize(), fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels([alg.title() for alg in algorithms], rotation=45)
            ax.set_title(metric.replace("_", " ").title(), fontsize=14,
                        fontweight='bold')
            ax.grid(True, axis='y', alpha=0.3)

            # Add value labels
            for i, (bar, mean) in enumerate(zip(bars, means)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + stds[i] + 0.01,
                       f"{mean:.3f}", ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(output_dir / "clustering_metrics.png", dpi=300)
        plt.close()

        # Plot 2: Overall score and runtime
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        overall_scores = [analysis[alg]["summary"]["overall_score"]["mean"]
                         for alg in algorithms]
        runtime_means = [analysis[alg]["summary"]["runtime"]["mean"]
                        for alg in algorithms]

        bars1 = ax1.bar(algorithms, overall_scores, color=colors,
                       alpha=0.8, edgecolor='black')
        ax1.set_ylabel("Overall Score", fontsize=14)
        ax1.set_title("Clustering Quality (Overall Score)", fontsize=14,
                     fontweight='bold')
        ax1.grid(True, axis='y', alpha=0.3)
        ax1.set_xticklabels([alg.title() for alg in algorithms], rotation=45)

        for bar, score in zip(bars1, overall_scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f"{score:.3f}", ha='center', va='bottom', fontsize=11,
                    fontweight='bold')

        bars2 = ax2.bar(algorithms, runtime_means, color=colors,
                       alpha=0.8, edgecolor='black')
        ax2.set_ylabel("Runtime (seconds)", fontsize=14)
        ax2.set_title("Computational Efficiency", fontsize=14,
                     fontweight='bold')
        ax2.grid(True, axis='y', alpha=0.3)
        ax2.set_xticklabels([alg.title() for alg in algorithms], rotation=45)

        for bar, runtime in zip(bars2, runtime_means):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + runtime*0.05,
                    f"{runtime:.3f}s", ha='center', va='bottom', fontsize=11,
                    fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / "clustering_overall.png", dpi=300)
        plt.close()

        # Plot 3: Trade-off analysis (quality vs runtime)
        fig, ax = plt.subplots(figsize=(12, 8))

        for alg, color in zip(algorithms, colors):
            mean_score = analysis[alg]["summary"]["overall_score"]["mean"]
            std_score = analysis[alg]["summary"]["overall_score"]["std"]
            mean_runtime = analysis[alg]["summary"]["runtime"]["mean"]
            std_runtime = analysis[alg]["summary"]["runtime"]["std"]

            ax.errorbar(mean_runtime, mean_score,
                       xerr=std_runtime, yerr=std_score,
                       marker='o', markersize=15, linewidth=2,
                       color=color, label=alg.title(),
                       markeredgecolor='black', markeredgewidth=2)

        ax.set_xlabel("Runtime (seconds)", fontsize=14)
        ax.set_ylabel("Overall Quality Score", fontsize=14)
        ax.set_title("Quality vs Runtime Trade-off",
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add efficiency annotation
        for alg in algorithms:
            mean_score = analysis[alg]["summary"]["overall_score"]["mean"]
            mean_runtime = analysis[alg]["summary"]["runtime"]["mean"]
            efficiency = mean_score / max(mean_runtime, 0.001)
            ax.annotate(f"{efficiency:.1f}\nscore/s",
                       xy=(mean_runtime, mean_score),
                       fontsize=9, ha='center', va='center',
                       bbox=dict(boxstyle='round,pad=0.3',
                               facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(output_dir / "clustering_tradeoff.png", dpi=300)
        plt.close()

        # Save analysis
        with open(output_dir / "clustering_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*70}")


def main():
    """Run clustering simulation."""
    import time

    sim = ClusteringSimulation(
        num_agents=200,
        num_communities=5,
        num_trials=10
    )

    analysis = sim.run_experiment()
    sim.plot_results(analysis, Path("simulations/results/clustering"))

    # Summary
    print("\n" + "=" * 70)
    print("CLUSTERING SIMULATION SUMMARY")
    print("=" * 70)

    for algorithm, data in analysis.items():
        print(f"\n{algorithm.upper()}:")
        print(f"  Overall Score: {data['summary']['overall_score']['mean']:.4f}")
        print(f"  Modularity: {data['summary']['modularity']['mean']:.4f}")
        print(f"  NMI: {data['summary']['nmi']['mean']:.4f}")
        print(f"  Runtime: {data['summary']['runtime']['mean']:.4f}s")


if __name__ == "__main__":
    main()
