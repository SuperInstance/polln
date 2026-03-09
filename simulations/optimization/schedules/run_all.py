"""
Master Schedule Optimizer
=========================
Runs all schedule optimization simulations and generates TypeScript schedules.

This is the main entry point for discovering optimal learning schedules across
all POLLN learning mechanisms.

Workflow:
1. Run learning rate schedule optimization (TD(λ), VAE, Hebbian, Oja)
2. Run exploration schedule optimization (Plinko temperature)
3. Run dream ratio optimization
4. Run plasticity schedule optimization
5. Run federated sync schedule optimization
6. Generate unified TypeScript schedule classes
7. Create integration documentation

Usage:
    python run_all.py [--skip-optimization] [--skip-generation]
"""

import sys
import argparse
from pathlib import Path
import time
import json

# Import optimization modules
sys.path.insert(0, str(Path(__file__).parent))

from lr_schedule_search import ScheduleOptimizer as LROptimizer
from exploration_schedule import ScheduleOptimizer as ExplorationOptimizer
from dream_ratio_optimization import ScheduleOptimizer as DreamOptimizer
from plasticity_schedule import ScheduleOptimizer as PlasticityOptimizer
from federated_sync_schedule import ScheduleOptimizer as FederatedOptimizer
from schedule_generator import TypeScriptGenerator


