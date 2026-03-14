#!/usr/bin/env python3
"""
Test Suite for CRDT Coordination Service

Tests for CRDT operations, path prediction, merge scheduling,
and API endpoints.
"""

import pytest
import asyncio
import time
from typing import List

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crdt_coordination_service import (
    Operation,
    OperationResult,
    PathPredictor,
    TA_CRDTState,
    AsyncMergeScheduler,
    CRDTCoordinationService,
)


# =============================================================================
# Operation Tests
# =============================================================================

class TestOperation:
    """Test Operation data class."""

    def test_operation_creation(self):
        """Test creating an operation."""
        op = Operation(
            op_id="op-001",
            op_type="write",
            key="test_key",
            value="test_value",
            criticality=0.5,
            conflict_probability=0.1
        )

        assert op.op_id == "op-001"
        assert op.op_type == "write"
        assert op.key == "test_key"
        assert op.value == "test_value"
        assert op.criticality == 0.5
        assert op.conflict_probability == 0.1

    def test_operation_to_dict(self):
        """Test converting operation to dictionary."""
        op = Operation(
            op_id="op-002",
            op_type="read",
            key="another_key"
        )

        data = op.to_dict()

        assert data["op_id"] == "op-002"
        assert data["op_type"] == "read"
        assert data["key"] == "another_key"
        assert "timestamp" in data

    def test_operation_from_dict(self):
        """Test creating operation from dictionary."""
        data = {
            "op_id": "op-003",
            "op_type": "compute",
            "key": "counter",
            "value": None,
            "criticality": 0.8,
            "conflict_probability": 0.5,
            "timestamp": time.time()
        }

        op = Operation.from_dict(data)

        assert op.op_id == "op-003"
        assert op.op_type == "compute"
        assert op.key == "counter"


# =============================================================================
# Path Predictor Tests
# =============================================================================

class TestPathPredictor:
    """Test path prediction logic."""

    @pytest.mark.asyncio
    async def test_fast_path_prediction(self):
        """Test fast path prediction for low-criticality ops."""
        predictor = PathPredictor(
            criticality_threshold=0.7,
            conflict_threshold=0.3
        )

        op = Operation(
            op_id="op-fast",
            op_type="write",
            key="test",
            criticality=0.5,
            conflict_probability=0.1
        )

        path = await predictor.predict_path(op)

        assert path == "fast"
        assert predictor.fast_path_count == 1

    @pytest.mark.asyncio
    async def test_slow_path_high_criticality(self):
        """Test slow path for high-criticality operations."""
        predictor = PathPredictor(
            criticality_threshold=0.7,
            conflict_threshold=0.3
        )

        op = Operation(
            op_id="op-slow-critical",
            op_type="write",
            key="critical_config",
            criticality=0.9,
            conflict_probability=0.1
        )

        path = await predictor.predict_path(op)

        assert path == "slow"
        assert predictor.slow_path_count == 1

    @pytest.mark.asyncio
    async def test_slow_path_high_conflict(self):
        """Test slow path for high-conflict operations."""
        predictor = PathPredictor(
            criticality_threshold=0.7,
            conflict_threshold=0.3
        )

        op = Operation(
            op_id="op-slow-conflict",
            op_type="write",
            key="hot_key",
            criticality=0.5,
            conflict_probability=0.8
        )

        path = await predictor.predict_path(op)

        assert path == "slow"
        assert predictor.slow_path_count == 1


# =============================================================================
# CRDT State Tests
# =============================================================================

class TestTA_CRDTState:
    """Test CRDT state management."""

    def test_write_operation(self):
        """Test write operation application."""
        state = TA_CRDTState()

        op = Operation(
            op_id="op-write-1",
            op_type="write",
            key="counter",
            value="42"
        )

        result = state.apply(op)

        assert result.success is True
        assert result.value == "42"
        assert result.version == 1
        assert state.data["counter"] == "42"

    def test_read_operation(self):
        """Test read operation application."""
        state = TA_CRDTState()

        # First write
        write_op = Operation(
            op_id="op-write-2",
            op_type="write",
            key="name",
            value="Alice"
        )
        state.apply(write_op)

        # Then read
        read_op = Operation(
            op_id="op-read-1",
            op_type="read",
            key="name"
        )

        result = state.apply(read_op)

        assert result.success is True
        assert result.value == "Alice"
        assert result.version == 1

    def test_compute_operation(self):
        """Test compute operation (increment)."""
        state = TA_CRDTState()

        # Initialize with 0
        write_op = Operation(
            op_id="op-write-3",
            op_type="write",
            key="counter",
            value=0
        )
        state.apply(write_op)

        # Increment
        compute_op = Operation(
            op_id="op-compute-1",
            op_type="compute",
            key="counter"
        )
        result = state.apply(compute_op)

        assert result.success is True
        assert result.value == 1
        assert state.data["counter"] == 1

    def test_state_merge(self):
        """Test state merge between replicas."""
        state1 = TA_CRDTState()
        state2 = TA_CRDTState()

        # Write to state1
        state1.apply(Operation(
            op_id="op-1",
            op_type="write",
            key="key1",
            value="value1"
        ))

        # Write to state2
        state2.apply(Operation(
            op_id="op-2",
            op_type="write",
            key="key2",
            value="value2"
        ))

        # Merge state2 into state1
        state1.merge(state2.get_state())

        assert "key1" in state1.data
        assert "key2" in state1.data
        assert state1.data["key1"] == "value1"
        assert state1.data["key2"] == "value2"

    def test_last_writer_wins_merge(self):
        """Test Last-Writer-Wins semantics during merge."""
        state1 = TA_CRDTState()
        state2 = TA_CRDTState()

        # Write same key to both states
        state1.apply(Operation(
            op_id="op-3",
            op_type="write",
            key="shared_key",
            value="value_v1"
        ))

        state2.apply(Operation(
            op_id="op-4",
            op_type="write",
            key="shared_key",
            value="value_v2"
        ))

        # Merge state2 (version 2) into state1 (version 1)
        state1.merge(state2.get_state())

        # State2 should win (higher version)
        assert state1.data["shared_key"] == "value_v2"


