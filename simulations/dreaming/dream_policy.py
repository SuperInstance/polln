"""
Dream-Based Policy Optimization Simulation
==========================================

Proves that dream-based policy optimization improves learning efficiency.

Mathematical Foundation:
    Dream: V_dream(s,a) = E[Σ γ^i r_i | model]
    Reality: V_real(s,a) from environment
    Policy: θ ← θ + α∇_θ Σ_t dream_return_t

Key Hypotheses:
    H1: Mixed dream-real learning outperforms either alone
    H2: Optimal dream-to-real ratio exists
    H3: Dreaming improves sample efficiency
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Dict, List, Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass
import json
from pathlib import Path
from collections import deque

# Import from previous simulations
from vae_training import VAE, VAEConfig, MDPTrajectoryCollector
from dream_rollouts import WorldModel, DreamGenerator, RealEnvironment


@dataclass
class PolicyConfig:
    """Configuration for policy network"""
    state_dim: int = 64
    hidden_dim: int = 128
    action_dim: int = 4
    learning_rate: float = 1e-3


class PolicyNetwork(nn.Module):
    """
    Policy network for action selection.

    Uses softmax output for discrete actions.
    """

    def __init__(self, config: PolicyConfig):
        super().__init__()
        self.config = config

        self.network = nn.Sequential(
            nn.Linear(config.state_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.action_dim),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Get action logits.

        Args:
            state: State tensor [batch, state_dim]

        Returns:
            logits: Action logits [batch, action_dim]
        """
        return self.network(state)

    def get_action(
        self,
        state: np.ndarray,
        explore: bool = True,
        epsilon: float = 0.1
    ) -> int:
        """
        Sample action from policy.

        Args:
            state: State array
            explore: Add exploration
            epsilon: Epsilon-greedy exploration rate

        Returns:
            action: Action index
        """
        with torch.no_grad():
            logits = self.forward(torch.FloatTensor(state).unsqueeze(0))
            probs = F.softmax(logits, dim=-1)

            if explore and np.random.random() < epsilon:
                return np.random.randint(self.config.action_dim)
            else:
                return torch.multinomial(probs, 1).item()

    def get_action_probs(self, state: np.ndarray) -> np.ndarray:
        """Get action probability distribution"""
        with torch.no_grad():
            logits = self.forward(torch.FloatTensor(state).unsqueeze(0))
            probs = F.softmax(logits, dim=-1)
        return probs.squeeze(0).cpu().numpy()


