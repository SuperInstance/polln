"""
Baseline Manager

Manages benchmark baselines for performance comparisons.
Handles storing, updating, and comparing against multiple baselines.
"""

import json
import hashlib
import shutil
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum


class BaselineStatus(Enum):
    """Status of a baseline"""
    ACTIVE = "active"           # Currently used for comparisons
    ARCHIVED = "archived"       # Old baseline, kept for reference
    PENDING = "pending"         # New baseline awaiting verification
    REJECTED = "rejected"       # Failed verification


@dataclass
class Baseline:
    """A benchmark baseline"""
    name: str
    version: str  # Semantic version or commit hash
    commit_hash: str
    branch: str
    created_at: float
    status: BaselineStatus
    description: str
    config: Dict  # Benchmark configuration used
    results: Dict  # Actual benchmark results
    metadata: Dict  # Additional metadata

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class BaselineComparison:
    """Comparison between current results and a baseline"""
    baseline_name: str
    baseline_version: str
    current_version: str
    comparisons: Dict[str, Dict]  # metric -> comparison data
    better_count: int  # Number of improved metrics
    worse_count: int   # Number of degraded metrics
    same_count: int    # Number of unchanged metrics
    verdict: str       # overall, better, worse

    def to_dict(self) -> Dict:
        return asdict(self)


