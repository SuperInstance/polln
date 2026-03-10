/**
 * Tile Cache - KV-Cache Sharing
 *
 * Enables multiple tiles to share cached key-value states:
 * reducing memory and and improving performance
 *
 * Features:
 * - LRU/LRU cache eviction
 * - Configurable max size
 * - Cache hit/miss tracking
 * - Automatic cleanup of expired entries
 *
 * Part of Phase 2: Infrastructure
 */

import { Tile } from '../core/Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Cache entry
 */
interface CacheEntry {
  key: string;
  value: unknown;
  timestamp: number;
  accessCount: number;
  size: number;
}

/**
 * Cache configuration
 */
export interface TileCacheConfig {
  /** Maximum cache size in bytes */
  maxSize?: number;
  /** Time to live for cache entries in ms */
  ttl?: number;
  /** Enable LRU eviction */
  lruEviction?: boolean;
  /** Enable size tracking */
  trackSize?: boolean;
}

/**
 * Cache statistics
 */
export interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  size: number;
  entries: number;
}

// ============================================================================
// TILE CACHE
// ============================================================================

/**
 * TileCache - Shared KV-cache for tile execution
 *
 * Enables tiles to share cached computation results:
 */
export class TileCache {
  private cache: Map<string, CacheEntry> = new Map();
  private config: Required<TileCacheConfig>;
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    evictions: 0,
    size: 0,
    entries: 0,
  };

  private maxSize: number;
  private ttl: number;

  constructor(config: TileCacheConfig = {}) {
    this.config = {
      maxSize: config.maxSize ?? 100 * 1024 * 1024, // 100MB default
      ttl: config.ttl ?? 60000, // 60 seconds default
      lruEviction: config.lruEviction ?? true,
      trackSize: config.trackSize ?? true,
    };
    this.maxSize = this.config.maxSize;
    this.ttl = this.config.ttl;
  }

  /**
   * Get value from cache
   */
  get<T>(key: string): T | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      return undefined;
    }

    this.stats.hits++;
    entry.accessCount++;

    // Check if expired
    if (Date.now() - entry.timestamp > this.ttl) {
      this.delete(key);
      this.stats.evictions++;
      return undefined;
    }

    return entry.value as T;
  }

  /**
   * Set value in cache
   */
  set<T>(key: string, value: T): void {
    const size = this.calculateSize(value);

    // Check if we need to evict
    while (this.stats.size + size > this.maxSize) {
      this.evictLRU();
    }

    const entry: CacheEntry = {
      key,
      value,
      timestamp: Date.now(),
      accessCount: 1,
      size,
    };

    this.cache.set(key, entry);
    this.stats.entries = this.cache.size;
    this.stats.size += size;
  }

  /**
   * Delete value from cache
   */
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (entry) {
      this.cache.delete(key);
      this.stats.entries--;
      this.stats.size -= entry.size;
      return true;
    }
    return false;
  }

  /**
   * Clear all entries from cache
   */
  clear(): void {
    this.cache.clear();
    this.stats.size = 0;
    this.stats.entries = 0;
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * Evict least recently used entry (LRU)
   */
  private evictLRU(): void {
    let lruKey: string | null;
    let lruAccess = 0;

    for (const [key, entry] of this.cache) {
      if (entry.accessCount < lruAccess) {
        lruKey = key;
        lruAccess = entry.accessCount;
      }
    }

    if (lruKey) {
      this.delete(lruKey);
      this.stats.evictions++;
    }
  }

  /**
   * Calculate size of a value in bytes
   */
  private calculateSize(value: unknown): number {
    return JSON.stringify(value).length;
  }
}

/**
 * Shared instance
 */
export const tileCache = new TileCache();

/**
 * Get global cache size in bytes
 */
export function getCacheSize(): number {
  return tileCache.stats.size;
}
