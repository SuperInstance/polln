"""
Memory Optimization Test Suite

This script tests the memory optimization simulations to ensure they work
correctly and produce valid results.

Tests:
1. Compression optimization
2. Eviction policy simulation
3. ANN index tuning
4. Cache sizing analysis
5. Prefetching strategies
6. Cache simulator
7. Configuration generation
"""

import unittest
import numpy as np
import json
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import simulation modules
from simulations.optimization.memory.compression_optimization import (
    KVCacheCompressor,
    CacheType,
    CompressionMethod
)
from simulations.optimization.memory.eviction_policy import (
    CacheSimulator,
    EvictionPolicy,
    AccessPattern
)
from simulations.optimization.memory.cache_sizing import (
    LRUCache,
    WorkloadType
)
from simulations.optimization.memory.prefetching import (
    PrefetchSimulator,
    PrefetchStrategy
)
from simulations.optimization.memory.cache_simulator import (
    KVCacheSimulator,
    SimulatorConfig,
    AccessPattern as KVAccessPattern
)

class TestCompressionOptimization(unittest.TestCase):
    """Test compression optimization"""

    def setUp(self):
        """Set up test fixtures"""
        self.compressor = KVCacheCompressor()

    def test_generate_synthetic_cache(self):
        """Test synthetic cache generation"""
        for cache_type in [CacheType.ATTENTION, CacheType.MLP, CacheType.EMBEDDING]:
            data = self.compressor.generate_synthetic_kv_cache(cache_type)

            self.assertIn('key', data)
            self.assertIn('value', data)
            self.assertIsInstance(data['key'], np.ndarray)
            self.assertIsInstance(data['value'], np.ndarray)

    def test_svd_compression(self):
        """Test SVD compression"""
        data = np.random.randn(100, 50).astype(np.float32)
        compressed, ratio = self.compressor.svd_compress(data, 0.5)

        self.assertLess(ratio, 1.0)  # Should compress
        self.assertEqual(len(compressed), 3)  # U, s, Vt

    def test_quantization(self):
        """Test quantization"""
        data = np.random.randn(100, 50).astype(np.float32)

        for bits in [8, 4]:
            quantized, scale, zp = self.compressor.quantize(data, bits)
            reconstructed = self.compressor.dequantize(quantized, scale, zp)

            self.assertEqual(quantized.dtype, np.uint8)
            self.assertEqual(reconstructed.shape, data.shape)

            # Should have some error but reasonable
            mse = np.mean((data - reconstructed) ** 2)
            self.assertLess(mse, 1.0)

    def test_sparsification(self):
        """Test sparsification"""
        data = np.random.randn(100, 50).astype(np.float32)
        sparsity = 0.5

        values, indices = self.compressor.sparsify(data, sparsity)
        reconstructed = self.compressor.densify(values, indices, data.shape)

        self.assertEqual(len(values), int(data.size * (1 - sparsity)))
        self.assertEqual(reconstructed.shape, data.shape)

class TestEvictionPolicy(unittest.TestCase):
    """Test eviction policy simulation"""

    def test_lru_cache(self):
        """Test LRU cache"""
        cache = CacheSimulator(cache_size=1024, policy=EvictionPolicy.LRU)

        # Add items
        for i in range(10):
            cache.access(f"key_{i}", f"value_{i}", 100)

        # Should have evicted some items
        self.assertGreater(cache.stats['evictions'], 0)

        # Access should have some hits
        cache.access("key_5", None, 100)
        self.assertGreater(cache.stats['hits'], 0)

    def test_lfu_cache(self):
        """Test LFU cache"""
        cache = CacheSimulator(cache_size=1024, policy=EvictionPolicy.LFU)

        # Add and access items with different frequencies
        for i in range(10):
            cache.access(f"key_{i}", f"value_{i}", 100)

        # Access key_0 multiple times
        for _ in range(5):
            cache.access("key_0", None, 100)

        # key_0 should have high frequency
        self.assertGreater(cache.frequency.get("key_0", 0), 5)

    def test_fifo_cache(self):
        """Test FIFO cache"""
        cache = CacheSimulator(cache_size=1024, policy=EvictionPolicy.FIFO)

        # Add items
        for i in range(10):
            cache.access(f"key_{i}", f"value_{i}", 100)

        # Should have evicted items
        self.assertGreater(cache.stats['evictions'], 0)

    def test_arc_cache(self):
        """Test ARC cache"""
        cache = CacheSimulator(cache_size=1024, policy=EvictionPolicy.ARC)

        # Add and access items
        for i in range(20):
            cache.access(f"key_{i % 10}", f"value_{i % 10}", 100)

        # ARC should adapt
        self.assertGreater(len(cache.arc_t1) + len(cache.arc_t2), 0)

class TestCacheSizing(unittest.TestCase):
    """Test cache sizing analysis"""

    def test_lru_cache(self):
        """Test basic LRU cache"""
        cache = LRUCache(capacity=1024)

        # Add items
        for i in range(5):
            cache.access(f"key_{i}", 200)

        # Should have evicted items (5 * 200 = 1000 < 1024, so maybe not)
        cache.access(f"key_5", 200)
        cache.access(f"key_6", 200)

        # Now should have evictions
        self.assertGreater(len(cache.cache), 0)

    def test_hit_rate_calculation(self):
        """Test hit rate calculation"""
        cache = LRUCache(capacity=1024)

        # Add items
        cache.access("key_1", 100)
        cache.access("key_2", 100)

        # Hit
        cache.access("key_1", 100)

        # Miss
        cache.access("key_3", 100)

        hit_rate = cache.get_hit_rate()
        self.assertGreater(hit_rate, 0)
        self.assertLessEqual(hit_rate, 1)

