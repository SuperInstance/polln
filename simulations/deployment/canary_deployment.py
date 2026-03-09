"""
Canary Deployment Simulation

Models incremental canary rollout with metrics monitoring.
Validates regression detection hypothesis (H3).

Hypothesis H3: Canary deployments detect 90% of regressions within 5 minutes
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import time


class CanaryPhase(Enum):
    STABLE = "stable"
    CANARY_1 = "canary_1pct"      # 1% traffic
    CANARY_5 = "canary_5pct"      # 5% traffic
    CANARY_25 = "canary_25pct"    # 25% traffic
    FULL_ROLLOUT = "full_rollout" # 100% traffic
    ROLLBACK = "rollback"


class RegressionType(Enum):
    PERFORMANCE = "performance"    # Increased latency
    ERROR_RATE = "error_rate"     # Increased errors
    CRASH = "crash"               # Service crashes
    MEMORY_LEAK = "memory_leak"   # Memory issues
    SUBTLE = "subtle"             # Subtle bugs (hard to detect)


@dataclass
class CanaryMetrics:
    """Metrics collected during canary deployment"""
    timestamp: float
    canary_percentage: float
    baseline_requests: int
    canary_requests: int
    baseline_errors: int
    canary_errors: int
    baseline_latency_p50: float
    canary_latency_p50: float
    baseline_latency_p99: float
    canary_latency_p99: float
    baseline_cpu: float
    canary_cpu: float


class CanaryInstance:
    """Represents a canary instance"""

    def __init__(
        self,
        instance_id: str,
        version: str,
        has_regression: bool = False,
        regression_type: Optional[RegressionType] = None,
        regression_severity: float = 1.0
    ):
        self.instance_id = instance_id
        self.version = version
        self.has_regression = has_regression
        self.regression_type = regression_type
        self.regression_severity = regression_severity

        self.request_count = 0
        self.error_count = 0
        self.latencies = []
        self.cpu_usage = []

    def handle_request(self) -> Tuple[bool, float]:
        """
        Handle a request.
        Returns (success, latency_ms)
        """
        self.request_count += 1

        # Base latency (log-normal distribution)
        latency = np.random.lognormal(mean=3.0, sigma=0.5)

        # Base error rate (0.05%)
        error_rate = 0.0005

        # Apply regression effects
        if self.has_regression:
            if self.regression_type == RegressionType.PERFORMANCE:
                # Performance regression: 2-5x slower
                latency *= (2.0 + self.regression_severity * 3.0)

            elif self.regression_type == RegressionType.ERROR_RATE:
                # Error rate regression: 10-100x more errors
                error_rate *= (10.0 + self.regression_severity * 90.0)

            elif self.regression_type == RegressionType.CRASH:
                # Crash: 50% chance of failure
                if np.random.random() < 0.5:
                    error_rate = 1.0

            elif self.regression_type == RegressionType.MEMORY_LEAK:
                # Memory leak: Gradual slowdown
                leak_factor = min(self.request_count / 10000.0, 5.0)
                latency *= (1.0 + leak_factor * self.regression_severity)

            elif self.regression_type == RegressionType.SUBTLE:
                # Subtle bug: 2-3x latency increase, 2-5x errors
                latency *= (2.0 + np.random.random())
                error_rate *= (2.0 + np.random.random() * 3.0)

        # Determine success
        success = np.random.random() > error_rate

        if not success:
            self.error_count += 1

        self.latencies.append(latency)

        # Simulate CPU usage
        base_cpu = np.random.uniform(0.3, 0.5)

        if self.has_regression and self.regression_type in [
            RegressionType.PERFORMANCE,
            RegressionType.MEMORY_LEAK
        ]:
            base_cpu *= (1.5 + self.regression_severity)

        self.cpu_usage.append(base_cpu)

        return success, latency

    def get_metrics(self) -> Dict[str, float]:
        """Get current instance metrics"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0.0,
            "latency_p50": np.median(self.latencies) if self.latencies else 0.0,
            "latency_p99": np.percentile(self.latencies, 99) if self.latencies else 0.0,
            "avg_cpu": np.mean(self.cpu_usage) if self.cpu_usage else 0.0
        }


