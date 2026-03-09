"""
Cache Sizing Optimization for POLLN

This script finds optimal cache sizes by simulating different cache capacities
and measuring hit rate vs cost tradeoffs.

Key questions:
- What cache size yields the best hit rate per dollar?
- Where is the "knee" of the curve (diminishing returns)?
- How does optimal size vary by workload?
- What's the marginal benefit of increasing size?

Metrics:
- Hit rate (primary)
- Memory cost
- Hit rate per MB (efficiency)
- Knee point detection
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from collections import OrderedDict

class WorkloadType(Enum):
    """Types of workloads"""
    CONVERSATION = "conversation"  # Dialogue-heavy
    CODING = "coding"              # Code-heavy with long contexts
    ANALYSIS = "analysis"          # Document analysis
    GENERAL = "general"            # Mixed workload

@dataclass
class SizingResult:
    """Results from cache sizing experiment"""
    workload: WorkloadType
    cache_size_bytes: int
    cache_size_mb: float
    hit_rate: float
    miss_rate: float
    total_accesses: int
    total_hits: int
    total_misses: int
    hit_rate_per_mb: float
    marginal_benefit: float  # Additional hit rate from doubling size
    is_knee: bool  # Is this the knee point?

class LRUCache:
    """Simple LRU cache for simulation"""

    def __init__(self, capacity: int):
        """
        Initialize LRU cache

        Args:
            capacity: Maximum capacity in bytes
        """
        self.capacity = capacity
        self.current_size = 0
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def access(self, key: str, size: int) -> bool:
        """
        Access cache

        Args:
            key: Access key
            size: Entry size in bytes

        Returns:
            True if hit, False if miss
        """
        if key in self.cache:
            # Hit
            self.hits += 1
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return True
        else:
            # Miss
            self.misses += 1

            # Evict if necessary
            while self.current_size + size > self.capacity and self.cache:
                lru_key, lru_size = self.cache.popitem(last=False)
                self.current_size -= lru_size

            # Insert if fits
            if size <= self.capacity:
                self.cache[key] = size
                self.current_size += size

            return False

    def get_hit_rate(self) -> float:
        """Get current hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

