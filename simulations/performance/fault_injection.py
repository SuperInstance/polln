"""
POLLN Fault Injection - Fault Tolerance Validation

Validates H4: System maintains 99.9% availability with 10% agent failure rate

This simulation models:
- Random agent failures
- Replication strategies
- Recovery mechanisms
- Availability calculation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum
import json
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

# Availability SLA target
AVAILABILITY_TARGET = 0.999  # 99.9% availability (8.76 hours downtime/year)

# Failure rates to test
FAILURE_RATES = [0.01, 0.05, 0.10, 0.20, 0.30]  # 1% to 30% failure rate

# Replication strategies
class ReplicationStrategy(Enum):
    NO_REPLICATION = "no_replication"
    ACTIVE_PASSIVE = "active_passive"  # 1 primary, 1 standby
    ACTIVE_ACTIVE = "active_active"     # 2 active replicas
    THREE_WAY = "three_way"             # 3-way replication

# Simulation parameters
NUM_AGENTS = 100
SIMULATION_DURATION_HOURS = 24  # 1 day simulation
NUM_TRIALS = 100
SEED = 42

# ============================================================================
# MATHEMATICAL MODELS
# ============================================================================

def calculate_availability(
    uptime_seconds: float,
    total_seconds: float
) -> float:
    """
    Calculate availability (uptime / total time).

    Returns:
        Availability fraction (0-1)
    """
    return uptime_seconds / total_seconds if total_seconds > 0 else 0


def calculate_mean_time_to_recovery(
    recovery_times: List[float]
) -> float:
    """
    Calculate MTTR (Mean Time To Recovery).

    Args:
        recovery_times: List of recovery times in seconds

    Returns:
        MTTR in seconds
    """
    if not recovery_times:
        return 0.0
    return np.mean(recovery_times)


def calculate_mean_time_between_failures(
    failure_times: List[float],
    total_time: float
) -> float:
    """
    Calculate MTBF (Mean Time Between Failures).

    Args:
        failure_times: List of failure timestamps
        total_time: Total observation period

    Returns:
        MTBF in seconds
    """
    if len(failure_times) < 2:
        return total_time

    intervals = np.diff(failure_times)
    return np.mean(intervals)


# ============================================================================
# FAULT INJECTION MODELS
# ============================================================================

@dataclass
class AgentFailure:
    """Represents a single agent failure event."""
    agent_id: str
    failure_time: float  # seconds from start
    recovery_time: float  # seconds from start
    is_replicated: bool
    data_loss: bool = False


@dataclass
class FaultInjectionMetrics:
    """Metrics from a fault injection simulation."""
    failure_rate: float
    replication_strategy: str
    uptime_seconds: float
    total_seconds: float
    availability: float
    num_failures: int
    num_data_loss_events: int
    mttr_seconds: float
    mtbf_seconds: float
    failed_requests: int
    total_requests: int
    meets_sla: bool


class AgentState:
    """State of a single agent."""

    def __init__(self, agent_id: str, has_replica: bool = False):
        self.agent_id = agent_id
        self.has_replica = has_replica
        self.is_active = True
        self.failure_time: Optional[float] = None
        self.recovery_time: Optional[float] = None


class FaultInjectionSimulation:
    """
    Simulates POLLN behavior under agent failures.

    Models:
    - Random agent failures
    - Replication strategies
    - Recovery processes
    - Data loss events
    """

    def __init__(
        self,
        num_agents: int = NUM_AGENTS,
        replication_strategy: ReplicationStrategy = ReplicationStrategy.NO_REPLICATION,
        mttr_seconds: float = 60,  # Mean time to recovery
        failure_rate: float = 0.10,
        seed: int = SEED
    ):
        self.num_agents = num_agents
        self.replication_strategy = replication_strategy
        self.mttr_seconds = mttr_seconds
        self.failure_rate = failure_rate
        self.seed = seed
        np.random.seed(seed)

        # Initialize agents
        self.agents: List[AgentState] = []
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agents based on replication strategy."""
        num_active_agents = self.num_agents

        if self.replication_strategy == ReplicationStrategy.ACTIVE_PASSIVE:
            # Each agent has 1 standby replica
            num_active_agents = self.num_agents // 2
            for i in range(num_active_agents):
                self.agents.append(AgentState(f"agent-{i}", has_replica=True))

        elif self.replication_strategy == ReplicationStrategy.ACTIVE_ACTIVE:
            # All agents are active, each has 1 replica
            num_active_agents = self.num_agents // 2
            for i in range(num_active_agents):
                self.agents.append(AgentState(f"agent-{i}", has_replica=True))

        elif self.replication_strategy == ReplicationStrategy.THREE_WAY:
            # Each agent has 2 replicas
            num_active_agents = self.num_agents // 3
            for i in range(num_active_agents):
                self.agents.append(AgentState(f"agent-{i}", has_replica=True))

        else:  # NO_REPLICATION
            for i in range(self.num_agents):
                self.agents.append(AgentState(f"agent-{i}", has_replica=False))

    def simulate(
        self,
        duration_seconds: float = SIMULATION_DURATION_HOURS * 3600,
        arrival_rate: float = 167  # requests per second (~10k RPM)
    ) -> FaultInjectionMetrics:
        """
        Simulate system with fault injection.

        Args:
            duration_seconds: Simulation duration
            arrival_rate: Request arrival rate

        Returns:
            FaultInjectionMetrics
        """
        # Track failures
        failures: List[AgentFailure] = []
        active_agents = set(agent.agent_id for agent in self.agents)

        # Track downtime
        downtime_seconds = 0
        last_check_time = 0

        # Track requests
        failed_requests = 0
        total_requests = 0

        # Simulate failures over time
        current_time = 0
        check_interval = 1.0  # Check every second

        while current_time < duration_seconds:
            # Check for failures
            for agent in self.agents:
                if agent.is_active:
                    # Probabilistic failure
                    if np.random.random() < self.failure_rate * check_interval:
                        # Agent fails
                        agent.is_active = False
                        agent.failure_time = current_time

                        # Check if system can handle this failure
                        if agent.has_replica:
                            # Replica takes over, no downtime
                            pass
                        else:
                            # No replica, system loses capacity
                            if agent.agent_id in active_agents:
                                active_agents.remove(agent.agent_id)

                        failures.append(AgentFailure(
                            agent_id=agent.agent_id,
                            failure_time=current_time,
                            recovery_time=current_time + np.random.exponential(self.mttr_seconds),
                            is_replicated=agent.has_replica,
                            data_loss=(not agent.has_replica and np.random.random() < 0.1)
                        ))

            # Check for recoveries
            for agent in self.agents:
                if not agent.is_active and agent.failure_time is not None:
                    # Check if recovery time has passed
                    time_since_failure = current_time - agent.failure_time
                    expected_recovery = np.random.exponential(self.mttr_seconds)

                    if time_since_failure >= expected_recovery:
                        # Agent recovers
                        agent.is_active = True
                        agent.recovery_time = current_time
                        active_agents.add(agent.agent_id)

            # Calculate downtime (when we don't have enough active agents)
            min_required_agents = len(self.agents) * 0.5  # Need at least 50%
            if len(active_agents) < min_required_agents:
                downtime_seconds += check_interval

            # Process requests
            num_requests = np.random.poisson(arrival_rate * check_interval)
            total_requests += num_requests

            # Failed requests due to insufficient capacity
            capacity_factor = len(active_agents) / len(self.agents)
            if capacity_factor < 1.0:
                # Some requests fail due to lack of capacity
                failure_prob = 1.0 - capacity_factor
                failed_requests += int(num_requests * failure_prob)

            current_time += check_interval

        # Calculate metrics
        uptime_seconds = duration_seconds - downtime_seconds
        availability = calculate_availability(uptime_seconds, duration_seconds)

        recovery_times = [
            f.recovery_time - f.failure_time
            for f in failures
            if f.recovery_time is not None and f.failure_time is not None
        ]
        mttr = calculate_mean_time_to_recovery(recovery_times)

        failure_timestamps = [f.failure_time for f in failures]
        mtbf = calculate_mean_time_between_failures(failure_timestamps, duration_seconds)

        num_data_loss_events = sum(1 for f in failures if f.data_loss)

        meets_sla = availability >= AVAILABILITY_TARGET

        return FaultInjectionMetrics(
            failure_rate=self.failure_rate,
            replication_strategy=self.replication_strategy.value,
            uptime_seconds=uptime_seconds,
            total_seconds=duration_seconds,
            availability=availability,
            num_failures=len(failures),
            num_data_loss_events=num_data_loss_events,
            mttr_seconds=mttr,
            mtbf_seconds=mtbf,
            failed_requests=failed_requests,
            total_requests=total_requests,
            meets_sla=meets_sla
        )


