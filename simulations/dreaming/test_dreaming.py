"""
Test Suite for Dreaming Simulations
====================================

Comprehensive tests for all dreaming simulation modules.

Tests:
- VAE encoding/decoding
- Transition model prediction
- Dream rollout generation
- Policy optimization
- Model-based RL agents
"""

import pytest
import torch
import numpy as np
from pathlib import Path


class TestVAE:
    """Test VAE functionality"""

    def test_vae_initialization(self):
        """Test VAE can be initialized"""
        from vae_training import VAE, VAEConfig

        config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(config)

        assert vae is not None
        assert vae.config.latent_dim == 32

    def test_vae_encode_decode(self):
        """Test VAE encoding and decoding"""
        from vae_training import VAE, VAEConfig

        config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(config)

        # Create dummy input
        x = torch.randn(1, 64)

        # Encode
        mean, log_var = vae.encode(x)
        assert mean.shape == (1, 32)
        assert log_var.shape == (1, 32)

        # Reparameterize
        z = vae.reparameterize(mean, log_var)
        assert z.shape == (1, 32)

        # Decode
        x_recon = vae.decode(z)
        assert x_recon.shape == (1, 64)

    def test_vae_loss_function(self):
        """Test VAE loss computation"""
        from vae_training import VAE, VAEConfig

        config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(config)

        x = torch.randn(4, 64)
        x_recon, mean, log_var = vae(x)

        total_loss, recon_loss, kl_loss = vae.loss_function(x, x_recon, mean, log_var)

        assert total_loss.item() > 0
        assert recon_loss.item() > 0
        assert kl_loss.item() >= 0  # KL is non-negative

    def test_trajectory_collection(self):
        """Test trajectory data collection"""
        from vae_training import MDPTrajectoryCollector

        trajectories = MDPTrajectoryCollector.collect_gridworld_trajectories(
            num_trajectories=10,
            trajectory_length=20
        )

        assert trajectories.shape == (200, 64)  # 10 * 20 trajectories


class TestTransitionModel:
    """Test transition model"""

    def test_transition_model_forward(self):
        """Test transition model prediction"""
        from dream_rollouts import TransitionModel, TransitionModelConfig

        config = TransitionModelConfig(latent_dim=32, action_dim=4)
        model = TransitionModel(config)

        state = torch.randn(2, 32)
        action = torch.LongTensor([0, 1])

        next_state, hidden = model(state, action)

        assert next_state.shape == (2, 32)
        assert hidden is not None

    def test_reward_model(self):
        """Test reward model prediction"""
        from dream_rollouts import RewardModel

        model = RewardModel(latent_dim=32, action_dim=4)

        state = torch.randn(2, 32)
        action = torch.LongTensor([0, 1])

        reward = model(state, action)

        assert reward.shape == (2, 1)


class TestWorldModel:
    """Test world model integration"""

    def test_world_model_forward(self):
        """Test world model prediction"""
        from vae_training import VAE, VAEConfig
        from dream_rollouts import TransitionModel, RewardModel, TransitionModelConfig, WorldModel

        # Create components
        vae_config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(vae_config)

        trans_config = TransitionModelConfig(latent_dim=32, action_dim=4)
        transition = TransitionModel(trans_config)

        reward = RewardModel(latent_dim=32, action_dim=4)

        # Create world model
        world_model = WorldModel(vae, transition, reward)

        # Test prediction
        obs = torch.randn(1, 64)
        action = torch.LongTensor([0])

        next_state, pred_reward, hidden = world_model.predict(obs, action)

        assert next_state.shape == (1, 32)
        assert pred_reward.shape == (1, 1)


class TestDreamGenerator:
    """Test dream episode generation"""

    def test_dream_rollout_generation(self):
        """Test dream episode generation"""
        from vae_training import VAE, VAEConfig
        from dream_rollouts import TransitionModel, RewardModel, TransitionModelConfig, WorldModel, DreamGenerator

        # Create world model
        vae_config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(vae_config)

        trans_config = TransitionModelConfig(latent_dim=32, action_dim=4)
        transition = TransitionModel(trans_config)

        reward = RewardModel(latent_dim=32, action_dim=4)

        world_model = WorldModel(vae, transition, reward)

        # Create dream generator
        device = torch.device('cpu')
        dream_gen = DreamGenerator(world_model, device)

        # Generate dream
        start_obs = np.random.randn(64)
        policy = lambda s: np.random.randint(4)

        dream_ep = dream_gen.dream_rollout(start_obs, policy, horizon=10)

        assert 'states' in dream_ep
        assert 'actions' in dream_ep
        assert 'rewards' in dream_ep
        assert len(dream_ep['actions']) == 10
        assert len(dream_ep['rewards']) == 10


class TestRealEnvironment:
    """Test real environment"""

    def test_environment_step(self):
        """Test environment step function"""
        from dream_rollouts import RealEnvironment

        env = RealEnvironment(grid_size=8)

        state = np.zeros(64)
        state[0] = 4  # x position
        state[1] = 4  # y position
        state[2] = 7  # goal x
        state[3] = 7  # goal y

        # Step right
        next_state, reward, done = env.step(state, 0)

        assert next_state[0] == 5  # x increased
        assert reward > 0  # Positive reward for moving toward goal
        assert not done

    def test_real_rollout(self):
        """Test real episode generation"""
        from dream_rollouts import RealEnvironment

        env = RealEnvironment(grid_size=8)

        state = np.zeros(64)
        state[0] = 0
        state[1] = 0
        state[2] = 7
        state[3] = 7

        policy = lambda s: np.random.randint(4)

        episode = env.real_rollout(state, policy, horizon=20)

        assert 'states' in episode
        assert 'actions' in episode
        assert 'rewards' in episode
        assert len(episode['actions']) > 0


