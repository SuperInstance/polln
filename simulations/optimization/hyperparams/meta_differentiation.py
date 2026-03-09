"""
META Tile Differentiation Parameters Optimization

Optimizes parameters for META tile differentiation and specialization.
Finds optimal signal response rates, differentiation thresholds, and plasticity rules.

Optimization Targets:
- Signal response rate: How quickly META tiles respond to signals [0.01, 0.05, 0.1, 0.2]
  - Higher: Faster differentiation but less stable
  - Lower: Slower differentiation but more stable

- Differentiation threshold: Signal strength required to differentiate [0.5, 0.7, 0.9, 0.95]
  - Lower: Easier to differentiate (may over-specialize)
  - Higher: Harder to differentiate (may under-specialize)

- Plasticity rule: Synaptic weight update rule ['hebbian', 'oja', 'bcm']
  - hebbian: Basic Hebbian learning (fire together, wire together)
  - oja: Oja's rule (normalized Hebbian)
  - bcm: Bienenstock-Cooper-Munro (homeostatic)

Metrics:
- Differentiation Speed: Episodes to reach stable specialization
- Specialization Quality: Performance on specialized tasks
- Stability: Resistance to catastrophic forgetting
"""

import numpy as np
import json
from typing import Dict, Tuple, List, Literal
from skopt import gp_minimize
from skopt.space import Real, Categorical
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# Plasticity Rules
# ============================================================================

class PlasticityRule:
    """Base class for plasticity rules"""

    def update(self, weights: np.ndarray, pre_synaptic: float, post_synaptic: float, lr: float = 0.01) -> np.ndarray:
        raise NotImplementedError


class HebbianRule(PlasticityRule):
    """
    Basic Hebbian learning: Δw = lr * pre * post
    'Neurons that fire together, wire together'
    """

    def update(self, weights: np.ndarray, pre_synaptic: float, post_synaptic: float, lr: float = 0.01) -> np.ndarray:
        delta_w = lr * pre_synaptic * post_synaptic
        return weights + delta_w


class OjaRule(PlasticityRule):
    """
    Oja's rule: Δw = lr * (pre * post - post^2 * w)
    Normalized Hebbian learning that prevents unbounded growth.
    """

    def update(self, weights: np.ndarray, pre_synaptic: float, post_synaptic: float, lr: float = 0.01) -> np.ndarray:
        delta_w = lr * (pre_synaptic * post_synaptic - post_synaptic ** 2 * weights)
        return weights + delta_w


class BCMRule(PlasticityRule):
    """
    Bienenstock-Cooper-Munro rule: Δw = lr * pre * post * (post - theta)
    Homeostatic plasticity that maintains average firing rate.
    """

    def __init__(self, theta: float = 0.5, tau: float = 100):
        self.theta = theta
        self.tau = tau
        self.post_history = []

    def update(self, weights: np.ndarray, pre_synaptic: float, post_synaptic: float, lr: float = 0.01) -> np.ndarray:
        # Update sliding threshold
        self.post_history.append(post_synaptic ** 2)
        if len(self.post_history) > self.tau:
            self.post_history.pop(0)

        avg_post = np.mean(self.post_history) if self.post_history else 0
        self.theta = avg_post

        # BCM update
        delta_w = lr * pre_synaptic * post_synaptic * (post_synaptic - self.theta)
        return weights + delta_w


# ============================================================================
# META Tile Simulation
# ============================================================================

