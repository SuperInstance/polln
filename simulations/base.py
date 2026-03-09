"""
POLLN Graph Evolution Simulation - Base Classes
===============================================

Core data structures and utilities for graph evolution simulations.
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Callable
from enum import Enum
import json
import time
from pathlib import Path


class PruningStrategy(Enum):
    """Pruning strategy options matching TypeScript implementation."""
    THRESHOLD = "threshold"
    AGE = "age"
    RANDOM = "random"
    MAGNITUDE = "magnitude"
    ACTIVITY = "activity"
    COMBINED = "combined"


class GraftingStrategy(Enum):
    """Grafting strategy options matching TypeScript implementation."""
    RANDOM = "random"
    SIMILARITY = "similarity"
    COMPLEMENTARY = "complementary"
    GRADIENT = "gradient"
    HEURISTIC = "heuristic"


@dataclass
class EvolutionConfig:
    """Configuration for graph evolution matching TypeScript implementation."""
    # Pruning parameters
    pruning_threshold: float = 0.05
    pruning_interval: int = 60  # timesteps (1 min in real time)
    pruning_strategy: PruningStrategy = PruningStrategy.COMBINED
    min_synapse_age: int = 30  # timesteps
    max_pruning_rate: float = 0.1

    # Grafting parameters
    grafting_probability: float = 0.01
    grafting_strategy: GraftingStrategy = GraftingStrategy.HEURISTIC
    max_new_connections: int = 5
    connection_bias: float = 0.3

    # Clustering parameters
    cluster_resolution: float = 1.0
    min_cluster_size: int = 2
    cluster_update_interval: int = 300  # timesteps

    # Plasticity parameters
    plasticity_rate: float = 0.001
    stability_threshold: float = 0.8
    homeostatic_target: float = 0.5


@dataclass
class EvolutionMetrics:
    """Metrics collected during evolution."""
    generation: int
    total_nodes: int
    total_edges: int
    avg_degree: float
    sparsity: float  # 1 - (actual_edges / possible_edges)
    clustering_coefficient: float
    modularity: float
    avg_path_length: float
    diameter: int
    pruned_this_cycle: int
    grafted_this_cycle: int

    # Network science metrics
    small_world_sigma: float = 0.0  # C/C_rand / L/L_rand
    degree_assortativity: float = 0.0
    spectral_gap: float = 0.0

    # Performance metrics
    performance_score: float = 0.0
    efficiency_score: float = 0.0
    robustness_score: float = 0.0

    # Power law metrics
    power_law_alpha: float = 0.0
    power_law_ks_distance: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "generation": self.generation,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "avg_degree": self.avg_degree,
            "sparsity": self.sparsity,
            "clustering_coefficient": self.clustering_coefficient,
            "modularity": self.modularity,
            "avg_path_length": self.avg_path_length,
            "diameter": self.diameter,
            "pruned_this_cycle": self.pruned_this_cycle,
            "grafted_this_cycle": self.grafted_this_cycle,
            "small_world_sigma": self.small_world_sigma,
            "degree_assortativity": self.degree_assortativity,
            "spectral_gap": self.spectral_gap,
            "performance_score": self.performance_score,
            "efficiency_score": self.efficiency_score,
            "robustness_score": self.robustness_score,
            "power_law_alpha": self.power_law_alpha,
            "power_law_ks_distance": self.power_law_ks_distance,
        }


class AgentNode:
    """Represents an agent node in the graph."""

    def __init__(self, node_id: str, capabilities: Optional[Dict[str, float]] = None):
        self.id = node_id
        self.capabilities = capabilities or {}
        self.activation_history: List[float] = []
        self.cluster: Optional[int] = None
        self.centrality: float = 0.0
        self.value_function: float = 0.0

    def add_activation(self, level: float):
        """Record an activation event."""
        self.activation_history.append(level)
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)

    def get_avg_activation(self) -> float:
        """Get average activation level."""
        if not self.activation_history:
            return 0.0
        return sum(self.activation_history) / len(self.activation_history)


class AgentEdge:
    """Represents an edge (synapse) between agents."""

    def __init__(self, source: str, target: str, weight: float = 0.5):
        self.source = source
        self.target = target
        self.weight = weight
        self.age: int = 0  # timesteps since last activation
        self.activity_level: int = 0
        self.last_active: int = 0
        self.coactivation_count: int = 0

    def activate(self):
        """Record activation of this synapse."""
        self.activity_level += 1
        self.coactivation_count += 1
        self.last_active = 0
        self.age = 0

    def age_step(self):
        """Age the synapse by one timestep."""
        self.age += 1
        self.last_active += 1


class AgentGraph:
    """
    Main graph structure for agent networks.

    Implements the graph evolution logic from TypeScript evolution.ts
    """

    def __init__(self, num_agents: int, config: Optional[EvolutionConfig] = None):
        self.num_agents = num_agents
        self.config = config or EvolutionConfig()

        # NetworkX graph for efficient operations
        self.graph = nx.DiGraph()

        # Agent nodes
        self.nodes: Dict[str, AgentNode] = {}

        # Edge tracking
        self.edges: Dict[Tuple[str, str], AgentEdge] = {}

        # Clusters
        self.clusters: Dict[int, Set[str]] = {}

        # Metrics history
        self.metrics_history: List[EvolutionMetrics] = []

        # Initialize graph
        self._initialize_graph()

    def _initialize_graph(self):
        """Initialize graph with random agents and connections."""
        # Create agents with random capabilities
        capability_names = [
            "reasoning", "creativity", "memory", "planning",
            "communication", "analysis", "synthesis", "evaluation"
        ]

        for i in range(self.num_agents):
            agent_id = f"agent_{i}"
            capabilities = {
                name: np.random.random() for name in capability_names
            }
            self.nodes[agent_id] = AgentNode(agent_id, capabilities)
            self.graph.add_node(agent_id)

        # Create initial random connections (Erdos-Renyi style)
        initial_density = 0.1  # Start sparse
        num_edges = int(self.num_agents * (self.num_agents - 1) * initial_density)

        for _ in range(num_edges):
            source = f"agent_{np.random.randint(0, self.num_agents)}"
            target = f"agent_{np.random.randint(0, self.num_agents)}"
            if source != target and not self.graph.has_edge(source, target):
                weight = np.random.uniform(0.1, 0.9)
                self._add_edge(source, target, weight)

    def _add_edge(self, source: str, target: str, weight: float):
        """Add an edge to the graph."""
        edge = AgentEdge(source, target, weight)
        self.edges[(source, target)] = edge
        self.graph.add_edge(source, target, weight=weight)

    def _remove_edge(self, source: str, target: str):
        """Remove an edge from the graph."""
        if (source, target) in self.edges:
            del self.edges[(source, target)]
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)

    def get_edge(self, source: str, target: str) -> Optional[AgentEdge]:
        """Get an edge if it exists."""
        return self.edges.get((source, target))

    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        return (source, target) in self.edges

    def activate_edge(self, source: str, target: str):
        """Activate an edge (Hebbian learning)."""
        edge = self.get_edge(source, target)
        if edge:
            edge.activate()

    def age_all_edges(self):
        """Age all edges by one timestep."""
        for edge in self.edges.values():
            edge.age_step()

    def compute_metrics(self, generation: int) -> EvolutionMetrics:
        """Compute comprehensive graph metrics."""
        G = self.graph

        # Basic metrics
        total_nodes = G.number_of_nodes()
        total_edges = G.number_of_edges()
        avg_degree = sum(dict(G.degree()).values()) / max(1, total_nodes)

        # Sparsity
        possible_edges = total_nodes * (total_nodes - 1)
        sparsity = 1 - (total_edges / max(1, possible_edges))

        # Clustering coefficient (for undirected version)
        G_undirected = G.to_undirected()
        clustering_coefficient = nx.average_clustering(G_undirected)

        # Modularity
        modularity = 0.0
        if self.clusters:
            # Create partition dict
            partition = {}
            for cluster_id, members in self.clusters.items():
                for node in members:
                    partition[node] = cluster_id
            modularity = nx.community.modularity(G_undirected, list(self.clusters.values()))

        # Path length metrics
        if nx.is_connected(G_undirected):
            avg_path_length = nx.average_shortest_path_length(G_undirected)
            diameter = nx.diameter(G_undirected)
        else:
            # For disconnected graphs, use largest component
            largest_cc = max(nx.connected_components(G_undirected), key=len)
            subgraph = G_undirected.subgraph(largest_cc)
            avg_path_length = nx.average_shortest_path_length(subgraph)
            diameter = nx.diameter(subgraph)

        # Small-world properties
        # Generate random graph with same degree sequence
        try:
            G_random = nx.configuration_model([d for n, d in G.degree()])
            G_random = nx.Graph(G_random)  # Remove multi-edges
            G_random.remove_edges_from(nx.selfloop_edges(G_random))

            if G_random.number_of_edges() > 0:
                C_random = nx.average_clustering(G_random)
                L_random = nx.average_shortest_path_length(G_random) if nx.is_connected(G_random) else avg_path_length
                small_world_sigma = (clustering_coefficient / max(C_random, 0.001)) / (avg_path_length / max(L_random, 0.001))
            else:
                small_world_sigma = 0.0
        except:
            small_world_sigma = 0.0

        # Degree assortativity
        degree_assortativity = nx.degree_assortativity_coefficient(G_undirected)

        # Spectral gap (second eigenvalue of Laplacian)
        try:
            L = nx.laplacian_matrix(G_undirected).toarray()
            eigenvalues = np.linalg.eigvals(L)
            eigenvalues = np.real(eigenvalues)
            eigenvalues = np.sort(eigenvalues)
            spectral_gap = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
        except:
            spectral_gap = 0.0

        # Power law fitting
        try:
            degrees = [d for n, d in G.degree()]
            if len(degrees) > 0 and min(degrees) > 0:
                from powerlaw import Fit
                fit = Fit(degrees, discrete=True)
                power_law_alpha = fit.power_law.alpha
                power_law_ks_distance = fit.power_law.KS()
            else:
                power_law_alpha = 0.0
                power_law_ks_distance = 0.0
        except:
            power_law_alpha = 0.0
            power_law_ks_distance = 0.0

        return EvolutionMetrics(
            generation=generation,
            total_nodes=total_nodes,
            total_edges=total_edges,
            avg_degree=avg_degree,
            sparsity=sparsity,
            clustering_coefficient=clustering_coefficient,
            modularity=modularity,
            avg_path_length=avg_path_length,
            diameter=diameter,
            pruned_this_cycle=0,
            grafted_this_cycle=0,
            small_world_sigma=small_world_sigma,
            degree_assortativity=degree_assortativity,
            spectral_gap=spectral_gap,
            power_law_alpha=power_law_alpha,
            power_law_ks_distance=power_law_ks_distance,
        )

    def compute_capability_similarity(self, agent1: str, agent2: str) -> float:
        """Compute cosine similarity between agent capabilities."""
        node1 = self.nodes.get(agent1)
        node2 = self.nodes.get(agent2)

        if not node1 or not node2:
            return 0.0

        # Get all capability keys
        all_keys = set(node1.capabilities.keys()) | set(node2.capabilities.keys())

        if not all_keys:
            return 0.0

        # Compute cosine similarity
        dot_product = sum(
            node1.capabilities.get(k, 0) * node2.capabilities.get(k, 0)
            for k in all_keys
        )
        norm1 = np.sqrt(sum(node1.capabilities.get(k, 0) ** 2 for k in all_keys))
        norm2 = np.sqrt(sum(node2.capabilities.get(k, 0) ** 2 for k in all_keys))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def compute_complementarity(self, agent1: str, agent2: str) -> float:
        """Compute how well capabilities complement each other."""
        node1 = self.nodes.get(agent1)
        node2 = self.nodes.get(agent2)

        if not node1 or not node2:
            return 0.0

        all_keys = set(node1.capabilities.keys()) | set(node2.capabilities.keys())

        if not all_keys:
            return 0.0

        # XOR-like complementarity
        complement = sum(
            abs(node1.capabilities.get(k, 0) - node2.capabilities.get(k, 0)) *
            min(node1.capabilities.get(k, 0), node2.capabilities.get(k, 0))
            for k in all_keys
        )

        return complement / len(all_keys)

    def save_metrics(self, filepath: Path):
        """Save metrics history to JSON file."""
        data = {
            "config": {
                "num_agents": self.num_agents,
                "pruning_strategy": self.config.pruning_strategy.value,
                "grafting_strategy": self.config.grafting_strategy.value,
                "pruning_threshold": self.config.pruning_threshold,
                "max_pruning_rate": self.config.max_pruning_rate,
                "grafting_probability": self.config.grafting_probability,
            },
            "metrics": [m.to_dict() for m in self.metrics_history]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_metrics(self, filepath: Path):
        """Load metrics history from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.metrics_history = [
            EvolutionMetrics(**m) for m in data["metrics"]
        ]

        return data.get("config", {})
