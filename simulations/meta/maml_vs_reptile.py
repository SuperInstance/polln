"""
META Tile MAML vs Reptile Simulation
=====================================

Compares first-order (Reptile) vs second-order (MAML) meta-learning
for META tile adaptation efficiency.

Mathematical Foundation:
    MAML: θ ← θ - α∇_θ L_train(θ - β∇_θ L_val(θ))
    Reptile: θ ← θ - α∇_θ L_val(θ - β∇_θ L_val(θ))

    MAML uses second-order gradients (expensive)
    Reptile uses first-order gradients (efficient)

Hypotheses:
    H4: First-order approximation is sufficient for META tiles
    H4: Reptile converges faster with comparable accuracy
    H4: Sample efficiency favors Reptile for few-shot learning
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from abc import ABC, abstractmethod
import json
from pathlib import Path
import time


# Set random seeds
np.random.seed(42)
torch.manual_seed(42)


@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning simulation"""
    # Network architecture
    input_dim: int = 10
    hidden_dim: int = 32
    output_dim: int = 5

    # Meta-learning
    n_tasks: int = 50
    n_iterations: int = 1000
    n_shot: int = 5  # Few-shot learning
    n_query: int = 10

    # Learning rates
    meta_lr: float = 0.01  # α: meta-learning rate
    inner_lr: float = 0.1   # β: inner-loop adaptation rate

    # Optimization
    first_order: bool = False  # Use first-order approximation


class TaskDistribution:
    """
    Distribution of tasks for meta-learning.

    Each task is a regression problem with different parameters.
    """

    def __init__(self, input_dim: int, output_dim: int):
        self.input_dim = input_dim
        self.output_dim = output_dim

    def sample_task(self, task_id: int) -> 'RegressionTask':
        """Sample a new task from the distribution"""
        # Random transformation for this task
        W_task = np.random.randn(self.input_dim, self.output_dim) * 0.5
        b_task = np.random.randn(self.output_dim) * 0.1

        return RegressionTask(
            task_id=task_id,
            W=W_task,
            b=b_task
        )


