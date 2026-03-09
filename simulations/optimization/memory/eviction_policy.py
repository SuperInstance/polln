"""
Cache Eviction Policy Optimization for POLLN

This script simulates different cache eviction policies to find optimal
strategies for KV-cache management.

Eviction policies tested:
- LRU (Least Recently Used)
- LFU (Least Frequently Used)
- FIFO (First In First Out)
- Random
- ARC (Adaptive Replacement Cache)
- LIRS (Low Inter-reference Recency Set)
- Size-based
- Hybrid policies

Access patterns simulated:
- Temporal locality (recent accesses predict future)
- Spatial locality (sequential/token-based)
- Zipf distribution (few items accessed frequently)
- Realistic conversation patterns
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict, defaultdict
import heapq
import random
import json

class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    RANDOM = "random"
    ARC = "arc"
    LIRS = "lirs"
    SIZE_BASED = "size_based"
    CLOCK = "clock"
    BELADY = "belady"  # Optimal (requires future knowledge)

class AccessPattern(Enum):
    """Access pattern types"""
    TEMPORAL = "temporal"  # Recent accesses predict future
    SPATIAL = "spatial"    # Sequential/token-based
    ZIPF = "zipf"          # Power law distribution
    CONVERSATION = "conversation"  # Realistic dialogue patterns
    HYBRID = "hybrid"      # Mixed patterns

@dataclass
class CacheEntry:
    """A cache entry with metadata"""
    key: str
    value: Any
    size: int
    access_count: int = 0
    last_access: int = 0
    insertion_time: int = 0
    reference_bits: int = 0  # For CLOCK algorithm

@dataclass
class EvictionResult:
    """Results from eviction experiment"""
    policy: EvictionPolicy
    access_pattern: AccessPattern
    cache_size: int
    hit_rate: float
    miss_rate: float
    total_accesses: int
    total_hits: int
    total_misses: int
    total_evictions: int
    avg_access_time: float
    memory_usage: float
    parameters: Dict[str, Any]

class CacheSimulator:
    """Simulates cache with different eviction policies"""

    def __init__(self, cache_size: int, policy: EvictionPolicy):
        """
        Initialize cache simulator

        Args:
            cache_size: Maximum cache size in bytes
            policy: Eviction policy to use
        """
        self.cache_size = cache_size
        self.policy = policy
        self.current_size = 0
        self.time = 0
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'access_times': []
        }

        # Policy-specific data structures
        self.cache: Dict[str, CacheEntry] = {}
        self.lru_order: OrderedDict = OrderedDict()
        self.frequency: Dict[str, int] = {}
        self.fifo_order: OrderedDict = OrderedDict()
        self.clock_hand: Optional[str] = None
        self.clock_buffer: List[str] = []

        # ARC-specific
        self.arc_p = 0  # Target size for T1
        self.arc_t1: OrderedDict = OrderedDict()  # Recency, page seen once
        self.arc_t2: OrderedDict = OrderedDict()  # Frequency, page seen twice
        self.arc_b1: OrderedDict = OrderedDict()  # Ghost entries evicted from T1
        self.arc_b2: OrderedDict = OrderedDict()  # Ghost entries evicted from T2

        # LIRS-specific
        self.lirs_lirs_size = cache_size // 2  # LIRS stack size
        self.lirs_stack: List[str] = []
        self.lirs_lir: Dict[str, int] = {}  # Low Inter-reference Recency
        self.lirs_hir: Dict[str, int] = {}  # High Inter-reference Recency

    def access(self, key: str, value: Any = None, size: int = 1024) -> bool:
        """
        Access a cache entry

        Args:
            key: Entry key
            value: Value (if miss)
            size: Entry size in bytes

        Returns:
            True if hit, False if miss
        """
        start_time = np.random.random() * 0.001  # Simulate access time

        self.time += 1
        hit = self._access(key, value, size)

        access_time = (np.random.random() * 0.001) + (0.0001 if not hit else 0.00001)
        self.stats['access_times'].append(access_time)

        if hit:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1

        return hit

    def _access(self, key: str, value: Any = None, size: int = 1024) -> bool:
        """Internal access logic"""
        if self.policy == EvictionPolicy.LRU:
            return self._access_lru(key, value, size)
        elif self.policy == EvictionPolicy.LFU:
            return self._access_lfu(key, value, size)
        elif self.policy == EvictionPolicy.FIFO:
            return self._access_fifo(key, value, size)
        elif self.policy == EvictionPolicy.RANDOM:
            return self._access_random(key, value, size)
        elif self.policy == EvictionPolicy.ARC:
            return self._access_arc(key, value, size)
        elif self.policy == EvictionPolicy.CLOCK:
            return self._access_clock(key, value, size)
        else:
            return self._access_lru(key, value, size)  # Default

    def _access_lru(self, key: str, value: Any, size: int) -> bool:
        """LRU access"""
        if key in self.cache:
            # Hit - update position
            entry = self.cache[key]
            entry.last_access = self.time
            entry.access_count += 1
            del self.lru_order[key]
            self.lru_order[key] = entry
            return True
        else:
            # Miss - insert
            entry = CacheEntry(key=key, value=value, size=size,
                             insertion_time=self.time, last_access=self.time)

            # Evict if necessary
            while self.current_size + size > self.cache_size and self.lru_order:
                self._evict_lru()

            self.cache[key] = entry
            self.lru_order[key] = entry
            self.current_size += size
            return False

    def _evict_lru(self):
        """Evict least recently used"""
        if not self.lru_order:
            return

        lru_key, lru_entry = self.lru_order.popitem(last=False)
        del self.cache[lru_key]
        self.current_size -= lru_entry.size
        self.stats['evictions'] += 1

    def _access_lfu(self, key: str, value: Any, size: int) -> bool:
        """LFU access"""
        if key in self.cache:
            # Hit - update frequency
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = self.time
            self.frequency[key] = entry.access_count
            return True
        else:
            # Miss - insert
            entry = CacheEntry(key=key, value=value, size=size,
                             insertion_time=self.time, last_access=self.time)

            # Evict if necessary
            while self.current_size + size > self.cache_size and self.cache:
                self._evict_lfu()

            self.cache[key] = entry
            self.frequency[key] = 1
            self.current_size += size
            return False

    def _evict_lfu(self):
        """Evict least frequently used"""
        if not self.cache:
            return

        # Find item with lowest frequency
        lfu_key = min(self.frequency.keys(), key=lambda k: (self.frequency[k], self.cache[k].last_access))

        entry = self.cache[lfu_key]
        del self.cache[lfu_key]
        del self.frequency[lfu_key]
        self.current_size -= entry.size
        self.stats['evictions'] += 1

    def _access_fifo(self, key: str, value: Any, size: int) -> bool:
        """FIFO access"""
        if key in self.cache:
            # Hit
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = self.time
            return True
        else:
            # Miss - insert
            entry = CacheEntry(key=key, value=value, size=size,
                             insertion_time=self.time, last_access=self.time)

            # Evict if necessary
            while self.current_size + size > self.cache_size and self.fifo_order:
                self._evict_fifo()

            self.cache[key] = entry
            self.fifo_order[key] = entry
            self.current_size += size
            return False

    def _evict_fifo(self):
        """Evict first in"""
        if not self.fifo_order:
            return

        fifo_key, fifo_entry = self.fifo_order.popitem(last=False)
        del self.cache[fifo_key]
        self.current_size -= fifo_entry.size
        self.stats['evictions'] += 1

    def _access_random(self, key: str, value: Any, size: int) -> bool:
        """Random eviction access"""
        if key in self.cache:
            # Hit
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = self.time
            return True
        else:
            # Miss - insert
            entry = CacheEntry(key=key, value=value, size=size,
                             insertion_time=self.time, last_access=self.time)

            # Evict if necessary
            while self.current_size + size > self.cache_size and self.cache:
                self._evict_random()

            self.cache[key] = entry
            self.current_size += size
            return False

    def _evict_random(self):
        """Evict random entry"""
        if not self.cache:
            return

        random_key = random.choice(list(self.cache.keys()))
        entry = self.cache[random_key]
        del self.cache[random_key]
        self.current_size -= entry.size
        self.stats['evictions'] += 1

    def _access_arc(self, key: str, value: Any, size: int) -> bool:
        """ARC (Adaptive Replacement Cache) access"""
        # Check if in T1 or T2 (actual cache)
        in_t1 = key in self.arc_t1
        in_t2 = key in self.arc_t2

        if in_t1 or in_t2:
            # Cache hit
            if in_t1:
                entry = self.arc_t1[key]
                del self.arc_t1[key]
                self.arc_t2[key] = entry  # Move to T2 (frequent)
            else:
                entry = self.arc_t2[key]
                del self.arc_t2[key]
                self.arc_t2[key] = entry  # Update position in T2
            return True

        # Check if in B1 or B2 (ghost cache)
        in_b1 = key in self.arc_b1
        in_b2 = key in self.arc_b2

        if in_b1:
            # Hit in ghost B1 - increase T1 size
            delta = max(1, in_b2 // in_t1) if in_t1 > 0 else 1
            self.arc_p = min(self.arc_p + delta, self.cache_size)

            # Replace
            self._arc_replace(key)
            del self.arc_b1[key]

        elif in_b2:
            # Hit in ghost B2 - decrease T1 size
            delta = max(1, in_t1 // in_b2) if in_b2 > 0 else 1
            self.arc_p = max(self.arc_p - delta, 0)

            # Replace
            self._arc_replace(key)
            del self.arc_b2[key]

        else:
            # Complete miss - insert into T1
            self._arc_replace(key)

        # Insert into T1
        entry = CacheEntry(key=key, value=value, size=size,
                         insertion_time=self.time, last_access=self.time)
        self.arc_t1[key] = entry
        return False

    def _arc_replace(self, key: str):
        """ARC replacement logic"""
        t1_size = sum(e.size for e in self.arc_t1.values())
        t2_size = sum(e.size for e in self.arc_t2.values())

        if t1_size + t2_size >= self.cache_size:
            # Cache is full
            if (len(self.arc_t1) > 0 and
                ((len(self.arc_t1) > self.arc_p) or
                 (key in self.arc_b2 and len(self.arc_t1) == self.arc_p))):
                # Evict from T1
                evicted_key, evicted_entry = self.arc_t1.popitem(last=False)
                self.arc_b1[evicted_key] = evicted_entry
                self.stats['evictions'] += 1
            else:
                # Evict from T2
                evicted_key, evicted_entry = self.arc_t2.popitem(last=False)
                self.arc_b2[evicted_key] = evicted_entry
                self.stats['evictions'] += 1

    def _access_clock(self, key: str, value: Any, size: int) -> bool:
        """CLOCK algorithm access"""
        if key in self.cache:
            # Hit
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = self.time
            entry.reference_bits = 1
            return True
        else:
            # Miss - insert
            entry = CacheEntry(key=key, value=value, size=size,
                             insertion_time=self.time, last_access=self.time,
                             reference_bits=1)

            # Evict if necessary
            while self.current_size + size > self.cache_size and self.cache:
                self._evict_clock()

            self.cache[key] = entry
            if not self.clock_hand:
                self.clock_hand = key
            self.current_size += size
            return False

    def _evict_clock(self):
        """CLOCK eviction"""
        if not self.cache:
            return

        # Find entry with reference bit = 0
        keys = list(self.cache.keys())
        start_idx = keys.index(self.clock_hand) if self.clock_hand in keys else 0

        for i in range(len(keys)):
            idx = (start_idx + i) % len(keys)
            key = keys[idx]

            if self.cache[key].reference_bits == 0:
                # Evict this one
                entry = self.cache[key]
                del self.cache[key]
                self.current_size -= entry.size
                self.stats['evictions'] += 1
                self.clock_hand = keys[(idx + 1) % len(keys)] if keys else None
                return
            else:
                # Give a second chance
                self.cache[key].reference_bits = 0

        # If all had reference bit = 1, evict first one
        key = keys[start_idx]
        entry = self.cache[key]
        del self.cache[key]
        self.current_size -= entry.size
        self.stats['evictions'] += 1

    def get_results(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_accesses = self.stats['hits'] + self.stats['misses']

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': self.stats['hits'] / total_accesses if total_accesses > 0 else 0,
            'miss_rate': self.stats['misses'] / total_accesses if total_accesses > 0 else 0,
            'avg_access_time': np.mean(self.stats['access_times']) if self.stats['access_times'] else 0,
            'memory_usage': self.current_size / self.cache_size if self.cache_size > 0 else 0
        }

def generate_access_trace(
    pattern: AccessPattern,
    num_accesses: int = 10000,
    num_keys: int = 1000
) -> List[Tuple[str, int]]:
    """
    Generate access trace with specific pattern

    Args:
        pattern: Access pattern type
        num_accesses: Number of accesses to generate
        num_keys: Number of unique keys

    Returns:
        List of (key, size) tuples
    """
    trace = []

    if pattern == AccessPattern.TEMPORAL:
        # Recent accesses predict future
        for i in range(num_accesses):
            if i < 100:
                # Warmup - random
                key = f"key_{random.randint(0, min(100, num_keys - 1))}"
            else:
                # 80% chance to access recent keys
                if random.random() < 0.8:
                    key = f"key_{random.randint(max(0, i - 100), min(i, num_keys - 1))}"
                else:
                    key = f"key_{random.randint(0, num_keys - 1)}"
            trace.append((key, random.randint(512, 2048)))

    elif pattern == AccessPattern.SPATIAL:
        # Sequential/token-based
        for i in range(num_accesses):
            if i < 10:
                key = f"key_{i}"
            else:
                # 70% chance to access next token
                if random.random() < 0.7:
                    prev_idx = int(trace[-1][0].split('_')[1])
                    key = f"key_{min(prev_idx + random.randint(1, 5), num_keys - 1)}"
                else:
                    key = f"key_{random.randint(0, num_keys - 1)}"
            trace.append((key, random.randint(512, 2048)))

    elif pattern == AccessPattern.ZIPF:
        # Power law distribution
        zipf_param = 1.5
        ranks = np.arange(1, num_keys + 1)
        probs = 1 / (ranks ** zipf_param)
        probs = probs / np.sum(probs)

        for i in range(num_accesses):
            key_idx = np.random.choice(num_keys, p=probs)
            key = f"key_{key_idx}"
            trace.append((key, random.randint(512, 2048)))

    elif pattern == AccessPattern.CONVERSATION:
        # Realistic conversation patterns
        # Topic-based clustering with occasional shifts
        topics = [f"topic_{i}" for i in range(10)]
        current_topic = random.choice(topics)
        tokens_in_topic = 0
        max_tokens_per_topic = random.randint(50, 200)

        for i in range(num_accesses):
            if tokens_in_topic >= max_tokens_per_topic or random.random() < 0.05:
                # Topic shift
                current_topic = random.choice(topics)
                tokens_in_topic = 0
                max_tokens_per_topic = random.randint(50, 200)

            # Access within current topic
            topic_offset = int(current_topic.split('_')[1]) * 100
            key = f"key_{topic_offset + random.randint(0, 99)}"
            trace.append((key, random.randint(512, 2048)))
            tokens_in_topic += 1

    elif pattern == AccessPattern.HYBRID:
        # Mix of patterns
        patterns = [AccessPattern.TEMPORAL, AccessPattern.SPATIAL,
                   AccessPattern.ZIPF, AccessPattern.CONVERSATION]

        for i in range(num_accesses):
            # Change pattern every 1000 accesses
            pattern_idx = (i // 1000) % len(patterns)
            current_pattern = patterns[pattern_idx]

            # Generate single access with pattern
            if current_pattern == AccessPattern.ZIPF:
                zipf_param = 1.5
                ranks = np.arange(1, num_keys + 1)
                probs = 1 / (ranks ** zipf_param)
                probs = probs / np.sum(probs)
                key_idx = np.random.choice(num_keys, p=probs)
                key = f"key_{key_idx}"
            else:
                key = f"key_{random.randint(0, num_keys - 1)}"

            trace.append((key, random.randint(512, 2048)))

    return trace

def run_eviction_experiments(
    cache_sizes: List[int] = [1024*1024, 5*1024*1024, 10*1024*1024],
    policies: List[EvictionPolicy] = None,
    patterns: List[AccessPattern] = None
) -> Dict[str, List[EvictionResult]]:
    """
    Run eviction policy experiments

    Args:
        cache_sizes: List of cache sizes to test
        policies: List of policies to test
        patterns: List of access patterns to test

    Returns:
        Dictionary of results
    """
    if policies is None:
        policies = [
            EvictionPolicy.LRU,
            EvictionPolicy.LFU,
            EvictionPolicy.FIFO,
            EvictionPolicy.RANDOM,
            EvictionPolicy.ARC,
            EvictionPolicy.CLOCK
        ]

    if patterns is None:
        patterns = [
            AccessPattern.TEMPORAL,
            AccessPattern.SPATIAL,
            AccessPattern.ZIPF,
            AccessPattern.CONVERSATION,
            AccessPattern.HYBRID
        ]

    results = defaultdict(list)

    print("="*70)
    print("CACHE EVICTION POLICY OPTIMIZATION")
    print("="*70)

    for pattern in patterns:
        print(f"\n{'='*70}")
        print(f"Testing Pattern: {pattern.value.upper()}")
        print(f"{'='*70}")

        # Generate trace
        trace = generate_access_trace(pattern, num_accesses=10000, num_keys=1000)

        for cache_size in cache_sizes:
            print(f"\nCache Size: {cache_size // 1024}KB")

            for policy in policies:
                print(f"  Testing {policy.value}...", end=" ")

                simulator = CacheSimulator(cache_size, policy)

                # Run trace
                for key, size in trace:
                    simulator.access(key, f"value_{key}", size)

                # Get results
                stats = simulator.get_results()

                result = EvictionResult(
                    policy=policy,
                    access_pattern=pattern,
                    cache_size=cache_size,
                    hit_rate=stats['hit_rate'],
                    miss_rate=stats['miss_rate'],
                    total_accesses=stats['hits'] + stats['misses'],
                    total_hits=stats['hits'],
                    total_misses=stats['misses'],
                    total_evictions=stats['evictions'],
                    avg_access_time=stats['avg_access_time'],
                    memory_usage=stats['memory_usage'],
                    parameters={}
                )

                results[pattern.value].append(result)

                print(f"Hit Rate: {result.hit_rate:.3f}, Evictions: {result.total_evictions}")

    return results

def find_optimal_policies(results: Dict[str, List[EvictionResult]]) -> Dict[str, Any]:
    """
    Find optimal eviction policy for each access pattern

    Args:
        results: Experiment results

    Returns:
        Optimal policy per pattern and overall
    """
    optimal_by_pattern = {}

    for pattern, pattern_results in results.items():
        # Find best hit rate
        best = max(pattern_results, key=lambda r: r.hit_rate)
        optimal_by_pattern[pattern] = {
            'policy': best.policy.value,
            'cache_size': best.cache_size,
            'hit_rate': best.hit_rate,
            'total_evictions': best.total_evictions
        }

        print(f"\n*** OPTIMAL for {pattern} ***")
        print(f"Policy: {best.policy.value}")
        print(f"Cache Size: {best.cache_size // 1024}KB")
        print(f"Hit Rate: {best.hit_rate:.3f}")

    # Find overall best
    all_results = []
    for pattern_results in results.values():
        all_results.extend(pattern_results)

    overall_best = max(all_results, key=lambda r: r.hit_rate)

    optimal_overall = {
        'policy': overall_best.policy.value,
        'cache_size': overall_best.cache_size,
        'hit_rate': overall_best.hit_rate,
        'pattern': overall_best.access_pattern.value
    }

    print(f"\n*** OVERALL OPTIMAL ***")
    print(f"Policy: {optimal_overall['policy']}")
    print(f"Cache Size: {optimal_overall['cache_size'] // 1024}KB")
    print(f"Hit Rate: {optimal_overall['hit_rate']:.3f}")
    print(f"Best Pattern: {optimal_overall['pattern']}")

    return {
        'by_pattern': optimal_by_pattern,
        'overall': optimal_overall
    }

def main():
    """Main optimization loop"""
    import os
    os.makedirs('simulations/optimization/memory/results', exist_ok=True)

    # Run experiments
    results = run_eviction_experiments(
        cache_sizes=[
            1024*1024,      # 1MB
            5*1024*1024,    # 5MB
            10*1024*1024,   # 10MB
            50*1024*1024,   # 50MB
            100*1024*1024   # 100MB
        ],
        policies=[
            EvictionPolicy.LRU,
            EvictionPolicy.LFU,
            EvictionPolicy.FIFO,
            EvictionPolicy.RANDOM,
            EvictionPolicy.ARC,
            EvictionPolicy.CLOCK
        ],
        patterns=[
            AccessPattern.TEMPORAL,
            AccessPattern.SPATIAL,
            AccessPattern.ZIPF,
            AccessPattern.CONVERSATION,
            AccessPattern.HYBRID
        ]
    )

    # Find optimal
    optimal = find_optimal_policies(results)

    # Save results
    output = {
        'results': {
            pattern: [
                {
                    'policy': r.policy.value,
                    'cache_size': r.cache_size,
                    'hit_rate': r.hit_rate,
                    'miss_rate': r.miss_rate,
                    'total_accesses': r.total_accesses,
                    'total_hits': r.total_hits,
                    'total_misses': r.total_misses,
                    'total_evictions': r.total_evictions,
                    'avg_access_time': r.avg_access_time,
                    'memory_usage': r.memory_usage
                }
                for r in pattern_results
            ]
            for pattern, pattern_results in results.items()
        },
        'optimal': optimal
    }

    with open('simulations/optimization/memory/results/eviction_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("Results saved to: simulations/optimization/memory/results/eviction_results.json")
    print("="*70)

    return optimal

if __name__ == '__main__':
    main()