def generate_workload_trace(
    workload: WorkloadType,
    num_accesses: int = 100000
) -> List[Tuple[str, int]]:
    """
    Generate access trace for specific workload

    Args:
        workload: Type of workload
        num_accesses: Number of accesses to generate

    Returns:
        List of (key, size) tuples
    """
    trace = []
    np.random.seed(42)

    if workload == WorkloadType.CONVERSATION:
        # Dialogue-heavy: repeated references to recent context
        # with occasional topic shifts
        current_context_size = 0
        max_context = 50

        for i in range(num_accesses):
            # 30% chance of topic shift
            if np.random.random() < 0.3 or current_context_size >= max_context:
                # Topic shift
                current_context_size = 0
                topic_id = np.random.randint(0, 100)
                key = f"conv_topic_{topic_id}"
            else:
                # Continue current topic
                if trace:
                    prev_key = trace[-1][0]
                    if 'topic' in prev_key:
                        topic_id = int(prev_key.split('_')[2])
                        # Reference recent tokens in same topic
                        token_offset = np.random.randint(0, min(20, current_context_size))
                        key = f"conv_topic_{topic_id}_token_{token_offset}"
                    else:
                        key = f"conv_token_{i}"
                else:
                    key = f"conv_token_{i}"

                current_context_size += 1

            # Variable size (token embeddings vary)
            size = np.random.randint(512, 2048)
            trace.append((key, size))

    elif workload == WorkloadType.CODING:
        # Code-heavy: long-lived references to functions, classes
        # with high temporal locality

        # Define some code entities
        functions = [f"func_{i}" for i in range(50)]
        classes = [f"class_{i}" for i in range(20)]
        variables = [f"var_{i}" for i in range(100)]

        # Current "scope"
        current_function = None
        current_class = None

        for i in range(num_accesses):
            # Determine access pattern
            rand = np.random.random()

            if rand < 0.4:
                # Access in current function scope
                if current_function:
                    key = f"{current_class}.{current_function}.{np.random.choice(variables[:20])}"
                else:
                    key = np.random.choice(functions)
            elif rand < 0.7:
                # Access current class
                if current_class:
                    key = f"{current_class}.{np.random.choice(functions[:10])}"
                else:
                    key = np.random.choice(classes)
            elif rand < 0.9:
                # Switch function
                current_function = np.random.choice(functions)
                key = current_function
            else:
                # Switch class (major context switch)
                current_class = np.random.choice(classes)
                current_function = np.random.choice(functions)
                key = current_class

            # Code has larger embeddings (syntax trees, etc.)
            size = np.random.randint(1024, 4096)
            trace.append((key, size))

    elif workload == WorkloadType.ANALYSIS:
        # Document analysis: sequential reads with some revisits
        # and cross-references

        # Simulate document structure
        documents = [f"doc_{i}" for i in range(20)]
        sections_per_doc = 10

        current_doc = None
        current_section = 0

        for i in range(num_accesses):
            rand = np.random.random()

            if rand < 0.6:
                # Sequential read within section
                if current_doc is None:
                    current_doc = np.random.choice(documents)
                key = f"{current_doc}_section_{current_section}_token_{np.random.randint(0, 100)}"
            elif rand < 0.8:
                # Move to next section
                current_section = (current_section + 1) % sections_per_doc
                key = f"{current_doc}_section_{current_section}_header"
            elif rand < 0.95:
                # Cross-reference to another section
                ref_section = np.random.randint(0, sections_per_doc)
                key = f"{current_doc}_section_{ref_section}_ref"
            else:
                # Switch to new document
                current_doc = np.random.choice(documents)
                current_section = 0
                key = f"{current_doc}_header"

            # Document analysis has medium-sized chunks
            size = np.random.randint(768, 1536)
            trace.append((key, size))

    elif workload == WorkloadType.GENERAL:
        # Mixed workload - combination of all patterns
        workloads = [
            WorkloadType.CONVERSATION,
            WorkloadType.CODING,
            WorkloadType.ANALYSIS
        ]

        # Switch workload every 1000 accesses
        for i in range(num_accesses):
            workload_idx = (i // 1000) % len(workloads)
            current_workload = workloads[workload_idx]

            # Generate single access
            if current_workload == WorkloadType.CONVERSATION:
                key = f"conv_{i % 100}"
            elif current_workload == WorkloadType.CODING:
                key = f"code_func_{i % 50}"
            else:
                key = f"doc_{i % 20}_section_{i % 10}"

            size = np.random.randint(512, 2048)
            trace.append((key, size))

    return trace

def simulate_cache_sizes(
    workload: WorkloadType,
    cache_sizes: List[int] = None
) -> List[SizingResult]:
    """
    Simulate different cache sizes for a workload

    Args:
        workload: Type of workload
        cache_sizes: List of cache sizes to test (bytes)

    Returns:
        List of sizing results
    """
    if cache_sizes is None:
        # Test from 1MB to 1GB, exponential scale
        cache_sizes = [
            1024 * 1024 * size_mb
            for size_mb in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
        ]

    # Generate trace
    trace = generate_workload_trace(workload, num_accesses=100000)

    results = []

    for cache_size in cache_sizes:
        cache = LRUCache(cache_size)

        # Run trace
        for key, size in trace:
            cache.access(key, size)

        hit_rate = cache.get_hit_rate()
        cache_size_mb = cache_size / (1024 * 1024)

        result = SizingResult(
            workload=workload,
            cache_size_bytes=cache_size,
            cache_size_mb=cache_size_mb,
            hit_rate=hit_rate,
            miss_rate=1 - hit_rate,
            total_accesses=cache.hits + cache.misses,
            total_hits=cache.hits,
            total_misses=cache.misses,
            hit_rate_per_mb=hit_rate / cache_size_mb if cache_size_mb > 0 else 0,
            marginal_benefit=0.0,  # Will compute later
            is_knee=False  # Will compute later
        )

        results.append(result)

        print(f"  Size: {cache_size_mb:6.1f}MB | Hit Rate: {hit_rate:.3f} | "
              f"Efficiency: {result.hit_rate_per_mb:.4f}")

    # Compute marginal benefits
    for i in range(1, len(results)):
        prev_size = results[i-1].cache_size_mb
        curr_size = results[i].cache_size_mb
        prev_hit = results[i-1].hit_rate
        curr_hit = results[i].hit_rate

        # Additional hit rate from doubling (roughly)
        size_ratio = curr_size / prev_size
        marginal_hit = curr_hit - prev_hit
        marginal_benefit = marginal_hit / (size_ratio - 1) if size_ratio > 1 else 0

        results[i].marginal_benefit = marginal_benefit

    return results

def find_knee_point(results: List[SizingResult]) -> int:
    """
    Find the knee point (diminishing returns)

    Uses the "kneedle" algorithm - find point of maximum curvature

    Args:
        results: Sizing results

    Returns:
        Index of knee point
    """
    if len(results) < 3:
        return len(results) // 2

    # Extract points
    x = np.array([r.cache_size_mb for r in results])
    y = np.array([r.hit_rate for r in results])

    # Normalize to [0, 1]
    x_norm = (x - x.min()) / (x.max() - x.min() + 1e-8)
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-8)

    # Compute distances from the line (0, 0) to (1, 1)
    # Point with maximum distance is the knee
    distances = []
    for i in range(len(x_norm)):
        # Distance from point to line x = y
        dist = abs(x_norm[i] - y_norm[i]) / np.sqrt(2)
        distances.append(dist)

    knee_idx = int(np.argmax(distances))
    results[knee_idx].is_knee = True

    return knee_idx

