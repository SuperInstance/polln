"""
Topology Generator for POLLN Agent Colonies

Generates diverse network topologies for agent communication systems.
Implements various graph models from network science and graph theory.
"""

import networkx as nx
import numpy as np
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random


class TopologyType(Enum):
    """Supported topology types."""
    ERDOS_RENYI = "erdos_renyi"
    WATTS_STROGATZ = "watts_strogatz"
    BARABASI_ALBERT = "barabasi_albert"
    REGULAR_LATTICE = "regular_lattice"
    RANDOM_GEOMETRIC = "random_geometric"
    HYBRID_SMALL_WORLD_SF = "hybrid_small_world_sf"
    HIERARCHICAL = "hierarchical"
    MODULAR = "modular"
    TWO_TIER = "two_tier"
    THREE_TIER = "three_tier"


@dataclass
class TopologyParams:
    """Parameters for topology generation."""
    n: int  # Number of nodes (agents)
    k: Optional[int] = None  # Mean degree
    p: Optional[float] = None  # Rewiring probability or edge probability
    m: Optional[int] = None  # Edges to add per step (BA)
    radius: Optional[float] = None  # Connection radius (geometric)
    levels: Optional[int] = None  # Hierarchy levels
    modules: Optional[int] = None  # Number of modules
    module_size: Optional[int] = None  # Size of each module
    seed: Optional[int] = None