class MetaTile:
    """
    Simulates a META tile that can differentiate into specialized types.

    Starts pluripotent (undifferentiated) and specializes based on signals.
    """

    def __init__(
        self,
        tile_id: int,
        signal_response_rate: float,
        differentiation_threshold: float,
        plasticity_rule: str
    ):
        self.id = tile_id
        self.signal_response_rate = signal_response_rate
        self.differentiation_threshold = differentiation_threshold
        self.plasticity_rule_name = plasticity_rule

        # Initialize plasticity rule
        if plasticity_rule == 'hebbian':
            self.plasticity_rule = HebbianRule()
        elif plasticity_rule == 'oja':
            self.plasticity_rule = OjaRule()
        elif plasticity_rule == 'bcm':
            self.plasticity_rule = BCMRule()
        else:
            raise ValueError(f"Unknown plasticity rule: {plasticity_rule}")

        # State
        self.differentiated = False
        self.specialization = None  # Will be set when differentiated

        # Connection weights (to different signal types)
        self.weights = np.random.rand(5) * 0.1 - 0.05  # 5 signal types

        # Activation history
        self.activation_history = []

    def process_signal(self, signal_type: int, signal_strength: float) -> float:
        """
        Process incoming signal and update weights.

        Returns:
            Activation level
        """
        # Get weight for this signal type
        weight = self.weights[signal_type]

        # Compute activation
        activation = weight * signal_strength

        # Update weights based on plasticity rule
        if self.differentiated:
            # If already differentiated, only strengthen specialization
            if self.specialization == signal_type:
                self.weights = self.plasticity_rule.update(
                    self.weights,
                    signal_strength,
                    activation,
                    lr=self.signal_response_rate
                )
        else:
            # If not differentiated, learn from all signals
            pre_synaptic = signal_strength
            post_synaptic = activation
            self.weights = self.plasticity_rule.update(
                self.weights,
                pre_synaptic,
                post_synaptic,
                lr=self.signal_response_rate
            )

        # Track activation
        self.activation_history.append(activation)

        # Check for differentiation
        if not self.differentiated and activation > self.differentiation_threshold:
            self.differentiate(signal_type)

        return activation

    def differentiate(self, specialization: int):
        """Differentiate into specialized type"""
        self.differentiated = True
        self.specialization = specialization

    def get_specialization_quality(self) -> float:
        """
        Measure how well-specialized the tile is.

        Returns:
            Quality score (higher is better)
        """
        if not self.differentiated:
            return 0.0

        # Quality = weight on specialization / sum of all weights
        spec_weight = self.weights[self.specialization]
        total_weight = np.sum(np.abs(self.weights))
        return spec_weight / (total_weight + 1e-10)


# ============================================================================
# Task Environment
# ============================================================================

class TaskEnvironment:
    """
    Simulates a multi-task environment where META tiles can specialize.
    """

    def __init__(self, n_tasks: int = 5):
        self.n_tasks = n_tasks
        self.current_task = 0
        self.task_switch_prob = 0.1

    def get_signal(self) -> Tuple[int, float]:
        """
        Get current task signal.

        Returns:
            (task_type, signal_strength)
        """
        # Randomly switch tasks
        if np.random.rand() < self.task_switch_prob:
            self.current_task = np.random.randint(0, self.n_tasks)

        # Return signal with strength
        signal_strength = np.random.uniform(0.5, 1.0)
        return self.current_task, signal_strength

    def get_task_reward(self, specialization: int, task: int) -> float:
        """
        Get reward for performing task with given specialization.

        Returns:
            Reward (higher if specialization matches task)
        """
        if specialization == task:
            return 1.0
        else:
            return -0.5


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(
    signal_response_rate: float,
    differentiation_threshold: float,
    plasticity_rule: str,
    n_tiles: int = 20,
    n_episodes: int = 500,
    seed: int = None
) -> Dict[str, float]:
    """
    Run META tile differentiation simulation with given parameters.

    Returns metrics on differentiation speed, quality, and stability.
    """

    if seed is not None:
        np.random.seed(seed)

    # Create tiles
    tiles = [
        MetaTile(
            tile_id=i,
            signal_response_rate=signal_response_rate,
            differentiation_threshold=differentiation_threshold,
            plasticity_rule=plasticity_rule
        )
        for i in range(n_tiles)
    ]

    # Create environment
    env = TaskEnvironment(n_tasks=5)

    # Track metrics
    differentiation_episodes = []
    specialization_qualities = []
    rewards = []
    catastrophic_forgetting = 0

    # Run episodes
    for episode in range(n_episodes):
        episode_reward = 0

        # Each episode: process signals for all tiles
        for tile in tiles:
            signal_type, signal_strength = env.get_signal()

            # Process signal
            activation = tile.process_signal(signal_type, signal_strength)

            # If differentiated, get reward
            if tile.differentiated:
                reward = env.get_task_reward(tile.specialization, signal_type)
                episode_reward += reward

                # Track quality
                quality = tile.get_specialization_quality()
                if quality > 0.5:
                    specialization_qualities.append(quality)

        rewards.append(episode_reward)

        # Track when each tile differentiates
        for tile in tiles:
            if tile.differentiated and tile.id not in [x[0] for x in differentiation_episodes]:
                differentiation_episodes.append((tile.id, episode))

        # Check for catastrophic forgetting (sudden performance drop)
        if episode > 50:
            recent_reward = np.mean(rewards[-10:])
            past_reward = np.mean(rewards[-50:-40])
            if past_reward - recent_reward > 2.0:
                catastrophic_forgetting += 1

    # Calculate metrics
    # Differentiation speed: average episode when tiles differentiate
    if differentiation_episodes:
        differentiation_speed = np.mean([ep for _, ep in differentiation_episodes])
    else:
        differentiation_speed = n_episodes  # Never differentiated

    # Specialization quality: average quality across all tiles
    if specialization_qualities:
        avg_specialization_quality = np.mean(specialization_qualities)
    else:
        avg_specialization_quality = 0.0

    # Stability: 1 - (catastrophic forgetting events / total episodes)
    stability = 1.0 - (catastrophic_forgetting / n_episodes)

    # Final performance: average reward over last 50 episodes
    final_performance = np.mean(rewards[-50:])

    # Differentiation rate: fraction of tiles that differentiated
    differentiation_rate = len(differentiation_episodes) / n_tiles

    return {
        'differentiation_speed': differentiation_speed,
        'specialization_quality': avg_specialization_quality,
        'stability': stability,
        'final_performance': final_performance,
        'differentiation_rate': differentiation_rate
    }


