# KV-Cache Optimization Guide for POLLN

This guide provides detailed explanations of KV-cache optimization strategies, algorithms, and best practices for the POLLN distributed intelligence system.

## Table of Contents

1. [Introduction](#introduction)
2. [Compression Strategies](#compression-strategies)
3. [Eviction Policies](#eviction-policies)
4. [ANN Indexing](#ann-indexing)
5. [Cache Sizing](#cache-sizing)
6. [Prefetching](#prefetching)
7. [Production Considerations](#production-considerations)

## Introduction

### What is KV-Cache?

In transformer models, KV-cache (Key-Value cache) stores computed keys and values from attention layers to avoid recomputation during autoregressive generation. This is critical for performance:

```
Without KV-cache: O(n²) per token (recompute all previous tokens)
With KV-cache: O(n) per token (reuse cached keys/values)
```

### Why Optimize?

KV-cache can be **very large**:
- 32-layer model, 4096 hidden dim, 8K context
- Approx: 32 × 4096 × 8K × 4 bytes ≈ **4GB per sequence**

Optimization goals:
1. **Reduce memory** via compression
2. **Improve hit rate** via better eviction policies
3. **Speed up retrieval** via ANN indexing
4. **Right-size cache** via capacity planning
5. **Reduce latency** via prefetching

## Compression Strategies

### Overview

Different cache types have different characteristics:

| Cache Type | Characteristics | Best Method |
|------------|----------------|-------------|
| Attention | Low-rank structure, smooth | SVD, PQ |
| MLP | Sparse, high variance | Sparsification, Quantization |
| Embedding | Semantic clustering | Quantization, PQ |
| FFN | Dense, low-rank | SVD, Hybrid |

### SVD (Singular Value Decomposition)

**Best for**: Attention, FFN caches

**How it works**:
```python
# Decompose matrix: A = U × Σ × V^T
U, s, Vt = svd(A)

# Keep top-k singular values
U_k = U[:, :k]
s_k = s[:k]
Vt_k = Vt[:k, :]

# Compressed size: k × (m + n + 1) vs m × n
# Compression ratio: k / min(m, n)
```

**Pros**:
- Optimal low-rank approximation
- Preserves semantic structure
- Predictable quality

**Cons**:
- Slower compression/decompression
- Less effective on sparse data

**Parameters**:
- `retainedVariance`: 0.90-0.99 (higher = better quality, less compression)

### Quantization

**Best for**: Embeddings, MLP caches

**How it works**:
```python
# 8-bit quantization
scale = (max - min) / 255
quantized = round((data - min) / scale)

# 4-bit quantization
scale = (max - min) / 15
quantized = round((data - min) / scale)
```

**Pros**:
- Very fast
- Simple implementation
- Good for uniformly distributed data

**Cons**:
- Loss of precision
- Not ideal for skewed distributions

**Parameters**:
- `bits`: 8, 4, or 2 (fewer bits = more compression)
- Expected error: ~2^-bits

### Product Quantization (PQ)

**Best for**: Large embeddings, attention caches

**How it works**:
```python
# Split vector into subvectors
subvectors = split(vector, n=8)

# Quantize each subvector separately
codebook = kmeans(subvector, n_codewords=256)
encoding = nearest_codebook(subvector, codebook)

# Compressed: 8 subvectors × log2(256) = 64 bits
```

**Pros**:
- Excellent compression ratio
- Fast similarity search
- Works well on high-dimensional data

**Cons**:
- Complex implementation
- Requires training codebooks
- Slower reconstruction

**Parameters**:
- `n_subvectors`: 4-16 (more = better quality)
- `n_bits`: 4-8 (more = larger codebook)

### Sparsification

**Best for**: MLP activations

**How it works**:
```python
# Keep top-k magnitude values
threshold = percentile(abs(data), sparsity)
sparse = data * (abs(data) > threshold)
```

**Pros**:
- Preserves important values
- Good for sparse data
- Simple

**Cons**:
- Irregular memory access
- Less effective on dense data

**Parameters**:
- `sparsity`: 0.5-0.9 (higher = more compression)

## Eviction Policies

### Overview

When cache is full, which items to evict?

### LRU (Least Recently Used)

**Best for**: Temporal locality patterns

**How it works**:
```python
# Track access order
on_access(key):
    move_to_front(key)

on_evict():
    remove_from_back()
```

**Pros**:
- Simple
- Good for temporal locality
- Fast implementation

**Cons**:
- Vulnerable to one-time scans
- Doesn't consider frequency

**When to use**:
- Sequential access patterns
- Conversation workloads
- General-purpose caching

### LFU (Least Frequently Used)

**Best for**: Stable access patterns

**How it works**:
```python
# Track access frequency
on_access(key):
    frequency[key] += 1

on_evict():
    remove_lowest_frequency()
```

**Pros**:
- Keeps popular items
- Good for repetitive patterns

**Cons**:
- Slow to adapt to changes
- Can accumulate old items

**When to use**:
- Stable access patterns
- Hot data sets
- Read-heavy workloads

### ARC (Adaptive Replacement Cache)

**Best for**: Mixed workloads

**How it works**:
```python
# Maintain two lists:
# T1: Recent items (once)
# T2: Frequent items (multiple times)

# Adaptively balance T1 and T2 sizes
on_access(key):
    if in T1: move to T2
    elif in T2: update position
    elif in ghost lists: adapt_sizes()
```

**Pros**:
- Self-tuning
- Handles diverse patterns
- No parameter tuning needed

**Cons**:
- More complex
- Higher overhead

**When to use**:
- Mixed workloads
- Unknown patterns
- Production systems

### Other Policies

**FIFO**: Simple but ineffective
**Random**: Unpredictable performance
**CLOCK**: Approximation of LRU, lower overhead
**LIRS**: Advanced, good for scanned data

## ANN Indexing

### Overview

Finding similar KV-anchors efficiently:

```
Brute force: O(n) per query
ANN: O(log n) per query (with small accuracy loss)
```

### HNSW (Hierarchical Navigable Small World)

**Best for**: High recall, fast queries

**How it works**:
```python
# Build hierarchical graph
# Top layers: coarse graph
# Bottom layer: fine-grained graph

on_build(vector):
    # Insert at each level
    for level in max_level downto 0:
        neighbors = search_greedy(vector, level, ef)
        connect(vector, neighbors[:M])

on_search(vector):
    # Search from top down
    for level in max_level downto 0:
        entry_point = search_greedy(vector, level, ef=1)
    return search_greedy(vector, 0, ef)
```

**Parameters**:
- `M`: Connectivity (16-32)
  - Higher: Better recall, slower build, more memory
- `efConstruction`: Build-time candidate list (100-400)
  - Higher: Better index quality, slower build
- `efSearch`: Search-time candidate list (20-100)
  - Higher: Better recall, slower query

**When to use**:
- Need high recall (>0.95)
- Can tolerate slower builds
- Sufficient memory

### LSH (Locality Sensitive Hashing)

**Best for**: Very large datasets

**How it works**:
```python
# Hash similar items to same bucket
hash_function = random_projection()

on_build(vector):
    bands = split_vector(vector, n_bands)
    for band in bands:
        bucket = hash(band)
        add_to_bucket(bucket, vector)

on_search(vector):
    candidates = []
    bands = split_vector(vector, n_bands)
    for band in bands:
        bucket = hash(band)
        candidates.extend(get_bucket(bucket))
    return exact_search(candidates)
```

**Parameters**:
- `nBands`: Number of bands (10-50)
  - Higher: Higher precision, lower recall
- `nRows`: Rows per band (3-10)
  - Higher: More hash functions, slower

**When to use**:
- Very large datasets (>1M vectors)
- Approximate results acceptable
- Fast builds required

### Ball Tree

**Best for**: Low-dimensional data

**How it works**:
```python
# Build hierarchical bounding balls
on_build(vectors):
    if size < leaf_size:
        return leaf(vectors)

    split_dim = highest_variance_dim()
    left, right = split(vectors, split_dim)

    return node(
        left=on_build(left),
        right=on_build(right),
        center=mean(vectors),
        radius=max_distance(center, vectors)
    )

on_search(vector, k):
    # Prune branches that can't contain k-NN
    search_recursive(vector, k, root)
```

**Parameters**:
- `leafSize`: Points per leaf (20-100)
  - Larger: Faster build, slower query

**When to use**:
- Low-dimensional data (<100 dims)
- Exact distances required
- Medium-sized datasets

## Cache Sizing

### Knee Point Detection

Finding optimal cache size (diminishing returns):

```python
# Method 1: Distance from diagonal
x_norm = (cache_sizes - min) / (max - min)
y_norm = (hit_rates - min) / (max - min)
distances = abs(x_norm - y_norm) / sqrt(2)
knee_idx = argmax(distances)

# Method 2: Marginal benefit
marginal_benefit[i] = (hit_rate[i] - hit_rate[i-1]) /
                      (cache_size[i] - cache_size[i-1])
knee_idx = argmin(marginal_benefit)
```

### Sizing by Workload

| Workload | Optimal Size | Hit Rate | Characteristics |
|----------|--------------|----------|-----------------|
| Conversation | 100-200MB | 0.85-0.90 | High locality, short context |
| Coding | 200-500MB | 0.80-0.85 | Long-lived references |
| Analysis | 500MB-1GB | 0.75-0.80 | Large documents, sequential |
| General | 200-300MB | 0.82-0.88 | Mixed patterns |

### Cost-Benefit Analysis

```python
value = hit_rate / cost
optimal = argmax(value)

# Or weighted score
score = w1 * hit_rate + w2 * (1 / cache_size)
optimal = argmax(score)
```

## Prefetching

### Markov Chain Prediction

Predict next accesses based on history:

```python
# Build transition matrix
transitions[current_state][next_state] += 1

# Predict
probs = transitions[current_state]
predicted = argsort(probs)[-k:]
```

### ML-Based Prediction

Train model to predict next accesses:

```python
features = [
    last_n_accesses,      # Recent history
    time_since_access,    # Temporal features
    access_frequency,     # Popularity
    context_features      # Conversation state
]

model.train(features, next_access)
predicted = model.predict(current_features)
```

### Prefetch Strategies

| Strategy | Accuracy | Overhead | Best For |
|----------|----------|----------|----------|
| None | - | None | Random access |
| Always | Low | High | Sequential |
| Probability | Medium | Low | Mixed |
| Markov | High | Medium | Repetitive |
| ML | Very High | High | Complex patterns |

## Production Considerations

### Monitoring

Track these metrics:

```typescript
interface CacheMetrics {
  // Hit rates
  hitRate: number;
  missRate: number;

  // Compression
  compressionRatio: number;
  reconstructionError: number;

  // ANN
  recall: number;
  queryTime: number;

  // Sizing
  memoryUsage: number;
  evictions: number;

  // Prefetching
  prefetchAccuracy: number;
  prefetchOverhead: number;
}
```

### Tuning

1. **Start with defaults** from `config.ts`
2. **Monitor** metrics in production
3. **Adjust** based on workload
4. **A/B test** changes
5. **Iterate** continuously

### Common Issues

**Problem**: Low hit rate
- **Solution**: Increase cache size, adjust eviction policy

**Problem**: High memory usage
- **Solution**: Increase compression, reduce cache size

**Problem**: Slow queries
- **Solution**: Tune ANN parameters, reduce `efSearch`

**Problem**: Poor reconstruction
- **Solution**: Reduce compression ratio, change method

## Best Practices

1. **Start simple**: Use default config
2. **Measure everything**: Log all metrics
3. **Tune gradually**: Change one parameter at a time
4. **Validate**: Test on real workloads
5. **Monitor continuously**: Set up alerts

## Further Reading

- [KVCOMM Paper](https://arxiv.org/abs/XXXX) (KV-cache communication)
- [HNSW Paper](https://arxiv.org/abs/1603.09320) (ANN indexing)
- [ARC Paper](https://www.usenix.org/conference/fast03/technical-session/papers/nimrod) (Eviction)
- [Product Quantization](https://lear.inrialpes.fr/pubs/2011/JDS11/jegou_searching_with_quantization.pdf) (Compression)
