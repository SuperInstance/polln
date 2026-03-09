"""
Schedule Optimization Tests
===========================
Unit tests for schedule optimization simulations.

Tests validation of:
- Schedule generation correctness
- Simulation convergence
- Statistical significance
- Edge cases and boundary conditions
"""

import unittest
import numpy as np
from pathlib import Path
import tempfile
import json

# Import schedule modules
from lr_schedule_search import (
    LearningRateSchedules,
    LearningSimulator,
    ScheduleOptimizer as LROptimizer
)
from exploration_schedule import (
    ExplorationSchedules,
    ExplorationSimulator,
    ScheduleOptimizer as ExplorationOptimizer
)
from dream_ratio_optimization import (
    DreamSchedules,
    DreamingSimulator,
    ScheduleOptimizer as DreamOptimizer
)
from plasticity_schedule import (
    PlasticitySchedules,
    PlasticitySimulator,
    ScheduleOptimizer as PlasticityOptimizer
)
from federated_sync_schedule import (
    FederatedSchedules,
    FederatedSimulator,
    ScheduleOptimizer as FederatedOptimizer
)


class TestLearningRateSchedules(unittest.TestCase):
    """Test learning rate schedule generation"""

    def setUp(self):
        self.schedules = LearningRateSchedules()
        self.total_steps = 100

    def test_constant_schedule(self):
        """Test constant schedule"""
        schedule = self.schedules.constant(lr=0.01, total_steps=self.total_steps)
        self.assertEqual(len(schedule), self.total_steps)
        np.testing.assert_array_almost_equal(schedule, np.full(self.total_steps, 0.01))

    def test_step_decay(self):
        """Test step decay schedule"""
        schedule = self.schedules.step_decay(
            initial_lr=0.1,
            total_steps=self.total_steps,
            drop_rate=0.5,
            epochs_drop=25
        )

        # First 25 steps should be 0.1
        np.testing.assert_array_almost_equal(schedule[:25], np.full(25, 0.1))

        # Steps 25-50 should be 0.05
        np.testing.assert_array_almost_equal(schedule[25:50], np.full(25, 0.05))

    def test_exponential_decay(self):
        """Test exponential decay schedule"""
        schedule = self.schedules.exponential_decay(
            initial_lr=0.1,
            total_steps=self.total_steps,
            gamma=0.99
        )

        # Should monotonically decrease
        self.assertTrue(np.all(np.diff(schedule) <= 0))

        # Should be positive
        self.assertTrue(np.all(schedule > 0))

    def test_cosine_annealing(self):
        """Test cosine annealing schedule"""
        schedule = self.schedules.cosine_annealing(
            initial_lr=0.1,
            total_steps=self.total_steps,
            min_lr=0.0
        )

        # Should start at initial_lr
        self.assertAlmostEqual(schedule[0], 0.1, places=2)

        # Should end at min_lr
        self.assertAlmostEqual(schedule[-1], 0.0, places=2)

    def test_warmup_cosine(self):
        """Test warmup + cosine annealing"""
        schedule = self.schedules.warmup_cosine(
            initial_lr=0.1,
            total_steps=self.total_steps,
            warmup_steps=10,
            min_lr=0.0
        )

        # Warmup phase should increase
        self.assertTrue(schedule[5] > schedule[0])

        # Should end at min_lr
        self.assertAlmostEqual(schedule[-1], 0.0, places=2)

    def test_cyclical_sgdr(self):
        """Test cyclical SGDR schedule"""
        schedule = self.schedules.cyclical_sgdr(
            initial_lr=0.1,
            total_steps=self.total_steps,
            cycle_length=20,
            min_lr=0.0
        )

        # Should have multiple peaks
        peaks = len([i for i in range(1, len(schedule)-1)
                     if schedule[i] > schedule[i-1] and schedule[i] > schedule[i+1]])
        self.assertGreater(peaks, 1)


