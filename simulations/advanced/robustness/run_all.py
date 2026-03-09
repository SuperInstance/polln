"""
POLLN Robustness Testing Suite - Master Orchestrator
====================================================

This script orchestrates all robustness simulations and generates
a comprehensive security report with hardening configurations.

Usage:
    python run_all.py [--quick] [--generate-config]

Options:
    --quick: Run reduced simulations for faster testing
    --generate-config: Generate TypeScript hardening config after simulations

Simulations:
1. Prompt Injection Testing
2. Byzantine Fault Tolerance
3. Cascading Failure Simulation
4. State Corruption Recovery
5. Resource Exhaustion Testing

Output:
- Comprehensive security report
- Hardening configurations
- TypeScript security module
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class RobustnessOrchestrator:
    """
    Orchestrates all robustness simulations

    Features:
    - Runs all simulations in sequence
    - Collects metrics from each simulation
    - Generates comprehensive reports
    - Creates hardening configurations
    - Validates results
    """

    def __init__(self, results_dir: str = "simulations/advanced/robustness/results"):
        """
        Initialize the orchestrator

        Args:
            results_dir: Directory to store simulation results
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.simulation_results = {}
        self.start_time = None
        self.end_time = None

    def print_header(self, title: str) -> None:
        """Print a formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")

    def print_section(self, title: str) -> None:
        """Print a formatted section header"""
        print("\n" + "-"*70)
        print(f"  {title}")
        print("-"*70 + "\n")

    def run_prompt_injection_simulation(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run prompt injection simulation"""
        self.print_section("1. Prompt Injection Simulation")

        # Import here to avoid circular imports
        sys.path.insert(0, str(Path(__file__).parent))
        from prompt_injection import PromptInjectionSimulator

        simulator = PromptInjectionSimulator(seed=42)
        iterations = 5 if quick_mode else 10

        print(f"Running prompt injection simulation ({iterations} iterations)...")
        metrics = simulator.run_simulation(num_iterations=iterations)
        simulator.print_metrics()

        # Save results
        simulator.save_results(str(self.results_dir / "prompt_injection_results.json"))

        return {
            'metrics': {
                'total_attacks': metrics.total_attacks,
                'attacks_detected': metrics.attacks_detected,
                'attacks_blocked': metrics.attacks_blocked,
                'detection_rate': metrics.detection_rate,
                'block_rate': metrics.block_rate,
                'avg_response_time_ms': metrics.avg_response_time_ms,
            },
            'safety_config': simulator.generate_safety_config(),
        }

    def run_byzantine_simulation(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run Byzantine fault tolerance simulation"""
        self.print_section("2. Byzantine Fault Tolerance Simulation")

        from byzantine_agents import ByzantineSimulator, AggregationStrategy

        simulator = ByzantineSimulator(
            num_agents=100,
            malicious_fraction=0.2,
            aggregation_strategy=AggregationStrategy.TRIMMED_MEAN,
        )

        rounds = 30 if quick_mode else 50

        print(f"Running Byzantine simulation ({rounds} rounds)...")
        metrics = simulator.run_simulation(num_rounds=rounds)
        simulator.print_metrics()

        # Find resilience threshold
        threshold = simulator.find_resilience_threshold()

        # Save results
        simulator.save_results(str(self.results_dir / "byzantine_results.json"))

        return {
            'metrics': {
                'total_rounds': metrics.total_rounds,
                'avg_error': metrics.avg_error,
                'final_error': metrics.final_error,
                'malicious_detection_rate': metrics.malicious_detection_rate,
                'false_positive_rate': metrics.false_positive_rate,
                'resilience_threshold': threshold,
            },
            'byzantine_config': simulator.generate_byzantine_config(),
        }

    def run_cascade_failure_simulation(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run cascading failure simulation"""
        self.print_section("3. Cascading Failure Simulation")

        from cascade_failure import (
            CascadingFailureSimulator,
            ContainmentStrategy
        )

        simulator = CascadingFailureSimulator(
            num_agents=100,
            initial_failure_rate=0.05,
            containment_strategies=[
                ContainmentStrategy.CIRCUIT_BREAKER,
                ContainmentStrategy.RATE_LIMITING,
                ContainmentStrategy.BULKHEADING,
            ],
        )

        max_steps = 50 if quick_mode else 100

        print(f"Running cascade failure simulation ({max_steps} steps)...")
        metrics = simulator.run_simulation(max_steps=max_steps)
        simulator.print_metrics()

        # Save results
        simulator.save_results(str(self.results_dir / "cascade_failure_results.json"))

        return {
            'metrics': {
                'total_failures': metrics.total_failures,
                'cascade_depth': metrics.cascade_depth,
                'agents_affected': metrics.agents_affected,
                'containment_effectiveness': metrics.containment_effectiveness,
                'final_healthy_percentage': metrics.final_healthy_percentage,
            },
            'cascade_config': simulator.generate_cascade_config(),
        }

    def run_state_corruption_simulation(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run state corruption recovery simulation"""
        self.print_section("4. State Corruption Recovery Simulation")

        from state_corruption import (
            StateCorruptionSimulator,
            RecoveryStrategy
        )

        simulator = StateCorruptionSimulator(
            num_agents=50,
            checkpoint_frequency=10,
            corruption_fraction=0.2,
            recovery_strategies=[
                RecoveryStrategy.CHECKPOINT_ROLLBACK,
                RecoveryStrategy.PEER_VALIDATION,
                RecoveryStrategy.ANOMALY_DETECTION,
            ],
        )

        num_steps = 50 if quick_mode else 100

        print(f"Running state corruption simulation ({num_steps} steps)...")
        metrics = simulator.run_simulation(num_steps=num_steps)
        simulator.print_metrics()

        # Save results
        simulator.save_results(str(self.results_dir / "state_corruption_results.json"))

        return {
            'metrics': {
                'total_corruptions': metrics.total_corruptions,
                'detected_corruptions': metrics.detected_corruptions,
                'recovered_corruptions': metrics.recovered_corruptions,
                'detection_rate': metrics.detection_rate,
                'recovery_success_rate': metrics.recovery_success_rate,
                'avg_recovery_time_ms': metrics.avg_recovery_time_ms,
                'data_loss_percentage': metrics.data_loss_percentage,
            },
            'resilience_config': simulator.generate_resilience_config(),
        }

    def run_resource_exhaustion_simulation(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run resource exhaustion simulation"""
        self.print_section("5. Resource Exhaustion Simulation")

        from resource_exhaustion import (
            ResourceExhaustionSimulator,
            MitigationStrategy,
            DegradationPattern
        )

        simulator = ResourceExhaustionSimulator(
            num_agents=50,
            base_load=0.5,
            peak_load=1.5,
            degradation_pattern=DegradationPattern.LINEAR,
            mitigation_strategies=[
                MitigationStrategy.THROTTLING,
                MitigationStrategy.LOAD_SHEDDING,
                MitigationStrategy.CACHING,
                MitigationStrategy.QUEUE_MANAGEMENT,
            ],
        )

        num_steps = 50 if quick_mode else 100

        print(f"Running resource exhaustion simulation ({num_steps} steps)...")
        metrics = simulator.run_simulation(num_steps=num_steps, surge_at_step=20)
        simulator.print_metrics()

        # Save results
        simulator.save_results(str(self.results_dir / "resource_exhaustion_results.json"))

        return {
            'metrics': {
                'total_tasks': metrics.total_tasks,
                'completed_tasks': metrics.completed_tasks,
                'dropped_tasks': metrics.dropped_tasks,
                'task_completion_rate': metrics.task_completion_rate,
                'degradation_rate': metrics.degradation_rate,
                'system_stability_index': metrics.system_stability_index,
            },
            'resource_config': simulator.generate_resource_config(),
        }

    def run_all_simulations(self, quick_mode: bool = False) -> None:
        """Run all robustness simulations"""
        self.start_time = time.time()

        self.print_header("POLLN ROBUSTNESS TESTING SUITE")

        print(f"Mode: {'Quick (reduced iterations)' if quick_mode else 'Full (comprehensive)'}")
        print(f"Results directory: {self.results_dir}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Run all simulations
            self.simulation_results['prompt_injection'] = self.run_prompt_injection_simulation(quick_mode)
            self.simulation_results['byzantine'] = self.run_byzantine_simulation(quick_mode)
            self.simulation_results['cascade'] = self.run_cascade_failure_simulation(quick_mode)
            self.simulation_results['state'] = self.run_state_corruption_simulation(quick_mode)
            self.simulation_results['resource'] = self.run_resource_exhaustion_simulation(quick_mode)

        except Exception as e:
            print(f"\n[ERROR] Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        self.end_time = time.time()
        duration = self.end_time - self.start_time

        print("\n" + "="*70)
        print(f"  ALL SIMULATIONS COMPLETED")
        print("="*70)
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

    def generate_comprehensive_report(self) -> None:
        """Generate comprehensive security report"""
        self.print_header("GENERATING COMPREHENSIVE SECURITY REPORT")

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'duration_seconds': self.end_time - self.start_time,
                'total_simulations': len(self.simulation_results),
            },
            'simulations': self.simulation_results,
            'summary': self._generate_summary(),
            'recommendations': self._generate_recommendations(),
        }

        # Save comprehensive report
        report_path = self.results_dir / "comprehensive_security_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Comprehensive report saved: {report_path}")

        # Also save as markdown
        self._generate_markdown_report(report)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all simulation results"""
        summary = {
            'overall_health_score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'strengths': [],
        }

        # Calculate health scores for each simulation
        scores = []

        # Prompt injection health
        pi_results = self.simulation_results.get('prompt_injection', {}).get('metrics', {})
        if pi_results:
            detection_rate = pi_results.get('detection_rate', 0)
            block_rate = pi_results.get('block_rate', 0)
            pi_health = (detection_rate + block_rate) / 2
            scores.append(pi_health)

            if detection_rate < 0.9:
                summary['critical_issues'].append(
                    f"Prompt injection detection rate: {detection_rate:.1%}"
                )
            else:
                summary['strengths'].append(
                    f"Strong prompt injection detection: {detection_rate:.1%}"
                )

        # Byzantine tolerance health
        bz_results = self.simulation_results.get('byzantine', {}).get('metrics', {})
        if bz_results:
            resilience = bz_results.get('resilience_threshold', 0)
            bz_health = resilience / 0.33  # Normalize to expected 33%
            scores.append(min(bz_health, 1.0))

            if resilience < 0.2:
                summary['critical_issues'].append(
                    f"Low Byzantine resilience threshold: {resilience:.1%}"
                )
            else:
                summary['strengths'].append(
                    f"Good Byzantine resilience: {resilience:.1%} tolerance"
                )

        # Cascade prevention health
        cf_results = self.simulation_results.get('cascade', {}).get('metrics', {})
        if cf_results:
            effectiveness = cf_results.get('containment_effectiveness', 0)
            scores.append(effectiveness)

            if effectiveness < 0.7:
                summary['warnings'].append(
                    f"Cascade containment effectiveness: {effectiveness:.1%}"
                )
            else:
                summary['strengths'].append(
                    f"Strong cascade containment: {effectiveness:.1%}"
                )

        # State protection health
        st_results = self.simulation_results.get('state', {}).get('metrics', {})
        if st_results:
            detection_rate = st_results.get('detection_rate', 0)
            recovery_rate = st_results.get('recovery_success_rate', 0)
            st_health = (detection_rate + recovery_rate) / 2
            scores.append(st_health)

            if recovery_rate < 0.8:
                summary['warnings'].append(
                    f"State corruption recovery rate: {recovery_rate:.1%}"
                )
            else:
                summary['strengths'].append(
                    f"Good state recovery: {recovery_rate:.1%}"
                )

        # Resource management health
        re_results = self.simulation_results.get('resource', {}).get('metrics', {})
        if re_results:
            completion_rate = re_results.get('task_completion_rate', 0)
            stability = re_results.get('system_stability_index', 0)
            re_health = (completion_rate + stability) / 2
            scores.append(re_health)

            if completion_rate < 0.8:
                summary['warnings'].append(
                    f"Task completion under stress: {completion_rate:.1%}"
                )
            else:
                summary['strengths'].append(
                    f"Good resource management: {completion_rate:.1%} completion"
                )

        # Calculate overall health score
        if scores:
            summary['overall_health_score'] = sum(scores) / len(scores)

        return summary

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        summary = self._generate_summary()

        # Critical issues first
        if summary['critical_issues']:
            recommendations.append("## CRITICAL (Address Immediately)")
            for issue in summary['critical_issues']:
                recommendations.append(f"- {issue}")

        # Warnings
        if summary['warnings']:
            recommendations.append("\n## WARNING (Monitor and Address)")
            for warning in summary['warnings']:
                recommendations.append(f"- {warning}")

        # General recommendations
        recommendations.append("\n## GENERAL RECOMMENDATIONS")
        recommendations.extend([
            "- Implement all security hardening configurations",
            "- Regular security audits (quarterly recommended)",
            "- Monitor key metrics in production",
            "- Test disaster recovery procedures",
            "- Keep dependencies updated",
            "- Train operations team on security procedures",
        ])

        return recommendations

    def _generate_markdown_report(self, report: Dict) -> None:
        """Generate markdown version of the report"""
        md_path = self.results_dir / "comprehensive_security_report.md"

        summary = report['summary']
        recommendations = report['recommendations']

        markdown = f"""# POLLN Comprehensive Security Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {report['metadata']['duration_seconds']:.1f} seconds
**Simulations:** {report['metadata']['total_simulations']}

## Executive Summary

**Overall Health Score:** {summary['overall_health_score']:.1%}

### Status
- **Critical Issues:** {len(summary['critical_issues'])}
- **Warnings:** {len(summary['warnings'])}
- **Strengths:** {len(summary['strengths'])}

"""

        if summary['critical_issues']:
            markdown += "### Critical Issues\n\n"
            for issue in summary['critical_issues']:
                markdown += f"- **{issue}**\n"
            markdown += "\n"

        if summary['warnings']:
            markdown += "### Warnings\n\n"
            for warning in summary['warnings']:
                markdown += f"- {warning}\n"
            markdown += "\n"

        if summary['strengths']:
            markdown += "### Strengths\n\n"
            for strength in summary['strengths']:
                markdown += f"- {strength}\n"
            markdown += "\n"

        markdown += "## Recommendations\n\n"
        for rec in recommendations:
            markdown += f"{rec}\n"

        markdown += "\n## Simulation Results\n\n"

        # Add detailed results for each simulation
        for sim_name, sim_results in report['simulations'].items():
            markdown += f"### {sim_name.replace('_', ' ').title()}\n\n"

            metrics = sim_results.get('metrics', {})
            for key, value in metrics.items():
                if isinstance(value, float):
                    markdown += f"- **{key}:** {value:.4f}\n"
                else:
                    markdown += f"- **{key}:** {value}\n"
            markdown += "\n"

        markdown += f"""
## Next Steps

1. Review and address all critical issues
2. Implement hardening configurations
3. Schedule regular security audits
4. Monitor key metrics in production
5. Update configurations based on production data

## Support

For questions or issues, refer to:
- Security Guide: `docs/SECURITY_GUIDE.md`
- Architecture: `docs/ARCHITECTURE.md`
- Main README: `README.md`

---

*Report generated by POLLN Robustness Testing Suite*
"""

        with open(md_path, 'w') as f:
            f.write(markdown)

        print(f"Markdown report saved: {md_path}")

    def generate_typescript_config(self) -> None:
        """Generate TypeScript hardening configuration"""
        self.print_section("GENERATING TYPESCRIPT HARDENING CONFIG")

        from hardening_generator import HardeningGenerator

        generator = HardeningGenerator(str(self.results_dir))
        config = generator.generate_config()

        # Generate TypeScript module
        generator.generate_typescript_module('src/core/security/hardening.ts')

        # Generate security guide
        generator.generate_security_guide('docs/SECURITY_GUIDE.md')

        print("\nTypeScript hardening configuration generated successfully!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='POLLN Robustness Testing Suite - Master Orchestrator'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run reduced simulations for faster testing'
    )
    parser.add_argument(
        '--generate-config',
        action='store_true',
        help='Generate TypeScript hardening config after simulations'
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = RobustnessOrchestrator()

    # Run all simulations
    orchestrator.run_all_simulations(quick_mode=args.quick)

    # Generate comprehensive report
    orchestrator.generate_comprehensive_report()

    # Generate TypeScript config if requested
    if args.generate_config:
        orchestrator.generate_typescript_config()

    print("\n" + "="*70)
    print("  ROBUSTNESS TESTING COMPLETE")
    print("="*70)
    print("\nResults:")
    print(f"  - {orchestrator.results_dir}/comprehensive_security_report.json")
    print(f"  - {orchestrator.results_dir}/comprehensive_security_report.md")

    if args.generate_config:
        print("\nGenerated Configurations:")
        print("  - src/core/security/hardening.ts")
        print("  - docs/SECURITY_GUIDE.md")

    print("\nThank you for using POLLN Robustness Testing Suite!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
