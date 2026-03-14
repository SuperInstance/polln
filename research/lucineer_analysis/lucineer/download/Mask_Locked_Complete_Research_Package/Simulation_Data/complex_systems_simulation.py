#!/usr/bin/env python3
"""
Complex Systems Analysis for Mask-Locked Inference Chip
=======================================================

This module implements comprehensive complex systems models including:
1. Self-Organized Criticality in Neural Network Activations
2. Network Science Analysis of Chip Architecture
3. Percolation Theory for Yield Modeling
4. Cellular Automata for Thermal Management
5. Game Theory for Resource Allocation
6. Information Thermodynamics Analysis

Author: Complex Systems Research Team
Date: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
from collections import defaultdict
import networkx as nx
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SECTION 1: SELF-ORGANIZED CRITICALITY IN NEURAL ACTIVATIONS
# ============================================================================

class NeuralActivationSOC:
    """
    Model neural network activations as exhibiting self-organized criticality.
    
    Key concepts:
    - Power-law distributions in activation magnitudes
    - Avalanches: cascades of activated neurons
    - Critical branching ratio σ ≈ 1
    """
    
    def __init__(self, n_neurons: int = 1024, threshold: float = 0.1):
        self.n_neurons = n_neurons
        self.threshold = threshold
        self.activations = np.zeros(n_neurons)
        self.avalanche_sizes = []
        self.avalanche_durations = []
        self.activation_history = []
        
    def _branching_process(self, sigma: float = 1.0) -> float:
        """
        Critical branching process for avalanche propagation.
        σ < 1: subcritical, σ > 1: supercritical, σ = 1: critical
        """
        # Number of offspring from each active neuron
        return np.random.poisson(sigma)
    
    def simulate_avalanche(self, sigma: float = 1.0, max_steps: int = 1000) -> Tuple[int, int]:
        """
        Simulate a single avalanche event.
        Returns (size, duration) of the avalanche.
        """
        # Initialize with single seed neuron
        active = {np.random.randint(0, self.n_neurons)}
        size = 0
        duration = 0
        
        while active and duration < max_steps:
            new_active = set()
            for neuron in active:
                size += 1
                # Branch to neighbors
                n_offspring = self._branching_process(sigma)
                for _ in range(n_offspring):
                    # Connect to random neighbor (small-world topology)
                    neighbor = np.random.randint(0, self.n_neurons)
                    new_active.add(neighbor)
            active = new_active
            duration += 1
            
        return size, duration
    
    def run_simulation(self, n_avalanches: int = 10000, sigma: float = 1.0):
        """Run multiple avalanche simulations."""
        self.avalanche_sizes = []
        self.avalanche_durations = []
        
        for _ in range(n_avalanches):
            size, duration = self.simulate_avalanche(sigma)
            self.avalanche_sizes.append(size)
            self.avalanche_durations.append(duration)
            
        self.avalanche_sizes = np.array(self.avalanche_sizes)
        self.avalanche_durations = np.array(self.avalanche_durations)
    
    def fit_power_law(self, data: np.ndarray) -> Tuple[float, float, float]:
        """
        Fit power-law distribution: P(x) ~ x^(-α)
        Returns (alpha, xmin, ks_statistic)
        """
        # Filter out zeros and very small values
        data = data[data > 1]
        if len(data) < 10:
            return 2.0, 1.0, 1.0
        
        # Use maximum likelihood estimation
        xmin = np.percentile(data, 10)
        data = data[data >= xmin]
        n = len(data)
        
        if n == 0:
            return 2.0, xmin, 1.0
            
        # MLE for power-law exponent
        alpha = 1 + n / np.sum(np.log(data / xmin))
        
        # KS statistic for goodness of fit
        sorted_data = np.sort(data)
        cdf_empirical = np.arange(1, n + 1) / n
        cdf_theoretical = 1 - (sorted_data / xmin) ** (-alpha + 1)
        ks_stat = np.max(np.abs(cdf_empirical - cdf_theoretical))
        
        return alpha, xmin, ks_stat
    
    def analyze_criticality(self) -> Dict:
        """Comprehensive criticality analysis."""
        # Fit power-law to sizes
        alpha_size, xmin_size, ks_size = self.fit_power_law(self.avalanche_sizes)
        
        # Fit power-law to durations
        alpha_dur, xmin_dur, ks_dur = self.fit_power_law(self.avalanche_durations)
        
        # Size vs duration scaling: S ~ T^γ
        valid = (self.avalanche_sizes > 1) & (self.avalanche_durations > 1)
        if np.sum(valid) > 10:
            log_sizes = np.log(self.avalanche_sizes[valid])
            log_durs = np.log(self.avalanche_durations[valid])
            gamma, _, r_value, _, _ = stats.linregress(log_durs, log_sizes)
        else:
            gamma = 1.5
            r_value = 0
            
        return {
            'size_exponent': alpha_size,
            'duration_exponent': alpha_dur,
            'scaling_exponent': gamma,
            'ks_statistic_size': ks_size,
            'ks_statistic_duration': ks_dur,
            'r_squared': r_value ** 2,
            'is_critical': 1.5 < alpha_size < 3.0 and ks_size < 0.1
        }
    
    def plot_avalanche_distribution(self, save_path: str = None):
        """Plot avalanche size and duration distributions."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Size distribution
        sizes = self.avalanche_sizes[self.avalanche_sizes > 0]
        if len(sizes) > 0:
            ax = axes[0]
            bins = np.logspace(0, np.log10(max(sizes)), 30)
            ax.hist(sizes, bins=bins, density=True, alpha=0.7, color='steelblue')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Avalanche Size')
            ax.set_ylabel('Probability Density')
            ax.set_title('Avalanche Size Distribution')
            
        # Duration distribution
        durations = self.avalanche_durations[self.avalanche_durations > 0]
        if len(durations) > 0:
            ax = axes[1]
            bins = np.logspace(0, np.log10(max(durations)), 30)
            ax.hist(durations, bins=bins, density=True, alpha=0.7, color='coral')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Avalanche Duration')
            ax.set_ylabel('Probability Density')
            ax.set_title('Avalanche Duration Distribution')
            
        # Size vs Duration scaling
        valid = (self.avalanche_sizes > 1) & (self.avalanche_durations > 1)
        if np.sum(valid) > 0:
            ax = axes[2]
            ax.scatter(self.avalanche_durations[valid], self.avalanche_sizes[valid], 
                      alpha=0.1, s=1, color='green')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Duration')
            ax.set_ylabel('Size')
            ax.set_title('Size-Duration Scaling')
            
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 2: NETWORK SCIENCE OF CHIP ARCHITECTURE
# ============================================================================

