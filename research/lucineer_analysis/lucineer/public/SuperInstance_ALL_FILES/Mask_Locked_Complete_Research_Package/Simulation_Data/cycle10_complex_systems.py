#!/usr/bin/env python3
"""
Cycle 10: Complex Systems Chip Emergence Analysis
===================================================

This module implements advanced complex systems analysis for the Mask-Locked 
Inference Chip, focusing on emergent behavior from local interactions:

1. Self-Organized Criticality:
   - Sandpile model for avalanche dynamics
   - Critical branching processes
   - Power-law distribution analysis

2. Emergence Analysis:
   - Local rules → global inference behavior
   - Collective phenomena in PE arrays
   - Synchronization patterns
   - Phase synchronization across chip

3. Nonlinear Dynamics:
   - Bifurcation analysis
   - Chaos vs stability in inference
   - Attractor dynamics
   - Limit cycles in recurrent processing

4. Multi-Scale Analysis:
   - Micro: transistor switching
   - Meso: PE array dynamics
   - Macro: chip-level inference
   - Cross-scale coupling

Author: Complex Systems Research Team
Date: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize, curve_fit
from scipy.signal import find_peaks, welch
from scipy.ndimage import label
from collections import defaultdict
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SECTION 1: SELF-ORGANIZED CRITICALITY - SANDPILE MODEL
# ============================================================================

class SandpileModel:
    """
    Sandpile model for avalanche dynamics in inference.
    
    Maps to chip behavior:
    - Grains = Input tokens
    - Toppling = PE activation and data propagation
    - Avalanches = Inference cascades through layers
    
    The system self-organizes to criticality where:
    - Avalanches have power-law size distribution
    - No characteristic scale exists
    - Optimal information transmission
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (32, 32), threshold: int = 4):
        self.grid_size = grid_size
        self.threshold = threshold
        self.grid = np.zeros(grid_size, dtype=int)
        self.avalanche_sizes = []
        self.avalanche_durations = []
        self.avalanche_areas = []
        self.total_grains = 0
        self.dissipated_grains = 0
        
    def add_grain(self, position: Tuple[int, int] = None) -> bool:
        """Add a grain to the system at specified or random position."""
        if position is None:
            position = (np.random.randint(0, self.grid_size[0]),
                       np.random.randint(0, self.grid_size[1]))
        self.grid[position] += 1
        self.total_grains += 1
        return self.grid[position] >= self.threshold
    
    def topple(self, i: int, j: int) -> List[Tuple[int, int]]:
        """Topple an unstable site, distributing grains to neighbors."""
        neighbors = []
        grains = self.grid[i, j]
        self.grid[i, j] = 0
        
        # Distribute grains to von Neumann neighbors
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.grid_size[0] and 0 <= nj < self.grid_size[1]:
                self.grid[ni, nj] += 1
                neighbors.append((ni, nj))
            else:
                # Grains leaving the system (dissipation)
                self.dissipated_grains += 1
                
        return neighbors
    
    def relax(self) -> Tuple[int, int, int]:
        """
        Relax the system until stable.
        Returns: (size, duration, area) of avalanche
        """
        size = 0  # Total topplings
        duration = 0  # Time steps
        area = set()  # Unique sites toppled
        
        # Find initial unstable sites
        unstable = list(zip(*np.where(self.grid >= self.threshold)))
        
        while unstable:
            new_unstable = set()
            for site in unstable:
                i, j = site
                if self.grid[i, j] >= self.threshold:
                    neighbors = self.topple(i, j)
                    size += 1
                    area.add((i, j))
                    new_unstable.update(neighbors)
            
            unstable = [s for s in new_unstable if self.grid[s] >= self.threshold]
            duration += 1
            
        return size, duration, len(area)
    
    def run_simulation(self, n_grains: int = 100000, transient: int = 10000) -> Dict:
        """Run sandpile simulation."""
        self.grid = np.zeros(self.grid_size, dtype=int)
        self.avalanche_sizes = []
        self.avalanche_durations = []
        self.avalanche_areas = []
        self.total_grains = 0
        self.dissipated_grains = 0
        
        # Transient period to reach critical state
        for _ in range(transient):
            self.add_grain()
            self.relax()
            
        # Measurement period
        for _ in range(n_grains):
            self.add_grain()
            size, duration, area = self.relax()
            if size > 0:
                self.avalanche_sizes.append(size)
                self.avalanche_durations.append(duration)
                self.avalanche_areas.append(area)
                
        return self.analyze_critical_state()
    
    def analyze_critical_state(self) -> Dict:
        """Analyze critical state signatures."""
        sizes = np.array(self.avalanche_sizes)
        durations = np.array(self.avalanche_durations)
        areas = np.array(self.avalanche_areas)
        
        results = {
            'n_avalanches': len(sizes),
            'avg_size': np.mean(sizes) if len(sizes) > 0 else 0,
            'max_size': np.max(sizes) if len(sizes) > 0 else 0,
            'dissipation_rate': self.dissipated_grains / max(self.total_grains, 1),
        }
        
        if len(sizes) > 100:
            # Power-law fit for sizes
            alpha_s, xmin_s, ks_s = self._fit_power_law(sizes)
            results['size_exponent'] = alpha_s
            results['size_xmin'] = xmin_s
            results['size_ks_stat'] = ks_s
            results['is_critical_size'] = 1.0 < alpha_s < 2.5
            
            # Power-law fit for durations
            alpha_d, xmin_d, ks_d = self._fit_power_law(durations)
            results['duration_exponent'] = alpha_d
            
            # Size-duration scaling: S ~ T^γ
            valid = (sizes > 1) & (durations > 1)
            if np.sum(valid) > 10:
                gamma, _, r, _, _ = stats.linregress(
                    np.log(durations[valid]), np.log(sizes[valid]))
                results['scaling_exponent'] = gamma
                results['scaling_r_squared'] = r ** 2
                
        return results
    
    def _fit_power_law(self, data: np.ndarray) -> Tuple[float, float, float]:
        """Fit power-law distribution using MLE."""
        data = data[data > 0]
        if len(data) < 10:
            return 2.0, 1.0, 1.0
            
        xmin = max(1, np.percentile(data, 5))
        data = data[data >= xmin]
        n = len(data)
        
        if n == 0:
            return 2.0, xmin, 1.0
            
        alpha = 1 + n / np.sum(np.log(data / xmin))
        
        # KS statistic
        sorted_data = np.sort(data)
        cdf_emp = np.arange(1, n + 1) / n
        cdf_theory = 1 - (sorted_data / xmin) ** (-alpha + 1)
        ks_stat = np.max(np.abs(cdf_emp - cdf_theory))
        
        return alpha, xmin, ks_stat
    
    def plot_avalanche_analysis(self, save_path: str = None):
        """Generate comprehensive avalanche analysis plots."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        sizes = np.array(self.avalanche_sizes)
        durations = np.array(self.avalanche_durations)
        
        # 1. Size distribution
        ax = axes[0, 0]
        if len(sizes) > 0:
            bins = np.logspace(0, np.log10(max(sizes) + 1), 40)
            ax.hist(sizes, bins=bins, density=True, alpha=0.7, color='steelblue')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Avalanche Size')
            ax.set_ylabel('P(S)')
            ax.set_title('Avalanche Size Distribution')
            
            # Fit line
            alpha, xmin, _ = self._fit_power_law(sizes)
            x_fit = np.logspace(np.log10(xmin), np.log10(max(sizes)), 100)
            y_fit = (alpha - 1) * xmin**(alpha - 1) * x_fit**(-alpha)
            ax.plot(x_fit, y_fit, 'r--', linewidth=2, label=f'α = {alpha:.2f}')
            ax.legend()
            
        # 2. Duration distribution
        ax = axes[0, 1]
        if len(durations) > 0:
            bins = np.logspace(0, np.log10(max(durations) + 1), 30)
            ax.hist(durations, bins=bins, density=True, alpha=0.7, color='coral')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Avalanche Duration')
            ax.set_ylabel('P(T)')
            ax.set_title('Avalanche Duration Distribution')
            
        # 3. Size vs Duration
        ax = axes[0, 2]
        valid = (sizes > 1) & (durations > 1)
        if np.sum(valid) > 0:
            ax.scatter(durations[valid], sizes[valid], alpha=0.1, s=1, color='green')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Duration')
            ax.set_ylabel('Size')
            ax.set_title('Size-Duration Scaling')
            
            # Fit line
            gamma, intercept, r, _, _ = stats.linregress(
                np.log(durations[valid]), np.log(sizes[valid]))
            x_fit = np.logspace(0, np.log10(max(durations)), 50)
            y_fit = np.exp(intercept) * x_fit ** gamma
            ax.plot(x_fit, y_fit, 'r--', linewidth=2, label=f'γ = {gamma:.2f}')
            ax.legend()
            
        # 4. Grid state visualization
        ax = axes[1, 0]
        im = ax.imshow(self.grid, cmap='YlOrRd', vmin=0, vmax=self.threshold)
        ax.set_title('Current Grid State')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.colorbar(im, ax=ax, label='Grains')
        
        # 5. Time series of avalanche sizes
        ax = axes[1, 1]
        if len(sizes) > 0:
            ax.plot(sizes[:min(5000, len(sizes))], alpha=0.5, linewidth=0.5)
            ax.set_xlabel('Avalanche Index')
            ax.set_ylabel('Size')
            ax.set_title('Avalanche Time Series')
            
        # 6. Area distribution
        ax = axes[1, 2]
        areas = np.array(self.avalanche_areas)
        if len(areas) > 0:
            bins = np.logspace(0, np.log10(max(areas) + 1), 30)
            ax.hist(areas, bins=bins, density=True, alpha=0.7, color='purple')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Avalanche Area')
            ax.set_ylabel('P(A)')
            ax.set_title('Avalanche Area Distribution')
            
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


class CriticalBranchingProcess:
    """
    Critical branching process for inference cascade modeling.
    
    Each active PE can activate downstream PEs.
    Critical state: each activation produces on average 1 offspring.
    """
    
    def __init__(self, n_pes: int = 1024, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
        self.n_pes = n_pes
        self.cascade_sizes = []
        self.cascade_durations = []
        
    def simulate_cascade(self, sigma: float = 1.0, max_steps: int = 1000,
                        topology: str = 'small_world') -> Tuple[int, int, np.ndarray]:
        """
        Simulate a single cascade.
        
        Args:
            sigma: Branching ratio (1.0 = critical)
            max_steps: Maximum cascade duration
            topology: Network topology ('random', 'small_world', 'grid')
            
        Returns:
            (size, duration, active_trajectory)
        """
        # Start from random seed
        active = {np.random.randint(0, self.n_pes)}
        size = 0
        duration = 0
        trajectory = []
        
        while active and duration < max_steps:
            trajectory.append(len(active))
            new_active = set()
            
            for pe in active:
                size += 1
                # Number of offspring
                n_offspring = np.random.poisson(sigma)
                
                for _ in range(n_offspring):
                    if topology == 'random':
                        neighbor = np.random.randint(0, self.n_pes)
                    elif topology == 'grid':
                        # 2D grid neighbors
                        side = int(np.sqrt(self.n_pes))
                        i, j = pe // side, pe % side
                        di, dj = np.random.choice([-1, 0, 1], 2)
                        ni, nj = (i + di) % side, (j + dj) % side
                        neighbor = ni * side + nj
                    elif topology == 'small_world':
                        # Mix of local and long-range
                        if np.random.random() < 0.1:
                            neighbor = np.random.randint(0, self.n_pes)
                        else:
                            neighbor = (pe + np.random.choice([-1, 1])) % self.n_pes
                    new_active.add(neighbor)
                    
            active = new_active
            duration += 1
            
        return size, duration, np.array(trajectory)
    
    def run_simulation(self, n_cascades: int = 10000, sigma: float = 1.0) -> Dict:
        """Run multiple cascades and analyze statistics."""
        self.cascade_sizes = []
        self.cascade_durations = []
        all_trajectories = []
        
        for _ in range(n_cascades):
            size, duration, traj = self.simulate_cascade(sigma)
            self.cascade_sizes.append(size)
            self.cascade_durations.append(duration)
            if duration > 10:
                all_trajectories.append(traj)
                
        self.cascade_sizes = np.array(self.cascade_sizes)
        self.cascade_durations = np.array(self.cascade_durations)
        
        return self._analyze_results()
    
    def _analyze_results(self) -> Dict:
        """Analyze cascade statistics."""
        sizes = self.cascade_sizes[self.cascade_sizes > 0]
        durations = self.cascade_durations[self.cascade_durations > 0]
        
        if len(sizes) < 10:
            return {'error': 'Insufficient data'}
            
        # Power-law fits
        alpha_s, _, _ = self._fit_power_law(sizes)
        alpha_d, _, _ = self._fit_power_law(durations)
        
        # Scaling relation
        valid = (self.cascade_sizes > 1) & (self.cascade_durations > 1)
        if np.sum(valid) > 10:
            gamma, _, r, _, _ = stats.linregress(
                np.log(self.cascade_durations[valid]),
                np.log(self.cascade_sizes[valid]))
        else:
            gamma, r = 1.5, 0
            
        return {
            'size_exponent': alpha_s,
            'duration_exponent': alpha_d,
            'scaling_exponent': gamma,
            'r_squared': r ** 2,
            'is_critical': 1.5 < alpha_s < 2.5,
            'mean_size': np.mean(sizes),
            'survival_probability': np.mean(self.cascade_sizes > 0)
        }
    
    def _fit_power_law(self, data: np.ndarray) -> Tuple[float, float, float]:
        """Fit power-law distribution."""
        data = data[data > 1]
        if len(data) < 10:
            return 2.0, 1.0, 1.0
            
        xmin = np.percentile(data, 10)
        data = data[data >= xmin]
        n = len(data)
        
        alpha = 1 + n / np.sum(np.log(data / xmin))
        
        sorted_data = np.sort(data)
        cdf_emp = np.arange(1, n + 1) / n
        cdf_theory = 1 - (sorted_data / xmin) ** (-alpha + 1)
        ks_stat = np.max(np.abs(cdf_emp - cdf_theory))
        
        return alpha, xmin, ks_stat


# ============================================================================
# SECTION 2: EMERGENCE ANALYSIS
# ============================================================================

class EmergenceAnalyzer:
    """
    Analyze emergence: how local rules produce global behavior.
    
    Key concepts:
    - Local interactions → Global patterns
    - Collective computation
    - Information integration
    - Downward causation
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (32, 32)):
        self.grid_size = grid_size
        self.n_cells = grid_size[0] * grid_size[1]
        
    def game_of_life_inference(self, n_steps: int = 200,
                               initial_density: float = 0.3) -> Dict:
        """
        Model inference as cellular automaton (Game of Life variant).
        
        States:
        - 0: Inactive
        - 1: Active (processing)
        - 2: Refractory (recently active)
        """
        # Initialize grid
        grid = (np.random.random(self.grid_size) < initial_density).astype(int)
        
        history = [grid.copy()]
        active_counts = [np.sum(grid == 1)]
        cluster_counts = []
        
        for step in range(n_steps):
            new_grid = np.zeros_like(grid)
            
            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    # Count active neighbors
                    neighbors = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = (i + di) % self.grid_size[0], (j + dj) % self.grid_size[1]
                            if grid[ni, nj] == 1:
                                neighbors += 1
                    
                    # Inference rules (Game of Life variant)
                    if grid[i, j] == 1:
                        # Active cell: stay active if 2-3 neighbors
                        if 2 <= neighbors <= 3:
                            new_grid[i, j] = 1
                        else:
                            new_grid[i, j] = 2  # Refractory
                    elif grid[i, j] == 2:
                        # Refractory: become inactive
                        new_grid[i, j] = 0
                    else:
                        # Inactive: become active if exactly 3 neighbors
                        if neighbors == 3:
                            new_grid[i, j] = 1
                            
            grid = new_grid
            history.append(grid.copy())
            active_counts.append(np.sum(grid == 1))
            
            # Cluster analysis
            labeled, n_clusters = label(grid == 1)
            cluster_counts.append(n_clusters)
            
        return {
            'history': np.array(history),
            'active_counts': np.array(active_counts),
            'cluster_counts': np.array(cluster_counts),
            'steady_state_active': np.mean(active_counts[-50:]),
            'steady_state_clusters': np.mean(cluster_counts[-50:]),
            'oscillation_period': self._detect_period(active_counts)
        }
    
    def _detect_period(self, signal: np.ndarray) -> int:
        """Detect oscillation period in signal."""
        if len(signal) < 50:
            return 0
        # Use autocorrelation
        signal = signal - np.mean(signal)
        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find first peak after 0
        peaks, _ = find_peaks(autocorr)
        if len(peaks) > 1:
            return peaks[1]
        return 0
    
    def measure_emergence(self, local_rule: Callable, n_steps: int = 100) -> Dict:
        """
        Quantify emergence using integrated information.
        
        Φ = H(whole) - Σ H(parts)
        """
        # Simulate with local rules
        grid = np.random.random(self.grid_size) > 0.5
        
        whole_entropies = []
        part_entropies = []
        
        for _ in range(n_steps):
            # Apply local rule
            grid = local_rule(grid)
            
            # Whole system entropy
            whole_prob = np.mean(grid)
            if 0 < whole_prob < 1:
                whole_H = -whole_prob * np.log2(whole_prob) - (1 - whole_prob) * np.log2(1 - whole_prob)
            else:
                whole_H = 0
            whole_entropies.append(whole_H)
            
            # Part entropies (divide into quadrants)
            part_H_sum = 0
            for qi in range(2):
                for qj in range(2):
                    quadrant = grid[qi*self.grid_size[0]//2:(qi+1)*self.grid_size[0]//2,
                                   qj*self.grid_size[1]//2:(qj+1)*self.grid_size[1]//2]
                    q_prob = np.mean(quadrant)
                    if 0 < q_prob < 1:
                        part_H_sum += -q_prob * np.log2(q_prob) - (1 - q_prob) * np.log2(1 - q_prob)
            part_entropies.append(part_H_sum)
            
        # Integrated information
        phi = np.mean(whole_entropies) - np.mean(part_entropies) / 4
        
        return {
            'integrated_information': phi,
            'whole_entropy': np.mean(whole_entropies),
            'mean_part_entropy': np.mean(part_entropies) / 4,
            'emergence_strength': max(0, phi)
        }


class SynchronizationAnalyzer:
    """
    Analyze synchronization patterns across PE array.
    
    Types of synchronization:
    - In-phase: All PEs synchronized
    - Anti-phase: Alternating patterns
    - Clustered: Group synchronization
    - Chimera: Coexistence of sync and async
    """
    
    def __init__(self, n_pes: int = 1024):
        self.n_pes = n_pes
        
    def kuramoto_model(self, n_steps: int = 500, K: float = 1.5,
                      coupling_matrix: np.ndarray = None) -> Dict:
        """
        Kuramoto model for phase synchronization.
        
        dθᵢ/dt = ωᵢ + (K/N) Σ sin(θⱼ - θᵢ)
        """
        # Natural frequencies (slight variation)
        omega = np.random.normal(0, 0.1, self.n_pes)
        
        # Initial phases
        theta = np.random.uniform(0, 2 * np.pi, self.n_pes)
        
        # Coupling matrix (default: all-to-all)
        if coupling_matrix is None:
            coupling = np.ones((self.n_pes, self.n_pes)) / self.n_pes
        else:
            coupling = coupling_matrix
            
        dt = 0.1
        order_params = []
        phase_history = []
        
        for step in range(n_steps):
            # Compute order parameter
            r = np.abs(np.mean(np.exp(1j * theta)))
            order_params.append(r)
            
            if step % 10 == 0:
                phase_history.append(theta.copy())
            
            # Update phases
            for i in range(self.n_pes):
                interaction = np.sum(coupling[i] * np.sin(theta - theta[i]))
                theta[i] += (omega[i] + K * interaction) * dt
                theta[i] = theta[i] % (2 * np.pi)
                
        # Analyze synchronization
        final_order = order_params[-1]
        
        # Detect chimera state
        phase_var = np.std(theta)
        
        # Cluster detection
        phase_clusters = self._detect_phase_clusters(theta)
        
        return {
            'order_parameter_history': np.array(order_params),
            'final_order_parameter': final_order,
            'phase_history': np.array(phase_history),
            'synchronization_time': self._find_sync_time(order_params),
            'is_synchronized': final_order > 0.8,
            'is_chimera': 0.3 < final_order < 0.7 and phase_var > 1.0,
            'n_clusters': phase_clusters['n_clusters'],
            'cluster_sizes': phase_clusters['sizes'],
            'critical_coupling': self._estimate_critical_coupling(omega)
        }
    
    def _detect_phase_clusters(self, phases: np.ndarray) -> Dict:
        """Detect clusters of synchronized phases."""
        # Use hierarchical clustering on phase differences
        from scipy.cluster.hierarchy import fcluster, linkage
        
        # Phase differences
        phase_matrix = np.abs(np.subtract.outer(phases, phases))
        phase_matrix = np.minimum(phase_matrix, 2 * np.pi - phase_matrix)
        
        # Hierarchical clustering
        condensed = phase_matrix[np.triu_indices(self.n_pes, k=1)]
        linkage_matrix = linkage(condensed, method='average')
        clusters = fcluster(linkage_matrix, t=0.5, criterion='distance')
        
        unique, counts = np.unique(clusters, return_counts=True)
        
        return {
            'n_clusters': len(unique),
            'sizes': counts,
            'assignment': clusters
        }
    
    def _find_sync_time(self, order_params: np.ndarray, threshold: float = 0.7) -> int:
        """Find time to reach synchronization."""
        for i, r in enumerate(order_params):
            if r > threshold:
                return i
        return len(order_params)
    
    def _estimate_critical_coupling(self, omega: np.ndarray) -> float:
        """Estimate critical coupling for synchronization."""
        # K_c = 2 / (π * g(0)) for Gaussian distribution
        sigma = np.std(omega)
        if sigma > 0:
            return 2 / (np.pi * np.sqrt(2 * np.pi) * sigma)
        return 0
    
    def measure_phase_sync(self, phase_history: np.ndarray) -> np.ndarray:
        """
        Compute pairwise phase synchronization.
        
        Returns matrix of synchronization indices.
        """
        n_times, n_pes = phase_history.shape
        sync_matrix = np.zeros((n_pes, n_pes))
        
        for i in range(n_pes):
            for j in range(i + 1, n_pes):
                # Mean phase coherence
                phase_diff = phase_history[:, i] - phase_history[:, j]
                sync_matrix[i, j] = np.abs(np.mean(np.exp(1j * phase_diff)))
                sync_matrix[j, i] = sync_matrix[i, j]
                
        return sync_matrix


# ============================================================================
# SECTION 3: NONLINEAR DYNAMICS
# ============================================================================

class NonlinearDynamicsAnalyzer:
    """
    Analyze nonlinear dynamics in inference processing.
    
    Key concepts:
    - Bifurcation analysis
    - Chaos detection
    - Attractor identification
    - Limit cycles
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim  # System dimension (reduced PE state)
        
    def recurrent_network(self, n_steps: int = 1000, 
                         weight_scale: float = 1.0,
                         nonlinearity: str = 'tanh',
                         input_pattern: np.ndarray = None) -> Dict:
        """
        Simulate recurrent network dynamics.
        
        x(t+1) = f(W @ x(t) + input)
        """
        # Random weight matrix
        W = np.random.randn(self.dim, self.dim) * weight_scale / np.sqrt(self.dim)
        
        # Initial state
        x = np.random.randn(self.dim) * 0.1
        
        # Input
        if input_pattern is None:
            input_pattern = np.zeros(self.dim)
            
        # Nonlinearity
        if nonlinearity == 'tanh':
            f = np.tanh
        elif nonlinearity == 'relu':
            f = lambda z: np.maximum(0, z)
        elif nonlinearity == 'sigmoid':
            f = lambda z: 1 / (1 + np.exp(-z))
        else:
            f = np.tanh
            
        # Simulate
        trajectory = [x.copy()]
        for _ in range(n_steps):
            x = f(W @ x + input_pattern)
            trajectory.append(x.copy())
            
        trajectory = np.array(trajectory)
        
        # Analysis
        lyapunov = self._estimate_lyapunov(trajectory, W)
        attractor = self._find_attractor(trajectory)
        
        return {
            'trajectory': trajectory,
            'final_state': trajectory[-1],
            'lyapunov_exponent': lyapunov,
            'is_chaotic': lyapunov > 0,
            'attractor_type': attractor['type'],
            'attractor_center': attractor['center'],
            'converged': attractor['converged']
        }
    
    def _estimate_lyapunov(self, trajectory: np.ndarray, W: np.ndarray) -> float:
        """Estimate largest Lyapunov exponent."""
        # Use trajectory divergence method
        n = len(trajectory)
        if n < 100:
            return 0
            
        divergences = []
        for i in range(0, n - 50, 10):
            # Find nearest neighbor
            distances = np.linalg.norm(trajectory[i+1:i+50] - trajectory[i], axis=1)
            if len(distances) > 0 and np.min(distances) > 1e-10:
                initial_dist = distances[0]
                final_dist = distances[-1]
                if initial_dist > 1e-10:
                    divergences.append(np.log(final_dist / initial_dist))
                    
        if len(divergences) > 0:
            return np.mean(divergences) / 50
        return 0
    
    def _find_attractor(self, trajectory: np.ndarray) -> Dict:
        """Identify attractor type and properties."""
        n = len(trajectory)
        
        # Check for fixed point
        last_100 = trajectory[-100:]
        variance = np.var(last_100, axis=0)
        mean_var = np.mean(variance)
        
        if mean_var < 1e-6:
            return {
                'type': 'fixed_point',
                'center': np.mean(last_100, axis=0),
                'converged': True
            }
            
        # Check for limit cycle (periodic)
        autocorr = np.correlate(np.mean(trajectory[-200:], axis=1),
                               np.mean(trajectory[-200:], axis=1), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        peaks, _ = find_peaks(autocorr)
        if len(peaks) > 2:
            period = np.diff(peaks).mean() if len(peaks) > 1 else 0
            if period > 5:
                return {
                    'type': 'limit_cycle',
                    'period': period,
                    'center': np.mean(last_100, axis=0),
                    'converged': True
                }
                
        # Otherwise, strange attractor or chaotic
        return {
            'type': 'strange_attractor' if mean_var > 0.1 else 'transient',
            'center': np.mean(last_100, axis=0),
            'converged': mean_var < 0.1
        }
    
    def bifurcation_analysis(self, param_range: np.ndarray = None,
                            param_name: str = 'weight_scale') -> Dict:
        """
        Analyze bifurcations as parameter varies.
        """
        if param_range is None:
            param_range = np.linspace(0.5, 2.5, 50)
            
        final_states = []
        attractor_types = []
        
        for p in param_range:
            if param_name == 'weight_scale':
                result = self.recurrent_network(n_steps=500, weight_scale=p)
            else:
                result = self.recurrent_network(n_steps=500)
                
            final_states.append(result['final_state'])
            attractor_types.append(result['attractor_type'])
            
        # Detect bifurcations
        bifurcations = self._detect_bifurcations(final_states, param_range)
        
        return {
            'parameter_values': param_range,
            'final_states': np.array(final_states),
            'attractor_types': attractor_types,
            'bifurcation_points': bifurcations,
            'n_bifurcations': len(bifurcations)
        }
    
    def _detect_bifurcations(self, states: List[np.ndarray], 
                            params: np.ndarray) -> List[Dict]:
        """Detect bifurcation points from state changes."""
        bifurcations = []
        
        for i in range(1, len(states)):
            # Check for qualitative change
            dist = np.linalg.norm(states[i] - states[i-1])
            
            # Also check attractor type change
            state_var = np.var([states[max(0, i-j)] for j in range(min(10, i))], axis=0)
            prev_var = np.var([states[max(0, i-1-j)] for j in range(min(10, i-1))], axis=0)
            
            if np.mean(state_var) > 2 * np.mean(prev_var) + 0.1:
                bifurcations.append({
                    'parameter': params[i],
                    'index': i,
                    'type': 'saddle_node' if dist < 1 else 'pitchfork'
                })
                
        return bifurcations
    
    def phase_portrait(self, trajectory: np.ndarray, 
                       save_path: str = None) -> None:
        """Generate 2D phase portrait from trajectory."""
        # Project to 2D using PCA
        from sklearn.decomposition import PCA
        
        pca = PCA(n_components=2)
        projected = pca.fit_transform(trajectory)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Phase portrait
        ax = axes[0]
        ax.plot(projected[:, 0], projected[:, 1], alpha=0.5, linewidth=0.5)
        ax.scatter(projected[0, 0], projected[0, 1], c='green', s=100, marker='o', label='Start')
        ax.scatter(projected[-1, 0], projected[-1, 1], c='red', s=100, marker='*', label='End')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_title('Phase Portrait')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Time series of PC1
        ax = axes[1]
        ax.plot(projected[:, 0], alpha=0.7)
        ax.set_xlabel('Time Step')
        ax.set_ylabel('PC1')
        ax.set_title('First Principal Component')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


class ChaosDetector:
    """
    Detect and quantify chaos in inference dynamics.
    """
    
    def __init__(self):
        pass
    
    def correlation_dimension(self, trajectory: np.ndarray, 
                             max_radius: float = None) -> Tuple[float, np.ndarray]:
        """
        Compute correlation dimension using Grassberger-Procaccia algorithm.
        
        C(r) ~ r^D for chaotic attractors
        """
        n = len(trajectory)
        
        # Compute pairwise distances
        distances = []
        for i in range(n):
            for j in range(i + 1, n):
                distances.append(np.linalg.norm(trajectory[i] - trajectory[j]))
        distances = np.array(distances)
        
        if max_radius is None:
            max_radius = np.percentile(distances, 90)
            
        # Compute correlation sum for various radii
        radii = np.logspace(np.log10(np.min(distances) + 1e-10), 
                           np.log10(max_radius), 30)
        correlation = []
        
        for r in radii:
            correlation.append(np.sum(distances < r) / len(distances))
            
        correlation = np.array(correlation)
        
        # Fit power law
        valid = (correlation > 1e-10) & (correlation < 1)
        if np.sum(valid) > 5:
            slope, _, r_value, _, _ = stats.linregress(
                np.log(radii[valid]), np.log(correlation[valid]))
            return slope, np.column_stack([radii, correlation])
        
        return 0, np.column_stack([radii, correlation])
    
    def largest_lyapunov(self, trajectory: np.ndarray, 
                        dim: int = None) -> float:
        """
        Estimate largest Lyapunov exponent using Rosenstein algorithm.
        """
        if dim is None:
            dim = trajectory.shape[1]
            
        n = len(trajectory)
        
        # Find nearest neighbors
        divergences = []
        
        for i in range(n - 10):
            # Find nearest neighbor
            distances = np.linalg.norm(trajectory[i+1:] - trajectory[i], axis=1)
            if len(distances) > 0 and np.min(distances) > 1e-10:
                j = np.argmin(distances) + i + 1
                
                # Track divergence
                k_max = min(n - i, n - j, 20)
                for k in range(1, k_max):
                    d = np.linalg.norm(trajectory[i + k] - trajectory[j + k])
                    if d > 1e-10:
                        divergences.append((k, np.log(d / distances[j - i - 1])))
                        
        if len(divergences) > 0:
            # Average divergence vs time
            times = np.array([d[0] for d in divergences])
            log_divs = np.array([d[1] for d in divergences])
            
            slope, _, _, _, _ = stats.linregress(times, log_divs)
            return slope
            
        return 0
    
    def surrogate_test(self, trajectory: np.ndarray, n_surrogates: int = 10) -> Dict:
        """
        Test if dynamics are truly chaotic using surrogate data.
        """
        # Original Lyapunov exponent
        original_lyap = self.largest_lyapunov(trajectory)
        
        # Generate surrogates (phase-randomized)
        surrogate_lyaps = []
        for _ in range(n_surrogates):
            surrogate = self._phase_shuffle(trajectory)
            surrogate_lyaps.append(self.largest_lyapunov(surrogate))
            
        # Statistical test
        surrogate_mean = np.mean(surrogate_lyaps)
        surrogate_std = np.std(surrogate_lyaps)
        
        if surrogate_std > 0:
            z_score = (original_lyap - surrogate_mean) / surrogate_std
        else:
            z_score = 0
            
        return {
            'original_lyapunov': original_lyap,
            'surrogate_mean': surrogate_mean,
            'surrogate_std': surrogate_std,
            'z_score': z_score,
            'is_chaotic': z_score > 2.0 and original_lyap > 0,
            'p_value': 1 - stats.norm.cdf(z_score) if z_score > 0 else stats.norm.cdf(z_score)
        }
    
    def _phase_shuffle(self, data: np.ndarray) -> np.ndarray:
        """Generate phase-randomized surrogate."""
        n = len(data)
        surrogate = np.zeros_like(data)
        
        for d in range(data.shape[1]):
            fft = np.fft.fft(data[:, d])
            phases = np.angle(fft)
            random_phases = np.random.uniform(0, 2 * np.pi, n)
            random_phases[0] = 0  # Keep DC component
            if n % 2 == 0:
                random_phases[n // 2] = 0
            fft_surrogate = np.abs(fft) * np.exp(1j * random_phases)
            surrogate[:, d] = np.real(np.fft.ifft(fft_surrogate))
            
        return surrogate


# ============================================================================
# SECTION 4: MULTI-SCALE ANALYSIS
# ============================================================================

class MultiScaleAnalyzer:
    """
    Analyze chip behavior across multiple scales.
    
    Scales:
    - Micro: Transistor switching (~ps, nm)
    - Meso: PE array dynamics (~ns, μm)
    - Macro: Chip-level inference (~μs, mm)
    
    Key questions:
    - How do micro fluctuations propagate to macro?
    - What emergent properties arise at each scale?
    - How to optimize cross-scale coupling?
    """
    
    def __init__(self, n_pes: int = 1024):
        self.n_pes = n_pes
        
    def transistor_dynamics(self, n_transistors: int = 1000,
                           temperature: float = 300) -> Dict:
        """
        Model transistor switching at micro scale.
        
        Includes:
        - Thermal noise
        - Random telegraph noise
        - Variability
        """
        kT = 8.617e-5 * temperature  # eV
        
        # Switching times (log-normal distribution)
        mean_switch_time = 1e-12  # 1 ps typical
        sigma_switch = 0.3
        switch_times = np.random.lognormal(np.log(mean_switch_time), sigma_switch, n_transistors)
        
        # Thermal noise current fluctuations
        noise_amplitude = np.sqrt(kT / 1e-6)  # Johnson noise
        noise = np.random.normal(0, noise_amplitude, n_transistors)
        
        # Threshold voltage variation
        vt_mean = 0.3  # V
        vt_sigma = 0.02
        vt_variation = np.random.normal(0, vt_sigma, n_transistors)
        
        # Switching activity simulation
        switching_events = []
        for i in range(n_transistors):
            # Poisson process for switching
            rate = 1 / switch_times[i]
            events = np.cumsum(np.random.exponential(1/rate, 100))
            switching_events.append(events)
            
        return {
            'switch_times': switch_times,
            'noise_amplitudes': noise,
            'vt_variations': vt_variation,
            'switching_events': switching_events,
            'mean_switch_time': np.mean(switch_times),
            'switch_time_std': np.std(switch_times)
        }
    
    def pe_array_dynamics(self, grid_size: Tuple[int, int] = (32, 32),
                         n_steps: int = 500,
                         input_rate: float = 0.1) -> Dict:
        """
        Model PE array dynamics at meso scale.
        
        Includes:
        - Local computation
        - Neighbor communication
        - Activity waves
        """
        n_pes = grid_size[0] * grid_size[1]
        
        # PE states: activity level (0-1)
        activity = np.zeros(grid_size)
        
        # Local processing state
        processing = np.zeros(grid_size, dtype=bool)
        
        # Communication buffer
        buffer = np.zeros(grid_size)
        
        activity_history = []
        wave_fronts = []
        
        for step in range(n_steps):
            # Input injection
            input_sites = np.random.random(grid_size) < input_rate
            activity[input_sites] = 1.0
            
            # Local processing (decay)
            activity *= 0.95
            
            # Communication (diffusion)
            new_activity = activity.copy()
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    neighbors = []
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
                            neighbors.append(activity[ni, nj])
                    if neighbors:
                        new_activity[i, j] += 0.1 * (np.mean(neighbors) - activity[i, j])
                        
            activity = np.clip(new_activity, 0, 1)
            activity_history.append(activity.copy())
            
            # Detect wave fronts
            threshold = 0.7
            front = np.where(activity > threshold)
            if len(front[0]) > 0:
                wave_fronts.append((step, front[0].mean(), front[1].mean()))
                
        activity_history = np.array(activity_history)
        
        # Analyze patterns
        total_activity = np.sum(activity_history, axis=(1, 2))
        spatial_variance = np.var(activity_history, axis=(1, 2))
        
        return {
            'activity_history': activity_history,
            'total_activity': total_activity,
            'spatial_variance': spatial_variance,
            'wave_fronts': wave_fronts,
            'steady_state_activity': np.mean(total_activity[-100:]),
            'activity_fluctuation': np.std(total_activity[-100:]),
            'wave_velocity': self._compute_wave_velocity(wave_fronts)
        }
    
    def _compute_wave_velocity(self, wave_fronts: List) -> float:
        """Compute wave propagation velocity."""
        if len(wave_fronts) < 2:
            return 0
            
        velocities = []
        for i in range(1, len(wave_fronts)):
            dt = wave_fronts[i][0] - wave_fronts[i-1][0]
            dx = np.sqrt((wave_fronts[i][1] - wave_fronts[i-1][1])**2 +
                        (wave_fronts[i][2] - wave_fronts[i-1][2])**2)
            if dt > 0:
                velocities.append(dx / dt)
                
        return np.mean(velocities) if velocities else 0
    
    def chip_level_inference(self, n_inferences: int = 1000,
                            model_complexity: float = 1.0) -> Dict:
        """
        Model chip-level inference at macro scale.
        
        Includes:
        - Token generation
        - Latency distribution
        - Throughput
        """
        # Latency per token (depends on complexity)
        base_latency = 1e-6  # 1 μs base
        latency_mean = base_latency * model_complexity
        latency_sigma = latency_mean * 0.2
        
        latencies = np.random.lognormal(np.log(latency_mean), 0.2, n_inferences)
        
        # Throughput calculation
        cumulative_time = np.cumsum(latencies)
        throughput = np.arange(1, n_inferences + 1) / cumulative_time
        
        # Token quality (simulated)
        quality = 1.0 - 0.1 * np.exp(-latencies / latency_mean)
        
        # Bottleneck analysis
        bottleneck_pe = np.argmax(latencies) if len(latencies) > 0 else 0
        
        return {
            'latencies': latencies,
            'mean_latency': np.mean(latencies),
            'latency_std': np.std(latencies),
            'throughput_history': throughput,
            'steady_state_throughput': throughput[-1] if len(throughput) > 0 else 0,
            'quality_scores': quality,
            'mean_quality': np.mean(quality),
            'total_time': cumulative_time[-1] if len(cumulative_time) > 0 else 0
        }
    
    def cross_scale_coupling(self, 
                            micro_scale: Dict,
                            meso_scale: Dict,
                            macro_scale: Dict) -> Dict:
        """
        Analyze coupling between scales.
        
        How do micro fluctuations affect macro behavior?
        """
        # Micro to Meso coupling
        micro_var = micro_scale.get('switch_time_std', 0)
        meso_var = meso_scale.get('activity_fluctuation', 0)
        
        micro_to_meso = meso_var / max(micro_var, 1e-15)
        
        # Meso to Macro coupling
        meso_activity = meso_scale.get('steady_state_activity', 0)
        macro_throughput = macro_scale.get('steady_state_throughput', 0)
        
        meso_to_macro = macro_throughput / max(meso_activity, 1e-15)
        
        # Propagation analysis
        micro_propagation = {
            'amplification': micro_to_meso > 1,
            'factor': micro_to_meso
        }
        
        meso_propagation = {
            'amplification': meso_to_macro > 1,
            'factor': meso_to_macro
        }
        
        return {
            'micro_to_meso_coupling': micro_to_meso,
            'meso_to_macro_coupling': meso_to_macro,
            'micro_propagation': micro_propagation,
            'meso_propagation': meso_propagation,
            'total_amplification': micro_to_meso * meso_to_macro,
            'is_stable': micro_to_meso * meso_to_macro < 10
        }
    
    def plot_multi_scale_analysis(self, 
                                  micro: Dict,
                                  meso: Dict,
                                  macro: Dict,
                                  save_path: str = None):
        """Generate multi-scale visualization."""
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        
        # Micro scale
        ax = axes[0, 0]
        if 'switch_times' in micro:
            ax.hist(micro['switch_times'] * 1e12, bins=50, color='blue', alpha=0.7)
            ax.set_xlabel('Switch Time (ps)')
            ax.set_ylabel('Count')
            ax.set_title('Micro: Transistor Switching')
            
        ax = axes[0, 1]
        if 'noise_amplitudes' in micro:
            ax.hist(micro['noise_amplitudes'] * 1e6, bins=50, color='green', alpha=0.7)
            ax.set_xlabel('Noise (μV)')
            ax.set_ylabel('Count')
            ax.set_title('Micro: Thermal Noise')
            
        ax = axes[0, 2]
        if 'vt_variations' in micro:
            ax.hist(micro['vt_variations'] * 1e3, bins=50, color='red', alpha=0.7)
            ax.set_xlabel('Vt Variation (mV)')
            ax.set_ylabel('Count')
            ax.set_title('Micro: Threshold Variation')
            
        # Meso scale
        ax = axes[1, 0]
        if 'total_activity' in meso:
            ax.plot(meso['total_activity'], alpha=0.7)
            ax.set_xlabel('Time Step')
            ax.set_ylabel('Total Activity')
            ax.set_title('Meso: PE Array Activity')
            
        ax = axes[1, 1]
        if 'activity_history' in meso:
            if len(meso['activity_history']) > 0:
                im = ax.imshow(meso['activity_history'][-1], cmap='hot')
                ax.set_xlabel('PE X')
                ax.set_ylabel('PE Y')
                ax.set_title('Meso: Final Activity Map')
                plt.colorbar(im, ax=ax)
                
        ax = axes[1, 2]
        if 'spatial_variance' in meso:
            ax.plot(meso['spatial_variance'], alpha=0.7, color='purple')
            ax.set_xlabel('Time Step')
            ax.set_ylabel('Spatial Variance')
            ax.set_title('Meso: Activity Heterogeneity')
            
        # Macro scale
        ax = axes[2, 0]
        if 'latencies' in macro:
            ax.hist(macro['latencies'] * 1e6, bins=50, color='orange', alpha=0.7)
            ax.set_xlabel('Latency (μs)')
            ax.set_ylabel('Count')
            ax.set_title('Macro: Inference Latency')
            
        ax = axes[2, 1]
        if 'throughput_history' in macro:
            ax.plot(macro['throughput_history'], alpha=0.7, color='teal')
            ax.set_xlabel('Inference #')
            ax.set_ylabel('Throughput (inf/s)')
            ax.set_title('Macro: Throughput Evolution')
            
        ax = axes[2, 2]
        if 'quality_scores' in macro:
            ax.hist(macro['quality_scores'], bins=50, color='magenta', alpha=0.7)
            ax.set_xlabel('Quality Score')
            ax.set_ylabel('Count')
            ax.set_title('Macro: Output Quality')
            
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# SECTION 5: INTEGRATED ANALYSIS
# ============================================================================

class ComplexSystemsEmergence:
    """
    Integrate all complex systems analysis for comprehensive chip understanding.
    """
    
    def __init__(self, n_pes: int = 1024):
        self.n_pes = n_pes
        self.sandpile = SandpileModel(grid_size=(32, 32))
        self.branching = CriticalBranchingProcess(n_pes=n_pes)
        self.emergence = EmergenceAnalyzer(grid_size=(32, 32))
        self.sync = SynchronizationAnalyzer(n_pes=n_pes)
        self.nonlinear = NonlinearDynamicsAnalyzer(dim=64)
        self.chaos = ChaosDetector()
        self.multiscale = MultiScaleAnalyzer(n_pes=n_pes)
        
    def run_full_analysis(self, n_iterations: int = 5000) -> Dict:
        """Run comprehensive analysis across all domains."""
        results = {}
        
        print("1. Running Sandpile SOC Analysis...")
        results['sandpile'] = self.sandpile.run_simulation(n_grains=n_iterations)
        
        print("2. Running Branching Process Analysis...")
        results['branching'] = self.branching.run_simulation(n_cascades=n_iterations)
        
        print("3. Running Emergence Analysis...")
        results['emergence'] = self.emergence.game_of_life_inference(n_steps=200)
        
        print("4. Running Synchronization Analysis...")
        results['sync'] = self.sync.kuramoto_model(n_steps=300)
        
        print("5. Running Nonlinear Dynamics Analysis...")
        results['nonlinear'] = self.nonlinear.recurrent_network(n_steps=500)
        
        print("6. Running Multi-Scale Analysis...")
        micro = self.multiscale.transistor_dynamics()
        meso = self.multiscale.pe_array_dynamics(n_steps=200)
        macro = self.multiscale.chip_level_inference(n_inferences=n_iterations)
        results['multiscale'] = self.multiscale.cross_scale_coupling(micro, meso, macro)
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive analysis report."""
        report = []
        report.append("=" * 70)
        report.append("COMPLEX SYSTEMS EMERGENCE ANALYSIS REPORT")
        report.append("=" * 70)
        
        # Sandpile Results
        report.append("\n1. SELF-ORGANIZED CRITICALITY (Sandpile Model)")
        report.append("-" * 50)
        sp = results.get('sandpile', {})
        report.append(f"   Avalanche Size Exponent: {sp.get('size_exponent', 0):.3f}")
        report.append(f"   Duration Exponent: {sp.get('duration_exponent', 0):.3f}")
        report.append(f"   Scaling Exponent (γ): {sp.get('scaling_exponent', 0):.3f}")
        report.append(f"   Is Critical: {sp.get('is_critical_size', False)}")
        report.append(f"   Dissipation Rate: {sp.get('dissipation_rate', 0):.3f}")
        
        # Branching Results
        report.append("\n2. CRITICAL BRANCHING PROCESS")
        report.append("-" * 50)
        br = results.get('branching', {})
        report.append(f"   Size Exponent: {br.get('size_exponent', 0):.3f}")
        report.append(f"   Duration Exponent: {br.get('duration_exponent', 0):.3f}")
        report.append(f"   Scaling Exponent: {br.get('scaling_exponent', 0):.3f}")
        report.append(f"   Is Critical: {br.get('is_critical', False)}")
        
        # Emergence Results
        report.append("\n3. EMERGENCE ANALYSIS")
        report.append("-" * 50)
        em = results.get('emergence', {})
        report.append(f"   Steady-State Active Fraction: {em.get('steady_state_active', 0):.3f}")
        report.append(f"   Mean Cluster Count: {em.get('steady_state_clusters', 0):.1f}")
        report.append(f"   Oscillation Period: {em.get('oscillation_period', 0)}")
        
        # Synchronization Results
        report.append("\n4. SYNCHRONIZATION ANALYSIS")
        report.append("-" * 50)
        sy = results.get('sync', {})
        report.append(f"   Final Order Parameter: {sy.get('final_order_parameter', 0):.3f}")
        report.append(f"   Is Synchronized: {sy.get('is_synchronized', False)}")
        report.append(f"   Is Chimera State: {sy.get('is_chimera', False)}")
        report.append(f"   Number of Clusters: {sy.get('n_clusters', 0)}")
        report.append(f"   Critical Coupling: {sy.get('critical_coupling', 0):.3f}")
        
        # Nonlinear Results
        report.append("\n5. NONLINEAR DYNAMICS")
        report.append("-" * 50)
        nl = results.get('nonlinear', {})
        report.append(f"   Lyapunov Exponent: {nl.get('lyapunov_exponent', 0):.4f}")
        report.append(f"   Is Chaotic: {nl.get('is_chaotic', False)}")
        report.append(f"   Attractor Type: {nl.get('attractor_type', 'unknown')}")
        report.append(f"   Converged: {nl.get('converged', False)}")
        
        # Multi-Scale Results
        report.append("\n6. MULTI-SCALE COUPLING")
        report.append("-" * 50)
        ms = results.get('multiscale', {})
        report.append(f"   Micro→Meso Coupling: {ms.get('micro_to_meso_coupling', 0):.3f}")
        report.append(f"   Meso→Macro Coupling: {ms.get('meso_to_macro_coupling', 0):.3f}")
        report.append(f"   Total Amplification: {ms.get('total_amplification', 0):.3f}")
        report.append(f"   Is Stable: {ms.get('is_stable', True)}")
        
        # Summary
        report.append("\n" + "=" * 70)
        report.append("SUMMARY: EMERGENT PROPERTIES")
        report.append("=" * 70)
        
        # Key findings
        findings = []
        if sp.get('is_critical_size'):
            findings.append("✓ System operates at self-organized criticality")
        if sy.get('is_synchronized'):
            findings.append("✓ PEs exhibit synchronized behavior")
        elif sy.get('is_chimera'):
            findings.append("✓ Chimera state detected (partial synchronization)")
        if not nl.get('is_chaotic'):
            findings.append("✓ Inference dynamics are stable (non-chaotic)")
        if ms.get('is_stable'):
            findings.append("✓ Cross-scale coupling is stable")
            
        for f in findings:
            report.append(f"   {f}")
            
        return "\n".join(report)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run comprehensive complex systems analysis."""
    print("=" * 70)
    print("CYCLE 10: COMPLEX SYSTEMS CHIP EMERGENCE ANALYSIS")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = ComplexSystemsEmergence(n_pes=1024)
    
    # Run full analysis
    results = analyzer.run_full_analysis(n_iterations=5000)
    
    # Generate report
    report = analyzer.generate_report(results)
    print("\n" + report)
    
    # Generate plots
    print("\nGenerating visualization plots...")
    
    # Sandpile plots
    analyzer.sandpile.plot_avalanche_analysis(
        save_path='/home/z/my-project/research/cycle10_avalanche_analysis.png')
    
    # Nonlinear dynamics plot
    if 'trajectory' in results['nonlinear']:
        analyzer.nonlinear.phase_portrait(
            results['nonlinear']['trajectory'],
            save_path='/home/z/my-project/research/cycle10_phase_portrait.png')
    
    # Multi-scale plot
    micro = analyzer.multiscale.transistor_dynamics()
    meso = analyzer.multiscale.pe_array_dynamics(n_steps=200)
    macro = analyzer.multiscale.chip_level_inference()
    analyzer.multiscale.plot_multi_scale_analysis(
        micro, meso, macro,
        save_path='/home/z/my-project/research/cycle10_multiscale_analysis.png')
    
    print("\nAnalysis complete. Plots saved.")
    
    return results


if __name__ == "__main__":
    results = main()
