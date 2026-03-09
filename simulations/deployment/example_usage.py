"""
Example Usage - Deployment Simulations

Demonstrates how to use deployment simulations for common scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rolling_deployment import RollingDeploymentSimulator
from blue_green_deployment import BlueGreenDeploymentSimulator
from canary_deployment import CanaryDeploymentSimulator, RegressionType
from rollback_simulation import RollbackSimulator, RollbackType


def example_1_emergency_hotfix():
    """
    Example 1: Emergency Hotfix Deployment

    Scenario: Critical bug discovered in production, needs immediate fix.
    Strategy: Blue-Green (fastest deployment + instant rollback)
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Emergency Hotfix Deployment")
    print("="*70)
    print("\nScenario: Critical bug in v1.0, deploying hotfix v1.0.1")
    print("Strategy: Blue-Green Deployment")
    print("Expected: Fast deployment (< 2 min) with instant rollback\n")

    simulator = BlueGreenDeploymentSimulator(
        num_instances=10,
        blue_version="v1.0",
        green_version="v1.0.1",
        enable_auto_rollback=True
    )

    result = simulator.run_deployment()

    print(f"\n📊 Results:")
    print(f"   Success: {result['success']}")
    print(f"   Deployment time: {result['deployment_time']:.2f}s")
    print(f"   Cutover time: {result['cutover_time']:.3f}s")
    print(f"   Downtime: {result['downtime']:.3f}s")

    return result


def example_2_major_feature_release():
    """
    Example 2: Major Feature Release with Canary

    Scenario: Releasing v2.0 with significant changes
    Strategy: Canary (best regression detection)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Major Feature Release")
    print("="*70)
    print("\nScenario: Major version v2.0 with significant changes")
    print("Strategy: Canary Deployment")
    print("Expected: Gradual rollout with regression detection\n")

    simulator = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v2.0",
        rollout_schedule=[0.01, 0.05, 0.25, 1.0],
        regression={"has_regression": False}
    )

    result = simulator.run_canary_deployment()

    print(f"\n📊 Results:")
    print(f"   Success: {result['success']}")
    print(f"   Regression detected: {result['regression_detected']}")
    print(f"   Deployment time: {result['deployment_time']:.1f}s")
    print(f"   Final canary percentage: {result['canary_percentage']*100:.0f}%")

    return result


def example_3_performance_regression_detection():
    """
    Example 3: Detecting Performance Regression with Canary

    Scenario: New version has performance issues
    Strategy: Canary (detects performance regressions)
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Performance Regression Detection")
    print("="*70)
    print("\nScenario: New version has 2x performance degradation")
    print("Strategy: Canary Deployment")
    print("Expected: Regression detected within first 5 minutes\n")

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

    print(f"\n📊 Results:")
    print(f"   Regression detected: {result['regression_detected']}")
    if result['regression_detected']:
        print(f"   Detection time: {result['detection_time']:.1f}s")
        print(f"   Detection reason: {result['detection_reason']}")
    print(f"   Rollback successful: {not result['success']}")

    return result


def example_4_minor_bug_fix():
    """
    Example 4: Minor Bug Fix with Rolling Deployment

    Scenario: Small fix, low risk
    Strategy: Rolling (efficient resource usage)
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Minor Bug Fix")
    print("="*70)
    print("\nScenario: Minor bug fix v1.0 → v1.0.1")
    print("Strategy: Rolling Deployment")
    print("Expected: Fast deployment with minimal downtime\n")

    simulator = RollingDeploymentSimulator(
        num_instances=10,
        current_version="v1.0",
        target_version="v1.0.1",
        batch_sizes=[0.1, 0.25, 0.5, 1.0]  # Faster batches
    )

    result = simulator.run_deployment()

    print(f"\n📊 Results:")
    print(f"   Success: {result['deployment_success']}")
    print(f"   Deployment time: {result['total_deployment_time']:.2f}s")
    print(f"   Downtime: {result['total_downtime']:.3f}s")
    print(f"   H1 (< 1s downtime): {'PASS' if result['hypothesis_h1_met'] else 'FAIL'}")

    return result


def example_5_rollback_safety():
    """
    Example 5: Rollback Safety Validation

    Scenario: Failed deployment requiring rollback
    Strategy: Full rollback with state restore
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Rollback Safety")
    print("="*70)
    print("\nScenario: Deployment fails, need to rollback with state restore")
    print("Strategy: Full Rollback")
    print("Expected: < 30s rollback with 100% state consistency\n")

    simulator = RollbackSimulator(
        num_instances=10,
        old_version="v1.0",
        new_version="v1.1"
    )

    # Deploy new version
    snapshots = simulator.deploy_new_version()

    # Simulate some traffic
    print("Simulating traffic...")
    for instance in simulator.old_instances:
        for _ in range(100):
            instance.handle_request()

    # Rollback
    result = simulator.trigger_rollback(snapshots, RollbackType.FULL_ROLLBACK)

    print(f"\n📊 Results:")
    print(f"   Success: {result['success']}")
    print(f"   Rollback time: {result['rollback_time']:.3f}s")
    print(f"   State consistent: {result['state_consistent']}")
    print(f"   H2 (< 30s rollback, 100% consistency): {'PASS' if result['rollback_time'] < 30 and result['state_consistent'] else 'FAIL'}")

    return result


