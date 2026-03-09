"""
Tests for workflow simulations
"""

import unittest
import numpy as np
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_patterns import (
    WorkflowSimulator,
    WorkflowPatternOptimizer,
    AgentConfig,
    Task,
    PatternType,
    create_sample_workflows
)
from agent_composition import (
    AgentTeamSimulator,
    CompositionOptimizer,
    TaskType,
    StrategyType,
    TeamConfig
)
from coordination_overhead import (
    CoordinationSimulator,
    GranularityOptimizer,
    Granularity,
    SyncStrategy,
    TaskDecomposition,
    CommunicationCost
)
from workflow_reliability import (
    ReliabilitySimulator,
    ReliabilityOptimizer,
    FailureScenario,
    FailureType,
    RetryStrategy,
    FallbackMode,
    ReliabilityConfig
)
from workflow_optimizer import (
    WorkflowOptimizer,
    WorkflowFeatureExtractor,
    WorkflowPredictor,
    PatternType as WOPatternType
)


class TestWorkflowPatterns(unittest.TestCase):
    """Test workflow pattern simulations"""

    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            AgentConfig('core', 1.0, 0.95, 0.001, 100),
            AgentConfig('role', 1.2, 0.90, 0.0015, 150),
            AgentConfig('task', 0.8, 0.85, 0.002, 50),
        ]
        self.simulator = WorkflowSimulator(self.agents)

    def test_sequential_pattern(self):
        """Test sequential workflow pattern"""
        tasks = [
            Task('t1', 'Task 1', 1.0, 0.5),
            Task('t2', 'Task 2', 2.0, 0.6),
            Task('t3', 'Task 3', 1.5, 0.4),
        ]

        metrics = self.simulator.simulate_sequential(tasks)

        self.assertGreater(metrics.completion_time, 0)
        self.assertGreater(metrics.quality_score, 0)
        self.assertLessEqual(metrics.quality_score, 1)
        self.assertEqual(metrics.agent_utilization, 1.0 / len(self.agents))

    def test_parallel_pattern(self):
        """Test parallel workflow pattern"""
        tasks = [
            Task('t1', 'Task 1', 1.0, 0.5),
            Task('t2', 'Task 2', 1.0, 0.5),
            Task('t3', 'Task 3', 1.0, 0.5),
        ]

        metrics = self.simulator.simulate_parallel(tasks)

        self.assertGreater(metrics.completion_time, 0)
        self.assertGreater(metrics.quality_score, 0)
        self.assertGreater(metrics.agent_utilization, 0)

    def test_pattern_optimizer(self):
        """Test pattern optimizer"""
        optimizer = WorkflowPatternOptimizer(self.simulator)

        tasks = create_sample_workflows()['data_pipeline']
        pattern, metrics = optimizer.find_optimal_pattern(tasks, iterations=2)

        self.assertIsInstance(pattern, PatternType)
        self.assertIsNotNone(metrics)


