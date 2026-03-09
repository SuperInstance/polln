#!/usr/bin/env python3
"""
Test suite for POLLN debugging tools.

Tests all debugging tools including A2A tracer, agent inspector,
colony diagnostics, value network debugger, issue detector, and replay debugger.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time

# Import debugging tools
import sys
sys.path.insert(0, str(Path(__file__).parent))

from a2a_tracer import A2ATracer, A2APackageSnapshot, A2APackageEvent
from agent_inspector import AgentInspector, AgentStateSnapshot
from colony_diagnostics import ColonyDiagnostics, HealthMetric
from value_network_debugger import ValueNetworkDebugger, ValueUpdateEvent
from issue_detector import IssueDetector, DetectedIssue
from replay_debugger import ReplayDebugger, ExecutionEvent


class TestA2ATracer(unittest.TestCase):
    """Test A2A package tracer."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracer = A2ATracer("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_trace_package(self):
        """Test tracing an A2A package."""
        package_data = {
            'id': 'pkg-1',
            'timestamp': time.time(),
            'senderId': 'agent-1',
            'receiverId': 'agent-2',
            'type': 'test',
            'layer': 'DELIBERATE',
            'privacyLevel': 'PRIVATE',
            'parentIds': [],
            'causalChainId': 'chain-1',
            'payload': {'test': 'data'}
        }

        snapshot = self.tracer.trace_package(package_data, 'agent-1', 'in_transit')

        self.assertIsInstance(snapshot, A2APackageSnapshot)
        self.assertEqual(snapshot.id, 'pkg-1')
        self.assertEqual(snapshot.sender_id, 'agent-1')
        self.assertEqual(snapshot.receiver_id, 'agent-2')
        self.assertIn('pkg-1', self.tracer.packages)

    def test_causal_chain_analysis(self):
        """Test causal chain analysis."""
        # Create packages with causal relationships
        for i in range(3):
            package_data = {
                'id': f'pkg-{i}',
                'timestamp': time.time(),
                'senderId': f'agent-{i}',
                'receiverId': f'agent-{i+1}',
                'type': 'test',
                'layer': 'DELIBERATE',
                'privacyLevel': 'PRIVATE',
                'parentIds': [f'pkg-{i-1}'] if i > 0 else [],
                'causalChainId': 'chain-1',
                'payload': {}
            }
            self.tracer.trace_package(package_data, f'agent-{i}', 'delivered')

        analysis = self.tracer.analyze_causal_chain('chain-1')

        self.assertEqual(analysis.chain_id, 'chain-1')
        self.assertEqual(analysis.total_packages, 3)
        self.assertFalse(analysis.cycle_detected)

    def test_generate_trace_report(self):
        """Test generating trace report."""
        # Add a test package
        package_data = {
            'id': 'pkg-1',
            'timestamp': time.time(),
            'senderId': 'agent-1',
            'receiverId': 'agent-2',
            'type': 'test',
            'layer': 'DELIBERATE',
            'privacyLevel': 'PRIVATE',
            'parentIds': [],
            'causalChainId': 'chain-1',
            'payload': {}
        }
        self.tracer.trace_package(package_data, 'agent-1', 'delivered')

        report = self.tracer.generate_trace_report()

        self.assertIn('colony_id', report)
        self.assertIn('summary', report)
        self.assertIn('packages', report)
        self.assertEqual(report['summary']['total_packages'], 1)


