"""
Integration tests for CRDT coordination service.

Tests the complete CRDT-based coordination system including:
- Fast path operations
- Slow path consensus
- State merge
- Convergence
- Performance

Author: SuperInstance Test Team
Version: 1.0.0
"""

import pytest
import pytest_asyncio
import time
import asyncio
from typing import List, Dict, Any

from production.crdt_deployment.crdt_coordination_service import (
    CRDTCoordinationService,
    Operation,
    OperationResult,
    PathPredictor,
    TA_CRDTState,
    AsyncMergeScheduler
)


# =============================================================================
# Fast Path Tests
# =============================================================================

class TestFastPathOperations:
    """Test fast path CRDT operations."""

    @pytest.mark.asyncio
    async def test_fast_path_read_operation(self, test_client):
        """Test fast path read operation."""
        response = test_client.post("/operation", json={
            "op_id": "test-read-001",
            "op_type": "read",
            "key": "test-key",
            "criticality": 0.1,  # Low criticality = fast path
            "conflict_probability": 0.1
        })

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["path_used"] == "fast"
        assert data["latency_ms"] < 10  # Fast path should be fast

    @pytest.mark.asyncio
    async def test_fast_path_write_operation(self, crdt_service):
        """Test fast path write operation."""
        op = Operation(
            op_id="test-write-001",
            op_type="write",
            key="test-key",
            value="test-value",
            criticality=0.3,  # Low criticality
            conflict_probability=0.2
        )

        result, path, latency = await crdt_service.submit_operation(op)

        assert result.success
        assert path == "fast"
        assert latency < 10  # Fast path latency
        assert result.value == "test-value"

    @pytest.mark.asyncio
    async def test_fast_path_compute_operation(self, crdt_service):
        """Test fast path compute operation."""
        # First write a value
        write_op = Operation(
            op_id="test-compute-write",
            op_type="write",
            key="counter",
            value="0",
            criticality=0.3,
            conflict_probability=0.2
        )
        await crdt_service.submit_operation(write_op)

        # Then compute (increment)
        compute_op = Operation(
            op_id="test-compute-001",
            op_type="compute",
            key="counter",
            criticality=0.3,
            conflict_probability=0.2
        )

        result, path, latency = await crdt_service.submit_operation(compute_op)

        assert result.success
        assert path == "fast"
        assert result.value == 1  # Incremented

    @pytest.mark.asyncio
    async def test_fast_path_batch_operations(self, crdt_service):
        """Test batch of fast path operations."""
        operations = [
            Operation(
                op_id=f"batch-{i:04d}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}",
                criticality=0.2,
                conflict_probability=0.1
            )
            for i in range(100)
        ]

        start_time = time.time()
        results = []

        for op in operations:
            result, path, latency = await crdt_service.submit_operation(op)
            results.append((result, path))

        duration = time.time() - start_time

        # All should succeed
        assert all(r.success for r, _ in results)

        # All should use fast path
        assert all(path == "fast" for _, path in results)

        # Throughput should be high
        throughput = len(operations) / duration
        assert throughput > 100  # At least 100 ops/sec


# =============================================================================
# Slow Path Tests
# =============================================================================

class TestSlowPathOperations:
    """Test slow path consensus operations."""

    @pytest.mark.asyncio
    async def test_slow_path_high_criticality(self, crdt_service):
        """Test slow path for high criticality operations."""
        op = Operation(
            op_id="test-critical-001",
            op_type="write",
            key="critical-key",
            value="critical-value",
            criticality=0.99,  # High criticality = slow path
            conflict_probability=0.9
        )

        # Mock consensus behavior (no actual consensus in tests)
        result, path, latency = await crdt_service.submit_operation(op)

        # Should use slow path (or fail gracefully without consensus)
        assert path == "slow"
        assert latency > 100 or not result.success  # Slow path is slower

    @pytest.mark.asyncio
    async def test_slow_path_high_conflict(self, crdt_service):
        """Test slow path for high conflict probability."""
        op = Operation(
            op_id="test-conflict-001",
            op_type="write",
            key="conflict-key",
            value="conflict-value",
            criticality=0.5,
            conflict_probability=0.95  # High conflict = slow path
        )

        result, path, latency = await crdt_service.submit_operation(op)

        # Should use slow path
        assert path == "slow"

    @pytest.mark.asyncio
    async def test_path_selector_accuracy(self, crdt_service):
        """Test ML path selector accuracy."""
        # Training data with known paths
        test_cases = [
            # (criticality, conflict_prob, expected_path)
            (0.1, 0.1, "fast"),
            (0.5, 0.2, "fast"),
            (0.8, 0.3, "slow"),
            (0.9, 0.8, "slow"),
            (0.3, 0.9, "slow"),
        ]

        correct = 0
        for criticality, conflict_prob, expected_path in test_cases:
            op = Operation(
                op_id=f"selector-test-{criticality}-{conflict_prob}",
                op_type="write",
                key="test-key",
                value="test-value",
                criticality=criticality,
                conflict_probability=conflict_prob
            )

            result, path, _ = await crdt_service.submit_operation(op)

            if path == expected_path:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.95  # 95% accuracy target


