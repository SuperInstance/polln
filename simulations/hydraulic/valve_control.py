"""
Valve Control Theory Simulation for POLLN Hydraulic Metaphor

This module simulates stochastic routing decisions (valves) using:
- Gumbel-softmax for differentiable routing
- Temperature annealing for exploration vs exploitation
- Optimal temperature schedule discovery

Mathematical Model:
    π_i = exp((logits_i)/τ) / Σ exp((logits_j)/τ)

Where:
    π_i = probability of choosing option i
    logits_i = log-preference for option i
    τ = temperature parameter

Key insights:
- High τ: More exploration (uniform distribution)
- Low τ: More exploitation (peak distribution)
- Optimal τ depends on task complexity and uncertainty
"""

import numpy as np
import networkx as nx
from scipy.special import softmax
from scipy.optimize import minimize_scalar
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
from collections import defaultdict


@dataclass
class ValveConfig:
    """Configuration for valve (routing) control"""
    num_options: int  # Number of routing options
    initial_logits: np.ndarray  # Initial log-preferences
    min_temperature: float = 0.01  # Minimum temperature
    max_temperature: float = 5.0  # Maximum temperature
    annealing_schedule: str = 'exponential'  # 'exponential', 'linear', 'cosine'


@dataclass
class SelectionResult:
    """Result of a valve selection"""
    selected_option: int
    probabilities: np.ndarray
    temperature: float
    entropy: float
    exploration_score: float


class GumbelSoftmaxValve:
    """
    Implements Gumbel-softmax valve for stochastic routing.

    The Gumbel-softmax trick provides differentiable samples from
    categorical distributions, enabling gradient-based optimization.

    Key equations:
        1. Gumbel noise: g = -log(-log(u)), u ~ Uniform(0,1)
        2. Perturbed logits: l_i' = (l_i + g_i) / τ
        3. Softmax: π_i = exp(l_i') / Σ exp(l_j')
    """

    def __init__(self, config: ValveConfig):
        """
        Initialize valve.

        Args:
            config: Valve configuration
        """
        self.config = config
        self.logits = config.initial_logits.copy()
        self.temperature_history = []
        self.selection_history = []
        self.reward_history = []

    def sample_gumbel(self, shape: Tuple[int, ...]) -> np.ndarray:
        """
        Sample from Gumbel distribution.

        g = -log(-log(u)), u ~ Uniform(0,1)

        Args:
            shape: Shape of output array

        Returns:
            Gumbel samples
        """
        u = np.random.uniform(0, 1, shape)
        return -np.log(-np.log(u + 1e-10) + 1e-10)

    def gumbel_softmax_sample(
        self,
        logits: np.ndarray,
        temperature: float
    ) -> np.ndarray:
        """
        Sample using Gumbel-softmax trick.

        Args:
            logits: Log-preferences
            temperature: Temperature parameter

        Returns:
            Probability distribution
        """
        # Add Gumbel noise
        gumbel_noise = self.sample_gumbel(logits.shape)

        # Perturb logits with temperature
        perturbed_logits = (logits + gumbel_noise) / temperature

        # Apply softmax
        probs = softmax(perturbed_logits)

        return probs

    def select(
        self,
        temperature: Optional[float] = None,
        hard: bool = False
    ) -> SelectionResult:
        """
        Make a selection using current valve state.

        Args:
            temperature: Override temperature (optional)
            hard: If True, return one-hot (argmax), else soft probabilities

        Returns:
            Selection result
        """
        if temperature is None:
            temperature = self.current_temperature

        # Get probabilities
        probs = self.gumbel_softmax_sample(self.logits, temperature)

        # Select option
        if hard:
            selected_option = np.argmax(probs)
            probabilities = np.zeros_like(probs)
            probabilities[selected_option] = 1.0
        else:
            selected_option = np.random.choice(len(probs), p=probs)
            probabilities = probs

        # Compute metrics
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        exploration_score = entropy / np.log(len(probs))

        result = SelectionResult(
            selected_option=selected_option,
            probabilities=probabilities,
            temperature=temperature,
            entropy=entropy,
            exploration_score=exploration_score
        )

        self.selection_history.append(result)
        self.temperature_history.append(temperature)

        return result

    def update_logits(
        self,
        selected_option: int,
        reward: float,
        learning_rate: float = 0.1
    ):
        """
        Update logits based on reward (policy gradient).

        ∇θ J(θ) = E[∇θ log π(a|s) * R]

        Args:
            selected_option: Option that was selected
            reward: Reward received
            learning_rate: Learning rate
        """
        # Policy gradient update
        for i in range(len(self.logits)):
            if i == selected_option:
                # Increase logits for selected option if reward > 0
                self.logits[i] += learning_rate * reward
            else:
                # Decrease logits for non-selected options
                self.logits[i] -= learning_rate * reward * 0.1

        self.reward_history.append(reward)

    @property
    def current_temperature(self) -> float:
        """Get current temperature (can be overridden by subclasses)"""
        return 1.0

    def reset(self):
        """Reset valve state"""
        self.logits = self.config.initial_logits.copy()
        self.temperature_history = []
        self.selection_history = []
        self.reward_history = []


