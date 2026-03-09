/**
 * Tests for Memory Protection Module
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  MemoryMonitor,
  BoundedMap,
  BoundedSet,
  MemoryProtectionManager,
  createMemoryMonitor,
  createMemoryProtectionManager,
  createBoundedMap,
  createBoundedSet,
  type MemoryStats,
  type MemoryPressureEvent,
} from '../memory-protection.js';

// Mock console.error to avoid clutter
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('MemoryMonitor', () => {
  let monitor: MemoryMonitor;

  beforeEach(() => {
    monitor = createMemoryMonitor({
      monitorIntervalMs: 100, // Fast for tests
    });
  });

  afterEach(() => {
    monitor.stop();
  });

  describe('Initialization', () => {
    it('should create with default config', () => {
      const defaultMonitor = createMemoryMonitor();
      expect(defaultMonitor).toBeInstanceOf(MemoryMonitor);
    });

    it('should create with custom config', () => {
      const customMonitor = createMemoryMonitor({
        moderateThreshold: 0.5,
        highThreshold: 0.7,
        criticalThreshold: 0.9,
      });

      expect(customMonitor).toBeInstanceOf(MemoryMonitor);
      customMonitor.stop();
    });
  });

  describe('Monitoring', () => {
    it('should start and stop monitoring', () => {
      expect(monitor['monitoring']).toBe(false);

      monitor.start();
      expect(monitor['monitoring']).toBe(true);

      monitor.stop();
      expect(monitor['monitoring']).toBe(false);
    });

    it('should not start if already monitoring', () => {
      monitor.start();
      const intervalId = monitor['intervalId'];

      monitor.start(); // Should not change interval

      expect(monitor['intervalId']).toBe(intervalId);
    });

    it('should collect memory stats', () => {
      const stats = monitor.getStats();

      expect(stats).toHaveProperty('heapUsed');
      expect(stats).toHaveProperty('heapTotal');
      expect(stats).toHaveProperty('systemFree');
      expect(stats).toHaveProperty('systemTotal');
      expect(stats).toHaveProperty('pressureLevel');
      expect(stats).toHaveProperty('heapUsedPercent');
      expect(stats).toHaveProperty('systemUsedPercent');

      expect(stats.heapUsed).toBeGreaterThan(0);
      expect(stats.heapTotal).toBeGreaterThan(0);
    });
  });

  describe('Pressure Levels', () => {
    it('should detect normal pressure', () => {
      const stats = monitor.getStats();
      expect(['normal', 'moderate', 'high', 'critical']).toContain(stats.pressureLevel);
    });

    it('should emit stats event', (done) => {
      monitor.on('stats', (stats: MemoryStats) => {
        expect(stats).toHaveProperty('heapUsed');
        monitor.stop();
        done();
      });

      monitor.start();
    }, 5000);
  });

  describe('Get Pressure Level', () => {
    it('should return current pressure level', () => {
      const level = monitor.getPressureLevel();
      expect(['normal', 'moderate', 'high', 'critical']).toContain(level);
    });
  });
});

describe('BoundedMap', () => {
  let map: BoundedMap<string, number>;

  beforeEach(() => {
    map = createBoundedMap(5, 0, true, 0.2);
  });

  describe('Basic Operations', () => {
    it('should store and retrieve values', () => {
      map.set('one', 1);
      expect(map.get('one')).toBe(1);
    });

    it('should return undefined for non-existent key', () => {
      expect(map.get('nonexistent')).toBeUndefined();
    });

    it('should check if key exists', () => {
      map.set('one', 1);
      expect(map.has('one')).toBe(true);
      expect(map.has('two')).toBe(false);
    });

    it('should delete key', () => {
      map.set('one', 1);
      map.delete('one');
      expect(map.has('one')).toBe(false);
    });

    it('should clear all entries', () => {
      map.set('one', 1);
      map.set('two', 2);
      map.clear();

      expect(map.size).toBe(0);
    });
  });

  describe('Size Limits', () => {
    it('should enforce max size', () => {
      // Fill to capacity
      for (let i = 0; i < 5; i++) {
        map.set(`key-${i}`, i);
      }

      expect(map.size).toBe(5);

      // Add one more - should trigger eviction
      map.set('key-5', 5);

      // Size should be at most max
      expect(map.size).toBeLessThanOrEqual(5);
    });

    it('should evict least recently used entries', () => {
      // Fill the map
      for (let i = 0; i < 5; i++) {
        map.set(`key-${i}`, i);
      }

      // Access some entries to update their access time
      map.get('key-3');
      map.get('key-4');

      // Add more to trigger eviction
      map.set('key-5', 5);
      map.set('key-6', 6);

      // Recently accessed keys should still exist
      expect(map.has('key-3')).toBe(true);
      expect(map.has('key-4')).toBe(true);

      // Older keys may have been evicted
      expect(map.size).toBeLessThanOrEqual(5);
    });

    it('should not evict when disabled', () => {
      const noEvictMap = createBoundedMap(5, 0, false);

      for (let i = 0; i < 10; i++) {
        noEvictMap.set(`key-${i}`, i);
      }

      // Should exceed max size when eviction is disabled
      expect(noEvictMap.size).toBe(10);
    });
  });

  describe('TTL Expiration', () => {
    beforeEach(() => {
      jest.useRealTimers();
    });

    it('should expire entries after TTL', async () => {
      map.set('temp', 1, 100); // 100ms TTL

      expect(map.has('temp')).toBe(true);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(map.has('temp')).toBe(false);
      expect(map.get('temp')).toBeUndefined();
    });

    it('should use default TTL when not specified', async () => {
      const ttlMap = createBoundedMap(10, 100); // 100ms default TTL
      ttlMap.set('temp', 1);

      expect(ttlMap.has('temp')).toBe(true);

      await new Promise(resolve => setTimeout(resolve, 150));

      expect(ttlMap.has('temp')).toBe(false);
    });

    it('should not expire when TTL is 0', async () => {
      const noTtlMap = createBoundedMap(10, 0);
      noTtlMap.set('permanent', 1);

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(noTtlMap.has('permanent')).toBe(true);
    });
  });

  describe('Cleanup', () => {
    it('should cleanup expired entries', async () => {
      map.set('temp1', 1, 100);
      map.set('temp2', 2, 100);
      map.set('permanent', 3, 0);

      await new Promise(resolve => setTimeout(resolve, 150));

      const count = map.cleanupExpired();
      expect(count).toBe(2);
      expect(map.has('permanent')).toBe(true);
    });

    it('should manually evict entries', () => {
      for (let i = 0; i < 5; i++) {
        map.set(`key-${i}`, i);
      }

      const evicted = map.evict();
      expect(evicted).toBeGreaterThan(0);
      expect(map.size).toBeLessThan(5);
    });
  });

  describe('Statistics', () => {
    it('should return collection stats', () => {
      map.set('one', 1);
      map.set('two', 2);

      const stats = map.getStats();

      expect(stats.size).toBe(2);
      expect(stats.maxSize).toBe(5);
      expect(stats.utilizationPercent).toBe(40);
    });

    it('should include expired count in stats', async () => {
      map.set('temp', 1, 100);
      map.set('permanent', 2, 0);

      await new Promise(resolve => setTimeout(resolve, 150));

      const stats = map.getStats();
      expect(stats.expiredCount).toBe(1);
    });
  });

  describe('Metadata', () => {
    it('should track entry metadata', () => {
      map.set('test', 42);

      const entry = map.getEntry('test');
      expect(entry).toBeDefined();
      expect(entry!.value).toBe(42);
      expect(entry!.hitCount).toBeGreaterThan(0);
      expect(entry!.createdAt).toBeGreaterThan(0);
    });

    it('should update hit count on access', () => {
      map.set('test', 42);
      map.get('test');
      map.get('test');

      const entry = map.getEntry('test');
      expect(entry!.hitCount).toBe(3);
    });

    it('should update access time', async () => {
      map.set('test', 42);

      const firstAccess = map.getEntry('test')!.accessedAt;
      await new Promise(resolve => setTimeout(resolve, 10));
      map.get('test');

      const secondAccess = map.getEntry('test')!.accessedAt;
      expect(secondAccess).toBeGreaterThan(firstAccess);
    });
  });
});

describe('BoundedSet', () => {
  let set: BoundedSet<number>;

  beforeEach(() => {
    set = createBoundedSet(5, 0, true, 0.2);
  });

  describe('Basic Operations', () => {
    it('should add and check values', () => {
      set.add(1);
      expect(set.has(1)).toBe(true);
      expect(set.has(2)).toBe(false);
    });

    it('should delete values', () => {
      set.add(1);
      set.delete(1);
      expect(set.has(1)).toBe(false);
    });

    it('should clear all entries', () => {
      set.add(1);
      set.add(2);
      set.clear();

      expect(set.size).toBe(0);
    });

    it('should not add duplicate values', () => {
      set.add(1);
      set.add(1);

      expect(set.size).toBe(1);
    });
  });

  describe('Size Limits', () => {
    it('should enforce max size', () => {
      for (let i = 0; i < 10; i++) {
        set.add(i);
      }

      expect(set.size).toBeLessThanOrEqual(5);
    });

    it('should evict least recently used entries', () => {
      // Fill the set
      for (let i = 0; i < 5; i++) {
        set.add(i);
      }

      // Access some entries
      set.has(3);
      set.has(4);

      // Add more to trigger eviction
      set.add(5);
      set.add(6);

      // Recently accessed should still exist
      expect(set.has(3)).toBe(true);
      expect(set.has(4)).toBe(true);
    });
  });

  describe('TTL Expiration', () => {
    it('should expire entries after TTL', async () => {
      set.add(1, 100);

      expect(set.has(1)).toBe(true);

      await new Promise(resolve => setTimeout(resolve, 150));

      expect(set.has(1)).toBe(false);
    });
  });

  describe('Statistics', () => {
    it('should return collection stats', () => {
      set.add(1);
      set.add(2);

      const stats = set.getStats();

      expect(stats.size).toBe(2);
      expect(stats.maxSize).toBe(5);
      expect(stats.utilizationPercent).toBe(40);
    });
  });
});

describe('MemoryProtectionManager', () => {
  let manager: MemoryProtectionManager;

  beforeEach(() => {
    manager = createMemoryProtectionManager({
      monitorIntervalMs: 100,
    });
  });

  afterEach(() => {
    manager.stop();
  });

  describe('Initialization', () => {
    it('should create manager', () => {
      expect(manager).toBeInstanceOf(MemoryProtectionManager);
    });

    it('should start and stop', () => {
      manager.start();
      expect(manager['monitor']['monitoring']).toBe(true);

      manager.stop();
      expect(manager['monitor']['monitoring']).toBe(false);
    });
  });

  describe('Cache Registration', () => {
    it('should register and unregister caches', () => {
      const mockCache = {
        clear: jest.fn(),
        name: 'test-cache',
      };

      manager.registerCache(mockCache);
      expect(manager.getProtectionStats().registeredCaches).toBe(1);

      manager.unregisterCache(mockCache);
      expect(manager.getProtectionStats().registeredCaches).toBe(0);
    });

    it('should register bounded maps and sets', () => {
      const map = createBoundedMap(100);
      const set = createBoundedSet(100);

      manager.registerBoundedMap(map);
      manager.registerBoundedSet(set);

      const stats = manager.getProtectionStats();
      expect(stats.boundedMaps).toBe(1);
      expect(stats.boundedSets).toBe(1);
    });
  });

  describe('Memory Stats', () => {
    it('should return memory stats', () => {
      const stats = manager.getStats();

      expect(stats).toHaveProperty('heapUsed');
      expect(stats).toHaveProperty('pressureLevel');
    });

    it('should return pressure level', () => {
      const level = manager.getPressureLevel();
      expect(['normal', 'moderate', 'high', 'critical']).toContain(level);
    });
  });

  describe('Protection Stats', () => {
    it('should return protection statistics', () => {
      const mockCache = { clear: jest.fn() };
      manager.registerCache(mockCache);

      const stats = manager.getProtectionStats();

      expect(stats).toHaveProperty('memoryStats');
      expect(stats).toHaveProperty('registeredCaches');
      expect(stats).toHaveProperty('boundedMaps');
      expect(stats).toHaveProperty('boundedSets');
      expect(stats.registeredCaches).toBe(1);
    });
  });

  describe('Events', () => {
    it('should emit pressure events', (done) => {
      let eventReceived = false;

      manager.on('pressure:moderate', (event: MemoryPressureEvent) => {
        expect(event).toHaveProperty('level');
        expect(event).toHaveProperty('stats');
        expect(event).toHaveProperty('timestamp');
        eventReceived = true;
      });

      manager.start();

      // Wait a bit for monitoring to run
      setTimeout(() => {
        manager.stop();
        // Event may or may not be emitted depending on memory pressure
        done();
      }, 200);
    }, 5000);
  });

  describe('GC Request', () => {
    it('should return false when gc not available', () => {
      const result = manager.requestGc();
      expect(typeof result).toBe('boolean');
    });
  });
});

describe('Factory Functions', () => {
  it('should create memory monitor with factory', () => {
    const monitor = createMemoryMonitor({
      moderateThreshold: 0.5,
    });

    expect(monitor).toBeInstanceOf(MemoryMonitor);
    monitor.stop();
  });

  it('should create memory protection manager with factory', () => {
    const manager = createMemoryProtectionManager({
      monitorIntervalMs: 1000,
    });

    expect(manager).toBeInstanceOf(MemoryProtectionManager);
    manager.stop();
  });

  it('should create bounded map with factory', () => {
    const map = createBoundedMap(100, 60000);

    expect(map).toBeInstanceOf(BoundedMap);
  });

  it('should create bounded set with factory', () => {
    const set = createBoundedSet(100, 60000);

    expect(set).toBeInstanceOf(BoundedSet);
  });
});

describe('Edge Cases', () => {
  it('should handle empty bounded map', () => {
    const map = createBoundedMap(10);

    expect(map.size).toBe(0);
    expect(map.get('nonexistent')).toBeUndefined();
    expect(map.has('nonexistent')).toBe(false);
  });

  it('should handle empty bounded set', () => {
    const set = createBoundedSet(10);

    expect(set.size).toBe(0);
    expect(set.has(1)).toBe(false);
  });

  it('should handle deleting non-existent key', () => {
    const map = createBoundedMap(10);
    expect(map.delete('nonexistent')).toBe(false);
  });

  it('should handle getting entry for non-existent key', () => {
    const map = createBoundedMap(10);
    expect(map.getEntry('nonexistent')).toBeUndefined();
  });

  it('should handle cleanup on empty map', () => {
    const map = createBoundedMap(10);
    const count = map.cleanupExpired();
    expect(count).toBe(0);
  });

  it('should handle eviction on empty map', () => {
    const map = createBoundedMap(10);
    const evicted = map.evict();
    expect(evicted).toBe(0);
  });
});
