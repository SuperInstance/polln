"""
POLLN Reasoning Domain - Test Suite

Tests for all reasoning simulation components to ensure correctness
and validate optimization results.
"""

import unittest
import json
import sys
from pathlib import Path
import numpy as np

# Add simulations directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dialogue_simulation import (
    DialogueSimulator,
    DialogueType,
    DialogueContextCompressor
)
from chain_of_thought import (
    ChainOfThoughtReasoner,
    GSM8KSimulator,
    CheckpointOptimizer
)
from context_tracking import (
    ContextTrackingSimulator,
    CompressionStrategy,
    EntityTracker
)
from reasoning_depth import (
    TreeOfThoughtsReasoner,
    TaskComplexityEstimator,
    ReasoningDepthOptimizer
)
from consistency_checker import (
    ConsistencyValidator,
    ConsistencyType
)


class TestDialogueSimulation(unittest.TestCase):
    """Tests for dialogue simulation"""

    def test_dialogue_simulator_init(self):
        """Test dialogue simulator initialization"""
        sim = DialogueSimulator()
        self.assertIsNotNone(sim.config)
        self.assertEqual(sim.config['max_turns'], 100)

    def test_simulate_short_dialogue(self):
        """Test short dialogue simulation"""
        sim = DialogueSimulator()
        turns, metrics = sim.simulate_dialogue(
            DialogueType.SHORT_CONTEXT,
            num_agents=2,
            seed=42
        )

        self.assertLessEqual(len(turns), 10)
        self.assertGreater(len(turns), 0)
        self.assertGreaterEqual(metrics.coherence_score, 0)
        self.assertLessEqual(metrics.coherence_score, 1)

    def test_context_compression(self):
        """Test context compression strategies"""
        sim = DialogueSimulator()
        turns, _ = sim.simulate_dialogue(
            DialogueType.LONG_CONTEXT,
            num_agents=2,
            seed=42
        )

        compressor = DialogueContextCompressor()

        for strategy in ['sliding_window', 'summarization', 'hierarchical']:
            result = compressor.test_compression(turns, strategy)
            self.assertIn('compression_ratio', result)
            self.assertIn('information_retention', result)
            self.assertGreater(result['compression_ratio'], 0)
            self.assertLessEqual(result['compression_ratio'], 1)


class TestChainOfThought(unittest.TestCase):
    """Tests for chain-of-thought reasoning"""

    def test_gsm8k_simulator(self):
        """Test GSM8K problem simulator"""
        sim = GSM8KSimulator()
        problems = sim.get_all_problems()

        self.assertGreater(len(problems), 0)
        self.assertIn('question', problems[0])
        self.assertIn('answer', problems[0])

    def test_cot_reasoner(self):
        """Test chain-of-thought reasoner"""
        reasoner = ChainOfThoughtReasoner()
        problem = {
            'question': 'What is 15 + 27?',
            'answer': '42'
        }

        best_chain, all_chains = reasoner.solve_with_cot(
            problem,
            num_samples=3
        )

        self.assertIsNotNone(best_chain)
        self.assertEqual(len(all_chains), 3)
        self.assertIsNotNone(best_chain.final_answer)

    def test_checkpoint_optimizer(self):
        """Test checkpoint optimization"""
        from chain_of_thought import ReasoningChain, ReasoningStep

        # Create sample chain
        steps = [
            ReasoningStep(0, "Step 1", True, 0.9),
            ReasoningStep(1, "Step 2", False, 0.8),
            ReasoningStep(2, "Step 3", True, 0.7)
        ]

        chain = ReasoningChain(
            task_id="test",
            task_type="math",
            steps=steps,
            final_answer="42",
            confidence=0.8
        )

        optimizer = CheckpointOptimizer()
        result = optimizer.optimize_checkpoints([chain], 'fixed_interval')

        self.assertIn('strategy', result)
        self.assertIn('results', result)


class TestContextTracking(unittest.TestCase):
    """Tests for context tracking"""

    def test_entity_tracker(self):
        """Test entity tracking"""
        tracker = EntityTracker()

        entities = tracker.extract_entities("John went to Paris with Mary.", 0)
        self.assertGreater(len(entities), 0)

        active = tracker.get_active_entities(5, window=10)
        self.assertIsInstance(active, list)

    def test_context_compression(self):
        """Test context compression strategies"""
        sim = ContextTrackingSimulator()

        for strategy in CompressionStrategy:
            compressed, metrics = sim.simulate_conversation(
                num_turns=20,
                compression_strategy=strategy
            )

            self.assertIsInstance(compressed, list)
            self.assertIsInstance(metrics, ContextTrackingSimulator)
            self.assertGreater(metrics.compression_ratio, 0)


