#!/usr/bin/env python3
"""
Thermal Simulation Engine - P11
=================================

Hierarchical thermal simulation using Fast Multipole Method for multi-agent systems.
Achieves O(n log n) scaling for heat diffusion problems.

Author: Casey DiGennaro
Date: March 2026
Paper: P11 - Thermal Simulation and Management for AI Workloads
"""

import numpy as np
from scipy import sparse
from scipy.special import sph_harm
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

# ============================================================================
# Configuration and Constants
# ============================================================================

@dataclass
class SimulationConfig:
    """Configuration for thermal simulation."""
    alpha: float = 0.1          # Thermal diffusivity
    order: int = 4              # Multipole expansion order
    theta: float = 0.5          # Opening angle criterion
    max_leaf_size: int = 16     # Maximum agents per leaf
    dt: float = 0.01            # Default timestep
    epsilon: float = 1e-10      # Small value to prevent singularity

# Material properties
MATERIALS = {
    'silicon': {
        'k': 148.0,      # Thermal conductivity [W/(m·K)]
        'rho': 2329.0,   # Density [kg/m³]
        'cp': 700.0,     # Specific heat [J/(kg·K)]
        'alpha': 9.07e-5 # Thermal diffusivity [m²/s]
    },
    'copper': {
        'k': 385.0,
        'rho': 8960.0,
        'cp': 385.0,
        'alpha': 1.12e-4
    },
    'air_300k': {
        'k': 0.026,
        'rho': 1.16,
        'cp': 1007.0,
        'alpha': 2.22e-5
    }
}

# ============================================================================
# Octree Data Structure
# ============================================================================

@dataclass
class OctreeNode:
    """Node in octree for hierarchical thermal simulation."""
    center: np.ndarray           # Center of bounding box [x, y, z]
    size: float                  # Half-width of bounding box
    agents: List[int]            # Agent indices in this node
    children: Optional[List['OctreeNode']] = None  # 8 children if internal
    multipole: Optional[np.ndarray] = None   # Multipole coefficients
    local: Optional[np.ndarray] = None       # Local expansion coefficients
    interaction_list: Optional[List[int]] = None  # Indices of interaction cells

    def is_leaf(self) -> bool:
        """Check if this node is a leaf."""
        return self.children is None

    def contains(self, position: np.ndarray) -> bool:
        """Check if position is within this node's bounding box."""
        return np.all(np.abs(position - self.center) <= self.size)

# ============================================================================
# Hierarchical Thermal Simulation
# ============================================================================

