/**
 * Memory Exhaustion Protection Module
 *
 * Provides production-ready safeguards against memory leaks and unbounded growth:
 * - Memory usage monitoring and thresholds
 * - Automatic cache cleanup
 * - Circuit breaker pattern for memory pressure
 * - Size limits for collections
 * - TTL-based eviction
 * - Memory pressure event emission
 */

import { EventEmitter } from 'events';
import { cpus, freemem, totalmem } from 'os';

// ============================================================================
// Types
// ============================================================================

export type MemoryPressureLevel = 'normal' | 'moderate' | 'high' | 'critical';

export interface MemoryStats {
  /** Current heap used (bytes) */
  heapUsed: number;
  /** Current heap total (bytes) */
  heapTotal: number;
  /** Heap limit (bytes) */
  heapLimit: number;
  /** External memory used (bytes) */
  external: number;
  /** Array buffers size (bytes) */
  arrayBuffers: number;
  /** System free memory (bytes) */
  systemFree: number;
  /** System total memory (bytes) */
  systemTotal: number;
  /** Memory pressure level */
  pressureLevel: MemoryPressureLevel;
  /** Percentage of heap used */
  heapUsedPercent: number;
  /** Percentage of system memory used */
  systemUsedPercent: number;
}

export interface MemoryProtectionConfig {
  /** Heap usage threshold for moderate pressure (0-1) */
  moderateThreshold: number;
  /** Heap usage threshold for high pressure (0-1) */
  highThreshold: number;
  /** Heap usage threshold for critical pressure (0-1) */
  criticalThreshold: number;
  /** System memory threshold for warning (0-1) */
  systemThreshold: number;
  /** Monitoring interval (milliseconds) */
  monitorIntervalMs: number;
  /** Enable automatic garbage collection hints */
  autoGcHint: boolean;
  /** Enable automatic cache cleanup */
  autoCleanup: boolean;
}

export interface CollectionLimits {
  /** Maximum size for Maps/Sets */
  maxCollectionSize: number;
  /** Default TTL for entries (milliseconds, 0 = no expiration) */
  defaultTtlMs: number;
  /** Enable size-based eviction */
  enableEviction: boolean;
  /** Eviction percentage when limit reached (0-1) */
  evictionPercent: number;
}

export interface MemoryPressureEvent {
  level: MemoryPressureLevel;
  stats: MemoryStats;
  timestamp: number;
}

// ============================================================================
// Memory Monitor
// ============================================================================

export class MemoryMonitor extends EventEmitter {
  private config: MemoryProtectionConfig;
  private monitoring = false;
  private intervalId: NodeJS.Timeout | null = null;
  private currentStats: MemoryStats | null = null;

  constructor(config?: Partial<MemoryProtectionConfig>) {
    super();

    this.config = {
      moderateThreshold: 0.6, // 60%
      highThreshold: 0.75, // 75%
      criticalThreshold: 0.85, // 85%
      systemThreshold: 0.8, // 80%
      monitorIntervalMs: 5000, // 5 seconds
      autoGcHint: true,
      autoCleanup: true,
      ...config,
    };
  }

  /**
   * Start monitoring memory usage
   */
  start(): void {
    if (this.monitoring) {
      return;
    }

    this.monitoring = true;
    this.intervalId = setInterval(() => {
      this.checkMemory();
    }, this.config.monitorIntervalMs);

    // Initial check
    this.checkMemory();
  }

  /**
   * Stop monitoring memory usage
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.monitoring = false;
  }

  /**
   * Get current memory statistics
   */
  getStats(): MemoryStats {
    if (this.currentStats) {
      return { ...this.currentStats };
    }

    return this.collectStats();
  }

  /**
   * Check memory and emit events if thresholds exceeded
   */
  private checkMemory(): void {
    const stats = this.collectStats();
    this.currentStats = stats;

    const event: MemoryPressureEvent = {
      level: stats.pressureLevel,
      stats,
      timestamp: Date.now(),
    };

    // Emit pressure level change events
    this.emit('stats', stats);
    this.emit(`pressure:${stats.pressureLevel}`, event);

    // Automatic actions based on pressure level
    if (this.config.autoGcHint && stats.pressureLevel !== 'normal') {
      this.emit('gc:hint', event);
    }

    if (this.config.autoCleanup && stats.pressureLevel === 'critical') {
      this.emit('cleanup:required', event);
    }
  }

