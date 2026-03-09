"""
Topology Evaluator for POLLN Agent Colonies

Evaluates network topologies on multiple dimensions:
- Structural properties (path length, clustering, centrality)
- Efficiency (global and local)
- Robustness (attack/failure tolerance)
- Cost (edge count, degree distribution)
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing


@dataclass
class TopologyMetrics:
    """Comprehensive metrics for a topology."""
    # Basic properties
    num_nodes: int
    num_edges: int
    avg_degree: float
    density: float

    # Path-based metrics
    avg_path_length: float
    diameter: int
    radius: int

    # Clustering
    clustering_coefficient: float
    transitivity: float

    # Centrality
    avg_betweenness: float
    max_betweenness: float
    avg_closeness: float
    max_closeness: float
    avg_eigenvector: float
    max_eigenvector: float

    # Efficiency
    global_efficiency: float
    local_efficiency: float

    # Robustness
    attack_tolerance: float  # Size of largest component after targeted attacks
    failure_tolerance: float  # Size of largest component after random failures
    connectivity: int  # Node connectivity
    edge_connectivity: int

    # Degree distribution
    degree_assortativity: float
    degree_entropy: float
    power_law_alpha: Optional[float]
    is_scale_free: bool

    # Spectral properties
    spectral_radius: float
    algebraic_connectivity: float

    # Cost
    edge_cost: float  # Normalized edge count
    degree_cost: float  # Normalized max degree


class TopologyEvaluator:
    """Evaluate network topologies on multiple dimensions."""

    def __init__(self, parallel: bool = True):
        """Initialize evaluator."""
        self.parallel = parallel
        if parallel:
            self.num_workers = multiprocessing.cpu_count()

    def evaluate(self, G: nx.Graph) -> TopologyMetrics:
        """Comprehensive evaluation of a topology."""
        metrics = {}

        # Basic properties
        metrics.update(self._basic_properties(G))

        # Path-based metrics
        metrics.update(self._path_metrics(G))

        # Clustering
        metrics.update(self._clustering_metrics(G))

        # Centrality
        metrics.update(self._centrality_metrics(G))

        # Efficiency
        metrics.update(self._efficiency_metrics(G))

        # Robustness (can be slow)
        metrics.update(self._robustness_metrics(G))

        # Degree distribution
        metrics.update(self._degree_metrics(G))

        # Spectral properties
        metrics.update(self._spectral_metrics(G))

        # Cost
        metrics.update(self._cost_metrics(G))

        return TopologyMetrics(**metrics)

    def _basic_properties(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate basic graph properties."""
        n = G.number_of_nodes()
        m = G.number_of_edges()
        degrees = [d for n, d in G.degree()]

        return {
            'num_nodes': n,
            'num_edges': m,
            'avg_degree': np.mean(degrees),
            'density': nx.density(G)
        }

    def _path_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate path-based metrics."""
        if nx.is_connected(G):
            avg_path_length = nx.average_shortest_path_length(G)
            diameter = nx.diameter(G)
            radius = nx.radius(G)
        else:
            # For disconnected graphs, use largest component
            largest_cc = max(nx.connected_components(G), key=len)
            G_largest = G.subgraph(largest_cc).copy()
            avg_path_length = nx.average_shortest_path_length(G_largest)
            diameter = nx.diameter(G_largest)
            radius = nx.radius(G_largest)

        return {
            'avg_path_length': avg_path_length,
            'diameter': diameter,
            'radius': radius
        }

    def _clustering_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate clustering metrics."""
        return {
            'clustering_coefficient': nx.average_clustering(G),
            'transitivity': nx.transitivity(G)
        }

    def _centrality_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate centrality metrics."""
        betweenness = nx.betweenness_centrality(G)
        closeness = nx.closeness_centrality(G)

        try:
            eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
        except nx.PowerIterationFailedConvergence:
            eigenvector = {n: 0.0 for n in G.nodes()}

        return {
            'avg_betweenness': np.mean(list(betweenness.values())),
            'max_betweenness': np.max(list(betweenness.values())),
            'avg_closeness': np.mean(list(closeness.values())),
            'max_closeness': np.max(list(closeness.values())),
            'avg_eigenvector': np.mean(list(eigenvector.values())),
            'max_eigenvector': np.max(list(eigenvector.values()))
        }

    def _efficiency_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate efficiency metrics."""
        global_eff = nx.global_efficiency(G)

        # Local efficiency can be slow for large graphs
        if G.number_of_nodes() <= 500:
            local_eff = nx.local_efficiency(G)
        else:
            # Approximate using sampling
            local_eff = self._approximate_local_efficiency(G)

        return {
            'global_efficiency': global_eff,
            'local_efficiency': local_eff
        }

    def _approximate_local_efficiency(self, G: nx.Graph, sample_size: int = 100) -> float:
        """Approximate local efficiency using sampling."""
        nodes = list(G.nodes())
        if len(nodes) <= sample_size:
            return nx.local_efficiency(G)

        sampled_nodes = np.random.choice(nodes, sample_size, replace=False)
        efficiencies = []

        for node in sampled_nodes:
            neighbors = list(G.neighbors(node))
            if len(neighbors) < 2:
                efficiencies.append(0.0)
                continue

            # Calculate efficiency on subgraph of neighbors
            subgraph = G.subgraph(neighbors)
            if subgraph.number_of_nodes() < 2:
                efficiencies.append(0.0)
            else:
                efficiencies.append(nx.global_efficiency(subgraph))

        return np.mean(efficiencies)

    def _robustness_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate robustness metrics."""
        # Node and edge connectivity
        try:
            connectivity = nx.node_connectivity(G)
        except:
            connectivity = 0

        try:
            edge_connectivity = nx.edge_connectivity(G)
        except:
            edge_connectivity = 0

        # Attack tolerance (remove top 10% by degree)
        attack_tolerance = self._attack_tolerance(G, fraction=0.1)

        # Failure tolerance (remove 10% randomly)
        failure_tolerance = self._failure_tolerance(G, fraction=0.1)

        return {
            'connectivity': connectivity,
            'edge_connectivity': edge_connectivity,
            'attack_tolerance': attack_tolerance,
            'failure_tolerance': failure_tolerance
        }

    def _attack_tolerance(self, G: nx.Graph, fraction: float = 0.1) -> float:
        """Measure tolerance to targeted attacks."""
        n = G.number_of_nodes()
        num_remove = int(n * fraction)

        if num_remove == 0:
            return 1.0

        # Find nodes with highest degree
        degrees = dict(G.degree())
        nodes_to_remove = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:num_remove]
        nodes_to_remove = [node for node, _ in nodes_to_remove]

        G_reduced = G.copy()
        G_reduced.remove_nodes_from(nodes_to_remove)

        if G_reduced.number_of_nodes() == 0:
            return 0.0

        # Size of largest component relative to original
        largest_cc = max(nx.connected_components(G_reduced), key=len)
        return len(largest_cc) / n

    def _failure_tolerance(self, G: nx.Graph, fraction: float = 0.1) -> float:
        """Measure tolerance to random failures."""
        n = G.number_of_nodes()
        num_remove = int(n * fraction)

        if num_remove == 0:
            return 1.0

        # Randomly remove nodes
        nodes_to_remove = np.random.choice(list(G.nodes()), num_remove, replace=False)

        G_reduced = G.copy()
        G_reduced.remove_nodes_from(nodes_to_remove)

        if G_reduced.number_of_nodes() == 0:
            return 0.0

        # Size of largest component relative to original
        largest_cc = max(nx.connected_components(G_reduced), key=len)
        return len(largest_cc) / n

    def _degree_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate degree distribution metrics."""
        degrees = [d for n, d in G.degree()]

        # Degree assortativity
        try:
            degree_assortativity = nx.degree_assortativity_coefficient(G)
        except:
            degree_assortativity = 0.0

        # Degree entropy
        degree_dist = np.bincount(degrees)
        degree_dist = degree_dist[degree_dist > 0] / len(degrees)
        degree_entropy = -np.sum(degree_dist * np.log2(degree_dist))

        # Power law test
        try:
            from powerlaw import Fit
            fit = Fit(degrees, discrete=True, suppress_warning=True)
            power_law_alpha = fit.power_law.alpha
            is_scale_free = fit.power_law.sigma < 0.1  # Goodness of fit
        except:
            # Fallback: simple heuristic
            power_law_alpha = None
            is_scale_free = self._is_scale_free_heuristic(G)

        return {
            'degree_assortativity': degree_assortativity,
            'degree_entropy': degree_entropy,
            'power_law_alpha': power_law_alpha,
            'is_scale_free': is_scale_free
        }

    def _is_scale_free_heuristic(self, G: nx.Graph) -> bool:
        """Heuristic check for scale-free network."""
        degrees = [d for n, d in G.degree()]
        max_degree = max(degrees)
        avg_degree = np.mean(degrees)

        # Scale-free networks have hubs with degree >> average
        return max_degree > 3 * avg_degree

    def _spectral_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate spectral properties."""
        try:
            L = nx.laplacian_matrix(G).todense()
            eigenvalues = np.linalg.eigvals(L).real
            eigenvalues = np.sort(eigenvalues)

            spectral_radius = max(abs(eigenvalues[0]), abs(eigenvalues[-1]))
            algebraic_connectivity = eigenvalues[1] if len(eigenvalues) > 1 else 0
        except:
            spectral_radius = 0.0
            algebraic_connectivity = 0.0

        return {
            'spectral_radius': spectral_radius,
            'algebraic_connectivity': algebraic_connectivity
        }

    def _cost_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate cost metrics."""
        n = G.number_of_nodes()
        m = G.number_of_edges()
        max_degree = max([d for n, d in G.degree()])

        # Normalize by complete graph
        max_edges = n * (n - 1) / 2
        edge_cost = m / max_edges if max_edges > 0 else 0

        # Normalize max degree by n-1
        degree_cost = max_degree / (n - 1) if n > 1 else 0

        return {
            'edge_cost': edge_cost,
            'degree_cost': degree_cost
        }

    def calculate_score(self, metrics: TopologyMetrics,
                       weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted score for topology selection."""
        if weights is None:
            weights = {
                'avg_path_length': -0.25,  # Minimize
                'clustering_coefficient': 0.15,  # Maximize
                'global_efficiency': 0.15,  # Maximize
                'attack_tolerance': 0.15,  # Maximize
                'failure_tolerance': 0.10,  # Maximize
                'edge_cost': -0.10,  # Minimize
                'degree_cost': -0.10,  # Minimize
            }

        # Normalize metrics to [0, 1]
        normalized = {
            'avg_path_length': min(metrics.avg_path_length / 10, 1.0),
            'clustering_coefficient': metrics.clustering_coefficient,
            'global_efficiency': metrics.global_efficiency,
            'attack_tolerance': metrics.attack_tolerance,
            'failure_tolerance': metrics.failure_tolerance,
            'edge_cost': metrics.edge_cost,
            'degree_cost': metrics.degree_cost,
        }

        score = sum(weights.get(k, 0) * v for k, v in normalized.items())
        return score

    def batch_evaluate(self, topologies: List[Tuple[str, nx.Graph]],
                      weights: Optional[Dict[str, float]] = None) -> Dict[str, Tuple[TopologyMetrics, float]]:
        """Evaluate multiple topologies in parallel."""
        results = {}

        if self.parallel:
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                futures = {
                    executor.submit(self.evaluate, G): name
                    for name, G in topologies
                }

                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        metrics = future.result()
                        score = self.calculate_score(metrics, weights)
                        results[name] = (metrics, score)
                    except Exception as e:
                        print(f"Error evaluating {name}: {e}")
        else:
            for name, G in topologies:
                try:
                    metrics = self.evaluate(G)
                    score = self.calculate_score(metrics, weights)
                    results[name] = (metrics, score)
                except Exception as e:
                    print(f"Error evaluating {name}: {e}")

        return results

    def export_metrics(self, metrics: TopologyMetrics, filepath: str) -> None:
        """Export metrics to JSON."""
        with open(filepath, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)

    def load_metrics(self, filepath: str) -> TopologyMetrics:
        """Load metrics from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return TopologyMetrics(**data)


if __name__ == "__main__":
    # Example usage
    from topology_generator import TopologyGenerator, TopologyType, TopologyParams, generate_benchmark_topologies

    evaluator = TopologyEvaluator(parallel=True)

    for n in [10, 50, 100]:
        print(f"\nEvaluating topologies for colony size {n}")

        topologies = generate_benchmark_topologies(n, seed=42)
        topology_list = [(name, G) for name, (G, _, _) in topologies.items()]

        results = evaluator.batch_evaluate(topology_list)

        # Sort by score
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)

        for name, (metrics, score) in sorted_results:
            print(f"\n{name}:")
            print(f"  Score: {score:.3f}")
            print(f"  Avg Path Length: {metrics.avg_path_length:.3f}")
            print(f"  Clustering: {metrics.clustering_coefficient:.3f}")
            print(f"  Global Efficiency: {metrics.global_efficiency:.3f}")
            print(f"  Attack Tolerance: {metrics.attack_tolerance:.3f}")
