# PyTorch Real Integration - Architecture Documentation

## System Overview

The PyTorch Real Integration system provides **production-grade tracing** of real PyTorch models, capturing actual execution metrics to replace synthetic workload traces. This enables accurate simulation of distributed ML workloads with real-world performance characteristics.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     PyTorch Real Integration                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   PyTorch    │      │   Tracer     │      │   Exporter   │  │
│  │    Models    │──────│    Engine    │──────│   Module     │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                │                   │             │
│                                ▼                   ▼             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Layer      │      │    Cache     │      │    CRDT      │  │
│  │  Analyzer    │      │    Line      │      │   Scorer     │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────┐
         │         Production Traces            │
         │  ┌─────────┐  ┌─────────┐  ┌──────┐ │
         │  │  JSON   │  │  HDF5   │  │ CSV  │ │
         │  └─────────┘  └─────────┘  └──────┘ │
         └──────────────────────────────────────┘
```

## Core Components

### 1. PyTorchTracer (Main Engine)

**Purpose:** Orchestrates model tracing and data collection

**Responsibilities:**
- Load pre-trained models (torchvision, transformers)
- Register forward hooks on all traceable layers
- Execute inference and capture metrics
- Manage device placement (CPU/CUDA)

**Key Methods:**
```python
PyTorchTracer(model_name, device)
trace(input_data) -> ModelTrace
_load_model(model_name) -> nn.Module
_create_hook(layer_name, layer) -> HookFunction
```

**Design Decisions:**
- **Forward hooks** used instead of backward pass for minimal overhead
- **Graceful degradation** to dummy models if pre-trained unavailable
- **Device-aware** automatic CUDA detection and fallback

### 2. LayerAnalyzer (Metric Computation)

**Purpose:** Compute layer-specific metrics (FLOPs, types, etc.)

**Responsibilities:**
- Identify layer types (conv2d, linear, attention, etc.)
- Compute accurate FLOPs for each layer type
- Estimate memory accesses

**Key Methods:**
```python
get_layer_type(layer) -> str
compute_flops(layer, input_shape, output_shape) -> int
_conv2d_flops(layer, input_shape, output_shape) -> int
_linear_flops(layer, input_shape, output_shape) -> int
_attention_flops(layer, input_shape) -> int
```

**FLOP Computation Formulas:**

| Layer Type | Formula |
|------------|---------|
| Conv2d | `batch * out_c * H * W * (kernel_h * kernel_w * in_c)` |
| Linear | `batch * in_features * out_features` |
| Attention | `batch * seq_len^2 * embed_dim * num_heads + 3 * batch * seq_len * embed_dim^2` |
| ReLU/Activation | `numel(output)` |

**Design Decisions:**
- **Exact formulas** for common layers (Conv2d, Linear)
- **Estimated formulas** for complex layers (Attention)
- **Fallback to 0** for unknown layers

### 3. CacheLineAnalyzer (Memory Access)

**Purpose:** Analyze cache line access patterns at 64-byte granularity

**Responsibilities:**
- Compute which cache lines are accessed
- Track read vs write patterns
- Estimate spatial locality

**Key Methods:**
```python
compute_cache_lines(tensor) -> List[int]
analyze_tensor_memory(tensor, layer_name, access_type) -> List[CacheLineAccess]
```

**Cache Line Calculation:**
```python
CACHE_LINE_SIZE = 64  # bytes
element_size = tensor.element_size()  # 4 for float32, 2 for float16
elements_per_line = 64 // element_size
cache_line = (tensor.data_ptr() + offset) // 64
```

**Design Decisions:**
- **64-byte cache lines** (standard for x86)
- **Sequential addressing** for simplicity
- **Limited to 10K elements** per tensor for performance
- **Set-based deduplication** to avoid duplicate lines

### 4. CRDTScorer (Distributability Analysis)

**Purpose:** Score layers on CRDT-friendliness (0-1 scale)

**Responsibilities:**
- Compute base scores for layer types
- Adjust scores based on layer characteristics
- Identify optimization opportunities

**Key Methods:**
```python
compute_score(layer, layer_type, input_shape, output_shape) -> float
```

**Scoring Matrix:**

| Layer Type | Base Score | Rationale |
|------------|------------|-----------|
| ReLU | 0.95 | Element-wise, highly commutative |
| Conv2d | 0.85 | Shared weights, spatial locality |
| Linear | 0.70 | Matrix operations, moderate parallelism |
| Attention | 0.65 | QKV parallel, some reduction |
| LayerNorm | 0.55 | Reduction operations |
| BatchNorm | 0.60 | Statistics, batchable |

**Adjustments:**
- **+0.05** for large tensors (>1M elements)
- **-0.05** for small tensors (<1K elements)
- **+0.03** for large parameter counts (>1M params)

**Design Decisions:**
- **Base scores** from layer operation characteristics
- **Size adjustments** for distribution benefits
- **Bounds checking** to ensure [0, 1] range

### 5. TraceExporter (Output Generation)

**Purpose:** Export traces in multiple formats

**Responsibilities:**
- Generate JSON for human-readable output
- Generate HDF5 for large datasets
- Generate CSV for quick analysis
- Print console summaries

**Key Methods:**
```python
to_json(trace, filepath, include_all_cache_lines=False)
to_hdf5(trace, filepath)
to_csv(trace, filepath)
print_summary(trace)
```

**Format Characteristics:**

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| JSON | Debugging, small traces | Human-readable, portable | Large file size |
| HDF5 | Large traces, research | Compressed, efficient | Requires h5py |
| CSV | Quick analysis | Spreadsheet-friendly | Limited info |

**Design Decisions:**
- **Default limited cache lines** in JSON (first 100)
- **Optional full cache lines** with flag
- **GZIP compression** in HDF5
- **Batch-friendly** CSV output

## Data Flow

### Tracing Pipeline

```
1. Model Loading
   └─> Pre-trained (torchvision/transformers)
   └─> Dummy fallback
   └─> Device placement