def example_6_optimal_batch_size():
    """
    Example 6: Finding Optimal Batch Size

    Scenario: Determine best batch size for rolling deployment
    Strategy: Analyze different batch configurations
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Optimal Batch Size Analysis")
    print("="*70)
    print("\nScenario: Finding optimal batch size for rolling deployment")
    print("Strategy: Analyze success rate vs batch size\n")

    simulator = RollingDeploymentSimulator(
        num_instances=20,
        current_version="v1.0",
        target_version="v1.1"
    )

    analysis = simulator.analyze_optimal_batch_size()

    print(f"\n📊 Results:")
    print(f"   Optimal batch size: {analysis['optimal_batch_size']*100:.1f}%")
    print(f"   Expected success rate: {analysis['analysis_results'][int(analysis['optimal_batch_size']*100)]['success_rate']*100:.1f}%")
    print(f"   Expected downtime: {analysis['analysis_results'][int(analysis['optimal_batch_size']*100)]['avg_downtime']:.3f}s")

    return analysis


def example_7_compare_strategies():
    """
    Example 7: Compare All Deployment Strategies

    Scenario: Compare rolling, blue-green, and canary for same deployment
    Strategy: Run all and compare metrics
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Strategy Comparison")
    print("="*70)
    print("\nScenario: Compare all deployment strategies")
    print("Deployment: v1.0 → v1.1 (minor update)\n")

    results = {}

    # Rolling
    print("\n1️⃣  Rolling Deployment:")
    rolling = RollingDeploymentSimulator(
        num_instances=10,
        current_version="v1.0",
        target_version="v1.1"
    )
    results['rolling'] = rolling.run_deployment()

    # Blue-Green
    print("\n2️⃣  Blue-Green Deployment:")
    blue_green = BlueGreenDeploymentSimulator(
        num_instances=10,
        blue_version="v1.0",
        green_version="v1.1"
    )
    results['blue_green'] = blue_green.run_deployment()

    # Canary
    print("\n3️⃣  Canary Deployment:")
    canary = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v1.1",
        regression={"has_regression": False}
    )
    results['canary'] = canary.run_canary_deployment()

    # Comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    print(f"\n{'Strategy':<15} {'Success':<10} {'Time':<12} {'Downtime':<12}")
    print("-" * 70)

    for strategy, result in results.items():
        strategy_name = strategy.replace('_', '-').title()
        success = "✓" if result.get('success') or result.get('deployment_success') else "✗"

        if strategy == 'canary':
            time_str = f"{result['deployment_time']:.1f}s"
            downtime_str = "0.000s"
        else:
            time_str = f"{result.get('deployment_time', result.get('total_deployment_time', 0)):.2f}s"
            downtime_str = f"{result.get('downtime', result.get('total_downtime', 0)):.3f}s"

        print(f"{strategy_name:<15} {success:<10} {time_str:<12} {downtime_str:<12}")

    return results


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "DEPLOYMENT SIMULATION EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates common deployment scenarios")
    print("using the deployment simulation suite.\n")

    examples = [
        ("Emergency Hotfix", example_1_emergency_hotfix),
        ("Major Feature Release", example_2_major_feature_release),
        ("Performance Regression Detection", example_3_performance_regression_detection),
        ("Minor Bug Fix", example_4_minor_bug_fix),
        ("Rollback Safety", example_5_rollback_safety),
        ("Optimal Batch Size", example_6_optimal_batch_size),
        ("Strategy Comparison", example_7_compare_strategies)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nSelect example to run (1-7), or 'all' to run all examples:")

    # For automation, run all examples
    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = "all"

    if choice == "all":
        for name, example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, example_func = examples[idx]
                example_func()
            else:
                print(f"Invalid choice: {choice}")
        except ValueError:
            print(f"Invalid choice: {choice}")

    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
