# POLLN Data Blueprint - Implementation Guide

**Version**: 1.0.0
**Last Updated**: 2026-03-08
**Author**: Architect-Data (Planning Team)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Examples](#quick-start-examples)
3. [Data Model Implementations](#data-model-implementations)
4. [Storage Patterns](#storage-patterns)
5. [Serialization/Deserialization](#serializationdeserialization)
6. [Edge Cases](#edge-cases)
7. [Concurrent Access Patterns](#concurrent-access-patterns)
8. [Performance Optimization](#performance-optimization)
9. [Test Scenarios](#test-scenarios)

---

## Introduction

This blueprint provides implementation guidance for glm-4.7 agents working with POLLN's data systems. It includes code examples, edge case handling, and test scenarios for all major data operations.

### Key Files Reference

| Module | Path | Purpose |
|--------|------|---------|
| `embedding.ts` | `src/core/embedding.ts` | PollenGrain creation, BES |
| `kvanchor.ts` | `src/core/kvanchor.ts` | KV-anchor pool, matching |
| `ann-index.ts` | `src/core/ann-index.ts` | ANN search algorithms |
| `cacheutils.ts` | `src/core/cacheutils.ts` | Cache manipulation utilities |
| `lmcache-adapter.ts` | `src/core/lmcache-adapter.ts` | LMCache backend bridge |
| `types.ts` | `src/core/types.ts` | Core type definitions |

---

## Quick Start Examples

### Creating a PollenGrain

```typescript
import { BES, PollenGrain, PrivacyTier } from './embedding.js';

// Initialize the Behavioral Embedding Space
const bes = new BES({
  defaultDimensionality: 1024,
  defaultPrivacyTier: 'LOCAL',
  maxDimensionality: 1024,
  minDimensionality: 32,
});

// Create a pollen grain from a raw embedding
const rawEmbedding = new Array(1024).fill(0).map(() => Math.random() * 2 - 1);

const grain = await bes.createGrain(rawEmbedding, 'gardener-001', {
  gardenerId: 'gardener-001',
  dimensionality: 1024,
  privacyTier: 'LOCAL',
});

console.log(`Created grain: ${grain.id}`);
console.log(`Dimensionality: ${grain.dimensionality}`);
console.log(`L2 Norm: ${Math.sqrt(grain.embedding.reduce((s, v) => s + v * v, 0))}`);
// Should output: L2 Norm: ~1.0 (normalized)
```

### Creating a KVAnchor

```typescript
import { KVAnchorPool, KVCacheSegment } from './kvanchor.js';

// Initialize anchor pool
const anchorPool = new KVAnchorPool({
  maxAnchors: 1000,
  embeddingDim: 128,
  keyProjectionDim: 64,
  valueProjectionDim: 64,
  quantizationBits: 8,
  enableANN: true,
  enableClustering: true,
  enableLRU: true,
});

// Create a KV-cache segment
const segment: KVCacheSegment = {
  layerId: 0,
  segmentId: 'seg-001',
  tokens: [1, 2, 3, 4, 5],
  keyCache: Array(10).fill(0).map(() => Array(64).fill(0).map(() => Math.random())),
  valueCache: Array(10).fill(0).map(() => Array(64).fill(0).map(() => Math.random())),
  metadata: {
    createdAt: Date.now(),
    modelHash: 'model-v1',
    agentId: 'agent-001',
    turnNumber: 1,
    position: 0,
    length: 10,
  },
};

// Compute embedding (simplified - use actual embedding model)
const embedding = new Array(128).fill(0).map(() => Math.random() * 2 - 1);

// Create anchor
const anchor = await anchorPool.createAnchor(segment, embedding);

console.log(`Created anchor: ${anchor.anchorId}`);
console.log(`Quality score: ${anchor.qualityScore}`);
console.log(`Compression ratio: ${anchor.compressionRatio}`);
```

### Finding Similar Anchors

```typescript
import { KVAnchorPool } from './kvanchor.js';

const anchorPool = new KVAnchorPool({ enableANN: true });

// ... add anchors to pool ...

// Search for similar anchors
const queryEmbedding = new Array(128).fill(0).map(() => Math.random());
const similarAnchors = anchorPool.findSimilarAnchors(queryEmbedding, 0, 0.8);

console.log(`Found ${similarAnchors.length} similar anchors`);
for (const anchor of similarAnchors) {
  console.log(`- ${anchor.anchorId} (quality: ${anchor.qualityScore.toFixed(2)})`);
}
```

---

## Data Model Implementations

### PollenGrain with Privacy Tiers

```typescript
import { BES, PRIVACY_PARAMS, PrivacyTier } from './embedding.js';

async function createGrainWithPrivacy(
  rawEmbedding: number[],
  gardenerId: string,
  privacyTier: PrivacyTier
) {
  const params = PRIVACY_PARAMS[privacyTier];

  const bes = new BES({
    defaultDimensionality: params.dimensionality,
    defaultPrivacyTier: privacyTier,
  });

  const grain = await bes.createGrain(rawEmbedding, gardenerId, {
    privacyTier,
    dimensionality: params.dimensionality,
  });

  // Verify differential privacy was applied
  if (privacyTier !== 'LOCAL') {
    console.log('DP Metadata:', grain.dpMetadata);
    console.log(`Epsilon consumed: ${grain.dpMetadata?.epsilon}`);
  }

  return grain;
}

// Usage examples
const localGrain = await createGrainWithPrivacy(rawEmb, 'user-1', 'LOCAL');
const publicGrain = await createGrainWithPrivacy(rawEmb, 'user-1', 'PUBLIC');
```

### KVAnchor with Custom Quantization

```typescript
import { KVAnchorPool, QuantizationMethod } from './kvanchor.js';

const anchorPool = new KVAnchorPool({
  quantizationBits: 4, // 4-bit quantization for higher compression
  compressionMethod: 'kmeans', // K-means quantization
  enableAdvancedCompression: true,
});

// Compression method comparison:
// - uniform: Simple, fast, ~8x compression
// - kmeans: Better quality, slower, ~10x compression
// - product: Best for high-dim, ~12x compression
```

### ANN Index Selection

```typescript
import { ANNIndex, ANNAlgorithm, benchmarkANNIndex } from './ann-index.js';

// Auto-select based on data characteristics
const autoIndex = new ANNIndex({
  algorithm: 'auto',
  dimension: 128,
});

// Explicit algorithm selection
const hnswIndex = new ANNIndex({
  algorithm: 'hnsw',
  dimension: 128,
  hnsw: {
    M: 16,              // Connections per node
    efConstruction: 200, // Build-time candidate list size
    efSearch: 50,       // Search-time candidate list size
  },
});

// Benchmark to choose optimal algorithm
const embeddings = generateTestEmbeddings(10000, 128);
const queries = generateTestEmbeddings(100, 128);

const benchmark = benchmarkANNIndex(embeddings, queries, 10);
console.log(`Speedup: ${benchmark.speedup.toFixed(2)}x`);
console.log(`Recall: ${(benchmark.recall * 100).toFixed(1)}%`);
console.log(`Algorithm: ${benchmark.buildStats.algorithm}`);
```

---

## Storage Patterns

### In-Memory Storage (Default)

```typescript
// PollenGrains stored in Map<string, PollenGrain>
class BES {
  private grains: Map<string, PollenGrain> = new Map();
  private privacyBudgets: Map<PrivacyTier, { used: number; total: number }>;
}

// KVAnchors stored with multiple indices for fast lookup
class KVAnchorPool {
  private anchors: Map<string, KVAnchor> = new Map();
  private layerIndices: Map<number, Set<string>> = new Map();
  private lruList: string[] = [];
  private clusters: Map<string, AnchorCluster> = new Map();
}
```

### LRU Eviction Pattern

```typescript
class KVAnchorPool {
  private lruList: string[] = [];
  private lruIndex: Map<string, number> = new Map();

  private addToLRU(anchorId: string): void {
    // Remove from current position if exists
    if (this.lruIndex.has(anchorId)) {
      const oldIndex = this.lruIndex.get(anchorId)!;
      this.lruList.splice(oldIndex, 1);
    }

    // Add to front (most recently used)
    this.lruList.unshift(anchorId);
    this.lruIndex.set(anchorId, 0);

    // Update indices for shifted items
    for (let i = 1; i < this.lruList.length; i++) {
      this.lruIndex.set(this.lruList[i], i);
    }
  }

  private lruEviction(): void {
    const toRemove = this.anchors.size - this.config.maxAnchors;
    for (let i = 0; i < toRemove; i++) {
      const anchorId = this.lruList.pop()!;
      this.lruIndex.delete(anchorId);
      this.removeAnchor(anchorId);
    }
  }
}
```

### Clustering Pattern

```typescript
class KVAnchorPool {
  private clusters: Map<string, AnchorCluster> = new Map();
  private anchorToCluster: Map<string, string> = new Map();

  private assignToCluster(anchor: KVAnchor): void {
    const layerClusters = Array.from(this.clusters.values())
      .filter(c => c.layerId === anchor.layerId);

    if (layerClusters.length === 0) {
      this.createClusterForAnchor(anchor);
      return;
    }

    // Find closest cluster
    let closestCluster: AnchorCluster | null = null;
    let minDistance = Infinity;

    for (const cluster of layerClusters) {
      const distance = this.euclideanDistance(anchor.embedding, cluster.centroid);
      if (distance < minDistance) {
        minDistance = distance;
        closestCluster = cluster;
      }
    }

    if (closestCluster && minDistance < this.config.clusterThreshold) {
      closestCluster.anchorIds.add(anchor.anchorId);
      anchor.clusterId = closestCluster.clusterId;
      this.anchorToCluster.set(anchor.anchorId, closestCluster.clusterId);
      this.updateClusterCentroid(closestCluster);
    } else {
      this.createClusterForAnchor(anchor);
    }
  }
}
```

---

## Serialization/Deserialization

### Full Serialization Example

```typescript
import { KVCacheSerializer, SerializedLMCache } from './lmcache-adapter.js';

const serializer = new KVCacheSerializer();

// Serialize anchor for storage/transfer
function serializeAnchor(anchor: KVAnchor): string {
  const serialized = serializer.serialize(anchor);
  return JSON.stringify(serialized);
}

// Deserialize anchor from storage
function deserializeAnchor(json: string): KVAnchor {
  const serialized: SerializedLMCache = JSON.parse(json);
  return serializer.deserialize(serialized);
}

// Batch serialization
function serializeAnchors(anchors: KVAnchor[]): string[] {
  const serialized = serializer.serializeBatch(anchors);
  return serialized.map(s => JSON.stringify(s));
}
```

### Tensor Serialization

```typescript
class KVCacheSerializer {
  serializeTensor(data: Float32Array): SerializedTensor {
    const buffer = data.buffer as ArrayBuffer;
    const base64 = this.bufferToBase64(buffer);

    return {
      dtype: 'float32',
      shape: [data.length],
      data: base64,
      compressed: true,
    };
  }

  deserializeTensor(tensor: SerializedTensor): Float32Array {
    const buffer = this.base64ToBuffer(tensor.data);

    if (tensor.dtype === 'float32') {
      const float32Array = new Float32Array(buffer.byteLength / 4);
      const view = new DataView(buffer);
      for (let i = 0; i < float32Array.length; i++) {
        float32Array[i] = view.getFloat32(i * 4, true);
      }
      return float32Array;
    }

    throw new Error(`Unsupported dtype: ${tensor.dtype}`);
  }

  private bufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (const byte of bytes) {
      binary += String.fromCharCode(byte);
    }
    return btoa(binary);
  }

  private base64ToBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
}
```

---

## Edge Cases

### 1. Large Embeddings (>1024 dimensions)

```typescript
// Problem: Embedding exceeds maximum dimensionality
// Solution: Automatic dimensionality reduction

class BES {
  private reduceDimensionality(embedding: number[], targetDim: number): number[] {
    if (embedding.length <= targetDim) {
      return embedding;
    }

    // Simple truncation (production: use PCA or learned projection)
    return embedding.slice(0, targetDim);
  }
}

// Test case
const largeEmbedding = new Array(2048).fill(0).map(() => Math.random());
const grain = await bes.createGrain(largeEmbedding, 'user-1');
console.log(grain.dimensionality); // Should be 1024 (max)
```

### 2. Empty KV-Cache Segments

```typescript
// Problem: Segment has no tokens
// Solution: Return null or throw based on configuration

async function createAnchorSafe(
  segment: KVCacheSegment,
  embedding: number[]
): Promise<KVAnchor | null> {
  if (segment.tokens.length === 0) {
    console.warn('Empty segment, skipping anchor creation');
    return null;
  }

  if (segment.keyCache.length === 0 || segment.valueCache.length === 0) {
    console.warn('Empty KV cache, skipping anchor creation');
    return null;
  }

  return anchorPool.createAnchor(segment, embedding);
}
```

### 3. Privacy Budget Exhaustion

```typescript
// Problem: Privacy budget depleted for tier
// Solution: Warn and degrade gracefully

class BES {
  private updatePrivacyBudget(tier: PrivacyTier, used: number): void {
    const budget = this.privacyBudgets.get(tier);
    if (budget) {
      budget.used += used;
      if (budget.used > budget.total) {
        console.warn(`Privacy budget exhausted for ${tier}`);
        // Options:
        // 1. Switch to higher privacy tier
        // 2. Reject the grain creation
        // 3. Continue with degraded privacy
      }
    }
  }
}

// Check budget before creating grain
function canCreateGrain(tier: PrivacyTier): boolean {
  const status = bes.getPrivacyBudgetStatus(tier);
  return status !== undefined && status.remaining > 0;
}
```

### 4. Zero-Norm Embeddings

```typescript
// Problem: Embedding has zero L2 norm (division by zero)
// Solution: Handle edge case in normalization

function normalizeEmbedding(embedding: number[]): number[] {
  const norm = Math.sqrt(embedding.reduce((sum, v) => sum + v * v, 0));

  if (norm === 0) {
    // Option 1: Return small random vector
    console.warn('Zero-norm embedding, returning random unit vector');
    const random = new Array(embedding.length)
      .fill(0)
      .map(() => Math.random() * 2 - 1);
    const randomNorm = Math.sqrt(random.reduce((s, v) => s + v * v, 0));
    return random.map(v => v / randomNorm);
  }

  return embedding.map(v => v / norm);
}
```

### 5. Mismatched Dimensions

```typescript
// Problem: Query embedding dimension doesn't match index
// Solution: Pad or truncate with warning

function matchDimensions(embedding: number[], targetDim: number): number[] {
  if (embedding.length === targetDim) {
    return embedding;
  }

  if (embedding.length > targetDim) {
    console.warn(`Truncating embedding from ${embedding.length} to ${targetDim}`);
    return embedding.slice(0, targetDim);
  }

  console.warn(`Padding embedding from ${embedding.length} to ${targetDim}`);
  return [...embedding, ...new Array(targetDim - embedding.length).fill(0)];
}
```

---

## Concurrent Access Patterns

### Read-Write Lock Pattern

```typescript
// For concurrent access to shared data structures

class ConcurrentKVAnchorPool {
  private anchors: Map<string, KVAnchor> = new Map();
  private readers = 0;
  private writer = false;
  private readQueue: (() => void)[] = [];
  private writeQueue: (() => void)[] = [];

  async read<T>(fn: () => T): Promise<T> {
    await this.acquireRead();
    try {
      return fn();
    } finally {
      this.releaseRead();
    }
  }

  async write<T>(fn: () => T): Promise<T> {
    await this.acquireWrite();
    try {
      return fn();
    } finally {
      this.releaseWrite();
    }
  }

  private async acquireRead(): Promise<void> {
    if (this.writer || this.writeQueue.length > 0) {
      await new Promise<void>(resolve => this.readQueue.push(resolve));
    }
    this.readers++;
  }

  private releaseRead(): void {
    this.readers--;
    if (this.readers === 0 && this.writeQueue.length > 0) {
      const next = this.writeQueue.shift()!;
      next();
    }
  }

  private async acquireWrite(): Promise<void> {
    if (this.writer || this.readers > 0) {
      await new Promise<void>(resolve => this.writeQueue.push(resolve));
    }
    this.writer = true;
  }

  private releaseWrite(): void {
    this.writer = false;
    // Prefer readers to prevent writer starvation
    while (this.readQueue.length > 0) {
      const next = this.readQueue.shift()!;
      next();
    }
    if (this.writeQueue.length > 0) {
      const next = this.writeQueue.shift()!;
      next();
    }
  }
}
```

### Atomic Operations

```typescript
// For single atomic operations without full locking

class AtomicCounter {
  private value = 0;
  private pending = Promise.resolve();

  async increment(): Promise<number> {
    return this.atomic(() => ++this.value);
  }

  async decrement(): Promise<number> {
    return this.atomic(() => --this.value);
  }

  private async atomic<T>(fn: () => T): Promise<T> {
    const result = this.pending.then(() => fn());
    this.pending = result.then(() => {});
    return result;
  }
}
```

### Batch Processing with Concurrency Limit

```typescript
async function processBatchWithConcurrency<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  maxConcurrency: number = 10
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let index = 0;

  async function worker(): Promise<void> {
    while (index < items.length) {
      const currentIndex = index++;
      results[currentIndex] = await processor(items[currentIndex]);
    }
  }

  const workers = Array(Math.min(maxConcurrency, items.length))
    .fill(0)
    .map(() => worker());

  await Promise.all(workers);
  return results;
}

// Usage
const anchors = await processBatchWithConcurrency(
  segments,
  async (segment) => anchorPool.createAnchor(segment, getEmbedding(segment)),
  5 // Max 5 concurrent operations
);
```

---

## Performance Optimization

### Memory-Efficient Embedding Storage

```typescript
// Use Float32Array instead of number[] for large embeddings

class OptimizedBES {
  private embeddings: Map<string, Float32Array> = new Map();

  createGrainOptimized(rawEmbedding: Float32Array, gardenerId: string): PollenGrain {
    // Avoid copying if possible
    const normalized = this.normalizeInPlace(Float32Array.from(rawEmbedding));

    const grain: PollenGrain = {
      id: uuidv4(),
      gardenerId,
      embedding: Array.from(normalized), // Convert only for interface
      dimensionality: normalized.length,
      sourceLogCount: 1,
      privacyTier: 'LOCAL',
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    // Store optimized version
    this.embeddings.set(grain.id, normalized);

    return grain;
  }

  private normalizeInPlace(arr: Float32Array): Float32Array {
    let norm = 0;
    for (let i = 0; i < arr.length; i++) {
      norm += arr[i] * arr[i];
    }
    norm = Math.sqrt(norm);

    if (norm > 0) {
      for (let i = 0; i < arr.length; i++) {
        arr[i] /= norm;
      }
    }

    return arr;
  }
}
```

### ANN Index Caching

```typescript
class CachedANNIndex {
  private index: ANNIndex;
  private queryCache: Map<string, SearchResult[]> = new Map();
  private cacheHits = 0;
  private cacheMisses = 0;

  search(query: number[], k: number): SearchResult[] {
    const cacheKey = this.hashQuery(query, k);

    if (this.queryCache.has(cacheKey)) {
      this.cacheHits++;
      return this.queryCache.get(cacheKey)!;
    }

    this.cacheMisses++;
    const results = this.index.searchWithScores(query, k);
    this.queryCache.set(cacheKey, results);

    // Evict old entries if cache is too large
    if (this.queryCache.size > 10000) {
      const keys = Array.from(this.queryCache.keys());
      for (let i = 0; i < keys.length / 2; i++) {
        this.queryCache.delete(keys[i]);
      }
    }

    return results;
  }

  private hashQuery(query: number[], k: number): string {
    // Simple hash - use proper hash in production
    return `${query.slice(0, 8).map(v => v.toFixed(4)).join(',')}:${k}`;
  }

  getCacheStats() {
    return {
      hits: this.cacheHits,
      misses: this.cacheMisses,
      hitRate: this.cacheHits / (this.cacheHits + this.cacheMisses),
      size: this.queryCache.size,
    };
  }
}
```

### Lazy ANN Index Rebuilding

```typescript
class LazyANNIndexManager {
  private index: ANNIndex | null = null;
  private pendingRebuild = false;
  private additionsSinceRebuild = 0;
  private rebuildThreshold = 100;

  search(query: number[], k: number): SearchResult[] {
    if (this.pendingRebuild || !this.index) {
      this.rebuildIndex();
    }
    return this.index!.searchWithScores(query, k);
  }

  add(embedding: number[]): void {
    if (this.index) {
      this.index.add(embedding);
      this.additionsSinceRebuild++;

      if (this.additionsSinceRebuild >= this.rebuildThreshold) {
        this.pendingRebuild = true;
      }
    }
  }

  private rebuildIndex(): void {
    // Collect all embeddings and rebuild
    // This is more efficient than incremental updates for HNSW
    this.index = new ANNIndex({ algorithm: 'hnsw' });
    // ... rebuild from source data ...
    this.pendingRebuild = false;
    this.additionsSinceRebuild = 0;
  }
}
```

---

## Test Scenarios

### Unit Tests

```typescript
describe('PollenGrain', () => {
  test('should create grain with correct dimensionality', async () => {
    const bes = new BES();
    const embedding = new Array(1024).fill(0).map(() => Math.random());
    const grain = await bes.createGrain(embedding, 'test-user');

    expect(grain.dimensionality).toBe(1024);
    expect(grain.embedding.length).toBe(1024);
  });

  test('should normalize embedding to unit length', async () => {
    const bes = new BES();
    const embedding = new Array(1024).fill(1); // Non-normalized
    const grain = await bes.createGrain(embedding, 'test-user');

    const norm = Math.sqrt(grain.embedding.reduce((s, v) => s + v * v, 0));
    expect(norm).toBeCloseTo(1.0, 5);
  });

  test('should apply differential privacy for non-LOCAL tiers', async () => {
    const bes = new BES({ defaultPrivacyTier: 'MEADOW' });
    const embedding = new Array(512).fill(1);
    const grain = await bes.createGrain(embedding, 'test-user');

    expect(grain.dpMetadata).toBeDefined();
    expect(grain.dpMetadata?.epsilon).toBe(1.0);
  });

  test('should not apply DP for LOCAL tier', async () => {
    const bes = new BES({ defaultPrivacyTier: 'LOCAL' });
    const embedding = new Array(1024).fill(1);
    const grain = await bes.createGrain(embedding, 'test-user');

    expect(grain.dpMetadata).toBeUndefined();
  });
});
```

### KVAnchor Tests

```typescript
describe('KVAnchorPool', () => {
  test('should create anchor from segment', async () => {
    const pool = new KVAnchorPool();
    const segment = createTestSegment();
    const embedding = new Array(128).fill(0).map(() => Math.random());

    const anchor = await pool.createAnchor(segment, embedding);

    expect(anchor.anchorId).toBeDefined();
    expect(anchor.qualityScore).toBeGreaterThan(0);
    expect(anchor.compressionRatio).toBeGreaterThan(1);
  });

  test('should find similar anchors', async () => {
    const pool = new KVAnchorPool();

    // Add anchors
    for (let i = 0; i < 10; i++) {
      const segment = createTestSegment();
      const embedding = createTestEmbedding(128);
      await pool.createAnchor(segment, embedding);
    }

    // Search
    const query = createTestEmbedding(128);
    const results = pool.findSimilarAnchors(query, 0, 0.0);

    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(5); // maxMatches
  });

  test('should evict anchors using LRU', async () => {
    const pool = new KVAnchorPool({ maxAnchors: 5, enableLRU: true });

    // Add 10 anchors
    for (let i = 0; i < 10; i++) {
      const segment = createTestSegment();
      const embedding = createTestEmbedding(128);
      await pool.createAnchor(segment, embedding);
    }

    const stats = pool.getStats();
    expect(stats.totalAnchors).toBe(5);
  });
});
```

### ANN Index Tests

```typescript
describe('ANNIndex', () => {
  test('should return approximate nearest neighbors', () => {
    const index = new ANNIndex({ algorithm: 'hnsw', dimension: 128 });
    const embeddings = generateRandomEmbeddings(1000, 128);
    index.build(embeddings);

    const query = generateRandomEmbeddings(1, 128)[0];
    const results = index.search(query, 10);

    expect(results.length).toBe(10);
  });

  test('should have high recall', () => {
    const embeddings = generateRandomEmbeddings(1000, 128);
    const queries = generateRandomEmbeddings(100, 128);

    const benchmark = benchmarkANNIndex(embeddings, queries, 10);

    expect(benchmark.recall).toBeGreaterThan(0.9); // 90% recall
    expect(benchmark.speedup).toBeGreaterThan(5); // 5x speedup
  });

  test('should handle empty index', () => {
    const index = new ANNIndex({ dimension: 128 });

    expect(() => index.search(new Array(128).fill(0), 10))
      .toThrow('Index not built');
  });
});
```

### Edge Case Tests

```typescript
describe('Edge Cases', () => {
  test('should handle zero-norm embedding', () => {
    const embedding = new Array(128).fill(0);
    const normalized = normalizeEmbedding(embedding);

    const norm = Math.sqrt(normalized.reduce((s, v) => s + v * v, 0));
    expect(norm).toBeCloseTo(1.0, 5);
  });

  test('should handle dimension mismatch', async () => {
    const pool = new KVAnchorPool({ embeddingDim: 128 });
    const segment = createTestSegment();
    const wrongDimEmbedding = new Array(256).fill(0).map(() => Math.random());

    // Should either error or auto-adjust
    const anchor = await pool.createAnchor(segment, wrongDimEmbedding);
    expect(anchor.embedding.length).toBe(128);
  });

  test('should handle concurrent access', async () => {
    const pool = new ConcurrentKVAnchorPool();

    const promises = Array(100).fill(0).map(async (_, i) => {
      if (i % 2 === 0) {
        return pool.read(() => pool.getStats());
      } else {
        return pool.write(async () => {
          const segment = createTestSegment();
          const embedding = createTestEmbedding(128);
          await pool.createAnchor(segment, embedding);
        });
      }
    });

    await Promise.all(promises);
    // Should complete without deadlock or race conditions
  });
});
```

### Integration Tests

```typescript
describe('Integration', () => {
  test('full pipeline: segment to anchor to match', async () => {
    const pool = new KVAnchorPool();

    // Create segment
    const segment = createTestSegment();
    const embedding = createTestEmbedding(128);

    // Create anchor
    const anchor = await pool.createAnchor(segment, embedding);

    // Search for similar
    const matches = pool.findSimilarAnchors(embedding, 0, 0.9);

    expect(matches.length).toBeGreaterThan(0);
    expect(matches[0].anchor.anchorId).toBe(anchor.anchorId);
  });

  test('LMCache integration', async () => {
    const adapter = createLMCacheAdapter({
      backend: 'cpu',
      enableLocalCache: true,
    });

    const isAvailable = await adapter.isAvailable();
    expect(typeof isAvailable).toBe('boolean');

    const anchor = createTestAnchor();
    await adapter.store(anchor);

    const retrieved = await adapter.lookup(anchor.embedding);
    expect(retrieved).not.toBeNull();
  });
});
```

---

## Appendix: Common Patterns Reference

### Creating Test Data

```typescript
function createTestSegment(): KVCacheSegment {
  return {
    layerId: 0,
    segmentId: `seg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    tokens: Array(10).fill(0).map(() => Math.floor(Math.random() * 1000)),
    keyCache: Array(10).fill(0).map(() =>
      Array(64).fill(0).map(() => Math.random() * 2 - 1)
    ),
    valueCache: Array(10).fill(0).map(() =>
      Array(64).fill(0).map(() => Math.random() * 2 - 1)
    ),
    metadata: {
      createdAt: Date.now(),
      modelHash: 'test-model',
      agentId: 'test-agent',
      turnNumber: 1,
      position: 0,
      length: 10,
    },
  };
}

function createTestEmbedding(dim: number): number[] {
  const embedding = new Array(dim).fill(0).map(() => Math.random() * 2 - 1);
  const norm = Math.sqrt(embedding.reduce((s, v) => s + v * v, 0));
  return embedding.map(v => v / norm);
}

function createTestAnchor(): KVAnchor {
  return {
    anchorId: `anchor-${Date.now()}`,
    layerId: 0,
    segmentId: 'test-segment',
    compressedKeys: new Float32Array(64).map(() => Math.random()),
    compressedValues: new Float32Array(64).map(() => Math.random()),
    embedding: createTestEmbedding(128),
    sourceSegmentId: 'test-segment',
    sourceAgentId: 'test-agent',
    usageCount: 0,
    lastUsed: Date.now(),
    qualityScore: 0.9,
    compressionRatio: 10,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
}
```

---

*Document generated for glm-4.7 implementation agents*
*Repository: https://github.com/SuperInstance/polln*
