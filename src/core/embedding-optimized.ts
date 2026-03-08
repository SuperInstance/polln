/**
 * POLLN Behavioral Embedding Space (BES) - Performance Optimized
 *
 * Optimizations:
 * - LRU cache for similarity search results
 * - Pre-computed embedding norms
 * - Batch similarity computation
 * - Early termination for similarity search
 * - Indexed lookup for frequent queries
 *
 * Sprint 7: Performance Optimization
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  PrivacyTier,
  PollenGrainConfig,
  PollenGrain,
  BESConfig,
  PrivacyBudgetStatus,
} from './embedding.js';
import { PRIVACY_PARAMS } from './embedding.js';

// ============================================================================
// LRU CACHE IMPLEMENTATION
// ============================================================================

interface LRUCacheNode<K, V> {
  key: K;
  value: V;
  prev: LRUCacheNode<K, V> | null;
  next: LRUCacheNode<K, V> | null;
}

class LRUCache<K, V> {
  private capacity: number;
  private cache: Map<K, LRUCacheNode<K, V>>;
  private head: LRUCacheNode<K, V> | null;
  private tail: LRUCacheNode<K, V> | null;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.cache = new Map();
    this.head = null;
    this.tail = null;
  }

  get(key: K): V | undefined {
    const node = this.cache.get(key);
    if (!node) return undefined;

    // Move to head (most recently used)
    this.moveToHead(node);
    return node.value;
  }

  set(key: K, value: V): void {
    const existingNode = this.cache.get(key);

    if (existingNode) {
      // Update existing node
      existingNode.value = value;
      this.moveToHead(existingNode);
    } else {
      // Create new node
      const newNode: LRUCacheNode<K, V> = {
        key,
        value,
        prev: null,
        next: null,
      };

      this.cache.set(key, newNode);
      this.addToHead(newNode);

      // Evict least recently used if over capacity
      if (this.cache.size > this.capacity) {
        if (this.tail) {
          this.removeNode(this.tail);
          this.cache.delete(this.tail.key);
        }
      }
    }
  }

  private moveToHead(node: LRUCacheNode<K, V>): void {
    this.removeNode(node);
    this.addToHead(node);
  }

  private addToHead(node: LRUCacheNode<K, V>): void {
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

  private removeNode(node: LRUCacheNode<K, V>): void {
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

  clear(): void {
    this.cache.clear();
    this.head = null;
    this.tail = null;
  }

  size(): number {
    return this.cache.size;
  }
}

// ============================================================================
// SIMILARITY CACHE KEY
// ============================================================================

interface SimilarityCacheKey {
  queryHash: string;
  threshold: number;
  limit: number;
}

function hashVector(vector: number[]): string {
  // Simple hash for caching
  let hash = 0;
  for (let i = 0; i < vector.length; i++) {
    const val = Math.floor(vector[i] * 1000);
    hash = ((hash << 5) - hash) + val;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash.toString(36);
}

// ============================================================================
// OPTIMIZED BES IMPLEMENTATION
// ============================================================================

export interface OptimizedBESConfig extends BESConfig {
  // Caching
  enableSimilarityCache: boolean;
  similarityCacheSize: number;

  // Pre-computation
  precomputeNorms: boolean;

  // Early termination
  earlyTerminationThreshold: number;
  maxCandidatesToConsider: number;
}

interface CachedPollenGrain extends PollenGrain {
  precomputedNorm?: number;
}

export class BESOptimized {
  private config: OptimizedBESConfig;
  private grains: Map<string, CachedPollenGrain> = new Map();
  private privacyBudgets: Map<PrivacyTier, { used: number; total: number }>;

  // Similarity search cache
  private similarityCache: LRUCache<string, PollenGrain[]>;

  constructor(config?: Partial<OptimizedBESConfig>) {
    this.config = {
      defaultDimensionality: 1024,
      defaultPrivacyTier: 'LOCAL',
      maxDimensionality: 1024,
      minDimensionality: 32,
      enableSimilarityCache: true,
      similarityCacheSize: 1000,
      precomputeNorms: true,
      earlyTerminationThreshold: 0.95,
      maxCandidatesToConsider: 100,
      ...config
    };

    // Initialize similarity cache
    this.similarityCache = new LRUCache(this.config.similarityCacheSize);

    // Initialize privacy budgets
    this.privacyBudgets = new Map([
      ['LOCAL', { used: 0, total: Infinity }],
      ['MEADOW', { used: 0, total: 1.0 }],
      ['RESEARCH', { used: 0, total: 0.5 }],
      ['PUBLIC', { used: 0, total: 0.3 }],
    ]);
  }

  /**
   * Create a pollen grain with pre-computed norm
   */
  async createGrain(
    embedding: number[],
    gardenerId: string,
    options?: Partial<PollenGrainConfig>
  ): Promise<PollenGrain> {
    const id = uuidv4();
    const now = Date.now();

    // Determine dimensionality based on privacy tier
    const privacyTier = options?.privacyTier || this.config.defaultPrivacyTier;
    const targetDim = this.getDimensionality(privacyTier);

    // Apply dimensionality reduction if needed
    const reducedEmbedding = this.reduceDimensionality(embedding, targetDim);

    // Apply differential privacy if not local
    const { noisyEmbedding, dpMetadata } = this.applyDP(reducedEmbedding, privacyTier);

    // Pre-compute norm for faster similarity
    const precomputedNorm = this.config.precomputeNorms
      ? this.computeNorm(noisyEmbedding)
      : undefined;

    const grain: CachedPollenGrain = {
      id,
      gardenerId,
      embedding: noisyEmbedding,
      dimensionality: targetDim,
      sourceLogCount: 1,
      privacyTier,
      dpMetadata,
      createdAt: now,
      updatedAt: now,
      precomputedNorm,
    };

    this.grains.set(id, grain);
    this.updatePrivacyBudget(privacyTier, dpMetadata?.epsilon || 0);

    // Invalidate similarity cache when new grain is added
    if (this.config.enableSimilarityCache) {
      this.similarityCache.clear();
    }

    return grain;
  }

  /**
   * Find similar grains with optimizations
   */
  findSimilar(
    query: number[],
    threshold: number = 0.8,
    limit: number = 10
  ): PollenGrain[] {
    // Check cache if enabled
    if (this.config.enableSimilarityCache) {
      const cacheKey = this.generateCacheKey(query, threshold, limit);
      const cached = this.similarityCache.get(cacheKey);
      if (cached) {
        return cached;
      }
    }

    const candidates: { grain: PollenGrain; similarity: number }[] = [];
    const queryNorm = this.computeNorm(query);

    // Early termination: if we find a perfect match, return immediately
    let earlyTerminate = false;

    for (const grain of this.grains.values()) {
      const similarity = this.cosineSimilarityFast(
        query,
        queryNorm,
        grain.embedding,
        grain.precomputedNorm
      );

      if (similarity >= threshold) {
        candidates.push({ grain, similarity });

        // Early termination for near-perfect matches
        if (similarity >= this.config.earlyTerminationThreshold) {
          earlyTerminate = true;
          break;
        }
      }
    }

    let results = candidates
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit)
      .map(c => c.grain);

    // Cache results if enabled
    if (this.config.enableSimilarityCache) {
      const cacheKey = this.generateCacheKey(query, threshold, limit);
      this.similarityCache.set(cacheKey, results);
    }

    return results;
  }

  /**
   * Batch similarity search for multiple queries
   */
  findSimilarBatch(
    queries: number[][],
    threshold: number = 0.8,
    limit: number = 10
  ): PollenGrain[][] {
    return queries.map(query => this.findSimilar(query, threshold, limit));
  }

  /**
   * Fast cosine similarity using pre-computed norms
   */
  private cosineSimilarityFast(
    a: number[],
    normA: number,
    b: number[],
    normB?: number
  ): number {
    if (a.length !== b.length) return 0;

    const normBComputed = normB !== undefined ? normB : this.computeNorm(b);

    if (normA === 0 || normBComputed === 0) return 0;

    // Compute dot product
    let dotProduct = 0;
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
    }

    return dotProduct / (normA * normBComputed);
  }

  /**
   * Compute vector norm (magnitude)
   */
  private computeNorm(vector: number[]): number {
    let sum = 0;
    for (let i = 0; i < vector.length; i++) {
      sum += vector[i] * vector[i];
    }
    return Math.sqrt(sum);
  }

  /**
   * Generate cache key for similarity search
   */
  private generateCacheKey(
    query: number[],
    threshold: number,
    limit: number
  ): string {
    const queryHash = hashVector(query);
    return `${queryHash}:${threshold}:${limit}`;
  }

  /**
   * Get dimensionality for privacy tier
   */
  private getDimensionality(tier: PrivacyTier): number {
    const params = PRIVACY_PARAMS[tier];
    return params?.dimensionality || this.config.defaultDimensionality;
  }

  /**
   * Reduce dimensionality based on privacy tier
   */
  private reduceDimensionality(
    embedding: number[],
    targetDimensionality: number
  ): number[] {
    if (embedding.length <= targetDimensionality) {
      return embedding;
    }

    // Simple truncation for reduction
    // In production, this would use PCA or learned projection
    return embedding.slice(0, targetDimensionality);
  }

  /**
   * Apply differential privacy
   */
  private applyDP(
    embedding: number[],
    tier: PrivacyTier
  ): { noisyEmbedding: number[]; dpMetadata: { epsilon: number; delta: number; noiseScale: number } | undefined } {
    if (tier === 'LOCAL') {
      return { noisyEmbedding: embedding, dpMetadata: undefined };
    }

    const params = PRIVACY_PARAMS[tier];
    const noiseScale = params.epsilon * 0.1;

    // Gaussian mechanism: add noise to each dimension
    const noisyEmbedding = embedding.map(() => {
      const u1 = Math.random();
      const u2 = Math.random();
      // Box-Muller transform for normal distribution
      return embedding[Math.floor(Math.random() * embedding.length)] +
        (Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2) * noiseScale);
    });

    return {
      noisyEmbedding,
      dpMetadata: {
        epsilon: params.epsilon,
        delta: params.delta,
        noiseScale,
      }
    };
  }

  /**
   * Update privacy budget
   */
  private updatePrivacyBudget(tier: PrivacyTier, used: number): void {
    const budget = this.privacyBudgets.get(tier);
    if (budget) {
      budget.used += used;
      if (budget.used > budget.total) {
        console.warn(`Privacy budget exhausted for ${tier}`);
      }
    }
  }

  /**
   * Get pollen grain
   */
  getGrain(id: string): PollenGrain | undefined {
    return this.grains.get(id);
  }

  /**
   * Get privacy budget status
   */
  getPrivacyBudgetStatus(tier: PrivacyTier): PrivacyBudgetStatus | undefined {
    const budget = this.privacyBudgets.get(tier);
    if (!budget) return undefined;

    return {
      tier,
      used: budget.used,
      total: budget.total,
      remaining: budget.total === Infinity ? Infinity : budget.total - budget.used,
    };
  }

  /**
   * Get statistics
   */
  getStats(): {
    totalGrains: number;
    grainsByTier: Record<PrivacyTier, number>;
    privacyBudgetStatus: Record<PrivacyTier, PrivacyBudgetStatus>;
    cacheSize: number;
    cacheHitRate: number;
  } {
    const grainsByTier: Record<PrivacyTier, number> = {
      LOCAL: 0,
      MEADOW: 0,
      RESEARCH: 0,
      PUBLIC: 0,
    };

    for (const grain of this.grains.values()) {
      grainsByTier[grain.privacyTier]++;
    }

    const privacyBudgetStatus: Record<PrivacyTier, PrivacyBudgetStatus> = {} as Record<PrivacyTier, PrivacyBudgetStatus>;
    for (const tier of this.privacyBudgets.keys()) {
      const status = this.getPrivacyBudgetStatus(tier);
      if (status) privacyBudgetStatus[tier] = status;
    }

    return {
      totalGrains: this.grains.size,
      grainsByTier,
      privacyBudgetStatus,
      cacheSize: this.similarityCache.size(),
      cacheHitRate: 0, // Would need tracking for accurate rate
    };
  }

  /**
   * Clear all caches
   */
  clearCache(): void {
    this.similarityCache.clear();
  }
}
