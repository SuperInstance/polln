"""
Optimization Framework Test Suite

Tests the hyperparameter optimization framework for correctness,
convergence, statistical validation, and config generation.
"""

import unittest
import json
import numpy as np
from pathlib import Path
import tempfile
import shutil


class TestPlinkoOptimization(unittest.TestCase):
    """Test Plinko temperature optimization"""

    def test_schedule_types(self):
        """Test all temperature schedule types"""
        from plinko_temperature import (
            ConstantSchedule,
            LinearDecaySchedule,
            ExponentialDecaySchedule,
            CyclicalSchedule
        )

        # Constant schedule
        schedule = ConstantSchedule(temperature=2.0)
        self.assertAlmostEqual(schedule.get_temperature(0, 100), 2.0)
        self.assertAlmostEqual(schedule.get_temperature(50, 100), 2.0)
        self.assertAlmostEqual(schedule.get_temperature(100, 100), 2.0)

        # Linear decay
        schedule = LinearDecaySchedule(initial_temp=2.0, min_temp=0.1)
        self.assertAlmostEqual(schedule.get_temperature(0, 100), 2.0)
        self.assertAlmostEqual(schedule.get_temperature(50, 100), 1.05)
        self.assertAlmostEqual(schedule.get_temperature(100, 100), 0.1)

        # Exponential decay
        schedule = ExponentialDecaySchedule(initial_temp=2.0, decay_rate=0.99, min_temp=0.1)
        temp_0 = schedule.get_temperature(0, 100)
        temp_50 = schedule.get_temperature(50, 100)
        self.assertGreater(temp_0, temp_50)
        self.assertGreaterEqual(temp_50, 0.1)

        # Cyclical schedule
        schedule = CyclicalSchedule(initial_temp=2.0, min_temp=0.1, cycle_length=50)
        temp_0 = schedule.get_temperature(0, 100)
        temp_25 = schedule.get_temperature(25, 100)
        temp_50 = schedule.get_temperature(50, 100)
        # Should cycle
        self.assertAlmostEqual(temp_0, temp_50, places=1)

    def test_plinko_selection(self):
        """Test Plinko stochastic selection"""
        from plinko_temperature import PlinkoLayer

        plinko = PlinkoLayer(n_arms=5)

        # With high temperature, should explore more
        high_temp_selections = [plinko.select_arm(temperature=10.0) for _ in range(100)]
        unique_high = len(set(high_temp_selections))

        # With low temperature, should exploit more
        plinko.value_estimates = np.array([1.0, 0.5, 0.3, 0.2, 0.1])
        low_temp_selections = [plinko.select_arm(temperature=0.1) for _ in range(100)]
        unique_low = len(set(low_temp_selections))

        # High temp should explore more diverse arms
        self.assertGreaterEqual(unique_high, unique_low)

    def test_simulation_convergence(self):
        """Test that simulation converges with reasonable parameters"""
        from plinko_temperature import run_simulation

        result = run_simulation(
            schedule_type='exponential',
            initial_temp=2.5,
            decay_rate=0.995,
            min_temp=0.1,
            n_arms=10,
            n_episodes=500,
            seed=42
        )

        # Should have all required metrics
        self.assertIn('convergence_speed', result)
        self.assertIn('final_performance', result)
        self.assertIn('exploration_efficiency', result)
        self.assertIn('total_regret', result)

        # Metrics should be in reasonable ranges
        self.assertGreater(result['convergence_speed'], 0)
        self.assertLessEqual(result['convergence_speed'], 500)
        self.assertGreater(result['exploration_efficiency'], 0)
        self.assertLessEqual(result['exploration_efficiency'], 1)


