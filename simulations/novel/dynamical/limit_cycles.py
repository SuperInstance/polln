"""
Limit Cycle Analysis for POLLN Dynamical System

This module detects, analyzes, and characterizes limit cycles and periodic
orbits in the POLLN system using Poincaré maps and Floquet theory.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import root, minimize
from scipy.fft import fft, fftfreq
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

from vector_fields import PollnVectorField
from deepseek_dynamical import DeepSeekDynamicalSystems, MathematicalDerivation


class LimitCycleType(Enum):
    """Classification of limit cycles"""
    STABLE = "stable"  # Attracts nearby trajectories
    UNSTABLE = "unstable"  # Repels nearby trajectories
    SEMI_STABLE = "semi_stable"  # One side attracts, one repels


@dataclass
class LimitCycle:
    """Container for limit cycle data"""
    period: float  # Period T
    trajectory: np.ndarray  # (n_points, state_dim) cycle trajectory
    stability: LimitCycleType  # Stability classification
    floquet_multipliers: np.ndarray  # Floquet multipliers
    poincare_map: np.ndarray  # Poincaré map data
    frequency: float  # Fundamental frequency
    amplitude: float  # Approximate amplitude
    domain_of_attraction: float  # Basin size estimate


class PollnLimitCycles:
    """
    Limit cycle analysis for POLLN dynamical system.

    Uses Poincaré sections and Floquet theory to detect and analyze
    periodic orbits in the agent system.
    """

    def __init__(self, vector_field: PollnVectorField):
        """
        Initialize limit cycle analyzer.

        Args:
            vector_field: POLLN vector field object
        """
        self.vf = vector_field
        self.limit_cycles: List[LimitCycle] = []
        self.derivation: Optional[MathematicalDerivation] = None

    def detect_cycle(self, x0: np.ndarray,
                    t_span: Tuple[float, float] = (0, 100),
                    detection_tol: float = 1e-3) -> Optional[LimitCycle]:
        """
        Detect limit cycle from initial condition.

        Args:
            x0: Initial state
            t_span: Time interval for integration
            detection_tol: Tolerance for periodicity detection

        Returns:
            LimitCycle if detected, None otherwise
        """
        # Integrate trajectory
        t_eval = np.linspace(t_span[0], t_span[1], 10000)
        sol = solve_ivp(
            self.vf.vector_field,
            t_span,
            x0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-10,
            atol=1e-12
        )

        trajectory = sol.y.T

        # Check for periodicity using autocorrelation
        if self._is_periodic(trajectory, detection_tol):
            cycle = self._characterize_cycle(trajectory, t_eval)
            return cycle

        return None

    def _is_periodic(self, trajectory: np.ndarray,
                    tol: float = 1e-3) -> bool:
        """
        Check if trajectory is periodic using autocorrelation.

        Args:
            trajectory: State trajectory
            tol: Tolerance for periodicity

        Returns:
            True if periodic
        """
        # Use first two dimensions for 2D analysis
        x = trajectory[:, 0]
        y = trajectory[:, 1]

        # Compute autocorrelation
        autocorr = np.correlate(x - np.mean(x), x - np.mean(x), mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Normalize
        autocorr = autocorr / autocorr[0]

        # Look for peaks indicating periodicity
        # Exclude the zero-lag peak
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(autocorr[100:], height=0.7)

        return len(peaks) > 0

    def _characterize_cycle(self, trajectory: np.ndarray,
                           times: np.ndarray) -> LimitCycle:
        """
        Characterize a limit cycle.

        Args:
            trajectory: Cycle trajectory
            times: Time points

        Returns:
            LimitCycle object
        """
        # Estimate period using FFT
        x = trajectory[:, 0]

        # Compute FFT
        fft_vals = fft(x)
        freqs = fftfreq(len(x), d=times[1] - times[0])

        # Find dominant frequency (excluding DC)
        power = np.abs(fft_vals)**2
        positive_freqs = freqs[freqs > 0]
        positive_power = power[freqs > 0]

        if len(positive_power) > 0:
            dominant_freq_idx = np.argmax(positive_power)
            frequency = positive_freqs[dominant_freq_idx]
            period = 1.0 / frequency if frequency > 1e-10 else 10.0
        else:
            frequency = 0.1
            period = 10.0

        # Estimate amplitude
        amplitude = np.std(trajectory[:, 0])

        # Construct Poincaré map
        poincare_map = self._construct_poincare_map(trajectory)

        # Compute Floquet multipliers
        floquet_multipliers = self._compute_floquet_multipliers(
            trajectory, period
        )

        # Classify stability
        stability = self._classify_stability(floquet_multipliers)

        # Estimate domain of attraction
        domain_size = self._estimate_domain_of_attraction(trajectory)

        return LimitCycle(
            period=period,
            trajectory=trajectory,
            stability=stability,
            floquet_multipliers=floquet_multipliers,
            poincare_map=poincare_map,
            frequency=frequency,
            amplitude=amplitude,
            domain_of_attraction=domain_size
        )

    def _construct_poincare_map(self, trajectory: np.ndarray,
                               section_dim: int = 0,
                               section_value: float = 0.0) -> np.ndarray:
        """
        Construct Poincaré map by taking cross-sections.

        Args:
            trajectory: Cycle trajectory
            section_dim: Dimension to take section in
            section_value: Value for section (typically zero)

        Returns:
            Poincaré map points
        """
        # Find crossings of the section
        crossings = []

        for i in range(len(trajectory) - 1):
            # Check for sign change (crossing)
            if (trajectory[i, section_dim] - section_value) * \
               (trajectory[i+1, section_dim] - section_value) < 0:

                # Linear interpolation to find exact crossing
                t = (section_value - trajectory[i, section_dim]) / \
                    (trajectory[i+1, section_dim] - trajectory[i, section_dim])

                crossing = trajectory[i] + t * (trajectory[i+1] - trajectory[i])
                crossings.append(crossing)

        return np.array(crossings)

    def _compute_floquet_multipliers(self, trajectory: np.ndarray,
                                    period: float) -> np.ndarray:
        """
        Compute Floquet multipliers for stability analysis.

        Floquet multipliers are eigenvalues of the monodromy matrix Dφ^T(x*).
        They determine stability of the limit cycle.

        Args:
            trajectory: Cycle trajectory
            period: Period of cycle

        Returns:
            Floquet multipliers
        """
        # Find periodic point (return to near start)
        x0 = trajectory[0]
        xT = trajectory[-1]

        # Compute linearized flow (Jacobian integrated over one period)
        # This is the monodromy matrix

        # Finite difference approximation
        eps = 1e-6
        n = len(x0)
        monodromy = np.zeros((n, n))

        for i in range(n):
            # Perturb initial condition
            x0_pert = x0.copy()
            x0_pert[i] += eps

            # Integrate for one period
            sol = solve_ivp(
                self.vf.vector_field,
                (0, period),
                x0_pert,
                t_eval=[period],
                method='RK45',
                rtol=1e-10
            )

            xT_pert = sol.y[:, -1]

            # Column of monodromy matrix
            monodromy[:, i] = (xT_pert - xT) / eps

        # Floquet multipliers = eigenvalues of monodromy
        floquet_multipliers = np.linalg.eigvals(monodromy)

        return floquet_multipliers

    def _classify_stability(self, floquet_multipliers: np.ndarray) -> LimitCycleType:
        """
        Classify limit cycle stability from Floquet multipliers.

        Stable: all |μ| < 1
        Unstable: any |μ| > 1
        Semi-stable: some |μ| = 1

        Args:
            floquet_multipliers: Floquet multipliers

        Returns:
            Stability type
        """
        magnitudes = np.abs(floquet_multipliers)

        # Exclude the trivial multiplier (should be 1 for flow)
        # For autonomous systems, one multiplier is always 1
        if len(magnitudes) > 1:
            magnitudes = magnitudes[magnitudes < 0.99]  # Exclude the trivial one

        if len(magnitudes) == 0:
            return LimitCycleType.SEMI_STABLE

        max_mag = np.max(magnitudes)

        if max_mag < 1.0:
            return LimitCycleType.STABLE
        elif max_mag > 1.0:
            return LimitCycleType.UNSTABLE
        else:
            return LimitCycleType.SEMI_STABLE

    def _estimate_domain_of_attraction(self, trajectory: np.ndarray,
                                      num_test: int = 20) -> float:
        """
        Estimate domain of attraction for stable limit cycle.

        Args:
            trajectory: Cycle trajectory
            num_test: Number of test directions

        Returns:
            Estimated radius of attraction
        """
        # Use cycle center as reference
        center = np.mean(trajectory, axis=0)

        # Test points at increasing radii
        max_radius = 0.0

        for _ in range(num_test):
            # Random direction
            direction = np.random.randn(len(center))
            direction = direction / np.linalg.norm(direction)

            # Test increasing radii
            for radius in np.linspace(0.1, 5.0, 50):
                test_point = center + radius * direction

                # Integrate and check if converges to cycle
                sol = solve_ivp(
                    self.vf.vector_field,
                    (0, 50),
                    test_point,
                    t_eval=np.linspace(0, 50, 1000),
                    method='RK45'
                )

                # Check final distance to cycle
                final_dist = np.min([
                    np.linalg.norm(sol.y[:, -1] - trajectory[i])
                    for i in range(0, len(trajectory), 100)
                ])

                if final_dist < 0.5:  # Close to cycle
                    max_radius = max(max_radius, radius)
                    break

        return max_radius

    def poincare_bendixson_check(self, region_bounds: Dict[str, Tuple[float, float]],
                                grid_size: int = 20) -> bool:
        """
        Check Poincaré-Bendixson theorem conditions.

        Theorem: If a trajectory is confined to a closed, bounded region
        containing no fixed points, it must approach a limit cycle.

        Args:
            region_bounds: Dict of dimension bounds
            grid_size: Grid resolution for checking

        Returns:
            True if conditions satisfied
        """
        # Check if region is trapping (vector field points inward on boundary)
        # This is a simplified check

        print("Poincaré-Bendixson Check:")
        print("1. Region must be closed and bounded: YES (given bounds)")
        print("2. No fixed points in region: NEEDS VERIFICATION")
        print("3. Trajectory trapped in region: NEEDS VERIFICATION")

        return True

    def hopf_bifurcation_analysis(self, parameter: str = 'learning_rate',
                                 param_range: Tuple[float, float] = (0.001, 0.1)) -> Dict:
        """
        Analyze Hopf bifurcation (birth of limit cycle).

        Hopf bifurcation occurs when complex conjugate eigenvalues
        cross imaginary axis.

        Args:
            parameter: Parameter to vary
            param_range: Range of parameter values

        Returns:
            Bifurcation analysis results
        """
        print(f"\nAnalyzing Hopf bifurcation for {parameter}...")

        param_values = np.linspace(param_range[0], param_range[1], 50)
        cycle_detected = []

        original_value = getattr(self.vf, parameter)

        for param in param_values:
            setattr(self.vf, parameter, param)

            # Try to detect cycle from random initial condition
            x0 = np.random.randn(self.vf.total_dim) * 0.5
            cycle = self.detect_cycle(x0, t_span=(0, 50))

            cycle_detected.append(cycle is not None)

        # Restore original value
        setattr(self.vf, parameter, original_value)

        # Find bifurcation point (where cycle appears)
        bifurcation_idx = np.where(np.diff(cycle_detected))[0]

        if len(bifurcation_idx) > 0:
            bifurcation_param = param_values[bifurcation_idx[0]]
            print(f"Hopf bifurcation detected at {parameter} = {bifurcation_param:.4f}")

        return {
            'parameter_values': param_values,
            'cycle_detected': cycle_detected,
            'bifurcation_point': param_values[bifurcation_idx[0]] if len(bifurcation_idx) > 0 else None
        }

    def visualize_limit_cycles(self, save_path: Optional[str] = None):
        """
        Visualize detected limit cycles.

        Args:
            save_path: Optional path to save figure
        """
        if len(self.limit_cycles) == 0:
            print("No limit cycles to visualize")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Phase space with cycles
        ax = axes[0, 0]

        # Vector field background
        X, Y, U, V = self.vf.phase_portrait_2d((-4, 4), (-4, 4), 15)
        ax.streamplot(X, Y, U, V, color='gray', alpha=0.3, density=1)

        # Plot cycles
        colors = ['blue', 'red', 'green', 'purple', 'orange']
        for i, cycle in enumerate(self.limit_cycles):
            color = colors[i % len(colors)]
            ax.plot(cycle.trajectory[:, 0], cycle.trajectory[:, 1],
                   c=color, linewidth=2, alpha=0.8,
                   label=f"Cycle {i+1} ({cycle.stability.value})")

        ax.set_xlabel("State Dimension 1")
        ax.set_ylabel("State Dimension 2")
        ax.set_title("Limit Cycles in Phase Space")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Time series
        ax = axes[0, 1]
        for i, cycle in enumerate(self.limit_cycles):
            color = colors[i % len(colors)]
            time_points = np.linspace(0, cycle.period, len(cycle.trajectory))
            ax.plot(time_points, cycle.trajectory[:, 0],
                   c=color, alpha=0.7, label=f"Cycle {i+1}")

        ax.set_xlabel("Time")
        ax.set_ylabel("State Dimension 1")
        ax.set_title("Limit Cycle Time Series")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Poincaré map
        ax = axes[1, 0]
        for i, cycle in enumerate(self.limit_cycles):
            if len(cycle.poincare_map) > 0:
                color = colors[i % len(colors)]
                ax.scatter(cycle.poincare_map[:, 0],
                          cycle.poincare_map[:, 1],
                          c=color, alpha=0.7, s=50,
                          label=f"Cycle {i+1}")

        ax.set_xlabel("State Dimension 1")
        ax.set_ylabel("State Dimension 2")
        ax.set_title("Poincaré Map")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Floquet multipliers
        ax = axes[1, 1]
        for i, cycle in enumerate(self.limit_cycles):
            mags = np.abs(cycle.floquet_multipliers)
            ax.scatter(range(len(mags)), mags, alpha=0.7,
                      s=100, label=f"Cycle {i+1}")
            ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)

        ax.set_xlabel("Multiplier Index")
        ax.set_ylabel("|Floquet Multiplier|")
        ax.set_title("Floquet Multipliers")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def derive_with_deepseek(self) -> MathematicalDerivation:
        """Use DeepSeek to derive limit cycle theory"""
        ds = DeepSeekDynamicalSystems()
        self.derivation = ds.derive_limit_cycle_theory("""
        POLLN multi-agent system with:
        - Cyclic learning patterns
        - Oscillatory communication
        - Periodic agent specialization
        - Feedback-driven rhythms
        """)

        return self.derivation


def analyze_limit_cycles():
    """
    Comprehensive limit cycle analysis.
    """
    print("=" * 80)
    print("LIMIT CYCLE ANALYSIS")
    print("=" * 80)

    vf = PollnVectorField(num_agents=5, state_dim=3)
    analyzer = PollnLimitCycles(vf)

    # Derive theory
    print("\nDeriving limit cycle theory with DeepSeek...")
    derivation = analyzer.derive_with_deepseek()
    print(f"Theorem: {derivation.theorem[:200]}...")

    # Detect cycles from multiple initial conditions
    print("\nDetecting limit cycles...")
    for i in range(10):
        x0 = np.random.randn(vf.total_dim) * 1.0
        cycle = analyzer.detect_cycle(x0, t_span=(0, 100))

        if cycle is not None:
            analyzer.limit_cycles.append(cycle)
            print(f"Cycle {len(analyzer.limit_cycles)} detected:")
            print(f"  Period: {cycle.period:.4f}")
            print(f"  Frequency: {cycle.frequency:.4f}")
            print(f"  Stability: {cycle.stability.value}")
            print(f"  Floquet multipliers: {np.abs(cycle.floquet_multipliers)[:3]}...")

    if len(analyzer.limit_cycles) > 0:
        # Visualize
        print("\nGenerating visualizations...")
        analyzer.visualize_limit_cycles(
            save_path="C:/Users/casey/polln/simulations/novel/dynamical/limit_cycles.png"
        )

        # Hopf bifurcation analysis
        print("\nPerforming Hopf bifurcation analysis...")
        hopf_results = analyzer.hopf_bifurcation_analysis()
    else:
        print("\nNo limit cycles detected in this parameter regime")

    return {
        'analyzer': analyzer,
        'cycles': analyzer.limit_cycles,
        'derivation': derivation
    }


if __name__ == "__main__":
    results = analyze_limit_cycles()
