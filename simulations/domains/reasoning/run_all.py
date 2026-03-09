"""
POLLN Reasoning Domain - Master Orchestrator

Runs all reasoning simulations and generates the optimized system.
This is the main entry point for reasoning domain optimization.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import time


class ReasoningSimulationOrchestrator:
    """
    Orchestrates all reasoning domain simulations and compiles results.
    """

    def __init__(self):
        self.simulations = [
            ('dialogue_simulation.py', 'Dialogue Management'),
            ('chain_of_thought.py', 'Chain-of-Thought Reasoning'),
            ('context_tracking.py', 'Context Tracking'),
            ('reasoning_depth.py', 'Reasoning Depth'),
            ('consistency_checker.py', 'Consistency Validation')
        ]
        self.results_dir = Path('simulations/domains/reasoning')
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_all_simulations(self, skip_existing: bool = False):
        """Run all reasoning simulations"""
        print("=" * 80)
        print("POLLN Reasoning Domain - Complete Simulation Suite")
        print("=" * 80)
        print()

        start_time = time.time()

        for i, (script_name, description) in enumerate(self.simulations, 1):
            print(f"\n[{i}/{len(self.simulations)}] Running: {description}")
            print("-" * 80)

            script_path = self.results_dir / script_name

            if skip_existing and self._result_file_exists(script_name):
                print(f"  Skipping {script_name} (results already exist)")
                continue

            try:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes per simulation
                )

                if result.returncode == 0:
                    print(f"  ✓ {description} completed successfully")
                    # Print key output
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if 'Results saved to' in line or 'score' in line.lower():
                            print(f"    {line.strip()}")
                else:
                    print(f"  ✗ {description} failed")
                    print(f"    Error: {result.stderr[-200:]}")

            except subprocess.TimeoutExpired:
                print(f"  ✗ {description} timed out")
            except Exception as e:
                print(f"  ✗ {description} error: {str(e)}")

        elapsed = time.time() - start_time

        print("\n" + "=" * 80)
        print(f"All simulations completed in {elapsed:.1f} seconds")
        print("=" * 80)

    def _result_file_exists(self, script_name: str) -> bool:
        """Check if result file for script already exists"""
        base_name = script_name.replace('.py', '')
        result_files = [
            self.results_dir / f'{base_name}_results.json',
            self.results_dir / f'{base_name}.json'
        ]
        return any(f.exists() for f in result_files)

    def compile_results(self):
        """Compile all simulation results"""
        print("\n" + "=" * 80)
        print("Compiling Simulation Results")
        print("=" * 80)

        # Import and run optimizer
        try:
            from reasoning_optimizer import ReasoningOptimizer

            optimizer = ReasoningOptimizer()
            optimizer.load_all_results()
            optimizer.compile_optimal_config()
            optimizer.generate_typescript_config()

            print("\n✓ Configuration compiled successfully")

            # Generate summary
            summary = optimizer.generate_summary_report()
            print("\n" + summary)

            return optimizer.optimal_config

        except ImportError as e:
            print(f"\n✗ Failed to import optimizer: {e}")
            print("  Run reasoning_optimizer.py manually")
            return None
        except Exception as e:
            print(f"\n✗ Failed to compile results: {e}")
            return None

    def validate_results(self) -> bool:
        """Validate that all expected results exist"""
        print("\n" + "=" * 80)
        print("Validating Results")
        print("=" * 80)

        expected_files = [
            'dialogue_results.json',
            'cot_results.json',
            'context_tracking_results.json',
            'depth_results.json',
            'consistency_results.json'
        ]

        all_valid = True

        for filename in expected_files:
            filepath = self.results_dir / filename
            if filepath.exists():
                # Try to load and validate JSON
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    print(f"  ✓ {filename}: Valid JSON ({len(data)} keys)")
                except Exception as e:
                    print(f"  ✗ {filename}: Invalid JSON - {e}")
                    all_valid = False
            else:
                print(f"  ✗ {filename}: Not found")
                all_valid = False

        # Check for generated config
        config_path = Path('src/domains/reasoning/config.ts')
        if config_path.exists():
            print(f"  ✓ config.ts: Generated successfully")
        else:
            print(f"  ✗ config.ts: Not found")
            all_valid = False

        return all_valid

    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 80)
        print("Generating Comprehensive Report")
        print("=" * 80)

        report_lines = []
        report_lines.append("# POLLN Reasoning Domain - Optimization Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Overview
        report_lines.append("## Overview")
        report_lines.append("")
        report_lines.append("This report summarizes the optimization of POLLN agents for dialogue")
        report_lines.append("and multi-step reasoning tasks. Simulations covered:")
        report_lines.append("")
        for _, description in self.simulations:
            report_lines.append(f"- {description}")
        report_lines.append("")

        # Key Findings
        report_lines.append("## Key Findings")
        report_lines.append("")

        # Load results for summary
        findings = self._compile_key_findings()
        for finding in findings:
            report_lines.append(f"- {finding}")

        report_lines.append("")

        # Configuration
        report_lines.append("## Optimal Configuration")
        report_lines.append("")

        config_path = self.results_dir / 'full_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Dialogue
            report_lines.append("### Dialogue Management")
            dialogue = config.get('dialogue', {})
            report_lines.append(f"- Max Turns: {dialogue.get('maxTurns', 'N/A')}")
            report_lines.append(f"- Summarization: Every {dialogue.get('summarizationThreshold', 'N/A')} turns")
            report_lines.append(f"- Entity Tracking: {dialogue.get('entityTracking', 'N/A')}")
            report_lines.append("")

            # Reasoning
            report_lines.append("### Chain-of-Thought Reasoning")
            cot = config.get('chainOfThought', {})
            report_lines.append(f"- Self-Consistency Samples: {cot.get('selfConsistency', {}).get('samples', 'N/A')}")
            report_lines.append(f"- Verifier: {cot.get('verifier', {}).get('enabled', 'N/A')}")
            report_lines.append(f"- Max Steps: {cot.get('maxSteps', 'N/A')}")
            report_lines.append("")

            # Context
            report_lines.append("### Context Management")
            context = config.get('context', {})
            report_lines.append(f"- Compression: {context.get('compression', {}).get('strategy', 'N/A')}")
            report_lines.append(f"- KV-Cache: {context.get('kvCache', {}).get('enabled', 'N/A')}")
            report_lines.append("")

            # Depth
            report_lines.append("### Reasoning Depth")
            depth = config.get('depth', {})
            for mode in ['shallow', 'medium', 'deep']:
                mode_config = depth.get(mode, {})
                report_lines.append(f"- {mode.capitalize()}: {mode_config.get('maxSteps', 'N/A')} steps, "
                                 f"{mode_config.get('breadth', 'N/A')} breadth")
            report_lines.append("")

        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        report_lines.append("")

        # Next Steps
        report_lines.append("## Next Steps")
        report_lines.append("")
        report_lines.append("1. Import the generated configuration into POLLN core")
        report_lines.append("2. Test reasoning-optimized agents on validation tasks")
        report_lines.append.append("3. Benchmark against baseline (non-optimized) agents")
        report_lines.append("4. Iterate based on real-world performance")
        report_lines.append("")

        # Write report
        report_path = self.results_dir / 'COMPREHENSIVE_REPORT.md'
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"\n✓ Report generated: {report_path}")
        print(f"\nReport Preview:")
        print("-" * 80)
        print('\n'.join(report_lines[:30]))
        print("-" * 80)
        print(f"\n(Full report: {report_path})")

    def _compile_key_findings(self) -> List[str]:
        """Compile key findings from simulations"""
        findings = []

        # Check for results and extract key metrics
        results_files = {
            'dialogue': 'dialogue_results.json',
            'cot': 'cot_results.json',
            'context': 'context_tracking_results.json',
            'depth': 'depth_results.json',
            'consistency': 'consistency_results.json'
        }

        for key, filename in results_files.items():
            filepath = self.results_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    # Extract key metrics based on simulation type
                    if key == 'dialogue':
                        optimal = data.get('optimal_config', {})
                        findings.append(f"**Dialogue**: Optimal agent count = {optimal.get('num_agents', 'N/A')}, "
                                      f"summarization threshold = {optimal.get('summarization_threshold', 'N/A')}")

                    elif key == 'cot':
                        metrics = data.get('metrics', {})
                        findings.append(f"**Chain-of-Thought**: Accuracy = {metrics.get('accuracy', 0):.3f}, "
                                      f"consensus rate = {metrics.get('consensus_rate', 0):.3f}")

                    elif key == 'context':
                        optimal = data.get('optimal_config', {})
                        strategy = optimal.get('compression', {}).get('strategy', 'N/A')
                        findings.append(f"**Context Tracking**: Best compression strategy = {strategy}")

                    elif key == 'depth':
                        optimal = data.get('optimal_config', {})
                        strategy = optimal.get('exploration_strategy', {}).get('default', 'N/A')
                        findings.append(f"**Reasoning Depth**: Optimal exploration = {strategy}")

                    elif key == 'consistency':
                        metrics = data.get('metrics', {})
                        findings.append(f"**Consistency**: Violation rate = {metrics.get('violation_rate', 0):.3f}, "
                                      f"average score = {metrics.get('average_score', 0):.3f}")

                except Exception as e:
                    findings.append(f"**{key.capitalize()}**: Unable to extract findings ({e})")

        if not findings:
            findings.append("Run simulations first to generate findings")

        return findings

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = [
            "Implement adaptive depth selection based on task complexity estimation",
            "Use tree-of-thoughts exploration for complex reasoning tasks",
            "Enable self-consistency sampling (n=5) for all chain-of-thought reasoning",
            "Apply hybrid compression (summarization + recent turns) for dialogue context",
            "Enable KV-cache with attention-based eviction for long conversations",
            "Run consistency validation on all multi-turn dialogue responses",
            "Use iterative refinement for tasks requiring precision",
            "Enable debate-based reasoning for problems with multiple valid approaches"
        ]

        return recommendations


def main():
    """Main orchestrator workflow"""
    print("\n" + "=" * 80)
    print("POLLN REASONING DOMAIN - MASTER ORCHESTRATOR")
    print("=" * 80)
    print("\nThis orchestrator will:")
    print("1. Run all reasoning simulations")
    print("2. Compile optimal configuration")
    print("3. Validate results")
    print("4. Generate comprehensive report")
    print("=" * 80)

    orchestrator = ReasoningSimulationOrchestrator()

    # Step 1: Run all simulations
    print("\nStep 1: Running all simulations...")
    print("-" * 80)
    orchestrator.run_all_simulations(skip_existing=False)

    # Step 2: Compile results
    print("\nStep 2: Compiling results...")
    print("-" * 80)
    config = orchestrator.compile_results()

    # Step 3: Validate
    print("\nStep 3: Validating results...")
    print("-" * 80)
    is_valid = orchestrator.validate_results()

    # Step 4: Generate report
    print("\nStep 4: Generating report...")
    print("-" * 80)
    orchestrator.generate_report()

    # Final summary
    print("\n" + "=" * 80)
    print("ORCHESTRATION COMPLETE")
    print("=" * 80)

    if is_valid and config:
        print("\n✓ All simulations completed successfully")
        print("✓ Configuration generated: src/domains/reasoning/config.ts")
        print("✓ Results validated")
        print("\nReady to integrate reasoning-optimized POLLN agents!")
    else:
        print("\n⚠ Some simulations may have failed")
        print("  Review the output above for details")
        print("  You can re-run individual simulations if needed")

    print("\nGenerated files:")
    print("  - src/domains/reasoning/config.ts (TypeScript configuration)")
    print("  - simulations/domains/reasoning/full_config.json (Full configuration)")
    print("  - simulations/domains/reasoning/COMPREHENSIVE_REPORT.md (Report)")
    print("  - simulations/domains/reasoning/OPTIMIZATION_SUMMARY.md (Summary)")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
