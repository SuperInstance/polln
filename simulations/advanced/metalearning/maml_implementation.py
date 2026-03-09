"""
Model-Agnostic Meta-Learning (MAML) Implementation for POLLN

Implements MAML for rapid adaptation of POLLN agents.
Key innovation: Learn initialization that can adapt to new tasks with few gradient steps.

Mathematical Foundation:
- Inner loop: θ'_i = θ - α∇_θ L_Ti(f_θ)  (adapt to task T_i)
- Outer loop: θ = θ - β∇_θ Σ L_Ti(f_θ'_i)  (meta-update across tasks)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Callable, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path


@dataclass
class MAMLConfig:
    """MAML hyperparameters"""
    inner_lr: float = 0.01          # α: adaptation learning rate
    outer_lr: float = 0.001         # β: meta-learning rate
    inner_steps: int = 5            # K: gradient steps per task
    meta_batch_size: int = 32       # Tasks per meta-update
    first_order: bool = False       # Use first-order approximation
    adapt_all_layers: bool = True   # Whether to adapt all layers
    frozen_layers: List[str] = None # Layers to freeze during adaptation

    # Task sampling
    num_tasks: int = 100            # Total tasks for meta-training
    shots: int = 5                  # K-shot learning (support examples)
    ways: int = 5                   # N-way classification (tasks per batch)

    # Optimization
    meta_epochs: int = 100          # Meta-training epochs
    val_tasks: int = 20             # Tasks for validation
    test_tasks: int = 20            # Tasks for testing


class MAMLAgent:
    """
    MAML-adaptable POLLN agent

    Implements bi-level optimization for meta-learning.
    """

    def __init__(self, config: MAMLConfig, model: nn.Module):
        self.config = config
        self.model = model
        self.meta_optimizer = optim.Adam(
            model.parameters(),
            lr=config.outer_lr
        )

        # Track meta-learning progress
        self.meta_history = {
            'train_loss': [],
            'val_loss': [],
            'adaptation_speed': [],
            'inner_losses': []
        }

        # Layer-specific learning rates
        self.layer_lrs = self._init_layer_lrs()

    def _init_layer_lrs(self) -> Dict[str, float]:
        """Initialize layer-specific learning rates"""
        if not self.config.adapt_all_layers:
            # Lower LR for frozen layers
            lrs = {}
            for name, param in self.model.named_parameters():
                if any(fl in name for fl in (self.config.frozen_layers or [])):
                    lrs[name] = self.config.inner_lr * 0.1
                else:
                    lrs[name] = self.config.inner_lr
            return lrs
        return {name: self.config.inner_lr
                for name, _ in self.model.named_parameters()}

    def inner_loop(self, task: Dict[str, torch.Tensor]) -> nn.Module:
        """
        Inner loop: Adapt to specific task

        Args:
            task: Dictionary with 'support_x', 'support_y', 'query_x', 'query_y'

        Returns:
            Adapted model copy
        """
        # Create a copy of the model for this task
        adapted_model = type(self.model)(*self.model.init_args)
        adapted_model.load_state_dict(self.model.state_dict())

        # Inner loop optimizer
        inner_optimizer = optim.SGD(
            adapted_model.parameters(),
            lr=self.config.inner_lr
        )

        support_x = task['support_x']
        support_y = task['support_y']

        inner_losses = []

        # K steps of gradient descent on support set
        for step in range(self.config.inner_steps):
            inner_optimizer.zero_grad()

            # Forward pass
            predictions = adapted_model(support_x)
            loss = nn.functional.mse_loss(predictions, support_y)

            # Backward pass
            loss.backward()

            # Apply layer-specific learning rates
            with torch.no_grad():
                for name, param in adapted_model.named_parameters():
                    if param.grad is not None:
                        param.data -= self.layer_lrs.get(name, self.config.inner_lr) * param.grad.data

            inner_losses.append(loss.item())

        self.meta_history['inner_losses'].append(inner_losses)

        return adapted_model

    def outer_loop(self, task_batch: List[Dict[str, torch.Tensor]]) -> Dict[str, float]:
        """
        Outer loop: Meta-update across task batch

        Args:
            task_batch: List of tasks

        Returns:
            Dictionary with meta-loss and metrics
        """
        meta_loss = 0.0
        query_losses = []

        # Compute adapted losses for each task
        for task in task_batch:
            # Inner loop: adapt to task
            adapted_model = self.inner_loop(task)

            # Compute loss on query set
            query_x = task['query_x']
            query_y = task['query_y']

            predictions = adapted_model(query_x)
            query_loss = nn.functional.mse_loss(predictions, query_y)

            meta_loss += query_loss
            query_losses.append(query_loss.item())

        # Average across tasks
        meta_loss /= len(task_batch)

        # Meta-update: update initial parameters
        self.meta_optimizer.zero_grad()

        if self.config.first_order:
            # First-order approximation (ignore second-order derivatives)
            meta_loss.backward(create_graph=False)
        else:
            # Full second-order MAML
            meta_loss.backward(create_graph=True)

        self.meta_optimizer.step()

        return {
            'meta_loss': meta_loss.item(),
            'query_loss_mean': np.mean(query_losses),
            'query_loss_std': np.std(query_losses)
        }

    def meta_train(self, task_sampler: Callable[[], List[Dict]]) -> Dict[str, Any]:
        """
        Full meta-training loop

        Args:
            task_sampler: Function that samples a batch of tasks

        Returns:
            Training statistics and final performance
        """
        print(f"Starting MAML meta-training...")
        print(f"Config: {self.config}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

        best_val_loss = float('inf')
        patience_counter = 0
        max_patience = 10

        for epoch in range(self.config.meta_epochs):
            # Sample meta-training tasks
            train_tasks = task_sampler()

            # Meta-update on training tasks
            train_metrics = self.outer_loop(train_tasks)

            # Validation
            if epoch % 5 == 0:
                val_tasks = [self._sample_task() for _ in range(self.config.val_tasks)]
                val_metrics = self.evaluate(val_tasks)

                print(f"Epoch {epoch}: "
                      f"Train Loss={train_metrics['meta_loss']:.4f}, "
                      f"Val Loss={val_metrics['val_loss']:.4f}, "
                      f"Adapt Speed={val_metrics['adaptation_steps']:.1f} steps")

                self.meta_history['train_loss'].append(train_metrics['meta_loss'])
                self.meta_history['val_loss'].append(val_metrics['val_loss'])
                self.meta_history['adaptation_speed'].append(
                    val_metrics['adaptation_steps']
                )

                # Early stopping
                if val_metrics['val_loss'] < best_val_loss:
                    best_val_loss = val_metrics['val_loss']
                    patience_counter = 0
                    self._save_checkpoint(f'best_maml_epoch_{epoch}.pt')
                else:
                    patience_counter += 1

                if patience_counter >= max_patience:
                    print(f"Early stopping at epoch {epoch}")
                    break

        return {
            'best_val_loss': best_val_loss,
            'final_train_loss': train_metrics['meta_loss'],
            'meta_history': self.meta_history
        }

    def evaluate(self, tasks: List[Dict]) -> Dict[str, float]:
        """
        Evaluate meta-learning performance

        Measures:
        1. Post-adaptation loss (after K gradient steps)
        2. Adaptation speed (how quickly it converges)
        3. Sample efficiency (performance vs number of shots)
        """
        total_loss = 0.0
        adaptation_steps = []

        for task in tasks:
            # Measure adaptation speed
            adapted_model = self.inner_loop(task)

            # Evaluate on query set
            query_x = task['query_x']
            query_y = task['query_y']
            predictions = adapted_model(query_x)
            loss = nn.functional.mse_loss(predictions, query_y)

            total_loss += loss.item()

            # Track how many steps to convergence
            steps = self._measure_convergence(task)
            adaptation_steps.append(steps)

        return {
            'val_loss': total_loss / len(tasks),
            'adaptation_steps': np.mean(adaptation_steps)
        }

    def _measure_convergence(self, task: Dict, threshold: float = 0.01) -> int:
        """Measure how many inner steps to reach threshold"""
        adapted_model = type(self.model)(*self.model.init_args)
        adapted_model.load_state_dict(self.model.state_dict())

        support_x = task['support_x']
        support_y = task['support_y']

        prev_loss = float('inf')

        for step in range(50):  # Max 50 steps
            predictions = adapted_model(support_x)
            loss = nn.functional.mse_loss(predictions, support_y)

            if abs(prev_loss - loss) < threshold:
                return step

            prev_loss = loss.item()

            # Gradient step
            loss.backward()
            with torch.no_grad():
                for param in adapted_model.parameters():
                    if param.grad is not None:
                        param.data -= self.config.inner_lr * param.grad.data

        return 50

    def _sample_task(self) -> Dict:
        """Sample a single task (placeholder for task distribution)"""
        # This will be implemented in task_distribution.py
        pass

    def _save_checkpoint(self, path: str):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.meta_optimizer.state_dict(),
            'config': self.config,
            'history': self.meta_history
        }
        torch.save(checkpoint, path)

    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.meta_optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.meta_history = checkpoint['history']


class MAMLPOLLNValueNetwork(nn.Module):
    """
    Value network with MAML support

    Implements TD(lambda) value prediction with meta-learning.
    """

    def __init__(self, state_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.init_args = (state_dim, hidden_dim)

        # Network architecture
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        self.value_head = nn.Linear(hidden_dim, 1)

        # Embedding layer (often frozen in meta-learning)
        self.embedding = nn.Embedding(1000, state_dim)

    def forward(self, states: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        if states.dtype == torch.long:
            embedded = self.embedding(states)
        else:
            embedded = states

        features = self.encoder(embedded)
        value = self.value_head(features)
        return value.squeeze(-1)


def optimize_maml_hyperparameters() -> Dict[str, Any]:
    """
    Grid search for optimal MAML hyperparameters

    Tests:
    1. Inner learning rate: [0.001, 0.01, 0.1]
    2. Outer learning rate: [0.0001, 0.001, 0.01]
    3. Inner steps: [1, 5, 10]
    4. Meta-batch size: [16, 32, 64]

    Returns:
        Best hyperparameters and results
    """
    print("Optimizing MAML hyperparameters...")

    # Hyperparameter grid
    grid = {
        'inner_lr': [0.001, 0.01, 0.1],
        'outer_lr': [0.0001, 0.001, 0.01],
        'inner_steps': [1, 5, 10],
        'meta_batch_size': [16, 32, 64]
    }

    results = []
    best_config = None
    best_val_loss = float('inf')

    # Simplified search (sample from grid)
    for _ in range(20):  # 20 random combinations
        config = MAMLConfig(
            inner_lr=np.random.choice(grid['inner_lr']),
            outer_lr=np.random.choice(grid['outer_lr']),
            inner_steps=int(np.random.choice(grid['inner_steps'])),
            meta_batch_size=int(np.random.choice(grid['meta_batch_size'])),
            meta_epochs=20  # Short epochs for search
        )

        model = MAMLPOLLNValueNetwork()
        maml = MAMLAgent(config, model)

        # Quick training
        def mock_sampler():
            return [generate_mock_task() for _ in range(config.meta_batch_size)]

        stats = maml.meta_train(mock_sampler)

        results.append({
            'config': config,
            'val_loss': stats['best_val_loss']
        })

        if stats['best_val_loss'] < best_val_loss:
            best_val_loss = stats['best_val_loss']
            best_config = config

    # Analysis
    print(f"\nBest MAML Configuration:")
    print(f"  Inner LR: {best_config.inner_lr}")
    print(f"  Outer LR: {best_config.outer_lr}")
    print(f"  Inner Steps: {best_config.inner_steps}")
    print(f"  Meta Batch Size: {best_config.meta_batch_size}")
    print(f"  Best Validation Loss: {best_val_loss:.4f}")

    # Plot results
    plot_hyperparameter_heatmap(results)

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


def plot_hyperparameter_heatmap(results: List[Dict]):
    """Plot hyperparameter sensitivity"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Inner LR vs Outer LR
    ax = axes[0, 0]
    for inner_lr in [0.001, 0.01, 0.1]:
        filtered = [r for r in results if r['config'].inner_lr == inner_lr]
        if filtered:
            outer_lrs = [r['config'].outer_lr for r in filtered]
            val_losses = [r['val_loss'] for r in filtered]
            ax.plot(outer_lrs, val_losses, 'o-', label=f'inner_lr={inner_lr}')
    ax.set_xlabel('Outer LR')
    ax.set_ylabel('Validation Loss')
    ax.set_title('Inner LR vs Outer LR')
    ax.legend()
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Inner Steps vs Meta Batch Size
    ax = axes[0, 1]
    for steps in [1, 5, 10]:
        filtered = [r for r in results if r['config'].inner_steps == steps]
        if filtered:
            batch_sizes = [r['config'].meta_batch_size for r in filtered]
            val_losses = [r['val_loss'] for r in filtered]
            ax.plot(batch_sizes, val_losses, 'o-', label=f'steps={steps}')
    ax.set_xlabel('Meta Batch Size')
    ax.set_ylabel('Validation Loss')
    ax.set_title('Inner Steps vs Meta Batch Size')
    ax.legend()

    # Adaptation speed
    ax = axes[1, 0]
    steps = [r['config'].inner_steps for r in results]
    losses = [r['val_loss'] for r in results]
    ax.scatter(steps, losses, alpha=0.6)
    ax.set_xlabel('Inner Steps')
    ax.set_ylabel('Validation Loss')
    ax.set_title('Adaptation Speed')

    # Meta-batch efficiency
    ax = axes[1, 1]
    batch_sizes = [r['config'].meta_batch_size for r in results]
    losses = [r['val_loss'] for r in results]
    ax.scatter(batch_sizes, losses, alpha=0.6)
    ax.set_xlabel('Meta Batch Size')
    ax.set_ylabel('Validation Loss')
    ax.set_title('Meta-Batch Efficiency')

    plt.tight_layout()
    plt.savefig('simulations/advanced/metalearning/maml_hyperparameters.png', dpi=150)
    plt.close()

    print("Saved MAML hyperparameter analysis to maml_hyperparameters.png")