class TestAgentComposition(unittest.TestCase):
    """Test agent composition simulations"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = AgentTeamSimulator()

    def test_team_creation(self):
        """Test team creation with different strategies"""
        config = TeamConfig(StrategyType.HYBRID, 5, 5, 0)
        team = self.simulator.create_team(config)

        self.assertGreater(len(team), 0)
        self.assertLessEqual(len(team), 10)

    def test_team_performance(self):
        """Test team performance simulation"""
        config = TeamConfig(StrategyType.GENERALIST, 5, 0, 0)
        team = self.simulator.create_team(config)

        task_type = TaskType("test", 0.5, 0.5, 0.5, 0.8)
        metrics = self.simulator.simulate_team_performance(team, task_type, num_tasks=10)

        self.assertGreater(metrics.completion_time, 0)
        self.assertGreater(metrics.quality_score, 0)
        self.assertGreater(metrics.cost_efficiency, 0)

    def test_composition_optimizer(self):
        """Test composition optimizer"""
        optimizer = CompositionOptimizer(self.simulator)

        task_type = TaskType("test", 0.5, 0.5, 0.5, 0.8)
        config, metrics = optimizer.optimize_for_task_type(task_type, iterations=5)

        self.assertIsNotNone(config)
        self.assertIsNotNone(metrics)


class TestCoordinationOverhead(unittest.TestCase):
    """Test coordination overhead simulations"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = CoordinationSimulator(num_agents=10)

    def test_fine_grained_simulation(self):
        """Test fine-grained task decomposition"""
        decomposition = TaskDecomposition(
            Granularity.FINE,
            num_tasks=100,
            avg_task_duration=0.1,
            dependencies=50,
            data_transfer=0.001
        )

        metrics = self.simulator.simulate_fine_grained(decomposition, SyncStrategy.ASYNC)

        self.assertGreater(metrics.execution_time, 0)
        self.assertGreater(metrics.throughput, 0)
        self.assertGreater(metrics.overhead_ratio, 0)

    def test_coarse_grained_simulation(self):
        """Test coarse-grained task decomposition"""
        decomposition = TaskDecomposition(
            Granularity.COARSE,
            num_tasks=10,
            avg_task_duration=10.0,
            dependencies=2,
            data_transfer=0.1
        )

        metrics = self.simulator.simulate_coarse_grained(decomposition, SyncStrategy.SYNC)

        self.assertGreater(metrics.execution_time, 0)
        self.assertLess(metrics.overhead_ratio, 0.5)  # Coarse should have lower overhead

    def test_granularity_optimizer(self):
        """Test granularity optimizer"""
        optimizer = GranularityOptimizer(self.simulator)

        granularity, strategy, metrics = optimizer.find_optimal_granularity(
            total_work=100.0,
            data_per_unit=1.0,
            dependency_ratio=0.1
        )

        self.assertIsNotNone(granularity)
        self.assertIsNotNone(strategy)
        self.assertIsNotNone(metrics)


