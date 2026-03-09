"""
Model-Based RL Simulation
==========================

Compare different model-based RL approaches: MPC, Dyna, Dreamer, PLANET.

Mathematical Foundation:
    MPC: π(s) = argmax_a Σ dream_return(s, a)
    Dyna: Real + Dream interleaved
    Dreamer: Latent imagination with value prediction
    PLANET: Trajectory sampling with posterior inference

Key Hypotheses:
    H1: Model-based methods improve sample efficiency
    H2: Dreaming is most beneficial in sample-limited settings
    H3: Trade-off between computation and sample efficiency
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
from copy import deepcopy

# Import from previous simulations
from vae_training import VAE, VAEConfig, MDPTrajectoryCollector
from dream_rollouts import WorldModel, DreamGenerator, RealEnvironment


@dataclass
class MBRLConfig:
    """Configuration for model-based RL"""
    latent_dim: int = 32
    hidden_dim: int = 128
    action_dim: int = 4
    planning_horizon: int = 10
    num_particles: int = 10
    learning_rate: float = 1e-3
    gamma: float = 0.99


class MPlanner:
    """
    Model Predictive Control (MPC) Planner.

    Plans by optimizing actions through dream rollouts.
    """

    def __init__(
        self,
        world_model: WorldModel,
        horizon: int = 10,
        num_candidates: int = 10
    ):
        self.world_model = world_model
        self.horizon = horizon
        self.num_candidates = num_candidates

    def plan(
        self,
        state: np.ndarray,
        device: torch.device
    ) -> int:
        """
        Plan action using MPC.

        Args:
            state: Current state
            device: Torch device

        Returns:
            action: Best action
        """
        self.world_model.eval()

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
            mean, log_var = self.world_model.encode(state_tensor)
            latent = self.world_model.vae.reparameterize(mean, log_var)

            best_action = 0
            best_return = -float('inf')

            # Try each action
            for action in range(4):
                returns = []

                # Sample multiple trajectories
                for _ in range(self.num_candidates):
                    total_reward = 0
                    current_latent = latent.clone()
                    hidden = None

                    # Rollout
                    for _ in range(self.horizon):
                        action_tensor = torch.LongTensor([action]).to(device)
                        next_latent, reward, hidden = self.world_model.predict(
                            current_latent, action_tensor, hidden
                        )
                        total_reward += reward.item()
                        current_latent = next_latent

                    returns.append(total_reward)

                # Average return
                avg_return = np.mean(returns)
                if avg_return > best_return:
                    best_return = avg_return
                    best_action = action

        return best_action


class DynaAgent:
    """
    Dyna-style agent: interleaves real and simulated experience.

    Updates model and policy using both real and dream data.
    """

    def __init__(
        self,
        world_model: WorldModel,
        policy: nn.Module,
        value: nn.Module,
        dream_steps_per_real: int = 5,
        device: torch.device = torch.device('cpu')
    ):
        self.world_model = world_model
        self.policy = policy
        self.value = value
        self.dream_steps_per_real = dream_steps_per_real
        self.device = device

        self.dream_gen = DreamGenerator(world_model, device)
        self.env = RealEnvironment(grid_size=8)

        # Optimizers
        self.policy_optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)
        self.value_optimizer = torch.optim.Adam(value.parameters(), lr=1e-3)

        # Experience buffer
        self.real_buffer = []

    def collect_real_step(
        self,
        state: np.ndarray,
        epsilon: float = 0.1
    ) -> Tuple[np.ndarray, float, bool, int]:
        """Take real environment step"""
        # Epsilon-greedy
        if np.random.random() < epsilon:
            action = np.random.randint(4)
        else:
            with torch.no_grad():
                logits = self.policy(torch.FloatTensor(state).unsqueeze(0).to(self.device))
                probs = F.softmax(logits, dim=-1)
                action = torch.multinomial(probs, 1).item()

        next_state, reward, done = self.env.step(state, action)
        return next_state, reward, done, action

    def dream_step(self, state: np.ndarray) -> Tuple[np.ndarray, float, int]:
        """Generate dream step"""
        # Random action
        action = np.random.randint(4)

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            mean, log_var = self.world_model.encode(state_tensor)
            latent = self.world_model.vae.reparameterize(mean, log_var)

            action_tensor = torch.LongTensor([action]).to(self.device)
            next_latent, reward, _ = self.world_model.predict(latent, action_tensor)

            next_state = self.world_model.decode(next_latent)

        return next_state.cpu().squeeze(0).numpy(), reward.item(), action

    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """Update policy and value from transition"""
        # Convert to tensors
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
        action_tensor = torch.LongTensor([action]).to(self.device)
        reward_tensor = torch.FloatTensor([reward]).to(self.device)

        # Compute target value
        with torch.no_grad():
            next_value = self.value(next_state_tensor)
            target = reward_tensor + self.gamma * next_value * (1 - done)

        # Update value
        value_pred = self.value(state_tensor)
        value_loss = F.mse_loss(value_pred, target)

        self.value_optimizer.zero_grad()
        value_loss.backward()
        self.value_optimizer.step()

        # Update policy (REINFORCE style)
        logits = self.policy(state_tensor)
        log_probs = F.log_softmax(logits, dim=-1)
        action_log_prob = log_probs[0, action]

        # Advantage
        advantage = (target - value_pred.detach()).squeeze()

        policy_loss = -action_log_prob * advantage

        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        self.policy_optimizer.step()

        return {
            'value_loss': value_loss.item(),
            'policy_loss': policy_loss.item(),
            'advantage': advantage.item(),
        }

    def train_episode(
        self,
        max_steps: int = 50,
        epsilon: float = 0.1
    ) -> Dict[str, float]:
        """Train for one episode with mixed real/dream experience"""
        # Initialize state
        start_x = np.random.randint(0, 8)
        start_y = np.random.randint(0, 8)
        goal_x = np.random.randint(0, 8)
        goal_y = np.random.randint(0, 8)

        state = np.zeros(64)
        state[0] = start_x / 8
        state[1] = start_y / 8
        state[2] = goal_x / 8
        state[3] = goal_y / 8

        total_reward = 0
        real_steps = 0

        for step in range(max_steps):
            # Real step
            next_state, reward, done, action = self.collect_real_step(state, epsilon)
            metrics = self.update(state, action, reward, next_state, done)

            total_reward += reward
            real_steps += 1

            # Dream steps
            for _ in range(self.dream_steps_per_real):
                dream_next_state, dream_reward, dream_action = self.dream_step(state)
                self.update(state, dream_action, dream_reward, dream_next_state, False)

            state = next_state
            if done:
                break

        return {
            'total_reward': total_reward,
            'episode_length': real_steps,
        }


class DreamerAgent:
    """
    Dreamer-style agent: learns in latent imagination space.

    Key features:
    - Predicts values in latent space
    - Optimizes policy through imagination rollouts
    """

    def __init__(
        self,
        world_model: WorldModel,
        policy: nn.Module,
        value: nn.Module,
        imagination_horizon: int = 15,
        device: torch.device = torch.device('cpu')
    ):
        self.world_model = world_model
        self.policy = policy
        self.value = value
        self.imagination_horizon = imagination_horizon
        self.device = device

        self.dream_gen = DreamGenerator(world_model, device)
        self.env = RealEnvironment(grid_size=8)

        # Optimizers
        self.policy_optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)
        self.value_optimizer = torch.optim.Adam(value.parameters(), lr=1e-3)

    def imagine_rollout(
        self,
        start_state: np.ndarray
    ) -> List[Dict]:
        """
        Generate imagination rollout from starting state.

        Returns:
            List of transition dictionaries
        """
        rollout = []

        with torch.no_grad():
            state_tensor = torch.FloatTensor(start_state).unsqueeze(0).to(self.device)
            mean, log_var = self.world_model.encode(state_tensor)
            latent = self.world_model.vae.reparameterize(mean, log_var)

            hidden = None

            for _ in range(self.imagination_horizon):
                # Get action from policy
                logits = self.policy(latent)
                probs = F.softmax(logits, dim=-1)
                action = torch.multinomial(probs, 1).item()

                # Predict next state
                action_tensor = torch.LongTensor([action]).to(self.device)
                next_latent, reward, hidden = self.world_model.predict(
                    latent, action_tensor, hidden
                )

                # Get value estimate
                value = self.value(next_latent)

                rollout.append({
                    'state': latent.cpu().squeeze(0).numpy(),
                    'action': action,
                    'reward': reward.item(),
                    'next_state': next_latent.cpu().squeeze(0).numpy(),
                    'value': value.item(),
                })

                latent = next_latent

        return rollout

    def update_from_imagination(
        self,
        rollout: List[Dict],
        gamma: float = 0.99
    ) -> Dict[str, float]:
        """Update policy and value from imagination rollout"""
        # Compute lambda returns
        returns = []
        values = [t['value'] for t in rollout]

        for i in range(len(rollout)):
            # Bootstrapped return
            R = rollout[i]['reward']
            if i < len(rollout) - 1:
                R += gamma * values[i + 1]
            returns.append(R)

        # Update value
        states = torch.FloatTensor(np.array([t['state'] for t in rollout])).to(self.device)
        returns_tensor = torch.FloatTensor(returns).unsqueeze(1).to(self.device)

        value_preds = self.value(states)
        value_loss = F.mse_loss(value_preds, returns_tensor)

        self.value_optimizer.zero_grad()
        value_loss.backward()
        self.value_optimizer.step()

        # Update policy
        actions = torch.LongTensor([t['action'] for t in rollout]).to(self.device)

        logits = self.policy(states)
        log_probs = F.log_softmax(logits, dim=-1)
        action_log_probs = log_probs[range(len(actions)), actions]

        advantages = (returns_tensor - value_preds.detach()).squeeze()
        policy_loss = -(action_log_probs * advantages).mean()

        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        self.policy_optimizer.step()

        return {
            'value_loss': value_loss.item(),
            'policy_loss': policy_loss.item(),
        }

    def train_episode(
        self,
        max_steps: int = 50,
        epsilon: float = 0.1
    ) -> Dict[str, float]:
        """Train for one episode"""
        # Initialize state
        start_x = np.random.randint(0, 8)
        start_y = np.random.randint(0, 8)
        goal_x = np.random.randint(0, 8)
        goal_y = np.random.randint(0, 8)

        state = np.zeros(64)
        state[0] = start_x / 8
        state[1] = start_y / 8
        state[2] = goal_x / 8
        state[3] = goal_y / 8

        total_reward = 0

        for step in range(max_steps):
            # Imagine rollout
            rollout = self.imagine_rollout(state)

            # Update from imagination
            metrics = self.update_from_imagination(rollout)

            # Real step
            if np.random.random() < epsilon:
                action = np.random.randint(4)
            else:
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                    logits = self.policy(state_tensor)
                    probs = F.softmax(logits, dim=-1)
                    action = torch.multinomial(probs, 1).item()

            next_state, reward, done = self.env.step(state, action)
            total_reward += reward

            state = next_state
            if done:
                break

        return {
            'total_reward': total_reward,
            'episode_length': step + 1,
        }


class PLANETAgent:
    """
    PLANET-style agent: trajectory sampling with posterior inference.

    Simplified implementation focusing on key ideas.
    """

    def __init__(
        self,
        world_model: WorldModel,
        policy: nn.Module,
        value: nn.Module,
        num_trajectories: int = 10,
        trajectory_horizon: int = 20,
        device: torch.device = torch.device('cpu')
    ):
        self.world_model = world_model
        self.policy = policy
        self.value = value
        self.num_trajectories = num_trajectories
        self.trajectory_horizon = trajectory_horizon
        self.device = device

        self.dream_gen = DreamGenerator(world_model, device)
        self.env = RealEnvironment(grid_size=8)

    def sample_trajectories(
        self,
        start_state: np.ndarray
    ) -> List[List[Dict]]:
        """Sample multiple action trajectories"""
        trajectories = []

        for _ in range(self.num_trajectories):
            traj = []

            with torch.no_grad():
                state_tensor = torch.FloatTensor(start_state).unsqueeze(0).to(self.device)
                mean, log_var = self.world_model.encode(state_tensor)
                latent = self.world_model.vae.reparameterize(mean, log_var)

                hidden = None

                for _ in range(self.trajectory_horizon):
                    # Random action (explore)
                    action = np.random.randint(4)

                    # Predict
                    action_tensor = torch.LongTensor([action]).to(self.device)
                    next_latent, reward, hidden = self.world_model.predict(
                        latent, action_tensor, hidden
                    )

                    traj.append({
                        'state': latent.cpu().squeeze(0).numpy(),
                        'action': action,
                        'reward': reward.item(),
                    })

                    latent = next_latent

            trajectories.append(traj)

        return trajectories

    def select_best_trajectory(
        self,
        trajectories: List[List[Dict]]
    ) -> int:
        """Select best trajectory using total reward"""
        best_idx = 0
        best_reward = -float('inf')

        for i, traj in enumerate(trajectories):
            total_reward = sum(t['reward'] for t in traj)
            if total_reward > best_reward:
                best_reward = total_reward
                best_idx = i

        return best_idx

    def train_episode(
        self,
        max_steps: int = 50,
        epsilon: float = 0.1
    ) -> Dict[str, float]:
        """Train for one episode"""
        # Initialize state
        start_x = np.random.randint(0, 8)
        start_y = np.random.randint(0, 8)
        goal_x = np.random.randint(0, 8)
        goal_y = np.random.randint(0, 8)

        state = np.zeros(64)
        state[0] = start_x / 8
        state[1] = start_y / 8
        state[2] = goal_x / 8
        state[3] = goal_y / 8

        total_reward = 0

        for step in range(max_steps):
            # Sample trajectories
            trajectories = self.sample_trajectories(state)

            # Select best trajectory
            best_idx = self.select_best_trajectory(trajectories)

            # Execute first action of best trajectory
            action = trajectories[best_idx][0]['action']

            # Real step
            next_state, reward, done = self.env.step(state, action)
            total_reward += reward

            state = next_state
            if done:
                break

        return {
            'total_reward': total_reward,
            'episode_length': step + 1,
        }


def run_mbrl_comparison():
    """
    Compare MPC, Dyna, Dreamer, PLANET.

    Hypothesis: Model-based methods improve sample efficiency.
    """
    print("=" * 60)
    print("Model-Based RL Comparison")
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

    # Define agents
    agent_configs = [
        {'name': 'MPC', 'type': 'mpc'},
        {'name': 'Dyna', 'type': 'dyna'},
        {'name': 'Dreamer', 'type': 'dreamer'},
        {'name': 'PLANET', 'type': 'planet'},
    ]

    results = []

    for config in agent_configs:
        print(f"\n{'=' * 60}")
        print(f"Agent: {config['name']}")
        print(f"{'=' * 60}")

        # Create policy and value
        from dream_policy import PolicyNetwork, PolicyConfig, ValueNetwork
        policy = PolicyNetwork(PolicyConfig()).to(device)
        value = ValueNetwork().to(device)

        # Create agent
        if config['type'] == 'mpc':
            agent = MPlanner(world_model, horizon=10, num_candidates=10)
        elif config['type'] == 'dyna':
            agent = DynaAgent(world_model, policy, value, dream_steps_per_real=5, device=device)
        elif config['type'] == 'dreamer':
            agent = DreamerAgent(world_model, policy, value, imagination_horizon=15, device=device)
        else:  # planet
            agent = PLANETAgent(world_model, policy, value, num_trajectories=10, device=device)

        # Evaluate
        num_episodes = 50
        episode_rewards = []

        for ep in range(num_episodes):
            if config['type'] == 'mpc':
                # MPC needs special handling
                start_x = np.random.randint(0, 8)
                start_y = np.random.randint(0, 8)
                goal_x = np.random.randint(0, 8)
                goal_y = np.random.randint(0, 8)

                state = np.zeros(64)
                state[0] = start_x / 8
                state[1] = start_y / 8
                state[2] = goal_x / 8
                state[3] = goal_y / 8

                total_reward = 0
                env = RealEnvironment(grid_size=8)

                for _ in range(50):
                    action = agent.plan(state, device)
                    next_state, reward, done = env.step(state, action)
                    total_reward += reward
                    state = next_state
                    if done:
                        break

                episode_rewards.append(total_reward)

            else:
                metrics = agent.train_episode(max_steps=50, epsilon=0.1)
                episode_rewards.append(metrics['total_reward'])

            if (ep + 1) % 10 == 0:
                avg_reward = np.mean(episode_rewards[-10:])
                print(f"  Episode {ep+1}: Avg Reward = {avg_reward:.4f}")

        results.append({
            'name': config['name'],
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'episode_rewards': episode_rewards,
        })

    # Print results
    print("\n" + "=" * 60)
    print("Results: Model-Based RL Comparison")
    print("=" * 60)

    for r in results:
        print(f"\n{r['name']}:")
        print(f"  Mean Reward: {r['mean_reward']:.4f} (+/- {r['std_reward']:.4f})")

    return results


def run_computational_tradeoff():
    """
    Experiment: Trade-off between computation and sample efficiency.

    Hypothesis: More computation -> better sample efficiency.
    """
    print("\n" + "=" * 60)
    print("Computational Trade-off Experiment")
    print("=" * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Train world model
    train_data = MDPTrajectoryCollector.collect_gridworld_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )
    vae_config = VAEConfig(latent_dim=32, epochs=50)
    from dream_rollouts import train_world_model
    world_model = train_world_model(train_data, vae_config, device, epochs=50)

    # Different computation levels
    dream_ratios = [0, 2, 5, 10]  # Dream steps per real step
    results = []

    for dream_ratio in dream_ratios:
        print(f"\n{'=' * 60}")
        print(f"Dream Ratio: {dream_ratio}")
        print(f"{'=' * 60}")

        from dream_policy import PolicyNetwork, PolicyConfig, ValueNetwork
        policy = PolicyNetwork(PolicyConfig()).to(device)
        value = ValueNetwork().to(device)

        agent = DynaAgent(world_model, policy, value,
                         dream_steps_per_real=dream_ratio, device=device)

        # Evaluate
        num_episodes = 30
        episode_rewards = []

        for _ in range(num_episodes):
            metrics = agent.train_episode(max_steps=50, epsilon=0.1)
            episode_rewards.append(metrics['total_reward'])

        avg_reward = np.mean(episode_rewards)
        print(f"  Mean Reward: {avg_reward:.4f}")

        results.append({
            'dream_ratio': dream_ratio,
            'mean_reward': avg_reward,
            'std_reward': np.std(episode_rewards),
        })

    print("\n" + "=" * 60)
    print("Results: Computation vs Sample Efficiency")
    print("=" * 60)

    for r in results:
        print(f"  Dream Ratio {r['dream_ratio']}: {r['mean_reward']:.4f}")

    return results


def plot_results(comparison_results: List[Dict], tradeoff_results: List[Dict], save_path: str = None):
    """Plot model-based RL results"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Agent comparison
    ax = axes[0]
    names = [r['name'] for r in comparison_results]
    means = [r['mean_reward'] for r in comparison_results]
    stds = [r['std_reward'] for r in comparison_results]

    ax.bar(names, means, yerr=stds, capsize=5, alpha=0.7)
    ax.set_ylabel('Mean Reward')
    ax.set_title('Model-Based Agent Comparison')
    ax.grid(True, alpha=0.3, axis='y')

    # Computation tradeoff
    ax = axes[1]
    ratios = [r['dream_ratio'] for r in tradeoff_results]
    rewards = [r['mean_reward'] for r in tradeoff_results]
    ax.plot(ratios, rewards, 'o-', linewidth=2, markersize=8)
    ax.set_xlabel('Dream Steps per Real Step')
    ax.set_ylabel('Mean Reward')
    ax.set_title('Computation vs Sample Efficiency')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"\nPlot saved to {save_path}")

    plt.show()


def main():
    """Run all model-based RL experiments"""
    print("=" * 60)
    print("MODEL-BASED RL SIMULATIONS")
    print("Comparing MPC, Dyna, Dreamer, PLANET")
    print("=" * 60)

    # Run experiments
    comparison_results = run_mbrl_comparison()
    tradeoff_results = run_computational_tradeoff()

    # Save results
    output_dir = Path("C:/Users/casey/polln/simulations/dreaming/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "mbrl_comparison_results.json", 'w') as f:
        json.dump(comparison_results, f, indent=2)

    with open(output_dir / "computation_tradeoff_results.json", 'w') as f:
        json.dump(tradeoff_results, f, indent=2)

    print("\n" + "=" * 60)
    print("Results saved to simulations/dreaming/results/")
    print("=" * 60)

    # Plot
    plot_results(comparison_results, tradeoff_results,
                save_path=output_dir / "mbrl_plots.png")

    return comparison_results, tradeoff_results


if __name__ == "__main__":
    main()
