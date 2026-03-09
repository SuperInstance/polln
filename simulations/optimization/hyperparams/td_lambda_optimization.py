"""
TD(λ) Parameter Optimization

Optimizes TD(λ) reinforcement learning parameters for the value network.
Finds optimal λ, α, and γ values for fastest convergence and best final performance.

Optimization Targets:
- λ (lambda): Eligibility trace decay [0, 1]
  - λ = 0: TD(0) - one-step lookahead
  - λ = 1: Monte Carlo - full episode return
  - Intermediate values: Balance between bias and variance

- α (alpha): Learning rate [0, 1]
  - Controls how quickly value estimates update
  - Too high: Unstable, may not converge
  - Too low: Slow convergence

- γ (gamma): Discount factor [0, 1]
  - Controls importance of future rewards
  - Closer to 1: Far-sighted (cares about distant future)
  - Closer to 0: Myopic (only cares about immediate rewards)

Metrics:
- Convergence Speed: Episodes to reach <1% value change
- Final MSE: Mean squared error of value predictions
- Stability: Variance of value estimates over last 100 episodes
"""

import numpy as np
import json
from typing import Dict, Tuple, List
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# Simulation Environment - Random Walk MDP
# ============================================================================

class RandomWalkMDP:
    """
    Classic random walk MDP for TD learning evaluation.
    States: 0, 1, 2, ..., N-1
    Terminal states: 0 and N-1
    Rewards: +1 for reaching N-1, 0 for reaching 0
    """

    def __init__(self, n_states: int = 7):
        self.n_states = n_states
        self.start_state = n_states // 2
        self.current_state = self.start_state
        self.terminal_states = [0, n_states - 1]

    def reset(self) -> int:
        """Reset to start state"""
        self.current_state = self.start_state
        return self.current_state

    def step(self) -> Tuple[int, float, bool]:
        """
        Take a random step (left or right with equal probability).

        Returns:
            next_state: Next state
            reward: Reward received
            done: Whether episode is complete
        """
        if self.current_state in self.terminal_states:
            return self.current_state, 0.0, True

        # Random step left or right
        if np.random.rand() < 0.5:
            self.current_state -= 1
        else:
            self.current_state += 1

        # Check if terminal
        done = self.current_state in self.terminal_states

        # Reward
        if self.current_state == self.n_states - 1:
            reward = 1.0
        elif self.current_state == 0:
            reward = 0.0
        else:
            reward = 0.0

        return self.current_state, reward, done

    def get_true_values(self) -> np.ndarray:
        """
        Get true state values using dynamic programming.
        For this MDP, V(s) = s / (n_states - 1)
        """
        true_values = np.zeros(self.n_states)
        for s in range(self.n_states):
            true_values[s] = s / (self.n_states - 1)
        return true_values


# ============================================================================
# TD(λ) Learning Agent
# ============================================================================