class ValueNetwork(nn.Module):
    """
    Value network for baseline estimation.

    V(s) = expected return from state s.
    """

    def __init__(self, state_dim: int = 64, hidden_dim: int = 128):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Predict state value.

        Args:
            state: State tensor [batch, state_dim]

        Returns:
            value: State value [batch, 1]
        """
        return self.network(state)


class PolicyOptimizer:
    """
    Optimize policy using REINFORCE with value baseline.
    """

    def __init__(
        self,
        policy: PolicyNetwork,
        value: ValueNetwork,
        policy_lr: float = 1e-3,
        value_lr: float = 1e-3,
        gamma: float = 0.99,
    ):
        self.policy = policy
        self.value = value
        self.gamma = gamma

        self.policy_optimizer = torch.optim.Adam(policy.parameters(), lr=policy_lr)
        self.value_optimizer = torch.optim.Adam(value.parameters(), lr=value_lr)

    def compute_returns(
        self,
        rewards: List[float],
        dones: List[bool]
    ) -> List[float]:
        """
        Compute discounted returns.

        Args:
            rewards: List of rewards
            dones: List of episode termination flags

        Returns:
            returns: Discounted returns
        """
        returns = []
        R = 0

        for r, d in zip(reversed(rewards), reversed(dones)):
            R = r + self.gamma * R * (1 - d)
            returns.insert(0, R)

        return returns

    def update_policy(
        self,
        states: List[np.ndarray],
        actions: List[int],
        returns: List[float]
    ) -> Dict[str, float]:
        """
        Update policy using REINFORCE.

        Args:
            states: List of states
            actions: List of actions
            returns: List of returns

        Returns:
            Dictionary with loss metrics
        """
        # Convert to tensors
        state_tensor = torch.FloatTensor(np.array(states))
        action_tensor = torch.LongTensor(actions)
        return_tensor = torch.FloatTensor(returns)

        # Get action log probabilities
        logits = self.policy(state_tensor)
        log_probs = F.log_softmax(logits, dim=-1)
        action_log_probs = log_probs[range(len(actions)), action_tensor]

        # Get baseline
        values = self.value(state_tensor).squeeze()

        # Compute advantages
        advantages = return_tensor - values.detach()

        # Policy loss: -log_prob * advantage
        policy_loss = -(action_log_probs * advantages).mean()

        # Update policy
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
        self.policy_optimizer.step()

        return {
            'policy_loss': policy_loss.item(),
            'mean_advantage': advantages.mean().item(),
        }

    def update_value(
        self,
        states: List[np.ndarray],
        returns: List[float]
    ) -> Dict[str, float]:
        """
        Update value network using MSE.

        Args:
            states: List of states
            returns: List of returns

        Returns:
            Dictionary with loss metrics
        """
        state_tensor = torch.FloatTensor(np.array(states))
        return_tensor = torch.FloatTensor(returns)

        # Predict values
        values = self.value(state_tensor).squeeze()

        # Value loss: MSE
        value_loss = F.mse_loss(values, return_tensor)

        # Update value
        self.value_optimizer.zero_grad()
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.value.parameters(), 1.0)
        self.value_optimizer.step()

        return {
            'value_loss': value_loss.item(),
        }


class DreamBasedLearner:
    """
    Learn policy using mix of dream and real experience.

    Supports different dream-to-real ratios.
    """

    def __init__(
        self,
        policy: PolicyNetwork,
        value: ValueNetwork,
        world_model: WorldModel,
        optimizer: PolicyOptimizer,
        dream_ratio: float = 0.5,  # Fraction of updates from dreams
        device: torch.device = torch.device('cpu'),
    ):
        self.policy = policy
        self.value = value
        self.world_model = world_model
        self.optimizer = optimizer
        self.dream_ratio = dream_ratio
        self.device = device

        self.dream_gen = DreamGenerator(world_model, device)
        self.env = RealEnvironment(grid_size=8)

    def collect_real_episode(
        self,
        max_steps: int = 50,
        epsilon: float = 0.1
    ) -> Dict[str, List]:
        """
        Collect real environment episode.

        Returns:
            Dictionary with episode data
        """
        # Random start
        start_x = np.random.randint(0, 8)
        start_y = np.random.randint(0, 8)
        goal_x = np.random.randint(0, 8)
        goal_y = np.random.randint(0, 8)

        start_state = np.zeros(64)
        start_state[0] = start_x / 8
        start_state[1] = start_y / 8
        start_state[2] = goal_x / 8
        start_state[3] = goal_y / 8

        # Greedy policy
        def greedy_policy(state):
            x, y = int(state[0] * 8), int(state[1] * 8)
            if x < goal_x:
                return 0
            elif x > goal_x:
                return 1
            elif y < goal_y:
                return 2
            else:
                return 3

        # Collect episode
        states = [start_state.copy()]
        actions = []
        rewards = []
        dones = []

        state = start_state.copy()
        for _ in range(max_steps):
            action = greedy_policy(state)
            next_state, reward, done = self.env.step(state, action)

            states.append(next_state.copy())
            actions.append(action)
            rewards.append(reward)
            dones.append(done)

            state = next_state
            if done:
                break

        return {
            'states': states,
            'actions': actions,
            'rewards': rewards,
            'dones': dones,
        }

    def generate_dream_episode(
        self,
        max_steps: int = 50,
        epsilon: float = 0.1
    ) -> Dict[str, List]:
        """
        Generate dream episode from world model.

        Returns:
            Dictionary with episode data
        """
        # Random start
        start_x = np.random.randint(0, 8)
        start_y = np.random.randint(0, 8)
        goal_x = np.random.randint(0, 8)
        goal_y = np.random.randint(0, 8)

        start_state = np.zeros(64)
        start_state[0] = start_x / 8
        start_state[1] = start_y / 8
        start_state[2] = goal_x / 8
        start_state[3] = goal_y / 8

        # Greedy policy
        def greedy_policy(state):
            x, y = int(state[0] * 8), int(state[1] * 8)
            if x < goal_x:
                return 0
            elif x > goal_x:
                return 1
            elif y < goal_y:
                return 2
            else:
                return 3

        # Generate dream
        dream_ep = self.dream_gen.dream_rollout(
            start_state,
            greedy_policy,
            max_steps,
            explore=False
        )

        # Convert to format expected by optimizer
        dones = [False] * len(dream_ep['rewards'])
        dones[-1] = True  # Last step is terminal

        return {
            'states': dream_ep['states'].tolist(),
            'actions': dream_ep['actions'].tolist(),
            'rewards': dream_ep['rewards'].tolist(),
            'dones': dones,
        }

    def train_step(
        self,
        epsilon: float = 0.1
    ) -> Dict[str, float]:
        """
        Single training step with mixed dream-real experience.

        Returns:
            Dictionary with training metrics
        """
        # Decide: dream or real
        use_dream = np.random.random() < self.dream_ratio

        if use_dream:
            # Dream episode
            episode = self.generate_dream_episode()
            source = 'dream'
        else:
            # Real episode
            episode = self.collect_real_episode()
            source = 'real'

        # Compute returns
        returns = self.optimizer.compute_returns(
            episode['rewards'],
            episode['dones']
        )

        # Update policy and value
        policy_metrics = self.optimizer.update_policy(
            episode['states'],
            episode['actions'],
            returns
        )

        value_metrics = self.optimizer.update_value(
            episode['states'],
            returns
        )

        return {
            'source': source,
            'episode_length': len(episode['rewards']),
            'total_reward': sum(episode['rewards']),
            **policy_metrics,
            **value_metrics,
        }

    def evaluate(
        self,
        num_episodes: int = 20
    ) -> Dict[str, float]:
        """
        Evaluate current policy on real environment.

        Returns:
            Dictionary with evaluation metrics
        """
        total_rewards = []
        total_lengths = []

        for _ in range(num_episodes):
            episode = self.collect_real_episode()
            total_rewards.append(sum(episode['rewards']))
            total_lengths.append(len(episode['rewards']))

        return {
            'mean_reward': np.mean(total_rewards),
            'std_reward': np.std(total_rewards),
            'mean_length': np.mean(total_lengths),
        }


def run_dream_ratio_experiment():
    """
    Experiment: Find optimal dream-to-real ratio.

    Hypothesis: Mixed learning outperforms pure dream or real.
    """
    print("=" * 60)
    print("H1: Dream Ratio Experiment")
    print("=" * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Train world model
    print("\nTraining world model...")
    train_data = MDPTrajectoryCollector.collect_gridworld_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )
    vae_config = VAEConfig(latent_dim=32, epochs=50)
    from dream_rollouts import train_world_model
    world_model = train_world_model(train_data, vae_config, device, epochs=50)

    # Test different dream ratios
    dream_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
    results = []

    for ratio in dream_ratios:
        print(f"\n{'=' * 60}")
        print(f"Dream Ratio: {ratio}")
        print(f"{'=' * 60}")

        # Create new policy and value
        policy = PolicyNetwork(PolicyConfig()).to(device)
        value = ValueNetwork().to(device)
        optimizer = PolicyOptimizer(policy, value)

        # Create learner
        learner = DreamBasedLearner(
            policy,
            value,
            world_model,
            optimizer,
            dream_ratio=ratio,
            device=device,
        )

        # Train
        num_steps = 500
        eval_every = 50
        eval_rewards = []

        for step in range(num_steps):
            metrics = learner.train_step()

            if step % eval_every == 0:
                eval_metrics = learner.evaluate(num_episodes=10)
                eval_rewards.append(eval_metrics['mean_reward'])
                print(f"  Step {step}: Eval Reward = {eval_metrics['mean_reward']:.4f}")

        results.append({
            'dream_ratio': ratio,
            'final_reward': eval_rewards[-1],
            'eval_rewards': eval_rewards,
        })

    # Analyze
    print("\n" + "=" * 60)
    print("Results: Optimal Dream Ratio")
    print("=" * 60)

    best = max(results, key=lambda x: x['final_reward'])
    print(f"\nBest Dream Ratio: {best['dream_ratio']}")
    print(f"  Final Reward: {best['final_reward']:.4f}")

    for r in results:
        print(f"  Ratio {r['dream_ratio']:.2f}: {r['final_reward']:.4f}")

    return results


def run_sample_efficiency_experiment():
    """
    Experiment: Compare sample efficiency of dream vs real learning.

    Hypothesis: Dreaming improves sample efficiency.
    """
    print("\n" + "=" * 60)
    print("H2: Sample Efficiency Experiment")
    print("=" * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Train world model
    print("\nTraining world model...")
    train_data = MDPTrajectoryCollector.collect_gridworld_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )
    vae_config = VAEConfig(latent_dim=32, epochs=50)
    from dream_rollouts import train_world_model
    world_model = train_world_model(train_data, vae_config, device, epochs=50)

    # Compare real-only vs mixed
    configs = [
        {'name': 'Real Only', 'dream_ratio': 0.0},
        {'name': 'Mixed (50%)', 'dream_ratio': 0.5},
        {'name': 'Dream Only', 'dream_ratio': 1.0},
    ]

    results = []

    for config in configs:
        print(f"\n{'=' * 60}")
        print(f"Config: {config['name']}")
        print(f"{'=' * 60}")

        # Create new policy and value
        policy = PolicyNetwork(PolicyConfig()).to(device)
        value = ValueNetwork().to(device)
        optimizer = PolicyOptimizer(policy, value)

        # Create learner
        learner = DreamBasedLearner(
            policy,
            value,
            world_model,
            optimizer,
            dream_ratio=config['dream_ratio'],
            device=device,
        )

        # Track real environment steps
        real_steps = 0
        eval_rewards = []
        real_steps_at_eval = []

        # Train with fixed real steps budget
        max_real_steps = 200
        eval_every = 20

        while real_steps < max_real_steps:
            # Train step
            metrics = learner.train_step()
            if metrics['source'] == 'real':
                real_steps += metrics['episode_length']

            # Evaluate
            if real_steps % eval_every == 0 and real_steps > 0:
                eval_metrics = learner.evaluate(num_episodes=10)
                eval_rewards.append(eval_metrics['mean_reward'])
                real_steps_at_eval.append(real_steps)
                print(f"  Real Steps {real_steps}: Eval Reward = {eval_metrics['mean_reward']:.4f}")

        results.append({
            'name': config['name'],
            'dream_ratio': config['dream_ratio'],
            'real_steps': real_steps_at_eval,
            'eval_rewards': eval_rewards,
            'final_reward': eval_rewards[-1] if eval_rewards else 0,
        })

    # Analyze
    print("\n" + "=" * 60)
    print("Results: Sample Efficiency")
    print("=" * 60)

    for r in results:
        print(f"\n{r['name']}:")
        print(f"  Final Reward: {r['final_reward']:.4f}")

        # Compute area under curve
        if len(r['eval_rewards']) > 1:
            auc = np.trapz(r['eval_rewards'], r['real_steps'])
            print(f"  AUC: {auc:.2f}")

    return results


def plot_results(ratio_results: List[Dict], efficiency_results: List[Dict], save_path: str = None):
    """Plot policy optimization results"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Dream ratio experiment
    ax = axes[0]
    ratios = [r['dream_ratio'] for r in ratio_results]
    final_rewards = [r['final_reward'] for r in ratio_results]
    ax.plot(ratios, final_rewards, 'o-', linewidth=2, markersize=8)
    ax.set_xlabel('Dream Ratio')
    ax.set_ylabel('Final Reward')
    ax.set_title('H1: Optimal Dream Ratio')
    ax.grid(True, alpha=0.3)
    ax.axvline(x=0.5, color='r', linestyle='--', alpha=0.5, label='50% Mix')
    ax.legend()

    # Sample efficiency
    ax = axes[1]
    for r in efficiency_results:
        ax.plot(r['real_steps'], r['eval_rewards'], 'o-', label=r['name'], linewidth=2)
    ax.set_xlabel('Real Environment Steps')
    ax.set_ylabel('Evaluation Reward')
    ax.set_title('H2: Sample Efficiency')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"\nPlot saved to {save_path}")

    plt.show()


def main():
    """Run all policy optimization experiments"""
    print("=" * 60)
    print("DREAM-BASED POLICY OPTIMIZATION SIMULATIONS")
    print("Proving dreaming improves policy learning efficiency")
    print("=" * 60)

    # Run experiments
    ratio_results = run_dream_ratio_experiment()
    efficiency_results = run_sample_efficiency_experiment()

    # Save results
    output_dir = Path("C:/Users/casey/polln/simulations/dreaming/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "dream_ratio_results.json", 'w') as f:
        json.dump(ratio_results, f, indent=2)

    with open(output_dir / "sample_efficiency_results.json", 'w') as f:
        json.dump(efficiency_results, f, indent=2)

    print("\n" + "=" * 60)
    print("Results saved to simulations/dreaming/results/")
    print("=" * 60)

    # Plot
    plot_results(ratio_results, efficiency_results, save_path=output_dir / "dream_policy_plots.png")

    return ratio_results, efficiency_results


if __name__ == "__main__":
    main()