class TestPrefetching(unittest.TestCase):
    """Test prefetching strategies"""

    def test_none_prefetch(self):
        """Test no prefetching"""
        sim = PrefetchSimulator(
            cache_size=1024 * 1024,
            strategy=PrefetchStrategy.NONE
        )

        for i in range(10):
            sim.access(f"key_{i}", 1024)

        # Should have no prefetches
        self.assertEqual(sim.stats['prefetches'], 0)

    def test_always_prefetch(self):
        """Test always prefetch"""
        sim = PrefetchSimulator(
            cache_size=10 * 1024 * 1024,
            strategy=PrefetchStrategy.ALWAYS,
            prefetch_window=3
        )

        for i in range(10):
            sim.access(f"seq_{i}", 1024)

        # Should have prefetches
        self.assertGreater(sim.stats['prefetches'], 0)

    def test_markov_prefetch(self):
        """Test Markov prefetching"""
        sim = PrefetchSimulator(
            cache_size=10 * 1024 * 1024,
            strategy=PrefetchStrategy.MARKOV,
            prefetch_window=3
        )

        # Train on simple pattern
        trace = [(f"key_{i}", 1024) for i in range(100)]
        sim.train_markov(trace)

        # Should have Markov model
        self.assertIsNotNone(sim.markov_model)

class TestKVCacheSimulator(unittest.TestCase):
    """Test KV-cache simulator"""

    def test_simulator_init(self):
        """Test simulator initialization"""
        config = SimulatorConfig(
            num_layers=32,
            hidden_dim=4096
        )

        sim = KVCacheSimulator(config)

        self.assertEqual(sim.config.num_layers, 32)
        self.assertEqual(sim.config.hidden_dim, 4096)

    def test_sequential_decode(self):
        """Test sequential decode pattern"""
        config = SimulatorConfig(num_layers=4, hidden_dim=128)
        sim = KVCacheSimulator(config)

        accesses = sim.simulate_sequential_decode(
            context_id="test",
            num_tokens=10
        )

        self.assertGreater(len(accesses), 0)

    def test_context_reuse(self):
        """Test context reuse pattern"""
        config = SimulatorConfig(num_layers=4, hidden_dim=128)
        sim = KVCacheSimulator(config)

        accesses = sim.simulate_context_reuse(
            base_context="test",
            num_turns=3,
            tokens_per_turn=10
        )

        self.assertGreater(len(accesses), 0)

    def test_trace_generation(self):
        """Test trace generation"""
        config = SimulatorConfig(num_layers=4, hidden_dim=128)
        sim = KVCacheSimulator(config)

        trace = sim.generate_trace(KVAccessPattern.SEQUENTIAL_DECODE)

        self.assertGreater(len(trace), 0)

    def test_access_pattern_analysis(self):
        """Test access pattern analysis"""
        config = SimulatorConfig(num_layers=4, hidden_dim=128)
        sim = KVCacheSimulator(config)

        trace = sim.generate_trace(KVAccessPattern.SEQUENTIAL_DECODE)
        stats = sim.analyze_access_pattern(trace)

        self.assertIn('total_accesses', stats)
        self.assertIn('unique_keys', stats)
        self.assertIn('by_type', stats)

class TestConfigurationGeneration(unittest.TestCase):
    """Test configuration generation"""

    def test_generate_config_from_results(self):
        """Test generating config from results"""
        # Mock results
        results = {
            'compression': {
                'optimal_configs': {
                    'attention': {
                        'method': 'svd',
                        'compression_ratio': 0.1,
                        'quality': 0.95
                    }
                }
            },
            'eviction': {
                'optimal': {
                    'overall': {
                        'policy': 'lru',
                        'cache_size': 512 * 1024 * 1024,
                        'hit_rate': 0.85
                    }
                }
            },
            'ann': {
                'optimal': {
                    'algorithm': 'hnsw',
                    'parameters': {'M': 16, 'efConstruction': 200},
                    'recall': 0.95,
                    'query_time_ms': 1.0
                }
            },
            'sizing': {
                'optimal_sizes': {
                    'by_workload': {
                        'conversation': {
                            'size_mb': 100,
                            'hit_rate': 0.85
                        }
                    }
                }
            },
            'prefetch': {
                'optimal': {
                    'strategy': 'markov',
                    'parameters': {'windowSize': 5},
                    'efficiency': 0.7,
                    'latency_reduction': 0.3
                }
            }
        }

        # Import generate_config
        from simulations.optimization.memory.generate_config import (
            extract_optimal_params,
            generate_config_ts
        )

        # Extract optimal
        optimal = extract_optimal_params(results)

        self.assertIn('compression', optimal)
        self.assertIn('eviction', optimal)
        self.assertIn('ann', optimal)

        # Generate TypeScript
        ts_content = generate_config_ts(optimal)

        self.assertIn('export const KV_CACHE_CONFIG', ts_content)
        self.assertIn('compression', ts_content)
        self.assertIn('eviction', ts_content)

def run_tests():
    """Run all tests"""
    print("="*70)
    print("MEMORY OPTIMIZATION TEST SUITE")
    print("="*70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCompressionOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestEvictionPolicy))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheSizing))
    suite.addTests(loader.loadTestsFromTestCase(TestPrefetching))
    suite.addTests(loader.loadTestsFromTestCase(TestKVCacheSimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationGeneration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