class TestTDLambdaOptimization(unittest.TestCase):
    """Test TD(λ) optimization"""

    def test_td_lambda_agent(self):
        """Test TD(λ) agent learning"""
        from td_lambda_optimization import TDLambdaAgent, RandomWalkMDP

        env = RandomWalkMDP(n_states=7)
        agent = TDLambdaAgent(n_states=7, lambda_=0.5, alpha=0.1, gamma=0.99)

        # Initial values should be zero
        np.testing.assert_array_equal(agent.values, np.zeros(7))

        # Train for a few episodes
        for episode in range(10):
            state = env.reset()
            done = False
            while not done:
                next_state, reward, done = env.step()
                agent.update(state, reward, next_state, done)
                state = next_state

        # Values should have changed
        self.assertFalse(np.allclose(agent.values, np.zeros(7)))

    def test_eligibility_traces(self):
        """Test eligibility trace decay"""
        from td_lambda_optimization import TDLambdaAgent

        agent = TDLambdaAgent(n_states=5, lambda_=0.9, alpha=0.1, gamma=0.99)

        # Set eligibility for state 0
        agent.eligibility[0] = 1.0

        # Update should decay traces
        agent.update(state=0, reward=0, next_state=1, done=False)

        # Trace should have decayed
        self.assertLess(agent.eligibility[0], 1.0)
        self.assertGreater(agent.eligibility[0], 0)

    def test_mse_calculation(self):
        """Test MSE calculation against true values"""
        from td_lambda_optimization import TDLambdaAgent

        agent = TDLambdaAgent(n_states=5, lambda_=0.5, alpha=0.1, gamma=0.99)
        true_values = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

        agent.values = np.array([0.1, 0.2, 0.6, 0.7, 0.9])

        mse = agent.get_mse(true_values)

        expected_mse = np.mean((agent.values - true_values) ** 2)
        self.assertAlmostEqual(mse, expected_mse, places=5)


class TestVAEOptimization(unittest.TestCase):
    """Test VAE architecture optimization"""

    def test_vae_forward_pass(self):
        """Test VAE forward pass"""
        from vae_architecture import VAE

        vae = VAE(input_dim=64, latent_dim=32, beta=1.0)

        # Forward pass
        x = np.random.randn(10, 64)
        x_recon, mu, logvar = vae.forward(x)

        # Check shapes
        self.assertEqual(x_recon.shape, x.shape)
        self.assertEqual(mu.shape, (10, 32))
        self.assertEqual(logvar.shape, (10, 32))

    def test_vae_loss_computation(self):
        """Test VAE loss computation"""
        from vae_architecture import VAE

        vae = VAE(input_dim=64, latent_dim=32, beta=1.0)

        x = np.random.randn(10, 64)
        x_recon, mu, logvar = vae.forward(x)
        losses = vae.compute_loss(x, x_recon, mu, logvar)

        # Should have all loss components
        self.assertIn('reconstruction', losses)
        self.assertIn('kl', losses)
        self.assertIn('total', losses)

        # Total loss should be sum of components
        expected_total = losses['reconstruction'] + vae.beta * losses['kl']
        self.assertAlmostEqual(losses['total'], expected_total, places=5)

    def test_beta_impact(self):
        """Test that beta affects KL weight"""
        from vae_architecture import VAE

        vae_low_beta = VAE(input_dim=64, latent_dim=32, beta=0.1)
        vae_high_beta = VAE(input_dim=64, latent_dim=32, beta=2.0)

        x = np.random.randn(10, 64)

        # Low beta
        x_recon1, mu1, logvar1 = vae_low_beta.forward(x)
        losses1 = vae_low_beta.compute_loss(x, x_recon1, mu1, logvar1)

        # High beta
        x_recon2, mu2, logvar2 = vae_high_beta.forward(x)
        losses2 = vae_high_beta.compute_loss(x, x_recon2, mu2, logvar2)

        # Higher beta should increase KL impact on total loss
        kl1_ratio = losses1['kl'] / losses1['total']
        kl2_ratio = losses2['kl'] / losses2['total']

        self.assertGreater(kl2_ratio, kl1_ratio)


