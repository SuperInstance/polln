/**
 * POLLN Microbiome - Performance Optimization Tests
 *
 * Phase 5: Production Optimization - Milestone 2
 * Comprehensive tests for the performance optimization system
 * including caching, batching, lazy loading, and parallel processing.
 *
 * @module microbiome/__tests__/optimization
 */

import {
  PerformanceOptimizer,
  ResultCache,
  OptimizationTarget,
  OptimizationStrategy,
  OptimizationResult,
  PerformanceProfile,
  CacheConfig,
  CacheStats,
  BatchResult,
  createPerformanceOptimizer,
  createObjectPool,
  ObjectPool,
  GenericObjectPool,
} from '../optimization.js';
import { PerformanceMonitor } from '../performance.js';
import {
  MicrobiomeAgent,
  FitnessScore,
  EcosystemSnapshot,
  ColonyStructure,
  AgentTaxonomy,
  ResourceType,
} from '../types.js';

describe('ResultCache', () => {
  let cache: ResultCache<number>;

  beforeEach(() => {
    cache = new ResultCache<number>({
      maxSizeBytes: 1024,
      defaultTTL: 1000,
      enableTTLExpiration: true,
      enableSizeEviction: true,
      cleanupInterval: 100,
    });
  });

  afterEach(() => {
    cache.destroy();
  });

  describe('Basic caching operations', () => {
    test('should store and retrieve values', () => {
      cache.set('key1', 42);
      expect(cache.get('key1')).toBe(42);
    });

    test('should return null for non-existent keys', () => {
      expect(cache.get('nonexistent')).toBeNull();
    });

    test('should update existing keys', () => {
      cache.set('key1', 42);
      cache.set('key1', 100);
      expect(cache.get('key1')).toBe(100);
    });

    test('should delete keys', () => {
      cache.set('key1', 42);
      expect(cache.delete('key1')).toBe(true);
      expect(cache.get('key1')).toBeNull();
    });

    test('should return false when deleting non-existent keys', () => {
      expect(cache.delete('nonexistent')).toBe(false);
    });

    test('should check if keys exist', () => {
      cache.set('key1', 42);
      expect(cache.has('key1')).toBe(true);
      expect(cache.has('nonexistent')).toBe(false);
    });
  });

  describe('TTL-based expiration', () => {
    test('should expire entries after TTL', async () => {
      cache.set('key1', 42, 100); // 100ms TTL
      expect(cache.get('key1')).toBe(42);

      await new Promise(resolve => setTimeout(resolve, 150));
      expect(cache.get('key1')).toBeNull();
    });

    test('should use default TTL when not specified', async () => {
      cache.set('key1', 42); // Uses default 1000ms TTL
      expect(cache.get('key1')).toBe(42);

      await new Promise(resolve => setTimeout(resolve, 1100));
      expect(cache.get('key1')).toBeNull();
    });

    test('should track expirations in stats', async () => {
      cache.set('key1', 42, 100);
      await new Promise(resolve => setTimeout(resolve, 150));

      cache.get('key1'); // Triggers expiration
      const stats = cache.getStats();
      expect(stats.expirations).toBeGreaterThan(0);
    });
  });

  describe('Size-based eviction (LRU)', () => {
    test('should evict least recently used entries when cache is full', () => {
      const smallCache = new ResultCache<number>({
        maxSizeBytes: 100, // Very small cache
        defaultTTL: 10000,
        enableSizeEviction: true,
      });

      // Fill cache
      for (let i = 0; i < 10; i++) {
        smallCache.set(`key${i}`, i);
      }

      // Access some entries to update LRU
      smallCache.get('key5');
      smallCache.get('key6');

      // Add more entries, should evict older ones
      for (let i = 10; i < 15; i++) {
        smallCache.set(`key${i}`, i);
      }

      // Recently accessed entries should still be there
      expect(smallCache.has('key5')).toBe(true);
      expect(smallCache.has('key6')).toBe(true);

      // Old entries should be evicted
      expect(smallCache.has('key0')).toBe(false);
      expect(smallCache.has('key1')).toBe(false);

      const stats = smallCache.getStats();
      expect(stats.evictions).toBeGreaterThan(0);

      smallCache.destroy();
    });

    test('should reject entries larger than cache size', () => {
      const smallCache = new ResultCache<string>({
        maxSizeBytes: 10,
        defaultTTL: 10000,
      });

      const result = smallCache.set('key1', 'this is a very long string that exceeds cache size');
      expect(result).toBe(false);

      smallCache.destroy();
    });
  });

  describe('Cache statistics', () => {
    test('should track hits and misses correctly', () => {
      cache.set('key1', 42);
      cache.set('key2', 100);

      cache.get('key1'); // Hit
      cache.get('key2'); // Hit
      cache.get('key3'); // Miss
      cache.get('key4'); // Miss

      const stats = cache.getStats();
      expect(stats.hits).toBe(2);
      expect(stats.misses).toBe(2);
      expect(stats.hitRate).toBe(0.5);
    });

    test('should calculate hit rate correctly', () => {
      cache.set('key1', 42);
      cache.get('key1'); // Hit
      cache.get('key1'); // Hit
      cache.get('key2'); // Miss

      const stats = cache.getStats();
      expect(stats.hitRate).toBeCloseTo(0.666, 2);
    });

    test('should track total entries', () => {
      expect(cache.getStats().totalEntries).toBe(0);

      cache.set('key1', 42);
      expect(cache.getStats().totalEntries).toBe(1);

      cache.set('key2', 100);
      expect(cache.getStats().totalEntries).toBe(2);

      cache.delete('key1');
      expect(cache.getStats().totalEntries).toBe(1);
    });

    test('should track average entry size', () => {
      cache.set('key1', 42);
      cache.set('key2', 100);

      const stats = cache.getStats();
      expect(stats.avgEntrySize).toBeGreaterThan(0);
    });
  });

  describe('Cache invalidation', () => {
    test('should invalidate entries matching predicate', () => {
      cache.set('prefix:key1', 42);
      cache.set('prefix:key2', 100);
      cache.set('other:key3', 200);

      const count = cache.invalidate((key) => key.startsWith('prefix:'));
      expect(count).toBe(2);

      expect(cache.has('prefix:key1')).toBe(false);
      expect(cache.has('prefix:key2')).toBe(false);
      expect(cache.has('other:key3')).toBe(true);
    });

    test('should clear all entries', () => {
      cache.set('key1', 42);
      cache.set('key2', 100);
      cache.set('key3', 200);

      cache.clear();

      expect(cache.getStats().totalEntries).toBe(0);
      expect(cache.get('key1')).toBeNull();
      expect(cache.get('key2')).toBeNull();
      expect(cache.get('key3')).toBeNull();
    });
  });
});