# =============================================================================
# CRDT Merge and Convergence Tests
# =============================================================================

class TestCRDTMerge:
    """Test CRDT state merge and convergence."""

    @pytest.mark.asyncio
    async def test_crdt_merge_convergence(self):
        """Test CRDT merge convergence."""
        # Create two CRDT replicas
        replica1 = TA_CRDTState()
        replica2 = TA_CRDTState()

        # Apply different operations to each
        op1 = Operation(op_id="op1", op_type="write", key="x", value="1")
        op2 = Operation(op_id="op2", op_type="write", key="y", value="2")
        op3 = Operation(op_id="op3", op_type="write", key="x", value="3")

        result1 = replica1.apply(op1)
        result2 = replica2.apply(op2)

        # Both should succeed
        assert result1.success
        assert result2.success

        # Merge replica2 into replica1
        state2 = replica2.get_state()
        replica1.merge(state2)

        # Now apply conflicting write to replica1
        result3 = replica1.apply(op3)
        assert result3.success

        # Merge back to replica2
        state1 = replica1.get_state()
        replica2.merge(state1)

        # Verify convergence (both have same state)
        assert replica1.get_state() == replica2.get_state()

    @pytest.mark.asyncio
    async def test_concurrent_writes_last_writer_wins(self):
        """Test Last-Writer-Wins semantics for concurrent writes."""
        replica1 = TA_CRDTState()
        replica2 = TA_CRDTState()

        # Concurrent writes to same key
        op1 = Operation(op_id="op1", op_type="write", key="x", value="value1")
        op2 = Operation(op_id="op2", op_type="write", key="x", value="value2")

        result1 = replica1.apply(op1)
        result2 = replica2.apply(op2)

        # Merge
        state2 = replica2.get_state()
        replica1.merge(state2)

        # Last writer should win (higher version)
        final_value = replica1.get_state()["data"]["x"]
        assert final_value == "value2"  # Higher version wins

    @pytest.mark.asyncio
    async def test_async_merge_scheduler(self):
        """Test asynchronous merge scheduler."""
        scheduler = AsyncMergeScheduler(
            merge_interval_ms=50,
            max_batch_size=10,
            replica_urls=[]
        )

        # Create CRDT state
        crdt_state = TA_CRDTState()

        # Start scheduler
        await scheduler.start(crdt_state)

        # Schedule some operations
        for i in range(5):
            op = Operation(
                op_id=f"merge-test-{i}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}"
            )
            await scheduler.schedule_merge(op)

        # Wait for processing
        await asyncio.sleep(0.2)

        # Stop scheduler
        await scheduler.stop()

        # Check stats
        stats = scheduler.get_stats()
        assert stats["batches_merged"] >= 1


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.asyncio
    async def test_fast_path_latency(self, crdt_service, performance_thresholds):
        """Test fast path latency meets threshold."""
        op = Operation(
            op_id="perf-fast-001",
            op_type="read",
            key="perf-key",
            criticality=0.1,
            conflict_probability=0.1
        )

        # Measure latency
        latencies = []
        for _ in range(100):
            result, path, latency = await crdt_service.submit_operation(op)
            if path == "fast":
                latencies.append(latency)

        # Calculate average
        avg_latency = sum(latencies) / len(latencies)

        # Should be below threshold
        assert avg_latency < performance_thresholds["fast_path_latency_ms"]

    @pytest.mark.asyncio
    async def test_throughput(self, crdt_service):
        """Test operation throughput."""
        num_operations = 1000
        operations = [
            Operation(
                op_id=f"throughput-{i:04d}",
                op_type="write",
                key=f"key-{i % 100}",  # Cycle through 100 keys
                value=f"value-{i}",
                criticality=0.2,
                conflict_probability=0.1
            )
            for i in range(num_operations)
        ]

        start_time = time.time()

        for op in operations:
            await crdt_service.submit_operation(op)

        duration = time.time() - start_time
        throughput = num_operations / duration

        # Should achieve high throughput
        assert throughput > 100  # At least 100 ops/sec

    @pytest.mark.asyncio
    async def test_merge_performance(self, crdt_service):
        """Test async merge performance."""
        # Apply many operations
        for i in range(100):
            op = Operation(
                op_id=f"merge-perf-{i}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}"
            )
            await crdt_service.submit_operation(op)

        # Wait for merges to complete
        await asyncio.sleep(1.0)

        # Check merge stats
        stats = crdt_service.get_metrics()
        merge_queue_size = stats["merge_queue_size"]

        # Queue should be processed
        assert merge_queue_size < 50  # Most operations should be merged


