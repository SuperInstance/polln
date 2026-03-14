#!/usr/bin/env python3
"""
Example usage of SuperInstance Monitoring Stack

Demonstrates how to integrate monitoring into a SuperInstance application
"""

import asyncio
import random
import time
from production.monitoring.monitoring_stack import (
    MonitoringStack,
    SuperInstanceMetrics,
    SuperInstanceTracer,
    configure_logging,
    HealthChecker,
    Alerter,
    AlertRule
)


async def example_basic_monitoring():
    """Example 1: Basic monitoring setup."""
    print("\n=== Example 1: Basic Monitoring ===\n")

    # Create monitoring stack
    monitoring = MonitoringStack(
        service_name="superinstance-example",
        config={
            "log_level": "INFO",
            "replica_urls": ["http://localhost:8001", "http://localhost:8002"],
            "consensus_url": "http://localhost:8003"
        }
    )

    # Start metrics server
    monitoring.start_metrics_server(port=9090)

    print("Metrics server started on http://localhost:9090/metrics")
    print("Grafana: http://localhost:3000")
    print("Prometheus: http://localhost:9091")

    # Simulate some operations
    for i in range(10):
        path_type = random.choice(["fast", "slow"])
        operation_type = random.choice(["read", "write", "merge"])
        status = random.choice(["success", "success", "success", "error"])
        duration = random.uniform(0.001, 0.1)

        monitoring.metrics.record_operation(path_type, operation_type, status, duration)
        monitoring.logger.info("operation_completed",
                              iteration=i,
                              path_type=path_type,
                              operation=operation_type,
                              status=status,
                              duration_sec=duration)

        await asyncio.sleep(0.1)

    await monitoring.shutdown()


async def example_tracing():
    """Example 2: Distributed tracing."""
    print("\n=== Example 2: Distributed Tracing ===\n")

    tracer = SuperInstanceTracer("superinstance-example")

    # Trace a fast path operation
    with tracer.trace_operation("read_value", "fast", key="user:123"):
        print("Executing fast path read...")
        await asyncio.sleep(0.001)

    # Trace a CRDT merge
    with tracer.trace_crdt_merge(replica_id="node-2", state_size=1024):
        print("Merging CRDT state...")
        await asyncio.sleep(0.01)

    # Trace consensus round
    with tracer.trace_consensus_round(round_id="round-123", participants=3):
        print("Running consensus...")
        await asyncio.sleep(0.05)

    # Trace tile execution
    with tracer.trace_tile_execution(tile_type="MapTile", tile_id="tile-456"):
        print("Executing tile...")
        await asyncio.sleep(0.002)

    await tracer.shutdown()


async def example_health_checks():
    """Example 3: Health checks."""
    print("\n=== Example 3: Health Checks ===\n")

    health_checker = HealthChecker()

    # Add custom health check
    async def check_database() -> tuple[bool, str, dict]:
        # Simulate database check
        is_healthy = random.random() > 0.1
        message = "Database OK" if is_healthy else "Database slow"
        details = {"latency_ms": random.uniform(1, 100)}
        return is_healthy, message, details

    health_checker.register_check("database", check_database)

    # Add another health check
    async def check_cache() -> tuple[bool, str, dict]:
        is_healthy = random.random() > 0.05
        message = "Cache OK" if is_healthy else "Cache miss rate high"
        details = {"hit_rate": random.uniform(0.8, 1.0)}
        return is_healthy, message, details

    health_checker.register_check("cache", check_cache)

    # Run health checks
    health = await health_checker.health_endpoint()

    print(f"Overall status: {health['status']}")
    for name, check in health['checks'].items():
        print(f"  {name}: {check['status']} - {check['message']}")

    return health_checker


async def example_alerting():
    """Example 4: Alerting."""
    print("\n=== Example 4: Alerting ===\n")

    alerter = Alerter()

    # Custom alert handler (just print in this example)
    async def print_alert(alert):
        print(f"🚨 ALERT: {alert['rule_name']} ({alert['severity']})")
        print(f"   Description: {alert.get('description', 'N/A')}")
        print(f"   Timestamp: {alert['timestamp_iso']}")
        print(f"   Metrics: {alert['metrics']}")
        print()

    alerter.add_handler(print_alert)

    # Add custom alert rule
    alerter.add_rule(AlertRule(
        name="custom_high_latency",
        condition=lambda m: m.get("avg_latency_ms", 0) > 10,
        severity="warning",
        description="Average latency exceeds 10ms",
        cooldown_sec=60
    ))

    # Simulate metrics
    metrics_samples = [
        {"avg_latency_ms": 5, "error_rate": 0.001, "fast_path_ratio": 0.95},
        {"avg_latency_ms": 15, "error_rate": 0.002, "fast_path_ratio": 0.85},
        {"avg_latency_ms": 8, "error_rate": 0.015, "fast_path_ratio": 0.92},
        {"avg_latency_ms": 25, "error_rate": 0.005, "fast_path_ratio": 0.75},
    ]

    for i, metrics in enumerate(metrics_samples):
        print(f"Sample {i+1}: {metrics}")
        await alerter.evaluate_rules(metrics)
        await asyncio.sleep(0.1)


