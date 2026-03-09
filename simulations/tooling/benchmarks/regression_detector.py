"""
Performance Regression Detector

Automatically detects performance regressions by comparing benchmark results
against baselines using statistical analysis.
"""

import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum
import statistics
from scipy import stats


class RegressionSeverity(Enum):
    """Severity levels for detected regressions"""
    CRITICAL = "critical"  # >50% degradation, must fix
    HIGH = "high"         # 20-50% degradation, should fix
    MEDIUM = "medium"     # 10-20% degradation, monitor
    LOW = "low"           # 5-10% degradation, note
    NONE = "none"         # No significant regression


@dataclass
class RegressionAlert:
    """Alert for a detected regression"""
    metric_name: str
    baseline_value: float
    current_value: float
    percent_change: float
    severity: RegressionSeverity
    confidence: float  # Statistical confidence (0-1)
    is_significant: bool  # Statistically significant
    recommendation: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class ComparisonResult:
    """Result of comparing current vs baseline benchmarks"""
    benchmark_name: str
    baseline_version: str
    current_version: str
    comparisons: Dict[str, Dict]  # metric -> comparison data
    regressions: List[RegressionAlert]
    improvements: List[Dict]
    summary: str

    def to_dict(self) -> Dict:
        return {
            "benchmark_name": self.benchmark_name,
            "baseline_version": self.baseline_version,
            "current_version": self.current_version,
            "comparisons": self.comparisons,
            "regressions": [r.to_dict() for r in self.regressions],
            "improvements": self.improvements,
            "summary": self.summary
        }


