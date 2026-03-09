"""
Dream Ratio Optimization
========================
Discovers optimal dream-to-real ratio schedules for dream-based policy optimization.

Strategies to Test:
1. Constant dream ratio (e.g., 50% dreams, 50% real)
2. Increasing dream ratio over time
3. Decreasing dream ratio over time
4. High early, low late (explore with dreams, exploit with real)
5. Low early, high late (learn basics first, then optimize)
6. Adaptive based on real episode performance
7. Adaptive based on dream prediction error
8. Cyclical (alternating phases)
9. One-cycle (dream-heavy early, real-heavy late)
10. Curriculum (harder dreams over time)

Goal: Find optimal dream ratio trajectory that balances:
- Sample efficiency (dreams are cheaper than real episodes)
- Policy quality (real data is more accurate)
- Computational cost (dreaming takes time)
- Exploration (dreams can explore more)

Output: Optimal dream ratio schedule for dreaming.ts
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import json
import seaborn as sns
from enum import Enum

sns.set_style("whitegrid")


class DreamStrategy(Enum):
    """Types of dream scheduling strategies"""
    CONSTANT = "constant"
    INCREASING = "increasing"
    DECREASING = "decreasing"
    HIGH_EARLY_LOW_LATE = "high_early_low_late"
    LOW_EARLY_HIGH_LATE = "low_early_high_late"
    ADAPTIVE_PERFORMANCE = "adaptive_performance"
    ADAPTIVE_PREDICTION_ERROR = "adaptive_prediction_error"
    CYCLICAL = "cyclical"
    ONE_CYCLE = "one_cycle"
    CURRICULUM = "curriculum"


@dataclass
class DreamResult:
    """Results from testing a dream ratio schedule"""
    strategy: str
    schedule_name: str
    final_performance: float
    sample_efficiency: float
    computational_cost: float
    convergence_speed: int
    policy_quality: float
    schedule_params: Dict


class DreamSchedules:
    """Various dream ratio schedule implementations"""

    @staticmethod
    def constant(ratio: float, total_steps: int) -> np.ndarray:
        """Constant dream ratio"""
        return np.full(total_steps, ratio)

    @staticmethod
    def increasing(initial_ratio: float, total_steps: int,
                   max_ratio: float = 0.9) -> np.ndarray:
        """Linearly increasing dream ratio"""
        return np.linspace(initial_ratio, max_ratio, total_steps)

    @staticmethod
    def decreasing(initial_ratio: float, total_steps: int,
                   min_ratio: float = 0.1) -> np.ndarray:
        """Linearly decreasing dream ratio"""
        return np.linspace(initial_ratio, min_ratio, total_steps)

    @staticmethod
    def high_early_low_late(initial_ratio: float, total_steps: int,
                            min_ratio: float = 0.1,
                            decay_rate: float = 0.995) -> np.ndarray:
        """High dream ratio early, low later (exponential decay)"""
        steps = np.arange(total_steps)
        ratio = initial_ratio * (decay_rate ** steps)
        return np.maximum(ratio, min_ratio)

    @staticmethod
    def low_early_high_late(initial_ratio: float, total_steps: int,
                            max_ratio: float = 0.9,
                            growth_rate: float = 1.005) -> np.ndarray:
        """Low dream ratio early, high later (exponential growth)"""
        steps = np.arange(total_steps)
        ratio = initial_ratio * (growth_rate ** steps)
        return np.minimum(ratio, max_ratio)

    @staticmethod
    def adaptive_performance(initial_ratio: float, total_steps: int,
                             window_size: int = 100,
                             min_ratio: float = 0.1,
                             max_ratio: float = 0.9) -> np.ndarray:
        """Adaptive based on real episode performance"""
        ratio_schedule = np.zeros(total_steps)
        current_ratio = initial_ratio

        # Simulated real episode returns (improving over time)
        real_returns = 2.0 * (1 - np.exp(-np.arange(total_steps) / 200)) + np.random.randn(total_steps) * 0.3

        for step in range(total_steps):
            if step > window_size:
                recent_returns = real_returns[max(0, step-window_size):step]
                recent_avg = np.mean(recent_returns)
                overall_avg = np.mean(real_returns[:step])

                # If performing well, decrease dreams (exploit)
                # If performing poorly, increase dreams (explore)
                if recent_avg > overall_avg * 1.1:
                    current_ratio = max(min_ratio, current_ratio * 0.98)
                elif recent_avg < overall_avg * 0.9:
                    current_ratio = min(max_ratio, current_ratio * 1.02)

            ratio_schedule[step] = current_ratio

        return ratio_schedule

    @staticmethod
    def adaptive_prediction_error(initial_ratio: float, total_steps: int,
                                   window_size: int = 100,
                                   min_ratio: float = 0.1,
                                   max_ratio: float = 0.9) -> np.ndarray:
        """Adaptive based on world model prediction error"""
        ratio_schedule = np.zeros(total_steps)
        current_ratio = initial_ratio

        # Simulated prediction error (decreases as world model improves)
        prediction_error = 1.0 * np.exp(-np.arange(total_steps) / 300) + 0.1 + \
                          np.random.randn(total_steps) * 0.05

        for step in range(total_steps):
            if step > window_size:
                recent_error = np.mean(prediction_error[max(0, step-window_size):step])

                # High prediction error -> need more dreams to improve world model
                # Low prediction error -> can rely more on real data
                if recent_error > 0.5:
                    current_ratio = min(max_ratio, current_ratio * 1.01)
                elif recent_error < 0.2:
                    current_ratio = max(min_ratio, current_ratio * 0.99)

            ratio_schedule[step] = current_ratio

        return ratio_schedule

    @staticmethod
    def cyclical(initial_ratio: float, total_steps: int,
                 cycle_length: int = 200,
                 min_ratio: float = 0.2,
                 max_ratio: float = 0.8) -> np.ndarray:
        """Cyclical dream ratio (alternating phases)"""
        steps = np.arange(total_steps)
        phase = (steps % cycle_length) / cycle_length
        ratio = min_ratio + 0.5 * (max_ratio - min_ratio) * (1 + np.cos(2 * np.pi * phase))
        return ratio

    @staticmethod
    def one_cycle(initial_ratio: float, total_steps: int,
                  max_ratio: float = 0.9,
                  min_ratio: float = 0.1) -> np.ndarray:
        """One-cycle policy: high dreams early, high real late"""
        mid_point = total_steps // 2
        schedule = np.zeros(total_steps)

        # First half: increase dream ratio
        for step in range(mid_point):
            pct = step / mid_point
            schedule[step] = initial_ratio + (max_ratio - initial_ratio) * pct

        # Second half: decrease dream ratio
        for step in range(mid_point, total_steps):
            pct = (step - mid_point) / (total_steps - mid_point)
            schedule[step] = max_ratio - (max_ratio - min_ratio) * pct

        return schedule

    @staticmethod
    def curriculum(initial_ratio: float, total_steps: int,
                   num_stages: int = 4) -> np.ndarray:
        """Curriculum: gradually increase dream difficulty"""
        schedule = np.zeros(total_steps)
        stage_length = total_steps // num_stages

        # Each stage increases dream ratio (harder dreams)
        stage_ratios = np.linspace(initial_ratio, 0.8, num_stages)

        for stage in range(num_stages):
            start = stage * stage_length
            end = min((stage + 1) * stage_length, total_steps)

            for step in range(start, end):
                progress = (step - start) / (end - start)
                schedule[step] = stage_ratios[stage]

        return schedule


class DreamingSimulator:
    """Simulates dream-based policy optimization"""

    def __init__(self, state_dim: int = 10, action_dim: int = 4, seed: int = 42):
        np.random.seed(seed)
        self.state_dim = state_dim
        self.action_dim = action_dim

        # Policy network (simple linear)
        self.policy_weights = np.random.randn(state_dim, action_dim) * 0.1

        # Value network
        self.value_weights = np.random.randn(state_dim, 1) * 0.1

        # World model (VAE-like)
        self.world_model = np.random.randn(state_dim, state_dim) * 0.1

    def select_action(self, state: np.ndarray, temperature: float = 0.1) -> int:
        """Select action using policy with temperature"""
        logits = state @ self.policy_weights
        probs = self._softmax(logits / max(temperature, 0.001))
        return np.random.choice(self.action_dim, p=probs)

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax function"""
        x_exp = np.exp(x - np.max(x))
        return x_exp / np.sum(x_exp)

    def real_episode(self, max_steps: int = 100) -> Tuple[float, List]:
        """Run a real environment episode"""
        state = np.random.randn(self.state_dim)
        total_reward = 0.0
        trajectory = []

        for step in range(max_steps):
            action = self.select_action(state)
            reward = np.random.randn() + 0.1 * action  # Simple reward
            next_state = state + np.random.randn(self.state_dim) * 0.1

            trajectory.append((state.copy(), action, reward, next_state.copy()))
            total_reward += reward
            state = next_state

        return total_reward, trajectory

    def dream_episode(self, difficulty: float = 0.5) -> Tuple[float, List]:
        """Generate and optimize a dream episode"""
        # Start from random state
        state = np.random.randn(self.state_dim)
        total_reward = 0.0
        trajectory = []

        # Dream length depends on difficulty
        max_steps = int(50 + 50 * difficulty)

        for step in range(max_steps):
            # Use world model to predict next states
            predicted_state = state @ self.world_model

            # Select action
            action = self.select_action(predicted_state)

            # Dream reward (based on exploration diversity)
            reward = difficulty * np.random.randn() + 0.2 * action

            # Next state (from world model)
            next_state = predicted_state + np.random.randn(self.state_dim) * 0.05 * difficulty

            trajectory.append((state.copy(), action, reward, next_state.copy()))
            total_reward += reward
            state = next_state

        return total_reward, trajectory

    def update_policy(self, trajectory: List, learning_rate: float = 0.01):
        """Update policy using policy gradient"""
        for state, action, reward, next_state in trajectory:
            # Simple policy gradient update
            logits = state @ self.policy_weights
            probs = self._softmax(logits)

            # Gradient: increase log prob of action * reward
            grad = np.zeros_like(self.policy_weights)
            for a in range(self.action_dim):
                if a == action:
                    grad[:, a] = state * (1 - probs[a]) * reward
                else:
                    grad[:, a] = -state * probs[a] * reward

            self.policy_weights += learning_rate * grad

    def update_world_model(self, trajectory: List, learning_rate: float = 0.01):
        """Update world model"""
        for state, action, reward, next_state in trajectory:
            # Predict next state
            predicted = state @ self.world_model

            # MSE loss
            error = next_state - predicted
            grad = -np.outer(state, error)

            self.world_model -= learning_rate * grad


