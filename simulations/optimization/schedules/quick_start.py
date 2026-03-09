#!/usr/bin/env python3
"""
Quick Start Script for POLLN Schedule Optimization
==================================================
Runs a fast subset of optimizations to demonstrate functionality.

For full optimization, run: python run_all.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("  POLLN SCHEDULE OPTIMIZATION - QUICK START")
    print("="*70)
    print("\nThis will run a fast subset of optimizations (~5 minutes)")
    print("For full optimization (30-60 min), run: python run_all.py")
    print("="*70)


def quick_learning_rate_optimization():
    """Run learning rate optimization with reduced steps"""
    print("\n[1/5] Learning Rate Optimization (fast mode)...")
    print("  Testing 4 schedules × 2 algorithms...")

    from lr_schedule_search import ScheduleOptimizer

    # Use faster settings
    optimizer = ScheduleOptimizer()

    # Just test TD(λ) and VAE with fewer steps
    for algorithm in ['td_lambda', 'vae']:
        results = optimizer.optimize_for_algorithm(
            algorithm=algorithm,
            num_steps=200,  # Reduced from 1000
            num_runs=2      # Reduced from 5
        )
        ranked = optimizer.rank_schedules(results)
        print(f"  Best for {algorithm}: {ranked[0].schedule_name}")

    print("  ✓ Learning rate optimization complete")


def quick_exploration_optimization():
    """Run exploration optimization with reduced steps"""
    print("\n[2/5] Exploration Optimization (fast mode)...")
    print("  Testing 6 strategies...")

    from exploration_schedule import ScheduleOptimizer as ExplorationOptimizer

    optimizer = ExplorationOptimizer()

    # Test subset of strategies
    results = []
    test_configs = [
        ("epsilon_constant", {"epsilon": 0.1}),
        ("epsilon_linear", {"initial_epsilon": 0.5, "min_epsilon": 0.01}),
        ("temperature_exponential", {"initial_temp": 2.5, "min_temp": 0.1}),
        ("temperature_cosine", {"initial_temp": 2.5, "min_temp": 0.1}),
    ]

    for schedule_name, params in test_configs:
        if 'epsilon' in schedule_name:
            result = optimizer.test_epsilon_schedule(
                schedule_name, params,
                num_steps=200,  # Reduced
                num_runs=2      # Reduced
            )
        else:
            result = optimizer.test_boltzmann_schedule(
                schedule_name, params,
                num_steps=200,
                num_runs=2
            )
        results.append(result)
        print(f"  Tested {schedule_name}: Reward = {result.final_reward:.4f}")

    ranked = optimizer.rank_results(results)
    print(f"  ✓ Exploration optimization complete")
    print(f"  Best: {ranked[0].schedule_name}")


def quick_dream_optimization():
    """Run dream ratio optimization with reduced steps"""
    print("\n[3/5] Dream Ratio Optimization (fast mode)...")

    from dream_ratio_optimization import ScheduleOptimizer as DreamOptimizer

    optimizer = DreamOptimizer()

    # Test subset
    test_configs = [
        ("constant", {"ratio": 0.5}),
        ("high_early_low_late", {"initial_ratio": 0.8, "min_ratio": 0.1}),
        ("one_cycle", {"initial_ratio": 0.2}),
    ]

    for schedule_name, params in test_configs:
        result = optimizer.test_dream_schedule(
            schedule_name, params,
            num_episodes=200,  # Reduced
            num_runs=2
        )
        print(f"  {schedule_name}: Performance = {result.final_performance:.4f}")

    print("  ✓ Dream ratio optimization complete")


def quick_plasticity_optimization():
    """Run plasticity optimization with reduced steps"""
    print("\n[4/5] Plasticity Optimization (fast mode)...")

    from plasticity_schedule import ScheduleOptimizer as PlasticityOptimizer

    optimizer = PlasticityOptimizer()

    # Test subset
    test_configs = [
        ("constant", {"plasticity": 0.5}),
        ("exponential_decay", {"initial_plasticity": 1.0}),
        ("u_shaped", {"initial_plasticity": 1.0}),
    ]

    for schedule_name, params in test_configs:
        result = optimizer.test_plasticity_schedule(
            schedule_name, params,
            num_steps=200,  # Reduced
            num_runs=2
        )
        print(f"  {schedule_name}: Accuracy = {result.final_accuracy:.4f}")

    print("  ✓ Plasticity optimization complete")


def quick_federated_optimization():
    """Run federated sync optimization with reduced steps"""
    print("\n[5/5] Federated Sync Optimization (fast mode)...")

    from federated_sync_schedule import ScheduleOptimizer as FederatedOptimizer

    optimizer = FederatedOptimizer()

    # Test subset
    test_configs = [
        ("fixed_frequency", {"sync_every": 50}),
        ("adaptive_divergence", {}),
        ("hybrid", {}),
    ]

    for schedule_name, params in test_configs:
        result = optimizer.test_sync_schedule(
            schedule_name, params,
            num_steps=200,  # Reduced
            num_colonies=3,
            num_runs=1
        )
        print(f"  {schedule_name}: Performance = {result.final_performance:.4f}")

    print("  ✓ Federated sync optimization complete")


def generate_sample_schedules():
    """Generate sample TypeScript schedules"""
    print("\n[6/6] Generating sample TypeScript schedules...")

    from schedule_generator import TypeScriptGenerator

    # Create dummy results for demonstration
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Generate TypeScript
    generator = TypeScriptGenerator(results_dir)
    generator.generate_all()

    print("  ✓ TypeScript schedules generated")
    print(f"  Location: {generator.output_dir}")


def print_summary():
    """Print summary"""
    print("\n" + "="*70)
    print("QUICK START COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  - results/*.png (visualizations)")
    print("  - results/*.json (optimal schedules)")
    print("  - src/core/schedules/*.ts (TypeScript classes)")
    print("\nNext steps:")
    print("  1. Review visualizations in results/")
    print("  2. Check optimal schedules in JSON files")
    print("  3. Use TypeScript schedules in POLLN core")
    print("\nFor full optimization, run:")
    print("  python run_all.py")
    print("\n" + "="*70)


def main():
    """Run quick start optimization"""
    print_banner()

    try:
        # Run reduced optimizations
        quick_learning_rate_optimization()
        quick_exploration_optimization()
        quick_dream_optimization()
        quick_plasticity_optimization()
        quick_federated_optimization()

        # Generate TypeScript schedules
        generate_sample_schedules()

        # Print summary
        print_summary()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