class TDLambdaAgent:
    """
    TD(λ) agent with eligibility traces.

    Uses online TD(λ) with replacing traces.
    """

    def __init__(self, n_states: int, lambda_: float, alpha: float, gamma: float):
        self.n_states = n_states
        self.lambda_ = lambda_
        self.alpha = alpha
        self.gamma = gamma

        # Value estimates
        self.values = np.zeros(n_states)

        # Eligibility traces
        self.eligibility = np.zeros(n_states)

    def get_action(self, state: int) -> int:
        """Get action (deterministic for this MDP)"""
        return 0  # Random walk takes random actions

    def update(self, state: int, reward: float, next_state: int, done: bool):
        """
        Update value estimates using TD(λ) with eligibility traces.

        V(s) <- V(s) + α * δ * e(s)

        where δ = r + γ * V(s') - V(s)
        and e(s) is eligibility trace
        """

        # TD error
        if done:
            td_error = reward - self.values[state]
        else:
            td_error = reward + self.gamma * self.values[next_state] - self.values[state]

        # Update eligibility traces (replacing traces)
        self.eligibility[state] = 1

        # Update all states
        for s in range(self.n_states):
            self.values[s] += self.alpha * td_error * self.eligibility[s]
            self.eligibility[s] *= self.gamma * self.lambda_

    def get_mse(self, true_values: np.ndarray) -> float:
        """Calculate mean squared error against true values"""
        return np.mean((self.values - true_values) ** 2)

    def get_value_variance(self, last_n: int = 100) -> float:
        """Calculate variance of value estimates (for stability metric)"""
        # For simplicity, return variance across all states
        return np.var(self.values)


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(
    lambda_: float,
    alpha: float,
    gamma: float,
    n_states: int = 7,
    n_episodes: int = 100,
    seed: int = None
) -> Dict[str, float]:
    """
    Run TD(λ) simulation with given parameters.

    Returns metrics on convergence speed, final MSE, and stability.
    """

    if seed is not None:
        np.random.seed(seed)

    # Create environment and agent
    env = RandomWalkMDP(n_states=n_states)
    agent = TDLambdaAgent(n_states, lambda_, alpha, gamma)
    true_values = env.get_true_values()

    # Track metrics
    mse_history = []
    value_changes = []

    prev_values = agent.values.copy()

    # Run episodes
    for episode in range(n_episodes):
        state = env.reset()
        done = False

        while not done:
            next_state, reward, done = env.step()
            agent.update(state, reward, next_state, done)
            state = next_state

        # Calculate MSE
        mse = agent.get_mse(true_values)
        mse_history.append(mse)

        # Track value changes for convergence detection
        value_change = np.abs(agent.values - prev_values).max()
        value_changes.append(value_change)
        prev_values = agent.values.copy()

    # Convergence speed: episodes to reach <1% value change
    convergence_threshold = 0.01
    convergence_episode = n_episodes
    for i, change in enumerate(value_changes):
        if change < convergence_threshold:
            convergence_episode = i
            break

    # Final MSE
    final_mse = mse_history[-1]

    # Stability: variance of MSE over last 20 episodes
    stability = np.std(mse_history[-20:])

    # Average MSE
    avg_mse = np.mean(mse_history)

    return {
        'convergence_speed': convergence_episode,
        'final_mse': final_mse,
        'stability': stability,
        'avg_mse': avg_mse,
        'mse_history': mse_history
    }


# ============================================================================
# Grid Search
# ============================================================================

def grid_search(
    lambda_values: List[float] = None,
    alpha_values: List[float] = None,
    gamma_values: List[float] = None
) -> Tuple[Dict, Dict]:
    """
    Perform exhaustive grid search over parameter space.

    Returns:
        best_params: Optimal parameter values
        all_results: All parameter combinations and their scores
    """

    if lambda_values is None:
        lambda_values = [0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]

    if alpha_values is None:
        alpha_values = [0.01, 0.05, 0.1, 0.2, 0.5]

    if gamma_values is None:
        gamma_values = [0.9, 0.95, 0.99, 0.999]

    print("Starting TD(λ) Grid Search...")
    print(f"λ values: {lambda_values}")
    print(f"α values: {alpha_values}")
    print(f"γ values: {gamma_values}")
    print(f"Total combinations: {len(lambda_values) * len(alpha_values) * len(gamma_values)}")

    all_results = []
    best_score = float('inf')
    best_params = None

    # Iterate over all combinations
    total_combinations = len(lambda_values) * len(alpha_values) * len(gamma_values)
    current = 0

    for lambda_ in lambda_values:
        for alpha in alpha_values:
            for gamma in gamma_values:
                current += 1
                if current % 10 == 0:
                    print(f"Progress: {current}/{total_combinations}")

                # Run simulation with 5 random seeds
                results = []
                for seed in range(5):
                    result = run_simulation(
                        lambda_=lambda_,
                        alpha=alpha,
                        gamma=gamma,
                        n_states=7,
                        n_episodes=100,
                        seed=seed
                    )
                    results.append(result)

                # Average results
                avg_convergence = np.mean([r['convergence_speed'] for r in results])
                avg_final_mse = np.mean([r['final_mse'] for r in results])
                avg_stability = np.mean([r['stability'] for r in results])

                # Weighted objective (lower is better)
                score = (
                    0.5 * (avg_convergence / 100) +  # Convergence speed (50% weight)
                    0.3 * avg_final_mse +               # Final MSE (30% weight)
                    0.2 * avg_stability                 # Stability (20% weight)
                )

                # Store results
                all_results.append({
                    'lambda': lambda_,
                    'alpha': alpha,
                    'gamma': gamma,
                    'score': score,
                    'convergence_speed': avg_convergence,
                    'final_mse': avg_final_mse,
                    'stability': avg_stability
                })

                # Track best
                if score < best_score:
                    best_score = score
                    best_params = {
                        'lambda': lambda_,
                        'alpha': alpha,
                        'gamma': gamma
                    }

    print("\nGrid search complete!")
    print(f"Best parameters found:")
    print(f"  λ (lambda): {best_params['lambda']}")
    print(f"  α (alpha): {best_params['alpha']}")
    print(f"  γ (gamma): {best_params['gamma']}")
    print(f"  Score: {best_score:.6f}")

    return best_params, {'all_results': all_results, 'best_score': best_score}