class TopologyGenerator:
    """Generate diverse network topologies for agent colonies."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional random seed."""
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    def generate(self, topology_type: TopologyType, params: TopologyParams) -> nx.Graph:
        """Generate a topology of the specified type."""
        generators = {
            TopologyType.ERDOS_RENYI: self._erdos_renyi,
            TopologyType.WATTS_STROGATZ: self._watts_strogatz,
            TopologyType.BARABASI_ALBERT: self._barabasi_albert,
            TopologyType.REGULAR_LATTICE: self._regular_lattice,
            TopologyType.RANDOM_GEOMETRIC: self._random_geometric,
            TopologyType.HYBRID_SMALL_WORLD_SF: self._hybrid_small_world_sf,
            TopologyType.HIERARCHICAL: self._hierarchical,
            TopologyType.MODULAR: self._modular,
            TopologyType.TWO_TIER: self._two_tier,
            TopologyType.THREE_TIER: self._three_tier,
        }

        if topology_type not in generators:
            raise ValueError(f"Unknown topology type: {topology_type}")

        return generators[topology_type](params)

    def _erdos_renyi(self, params: TopologyParams) -> nx.Graph:
        """Generate Erdős-Rényi random graph."""
        n = params.n
        p = params.p if params.p is not None else 2 * np.log(n) / n
        return nx.erdos_renyi_graph(n, p, seed=params.seed)

    def _watts_strogatz(self, params: TopologyParams) -> nx.Graph:
        """Generate Watts-Strogatz small-world graph."""
        n = params.n
        k = params.k if params.k is not None else max(4, int(np.log2(n)))
        p = params.p if params.p is not None else 0.1
        return nx.watts_strogatz_graph(n, k, p, seed=params.seed)

    def _barabasi_albert(self, params: TopologyParams) -> nx.Graph:
        """Generate Barabási-Albert scale-free graph."""
        n = params.n
        m = params.m if params.m is not None else max(2, int(np.log2(n)))
        return nx.barabasi_albert_graph(n, m, seed=params.seed)

    def _regular_lattice(self, params: TopologyParams) -> nx.Graph:
        """Generate regular lattice graph."""
        n = params.n
        k = params.k if params.k is not None else 4
        # Create a 2D grid if possible
        side = int(np.sqrt(n))
        if side * side == n:
            return nx.grid_2d_graph(side, side)
        else:
            # Fallback to regular ring lattice
            return nx.watts_strogatz_graph(n, k, 0, seed=params.seed)

    def _random_geometric(self, params: TopologyParams) -> nx.Graph:
        """Generate random geometric graph."""
        n = params.n
        # Calculate radius for average degree ~k
        k = params.k if params.k is not None else 6
        radius = np.sqrt(k / (n * np.pi)) if params.radius is None else params.radius
        return nx.random_geometric_graph(n, radius, seed=params.seed)

    def _hybrid_small_world_sf(self, params: TopologyParams) -> nx.Graph:
        """Generate hybrid small-world + scale-free topology."""
        n = params.n
        k = params.k if params.k is not None else max(4, int(np.log2(n)))
        p = params.p if params.p is not None else 0.1

        # Start with Watts-Strogatz small-world
        G = nx.watts_strogatz_graph(n, k, p, seed=params.seed)

        # Add scale-free characteristics
        # Add preferential attachment edges
        degrees = dict(G.degree())
        total_degree = sum(degrees.values())

        # Add extra edges to high-degree nodes
        num_extra_edges = int(n * 0.1)  # Add 10% more edges
        for _ in range(num_extra_edges):
            # Select node with probability proportional to degree
            nodes = list(G.nodes())
            probs = [degrees[node] / total_degree for node in nodes]
            node1 = np.random.choice(nodes, p=probs)

            # Find non-neighbor
            non_neighbors = [n for n in nodes if n != node1 and not G.has_edge(node1, n)]
            if non_neighbors:
                node2 = np.random.choice(non_neighbors)
                G.add_edge(node1, node2)
                degrees[node1] += 1
                degrees[node2] += 1
                total_degree += 2

        return G

    def _hierarchical(self, params: TopologyParams) -> nx.Graph:
        """Generate hierarchical topology."""
        n = params.n
        levels = params.levels if params.levels is not None else 3

        G = nx.Graph()

        # Calculate nodes per level
        nodes_per_level = []
        remaining = n
        for i in range(levels):
            if i == levels - 1:
                nodes_per_level.append(remaining)
            else:
                # Level i has 1/4 of remaining nodes
                count = max(1, int(remaining / 4))
                nodes_per_level.append(count)
                remaining -= count

        # Create hierarchical connections
        level_start = 0
        upper_nodes = []

        for level_idx, count in enumerate(nodes_per_level):
            level_nodes = list(range(level_start, level_start + count))
            G.add_nodes_from(level_nodes)

            if level_idx == 0:
                # Top level: fully connected
                for i in level_nodes:
                    for j in level_nodes:
                        if i < j:
                            G.add_edge(i, j)
                upper_nodes = level_nodes
            else:
                # Connect to upper level
                for node in level_nodes:
                    # Connect to random subset of upper level
                    num_connections = min(len(upper_nodes), 3)
                    targets = random.sample(upper_nodes, num_connections)
                    for target in targets:
                        G.add_edge(node, target)

                # Within level connections (partial)
                for i in level_nodes:
                    for j in level_nodes:
                        if i < j and random.random() < 0.3:
                            G.add_edge(i, j)

                upper_nodes.extend(level_nodes[:max(1, len(level_nodes) // 4)])

            level_start += count

        return G

    def _modular(self, params: TopologyParams) -> nx.Graph:
        """Generate modular topology with inter-module connections."""
        n = params.n
        num_modules = params.modules if params.modules is not None else max(3, int(np.sqrt(n)))
        module_size = params.module_size if params.module_size is not None else n // num_modules

        G = nx.Graph()
        modules = []

        # Create modules
        for i in range(num_modules):
            start_idx = i * module_size
            end_idx = min(start_idx + module_size, n)
            module_nodes = list(range(start_idx, end_idx))

            # Create small-world within module
            if len(module_nodes) > 2:
                k = min(len(module_nodes) - 1, 4)
                module_graph = nx.watts_strogatz_graph(len(module_nodes), k, 0.1, seed=params.seed)

                # Relabel nodes and add to main graph
                mapping = {j: module_nodes[j] for j in range(len(module_nodes))}
                module_graph = nx.relabel_nodes(module_graph, mapping)
                G.add_nodes_from(module_graph.nodes())
                G.add_edges_from(module_graph.edges())

            modules.append(module_nodes)

        # Add inter-module connections
        for i in range(num_modules):
            for j in range(i + 1, num_modules):
                # Add a few bridge connections
                num_bridges = min(2, len(modules[i]), len(modules[j]))
                for _ in range(num_bridges):
                    node1 = random.choice(modules[i])
                    node2 = random.choice(modules[j])
                    G.add_edge(node1, node2)

        return G

    def _two_tier(self, params: TopologyParams) -> nx.Graph:
        """Generate two-tier topology (core + edge)."""
        n = params.n
        k = params.k if params.k is not None else 4

        # Core tier: 20% of nodes
        core_size = max(3, int(n * 0.2))
        edge_size = n - core_size

        G = nx.Graph()

        # Core nodes: fully connected
        core_nodes = list(range(core_size))
        for i in core_nodes:
            for j in core_nodes:
                if i < j:
                    G.add_edge(i, j)

        # Edge nodes: connect to subset of core
        edge_nodes = list(range(core_size, n))
        for node in edge_nodes:
            # Connect to k core nodes
            connections = random.sample(core_nodes, min(k, core_size))
            for target in connections:
                G.add_edge(node, target)

        # Some edge-to-edge connections
        for i in edge_nodes:
            for j in edge_nodes:
                if i < j and random.random() < 0.1:
                    G.add_edge(i, j)

        return G

    def _three_tier(self, params: TopologyParams) -> nx.Graph:
        """Generate three-tier topology (core + aggregation + edge)."""
        n = params.n

        # Tier sizes
        core_size = max(3, int(n * 0.1))
        agg_size = max(5, int(n * 0.3))
        edge_size = n - core_size - agg_size

        G = nx.Graph()

        # Core tier: fully connected
        core_nodes = list(range(core_size))
        for i in core_nodes:
            for j in core_nodes:
                if i < j:
                    G.add_edge(i, j)

        # Aggregation tier
        agg_nodes = list(range(core_size, core_size + agg_size))
        for node in agg_nodes:
            # Connect to 2-3 core nodes
            connections = random.sample(core_nodes, min(3, core_size))
            for target in connections:
                G.add_edge(node, target)

        # Within aggregation tier
        for i in agg_nodes:
            for j in agg_nodes:
                if i < j and random.random() < 0.3:
                    G.add_edge(i, j)

        # Edge tier
        edge_nodes = list(range(core_size + agg_size, n))
        for node in edge_nodes:
            # Connect to 1-2 aggregation nodes
            connections = random.sample(agg_nodes, min(2, agg_size))
            for target in connections:
                G.add_edge(node, target)

        return G

    def parameter_sweep(self, topology_type: TopologyType, n: int,
                       param_ranges: Dict[str, List[Any]]) -> List[Tuple[TopologyParams, nx.Graph]]:
        """Generate multiple topologies with parameter sweeps."""
        results = []

        # Generate parameter combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())

        for combination in self._cartesian_product(param_values):
            param_dict = dict(zip(param_names, combination))
            params = TopologyParams(n=n, **param_dict)

            try:
                G = self.generate(topology_type, params)
                results.append((params, G))
            except Exception as e:
                print(f"Failed to generate topology with params {param_dict}: {e}")

        return results

    def _cartesian_product(self, lists):
        """Generate Cartesian product of lists."""
        if not lists:
            yield ()
        else:
            for item in lists[0]:
                for rest in self._cartesian_product(lists[1:]):
                    yield (item,) + rest

    def export_graphml(self, G: nx.Graph, filepath: str) -> None:
        """Export graph to GraphML format."""
        nx.write_graphml(G, filepath)

    def export_json(self, G: nx.Graph, filepath: str,
                    topology_type: TopologyType,
                    params: TopologyParams) -> None:
        """Export graph to JSON format."""
        data = {
            'topology_type': topology_type.value,
            'params': asdict(params),
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'adjacency': nx.to_dict_of_lists(G)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_json(self, filepath: str) -> Tuple[nx.Graph, TopologyType, TopologyParams]:
        """Load graph from JSON format."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        G = nx.from_dict_of_lists(data['adjacency'])
        topology_type = TopologyType(data['topology_type'])
        params = TopologyParams(**{k: v for k, v in data['params'].items() if k != 'seed'})

        return G, topology_type, params


def generate_benchmark_topologies(n: int, seed: int = 42) -> Dict[str, Tuple[nx.Graph, TopologyType, TopologyParams]]:
    """Generate benchmark topologies for a given colony size."""
    generator = TopologyGenerator(seed=seed)
    topologies = {}

    # Erdős-Rényi
    params = TopologyParams(n=n, p=2*np.log(n)/n, seed=seed)
    G = generator.generate(TopologyType.ERDOS_RENYI, params)
    topologies['erdos_renyi'] = (G, TopologyType.ERDOS_RENYI, params)

    # Watts-Strogatz
    k = max(4, int(np.log2(n)))
    params = TopologyParams(n=n, k=k, p=0.1, seed=seed)
    G = generator.generate(TopologyType.WATTS_STROGATZ, params)
    topologies['watts_strogatz'] = (G, TopologyType.WATTS_STROGATZ, params)

    # Barabási-Albert
    m = max(2, int(np.log2(n)))
    params = TopologyParams(n=n, m=m, seed=seed)
    G = generator.generate(TopologyType.BARABASI_ALBERT, params)
    topologies['barabasi_albert'] = (G, TopologyType.BARABASI_ALBERT, params)

    # Two-tier
    params = TopologyParams(n=n, k=4, seed=seed)
    G = generator.generate(TopologyType.TWO_TIER, params)
    topologies['two_tier'] = (G, TopologyType.TWO_TIER, params)

    # Modular
    num_modules = max(3, int(np.sqrt(n)))
    params = TopologyParams(n=n, modules=num_modules, seed=seed)
    G = generator.generate(TopologyType.MODULAR, params)
    topologies['modular'] = (G, TopologyType.MODULAR, params)

    return topologies


if __name__ == "__main__":
    # Example usage
    generator = TopologyGenerator(seed=42)

    # Generate topologies for different colony sizes
    for n in [10, 50, 100, 500, 1000]:
        print(f"\nGenerating topologies for colony size {n}")

        topologies = generate_benchmark_topologies(n, seed=42)

        for name, (G, topo_type, params) in topologies.items():
            print(f"  {name}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

            # Export
            output_dir = f"output/topologies/{n}"
            import os
            os.makedirs(output_dir, exist_ok=True)

            generator.export_graphml(G, f"{output_dir}/{name}.graphml")
            generator.export_json(G, f"{output_dir}/{name}.json", topo_type, params)
