#!/usr/bin/env python3
"""
Weight-Logic Algebra Simulation Suite
=====================================

Comprehensive Python simulation for verifying the mathematical theorems
developed in the Cycle 1 Weight-Logic Algebra research.

This module provides:
1. Ternary matrix decomposition analysis
2. Spectral analysis of weight matrices
3. Graph-based scheduling simulation
4. Information flow analysis
5. Error propagation simulation
6. Layer arrangement optimization

Author: Mathematical Research Agent
Version: 1.0
Date: January 2025
"""

import numpy as np
from scipy import linalg
from scipy.stats import entropy
import networkx as nx
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


# ==============================================================================
# Part I: Ternary Weight Matrix Decomposition
# ==============================================================================

class TernaryMatrixDecomposition:
    """
    Analysis and decomposition of ternary weight matrices.
    
    Implements Theorems 1.1-1.6 from the research document.
    """
    
    def __init__(self, m: int, n: int, sparsity: float = 0.66):
        """
        Initialize ternary matrix analyzer.
        
        Args:
            m: Number of rows
            n: Number of columns
            sparsity: Probability of non-zero weights
        """
        self.m = m
        self.n = n
        self.sparsity = sparsity
    
    def generate_bitnet_matrix(self, seed: int = 42) -> np.ndarray:
        """
        Generate BitNet-style ternary weight matrix.
        
        The distribution matches BitNet b1.58 empirical weights:
        - P(w = -1) ≈ 0.32
        - P(w = 0) ≈ 0.36
        - P(w = +1) ≈ 0.32
        """
        np.random.seed(seed)
        probs = [0.32, 0.36, 0.32]
        W = np.random.choice([-1, 0, 1], size=(self.m, self.n), p=probs)
        return W
    
    def decompose_pn(self, W: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Decompose ternary matrix into P - N (Theorem 1.1).
        
        W = P - N where P, N are binary matrices with disjoint support.
        
        Args:
            W: Ternary weight matrix
            
        Returns:
            P: Binary matrix of positive weights
            N: Binary matrix of negative weights
        """
        P = (W == 1).astype(np.int8)
        N = (W == -1).astype(np.int8)
        return P, N
    
    def verify_decomposition(self, W: np.ndarray, P: np.ndarray, N: np.ndarray) -> Dict:
        """Verify the P-N decomposition satisfies all properties."""
        reconstruction = P - N
        
        return {
            'reconstruction_correct': np.allclose(W, reconstruction),
            'support_orthogonal': np.sum(P * N) == 0,
            'sparsity_preserved': np.sum(P) + np.sum(N) == np.sum(W != 0),
            'minimality': np.all(P + N <= 1)
        }
    
    def ifairy_decompose(self, W: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Decompose iFairy complex matrix (Theorem 1.6).
        
        W = P - N + i(Q - R)
        
        Args:
            W: Complex weight matrix with values in {±1, ±i}
            
        Returns:
            P, N, Q, R: Binary matrices for +1, -1, +i, -i weights
        """
        P = (W == 1).astype(np.int8)
        N = (W == -1).astype(np.int8)
        Q = (W == 1j).astype(np.int8)
        R = (W == -1j).astype(np.int8)
        return P, N, Q, R
    
    def compute_accumulator_bits(self, n: int, activation_bits: int = 8) -> int:
        """
        Compute optimal accumulator size (Theorem 1.5).
        
        For INT8 activations: max_sum = n × 127
        """
        max_val = 2 ** (activation_bits - 1) - 1
        max_sum = n * max_val
        bits = int(np.ceil(np.log2(max_sum + 1)))
        return bits


# ==============================================================================
# Part II: Spectral Analysis
# ==============================================================================

class SpectralAnalyzer:
    """
    Spectral analysis of ternary weight matrices.
    
    Implements Theorems 3.1-3.7 from the research document.
    """
    
    def __init__(self, matrix: np.ndarray):
        """Initialize with a weight matrix."""
        self.W = matrix
        self.m, self.n = matrix.shape
    
    def compute_spectrum(self) -> Dict:
        """Compute eigenvalue distribution."""
        # For rectangular matrices, use W @ W.T
        if self.m != self.n:
            eigenvalues = linalg.eigvals(self.W @ self.W.T / self.n)
            eigenvalues = eigenvalues.real
        else:
            eigenvalues = linalg.eigvals(self.W)
            eigenvalues = eigenvalues.real
        
        return {
            'eigenvalues': eigenvalues,
            'spectral_radius': np.max(np.abs(eigenvalues)),
            'spectral_gap': self._compute_spectral_gap(eigenvalues),
            'condition_number': self._compute_condition_number(eigenvalues)
        }
    
    def _compute_spectral_gap(self, eigenvalues: np.ndarray) -> float:
        """Compute spectral gap λ_1 / λ_2."""
        sorted_eigs = np.sort(np.abs(eigenvalues))[::-1]
        if len(sorted_eigs) > 1 and sorted_eigs[1] > 0:
            return sorted_eigs[0] / sorted_eigs[1]
        return np.inf
    
    def _compute_condition_number(self, eigenvalues: np.ndarray) -> float:
        """Compute condition number κ = |λ_max| / |λ_min|."""
        abs_eigs = np.abs(eigenvalues)
        if np.min(abs_eigs) > 0:
            return np.max(abs_eigs) / np.min(abs_eigs)
        return np.inf
    
    def compare_to_wigner(self) -> Dict:
        """
        Compare empirical spectrum to Wigner semicircle law (Theorem 3.1).
        
        Theoretical radius: 2√(p × n) where p = sparsity
        """
        p = np.mean(self.W != 0)
        n = min(self.m, self.n)
        
        theoretical_radius = 2 * np.sqrt(p * n)
        
        spectrum = self.compute_spectrum()
        empirical_radius = spectrum['spectral_radius']
        
        return {
            'theoretical_radius': theoretical_radius,
            'empirical_radius': empirical_radius,
            'ratio': empirical_radius / theoretical_radius,
            'sparsity': p
        }
    
    def compare_to_marchenko_pastur(self) -> Dict:
        """
        Compare singular values to Marchenko-Pastur distribution (Theorem 3.3).
        """
        s = linalg.svdvals(self.W)
        
        c = self.m / self.n  # Aspect ratio
        p = np.mean(self.W != 0)
        sigma_sq = np.var(self.W[self.W != 0]) if np.any(self.W != 0) else 1
        
        # Marchenko-Pastur bounds
        if c >= 1:
            a = sigma_sq * (1 - np.sqrt(1/c))**2
            b = sigma_sq * (1 + np.sqrt(1/c))**2
        else:
            a = sigma_sq * (1 - np.sqrt(c))**2
            b = sigma_sq * (1 + np.sqrt(c))**2
        
        return {
            'singular_values': s,
            'mp_bounds': (a, b),
            'aspect_ratio': c,
            'theoretical_spread': b - a,
            'empirical_spread': np.max(s) - np.min(s)
        }
    
    def compute_effective_rank(self) -> float:
        """
        Compute effective rank (Definition 3.3).
        
        r_eff = (∑σ_i)² / ∑σ_i²
        """
        s = linalg.svdvals(self.W)
        s_sum = np.sum(s)
        s_sq_sum = np.sum(s ** 2)
        
        if s_sq_sum > 0:
            return (s_sum ** 2) / s_sq_sum
        return 0
    
    def analyze_quantization_effect(self, W_fp16: np.ndarray) -> Dict:
        """
        Analyze effect of quantization on spectrum (Theorem 3.4).
        """
        spectrum_fp16 = SpectralAnalyzer(W_fp16).compute_spectrum()
        spectrum_ternary = self.compute_spectrum()
        
        eigs_fp16 = spectrum_fp16['eigenvalues']
        eigs_ternary = spectrum_ternary['eigenvalues']
        
        # Align lengths
        min_len = min(len(eigs_fp16), len(eigs_ternary))
        spectral_drift = np.linalg.norm(eigs_fp16[:min_len] - eigs_ternary[:min_len])
        
        # Frobenius norm bound
        frobenius_bound = np.linalg.norm(W_fp16 - self.W, 'fro')
        
        return {
            'spectral_drift': spectral_drift,
            'frobenius_bound': frobenius_bound,
            'bound_satisfied': spectral_drift <= frobenius_bound,
            'spectral_radius_change': spectrum_ternary['spectral_radius'] - spectrum_fp16['spectral_radius']
        }


# ==============================================================================
# Part III: Graph-Based Inference Analysis
# ==============================================================================

class InferenceDAG:
    """
    Analyze inference computation as a Directed Acyclic Graph.
    
    Implements Theorems 2.1-2.7 from the research document.
    """
    
    def __init__(self, num_layers: int = 24, hidden_dim: int = 2048, 
                 num_heads: int = 32, ffn_mult: int = 4):
        """
        Initialize transformer DAG.
        
        Args:
            num_layers: Number of transformer layers
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
            ffn_mult: FFN expansion factor
        """
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.ffn_dim = hidden_dim * ffn_mult
        self.G = nx.DiGraph()
        self._build_dag()
    
    def _build_dag(self):
        """Build the computation DAG for transformer inference."""
        node_id = 0
        self.layer_nodes = {}
        
        for layer in range(self.num_layers):
            layer_nodes = {}
            
            # Attention: Q, K, V projections (parallel)
            for proj in ['Q', 'K', 'V']:
                for head in range(self.num_heads):
                    self.G.add_node(node_id,
                                   layer=layer,
                                   type=f'attn_{proj}',
                                   head=head,
                                   ops=self.hidden_dim * self.head_dim)
                    node_id += 1
            
            # Attention score computation
            self.G.add_node(node_id,
                          layer=layer,
                          type='attn_score',
                          ops=self.num_heads * 128 * 128)  # seq_len^2 approximation
            attn_score_node = node_id
            layer_nodes['attn_score'] = attn_score_node
            node_id += 1
            
            # Attention output projection
            self.G.add_node(node_id,
                          layer=layer,
                          type='attn_out',
                          ops=self.hidden_dim * self.hidden_dim)
            attn_out_node = node_id
            layer_nodes['attn_out'] = attn_out_node
            node_id += 1
            
            # FFN up projection
            self.G.add_node(node_id,
                          layer=layer,
                          type='ffn_up',
                          ops=self.hidden_dim * self.ffn_dim)
            ffn_up_node = node_id
            layer_nodes['ffn_up'] = ffn_up_node
            node_id += 1
            
            # FFN down projection
            self.G.add_node(node_id,
                          layer=layer,
                          type='ffn_down',
                          ops=self.ffn_dim * self.hidden_dim)
            ffn_down_node = node_id
            layer_nodes['ffn_down'] = ffn_down_node
            node_id += 1
            
            # Add edges within layer
            self.G.add_edge(attn_score_node, attn_out_node)
            self.G.add_edge(ffn_up_node, ffn_down_node)
            
            self.layer_nodes[layer] = layer_nodes
            
            # Add edges between layers
            if layer > 0:
                prev_layer = self.layer_nodes[layer - 1]
                # Residual connection flow
                self.G.add_edge(prev_layer['ffn_down'], layer_nodes['attn_score'])
                self.G.add_edge(prev_layer['ffn_down'], ffn_up_node)
    
    def critical_path_analysis(self) -> Dict:
        """
        Find critical path through DAG (Definition 2.2, Theorem 2.2).
        """
        topo_order = list(nx.topological_sort(self.G))
        
        # Longest path computation
        dist = {node: 0 for node in self.G.nodes()}
        pred = {node: None for node in self.G.nodes()}
        
        for node in topo_order:
            ops = self.G.nodes[node].get('ops', 1)
            for successor in self.G.successors(node):
                if dist[node] + ops > dist[successor]:
                    dist[successor] = dist[node] + ops
                    pred[successor] = node
        
        # Reconstruct path
        end_node = max(dist, key=dist.get)
        path = []
        current = end_node
        while current is not None:
            path.append((current, self.G.nodes[current]))
            current = pred[current]
        path.reverse()
        
        return {
            'critical_path': path,
            'critical_path_length': dist[end_node],
            'total_ops': sum(self.G.nodes[n].get('ops', 1) for n in self.G.nodes())
        }
    
    def parallelism_analysis(self) -> Dict:
        """Analyze available parallelism (Definition 2.3)."""
        # Compute levels (depth from start)
        levels = {}
        for node in nx.topological_sort(self.G):
            level = 0
            for pred in self.G.predecessors(node):
                level = max(level, levels.get(pred, 0) + 1)
            levels[node] = level
        
        # Nodes per level
        level_nodes = defaultdict(list)
        for node, level in levels.items():
            level_nodes[level].append(node)
        
        parallelism = {level: len(nodes) for level, nodes in level_nodes.items()}
        
        return {
            'max_parallelism': max(parallelism.values()) if parallelism else 0,
            'avg_parallelism': np.mean(list(parallelism.values())) if parallelism else 0,
            'num_levels': len(level_nodes),
            'parallelism_profile': parallelism
        }
    
    def systolic_schedule(self, array_size: int = 32) -> List[Dict]:
        """Generate systolic array schedule (Theorem 2.5)."""
        schedule = []
        cycle = 0
        dim = self.hidden_dim
        
        for layer in range(self.num_layers):
            # Matrix operations per layer
            cycles_per_matmul = (dim // array_size) ** 2 + dim // array_size
            
            # Attention (Q, K, V parallel, then score, then output)
            attn_cycles = 4 * cycles_per_matmul
            
            # FFN (up, down)
            ffn_cycles = 2 * cycles_per_matmul * 4  # 4x expansion
            
            schedule.append({
                'layer': layer,
                'start_cycle': cycle,
                'attn_cycles': attn_cycles,
                'ffn_cycles': ffn_cycles,
                'end_cycle': cycle + attn_cycles + ffn_cycles,
                'array_utilization': 0.66  # Ternary sparsity
            })
            cycle += attn_cycles + ffn_cycles
        
        return schedule


# ==============================================================================
# Part IV: Layer Arrangement Optimization
# ==============================================================================

class LayerArrangementOptimizer:
    """
    Optimize physical layer arrangement for wire length minimization.
    
    Implements Theorems 4.1-4.6 from the research document.
    """
    
    def __init__(self, num_layers: int = 24, data_widths: Optional[List[int]] = None):
        """
        Initialize layer arrangement optimizer.
        
        Args:
            num_layers: Number of layers to arrange
            data_widths: Data width for each connection (bits)
        """
        self.num_layers = num_layers
        if data_widths is None:
            # Default: uniform data widths
            self.data_widths = [2048] * (num_layers - 1)
        else:
            self.data_widths = data_widths
    
    def compute_wire_length(self, permutation: List[int], 
                           positions: Optional[np.ndarray] = None) -> float:
        """
        Compute total wire length for a permutation (Theorem 4.1).
        
        Args:
            permutation: Layer ordering
            positions: Optional 2D positions for each layer
            
        Returns:
            Total wire length
        """
        if positions is None:
            # Linear arrangement: position = index
            positions = np.arange(self.num_layers).reshape(-1, 1)
        
        total_length = 0
        for i in range(self.num_layers - 1):
            # Find positions of consecutive layers in permutation
            pos_i = positions[permutation[i]]
            pos_j = positions[permutation[i + 1]]
            
            # Manhattan distance
            distance = np.abs(pos_i - pos_j).sum()
            
            # Weight by data width
            total_length += distance * self.data_widths[i]
        
        return total_length
    
    def simulated_annealing(self, initial_order: Optional[List[int]] = None,
                           T0: float = 1000.0, alpha: float = 0.95,
                           iterations: int = 10000) -> Dict:
        """
        Simulated annealing for layer arrangement (Algorithm 4.1).
        
        Args:
            initial_order: Initial permutation
            T0: Initial temperature
            alpha: Cooling rate
            iterations: Number of iterations
            
        Returns:
            Optimization results
        """
        if initial_order is None:
            initial_order = list(range(self.num_layers))
        
        current_order = initial_order.copy()
        current_cost = self.compute_wire_length(current_order)
        
        best_order = current_order.copy()
        best_cost = current_cost
        
        history = [current_cost]
        T = T0
        
        np.random.seed(42)
        
        for k in range(iterations):
            # Generate neighbor by swap
            new_order = current_order.copy()
            i, j = np.random.choice(self.num_layers, 2, replace=False)
            new_order[i], new_order[j] = new_order[j], new_order[i]
            
            new_cost = self.compute_wire_length(new_order)
            delta = new_cost - current_cost
            
            # Metropolis criterion
            if delta < 0 or np.random.random() < np.exp(-delta / T):
                current_order = new_order
                current_cost = new_cost
                
                if current_cost < best_cost:
                    best_order = current_order.copy()
                    best_cost = current_cost
            
            history.append(current_cost)
            T *= alpha
        
        return {
            'optimal_order': best_order,
            'optimal_cost': best_cost,
            'initial_cost': self.compute_wire_length(initial_order),
            'improvement': (self.compute_wire_length(initial_order) - best_cost) / self.compute_wire_length(initial_order),
            'cost_history': history
        }
    
    def genetic_algorithm(self, pop_size: int = 100, generations: int = 500,
                         mutation_rate: float = 0.1) -> Dict:
        """
        Genetic algorithm for layer arrangement (Algorithm 4.2).
        """
        np.random.seed(42)
        
        def random_permutation():
            perm = list(range(self.num_layers))
            np.random.shuffle(perm)
            return perm
        
        def order_crossover(p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
            """Order crossover (OX) for permutations."""
            n = len(p1)
            a, b = sorted(np.random.choice(n, 2, replace=False))
            
            c1 = [None] * n
            c2 = [None] * n
            
            # Copy segment
            c1[a:b] = p1[a:b]
            c2[a:b] = p2[a:b]
            
            # Fill remaining
            for parent, child in [(p2, c1), (p1, c2)]:
                idx = b % n
                for i in range(b, n + a):
                    pos = i % n
                    if parent[idx] not in child:
                        child[pos] = parent[idx]
                    idx = (idx + 1) % n
            
            return c1, c2
        
        def swap_mutation(perm: List[int]) -> List[int]:
            new_perm = perm.copy()
            i, j = np.random.choice(len(perm), 2, replace=False)
            new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
            return new_perm
        
        # Initialize population
        population = [random_permutation() for _ in range(pop_size)]
        fitness = [1 / self.compute_wire_length(p) for p in population]
        
        best_ever = population[np.argmax(fitness)]
        best_ever_cost = 1 / max(fitness)
        
        for gen in range(generations):
            # Tournament selection
            new_population = []
            for _ in range(pop_size // 2):
                tournament = np.random.choice(pop_size, 3, replace=False)
                winner = tournament[np.argmax([fitness[i] for i in tournament])]
                new_population.append(population[winner].copy())
            
            # Crossover
            offspring = []
            for i in range(0, len(new_population) - 1, 2):
                c1, c2 = order_crossover(new_population[i], new_population[i + 1])
                offspring.extend([c1, c2])
            
            # Mutation
            for i in range(len(offspring)):
                if np.random.random() < mutation_rate:
                    offspring[i] = swap_mutation(offspring[i])
            
            # Elitism
            offspring[0] = best_ever.copy()
            
            population = offspring[:pop_size]
            fitness = [1 / self.compute_wire_length(p) for p in population]
            
            current_best_idx = np.argmax(fitness)
            current_best_cost = 1 / fitness[current_best_idx]
            
            if current_best_cost < best_ever_cost:
                best_ever = population[current_best_idx].copy()
                best_ever_cost = current_best_cost
        
        return {
            'optimal_order': best_ever,
            'optimal_cost': best_ever_cost,
            'initial_cost': self.compute_wire_length(list(range(self.num_layers))),
            'improvement': (self.compute_wire_length(list(range(self.num_layers))) - best_ever_cost) / self.compute_wire_length(list(range(self.num_layers)))
        }


# ==============================================================================
# Part V: Information Flow Analysis
# ==============================================================================

class InformationFlowAnalyzer:
    """
    Analyze information flow through neural network layers.
    
    Implements Theorems 5.1-5.8 from the research document.
    """
    
    def __init__(self):
        pass
    
    def estimate_entropy(self, X: np.ndarray, bins: int = 50) -> float:
        """Estimate differential entropy of activation distribution."""
        hist, _ = np.histogram(X.flatten(), bins=bins, density=True)
        hist = hist + 1e-10
        hist = hist / hist.sum()
        h = -np.sum(hist * np.log2(hist))
        return h
    
    def estimate_mutual_information(self, X: np.ndarray, Y: np.ndarray, 
                                   bins: int = 50) -> float:
        """
        Estimate mutual information I(X; Y).
        
        I(X; Y) = H(X) + H(Y) - H(X, Y)
        """
        # Marginal entropies
        h_x = self.estimate_entropy(X, bins)
        h_y = self.estimate_entropy(Y, bins)
        
        # Joint entropy
        n_samples = min(X.flatten().shape[0], Y.flatten().shape[0], 10000)
        joint = np.column_stack([
            X.flatten()[:n_samples],
            Y.flatten()[:n_samples]
        ])
        
        hist_2d, _, _ = np.histogram2d(joint[:, 0], joint[:, 1], bins=bins)
        hist_2d = hist_2d + 1e-10
        hist_2d = hist_2d / hist_2d.sum()
        h_xy = -np.sum(hist_2d * np.log2(hist_2d))
        
        mi = h_x + h_y - h_xy
        return max(0, mi)
    
    def information_bottleneck_analysis(self, activations: List[np.ndarray]) -> List[Dict]:
        """
        Analyze information bottleneck across layers (Theorem 5.3).
        """
        results = []
        
        for i in range(len(activations) - 1):
            X_l = activations[i]
            X_lp1 = activations[i + 1]
            
            mi = self.estimate_mutual_information(X_l, X_lp1)
            h = self.estimate_entropy(X_lp1)
            
            results.append({
                'layer': i,
                'mi_consecutive': mi,
                'entropy': h,
                'information_efficiency': mi / h if h > 0 else 0
            })
        
        return results
    
    def optimal_bit_allocation(self, sensitivities: List[float], 
                               total_budget: float,
                               min_bits: float = 1.58) -> np.ndarray:
        """
        Water-filling algorithm for bit allocation (Theorem 5.5).
        
        Args:
            sensitivities: Layer sensitivity values
            total_budget: Total bits available
            min_bits: Minimum bits per layer (ternary = 1.58)
            
        Returns:
            Bit allocation per layer
        """
        n_layers = len(sensitivities)
        
        # Weight by inverse sensitivity
        weights = 1 / (np.array(sensitivities) + 1e-6)
        weights = weights / weights.sum()
        
        # Initial allocation
        allocation = weights * total_budget
        
        # Enforce minimum
        allocation = np.maximum(allocation, min_bits)
        
        # Redistribute if over budget
        max_iterations = 100
        for _ in range(max_iterations):
            if allocation.sum() <= total_budget:
                break
            
            excess = allocation.sum() - total_budget
            sorted_idx = np.argsort(sensitivities)[::-1]  # Least sensitive first
            
            for idx in sorted_idx:
                if allocation[idx] > min_bits:
                    reduction = min(allocation[idx] - min_bits, excess)
                    allocation[idx] -= reduction
                    excess -= reduction
                    if excess <= 0:
                        break
        
        return allocation


# ==============================================================================
# Part VI: Error Propagation Analysis
# ==============================================================================

class ErrorPropagationAnalyzer:
    """
    Analyze quantization error propagation through networks.
    
    Implements Theorems 6.1-6.9 from the research document.
    """
    
    def __init__(self):
        pass
    
    def quantize_to_ternary(self, W: np.ndarray, gamma: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Quantize weights to ternary (Definition 6.1).
        
        Args:
            W: Full-precision weight matrix
            gamma: Quantization threshold
            
        Returns:
            W_quant: Quantized weights
            E: Quantization error
        """
        if gamma is None:
            gamma = np.mean(np.abs(W))
        
        W_quant = np.zeros_like(W)
        W_quant[W > gamma / 2] = 1
        W_quant[W < -gamma / 2] = -1
        
        E = W - W_quant
        
        return W_quant, E
    
    def analyze_error_statistics(self, E: np.ndarray) -> Dict:
        """Compute error statistics (Theorem 6.1)."""
        return {
            'mean': np.mean(E),
            'variance': np.var(E),
            'max': np.max(np.abs(E)),
            'frobenius_norm': np.linalg.norm(E, 'fro'),
            'spectral_norm': np.linalg.norm(E, 2)
        }
    
    def simulate_propagation(self, W_sequence: List[np.ndarray], 
                            x: np.ndarray,
                            num_trials: int = 10) -> Dict:
        """
        Simulate error propagation through network (Theorems 6.2-6.4).
        """
        num_layers = len(W_sequence)
        
        # True forward pass
        y_true = x.copy()
        for W in W_sequence:
            y_true = y_true @ W
            y_true = (y_true - y_true.mean()) / (y_true.std() + 1e-6)  # LayerNorm
        
        all_errors = []
        
        for trial in range(num_trials):
            np.random.seed(trial)
            
            # Quantized forward pass
            y_quant = x.copy()
            layer_errors = []
            
            for W in W_sequence:
                W_q, E = self.quantize_to_ternary(W)
                y_quant = y_quant @ W_q
                y_quant = (y_quant - y_quant.mean()) / (y_quant.std() + 1e-6)
                
                error = np.linalg.norm(y_true - y_quant) / (np.linalg.norm(y_true) + 1e-6)
                layer_errors.append(error)
            
            all_errors.append(layer_errors)
        
        all_errors = np.array(all_errors)
        
        return {
            'mean_layer_errors': np.mean(all_errors, axis=0),
            'std_layer_errors': np.std(all_errors, axis=0),
            'mean_output_error': np.mean(all_errors[:, -1]),
            'worst_case_error': np.max(all_errors[:, -1])
        }
    
    def theoretical_bound(self, W_sequence: List[np.ndarray], 
                         E_sequence: List[np.ndarray]) -> float:
        """Compute theoretical error bound (Theorem 6.3)."""
        bound = 0
        num_layers = len(W_sequence)
        
        for l in range(num_layers):
            contribution = np.linalg.norm(E_sequence[l], 2)
            for k in range(l + 1, num_layers):
                contribution *= np.linalg.norm(W_sequence[k], 2)
            bound += contribution
        
        return bound
    
    def layernorm_suppression(self, error_magnitude: float, 
                             activation_std: float) -> float:
        """
        Compute LayerNorm error suppression (Theorem 6.4).
        
        Suppression ≈ σ / √(σ² + e²) ≈ 1 - e²/(2σ²)
        """
        suppression = activation_std / np.sqrt(activation_std**2 + error_magnitude**2)
        return suppression


# ==============================================================================
# Main Simulation Runner
# ==============================================================================

def run_all_simulations():
    """Run all simulations and print results."""
    print("=" * 80)
    print("WEIGHT-LOGIC ALGEBRA SIMULATION RESULTS")
    print("=" * 80)
    
    # Part I: Ternary Matrix Decomposition
    print("\n" + "=" * 80)
    print("PART I: TERNARY MATRIX DECOMPOSITION")
    print("=" * 80)
    
    decomp = TernaryMatrixDecomposition(m=512, n=512)
    W = decomp.generate_bitnet_matrix()
    P, N = decomp.decompose_pn(W)
    verification = decomp.verify_decomposition(W, P, N)
    
    print(f"\nGenerated BitNet-style matrix: {W.shape}")
    print(f"Sparsity: {np.mean(W != 0):.2%}")
    print(f"Distribution: P(-1)={np.mean(W==-1):.2%}, P(0)={np.mean(W==0):.2%}, P(+1)={np.mean(W==1):.2%}")
    print(f"\nDecomposition verification:")
    for key, value in verification.items():
        print(f"  {key}: {value}")
    
    acc_bits = decomp.compute_accumulator_bits(4096)
    print(f"\nAccumulator bits for 4096 weights with INT8 activations: {acc_bits} bits")
    
    # Part II: Spectral Analysis
    print("\n" + "=" * 80)
    print("PART II: SPECTRAL ANALYSIS")
    print("=" * 80)
    
    spectral = SpectralAnalyzer(W)
    spectrum = spectral.compute_spectrum()
    wigner = spectral.compare_to_wigner()
    mp = spectral.compare_to_marchenko_pastur()
    r_eff = spectral.compute_effective_rank()
    
    print(f"\nSpectral analysis:")
    print(f"  Spectral radius: {spectrum['spectral_radius']:.2f}")
    print(f"  Spectral gap: {spectrum['spectral_gap']:.2f}")
    print(f"  Condition number: {spectrum['condition_number']:.2f}")
    print(f"  Effective rank: {r_eff:.1f} ({r_eff/512*100:.1f}% of full rank)")
    
    print(f"\nRandom matrix theory comparison:")
    print(f"  Theoretical Wigner radius: {wigner['theoretical_radius']:.2f}")
    print(f"  Empirical radius: {wigner['empirical_radius']:.2f}")
    print(f"  Ratio: {wigner['ratio']:.2f}")
    
    # Part III: Graph-Based Analysis
    print("\n" + "=" * 80)
    print("PART III: GRAPH-BASED INFERENCE ANALYSIS")
    print("=" * 80)
    
    dag = InferenceDAG(num_layers=24, hidden_dim=2048, num_heads=32)
    critical = dag.critical_path_analysis()
    parallelism = dag.parallelism_analysis()
    schedule = dag.systolic_schedule(array_size=32)
    
    print(f"\nDAG statistics:")
    print(f"  Nodes: {dag.G.number_of_nodes()}")
    print(f"  Edges: {dag.G.number_of_edges()}")
    print(f"  Critical path length: {critical['critical_path_length']:,} operations")
    print(f"  Total operations: {critical['total_ops']:,}")
    
    print(f"\nParallelism analysis:")
    print(f"  Maximum parallelism: {parallelism['max_parallelism']}")
    print(f"  Average parallelism: {parallelism['avg_parallelism']:.1f}")
    print(f"  Number of levels: {parallelism['num_levels']}")
    
    print(f"\nSystolic schedule (32×32 array):")
    print(f"  Total cycles: {schedule[-1]['end_cycle']:,}")
    print(f"  Array utilization: {schedule[0]['array_utilization']:.0%}")
    
    # Part IV: Layer Arrangement
    print("\n" + "=" * 80)
    print("PART IV: LAYER ARRANGEMENT OPTIMIZATION")
    print("=" * 80)
    
    optimizer = LayerArrangementOptimizer(num_layers=24)
    
    # Simulated annealing
    sa_result = optimizer.simulated_annealing(iterations=5000)
    print(f"\nSimulated Annealing:")
    print(f"  Initial cost: {sa_result['initial_cost']:,.0f}")
    print(f"  Optimal cost: {sa_result['optimal_cost']:,.0f}")
    print(f"  Improvement: {sa_result['improvement']:.1%}")
    
    # Part V: Information Flow
    print("\n" + "=" * 80)
    print("PART V: INFORMATION FLOW ANALYSIS")
    print("=" * 80)
    
    # Simulate activations
    np.random.seed(42)
    activations = [np.random.randn(100, 2048)]
    for i in range(23):
        W_temp = np.random.randn(2048, 2048) * 0.02
        activations.append(np.tanh(activations[-1] @ W_temp))
    
    info_analyzer = InformationFlowAnalyzer()
    ib_results = info_analyzer.information_bottleneck_analysis(activations[:6])
    
    print(f"\nInformation Bottleneck Analysis (first 6 layers):")
    for result in ib_results:
        print(f"  Layer {result['layer']}: MI={result['mi_consecutive']:.3f}, "
              f"H={result['entropy']:.3f}, eff={result['information_efficiency']:.3f}")
    
    sensitivities = [1.0 / (1 + i * 0.1) for i in range(24)]
    bit_alloc = info_analyzer.optimal_bit_allocation(sensitivities, 24 * 8)
    print(f"\nOptimal bit allocation (avg 8 bits per layer):")
    print(f"  Min: {bit_alloc.min():.2f}, Max: {bit_alloc.max():.2f}, Mean: {bit_alloc.mean():.2f}")
    
    # Part VI: Error Propagation
    print("\n" + "=" * 80)
    print("PART VI: ERROR PROPAGATION ANALYSIS")
    print("=" * 80)
    
    error_analyzer = ErrorPropagationAnalyzer()
    
    # Simulate weight sequence
    W_sequence = [np.random.randn(2048, 2048) * 0.02 for _ in range(24)]
    x = np.random.randn(1, 2048)
    
    error_results = error_analyzer.simulate_propagation(W_sequence, x, num_trials=5)
    
    print(f"\nError propagation simulation (5 trials):")
    print(f"  Mean output error: {error_results['mean_output_error']*100:.2f}%")
    print(f"  Worst case error: {error_results['worst_case_error']*100:.2f}%")
    print(f"  Layer-wise error growth:")
    for i, (mean, std) in enumerate(zip(error_results['mean_layer_errors'][::6],
                                         error_results['std_layer_errors'][::6])):
        print(f"    Layer {i*6}: {mean*100:.2f}% ± {std*100:.2f}%")
    
    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_all_simulations()
