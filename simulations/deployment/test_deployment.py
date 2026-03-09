"""
Deployment Simulation Tests

Comprehensive tests for all deployment simulation modules.
Validates correctness and mathematical properties of deployment patterns.
"""

import pytest
import numpy as np
import time
from typing import Dict, List

# Import simulation modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rolling_deployment import RollingDeploymentSimulator, Instance
from blue_green_deployment import BlueGreenDeploymentSimulator, DeploymentEnvironment
from canary_deployment import CanaryDeploymentSimulator, CanaryInstance, RegressionType
from rollback_simulation import RollbackSimulator, RollbackType


class TestRollingDeployment:
    """Test rolling deployment simulation"""

    def test_instance_creation(self):
        """Test instance initialization"""
        instance = Instance("test-instance", "v1.0")

        assert instance.instance_id == "test-instance"
        assert instance.version == "v1.0"
        assert instance.status.value == "starting"
        assert instance.request_count == 0

    def test_instance_update(self):
        """Test instance version update"""
        instance = Instance("test-instance", "v1.0")

        instance.update("v1.1")

        assert instance.version == "v1.1"
        assert instance.status.value == "starting"

    def test_health_check(self):
        """Test health check functionality"""
        instance = Instance("test-instance", "v1.0", startup_time=0.1)

        # Initially not healthy (startup time)
        assert not instance.health_check()

        # Wait for startup
        time.sleep(0.2)

        # Should be healthy now (with high probability)
        assert instance.health_check()

    def test_rolling_deployment_basic(self):
        """Test basic rolling deployment"""
        simulator = RollingDeploymentSimulator(
            num_instances=5,
            current_version="v1.0",
            target_version="v1.1",
            batch_sizes=[0.2, 0.4, 0.6, 0.8, 1.0]
        )

        result = simulator.run_deployment()

        assert result is not None
        assert "deployment_success" in result
        assert "total_downtime" in result
        assert result["total_downtime"] >= 0

    def test_rolling_deployment_hypothesis_h1(self):
        """Test H1: < 1s downtime with proper batch sizing"""
        simulator = RollingDeploymentSimulator(
            num_instances=10,
            current_version="v1.0",
            target_version="v1.1",
            batch_sizes=[0.01, 0.05, 0.10, 0.25, 0.50, 1.0]
        )

        result = simulator.run_deployment()

        # Check if downtime is less than 1 second
        if result["deployment_success"]:
            assert result["total_downtime"] < 1.0, f"Downtime {result['total_downtime']}s exceeds 1s"

    def test_optimal_batch_size_analysis(self):
        """Test optimal batch size analysis"""
        simulator = RollingDeploymentSimulator(
            num_instances=10,
            current_version="v1.0",
            target_version="v1.1"
        )

        analysis = simulator.analyze_optimal_batch_size()

        assert "optimal_batch_size" in analysis
        assert "analysis_results" in analysis
        assert 0.0 < analysis["optimal_batch_size"] <= 1.0


class TestBlueGreenDeployment:
    """Test blue-green deployment simulation"""

    def test_environment_creation(self):
        """Test environment initialization"""
        env = DeploymentEnvironment(
            color="blue",
            version="v1.0",
            num_instances=10
        )

        assert env.color.value == "blue"
        assert env.version == "v1.0"
        assert env.num_instances == 10
        assert env.healthy_instances == 10

    def test_environment_deploy(self):
        """Test deployment to environment"""
        env = DeploymentEnvironment(
            color="green",
            version="v1.0",
            num_instances=10,
            failure_probability=0.0
        )

        success = env.deploy("v1.1")

        assert success is True
        assert env.version == "v1.1"
        assert env.deployment_complete is True

    def test_environment_health_check(self):
        """Test environment health check"""
        env = DeploymentEnvironment(
            color="blue",
            version="v1.0",
            num_instances=10
        )

        env.deployment_complete = True

        # Health check should pass with high probability
        is_healthy = env.health_check()

        assert isinstance(is_healthy, bool)

    def test_blue_green_deployment_basic(self):
        """Test basic blue-green deployment"""
        simulator = BlueGreenDeploymentSimulator(
            num_instances=10,
            blue_version="v1.0",
            green_version="v1.1"
        )

        result = simulator.run_deployment()

        assert result is not None
        assert "success" in result
        assert "deployment_time" in result
        assert "cutover_time" in result

    def test_cutover_time(self):
        """Test that cutover time is very fast"""
        simulator = BlueGreenDeploymentSimulator(
            num_instances=10,
            blue_version="v1.0",
            green_version="v1.1"
        )

        result = simulator.run_deployment()

        if result["success"]:
            # Cutover should be nearly instant (< 0.5s)
            assert result["cutover_time"] < 0.5, f"Cutover time {result['cutover_time']}s exceeds 0.5s"

    def test_failed_deployment_rollback(self):
        """Test rollback on failed deployment"""
        simulator = BlueGreenDeploymentSimulator(
            num_instances=10,
            blue_version="v1.0",
            green_version="v1.1",
            enable_auto_rollback=True
        )

        # Force green deployment to fail
        simulator.green_env.failure_probability = 1.0

        result = simulator.run_deployment()

        assert result["success"] is False
        assert result["rolled_back"] is True