def run_sizing_experiments() -> Dict[str, List[SizingResult]]:
    """
    Run cache sizing experiments for all workloads

    Returns:
        Dictionary of results by workload
    """
    print("="*70)
    print("CACHE SIZING OPTIMIZATION")
    print("="*70)

    workloads = [
        WorkloadType.CONVERSATION,
        WorkloadType.CODING,
        WorkloadType.ANALYSIS,
        WorkloadType.GENERAL
    ]

    all_results = {}

    for workload in workloads:
        print(f"\n{'='*70}")
        print(f"Workload: {workload.value.upper()}")
        print(f"{'='*70}")

        results = simulate_cache_sizes(workload)

        # Find knee point
        knee_idx = find_knee_point(results)
        knee = results[knee_idx]

        print(f"\n*** KNEE POINT ***")
        print(f"Size: {knee.cache_size_mb:.1f}MB")
        print(f"Hit Rate: {knee.hit_rate:.3f}")
        print(f"Efficiency: {knee.hit_rate_per_mb:.4f} per MB")

        all_results[workload.value] = results

    return all_results

def find_optimal_sizes(all_results: Dict[str, List[SizingResult]]) -> Dict[str, Any]:
    """
    Find optimal cache sizes for each workload and overall

    Args:
        all_results: Results from all workloads

    Returns:
        Optimal size recommendations
    """
    print("\n" + "="*70)
    print("OPTIMAL CACHE SIZE RECOMMENDATIONS")
    print("="*70)

    optimal_by_workload = {}

    for workload, results in all_results.items():
        # Find knee point
        knee_idx = find_knee_point(results)
        knee = results[knee_idx]

        optimal_by_workload[workload] = {
            'size_mb': knee.cache_size_mb,
            'size_bytes': knee.cache_size_bytes,
            'hit_rate': knee.hit_rate,
            'efficiency': knee.hit_rate_per_mb
        }

        print(f"\n{workload.upper()}:")
        print(f"  Optimal Size: {knee.cache_size_mb:.1f}MB")
        print(f"  Expected Hit Rate: {knee.hit_rate:.3f}")
        print(f"  Efficiency: {knee.hit_rate_per_mb:.4f} per MB")

    # Find overall optimal (average across workloads)
    avg_optimal_size = np.mean([
        opt['size_bytes']
        for opt in optimal_by_workload.values()
    ])

    # Find closest cache size in results
    all_sizes = sorted(set(
        r.cache_size_bytes
        for results in all_results.values()
        for r in results
    ))

    closest_size = min(all_sizes, key=lambda s: abs(s - avg_optimal_size))

    print(f"\n{'='*70}")
    print("OVERALL RECOMMENDATION:")
    print(f"  Optimal Size: {closest_size / (1024*1024):.1f}MB")
    print(f"  (Average across workloads)")

    return {
        'by_workload': optimal_by_workload,
        'overall': {
            'size_bytes': closest_size,
            'size_mb': closest_size / (1024 * 1024)
        }
    }

