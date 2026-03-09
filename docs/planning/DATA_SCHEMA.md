# POLLN Data Schema Documentation

**Version**: 1.0.0
**Last Updated**: 2026-03-08
**Author**: Architect-Data (Planning Team)

---

## Table of Contents

1. [Overview](#overview)
2. [Core Data Models](#core-data-models)
3. [Embedding Schemas](#embedding-schemas)
4. [KV-Cache Schemas](#kv-cache-schemas)
5. [Storage Interface Contracts](#storage-interface-contracts)
6. [Serialization Formats](#serialization-formats)
7. [Data Invariants](#data-invariants)
8. [Data Flow Diagrams](#data-flow-diagrams)

---

## Overview

POLLN's data architecture centers on three primary data types that enable distributed intelligence:

1. **PollenGrains** - Compressed behavioral patterns (embeddings)
2. **KVAnchors** - Compressed KV-cache segments for efficient context reuse
3. **A2APackages** - Agent-to-agent communication artifacts

The system uses a layered approach where data flows through multiple transformation stages, each with specific schema requirements.

### Design Principles

- **Immutability by Default**: Core data structures are immutable; updates create new versions
- **Privacy-First**: All schemas include privacy tier metadata
- **Traceability**: Every data artifact has `parentIds` and `causalChainId` for replay
- **Compression-Aware**: Schemas support both raw and compressed representations

---

## Core Data Models

### 1. PollenGrain (Behavioral Embedding)

```typescript
interface PollenGrain {
  // Identity
  id: string;                    // UUID v4
  gardenerId: string;            // Owner/cultivator identifier

  // Embedding Vector
  embedding: number[];           // L2-normalized embedding vector
  dimensionality: number;        // Vector dimension (32-1024)

  // Source Tracking
  sourceLogCount: number;        // Number of behavior logs compressed
  privacyTier: PrivacyTier;      // 'LOCAL' | 'MEADOW' | 'RESEARCH' | 'PUBLIC'

  // Differential Privacy Metadata
  dpMetadata?: {
    epsilon: number;             // Privacy budget consumed
    delta: number;               // Privacy relaxation parameter
    noiseScale: number;          // Gaussian noise scale applied
  };

  // Temporal
  createdAt: number;             // Unix timestamp (ms)
  updatedAt: number;             // Unix timestamp (ms)
}
```

**Invariants**:
- `embedding.length === dimensionality`
- `dimensionality` must match `PRIVACY_PARAMS[privacyTier].dimensionality`
- `L2Norm(embedding) === 1.0` (normalized)
- `createdAt <= updatedAt`

**Storage Size Estimate**:
- LOCAL (1024-dim): ~8KB per grain
- MEADOW (512-dim): ~4KB per grain
- PUBLIC (128-dim): ~1KB per grain

---

### 2. KVAnchor (Compressed KV-Cache)

```typescript
interface KVAnchor {
  // Identity
  anchorId: string;              // Format: anchor-{layerId}-{segmentId}-{timestamp}
  layerId: number;               // Transformer layer index (0-based)
  segmentId: string;             // Original segment identifier

  // Compressed KV Data
  compressedKeys: Float32Array;   // Quantized + projected key cache
  compressedValues: Float32Array; // Quantized + projected value cache

  // Embedding for Similarity Search
  embedding: number[];           // Search embedding (128-dim default)

  // Source Reference
  sourceSegmentId: string;       // Original KVCacheSegment.id
  sourceAgentId: string;         // Agent that created this anchor

  // Usage Statistics (LRU)
  usageCount: number;            // Number of times accessed
  lastUsed: number;              // Unix timestamp (ms)

  // Quality Metrics
  qualityScore: number;          // 0-1, based on reconstruction error
  compressionRatio: number;      // original_size / compressed_size

  // Temporal
  createdAt: number;
  updatedAt: number;

  // Clustering (optional)
  clusterId?: string;
  clusterCenterDistance?: number;
}
```

**Invariants**:
- `0 <= qualityScore <= 1`
- `compressionRatio >= 1.0`
- `compressedKeys.length === keyProjectionDim`
- `compressedValues.length === valueProjectionDim`
- `embedding.length === embeddingDim`
- `layerId >= 0`

**Storage Size Estimate**:
- Key projection (64-dim): 256 bytes
- Value projection (64-dim): 256 bytes
- Embedding (128-dim): 512 bytes
- Metadata: ~200 bytes
- **Total**: ~1.2KB per anchor

---

### 3. KVCacheSegment (Original, Uncompressed)

```typescript
interface KVCacheSegment {
  layerId: number;
  segmentId: string;
  tokens: number[];              // Token IDs

  // KV Tensors
  keyCache: number[][];          // Shape: [seq_len, d_k]
  valueCache: number[][];        // Shape: [seq_len, d_v]

  metadata: KVCacheMetadata;
}

interface KVCacheMetadata {
  createdAt: number;
  modelHash: string;             // Hash of model architecture
  agentId: string;
  conversationId?: string;
  turnNumber: number;            // Conversation turn
  position: number;              // Starting position in sequence
  length: number;                // Number of tokens
}
```

**Size Estimate** (typical LLM):
- seq_len=128, d_k=d_v=64: ~128KB per segment

---

### 4. A2APackage (Agent Communication)

```typescript
interface A2APackage<T = unknown> {
  id: string;                    // UUID v4
  timestamp: number;             // Unix timestamp (ms)

  // Routing
  senderId: string;
  receiverId: string;

  // Content
  type: string;                  // Message type discriminator
  payload: T;                    // Type-specific payload

  // Causal Chain (Traceability)
  parentIds: string[];           // IDs of triggering packages
  causalChainId: string;         // Shared ID for related packages

  // Privacy
  privacyLevel: PrivacyLevel;    // 'PUBLIC' | 'COLONY' | 'PRIVATE'

  // Subsumption Architecture
  layer: SubsumptionLayer;       // 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE'

  // Differential Privacy (optional)
  dpMetadata?: {
    epsilon: number;
    delta: number;
    noiseScale: number;
  };
}
```

**Invariants**:
- `timestamp` is monotonically increasing within a causal chain
- `parentIds` must reference existing packages or be empty
- SAFETY layer packages bypass all other layers

---

## Embedding Schemas

### Privacy Tier Configuration

```typescript
type PrivacyTier = 'LOCAL' | 'MEADOW' | 'RESEARCH' | 'PUBLIC';

interface PrivacyParams {
  dimensionality: number;
  epsilon: number;               // DP epsilon
  delta: number;                 // DP delta
}

const PRIVACY_PARAMS: Record<PrivacyTier, PrivacyParams> = {
  LOCAL:    { dimensionality: 1024, epsilon: Infinity, delta: 0 },
  MEADOW:   { dimensionality: 512,  epsilon: 1.0,      delta: 1e-5 },
  RESEARCH: { dimensionality: 256,  epsilon: 0.5,      delta: 1e-6 },
  PUBLIC:   { dimensionality: 128,  epsilon: 0.3,      delta: 1e-7 },
};
```

### BES Configuration

```typescript
interface BESConfig {
  defaultDimensionality: number;  // Default: 1024
  defaultPrivacyTier: PrivacyTier;// Default: 'LOCAL'
  maxDimensionality: number;      // Default: 1024
  minDimensionality: number;      // Default: 32
}
```

### Privacy Budget Tracking

```typescript
interface PrivacyBudgetStatus {
  tier: PrivacyTier;
  used: number;
  total: number;
  remaining: number;
}
```

---

## KV-Cache Schemas

### Anchor Pool Configuration

```typescript
interface KVAnchorPoolConfig {
  // Capacity
  maxAnchors: number;            // Default: 1000
  maxAgeMs: number;              // Default: 86400000 (24h)

  // Quality Thresholds
  minQualityScore: number;       // Default: 0.7
  minCompressionRatio: number;   // Default: 2.0

  // Matching
  similarityThreshold: number;   // Default: 0.8
  maxMatches: number;            // Default: 5

  // Compression
  keyProjectionDim: number;      // Default: 64
  valueProjectionDim: number;    // Default: 64
  quantizationBits: 4 | 8;       // Default: 8

  // Embedding
  embeddingDim: number;          // Default: 128

  // Clustering
  enableClustering: boolean;     // Default: true
  numClusters: number;           // Default: 10
  clusterThreshold: number;      // Default: 0.3

  // LRU
  enableLRU: boolean;            // Default: true
  lruSampleSize: number;         // Default: 100

  // ANN Index
  enableANN: boolean;            // Default: true
  annAlgorithm: ANNAlgorithm;    // Default: 'auto'
  annRebuildThreshold: number;   // Default: 100
}
```

### Anchor Match Result

```typescript
interface AnchorMatch {
  anchor: KVAnchor;
  similarity: number;            // Cosine similarity
  tokenOverlap: number;          // Shared token count
  positionalDeviation: number;   // Position difference
}
```

### Offset Prediction

```typescript
interface OffsetPrediction {
  anchorId: string;
  predictedOffset: number[][];   // Shape: [seq_len, d_model]
  confidence: number;            // 0-1
  deviationScore: number;        // Prediction variance
}
```

---

## Storage Interface Contracts

### Cache Interface

```typescript
interface Cache<T = TensorLike> {
  data: T;
  sequenceLength: number;
  metadata?: CacheMetadata;
}

interface CacheMetadata {
  id?: string;
  timestamp?: number;
  sourceAgentId?: string;
  version?: number;
  compressionInfo?: {
    originalSize: number;
    compressedSize: number;
    method: string;
  };
}
```

### ANN Index Interface

```typescript
interface ANNIndexConfig {
  algorithm: ANNAlgorithm;       // 'hnsw' | 'lsh' | 'balltree' | 'auto'
  dimension: number;

  // HNSW
  hnsw?: {
    M: number;                   // Max connections (default: 16)
    efConstruction: number;      // Build candidates (default: 200)
    efSearch: number;            // Search candidates (default: 50)
  };

  // LSH
  lsh?: {
    numTables: number;           // Hash tables (default: 10)
    hashSize: number;            // Hash functions per table (default: 10)
    width: number;               // Bucket width (default: 4.0)
  };

  // Ball Tree
  balltree?: {
    leafSize: number;            // Max points per leaf (default: 40)
    metric: 'euclidean' | 'manhattan' | 'cosine';
  };
}

interface SearchResult {
  index: number;
  distance: number;
  similarity: number;
}
```

### LMCache Adapter Interface

```typescript
interface LMCacheAdapterConfig {
  backend: LMCacheBackendType;   // 'cpu' | 'disk' | 's3' | 'redis'
  chunkSize: number;
  maxChunks: number;
  compression: boolean;
  compressionType?: 'gzip' | 'zstd';
  evictionPolicy: 'lru' | 'lfu';
  maxSizeGb: number;

  // Distributed
  enableRemote: boolean;
  remoteUrl?: string;
  workerId?: string;

  // Connection Pooling
  maxConnections?: number;       // Default: 10
  connectionTimeout?: number;    // Default: 30000ms
  requestTimeout?: number;       // Default: 10000ms

  // Retry
  maxRetries?: number;           // Default: 3
  retryDelay?: number;           // Default: 1000ms

  // Local Cache
  enableLocalCache: boolean;
  localCacheSize?: number;       // Default: 1000
  localCacheTtl?: number;        // Default: 3600000ms (1h)

  // Batching
  enableBatching: boolean;
  batchSize?: number;            // Default: 10
  batchTimeout?: number;         // Default: 1000ms
}
```

---

## Serialization Formats

### Serialized LMCache Format

```typescript
interface SerializedLMCache {
  // Header
  version: number;               // Schema version
  format: string;                // 'polln-kvanchor'
  timestamp: number;

  // Identification
  anchorId: string;
  layerId: number;
  segmentId: string;
  sourceAgentId: string;

  // KV Data
  kvData: {
    keys: SerializedTensor;
    values: SerializedTensor;
  };

  // Embedding
  embedding: {
    vector: number[];
    dimension: number;
  };

  // Metadata
  metadata: {
    qualityScore: number;
    compressionRatio: number;
    usageCount: number;
    lastUsed: number;
    createdAt: number;
    updatedAt: number;
    clusterId?: string;
    clusterCenterDistance?: number;
  };

  // Privacy (federated sharing)
  privacy?: {
    epsilon: number;
    delta: number;
    noiseScale: number;
  };
}
```

### Serialized Tensor

```typescript
interface SerializedTensor {
  dtype: 'float32' | 'float64' | 'int8' | 'int16';
  shape: number[];
  data: string;                  // Base64 encoded binary
  compressed: boolean;
}
```

### Encoding/Decoding

**Float32Array to Base64**:
```typescript
function bufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}
```

**Base64 to Float32Array**:
```typescript
function base64ToBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}
```

---

## Data Invariants

### Global Invariants

1. **ID Uniqueness**: All `id`, `anchorId`, `segmentId` values are globally unique
2. **Timestamp Monotonicity**: Within a causal chain, timestamps are monotonically increasing
3. **Embedding Normalization**: All embeddings are L2-normalized (unit vectors)
4. **Privacy Budget**: `used <= total` for all privacy tiers

### PollenGrain Invariants

```typescript
// INV-PG-001: Dimensionality matches embedding length
assert(grain.embedding.length === grain.dimensionality);

// INV-PG-002: Dimensionality matches privacy tier
assert(grain.dimensionality === PRIVACY_PARAMS[grain.privacyTier].dimensionality);

// INV-PG-003: Embedding is L2-normalized
const norm = Math.sqrt(grain.embedding.reduce((s, v) => s + v * v, 0));
assert(Math.abs(norm - 1.0) < 1e-6);

// INV-PG-004: Timestamp ordering
assert(grain.createdAt <= grain.updatedAt);
```

### KVAnchor Invariants

```typescript
// INV-KA-001: Quality score bounds
assert(anchor.qualityScore >= 0 && anchor.qualityScore <= 1);

// INV-KA-002: Compression ratio is positive
assert(anchor.compressionRatio >= 1.0);

// INV-KA-003: Usage count is non-negative
assert(anchor.usageCount >= 0);

// INV-KA-004: Layer ID is non-negative
assert(anchor.layerId >= 0);

// INV-KA-005: Timestamp ordering
assert(anchor.createdAt <= anchor.updatedAt);
assert(anchor.createdAt <= anchor.lastUsed);
```

### A2APackage Invariants

```typescript
// INV-A2A-001: Parent existence (referential integrity)
for (const parentId of pkg.parentIds) {
  assert(packageExists(parentId));
}

// INV-A2A-002: Timestamp consistency
for (const parentId of pkg.parentIds) {
  assert(getPackage(parentId).timestamp < pkg.timestamp);
}

// INV-A2A-003: Causal chain consistency
for (const parentId of pkg.parentIds) {
  assert(getPackage(parentId).causalChainId === pkg.causalChainId);
}
```

### Cache Invariants

```typescript
// INV-CACHE-001: Sequence length matches data
assert(cache.sequenceLength === getSequenceLength(cache.data));

// INV-CACHE-002: Version monotonicity on updates
assert(newCache.metadata.version > oldCache.metadata.version);
```

---

## Data Flow Diagrams

### 1. PollenGrain Creation Flow

```
[Behavior Log] --> [Embedding Extractor] --> [Raw Embedding]
                                                |
                                                v
                                        [Dimensionality Reduction]
                                        (based on privacy tier)
                                                |
                                                v
                                        [Differential Privacy]
                                        (Gaussian mechanism)
                                                |
                                                v
                                        [L2 Normalization]
                                                |
                                                v
                                        [PollenGrain]
                                                |
                                                v
                                        [BES Storage]
```

### 2. KVAnchor Creation Flow

```
[KVCacheSegment] --> [Flatten Keys/Values]
                            |
                            v
                    [Project to Lower Dim]
                            |
                            v
                    [Quantization]
                    (uniform/kmeans/product)
                            |
                            v
                    [Float32Array]
                            |
                            v
                [Compute Embedding]
                            |
                            v
                [Estimate Quality Score]
                            |
                            v
                    [KVAnchor]
                            |
                            v
                [Assign to Cluster]
                            |
                            v
                [Update ANN Index]
                            |
                            v
                [KVAnchorPool Storage]
```

### 3. Anchor Matching Flow

```
[Query Segment] --> [Compute Query Embedding]
                            |
                            v
                    [ANN Index Search]
                            |
                            v
                    [Cluster Lookup]
                    (if enabled)
                            |
                            v
                    [Similarity Filter]
                    (threshold >= 0.8)
                            |
                            v
                    [AnchorMatch[]]
                            |
                            v
                    [Offset Prediction]
                            |
                            v
                    [KVCache Reconstruction]
```

### 4. A2A Package Flow

```
[Agent A] --> [Create A2APackage]
                    |
                    v
            [Safety Layer Check]
                    |
                    v
            [Apply Privacy Tier]
                    |
                    v
            [Add DP Noise]
            (if not LOCAL)
                    |
                    v
            [Serialize Package]
                    |
                    v
            [Transport Layer]
                    |
                    v
            [Agent B] --> [Validate Package]
                                |
                                v
                        [Process Payload]
```

### 5. LMCache Sync Flow

```
[KVAnchorPool] --> [Serialize Anchors]
                            |
                            v
                    [Python Bridge]
                            |
                            v
                    [Connection Pool]
                            |
                            v
                    [Batch Update]
                    (if enabled)
                            |
                            v
                    [LMCache Backend]
                    (cpu/disk/s3/redis)
                            |
                            v
                    [Distributed Sync]
                    (if enabled)
```

---

## Appendix: Type Definitions Reference

### Enums

```typescript
enum PrivacyLevel {
  PUBLIC = 'PUBLIC',
  COLONY = 'COLONY',
  PRIVATE = 'PRIVATE'
}

enum SubsumptionLayer {
  SAFETY = 'SAFETY',
  REFLEX = 'REFLEX',
  HABITUAL = 'HABITUAL',
  DELIBERATE = 'DELIBERATE'
}

enum SafetySeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

type PrivacyTier = 'LOCAL' | 'MEADOW' | 'RESEARCH' | 'PUBLIC';
type ANNAlgorithm = 'hnsw' | 'lsh' | 'balltree' | 'auto';
type LMCacheBackendType = 'cpu' | 'disk' | 's3' | 'redis';
type QuantizationMethod = 'uniform' | 'kmeans' | 'product';
```

### Utility Types

```typescript
type TensorLike = any; // Arrays, TypedArrays, nested structures
type EmbeddingVector = number[];
```

---

*Document generated for glm-4.7 implementation agents*
*Repository: https://github.com/SuperInstance/polln*