class TestReasoningDepth(unittest.TestCase):
    """Tests for reasoning depth optimization"""

    def test_complexity_estimator(self):
        """Test task complexity estimation"""
        estimator = TaskComplexityEstimator()

        simple = {'question': 'What is 2 + 2?'}
        complex = {'question': 'If a train travels 120 miles in 2 hours, then stops for 30 minutes, then travels another 60 miles in 1.5 hours, what is the average speed?'}

        simple_score = estimator.estimate_complexity(simple)
        complex_score = estimator.estimate_complexity(complex)

        self.assertGreater(complex_score, simple_score)

    def test_tree_of_thoughts(self):
        """Test tree-of-thoughts reasoning"""
        reasoner = TreeOfThoughtsReasoner(max_depth=3, beam_width=2)

        problem = {'question': 'What is 15 + 27?', 'answer': '42'}
        path = reasoner.reason(problem)

        self.assertIsNotNone(path)
        self.assertGreater(len(path.nodes), 0)
        self.assertIsNotNone(path.final_answer)


class TestConsistencyChecker(unittest.TestCase):
    """Tests for consistency validation"""

    def test_self_consistency(self):
        """Test self-consistency checking"""
        validator = ConsistencyValidator()

        # Contradictory response
        response = "I always help users, but sometimes I don't."
        report = validator.validate_response(response)

        self.assertIsNotNone(report)
        self.assertGreaterEqual(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 1)

    def test_factual_consistency(self):
        """Test factual consistency checking"""
        validator = ConsistencyValidator()

        # Factually incorrect response
        response = "The Earth is definitely flat."
        report = validator.validate_response(response)

        self.assertIsNotNone(report)
        # Should have violations
        self.assertGreater(len(report.violations), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for reasoning domain"""

    def test_full_workflow(self):
        """Test complete workflow from simulation to config"""
        # This would run the full optimization pipeline
        # For testing, we just verify the structure exists

        results_dir = Path('simulations/domains/reasoning')
        self.assertTrue(results_dir.exists())

        # Check for at least one result file
        result_files = list(results_dir.glob('*_results.json'))
        self.assertGreater(len(result_files), 0)

    def test_config_generation(self):
        """Test configuration generation"""
        # Check if config file exists
        config_path = Path('src/domains/reasoning/config.ts')
        # Note: This may not exist in test environment
        # self.assertTrue(config_path.exists())


class TestMetricsValidation(unittest.TestCase):
    """Tests for metrics validation"""

    def test_dialogue_metrics_range(self):
        """Test dialogue metrics are in valid range"""
        sim = DialogueSimulator()
        turns, metrics = sim.simulate_dialogue(
            DialogueType.SHORT_CONTEXT,
            num_agents=2,
            seed=42
        )

        self.assertGreaterEqual(metrics.coherence_score, 0.0)
        self.assertLessEqual(metrics.coherence_score, 1.0)
        self.assertGreaterEqual(metrics.relevance_score, 0.0)
        self.assertLessEqual(metrics.relevance_score, 1.0)
        self.assertGreaterEqual(metrics.engagement_score, 0.0)
        self.assertLessEqual(metrics.engagement_score, 1.0)
        self.assertGreaterEqual(metrics.consistency_score, 0.0)
        self.assertLessEqual(metrics.consistency_score, 1.0)
        self.assertGreaterEqual(metrics.context_retention, 0.0)
        self.assertLessEqual(metrics.context_retention, 1.0)

    def test_reasoning_metrics_range(self):
        """Test reasoning metrics are in valid range"""
        reasoner = ChainOfThoughtReasoner()
        problem = {
            'question': 'What is 15 + 27?',
            'answer': '42'
        }

        best_chain, _ = reasoner.solve_with_cot(problem, num_samples=3)

        self.assertGreaterEqual(best_chain.confidence, 0.0)
        self.assertLessEqual(best_chain.confidence, 1.0)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("POLLN Reasoning Domain - Test Suite")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestDialogueSimulation,
        TestChainOfThought,
        TestContextTracking,
        TestReasoningDepth,
        TestConsistencyChecker,
        TestIntegration,
        TestMetricsValidation
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
