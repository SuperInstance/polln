"""
META Tile Plasticity Rules Simulation
======================================

Compares different synaptic plasticity rules for META tile learning.

Mathematical Foundation:
    Hebbian: Δw_ij = η × pre_i × post_j
    Oja's rule: Δw_ij = η × pre_i × post_j - α × post_j² × w_ij
    RPROP: Resilient backpropagation
    Adam: Adaptive moments

Hypotheses:
    H2: For learning rate η < 2/λ_max, weights converge
    H2: Oja's rule provides best stability for META tiles
    H2: Meta-learning efficiency varies by rule
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
from abc import ABC, abstractmethod
import json
from pathlib import Path


# Set random seeds
np.random.seed(42)
torch.manual_seed(42)


@dataclass
class PlasticityConfig:
    """Configuration for plasticity simulation"""
    n_neurons: int = 100
    n_synapses: int = 500
    n_tasks: int = 5
    n_episodes: int = 1000

    # Learning rates
    base_lr: float = 0.01
    max_lr: float = 0.1

    # Plasticity parameters
    hebbian_lr: float = 0.01
    oja_lr: float = 0.01
    oja_decay: float = 0.001
    rprop_eta_plus: float = 1.2
    rprop_eta_minus: float = 0.5
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999


class SynapticMatrix:
    """
    Represents synaptic weight matrix between neurons.

    Tracks:
    - Weights
    - Eligibility traces (for meta-learning)
    - Update history
    """

    def __init__(self, n_pre: int, n_post: int):
        self.n_pre = n_pre
        self.n_post = n_post

        # Initialize with small random weights
        self.weights = np.random.randn(n_pre, n_post) * 0.01

        # Eligibility traces (for meta-learning)
        self.eligibility = np.zeros_like(self.weights)

        # Update history
        self.update_history: List[np.ndarray] = [self.weights.copy()]

        # Statistics
        self.weight_variance: List[float] = [np.var(self.weights)]
        self.convergence_metric: List[float] = []

    def update(self, delta: np.ndarray):
        """Apply weight update"""
        self.weights += delta
        self.update_history.append(self.weights.copy())
        self.weight_variance.append(np.var(self.weights))

    def get_convergence_metric(self, window: int = 10) -> float:
        """Measure how much weights are changing"""
        if len(self.update_history) < window + 1:
            return float('inf')

        recent = self.update_history[-window:]
        changes = [np.linalg.norm(recent[i] - recent[i-1]) for i in range(1, len(recent))]
        return np.mean(changes)


class PlasticityRule(ABC):
    """Abstract base class for plasticity rules"""

    def __init__(self, config: PlasticityConfig):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        """Compute weight update ΔW"""
        pass


class HebbianRule(PlasticityRule):
    """
    Basic Hebbian learning: neurons that fire together, wire together.

    Δw_ij = η × pre_i × post_j
    """

    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        eta = self.config.hebbian_lr
        delta = eta * np.outer(pre, post)
        return delta


class OjaRule(PlasticityRule):
    """
    Oja's rule: Normalized Hebbian learning preventing unbounded growth.

    Δw_ij = η × pre_i × post_j - α × post_j² × w_ij

    The decay term keeps weights bounded and promotes normalization.
    """

    def __init__(self, config: PlasticityConfig):
        super().__init__(config)
        self.decay = config.oja_decay

    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        eta = self.config.oja_lr
        alpha = self.decay

        # Hebbian term
        hebbian = eta * np.outer(pre, post)

        # Decay term (normalization)
        decay = alpha * np.outer(post * post, np.ones(weights.shape[0])).T * weights

        return hebbian - decay.T


class RPROPRule(PlasticityRule):
    """
    Resilient Backpropagation (RPROP): Adaptive learning rates per weight.

    Uses sign of gradient to adjust individual learning rates.
    """

    def __init__(self, config: PlasticityConfig):
        super().__init__(config)
        self.prev_gradient = None
        self.learning_rates = np.ones((config.n_synapses, config.n_synapses)) * config.base_lr
        self.eta_plus = config.rprop_eta_plus
        self.eta_minus = config.rprop_eta_minus

    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        # Compute gradient
        gradient = np.outer(pre, post)

        if self.prev_gradient is None:
            self.prev_gradient = gradient
            return -self.learning_rates * np.sign(gradient)

        # Update learning rates based on gradient sign changes
        product = gradient * self.prev_gradient

        # Increase LR if gradient didn't change sign
        increase_mask = product > 0
        self.learning_rates[increase_mask] *= self.eta_plus

        # Decrease LR if gradient changed sign
        decrease_mask = product < 0
        self.learning_rates[decrease_mask] *= self.eta_minus

        # Clip learning rates
        self.learning_rates = np.clip(self.learning_rates,
                                      0.000001,
                                      self.config.max_lr)

        self.prev_gradient = gradient.copy()

        return -self.learning_rates * np.sign(gradient)


class AntiHebbianRule(PlasticityRule):
    """
    Anti-Hebbian learning: neurons that fire together, unwire.

    Useful for promoting diversity and preventing collapse.
    """

    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        eta = self.config.hebbian_lr
        delta = -eta * np.outer(pre, post)
        return delta


class BCMRule(PlasticityRule):
    """
    Bienenstock-Cooper-Munro rule: Sliding threshold for homeostatic plasticity.

    Δw_ij = η × pre_i × post_j × (post_j - θ)

    Where θ is a sliding threshold that maintains selectivity.
    """

    def __init__(self, config: PlasticityConfig):
        super().__init__(config)
        self.threshold = 0.5  # Moving average threshold
        self.threshold_lr = 0.001

    def compute_update(self, pre: np.ndarray, post: np.ndarray,
                      weights: np.ndarray) -> np.ndarray:
        eta = self.config.hebbian_lr

        # Update sliding threshold
        self.threshold += self.threshold_lr * (np.mean(post**2) - self.threshold)

        # BCM update with sliding threshold
        modulation = post - self.threshold
        delta = eta * np.outer(pre, post * modulation)

        return delta


class MetaLearningTask:
    """
    Meta-learning task for testing plasticity rules.

    Task: Learn to predict output from input with few-shot adaptation.
    """

    def __init__(self, task_id: int, input_dim: int, output_dim: int):
        self.task_id = task_id
        self.input_dim = input_dim
        self.output_dim = output_dim

        # Generate task-specific parameters
        self.W_true = np.random.randn(input_dim, output_dim) * 0.5
        self.b_true = np.random.randn(output_dim) * 0.1

    def generate_samples(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate input-output pairs"""
        X = np.random.randn(n_samples, self.input_dim)
        y = X @ self.W_true + self.b_true + np.random.randn(n_samples, self.output_dim) * 0.1
        return X, y

    def evaluate(self, W: np.ndarray) -> float:
        """Evaluate prediction error with given weights"""
        X_test, y_test = self.generate_samples(100)
        y_pred = X_test @ W
        error = np.mean((y_pred - y_test)**2)
        return error


