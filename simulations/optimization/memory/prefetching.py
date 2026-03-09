"""
Prefetching Strategy Optimization for POLLN

This script evaluates different prefetching strategies to find optimal
approaches for KV-cache prefetching.

Prefetch strategies tested:
- None (baseline)
- Always (aggressive)
- Probability-based (threshold)
- Markov chain prediction
- ML-based (simulated)

Metrics:
- Prefetch accuracy
- Memory overhead
- Latency reduction
- Prefetch efficiency (useful prefetches / total)
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os
from collections import defaultdict, deque

class PrefetchStrategy(Enum):
    """Prefetching strategies"""
    NONE = "none"
    ALWAYS = "always"
    PROBABILITY = "probability"
    MARKOV = "markov"
    ML_PREDICTIVE = "ml_predictive"
    HYBRID = "hybrid"

@dataclass
class PrefetchResult:
    """Results from prefetch experiment"""
    strategy: PrefetchStrategy
    accuracy: float  # Correct predictions / total predictions
    coverage: float  # Actual prefetch hits / total accesses
    memory_overhead: float  # Extra memory used
    latency_reduction: float  # Time saved
    prefetch_efficiency: float  # Useful prefetches / total prefetches
    total_prefetches: int
    useful_prefetches: int
    wasted_prefetches: int
    parameters: Dict[str, Any]

class MarkovModel:
    """Markov chain for predicting next accesses"""

    def __init__(self, order: int = 1):
        """
        Initialize Markov model

        Args:
            order: Order of Markov chain (1 = next state depends on current)
        """
        self.order = order
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.context = deque(maxlen=order)

    def train(self, sequence: List[str]):
        """Train on sequence of accesses"""
        for i in range(len(sequence) - self.order):
            # Build context
            context = tuple(sequence[i:i + self.order])
            next_item = sequence[i + self.order]

            self.transitions[context][next_item] += 1

    def predict_next(self, context: List[str], top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predict next items given context

        Args:
            context: Recent access history
            top_k: Number of predictions to return

        Returns:
            List of (item, probability) tuples
        """
        if len(context) < self.order:
            return []

        context_tuple = tuple(context[-self.order:])

        if context_tuple not in self.transitions:
            return []

        # Get transition counts
        transitions = self.transitions[context_tuple]
        total = sum(transitions.values())

        # Sort by count and return top k
        predictions = [
            (item, count / total)
            for item, count in sorted(transitions.items(), key=lambda x: -x[1])
        ][:top_k]

        return predictions

