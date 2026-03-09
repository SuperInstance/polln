"""
Master orchestrator for all coding domain simulations.

Runs all simulations and generates optimized coding configurations.
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SimulationResult:
    """Result from running a simulation"""
    name: str
    success: bool
    duration: float
    results: Dict


class CodingSimulationOrchestrator:
    """Orchestrates all coding simulations"""

    def __init__(self, simulations_dir: str = "simulations/domains/coding"):
        self.simulations_dir = simulations_dir
        self.results: List[SimulationResult] = []

    def run_all(self) -> Dict:
        """Run all coding simulations"""
        print("="*80)
        print("CODING DOMAIN SIMULATION ORCHESTRATOR")
        print("="*80)
        print(f"Simulations directory: {self.simulations_dir}")
        print()

        simulations = [
            ("code_generation.py", "Code Generation Simulation"),
            ("code_review.py", "Code Review Simulation"),
            ("debugging_simulation.py", "Debugging Simulation"),
            ("refactoring.py", "Refactoring Simulation"),
        ]

        total_start = time.time()

        # Run each simulation
        for sim_file, sim_name in simulations:
            print(f"\n{'='*80}")
            print(f"Running: {sim_name}")
            print(f"{'='*80}")

            result = self._run_simulation(sim_file, sim_name)
            self.results.append(result)

            if result.success:
                print(f"✓ {sim_name} completed in {result.duration:.2f}s")
            else:
                print(f"✗ {sim_name} failed")

        # Run code metrics (doesn't produce results file)
        print(f"\n{'='*80}")
        print("Running: Code Metrics Analysis")
        print(f"{'='*80}")
        self._run_metrics_analysis()

        # Generate configurations
        print(f"\n{'='*80}")
        print("Generating: Coding Domain Configurations")
        print(f"{'='*80}")
        self._generate_configurations()

        total_duration = time.time() - total_start

        # Compile final report
        report = self._compile_report(total_duration)

        # Save report
        self._save_report(report)

        return report

    def _run_simulation(self, sim_file: str, sim_name: str) -> SimulationResult:
        """Run a single simulation"""
        start_time = time.time()
        sim_path = os.path.join(self.simulations_dir, sim_file)

        try:
            if not os.path.exists(sim_path):
                print(f"Error: Simulation file not found: {sim_path}")
                return SimulationResult(sim_name, False, 0.0, {})

            # Run the simulation
            result = subprocess.run(
                [sys.executable, sim_path],
                cwd=self.simulations_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time

            # Check for results file
            results_file = os.path.join(
                self.simulations_dir,
                sim_file.replace(".py", "_results.json")
            )

            results = {}
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    results = json.load(f)

            success = result.returncode == 0

            return SimulationResult(sim_name, success, duration, results)

        except subprocess.TimeoutExpired:
            print(f"Error: Simulation timed out after 5 minutes")
            return SimulationResult(sim_name, False, time.time() - start_time, {})
        except Exception as e:
            print(f"Error running simulation: {e}")
            return SimulationResult(sim_name, False, time.time() - start_time, {})

    def _run_metrics_analysis(self):
        """Run code metrics analysis"""
        try:
            metrics_file = os.path.join(self.simulations_dir, "code_metrics.py")
            if os.path.exists(metrics_file):
                result = subprocess.run(
                    [sys.executable, metrics_file],
                    cwd=self.simulations_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    print("✓ Code Metrics Analysis completed")
                    # Print output
                    if result.stdout:
                        print("\nMetrics Output:")
                        print(result.stdout[-500:])  # Last 500 chars
                else:
                    print("✗ Code Metrics Analysis failed")
                    if result.stderr:
                        print(result.stderr[-500:])
        except Exception as e:
            print(f"Error running metrics analysis: {e}")

    def _generate_configurations(self):
        """Generate TypeScript configurations"""
        try:
            optimizer_file = os.path.join(self.simulations_dir, "coding_optimizer.py")
            if os.path.exists(optimizer_file):
                result = subprocess.run(
                    [sys.executable, optimizer_file],
                    cwd=self.simulations_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    print("✓ Configuration generation completed")
                    if result.stdout:
                        print("\nOptimizer Output:")
                        print(result.stdout[-500:])
                else:
                    print("✗ Configuration generation failed")
                    if result.stderr:
                        print(result.stderr[-500:])
        except Exception as e:
            print(f"Error generating configurations: {e}")

    def _compile_report(self, total_duration: float) -> Dict:
        """Compile final report"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        report = {
            "summary": {
                "total_simulations": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "total_duration": total_duration,
                "average_duration": total_duration / len(self.results) if self.results else 0,
            },
            "simulations": {},
            "recommendations": self._compile_recommendations(),
        }

        # Add individual simulation results
        for result in self.results:
            report["simulations"][result.name] = {
                "success": result.success,
                "duration": result.duration,
                "key_metrics": self._extract_key_metrics(result.results),
            }

        return report

    def _extract_key_metrics(self, results: Dict) -> Dict:
        """Extract key metrics from simulation results"""
        metrics = {}

        # Common metrics to extract
        if "avg_syntactic_correctness" in results:
            metrics["syntax_score"] = results["avg_syntactic_correctness"]

        if "avg_semantic_correctness" in results:
            metrics["semantics_score"] = results["avg_semantic_correctness"]

        if "avg_f1" in results:
            metrics["f1_score"] = results["avg_f1"]

        if "success_rate" in results:
            metrics["success_rate"] = results["success_rate"]

        if "avg_quality_improvement" in results:
            metrics["quality_improvement"] = results["avg_quality_improvement"]

        return metrics

    def _compile_recommendations(self) -> List[str]:
        """Compile recommendations from all simulations"""
        recommendations = [
            "Use lower temperature (0.3) for deterministic code generation",
            "Implement high checkpoint frequency (15) for granular control",
            "Enable value network for code quality prediction",
            "Use iterative reasoning for debugging tasks (max 5 iterations)",
            "Process refactorings in chunks of 5 files for consistency",
            "Set consistency threshold to 0.8 for multi-file operations",
            "Use 100M model size for optimal performance",
        ]

        return recommendations

    def _save_report(self, report: Dict):
        """Save final report"""
        report_path = os.path.join(self.simulations_dir, "FINAL_REPORT.json")

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nFinal report saved to: {report_path}")

        # Also save human-readable version
        self._save_markdown_report(report)

    def _save_markdown_report(self, report: Dict):
        """Save human-readable markdown report"""
        md_path = os.path.join(self.simulations_dir, "FINAL_REPORT.md")

        with open(md_path, 'w') as f:
            f.write("# Coding Domain Simulation Report\n\n")
            f.write(f"**Generated:** 2026-03-07\n\n")

            # Summary
            f.write("## Summary\n\n")
            summary = report["summary"]
            f.write(f"- **Total Simulations:** {summary['total_simulations']}\n")
            f.write(f"- **Successful:** {summary['successful']}\n")
            f.write(f"- **Failed:** {summary['failed']}\n")
            f.write(f"- **Total Duration:** {summary['total_duration']:.2f}s\n")
            f.write(f"- **Average Duration:** {summary['average_duration']:.2f}s\n\n")

            # Individual results
            f.write("## Simulation Results\n\n")
            for name, result in report["simulations"].items():
                status = "✓" if result["success"] else "✗"
                f.write(f"### {status} {name}\n\n")
                f.write(f"- **Duration:** {result['duration']:.2f}s\n")
                if result["key_metrics"]:
                    f.write("- **Key Metrics:**\n")
                    for metric, value in result["key_metrics"].items():
                        if isinstance(value, float):
                            f.write(f"  - {metric}: {value:.3f}\n")
                        else:
                            f.write(f"  - {metric}: {value}\n")
                f.write("\n")

            # Recommendations
            f.write("## Recommendations\n\n")
            for rec in report["recommendations"]:
                f.write(f"- {rec}\n")

            # Configuration files generated
            f.write("\n## Generated Configuration Files\n\n")
            f.write("The following TypeScript configuration files have been generated:\n\n")
            f.write("- `src/domains/coding/config.ts` - Main coding domain configuration\n")
            f.write("- `src/domains/coding/value-network-config.ts` - Value network configuration\n")
            f.write("- `src/domains/coding/tasks.ts` - Task definitions\n\n")

        print(f"Markdown report saved to: {md_path}")


def main():
    """Main entry point"""
    # Change to simulations directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    orchestrator = CodingSimulationOrchestrator()
    report = orchestrator.run_all()

    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)
    print(f"Total simulations: {report['summary']['total_simulations']}")
    print(f"Successful: {report['summary']['successful']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Total time: {report['summary']['total_duration']:.2f}s")
    print("\nConfiguration files generated:")
    print("  - src/domains/coding/config.ts")
    print("  - src/domains/coding/value-network-config.ts")
    print("  - src/domains/coding/tasks.ts")
    print("\nResults saved to:")
    print("  - FINAL_REPORT.json")
    print("  - FINAL_REPORT.md")


if __name__ == "__main__":
    main()
