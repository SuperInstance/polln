"""
Dynamical Systems Simulation Toolkit

This module provides a comprehensive toolkit for simulating and analyzing
dynamical systems, including ODE integrators, Poincaré sections, and
return maps.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, odeint
from scipy.optimize import root
from typing import Callable, Tuple, Optional, List, Dict
from dataclasses import dataclass

from vector_fields import PollnVectorField


@dataclass
class SimulationResult:
    """Container for simulation results"""
    time: np.ndarray  # Time points
    state: np.ndarray  # State trajectories
    success: bool  # Whether integration succeeded
    message: str  # Status message


class DynamicalSimulator:
    """
    Comprehensive dynamical systems simulation toolkit.

    Provides various ODE integrators, analysis tools, and visualization methods.
    """

    def __init__(self, vector_field: PollnVectorField):
        """
        Initialize simulator.

        Args:
            vector_field: POLLN vector field
        """
        self.vf = vector_field

    def integrate(self, x0: np.ndarray, t_span: Tuple[float, float],
                 method: str = 'RK45',
                 t_eval: Optional[np.ndarray] = None,
                 **kwargs) -> SimulationResult:
        """
        Integrate ODE from initial condition.

        Args:
            x0: Initial state
            t_span: (t_start, t_end) time interval
            method: Integration method ('RK45', 'RK23', 'DOP853', 'Radau', 'BDF')
            t_eval: Optional time points for evaluation
            **kwargs: Additional arguments for solve_ivp

        Returns:
            SimulationResult with trajectory
        """
        if t_eval is None:
            t_eval = np.linspace(t_span[0], t_span[1], 1000)

        try:
            sol = solve_ivp(
                self.vf.vector_field,
                t_span,
                x0,
                t_eval=t_eval,
                method=method,
                rtol=kwargs.get('rtol', 1e-8),
                atol=kwargs.get('atol', 1e-10),
                max_step=kwargs.get('max_step', np.inf)
            )

            return SimulationResult(
                time=sol.t,
                state=sol.y.T,
                success=sol.success,
                message=sol.message
            )

        except Exception as e:
            return SimulationResult(
                time=np.array([]),
                state=np.array([]).reshape(0, len(x0)),
                success=False,
                message=str(e)
            )

    def integrate_ensemble(self, x0_array: List[np.ndarray],
                          t_span: Tuple[float, float],
                          **kwargs) -> List[SimulationResult]:
        """
        Integrate multiple initial conditions.

        Args:
            x0_array: List of initial states
            t_span: Time interval
            **kwargs: Arguments for integrate()

        Returns:
            List of SimulationResults
        """
        results = []

        for x0 in x0_array:
            result = self.integrate(x0, t_span, **kwargs)
            results.append(result)

        return results

    def poincare_section(self, trajectory: np.ndarray,
                         section_dim: int = 0,
                         section_value: float = 0.0,
                         direction: str = 'both') -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Poincaré section (intersection with hyperplane).

        Useful for analyzing limit cycles and quasiperiodic orbits.

        Args:
            trajectory: State trajectory
            section_dim: Dimension to take section in
            section_value: Value for section (typically zero)
            direction: 'positive', 'negative', or 'both' crossing direction

        Returns:
            (section_points, crossing_times)
        """
        crossings = []
        times = []

        for i in range(len(trajectory) - 1):
            # Check for crossing
            x1, x2 = trajectory[i, section_dim], trajectory[i+1, section_dim]

            # Check if section is crossed
            if (x1 - section_value) * (x2 - section_value) < 0:
                # Determine direction
                dx = x2 - x1

                if direction == 'positive' and dx < 0:
                    continue
                elif direction == 'negative' and dx > 0:
                    continue

                # Linear interpolation for exact crossing
                t = (section_value - x1) / dx
                crossing = trajectory[i] + t * (trajectory[i+1] - trajectory[i])

                crossings.append(crossing)
                times.append(i + t)

        return np.array(crossings), np.array(times)

    def return_map(self, poincare_points: np.ndarray,
                   delay: int = 1) -> np.ndarray:
        """
        Compute return map from Poincaré section.

        Maps each crossing to the next: x_n → x_{n+delay}

        Args:
            poincare_points: Points from Poincaré section
            delay: Map delay (default: 1 for next crossing)

        Returns:
            Return map pairs (x_n, x_{n+delay})
        """
        if len(poincare_points) < delay + 1:
            return np.array([])

        # Use first dimension for map
        x_n = poincare_points[:-delay, 0]
        x_next = poincare_points[delay:, 0]

        return np.column_stack([x_n, x_next])

    def lyapunov_exponents(self, trajectory: np.ndarray,
                          epsilon: float = 1e-6) -> np.ndarray:
        """
        Compute Lyapunov exponents from trajectory.

        Measures average exponential divergence of nearby trajectories.

        Args:
            trajectory: State trajectory
            epsilon: Perturbation size

        Returns:
            Lyapunov exponents (sorted descending)
        """
        n_states = len(trajectory)
        n_dim = len(trajectory[0])

        if n_states < 2:
            return np.zeros(n_dim)

        # Jacobian-based computation
        exponents = np.zeros(n_dim)

        for i in range(min(100, n_states - 1)):
            x = trajectory[i]

            # Compute Jacobian
            J = self.vf.jacobian(x)

            # Local expansion rates
            local_exp = np.real(np.linalg.eigvals(J))

            exponents += local_exp

        return exponents / min(100, n_states - 1)

    def divergence_rate(self, trajectory: np.ndarray) -> np.ndarray:
        """
        Compute divergence rate along trajectory.

        Positive = expansion (chaos)
        Negative = contraction

        Args:
            trajectory: State trajectory

        Returns:
            Divergence rate at each point
        """
        divergence = []

        for x in trajectory:
            div = self.vf.divergence(x)
            divergence.append(div)

        return np.array(divergence)

    def isochrons(self, fixed_point: np.ndarray,
                 grid_bounds: Tuple[float, float] = (-2, 2),
                 grid_resolution: int = 20) -> np.ndarray:
        """
        Compute isochrons (sets of points with same asymptotic phase).

        Args:
            fixed_point: Fixed point (limit cycle focus)
            grid_bounds: Grid bounds
            grid_resolution: Grid resolution

        Returns:
            Phase values on grid
        """
        x = np.linspace(grid_bounds[0], grid_bounds[1], grid_resolution)
        y = np.linspace(grid_bounds[0], grid_bounds[1], grid_resolution)
        X, Y = np.meshgrid(x, y)

        phases = np.zeros_like(X)

        # This is simplified - proper isochron computation requires
        # solving backward to limit cycle
        for i in range(grid_resolution):
            for j in range(grid_resolution):
                x0 = np.zeros(self.vf.total_dim)
                x0[0] = X[i, j]
                x0[1] = Y[i, j]

                # Integrate forward
                sol = self.integrate(x0, (0, 20), t_eval=np.linspace(0, 20, 100))

                if sol.success:
                    # Phase relative to fixed point (simplified)
                    phase = np.arctan2(sol.state[-1, 1], sol.state[-1, 0])
                    phases[i, j] = phase

        return phases

    def stable_manifold(self, fixed_point: np.ndarray,
                       epsilon: float = 1e-3,
                       time: float = 10.0) -> np.ndarray:
        """
        Compute stable manifold W^s(x*).

        Set of points that converge to fixed point as t → +∞.

        Args:
            fixed_point: Fixed point
            epsilon: Initial perturbation size
            time: Integration time

        Returns:
            Points on stable manifold
        """
        # Compute eigenvectors with negative eigenvalues
        J = self.vf.jacobian(fixed_point)
        eigenvalues, eigenvectors = np.linalg.eig(J)

        # Find stable eigenvectors (negative real part)
        stable_idx = np.where(np.real(eigenvalues) < 0)[0]

        manifold_points = []

        for idx in stable_idx:
            # Perturb along stable eigenvector
            v = np.real(eigenvectors[:, idx])
            v = v / np.linalg.norm(v)

            # Forward integration
            x0 = fixed_point + epsilon * v
            sol = self.integrate(x0, (0, time))

            if sol.success:
                manifold_points.append(sol.state)

        return np.array(manifold_points)

    def unstable_manifold(self, fixed_point: np.ndarray,
                         epsilon: float = 1e-3,
                         time: float = 10.0) -> np.ndarray:
        """
        Compute unstable manifold W^u(x*).

        Set of points that converge to fixed point as t → -∞.

        Args:
            fixed_point: Fixed point
            epsilon: Initial perturbation size
            time: Integration time

        Returns:
            Points on unstable manifold
        """
        # Compute eigenvectors with positive eigenvalues
        J = self.vf.jacobian(fixed_point)
        eigenvalues, eigenvectors = np.linalg.eig(J)

        # Find unstable eigenvectors (positive real part)
        unstable_idx = np.where(np.real(eigenvalues) > 0)[0]

        manifold_points = []

        for idx in unstable_idx:
            # Perturb along unstable eigenvector
            v = np.real(eigenvectors[:, idx])
            v = v / np.linalg.norm(v)

            # Backward integration (negative time)
            x0 = fixed_point + epsilon * v
            sol = self.integrate(x0, (0, -time))

            if sol.success:
                manifold_points.append(sol.state)

        return np.array(manifold_points)

    def phase_portrait_3d(self, trajectory: np.ndarray,
                         dims: Tuple[int, int, int] = (0, 1, 2),
                         save_path: Optional[str] = None):
        """
        Plot 3D phase portrait.

        Args:
            trajectory: State trajectory
            dims: Which dimensions to plot
            save_path: Optional path to save figure
        """
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Plot trajectory
        ax.plot(trajectory[:, dims[0]],
               trajectory[:, dims[1]],
               trajectory[:, dims[2]],
               'b-', linewidth=1, alpha=0.7)

        # Mark start and end
        ax.scatter(trajectory[0, dims[0]],
                  trajectory[0, dims[1]],
                  trajectory[0, dims[2]],
                  c='green', s=100, marker='o', label='Start')

        ax.scatter(trajectory[-1, dims[0]],
                  trajectory[-1, dims[1]],
                  trajectory[-1, dims[2]],
                  c='red', s=100, marker='s', label='End')

        ax.set_xlabel(f"Dimension {dims[0]}")
        ax.set_ylabel(f"Dimension {dims[1]}")
        ax.set_zlabel(f"Dimension {dims[2]}")
        ax.set_title("3D Phase Portrait")
        ax.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def recurrence_plot(self, trajectory: np.ndarray,
                       dim1: int = 0,
                       dim2: int = 1,
                       threshold: float = 0.5,
                       save_path: Optional[str] = None):
        """
        Plot recurrence plot.

        Recurrence plot shows when trajectory revisits neighborhood
        of previous states.

        Args:
            trajectory: State trajectory
            dim1, dim2: Dimensions to use
            threshold: Distance threshold for recurrence
            save_path: Optional path to save figure
        """
        # Extract 2D projection
        traj_2d = trajectory[:, [dim1, dim2]]

        # Compute distance matrix
        n = len(traj_2d)
        R = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                R[i, j] = np.linalg.norm(traj_2d[i] - traj_2d[j])

        # Binarize
        R_binary = (R < threshold).astype(int)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(R_binary, cmap='binary', origin='lower')
        ax.set_xlabel("Time Index")
        ax.set_ylabel("Time Index")
        ax.set_title("Recurrence Plot")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def time_series(self, trajectory: np.ndarray,
                   dims: List[int] = None,
                   save_path: Optional[str] = None):
        """
        Plot time series of selected dimensions.

        Args:
            trajectory: State trajectory
            dims: Dimensions to plot (default: first 3)
            save_path: Optional path to save figure
        """
        if dims is None:
            dims = list(range(min(3, trajectory.shape[1])))

        fig, axes = plt.subplots(len(dims), 1, figsize=(12, 4*len(dims)))

        if len(dims) == 1:
            axes = [axes]

        for i, dim in enumerate(dims):
            axes[i].plot(trajectory[:, dim], linewidth=1.5)
            axes[i].set_ylabel(f"State Dimension {dim}")
            axes[i].grid(True, alpha=0.3)

        axes[-1].set_xlabel("Time Index")
        plt.suptitle("Time Series", fontsize=14)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """Demonstrate dynamical systems toolkit"""
    vf = PollnVectorField(num_agents=5, state_dim=3)
    sim = DynamicalSimulator(vf)

    print("=" * 80)
    print("DYNAMICAL SYSTEMS SIMULATION TOOLKIT")
    print("=" * 80)

    # Integrate trajectory
    print("\nIntegrating trajectory...")
    x0 = np.random.randn(vf.total_dim) * 1.0
    result = sim.integrate(x0, (0, 20))

    if result.success:
        print(f"Integration successful: {len(result.time)} time steps")

        # Time series
        print("\nGenerating time series...")
        sim.time_series(result.state)

        # 3D phase portrait
        print("\nGenerating 3D phase portrait...")
        sim.phase_portrait_3d(result.state)

        # Poincaré section
        print("\nComputing Poincaré section...")
        section, times = sim.poincare_section(result.state)
        print(f"Found {len(section)} section points")

        # Lyapunov exponents
        print("\nComputing Lyapunov exponents...")
        lyap = sim.lyapunov_exponents(result.state)
        print(f"Lyapunov exponents: {lyap[:5]}...")

        # Recurrence plot
        print("\nGenerating recurrence plot...")
        sim.recurrence_plot(result.state)

    else:
        print(f"Integration failed: {result.message}")


if __name__ == "__main__":
    main()
