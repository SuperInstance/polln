"""
Plasticity Schedule Optimization
=================================
Discovers optimal plasticity modulation schedules for META tile differentiation.

Strategies to Test:
1. Constant plasticity (no modulation)
2. Linear decay (critical period)
3. Exponential decay (rapid early learning)
4. Step decay (developmental stages)
5. Adaptive based on performance
6. Adaptive based on environmental change
7. U-shaped (high early, low mid, high late)
8. Inverse U-shaped (low early, high mid, low late)
9. Cyclical (periodic re-plasticization)
10. Homeostatic (maintain optimal plasticity)

Goal: Find optimal plasticity trajectory that balances:
- Early learning (high plasticity for rapid acquisition)
- Stability (low plasticity to retain learned patterns)
- Adaptability (re-activate plasticity when needed)
- Catastrophic forgetting prevention

Output: Optimal plasticity schedule for meta.ts
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
class PlasticityResult:
    """Results from testing a plasticity schedule"""
    schedule_name: str
    final_accuracy: float
    forgetting_score: float
    adaptation_speed: float
    stability_score: float
    combined_score: float
    schedule_params: Dict


class PlasticitySchedules:
    """Various plasticity schedule implementations"""

    @staticmethod
    def constant(plasticity: float, total_steps: int) -> np.ndarray:
        """Constant plasticity"""
        return np.full(total_steps, plasticity)

    @staticmethod
    def linear_decay(initial_plasticity: float, total_steps: int,
                     min_plasticity: float = 0.01) -> np.ndarray:
        """Linear decay (critical period)"""
        return np.linspace(initial_plasticity, min_plasticity, total_steps)

    @staticmethod
    def exponential_decay(initial_plasticity: float, total_steps: int,
                          min_plasticity: float = 0.01,
                          decay_rate: float = 0.99) -> np.ndarray:
        """Exponential decay"""
        steps = np.arange(total_steps)
        plasticity = initial_plasticity * (decay_rate ** steps)
        return np.maximum(plasticity, min_plasticity)

    @staticmethod
    def step_decay(initial_plasticity: float, total_steps: int,
                   num_stages: int = 4,
                   min_plasticity: float = 0.01) -> np.ndarray:
        """Step decay (developmental stages)"""
        schedule = np.zeros(total_steps)
        stage_length = total_steps // num_stages

        stage_plasticities = np.linspace(initial_plasticity, min_plasticity, num_stages)

        for stage in range(num_stages):
            start = stage * stage_length
            end = min((stage + 1) * stage_length, total_steps)
            schedule[start:end] = stage_plasticities[stage]

        return schedule

    @staticmethod
    def adaptive_performance(initial_plasticity: float, total_steps: int,
                             window_size: int = 100,
                             min_plasticity: float = 0.01,
                             max_plasticity: float = 1.0) -> np.ndarray:
        """Adaptive based on task performance"""
        schedule = np.zeros(total_steps)
        current_plasticity = initial_plasticity

        # Simulated performance (improves then plateaus)
        performance = 1.0 - 0.8 * np.exp(-np.arange(total_steps) / 200) + \
                     np.random.randn(total_steps) * 0.05

        for step in range(total_steps):
            if step > window_size:
                recent_perf = np.mean(performance[max(0, step-window_size):step])
                overall_perf = np.mean(performance[:step])

                # If performance is stagnating, increase plasticity
                # If performance is improving, maintain or decrease
                improvement_rate = (recent_perf - overall_perf) / (overall_perf + 1e-8)

                if improvement_rate < 0.01:  # Stagnating
                    current_plasticity = min(max_plasticity, current_plasticity * 1.02)
                elif improvement_rate > 0.05:  # Improving rapidly
                    current_plasticity = max(min_plasticity, current_plasticity * 0.99)

            schedule[step] = current_plasticity

        return schedule

    @staticmethod
    def adaptive_environment(initial_plasticity: float, total_steps: int,
                             window_size: int = 100,
                             change_frequency: int = 500,
                             min_plasticity: float = 0.01,
                             max_plasticity: float = 1.0) -> np.ndarray:
        """Adaptive based on environmental change"""
        schedule = np.zeros(total_steps)
        current_plasticity = initial_plasticity

        # Simulate environmental changes
        env_changes = np.zeros(total_steps)
        for t in range(total_steps):
            if t % change_frequency == 0 and t > 0:
                env_changes[t] = 1.0  # Environment changed

        # Smooth detection
        env_signal = np.convolve(env_changes, np.ones(window_size)/window_size, mode='same')

        for step in range(total_steps):
            if env_signal[step] > 0.5:  # Environment changing
                current_plasticity = max_plasticity
            else:  # Stable environment
                current_plasticity = max(min_plasticity, current_plasticity * 0.995)

            schedule[step] = current_plasticity

        return schedule

    @staticmethod
    def u_shaped(initial_plasticity: float, total_steps: int,
                 min_plasticity: float = 0.1,
                 peak_ratio: float = 0.3) -> np.ndarray:
        """U-shaped: high early, low mid, high late"""
        steps = np.arange(total_steps)
        mid_point = total_steps // 2

        # First half: decrease
        first_half = np.linspace(initial_plasticity, min_plasticity, mid_point)
        # Second half: increase
        second_half = np.linspace(min_plasticity, initial_plasticity * peak_ratio, total_steps - mid_point)

        return np.concatenate([first_half, second_half])

    @staticmethod
    def inverse_u_shaped(min_plasticity: float, total_steps: int,
                         max_plasticity: float = 0.9,
                         peak_ratio: float = 0.5) -> np.ndarray:
        """Inverse U-shaped: low early, high mid, low late"""
        steps = np.arange(total_steps)
        mid_point = total_steps // 2

        # First half: increase
        first_half = np.linspace(min_plasticity, max_plasticity, mid_point)
        # Second half: decrease
        second_half = np.linspace(max_plasticity, min_plasticity, total_steps - mid_point)

        return np.concatenate([first_half, second_half])

    @staticmethod
    def cyclical(initial_plasticity: float, total_steps: int,
                 cycle_length: int = 200,
                 min_plasticity: float = 0.2,
                 max_plasticity: float = 0.9) -> np.ndarray:
        """Cyclical plasticity (periodic re-plasticization)"""
        steps = np.arange(total_steps)
        phase = (steps % cycle_length) / cycle_length
        plasticity = min_plasticity + 0.5 * (max_plasticity - min_plasticity) * \
                    (1 + np.cos(2 * np.pi * phase))
        return plasticity

    @staticmethod
    def homeostatic(initial_plasticity: float, total_steps: int,
                    target_performance: float = 0.8,
                    window_size: int = 50,
                    min_plasticity: float = 0.01,
                    max_plasticity: float = 1.0) -> np.ndarray:
        """Homeostatic: maintain optimal plasticity for target performance"""
        schedule = np.zeros(total_steps)
        current_plasticity = initial_plasticity

        # Simulated performance
        performance = np.zeros(total_steps)
        for t in range(total_steps):
            base_perf = 0.5 + 0.4 * (1 - np.exp(-t / 200))
            performance[t] = base_perf + np.random.randn() * 0.1

        for step in range(total_steps):
            if step > window_size:
                recent_perf = np.mean(performance[max(0, step-window_size):step])

                # Homeostatic regulation
                error = target_performance - recent_perf

                if abs(error) < 0.05:  # At target
                    current_plasticity = max(min_plasticity, current_plasticity * 0.99)
                elif error > 0.1:  # Below target
                    current_plasticity = min(max_plasticity, current_plasticity * 1.05)
                elif error < -0.1:  # Above target
                    current_plasticity = max(min_plasticity, current_plasticity * 0.95)

            schedule[step] = current_plasticity

        return schedule


class PlasticitySimulator:
    """Simulates neural network learning with plasticity modulation"""

    def __init__(self, num_neurons: int = 100, num_patterns: int = 20, seed: int = 42):
        np.random.seed(seed)
        self.num_neurons = num_neurons
        self.num_patterns = num_patterns

        # Patterns to learn
        self.patterns = np.random.randn(num_patterns, num_neurons)
        self.patterns = self.patterns / np.linalg.norm(self.patterns, axis=1, keepdims=True)

        # Labels for patterns
        self.labels = np.random.randint(0, 2, num_patterns)

        # Network weights
        self.weights = np.random.randn(num_neurons, num_neurons) * 0.01

    def activate(self, pattern: np.ndarray) -> np.ndarray:
        """Activate network with pattern"""
        return np.tanh(pattern @ self.weights)

    def hebbian_update(self, pre: np.ndarray, post: np.ndarray,
                       plasticity: float, learning_rate: float = 0.01):
        """Hebbian update with plasticity modulation"""
        # Δw = η * plasticity * (pre * post - w)
        dw = learning_rate * plasticity * np.outer(pre, post)
        dw -= learning_rate * plasticity * 0.01 * self.weights  # Weight decay

        self.weights += dw

    def recall(self, pattern: np.ndarray) -> int:
        """Recall label for pattern"""
        activation = self.activate(pattern)
        # Simple readout: sum of activation
        return 1 if np.sum(activation) > 0 else 0

    def accuracy(self) -> float:
        """Calculate current accuracy on all patterns"""
        correct = 0
        for i in range(self.num_patterns):
            prediction = self.recall(self.patterns[i])
            if prediction == self.labels[i]:
                correct += 1

        return correct / self.num_patterns

    def catastrophic_forgetting(self, old_patterns: np.ndarray,
                                 old_labels: np.ndarray) -> float:
        """Measure catastrophic forgetting"""
        correct = 0
        for i in range(len(old_patterns)):
            prediction = self.recall(old_patterns[i])
            if prediction == old_labels[i]:
                correct += 1

        return 1.0 - (correct / len(old_patterns))  # Forgetting = 1 - accuracy


class ScheduleOptimizer:
    """Optimizes plasticity schedules"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.schedules = PlasticitySchedules()

    def test_plasticity_schedule(self, schedule_name: str, params: Dict,
                                  num_steps: int = 1000,
                                  num_runs: int = 5) -> PlasticityResult:
        """Test a plasticity schedule"""
        schedule_func = getattr(self.schedules, schedule_name)
        schedule = schedule_func(**params, total_steps=num_steps)

        all_final_accuracy = []
        all_forgetting_score = []
        all_adaptation_speed = []
        all_stability_score = []

        for run in range(num_runs):
            simulator = PlasticitySimulator(seed=42 + run)

            # Learn first half of patterns
            first_half = simulator.num_patterns // 2
            first_patterns = simulator.patterns[:first_half].copy()
            first_labels = simulator.labels[:first_half].copy()

            accuracy_history = []

            for step in range(num_steps):
                plasticity = schedule[step]

                # Select pattern to train
                if step < num_steps // 2:
                    # Learn first half
                    pattern_idx = step % first_half
                else:
                    # Learn second half (test for catastrophic forgetting)
                    pattern_idx = first_half + (step % (simulator.num_patterns - first_half))

                pattern = simulator.patterns[pattern_idx]
                activation = simulator.activate(pattern)
                simulator.hebbian_update(pattern, activation, plasticity)

                # Track accuracy
                if step % 10 == 0:
                    acc = simulator.accuracy()
                    accuracy_history.append(acc)

            # Metrics
            final_accuracy = accuracy_history[-1]

            # Catastrophic forgetting
            forgetting = simulator.catastrophic_forgetting(first_patterns, first_labels)

            # Adaptation speed: steps to reach 80% accuracy
            target_acc = 0.8
            convergence_idx = np.where(np.array(accuracy_history) >= target_acc)[0]
            adaptation_speed = convergence_idx[0] * 10 if len(convergence_idx) > 0 else num_steps

            # Stability: variance of last 20% of accuracy
            stability = np.var(accuracy_history[-20:])

            all_final_accuracy.append(final_accuracy)
            all_forgetting_score.append(forgetting)
            all_adaptation_speed.append(adaptation_speed)
            all_stability_score.append(stability)

        # Average across runs
        avg_accuracy = np.mean(all_final_accuracy)
        avg_forgetting = np.mean(all_forgetting_score)
        avg_adaptation = np.mean(all_adaptation_speed)
        avg_stability = np.mean(all_stability_score)

        # Combined score: accuracy high, forgetting low, adaptation fast, stable
        combined_score = (
            avg_accuracy * 2.0 -
            avg_forgetting * 1.0 -
            avg_adaptation * 0.001 -
            avg_stability * 0.5
        )

        return PlasticityResult(
            schedule_name=schedule_name,
            final_accuracy=float(avg_accuracy),
            forgetting_score=float(avg_forgetting),
            adaptation_speed=float(avg_adaptation),
            stability_score=float(avg_stability),
            combined_score=float(combined_score),
            schedule_params=params
        )

    def optimize_plasticity(self, num_steps: int = 1000) -> List[PlasticityResult]:
        """Find optimal plasticity schedule"""
        print(f"\n{'='*60}")
        print("PLASTICITY SCHEDULE OPTIMIZATION")
        print(f"{'='*60}\n")

        results = []

        # Define schedule configurations
        schedule_configs = [
            ("constant", {"plasticity": 0.1}),
            ("constant", {"plasticity": 0.5}),
            ("constant", {"plasticity": 1.0}),
            ("linear_decay", {"initial_plasticity": 1.0}),
            ("exponential_decay", {"initial_plasticity": 1.0}),
            ("step_decay", {"initial_plasticity": 1.0, "num_stages": 4}),
            ("adaptive_performance", {"initial_plasticity": 0.5}),
            ("adaptive_environment", {"initial_plasticity": 0.5}),
            ("u_shaped", {"initial_plasticity": 1.0}),
            ("inverse_u_shaped", {"min_plasticity": 0.1}),
            ("cyclical", {"initial_plasticity": 0.5}),
            ("homeostatic", {"initial_plasticity": 0.5}),
        ]

        for schedule_name, params in schedule_configs:
            print(f"Testing {schedule_name}...")
            result = self.test_plasticity_schedule(schedule_name, params, num_steps)
            results.append(result)

            print(f"  Final Accuracy: {result.final_accuracy:.4f}")
            print(f"  Forgetting: {result.forgetting_score:.4f}")
            print(f"  Adaptation Speed: {result.adaptation_speed:.2f}")
            print(f"  Stability: {result.stability_score:.4f}")
            print(f"  Combined Score: {result.combined_score:.4f}")

        return results

    def visualize_results(self, results: List[PlasticityResult]):
        """Create visualization for plasticity schedule comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        sorted_results = sorted(results, key=lambda r: r.combined_score, reverse=True)
        top_results = sorted_results[:8]

        names = [r.schedule_name for r in top_results]
        colors = plt.cm.viridis(np.linspace(0, 1, len(names)))

        # Bar chart: Final Accuracy
        ax = axes[0, 0]
        accuracy = [r.final_accuracy for r in top_results]
        ax.barh(names, accuracy, color=colors)
        ax.set_xlabel("Final Accuracy (higher is better)")
        ax.set_title("Learning Accuracy", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Forgetting Score
        ax = axes[0, 1]
        forgetting = [r.forgetting_score for r in top_results]
        ax.barh(names, forgetting, color=colors)
        ax.set_xlabel("Forgetting Score (lower is better)")
        ax.set_title("Catastrophic Forgetting", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Adaptation Speed
        ax = axes[1, 0]
        speed = [r.adaptation_speed for r in top_results]
        ax.barh(names, speed, color=colors)
        ax.set_xlabel("Adaptation Speed (lower is better)")
        ax.set_title("Convergence Speed", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Combined Score
        ax = axes[1, 1]
        scores = [r.combined_score for r in top_results]
        ax.barh(names, scores, color=colors)
        ax.set_xlabel("Combined Score (higher is better)")
        ax.set_title("Overall Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "plasticity_schedule_comparison.png", dpi=300)
        plt.close()

        # Plot example schedules
        fig, ax = plt.subplots(figsize=(12, 6))

        for i, result in enumerate(top_results[:5]):
            schedule_func = getattr(self.schedules, result.schedule_name)
            schedule = schedule_func(**result.schedule_params, total_steps=1000)
            ax.plot(schedule, label=result.schedule_name, linewidth=2)

        ax.set_title("Top 5 Plasticity Schedules", fontsize=14, fontweight='bold')
        ax.set_xlabel("Training Step")
        ax.set_ylabel("Plasticity")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.1)

        plt.tight_layout()
        plt.savefig(self.output_dir / "plasticity_schedule_curves.png", dpi=300)
        plt.close()

    def save_results(self, ranked_results: List[PlasticityResult]):
        """Save results to JSON"""
        output = {
            "optimal_schedule": ranked_results[0].schedule_name,
            "optimal_params": ranked_results[0].schedule_params,
            "all_schedules": [
                {
                    "schedule_name": r.schedule_name,
                    "final_accuracy": float(r.final_accuracy),
                    "forgetting_score": float(r.forgetting_score),
                    "adaptation_speed": float(r.adaptation_speed),
                    "stability_score": float(r.stability_score),
                    "combined_score": float(r.combined_score),
                    "params": r.schedule_params
                }
                for r in ranked_results
            ]
        }

        with open(self.output_dir / "plasticity_optimal_schedule.json", "w") as f:
            json.dump(output, f, indent=2)


def main():
    """Run plasticity schedule optimization"""
    optimizer = ScheduleOptimizer()

    print("="*70)
    print("PLASTICITY SCHEDULE OPTIMIZATION")
    print("="*70)
    print("\nTesting 12 different plasticity scheduling strategies:")
    print("  - Constant plasticity (3 levels)")
    print("  - Linear & Exponential decay")
    print("  - Step decay (developmental stages)")
    print("  - Adaptive (performance & environment)")
    print("  - U-shaped & Inverse U-shaped")
    print("  - Cyclical & Homeostatic")
    print("\nEach schedule tested with 5 runs for statistical validity")
    print("="*70)

    results = optimizer.optimize_plasticity()
    ranked = sorted(results, key=lambda r: r.combined_score, reverse=True)

    optimizer.visualize_results(ranked)
    optimizer.save_results(ranked)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nBest Schedule: {ranked[0].schedule_name}")
    print(f"Parameters: {ranked[0].schedule_params}")
    print(f"Final Accuracy: {ranked[0].final_accuracy:.4f}")
    print(f"Forgetting Score: {ranked[0].forgetting_score:.4f}")
    print(f"Combined Score: {ranked[0].combined_score:.4f}")
    print("\nResults saved to:", optimizer.output_dir)
    print("="*70)


if __name__ == "__main__":
    main()