class ScheduleOptimizer:
    """Optimizes dream ratio schedules"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.simulator = DreamingSimulator()
        self.schedules = DreamSchedules()

    def test_dream_schedule(self, schedule_name: str, params: Dict,
                            num_episodes: int = 1000,
                            num_runs: int = 5) -> DreamResult:
        """Test a dream ratio schedule"""
        schedule_func = getattr(self.schedules, schedule_name)
        schedule = schedule_func(**params, total_steps=num_episodes)

        all_final_performance = []
        all_sample_efficiency = []
        all_computational_cost = []
        all_convergence_speed = []
        all_policy_quality = []

        for run in range(num_runs):
            # Reset simulator
            simulator = DreamingSimulator(seed=42 + run)

            performance_history = []
            total_dreams = 0
            total_real = 0
            total_computation = 0

            for episode in range(num_episodes):
                dream_ratio = schedule[episode]

                # Decide whether to dream or run real episode
                if np.random.random() < dream_ratio:
                    # Dream episode
                    difficulty = 0.3 + 0.7 * (episode / num_episodes)  # Curriculum
                    reward, trajectory = simulator.dream_episode(difficulty)
                    total_dreams += 1
                    total_computation += 0.5  # Dreams are cheaper
                else:
                    # Real episode
                    reward, trajectory = simulator.real_episode()
                    total_real += 1
                    total_computation += 1.0  # Real episodes cost more

                # Update policy and world model
                simulator.update_policy(trajectory)
                simulator.update_world_model(trajectory)

                # Track performance (average of last 10 episodes)
                if episode >= 10:
                    recent_reward = np.mean(performance_history[-10:])
                else:
                    recent_reward = reward

                performance_history.append(reward)

            # Metrics
            final_performance = np.mean(performance_history[-100:])
            sample_efficiency = final_performance / (total_real + 0.5 * total_dreams)  # Performance per computation
            computational_cost = total_computation
            policy_quality = final_performance

            # Convergence speed
            smoothed = np.convolve(performance_history, np.ones(50)/50, mode='valid')
            target = np.max(smoothed) * 0.9
            convergence_idx = np.where(smoothed >= target)[0]
            convergence_speed = convergence_idx[0] if len(convergence_idx) > 0 else num_episodes

            all_final_performance.append(final_performance)
            all_sample_efficiency.append(sample_efficiency)
            all_computational_cost.append(computational_cost)
            all_convergence_speed.append(convergence_speed)
            all_policy_quality.append(policy_quality)

        # Average across runs
        return DreamResult(
            strategy=schedule_name,
            schedule_name=schedule_name,
            final_performance=float(np.mean(all_final_performance)),
            sample_efficiency=float(np.mean(all_sample_efficiency)),
            computational_cost=float(np.mean(all_computational_cost)),
            convergence_speed=int(np.mean(all_convergence_speed)),
            policy_quality=float(np.mean(all_policy_quality)),
            schedule_params=params
        )

    def optimize_dream_ratio(self, num_episodes: int = 1000) -> List[DreamResult]:
        """Find optimal dream ratio schedule"""
        print(f"\n{'='*60}")
        print("DREAM RATIO OPTIMIZATION")
        print(f"{'='*60}\n")

        results = []

        # Define schedule configurations
        schedule_configs = [
            ("constant", {"ratio": 0.3}),
            ("constant", {"ratio": 0.5}),
            ("constant", {"ratio": 0.7}),
            ("increasing", {"initial_ratio": 0.2, "max_ratio": 0.8}),
            ("decreasing", {"initial_ratio": 0.8, "min_ratio": 0.2}),
            ("high_early_low_late", {"initial_ratio": 0.8, "min_ratio": 0.1}),
            ("low_early_high_late", {"initial_ratio": 0.2, "max_ratio": 0.9}),
            ("adaptive_performance", {"initial_ratio": 0.5}),
            ("adaptive_prediction_error", {"initial_ratio": 0.5}),
            ("cyclical", {"initial_ratio": 0.5}),
            ("one_cycle", {"initial_ratio": 0.2}),
            ("curriculum", {"initial_ratio": 0.3}),
        ]

        for schedule_name, params in schedule_configs:
            print(f"Testing {schedule_name}...")
            result = self.test_dream_schedule(schedule_name, params, num_episodes)
            results.append(result)

            print(f"  Final Performance: {result.final_performance:.4f}")
            print(f"  Sample Efficiency: {result.sample_efficiency:.4f}")
            print(f"  Computational Cost: {result.computational_cost:.2f}")
            print(f"  Convergence: Episode {result.convergence_speed}")

        return results

    def rank_results(self, results: List[DreamResult]) -> List[DreamResult]:
        """Rank dream schedules by combined score"""
        for result in results:
            # Combined score: performance high, cost low, convergence fast
            result.combined_score = (
                result.final_performance * 2.0 +
                result.sample_efficiency * 1.0 -
                result.computational_cost * 0.001
            )

        return sorted(results, key=lambda r: r.combined_score, reverse=True)

    def visualize_results(self, results: List[DreamResult]):
        """Create visualization for dream schedule comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        ranked = sorted(results, key=lambda r: getattr(r, 'combined_score', 0), reverse=True)
        top_results = ranked[:8]

        names = [r.schedule_name for r in top_results]
        colors = plt.cm.magma(np.linspace(0, 1, len(names)))

        # Bar chart: Final Performance
        ax = axes[0, 0]
        performance = [r.final_performance for r in top_results]
        ax.barh(names, performance, color=colors)
        ax.set_xlabel("Final Performance (higher is better)")
        ax.set_title("Policy Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Sample Efficiency
        ax = axes[0, 1]
        efficiency = [r.sample_efficiency for r in top_results]
        ax.barh(names, efficiency, color=colors)
        ax.set_xlabel("Sample Efficiency (higher is better)")
        ax.set_title("Efficiency", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Computational Cost
        ax = axes[1, 0]
        cost = [r.computational_cost for r in top_results]
        ax.barh(names, cost, color=colors)
        ax.set_xlabel("Computational Cost (lower is better)")
        ax.set_title("Cost", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Combined Score
        ax = axes[1, 1]
        scores = [getattr(r, 'combined_score', 0) for r in top_results]
        ax.barh(names, scores, color=colors)
        ax.set_xlabel("Combined Score (higher is better)")
        ax.set_title("Overall Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "dream_ratio_comparison.png", dpi=300)
        plt.close()

        # Plot example schedules
        fig, ax = plt.subplots(figsize=(12, 6))

        for i, result in enumerate(top_results[:5]):
            schedule_func = getattr(self.schedules, result.schedule_name)
            schedule = schedule_func(**result.schedule_params, total_steps=1000)
            ax.plot(schedule, label=result.schedule_name, linewidth=2)

        ax.set_title("Top 5 Dream Ratio Schedules", fontsize=14, fontweight='bold')
        ax.set_xlabel("Episode")
        ax.set_ylabel("Dream Ratio")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)

        plt.tight_layout()
        plt.savefig(self.output_dir / "dream_ratio_schedules.png", dpi=300)
        plt.close()

    def save_results(self, ranked_results: List[DreamResult]):
        """Save results to JSON"""
        output = {
            "optimal_schedule": ranked_results[0].schedule_name,
            "optimal_params": ranked_results[0].schedule_params,
            "all_schedules": [
                {
                    "strategy": r.strategy,
                    "schedule_name": r.schedule_name,
                    "final_performance": float(r.final_performance),
                    "sample_efficiency": float(r.sample_efficiency),
                    "computational_cost": float(r.computational_cost),
                    "convergence_speed": int(r.convergence_speed),
                    "policy_quality": float(r.policy_quality),
                    "combined_score": float(getattr(r, 'combined_score', 0)),
                    "params": r.schedule_params
                }
                for r in ranked_results
            ]
        }

        with open(self.output_dir / "dream_ratio_optimal.json", "w") as f:
            json.dump(output, f, indent=2)


def main():
    """Run dream ratio optimization"""
    optimizer = ScheduleOptimizer()

    print("="*70)
    print("DREAM RATIO OPTIMIZATION")
    print("="*70)
    print("\nTesting 12 different dream scheduling strategies:")
    print("  - Constant ratios (0.3, 0.5, 0.7)")
    print("  - Increasing/Decreasing schedules")
    print("  - High-early-low-late / Low-early-high-late")
    print("  - Adaptive (performance & prediction error)")
    print("  - Cyclical, One-cycle, Curriculum")
    print("\nEach schedule tested with 5 runs for statistical validity")
    print("="*70)

    results = optimizer.optimize_dream_ratio()
    ranked = optimizer.rank_results(results)

    optimizer.visualize_results(ranked)
    optimizer.save_results(ranked)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nBest Schedule: {ranked[0].schedule_name}")
    print(f"Parameters: {ranked[0].schedule_params}")
    print(f"Final Performance: {ranked[0].final_performance:.4f}")
    print(f"Sample Efficiency: {ranked[0].sample_efficiency:.4f}")
    print("\nResults saved to:", optimizer.output_dir)
    print("="*70)


if __name__ == "__main__":
    main()
