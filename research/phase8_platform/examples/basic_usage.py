"""
Basic Usage Examples for SuperInstance Research Platform
========================================================

Examples demonstrating basic platform usage.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_platform import (
    create_platform,
    create_experiment,
    Backend,
    SimulationType,
    ValidationType,
    PlatformConfig
)


async def example_1_simple_simulation():
    """Example 1: Run a simple simulation."""
    print("\n=== Example 1: Simple Simulation ===\n")

    # Create platform
    platform = create_platform()

    # Create experiment
    experiment = create_experiment(
        experiment_id="example_001",
        name="Simple Simulation",
        simulation_type=SimulationType.GPU_ACCELERATED,
        parameters={
            "matrix_size": 1000,
            "iterations": 100
        }
    )

    # Run simulation
    result = await platform.run_simulation(experiment)

    # Print results
    print(f"Experiment ID: {result.experiment_id}")
    print(f"Status: {result.status.name}")
    print(f"Backend: {result.backend_used.value if result.backend_used else 'N/A'}")
    print(f"Execution Time: {result.execution_time_ms:.2f}ms")
    print(f"Cost: ${result.cost_usd:.4f}")

    # Cleanup
    await platform.shutdown()


async def example_2_with_validation():
    """Example 2: Run simulation with validation."""
    print("\n=== Example 2: Simulation with Validation ===\n")

    platform = create_platform()

    experiment = create_experiment(
        experiment_id="example_002",
        name="Validated Simulation",
        simulation_type=SimulationType.HYBRID_MULTI_PAPER,
        parameters={
            "num_agents": 50,
            "timesteps": 500
        },
        validation_types=[
            ValidationType.STATISTICAL,
            ValidationType.SANITY
        ]
    )

    result = await platform.run_simulation(experiment)

    print(f"Status: {result.status.name}")
    print(f"\nValidation Results:")
    for report in result.validation_results:
        print(f"  - {report['validation_type']}: {'PASSED' if report['passed'] else 'FAILED'}")
        print(f"    Score: {report['score']:.2f}")

    await platform.shutdown()


async def example_3_backend_selection():
    """Example 3: Compare different backends."""
    print("\n=== Example 3: Backend Comparison ===\n")

    platform = create_platform()

    backends = [Backend.LOCAL_GPU, Backend.LOCAL_CPU]
    results = {}

    for backend in backends:
        if backend == Backend.LOCAL_GPU and not sys.modules.get('cupy'):
            print(f"Skipping {backend.value} (CuPy not available)")
            continue

        experiment = create_experiment(
            experiment_id=f"backend_test_{backend.value}",
            name=f"Backend Test: {backend.value}",
            simulation_type=SimulationType.GPU_ACCELERATED,
            parameters={
                "matrix_size": 500,
                "iterations": 50
            },
            backend_preference=backend
        )

        result = await platform.run_simulation(experiment)
        results[backend.value] = result

        print(f"\n{backend.value.upper()}:")
        print(f"  Execution Time: {result.execution_time_ms:.2f}ms")
        print(f"  Cost: ${result.cost_usd:.4f}")

    await platform.shutdown()


async def example_4_async_execution():
    """Example 4: Run multiple experiments asynchronously."""
    print("\n=== Example 4: Async Execution ===\n")

    platform = create_platform()

    # Submit multiple experiments
    experiment_ids = []
    for i in range(3):
        experiment = create_experiment(
            experiment_id=f"async_exp_{i:03d}",
            name=f"Async Experiment {i}",
            simulation_type=SimulationType.GPU_ACCELERATED,
            parameters={
                "matrix_size": 100 * (i + 1),
                "iterations": 10
            }
        )

        eid = await platform.run_simulation_async(experiment)
        experiment_ids.append(eid)
        print(f"Submitted: {eid}")

    # Wait for all to complete
    print("\nWaiting for completion...")
    for eid in experiment_ids:
        while True:
            status = await platform.get_experiment_status(eid)
            if status['done']:
                result = platform.data.load_results(eid)
                print(f"{eid}: {result.status.name} ({result.execution_time_ms:.2f}ms)")
                break
            await asyncio.sleep(0.5)

    await platform.shutdown()


async def example_5_compare_experiments():
    """Example 5: Compare multiple experiments."""
    print("\n=== Example 5: Compare Experiments ===\n")

    platform = create_platform()

    # Run experiments with different parameters
    experiment_ids = []
    for size in [100, 200, 400]:
        experiment = create_experiment(
            experiment_id=f"compare_size_{size}",
            name=f"Size Comparison: {size}",
            simulation_type=SimulationType.GPU_ACCELERATED,
            parameters={
                "matrix_size": size,
                "iterations": 50
            }
        )

        result = await platform.run_simulation(experiment)
        experiment_ids.append(result.experiment_id)

    # Compare results
    comparison = await platform.compare_results(
        experiment_ids=experiment_ids,
        comparison_type="performance"
    )

    print("\nComparison Results:")
    print(f"Experiments: {', '.join(comparison.experiment_ids)}")
    print(f"\nInsights:")
    for insight in comparison.insights:
        print(f"  - {insight}")

    await platform.shutdown()


async def example_6_custom_config():
    """Example 6: Use custom platform configuration."""
    print("\n=== Example 6: Custom Configuration ===\n")

    # Create custom config
    config = PlatformConfig(
        max_concurrent_experiments=10,
        max_gpu_memory_gb=5.0,
        enable_auto_validation=True,
        enable_realtime_viz=True
    )

    platform = create_platform(config)

    print(f"Max Concurrent: {config.max_concurrent_experiments}")
    print(f"Max GPU Memory: {config.max_gpu_memory_gb}GB")
    print(f"Auto Validation: {config.enable_auto_validation}")

    await platform.shutdown()


async def example_7_list_and_filter():
    """Example 7: List and filter experiments."""
    print("\n=== Example 7: List and Filter Experiments ===\n")

    platform = create_platform()

    # Create some tagged experiments
    for i in range(3):
        experiment = create_experiment(
            experiment_id=f"list_test_{i}",
            name=f"List Test {i}",
            simulation_type=SimulationType.GPU_ACCELERATED,
            parameters={"size": 100},
            tags=["demo", "test"]
        )

        await platform.run_simulation(experiment)

    # List all experiments
    all_experiments = platform.data.list_experiments()
    print(f"Total experiments: {len(all_experiments)}")

    # Filter by tag
    demo_experiments = platform.data.list_experiments(tag="demo")
    print(f"Demo experiments: {len(demo_experiments)}")

    # Filter by status
    completed = platform.data.list_experiments(status=None)
    print(f"Completed experiments: {len([e for e in completed if platform.data.load_results(e)])}")

    await platform.shutdown()


async def main():
    """Run all examples."""
    examples = [
        example_1_simple_simulation,
        example_2_with_validation,
        example_3_backend_selection,
        example_4_async_execution,
        example_5_compare_experiments,
        example_6_custom_config,
        example_7_list_and_filter
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nExample failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
