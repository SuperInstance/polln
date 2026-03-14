#!/usr/bin/env python3
"""
Lucineer Simulation Validation Suite - Quick Start Script
Run complete validation suite with comprehensive reporting

Usage:
    python run_validations.py [--output-dir OUTPUT_DIR] [--verbose]

Author: Simulation & Validation Expert Team
Version: 1.0
Date: 2026-03-13
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core_simulators import (
    ValidationSuite,
    ChipConfig,
    EnergyEfficiencySimulator,
    ThroughputAnalyzer,
    PowerSimulator,
    GateCountAnalyzer,
)


def print_banner():
    """Print validation suite banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║         LUCINEER SIMULATION VALIDATION SUITE                      ║
║         Mask-Locked Inference Chip Validation                     ║
║                                                                   ║
║         Claims to Validate:                                       ║
║         • 50× Energy Efficiency                                   ║
║         • 80-150 tok/s Throughput                                 ║
║         • 2-3W Power Consumption                                  ║
║         • 95% Gate Reduction                                      ║
║         • 3.2× Thermal Isolation                                  ║
║         • 8.2× IR Drop Isolation                                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run Lucineer Simulation Validation Suite'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='validation_results',
        help='Output directory for results (default: validation_results)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file (JSON)'
    )
    parser.add_argument(
        '--tests',
        type=str,
        nargs='+',
        choices=['energy', 'throughput', 'power', 'gates', 'all'],
        default=['all'],
        help='Specific tests to run (default: all)'
    )

    return parser.parse_args()


def load_config(config_path: str = None) -> ChipConfig:
    """Load configuration from file or use defaults"""
    if config_path:
        import json
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return ChipConfig(**config_dict)
    else:
        return ChipConfig()


def run_specific_tests(test_names: list, config: ChipConfig, verbose: bool = False):
    """Run specific validation tests"""
    results = {}

    if 'all' in test_names or 'energy' in test_names:
        print("\n" + "="*70)
        print("ENERGY EFFICIENCY VALIDATION")
        print("="*70)
        energy_sim = EnergyEfficiencySimulator(config)
        results['energy_efficiency'] = energy_sim.validate_50x_efficiency_claim()
        print(f"Result: {'✓ PASSED' if results['energy_efficiency'].validated else '✗ FAILED'}")
        if verbose:
            print(f"Measured: {results['energy_efficiency'].measured_value:.6f} J/token")
            print(f"Target: {results['energy_efficiency'].target_value:.6f} J/token")

    if 'all' in test_names or 'throughput' in test_names:
        print("\n" + "="*70)
        print("THROUGHPUT VALIDATION")
        print("="*70)
        throughput_analyzer = ThroughputAnalyzer(config)
        results['throughput'] = throughput_analyzer.validate_throughput_claim()
        print(f"Result: {'✓ PASSED' if results['throughput'].validated else '✗ FAILED'}")
        if verbose:
            print(f"Measured: {results['throughput'].measured_value:.1f} tok/s")
            print(f"Target: 80-150 tok/s")

    if 'all' in test_names or 'power' in test_names:
        print("\n" + "="*70)
        print("POWER CONSUMPTION VALIDATION")
        print("="*70)
        power_sim = PowerSimulator(config)
        results['power'] = power_sim.validate_power_claim()
        print(f"Result: {'✓ PASSED' if results['power'].validated else '✗ FAILED'}")
        if verbose:
            print(f"Measured: {results['power'].measured_value:.2f} W")
            print(f"Target: 2-3 W")

    if 'all' in test_names or 'gates' in test_names:
        print("\n" + "="*70)
        print("GATE REDUCTION VALIDATION")
        print("="*70)
        gate_analyzer = GateCountAnalyzer()
        results['gate_reduction'] = gate_analyzer.validate_gate_reduction_claim()
        print(f"Result: {'✓ PASSED' if results['gate_reduction'].validated else '✗ FAILED'}")
        if verbose:
            print(f"Measured: {results['gate_reduction'].measured_value*100:.1f}% reduction")
            print(f"Target: 95% reduction")

    return results


def print_summary(results: dict):
    """Print validation summary"""
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r.validated)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    for name, result in results.items():
        status = "✓ PASSED" if result.validated else "✗ FAILED"
        print(f"{name:20s}: {status}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print(f"Pass Rate: {pass_rate:.1f}%")

    if pass_rate == 100:
        print("\n🎉 All tests PASSED!")
    elif pass_rate >= 50:
        print("\n⚠️  Some tests failed - review results")
    else:
        print("\n❌ Multiple tests failed - critical issues detected")

    print("="*70)


def save_results(results: dict, output_dir: str):
    """Save validation results to files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save JSON results
    import json
    json_path = output_path / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump({name: result.to_dict() for name, result in results.items()},
                 f, indent=2)
    print(f"\nJSON results saved to: {json_path}")

    # Save markdown report
    report_path = output_path / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w') as f:
        f.write(generate_markdown_report(results))
    print(f"Markdown report saved to: {report_path}")

    return json_path, report_path


def generate_markdown_report(results: dict) -> str:
    """Generate markdown report from results"""
    report = f"""# Lucineer Validation Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

"""

    passed = sum(1 for r in results.values() if r.validated)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    report += f"""- **Total Tests**: {total}
- **Passed**: {passed}
- **Failed**: {total - passed}
- **Pass Rate**: {pass_rate:.1f}%

## Detailed Results

"""

    for name, result in results.items():
        status = "✓ PASSED" if result.validated else "✗ FAILED"

        report += f"""
### {name.replace('_', ' ').title()}

**Status**: {status}
**Claim**: {result.claim_description}
**Target**: {result.target_value}
**Measured**: {result.measured_value:.6f}

"""

        if result.confidence_interval:
            ci_low, ci_high = result.confidence_interval
            report += f"**95% CI**: [{ci_low:.6f}, {ci_high:.6f}]\n"

        if result.additional_metrics:
            report += "\n**Additional Metrics**:\n"
            for key, value in result.additional_metrics.items():
                report += f"- {key}: {value}\n"

        if result.failure_reason:
            report += f"\n**Failure Reason**: {result.failure_reason}\n"

        report += "\n---\n"

    return report


def main():
    """Main entry point"""
    args = parse_arguments()

    print_banner()

    # Load configuration
    print(f"\n{'='*70}")
    print("INITIALIZATION")
    print(f"{'='*70}")
    config = load_config(args.config)
    print(f"Technology Node: {config.technology_node}")
    print(f"Die Area: {config.die_area_mm2} mm²")
    print(f"Frequency: {config.frequency_max/1e9} GHz")
    print(f"Voltage: {config.voltage_nominal} V")

    # Run tests
    print(f"\n{'='*70}")
    print("RUNNING VALIDATIONS")
    print(f"{'='*70}")

    results = run_specific_tests(args.tests, config, args.verbose)

    # Print summary
    print_summary(results)

    # Save results
    json_path, report_path = save_results(results, args.output_dir)

    # Exit with appropriate code
    passed = sum(1 for r in results.values() if r.validated)
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