class CanaryDeploymentSimulator:
    """Simulates canary deployment strategy"""

    def __init__(
        self,
        num_instances: int = 100,
        baseline_version: str = "v1.0",
        canary_version: str = "v1.1",
        rollout_schedule: List[float] = None,
        traffic_per_second: int = 1000,
        monitoring_interval: int = 10,
        regression: Optional[Dict] = None
    ):
        self.num_instances = num_instances
        self.baseline_version = baseline_version
        self.canary_version = canary_version
        self.rollout_schedule = rollout_schedule or [0.01, 0.05, 0.25, 1.0]
        self.traffic_per_second = traffic_per_second
        self.monitoring_interval = monitoring_interval

        # Regression configuration
        self.regression = regression or {
            "has_regression": False,
            "type": None,
            "severity": 1.0
        }

        # Initialize instances
        self.baseline_instances = [
            CanaryInstance(f"baseline-{i}", baseline_version)
            for i in range(num_instances)
        ]

        self.canary_instances = []

        # Deployment state
        self.current_phase = CanaryPhase.STABLE
        self.canary_percentage = 0.0
        self.metrics_history = []
        self.detection_time = None
        self.rollback_triggered = False
        self.deployment_success = False

    def create_canary_instances(self, count: int):
        """Create canary instances"""
        for i in range(count):
            instance_id = f"canary-{len(self.canary_instances)}"
            instance = CanaryInstance(
                instance_id,
                self.canary_version,
                has_regression=self.regression["has_regression"],
                regression_type=self.regression.get("type"),
                regression_severity=self.regression.get("severity", 1.0)
            )
            self.canary_instances.append(instance)

    def distribute_traffic(self) -> Tuple[int, int]:
        """
        Distribute traffic between baseline and canary.
        Returns (baseline_requests, canary_requests)
        """
        total_requests = self.traffic_per_second * self.monitoring_interval
        canary_requests = int(total_requests * self.canary_percentage)
        baseline_requests = total_requests - canary_requests

        return baseline_requests, canary_requests

    def simulate_traffic(self, baseline_requests: int, canary_requests: int):
        """Simulate traffic to instances"""

        # Distribute baseline traffic
        baseline_per_instance = baseline_requests // len(self.baseline_instances) if self.baseline_instances else 0
        for instance in self.baseline_instances:
            for _ in range(baseline_per_instance):
                instance.handle_request()

        # Distribute canary traffic
        if self.canary_instances:
            canary_per_instance = canary_requests // len(self.canary_instances)
            for instance in self.canary_instances:
                for _ in range(canary_per_instance):
                    instance.handle_request()

    def collect_metrics(self) -> CanaryMetrics:
        """Collect metrics from baseline and canary"""

        # Aggregate baseline metrics
        baseline_requests = sum(i.request_count for i in self.baseline_instances)
        baseline_errors = sum(i.error_count for i in self.baseline_instances)
        baseline_latencies = []
        baseline_cpus = []

        for instance in self.baseline_instances:
            baseline_latencies.extend(instance.latencies[-100:])  # Last 100 requests
            baseline_cpus.extend(instance.cpu_usage[-100:])

        # Aggregate canary metrics
        canary_requests = sum(i.request_count for i in self.canary_instances) if self.canary_instances else 0
        canary_errors = sum(i.error_count for i in self.canary_instances) if self.canary_instances else 0
        canary_latencies = []
        canary_cpus = []

        for instance in self.canary_instances:
            canary_latencies.extend(instance.latencies[-100:])
            canary_cpus.extend(instance.cpu_usage[-100:])

        metrics = CanaryMetrics(
            timestamp=time.time(),
            canary_percentage=self.canary_percentage,
            baseline_requests=baseline_requests,
            canary_requests=canary_requests,
            baseline_errors=baseline_errors,
            canary_errors=canary_errors,
            baseline_latency_p50=np.median(baseline_latencies) if baseline_latencies else 0.0,
            canary_latency_p50=np.median(canary_latencies) if canary_latencies else 0.0,
            baseline_latency_p99=np.percentile(baseline_latencies, 99) if baseline_latencies else 0.0,
            canary_latency_p99=np.percentile(canary_latencies, 99) if canary_latencies else 0.0,
            baseline_cpu=np.mean(baseline_cpus) if baseline_cpus else 0.0,
            canary_cpu=np.mean(canary_cpus) if canary_cpus else 0.0
        )

        self.metrics_history.append(metrics)
        return metrics

    def detect_regression(self, metrics: CanaryMetrics) -> Tuple[bool, str]:
        """
        Detect regression by comparing canary vs baseline.
        Returns (detected, reason)
        """

        # Calculate baseline error rate
        baseline_error_rate = (
            metrics.baseline_errors / metrics.baseline_requests
            if metrics.baseline_requests > 0 else 0.0
        )

        # Calculate canary error rate
        canary_error_rate = (
            metrics.canary_errors / metrics.canary_requests
            if metrics.canary_requests > 0 else 0.0
        )

        # Error rate threshold: 2x baseline (minimum 1% absolute increase)
        error_rate_threshold = max(baseline_error_rate * 2.0, 0.01)

        if canary_error_rate > error_rate_threshold and metrics.canary_requests > 100:
            return True, f"High error rate: {canary_error_rate:.3%} vs {baseline_error_rate:.3%}"

        # Latency threshold: 1.5x baseline
        latency_threshold = metrics.baseline_latency_p50 * 1.5

        if metrics.canary_latency_p50 > latency_threshold and metrics.canary_requests > 100:
            return True, f"High latency: {metrics.canary_latency_p50:.1f}ms vs {metrics.baseline_latency_p50:.1f}ms"

        # CPU threshold: 1.5x baseline
        cpu_threshold = metrics.baseline_cpu * 1.5

        if metrics.canary_cpu > cpu_threshold and metrics.canary_requests > 100:
            return True, f"High CPU: {metrics.canary_cpu:.1%} vs {metrics.baseline_cpu:.1%}"

        return False, ""

    def rollback(self) -> float:
        """Execute rollback"""
        self.rollback_triggered = True
        self.current_phase = CanaryPhase.ROLLBACK

        print(f"\n⚠️  ROLLBACK TRIGGERED")
        print(f"   Redirecting traffic from canary to baseline...")

        # Simulate rollback time
        rollback_time = 2.0  # Fast rollback
        time.sleep(rollback_time / 10)

        self.canary_percentage = 0.0

        print(f"   Rollback complete in {rollback_time:.2f}s")

        return rollback_time

    def run_canary_deployment(self) -> Dict[str, any]:
        """Run complete canary deployment simulation"""
        print(f"\n{'='*70}")
        print(f"CANARY DEPLOYMENT: {self.baseline_version} → {self.canary_version}")
        print(f"Instances: {self.num_instances}")
        print(f"Rollout schedule: {[f'{p*100:.0f}%' for p in self.rollout_schedule]}")
        print(f"Regression: {self.regression['has_regression']} ({self.regression.get('type', 'N/A')})")
        print(f"{'='*70}\n")

        deployment_start = time.time()

        for phase_idx, target_percentage in enumerate(self.rollout_schedule):
            phase_name = f"Phase {phase_idx + 1}: {target_percentage*100:.0f}% canary"

            print(f"\n📍 {phase_name}")

            # Update canary instances
            num_canary = int(self.num_instances * target_percentage)
            current_canary = len(self.canary_instances)

            if num_canary > current_canary:
                new_instances = num_canary - current_canary
                self.create_canary_instances(new_instances)
                print(f"   Created {new_instances} canary instances")

            self.canary_percentage = target_percentage

            # Monitor for this phase
            phase_duration = 300  # 5 minutes per phase
            monitoring_intervals = phase_duration // self.monitoring_interval

            regression_detected = False
            detection_reason = ""

            for interval in range(monitoring_intervals):
                # Simulate traffic
                baseline_requests, canary_requests = self.distribute_traffic()
                self.simulate_traffic(baseline_requests, canary_requests)

                # Collect metrics
                metrics = self.collect_metrics()

                # Check for regression
                detected, reason = self.detect_regression(metrics)

                if detected:
                    regression_detected = True
                    detection_reason = reason
                    self.detection_time = time.time() - deployment_start

                    print(f"\n   ⚠️  REGRESSION DETECTED at {self.detection_time:.1f}s")
                    print(f"   Reason: {reason}")

                    # Rollback
                    rollback_time = self.rollback()

                    return {
                        "success": False,
                        "regression_detected": True,
                        "detection_time": self.detection_time,
                        "detection_reason": detection_reason,
                        "rollback_time": rollback_time,
                        "canary_percentage": self.canary_percentage,
                        "metrics_history": self.metrics_history
                    }

                # Progress indicator
                if (interval + 1) % 30 == 0:
                    print(f"   Monitoring: {(interval+1)*self.monitoring_interval}s / {phase_duration}s")

            # Phase complete - no regression detected
            print(f"   ✓ Phase complete: No regressions detected")

        # All phases complete - deployment successful!
        self.deployment_success = True
        deployment_time = time.time() - deployment_start

        print(f"\n✓ CANARY DEPLOYMENT SUCCESSFUL")
        print(f"   Total time: {deployment_time:.1f}s")
        print(f"   Final canary percentage: 100%")

        return {
            "success": True,
            "regression_detected": False,
            "deployment_time": deployment_time,
            "canary_percentage": 1.0,
            "metrics_history": self.metrics_history
        }


