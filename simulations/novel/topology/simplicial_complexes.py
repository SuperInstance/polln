"""
Simplicial Complex Construction for Network Analysis

This module implements constructions of various simplicial complexes from
network data, including clique complexes, Vietoris-Rips complexes, and Čech complexes.
"""

import numpy as np
from typing import List, Set, Tuple, Dict, Optional, Any
from itertools import combinations, chain
from collections import defaultdict
import networkx as nx
from scipy.spatial import distance_matrix
from dataclasses import dataclass

from .deepseek_topology import DeepSeekTopologyDeriver


@dataclass
class Simplex:
    """Represents a simplex (unordered set of vertices)."""

    vertices: Tuple[int, ...]

    def __post_init__(self):
        """Ensure vertices are sorted and unique."""
        self.vertices = tuple(sorted(set(self.vertices)))

    @property
    def dimension(self) -> int:
        """Dimension of simplex: |vertices| - 1."""
        return len(self.vertices) - 1

    def faces(self) -> List['Simplex']:
        """Return all proper faces of this simplex."""
        result = []
        for i in range(len(self.vertices)):
            face_verts = self.vertices[:i] + self.vertices[i+1:]
            if len(face_verts) > 0:
                result.append(Simplex(face_verts))
        return result

    def __contains__(self, vertex: int) -> bool:
        """Check if vertex is in simplex."""
        return vertex in self.vertices

    def __eq__(self, other: 'Simplex') -> bool:
        """Check equality of simplices."""
        return self.vertices == other.vertices

    def __hash__(self) -> int:
        """Hash function for using simplices in sets."""
        return hash(self.vertices)

    def __repr__(self) -> str:
        """String representation."""
        return f"Simplex({self.vertices})"

    def __len__(self) -> int:
        """Number of vertices."""
        return len(self.vertices)


class SimplicialComplex:
    """
    Abstract simplicial complex.

    A simplicial complex K is a set of simplices closed under taking faces.
    """

    def __init__(self):
        """Initialize empty simplicial complex."""
        self.simplices: Dict[int, Set[Simplex]] = defaultdict(set)

    def add_simplex(self, vertices: Tuple[int, ...]) -> bool:
        """
        Add a simplex and all its faces to the complex.

        Args:
            vertices: Tuple of vertex indices

        Returns:
            True if simplex was added, False if already present
        """
        simplex = Simplex(vertices)

        # Check if already present
        if simplex in self.simplices[simplex.dimension]:
            return False

        # Add simplex
        self.simplices[simplex.dimension].add(simplex)

        # Recursively add all faces
        for face in simplex.faces():
            self.add_simplex(face.vertices)

        return True

    def add_simplices(self, simplices: List[Tuple[int, ...]]) -> int:
        """
        Add multiple simplices.

        Args:
            simplices: List of vertex tuples

        Returns:
            Number of simplices added
        """
        count = 0
        for verts in simplices:
            if self.add_simplex(verts):
                count += 1
        return count

    def get_simplices_of_dimension(self, dim: int) -> Set[Simplex]:
        """Get all simplices of given dimension."""
        return self.simplices.get(dim, set())

    @property
    def dimension(self) -> int:
        """Maximum dimension of any simplex in complex."""
        dims = [d for d, s in self.simplices.items() if len(s) > 0]
        return max(dims) if dims else -1

    @property
    def num_simplices(self) -> int:
        """Total number of simplices in complex."""
        return sum(len(s) for s in self.simplices.values())

    @property
    def num_vertices(self) -> int:
        """Number of 0-simplices (vertices)."""
        return len(self.simplices.get(0, set()))

    @property
    def vertices(self) -> Set[int]:
        """Set of all vertices in complex."""
        verts = set()
        for simplex in self.simplices[0]:
            verts.update(simplex.vertices)
        return verts

    def facets(self) -> List[Simplex]:
        """
        Return all facets (maximal faces) of the complex.

        A facet is a simplex that is not a proper face of any other simplex.
        """
        all_simplices = set()
        for dim_simplices in self.simplices.values():
            all_simplices.update(dim_simplices)

        facets = []
        for simplex in all_simplices:
            # Check if simplex is maximal
            is_maximal = True
            for other in all_simplices:
                if (simplex != other and
                    len(other.vertices) > len(simplex.vertices) and
                    set(simplex.vertices).issubset(set(other.vertices))):
                    is_maximal = False
                    break

            if is_maximal and len(simplex.vertices) > 0:
                facets.append(simplex)

        return facets

    def skeleton(self, dim: int) -> 'SimplicialComplex':
        """
        Return the k-skeleton (all simplices of dimension ≤ k).

        Args:
            dim: Maximum dimension

        Returns:
            New simplicial complex with only simplices of dimension ≤ dim
        """
        skeleton = SimplicialComplex()
        for d in range(min(dim + 1, self.dimension + 1)):
            for simplex in self.simplices.get(d, set()):
                skeleton.add_simplex(simplex.vertices)
        return skeleton

    def euler_characteristic(self) -> int:
        """
        Compute Euler characteristic χ.

        χ = Σ(-1)^k * f_k where f_k = number of k-simplices.
        """
        chi = 0
        for dim, simplices in self.simplices.items():
            chi += ((-1) ** dim) * len(simplices)
        return chi

    def f_vector(self) -> List[int]:
        """
        Compute f-vector (f_0, f_1, ..., f_d).

        f_k = number of k-simplices.
        """
        max_dim = self.dimension
        f_vec = []
        for d in range(max_dim + 1):
            f_vec.append(len(self.simplices.get(d, set())))
        return f_vec

    def __repr__(self) -> str:
        """String representation."""
        return (f"SimplicialComplex(dim={self.dimension}, "
                f"num_simplices={self.num_simplices}, "
                f"num_vertices={self.num_vertices})")


