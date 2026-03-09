"""
Master Orchestrator for Multiobjective Pareto Optimization

Runs all Pareto optimizations and generates unified recommendation system.
"""

import subprocess
import sys
from pathlib import Path
import json
import time
from typing import Dict, List


class MultiobjectiveOrchestrator:
    """Orchestrates all Pareto optimizations."""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.script_dir = self.base_dir
        self.output_dir = self.base_dir.parent.parent / 'outputs'
        self.config_dir = self.base_dir.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'

        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def run_script(self, script_name: str) -> bool:
        """Run a single optimization script."""
        script_path = self.script_dir / script_name
        print(f"\n{'=' * 70}")
        print(f"Running: {script_name}")
        print(f"{'=' * 70}")

        if not script_path.exists():
            print(f"Error: Script not found: {script_path}")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per script
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            if result.returncode != 0:
                print(f"Error: {script_name} failed with return code {result.returncode}")
                return False

            print(f"✓ Completed: {script_name}")
            return True

        except subprocess.TimeoutExpired:
            print(f"Error: {script_name} timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return False

    def run_all_optimizations(self) -> Dict[str, bool]:
        """Run all Pareto optimization scripts."""
        print("\n" + "=" * 70)
        print("MULTIOBJECTIVE PARETO OPTIMIZATION - ALL FRONTIERS")
        print("=" * 70)

        scripts = [
            'pareto_accuracy_cost.py',
            'pareto_speed_quality.py',
            'pareto_robustness_efficiency.py',
            'pareto_scalability_complexity.py'
        ]

        results = {}
        start_time = time.time()

        for script in scripts:
            results[script] = self.run_script(script)

        total_time = time.time() - start_time

        print("\n" + "=" * 70)
        print("OPTIMIZATION SUMMARY")
        print("=" * 70)

        for script, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{status}: {script}")

        print(f"\nTotal time: {total_time:.1f} seconds")

        return results

    def verify_outputs(self) -> Dict[str, bool]:
        """Verify all expected output files exist."""
        print("\n" + "=" * 70)
        print("VERIFYING OUTPUTS")
        print("=" * 70)

        expected_files = {
            'accuracy_cost': self.config_dir / 'accuracy_cost_tiers.json',
            'speed_quality': self.config_dir / 'speed_quality_tiers.json',
            'robustness_efficiency': self.config_dir / 'robustness_efficiency_tiers.json',
            'scalability_complexity': self.config_dir / 'scalability_complexity_tiers.json'
        }

        plots = {
            'accuracy_cost': self.output_dir / 'pareto_accuracy_cost.png',
            'speed_quality': self.output_dir / 'pareto_speed_quality.png',
            'robustness_efficiency': self.output_dir / 'pareto_robustness_efficiency.png',
            'scalability_complexity': self.output_dir / 'pareto_scalability_complexity.png'
        }

        verification = {}

        # Check config files
        print("\nConfig Files:")
        for name, path in expected_files.items():
            exists = path.exists()
            verification[f'config_{name}'] = exists
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {path}")

        # Check plot files
        print("\nPlot Files:")
        for name, path in plots.items():
            exists = path.exists()
            verification[f'plot_{name}'] = exists
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {path}")

        return verification

    def generate_unified_config(self) -> str:
        """Generate unified TypeScript configuration file."""
        print("\n" + "=" * 70)
        print("GENERATING UNIFIED TYPESCRIPT CONFIGURATION")
        print("=" * 70)

        # Load all tier configs
        all_configs = {}

        for category in ['accuracy_cost', 'speed_quality', 'robustness_efficiency', 'scalability_complexity']:
            config_file = self.config_dir / f'{category}_tiers.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    all_configs[category] = json.load(f)
                print(f"  ✓ Loaded {category}")
            else:
                print(f"  ✗ Missing {category}")
                all_configs[category] = {}

        # Generate TypeScript
        ts_content = self._generate_typescript_config(all_configs)

        # Save TypeScript file
        ts_output = self.config_dir.parent / 'index.ts'
        ts_output.parent.mkdir(parents=True, exist_ok=True)
        with open(ts_output, 'w') as f:
            f.write(ts_content)

        print(f"\n✓ Generated unified config: {ts_output}")

        return str(ts_output)

    def _generate_typescript_config(self, all_configs: Dict) -> str:
        """Generate TypeScript configuration content."""
        lines = []

        lines.append("/**")
        lines.append(" * POLLN Configuration Tiers")
        lines.append(" * ")
        lines.append(" * Auto-generated from Pareto-optimal configurations")
        lines.append(" * ")
        lines.append(" * Categories:")
        lines.append(" * - Accuracy vs Cost")
        lines.append(" * - Speed vs Quality")
        lines.append(" * - Robustness vs Efficiency")
        lines.append(" * - Scalability vs Complexity")
        lines.append(" */")
        lines.append("")
        lines.append("export interface PollnConfigTier {")
        lines.append("  model_size?: string;")
        lines.append("  checkpoint_frequency?: number;")
        lines.append("  cache_size?: string;")
        lines.append("  kv_cache_size?: string;")
        lines.append("  batch_size?: number;")
        lines.append("  compression_level?: number;")
        lines.append("  temperature?: number;")
        lines.append("  top_p?: number;")
        lines.append("  max_tokens?: number;")
        lines.append("  replication_factor?: number;")
        lines.append("  monitoring_level?: number;")
        lines.append("  colony_size?: number;")
        lines.append("  topology_depth?: number;")
        lines.append("  agent_types?: number;")
        lines.append("  decentralization_level?: number;")
        lines.append("  horizontal_scaling?: boolean;")
        lines.append("  auto_scaling?: boolean;")
        lines.append("  load_balancing_strategy?: string;")
        lines.append("  cache_sharding?: boolean;")
        lines.append("  federation_enabled?: boolean;")
        lines.append("  meta_tile_ratio?: number;")
        lines.append("  communication_pattern?: string;")
        lines.append("  use_speculative_decoding?: boolean;")
        lines.append("  use_quantization?: boolean;")
        lines.append("  use_federated?: boolean;")
        lines.append("  backup_enabled?: boolean;")
        lines.append("  use_quorum?: boolean;")
        lines.append("  disaster_recovery_enabled?: boolean;")
        lines.append("  retry_policy?: string;")
        lines.append("  max_retries?: number;")
        lines.append("  timeout_multiplier?: number;")
        lines.append("  checkpoint_interval_sec?: number;")
        lines.append("  health_check_interval_sec?: number;")
        lines.append("  circuit_breaker_threshold?: number;")
        lines.append("  backup_frequency_hours?: number;")
        lines.append("  expected_accuracy?: number;")
        lines.append("  expected_latency_ms?: number;")
        lines.append("  expected_availability?: string;")
        lines.append("  expected_throughput?: number;")
        lines.append("  expected_cost_multiplier?: number;")
        lines.append("  expected_complexity?: number;")
        lines.append("  target: string;")
        lines.append("}")
        lines.append("")
        lines.append("export const CONFIG_TIERS: Record<string, PollnConfigTier> = {")

        # Flatten all configs
        for category, configs in all_configs.items():
            for tier_name, config in configs.items():
                full_name = f"{category.upper()}_{tier_name}"
                lines.append(f"  {full_name}: {{")

                for key, value in config.items():
                    if isinstance(value, str):
                        lines.append(f"    {key}: '{value}',")
                    elif isinstance(value, bool):
                        lines.append(f"    {key}: {str(value).lower()},")
                    else:
                        lines.append(f"    {key}: {value},")

                lines.append("  },")
                lines.append("")

        lines.append("};")
        lines.append("")
        lines.append("export default CONFIG_TIERS;")

        return '\n'.join(lines)

    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report."""
        print("\n" + "=" * 70)
        print("GENERATING SUMMARY REPORT")
        print("=" * 70)

        report_lines = []
        report_lines.append("# POLLN Multiobjective Pareto Optimization Report\n")
        report_lines.append("*Auto-generated by run_all.py*\n\n")

        report_lines.append("## Overview\n")
        report_lines.append("This report summarizes Pareto-optimal configurations across four key tradeoffs:\n\n")
        report_lines.append("1. **Accuracy vs Cost** - Quality vs resource expenditure")
        report_lines.append("2. **Speed vs Quality** - Latency vs response quality")
        report_lines.append("3. **Robustness vs Efficiency** - Availability vs cost overhead")
        report_lines.append("4. **Scalability vs Complexity** - Throughput vs management overhead\n\n")

        # Load and summarize each frontier
        for category in ['accuracy_cost', 'speed_quality', 'robustness_efficiency', 'scalability_complexity']:
            config_file = self.config_dir / f'{category}_tiers.json'

            if not config_file.exists():
                continue

            with open(config_file, 'r') as f:
                configs = json.load(f)

            report_lines.append(f"## {category.replace('_', ' ').title()}\n\n")

            for tier_name, config in configs.items():
                report_lines.append(f"### {tier_name}\n\n")

                # Expected metrics
                report_lines.append("**Expected Metrics:**\n")
                for key in config.keys():
                    if key.startswith('expected_'):
                        report_lines.append(f"- {key}: {config[key]}\n")

                report_lines.append("\n**Configuration:**\n")
                for key, value in config.items():
                    if not key.startswith('expected_'):
                        report_lines.append(f"- {key}: {value}\n")

                report_lines.append("\n")

        # Save report
        report_path = self.output_dir / 'pareto_optimization_report.md'
        with open(report_path, 'w') as f:
            f.write(''.join(report_lines))

        print(f"✓ Generated summary report: {report_path}")

        return str(report_path)

    def run_full_pipeline(self) -> Dict[str, any]:
        """Run complete optimization pipeline."""
        print("\n" + "=" * 70)
        print("POLLN MULTIOBJECTIVE OPTIMIZATION PIPELINE")
        print("=" * 70)
        print(f"Base directory: {self.base_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Config directory: {self.config_dir}")

        results = {
            'optimizations': {},
            'verification': {},
            'outputs': {}
        }

        # Step 1: Run all optimizations
        results['optimizations'] = self.run_all_optimizations()

        # Step 2: Verify outputs
        results['verification'] = self.verify_outputs()

        # Step 3: Generate unified config
        try:
            results['outputs']['unified_config'] = self.generate_unified_config()
        except Exception as e:
            print(f"Error generating unified config: {e}")
            results['outputs']['unified_config'] = None

        # Step 4: Generate summary report
        try:
            results['outputs']['summary_report'] = self.generate_summary_report()
        except Exception as e:
            print(f"Error generating summary report: {e}")
            results['outputs']['summary_report'] = None

        # Step 5: Run recommendation engine report
        try:
            from recommendation_engine import generate_recommendation_report
            results['outputs']['recommendation_report'] = \
                self.output_dir / 'recommendation_report.md'
            generate_recommendation_report(str(self.output_dir))
        except Exception as e:
            print(f"Error generating recommendation report: {e}")
            results['outputs']['recommendation_report'] = None

        # Final summary
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)

        success_count = sum(1 for v in results['optimizations'].values() if v)
        total_count = len(results['optimizations'])

        print(f"\nOptimizations: {success_count}/{total_count} successful")

        if results['outputs']['unified_config']:
            print(f"✓ Unified config: {results['outputs']['unified_config']}")

        if results['outputs']['summary_report']:
            print(f"✓ Summary report: {results['outputs']['summary_report']}")

        if results['outputs']['recommendation_report']:
            print(f"✓ Recommendation report: {results['outputs']['recommendation_report']}")

        print("\nNext steps:")
        print("1. Review plots in outputs/ directory")
        print("2. Check generated configs in src/core/config/tiers/")
        print("3. Use recommendation_engine.py for scenario-based recommendations")
        print("4. Import CONFIG_TIERS in your TypeScript code")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run all Pareto optimizations')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing outputs')
    parser.add_argument('--unified-only', action='store_true',
                       help='Only generate unified config')
    parser.add_argument('--report-only', action='store_true',
                       help='Only generate summary report')

    args = parser.parse_args()

    orchestrator = MultiobjectiveOrchestrator()

    if args.verify_only:
        orchestrator.verify_outputs()
    elif args.unified_only:
        orchestrator.generate_unified_config()
    elif args.report_only:
        orchestrator.generate_summary_report()
    else:
        orchestrator.run_full_pipeline()


if __name__ == '__main__':
    main()