def run_canary_detection_study():
    """
    Run comprehensive detection study to validate H3.
    Tests detection rates for different regression types.
    """
    print("\n" + "="*70)
    print("CANARY DETECTION STUDY")
    print("Testing regression detection rates across different scenarios...")
    print("="*70 + "\n")

    regression_types = [
        RegressionType.PERFORMANCE,
        RegressionType.ERROR_RATE,
        RegressionType.CRASH,
        RegressionType.MEMORY_LEAK,
        RegressionType.SUBTLE
    ]

    results = {}

    for regression_type in regression_types:
        print(f"\n🔍 Testing: {regression_type.value}")

        num_trials = 100
        detection_count = 0
        detection_times = []

        for trial in range(num_trials):
            simulator = CanaryDeploymentSimulator(
                num_instances=100,
                baseline_version="v1.0",
                canary_version="v1.1",
                regression={
                    "has_regression": True,
                    "type": regression_type,
                    "severity": 1.0
                }
            )

            result = simulator.run_canary_deployment()

            if result.get("regression_detected"):
                detection_count += 1
                detection_times.append(result["detection_time"])

        detection_rate = detection_count / num_trials
        avg_detection_time = np.mean(detection_times) if detection_times else 0.0
        p95_detection_time = np.percentile(detection_times, 95) if detection_times else 0.0

        results[regression_type.value] = {
            "detection_rate": detection_rate,
            "avg_detection_time": avg_detection_time,
            "p95_detection_time": p95_detection_time
        }

        print(f"   Detection rate: {detection_rate:.1%}")
        print(f"   Avg detection time: {avg_detection_time:.1f}s")
        print(f"   P95 detection time: {p95_detection_time:.1f}s")

    # Overall statistics
    print(f"\n{'='*70}")
    print(f"DETECTION STUDY SUMMARY")
    print(f"{'='*70}")

    overall_detection_rate = np.mean([r["detection_rate"] for r in results.values()])
    overall_avg_detection_time = np.mean([r["avg_detection_time"] for r in results.values()])

    print(f"\nOverall Detection Rate: {overall_detection_rate:.1%}")
    print(f"Overall Avg Detection Time: {overall_avg_detection_time:.1f}s")

    print(f"\nHypothesis H3 Validation:")
    print(f"  Target: 90% detection within 5 minutes (300s)")
    print(f"  Achieved: {overall_detection_rate:.1%} detection")
    print(f"  Avg time: {overall_avg_detection_time:.1f}s")
    print(f"  Status: {'✓ PASS' if overall_detection_rate >= 0.90 and overall_avg_detection_time <= 300 else '❌ FAIL'}")

    print(f"\nDetailed Results:")
    for regression_type, stats in results.items():
        within_5min = stats["avg_detection_time"] <= 300
        print(f"  {regression_type}:")
        print(f"    Detection: {stats['detection_rate']:.1%}")
        print(f"    Time: {stats['avg_detection_time']:.1f}s avg")
        print(f"    Within 5min: {'✓' if within_5min else '❌'}")

    print(f"{'='*70}\n")

    return {
        "overall_detection_rate": overall_detection_rate,
        "overall_avg_detection_time": overall_avg_detection_time,
        "hypothesis_h3_met": overall_detection_rate >= 0.90 and overall_avg_detection_time <= 300,
        "detailed_results": results
    }


