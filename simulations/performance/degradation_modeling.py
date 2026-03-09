"""
POLLN Degradation Modeling - Graceful Degradation Analysis

Validates H3: Performance degrades linearly under overload (no catastrophic failure)

This simulation models:
- Backpressure mechanisms
- Queue overload behavior
- Linear degradation curves
- Comparison against catastrophic failure scenarios
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from datetime import datetime
from pathlib import Path

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Degradation scenarios
OVERLOAD_MULTIPLIERS = [1.0, 1.5, 2.0, 5.0, 10.0]  # 1x to 10x capacity
BASE_CAPACITY_RPM = 10000  # Base capacity in requests per minute

# Degradation model parameters
MAX_ACCEPTABLE_DEGRADATION = 0.5  # 50% degradation is acceptable
CATASTROPHIC_FAILURE_THRESHOLD = 0.8  # >80% degradation = catastrophic

# Simulation parameters
NUM_TRIALS = 100
SEED = 42

# ============================================================================
# MATHEMATICAL MODELS
# ============================================================================

def linear_degradation_model(
    overload_factor: float,
    slope: float = 0.1
) -> float:
    """
    Linear degradation model.

    Args:
        overload_factor: Multiple of base capacity (e.g., 2.0 = 2x load)
        slope: Degradation rate (0.1 = 10% degradation per unit overload)

    Returns:
        Fraction of original throughput maintained (0-1)
    """
    if overload_factor <= 1.0:
        return 1.0

    degradation = slope * (overload_factor - 1.0)
    return max(0.0, 1.0 - degradation)


def exponential_degradation_model(
    overload_factor: float,
    rate: float = 0.2
) -> float:
    """
    Exponential degradation model (catastrophic).

    Args:
        overload_factor: Multiple of base capacity
        rate: Exponential decay rate

    Returns:
        Fraction of original throughput maintained
    """
    if overload_factor <= 1.0:
        return 1.0

    return np.exp(-rate * (overload_factor - 1.0))


def backpressure_model(
    queue_length: int,
    queue_capacity: int,
    rejection_threshold: float = 0.9
) -> Tuple[int, int]:
    """
    Backpressure mechanism.

    Args:
        queue_length: Current queue length
        queue_capacity: Maximum queue capacity
        rejection_threshold: Reject requests when queue > threshold * capacity

    Returns:
        (accepted, rejected) counts
    """
    if queue_length >= queue_capacity:
        return (0, 1)  # Reject all

    if queue_length > rejection_threshold * queue_capacity:
        # Probabilistic rejection
        reject_prob = (queue_length - rejection_threshold * queue_capacity) / \
                     (queue_capacity - rejection_threshold * queue_capacity)
        if np.random.random() < reject_prob:
            return (0, 1)

    return (1, 0)  # Accept


# ============================================================================
# DEGRADATION SIMULATION
# ============================================================================

@dataclass
class DegradationMetrics:
    """Metrics from a degradation simulation."""
    overload_factor: float
    throughput_rpm: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float
    rejected_requests: int
    degradation_fraction: float  # 0-1, where 1 = no degradation
    is_catastrophic: bool


class DegradationSimulation:
    """
    Simulates POLLN behavior under overload conditions.

    Models:
    - Queue dynamics with backpressure
    - Service time degradation
    - Error rate increase
    - Throughput maintenance
    """

    def __init__(
        self,
        num_agents: int = 100,
        base_service_rate: float = 2.0,
        queue_capacity: int = 1000,
        enable_backpressure: bool = True,
        seed: int = SEED
    ):
        self.num_agents = num_agents
        self.base_service_rate = base_service_rate
        self.queue_capacity = queue_capacity
        self.enable_backpressure = enable_backpressure
        self.seed = seed
        np.random.seed(seed)

    def simulate_overload(
        self,
        overload_factor: float,
        duration_sec: float = 60
    ) -> DegradationMetrics:
        """
        Simulate system under given overload factor.

        Args:
            overload_factor: Multiple of base capacity
            duration_sec: Simulation duration

        Returns:
            DegradationMetrics
        """
        # Compute arrival rate
        base_arrival_rate = BASE_CAPACITY_RPM / 60  # requests per second
        arrival_rate = base_arrival_rate * overload_factor

        # Generate arrival times (Poisson process)
        num_requests = int(arrival_rate * duration_sec)
        inter_arrivals = np.random.exponential(1.0 / arrival_rate, num_requests)
        arrival_times = np.cumsum(inter_arrivals)

        # Simulate processing
        processed_requests = []
        queue = []
        rejected_count = 0

        agent_available_times = np.zeros(self.num_agents)

        for arrival_time in arrival_times:
            # Apply backpressure
            if self.enable_backpressure:
                accepted, rejected = backpressure_model(
                    len(queue),
                    self.queue_capacity
                )
                if rejected:
                    rejected_count += 1
                    continue

            # Add to queue
            queue.append(arrival_time)

            # Process requests
            while queue:
                # Find available agent
                available_agents = np.where(agent_available_times <= arrival_time)[0]

                if len(available_agents) == 0:
                    break

                # Get next request
                request_arrival = queue.pop(0)

                # Compute service time (degrades with load)
                load_factor = len(queue) / self.queue_capacity
                service_degradation = 1.0 + load_factor  # Up to 2x slower

                service_time = (1.0 / self.base_service_rate) * service_degradation
                service_time *= np.random.uniform(0.8, 1.2)  # Add variability

                # Assign to agent
                agent_idx = available_agents[0]
                start_time = max(arrival_time, agent_available_times[agent_idx])
                end_time = start_time + service_time

                agent_available_times[agent_idx] = end_time

                # Track
                latency_ms = (end_time - request_arrival) * 1000
                processed_requests.append(latency_ms)

        # Compute metrics
        if len(processed_requests) == 0:
            throughput_rpm = 0
            p50_latency = p95_latency = p99_latency = float('inf')
            error_rate = 1.0
        else:
            throughput_rpm = (len(processed_requests) / duration_sec) * 60
            p50_latency = np.percentile(processed_requests, 50)
            p95_latency = np.percentile(processed_requests, 95)
            p99_latency = np.percentile(processed_requests, 99)
            error_rate = rejected_count / num_requests

        # Compute degradation
        expected_throughput = BASE_CAPACITY_RPM
        degradation_fraction = throughput_rpm / expected_throughput if expected_throughput > 0 else 0

        # Check for catastrophic failure
        is_catastrophic = degradation_fraction < (1 - CATASTROPHIC_FAILURE_THRESHOLD)

        return DegradationMetrics(
            overload_factor=overload_factor,
            throughput_rpm=throughput_rpm,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            error_rate=error_rate,
            rejected_requests=rejected_count,
            degradation_fraction=degradation_fraction,
            is_catastrophic=is_catastrophic
        )


def run_degradation_experiment(
    overload_multipliers: List[float] = None,
    num_trials: int = NUM_TRIALS,
    enable_backpressure: bool = True,
    seed: int = SEED
) -> pd.DataFrame:
    """
    Run degradation experiment across multiple overload levels.

    Returns:
        DataFrame with all results
    """
    if overload_multipliers is None:
        overload_multipliers = OVERLOAD_MULTIPLIERS

    results = []

    for overload_factor in overload_multipliers:
        for trial in range(num_trials):
            trial_seed = seed + trial

            sim = DegradationSimulation(
                enable_backpressure=enable_backpressure,
                seed=trial_seed
            )

            metrics = sim.simulate_overload(
                overload_factor=overload_factor,
                duration_sec=60
            )

            results.append({
                'trial': trial,
                'overload_factor': overload_factor,
                'throughput_rpm': metrics.throughput_rpm,
                'p50_latency_ms': metrics.p50_latency_ms,
                'p95_latency_ms': metrics.p95_latency_ms,
                'p99_latency_ms': metrics.p99_latency_ms,
                'error_rate': metrics.error_rate,
                'rejected_requests': metrics.rejected_requests,
                'degradation_fraction': metrics.degradation_fraction,
                'is_catastrophic': metrics.is_catastrophic,
            })

    return pd.DataFrame(results)


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def fit_degradation_curve(
    results: pd.DataFrame
) -> Tuple[Dict, float]:
    """
    Fit degradation curve to determine if degradation is linear or catastrophic.

    Returns:
        (model_params, r_squared)
    """
    # Aggregate by overload factor
    agg = results.groupby('overload_factor').agg({
        'degradation_fraction': 'mean'
    }).reset_index()

    x = agg['overload_factor'].values
    y = agg['degradation_fraction'].values

    # Fit linear model: y = 1 - slope * (x - 1) for x > 1
    def linear_func(x, slope):
        return np.maximum(0, 1 - slope * (x - 1))

    # Fit exponential model: y = exp(-rate * (x - 1))
    def exp_func(x, rate):
        return np.exp(-rate * np.maximum(0, x - 1))

    try:
        popt_linear, _ = curve_fit(linear_func, x, y, p0=[0.1])
        residuals_linear = y - linear_func(x, *popt_linear)
        ss_res_linear = np.sum(residuals_linear**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared_linear = 1 - (ss_res_linear / ss_tot)

        popt_exp, _ = curve_fit(exp_func, x, y, p0=[0.2])
        residuals_exp = y - exp_func(x, *popt_exp)
        ss_res_exp = np.sum(residuals_exp**2)
        r_squared_exp = 1 - (ss_res_exp / ss_tot)

        # Choose better model
        if r_squared_linear > r_squared_exp:
            return {
                'model_type': 'linear',
                'slope': float(popt_linear[0]),
                'r_squared': float(r_squared_linear),
                'is_graceful': r_squared_linear > 0.8
            }, r_squared_linear
        else:
            return {
                'model_type': 'exponential',
                'rate': float(popt_exp[0]),
                'r_squared': float(r_squared_exp),
                'is_graceful': False  # Exponential = catastrophic
            }, r_squared_exp

    except Exception as e:
        return {
            'model_type': 'unknown',
            'error': str(e),
            'is_graceful': False
        }, 0.0


def analyze_hypothesis_h3(results: pd.DataFrame) -> Dict:
    """
    Analyze H3: Performance degrades linearly under overload.

    Returns:
        Dictionary with hypothesis validation results
    """
    # Fit degradation curve
    fit_results, r_squared = fit_degradation_curve(results)

    # Check for catastrophic failures
    catastrophic_count = results['is_catastrophic'].sum()
    total_count = len(results)

    # Analyze degradation at each overload level
    by_overload = {}
    for overload in sorted(results['overload_factor'].unique()):
        overload_data = results[results['overload_factor'] == overload]

        by_overload[float(overload)] = {
            'mean_degradation': float(overload_data['degradation_fraction'].mean()),
            'std_degradation': float(overload_data['degradation_fraction'].std()),
            'mean_throughput_rpm': float(overload_data['throughput_rpm'].mean()),
            'mean_error_rate': float(overload_data['error_rate'].mean()),
            'catastrophic_count': int(overload_data['is_catastrophic'].sum()),
        }

    # Determine if degradation is linear (graceful) or catastrophic
    is_graceful = (
        fit_results.get('is_graceful', False) and
        catastrophic_count == 0 and
        r_squared > 0.8
    )

    return {
        'hypothesis': 'H3: Performance degrades linearly under overload (no catastrophic failure)',
        'is_graceful': is_graceful,
        'degradation_model': fit_results,
        'r_squared': float(r_squared),
        'catastrophic_failures': {
            'count': int(catastrophic_count),
            'total': total_count,
            'percentage': float(catastrophic_count / total_count * 100) if total_count > 0 else 0
        },
        'by_overload_level': by_overload,
    }


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_degradation_results(
    results: pd.DataFrame,
    analysis: Dict,
    output_dir: Path
):
    """Generate publication-quality plots for degradation results."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Throughput degradation curve
    fig, ax = plt.subplots(figsize=(12, 6))

    # Aggregate data
    agg = results.groupby('overload_factor').agg({
        'throughput_rpm': ['mean', 'std'],
        'degradation_fraction': ['mean', 'std']
    }).reset_index()

    agg.columns = ['overload_factor', 'throughput_mean', 'throughput_std',
                   'degradation_mean', 'degradation_std']

    # Plot throughput
    ax.errorbar(agg['overload_factor'], agg['throughput_mean'],
               yerr=agg['throughput_std'], marker='o', capsize=5,
               linewidth=2, label='Measured Throughput', color='blue')

    # Plot theoretical linear degradation
    x_theory = np.linspace(1, max(agg['overload_factor']), 100)
    if analysis['degradation_model'].get('model_type') == 'linear':
        slope = analysis['degradation_model']['slope']
        y_theory = BASE_CAPACITY_RPM * np.maximum(0, 1 - slope * (x_theory - 1))
        ax.plot(x_theory, y_theory, '--', linewidth=2,
               label=f'Linear Model (slope={slope:.3f})', color='green')

    # Plot expected (no degradation)
    ax.axhline(y=BASE_CAPACITY_RPM, color='gray', linestyle=':',
              label='Expected (No Degradation)')

    ax.set_xlabel('Overload Factor (× Capacity)')
    ax.set_ylabel('Throughput (requests/minute)')
    ax.set_title('System Degradation Under Overload')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'degradation_curve.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Degradation fraction
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.errorbar(agg['overload_factor'], agg['degradation_mean'],
               yerr=agg['degradation_std'], marker='o', capsize=5,
               linewidth=2, label='Measured', color='blue')

    # Thresholds
    ax.axhline(y=1.0, color='green', linestyle='--', label='No Degradation')
    ax.axhline(y=1 - MAX_ACCEPTABLE_DEGRADATION, color='orange',
              linestyle='--', label='Max Acceptable Degradation')
    ax.axhline(y=1 - CATASTROPHIC_FAILURE_THRESHOLD, color='red',
              linestyle='--', label='Catastrophic Failure Threshold')

    ax.set_xlabel('Overload Factor (× Capacity)')
    ax.set_ylabel('Fraction of Original Throughput')
    ax.set_title('Degradation Fraction vs Overload')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.1])

    plt.tight_layout()
    plt.savefig(output_dir / 'degradation_fraction.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Latency degradation
    fig, ax = plt.subplots(figsize=(12, 6))

    agg_lat = results.groupby('overload_factor').agg({
        'p50_latency_ms': 'mean',
        'p95_latency_ms': 'mean',
        'p99_latency_ms': 'mean'
    }).reset_index()

    ax.plot(agg_lat['overload_factor'], agg_lat['p50_latency_ms'],
           marker='o', label='p50 Latency', linewidth=2)
    ax.plot(agg_lat['overload_factor'], agg_lat['p95_latency_ms'],
           marker='s', label='p95 Latency', linewidth=2)
    ax.plot(agg_lat['overload_factor'], agg_lat['p99_latency_ms'],
           marker='^', label='p99 Latency', linewidth=2)

    ax.set_xlabel('Overload Factor (× Capacity)')
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Latency Degradation Under Overload')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(output_dir / 'latency_degradation.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Error rate evolution
    fig, ax = plt.subplots(figsize=(12, 6))

    agg_err = results.groupby('overload_factor').agg({
        'error_rate': ['mean', 'std']
    }).reset_index()

    agg_err.columns = ['overload_factor', 'error_mean', 'error_std']

    ax.errorbar(agg_err['overload_factor'], agg_err['error_mean'],
               yerr=agg_err['error_std'], marker='o', capsize=5,
               linewidth=2, color='red')

    ax.axhline(y=0.001, color='orange', linestyle='--',
              label='SLA Threshold (0.1%)')

    ax.set_xlabel('Overload Factor (× Capacity)')
    ax.set_ylabel('Error Rate')
    ax.set_title('Error Rate Evolution Under Overload')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(output_dir / 'error_rate_evolution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Model fit comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Linear model fit
    x = agg['overload_factor'].values
    y = agg['degradation_mean'].values

    ax1.scatter(x, y, alpha=0.6, s=50, label='Data')

    if analysis['degradation_model'].get('model_type') == 'linear':
        slope = analysis['degradation_model']['slope']
        x_fit = np.linspace(1, max(x), 100)
        y_fit = np.maximum(0, 1 - slope * (x_fit - 1))
        ax1.plot(x_fit, y_fit, 'r-', linewidth=2,
                label=f'Linear Fit (R²={analysis["r_squared"]:.3f})')

    ax1.set_xlabel('Overload Factor')
    ax1.set_ylabel('Degradation Fraction')
    ax1.set_title('Linear Model Fit')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.1])

    # Residuals
    if analysis['degradation_model'].get('model_type') == 'linear':
        y_pred = np.maximum(0, 1 - slope * (x - 1))
        residuals = y - y_pred

        ax2.scatter(x, residuals, alpha=0.6, s=50)
        ax2.axhline(y=0, color='red', linestyle='--')
        ax2.set_xlabel('Overload Factor')
        ax2.set_ylabel('Residuals')
        ax2.set_title('Model Residuals')
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'model_fit.png', dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    """Run comprehensive degradation modeling experiment."""

    print("=" * 80)
    print("POLLN Degradation Modeling - Graceful Degradation Analysis")
    print("=" * 80)

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run experiment
    print("\nRunning degradation simulations...")
    results = run_degradation_experiment(
        overload_multipliers=OVERLOAD_MULTIPLIERS,
        num_trials=100,
        enable_backpressure=True,
        seed=SEED
    )

    # Save results
    results.to_csv(output_dir / 'degradation_results.csv', index=False)

    # Analyze H3
    print("\nAnalyzing H3...")
    analysis = analyze_hypothesis_h3(results)

    # Save analysis
    with open(output_dir / 'degradation_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    # Generate plots
    print("\nGenerating plots...")
    plot_degradation_results(results, analysis, output_dir)

    # Generate summary report
    report_path = output_dir / 'degradation_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("POLLN DEGRADATION MODELING REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        f.write("HYPOTHESIS H3\n")
        f.write("-" * 80 + "\n")
        f.write(f"{analysis['hypothesis']}\n")
        f.write(f"Is Graceful: {analysis['is_graceful']}\n")
        f.write(f"Model Type: {analysis['degradation_model'].get('model_type', 'unknown')}\n")
        f.write(f"R²: {analysis['r_squared']:.3f}\n\n")

        f.write("CATASTROPHIC FAILURES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Count: {analysis['catastrophic_failures']['count']}\n")
        f.write(f"Total Trials: {analysis['catastrophic_failures']['total']}\n")
        f.write(f"Percentage: {analysis['catastrophic_failures']['percentage']:.2f}%\n\n")

        f.write("DEGRADATION BY OVERLOAD LEVEL\n")
        f.write("-" * 80 + "\n")
        for overload, data in analysis['by_overload_level'].items():
            f.write(f"\n{overload}x Capacity:\n")
            f.write(f"  Throughput: {data['mean_throughput_rpm']:.0f} RPM "
                   f"({data['mean_degradation']*100:.1f}% of original)\n")
            f.write(f"  Error Rate: {data['mean_error_rate']*100:.2f}%\n")
            f.write(f"  Catastrophic: {data['catastrophic_count']} trials\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("-" * 80 + "\n")

        if analysis['is_graceful']:
            f.write("✓ H3 VALIDATED: Performance degrades linearly under overload\n")
            f.write(f"  - Linear degradation with R² = {analysis['r_squared']:.3f}\n")
            f.write(f"  - No catastrophic failures observed\n")
            f.write(f"  - Backpressure mechanism prevents collapse\n")
        else:
            f.write("✗ H3 NOT VALIDATED: System shows catastrophic failure behavior\n")
            if analysis['catastrophic_failures']['count'] > 0:
                f.write(f"  - {analysis['catastrophic_failures']['count']} catastrophic failures detected\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nResults saved to {output_dir}")
    print(f"Summary report: {report_path}")

    return results, analysis


if __name__ == '__main__':
    main()
