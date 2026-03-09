"""
Attractor Analysis for POLLN Dynamical System

This module identifies and characterizes attractors (fixed points, limit cycles,
strange attractors) and computes their basins of attraction.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.spatial.distance import pdist, squareform
from scipy.stats import gaussian_kde
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

from vector_fields import PollnVectorField
from fixed_points import PollnFixedPoints, FixedPoint, FixedPointType
from limit_cycles import PollnLimitCycles, LimitCycle
from deepseek_dynamical import DeepSeekDynamicalSystems, MathematicalDerivation


class AttractorType(Enum):
    """Types of attractors"""
    FIXED_POINT = "fixed_point"  # Point attractor
    LIMIT_CYCLE = "limit_cycle"  # Periodic attractor
    STRANGE = "strange"  # Chaotic attractor
    TORUS = "torus"  # Quasi-periodic attractor


@dataclass
class Attractor:
    """Container for attractor data"""
    type: AttractorType
    center: np.ndarray  # Approximate center
    trajectory: np.ndarray  # Representative trajectory
    basin_points: List[np.ndarray]  # Points in basin of attraction
    dimension: float  # Fractal dimension (for strange attractors)
    lyapunov_spectrum: np.ndarray  # Lyapunov exponents
    entropy: float  # Kolmogorov-Sinai entropy
    mixing_time: float  # Time to reach attractor


class PollnAttractors:
    """
    Attractor analysis for POLLN dynamical system.

    Identifies attractors, computes basins of attraction, and
    characterizes strange attractors using fractal dimensions.
    """

    def __init__(self, vector_field: PollnVectorField):
        """
        Initialize attractor analyzer.

        Args:
            vector_field: POLLN vector field
        """
        self.vf = vector_field
        self.attractors: List[Attractor] = []
        self.derivation: Optional[MathematicalDerivation] = None

    def identify_attractors(self, num_trials: int = 50,
                           integration_time: float = 50.0) -> List[Attractor]:
        """
        Identify attractors from random initial conditions.

        Args:
            num_trials: Number of random initial conditions
            integration_time: Time to integrate each trajectory

        Returns:
            List of identified attractors
        """
        print(f"Searching for attractors from {num_trials} initial conditions...")

        endpoints = []

        for i in range(num_trials):
            # Random initial condition
            x0 = np.random.randn(self.vf.total_dim) * 2.0

            # Integrate forward
            sol = solve_ivp(
                self.vf.vector_field,
                (0, integration_time),
                x0,
                t_eval=np.linspace(0, integration_time, 1000),
                method='RK45',
                rtol=1e-10
            )

            # Store endpoint
            endpoint = sol.y[:, -1]
            endpoints.append(endpoint)

        # Cluster endpoints to find attractors
        unique_attractors = self._cluster_endpoints(endpoints)

        print(f"Found {len(unique_attractors)} attractors")

        return unique_attractors

    def _cluster_endpoints(self, endpoints: List[np.ndarray],
                          tol: float = 0.5) -> List[Attractor]:
        """
        Cluster trajectory endpoints to identify attractors.

        Args:
            endpoints: List of trajectory endpoints
            tol: Distance tolerance for clustering

        Returns:
            List of unique attractors
        """
        clusters = []

        for endpoint in endpoints:
            # Check if endpoint belongs to existing cluster
            found_cluster = False

            for cluster in clusters:
                if np.linalg.norm(endpoint - cluster['center']) < tol:
                    cluster['points'].append(endpoint)
                    cluster['center'] = np.mean(cluster['points'], axis=0)
                    found_cluster = True
                    break

            if not found_cluster:
                clusters.append({
                    'center': endpoint,
                    'points': [endpoint]
                })

        # Convert to attractors
        attractors = []

        for cluster in clusters:
            # Characterize the attractor
            center = cluster['center']
            trajectory = self._get_attractor_trajectory(center)

            # Compute Lyapunov spectrum
            lyap_spectrum = self._compute_lyapunov_spectrum(trajectory)

            # Classify attractor type
            if np.all(lyap_spectrum < 0):
                attr_type = AttractorType.FIXED_POINT
            elif np.any(np.abs(lyap_spectrum) < 1e-3) and np.any(lyap_spectrum > 0):
                attr_type = AttractorType.LIMIT_CYCLE
            elif np.max(lyap_spectrum) > 1e-3:
                attr_type = AttractorType.STRANGE
            else:
                attr_type = AttractorType.TORUS

            # Compute fractal dimension for strange attractors
            if attr_type == AttractorType.STRANGE:
                dimension = self._compute_fractal_dimension(trajectory)
            else:
                dimension = float(len(lyap_spectrum) > 0)

            # Estimate KS entropy
            entropy = self._estimate_ks_entropy(lyap_spectrum)

            attractor = Attractor(
                type=attr_type,
                center=center,
                trajectory=trajectory,
                basin_points=[],
                dimension=dimension,
                lyapunov_spectrum=lyap_spectrum,
                entropy=entropy,
                mixing_time=self._estimate_mixing_time(center)
            )

            attractors.append(attractor)

        return attractors

    def _get_attractor_trajectory(self, center: np.ndarray,
                                  time: float = 20.0) -> np.ndarray:
        """Get representative trajectory on attractor"""
        sol = solve_ivp(
            self.vf.vector_field,
            (0, time),
            center,
            t_eval=np.linspace(0, time, 1000),
            method='RK45',
            rtol=1e-10
        )
        return sol.y.T

    def _compute_lyapunov_spectrum(self, trajectory: np.ndarray,
                                   epsilon: float = 1e-6) -> np.ndarray:
        """
        Compute Lyapunov exponents using Wolf's algorithm.

        Lyapunov exponents measure average exponential divergence of nearby trajectories.
        Positive exponent = chaos (sensitive dependence).

        Args:
            trajectory: Attractor trajectory
            epsilon: Perturbation size

        Returns:
            Lyapunov spectrum (sorted, largest first)
        """
        # Simplified computation using Jacobian eigenvalues
        n_states = len(trajectory)
        n_dim = len(trajectory[0])

        exponents = np.zeros(n_dim)

        for i in range(min(100, n_states - 1)):
            x = trajectory[i]

            # Compute Jacobian
            J = self.vf.jacobian(x)

            # Local expansion rates from eigenvalues
            local_exp = np.real(np.linalg.eigvals(J))

            exponents += local_exp

        # Average over trajectory
        lyapunov = exponents / min(100, n_states - 1)

        # Sort descending
        lyapunov = np.sort(lyapunov)[::-1]

        return lyapunov

    def _compute_fractal_dimension(self, trajectory: np.ndarray,
                                   method: str = 'correlation') -> float:
        """
        Compute fractal dimension of attractor.

        Args:
            trajectory: Attractor trajectory
            method: 'correlation' or 'box_counting'

        Returns:
            Fractal dimension estimate
        """
        if method == 'correlation':
            return self._correlation_dimension(trajectory)
        else:
            return self._box_counting_dimension(trajectory)

    def _correlation_dimension(self, trajectory: np.ndarray,
                               max_epsilon: float = 1.0) -> float:
        """
        Compute correlation dimension using Grassberger-Procaccia algorithm.

        D_c = lim_{ε→0} log(C(ε)) / log(ε)
        where C(ε) is correlation sum

        Args:
            trajectory: Attractor trajectory
            max_epsilon: Maximum scale

        Returns:
            Correlation dimension
        """
        # Use first 3 dimensions for efficiency
        points = trajectory[:, :3]

        # Compute pairwise distances
        distances = pdist(points)

        # Correlation sum at different scales
        epsilons = np.logspace(-3, np.log10(max_epsilon), 20)
        correlation_sums = []

        for eps in epsilons:
            C = np.sum(distances < eps) / len(distances)**2
            correlation_sums.append(C)

        # Fit power law: log(C) ~ D * log(ε)
        log_eps = np.log(epsilons[correlation_sums > 0])
        log_C = np.log([c for c in correlation_sums if c > 0])

        if len(log_eps) > 1 and len(log_C) > 1:
            # Linear regression
            D = np.polyfit(log_eps, log_C, 1)[0]
            return abs(D)
        else:
            return 1.0

    def _box_counting_dimension(self, trajectory: np.ndarray,
                               scales: Optional[np.ndarray] = None) -> float:
        """
        Compute box-counting dimension.

        D_b = lim_{ε→0} log(N(ε)) / log(1/ε)
        where N(ε) is number of boxes of size ε needed

        Args:
            trajectory: Attractor trajectory
            scales: Box sizes to try

        Returns:
            Box-counting dimension
        """
        if scales is None:
            scales = np.logspace(-2, 0, 10)

        # Use first 2 dimensions for visualization
        points = trajectory[:, :2]

        # Normalize to [0, 1]
        points = (points - points.min(axis=0)) / (points.max(axis=0) - points.min(axis=0))

        box_counts = []

        for scale in scales:
            # Count boxes
            grid = np.floor(points / scale).astype(int)
            unique_boxes = len(np.unique(grid, axis=0))
            box_counts.append(unique_boxes)

        # Fit power law
        log_scales = np.log(scales)
        log_counts = np.log(box_counts)

        coeffs = np.polyfit(log_scales, log_counts, 1)
        dimension = -coeffs[0]

        return dimension

    def _estimate_ks_entropy(self, lyapunov_spectrum: np.ndarray) -> float:
        """
        Estimate Kolmogorov-Sinai entropy.

        h_KS = Σ_{λ_i > 0} λ_i
        Sum of positive Lyapunov exponents

        Args:
            lyapunov_spectrum: Lyapunov exponents

        Returns:
            KS entropy estimate
        """
        return np.sum(lyapunov_spectrum[lyapunov_spectrum > 0])

    def _estimate_mixing_time(self, center: np.ndarray) -> float:
        """
        Estimate time to reach attractor from neighborhood.

        Args:
            center: Attractor center

        Returns:
            Mixing time estimate
        """
        # Start from perturbed initial condition
        x0 = center + np.random.randn(len(center)) * 0.1

        # Integrate and track distance to attractor
        sol = solve_ivp(
            self.vf.vector_field,
            (0, 20),
            x0,
            t_eval=np.linspace(0, 20, 200),
            method='RK45'
        )

        distances = [np.linalg.norm(sol.y[:, i] - center) for i in range(len(sol.t))]

        # Find when distance drops below threshold
        threshold = 0.01
        for i, dist in enumerate(distances):
            if dist < threshold:
                return sol.t[i]

        return 20.0  # Default if never reaches

    def compute_basin_of_attraction(self, attractor: Attractor,
                                   grid_bounds: Tuple[float, float] = (-3, 3),
                                   grid_resolution: int = 20) -> np.ndarray:
        """
        Compute basin of attraction in 2D projection.

        Args:
            attractor: Target attractor
            grid_bounds: (min, max) for grid
            grid_resolution: Grid resolution

        Returns:
            Basin mask (1 if in basin, 0 otherwise)
        """
        x = np.linspace(grid_bounds[0], grid_bounds[1], grid_resolution)
        y = np.linspace(grid_bounds[0], grid_bounds[1], grid_resolution)
        X, Y = np.meshgrid(x, y)

        basin = np.zeros_like(X)

        for i in range(grid_resolution):
            for j in range(grid_resolution):
                # Create initial condition
                x0 = np.zeros(self.vf.total_dim)
                x0[0] = X[i, j]
                x0[1] = Y[i, j]

                # Integrate
                sol = solve_ivp(
                    self.vf.vector_field,
                    (0, 30),
                    x0,
                    t_eval=[30],
                    method='RK45'
                )

                endpoint = sol.y[:, -1]

                # Check if converges to attractor
                if np.linalg.norm(endpoint - attractor.center) < 0.5:
                    basin[i, j] = 1

        return basin

    def visualize_attractors(self, save_path: Optional[str] = None):
        """Visualize identified attractors"""
        if len(self.attractors) == 0:
            print("No attractors to visualize")
            return

        fig = plt.figure(figsize=(16, 12))

        # Plot 1: Phase space with attractors
        ax1 = fig.add_subplot(2, 2, 1)

        # Vector field
        X, Y, U, V = self.vf.phase_portrait_2d((-4, 4), (-4, 4), 15)
        ax1.streamplot(X, Y, U, V, color='gray', alpha=0.3, density=1)

        # Plot attractors
        colors = ['blue', 'red', 'green', 'purple', 'orange']
        for i, attr in enumerate(self.attractors):
            color = colors[i % len(colors)]
            ax1.scatter(attr.center[0], attr.center[1],
                       c=color, s=200, alpha=0.8,
                       label=f"{attr.type.value}", edgecolors='black')
            ax1.plot(attr.trajectory[:, 0], attr.trajectory[:, 1],
                    c=color, alpha=0.5, linewidth=1)

        ax1.set_xlabel("State Dimension 1")
        ax1.set_ylabel("State Dimension 2")
        ax1.set_title("Attractors in Phase Space")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Lyapunov spectrum
        ax2 = fig.add_subplot(2, 2, 2)

        for i, attr in enumerate(self.attractors):
            color = colors[i % len(colors)]
            ax2.plot(attr.lyapunov_spectrum, 'o-',
                    c=color, markersize=8,
                    label=f"{attr.type.value}")
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)

        ax2.set_xlabel("Exponent Index")
        ax2.set_ylabel("Lyapunov Exponent")
        ax2.set_title("Lyapunov Spectrum")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Fractal dimensions
        ax3 = fig.add_subplot(2, 2, 3)

        attr_types = [attr.type.value for attr in self.attractors]
        dimensions = [attr.dimension for attr in self.attractors]

        ax3.bar(range(len(attr_types)), dimensions,
               color=[colors[i % len(colors)] for i in range(len(attr_types))])
        ax3.set_xticks(range(len(attr_types)))
        ax3.set_xticklabels(attr_types, rotation=45, ha='right')
        ax3.set_ylabel("Fractal Dimension")
        ax3.set_title("Attractor Dimensions")

        # Plot 4: Basin of attraction (for first attractor)
        ax4 = fig.add_subplot(2, 2, 4)

        if len(self.attractors) > 0:
            basin = self.compute_basin_of_attraction(self.attractors[0])
            ax4.contourf(basin, levels=20, cmap='RdBu')
            ax4.scatter(self.attractors[0].center[0],
                       self.attractors[0].center[1],
                       c='black', s=200, marker='*', edgecolors='white')

        ax4.set_xlabel("State Dimension 1")
        ax4.set_ylabel("State Dimension 2")
        ax4.set_title("Basin of Attraction")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def derive_with_deepseek(self) -> MathematicalDerivation:
        """Use DeepSeek to derive attractor theory"""
        ds = DeepSeekDynamicalSystems()
        self.derivation = ds.derive_attractor_theory("""
        POLLN multi-agent system with:
        - Emergent collective behaviors
        - Metastable states
        - Convergence to optimal configurations
        - Possible chaotic dynamics
        """)

        return self.derivation


def analyze_attractors():
    """
    Comprehensive attractor analysis.
    """
    print("=" * 80)
    print("ATTRACTOR ANALYSIS")
    print("=" * 80)

    vf = PollnVectorField(num_agents=5, state_dim=3)
    analyzer = PollnAttractors(vf)

    # Derive theory
    print("\nDeriving attractor theory with DeepSeek...")
    derivation = analyzer.derive_with_deepseek()
    print(f"Theorem: {derivation.theorem[:200]}...")

    # Identify attractors
    print("\nIdentifying attractors...")
    attractors = analyzer.identify_attractors(num_trials=30)
    analyzer.attractors = attractors

    # Analyze each attractor
    print("\n" + "="*80)
    print("ATTRACTOR SUMMARY")
    print("="*80)

    for i, attr in enumerate(attractors):
        print(f"\nAttractor {i+1}:")
        print(f"  Type: {attr.type.value}")
        print(f"  Center: {attr.center[:3]}...")
        print(f"  Dimension: {attr.dimension:.4f}")
        print(f"  Max Lyapunov: {np.max(attr.lyapunov_spectrum):.4f}")
        print(f"  KS Entropy: {attr.entropy:.4f}")
        print(f"  Mixing Time: {attr.mixing_time:.4f}")

    # Visualize
    print("\nGenerating visualizations...")
    analyzer.visualize_attractors(
        save_path="C:/Users/casey/polln/simulations/novel/dynamical/attractors.png"
    )

    return {
        'analyzer': analyzer,
        'attractors': attractors,
        'derivation': derivation
    }


if __name__ == "__main__":
    results = analyze_attractors()
