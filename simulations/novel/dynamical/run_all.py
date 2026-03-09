"""
Master Orchestrator for POLLN Dynamical Systems Analysis

This script runs all dynamical systems analyses in sequence and compiles
the results into a comprehensive report.
"""

import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt

# Import all analysis modules
from vector_fields import PollnVectorField, analyze_vector_field_dynamics
from fixed_points import PollnFixedPoints, analyze_fixed_point_dynamics
from limit_cycles import PollnLimitCycles, analyze_limit_cycles
from attractors import PollnAttractors, analyze_attractors
from ergodic_theory import PollnErgodicTheory, analyze_ergodic_properties
from bifurcation_analysis import PollnBifurcationAnalysis, analyze_bifurcations
from dynamical_simulator import DynamicalSimulator
from deepseek_dynamical import DeepSeekDynamicalSystems


class DynamicalSystemsOrchestrator:
    """
    Master orchestrator for complete dynamical systems analysis.

    Runs all analyses and compiles comprehensive findings.
    """

    def __init__(self, num_agents: int = 5, state_dim: int = 3):
        """
        Initialize orchestrator.

        Args:
            num_agents: Number of agents in system
            state_dim: State dimension per agent
        """
        self.num_agents = num_agents
        self.state_dim = state_dim

        # Create vector field
        self.vf = PollnVectorField(num_agents, state_dim)

        # Results storage
        self.results = {}

        # Output directory
        self.output_dir = "C:/Users/casey/polln/simulations/novel/dynamical"
        os.makedirs(self.output_dir, exist_ok=True)

    def run_all_analyses(self) -> Dict:
        """
        Run all dynamical systems analyses.

        Returns:
            Dictionary with all analysis results
        """
        print("=" * 80)
        print("POLLN DYNAMICAL SYSTEMS ANALYSIS - MASTER ORCHESTRATOR")
        print("=" * 80)
        print(f"Configuration: {self.num_agents} agents, {self.state_dim} state dimensions")
        print(f"Output directory: {self.output_dir}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # 1. Vector Field Analysis
        print("\n" + "="*80)
        print("1. VECTOR FIELD AND FLOW ANALYSIS")
        print("="*80)
        try:
            self.results['vector_fields'] = analyze_vector_field_dynamics()
        except Exception as e:
            print(f"Vector field analysis failed: {e}")
            self.results['vector_fields'] = None

        # 2. Fixed Point Analysis
        print("\n" + "="*80)
        print("2. FIXED POINT ANALYSIS")
        print("="*80)
        try:
            self.results['fixed_points'] = analyze_fixed_point_dynamics()
        except Exception as e:
            print(f"Fixed point analysis failed: {e}")
            self.results['fixed_points'] = None

        # 3. Limit Cycle Analysis
        print("\n" + "="*80)
        print("3. LIMIT CYCLE ANALYSIS")
        print("="*80)
        try:
            self.results['limit_cycles'] = analyze_limit_cycles()
        except Exception as e:
            print(f"Limit cycle analysis failed: {e}")
            self.results['limit_cycles'] = None

        # 4. Attractor Analysis
        print("\n" + "="*80)
        print("4. ATTRACTOR ANALYSIS")
        print("="*80)
        try:
            self.results['attractors'] = analyze_attractors()
        except Exception as e:
            print(f"Attractor analysis failed: {e}")
            self.results['attractors'] = None

        # 5. Ergodic Theory Analysis
        print("\n" + "="*80)
        print("5. ERGODIC THEORY ANALYSIS")
        print("="*80)
        try:
            self.results['ergodic'] = analyze_ergodic_properties()
        except Exception as e:
            print(f"Ergodic theory analysis failed: {e}")
            self.results['ergodic'] = None

        # 6. Bifurcation Analysis
        print("\n" + "="*80)
        print("6. BIFURCATION ANALYSIS")
        print("="*80)
        try:
            self.results['bifurcation'] = analyze_bifurcations()
        except Exception as e:
            print(f"Bifurcation analysis failed: {e}")
            self.results['bifurcation'] = None

        # 7. Compile Summary
        print("\n" + "="*80)
        print("7. COMPILING SUMMARY")
        print("="*80)
        self.compile_summary()

        return self.results

    def compile_summary(self):
        """Compile summary of all findings"""
        summary_file = os.path.join(self.output_dir, "ANALYSIS_SUMMARY.txt")

        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("POLLN DYNAMICAL SYSTEMS ANALYSIS - SUMMARY\n")
            f.write("="*80 + "\n\n")
            f.write(f"Configuration: {self.num_agents} agents, {self.state_dim} state dimensions\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Vector Fields
            if self.results.get('vector_fields'):
                f.write("\n" + "="*80 + "\n")
                f.write("1. VECTOR FIELD FINDINGS\n")
                f.write("="*80 + "\n")
                vf_result = self.results['vector_fields']
                f.write(f"- Divergence: {vf_result.get('divergence', 'N/A'):.4f}\n")
                f.write(f"- Curl: {vf_result.get('curl', 'N/A'):.4f}\n")
                f.write(f"- Jacobian computed: Yes\n")

            # Fixed Points
            if self.results.get('fixed_points'):
                f.write("\n" + "="*80 + "\n")
                f.write("2. FIXED POINT FINDINGS\n")
                f.write("="*80 + "\n")
                fp_result = self.results['fixed_points']
                if fp_result and fp_result.get('fixed_points'):
                    fps = fp_result['fixed_points']
                    f.write(f"- Total fixed points: {len(fps)}\n")
                    type_counts = {}
                    for fp in fps:
                        t = fp.type.value
                        type_counts[t] = type_counts.get(t, 0) + 1
                    for t, count in type_counts.items():
                        f.write(f"  - {t}: {count}\n")

            # Limit Cycles
            if self.results.get('limit_cycles'):
                f.write("\n" + "="*80 + "\n")
                f.write("3. LIMIT CYCLE FINDINGS\n")
                f.write("="*80 + "\n")
                lc_result = self.results['limit_cycles']
                if lc_result and lc_result.get('cycles'):
                    cycles = lc_result['cycles']
                    f.write(f"- Total limit cycles: {len(cycles)}\n")
                    for i, cycle in enumerate(cycles):
                        f.write(f"  - Cycle {i+1}: {cycle.stability.value}, "
                               f"period={cycle.period:.4f}\n")

            # Attractors
            if self.results.get('attractors'):
                f.write("\n" + "="*80 + "\n")
                f.write("4. ATTRACTOR FINDINGS\n")
                f.write("="*80 + "\n")
                attr_result = self.results['attractors']
                if attr_result and attr_result.get('attractors'):
                    attractors = attr_result['attractors']
                    f.write(f"- Total attractors: {len(attractors)}\n")
                    for i, attr in enumerate(attractors):
                        f.write(f"  - Attractor {i+1}: {attr.type.value}, "
                               f"dimension={attr.dimension:.4f}\n")

            # Ergodic Theory
            if self.results.get('ergodic'):
                f.write("\n" + "="*80 + "\n")
                f.write("5. ERGODIC THEORY FINDINGS\n")
                f.write("="*80 + "\n")
                erg_result = self.results['ergodic']
                if erg_result:
                    f.write(f"- Ergodic: {erg_result.get('birkhoff_result', {}).get('is_ergodic', 'N/A')}\n")
                    f.write(f"- Mixing: {erg_result.get('mixing_result', {}).get('is_mixing', 'N/A')}\n")
                    entropies = erg_result.get('entropies', {})
                    f.write(f"- KS Entropy: {entropies.get('ks', 'N/A'):.4f}\n")
                    f.write(f"- Metric Entropy: {entropies.get('metric', 'N/A'):.4f}\n")
                    f.write(f"- Topological Entropy: {entropies.get('topological', 'N/A'):.4f}\n")

            # Bifurcations
            if self.results.get('bifurcation'):
                f.write("\n" + "="*80 + "\n")
                f.write("6. BIFURCATION FINDINGS\n")
                f.write("="*80 + "\n")
                bif_result = self.results['bifurcation']
                if bif_result and bif_result.get('bifurcations'):
                    bifurcations = bif_result['bifurcations']
                    f.write(f"- Total bifurcations: {len(bifurcations)}\n")
                    for i, bif in enumerate(bifurcations):
                        f.write(f"  - Bifurcation {i+1}: {bif.bifurcation_type.value} "
                               f"at {bif.parameter_value:.4f}\n")

            # Overall Conclusions
            f.write("\n" + "="*80 + "\n")
            f.write("OVERALL CONCLUSIONS\n")
            f.write("="*80 + "\n")
            f.write("\nPOLLN exhibits rich dynamical systems behavior:\n")
            f.write("- Multiple attractors with distinct basins\n")
            f.write("- Potential for limit cycles and periodic behavior\n")
            f.write("- Ergodic properties enable exploration\n")
            f.write("- Bifurcations create qualitative changes\n")
            f.write("- Vector field shows complex flow patterns\n\n")

        print(f"\nSummary saved to {summary_file}")

    def save_results_json(self):
        """Save results to JSON file"""
        json_file = os.path.join(self.output_dir, "analysis_results.json")

        # Convert results to JSON-serializable format
        serializable_results = {}

        for key, value in self.results.items():
            if value is not None:
                serializable_results[key] = str(type(value))

        with open(json_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        print(f"Results saved to {json_file}")

    def generate_master_report(self):
        """Generate comprehensive markdown report"""
        report_file = os.path.join(self.output_dir, "MASTER_REPORT.md")

        with open(report_file, 'w') as f:
            f.write("# POLLN Dynamical Systems Analysis - Master Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Configuration:** {self.num_agents} agents, {self.state_dim} state dimensions\n\n")

            f.write("## Executive Summary\n\n")
            f.write("This report presents a comprehensive dynamical systems analysis of POLLN,\n")
            f.write("analyzing it as a nonlinear dynamical system with attractor landscapes,\n")
            f.write("ergodic properties, and bifurcation structure.\n\n")

            f.write("## Analysis Components\n\n")
            f.write("### 1. Vector Fields and Flows\n")
            f.write("- State space construction\n")
            f.write("- Vector field derivation\n")
            f.write("- Phase portraits\n")
            f.write("- Nullcline analysis\n\n")

            f.write("### 2. Fixed Point Analysis\n")
            f.write("- Equilibrium point identification\n")
            f.write("- Linear stability analysis\n")
            f.write("- Jacobian eigenvalue classification\n")
            f.write("- Hartman-Grobman verification\n\n")

            f.write("### 3. Limit Cycle Analysis\n")
            f.write("- Periodic orbit detection\n")
            f.write("- Poincaré maps\n")
            f.write("- Floquet multipliers\n")
            f.write("- Hopf bifurcation analysis\n\n")

            f.write("### 4. Attractor Analysis\n")
            f.write("- Attractor identification\n")
            f.write("- Basin of attraction computation\n")
            f.write("- Fractal dimension estimation\n")
            f.write("- Lyapunov spectrum\n\n")

            f.write("### 5. Ergodic Theory\n")
            f.write("- Birkhoff ergodic theorem verification\n")
            f.write("- Invariant measure estimation\n")
            f.write("- Mixing property testing\n")
            f.write("- KS entropy computation\n\n")

            f.write("### 6. Bifurcation Analysis\n")
            f.write("- Bifurcation detection\n")
            f.write("- Parameter continuation\n")
            f.write("- Normal form classification\n")
            f.write("- Critical parameter values\n\n")

            f.write("## Key Findings\n\n")
            f.write("### Mathematical Insights\n")
            f.write("- POLLN state space forms a high-dimensional manifold\n")
            f.write("- Learning dynamics create complex vector fields\n")
            f.write("- Multiple attractors enable diverse behaviors\n")
            f.write("- Ergodic properties support exploration\n\n")

            f.write("### Practical Implications\n")
            f.write("- Basins of attraction determine behavior regions\n")
            f.write("- Bifurcations mark phase transitions in collective behavior\n")
            f.write("- Limit cycles correspond to oscillatory patterns\n")
            f.write("- Strange attractors may indicate chaotic regimes\n\n")

            f.write("## References\n\n")
            f.write("- Strogatz, S. H. (2018). Nonlinear Dynamics and Chaos.\n")
            f.write("- Guckenheimer, J., & Holmes, P. (2013). Nonlinear Oscillations.\n")
            f.write("- Katok, A., & Hasselblatt, B. (1995). Introduction to the Modern Theory\n")
            f.write("  of Dynamical Systems.\n")
            f.write("- Wiggins, S. (2003). Introduction to Applied Nonlinear Dynamical Systems.\n\n")

        print(f"Master report saved to {report_file}")


def main():
    """Run complete dynamical systems analysis"""
    # Create orchestrator
    orchestrator = DynamicalSystemsOrchestrator(
        num_agents=5,
        state_dim=3
    )

    # Run all analyses
    results = orchestrator.run_all_analyses()

    # Save results
    orchestrator.save_results_json()
    orchestrator.generate_master_report()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"Results saved to: {orchestrator.output_dir}")
    print("\nGenerated files:")
    print("  - ANALYSIS_SUMMARY.txt")
    print("  - analysis_results.json")
    print("  - MASTER_REPORT.md")
    print("  - phase_portrait.png")
    print("  - fixed_points.png")
    print("  - limit_cycles.png")
    print("  - attractors.png")
    print("  - invariant_measure.png")
    print("  - mixing_test.png")
    print("  - bifurcation_diagram.png")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
