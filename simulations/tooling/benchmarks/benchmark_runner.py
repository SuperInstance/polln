"""
Automated Benchmark Runner

Orchestrates automated benchmark execution for CI/CD pipelines.
Supports parallel execution, caching, and result aggregation.
"""

import json
import time
import hashlib
import subprocess
import multiprocessing as mp
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
import os


@dataclass
class BenchmarkJob:
    """A single benchmark job configuration"""
    name: str
    category: str  # agents, colony, learning, kv_cache
    scale: str  # small, medium, large
    script: str
    args: Dict[str, Any]
    priority: int = 0  # Higher = run first
    timeout: int = 600  # seconds

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class JobResult:
    """Result of a benchmark job execution"""
    job_name: str
    status: str  # success, failed, timeout, skipped
    duration: float
    output_file: Optional[str]
    error_message: Optional[str]
    metrics: Dict[str, float]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BenchmarkRun:
    """Complete benchmark run results"""
    run_id: str
    timestamp: float
    commit_hash: str
    branch: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: str
    total_duration: float
    jobs: List[JobResult]
    summary: str

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "total_jobs": self.total_jobs,
            "successful_jobs": self.successful_jobs,
            "failed_jobs": self.failed_jobs,
            "total_duration": self.total_duration,
            "jobs": [j.to_dict() for j in self.jobs],
            "summary": self.summary
        }


