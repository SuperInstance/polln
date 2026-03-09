"""
POLLN Network Topology Optimization
====================================

This module compares different network topologies for POLLN colonies to identify
the most efficient structure for large-scale agent communication.

Hypothesis H4: Small-world network structure minimizes communication overhead.

Author: POLLN Simulation Team
Date: 2026-03-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import deque
import networkx as nx
import pandas as pd
from pathlib import Path


@dataclass
class TopologyMetrics:
    """Metrics for a network topology."""
    topology_name: str
    n_nodes: int
    avg_degree: float
    avg_path_length: float
    clustering_coefficient: float
    diameter: int
    avg_hops: float
    communication_efficiency: float
    fault_tolerance: float
    scaling_factor: float


class TopologyGenerator:
    """Generate various network topologies for testing."""

    @staticmethod
    def fully_connected(n: int) -> nx.Graph:
        """Generate fully connected network."""
        return nx.complete_graph(n)

    @staticmethod
    def small_world(n: int, k: int = 6, p: float = 0.1) -> nx.Graph:
        """
        Generate Watts-Strogatz small-world network.

        Args:
            n: Number of nodes
            k: Each node connected to k nearest neighbors
            p: Probability of rewiring each edge
        """
        return nx.watts_strogatz_graph(n, k, p, seed=42)

    @staticmethod
    def hierarchical(n: int, branching_factor: int = 3) -> nx.Graph:
        """Generate hierarchical tree network."""
        # Create a balanced tree
        height = int(np.log(n) / np.log(branching_factor))
        tree = nx.balanced_tree(branching_factor, height)

        # If tree is too small, add more nodes
        while tree.number_of_nodes() < n:
            # Add random connections to extend
            new_node = tree.number_of_nodes()
            tree.add_node(new_node)
            target = np.random.randint(0, tree.number_of_nodes() - 1)
            tree.add_edge(new_node, target)

        return nx.Graph(tree)

    @staticmethod
    def random_network(n: int, p: float = 0.1) -> nx.Graph:
        """Generate Erdős-Rényi random network."""
        return nx.erdos_renyi_graph(n, p, seed=42)

    @staticmethod
    def scale_free(n: int) -> nx.Graph:
        """Generate Barabási-Albert scale-free network."""
        return nx.barabasi_albert_graph(n, 2, seed=42)


class TopologyOptimizer:
    """
    Analyzes and optimizes network topologies for POLLN colonies.
    """

    def __init__(self, seed: int = 42):
        """Initialize optimizer."""
        np.random.seed(seed)

    def analyze_topology(
        self,
        G: nx.Graph,
        topology_name: str
    ) -> TopologyMetrics:
        """
        Analyze a network topology's characteristics.
        """
        n = G.number_of_nodes()

        # Basic metrics
        avg_degree = np.mean([d for _, d in G.degree()])

        # Path length (use approximation for large networks)
        if n <= 500:
            avg_path_length = nx.average_shortest_path_length(G)
        else:
            # Sample-based approximation
            sample_nodes = np.random.choice(G.nodes(), size=min(100, n), replace=False)
            paths = []
            for source in sample_nodes:
                lengths = nx.single_source_shortest_path_length(G, source)
                paths.extend(lengths.values())
            avg_path_length = np.mean(paths)

        # Clustering coefficient
        clustering_coefficient = nx.average_clustering(G)

        # Diameter (use approximation for large networks)
        if n <= 500:
            diameter = nx.diameter(G)
        else:
            # Estimate diameter from average path length
            diameter = int(avg_path_length * 2)

        # Average hops for communication
        avg_hops = avg_path_length

        # Communication efficiency (inverse of path length)
        communication_efficiency = 1.0 / (avg_path_length + 1)

        # Fault tolerance (based on connectivity and clustering)
        fault_tolerance = clustering_coefficient * (1 - 1/n)

        # Scaling factor (how well topology scales)
        # Ideal: O(log N) path length, constant clustering
        scaling_score = (1.0 / avg_path_length) * clustering_coefficient
        scaling_factor = scaling_score

        return TopologyMetrics(
            topology_name=topology_name,
            n_nodes=n,
            avg_degree=avg_degree,
            avg_path_length=avg_path_length,
            clustering_coefficient=clustering_coefficient,
            diameter=diameter,
            avg_hops=avg_hops,
            communication_efficiency=communication_efficiency,
            fault_tolerance=fault_tolerance,
            scaling_factor=scaling_factor
        )

    def simulate_communication(
        self,
        G: nx.Graph,
        n_packages: int = 1000,
        package_size_kb: float = 2.0
    ) -> Dict:
        """
        Simulate A2A package propagation through the network.

        Returns statistics on latency, bandwidth, and success rate.
        """
        nodes = list(G.nodes())
        n = len(nodes)

        # Generate random source-destination pairs
        sources = np.random.choice(nodes, size=n_packages)
        destinations = np.random.choice(nodes, size=n_packages)

        # Calculate path lengths
        path_lengths = []
        success_count = 0

        for source, dest in zip(sources, destinations):
            try:
                length = nx.shortest_path_length(G, source, dest)
                path_lengths.append(length)
                success_count += 1
            except nx.NetworkXNoPath:
                # No path exists
                pass

        if not path_lengths:
            return {
                'avg_latency_ms': float('inf'),
                'success_rate': 0.0,
                'total_hops': 0
            }

        # Calculate latency (base + per-hop)
        base_latency = 0.5  # ms
        per_hop_latency = 0.1  # ms
        latencies = [base_latency + per_hop_latency * length for length in path_lengths]

        return {
            'avg_latency_ms': np.mean(latencies),
            'std_latency_ms': np.std(latencies),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies),
            'success_rate': success_count / n_packages,
            'total_hops': np.sum(path_lengths),
            'avg_hops': np.mean(path_lengths)
        }

    def run_topology_comparison(
        self,
        colony_sizes: List[int] = None,
        n_trials: int = 10
    ) -> Tuple[Dict[str, List[TopologyMetrics]], Dict]:
        """
        Compare different topologies across various colony sizes.
        """
        if colony_sizes is None:
            colony_sizes = [50, 100, 200, 500, 1000]

        print("="*60)
        print("Network Topology Comparison")
        print("="*60)

        topologies = {
            'Fully Connected': TopologyGenerator.fully_connected,
            'Small-World': lambda n: TopologyGenerator.small_world(n, k=6, p=0.1),
            'Hierarchical': TopologyGenerator.hierarchical,
            'Random': lambda n: TopologyGenerator.random_network(n, p=0.1),
            'Scale-Free': TopologyGenerator.scale_free
        }

        results = {name: [] for name in topologies.keys()}

        for size in colony_sizes:
            print(f"\nAnalyzing colony size N={size}...")

            for topo_name, generator in topologies.items():
                try:
                    G = generator(size)

                    # Analyze topology
                    metrics = self.analyze_topology(G, topo_name)
                    results[topo_name].append(metrics)

                    # Simulate communication
                    comm_stats = self.simulate_communication(G, n_packages=500)

                    print(f"  {topo_name:20s}: L={metrics.avg_path_length:.2f}, "
                          f"C={metrics.clustering_coefficient:.3f}, "
                          f"Lat={comm_stats['avg_latency_ms']:.2f}ms")

                except Exception as e:
                    print(f"  {topo_name:20s}: ERROR - {e}")
                    continue

        # Perform statistical analysis
        analysis = self._analyze_topologies(results, colony_sizes)

        return results, analysis

    def _analyze_topologies(
        self,
        results: Dict[str, List[TopologyMetrics]],
        colony_sizes: List[int]
    ) -> Dict:
        """
        Analyze topology performance and identify optimal structure.
        """
        analysis = {}

        # Calculate average metrics across colony sizes
        for topo_name, metrics_list in results.items():
            if not metrics_list:
                continue

            # Average path length scaling
            avg_path_lengths = [m.avg_path_length for m in metrics_list]

            # Fit scaling model: L ~ a * N^b
            from scipy.optimize import curve_fit

            def power_law(N, a, b):
                return a * np.power(N, b)

            try:
                popt, _ = curve_fit(power_law, colony_sizes[:len(avg_path_lengths)],
                                   avg_path_lengths)
                scaling_exponent = popt[1]
            except:
                scaling_exponent = float('nan')

            analysis[topo_name] = {
                'avg_path_length': np.mean(avg_path_lengths),
                'scaling_exponent': scaling_exponent,
                'clustering_coefficient': np.mean([m.clustering_coefficient for m in metrics_list]),
                'communication_efficiency': np.mean([m.communication_efficiency for m in metrics_list]),
                'fault_tolerance': np.mean([m.fault_tolerance for m in metrics_list])
            }

        # Find best topology for each metric
        best_path_length = min(analysis.items(), key=lambda x: x[1]['avg_path_length'])
        best_scaling = min(analysis.items(), key=lambda x: x[1]['scaling_exponent'])
        best_efficiency = max(analysis.items(), key=lambda x: x[1]['communication_efficiency'])
        best_fault_tolerance = max(analysis.items(), key=lambda x: x[1]['fault_tolerance'])

        # H4 validation: Is small-world optimal?
        small_world_metrics = analysis.get('Small-World', {})

        # Check if small-world has best or near-best metrics
        is_optimal = (
            best_path_length[0] == 'Small-World' or
            best_scaling[0] == 'Small-World' or
            best_efficiency[0] == 'Small-World'
        )

        analysis['summary'] = {
            'best_path_length': best_path_length[0],
            'best_scaling': best_scaling[0],
            'best_efficiency': best_efficiency[0],
            'best_fault_tolerance': best_fault_tolerance[0]
        }

        analysis['hypothesis_h4'] = {
            'validated': is_optimal,
            'small_world_rank': self._get_rank(analysis, 'Small-World'),
            'conclusion': 'H4 VALIDATED: Small-world is optimal or near-optimal' if is_optimal
                         else 'H4 REJECTED: Another topology is better'
        }

        return analysis

    def _get_rank(self, analysis: Dict, topo_name: str) -> int:
        """Get ranking of topology by overall score."""
        scores = []
        for name, metrics in analysis.items():
            if name == 'summary' or name == 'hypothesis_h4':
                continue
            score = (metrics['communication_efficiency'] +
                    metrics['fault_tolerance']) / metrics['avg_path_length']
            scores.append((name, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        for rank, (name, _) in enumerate(scores, 1):
            if name == topo_name:
                return rank
        return len(scores)

    def plot_topology_comparison(
        self,
        results: Dict[str, List[TopologyMetrics]],
        analysis: Dict,
        colony_sizes: List[int],
        output_dir: str = None
    ):
        """Generate topology comparison plots."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'plots'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-paper')
        plt.rcParams.update({
            'font.size': 10,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'figure.dpi': 300
        })

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Network Topology Comparison', fontsize=16, fontweight='bold')

        colors = {
            'Fully Connected': 'red',
            'Small-World': 'green',
            'Hierarchical': 'blue',
            'Random': 'orange',
            'Scale-Free': 'purple'
        }

        markers = {
            'Fully Connected': 'o',
            'Small-World': 's',
            'Hierarchical': '^',
            'Random': 'd',
            'Scale-Free': 'v'
        }

        # Plot 1: Average Path Length vs Colony Size
        ax1 = axes[0, 0]
        for topo_name, metrics_list in results.items():
            if not metrics_list:
                continue
            sizes = [m.n_nodes for m in metrics_list]
            path_lengths = [m.avg_path_length for m in metrics_list]
            ax1.plot(sizes, path_lengths, marker=markers.get(topo_name, 'o'),
                    color=colors.get(topo_name, 'gray'), label=topo_name, alpha=0.7)

        ax1.set_xlabel('Colony Size (N)')
        ax1.set_ylabel('Average Path Length')
        ax1.set_title('Path Length Scaling')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')

        # Plot 2: Clustering Coefficient vs Colony Size
        ax2 = axes[0, 1]
        for topo_name, metrics_list in results.items():
            if not metrics_list:
                continue
            sizes = [m.n_nodes for m in metrics_list]
            clustering = [m.clustering_coefficient for m in metrics_list]
            ax2.plot(sizes, clustering, marker=markers.get(topo_name, 'o'),
                    color=colors.get(topo_name, 'gray'), label=topo_name, alpha=0.7)

        ax2.set_xlabel('Colony Size (N)')
        ax2.set_ylabel('Clustering Coefficient')
        ax2.set_title('Clustering')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Communication Efficiency vs Colony Size
        ax3 = axes[1, 0]
        for topo_name, metrics_list in results.items():
            if not metrics_list:
                continue
            sizes = [m.n_nodes for m in metrics_list]
            efficiency = [m.communication_efficiency for m in metrics_list]
            ax3.plot(sizes, efficiency, marker=markers.get(topo_name, 'o'),
                    color=colors.get(topo_name, 'gray'), label=topo_name, alpha=0.7)

        ax3.set_xlabel('Colony Size (N)')
        ax3.set_ylabel('Communication Efficiency')
        ax3.set_title('Efficiency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Scaling Exponents
        ax4 = axes[1, 1]
        topo_names = []
        exponents = []

        for topo_name, metrics_list in results.items():
            if not metrics_list:
                continue
            topo_names.append(topo_name)
            exp = analysis[topo_name]['scaling_exponent']
            exponents.append(exp if not np.isnan(exp) else 0)

        colors_list = [colors.get(name, 'gray') for name in topo_names]
        ax4.barh(topo_names, exponents, color=colors_list, alpha=0.7)
        ax4.axvline(x=0.5, color='r', linestyle='--', label='Ideal (0.5)')
        ax4.set_xlabel('Scaling Exponent')
        ax4.set_title('Path Length Scaling (L ~ N^α)')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        fig_path = output_dir / 'topology_comparison.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"\nTopology comparison saved to: {fig_path}")

        return fig_path

    def visualize_topologies(
        self,
        n: int = 50,
        output_dir: str = None
    ):
        """Create visual representations of different topologies."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'plots'
        output_dir.mkdir(parents=True, exist_ok=True)

        topologies = {
            'Small-World': TopologyGenerator.small_world(n, k=6, p=0.1),
            'Hierarchical': TopologyGenerator.hierarchical(n),
            'Random': TopologyGenerator.random_network(n, p=0.1),
            'Scale-Free': TopologyGenerator.scale_free(n)
        }

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle(f'Network Topology Visualizations (N={n})',
                    fontsize=16, fontweight='bold')

        pos_map = {
            'Small-World': (0, 0),
            'Hierarchical': (0, 1),
            'Random': (1, 0),
            'Scale-Free': (1, 1)
        }

        for topo_name, G in topologies.items():
            ax = axes[pos_map[topo_name]]

            # Use spring layout for visualization
            pos = nx.spring_layout(G, seed=42)

            # Draw network
            nx.draw(G, pos, ax=ax, node_size=50, node_color='steelblue',
                   edge_color='gray', width=0.5, with_labels=False)

            # Calculate metrics
            metrics = self.analyze_topology(G, topo_name)

            ax.set_title(f'{topo_name}\n'
                        f'L={metrics.avg_path_length:.2f}, '
                        f'C={metrics.clustering_coefficient:.3f}',
                        fontsize=12)

        plt.tight_layout()

        fig_path = output_dir / 'topology_visualizations.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"Topology visualizations saved to: {fig_path}")

        return fig_path


def main():
    """Main execution function."""
    optimizer = TopologyOptimizer(seed=42)

    # Run topology comparison
    colony_sizes = [50, 100, 200, 500, 1000]
    results, analysis = optimizer.run_topology_comparison(colony_sizes=colony_sizes)

    # Print results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    print("\nTopology Rankings:")
    print(f"{'Topology':<20} {'Path Length':>15} {'Efficiency':>15} {'Fault Tol':>12}")
    print("-"*70)
    for topo_name, metrics in analysis.items():
        if topo_name in ['summary', 'hypothesis_h4']:
            continue
        print(f"{topo_name:<20} {metrics['avg_path_length']:>15.3f} "
              f"{metrics['communication_efficiency']:>15.3f} "
              f"{metrics['fault_tolerance']:>12.3f}")

    print("\n" + "="*60)
    print("HYPOTHESIS H4 VALIDATION")
    print("="*60)
    h4_result = analysis['hypothesis_h4']
    print(f"\n{h4_result['conclusion']}")
    print(f"Small-world rank: {h4_result['small_world_rank']} out of 5")

    print(f"\nBest by category:")
    print(f"  Path Length: {analysis['summary']['best_path_length']}")
    print(f"  Scaling: {analysis['summary']['best_scaling']}")
    print(f"  Efficiency: {analysis['summary']['best_efficiency']}")
    print(f"  Fault Tolerance: {analysis['summary']['best_fault_tolerance']}")

    # Generate plots
    print("\n" + "="*60)
    print("GENERATING PLOTS")
    print("="*60)
    optimizer.plot_topology_comparison(results, analysis, colony_sizes)
    optimizer.visualize_topologies(n=50)

    # Save results
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create summary DataFrame
    summary_data = []
    for topo_name, metrics_list in results.items():
        for m in metrics_list:
            summary_data.append({
                'topology': topo_name,
                'n_nodes': m.n_nodes,
                'avg_degree': m.avg_degree,
                'avg_path_length': m.avg_path_length,
                'clustering_coefficient': m.clustering_coefficient,
                'diameter': m.diameter,
                'communication_efficiency': m.communication_efficiency,
                'fault_tolerance': m.fault_tolerance
            })

    df = pd.DataFrame(summary_data)
    csv_path = output_dir / 'topology_metrics.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to: {csv_path}")

    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)

    return results, analysis


if __name__ == '__main__':
    results, analysis = main()