async def example_gpu_monitoring():
    """Example 5: GPU monitoring."""
    print("\n=== Example 5: GPU Monitoring ===\n")

    metrics = SuperInstanceMetrics()

    # Simulate GPU metrics
    gpu_configs = [
        {"utilization": 45.2, "memory_used": 2.1, "memory_total": 6.0, "temperature": 65, "power": 125},
        {"utilization": 78.5, "memory_used": 4.5, "memory_total": 6.0, "temperature": 78, "power": 215},
        {"utilization": 92.1, "memory_used": 5.8, "memory_total": 6.0, "temperature": 88, "power": 285},
    ]

    for i, config in enumerate(gpu_configs):
        metrics.record_gpu_metrics(
            gpu_id=0,
            utilization=config["utilization"],
            memory_used=int(config["memory_used"] * 1024**3),
            memory_total=int(config["memory_total"] * 1024**3),
            temperature=config["temperature"],
            power_draw=config["power"]
        )

        print(f"GPU {i}: {config['utilization']}% util, "
              f"{config['temperature']}°C, "
              f"{config['memory_used']}/{config['memory_total']} GB")

    print("\nGPU metrics recorded. View in Grafana!")


async def example_crdt_monitoring():
    """Example 6: CRDT monitoring."""
    print("\n=== Example 6: CRDT Monitoring ===\n")

    monitoring = MonitoringStack("superinstance-crdt")
    monitoring.logger = configure_logging("crdt-example")

    # Simulate CRDT operations
    replicas = ["node-1", "node-2", "node-3"]

    for i in range(20):
        replica = random.choice(replicas)
        state_size = random.randint(1000, 50000)
        duration = random.uniform(0.001, 0.1)

        # Record merge metrics
        monitoring.metrics.record_crdt_merge(
            replica_id=replica,
            duration_sec=duration,
            state_size=state_size,
            node_id="node-1"
        )

        # Trace the merge
        with monitoring.tracer.trace_crdt_merge(replica, state_size):
            await asyncio.sleep(0.001)

        # Log the operation
        monitoring.logger.info("crdt_merge_completed",
                              replica=replica,
                              state_size=state_size,
                              duration_sec=duration,
                              iteration=i)

        await asyncio.sleep(0.05)

    print("CRDT monitoring complete!")


async def example_consensus_monitoring():
    """Example 7: Consensus monitoring."""
    print("\n=== Example 7: Consensus Monitoring ===\n")

    monitoring = MonitoringStack("superinstance-consensus")

    # Simulate consensus rounds
    for i in range(15):
        participants = random.randint(3, 5)
        duration = random.uniform(0.05, 0.5)
        result = random.choice(["success", "success", "success", "timeout"])

        monitoring.metrics.record_consensus_round(
            round_type="raft",
            result=result,
            duration_sec=duration,
            participants=participants
        )

        monitoring.logger.info("consensus_round_completed",
                              round_id=f"round-{i}",
                              participants=participants,
                              result=result,
                              duration_sec=duration)

        await asyncio.sleep(0.1)

    print("Consensus monitoring complete!")


async def example_tile_monitoring():
    """Example 8: Tile execution monitoring."""
    print("\n=== Example 8: Tile Monitoring ===\n")

    monitoring = MonitoringStack("superinstance-tiles")

    # Simulate tile executions
    tile_types = ["MapTile", "FilterTile", "ReduceTile", "JoinTile"]

    for i in range(30):
        tile_type = random.choice(tile_types)
        status = random.choice(["success", "success", "success", "error"])
        duration = random.uniform(0.0001, 0.01)

        monitoring.metrics.tile_executions_total.labels(
            tile_type=tile_type,
            status=status
        ).inc()

        monitoring.metrics.tile_execution_duration.labels(
            tile_type=tile_type
        ).observe(duration)

        # Trace tile execution
        with monitoring.tracer.trace_tile_execution(tile_type, f"tile-{i}"):
            await asyncio.sleep(0.001)

        monitoring.logger.info("tile_executed",
                              tile_type=tile_type,
                              tile_id=f"tile-{i}",
                              status=status,
                              duration_sec=duration)

        await asyncio.sleep(0.05)

    print("Tile monitoring complete!")