class TestAgentInspector(unittest.TestCase):
    """Test agent inspector."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.inspector = AgentInspector("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_inspect_agent(self):
        """Test inspecting an agent."""
        agent_data = {
            'id': 'agent-1',
            'typeId': 'TaskAgent',
            'status': 'active',
            'lastActive': time.time(),
            'valueFunction': 0.7,
            'successCount': 80,
            'failureCount': 20,
            'avgLatencyMs': 150,
            'stateSnapshot': {'test': 'data'}
        }

        snapshot = self.inspector.inspect_agent(agent_data)

        self.assertIsInstance(snapshot, AgentStateSnapshot)
        self.assertEqual(snapshot.agent_id, 'agent-1')
        self.assertEqual(snapshot.status, 'active')
        self.assertAlmostEqual(snapshot.success_rate, 0.8, places=1)
        self.assertFalse(snapshot.is_hung)

    def test_detect_hung_agents(self):
        """Test detecting hung agents."""
        # Add an agent with old lastActive time
        agent_data = {
            'id': 'hung-agent',
            'typeId': 'TaskAgent',
            'status': 'active',
            'lastActive': time.time() - 400,  # 400 seconds ago
            'valueFunction': 0.5,
            'successCount': 0,
            'failureCount': 0
        }
        self.inspector.inspect_agent(agent_data)

        hung = self.inspector.detect_hung_agents(timeout_seconds=300)

        self.assertIn('hung-agent', hung)

    def test_inspect_synapse(self):
        """Test inspecting a synapse."""
        synapse_data = {
            'weight': 0.8,
            'coactivationCount': 100,
            'lastCoactivated': time.time() - 100
        }

        inspection = self.inspector.inspect_synapse('agent-1', 'agent-2', synapse_data)

        self.assertEqual(inspection.source_id, 'agent-1')
        self.assertEqual(inspection.target_id, 'agent-2')
        self.assertEqual(inspection.weight, 0.8)


class TestColonyDiagnostics(unittest.TestCase):
    """Test colony diagnostics."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.diagnostics = ColonyDiagnostics("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_check_agent_health(self):
        """Test checking agent health."""
        agent_data = {
            'id': 'agent-1',
            'status': 'active',
            'valueFunction': 0.3,  # Low value
            'successCount': 3,
            'failureCount': 7,
            'lastActive': time.time()
        }

        metrics = self.diagnostics.check_agent_health('agent-1', agent_data)

        self.assertGreater(len(metrics), 0)
        # Should have warning about low value function
        self.assertTrue(any('value' in m.name.lower() for m in metrics))

    def test_record_resource_usage(self):
        """Test recording resource usage."""
        resource_data = {
            'cpuPercent': 85,
            'memoryMb': 750,
            'networkIoMb': 50,
            'activeConnections': 10,
            'queueDepth': 800
        }

        usage = self.diagnostics.record_resource_usage('agent-1', resource_data)

        self.assertEqual(usage.agent_id, 'agent-1')
        self.assertEqual(usage.cpu_percent, 85)
        self.assertEqual(usage.memory_status, 'warning')

    def test_detect_deadlocks(self):
        """Test deadlock detection."""
        # Create a simple waiting cycle
        self.diagnostics.record_resource_usage('agent-1', {'queueDepth': 1500, 'cpuPercent': 50})
        self.diagnostics.record_resource_usage('agent-2', {'queueDepth': 1500, 'cpuPercent': 50})
        self.diagnostics.record_communication('agent-1', 'agent-2')
        self.diagnostics.record_communication('agent-2', 'agent-1')

        deadlock = self.diagnostics.detect_deadlocks()

        self.assertIsInstance(deadlock, dict)


class TestValueNetworkDebugger(unittest.TestCase):
    """Test value network debugger."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.debugger = ValueNetworkDebugger("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_record_update(self):
        """Test recording value updates."""
        self.debugger.record_update(
            'agent-1',
            0.5,
            0.6,
            reward=1.0,
            td_error=0.1,
            eligibility_trace=0.9,
            learning_rate=0.1,
            lambda_param=0.9
        )

        self.assertIn('agent-1', self.debugger.value_history)
        self.assertEqual(len(self.debugger.value_history['agent-1']), 1)

    def test_analyze_convergence(self):
        """Test convergence analysis."""
        # Create a converging sequence
        values = [0.5 + 0.5 * (0.9 ** i) for i in range(100)]
        for v in values:
            self.debugger.value_history['agent-1'].append(v)

        analysis = self.debugger.analyze_convergence('agent-1')

        self.assertTrue(analysis.stability_score > 0.5)
        self.assertFalse(analysis.oscillation_detected)

    def test_detect_oscillation(self):
        """Test oscillation detection."""
        # Create an oscillating sequence
        values = [0.5 + 0.3 * (-1) ** i for i in range(50)]
        for v in values:
            self.debugger.value_history['agent-1'].append(v)

        analysis = self.debugger.analyze_convergence('agent-1')

        self.assertTrue(analysis.oscillation_detected)


class TestIssueDetector(unittest.TestCase):
    """Test issue detector."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = IssueDetector("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_check_memory_leaks(self):
        """Test memory leak detection."""
        agent_data = {
            'id': 'agent-1',
            'memoryMb': 950  # Over critical threshold
        }

        issue = self.detector.check_memory_leaks(agent_data)

        self.assertIsNotNone(issue)
        self.assertEqual(issue.severity, 'critical')
        self.assertEqual(issue.category, 'memory')

    def test_check_stuck_agents(self):
        """Test stuck agent detection."""
        agent_data = {
            'id': 'stuck-agent',
            'status': 'active',
            'lastActive': time.time() - 700  # 700 seconds ago
        }

        issue = self.detector.check_stuck_agents(agent_data)

        self.assertIsNotNone(issue)
        self.assertEqual(issue.severity, 'critical')
        self.assertEqual(issue.category, 'agent_hang')

    def test_check_value_anomalies(self):
        """Test value anomaly detection."""
        agent_data = {
            'id': 'agent-1',
            'valueFunction': 0.05  # Very low
        }

        issue = self.detector.check_value_anomalies(agent_data)

        self.assertIsNotNone(issue)
        self.assertEqual(issue.category, 'value_function')

    def test_detect_patterns(self):
        """Test pattern detection."""
        # Add multiple issues of same category
        for i in range(3):
            agent_data = {
                'id': f'agent-{i}',
                'memoryMb': 950
            }
            issue = self.detector.check_memory_leaks(agent_data)
            self.detector.detected_issues[issue.issue_id] = issue

        patterns = self.detector.detect_patterns()

        self.assertGreater(len(patterns), 0)
        self.assertTrue(any('memory' in p.pattern_name.lower() for p in patterns))