class PlasticitySimulation:
    """
    Main simulation comparing plasticity rules for meta-learning.
    """

    def __init__(self, config: PlasticityConfig):
        self.config = config

        # Initialize plasticity rules
        self.rules: List[PlasticityRule] = [
            HebbianRule(config),
            OjaRule(config),
            BCMRule(config),
            AntiHebbianRule(config),
        ]

        # Create synaptic matrices for each rule
        self.synapses: Dict[str, SynapticMatrix] = {}
        for rule in self.rules:
            self.synapses[rule.name] = SynapticMatrix(
                config.n_synapses,
                config.n_synapses
            )

        # Generate meta-learning tasks
        self.tasks = [
            MetaLearningTask(i, config.n_synapses, config.n_synapses)
            for i in range(config.n_tasks)
        ]

        # Results storage
        self.results: Dict[str, Dict] = {rule.name: {} for rule in self.rules}

    def simulate_episode(self, rule: PlasticityRule, synapse: SynapticMatrix,
                        task: MetaLearningTask, episode: int) -> Dict:
        """Simulate one learning episode"""

        # Generate few-shot samples
        n_shot = 5
        X, y = task.generate_samples(n_shot)

        # Compute pre- and post-synaptic activity
        pre = X.mean(axis=0)  # Average input activity
        post = y.mean(axis=0)  # Average output activity

        # Compute weight update
        delta = rule.compute_update(pre, post, synapse.weights)

        # Apply update
        synapse.update(delta)

        # Evaluate performance
        error = task.evaluate(synapse.weights)

        return {
            'episode': episode,
            'error': error,
            'weight_change': np.linalg.norm(delta),
            'weight_variance': np.var(synapse.weights),
            'convergence': synapse.get_convergence_metric()
        }

    def run_rule(self, rule: PlasticityRule) -> Dict:
        """Run full simulation for one plasticity rule"""
        print(f"\nRunning {rule.name}...")

        synapse = self.synapses[rule.name]
        history = []

        for episode in range(self.config.n_episodes):
            # Cycle through tasks
            task = self.tasks[episode % len(self.tasks)]

            # Simulate episode
            episode_result = self.simulate_episode(rule, synapse, task, episode)
            episode_result['rule'] = rule.name
            history.append(episode_result)

            # Early stopping if converged
            if episode > 100 and synapse.get_convergence_metric() < 1e-6:
                print(f"  Converged at episode {episode}")
                break

        # Compute statistics
        errors = [h['error'] for h in history]
        weight_changes = [h['weight_change'] for h in history]
        convergence_metrics = [h['convergence'] for h in history]

        stats = {
            'history': history,
            'final_error': errors[-1] if errors else float('inf'),
            'mean_error': np.mean(errors),
            'std_error': np.std(errors),
            'final_weight_variance': synapse.weight_variance[-1],
            'convergence_episode': next(
                (i for i, m in enumerate(convergence_metrics) if m < 1e-6),
                len(convergence_metrics)
            ),
            'stability_score': self._compute_stability(history)
        }

        print(f"  Final error: {stats['final_error']:.4f}")
        print(f"  Convergence: Episode {stats['convergence_episode']}")
        print(f"  Stability: {stats['stability_score']:.4f}")

        return stats

    def _compute_stability(self, history: List[Dict]) -> float:
        """Compute stability score (lower variance = more stable)"""
        if len(history) < 10:
            return 0.0

        errors = [h['error'] for h in history]
        # Stability = 1 / (1 + variance of recent errors)
        recent_errors = errors[-min(100, len(errors)):]
        variance = np.var(recent_errors)
        return 1.0 / (1.0 + variance)

    def run(self) -> Dict:
        """Run comparison across all plasticity rules"""
        print("="*70)
        print("META TILE PLASTICITY RULES SIMULATION")
        print("="*70)

        for rule in self.rules:
            stats = self.run_rule(rule)
            self.results[rule.name] = stats

        # Comparative analysis
        comparison = self._compare_rules()

        return {
            'individual': self.results,
            'comparison': comparison
        }

    def _compare_rules(self) -> Dict:
        """Compare performance across rules"""
        comparison = {}

        metrics = ['final_error', 'mean_error', 'convergence_episode', 'stability_score']

        for metric in metrics:
            values = {
                name: results[metric]
                for name, results in self.results.items()
            }

            # Find best
            if metric == 'convergence_episode':
                best_name = min(values, key=values.get)  # Lower is better
            else:
                best_name = max(values, key=values.get)  # Higher is better for stability

            comparison[metric] = {
                'values': values,
                'best': best_name,
                'best_value': values[best_name]
            }

        return comparison

    def visualize(self, save_path: Optional[Path] = None):
        """Visualize comparison results"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Learning curves (error over time)
        ax = axes[0, 0]
        for rule_name, results in self.results.items():
            history = results['history']
            errors = [h['error'] for h in history]
            # Smooth curve
            window = 20
            if len(errors) > window:
                errors_smooth = np.convolve(errors, np.ones(window)/window, mode='valid')
                ax.plot(errors_smooth, label=rule_name, linewidth=2)
            else:
                ax.plot(errors, label=rule_name, linewidth=2, alpha=0.7)

        ax.set_xlabel('Episode')
        ax.set_ylabel('Error')
        ax.set_title('Learning Curves')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')

        # 2. Weight variance over time
        ax = axes[0, 1]
        for rule_name, synapse in self.synapses.items():
            if rule_name in self.results:
                variances = synapse.weight_variance
                ax.plot(variances, label=rule_name, linewidth=2, alpha=0.7)

        ax.set_xlabel('Update Step')
        ax.set_ylabel('Weight Variance')
        ax.set_title('Weight Variance Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Convergence comparison
        ax = axes[1, 0]
        names = list(self.results.keys())
        convergence_episodes = [
            self.results[name]['convergence_episode']
            for name in names
        ]
        colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
        ax.barh(names, convergence_episodes, color=colors)
        ax.set_xlabel('Episode')
        ax.set_title('Convergence Speed (lower is better)')
        ax.grid(True, alpha=0.3, axis='x')

        # 4. Stability comparison
        ax = axes[1, 1]
        stability_scores = [
            self.results[name]['stability_score']
            for name in names
        ]
        ax.bar(names, stability_scores, color=colors)
        ax.set_ylabel('Stability Score')
        ax.set_title('Learning Stability (higher is better)')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plasticity comparison plot to {save_path}")

        return fig


def run_learning_rate_sweep():
    """Experiment: Find optimal learning rate for each rule"""
    print("\n" + "="*70)
    print("EXPERIMENT: Learning Rate Sweep")
    print("="*70)

    learning_rates = np.logspace(-4, -1, 10)
    results = {rule.__name__: [] for rule in [HebbianRule, OjaRule, BCMRule]}

    for lr in learning_rates:
        config = PlasticityConfig(
            n_neurons=50,
            n_synapses=50,
            n_tasks=3,
            n_episodes=500,
            hebbian_lr=lr,
            oja_lr=lr
        )

        sim = PlasticitySimulation(config)

        # Test each rule
        for RuleClass in [HebbianRule, OjaRule, BCMRule]:
            rule = RuleClass(config)
            synapse = SynapticMatrix(config.n_synapses, config.n_synapses)

            # Run simplified simulation
            task = sim.tasks[0]
            final_error = None
            for episode in range(config.n_episodes):
                X, y = task.generate_samples(5)
                pre = X.mean(axis=0)
                post = y.mean(axis=0)
                delta = rule.compute_update(pre, post, synapse.weights)
                synapse.update(delta)

                if episode % 100 == 0:
                    error = task.evaluate(synapse.weights)
                    final_error = error

            results[RuleClass.__name__].append({
                'learning_rate': lr,
                'final_error': final_error
            })

    return results


def run_convergence_analysis():
    """Experiment: Analyze convergence conditions"""
    print("\n" + "="*70)
    print("EXPERIMENT: Convergence Analysis")
    print("="*70)

    # Test H2: For η < 2/λ_max, weights converge
    # Estimate λ_max (maximum eigenvalue of weight matrix)

    config = PlasticityConfig(
        n_neurons=100,
        n_synapses=100,
        n_tasks=3,
        n_episodes=1000,
        hebbian_lr=0.01
    )

    # Compute eigenvalues of typical weight matrix
    W = np.random.randn(config.n_synapses, config.n_synapses) * 0.01
    eigenvalues = np.linalg.eigvals(W @ W.T)  # W @ W.T for symmetric
    lambda_max = np.max(np.real(eigenvalues))

    # Theoretical max learning rate for convergence
    max_lr_theoretical = 2.0 / lambda_max if lambda_max > 0 else 1.0

    print(f"  λ_max = {lambda_max:.6f}")
    print(f"  Theoretical max LR for convergence: {max_lr_theoretical:.6f}")

    # Test different learning rates
    lrs = np.linspace(0.1 * max_lr_theoretical, 2.0 * max_lr_theoretical, 10)
    convergence_results = []

    for lr in lrs:
        config.hebbian_lr = lr
        sim = PlasticitySimulation(config)
        rule = HebbianRule(config)
        synapse = SynapticMatrix(config.n_synapses, config.n_synapses)

        converged = False
        convergence_episode = None

        for episode in range(config.n_episodes):
            task = sim.tasks[episode % len(sim.tasks)]
            X, y = task.generate_samples(5)
            pre = X.mean(axis=0)
            post = y.mean(axis=0)
            delta = rule.compute_update(pre, post, synapse.weights)
            synapse.update(delta)

            if episode > 100 and synapse.get_convergence_metric() < 1e-6:
                converged = True
                convergence_episode = episode
                break

        convergence_results.append({
            'learning_rate': lr,
            'converged': converged,
            'convergence_episode': convergence_episode,
            'relative_lr': lr / max_lr_theoretical
        })

    return {
        'lambda_max': lambda_max,
        'max_lr_theoretical': max_lr_theoretical,
        'results': convergence_results
    }


def main():
    """Run all plasticity experiments"""
    # Create output directory
    output_dir = Path('/c/Users/casey/polln/simulations/results')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run main comparison
    config = PlasticityConfig(
        n_neurons=100,
        n_synapses=100,
        n_tasks=5,
        n_episodes=1000
    )

    sim = PlasticitySimulation(config)
    results = sim.run()

    print("\n" + "="*70)
    print("PLASTICITY RULES COMPARISON RESULTS")
    print("="*70)

    comparison = results['comparison']
    print("\nBest performers by metric:")
    for metric, data in comparison.items():
        print(f"  {metric}: {data['best']} ({data['best_value']:.4f})")

    # Visualize
    fig_dir = Path('/c/Users/casey/polln/simulations/figures')
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig = sim.visualize(fig_dir / 'plasticity_comparison.png')

    # Run experiments
    lr_results = run_learning_rate_sweep()
    convergence_results = run_convergence_analysis()

    # Save all results
    all_results = {
        'main_comparison': results,
        'learning_rate_sweep': lr_results,
        'convergence_analysis': convergence_results
    }

    results_path = output_dir / 'plasticity_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {results_path}")

    return results


if __name__ == '__main__':
    results = main()