describe('PerformanceOptimizer', () => {
  let optimizer: PerformanceOptimizer;
  let monitor: PerformanceMonitor;

  beforeEach(() => {
    monitor = new PerformanceMonitor({
      maxSamples: 100,
      enableAnomalyDetection: false,
    });
    optimizer = createPerformanceOptimizer(monitor);
  });

  afterEach(() => {
    optimizer.destroy();
  });

  describe('Initialization', () => {
    test('should create optimizer with monitor', () => {
      expect(optimizer).toBeInstanceOf(PerformanceOptimizer);
    });

    test('should initialize with default configurations', () => {
      const stats = optimizer.getCacheStats();

      expect(stats.fitness).toBeDefined();
      expect(stats.colony).toBeDefined();
      expect(stats.pattern).toBeDefined();
    });
  });

  describe('Fitness caching', () => {
    test('should cache and retrieve fitness scores', () => {
      const agentId = 'agent1';
      const fitness: FitnessScore = {
        throughput: 0.8,
        accuracy: 0.9,
        efficiency: 0.7,
        cooperation: 0.85,
      };

      optimizer.setCachedFitness(agentId, fitness);
      const retrieved = optimizer.getCachedFitness(agentId);

      expect(retrieved).toEqual(fitness);
    });

    test('should invalidate fitness cache for specific agent', () => {
      optimizer.setCachedFitness('agent1', { throughput: 0.8, accuracy: 0.9, efficiency: 0.7, cooperation: 0.85 });
      optimizer.setCachedFitness('agent2', { throughput: 0.9, accuracy: 0.95, efficiency: 0.8, cooperation: 0.9 });

      const count = optimizer.invalidateFitnessCache('agent1');

      expect(count).toBeGreaterThan(0);
      expect(optimizer.getCachedFitness('agent1')).toBeNull();
      expect(optimizer.getCachedFitness('agent2')).not.toBeNull();
    });
  });

  describe('Colony caching', () => {
    test('should cache and retrieve colonies', () => {
      const agentIds = ['agent1', 'agent2', 'agent3'];
      const colonies: ColonyStructure[] = [
        {
          id: 'colony1',
          members: agentIds,
          communicationChannels: new Map(),
          formationTime: Date.now(),
          stability: 0.8,
          coEvolutionBonus: 0.15,
        },
      ];

      optimizer.setCachedColonies(agentIds, colonies);
      const retrieved = optimizer.getCachedColonies(agentIds);

      expect(retrieved).toEqual(colonies);
    });
  });

  describe('Pattern caching', () => {
    test('should cache and retrieve patterns', () => {
      const contextId = 'context1';
      const patterns = [{ type: 'pattern1', confidence: 0.9 }];

      optimizer.setCachedPatterns(contextId, patterns);
      const retrieved = optimizer.getCachedPatterns(contextId);

      expect(retrieved).toEqual(patterns);
    });
  });

  describe('Batch processing', () => {
    test('should process items in batches', async () => {
      const items = [1, 2, 3, 4, 5];
      const processor = (item: number) => item * 2;

      const result = await optimizer.batchProcess(items, processor, { batchSize: 2 });

      expect(result.successes.length).toBe(5);
      expect(result.failures.length).toBe(0);
      expect(result.successRate).toBe(1);
      expect(result.batchSize).toBe(2);

      expect(result.successes[0].result).toBe(2);
      expect(result.successes[4].result).toBe(10);
    });

    test('should handle processing errors', async () => {
      const items = [1, 2, 3, 4, 5];
      const processor = (item: number) => {
        if (item === 3) throw new Error('Test error');
        return item * 2;
      };

      const result = await optimizer.batchProcess(items, processor, {
        batchSize: 2,
        continueOnError: true,
      });

      expect(result.successes.length).toBe(4);
      expect(result.failures.length).toBe(1);
      expect(result.successRate).toBe(0.8);
      expect(result.failures[0].index).toBe(2);
      expect(result.failures[0].error.message).toBe('Test error');
    });

    test('should stop on error when continueOnError is false', async () => {
      const items = [1, 2, 3, 4, 5];
      const processor = (item: number) => {
        if (item === 3) throw new Error('Test error');
        return item * 2;
      };

      await expect(
        optimizer.batchProcess(items, processor, { continueOnError: false })
      ).rejects.toThrow('Test error');
    });

    test('should handle async processors', async () => {
      const items = [1, 2, 3];
      const processor = async (item: number) => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return item * 2;
      };

      const result = await optimizer.batchProcess(items, processor);

      expect(result.successes.length).toBe(3);
      expect(result.successes[0].result).toBe(2);
    });
  });

  describe('Parallel processing', () => {
    test('should process items in parallel', async () => {
      const items = [1, 2, 3, 4, 5];
      const processor = async (item: number) => {
        await new Promise(resolve => setTimeout(resolve, 50));
        return item * 2;
      };

      const startTime = Date.now();
      const result = await optimizer.parallelProcess(items, processor, { maxWorkers: 3 });
      const duration = Date.now() - startTime;

      expect(result.successes.length).toBe(5);
      expect(result.successRate).toBe(1);

      // With 3 workers and 5 items, should take roughly 2 batches * 50ms = ~100ms
      // (Much less than sequential 5 * 50ms = 250ms)
      expect(duration).toBeLessThan(200);
    });

    test('should handle task timeout', async () => {
      const items = [1, 2, 3];
      const processor = async (item: number) => {
        await new Promise(resolve => setTimeout(resolve, 200));
        return item * 2;
      };

      const result = await optimizer.parallelProcess(items, processor, {
        maxWorkers: 2,
        taskTimeout: 50,
      });

      expect(result.failures.length).toBeGreaterThan(0);
      expect(result.failures[0].error.message).toBe('Task timeout');
    });

    test('should limit concurrent workers', async () => {
      let activeWorkers = 0;
      let maxActiveWorkers = 0;

      const items = Array.from({ length: 10 }, (_, i) => i);
      const processor = async (item: number) => {
        activeWorkers++;
        maxActiveWorkers = Math.max(maxActiveWorkers, activeWorkers);
        await new Promise(resolve => setTimeout(resolve, 20));
        activeWorkers--;
        return item * 2;
      };

      await optimizer.parallelProcess(items, processor, { maxWorkers: 3 });

      expect(maxActiveWorkers).toBeLessThanOrEqual(3);
    });
  });

  describe('Lazy loading', () => {
    test('should load agents lazily with pagination', () => {
      const agents: MicrobiomeAgent[] = Array.from({ length: 100 }, (_, i) => ({
        id: `agent${i}`,
        taxonomy: AgentTaxonomy.BACTERIA,
        metabolism: {
          resourcePool: {
            pools: new Map(),
            setCapacity: () => {},
            getCapacity: () => 100,
            add: () => true,
            consume: () => true,
            getAmount: () => 50,
          },
          consumptionRate: new Map([[ResourceType.ENERGY, 1.0]]),
          productionRate: new Map([[ResourceType.BIOMASS, 0.5]]),
        },
        lifecycle: {
          isAlive: true,
          age: 0,
          maxAge: 10000,
          deathRate: 0.001,
        },
        goals: [{ type: 'survive', priority: 1.0, progress: 0.5 }],
        methods: [{ name: 'consume', parameters: [], successRate: 0.9 }],
        fitness: { throughput: 0.8, accuracy: 0.9, efficiency: 0.7, cooperation: 0.85 },
      }));

      // Load first page
      const page0 = optimizer.lazyLoadAgents(agents, 0, 10);
      expect(page0.length).toBe(10);
      expect(page0[0].id).toBe('agent0');

      // Load second page
      const page1 = optimizer.lazyLoadAgents(agents, 1, 10);
      expect(page1.length).toBe(10);
      expect(page1[0].id).toBe('agent10');

      // Load last page (partial)
      const page9 = optimizer.lazyLoadAgents(agents, 9, 10);
      expect(page9.length).toBe(10);
      expect(page9[0].id).toBe('agent90');

      // Load beyond available
      const page10 = optimizer.lazyLoadAgents(agents, 10, 10);
      expect(page10.length).toBe(0);
    });

    test('should return all agents when lazy loading disabled', () => {
      const agents: MicrobiomeAgent[] = Array.from({ length: 100 }, (_, i) => ({
        id: `agent${i}`,
        taxonomy: AgentTaxonomy.BACTERIA,
        metabolism: {
          resourcePool: {
            pools: new Map(),
            setCapacity: () => {},
            getCapacity: () => 100,
            add: () => true,
            consume: () => true,
            getAmount: () => 50,
          },
          consumptionRate: new Map([[ResourceType.ENERGY, 1.0]]),
          productionRate: new Map([[ResourceType.BIOMASS, 0.5]]),
        },
        lifecycle: {
          isAlive: true,
          age: 0,
          maxAge: 10000,
          deathRate: 0.001,
        },
        goals: [{ type: 'survive', priority: 1.0, progress: 0.5 }],
        methods: [{ name: 'consume', parameters: [], successRate: 0.9 }],
        fitness: { throughput: 0.8, accuracy: 0.9, efficiency: 0.7, cooperation: 0.85 },
      }));

      optimizer.updateLazyConfig({ enabled: false });

      const result = optimizer.lazyLoadAgents(agents, 0, 10);
      expect(result.length).toBe(100);
    });
  });

  describe('Profiling', () => {
    test('should profile system and identify bottlenecks', () => {
      // Record some operations
      monitor.recordOperation('evolution_step', 500);
      monitor.recordOperation('colony_discovery', 100);
      monitor.recordOperation('immune_scan', 50);
      monitor.recordOperation('evolution_step', 600);
      monitor.recordOperation('colony_discovery', 120);

      const profile = optimizer.profile(['evolution_step', 'colony_discovery', 'immune_scan']);

      expect(profile.timestamp).toBeDefined();
      expect(profile.bottlenecks.length).toBeGreaterThan(0);
      expect(profile.recommendations.length).toBeGreaterThan(0);

      // Check that bottlenecks are sorted by avgTime
      expect(profile.bottlenecks[0].avgTime).toBeGreaterThanOrEqual(profile.bottlenecks[1]?.avgTime || 0);
    });

    test('should provide optimization recommendations', () => {
      monitor.recordOperation('evolution_fitness', 1000);
      monitor.recordOperation('colony_discovery', 500);

      const profile = optimizer.profile(['evolution_fitness', 'colony_discovery']);

      expect(profile.recommendations.length).toBeGreaterThan(0);

      const evolutionRec = profile.recommendations.find(r => r.target === OptimizationTarget.EVOLUTION_SPEED);
      expect(evolutionRec).toBeDefined();
      expect(evolutionRec?.strategy).toBe(OptimizationStrategy.CACHING);
    });
  });

  describe('Cache statistics', () => {
    test('should provide comprehensive cache statistics', () => {
      optimizer.setCachedFitness('agent1', { throughput: 0.8, accuracy: 0.9, efficiency: 0.7, cooperation: 0.85 });
      optimizer.getCachedFitness('agent1'); // Hit
      optimizer.getCachedFitness('agent2'); // Miss

      const stats = optimizer.getCacheStats();

      expect(stats.fitness.hits).toBe(1);
      expect(stats.fitness.misses).toBe(1);
      expect(stats.fitness.hitRate).toBe(0.5);
    });
  });

  describe('Cache management', () => {
    test('should clear all caches', () => {
      optimizer.setCachedFitness('agent1', { throughput: 0.8, accuracy: 0.9, efficiency: 0.7, cooperation: 0.85 });
      optimizer.setCachedColonies(['agent1'], [{ id: 'c1', members: ['agent1'], communicationChannels: new Map(), formationTime: Date.now(), stability: 0.8, coEvolutionBonus: 0.1 }]);
      optimizer.setCachedPatterns('ctx1', [{ type: 'p1' }]);

      optimizer.clearAllCaches();

      expect(optimizer.getCachedFitness('agent1')).toBeNull();
      expect(optimizer.getCachedColonies(['agent1'])).toBeNull();
      expect(optimizer.getCachedPatterns('ctx1')).toBeNull();
    });
  });
});