def run_fault_injection_experiment(
    failure_rates: List[float] = None,
    replication_strategies: List[ReplicationStrategy] = None,
    num_trials: int = NUM_TRIALS,
    seed: int = SEED
) -> pd.DataFrame:
    """
    Run fault injection experiment across multiple scenarios.

    Returns:
        DataFrame with all results
    """
    if failure_rates is None:
        failure_rates = FAILURE_RATES

    if replication_strategies is None:
        replication_strategies = [
            ReplicationStrategy.NO_REPLICATION,
            ReplicationStrategy.ACTIVE_PASSIVE,
            ReplicationStrategy.ACTIVE_ACTIVE,
            ReplicationStrategy.THREE_WAY,
        ]

    results = []

    for strategy in replication_strategies:
        for failure_rate in failure_rates:
            for trial in range(num_trials):
                trial_seed = seed + trial

                sim = FaultInjectionSimulation(
                    num_agents=NUM_AGENTS,
                    replication_strategy=strategy,
                    failure_rate=failure_rate,
                    seed=trial_seed
                )

                metrics = sim.simulate(
                    duration_seconds=SIMULATION_DURATION_HOURS * 3600,
                    arrival_rate=167
                )

                results.append({
                    'trial': trial,
                    'replication_strategy': strategy.value,
                    'failure_rate': failure_rate,
                    'availability': metrics.availability,
                    'uptime_hours': metrics.uptime_seconds / 3600,
                    'downtime_seconds': metrics.total_seconds - metrics.uptime_seconds,
                    'num_failures': metrics.num_failures,
                    'num_data_loss_events': metrics.num_data_loss_events,
                    'mttr_seconds': metrics.mttr_seconds,
                    'mtbf_seconds': metrics.mtbf_seconds,
                    'failed_requests': metrics.failed_requests,
                    'total_requests': metrics.total_requests,
                    'request_success_rate': 1 - (metrics.failed_requests / metrics.total_requests),
                    'meets_sla': metrics.meets_sla,
                })

    return pd.DataFrame(results)


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_hypothesis_h4(results: pd.DataFrame) -> Dict:
    """
    Analyze H4: System maintains 99.9% availability with 10% agent failure rate.

    Returns:
        Dictionary with hypothesis validation results
    """
    # Filter for 10% failure rate
    results_10pct = results[results['failure_rate'] == 0.10]

    # Check each replication strategy
    strategy_results = {}
    for strategy in results_10pct['replication_strategy'].unique():
        strategy_data = results_10pct[results_10pct['replication_strategy'] == strategy]

        strategy_results[strategy] = {
            'mean_availability': float(strategy_data['availability'].mean()),
            'std_availability': float(strategy_data['availability'].std()),
            'min_availability': float(strategy_data['availability'].min()),
            'meets_sla': strategy_data['meets_sla'].all(),
            'mean_downtime_seconds': float(strategy_data['downtime_seconds'].mean()),
            'mean_mttr_seconds': float(strategy_data['mttr_seconds'].mean()),
            'mean_data_loss_events': float(strategy_data['num_data_loss_events'].mean()),
        }

    # Best strategy
    best_strategy = max(strategy_results.items(),
                       key=lambda x: x[1]['mean_availability'])

    # Overall compliance (with best strategy)
    overall_compliant = best_strategy[1]['meets_sla']

    # Availability vs failure rate analysis
    by_failure_rate = {}
    for rate in sorted(results['failure_rate'].unique()):
        rate_data = results[results['failure_rate'] == rate]

        # Use best strategy for this rate
        best_for_rate = rate_data.groupby('replication_strategy')['availability'].mean().idxmax()
        best_data = rate_data[rate_data['replication_strategy'] == best_for_rate]

        by_failure_rate[float(rate)] = {
            'best_strategy': best_for_rate,
            'mean_availability': float(best_data['availability'].mean()),
            'meets_sla': bool(best_data['meets_sla'].all()),
        }

    return {
        'hypothesis': 'H4: System maintains 99.9% availability with 10% agent failure rate',
        'target_availability': AVAILABILITY_TARGET,
        'overall_compliant': overall_compliant,
        'best_strategy': best_strategy[0],
        'by_replication_strategy': strategy_results,
        'by_failure_rate': by_failure_rate,
    }


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_fault_injection_results(
    results: pd.DataFrame,
    analysis: Dict,
    output_dir: Path
):
    """Generate publication-quality plots for fault injection results."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Availability by replication strategy (10% failure rate)
    fig, ax = plt.subplots(figsize=(12, 6))

    results_10pct = results[results['failure_rate'] == 0.10]

    strategies = results_10pct['replication_strategy'].unique()
    x = np.arange(len(strategies))
    width = 0.35

    means = [results_10pct[results_10pct['replication_strategy'] == s]['availability'].mean()
             for s in strategies]
    stds = [results_10pct[results_10pct['replication_strategy'] == s]['availability'].std()
            for s in strategies]

    bars = ax.bar(x, means, width, yerr=stds, capsize=5, alpha=0.7)

    # Color bars by compliance
    for i, bar in enumerate(bars):
        if means[i] >= AVAILABILITY_TARGET:
            bar.set_color('green')
        else:
            bar.set_color('red')

    ax.axhline(y=AVAILABILITY_TARGET, color='red', linestyle='--',
               label=f'SLA Target ({AVAILABILITY_TARGET*100:.1f}%)')

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies],
                       rotation=45, ha='right')
    ax.set_ylabel('Availability')
    ax.set_title('System Availability by Replication Strategy (10% Failure Rate)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.98, 1.0])

    plt.tight_layout()
    plt.savefig(output_dir / 'availability_by_strategy.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Availability vs failure rate
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy in strategies:
        strategy_data = results[results['replication_strategy'] == strategy]

        rates = sorted(strategy_data['failure_rate'].unique())
        availabilities = [strategy_data[strategy_data['failure_rate'] == r]['availability'].mean()
                         for r in rates]

        ax.plot(rates, availabilities, marker='o', label=strategy.replace('_', ' ').title(),
               linewidth=2)

    ax.axhline(y=AVAILABILITY_TARGET, color='red', linestyle='--',
               label=f'SLA Target ({AVAILABILITY_TARGET*100:.1f}%)')

    ax.set_xlabel('Failure Rate')
    ax.set_ylabel('Availability')
    ax.set_title('Availability vs Failure Rate')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.98, 1.0])

    plt.tight_layout()
    plt.savefig(output_dir / 'availability_vs_failure_rate.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Downtime distribution
    fig, ax = plt.subplots(figsize=(12, 6))

    results_10pct = results[results['failure_rate'] == 0.10]

    data_to_plot = []
    labels = []

    for strategy in strategies:
        strategy_data = results_10pct[results_10pct['replication_strategy'] == strategy]
        data_to_plot.append(strategy_data['downtime_seconds'].values)
        labels.append(strategy.replace('_', ' ').title())

    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)

    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')

    ax.set_ylabel('Downtime (seconds)')
    ax.set_title('Downtime Distribution by Strategy (10% Failure Rate)')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(output_dir / 'downtime_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Data loss events
    fig, ax = plt.subplots(figsize=(12, 6))

    results_10pct = results[results['failure_rate'] == 0.10]

    means = [results_10pct[results_10pct['replication_strategy'] == s]['num_data_loss_events'].mean()
             for s in strategies]

    bars = ax.bar(range(len(strategies)), means, alpha=0.7)

    ax.set_xticks(range(len(strategies)))
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies],
                       rotation=45, ha='right')
    ax.set_ylabel('Mean Data Loss Events')
    ax.set_title('Data Loss Events by Strategy (10% Failure Rate)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'data_loss_events.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. MTTR comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    results_10pct = results[results['failure_rate'] == 0.10]

    means = [results_10pct[results_10pct['replication_strategy'] == s]['mttr_seconds'].mean()
             for s in strategies]
    stds = [results_10pct[results_10pct['replication_strategy'] == s]['mttr_seconds'].std()
            for s in strategies]

    ax.bar(range(len(strategies)), means, yerr=stds, capsize=5, alpha=0.7)

    ax.set_xticks(range(len(strategies)))
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies],
                       rotation=45, ha='right')
    ax.set_ylabel('Mean Time To Recovery (seconds)')
    ax.set_title('MTTR by Strategy (10% Failure Rate)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'mttr_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    """Run comprehensive fault injection experiment."""

    print("=" * 80)
    print("POLLN Fault Injection - Fault Tolerance Validation")
    print("=" * 80)

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run experiment
    print("\nRunning fault injection simulations...")
    results = run_fault_injection_experiment(
        failure_rates=FAILURE_RATES,
        replication_strategies=list(ReplicationStrategy),
        num_trials=100,
        seed=SEED
    )

    # Save results
    results.to_csv(output_dir / 'fault_injection_results.csv', index=False)

    # Analyze H4
    print("\nAnalyzing H4...")
    analysis = analyze_hypothesis_h4(results)

    # Save analysis
    with open(output_dir / 'fault_injection_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    # Generate plots
    print("\nGenerating plots...")
    plot_fault_injection_results(results, analysis, output_dir)

    # Generate summary report
    report_path = output_dir / 'fault_injection_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("POLLN FAULT INJECTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"SLA Target: {AVAILABILITY_TARGET*100:.1f}% availability\n")
        f.write(f"Simulation Duration: {SIMULATION_DURATION_HOURS} hours\n")
        f.write(f"Failure Rate: 10%\n\n")

        f.write("HYPOTHESIS H4\n")
        f.write("-" * 80 + "\n")
        f.write(f"{analysis['hypothesis']}\n")
        f.write(f"Overall Compliant: {analysis['overall_compliant']}\n")
        f.write(f"Best Strategy: {analysis['best_strategy']}\n\n")

        f.write("BY REPLICATION STRATEGY (10% failure rate)\n")
        f.write("-" * 80 + "\n")
        for strategy, data in analysis['by_replication_strategy'].items():
            f.write(f"\n{strategy.upper().replace('_', ' ')}\n")
            f.write(f"  Mean Availability: {data['mean_availability']*100:.4f}%\n")
            f.write(f"  Min Availability: {data['min_availability']*100:.4f}%\n")
            f.write(f"  Meets SLA: {data['meets_sla']}\n")
            f.write(f"  Mean Downtime: {data['mean_downtime_seconds']:.1f} seconds\n")
            f.write(f"  Mean MTTR: {data['mean_mttr_seconds']:.1f} seconds\n")
            f.write(f"  Mean Data Loss Events: {data['mean_data_loss_events']:.1f}\n")

        f.write("\nAVAILABILITY VS FAILURE RATE\n")
        f.write("-" * 80 + "\n")
        for rate, data in analysis['by_failure_rate'].items():
            f.write(f"\n{rate*100:.0f}% Failure Rate:\n")
            f.write(f"  Best Strategy: {data['best_strategy']}\n")
            f.write(f"  Mean Availability: {data['mean_availability']*100:.4f}%\n")
            f.write(f"  Meets SLA: {data['meets_sla']}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("-" * 80 + "\n")

        if analysis['overall_compliant']:
            f.write("✓ H4 VALIDATED: System maintains 99.9% availability with 10% failure\n")
            f.write(f"  - {analysis['best_strategy']} strategy achieves ")
            f.write(f"{analysis['by_replication_strategy'][analysis['best_strategy']]['mean_availability']*100:.4f}% availability\n")
            f.write(f"  - Average downtime: {analysis['by_replication_strategy'][analysis['best_strategy']]['mean_downtime_seconds']:.1f} seconds\n")
        else:
            f.write("✗ H4 NOT VALIDATED: System does not maintain 99.9% availability\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"\nResults saved to {output_dir}")
    print(f"Summary report: {report_path}")

    return results, analysis


if __name__ == '__main__':
    main()