class AnnealedValve(GumbelSoftmaxValve):
    """
    Valve with temperature annealing schedule.

    Supports multiple annealing schedules:
    1. Exponential: τ_t = τ_max * (τ_min/τ_max)^(t/T)
    2. Linear: τ_t = τ_max - (τ_max - τ_min) * (t/T)
    3. Cosine: τ_t = τ_min + 0.5(τ_max - τ_min)(1 + cos(πt/T))
    """

    def __init__(
        self,
        config: ValveConfig,
        total_steps: int = 1000
    ):
        """
        Initialize annealed valve.

        Args:
            config: Valve configuration
            total_steps: Total number of annealing steps
        """
        super().__init__(config)
        self.total_steps = total_steps
        self.current_step = 0

    @property
    def current_temperature(self) -> float:
        """Compute current temperature based on annealing schedule"""
        t = self.current_step / self.total_steps

        if self.config.annealing_schedule == 'exponential':
            # Exponential decay
            return self.config.max_temperature * (
                self.config.min_temperature / self.config.max_temperature
            ) ** t

        elif self.config.annealing_schedule == 'linear':
            # Linear decay
            return self.config.max_temperature - (
                self.config.max_temperature - self.config.min_temperature
            ) * t

        elif self.config.annealing_schedule == 'cosine':
            # Cosine annealing
            return self.config.min_temperature + 0.5 * (
                self.config.max_temperature - self.config.min_temperature
            ) * (1 + np.cos(np.pi * t))

        else:
            raise ValueError(f"Unknown schedule: {self.config.annealing_schedule}")

    def step(self):
        """Advance annealing step"""
        self.current_step = min(self.current_step + 1, self.total_steps)


class AdaptiveValve(GumbelSoftmaxValve):
    """
    Valve with adaptive temperature based on performance.

    Adjusts temperature based on:
    1. Recent reward variance (high variance → higher temperature)
    2. Performance plateau (stagnant rewards → higher temperature)
    3. Success rate (high success → lower temperature)
    """

    def __init__(
        self,
        config: ValveConfig,
        window_size: int = 100,
        target_entropy: float = 0.5
    ):
        """
        Initialize adaptive valve.

        Args:
            config: Valve configuration
            window_size: Window for computing statistics
            target_entropy: Target exploration level (0-1)
        """
        super().__init__(config)
        self.window_size = window_size
        self.target_entropy = target_entropy
        self.adaptive_temperature = config.max_temperature / 2

    @property
    def current_temperature(self) -> float:
        """Get adaptive temperature"""
        return self.adaptive_temperature

    def update_temperature(self):
        """
        Update temperature based on recent performance.

        Rules:
        1. If recent entropy < target: increase temperature
        2. If rewards stagnant: increase temperature
        3. If high success rate: decrease temperature
        """
        if len(self.reward_history) < self.window_size:
            return

        recent_rewards = self.reward_history[-self.window_size:]
        recent_selections = self.selection_history[-self.window_size:]

        # Compute statistics
        reward_std = np.std(recent_rewards)
        reward_mean = np.mean(recent_rewards)
        avg_entropy = np.mean([s.entropy for s in recent_selections])

        # Normalize entropy to [0,1]
        max_entropy = np.log(len(self.logits))
        normalized_entropy = avg_entropy / max_entropy

        # Adjust temperature
        entropy_error = self.target_entropy - normalized_entropy

        if abs(entropy_error) > 0.1:
            # Need to adjust exploration
            if entropy_error > 0:
                # Increase exploration
                self.adaptive_temperature *= 1.1
            else:
                # Decrease exploration
                self.adaptive_temperature *= 0.9

        # Clamp temperature
        self.adaptive_temperature = np.clip(
            self.adaptive_temperature,
            self.config.min_temperature,
            self.config.max_temperature
        )


