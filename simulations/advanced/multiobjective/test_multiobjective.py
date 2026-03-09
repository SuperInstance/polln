"""
Tests for Multiobjective Pareto Optimization

Validates optimization algorithms, Pareto frontiers, and configuration generation.
"""

import unittest
import numpy as np
from pathlib import Path
import json
import tempfile
import shutil

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent))

from pareto_accuracy_cost import (
    Configuration, AccuracyCostEvaluator, NSGA2Optimizer
)
from pareto_speed_quality import (
    SpeedConfiguration, SpeedQualityEvaluator
)
from pareto_robustness_efficiency import (
    RobustnessConfiguration, RobustnessEfficiencyEvaluator
)
from pareto_scalability_complexity import (
    ScalabilityConfiguration, ScalabilityComplexityEvaluator
)


class TestAccuracyCostOptimization(unittest.TestCase):
    """Test accuracy vs cost optimization."""

    def setUp(self):
        self.evaluator = AccuracyCostEvaluator(tokens_per_request=1000, requests_per_hour=100)

    def test_configuration_creation(self):
        """Test configuration dataclass creation."""
        config = Configuration(
            model_size=100,
            checkpoint_frequency=10,
            cache_size_mb=512,
            batch_size=16,
            compression_level=0.5,
            temperature=0.7,
            use_federated=True,
            replication_factor=2
        )

        self.assertEqual(config.model_size, 100)
        self.assertTrue(config.use_federated)

    def test_accuracy_estimation(self):
        """Test accuracy estimation."""
        config = Configuration(
            model_size=100,
            checkpoint_frequency=10,
            cache_size_mb=512,
            batch_size=16,
            compression_level=0.5,
            temperature=0.7,
            use_federated=False,
            replication_factor=1
        )

        accuracy = self.evaluator.estimate_accuracy(config)
        self.assertGreater(accuracy, 0.5)
        self.assertLess(accuracy, 1.0)

    def test_cost_estimation(self):
        """Test cost estimation."""
        config = Configuration(
            model_size=100,
            checkpoint_frequency=10,
            cache_size_mb=512,
            batch_size=16,
            compression_level=0.5,
            temperature=0.7,
            use_federated=False,
            replication_factor=1
        )

        cost = self.evaluator.estimate_hourly_cost(config)
        self.assertGreater(cost, 0)

    def test_accuracy_cost_tradeoff(self):
        """Test that higher accuracy generally costs more."""
        small_config = Configuration(
            model_size=10,
            checkpoint_frequency=5,
            cache_size_mb=128,
            batch_size=1,
            compression_level=0.8,
            temperature=1.0,
            use_federated=False,
            replication_factor=1
        )

        large_config = Configuration(
            model_size=500,
            checkpoint_frequency=20,
            cache_size_mb=2048,
            batch_size=32,
            compression_level=0.0,
            temperature=0.5,
            use_federated=True,
            replication_factor=3
        )

        small_accuracy = self.evaluator.estimate_accuracy(small_config)
        large_accuracy = self.evaluator.estimate_accuracy(large_config)
        small_cost = self.evaluator.estimate_hourly_cost(small_config)
        large_cost = self.evaluator.estimate_hourly_cost(large_config)

        self.assertLess(small_accuracy, large_accuracy)
        self.assertLess(small_cost, large_cost)


class TestSpeedQualityOptimization(unittest.TestCase):
    """Test speed vs quality optimization."""

    def setUp(self):
        self.evaluator = SpeedQualityEvaluator(avg_tokens_per_request=500)

    def test_latency_estimation(self):
        """Test latency estimation."""
        config = SpeedConfiguration(
            model_size=100,
            batch_size=16,
            max_parallel_requests=8,
            kv_cache_size_mb=512,
            compression_level=0.5,
            use_speculative_decoding=False,
            use_quantization=False,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1000
        )

        latency = self.evaluator.estimate_latency_ms(config)
        self.assertGreater(latency, 0)

    def test_quality_estimation(self):
        """Test quality estimation."""
        config = SpeedConfiguration(
            model_size=100,
            batch_size=16,
            max_parallel_requests=8,
            kv_cache_size_mb=512,
            compression_level=0.5,
            use_speculative_decoding=False,
            use_quantization=False,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1000
        )

        quality = self.evaluator.estimate_quality(config)
        self.assertGreater(quality, 0)
        self.assertLess(quality, 1.0)

    def test_throughput_estimation(self):
        """Test throughput estimation."""
        config = SpeedConfiguration(
            model_size=100,
            batch_size=16,
            max_parallel_requests=8,
            kv_cache_size_mb=512,
            compression_level=0.5,
            use_speculative_decoding=False,
            use_quantization=False,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1000
        )

        throughput = self.evaluator.estimate_throughput(config)
        self.assertGreater(throughput, 0)

    def test_quantization_speedup(self):
        """Test that quantization improves latency at quality cost."""
        base_config = SpeedConfiguration(
            model_size=100,
            batch_size=16,
            max_parallel_requests=8,
            kv_cache_size_mb=512,
            compression_level=0.0,
            use_speculative_decoding=False,
            use_quantization=False,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1000
        )

        quantized_config = SpeedConfiguration(
            model_size=100,
            batch_size=16,
            max_parallel_requests=8,
            kv_cache_size_mb=512,
            compression_level=0.0,
            use_speculative_decoding=False,
            use_quantization=True,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1000
        )

        base_latency = self.evaluator.estimate_latency_ms(base_config)
        quantized_latency = self.evaluator.estimate_latency_ms(quantized_config)
        base_quality = self.evaluator.estimate_quality(base_config)
        quantized_quality = self.evaluator.estimate_quality(quantized_config)

        self.assertLess(quantized_latency, base_latency)
        self.assertLess(quantized_quality, base_quality)