# =============================================================================
# Async Merge Scheduler Tests
# =============================================================================

class TestAsyncMergeScheduler:
    """Test async merge scheduler."""

    @pytest.mark.asyncio
    async def test_schedule_merge(self):
        """Test scheduling operation for merge."""
        scheduler = AsyncMergeScheduler(
            replica_urls=[],
            merge_interval_ms=100
        )

        op = Operation(
            op_id="op-merge-1",
            op_type="write",
            key="test",
            value="merge_test"
        )

        await scheduler.schedule_merge(op)

        assert scheduler.merge_queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_batch_collection(self):
        """Test batch collection from merge queue."""
        scheduler = AsyncMergeScheduler(
            replica_urls=[],
            merge_interval_ms=100
        )

        # Schedule multiple operations
        for i in range(5):
            await scheduler.schedule_merge(Operation(
                op_id=f"op-batch-{i}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}"
            ))

        # Get batch
        batch = await scheduler._get_merge_batch()

        assert len(batch) == 5

    @pytest.mark.asyncio
    async def test_merge_loop_lifecycle(self):
        """Test merge loop start and stop."""
        state = TA_CRDTState()
        scheduler = AsyncMergeScheduler(
            replica_urls=[],
            merge_interval_ms=50
        )

        # Start scheduler
        await scheduler.start(state)
        assert scheduler.running is True

        # Wait a bit
        await asyncio.sleep(0.2)

        # Stop scheduler
        await scheduler.stop()
        assert scheduler.running is False


# =============================================================================
# Integration Tests
# =============================================================================

class TestCRDTCoordinationService:
    """Integration tests for CRDT coordination service."""

    @pytest.fixture
    async def service(self):
        """Create service instance for testing."""
        service = CRDTCoordinationService(
            node_id="test-node-1",
            replica_urls=[],  # No replicas for testing
            consensus_url=None,  # No consensus for testing
            merge_interval_ms=100
        )

        await service.start()

        yield service

        await service.stop()

    @pytest.mark.asyncio
    async def test_fast_path_operation(self, service):
        """Test operation via fast path."""
        op = Operation(
            op_id="test-fast-1",
            op_type="write",
            key="fast_key",
            value="fast_value",
            criticality=0.5
        )

        result, path, latency = await service.submit_operation(op)

        assert result.success is True
        assert path == "fast"
        assert latency < 50  # Should be fast
        assert service.crdt_state.data["fast_key"] == "fast_value"

    @pytest.mark.asyncio
    async def test_operation_metrics(self, service):
        """Test operation metrics tracking."""
        op1 = Operation(
            op_id="test-metrics-1",
            op_type="write",
            key="metrics_key",
            value="metrics_value"
        )

        await service.submit_operation(op1)

        metrics = service.get_metrics()

        assert metrics["total_ops"] == 1
        assert metrics["fast_path_ops"] == 1
        assert metrics["avg_latency_ms"] > 0

    @pytest.mark.asyncio
    async def test_multiple_operations(self, service):
        """Test multiple operations in sequence."""
        operations = [
            Operation(
                op_id=f"test-multi-{i}",
                op_type="write",
                key=f"key-{i}",
                value=f"value-{i}"
            )
            for i in range(10)
        ]

        results = []
        for op in operations:
            result, _, _ = await service.submit_operation(op)
            results.append(result)

        assert all(r.success for r in results)
        assert len(service.crdt_state.data) == 10


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Performance benchmarks."""

    @pytest.mark.asyncio
    async def test_fast_path_latency(self):
        """Benchmark fast path latency."""
        service = CRDTCoordinationService(
            node_id="perf-node",
            replica_urls=[],
            consensus_url=None
        )

        await service.start()

        try:
            latencies = []
            for i in range(100):
                op = Operation(
                    op_id=f"perf-op-{i}",
                    op_type="write",
                    key=f"perf-key-{i}",
                    value=f"perf-value-{i}"
                )

                _, path, latency = await service.submit_operation(op)
                latencies.append(latency)

            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)

            print(f"\nFast Path Latency (100 ops):")
            print(f"  Average: {avg_latency:.2f}ms")
            print(f"  Max: {max_latency:.2f}ms")

            # Assert performance targets
            assert avg_latency < 10  # Should average < 10ms
            assert max_latency < 50  # Should never exceed 50ms

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Benchmark concurrent operation handling."""
        service = CRDTCoordinationService(
            node_id="concurrent-node",
            replica_urls=[],
            consensus_url=None
        )

        await service.start()

        try:
            async def submit_op(i):
                op = Operation(
                    op_id=f"concurrent-op-{i}",
                    op_type="write",
                    key=f"concurrent-key-{i}",
                    value=f"concurrent-value-{i}"
                )
                return await service.submit_operation(op)

            # Submit 100 operations concurrently
            start_time = time.time()
            results = await asyncio.gather(*[
                submit_op(i) for i in range(100)
            ])
            total_time = time.time() - start_time

            throughput = len(results) / total_time

            print(f"\nConcurrent Operations (100 ops):")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Throughput: {throughput:.2f} ops/sec")

            # All should succeed
            assert all(r[0].success for r in results)

            # Reasonable throughput
            assert throughput > 50  # Should handle > 50 ops/sec

        finally:
            await service.stop()


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