# ============================================================================
# Bayesian Optimization
# ============================================================================

# Parameter search space
search_space = [
    Real(0.01, 0.2, name='signal_response_rate'),
    Real(0.5, 0.95, name='differentiation_threshold'),
    Categorical(['hebbian', 'oja', 'bcm'], name='plasticity_rule')
]


@use_named_args(search_space)
def objective(**params) -> float:
    """Objective function for Bayesian optimization"""

    # Run simulation with 3 different random seeds
    results = []
    for seed in range(3):
        result = run_simulation(
            signal_response_rate=params['signal_response_rate'],
            differentiation_threshold=params['differentiation_threshold'],
            plasticity_rule=params['plasticity_rule'],
            n_tiles=20,
            n_episodes=500,
            seed=seed
        )
        results.append(result)

    # Average results
    avg_speed = np.mean([r['differentiation_speed'] for r in results])
    avg_quality = np.mean([r['specialization_quality'] for r in results])
    avg_stability = np.mean([r['stability'] for r in results])
    avg_performance = np.mean([r['final_performance'] for r in results])
    avg_rate = np.mean([r['differentiation_rate'] for r in results])

    # Weighted objective (lower is better)
    objective = (
        0.3 * (avg_speed / 500) +             # Speed (30% weight, minimize)
        0.3 * (1.0 - avg_quality) +            # Quality (30% weight, maximize)
        0.2 * (1.0 - avg_stability) +          # Stability (20% weight, maximize)
        0.1 * (-avg_performance / 10) +         # Performance (10% weight, maximize)
        0.1 * (1.0 - avg_rate)                  # Rate (10% weight, maximize)
    )

    return objective


def run_optimization(n_calls: int = 50) -> Tuple[Dict, Dict]:
    """Run Bayesian optimization to find optimal META parameters"""

    print("Starting META Tile Differentiation Parameters Optimization...")
    print(f"Running {n_calls} iterations of Bayesian optimization...")

    result = gp_minimize(
        objective,
        search_space,
        n_calls=n_calls,
        n_initial_points=15,
        random_state=42,
        verbose=True
    )

    best_params = {
        'signal_response_rate': result.x[0],
        'differentiation_threshold': result.x[1],
        'plasticity_rule': result.x[2]
    }

    print("\nOptimization complete!")
    print(f"Best parameters found:")
    print(f"  Signal response rate: {best_params['signal_response_rate']:.4f}")
    print(f"  Differentiation threshold: {best_params['differentiation_threshold']:.4f}")
    print(f"  Plasticity rule: {best_params['plasticity_rule']}")
    print(f"  Objective value: {result.fun:.6f}")

    return best_params, result


# ============================================================================
# Results Analysis and Visualization
# ============================================================================

