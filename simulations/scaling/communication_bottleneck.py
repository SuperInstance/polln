"""
POLLN Communication Bottleneck Analysis
========================================

This module identifies the communication limits in large POLLN colonies.

Hypothesis H2: A2A communication becomes the bottleneck at N > 1000 agents.

Author: POLLN Simulation Team
Date: 2026-03-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from dataclasses import dataclass
from scipy.optimize import curve_fit
import pandas as pd
from pathlib import Path


@dataclass
class CommunicationMetrics:
    """Communication metrics for a colony."""
    colony_size: int
    a2a_packages_per_sec: float
    avg_package_size_kb: float
    serialization_latency_ms: float
    network_latency_ms: float
    total_bandwidth_gbps: float
    bandwidth_utilization_pct: float
    queue_depth: int
    dropped_packages_pct: float


class CommunicationBottleneckSimulator:
    """
    Simulates A2A package propagation to identify communication bottlenecks.
    """

    def __init__(self, seed: int = 42):
        """Initialize simulator."""
        np.random.seed(seed)

        # Communication parameters
        self.base_package_size_kb = 2.0  # Average A2A package size
        self.serialization_overhead = 0.05  # ms per KB
        self.network_bandwidth_gbps = 10.0  # Total available bandwidth
        self.max_queue_depth = 1000  # Max packages in queue

    def simulate_communication(
        self,
        n_agents: int,
        communication_rate: float = 10.0,  # Packages per agent per second
        duration_sec: float = 10.0
    ) -> CommunicationMetrics:
        """
        Simulate A2A communication in a colony of n_agents.

        Models:
        - Package generation
        - Serialization overhead
        - Network transmission
        - Queue buildup
        - Package drops
        """
        # Calculate total packages
        total_packages = int(n_agents * communication_rate * duration_sec)

        # Generate package sizes (log-normal distribution)
        package_sizes = np.random.lognormal(
            mean=np.log(self.base_package_size_kb),
            sigma=0.5,
            size=total_packages
        )

        # Serialization latency (scales with package size)
        serialization_latencies = package_sizes * self.serialization_overhead

        # Network latency (scales with colony size due to contention)
        # Model: base latency + contention penalty
        base_network_latency = 0.1  # ms
        contention_penalty = 0.001 * np.log(n_agents)  # Grows with log(N)
        network_latencies = base_network_latency + contention_penalty

        # Total latency per package
        total_latencies = serialization_latencies + network_latencies

        # Calculate bandwidth utilization
        total_data_gb = np.sum(package_sizes) / (1024 * 1024)  # Convert KB to GB
        effective_bandwidth = total_data_gb / duration_sec
        bandwidth_utilization = (effective_bandwidth / self.network_bandwidth_gbps) * 100

        # Simulate queue dynamics
        # Packages arrive at communication_rate * n_agents
        # Packages are processed at network_bandwidth / avg_package_size
        arrival_rate = n_agents * communication_rate  # packages/sec
        service_rate = (self.network_bandwidth_gbps * 1024 * 1024) / np.mean(package_sizes)

        # Queue buildup model (M/M/1 queue approximation)
        if arrival_rate < service_rate:
            traffic_intensity = arrival_rate / service_rate
            avg_queue_depth = (traffic_intensity ** 2) / (1 - traffic_intensity)
            dropped_packages = 0.0
        else:
            # System is overloaded
            avg_queue_depth = self.max_queue_depth
            excess_packages = total_packages - int(service_rate * duration_sec)
            dropped_packages = (excess_packages / total_packages) * 100

        return CommunicationMetrics(
            colony_size=n_agents,
            a2a_packages_per_sec=arrival_rate,
            avg_package_size_kb=np.mean(package_sizes),
            serialization_latency_ms=np.mean(serialization_latencies),
            network_latency_ms=np.mean(network_latencies),
            total_bandwidth_gbps=effective_bandwidth,
            bandwidth_utilization_pct=min(100, bandwidth_utilization),
            queue_depth=int(avg_queue_depth),
            dropped_packages_pct=dropped_packages
        )

    def find_bottleneck_threshold(
        self,
        min_agents: int = 100,
        max_agents: int = 10000,
        n_points: int = 50
    ) -> Tuple[int, Dict]:
        """
        Find the colony size where communication becomes a bottleneck.

        Bottleneck defined as:
        1. Bandwidth utilization > 80%
        2. Queue depth growing exponentially
        3. Dropped packages > 1%
        """
        print(f"Searching for bottleneck threshold between {min_agents} and {max_agents} agents...")

        colony_sizes = np.linspace(min_agents, max_agents, n_points, dtype=int)
        metrics_list = []

        for size in colony_sizes:
            metrics = self.simulate_communication(size)
            metrics_list.append(metrics)

        # Analyze metrics to find bottleneck
        bandwidth_util = [m.bandwidth_utilization_pct for m in metrics_list]
        dropped_pkgs = [m.dropped_packages_pct for m in metrics_list]
        queue_depths = [m.queue_depth for m in metrics_list]

        # Find threshold points
        bandwidth_threshold = None
        dropped_threshold = None
        queue_threshold = None

        for i, size in enumerate(colony_sizes):
            if bandwidth_threshold is None and bandwidth_util[i] > 80:
                bandwidth_threshold = size
            if dropped_threshold is None and dropped_pkgs[i] > 1.0:
                dropped_threshold = size
            if queue_threshold is None and queue_depths[i] > 100:
                queue_threshold = size

        # Overall bottleneck (first threshold reached)
        thresholds = [t for t in [bandwidth_threshold, dropped_threshold, queue_threshold] if t is not None]
        bottleneck_threshold = min(thresholds) if thresholds else max_agents

        # Fit models to predict bottleneck at other communication rates
        bottleneck_analysis = {
            'threshold': bottleneck_threshold,
            'bandwidth_threshold': bandwidth_threshold,
            'dropped_packages_threshold': dropped_threshold,
            'queue_threshold': queue_threshold,
            'at_threshold': {
                'bandwidth_utilization': bandwidth_util[colony_sizes.tolist().index(bottleneck_threshold)],
                'dropped_packages': dropped_pkgs[colony_sizes.tolist().index(bottleneck_threshold)],
                'queue_depth': queue_depths[colony_sizes.tolist().index(bottleneck_threshold)]
            }
        }

        return bottleneck_threshold, bottleneck_analysis

    def run_bottleneck_analysis(
        self,
        colony_sizes: List[int] = None,
        communication_rates: List[float] = None
    ) -> Tuple[List[CommunicationMetrics], Dict]:
        """
        Run comprehensive bottleneck analysis.

        Tests multiple colony sizes and communication rates to find
        the operating envelope and bottleneck boundaries.
        """
        if colony_sizes is None:
            colony_sizes = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000]

        if communication_rates is None:
            communication_rates = [5.0, 10.0, 20.0, 50.0]  # Packages/agent/sec

        print(f"Running bottleneck analysis across {len(colony_sizes)} colony sizes "
              f"and {len(communication_rates)} communication rates...")

        results = {}

        for rate in communication_rates:
            print(f"\nCommunication rate: {rate} packages/agent/sec")
            rate_metrics = []

            for size in colony_sizes:
                metrics = self.simulate_communication(size, communication_rate=rate)
                rate_metrics.append(metrics)

                if size in [500, 1000, 2000, 5000]:
                    print(f"  N={size:5d}: BW={metrics.bandwidth_utilization_pct:5.1f}%, "
                          f"Dropped={metrics.dropped_packages_pct:4.1f}%, "
                          f"Queue={metrics.queue_depth:4d}")

            results[rate] = rate_metrics

        # Find bottleneck threshold for each rate
        threshold_analysis = {}
        for rate, rate_metrics in results.items():
            for metrics in rate_metrics:
                if metrics.bandwidth_utilization_pct > 80 or \
                   metrics.dropped_packages_pct > 1.0:
                    threshold_analysis[rate] = metrics.colony_size
                    break

        # H2 validation: Is bottleneck around N ≈ 1000?
        # Check at standard communication rate (10 packages/sec)
        standard_rate_threshold = threshold_analysis.get(10.0, 10000)
        h2_validated = 900 <= standard_rate_threshold <= 1100

        analysis = {
            'thresholds_by_rate': threshold_analysis,
            'hypothesis_h2': {
                'validated': h2_validated,
                'threshold_at_standard_rate': standard_rate_threshold,
                'conclusion': 'H2 VALIDATED: Bottleneck at N ≈ 1000' if h2_validated
                             else f'H2 REJECTED: Bottleneck at N = {standard_rate_threshold}'
            }
        }

        return results, analysis

    def plot_bottleneck_analysis(
        self,
        results: Dict,
        analysis: Dict,
        output_dir: str = None
    ):
        """Generate bottleneck analysis plots."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'plots'
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-paper')
        plt.rcParams.update({
            'font.size': 10,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'figure.dpi': 300
        })

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Communication Bottleneck Analysis', fontsize=16, fontweight='bold')

        # Get data for standard rate (10 packages/sec)
        standard_metrics = results[10.0]
        colony_sizes = [m.colony_size for m in standard_metrics]

        # Plot 1: Bandwidth Utilization
        ax1 = axes[0, 0]
        for rate, metrics_list in results.items():
            sizes = [m.colony_size for m in metrics_list]
            utils = [m.bandwidth_utilization_pct for m in metrics_list]
            ax1.plot(sizes, utils, 'o-', label=f'{rate} pkg/s', alpha=0.7)

        ax1.axhline(y=80, color='r', linestyle='--', label='80% threshold')
        ax1.set_xlabel('Colony Size (N)')
        ax1.set_ylabel('Bandwidth Utilization (%)')
        ax1.set_title('Bandwidth Saturation')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Dropped Packages
        ax2 = axes[0, 1]
        for rate, metrics_list in results.items():
            sizes = [m.colony_size for m in metrics_list]
            dropped = [m.dropped_packages_pct for m in metrics_list]
            ax2.plot(sizes, dropped, 'o-', label=f'{rate} pkg/s', alpha=0.7)

        ax2.axhline(y=1.0, color='r', linestyle='--', label='1% threshold')
        ax2.set_xlabel('Colony Size (N)')
        ax2.set_ylabel('Dropped Packages (%)')
        ax2.set_title('Package Loss')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')

        # Plot 3: Queue Depth
        ax3 = axes[1, 0]
        for rate, metrics_list in results.items():
            sizes = [m.colony_size for m in metrics_list]
            queues = [m.queue_depth for m in metrics_list]
            ax3.plot(sizes, queues, 'o-', label=f'{rate} pkg/s', alpha=0.7)

        ax3.axhline(y=100, color='r', linestyle='--', label='Critical threshold')
        ax3.set_xlabel('Colony Size (N)')
        ax3.set_ylabel('Queue Depth')
        ax3.set_title('Queue Buildup')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')

        # Plot 4: Bottleneck Threshold vs Communication Rate
        ax4 = axes[1, 1]
        rates = sorted(results.keys())
        thresholds = [analysis['thresholds_by_rate'].get(r, 10000) for r in rates]
        ax4.plot(rates, thresholds, 'o-', color='steelblue', linewidth=2, markersize=8)
        ax4.axhline(y=1000, color='r', linestyle='--', label='N = 1000')
        ax4.fill_between(rates, 900, 1100, alpha=0.3, color='red', label='Target range')
        ax4.set_xlabel('Communication Rate (packages/agent/sec)')
        ax4.set_ylabel('Bottleneck Threshold (N)')
        ax4.set_title('Bottleneck vs Communication Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        fig_path = output_dir / 'bottleneck_analysis.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"\nBottleneck analysis saved to: {fig_path}")

        return fig_path

    def plot_serialization_overhead(
        self,
        output_dir: str = None
    ):
        """Analyze and plot serialization overhead vs package size."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'plots'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Test different package sizes
        package_sizes_kb = np.logspace(-1, 2, 50)  # 0.1 to 100 KB
        serialization_times = package_sizes_kb * self.serialization_overhead

        # Transmission times (at 10 Gbps)
        transmission_times = (package_sizes_kb * 8) / (10 * 1e6) * 1000  # Convert to ms

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(package_sizes_kb, serialization_times, 'r-', linewidth=2, label='Serialization')
        ax.plot(package_sizes_kb, transmission_times, 'b-', linewidth=2, label='Network transmission')
        ax.plot(package_sizes_kb, serialization_times + transmission_times,
                'g--', linewidth=2, label='Total latency')

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Package Size (KB)')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Communication Latency Breakdown')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add text showing crossover point
        crossover_idx = np.argmin(np.abs(serialization_times - transmission_times))
        crossover_size = package_sizes_kb[crossover_idx]
        ax.axvline(x=crossover_size, color='gray', linestyle=':', alpha=0.7)
        ax.text(crossover_size, ax.get_ylim()[1] * 0.5,
                f'Crossover: {crossover_size:.2f} KB',
                rotation=90, verticalalignment='center')

        plt.tight_layout()

        fig_path = output_dir / 'serialization_overhead.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"Serialization overhead plot saved to: {fig_path}")

        return fig_path


def main():
    """Main execution function."""
    print("="*60)
    print("POLLN Communication Bottleneck Analysis")
    print("="*60)

    simulator = CommunicationBottleneckSimulator(seed=42)

    # Run bottleneck analysis
    results, analysis = simulator.run_bottleneck_analysis()

    # Print results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    print("\nBottleneck thresholds by communication rate:")
    for rate, threshold in sorted(analysis['thresholds_by_rate'].items()):
        print(f"  {rate:5.1f} pkg/s: N = {threshold}")

    print("\n" + "="*60)
    print("HYPOTHESIS H2 VALIDATION")
    print("="*60)
    h2_result = analysis['hypothesis_h2']
    print(f"\n{h2_result['conclusion']}")
    print(f"Threshold at standard rate (10 pkg/s): N = {h2_result['threshold_at_standard_rate']}")

    # Generate plots
    print("\n" + "="*60)
    print("GENERATING PLOTS")
    print("="*60)
    simulator.plot_bottleneck_analysis(results, analysis)
    simulator.plot_serialization_overhead()

    # Save results
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    all_metrics = []
    for rate, metrics_list in results.items():
        for metrics in metrics_list:
            data = vars(metrics).copy()
            data['communication_rate'] = rate
            all_metrics.append(data)

    df = pd.DataFrame(all_metrics)
    csv_path = output_dir / 'bottleneck_metrics.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nMetrics saved to: {csv_path}")

    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)

    return results, analysis


if __name__ == '__main__':
    results, analysis = main()