class ChipNetworkModel:
    """
    Model the chip architecture as a complex network.
    Nodes = Processing Elements (PEs)
    Edges = Interconnect wires
    
    Key metrics:
    - Degree distribution
    - Clustering coefficient
    - Average path length
    - Small-world index
    """
    
    def __init__(self, n_pes: int = 1024, topology: str = 'hybrid'):
        self.n_pes = n_pes
        self.topology = topology
        self.graph = nx.Graph()
        self._build_network()
        
    def _build_network(self):
        """Build chip network topology."""
        self.graph.clear()
        self.graph.add_nodes_from(range(self.n_pes))
        
        if self.topology == 'grid':
            self._build_grid()
        elif self.topology == 'small_world':
            self._build_small_world()
        elif self.topology == 'hybrid':
            self._build_hybrid()
        elif self.topology == 'hierarchical':
            self._build_hierarchical()
            
    def _build_grid(self):
        """2D mesh topology (traditional)."""
        side = int(np.sqrt(self.n_pes))
        for i in range(side):
            for j in range(side):
                node = i * side + j
                if i < side - 1:
                    self.graph.add_edge(node, node + side)
                if j < side - 1:
                    self.graph.add_edge(node, node + 1)
                    
    def _build_small_world(self, k: int = 8, p: float = 0.1):
        """Watts-Strogatz small-world topology."""
        # Create ring lattice
        for i in range(self.n_pes):
            for j in range(1, k // 2 + 1):
                self.graph.add_edge(i, (i + j) % self.n_pes)
                
        # Rewire edges with probability p
        edges = list(self.graph.edges())
        for u, v in edges:
            if np.random.random() < p:
                self.graph.remove_edge(u, v)
                new_v = np.random.randint(self.n_pes)
                while new_v == u:
                    new_v = np.random.randint(self.n_pes)
                self.graph.add_edge(u, new_v)
                
    def _build_hybrid(self):
        """
        Hybrid topology: local clusters with global shortcuts.
        Optimized for inference workloads.
        """
        # Create 16 clusters of 64 PEs each
        n_clusters = 16
        pes_per_cluster = self.n_pes // n_clusters
        
        # Intra-cluster connections (dense)
        for c in range(n_clusters):
            cluster_nodes = range(c * pes_per_cluster, (c + 1) * pes_per_cluster)
            # Ring within cluster
            for i in cluster_nodes:
                next_node = i + 1 if i < (c + 1) * pes_per_cluster - 1 else c * pes_per_cluster
                self.graph.add_edge(i, next_node)
                # Additional local connections
                for j in range(1, 4):
                    neighbor = i + j * 4
                    if neighbor < (c + 1) * pes_per_cluster:
                        self.graph.add_edge(i, neighbor)
                        
        # Inter-cluster connections (sparse shortcuts)
        for c in range(n_clusters):
            # Connect to 2-3 other clusters
            n_connections = np.random.randint(2, 4)
            target_clusters = np.random.choice(
                [x for x in range(n_clusters) if x != c],
                size=min(n_connections, n_clusters - 1),
                replace=False
            )
            for tc in target_clusters:
                node1 = c * pes_per_cluster + np.random.randint(pes_per_cluster)
                node2 = tc * pes_per_cluster + np.random.randint(pes_per_cluster)
                self.graph.add_edge(node1, node2)
                
    def _build_hierarchical(self):
        """
        Hierarchical topology: tree-like structure with local mesh.
        """
        # Level 0: Individual PEs
        # Level 1: Groups of 16 PEs
        # Level 2: Groups of 256 PEs
        # Level 3: Full chip
        
        for i in range(self.n_pes):
            # Connect to siblings in same group of 16
            group_start = (i // 16) * 16
            for j in range(group_start, min(group_start + 16, self.n_pes)):
                if i != j and np.random.random() < 0.3:
                    self.graph.add_edge(i, j)
                    
            # Connect to parent group (one per 256)
            super_group = (i // 256) * 256 + 128  # Representative node
            if i != super_group and np.random.random() < 0.1:
                self.graph.add_edge(i, super_group)
                
    def compute_metrics(self) -> Dict:
        """Compute network science metrics."""
        degrees = dict(self.graph.degree())
        degree_values = list(degrees.values())
        
        # Basic metrics
        metrics = {
            'n_nodes': self.graph.number_of_nodes(),
            'n_edges': self.graph.number_of_edges(),
            'avg_degree': np.mean(degree_values),
            'std_degree': np.std(degree_values),
            'min_degree': min(degree_values),
            'max_degree': max(degree_values),
        }
        
        # Clustering coefficient
        metrics['clustering_coefficient'] = nx.average_clustering(self.graph)
        
        # Path length (use largest connected component)
        if nx.is_connected(self.graph):
            metrics['avg_path_length'] = nx.average_shortest_path_length(self.graph)
            metrics['diameter'] = nx.diameter(self.graph)
        else:
            largest_cc = max(nx.connected_components(self.graph), key=len)
            subgraph = self.graph.subgraph(largest_cc)
            metrics['avg_path_length'] = nx.average_shortest_path_length(subgraph)
            metrics['diameter'] = nx.diameter(subgraph)
            metrics['connected_fraction'] = len(largest_cc) / self.n_pes
            
        # Small-world properties
        # Compare to equivalent random graph
        n_edges = self.graph.number_of_edges()
        random_graph = nx.gnm_random_graph(self.n_pes, n_edges)
        random_clustering = nx.average_clustering(random_graph)
        
        if nx.is_connected(random_graph):
            random_path = nx.average_shortest_path_length(random_graph)
        else:
            random_path = metrics['avg_path_length']
            
        if random_clustering > 0 and random_path > 0:
            metrics['small_world_index'] = (
                metrics['clustering_coefficient'] / random_clustering
            ) / (metrics['avg_path_length'] / random_path)
        else:
            metrics['small_world_index'] = 1.0
            
        # Degree distribution statistics
        metrics['degree_skewness'] = stats.skew(degree_values)
        metrics['degree_kurtosis'] = stats.kurtosis(degree_values)
        
        # Fit power-law to degree distribution
        if max(degree_values) > min(degree_values):
            try:
                fit = stats.powerlaw.fit(degree_values)
                metrics['degree_power_law_param'] = fit[0]
            except:
                metrics['degree_power_law_param'] = 1.0
                
        return metrics
    
    def analyze_communication_centrality(self) -> Dict:
        """Analyze node centrality for communication optimization."""
        # Degree centrality
        degree_cent = nx.degree_centrality(self.graph)
        
        # Betweenness centrality (bottleneck identification)
        betweenness_cent = nx.betweenness_centrality(self.graph, k=100)
        
        # Closeness centrality
        closeness_cent = nx.closeness_centrality(self.graph)
        
        # Identify critical nodes (high betweenness = potential bottlenecks)
        betweenness_values = np.array(list(betweenness_cent.values()))
        critical_threshold = np.percentile(betweenness_values, 90)
        critical_nodes = [n for n, b in betweenness_cent.items() if b >= critical_threshold]
        
        return {
            'avg_degree_centrality': np.mean(list(degree_cent.values())),
            'avg_betweenness_centrality': np.mean(betweenness_values),
            'avg_closeness_centrality': np.mean(list(closeness_cent.values())),
            'critical_nodes': critical_nodes,
            'n_critical_nodes': len(critical_nodes),
            'centrality_concentration': np.std(betweenness_values) / np.mean(betweenness_values)
        }
    
    def plot_network(self, save_path: str = None):
        """Visualize network topology."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Degree distribution
        degrees = [d for n, d in self.graph.degree()]
        ax = axes[0]
        ax.hist(degrees, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Node Degree')
        ax.set_ylabel('Frequency')
        ax.set_title('Degree Distribution')
        
        # Network visualization (sample)
        ax = axes[1]
        if self.n_pes > 256:
            sample_nodes = np.random.choice(self.n_pes, 256, replace=False)
            subgraph = self.graph.subgraph(sample_nodes)
        else:
            subgraph = self.graph
        pos = nx.spring_layout(subgraph, iterations=50)
        nx.draw(subgraph, pos, ax=ax, node_size=10, alpha=0.6, 
                node_color='coral', edge_color='gray', width=0.5)
        ax.set_title('Network Topology (Sample)')
        
        # Clustering coefficient distribution
        ax = axes[2]
        clustering = nx.clustering(self.graph)
        ax.hist(list(clustering.values()), bins=30, color='green', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Clustering Coefficient')
        ax.set_ylabel('Frequency')
        ax.set_title('Local Clustering Distribution')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 3: PERCOLATION THEORY FOR YIELD
# ============================================================================

class PercolationYieldModel:
    """
    Model chip defects using percolation theory.
    
    Key concepts:
    - Site percolation: defective PEs
    - Bond percolation: broken interconnects
    - Critical defect density for functional chip
    """
    
    def __init__(self, n_pes: int = 1024, topology: str = 'grid'):
        self.n_pes = n_pes
        self.topology = topology
        self.defect_mask = np.zeros(n_pes, dtype=bool)
        
    def create_lattice(self) -> np.ndarray:
        """Create 2D lattice for percolation simulation."""
        side = int(np.sqrt(self.n_pes))
        return np.zeros((side, side), dtype=int)
    
    def site_percolation(self, defect_prob: float) -> Tuple[np.ndarray, bool, float]:
        """
        Site percolation simulation.
        defect_prob: probability of a PE being defective
        
        Returns: (lattice, percolates, connected_fraction)
        """
        lattice = self.create_lattice()
        side = lattice.shape[0]
        
        # Mark defective sites
        defect_mask = np.random.random((side, side)) < defect_prob
        lattice[defect_mask] = -1  # Defective
        lattice[~defect_mask] = 1   # Functional
        
        # Check for percolation (path from top to bottom or left to right)
        functional = (lattice == 1)
        
        # Find connected components
        from scipy.ndimage import label
        labeled, n_components = label(functional)
        
        if n_components == 0:
            return lattice, False, 0.0
            
        # Largest component
        component_sizes = np.bincount(labeled.ravel())[1:]
        largest_fraction = np.max(component_sizes) / np.sum(functional)
        
        # Check percolation (component touches both edges)
        percolates = False
        for comp_id in range(1, n_components + 1):
            component = (labeled == comp_id)
            if (np.any(component[0, :]) and np.any(component[-1, :])) or \
               (np.any(component[:, 0]) and np.any(component[:, -1])):
                percolates = True
                break
                
        return lattice, percolates, largest_fraction
    
    def find_critical_threshold(self, n_trials: int = 100) -> float:
        """
        Find critical percolation threshold p_c.
        For 2D square lattice, p_c ≈ 0.5927 (site percolation)
        """
        probs = np.linspace(0.3, 0.8, 50)
        percolation_probs = []
        
        for p in probs:
            percolates_count = 0
            for _ in range(n_trials):
                _, percolates, _ = self.site_percolation(p)
                if percolates:
                    percolates_count += 1
            percolation_probs.append(percolates_count / n_trials)
            
        # Find threshold where probability crosses 0.5
        percolation_probs = np.array(percolation_probs)
        idx = np.argmin(np.abs(percolation_probs - 0.5))
        
        return probs[idx]
    
    def analyze_yield(self, defect_prob: float, n_simulations: int = 1000) -> Dict:
        """
        Comprehensive yield analysis.
        """
        results = {
            'percolates': [],
            'connected_fractions': [],
            'functional_pes': [],
            'largest_cluster_sizes': []
        }
        
        for _ in range(n_simulations):
            lattice, percolates, fraction = self.site_percolation(defect_prob)
            results['percolates'].append(percolates)
            results['connected_fractions'].append(fraction)
            results['functional_pes'].append(np.sum(lattice == 1))
            
            # Largest cluster
            functional = (lattice == 1)
            from scipy.ndimage import label
            labeled, n_comp = label(functional)
            if n_comp > 0:
                results['largest_cluster_sizes'].append(np.max(np.bincount(labeled.ravel())[1:]))
            else:
                results['largest_cluster_sizes'].append(0)
                
        return {
            'percolation_probability': np.mean(results['percolates']),
            'avg_connected_fraction': np.mean(results['connected_fractions']),
            'avg_functional_pes': np.mean(results['functional_pes']),
            'expected_yield': np.mean(np.array(results['connected_fractions']) > 0.5),
            'largest_cluster_mean': np.mean(results['largest_cluster_sizes']),
            'largest_cluster_std': np.std(results['largest_cluster_sizes'])
        }
    
    def design_redundancy(self, required_pes: int = 1024, target_yield: float = 0.95) -> Dict:
        """
        Design redundancy scheme based on percolation analysis.
        """
        # Calculate required extra PEs for target yield
        for extra_pes in [0, 64, 128, 256, 512]:
            total_pes = required_pes + extra_pes
            defect_rate = 0.01  # Assume 1% defect rate
            
            # Effective defect probability
            effective_yield = (1 - defect_rate) ** total_pes
            
            # Percolation-adjusted yield
            lattice, _, connected_frac = self.site_percolation(defect_rate)
            adjusted_yield = effective_yield * connected_frac
            
            if adjusted_yield >= target_yield:
                return {
                    'required_pes': required_pes,
                    'redundant_pes': extra_pes,
                    'total_pes': total_pes,
                    'achieved_yield': adjusted_yield,
                    'efficiency': required_pes / total_pes
                }
                
        return {
            'required_pes': required_pes,
            'redundant_pes': 512,
            'total_pes': required_pes + 512,
            'achieved_yield': adjusted_yield,
            'efficiency': required_pes / (required_pes +  512),
            'note': 'Could not achieve target yield with reasonable redundancy'
        }
    
    def plot_percolation_phase_diagram(self, save_path: str = None):
        """Plot percolation probability vs defect probability."""
        probs = np.linspace(0.0, 0.8, 40)
        n_trials = 50
        
        percolation_probs = []
        connected_fracs = []
        
        for p in probs:
            percolates_count = 0
            fracs = []
            for _ in range(n_trials):
                _, percolates, frac = self.site_percolation(p)
                if percolates:
                    percolates_count += 1
                fracs.append(frac)
            percolation_probs.append(percolates_count / n_trials)
            connected_fracs.append(np.mean(fracs))
            
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Percolation probability
        ax = axes[0]
        ax.plot(probs, percolation_probs, 'b-', linewidth=2)
        ax.axvline(x=0.5927, color='r', linestyle='--', label='p_c ≈ 0.593')
        ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
        ax.set_xlabel('Defect Probability')
        ax.set_ylabel('Percolation Probability')
        ax.set_title('Percolation Phase Transition')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Connected fraction
        ax = axes[1]
        ax.plot(probs, connected_fracs, 'g-', linewidth=2)
        ax.axvline(x=0.5927, color='r', linestyle='--', label='p_c ≈ 0.593')
        ax.set_xlabel('Defect Probability')
        ax.set_ylabel('Connected Fraction')
        ax.set_title('Functional PE Fraction')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 4: CELLULAR AUTOMATA FOR THERMAL MANAGEMENT
# ============================================================================

class ThermalCellularAutomaton:
    """
    Model heat propagation using cellular automata.
    
    State variables:
    - Temperature (discrete levels)
    - Activity (PE utilization)
    
    Rules:
    - Heat diffusion between neighbors
    - Heat generation from computation
    - Heat dissipation to environment
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (32, 32)):
        self.grid_size = grid_size
        self.n_states = 16  # Temperature levels (0-15)
        self.temperature = np.zeros(grid_size, dtype=int)
        self.activity = np.zeros(grid_size, dtype=float)
        self.time_history = []
        
        # Physical parameters (normalized)
        self.diffusion_rate = 0.125  # Heat spread rate
        self.generation_rate = 2.0   # Heat from activity
        self.dissipation_rate = 0.1  # Heat loss to ambient
        self.max_temp = 15           # Maximum temperature state
        self.critical_temp = 12      # Throttling threshold
        
    def set_activity_pattern(self, pattern: str = 'uniform'):
        """Set PE activity pattern."""
        if pattern == 'uniform':
            self.activity = np.ones(self.grid_size) * 0.5
        elif pattern == 'hotspot':
            self.activity = np.ones(self.grid_size) * 0.2
            center = (self.grid_size[0] // 2, self.grid_size[1] // 2)
            self.activity[center[0]-4:center[0]+4, center[1]-4:center[1]+4] = 0.9
        elif pattern == 'gradient':
            x = np.linspace(0, 1, self.grid_size[1])
            y = np.linspace(0, 1, self.grid_size[0])
            X, Y = np.meshgrid(x, y)
            self.activity = X * Y
        elif pattern == 'stripes':
            self.activity = np.zeros(self.grid_size)
            for i in range(0, self.grid_size[0], 4):
                self.activity[i:i+2, :] = 0.8
        elif pattern == 'random':
            self.activity = np.random.random(self.grid_size)
            
    def get_neighbors(self, i: int, j: int) -> List[Tuple[int, int]]:
        """Get valid neighbor coordinates (von Neumann neighborhood)."""
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.grid_size[0] and 0 <= nj < self.grid_size[1]:
                neighbors.append((ni, nj))
        return neighbors
    
    def apply_rules(self, temp: int, neighbor_temps: List[int], 
                   activity: float) -> int:
        """
        Apply cellular automaton rules for temperature update.
        """
        # Rule 1: Heat diffusion (average of neighbors)
        if neighbor_temps:
            avg_neighbor = sum(neighbor_temps) / len(neighbor_temps)
            diffusion = int(self.diffusion_rate * (avg_neighbor - temp))
        else:
            diffusion = 0
            
        # Rule 2: Heat generation from activity
        generation = int(self.generation_rate * activity)
        
        # Rule 3: Heat dissipation
        dissipation = int(self.dissipation_rate * temp)
        
        # Update temperature
        new_temp = temp + diffusion + generation - dissipation
        
        # Clamp to valid range
        return max(0, min(self.max_temp, new_temp))
    
    def step(self) -> float:
        """
        Execute one CA time step.
        Returns average temperature.
        """
        new_temp = np.zeros_like(self.temperature, dtype=int)
        
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                neighbors = self.get_neighbors(i, j)
                neighbor_temps = [self.temperature[ni, nj] for ni, nj in neighbors]
                new_temp[i, j] = self.apply_rules(
                    self.temperature[i, j],
                    neighbor_temps,
                    self.activity[i, j]
                )
                
        self.temperature = new_temp
        avg_temp = np.mean(self.temperature)
        self.time_history.append(avg_temp)
        return avg_temp
    
    def run_simulation(self, n_steps: int = 100) -> Dict:
        """Run thermal simulation."""
        self.time_history = []
        max_temps = []
        hotspot_counts = []
        
        for _ in range(n_steps):
            self.step()
            max_temps.append(np.max(self.temperature))
            hotspot_counts.append(np.sum(self.temperature > self.critical_temp))
            
        return {
            'final_avg_temp': self.time_history[-1],
            'final_max_temp': max_temps[-1],
            'max_temp_reached': max(max_temps),
            'hotspot_fraction': hotspot_counts[-1] / np.prod(self.grid_size),
            'steady_state': np.std(self.time_history[-10:]) < 0.1
        }
    
    def throttling_strategy(self) -> np.ndarray:
        """
        Determine throttling based on temperature.
        Returns activity multipliers (0-1).
        """
        throttling = np.ones_like(self.temperature, dtype=float)
        
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                temp = self.temperature[i, j]
                if temp >= self.critical_temp:
                    # Exponential throttling
                    excess = temp - self.critical_temp
                    throttling[i, j] = np.exp(-0.5 * excess)
                    
        return throttling
    
    def predict_thermal_emergency(self, horizon: int = 10) -> Dict:
        """Predict future thermal state."""
        predictions = []
        temp_copy = self.temperature.copy()
        
        for _ in range(horizon):
            self.step()
            predictions.append({
                'avg_temp': np.mean(self.temperature),
                'max_temp': np.max(self.temperature),
                'hotspots': np.sum(self.temperature > self.critical_temp)
            })
            
        self.temperature = temp_copy
        
        return {
            'predictions': predictions,
            'emergency_imminent': any(p['max_temp'] >= self.max_temp - 1 for p in predictions),
            'critical_step': next((i for i, p in enumerate(predictions) 
                                  if p['max_temp'] >= self.critical_temp + 2), -1)
        }
    
    def plot_thermal_evolution(self, save_path: str = None):
        """Visualize thermal state evolution."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Initial state
        self.set_activity_pattern('hotspot')
        self.temperature = np.zeros(self.grid_size, dtype=int)
        
        snapshots = [0, 10, 30, 50, 80, 100]
        snapshot_temps = []
        
        for step in range(max(snapshots) + 1):
            self.step()
            if step in snapshots:
                snapshot_temps.append(self.temperature.copy())
                
        for idx, (step, temp) in enumerate(zip(snapshots, snapshot_temps)):
            ax = axes[idx // 3, idx % 3]
            im = ax.imshow(temp, cmap='hot', vmin=0, vmax=self.max_temp)
            ax.set_title(f'Step {step}')
            ax.set_xlabel('PE X')
            ax.set_ylabel('PE Y')
            plt.colorbar(im, ax=ax, label='Temperature')
            
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 5: GAME THEORY FOR RESOURCE ALLOCATION
# ============================================================================

class ResourceAllocationGame:
    """
    Game-theoretic model of PE competition for memory bandwidth.
    
    Players: Processing Elements (PEs)
    Strategy: Memory request timing
    Payoff: Effective bandwidth achieved
    
    Key concepts:
    - Nash equilibrium
    - Mechanism design for fair allocation
    - Congestion game
    """
    
    def __init__(self, n_players: int = 16, total_bandwidth: float = 100.0):
        self.n_players = n_players
        self.total_bandwidth = total_bandwidth
        self.strategies = np.zeros(n_players)  # Request intensity (0-1)
        self.utilities = np.zeros(n_players)
        self.history = []
        
        # Memory architecture
        self.n_memory_banks = 4
        self.bank_bandwidth = total_bandwidth / self.n_memory_banks
        
        # PE to bank mapping
        self.bank_assignment = np.random.randint(0, self.n_memory_banks, n_players)
        
    def calculate_utility(self, strategies: np.ndarray) -> np.ndarray:
        """
        Calculate utility for each player given strategies.
        Utility = bandwidth_achieved - latency_cost - contention_cost
        """
        utilities = np.zeros(self.n_players)
        
        for bank in range(self.n_memory_banks):
            # PEs assigned to this bank
            mask = self.bank_assignment == bank
            bank_demand = np.sum(strategies[mask])
            
            if bank_demand > 0:
                # Bandwidth allocation (proportional fair)
                for i in np.where(mask)[0]:
                    share = strategies[i] / bank_demand
                    bandwidth = share * self.bank_bandwidth
                    
                    # Utility from bandwidth (diminishing returns)
                    utility_bandwidth = np.sqrt(bandwidth)
                    
                    # Latency cost (increases with congestion)
                    latency_cost = 0.1 * bank_demand ** 2
                    
                    # Contention cost
                    contention_cost = 0.05 * (bank_demand - 1) ** 2
                    
                    utilities[i] = utility_bandwidth - latency_cost - contention_cost
                    
        return utilities
    
    def best_response(self, player: int, others_strategies: np.ndarray) -> float:
        """Find best response strategy for a player."""
        best_utility = -np.inf
        best_strategy = 0.5
        
        for s in np.linspace(0, 1, 21):
            strategies = others_strategies.copy()
            strategies[player] = s
            utility = self.calculate_utility(strategies)[player]
            
            if utility > best_utility:
                best_utility = utility
                best_strategy = s
                
        return best_strategy
    
    def find_nash_equilibrium(self, max_iterations: int = 1000, 
                             convergence_threshold: float = 1e-4) -> Dict:
        """
        Find Nash equilibrium using iterated best response.
        """
        self.strategies = np.random.random(self.n_players) * 0.5 + 0.25
        self.history = [self.strategies.copy()]
        
        for iteration in range(max_iterations):
            old_strategies = self.strategies.copy()
            
            # Random order best response
            order = np.random.permutation(self.n_players)
            for player in order:
                self.strategies[player] = self.best_response(player, self.strategies)
                
            self.history.append(self.strategies.copy())
            
            # Check convergence
            diff = np.max(np.abs(self.strategies - old_strategies))
            if diff < convergence_threshold:
                break
                
        self.utilities = self.calculate_utility(self.strategies)
        
        return {
            'nash_strategies': self.strategies.copy(),
            'nash_utilities': self.utilities.copy(),
            'iterations': iteration + 1,
            'converged': diff < convergence_threshold,
            'total_bandwidth_used': np.sum(self.strategies) * self.total_bandwidth / self.n_players,
            'fairness': np.std(self.utilities) / np.mean(self.utilities) if np.mean(self.utilities) > 0 else 0
        }
    
    def mechanism_design(self) -> Dict:
        """
        Design mechanism for fair resource allocation.
        VCG-like mechanism with bandwidth guarantees.
        """
        # Guaranteed minimum bandwidth per PE
        guaranteed_bw = self.total_bandwidth / self.n_players / 2
        
        # Bonus bandwidth pool
        bonus_pool = self.total_bandwidth / 2
        
        # Allocation mechanism
        allocation = np.ones(self.n_players) * guaranteed_bw
        
        # Competitive allocation of bonus
        requests = np.random.random(self.n_players)  # Requested extra
        total_requests = np.sum(requests)
        
        if total_requests > 0:
            bonus_allocation = bonus_pool * requests / total_requests
            allocation += bonus_allocation
            
        # Compute social welfare
        welfare = np.sum(np.sqrt(allocation))  # Square root utility
        
        # VCG payments (simplified)
        payments = np.zeros(self.n_players)
        for i in range(self.n_players):
            # Welfare without player i
            others_allocation = allocation.copy()
            others_allocation[i] = 0
            welfare_without = np.sum(np.sqrt(others_allocation[others_allocation > 0]))
            payments[i] = welfare - welfare_without + np.sqrt(allocation[i])
            
        return {
            'allocation': allocation,
            'guaranteed_bandwidth': guaranteed_bw,
            'bonus_pool': bonus_pool,
            'payments': payments,
            'social_welfare': welfare,
            'price_of_anarchy': self._compute_price_of_anarchy()
        }
    
    def _compute_price_of_anarchy(self) -> float:
        """
        Compute Price of Anarchy: ratio of optimal to equilibrium welfare.
        """
        # Optimal: equal distribution
        optimal_strategies = np.ones(self.n_players) * 0.5
        optimal_utility = np.sum(self.calculate_utility(optimal_strategies))
        
        # Nash equilibrium utility
        nash_utility = np.sum(self.utilities)
        
        if nash_utility > 0:
            return optimal_utility / nash_utility
        return 1.0
    
    def cooperative_solution(self) -> Dict:
        """
        Find cooperative (socially optimal) solution.
        """
        from scipy.optimize import minimize
        
        def neg_welfare(strategies):
            return -np.sum(self.calculate_utility(strategies))
        
        # Constraints: strategies in [0, 1]
        bounds = [(0, 1)] * self.n_players
        
        # Initial guess
        x0 = np.ones(self.n_players) * 0.5
        
        result = minimize(neg_welfare, x0, bounds=bounds, method='L-BFGS-B')
        
        cooperative_strategies = result.x
        cooperative_utilities = self.calculate_utility(cooperative_strategies)
        
        return {
            'cooperative_strategies': cooperative_strategies,
            'cooperative_utilities': cooperative_utilities,
            'social_welfare': -result.fun,
            'total_utilization': np.sum(cooperative_strategies)
        }
    
    def plot_game_analysis(self, save_path: str = None):
        """Visualize game-theoretic analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Find Nash equilibrium
        nash_result = self.find_nash_equilibrium()
        
        # Strategy distribution
        ax = axes[0, 0]
        ax.hist(nash_result['nash_strategies'], bins=20, color='steelblue', 
               alpha=0.7, edgecolor='black')
        ax.set_xlabel('Strategy (Request Intensity)')
        ax.set_ylabel('Frequency')
        ax.set_title('Nash Equilibrium Strategies')
        
        # Utility distribution
        ax = axes[0, 1]
        ax.hist(nash_result['nash_utilities'], bins=20, color='coral',
               alpha=0.7, edgecolor='black')
        ax.set_xlabel('Utility')
        ax.set_ylabel('Frequency')
        ax.set_title('Nash Equilibrium Utilities')
        
        # Convergence history
        ax = axes[1, 0]
        history = np.array(self.history)
        for i in range(min(5, self.n_players)):
            ax.plot(history[:, i], alpha=0.7, label=f'PE {i}')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Strategy')
        ax.set_title('Strategy Convergence')
        ax.legend()
        
        # Comparison with cooperative
        ax = axes[1, 1]
        coop = self.cooperative_solution()
        x = np.arange(self.n_players)
        width = 0.35
        ax.bar(x - width/2, nash_result['nash_utilities'], width, 
              label='Nash', color='steelblue', alpha=0.7)
        ax.bar(x + width/2, coop['cooperative_utilities'], width,
              label='Cooperative', color='green', alpha=0.7)
        ax.set_xlabel('PE Index')
        ax.set_ylabel('Utility')
        ax.set_title('Nash vs Cooperative Utilities')
        ax.legend()
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 6: INFORMATION THERMODYNAMICS
# ============================================================================

class InformationThermodynamics:
    """
    Analyze information-theoretic bounds on energy consumption.
    
    Key concepts:
    - Landauer's principle: E ≥ kT ln(2) per bit erased
    - Maxwell's demon and information erasure
    - Szilard engine analysis
    """
    
    def __init__(self, temperature: float = 300.0):
        self.temperature = temperature  # Kelvin
        self.k_B = 1.38e-23  # Boltzmann constant (J/K)
        self.landauer_limit = self.k_B * temperature * np.log(2)
        
    def landauer_energy(self, n_bits: int) -> float:
        """
        Minimum energy required to erase n bits (Landauer's principle).
        """
        return n_bits * self.landauer_limit
    
    def szilard_engine_analysis(self, n_bits: int = 1024) -> Dict:
        """
        Analyze Szilard engine for inference operations.
        
        In a Szilard engine, information is used to extract work.
        For inference, we analyze the reverse: work to process information.
        """
        # Theoretical maximum work extractable per bit
        work_per_bit = self.k_B * self.temperature * np.log(2)
        
        # For inference, we need to:
        # 1. Erase previous state (Landauer cost)
        # 2. Compute new state (can be thermodynamically reversible)
        
        erase_cost = self.landauer_energy(n_bits)
        max_extractable = n_bits * work_per_bit
        
        # Net energy for inference cycle
        # In practice: much higher due to irreversible operations
        
        return {
            'bits_processed': n_bits,
            'landauer_erase_cost_J': erase_cost,
            'landauer_erase_cost_eV': erase_cost / 1.6e-19,
            'max_work_extractable_J': max_extractable,
            'theoretical_efficiency': max_extractable / (erase_cost + 1e-30),
            'temperature_K': self.temperature
        }
    
    def inference_energy_analysis(self, model_params: Dict) -> Dict:
        """
        Analyze energy bounds for neural network inference.
        """
        n_weights = model_params.get('n_weights', 1_000_000)
        n_activations = model_params.get('n_activations', 1024)
        precision_bits = model_params.get('precision', 8)
        operations = model_params.get('operations', 1e9)
        
        # Information content
        weight_bits = n_weights * precision_bits
        activation_bits = n_activations * precision_bits * 32  # Assuming 32 layers
        
        # Minimum energy for weight loading (one-time)
        weight_energy = self.landauer_energy(weight_bits)
        
        # Energy for activation computation per inference
        activation_energy = self.landauer_energy(activation_bits)
        
        # Total thermodynamic minimum
        total_minimum = weight_energy + activation_energy
        
        # Practical energy (assuming 1pJ per operation)
        practical_energy = operations * 1e-12
        
        return {
            'weight_information_bits': weight_bits,
            'activation_information_bits': activation_bits,
            'minimum_energy_J': total_minimum,
            'minimum_energy_pJ': total_minimum * 1e12,
            'practical_energy_J': practical_energy,
            'practical_energy_pJ': practical_energy * 1e12,
            'efficiency_gap': practical_energy / total_minimum,
            'landauer_limit_per_op_eV': self.landauer_limit / 1.6e-19,
            'theoretical_lower_bound_achieved': practical_energy < total_minimum * 1000
        }
    
    def maxwell_demon_memory(self, n_measurements: int = 1024) -> Dict:
        """
        Model memory as Maxwell's demon.
        
        The demon measures and stores information, but must eventually
        erase it, paying the Landauer cost.
        """
        # Information gathered per measurement (assuming binary)
        info_per_measurement = 1  # bit
        total_info = n_measurements * info_per_measurement
        
        # Energy cost of erasure
        erasure_cost = self.landauer_energy(total_info)
        
        # Energy that could be extracted (if used optimally)
        extractable = self.k_B * self.temperature * total_info * np.log(2)
        
        # Memory entropy increase
        entropy_increase = total_info * self.k_B * np.log(2)
        
        return {
            'n_measurements': n_measurements,
            'information_bits': total_info,
            'erasure_cost_J': erasure_cost,
            'potential_work_J': extractable,
            'entropy_increase_J_K': entropy_increase / self.temperature,
            'information_battery_capacity': total_info  # bits can store energy
        }
    
    def reversible_computation_potential(self) -> Dict:
        """
        Analyze potential for reversible computation in inference.
        
        Reversible computation doesn't erase information, so can avoid
        Landauer limit (but requires perfect reversibility).
        """
        # Reversible gates (Fredkin, Toffoli) require:
        # 1. No information erasure
        # 2. Input reconstruction possible
        
        # For inference:
        # - Weight multiplication: can be reversible
        # - Activation function: generally irreversible (ReLU discards negatives)
        # - Max pooling: irreversible
        
        reversible_ops = {
            'multiplication': True,
            'addition': True,  # With carry preservation
            'activation': False,  # ReLU is irreversible
            'max_pooling': False,
            'softmax': False,
            'batch_norm': True  # If parameters stored
        }
        
        # Typical layer breakdown (percentage of ops)
        layer_ops = {
            'matmul': 0.70,
            'activation': 0.10,
            'pooling': 0.05,
            'normalization': 0.10,
            'other': 0.05
        }
        
        reversible_fraction = (
            layer_ops['matmul'] + 
            layer_ops['normalization'] * 0.5  # Partially reversible
        )
        
        return {
            'reversible_operations': reversible_ops,
            'layer_operation_fractions': layer_ops,
            'reversible_fraction': reversible_fraction,
            'energy_reduction_potential': reversible_fraction,  # Up to this fraction
            'challenges': [
                'Memory overhead for reversibility',
                'Circuit complexity increase',
                'Irreversible activation functions',
                'Numerical precision requirements'
            ]
        }
    
    def plot_thermodynamic_analysis(self, save_path: str = None):
        """Visualize thermodynamic analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Landauer limit vs temperature
        ax = axes[0, 0]
        temps = np.linspace(200, 500, 100)
        limits = [self.k_B * T * np.log(2) * 1e21 for T in temps]  # zJ
        ax.plot(temps, limits, 'b-', linewidth=2)
        ax.axvline(x=self.temperature, color='r', linestyle='--', 
                  label=f'Operating: {self.temperature}K')
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Landauer Limit (zJ/bit)')
        ax.set_title('Energy Bound vs Temperature')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Energy comparison
        ax = axes[0, 1]
        model_params = {'n_weights': 1_000_000, 'n_activations': 1024, 
                       'precision': 8, 'operations': 1e9}
        energy_analysis = self.inference_energy_analysis(model_params)
        
        categories = ['Landauer\nMinimum', 'Practical\nConsumption']
        values = [energy_analysis['minimum_energy_pJ'], 
                 energy_analysis['practical_energy_pJ']]
        colors = ['green', 'red']
        ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Energy (pJ)')
        ax.set_title('Energy: Theoretical vs Practical')
        ax.set_yscale('log')
        
        # Szilard engine analysis
        ax = axes[1, 0]
        bit_counts = [128, 256, 512, 1024, 2048]
        erase_costs = [self.landauer_energy(n) * 1e21 for n in bit_counts]
        ax.plot(bit_counts, erase_costs, 'go-', linewidth=2, markersize=8)
        ax.set_xlabel('Number of Bits')
        ax.set_ylabel('Erase Energy (zJ)')
        ax.set_title('Landauer Erasure Cost')
        ax.grid(True, alpha=0.3)
        
        # Reversible computation potential
        ax = axes[1, 1]
        reversible = self.reversible_computation_potential()
        labels = list(reversible['layer_operation_fractions'].keys())
        fractions = list(reversible['layer_operation_fractions'].values())
        colors = ['green' if reversible['reversible_operations'].get(
            k.replace('_', ' '), False) else 'red' for k in labels]
        ax.pie(fractions, labels=labels, colors=['green', 'red', 'red', 'yellow', 'gray'],
              autopct='%1.1f%%', startangle=90)
        ax.set_title('Operation Reversibility')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# COMPREHENSIVE ANALYSIS RUNNER
# ============================================================================

def run_full_analysis(output_dir: str = '/home/z/my-project/research'):
    """Run all complex systems analyses and save results."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("COMPLEX SYSTEMS ANALYSIS FOR MASK-LOCKED INFERENCE CHIP")
    print("=" * 60)
    
    results = {}
    
    # 1. Self-Organized Criticality
    print("\n[1/6] Self-Organized Criticality Analysis...")
    soc = NeuralActivationSOC(n_neurons=1024)
    soc.run_simulation(n_avalanches=5000, sigma=1.0)
    results['soc'] = soc.analyze_criticality()
    soc.plot_avalanche_distribution(f'{output_dir}/soc_avalanches.png')
    print(f"   Avalanche size exponent: {results['soc']['size_exponent']:.2f}")
    print(f"   Is critical: {results['soc']['is_critical']}")
    
    # 2. Network Science
    print("\n[2/6] Network Science Analysis...")
    network = ChipNetworkModel(n_pes=1024, topology='hybrid')
    results['network'] = network.compute_metrics()
    results['centrality'] = network.analyze_communication_centrality()
    network.plot_network(f'{output_dir}/network_topology.png')
    print(f"   Small-world index: {results['network']['small_world_index']:.2f}")
    print(f"   Clustering coefficient: {results['network']['clustering_coefficient']:.3f}")
    
    # 3. Percolation Theory
    print("\n[3/6] Percolation Theory Analysis...")
    percolation = PercolationYieldModel(n_pes=1024)
    results['percolation'] = percolation.analyze_yield(defect_prob=0.1)
    results['redundancy'] = percolation.design_redundancy(required_pes=1024)
    percolation.plot_percolation_phase_diagram(f'{output_dir}/percolation_phase.png')
    print(f"   Percolation probability at 10% defects: {results['percolation']['percolation_probability']:.2%}")
    print(f"   Redundancy needed for 95% yield: {results['redundancy']['redundant_pes']} PEs")
    
    # 4. Cellular Automata Thermal
    print("\n[4/6] Thermal Cellular Automata Analysis...")
    thermal = ThermalCellularAutomaton(grid_size=(32, 32))
    thermal.set_activity_pattern('hotspot')
    results['thermal'] = thermal.run_simulation(n_steps=100)
    thermal.plot_thermal_evolution(f'{output_dir}/thermal_evolution.png')
    print(f"   Final max temperature: {results['thermal']['final_max_temp']}")
    print(f"   Hotspot fraction: {results['thermal']['hotspot_fraction']:.2%}")
    
    # 5. Game Theory
    print("\n[5/6] Game Theory Analysis...")
    game = ResourceAllocationGame(n_players=16, total_bandwidth=100.0)
    results['game_theory'] = game.find_nash_equilibrium()
    results['mechanism'] = game.mechanism_design()
    game.plot_game_analysis(f'{output_dir}/game_theory.png')
    print(f"   Nash equilibrium fairness: {results['game_theory']['fairness']:.3f}")
    print(f"   Price of anarchy: {results['mechanism']['price_of_anarchy']:.2f}")
    
    # 6. Information Thermodynamics
    print("\n[6/6] Information Thermodynamics Analysis...")
    thermo = InformationThermodynamics(temperature=300.0)
    results['thermodynamics'] = thermo.inference_energy_analysis({
        'n_weights': 1_000_000,
        'n_activations': 1024,
        'precision': 8,
        'operations': 1e9
    })
    results['szilard'] = thermo.szilard_engine_analysis(n_bits=1024)
    thermo.plot_thermodynamic_analysis(f'{output_dir}/thermodynamics.png')
    print(f"   Landauer minimum energy: {results['thermodynamics']['minimum_energy_pJ']:.2e} pJ")
    print(f"   Efficiency gap: {results['thermodynamics']['efficiency_gap']:.2e}x")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    results = run_full_analysis()
