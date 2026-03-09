"""
POLLN Graph Evolution Simulations - Main Runner
===============================================

Run all graph evolution simulations to prove optimization hypotheses.

This script orchestrates:
1. Pruning simulation - Proves optimal sparsity (H1)
2. Grafting simulation - Discovers useful connections
3. Clustering simulation - Organizes agents optimally
4. Co-evolution simulation - Validates stability (H3)
"""

import sys
import argparse
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulations.evolution.pruning import PruningSimulation, PruningExperimentConfig
from simulations.evolution.grafting import GraftingSimulation
from simulations.evolution.clustering import ClusteringSimulation
from simulations.evolution.coevolution import CoevolutionSimulation


def print_banner():
    """Print simulation banner."""
    print("\n" + "=" * 70)
    print(" " * 15 + "POLLN GRAPH EVOLUTION SIMULATIONS")
    print("=" * 70)
    print("\nProving that graph evolution optimizes agent networks")
    print("\nHypotheses:")
    print("  H1: Performance = f(sparsity) is concave (optimal ≈ 0.3-0.5)")
    print("  H2: Evolution converges to small-world topology (σ > 1)")
    print("  H3: Evolved networks are more robust")
    print("\n" + "=" * 70 + "\n")


def run_pruning_simulation(args):
    """Run pruning simulation."""
    print("\n" + "=" * 70)
    print("SIMULATION 1: PRUNING - Proving Optimal Sparsity (H1)")
    print("=" * 70)

    config = PruningExperimentConfig(
        num_agents=args.agents,
        generations=args.generations,
        num_trials=args.trials,
        threshold_range=(0.01, 0.15),
    )

    sim = PruningSimulation(config)
    analysis = sim.run_experiment()

    output_dir = Path("simulations/results/pruning")
    sim.plot_results(analysis, output_dir)

    print(f"\n✓ Pruning simulation complete!")
    print(f"  Results: {output_dir}")

    return analysis


def run_grafting_simulation(args):
    """Run grafting simulation."""
    print("\n" + "=" * 70)
    print("SIMULATION 2: GRAFTING - Discovering Useful Connections")
    print("=" * 70)

    sim = GraftingSimulation(
        num_agents=args.agents,
        generations=args.generations // 2,  # Faster
        num_trials=args.trials
    )

    analysis = sim.run_experiment()

    output_dir = Path("simulations/results/grafting")
    sim.plot_results(analysis, output_dir)

    print(f"\n✓ Grafting simulation complete!")
    print(f"  Results: {output_dir}")

    return analysis


def run_clustering_simulation(args):
    """Run clustering simulation."""
    print("\n" + "=" * 70)
    print("SIMULATION 3: CLUSTERING - Organizing Agents Optimally")
    print("=" * 70)

    sim = ClusteringSimulation(
        num_agents=args.agents * 2,
        num_communities=5,
        num_trials=args.trials
    )

    analysis = sim.run_experiment()

    output_dir = Path("simulations/results/clustering")
    sim.plot_results(analysis, output_dir)

    print(f"\n✓ Clustering simulation complete!")
    print(f"  Results: {output_dir}")

    return analysis


def run_coevolution_simulation(args):
    """Run co-evolution simulation."""
    print("\n" + "=" * 70)
    print("SIMULATION 4: CO-EVOLUTION - Validating Stability (H3)")
    print("=" * 70)

    sim = CoevolutionSimulation(
        num_agents=args.agents,
        generations=args.generations,
        num_trials=args.trials
    )

    analysis = sim.run_experiment()

    output_dir = Path("simulations/results/coevolution")
    sim.plot_results(analysis, output_dir)

    print(f"\n✓ Co-evolution simulation complete!")
    print(f"  Results: {output_dir}")

    return analysis


