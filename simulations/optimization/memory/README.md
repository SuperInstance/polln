# Memory Optimization Simulations for POLLN

This directory contains comprehensive Python simulations for optimizing KV-cache compression and retrieval in the POLLN distributed intelligence system.

## Overview

These simulations find optimal parameters for:
- **Compression**: Best compression strategies for different cache types
- **Eviction**: Optimal cache eviction policies
- **ANN Indexing**: Tuning approximate nearest neighbor search
- **Sizing**: Finding optimal cache capacities
- **Prefetching**: Predictive cache loading strategies

## Project Structure

```
simulations/optimization/memory/
├── compression_optimization.py   # KV-cache compression strategies
├── eviction_policy.py            # Cache eviction policy testing
├── ann_index_tuning.py           # ANN index parameter tuning
├── cache_sizing.py               # Optimal cache capacity analysis
├── prefetching.py                # Prefetching strategy optimization
├── cache_simulator.py            # Realistic KV-cache simulator
├── run_all.py                    # Master optimizer script
├── generate_config.py            # TypeScript config generator
├── test_memory.py                # Test suite
├── README.md                     # This file
├── CACHE_GUIDE.md                # Detailed cache optimization guide
├── INTEGRATION.md                # Integration instructions
└── results/                      # Simulation results (generated)
    ├── compression_results.json
    ├── eviction_results.json
    ├── ann_results.json
    ├── sizing_results.json
    ├── prefetch_results.json
    └── unified_config.json
```

## Quick Start

### 1. Run All Optimizations

```bash
# Run all memory optimizations
python simulations/optimization/memory/run_all.py

# This will:
# - Run all 5 optimization simulations
# - Generate results JSON files
# - Create TypeScript configuration file
```

### 2. Run Individual Optimizations

```bash
# Compression optimization
python simulations/optimization/memory/compression_optimization.py

# Eviction policy testing
python simulations/optimization/memory/eviction_policy.py

# ANN index tuning
python simulations/optimization/memory/ann_index_tuning.py

# Cache sizing analysis
python simulations/optimization/memory/cache_sizing.py

# Prefetching optimization
python simulations/optimization/memory/prefetching.py
```

### 3. Generate Configuration

```bash
# Generate TypeScript config from results
python simulations/optimization/memory/generate_config.py
```

### 4. Run Tests

```bash
# Run test suite
python simulations/optimization/memory/test_memory.py
```

## Simulation Details

### Compression Optimization (`compression_optimization.py`)

Tests different compression strategies for KV-cache data:

**Strategies:**
- SVD (Singular Value Decomposition)
- Quantization (8-bit, 4-bit, 2-bit)
- Sparsification (magnitude-based)
- Product Quantization (PQ)
- Hybrid approaches

**Cache Types:**
- Attention (K/V matrices)
- MLP (activations)
- Embedding (token embeddings)
- FFN (feed-forward states)

**Metrics:**
- Compression ratio
- Reconstruction error (MSE)
- Retrieval quality (cosine similarity)
- Compression/decompression time

### Eviction Policy (`eviction_policy.py`)

Simulates different cache eviction policies:

**Policies:**
- LRU (Least Recently Used)
- LFU (Least Frequently Used)
- FIFO (First In First Out)
- Random
- ARC (Adaptive Replacement Cache)
- CLOCK

**Access Patterns:**
- Temporal locality
- Spatial locality
- Zipf distribution
- Conversation patterns
- Hybrid patterns

**Metrics:**
- Hit rate
- Miss rate
- Eviction cost
- Memory usage

### ANN Index Tuning (`ann_index_tuning.py`)

Optimizes Approximate Nearest Neighbor index parameters:

**Algorithms:**
- HNSW (Hierarchical Navigable Small World)
- LSH (Locality Sensitive Hashing)
- Ball Tree
- IVF (Inverted File Index)

**Parameters:**
- HNSW: M, efConstruction, efSearch
- LSH: nBands, nRows
- Ball Tree: leafSize
- IVF: nClusters, nProbe

**Metrics:**
- Recall (accuracy)
- Query time
- Index size
- Build time

### Cache Sizing (`cache_sizing.py`)

Finds optimal cache sizes for different workloads:

**Workloads:**
- Conversation (dialogue-heavy)
- Coding (code with long contexts)
- Analysis (document analysis)
- General (mixed)