class BaselineManager:
    """
    Manage benchmark baselines for performance tracking.

    Features:
    - Store multiple baselines per configuration
    - Update baselines when improvements verified
    - Compare against multiple baselines
    - Automatic baseline versioning
    - Baseline status tracking
    """

    def __init__(
        self,
        baseline_dir: str = "reports/benchmarks/baselines",
        current_dir: str = "reports/benchmarks/current"
    ):
        self.baseline_dir = Path(baseline_dir)
        self.current_dir = Path(current_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.baselines: Dict[str, Baseline] = {}
        self.load_all_baselines()

    def load_all_baselines(self):
        """Load all baselines from directory"""

        for baseline_file in self.baseline_dir.glob("*.json"):
            try:
                with open(baseline_file, 'r') as f:
                    data = json.load(f)

                baseline = Baseline(
                    name=data["name"],
                    version=data["version"],
                    commit_hash=data["commit_hash"],
                    branch=data["branch"],
                    created_at=data["created_at"],
                    status=BaselineStatus(data["status"]),
                    description=data["description"],
                    config=data["config"],
                    results=data["results"],
                    metadata=data.get("metadata", {})
                )

                self.baselines[baseline.name] = baseline

            except Exception as e:
                print(f"Error loading baseline {baseline_file}: {e}")

    def create_baseline(
        self,
        name: str,
        results_file: str,
        description: str = "",
        version: str = None,
        status: BaselineStatus = BaselineStatus.ACTIVE
    ) -> Baseline:
        """Create a new baseline from benchmark results"""

        # Load benchmark results
        results_path = self.current_dir / results_file
        if not results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_path}")

        with open(results_path, 'r') as f:
            results_data = json.load(f)

        # Get commit info
        try:
            import subprocess
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            commit_hash = "unknown"
            branch = "main"

        # Generate version if not provided
        if version is None:
            version = commit_hash[:8] if commit_hash != "unknown" else "0.0.0"

        # Create baseline
        baseline = Baseline(
            name=name,
            version=version,
            commit_hash=commit_hash,
            branch=branch,
            created_at=datetime.now().timestamp(),
            status=status,
            description=description,
            config=results_data.get("config", {}),
            results=results_data,
            metadata={
                "source_file": str(results_path),
                "created_by": "baseline_manager"
            }
        )

        # Save baseline
        self.save_baseline(baseline)
        self.baselines[name] = baseline

        return baseline

    def save_baseline(self, baseline: Baseline) -> Path:
        """Save baseline to file"""

        filename = f"{baseline.name}_{baseline.version}.json"
        output_path = self.baseline_dir / filename

        with open(output_path, 'w') as f:
            json.dump(baseline.to_dict(), f, indent=2)

        return output_path

    def get_baseline(self, name: str) -> Optional[Baseline]:
        """Get baseline by name"""

        return self.baselines.get(name)

    def get_active_baseline(self) -> Optional[Baseline]:
        """Get the currently active baseline"""

        for baseline in self.baselines.values():
            if baseline.status == BaselineStatus.ACTIVE:
                return baseline

        return None

    def set_active_baseline(self, name: str):
        """Set a baseline as active (deactivates others)"""

        if name not in self.baselines:
            raise ValueError(f"Baseline not found: {name}")

        # Deactivate all others
        for baseline in self.baselines.values():
            if baseline.status == BaselineStatus.ACTIVE:
                baseline.status = BaselineStatus.ARCHIVED
                self.save_baseline(baseline)

        # Activate selected
        self.baselines[name].status = BaselineStatus.ACTIVE
        self.save_baseline(self.baselines[name])

    def compare_to_baseline(
        self,
        current_results: List[Dict],
        baseline_name: str = None
    ) -> BaselineComparison:
        """Compare current results against a baseline"""

        # Get baseline
        if baseline_name is None:
            baseline = self.get_active_baseline()
            if baseline is None:
                raise ValueError("No active baseline found")
        else:
            baseline = self.get_baseline(baseline_name)
            if baseline is None:
                raise ValueError(f"Baseline not found: {baseline_name}")

        baseline_results = baseline.results.get("results", [])

        # Group by benchmark name
        baseline_by_name = {r["name"]: r for r in baseline_results}
        current_by_name = {r["name"]: r for r in current_results}

        comparisons = {}
        better_count = 0
        worse_count = 0
        same_count = 0

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
                    baseline_val = baseline[metric_key]
                    current_val = current[metric_key]

                    # Calculate percent change
                    if lower_is_better:
                        percent_change = ((current_val - baseline_val) / baseline_val) * 100
                        is_better = current_val < baseline_val
                    else:
                        percent_change = ((baseline_val - current_val) / baseline_val) * 100
                        is_better = current_val > baseline_val

                    comparison[metric_key] = {
                        "metric": metric_label,
                        "baseline": baseline_val,
                        "current": current_val,
                        "percent_change": percent_change,
                        "is_better": is_better,
                        "is_same": abs(percent_change) < 2
                    }

            comparisons[name] = comparison

            # Count improvements/degradations
            for metric_comp in comparison.values():
                if metric_comp["is_same"]:
                    same_count += 1
                elif metric_comp["is_better"]:
                    better_count += 1
                else:
                    worse_count += 1

        # Determine verdict
        if better_count > worse_count * 1.5:
            verdict = "better"
        elif worse_count > better_count * 1.5:
            verdict = "worse"
        else:
            verdict = "similar"

        return BaselineComparison(
            baseline_name=baseline.name,
            baseline_version=baseline.version,
            current_version="current",
            comparisons=comparisons,
            better_count=better_count,
            worse_count=worse_count,
            same_count=same_count,
            verdict=verdict
        )

    def should_update_baseline(
        self,
        current_results: List[Dict],
        baseline_name: str = None,
        improvement_threshold: float = 5.0  # percent
    ) -> Tuple[bool, str]:
        """
        Determine if baseline should be updated based on current results.

        Returns:
            (should_update, reason)
        """

        comparison = self.compare_to_baseline(current_results, baseline_name)

        # Calculate net improvement
        total_metrics = comparison.better_count + comparison.worse_count + comparison.same_count
        if total_metrics == 0:
            return False, "No metrics to compare"

        improvement_ratio = comparison.better_count / total_metrics

        if comparison.verdict == "better" and improvement_ratio > 0.6:
            return True, f"Significant improvement detected ({comparison.better_count} better vs {comparison.worse_count} worse)"
        elif comparison.verdict == "similar":
            return False, "Performance is similar to baseline"
        else:
            return False, f"Performance degraded compared to baseline"

    def update_baseline(
        self,
        current_results_file: str,
        baseline_name: str = None,
        description: str = None
    ) -> Baseline:
        """Update baseline with current results"""

        # Check if update is warranted
        with open(self.current_dir / current_results_file, 'r') as f:
            data = json.load(f)

        current_results = data.get("results", [])

        should_update, reason = self.should_update_baseline(
            current_results,
            baseline_name
        )

        if not should_update:
            raise ValueError(f"Cannot update baseline: {reason}")

        # Get old baseline info
        old_baseline = self.get_baseline(baseline_name) if baseline_name else self.get_active_baseline()

        # Generate new version
        if old_baseline:
            old_version = old_baseline.version
            new_version = f"{old_version}+"
        else:
            new_version = "1.0.0"

        # Create new baseline
        if description is None:
            description = reason

        new_baseline = self.create_baseline(
            name=baseline_name or "main",
            results_file=current_results_file,
            description=description,
            version=new_version,
            status=BaselineStatus.PENDING
        )

        # Archive old baseline
        if old_baseline:
            old_baseline.status = BaselineStatus.ARCHIVED
            self.save_baseline(old_baseline)

        return new_baseline

    def approve_baseline(self, name: str):
        """Approve a pending baseline"""

        if name not in self.baselines:
            raise ValueError(f"Baseline not found: {name}")

        baseline = self.baselines[name]
        if baseline.status != BaselineStatus.PENDING:
            raise ValueError(f"Baseline is not pending: {name}")

        # Deactivate current active baseline
        active = self.get_active_baseline()
        if active:
            active.status = BaselineStatus.ARCHIVED
            self.save_baseline(active)

        # Activate new baseline
        baseline.status = BaselineStatus.ACTIVE
        self.save_baseline(baseline)

    def list_baselines(
        self,
        status: BaselineStatus = None
    ) -> List[Baseline]:
        """List all baselines, optionally filtered by status"""

        baselines = list(self.baselines.values())

        if status:
            baselines = [b for b in baselines if b.status == status]

        return sorted(baselines, key=lambda b: b.created_at, reverse=True)

    def delete_baseline(self, name: str):
        """Delete a baseline"""

        if name not in self.baselines:
            raise ValueError(f"Baseline not found: {name}")

        baseline = self.baselines[name]

        # Don't delete active baseline
        if baseline.status == BaselineStatus.ACTIVE:
            raise ValueError("Cannot delete active baseline")

        # Delete file
        filename = f"{baseline.name}_{baseline.version}.json"
        filepath = self.baseline_dir / filename

        if filepath.exists():
            filepath.unlink()

        # Remove from memory
        del self.baselines[name]

    def print_summary(self):
        """Print summary of all baselines"""

        print(f"\n{'='*80}")
        print(f"BASELINE SUMMARY")
        print(f"{'='*80}\n")

        active = self.get_active_baseline()
        if active:
            print(f"Active Baseline: {active.name} (v{active.version})")
            print(f"  Created: {datetime.fromtimestamp(active.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Commit: {active.commit_hash}")
            print(f"  Description: {active.description}")
        else:
            print("No active baseline")

        print(f"\nAll Baselines:")

        for baseline in self.list_baselines():
            status_emoji = {
                BaselineStatus.ACTIVE: "✅",
                BaselineStatus.PENDING: "⏳",
                BaselineStatus.ARCHIVED: "📦",
                BaselineStatus.REJECTED: "❌"
            }

            emoji = status_emoji.get(baseline.status, "❓")

            print(f"\n{emoji} {baseline.name} (v{baseline.version})")
            print(f"   Status: {baseline.status.value}")
            print(f"   Created: {datetime.fromtimestamp(baseline.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Description: {baseline.description}")


