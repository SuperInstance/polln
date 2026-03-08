/**
 * Enhanced LRU Cache for KV Anchors
 *
 * Optimizations:
 * - O(1) get/put operations with doubly-linked list
 * - Configurable capacity with eviction policies
 * - Statistics tracking for cache performance
 * - Batch operations for efficiency
 * - Memory-aware eviction based on anchor size
 *
 * Sprint 7: Performance Optimization
 */

import type { KVAnchor, KVCacheSegment } from './kvanchor.js';

// ============================================================================
// LRU CACHE NODE
// ============================================================================

interface LRUNode<K, V> {
  key: K;
  value: V;
  size: number; // Approximate memory size in bytes
  prev: LRUNode<K, V> | null;
  next: LRUNode<K, V> | null;
  accessCount: number;
  lastAccess: number;
}

// ============================================================================
// LRU CACHE STATISTICS
// ============================================================================

export interface LRUStats {
  hits: number;
  misses: number;
  hitRate: number;
  evictions: number;
  currentSize: number;
  currentMemory: number;
  avgAccessCount: number;
}

// ============================================================================
// EVICTION POLICY
// ============================================================================

export type EvictionPolicy = 'lru' | 'lfu' | 'size' | 'adaptive';

export interface LRUCacheConfig<K, V> {
  capacity: number; // Maximum number of items
  maxMemoryMB?: number; // Maximum memory in MB
  evictionPolicy: EvictionPolicy;
  enableStats: boolean;
  computeSize?: (value: V) => number; // Function to compute value size
}

// ============================================================================
// ENHANCED LRU CACHE
// ============================================================================

export class LRUCache<K, V> {
  private capacity: number;
  private maxMemory?: number;
  private evictionPolicy: EvictionPolicy;
  private enableStats: boolean;
  private computeSize?: (value: V) => number;

  private cache: Map<K, LRUNode<K, V>>;
  private head: LRUNode<K, V> | null = null;
  private tail: LRUNode<K, V> | null = null;

  private currentMemory: number = 0;

  // Statistics
  private hits: number = 0;
  private misses: number = 0;
  private evictions: number = 0;

  constructor(config: LRUCacheConfig<K, V>) {
    this.capacity = config.capacity;
    this.maxMemory = config.maxMemoryMB ? config.maxMemoryMB * 1024 * 1024 : undefined;
    this.evictionPolicy = config.evictionPolicy;
    this.enableStats = config.enableStats;
    this.computeSize = config.computeSize;

    this.cache = new Map();
  }

  /**
   * Get value from cache
   */
  get(key: K): V | undefined {
    const node = this.cache.get(key);

    if (!node) {
      if (this.enableStats) {
        this.misses++;
      }
      return undefined;
    }

    if (this.enableStats) {
      this.hits++;
      node.accessCount++;
      node.lastAccess = Date.now();
    }

    // Move to head (most recently used)
    this.moveToHead(node);

    return node.value;
  }

  /**
   * Set value in cache
   */
  set(key: K, value: V): void {
    const existingNode = this.cache.get(key);
    const size = this.computeSize ? this.computeSize(value) : this.estimateSize(value);

    if (existingNode) {
      // Update existing node
      this.currentMemory -= existingNode.size;
      existingNode.value = value;
      existingNode.size = size;
      existingNode.lastAccess = Date.now();

      if (this.enableStats) {
        existingNode.accessCount++;
      }

      this.currentMemory += size;
      this.moveToHead(existingNode);

      // Check memory constraint
      if (this.maxMemory && this.currentMemory > this.maxMemory) {
        this.evictUntilMemoryFits();
      }
    } else {
      // Create new node
      const newNode: LRUNode<K, V> = {
        key,
        value,
        size,
        prev: null,
        next: null,
        accessCount: 1,
        lastAccess: Date.now(),
      };

      this.cache.set(key, newNode);
      this.addToHead(newNode);
      this.currentMemory += size;

      // Evict if over capacity or memory
      if (this.cache.size > this.capacity || (this.maxMemory && this.currentMemory > this.maxMemory)) {
        this.evict();
      }
    }
  }

  /**
   * Check if key exists
   */
  has(key: K): boolean {
    return this.cache.has(key);
  }

  /**
   * Delete key from cache
   */
  delete(key: K): boolean {
    const node = this.cache.get(key);
    if (!node) return false;

    this.removeNode(node);
    this.cache.delete(key);
    this.currentMemory -= node.size;
    return true;
  }

  /**
   * Clear all entries
   */
  clear(): void {
    this.cache.clear();
    this.head = null;
    this.tail = null;
    this.currentMemory = 0;

    if (this.enableStats) {
      this.hits = 0;
      this.misses = 0;
      this.evictions = 0;
    }
  }

  /**
   * Get multiple keys (batch operation)
   */
  getBatch(keys: K[]): Map<K, V> {
    const result = new Map<K, V>();
    for (const key of keys) {
      const value = this.get(key);
      if (value !== undefined) {
        result.set(key, value);
      }
    }
    return result;
  }

