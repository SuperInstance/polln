"""
Exploration Schedule Optimization
==================================
Discovers optimal exploration-exploitation schedules for Plinko stochastic selection.

Schedules to Test:
1. Epsilon-greedy: Constant epsilon
2. Epsilon-greedy: Linear decay
3. Epsilon-greedy: Exponential decay
4. Epsilon-greedy: Inverse time decay
5. Boltzmann/Softmax: Constant temperature
6. Boltzmann: Exponential temperature decay
7. Boltzmann: Cosine temperature annealing
8. UCB (Upper Confidence Bound)
9. Thompson Sampling
10. Adaptive (based on value variance)

Goal: Find optimal exploration trajectory that balances:
- Early exploration of diverse strategies
- Mid-stage refinement of promising options
- Late-stage exploitation of best policies

Output: Optimal temperature/epsilon schedule for Plinko decision layer
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import json
from enum import Enum
import seaborn as sns

sns.set_style("whitegrid")


class ExplorationStrategy(Enum):
    """Types of exploration strategies"""
    EPSILON_GREEDY = "epsilon_greedy"
    BOLTZMANN = "boltzmann"
    UCB = "ucb"
    THOMPSON_SAMPLING = "thompson_sampling"


@dataclass
class ExplorationResult:
    """Results from testing an exploration schedule"""
    strategy: str
    schedule_name: str
    final_reward: float
    cumulative_reward: float
    regret: float
    best_action_percentage: float
    diversity_score: float
    convergence_speed: int
    schedule_params: Dict


class ExplorationSchedules:
    """Various exploration schedule implementations"""

    @staticmethod
    def epsilon_constant(epsilon: float, total_steps: int) -> np.ndarray:
        """Constant epsilon"""
        return np.full(total_steps, epsilon)

    @staticmethod
    def epsilon_linear(initial_epsilon: float, total_steps: int,
                       min_epsilon: float = 0.01) -> np.ndarray:
        """Linear decay from initial to min"""
        return np.linspace(initial_epsilon, min_epsilon, total_steps)

    @staticmethod
    def epsilon_exponential(initial_epsilon: float, total_steps: int,
                            min_epsilon: float = 0.01,
                            decay_rate: float = 0.995) -> np.ndarray:
        """Exponential decay"""
        steps = np.arange(total_steps)
        epsilon = initial_epsilon * (decay_rate ** steps)
        return np.maximum(epsilon, min_epsilon)

    @staticmethod
    def epsilon_inverse(initial_epsilon: float, total_steps: int,
                        min_epsilon: float = 0.01,
                        decay_scale: float = 100.0) -> np.ndarray:
        """1 / (1 + t/scale) decay"""
        steps = np.arange(total_steps)
        epsilon = initial_epsilon / (1 + steps / decay_scale)
        return np.maximum(epsilon, min_epsilon)

    @staticmethod
    def temperature_constant(temperature: float, total_steps: int) -> np.ndarray:
        """Constant temperature for Boltzmann"""
        return np.full(total_steps, temperature)

    @staticmethod
    def temperature_exponential(initial_temp: float, total_steps: int,
                                 min_temp: float = 0.1,
                                 decay_rate: float = 0.995) -> np.ndarray:
        """Exponential decay for temperature"""
        steps = np.arange(total_steps)
        temp = initial_temp * (decay_rate ** steps)
        return np.maximum(temp, min_temp)

    @staticmethod
    def temperature_cosine(initial_temp: float, total_steps: int,
                           min_temp: float = 0.1) -> np.ndarray:
        """Cosine annealing for temperature"""
        steps = np.arange(total_steps)
        return min_temp + 0.5 * (initial_temp - min_temp) * \
               (1 + np.cos(np.pi * steps / total_steps))

    @staticmethod
    def temperature_adaptive(initial_temp: float, total_steps: int,
                             window_size: int = 100,
                             min_temp: float = 0.1,
                             max_temp: float = 5.0) -> np.ndarray:
        """Adaptive temperature based on reward variance"""
        temp_schedule = np.zeros(total_steps)
        current_temp = initial_temp

        # Simulated reward variance (high early, low late)
        reward_variance = 2.0 * np.exp(-np.arange(total_steps) / 300) + 0.3

        for step in range(total_steps):
            if step > window_size:
                recent_var = np.mean(reward_variance[max(0, step-window_size):step])

                # Adjust temperature based on variance
                if recent_var > 1.0:  # High variance -> increase exploration
                    current_temp = min(max_temp, current_temp * 1.02)
                elif recent_var < 0.5:  # Low variance -> decrease exploration
                    current_temp = max(min_temp, current_temp * 0.98)

            temp_schedule[step] = current_temp

        return temp_schedule


class PlinkoSelector:
    """Plinko stochastic selection mechanism"""

    @staticmethod
    def epsilon_greedy_select(q_values: np.ndarray, epsilon: float) -> int:
        """Epsilon-greedy selection"""
        if np.random.random() < epsilon:
            return np.random.randint(len(q_values))
        else:
            # Sample from max-valued actions (ties broken randomly)
            max_q = np.max(q_values)
            max_indices = np.where(np.abs(q_values - max_q) < 1e-8)[0]
            return np.random.choice(max_indices)

    @staticmethod
    def boltzmann_select(q_values: np.ndarray, temperature: float) -> int:
        """Boltzmann/softmax selection"""
        # Subtract max for numerical stability
        q_exp = np.exp((q_values - np.max(q_values)) / max(temperature, 0.001))
        probs = q_exp / np.sum(q_exp)

        # Sample from probability distribution
        return np.random.choice(len(q_values), p=probs)

    @staticmethod
    def ucb_select(q_values: np.ndarray, counts: np.ndarray,
                   t: int, c: float = 2.0) -> int:
        """Upper Confidence Bound selection"""
        # Avoid division by zero
        counts = np.maximum(counts, 1)

        ucb_values = q_values + c * np.sqrt(np.log(t) / counts)
        return np.argmax(ucb_values)

    @staticmethod
    def thompson_sampling_select(q_mean: np.ndarray, q_var: np.ndarray) -> int:
        """Thompson sampling from Gaussian posterior"""
        samples = np.random.normal(q_mean, np.sqrt(np.maximum(q_var, 0.001)))
        return np.argmax(samples)


class MultiArmedBandit:
    """Multi-armed bandit environment for testing exploration"""

    def __init__(self, num_arms: int = 10, reward_variance: float = 1.0, seed: int = 42):
        np.random.seed(seed)
        self.num_arms = num_arms

        # True mean rewards (sampled from normal)
        self.true_means = np.random.randn(num_arms)

        # Reward variance
        self.reward_variance = reward_variance

        # Best arm
        self.best_arm = np.argmax(self.true_means)

    def pull(self, arm: int) -> float:
        """Pull an arm and get reward"""
        reward = np.random.normal(self.true_means[arm], np.sqrt(self.reward_variance))
        return reward

    def get_optimal_reward(self) -> float:
        """Get expected reward from best arm"""
        return self.true_means[self.best_arm]


class NonStationaryBandit:
    """Non-stationary bandit where rewards change over time"""

    def __init__(self, num_arms: int = 10, change_frequency: int = 500,
                 change_magnitude: float = 0.5, seed: int = 42):
        np.random.seed(seed)
        self.num_arms = num_arms
        self.change_frequency = change_frequency
        self.change_magnitude = change_magnitude
        self.step_count = 0

        # Initial true means
        self.true_means = np.random.randn(num_arms)

        # Track changes
        self.change_history = []

    def pull(self, arm: int) -> float:
        """Pull an arm and get reward (with potential environment change)"""
        # Check if environment should change
        if self.step_count > 0 and self.step_count % self.change_frequency == 0:
            # Add random perturbation to all arms
            perturbation = np.random.randn(self.num_arms) * self.change_magnitude
            self.true_means += perturbation

            # Track change
            self.change_history.append({
                'step': self.step_count,
                'new_means': self.true_means.copy()
            })

        self.step_count += 1
        reward = np.random.normal(self.true_means[arm], 1.0)
        return reward

    def get_optimal_reward(self) -> float:
        """Get expected reward from current best arm"""
        return np.max(self.true_means)


class ExplorationSimulator:
    """Simulates exploration strategies on bandit tasks"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def simulate_epsilon_greedy(self, schedule: np.ndarray,
                                 bandit: MultiArmedBandit) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simulate epsilon-greedy strategy"""
        num_steps = len(schedule)
        num_arms = bandit.num_arms

        q_values = np.zeros(num_arms)
        counts = np.zeros(num_arms)

        rewards = np.zeros(num_steps)
        regrets = np.zeros(num_steps)
        actions = np.zeros(num_steps, dtype=int)

        for step in range(num_steps):
            epsilon = schedule[step]
            arm = PlinkoSelector.epsilon_greedy_select(q_values, epsilon)

            reward = bandit.pull(arm)
            optimal_reward = bandit.get_optimal_reward()

            # Update Q-values (sample average)
            counts[arm] += 1
            q_values[arm] += (reward - q_values[arm]) / counts[arm]

            rewards[step] = reward
            regrets[step] = optimal_reward - reward
            actions[step] = arm

        return rewards, regrets, actions

    def simulate_boltzmann(self, schedule: np.ndarray,
                           bandit: MultiArmedBandit) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simulate Boltzmann/softmax strategy"""
        num_steps = len(schedule)
        num_arms = bandit.num_arms

        q_values = np.zeros(num_arms)
        counts = np.zeros(num_arms)

        rewards = np.zeros(num_steps)
        regrets = np.zeros(num_steps)
        actions = np.zeros(num_steps, dtype=int)

        for step in range(num_steps):
            temperature = schedule[step]
            arm = PlinkoSelector.boltzmann_select(q_values, temperature)

            reward = bandit.pull(arm)
            optimal_reward = bandit.get_optimal_reward()

            # Update Q-values
            counts[arm] += 1
            q_values[arm] += (reward - q_values[arm]) / counts[arm]

            rewards[step] = reward
            regrets[step] = optimal_reward - reward
            actions[step] = arm

        return rewards, regrets, actions

    def simulate_ucb(self, bandit: MultiArmedBandit,
                     c: float = 2.0,
                     num_steps: int = 1000) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simulate UCB strategy"""
        num_arms = bandit.num_arms

        q_values = np.zeros(num_arms)
        counts = np.zeros(num_arms)

        rewards = np.zeros(num_steps)
        regrets = np.zeros(num_steps)
        actions = np.zeros(num_steps, dtype=int)

        # Initialize each arm once
        for arm in range(num_arms):
            reward = bandit.pull(arm)
            counts[arm] += 1
            q_values[arm] = reward
            rewards[arm] = reward
            regrets[arm] = bandit.get_optimal_reward() - reward
            actions[arm] = arm

        # UCB selection
        for step in range(num_arms, num_steps):
            arm = PlinkoSelector.ucb_select(q_values, counts, step + 1, c)

            reward = bandit.pull(arm)
            optimal_reward = bandit.get_optimal_reward()

            counts[arm] += 1
            q_values[arm] += (reward - q_values[arm]) / counts[arm]

            rewards[step] = reward
            regrets[step] = optimal_reward - reward
            actions[step] = arm

        return rewards, regrets, actions

    def simulate_thompson_sampling(self, bandit: MultiArmedBandit,
                                    num_steps: int = 1000,
                                    prior_variance: float = 1.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simulate Thompson sampling strategy"""
        num_arms = bandit.num_arms

        q_mean = np.zeros(num_arms)
        q_var = np.full(num_arms, prior_variance)
        counts = np.zeros(num_arms)

        rewards = np.zeros(num_steps)
        regrets = np.zeros(num_steps)
        actions = np.zeros(num_steps, dtype=int)

        for step in range(num_steps):
            arm = PlinkoSelector.thompson_sampling_select(q_mean, q_var)

            reward = bandit.pull(arm)
            optimal_reward = bandit.get_optimal_reward()

            # Update posterior
            counts[arm] += 1
            q_mean[arm] += (reward - q_mean[arm]) / counts[arm]
            q_var[arm] = q_var[arm] / (counts[arm] + 1)

            rewards[step] = reward
            regrets[step] = optimal_reward - reward
            actions[step] = arm

        return rewards, regrets, actions