# ============================================================================
# Bayesian Optimization (Alternative to Grid Search)
# ============================================================================

# Parameter search space for Bayesian optimization
search_space = [
    Real(0.0, 0.99, name='lambda'),
    Real(0.01, 0.5, name='alpha'),
    Real(0.9, 0.999, name='gamma')
]


@use_named_args(search_space)
def objective(**params) -> float:
    """Objective function for Bayesian optimization"""

    # Run simulation with 5 different random seeds
    results = []
    for seed in range(5):
        result = run_simulation(
            lambda_=params['lambda'],
            alpha=params['alpha'],
            gamma=params['gamma'],
            n_states=7,
            n_episodes=100,
            seed=seed
        )
        results.append(result)

    # Average results
    avg_convergence = np.mean([r['convergence_speed'] for r in results])
    avg_final_mse = np.mean([r['final_mse'] for r in results])
    avg_stability = np.mean([r['stability'] for r in results])

    # Weighted objective
    objective = (
        0.5 * (avg_convergence / 100) +
        0.3 * avg_final_mse +
        0.2 * avg_stability
    )

    return objective


def run_bayesian_optimization(n_calls: int = 50) -> Tuple[Dict, Dict]:
    """Run Bayesian optimization to find optimal TD(λ) parameters"""

    print("Starting TD(λ) Bayesian Optimization...")
    print(f"Running {n_calls} iterations...")

    result = gp_minimize(
        objective,
        search_space,
        n_calls=n_calls,
        n_initial_points=15,
        random_state=42,
        verbose=True
    )

    best_params = {
        'lambda': result.x[0],
        'alpha': result.x[1],
        'gamma': result.x[2]
    }

    print("\nOptimization complete!")
    print(f"Best parameters found:")
    print(f"  λ (lambda): {best_params['lambda']:.4f}")
    print(f"  α (alpha): {best_params['alpha']:.4f}")
    print(f"  γ (gamma): {best_params['gamma']:.6f}")
    print(f"  Objective value: {result.fun:.6f}")

    return best_params, result


# ============================================================================
# Results Analysis and Visualization
# ============================================================================