class TestPolicyNetwork:
    """Test policy network"""

    def test_policy_forward(self):
        """Test policy forward pass"""
        from dream_policy import PolicyNetwork, PolicyConfig

        config = PolicyConfig(state_dim=64, action_dim=4)
        policy = PolicyNetwork(config)

        state = torch.randn(2, 64)
        logits = policy(state)

        assert logits.shape == (2, 4)

    def test_policy_get_action(self):
        """Test action sampling"""
        from dream_policy import PolicyNetwork, PolicyConfig

        config = PolicyConfig(state_dim=64, action_dim=4)
        policy = PolicyNetwork(config)

        state = np.random.randn(64)

        # No exploration
        action = policy.get_action(state, explore=False, epsilon=0.0)
        assert 0 <= action < 4

        # With exploration
        action = policy.get_action(state, explore=True, epsilon=1.0)
        assert 0 <= action < 4


class TestValueNetwork:
    """Test value network"""

    def test_value_forward(self):
        """Test value prediction"""
        from dream_policy import ValueNetwork

        value = ValueNetwork(state_dim=64)

        state = torch.randn(2, 64)
        values = value(state)

        assert values.shape == (2, 1)


class TestPolicyOptimizer:
    """Test policy optimizer"""

    def test_compute_returns(self):
        """Test return computation"""
        from dream_policy import PolicyOptimizer
        from dream_policy import PolicyNetwork, PolicyConfig, ValueNetwork

        policy = PolicyNetwork(PolicyConfig())
        value = ValueNetwork()
        optimizer = PolicyOptimizer(policy, value, gamma=0.99)

        rewards = [1, 2, 3, 4, 5]
        dones = [False, False, False, False, True]

        returns = optimizer.compute_returns(rewards, dones)

        assert len(returns) == len(rewards)
        # Last return should be last reward
        assert abs(returns[-1] - rewards[-1]) < 1e-6


class TestDreamBasedLearner:
    """Test dream-based learner"""

    def test_learner_initialization(self):
        """Test learner can be initialized"""
        from dream_policy import DreamBasedLearner
        from dream_policy import PolicyNetwork, PolicyConfig, ValueNetwork, PolicyOptimizer
        from vae_training import VAE, VAEConfig
        from dream_rollouts import TransitionModel, RewardModel, TransitionModelConfig, WorldModel

        # Create components
        vae_config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(vae_config)

        trans_config = TransitionModelConfig(latent_dim=32, action_dim=4)
        transition = TransitionModel(trans_config)

        reward = RewardModel(latent_dim=32, action_dim=4)

        world_model = WorldModel(vae, transition, reward)

        policy = PolicyNetwork(PolicyConfig())
        value = ValueNetwork()
        optimizer = PolicyOptimizer(policy, value)

        # Create learner
        device = torch.device('cpu')
        learner = DreamBasedLearner(
            policy, value, world_model, optimizer,
            dream_ratio=0.5, device=device
        )

        assert learner.dream_ratio == 0.5


class TestMBrLAgents:
    """Test model-based RL agents"""

    def test_mpc_planner(self):
        """Test MPC planner"""
        from mb_rl import MPlanner
        from vae_training import VAE, VAEConfig
        from dream_rollouts import TransitionModel, RewardModel, TransitionModelConfig, WorldModel

        # Create world model
        vae_config = VAEConfig(latent_dim=32, input_dim=64)
        vae = VAE(vae_config)

        trans_config = TransitionModelConfig(latent_dim=32, action_dim=4)
        transition = TransitionModel(trans_config)

        reward = RewardModel(latent_dim=32, action_dim=4)

        world_model = WorldModel(vae, transition, reward)

        # Create MPC planner
        planner = MPlanner(world_model, horizon=5, num_candidates=3)

        device = torch.device('cpu')
        state = np.random.randn(64)

        action = planner.plan(state, device)

        assert 0 <= action < 4


class TestIntegration:
    """Integration tests"""

    def test_full_dream_workflow(self):
        """Test complete dream workflow"""
        from vae_training import VAE, VAEConfig, MDPTrajectoryCollector
        from dream_rollouts import TransitionModel, RewardModel, TransitionModelConfig, WorldModel, DreamGenerator

        # Collect data
        data = MDPTrajectoryCollector.collect_gridworld_trajectories(
            num_trajectories=10,
            trajectory_length=20
        )

        # Create and train VAE
        vae_config = VAEConfig(latent_dim=32, input_dim=64, epochs=2)
        from vae_training import VAETrainer
        trainer = VAETrainer(vae_config)
        trainer.train(data, verbose=False)

        # Create world model
        trans_config = TransitionModelConfig(latent_dim=32, action_dim=4)
        transition = TransitionModel(trans_config)
        reward = RewardModel(latent_dim=32, action_dim=4)

        world_model = WorldModel(trainer.model, transition, reward)

        # Generate dream
        device = torch.device('cpu')
        dream_gen = DreamGenerator(world_model, device)

        start_obs = data[0]
        policy = lambda s: np.random.randint(4)

        dream_ep = dream_gen.dream_rollout(start_obs, policy, horizon=10)

        assert dream_ep is not None
        assert len(dream_ep['actions']) == 10


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
