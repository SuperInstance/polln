"""
Plinko Temperature Schedule Optimization

Optimizes temperature annealing schedules for the Plinko stochastic selection layer.
Finds optimal initial temperature, decay rate, and schedule type for best exploration-exploitation balance.

Optimization Targets:
- Initial temperature: Controls exploration range
- Decay rate: How fast temperature decreases
- Minimum temperature: Floor for exploitation
- Schedule type: How temperature changes over time (constant, linear, exponential, cyclical)

Metrics:
- Convergence speed: Episodes to reach 90% optimal performance
- Final performance: Average reward at convergence
- Exploration efficiency: Unique states visited per episode
"""

import numpy as np
import json
from typing import Dict, Tuple, Callable
from skopt import gp_minimize
from skopt.space import Real, Categorical
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# Simulation Environment - Multi-Armed Bandit with Non-Stationary Rewards
# ============================================================================

class NonStationaryBandit:
    """
    Simulates a non-stationary multi-armed bandit environment
    to test Plinko temperature schedules.
    """

    def __init__(self, n_arms: int = 10, change_rate: float = 0.01):
        self.n_arms = n_arms
        self.change_rate = change_rate
        self.true_values = np.random.randn(n_arms)
        self.optimal_arm = np.argmax(self.true_values)

    def pull(self, arm: int) -> float:
        """Pull an arm and return reward"""
        # Non-stationary: values drift over time
        self.true_values += np.random.randn(self.n_arms) * self.change_rate
        self.optimal_arm = np.argmax(self.true_values)

        reward = self.true_values[arm] + np.random.randn() * 0.1
        return reward

    def get_optimal_reward(self) -> float:
        """Get reward of optimal arm"""
        return self.true_values[self.optimal_arm]


# ============================================================================
# Temperature Schedules
# ============================================================================

class TemperatureSchedule:
    """Base class for temperature schedules"""

    def get_temperature(self, episode: int, max_episodes: int) -> float:
        raise NotImplementedError


class ConstantSchedule(TemperatureSchedule):
    """Constant temperature (no annealing)"""

    def __init__(self, temperature: float):
        self.temperature = temperature

    def get_temperature(self, episode: int, max_episodes: int) -> float:
        return self.temperature


class LinearDecaySchedule(TemperatureSchedule):
    """Linear temperature decay"""

    def __init__(self, initial_temp: float, min_temp: float):
        self.initial_temp = initial_temp
        self.min_temp = min_temp

    def get_temperature(self, episode: int, max_episodes: int) -> float:
        progress = episode / max_episodes
        temp = self.initial_temp - (self.initial_temp - self.min_temp) * progress
        return max(temp, self.min_temp)


class ExponentialDecaySchedule(TemperatureSchedule):
    """Exponential temperature decay"""

    def __init__(self, initial_temp: float, decay_rate: float, min_temp: float):
        self.initial_temp = initial_temp
        self.decay_rate = decay_rate
        self.min_temp = min_temp

    def get_temperature(self, episode: int, max_episodes: int) -> float:
        temp = self.initial_temp * (self.decay_rate ** episode)
        return max(temp, self.min_temp)


class CyclicalSchedule(TemperatureSchedule):
    """Cyclical temperature with periodic exploration bursts"""

    def __init__(self, initial_temp: float, min_temp: float, cycle_length: int):
        self.initial_temp = initial_temp
        self.min_temp = min_temp
        self.cycle_length = cycle_length

    def get_temperature(self, episode: int, max_episodes: int) -> float:
        cycle_pos = (episode % self.cycle_length) / self.cycle_length
        # Sine wave between min_temp and initial_temp
        amplitude = (self.initial_temp - self.min_temp) / 2
        base = (self.initial_temp + self.min_temp) / 2
        temp = base + amplitude * np.sin(2 * np.pi * cycle_pos)
        return temp


# ============================================================================
# Plinko Selection Layer
# ============================================================================

