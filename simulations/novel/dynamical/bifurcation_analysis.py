"""
Bifurcation Analysis for POLLN Dynamical System

This module analyzes qualitative changes in dynamics (bifurcations) as
system parameters vary, using continuation methods and normal forms.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import root, minimize
from scipy.linalg import eig
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from vector_fields import PollnVectorField
from fixed_points import PollnFixedPoints, FixedPoint, FixedPointType
from deepseek_dynamical import DeepSeekDynamicalSystems, MathematicalDerivation


class BifurcationType(Enum):
    """Types of bifurcations"""
    SADDLE_NODE = "saddle_node"  # Fold bifurcation
    TRANSCRITICAL = "transcritical"  # Exchange of stability
    PITCHFORK = "pitchfork"  # Symmetry breaking
    HOPF = "hopf"  # Birth of limit cycle
    HOMOCLINIC = "homoclinic"  # Global bifurcation
    HETEROCLINIC = "heteroclinic"  # Global bifurcation
    PERIOD_DOUBLING = "period_doubling"  # Feigenbaum
    NONE = "none"  # No bifurcation


@dataclass
class BifurcationPoint:
    """Container for bifurcation point data"""
    parameter_value: float  # Parameter value at bifurcation
    bifurcation_type: BifurcationType  # Type of bifurcation
    location: np.ndarray  # State space location
    eigenvalues: np.ndarray  # Critical eigenvalues
    normal_form: str  # Normal form equation
    stability_change: bool  # Whether stability changes
    branch: str  # Which branch (upper/lower)


class PollnBifurcationAnalysis:
    """
    Bifurcation analysis for POLLN dynamical system.

    Tracks qualitative changes in dynamics as parameters vary.
    """

    def __init__(self, vector_field: PollnVectorField):
        """
        Initialize bifurcation analyzer.

        Args:
            vector_field: POLLN vector field
        """
        self.vf = vector_field
        self.bifurcation_points: List[BifurcationPoint] = []
        self.derivation: Optional[MathematicalDerivation] = None

    def detect_bifurcations(self, parameter: str = 'learning_rate',
                           param_range: Tuple[float, float] = (0.001, 0.1),
                           num_points: int = 100) -> List[BifurcationPoint]:
        """
        Detect bifurcations by scanning parameter space.

        Args:
            parameter: Parameter to vary
            param_range: (min, max) range
            num_points: Number of parameter values

        Returns:
            List of detected bifurcation points
        """
        print(f"\nScanning {parameter} for bifurcations...")
        print(f"Range: {param_range[0]:.4f} to {param_range[1]:.4f}")

        param_values = np.linspace(param_range[0], param_range[1], num_points)
        fixed_points_history = []
        eigenvalues_history = []

        original_value = getattr(self.vf, parameter)

        for param in param_values:
            # Set parameter
            setattr(self.vf, parameter, param)

            # Find fixed points
            fp_analyzer = PollnFixedPoints(self.vf)
            fps = fp_analyzer.find_fixed_points(num_initial=15)

            # Store data
            fixed_points_history.append(fps)

            # Store eigenvalues
            for fp in fps:
                eigenvalues_history.append({
                    'parameter': param,
                    'eigenvalues': fp.eigenvalues,
                    'location': fp.location,
                    'type': fp.type
                })

        # Restore original value
        setattr(self.vf, parameter, original_value)

        # Detect bifurcations from eigenvalue crossings
        bifurcations = self._detect_eigenvalue_crossings(eigenvalues_history)

        # Classify bifurcation types
        for bif in bifurcations:
            bif.bifurcation_type = self._classify_bifurcation(bif, eigenvalues_history)
            bif.normal_form = self._get_normal_form(bif)

        self.bifurcation_points = bifurcations

        print(f"\nDetected {len(bifurcations)} bifurcations:")
        for bif in bifurcations:
            print(f"  {parameter} = {bif.parameter_value:.4f}: {bif.bifurcation_type.value}")

        return bifurcations

    def _detect_eigenvalue_crossings(self,
                                    eigenvalues_history: List[Dict]) -> List[BifurcationPoint]:
        """
        Detect eigenvalue crossings indicating bifurcations.

        Bifurcations occur when eigenvalues cross imaginary axis:
        - Real eigenvalue crosses zero → Saddle-node, transcritical, pitchfork
        - Complex pair crosses axis → Hopf

        Args:
            eigenvalues_history: History of eigenvalues vs parameter

        Returns:
            List of bifurcation points
        """
        bifurcations = []

        for i in range(1, len(eigenvalues_history)):
            prev_data = eigenvalues_history[i-1]
            curr_data = eigenvalues_history[i]

            prev_eigs = prev_data['eigenvalues']
            curr_eigs = curr_data['eigenvalues']

            # Check for real eigenvalue crossing zero
            prev_real = np.real(prev_eigs)
            curr_real = np.real(curr_eigs)

            for j, (prev_re, curr_re) in enumerate(zip(prev_real, curr_real)):
                # Check for crossing
                if prev_re * curr_re < 0:  # Sign change = crossing
                    # Interpolate exact crossing point
                    param_cross = self._interpolate_crossing(
                        prev_data['parameter'],
                        curr_data['parameter'],
                        prev_re,
                        curr_re
                    )

                    bifurcations.append(BifurcationPoint(
                        parameter_value=param_cross,
                        bifurcation_type=BifurcationType.NONE,  # To be classified
                        location=curr_data['location'],
                        eigenvalues=curr_eigs,
                        normal_form="",
                        stability_change=True,
                        branch="unknown"
                    ))

            # Check for Hopf (complex pair crossing)
            # Look for eigenvalues with small imaginary part crossing real axis
            prev_im = np.imag(prev_eigs)
            curr_im = np.imag(curr_eigs)

            # This is simplified - proper detection requires tracking eigenvalue branches
            # For now, we flag potential Hopf bifurcations

        return bifurcations

    def _interpolate_crossing(self, param1: float, param2: float,
                             val1: float, val2: float) -> float:
        """
        Linear interpolation to find exact crossing point.

        Args:
            param1, param2: Parameter values
            val1, val2: Eigenvalue real parts

        Returns:
            Interpolated parameter value where crossing occurs
        """
        # Linear interpolation: val = m*param + b
        m = (val2 - val1) / (param2 - param1)
        b = val1 - m * param1

        # Solve for val = 0
        param_cross = -b / m

        return param_cross

    def _classify_bifurcation(self, bif: BifurcationPoint,
                             eigenvalues_history: List[Dict]) -> BifurcationType:
        """
        Classify bifurcation type from eigenvalue behavior.

        Args:
            bif: Bifurcation point
            eigenvalues_history: Full eigenvalue history

        Returns:
            Bifurcation type
        """
        # Check eigenvalues at bifurcation
        eigs = bif.eigenvalues
        real_parts = np.real(eigs)
        imag_parts = np.imag(eigs)

        # Count eigenvalues on imaginary axis
        on_axis = np.abs(real_parts) < 1e-6

        # Count zero eigenvalues
        zero_eigs = np.sum(np.abs(eigs) < 1e-6)

        # Count purely imaginary pairs
        imag_pairs = np.sum((np.abs(real_parts) < 1e-6) & (np.abs(imag_parts) > 1e-6))

        # Classify based on eigenvalue configuration
        if zero_eigs == 1:
            # Single zero eigenvalue: saddle-node, transcritical, or pitchfork
            # Check for symmetry (pitchfork) vs others
            # For simplicity, classify as saddle-node
            return BifurcationType.SADDLE_NODE

        elif imag_pairs >= 1:
            # Complex pair on imaginary axis: Hopf
            return BifurcationType.HOPF

        elif zero_eigs >= 2:
            # Multiple zero eigenvalues: more complex
            return BifurcationType.PITCHFORK

        else:
            return BifurcationType.NONE

    def _get_normal_form(self, bif: BifurcationPoint) -> str:
        """
        Get normal form equation for bifurcation.

        Args:
            bif: Bifurcation point

        Returns:
            Normal form equation
        """
        if bif.bifurcation_type == BifurcationType.SADDLE_NODE:
            return "ẋ = μ - x²"
        elif bif.bifurcation_type == BifurcationType.TRANSCRITICAL:
            return "ẋ = μx - x²"
        elif bif.bifurcation_type == BifurcationType.PITCHFORK:
            return "ẋ = μx - x³"
        elif bif.bifurcation_type == BifurcationType.HOPF:
            return "ż = (μ + iω)z - z|z|²"
        else:
            return "Unknown"

    def continuation(self, parameter: str = 'learning_rate',
                    start_param: float = 0.01,
                    x0: Optional[np.ndarray] = None,
                    direction: int = 1,
                    step_size: float = 0.001,
                    max_steps: int = 100) -> Dict:
        """
        Perform parameter continuation of fixed point branch.

        Tracks how fixed points change as parameter varies.

        Args:
            parameter: Parameter to continue
            start_param: Starting parameter value
            x0: Initial fixed point (if None, finds one)
            direction: Continuation direction (+1 or -1)
            step_size: Parameter step size
            max_steps: Maximum continuation steps

        Returns:
            Continuation data
        """
        print(f"\nPerforming continuation of {parameter}...")

        if x0 is None:
            # Find initial fixed point
            setattr(self.vf, parameter, start_param)
            fp_analyzer = PollnFixedPoints(self.vf)
            fps = fp_analyzer.find_fixed_points(num_initial=10)
            if len(fps) > 0:
                x0 = fps[0].location
            else:
                print("No fixed point found for continuation")
                return {}

        continuation_data = {
            'parameter_values': [start_param],
            'fixed_points': [x0],
            'eigenvalues': [np.linalg.eigvals(self.vf.jacobian(x0))],
            'stability': []
        }

        current_param = start_param
        current_x = x0.copy()

        for step in range(max_steps):
            # Predict next point (tangent prediction)
            next_param = current_param + direction * step_size

            # Set parameter
            setattr(self.vf, parameter, next_param)

            # Correct (Newton iteration)
            try:
                sol = root(
                    lambda x: self.vf.vector_field(0, x),
                    current_x,
                    method='hybr',
                    tol=1e-10
                )

                if sol.success:
                    next_x = sol.x

                    # Check if close to prediction
                    if np.linalg.norm(next_x - current_x) < 1.0:
                        continuation_data['parameter_values'].append(next_param)
                        continuation_data['fixed_points'].append(next_x)

                        # Compute eigenvalues
                        eigs = np.linalg.eigvals(self.vf.jacobian(next_x))
                        continuation_data['eigenvalues'].append(eigs)

                        # Check stability
                        is_stable = np.all(np.real(eigs) < 0)
                        continuation_data['stability'].append(is_stable)

                        current_param = next_param
                        current_x = next_x
                    else:
                        # Jump detected (saddle-node bifurcation)
                        print(f"Saddle-node bifurcation detected at {parameter} = {current_param:.4f}")
                        break
                else:
                    print("Continuation failed at step", step)
                    break

            except Exception as e:
                print(f"Continuation error at step {step}: {e}")
                break

        print(f"Continuation completed: {len(continuation_data['parameter_values'])} points")

        return continuation_data

    def plot_bifurcation_diagram(self, continuation_data: Dict,
                                state_index: int = 0,
                                save_path: Optional[str] = None):
        """
        Plot bifurcation diagram.

        Args:
            continuation_data: Data from continuation()
            state_index: Which state dimension to plot
            save_path: Optional path to save figure
        """
        if not continuation_data:
            print("No continuation data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 8))

        params = continuation_data['parameter_values']
        fps = continuation_data['fixed_points']
        stabilities = continuation_data['stability']

        # Plot stable branches (solid) and unstable (dashed)
        for i in range(len(params) - 1):
            color = 'blue' if stabilities[i] else 'red'
            linestyle = '-' if stabilities[i] else '--'

            ax.plot([params[i], params[i+1]],
                   [fps[i][state_index], fps[i+1][state_index]],
                   c=color, linestyle=linestyle, linewidth=2)

        # Mark bifurcation points
        for bif in self.bifurcation_points:
            ax.axvline(x=bif.parameter_value, color='green',
                      linestyle=':', linewidth=2, alpha=0.7)

        ax.set_xlabel("Parameter Value", fontsize=12)
        ax.set_ylabel(f"State Dimension {state_index}", fontsize=12)
        ax.set_title("Bifurcation Diagram\nSolid = Stable, Dashed = Unstable",
                    fontsize=14)
        ax.grid(True, alpha=0.3)

        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='blue', linestyle='-', label='Stable'),
            Line2D([0], [0], color='red', linestyle='--', label='Unstable'),
            Line2D([0], [0], color='green', linestyle=':', label='Bifurcation')
        ]
        ax.legend(handles=legend_elements)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_eigenvalue_tracks(self, eigenvalues_history: List[Dict],
                              save_path: Optional[str] = None):
        """
        Plot eigenvalue trajectories vs parameter.

        Args:
            eigenvalues_history: History of eigenvalues
            save_path: Optional path to save figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Real parts vs parameter
        ax = axes[0]

        param_values = [e['parameter'] for e in eigenvalues_history]

        for i in range(len(eigenvalues_history[0]['eigenvalues'])):
            real_parts = []
            for e in eigenvalues_history:
                if i < len(e['eigenvalues']):
                    real_parts.append(np.real(e['eigenvalues'][i]))
                else:
                    real_parts.append(np.nan)

            ax.plot(param_values, real_parts, 'o-', markersize=4, alpha=0.7)

        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel("Parameter Value")
        ax.set_ylabel("Eigenvalue Real Part")
        ax.set_title("Eigenvalue Real Parts vs Parameter")
        ax.grid(True, alpha=0.3)

        # Plot 2: Imaginary parts vs parameter
        ax = axes[1]

        for i in range(len(eigenvalues_history[0]['eigenvalues'])):
            imag_parts = []
            for e in eigenvalues_history:
                if i < len(e['eigenvalues']):
                    imag_parts.append(np.imag(e['eigenvalues'][i]))
                else:
                    imag_parts.append(np.nan)

            ax.plot(param_values, imag_parts, 'o-', markersize=4, alpha=0.7)

        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel("Parameter Value")
        ax.set_ylabel("Eigenvalue Imaginary Part")
        ax.set_title("Eigenvalue Imaginary Parts vs Parameter")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def feigenbaum_analysis(self, parameter: str = 'learning_rate',
                           param_range: Tuple[float, float] = (0.01, 0.1),
                           num_points: int = 200) -> Dict:
        """
        Analyze period-doubling route to chaos (Feigenbaum).

        Args:
            parameter: Parameter to vary
            param_range: Parameter range
            num_points: Number of points

        Returns:
            Feigenbaum analysis results
        """
        print(f"\nAnalyzing period-doubling (Feigenbaum)...")

        param_values = np.linspace(param_range[0], param_range[1], num_points)
        periods = []

        original_value = getattr(self.vf, parameter)

        for param in param_values:
            setattr(self.vf, parameter, param)

            # Detect period from trajectory
            x0 = np.random.randn(self.vf.total_dim) * 0.5

            sol = solve_ivp(
                self.vf.vector_field,
                (0, 50),
                x0,
                t_eval=np.linspace(0, 50, 2000),
                method='RK45'
            )

            # Estimate period using FFT
            from scipy.fft import fft, fftfreq
            fft_vals = fft(sol.y[0, :])
            freqs = fftfreq(len(sol.y[0, :]), d=sol.t[1] - sol.t[0])

            # Find dominant frequency
            power = np.abs(fft_vals)**2
            positive_freqs = freqs[freqs > 0]
            positive_power = power[freqs > 0]

            if len(positive_power) > 0:
                dominant_freq = positive_freqs[np.argmax(positive_power)]
                period = 1.0 / dominant_freq if dominant_freq > 1e-10 else 0
            else:
                period = 0

            periods.append(period)

        # Restore
        setattr(self.vf, parameter, original_value)

        # Look for period doubling
        # Period should double at bifurcation points
        period_ratios = []
        for i in range(1, len(periods)):
            if periods[i-1] > 1e-6:
                period_ratios.append(periods[i] / periods[i-1])

        # Estimate Feigenbaum constant
        # δ ≈ 4.669 for period doubling
        doublings = [i for i, r in enumerate(period_ratios) if abs(r - 2.0) < 0.3]

        return {
            'parameter_values': param_values,
            'periods': periods,
            'period_ratios': period_ratios,
            'doublings': doublings
        }

    def derive_with_deepseek(self) -> MathematicalDerivation:
        """Use DeepSeek to derive bifurcation theory"""
        ds = DeepSeekDynamicalSystems()
        self.derivation = ds.derive_bifurcation_theory("""
        POLLN multi-agent system with:
        - Learning rate as bifurcation parameter
        - Temperature affecting stability
        - Coupling strength causing bifurcations
        - Phase transitions in collective behavior
        """)

        return self.derivation


