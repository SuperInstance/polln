"""
Learning Rate Schedule Search
==============================
Discovers optimal learning rate schedules for all POLLN learning mechanisms:

- TD(λ) Value Network
- VAE World Model
- Hebbian Learning
- Oja's Rule (PCA-like)

Schedules to Test:
1. Constant
2. Step Decay
3. Exponential Decay
4. Cosine Annealing
5. Warmup + Cosine
6. Cyclical/SGDR
7. One-Cycle Policy
8. Adaptive (based on gradient noise)

Outputs:
- Optimal schedule per algorithm
- Convergence analysis
- Final performance metrics
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import json
import seaborn as sns

sns.set_style("whitegrid")


@dataclass
class ScheduleResult:
    """Results from testing a learning rate schedule"""
    schedule_name: str
    final_loss: float
    convergence_epoch: int
    final_performance: float
    stability_score: float
    schedule_params: Dict


class LearningRateSchedules:
    """Various learning rate schedule implementations"""

    @staticmethod
    def constant(lr: float, total_steps: int) -> np.ndarray:
        """Constant learning rate"""
        return np.full(total_steps, lr)

    @staticmethod
    def step_decay(initial_lr: float, total_steps: int,
                   drop_rate: float = 0.5, epochs_drop: int = 100) -> np.ndarray:
        """Step decay: drop LR by factor every N epochs"""
        schedule = np.zeros(total_steps)
        for step in range(total_steps):
            epoch = step // 10  # Assume 10 steps per epoch
            schedule[step] = initial_lr * (drop_rate ** (epoch // epochs_drop))
        return schedule

    @staticmethod
    def exponential_decay(initial_lr: float, total_steps: int, gamma: float = 0.995) -> np.ndarray:
        """Exponential decay: LR = initial_lr * gamma^step"""
        steps = np.arange(total_steps)
        return initial_lr * (gamma ** steps)

    @staticmethod
    def cosine_annealing(initial_lr: float, total_steps: int, min_lr: float = 0.0) -> np.ndarray:
        """Cosine annealing: LR = min_lr + 0.5*(max_lr-min_lr)*(1+cos(pi*t/T))"""
        steps = np.arange(total_steps)
        return min_lr + 0.5 * (initial_lr - min_lr) * (1 + np.cos(np.pi * steps / total_steps))

    @staticmethod
    def warmup_cosine(initial_lr: float, total_steps: int, warmup_steps: int = 100,
                      min_lr: float = 0.0) -> np.ndarray:
        """Warmup + Cosine annealing"""
        schedule = np.zeros(total_steps)

        # Warmup phase
        for step in range(min(warmup_steps, total_steps)):
            schedule[step] = initial_lr * (step + 1) / warmup_steps

        # Cosine annealing phase
        if warmup_steps < total_steps:
            remaining_steps = total_steps - warmup_steps
            for step in range(warmup_steps, total_steps):
                t = step - warmup_steps
                schedule[step] = min_lr + 0.5 * (initial_lr - min_lr) * \
                               (1 + np.cos(np.pi * t / remaining_steps))

        return schedule

    @staticmethod
    def cyclical_sgdr(initial_lr: float, total_steps: int,
                      cycle_length: int = 200, min_lr: float = 0.0) -> np.ndarray:
        """Stochastic Gradient Descent with Restarts (SGDR)"""
        schedule = np.zeros(total_steps)
        cycle_num = 0

        for step in range(total_steps):
            t = step % cycle_length
            if t == 0 and step > 0:
                cycle_num += 1
            schedule[step] = min_lr + 0.5 * (initial_lr - min_lr) * \
                           (1 + np.cos(np.pi * t / cycle_length))

        return schedule

    @staticmethod
    def one_cycle(initial_lr: float, total_steps: int,
                  max_lr: float = None, min_lr: float = 0.0) -> np.ndarray:
        """One-Cycle Policy (Smith 2018)"""
        if max_lr is None:
            max_lr = initial_lr * 10

        schedule = np.zeros(total_steps)
        mid_point = total_steps // 2

        # First half: increase from initial_lr to max_lr
        for step in range(mid_point):
            pct = step / mid_point
            schedule[step] = initial_lr + (max_lr - initial_lr) * pct

        # Second half: decrease from max_lr to min_lr
        for step in range(mid_point, total_steps):
            pct = (step - mid_point) / (total_steps - mid_point)
            schedule[step] = max_lr - (max_lr - min_lr) * pct

        return schedule

    @staticmethod
    def adaptive(initial_lr: float, total_steps: int,
                 window_size: int = 50, increase_factor: float = 1.02,
                 decrease_factor: float = 0.95) -> np.ndarray:
        """Adaptive LR based on gradient variance (simulated)"""
        schedule = np.zeros(total_steps)
        current_lr = initial_lr

        # Simulate gradient variance (decreases over training)
        gradient_variance = np.ones(total_steps)
        for step in range(total_steps):
            gradient_variance[step] = 1.0 * np.exp(-step / 500) + 0.1

        for step in range(total_steps):
            # Adjust LR based on recent gradient variance
            if step > window_size:
                recent_var = np.mean(gradient_variance[max(0, step-window_size):step])
                if recent_var < 0.3:  # Low variance = increase LR
                    current_lr *= increase_factor
                elif recent_var > 0.7:  # High variance = decrease LR
                    current_lr *= decrease_factor

            schedule[step] = current_lr

        return schedule


class LearningSimulator:
    """Simulates learning dynamics for different algorithms"""

    def __init__(self, seed: int = 42):
        np.random.seed(seed)

    def simulate_td_lambda(self, lr_schedule: np.ndarray,
                          num_states: int = 100,
                          gamma: float = 0.99,
                          lambda_: float = 0.7) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate TD(λ) learning with given LR schedule"""
        num_steps = len(lr_schedule)
        values = np.zeros(num_states)
        losses = np.zeros(num_steps)

        # True value function (exponentially decaying)
        true_values = np.exp(-np.arange(num_states) / 20.0)

        eligibility_trace = np.zeros(num_states)

        for step in range(num_steps):
            # Sample random state
            state = np.random.randint(0, num_states - 1)
            next_state = state + 1

            if next_state >= num_states:
                # Terminal state
                td_error = 0 - values[state]
            else:
                td_error = true_values[next_state] + gamma * values[next_state] - values[state]

            # Update eligibility trace
            eligibility_trace *= gamma * lambda_
            eligibility_trace[state] += 1

            # Update values
            lr = lr_schedule[step]
            values += lr * td_error * eligibility_trace

            # Track loss
            losses[step] = np.mean((values - true_values) ** 2)

        return values, losses

    def simulate_vae(self, lr_schedule: np.ndarray,
                    input_dim: int = 784,
                    latent_dim: int = 32,
                    num_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate VAE training with given LR schedule"""
        num_steps = len(lr_schedule)
        num_batches = num_steps // 10

        # Generate synthetic data
        np.random.seed(42)
        data = np.random.randn(num_samples, input_dim)

        # Simulated encoder/decoder weights
        encoder = np.random.randn(input_dim, latent_dim) * 0.01
        decoder = np.random.randn(latent_dim, input_dim) * 0.01

        reconstruction_losses = np.zeros(num_steps)
        kl_losses = np.zeros(num_steps)

        for step in range(num_steps):
            # Mini-batch
            batch_size = 32
            batch_idx = np.random.choice(num_samples, batch_size, replace=False)
            batch = data[batch_idx]

            # Forward pass (simplified)
            z = batch @ encoder
            reconstructed = z @ decoder

            # Compute losses
            reconstruction_loss = np.mean((batch - reconstructed) ** 2)
            kl_loss = -0.5 * np.mean(1 + np.log(np.var(z, axis=0) + 1e-8) - np.mean(z, axis=0)**2 - np.var(z, axis=0))

            # Backward pass (gradient descent simulation)
            lr = lr_schedule[step]
            encoder_grad = 2 * lr * (batch.T @ (reconstructed - batch)) @ decoder.T / batch_size
            decoder_grad = 2 * lr * z.T @ (reconstructed - batch) / batch_size

            # Update weights
            encoder -= encoder_grad
            decoder -= decoder_grad

            reconstruction_losses[step] = reconstruction_loss
            kl_losses[step] = kl_loss

        total_losses = reconstruction_losses + 0.1 * kl_losses
        return encoder, total_losses

    def simulate_hebbian(self, lr_schedule: np.ndarray,
                        num_neurons: int = 100,
                        input_dim: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate Hebbian learning with given LR schedule"""
        num_steps = len(lr_schedule)
        weights = np.random.randn(num_neurons, input_dim) * 0.01

        # Generate input patterns
        np.random.seed(42)
        patterns = np.random.randn(num_steps, input_dim)

        # Normalize patterns
        patterns = patterns / np.linalg.norm(patterns, axis=1, keepdims=True)

        correlation_measures = np.zeros(num_steps)

        for step in range(num_steps):
            pattern = patterns[step]

            # Hebbian update: Δw = η * (x * y - w)
            # y = w @ x
            outputs = weights @ pattern

            lr = lr_schedule[step]
            dw = lr * np.outer(outputs, pattern)

            # Weight decay for stability
            dw -= 0.01 * weights

            weights += dw

            # Measure correlation (higher is better)
            correlation = np.mean(np.abs(np.corrcoef(patterns[:min(step+1, 100)], weights[:min(step+1, 100)])))
            correlation_measures[step] = correlation

        return weights, correlation_measures

    def simulate_oja(self, lr_schedule: np.ndarray,
                    num_neurons: int = 10,
                    input_dim: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate Oja's rule (PCA-like) with given LR schedule"""
        num_steps = len(lr_schedule)
        weights = np.random.randn(input_dim, num_neurons) * 0.01

        # Generate correlated input data
        np.random.seed(42)
        covariance = np.random.randn(input_dim, input_dim)
        covariance = covariance @ covariance.T  # Make positive semi-definite

        patterns = np.random.multivariate_normal(
            np.zeros(input_dim),
            covariance,
            num_steps
        )

        # Normalize
        patterns = patterns / (np.linalg.norm(patterns, axis=1, keepdims=True) + 1e-8)

        explained_variances = np.zeros(num_steps)

        for step in range(num_steps):
            pattern = patterns[step]

            # Oja's rule: Δw = η * (x * y - y^2 * w)
            # where y = w^T @ x
            outputs = weights.T @ pattern

            lr = lr_schedule[step]
            dw = lr * np.outer(pattern, outputs)
            dw -= lr * np.outer(weights, outputs ** 2)

            weights += dw

            # Measure explained variance (should converge to eigenvectors)
            if step % 10 == 0:
                projected_variance = np.var(patterns[:step+1] @ weights, axis=0)
                explained_variances[step] = np.sum(projected_variance)

        return weights, explained_variances


class ScheduleOptimizer:
    """Optimizes learning rate schedules for different algorithms"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.simulator = LearningSimulator()
        self.schedules = LearningRateSchedules()

    def optimize_for_algorithm(self, algorithm: str,
                              num_steps: int = 1000,
                              num_runs: int = 5) -> List[ScheduleResult]:
        """Find optimal schedule for a specific algorithm"""
        print(f"\n{'='*60}")
        print(f"Optimizing schedules for {algorithm}")
        print(f"{'='*60}")

        results = []

        # Define schedule configurations to test
        schedule_configs = [
            ("constant", {"lr": 0.01}),
            ("step_decay", {"initial_lr": 0.01, "drop_rate": 0.5, "epochs_drop": 100}),
            ("exponential_decay", {"initial_lr": 0.01, "gamma": 0.995}),
            ("cosine_annealing", {"initial_lr": 0.01, "min_lr": 0.0001}),
            ("warmup_cosine", {"initial_lr": 0.01, "warmup_steps": 100, "min_lr": 0.0001}),
            ("cyclical_sgdr", {"initial_lr": 0.01, "cycle_length": 200, "min_lr": 0.0001}),
            ("one_cycle", {"initial_lr": 0.001, "max_lr": 0.01, "min_lr": 0.0001}),
            ("adaptive", {"initial_lr": 0.01, "window_size": 50}),
        ]

        for schedule_name, params in schedule_configs:
            print(f"\nTesting {schedule_name}...")

            # Generate schedule
            schedule_func = getattr(self.schedules, schedule_name)
            lr_schedule = schedule_func(**params, total_steps=num_steps)

            # Run multiple trials
            final_losses = []
            convergence_epochs = []
            final_performances = []
            stability_scores = []

            for run in range(num_runs):
                # Run simulation
                if algorithm == "td_lambda":
                    _, losses = self.simulator.simulate_td_lambda(lr_schedule)
                elif algorithm == "vae":
                    _, losses = self.simulator.simulate_vae(lr_schedule)
                elif algorithm == "hebbian":
                    _, measures = self.simulator.simulate_hebbian(lr_schedule)
                    losses = -measures  # Convert to loss (lower is better)
                elif algorithm == "oja":
                    _, measures = self.simulator.simulate_oja(lr_schedule)
                    losses = -measures  # Convert to loss
                else:
                    raise ValueError(f"Unknown algorithm: {algorithm}")

                # Metrics
                final_loss = np.mean(losses[-100:])
                final_losses.append(final_loss)

                # Convergence: when loss drops below 110% of final loss
                convergence_threshold = final_loss * 1.1
                convergence_epoch = np.where(losses < convergence_threshold)[0]
                convergence_epoch = convergence_epoch[0] if len(convergence_epoch) > 0 else num_steps
                convergence_epochs.append(cononvergence_epoch)

                # Final performance (inverse of final loss)
                final_performances.append(1.0 / (final_loss + 1e-8))

                # Stability: std of last 100 steps
                stability = np.std(losses[-100:])
                stability_scores.append(stability)

            # Aggregate results
            result = ScheduleResult(
                schedule_name=schedule_name,
                final_loss=np.mean(final_losses),
                convergence_epoch=int(np.mean(convergence_epochs)),
                final_performance=np.mean(final_performances),
                stability_score=np.mean(stability_scores),
                schedule_params=params
            )
            results.append(result)

            print(f"  Final Loss: {result.final_loss:.6f}")
            print(f"  Convergence: Epoch {result.convergence_epoch}")
            print(f"  Performance: {result.final_performance:.4f}")
            print(f"  Stability: {result.stability_score:.6f}")

        return results

    def rank_schedules(self, results: List[ScheduleResult]) -> List[ScheduleResult]:
        """Rank schedules by combined score"""
        for result in results:
            # Combined score: performance / (convergence_epoch * stability)
            # Higher is better
            result.combined_score = (
                result.final_performance /
                (result.convergence_epoch * result.stability_score + 1e-8)
            )

        return sorted(results, key=lambda r: r.combined_score, reverse=True)

    def visualize_results(self, algorithm: str, results: List[ScheduleResult]):
        """Create visualization for schedule comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot example learning curves for top 3 schedules
        top_3 = results[:3]
        ax = axes[0, 0]

        for result in top_3:
            schedule_func = getattr(self.schedules, result.schedule_name)
            lr_schedule = schedule_func(**result.schedule_params, total_steps=1000)

            if algorithm == "td_lambda":
                _, losses = self.simulator.simulate_td_lambda(lr_schedule)
            elif algorithm == "vae":
                _, losses = self.simulator.simulate_vae(lr_schedule)
            elif algorithm == "hebbian":
                _, measures = self.simulator.simulate_hebbian(lr_schedule)
                losses = -measures
            elif algorithm == "oja":
                _, measures = self.simulator.simulate_oja(lr_schedule)
                losses = -measures

            # Smooth the curve
            window = 50
            smoothed = np.convolve(losses, np.ones(window)/window, mode='valid')
            ax.plot(smoothed, label=result.schedule_name, linewidth=2)

        ax.set_title(f"Top 3 Learning Curves - {algorithm}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Training Step")
        ax.set_ylabel("Loss")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Bar chart: Final Loss
        ax = axes[0, 1]
        names = [r.schedule_name for r in results]
        losses = [r.final_loss for r in results]
        colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
        ax.barh(names, losses, color=colors)
        ax.set_xlabel("Final Loss (lower is better)")
        ax.set_title("Final Loss Comparison", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Convergence Speed
        ax = axes[1, 0]
        convergence = [r.convergence_epoch for r in results]
        ax.barh(names, convergence, color=colors)
        ax.set_xlabel("Convergence Epoch (lower is better)")
        ax.set_title("Convergence Speed", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Combined Score
        ax = axes[1, 1]
        scores = [getattr(r, 'combined_score', 0) for r in results]
        ax.barh(names, scores, color=colors)
        ax.set_xlabel("Combined Score (higher is better)")
        ax.set_title("Overall Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / f"{algorithm}_schedule_comparison.png", dpi=300)
        plt.close()

    def save_results(self, algorithm: str, ranked_results: List[ScheduleResult]):
        """Save results to JSON"""
        output = {
            "algorithm": algorithm,
            "optimal_schedule": ranked_results[0].schedule_name,
            "optimal_params": ranked_results[0].schedule_params,
            "all_schedules": [
                {
                    "name": r.schedule_name,
                    "final_loss": float(r.final_loss),
                    "convergence_epoch": int(r.convergence_epoch),
                    "final_performance": float(r.final_performance),
                    "stability_score": float(r.stability_score),
                    "combined_score": float(getattr(r, 'combined_score', 0)),
                    "params": r.schedule_params
                }
                for r in ranked_results
            ]
        }

        with open(self.output_dir / f"{algorithm}_optimal_schedule.json", "w") as f:
            json.dump(output, f, indent=2)

    def run_all_optimizations(self):
        """Run schedule optimization for all algorithms"""
        algorithms = ["td_lambda", "vae", "hebbian", "oja"]

        all_results = {}

        for algorithm in algorithms:
            results = self.optimize_for_algorithm(algorithm)
            ranked = self.rank_schedules(results)

            self.visualize_results(algorithm, ranked)
            self.save_results(algorithm, ranked)

            all_results[algorithm] = ranked[0].schedule_name

            print(f"\n{'='*60}")
            print(f"Best schedule for {algorithm}: {ranked[0].schedule_name}")
            print(f"  Parameters: {ranked[0].schedule_params}")
            print(f"  Combined Score: {ranked[0].combined_score:.4f}")
            print(f"{'='*60}")

        # Save summary
        with open(self.output_dir / "schedule_optimization_summary.json", "w") as f:
            json.dump(all_results, f, indent=2)

        return all_results


def main():
    """Run learning rate schedule optimization"""
    optimizer = ScheduleOptimizer()

    print("="*70)
    print("LEARNING RATE SCHEDULE OPTIMIZATION")
    print("="*70)
    print("\nTesting 8 different schedules across 4 learning algorithms:")
    print("  - TD(λ) Value Learning")
    print("  - VAE World Model")
    print("  - Hebbian Learning")
    print("  - Oja's Rule (PCA)")
    print("\nEach schedule tested with 5 runs for statistical validity")
    print("="*70)

    optimal_schedules = optimizer.run_all_optimizations()

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print("\nOptimal Schedules:")
    for algorithm, schedule in optimal_schedules.items():
        print(f"  {algorithm:20s} -> {schedule}")
    print("\nResults saved to:", optimizer.output_dir)
    print("="*70)


if __name__ == "__main__":
    main()