class CliqueComplex(SimplicialComplex):
    """
    Clique complex (flag complex) constructed from a graph.

    Every k-clique in the graph becomes a (k-1)-simplex.
    """

    def __init__(self, graph: Optional[nx.Graph] = None):
        """
        Initialize clique complex.

        Args:
            graph: NetworkX graph to construct complex from
        """
        super().__init__()

        if graph is not None:
            self.from_graph(graph)

    def from_graph(self, graph: nx.Graph) -> None:
        """
        Construct clique complex from graph.

        Every k-clique becomes a (k-1)-simplex.

        Args:
            graph: NetworkX graph
        """
        # Add all vertices as 0-simplices
        for node in graph.nodes():
            self.add_simplex((node,))

        # Find all cliques and add as simplices
        # Use NetworkX's clique finder
        for clique in nx.find_cliques(graph):
            if len(clique) > 1:  # Skip single vertices (already added)
                self.add_simplex(tuple(clique))

    @classmethod
    def from_adjacency_matrix(cls, adj_matrix: np.ndarray) -> 'CliqueComplex':
        """
        Construct clique complex from adjacency matrix.

        Args:
            adj_matrix: Symmetric adjacency matrix

        Returns:
            CliqueComplex
        """
        # Convert to NetworkX graph
        graph = nx.from_numpy_array(adj_matrix)
        return cls(graph)


