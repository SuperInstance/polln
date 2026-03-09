# Integration Guide: Memory Optimization for POLLN

This guide explains how to integrate the optimized memory configuration into your POLLN implementation.

## Table of Contents

1. [Quick Integration](#quick-integration)
2. [Configuration Usage](#configuration-usage)
3. [Component Integration](#component-integration)
4. [Testing](#testing)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Quick Integration

### Step 1: Generate Configuration

Run the memory optimizations:

```bash
cd /path/to/polln
python simulations/optimization/memory/run_all.py
```

This creates:
- `src/core/kv/config.ts` - TypeScript configuration
- `simulations/optimization/memory/results/*.json` - Raw results

### Step 2: Import Configuration

In your KV-cache implementation:

```typescript
// src/core/kvanchor.ts
import { KV_CACHE_CONFIG } from './kv/config';

export class KVAnchorPool {
  private config = KV_CACHE_CONFIG;

  constructor() {
    console.log('KV-Cache config:', this.config);
  }
}
```

### Step 3: Use Configuration

Apply the optimized parameters:

```typescript
// Compression
compressKVCache(data: KVCache, type: CacheType): CompressedCache {
  const config = this.config.compression[type];

  return {
    method: config.method,
    ratio: config.ratio,
    data: this.compress(data, config.method, config.ratio)
  };
}

// Eviction
evict(): void {
  const policy = this.config.eviction.policy;
  const maxSize = this.config.eviction.maxSize;

  if (policy === 'adaptive_arc') {
    this.evictARC(maxSize);
  }
  // ... other policies
}

// ANN Index
buildIndex(): void {
  const annConfig = this.config.annIndex;

  this.index = new HNSWIndex({
    M: annConfig.params.M,
    efConstruction: annConfig.params.efConstruction
  });
}
```

## Configuration Usage

### Compression Configuration

```typescript
// Access compression settings
const attentionConfig = KV_CACHE_CONFIG.compression.attention;

// Config structure:
interface CompressionConfig {
  method: 'svd' | 'quantization' | 'product_quantization' | 'sparsification';
  ratio: number;        // Target compression ratio (0.0-1.0)
  quality: number;      // Expected quality (cosine similarity)
  params?: Record<string, any>;
}

// Example usage:
function compressKVCache(
  data: Float32Array,
  type: 'attention' | 'mlp' | 'embedding' | 'ffn'
): CompressedKVCache {
  const config = KV_CACHE_CONFIG.compression[type];

  switch (config.method) {
    case 'svd':
      return compressSVD(data, config.ratio, config.params.retainedVariance);

    case 'quantization':
      return compressQuantize(data, config.params.quantizationBits);

    case 'product_quantization':
      return compressPQ(data, config.params.n_subvectors);

    // ...
  }
}
```

### Eviction Configuration

```typescript
// Access eviction settings
const evictionConfig = KV_CACHE_CONFIG.eviction;

// Config structure:
interface EvictionConfig {
  policy: 'lru' | 'lfu' | 'fifo' | 'random' | 'adaptive_arc' | 'clock';
  maxSize: number;        // Maximum cache size in bytes
  expectedHitRate: number; // Expected hit rate (0.0-1.0)
}

// Example usage:
class KVAnchorPool {
  private cache: Map<string, KVAnchor> = new Map();
  private currentSize: number = 0;

  evictIfNeeded(requiredSpace: number): void {
    const config = KV_CACHE_CONFIG.eviction;

    while (this.currentSize + requiredSpace > config.maxSize) {
      this.evictOne(config.policy);
    }
  }

  private evictOne(policy: string): void {
    switch (policy) {
      case 'lru':
        this.evictLRU();
        break;
      case 'adaptive_arc':
        this.evictARC();
        break;
      // ...
    }
  }
}
```

### ANN Index Configuration

```typescript
// Access ANN index settings
const annConfig = KV_CACHE_CONFIG.annIndex;

// Config structure:
interface ANNIndexConfig {
  algorithm: 'hnsw' | 'lsh' | 'ball_tree' | 'ivf';
  params: Record<string, any>;  // Algorithm-specific parameters
  expectedRecall: number;        // Expected recall (0.0-1.0)
  expectedQueryTimeMs: number;   // Expected query time in ms
}

// Example usage:
class AnchorMatcher {
  private index: ANNIndex;

  buildIndex(anchors: Float32Array[]): void {
    const config = KV_CACHE_CONFIG.annIndex;

    switch (config.algorithm) {
      case 'hnsw':
        this.index = new HNSWIndex({
          M: config.params.M,
          efConstruction: config.params.efConstruction,
          efSearch: config.params.efSearch
        });
        break;

      case 'lsh':
        this.index = new LSHIndex({
          nBands: config.params.nBands,
          nRows: config.params.nRows
        });
        break;
      // ...
    }

    this.index.build(anchors);
  }
}
```

### Sizing Configuration

```typescript
// Access sizing recommendations
const sizingConfig = KV_CACHE_CONFIG.sizing;

// Config structure:
interface SizingConfig {
  conversation: { sizeMb: number; sizeBytes: number; expectedHitRate: number };
  coding: { sizeMb: number; sizeBytes: number; expectedHitRate: number };
  analysis: { sizeMb: number; sizeBytes: number; expectedHitRate: number };
  general: { sizeMb: number; sizeBytes: number; expectedHitRate: number };
}

// Example usage:
function getCacheSizeForWorkload(workload: string): number {
  const config = KV_CACHE_CONFIG.sizing[workload] || KV_CACHE_CONFIG.sizing.general;

  return config.sizeBytes;
}

// Usage:
class Colony {
  initialize(workload: 'conversation' | 'coding' | 'analysis' | 'general'): void {
    const cacheSize = getCacheSizeForWorkload(workload);
    this.kvCache = new KVAnchorPool(cacheSize);
  }
}
```

### Prefetch Configuration

```typescript
// Access prefetch settings
const prefetchConfig = KV_CACHE_CONFIG.prefetch;

// Config structure:
interface PrefetchConfig {
  enabled: boolean;
  strategy: 'none' | 'always' | 'probability' | 'markov' | 'ml_predictive';
  params: Record<string, any>;
  expectedEfficiency: number;      // Prefetch efficiency (0.0-1.0)
  expectedLatencyReduction: number; // Latency reduction (0.0-1.0)
}

// Example usage:
class KVAnchorPool {
  private prefetcher: Prefetcher;

  constructor() {
    const config = KV_CACHE_CONFIG.prefetch;

    if (config.enabled) {
      this.prefetcher = new Prefetcher(config.strategy, config.params);
    }
  }

  async access(key: string): Promise<KVAnchor | null> {
    const anchor = this.cache.get(key);

    if (anchor) {
      // Cache hit - trigger prefetch
      if (this.prefetcher) {
        this.prefetcher.trigger(key);
      }
      return anchor;
    }

    return null;
  }
}
```

## Component Integration

### Integrating with kvanchor.ts

```typescript
// src/core/kvanchor.ts

import { KV_CACHE_CONFIG } from './kv/config';

export class KVAnchorPool {
  private config = KV_CACHE_CONFIG;
  private cache: Map<string, CompressedKVAnchor> = new Map();
  private currentSize: number = 0;

  constructor(initialSize?: number) {
    // Use config size or override
    this.maxSize = initialSize || this.config.eviction.maxSize;
  }

  // Compression
  compress(anchor: KVAnchor, type: CacheType): CompressedKVAnchor {
    const config = this.config.compression[type];

    // Apply compression
    return {
      ...anchor,
      data: this.applyCompression(anchor.data, config.method, config.ratio),
      compressionMethod: config.method,
      compressionRatio: config.ratio
    };
  }

  // Decompression
  decompress(compressed: CompressedKVAnchor): KVAnchor {
    return {
      ...compressed,
      data: this.applyDecompression(compressed.data, compressed.compressionMethod)
    };
  }

  // Eviction
  private evictIfNeeded(requiredSpace: number): void {
    while (this.currentSize + requiredSpace > this.config.eviction.maxSize) {
      this.evictOne(this.config.eviction.policy);
    }
  }

  private evictOne(policy: string): void {
    const lruKey = this.findLRU();
    const entry = this.cache.get(lruKey);
    this.cache.delete(lruKey);
    this.currentSize -= entry.size;
  }

  // ... rest of implementation
}
```

### Integrating with ann-index.ts

```typescript
// src/core/ann-index.ts

import { KV_CACHE_CONFIG } from './kv/config';

export class ANNIndex {
  private config = KV_CACHE_CONFIG.annIndex;
  private index: any;

  constructor(customConfig?: Partial<typeof KV_CACHE_CONFIG.annIndex>) {
    // Merge with defaults
    const finalConfig = { ...this.config, ...customConfig };
    this.initialize(finalConfig);
  }

  private initialize(config: typeof KV_CACHE_CONFIG.annIndex): void {
    switch (config.algorithm) {
      case 'hnsw':
        this.index = new HNSWIndex(config.params);
        break;

      case 'lsh':
        this.index = new LSHIndex(config.params);
        break;

      case 'ball_tree':
        this.index = new BallTreeIndex(config.params);
        break;

      case 'ivf':
        this.index = new IVFIndex(config.params);
        break;

      default:
        throw new Error(`Unknown ANN algorithm: ${config.algorithm}`);
    }
  }

  build(anchors: Float32Array[]): void {
    this.index.build(anchors);
  }

  search(query: Float32Array, k: number): number[] {
    return this.index.search(query, k);
  }
}
```

### Integrating with kvtile.ts

```typescript
// src/core/kvtile.ts

import { KV_CACHE_CONFIG } from './kv/config';

export class KTVTile extends BaseTile {
  private config = KV_CACHE_CONFIG;

  async process(input: A2APackage): Promise<A2APackage> {
    // Get compression config
    const compressionConfig = this.config.compression.attention;

    // Compress KV cache
    const compressed = this.compressKVCache(input.kvCache, compressionConfig);

    // Create output package
    return {
      ...input,
      kvCache: compressed,
      metadata: {
        ...input.metadata,
        compression: {
          method: compressionConfig.method,
          ratio: compressionConfig.ratio
        }
      }
    };
  }
}
```

## Testing

### Unit Tests

```typescript
// src/core/__tests__/kv-config.test.ts

import { KV_CACHE_CONFIG } from '../kv/config';

describe('KV_CACHE_CONFIG', () => {
  test('should have compression config for all types', () => {
    expect(KV_CACHE_CONFIG.compression).toHaveProperty('attention');
    expect(KV_CACHE_CONFIG.compression).toHaveProperty('mlp');
    expect(KV_CACHE_CONFIG.compression).toHaveProperty('embedding');
    expect(KV_CACHE_CONFIG.compression).toHaveProperty('ffn');
  });

  test('should have valid eviction config', () => {
    expect(KV_CACHE_CONFIG.eviction.policy).toBeTruthy();
    expect(KV_CACHE_CONFIG.eviction.maxSize).toBeGreaterThan(0);
    expect(KV_CACHE_CONFIG.eviction.expectedHitRate).toBeGreaterThan(0);
  });

  test('should have valid ANN config', () => {
    expect(KV_CACHE_CONFIG.annIndex.algorithm).toBeTruthy();
    expect(KV_CACHE_CONFIG.annIndex.params).toBeDefined();
    expect(KV_CACHE_CONFIG.annIndex.expectedRecall).toBeGreaterThan(0);
  });
});
```

### Integration Tests

```typescript
// src/core/__tests__/kv-config-integration.test.ts

import { KVAnchorPool } from '../kvanchor';
import { ANNIndex } from '../ann-index';
import { KV_CACHE_CONFIG } from '../kv/config';

describe('KV Cache Config Integration', () => {
  test('should use config in KVAnchorPool', () => {
    const pool = new KVAnchorPool();

    expect(pool.maxSize).toBe(KV_CACHE_CONFIG.eviction.maxSize);
  });

  test('should use config in ANNIndex', () => {
    const index = new ANNIndex();

    expect(index.algorithm).toBe(KV_CACHE_CONFIG.annIndex.algorithm);
  });

  test('should compress according to config', () => {
    const pool = new KVAnchorPool();
    const anchor = createMockAnchor();

    const compressed = pool.compress(anchor, 'attention');

    expect(compressed.compressionMethod).toBe(
      KV_CACHE_CONFIG.compression.attention.method
    );
  });
});
```

## Monitoring

### Metrics Collection

```typescript
// src/core/kv/metrics.ts

export class KVCacheMetrics {
  private config = KV_CACHE_CONFIG;
  private metrics = {
    hits: 0,
    misses: 0,
    evictions: 0,
    compressionTime: 0,
    decompressionTime: 0,
    queryTime: 0
  };

  recordHit(): void {
    this.metrics.hits++;
  }

  recordMiss(): void {
    this.metrics.misses++;
  }

  getHitRate(): number {
    const total = this.metrics.hits + this.metrics.misses;
    return this.metrics.hits / total;
  }

  compareWithExpected(): void {
    const actualHitRate = this.getHitRate();
    const expectedHitRate = this.config.eviction.expectedHitRate;

    if (actualHitRate < expectedHitRate * 0.9) {
      console.warn(
        `Hit rate (${actualHitRate}) below expected (${expectedHitRate})`
      );
    }
  }
}
```

### Health Checks

```typescript
// src/api/health.ts

export async function checkKVCacheHealth(): Promise<HealthStatus> {
  const config = KV_CACHE_CONFIG;

  const metrics = await collectMetrics();

  return {
    status: 'healthy',
    metrics: {
      hitRate: {
        actual: metrics.hitRate,
        expected: config.eviction.expectedHitRate,
        status: metrics.hitRate >= config.eviction.expectedHitRate * 0.9
          ? 'ok'
          : 'degraded'
      },
      compression: {
        actualRatio: metrics.compressionRatio,
        expectedRatio: config.compression.attention.ratio,
        status: 'ok'
      },
      ann: {
        actualRecall: metrics.annRecall,
        expectedRecall: config.annIndex.expectedRecall,
        status: metrics.annRecall >= config.annIndex.expectedRecall * 0.95
          ? 'ok'
          : 'degraded'
      }
    }
  };
}
```

## Troubleshooting

### Issue: Low Hit Rate

**Symptoms**: Actual hit rate < expected hit rate

**Solutions**:

1. Check if workload matches configuration:
```typescript
const workload = detectWorkload();
const expectedSize = KV_CACHE_CONFIG.sizing[workload].sizeBytes;

if (currentCacheSize < expectedSize) {
  console.warn('Cache size below recommendation for workload:', workload);
}
```

2. Try different eviction policy:
```typescript
const alternatives = ['lru', 'lfu', 'adaptive_arc', 'clock'];
for (const policy of alternatives) {
  // Test and compare hit rates
}
```

3. Increase cache size:
```typescript
const newSize = currentCacheSize * 1.5;
```

### Issue: Poor Compression Quality

**Symptoms**: High reconstruction error

**Solutions**:

1. Check compression method:
```typescript
const config = KV_CACHE_CONFIG.compression.attention;
if (config.quality < 0.9) {
  console.warn('Low quality expected:', config.quality);
}
```

2. Adjust compression ratio:
```typescript
const newRatio = config.ratio * 0.8; // Less compression, better quality
```

3. Try different method:
```typescript
const methods = ['svd', 'quantization', 'product_quantization'];
// Test and compare
```

### Issue: Slow ANN Queries

**Symptoms**: Query time > expected

**Solutions**:

1. Check ANN parameters:
```typescript
const config = KV_CACHE_CONFIG.annIndex;

if (config.algorithm === 'hnsw') {
  // Reduce efSearch for faster queries
  config.params.efSearch = Math.max(20, config.params.efSearch * 0.8);
}
```

2. Consider different algorithm:
```typescript
// LSH is faster but less accurate
if (queryTime > threshold) {
  switch to 'lsh';
}
```

3. Reduce index size:
```typescript
// Rebuild with smaller M
config.params.M = Math.max(8, config.params.M - 4);
```

### Issue: High Memory Usage

**Symptoms**: Memory exceeds cache size

**Solutions**:

1. Check compression:
```typescript
const config = KV_CACHE_CONFIG.compression;

// Increase compression
for (const type in config) {
  config[type].ratio *= 0.8;
}
```

2. Trigger more aggressive eviction:
```typescript
const targetFree = currentSize * 0.2; // Free up 20%
while (currentSize > maxSize - targetFree) {
  evictOne();
}
```

3. Use larger cache:
```typescript
const newSize = KV_CACHE_CONFIG.sizing.general.sizeBytes * 1.5;
```

## Best Practices

1. **Monitor Continuously**: Track all metrics and compare with expected values
2. **Adjust Gradually**: Change one parameter at a time
3. **Validate Changes**: Run tests before deploying to production
4. **Version Config**: Tag config versions with deployments
5. **Document Deviations**: Note any custom changes to defaults
6. **Re-run Optimizations**: Periodically re-run simulations with new data
7. **A/B Test**: Test new configurations before full rollout

## Support

For issues or questions:
1. Check simulation results in `simulations/optimization/memory/results/`
2. Review `CACHE_GUIDE.md` for detailed explanations
3. Run `test_memory.py` to validate configuration
4. Open an issue on GitHub

Generated: 2026-03-07
Source: `simulations/optimization/memory/`