# =============================================================================
# Metrics and Monitoring Tests
# =============================================================================

class TestMetrics:
    """Test metrics collection and reporting."""

    @pytest.mark.asyncio
    async def test_metrics_collection(self, crdt_service):
        """Test metrics are collected correctly."""
        # Submit some operations
        for i in range(10):
            op = Operation(
                op_id=f"metrics-{i}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}",
                criticality=0.3 if i < 7 else 0.9,  # Mix of fast/slow
                conflict_probability=0.2
            )
            await crdt_service.submit_operation(op)

        # Get metrics
        metrics = crdt_service.get_metrics()

        # Check metrics
        assert metrics["total_ops"] == 10
        assert metrics["fast_path_ops"] > 0
        assert metrics["slow_path_ops"] > 0
        assert metrics["avg_latency_ms"] > 0
        assert 0 <= metrics["fast_path_ratio"] <= 1

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, test_client):
        """Test metrics HTTP endpoint."""
        response = test_client.get("/metrics")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "node_id" in data
        assert "fast_path_ops" in data
        assert "slow_path_ops" in data
        assert "total_ops" in data
        assert "avg_latency_ms" in data

    @pytest.mark.asyncio
    async def test_detailed_metrics_endpoint(self, test_client):
        """Test detailed metrics endpoint."""
        response = test_client.get("/metrics/detail")

        assert response.status_code == 200
        data = response.json()

        # Check for detailed information
        assert "merge_stats" in data
        assert "path_predictor" in data


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_operation_type(self, crdt_service):
        """Test handling of invalid operation type."""
        op = Operation(
            op_id="error-invalid-type",
            op_type="invalid_type",
            key="test-key",
            criticality=0.5,
            conflict_probability=0.1
        )

        result, path, latency = await crdt_service.submit_operation(op)

        # Should fail gracefully
        assert not result.success
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_compute_on_non_numeric(self, crdt_service):
        """Test compute operation on non-numeric value."""
        # Write non-numeric value
        write_op = Operation(
            op_id="error-non-numeric-write",
            op_type="write",
            key="non-numeric-key",
            value="not-a-number"
        )
        await crdt_service.submit_operation(write_op)

        # Try to compute (increment)
        compute_op = Operation(
            op_id="error-non-numeric-compute",
            op_type="compute",
            key="non-numeric-key"
        )

        result, path, _ = await crdt_service.submit_operation(compute_op)

        # Should fail gracefully
        assert not result.success
        assert "non-numeric" in result.error.lower()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, crdt_service):
        """Test handling of concurrent operations."""
        # Submit many concurrent operations
        tasks = []
        for i in range(100):
            op = Operation(
                op_id=f"concurrent-{i}",
                op_type="write",
                key=f"key-{i % 10}",  # High contention on 10 keys
                value=f"value-{i}"
            )
            tasks.append(crdt_service.submit_operation(op))

        # Wait for all to complete
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.success for r, _, _ in results)


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthChecks:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "node_id" in data
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0