class VietorisRipsComplex(SimplicialComplex):
    """
    Vietoris-Rips complex constructed from point cloud data.

    At scale ε, form a simplex for every set of points with pairwise
    distances ≤ ε.
    """

    def __init__(self, points: Optional[np.ndarray] = None,
                 max_dimension: int = 3):
        """
        Initialize VR complex.

        Args:
            points: Point cloud data (n_samples, n_features)
            max_dimension: Maximum simplex dimension to compute
        """
        super().__init__()
        self.points = points
        self.max_dimension = max_dimension

        if points is not None:
            self.distance_matrix = distance_matrix(points, points)

    def from_points(self, points: np.ndarray, epsilon: float,
                    max_dimension: Optional[int] = None) -> None:
        """
        Construct VR complex from points at scale ε.

        Args:
            points: Point cloud (n_samples, n_features)
            epsilon: Distance scale parameter
            max_dimension: Maximum simplex dimension
        """
        self.points = points
        self.distance_matrix = distance_matrix(points, points)
        self.max_dimension = max_dimension or self.max_dimension

        # Find all simplices with diameter ≤ ε
        n_points = len(points)

        # Add all vertices
        for i in range(n_points):
            self.add_simplex((i,))

        # Build adjacency for 1-skeleton
        edges = []
        for i in range(n_points):
            for j in range(i + 1, n_points):
                if self.distance_matrix[i, j] <= epsilon:
                    edges.append((i, j))
                    self.add_simplex((i, j))

        # Higher-dimensional simplices: cliques in 1-skeleton
        # Create graph of edges
        graph = nx.Graph()
        graph.add_nodes_from(range(n_points))
        graph.add_edges_from(edges)

        # Find cliques up to max_dimension + 1
        for clique in nx.find_cliques(graph):
            k = len(clique) - 1  # simplex dimension
            if k <= self.max_dimension and k > 1:
                self.add_simplex(tuple(clique))

    def filtration(self, epsilon_max: float, num_steps: int = 100) -> List['SimplicialComplex']:
        """
        Generate VR filtration from ε=0 to ε=epsilon_max.

        Args:
            epsilon_max: Maximum scale
            num_steps: Number of filtration steps

        Returns:
            List of simplicial complexes at increasing scales
        """
        epsilons = np.linspace(0, epsilon_max, num_steps)
        filtration = []

        for eps in epsilons:
            complex = VietorisRipsComplex(self.points, self.max_dimension)
            complex.from_points(self.points, eps, self.max_dimension)
            filtration.append(complex)

        return filtration


class CechComplex(SimplicialComplex):
    """
    Čech complex constructed from ball coverings.

    For a set of balls B(p, ε), form a simplex when the intersection
    of all corresponding balls is non-empty.
    """

    def __init__(self, points: Optional[np.ndarray] = None,
                 max_dimension: int = 3):
        """
        Initialize Čech complex.

        Args:
            points: Point cloud data (n_samples, n_features)
            max_dimension: Maximum simplex dimension to compute
        """
        super().__init__()
        self.points = points
        self.max_dimension = max_dimension

    def from_points(self, points: np.ndarray, epsilon: float,
                    max_dimension: Optional[int] = None,
                    approximation: str = 'rips') -> None:
        """
        Construct Čech complex from points at scale ε.

        Note: Exact Čech is computationally expensive. We use the
        Vietoris-Rips complex as an approximation by default.

        Args:
            points: Point cloud (n_samples, n_features)
            epsilon: Ball radius parameter
            max_dimension: Maximum simplex dimension
            approximation: 'rips' (Vietoris-Rips) or 'exact' (intersection)
        """
        self.points = points
        self.max_dimension = max_dimension or self.max_dimension

        if approximation == 'rips':
            # VR ⊆ Čech ⊆ VR_{2ε} (inclusion up to scale 2)
            vr_complex = VietorisRipsComplex(points)
            vr_complex.from_points(points, epsilon, self.max_dimension)

            # Copy VR simplices
            for dim, simplices in vr_complex.simplices.items():
                for simplex in simplices:
                    self.add_simplex(simplex.vertices)

        elif approximation == 'exact':
            # Exact Čech: check non-empty intersection of balls
            # This is very expensive for high dimensions
            self._exact_cech(points, epsilon)

    def _exact_cech(self, points: np.ndarray, epsilon: float) -> None:
        """
        Compute exact Čech complex (expensive!).

        Only for small datasets or low dimensions.
        """
        from scipy.optimize import minimize

        n_points = len(points)
        dim = points.shape[1]

        # Add all vertices
        for i in range(n_points):
            self.add_simplex((i,))

        # Function to check if balls have non-empty intersection
        def balls_intersect(indices):
            """Check if intersection of balls is non-empty."""

            # Optimization: find point minimizing max distance to centers
            def max_dist_to_centers(x):
                dists = [np.linalg.norm(x - points[i]) for i in indices]
                return max(dists)

            # Start at centroid
            centroid = np.mean([points[i] for i in indices], axis=0)

            # Minimize maximum distance
            result = minimize(
                max_dist_to_centers,
                centroid,
                method='Nelder-Mead'
            )

            # Check if min max distance ≤ ε
            return result.fun <= epsilon

        # Check all subsets
        for k in range(2, min(n_points + 1, self.max_dimension + 2)):
            for subset in combinations(range(n_points), k):
                if balls_intersect(subset):
                    self.add_simplex(subset)


