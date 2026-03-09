"""
Vector Fields and Flows for POLLN Dynamical System

This module constructs and analyzes vector fields for multi-agent systems,
providing phase portraits, nullclines, and flow visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.integrate import odeint, solve_ivp
from scipy.optimize import root
from typing import Tuple, List, Callable, Optional
from dataclasses import dataclass

from deepseek_dynamical import DeepSeekDynamicalSystems, MathematicalDerivation


@dataclass
class VectorFieldResult:
    """Container for vector field analysis results"""
    field: Callable  # Vector field function
    flow: Callable  # Flow function
    nullclines_x: np.ndarray  # x-nullcline points
    nullclines_y: np.ndarray  # y-nullcline points
    phase_portrait: np.ndarray  # 2D field data
    trajectories: List[np.ndarray]  # Computed trajectories


class PollnVectorField:
    """
    Vector field construction for POLLN dynamical system.

    The state space is R^n where n = num_agents * state_dim
    The vector field F: R^n → R^n describes the rate of change.
    """

    def __init__(self, num_agents: int = 5, state_dim: int = 3):
        """
        Initialize POLLN vector field.

        Args:
            num_agents: Number of agents in the system
            state_dim: Dimension of each agent's state
        """
        self.num_agents = num_agents
        self.state_dim = state_dim
        self.total_dim = num_agents * state_dim

        # System parameters
        self.learning_rate = 0.01
        self.temperature = 1.0
        self.discount = 0.99
        self.trace_decay = 0.9

        # Coupling matrix (agent interactions)
        self.coupling = np.random.randn(num_agents, num_agents) * 0.1

        # Store DeepSeek derivations
        self.derivation = None

    def state_vector(self, agent_states: np.ndarray) -> np.ndarray:
        """
        Flatten agent states into global state vector.

        Args:
            agent_states: (num_agents, state_dim) array

        Returns:
            Flattened state vector of length total_dim
        """
        return agent_states.flatten()

    def agent_states(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Reshape global state vector into agent states.

        Args:
            state_vector: Global state vector

        Returns:
            (num_agents, state_dim) array
        """
        return state_vector.reshape((self.num_agents, self.state_dim))

    def vector_field(self, t: float, x: np.ndarray) -> np.ndarray:
        """
        Compute vector field F(x) = dx/dt at state x.

        The field combines:
        1. Individual agent dynamics
        2. Coupling between agents
        3. Stochastic exploration (temperature)
        4. Learning dynamics

        Args:
            t: Time parameter
            x: State vector

        Returns:
            Derivative dx/dt
        """
        # Reshape to agent states
        agent_states = self.agent_states(x)
        dxdt = np.zeros_like(agent_states)

        for i in range(self.num_agents):
            # Self-dynamics (sigmoid activation)
            state = agent_states[i]
            dxdt[i, 0] = -state[0] + np.tanh(state[1])  # Belief dynamics
            dxdt[i, 1] = -state[1] + np.tanh(state[2])  # Policy dynamics
            dxdt[i, 2] = -state[2] + np.tanh(state[0])  # Value dynamics

            # Coupling from other agents
            for j in range(self.num_agents):
                if i != j:
                    coupling_strength = self.coupling[i, j]
                    dxdt[i] += coupling_strength * agent_states[j]

            # Temperature-controlled noise
            noise = np.random.randn(self.state_dim) * self.temperature * 0.1
            dxdt[i] += noise

        return dxdt.flatten()

    def compute_flow(self, x0: np.ndarray, t_span: Tuple[float, float],
                     t_eval: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute flow (trajectory) from initial condition.

        Flow φ^t(x0) gives the state at time t starting from x0.

        Args:
            x0: Initial state vector
            t_span: (t_start, t_end) time interval
            t_eval: Optional time points for evaluation

        Returns:
            Trajectory array
        """
        if t_eval is None:
            t_eval = np.linspace(t_span[0], t_span[1], 1000)

        sol = solve_ivp(
            self.vector_field,
            t_span,
            x0,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )

        return sol.y.T

    def phase_portrait_2d(self, x_range: Tuple[float, float],
                         y_range: Tuple[float, float],
                         grid_size: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute 2D phase portrait (projection).

        Args:
            x_range: (x_min, x_max) for first state dimension
            y_range: (y_min, y_max) for second state dimension
            grid_size: Number of grid points

        Returns:
            (X, Y, U, V) meshgrid with vector components
        """
        x = np.linspace(x_range[0], x_range[1], grid_size)
        y = np.linspace(y_range[0], y_range[1], grid_size)
        X, Y = np.meshgrid(x, y)

        U = np.zeros_like(X)
        V = np.zeros_like(Y)

        for i in range(grid_size):
            for j in range(grid_size):
                # Create 2D state
                state_2d = np.array([X[i, j], Y[i, j]])

                # Pad to full dimension (use zeros for other dims)
                state_full = np.zeros(self.total_dim)
                state_full[0] = state_2d[0]
                state_full[1] = state_2d[1]

                # Compute derivative
                deriv = self.vector_field(0, state_full)
                U[i, j] = deriv[0]
                V[i, j] = deriv[1]

        return X, Y, U, V

    def find_nullclines(self, x_range: Tuple[float, float],
                       y_range: Tuple[float, float],
                       grid_size: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find nullclines (curves where dx/dt = 0 or dy/dt = 0).

        Nullclines are where the flow is parallel to axes.
        They intersect at fixed points.

        Args:
            x_range: Range for first dimension
            y_range: Range for second dimension
            grid_size: Grid resolution

        Returns:
            (x_nullcline, y_nullcline) points
        """
        x = np.linspace(x_range[0], x_range[1], grid_size)
        y = np.linspace(y_range[0], y_range[1], grid_size)

        x_null = []
        y_null = []

        for xi in x:
            for yi in y:
                state = np.zeros(self.total_dim)
                state[0] = xi
                state[1] = yi

                deriv = self.vector_field(0, state)

                # x-nullcline: dx/dt ≈ 0
                if abs(deriv[0]) < 0.01:
                    x_null.append([xi, yi])

                # y-nullcline: dy/dt ≈ 0
                if abs(deriv[1]) < 0.01:
                    y_null.append([xi, yi])

        return np.array(x_null), np.array(y_null)

    def visualize_phase_portrait(self, x_range: Tuple[float, float] = (-3, 3),
                                y_range: Tuple[float, float] = (-3, 3),
                                save_path: Optional[str] = None):
        """
        Visualize phase portrait with nullclines and sample trajectories.

        Args:
            x_range: Range for x-axis
            y_range: Range for y-axis
            save_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        # Compute phase portrait
        X, Y, U, V = self.phase_portrait_2d(x_range, y_range, grid_size=25)

        # Plot vector field
        speed = np.sqrt(U**2 + V**2)
        strm = ax.streamplot(X, Y, U, V, color=speed, cmap='viridis',
                            linewidth=1, arrowsize=1.5, density=2)
        fig.colorbar(strm.lines, ax=ax, label='Flow speed')

        # Plot nullclines
        x_null, y_null = self.find_nullclines(x_range, y_range)
        if len(x_null) > 0:
            ax.scatter(x_null[:, 0], x_null[:, 1], c='red', s=10,
                      alpha=0.5, label='x-nullcline (dx/dt=0)')
        if len(y_null) > 0:
            ax.scatter(y_null[:, 0], y_null[:, 1], c='blue', s=10,
                      alpha=0.5, label='y-nullcline (dy/dt=0)')

        # Plot sample trajectories
        for _ in range(5):
            x0 = np.random.uniform(-2, 2, self.total_dim)
            trajectory = self.compute_flow(x0, (0, 10), np.linspace(0, 10, 500))
            ax.plot(trajectory[:, 0], trajectory[:, 1], 'g-', alpha=0.6, linewidth=2)
            ax.plot(trajectory[0, 0], trajectory[0, 1], 'go', markersize=8)

        ax.set_xlabel('State Dimension 1', fontsize=12)
        ax.set_ylabel('State Dimension 2', fontsize=12)
        ax.set_title('POLLN Phase Portrait\nVector Field, Nullclines, and Trajectories',
                    fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def divergence(self, x: np.ndarray) -> float:
        """
        Compute divergence of vector field at state x.

        Div F = ∇·F = Σ ∂F_i/∂x_i
        Positive divergence = source (expanding)
        Negative divergence = sink (contracting)

        Args:
            x: State vector

        Returns:
            Divergence value
        """
        eps = 1e-6
        div = 0.0

        for i in range(len(x)):
            # Forward difference
            x_plus = x.copy()
            x_plus[i] += eps
            F_plus = self.vector_field(0, x_plus)

            # Backward difference
            x_minus = x.copy()
            x_minus[i] -= eps
            F_minus = self.vector_field(0, x_minus)

            # Central difference for ∂F_i/∂x_i
            div += (F_plus[i] - F_minus[i]) / (2 * eps)

        return div

    def curl_2d(self, x: np.ndarray) -> float:
        """
        Compute 2D curl (vorticity) of vector field.

        Curl = ∂F_y/∂x - ∂F_x/∂y
        Measures rotation in the flow.

        Args:
            x: State vector (must have at least 2 dimensions)

        Returns:
            Curl value
        """
        if len(x) < 2:
            return 0.0

        eps = 1e-6

        # ∂F_y/∂x
        x_plus = x.copy()
        x_plus[0] += eps
        F_y_plus = self.vector_field(0, x_plus)[1]

        x_minus = x.copy()
        x_minus[0] -= eps
        F_y_minus = self.vector_field(0, x_minus)[1]

        dFy_dx = (F_y_plus - F_y_minus) / (2 * eps)

        # ∂F_x/∂y
        y_plus = x.copy()
        y_plus[1] += eps
        F_x_plus = self.vector_field(0, y_plus)[0]

        y_minus = x.copy()
        y_minus[1] -= eps
        F_x_minus = self.vector_field(0, y_minus)[0]

        dFx_dy = (F_x_plus - F_x_minus) / (2 * eps)

        return dFy_dx - dFx_dy

    def jacobian(self, x: np.ndarray) -> np.ndarray:
        """
        Compute Jacobian matrix J_ij = ∂F_i/∂x_j at state x.

        The Jacobian determines linear stability and bifurcations.

        Args:
            x: State vector

        Returns:
            Jacobian matrix
        """
        n = len(x)
        J = np.zeros((n, n))
        eps = 1e-6

        for i in range(n):
            for j in range(n):
                x_plus = x.copy()
                x_plus[j] += eps
                F_plus = self.vector_field(0, x_plus)[i]

                x_minus = x.copy()
                x_minus[j] -= eps
                F_minus = self.vector_field(0, x_minus)[i]

                J[i, j] = (F_plus - F_minus) / (2 * eps)

        return J

    def derive_with_deepseek(self) -> MathematicalDerivation:
        """
        Use DeepSeek to derive vector field theory for POLLN.

        Returns:
            Mathematical derivation from DeepSeek
        """
        ds = DeepSeekDynamicalSystems()
        self.derivation = ds.derive_vector_field_equations("""
        POLLN multi-agent system with:
        - State variables: agent beliefs, policies, values
        - Coupling: Hebbian learning between agents
        - Stochasticity: Temperature-controlled exploration
        - Timescales: Fast (reflex), medium (habit), slow (deliberate)
        """)

        return self.derivation


def analyze_vector_field_dynamics():
    """
    Comprehensive vector field analysis of POLLN.
    """
    print("=" * 80)
    print("VECTOR FIELD AND FLOW ANALYSIS")
    print("=" * 80)

    # Create vector field
    vf = PollnVectorField(num_agents=5, state_dim=3)

    # Derive theory with DeepSeek
    print("\nDeriving vector field theory with DeepSeek...")
    derivation = vf.derive_with_deepseek()
    print(f"Theorem: {derivation.theorem[:200]}...")
    print(f"Equations: {len(derivation.equations)}")

    # Visualize phase portrait
    print("\nGenerating phase portrait...")
    vf.visualize_phase_portrait(
        x_range=(-3, 3),
        y_range=(-3, 3),
        save_path="C:/Users/casey/polln/simulations/novel/dynamical/phase_portrait.png"
    )

    # Analyze flow properties
    print("\nAnalyzing flow properties...")
    x0 = np.random.randn(vf.total_dim)

    # Divergence at random state
    div = vf.divergence(x0)
    print(f"Divergence at random state: {div:.4f}")
    print(f"Interpretation: {'Source (expanding)' if div > 0 else 'Sink (contracting)'}")

    # Curl at random state
    curl = vf.curl_2d(x0)
    print(f"2D Curl at random state: {curl:.4f}")
    print(f"Interpretation: {'Counter-clockwise rotation' if curl > 0 else 'Clockwise rotation'}")

    # Jacobian at random state
    J = vf.jacobian(x0)
    print(f"\nJacobian matrix shape: {J.shape}")
    print(f"Jacobian eigenvalues: {np.linalg.eigvals(J)[:5]}...")

    # Compute trajectory
    print("\nComputing sample trajectory...")
    trajectory = vf.compute_flow(x0, (0, 10))
    print(f"Trajectory shape: {trajectory.shape}")
    print(f"Final state: {trajectory[-1, :5]}...")

    # Find nullclines
    print("\nFinding nullclines...")
    x_null, y_null = vf.find_nullclines((-3, 3), (-3, 3))
    print(f"x-nullcline points: {len(x_null)}")
    print(f"y-nullcline points: {len(y_null)}")

    return {
        'vector_field': vf,
        'derivation': derivation,
        'trajectory': trajectory,
        'divergence': div,
        'curl': curl,
        'jacobian': J
    }


if __name__ == "__main__":
    results = analyze_vector_field_dynamics()
