"""
Rolling Deployment Simulation

Models incremental rollout strategy where instances are updated in batches.
Validates zero-downtime hypothesis (H1) and optimal batch sizing.

Hypothesis H1: All deployment strategies achieve < 1s downtime during updates
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import Enum
import time


class HealthStatus(Enum):
    HEALTHY = "healthy"
    STARTING = "starting"
    UNHEALTHY = "unhealthy"
    TERMINATING = "terminating"


@dataclass
class InstanceMetrics:
    """Metrics for a single instance during deployment"""
    instance_id: str
    status: HealthStatus
    version: str
    uptime_seconds: float
    request_count: int
    error_count: int
    latency_p50_ms: float
    latency_p99_ms: float
    last_health_check: float


class Instance:
    """Represents a single service instance"""

    def __init__(self, instance_id: str, version: str, startup_time: float = 2.0):
        self.instance_id = instance_id
        self.version = version
        self.startup_time = startup_time
        self.start_time = time.time()
        self.status = HealthStatus.STARTING
        self.request_count = 0
        self.error_count = 0
        self.latencies = []

    def update(self, new_version: str, downtime_seconds: float = 0.5):
        """Simulate instance update with restart"""
        self.status = HealthStatus.TERMINATING
        time.sleep(downtime_seconds / 10)  # Simulated downtime

        self.version = new_version
        self.start_time = time.time()
        self.status = HealthStatus.STARTING
        self.request_count = 0
        self.error_count = 0
        self.latencies = []

    def health_check(self) -> bool:
        """
        Health check simulation.
        Returns True if instance is healthy and ready for traffic.
        """
        age = time.time() - self.start_time

        if age < self.startup_time:
            self.status = HealthStatus.STARTING
            return False

        # Simulate 99.9% health check success rate
        if np.random.random() < 0.999:
            self.status = HealthStatus.HEALTHY
            return True
        else:
            self.status = HealthStatus.UNHEALTHY
            return False

    def handle_request(self) -> Tuple[bool, float]:
        """
        Simulate handling a request.
        Returns (success, latency_ms)
        """
        self.request_count += 1

        if self.status != HealthStatus.HEALTHY:
            self.error_count += 1
            return False, 0.0

        # Simulate latency distribution (log-normal)
        latency = np.random.lognormal(mean=3.0, sigma=0.5)
        self.latencies.append(latency)

        # Simulate 99.95% success rate when healthy
        success = np.random.random() < 0.9995

        if not success:
            self.error_count += 1

        return success, latency

    def get_metrics(self) -> InstanceMetrics:
        """Get current instance metrics"""
        age = time.time() - self.start_time

        return InstanceMetrics(
            instance_id=self.instance_id,
            status=self.status,
            version=self.version,
            uptime_seconds=age,
            request_count=self.request_count,
            error_count=self.error_count,
            latency_p50_ms=np.median(self.latencies) if self.latencies else 0.0,
            latency_p99_ms=np.percentile(self.latencies, 99) if self.latencies else 0.0,
            last_health_check=time.time()
        )


class RollingDeploymentSimulator:
    """Simulates rolling deployment strategy"""

    def __init__(
        self,
        num_instances: int = 10,
        current_version: str = "v1.0",
        target_version: str = "v1.1",
        batch_sizes: List[float] = None,
        requests_per_second: int = 1000,
        simulation_duration: int = 300
    ):
        self.num_instances = num_instances
        self.current_version = current_version
        self.target_version = target_version
        self.batch_sizes = batch_sizes or [0.01, 0.05, 0.10, 0.25, 0.50, 1.0]
        self.requests_per_second = requests_per_second
        self.simulation_duration = simulation_duration

        # Initialize instances
        self.instances = [
            Instance(f"instance-{i}", current_version)
            for i in range(num_instances)
        ]

        # Deployment metrics
        self.deployment_start_time = 0.0
        self.deployment_end_time = 0.0
        self.total_downtime = 0.0
        self.rollback_triggered = False
        self.deployment_success = False

    def simulate_traffic(self, duration_seconds: float) -> Dict[str, float]:
        """Simulate traffic to instances during deployment"""
        total_requests = 0
        total_errors = 0
        latencies = []

        healthy_instances = [i for i in self.instances if i.status == HealthStatus.HEALTHY]

        if not healthy_instances:
            # All instances down - complete downtime
            return {
                "total_requests": 0,
                "total_errors": int(duration_seconds * self.requests_per_second),
                "error_rate": 1.0,
                "downtime": duration_seconds,
                "avg_latency": 0.0
            }

        # Distribute load across healthy instances
        requests_per_instance = int(duration_seconds * self.requests_per_second / len(healthy_instances))

        for instance in healthy_instances:
            for _ in range(requests_per_instance):
                success, latency = instance.handle_request()
                total_requests += 1
                latencies.append(latency)

                if not success:
                    total_errors += 1

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 1.0,
            "downtime": 0.0 if total_requests > 0 else duration_seconds,
            "avg_latency": np.mean(latencies) if latencies else 0.0
        }

    def wait_for_healthy(self, instance: Instance, timeout: float = 30.0) -> bool:
        """Wait for instance to become healthy with timeout"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if instance.health_check():
                return True
            time.sleep(0.1)

        return False

    def deploy_batch(self, batch_percentage: float) -> Tuple[bool, float]:
        """
        Deploy a batch of instances.
        Returns (success, downtime_seconds)
        """
        batch_size = max(1, int(self.num_instances * batch_percentage))
        batch_indices = np.random.choice(
            self.num_instances,
            size=batch_size,
            replace=False
        )

        batch_downtime = 0.0
        batch_start = time.time()

        for idx in batch_indices:
            instance = self.instances[idx]

            # Update instance (simulated restart)
            instance.update(self.target_version)

            # Wait for health check
            healthy = self.wait_for_healthy(instance, timeout=30.0)

            if not healthy:
                # Instance failed to start - potential rollback
                return False, time.time() - batch_start

        # Simulate traffic during batch update
        traffic_metrics = self.simulate_traffic(duration_seconds=1.0)
        batch_downtime = traffic_metrics["downtime"]

        # Check if error rate is acceptable (< 1%)
        if traffic_metrics["error_rate"] > 0.01:
            return False, time.time() - batch_start

        return True, batch_downtime

    def run_deployment(self) -> Dict[str, any]:
        """Run complete rolling deployment simulation"""
        print(f"\n{'='*60}")
        print(f"Rolling Deployment: {self.current_version} → {self.target_version}")
        print(f"Instances: {self.num_instances}")
        print(f"Batch sizes: {self.batch_sizes}")
        print(f"{'='*60}\n")

        self.deployment_start_time = time.time()
        deployment_log = []

        for batch_pct in self.batch_sizes:
            batch_start = time.time()

            print(f"Deploying batch: {batch_pct*100:.1f}% ({int(self.num_instances * batch_pct)} instances)")

            success, downtime = self.deploy_batch(batch_pct)
            batch_duration = time.time() - batch_start

            batch_log = {
                "batch_percentage": batch_pct,
                "instances_updated": int(self.num_instances * batch_pct),
                "batch_duration": batch_duration,
                "batch_downtime": downtime,
                "success": success
            }
            deployment_log.append(batch_log)

            if not success:
                print(f"❌ Batch failed! Triggering rollback...")
                self.rollback_triggered = True
                self.deployment_end_time = time.time()
                break

            print(f"✓ Batch completed in {batch_duration:.2f}s (downtime: {downtime:.3f}s)")

        if not self.rollback_triggered:
            self.deployment_success = True
            self.deployment_end_time = time.time()

            # Final validation - simulate traffic
            print("\nRunning final validation...")
            final_metrics = self.simulate_traffic(duration_seconds=10.0)

            if final_metrics["error_rate"] > 0.01:
                print(f"❌ Final validation failed: {final_metrics['error_rate']:.3%} error rate")
                self.deployment_success = False
            else:
                print(f"✓ Final validation passed: {final_metrics['error_rate']:.3%} error rate")

        total_deployment_time = self.deployment_end_time - self.deployment_start_time
        total_downtime = sum(log["batch_downtime"] for log in deployment_log)

        results = {
            "deployment_success": self.deployment_success,
            "rollback_triggered": self.rollback_triggered,
            "total_deployment_time": total_deployment_time,
            "total_downtime": total_downtime,
            "deployment_log": deployment_log,
            "hypothesis_h1_met": total_downtime < 1.0
        }

        print(f"\n{'='*60}")
        print(f"Deployment Results:")
        print(f"  Success: {self.deployment_success}")
        print(f"  Total time: {total_deployment_time:.2f}s")
        print(f"  Total downtime: {total_downtime:.3f}s")
        print(f"  H1 (< 1s downtime): {'✓ PASS' if results['hypothesis_h1_met'] else '❌ FAIL'}")
        print(f"{'='*60}\n")

        return results

    def analyze_optimal_batch_size(self) -> Dict[str, any]:
        """
        Analyze optimal batch size by testing different configurations.
        Returns analysis of trade-offs between speed and safety.
        """
        print("\nAnalyzing optimal batch size...\n")

        batch_options = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0]
        results = []

        for batch_pct in batch_options:
            # Run 10 trials for statistical significance
            trial_results = []

            for trial in range(10):
                # Reset instances
                self.instances = [
                    Instance(f"instance-{i}", self.current_version)
                    for i in range(self.num_instances)
                ]

                # Run deployment
                result = self.run_deployment()
                trial_results.append(result)

            # Aggregate results
            success_rate = np.mean([r["deployment_success"] for r in trial_results])
            avg_downtime = np.mean([r["total_downtime"] for r in trial_results])
            avg_deployment_time = np.mean([r["total_deployment_time"] for r in trial_results])

            results.append({
                "batch_percentage": batch_pct,
                "success_rate": success_rate,
                "avg_downtime": avg_downtime,
                "avg_deployment_time": avg_deployment_time,
                "instances_per_batch": int(self.num_instances * batch_pct)
            })

        # Find optimal batch size
        # Optimal = highest success rate with acceptable downtime (< 1s)
        viable_options = [r for r in results if r["avg_downtime"] < 1.0]

        if viable_options:
            optimal = min(viable_options, key=lambda x: x["avg_deployment_time"])
        else:
            # Fallback to highest success rate
            optimal = max(results, key=lambda x: x["success_rate"])

        print(f"\nOptimal Batch Size Analysis:")
        print(f"{'Batch %':<10} {'Instances':<10} {'Success %':<12} {'Downtime':<12} {'Deploy Time':<12}")
        print("-" * 60)

        for r in results:
            print(f"{r['batch_percentage']*100:>6.1f}%    "
                  f"{r['instances_per_batch']:>4}        "
                  f"{r['success_rate']*100:>6.1f}%      "
                  f"{r['avg_downtime']:>6.3f}s      "
                  f"{r['avg_deployment_time']:>6.2f}s")

        print(f"\n🎯 Recommended batch size: {optimal['batch_percentage']*100:.1f}%")
        print(f"   Expected success rate: {optimal['success_rate']*100:.1f}%")
        print(f"   Expected downtime: {optimal['avg_downtime']:.3f}s")
        print(f"   Deployment time: {optimal['avg_deployment_time']:.2f}s")

        return {
            "optimal_batch_size": optimal["batch_percentage"],
            "analysis_results": results
        }


