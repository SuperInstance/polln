#!/usr/bin/env python3
"""
Test Suite for SuperInstance Monitoring Stack

Comprehensive tests for all monitoring components.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import monitoring components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from production.monitoring.monitoring_stack import (
    SuperInstanceMetrics,
    SuperInstanceTracer,
    configure_logging,
    HealthChecker,
    Alerter,
    AlertRule,
    HealthStatus,
    HealthCheck,
    MonitoringStack
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_prometheus():
    """Mock Prometheus client."""
    with patch('production.monitoring.monitoring_stack.PROMETHEUS_AVAILABLE', True):
        with patch('production.monitoring.monitoring_stack.Counter'):
            with patch('production.monitoring.monitoring_stack.Histogram'):
                with patch('production.monitoring.monitoring_stack.Gauge'):
                    yield


@pytest.fixture
def mock_otel():
    """Mock OpenTelemetry."""
    with patch('production.monitoring.monitoring_stack.OTEL_AVAILABLE', True):
        with patch('production.monitoring.monitoring_stack.trace'):
            with patch('production.monitoring.monitoring_stack.TracerProvider'):
                with patch('production.monitoring.monitoring_stack.BatchSpanProcessor'):
                    yield


@pytest.fixture
def mock_structlog():
    """Mock structlog."""
    with patch('production.monitoring.monitoring_stack.STRUCTLOG_AVAILABLE', True):
        with patch('production.monitoring.monitoring_stack.structlog'):
            with patch('production.monitoring.monitoring_stack.logging'):
                yield


@pytest.fixture
def metrics(mock_prometheus):
    """Create metrics instance."""
    return SuperInstanceMetrics()


@pytest.fixture
def tracer(mock_otel):
    """Create tracer instance."""
    return SuperInstanceTracer("test-service")


@pytest.fixture
def logger(mock_structlog):
    """Create logger instance."""
    return configure_logging("test-service")


# =============================================================================
# Test SuperInstanceMetrics
# =============================================================================

class TestSuperInstanceMetrics:
    """Test suite for SuperInstanceMetrics."""

    def test_initialization(self, metrics):
        """Test metrics initialization."""
        assert metrics is not None
        assert hasattr(metrics, 'operations_total')
        assert hasattr(metrics, 'operation_duration')
        assert hasattr(metrics, 'crdt_merge_duration')
        assert hasattr(metrics, 'consensus_rounds_total')
        assert hasattr(metrics, 'gpu_utilization')
        assert hasattr(metrics, 'agent_count')

    def test_record_operation(self, metrics):
        """Test operation recording."""
        # Should not raise any exceptions
        metrics.record_operation(
            path_type="fast",
            operation_type="read",
            status="success",
            duration_sec=0.002
        )

    def test_record_crdt_merge(self, metrics):
        """Test CRDT merge recording."""
        metrics.record_crdt_merge(
            replica_id="node-1",
            duration_sec=0.01,
            state_size=1024,
            node_id="node-2"
        )

    def test_record_consensus_round(self, metrics):
        """Test consensus round recording."""
        metrics.record_consensus_round(
            round_type="raft",
            result="success",
            duration_sec=0.15,
            participants=3
        )

    def test_record_gpu_metrics(self, metrics):
        """Test GPU metrics recording."""
        metrics.record_gpu_metrics(
            gpu_id=0,
            utilization=75.5,
            memory_used=2 * 1024**3,
            memory_total=6 * 1024**3,
            temperature=65.0,
            power_draw=150.0
        )

    def test_disabled_metrics(self):
        """Test metrics when Prometheus is not available."""
        with patch('production.monitoring.monitoring_stack.PROMETHEUS_AVAILABLE', False):
            metrics = SuperInstanceMetrics()
            assert metrics._enabled is False

            # Should not raise exceptions
            metrics.record_operation("fast", "read", "success", 0.001)


# =============================================================================
# Test SuperInstanceTracer
# =============================================================================

class TestSuperInstanceTracer:
    """Test suite for SuperInstanceTracer."""

    def test_initialization(self, tracer):
        """Test tracer initialization."""
        assert tracer is not None
        assert tracer.service_name == "test-service"

    def test_trace_operation(self, tracer):
        """Test operation tracing."""
        with tracer.trace_operation("test_operation", "fast", key="test"):
            pass  # Operation executes here

    def test_trace_crdt_merge(self, tracer):
        """Test CRDT merge tracing."""
        with tracer.trace_crdt_merge(replica_id="node-1", state_size=2048):
            pass  # Merge executes here

    def test_trace_consensus_round(self, tracer):
        """Test consensus round tracing."""
        with tracer.trace_consensus_round(round_id="round-1", participants=5):
            pass  # Consensus executes here

    def test_trace_tile_execution(self, tracer):
        """Test tile execution tracing."""
        with tracer.trace_tile_execution(tile_type="MapTile", tile_id="tile-1"):
            pass  # Tile executes here

    def test_disabled_tracer(self):
        """Test tracer when OpenTelemetry is not available."""
        with patch('production.monitoring.monitoring_stack.OTEL_AVAILABLE', False):
            tracer = SuperInstanceTracer("test-service")
            assert tracer._enabled is False

            # Should not raise exceptions
            with tracer.trace_operation("test", "fast"):
                pass


# =============================================================================
# Test HealthChecker
# =============================================================================

class TestHealthChecker:
    """Test suite for HealthChecker."""

    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        return HealthChecker()

    def test_initialization(self, health_checker):
        """Test health checker initialization."""
        assert health_checker is not None
        assert health_checker.checks == {}

    def test_register_check(self, health_checker):
        """Test registering health checks."""
        async def mock_check():
            return True, "OK", {}

        health_checker.register_check("test", mock_check)
        assert "test" in health_checker.checks

    @pytest.mark.asyncio
    async def test_check_health_success(self, health_checker):
        """Test successful health check."""
        async def mock_check():
            return True, "Service OK", {"latency": 10}

        health_checker.register_check("service", mock_check)
        results = await health_checker.check_health()

        assert "service" in results
        assert results["service"].status == HealthStatus.HEALTHY
        assert results["service"].message == "Service OK"

    @pytest.mark.asyncio
    async def test_check_health_failure(self, health_checker):
        """Test failed health check."""
        async def mock_check():
            return False, "Service down", {}

        health_checker.register_check("service", mock_check)
        results = await health_checker.check_health()

        assert "service" in results
        assert results["service"].status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_health_exception(self, health_checker):
        """Test health check with exception."""
        async def mock_check():
            raise ValueError("Test error")

        health_checker.register_check("service", mock_check)
        results = await health_checker.check_health()

        assert "service" in results
        assert results["service"].status == HealthStatus.UNHEALTHY
        assert "Test error" in results["service"].message

    def test_overall_status_healthy(self, health_checker):
        """Test overall status with all healthy."""
        checks = {
            "service1": HealthCheck("service1", HealthStatus.HEALTHY, "OK", datetime.utcnow().isoformat()),
            "service2": HealthCheck("service2", HealthStatus.HEALTHY, "OK", datetime.utcnow().isoformat()),
        }
        status = health_checker.overall_status(checks)
        assert status == HealthStatus.HEALTHY

    def test_overall_status_degraded(self, health_checker):
        """Test overall status with degraded services."""
        checks = {
            "service1": HealthCheck("service1", HealthStatus.HEALTHY, "OK", datetime.utcnow().isoformat()),
            "service2": HealthCheck("service2", HealthStatus.DEGRADED, "Slow", datetime.utcnow().isoformat()),
        }
        status = health_checker.overall_status(checks)
        assert status == HealthStatus.DEGRADED

    def test_overall_status_unhealthy(self, health_checker):
        """Test overall status with unhealthy services."""
        checks = {
            "service1": HealthCheck("service1", HealthStatus.HEALTHY, "OK", datetime.utcnow().isoformat()),
            "service2": HealthCheck("service2", HealthStatus.UNHEALTHY, "Down", datetime.utcnow().isoformat()),
        }
        status = health_checker.overall_status(checks)
        assert status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_health_endpoint(self, health_checker):
        """Test health endpoint response."""
        async def mock_check():
            return True, "OK", {}

        health_checker.register_check("service", mock_check)
        response = await health_checker.health_endpoint()

        assert "status" in response
        assert "timestamp" in response
        assert "checks" in response
        assert "service" in response["checks"]


# =============================================================================
# Test Alerter
# =============================================================================

class TestAlerter:
    """Test suite for Alerter."""

    @pytest.fixture
    def alerter(self):
        """Create alerter instance."""
        return Alerter()

    def test_initialization(self, alerter):
        """Test alerter initialization."""
        assert alerter is not None
        assert alerter.rules == []
        assert alerter.alert_handlers == []

    def test_add_rule(self, alerter):
        """Test adding alert rule."""
        rule = AlertRule(
            name="test_alert",
            condition=lambda m: m.get("test", 0) > 10,
            severity="warning"
        )
        alerter.add_rule(rule)
        assert len(alerter.rules) == 1

    def test_add_handler(self, alerter):
        """Test adding alert handler."""
        async def handler(alert):
            pass

        alerter.add_handler(handler)
        assert len(alerter.alert_handlers) == 1

    @pytest.mark.asyncio
    async def test_evaluate_rules_trigger(self, alerter):
        """Test alert rule evaluation with trigger."""
        triggered = []

        async def handler(alert):
            triggered.append(alert)

        rule = AlertRule(
            name="test_alert",
            condition=lambda m: m.get("test", 0) > 10,
            severity="warning"
        )
        alerter.add_rule(rule)
        alerter.add_handler(handler)

        await alerter.evaluate_rules({"test": 15})

        assert len(triggered) == 1
        assert triggered[0]["rule_name"] == "test_alert"

    @pytest.mark.asyncio
    async def test_evaluate_rules_no_trigger(self, alerter):
        """Test alert rule evaluation without trigger."""
        triggered = []

        async def handler(alert):
            triggered.append(alert)

        rule = AlertRule(
            name="test_alert",
            condition=lambda m: m.get("test", 0) > 10,
            severity="warning"
        )
        alerter.add_rule(rule)
        alerter.add_handler(handler)

        await alerter.evaluate_rules({"test": 5})

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_cooldown(self, alerter):
        """Test alert cooldown."""
        triggered = []

        async def handler(alert):
            triggered.append(alert)

        rule = AlertRule(
            name="test_alert",
            condition=lambda m: m.get("test", 0) > 10,
            severity="warning",
            cooldown_sec=1
        )
        alerter.add_rule(rule)
        alerter.add_handler(handler)

        # First trigger
        await alerter.evaluate_rules({"test": 15})
        assert len(triggered) == 1

        # Immediate second trigger (should be suppressed by cooldown)
        await alerter.evaluate_rules({"test": 15})
        assert len(triggered) == 1  # Still 1

        # Wait for cooldown
        await asyncio.sleep(1.5)

        # Third trigger (should fire again)
        await alerter.evaluate_rules({"test": 15})
        assert len(triggered) == 2

    def test_get_alert_history(self, alerter):
        """Test getting alert history."""
        # Add some alerts to history
        alerter.alert_history = [
            {"rule_name": "alert1", "timestamp": time.time() - 100},
            {"rule_name": "alert2", "timestamp": time.time() - 50},
            {"rule_name": "alert3", "timestamp": time.time()},
        ]

        history = alerter.get_alert_history(limit=2)
        assert len(history) == 2
        assert history[0]["rule_name"] == "alert2"
        assert history[1]["rule_name"] == "alert3"


# =============================================================================
# Test MonitoringStack
# =============================================================================

class TestMonitoringStack:
    """Test suite for MonitoringStack."""

    @pytest.fixture
    def monitoring_stack(self):
        """Create monitoring stack instance."""
        return MonitoringStack(
            service_name="test-service",
            config={
                "replica_urls": ["http://node-1:8000", "http://node-2:8000"],
                "consensus_url": "http://consensus:8001",
                "log_level": "INFO"
            }
        )

    def test_initialization(self, monitoring_stack):
        """Test monitoring stack initialization."""
        assert monitoring_stack is not None
        assert monitoring_stack.service_name == "test-service"
        assert monitoring_stack.metrics is not None
        assert monitoring_stack.tracer is not None
        assert monitoring_stack.logger is not None
        assert monitoring_stack.health_checker is not None
        assert monitoring_stack.alerter is not None

    def test_default_health_checks_registered(self, monitoring_stack):
        """Test default health checks are registered."""
        assert "replicas" in monitoring_stack.health_checker.checks
        assert "consensus" in monitoring_stack.health_checker.checks
        assert "gpu" in monitoring_stack.health_checker.checks
        assert "disk_space" in monitoring_stack.health_checker.checks
        assert "memory" in monitoring_stack.health_checker.checks

    def test_default_alerts_registered(self, monitoring_stack):
        """Test default alerts are registered."""
        alert_names = [rule.name for rule in monitoring_stack.alerter.rules]
        assert "high_latency" in alert_names
        assert "low_fast_path_ratio" in alert_names
        assert "high_error_rate" in alert_names
        assert "replica_down" in alert_names

    @pytest.mark.asyncio
    async def test_collect_metrics(self, monitoring_stack):
        """Test metrics collection."""
        metrics = await monitoring_stack.collect_metrics()

        assert "timestamp" in metrics
        assert "fast_path_ops" in metrics
        assert "slow_path_ops" in metrics
        assert "fast_path_ratio" in metrics
        assert "p95_latency_ms" in metrics
        assert "error_rate" in metrics
        assert "healthy_replicas" in metrics

    @pytest.mark.asyncio
    async def test_get_health(self, monitoring_stack):
        """Test getting health status."""
        health = await monitoring_stack.get_health()

        assert "status" in health
        assert "timestamp" in health
        assert "checks" in health

    def test_get_alert_history(self, monitoring_stack):
        """Test getting alert history."""
        history = monitoring_stack.get_alert_history(limit=10)
        assert isinstance(history, list)

    @pytest.mark.asyncio
    async def test_shutdown(self, monitoring_stack):
        """Test graceful shutdown."""
        # Should not raise exceptions
        await monitoring_stack.shutdown()


# =============================================================================
# Integration Tests
# =============================================================================

class TestMonitoringIntegration:
    """Integration tests for monitoring stack."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete monitoring workflow."""
        # Create monitoring stack
        monitoring = MonitoringStack("test-integration")

        # Record metrics
        monitoring.metrics.record_operation("fast", "read", "success", 0.002)
        monitoring.metrics.record_operation("slow", "merge", "success", 0.1)

        # Trace operations
        with monitoring.tracer.trace_operation("test_op", "fast"):
            pass

        # Log events
        monitoring.logger.info("test_event", test_key="test_value")

        # Get health
        health = await monitoring.get_health()
        assert health is not None

        # Get metrics
        metrics = await monitoring.collect_metrics()
        assert metrics is not None

        # Shutdown
        await monitoring.shutdown()

    @pytest.mark.asyncio
    async def test_monitoring_loop_simulation(self):
        """Test monitoring loop behavior."""
        monitoring = MonitoringStack("test-loop")

        # Simulate monitoring iterations
        for i in range(3):
            metrics = await monitoring.collect_metrics()
            monitoring.logger.info("monitoring_iteration", iteration=i, **metrics)

            # Evaluate alerts (should not trigger with default metrics)
            await monitoring.alerter.evaluate_rules(metrics)

            await asyncio.sleep(0.1)

        await monitoring.shutdown()


# =============================================================================
# Performance Tests
# =============================================================================

class TestMonitoringPerformance:
    """Performance tests for monitoring stack."""

    @pytest.mark.asyncio
    async def test_metrics_recording_performance(self):
        """Test metrics recording performance."""
        monitoring = MonitoringStack("perf-test")

        # Record 1000 operations
        start = time.time()
        for i in range(1000):
            monitoring.metrics.record_operation("fast", "read", "success", 0.001)
        duration = time.time() - start

        # Should complete in less than 1 second
        assert duration < 1.0

        await monitoring.shutdown()

    @pytest.mark.asyncio
    async def test_tracing_performance(self):
        """Test tracing performance."""
        monitoring = MonitoringStack("perf-test")

        # Trace 1000 operations
        start = time.time()
        for i in range(1000):
            with monitoring.tracer.trace_operation(f"op_{i}", "fast"):
                pass
        duration = time.time() - start

        # Should complete in less than 1 second
        assert duration < 1.0

        await monitoring.shutdown()


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