class PlinkoLayer:
    """
    Simulates Plinko stochastic selection with temperature-controlled exploration.
    """

    def __init__(self, n_arms: int):
        self.n_arms = n_arms
        self.value_estimates = np.zeros(n_arms)
        self.pull_counts = np.zeros(n_arms)

    def select_arm(self, temperature: float) -> int:
        """
        Select arm using Plinko stochastic selection.
        Higher temperature = more exploration.
        """
        # Boltzmann distribution with temperature
        exp_values = np.exp(self.value_estimates / temperature)
        probabilities = exp_values / np.sum(exp_values)

        # Sample from distribution
        return np.random.choice(self.n_arms, p=probabilities)

    def update(self, arm: int, reward: float, alpha: float = 0.1):
        """Update value estimate using incremental average"""
        self.pull_counts[arm] += 1
        self.value_estimates[arm] += alpha * (reward - self.value_estimates[arm])


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(
    schedule_type: str,
    initial_temp: float,
    decay_rate: float,
    min_temp: float,
    n_arms: int = 10,
    n_episodes: int = 1000,
    seed: int = None
) -> Dict[str, float]:
    """
    Run a Plinko simulation with given parameters.

    Returns metrics on convergence speed, final performance, and exploration.
    """

    if seed is not None:
        np.random.seed(seed)

    # Create environment
    env = NonStationaryBandit(n_arms=n_arms, change_rate=0.01)

    # Create schedule
    if schedule_type == 'constant':
        schedule = ConstantSchedule(initial_temp)
    elif schedule_type == 'linear':
        schedule = LinearDecaySchedule(initial_temp, min_temp)
    elif schedule_type == 'exponential':
        schedule = ExponentialDecaySchedule(initial_temp, decay_rate, min_temp)
    elif schedule_type == 'cyclical':
        schedule = CyclicalSchedule(initial_temp, min_temp, cycle_length=100)
    else:
        raise ValueError(f"Unknown schedule type: {schedule_type}")

    # Create Plinko layer
    plinko = PlinkoLayer(n_arms=n_arms)

    # Track metrics
    rewards = []
    optimal_rewards = []
    unique_arms_pulled = set()

    # Run episodes
    for episode in range(n_episodes):
        # Get temperature
        temp = schedule.get_temperature(episode, n_episodes)

        # Select and pull arm
        arm = plinko.select_arm(temp)
        reward = env.pull(arm)
        optimal_reward = env.get_optimal_reward()

        # Update value estimate
        plinko.update(arm, reward)

        # Track metrics
        rewards.append(reward)
        optimal_rewards.append(optimal_reward)
        unique_arms_pulled.add(arm)

    # Calculate metrics
    rewards = np.array(rewards)
    optimal_rewards = np.array(optimal_rewards)

    # Convergence speed: episodes to reach 90% of optimal performance
    regret = optimal_rewards - rewards
    cumulative_regret = np.cumsum(regret)
    target_regret = 0.1 * np.sum(optimal_rewards)  # 10% total regret

    convergence_episode = n_episodes
    for i in range(len(cumulative_regret)):
        if cumulative_regret[i] <= target_regret:
            convergence_episode = i
            break

    # Final performance: average reward over last 100 episodes
    final_performance = np.mean(rewards[-100:])

    # Exploration efficiency: unique arms per episode
    exploration_efficiency = len(unique_arms_pulled) / n_arms

    return {
        'convergence_speed': convergence_episode,
        'final_performance': final_performance,
        'exploration_efficiency': exploration_efficiency,
        'total_regret': np.sum(regret)
    }


# ============================================================================
# Bayesian Optimization
# ============================================================================

# Parameter search space
search_space = [
    Categorical(['constant', 'linear', 'exponential', 'cyclical'], name='schedule_type'),
    Real(1.0, 5.0, name='initial_temp'),
    Real(0.990, 0.999, name='decay_rate'),
    Real(0.01, 0.5, name='min_temp')
]


@use_named_args(search_space)
def objective(**params) -> float:
    """
    Objective function for Bayesian optimization.
    Minimizes a weighted combination of metrics.
    """
    # Run simulation with 5 different random seeds for robustness
    results = []
    for seed in range(5):
        result = run_simulation(
            schedule_type=params['schedule_type'],
            initial_temp=params['initial_temp'],
            decay_rate=params['decay_rate'],
            min_temp=params['min_temp'],
            n_arms=10,
            n_episodes=1000,
            seed=seed
        )
        results.append(result)

    # Average results across seeds
    avg_convergence = np.mean([r['convergence_speed'] for r in results])
    avg_final_perf = np.mean([r['final_performance'] for r in results])
    avg_exploration = np.mean([r['exploration_efficiency'] for r in results])
    avg_regret = np.mean([r['total_regret'] for r in results])

    # Weighted objective (lower is better)
    # Normalize each metric to [0, 1] range roughly
    objective = (
        0.4 * (avg_convergence / 1000) +  # Convergence speed (40% weight)
        0.3 * (1.0 - avg_final_perf) +      # Final performance (30% weight)
        0.2 * (1.0 - avg_exploration) +    # Exploration efficiency (20% weight)
        0.1 * (avg_regret / 1000)           # Total regret (10% weight)
    )

    return objective


