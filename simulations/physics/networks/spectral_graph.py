"""
Spectral Graph Theory Analysis for POLLN Networks

This module implements advanced spectral graph theory techniques for analyzing
the communication structure of POLLN agent networks. Uses DeepSeek-derived
mathematical frameworks for rigorous analysis.

Author: POLLN Network Science Team
Date: 2026-03-07
"""

import numpy as np
import scipy.linalg as la
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import networkx as nx
from pathlib import Path
import json

from deepseek_networks import DeepSeekNetworkDeriver


@dataclass
class SpectralProperties:
    """Container for spectral properties of a graph."""
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    fiedler_value: float
    fiedler_vector: np.ndarray
    spectral_gap: float
    algebraic_connectivity: float
    cheeger_constant_estimate: float
    expansion_ratio: float
    is_expander: bool
    is_ramanujan: bool


@dataclass
class SpectralClusterResult:
    """Container for spectral clustering results."""
    labels: np.ndarray
    n_clusters: int
    modularity: float
    conductance: float
    cluster_sizes: List[int]
    spectral_embeddings: np.ndarray


class SpectralGraphAnalyzer:
    """
    Advanced spectral graph theory analysis for POLLN networks.

    Implements:
    - Graph Laplacian spectral analysis
    - Algebraic connectivity estimation
    - Spectral clustering
    - Cheeger inequalities
    - Expander graph detection
    - Ramanujan graph verification
    """

    def __init__(self, use_deepseek: bool = True):
        """
        Initialize the spectral graph analyzer.

        Args:
            use_deepseek: Whether to use DeepSeek for theoretical derivations
        """
        self.use_deepseek = use_deepseek
        if use_deepseek:
            self.deriver = DeepSeekNetworkDeriver()
            self.theory = self.deriver.derive_spectral_theory()
        else:
            self.deriver = None
            self.theory = None

        self.cache_dir = Path(__file__).parent / ".spectral_cache"
        self.cache_dir.mkdir(exist_ok=True)

    def compute_laplacian(self,
                         adj_matrix: Union[np.ndarray, sp.spmatrix],
                         normalized: bool = True) -> Union[np.ndarray, sp.spmatrix]:
        """
        Compute graph Laplacian matrix.

        Args:
            adj_matrix: Adjacency matrix (sparse or dense)
            normalized: Whether to use normalized Laplacian

        Returns:
            Laplacian matrix L = D - A (combinatorial) or
            L = I - D^(-1/2) A D^(-1/2) (normalized)
        """
        if sp.issparse(adj_matrix):
            return self._compute_laplacian_sparse(adj_matrix, normalized)
        else:
            return self._compute_laplacian_dense(adj_matrix, normalized)

    def _compute_laplacian_dense(self,
                                 adj_matrix: np.ndarray,
                                 normalized: bool) -> np.ndarray:
        """Compute Laplacian for dense matrix."""
        degrees = np.sum(adj_matrix, axis=1)
        D = np.diag(degrees)

        if not normalized:
            # Combinatorial Laplacian: L = D - A
            L = D - adj_matrix
        else:
            # Normalized Laplacian: L = I - D^(-1/2) A D^(-1/2)
            D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees + 1e-10))
            L = np.eye(adj_matrix.shape[0]) - D_inv_sqrt @ adj_matrix @ D_inv_sqrt

        return L

    def _compute_laplacian_sparse(self,
                                  adj_matrix: sp.spmatrix,
                                  normalized: bool) -> sp.spmatrix:
        """Compute Laplacian for sparse matrix."""
        degrees = np.array(adj_matrix.sum(axis=1)).flatten()
        D = sp.diags(degrees)

        if not normalized:
            L = D - adj_matrix
        else:
            D_inv_sqrt = sp.diags(1.0 / np.sqrt(degrees + 1e-10))
            L = sp.eye(adj_matrix.shape[0]) - D_inv_sqrt @ adj_matrix @ D_inv_sqrt

        return L

    def compute_spectrum(self,
                        laplacian: Union[np.ndarray, sp.spmatrix],
                        k: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute eigenvalues and eigenvectors of Laplacian.

        Args:
            laplacian: Laplacian matrix
            k: Number of eigenvalues to compute (None = all)

        Returns:
            Tuple of (eigenvalues, eigenvectors)
        """
        if sp.issparse(laplacian):
            if k is None:
                k = min(laplacian.shape[0] - 1, 100)
            # Use sparse eigensolver for large graphs
            eigenvalues, eigenvectors = spla.eigsh(
                laplacian,
                k=k,
                which='SM'  # Smallest magnitude
            )
        else:
            # Use dense eigensolver for small graphs
            eigenvalues, eigenvectors = la.eigh(laplacian)

            if k is not None:
                eigenvalues = eigenvalues[:k]
                eigenvectors = eigenvectors[:, :k]

        # Sort eigenvalues
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        return eigenvalues, eigenvectors

    def analyze_spectral_properties(self,
                                   adj_matrix: Union[np.ndarray, sp.spmatrix],
                                   max_degree: Optional[int] = None) -> SpectralProperties:
        """
        Perform comprehensive spectral analysis.

        Args:
            adj_matrix: Adjacency matrix
            max_degree: Maximum degree for expander test (auto-detected if None)

        Returns:
            SpectralProperties object with complete spectral analysis
        """
        n = adj_matrix.shape[0]

        # Compute Laplacian and spectrum
        L = self.compute_laplacian(adj_matrix, normalized=True)
        eigenvalues, eigenvectors = self.compute_spectrum(L)

        # Fiedler value and vector (2nd smallest eigenvalue/vector)
        fiedler_value = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
        fiedler_vector = eigenvectors[:, 1] if eigenvectors.shape[1] > 1 else np.zeros(n)

        # Spectral gap
        spectral_gap = eigenvalues[1] - eigenvalues[0] if len(eigenvalues) > 1 else 0.0

        # Algebraic connectivity (Fiedler value)
        algebraic_connectivity = fiedler_value

        # Cheeger constant estimate (using Cheeger inequality)
        # h²/2 ≤ λ₂ ≤ 2h, so h ≥ λ₂/2 and h ≥ √(λ₂/2)
        cheeger_lower = fiedler_value / 2
        cheeger_upper = 2 * fiedler_value
        cheeger_constant_estimate = np.sqrt(fiedler_value / 2)

        # Expansion ratio
        if max_degree is None:
            if sp.issparse(adj_matrix):
                degrees = np.array(adj_matrix.sum(axis=1)).flatten()
            else:
                degrees = np.sum(adj_matrix, axis=1)
            max_degree = int(np.max(degrees))

        # λ₂ ≥ d(1 - √(1 - h²)) suggests expander if λ₂ is large
        # For d-regular graphs, λ₂ small is good for expansion
        expansion_ratio = fiedler_value

        # Check if expander (λ₂ bounded away from 0)
        is_expander = fiedler_value > 0.1  # Heuristic threshold

        # Check if Ramanujan (for d-regular graphs, non-trivial eigenvalues ≤ 2√(d-1))
        if max_degree > 1:
            ramanujan_bound = 2 * np.sqrt(max_degree - 1)
            # Check if all non-trivial eigenvalues satisfy the bound
            non_trivial_eigs = eigenvalues[1:-1] if len(eigenvalues) > 2 else []
            is_ramanujan = all(np.abs(eig) <= ramanujan_bound for eig in non_trivial_eigs)
        else:
            is_ramanujan = False

        return SpectralProperties(
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            fiedler_value=fiedler_value,
            fiedler_vector=fiedler_vector,
            spectral_gap=spectral_gap,
            algebraic_connectivity=algebraic_connectivity,
            cheeger_constant_estimate=cheeger_constant_estimate,
            expansion_ratio=expansion_ratio,
            is_expander=is_expander,
            is_ramanujan=is_ramanujan
        )

    def spectral_clustering(self,
                           adj_matrix: Union[np.ndarray, sp.spmatrix],
                           n_clusters: int) -> SpectralClusterResult:
        """
        Perform spectral clustering using normalized cuts.

        Args:
            adj_matrix: Adjacency matrix
            n_clusters: Number of clusters

        Returns:
            SpectralClusterResult with clustering results
        """
        n = adj_matrix.shape[0]

        # Compute normalized Laplacian
        L = self.compute_laplacian(adj_matrix, normalized=True)

        # Compute first k eigenvectors (corresponding to smallest eigenvalues)
        eigenvalues, eigenvectors = self.compute_spectrum(L, k=n_clusters)

        # Use eigenvectors as embeddings (skip first eigenvector which is constant)
        embeddings = eigenvectors[:, 1:n_clusters] if n_clusters > 1 else eigenvectors[:, :1]

        # Normalize rows
        embeddings_norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings_norm = embeddings / (embeddings_norm + 1e-10)

        # K-means clustering on embeddings
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
        labels = kmeans.fit_predict(embeddings_norm)

        # Compute cluster statistics
        cluster_sizes = [int(np.sum(labels == i)) for i in range(n_clusters)]

        # Compute conductance for each cluster
        conductances = []
        for i in range(n_clusters):
            mask = labels == i
            cluster_nodes = np.where(mask)[0]
            conductance = self._compute_conductance(adj_matrix, cluster_nodes, n)
            conductances.append(conductance)

        avg_conductance = float(np.mean(conductances))

        # Compute modularity
        modularity = self._compute_modularity(adj_matrix, labels)

        return SpectralClusterResult(
            labels=labels,
            n_clusters=n_clusters,
            modularity=modularity,
            conductance=avg_conductance,
            cluster_sizes=cluster_sizes,
            spectral_embeddings=embeddings_norm
        )

    def _compute_conductance(self,
                            adj_matrix: Union[np.ndarray, sp.spmatrix],
                            cluster_nodes: np.ndarray,
                            n: int) -> float:
        """Compute conductance of a cluster."""
        if sp.issparse(adj_matrix):
            adj_matrix = adj_matrix.toarray()

        cluster_set = set(cluster_nodes)
        cluster_size = len(cluster_nodes)

        if cluster_size == 0 or cluster_size == n:
            return 0.0

        # Count edges crossing the cut
        cut_edges = 0
        for i in cluster_nodes:
            for j in range(n):
                if j not in cluster_set and adj_matrix[i, j] > 0:
                    cut_edges += adj_matrix[i, j]

        # Count edges inside cluster
        internal_edges = 0
        for i in cluster_nodes:
            for j in cluster_nodes:
                if i < j and adj_matrix[i, j] > 0:
                    internal_edges += adj_matrix[i, j]

        # Conductance
        vol = cut_edges + internal_edges
        if vol == 0:
            return 0.0

        return cut_edges / vol

    def _compute_modularity(self,
                           adj_matrix: Union[np.ndarray, sp.spmatrix],
                           labels: np.ndarray) -> float:
        """Compute modularity of clustering."""
        if sp.issparse(adj_matrix):
            adj_matrix = adj_matrix.toarray()

        n = adj_matrix.shape[0]
        m = np.sum(adj_matrix) / 2  # Total edges (undirected)

        if m == 0:
            return 0.0

        # Degree of each node
        degrees = np.sum(adj_matrix, axis=1)

        # Compute modularity
        Q = 0.0
        for i in range(n):
            for j in range(n):
                if labels[i] == labels[j]:
                    expected = degrees[i] * degrees[j] / (2 * m)
                    Q += (adj_matrix[i, j] - expected)

        Q = Q / (2 * m)

        return float(Q)

    def detect_bottlenecks(self,
                          spectral_props: SpectralProperties,
                          threshold: float = 0.1) -> List[int]:
        """
        Detect bottleneck nodes using Fiedler vector.

        Args:
            spectral_props: Spectral properties from analysis
            threshold: Threshold for bottleneck detection

        Returns:
            List of bottleneck node indices
        """
        fiedler = spectral_props.fiedler_vector

        # Nodes with Fiedler values near zero are potential bottlenecks
        # These are nodes that, if removed, would disconnect the graph
        bottlenecks = []

        # Use zero crossings and small values
        median_val = np.median(fiedler)
        std_val = np.std(fiedler)

        for i, val in enumerate(fiedler):
            if abs(val - median_val) < threshold * std_val:
                bottlenecks.append(i)

        return bottlenecks

    def compute_spectral_partition(self,
                                   spectral_props: SpectralProperties) -> Tuple[List[int], List[int]]:
        """
        Partition graph using Fiedler vector sign.

        Args:
            spectral_props: Spectral properties from analysis

        Returns:
            Tuple of (partition1_nodes, partition2_nodes)
        """
        fiedler = spectral_props.fiedler_vector

        # Partition by sign of Fiedler vector
        partition1 = np.where(fiedler >= 0)[0].tolist()
        partition2 = np.where(fiedler < 0)[0].tolist()

        return partition1, partition2

    def estimate_network_diameter(self,
                                  spectral_props: SpectralProperties,
                                  n: int) -> float:
        """
        Estimate network diameter using spectral bounds.

        Uses the inequality: diam(G) ≤ ⌈3/(λ₂ ln(2/Δ))⌉ where Δ is max degree

        Args:
            spectral_props: Spectral properties from analysis
            n: Number of nodes

        Returns:
            Estimated diameter
        """
        fiedler_value = spectral_props.fiedler_value

        if fiedler_value < 1e-10:
            return float(n)  # Disconnected graph

        # Use spectral bound
        diameter_estimate = 3.0 / (fiedler_value * np.log(2.0 / 0.5))

        return min(diameter_estimate, float(n))

    def save_results(self,
                    spectral_props: SpectralProperties,
                    filename: str):
        """
        Save spectral analysis results to file.

        Args:
            spectral_props: Spectral properties to save
            filename: Output filename
        """
        filepath = self.cache_dir / filename

        # Convert numpy arrays to lists for JSON serialization
        data = {
            'eigenvalues': spectral_props.eigenvalues.tolist(),
            'eigenvectors': spectral_props.eigenvectors.tolist(),
            'fiedler_value': float(spectral_props.fiedler_value),
            'fiedler_vector': spectral_props.fiedler_vector.tolist(),
            'spectral_gap': float(spectral_props.spectral_gap),
            'algebraic_connectivity': float(spectral_props.algebraic_connectivity),
            'cheeger_constant_estimate': float(spectral_props.cheeger_constant_estimate),
            'expansion_ratio': float(spectral_props.expansion_ratio),
            'is_expander': bool(spectral_props.is_expander),
            'is_ramanujan': bool(spectral_props.is_ramanujan)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_results(self, filename: str) -> SpectralProperties:
        """
        Load spectral analysis results from file.

        Args:
            filename: Input filename

        Returns:
            SpectralProperties object
        """
        filepath = self.cache_dir / filename

        with open(filepath, 'r') as f:
            data = json.load(f)

        return SpectralProperties(
            eigenvalues=np.array(data['eigenvalues']),
            eigenvectors=np.array(data['eigenvectors']),
            fiedler_value=data['fiedler_value'],
            fiedler_vector=np.array(data['fiedler_vector']),
            spectral_gap=data['spectral_gap'],
            algebraic_connectivity=data['algebraic_connectivity'],
            cheeger_constant_estimate=data['cheeger_constant_estimate'],
            expansion_ratio=data['expansion_ratio'],
            is_expander=data['is_expander'],
            is_ramanujan=data['is_ramanujan']
        )


def analyze_polln_network(adj_matrix: Union[np.ndarray, sp.spmatrix],
                          use_deepseek: bool = True) -> Dict:
    """
    Perform complete spectral analysis of POLLN network.

    Args:
        adj_matrix: Adjacency matrix of POLLN communication graph
        use_deepseek: Whether to use DeepSeek for theoretical guidance

    Returns:
        Dictionary with complete spectral analysis
    """
    analyzer = SpectralGraphAnalyzer(use_deepseek=use_deepseek)

    # Compute spectral properties
    spectral_props = analyzer.analyze_spectral_properties(adj_matrix)

    # Perform spectral clustering for different k values
    cluster_results = {}
    for k in [2, 3, 4, 5]:
        if k <= adj_matrix.shape[0]:
            try:
                result = analyzer.spectral_clustering(adj_matrix, k)
                cluster_results[f'k_{k}'] = {
                    'modularity': result.modularity,
                    'conductance': result.conductance,
                    'cluster_sizes': result.cluster_sizes
                }
            except Exception as e:
                cluster_results[f'k_{k}'] = {'error': str(e)}

    # Detect bottlenecks
    bottlenecks = analyzer.detect_bottlenecks(spectral_props)

    # Estimate diameter
    diameter = analyzer.estimate_network_diameter(
        spectral_props,
        adj_matrix.shape[0]
    )

    # Spectral partition
    partition1, partition2 = analyzer.compute_spectral_partition(spectral_props)

    return {
        'spectral_properties': {
            'fiedler_value': float(spectral_props.fiedler_value),
            'spectral_gap': float(spectral_props.spectral_gap),
            'algebraic_connectivity': float(spectral_props.algebraic_connectivity),
            'cheeger_constant': float(spectral_props.cheeger_constant_estimate),
            'expansion_ratio': float(spectral_props.expansion_ratio),
            'is_expander': bool(spectral_props.is_expander),
            'is_ramanujan': bool(spectral_props.is_ramanujan),
            'estimated_diameter': float(diameter)
        },
        'clustering': cluster_results,
        'bottlenecks': bottlenecks,
        'partition': {
            'partition1_size': len(partition1),
            'partition2_size': len(partition2)
        },
        'eigenvalue_distribution': {
            'mean': float(np.mean(spectral_props.eigenvalues)),
            'std': float(np.std(spectral_props.eigenvalues)),
            'min': float(np.min(spectral_props.eigenvalues)),
            'max': float(np.max(spectral_props.eigenvalues))
        }
    }


if __name__ == "__main__":
    # Test with synthetic network
    print("Creating synthetic network...")

    # Create a random graph
    n = 100
    p = 0.1
    G = nx.erdos_renyi_graph(n, p, seed=42)
    adj_matrix = nx.to_scipy_sparse_array(G)

    print(f"Network: {n} nodes, {G.number_of_edges()} edges")

    # Perform spectral analysis
    print("\nPerforming spectral analysis...")
    results = analyze_polln_network(adj_matrix, use_deepseek=True)

    print("\n=== SPECTRAL ANALYSIS RESULTS ===\n")

    print("Spectral Properties:")
    for key, value in results['spectral_properties'].items():
        print(f"  {key}: {value}")

    print("\nClustering Results:")
    for k, result in results['clustering'].items():
        if 'error' not in result:
            print(f"  {k}:")
            print(f"    Modularity: {result['modularity']:.4f}")
            print(f"    Conductance: {result['conductance']:.4f}")
            print(f"    Cluster sizes: {result['cluster_sizes']}")
        else:
            print(f"  {k}: {result['error']}")

    print(f"\nBottlenecks detected: {len(results['bottlenecks'])}")
    print(f"Partition sizes: {results['partition']['partition1_size']} vs {results['partition']['partition2_size']}")

    print("\nEigenvalue Distribution:")
    for key, value in results['eigenvalue_distribution'].items():
        print(f"  {key}: {value:.4f}")

    print("\nSpectral analysis complete!")