def plot_plasticity_rule_comparison(result, output_dir: str):
    """Compare performance of different plasticity rules"""

    # Group results by plasticity rule
    from collections import defaultdict

    rule_scores = defaultdict(list)
    for params, score in zip(result.x_iters, result.func_vals):
        rule = params[2]
        rule_scores[rule].append(score)

    # Calculate statistics
    rules = sorted(rule_scores.keys())
    means = [np.mean(rule_scores[r]) for r in rules]
    stds = [np.std(rule_scores[r]) for r in rules]

    # Plot
    plt.figure(figsize=(10, 6))
    x_pos = np.arange(len(rules))
    plt.bar(x_pos, means, yerr=stds, alpha=0.7, capsize=5, color='steelblue')
    plt.xlabel('Plasticity Rule')
    plt.ylabel('Objective Value (lower is better)')
    plt.title('META Tile: Plasticity Rule Comparison')
    plt.xticks(x_pos, rules)
    plt.grid(True, alpha=0.3, axis='y')

    plt.savefig(f"{output_dir}/meta_plasticity_comparison.png",
                dpi=300, bbox_inches='tight')
    print(f"Saved plasticity comparison to {output_dir}/meta_plasticity_comparison.png")


def plot_differentiation_trajectory(best_params: Dict, output_dir: str):
    """Plot differentiation trajectory with best parameters"""

    # Run detailed simulation
    np.random.seed(42)
    n_tiles = 20
    n_episodes = 500

    tiles = [
        MetaTile(
            tile_id=i,
            signal_response_rate=best_params['signal_response_rate'],
            differentiation_threshold=best_params['differentiation_threshold'],
            plasticity_rule=best_params['plasticity_rule']
        )
        for i in range(n_tiles)
    ]

    env = TaskEnvironment(n_tasks=5)

    # Track differentiation over time
    differentiated_counts = []
    specializations = []

    for episode in range(n_episodes):
        for tile in tiles:
            signal_type, signal_strength = env.get_signal()
            tile.process_signal(signal_type, signal_strength)

        # Count differentiated tiles
        n_differentiated = sum(1 for t in tiles if t.differentiated)
        differentiated_counts.append(n_differentiated)

        # Track specializations
        specs = [t.specialization for t in tiles if t.differentiated]
        specializations.append(specs)

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Differentiation over time
    axes[0].plot(range(1, n_episodes + 1), differentiated_counts, 'b-', linewidth=2)
    axes[0].axhline(y=n_tiles, color='r', linestyle='--', label='All tiles')
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Number of Differentiated Tiles')
    axes[0].set_title('META Tile Differentiation Trajectory')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Specialization distribution at end
    final_specs = [s for s in specializations[-1] if s is not None]
    if final_specs:
        unique, counts = np.unique(final_specs, return_counts=True)
        axes[1].bar(unique, counts, alpha=0.7, color='steelblue')
        axes[1].set_xlabel('Specialization Type')
        axes[1].set_ylabel('Count')
        axes[1].set_title('Final Specialization Distribution')
        axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/meta_differentiation_trajectory.png",
                dpi=300, bbox_inches='tight')
    print(f"Saved differentiation trajectory to {output_dir}/meta_differentiation_trajectory.png")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""

    # Create results directory
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Run optimization
    best_params, result = run_optimization(n_calls=50)

    # Validate best parameters
    print("\nValidating best parameters with multiple trials...")
    validation_results = []
    for seed in range(10):
        result_dict = run_simulation(
            signal_response_rate=best_params['signal_response_rate'],
            differentiation_threshold=best_params['differentiation_threshold'],
            plasticity_rule=best_params['plasticity_rule'],
            n_tiles=20,
            n_episodes=500,
            seed=seed
        )
        validation_results.append(result_dict)

    # Calculate validation statistics
    metrics = ['differentiation_speed', 'specialization_quality', 'stability',
               'final_performance', 'differentiation_rate']
    validation_stats = {}

    for metric in metrics:
        values = [r[metric] for r in validation_results]
        validation_stats[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }

    print("\nValidation Statistics:")
    for metric, stat in validation_stats.items():
        print(f"  {metric}: {stat['mean']:.4f} (+/- {stat['std']:.4f})")

    # Generate visualizations
    plot_plasticity_rule_comparison(result, str(results_dir))
    plot_differentiation_trajectory(best_params, str(results_dir))

    # Save results to JSON
    output = {
        'best_parameters': best_params,
        'optimization_objective': float(result.fun),
        'validation_statistics': validation_stats,
        'n_iterations': len(result.x_iters),
        'timestamp': str(pd.Timestamp.now())
    }

    output_path = results_dir / 'meta_differentiation_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return best_params, validation_stats


if __name__ == '__main__':
    import pandas as pd  # For timestamp

    best_params, stats = main()
