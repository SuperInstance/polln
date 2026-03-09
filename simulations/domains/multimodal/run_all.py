"""
Master orchestrator for multi-modal simulations

Runs all multi-modal optimization simulations and generates the final configuration.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


class SimulationRunner:
    """Run all multi-modal simulations"""

    def __init__(self, base_dir: str = "C:/Users/casey/polln"):
        self.base_dir = Path(base_dir)
        self.sim_dir = self.base_dir / "simulations" / "domains" / "multimodal"
        self.results_dir = self.sim_dir / "results"

    def setup(self):
        """Setup directories"""
        print("Setting up directories...")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created: {self.results_dir}")

    def run_simulation(self, script_name: str, description: str) -> bool:
        """Run a single simulation"""
        print(f"\n{'='*80}")
        print(f"Running: {description}")
        print(f"Script: {script_name}")
        print('='*80)

        script_path = self.sim_dir / script_name

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max per simulation
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            if result.returncode == 0:
                print(f"✓ {description} completed successfully")
                return True
            else:
                print(f"✗ {description} failed with return code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print(f"✗ {description} timed out")
            return False
        except Exception as e:
            print(f"✗ {description} failed with error: {e}")
            return False

    def run_all_simulations(self):
        """Run all simulations in sequence"""

        start_time = time.time()

        print("\n" + "="*80)
        print("MULTI-MODAL SIMULATION SUITE")
        print("="*80)
        print(f"Base directory: {self.base_dir}")
        print(f"Simulation directory: {self.sim_dir}")
        print(f"Results directory: {self.results_dir}")

        # Setup
        self.setup()

        # Define simulations
        simulations = [
            ("multimodal_architecture.py", "Multi-modal Architecture Simulation"),
            ("cross_modal_attention.py", "Cross-modal Attention Optimization"),
            ("modality_embedding.py", "Modality Embedding Optimization"),
            ("multimodal_reasoning.py", "Multi-modal Reasoning Simulation"),
            ("generation_quality.py", "Generation Quality Simulation"),
        ]

        # Run simulations
        results = {}
        for script_name, description in simulations:
            success = self.run_simulation(script_name, description)
            results[description] = success

            if not success:
                print(f"\nWarning: {description} failed, continuing...")

        # Generate final configuration
        print(f"\n{'='*80}")
        print("Generating final multi-modal configuration...")
        print('='*80)

        success = self.run_simulation(
            "multimodal_optimizer.py",
            "Multi-modal Configuration Optimizer"
        )
        results["Configuration Optimizer"] = success

        # Summary
        elapsed_time = time.time() - start_time

        print("\n" + "="*80)
        print("SIMULATION SUMMARY")
        print("="*80)
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"\nResults:")

        for description, success in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {status}: {description}")

        # Check if config was generated
        config_path = self.base_dir / "src" / "domains" / "multimodal" / "config.ts"
        if config_path.exists():
            print(f"\n✓ Configuration file generated: {config_path}")
        else:
            print(f"\n✗ Configuration file not found: {config_path}")

        return all(results.values())


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run multi-modal simulations")
    parser.add_argument(
        "--base-dir",
        default="C:/Users/casey/polln",
        help="Base directory for polln project"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip simulations that already have results"
    )

    args = parser.parse_args()

    runner = SimulationRunner(args.base_dir)

    if args.skip_existing:
        print("Checking for existing results...")
        # Check which results already exist
        existing = list(runner.results_dir.glob("*.json"))
        if existing:
            print(f"Found {len(existing)} existing result files")
            for f in existing:
                print(f"  - {f.name}")

    success = runner.run_all_simulations()

    if success:
        print("\n✓ All simulations completed successfully!")
        return 0
    else:
        print("\n✗ Some simulations failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
