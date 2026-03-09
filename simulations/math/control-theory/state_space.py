"""
State-Space Modeling for POLLN

This module provides state-space modeling capabilities for analyzing
POLLN colony dynamics using control theory.

State-space form:
  ẋ = Ax + Bu  (state equation)
  y = Cx + Du  (output equation)

where:
  x: state vector (agent weights, colony state, etc.)
  u: control input (parameter updates, spawning signals)
  y: output (performance metrics, observations)
"""

import numpy as np
from scipy import linalg
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path

from deepseek_control import DeepSeekControlTheorist


@dataclass
class StateSpaceModel:
    """Container for state-space model"""
    A: np.ndarray  # State matrix
    B: np.ndarray  # Input matrix
    C: np.ndarray  # Output matrix
    D: np.ndarray  # Feedthrough matrix
    state_names: List[str]
    input_names: List[str]
    output_names: List[str]
    description: str


@dataclass
class SystemProperties:
    """System structural properties"""
    controllable: bool
    observable: bool
    stabilizable: bool
    detectable: bool
    minimal: bool
    system_type: str  # 'type-0', 'type-1', 'type-2', etc.
    relative_degree: int


class StateSpaceModeler:
    """
    State-space modeling for POLLN systems.

    Models colony dynamics, learning processes, and control inputs
    in state-space form for control-theoretic analysis.
    """

    def __init__(self, use_deepseek: bool = True):
        """
        Initialize state-space modeler.

        Args:
            use_deepseek: Whether to use DeepSeek for model derivation
        """
        self.use_deepseek = use_deepseek
        if use_deepseek:
            self.theorist = DeepSeekControlTheorist()

        self.models: Dict[str, StateSpaceModel] = {}

    def model_colony_dynamics(self, n_agents: int = 10) -> StateSpaceModel:
        """
        Model agent colony dynamics.

        State variables:
        - Agent synaptic weights
        - Agent activation levels
        - Resource allocation
        - Learning progress

        Control inputs:
        - Parameter updates
        - Agent spawning
        - Resource injection

        Outputs:
        - Performance metrics
        - Resource utilization
        """
        n_states = 4 * n_agents  # 4 states per agent
        n_inputs = 3  # Parameter updates, spawning, resources
        n_outputs = 2  # Performance, utilization

        # State matrix A: Inter-agent dynamics
        # This models the coupling between agents through Hebbian learning
        A = np.zeros((n_states, n_states))

        for i in range(n_agents):
            # Base agent block (4x4)
            base_idx = 4 * i

            # Weight dynamics (decay + learning)
            A[base_idx, base_idx] = -0.1  # Weight decay
            A[base_idx, base_idx + 1] = 0.05  # Learning from activation

            # Activation dynamics (response to weights)
            A[base_idx + 1, base_idx] = 0.1  # Weight influence
            A[base_idx + 1, base_idx + 1] = -0.2  # Activation decay

            # Resource dynamics
            A[base_idx + 2, base_idx + 2] = -0.05  # Resource consumption
            A[base_idx + 2, base_idx + 3] = 0.02  # Learning consumes resources

            # Learning progress
            A[base_idx + 3, base_idx + 1] = 0.08  # Activation drives learning
            A[base_idx + 3, base_idx + 3] = -0.01  # Forgetting

            # Inter-agent coupling (Hebbian: neurons that fire together wire together)
            for j in range(n_agents):
                if i != j:
                    target_idx = 4 * j
                    # Weight coupling
                    A[base_idx, target_idx + 1] = 0.02 * np.exp(-0.1 * abs(i - j))
                    # Activation coupling
                    A[base_idx + 1, target_idx] = 0.01 * np.exp(-0.1 * abs(i - j))

        # Input matrix B
        B = np.zeros((n_states, n_inputs))

        for i in range(n_agents):
            base_idx = 4 * i
            # Parameter updates affect weights
            B[base_idx, 0] = 0.5
            # Agent spawning affects activation
            B[base_idx + 1, 1] = 1.0
            # Resource injection affects resources
            B[base_idx + 2, 2] = 1.0

        # Output matrix C
        C = np.zeros((n_outputs, n_states))

        for i in range(n_agents):
            base_idx = 4 * i
            # Performance: weighted sum of activation and learning
            C[0, base_idx + 1] = 1.0 / n_agents
            C[0, base_idx + 3] = 1.0 / n_agents
            # Utilization: weighted sum of resources
            C[1, base_idx + 2] = 1.0 / n_agents

        # Feedthrough matrix D
        D = np.zeros((n_outputs, n_inputs))

        state_names = []
        for i in range(n_agents):
            state_names.extend([
                f'agent_{i}_weight',
                f'agent_{i}_activation',
                f'agent_{i}_resource',
                f'agent_{i}_learning'
            ])

        input_names = ['param_update', 'agent_spawn', 'resource_inject']
        output_names = ['performance', 'utilization']

        model = StateSpaceModel(
            A=A, B=B, C=C, D=D,
            state_names=state_names,
            input_names=input_names,
            output_names=output_names,
            description=f"Colony dynamics with {n_agents} agents"
        )

        self.models['colony_dynamics'] = model
        return model

    def model_learning_dynamics(self, n_params: int = 50) -> StateSpaceModel:
        """
        Model parameter learning dynamics (e.g., SGD, Adam).

        State variables:
        - Parameter values
        - First moment estimate (Adam)
        - Second moment estimate (Adam)

        Control inputs:
        - Learning rate schedule
        - Gradient inputs

        Outputs:
        - Parameter trajectory
        - Convergence metric
        """
        n_states = 3 * n_params  # params, m, v for Adam
        n_inputs = 2  # Learning rate, gradient
        n_outputs = 2  # Params, convergence

        # State matrix A
        A = np.zeros((n_states, n_states))

        # Parameter dynamics
        for i in range(n_params):
            param_idx = 3 * i

            # Parameter updates based on moments
            A[param_idx, param_idx + 1] = -0.1  # First moment influence
            A[param_idx, param_idx + 2] = -0.05  # Second moment influence

            # First moment (momentum)
            A[param_idx + 1, param_idx + 1] = 0.9  # Beta1 decay

            # Second moment (RMSprop)
            A[param_idx + 2, param_idx + 2] = 0.999  # Beta2 decay

        # Input matrix B
        B = np.zeros((n_states, n_inputs))

        for i in range(n_params):
            param_idx = 3 * i
            # Learning rate affects parameter updates
            B[param_idx, 0] = -0.1
            # Gradients affect moments
            B[param_idx + 1, 1] = 0.1  # Gradient affects first moment
            B[param_idx + 2, 1] = 0.01  # Gradient affects second moment

        # Output matrix C
        C = np.zeros((n_outputs, n_states))

        for i in range(n_params):
            param_idx = 3 * i
            # Parameter output
            C[0, param_idx] = 1.0
            # Convergence: parameter change
            C[1, param_idx] = 0.01

        # Feedthrough matrix D
        D = np.zeros((n_outputs, n_inputs))

        state_names = []
        for i in range(n_params):
            state_names.extend([
                f'param_{i}',
                f'param_{i}_m',
                f'param_{i}_v'
            ])

        input_names = ['learning_rate', 'gradient']
        output_names = ['parameters', 'convergence']

        model = StateSpaceModel(
            A=A, B=B, C=C, D=D,
            state_names=state_names,
            input_names=input_names,
            output_names=output_names,
            description=f"Learning dynamics (Adam) with {n_params} parameters"
        )

        self.models['learning_dynamics'] = model
        return model

    def model_plinko_selection(self, n_options: int = 10) -> StateSpaceModel:
        """
        Model Plinko stochastic selection dynamics.

        State variables:
        - Selection probabilities
        - Temperature parameter
        - Exploration state

        Control inputs:
        - Temperature schedule
        - Reward feedback

        Outputs:
        - Selection distribution
        - Exploration level
        """
        n_states = n_options + 2  # probs + temperature + exploration
        n_inputs = 2  # Temperature, reward
        n_outputs = 2  # Distribution, exploration

        # State matrix A
        A = np.zeros((n_states, n_states))

        # Probability dynamics (softmax normalization)
        for i in range(n_options):
            # Probability decay towards uniform
            A[i, i] = -0.1
            for j in range(n_options):
                if i != j:
                    A[i, j] = 0.01

        # Temperature dynamics
        A[n_options, n_options] = -0.05  # Temperature decay

        # Exploration dynamics
        A[n_options + 1, n_options] = 0.1  # Temperature drives exploration
        A[n_options + 1, n_options + 1] = -0.2  # Exploration decay

        # Input matrix B
        B = np.zeros((n_states, n_inputs))

        # Temperature control
        B[n_options, 0] = 0.5

        # Reward feedback affects probabilities
        for i in range(n_options):
            B[i, 1] = 0.1

        # Output matrix C
        C = np.zeros((n_outputs, n_states))

        # Selection distribution
        for i in range(n_options):
            C[0, i] = 1.0

        # Exploration level
        C[1, n_options + 1] = 1.0

        # Feedthrough matrix D
        D = np.zeros((n_outputs, n_inputs))

        state_names = [f'prob_{i}' for i in range(n_options)] + ['temperature', 'exploration']
        input_names = ['temp_schedule', 'reward']
        output_names = ['distribution', 'exploration_level']

        model = StateSpaceModel(
            A=A, B=B, C=C, D=D,
            state_names=state_names,
            input_names=input_names,
            output_names=output_names,
            description=f"Plinko selection with {n_options} options"
        )

        self.models['plinko_selection'] = model
        return model

    def model_hebbian_learning(self, n_neurons: int = 20) -> StateSpaceModel:
        """
        Model Hebbian learning dynamics.

        State variables:
        - Synaptic weights
        - Pre-synaptic activity
        - Post-synaptic activity

        Control inputs:
        - Learning rate
        - Activity injection

        Outputs:
        - Weight matrix (flattened)
        - Total synaptic strength
        """
        n_states = n_neurons * n_neurons + 2 * n_neurons  # weights + pre + post activity
        n_inputs = 2  # Learning rate, activity
        n_outputs = 2  # Total weight, activity

        # Simplified model: focus on weight dynamics
        n_weights = n_neurons * n_neurons
        A = np.zeros((n_states, n_states))

        # Weight dynamics (Hebbian: ΔW = η * pre * post)
        for i in range(n_weights):
            A[i, i] = -0.01  # Weight decay
            # Coupling to pre/post activity (simplified)
            A[i, n_weights + (i // n_neurons)] = 0.05
            A[i, n_weights + n_neurons + (i % n_neurons)] = 0.05

        # Pre-synaptic activity
        for i in range(n_neurons):
            idx = n_weights + i
            A[idx, idx] = -0.5  # Activity decay

        # Post-synaptic activity
        for i in range(n_neurons):
            idx = n_weights + n_neurons + i
            A[idx, idx] = -0.5  # Activity decay

        # Input matrix B
        B = np.zeros((n_states, n_inputs))

        for i in range(n_weights):
            # Learning rate affects weight updates
            B[i, 0] = 0.1

        for i in range(n_neurons):
            # Activity injection
            B[n_weights + i, 1] = 1.0
            B[n_weights + n_neurons + i, 1] = 1.0

        # Output matrix C
        C = np.zeros((n_outputs, n_states))

        # Total weight
        for i in range(n_weights):
            C[0, i] = 1.0 / n_weights

        # Total activity
        for i in range(n_neurons):
            C[1, n_weights + i] = 1.0 / (2 * n_neurons)
            C[1, n_weights + n_neurons + i] = 1.0 / (2 * n_neurons)

        # Feedthrough matrix D
        D = np.zeros((n_outputs, n_inputs))

        state_names = ([f'weight_{i}_{j}' for i in range(n_neurons) for j in range(n_neurons)] +
                      [f'pre_{i}' for i in range(n_neurons)] +
                      [f'post_{i}' for i in range(n_neurons)])
        input_names = ['learning_rate', 'activity']
        output_names = ['total_weight', 'total_activity']

        model = StateSpaceModel(
            A=A, B=B, C=C, D=D,
            state_names=state_names,
            input_names=input_names,
            output_names=output_names,
            description=f"Hebbian learning with {n_neurons} neurons"
        )

        self.models['hebbian_learning'] = model
        return model

    def analyze_properties(self, model: StateSpaceModel) -> SystemProperties:
        """
        Analyze structural properties of state-space model.

        Args:
            model: State-space model

        Returns:
            SystemProperties with structural analysis
        """
        A, B, C = model.A, model.B, model.C
        n = A.shape[0]

        # Controllability
        Co = np.column_stack([B] + [np.linalg.matrix_power(A, i) @ B for i in range(1, n)])
        controllable = np.linalg.matrix_rank(Co) == n

        # Observability
        Ob = np.vstack([C] + [C @ np.linalg.matrix_power(A, i) for i in range(1, n)])
        observable = np.linalg.matrix_rank(Ob) == n

        # Stabilizable (uncontrollable modes stable)
        if not controllable:
            # Compute uncontrollable modes
            # This is simplified - full analysis requires PBH test
            stabilizable = True  # Placeholder
        else:
            stabilizable = True

        # Detectable (unobservable modes stable)
        if not observable:
            detectable = True  # Placeholder
        else:
            detectable = True

        # Minimal realization
        minimal = controllable and observable

        # System type (number of integrators)
        # Check poles at origin
        poles, _ = linalg.pole(model.A, model.B, model.C, model.D)
        poles_at_origin = np.sum(np.abs(poles) < 1e-10)
        system_type = f'type-{int(poles_at_origin)}'

        # Relative degree
        # For SISO systems: min k such that C*A^k*B != 0
        if B.shape[1] == 1 and C.shape[0] == 1:
            relative_degree = 0
            for k in range(n):
                if not np.allclose(C @ np.linalg.matrix_power(A, k) @ B, 0):
                    relative_degree = k
                    break
        else:
            relative_degree = None  # MIMO system

        return SystemProperties(
            controllable=controllable,
            observable=observable,
            stabilizable=stabilizable,
            detectable=detectable,
            minimal=minimal,
            system_type=system_type,
            relative_degree=relative_degree
        )

    def compute_transfer_function(self, model: StateSpaceModel) -> Any:
        """
        Compute transfer function from state-space model.

        For SISO systems: G(s) = C(sI - A)^(-1)B + D

        Args:
            model: State-space model

        Returns:
            Transfer function (scipy.signal.TransferFunction)
        """
        from scipy import signal

        if model.B.shape[1] == 1 and model.C.shape[0] == 1:
            # SISO system
            num, den = signal.ss2tf(model.A, model.B, model.C, model.D)
            return signal.TransferFunction(num, den)
        else:
            # MIMO system - return state-space
            return signal.StateSpace(model.A, model.B, model.C, model.D)

    def compute_poles_zeros(self, model: StateSpaceModel) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute poles and zeros of the system.

        Args:
            model: State-space model

        Returns:
            Tuple of (poles, zeros)
        """
        poles, zeros = linalg.pole(model.A, model.B, model.C, model.D)
        return poles, zeros

    def balancing_transformation(self, model: StateSpaceModel) -> Tuple[np.ndarray, StateSpaceModel]:
        """
        Compute balancing transformation for model reduction.

        Uses balanced realization to identify states with minimal
        contribution to input-output behavior.

        Args:
            model: State-space model

        Returns:
            Tuple of (Hankel singular values, balanced model)
        """
        # Compute Gramians
        Wc = self._compute_controllability_gramian(model.A, model.B)
        Wo = self._compute_observability_gramian(model.A, model.C)

        # Cholesky factorization
        Lc = linalg.cholesky(Wc, lower=True)
        Lo = linalg.cholesky(Wo, lower=True)

        # SVD
        U, sigma, _ = linalg.svd(Lo.T @ Lc)

        # Balancing transformation
        T = linalg.sqrtm(Wc) @ U @ np.diag(1.0 / np.sqrt(sigma))
        Ti = np.linalg.inv(T)

        # Balanced realization
        A_bal = Ti @ model.A @ T
        B_bal = Ti @ model.B
        C_bal = model.C @ T

        balanced_model = StateSpaceModel(
            A=A_bal, B=B_bal, C=C_bal, D=model.D,
            state_names=model.state_names,
            input_names=model.input_names,
            output_names=model.output_names,
            description=f"Balanced: {model.description}"
        )

        return sigma, balanced_model

    def reduce_model(self, model: StateSpaceModel, order: int) -> StateSpaceModel:
        """
        Reduce model order using balanced truncation.

        Args:
            model: Original state-space model
            order: Reduced order

        Returns:
            Reduced-order state-space model
        """
        sigma, balanced_model = self.balancing_transformation(model)

        # Truncate to dominant states
        A_red = balanced_model.A[:order, :order]
        B_red = balanced_model.B[:order, :]
        C_red = balanced_model.C[:, :order]
        D_red = balanced_model.D

        reduced_model = StateSpaceModel(
            A=A_red, B=B_red, C=C_red, D=D_red,
            state_names=model.state_names[:order],
            input_names=model.input_names,
            output_names=model.output_names,
            description=f"Reduced (order {order}): {model.description}"
        )

        return reduced_model

    def _compute_controllability_gramian(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Solve Lyapunov equation for controllability Gramian"""
        Q = B @ B.T
        Wc = linalg.solve_continuous_lyapunov(A, -Q)
        return Wc

    def _compute_observability_gramian(self, A: np.ndarray, C: np.ndarray) -> np.ndarray:
        """Solve Lyapunov equation for observability Gramian"""
        Q = C.T @ C
        Wo = linalg.solve_continuous_lyapunov(A.T, -Q)
        return Wo

    def plot_pole_zero_map(self, model: StateSpaceModel, save_path: Optional[str] = None):
        """
        Plot pole-zero map.

        Args:
            model: State-space model
            save_path: Optional path to save figure
        """
        poles, zeros = self.compute_poles_zeros(model)

        plt.figure(figsize=(10, 8))

        # Plot poles
        plt.scatter(poles.real, poles.imag, marker='x', s=100, color='red', label='Poles', zorder=5)

        # Plot zeros
        if len(zeros) > 0:
            plt.scatter(zeros.real, zeros.imag, marker='o', s=100, color='blue', facecolors='none', label='Zeros', zorder=5)

        # Plot axes
        plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

        # Stability region
        plt.axvline(x=0, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Stability boundary')

        plt.xlabel('Real Part')
        plt.ylabel('Imaginary Part')
        plt.title(f'Pole-Zero Map: {model.description}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def simulate_response(self, model: StateSpaceModel,
                         initial_state: Optional[np.ndarray] = None,
                         input_signal: Optional[np.ndarray] = None,
                         time_span: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate state-space response.

        Args:
            model: State-space model
            initial_state: Initial state (default: zero)
            input_signal: Input signal (time x inputs)
            time_span: Time vector

        Returns:
            Tuple of (time, state_trajectory, output_trajectory)
        """
        from scipy import signal

        if time_span is None:
            time_span = np.linspace(0, 10, 1000)

        if initial_state is None:
            initial_state = np.zeros(model.A.shape[0])

        if input_signal is None:
            # Step response
            t, y = signal.step((model.A, model.B, model.C, model.D), T=time_span)
            # Compute state trajectory
            x = np.zeros((len(t), model.A.shape[0]))
            x[0] = initial_state
            for i in range(1, len(t)):
                dt = t[i] - t[i-1]
                x[i] = x[i-1] + dt * (model.A @ x[i-1] + model.B @ np.ones(model.B.shape[1]))
            return t, x, y
        else:
            # General input response
            t, y, x = signal.lsim((model.A, model.B, model.C, model.D), input_signal, time_span)
            return t, x, y

    def derive_with_deepseek(self, system_description: str) -> Dict[str, Any]:
        """
        Use DeepSeek to derive state-space model.

        Args:
            system_description: Text description of system

        Returns:
            Analysis results with matrices and derivations
        """
        if not self.use_deepseek:
            raise ValueError("DeepSeek not enabled. Initialize with use_deepseek=True.")

        analysis = self.theorist.analyze_stability(system_description)
        return analysis.state_space_model


def create_polln_state_space() -> StateSpaceModel:
    """
    Create comprehensive state-space model for entire POLLN system.

    Combines colony dynamics, learning, Plinko selection, and Hebbian learning.
    """
    modeler = StateSpaceModeler(use_deepseek=False)

    # Individual models
    colony = modeler.model_colony_dynamics(n_agents=5)
    learning = modeler.model_learning_dynamics(n_params=20)
    plinko = modeler.model_plinko_selection(n_options=8)
    hebbian = modeler.model_hebbian_learning(n_neurons=10)

    # Combine models (simplified - in practice, use more sophisticated interconnection)
    total_states = colony.A.shape[0] + learning.A.shape[0] + plinko.A.shape[0] + hebbian.A.shape[0]
    total_inputs = colony.B.shape[1] + learning.B.shape[1] + plinko.B.shape[1] + hebbian.B.shape[1]
    total_outputs = colony.C.shape[0] + learning.C.shape[0] + plinko.C.shape[0] + hebbian.C.shape[0]

    A_combined = linalg.block_diag(colony.A, learning.A, plinko.A, hebbian.A)
    B_combined = linalg.block_diag(colony.B, learning.B, plinko.B, hebbian.B)
    C_combined = linalg.block_diag(colony.C, learning.C, plinko.C, hebbian.C)
    D_combined = linalg.block_diag(colony.D, learning.D, plinko.D, hebbian.D)

    # Add inter-block coupling (simplified)
    # Colony influences Plinko (performance affects selection)
    A_combined[colony.A.shape[0]:colony.A.shape[0]+learning.A.shape[0], :colony.A.shape[0]] += np.random.randn(learning.A.shape[0], colony.A.shape[0]) * 0.01

    combined_model = StateSpaceModel(
        A=A_combined,
        B=B_combined,
        C=C_combined,
        D=D_combined,
        state_names=(colony.state_names + learning.state_names +
                    plinko.state_names + hebbian.state_names),
        input_names=(colony.input_names + learning.input_names +
                    plinko.input_names + hebbian.input_names),
        output_names=(colony.output_names + learning.output_names +
                     plinko.output_names + hebbian.output_names),
        description="Combined POLLN system"
    )

    return combined_model


if __name__ == "__main__":
    # Example usage
    print("Creating state-space models for POLLN...")

    modeler = StateSpaceModeler(use_deepseek=False)

    # Colony dynamics
    print("\n1. Colony Dynamics")
    colony = modeler.model_colony_dynamics(n_agents=5)
    props = modeler.analyze_properties(colony)
    print(f"   Controllable: {props.controllable}")
    print(f"   Observable: {props.observable}")
    print(f"   System type: {props.system_type}")

    # Learning dynamics
    print("\n2. Learning Dynamics")
    learning = modeler.model_learning_dynamics(n_params=20)
    props = modeler.analyze_properties(learning)
    print(f"   Controllable: {props.controllable}")
    print(f"   Observable: {props.observable}")

    # Plot pole-zero map
    print("\n3. Pole-Zero Map")
    modeler.plot_pole_zero_map(colony, save_path="simulations/math/control-theory/colony_pole_zero.png")

    # Combined system
    print("\n4. Combined POLLN System")
    combined = create_polln_state_space()
    print(f"   Total states: {combined.A.shape[0]}")
    print(f"   Total inputs: {combined.B.shape[1]}")
    print(f"   Total outputs: {combined.C.shape[0]}")

    print("\nState-space modeling complete!")