class NerveComplex(SimplicialComplex):
    """
    Nerve of a cover.

    Given a cover {U_i} of a space X, the nerve is a simplicial complex
    where a simplex {i_0, ..., i_k} exists iff U_{i_0} ∩ ... ∩ U_{i_k} ≠ ∅.
    """

    def __init__(self, cover_sets: Optional[List[Set[Any]]] = None):
        """
        Initialize nerve complex.

        Args:
            cover_sets: List of sets representing the cover
        """
        super().__init__()

        if cover_sets is not None:
            self.from_cover(cover_sets)

    def from_cover(self, cover_sets: List[Set[Any]]) -> None:
        """
        Construct nerve from cover.

        Args:
            cover_sets: List of sets in the cover
        """
        n_sets = len(cover_sets)

        # Add all vertices
        for i in range(n_sets):
            self.add_simplex((i,))

        # Check all intersections
        for k in range(2, n_sets + 1):
            for subset in combinations(range(n_sets), k):
                # Check if intersection is non-empty
                intersection = set.intersection(
                    *[cover_sets[i] for i in subset]
                )

                if len(intersection) > 0:
                    self.add_simplex(subset)


def verify_nerve_theorem(cover_sets: List[Set[Any]]) -> bool:
    """
    Verify nerve theorem conditions for a cover.

    The nerve theorem states that if {U_i} is a good cover (all finite
    intersections are contractible), then Nerve({U_i}) ≃ ∪ U_i.

    Args:
        cover_sets: List of sets in the cover

    Returns:
        True if cover is good (contractible intersections), False otherwise
    """
    # Check all finite intersections
    for k in range(1, len(cover_sets) + 1):
        for subset in combinations(range(len(cover_sets)), k):
            intersection = set.intersection(
                *[cover_sets[i] for i in subset]
            )

            # Check if intersection is contractible
            # For discrete sets, contractible means empty or single point
            if len(intersection) > 1:
                return False  # Not contractible

    return True


def geometric_realization(complex: SimplicialComplex,
                         embedding_dim: int = 3) -> Dict[int, np.ndarray]:
    """
    Compute geometric realization of simplicial complex.

    Places vertices in general position and computes coordinates.

    Args:
        complex: Simplicial complex
        embedding_dim: Dimension for embedding

    Returns:
        Dictionary mapping vertex indices to coordinates
    """
    vertices = list(complex.vertices)
    n_verts = len(vertices)

    # Place vertices randomly in general position
    coords = np.random.randn(n_verts, embedding_dim)

    # Apply small perturbation for general position
    coords += np.random.randn(*coords.shape) * 1e-6

    return {v: coords[i] for i, v in enumerate(vertices)}


def compare_complexes(K1: SimplicialComplex, K2: SimplicialComplex) -> Dict[str, Any]:
    """
    Compare two simplicial complexes.

    Args:
        K1: First complex
        K2: Second complex

    Returns:
        Dictionary of comparison metrics
    """
    return {
        'K1_dimension': K1.dimension,
        'K2_dimension': K2.dimension,
        'K1_num_simplices': K1.num_simplices,
        'K2_num_simplices': K2.num_simplices,
        'K1_euler': K1.euler_characteristic(),
        'K2_euler': K2.euler_characteristic(),
        'K1_f_vector': K1.f_vector(),
        'K2_f_vector': K2.f_vector()
    }


# ============================================================================
# POLLN-Specific Functions
# ============================================================================