def plot_parameter_heatmaps(all_results: List[Dict], output_dir: str):
    """Generate heatmaps showing performance across parameter space"""

    # Convert to DataFrame for easier manipulation
    import pandas as pd

    df = pd.DataFrame(all_results)

    # Create heatmaps for each pair of parameters
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Lambda vs Alpha (averaged over gamma)
    pivot_la = df.pivot_table(values='score', index='lambda', columns='alpha', aggfunc='mean')
    im1 = axes[0].imshow(pivot_la.values, aspect='auto', cmap='viridis_r', origin='lower')
    axes[0].set_xticks(range(len(pivot_la.columns)))
    axes[0].set_xticklabels([f"{x:.2f}" for x in pivot_la.columns])
    axes[0].set_yticks(range(len(pivot_la.index)))
    axes[0].set_yticklabels([f"{x:.2f}" for x in pivot_la.index])
    axes[0].set_xlabel('α (alpha)')
    axes[0].set_ylabel('λ (lambda)')
    axes[0].set_title('λ vs α (lower is better)')
    plt.colorbar(im1, ax=axes[0])

    # Lambda vs Gamma (averaged over alpha)
    pivot_lg = df.pivot_table(values='score', index='lambda', columns='gamma', aggfunc='mean')
    im2 = axes[1].imshow(pivot_lg.values, aspect='auto', cmap='viridis_r', origin='lower')
    axes[1].set_xticks(range(len(pivot_lg.columns)))
    axes[1].set_xticklabels([f"{x:.3f}" for x in pivot_lg.columns])
    axes[1].set_yticks(range(len(pivot_lg.index)))
    axes[1].set_yticklabels([f"{x:.2f}" for x in pivot_lg.index])
    axes[1].set_xlabel('γ (gamma)')
    axes[1].set_ylabel('λ (lambda)')
    axes[1].set_title('λ vs γ (lower is better)')
    plt.colorbar(im2, ax=axes[1])

    # Alpha vs Gamma (averaged over lambda)
    pivot_ag = df.pivot_table(values='score', index='alpha', columns='gamma', aggfunc='mean')
    im3 = axes[2].imshow(pivot_ag.values, aspect='auto', cmap='viridis_r', origin='lower')
    axes[2].set_xticks(range(len(pivot_ag.columns)))
    axes[2].set_xticklabels([f"{x:.3f}" for x in pivot_ag.columns])
    axes[2].set_yticks(range(len(pivot_ag.index)))
    axes[2].set_yticklabels([f"{x:.2f}" for x in pivot_ag.index])
    axes[2].set_xlabel('γ (gamma)')
    axes[2].set_ylabel('α (alpha)')
    axes[2].set_title('α vs γ (lower is better)')
    plt.colorbar(im3, ax=axes[2])

    plt.tight_layout()
    plt.savefig(f"{output_dir}/td_lambda_heatmaps.png", dpi=300, bbox_inches='tight')
    print(f"Saved heatmaps to {output_dir}/td_lambda_heatmaps.png")


def plot_learning_curves(best_params: Dict, output_dir: str):
    """Plot learning curves for best parameters"""

    # Run simulation to get MSE history
    result = run_simulation(
        lambda_=best_params['lambda'],
        alpha=best_params['alpha'],
        gamma=best_params['gamma'],
        n_states=7,
        n_episodes=100,
        seed=42
    )

    plt.figure(figsize=(10, 6))
    plt.plot(result['mse_history'], 'b-', linewidth=2)
    plt.xlabel('Episode')
    plt.ylabel('Mean Squared Error')
    plt.title(f'TD(λ) Learning Curve\n'
              f'λ={best_params["lambda"]:.2f}, α={best_params["alpha"]:.2f}, γ={best_params["gamma"]:.3f}')
    plt.grid(True, alpha=0.3)

    plt.savefig(f"{output_dir}/td_lambda_learning_curve.png", dpi=300, bbox_inches='tight')
    print(f"Saved learning curve to {output_dir}/td_lambda_learning_curve.png")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""

    # Create results directory
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Run grid search
    best_params, grid_results = grid_search()

    # Alternatively, run Bayesian optimization
    # best_params, bayes_result = run_bayesian_optimization(n_calls=50)

    # Validate best parameters with more trials
    print("\nValidating best parameters...")
    validation_results = []
    for seed in range(20):
        result = run_simulation(
            lambda_=best_params['lambda'],
            alpha=best_params['alpha'],
            gamma=best_params['gamma'],
            n_states=7,
            n_episodes=100,
            seed=seed
        )
        validation_results.append(result)

    # Calculate validation statistics
    metrics = ['convergence_speed', 'final_mse', 'stability', 'avg_mse']
    validation_stats = {}

    for metric in metrics:
        values = [r[metric] for r in validation_results]
        validation_stats[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }

    # Generate visualizations
    plot_parameter_heatmaps(grid_results['all_results'], str(results_dir))
    plot_learning_curves(best_params, str(results_dir))

    # Save results to JSON
    output = {
        'best_parameters': best_params,
        'grid_search_score': float(grid_results['best_score']),
        'validation_statistics': validation_stats,
        'all_results': grid_results['all_results']
    }

    output_path = results_dir / 'td_lambda_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return best_params, validation_stats


if __name__ == '__main__':
    best_params, stats = main()