describe('GenericObjectPool', () => {
  let pool: ObjectPool<{ value: number }>;

  beforeEach(() => {
    pool = new GenericObjectPool(
      () => ({ value: 0 }),
      (obj) => { obj.value = 0; },
      10
    );
  });

  afterEach(() => {
    pool.clear();
  });

  describe('Basic pool operations', () => {
    test('should create new objects when pool is empty', () => {
      const obj1 = pool.acquire();
      const obj2 = pool.acquire();

      expect(obj1).toEqual({ value: 0 });
      expect(obj2).toEqual({ value: 0 });
      expect(pool.size()).toBe(0);
    });

    test('should reuse objects from pool', () => {
      const obj1 = pool.acquire();
      obj1.value = 42;
      pool.release(obj1);

      expect(pool.size()).toBe(1);

      const obj2 = pool.acquire();
      expect(obj2).toBe(obj1); // Same object reference
      expect(obj2.value).toBe(0); // Reset by release
      expect(pool.size()).toBe(0);
    });

    test('should limit pool size', () => {
      const maxSize = 10;
      const customPool = new GenericObjectPool(
        () => ({ value: 0 }),
        undefined,
        maxSize
      );

      // Create and release many distinct objects
      const objects: Array<{ value: number }> = [];
      for (let i = 0; i < maxSize + 5; i++) {
        objects.push({ value: i }); // Create distinct objects
        customPool.release(objects[i]);
      }

      // Pool should not exceed max size
      expect(customPool.size()).toBeLessThanOrEqual(maxSize);

      customPool.clear();
    });

    test('should clear pool', () => {
      const obj1 = pool.acquire();
      const obj2 = pool.acquire();

      pool.release(obj1);
      pool.release(obj2);

      expect(pool.size()).toBe(2);

      pool.clear();

      expect(pool.size()).toBe(0);
    });
  });

  describe('Reset functionality', () => {
    test('should reset objects on release when reset function provided', () => {
      const poolWithReset = new GenericObjectPool(
        () => ({ value: 0 }),
        (obj) => { obj.value = 0; }
      );

      const obj1 = poolWithReset.acquire();
      obj1.value = 42;
      poolWithReset.release(obj1);

      const obj2 = poolWithReset.acquire();
      expect(obj2.value).toBe(0);

      poolWithReset.clear();
    });

    test('should not reset when reset function not provided', () => {
      const poolWithoutReset = new GenericObjectPool(
        () => ({ value: 0 })
      );

      const obj1 = poolWithoutReset.acquire();
      obj1.value = 42;
      poolWithoutReset.release(obj1);

      const obj2 = poolWithoutReset.acquire();
      expect(obj2.value).toBe(42); // Not reset

      poolWithoutReset.clear();
    });
  });
});

describe('Factory functions', () => {
  test('should create performance optimizer', () => {
    const monitor = new PerformanceMonitor();
    const optimizer = createPerformanceOptimizer(monitor);

    expect(optimizer).toBeInstanceOf(PerformanceOptimizer);

    optimizer.destroy();
  });

  test('should create object pool', () => {
    const pool = createObjectPool(
      () => ({ value: 0 }),
      (obj) => { obj.value = 0; },
      10
    );

    expect(pool).toBeInstanceOf(GenericObjectPool);

    const obj = pool.acquire();
    expect(obj).toEqual({ value: 0 });

    pool.release(obj);
    pool.clear();
  });
});