def generate_summary_report(pruning_analysis, grafting_analysis,
                           clustering_analysis, coevolution_analysis):
    """Generate comprehensive summary report."""
    print("\n" + "=" * 70)
    print(" " * 20 + "SIMULATION SUMMARY REPORT")
    print("=" * 70)

    # Pruning results (H1)
    print("\n" + "-" * 70)
    print("HYPOTHESIS H1: Optimal Sparsity")
    print("-" * 70)

    for strategy, data in pruning_analysis.items():
        opt_sparsity = data['optimal_sparsity']
        opt_perf = data['optimal_performance']

        status = "✓ CONFIRMED" if 0.3 <= opt_sparsity <= 0.5 else "✗ NOT CONFIRMED"

        print(f"\n{strategy.upper()}:")
        print(f"  Optimal Sparsity: {opt_sparsity:.3f}")
        print(f"  Peak Performance: {opt_perf:.4f}")
        print(f"  Status: {status}")

    # Grafting results
    print("\n" + "-" * 70)
    print("GRAFTING: Connection Discovery")
    print("-" * 70)

    for strategy, data in grafting_analysis.items():
        opt_prob = data['optimal_probability']
        opt_perf = data['optimal_performance']

        print(f"\n{strategy.upper()}:")
        print(f"  Optimal Probability: {opt_prob:.4f}")
        print(f"  Peak Performance: {opt_perf:.4f}")

    # Clustering results
    print("\n" + "-" * 70)
    print("CLUSTERING: Community Organization")
    print("-" * 70)

    for algorithm, data in clustering_analysis.items():
        overall_score = data['summary']['overall_score']['mean']
        modularity = data['summary']['modularity']['mean']

        print(f"\n{algorithm.upper()}:")
        print(f"  Overall Score: {overall_score:.4f}")
        print(f"  Modularity: {modularity:.4f}")

    # Co-evolution results (H3)
    print("\n" + "-" * 70)
    print("HYPOTHESIS H3: Network Robustness")
    print("-" * 70)

    for env_type, data in coevolution_analysis.items():
        stability = data['avg_stability']
        diversity = data['avg_diversity']

        status = "✓ STABLE" if stability > 0.5 else "✗ UNSTABLE"

        print(f"\n{env_type.upper()}:")
        print(f"  Stability: {stability:.4f}")
        print(f"  Diversity: {diversity:.4f}")
        print(f"  Status: {status}")

    # Small-world emergence (H2)
    print("\n" + "-" * 70)
    print("HYPOTHESIS H2: Small-World Emergence")
    print("-" * 70)

    small_world_found = False
    for strategy, data in grafting_analysis.items():
        for prob_data in data['prob_performance']:
            if prob_data['mean_small_world'] > 1.0:
                print(f"\n✓ Small-world topology found!")
                print(f"  Strategy: {strategy}")
                print(f"  Grafting Probability: {prob_data['probability']:.4f}")
                print(f"  Sigma (σ): {prob_data['mean_small_world']:.4f} > 1.0")
                small_world_found = True
                break

    if not small_world_found:
        print("\n✗ Small-world topology not strongly observed")
        print("  (May require different parameters or more generations)")

    print("\n" + "=" * 70)
    print("SIMULATIONS COMPLETE")
    print("=" * 70)
    print("\nAll results saved to: simulations/results/")
    print("\nTo view plots, check:")
    print("  - simulations/results/pruning/")
    print("  - simulations/results/grafting/")
    print("  - simulations/results/clustering/")
    print("  - simulations/results/coevolution/")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run POLLN graph evolution simulations"
    )

    parser.add_argument(
        "--simulation", "-s",
        choices=["all", "pruning", "grafting", "clustering", "coevolution"],
        default="all",
        help="Which simulation to run"
    )

    parser.add_argument(
        "--agents", "-n",
        type=int,
        default=100,
        help="Number of agents (default: 100)"
    )

    parser.add_argument(
        "--generations", "-g",
        type=int,
        default=500,
        help="Number of generations (default: 500)"
    )

    parser.add_argument(
        "--trials", "-t",
        type=int,
        default=5,
        help="Number of trials per condition (default: 5)"
    )

    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick run with reduced parameters"
    )

    args = parser.parse_args()

    # Adjust for quick run
    if args.quick:
        args.agents = min(args.agents, 50)
        args.generations = min(args.generations, 200)
        args.trials = min(args.trials, 3)
        print("\nQUICK RUN MODE: Reduced parameters for faster execution")

    print_banner()

    start_time = time.time()

    # Run selected simulations
    pruning_analysis = None
    grafting_analysis = None
    clustering_analysis = None
    coevolution_analysis = None

    try:
        if args.simulation in ["all", "pruning"]:
            pruning_analysis = run_pruning_simulation(args)

        if args.simulation in ["all", "grafting"]:
            grafting_analysis = run_grafting_simulation(args)

        if args.simulation in ["all", "clustering"]:
            clustering_analysis = run_clustering_simulation(args)

        if args.simulation in ["all", "coevolution"]:
            coevolution_analysis = run_coevolution_simulation(args)

        # Generate summary
        if args.simulation == "all":
            generate_summary_report(
                pruning_analysis,
                grafting_analysis,
                clustering_analysis,
                coevolution_analysis
            )

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    elapsed = time.time() - start_time

    print(f"\nTotal simulation time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print("\n" + "=" * 70)
    print("Thank you for using POLLN Graph Evolution Simulations!")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