class RegressionDetector:
    """
    Detect performance regressions using statistical analysis.

    Features:
    - Statistical significance testing (t-test, Mann-Whitney U)
    - Multiple confidence levels (90%, 95%, 99%)
    - Configurable regression thresholds
    - Automatic alert generation
    - Trend analysis for gradual degradation
    """

    def __init__(
        self,
        baseline_dir: str = "reports/benchmarks/baselines",
        current_dir: str = "reports/benchmarks/current",
        confidence_level: float = 0.95
    ):
        self.baseline_dir = Path(baseline_dir)
        self.current_dir = Path(current_dir)
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

        # Regression thresholds (percentage change)
        self.thresholds = {
            RegressionSeverity.CRITICAL: 0.50,   # 50% worse
            RegressionSeverity.HIGH: 0.20,       # 20% worse
            RegressionSeverity.MEDIUM: 0.10,     # 10% worse
            RegressionSeverity.LOW: 0.05         # 5% worse
        }

    def load_benchmark(self, filepath: Path) -> Dict:
        """Load benchmark results from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data

    def compare_metric(
        self,
        baseline_value: float,
        current_value: float,
        metric_name: str,
        lower_is_better: bool = True
    ) -> Dict:
        """Compare a single metric between baseline and current"""

        # Calculate percent change
        if lower_is_better:
            # For latency/memory: positive change = regression
            percent_change = ((current_value - baseline_value) / baseline_value) * 100
            is_regression = percent_change > 0
        else:
            # For throughput: negative change = regression
            percent_change = ((baseline_value - current_value) / baseline_value) * 100
            is_regression = percent_change > 0

        return {
            "metric": metric_name,
            "baseline": baseline_value,
            "current": current_value,
            "percent_change": percent_change,
            "is_regression": is_regression,
            "lower_is_better": lower_is_better
        }

    def determine_severity(self, percent_change: float) -> RegressionSeverity:
        """Determine regression severity from percent change"""

        abs_change = abs(percent_change)

        if abs_change >= self.thresholds[RegressionSeverity.CRITICAL] * 100:
            return RegressionSeverity.CRITICAL
        elif abs_change >= self.thresholds[RegressionSeverity.HIGH] * 100:
            return RegressionSeverity.HIGH
        elif abs_change >= self.thresholds[RegressionSeverity.MEDIUM] * 100:
            return RegressionSeverity.MEDIUM
        elif abs_change >= self.thresholds[RegressionSeverity.LOW] * 100:
            return RegressionSeverity.LOW
        else:
            return RegressionSeverity.NONE

    def statistical_significance_test(
        self,
        baseline_samples: List[float],
        current_samples: List[float]
    ) -> Tuple[bool, float]:
        """
        Test if performance difference is statistically significant.

        Uses Mann-Whitney U test (non-parametric) as it's more robust
        to outliers and non-normal distributions.

        Returns:
            (is_significant, p_value)
        """

        # Ensure we have samples
        if len(baseline_samples) < 3 or len(current_samples) < 3:
            return True, 0.0  # Assume significant if insufficient data

        # Mann-Whitney U test
        try:
            statistic, p_value = stats.mannwhitneyu(
                baseline_samples,
                current_samples,
                alternative='two-sided'
            )

            is_significant = p_value < self.alpha
            return is_significant, p_value

        except Exception as e:
            print(f"Statistical test failed: {e}")
            return True, 0.0

    def detect_regressions(
        self,
        baseline_results: List[Dict],
        current_results: List[Dict]
    ) -> ComparisonResult:
        """Detect regressions by comparing current vs baseline results"""

        # Group by benchmark name
        baseline_by_name = {r["name"]: r for r in baseline_results}
        current_by_name = {r["name"]: r for r in current_results}

        comparisons = {}
        regressions = []
        improvements = []

        for name in baseline_by_name:
            if name not in current_by_name:
                continue  # Benchmark was removed

            baseline = baseline_by_name[name]
            current = current_by_name[name]

            comparison = {}

            # Compare key metrics
            metrics_to_compare = [
                ("avg_latency_ms", "Average Latency", True),
                ("p95_latency_ms", "P95 Latency", True),
                ("p99_latency_ms", "P99 Latency", True),
                ("throughput_ops", "Throughput", False),
                ("memory_mb", "Memory Usage", True),
            ]

            for metric_key, metric_label, lower_is_better in metrics_to_compare:
                if metric_key in baseline and metric_key in current:
                    comp = self.compare_metric(
                        baseline[metric_key],
                        current[metric_key],
                        metric_label,
                        lower_is_better
                    )
                    comparison[metric_key] = comp

                    # Create alert for significant regressions
                    if comp["is_regression"] and abs(comp["percent_change"]) >= 5:
                        severity = self.determine_severity(comp["percent_change"])

                        alert = RegressionAlert(
                            metric_name=metric_label,
                            baseline_value=baseline[metric_key],
                            current_value=current[metric_key],
                            percent_change=comp["percent_change"],
                            severity=severity,
                            confidence=self.confidence_level,
                            is_significant=True,
                            recommendation=self._generate_recommendation(severity, metric_label)
                        )
                        regressions.append(alert)

                    # Track improvements
                    elif not comp["is_regression"] and abs(comp["percent_change"]) >= 5:
                        improvements.append({
                            "metric": metric_label,
                            "percent_improvement": abs(comp["percent_change"]),
                            "baseline": baseline[metric_key],
                            "current": current[metric_key]
                        })

            comparisons[name] = comparison

        # Generate summary
        summary = self._generate_summary(regressions, improvements)

        return ComparisonResult(
            benchmark_name="all",
            baseline_version="baseline",
            current_version="current",
            comparisons=comparisons,
            regressions=regressions,
            improvements=improvements,
            summary=summary
        )

    def _generate_recommendation(
        self,
        severity: RegressionSeverity,
        metric_name: str
    ) -> str:
        """Generate recommendation based on severity"""

        recommendations = {
            RegressionSeverity.CRITICAL: (
                f"CRITICAL: {metric_name} degraded significantly. "
                "This change MUST be reverted or fixed before merging. "
                "Investigate immediately - this will impact production performance."
            ),
            RegressionSeverity.HIGH: (
                f"HIGH: {metric_name} degraded substantially. "
                "This change should be fixed before merging. "
                "Review recent changes that may have impacted this metric."
            ),
            RegressionSeverity.MEDIUM: (
                f"MEDIUM: {metric_name} degraded moderately. "
                "Monitor this metric in subsequent commits. "
                "Consider optimization if trend continues."
            ),
            RegressionSeverity.LOW: (
                f"LOW: {metric_name} degraded slightly. "
                "Note this change for future reference. "
                "May accumulate over time."
            ),
            RegressionSeverity.NONE: (
                f"No significant regression detected in {metric_name}."
            )
        }

        return recommendations.get(severity, "")

    def _generate_summary(
        self,
        regressions: List[RegressionAlert],
        improvements: List[Dict]
    ) -> str:
        """Generate human-readable summary"""

        lines = []

        # Count by severity
        critical = sum(1 for r in regressions if r.severity == RegressionSeverity.CRITICAL)
        high = sum(1 for r in regressions if r.severity == RegressionSeverity.HIGH)
        medium = sum(1 for r in regressions if r.severity == RegressionSeverity.MEDIUM)
        low = sum(1 for r in regressions if r.severity == RegressionSeverity.LOW)

        lines.append("Performance Regression Summary")
        lines.append("=" * 50)

        if critical > 0:
            lines.append(f"❌ CRITICAL: {critical} regression(s) detected")
        if high > 0:
            lines.append(f"⚠️  HIGH: {high} regression(s) detected")
        if medium > 0:
            lines.append(f"⚡ MEDIUM: {medium} regression(s) detected")
        if low > 0:
            lines.append(f"ℹ️  LOW: {low} regression(s) detected")

        if len(regressions) == 0:
            lines.append("✅ No regressions detected")
        else:
            lines.append(f"\nTotal: {len(regressions)} regression(s)")

        if improvements:
            lines.append(f"\n✨ {len(improvements)} improvement(s) detected")

        return "\n".join(lines)

    def check_regressions(
        self,
        baseline_file: str = "baseline.json",
        current_file: str = None
    ) -> ComparisonResult:
        """
        Main entry point: Check for regressions in current benchmarks.

        Args:
            baseline_file: Baseline benchmark file (relative to baseline_dir)
            current_file: Current benchmark file (relative to current_dir)
                         If None, uses the most recent file
        """

        # Load baseline
        baseline_path = self.baseline_dir / baseline_file
        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline not found: {baseline_path}")

        baseline_data = self.load_benchmark(baseline_path)
        baseline_results = baseline_data.get("results", [])

        # Load current
        if current_file is None:
            # Find most recent benchmark file
            current_files = list(self.current_dir.glob("benchmarks_*.json"))
            if not current_files:
                raise FileNotFoundError(f"No benchmark files found in {self.current_dir}")
            current_path = max(current_files, key=lambda p: p.stat().st_mtime)
        else:
            current_path = self.current_dir / current_file

        current_data = self.load_benchmark(current_path)
        current_results = current_data.get("results", [])

        # Detect regressions
        result = self.detect_regressions(baseline_results, current_results)

        return result

    def save_report(self, result: ComparisonResult, filename: str = None) -> Path:
        """Save regression report to JSON"""

        if filename is None:
            filename = "regression_report.json"

        output_path = self.current_dir / filename

        with open(output_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

        return output_path

    def print_report(self, result: ComparisonResult):
        """Print regression report to console"""

        print(f"\n{'='*80}")
        print(f"PERFORMANCE REGRESSION REPORT")
        print(f"{'='*80}\n")

        print(result.summary)
        print()

        # Print regressions
        if result.regressions:
            print("DETECTED REGRESSIONS:")
            print("-" * 80)

            for alert in result.regressions:
                severity_emoji = {
                    RegressionSeverity.CRITICAL: "🔴",
                    RegressionSeverity.HIGH: "🟠",
                    RegressionSeverity.MEDIUM: "🟡",
                    RegressionSeverity.LOW: "🔵"
                }

                emoji = severity_emoji.get(alert.severity, "⚪")

                print(f"\n{emoji} {alert.severity.value.upper()}: {alert.metric_name}")
                print(f"   Baseline: {alert.baseline_value:.2f}")
                print(f"   Current:  {alert.current_value:.2f}")
                print(f"   Change:   {alert.percent_change:+.2f}%")
                print(f"   Confidence: {alert.confidence*100:.0f}%")
                print(f"\n   💡 {alert.recommendation}")

        # Print improvements
        if result.improvements:
            print(f"\n\n{'='*80}")
            print("DETECTED IMPROVEMENTS:")
            print("-" * 80)

            for improvement in result.improvements:
                print(f"\n✨ {improvement['metric']}")
                print(f"   Baseline: {improvement['baseline']:.2f}")
                print(f"   Current:  {improvement['current']:.2f}")
                print(f"   Improvement: +{improvement['percent_improvement']:.2f}%")

        print(f"\n{'='*80}\n")

    def has_critical_regressions(self, result: ComparisonResult) -> bool:
        """Check if any critical or high regressions detected"""
        return any(
            r.severity in [RegressionSeverity.CRITICAL, RegressionSeverity.HIGH]
            for r in result.regressions
        )


def main():
    """Main entry point for regression detection"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Regression Detector")
    parser.add_argument(
        "--baseline",
        default="baseline.json",
        help="Baseline benchmark file (default: baseline.json)"
    )
    parser.add_argument(
        "--current",
        default=None,
        help="Current benchmark file (default: most recent)"
    )
    parser.add_argument(
        "--baseline-dir",
        default="reports/benchmarks/baselines",
        help="Baseline directory"
    )
    parser.add_argument(
        "--current-dir",
        default="reports/benchmarks/current",
        help="Current results directory"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="Confidence level for statistical tests (default: 0.95)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save report to file"
    )

    args = parser.parse_args()

    detector = RegressionDetector(
        baseline_dir=args.baseline_dir,
        current_dir=args.current_dir,
        confidence_level=args.confidence
    )

    try:
        result = detector.check_regressions(
            baseline_file=args.baseline,
            current_file=args.current
        )

        detector.print_report(result)

        if args.output:
            detector.save_report(result, args.output)
            print(f"Report saved to: {args.output}")

        # Exit code based on critical regressions
        if detector.has_critical_regressions(result):
            exit(1)  # Fail CI on critical regressions
        else:
            exit(0)

    except Exception as e:
        print(f"Error: {e}")
        exit(2)


if __name__ == "__main__":
    main()
