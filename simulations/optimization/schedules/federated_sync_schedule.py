"""
Federated Sync Schedule Optimization
=====================================
Discovers optimal federated synchronization schedules for multi-colony learning.

Strategies to Test:
1. Fixed frequency (every N episodes)
2. Exponential backoff (sync less frequently over time)
3. Adaptive based on divergence
4. Adaptive based on performance gap
5. Event-driven (sync on significant updates)
6. Hierarchical (local clusters sync more frequently)
7. Gossip-style (random pairwise sync)
8. Elastic (sync more when colony sizes differ)
9. Learning rate dependent (sync when learning slows)
10. Hybrid (combination of strategies)

Goal: Find optimal sync cadence that balances:
- Communication cost (fewer syncs = less overhead)
- Knowledge sharing (more syncs = faster convergence)
- Privacy (fewer syncs = less data exposure)
- Robustness (regular syncs prevent drift)

Output: Optimal sync schedule for federated.ts
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import seaborn as sns

sns.set_style("whitegrid")


@dataclass
class SyncResult:
    """Results from testing a sync schedule"""
    schedule_name: str
    final_performance: float
    convergence_speed: int
    communication_cost: float
    knowledge_transfer: float
    privacy_preservation: float
    combined_score: float
    schedule_params: Dict


class FederatedSchedules:
    """Various federated sync schedule implementations"""

    @staticmethod
    def fixed_frequency(sync_every: int, total_steps: int) -> np.ndarray:
        """Fixed frequency synchronization"""
        sync_mask = np.zeros(total_steps, dtype=bool)
        sync_mask[::sync_every] = True
        return sync_mask

    @staticmethod
    def exponential_backoff(initial_interval: int, total_steps: int,
                             max_interval: int = 500,
                             growth_factor: float = 1.1) -> np.ndarray:
        """Exponentially increasing sync intervals"""
        sync_mask = np.zeros(total_steps, dtype=bool)
        interval = initial_interval
        next_sync = interval

        for step in range(total_steps):
            if step >= next_sync:
                sync_mask[step] = True
                interval = min(max_interval, int(interval * growth_factor))
                next_sync = step + interval

        return sync_mask

    @staticmethod
    def adaptive_divergence(total_steps: int,
                            divergence_threshold: float = 0.3,
                            min_interval: int = 10) -> np.ndarray:
        """Adaptive sync based on model divergence"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Simulated divergence between colonies
        base_divergence = 0.5 * np.exp(-np.arange(total_steps) / 300)
        divergence = base_divergence + np.random.randn(total_steps) * 0.1

        last_sync = -min_interval

        for step in range(total_steps):
            if step - last_sync >= min_interval and divergence[step] > divergence_threshold:
                sync_mask[step] = True
                last_sync = step

        return sync_mask

    @staticmethod
    def adaptive_performance_gap(total_steps: int,
                                  gap_threshold: float = 0.2,
                                  min_interval: int = 10) -> np.ndarray:
        """Adaptive sync based on performance gap between colonies"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Simulated performance gap between best and worst colony
        base_gap = 0.4 * np.exp(-np.arange(total_steps) / 200)
        performance_gap = base_gap + np.random.randn(total_steps) * 0.05

        last_sync = -min_interval

        for step in range(total_steps):
            if step - last_sync >= min_interval and performance_gap[step] > gap_threshold:
                sync_mask[step] = True
                last_sync = step

        return sync_mask

    @staticmethod
    def event_driven(total_steps: int,
                     event_probability: float = 0.02,
                     min_interval: int = 20) -> np.ndarray:
        """Event-driven synchronization"""
        sync_mask = np.zeros(total_steps, dtype=bool)
        last_sync = -min_interval

        for step in range(total_steps):
            if step - last_sync >= min_interval:
                # Significant update event
                if np.random.random() < event_probability:
                    sync_mask[step] = True
                    last_sync = step

        return sync_mask

    @staticmethod
    def hierarchical(total_steps: int,
                      local_cluster_interval: int = 50,
                      global_sync_interval: int = 200) -> np.ndarray:
        """Hierarchical: local clusters sync more frequently"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Mark which syncs are global (True) vs local (False but still sync)
        # For simplicity, we just track all syncs
        sync_mask[::local_cluster_interval] = True

        return sync_mask

    @staticmethod
    def gossip_style(total_steps: int,
                      gossip_probability: float = 0.05) -> np.ndarray:
        """Gossip-style: random pairwise synchronization"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        for step in range(total_steps):
            if np.random.random() < gossip_probability:
                sync_mask[step] = True

        return sync_mask

    @staticmethod
    def elastic(total_steps: int,
                base_interval: int = 100,
                size_sensitivity: float = 0.1) -> np.ndarray:
        """Elastic: sync more when colony sizes differ"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Simulated colony size difference
        size_diff = 0.5 * np.sin(np.arange(total_steps) / 200) + 0.5

        next_sync = 0
        for step in range(total_steps):
            if step >= next_sync:
                sync_mask[step] = True
                # Larger size difference -> more frequent sync
                interval = int(base_interval * (1 - size_sensitivity * size_diff[step]))
                next_sync = step + max(20, interval)

        return sync_mask

    @staticmethod
    def learning_rate_dependent(total_steps: int,
                                 learning_rate_threshold: float = 0.001) -> np.ndarray:
        """Sync when learning rate decreases below threshold"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Simulated learning rate schedule
        learning_rate = 0.1 * np.exp(-np.arange(total_steps) / 200)

        last_sync = -50
        for step in range(total_steps):
            if step - last_sync >= 50 and learning_rate[step] < learning_rate_threshold:
                sync_mask[step] = True
                last_sync = step

        return sync_mask

    @staticmethod
    def hybrid(total_steps: int,
                base_interval: int = 100,
                divergence_threshold: float = 0.3) -> np.ndarray:
        """Hybrid: combination of strategies"""
        sync_mask = np.zeros(total_steps, dtype=bool)

        # Simulated divergence
        base_divergence = 0.5 * np.exp(-np.arange(total_steps) / 300)
        divergence = base_divergence + np.random.randn(total_steps) * 0.1

        next_sync = base_interval
        for step in range(total_steps):
            # Sync if scheduled OR if divergence is high
            if step >= next_sync or divergence[step] > divergence_threshold:
                sync_mask[step] = True
                next_sync = step + base_interval

        return sync_mask


class FederatedColony:
    """Simulates a single colony in federated learning"""

    def __init__(self, colony_id: int, state_dim: int = 10, seed: int = 42):
        np.random.seed(seed + colony_id)
        self.colony_id = colony_id
        self.state_dim = state_dim

        # Colony-specific policy
        self.policy = np.random.randn(state_dim) * 0.1

        # Performance tracking
        self.performance_history = []

        # Local data distribution (slightly different per colony)
        self.data_shift = np.random.randn(state_dim) * 0.2

    def local_update(self, learning_rate: float = 0.01):
        """Perform local update"""
        # Simulated gradient step
        gradient = np.random.randn(self.state_dim) + self.data_shift
        self.policy -= learning_rate * gradient

        # Evaluate performance
        performance = np.mean(np.abs(self.policy)) + np.random.randn() * 0.1
        self.performance_history.append(max(0, performance))

    def sync(self, other_colonies: List['FederatedColony'],
              aggregation: str = 'average'):
        """Synchronize with other colonies"""
        if aggregation == 'average':
            # Average policies
            all_policies = np.array([c.policy for c in other_colonies])
            avg_policy = np.mean(all_policies, axis=0)

            # Update self (soft update)
            self.policy = 0.9 * self.policy + 0.1 * avg_policy

        elif aggregation == 'weighted':
            # Weight by performance
            performances = np.array([c.performance_history[-1] if c.performance_history else 0
                                    for c in other_colonies])
            performances = np.maximum(performances, 0.01)  # Avoid division by zero
            weights = performances / np.sum(performances)

            all_policies = np.array([c.policy for c in other_colonies])
            weighted_policy = np.sum(all_policies * weights[:, np.newaxis], axis=0)

            self.policy = 0.9 * self.policy + 0.1 * weighted_policy


class FederatedSimulator:
    """Simulates federated learning across multiple colonies"""

    def __init__(self, num_colonies: int = 5, state_dim: int = 10, seed: int = 42):
        self.num_colonies = num_colonies
        self.state_dim = state_dim

        self.colonies = [
            FederatedColony(i, state_dim, seed)
            for i in range(num_colonies)
        ]

    def step(self, sync_mask: bool, learning_rate: float = 0.01):
        """Execute one step of federated learning"""
        # Local updates
        for colony in self.colonies:
            colony.local_update(learning_rate)

        # Synchronization
        if sync_mask:
            # All colonies sync with each other
            for colony in self.colonies:
                colony.sync(self.colonies)

    def get_average_performance(self) -> float:
        """Get average performance across all colonies"""
        performances = [
            colony.performance_history[-1] if colony.performance_history else 0
            for colony in self.colonies
        ]
        return np.mean(performances)

    def get_divergence(self) -> float:
        """Measure divergence between colony policies"""
        policies = np.array([c.policy for c in self.colonies])
        mean_policy = np.mean(policies, axis=0)

        divergences = [
            np.linalg.norm(c.policy - mean_policy)
            for c in self.colonies
        ]

        return np.mean(divergences)

    def get_performance_gap(self) -> float:
        """Get performance gap between best and worst colony"""
        performances = [
            colony.performance_history[-1] if colony.performance_history else 0
            for colony in self.colonies
        ]

        return np.max(performances) - np.min(performances)


class ScheduleOptimizer:
    """Optimizes federated sync schedules"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.schedules = FederatedSchedules()

    def test_sync_schedule(self, schedule_name: str, params: Dict,
                           num_steps: int = 1000,
                           num_colonies: int = 5,
                           num_runs: int = 3) -> SyncResult:
        """Test a sync schedule"""
        schedule_func = getattr(self.schedules, schedule_name)
        sync_mask = schedule_func(**params, total_steps=num_steps)

        all_final_performance = []
        all_convergence_speed = []
        all_communication_cost = []
        all_knowledge_transfer = []
        all_privacy_preservation = []

        for run in range(num_runs):
            simulator = FederatedSimulator(num_colonies=num_colonies, seed=42 + run)

            performance_history = []
            divergence_history = []

            for step in range(num_steps):
                should_sync = sync_mask[step]
                simulator.step(should_sync)

                if step % 10 == 0:
                    performance_history.append(simulator.get_average_performance())
                    divergence_history.append(simulator.get_divergence())

            # Metrics
            final_performance = np.mean(performance_history[-10:])

            # Convergence speed
            target_performance = np.max(performance_history) * 0.9
            convergence_idx = np.where(np.array(performance_history) >= target_performance)[0]
            convergence_speed = convergence_idx[0] * 10 if len(convergence_idx) > 0 else num_steps

            # Communication cost: number of syncs
            communication_cost = np.sum(sync_mask)

            # Knowledge transfer: inverse of final divergence
            knowledge_transfer = 1.0 / (divergence_history[-1] + 0.01)

            # Privacy preservation: inverse of sync frequency
            privacy_preservation = 1.0 / (communication_cost / num_steps + 0.01)

            all_final_performance.append(final_performance)
            all_convergence_speed.append(convergence_speed)
            all_communication_cost.append(communication_cost)
            all_knowledge_transfer.append(knowledge_transfer)
            all_privacy_preservation.append(privacy_preservation)

        # Average across runs
        avg_performance = np.mean(all_final_performance)
        avg_convergence = np.mean(all_convergence_speed)
        avg_comm_cost = np.mean(all_communication_cost)
        avg_knowledge = np.mean(all_knowledge_transfer)
        avg_privacy = np.mean(all_privacy_preservation)

        # Combined score: performance high, cost low, knowledge high, privacy high
        combined_score = (
            avg_performance * 2.0 +
            avg_knowledge * 0.5 +
            avg_privacy * 0.3 -
            avg_comm_cost * 0.001 -
            avg_convergence * 0.0001
        )

        return SyncResult(
            schedule_name=schedule_name,
            final_performance=float(avg_performance),
            convergence_speed=int(avg_convergence),
            communication_cost=float(avg_comm_cost),
            knowledge_transfer=float(avg_knowledge),
            privacy_preservation=float(avg_privacy),
            combined_score=float(combined_score),
            schedule_params=params
        )

    def optimize_sync_schedule(self, num_steps: int = 1000) -> List[SyncResult]:
        """Find optimal sync schedule"""
        print(f"\n{'='*60}")
        print("FEDERATED SYNC SCHEDULE OPTIMIZATION")
        print(f"{'='*60}\n")

        results = []

        # Define schedule configurations
        schedule_configs = [
            ("fixed_frequency", {"sync_every": 50}),
            ("fixed_frequency", {"sync_every": 100}),
            ("fixed_frequency", {"sync_every": 200}),
            ("exponential_backoff", {"initial_interval": 50}),
            ("adaptive_divergence", {}),
            ("adaptive_performance_gap", {}),
            ("event_driven", {}),
            ("hierarchical", {}),
            ("gossip_style", {"gossip_probability": 0.05}),
            ("elastic", {}),
            ("learning_rate_dependent", {}),
            ("hybrid", {}),
        ]

        for schedule_name, params in schedule_configs:
            print(f"Testing {schedule_name}...")
            result = self.test_sync_schedule(schedule_name, params, num_steps)
            results.append(result)

            print(f"  Final Performance: {result.final_performance:.4f}")
            print(f"  Communication Cost: {result.communication_cost:.2f}")
            print(f"  Knowledge Transfer: {result.knowledge_transfer:.4f}")
            print(f"  Combined Score: {result.combined_score:.4f}")

        return results

    def visualize_results(self, results: List[SyncResult]):
        """Create visualization for sync schedule comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        sorted_results = sorted(results, key=lambda r: r.combined_score, reverse=True)
        top_results = sorted_results[:8]

        names = [r.schedule_name for r in top_results]
        colors = plt.cm.plasma(np.linspace(0, 1, len(names)))

        # Bar chart: Final Performance
        ax = axes[0, 0]
        performance = [r.final_performance for r in top_results]
        ax.barh(names, performance, color=colors)
        ax.set_xlabel("Final Performance (higher is better)")
        ax.set_title("Learning Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Communication Cost
        ax = axes[0, 1]
        cost = [r.communication_cost for r in top_results]
        ax.barh(names, cost, color=colors)
        ax.set_xlabel("Communication Cost (lower is better)")
        ax.set_title("Sync Frequency", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Knowledge Transfer
        ax = axes[1, 0]
        knowledge = [r.knowledge_transfer for r in top_results]
        ax.barh(names, knowledge, color=colors)
        ax.set_xlabel("Knowledge Transfer (higher is better)")
        ax.set_title("Convergence Quality", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Combined Score
        ax = axes[1, 1]
        scores = [r.combined_score for r in top_results]
        ax.barh(names, scores, color=colors)
        ax.set_xlabel("Combined Score (higher is better)")
        ax.set_title("Overall Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "federated_sync_comparison.png", dpi=300)
        plt.close()

        # Plot sync patterns
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        for i, result in enumerate(top_results[:3]):
            ax = axes[i]
            schedule_func = getattr(self.schedules, result.schedule_name)
            sync_mask = schedule_func(**result.schedule_params, total_steps=1000)

            # Plot sync events
            sync_times = np.where(sync_mask)[0]
            ax.vlines(sync_times, 0, 1, colors='red', alpha=0.3, linewidth=1)
            ax.scatter(sync_times, np.ones_like(sync_times) * 0.5,
                      c='red', s=10, alpha=0.6, label='Sync Event')

            ax.set_title(f"{result.schedule_name} ({result.communication_cost:.0f} syncs)",
                        fontsize=11, fontweight='bold')
            ax.set_xlim(0, 1000)
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            ax.set_xlabel("Training Step")
            ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(self.output_dir / "federated_sync_patterns.png", dpi=300)
        plt.close()

    def save_results(self, ranked_results: List[SyncResult]):
        """Save results to JSON"""
        output = {
            "optimal_schedule": ranked_results[0].schedule_name,
            "optimal_params": ranked_results[0].schedule_params,
            "all_schedules": [
                {
                    "schedule_name": r.schedule_name,
                    "final_performance": float(r.final_performance),
                    "convergence_speed": int(r.convergence_speed),
                    "communication_cost": float(r.communication_cost),
                    "knowledge_transfer": float(r.knowledge_transfer),
                    "privacy_preservation": float(r.privacy_preservation),
                    "combined_score": float(r.combined_score),
                    "params": r.schedule_params
                }
                for r in ranked_results
            ]
        }

        with open(self.output_dir / "federated_sync_optimal.json", "w") as f:
            json.dump(output, f, indent=2)


def main():
    """Run federated sync schedule optimization"""
    optimizer = ScheduleOptimizer()

    print("="*70)
    print("FEDERATED SYNC SCHEDULE OPTIMIZATION")
    print("="*70)
    print("\nTesting 12 different federated synchronization strategies:")
    print("  - Fixed frequency (3 intervals)")
    print("  - Exponential backoff")
    print("  - Adaptive (divergence & performance gap)")
    print("  - Event-driven, Hierarchical, Gossip-style")
    print("  - Elastic, Learning rate dependent, Hybrid")
    print("\nEach schedule tested with 3 runs and 5 colonies")
    print("="*70)

    results = optimizer.optimize_sync_schedule()
    ranked = sorted(results, key=lambda r: r.combined_score, reverse=True)

    optimizer.visualize_results(ranked)
    optimizer.save_results(ranked)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nBest Schedule: {ranked[0].schedule_name}")
    print(f"Parameters: {ranked[0].schedule_params}")
    print(f"Final Performance: {ranked[0].final_performance:.4f}")
    print(f"Communication Cost: {ranked[0].communication_cost:.2f}")
    print(f"Combined Score: {ranked[0].combined_score:.4f}")
    print("\nResults saved to:", optimizer.output_dir)
    print("="*70)


if __name__ == "__main__":
    main()