2. Hook Registration
   └─> Iterate all named modules
   └─> Filter traceable layers
   └─> Register forward hooks

3. Inference Execution
   └─> Prepare input data
   └─> Forward pass with torch.no_grad()
   └─> Hooks capture metrics

4. Post-Processing
   └─> Remove hooks
   └─> Aggregate metrics
   └─> Build ModelTrace

5. Export
   └─> Generate JSON/HDF5/CSV
   └─> Print summary
```

### Hook Execution

```
Forward Pass Start
    │
    ├─> Layer N: Pre-hook
    │   ├─> Capture input shape
    │   ├─> Start timer
    │   └─>
    │
    ├─> Layer N: Computation
    │   ├─> Actual layer forward()
    │   └─>
    │
    ├─> Layer N: Post-hook
    │   ├─> Capture output shape
    │   ├─> Compute FLOPs
    │   ├─> Estimate memory
    │   ├─> Analyze cache lines
    │   ├─> Compute CRDT score
    │   ├─> Stop timer
    │   └─> Store LayerTrace
    │
    └─> Continue to next layer
```

## Memory Management

### Memory Considerations

1. **Tensor Storage**
   - Inputs/outputs referenced (not copied)
   - Hooks capture metadata only
   - Cache lines computed lazily

2. **Trace Storage**
   - Layer traces stored in list
   - Cache line accesses limited
   - Export after trace completion

3. **GPU Memory**
   - Automatic device detection
   - Fallback to CPU if OOM
   - Hooks don't retain gradients

### Performance Overhead

| Component | Overhead | Mitigation |
|-----------|----------|------------|
| Hook registration | ~1ms | One-time cost |
| Metric computation | ~5% per layer | Minimal calculations |
| Cache line analysis | ~2% per layer | Limited to 10K elements |
| JSON export | ~100ms | After trace completion |
| **Total** | **~5-10%** | Acceptable for tracing |

## Error Handling

### Graceful Degradation

```python
try:
    model = load_pretrained(model_name)
except Exception as e:
    logger.warning(f"Failed to load {model_name}: {e}")
    model = create_dummy_model(model_name)
```

### Error Scenarios

| Scenario | Handling |
|----------|----------|
| Model download fails | Use dummy model |
| CUDA OOM | CPU fallback |
| Unknown layer type | Default FLOPs=0, score=0.5 |
| Export fails | Log error, continue |

## Extensibility

### Adding New Layer Types

```python
# 1. Add to LayerAnalyzer.LAYER_TYPE_MAP
LAYER_TYPE_MAP[nn.NewLayer] = "new_layer"

# 2. Add FLOP computation
@staticmethod
def _new_layer_flops(layer, input_shape, output_shape):
    # Implement formula
    return flops

# 3. Add to compute_flops method
elif isinstance(layer, nn.NewLayer):
    return cls._new_layer_flops(layer, input_shape, output_shape)

# 4. Add CRDT score
BASE_SCORES["new_layer"] = 0.75  # Choose appropriate score
```

### Adding New Export Formats

```python
@staticmethod
def to_parquet(trace: ModelTrace, filepath: str):
    import pyarrow.parquet as pq
    # Convert trace to DataFrame
    # Save as Parquet
```

## Testing Strategy

### Test Coverage

1. **Unit Tests**
   - LayerAnalyzer: FLOP computation accuracy
   - CacheLineAnalyzer: Cache line calculations
   - CRDTScorer: Score bounds and logic

2. **Integration Tests**
   - End-to-end tracing workflow
   - Multi-format export
   - Error handling

3. **Performance Tests**
   - Tracing overhead measurement
   - Memory leak detection
   - Large model handling

### Test Fixtures

- `simple_model`: Conv2d + ReLU + Pooling
- `linear_model`: Linear + ReLU layers
- `temp_output_dir`: Isolated test outputs

## Production Considerations

### Scalability

- **Large models:** BERT-large, GPT-3
- **Batch processing:** Trace multiple inputs
- **Distributed tracing:** Multi-GPU support (future)

### Reliability

- **Deterministic traces:** Same input → same trace
- **Reproducibility:** Fixed random seeds
- **Validation:** Cross-check FLOPs with profilers

### Performance

- **Minimal overhead:** <10% slowdown
- **Memory efficient:** No tensor retention
- **Fast export:** Streaming for large traces

## Future Enhancements

### Short Term
- [ ] Dynamic shape support
- [ ] Training loop tracing (backward pass)
- [ ] Profiler integration (torch.profiler)

### Medium Term
- [ ] Multi-GPU tracing
- [ ] Real-time tracing API
- [ ] ONNX model support

### Long Term
- [ ] Distributed tracing coordination
- [ ] Hardware counter integration
- [ ] ML-based workload prediction

## References

- PyTorch Hooks: https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.register_forward_hook
- CUDA Cache Lines: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#cache-lines
- CRDT Theory: https://hal.inria.fr/hal-00955301/document
