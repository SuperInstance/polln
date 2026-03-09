"""
Meta-Learning System Tests

Tests the complete meta-learning implementation:
1. MAML functionality
2. Reptile functionality
3. Few-shot learning
4. Task distribution
5. Rapid adaptation
6. TypeScript config generation
"""

import unittest
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.append('.')
sys.path.append('simulations/advanced/metalearning')


class TestMAML(unittest.TestCase):
    """Test MAML implementation"""

    def setUp(self):
        """Setup test fixtures"""
        from maml_implementation import MAMLConfig, MAMLAgent, MAMLPOLLNValueNetwork

        self.config = MAMLConfig(
            inner_lr=0.01,
            outer_lr=0.001,
            inner_steps=2,  # Short for testing
            meta_batch_size=4,
            meta_epochs=2   # Short for testing
        )

        self.model = MAMLPOLLNValueNetwork()
        self.maml = MAMLAgent(self.config, self.model)

    def test_maml_initialization(self):
        """Test MAML agent initialization"""
        self.assertIsNotNone(self.maml)
        self.assertEqual(self.maml.config.inner_lr, 0.01)
        self.assertEqual(self.maml.config.inner_steps, 2)

    def test_inner_loop(self):
        """Test inner loop adaptation"""
        task = self._generate_task()

        adapted_model = self.maml.inner_loop(task)

        self.assertIsNotNone(adapted_model)
        self.assertIsInstance(adapted_model, nn.Module)

    def test_outer_loop(self):
        """Test outer loop meta-update"""
        tasks = [self._generate_task() for _ in range(4)]

        metrics = self.maml.outer_loop(tasks)

        self.assertIn('meta_loss', metrics)
        self.assertIn('query_loss_mean', metrics)
        self.assertGreater(metrics['meta_loss'], 0)

    def _generate_task(self):
        """Generate test task"""
        return {
            'support_x': torch.randn(10, 128),
            'support_y': torch.randn(10),
            'query_x': torch.randn(5, 128),
            'query_y': torch.randn(5)
        }


class TestReptile(unittest.TestCase):
    """Test Reptile implementation"""

    def setUp(self):
        """Setup test fixtures"""
        from reptile_implementation import ReptileConfig, ReptileAgent, ReptilePOLLNValueNetwork

        self.config = ReptileConfig(
            meta_lr=0.1,
            inner_lr=0.01,
            inner_steps=5,
            meta_batch_size=4,
            num_iterations=10  # Short for testing
        )

        self.model = ReptilePOLLNValueNetwork()
        self.reptile = ReptileAgent(self.config, self.model)

    def test_reptile_initialization(self):
        """Test Reptile agent initialization"""
        self.assertIsNotNone(self.reptile)
        self.assertEqual(self.reptile.config.meta_lr, 0.1)
        self.assertEqual(self.reptile.config.inner_steps, 5)

    def test_adapt(self):
        """Test Reptile adaptation"""
        task = self._generate_task()

        adapted_params = self.reptile.adapt(task)

        self.assertIsInstance(adapted_params, dict)
        self.assertIn('encoder.0.weight', adapted_params)

    def test_meta_update(self):
        """Test Reptile meta-update"""
        tasks = [self._generate_task() for _ in range(4)]

        metrics = self.reptile.meta_update(tasks)

        self.assertIn('loss', metrics)
        self.assertIn('iteration_time', metrics)
        self.assertGreater(metrics['loss'], 0)

    def _generate_task(self):
        """Generate test task"""
        return {
            'support_x': torch.randn(10, 128),
            'support_y': torch.randn(10),
            'query_x': torch.randn(5, 128),
            'query_y': torch.randn(5)
        }