  /**
   * Set multiple key-value pairs (batch operation)
   */
  setBatch(entries: [K, V][]): void {
    for (const [key, value] of entries) {
      this.set(key, value);
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): LRUStats {
    const totalAccesses = this.hits + this.misses;
    const hitRate = totalAccesses > 0 ? this.hits / totalAccesses : 0;

    let avgAccessCount = 0;
    if (this.enableStats && this.cache.size > 0) {
      let totalAccessCount = 0;
      for (const node of this.cache.values()) {
        totalAccessCount += node.accessCount;
      }
      avgAccessCount = totalAccessCount / this.cache.size;
    }

    return {
      hits: this.hits,
      misses: this.misses,
      hitRate,
      evictions: this.evictions,
      currentSize: this.cache.size,
      currentMemory: this.currentMemory,
      avgAccessCount,
    };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    if (this.enableStats) {
      this.hits = 0;
      this.misses = 0;
      this.evictions = 0;
    }
  }

  /**
   * Get current size
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Get current memory usage in bytes
   */
  getMemoryUsage(): number {
    return this.currentMemory;
  }

  // ==========================================================================
  // PRIVATE METHODS
  // ==========================================================================

  private moveToHead(node: LRUNode<K, V>): void {
    this.removeNode(node);
    this.addToHead(node);
  }

  private addToHead(node: LRUNode<K, V>): void {
    node.prev = null;
    node.next = this.head;

    if (this.head) {
      this.head.prev = node;
    }

    this.head = node;

    if (!this.tail) {
      this.tail = node;
    }
  }

  private removeNode(node: LRUNode<K, V>): void {
    if (node.prev) {
      node.prev.next = node.next;
    } else {
      this.head = node.next;
    }

    if (node.next) {
      node.next.prev = node.prev;
    } else {
      this.tail = node.prev;
    }
  }

  private evict(): void {
    if (!this.tail) return;

    // Determine eviction target based on policy
    let targetNode: LRUNode<K, V> = this.tail;

    if (this.evictionPolicy === 'lfu' || this.evictionPolicy === 'adaptive') {
      // Find least frequently used node
      let minAccessCount = Infinity;
      let currentNode = this.tail;

      while (currentNode) {
        if (currentNode.accessCount < minAccessCount) {
          minAccessCount = currentNode.accessCount;
          targetNode = currentNode;
        }
        currentNode = currentNode.prev!;
      }
    } else if (this.evictionPolicy === 'size') {
      // Find largest node
      let maxSize = 0;
      let currentNode = this.tail;

      while (currentNode) {
        if (currentNode.size > maxSize) {
          maxSize = currentNode.size;
          targetNode = currentNode;
        }
        currentNode = currentNode.prev!;
      }
    }

    // Evict target node
    this.removeNode(targetNode);
    this.cache.delete(targetNode.key);
    this.currentMemory -= targetNode.size;

    if (this.enableStats) {
      this.evictions++;
    }
  }

  private evictUntilMemoryFits(): void {
    while (this.maxMemory && this.currentMemory > this.maxMemory && this.tail) {
      this.evict();
    }
  }

  private estimateSize(value: any): number {
    // Rough estimation: assume each reference is 8 bytes + value size
    if (typeof value === 'number') return 8;
    if (typeof value === 'string') return value.length * 2;
    if (typeof value === 'boolean') return 4;
    if (Array.isArray(value)) return value.length * 8;
    if (typeof value === 'object' && value !== null) {
      return Object.keys(value).length * 16;
    }
    return 64; // Default estimate
  }
}

// ============================================================================
// KV ANCHOR LRU CACHE SPECIALIZATION
// ============================================================================

export interface KVAnchorCacheConfig {
  capacity: number;
  maxMemoryMB?: number;
  evictionPolicy: EvictionPolicy;
  enableStats: boolean;
}

export class KVAnchorLRUCache extends LRUCache<string, KVAnchor> {
  constructor(config: KVAnchorCacheConfig) {
    super({
      capacity: config.capacity,
      maxMemoryMB: config.maxMemoryMB,
      evictionPolicy: config.evictionPolicy,
      enableStats: config.enableStats,
      computeSize: (anchor: KVAnchor) => {
        // Estimate KVAnchor size
        let size = 100; // Base metadata size

        // Compressed keys and values (Float32Array)
        size += anchor.compressedKeys.byteLength;
        size += anchor.compressedValues.byteLength;

        // Embedding
        size += anchor.embedding.length * 8; // Double for each number

        return size;
      },
    });
  }

  /**
   * Get frequently accessed anchors (high access count)
   */
  getFrequentlyAccessed(threshold: number = 10): KVAnchor[] {
    const frequent: KVAnchor[] = [];

    for (const node of this['cache'].values()) {
      if (node.accessCount >= threshold) {
        frequent.push(node.value);
      }
    }

    return frequent.sort((a, b) => b.usageCount - a.usageCount);
  }

  /**
   * Get cache efficiency metrics
   */
  getEfficiencyMetrics(): {
    hitRate: number;
    memoryEfficiency: number;
    avgAnchorSize: number;
    topAnchors: KVAnchor[];
  } {
    const stats = this.getStats();
    const currentMemory = this.getMemoryUsage();
    const maxSize = this['maxMemory'] || currentMemory;

    const avgAnchorSize = this.size() > 0 ? currentMemory / this.size() : 0;
    const topAnchors = this.getFrequentlyAccessed(5);

    return {
      hitRate: stats.hitRate,
      memoryEfficiency: currentMemory / maxSize,
      avgAnchorSize,
      topAnchors,
    };
  }
}
