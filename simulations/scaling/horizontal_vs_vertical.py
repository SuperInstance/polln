"""
POLLN Horizontal vs Vertical Scaling Analysis
==============================================

This module compares horizontal scaling (many small agents) with vertical scaling
(few large agents) to determine the most cost-effective approach.

Hypothesis H3: Horizontal scaling achieves 3-5x better cost-performance.

Author: POLLN Simulation Team
Date: 2026-03-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from dataclasses import dataclass
from scipy.optimize import curve_fit
from scipy.stats import ttest_ind
import pandas as pd
from pathlib import Path


@dataclass
class ScalingConfiguration:
    """Configuration for a scaling experiment."""
    name: str
    n_agents: int
    agent_memory_mb: float
    agent_cpu_cores: float
    agent_cost_per_hour: float


@dataclass
class ScalingMetrics:
    """Metrics from a scaling experiment."""
    config: ScalingConfiguration
    total_throughput: float  # requests/second
    avg_latency_ms: float
    cost_per_1m_requests: float  # USD
    fault_tolerance_score: float
    memory_utilization_pct: float
    cpu_utilization_pct: float
    total_memory_gb: float
    total_cpu_cores: float
    total_cost_per_hour: float


class ScalingComparisonSimulator:
    """
    Simulates and compares horizontal vs vertical scaling strategies.
    """

    def __init__(self, seed: int = 42):
        """Initialize simulator."""
        np.random.seed(seed)

        # Cost model (based on cloud pricing)
        self.cost_per_gb_memory = 0.005  # $/hour
        self.cost_per_cpu_core = 0.05  # $/hour
        self.base_agent_cost = 0.001  # $/hour overhead per agent

    def create_configurations(self) -> List[ScalingConfiguration]:
        """
        Create test configurations for horizontal and vertical scaling.

        Horizontal: Many small, cheap agents
        Vertical: Few large, expensive agents
        """
        configs = []

        # Horizontal scaling (many small agents)
        # Target: 1000 agents, 10MB each
        configs.append(ScalingConfiguration(
            name="Horizontal-1000",
            n_agents=1000,
            agent_memory_mb=10,
            agent_cpu_cores=0.01,
            agent_cost_per_hour=self._calculate_agent_cost(10, 0.01)
        ))

        configs.append(ScalingConfiguration(
            name="Horizontal-500",
            n_agents=500,
            agent_memory_mb=20,
            agent_cpu_cores=0.02,
            agent_cost_per_hour=self._calculate_agent_cost(20, 0.02)
        ))

        # Vertical scaling (few large agents)
        # Target: 10 agents, 1GB each
        configs.append(ScalingConfiguration(
            name="Vertical-10",
            n_agents=10,
            agent_memory_mb=1000,
            agent_cpu_cores=1.0,
            agent_cost_per_hour=self._calculate_agent_cost(1000, 1.0)
        ))

        configs.append(ScalingConfiguration(
            name="Vertical-20",
            n_agents=20,
            agent_memory_mb=500,
            agent_cpu_cores=0.5,
            agent_cost_per_hour=self._calculate_agent_cost(500, 0.5)
        ))

        # Hybrid approaches
        configs.append(ScalingConfiguration(
            name="Hybrid-100",
            n_agents=100,
            agent_memory_mb=100,
            agent_cpu_cores=0.1,
            agent_cost_per_hour=self._calculate_agent_cost(100, 0.1)
        ))

        return configs

    def _calculate_agent_cost(self, memory_mb: float, cpu_cores: float) -> float:
        """Calculate hourly cost for a single agent."""
        memory_cost = (memory_mb / 1024) * self.cost_per_gb_memory
        cpu_cost = cpu_cores * self.cost_per_cpu_core
        return memory_cost + cpu_cost + self.base_agent_cost

    def simulate_configuration(
        self,
        config: ScalingConfiguration,
        duration_sec: float = 3600
    ) -> ScalingMetrics:
        """
        Simulate a scaling configuration.

        Models:
        - Agent performance (scales with resources)
        - Communication overhead (scales with colony size)
        - Fault tolerance (scales with agent count)
        """
        # Performance model
        # Throughput scales with CPU cores but has diminishing returns
        base_throughput_per_core = 1000  # requests/second/core
        cpu_efficiency = 1.0 - np.exp(-config.agent_cpu_cores * 5)
        agent_throughput = base_throughput_per_core * config.agent_cpu_cores * cpu_efficiency

        # Communication overhead penalty
        # More agents = more communication overhead
        comm_overhead = 0.01 * np.log(config.n_agents)
        effective_throughput = agent_throughput * (1 - comm_overhead)

        total_throughput = effective_throughput * config.n_agents

        # Latency model
        base_latency = 1.0  # ms
        memory_latency_penalty = 0.001 * (config.agent_memory_mb / 100)
        comm_latency_penalty = 0.1 * np.log(config.n_agents)
        avg_latency = base_latency + memory_latency_penalty + comm_latency_penalty

        # Cost calculations
        total_cost_per_hour = config.agent_cost_per_hour * config.n_agents
        requests_per_hour = total_throughput * 3600
        cost_per_1m_requests = (total_cost_per_hour / requests_per_hour) * 1e6

        # Fault tolerance score
        # More agents = better fault tolerance (redundancy)
        # Model: 1 - exp(-k * N) where k scales with agent size
        redundancy_factor = 0.001 * (config.agent_memory_mb / 10)
        fault_tolerance = 1 - np.exp(-redundancy_factor * config.n_agents)

        # Resource utilization
        memory_utilization = 75 + np.random.normal(0, 5)  # % with noise
        cpu_utilization = 70 + np.random.normal(0, 10)  # % with noise

        return ScalingMetrics(
            config=config,
            total_throughput=total_throughput,
            avg_latency_ms=avg_latency,
            cost_per_1m_requests=cost_per_1m_requests,
            fault_tolerance_score=fault_tolerance,
            memory_utilization_pct=max(0, min(100, memory_utilization)),
            cpu_utilization_pct=max(0, min(100, cpu_utilization)),
            total_memory_gb=(config.agent_memory_mb * config.n_agents) / 1024,
            total_cpu_cores=config.agent_cpu_cores * config.n_agents,
            total_cost_per_hour=total_cost_per_hour
        )

    def run_comparison_experiment(
        self,
        n_trials: int = 20
    ) -> Tuple[List[ScalingMetrics], Dict]:
        """
        Run comparison between horizontal and vertical scaling.
        """
        print("="*60)
        print("Horizontal vs Vertical Scaling Comparison")
        print("="*60)

        configs = self.create_configurations()
        print(f"\nTesting {len(configs)} configurations, {n_trials} trials each...")

        results = {config.name: [] for config in configs}

        for config in configs:
            print(f"\n{config.name}:")
            print(f"  Agents: {config.n_agents}")
            print(f"  Memory/agent: {config.agent_memory_mb} MB")
            print(f"  CPU/agent: {config.agent_cpu_cores} cores")
            print(f"  Cost/agent: ${config.agent_cost_per_hour:.4f}/hour")

            for trial in range(n_trials):
                metrics = self.simulate_configuration(config)
                results[config.name].append(metrics)

                if trial == 0:
                    print(f"  Trial 1: {metrics.total_throughput:.0f} req/s, "
                          f"${metrics.cost_per_1m_requests:.4f}/1M req")

        # Aggregate results
        aggregated = {}
        for config_name, metrics_list in results.items():
            throughputs = [m.total_throughput for m in metrics_list]
            costs = [m.cost_per_1m_requests for m in metrics_list]
            latencies = [m.avg_latency_ms for m in metrics_list]
            fault_scores = [m.fault_tolerance_score for m in metrics_list]

            aggregated[config_name] = {
                'avg_throughput': np.mean(throughputs),
                'std_throughput': np.std(throughputs),
                'avg_cost': np.mean(costs),
                'std_cost': np.std(costs),
                'avg_latency': np.mean(latencies),
                'avg_fault_tolerance': np.mean(fault_scores),
                'avg_metrics': metrics_list[0]  # Use first as representative
            }

        # Statistical analysis
        analysis = self._perform_statistical_analysis(results, aggregated)

        return aggregated, analysis

    def _perform_statistical_analysis(
        self,
        results: Dict[str, List[ScalingMetrics]],
        aggregated: Dict[str, Dict]
    ) -> Dict:
        """
        Perform statistical analysis to compare horizontal vs vertical scaling.

        Tests:
        - Cost difference significance (t-test)
        - Throughput difference significance
        - Calculate cost-performance ratio
        """
        horizontal_costs = [m.cost_per_1m_requests
                           for m in results['Horizontal-1000']]
        vertical_costs = [m.cost_per_1m_requests
                         for m in results['Vertical-10']]

        horizontal_throughput = [m.total_throughput
                                 for m in results['Horizontal-1000']]
        vertical_throughput = [m.total_throughput
                               for m in results['Vertical-10']]

        # T-tests for significance
        cost_t_stat, cost_p_value = ttest_ind(horizontal_costs, vertical_costs)
        throughput_t_stat, throughput_p_value = ttest_ind(
            horizontal_throughput, vertical_throughput
        )

        # Calculate cost-performance ratio
        horizontal_avg_cost = aggregated['Horizontal-1000']['avg_cost']
        vertical_avg_cost = aggregated['Vertical-10']['avg_cost']
        horizontal_avg_throughput = aggregated['Horizontal-1000']['avg_throughput']
        vertical_avg_throughput = aggregated['Vertical-10']['avg_throughput']

        horizontal_cpr = horizontal_avg_throughput / horizontal_avg_cost
        vertical_cpr = vertical_avg_throughput / vertical_avg_cost

        cost_performance_ratio = horizontal_cpr / vertical_cpr

        # H3 validation: Is horizontal 3-5x better?
        h3_validated = 3.0 <= cost_performance_ratio <= 5.0

        analysis = {
            'statistical_tests': {
                'cost_difference': {
                    't_statistic': cost_t_stat,
                    'p_value': cost_p_value,
                    'significant': cost_p_value < 0.05
                },
                'throughput_difference': {
                    't_statistic': throughput_t_stat,
                    'p_value': throughput_p_value,
                    'significant': throughput_p_value < 0.05
                }
            },
            'cost_performance': {
                'horizontal_cpr': horizontal_cpr,
                'vertical_cpr': vertical_cpr,
                'ratio': cost_performance_ratio
            },
            'hypothesis_h3': {
                'validated': h3_validated,
                'cost_performance_ratio': cost_performance_ratio,
                'conclusion': f'H3 VALIDATED: Horizontal is {cost_performance_ratio:.2f}x better'
                             if h3_validated
                             else f'H3 REJECTED: Ratio is {cost_performance_ratio:.2f}x (expected 3-5x)'
            }
        }

        return analysis

    def plot_comparison(
        self,
        aggregated: Dict[str, Dict],
        analysis: Dict,
        output_dir: str = None
    ):
        """Generate comparison plots."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'plots'
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
        fig.suptitle('Horizontal vs Vertical Scaling Comparison',
                    fontsize=16, fontweight='bold')

        config_names = list(aggregated.keys())
        x = np.arange(len(config_names))

        # Plot 1: Total Throughput
        ax1 = axes[0, 0]
        throughputs = [aggregated[name]['avg_throughput'] for name in config_names]
        errors = [aggregated[name]['std_throughput'] for name in config_names]

        colors = ['green' if 'Horizontal' in name else 'orange' if 'Vertical' in name else 'blue'
                 for name in config_names]

        ax1.bar(x, throughputs, yerr=errors, alpha=0.7, color=colors, capsize=5)
        ax1.set_xticks(x)
        ax1.set_xticklabels(config_names, rotation=45, ha='right')
        ax1.set_ylabel('Total Throughput (req/s)')
        ax1.set_title('Throughput Comparison')
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Cost per 1M Requests
        ax2 = axes[0, 1]
        costs = [aggregated[name]['avg_cost'] for name in config_names]
        cost_errors = [aggregated[name]['std_cost'] for name in config_names]

        ax2.bar(x, costs, yerr=cost_errors, alpha=0.7, color=colors, capsize=5)
        ax2.set_xticks(x)
        ax2.set_xticklabels(config_names, rotation=45, ha='right')
        ax2.set_ylabel('Cost per 1M Requests ($)')
        ax2.set_title('Cost Efficiency')
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Cost-Performance Ratio
        ax3 = axes[1, 0]
        cpr_values = [aggregated[name]['avg_throughput'] / aggregated[name]['avg_cost']
                     for name in config_names]

        ax3.bar(x, cpr_values, alpha=0.7, color=colors)
        ax3.set_xticks(x)
        ax3.set_xticklabels(config_names, rotation=45, ha='right')
        ax3.set_ylabel('Cost-Performance Ratio\n(req/s per $)')
        ax3.set_title('Cost-Performance')
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: Fault Tolerance
        ax4 = axes[1, 1]
        fault_scores = [aggregated[name]['avg_fault_tolerance'] for name in config_names]

        ax4.bar(x, fault_scores, alpha=0.7, color=colors)
        ax4.set_xticks(x)
        ax4.set_xticklabels(config_names, rotation=45, ha='right')
        ax4.set_ylabel('Fault Tolerance Score')
        ax4.set_title('Fault Tolerance')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_ylim([0, 1])

        plt.tight_layout()

        fig_path = output_dir / 'horizontal_vs_vertical.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"\nComparison plot saved to: {fig_path}")

        # Create summary comparison table
        fig_table, ax_table = plt.subplots(figsize=(12, 6))
        ax_table.axis('tight')
        ax_table.axis('off')

        # Prepare comparison data
        horizontal = aggregated['Horizontal-1000']
        vertical = aggregated['Vertical-10']

        table_data = [
            ['Metric', 'Horizontal (1000×10MB)', 'Vertical (10×1GB)', 'Improvement'],
            ['Total Throughput (req/s)',
             f'{horizontal["avg_throughput"]:.0f}',
             f'{vertical["avg_throughput"]:.0f}',
             f'{horizontal["avg_throughput"]/vertical["avg_throughput"]:.2f}x'],
            ['Cost per 1M Requests ($)',
             f'{horizontal["avg_cost"]:.4f}',
             f'{vertical["avg_cost"]:.4f}',
             f'{vertical["avg_cost"]/horizontal["avg_cost"]:.2f}x cheaper'],
            ['Cost-Performance Ratio',
             f'{horizontal["avg_throughput"]/horizontal["avg_cost"]:.0f}',
             f'{vertical["avg_throughput"]/vertical["avg_cost"]:.0f}',
             f'{analysis["cost_performance"]["ratio"]:.2f}x'],
            ['Fault Tolerance Score',
             f'{horizontal["avg_fault_tolerance"]:.3f}',
             f'{vertical["avg_fault_tolerance"]:.3f}',
             f'{horizontal["avg_fault_tolerance"]/vertical["avg_fault_tolerance"]:.2f}x'],
            ['Total Memory (GB)',
             f'{horizontal["avg_metrics"].total_memory_gb:.1f}',
             f'{vertical["avg_metrics"].total_memory_gb:.1f}',
             'Same'],
            ['Total CPU Cores',
             f'{horizontal["avg_metrics"].total_cpu_cores:.1f}',
             f'{vertical["avg_metrics"].total_cpu_cores:.1f}',
             'Same']
        ]

        table = ax_table.table(cellText=table_data, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.5, 2)

        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Highlight improvement column
        for i in range(1, 8):
            table[(i, 3)].set_facecolor('#E8F5E9')

        fig_table.suptitle('Horizontal vs Vertical Scaling Summary',
                          fontsize=14, fontweight='bold')

        table_path = output_dir / 'scaling_comparison_table.png'
        plt.savefig(table_path, dpi=300, bbox_inches='tight')
        print(f"Comparison table saved to: {table_path}")

        return fig_path, table_path

    def save_results(
        self,
        aggregated: Dict[str, Dict],
        analysis: Dict,
        output_dir: str = None
    ):
        """Save results to CSV."""
        if output_dir is None:
            output_dir = Path(__file__).parent / 'results'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create summary DataFrame
        summary_data = []
        for config_name, data in aggregated.items():
            metrics = data['avg_metrics']
            summary_data.append({
                'configuration': config_name,
                'n_agents': metrics.config.n_agents,
                'agent_memory_mb': metrics.config.agent_memory_mb,
                'agent_cpu_cores': metrics.config.agent_cpu_cores,
                'total_throughput': data['avg_throughput'],
                'throughput_std': data['std_throughput'],
                'cost_per_1m_requests': data['avg_cost'],
                'cost_std': data['std_cost'],
                'avg_latency_ms': data['avg_latency'],
                'fault_tolerance_score': data['avg_fault_tolerance'],
                'total_memory_gb': metrics.total_memory_gb,
                'total_cpu_cores': metrics.total_cpu_cores,
                'cost_per_hour': metrics.total_cost_per_hour
            })

        df = pd.DataFrame(summary_data)
        csv_path = output_dir / 'scaling_comparison.csv'
        df.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

        return csv_path


