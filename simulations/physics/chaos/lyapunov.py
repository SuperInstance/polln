"""
Lyapunov Exponent Computation Module
====================================

Computes complete Lyapunov spectrum for dynamical systems using:
- Wolf algorithm (continuous systems from time series)
- Rosenstein algorithm (fast LTE from small datasets)
- Kantz algorithm (local divergence rates)
- QR decomposition (complete spectrum from Jacobian)
- Benettin's algorithm (standard for ODE systems)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.integrate import odeint
from scipy.linalg import qr, expm
from scipy.spatial.distance import cdist
import warnings

from deepseek_chaos import DeepSeekChaosAnalyzer


@dataclass
class LyapunovSpectrum:
    """Container for Lyapunov spectrum results."""
    exponents: np.ndarray  # Complete spectrum [λ₁, λ₂, ..., λₙ]
    largest_exponent: float  # λ₁ (chaos indicator if > 0)
    predictability_horizon: float  # ~ 1/λ₁
    kolmogorov_sinai_entropy: float  # Sum of positive exponents
    lyapunov_dimension: float  # Kaplan-Yorke dimension
    chaos_indicated: bool  # True if λ₁ > 0
    method_used: str
    convergence: float  # Convergence metric


class LyapunovComputer:
    """
    Compute Lyapunov exponents for dynamical systems.

    Supports multiple algorithms for different data types and system sizes.
    """

    def __init__(self, use_deepseek: bool = True):
        """Initialize Lyapunov computer."""
        if use_deepseek:
            self.deepseek = DeepSeekChaosAnalyzer()
        else:
            self.deepseek = None

    def from_jacobian(
        self,
        jacobian_func: Callable[[np.ndarray], np.ndarray],
        trajectory: np.ndarray,
        dt: float = 0.01
    ) -> LyapunovSpectrum:
        """
        Compute Lyapunov spectrum using Jacobian matrix (Benettin's algorithm).

        This is the most accurate method when the Jacobian is known.

        Args:
            jacobian_func: Function J(x) returning Jacobian matrix
            trajectory: State trajectory [n_steps, n_dim]
            dt: Time step

        Returns:
            LyapunovSpectrum with complete spectrum
        """
        n_dim = trajectory.shape[1]
        n_steps = trajectory.shape[0]

        # Initialize orthonormal basis
        Q = np.eye(n_dim)
        exponents = np.zeros(n_dim)

        # Time evolution with QR decomposition
        for i in range(1, n_steps):
            x = trajectory[i-1]
            J = jacobian_func(x)

            # Evolve tangent vectors: dQ/dt = J*Q
            # Approximation: Q_new = Q + dt*J*Q
            Q_new = Q + dt * J @ Q

            # QR decomposition to maintain orthonormality
            Q_next, R = qr(Q_new)

            # Accumulate expansion rates
            exponents += np.log(np.abs(np.diag(R))) / dt

            Q = Q_next

        # Normalize by time
        T = n_steps * dt
        exponents /= T

        # Sort descending (standard convention)
        exponents = np.sort(exponents)[::-1]

        return self._create_spectrum(exponents, dt, "Benettin QR")

    def from_timeseries_wolf(
        self,
        timeseries: np.ndarray,
        dt: float = 0.01,
        max_time: float = 10.0,
        embedding_dim: Optional[int] = None
    ) -> LyapunovSpectrum:
        """
        Compute largest Lyapunov exponent using Wolf's algorithm.

        Wolf et al. (1985) - tracks divergence of nearby trajectories.

        Args:
            timeseries: 1D or multi-dimensional time series
            dt: Time step
            max_time: Maximum tracking time
            embedding_dim: Embedding dimension (auto if None)

        Returns:
            LyapunovSpectrum with largest exponent
        """
        # Ensure 2D array
        if timeseries.ndim == 1:
            timeseries = timeseries.reshape(-1, 1)

        n_dim = timeseries.shape[1]

        # Auto-detect embedding dimension if needed
        if embedding_dim is None:
            embedding_dim = self._false_nearest_neighbors(timeseries)[0]

        # Reconstruct phase space (Takens embedding)
        embedded = self._takens_embedding(timeseries, embedding_dim, tau=1)

        n_points = embedded.shape[0]

        # Find nearest neighbor (exclude temporally close points)
        min_dist = float('inf')
        neighbor_idx = 0
        min_separation = 100  # Minimum time separation

        for i in range(n_points - max_time - min_separation):
            for j in range(i + min_separation, n_points - int(max_time/dt)):
                dist = np.linalg.norm(embedded[i] - embedded[j])
                if dist < min_dist:
                    min_dist = dist
                    neighbor_idx = j

        # Track divergence
        divergences = []
        t_vals = []

        current_idx = 0
        current_neighbor = neighbor_idx
        t = 0

        while t < max_time and current_idx + 1 < n_points and current_neighbor + 1 < n_points:
            # Compute distance at next time step
            next_dist = np.linalg.norm(
                embedded[current_idx + 1] - embedded[current_neighbor + 1]
            )

            if next_dist > 0:
                divergences.append(next_dist / min_dist)
                t_vals.append(t)

            current_idx += 1
            current_neighbor += 1
            t += dt

        # Fit exponential growth: d(t) = d_0 * exp(λ*t)
        if len(divergences) > 10:
            log_div = np.log(np.array(divergences))
            coeffs = np.polyfit(t_vals, log_div, 1)
            lambda_largest = coeffs[0]
        else:
            lambda_largest = 0

        # Single exponent from Wolf
        exponents = np.array([lambda_largest] + [0] * (n_dim - 1))

        return self._create_spectrum(exponents, dt, "Wolf")

    def from_timeseries_rosenstein(
        self,
        timeseries: np.ndarray,
        dt: float = 0.01,
        max_time: float = 5.0,
        embedding_dim: Optional[int] = None
    ) -> LyapunovSpectrum:
        """
        Compute largest Lyapunov exponent using Rosenstein's algorithm.

        Rosenstein et al. (1993) - fast, works with small datasets.

        Args:
            timeseries: Time series data
            dt: Time step
            max_time: Maximum evolution time
            embedding_dim: Embedding dimension

        Returns:
            LyapunovSpectrum with largest exponent
        """
        if timeseries.ndim == 1:
            timeseries = timeseries.reshape(-1, 1)

        n_dim = timeseries.shape[1]

        # Auto-detect embedding dimension
        if embedding_dim is None:
            embedding_dim = self._false_nearest_neighbors(timeseries)[0]

        # Phase space reconstruction
        embedded = self._takens_embedding(timeseries, embedding_dim, tau=1)

        n_points = embedded.shape[0]

        # Find nearest neighbors for each point
        min_separation = int(0.1 * n_points)  # Attractor threshold
        divergences_all = []

        for i in range(n_points - int(max_time/dt)):
            # Find nearest neighbor (excluding nearby points)
            distances = np.linalg.norm(
                embedded[i] - embedded[:i-min_separation],
                axis=1
            )
            neighbor = np.argmin(distances)

            # Track divergence
            divs = []
            for k in range(int(max_time/dt)):
                if i + k < n_points and neighbor + k < n_points:
                    dist = np.linalg.norm(
                        embedded[i + k] - embedded[neighbor + k]
                    )
                    divs.append(dist)

            if len(divs) > 0:
                divergences_all.append(divs)

        # Average across all starting points
        max_len = max(len(d) for d in divergences_all)
        divergence_avg = np.zeros(max_len)

        for divs in divergences_all:
            for k, d in enumerate(divs):
                divergence_avg[k] += d

        divergence_avg /= len(divergences_all)

        # Fit line to log-linear region
        t_points = np.arange(len(divergence_avg)) * dt
        log_div = np.log(divergence_avg[divergence_avg > 0])

        if len(log_div) > 10:
            # Use linear region (exclude saturation)
            linear_region = slice(10, min(50, len(log_div)))
            coeffs = np.polyfit(t_points[linear_region], log_div[linear_region], 1)
            lambda_largest = coeffs[0]
        else:
            lambda_largest = 0

        exponents = np.array([lambda_largest] + [0] * (n_dim - 1))

        return self._create_spectrum(exponents, dt, "Rosenstein")

    def from_timeseries_kantz(
        self,
        timeseries: np.ndarray,
        dt: float = 0.01,
        epsilon: float = 0.1,
        max_time: float = 5.0,
        embedding_dim: Optional[int] = None
    ) -> LyapunovSpectrum:
        """
        Compute largest Lyapunov exponent using Kantz's algorithm.

        Kantz (1994) - local divergence rate, robust to noise.

        Args:
            timeseries: Time series data
            dt: Time step
            epsilon: Neighborhood size
            max_time: Maximum evolution time
            embedding_dim: Embedding dimension

        Returns:
            LyapunovSpectrum with largest exponent
        """
        if timeseries.ndim == 1:
            timeseries = timeseries.reshape(-1, 1)

        n_dim = timeseries.shape[1]

        if embedding_dim is None:
            embedding_dim = self._false_nearest_neighbors(timeseries)[0]

        embedded = self._takens_embedding(timeseries, embedding_dim, tau=1)
        n_points = embedded.shape[0]

        # Compute local divergence rates
        t_max = int(max_time / dt)
        S = np.zeros(t_max)

        for t_idx in range(t_max):
            sum_div = 0
            count = 0

            for i in range(n_points - t_idx - 10):
                # Find neighbors within epsilon
                distances = np.linalg.norm(
                    embedded[i] - embedded[:i-10],
                    axis=1
                )
                neighbors = np.where(distances < epsilon)[0]

                if len(neighbors) > 0:
                    # Compute divergence after time t
                    for neighbor in neighbors:
                        if neighbor + t_idx < n_points:
                            div = np.linalg.norm(
                                embedded[i + t_idx] - embedded[neighbor + t_idx]
                            )
                            sum_div += div
                            count += 1

            if count > 0:
                S[t_idx] = sum_div / count

        # Fit linear region: S(t) ~ exp(λ*t)
        t_points = np.arange(t_max) * dt
        log_S = np.log(S[S > 0])

        if len(log_S) > 10:
            linear_region = slice(5, min(30, len(log_S)))
            coeffs = np.polyfit(t_points[linear_region], log_S[linear_region], 1)
            lambda_largest = coeffs[0]
        else:
            lambda_largest = 0

        exponents = np.array([lambda_largest] + [0] * (n_dim - 1))

        return self._create_spectrum(exponents, dt, "Kantz")

    def complete_spectrum_ode(
        self,
        rhs_func: Callable[[np.ndarray, float], np.ndarray],
        jacobian_func: Callable[[np.ndarray], np.ndarray],
        initial_state: np.ndarray,
        t_span: Tuple[float, float],
        dt: float = 0.01
    ) -> LyapunovSpectrum:
        """
        Compute complete Lyapunov spectrum from ODE system.

        Uses Benettin's algorithm with variational equations.

        Args:
            rhs_func: Right-hand side of ODE: dx/dt = f(x, t)
            jacobian_func: Jacobian J(x) = ∂f/∂x
            initial_state: Initial condition
            t_span: (t_start, t_end)
            dt: Time step

        Returns:
            Complete Lyapunov spectrum
        """
        n_dim = len(initial_state)
        t_eval = np.arange(t_span[0], t_span[1], dt)

        # Integrate main trajectory
        trajectory = odeint(rhs_func, initial_state, t_eval)

        # Variational equations: dΦ/dt = J(x(t))*Φ
        # Initialize orthonormal tangent vectors
        Phi = np.eye(n_dim)
        exponents = np.zeros(n_dim)

        for i in range(1, len(t_eval)):
            x = trajectory[i-1]
            J = jacobian_func(x)

            # Evolve tangent vectors
            Phi = Phi + dt * J @ Phi

            # QR decomposition every few steps
            if i % 10 == 0:
                Q, R = qr(Phi)
                exponents += np.log(np.abs(np.diag(R))) / dt
                Phi = Q

        # Final normalization
        T = t_span[1] - t_span[0]
        exponents /= T

        # Sort descending
        exponents = np.sort(exponents)[::-1]

        return self._create_spectrum(exponents, dt, "Benettin Variational")

    def _create_spectrum(
        self,
        exponents: np.ndarray,
        dt: float,
        method: str
    ) -> LyapunovSpectrum:
        """Create LyapunovSpectrum from computed exponents."""
        # Largest exponent
        lambda_1 = exponents[0]

        # Predictability horizon: t ~ 1/λ₁
        if lambda_1 > 0:
            horizon = 1.0 / lambda_1
        else:
            horizon = float('inf')

        # Kolmogorov-Sinai entropy: sum of positive exponents
        ks_entropy = np.sum(exponents[exponents > 0])

        # Kaplan-Yorke (Lyapunov) dimension
        lyap_dim = self._kaplan_yorke_dimension(exponents)

        # Chaos indicator
        chaos = lambda_1 > 1e-10  # Numerical threshold

        # Convergence estimate (variance of recent values)
        convergence = 0.95  # Placeholder

        return LyapunovSpectrum(
            exponents=exponents,
            largest_exponent=lambda_1,
            predictability_horizon=horizon,
            kolmogorov_sinai_entropy=ks_entropy,
            lyapunov_dimension=lyap_dim,
            chaos_indicated=chaos,
            method_used=method,
            convergence=convergence
        )

    def _kaplan_yorke_dimension(self, exponents: np.ndarray) -> float:
        """
        Compute Kaplan-Yorke (Lyapunov) dimension.

        d_L = j + (λ₁ + ... + λ_j) / |λ_{j+1}|

        where j is largest integer with λ₁ + ... + λ_j > 0.
        """
        cumsum = np.cumsum(exponents)
        j = np.where(cumsum > 0)[0]

        if len(j) == 0:
            return 0.0

        j = j[-1]

        if j == len(exponents) - 1:
            return float(j + 1)

        d_lyap = j + cumsum[j] / abs(exponents[j + 1])

        return d_lyap

    def _takens_embedding(
        self,
        timeseries: np.ndarray,
        embedding_dim: int,
        tau: int = 1
    ) -> np.ndarray:
        """
        Phase space reconstruction using Takens embedding theorem.

        y_n = [x_n, x_{n-τ}, ..., x_{n-(d-1)τ}]
        """
        n = len(timeseries)
        embedded = np.zeros((n - (embedding_dim - 1) * tau, embedding_dim))

        for i in range(embedding_dim):
            embedded[:, i] = timeseries[n - (embedding_dim - 1) * tau - 1::-1][i:i + len(embedded)]

        return embedded

    def _false_nearest_neighbors(
        self,
        timeseries: np.ndarray,
        max_dim: int = 10,
        tau: int = 1
    ) -> Tuple[int, np.ndarray]:
        """
        Determine optimal embedding dimension using false nearest neighbors.

        Kennel et al. (1992) - increase dimension until false neighbors vanish.
        """
        if timeseries.ndim == 1:
            timeseries = timeseries.reshape(-1, 1)

        n = len(timeseries)
        fraction_fnn = []

        for dim in range(1, max_dim + 1):
            # Embed with dimension dim
            embedded = self._takens_embedding(timeseries, dim, tau)

            if dim < max_dim:
                # Embed with dimension dim+1
                embedded_next = self._takens_embedding(timeseries, dim + 1, tau)

                # Find nearest neighbors in dim
                nn_idx = []
                for i in range(len(embedded)):
                    distances = np.linalg.norm(
                        embedded[i] - embedded[:i],
                        axis=1
                    )
                    if len(distances) > 0:
                        nn_idx.append(np.argmin(distances))

                # Check false neighbors
                false_count = 0
                for i, nn in enumerate(nn_idx):
                    if i < len(embedded_next) and nn < len(embedded_next):
                        dist_dim = np.linalg.norm(embedded[i] - embedded[nn])
                        dist_next = np.linalg.norm(embedded_next[i] - embedded_next[nn])

                        if dist_dim > 0:
                            if dist_next / dist_dim > 10:
                                false_count += 1

                fraction = false_count / len(nn_idx) if len(nn_idx) > 0 else 0
                fraction_fnn.append(fraction)
            else:
                fraction_fnn.append(0)

        fraction_fnn = np.array(fraction_fnn)

        # Find dimension where fraction < 1%
        optimal_dim = np.where(fraction_fnn < 0.01)[0]

        if len(optimal_dim) > 0:
            return int(optimal_dim[0] + 1), fraction_fnn
        else:
            return max_dim, fraction_fnn

    def compute_all_methods(
        self,
        timeseries: np.ndarray,
        dt: float = 0.01
    ) -> Dict[str, LyapunovSpectrum]:
        """
        Compute Lyapunov exponents using all available methods.

        Useful for cross-validation and uncertainty estimation.
        """
        results = {}

        try:
            results['wolf'] = self.from_timeseries_wolf(timeseries, dt)
        except Exception as e:
            warnings.warn(f"Wolf algorithm failed: {e}")

        try:
            results['rosenstein'] = self.from_timeseries_rosenstein(timeseries, dt)
        except Exception as e:
            warnings.warn(f"Rosenstein algorithm failed: {e}")

        try:
            results['kantz'] = self.from_timeseries_kantz(timeseries, dt)
        except Exception as e:
            warnings.warn(f"Kantz algorithm failed: {e}")

        return results

    def compare_methods(
        self,
        timeseries: np.ndarray,
        dt: float = 0.01
    ) -> Dict[str, Any]:
        """
        Compare different Lyapunov exponent computation methods.
        """
        results = self.compute_all_methods(timeseries, dt)

        comparison = {
            "methods": list(results.keys()),
            "largest_exponents": {
                method: spectrum.largest_exponent
                for method, spectrum in results.items()
            },
            "chaos_indicated": {
                method: spectrum.chaos_indicated
                for method, spectrum in results.items()
            },
            "predictability_horizons": {
                method: spectrum.predictability_horizon
                for method, spectrum in results.items()
            }
        }

        # Consensus
        lambda_values = [s.largest_exponent for s in results.values()]
        comparison['consensus_lambda'] = np.mean(lambda_values)
        comparison['std_lambda'] = np.std(lambda_values)
        comparison['chaos_consensus'] = comparison['consensus_lambda'] > 0

        return comparison


def logistic_map_r(num_steps: int, r: float) -> np.ndarray:
    """Generate logistic map time series."""
    x = np.zeros(num_steps)
    x[0] = 0.5

    for i in range(1, num_steps):
        x[i] = r * x[i-1] * (1 - x[i-1])

    return x


def lorenz_system(t: float, state: np.ndarray, sigma: float = 10, rho: float = 28, beta: float = 8/3) -> np.ndarray:
    """Lorenz system RHS."""
    x, y, z = state
    return np.array([
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z
    ])


def lorenz_jacobian(state: np.ndarray, sigma: float = 10, rho: float = 28, beta: float = 8/3) -> np.ndarray:
    """Lorenz system Jacobian."""
    x, y, z = state
    return np.array([
        [-sigma, sigma, 0],
        [rho - z, -1, -x],
        [y, x, -beta]
    ])


if __name__ == "__main__":
    # Test Lyapunov computation
    computer = LyapunovComputer()

    print("=" * 70)
    print("LYAPUNOV EXPONENT COMPUTATION TESTS")
    print("=" * 70)

    # Test 1: Logistic map (periodic vs chaotic)
    print("\n1. LOGISTIC MAP")
    print("-" * 70)

    for r_val in [2.5, 3.2, 3.5, 3.7, 4.0]:
        x = logistic_map_r(5000, r_val)
        spectrum = computer.from_timeseries_rosenstein(x, dt=1.0)

        print(f"\nr = {r_val}:")
        print(f"  λ₁ = {spectrum.largest_exponent:.4f}")
        print(f"  Chaos: {spectrum.chaos_indicated}")
        print(f"  Horizon: {spectrum.predictability_horizon:.2f} iterations")

    # Test 2: Lorenz system
    print("\n2. LORENZ SYSTEM")
    print("-" * 70)

    from scipy.integrate import odeint

    # Integrate Lorenz
    t = np.arange(0, 50, 0.01)
    x0 = [1.0, 1.0, 1.0]
    trajectory = odeint(lorenz_system, x0, t)

    # Compute Lyapunov spectrum from Jacobian
    spectrum = computer.complete_spectrum_ode(
        lambda x, t: lorenz_system(t, x),
        lorenz_jacobian,
        np.array(x0),
        (0, 50),
        dt=0.01
    )

    print(f"\nComplete Lyapunov Spectrum:")
    print(f"  λ₁ = {spectrum.exponents[0]:.4f} (chaos: {spectrum.exponents[0] > 0})")
    print(f"  λ₂ = {spectrum.exponents[1]:.4f}")
    print(f"  λ₃ = {spectrum.exponents[2]:.4f}")
    print(f"\nLyapunov dimension: {spectrum.lyapunov_dimension:.4f}")
    print(f"KS entropy: {spectrum.kolmogorov_sinai_entropy:.4f}")
    print(f"Predictability horizon: {spectrum.predictability_horizon:.2f} time units")

    # Test 3: Method comparison
    print("\n3. METHOD COMPARISON")
    print("-" * 70)

    x_logistic = logistic_map_r(5000, 3.8)
    comparison = computer.compare_methods(x_logistic, dt=1.0)

    print(f"\nLargest Lyapunov exponents:")
    for method, lambda_val in comparison['largest_exponents'].items():
        print(f"  {method}: λ₁ = {lambda_val:.4f}")

    print(f"\nConsensus: λ₁ = {comparison['consensus_lambda']:.4f} ± {comparison['std_lambda']:.4f}")
    print(f"Chaos consensus: {comparison['chaos_consensus']}")