def main():
    """Main execution"""
    print("=" * 60)
    print("MAML Implementation for POLLN")
    print("=" * 60)

    # Create output directory
    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)

    # 1. Optimize hyperparameters
    print("\n1. Hyperparameter Optimization")
    print("-" * 60)
    optimal_config = optimize_maml_hyperparameters()

    # 2. Train full MAML model
    print("\n2. Full MAML Training")
    print("-" * 60)
    config = optimal_config['best_config']
    config.meta_epochs = 100  # Full training

    model = MAMLPOLLNValueNetwork()
    maml = MAMLAgent(config, model)

    def task_sampler():
        return [generate_mock_task() for _ in range(config.meta_batch_size)]

    results = maml.meta_train(task_sampler)

    # 3. Generate recommendations
    print("\n3. MAML Recommendations")
    print("-" * 60)
    recommendations = {
        'inner_lr': config.inner_lr,
        'outer_lr': config.outer_lr,
        'inner_steps': config.inner_steps,
        'meta_batch_size': config.meta_batch_size,
        'adapt_all_layers': config.adapt_all_layers,
        'first_order': config.first_order,
        'sample_efficiency': f"{config.shots}-shot learning",
        'expected_adaptation_speed': f"{np.mean(results['meta_history']['adaptation_speed']):.1f} steps"
    }

    print("\nOptimal MAML Configuration:")
    for key, value in recommendations.items():
        print(f"  {key}: {value}")

    # Save recommendations
    import json
    with open('simulations/advanced/metalearning/maml_config.json', 'w') as f:
        json.dump(recommendations, f, indent=2)

    print("\n" + "=" * 60)
    print("MAML implementation complete!")
    print("=" * 60)

    return recommendations


if __name__ == '__main__':
    main()