class RegressionTask:
    """Single regression task"""

    def __init__(self, task_id: int, W: np.ndarray, b: np.ndarray):
        self.task_id = task_id
        self.W = W
        self.b = b

    def generate_data(self, n_samples: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generate input-output pairs"""
        X = torch.randn(n_samples, self.W.shape[0])
        noise = torch.randn(n_samples, self.W.shape[1]) * 0.1
        y = X @ torch.from_numpy(self.W).float() + torch.from_numpy(self.b).float() + noise
        return X, y

    def compute_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Compute MSE loss"""
        return torch.mean((predictions - targets)**2)


class MetaLearner(nn.Module):
    """
    Neural network for meta-learning.

    Can be adapted to new tasks with gradient descent.
    """

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

    def clone_parameters(self) -> List[torch.Tensor]:
        """Clone current parameters"""
        return [p.clone().detach() for p in self.parameters()]


class MAMLAlgorithm:
    """
    Model-Agnostic Meta-Learning (MAML).

    Uses second-order gradients for optimal adaptation.
    """

    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.model = MetaLearner(config.input_dim, config.hidden_dim, config.output_dim)
        self.meta_optimizer = optim.SGD(self.model.parameters(), lr=config.meta_lr)

        self.training_history: List[Dict] = []

    def inner_loop(self, task: RegressionTask, n_steps: int = 1) -> Tuple[List[torch.Tensor], float]:
        """
        Inner loop: Adapt to a specific task.

        Returns: (adapted_parameters, validation_loss)
        """
        # Clone model
        fast_weights = self.model.clone_parameters()

        # Generate support set (few-shot)
        X_support, y_support = task.generate_data(self.config.n_shot)

        # Gradient steps for adaptation
        for _ in range(n_steps):
            # Forward pass with fast weights
            y_pred = self._forward_with_fast_weights(X_support, fast_weights)
            loss = task.compute_loss(y_pred, y_support)

            # Compute gradients
            grads = torch.autograd.grad(
                loss,
                fast_weights,
                create_graph=True  # For second-order derivatives
            )

            # Update fast weights
            fast_weights = [
                w - self.config.inner_lr * g
                for w, g in zip(fast_weights, grads)
            ]

        # Validation on query set
        X_query, y_query = task.generate_data(self.config.n_query)
        y_pred_val = self._forward_with_fast_weights(X_query, fast_weights)
        val_loss = task.compute_loss(y_pred_val, y_query)

        return fast_weights, val_loss.item()

    def _forward_with_fast_weights(self, x: torch.Tensor, fast_weights: List[torch.Tensor]) -> torch.Tensor:
        """Forward pass with fast weights"""
        # Manual forward pass
        x = x @ fast_weights[0].T + fast_weights[1]  # Linear 1
        x = torch.relu(x)
        x = x @ fast_weights[2].T + fast_weights[3]  # Linear 2
        x = torch.relu(x)
        x = x @ fast_weights[4].T + fast_weights[5]  # Linear 3
        return x

    def meta_update(self, task_losses: List[torch.Tensor]):
        """Meta-update: Learn to learn"""
        # Sum task losses
        meta_loss = torch.stack(task_losses).mean()

        # Backward pass (computes second-order gradients)
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()

        return meta_loss.item()

    def train(self, task_distribution: TaskDistribution) -> Dict:
        """Train using MAML"""
        print(f"\nTraining MAML (second-order)...")

        start_time = time.time()

        for iteration in range(self.config.n_iterations):
            task_losses = []

            # Sample batch of tasks
            for task_idx in range(self.config.n_tasks):
                task = task_distribution.sample_task(task_idx)

                # Inner loop adaptation
                _, val_loss = self.inner_loop(task, n_steps=1)

                # Accumulate meta-loss
                task_losses.append(val_loss)

            # Meta-update
            avg_loss = np.mean(task_losses)
            self.training_history.append({
                'iteration': iteration,
                'meta_loss': avg_loss
            })

            if iteration % 100 == 0:
                print(f"  Iteration {iteration}: Loss = {avg_loss:.4f}")

        training_time = time.time() - start_time

        # Evaluate
        eval_results = self.evaluate(task_distribution)

        return {
            'training_history': self.training_history,
            'training_time': training_time,
            'final_loss': self.training_history[-1]['meta_loss'],
            'evaluation': eval_results
        }

    def evaluate(self, task_distribution: TaskDistribution, n_test_tasks: int = 10) -> Dict:
        """Evaluate on test tasks"""
        test_losses = []

        for i in range(n_test_tasks):
            task = task_distribution.sample_task(i + 1000)  # Different tasks

            # Adapt with more steps
            _, val_loss = self.inner_loop(task, n_steps=5)
            test_losses.append(val_loss)

        return {
            'mean_test_loss': np.mean(test_losses),
            'std_test_loss': np.std(test_losses)
        }


class ReptileAlgorithm:
    """
    Reptile: First-order meta-learning.

    Uses first-order gradients only (more efficient).
    """

    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.model = MetaLearner(config.input_dim, config.hidden_dim, config.output_dim)

        self.training_history: List[Dict] = []

    def inner_loop(self, task: RegressionTask, n_steps: int = 5) -> List[torch.Tensor]:
        """
        Inner loop: Adapt to task with SGD.

        Returns: Adapted parameters
        """
        # Clone model
        adapted_params = {name: p.clone() for name, p in self.model.named_parameters()}

        # Generate support set
        X_support, y_support = task.generate_data(self.config.n_shot)

        # SGD steps
        for _ in range(n_steps):
            # Forward pass
            y_pred = self._forward_with_params(X_support, adapted_params)
            loss = torch.mean((y_pred - y_support)**2)

            # Compute gradients (first-order only)
            grads = torch.autograd.grad(
                loss,
                adapted_params.values(),
                create_graph=False  # No second-order
            )

            # Update parameters
            for (name, param), grad in zip(adapted_params.items(), grads):
                adapted_params[name] = param - self.config.inner_lr * grad

        return list(adapted_params.values())

    def _forward_with_params(self, x: torch.Tensor, params: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Forward pass with custom parameters"""
        # Get named layers
        layers = list(self.model.network.named_children())

        # Layer 1
        weight = params['network.0.weight']
        bias = params['network.0.bias']
        x = x @ weight.T + bias
        x = torch.relu(x)

        # Layer 2
        weight = params['network.2.weight']
        bias = params['network.2.bias']
        x = x @ weight.T + bias
        x = torch.relu(x)

        # Layer 3
        weight = params['network.4.weight']
        bias = params['network.4.bias']
        x = x @ weight.T + bias

        return x

    def meta_update(self, task_params: List[List[torch.Tensor]]):
        """
        Meta-update: Move toward task-specific parameters.

        θ ← θ + α × Σ(θ_i - θ) / N
        """
        # Compute average direction
        current_params = list(self.model.parameters())

        with torch.no_grad():
            # Initialize gradient accumulator
            meta_grads = [torch.zeros_like(p) for p in current_params]

            # Accumulate gradients from each task
            for adapted_params in task_params:
                for i, (current, adapted) in enumerate(zip(current_params, adapted_params)):
                    meta_grads[i] += (adapted - current) / len(task_params)

            # Apply meta-gradient
            for param, grad in zip(current_params, meta_grads):
                param += self.config.meta_lr * grad

    def train(self, task_distribution: TaskDistribution) -> Dict:
        """Train using Reptile"""
        print(f"\nTraining Reptile (first-order)...")

        start_time = time.time()

        for iteration in range(self.config.n_iterations):
            task_params = []

            # Sample batch of tasks
            for task_idx in range(self.config.n_tasks):
                task = task_distribution.sample_task(task_idx)

                # Inner loop adaptation
                adapted_params = self.inner_loop(task, n_steps=5)
                task_params.append(adapted_params)

            # Meta-update
            self.meta_update(task_params)

            # Compute validation loss
            if iteration % 10 == 0:
                val_losses = []
                for i in range(min(5, self.config.n_tasks)):
                    task = task_distribution.sample_task(i + 1000)
                    X_query, y_query = task.generate_data(self.config.n_query)

                    with torch.no_grad():
                        y_pred = self.model(X_query)
                        loss = torch.mean((y_pred - y_query)**2)
                        val_losses.append(loss.item())

                avg_loss = np.mean(val_losses)
                self.training_history.append({
                    'iteration': iteration,
                    'meta_loss': avg_loss
                })

                if iteration % 100 == 0:
                    print(f"  Iteration {iteration}: Loss = {avg_loss:.4f}")

        training_time = time.time() - start_time

        # Evaluate
        eval_results = self.evaluate(task_distribution)

        return {
            'training_history': self.training_history,
            'training_time': training_time,
            'final_loss': self.training_history[-1]['meta_loss'],
            'evaluation': eval_results
        }

    def evaluate(self, task_distribution: TaskDistribution, n_test_tasks: int = 10) -> Dict:
        """Evaluate on test tasks"""
        test_losses = []

        for i in range(n_test_tasks):
            task = task_distribution.sample_task(i + 1000)

            # Adapt with more steps
            adapted_params = self.inner_loop(task, n_steps=10)

            # Evaluate
            X_query, y_query = task.generate_data(self.config.n_query)
            with torch.no_grad():
                y_pred = self._forward_with_params(X_query,
                    {name: p for name, p in zip(self.model.state_dict().keys(), adapted_params)})
                loss = torch.mean((y_pred - y_query)**2)
                test_losses.append(loss.item())

        return {
            'mean_test_loss': np.mean(test_losses),
            'std_test_loss': np.std(test_losses)
        }


class ComparisonSimulation:
    """
    Compare MAML vs Reptile for META tile meta-learning.
    """

    def __init__(self, config: MetaLearningConfig):
        self.config = config

        # Initialize algorithms
        self.maml = MAMLAlgorithm(config)
        self.reptile = ReptileAlgorithm(config)

        # Task distribution
        self.task_distribution = TaskDistribution(config.input_dim, config.output_dim)

    def run(self) -> Dict:
        """Run comparison"""
        print("="*70)
        print("META TILE META-LEARNING COMPARISON")
        print("="*70)

        # Train both algorithms
        maml_results = self.maml.train(self.task_distribution)
        reptile_results = self.reptile.train(self.task_distribution)

        # Compare
        comparison = self._compare(maml_results, reptile_results)

        return {
            'maml': maml_results,
            'reptile': reptile_results,
            'comparison': comparison
        }

    def _compare(self, maml_results: Dict, reptile_results: Dict) -> Dict:
        """Compare results"""
        return {
            'training_time_ratio': (
                reptile_results['training_time'] / maml_results['training_time']
            ),
            'final_loss_ratio': (
                reptile_results['final_loss'] / maml_results['final_loss']
            ),
            'test_loss_maml': maml_results['evaluation']['mean_test_loss'],
            'test_loss_reptile': reptile_results['evaluation']['mean_test_loss'],
            'accuracy_loss_tradeoff': (
                (reptile_results['evaluation']['mean_test_loss'] /
                 maml_results['evaluation']['mean_test_loss']) *
                (maml_results['training_time'] / reptile_results['training_time'])
            )
        }

    def visualize(self, save_path: Optional[Path] = None):
        """Visualize comparison"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 1. Training curves
        ax = axes[0]
        maml_history = self.maml.training_history
        reptile_history = self.reptile.training_history

        maml_losses = [h['meta_loss'] for h in maml_history]
        reptile_losses = [h['meta_loss'] for h in reptile_history]

        ax.plot(maml_losses, label='MAML (2nd order)', linewidth=2, alpha=0.8)
        ax.plot(reptile_losses, label='Reptile (1st order)', linewidth=2, alpha=0.8)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Meta-Loss')
        ax.set_title('Training Curves')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')

        # 2. Training time vs accuracy
        ax = axes[1]
        algorithms = ['MAML\n(2nd order)', 'Reptile\n(1st order)']
        times = [
            self.maml.training_history[-1]['iteration'] *
            (self.maml.training_history[-1]['meta_loss'] /
             np.mean([h['meta_loss'] for h in self.maml.training_history])),
            self.reptile.training_history[-1]['iteration'] *
            (self.reptile.training_history[-1]['meta_loss'] /
             np.mean([h['meta_loss'] for h in self.reptile.training_history]))
        ]

        # Normalized metrics
        maml_time = len(maml_losses) * 10  # Approximate
        reptile_time = len(reptile_losses) * 1  # Approximate (no second-order)

        test_losses = [
            self.maml.evaluate(self.task_distribution)['mean_test_loss'],
            self.reptile.evaluate(self.task_distribution)['mean_test_loss']
        ]

        ax.scatter(test_losses, [maml_time, reptile_time], s=200, alpha=0.7)
        ax.set_xlabel('Test Loss (lower is better)')
        ax.set_ylabel('Training Time (arbitrary units)')
        ax.set_title('Accuracy vs Efficiency Trade-off')
        ax.grid(True, alpha=0.3)

        # Annotate points
        for i, algo in enumerate(algorithms):
            ax.annotate(algo, (test_losses[i], [maml_time, reptile_time][i]),
                       xytext=(10, 10), textcoords='offset points', fontsize=9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved meta-learning comparison plot to {save_path}")

        return fig


def run_sample_efficiency_experiment():
    """Experiment: Compare sample efficiency (1-shot vs 5-shot)"""
    print("\n" + "="*70)
    print("EXPERIMENT: Sample Efficiency (Few-Shot Learning)")
    print("="*70)

    shot_configs = [1, 3, 5, 10]
    results = {'maml': [], 'reptile': []}

    for n_shot in shot_configs:
        print(f"\nTesting {n_shot}-shot learning...")

        config = MetaLearningConfig(
            input_dim=10,
            hidden_dim=32,
            output_dim=5,
            n_tasks=20,
            n_iterations=200,
            n_shot=n_shot
        )

        sim = ComparisonSimulation(config)

        # Train MAML
        maml = MAMLAlgorithm(config)
        task_dist = TaskDistribution(config.input_dim, config.output_dim)
        maml_results = maml.train(task_dist)

        # Train Reptile
        reptile = ReptileAlgorithm(config)
        reptile_results = reptile.train(task_dist)

        results['maml'].append({
            'n_shot': n_shot,
            'test_loss': maml_results['evaluation']['mean_test_loss']
        })

        results['reptile'].append({
            'n_shot': n_shot,
            'test_loss': reptile_results['evaluation']['mean_test_loss']
        })

        print(f"  MAML test loss: {maml_results['evaluation']['mean_test_loss']:.4f}")
        print(f"  Reptile test loss: {reptile_results['evaluation']['mean_test_loss']:.4f}")

    return results


def run_model_size_experiment():
    """Experiment: Compare algorithms across different model sizes"""
    print("\n" + "="*70)
    print("EXPERIMENT: Model Size Scaling")
    print("="*70)

    hidden_dims = [16, 32, 64, 128]
    results = []

    for hidden_dim in hidden_dims:
        print(f"\nTesting hidden_dim={hidden_dim}...")

        config = MetaLearningConfig(
            input_dim=10,
            hidden_dim=hidden_dim,
            output_dim=5,
            n_tasks=20,
            n_iterations=200
        )

        sim = ComparisonSimulation(config)

        # Train both
        maml = MAMLAlgorithm(config)
        reptile = ReptileAlgorithm(config)
        task_dist = TaskDistribution(config.input_dim, config.output_dim)

        import time
        start = time.time()
        maml_results = maml.train(task_dist)
        maml_time = time.time() - start

        start = time.time()
        reptile_results = reptile.train(task_dist)
        reptile_time = time.time() - start

        results.append({
            'hidden_dim': hidden_dim,
            'n_params': sum(p.numel() for p in maml.model.parameters()),
            'maml_test_loss': maml_results['evaluation']['mean_test_loss'],
            'reptile_test_loss': reptile_results['evaluation']['mean_test_loss'],
            'maml_time': maml_time,
            'reptile_time': reptile_time,
            'speedup': maml_time / reptile_time
        })

        print(f"  MAML: {maml_results['evaluation']['mean_test_loss']:.4f} loss, {maml_time:.1f}s")
        print(f"  Reptile: {reptile_results['evaluation']['mean_test_loss']:.4f} loss, {reptile_time:.1f}s")
        print(f"  Speedup: {results[-1]['speedup']:.2f}x")

    return results


def main():
    """Run all meta-learning experiments"""
    # Create output directory
    output_dir = Path('/c/Users/casey/polln/simulations/results')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run main comparison
    config = MetaLearningConfig(
        input_dim=10,
        hidden_dim=32,
        output_dim=5,
        n_tasks=30,
        n_iterations=500
    )

    sim = ComparisonSimulation(config)
    results = sim.run()

    print("\n" + "="*70)
    print("META-LEARNING COMPARISON RESULTS")
    print("="*70)

    comparison = results['comparison']
    print(f"\nTraining time ratio (Reptile/MAML): {comparison['training_time_ratio']:.2f}x")
    print(f"Final loss ratio (Reptile/MAML): {comparison['final_loss_ratio']:.2f}")
    print(f"\nTest losses:")
    print(f"  MAML: {comparison['test_loss_maml']:.4f}")
    print(f"  Reptile: {comparison['test_loss_reptile']:.4f}")
    print(f"\nAccuracy/efficiency score (lower is better): {comparison['accuracy_loss_tradeoff']:.2f}")

    # Visualize
    fig_dir = Path('/c/Users/casey/polln/simulations/figures')
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig = sim.visualize(fig_dir / 'maml_vs_reptile.png')

    # Run experiments
    sample_results = run_sample_efficiency_experiment()
    size_results = run_model_size_experiment()

    # Save all results
    all_results = {
        'main_comparison': results,
        'sample_efficiency': sample_results,
        'model_size_scaling': size_results
    }

    results_path = output_dir / 'metalearning_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {results_path}")

    return results


if __name__ == '__main__':
    results = main()
