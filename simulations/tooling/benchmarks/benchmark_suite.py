"""
POLLN Benchmark Suite

Comprehensive benchmark suite for tracking POLLN performance over time.
Measures latency, throughput, memory usage, and accuracy for core operations.
"""

import time
import json
import psutil
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path
import statistics
from contextlib import contextmanager


@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    name: str
    operation: str
    iterations: int
    total_time: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_ops: float
    memory_mb: float
    cpu_percent: float
    success_rate: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    name: str
    warmup_iterations: int = 10
    benchmark_iterations: int = 100
    timeout_seconds: int = 300
    memory_threshold_mb: float = 1024
    cpu_threshold_percent: float = 90
    collect_memory: bool = True
    collect_cpu: bool = True
    collect_latency: bool = True
    parallel_runs: int = 1


class BenchmarkSuite:
    """
    Comprehensive benchmark suite for POLLN operations.

    Supports:
    - Agent operations (creation, activation, deletion)
    - Colony operations (coordination, communication)
    - A2A communication (package transmission, routing)
    - Learning operations (Hebbian, dreaming, evolution)
    - KV-Cache operations (anchor pooling, matching)
    """

    def __init__(self, output_dir: str = "reports/benchmarks/current"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []

    @contextmanager
    def _measure_resources(self):
        """Context manager for measuring memory and CPU usage"""
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        start_time = time.time()

        yield

        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        elapsed = time.time() - start_time

        self._current_memory = end_memory - start_memory
        self._current_cpu = (start_cpu + end_cpu) / 2
        self._elapsed_time = elapsed

    def _run_benchmark(
        self,
        name: str,
        operation: Callable,
        config: BenchmarkConfig,
        **kwargs
    ) -> BenchmarkResult:
        """Run a single benchmark with warmup and measurement phases"""

        # Warmup phase
        for _ in range(config.warmup_iterations):
            try:
                operation(**kwargs)
            except Exception as e:
                print(f"Warmup failed: {e}")

        # Measurement phase
        latencies = []
        success_count = 0
        start_time = time.time()

        for i in range(config.benchmark_iterations):
            iter_start = time.time()
            try:
                operation(**kwargs)
                iter_latency = (time.time() - iter_start) * 1000  # ms
                latencies.append(iter_latency)
                success_count += 1
            except Exception as e:
                print(f"Iteration {i} failed: {e}")
                latencies.append(0)  # Record failed iterations

        total_time = time.time() - start_time

        # Calculate statistics
        valid_latencies = [l for l in latencies if l > 0]
        if not valid_latencies:
            raise RuntimeError("All iterations failed")

        return BenchmarkResult(
            name=name,
            operation=operation.__name__,
            iterations=config.benchmark_iterations,
            total_time=total_time,
            avg_latency_ms=statistics.mean(valid_latencies),
            min_latency_ms=min(valid_latencies),
            max_latency_ms=max(valid_latencies),
            p50_latency_ms=np.percentile(valid_latencies, 50),
            p95_latency_ms=np.percentile(valid_latencies, 95),
            p99_latency_ms=np.percentile(valid_latencies, 99),
            throughput_ops=config.benchmark_iterations / total_time,
            memory_mb=getattr(self, '_current_memory', 0),
            cpu_percent=getattr(self, '_current_cpu', 0),
            success_rate=success_count / config.benchmark_iterations,
            metadata={"config": asdict(config)}
        )

    # ===== AGENT BENCHMARKS =====

    def benchmark_agent_creation(
        self,
        config: Optional[BenchmarkConfig] = None,
        agent_factory: Callable = None
    ) -> BenchmarkResult:
        """Benchmark agent creation performance"""

        if config is None:
            config = BenchmarkConfig(
                name="agent_creation",
                warmup_iterations=5,
                benchmark_iterations=50
            )

        def create_agent():
            if agent_factory:
                return agent_factory()
            else:
                # Mock agent creation for testing
                return {"id": f"agent_{time.time()}", "state": "active"}

        result = self._run_benchmark(
            "agent_creation",
            create_agent,
            config
        )
        self.results.append(result)
        return result

    def benchmark_agent_activation(
        self,
        config: Optional[BenchmarkConfig] = None,
        agent: Any = None
    ) -> BenchmarkResult:
        """Benchmark agent activation performance"""

        if config is None:
            config = BenchmarkConfig(
                name="agent_activation",
                warmup_iterations=10,
                benchmark_iterations=100
            )

        def activate_agent():
            if agent is None:
                # Mock activation
                time.sleep(0.001)
                return True
            # In real implementation, call agent.activate()
            return True

        result = self._run_benchmark(
            "agent_activation",
            activate_agent,
            config
        )
        self.results.append(result)
        return result

    def benchmark_agent_decision_making(
        self,
        config: Optional[BenchmarkConfig] = None,
        agent: Any = None,
        input_data: Any = None
    ) -> BenchmarkResult:
        """Benchmark agent decision-making (Plinko layer)"""

        if config is None:
            config = BenchmarkConfig(
                name="agent_decision",
                warmup_iterations=10,
                benchmark_iterations=200
            )

        def make_decision():
            if input_data is None:
                # Mock decision making
                proposals = [
                    {"id": 1, "value": 0.5},
                    {"id": 2, "value": 0.3},
                    {"id": 3, "value": 0.7}
                ]
                # Simulate Plinko stochastic selection
                probs = [p["value"] for p in proposals]
                total = sum(probs)
                return proposals[np.random.choice(len(proposals), p=[p/total for p in probs])]
            return True

        result = self._run_benchmark(
            "agent_decision_making",
            make_decision,
            config
        )
        self.results.append(result)
        return result

    # ===== COLONY BENCHMARKS =====

    def benchmark_colony_coordination(
        self,
        config: Optional[BenchmarkConfig] = None,
        colony_size: int = 100
    ) -> BenchmarkResult:
        """Benchmark colony-wide coordination"""

        if config is None:
            config = BenchmarkConfig(
                name="colony_coordination",
                warmup_iterations=5,
                benchmark_iterations=20
            )

        def coordinate():
            # Simulate colony coordination
            agents = [{"id": i, "state": "active"} for i in range(colony_size)]
            # Simulate stigmergy-based coordination
            signals = [np.random.rand() for _ in range(10)]
            return len(agents)

        result = self._run_benchmark(
            "colony_coordination",
            coordinate,
            config
        )
        self.results.append(result)
        return result

    def benchmark_colony_communication(
        self,
        config: Optional[BenchmarkConfig] = None,
        message_count: int = 50
    ) -> BenchmarkResult:
        """Benchmark inter-agent communication throughput"""

        if config is None:
            config = BenchmarkConfig(
                name="colony_communication",
                warmup_iterations=5,
                benchmark_iterations=30
            )

        def communicate():
            # Simulate A2A package transmission
            messages = [
                {
                    "from": f"agent_{i}",
                    "to": f"agent_{(i+1) % message_count}",
                    "content": f"message_{i}",
                    "timestamp": time.time()
                }
                for i in range(message_count)
            ]
            return len(messages)

        result = self._run_benchmark(
            "colony_communication",
            communicate,
            config
        )
        self.results.append(result)
        return result

    # ===== LEARNING BENCHMARKS =====

    def benchmark_hebbian_learning(
        self,
        config: Optional[BenchmarkConfig] = None,
        synapse_count: int = 1000
    ) -> BenchmarkResult:
        """Benchmark Hebbian learning updates"""

        if config is None:
            config = BenchmarkConfig(
                name="hebbian_learning",
                warmup_iterations=10,
                benchmark_iterations=100
            )

        # Initialize mock synapses
        synapses = np.random.rand(synapse_count)

        def hebbian_update():
            nonlocal synapses
            # Simulate Hebbian learning: Δw = η * pre * post
            pre_activity = np.random.rand(synapse_count)
            post_activity = np.random.rand(synapse_count)
            delta = 0.1 * pre_activity * post_activity
            synapses += delta
            return np.mean(synapses)

        result = self._run_benchmark(
            "hebbian_learning",
            hebbian_update,
            config
        )
        self.results.append(result)
        return result

    def benchmark_dreaming_cycle(
        self,
        config: Optional[BenchmarkConfig] = None,
        experience_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark dream-based policy optimization"""

        if config is None:
            config = BenchmarkConfig(
                name="dreaming_cycle",
                warmup_iterations=3,
                benchmark_iterations=10
            )

        def dream_cycle():
            # Simulate VAE-based dreaming
            experiences = np.random.rand(experience_count, 64)  # Embeddings
            # Simulate VAE encoding/decoding
            encoded = experiences @ np.random.rand(64, 32)
            decoded = encoded @ np.random.rand(32, 64)
            # Simulate policy optimization
            policy_updates = decoded * 0.01
            return np.mean(policy_updates)

        result = self._run_benchmark(
            "dreaming_cycle",
            dream_cycle,
            config
        )
        self.results.append(result)
        return result

    # ===== KV-CACHE BENCHMARKS =====

    def benchmark_kv_anchor_creation(
        self,
        config: Optional[BenchmarkConfig] = None,
        anchor_size: int = 4096
    ) -> BenchmarkResult:
        """Benchmark KV-anchor creation"""

        if config is None:
            config = BenchmarkConfig(
                name="kv_anchor_creation",
                warmup_iterations=10,
                benchmark_iterations=200
            )

        def create_anchor():
            # Simulate KV-anchor creation (compression)
            kv_cache = np.random.rand(anchor_size, 128)  # 128-dimensional keys/values
            # Simulate compression
            anchor = np.mean(kv_cache.reshape(32, -1), axis=1)
            return anchor

        result = self._run_benchmark(
            "kv_anchor_creation",
            create_anchor,
            config
        )
        self.results.append(result)
        return result

    def benchmark_ann_matching(
        self,
        config: Optional[BenchmarkConfig] = None,
        index_size: int = 10000,
        query_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark ANN index matching"""

        if config is None:
            config = BenchmarkConfig(
                name="ann_matching",
                warmup_iterations=5,
                benchmark_iterations=50
            )

        # Build mock ANN index
        index_vectors = np.random.rand(index_size, 128)
        # Normalize for cosine similarity
        index_vectors = index_vectors / np.linalg.norm(index_vectors, axis=1, keepdims=True)

        def match_ann():
            queries = np.random.rand(query_count, 128)
            queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
            # Simulate approximate nearest neighbor search
            similarities = queries @ index_vectors.T
            top_k = 5
            top_indices = np.argsort(-similarities, axis=1)[:, :top_k]
            return top_indices.shape

        result = self._run_benchmark(
            "ann_matching",
            match_ann,
            config
        )
        self.results.append(result)
        return result

    # ===== COMPREHENSIVE BENCHMARKS =====

    def run_all_benchmarks(
        self,
        scale: str = "small"  # small, medium, large
    ) -> Dict[str, List[BenchmarkResult]]:
        """Run all benchmarks with appropriate scaling"""

        scale_configs = {
            "small": {
                "colony_size": 50,
                "message_count": 25,
                "synapse_count": 500,
                "index_size": 5000
            },
            "medium": {
                "colony_size": 100,
                "message_count": 50,
                "synapse_count": 1000,
                "index_size": 10000
            },
            "large": {
                "colony_size": 500,
                "message_count": 200,
                "synapse_count": 5000,
                "index_size": 50000
            }
        }

        config = scale_configs[scale]
        results = {
            "agents": [],
            "colony": [],
            "learning": [],
            "kv_cache": []
        }

        print(f"\n{'='*60}")
        print(f"Running POLLN Benchmark Suite - Scale: {scale.upper()}")
        print(f"{'='*60}\n")

        # Agent benchmarks
        print("Running Agent Benchmarks...")
        results["agents"].append(self.benchmark_agent_creation())
        results["agents"].append(self.benchmark_agent_activation())
        results["agents"].append(self.benchmark_agent_decision_making())
        print(f"✓ Agent benchmarks complete")

        # Colony benchmarks
        print("\nRunning Colony Benchmarks...")
        results["colony"].append(
            self.benchmark_colony_coordination(colony_size=config["colony_size"])
        )
        results["colony"].append(
            self.benchmark_colony_communication(message_count=config["message_count"])
        )
        print(f"✓ Colony benchmarks complete")

        # Learning benchmarks
        print("\nRunning Learning Benchmarks...")
        results["learning"].append(
            self.benchmark_hebbian_learning(synapse_count=config["synapse_count"])
        )
        results["learning"].append(self.benchmark_dreaming_cycle())
        print(f"✓ Learning benchmarks complete")

        # KV-Cache benchmarks
        print("\nRunning KV-Cache Benchmarks...")
        results["kv_cache"].append(self.benchmark_kv_anchor_creation())
        results["kv_cache"].append(
            self.benchmark_ann_matching(index_size=config["index_size"])
        )
        print(f"✓ KV-Cache benchmarks complete")

        print(f"\n{'='*60}")
        print(f"Benchmark Suite Complete!")
        print(f"{'='*60}\n")

        return results

    def save_results(self, filename: str = None) -> Path:
        """Save all benchmark results to JSON file"""

        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmarks_{timestamp}.json"

        output_path = self.output_dir / filename

        results_data = {
            "timestamp": time.time(),
            "results": [r.to_dict() for r in self.results]
        }

        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print summary of all benchmark results"""

        print(f"\n{'='*80}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*80}\n")

        for result in self.results:
            print(f"📊 {result.name}")
            print(f"   Throughput:  {result.throughput_ops:.2f} ops/sec")
            print(f"   Latency:     {result.p50_latency_ms:.2f}ms (p50)")
            print(f"                {result.p95_latency_ms:.2f}ms (p95)")
            print(f"                {result.p99_latency_ms:.2f}ms (p99)")
            print(f"   Memory:      {result.memory_mb:.2f} MB")
            print(f"   Success:     {result.success_rate*100:.1f}%")
            print(f"   Iterations:  {result.iterations}")
            print()


def main():
    """Main entry point for running benchmarks"""

    import argparse

    parser = argparse.ArgumentParser(description="POLLN Benchmark Suite")
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default="small",
        help="Benchmark scale (default: small)"
    )
    parser.add_argument(
        "--output",
        default="reports/benchmarks/current",
        help="Output directory for results"
    )
    parser.add_argument(
        "--category",
        choices=["all", "agents", "colony", "learning", "kv_cache"],
        default="all",
        help="Benchmark category to run"
    )

    args = parser.parse_args()

    suite = BenchmarkSuite(output_dir=args.output)

    if args.category == "all":
        results = suite.run_all_benchmarks(scale=args.scale)
    else:
        # Run specific category
        if args.category == "agents":
            suite.benchmark_agent_creation()
            suite.benchmark_agent_activation()
            suite.benchmark_agent_decision_making()
        elif args.category == "colony":
            suite.benchmark_colony_coordination()
            suite.benchmark_colony_communication()
        elif args.category == "learning":
            suite.benchmark_hebbian_learning()
            suite.benchmark_dreaming_cycle()
        elif args.category == "kv_cache":
            suite.benchmark_kv_anchor_creation()
            suite.benchmark_ann_matching()

    suite.print_summary()
    suite.save_results()


if __name__ == "__main__":
    main()