class TestGraphEvolutionOptimization(unittest.TestCase):
    """Test graph evolution optimization"""

    def test_graph_initialization(self):
        """Test graph initialization"""
        from graph_evolution_params import AgentGraph

        graph = AgentGraph(n_agents=20, initial_density=0.2)

        # Check dimensions
        self.assertEqual(graph.adjacency.shape, (20, 20))

        # Check no self-connections
        np.testing.assert_array_equal(np.diag(graph.adjacency), np.zeros(20))

        # Check symmetry
        np.testing.assert_array_equal(graph.adjacency, graph.adjacency.T)

    def test_edge_operations(self):
        """Test adding and removing edges"""
        from graph_evolution_params import AgentGraph

        graph = AgentGraph(n_agents=10, initial_density=0.0)

        # Add edge
        graph.add_edge(0, 1)
        self.assertEqual(graph.adjacency[0, 1], 1)
        self.assertEqual(graph.adjacency[1, 0], 1)

        # Remove edge
        graph.remove_edge(0, 1)
        self.assertEqual(graph.adjacency[0, 1], 0)
        self.assertEqual(graph.adjacency[1, 0], 0)

    def test_pruning(self):
        """Test edge pruning"""
        from graph_evolution_params import AgentGraph

        graph = AgentGraph(n_agents=10, initial_density=1.0)

        # All agents connected to all others
        initial_edges = np.sum(graph.adjacency) / 2

        # Prune with threshold
        activity_weights = np.random.rand(10, 10)
        graph.prune_edges(threshold=0.5, activity_weights=activity_weights)

        # Should have fewer edges
        final_edges = np.sum(graph.adjacency) / 2
        self.assertLess(final_edges, initial_edges)

    def test_efficiency_calculation(self):
        """Test graph efficiency calculation"""
        from graph_evolution_params import AgentGraph

        # Complete graph (maximum efficiency)
        graph = AgentGraph(n_agents=10, initial_density=1.0)
        efficiency = graph.compute_efficiency()
        self.assertGreater(efficiency, 0)

        # Empty graph (zero efficiency)
        graph2 = AgentGraph(n_agents=10, initial_density=0.0)
        efficiency2 = graph2.compute_efficiency()
        self.assertEqual(efficiency2, 0)


class TestMetaDifferentiation(unittest.TestCase):
    """Test META tile differentiation optimization"""

    def test_meta_tile_initialization(self):
        """Test META tile initialization"""
        from meta_differentiation import MetaTile

        tile = MetaTile(
            tile_id=0,
            signal_response_rate=0.1,
            differentiation_threshold=0.9,
            plasticity_rule='hebbian'
        )

        # Should start undifferentiated
        self.assertFalse(tile.differentiated)
        self.assertIsNone(tile.specialization)

        # Should have weights
        self.assertEqual(tile.weights.shape, (5,))

    def test_signal_processing(self):
        """Test signal processing and weight updates"""
        from meta_differentiation import MetaTile

        tile = MetaTile(
            tile_id=0,
            signal_response_rate=0.1,
            differentiation_threshold=0.9,
            plasticity_rule='hebbian'
        )

        initial_weights = tile.weights.copy()

        # Process signal
        activation = tile.process_signal(signal_type=0, signal_strength=1.0)

        # Weights should have changed
        self.assertFalse(np.allclose(tile.weights, initial_weights))

        # Activation should be positive
        self.assertGreater(activation, 0)

    def test_differentiation(self):
        """Test tile differentiation"""
        from meta_differentiation import MetaTile

        tile = MetaTile(
            tile_id=0,
            signal_response_rate=0.5,
            differentiation_threshold=0.5,
            plasticity_rule='hebbian'
        )

        # Process strong signal
        tile.process_signal(signal_type=2, signal_strength=1.0)

        # Should differentiate
        self.assertTrue(tile.differentiated)
        self.assertEqual(tile.specialization, 2)

    def test_specialization_quality(self):
        """Test specialization quality measurement"""
        from meta_differentiation import MetaTile

        tile = MetaTile(
            tile_id=0,
            signal_response_rate=0.1,
            differentiation_threshold=0.9,
            plasticity_rule='hebbian'
        )

        # Before differentiation
        quality = tile.get_specialization_quality()
        self.assertEqual(quality, 0.0)

        # After differentiation
        tile.differentiate(specialization=0)
        tile.weights = np.array([1.0, 0.1, 0.1, 0.1, 0.1])

        quality = tile.get_specialization_quality()
        self.assertGreater(quality, 0)


