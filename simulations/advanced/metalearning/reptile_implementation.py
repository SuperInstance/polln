"""
Reptile Implementation for POLLN

Implements first-order meta-learning (Reptile) for faster adaptation.
Key advantage: 3x faster than MAML by avoiding second-order derivatives.

Mathematical Foundation:
- Adapt: θ'_i = θ - α∇_θ L_Ti(f_θ)
- Meta-update: θ ← θ + ε(θ'_i - θ)  (interpolate toward adapted parameters)
- Key insight: Gradient difference ≈ direction for better initialization
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Callable, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import time


@dataclass
class ReptileConfig:
    """Reptile hyperparameters"""
    meta_lr: float = 0.1             # ε: meta-learning rate
    inner_lr: float = 0.01           # α: task adaptation learning rate
    inner_steps: int = 10            # K: gradient steps per task
    meta_batch_size: int = 32        # Tasks per meta-update
    num_iterations: int = 10000      # Total meta-training iterations

    # Task sampling
    shots: int = 5                   # K-shot learning
    ways: int = 5                    # N-way classification

    # Optimization
    val_interval: int = 100          # Validation frequency
    val_tasks: int = 20              # Tasks for validation
    save_interval: int = 1000        # Checkpoint frequency


class ReptileAgent:
    """
    Reptile meta-learning for POLLN agents

    First-order approximation: much faster than MAML.
    """

    def __init__(self, config: ReptileConfig, model: nn.Module):
        self.config = config
        self.model = model

        # Track meta-learning progress
        self.meta_history = {
            'train_loss': [],
            'val_loss': [],
            'adaptation_speed': [],
            'computation_time': []
        }

        # Timing statistics
        self.iteration_times = []

    def adapt(self, task: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Inner loop: Adapt to specific task

        Args:
            task: Dictionary with 'support_x', 'support_y'

        Returns:
            Adapted parameters
        """
        # Copy current parameters
        original_params = {name: param.clone()
                          for name, param in self.model.named_parameters()}

        # Inner loop optimization
        for step in range(self.config.inner_steps):
            loss = self._compute_loss(task)

            # Compute gradients
            self.model.zero_grad()
            loss.backward()

            # Gradient descent step
            with torch.no_grad():
                for param in self.model.parameters():
                    if param.grad is not None:
                        param.data -= self.config.inner_lr * param.grad.data

        # Get adapted parameters
        adapted_params = {name: param.clone()
                         for name, param in self.model.named_parameters()}

        # Restore original parameters
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                param.data.copy_(original_params[name])

        return adapted_params

    def meta_update(self, task_batch: List[Dict[str, torch.Tensor]]) -> Dict[str, float]:
        """
        Outer loop: Meta-update via Reptile interpolation

        Key: θ ← θ + ε Σ(θ'_i - θ) = θ + ε Σ(-α∇L_i)
        This is equivalent to moving toward the task-specific optima.
        """
        start_time = time.time()

        # Collect adapted parameters from all tasks
        adapted_params_list = []
        losses = []

        for task in task_batch:
            adapted_params = self.adapt(task)
            adapted_params_list.append(adapted_params)

            # Compute loss for tracking
            loss = self._compute_loss(task)
            losses.append(loss.item())

        # Meta-update: interpolate toward adapted parameters
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                # Average gradient difference across tasks
                grad_diff = torch.zeros_like(param)

                for adapted_params in adapted_params_list:
                    grad_diff += (adapted_params[name] - param.data)

                grad_diff /= len(task_batch)

                # Reptile update: move toward adapted parameters
                param.data += self.config.meta_lr * grad_diff

        iteration_time = time.time() - start_time
        self.iteration_times.append(iteration_time)

        return {
            'loss': np.mean(losses),
            'iteration_time': iteration_time
        }

    def meta_train(self, task_sampler: Callable[[], List[Dict]]) -> Dict[str, Any]:
        """
        Full Reptile meta-training loop

        Args:
            task_sampler: Function that samples a batch of tasks

        Returns:
            Training statistics
        """
        print(f"Starting Reptile meta-training...")
        print(f"Config: {self.config}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

        best_val_loss = float('inf')

        for iteration in range(self.config.num_iterations):
            # Sample meta-training tasks
            task_batch = task_sampler()

            # Meta-update
            metrics = self.meta_update(task_batch)

            # Validation
            if iteration % self.config.val_interval == 0:
                val_tasks = [self._sample_task() for _ in range(self.config.val_tasks)]
                val_metrics = self.evaluate(val_tasks)

                avg_time = np.mean(self.iteration_times[-100:])

                print(f"Iter {iteration}: "
                      f"Train Loss={metrics['loss']:.4f}, "
                      f"Val Loss={val_metrics['val_loss']:.4f}, "
                      f"Time={avg_time*1000:.1f}ms, "
                      f"Adapt Speed={val_metrics['adaptation_steps']:.1f} steps")

                self.meta_history['train_loss'].append(metrics['loss'])
                self.meta_history['val_loss'].append(val_metrics['val_loss'])
                self.meta_history['adaptation_speed'].append(
                    val_metrics['adaptation_steps']
                )
                self.meta_history['computation_time'].append(avg_time)

                if val_metrics['val_loss'] < best_val_loss:
                    best_val_loss = val_metrics['val_loss']
                    self._save_checkpoint(f'best_reptile_iter_{iteration}.pt')

            # Checkpoint
            if iteration % self.config.save_interval == 0:
                self._save_checkpoint(f'reptile_checkpoint_{iteration}.pt')

        return {
            'best_val_loss': best_val_loss,
            'final_train_loss': metrics['loss'],
            'avg_iteration_time': np.mean(self.iteration_times),
            'meta_history': self.meta_history
        }

    def evaluate(self, tasks: List[Dict]) -> Dict[str, float]:
        """Evaluate Reptile meta-learning performance"""
        total_loss = 0.0
        adaptation_steps = []

        for task in tasks:
            # Adapt to task
            adapted_params = self.adapt(task)

            # Evaluate with adapted parameters
            loss = self._compute_loss(task, adapted_params)
            total_loss += loss.item()

            # Measure adaptation speed
            steps = self._measure_convergence(task)
            adaptation_steps.append(steps)

        return {
            'val_loss': total_loss / len(tasks),
            'adaptation_steps': np.mean(adaptation_steps)
        }

    def _compute_loss(
        self,
        task: Dict[str, torch.Tensor],
        params: Dict[str, torch.Tensor] = None
    ) -> torch.Tensor:
        """Compute loss with given parameters"""
        support_x = task['support_x']
        support_y = task['support_y']

        # Use adapted parameters if provided
        if params is not None:
            original_params = {name: param.clone()
                             for name, param in self.model.named_parameters()}

            with torch.no_grad():
                for name, param in self.model.named_parameters():
                    param.data.copy_(params[name])

        # Forward pass
        predictions = self.model(support_x)
        loss = nn.functional.mse_loss(predictions, support_y)

        # Restore parameters
        if params is not None:
            with torch.no_grad():
                for name, param in self.model.named_parameters():
                    param.data.copy_(original_params[name])

        return loss

    def _measure_convergence(self, task: Dict, threshold: float = 0.01) -> int:
        """Measure how many inner steps to reach threshold"""
        adapted_params = {name: param.clone()
                         for name, param in self.model.named_parameters()}

        support_x = task['support_x']
        support_y = task['support_y']
        prev_loss = float('inf')

        # Temporarily adapt model
        original_params = {name: param.clone()
                         for name, param in self.model.named_parameters()}

        for step in range(50):
            # Apply adaptation
            with torch.no_grad():
                for name, param in self.model.named_parameters():
                    param.data.copy_(adapted_params[name])

            loss = self._compute_loss(task)

            if abs(prev_loss - loss.item()) < threshold:
                # Restore original
                with torch.no_grad():
                    for name, param in self.model.named_parameters():
                        param.data.copy_(original_params[name])
                return step

            prev_loss = loss.item()

            # Gradient step
            self.model.zero_grad()
            loss.backward()

            with torch.no_grad():
                for param in self.model.parameters():
                    if param.grad is not None:
                        adapted_params[name] -= self.config.inner_lr * param.grad.data

        # Restore original
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                param.data.copy_(original_params[name])

        return 50

    def _sample_task(self) -> Dict:
        """Sample a single task"""
        pass  # Implemented in task_distribution.py

    def _save_checkpoint(self, path: str):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'history': self.meta_history
        }
        torch.save(checkpoint, path)