class TestCanaryDeployment:
    """Test canary deployment simulation"""

    def test_canary_instance_creation(self):
        """Test canary instance initialization"""
        instance = CanaryInstance(
            "canary-1",
            "v1.1",
            has_regression=False
        )

        assert instance.instance_id == "canary-1"
        assert instance.version == "v1.1"
        assert instance.has_regression is False

    def test_canary_instance_with_regression(self):
        """Test canary instance with regression"""
        instance = CanaryInstance(
            "canary-1",
            "v1.1",
            has_regression=True,
            regression_type=RegressionType.PERFORMANCE,
            regression_severity=2.0
        )

        assert instance.has_regression is True
        assert instance.regression_type == RegressionType.PERFORMANCE
        assert instance.regression_severity == 2.0

    def test_regression_detection(self):
        """Test regression detection"""
        simulator = CanaryDeploymentSimulator(
            num_instances=100,
            baseline_version="v1.0",
            canary_version="v1.1",
            regression={
                "has_regression": True,
                "type": RegressionType.PERFORMANCE,
                "severity": 2.0
            }
        )

        result = simulator.run_canary_deployment()

        assert "regression_detected" in result
        assert isinstance(result["regression_detected"], bool)

    def test_canary_deployment_no_regression(self):
        """Test canary deployment without regression"""
        simulator = CanaryDeploymentSimulator(
            num_instances=100,
            baseline_version="v1.0",
            canary_version="v1.1",
            regression={"has_regression": False}
        )

        result = simulator.run_canary_deployment()

        assert result["success"] is True
        assert result["regression_detected"] is False
        assert result["canary_percentage"] == 1.0

    def test_canary_deployment_with_regression(self):
        """Test canary deployment with regression detection"""
        simulator = CanaryDeploymentSimulator(
            num_instances=100,
            baseline_version="v1.0",
            canary_version="v1.1",
            regression={
                "has_regression": True,
                "type": RegressionType.ERROR_RATE,
                "severity": 5.0
            }
        )

        result = simulator.run_canary_deployment()

        # Should detect regression and rollback
        assert result["success"] is False
        assert result["regression_detected"] is True
        assert "detection_time" in result


class TestRollbackSimulation:
    """Test rollback simulation"""

    def test_state_snapshot(self):
        """Test state snapshot creation"""
        simulator = RollbackSimulator(
            num_instances=10,
            old_version="v1.0",
            new_version="v1.1"
        )

        instance = simulator.old_instances[0]
        snapshot = instance.create_snapshot()

        assert snapshot is not None
        assert snapshot.version == "v1.0"
        assert snapshot.data_hash is not None
        assert len(snapshot.data) > 0

    def test_state_restore(self):
        """Test state restoration from snapshot"""
        simulator = RollbackSimulator(
            num_instances=10,
            old_version="v1.0",
            new_version="v1.1"
        )

        instance = simulator.old_instances[0]
        snapshot = instance.create_snapshot()

        # Modify state
        instance.state.update("test_key", "test_value")

        # Restore from snapshot
        success, restore_time = instance.rollback_to_snapshot(snapshot)

        assert success is True
        assert restore_time >= 0
        assert "test_key" not in instance.state.data

    def test_version_revert_rollback(self):
        """Test version revert rollback"""
        simulator = RollbackSimulator(
            num_instances=10,
            old_version="v1.0",
            new_version="v1.1"
        )

        snapshots = simulator.deploy_new_version()

        result = simulator.trigger_rollback(snapshots, RollbackType.VERSION_REVERT)

        assert result["success"] is True
        assert result["rollback_time"] < 30.0

    def test_full_rollback_with_state_restore(self):
        """Test full rollback with state restoration"""
        simulator = RollbackSimulator(
            num_instances=10,
            old_version="v1.0",
            new_version="v1.1"
        )

        snapshots = simulator.deploy_new_version()

        # Simulate traffic
        for instance in simulator.old_instances:
            for _ in range(100):
                instance.handle_request()

        result = simulator.trigger_rollback(snapshots, RollbackType.FULL_ROLLBACK)

        assert result["success"] is True
        assert result["rollback_time"] < 30.0
        assert result["state_consistent"] is True