class ValveControlSimulation:
    """
    Simulates valve control in multi-agent routing scenarios.
    """

    def __init__(
        self,
        num_agents: int = 20,
        num_tasks: int = 100,
        task_complexities: Optional[List[float]] = None
    ):
        """
        Initialize simulation.

        Args:
            num_agents: Number of agents (routing options)
            num_tasks: Number of tasks to route
            task_complexities: List of task complexities
        """
        self.num_agents = num_agents
        self.num_tasks = num_tasks

        if task_complexities is None:
            # Generate task complexities (power law)
            self.task_complexities = np.random.pareto(2.0, num_tasks)
        else:
            self.task_complexities = np.array(task_complexities)

        # Agent capabilities (random)
        self.agent_capabilities = np.random.rand(num_agents)

        # Results
        self.results = defaultdict(dict)

    def simulate_routing(
        self,
        valve: GumbelSoftmaxValve,
        task_idx: int
    ) -> Tuple[int, float]:
        """
        Simulate routing a single task.

        Args:
            valve: Valve to use for routing
            task_idx: Task index

        Returns:
            Tuple of (selected_agent, reward)
        """
        # Select agent
        result = valve.select()

        # Compute reward based on match between task and agent
        task_complexity = self.task_complexities[task_idx]
        agent_capability = self.agent_capabilities[result.selected_option]

        # Reward: better match = higher reward
        # Ideal: capability ≈ complexity
        mismatch = abs(task_complexity - agent_capability)
        reward = np.exp(-mismatch) - 0.5  # Normalize around 0

        # Update valve
        valve.update_logits(result.selected_option, reward)

        return result.selected_option, reward

    def compare_annealing_schedules(
        self,
        schedules: List[str] = None,
        num_trials: int = 20
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Compare different annealing schedules.

        Args:
            schedules: List of schedule names
            num_trials: Number of trials per schedule

        Returns:
            Comparison results
        """
        if schedules is None:
            schedules = ['exponential', 'linear', 'cosine']

        results = defaultdict(lambda: defaultdict(list))

        for schedule in schedules:
            print(f"\nTesting {schedule} schedule...")

            for trial in range(num_trials):
                # Create valve
                config = ValveConfig(
                    num_options=self.num_agents,
                    initial_logits=np.random.randn(self.num_agents),
                    annealing_schedule=schedule
                )
                valve = AnnealedValve(config, total_steps=self.num_tasks)

                # Simulate routing
                total_reward = 0
                rewards_per_step = []

                for task_idx in range(self.num_tasks):
                    agent, reward = self.simulate_routing(valve, task_idx)
                    total_reward += reward
                    rewards_per_step.append(reward)
                    valve.step()

                # Store results
                results[schedule]['total_reward'].append(total_reward)
                results[schedule]['final_reward'].append(rewards_per_step[-1])
                results[schedule]['reward_trajectory'].append(rewards_per_step)

        return dict(results)

    def find_optimal_temperature(
        self,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """
        Find optimal temperature for exploration-exploitation trade-off.

        Args:
            num_samples: Number of temperatures to test

        Returns:
            Optimal temperatures and corresponding rewards
        """
        temperatures = np.logspace(-2, 1, num_samples)
        avg_rewards = []

        for temp in temperatures:
            # Create valve with fixed temperature
            config = ValveConfig(
                num_options=self.num_agents,
                initial_logits=np.random.randn(self.num_agents)
            )

            class FixedTempValve(GumbelSoftmaxValve):
                def __init__(self, config, temperature):
                    super().__init__(config)
                    self.fixed_temp = temperature

                @property
                def current_temperature(self):
                    return self.fixed_temp

            valve = FixedTempValve(config, temp)

            # Simulate
            total_reward = 0
            for task_idx in range(min(self.num_tasks, 100)):
                _, reward = self.simulate_routing(valve, task_idx)
                total_reward += reward

            avg_rewards.append(total_reward / min(self.num_tasks, 100))

        # Find optimal temperature
        optimal_idx = np.argmax(avg_rewards)
        optimal_temp = temperatures[optimal_idx]

        return {
            'optimal_temperature': optimal_temp,
            'optimal_reward': avg_rewards[optimal_idx],
            'temperatures': temperatures,
            'rewards': avg_rewards
        }

    def simulate_adaptive_control(
        self,
        num_steps: int = 1000
    ) -> Dict[str, List]:
        """
        Simulate adaptive temperature control.

        Args:
            num_steps: Number of simulation steps

        Returns:
            Simulation results
        """
        # Create adaptive valve
        config = ValveConfig(
            num_options=self.num_agents,
            initial_logits=np.random.randn(self.num_agents)
        )
        valve = AdaptiveValve(config, window_size=100)

        results = {
            'temperature': [],
            'rewards': [],
            'entropy': [],
            'exploration': []
        }

        for step in range(num_steps):
            task_idx = step % self.num_tasks

            # Route task
            _, reward = self.simulate_routing(valve, task_idx)

            # Update temperature
            valve.update_temperature()

            # Record results
            results['temperature'].append(valve.current_temperature)
            results['rewards'].append(reward)

            if valve.selection_history:
                last_selection = valve.selection_history[-1]
                results['entropy'].append(last_selection.entropy)
                results['exploration'].append(last_selection.exploration_score)

        return results

    def visualize_temperature_schedules(
        self,
        results: Dict[str, Dict[str, List[float]]],
        save_path: Optional[str] = None
    ):
        """
        Visualize temperature annealing schedules.

        Args:
            results: Comparison results
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        schedules = list(results.keys())

        # 1. Total reward comparison
        ax = axes[0, 0]
        for schedule in schedules:
            rewards = results[schedule]['total_reward']
            ax.hist(rewards, alpha=0.5, label=schedule, bins=20)
        ax.set_xlabel('Total Reward')
        ax.set_ylabel('Frequency')
        ax.set_title('Total Reward Distribution')
        ax.legend()

        # 2. Reward trajectory (mean and std)
        ax = axes[0, 1]
        steps = range(self.num_tasks)
        for schedule in schedules:
            trajectories = np.array(results[schedule]['reward_trajectory'])
            mean_reward = np.mean(trajectories, axis=0)
            std_reward = np.std(trajectories, axis=0)

            ax.plot(steps, mean_reward, label=schedule, linewidth=2)
            ax.fill_between(
                steps,
                mean_reward - std_reward,
                mean_reward + std_reward,
                alpha=0.2
            )
        ax.set_xlabel('Task')
        ax.set_ylabel('Reward')
        ax.set_title('Learning Curves')
        ax.legend()

        # 3. Final reward comparison
        ax = axes[1, 0]
        final_rewards = [results[s]['final_reward'] for s in schedules]
        ax.boxplot(final_rewards, labels=schedules)
        ax.set_ylabel('Final Reward')
        ax.set_title('Final Performance Comparison')
        ax.tick_params(axis='x', rotation=45)

        # 4. Summary statistics
        ax = axes[1, 1]
        ax.axis('off')

        summary_text = "Summary Statistics\n\n"
        for schedule in schedules:
            rewards = results[schedule]['total_reward']
            summary_text += f"{schedule.capitalize()}:\n"
            summary_text += f"  Mean: {np.mean(rewards):.4f}\n"
            summary_text += f"  Std: {np.std(rewards):.4f}\n"
            summary_text += f"  Max: {np.max(rewards):.4f}\n\n"

        ax.text(0.1, 0.5, summary_text, fontsize=10, family='monospace')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_optimal_temperature(
        self,
        opt_results: Dict[str, float],
        save_path: Optional[str] = None
    ):
        """
        Visualize optimal temperature analysis.

        Args:
            opt_results: Results from find_optimal_temperature
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))

        # 1. Temperature vs Reward
        ax = axes[0]
        temps = opt_results['temperatures']
        rewards = opt_results['rewards']

        ax.semilogx(temps, rewards, linewidth=2)
        ax.axvline(
            opt_results['optimal_temperature'],
            color='red',
            linestyle='--',
            label=f"Optimal: {opt_results['optimal_temperature']:.4f}"
        )
        ax.scatter([opt_results['optimal_temperature']], [opt_results['optimal_reward']],
                  color='red', s=100, zorder=5)
        ax.set_xlabel('Temperature')
        ax.set_ylabel('Average Reward')
        ax.set_title('Temperature vs Reward')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Exploration-Exploitation Trade-off
        ax = axes[1]

        # Compute exploration level for each temperature
        exploration_levels = []
        for temp in temps:
            # Sample probabilities at this temperature
            logits = np.random.randn(10)
            probs = softmax(logits / temp)
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            max_entropy = np.log(10)
            exploration_levels.append(entropy / max_entropy)

        ax.plot(exploration_levels, rewards, linewidth=2)
        ax.axvline(0.5, color='gray', linestyle='--', alpha=0.5, label='Balanced')
        ax.scatter(
            [exploration_levels[np.argmax(rewards)]],
            [opt_results['optimal_reward']],
            color='red',
            s=100,
            zorder=5
        )
        ax.set_xlabel('Exploration Level')
        ax.set_ylabel('Average Reward')
        ax.set_title('Exploration-Exploitation Trade-off')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_adaptive_control(
        self,
        results: Dict[str, List],
        save_path: Optional[str] = None
    ):
        """
        Visualize adaptive control results.

        Args:
            results: Simulation results
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        steps = range(len(results['temperature']))

        # 1. Temperature evolution
        ax = axes[0, 0]
        ax.plot(steps, results['temperature'], linewidth=2)
        ax.set_xlabel('Step')
        ax.set_ylabel('Temperature')
        ax.set_title('Adaptive Temperature Evolution')
        ax.grid(True, alpha=0.3)

        # 2. Reward trajectory
        ax = axes[0, 1]
        # Compute moving average
        window = 50
        if len(results['rewards']) > window:
            moving_avg = np.convolve(
                results['rewards'],
                np.ones(window) / window,
                mode='valid'
            )
            ax.plot(steps[window-1:], moving_avg, linewidth=2, label='Moving Average')
        ax.scatter(steps, results['rewards'], alpha=0.3, s=10, label='Rewards')
        ax.set_xlabel('Step')
        ax.set_ylabel('Reward')
        ax.set_title('Reward Trajectory')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Entropy evolution
        ax = axes[1, 0]
        ax.plot(steps, results['entropy'], linewidth=2, color='purple')
        ax.axhline(
            np.mean(results['entropy']),
            color='red',
            linestyle='--',
            label=f"Mean: {np.mean(results['entropy']):.4f}"
        )
        ax.set_xlabel('Step')
        ax.set_ylabel('Entropy')
        ax.set_title('Selection Entropy')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 4. Exploration score
        ax = axes[1, 1]
        ax.plot(steps, results['exploration'], linewidth=2, color='orange')
        ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='Balanced')
        ax.set_xlabel('Step')
        ax.set_ylabel('Exploration Score')
        ax.set_title('Exploration Level')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """Run demonstration simulations"""
    print("=" * 60)
    print("VALVE CONTROL THEORY SIMULATION")
    print("=" * 60)

    # Create simulation
    sim = ValveControlSimulation(
        num_agents=20,
        num_tasks=100
    )

    print(f"\nConfiguration:")
    print(f"  Agents: {sim.num_agents}")
    print(f"  Tasks: {sim.num_tasks}")

    # Compare annealing schedules
    print("\n" + "="*60)
    print("COMPARING ANNEALING SCHEDULES")
    print("="*60)

    results = sim.compare_annealing_schedules(
        schedules=['exponential', 'linear', 'cosine'],
        num_trials=20
    )

    sim.visualize_temperature_schedules(results)

    # Find optimal temperature
    print("\n" + "="*60)
    print("FINDING OPTIMAL TEMPERATURE")
    print("="*60)

    opt_results = sim.find_optimal_temperature(num_samples=50)
    print(f"\nOptimal Temperature: {opt_results['optimal_temperature']:.4f}")
    print(f"Optimal Reward: {opt_results['optimal_reward']:.4f}")

    sim.visualize_optimal_temperature(opt_results)

    # Simulate adaptive control
    print("\n" + "="*60)
    print("SIMULATING ADAPTIVE CONTROL")
    print("="*60)

    adaptive_results = sim.simulate_adaptive_control(num_steps=1000)

    sim.visualize_adaptive_control(adaptive_results)

    print("\nSimulation complete!")


if __name__ == '__main__':
    main()