class ReptilePOLLNValueNetwork(nn.Module):
    """Value network with Reptile support"""

    def __init__(self, state_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.value_head = nn.Linear(hidden_dim, 1)
        self.embedding = nn.Embedding(1000, state_dim)

    def forward(self, states: torch.Tensor) -> torch.Tensor:
        if states.dtype == torch.long:
            embedded = self.embedding(states)
        else:
            embedded = states

        features = self.encoder(embedded)
        value = self.value_head(features)
        return value.squeeze(-1)


def compare_maml_reptile() -> Dict[str, Any]:
    """
    Compare MAML vs Reptile performance

    Validates the 3x speedup claim of Reptile.
    """
    print("\n" + "=" * 60)
    print("MAML vs Reptile Comparison")
    print("=" * 60)

    # Task sampler
    def task_sampler():
        return [generate_mock_task() for _ in range(32)]

    # 1. Run MAML
    print("\n1. Running MAML...")
    from maml_implementation import MAMLAgent, MAMLConfig

    maml_config = MAMLConfig(
        inner_lr=0.01,
        outer_lr=0.001,
        inner_steps=5,
        meta_batch_size=32,
        meta_epochs=20  # Short for comparison
    )

    maml_model = ReptilePOLLNValueNetwork()
    maml = MAMLAgent(maml_config, maml_model)

    start_time = time.time()
    maml_results = maml.meta_train(task_sampler)
    maml_time = time.time() - start_time

    # 2. Run Reptile
    print("\n2. Running Reptile...")
    reptile_config = ReptileConfig(
        meta_lr=0.1,
        inner_lr=0.01,
        inner_steps=10,
        meta_batch_size=32,
        num_iterations=1000  # Roughly equivalent to 20 MAML epochs
    )

    reptile_model = ReptilePOLLNValueNetwork()
    reptile = ReptileAgent(reptile_config, reptile_model)

    start_time = time.time()
    reptile_results = reptile.meta_train(task_sampler)
    reptile_time = time.time() - start_time

    # 3. Comparison
    print("\n3. Performance Comparison")
    print("-" * 60)

    comparison = {
        'maml': {
            'training_time': maml_time,
            'best_val_loss': maml_results['best_val_loss'],
            'adaptation_speed': np.mean(maml_results['meta_history']['adaptation_speed']),
            'memory_usage': 'high (second-order)'
        },
        'reptile': {
            'training_time': reptile_time,
            'best_val_loss': reptile_results['best_val_loss'],
            'adaptation_speed': np.mean(reptile_results['meta_history']['adaptation_speed']),
            'memory_usage': 'low (first-order)'
        },
        'speedup': maml_time / reptile_time,
        'performance_ratio': reptile_results['best_val_loss'] / maml_results['best_val_loss']
    }

    print(f"\nTraining Time:")
    print(f"  MAML: {maml_time:.2f}s")
    print(f"  Reptile: {reptile_time:.2f}s")
    print(f"  Speedup: {comparison['speedup']:.2f}x")

    print(f"\nValidation Loss:")
    print(f"  MAML: {comparison['maml']['best_val_loss']:.4f}")
    print(f"  Reptile: {comparison['reptile']['best_val_loss']:.4f}")

    print(f"\nAdaptation Speed:")
    print(f"  MAML: {comparison['maml']['adaptation_speed']:.1f} steps")
    print(f"  Reptile: {comparison['reptile']['adaptation_speed']:.1f} steps")

    # Plot comparison
    plot_comparison(maml_results, reptile_results)

    return comparison


def plot_comparison(maml_results: Dict, reptile_results: Dict):
    """Plot MAML vs Reptile comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Training loss
    ax = axes[0, 0]
    ax.plot(maml_results['meta_history']['train_loss'],
            label='MAML', marker='o')
    ax.plot(reptile_results['meta_history']['train_loss'],
            label='Reptile', marker='s')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Training Loss')
    ax.set_title('Training Loss')
    ax.legend()
    ax.set_yscale('log')

    # Validation loss
    ax = axes[0, 1]
    ax.plot(maml_results['meta_history']['val_loss'],
            label='MAML', marker='o')
    ax.plot(reptile_results['meta_history']['val_loss'],
            label='Reptile', marker='s')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Validation Loss')
    ax.set_title('Validation Loss')
    ax.legend()
    ax.set_yscale('log')

    # Adaptation speed
    ax = axes[1, 0]
    ax.plot(maml_results['meta_history']['adaptation_speed'],
            label='MAML', marker='o')
    ax.plot(reptile_results['meta_history']['adaptation_speed'],
            label='Reptile', marker='s')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Adaptation Steps')
    ax.set_title('Adaptation Speed')
    ax.legend()

    # Computation time
    ax = axes[1, 1]
    if reptile_results['meta_history']['computation_time']:
        ax.plot(reptile_results['meta_history']['computation_time'],
                label='Reptile', marker='s')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Time per Iteration (s)')
    ax.set_title('Computation Time')
    ax.legend()

    plt.tight_layout()
    plt.savefig('simulations/advanced/metalearning/maml_reptile_comparison.png', dpi=150)
    plt.close()

    print("\nSaved comparison plot to maml_reptile_comparison.png")


def optimize_reptile_hyperparameters() -> Dict[str, Any]:
    """
    Optimize Reptile hyperparameters

    Key parameters to optimize:
    1. Meta-learning rate (ε): controls how much to move toward adapted params
    2. Inner learning rate (α): task adaptation speed
    3. Inner steps (K): how much to adapt per task
    4. Meta-batch size: stability of meta-update
    """
    print("\nOptimizing Reptile hyperparameters...")

    grid = {
        'meta_lr': [0.01, 0.1, 0.5],
        'inner_lr': [0.001, 0.01, 0.1],
        'inner_steps': [5, 10, 20],
        'meta_batch_size': [16, 32, 64]
    }

    results = []
    best_config = None
    best_val_loss = float('inf')

    for _ in range(20):
        config = ReptileConfig(
            meta_lr=np.random.choice(grid['meta_lr']),
            inner_lr=np.random.choice(grid['inner_lr']),
            inner_steps=int(np.random.choice(grid['inner_steps'])),
            meta_batch_size=int(np.random.choice(grid['meta_batch_size'])),
            num_iterations=500  # Short for search
        )

        model = ReptilePOLLNValueNetwork()
        reptile = ReptileAgent(config, model)

        def task_sampler():
            return [generate_mock_task() for _ in range(config.meta_batch_size)]

        stats = reptile.meta_train(task_sampler)

        results.append({
            'config': config,
            'val_loss': stats['best_val_loss']
        })

        if stats['best_val_loss'] < best_val_loss:
            best_val_loss = stats['best_val_loss']
            best_config = config

    print(f"\nBest Reptile Configuration:")
    print(f"  Meta LR: {best_config.meta_lr}")
    print(f"  Inner LR: {best_config.inner_lr}")
    print(f"  Inner Steps: {best_config.inner_steps}")
    print(f"  Meta Batch Size: {best_config.meta_batch_size}")
    print(f"  Best Validation Loss: {best_val_loss:.4f}")

    return {
        'best_config': best_config,
        'best_val_loss': best_val_loss,
        'all_results': results
    }


def generate_mock_task(
    state_dim: int = 128,
    num_support: int = 25,
    num_query: int = 15
) -> Dict[str, torch.Tensor]:
    """Generate a mock task for testing"""
    support_x = torch.randn(num_support, state_dim)
    support_y = torch.randn(num_support)
    query_x = torch.randn(num_query, state_dim)
    query_y = torch.randn(num_query)

    return {
        'support_x': support_x,
        'support_y': support_y,
        'query_x': query_x,
        'query_y': query_y
    }


def main():
    """Main execution"""
    print("=" * 60)
    print("Reptile Implementation for POLLN")
    print("=" * 60)

    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)

    # 1. Optimize hyperparameters
    print("\n1. Hyperparameter Optimization")
    print("-" * 60)
    optimal_config = optimize_reptile_hyperparameters()

    # 2. Compare MAML vs Reptile
    print("\n2. MAML vs Reptile Comparison")
    print("-" * 60)
    comparison = compare_maml_reptile()

    # 3. Generate recommendations
    print("\n3. Reptile Recommendations")
    print("-" * 60)
    recommendations = {
        'meta_lr': optimal_config['best_config'].meta_lr,
        'inner_lr': optimal_config['best_config'].inner_lr,
        'inner_steps': optimal_config['best_config'].inner_steps,
        'meta_batch_size': optimal_config['best_config'].meta_batch_size,
        'speedup_vs_maml': f"{comparison['speedup']:.2f}x",
        'performance_vs_maml': f"{comparison['performance_ratio']:.2f}x",
        'recommended': 'Reptile' if comparison['speedup'] > 2.5 else 'MAML'
    }

    print("\nOptimal Reptile Configuration:")
    for key, value in recommendations.items():
        print(f"  {key}: {value}")

    # Save recommendations
    import json
    with open('simulations/advanced/metalearning/reptile_config.json', 'w') as f:
        json.dump(recommendations, f, indent=2)

    print("\n" + "=" * 60)
    print("Reptile implementation complete!")
    print("=" * 60)

    return recommendations


if __name__ == '__main__':
    main()