class TestReplayDebugger(unittest.TestCase):
    """Test replay debugger."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.debugger = ReplayDebugger("test_colony", self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_record_event(self):
        """Test recording events."""
        self.debugger.start_recording()

        self.debugger.record_event(
            'agent_spawn',
            'agent-1',
            {'type': 'TaskAgent'},
            {'agents': {'agent-1': {'status': 'active'}}}
        )

        self.assertEqual(len(self.debugger.events), 1)

    def test_replay_navigation(self):
        """Test replay navigation."""
        # Create test events
        for i in range(5):
            self.debugger.events.append(ExecutionEvent(
                event_id=f'event-{i}',
                timestamp=float(i),
                event_type='test',
                agent_id=f'agent-{i}',
                data={},
                state_snapshot={'agents': {}}
            ))

        self.debugger.replay_state.total_events = 5

        # Test stepping
        event = self.debugger.step_forward()
        self.assertEqual(self.debugger.replay_state.current_position, 1)

        event = self.debugger.step_backward()
        self.assertEqual(self.debugger.replay_state.current_position, 0)

    def test_breakpoint(self):
        """Test breakpoint functionality."""
        bp = self.debugger.set_breakpoint("agent_id == 'agent-1'")

        self.assertEqual(bp.enabled, True)
        self.assertIn(bp.breakpoint_id, self.debugger.replay_state.breakpoints)


class TestIntegration(unittest.TestCase):
    """Integration tests for debugging tools."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_full_diagnostic_workflow(self):
        """Test complete diagnostic workflow."""
        # Create sample colony data
        colony_data = {
            'agents': [
                {
                    'id': 'agent-1',
                    'typeId': 'TaskAgent',
                    'status': 'active',
                    'lastActive': time.time(),
                    'valueFunction': 0.7,
                    'successCount': 80,
                    'failureCount': 20,
                    'resources': {
                        'cpuPercent': 50,
                        'memoryMb': 400,
                        'queueDepth': 100
                    }
                }
            ],
            'a2a_packages': [
                {
                    'id': 'pkg-1',
                    'timestamp': time.time(),
                    'senderId': 'agent-1',
                    'receiverId': 'agent-2',
                    'type': 'test',
                    'layer': 'DELIBERATE',
                    'privacyLevel': 'PRIVATE',
                    'parentIds': [],
                    'causalChainId': 'chain-1',
                    'payload': {}
                }
            ],
            'communicationMatrix': {}
        }

        # Save colony data
        colony_file = Path(self.temp_dir) / 'colony_data.json'
        with open(colony_file, 'w') as f:
            json.dump(colony_data, f)

        # Run diagnostics
        from diagnostic_generator import DiagnosticGenerator

        generator = DiagnosticGenerator("test_colony", self.temp_dir)
        generator.load_colony_data(str(colony_file))

        report = generator.generate_comprehensive_report()

        self.assertIn('colony_id', report)
        self.assertIn('overall_health_score', report)
        self.assertIn('diagnostics', report)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestA2ATracer))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentInspector))
    suite.addTests(loader.loadTestsFromTestCase(TestColonyDiagnostics))
    suite.addTests(loader.loadTestsFromTestCase(TestValueNetworkDebugger))
    suite.addTests(loader.loadTestsFromTestCase(TestIssueDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestReplayDebugger))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
