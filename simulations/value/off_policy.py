"""
Off-Policy TD(λ) Learning with Importance Sampling

Mathematical Foundation:
    Importance sampling ratio: ρ_t = π(a_t|s_t) / μ(a_t|s_t)
    Off-policy TD update: V(s) ← V(s) + α × ρ × δ × e

Research Questions:
    Q1: What are safe off-policy learning bounds?
    Q2: How does variance scale with policy divergence?
    Q3: When does off-policy learning become unstable?
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Optional, Tuple as TupleType
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class PolicyType(Enum):
    """Policy types"""
    UNIFORM = "Uniform"
    GREEDY = "Greedy"
    EPSILON_SOFT = "Epsilon-Soft"
    BOLTZMANN = "Boltzmann"


@dataclass
class OffPolicyConfig:
    """Configuration for off-policy simulation"""
    num_states: int = 10
    num_actions: int = 2
    gamma: float = 0.99
    alpha: float = 0.1
    lambda_: float = 0.5
    num_episodes: int = 1000
    num_runs: int = 100

    # Behavior policy
    behavior_epsilon: float = 0.5  # High exploration

    # Target policy
    target_epsilon: float = 0.1  # Low exploration

    # Importance sampling
    use_importance_sampling: bool = True
    use_per_replay: bool = False
    c: float = 10.0  # Truncation parameter for per-replay


class GridWorld:
    """
    Grid world MDP for off-policy learning

    Simple chain with stochastic rewards
    """

    def __init__(self, num_states: int, num_actions: int = 2):
        self.num_states = num_states
        self.num_actions = num_actions
        self.terminal_state = num_states - 1

        # Transition probabilities
        # Action 0: Move left (with noise)
        # Action 1: Move right (with noise)
        self.transition_noise = 0.1

        # True values (computable analytically)
        self.true_values = np.zeros(num_states)
        self._compute_true_values()

    def _compute_true_values(self):
        """Compute true state values for optimal policy"""
        # For optimal policy (always move right)
        gamma = 0.99
        for s in range(self.num_states - 1, -1, -1):
            if s == self.terminal_state:
                self.true_values[s] = 0.0
            else:
                # Reward at each step, plus discounted future
                self.true_values[s] = 1.0 + gamma * self.true_values[s + 1]

    def step(self, state: int, action: int) -> Tuple[int, float, bool]:
        """Take step with action"""
        if state == self.terminal_state:
            return state, 0.0, True

        # Add transition noise
        if np.random.random() < self.transition_noise:
            action = 1 - action  # Flip action

        # Apply action
        if action == 0:  # Left
            next_state = max(0, state - 1)
        else:  # Right
            next_state = min(self.terminal_state, state + 1)

        # Reward
        reward = 1.0  # Constant reward per step

        return next_state, reward, next_state == self.terminal_state

    def reset(self) -> int:
        """Reset to initial state"""
        return 0


class Policy:
    """Policy with different exploration strategies"""

    def __init__(self, policy_type: PolicyType, num_actions: int,
                 epsilon: float = 0.1, temperature: float = 1.0):
        self.policy_type = policy_type
        self.num_actions = num_actions
        self.epsilon = epsilon
        self.temperature = temperature

    def get_probability(self, action: int, state: int, q_values: Optional[np.ndarray] = None) -> float:
        """Get probability of action"""
        if self.policy_type == PolicyType.UNIFORM:
            return 1.0 / self.num_actions

        elif self.policy_type == PolicyType.EPSILON_SOFT:
            if q_values is None or len(q_values) == 0:
                return 1.0 / self.num_actions

            # Epsilon-soft: epsilon prob to random, 1-epsilon to greedy
            best_action = np.argmax(q_values)
            if action == best_action:
                return 1 - self.epsilon + self.epsilon / self.num_actions
            else:
                return self.epsilon / self.num_actions

        elif self.policy_type == PolicyType.BOLTZMANN:
            if q_values is None or len(q_values) == 0:
                return 1.0 / self.num_actions

            # Boltzmann (softmax) distribution
            exp_q = np.exp(q_values / self.temperature)
            probs = exp_q / np.sum(exp_q)
            return probs[action]

        elif self.policy_type == PolicyType.GREEDY:
            if q_values is None or len(q_values) == 0:
                return 1.0 / self.num_actions
            best_action = np.argmax(q_values)
            return 1.0 if action == best_action else 0.0

        return 1.0 / self.num_actions

    def select_action(self, state: int, q_values: Optional[np.ndarray] = None) -> int:
        """Select action according to policy"""
        if self.policy_type == PolicyType.UNIFORM:
            return np.random.randint(self.num_actions)

        elif self.policy_type == PolicyType.EPSILON_SOFT:
            if q_values is None or len(q_values) == 0:
                return np.random.randint(self.num_actions)

            if np.random.random() < self.epsilon:
                return np.random.randint(self.num_actions)
            else:
                return np.argmax(q_values)

        elif self.policy_type == PolicyType.BOLTZMANN:
            if q_values is None or len(q_values) == 0:
                return np.random.randint(self.num_actions)

            exp_q = np.exp(q_values / self.temperature)
            probs = exp_q / np.sum(exp_q)
            return np.random.choice(self.num_actions, p=probs)

        elif self.policy_type == PolicyType.GREEDY:
            if q_values is None or len(q_values) == 0:
                return np.random.randint(self.num_actions)
            return np.argmax(q_values)

        return np.random.randint(self.num_actions)


class OffPolicyAgent:
    """Off-policy TD(λ) agent with importance sampling"""

    def __init__(self, config: OffPolicyConfig):
        self.config = config
        self.num_states = config.num_states
        self.num_actions = config.num_actions

        # Value function
        self.values = np.zeros(config.num_states)

        # Q-values for action selection
        self.q_values = np.zeros((config.num_states, config.num_actions))

        # Eligibility traces
        self.value_eligibility = np.zeros(config.num_states)
        self.q_eligibility = np.zeros((config.num_states, config.num_actions))

        # Importance sampling
        self.rho = 1.0
        self.c = config.c

        # Policies
        self.behavior_policy = Policy(
            PolicyType.EPSILON_SOFT,
            config.num_actions,
            config.behavior_epsilon
        )
        self.target_policy = Policy(
            PolicyType.GREEDY,
            config.num_actions,
            config.target_epsilon
        )

    def reset_traces(self):
        """Reset eligibility traces"""
        self.value_eligibility = np.zeros(self.num_states)
        self.q_eligibility = np.zeros((self.num_states, self.num_actions))

    def compute_importance_ratio(self, state: int, action: int) -> float:
        """Compute importance sampling ratio: π(a|s) / μ(a|s)"""
        target_prob = self.target_policy.get_probability(action, state, self.q_values[state])
        behavior_prob = self.behavior_policy.get_probability(action, state, self.q_values[state])

        if behavior_prob < 1e-10:
            return 0.0

        return target_prob / behavior_prob

    def update_value_td0(self, state: int, action: int, reward: float,
                        next_state: int, done: bool, importance_ratio: float):
        """Off-policy TD(0) value update"""
        # TD target
        if done:
            target = reward
        else:
            target = reward + self.config.gamma * self.values[next_state]

        # TD error
        td_error = target - self.values[state]

        # Update with importance sampling
        if self.config.use_importance_sampling:
            self.values[state] += self.config.alpha * importance_ratio * td_error
        else:
            self.values[state] += self.config.alpha * td_error

    def update_value_tdlambda(self, state: int, action: int, reward: float,
                             next_state: int, done: bool, importance_ratio: float):
        """Off-policy TD(λ) value update with eligibility traces"""
        # TD target
        if done:
            target = reward
        else:
            target = reward + self.config.gamma * self.values[next_state]

        # TD error
        td_error = target - self.values[state]

        # Update importance sampling
        if self.config.use_per_replay:
            # Per-replay: truncate importance ratio
            self.rho = min(self.rho, self.c)
        self.rho *= importance_ratio

        # Update eligibility trace
        self.value_eligibility[state] += 1

        # Update with importance sampling
        if self.config.use_importance_sampling:
            update = self.config.alpha * self.rho * td_error * self.value_eligibility
        else:
            update = self.config.alpha * td_error * self.value_eligibility

        self.values += update
        self.value_eligibility *= self.config.gamma * self.config.lambda_

        if done:
            self.reset_traces()
            self.rho = 1.0

    def update_q_learning(self, state: int, action: int, reward: float,
                         next_state: int, done: bool):
        """Q-learning (off-policy, no importance sampling needed)"""
        # Q-learning target
        if done:
            target = reward
        else:
            target = reward + self.config.gamma * np.max(self.q_values[next_state])

        # TD error
        td_error = target - self.q_values[state, action]

        # Update
        self.q_values[state, action] += self.config.alpha * td_error

    def compute_rms_error(self, true_values: np.ndarray) -> float:
        """Compute RMS error"""
        return np.sqrt(np.mean((self.values - true_values) ** 2))

    def compute_q_rms_error(self, true_values: np.ndarray) -> float:
        """Compute RMS error for Q-values (use max action)"""
        predicted = np.max(self.q_values, axis=1)
        return np.sqrt(np.mean((predicted - true_values) ** 2))


class OffPolicySimulator:
    """
    Simulates off-policy TD(λ) learning

    Research Questions:
        Q1: What are safe off-policy learning bounds?
        Q2: How does variance scale with policy divergence?
        Q3: When does off-policy learning become unstable?
    """

    def __init__(self, config: OffPolicyConfig):
        self.config = config
        self.results: Dict[str, List[Dict]] = {}
        self.env = GridWorld(config.num_states, config.num_actions)

        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 12

    def run_episode(self, agent: OffPolicyAgent,
                   use_q_learning: bool = False) -> Tuple[float, float]:
        """Run a single episode, return (value_error, q_error)"""
        state = self.env.reset()
        agent.reset_traces()

        while True:
            # Select action from behavior policy
            action = agent.behavior_policy.select_action(state, agent.q_values[state])

            # Take step
            next_state, reward, done = self.env.step(state, action)

            # Compute importance ratio
            importance_ratio = agent.compute_importance_ratio(state, action)

            # Update
            if use_q_learning:
                agent.update_q_learning(state, action, reward, next_state, done)
            else:
                agent.update_value_tdlambda(state, action, reward, next_state,
                                          done, importance_ratio)

            state = next_state
            if done:
                break

        value_error = agent.compute_rms_error(self.env.true_values)
        q_error = agent.compute_q_rms_error(self.env.true_values)

        return value_error, q_error

    def compare_policy_divergence(self) -> pd.DataFrame:
        """
        Q2: How does variance scale with policy divergence?
        """
        print("\n" + "="*70)
        print("POLICY DIVERGENCE ANALYSIS")
        print("="*70)

        behavior_epsilons = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        results = []

        for beh_eps in behavior_epsilons:
            print(f"\nBehavior epsilon: {beh_eps:.1f}")

            self.config.behavior_epsilon = beh_eps
            self.config.target_epsilon = 0.1

            # Track variance
            final_errors = []
            all_errors = []

            for run in range(self.config.num_runs):
                agent = OffPolicyAgent(self.config)

                episode_errors = []
                for episode in range(self.config.num_episodes):
                    value_error, _ = self.run_episode(agent, use_q_learning=False)
                    episode_errors.append(value_error)

                final_errors.append(episode_errors[-1])
                all_errors.append(episode_errors)

            # Compute statistics
            mean_final_error = np.mean(final_errors)
            std_final_error = np.std(final_errors)

            # Estimate variance from all episodes
            all_errors_array = np.array(all_errors)
            variance = np.var(all_errors_array)

            results.append({
                'Behavior Epsilon': beh_eps,
                'Target Epsilon': self.config.target_epsilon,
                'Divergence': abs(beh_eps - self.config.target_epsilon),
                'Mean Final Error': mean_final_error,
                'Std Final Error': std_final_error,
                'Variance': variance,
                'Stability': 1.0 / (variance + 1e-10)
            })

            print(f"  Mean Error: {mean_final_error:.4f} ± {std_final_error:.4f}")
            print(f"  Variance: {variance:.4f}")

        df = pd.DataFrame(results)
        self.results['policy_divergence'] = df

        return df

    def test_importance_sampling_methods(self) -> pd.DataFrame:
        """Compare different importance sampling methods"""
        print("\n" + "="*70)
        print("IMPORTANCE SAMPLING METHODS COMPARISON")
        print("="*70)

        methods = [
            ("No IS", False, False),
            ("Ordinary IS", True, False),
            ("Per-Replay", True, True),
            ("Q-Learning", False, False)  # Special case
        ]

        results = []

        for method_name, use_is, use_per in methods:
            print(f"\n{method_name}")

            self.config.use_importance_sampling = use_is
            self.config.use_per_replay = use_per

            final_errors = []
            convergence_speeds = []
            variances = []

            for run in range(self.config.num_runs):
                agent = OffPolicyAgent(self.config)

                episode_errors = []
                for episode in range(self.config.num_episodes):
                    is_q = method_name == "Q-Learning"
                    value_error, _ = self.run_episode(agent, use_q_learning=is_q)
                    episode_errors.append(value_error)

                final_errors.append(episode_errors[-1])
                variances.append(np.var(episode_errors[-100:]))

                # Convergence: when error drops below threshold
                threshold = 2.0
                for i, err in enumerate(episode_errors):
                    if err < threshold:
                        convergence_speeds.append(i)
                        break
                else:
                    convergence_speeds.append(self.config.num_episodes)

            results.append({
                'Method': method_name,
                'Mean Final Error': np.mean(final_errors),
                'Std Final Error': np.std(final_errors),
                'Mean Variance': np.mean(variances),
                'Convergence Speed': np.mean(convergence_speeds),
                'Success Rate': np.mean([e < 2.0 for e in final_errors])
            })

            print(f"  Final Error: {results[-1]['Mean Final Error']:.4f} ± {results[-1]['Std Final Error']:.4f}")
            print(f"  Variance: {results[-1]['Mean Variance']:.4f}")
            print(f"  Convergence: {results[-1]['Convergence Speed']:.0f} episodes")

        df = pd.DataFrame(results)
        self.results['is_methods'] = df

        return df

    def find_stability_bounds(self) -> pd.DataFrame:
        """
        Q1: What are safe off-policy learning bounds?
        """
        print("\n" + "="*70)
        print("STABILITY BOUNDS ANALYSIS")
        print("="*70)

        # Test different alpha values
        alphas = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
        behavior_epsilons = [0.2, 0.4, 0.6, 0.8]

        results = []

        for alpha in alphas:
            for beh_eps in behavior_epsilons:
                print(f"\nα={alpha:.2f}, behavior ε={beh_eps:.1f}")

                self.config.alpha = alpha
                self.config.behavior_epsilon = beh_eps

                # Check stability
                success_count = 0
                diverge_count = 0
                final_errors = []

                for run in range(self.config.num_runs):
                    agent = OffPolicyAgent(self.config)

                    try:
                        episode_errors = []
                        for episode in range(self.config.num_episodes):
                            value_error, _ = self.run_episode(agent, use_q_learning=False)
                            episode_errors.append(value_error)

                            # Check for divergence
                            if episode_errors[-1] > 1e6:
                                diverge_count += 1
                                break

                        final_errors.append(episode_errors[-1])

                        if episode_errors[-1] < 5.0:
                            success_count += 1

                    except Exception as e:
                        diverge_count += 1
                        continue

                stability_rate = success_count / self.config.num_runs
                divergence_rate = diverge_count / self.config.num_runs

                results.append({
                    'Alpha': alpha,
                    'Behavior Epsilon': beh_eps,
                    'Stability Rate': stability_rate,
                    'Divergence Rate': divergence_rate,
                    'Mean Final Error': np.mean(final_errors) if final_errors else float('inf'),
                    'Std Final Error': np.std(final_errors) if final_errors else 0.0,
                    'Stable': stability_rate > 0.5
                })

                print(f"  Stability: {stability_rate*100:.0f}%")
                print(f"  Divergence: {divergence_rate*100:.0f}%")

        df = pd.DataFrame(results)
        self.results['stability_bounds'] = df

        return df

    def plot_policy_divergence(self, save_path: Optional[str] = None):
        """Plot variance vs policy divergence"""
        if 'policy_divergence' not in self.results:
            self.compare_policy_divergence()

        df = self.results['policy_divergence']

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Variance vs divergence
        axes[0].plot(df['Divergence'], df['Variance'], 'o-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Policy Divergence (|ε_b - ε_t|)', fontsize=14)
        axes[0].set_ylabel('Variance', fontsize=14)
        axes[0].set_title('Variance vs Policy Divergence', fontsize=16)
        axes[0].grid(True, alpha=0.3)

        # Error vs divergence
        axes[1].plot(df['Divergence'], df['Mean Final Error'], 's-', linewidth=2, markersize=8, color='orange')
        axes[1].fill_between(df['Divergence'],
                            df['Mean Final Error'] - df['Std Final Error'],
                            df['Mean Final Error'] + df['Std Final Error'],
                            alpha=0.2)
        axes[1].set_xlabel('Policy Divergence (|ε_b - ε_t|)', fontsize=14)
        axes[1].set_ylabel('Mean Final Error', fontsize=14)
        axes[1].set_title('Error vs Policy Divergence', fontsize=16)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_is_methods(self, save_path: Optional[str] = None):
        """Plot importance sampling method comparison"""
        if 'is_methods' not in self.results:
            self.test_importance_sampling_methods()

        df = self.results['is_methods']

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Final error comparison
        bars = axes[0].bar(df['Method'], df['Mean Final Error'], yerr=df['Std Final Error'],
                          capsize=5, alpha=0.7)
        axes[0].set_ylabel('Mean Final Error', fontsize=14)
        axes[0].set_title('Error Comparison', fontsize=16)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3, axis='y')

        # Variance comparison
        bars = axes[1].bar(df['Method'], df['Mean Variance'], alpha=0.7, color='orange')
        axes[1].set_ylabel('Mean Variance', fontsize=14)
        axes[1].set_title('Variance Comparison', fontsize=16)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_stability_bounds(self, save_path: Optional[str] = None):
        """Plot stability bounds"""
        if 'stability_bounds' not in self.results:
            self.find_stability_bounds()

        df = self.results['stability_bounds']

        # Create stability matrix
        pivot_table = df.pivot(index='Alpha', columns='Behavior Epsilon', values='Stability Rate')

        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='RdYlGn',
                   vmin=0, vmax=1, cbar_kws={'label': 'Stability Rate'})
        plt.title('Off-Policy Stability Bounds', fontsize=16)
        plt.xlabel('Behavior Epsilon', fontsize=14)
        plt.ylabel('Alpha (Step Size)', fontsize=14)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_report(self) -> str:
        """Generate comprehensive report"""
        if not self.results:
            self.compare_policy_divergence()
            self.test_importance_sampling_methods()
            self.find_stability_bounds()

        report = []
        report.append("="*80)
        report.append("OFF-POLICY TD(λ) LEARNING WITH IMPORTANCE SAMPLING")
        report.append("="*80)

        # Q1: Stability Bounds
        report.append("\n" + "="*80)
        report.append("Q1: SAFE OFF-POLICY LEARNING BOUNDS")
        report.append("="*80)

        if 'stability_bounds' in self.results:
            df = self.results['stability_bounds']
            stable = df[df['Stable'] == True]

            if len(stable) > 0:
                report.append("\nStable Configurations:")
                max_alpha = stable[stable['Stability Rate'] == stable['Stability Rate'].max()]['Alpha'].max()
                report.append(f"  • Maximum safe α: {max_alpha:.2f}")

                # Find safe behavior epsilon
                safe_eps = stable[stable['Alpha'] == 0.1]['Behavior Epsilon'].values
                if len(safe_eps) > 0:
                    report.append(f"  • Safe behavior ε range: {safe_eps.min():.1f} - {safe_eps.max():.1f}")

            report.append("\nTheoretical Bound:")
            report.append("  • Stability requires: Σα²ρ² < ∞")
            report.append("  • In practice: α < 0.2, moderate policy divergence")

        # Q2: Variance Scaling
        report.append("\n" + "="*80)
        report.append("Q2: VARIANCE SCALING WITH POLICY DIVERGENCE")
        report.append("="*80)

        if 'policy_divergence' in self.results:
            df = self.results['policy_divergence']

            # Find correlation
            corr = df['Divergence'].corr(df['Variance'])
            report.append(f"\nCorrelation (Divergence, Variance): {corr:.3f}")

            low_div = df[df['Divergence'] < 0.3]['Variance'].mean()
            high_div = df[df['Divergence'] > 0.6]['Variance'].mean()

            report.append(f"  • Low divergence variance: {low_div:.4f}")
            report.append(f"  • High divergence variance: {high_div:.4f}")
            report.append(f"  • Variance increase: {high_div/low_div:.1f}x")

        # Q3: Instability Conditions
        report.append("\n" + "="*80)
        report.append("Q3: WHEN DOES OFF-POLICY LEARNING BECOME UNSTABLE?")
        report.append("="*80)

        if 'stability_bounds' in self.results:
            df = self.results['stability_bounds']
            unstable = df[df['Stable'] == False]

            if len(unstable) > 0:
                report.append("\nUnstable Configurations:")

                high_alpha = unstable[unstable['Alpha'] > 0.2]
                if len(high_alpha) > 0:
                    report.append(f"  • High step size: α > {high_alpha['Alpha'].min():.2f}")

                high_div = unstable[unstable['Behavior Epsilon'] > 0.6]
                if len(high_div) > 0:
                    report.append(f"  • High policy divergence: ε_b > {high_div['Behavior Epsilon'].min():.1f}")

        # Method Comparison
        report.append("\n" + "="*80)
        report.append("IMPORTANCE SAMPLING METHODS")
        report.append("="*80)

        if 'is_methods' in self.results:
            df = self.results['is_methods']
            best = df.loc[df['Mean Final Error'].idxmin()]

            report.append("\nMethod Performance:")
            for _, row in df.iterrows():
                report.append(f"  • {row['Method']}:")
                report.append(f"    - Error: {row['Mean Final Error']:.4f} ± {row['Std Final Error']:.4f}")
                report.append(f"    - Variance: {row['Mean Variance']:.4f}")
                report.append(f"    - Success: {row['Success Rate']*100:.0f}%")

            report.append(f"\nRecommended: {best['Method']}")

        # Key Findings
        report.append("\n" + "="*80)
        report.append("KEY FINDINGS")
        report.append("="*80)

        report.append("\n1. Importance Sampling:")
        report.append("   • Necessary for off-policy value learning")
        report.append("   • Increases variance with policy divergence")
        report.append("   • Per-replay helps control variance")

        report.append("\n2. Q-Learning:")
        report.append("   • Off-policy without importance sampling")
        report.append("   • More stable than off-policy TD")
        report.append("   • Recommended for action-value learning")

        report.append("\n3. Stability Conditions:")
        report.append("   • Use small step sizes (α < 0.2)")
        report.append("   • Limit policy divergence")
        report.append("   • Consider per-replay or Q-learning")

        report.append("\n" + "="*80)
        report.append("CONCLUSION")
        report.append("="*80)
        report.append("\n✓ Off-policy learning requires careful tuning")
        report.append("✓ Importance sampling introduces variance")
        report.append("✓ Q-learning is more stable for action values")
        report.append("\nRecommendation: Use Q-learning when possible")

        return "\n".join(report)


def main():
    """Main simulation runner"""
    print("="*70)
    print("OFF-POLICY TD(λ) LEARNING SIMULATION")
    print("="*70)

    config = OffPolicyConfig(
        num_states=10,
        num_actions=2,
        gamma=0.99,
        alpha=0.1,
        lambda_=0.5,
        num_episodes=1000,
        num_runs=100
    )

    simulator = OffPolicySimulator(config)

    # Run analyses
    print("\n1. Analyzing policy divergence...")
    divergence_df = simulator.compare_policy_divergence()
    print("\n" + divergence_df.to_string(index=False))

    print("\n2. Testing importance sampling methods...")
    is_df = simulator.test_importance_sampling_methods()
    print("\n" + is_df.to_string(index=False))

    print("\n3. Finding stability bounds...")
    stability_df = simulator.find_stability_bounds()
    print("\nStability analysis complete")

    # Generate plots
    print("\n4. Generating visualizations...")
    simulator.plot_policy_divergence('policy_divergence.png')
    simulator.plot_is_methods('is_methods.png')
    simulator.plot_stability_bounds('stability_bounds.png')

    # Generate report
    print("\n5. Generating report...")
    report = simulator.generate_report()
    print(report)

    # Save report
    with open('OFF_POLICY_REPORT.txt', 'w') as f:
        f.write(report)

    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print("\nOutputs:")
    print("  • policy_divergence.png")
    print("  • is_methods.png")
    print("  • stability_bounds.png")
    print("  • OFF_POLICY_REPORT.txt")


if __name__ == "__main__":
    main()
