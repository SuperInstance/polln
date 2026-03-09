"""
POLLN Transfer Learning - Master Orchestrator
=============================================

Runs all transfer learning simulations and generates the complete
transfer system configuration.

Usage:
    python run_all.py [--skip-optimization]
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time
from datetime import datetime


class TransferOrchestrator:
    """Orchestrates all transfer learning simulations"""

    def __init__(self, base_dir: str = "simulations/advanced/transfer"):
        self.base_dir = Path(base_dir)
        self.scripts = [
            "task_similarity.py",
            "fine_tuning_strategies.py",
            "succession_efficiency.py",
            "cross_colony_transfer.py",
            "negative_transfer.py",
        ]
        self.results = {}

    def run_script(self, script_name: str) -> bool:
        """Run a single simulation script"""

        script_path = self.base_dir / script_name

        if not script_path.exists():
            print(f"   ERROR: {script_name} not found")
            return False

        print(f"\n{'=' * 70}")
        print(f"Running: {script_name}")
        print(f"{'=' * 70}")

        start_time = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per script
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"\n✓ {script_name} completed successfully ({duration:.1f}s)")
                self.results[script_name] = {
                    'success': True,
                    'duration': duration,
                    'stdout': result.stdout
                }
                return True
            else:
                print(f"\n✗ {script_name} failed")
                print(f"Error output:\n{result.stderr}")
                self.results[script_name] = {
                    'success': False,
                    'duration': duration,
                    'stderr': result.stderr
                }
                return False

        except subprocess.TimeoutExpired:
            print(f"\n✗ {script_name} timed out after 300s")
            self.results[script_name] = {
                'success': False,
                'duration': 300,
                'error': 'timeout'
            }
            return False
        except Exception as e:
            print(f"\n✗ {script_name} failed with exception: {e}")
            self.results[script_name] = {
                'success': False,
                'error': str(e)
            }
            return False

    def run_all(self, skip_optimization: bool = False) -> bool:
        """Run all simulation scripts"""

        print("=" * 70)
        print("POLLN Transfer Learning - Master Orchestrator")
        print("=" * 70)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base directory: {self.base_dir}")
        print(f"Scripts to run: {len(self.scripts)}")

        total_start = time.time()

        # Run each script
        successful = 0
        failed = 0

        for script in self.scripts:
            if self.run_script(script):
                successful += 1
            else:
                failed += 1

        # Run optimizer
        if not skip_optimization:
            print(f"\n{'=' * 70}")
            print("Running: transfer_optimizer.py")
            print(f"{'=' * 70}")

            optimizer_script = self.base_dir / "transfer_optimizer.py"
            if optimizer_script.exists():
                if self.run_script("transfer_optimizer.py"):
                    successful += 1
                else:
                    failed += 1
            else:
                print("   WARNING: transfer_optimizer.py not found, skipping")

        total_duration = time.time() - total_start

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\nTotal scripts: {len(self.scripts) + (0 if skip_optimization else 1)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")

        # Detailed results
        if failed > 0:
            print("\nFailed scripts:")
            for script, result in self.results.items():
                if not result.get('success', False):
                    print(f"  - {script}")

        # Check for output files
        print("\nGenerated files:")
        output_files = [
            "task_similarity_matrix.json",
            "finetuning_config.json",
            "finetuning_results.csv",
            "succession_config.json",
            "succession_results.csv",
            "federation_config.json",
            "federation_results.csv",
            "negative_transfer_config.json",
            "negative_transfer_results.csv",
            "optimization_summary.json",
        ]

        for file in output_files:
            file_path = self.base_dir / file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✓ {file} ({size:,} bytes)")
            else:
                print(f"  ✗ {file} (not found)")

        # Check for TypeScript output
        ts_output = Path("src/core/learning/transfer.ts")
        if ts_output.exists():
            size = ts_output.stat().st_size
            print(f"\n  ✓ TypeScript config: {ts_output} ({size:,} bytes)")
        else:
            print(f"\n  ✗ TypeScript config not generated")

        print("\n" + "=" * 70)

        return failed == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run all POLLN transfer learning simulations"
    )
    parser.add_argument(
        '--skip-optimization',
        action='store_true',
        help='Skip the transfer optimizer step'
    )
    parser.add_argument(
        '--base-dir',
        default='simulations/advanced/transfer',
        help='Base directory for simulations'
    )

    args = parser.parse_args()

    orchestrator = TransferOrchestrator(base_dir=args.base_dir)
    success = orchestrator.run_all(skip_optimization=args.skip_optimization)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
