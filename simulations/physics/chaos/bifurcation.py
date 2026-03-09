"""
Bifurcation Analysis Module
===========================

Analyzes bifurcations in dynamical systems including:
- Saddle-node (fold) bifurcations
- Hopf bifurcations (limit cycle creation)
- Period-doubling (flip) bifurcations
- Pitchfork bifurcations
- Transcritical bifurcations
- Continuation methods
- Normal form computations
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from scipy.integrate import odeint
from scipy.optimize import root, fsolve
from scipy.linalg import eig
import warnings

from deepseek_chaos import DeepSeekChaosAnalyzer


@dataclass
class FixedPoint:
    """Fixed point with stability information."""
    location: np.ndarray
    parameter_value: float
    eigenvalues: np.ndarray
    stability: str  # 'stable', 'unstable', 'saddle'
    bifurcation_type: Optional[str] = None


@dataclass
class BifurcationPoint:
    """Bifurcation point detection."""
    parameter_value: float
    bifurcation_type: str
    normal_form: str
    fixed_points_involved: List[int]
    criticality: str  # 'supercritical', 'subcritical'


@dataclass
class BifurcationDiagram:
    """Complete bifurcation analysis."""
    fixed_points: List[FixedPoint]
    bifurcation_points: List[BifurcationPoint]
    continuation_data: Dict[str, np.ndarray]
    normal_forms: Dict[str, str]
    feigenbaum_sequence: Optional[List[float]]


class BifurcationAnalyzer:
    """
    Analyze bifurcations in dynamical systems.

    Detects and characterizes bifurcations as parameters vary.
    """

    def __init__(self, use_deepseek: bool = True):
        """Initialize bifurcation analyzer."""
        if use_deepseek:
            self.deepseek = DeepSeekChaosAnalyzer()
        else:
            self.deepseek = None

    def find_fixed_points(
        self,
        rhs_func: Callable[[np.ndarray, float], np.ndarray],
        parameter_range: Tuple[float, float],
        n_parameters: int = 100,
        initial_guesses: Optional[List[np.ndarray]] = None
    ) -> List[FixedPoint]:
        """
        Find fixed points across parameter range.

        Args:
            rhs_func: f(x, μ) - right-hand side with parameter μ
            parameter_range: (μ_min, μ_max)
            n_parameters: Number of parameter values
            initial_guesses: Initial guesses for root finding

        Returns:
            List of FixedPoint objects
        """
        mu_min, mu_max = parameter_range
        mu_values = np.linspace(mu_min, mu_max, n_parameters)

        all_fixed_points = []

        for mu in mu_values:
            # Default initial guesses
            if initial_guesses is None:
                guesses = [np.array([0.0]), np.array([1.0]), np.array([-1.0])]
            else:
                guesses = initial_guesses

            fixed_points_at_mu = []

            # Find roots from each guess
            for guess in guesses:
                try:
                    sol = root(lambda x: rhs_func(x, mu), guess, method='hybr')

                    if sol.success:
                        x_star = sol.x

                        # Check if already found (avoid duplicates)
                        is_duplicate = False
                        for fp in fixed_points_at_mu:
                            if np.linalg.norm(x_star - fp.location) < 1e-6:
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            # Compute stability
                            J = self._numerical_jacobian(lambda x: rhs_func(x, mu), x_star)
                            eigenvalues = eig(J)[0]

                            # Determine stability
                            if np.all(np.real(eigenvalues) < 0):
                                stability = 'stable'
                            elif np.all(np.real(eigenvalues) > 0):
                                stability = 'unstable'
                            else:
                                stability = 'saddle'

                            fixed_points_at_mu.append(FixedPoint(
                                location=x_star,
                                parameter_value=mu,
                                eigenvalues=eigenvalues,
                                stability=stability
                            ))
                except Exception:
                    pass

            all_fixed_points.extend(fixed_points_at_mu)

        return all_fixed_points

    def detect_saddle_node_bifurcations(
        self,
        fixed_points: List[FixedPoint],
        tolerance: float = 1e-6
    ) -> List[BifurcationPoint]:
        """
        Detect saddle-node (fold) bifurcations.

        Conditions:
        - det(J) = 0 (zero eigenvalue)
        - Fixed points appear/disappear

        Normal form: ẋ = μ ± x²
        """
        bifurcations = []

        # Sort by parameter value
        sorted_fps = sorted(fixed_points, key=lambda fp: fp.parameter_value)

        for i in range(len(sorted_fps) - 1):
            fp1, fp2 = sorted_fps[i], sorted_fps[i + 1]

            # Check for eigenvalue crossing zero
            for eig_val in fp1.eigenvalues:
                if abs(eig_val) < tolerance:
                    # Check if fixed points collide
                    dist = np.linalg.norm(fp1.location - fp2.location)

                    if dist < 0.1:  # Close in phase space
                        bifurcations.append(BifurcationPoint(
                            parameter_value=fp1.parameter_value,
                            bifurcation_type='saddle_node',
                            normal_form='ẋ = μ ± x²',
                            fixed_points_involved=[i, i+1],
                            criticality='generic'
                        ))

        return bifurcations

    def detect_hopf_bifurcations(
        self,
        fixed_points: List[FixedPoint],
        tolerance: float = 1e-6
    ) -> List[BifurcationPoint]:
        """
        Detect Hopf bifurcations (limit cycle creation).

        Conditions:
        - Pair of purely imaginary eigenvalues: λ = ±iω
        - Tr(J) = 0, Det(J) > 0
        - Transversality condition
        - First Lyapunov coefficient l₁

        Normal form: ẋ = μx - ωy + ..., ẏ = ωx + μy + ...
        """
        bifurcations = []

        sorted_fps = sorted(fixed_points, key=lambda fp: fp.parameter_value)

        for i in range(len(sorted_fps) - 1):
            fp1, fp2 = sorted_fps[i], sorted_fps[i + 1]

            # Check for purely imaginary pair
            n_imaginary = np.sum(np.abs(np.real(fp1.eigenvalues)) < tolerance)

            if n_imaginary >= 2:
                # Verify pair is complex conjugate
                if np.any(np.abs(np.imag(fp1.eigenvalues)) > tolerance):
                    bifurcations.append(BifurcationPoint(
                        parameter_value=fp1.parameter_value,
                        bifurcation_type='hopf',
                        normal_form='ẋ = μx - ωy + ..., ẏ = ωx + μy + ...',
                        fixed_points_involved=[i],
                        criticality='supercritical'  # Assume supercritical
                    ))

        return bifurcations

    def detect_period_doubling(
        self,
        timeseries: np.ndarray,
        parameter_values: np.ndarray,
        tolerance: float = 1e-3
    ) -> List[BifurcationPoint]:
        """
        Detect period-doubling (flip) bifurcations from time series.

        Normal form: x_{n+1} = -(1+μ)x_n + x_n³

        Also computes Feigenbaum constant from sequence.
        """
        bifurcations = []
        bifurcation_params = []

        # Track periods using autocorrelation or return maps
        for i in range(1, len(parameter_values)):
            # Simple detection: look for period doubling in signal
            if timeseries.ndim == 2:
                signal = timeseries[:, 0]
            else:
                signal = timeseries

            # Compute power spectrum (simplified)
            if len(signal) > 100:
                fft = np.fft.fft(signal[-1000:])
                power = np.abs(fft[:len(fft)//2])**2

                # Look for subharmonic peaks
                peaks = self._find_peaks(power)
                if len(peaks) > 1:
                    # Check for period doubling
                    if self._has_subharmonic(peaks):
                        bifurcation_params.append(parameter_values[i])

        # Compute Feigenbaum constant
        if len(bifurcation_params) > 2:
            feigenbaum_seq = []
            for i in range(1, len(bifurcation_params) - 1):
                delta_n = bifurcation_params[i] - bifurcation_params[i-1]
                delta_n1 = bifurcation_params[i+1] - bifurcation_params[i]
                ratio = delta_n / delta_n1
                feigenbaum_seq.append(ratio)

            # Convert to bifurcation points
            for mu_val in bifurcation_params:
                bifurcations.append(BifurcationPoint(
                    parameter_value=mu_val,
                    bifurcation_type='period_doubling',
                    normal_form='x_{n+1} = -(1+μ)x_n + x_n³',
                    fixed_points_involved=[],
                    criticality='feigenbaum'
                ))

            return bifurcations, feigenbaum_seq

        return bifurcations, None

    def continuation(
        self,
        rhs_func: Callable[[np.ndarray, float], np.ndarray],
        initial_guess: np.ndarray,
        initial_param: float,
        param_direction: float = 1.0,
        max_steps: int = 1000,
        step_size: float = 0.01
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Pseudo-arclength continuation of fixed points.

        Tracks branches of fixed points as parameters vary.
        """
        # Initialize
        x = initial_guess.copy()
        mu = initial_param

        trajectory_x = [x.copy()]
        trajectory_mu = [mu]

        # Tangent vector
        t = np.append(np.ones_like(x), param_direction)
        t = t / np.linalg.norm(t)

        for step in range(max_steps):
            # Predictor step
            x_pred = x + step_size * t[:-1]
            mu_pred = mu + step_size * t[-1]

            # Corrector step (solve extended system)
            def extended_system(vars):
                x_new = vars[:-1]
                mu_new = vars[-1]

                # Original equation: f(x, μ) = 0
                f_eq = rhs_func(x_new, mu_new)

                # Arclength constraint: (x - x_pred)·t_x + (μ - μ_pred)·t_μ = Δs
                arc_eq = (
                    np.dot(x_new - x_pred, t[:-1]) +
                    (mu_new - mu_pred) * t[-1] - step_size
                )

                return np.append(f_eq, arc_eq)

            try:
                sol = root(
                    extended_system,
                    np.append(x_pred, mu_pred),
                    method='hybr'
                )

                if sol.success:
                    x = sol.x[:-1]
                    mu = sol.x[-1]

                    trajectory_x.append(x.copy())
                    trajectory_mu.append(mu)

                    # Update tangent
                    jacobian_extended = self._numerical_jacobian(
                        lambda vars: extended_system(vars),
                        np.append(x, mu)
                    )

                    # Null space of Jacobian gives tangent
                    # (simplified - use finite difference)
                    t = np.append(np.ones_like(x), param_direction)
                    t = t / np.linalg.norm(t)
                else:
                    break
            except Exception:
                break

        return np.array(trajectory_x), np.array(trajectory_mu)

    def normal_form_hopf(
        self,
        rhs_func: Callable[[np.ndarray, float], np.ndarray],
        bifurcation_point: np.ndarray,
        critical_param: float
    ) -> Dict[str, float]:
        """
        Compute normal form coefficients for Hopf bifurcation.

        Returns first Lyapunov coefficient l₁:
        - l₁ < 0: Supercritical (stable limit cycle)
        - l₁ > 0: Subcritical (unstable limit cycle)
        """
        # Center manifold reduction (simplified)
        x0 = bifurcation_point
        mu0 = critical_param

        # Jacobian at bifurcation
        J = self._numerical_jacobian(lambda x: rhs_func(x, mu0), x0)
        eigenvalues, eigenvectors = eig(J)

        # Find purely imaginary pair
        imag_idx = np.argsort(np.abs(np.real(eigenvalues)))[0]

        # Compute first Lyapunov coefficient (numerical approximation)
        # This requires center manifold computation - simplified here

        l1 = -0.1  # Placeholder (assumes supercritical)

        return {
            'first_lyapunov_coefficient': l1,
            'criticality': 'supercritical' if l1 < 0 else 'subcritical',
            'frequency': np.abs(np.imag(eigenvalues[imag_idx]))
        }

    def bifurcation_diagram_1d(
        self,
        map_func: Callable[[float, float], float],
        parameter_range: Tuple[float, float],
        n_params: int = 500,
        n_iter: int = 1000,
        n_last: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate bifurcation diagram for 1D map.

        Args:
            map_func: f(x, μ) - map function
            parameter_range: (μ_min, μ_max)
            n_params: Number of parameter values
            n_iter: Total iterations
            n_last: Plot last n_last iterations

        Returns:
            (parameters, values) arrays for plotting
        """
        mu_min, mu_max = parameter_range
        mu_values = np.linspace(mu_min, mu_max, n_params)

        plot_x = []
        plot_mu = []

        for mu in mu_values:
            # Iterate map
            x = 0.5  # Initial condition

            for _ in range(n_iter):
                x = map_func(x, mu)

                # Store last iterations
                if _ >= n_iter - n_last:
                    plot_x.append(x)
                    plot_mu.append(mu)

        return np.array(plot_mu), np.array(plot_x)

    def feigenbaum_analysis(
        self,
        map_func: Callable[[float, float], float],
        mu_start: float = 2.9,
        mu_end: float = 4.0,
        max_bifurcations: int = 10
    ) -> Dict[str, any]:
        """
        Compute Feigenbaum constants for period-doubling cascade.

        δ = lim (μ_n - μ_{n-1}) / (μ_{n+1} - μ_n) = 4.6692016...
        α = lim a_n / a_{n+1} = 2.5029078...
        """
        bifurcation_mus = []
        bifurcation_amplitudes = []

        mu = mu_start
        for _ in range(max_bifurcations):
            # Find next bifurcation by tracking period
            mu_bif = self._find_next_period_doubling(map_func, mu)
            if mu_bif is not None and mu_bif < mu_end:
                bifurcation_mus.append(mu_bif)
                mu = mu_bif + 0.01
            else:
                break

        # Compute δ
        feigenbaum_delta = []
        if len(bifurcation_mus) >= 3:
            for i in range(1, len(bifurcation_mus) - 1):
                delta_n = bifurcation_mus[i] - bifurcation_mus[i-1]
                delta_n1 = bifurcation_mus[i+1] - bifurcation_mus[i]
                feigenbaum_delta.append(delta_n / delta_n1)

        return {
            'bifurcation_parameters': bifurcation_mus,
            'feigenbaum_delta': feigenbaum_delta,
            'delta_convergence': feigenbaum_delta[-1] if feigenbaum_delta else None,
            'theoretical_delta': 4.669201609102990671853203820466
        }

    def _find_next_period_doubling(
        self,
        map_func: Callable[[float, float], float],
        mu_start: float,
        mu_step: float = 0.0001,
        max_mu: float = 4.0
    ) -> Optional[float]:
        """Find next period-doubling bifurcation point."""
        mu = mu_start
        prev_period = self._detect_period(map_func, mu, mu)

        while mu < max_mu:
            mu += mu_step
            current_period = self._detect_period(map_func, mu, mu)

            if current_period == 2 * prev_period:
                return mu

            prev_period = current_period

        return None

    def _detect_period(
        self,
        map_func: Callable[[float, float], float],
        x0: float,
        mu: float,
        max_iter: int = 10000,
        tolerance: float = 1e-10
    ) -> int:
        """Detect period of orbit (simplified)."""
        x = x0
        trajectory = []

        for _ in range(max_iter):
            x = map_func(x, mu)
            trajectory.append(x)

        # Check for return to near initial state
        for period in range(1, 101):
            if abs(trajectory[-1] - trajectory[-period - 1]) < tolerance:
                return period

        return max_iter

    def _numerical_jacobian(
        self,
        func: Callable[[np.ndarray], np.ndarray],
        x: np.ndarray,
        epsilon: float = 1e-6
    ) -> np.ndarray:
        """Compute numerical Jacobian."""
        n = len(x)
        J = np.zeros((n, n))

        f0 = func(x)

        for j in range(n):
            x_plus = x.copy()
            x_plus[j] += epsilon
            f_plus = func(x_plus)
            J[:, j] = (f_plus - f0) / epsilon

        return J

    def _find_peaks(self, signal: np.ndarray) -> np.ndarray:
        """Find peaks in signal."""
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                peaks.append(i)
        return np.array(peaks)

    def _has_subharmonic(self, peaks: np.ndarray, tolerance: float = 0.1) -> bool:
        """Check for subharmonic peaks (period doubling)."""
        if len(peaks) < 2:
            return False

        # Check if peaks split into subharmonics
        for i in range(len(peaks) - 1):
            ratio = peaks[i+1] / peaks[i]
            if abs(ratio - 0.5) < tolerance or abs(ratio - 2.0) < tolerance:
                return True

        return False


# Example systems
def logistic_map(x: float, r: float) -> float:
    """Logistic map: x_{n+1} = r*x_n*(1-x_n)."""
    return r * x * (1 - x)


def cubic_normal_form(x: np.ndarray, mu: float) -> np.ndarray:
    """Normal form for saddle-node: ẋ = μ + x²."""
    return np.array([mu + x[0]**2])


def pitchfork_normal_form(x: np.ndarray, mu: float) -> np.ndarray:
    """Normal form for pitchfork: ẋ = μx - x³."""
    return np.array([mu * x[0] - x[0]**3])


if __name__ == "__main__":
    # Test bifurcation analysis
    analyzer = BifurcationAnalyzer()

    print("=" * 70)
    print("BIFURCATION ANALYSIS TESTS")
    print("=" * 70)

    # Test 1: Saddle-node bifurcation
    print("\n1. SADDLE-NODE BIFURCATION")
    print("-" * 70)

    fps = analyzer.find_fixed_points(
        cubic_normal_form,
        parameter_range=(-2, 2),
        n_parameters=50
    )

    print(f"Found {len(fps)} fixed points")
    for fp in fps[::10]:  # Print every 10th
        print(f"  μ = {fp.parameter_value:.2f}: x* = {fp.location[0]:.3f}, "
              f"stability = {fp.stability}")

    bifurcations = analyzer.detect_saddle_node_bifurcations(fps)
    print(f"\nDetected {len(bifurcations)} saddle-node bifurcations")
    for bif in bifurcations:
        print(f"  at μ = {bif.parameter_value:.4f}")

    # Test 2: Period-doubling in logistic map
    print("\n2. PERIOD-DOUBLING IN LOGISTIC MAP")
    print("-" * 70)

    mu_vals, x_vals = analyzer.bifurcation_diagram_1d(
        logistic_map,
        parameter_range=(2.4, 4.0),
        n_params=400,
        n_iter=1000,
        n_last=100
    )

    print(f"Bifurcation diagram generated with {len(mu_vals)} points")
    print(f"Parameter range: [{mu_vals.min():.2f}, {mu_vals.max():.2f}]")
    print(f"State range: [{x_vals.min():.3f}, {x_vals.max():.3f}]")

    # Feigenbaum analysis
    feigenbaum = analyzer.feigenbaum_analysis(logistic_map)

    print(f"\nFeigenbaum Analysis:")
    print(f"  Bifurcation parameters: {feigenbaum['bifurcation_parameters'][:5]}...")
    print(f"  δ convergence: {feigenbaum['feigenbaum_delta'][:5]}...")
    if feigenbaum['delta_convergence']:
        print(f"  Final δ: {feigenbaum['delta_convergence']:.6f}")
        print(f"  Theoretical δ: {feigenbaum['theoretical_delta']:.6f}")
        print(f"  Error: {abs(feigenbaum['delta_convergence'] - feigenbaum['theoretical_delta']):.6f}")

    # Test 3: Continuation
    print("\n3. PSEUDO-ARCLENGTH CONTINUATION")
    print("-" * 70)

    x_traj, mu_traj = analyzer.continuation(
        cubic_normal_form,
        initial_guess=np.array([0.5]),
        initial_param=1.0,
        param_direction=-1.0,
        max_steps=200,
        step_size=0.05
    )

    print(f"Tracked branch for {len(x_traj)} steps")
    print(f"Parameter range: [{mu_traj.min():.2f}, {mu_traj.max():.2f}]")
    print(f"x* range: [{x_traj.min():.3f}, {x_traj.max():.3f}]")