class TestRobustnessOptimization(unittest.TestCase):
    """Test robustness vs efficiency optimization."""

    def setUp(self):
        self.evaluator = RobustnessEfficiencyEvaluator(base_cost=1.0)

    def test_availability_estimation(self):
        """Test availability estimation."""
        config = RobustnessConfiguration(
            replication_factor=3,
            checkpoint_interval_sec=60,
            backup_enabled=True,
            backup_frequency_hours=6,
            monitoring_level=2,
            health_check_interval_sec=30,
            circuit_breaker_threshold=5,
            retry_policy='exponential',
            max_retries=3,
            timeout_multiplier=1.5,
            use_quorum=True,
            disaster_recovery_enabled=False
        )

        availability = self.evaluator.estimate_availability(config)
        self.assertGreater(availability, 0.99)
        self.assertLess(availability, 1.0)

    def test_replication_improves_availability(self):
        """Test that replication improves availability."""
        single_config = RobustnessConfiguration(
            replication_factor=1,
            checkpoint_interval_sec=60,
            backup_enabled=False,
            backup_frequency_hours=24,
            monitoring_level=0,
            health_check_interval_sec=60,
            circuit_breaker_threshold=1,
            retry_policy='none',
            max_retries=0,
            timeout_multiplier=1.0,
            use_quorum=False,
            disaster_recovery_enabled=False
        )

        replicated_config = RobustnessConfiguration(
            replication_factor=3,
            checkpoint_interval_sec=60,
            backup_enabled=True,
            backup_frequency_hours=6,
            monitoring_level=2,
            health_check_interval_sec=30,
            circuit_breaker_threshold=5,
            retry_policy='exponential',
            max_retries=3,
            timeout_multiplier=1.5,
            use_quorum=True,
            disaster_recovery_enabled=True
        )

        single_availability = self.evaluator.estimate_availability(single_config)
        replicated_availability = self.evaluator.estimate_availability(replicated_config)

        self.assertLess(single_availability, replicated_availability)

    def test_cost_multiplier(self):
        """Test cost multiplier estimation."""
        config = RobustnessConfiguration(
            replication_factor=2,
            checkpoint_interval_sec=60,
            backup_enabled=True,
            backup_frequency_hours=12,
            monitoring_level=1,
            health_check_interval_sec=60,
            circuit_breaker_threshold=3,
            retry_policy='fixed',
            max_retries=2,
            timeout_multiplier=1.2,
            use_quorum=False,
            disaster_recovery_enabled=False
        )

        cost = self.evaluator.estimate_cost_multiplier(config)
        self.assertGreater(cost, 1.0)


class TestScalabilityOptimization(unittest.TestCase):
    """Test scalability vs complexity optimization."""

    def setUp(self):
        self.evaluator = ScalabilityComplexityEvaluator()

    def test_throughput_estimation(self):
        """Test throughput estimation."""
        config = ScalabilityConfiguration(
            colony_size=100,
            topology_depth=3,
            agent_types=5,
            decentralization_level=0.5,
            horizontal_scaling=True,
            auto_scaling=False,
            load_balancing_strategy='least_loaded',
            cache_sharding=True,
            federation_enabled=False,
            meta_tile_ratio=0.3,
            communication_pattern='hierarchical'
        )

        throughput = self.evaluator.estimate_throughput(config)
        self.assertGreater(throughput, 0)

    def test_complexity_estimation(self):
        """Test complexity estimation."""
        config = ScalabilityConfiguration(
            colony_size=100,
            topology_depth=3,
            agent_types=5,
            decentralization_level=0.5,
            horizontal_scaling=True,
            auto_scaling=False,
            load_balancing_strategy='least_loaded',
            cache_sharding=True,
            federation_enabled=False,
            meta_tile_ratio=0.3,
            communication_pattern='hierarchical'
        )

        complexity = self.evaluator.estimate_complexity_score(config)
        self.assertGreater(complexity, 0)
        self.assertLess(complexity, 1.0)

    def test_scaling_law(self):
        """Test that larger colonies have higher throughput."""
        small_config = ScalabilityConfiguration(
            colony_size=10,
            topology_depth=2,
            agent_types=3,
            decentralization_level=0.3,
            horizontal_scaling=False,
            auto_scaling=False,
            load_balancing_strategy='round_robin',
            cache_sharding=False,
            federation_enabled=False,
            meta_tile_ratio=0.1,
            communication_pattern='star'
        )

        large_config = ScalabilityConfiguration(
            colony_size=500,
            topology_depth=5,
            agent_types=10,
            decentralization_level=0.7,
            horizontal_scaling=True,
            auto_scaling=True,
            load_balancing_strategy='least_loaded',
            cache_sharding=True,
            federation_enabled=True,
            meta_tile_ratio=0.5,
            communication_pattern='mesh'
        )

        small_throughput = self.evaluator.estimate_throughput(small_config)
        large_throughput = self.evaluator.estimate_throughput(large_config)

        self.assertLess(small_throughput, large_throughput)


