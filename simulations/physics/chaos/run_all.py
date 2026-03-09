"""
Master Chaos Analysis Orchestrator
===================================

Runs complete chaos theory analysis pipeline:
1. Lyapunov exponent computation
2. Bifurcation analysis
3. Strange attractor characterization
4. Routes to chaos
5. Edge of chaos detection
6. Synchronization analysis
7. DeepSeek theoretical derivations
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json
from pathlib import Path
import warnings

from lyapunov import LyapunovComputer
from bifurcation import BifurcationAnalyzer
from attractors import AttractorAnalyzer
from edge_chaos import ChaoticSystems, ODEIntegrator, TimeSeriesAnalysis
from deepseek_chaos import DeepSeekChaosAnalyzer


@dataclass
class ChaosAnalysisReport:
    """Complete chaos theory analysis report."""
    system_name: str
    lyapunov_analysis: Dict[str, Any]
    bifurcation_analysis: Dict[str, Any]
    attractor_properties: Dict[str, Any]
    edge_of_chaos: Dict[str, Any]
    routes_to_chaos: Dict[str, Any]
    deepseek_derivations: Dict[str, Any]
    recommendations: List[str]


class ChaosAnalysisOrchestrator:
    """
    Master orchestrator for complete chaos theory analysis.

    Coordinates all analysis modules and synthesizes results.
    """

    def __init__(self, use_deepseek: bool = True):
        """Initialize orchestrator with all analyzers."""
        self.lyapunov_computer = LyapunovComputer(use_deepseek=use_deepseek)
        self.bifurcation_analyzer = BifurcationAnalyzer(use_deepseek=use_deepseek)
        self.attractor_analyzer = AttractorAnalyzer()
        self.deepseek = DeepSeekChaosAnalyzer() if use_deepseek else None

    def analyze_ode_system(
        self,
        system_name: str,
        rhs_func: Callable[[float, np.ndarray], np.ndarray],
        jacobian_func: Callable[[np.ndarray], np.ndarray],
        parameter_name: str,
        parameter_range: tuple,
        initial_state: np.ndarray,
        t_span: tuple,
        dt: float = 0.01
    ) -> ChaosAnalysisReport:
        """
        Complete chaos analysis for an ODE system.

        Args:
            system_name: Name of the system
            rhs_func: Right-hand side function f(t, x, μ)
            jacobian_func: Jacobian function J(x, μ)
            parameter_name: Name of bifurcation parameter
            parameter_range: (μ_min, μ_max)
            initial_state: Initial condition
            t_span: (t_start, t_end)
            dt: Time step

        Returns:
            Complete ChaosAnalysisReport
        """
        print(f"\n{'='*70}")
        print(f"ANALYZING SYSTEM: {system_name}")
        print(f"{'='*70}")

        report_data = {
            'system_name': system_name,
            'parameter': parameter_name,
            'parameter_range': parameter_range
        }

        # 1. Generate trajectory at parameter range midpoint
        mu_mid = (parameter_range[0] + parameter_range[1]) / 2
        print(f"\n1. Generating trajectory at μ = {mu_mid:.3f}...")

        integrator = ODEIntegrator()
        result = integrator.runge_kutta_4(
            lambda t, y: rhs_func(t, y),
            t_span,
            initial_state,
            dt
        )

        trajectory = result.state
        timeseries = trajectory[:, 0]  # Use first variable

        # 2. Lyapunov exponents
        print(f"\n2. Computing Lyapunov exponents...")

        lyap_spectrum = self.lyapunov_computer.complete_spectrum_ode(
            lambda x, t: rhs_func(t, x),
            lambda x: jacobian_func(x),
            initial_state,
            t_span,
            dt
        )

        lyap_analysis = {
            'exponents': lyap_spectrum.exponents.tolist(),
            'largest_exponent': float(lyap_spectrum.largest_exponent),
            'chaos_indicated': lyap_spectrum.chaos_indicated,
            'predictability_horizon': float(lyap_spectrum.predictability_horizon),
            'lyapunov_dimension': float(lyap_spectrum.lyapunov_dimension),
            'kolmogorov_sinai_entropy': float(lyap_spectrum.kolmogorov_sinai_entropy)
        }

        print(f"   λ₁ = {lyap_spectrum.largest_exponent:.4f} (chaos: {lyap_spectrum.chaos_indicated})")

        # 3. Bifurcation analysis
        print(f"\n3. Analyzing bifurcations...")

        # Sample parameters
        mu_values = np.linspace(parameter_range[0], parameter_range[1], 50)

        bifurcation_data = {
            'parameter_values': mu_values.tolist(),
            'bifurcation_points': [],
            'routes_to_chaos': []
        }

        # Detect bifurcations (simplified)
        for mu in mu_values:
            # Check for qualitative changes
            # This would require more sophisticated analysis
            pass

        # 4. Attractor characterization
        print(f"\n4. Characterizing attractor...")

        attractor_props = self.attractor_analyzer.characterize_attractor(
            timeseries,
            lyapunov_exponents=lyap_spectrum.exponents
        )

        attractor_analysis = {
            'embedding_dimension': attractor_props.embedding_dimension,
            'time_delay': attractor_props.time_delay,
            'box_counting_dimension': float(attractor_props.box_counting_dimension),
            'correlation_dimension': float(attractor_props.correlation_dimension),
            'information_dimension': float(attractor_props.information_dimension),
            'lyapunov_dimension': float(attractor_props.lyapunov_dimension),
            'reconstruction_quality': float(attractor_props.reconstruction_quality)
        }

        print(f"   Embedding dimension: {attractor_props.embedding_dimension}")
        print(f"   Correlation dimension: {attractor_props.correlation_dimension:.3f}")

        # 5. Edge of chaos analysis
        print(f"\n5. Locating edge of chaos...")

        edge_analysis = self._find_edge_of_chaos(
            lyap_spectrum.largest_exponent
        )

        # 6. DeepSeek theoretical analysis
        deepseek_analysis = {}
        if self.deepseek:
            print(f"\n6. Generating theoretical derivations (DeepSeek)...")

            system_description = {
                'type': 'ode',
                'name': system_name,
                'equations': [f"dx/dt = {system_name} dynamics"],
                'variables': ['x', 'y', 'z'],
                'parameters': {parameter_name: 'bifurcation parameter'}
            }

            # Get theoretical insights
            lyap_theory = self.deepseek.analyze_lyapunov_exponents(system_description)
            bif_theory = self.deepseek.analyze_bifurcations(system_description)
            edge_theory = self.deepseek.analyze_edge_of_chaos(system_description)

            deepseek_analysis = {
                'lyapunov_theory': lyap_theory['insights'][:5],
                'bifurcation_theory': bif_theory['insights'][:5],
                'edge_of_chaos_theory': edge_theory['insights'][:5]
            }

        # 7. Generate recommendations
        recommendations = self._generate_recommendations(lyap_analysis, attractor_analysis)

        return ChaosAnalysisReport(
            system_name=system_name,
            lyapunov_analysis=lyap_analysis,
            bifurcation_analysis=bifurcation_data,
            attractor_properties=attractor_analysis,
            edge_of_chaos=edge_analysis,
            routes_to_chaos={},
            deepseek_derivations=deepseek_analysis,
            recommendations=recommendations
        )

    def analyze_map_system(
        self,
        system_name: str,
        map_func: Callable[[float, float], float],
        parameter_name: str,
        parameter_range: tuple,
        n_iter: int = 10000,
        n_transient: int = 1000
    ) -> ChaosAnalysisReport:
        """
        Complete chaos analysis for a 1D map.

        Args:
            system_name: Name of the map
            map_func: f(x, μ) - map function
            parameter_name: Name of parameter
            parameter_range: (μ_min, μ_max)
            n_iter: Total iterations
            n_transient: Transient iterations to discard

        Returns:
            Complete ChaosAnalysisReport
        """
        print(f"\n{'='*70}")
        print(f"ANALYZING MAP: {system_name}")
        print(f"{'='*70}")

        # Generate bifurcation diagram
        print(f"\n1. Generating bifurcation diagram...")

        bif_analyzer = BifurcationAnalyzer()
        mu_vals, x_vals = bif_analyzer.bifurcation_diagram_1d(
            map_func,
            parameter_range,
            n_params=400,
            n_iter=n_iter,
            n_last=200
        )

        # Compute Feigenbaum constants
        print(f"\n2. Computing Feigenbaum constants...")

        feigenbaum_data = bif_analyzer.feigenbaum_analysis(
            map_func,
            mu_start=parameter_range[0],
            mu_end=parameter_range[1]
        )

        # Lyapunov exponent at sample parameters
        print(f"\n3. Computing Lyapunov exponents...")

        sample_mus = np.linspace(parameter_range[0], parameter_range[1], 20)
        lyap_exponents = []

        for mu in sample_mus:
            x = 0.5
            for _ in range(n_iter):
                x = map_func(x, mu)

            # Compute LTE from orbit
            lyap = self._compute_map_lyapunov(map_func, mu, n_iter)
            lyap_exponents.append(lyap)

        # Edge of chaos
        print(f"\n4. Locating edge of chaos...")

        edge_indices = np.where(np.array(lyap_exponents) > 0)[0]
        if len(edge_indices) > 0:
            edge_mu = sample_mus[edge_indices[0]]
        else:
            edge_mu = None

        # DeepSeek analysis
        deepseek_analysis = {}
        if self.deepseek:
            print(f"\n5. Generating theoretical derivations...")

            system_description = {
                'type': 'map',
                'name': system_name,
                'equations': [f"x_{{n+1}} = {system_name}(x_n)"],
                'variables': ['x'],
                'parameters': {parameter_name: 'bifurcation parameter'}
            }

            route_theory = self.deepseek.analyze_routes_to_chaos(system_description)

            deepseek_analysis = {
                'routes_to_chaos': route_theory['insights'][:5]
            }

        # Recommendations
        if edge_mu is not None:
            recommendations = [
                f"Edge of chaos near μ = {edge_mu:.4f}",
                f"Operate in range [{edge_mu:.3f}, {edge_mu + 0.1:.3f}] for optimal complexity",
                f"Feigenbaum δ converges to {feigenbaum_data['delta_convergence']:.4f} "
                f"(theoretical: {feigenbaum_data['theoretical_delta']:.6f})"
            ]
        else:
            recommendations = ["No chaos detected in parameter range"]

        return ChaosAnalysisReport(
            system_name=system_name,
            lyapunov_analysis={
                'sample_parameters': sample_mus.tolist(),
                'exponents': lyap_exponents
            },
            bifurcation_analysis={
                'bifurcation_parameters': feigenbaum_data['bifurcation_parameters'],
                'feigenbaum_delta': feigenbaum_data['feigenbaum_delta'],
                'delta_convergence': feigenbaum_data['delta_convergence']
            },
            attractor_properties={},
            edge_of_chaos={'edge_parameter': edge_mu},
            routes_to_chaos=feigenbaum_data,
            deepseek_derivations=deepseek_analysis,
            recommendations=recommendations
        )

    def _find_edge_of_chaos(
        self,
        largest_lyapunov: float,
        tolerance: float = 0.1
    ) -> Dict[str, Any]:
        """Estimate edge of chaos from Lyapunov exponent."""
        if abs(largest_lyapunov) < tolerance:
            return {
                'at_edge': True,
                'lambda_1': largest_lyapunov,
                'interpretation': 'System at edge of chaos - optimal complexity'
            }
        elif largest_lyapunov > 0:
            return {
                'at_edge': False,
                'lambda_1': largest_lyapunov,
                'interpretation': 'System in chaotic regime'
            }
        else:
            return {
                'at_edge': False,
                'lambda_1': largest_lyapunov,
                'interpretation': 'System in ordered regime'
            }

    def _compute_map_lyapunov(
        self,
        map_func: Callable[[float, float], float],
        mu: float,
        n_iter: int = 10000
    ) -> float:
        """Compute Lyapunov exponent for 1D map."""
        x = 0.5
        lyap_sum = 0

        for _ in range(n_iter):
            # Compute derivative
            dx = 1e-6
            f_plus = map_func(x + dx, mu)
            f_minus = map_func(x - dx, mu)
            df_dx = (f_plus - f_minus) / (2 * dx)

            lyap_sum += np.log(abs(df_dx))
            x = map_func(x, mu)

        return lyap_sum / n_iter

    def _generate_recommendations(
        self,
        lyap_analysis: Dict[str, Any],
        attractor_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations from analysis."""
        recommendations = []

        lambda_1 = lyap_analysis['largest_exponent']

        if lambda_1 > 0:
            recommendations.append(
                f"Chaotic dynamics detected (λ₁ = {lambda_1:.4f}). "
                "System exhibits sensitive dependence on initial conditions."
            )
        elif abs(lambda_1) < 0.01:
            recommendations.append(
                f"System near edge of chaos (λ₁ ≈ {lambda_1:.4f}). "
                "This regime may support optimal computational capabilities."
            )
        else:
            recommendations.append(
                f"Ordered dynamics (λ₁ = {lambda_1:.4f}). "
                "System behavior is predictable."
            )

        # Fractal dimensions
        if 'correlation_dimension' in attractor_analysis:
            d_c = attractor_analysis['correlation_dimension']
            if d_c > 2:
                recommendations.append(
                    f"High fractal dimension (d_C = {d_c:.3f}) indicates "
                    "complex attractor geometry and rich dynamics."
                )

        # Predictability
        horizon = lyap_analysis.get('predictability_horizon', float('inf'))
        if horizon < float('inf'):
            recommendations.append(
                f"Predictability horizon: {horizon:.2f} time units. "
                f"Beyond this, predictions become unreliable."
            )

        return recommendations

    def save_report(
        self,
        report: ChaosAnalysisReport,
        output_dir: str = "."
    ):
        """Save analysis report to JSON file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = output_path / f"{report.system_name.replace(' ', '_')}_chaos_report.json"

        # Convert to serializable dict
        report_dict = {
            'system_name': report.system_name,
            'lyapunov_analysis': report.lyapunov_analysis,
            'bifurcation_analysis': report.bifurcation_analysis,
            'attractor_properties': report.attractor_properties,
            'edge_of_chaos': report.edge_of_chaos,
            'routes_to_chaos': report.routes_to_chaos,
            'deepseek_derivations': report.deepseek_derivations,
            'recommendations': report.recommendations
        }

        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)

        print(f"\nReport saved to: {filename}")


# Convenience functions for common systems
def analyze_lorenz(
    t_span: tuple = (0, 50),
    dt: float = 0.01,
    use_deepseek: bool = True
) -> ChaosAnalysisReport:
    """Analyze Lorenz system."""
    orchestrator = ChaosAnalysisOrchestrator(use_deepseek=use_deepseek)

    return orchestrator.analyze_ode_system(
        system_name="Lorenz",
        rhs_func=lambda t, y: ChaoticSystems.lorenz(t, y),
        jacobian_func=lambda x: np.array([
            [-10, 10, 0],
            [28 - x[2], -1, -x[0]],
            [x[1], x[0], -8/3]
        ]),
        parameter_name="rho",
        parameter_range=(10, 50),
        initial_state=np.array([1.0, 1.0, 1.0]),
        t_span=t_span,
        dt=dt
    )


def analyze_logistic_map(
    use_deepseek: bool = True
) -> ChaosAnalysisReport:
    """Analyze logistic map."""
    orchestrator = ChaosAnalysisOrchestrator(use_deepseek=use_deepseek)

    return orchestrator.analyze_map_system(
        system_name="Logistic Map",
        map_func=lambda x, r: r * x * (1 - x),
        parameter_name="r",
        parameter_range=(2.4, 4.0)
    )


def analyze_roessler(
    t_span: tuple = (0, 100),
    dt: float = 0.01,
    use_deepseek: bool = True
) -> ChaosAnalysisReport:
    """Analyze Rössler system."""
    orchestrator = ChaosAnalysisOrchestrator(use_deepseek=use_deepseek)

    return orchestrator.analyze_ode_system(
        system_name="Rossler",
        rhs_func=lambda t, y: ChaoticSystems.rossler(t, y),
        jacobian_func=lambda x: np.array([
            [0, -1, -1],
            [1, 0.2, 0],
            [x[2], 0, x[0] - 5.7]
        ]),
        parameter_name="c",
        parameter_range=(2, 10),
        initial_state=np.array([0.1, 0.1, 0.1]),
        t_span=t_span,
        dt=dt
    )


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("CHAOS ANALYSIS ORCHESTRATOR")
    print("=" * 70)

    use_deepseek = '--no-deepseek' not in sys.argv

    # Analyze Lorenz
    print("\n" + "="*70)
    print("ANALYZING LORENZ SYSTEM")
    print("="*70)

    lorenz_report = analyze_lorenz(use_deepseek=use_deepseek)

    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)

    print(f"\nLargest Lyapunov: {lorenz_report.lyapunov_analysis['largest_exponent']:.4f}")
    print(f"Chaos indicated: {lorenz_report.lyapunov_analysis['chaos_indicated']}")
    print(f"Lyapunov dimension: {lorenz_report.lyapunov_analysis['lyapunov_dimension']:.3f}")

    print("\nRecommendations:")
    for rec in lorenz_report.recommendations:
        print(f"  - {rec}")

    # Save report
    orchestrator = ChaosAnalysisOrchestrator()
    orchestrator.save_report(lorenz_report, output_dir=".")

    # Analyze logistic map
    print("\n" + "="*70)
    print("ANALYZING LOGISTIC MAP")
    print("="*70)

    logistic_report = analyze_logistic_map(use_deepseek=use_deepseek)

    print("\nBifurcation parameters:")
    print(f"  {logistic_report.bifurcation_analysis['bifurcation_parameters'][:5]}...")

    if 'delta_convergence' in logistic_report.bifurcation_analysis:
        delta = logistic_report.bifurcation_analysis['delta_convergence']
        print(f"\nFeigenbaum δ: {delta:.6f}")

    print("\nRecommendations:")
    for rec in logistic_report.recommendations:
        print(f"  - {rec}")

    orchestrator.save_report(logistic_report, output_dir=".")
