# Performance Optimization Schema

**Version**: 1.0.0
**Created**: 2026-03-08
**Target Implementation Agent**: glm-4.7

This document defines the schemas, interfaces, and invariants for high-performance implementations in the POLLN system.

---

## Table of Contents

1. [Cache Interface Schemas](#1-cache-interface-schemas)
2. [Benchmark Specifications](#2-benchmark-specifications)
3. [Metric Collection Schemas](#3-metric-collection-schemas)
4. [Optimization Pattern Schemas](#4-optimization-pattern-schemas)
5. [Performance Invariants](#5-performance-invariants)
6. [Configuration Schemas](#6-configuration-schemas)

---

## 1. Cache Interface Schemas

### 1.1 Core Cache Interface

```typescript
/**
 * Base cache entry schema
 */
interface CacheEntry<T> {
  /** Unique identifier for the cache entry */
  id: string;

  /** The cached value */
  value: T;

  /** Timestamp when entry was created (ms since epoch) */
  createdAt: number;

  /** Timestamp when entry was last accessed */
  lastAccessedAt: number;

  /** Time-to-live in milliseconds (0 = no expiry) */
  ttl: number;

  /** Size in bytes (for memory management) */
  size: number;

  /** Access frequency counter */
  accessCount: number;

  /** Quality score (0-1) for priority-based eviction */
  qualityScore: number;

  /** Optional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Cache storage interface
 */
interface ICacheStorage<K, V> {
  /** Get entry by key */
  get(key: K): Promise<CacheEntry<V> | undefined>;

  /** Set entry with optional TTL */
  set(key: K, value: V, ttl?: number): Promise<void>;

  /** Delete entry by key */
  delete(key: K): Promise<boolean>;

  /** Check if key exists */
  has(key: K): Promise<boolean>;

  /** Clear all entries */
  clear(): Promise<void>;

  /** Get current size (number of entries) */
  size(): Promise<number>;

  /** Get memory usage in bytes */
  memoryUsage(): Promise<number>;
}
```

### 1.2 TTL (Time-To-Live) Schema

```typescript
/**
 * TTL configuration schema
 */
interface TTLConfig {
  /** Default TTL in milliseconds */
  defaultTTL: number;

  /** Maximum TTL allowed */
  maxTTL: number;

  /** Whether to refresh TTL on access */
  refreshOnAccess: boolean;

  /** Refresh factor (multiplies remaining TTL) */
  refreshFactor: number;

  /** Minimum remaining TTL to trigger refresh */
  minRemainingForRefresh: number;

  /** TTL tiers by entry type */
  tiers: {
    hot: number;      // Frequently accessed (e.g., 3600000 = 1 hour)
    warm: number;     // Moderately accessed (e.g., 1800000 = 30 min)
    cold: number;     // Rarely accessed (e.g., 300000 = 5 min)
  };
}

/**
 * TTL policy enum
 */
type TTLPolicy =
  | 'fixed'           // Fixed TTL from creation
  | 'sliding'         // Resets on each access
  | 'adaptive'        // Adjusts based on access patterns
  | 'hybrid';         // Combination of fixed + sliding

/**
 * TTL state for an entry
 */
interface TTLState {
  /** Absolute expiration timestamp */
  expiresAt: number;

  /** Remaining time in ms */
  remaining: number;

  /** Whether entry is expired */
  isExpired: boolean;

  /** Policy in use */
  policy: TTLPolicy;
}
```

### 1.3 Eviction Policy Schema

```typescript
/**
 * Eviction policy types
 */
type EvictionPolicy =
  | 'lru'             // Least Recently Used
  | 'lfu'             // Least Frequently Used
  | 'fifo'            // First In First Out
  | 'ttl'             // Time-based expiration
  | 'quality-aware'   // Based on quality score
  | 'hybrid';         // Combination of policies

/**
 * Eviction configuration
 */
interface EvictionConfig {
  /** Eviction policy to use */
  policy: EvictionPolicy;

  /** Maximum number of entries */
  maxEntries: number;

  /** Maximum memory in bytes */
  maxMemoryBytes: number;

  /** Eviction batch size (entries removed per cycle) */
  evictionBatchSize: number;

  /** Threshold to trigger eviction (0-1 of max capacity) */
  evictionThreshold: number;

  /** Weight for LRU component in hybrid policy */
  lruWeight: number;

  /** Weight for LFU component in hybrid policy */
  lfuWeight: number;

  /** Weight for quality score in hybrid policy */
  qualityWeight: number;

  /** Minimum quality score to avoid eviction */
  minQualityThreshold: number;
}

/**
 * Eviction event schema
 */
interface EvictionEvent {
  /** Timestamp of eviction */
  timestamp: number;

  /** ID of evicted entry */
  entryId: string;

  /** Reason for eviction */
  reason: 'capacity' | 'ttl' | 'memory' | 'quality' | 'manual';

  /** Entry size in bytes */
  size: number;

  /** Entry age in ms */
  age: number;

  /** Access count at eviction */
  accessCount: number;

  /** Quality score at eviction */
  qualityScore: number;
}
```

### 1.4 Invalidation Schema

```typescript
/**
 * Invalidation trigger types
 */
type InvalidationTrigger =
  | 'explicit'        // Manual invalidation
  | 'dependency'      // Related entry changed
  | 'pattern'         // Pattern-based invalidation
  | 'version'         // Version mismatch
  | 'source-change';  // Source data changed

/**
 * Invalidation rule schema
 */
interface InvalidationRule {
  /** Rule identifier */
  id: string;

  /** Pattern to match keys */
  keyPattern: string | RegExp;

  /** Dependencies (other keys that trigger invalidation) */
  dependencies: string[];

  /** Version constraint */
  versionConstraint?: string;

  /** Time-based invalidation schedule (cron format) */
  schedule?: string;

  /** Whether to cascade invalidation to dependents */
  cascade: boolean;

  /** Maximum cascade depth */
  maxCascadeDepth: number;
}

/**
 * Invalidation event schema
 */
interface InvalidationEvent {
  /** Timestamp of invalidation */
  timestamp: number;

  /** Keys invalidated */
  keys: string[];

  /** Trigger type */
  trigger: InvalidationTrigger;

  /** Source of invalidation (what caused it) */
  source: string;

  /** Cascaded invalidations */
  cascaded: string[];

  /** Duration of invalidation operation in ms */
  duration: number;
}

/**
 * Cache dependency graph schema
 */
interface DependencyGraph {
  /** Map of key to its dependencies */
  dependencies: Map<string, Set<string>>;

  /** Map of key to its dependents (reverse) */
  dependents: Map<string, Set<string>>;

  /** Version map for dependency tracking */
  versions: Map<string, number>;
}
```

### 1.5 KV-Cache Specific Schema

```typescript
/**
 * KV-Cache anchor schema (extends base cache)
 */
interface KVAnchorEntry extends CacheEntry<{
  /** Layer ID in transformer */
  layerId: number;

  /** Compressed key cache */
  compressedKeys: Float32Array;

  /** Compressed value cache */
  compressedValues: Float32Array;

  /** Embedding for similarity matching */
  embedding: number[];

  /** Compression ratio achieved */
  compressionRatio: number;

  /** Offset prediction metadata */
  offsetMetadata?: OffsetMetadata;
}> {
  /** Cross-colony reuse count */
  crossColonyReuseCount: number;

  /** Token span this anchor covers */
  tokenSpan: { start: number; end: number };
}

/**
 * Offset prediction for cache reuse
 */
interface OffsetMetadata {
  /** Predicted offset for next token */
  predictedOffset: number;

  /** Confidence of prediction */
  confidence: number;

  /** Historical accuracy */
  accuracy: number;

  /** Number of predictions made */
  predictionCount: number;
}

/**
 * Anchor match result
 */
interface AnchorMatchResult {
  /** Matched anchor */
  anchor: KVAnchorEntry;

  /** Similarity score (0-1) */
  similarity: number;

  /** Match confidence */
  confidence: number;

  /** Predicted offset if applicable */
  predictedOffset?: number;

  /** Time to find match in ms */
  lookupTime: number;
}
```

---

## 2. Benchmark Specifications

### 2.1 Benchmark Configuration Schema

```typescript
/**
 * Benchmark configuration schema
 */
interface BenchmarkSpec {
  /** Unique benchmark identifier */
  id: string;

  /** Benchmark name */
  name: string;

  /** Description of what is being benchmarked */
  description: string;

  /** Benchmark version */
  version: string;

  /** Execution configuration */
  execution: BenchmarkExecutionConfig;

  /** Target thresholds */
  targets: BenchmarkTargets;

  /** Metrics to collect */
  metrics: MetricSpec[];

  /** Warmup configuration */
  warmup: WarmupConfig;

  /** Output configuration */
  output: OutputConfig;
}

/**
 * Benchmark execution configuration
 */
interface BenchmarkExecutionConfig {
  /** Number of iterations */
  iterations: number;

  /** Concurrency level */
  concurrency: number;

  /** Timeout per iteration in ms */
  iterationTimeout: number;

  /** Total benchmark timeout in ms */
  totalTimeout: number;

  /** Random seed for reproducibility */
  seed: number;

  /** Whether to fail fast on error */
  failFast: boolean;

  /** Environment variables */
  env: Record<string, string>;
}

/**
 * Benchmark target thresholds (KVCOMM-inspired)
 */
interface BenchmarkTargets {
  /** Target cache hit rate (0-1) */
  cacheHitRate: number; // Default: 0.70 (70%)

  /** Target TTFT speedup multiplier */
  ttftSpeedup: number; // Default: 7.8x

  /** Target memory reduction (0-1) */
  memoryReduction: number; // Default: 0.50 (50%)

  /** Maximum latency in ms (p99) */
  maxLatencyP99: number;

  /** Minimum throughput (ops/sec) */
  minThroughput: number;

  /** Maximum memory usage in bytes */
  maxMemoryUsage: number;
}

/**
 * Warmup configuration
 */
interface WarmupConfig {
  /** Number of warmup iterations */
  iterations: number;

  /** Warmup duration in ms */
  duration: number;

  /** Whether to discard warmup results */
  discardResults: boolean;
}
```

### 2.2 Workload Schema

```typescript
/**
 * Workload specification for benchmarks
 */
interface WorkloadSpec {
  /** Workload identifier */
  id: string;

  /** Workload type */
  type: WorkloadType;

  /** Number of agents to simulate */
  numAgents: number;

  /** Number of requests to generate */
  numRequests: number;

  /** Sequence length for cache operations */
  sequenceLength: number;

  /** Embedding dimension */
  embeddingDim: number;

  /** Prefix overlap ratio (0-1) */
  prefixOverlap: number;

  /** Entropy/randomness level (0-1) */
  entropy: number;

  /** Burstiness factor (0-1) */
  burstiness: number;

  /** Request distribution */
  distribution: 'uniform' | 'poisson' | 'burst' | 'custom';
}

/**
 * Workload types
 */
type WorkloadType =
  | 'single-agent-baseline'
  | 'shared-prefix'
  | 'pipeline-coordination'
  | 'consensus-formation'
  | 'federated-learning'
  | 'dreaming-optimization'
  | 'multi-turn-conversation';

/**
 * Agent request schema
 */
interface AgentRequestSpec {
  /** Request ID */
  requestId: string;

  /** Agent ID making request */
  agentId: string;

  /** Prompt or input */
  prompt: string;

  /** Embedding vector */
  embedding: number[];

  /** Layer ID */
  layerId: number;

  /** Request timestamp */
  timestamp: number;

  /** Context strings */
  context?: string[];

  /** Priority (higher = more important) */
  priority?: number;
}
```

### 2.3 Benchmark Result Schema

```typescript
/**
 * Benchmark result schema
 */
interface BenchmarkResult {
  /** Result ID */
  id: string;

  /** Benchmark specification used */
  benchmarkSpec: BenchmarkSpec;

  /** Timestamp of execution */
  timestamp: number;

  /** Duration in ms */
  duration: number;

  /** Status */
  status: 'passed' | 'failed' | 'error' | 'timeout';

  /** Collected metrics */
  metrics: BenchmarkMetrics;

  /** Raw data samples */
  rawData: RawBenchmarkData;

  /** Comparison against targets */
  comparison: TargetComparison;

  /** Environment info */
  environment: EnvironmentInfo;

  /** Error details if failed */
  error?: BenchmarkError;
}

/**
 * Collected benchmark metrics
 */
interface BenchmarkMetrics {
  // Cache metrics
  cacheHitRate: number;
  cacheMissRate: number;
  avgAccessTime: number;
  p95AccessTime: number;
  p99AccessTime: number;

  // TTFT metrics
  baselineTTFT: number;
  cachedTTFT: number;
  ttftSpeedup: number;
  ttftImprovement: number;

  // Memory metrics
  baselineMemory: number;
  cachedMemory: number;
  memoryReduction: number;
  memorySavings: number;

  // Throughput metrics
  baselineThroughput: number;
  cachedThroughput: number;
  throughputSpeedup: number;

  // Quality metrics
  avgAnchorQuality: number;
  avgCompressionRatio: number;
  avgSimilarity: number;

  // Timing
  totalBenchmarkTime: number;
  avgIterationTime: number;
}

/**
 * Raw benchmark data
 */
interface RawBenchmarkData {
  /** TTFT samples (ms) */
  ttftSamples: number[];

  /** Memory samples (bytes) */
  memorySamples: number[];

  /** Cache access times (ms) */
  cacheAccessTimes: number[];

  /** Total cache hits */
  cacheHits: number;

  /** Total cache misses */
  cacheMisses: number;

  /** Anchor usage counts */
  anchorUsage: Map<string, number>;

  /** Similarity scores */
  similarityScores: number[];
}
```

---

## 3. Metric Collection Schemas

### 3.1 Metric Definition Schema

```typescript
/**
 * Metric specification
 */
interface MetricSpec {
  /** Metric name */
  name: string;

  /** Metric description */
  description: string;

  /** Metric type */
  type: MetricType;

  /** Unit of measurement */
  unit: string;

  /** Aggregation method */
  aggregation: AggregationMethod;

  /** Whether higher is better */
  higherIsBetter: boolean;

  /** Tags for categorization */
  tags: string[];

  /** Collection interval in ms (0 = per-operation) */
  collectionInterval: number;
}

/**
 * Metric types
 */
type MetricType =
  | 'counter'      // Monotonically increasing
  | 'gauge'        // Point-in-time value
  | 'histogram'    // Distribution of values
  | 'summary'      // Similar to histogram with quantiles
  | 'timer';       // Duration measurement

/**
 * Aggregation methods
 */
type AggregationMethod =
  | 'sum'
  | 'avg'
  | 'min'
  | 'max'
  | 'p50'
  | 'p95'
  | 'p99'
  | 'count'
  | 'rate';
```

### 3.2 Performance Metrics Schema

```typescript
/**
 * Performance metrics collection
 */
interface PerformanceMetrics {
  /** Cache performance metrics */
  cache: CacheMetrics;

  /** Latency metrics */
  latency: LatencyMetrics;

  /** Throughput metrics */
  throughput: ThroughputMetrics;

  /** Memory metrics */
  memory: MemoryMetrics;

  /** Resource utilization */
  resources: ResourceMetrics;

  /** Custom metrics */
  custom: Map<string, number>;
}

/**
 * Cache-specific metrics
 */
interface CacheMetrics {
  /** Total operations */
  totalOps: number;

  /** Hit count */
  hits: number;

  /** Miss count */
  misses: number;

  /** Hit rate (0-1) */
  hitRate: number;

  /** Eviction count */
  evictions: number;

  /** Average entry size in bytes */
  avgEntrySize: number;

  /** Current entry count */
  entryCount: number;

  /** Memory used in bytes */
  memoryUsed: number;

  /** Lookup latency distribution */
  lookupLatency: LatencyDistribution;
}

/**
 * Latency distribution
 */
interface LatencyDistribution {
  min: number;
  max: number;
  mean: number;
  median: number;
  p50: number;
  p90: number;
  p95: number;
  p99: number;
  stdDev: number;
  samples: number;
}

/**
 * Latency metrics
 */
interface LatencyMetrics {
  /** Time to first token */
  ttft: LatencyDistribution;

  /** End-to-end latency */
  e2e: LatencyDistribution;

  /** Processing latency */
  processing: LatencyDistribution;

  /** Network latency */
  network: LatencyDistribution;
}

/**
 * Throughput metrics
 */
interface ThroughputMetrics {
  /** Requests per second */
  requestsPerSecond: number;

  /** Tokens per second */
  tokensPerSecond: number;

  /** Operations per second */
  opsPerSecond: number;

  /** Bytes per second */
  bytesPerSecond: number;
}

/**
 * Memory metrics
 */
interface MemoryMetrics {
  /** Heap used (bytes) */
  heapUsed: number;

  /** Heap total (bytes) */
  heapTotal: number;

  /** External memory (bytes) */
  external: number;

  /** RSS (bytes) */
  rss: number;

  /** Array buffers (bytes) */
  arrayBuffers: number;

  /** Peak memory usage */
  peakUsage: number;

  /** Garbage collection count */
  gcCount: number;

  /** GC time total (ms) */
  gcTimeTotal: number;
}

/**
 * Resource utilization metrics
 */
interface ResourceMetrics {
  /** CPU usage (0-1) */
  cpuUsage: number;

  /** Memory usage (0-1) */
  memoryUsage: number;

  /** Event loop lag (ms) */
  eventLoopLag: number;

  /** Active handles */
  activeHandles: number;

  /** Active requests */
  activeRequests: number;
}
```

### 3.3 Metric Collection Configuration

```typescript
/**
 * Metric collection configuration
 */
interface MetricCollectionConfig {
  /** Enable metric collection */
  enabled: boolean;

  /** Collection interval in ms */
  interval: number;

  /** Metrics to collect */
  metrics: string[];

  /** Retention period in ms */
  retentionPeriod: number;

  /** Export configuration */
  export: MetricExportConfig;

  /** Sampling configuration */
  sampling: SamplingConfig;
}

/**
 * Metric export configuration
 */
interface MetricExportConfig {
  /** Export format */
  format: 'json' | 'prometheus' | 'statsd' | 'custom';

  /** Export endpoint */
  endpoint?: string;

  /** Export interval in ms */
  interval: number;

  /** Batch size for exports */
  batchSize: number;

  /** Custom exporter function */
  customExporter?: (metrics: PerformanceMetrics) => Promise<void>;
}

/**
 * Sampling configuration
 */
interface SamplingConfig {
  /** Sampling rate (0-1) */
  rate: number;

  /** Minimum samples before sampling kicks in */
  minSamples: number;

  /** Adaptive sampling enabled */
  adaptive: boolean;

  /** Target samples per interval */
  targetSamplesPerInterval: number;
}
```

---

## 4. Optimization Pattern Schemas

### 4.1 Lazy Loading Schema

```typescript
/**
 * Lazy loading configuration
 */
interface LazyLoadingConfig {
  /** Enable lazy loading */
  enabled: boolean;

  /** Loading strategy */
  strategy: LazyLoadingStrategy;

  /** Prefetch threshold (0-1 of access probability) */
  prefetchThreshold: number;

  /** Maximum concurrent loads */
  maxConcurrentLoads: number;

  /** Load timeout in ms */
  loadTimeout: number;

  /** Retry configuration */
  retry: RetryConfig;
}

/**
 * Lazy loading strategies
 */
type LazyLoadingStrategy =
  | 'on-demand'      // Load when first accessed
  | 'prefetch'       // Predict and prefetch
  | 'progressive'    // Load in stages
  | 'suspended';     // Load only when explicitly requested

/**
 * Lazy loadable entry
 */
interface LazyLoadableEntry<T> {
  /** Entry ID */
  id: string;

  /** Loading state */
  state: 'unloaded' | 'loading' | 'loaded' | 'error';

  /** Loader function */
  loader: () => Promise<T>;

  /** Loaded value (if state is 'loaded') */
  value?: T;

  /** Error (if state is 'error') */
  error?: Error;

  /** Load timestamp */
  loadedAt?: number;

  /** Access count while unloaded */
  pendingAccessCount: number;
}
```

### 4.2 Batching Schema

```typescript
/**
 * Batching configuration
 */
interface BatchingConfig {
  /** Enable batching */
  enabled: boolean;

  /** Maximum batch size */
  maxBatchSize: number;

  /** Maximum wait time in ms before processing batch */
  maxWaitTime: number;

  /** Minimum batch size to process */
  minBatchSize: number;

  /** Batch processing strategy */
  strategy: BatchingStrategy;
}

/**
 * Batching strategies
 */
type BatchingStrategy =
  | 'size-based'     // Process when batch reaches maxBatchSize
  | 'time-based'     // Process after maxWaitTime
  | 'adaptive'       // Adjust based on load
  | 'priority';      // Process high-priority items immediately

/**
 * Batch operation schema
 */
interface BatchOperation<K, V> {
  /** Batch ID */
  batchId: string;

  /** Operations in batch */
  operations: BatchOp<K, V>[];

  /** Creation timestamp */
  createdAt: number;

  /** Processing status */
  status: 'pending' | 'processing' | 'completed' | 'failed';

  /** Processing result */
  results?: Map<K, BatchResult<V>>;
}

/**
 * Single batch operation
 */
interface BatchOp<K, V> {
  key: K;
  operation: 'get' | 'set' | 'delete';
  value?: V;
  ttl?: number;
  priority: number;
}

/**
 * Batch result
 */
interface BatchResult<V> {
  success: boolean;
  value?: V;
  error?: Error;
}
```

### 4.3 Parallelization Schema

```typescript
/**
 * Parallelization configuration
 */
interface ParallelizationConfig {
  /** Enable parallel execution */
  enabled: boolean;

  /** Maximum parallel workers */
  maxWorkers: number;

  /** Task queue size */
  queueSize: number;

  /** Task timeout in ms */
  taskTimeout: number;

  /** Scheduling strategy */
  scheduler: SchedulingStrategy;
}

/**
 * Scheduling strategies
 */
type SchedulingStrategy =
  | 'fifo'           // First in, first out
  | 'priority'       // Higher priority first
  | 'round-robin'    // Fair distribution
  | 'work-stealing'; // Workers steal from each other

/**
 * Parallel task schema
 */
interface ParallelTask<T, R> {
  /** Task ID */
  taskId: string;

  /** Input data */
  input: T;

  /** Processing function */
  processor: (input: T) => Promise<R>;

  /** Priority (higher = more important) */
  priority: number;

  /** Created timestamp */
  createdAt: number;

  /** Status */
  status: 'queued' | 'running' | 'completed' | 'failed';

  /** Result */
  result?: R;

  /** Error */
  error?: Error;

  /** Worker ID assigned */
  workerId?: string;
}
```

---

## 5. Performance Invariants

### 5.1 Cache Invariants

```typescript
/**
 * Cache performance invariants
 *
 * These invariants MUST be maintained by any cache implementation.
 * Violation indicates a bug or performance regression.
 */
interface CacheInvariants {
  /**
   * INV-CACHE-001: Hit rate monotonicity
   * Under identical workload patterns, cache hit rate should not
   * decrease as the cache warms up.
   */
  hitRateMonotonicity: {
    description: string;
    check: (before: number, after: number) => boolean;
    // after >= before || after == 0 (empty cache)
  };

  /**
   * INV-CACHE-002: Lookup time bounds
   * Cache lookup should never exceed a maximum threshold.
   * Default: 10ms for local cache, 100ms for distributed.
   */
  lookupTimeBounds: {
    maxLocalMs: number;
    maxDistributedMs: number;
    check: (time: number, isLocal: boolean) => boolean;
  };

  /**
   * INV-CACHE-003: Memory bounds
   * Memory usage should never exceed configured maximum.
   */
  memoryBounds: {
    check: (used: number, max: number) => boolean;
    // used <= max * 1.05 (5% tolerance)
  };

  /**
   * INV-CACHE-004: Eviction correctness
   * Evicted entries should not be accessed after eviction.
   */
  evictionCorrectness: {
    check: (evictedIds: Set<string>, accessedId: string) => boolean;
    // !evictedIds.has(accessedId)
  };

  /**
   * INV-CACHE-005: TTL accuracy
   * Entries should not be accessible after TTL expiration.
   */
  ttlAccuracy: {
    toleranceMs: number; // Default: 100ms
    check: (expiresAt: number, now: number, accessible: boolean) => boolean;
    // if (now > expiresAt + toleranceMs) then !accessible
  };

  /**
   * INV-CACHE-006: Consistency
   * After set(key, value), get(key) should return the same value.
   */
  consistency: {
    check: <T>(written: T, read: T) => boolean;
    // deepEqual(written, read)
  };
}
```

### 5.2 Performance Invariants

```typescript
/**
 * System performance invariants
 */
interface PerformanceInvariants {
  /**
   * INV-PERF-001: Latency percentile ordering
   * P50 <= P90 <= P95 <= P99 must always hold.
   */
  latencyPercentileOrdering: {
    check: (p50: number, p90: number, p95: number, p99: number) => boolean;
    // p50 <= p90 && p90 <= p95 && p95 <= p99
  };

  /**
   * INV-PERF-002: Throughput stability
   * Throughput variance should not exceed threshold.
   */
  throughputStability: {
    maxVariance: number; // Default: 0.2 (20%)
    check: (samples: number[]) => boolean;
    // variance(samples) / mean(samples) <= maxVariance
  };

  /**
   * INV-PERF-003: Memory growth rate
   * Memory should not grow unboundedly over time.
   */
  memoryGrowthRate: {
    maxGrowthPerHour: number; // Default: 10MB
    check: (startMemory: number, endMemory: number, hoursElapsed: number) => boolean;
    // (endMemory - startMemory) / hoursElapsed <= maxGrowthPerHour
  };

  /**
   * INV-PERF-004: GC overhead
   * Time spent in GC should not exceed threshold.
   */
  gcOverhead: {
    maxGCRatio: number; // Default: 0.1 (10%)
    check: (gcTime: number, totalTime: number) => boolean;
    // gcTime / totalTime <= maxGCRatio
  };

  /**
   * INV-PERF-005: Event loop responsiveness
   * Event loop lag should stay below threshold.
   */
  eventLoopResponsiveness: {
    maxLagMs: number; // Default: 100ms
    check: (lag: number) => boolean;
    // lag <= maxLagMs
  };
}
```

### 5.3 KV-Cache Specific Invariants

```typescript
/**
 * KV-Cache specific invariants (KVCOMM-inspired)
 */
interface KVCacheInvariants {
  /**
   * INV-KV-001: Anchor similarity threshold
   * Matched anchors must meet minimum similarity threshold.
   */
  anchorSimilarityThreshold: {
    minSimilarity: number; // Default: 0.8
    check: (similarity: number) => boolean;
    // similarity >= minSimilarity
  };

  /**
   * INV-KV-002: Compression ratio bounds
   * Compressed anchor size should not exceed original.
   */
  compressionRatioBounds: {
    check: (originalSize: number, compressedSize: number) => boolean;
    // compressedSize <= originalSize
  };

  /**
   * INV-KV-003: Offset prediction accuracy
   * Offset predictions should improve with more data.
   */
  offsetPredictionAccuracy: {
    minSamples: number;
    minAccuracy: number; // Default: 0.7
    check: (samples: number, accuracy: number) => boolean;
    // samples < minSamples || accuracy >= minAccuracy
  };

  /**
   * INV-KV-004: Cross-colony reuse tracking
   * Reuse count should only increase.
   */
  crossColonyReuseMonotonicity: {
    check: (before: number, after: number) => boolean;
    // after >= before
  };

  /**
   * INV-KV-005: TTFT improvement
   * Cache-enabled TTFT should be faster than baseline.
   */
  ttftImprovement: {
    check: (baselineTTFT: number, cachedTTFT: number) => boolean;
    // cachedTTFT < baselineTTFT
  };
}
```

---

## 6. Configuration Schemas

### 6.1 Performance Configuration

```typescript
/**
 * Complete performance configuration
 */
interface PerformanceConfig {
  /** Cache configuration */
  cache: CacheConfig;

  /** Benchmark configuration */
  benchmark: BenchmarkConfig;

  /** Metrics configuration */
  metrics: MetricCollectionConfig;

  /** Optimization configuration */
  optimization: OptimizationConfig;
}

/**
 * Cache configuration
 */
interface CacheConfig {
  /** Storage backend */
  backend: 'memory' | 'redis' | 'distributed';

  /** TTL configuration */
  ttl: TTLConfig;

  /** Eviction configuration */
  eviction: EvictionConfig;

  /** Invalidation rules */
  invalidation: InvalidationRule[];

  /** KV-Cache specific config */
  kvCache: KVCacheConfig;
}

/**
 * KV-Cache configuration
 */
interface KVCacheConfig {
  /** Anchor pool configuration */
  anchorPool: {
    maxAnchors: number;
    similarityThreshold: number;
    embeddingDim: number;
  };

  /** ANN index configuration */
  annIndex: {
    algorithm: 'hnsw' | 'lsh' | 'ball-tree';
    efSearch: number;
    efConstruction: number;
  };

  /** Offset predictor configuration */
  offsetPredictor: {
    enabled: boolean;
    minSamples: number;
    confidenceThreshold: number;
  };
}

/**
 * Optimization configuration
 */
interface OptimizationConfig {
  /** Lazy loading */
  lazyLoading: LazyLoadingConfig;

  /** Batching */
  batching: BatchingConfig;

  /** Parallelization */
  parallelization: ParallelizationConfig;

  /** Prefetching */
  prefetching: {
    enabled: boolean;
    lookahead: number;
    maxPrefetchSize: number;
  };
}

/**
 * Benchmark configuration
 */
interface BenchmarkConfig {
  /** Default targets */
  targets: BenchmarkTargets;

  /** Workload configurations by type */
  workloads: Record<WorkloadType, WorkloadSpec>;

  /** Regression thresholds */
  regression: {
    maxHitRateRegression: number;
    maxTTFTRegression: number;
    maxMemoryRegression: number;
  };
}
```

### 6.2 Default Configuration Values

```typescript
/**
 * Default performance configuration
 */
const DEFAULT_PERFORMANCE_CONFIG: PerformanceConfig = {
  cache: {
    backend: 'memory',
    ttl: {
      defaultTTL: 3600000, // 1 hour
      maxTTL: 86400000,    // 24 hours
      refreshOnAccess: true,
      refreshFactor: 1.5,
      minRemainingForRefresh: 300000, // 5 minutes
      tiers: {
        hot: 7200000,   // 2 hours
        warm: 3600000,  // 1 hour
        cold: 600000,   // 10 minutes
      },
    },
    eviction: {
      policy: 'hybrid',
      maxEntries: 10000,
      maxMemoryBytes: 1073741824, // 1GB
      evictionBatchSize: 100,
      evictionThreshold: 0.9,
      lruWeight: 0.4,
      lfuWeight: 0.3,
      qualityWeight: 0.3,
      minQualityThreshold: 0.5,
    },
    invalidation: [],
    kvCache: {
      anchorPool: {
        maxAnchors: 1000,
        similarityThreshold: 0.8,
        embeddingDim: 768,
      },
      annIndex: {
        algorithm: 'hnsw',
        efSearch: 50,
        efConstruction: 200,
      },
      offsetPredictor: {
        enabled: true,
        minSamples: 10,
        confidenceThreshold: 0.7,
      },
    },
  },
  benchmark: {
    targets: {
      cacheHitRate: 0.70,      // 70% (KVCOMM target)
      ttftSpeedup: 7.8,        // 7.8x (KVCOMM target)
      memoryReduction: 0.50,   // 50%
      maxLatencyP99: 100,      // 100ms
      minThroughput: 1000,     // 1000 ops/sec
      maxMemoryUsage: 2147483648, // 2GB
    },
    workloads: {
      'shared-prefix': {
        prefixOverlap: 0.7,
        entropy: 0.3,
        burstiness: 0.5,
      },
    },
    regression: {
      maxHitRateRegression: 0.05,
      maxTTFTRegression: 0.05,
      maxMemoryRegression: 0.10,
    },
  },
  metrics: {
    enabled: true,
    interval: 1000,
    metrics: [
      'cache.hitRate',
      'cache.accessTime',
      'latency.ttft',
      'memory.heapUsed',
      'throughput.opsPerSecond',
    ],
    retentionPeriod: 86400000, // 24 hours
    export: {
      format: 'json',
      interval: 60000,
      batchSize: 1000,
    },
    sampling: {
      rate: 1.0,
      minSamples: 100,
      adaptive: true,
      targetSamplesPerInterval: 10000,
    },
  },
  optimization: {
    lazyLoading: {
      enabled: true,
      strategy: 'prefetch',
      prefetchThreshold: 0.7,
      maxConcurrentLoads: 10,
      loadTimeout: 5000,
    },
    batching: {
      enabled: true,
      maxBatchSize: 100,
      maxWaitTime: 50,
      minBatchSize: 10,
      strategy: 'adaptive',
    },
    parallelization: {
      enabled: true,
      maxWorkers: 4,
      queueSize: 1000,
      taskTimeout: 30000,
      scheduler: 'work-stealing',
    },
    prefetching: {
      enabled: true,
      lookahead: 3,
      maxPrefetchSize: 1048576, // 1MB
    },
  },
};
```

---

## Appendix A: Type Reference

### A.1 Common Types

```typescript
/** Timestamp in milliseconds since epoch */
type Timestamp = number;

/** Duration in milliseconds */
type Duration = number;

/** Size in bytes */
type ByteSize = number;

/** Probability value (0-1) */
type Probability = number;

/** Quality score (0-1) */
type QualityScore = number;

/** Similarity score (0-1) */
type SimilarityScore = number;

/** Unique identifier */
type UUID = string;

/** Semantic version string */
type Version = string;
```

### A.2 Result Types

```typescript
/** Operation result */
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

/** Async operation result */
type AsyncResult<T, E = Error> = Promise<Result<T, E>>;
```

---

## Appendix B: Schema Versioning

All schemas in this document follow semantic versioning:

- **Major version**: Breaking changes to schema structure
- **Minor version**: New optional fields added
- **Patch version**: Documentation updates, default value changes

Current schema version: `1.0.0`

---

*Document generated for glm-4.7 implementation agents*
*POLLN Performance Architecture Team*