class BenchmarkRunner:
    """
    Automated benchmark execution for CI/CD.

    Features:
    - Parallel job execution
    - Result caching to avoid redundant runs
    - Timeout handling
    - Progress tracking
    - Automatic retries
    - CI/CD integration
    """

    def __init__(
        self,
        output_dir: str = "reports/benchmarks/current",
        cache_dir: str = "reports/benchmarks/cache",
        max_workers: Optional[int] = None
    ):
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Use CPU count if not specified
        if max_workers is None:
            self.max_workers = max(1, mp.cpu_count() - 1)
        else:
            self.max_workers = max_workers

    def get_commit_info(self) -> tuple:
        """Get current git commit hash and branch"""
        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            return commit_hash, branch
        except Exception:
            return "unknown", "unknown"

    def generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        commit_hash, _ = self.get_commit_info()
        short_hash = commit_hash[:8] if commit_hash != "unknown" else "unknown"
        return f"run_{timestamp}_{short_hash}"

    def get_cache_key(self, job: BenchmarkJob) -> str:
        """Generate cache key for a job"""
        # Hash job configuration
        job_data = json.dumps(job.to_dict(), sort_keys=True)
        return hashlib.md5(job_data.encode()).hexdigest()

    def check_cache(self, job: BenchmarkJob) -> Optional[Dict]:
        """Check if job result is cached"""

        cache_key = self.get_cache_key(job)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)

                # Check if cache is fresh (less than 24 hours)
                cache_age = time.time() - cached.get("timestamp", 0)
                if cache_age < 86400:  # 24 hours
                    return cached
            except Exception:
                pass

        return None

    def save_to_cache(self, job: BenchmarkJob, result: Dict):
        """Save job result to cache"""

        cache_key = self.get_cache_key(job)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            "timestamp": time.time(),
            "job": job.to_dict(),
            "result": result
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def execute_job(self, job: BenchmarkJob, use_cache: bool = True) -> JobResult:
        """Execute a single benchmark job"""

        start_time = time.time()

        # Check cache first
        if use_cache:
            cached = self.check_cache(job)
            if cached:
                return JobResult(
                    job_name=job.name,
                    status="success",
                    duration=0.0,
                    output_file=cached.get("output_file"),
                    error_message=None,
                    metrics=cached.get("result", {}).get("metrics", {})
                )

        try:
            # Import and run benchmark suite
            from benchmark_suite import BenchmarkSuite

            suite = BenchmarkSuite(output_dir=str(self.output_dir))

            # Run appropriate benchmark
            if job.category == "agents":
                if "creation" in job.name:
                    result = suite.benchmark_agent_creation()
                elif "activation" in job.name:
                    result = suite.benchmark_agent_activation()
                elif "decision" in job.name:
                    result = suite.benchmark_agent_decision_making()
            elif job.category == "colony":
                if "coordination" in job.name:
                    result = suite.benchmark_colony_coordination(
                        colony_size=job.args.get("colony_size", 100)
                    )
                elif "communication" in job.name:
                    result = suite.benchmark_colony_communication(
                        message_count=job.args.get("message_count", 50)
                    )
            elif job.category == "learning":
                if "hebbian" in job.name:
                    result = suite.benchmark_hebbian_learning(
                        synapse_count=job.args.get("synapse_count", 1000)
                    )
                elif "dreaming" in job.name:
                    result = suite.benchmark_dreaming_cycle()
            elif job.category == "kv_cache":
                if "anchor" in job.name:
                    result = suite.benchmark_kv_anchor_creation()
                elif "ann" in job.name:
                    result = suite.benchmark_ann_matching(
                        index_size=job.args.get("index_size", 10000)
                    )
            else:
                raise ValueError(f"Unknown category: {job.category}")

            duration = time.time() - start_time

            # Extract key metrics
            metrics = {
                "throughput": result.throughput_ops,
                "avg_latency": result.avg_latency_ms,
                "p95_latency": result.p95_latency_ms,
                "memory_mb": result.memory_mb,
                "success_rate": result.success_rate
            }

            # Save to cache
            self.save_to_cache(job, {"metrics": metrics})

            return JobResult(
                job_name=job.name,
                status="success",
                duration=duration,
                output_file=None,
                error_message=None,
                metrics=metrics
            )

        except Exception as e:
            duration = time.time() - start_time
            return JobResult(
                job_name=job.name,
                status="failed",
                duration=duration,
                output_file=None,
                error_message=str(e),
                metrics={}
            )

    def create_default_jobs(self, scale: str = "small") -> List[BenchmarkJob]:
        """Create default benchmark jobs for a given scale"""

        scale_configs = {
            "small": {"colony_size": 50, "message_count": 25, "synapse_count": 500, "index_size": 5000},
            "medium": {"colony_size": 100, "message_count": 50, "synapse_count": 1000, "index_size": 10000},
            "large": {"colony_size": 500, "message_count": 200, "synapse_count": 5000, "index_size": 50000}
        }

        config = scale_configs[scale]

        return [
            # Agent benchmarks
            BenchmarkJob(
                name="agent_creation",
                category="agents",
                scale=scale,
                script="benchmark_suite.py",
                args={},
                priority=10
            ),
            BenchmarkJob(
                name="agent_activation",
                category="agents",
                scale=scale,
                script="benchmark_suite.py",
                args={},
                priority=10
            ),
            BenchmarkJob(
                name="agent_decision_making",
                category="agents",
                scale=scale,
                script="benchmark_suite.py",
                args={},
                priority=10
            ),

            # Colony benchmarks
            BenchmarkJob(
                name="colony_coordination",
                category="colony",
                scale=scale,
                script="benchmark_suite.py",
                args={"colony_size": config["colony_size"]},
                priority=8
            ),
            BenchmarkJob(
                name="colony_communication",
                category="colony",
                scale=scale,
                script="benchmark_suite.py",
                args={"message_count": config["message_count"]},
                priority=8
            ),

            # Learning benchmarks
            BenchmarkJob(
                name="hebbian_learning",
                category="learning",
                scale=scale,
                script="benchmark_suite.py",
                args={"synapse_count": config["synapse_count"]},
                priority=7
            ),
            BenchmarkJob(
                name="dreaming_cycle",
                category="learning",
                scale=scale,
                script="benchmark_suite.py",
                args={},
                priority=7
            ),

            # KV-Cache benchmarks
            BenchmarkJob(
                name="kv_anchor_creation",
                category="kv_cache",
                scale=scale,
                script="benchmark_suite.py",
                args={},
                priority=9
            ),
            BenchmarkJob(
                name="ann_matching",
                category="kv_cache",
                scale=scale,
                script="benchmark_suite.py",
                args={"index_size": config["index_size"]},
                priority=9
            ),
        ]

    def run_benchmarks(
        self,
        scale: str = "small",
        categories: Optional[List[str]] = None,
        parallel: bool = True,
        use_cache: bool = True
    ) -> BenchmarkRun:
        """Run benchmark suite"""

        start_time = time.time()
        commit_hash, branch = self.get_commit_info()
        run_id = self.generate_run_id()

        # Create jobs
        all_jobs = self.create_default_jobs(scale)

        # Filter by category if specified
        if categories:
            all_jobs = [j for j in all_jobs if j.category in categories]

        # Sort by priority
        all_jobs.sort(key=lambda j: j.priority, reverse=True)

        # Execute jobs
        results = []

        if parallel:
            # Parallel execution
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_job = {
                    executor.submit(self.execute_job, job, use_cache): job
                    for job in all_jobs
                }

                for future in as_completed(future_to_job):
                    job = future_to_job[future]
                    try:
                        result = future.result(timeout=job.timeout)
                        results.append(result)
                        print(f"✓ {job.name}: {result.status}")
                    except Exception as e:
                        results.append(JobResult(
                            job_name=job.name,
                            status="failed",
                            duration=0.0,
                            output_file=None,
                            error_message=str(e),
                            metrics={}
                        ))
                        print(f"✗ {job.name}: {e}")
        else:
            # Sequential execution
            for job in all_jobs:
                print(f"Running: {job.name}")
                result = self.execute_job(job, use_cache)
                results.append(result)
                print(f"  Status: {result.status}")

        # Calculate summary
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")

        summary = f"Benchmark run complete: {successful}/{len(results)} successful"

        run = BenchmarkRun(
            run_id=run_id,
            timestamp=time.time(),
            commit_hash=commit_hash,
            branch=branch,
            total_jobs=len(all_jobs),
            successful_jobs=successful,
            failed_jobs=failed,
            total_duration=total_duration,
            jobs=results,
            summary=summary
        )

        return run

    def save_run(self, run: BenchmarkRun, filename: str = None) -> Path:
        """Save benchmark run results"""

        if filename is None:
            filename = f"benchmark_run_{run.run_id}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(run.to_dict(), f, indent=2)

        return output_path

    def print_summary(self, run: BenchmarkRun):
        """Print benchmark run summary"""

        print(f"\n{'='*80}")
        print(f"BENCHMARK RUN SUMMARY")
        print(f"{'='*80}\n")

        print(f"Run ID: {run.run_id}")
        print(f"Commit: {run.commit_hash}")
        print(f"Branch: {run.branch}")
        print(f"Duration: {run.total_duration:.2f}s")

        print(f"\nResults: {run.successful_jobs}/{run.total_jobs} successful")

        print(f"\n{'='*60}")
        print("Job Results:")
        print(f"{'='*60}")

        for job in run.jobs:
            status_emoji = {"success": "✓", "failed": "✗", "skipped": "⊘"}
            emoji = status_emoji.get(job.status, "?")

            print(f"\n{emoji} {job.job_name}")
            print(f"   Status: {job.status}")
            print(f"   Duration: {job.duration:.2f}s")

            if job.metrics:
                print(f"   Metrics:")
                for key, value in job.metrics.items():
                    print(f"     {key}: {value:.2f}")

            if job.error_message:
                print(f"   Error: {job.error_message}")

        print(f"\n{'='*80}\n")

    def copy_to_history(self, run: BenchmarkRun):
        """Copy benchmark results to history directory"""

        history_dir = Path("reports/benchmarks/history")
        history_dir.mkdir(parents=True, exist_ok=True)

        # Create directory for this commit
        commit_dir = history_dir / run.commit_hash
        commit_dir.mkdir(exist_ok=True)

        # Copy run file
        source_file = self.output_dir / f"benchmark_run_{run.run_id}.json"
        dest_file = commit_dir / f"{run.run_id}.json"

        if source_file.exists():
            import shutil
            shutil.copy(source_file, dest_file)
            print(f"Copied to history: {dest_file}")