class ThermalSimulation:
    """
    Hierarchical thermal simulation using Fast Multipole Method.

    This class implements O(n log n) heat diffusion simulation for
    multi-agent systems through hierarchical multipole approximation.
    """

    def __init__(
        self,
        positions: np.ndarray,
        temperatures: np.ndarray,
        config: SimulationConfig = SimulationConfig()
    ):
        """
        Initialize thermal simulation.

        Args:
            positions: (n, 3) array of agent positions
            temperatures: (n,) array of initial temperatures
            config: Simulation configuration
        """
        self.positions = positions
        self.temperatures = temperatures
        self.config = config
        self.n = len(temperatures)

        # Build octree
        self.root = self._build_octree()

        # Statistics
        self.stats = {
            'build_time': 0.0,
            'step_time': 0.0,
            'multipole_time': 0.0,
            'local_time': 0.0,
        }

    def _build_octree(self) -> OctreeNode:
        """Build octree from agent positions."""
        start_time = time.time()

        # Compute bounding box
        min_pos = self.positions.min(axis=0)
        max_pos = self.positions.max(axis=0)
        center = (min_pos + max_pos) / 2
        size = np.max(max_pos - min_pos) / 2 * 1.01  # Slight padding

        # Create root with all agents
        root = OctreeNode(
            center=center,
            size=size,
            agents=list(range(self.n))
        )

        # Recursively subdivide
        self._subdivide(root)

        self.stats['build_time'] = time.time() - start_time
        return root

    def _subdivide(self, node: OctreeNode):
        """Recursively subdivide node until leaves are small enough."""
        if len(node.agents) <= self.config.max_leaf_size:
            return

        # Create 8 children
        node.children = []
        half_size = node.size / 2

        for i in range(8):
            # Compute child center using binary encoding
            offset = np.array([
                (i & 1) * 2 - 1,
                ((i >> 1) & 1) * 2 - 1,
                ((i >> 2) & 1) * 2 - 1
            ]) * half_size

            child = OctreeNode(
                center=node.center + offset,
                size=half_size,
                agents=[]
            )
            node.children.append(child)

        # Distribute agents to children
        for idx in node.agents:
            pos = self.positions[idx]
            for child in node.children:
                if child.contains(pos):
                    child.agents.append(idx)
                    break

        # Clear agents from internal node
        node.agents = []

        # Recursively subdivide children
        for child in node.children:
            if len(child.agents) > 0:
                self._subdivide(child)

        # Build interaction list
        self._build_interaction_list(node)

    def _build_interaction_list(self, node: OctreeNode):
        """
        Build interaction list for node using Barnes-Hut criterion.

        The interaction list contains cells that are:
        1. Well-separated from this node
        2. Not in the well-separated list of this node's parent
        """
        if node.is_leaf():
            return

        # Find interaction list for each child
        for child in node.children:
            child.interaction_list = []
            self._find_interactions(child, self.root, child.interaction_list)

    def _find_interactions(
        self,
        node: OctreeNode,
        other: OctreeNode,
        interaction_list: List[int]
    ):
        """Recursively find interaction list cells."""
        if other.is_leaf() or len(other.agents) == 0:
            return

        # Check if well-separated
        distance = np.linalg.norm(node.center - other.center)
        if distance > self.config.theta * (node.size + other.size):
            # Well-separated - add to interaction list
            if other not in interaction_list:
                interaction_list.append(other)
        else:
            # Not well-separated - check children
            if other.children:
                for child in other.children:
                    self._find_interactions(node, child, interaction_list)

    # ========================================================================
    # Multipole Operations
    # ========================================================================

    def _compute_multipole(self, node: OctreeNode):
        """Compute multipole expansion for node (upward pass)."""
        if node.multipole is not None:
            return

        start_time = time.time()

        # Initialize multipole coefficients
        # For order p, we need (p+1)^2 coefficients
        num_coeffs = (self.config.order + 1) ** 2
        node.multipole = np.zeros(num_coeffs, dtype=complex)

        if node.is_leaf():
            # Compute from agents directly
            for idx in node.agents:
                pos = self.positions[idx] - node.center
                temp = self.temperatures[idx]

                # Spherical coordinates
                r = np.linalg.norm(pos)
                if r < self.config.epsilon:
                    continue

                theta = np.arccos(pos[2] / r)
                phi = np.arctan2(pos[1], pos[0])

                # Add contribution to each multipole term
                k = 0
                for l in range(self.config.order + 1):
                    for m in range(-l, l + 1):
                        Y_lm = sph_harm(m, l, phi, theta)
                        node.multipole[k] += temp * (r ** l) * Y_lm
                        k += 1
        else:
            # Compute from children via M2M translation
            for child in node.children:
                if child.agents or (child.children and any(c.agents for c in child.children)):
                    self._compute_multipole(child)
                    self._m2m_translation(node, child)

        self.stats['multipole_time'] += time.time() - start_time

    def _m2m_translation(self, parent: OctreeNode, child: OctreeNode):
        """Translate multipole from child to parent (M2M)."""
        if child.multipole is None:
            return

        # Displacement from parent to child center
        d = child.center - parent.center
        r = np.linalg.norm(d)
        if r < self.config.epsilon:
            return

        theta = np.arccos(d[2] / r)
        phi = np.arctan2(d[1], d[0])

        # Simplified translation (full implementation requires rotation operators)
        # For order p, we translate each term
        k_child = 0
        for l in range(self.config.order + 1):
            for m in range(-l, l + 1):
                if abs(child.multipole[k_child]) > 1e-15:
                    # Add translated contribution to parent
                    k_parent = 0
                    for lp in range(l, self.config.order + 1):
                        for mp in range(-lp, lp + 1):
                            # Translation operator (simplified)
                            coeff = (r ** (lp - l)) * sph_harm(m - mp, lp - l, phi, theta)
                            parent.multipole[k_parent] += child.multipole[k_child] * coeff
                            k_parent += 1
                k_child += 1

    def _compute_local(self, node: OctreeNode):
        """Compute local expansion for node (downward pass)."""
        if node.local is None:
            node.local = np.zeros((self.config.order + 1) ** 2, dtype=complex)

        start_time = time.time()

        # Process interaction list
        if node.interaction_list:
            for interaction_cell in node.interaction_list:
                if interaction_cell.multipole is not None:
                    self._m2l_translation(node, interaction_cell)

        # Translate to children
        if not node.is_leaf() and node.children:
            for child in node.children:
                child.local = np.zeros_like(node.local)
                self._l2l_translation(child, node)
                self._compute_local(child)

        self.stats['local_time'] += time.time() - start_time

    def _m2l_translation(self, target: OctreeNode, source: OctreeNode):
        """Translate multipole to local expansion (M2L)."""
        if source.multipole is None:
            return

        # Displacement from source to target
        d = target.center - source.center
        r = np.linalg.norm(d)
        if r < self.config.epsilon:
            return

        theta = np.arccos(d[2] / r)
        phi = np.arctan2(d[1], d[0])

        # Convert multipole to local expansion
        k_source = 0
        for l in range(self.config.order + 1):
            for m in range(-l, l + 1):
                if abs(source.multipole[k_source]) > 1e-15:
                    # Add to target local expansion
                    k_target = 0
                    for lp in range(self.config.order + 1):
                        for mp in range(-lp, lp + 1):
                            # M2L translation operator
                            coeff = source.multipole[k_source] / (r ** (l + lp + 1))
                            coeff *= sph_harm(mp - m, lp + l, phi, theta)
                            target.local[k_target] += coeff
                            k_target += 1
                k_source += 1

    def _l2l_translation(self, child: OctreeNode, parent: OctreeNode):
        """Translate local expansion from parent to child (L2L)."""
        if parent.local is None:
            return

        # Displacement from parent to child
        d = child.center - parent.center
        r = np.linalg.norm(d)
        if r < self.config.epsilon:
            child.local = parent.local.copy()
            return

        theta = np.arccos(d[2] / r)
        phi = np.arctan2(d[1], d[0])

        # Translate local expansion
        k_parent = 0
        for l in range(self.config.order + 1):
            for m in range(-l, l + 1):
                if abs(parent.local[k_parent]) > 1e-15:
                    # Add to child local expansion
                    k_child = 0
                    for lp in range(l, self.config.order + 1):
                        for mp in range(-lp, lp + 1):
                            # L2L translation operator
                            coeff = (r ** (lp - l)) * sph_harm(m - mp, lp - l, phi, theta)
                            child.local[k_child] += parent.local[k_parent] * coeff
                            k_child += 1
                k_parent += 1

    # ========================================================================
    # Field Computation
    # ========================================================================

    def _compute_near_field(self, node: OctreeNode, idx: int) -> float:
        """Compute direct thermal interaction for nearby agents."""
        pos_i = self.positions[idx]
        T_i = self.temperatures[idx]
        sum_interaction = 0.0

        for j in node.agents:
            if j != idx:
                r = self.positions[j] - pos_i
                dist2 = np.dot(r, r)
                T_j = self.temperatures[j]
                sum_interaction += (T_j - T_i) / (dist2 + self.config.epsilon)

        return sum_interaction

    def _compute_far_field(self, node: OctreeNode, idx: int) -> float:
        """Compute far-field thermal interaction via local expansion."""
        if node.local is None:
            return 0.0

        pos_i = self.positions[idx] - node.center
        r = np.linalg.norm(pos_i)

        if r < self.config.epsilon:
            return 0.0

        theta = np.arccos(pos_i[2] / r)
        phi = np.arctan2(pos_i[1], pos_i[0])

        # Evaluate local expansion
        result = 0.0
        k = 0
        for l in range(self.config.order + 1):
            for m in range(-l, l + 1):
                Y_lm = sph_harm(m, l, phi, theta)
                result += (node.local[k] * Y_lm).real / (r ** (l + 1) + self.config.epsilon)
                k += 1

        return result

    def _find_leaf(self, node: OctreeNode, idx: int) -> OctreeNode:
        """Find leaf node containing agent idx."""
        if node.is_leaf():
            return node

        for child in node.children:
            if child.contains(self.positions[idx]):
                return self._find_leaf(child, idx)

        return node

    # ========================================================================
    # Time Integration
    # ========================================================================

    def step(self, dt: Optional[float] = None) -> np.ndarray:
        """
        Perform one timestep of thermal simulation.

        Args:
            dt: Timestep (uses config.dt if None)

        Returns:
            New temperatures
        """
        if dt is None:
            dt = self.config.dt

        start_time = time.time()

        # Reset stats
        self.stats['multipole_time'] = 0.0
        self.stats['local_time'] = 0.0

        # Upward pass: compute multipole expansions
        self._compute_multipole(self.root)

        # Downward pass: compute local expansions
        if self.root.local is None:
            self.root.local = np.zeros((self.config.order + 1) ** 2, dtype=complex)
        self._compute_local(self.root)

        # Compute new temperatures
        new_temperatures = np.zeros_like(self.temperatures)

        for idx in range(self.n):
            # Find leaf containing this agent
            leaf = self._find_leaf(self.root, idx)

            # Near-field (direct computation)
            near = self._compute_near_field(leaf, idx)

            # Far-field (local expansion)
            far = self._compute_far_field(leaf, idx)

            # Update temperature using heat equation
            new_temperatures[idx] = self.temperatures[idx] + self.config.alpha * dt * (near + far)

        self.temperatures = new_temperatures
        self.stats['step_time'] = time.time() - start_time

        return self.temperatures

    def adaptive_step(self, max_dt: float = 0.1) -> np.ndarray:
        """
        Perform timestep with adaptive dt based on stability (CFL condition).

        Args:
            max_dt: Maximum allowed timestep

        Returns:
            New temperatures
        """
        # Compute minimum inter-agent distance
        min_dist = self._compute_min_distance()

        # Maximum stable timestep (CFL condition)
        dt_max = min_dist ** 2 / (6 * self.config.alpha)
        dt = min(max_dt, dt_max)

        return self.step(dt)

    def _compute_min_distance(self) -> float:
        """Compute minimum distance between any two agents."""
        min_dist = np.inf

        for i in range(min(100, self.n)):  # Sample for efficiency
            for j in range(i + 1, min(100, self.n)):
                dist = np.linalg.norm(self.positions[i] - self.positions[j])
                min_dist = min(min_dist, dist)

        return min_dist

    # ========================================================================
    # Analysis Methods
    # ========================================================================

    def total_energy(self) -> float:
        """Compute total thermal energy."""
        return np.sum(self.temperatures)

    def max_temperature(self) -> float:
        """Compute maximum temperature."""
        return np.max(self.temperatures)

    def min_temperature(self) -> float:
        """Compute minimum temperature."""
        return np.min(self.temperatures)

    def mean_temperature(self) -> float:
        """Compute mean temperature."""
        return np.mean(self.temperatures)

    def get_stats(self) -> dict:
        """Get simulation statistics."""
        return self.stats.copy()