def agent_network_to_clique_complex(colony) -> CliqueComplex:
    """
    Convert POLLN agent colony to clique complex.

    Agents become vertices, communication edges become 1-simplices,
    and cooperating agent groups become higher simplices.

    Args:
        colony: POLLN colony object

    Returns:
        CliqueComplex representing agent network
    """
    # Build communication graph
    graph = nx.Graph()

    # Add all agents
    for agent_id in colony.agents.keys():
        graph.add_node(agent_id)

    # Add communication edges
    for agent_id, agent in colony.agents.items():
        for target_id in agent.outgoing_connections:
            graph.add_edge(agent_id, target_id)

    # Construct clique complex
    complex = CliqueComplex(graph)

    return complex


def synapse_network_vr_complex(embeddings: np.ndarray,
                               epsilon: float = 0.5,
                               max_dimension: int = 3) -> VietorisRipsComplex:
    """
    Construct VR complex from synapse embeddings.

    Args:
        embeddings: Synapse embedding matrix (n_synapses, embedding_dim)
        epsilon: Distance scale
        max_dimension: Maximum simplex dimension

    Returns:
        VietorisRipsComplex
    """
    vr_complex = VietorisRipsComplex(embeddings, max_dimension)
    vr_complex.from_points(embeddings, epsilon, max_dimension)

    return vr_complex


def analyze_network_topology(graph: nx.Graph) -> Dict[str, Any]:
    """
    Analyze topological features of a network.

    Args:
        graph: NetworkX graph

    Returns:
        Dictionary of topological features
    """
    # Construct clique complex
    complex = CliqueComplex(graph)

    return {
        'num_vertices': complex.num_vertices,
        'num_edges': len(complex.get_simplices_of_dimension(1)),
        'num_triangles': len(complex.get_simplices_of_dimension(2)),
        'num_tetrahedra': len(complex.get_simplices_of_dimension(3)),
        'max_clique_size': complex.dimension + 1,
        'euler_characteristic': complex.euler_characteristic(),
        'f_vector': complex.f_vector(),
        'num_facets': len(complex.facets())
    }


# ============================================================================
# DeepSeek Integration
# ============================================================================

def derive_with_deepseek() -> str:
    """Use DeepSeek to derive simplicial complex theory."""
    deriver = DeepSeekTopologyDeriver()
    return deriver.derive_simplicial_complexes()


if __name__ == "__main__":
    # Example usage
    print("Simplicial Complex Examples\n")

    # Example 1: Clique complex from graph
    print("1. Clique Complex from Graph")
    G = nx.karate_club_graph()
    clique_complex = CliqueComplex(G)
    print(f"   Dimension: {clique_complex.dimension}")
    print(f"   Simplices: {clique_complex.num_simplices}")
    print(f"   Euler characteristic: {clique_complex.euler_characteristic()}")
    print(f"   f-vector: {clique_complex.f_vector()}")
    print()

    # Example 2: Vietoris-Rips complex
    print("2. Vietoris-Rips Complex")
    points = np.random.randn(20, 2)
    vr_complex = VietorisRipsComplex(points, max_dimension=2)
    vr_complex.from_points(points, epsilon=1.0)
    print(f"   Dimension: {vr_complex.dimension}")
    print(f"   Simplices: {vr_complex.num_simplices}")
    print(f"   Euler characteristic: {vr_complex.euler_characteristic()}")
    print()

    # Example 3: Nerve complex
    print("3. Nerve Complex")
    cover = [
        {1, 2, 3},
        {2, 3, 4},
        {3, 4, 5},
        {4, 5, 6}
    ]
    nerve = NerveComplex(cover)
    print(f"   Dimension: {nerve.dimension}")
    print(f"   Simplices: {nerve.num_simplices}")
    print()

    # Example 4: Network analysis
    print("4. Network Topology Analysis")
    topology = analyze_network_topology(G)
    for key, value in topology.items():
        print(f"   {key}: {value}")
    print()

    # Example 5: DeepSeek derivation
    print("5. DeepSeek Derivation")
    try:
        derivation = derive_with_deepseek()
        print(f"   Got {len(derivation)} characters of theory")
    except Exception as e:
        print(f"   Error: {e}")