**Analysis:**
- Hit rate vs cache size
- Knee point detection
- Cost-benefit analysis
- Marginal benefit calculation

### Prefetching (`prefetching.py`)

Evaluates prefetching strategies:

**Strategies:**
- None (baseline)
- Always (aggressive)
- Probability-based
- Markov prediction
- ML-based (simulated)
- Hybrid

**Metrics:**
- Prefetch accuracy
- Coverage
- Memory overhead
- Latency reduction
- Efficiency

### Cache Simulator (`cache_simulator.py`)

Realistic KV-cache access pattern simulator:

**Patterns:**
- Sequential decode (autoregressive)
- Context reuse (multi-turn)
- Long context (documents)
- Branching (tree-based search)

**Models:**
- Attention K/V reuse
- Context window patterns
- Multi-turn conversations
- Agent preferences

## Output Files

### Results (`results/`)

JSON files containing detailed simulation results:

- `compression_results.json` - Compression experiment results
- `eviction_results.json` - Eviction policy results
- `ann_results.json` - ANN index tuning results
- `sizing_results.json` - Cache sizing analysis
- `prefetch_results.json` - Prefetching strategy results
- `unified_config.json` - Unified configuration

### Configuration (`src/core/kv/config.ts`)

Auto-generated TypeScript configuration:

```typescript
export const KV_CACHE_CONFIG = {
  compression: {
    attention: { method: 'svd', ratio: 0.1, quality: 0.95 },
    mlp: { method: 'quantization', ratio: 0.25, quality: 0.90 },
    // ...
  },
  eviction: {
    policy: 'adaptive_arc',
    maxSize: 512 * 1024 * 1024,
    expectedHitRate: 0.85
  },
  annIndex: {
    algorithm: 'hnsw',
    params: { M: 16, efConstruction: 200, efSearch: 50 }
  },
  // ...
};
```

## Dependencies

Required Python packages:

```bash
numpy>=1.20.0
scikit-learn>=0.24.0
```

Install with:

```bash
pip install numpy scikit-learn
```

## Configuration

Each simulation has configurable parameters. Edit the files directly or modify the `run_all.py` script to customize:

- Cache sizes
- Number of iterations
- Workload types
- Metric thresholds

## Interpreting Results

### Compression Results

Look for:
- **Compression Ratio**: Lower is better (more compression)
- **Quality**: Higher is better (closer to 1.0)
- **Best Tradeoff**: High quality with low ratio

### Eviction Results

Look for:
- **Hit Rate**: Higher is better
- **Policy**: Which policy works best for your workload
- **Knee Point**: Where increasing cache size has diminishing returns

### ANN Results

Look for:
- **Recall**: Should be > 0.90 for production
- **Query Time**: Lower is better
- **Pareto Frontier**: Best recall/time tradeoff

### Sizing Results

Look for:
- **Knee Point**: Optimal cache size
- **Hit Rate per MB**: Efficiency metric
- **Workload-specific**: Different workloads may need different sizes

### Prefetch Results

Look for:
- **Efficiency**: % of useful prefetches
- **Latency Reduction**: Time saved
- **Memory Overhead**: Extra memory used

## Integration with POLLN

After running optimizations:

1. **Review generated config**: `src/core/kv/config.ts`
2. **Import in your code**:
   ```typescript
   import { KV_CACHE_CONFIG } from './kv/config';
   ```
3. **Use in kvanchor.ts**:
   ```typescript
   const config = KV_CACHE_CONFIG.compression.attention;
   const compressed = this.compress(data, config.method, config.ratio);
   ```
4. **Use in ann-index.ts**:
   ```typescript
   const annConfig = KV_CACHE_CONFIG.annIndex;
   this.index = new HNSWIndex(annConfig.params);
   ```

## Troubleshooting

### Out of Memory

Reduce simulation parameters:
- Fewer cache sizes to test
- Smaller data dimensions
- Fewer iterations

### Slow Execution

Run individual simulations instead of all at once:
```bash
python simulations/optimization/memory/compression_optimization.py
```

### Import Errors

Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

## Contributing

To add new optimizations:

1. Create new simulation file following existing patterns
2. Add to `run_all.py`
3. Update `generate_config.py` to include new results
4. Add tests to `test_memory.py`

## License

Same as POLLN project.

## Contact

For questions or issues, please open a GitHub issue on the POLLN repository.