async def example_complete_stack():
    """Example 9: Complete monitoring stack in action."""
    print("\n=== Example 9: Complete Stack ===\n")

    # Create complete stack
    monitoring = MonitoringStack(
        service_name="superinstance-complete",
        config={
            "log_level": "INFO",
            "replica_urls": ["http://node-1:8000", "http://node-2:8000"],
            "consensus_url": "http://consensus:8001"
        }
    )

    # Start metrics server
    monitoring.start_metrics_server(port=9090)

    print("🚀 Starting complete monitoring stack demo...")
    print("   Metrics: http://localhost:9090/metrics")
    print("   Grafana: http://localhost:3000")
    print("   Jaeger: http://localhost:16686")
    print()

    # Simulate application workload
    tasks = []
    for i in range(50):
        # Choose operation type
        op_type = random.choice([
            "fast_read",
            "fast_write",
            "slow_merge",
            "consensus",
            "tile_exec",
            "crdt_sync"
        ])

        if op_type == "fast_read":
            task = _simulate_fast_read(monitoring, i)
        elif op_type == "fast_write":
            task = _simulate_fast_write(monitoring, i)
        elif op_type == "slow_merge":
            task = _simulate_slow_merge(monitoring, i)
        elif op_type == "consensus":
            task = _simulate_consensus(monitoring, i)
        elif op_type == "tile_exec":
            task = _simulate_tile_exec(monitoring, i)
        else:  # crdt_sync
            task = _simulate_crdt_sync(monitoring, i)

        tasks.append(task)
        await asyncio.sleep(random.uniform(0.01, 0.05))

    # Wait for all tasks
    await asyncio.gather(*tasks)

    # Get health status
    health = await monitoring.get_health()
    print(f"\n📊 Health Status: {health['status']}")
    for name, check in health['checks'].items():
        print(f"   {name}: {check['status']}")

    # Get recent alerts
    alerts = monitoring.get_alert_history(limit=5)
    if alerts:
        print(f"\n🚨 Recent Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"   - {alert['rule_name']} ({alert['severity']})")

    print("\n✅ Demo complete! Check Grafana for visualizations.")
    await monitoring.shutdown()


async def _simulate_fast_read(monitoring, i):
    """Simulate fast path read operation."""
    with monitoring.tracer.trace_operation("fast_read", "fast", key=f"user-{i}"):
        duration = random.uniform(0.001, 0.005)
        monitoring.metrics.record_operation("fast", "read", "success", duration)
        monitoring.logger.info("fast_read", iteration=i, duration_sec=duration)
        await asyncio.sleep(duration)


async def _simulate_fast_write(monitoring, i):
    """Simulate fast path write operation."""
    with monitoring.tracer.trace_operation("fast_write", "fast", key=f"user-{i}"):
        duration = random.uniform(0.002, 0.008)
        status = "success" if random.random() > 0.05 else "error"
        monitoring.metrics.record_operation("fast", "write", status, duration)
        monitoring.logger.info("fast_write", iteration=i, status=status, duration_sec=duration)
        await asyncio.sleep(duration)


async def _simulate_slow_merge(monitoring, i):
    """Simulate slow path merge operation."""
    with monitoring.tracer.trace_operation("slow_merge", "slow"):
        duration = random.uniform(0.05, 0.2)
        monitoring.metrics.record_operation("slow", "merge", "success", duration)
        monitoring.logger.info("slow_merge", iteration=i, duration_sec=duration)
        await asyncio.sleep(duration)


async def _simulate_consensus(monitoring, i):
    """Simulate consensus round."""
    participants = random.randint(3, 5)
    with monitoring.tracer.trace_consensus_round(f"round-{i}", participants):
        duration = random.uniform(0.1, 0.3)
        result = "success" if random.random() > 0.1 else "timeout"
        monitoring.metrics.record_consensus_round("raft", result, duration, participants)
        monitoring.logger.info("consensus", round_id=i, result=result, duration_sec=duration)
        await asyncio.sleep(duration)


async def _simulate_tile_exec(monitoring, i):
    """Simulate tile execution."""
    tile_type = random.choice(["MapTile", "FilterTile", "ReduceTile"])
    with monitoring.tracer.trace_tile_execution(tile_type, f"tile-{i}"):
        duration = random.uniform(0.0005, 0.005)
        monitoring.metrics.tile_executions_total.labels(tile_type=tile_type, status="success").inc()
        monitoring.metrics.tile_execution_duration.labels(tile_type=tile_type).observe(duration)
        monitoring.logger.info("tile_exec", tile_type=tile_type, duration_sec=duration)
        await asyncio.sleep(duration)


async def _simulate_crdt_sync(monitoring, i):
    """Simulate CRDT synchronization."""
    replica = f"node-{random.randint(1, 3)}"
    state_size = random.randint(5000, 20000)
    with monitoring.tracer.trace_crdt_merge(replica, state_size):
        duration = random.uniform(0.01, 0.05)
        monitoring.metrics.record_crdt_merge(replica, duration, state_size, "node-1")
        monitoring.logger.info("crdt_sync", replica=replica, state_size=state_size, duration_sec=duration)
        await asyncio.sleep(duration)


# =============================================================================
# Main
# =============================================================================

async def main():
    """Run all examples."""
    examples = [
        ("Basic Monitoring", example_basic_monitoring),
        ("Distributed Tracing", example_tracing),
        ("Health Checks", example_health_checks),
        ("Alerting", example_alerting),
        ("GPU Monitoring", example_gpu_monitoring),
        ("CRDT Monitoring", example_crdt_monitoring),
        ("Consensus Monitoring", example_consensus_monitoring),
        ("Tile Monitoring", example_tile_monitoring),
        ("Complete Stack", example_complete_stack),
    ]

    print("=" * 60)
    print("SuperInstance Monitoring Stack Examples")
    print("=" * 60)

    for name, example_fn in examples:
        try:
            await example_fn()
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
