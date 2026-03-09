"""
CI/CD Integration for Benchmark System

Automated benchmark execution and regression detection for CI/CD pipelines.
Includes GitHub Actions integration and PR comment generation.
"""

import json
import os
import sys
import subprocess
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class CIResult:
    """Result of CI benchmark run"""
    success: bool
    has_regressions: bool
    critical_regressions: int
    high_regressions: int
    report_url: Optional[str]
    summary: str

    def to_dict(self) -> Dict:
        return asdict(self)


class BenchmarkCI:
    """
    CI/CD integration for benchmark system.

    Features:
    - Automated benchmark execution in CI
    - Regression detection with fail-fast
    - PR comment generation with results
    - Status check integration
    - Artifact upload
    """

    def __init__(
        self,
        output_dir: str = "reports/benchmarks/current",
        baseline_dir: str = "reports/benchmarks/baselines"
    ):
        self.output_dir = Path(output_dir)
        self.baseline_dir = Path(baseline_dir)
        self.is_ci = self._detect_ci()
        self.ci_provider = self._detect_ci_provider()

    def _detect_ci(self) -> bool:
        """Detect if running in CI environment"""

        ci_indicators = [
            "CI",                     # Generic CI
            "GITHUB_ACTIONS",         # GitHub Actions
            "TRAVIS",                 # Travis CI
            "CIRCLECI",               # CircleCI
            "JENKINS_HOME",           # Jenkins
            "GITLAB_CI",              # GitLab CI
            "BITBUCKET_BUILD_NUMBER"  # Bitbucket
        ]

        return any(indicator in os.environ for indicator in ci_indicators)

    def _detect_ci_provider(self) -> str:
        """Detect which CI provider is being used"""

        if "GITHUB_ACTIONS" in os.environ:
            return "github"
        elif "TRAVIS" in os.environ:
            return "travis"
        elif "CIRCLECI" in os.environ:
            return "circleci"
        elif "GITLAB_CI" in os.environ:
            return "gitlab"
        else:
            return "unknown"

    def get_commit_info(self) -> Dict[str, str]:
        """Get current commit information"""

        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            commit_message = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            return {
                "hash": commit_hash,
                "message": commit_message,
                "branch": branch
            }

        except Exception:
            return {
                "hash": "unknown",
                "message": "unknown",
                "branch": "unknown"
            }

    def run_benchmarks(self, scale: str = "small") -> bool:
        """Run benchmark suite"""

        print(f"Running benchmarks (scale: {scale})...")

        try:
            # Import and run benchmark suite
            from benchmark_suite import BenchmarkSuite

            suite = BenchmarkSuite(output_dir=str(self.output_dir))
            results = suite.run_all_benchmarks(scale=scale)
            suite.save_results()

            print("✓ Benchmarks completed successfully")
            return True

        except Exception as e:
            print(f"✗ Benchmark execution failed: {e}")
            return False

    def check_regressions(self) -> CIResult:
        """Check for performance regressions"""

        print("Checking for regressions...")

        try:
            from regression_detector import RegressionDetector

            detector = RegressionDetector(
                baseline_dir=str(self.baseline_dir),
                current_dir=str(self.output_dir)
            )

            # Try to load baseline
            baseline_files = list(self.baseline_dir.glob("*.json"))
            if not baseline_files:
                print("⚠ No baseline found, skipping regression check")
                return CIResult(
                    success=True,
                    has_regressions=False,
                    critical_regressions=0,
                    high_regressions=0,
                    report_url=None,
                    summary="No baseline to compare against"
                )

            baseline_file = baseline_files[0].name

            result = detector.check_regressions(baseline_file=baseline_file)
            detector.save_report(result)
            detector.print_report(result)

            # Count regressions by severity
            critical = sum(1 for r in result.regressions if r.severity.value == "critical")
            high = sum(1 for r in result.regressions if r.severity.value == "high")

            has_critical = detector.has_critical_regressions(result)

            return CIResult(
                success=not has_critical,
                has_regressions=len(result.regressions) > 0,
                critical_regressions=critical,
                high_regressions=high,
                report_url=None,
                summary=result.summary
            )

        except Exception as e:
            print(f"✗ Regression check failed: {e}")
            return CIResult(
                success=False,
                has_regressions=False,
                critical_regressions=0,
                high_regressions=0,
                report_url=None,
                summary=f"Regression check failed: {e}"
            )

    def generate_pr_comment(self, result: CIResult) -> str:
        """Generate PR comment with benchmark results"""

        commit_info = self.get_commit_info()

        # Build status emoji
        if result.success and not result.has_regressions:
            status_emoji = "✅"
            status_text = "All benchmarks passed, no regressions detected"
        elif result.has_regressions:
            status_emoji = "⚠️"
            status_text = f"Performance regressions detected"
        else:
            status_emoji = "❌"
            status_text = "Benchmark execution failed"

        comment = f"""
## 📊 Benchmark Results

{status_emoji} **Status:** {status_text}

**Commit:** `{commit_info['hash'][:8]}`
**Branch:** `{commit_info['branch']}`

### Summary

{result.summary}

"""

        if result.has_regressions:
            comment += """
### Regressions Detected

⚠️ Performance regressions were detected in this commit. Please review the changes before merging.

- **Critical:** {critical} regression(s)
- **High:** {high} regression(s)

See the full benchmark report for details.
""".format(
                critical=result.critical_regressions,
                high=result.high_regressions
            )

        comment += """
---

*This comment was automatically generated by the POLLN Benchmark System*
"""

        return comment

    def post_pr_comment(self, comment: str):
        """Post comment to PR (GitHub Actions)"""

        if self.ci_provider != "github":
            print(f"PR comments not supported for {self.ci_provider}")
            return

        try:
            # Get PR number from environment
            event_path = os.environ.get("GITHUB_EVENT_PATH")
            if not event_path:
                print("No GitHub event path found")
                return

            with open(event_path, 'r') as f:
                event_data = json.load(f)

            # Check if this is a PR event
            if "pull_request" not in event_data:
                print("Not a pull request event")
                return

            # Use GitHub CLI to post comment
            pr_number = event_data["pull_request"]["number"]

            # Save comment to file for GitHub CLI
            comment_file = Path("pr_comment.md")
            with open(comment_file, 'w') as f:
                f.write(comment)

            # Post comment using gh CLI
            subprocess.run([
                "gh", "pr", "comment", str(pr_number),
                "--body-file", str(comment_file)
            ], check=True)

            print(f"✓ Posted PR comment")

        except Exception as e:
            print(f"Failed to post PR comment: {e}")

    def run_ci_pipeline(
        self,
        scale: str = "small",
        fail_on_regression: bool = True
    ) -> CIResult:
        """Run complete CI pipeline"""

        print("=" * 80)
        print("POLLN Benchmark CI Pipeline")
        print("=" * 80)
        print()

        commit_info = self.get_commit_info()
        print(f"Commit: {commit_info['hash'][:8]}")
        print(f"Branch: {commit_info['branch']}")
        print(f"CI Provider: {self.ci_provider}")
        print()

        # Run benchmarks
        benchmark_success = self.run_benchmarks(scale)

        if not benchmark_success:
            result = CIResult(
                success=False,
                has_regressions=False,
                critical_regressions=0,
                high_regressions=0,
                report_url=None,
                summary="Benchmark execution failed"
            )

            # Post PR comment
            if self.is_ci:
                comment = self.generate_pr_comment(result)
                self.post_pr_comment(comment)

            return result

        # Check regressions
        result = self.check_regressions()

        # Post PR comment
        if self.is_ci:
            comment = self.generate_pr_comment(result)
            self.post_pr_comment(comment)

        # Exit with appropriate code
        if fail_on_regression and not result.success:
            print("\n❌ CI failed: Critical regressions detected")
            sys.exit(1)
        elif not result.success:
            print("\n⚠️ CI passed with warnings")
            sys.exit(0)
        else:
            print("\n✅ CI passed")
            sys.exit(0)

        return result


def main():
    """Main entry point for CI"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Benchmark CI")
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default="small",
        help="Benchmark scale (default: small)"
    )
    parser.add_argument(
        "--no-fail-on-regression",
        action="store_false",
        dest="fail_on_regression",
        help="Don't fail CI on regression"
    )
    parser.add_argument(
        "--output-dir",
        default="reports/benchmarks/current",
        help="Output directory"
    )
    parser.add_argument(
        "--baseline-dir",
        default="reports/benchmarks/baselines",
        help="Baseline directory"
    )

    args = parser.parse_args()

    ci = BenchmarkCI(
        output_dir=args.output_dir,
        baseline_dir=args.baseline_dir
    )

    ci.run_ci_pipeline(
        scale=args.scale,
        fail_on_regression=args.fail_on_regression
    )


if __name__ == "__main__":
    main()