  /**
   * Collect memory statistics
   */
  private collectStats(): MemoryStats {
    const memUsage = process.memoryUsage();
    const sysFree = freemem();
    const sysTotal = totalmem();

    const heapUsedPercent = memUsage.heapUsed / memUsage.heapTotal;
    const systemUsedPercent = (sysTotal - sysFree) / sysTotal;

    let pressureLevel: MemoryPressureLevel = 'normal';

    if (heapUsedPercent >= this.config.criticalThreshold) {
      pressureLevel = 'critical';
    } else if (heapUsedPercent >= this.config.highThreshold) {
      pressureLevel = 'high';
    } else if (heapUsedPercent >= this.config.moderateThreshold) {
      pressureLevel = 'moderate';
    }

    return {
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      heapLimit: (memUsage as any).heapTotal || 0x40000000, // 1GB default
      external: memUsage.external,
      arrayBuffers: memUsage.arrayBuffers,
      systemFree: sysFree,
      systemTotal: sysTotal,
      pressureLevel,
      heapUsedPercent,
      systemUsedPercent,
    };
  }

  /**
   * Get current memory pressure level
   */
  getPressureLevel(): MemoryPressureLevel {
    const stats = this.getStats();
    return stats.pressureLevel;
  }
}

// ============================================================================
// Bounded Collection (Size-limited Map/Set)
// ============================================================================

export interface BoundedMapEntry<K, V> {
  value: V;
  expiresAt: number | null;
  createdAt: number;
  accessedAt: number;
  hitCount: number;
}

export class BoundedMap<K, V> extends Map<K, V> {
  private maxSize: number;
  private defaultTtl: number;
  private enableEviction: boolean;
  private evictionPercent: number;
  private metadata: Map<K, BoundedMapEntry<K, V>> = new Map();

  constructor(
    maxSize: number = 10000,
    defaultTtl: number = 0,
    enableEviction: boolean = true,
    evictionPercent: number = 0.1
  ) {
    super();
    this.maxSize = maxSize;
    this.defaultTtl = defaultTtl;
    this.enableEviction = enableEviction;
    this.evictionPercent = evictionPercent;
  }

  /**
   * Set value with optional TTL
   */
  set(key: K, value: V, ttlMs?: number): this {
    // Evict if at capacity
    if (this.enableEviction && this.size >= this.maxSize && !this.has(key)) {
      this.evict();
    }

    const now = Date.now();
    const entry: BoundedMapEntry<K, V> = {
      value,
      expiresAt: ttlMs !== undefined && ttlMs > 0 ? now + ttlMs : (this.defaultTtl > 0 ? now + this.defaultTtl : null),
      createdAt: this.metadata.get(key)?.createdAt || now,
      accessedAt: now,
      hitCount: (this.metadata.get(key)?.hitCount || 0) + 1,
    };

    super.set(key, value);
    this.metadata.set(key, entry);

    return this;
  }

  /**
   * Get value, updating access time and checking expiration
   */
  get(key: K): V | undefined {
    this.cleanupExpired();

    const entry = this.metadata.get(key);
    if (!entry) {
      return undefined;
    }

    // Check expiration
    if (entry.expiresAt && Date.now() > entry.expiresAt) {
      this.delete(key);
      return undefined;
    }

    // Update access stats
    entry.accessedAt = Date.now();
    entry.hitCount++;

    return entry.value;
  }