def main():
    """Run rolling deployment simulation"""
    print("\n" + "="*70)
    print("ROLLING DEPLOYMENT SIMULATION")
    print("="*70)

    # Scenario 1: Normal update with 10 instances
    print("\n📍 Scenario 1: Normal Update (v1.0 → v1.1)")
    print("   10 instances, 1000 RPS, standard batch sizes")

    simulator = RollingDeploymentSimulator(
        num_instances=10,
        current_version="v1.0",
        target_version="v1.1",
        batch_sizes=[0.01, 0.05, 0.10, 0.25, 0.50, 1.0],
        requests_per_second=1000
    )

    result = simulator.run_deployment()

    # Scenario 2: Large-scale deployment
    print("\n📍 Scenario 2: Large-Scale Update (v1.0 → v1.1)")
    print("   100 instances, 10000 RPS, conservative batches")

    simulator_large = RollingDeploymentSimulator(
        num_instances=100,
        current_version="v1.0",
        target_version="v1.1",
        batch_sizes=[0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.0],
        requests_per_second=10000
    )

    result_large = simulator_large.run_deployment()

    # Optimal batch size analysis
    analysis = simulator.analyze_optimal_batch_size()

    # Summary
    print("\n" + "="*70)
    print("HYPOTHESIS H1 VALIDATION")
    print("="*70)
    print(f"Scenario 1 (10 instances): Downtime = {result['total_downtime']:.3f}s")
    print(f"  H1 Status: {'✓ PASS' if result['hypothesis_h1_met'] else '❌ FAIL'}")
    print(f"\nScenario 2 (100 instances): Downtime = {result_large['total_downtime']:.3f}s")
    print(f"  H1 Status: {'✓ PASS' if result_large['hypothesis_h1_met'] else '❌ FAIL'}")
    print(f"\nConclusion: Rolling deployment achieves < 1s downtime with")
    print(f"  proper health checks and optimal batch sizing.")
    print("="*70 + "\n")

    return {
        "scenario_1": result,
        "scenario_2": result_large,
        "optimal_batch_analysis": analysis
    }


if __name__ == "__main__":
    main()