def calculate_cost_benefit(
    results: Dict[str, List[SizingResult]],
    cost_per_mb: float = 0.01  # Arbitrary cost unit
) -> Dict[str, Any]:
    """
    Calculate cost-benefit analysis

    Args:
        results: Sizing results
        cost_per_mb: Cost per MB of cache

    Returns:
        Cost-benefit metrics
    """
    print("\n" + "="*70)
    print("COST-BENEFIT ANALYSIS")
    print("="*70)

    analysis = {}

    for workload, sizing_results in results.items():
        # Find point with best hit rate per cost
        best_idx = 0
        best_value = 0

        for i, r in enumerate(sizing_results):
            cost = r.cache_size_mb * cost_per_mb
            value = r.hit_rate / cost if cost > 0 else 0

            if value > best_value:
                best_value = value
                best_idx = i

        best = sizing_results[best_idx]

        analysis[workload] = {
            'optimal_size_mb': best.cache_size_mb,
            'hit_rate': best.hit_rate,
            'cost': best.cache_size_mb * cost_per_mb,
            'value_per_cost': best_value
        }

        print(f"\n{workload.upper()}:")
        print(f"  Best value at: {best.cache_size_mb:.1f}MB")
        print(f"  Hit Rate: {best.hit_rate:.3f}")
        print(f"  Cost: {best.cache_size_mb * cost_per_mb:.2f}")
        print(f"  Value/Cost: {best_value:.4f}")

    return analysis

def main():
    """Main optimization loop"""
    os.makedirs('simulations/optimization/memory/results', exist_ok=True)

    # Run experiments
    all_results = run_sizing_experiments()

    # Find optimal sizes
    optimal = find_optimal_sizes(all_results)

    # Cost-benefit analysis
    cost_benefit = calculate_cost_benefit(all_results)

    # Prepare output
    output = {
        'results': {
            workload: [
                {
                    'cache_size_mb': r.cache_size_mb,
                    'cache_size_bytes': r.cache_size_bytes,
                    'hit_rate': r.hit_rate,
                    'miss_rate': r.miss_rate,
                    'total_accesses': r.total_accesses,
                    'total_hits': r.total_hits,
                    'total_misses': r.total_misses,
                    'hit_rate_per_mb': r.hit_rate_per_mb,
                    'marginal_benefit': r.marginal_benefit,
                    'is_knee': r.is_knee
                }
                for r in results
            ]
            for workload, results in all_results.items()
        },
        'optimal_sizes': optimal,
        'cost_benefit': cost_benefit
    }

    # Save results
    with open('simulations/optimization/memory/results/sizing_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("Results saved to: simulations/optimization/memory/results/sizing_results.json")
    print("="*70)

    return optimal

if __name__ == '__main__':
    main()
