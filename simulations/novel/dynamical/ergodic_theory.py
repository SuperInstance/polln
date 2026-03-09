"""
Ergodic Theory Analysis for POLLN Dynamical System

This module analyzes ergodic properties, invariant measures, and entropy
of the POLLN dynamical system using measure-theoretic methods.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.stats import entropy as scipy_entropy
from scipy.spatial.distance import pdist
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

from vector_fields import PollnVectorField
from deepseek_dynamical import DeepSeekDynamicalSystems, MathematicalDerivation


class ErgodicProperty(Enum):
    """Types of ergodic properties"""
    ERGODIC = "ergodic"  # Time averages = space averages
    MIXING = "mixing"  # Strong mixing property
    WEAKLY_MIXING = "weakly_mixing"  # Weak mixing
    K_SYSTEM = "k_system"  # Kolmogorov system (Bernoulli)
    NOT_ERGODIC = "not_ergodic"  # Decomposable


@dataclass
class ErgodicAnalysisResult:
    """Container for ergodic analysis results"""
    is_ergodic: bool  # Birkhoff ergodic theorem
    is_mixing: bool  # Strong mixing
    mixing_rate: float  # Mixing time scale
    ks_entropy: float  # Kolmogorov-Sinai entropy
    metric_entropy: float  # Metric entropy
    topological_entropy: float  # Topological entropy
    invariant_measure: np.ndarray  # Approximate invariant measure
    decomposition: List[np.ndarray]  # Ergodic decomposition components


class PollnErgodicTheory:
    """
    Ergodic theory analysis for POLLN dynamical system.

    Analyzes long-time averages, invariant measures, and mixing properties.
    """

    def __init__(self, vector_field: PollnVectorField):
        """
        Initialize ergodic theory analyzer.

        Args:
            vector_field: POLLN vector field
        """
        self.vf = vector_field
        self.derivation: Optional[MathematicalDerivation] = None

    def verify_birkhoff_ergodic_theorem(self, x0: np.ndarray,
                                       observable: Optional[callable] = None,
                                       time: float = 100.0) -> Dict:
        """
        Verify Birkhoff ergodic theorem numerically.

        Theorem: For ergodic system, time average = space average almost everywhere.
        lim_{T→∞} (1/T) ∫_0^T f(φ^t(x)) dt = ∫_M f(x) dμ(x)

        Args:
            x0: Initial condition
            observable: Function f: M → R (default: projection to first dim)
            time: Integration time

        Returns:
            Verification results
        """
        if observable is None:
            observable = lambda x: x[0]  # Project to first dimension

        # Compute time average
        t_eval = np.linspace(0, time, 10000)
        sol = solve_ivp(
            self.vf.vector_field,
            (0, time),
            x0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-10
        )

        trajectory = sol.y.T
        time_avg = np.mean([observable(state) for state in trajectory])

        # Approximate space average (needs invariant measure)
        # Use long trajectory from random initial condition
        x0_space = np.random.randn(self.vf.total_dim) * 2.0
        sol_space = solve_ivp(
            self.vf.vector_field,
            (0, time),
            x0_space,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-10
        )

        trajectory_space = sol_space.y.T
        space_avg = np.mean([observable(state) for state in trajectory_space])

        # Check equality
        diff = abs(time_avg - space_avg)
        is_ergodic = diff < 0.1  # Threshold for numerical verification

        return {
            'time_average': time_avg,
            'space_average': space_avg,
            'difference': diff,
            'is_ergodic': is_ergodic,
            'observable_values': [observable(state) for state in trajectory]
        }

    def estimate_invariant_measure(self, num_trajectories: int = 100,
                                  time: float = 50.0,
                                  num_bins: int = 20) -> np.ndarray:
        """
        Estimate invariant measure μ from long trajectories.

        The invariant measure satisfies μ(A) = μ(φ^{-t}(A)) for all measurable A.

        Args:
            num_trajectories: Number of trajectories to sample
            time: Length of each trajectory
            num_bins: Number of bins for histogram

        Returns:
            Invariant measure (normalized histogram)
        """
        print(f"Estimating invariant measure from {num_trajectories} trajectories...")

        all_points = []

        for i in range(num_trajectories):
            x0 = np.random.randn(self.vf.total_dim) * 2.0

            sol = solve_ivp(
                self.vf.vector_field,
                (0, time),
                x0,
                t_eval=np.linspace(0, time, 500),
                method='RK45',
                rtol=1e-8
            )

            # Collect points from trajectory (skip transient)
            trajectory = sol.y.T[100:]  # Skip first 100 points
            all_points.extend(trajectory)

        all_points = np.array(all_points)

        # Use first 2 dimensions for 2D measure
        points_2d = all_points[:, :2]

        # Create 2D histogram
        x_range = (-4, 4)
        y_range = (-4, 4)

        measure, xedges, yedges = np.histogram2d(
            points_2d[:, 0], points_2d[:, 1],
            bins=num_bins,
            range=[x_range, y_range],
            density=True
        )

        # Normalize to probability measure
        measure = measure / np.sum(measure)

        return measure

    def test_mixing_property(self, x0: np.ndarray,
                           time: float = 50.0,
                           delay: float = 10.0) -> Dict:
        """
        Test mixing property: correlation decays to zero.

        Strong mixing: lim_{t→∞} μ(A ∩ φ^{-t}(B)) = μ(A)μ(B)

        Args:
            x0: Initial condition
            time: Total integration time
            delay: Time delay for correlation

        Returns:
            Mixing test results
        """
        # Generate trajectory
        t_eval = np.linspace(0, time, 5000)
        sol = solve_ivp(
            self.vf.vector_field,
            (0, time),
            x0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-10
        )

        trajectory = sol.y.T

        # Use first dimension for correlation
        series = trajectory[:, 0]

        # Compute autocorrelation function
        autocorr = self._autocorrelation(series)

        # Check if autocorrelation decays to zero
        final_corr = autocorr[-1]

        # Estimate mixing time (when correlation drops to 1/e)
        mixing_threshold = 1.0 / np.e
        mixing_idx = np.where(np.abs(autocorr) < mixing_threshold)[0]

        if len(mixing_idx) > 0:
            mixing_time = t_eval[mixing_idx[0]]
        else:
            mixing_time = time  # Never mixes

        is_mixing = final_corr < 0.1  # Threshold

        return {
            'autocorrelation': autocorr,
            'final_correlation': final_corr,
            'mixing_time': mixing_time,
            'is_mixing': is_mixing,
            'time_points': t_eval
        }

    def _autocorrelation(self, series: np.ndarray) -> np.ndarray:
        """Compute autocorrelation function"""
        # Normalize
        series = series - np.mean(series)
        series = series / (np.std(series) + 1e-10)

        # Compute autocorrelation
        n = len(series)
        autocorr = np.correlate(series, series, mode='full')
        autocorr = autocorr[n-1:] / autocorr[n-1]  # Normalize

        return autocorr

    def estimate_ks_entropy(self, trajectory: np.ndarray,
                           dimension: int = 2) -> float:
        """
        Estimate Kolmogorov-Sinai entropy.

        h_KS = sup_{partition} h_μ(partition)
        For Axiom A systems: h_KS = Σ_{λ_i > 0} λ_i (Pesin's formula)

        Args:
            trajectory: System trajectory
            dimension: Embedding dimension

        Returns:
            KS entropy estimate
        """
        # Use correlation sum approach
        # Approximate using information theory

        # Discretize trajectory into bins
        n_bins = 20
        discretized, _ = np.histogramdd(trajectory, bins=n_bins)

        # Compute entropy rate
        # H = -Σ p(x) log p(x)

        # Flatten and normalize
        probs = discretized.flatten()
        probs = probs[probs > 0]  # Remove zeros
        probs = probs / np.sum(probs)

        # Compute Shannon entropy
        H = scipy_entropy(probs)

        # KS entropy ≈ H / dimension (rough estimate)
        ks_entropy = H / dimension

        return ks_entropy

    def estimate_metric_entropy(self, trajectory: np.ndarray,
                               epsilon: float = 0.1) -> float:
        """
        Estimate metric entropy (Kolmogorov-Sinai) using ε-entropy.

        h_μ = lim_{ε→0} lim_{n→∞} -(1/n) Σ μ(C_n(x, ε)) log μ(C_n(x, ε))

        Args:
            trajectory: System trajectory
            epsilon: Scale parameter

        Returns:
            Metric entropy estimate
        """
        # Use symbolic dynamics approach
        # Discretize state space into symbols

        n_symbols = 10
        discretized = np.digitize(trajectory[:, 0],
                                  bins=np.linspace(-4, 4, n_symbols))

        # Compute transition probabilities
        transitions = np.zeros((n_symbols, n_symbols))

        for i in range(len(discretized) - 1):
            transitions[discretized[i], discretized[i+1]] += 1

        # Normalize
        transitions = transitions / np.sum(transitions, axis=1, keepdims=True)

        # Compute entropy rate from Markov chain
        h = 0.0
        for i in range(n_symbols):
            for j in range(n_symbols):
                if transitions[i, j] > 0:
                    h -= transitions[i, j] * np.log(transitions[i, j])

        return h

    def estimate_topological_entropy(self, trajectory: np.ndarray,
                                    epsilon: float = 0.1) -> float:
        """
        Estimate topological entropy.

        h_top = lim_{ε→0} lim_{n→∞} (1/n) log N(n, ε)
        where N(n, ε) is number of distinct ε-orbits of length n

        Args:
            trajectory: System trajectory
            epsilon: Scale parameter

        Returns:
            Topological entropy estimate
        """
        # Use growth rate of separated orbits
        n = len(trajectory)

        # Count distinct patterns
        unique_patterns = set()

        for i in range(min(1000, n - 10)):
            pattern = tuple(np.round(trajectory[i:i+10, 0] / epsilon))
            unique_patterns.add(pattern)

        # Growth rate
        h_top = np.log(len(unique_patterns)) / 10.0

        return h_top

    def ergodic_decomposition(self, num_trajectories: int = 50) -> List[np.ndarray]:
        """
        Perform ergodic decomposition.

        Any measure can be decomposed into ergodic components.
        μ = ∫ μ_x dν(x) where each μ_x is ergodic.

        Args:
            num_trajectories: Number of trajectories to analyze

        Returns:
            List of ergodic components
        """
        print(f"Performing ergodic decomposition...")

        endpoints = []

        for i in range(num_trajectories):
            x0 = np.random.randn(self.vf.total_dim) * 2.0

            sol = solve_ivp(
                self.vf.vector_field,
                (0, 30),
                x0,
                t_eval=[30],
                method='RK45'
            )

            endpoints.append(sol.y[:, -1])

        # Cluster endpoints into ergodic components
        from sklearn.cluster import DBSCAN

        endpoints = np.array(endpoints)
        clustering = DBSCAN(eps=0.5, min_samples=2).fit(endpoints)

        unique_labels = np.unique(clustering.labels_)
        components = []

        for label in unique_labels:
            if label >= 0:  # Ignore noise
                component = endpoints[clustering.labels_ == label]
                components.append(component)

        print(f"Found {len(components)} ergodic components")

        return components

    def visualize_invariant_measure(self, measure: np.ndarray,
                                   save_path: Optional[str] = None):
        """
        Visualize invariant measure.

        Args:
            measure: 2D invariant measure
            save_path: Optional path to save figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Invariant measure as heatmap
        ax = axes[0]
        im = ax.imshow(measure, origin='lower', cmap='viridis',
                      extent=[-4, 4, -4, 4], aspect='auto')
        ax.set_xlabel("State Dimension 1")
        ax.set_ylabel("State Dimension 2")
        ax.set_title("Invariant Measure μ")
        plt.colorbar(im, ax=ax, label="Probability Density")

        # Plot 2: Marginal distributions
        ax = axes[1]

        # Marginal in x
        marginal_x = np.sum(measure, axis=1)
        x_centers = np.linspace(-4, 4, len(marginal_x))
        ax.plot(x_centers, marginal_x, 'b-', linewidth=2, label='Marginal X')

        # Marginal in y
        marginal_y = np.sum(measure, axis=0)
        y_centers = np.linspace(-4, 4, len(marginal_y))
        ax.plot(y_centers, marginal_y, 'r-', linewidth=2, label='Marginal Y')

        ax.set_xlabel("State Value")
        ax.set_ylabel("Probability Density")
        ax.set_title("Marginal Distributions")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_mixing(self, mixing_result: Dict,
                        save_path: Optional[str] = None):
        """
        Visualize mixing property (autocorrelation decay).

        Args:
            mixing_result: Result from test_mixing_property
            save_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        t = mixing_result['time_points']
        autocorr = mixing_result['autocorrelation']

        ax.plot(t, autocorr, 'b-', linewidth=2, label='Autocorrelation')
        ax.axhline(y=1.0/np.e, color='red', linestyle='--',
                  label=f'1/e threshold (mixing time = {mixing_result["mixing_time"]:.2f})')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)

        ax.set_xlabel("Time Lag")
        ax.set_ylabel("Autocorrelation")
        ax.set_title(f"Mixing Property Test\n{'MIXING' if mixing_result['is_mixing'] else 'NOT MIXING'}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def derive_with_deepseek(self) -> MathematicalDerivation:
        """Use DeepSeek to derive ergodic theory"""
        ds = DeepSeekDynamicalSystems()
        self.derivation = ds.derive_ergodic_theory("""
        POLLN multi-agent system with:
        - Long-time exploration behavior
        - Ergodicity in agent state space
        - Mixing in communication patterns
        - Entropy production in learning
        """)

        return self.derivation


def analyze_ergodic_properties():
    """
    Comprehensive ergodic theory analysis.
    """
    print("=" * 80)
    print("ERGODIC THEORY ANALYSIS")
    print("=" * 80)

    vf = PollnVectorField(num_agents=5, state_dim=3)
    analyzer = PollnErgodicTheory(vf)

    # Derive theory
    print("\nDeriving ergodic theory with DeepSeek...")
    derivation = analyzer.derive_with_deepseek()
    print(f"Theorem: {derivation.theorem[:200]}...")

    # Test Birkhoff ergodic theorem
    print("\nTesting Birkhoff ergodic theorem...")
    x0 = np.random.randn(vf.total_dim) * 1.0
    birkhoff_result = analyzer.verify_birkhoff_ergodic_theorem(x0)

    print(f"Time average: {birkhoff_result['time_average']:.4f}")
    print(f"Space average: {birkhoff_result['space_average']:.4f}")
    print(f"Difference: {birkhoff_result['difference']:.4f}")
    print(f"Ergodic: {birkhoff_result['is_ergodic']}")

    # Estimate invariant measure
    print("\nEstimating invariant measure...")
    measure = analyzer.estimate_invariant_measure(
        num_trajectories=50,
        time=30.0,
        num_bins=20
    )

    # Visualize invariant measure
    analyzer.visualize_invariant_measure(
        measure,
        save_path="C:/Users/casey/polln/simulations/novel/dynamical/invariant_measure.png"
    )

    # Test mixing property
    print("\nTesting mixing property...")
    mixing_result = analyzer.test_mixing_property(x0, time=50.0)

    print(f"Final correlation: {mixing_result['final_correlation']:.4f}")
    print(f"Mixing time: {mixing_result['mixing_time']:.4f}")
    print(f"Mixing: {mixing_result['is_mixing']}")

    analyzer.visualize_mixing(
        mixing_result,
        save_path="C:/Users/casey/polln/simulations/novel/dynamical/mixing_test.png"
    )

    # Estimate entropies
    print("\nEstimating entropies...")

    # Generate long trajectory for entropy estimation
    sol = solve_ivp(
        vf.vector_field,
        (0, 50),
        x0,
        t_eval=np.linspace(0, 50, 5000),
        method='RK45'
    )
    trajectory = sol.y.T

    ks_entropy = analyzer.estimate_ks_entropy(trajectory)
    print(f"KS Entropy: {ks_entropy:.4f}")

    metric_entropy = analyzer.estimate_metric_entropy(trajectory)
    print(f"Metric Entropy: {metric_entropy:.4f}")

    topological_entropy = analyzer.estimate_topological_entropy(trajectory)
    print(f"Topological Entropy: {topological_entropy:.4f}")

    # Ergodic decomposition
    print("\nPerforming ergodic decomposition...")
    components = analyzer.ergodic_decomposition(num_trajectories=30)
    print(f"Number of ergodic components: {len(components)}")

    return {
        'analyzer': analyzer,
        'birkhoff_result': birkhoff_result,
        'invariant_measure': measure,
        'mixing_result': mixing_result,
        'entropies': {
            'ks': ks_entropy,
            'metric': metric_entropy,
            'topological': topological_entropy
        },
        'components': components,
        'derivation': derivation
    }


if __name__ == "__main__":
    results = analyze_ergodic_properties()