def main():
    """Main entry point for benchmark runner"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Benchmark Runner")
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default="small",
        help="Benchmark scale (default: small)"
    )
    parser.add_argument(
        "--category",
        choices=["agents", "colony", "learning", "kv_cache"],
        action="append",
        help="Benchmark categories to run (default: all)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run benchmarks in parallel (default: True)"
    )
    parser.add_argument(
        "--sequential",
        action="store_false",
        dest="parallel",
        help="Run benchmarks sequentially"
    )
    parser.add_argument(
        "--no-cache",
        action="store_false",
        dest="use_cache",
        help="Disable result caching"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: CPU count - 1)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports/benchmarks/current",
        help="Output directory for results"
    )

    args = parser.parse_args()

    runner = BenchmarkRunner(
        output_dir=args.output_dir,
        max_workers=args.workers
    )

    print("Starting benchmark run...")
    print(f"Scale: {args.scale}")
    print(f"Categories: {args.category or 'all'}")
    print(f"Parallel: {args.parallel}")
    print()

    run = runner.run_benchmarks(
        scale=args.scale,
        categories=args.category,
        parallel=args.parallel,
        use_cache=args.use_cache
    )

    runner.print_summary(run)
    runner.save_run(run)
    runner.copy_to_history(run)

    # Exit with error code if any jobs failed
    if run.failed_jobs > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