# ============================================================================
# Direct Method for Validation
# ============================================================================

class DirectThermalSimulation:
    """Direct O(n²) thermal simulation for validation."""

    def __init__(
        self,
        positions: np.ndarray,
        temperatures: np.ndarray,
        alpha: float = 0.1,
        epsilon: float = 1e-10
    ):
        self.positions = positions
        self.temperatures = temperatures
        self.alpha = alpha
        self.epsilon = epsilon
        self.n = len(temperatures)

    def step(self, dt: float) -> np.ndarray:
        """Perform one timestep using direct O(n²) computation."""
        new_temperatures = np.zeros_like(self.temperatures)

        for i in range(self.n):
            pos_i = self.positions[i]
            T_i = self.temperatures[i]
            sum_interaction = 0.0

            for j in range(self.n):
                if i == j:
                    continue

                r = self.positions[j] - pos_i
                dist2 = np.dot(r, r)
                T_j = self.temperatures[j]
                sum_interaction += (T_j - T_i) / (dist2 + self.epsilon)

            new_temperatures[i] = T_i + self.alpha * dt * sum_interaction

        self.temperatures = new_temperatures
        return self.temperatures


# ============================================================================
# Utility Functions
# ============================================================================

def generate_random_agents(n: int, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate random agent positions and temperatures.

    Args:
        n: Number of agents
        seed: Random seed

    Returns:
        (positions, temperatures) tuple
    """
    np.random.seed(seed)
    positions = np.random.rand(n, 3) * 10.0  # Random positions in [0, 10]
    temperatures = np.random.randn(n) * 10 + 300  # Random temps around 300K
    return positions, temperatures


def generate_grid_agents(n_per_side: int, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate agents on a regular grid with hotspot.

    Args:
        n_per_side: Agents per side of grid
        seed: Random seed

    Returns:
        (positions, temperatures) tuple
    """
    np.random.seed(seed)
    n = n_per_side ** 3

    # Grid positions
    x = np.linspace(0, 10, n_per_side)
    y = np.linspace(0, 10, n_per_side)
    z = np.linspace(0, 10, n_per_side)
    xx, yy, zz = np.meshgrid(x, y, z)
    positions = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    # Temperature with hotspot at center
    center = np.array([5, 5, 5])
    distances = np.linalg.norm(positions - center, axis=1)
    temperatures = 300 + 100 * np.exp(-distances ** 2 / 10)

    return positions, temperatures


def compare_methods(n: int, timesteps: int = 10) -> dict:
    """
    Compare hierarchical vs direct methods.

    Args:
        n: Number of agents
        timesteps: Number of timesteps to run

    Returns:
        Comparison results dictionary
    """
    print(f"\nComparing methods for {n} agents...")

    # Generate agents
    positions, temperatures = generate_random_agents(n)

    # Direct method
    print("Running direct method...")
    sim_direct = DirectThermalSimulation(positions.copy(), temperatures.copy())
    start = time.time()
    for _ in range(timesteps):
        temps_direct = sim_direct.step(dt=0.01)
    time_direct = time.time() - start

    # Hierarchical method
    print("Running hierarchical method...")
    config = SimulationConfig(order=4)
    sim_hier = ThermalSimulation(positions.copy(), temperatures.copy(), config)
    start = time.time()
    for _ in range(timesteps):
        temps_hier = sim_hier.step(dt=0.01)
    time_hier = time.time() - start

    # Compute error
    error = np.abs(temps_hier - temps_direct) / (np.abs(temps_direct) + 1e-10)
    max_error = np.max(error)
    mean_error = np.mean(error)

    # Energy conservation
    energy_initial = np.sum(temperatures)
    energy_final = np.sum(temps_hier)
    energy_drift = abs(energy_final - energy_initial) / energy_initial

    results = {
        'n': n,
        'time_direct': time_direct,
        'time_hier': time_hier,
        'speedup': time_direct / time_hier,
        'max_error': max_error,
        'mean_error': mean_error,
        'energy_drift': energy_drift
    }

    print(f"Direct time: {time_direct:.3f}s")
    print(f"Hierarchical time: {time_hier:.3f}s")
    print(f"Speedup: {results['speedup']:.1f}x")
    print(f"Max error: {max_error:.2%}")
    print(f"Energy drift: {energy_drift:.2e}")

    return results


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Thermal Simulation Engine - P11")
    print("=" * 70)

    # Run comparisons for different problem sizes
    problem_sizes = [1000, 10000, 50000]
    all_results = []

    for n in problem_sizes:
        results = compare_methods(n, timesteps=5)
        all_results.append(results)

    # Summary table
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"{'Agents':>10} {'Direct (s)':>12} {'Hier (s)':>12} {'Speedup':>10} {'Error':>10}")
    print("-" * 70)

    for r in all_results:
        print(f"{r['n']:>10} {r['time_direct']:>12.3f} {r['time_hier']:>12.3f} "
              f"{r['speedup']:>10.1f}x {r['max_error']:>9.2%}")

    print("\nSimulation complete!")
    print("=" * 70)