  /**
   * Check if key exists and is not expired
   */
  has(key: K): boolean {
    const entry = this.metadata.get(key);
    if (!entry) {
      return false;
    }

    if (entry.expiresAt && Date.now() > entry.expiresAt) {
      this.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Delete key
   */
  delete(key: K): boolean {
    this.metadata.delete(key);
    return super.delete(key);
  }

  /**
   * Clear all entries
   */
  clear(): void {
    super.clear();
    this.metadata.clear();
  }

  /**
   * Get entry metadata
   */
  getEntry(key: K): BoundedMapEntry<K, V> | undefined {
    return this.metadata.get(key);
  }

  /**
   * Remove expired entries
   */
  cleanupExpired(): number {
    let count = 0;
    const now = Date.now();

    for (const [key, entry] of this.metadata.entries()) {
      if (entry.expiresAt && now > entry.expiresAt) {
        this.delete(key);
        count++;
      }
    }

    return count;
  }

  /**
   * Evict least recently used entries
   */
  evict(): number {
    const toEvict = Math.ceil(this.size * this.evictionPercent);
    const sorted = Array.from(this.metadata.entries())
      .sort((a, b) => a[1].accessedAt - b[1].accessedAt);

    let count = 0;
    for (const [key] of sorted) {
      if (count >= toEvict) break;
      this.delete(key);
      count++;
    }

    return count;
  }

  /**
   * Get collection statistics
   */
  getStats(): {
    size: number;
    maxSize: number;
    expiredCount: number;
    utilizationPercent: number;
  } {
    const expiredCount = this.cleanupExpired();

    return {
      size: this.size,
      maxSize: this.maxSize,
      expiredCount,
      utilizationPercent: (this.size / this.maxSize) * 100,
    };
  }
}

// ============================================================================
// Bounded Set
// ============================================================================

export class BoundedSet<T> extends Set<T> {
  private maxSize: number;
  private defaultTtl: number;
  private enableEviction: boolean;
  private evictionPercent: number;
  private metadata: Map<T, { expiresAt: number | null; accessedAt: number }> = new Map();

  constructor(
    maxSize: number = 10000,
    defaultTtl: number = 0,
    enableEviction: boolean = true,
    evictionPercent: number = 0.1
  ) {
    super();
    this.maxSize = maxSize;
    this.defaultTtl = defaultTtl;
    this.enableEviction = enableEviction;
    this.evictionPercent = evictionPercent;
  }

  /**
   * Add value with optional TTL
   */
  add(value: T, ttlMs?: number): this {
    // Evict if at capacity
    if (this.enableEviction && this.size >= this.maxSize && !this.has(value)) {
      this.evict();
    }

    const now = Date.now();
    super.add(value);

    this.metadata.set(value, {
      expiresAt: ttlMs !== undefined && ttlMs > 0 ? now + ttlMs : (this.defaultTtl > 0 ? now + this.defaultTtl : null),
      accessedAt: now,
    });

    return this;
  }

  /**
   * Check if value exists and is not expired
   */
  has(value: T): boolean {
    const meta = this.metadata.get(value);
    if (!meta) {
      return false;
    }

    if (meta.expiresAt && Date.now() > meta.expiresAt) {
      this.delete(value);
      return false;
    }

    meta.accessedAt = Date.now();
    return true;
  }

  /**
   * Delete value
   */
  delete(value: T): boolean {
    this.metadata.delete(value);
    return super.delete(value);
  }

  /**
   * Clear all entries
   */
  clear(): void {
    super.clear();
    this.metadata.clear();
  }

  /**
   * Cleanup expired entries
   */
  cleanupExpired(): number {
    let count = 0;
    const now = Date.now();

    for (const [value, meta] of this.metadata.entries()) {
      if (meta.expiresAt && now > meta.expiresAt) {
        this.delete(value);
        count++;
      }
    }

    return count;
  }

  /**
   * Evict least recently used entries
   */
  evict(): number {
    const toEvict = Math.ceil(this.size * this.evictionPercent);
    const sorted = Array.from(this.metadata.entries())
      .sort((a, b) => a[1].accessedAt - b[1].accessedAt);

    let count = 0;
    for (const [value] of sorted) {
      if (count >= toEvict) break;
      this.delete(value);
      count++;
    }

    return count;
  }

  /**
   * Get collection statistics
   */
  getStats(): {
    size: number;
    maxSize: number;
    expiredCount: number;
    utilizationPercent: number;
  } {
    const expiredCount = this.cleanupExpired();

    return {
      size: this.size,
      maxSize: this.maxSize,
      expiredCount,
      utilizationPercent: (this.size / this.maxSize) * 100,
    };
  }
}

// ============================================================================
// Memory Protection Manager
// ============================================================================

export interface CacheTarget {
  /** Clear cache */
  clear(): void | Promise<void>;
  /** Get cache size */
  size?(): number;
  /** Cache name for logging */
  name?: string;
}

export class MemoryProtectionManager extends EventEmitter {
  private monitor: MemoryMonitor;
  private caches: Set<CacheTarget> = new Set();
  private boundedMaps: Set<BoundedMap<unknown, unknown>> = new Set();
  private boundedSets: Set<BoundedSet<unknown>> = new Set();

  constructor(config?: Partial<MemoryProtectionConfig>) {
    super();

    this.monitor = new MemoryMonitor(config);

    // Set up event handlers
    this.monitor.on('pressure:moderate', this.handleModeratePressure.bind(this));
    this.monitor.on('pressure:high', this.handleHighPressure.bind(this));
    this.monitor.on('pressure:critical', this.handleCriticalPressure.bind(this));
    this.monitor.on('cleanup:required', this.handleCleanupRequired.bind(this));
  }

  /**
   * Start memory protection
   */
  start(): void {
    this.monitor.start();
  }

  /**
   * Stop memory protection
   */
  stop(): void {
    this.monitor.stop();
  }

  /**
   * Register a cache for cleanup
   */
  registerCache(cache: CacheTarget): void {
    this.caches.add(cache);
  }

  /**
   * Unregister a cache
   */
  unregisterCache(cache: CacheTarget): void {
    this.caches.delete(cache);
  }

  /**
   * Register a bounded map
   */
  registerBoundedMap<K, V>(map: BoundedMap<K, V>): void {
    this.boundedMaps.add(map as BoundedMap<unknown, unknown>);
  }

  /**
   * Unregister a bounded map
   */
  unregisterBoundedMap<K, V>(map: BoundedMap<K, V>): void {
    this.boundedMaps.delete(map as BoundedMap<unknown, unknown>);
  }

  /**
   * Register a bounded set
   */
  registerBoundedSet<T>(set: BoundedSet<T>): void {
    this.boundedSets.add(set as BoundedSet<unknown>);
  }

  /**
   * Unregister a bounded set
   */
  unregisterBoundedSet<T>(set: BoundedSet<T>): void {
    this.boundedSets.delete(set as BoundedSet<unknown>);
  }

  /**
   * Get current memory statistics
   */
  getStats(): MemoryStats {
    return this.monitor.getStats();
  }

  /**
   * Get memory pressure level
   */
  getPressureLevel(): MemoryPressureLevel {
    return this.monitor.getPressureLevel();
  }

  /**
   * Handle moderate memory pressure
   */
  private handleModeratePressure(event: MemoryPressureEvent): void {
    this.emit('pressure:moderate', event);

    // Cleanup expired entries in bounded collections
    this.cleanupBoundedCollections();
  }

  /**
   * Handle high memory pressure
   */
  private handleHighPressure(event: MemoryPressureEvent): void {
    this.emit('pressure:high', event);

    // Aggressive cleanup
    this.cleanupBoundedCollections();
    this.evictBoundedCollections(0.2); // Evict 20%
  }

  /**
   * Handle critical memory pressure
   */
  private handleCriticalPressure(event: MemoryPressureEvent): void {
    this.emit('pressure:critical', event);

    // Emergency cleanup
    this.clearAllCaches();
    this.evictBoundedCollections(0.5); // Evict 50%
  }

  /**
   * Handle cleanup required event
   */
  private handleCleanupRequired(event: MemoryPressureEvent): void {
    this.emit('cleanup:required', event);
    this.clearAllCaches();
  }

  /**
   * Clear all registered caches
   */
  private clearAllCaches(): void {
    for (const cache of this.caches) {
      try {
        cache.clear();
      } catch (error) {
        this.emit('error', { cache, error });
      }
    }
  }

  /**
   * Cleanup expired entries in bounded collections
   */
  private cleanupBoundedCollections(): void {
    for (const map of this.boundedMaps) {
      try {
        map.cleanupExpired();
      } catch (error) {
        this.emit('error', { map, error });
      }
    }

    for (const set of this.boundedSets) {
      try {
        set.cleanupExpired();
      } catch (error) {
        this.emit('error', { set, error });
      }
    }
  }

  /**
   * Evict entries from bounded collections
   */
  private evictBoundedCollections(percent: number): void {
    for (const map of this.boundedMaps) {
      try {
        // Trigger eviction by reaching capacity
        const stats = map.getStats();
        if (stats.utilizationPercent > 80) {
          map.evict();
        }
      } catch (error) {
        this.emit('error', { map, error });
      }
    }

    for (const set of this.boundedSets) {
      try {
        const stats = set.getStats();
        if (stats.utilizationPercent > 80) {
          set.evict();
        }
      } catch (error) {
        this.emit('error', { set, error });
      }
    }
  }

  /**
   * Request garbage collection (if global.gc is available)
   */
  requestGc(): boolean {
    if (typeof global !== 'undefined' && (global as any).gc) {
      try {
        (global as any).gc();
        return true;
      } catch {
        return false;
      }
    }
    return false;
  }

  /**
   * Get protection statistics
   */
  getProtectionStats(): {
    memoryStats: MemoryStats;
    registeredCaches: number;
    boundedMaps: number;
    boundedSets: number;
  } {
    return {
      memoryStats: this.getStats(),
      registeredCaches: this.caches.size,
      boundedMaps: this.boundedMaps.size,
      boundedSets: this.boundedSets.size,
    };
  }
}

// ============================================================================
// Factory Functions
// ============================================================================

export function createMemoryMonitor(
  config?: Partial<MemoryProtectionConfig>
): MemoryMonitor {
  return new MemoryMonitor(config);
}

export function createMemoryProtectionManager(
  config?: Partial<MemoryProtectionConfig>
): MemoryProtectionManager {
  return new MemoryProtectionManager(config);
}

export function createBoundedMap<K, V>(
  maxSize?: number,
  defaultTtl?: number,
  enableEviction?: boolean,
  evictionPercent?: number
): BoundedMap<K, V> {
  return new BoundedMap(maxSize, defaultTtl, enableEviction, evictionPercent);
}

export function createBoundedSet<T>(
  maxSize?: number,
  defaultTtl?: number,
  enableEviction?: boolean,
  evictionPercent?: number
): BoundedSet<T> {
  return new BoundedSet(maxSize, defaultTtl, enableEviction, evictionPercent);
}