def main():
    """Main entry point for baseline management"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Baseline Manager")
    parser.add_argument(
        "action",
        choices=["create", "list", "set-active", "approve", "delete", "compare", "update"],
        help="Action to perform"
    )
    parser.add_argument(
        "--name",
        help="Baseline name"
    )
    parser.add_argument(
        "--results",
        help="Benchmark results file (for create/update)"
    )
    parser.add_argument(
        "--description",
        default="",
        help="Baseline description"
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

    args = parser.parse_args()

    manager = BaselineManager(
        baseline_dir=args.baseline_dir,
        current_dir=args.current_dir
    )

    try:
        if args.action == "create":
            if not args.name or not args.results:
                print("Error: --name and --results required for create")
                exit(1)

            baseline = manager.create_baseline(
                name=args.name,
                results_file=args.results,
                description=args.description
            )

            print(f"Created baseline: {baseline.name} (v{baseline.version})")
            print(f"File: {manager.save_baseline(baseline)}")

        elif args.action == "list":
            manager.print_summary()

        elif args.action == "set-active":
            if not args.name:
                print("Error: --name required for set-active")
                exit(1)

            manager.set_active_baseline(args.name)
            print(f"Set {args.name} as active baseline")

        elif args.action == "approve":
            if not args.name:
                print("Error: --name required for approve")
                exit(1)

            manager.approve_baseline(args.name)
            print(f"Approved baseline: {args.name}")

        elif args.action == "delete":
            if not args.name:
                print("Error: --name required for delete")
                exit(1)

            manager.delete_baseline(args.name)
            print(f"Deleted baseline: {args.name}")

        elif args.action == "compare":
            # Load current results
            current_files = list(Path(args.current_dir).glob("benchmarks_*.json"))
            if not current_files:
                current_files = list(Path(args.current_dir).glob("benchmark_run_*.json"))

            if not current_files:
                print("Error: No current benchmark results found")
                exit(1)

            with open(current_files[0], 'r') as f:
                data = json.load(f)

            current_results = data.get("results", [])

            comparison = manager.compare_to_baseline(current_results, args.name)

            print(f"\nComparison vs {comparison.baseline_name} (v{comparison.baseline_version})")
            print(f"Verdict: {comparison.verdict}")
            print(f"Better: {comparison.better_count}")
            print(f"Worse: {comparison.worse_count}")
            print(f"Same: {comparison.same_count}")

        elif args.action == "update":
            if not args.results:
                print("Error: --results required for update")
                exit(1)

            new_baseline = manager.update_baseline(
                current_results_file=args.results,
                baseline_name=args.name,
                description=args.description
            )

            print(f"Created new baseline version: {new_baseline.version}")
            print(f"Status: {new_baseline.status.value}")
            print(f"Approve with: python baseline_manager.py approve --name {new_baseline.name}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
