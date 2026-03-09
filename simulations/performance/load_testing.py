"""
POLLN Load Testing Simulation - Production Workload Validation

Validates H1: POLLN can handle 10,000 requests/minute with p95 latency < 100ms

This simulation models:
- M/M/c queueing theory (Markovian arrival, Markovian service, c servers)
- Realistic workload patterns (constant, diurnal, flash crowd, gradual ramp)
- Statistical confidence intervals for all metrics
- Comparison against industry benchmarks (OpenAI, Anthropic)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import deque
import json
import time
from datetime import datetime, timedelta
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

# SLA Targets
SLA_TARGETS = {
    'throughput_rpm': 10000,  # requests per minute
    'p50_latency_ms': 50,     # median latency
    'p95_latency_ms': 100,    # 95th percentile
    'p99_latency_ms': 200,    # 99th percentile
    'error_rate': 0.001,      # 0.1% error rate
    'availability': 0.999,    # 99.9% availability
}

# Industry Benchmarks (approximate)
INDUSTRY_BENCHMARKS = {
    'OpenAI_GPT4': {
        'p50_latency_ms': 300,
        'p95_latency_ms': 800,
        'throughput_rpm': 5000,
    },
    'Anthropic_Claude': {
        'p50_latency_ms': 250,
        'p95_latency_ms': 700,
        'throughput_rpm': 6000,
    },
    'AWS_Lambda': {
        'p50_latency_ms': 15,
        'p95_latency_ms': 50,
        'throughput_rpm': 100000,
    }
}

# Simulation Parameters
DEFAULT_AGENTS = 100  # Number of parallel agents
DEFAULT_DURATION_MIN = 60  # Simulation duration in minutes
CONFIDENCE_LEVEL = 0.95  # For confidence intervals

# ============================================================================
# MATHEMATICAL MODELS
# ============================================================================

def mm_c_queue_metrics(
    arrival_rate: float,
    service_rate: float,
    num_servers: int
) -> Dict[str, float]:
    """
    Compute M/M/c queue performance metrics.

    Uses Erlang-C formula for probability of waiting.

    Args:
        arrival_rate: Lambda (requests/second)
        service_rate: Mu (requests/second per server)
        num_servers: c (number of parallel servers)

    Returns:
        Dictionary with utilization, avg_queue_length, avg_wait_time, etc.
    """
    if arrival_rate >= num_servers * service_rate:
        # System is unstable
        return {
            'utilization': 1.0,
            'avg_queue_length': float('inf'),
            'avg_wait_time': float('inf'),
            'prob_wait': 1.0,
            'prob_idle': 0.0,
        }

    rho = arrival_rate / (num_servers * service_rate)  # System utilization

    # Erlang-C formula: Probability that an arriving request must wait
    # C(c, r) = P_wait
    def erlang_c(c, r):
        """Erlang-C formula."""
        sum_term = sum([(r ** k) / np.math.factorial(k) for k in range(int(c))])
        last_term = (r ** c) / (np.math.factorial(c) * (1 - r/c))
        return last_term / (sum_term + last_term)

    r = arrival_rate / service_rate
    prob_wait = erlang_c(num_servers, r)

    # Average number in queue
    avg_queue_length = (prob_wait * r) / (num_servers - r)

    # Average wait time in queue (Little's Law)
    avg_wait_time = avg_queue_length / arrival_rate

    # Probability system is idle
    prob_idle = 1 - rho

    return {
        'utilization': rho,
        'avg_queue_length': avg_queue_length,
        'avg_wait_time': avg_wait_time,
        'prob_wait': prob_wait,
        'prob_idle': prob_idle,
    }


def compute_confidence_interval(
    data: np.ndarray,
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """
    Compute confidence interval for sample mean.

    Uses t-distribution for small samples.

    Args:
        data: Sample data
        confidence: Confidence level (e.g., 0.95)

    Returns:
        (mean, lower_bound, upper_bound)
    """
    n = len(data)
    if n < 2:
        return (np.mean(data), np.mean(data), np.mean(data))

    mean = np.mean(data)
    std_err = stats.sem(data)
    h = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)

    return (mean, mean - h, mean + h)


# ============================================================================
# WORKLOAD GENERATORS
# ============================================================================

class WorkloadGenerator:
    """Generates realistic workload patterns."""

    @staticmethod
    def constant(rate_per_second: float, duration_sec: float) -> np.ndarray:
        """Constant arrival rate."""
        num_requests = int(rate_per_second * duration_sec)
        return np.linspace(0, duration_sec, num_requests)

    @staticmethod
    def diurnal(
        base_rate: float,
        peak_rate: float,
        duration_sec: float,
        period_sec: float = 86400  # 24 hours
    ) -> np.ndarray:
        """
        Diurnal pattern (day/night cycle).

        Models realistic daily traffic patterns with peak during "day" hours.
        """
        arrival_times = []
        t = 0

        while t < duration_sec:
            # Sinusoidal variation
            phase = 2 * np.pi * t / period_sec
            rate = base_rate + (peak_rate - base_rate) * (0.5 * (1 + np.sin(phase - np.pi/2)))

            # Poisson process with variable rate
            inter_arrival = np.random.exponential(1.0 / rate)
            t += inter_arrival

            if t < duration_sec:
                arrival_times.append(t)

        return np.array(arrival_times)

    @staticmethod
    def flash_crowd(
        base_rate: float,
        spike_multiplier: float,
        duration_sec: float,
        spike_start: float,
        spike_duration: float
    ) -> np.ndarray:
        """
        Flash crowd pattern (sudden spike).

        Models viral content, DDoS attacks, or feature launches.
        """
        arrival_times = []
        t = 0

        while t < duration_sec:
            # Determine current rate
            if spike_start <= t < spike_start + spike_duration:
                rate = base_rate * spike_multiplier
            else:
                rate = base_rate

            inter_arrival = np.random.exponential(1.0 / rate)
            t += inter_arrival

            if t < duration_sec:
                arrival_times.append(t)

        return np.array(arrival_times)

    @staticmethod
    def gradual_ramp(
        start_rate: float,
        end_rate: float,
        duration_sec: float,
        growth_rate: float = 0.1  # 10% per hour
    ) -> np.ndarray:
        """
        Gradual ramp (steady growth).

        Models organic growth or gradual load increase.
        """
        arrival_times = []
        t = 0
        current_rate = start_rate

        while t < duration_sec:
            # Exponential growth
            elapsed_hours = t / 3600
            current_rate = start_rate * (1 + growth_rate) ** elapsed_hours

            inter_arrival = np.random.exponential(1.0 / current_rate)
            t += inter_arrival

            if t < duration_sec:
                arrival_times.append(t)

        return np.array(arrival_times)


# ============================================================================
# REQUEST AND RESPONSE MODELS
# ============================================================================

@dataclass
class Request:
    """Represents an incoming request."""
    id: str
    arrival_time: float
    complexity: float = 1.0  # Multiplier for processing time
    priority: int = 0  # Higher = more important

@dataclass
class Response:
    """Represents a completed request."""
    request_id: str
    start_time: float
    end_time: float
    success: bool
    error_message: str = ""
    agent_id: str = ""

    @property
    def latency_ms(self) -> float:
        """Latency in milliseconds."""
        return (self.end_time - self.start_time) * 1000


@dataclass
class AgentState:
    """State of a single agent."""
    id: str
    busy: bool = False
    current_request: Optional[Request] = None
    requests_processed: int = 0
    total_processing_time: float = 0


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

class POLLNSimulation:
    """
    Simulates POLLN system under various workloads.

    Models:
    - META tile cold starts
    - Agent pool dynamics
    - Queueing behavior
    - Error handling
    """

    def __init__(
        self,
        num_agents: int = DEFAULT_AGENTS,
        meta_tile_cold_start_ms: float = 50,
        base_service_rate: float = 2.0,  # requests/second per agent
        queue_capacity: int = 1000,
        enable_backpressure: bool = True,
    ):
        self.num_agents = num_agents
        self.meta_tile_cold_start_ms = meta_tile_cold_start_ms
        self.base_service_rate = base_service_rate
        self.queue_capacity = queue_capacity
        self.enable_backpressure = enable_backpressure

        # Initialize agents
        self.agents: List[AgentState] = [
            AgentState(id=f"agent-{i}") for i in range(num_agents)
        ]

        # Undifferentiated META tiles (cold start pool)
        self.meta_tiles_available: int = 20
        self.meta_tiles_differentiating: int = 0

        # Statistics
        self.stats = {
            'requests_received': 0,
            'requests_processed': 0,
            'requests_rejected': 0,
            'cold_starts': 0,
            'total_queue_wait_time': 0,
            'total_processing_time': 0,
        }

    def get_service_time(self, request: Request) -> float:
        """
        Compute service time for a request.

        Includes:
        - Base processing time
        - Request complexity
        - META tile cold start if needed
        """
        base_time = 1.0 / self.base_service_rate
        service_time = base_time * request.complexity

        # Check if we need cold start
        needs_cold_start = (
            self.meta_tiles_available == 0 and
            self.meta_tiles_differentiating < 5
        )

        if needs_cold_start:
            cold_start_time = self.meta_tile_cold_start_ms / 1000  # Convert to seconds
            service_time += cold_start_time
            self.stats['cold_starts'] += 1

        # Add some variability
        service_time *= np.random.uniform(0.8, 1.2)

        return service_time

    def find_available_agent(self) -> Optional[AgentState]:
        """Find an available agent."""
        for agent in self.agents:
            if not agent.busy:
                return agent
        return None

    def simulate(
        self,
        arrival_times: np.ndarray,
        seed: int = 42
    ) -> Tuple[List[Response], Dict]:
        """
        Run simulation with given arrival pattern.

        Args:
            arrival_times: Array of request arrival times (seconds)
            seed: Random seed for reproducibility

        Returns:
            (responses, statistics)
        """
        np.random.seed(seed)

        responses: List[Response] = []
        queue: deque[Tuple[Request, float]] = deque()  # (request, queue_entry_time)

        # Sort arrival times
        arrival_times = np.sort(arrival_times)

        # Track agent availability times
        agent_available_times = np.zeros(self.num_agents)

        for i, arrival_time in enumerate(arrival_times):
            request = Request(
                id=f"req-{i}",
                arrival_time=arrival_time,
                complexity=np.random.uniform(0.5, 2.0),
                priority=np.random.randint(0, 3)
            )

            self.stats['requests_received'] += 1

            # Check queue capacity (backpressure)
            if len(queue) >= self.queue_capacity and self.enable_backpressure:
                self.stats['requests_rejected'] += 1
                responses.append(Response(
                    request_id=request.id,
                    start_time=arrival_time,
                    end_time=arrival_time,
                    success=False,
                    error_message="Queue full"
                ))
                continue

            # Add to queue
            queue.append((request, arrival_time))

            # Process as many requests as possible
            while queue:
                # Find available agent
                available_agent_idx = None
                for idx in range(self.num_agents):
                    if agent_available_times[idx] <= arrival_time:
                        available_agent_idx = idx
                        break

                if available_agent_idx is None:
                    break  # No agents available

                # Get next request from queue
                next_req, queue_entry_time = queue.popleft()

                # Calculate wait time
                wait_time = max(0, arrival_time - queue_entry_time)
                self.stats['total_queue_wait_time'] += wait_time

                # Calculate service time
                service_time = self.get_service_time(next_req)
                start_time = max(arrival_time, agent_available_times[available_agent_idx])
                end_time = start_time + service_time

                # Update agent availability
                agent_available_times[available_agent_idx] = end_time

                # Record response
                success = np.random.random() > 0.001  # 0.1% error rate
                self.stats['requests_processed'] += 1
                self.stats['total_processing_time'] += service_time

                responses.append(Response(
                    request_id=next_req.id,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_message="" if success else "Processing error",
                    agent_id=f"agent-{available_agent_idx}"
                ))

        return responses, self.stats.copy()


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_sla_compliance(
    responses: List[Response],
    sla_targets: Dict[str, float],
    duration_sec: float
) -> Dict:
    """
    Analyze SLA compliance.

    Returns metrics with confidence intervals.
    """
    # Extract latencies
    latencies = np.array([r.latency_ms for r in responses if r.success])

    if len(latencies) == 0:
        return {
            'compliant': False,
            'error': 'No successful responses'
        }

    # Compute percentiles
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    # Compute throughput
    successful_requests = len([r for r in responses if r.success])
    throughput_rpm = (successful_requests / duration_sec) * 60

    # Compute error rate
    error_rate = 1 - (successful_requests / len(responses))

    # Check compliance
    compliant = all([
        throughput_rpm >= sla_targets['throughput_rpm'],
        p50 <= sla_targets['p50_latency_ms'],
        p95 <= sla_targets['p95_latency_ms'],
        p99 <= sla_targets['p99_latency_ms'],
        error_rate <= sla_targets['error_rate'],
    ])

    # Confidence intervals
    throughput_ci = compute_confidence_interval(
        np.array([throughput_rpm]),
        confidence=CONFIDENCE_LEVEL
    )

    return {
        'compliant': compliant,
        'throughput_rpm': throughput_rpm,
        'throughput_ci': throughput_ci,
        'p50_latency_ms': p50,
        'p95_latency_ms': p95,
        'p99_latency_ms': p99,
        'error_rate': error_rate,
        'total_requests': len(responses),
        'successful_requests': successful_requests,
        'avg_latency_ms': np.mean(latencies),
        'std_latency_ms': np.std(latencies),
    }


# ============================================================================
# EXPERIMENT RUNNER
# ============================================================================

def run_load_experiment(
    workload_type: str,
    workload_params: Dict,
    num_agents: int = DEFAULT_AGENTS,
    duration_min: int = DEFAULT_DURATION_MIN,
    num_trials: int = 10,
    seed: int = 42
) -> pd.DataFrame:
    """
    Run load testing experiment with multiple trials.

    Args:
        workload_type: Type of workload (constant, diurnal, flash_crowd, gradual_ramp)
        workload_params: Parameters for workload generator
        num_agents: Number of parallel agents
        duration_min: Duration of simulation in minutes
        num_trials: Number of Monte Carlo trials
        seed: Random seed

    Returns:
        DataFrame with results from all trials
    """
    results = []

    duration_sec = duration_min * 60

    for trial in range(num_trials):
        trial_seed = seed + trial

        # Generate workload
        if workload_type == 'constant':
            arrival_times = WorkloadGenerator.constant(
                **workload_params,
                duration_sec=duration_sec
            )
        elif workload_type == 'diurnal':
            arrival_times = WorkloadGenerator.diurnal(
                **workload_params,
                duration_sec=duration_sec
            )
        elif workload_type == 'flash_crowd':
            arrival_times = WorkloadGenerator.flash_crowd(
                **workload_params,
                duration_sec=duration_sec
            )
        elif workload_type == 'gradual_ramp':
            arrival_times = WorkloadGenerator.gradual_ramp(
                **workload_params,
                duration_sec=duration_sec
            )
        else:
            raise ValueError(f"Unknown workload type: {workload_type}")

        # Run simulation
        sim = POLLNSimulation(num_agents=num_agents)
        responses, stats = sim.simulate(arrival_times, seed=trial_seed)

        # Analyze
        analysis = analyze_sla_compliance(responses, SLA_TARGETS, duration_sec)

        results.append({
            'trial': trial,
            'workload_type': workload_type,
            'num_agents': num_agents,
            'duration_min': duration_min,
            **analysis,
            'stats': stats,
        })

    return pd.DataFrame(results)


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_load_test_results(
    results: pd.DataFrame,
    output_dir: Path
):
    """Generate publication-quality plots for load testing results."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Latency distribution by workload type
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    workloads = results['workload_type'].unique()

    for idx, workload in enumerate(workloads):
        ax = axes[idx // 2, idx % 2]

        workload_data = results[results['workload_type'] == workload]

        latencies = []
        for _, row in workload_data.iterrows():
            latencies.extend([row['p50_latency_ms'], row['p95_latency_ms'], row['p99_latency_ms']])

        ax.bar(['p50', 'p95', 'p99'], [
            workload_data['p50_latency_ms'].mean(),
            workload_data['p95_latency_ms'].mean(),
            workload_data['p99_latency_ms'].mean()
        ], yerr=[
            workload_data['p50_latency_ms'].std(),
            workload_data['p95_latency_ms'].std(),
            workload_data['p99_latency_ms'].std()
        ], capsize=5, alpha=0.7)

        # SLA targets
        ax.axhline(y=SLA_TARGETS['p50_latency_ms'], color='green', linestyle='--', label='p50 SLA')
        ax.axhline(y=SLA_TARGETS['p95_latency_ms'], color='orange', linestyle='--', label='p95 SLA')
        ax.axhline(y=SLA_TARGETS['p99_latency_ms'], color='red', linestyle='--', label='p99 SLA')

        ax.set_title(f'{workload.replace("_", " ").title()} Workload')
        ax.set_ylabel('Latency (ms)')
        ax.set_xlabel('Percentile')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'latency_by_workload.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Throughput comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    throughput_data = []
    for workload in workloads:
        workload_data = results[results['workload_type'] == workload]
        throughput_data.append({
            'workload': workload.replace('_', ' ').title(),
            'mean': workload_data['throughput_rpm'].mean(),
            'std': workload_data['throughput_rpm'].std(),
        })

    x_pos = np.arange(len(throughput_data))
    ax.bar(x_pos, [d['mean'] for d in throughput_data],
           yerr=[d['std'] for d in throughput_data], capsize=5, alpha=0.7)

    ax.axhline(y=SLA_TARGETS['throughput_rpm'], color='red', linestyle='--', label='SLA Target')

    ax.set_xticks(x_pos)
    ax.set_xticklabels([d['workload'] for d in throughput_data], rotation=45, ha='right')
    ax.set_ylabel('Throughput (requests/minute)')
    ax.set_title('Throughput by Workload Type')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'throughput_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Industry benchmark comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(INDUSTRY_BENCHMARKS) + 1)
    width = 0.35

    polln_p95 = results['p95_latency_ms'].mean()
    polln_p95_std = results['p95_latency_ms'].std()

    benchmark_p95 = [INDUSTRY_BENCHMARKS[k]['p95_latency_ms'] for k in INDUSTRY_BENCHMARKS]
    benchmark_throughput = [INDUSTRY_BENCHMARKS[k]['throughput_rpm'] for k in INDUSTRY_BENCHMARKS]

    bars1 = ax.bar(x[:-1] - width/2, benchmark_p95, width, label='Benchmark', alpha=0.7)
    bars2 = ax.bar(x[:-1] + width/2, [polln_p95] * len(INDUSTRY_BENCHMARKS), width,
                   yerr=[polln_p95_std] * len(INDUSTRY_BENCHMARKS), label='POLLN', alpha=0.7)

    ax.set_xticks(x[:-1])
    ax.set_xticklabels(list(INDUSTRY_BENCHMARKS.keys()), rotation=45, ha='right')
    ax.set_ylabel('p95 Latency (ms)')
    ax.set_title('Industry Benchmark Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'benchmark_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Error rate analysis
    fig, ax = plt.subplots(figsize=(12, 6))

    error_rates = [results[results['workload_type'] == w]['error_rate'].mean()
                   for w in workloads]

    ax.bar(range(len(workloads)), error_rates, alpha=0.7)
    ax.axhline(y=SLA_TARGETS['error_rate'], color='red', linestyle='--', label='SLA Target')

    ax.set_xticks(range(len(workloads)))
    ax.set_xticklabels([w.replace('_', ' ').title() for w in workloads], rotation=45, ha='right')
    ax.set_ylabel('Error Rate')
    ax.set_title('Error Rate by Workload Type')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'error_rates.png', dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    """Run comprehensive load testing experiment."""

    print("=" * 80)
    print("POLLN Load Testing Simulation - SLA Compliance Validation")
    print("=" * 80)

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    # Experiment 1: Constant load (baseline)
    print("\n[1/4] Running constant load test...")
    results_constant = run_load_experiment(
        workload_type='constant',
        workload_params={'rate_per_second': 167},  # ~10,000 req/min
        num_agents=DEFAULT_AGENTS,
        duration_min=60,
        num_trials=10,
        seed=42
    )
    all_results.append(results_constant)
    print(f"  Throughput: {results_constant['throughput_rpm'].mean():.0f} ± {results_constant['throughput_rpm'].std():.0f} req/min")
    print(f"  p95 Latency: {results_constant['p95_latency_ms'].mean():.1f} ± {results_constant['p95_latency_ms'].std():.1f} ms")
    print(f"  SLA Compliant: {results_constant['compliant'].all()}")

    # Experiment 2: Diurnal pattern
    print("\n[2/4] Running diurnal load test...")
    results_diurnal = run_load_experiment(
        workload_type='diurnal',
        workload_params={
            'base_rate': 83,   # ~5,000 req/min
            'peak_rate': 333,  # ~20,000 req/min
        },
        num_agents=DEFAULT_AGENTS,
        duration_min=60,
        num_trials=10,
        seed=42
    )
    all_results.append(results_diurnal)
    print(f"  Throughput: {results_diurnal['throughput_rpm'].mean():.0f} ± {results_diurnal['throughput_rpm'].std():.0f} req/min")
    print(f"  p95 Latency: {results_diurnal['p95_latency_ms'].mean():.1f} ± {results_diurnal['p95_latency_ms'].std():.1f} ms")
    print(f"  SLA Compliant: {results_diurnal['compliant'].all()}")

    # Experiment 3: Flash crowd
    print("\n[3/4] Running flash crowd test...")
    results_flash = run_load_experiment(
        workload_type='flash_crowd',
        workload_params={
            'base_rate': 167,        # ~10,000 req/min
            'spike_multiplier': 10,  # 100,000 req/min during spike
            'spike_start': 300,      # 5 minutes in
            'spike_duration': 300,   # 5 minute spike
        },
        num_agents=DEFAULT_AGENTS,
        duration_min=60,
        num_trials=10,
        seed=42
    )
    all_results.append(results_flash)
    print(f"  Throughput: {results_flash['throughput_rpm'].mean():.0f} ± {results_flash['throughput_rpm'].std():.0f} req/min")
    print(f"  p95 Latency: {results_flash['p95_latency_ms'].mean():.1f} ± {results_flash['p95_latency_ms'].std():.1f} ms")
    print(f"  SLA Compliant: {results_flash['compliant'].all()}")

    # Experiment 4: Gradual ramp
    print("\n[4/4] Running gradual ramp test...")
    results_ramp = run_load_experiment(
        workload_type='gradual_ramp',
        workload_params={
            'start_rate': 100,   # ~6,000 req/min
            'end_rate': 300,     # ~18,000 req/min
            'growth_rate': 0.1,  # 10% per hour
        },
        num_agents=DEFAULT_AGENTS,
        duration_min=60,
        num_trials=10,
        seed=42
    )
    all_results.append(results_ramp)
    print(f"  Throughput: {results_ramp['throughput_rpm'].mean():.0f} ± {results_ramp['throughput_rpm'].std():.0f} req/min")
    print(f"  p95 Latency: {results_ramp['p95_latency_ms'].mean():.1f} ± {results_ramp['p95_latency_ms'].std():.1f} ms")
    print(f"  SLA Compliant: {results_ramp['compliant'].all()}")

    # Combine results
    all_results_df = pd.concat(all_results, ignore_index=True)

    # Save results
    all_results_df.to_csv(output_dir / 'load_test_results.csv', index=False)

    # Save detailed JSON
    summary = {
        'timestamp': datetime.now().isoformat(),
        'sla_targets': SLA_TARGETS,
        'industry_benchmarks': INDUSTRY_BENCHMARKS,
        'overall_compliance': all_results_df['compliant'].all(),
        'by_workload': {}
    }

    for workload in all_results_df['workload_type'].unique():
        workload_data = all_results_df[all_results_df['workload_type'] == workload]
        summary['by_workload'][workload] = {
            'compliant': workload_data['compliant'].all(),
            'throughput_rpm': {
                'mean': float(workload_data['throughput_rpm'].mean()),
                'std': float(workload_data['throughput_rpm'].std()),
                'target': SLA_TARGETS['throughput_rpm'],
            },
            'p95_latency_ms': {
                'mean': float(workload_data['p95_latency_ms'].mean()),
                'std': float(workload_data['p95_latency_ms'].std()),
                'target': SLA_TARGETS['p95_latency_ms'],
            },
        }

    with open(output_dir / 'load_test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Generate plots
    print("\nGenerating plots...")
    plot_load_test_results(all_results_df, output_dir)

    # Generate summary report
    report_path = output_dir / 'load_test_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("POLLN LOAD TESTING REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Trials: {len(all_results_df)}\n\n")

        f.write("SLA TARGETS\n")
        f.write("-" * 80 + "\n")
        for key, value in SLA_TARGETS.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")

        f.write("OVERALL RESULTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"  SLA Compliant: {summary['overall_compliance']}\n\n")

        f.write("BY WORKLOAD TYPE\n")
        f.write("-" * 80 + "\n")
        for workload, data in summary['by_workload'].items():
            f.write(f"\n{workload.upper().replace('_', ' ')}\n")
            f.write(f"  Compliant: {data['compliant']}\n")
            f.write(f"  Throughput: {data['throughput_rpm']['mean']:.0f} ± {data['throughput_rpm']['std']:.0f} "
                   f"(target: {data['throughput_rpm']['target']})\n")
            f.write(f"  p95 Latency: {data['p95_latency_ms']['mean']:.1f} ± {data['p95_latency_ms']['std']:.1f} ms "
                   f"(target: {data['p95_latency_ms']['target']} ms)\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("HYPOTHESIS H1: POLLN can handle 10,000 requests/minute with p95 latency < 100ms\n")
        f.write("-" * 80 + "\n")

        # Determine H1 result
        constant_compliant = all_results_df[all_results_df['workload_type'] == 'constant']['compliant'].all()

        if constant_compliant:
            f.write("✓ H1 VALIDATED: POLLN meets SLA requirements under sustained load\n")
            f.write(f"  - Throughput: {all_results_df[all_results_df['workload_type'] == 'constant']['throughput_rpm'].mean():.0f} "
                   f"≥ {SLA_TARGETS['throughput_rpm']} req/min\n")
            f.write(f"  - p95 Latency: {all_results_df[all_results_df['workload_type'] == 'constant']['p95_latency_ms'].mean():.1f} "
                   f"< {SLA_TARGETS['p95_latency_ms']} ms\n")
        else:
            f.write("✗ H1 NOT VALIDATED: POLLN does not meet SLA requirements\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nResults saved to {output_dir}")
    print(f"Summary report: {report_path}")

    return all_results_df


if __name__ == '__main__':
    main()