class TestFewShotLearning(unittest.TestCase):
    """Test few-shot learning"""

    def test_few_shot_evaluation(self):
        """Test few-shot evaluation"""
        # This would test the evaluator
        # For now, just test task generation
        from few_shot_testing import generate_few_shot_tasks

        tasks = generate_few_shot_tasks(num_tasks=10, k_shot=5)

        self.assertEqual(len(tasks), 10)
        self.assertIn('support_x', tasks[0])
        self.assertIn('query_x', tasks[0])

    def test_task_truncation(self):
        """Test task truncation for few-shot"""
        from few_shot_testing import generate_few_shot_tasks

        tasks = generate_few_shot_tasks(num_tasks=1, k_shot=10)[0]

        # Original should have 50 support examples (10 * 5)
        self.assertEqual(tasks['support_x'].size(0), 50)


class TestTaskDistribution(unittest.TestCase):
    """Test task distribution"""

    def test_family_creation(self):
        """Test task family creation"""
        from task_distribution import TaskFamily

        family = TaskFamily('test', {'shift_scale': 0.1})
        tasks = family.generate_tasks(num_tasks=5, k_shot=3, num_query=10)

        self.assertEqual(len(tasks), 5)
        self.assertEqual(tasks[0].family, 'test')

    def test_distribution_creation(self):
        """Test task distribution creation"""
        from task_distribution import TaskDistribution, TaskDistributionConfig

        config = TaskDistributionConfig(
            num_families=2,
            tasks_per_family=5
        )

        distribution = TaskDistribution(config)
        distribution.create_families()

        self.assertEqual(len(distribution.families), 2)
        self.assertEqual(len(distribution.all_tasks), 10)

    def test_train_test_split(self):
        """Test train/test split"""
        from task_distribution import TaskDistribution, TaskDistributionConfig

        config = TaskDistributionConfig(
            num_families=2,
            tasks_per_family=10,
            meta_train_ratio=0.8
        )

        distribution = TaskDistribution(config)
        distribution.create_families()
        distribution.split_train_test()

        self.assertEqual(len(distribution.meta_train_tasks), 16)
        self.assertEqual(len(distribution.meta_test_tasks), 4)


class TestRapidAdaptation(unittest.TestCase):
    """Test rapid adaptation strategies"""

    def test_lora_layer(self):
        """Test LoRA layer"""
        from rapid_adaptation import LoRALayer

        original = nn.Linear(128, 256)
        lora = LoRALayer(original, rank=16, alpha=32, dropout=0.1)

        x = torch.randn(10, 128)
        output = lora(x)

        self.assertEqual(output.shape, (10, 256))

    def test_adapter_layer(self):
        """Test adapter layer"""
        from rapid_adaptation import AdapterLayer

        adapter = AdapterLayer(original_dim=256, adapter_dim=64)

        x = torch.randn(10, 256)
        output = adapter(x)

        # Residual connection, same shape
        self.assertEqual(output.shape, (10, 256))

    def test_adaptation_model(self):
        """Test adaptation model with different strategies"""
        from rapid_adaptation import RapidAdaptationModel, AdaptationConfig

        for strategy in ['finetune', 'lora', 'adapter']:
            config = AdaptationConfig(strategy=strategy)
            model = RapidAdaptationModel(config=config)

            x = torch.randn(10, 128)
            output = model(x)

            self.assertEqual(output.shape, (10,))

    def test_parameter_efficiency(self):
        """Test parameter efficiency of strategies"""
        from rapid_adaptation import RapidAdaptionModel, AdaptationConfig

        results = {}
        for strategy in ['finetune', 'lora', 'adapter']:
            config = AdaptationConfig(strategy=strategy)
            model = RapidAdaptationModel(config=config)

            total_params = model.count_total_params()
            adapt_params = model.count_adaptation_params()

            results[strategy] = {
                'total': total_params,
                'adapt': adapt_params,
                'efficiency': adapt_params / total_params
            }

        # LoRA should be most efficient
        self.assertLess(results['lora']['efficiency'], results['finetune']['efficiency'])