class TestWorkflowReliability(unittest.TestCase):
    """Test workflow reliability simulations"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = ReliabilitySimulator(num_agents=10, num_tasks=50)

    def test_no_failures(self):
        """Test workflow with no failures"""
        scenarios = []  # No failure scenarios
        config = ReliabilityConfig(
            RetryStrategy.NONE,
            max_retries=0,
            fallback_mode=FallbackMode.FAIL_FAST,
            circuit_breaker_threshold=0.5,
            circuit_breaker_window=10,
            timeout_ms=5000
        )

        metrics = self.simulator.simulate_workflow(scenarios, config)

        self.assertEqual(metrics.success_rate, 1.0)
        self.assertEqual(metrics.failure_rate, 0.0)

    def test_with_failures(self):
        """Test workflow with failures"""
        scenarios = [
            FailureScenario(FailureType.AGENT_FAILURE, 0.1, 1.0, 'single_agent'),
            FailureScenario(FailureType.TIMEOUT, 0.1, 0.5, 'single_agent'),
        ]
        config = ReliabilityConfig(
            RetryStrategy.EXPONENTIAL_BACKOFF,
            max_retries=3,
            fallback_mode=FallbackMode.DEGRADE_GRACEFULLY,
            circuit_breaker_threshold=0.5,
            circuit_breaker_window=10,
            timeout_ms=5000
        )

        metrics = self.simulator.simulate_workflow(scenarios, config)

        self.assertGreater(metrics.success_rate, 0)
        self.assertGreater(metrics.retry_count, 0)

    def test_reliability_optimizer(self):
        """Test reliability optimizer"""
        scenarios = [
            FailureScenario(FailureType.AGENT_FAILURE, 0.05, 1.0, 'single_agent'),
        ]
        optimizer = ReliabilityOptimizer(self.simulator)

        config, metrics = optimizer.find_optimal_config(scenarios, iterations=5)

        self.assertIsNotNone(config)
        self.assertIsNotNone(metrics)


class TestWorkflowOptimizer(unittest.TestCase):
    """Test workflow optimizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = WorkflowOptimizer()
        self.predictor = self.optimizer.predictor
        self.feature_extractor = WorkflowFeatureExtractor()

    def test_feature_extraction(self):
        """Test feature extraction from workflows"""
        workflow = {
            'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 1.0},
                {'duration': 2.0, 'dependencies': [0], 'data_size': 2.0},
                {'duration': 1.5, 'dependencies': [1], 'data_size': 1.5},
            ],
            'criticality': 0.8
        }

        features = self.feature_extractor.extract_features(workflow)

        self.assertEqual(features.num_tasks, 3)
        self.assertGreater(features.complexity_score, 0)
        self.assertGreater(features.dependency_ratio, 0)

    def test_pattern_prediction(self):
        """Test pattern prediction"""
        # Train with some data
        training_data = [
            {
                'workflow': {
                    'tasks': [
                        {'duration': 1.0, 'dependencies': [], 'data_size': 1.0}
                        for _ in range(5)
                    ],
                    'criticality': 0.5
                },
                'pattern': 'parallel',
                'agent_count': 5,
                'completion_time': 2.0,
                'quality_score': 0.9,
                'success': True,
                'cost': 0.5
            }
        ]

        self.predictor.train(training_data)

        # Test prediction
        workflow = {
            'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 1.0}
                for _ in range(10)
            ],
            'criticality': 0.6
        }

        pattern, confidence = self.predictor.predict_pattern(workflow)

        self.assertIsNotNone(pattern)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)

    def test_workflow_optimization(self):
        """Test complete workflow optimization"""
        workflow = {
            'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 1.0},
                {'duration': 2.0, 'dependencies': [0], 'data_size': 2.0},
            ],
            'criticality': 0.7
        }

        config = self.optimizer.optimize_workflow(workflow)

        self.assertIn('pattern', config)
        self.assertIn('agent_count', config)
        self.assertIn('confidence', config)
        self.assertIn('expected_performance', config)


class TestIntegration(unittest.TestCase):
    """Integration tests for workflow domain"""

    def test_end_to_end_workflow(self):
        """Test complete workflow from specification to configuration"""
        # Create workflow specification
        workflow = {
            'name': 'test_pipeline',
            'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 1.0},
                {'duration': 2.0, 'dependencies': [0], 'data_size': 2.0},
                {'duration': 1.5, 'dependencies': [1], 'data_size': 1.5},
            ],
            'criticality': 0.8
        }

        # Optimize workflow
        optimizer = WorkflowOptimizer()
        config = optimizer.optimize_workflow(workflow)

        # Verify configuration
        self.assertIsNotNone(config)
        self.assertIn('pattern', config)
        self.assertIn('agent_count', config)
        self.assertIn('parameters', config)

    def test_multi_scenario_comparison(self):
        """Test comparison across multiple scenarios"""
        scenarios = [
            {'name': 'simple', 'tasks': [{'duration': 1.0, 'dependencies': []}] * 5},
            {'name': 'complex', 'tasks': [
                {'duration': 1.0, 'dependencies': [], 'data_size': 1.0},
                {'duration': 2.0, 'dependencies': [0], 'data_size': 2.0},
                {'duration': 1.5, 'dependencies': [0], 'data_size': 1.5},
                {'duration': 1.0, 'dependencies': [1, 2], 'data_size': 1.0},
            ]},
        ]

        results = {}
        optimizer = WorkflowOptimizer()

        for scenario in scenarios:
            config = optimizer.optimize_workflow(scenario)
            results[scenario['name']] = config

        self.assertEqual(len(results), 2)
        self.assertIn('simple', results)
        self.assertIn('complex', results)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowPatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentComposition))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinationOverhead))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowReliability))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