def main():
    """Run canary deployment simulation"""
    print("\n" + "="*70)
    print("CANARY DEPLOYMENT SIMULATION")
    print("="*70)

    # Scenario 1: Successful canary (no regression)
    print("\n📍 Scenario 1: Successful Canary (No Regression)")

    simulator = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v1.1",
        regression={"has_regression": False}
    )

    result = simulator.run_canary_deployment()

    # Scenario 2: Performance regression detection
    print("\n📍 Scenario 2: Performance Regression Detection")

    simulator_perf = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v1.1",
        regression={
            "has_regression": True,
            "type": RegressionType.PERFORMANCE,
            "severity": 2.0
        }
    )

    result_perf = simulator_perf.run_canary_deployment()

    # Scenario 3: Subtle regression detection
    print("\n📍 Scenario 3: Subtle Regression Detection")

    simulator_subtle = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v1.1",
        regression={
            "has_regression": True,
            "type": RegressionType.SUBTLE,
            "severity": 1.0
        }
    )

    result_subtle = simulator_subtle.run_canary_deployment()

    # Detection study
    detection_results = run_canary_detection_study()

    return {
        "scenario_1": result,
        "scenario_2": result_perf,
        "scenario_3": result_subtle,
        "detection_study": detection_results
    }


if __name__ == "__main__":
    main()