class PrefetchSimulator:
    """Simulates cache with prefetching"""

    def __init__(
        self,
        cache_size: int,
        strategy: PrefetchStrategy,
        prefetch_window: int = 5,
        prefetch_threshold: float = 0.3,
        markov_order: int = 2
    ):
        """
        Initialize prefetch simulator

        Args:
            cache_size: Maximum cache size in bytes
            strategy: Prefetch strategy
            prefetch_window: Number of items to prefetch
            prefetch_threshold: Probability threshold for prefetch
            markov_order: Order of Markov model
        """
        self.cache_size = cache_size
        self.strategy = strategy
        self.prefetch_window = prefetch_window
        self.prefetch_threshold = prefetch_threshold

        # Cache state
        self.cache = {}  # key -> (value, size, timestamp)
        self.current_size = 0

        # Statistics
        self.stats = {
            'accesses': 0,
            'hits': 0,
            'misses': 0,
            'prefetches': 0,
            'prefetch_hits': 0,
            'prefetch_misses': 0,
            'evictions': 0
        }

        # Access history for Markov model
        self.access_history = []

        # Markov model (trained on trace)
        self.markov_model = None

        # Timing
        self.total_latency = 0.0
        self.prefetch_latency = 0.0

    def train_markov(self, trace: List[Tuple[str, int]]):
        """Train Markov model on trace"""
        if self.strategy in [PrefetchStrategy.MARKOV, PrefetchStrategy.HYBRID]:
            self.markov_model = MarkovModel(order=2)
            keys = [key for key, _ in trace[:len(trace)//2]]  # Train on first half
            self.markov_model.train(keys)

    def access(self, key: str, size: int) -> bool:
        """
        Access cache entry

        Args:
            key: Access key
            size: Entry size in bytes

        Returns:
            True if hit, False if miss
        """
        self.stats['accesses'] += 1
        self.access_history.append(key)

        # Check cache
        if key in self.cache:
            # Hit
            self.stats['hits'] += 1
            self.total_latency += 0.001  # 1ms for cache hit

            # Update timestamp (for LRU)
            value, entry_size, _ = self.cache[key]
            self.cache[key] = (value, entry_size, self.stats['accesses'])

            # Prefetch next items
            if self.strategy != PrefetchStrategy.NONE:
                self._prefetch(key, trace_context=self.access_history)

            return True
        else:
            # Miss
            self.stats['misses'] += 1
            self.total_latency += 0.010  # 10ms for cache miss

            # Check if it was prefetched
            if key in getattr(self, 'prefetch_buffer', {}):
                self.stats['prefetch_hits'] += 1
            else:
                self.stats['prefetch_misses'] += 1

            # Insert into cache
            self._insert(key, size)

            # Prefetch next items
            if self.strategy != PrefetchStrategy.NONE:
                self._prefetch(key, trace_context=self.access_history)

            return False

    def _insert(self, key: str, size: int):
        """Insert item into cache"""
        # Evict if necessary
        while self.current_size + size > self.cache_size and self.cache:
            # LRU eviction
            lru_key = min(self.cache.keys(), key=lambda k: self.cache[k][2])
            self._evict(lru_key)

        # Insert
        self.cache[key] = (None, size, self.stats['accesses'])  # Value not stored in sim
        self.current_size += size

    def _evict(self, key: str):
        """Evict item from cache"""
        if key in self.cache:
            _, size, _ = self.cache[key]
            del self.cache[key]
            self.current_size -= size
            self.stats['evictions'] += 1

    def _prefetch(self, current_key: str, trace_context: List[str]):
        """Prefetch next items based on strategy"""
        if self.strategy == PrefetchStrategy.ALWAYS:
            self._prefetch_always(current_key)

        elif self.strategy == PrefetchStrategy.PROBABILITY:
            self._prefetch_probability(current_key)

        elif self.strategy == PrefetchStrategy.MARKOV:
            self._prefetch_markov(trace_context)

        elif self.strategy == PrefetchStrategy.ML_PREDICTIVE:
            self._prefetch_ml(trace_context)

        elif self.strategy == PrefetchStrategy.HYBRID:
            self._prefetch_hybrid(trace_context)

    def _prefetch_always(self, current_key: str):
        """Always prefetch next sequential items"""
        # Extract numeric part and prefetch next few
        try:
            parts = current_key.split('_')
            if len(parts) > 0 and parts[-1].isdigit():
                current_num = int(parts[-1])

                for i in range(1, self.prefetch_window + 1):
                    next_key = '_'.join(parts[:-1]) + f'_{current_num + i}'
                    self._do_prefetch(next_key, 1024)  # Assume size
        except:
            pass

    def _prefetch_probability(self, current_key: str):
        """Prefetch based on probability threshold"""
        if np.random.random() < self.prefetch_threshold:
            self._prefetch_always(current_key)

    def _prefetch_markov(self, trace_context: List[str]):
        """Prefetch based on Markov model predictions"""
        if self.markov_model is None:
            return

        predictions = self.markov_model.predict_next(
            trace_context[-10:],
            top_k=self.prefetch_window
        )

        for key, prob in predictions:
            if prob >= self.prefetch_threshold:
                self._do_prefetch(key, 1024)

    def _prefetch_ml(self, trace_context: List[str]):
        """
        Simulated ML-based prefetching

        In reality, this would use a trained model.
        Here we simulate with access frequency.
        """
        # Count recent accesses
        recent = trace_context[-50:]
        freq = defaultdict(int)

        for key in recent:
            freq[key] += 1

        # Prefetch most frequently accessed items not in cache
        sorted_items = sorted(freq.items(), key=lambda x: -x[1])

        for key, _ in sorted_items[:self.prefetch_window]:
            if key not in self.cache:
                self._do_prefetch(key, 1024)

    def _prefetch_hybrid(self, trace_context: List[str]):
        """Hybrid: combine Markov and frequency-based"""
        # Use Markov if available, otherwise fall back to frequency
        if self.markov_model and len(trace_context) >= 2:
            self._prefetch_markov(trace_context)
        else:
            self._prefetch_ml(trace_context)

    def _do_prefetch(self, key: str, size: int):
        """Actually perform prefetch"""
        if key in self.cache:
            return

        self.stats['prefetches'] += 1
        self.prefetch_latency += 0.002  # 2ms prefetch cost

        # Insert into cache (will evict if necessary)
        self._insert(key, size)

        # Track in prefetch buffer
        if not hasattr(self, 'prefetch_buffer'):
            self.prefetch_buffer = {}

        self.prefetch_buffer[key] = True

    def get_results(self) -> PrefetchResult:
        """Get prefetch results"""
        total_accesses = self.stats['accesses']
        total_prefetches = self.stats['prefetches']

        # Accuracy: correct predictions / total predictions
        accuracy = self.stats['prefetch_hits'] / total_prefetches if total_prefetches > 0 else 0

        # Coverage: accesses served by prefetch
        coverage = self.stats['prefetch_hits'] / total_accesses if total_accesses > 0 else 0

        # Memory overhead
        memory_overhead = self.stats['prefetches'] / self.cache_size if self.cache_size > 0 else 0

        # Latency reduction (compared to always miss)
        baseline_latency = total_accesses * 0.010  # 10ms per miss
        actual_latency = self.total_latency
        latency_reduction = (baseline_latency - actual_latency) / baseline_latency

        # Efficiency: useful prefetches / total prefetches
        useful_prefetches = self.stats['prefetch_hits']
        wasted_prefetches = total_prefetches - useful_prefetches
        efficiency = useful_prefetches / total_prefetches if total_prefetches > 0 else 0

        return PrefetchResult(
            strategy=self.strategy,
            accuracy=accuracy,
            coverage=coverage,
            memory_overhead=memory_overhead,
            latency_reduction=latency_reduction,
            prefetch_efficiency=efficiency,
            total_prefetches=total_prefetches,
            useful_prefetches=useful_prefetches,
            wasted_prefetches=wasted_prefetches,
            parameters={
                'prefetch_window': self.prefetch_window,
                'prefetch_threshold': self.prefetch_threshold
            }
        )

def generate_trace(
    pattern: str = "mixed",
    num_accesses: int = 10000
) -> List[Tuple[str, int]]:
    """
    Generate access trace for prefetch testing

    Args:
        pattern: Access pattern (sequential, random, mixed)
        num_accesses: Number of accesses

    Returns:
        List of (key, size) tuples
    """
    trace = []
    np.random.seed(42)

    if pattern == "sequential":
        # Highly predictable sequential access
        for i in range(num_accesses):
            key = f"seq_{i // 100}_{i % 100}"
            size = np.random.randint(512, 2048)
            trace.append((key, size))

    elif pattern == "random":
        # Random access (hard to predict)
        for i in range(num_accesses):
            key = f"rand_{np.random.randint(0, 1000)}"
            size = np.random.randint(512, 2048)
            trace.append((key, size))

    elif pattern == "mixed":
        # Mixed pattern - realistic
        for i in range(num_accesses):
            if i % 500 < 300:  # 60% sequential
                key = f"seq_{i // 100}_{i % 100}"
            elif i % 500 < 450:  # 30% repetitive
                key = f"repeat_{(i // 50) % 20}_{i % 10}"
            else:  # 10% random
                key = f"rand_{np.random.randint(0, 100)}"

            size = np.random.randint(512, 2048)
            trace.append((key, size))

    elif pattern == "conversation":
        # Conversation-like pattern
        topic = 0
        tokens_in_topic = 0

        for i in range(num_accesses):
            if tokens_in_topic > 100 or np.random.random() < 0.05:
                # Topic shift
                topic = np.random.randint(0, 50)
                tokens_in_topic = 0

            key = f"topic_{topic}_token_{tokens_in_topic}"
            size = np.random.randint(512, 2048)
            trace.append((key, size))
            tokens_in_topic += 1

    return trace

def run_prefetch_experiments() -> Dict[str, List[PrefetchResult]]:
    """
    Run prefetching experiments

    Returns:
        Dictionary of results by pattern
    """
    print("="*70)
    print("PREFETCHING STRATEGY OPTIMIZATION")
    print("="*70)

    patterns = ["sequential", "random", "mixed", "conversation"]
    strategies = [
        PrefetchStrategy.NONE,
        PrefetchStrategy.ALWAYS,
        PrefetchStrategy.PROBABILITY,
        PrefetchStrategy.MARKOV,
        PrefetchStrategy.ML_PREDICTIVE,
        PrefetchStrategy.HYBRID
    ]

    all_results = {}

    for pattern in patterns:
        print(f"\n{'='*70}")
        print(f"Pattern: {pattern.upper()}")
        print(f"{'='*70}")

        # Generate trace
        trace = generate_trace(pattern, num_accesses=10000)

        pattern_results = []

        for strategy in strategies:
            print(f"\nTesting {strategy.value}...", end=" ")

            # Test different window sizes
            for window_size in [3, 5, 10]:
                sim = PrefetchSimulator(
                    cache_size=10 * 1024 * 1024,  # 10MB
                    strategy=strategy,
                    prefetch_window=window_size,
                    prefetch_threshold=0.3
                )

                # Train Markov if needed
                sim.train_markov(trace)

                # Run trace
                for key, size in trace:
                    sim.access(key, size)

                # Get results
                result = sim.get_results()
                pattern_results.append(result)

                print(f"[w={window_size}] ", end="")

            print()

        all_results[pattern] = pattern_results

        # Print best for this pattern
        print(f"\n*** Best for {pattern} ***")
        best = max(pattern_results, key=lambda r: r.prefetch_efficiency)
        print(f"Strategy: {best.strategy.value}")
        print(f"Efficiency: {best.prefetch_efficiency:.3f}")
        print(f"Latency Reduction: {best.latency_reduction:.2%}")
        print(f"Accuracy: {best.accuracy:.3f}")

    return all_results

def find_optimal_strategy(
    results: Dict[str, List[PrefetchResult]]
) -> Dict[str, Any]:
    """
    Find optimal prefetching strategy across all patterns

    Args:
        results: Experiment results

    Returns:
        Optimal strategy configuration
    """
    print("\n" + "="*70)
    print("FINDING OPTIMAL PREFETCH STRATEGY")
    print("="*70)

    # Flatten results
    all_results = []
    for pattern, pattern_results in results.items():
        for r in pattern_results:
            r.pattern = pattern
            all_results.append(r)

    # Find best by different metrics
    best_efficiency = max(all_results, key=lambda r: r.prefetch_efficiency)
    best_latency = max(all_results, key=lambda r: r.latency_reduction)
    best_accuracy = max(all_results, key=lambda r: r.accuracy)

    # Find overall best (weighted score)
    for r in all_results:
        r.score = (
            r.prefetch_efficiency * 0.4 +
            r.latency_reduction * 0.4 +
            r.accuracy * 0.2
        )

    best_overall = max(all_results, key=lambda r: r.score)

    print(f"\n*** BEST EFFICIENCY ***")
    print(f"Strategy: {best_efficiency.strategy.value}")
    print(f"Pattern: {best_efficiency.pattern}")
    print(f"Efficiency: {best_efficiency.prefetch_efficiency:.3f}")

    print(f"\n*** BEST LATENCY REDUCTION ***")
    print(f"Strategy: {best_latency.strategy.value}")
    print(f"Pattern: {best_latency.pattern}")
    print(f"Reduction: {best_latency.latency_reduction:.2%}")

    print(f"\n*** BEST ACCURACY ***")
    print(f"Strategy: {best_accuracy.strategy.value}")
    print(f"Pattern: {best_accuracy.pattern}")
    print(f"Accuracy: {best_accuracy.accuracy:.3f}")

    print(f"\n*** OVERALL OPTIMAL ***")
    print(f"Strategy: {best_overall.strategy.value}")
    print(f"Window Size: {best_overall.parameters['prefetch_window']}")
    print(f"Score: {best_overall.score:.3f}")

    return {
        'strategy': best_overall.strategy.value,
        'parameters': best_overall.parameters,
        'efficiency': best_overall.prefetch_efficiency,
        'latency_reduction': best_overall.latency_reduction,
        'accuracy': best_overall.accuracy
    }

def main():
    """Main optimization loop"""
    os.makedirs('simulations/optimization/memory/results', exist_ok=True)

    # Run experiments
    results = run_prefetch_experiments()

    # Find optimal
    optimal = find_optimal_strategy(results)

    # Save results
    output = {
        'results': {
            pattern: [
                {
                    'strategy': r.strategy.value,
                    'accuracy': r.accuracy,
                    'coverage': r.coverage,
                    'memory_overhead': r.memory_overhead,
                    'latency_reduction': r.latency_reduction,
                    'prefetch_efficiency': r.prefetch_efficiency,
                    'total_prefetches': r.total_prefetches,
                    'useful_prefetches': r.useful_prefetches,
                    'wasted_prefetches': r.wasted_prefetches,
                    'parameters': r.parameters
                }
                for r in pattern_results
            ]
            for pattern, pattern_results in results.items()
        },
        'optimal': optimal
    }

    with open('simulations/optimization/memory/results/prefetch_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("Results saved to: simulations/optimization/memory/results/prefetch_results.json")
    print("="*70)

    return optimal

if __name__ == '__main__':
    main()