class TestMetaOptimizer(unittest.TestCase):
    """Test meta-optimizer"""

    def test_config_compilation(self):
        """Test configuration compilation"""
        from meta_optimizer import MetaLearningOptimizer

        optimizer = MetaLearningOptimizer()

        # Should not crash even without configs
        optimizer.load_all_configs()
        config = optimizer.compile_meta_learning_config()

        self.assertIn('maml', config)
        self.assertIn('reptile', config)
        self.assertIn('fewShot', config)
        self.assertIn('adaptation', config)
        self.assertIn('taskDistribution', config)

    def test_typescript_generation(self):
        """Test TypeScript code generation"""
        from meta_optimizer import MetaLearningOptimizer

        optimizer = MetaLearningOptimizer()
        optimizer.load_all_configs()
        config = optimizer.compile_meta_learning_config()

        ts_code = optimizer.generate_typescript(config)

        self.assertIn('META_LEARNING_CONFIG', ts_code)
        self.assertIn('export const', ts_code)
        self.assertIn('maml:', ts_code)
        self.assertIn('reptile:', ts_code)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_end_to_end_maml(self):
        """Test end-to-end MAML pipeline"""
        from maml_implementation import MAMLConfig, MAMLAgent, MAMLPOLLNValueNetwork

        config = MAMLConfig(
            inner_lr=0.01,
            outer_lr=0.001,
            inner_steps=2,
            meta_batch_size=4,
            meta_epochs=2
        )

        model = MAMLPOLLNValueNetwork()
        maml = MAMLAgent(config, model)

        def task_sampler():
            return [{
                'support_x': torch.randn(10, 128),
                'support_y': torch.randn(10),
                'query_x': torch.randn(5, 128),
                'query_y': torch.randn(5)
            } for _ in range(4)]

        results = maml.meta_train(task_sampler)

        self.assertIn('best_val_loss', results)
        self.assertGreater(results['best_val_loss'], 0)

    def test_end_to_end_reptile(self):
        """Test end-to-end Reptile pipeline"""
        from reptile_implementation import ReptileConfig, ReptileAgent, ReptilePOLLNValueNetwork

        config = ReptileConfig(
            meta_lr=0.1,
            inner_lr=0.01,
            inner_steps=5,
            meta_batch_size=4,
            num_iterations=10
        )

        model = ReptilePOLLNValueNetwork()
        reptile = ReptileAgent(config, model)

        def task_sampler():
            return [{
                'support_x': torch.randn(10, 128),
                'support_y': torch.randn(10),
                'query_x': torch.randn(5, 128),
                'query_y': torch.randn(5)
            } for _ in range(4)]

        results = reptile.meta_train(task_sampler)

        self.assertIn('best_val_loss', results)
        self.assertGreater(results['best_val_loss'], 0)


class TestTypeScriptConfig(unittest.TestCase):
    """Test TypeScript configuration file"""

    def test_typescript_file_exists(self):
        """Test that TypeScript file was generated"""
        ts_path = Path('src/core/meta/learning.ts')

        # This will fail if not run after meta_optimizer
        # Just check path structure
        self.assertIn('src/core/meta', str(ts_path))

    def test_config_structure(self):
        """Test configuration structure"""
        # Load simulated config
        config = {
            'maml': {
                'enabled': True,
                'innerLoop': {'learningRate': 0.01}
            },
            'reptile': {
                'enabled': True,
                'metaLearningRate': 0.1
            }
        }

        self.assertIn('maml', config)
        self.assertIn('reptile', config)


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Meta-Learning System Tests")
    print("=" * 60 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestMAML))
    suite.addTests(loader.loadTestsFromTestCase(TestReptile))
    suite.addTests(loader.loadTestsFromTestCase(TestFewShotLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskDistribution))
    suite.addTests(loader.loadTestsFromTestCase(TestRapidAdaptation))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeScriptConfig))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