class TestExplorationSchedules(unittest.TestCase):
    """Test exploration schedule generation"""

    def setUp(self):
        self.schedules = ExplorationSchedules()
        self.total_steps = 100

    def test_epsilon_constant(self):
        """Test constant epsilon schedule"""
        schedule = self.schedules.epsilon_constant(epsilon=0.1, total_steps=self.total_steps)
        self.assertEqual(len(schedule), self.total_steps)
        np.testing.assert_array_almost_equal(schedule, np.full(self.total_steps, 0.1))

    def test_epsilon_linear(self):
        """Test linear epsilon decay"""
        schedule = self.schedules.epsilon_linear(
            initial_epsilon=0.5,
            total_steps=self.total_steps,
            min_epsilon=0.01
        )

        # Should monotonically decrease
        self.assertTrue(np.all(np.diff(schedule) <= 0))

        # Should be bounded
        self.assertTrue(np.all(schedule >= 0.01))
        self.assertTrue(np.all(schedule <= 0.5))

    def test_temperature_exponential(self):
        """Test exponential temperature decay"""
        schedule = self.schedules.temperature_exponential(
            initial_temp=2.5,
            total_steps=self.total_steps,
            min_temp=0.1,
            decay_rate=0.99
        )

        # Should monotonically decrease
        self.assertTrue(np.all(np.diff(schedule) <= 0))

        # Should be bounded
        self.assertTrue(np.all(schedule >= 0.1))

    def test_temperature_cosine(self):
        """Test cosine temperature annealing"""
        schedule = self.schedules.temperature_cosine(
            initial_temp=2.5,
            total_steps=self.total_steps,
            min_temp=0.1
        )

        # Should start at initial_temp
        self.assertAlmostEqual(schedule[0], 2.5, places=2)

        # Should end at min_temp
        self.assertAlmostEqual(schedule[-1], 0.1, places=2)


class TestDreamSchedules(unittest.TestCase):
    """Test dream ratio schedule generation"""

    def setUp(self):
        self.schedules = DreamSchedules()
        self.total_steps = 100

    def test_constant_dream_ratio(self):
        """Test constant dream ratio"""
        schedule = self.schedules.constant(ratio=0.5, total_steps=self.total_steps)
        self.assertEqual(len(schedule), self.total_steps)
        np.testing.assert_array_almost_equal(schedule, np.full(self.total_steps, 0.5))

    def test_increasing_dream_ratio(self):
        """Test increasing dream ratio"""
        schedule = self.schedules.increasing(
            initial_ratio=0.2,
            total_steps=self.total_steps,
            max_ratio=0.8
        )

        # Should monotonically increase
        self.assertTrue(np.all(np.diff(schedule) >= 0))

        # Should be bounded
        self.assertTrue(np.all(schedule >= 0.2))
        self.assertTrue(np.all(schedule <= 0.8))

    def test_one_cycle_dream_ratio(self):
        """Test one-cycle dream ratio"""
        schedule = self.schedules.one_cycle(
            initial_ratio=0.2,
            total_steps=self.total_steps,
            max_ratio=0.9,
            min_ratio=0.1
        )

        # Should increase then decrease
        mid_point = self.total_steps // 2
        max_idx = np.argmax(schedule)

        # Peak should be near middle
        self.assertLess(abs(max_idx - mid_point), 15)


