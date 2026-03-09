"""
Master Orchestrator - Run All Meta-Learning Simulations

Runs complete meta-learning pipeline:
1. MAML implementation and optimization
2. Reptile implementation and optimization
3. Few-shot learning testing
4. Task distribution design
5. Rapid adaptation strategies
6. Meta-optimizer (generate TypeScript)

Usage:
    python run_all.py              # Run all simulations
    python run_all.py --skip-tests # Skip time-consuming tests
    python run_all.py --quick      # Quick run with reduced iterations
"""

import sys
import time
import argparse
from pathlib import Path
import subprocess


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title: str):
    """Print formatted section"""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70 + "\n")


def run_simulation(script_name: str, description: str) -> bool:
    """Run a single simulation"""
    print_section(f"Running: {description}")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd='simulations/advanced/metalearning',
            capture_output=False,
            text=True
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✓ {description} completed in {elapsed:.1f}s")
            return True
        else:
            print(f"✗ {description} failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"✗ {description} failed with error: {e}")
        return False


def main():
    """Main orchestrator"""
    parser = argparse.ArgumentParser(description='Run all meta-learning simulations')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip time-consuming test runs')
    parser.add_argument('--quick', action='store_true',
                       help='Quick run with reduced iterations')
    parser.add_argument('--step', type=str, default=None,
                       help='Run specific step (maml, reptile, few_shot, tasks, adaptation, optimizer)')

    args = parser.parse_args()

    print_header("POLLN Meta-Learning Simulation Suite")

    print("This will run the complete meta-learning pipeline:")
    print("  1. MAML implementation and optimization")
    print("  2. Reptile implementation and optimization")
    print("  3. Few-shot learning testing")
    print("  4. Task distribution design")
    print("  5. Rapid adaptation strategies")
    print("  6. Meta-optimizer (generate TypeScript)")
    print("\nEstimated time: 10-15 minutes (full), 3-5 minutes (quick)")

    if not args.quick:
        response = input("\nContinue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Create output directory
    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    results = {}

    # Step 1: MAML
    if not args.step or args.step == 'maml':
        results['maml'] = run_simulation(
            'maml_implementation.py',
            'MAML Implementation'
        )
    else:
        print("Skipping MAML...")

    # Step 2: Reptile
    if not args.step or args.step == 'reptile':
        results['reptile'] = run_simulation(
            'reptile_implementation.py',
            'Reptile Implementation'
        )
    else:
        print("Skipping Reptile...")

    # Step 3: Few-shot testing
    if not args.step or args.step == 'few_shot':
        if not args.skip_tests:
            results['few_shot'] = run_simulation(
                'few_shot_testing.py',
                'Few-Shot Learning Testing'
            )
        else:
            print("Skipping few-shot tests (--skip-tests)...")
            results['few_shot'] = None
    else:
        print("Skipping few-shot testing...")

    # Step 4: Task distribution
    if not args.step or args.step == 'tasks':
        results['tasks'] = run_simulation(
            'task_distribution.py',
            'Task Distribution Design'
        )
    else:
        print("Skipping task distribution...")

    # Step 5: Rapid adaptation
    if not args.step or args.step == 'adaptation':
        if not args.skip_tests:
            results['adaptation'] = run_simulation(
                'rapid_adaptation.py',
                'Rapid Adaptation Strategies'
            )
        else:
            print("Skipping rapid adaptation tests (--skip-tests)...")
            results['adaptation'] = None
    else:
        print("Skipping rapid adaptation...")

    # Step 6: Meta-optimizer
    if not args.step or args.step == 'optimizer':
        results['optimizer'] = run_simulation(
            'meta_optimizer.py',
            'Meta-Optimizer (Generate TypeScript)'
        )
    else:
        print("Skipping meta-optimizer...")

    # Summary
    elapsed = time.time() - start_time

    print_header("Simulation Complete")

    print("\nResults:")
    for step, success in results.items():
        if success is None:
            status = "SKIPPED"
        elif success:
            status = "✓ SUCCESS"
        else:
            status = "✗ FAILED"
        print(f"  {step}: {status}")

    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")

    # Generated files
    print_header("Generated Files")

    print("\nTypeScript:")
    print("  - src/core/meta/learning.ts")

    print("\nConfiguration files:")
    print("  - simulations/advanced/metalearning/maml_config.json")
    print("  - simulations/advanced/metalearning/reptile_config.json")
    print("  - simulations/advanced/metalearning/few_shot_config.json")
    print("  - simulations/advanced/metalearning/task_config.json")
    print("  - simulations/advanced/metalearning/rapid_adaptation_config.json")
    print("  - simulations/advanced/metalearning/meta_learning_config.json")

    print("\nDocumentation:")
    print("  - simulations/advanced/metalearning/META_LEARNING_SUMMARY.txt")
    print("  - simulations/advanced/metalearning/README.md")
    print("  - simulations/advanced/metalearning/META_LEARNING_GUIDE.md")

    print("\nVisualizations:")
    print("  - simulations/advanced/metalearning/maml_hyperparameters.png")
    print("  - simulations/advanced/metalearning/maml_reptile_comparison.png")
    print("  - simulations/advanced/metalearning/few_shot_sample_efficiency.png")
    print("  - simulations/advanced/metalearning/adaptation_quality.png")
    print("  - simulations/advanced/metalearning/task_distribution.png")
    print("  - simulations/advanced/metalearning/rapid_adaptation_comparison.png")

    # Next steps
    print_header("Next Steps")

    print("\n1. Review generated TypeScript:")
    print("   cat src/core/meta/learning.ts")

    print("\n2. Run tests:")
    print("   python simulations/advanced/metalearning/test_metalearning.py")

    print("\n3. Integrate into POLLN:")
    print("   import {{ META_LEARNING_CONFIG }} from './core/meta/learning'")

    print("\n4. Use in agents:")
    print("   const method = selectMetaLearningMethod({ accuracy: 'high', speed: 'fast' }})")

    print("\n" + "=" * 70)
    print("Meta-learning simulation suite complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
