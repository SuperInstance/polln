"""
Test configuration and fixtures for integration tests.

Author: SuperInstance Test Team
Version: 1.0.0
"""

import pytest
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from pathlib import Path

# Add production directory to path
repo_root = Path(__file__).parent.parent.parent
production_dir = repo_root / "production"
sys.path.insert(0, str(production_dir))

from fastapi.testclient import TestClient


# =============================================================================
# Environment Configuration
# =============================================================================

@pytest.fixture(scope="session")
def test_env():
    """Get test environment configuration."""
    return {
        "DATABASE_URL": os.getenv(
            "TEST_DATABASE_URL",
            "postgresql://test_user:test_password@localhost:5432/test_db"
        ),
        "REDIS_URL": os.getenv(
            "TEST_REDIS_URL",
            "redis://localhost:6379"
        ),
        "API_URL": os.getenv(
            "TEST_API_URL",
            "http://localhost:8001"
        )
    }


# =============================================================================
# Async Event Loop
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Test Client Fixtures
# =============================================================================

@pytest.fixture
async def test_client():
    """
    Test client for FastAPI applications.

    This fixture provides a test client that can be used to test
    FastAPI endpoints without running a server.
    """
    from production.crdt_deployment.crdt_coordination_service import app

    with TestClient(app) as client:
        yield client


# =============================================================================
# Service Fixtures
# =============================================================================

@pytest.fixture
async def crdt_service():
    """
    Initialize CRDT coordination service for testing.

    This fixture creates a fresh CRDT service instance for each test,
    ensuring test isolation.
    """
    from production.crdt_deployment.crdt_coordination_service import (
        CRDTCoordinationService,
        Operation
    )

    # Create service with test configuration
    service = CRDTCoordinationService(
        node_id="test-node-1",
        replica_urls=["http://test-node-2:8001", "http://test-node-3:8001"],
        consensus_url=None,  # Disable consensus for tests
        merge_interval_ms=50  # Fast merges for tests
    )

    # Start service
    await service.start()

    yield service

    # Cleanup
    await service.stop()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
async def test_db(test_env):
    """
    Create test database connection.

    This fixture sets up a test database and cleans up after tests.
    """
    import asyncpg

    # Connect to database
    conn = await asyncpg.connect(test_env["DATABASE_URL"])

    # Create test tables
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS test_operations (
            id SERIAL PRIMARY KEY,
            op_id VARCHAR(255) UNIQUE,
            op_type VARCHAR(50),
            key VARCHAR(255),
            value TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    yield conn

    # Cleanup: drop test tables
    await conn.execute("DROP TABLE IF EXISTS test_operations")
    await conn.close()


# =============================================================================
# Redis Fixtures
# =============================================================================

@pytest.fixture
async def test_redis(test_env):
    """
    Create test Redis connection.

    This fixture sets up a test Redis connection and cleans up after tests.
    """
    import redis.asyncio as redis

    # Connect to Redis
    client = await redis.from_url(test_env["REDIS_URL"], decode_responses=True)

    yield client

    # Cleanup: flush test database
    await client.flushdb()
    await client.close()


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_operations():
    """
    Sample operations for testing.

    Returns a list of test operations with various characteristics.
    """
    return [
        {
            "op_id": "test-001",
            "op_type": "read",
            "key": "test-key-1",
            "criticality": 0.1,
            "conflict_probability": 0.1
        },
        {
            "op_id": "test-002",
            "op_type": "write",
            "key": "test-key-2",
            "value": "test-value-2",
            "criticality": 0.5,
            "conflict_probability": 0.3
        },
        {
            "op_id": "test-003",
            "op_type": "write",
            "key": "critical-key",
            "value": "critical-value",
            "criticality": 0.99,
            "conflict_probability": 0.9
        },
        {
            "op_id": "test-004",
            "op_type": "compute",
            "key": "counter",
            "criticality": 0.3,
            "conflict_probability": 0.2
        }
    ]


@pytest.fixture
def edge_case_operations():
    """
    Edge case operations for testing.

    Returns operations that test edge cases and error conditions.
    """
    return [
        {
            "op_id": "edge-001",
            "op_type": "write",
            "key": "",  # Empty key
            "value": "value",
            "criticality": 0.5,
            "conflict_probability": 0.1
        },
        {
            "op_id": "edge-002",
            "op_type": "invalid",  # Invalid operation type
            "key": "key",
            "criticality": 0.5,
            "conflict_probability": 0.1
        },
        {
            "op_id": "edge-003",
            "op_type": "write",
            "key": "key",
            "value": None,  # None value
            "criticality": 0.5,
            "conflict_probability": 0.1
        }
    ]


# =============================================================================
# Simulation Fixtures
# =============================================================================

@pytest.fixture
def simulation_configs():
    """
    Simulation configurations for testing.

    Returns configurations for different simulation types.
    """
    return {
        "self_play": {
            "num_tiles": 10,
            "strategy_dim": 20,
            "temperature": 0.8,
            "mutation_rate": 0.1,
            "crossover_rate": 0.3
        },
        "hydraulic": {
            "num_agents": 15,
            "pressure_threshold": 0.7,
            "flow_conservation": True
        },
        "value_network": {
            "num_states": 100,
            "learning_rate": 0.01,
            "discount_factor": 0.99
        }
    }


# =============================================================================
# Performance Testing Fixtures
# =============================================================================

@pytest.fixture
def performance_thresholds():
    """
    Performance thresholds for testing.

    Returns threshold values for various performance metrics.
    """
    return {
        "fast_path_latency_ms": 10.0,
        "slow_path_latency_ms": 200.0,
        "merge_latency_ms": 50.0,
        "throughput_ops_per_second": 1000,
        "memory_mb": 512
    }


# =============================================================================
# Monitoring Fixtures
# =============================================================================

@pytest.fixture
def mock_prometheus_metrics():
    """
    Mock Prometheus metrics for testing.

    Returns sample metric data for testing monitoring endpoints.
    """
    return {
        "fast_path_ops": 850,
        "slow_path_ops": 150,
        "total_ops": 1000,
        "avg_latency_ms": 15.5,
        "fast_path_ratio": 0.85,
        "error_count": 5,
        "merge_queue_size": 10
    }


# =============================================================================
# Helpers
# =============================================================================

@pytest.fixture
def wait_for_condition():
    """
    Helper to wait for a condition to be true.

    Usage:
        await wait_for_condition(lambda: some_condition(), timeout=5.0)
    """
    async def _wait_for_condition(condition, timeout=5.0, interval=0.1):
        """Wait for condition to be true."""
        start = asyncio.get_event_loop().time()

        while True:
            if condition():
                return True

            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError(f"Condition not met within {timeout}s")

            await asyncio.sleep(interval)

    return _wait_for_condition