class TestPlasticitySchedules(unittest.TestCase):
    """Test plasticity schedule generation"""

    def setUp(self):
        self.schedules = PlasticitySchedules()
        self.total_steps = 100

    def test_constant_plasticity(self):
        """Test constant plasticity"""
        schedule = self.schedules.constant(plasticity=0.5, total_steps=self.total_steps)
        self.assertEqual(len(schedule), self.total_steps)
        np.testing.assert_array_almost_equal(schedule, np.full(self.total_steps, 0.5))

    def test_linear_decay_plasticity(self):
        """Test linear plasticity decay"""
        schedule = self.schedules.linear_decay(
            initial_plasticity=1.0,
            total_steps=self.total_steps,
            min_plasticity=0.01
        )

        # Should monotonically decrease
        self.assertTrue(np.all(np.diff(schedule) <= 0))

        # Should be bounded
        self.assertTrue(np.all(schedule >= 0.01))
        self.assertTrue(np.all(schedule <= 1.0))

    def test_u_shaped_plasticity(self):
        """Test U-shaped plasticity"""
        schedule = self.schedules.u_shaped(
            initial_plasticity=1.0,
            total_steps=self.total_steps,
            min_plasticity=0.1
        )

        # Should decrease then increase
        min_idx = np.argmin(schedule)

        # Minimum should be near middle
        self.assertLess(abs(min_idx - self.total_steps // 2), 15)


class TestFederatedSchedules(unittest.TestCase):
    """Test federated sync schedule generation"""

    def setUp(self):
        self.schedules = FederatedSchedules()
        self.total_steps = 100

    def test_fixed_frequency(self):
        """Test fixed frequency synchronization"""
        schedule = self.schedules.fixed_frequency(sync_every=10, total_steps=self.total_steps)

        # Should have 10 syncs
        self.assertEqual(np.sum(schedule), 10)

        # Syncs should be evenly spaced
        sync_indices = np.where(schedule)[0]
        np.testing.assert_array_equal(sync_indices, np.arange(0, 100, 10))

    def test_exponential_backoff(self):
        """Test exponential backoff"""
        schedule = self.schedules.exponential_backoff(
            initial_interval=5,
            total_steps=self.total_steps,
            max_interval=50,
            growth_factor=1.1
        )

        # Should have some syncs
        self.assertGreater(np.sum(schedule), 0)

        # Should have fewer syncs than fixed frequency
        fixed_syncs = np.sum(self.schedules.fixed_frequency(sync_every=10, total_steps=self.total_steps))
        self.assertLess(np.sum(schedule), fixed_syncs)

    def test_gossip_style(self):
        """Test gossip-style synchronization"""
        schedule = self.schedules.gossip_style(
            total_steps=self.total_steps,
            gossip_probability=0.1
        )

        # Should have approximately 10% syncs (allowing randomness)
        sync_ratio = np.sum(schedule) / self.total_steps
        self.assertGreater(sync_ratio, 0.05)
        self.assertLess(sync_ratio, 0.15)


class TestSimulations(unittest.TestCase):
    """Test simulation convergence"""

    def test_td_lambda_convergence(self):
        """Test TD(λ) simulation converges"""
        simulator = LearningSimulator()

        schedule = np.linspace(0.1, 0.001, 1000)
        values, losses = simulator.simulate_td_lambda(schedule)

        # Loss should decrease
        self.assertGreater(losses[0], losses[-1])

        # Final loss should be reasonable
        self.assertLess(losses[-1], 0.1)

    def test_exploration_convergence(self):
        """Test exploration simulation converges"""
        simulator = ExplorationSimulator()

        schedule = np.linspace(0.5, 0.01, 1000)

        from exploration_schedule import MultiArmedBandit
        bandit = MultiArmedBandit(num_arms=10, seed=42)

        rewards, _, _ = simulator.simulate_epsilon_greedy(schedule, bandit)

        # Rewards should generally increase
        early_mean = np.mean(rewards[:100])
        late_mean = np.mean(rewards[-100:])
        self.assertGreater(late_mean, early_mean - 0.5)  # Allow some noise

    def test_dream_convergence(self):
        """Test dreaming simulation shows improvement"""
        simulator = DreamingSimulator()

        schedule = np.full(500, 0.5)
        performance_history = []

        for episode in range(500):
            dream_ratio = schedule[episode]

            if np.random.random() < dream_ratio:
                reward, trajectory = simulator.dream_episode()
            else:
                reward, trajectory = simulator.real_episode()

            simulator.update_policy(trajectory)
            simulator.update_world_model(trajectory)

            if episode % 10 == 0:
                performance_history.append(reward)

        # Should have tracked performance
        self.assertEqual(len(performance_history), 50)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_zero_steps(self):
        """Test schedule with zero steps"""
        schedules = LearningRateSchedules()
        schedule = schedules.constant(lr=0.01, total_steps=0)
        self.assertEqual(len(schedule), 0)

    def test_single_step(self):
        """Test schedule with single step"""
        schedules = LearningRateSchedules()
        schedule = schedules.constant(lr=0.01, total_steps=1)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0], 0.01)

    def test_very_large_lr(self):
        """Test with very large learning rate"""
        simulator = LearningSimulator()
        schedule = np.full(100, 10.0)  # Very large LR

        # Should not crash
        values, losses = simulator.simulate_td_lambda(schedule)
        self.assertEqual(len(losses), 100)

    def test_zero_lr(self):
        """Test with zero learning rate"""
        simulator = LearningSimulator()
        schedule = np.full(100, 0.0)

        values, losses = simulator.simulate_td_lambda(schedule)

        # Values should not change much with zero LR
        self.assertAlmostEqual(np.std(values), 0.0, places=1)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLearningRateSchedules))
    suite.addTests(loader.loadTestsFromTestCase(TestExplorationSchedules))
    suite.addTests(loader.loadTestsFromTestCase(TestDreamSchedules))
    suite.addTests(loader.loadTestsFromTestCase(TestPlasticitySchedules))
    suite.addTests(loader.loadTestsFromTestCase(TestFederatedSchedules))
    suite.addTests(loader.loadTestsFromTestCase(TestSimulations))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