class MasterOptimizer:
    """Orchestrates all schedule optimizations"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results_summary = {}

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)

    def optimize_learning_rates(self) -> dict:
        """Optimize learning rate schedules"""
        self.print_header("PHASE 1: LEARNING RATE OPTIMIZATION")

        print("\nOptimizing schedules for:")
        print("  - TD(λ) Value Learning")
        print("  - VAE World Model")
        print("  - Hebbian Learning")
        print("  - Oja's Rule (PCA)")

        optimizer = LROptimizer(output_dir=self.output_dir)
        results = optimizer.run_all_optimizations()

        self.results_summary['learning_rates'] = results

        print("\n✓ Learning rate optimization complete")
        return results

    def optimize_exploration(self) -> dict:
        """Optimize exploration schedules"""
        self.print_header("PHASE 2: EXPLORATION SCHEDULE OPTIMIZATION")

        print("\nOptimizing exploration strategies for:")
        print("  - Epsilon-greedy (8 schedules)")
        print("  - Boltzmann/Softmax (7 schedules)")
        print("  - UCB")
        print("  - Thompson Sampling")

        optimizer = ExplorationOptimizer(output_dir=self.output_dir)
        results = optimizer.optimize_exploration()
        ranked = optimizer.rank_results(results)

        optimizer.visualize_results(ranked)
        optimizer.save_results(ranked)

        summary = {
            'optimal_strategy': ranked[0].strategy,
            'optimal_schedule': ranked[0].schedule_name,
            'final_reward': float(ranked[0].final_reward),
            'regret': float(ranked[0].regret)
        }

        self.results_summary['exploration'] = summary

        print(f"\n✓ Exploration optimization complete")
        print(f"  Best: {ranked[0].schedule_name}")
        print(f"  Final Reward: {ranked[0].final_reward:.4f}")

        return summary

    def optimize_dream_ratio(self) -> dict:
        """Optimize dream ratio schedules"""
        self.print_header("PHASE 3: DREAM RATIO OPTIMIZATION")

        print("\nOptimizing dream scheduling for:")
        print("  - Sample efficiency")
        print("  - Policy quality")
        print("  - Computational cost")

        optimizer = DreamOptimizer(output_dir=self.output_dir)
        results = optimizer.optimize_dream_ratio()
        ranked = optimizer.rank_results(results)

        optimizer.visualize_results(ranked)
        optimizer.save_results(ranked)

        summary = {
            'optimal_schedule': ranked[0].schedule_name,
            'final_performance': float(ranked[0].final_performance),
            'sample_efficiency': float(ranked[0].sample_efficiency)
        }

        self.results_summary['dream_ratio'] = summary

        print(f"\n✓ Dream ratio optimization complete")
        print(f"  Best: {ranked[0].schedule_name}")
        print(f"  Performance: {ranked[0].final_performance:.4f}")

        return summary

    def optimize_plasticity(self) -> dict:
        """Optimize plasticity schedules"""
        self.print_header("PHASE 4: PLASTICITY SCHEDULE OPTIMIZATION")

        print("\nOptimizing plasticity for:")
        print("  - META tile differentiation")
        print("  - Catastrophic forgetting prevention")
        print("  - Adaptability vs stability")

        optimizer = PlasticityOptimizer(output_dir=self.output_dir)
        results = optimizer.optimize_plasticity()
        ranked = sorted(results, key=lambda r: r.combined_score, reverse=True)

        optimizer.visualize_results(ranked)
        optimizer.save_results(ranked)

        summary = {
            'optimal_schedule': ranked[0].schedule_name,
            'final_accuracy': float(ranked[0].final_accuracy),
            'forgetting_score': float(ranked[0].forgetting_score)
        }

        self.results_summary['plasticity'] = summary

        print(f"\n✓ Plasticity optimization complete")
        print(f"  Best: {ranked[0].schedule_name}")
        print(f"  Accuracy: {ranked[0].final_accuracy:.4f}")

        return summary

    def optimize_federated_sync(self) -> dict:
        """Optimize federated sync schedules"""
        self.print_header("PHASE 5: FEDERATED SYNC OPTIMIZATION")

        print("\nOptimizing federated synchronization for:")
        print("  - Multi-colony learning")
        print("  - Communication cost")
        print("  - Knowledge transfer")

        optimizer = FederatedOptimizer(output_dir=self.output_dir)
        results = optimizer.optimize_sync_schedule()
        ranked = sorted(results, key=lambda r: r.combined_score, reverse=True)

        optimizer.visualize_results(ranked)
        optimizer.save_results(ranked)

        summary = {
            'optimal_schedule': ranked[0].schedule_name,
            'final_performance': float(ranked[0].final_performance),
            'communication_cost': float(ranked[0].communication_cost)
        }

        self.results_summary['federated_sync'] = summary

        print(f"\n✓ Federated sync optimization complete")
        print(f"  Best: {ranked[0].schedule_name}")
        print(f"  Performance: {ranked[0].final_performance:.4f}")

        return summary

    def generate_typescript_schedules(self):
        """Generate TypeScript schedule classes"""
        self.print_header("PHASE 6: TYPESCRIPT GENERATION")

        print("\nGenerating production-ready TypeScript schedules...")

        generator = TypeScriptGenerator(self.output_dir)
        generator.generate_all()

        self.results_summary['typescript_generated'] = True

        print("\n✓ TypeScript schedules generated")
        print(f"  Location: {generator.output_dir}")

    def create_summary_report(self):
        """Create comprehensive summary report"""
        self.print_header("OPTIMIZATION SUMMARY")

        # Save summary to JSON
        summary_file = self.output_dir / "optimization_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(self.results_summary, f, indent=2)

        print("\n" + "="*70)
        print("OPTIMAL SCHEDULES DISCOVERED")
        print("="*70)

        if 'learning_rates' in self.results_summary:
            print("\nLearning Rates:")
            for algo, schedule in self.results_summary['learning_rates'].items():
                print(f"  {algo:20s} -> {schedule}")

        if 'exploration' in self.results_summary:
            exp = self.results_summary['exploration']
            print(f"\nExploration:")
            print(f"  Strategy: {exp['optimal_strategy']}")
            print(f"  Schedule: {exp['optimal_schedule']}")
            print(f"  Final Reward: {exp['final_reward']:.4f}")

        if 'dream_ratio' in self.results_summary:
            dream = self.results_summary['dream_ratio']
            print(f"\nDream Ratio:")
            print(f"  Schedule: {dream['optimal_schedule']}")
            print(f"  Performance: {dream['final_performance']:.4f}")
            print(f"  Efficiency: {dream['sample_efficiency']:.4f}")

        if 'plasticity' in self.results_summary:
            plasticity = self.results_summary['plasticity']
            print(f"\nPlasticity:")
            print(f"  Schedule: {plasticity['optimal_schedule']}")
            print(f"  Accuracy: {plasticity['final_accuracy']:.4f}")
            print(f"  Forgetting: {plasticity['forgetting_score']:.4f}")

        if 'federated_sync' in self.results_summary:
            sync = self.results_summary['federated_sync']
            print(f"\nFederated Sync:")
            print(f"  Schedule: {sync['optimal_schedule']}")
            print(f"  Performance: {sync['final_performance']:.4f}")
            print(f"  Comm Cost: {sync['communication_cost']:.2f}")

        print("\n" + "="*70)
        print(f"Summary saved to: {summary_file}")
        print("="*70)

    def run_all(self, skip_optimization: bool = False, skip_generation: bool = False):
        """Run complete optimization pipeline"""
        start_time = time.time()

        self.print_header("POLLN SCHEDULE OPTIMIZATION")

        print("\nDiscovering optimal learning schedules for all POLLN mechanisms")
        print("This may take 30-60 minutes depending on computational resources...")

        try:
            if not skip_optimization:
                # Run all optimizations
                self.optimize_learning_rates()
                self.optimize_exploration()
                self.optimize_dream_ratio()
                self.optimize_plasticity()
                self.optimize_federated_sync()
            else:
                print("\nSkipping optimization phase (using existing results)")

            if not skip_generation:
                # Generate TypeScript schedules
                self.generate_typescript_schedules()
            else:
                print("\nSkipping TypeScript generation")

            # Create summary report
            self.create_summary_report()

            elapsed = time.time() - start_time
            self.print_header("OPTIMIZATION COMPLETE")
            print(f"\nTotal time: {elapsed/60:.1f} minutes")
            print(f"Results directory: {self.output_dir}")
            print("\nNext steps:")
            print("  1. Review visualizations in results/")
            print("  2. Check generated TypeScript schedules in src/core/schedules/")
            print("  3. Run tests: npm run test -- src/core/schedules/")
            print("  4. Integrate schedules into POLLN core")

        except Exception as e:
            print(f"\n✗ Error during optimization: {e}")
            import traceback
            traceback.print_exc()
            return 1

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="POLLN Schedule Optimization - Discover optimal learning schedules"
    )

    parser.add_argument(
        '--skip-optimization',
        action='store_true',
        help='Skip optimization phase (use existing results)'
    )

    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip TypeScript generation'
    )

    args = parser.parse_args()

    optimizer = MasterOptimizer()
    exit_code = optimizer.run_all(
        skip_optimization=args.skip_optimization,
        skip_generation=args.skip_generation
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
