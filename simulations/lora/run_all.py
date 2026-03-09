"""
Main runner for LoRA Composition Mathematics Validation

Executes all simulation modules and generates comprehensive report
"""

import argparse
from pathlib import Path
import json
import sys
import time
from datetime import datetime

# Import simulation modules
from rank_analysis import RankSufficiencyAnalyzer
from interference import InterferenceDetector
from composition import CompositionOptimizer
from scaling_laws import ScalingLawAnalyzer


class LoRASimulationRunner:
    """
    Orchestrates all LoRA composition validation simulations
    """

    def __init__(
        self,
        output_dir: Path = Path("./simulations/lora/results"),
        base_dim: int = 1024,
        quick_mode: bool = False
    ):
        self.output_dir = Path(output_dir)
        self.base_dim = base_dim
        self.quick_mode = quick_mode

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Results storage
        self.all_results = {}

        # Logging
        self.log_file = self.output_dir / f"simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def log(self, message: str):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"

        print(log_message)

        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')

    def run_rank_analysis(self) -> dict:
        """Run rank sufficiency analysis"""
        self.log("\n" + "=" * 70)
        self.log("MODULE 1: Rank Sufficiency Analysis")
        self.log("=" * 70)

        max_rank = 64 if self.quick_mode else 256
        base_dim = 512 if self.quick_mode else self.base_dim

        analyzer = RankSufficiencyAnalyzer(
            base_dim=base_dim,
            max_rank=max_rank,
            domains=["code", "writing", "analysis", "research"]
        )

        start_time = time.time()
        results = analyzer.run_full_analysis(self.output_dir)
        elapsed = time.time() - start_time

        # Test hypothesis H1
        h1_results = analyzer.test_hypothesis_h1()

        self.log(f"✓ Rank analysis completed in {elapsed:.2f}s")

        return {
            "rank_analysis": results,
            "hypothesis_h1": h1_results,
            "runtime_seconds": elapsed
        }

    def run_interference_detection(self) -> dict:
        """Run interference detection analysis"""
        self.log("\n" + "=" * 70)
        self.log("MODULE 2: Interference Detection")
        self.log("=" * 70)

        base_dim = 512 if self.quick_mode else self.base_dim

        detector = InterferenceDetector(
            base_dim=base_dim,
            ranks=[8, 16, 32, 64],
            domains=["code", "writing", "analysis", "research"]
        )

        start_time = time.time()
        results = detector.run_full_analysis(self.output_dir)
        elapsed = time.time() - start_time

        self.log(f"✓ Interference detection completed in {elapsed:.2f}s")

        return {
            "interference_detection": results,
            "runtime_seconds": elapsed
        }

    def run_composition_optimization(self) -> dict:
        """Run composition optimization analysis"""
        self.log("\n" + "=" * 70)
        self.log("MODULE 3: Composition Optimization")
        self.log("=" * 70)

        base_dim = 512 if self.quick_mode else self.base_dim
        n_scenarios = 20 if self.quick_mode else 50

        optimizer = CompositionOptimizer(
            base_dim=base_dim,
            lambda_reg=0.01
        )

        start_time = time.time()
        results = optimizer.run_full_analysis(self.output_dir)
        elapsed = time.time() - start_time

        self.log(f"✓ Composition optimization completed in {elapsed:.2f}s")

        return {
            "composition_optimization": results,
            "runtime_seconds": elapsed
        }

    def run_scaling_laws(self) -> dict:
        """Run scaling laws analysis"""
        self.log("\n" + "=" * 70)
        self.log("MODULE 4: Scaling Laws Analysis")
        self.log("=" * 70)

        analyzer = ScalingLawAnalyzer()

        start_time = time.time()
        results = analyzer.run_full_analysis(self.output_dir)
        elapsed = time.time() - start_time

        self.log(f"✓ Scaling laws analysis completed in {elapsed:.2f}s")

        return {
            "scaling_laws": results,
            "runtime_seconds": elapsed
        }

    def generate_summary_report(self) -> dict:
        """Generate comprehensive summary report"""
        self.log("\n" + "=" * 70)
        self.log("GENERATING SUMMARY REPORT")
        self.log("=" * 70)

        summary = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_dim": self.base_dim,
                "quick_mode": self.quick_mode,
                "total_runtime_seconds": sum(
                    r.get("runtime_seconds", 0)
                    for r in self.all_results.values()
                )
            },
            "modules": list(self.all_results.keys()),
            "key_findings": {}
        }

        # Extract key findings from each module
        if "rank_analysis" in self.all_results:
            rank_results = self.all_results["rank_analysis"]["rank_analysis"]
            summary["key_findings"]["rank_sufficiency"] = {
                "sufficient_ranks_95": rank_results.get("sufficient_ranks", {}),
                "hypothesis_h1_validated": self.all_results["rank_analysis"]["hypothesis_h1"]
            }

        if "interference_detection" in self.all_results:
            int_results = self.all_results["interference_detection"]["interference_detection"]
            summary["key_findings"]["interference"] = {
                "feature_importance": int_results.get("feature_importance", {}),
                "metrics_summary": int_results.get("metrics_summary", {})
            }

        if "composition_optimization" in self.all_results:
            comp_results = self.all_results["composition_optimization"]["composition_optimization"]
            summary["key_findings"]["composition"] = {
                "best_strategy": comp_results.get("inverse_sqrt_hypothesis", {}),
                "linearity_error": comp_results.get("linearity_analysis", {})
            }

        if "scaling_laws" in self.all_results:
            scale_results = self.all_results["scaling_laws"]["scaling_laws"]
            summary["key_findings"]["scaling"] = {
                "coefficients": scale_results.get("coefficients", {}),
                "optimal_configurations": scale_results.get("optimal_configurations", {})
            }

        # Save summary
        summary_path = self.output_dir / "summary_report.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.log(f"✓ Summary report saved: {summary_path}")

        return summary

    def run_all(self, modules: list = None):
        """
        Run all simulation modules

        Args:
            modules: List of modules to run. If None, runs all.
                     Options: ["rank", "interference", "composition", "scaling"]
        """
        if modules is None:
            modules = ["rank", "interference", "composition", "scaling"]

        self.log("Starting LoRA Composition Mathematics Validation")
        self.log(f"Output directory: {self.output_dir}")
        self.log(f"Quick mode: {self.quick_mode}")
        self.log(f"Modules to run: {', '.join(modules)}")

        total_start = time.time()

        try:
            # Run each module
            if "rank" in modules:
                self.all_results["rank_analysis"] = self.run_rank_analysis()

            if "interference" in modules:
                self.all_results["interference_detection"] = self.run_interference_detection()

            if "composition" in modules:
                self.all_results["composition_optimization"] = self.run_composition_optimization()

            if "scaling" in modules:
                self.all_results["scaling_laws"] = self.run_scaling_laws()

            # Generate summary
            summary = self.generate_summary_report()

            total_elapsed = time.time() - total_start

            self.log("\n" + "=" * 70)
            self.log("ALL SIMULATIONS COMPLETED SUCCESSFULLY")
            self.log("=" * 70)
            self.log(f"Total runtime: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
            self.log(f"Results directory: {self.output_dir}")
            self.log(f"Summary report: {self.output_dir / 'summary_report.json'}")

            # Print key findings
            self.log("\nKEY FINDINGS:")
            self.log("-" * 70)

            if "rank_analysis" in self.all_results:
                h1 = self.all_results["rank_analysis"]["hypothesis_h1"]
                h1_valid = all(r["h1_holds"] for r in h1.values())
                self.log(f"✓ H1 (Rank Decomposition): {'VALIDATED' if h1_valid else 'NOT VALIDATED'}")
                self.log(f"  - r=64 sufficient for 95% variance: {h1_valid}")

            if "interference_detection" in self.all_results:
                int_feat = self.all_results["interference_detection"]["interference_detection"]["feature_importance"]
                top_feature = max(int_feat.items(), key=lambda x: abs(x[1]))
                self.log(f"✓ Interference predictor trained")
                self.log(f"  - Top predictive feature: {top_feature[0]} ({top_feature[1]:.4f})")

            if "composition_optimization" in self.all_results:
                comp = self.all_results["composition_optimization"]["composition_optimization"]
                inv_sqrt_p = comp["inverse_sqrt_hypothesis"]["p_value"]
                self.log(f"✓ 1/√N weighting: {'BETTER than uniform' if inv_sqrt_p < 0.05 else 'Not significantly better'} (p={inv_sqrt_p:.4f})")

            if "scaling_laws" in self.all_results:
                coeffs = self.all_results["scaling_laws"]["scaling_laws"]["coefficients"]
                self.log(f"✓ Scaling law: accuracy = {coeffs['a']:.3f} + {coeffs['b']:.3f}·log(params) + {coeffs['c']:.3f}·n_loras - {coeffs['d']:.3f}·interference")

            self.log("=" * 70)

            return summary

        except Exception as e:
            self.log(f"\n✗ ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="LoRA Composition Mathematics Validation Suite"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./simulations/lora/results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--base-dim",
        type=int,
        default=1024,
        help="Base model dimension (for testing)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (faster but less comprehensive)"
    )
    parser.add_argument(
        "--modules",
        type=str,
        nargs="+",
        choices=["rank", "interference", "composition", "scaling"],
        help="Modules to run (default: all)"
    )

    args = parser.parse_args()

    # Create runner
    runner = LoRASimulationRunner(
        output_dir=Path(args.output_dir),
        base_dim=args.base_dim,
        quick_mode=args.quick
    )

    # Run simulations
    runner.run_all(modules=args.modules)


if __name__ == "__main__":
    main()
