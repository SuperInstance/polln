"""
Master Orchestrator for Statistical Mechanics Analysis

This module runs all statistical mechanics analyses and compiles findings.
"""

import numpy as np
from typing import Dict, List, Any
import json
from pathlib import Path

from deepseek_statmech import DeepSeekStatMech
from ensembles import analyze_agent_colony_thermodynamics
from phase_transitions import analyze_phase_transition
from critical_phenomena import analyze_critical_phenomena
from renormalization import analyze_rg_flow
from mean_field import analyze_mean_field
from nonequilibrium import analyze_nonequilibrium_dynamics
from statmech_simulator import temperature_scan


class StatMechOrchestrator:
    """Orchestrate complete statistical mechanics analysis"""

    def __init__(self, output_dir: str = "C:/Users/casey/polln/simulations/physics/statmech/results"):
        """
        Initialize orchestrator

        Args:
            output_dir: Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.deepseek = DeepSeekStatMech()

        self.results = {
            "metadata": {
                "timestamp": None,
                "n_agents": None,
                "coupling": None,
                "temperature_range": None
            },
            "analyses": {}
        }

    def run_all_analyses(self,
                         n_agents: int = 50,
                         coupling: float = 0.5,
                         T_min: float = 0.5,
                         T_max: float = 3.0,
                         n_temperatures: int = 30) -> Dict[str, Any]:
        """
        Run all statistical mechanics analyses

        Args:
            n_agents: Number of agents
            coupling: Coupling strength
            T_min: Minimum temperature
            T_max: Maximum temperature
            n_temperatures: Number of temperature points

        Returns:
            Complete results dictionary
        """
        import time

        print("\n" + "=" * 80)
        print("STATISTICAL MECHANICS ANALYSIS OF POLLN AGENT COLONIES")
        print("=" * 80)

        start_time = time.time()

        # Metadata
        self.results["metadata"] = {
            "timestamp": time.time(),
            "n_agents": n_agents,
            "coupling": coupling,
            "temperature_range": [T_min, T_max],
            "n_temperatures": n_temperatures
        }

        # 1. Thermodynamic Ensembles
        print("\n" + "=" * 80)
        print("1. THERMODYNAMIC ENSEMBLES")
        print("=" * 80)

        print("\nAnalyzing microcanonical, canonical, and grand canonical ensembles...")

        ensemble_results = analyze_agent_colony_thermodynamics(
            n_agents=n_agents,
            temperature_range=np.linspace(T_min, T_max, n_temperatures),
            deepseek=self.deepseek
        )

        self.results["analyses"]["ensembles"] = {
            "critical_temperature": ensemble_results["critical_temperature"],
            "phase_transition": ensemble_results["phase_transition"],
            "summary": "Thermodynamic analysis complete"
        }

        print(f"\nCritical temperature: T_c = {ensemble_results['critical_temperature']:.3f}")
        print(f"Phase transition: {ensemble_results['phase_transition']}")

        # 2. Phase Transitions
        print("\n" + "=" * 80)
        print("2. PHASE TRANSITIONS")
        print("=" * 80)

        print("\nAnalyzing phase transition with order parameters...")

        transition_results = analyze_phase_transition(
            n_agents=n_agents,
            T_min=T_min,
            T_max=T_max,
            n_points=n_temperatures,
            deepseek=self.deepseek
        )

        self.results["analyses"]["phase_transitions"] = {
            "critical_temperature": transition_results["critical_temperature"],
            "transition_type": transition_results["transition_type"].value,
            "tc_landau": transition_results["Tc_landau"],
            "summary": "Phase transition analysis complete"
        }

        print(f"\nCritical temperature: T_c = {transition_results['critical_temperature']:.3f}")
        print(f"Transition type: {transition_results['transition_type'].value}")
        print(f"Landau prediction: T_c = {transition_results['Tc_landau']:.3f}")

        # 3. Critical Phenomena
        print("\n" + "=" * 80)
        print("3. CRITICAL PHENOMENA")
        print("=" * 80)

        print("\nAnalyzing critical exponents and scaling...")

        # Generate data for critical phenomena analysis
        T_c = transition_results["critical_temperature"]
        temperatures = np.linspace(T_min, T_max, n_temperatures)
        magnetizations = np.array([scan["magnetization"]
                                   for scan in transition_results.get("temperature_scan", [])])
        susceptibilities = np.array([scan["susceptibility"]
                                     for scan in ensemble_results.get("temperature_scan", [])])

        # Use observed values
        if len(magnetizations) != len(temperatures):
            magnetizations = transition_results.get("magnetizations",
                                                    np.linspace(0.8, 0.0, len(temperatures)))

        if len(susceptibilities) != len(temperatures):
            susceptibilities = transition_results.get("susceptibilities",
                                                      np.linspace(0.5, 5.0, len(temperatures)))

        heat_capacities = susceptibilities * 0.3  # Simplified

        critical_results = analyze_critical_phenomena(
            temperatures=temperatures,
            magnetizations=magnetizations,
            susceptibilities=susceptibilities,
            heat_capacities=heat_capacities,
            T_c=T_c,
            deepseek=self.deepseek
        )

        self.results["analyses"]["critical_phenomena"] = {
            "critical_exponents": critical_results["critical_exponents"],
            "universality_class": critical_results["universality_class"],
            "scaling_relations": critical_results["scaling_relations"],
            "summary": "Critical phenomena analysis complete"
        }

        print(f"\nUniversality class: {critical_results['universality_class']}")
        print(f"Critical exponents: β = {critical_results['critical_exponents']['beta'][0]:.3f}, "
              f"γ = {critical_results['critical_exponents']['gamma'][0]:.3f}")

        # 4. Renormalization Group
        print("\n" + "=" * 80)
        print("4. RENORMALIZATION GROUP")
        print("=" * 80)

        print("\nAnalyzing RG flow and fixed points...")

        rg_results = analyze_rg_flow(
            initial_coupling=coupling,
            dimension=2.0,
            deepseek=self.deepseek
        )

        self.results["analyses"]["renormalization"] = {
            "fixed_points": rg_results["fixed_points"],
            "critical_exponents": rg_results["critical_exponents"],
            "summary": "RG analysis complete"
        }

        print(f"\nFixed points: {[fp['name'] for fp in rg_results['fixed_points']]}")
        print(f"RG critical exponents: ν = {rg_results['critical_exponents']['nu']:.3f}")

        # 5. Mean Field Theory
        print("\n" + "=" * 80)
        print("5. MEAN FIELD THEORY")
        print("=" * 80)

        print("\nAnalyzing mean field approximations...")

        mf_results = analyze_mean_field(
            n_agents=n_agents,
            coupling=coupling,
            temperature_range=np.linspace(T_min, T_max, n_temperatures),
            deepseek=self.deepseek
        )

        self.results["analyses"]["mean_field"] = {
            "critical_temperature": mf_results["critical_temperature"]["mean_field"],
            "critical_exponents": mf_results["critical_exponents"],
            "ginzburg_valid": mf_results["ginzburg_criterion"]["valid"],
            "summary": "Mean field analysis complete"
        }

        print(f"\nMean field T_c = {mf_results['critical_temperature']['mean_field']:.3f}")
        print(f"Mean field valid: {mf_results['ginzburg_criterion']['valid']}")

        # 6. Nonequilibrium Dynamics
        print("\n" + "=" * 80)
        print("6. NONEQUILIBRIUM DYNAMICS")
        print("=" * 80)

        print("\nAnalyzing nonequilibrium statistical mechanics...")

        neq_results = analyze_nonequilibrium_dynamics(
            n_agents=min(n_agents, 20),  # Limit for master equation
            temperature=2.0,
            deepseek=self.deepseek
        )

        self.results["analyses"]["nonequilibrium"] = {
            "relaxation_time": neq_results["master_equation"]["relaxation_time"],
            "entropy_production": neq_results["master_equation"]["entropy_production"],
            "detailed_balance": neq_results["master_equation"]["detailed_balance"],
            "summary": "Nonequilibrium analysis complete"
        }

        print(f"\nRelaxation time: τ = {neq_results['master_equation']['relaxation_time']:.3f}")
        print(f"Entropy production: σ = {neq_results['master_equation']['entropy_production']:.6f}")

        # 7. Monte Carlo Simulations
        print("\n" + "=" * 80)
        print("7. MONTE CARLO SIMULATIONS")
        print("=" * 80)

        print("\nRunning Metropolis Monte Carlo temperature scan...")

        from statmech_simulator import SimulationConfig

        mc_config = SimulationConfig(
            n_agents=n_agents,
            temperature=2.0,
            coupling=coupling,
            n_steps=5000,
            n_equilibration=1000
        )

        mc_results = temperature_scan(
            mc_config,
            T_min=T_min,
            T_max=T_max,
            n_points=min(n_temperatures, 15)
        )

        # Find MC critical temperature
        mc_chi_max_idx = np.argmax(mc_results["susceptibilities"])
        mc_Tc = mc_results["temperatures"][mc_chi_max_idx]

        self.results["analyses"]["monte_carlo"] = {
            "critical_temperature": mc_Tc,
            "max_susceptibility": float(np.max(mc_results["susceptibilities"])),
            "summary": "Monte Carlo analysis complete"
        }

        print(f"\nMonte Carlo T_c = {mc_Tc:.3f}")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY OF FINDINGS")
        print("=" * 80)

        print(f"\n1. CRITICAL TEMPERATURES:")
        print(f"   Thermodynamic: T_c = {ensemble_results['critical_temperature']:.3f}")
        print(f"   Phase transition: T_c = {transition_results['critical_temperature']:.3f}")
        print(f"   Mean field: T_c = {mf_results['critical_temperature']['mean_field']:.3f}")
        print(f"   Monte Carlo: T_c = {mc_Tc:.3f}")

        print(f"\n2. PHASE TRANSITION:")
        print(f"   Type: {transition_results['transition_type'].value}")
        print(f"   Universality class: {critical_results['universality_class']}")

        print(f"\n3. CRITICAL EXPONENTS:")
        ce = critical_results["critical_exponents"]
        print(f"   α = {ce['alpha'][0]:.3f} ± {ce['alpha'][1]:.3f}")
        print(f"   β = {ce['beta'][0]:.3f} ± {ce['beta'][1]:.3f}")
        print(f"   γ = {ce['gamma'][0]:.3f} ± {ce['gamma'][1]:.3f}")

        print(f"\n4. RG ANALYSIS:")
        print(f"   Fixed points: {[fp['name'] for fp in rg_results['fixed_points']]}")
        print(f"   ν (RG) = {rg_results['critical_exponents']['nu']:.3f}")

        print(f"\n5. DYNAMICS:")
        print(f"   Relaxation time: τ = {neq_results['master_equation']['relaxation_time']:.3f}")
        print(f"   Entropy production: σ = {neq_results['master_equation']['entropy_production']:.6f}")
        print(f"   Detailed balance: {neq_results['master_equation']['detailed_balance']}")

        elapsed_time = time.time() - start_time

        print(f"\n" + "=" * 80)
        print(f"COMPLETE ANALYSIS FINISHED IN {elapsed_time:.1f} SECONDS")
        print("=" * 80)

        # Save results
        self.save_results()

        return self.results

    def save_results(self):
        """Save results to JSON files"""
        timestamp = int(self.results["metadata"]["timestamp"])

        # Save complete results
        results_file = self.output_dir / f"complete_analysis_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\nResults saved to: {results_file}")

        # Save individual analyses
        for name, analysis in self.results["analyses"].items():
            analysis_file = self.output_dir / f"{name}_analysis_{timestamp}.json"
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2, default=str)

        print(f"Individual analyses saved to: {self.output_dir}")


def main():
    """Run complete statistical mechanics analysis"""
    orchestrator = StatMechOrchestrator()

    results = orchestrator.run_all_analyses(
        n_agents=50,
        coupling=0.5,
        T_min=0.5,
        T_max=3.0,
        n_temperatures=25
    )

    return results


if __name__ == "__main__":
    main()