class ScheduleOptimizer:
    """Optimizes exploration schedules"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.simulator = ExplorationSimulator()
        self.schedules = ExplorationSchedules()

    def calculate_metrics(self, rewards: np.ndarray, regrets: np.ndarray,
                          actions: np.ndarray, num_arms: int) -> Dict:
        """Calculate performance metrics"""
        # Final reward (average of last 100 steps)
        final_reward = np.mean(rewards[-100:])

        # Cumulative reward
        cumulative_reward = np.sum(rewards)

        # Total regret
        total_regret = np.sum(regrets)

        # Best action percentage (last 100 steps)
        unique_actions, counts = np.unique(actions[-100:], return_counts=True)
        best_action_pct = np.max(counts) / 100.0

        # Diversity: entropy of action distribution (last 500 steps)
        if len(actions) >= 500:
            action_dist = np.bincount(actions[-500:], minlength=num_arms) / 500.0
            action_dist = action_dist[action_dist > 0]
            diversity = -np.sum(action_dist * np.log(action_dist))
        else:
            diversity = 0.0

        # Convergence speed: when cumulative regret growth slows
        cumulative_regret = np.cumsum(regrets)
        regret_growth = np.diff(cumulative_regret)
        window = 50
        if len(regret_growth) > window:
            smoothed_growth = np.convolve(regret_growth, np.ones(window)/window, mode='valid')
            convergence_idx = np.where(smoothed_growth < 0.1)[0]
            convergence_speed = convergence_idx[0] if len(convergence_idx) > 0 else len(regrets)
        else:
            convergence_speed = len(regrets)

        return {
            'final_reward': final_reward,
            'cumulative_reward': cumulative_reward,
            'total_regret': total_regret,
            'best_action_percentage': best_action_pct,
            'diversity_score': diversity,
            'convergence_speed': convergence_speed
        }

    def test_epsilon_schedule(self, schedule_name: str, params: Dict,
                              num_steps: int = 1000, num_runs: int = 10) -> ExplorationResult:
        """Test an epsilon-greedy schedule"""
        schedule_func = getattr(self.schedules, schedule_name)
        schedule = schedule_func(**params, total_steps=num_steps)

        all_metrics = []

        for run in range(num_runs):
            bandit = MultiArmedBandit(num_arms=10, seed=42 + run)
            rewards, regrets, actions = self.simulator.simulate_epsilon_greedy(schedule, bandit)
            metrics = self.calculate_metrics(rewards, regrets, actions, bandit.num_arms)
            all_metrics.append(metrics)

        # Average metrics across runs
        avg_metrics = {
            k: np.mean([m[k] for m in all_metrics])
            for k in all_metrics[0].keys()
        }

        return ExplorationResult(
            strategy="epsilon_greedy",
            schedule_name=schedule_name,
            final_reward=avg_metrics['final_reward'],
            cumulative_reward=avg_metrics['cumulative_reward'],
            regret=avg_metrics['total_regret'],
            best_action_percentage=avg_metrics['best_action_percentage'],
            diversity_score=avg_metrics['diversity_score'],
            convergence_speed=int(avg_metrics['convergence_speed']),
            schedule_params=params
        )

    def test_boltzmann_schedule(self, schedule_name: str, params: Dict,
                                 num_steps: int = 1000, num_runs: int = 10) -> ExplorationResult:
        """Test a Boltzmann schedule"""
        schedule_func = getattr(self.schedules, schedule_name)
        schedule = schedule_func(**params, total_steps=num_steps)

        all_metrics = []

        for run in range(num_runs):
            bandit = MultiArmedBandit(num_arms=10, seed=42 + run)
            rewards, regrets, actions = self.simulator.simulate_boltzmann(schedule, bandit)
            metrics = self.calculate_metrics(rewards, regrets, actions, bandit.num_arms)
            all_metrics.append(metrics)

        avg_metrics = {
            k: np.mean([m[k] for m in all_metrics])
            for k in all_metrics[0].keys()
        }

        return ExplorationResult(
            strategy="boltzmann",
            schedule_name=schedule_name,
            final_reward=avg_metrics['final_reward'],
            cumulative_reward=avg_metrics['cumulative_reward'],
            regret=avg_metrics['total_regret'],
            best_action_percentage=avg_metrics['best_action_percentage'],
            diversity_score=avg_metrics['diversity_score'],
            convergence_speed=int(avg_metrics['convergence_speed']),
            schedule_params=params
        )

    def optimize_exploration(self, num_steps: int = 1000) -> List[ExplorationResult]:
        """Find optimal exploration schedule"""
        print(f"\n{'='*60}")
        print("EXPLORATION SCHEDULE OPTIMIZATION")
        print(f"{'='*60}\n")

        results = []

        # Test epsilon-greedy schedules
        print("Testing Epsilon-Greedy Schedules...")
        epsilon_configs = [
            ("epsilon_constant", {"epsilon": 0.1}),
            ("epsilon_constant", {"epsilon": 0.2}),
            ("epsilon_linear", {"initial_epsilon": 0.5, "min_epsilon": 0.01}),
            ("epsilon_linear", {"initial_epsilon": 0.8, "min_epsilon": 0.05}),
            ("epsilon_exponential", {"initial_epsilon": 0.5, "min_epsilon": 0.01, "decay_rate": 0.995}),
            ("epsilon_exponential", {"initial_epsilon": 0.8, "min_epsilon": 0.05, "decay_rate": 0.998}),
            ("epsilon_inverse", {"initial_epsilon": 0.5, "min_epsilon": 0.01, "decay_scale": 100.0}),
            ("epsilon_inverse", {"initial_epsilon": 0.8, "min_epsilon": 0.05, "decay_scale": 200.0}),
        ]

        for schedule_name, params in epsilon_configs:
            result = self.test_epsilon_schedule(schedule_name, params, num_steps)
            results.append(result)
            print(f"  {schedule_name}: Final Reward = {result.final_reward:.4f}, Regret = {result.regret:.2f}")

        # Test Boltzmann schedules
        print("\nTesting Boltzmann Schedules...")
        boltzmann_configs = [
            ("temperature_constant", {"temperature": 0.5}),
            ("temperature_constant", {"temperature": 1.0}),
            ("temperature_exponential", {"initial_temp": 2.5, "min_temp": 0.1, "decay_rate": 0.995}),
            ("temperature_exponential", {"initial_temp": 3.0, "min_temp": 0.2, "decay_rate": 0.998}),
            ("temperature_cosine", {"initial_temp": 2.5, "min_temp": 0.1}),
            ("temperature_cosine", {"initial_temp": 3.0, "min_temp": 0.2}),
            ("temperature_adaptive", {"initial_temp": 2.5, "min_temp": 0.1, "window_size": 100}),
        ]

        for schedule_name, params in boltzmann_configs:
            result = self.test_boltzmann_schedule(schedule_name, params, num_steps)
            results.append(result)
            print(f"  {schedule_name}: Final Reward = {result.final_reward:.4f}, Regret = {result.regret:.2f}")

        # Test UCB
        print("\nTesting UCB...")
        for run in range(10):
            bandit = MultiArmedBandit(num_arms=10, seed=42 + run)
            rewards, regrets, actions = self.simulator.simulate_ucb(bandit, num_steps=num_steps)
            metrics = self.calculate_metrics(rewards, regrets, actions, bandit.num_arms)

        # Average across runs
        avg_metrics = {
            'final_reward': np.mean([metrics['final_reward']]),
            'cumulative_reward': np.mean([metrics['cumulative_reward']]),
            'total_regret': np.mean([metrics['total_regret']]),
            'best_action_percentage': np.mean([metrics['best_action_percentage']]),
            'diversity_score': np.mean([metrics['diversity_score']]),
            'convergence_speed': int(np.mean([metrics['convergence_speed']]))
        }

        ucb_result = ExplorationResult(
            strategy="ucb",
            schedule_name="ucb",
            final_reward=avg_metrics['final_reward'],
            cumulative_reward=avg_metrics['cumulative_reward'],
            regret=avg_metrics['total_regret'],
            best_action_percentage=avg_metrics['best_action_percentage'],
            diversity_score=avg_metrics['diversity_score'],
            convergence_speed=avg_metrics['convergence_speed'],
            schedule_params={"c": 2.0}
        )
        results.append(ucb_result)
        print(f"  UCB: Final Reward = {ucb_result.final_reward:.4f}, Regret = {ucb_result.regret:.2f}")

        # Test Thompson Sampling
        print("\nTesting Thompson Sampling...")
        for run in range(10):
            bandit = MultiArmedBandit(num_arms=10, seed=42 + run)
            rewards, regrets, actions = self.simulator.simulate_thompson_sampling(bandit, num_steps=num_steps)
            metrics = self.calculate_metrics(rewards, regrets, actions, bandit.num_arms)

        thompson_result = ExplorationResult(
            strategy="thompson_sampling",
            schedule_name="thompson_sampling",
            final_reward=avg_metrics['final_reward'],
            cumulative_reward=avg_metrics['cumulative_reward'],
            regret=avg_metrics['total_regret'],
            best_action_percentage=avg_metrics['best_action_percentage'],
            diversity_score=avg_metrics['diversity_score'],
            convergence_speed=avg_metrics['convergence_speed'],
            schedule_params={"prior_variance": 1.0}
        )
        results.append(thompson_result)
        print(f"  Thompson Sampling: Final Reward = {thompson_result.final_reward:.4f}, Regret = {thompson_result.regret:.2f}")

        return results

    def rank_results(self, results: List[ExplorationResult]) -> List[ExplorationResult]:
        """Rank exploration strategies by combined score"""
        for result in results:
            # Combined score: reward high, regret low, diversity moderate
            result.combined_score = (
                result.final_reward * 2.0 -
                result.regret * 0.001 +
                result.diversity_score * 0.1
            )

        return sorted(results, key=lambda r: r.combined_score, reverse=True)

    def visualize_results(self, results: List[ExplorationResult]):
        """Create visualization for exploration schedule comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Sort by combined score
        ranked = sorted(results, key=lambda r: getattr(r, 'combined_score', 0), reverse=True)
        top_5 = ranked[:5]

        names = [r.schedule_name for r in top_5]
        colors = plt.cm.plasma(np.linspace(0, 1, len(names)))

        # Bar chart: Final Reward
        ax = axes[0, 0]
        rewards = [r.final_reward for r in top_5]
        ax.barh(names, rewards, color=colors)
        ax.set_xlabel("Final Reward (higher is better)")
        ax.set_title("Final Reward Comparison", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Cumulative Regret
        ax = axes[0, 1]
        regrets = [r.regret for r in top_5]
        ax.barh(names, regrets, color=colors)
        ax.set_xlabel("Cumulative Regret (lower is better)")
        ax.set_title("Regret Comparison", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Diversity Score
        ax = axes[1, 0]
        diversity = [r.diversity_score for r in top_5]
        ax.barh(names, diversity, color=colors)
        ax.set_xlabel("Diversity Score (higher is better)")
        ax.set_title("Action Diversity", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Bar chart: Combined Score
        ax = axes[1, 1]
        scores = [getattr(r, 'combined_score', 0) for r in top_5]
        ax.barh(names, scores, color=colors)
        ax.set_xlabel("Combined Score (higher is better)")
        ax.set_title("Overall Performance", fontsize=12, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "exploration_schedule_comparison.png", dpi=300)
        plt.close()

        # Plot top 3 learning curves
        fig, ax = plt.subplots(figsize=(12, 6))

        for i, result in enumerate(top_5[:3]):
            # Simulate again to get full curve
            schedule_func = getattr(self.schedules, result.schedule_name, None)

            if schedule_func is not None and result.strategy == "epsilon_greedy":
                schedule = schedule_func(**result.schedule_params, total_steps=1000)
                bandit = MultiArmedBandit(num_arms=10, seed=42)
                rewards, _, _ = self.simulator.simulate_epsilon_greedy(schedule, bandit)
            elif schedule_func is not None and result.strategy == "boltzmann":
                schedule = schedule_func(**result.schedule_params, total_steps=1000)
                bandit = MultiArmedBandit(num_arms=10, seed=42)
                rewards, _, _ = self.simulator.simulate_boltzmann(schedule, bandit)
            else:
                continue

            # Smooth curve
            window = 50
            smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
            ax.plot(smoothed, label=result.schedule_name, linewidth=2)

        ax.set_title("Top 3 Exploration Learning Curves", fontsize=14, fontweight='bold')
        ax.set_xlabel("Step")
        ax.set_ylabel("Reward (smoothed)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "exploration_learning_curves.png", dpi=300)
        plt.close()

    def save_results(self, ranked_results: List[ExplorationResult]):
        """Save results to JSON"""
        output = {
            "optimal_strategy": ranked_results[0].strategy,
            "optimal_schedule": ranked_results[0].schedule_name,
            "optimal_params": ranked_results[0].schedule_params,
            "all_schedules": [
                {
                    "strategy": r.strategy,
                    "schedule_name": r.schedule_name,
                    "final_reward": float(r.final_reward),
                    "cumulative_reward": float(r.cumulative_reward),
                    "regret": float(r.regret),
                    "best_action_percentage": float(r.best_action_percentage),
                    "diversity_score": float(r.diversity_score),
                    "convergence_speed": int(r.convergence_speed),
                    "combined_score": float(getattr(r, 'combined_score', 0)),
                    "params": r.schedule_params
                }
                for r in ranked_results
            ]
        }

        with open(self.output_dir / "exploration_optimal_schedule.json", "w") as f:
            json.dump(output, f, indent=2)


def main():
    """Run exploration schedule optimization"""
    optimizer = ScheduleOptimizer()

    print("="*70)
    print("EXPLORATION SCHEDULE OPTIMIZATION")
    print("="*70)
    print("\nTesting exploration strategies on multi-armed bandit:")
    print("  - Epsilon-greedy (8 schedules)")
    print("  - Boltzmann/Softmax (7 schedules)")
    print("  - UCB")
    print("  - Thompson Sampling")
    print("\nEach strategy tested with 10 runs for statistical validity")
    print("="*70)

    results = optimizer.optimize_exploration()
    ranked = optimizer.rank_results(results)

    optimizer.visualize_results(ranked)
    optimizer.save_results(ranked)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nBest Strategy: {ranked[0].strategy}")
    print(f"Best Schedule: {ranked[0].schedule_name}")
    print(f"Parameters: {ranked[0].schedule_params}")
    print(f"Final Reward: {ranked[0].final_reward:.4f}")
    print(f"Cumulative Regret: {ranked[0].regret:.2f}")
    print("\nResults saved to:", optimizer.output_dir)
    print("="*70)


if __name__ == "__main__":
    main()
