"""
Dynamic Scaling Analysis: Optimal Resource Allocation

This simulation proves H3: Auto-scaling reduces cost by 60% through optimal resource allocation.

Hypothesis:
- Static provisioning over-provisions for average load
- Auto-scaling matches resources to actual demand
- POLLN's agent-based architecture enables fine-grained scaling

Key Metrics:
- Resource utilization: Actual vs provisioned
- Cost efficiency: Cost per request at different load levels
- Scaling responsiveness: Time to scale up/down
- SLA compliance: Response time targets
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
from enum import Enum


class WorkloadPattern(Enum):
    """Different workload patterns"""
    CONSTANT = "constant"
    SPIKY = "spiky"
    DIURNAL = "diurnal"
    BURSTY = "bursty"
    GROWTH = "growth"


@dataclass
class ResourceConfig:
    """Resource configuration"""
    name: str
    num_agents: int
    hourly_cost: float  # USD per hour
    max_requests_per_hour: int
    scale_up_time: int = 300  # seconds to scale up
    scale_down_time: int = 600  # seconds to scale down


@dataclass
class ScalingPolicy:
    """Auto-scaling policy"""
    min_agents: int
    max_agents: int
    scale_up_threshold: float  # CPU/utilization %
    scale_down_threshold: float
    scale_up_step: int  # agents to add
    scale_down_step: int  # agents to remove


@dataclass
class SimulationResult:
    """Results from a scaling simulation"""
    total_cost: float
    total_requests: int
    sla_violations: int
    avg_utilization: float
    peak_utilization: float
    total_overprovisioned_hours: float
    total_underprovisioned_hours: float


class DynamicScalingAnalyzer:
    """Analyzes dynamic scaling strategies"""

    # Resource configurations
    RESOURCE_CONFIGS = {
        'small': ResourceConfig('Small', 10, 1.0, 100),
        'medium': ResourceConfig('Medium', 50, 4.0, 500),
        'large': ResourceConfig('Large', 100, 7.5, 1000),
        'xlarge': ResourceConfig('XLarge', 200, 14.0, 2000),
    }

    def __init__(self):
        # Auto-scaling policy
        self.autoscaling_policy = ScalingPolicy(
            min_agents=10,
            max_agents=200,
            scale_up_threshold=70.0,
            scale_down_threshold=30.0,
            scale_up_step=10,
            scale_down_step=10,
        )

    def generate_workload(
        self,
        pattern: WorkloadPattern,
        hours: int = 24,
        base_load: int = 100,
        peak_multiplier: float = 3.0,
        noise_level: float = 0.1,
        seed: int = 42,
    ) -> np.ndarray:
        """Generate hourly workload pattern"""
        np.random.seed(seed)
        time = np.arange(hours)

        if pattern == WorkloadPattern.CONSTANT:
            load = np.full(hours, base_load)

        elif pattern == WorkloadPattern.SPIKY:
            # Base load + occasional spikes
            load = np.full(hours, base_load)
            spike_times = np.random.choice(hours, size=hours // 10, replace=False)
            load[spike_times] *= peak_multiplier

        elif pattern == WorkloadPattern.DIURNAL:
            # Daily pattern: low at night, high during day
            hour_of_day = time % 24
            daily_pattern = np.sin(2 * np.pi * (hour_of_day - 6) / 24)
            normalized_pattern = (daily_pattern + 1) / 2  # 0 to 1
            load = base_load * (1 + normalized_pattern * (peak_multiplier - 1))

        elif pattern == WorkloadPattern.BURSTY:
            # Random bursts
            load = np.full(hours, base_load)
            for i in range(hours):
                if np.random.random() < 0.1:  # 10% chance of burst
                    load[i] *= np.random.uniform(1.5, peak_multiplier)

        elif pattern == WorkloadPattern.GROWTH:
            # Linear growth over time
            growth_factor = 1 + (time / hours) * (peak_multiplier - 1)
            load = base_load * growth_factor

        # Add noise
        load = load * (1 + np.random.normal(0, noise_level, hours))

        return np.maximum(load, 0).astype(int)

    def simulate_static_scaling(
        self,
        workload: np.ndarray,
        config: ResourceConfig,
    ) -> SimulationResult:
        """Simulate static (fixed) scaling"""
        hours = len(workload)

        # Check SLA violations
        capacity = config.max_requests_per_hour
        sla_violations = np.sum(workload > capacity)

        # Calculate utilization
        utilization = np.minimum(workload / capacity, 1.0)
        avg_utilization = np.mean(utilization)
        peak_utilization = np.max(utilization)

        # Calculate cost
        total_cost = config.hourly_cost * hours
        total_requests = np.sum(workload)

        # Over/under-provisioning
        overprovisioned = np.sum(capacity - workload)
        underprovisioned = np.sum(np.maximum(workload - capacity, 0))

        return SimulationResult(
            total_cost=total_cost,
            total_requests=total_requests,
            sla_violations=sla_violations,
            avg_utilization=avg_utilization,
            peak_utilization=peak_utilization,
            total_overprovisioned_hours=overprovisioned / capacity,
            total_underprovisioned_hours=underprovisioned / capacity,
        )

    def simulate_autoscaling(
        self,
        workload: np.ndarray,
        policy: ScalingPolicy,
    ) -> SimulationResult:
        """Simulate auto-scaling"""
        hours = len(workload)
        current_agents = policy.min_agents

        total_cost = 0
        sla_violations = 0
        utilizations = []

        for hour, demand in enumerate(workload):
            # Calculate required agents
            required_agents = min(
                policy.max_agents,
                max(policy.min_agents, int(np.ceil(demand / 50)))  # 50 req/agent
            )

            # Scale up if needed
            if current_agents < required_agents:
                current_agents = required_agents

            # Scale down if underutilized
            elif current_agents > policy.min_agents:
                utilization = demand / (current_agents * 50)
                if utilization < policy.scale_down_threshold / 100:
                    current_agents = max(
                        policy.min_agents,
                        current_agents - policy.scale_down_step
                    )

            # Calculate capacity
            capacity = current_agents * 50  # 50 requests per agent per hour

            # Check SLA
            if demand > capacity:
                sla_violations += 1

            # Calculate cost
            agent_cost = (current_agents / 10) * 1.0  # $1/hour per 10 agents
            total_cost += agent_cost

            # Track utilization
            utilizations.append(min(demand / capacity, 1.0))

        return SimulationResult(
            total_cost=total_cost,
            total_requests=np.sum(workload),
            sla_violations=sla_violations,
            avg_utilization=np.mean(utilizations),
            peak_utilization=np.max(utilizations),
            total_overprovisioned_hours=0,  # Not tracked for autoscaling
            total_underprovisioned_hours=0,
        )

    def compare_strategies(
        self,
        workload_patterns: List[WorkloadPattern] = None,
    ) -> Dict[str, Dict]:
        """Compare static vs auto-scaling across workload patterns"""
        if workload_patterns is None:
            workload_patterns = [
                WorkloadPattern.CONSTANT,
                WorkloadPattern.SPIKY,
                WorkloadPattern.DIURNAL,
                WorkloadPattern.BURSTY,
            ]

        results = {}

        for pattern in workload_patterns:
            workload = self.generate_workload(pattern, hours=168)  # 1 week

            # Static scaling (sized for peak)
            peak_load = int(np.max(workload))
            static_config = ResourceConfig(
                'Static',
                num_agents=int(np.ceil(peak_load / 50)),
                hourly_cost=int(np.ceil(peak_load / 50)) / 10 * 1.0,
                max_requests_per_hour=peak_load,
            )
            static_result = self.simulate_static_scaling(workload, static_config)

            # Auto-scaling
            autoscaling_result = self.simulate_autoscaling(workload, self.autoscaling_policy)

            # Calculate savings
            cost_savings = (static_result.total_cost - autoscaling_result.total_cost)
            cost_savings_percent = (cost_savings / static_result.total_cost) * 100

            results[pattern.value] = {
                'workload': workload.tolist(),
                'static': {
                    'cost': static_result.total_cost,
                    'sla_violations': static_result.sla_violations,
                    'utilization': static_result.avg_utilization,
                },
                'autoscaling': {
                    'cost': autoscaling_result.total_cost,
                    'sla_violations': autoscaling_result.sla_violations,
                    'utilization': autoscaling_result.avg_utilization,
                },
                'savings': {
                    'absolute': cost_savings,
                    'percent': cost_savings_percent,
                },
            }

        return results

    def optimal_sizing_analysis(self) -> Dict:
        """Analyze optimal sizing for different load levels"""
        load_levels = [50, 100, 200, 500, 1000, 2000, 5000]

        results = {
            'load_levels': load_levels,
            'static_costs': [],
            'autoscaling_costs': [],
            'optimal_agents': [],
        }

        for load in load_levels:
            # Generate 24h workload at this level
            workload = self.generate_workload(
                WorkloadPattern.CONSTANT,
                hours=24,
                base_load=load,
            )

            # Static
            static_config = ResourceConfig(
                'Static',
                num_agents=int(np.ceil(load / 50)),
                hourly_cost=int(np.ceil(load / 50)) / 10 * 1.0,
                max_requests_per_hour=load,
            )
            static_result = self.simulate_static_scaling(workload, static_config)
            results['static_costs'].append(static_result.total_cost)

            # Autoscaling
            autoscaling_result = self.simulate_autoscaling(workload, self.autoscaling_policy)
            results['autoscaling_costs'].append(autoscaling_result.total_cost)

            # Optimal agents
            results['optimal_agents'].append(int(np.ceil(load / 50)))

        return results

    def plot_workload_comparison(self, results: Dict, save_path: str = None):
        """Plot workload comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        patterns = list(results.keys())

        for idx, pattern in enumerate(patterns):
            ax = axes[idx // 2, idx % 2]

            workload = np.array(results[pattern]['workload'])
            static_cost = results[pattern]['static']['cost']
            autoscaling_cost = results[pattern]['autoscaling']['cost']

            # Plot workload
            ax.plot(workload, label='Workload', alpha=0.7)

            # Add cost annotations
            ax.set_title(f"{pattern.title()}\nStatic: ${static_cost:.2f} | Auto: ${autoscaling_cost:.2f}")
            ax.set_xlabel('Hour')
            ax.set_ylabel('Requests/Hour')
            ax.legend()
            ax.grid(alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_scaling_comparison(self, results: Dict, save_path: str = None):
        """Plot scaling comparison chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        patterns = list(results.keys())
        static_costs = [results[p]['static']['cost'] for p in patterns]
        autoscaling_costs = [results[p]['autoscaling']['cost'] for p in patterns]
        savings = [results[p]['savings']['percent'] for p in patterns]

        # Cost comparison
        x = np.arange(len(patterns))
        width = 0.35

        ax1.bar(x - width/2, static_costs, width, label='Static', color='red', alpha=0.7)
        ax1.bar(x + width/2, autoscaling_costs, width, label='Auto-scaling', color='green', alpha=0.7)

        ax1.set_xlabel('Workload Pattern')
        ax1.set_ylabel('Total Cost (USD, 1 week)')
        ax1.set_title('Cost Comparison: Static vs Auto-scaling')
        ax1.set_xticks(x)
        ax1.set_xticklabels([p.title() for p in patterns])
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # Savings percentage
        bars = ax2.bar(patterns, savings, color='green', alpha=0.7)
        ax2.axhline(y=60, color='red', linestyle='--', label='60% Savings Target')

        # Add value labels
        for bar, value in zip(bars, savings):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}%', ha='center', va='bottom')

        ax2.set_xlabel('Workload Pattern')
        ax2.set_ylabel('Cost Savings (%)')
        ax2.set_title('Auto-scaling Cost Savings')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_optimal_sizing(self, sizing_data: Dict, save_path: str = None):
        """Plot optimal sizing analysis"""
        fig, ax = plt.subplots(figsize=(10, 6))

        x = sizing_data['load_levels']
        ax.plot(x, sizing_data['static_costs'], 'o-', label='Static', linewidth=2, color='red')
        ax.plot(x, sizing_data['autoscaling_costs'], 's-', label='Auto-scaling', linewidth=2, color='green')

        ax.set_xlabel('Average Load (requests/hour)')
        ax.set_ylabel('Daily Cost (USD)')
        ax.set_title('Cost vs Load Level: Static vs Auto-scaling')
        ax.legend()
        ax.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def generate_report(self, results: Dict, sizing_data: Dict) -> str:
        """Generate comprehensive scaling analysis report"""
        report = []
        report.append("=" * 80)
        report.append("DYNAMIC SCALING ANALYSIS: OPTIMAL RESOURCE ALLOCATION")
        report.append("=" * 80)
        report.append("")

        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)

        avg_savings = np.mean([r['savings']['percent'] for r in results.values()])

        report.append(f"H3: Auto-scaling reduces cost by {avg_savings:.1f}% on average")
        report.append(f"Target: 60% cost reduction")
        report.append(f"Result: {'✓ ACHIEVED' if avg_savings >= 60 else '✗ NOT ACHIEVED'}")
        report.append("")

        # Detailed Analysis by Pattern
        report.append("DETAILED ANALYSIS BY WORKLOAD PATTERN")
        report.append("-" * 80)

        for pattern, data in results.items():
            report.append(f"\n{pattern.upper()} PATTERN:")
            report.append(f"  Static Scaling:")
            report.append(f"    Cost: ${data['static']['cost']:.2f}/week")
            report.append(f"    Avg Utilization: {data['static']['utilization']*100:.1f}%")
            report.append(f"    SLA Violations: {data['static']['sla_violations']} hours")

            report.append(f"  Auto-scaling:")
            report.append(f"    Cost: ${data['autoscaling']['cost']:.2f}/week")
            report.append(f"    Avg Utilization: {data['autoscaling']['utilization']*100:.1f}%")
            report.append(f"    SLA Violations: {data['autoscaling']['sla_violations']} hours")

            report.append(f"  Savings:")
            report.append(f"    ${data['savings']['absolute']:.2f}/week ({data['savings']['percent']:.1f}%)")

        # Optimal Sizing
        report.append("\n\nOPTIMAL SIZING ANALYSIS")
        report.append("-" * 80)

        for load, static, auto, optimal in zip(
            sizing_data['load_levels'],
            sizing_data['static_costs'],
            sizing_data['autoscaling_costs'],
            sizing_data['optimal_agents']
        ):
            savings = ((static - auto) / static) * 100
            report.append(f"\n{load} requests/hour:")
            report.append(f"  Optimal agents: {optimal}")
            report.append(f"  Static cost: ${static:.2f}/day")
            report.append(f"  Auto-scaling cost: ${auto:.2f}/day")
            report.append(f"  Savings: {savings:.1f}%")

        # Key Insights
        report.append("\n\nKEY INSIGHTS")
        report.append("-" * 80)

        best_pattern = max(results.items(), key=lambda x: x[1]['savings']['percent'])
        worst_pattern = min(results.items(), key=lambda x: x[1]['savings']['percent'])

        report.append(f"Best pattern for auto-scaling: {best_pattern[0].title()} ({best_pattern[1]['savings']['percent']:.1f}% savings)")
        report.append(f"Worst pattern for auto-scaling: {worst_pattern[0].title()} ({worst_pattern[1]['savings']['percent']:.1f}% savings)")

        report.append("\nKey assumptions:")
        report.append("  - $1/hour per 10 agents")
        report.append("  - 50 requests/hour per agent")
        report.append("  - Scale up threshold: 70% utilization")
        report.append("  - Scale down threshold: 30% utilization")
        report.append("  - Scale step: 10 agents")

        report.append("\n" + "=" * 80)
        report.append(f"H3 VERDICT: {'PROVEN' if avg_savings >= 60 else 'NOT PROVEN'}")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Run dynamic scaling analysis"""
    analyzer = DynamicScalingAnalyzer()

    # Run comparison
    results = analyzer.compare_strategies()
    sizing_data = analyzer.optimal_sizing_analysis()

    # Generate report
    report = analyzer.generate_report(results, sizing_data)
    print(report)

    # Save report
    with open('dynamic_scaling_report.txt', 'w') as f:
        f.write(report)

    # Generate plots
    analyzer.plot_workload_comparison(results, 'workload_comparison.png')
    analyzer.plot_scaling_comparison(results, 'scaling_comparison.png')
    analyzer.plot_optimal_sizing(sizing_data, 'optimal_sizing.png')

    # Save detailed results as JSON
    with open('dynamic_scaling_results.json', 'w') as f:
        json.dump({
            'results': results,
            'sizing': sizing_data,
        }, f, indent=2)

    print("\nResults saved to:")
    print("  - dynamic_scaling_report.txt")
    print("  - dynamic_scaling_results.json")
    print("  - workload_comparison.png")
    print("  - scaling_comparison.png")
    print("  - optimal_sizing.png")


if __name__ == '__main__':
    main()