class TestDeploymentComparison:
    """Test deployment comparison functionality"""

    def test_all_simulations_run(self):
        """Test that all simulations can run without errors"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()

        # Run a subset of simulations for testing
        comparison._run_rolling_simulations()
        comparison._run_blue_green_simulations()
        comparison._run_canary_simulations()
        comparison._run_rollback_simulations()

        assert comparison.results is not None
        assert "rolling" in comparison.results
        assert "blue_green" in comparison.results
        assert "canary" in comparison.results
        assert "rollback" in comparison.results

    def test_comparison_generation(self):
        """Test strategy comparison"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()

        # Run minimal simulations
        comparison._run_rolling_simulations()
        comparison._run_blue_green_simulations()

        comparison_results = comparison._compare_strategies()

        assert "dimensions" in comparison_results
        assert "best_by_dimension" in comparison_results
        assert "downtime" in comparison_results["dimensions"]

    def test_recommendations_generation(self):
        """Test recommendation generation"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()
        recommendations = comparison._generate_recommendations()

        assert isinstance(recommendations, dict)
        assert "emergency_hotfix" in recommendations
        assert "major_feature_release" in recommendations


class TestHypothesisValidation:
    """Test hypothesis validation"""

    def test_hypothesis_h1_validation(self):
        """Test H1 validation logic"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()

        # Run minimal simulations
        comparison._run_rolling_simulations()
        comparison._run_blue_green_simulations()

        status = comparison._check_hypothesis_h1()

        assert status in ["pass", "fail"]

    def test_hypothesis_h2_validation(self):
        """Test H2 validation logic"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()

        # Run minimal simulations
        comparison._run_rollback_simulations()

        status = comparison._check_hypothesis_h2()

        assert status in ["pass", "fail"]

    def test_hypothesis_h4_validation(self):
        """Test H4 validation logic"""
        from run_all import DeploymentComparison

        comparison = DeploymentComparison()

        # Run minimal simulations
        comparison._run_blue_green_simulations()

        status = comparison._check_hypothesis_h4()

        assert status in ["pass", "fail"]


# Integration tests

class TestIntegrationScenarios:
    """Integration tests for deployment scenarios"""

    def test_emergency_hotfix_scenario(self):
        """Test emergency hotfix deployment (blue-green recommended)"""
        simulator = BlueGreenDeploymentSimulator(
            num_instances=10,
            blue_version="v1.0",
            green_version="v1.0.1",  # Hotfix version
            enable_auto_rollback=True
        )

        result = simulator.run_deployment()

        # Emergency hotfix should succeed quickly
        assert result["deployment_time"] < 60.0  # Should complete in < 1 minute

    def test_major_feature_release_scenario(self):
        """Test major feature release (canary recommended)"""
        simulator = CanaryDeploymentSimulator(
            num_instances=100,
            baseline_version="v1.0",
            canary_version="v2.0",  # Major version bump
            regression={"has_regression": False}
        )

        result = simulator.run_canary_deployment()

        # Canary should complete successfully
        assert result["success"] is True
        assert result["canary_percentage"] == 1.0

    def test_minor_bug_fix_scenario(self):
        """Test minor bug fix (rolling recommended)"""
        simulator = RollingDeploymentSimulator(
            num_instances=20,
            current_version="v1.0",
            target_version="v1.0.1",
            batch_sizes=[0.05, 0.10, 0.25, 0.50, 1.0]
        )

        result = simulator.run_deployment()

        # Rolling deployment should succeed
        assert result["deployment_success"] is True
        assert result["total_downtime"] < 1.0


# Performance tests

class TestPerformanceMetrics:
    """Test performance-related assertions"""

    def test_rolling_deployment_scales_linearly(self):
        """Test that rolling deployment scales linearly with instance count"""
        # Small deployment
        simulator_small = RollingDeploymentSimulator(
            num_instances=10,
            current_version="v1.0",
            target_version="v1.1"
        )

        result_small = simulator_small.run_deployment()

        # Large deployment
        simulator_large = RollingDeploymentSimulator(
            num_instances=100,
            current_version="v1.0",
            target_version="v1.1"
        )

        result_large = simulator_large.run_deployment()

        # Large deployment should take roughly 10x longer (linear scaling)
        if result_small["deployment_success"] and result_large["deployment_success"]:
            ratio = result_large["total_deployment_time"] / result_small["total_deployment_time"]
            # Allow for some variance (5x to 15x)
            assert 5.0 < ratio < 15.0, f"Scaling ratio {ratio} is not linear"

    def test_canary_detection_accuracy(self):
        """Test canary detection accuracy for different regression types"""
        regression_types = [
            RegressionType.PERFORMANCE,
            RegressionType.ERROR_RATE,
            RegressionType.CRASH
        ]

        detection_rates = []

        for regression_type in regression_types:
            detected_count = 0
            trials = 10

            for _ in range(trials):
                simulator = CanaryDeploymentSimulator(
                    num_instances=100,
                    baseline_version="v1.0",
                    canary_version="v1.1",
                    regression={
                        "has_regression": True,
                        "type": regression_type,
                        "severity": 2.0
                    }
                )

                result = simulator.run_canary_deployment()

                if result.get("regression_detected"):
                    detected_count += 1

            detection_rate = detected_count / trials
            detection_rates.append(detection_rate)

        # All regression types should have high detection rates
        for detection_rate in detection_rates:
            assert detection_rate >= 0.5, f"Detection rate {detection_rate} is too low"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
