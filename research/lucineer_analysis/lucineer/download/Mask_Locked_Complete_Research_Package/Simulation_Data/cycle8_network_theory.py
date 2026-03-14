"""
Cycle 8: Network-Theoretic Inference Architecture Analysis
===========================================================

Comprehensive analysis of PE interconnection network topology for
mask-locked inference chips, including:

1. Graph-theoretic chip topology (32×32 PE array = 1024 nodes)
2. Small-world and scale-free network properties
3. Network diameter and average path length
4. Clustering coefficient optimization
5. Percolation theory for reliability
6. Max-flow min-cut for bandwidth analysis
7. Systolic dataflow patterns

Author: Network Theory Research Cycle
Date: March 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings
import json
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class PEArrayConfig:
    """Configuration for Processing Element array."""
    rows: int = 32
    cols: int = 32
    neighbor_connectivity: str = "mesh"  # mesh, torus, hexagonal, small_world
    local_bandwidth: float = 64.0  # GB/s per link
    diagonal_bandwidth: float = 32.0  # GB/s for diagonal links
    long_range_prob: float = 0.05  # Probability of long-range connections
    
    @property
    def n_pes(self) -> int:
        return self.rows * self.cols
    
    @property
    def aspect_ratio(self) -> float:
        return self.rows / self.cols


@dataclass
class DefectConfig:
    """Configuration for manufacturing defects."""
    pe_defect_rate: float = 1e-8  # Defect probability per PE
    link_defect_rate: float = 1e-7  # Defect probability per link
    cluster_defect_prob: float = 0.1  # Probability of clustered defects
    
    # For percolation analysis
    critical_threshold: float = 0.5927  # 2D square lattice percolation threshold


# ============================================================================
# Graph Construction
# ============================================================================

class PEInterconnectionGraph:
    """
    Graph representation of PE interconnection network.
    
    Nodes: Processing Elements (PEs) indexed by (row, col)
    Edges: Interconnect links with bandwidth weights
    """
    
    def __init__(self, config: PEArrayConfig):
        self.config = config
        self.n_nodes = config.n_pes
        self.adjacency: Dict[int, Dict[int, float]] = defaultdict(dict)
        self.node_coords: Dict[int, Tuple[int, int]] = {}
        self.coord_to_node: Dict[Tuple[int, int], int] = {}
        
        self._build_graph()
    
    def _build_graph(self):
        """Build the interconnection graph based on topology."""
        # Create node mappings
        for r in range(self.config.rows):
            for c in range(self.config.cols):
                node_id = r * self.config.cols + c
                self.node_coords[node_id] = (r, c)
                self.coord_to_node[(r, c)] = node_id
        
        # Add edges based on topology
        if self.config.neighbor_connectivity == "mesh":
            self._build_mesh()
        elif self.config.neighbor_connectivity == "torus":
            self._build_torus()
        elif self.config.neighbor_connectivity == "hexagonal":
            self._build_hexagonal()
        elif self.config.neighbor_connectivity == "small_world":
            self._build_small_world()
    
    def _build_mesh(self):
        """Build 2D mesh topology with optional diagonal links."""
        for r in range(self.config.rows):
            for c in range(self.config.cols):
                node = self.coord_to_node[(r, c)]
                
                # Cardinal neighbors (N, S, E, W)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.config.rows and 0 <= nc < self.config.cols:
                        neighbor = self.coord_to_node[(nr, nc)]
                        self._add_edge(node, neighbor, self.config.local_bandwidth)
    
    def _build_torus(self):
        """Build torus topology (wrap-around mesh)."""
        for r in range(self.config.rows):
            for c in range(self.config.cols):
                node = self.coord_to_node[(r, c)]
                
                # Wrap-around neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr = (r + dr) % self.config.rows
                    nc = (c + dc) % self.config.cols
                    neighbor = self.coord_to_node[(nr, nc)]
                    self._add_edge(node, neighbor, self.config.local_bandwidth)
    
    def _build_hexagonal(self):
        """Build hexagonal mesh topology (6 neighbors per PE)."""
        for r in range(self.config.rows):
            for c in range(self.config.cols):
                node = self.coord_to_node[(r, c)]
                
                # Hexagonal neighbors (offset based on row parity)
                if r % 2 == 0:
                    offsets = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
                else:
                    offsets = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
                
                for dr, dc in offsets:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.config.rows and 0 <= nc < self.config.cols:
                        neighbor = self.coord_to_node[(nr, nc)]
                        self._add_edge(node, neighbor, self.config.local_bandwidth)
    
    def _build_small_world(self):
        """
        Build small-world network using Watts-Strogatz model.
        
        Starts with mesh topology and rewires edges with probability p.
        """
        # Start with mesh
        self._build_mesh()
        
        # Rewire edges
        edges_to_rewire = []
        for node in self.adjacency:
            for neighbor in list(self.adjacency[node].keys()):
                if np.random.random() < self.config.long_range_prob:
                    edges_to_rewire.append((node, neighbor))
        
        # Perform rewiring
        for node, old_neighbor in edges_to_rewire:
            # Remove old edge
            if old_neighbor in self.adjacency[node]:
                del self.adjacency[node][old_neighbor]
            if node in self.adjacency[old_neighbor]:
                del self.adjacency[old_neighbor][node]
            
            # Add new random edge
            new_neighbor = np.random.randint(0, self.n_nodes)
            while new_neighbor == node or new_neighbor in self.adjacency[node]:
                new_neighbor = np.random.randint(0, self.n_nodes)
            
            self._add_edge(node, new_neighbor, self.config.local_bandwidth)
    
    def _add_edge(self, u: int, v: int, weight: float):
        """Add undirected edge with weight."""
        self.adjacency[u][v] = weight
        self.adjacency[v][u] = weight
    
    def get_neighbors(self, node: int) -> List[int]:
        """Get neighbors of a node."""
        return list(self.adjacency[node].keys())
    
    def get_edge_weight(self, u: int, v: int) -> float:
        """Get edge weight (bandwidth)."""
        return self.adjacency[u].get(v, 0.0)
    
    def get_degree(self, node: int) -> int:
        """Get degree of a node."""
        return len(self.adjacency[node])
    
    def get_all_degrees(self) -> List[int]:
        """Get degrees of all nodes."""
        return [self.get_degree(n) for n in range(self.n_nodes)]


# ============================================================================
# Network Metrics
# ============================================================================

class NetworkMetrics:
    """
    Compute graph-theoretic metrics for PE network.
    """
    
    def __init__(self, graph: PEInterconnectionGraph):
        self.graph = graph
        self._path_cache: Dict[Tuple[int, int], List[int]] = {}
        self._distance_cache: Dict[Tuple[int, int], float] = {}
    
    def compute_all_metrics(self) -> Dict:
        """Compute all network metrics."""
        return {
            "basic_metrics": self.basic_metrics(),
            "degree_statistics": self.degree_statistics(),
            "path_metrics": self.path_metrics(),
            "clustering_coefficient": self.clustering_coefficient(),
            "small_world_coefficient": self.small_world_coefficient(),
            "scale_free_analysis": self.scale_free_analysis(),
            "connectivity_analysis": self.connectivity_analysis()
        }
    
    def basic_metrics(self) -> Dict:
        """Compute basic graph metrics."""
        n = self.graph.n_nodes
        m = sum(len(neighbors) for neighbors in self.graph.adjacency.values()) // 2
        
        return {
            "n_nodes": n,
            "n_edges": m,
            "density": 2 * m / (n * (n - 1)) if n > 1 else 0,
            "avg_degree": 2 * m / n if n > 0 else 0
        }
    
    def degree_statistics(self) -> Dict:
        """Compute degree distribution statistics."""
        degrees = self.graph.get_all_degrees()
        
        return {
            "min_degree": int(min(degrees)),
            "max_degree": int(max(degrees)),
            "mean_degree": np.mean(degrees),
            "std_degree": np.std(degrees),
            "degree_distribution": dict(Counter(degrees))
        }
    
    def shortest_path(self, source: int, target: int) -> Tuple[List[int], float]:
        """
        Compute shortest path using Dijkstra's algorithm.
        
        Returns (path, distance).
        """
        if (source, target) in self._path_cache:
            return self._path_cache[(source, target)], self._distance_cache[(source, target)]
        
        if source == target:
            self._path_cache[(source, target)] = [source]
            self._distance_cache[(source, target)] = 0.0
            return [source], 0.0
        
        # Dijkstra
        dist = {source: 0.0}
        prev = {source: None}
        unvisited = set(range(self.graph.n_nodes))
        
        while unvisited:
            # Find minimum distance node
            current = min(unvisited, key=lambda x: dist.get(x, float('inf')))
            
            if dist.get(current, float('inf')) == float('inf'):
                break  # No path exists
            
            if current == target:
                break
            
            unvisited.remove(current)
            
            # Update neighbors
            for neighbor, weight in self.graph.adjacency[current].items():
                if neighbor in unvisited:
                    new_dist = dist[current] + 1.0  # Hop count for path length
                    if new_dist < dist.get(neighbor, float('inf')):
                        dist[neighbor] = new_dist
                        prev[neighbor] = current
        
        # Reconstruct path
        if target not in prev:
            self._path_cache[(source, target)] = []
            self._distance_cache[(source, target)] = float('inf')
            return [], float('inf')
        
        path = []
        node = target
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()
        
        self._path_cache[(source, target)] = path
        self._distance_cache[(source, target)] = dist[target]
        
        return path, dist[target]
    
    def path_metrics(self, sample_size: int = 1000) -> Dict:
        """
        Compute network diameter and average path length.
        
        Uses sampling for large networks.
        """
        if self.graph.n_nodes <= 100:
            # Compute all pairs
            pairs = [(i, j) for i in range(self.graph.n_nodes) 
                     for j in range(i + 1, self.graph.n_nodes)]
        else:
            # Sample pairs
            pairs = []
            for _ in range(sample_size):
                i = np.random.randint(0, self.graph.n_nodes)
                j = np.random.randint(0, self.graph.n_nodes)
                if i != j:
                    pairs.append((i, j))
        
        distances = []
        for source, target in pairs:
            _, dist = self.shortest_path(source, target)
            if dist < float('inf'):
                distances.append(dist)
        
        if not distances:
            return {
                "diameter": float('inf'),
                "avg_path_length": float('inf'),
                "characteristic_path_length": float('inf')
            }
        
        # Diameter is maximum shortest path
        diameter = max(distances)
        avg_path = np.mean(distances)
        
        return {
            "diameter": diameter,
            "avg_path_length": avg_path,
            "characteristic_path_length": avg_path,
            "path_length_std": np.std(distances),
            "n_pairs_sampled": len(distances)
        }
    
    def clustering_coefficient(self) -> Dict:
        """
        Compute clustering coefficient for each node and global average.
        
        C_i = 2 * e_i / (k_i * (k_i - 1))
        
        Where e_i is number of edges between neighbors of node i.
        """
        node_clustering = {}
        
        for node in range(self.graph.n_nodes):
            neighbors = self.graph.get_neighbors(node)
            k = len(neighbors)
            
            if k < 2:
                node_clustering[node] = 0.0
                continue
            
            # Count edges between neighbors
            e_i = 0
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    if n2 in self.graph.adjacency[n1]:
                        e_i += 1
            
            # Clustering coefficient
            c_i = 2 * e_i / (k * (k - 1))
            node_clustering[node] = c_i
        
        # Global clustering coefficient
        global_c = np.mean(list(node_clustering.values()))
        
        # Node clustering by position (center vs edge)
        center_nodes = []
        edge_nodes = []
        corner_nodes = []
        
        for node, cc in node_clustering.items():
            r, c = self.graph.node_coords[node]
            on_edge = (r == 0 or r == self.graph.config.rows - 1 or 
                      c == 0 or c == self.graph.config.cols - 1)
            is_corner = ((r == 0 or r == self.graph.config.rows - 1) and 
                        (c == 0 or c == self.graph.config.cols - 1))
            
            if is_corner:
                corner_nodes.append(cc)
            elif on_edge:
                edge_nodes.append(cc)
            else:
                center_nodes.append(cc)
        
        return {
            "global_clustering": global_c,
            "avg_center_clustering": np.mean(center_nodes) if center_nodes else 0,
            "avg_edge_clustering": np.mean(edge_nodes) if edge_nodes else 0,
            "avg_corner_clustering": np.mean(corner_nodes) if corner_nodes else 0,
            "node_clustering": node_clustering
        }
    
    def small_world_coefficient(self) -> Dict:
        """
        Compute small-world coefficient (sigma).
        
        sigma = (C / C_rand) / (L / L_rand)
        
        Where C is clustering coefficient, L is average path length,
        and rand denotes random graph equivalents.
        """
        # Get actual metrics
        actual_c = self.clustering_coefficient()["global_clustering"]
        actual_l = self.path_metrics()["avg_path_length"]
        
        # Estimate random graph metrics
        n = self.graph.n_nodes
        m = sum(len(neighbors) for neighbors in self.graph.adjacency.values()) // 2
        p = 2 * m / (n * (n - 1))  # Edge probability
        
        # Random graph expected values
        if p < 1:
            # Erdos-Renyi G(n, p)
            c_rand = p  # Expected clustering coefficient
            l_rand = np.log(n) / np.log(max(2, n * p))  # Expected path length
        else:
            c_rand = 1.0
            l_rand = 1.0
        
        # Small-world coefficient
        if c_rand > 0 and l_rand > 0 and actual_l < float('inf'):
            sigma = (actual_c / c_rand) / (actual_l / l_rand)
        else:
            sigma = 0.0
        
        # Omega coefficient (alternative measure)
        # omega = (L_rand / L) - (C / C_lattice)
        c_lattice = 0.0  # For mesh, theoretical lattice clustering
        if self.graph.config.neighbor_connectivity == "mesh":
            # Estimate lattice clustering
            c_lattice = 0.0  # Pure lattice has C=0 for mesh
        
        if actual_l > 0:
            omega = (l_rand / actual_l) - (actual_c / max(c_lattice, 0.01))
        else:
            omega = 0.0
        
        return {
            "sigma": sigma,
            "omega": omega,
            "c_actual": actual_c,
            "c_random": c_rand,
            "l_actual": actual_l,
            "l_random": l_rand,
            "is_small_world": sigma > 1.0
        }
    
    def scale_free_analysis(self) -> Dict:
        """
        Analyze scale-free properties of the network.
        
        A scale-free network has degree distribution following power law:
        P(k) ~ k^(-gamma)
        """
        degrees = self.graph.get_all_degrees()
        degree_counts = Counter(degrees)
        
        # Fit power law
        k_values = np.array(sorted(degree_counts.keys()))
        p_k = np.array([degree_counts[k] for k in k_values])
        p_k = p_k / p_k.sum()  # Normalize
        
        # Log-log regression for gamma
        if len(k_values) > 2:
            # Filter out zeros for log
            mask = (k_values > 0) & (p_k > 0)
            if mask.sum() > 2:
                log_k = np.log(k_values[mask])
                log_p = np.log(p_k[mask])
                
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(log_k, log_p)
                gamma = -slope
                r_squared = r_value ** 2
            else:
                gamma = 0.0
                r_squared = 0.0
        else:
            gamma = 0.0
            r_squared = 0.0
        
        # Check for hub nodes (highly connected)
        mean_degree = np.mean(degrees)
        std_degree = np.std(degrees)
        hub_threshold = mean_degree + 2 * std_degree
        hubs = [i for i, d in enumerate(degrees) if d >= hub_threshold]
        
        return {
            "power_law_exponent": gamma,
            "r_squared": r_squared,
            "is_scale_free": 2.0 < gamma < 3.5,  # Typical range for scale-free
            "n_hubs": len(hubs),
            "hub_nodes": hubs[:10] if hubs else [],
            "hub_fraction": len(hubs) / len(degrees) if degrees else 0
        }
    
    def connectivity_analysis(self) -> Dict:
        """Analyze network connectivity."""
        # Check if graph is connected using BFS
        visited = set()
        queue = [0]
        
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(self.graph.get_neighbors(node))
        
        is_connected = len(visited) == self.graph.n_nodes
        n_components = 1 if is_connected else self._count_components()
        
        return {
            "is_connected": is_connected,
            "n_components": n_components,
            "largest_component_size": len(visited) if is_connected else self._largest_component_size()
        }
    
    def _count_components(self) -> int:
        """Count number of connected components."""
        visited = set()
        components = 0
        
        for start in range(self.graph.n_nodes):
            if start not in visited:
                components += 1
                queue = [start]
                while queue:
                    node = queue.pop(0)
                    if node not in visited:
                        visited.add(node)
                        queue.extend(self.graph.get_neighbors(node))
        
        return components
    
    def _largest_component_size(self) -> int:
        """Find size of largest connected component."""
        visited = set()
        max_size = 0
        
        for start in range(self.graph.n_nodes):
            if start not in visited:
                component_size = 0
                queue = [start]
                while queue:
                    node = queue.pop(0)
                    if node not in visited:
                        visited.add(node)
                        component_size += 1
                        queue.extend(self.graph.get_neighbors(node))
                max_size = max(max_size, component_size)
        
        return max_size


# ============================================================================
# Percolation Analysis
# ============================================================================

class PercolationAnalysis:
    """
    Percolation theory analysis for reliability.
    
    Models:
    - Site percolation (PE defects)
    - Bond percolation (link defects)
    - Critical threshold analysis
    """
    
    def __init__(self, graph: PEInterconnectionGraph, defect_config: DefectConfig):
        self.graph = graph
        self.config = defect_config
        self.rng = np.random.default_rng(42)
    
    def site_percolation(self, defect_prob: float, n_trials: int = 100) -> Dict:
        """
        Site percolation analysis - removing PEs.
        
        Returns probability of percolation (spanning cluster exists).
        """
        n_nodes = self.graph.n_nodes
        percolation_count = 0
        cluster_sizes = []
        
        for _ in range(n_trials):
            # Randomly remove nodes
            active_nodes = set(range(n_nodes))
            for node in range(n_nodes):
                if self.rng.random() < defect_prob:
                    active_nodes.discard(node)
            
            # Find largest cluster
            largest = self._find_largest_cluster(active_nodes)
            cluster_sizes.append(largest)
            
            # Check for percolation (spanning from top to bottom, left to right)
            if self._check_spanning(active_nodes):
                percolation_count += 1
        
        percolation_prob = percolation_count / n_trials
        
        return {
            "defect_probability": defect_prob,
            "percolation_probability": percolation_prob,
            "avg_cluster_size": np.mean(cluster_sizes),
            "max_cluster_fraction": np.max(cluster_sizes) / n_nodes,
            "n_trials": n_trials
        }
    
    def bond_percolation(self, defect_prob: float, n_trials: int = 100) -> Dict:
        """
        Bond percolation analysis - removing links.
        """
        percolation_count = 0
        cluster_sizes = []
        
        for _ in range(n_trials):
            # Create graph with random edge removal
            active_edges = set()
            for node in self.graph.adjacency:
                for neighbor in self.graph.adjacency[node]:
                    if node < neighbor:  # Avoid double counting
                        if self.rng.random() >= defect_prob:
                            active_edges.add((node, neighbor))
            
            # Find connected components
            largest = self._find_largest_cluster_bond(active_edges)
            cluster_sizes.append(largest)
            
            # Check spanning
            if self._check_spanning_bond(active_edges):
                percolation_count += 1
        
        return {
            "defect_probability": defect_prob,
            "percolation_probability": percolation_count / n_trials,
            "avg_cluster_size": np.mean(cluster_sizes),
            "max_cluster_fraction": np.max(cluster_sizes) / self.graph.n_nodes,
            "n_trials": n_trials
        }
    
    def critical_threshold_analysis(self, n_points: int = 20, n_trials: int = 50) -> Dict:
        """
        Find critical percolation threshold.
        """
        probs = np.linspace(0.0, 1.0, n_points)
        site_results = []
        bond_results = []
        
        for p in probs:
            site_results.append(self.site_percolation(p, n_trials))
            bond_results.append(self.bond_percolation(p, n_trials))
        
        # Find critical threshold (where percolation probability drops to 0.5)
        site_perc_probs = [r["percolation_probability"] for r in site_results]
        bond_perc_probs = [r["percolation_probability"] for r in bond_results]
        
        # Interpolate to find threshold
        site_threshold = self._interpolate_threshold(probs, site_perc_probs)
        bond_threshold = self._interpolate_threshold(probs, bond_perc_probs)
        
        return {
            "site_percolation_results": site_results,
            "bond_percolation_results": bond_results,
            "site_critical_threshold": site_threshold,
            "bond_critical_threshold": bond_threshold,
            "theoretical_site_threshold": self.config.critical_threshold,
            "threshold_margin": site_threshold - self.config.critical_threshold
        }
    
    def defect_tolerance_analysis(self, max_defect_rate: float = 0.5, n_steps: int = 20) -> Dict:
        """
        Analyze system tolerance to defects.
        """
        defect_rates = np.linspace(0, max_defect_rate, n_steps)
        results = []
        
        for rate in defect_rates:
            site_result = self.site_percolation(rate, n_trials=50)
            bond_result = self.bond_percolation(rate, n_trials=50)
            
            results.append({
                "defect_rate": rate,
                "functional_fraction": site_result["max_cluster_fraction"],
                "site_percolation": site_result["percolation_probability"],
                "bond_percolation": bond_result["percolation_probability"]
            })
        
        # Find acceptable defect rate (where functional fraction > 0.9)
        acceptable_rate = 0.0
        for r in results:
            if r["functional_fraction"] >= 0.9:
                acceptable_rate = r["defect_rate"]
        
        return {
            "results": results,
            "acceptable_defect_rate": acceptable_rate,
            "manufacturing_margin": acceptable_rate - self.config.pe_defect_rate
        }
    
    def _find_largest_cluster(self, active_nodes: Set[int]) -> int:
        """Find size of largest connected component among active nodes."""
        if not active_nodes:
            return 0
        
        visited = set()
        max_size = 0
        
        for start in active_nodes:
            if start not in visited:
                component_size = 0
                queue = [start]
                while queue:
                    node = queue.pop(0)
                    if node not in visited and node in active_nodes:
                        visited.add(node)
                        component_size += 1
                        for neighbor in self.graph.get_neighbors(node):
                            if neighbor in active_nodes:
                                queue.append(neighbor)
                max_size = max(max_size, component_size)
        
        return max_size
    
    def _find_largest_cluster_bond(self, active_edges: Set[Tuple[int, int]]) -> int:
        """Find largest cluster with bond percolation."""
        # Build adjacency from active edges
        adj = defaultdict(set)
        for u, v in active_edges:
            adj[u].add(v)
            adj[v].add(u)
        
        visited = set()
        max_size = 0
        
        for start in range(self.graph.n_nodes):
            if start not in visited and start in adj:
                component_size = 0
                queue = [start]
                while queue:
                    node = queue.pop(0)
                    if node not in visited:
                        visited.add(node)
                        component_size += 1
                        queue.extend(adj[node] - visited)
                max_size = max(max_size, component_size)
        
        return max_size
    
    def _check_spanning(self, active_nodes: Set[int]) -> bool:
        """Check if active nodes span from top to bottom."""
        # Top row nodes
        top_nodes = {i for i in range(self.graph.config.cols) if i in active_nodes}
        # Bottom row nodes
        bottom_start = (self.graph.config.rows - 1) * self.graph.config.cols
        bottom_nodes = {i for i in range(bottom_start, bottom_start + self.graph.config.cols) 
                       if i in active_nodes}
        
        if not top_nodes or not bottom_nodes:
            return False
        
        # BFS from top
        visited = set()
        queue = list(top_nodes)
        
        while queue:
            node = queue.pop(0)
            if node not in visited and node in active_nodes:
                visited.add(node)
                for neighbor in self.graph.get_neighbors(node):
                    if neighbor in active_nodes:
                        queue.append(neighbor)
        
        return bool(visited & bottom_nodes)
    
    def _check_spanning_bond(self, active_edges: Set[Tuple[int, int]]) -> bool:
        """Check spanning with bond percolation."""
        adj = defaultdict(set)
        for u, v in active_edges:
            adj[u].add(v)
            adj[v].add(u)
        
        top_nodes = set(range(self.graph.config.cols))
        bottom_start = (self.graph.config.rows - 1) * self.graph.config.cols
        bottom_nodes = set(range(bottom_start, bottom_start + self.graph.config.cols))
        
        visited = set()
        queue = list(top_nodes)
        
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(adj[node] - visited)
        
        return bool(visited & bottom_nodes)
    
    def _interpolate_threshold(self, probs: np.ndarray, perc_probs: List[float]) -> float:
        """Interpolate to find threshold where percolation probability = 0.5."""
        for i in range(len(perc_probs) - 1):
            if perc_probs[i] >= 0.5 > perc_probs[i + 1]:
                # Linear interpolation
                t = (0.5 - perc_probs[i]) / (perc_probs[i + 1] - perc_probs[i])
                return probs[i] + t * (probs[i + 1] - probs[i])
        return 0.5


# ============================================================================
# Network Flow Analysis
# ============================================================================

class NetworkFlowAnalysis:
    """
    Max-flow min-cut analysis for PE network bandwidth.
    """
    
    def __init__(self, graph: PEInterconnectionGraph):
        self.graph = graph
    
    def max_flow(self, source: int, sink: int) -> Tuple[float, List[Tuple[int, int]]]:
        """
        Compute maximum flow using Edmonds-Karp algorithm.
        
        Returns (max_flow, min_cut_edges).
        """
        # Build residual graph
        residual = defaultdict(dict)
        for u in self.graph.adjacency:
            for v, cap in self.graph.adjacency[u].items():
                residual[u][v] = cap
                residual[v][u] = 0.0
        
        max_flow = 0.0
        parent = {}
        
        # BFS to find augmenting path
        def bfs():
            visited = set([source])
            queue = [source]
            parent.clear()
            
            while queue:
                u = queue.pop(0)
                for v in residual[u]:
                    if v not in visited and residual[u][v] > 0:
                        visited.add(v)
                        parent[v] = u
                        if v == sink:
                            return True
                        queue.append(v)
            return False
        
        # Augment flow
        while bfs():
            # Find minimum residual capacity on path
            path_flow = float('inf')
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                v = u
            
            max_flow += path_flow
            
            # Update residual capacities
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u
        
        # Find min-cut edges
        # BFS from source in residual graph
        visited = set([source])
        queue = [source]
        while queue:
            u = queue.pop(0)
            for v in residual[u]:
                if v not in visited and residual[u][v] > 0:
                    visited.add(v)
                    queue.append(v)
        
        # Min-cut edges go from visited to unvisited
        min_cut = []
        for u in visited:
            for v in self.graph.adjacency[u]:
                if v not in visited:
                    min_cut.append((u, v))
        
        return max_flow, min_cut
    
    def systolic_dataflow_analysis(self) -> Dict:
        """
        Analyze bandwidth for systolic array dataflow.
        
        Models data movement in a 2D systolic array.
        """
        rows = self.graph.config.rows
        cols = self.graph.config.cols
        
        # Horizontal flow (weight stationary)
        h_bandwidth = self._compute_row_bandwidth()
        
        # Vertical flow (input stationary)
        v_bandwidth = self._compute_col_bandwidth()
        
        # Diagonal flow (output stationary)
        d_bandwidth = self._compute_diagonal_bandwidth()
        
        # Total systolic throughput
        # For a systolic array, throughput = min of all directions
        total_bandwidth = min(h_bandwidth, v_bandwidth, d_bandwidth)
        
        # Bottleneck identification
        bottlenecks = []
        if h_bandwidth == total_bandwidth:
            bottlenecks.append("horizontal")
        if v_bandwidth == total_bandwidth:
            bottlenecks.append("vertical")
        if d_bandwidth == total_bandwidth:
            bottlenecks.append("diagonal")
        
        return {
            "horizontal_bandwidth": h_bandwidth,
            "vertical_bandwidth": v_bandwidth,
            "diagonal_bandwidth": d_bandwidth,
            "total_systolic_bandwidth": total_bandwidth,
            "bottleneck_directions": bottlenecks,
            "theoretical_peak": rows * cols * self.graph.config.local_bandwidth,
            "efficiency": total_bandwidth / (rows * cols * self.graph.config.local_bandwidth)
        }
    
    def _compute_row_bandwidth(self) -> float:
        """Compute total horizontal bandwidth."""
        total = 0.0
        for r in range(self.graph.config.rows):
            row_bandwidth = 0.0
            for c in range(self.graph.config.cols - 1):
                node = r * self.graph.config.cols + c
                right = r * self.graph.config.cols + c + 1
                row_bandwidth += self.graph.get_edge_weight(node, right)
            total += row_bandwidth
        return total
    
    def _compute_col_bandwidth(self) -> float:
        """Compute total vertical bandwidth."""
        total = 0.0
        for c in range(self.graph.config.cols):
            col_bandwidth = 0.0
            for r in range(self.graph.config.rows - 1):
                node = r * self.graph.config.cols + c
                down = (r + 1) * self.graph.config.cols + c
                col_bandwidth += self.graph.get_edge_weight(node, down)
            total += col_bandwidth
        return total
    
    def _compute_diagonal_bandwidth(self) -> float:
        """Compute diagonal bandwidth (if diagonal links exist)."""
        # For mesh without diagonal links, approximate through routing
        # Each diagonal path requires 2 hops
        return min(self._compute_row_bandwidth(), self._compute_col_bandwidth()) / 2
    
    def bottleneck_analysis(self) -> Dict:
        """
        Identify bottlenecks in the network.
        """
        bottlenecks = []
        
        # Edge utilization (assume uniform traffic)
        edge_flows = defaultdict(float)
        
        # Sample random pairs and compute paths
        n_samples = 100
        for _ in range(n_samples):
            source = np.random.randint(0, self.graph.n_nodes)
            sink = np.random.randint(0, self.graph.n_nodes)
            if source != sink:
                path, _ = NetworkMetrics(self.graph).shortest_path(source, sink)
                for i in range(len(path) - 1):
                    edge = (min(path[i], path[i+1]), max(path[i], path[i+1]))
                    edge_flows[edge] += 1
        
        # Normalize
        max_flow = max(edge_flows.values()) if edge_flows else 1
        for edge, flow in edge_flows.items():
            if flow > max_flow * 0.8:  # High utilization
                bottlenecks.append({
                    "edge": edge,
                    "utilization": flow / max_flow,
                    "coordinates": (self.graph.node_coords[edge[0]], 
                                   self.graph.node_coords[edge[1]])
                })
        
        # Compute centrality measures
        betweenness = self._compute_betweenness_centrality()
        
        # High centrality nodes are critical
        critical_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "bottleneck_edges": bottlenecks[:10],
            "critical_nodes": [(n, c) for n, c in critical_nodes],
            "max_edge_utilization": max(edge_flows.values()) / n_samples if edge_flows else 0
        }
    
    def _compute_betweenness_centrality(self, sample_size: int = 500) -> Dict[int, float]:
        """
        Compute betweenness centrality using sampling.
        """
        centrality = defaultdict(float)
        
        for _ in range(sample_size):
            source = np.random.randint(0, self.graph.n_nodes)
            sink = np.random.randint(0, self.graph.n_nodes)
            
            if source != sink:
                path, _ = NetworkMetrics(self.graph).shortest_path(source, sink)
                for node in path[1:-1]:  # Exclude source and sink
                    centrality[node] += 1
        
        # Normalize
        total = sum(centrality.values())
        if total > 0:
            for node in centrality:
                centrality[node] /= total
        
        return dict(centrality)
    
    def optimal_routing(self, traffic_pattern: str = "uniform") -> Dict:
        """
        Compute optimal routing strategy.
        """
        if traffic_pattern == "uniform":
            return self._uniform_routing()
        elif traffic_pattern == "transpose":
            return self._transpose_routing()
        elif traffic_pattern == "hotspot":
            return self._hotspot_routing()
        else:
            return {"routing": "xy", "description": "Dimension-ordered routing"}
    
    def _uniform_routing(self) -> Dict:
        """Uniform random traffic routing."""
        # XY routing is optimal for mesh with uniform traffic
        return {
            "routing": "xy",
            "description": "Dimension-ordered (X then Y) routing",
            "avg_hops": (self.graph.config.rows + self.graph.config.cols) / 3,
            "max_hops": self.graph.config.rows + self.graph.config.cols - 2,
            "throughput_efficiency": 1.0  # Optimal for uniform traffic
        }
    
    def _transpose_routing(self) -> Dict:
        """Transpose traffic pattern (corner-to-corner)."""
        return {
            "routing": "adaptive",
            "description": "Adaptive routing for transpose pattern",
            "avg_hops": self.graph.config.rows + self.graph.config.cols - 2,
            "max_hops": self.graph.config.rows + self.graph.config.cols - 2,
            "throughput_efficiency": 0.5  # Reduced due to congestion
        }
    
    def _hotspot_routing(self) -> Dict:
        """Hotspot traffic pattern."""
        return {
            "routing": "load_balanced",
            "description": "Load-balanced routing for hotspot pattern",
            "avg_hops": (self.graph.config.rows + self.graph.config.cols) / 4,
            "throughput_efficiency": 0.3  # Severely limited by hotspot
        }


# ============================================================================
# Visualization
# ============================================================================

def create_visualizations(graph: PEInterconnectionGraph, metrics: NetworkMetrics,
                         percolation: PercolationAnalysis, flow: NetworkFlowAnalysis,
                         output_dir: str = "/home/z/my-project/research"):
    """Create all visualizations."""
    output_path = Path(output_dir)
    
    # 1. Network Topology Visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    
    # 1a. Network topology
    ax = axes[0, 0]
    ax.set_title("PE Network Topology (32×32 Mesh)", fontsize=12, fontweight='bold')
    
    # Draw nodes
    for node in range(graph.n_nodes):
        r, c = graph.node_coords[node]
        degree = graph.get_degree(node)
        color = plt.cm.viridis(degree / 6)
        ax.scatter(c, -r, c=[color], s=20, alpha=0.7)
    
    # Draw edges (sample for visibility)
    edge_count = 0
    for node in range(min(graph.n_nodes, 100)):  # Limit for visibility
        r, c = graph.node_coords[node]
        for neighbor in graph.get_neighbors(node):
            nr, nc = graph.node_coords[neighbor]
            if nr > r or (nr == r and nc > c):  # Draw each edge once
                ax.plot([c, nc], [-r, -nr], 'b-', alpha=0.1, linewidth=0.5)
                edge_count += 1
    
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_aspect('equal')
    ax.set_xlim(-1, graph.config.cols)
    ax.set_ylim(-graph.config.rows, 1)
    
    # 1b. Degree distribution
    ax = axes[0, 1]
    ax.set_title("Degree Distribution", fontsize=12, fontweight='bold')
    degrees = graph.get_all_degrees()
    ax.hist(degrees, bins=range(min(degrees), max(degrees) + 2), 
            edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel("Degree")
    ax.set_ylabel("Frequency")
    ax.axvline(np.mean(degrees), color='red', linestyle='--', 
               label=f'Mean: {np.mean(degrees):.2f}')
    ax.legend()
    
    # 1c. Clustering coefficient heatmap
    ax = axes[1, 0]
    ax.set_title("Clustering Coefficient Heatmap", fontsize=12, fontweight='bold')
    
    cc_data = metrics.clustering_coefficient()
    cc_grid = np.zeros((graph.config.rows, graph.config.cols))
    for node, cc in cc_data["node_clustering"].items():
        r, c = graph.node_coords[node]
        cc_grid[r, c] = cc
    
    im = ax.imshow(cc_grid, cmap='RdYlGn', aspect='equal')
    plt.colorbar(im, ax=ax, label='Clustering Coefficient')
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    
    # 1d. Path length distribution
    ax = axes[1, 1]
    ax.set_title("Path Length Distribution", fontsize=12, fontweight='bold')
    
    # Sample path lengths
    path_lengths = []
    for _ in range(500):
        source = np.random.randint(0, graph.n_nodes)
        sink = np.random.randint(0, graph.n_nodes)
        if source != sink:
            _, dist = metrics.shortest_path(source, sink)
            if dist < float('inf'):
                path_lengths.append(dist)
    
    ax.hist(path_lengths, bins=30, edgecolor='black', alpha=0.7, color='forestgreen')
    ax.set_xlabel("Path Length (hop count)")
    ax.set_ylabel("Frequency")
    ax.axvline(np.mean(path_lengths), color='red', linestyle='--',
               label=f'Mean: {np.mean(path_lengths):.2f}')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path / "cycle8_network_topology.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Percolation Analysis
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 2a. Percolation probability vs defect rate
    ax = axes[0]
    ax.set_title("Percolation Probability vs Defect Rate", fontsize=12, fontweight='bold')
    
    threshold_results = percolation.critical_threshold_analysis(n_points=15, n_trials=30)
    
    probs = [r["defect_probability"] for r in threshold_results["site_percolation_results"]]
    site_perc = [r["percolation_probability"] for r in threshold_results["site_percolation_results"]]
    bond_perc = [r["percolation_probability"] for r in threshold_results["bond_percolation_results"]]
    
    ax.plot(probs, site_perc, 'b-o', label='Site Percolation', linewidth=2)
    ax.plot(probs, bond_perc, 'r-s', label='Bond Percolation', linewidth=2)
    ax.axvline(threshold_results["site_critical_threshold"], color='blue', 
               linestyle='--', label=f'Site Threshold: {threshold_results["site_critical_threshold"]:.3f}')
    ax.axvline(threshold_results["bond_critical_threshold"], color='red',
               linestyle='--', label=f'Bond Threshold: {threshold_results["bond_critical_threshold"]:.3f}')
    ax.axhline(0.5, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel("Defect Probability")
    ax.set_ylabel("Percolation Probability")
    ax.legend(loc='upper right', fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    # 2b. Cluster size vs defect rate
    ax = axes[1]
    ax.set_title("Largest Cluster Size vs Defect Rate", fontsize=12, fontweight='bold')
    
    cluster_sizes = [r["max_cluster_fraction"] for r in threshold_results["site_percolation_results"]]
    ax.plot(probs, cluster_sizes, 'g-^', linewidth=2, markersize=8)
    ax.axhline(0.9, color='orange', linestyle='--', label='90% Functional Threshold')
    ax.set_xlabel("Defect Probability")
    ax.set_ylabel("Largest Cluster Fraction")
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    # 2c. Critical threshold comparison
    ax = axes[2]
    ax.set_title("Critical Threshold Analysis", fontsize=12, fontweight='bold')
    
    categories = ['Site\n(Measured)', 'Bond\n(Measured)', 'Site\n(Theoretical)']
    values = [threshold_results["site_critical_threshold"],
              threshold_results["bond_critical_threshold"],
              threshold_results["theoretical_site_threshold"]]
    colors = ['blue', 'red', 'gray']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel("Critical Threshold")
    ax.set_ylim(0, 1)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10)
    
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path / "cycle8_percolation_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Network Flow Analysis
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 3a. Systolic dataflow bandwidth
    ax = axes[0]
    ax.set_title("Systolic Dataflow Bandwidth", fontsize=12, fontweight='bold')
    
    systolic = flow.systolic_dataflow_analysis()
    
    categories = ['Horizontal', 'Vertical', 'Diagonal', 'Total\nSystolic']
    values = [systolic["horizontal_bandwidth"]/1e3,
              systolic["vertical_bandwidth"]/1e3,
              systolic["diagonal_bandwidth"]/1e3,
              systolic["total_systolic_bandwidth"]/1e3]
    colors = ['blue', 'green', 'orange', 'red']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel("Bandwidth (TB/s)")
    ax.set_ylim(0, max(values) * 1.2)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                f'{val:.1f}', ha='center', va='bottom', fontsize=10)
    
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3b. Bandwidth efficiency
    ax = axes[1]
    ax.set_title("Bandwidth Efficiency Analysis", fontsize=12, fontweight='bold')
    
    efficiency_categories = ['Theoretical\nPeak', 'Achievable\nPeak', 'Efficiency']
    efficiency_values = [systolic["theoretical_peak"]/1e3,
                         systolic["total_systolic_bandwidth"]/1e3,
                         systolic["efficiency"] * 100]
    
    bars = ax.bar(efficiency_categories[:2], efficiency_values[:2], 
                  color=['gray', 'steelblue'], alpha=0.7, edgecolor='black')
    
    ax2 = ax.twinx()
    ax2.bar(efficiency_categories[2], efficiency_values[2], 
            color='green', alpha=0.7, edgecolor='black')
    
    ax.set_ylabel("Bandwidth (TB/s)")
    ax2.set_ylabel("Efficiency (%)")
    ax.set_ylim(0, efficiency_values[0] * 1.2)
    ax2.set_ylim(0, 120)
    
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3c. Routing comparison
    ax = axes[2]
    ax.set_title("Routing Strategy Comparison", fontsize=12, fontweight='bold')
    
    routing_patterns = ['Uniform', 'Transpose', 'Hotspot']
    efficiencies = [1.0, 0.5, 0.3]
    avg_hops = [32/3, 62, 32/6]  # Approximate values
    
    x = np.arange(len(routing_patterns))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, efficiencies, width, label='Efficiency', color='steelblue')
    bars2 = ax.bar(x + width/2, [h/62 for h in avg_hops], width, label='Normalized Hops', color='orange')
    
    ax.set_ylabel("Normalized Value")
    ax.set_xticks(x)
    ax.set_xticklabels(routing_patterns)
    ax.legend()
    ax.set_ylim(0, 1.2)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path / "cycle8_network_flow.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 4. Small-World and Scale-Free Analysis
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 4a. Small-world coefficient
    ax = axes[0]
    ax.set_title("Small-World Network Analysis", fontsize=12, fontweight='bold')
    
    sw = metrics.small_world_coefficient()
    
    labels = ['σ (sigma)', 'ω (omega)']
    values = [sw["sigma"], sw["omega"]]
    colors = ['green' if sw["is_small_world"] else 'red', 'blue']
    
    bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(1.0, color='red', linestyle='--', label='Small-World Threshold (σ=1)')
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_ylabel("Coefficient Value")
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add text annotation
    ax.text(0.5, 0.9, f"Is Small-World: {sw['is_small_world']}", 
            transform=ax.transAxes, ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 4b. Scale-free analysis (degree distribution log-log)
    ax = axes[1]
    ax.set_title("Scale-Free Network Analysis", fontsize=12, fontweight='bold')
    
    sf = metrics.scale_free_analysis()
    degrees = graph.get_all_degrees()
    degree_counts = Counter(degrees)
    
    k = np.array(sorted(degree_counts.keys()))
    p_k = np.array([degree_counts[ki] for ki in k])
    p_k = p_k / p_k.sum()
    
    ax.loglog(k, p_k, 'bo-', markersize=8, label='Observed')
    
    # Fit power law
    if sf["power_law_exponent"] > 0:
        k_fit = k[k > 0]
        p_fit = k_fit ** (-sf["power_law_exponent"])
        p_fit = p_fit / p_fit.sum()
        ax.loglog(k_fit, p_fit, 'r--', linewidth=2, 
                  label=f'Power Law (γ={sf["power_law_exponent"]:.2f})')
    
    ax.set_xlabel("Degree k")
    ax.set_ylabel("P(k)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add text annotation
    ax.text(0.7, 0.9, f"Is Scale-Free: {sf['is_scale_free']}\nR² = {sf['r_squared']:.3f}", 
            transform=ax.transAxes, ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path / "cycle8_network_properties.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to {output_path}")


# ============================================================================
# Main Simulation
# ============================================================================

def run_simulation():
    """Run complete network-theoretic analysis."""
    print("=" * 70)
    print("Cycle 8: Network-Theoretic Inference Architecture Analysis")
    print("=" * 70)
    
    # Configuration
    pe_config = PEArrayConfig(
        rows=32,
        cols=32,
        neighbor_connectivity="mesh",
        local_bandwidth=64.0,
        long_range_prob=0.05
    )
    
    defect_config = DefectConfig(
        pe_defect_rate=1e-8,
        link_defect_rate=1e-7,
        critical_threshold=0.5927
    )
    
    print(f"\n1. BUILDING PE INTERCONNECTION NETWORK")
    print("-" * 50)
    print(f"   Array Size: {pe_config.rows}×{pe_config.cols} = {pe_config.n_pes} PEs")
    print(f"   Topology: {pe_config.neighbor_connectivity}")
    print(f"   Link Bandwidth: {pe_config.local_bandwidth} GB/s")
    
    # Build graph
    graph = PEInterconnectionGraph(pe_config)
    
    # Compute metrics
    print(f"\n2. COMPUTING NETWORK METRICS")
    print("-" * 50)
    metrics = NetworkMetrics(graph)
    all_metrics = metrics.compute_all_metrics()
    
    print(f"   Nodes: {all_metrics['basic_metrics']['n_nodes']}")
    print(f"   Edges: {all_metrics['basic_metrics']['n_edges']}")
    print(f"   Density: {all_metrics['basic_metrics']['density']:.6f}")
    print(f"   Avg Degree: {all_metrics['basic_metrics']['avg_degree']:.2f}")
    
    print(f"\n3. PATH ANALYSIS")
    print("-" * 50)
    path_metrics = all_metrics["path_metrics"]
    print(f"   Network Diameter: {path_metrics['diameter']:.2f} hops")
    print(f"   Avg Path Length: {path_metrics['avg_path_length']:.2f} hops")
    
    print(f"\n4. CLUSTERING ANALYSIS")
    print("-" * 50)
    clustering = all_metrics["clustering_coefficient"]
    print(f"   Global Clustering: {clustering['global_clustering']:.4f}")
    print(f"   Center Clustering: {clustering['avg_center_clustering']:.4f}")
    print(f"   Edge Clustering: {clustering['avg_edge_clustering']:.4f}")
    
    print(f"\n5. SMALL-WORLD ANALYSIS")
    print("-" * 50)
    sw = all_metrics["small_world_coefficient"]
    print(f"   σ (sigma): {sw['sigma']:.4f}")
    print(f"   ω (omega): {sw['omega']:.4f}")
    print(f"   Is Small-World: {sw['is_small_world']}")
    
    print(f"\n6. SCALE-FREE ANALYSIS")
    print("-" * 50)
    sf = all_metrics["scale_free_analysis"]
    print(f"   Power Law Exponent (γ): {sf['power_law_exponent']:.4f}")
    print(f"   R-squared: {sf['r_squared']:.4f}")
    print(f"   Is Scale-Free: {sf['is_scale_free']}")
    print(f"   Hub Nodes: {len(sf['hub_nodes'])}")
    
    # Fix boolean values for JSON serialization
    def json_serialize(obj):
        if isinstance(obj, bool):
            return str(obj).lower()
        return obj
    
    # Percolation analysis
    print(f"\n7. PERCOLATION ANALYSIS")
    print("-" * 50)
    percolation = PercolationAnalysis(graph, defect_config)
    
    # Quick percolation test
    site_result = percolation.site_percolation(0.3, n_trials=30)
    bond_result = percolation.bond_percolation(0.3, n_trials=30)
    
    print(f"   Site Percolation (p=0.3): {site_result['percolation_probability']:.3f}")
    print(f"   Bond Percolation (p=0.3): {bond_result['percolation_probability']:.3f}")
    
    # Critical threshold
    threshold_results = percolation.critical_threshold_analysis(n_points=12, n_trials=25)
    print(f"   Critical Site Threshold: {threshold_results['site_critical_threshold']:.4f}")
    print(f"   Critical Bond Threshold: {threshold_results['bond_critical_threshold']:.4f}")
    print(f"   Theoretical Threshold: {threshold_results['theoretical_site_threshold']:.4f}")
    
    # Defect tolerance
    tolerance = percolation.defect_tolerance_analysis(max_defect_rate=0.4, n_steps=15)
    print(f"   Acceptable Defect Rate: {tolerance['acceptable_defect_rate']:.4f}")
    print(f"   Manufacturing Margin: {tolerance['manufacturing_margin']:.4e}")
    
    # Network flow analysis
    print(f"\n8. NETWORK FLOW ANALYSIS")
    print("-" * 50)
    flow = NetworkFlowAnalysis(graph)
    
    # Systolic dataflow
    systolic = flow.systolic_dataflow_analysis()
    print(f"   Horizontal Bandwidth: {systolic['horizontal_bandwidth']/1e3:.2f} TB/s")
    print(f"   Vertical Bandwidth: {systolic['vertical_bandwidth']/1e3:.2f} TB/s")
    print(f"   Total Systolic Bandwidth: {systolic['total_systolic_bandwidth']/1e3:.2f} TB/s")
    print(f"   Bandwidth Efficiency: {systolic['efficiency']*100:.1f}%")
    print(f"   Bottleneck: {systolic['bottleneck_directions']}")
    
    # Bottleneck analysis
    bottlenecks = flow.bottleneck_analysis()
    print(f"   Critical Nodes (top 5): {bottlenecks['critical_nodes'][:5]}")
    
    # Routing analysis
    print(f"\n9. ROUTING ANALYSIS")
    print("-" * 50)
    for pattern in ["uniform", "transpose", "hotspot"]:
        routing = flow.optimal_routing(pattern)
        print(f"   {pattern.capitalize()} Traffic:")
        print(f"     Strategy: {routing['routing']}")
        print(f"     Avg Hops: {routing['avg_hops']:.2f}")
        print(f"     Efficiency: {routing['throughput_efficiency']*100:.1f}%")
    
    # Create visualizations
    print(f"\n10. GENERATING VISUALIZATIONS")
    print("-" * 50)
    create_visualizations(graph, metrics, percolation, flow)
    
    # Compile results - convert numpy types to Python native
    results = {
        "configuration": {
            "array_size": f"{pe_config.rows}×{pe_config.cols}",
            "n_pes": int(pe_config.n_pes),
            "topology": pe_config.neighbor_connectivity,
            "link_bandwidth_gb_s": float(pe_config.local_bandwidth)
        },
        "network_metrics": {
            "n_nodes": int(all_metrics["basic_metrics"]["n_nodes"]),
            "n_edges": int(all_metrics["basic_metrics"]["n_edges"]),
            "density": float(all_metrics["basic_metrics"]["density"]),
            "avg_degree": float(all_metrics["basic_metrics"]["avg_degree"]),
            "diameter": float(path_metrics["diameter"]),
            "avg_path_length": float(path_metrics["avg_path_length"]),
            "global_clustering": float(clustering["global_clustering"]),
            "small_world_sigma": float(sw["sigma"]),
            "is_small_world": bool(sw["is_small_world"]),
            "power_law_exponent": float(sf["power_law_exponent"]),
            "is_scale_free": bool(sf["is_scale_free"])
        },
        "percolation_analysis": {
            "site_critical_threshold": float(threshold_results["site_critical_threshold"]),
            "bond_critical_threshold": float(threshold_results["bond_critical_threshold"]),
            "acceptable_defect_rate": float(tolerance["acceptable_defect_rate"]),
            "manufacturing_margin": float(tolerance["manufacturing_margin"])
        },
        "flow_analysis": {
            "horizontal_bandwidth_tb_s": float(systolic["horizontal_bandwidth"]/1e3),
            "vertical_bandwidth_tb_s": float(systolic["vertical_bandwidth"]/1e3),
            "total_systolic_bandwidth_tb_s": float(systolic["total_systolic_bandwidth"]/1e3),
            "efficiency": float(systolic["efficiency"]),
            "bottleneck_directions": systolic["bottleneck_directions"]
        },
        "key_findings": {
            "network_resilience": f"Maintains >90% functionality up to {tolerance['acceptable_defect_rate']*100:.1f}% defects",
            "optimal_topology": "2D mesh with potential for small-world enhancement",
            "data_movement_efficiency": f"{systolic['efficiency']*100:.1f}% of theoretical peak bandwidth"
        }
    }
    
    # Save results
    output_path = Path("/home/z/my-project/research")
    with open(output_path / "cycle8_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_path}/cycle8_results.json")
    
    return results


if __name__ == "__main__":
    results = run_simulation()
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"  • Network Diameter: {results['network_metrics']['diameter']:.1f} hops")
    print(f"  • Average Path Length: {results['network_metrics']['avg_path_length']:.2f} hops")
    print(f"  • Global Clustering: {results['network_metrics']['global_clustering']:.4f}")
    print(f"  • Small-World σ: {results['network_metrics']['small_world_sigma']:.4f}")
    print(f"  • Percolation Threshold: {results['percolation_analysis']['site_critical_threshold']:.4f}")
    print(f"  • Systolic Bandwidth: {results['flow_analysis']['total_systolic_bandwidth_tb_s']:.2f} TB/s")
    print(f"  • Bandwidth Efficiency: {results['flow_analysis']['efficiency']*100:.1f}%")