def main():
    """Main execution function."""
    simulator = ScalingComparisonSimulator(seed=42)

    # Run comparison experiment
    aggregated, analysis = simulator.run_comparison_experiment(n_trials=20)

    # Print results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    print("\nConfiguration Performance:")
    print(f"{'Configuration':<20} {'Throughput':>15} {'Cost/1M':>12} {'CPR':>12}")
    print("-"*70)
    for config_name, data in aggregated.items():
        cpr = data['avg_throughput'] / data['avg_cost']
        print(f"{config_name:<20} {data['avg_throughput']:>15.0f} "
              f"{data['avg_cost']:>12.4f} {cpr:>12.0f}")

    print("\n" + "="*60)
    print("HYPOTHESIS H3 VALIDATION")
    print("="*60)
    h3_result = analysis['hypothesis_h3']
    print(f"\n{h3_result['conclusion']}")
    print(f"Cost-Performance Ratio: {h3_result['cost_performance_ratio']:.2f}x")

    print(f"\nStatistical Significance:")
    print(f"Cost difference: p = {analysis['statistical_tests']['cost_difference']['p_value']:.6f}")
    print(f"Throughput difference: p = {analysis['statistical_tests']['throughput_difference']['p_value']:.6f}")

    # Generate plots
    print("\n" + "="*60)
    print("GENERATING PLOTS")
    print("="*60)
    simulator.plot_comparison(aggregated, analysis)

    # Save results
    simulator.save_results(aggregated, analysis)

    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)

    return aggregated, analysis


if __name__ == '__main__':
    aggregated, analysis = main()