def run_optimization(n_calls: int = 100) -> Tuple[Dict, Dict]:
    """
    Run Bayesian optimization to find optimal temperature schedule.

    Returns:
        best_params: Optimal parameter values
        optimization_result: Full optimization results from skopt
    """

    print("Starting Plinko Temperature Schedule Optimization...")
    print(f"Running {n_calls} iterations of Bayesian optimization...")

    # Run Bayesian optimization
    result = gp_minimize(
        objective,
        search_space,
        n_calls=n_calls,
        n_initial_points=20,
        random_state=42,
        verbose=True
    )

    # Extract best parameters
    best_params = {
        'schedule_type': result.x[0],
        'initial_temp': result.x[1],
        'decay_rate': result.x[2],
        'min_temp': result.x[3]
    }

    print("\nOptimization complete!")
    print(f"Best parameters found:")
    print(f"  Schedule type: {best_params['schedule_type']}")
    print(f"  Initial temperature: {best_params['initial_temp']:.4f}")
    print(f"  Decay rate: {best_params['decay_rate']:.6f}")
    print(f"  Minimum temperature: {best_params['min_temp']:.4f}")
    print(f"  Objective value: {result.fun:.4f}")

    return best_params, result


# ============================================================================
# Results Analysis and Visualization
# ============================================================================

def plot_optimization_convergence(result, output_path: str = None):
    """Plot optimization convergence over iterations"""

    plt.figure(figsize=(10, 6))
    plt.plot(result.func_vals, 'b-', alpha=0.6, label='Objective value')
    plt.plot(np.minimum.accumulate(result.func_vals), 'r-', linewidth=2,
             label='Best objective')

    plt.xlabel('Iteration')
    plt.ylabel('Objective Value (lower is better)')
    plt.title('Plinko Temperature Optimization Convergence')
    plt.legend()
    plt.grid(True, alpha=0.3)

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved convergence plot to {output_path}")
    else:
        plt.show()


def plot_parameter_sensitivity(result, output_path: str = None):
    """Plot parameter importance/convergence"""

    dimensions = result.space.dimensions
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    param_names = ['Schedule Type', 'Initial Temp', 'Decay Rate', 'Min Temp']

    for i, (ax, dim, name) in enumerate(zip(axes, dimensions, param_names)):
        # Plot parameter values over iterations
        values = [x[i] for x in result.x_iters]
        ax.plot(values, 'o-', alpha=0.6, markersize=4)
        ax.set_xlabel('Iteration')
        ax.set_ylabel(name)
        ax.set_title(f'{name} over iterations')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved sensitivity plot to {output_path}")
    else:
        plt.show()


def validate_best_parameters(best_params: Dict, n_trials: int = 10) -> Dict:
    """
    Validate best parameters with multiple trials.

    Returns statistics on performance metrics.
    """

    print("\nValidating best parameters with multiple trials...")

    results = []
    for seed in range(n_trials):
        result = run_simulation(
            schedule_type=best_params['schedule_type'],
            initial_temp=best_params['initial_temp'],
            decay_rate=best_params['decay_rate'],
            min_temp=best_params['min_temp'],
            n_arms=10,
            n_episodes=1000,
            seed=seed
        )
        results.append(result)

    # Calculate statistics
    metrics = ['convergence_speed', 'final_performance',
               'exploration_efficiency', 'total_regret']
    stats = {}

    for metric in metrics:
        values = [r[metric] for r in results]
        stats[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values))
        }

    print("\nValidation Statistics:")
    for metric, stat in stats.items():
        print(f"  {metric}: {stat['mean']:.4f} (+/- {stat['std']:.4f})")

    return stats


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""

    # Create results directory
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Run optimization
    best_params, result = run_optimization(n_calls=100)

    # Validate best parameters
    validation_stats = validate_best_parameters(best_params, n_trials=20)

    # Generate plots
    plot_optimization_convergence(
        result,
        output_path=str(results_dir / 'plinko_convergence.png')
    )
    plot_parameter_sensitivity(
        result,
        output_path=str(results_dir / 'plinko_sensitivity.png')
    )

    # Save results to JSON
    output = {
        'best_parameters': best_params,
        'optimization_objective': float(result.fun),
        'validation_statistics': validation_stats,
        'n_iterations': len(result.x_iters),
        'timestamp': str(pd.Timestamp.now())
    }

    output_path = results_dir / 'plinko_temperature_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return best_params, validation_stats


if __name__ == '__main__':
    import pandas as pd  # For timestamp

    best_params, stats = main()