class TestParetoFrontiers(unittest.TestCase):
    """Test Pareto frontier generation."""

    def test_dominance_relation(self):
        """Test Pareto dominance relation."""
        # For accuracy/cost: higher accuracy, lower cost dominates
        obj1 = (0.9, 1.0)  # (accuracy, cost)
        obj2 = (0.8, 1.5)

        optimizer = NSGA2Optimizer(population_size=10, generations=5)
        self.assertTrue(optimizer.dominates(obj1, obj2))
        self.assertFalse(optimizer.dominates(obj2, obj1))

    def test_non_dominated_sort(self):
        """Test fast non-dominated sort."""
        evaluator = AccuracyCostEvaluator()
        optimizer = NSGA2Optimizer(population_size=20, generations=5)

        # Create population
        population = []
        for _ in range(20):
            population.append(Configuration(
                model_size=np.random.randint(10, 500),
                checkpoint_frequency=np.random.randint(1, 30),
                cache_size_mb=np.random.randint(64, 2048),
                batch_size=np.random.randint(1, 32),
                compression_level=np.random.uniform(0, 1),
                temperature=np.random.uniform(0.1, 2.0),
                use_federated=np.random.choice([True, False]),
                replication_factor=np.random.randint(1, 4)
            ))

        fronts = optimizer.fast_non_dominated_sort(population, evaluator)

        self.assertGreater(len(fronts), 0)
        self.assertGreater(len(fronts[0]), 0)  # First front should have solutions


class TestConfigurationGeneration(unittest.TestCase):
    """Test configuration file generation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_generate_accuracy_cost_tiers(self):
        """Test accuracy/cost tier generation."""
        from pareto_accuracy_cost import generate_tier_configs

        # Create dummy Pareto front
        evaluator = AccuracyCostEvaluator()
        dummy_front = [
            Configuration(10, 5, 128, 1, 0.8, 1.0, False, 1),
            Configuration(100, 10, 512, 16, 0.5, 0.7, True, 2),
            Configuration(500, 20, 2048, 32, 0.0, 0.5, True, 3)
        ]

        configs = generate_tier_configs(dummy_front, evaluator, self.temp_dir)

        self.assertGreater(len(configs), 0)

        # Check file was created
        config_file = Path(self.temp_dir) / 'accuracy_cost_tiers.json'
        self.assertTrue(config_file.exists())

        # Validate JSON structure
        with open(config_file, 'r') as f:
            data = json.load(f)
            self.assertIn('BUDGET', data)


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine."""

    def test_user_priorities_normalization(self):
        """Test user priorities normalization."""
        from recommendation_engine import UserPriorities

        priorities = UserPriorities(
            accuracy=0.5,
            cost=0.3,
            latency=0.2,
            availability=0.0,
            scalability=0.0,
            complexity=0.0
        )

        normalized = priorities.normalize()

        total = sum([
            normalized.accuracy,
            normalized.cost,
            normalized.latency,
            normalized.availability,
            normalized.scalability,
            normalized.complexity
        ])

        self.assertAlmostEqual(total, 1.0, places=5)

    def test_scenario_creation(self):
        """Test predefined scenarios."""
        from recommendation_engine import Scenario

        production = Scenario.production()
        self.assertEqual(production.name, "PRODUCTION")
        self.assertGreater(production.priorities.availability, 0.2)

        edge = Scenario.edge()
        self.assertEqual(edge.name, "EDGE")
        self.assertGreater(edge.priorities.latency, 0.3)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAccuracyCostOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestSpeedQualityOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestRobustnessOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestScalabilityOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestParetoFrontiers))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendationEngine))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