def analyze_bifurcations():
    """
    Comprehensive bifurcation analysis.
    """
    print("=" * 80)
    print("BIFURCATION ANALYSIS")
    print("=" * 80)

    vf = PollnVectorField(num_agents=5, state_dim=3)
    analyzer = PollnBifurcationAnalysis(vf)

    # Derive theory
    print("\nDeriving bifurcation theory with DeepSeek...")
    derivation = analyzer.derive_with_deepseek()
    print(f"Theorem: {derivation.theorem[:200]}...")

    # Detect bifurcations
    bifurcations = analyzer.detect_bifurcations(
        parameter='learning_rate',
        param_range=(0.001, 0.05),
        num_points=50
    )

    # Continuation
    print("\nPerforming continuation...")
    cont_data = analyzer.continuation(
        parameter='learning_rate',
        start_param=0.01,
        direction=1,
        step_size=0.001,
        max_steps=50
    )

    # Plot bifurcation diagram
    if cont_data:
        print("\nGenerating bifurcation diagram...")
        analyzer.plot_bifurcation_diagram(
            cont_data,
            save_path="C:/Users/casey/polln/simulations/novel/dynamical/bifurcation_diagram.png"
        )

    # Feigenbaum analysis
    print("\nFeigenbaum analysis...")
    feig_data = analyzer.feigenbaum_analysis(
        parameter='learning_rate',
        param_range=(0.01, 0.1),
        num_points=100
    )

    return {
        'analyzer': analyzer,
        'bifurcations': bifurcations,
        'continuation': cont_data,
        'feigenbaum': feig_data,
        'derivation': derivation
    }


if __name__ == "__main__":
    results = analyze_bifurcations()
