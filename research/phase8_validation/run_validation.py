"""
Phase 8 Validation Execution Script

This script runs comprehensive validation of all Phase 6-7 discoveries
with detailed reporting and analysis.

Usage:
    python run_validation.py [options]

Options:
    --discoveries    Comma-separated list of discoveries to validate
    --trials         Number of trials per claim (default: 100)
    --confidence     Confidence level (default: 0.95)
    --correction     Multiple comparison correction: bonferroni|fdr (default: bonferroni)
    --seed           Random seed (default: 42)
    --output         Output directory (default: results/)
    --quick          Quick validation (20 trials, faster execution)
    --comprehensive  Comprehensive validation (200 trials, slower but thorough)
    --report-only    Generate reports from existing results (skip validation)
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

# Import validation framework
from experimental_validation import (
    ExperimentalValidator,
    ExperimentConfig,
    ValidationReport,
    validate_hybrid_simulations,
    validate_novel_algorithms,
    validate_hardware_models,
    validate_emergence_prediction,
    validate_gpu_optimizations
)

# Available discoveries
DISCOVERIES = {
    'hybrid': ('Hybrid Simulations', validate_hybrid_simulations),
    'algorithms': ('Novel Algorithms', validate_novel_algorithms),
    'hardware': ('Hardware Models', validate_hardware_models),
    'emergence': ('Emergence Prediction', validate_emergence_prediction),
    'gpu': ('GPU Optimizations', validate_gpu_optimizations),
    'all': ('All Discoveries', None)  # Special case
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Phase 8: Experimental Validation of Phases 6-7 Discoveries'
    )

    parser.add_argument(
        '--discoveries',
        type=str,
        default='all',
        help='Comma-separated list of discoveries to validate (hybrid,algorithms,hardware,emergence,gpu,all)'
    )

    parser.add_argument(
        '--trials',
        type=int,
        default=100,
        help='Number of trials per claim (default: 100)'
    )

    parser.add_argument(
        '--confidence',
        type=float,
        default=0.95,
        help='Confidence level for intervals (default: 0.95)'
    )

    parser.add_argument(
        '--correction',
        type=str,
        choices=['bonferroni', 'fdr'],
        default='bonferroni',
        help='Multiple comparison correction method (default: bonferroni)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory for reports (default: results/)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick validation (20 trials, faster execution)'
    )

    parser.add_argument(
        '--comprehensive',
        action='store_true',
        help='Comprehensive validation (200 trials, slower but thorough)'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate reports from existing results (skip validation)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    return parser.parse_args()

def setup_environment(args):
    """Setup validation environment."""
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure trials based on mode
    if args.quick:
        num_trials = 20
        print("Quick validation mode: 20 trials per claim")
    elif args.comprehensive:
        num_trials = 200
        print("Comprehensive validation mode: 200 trials per claim")
    else:
        num_trials = args.trials
        print(f"Standard validation mode: {num_trials} trials per claim")

    # Create validator configuration
    config = ExperimentConfig(
        num_trials=num_trials,
        confidence_level=args.confidence,
        multiple_comparison_correction=args.correction,
        random_seed=args.seed
    )

    return ExperimentalValidator(config), output_dir

def validate_discoveries(
    validator: ExperimentalValidator,
    discovery_names: List[str],
    verbose: bool = False
) -> List[ValidationReport]:
    """Validate specified discoveries."""
    reports = []

    print("\n" + "="*80)
    print("PHASE 8: EXPERIMENTAL VALIDATION OF PHASES 6-7 DISCOVERIES")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Trials per claim: {validator.config.num_trials}")
    print(f"  Confidence level: {validator.config.confidence_level}")
    print(f"  Multiple comparison correction: {validator.config.multiple_comparison_correction}")
    print(f"  Random seed: {validator.config.random_seed}")
    print(f"  Effect size threshold: {validator.config.effect_size_threshold}")

    # Resolve 'all' to all discoveries
    if 'all' in discovery_names:
        discovery_names = [k for k in DISCOVERIES.keys() if k != 'all']

    # Validate each discovery
    for i, name in enumerate(discovery_names, 1):
        if name not in DISCOVERIES:
            print(f"\nWarning: Unknown discovery '{name}', skipping...")
            continue

        description, validation_fn = DISCOVERIES[name]

        if validation_fn is None:  # 'all' case
            continue

        print(f"\n{'='*80}")
        print(f"[{i}/{len(discovery_names)}] Validating: {description}")
        print(f"{'='*80}")

        try:
            report = validation_fn(validator)
            reports.append(report)

            if verbose:
                print(f"\nDetailed Results:")
                for result in report.results:
                    status = "[OK] PASSED" if result.validated else "[FAIL] FAILED"
                    print(f"  {status}: {result.claim_id}")
                    print(f"    Mean: {result.mean:.4f} ± {result.std:.4f}")
                    print(f"    95% CI: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")

        except Exception as e:
            print(f"\n[FAIL] Error validating {name}: {e}")
            import traceback
            traceback.print_exc()

    return reports

def generate_summary(reports: List[ValidationReport]) -> str:
    """Generate comprehensive summary report."""
    if not reports:
        return "# No validation reports generated\n"

    md = []
    md.append("# Phase 8: Experimental Validation Summary\n")
    md.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    md.append(f"**Total Discoveries Validated:** {len(reports)}\n")

    # Overall statistics
    validated = sum(1 for r in reports if r.overall_validated)
    total_claims = sum(len(r.results) for r in reports)
    validated_claims = sum(sum(1 for res in r.results if res.validated) for r in reports)

    md.append("\n## Overall Results\n")
    md.append(f"| Metric | Value |\n")
    md.append(f"|--------|-------|\n")
    md.append(f"| Discoveries Validated | {validated}/{len(reports)} ({validated/len(reports)*100:.1f}%) |\n")
    md.append(f"| Claims Validated | {validated_claims}/{total_claims} ({validated_claims/total_claims*100:.1f}%) |\n")

    avg_power = sum(r.statistical_power for r in reports) / len(reports)
    avg_repro = sum(r.reproducibility_score for r in reports) / len(reports)

    md.append(f"| Average Statistical Power | {avg_power:.3f} |\n")
    md.append(f"| Average Reproducibility | {avg_repro:.3f} |\n")

    # Discovery-by-discovery summary
    md.append("\n## Discovery Details\n")

    for report in reports:
        status = "[OK] VALIDATED" if report.overall_validated else "[FAIL] FAILED"
        md.append(f"\n### {report.discovery_id}: {status}\n")
        md.append(f"{report.discovery_description}\n")
        md.append(f"- **Statistical Power:** {report.statistical_power:.3f}\n")
        md.append(f"- **Reproducibility:** {report.reproducibility_score:.3f}\n")
        md.append(f"- **Generation Time:** {report.generation_time:.2f}s\n")
        md.append(f"- **Claims:** {len(report.results)}\n")

        # Claim details
        md.append("\n**Claims:**\n")
        for result in report.results:
            claim_status = "[OK]" if result.validated else "[FAIL]"
            md.append(f"- {claim_status} **{result.claim_id}:** ")
            md.append(f"{result.mean:.4f} ± {result.std:.4f}, ")
            md.append(f"95% CI [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]\n")

    # Recommendations
    md.append("\n## Recommendations\n")
    all_recommendations = set()
    for report in reports:
        all_recommendations.update(report.recommendations)

    for i, rec in enumerate(sorted(all_recommendations), 1):
        md.append(f"{i}. {rec}\n")

    return "\n".join(md)

def save_reports(
    validator: ExperimentalValidator,
    reports: List[ValidationReport],
    output_dir: Path
):
    """Save all validation reports."""
    print(f"\n{'='*80}")
    print("Saving Reports")
    print(f"{'='*80}")

    # Save individual reports
    for report in reports:
        # JSON report
        json_path = output_dir / f"{report.discovery_id}_validation.json"
        validator.save_report(report, str(json_path))
        print(f"[OK] Saved JSON: {json_path}")

        # Markdown report
        md_path = output_dir / f"{report.discovery_id}_validation.md"
        md_content = validator.generate_markdown_report(report)
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"[OK] Saved Markdown: {md_path}")

    # Save summary
    summary_path = output_dir / "VALIDATION_SUMMARY.md"
    summary_content = generate_summary(reports)
    with open(summary_path, 'w') as f:
        f.write(summary_content)
    print(f"[OK] Saved Summary: {summary_path}")

    print(f"\nAll reports saved to: {output_dir.absolute()}")

def main():
    """Main execution."""
    args = parse_args()

    # Setup
    validator, output_dir = setup_environment(args)

    # Parse discoveries to validate
    discovery_names = [d.strip() for d in args.discoveries.split(',')]

    if not args.report_only:
        # Run validations
        reports = validate_discoveries(validator, discovery_names, args.verbose)

        # Save reports
        if reports:
            save_reports(validator, reports, output_dir)

            # Print summary
            print("\n" + "="*80)
            print("VALIDATION COMPLETE")
            print("="*80)

            validated = sum(1 for r in reports if r.overall_validated)
            print(f"\n[OK] Discoveries Validated: {validated}/{len(reports)}")
            print(f"[INFO] See {output_dir} for detailed reports\n")
        else:
            print("\n[FAIL] No validations completed. Check error messages above.\n")
    else:
        print("\nReport-only mode: skipping validation, generating reports from existing data...")
        print("Feature not yet implemented. Run without --report-only to perform validation.\n")

if __name__ == "__main__":
    main()