class TestConfigGeneration(unittest.TestCase):
    """Test configuration file generation"""

    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_typescript_generation(self):
        """Test TypeScript config generation"""
        from generate_config import generate_typescript_config

        # Mock results
        results = {
            'optimizations': {
                'plinko_temperature': {
                    'best_parameters': {
                        'initial_temp': 2.5,
                        'schedule_type': 'exponential',
                        'decay_rate': 0.995,
                        'min_temp': 0.1
                    }
                },
                'td_lambda_optimization': {
                    'best_parameters': {
                        'lambda': 0.95,
                        'alpha': 0.1,
                        'gamma': 0.99
                    }
                }
            }
        }

        ts_content = generate_typescript_config(results)

        # Check that it contains expected content
        self.assertIn('PLINKO_CONFIG', ts_content)
        self.assertIn('TD_LAMBDA_CONFIG', ts_content)
        self.assertIn('initialTemperature: 2.5', ts_content)
        self.assertIn('lambda: 0.95', ts_content)
        self.assertIn('OPTIMIZED_CONFIG', ts_content)

    def test_json_generation(self):
        """Test JSON config generation"""
        from generate_config import generate_json_config

        # Mock results
        results = {
            'optimizations': {
                'plinko_temperature': {
                    'best_parameters': {
                        'initial_temp': 2.5,
                        'schedule_type': 'exponential',
                        'decay_rate': 0.995,
                        'min_temp': 0.1
                    }
                }
            }
        }

        json_config = generate_json_config(results)

        # Check structure
        self.assertIn('plinko', json_config)
        self.assertIn('initialTemperature', json_config['plinko'])
        self.assertEqual(json_config['plinko']['initialTemperature'], 2.5)


class TestOptimizationConvergence(unittest.TestCase):
    """Test that optimizations converge to reasonable solutions"""

    def test_plinko_convergence(self):
        """Test Plinko optimization converges"""
        from plinko_temperature import run_simulation

        # Test multiple parameter sets
        results = []
        for schedule in ['constant', 'linear', 'exponential']:
            result = run_simulation(
                schedule_type=schedule,
                initial_temp=2.5,
                decay_rate=0.995,
                min_temp=0.1,
                n_arms=10,
                n_episodes=200,
                seed=42
            )
            results.append(result)

        # All should complete
        self.assertEqual(len(results), 3)

        # Exponential should perform best (typically)
        exp_result = results[2]
        self.assertGreater(exp_result['final_performance'], 0)

    def test_grid_search_completes(self):
        """Test that TD(λ) grid search completes"""
        from td_lambda_optimization import grid_search

        # Small grid search for testing
        best_params, grid_results = grid_search(
            lambda_values=[0.5, 0.9],
            alpha_values=[0.1, 0.2],
            gamma_values=[0.99]
        )

        # Should find best parameters
        self.assertIn('lambda', best_params)
        self.assertIn('alpha', best_params)
        self.assertIn('gamma', best_params)

        # Should have results
        self.assertIn('all_results', grid_results)
        self.assertEqual(len(grid_results['all_results']), 2 * 2 * 1)  # 4 combinations


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlinkoOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestTDLambdaOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestVAEOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphEvolutionOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaDifferentiation))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizationConvergence))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
