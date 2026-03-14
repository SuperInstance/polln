# PyTorch Real Integration - Complete Documentation Index

Complete documentation index for the PyTorch Real Integration system.

## Quick Navigation

- **[Quick Start](#quick-start)** - Get tracing in 5 minutes
- **[Documentation](#documentation)** - Detailed guides
- **[Code Reference](#code-reference)** - API documentation
- **[Examples](#examples)** - Usage examples
- **[Integration](#integration)** - Production integration

---

## Quick Start

### Installation (2 minutes)
```bash
cd C:/Users/casey/polln/production/pytorch_integration
pip install -r requirements.txt
```

### Basic Usage (3 lines of code)
```python
from pytorch_tracer import PyTorchTracer, TraceExporter

tracer = PyTorchTracer("resnet50", device="cuda")
trace = tracer.trace(torch.randn(1, 3, 224, 224).cuda())
TraceExporter.to_json(trace, "resnet50.json")
```

**Full Guide:** [QUICKSTART.md](QUICKSTART.md)

---

## Documentation

### User Guides

| Document | Description | Link |
|----------|-------------|------|
| **Quick Start** | Get tracing in 5 minutes | [QUICKSTART.md](QUICKSTART.md) |
| **README** | Full feature documentation | [README.md](README.md) |
| **Architecture** | System design and internals | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Integration** | Production framework integration | [INTEGRATION.md](INTEGRATION.md) |

### Quick Reference

| Task | Command | File |
|------|---------|------|
| **Trace model** | `python pytorch_tracer.py` | [pytorch_tracer.py](pytorch_tracer.py) |
| **Run examples** | `python example_usage.py` | [example_usage.py](example_usage.py) |
| **Run tests** | `pytest test_pytorch_tracer.py` | [test_pytorch_tracer.py](test_pytorch_tracer.py) |
| **Install** | `pip install -r requirements.txt` | [requirements.txt](requirements.txt) |

---

## Code Reference

### Core Components

#### 1. PyTorchTracer
**Purpose:** Main tracing engine

```python
class PyTorchTracer:
    def __init__(self, model_name: str, device: str = "cuda")
    def trace(self, input_data) -> ModelTrace
```

**Key Features:**
- Loads pre-trained models (ResNet, BERT, GPT-2)
- Registers forward hooks
- Captures layer metrics
- Graceful fallback to dummy models

#### 2. LayerAnalyzer
**Purpose:** Compute layer metrics

```python
class LayerAnalyzer:
    @staticmethod
    def get_layer_type(layer: nn.Module) -> str
    @staticmethod
    def compute_flops(layer, input_shape, output_shape) -> int
```

**Layer Types Supported:**
- Conv2d, Linear, ReLU, GELU
- BatchNorm, LayerNorm
- Attention, Embedding
- Pooling layers

#### 3. CacheLineAnalyzer
**Purpose:** Analyze memory access patterns

```python
class CacheLineAnalyzer:
    CACHE_LINE_SIZE = 64  # bytes

    @staticmethod
    def compute_cache_lines(tensor: torch.Tensor) -> List[int]
```

**Features:**
- 64-byte cache line granularity
- Supports float32 and float16
- Set-based deduplication

#### 4. CRDTScorer
**Purpose:** Score layer distributability

```python
class CRDTScorer:
    @staticmethod
    def compute_score(layer, layer_type, input_shape, output_shape) -> float
```

**Score Interpretation:**
- 0.9-1.0: Excellent (element-wise ops)
- 0.8-0.9: Very good (Conv2D, Embedding)
- 0.6-0.8: Good (Linear, Pooling)
- <0.6: Challenging (reduction ops)

#### 5. TraceExporter
**Purpose:** Export traces in multiple formats

```python
class TraceExporter:
    @staticmethod
    def to_json(trace: ModelTrace, filepath: str)
    @staticmethod
    def to_hdf5(trace: ModelTrace, filepath: str)
    @staticmethod
    def to_csv(trace: ModelTrace, filepath: str)
    @staticmethod
    def print_summary(trace: ModelTrace)
```

### Data Structures

#### ModelTrace
```python
@dataclass
class ModelTrace:
    model_name: str
    framework: str
    layers: List[LayerTrace]
    total_flops: int
    total_memory_mb: float
    total_time_ms: float
    capture_timestamp: str
    device: str
    input_shape: Tuple[int, ...]
```

#### LayerTrace
```python
@dataclass
class LayerTrace:
    layer_name: str
    layer_type: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    parameters: int
    flops: int
    memory_reads_mb: float
    memory_writes_mb: float
    compute_time_ms: float
    cache_line_accesses: List[int]
    crdt_friendly_score: float
    layer_depth: int
    parent_name: str
```

---

## Examples

### Available Examples

| Example | Description | File |
|---------|-------------|------|
| **Example 1** | Basic model tracing | [example_usage.py](example_usage.py#L29) |
| **Example 2** | Layer-by-layer analysis | [example_usage.py](example_usage.py#L55) |
| **Example 3** | Memory access patterns | [example_usage.py](example_usage.py#L103) |
| **Example 4** | CRDT optimization | [example_usage.py](example_usage.py#L147) |
| **Example 5** | Model comparison | [example_usage.py](example_usage.py#L213) |
| **Example 6** | Visualization | [example_usage.py](example_usage.py#L266) |

### Running Examples

```bash
# Run all examples
python example_usage.py

# Run specific example
python -c "from example_usage import example_1_basic_tracing; example_1_basic_tracing()"
```

### Example Output

```
================================================================================
Model Trace Summary: resnet50
================================================================================
Framework: pytorch
Device: cuda
Input Shape: (1, 3, 224, 224)
Layers Traced: 50
Total FLOPs: 4,130,000,000
Total Memory: 102.45 MB
Total Time: 45.23 ms

--------------------------------------------------------------------------------
Layer Name                                Type                 FLOPs       CRDT
--------------------------------------------------------------------------------
conv1                                     conv2d       118,000,000  0.850
bn1                                       batchnorm2d    3,161,600  0.600
relu                                      relu           3,161,600  0.950
...
--------------------------------------------------------------------------------
```

---

## Integration

### Production Framework Integration

The PyTorch tracer integrates with the production simulation framework:

```
PyTorch Tracer → Real Traces → Workload Simulator → Cache/CRDT Optimization
```

**Key Integration Points:**

1. **Trace Generation**
   ```python
   # Generate real traces
   tracer = PyTorchTracer("resnet50")
   trace = tracer.trace(input_data)
   TraceExporter.to_json(trace, "production/traces/resnet50.json")
   ```

2. **Trace Loading**
   ```python
   # Load in simulation
   from production.simulation import TraceLoader
   workload = TraceLoader.load("production/traces/resnet50.json")
   ```

3. **Cache Simulation**
   ```python
   # Simulate with real cache line accesses
   cache_sim = CacheSimulator(size_mb=4)
   results = cache_sim.simulate(workload)
   ```

4. **CRDT Optimization**
   ```python
   # Identify distribution opportunities
   high_crdt = [l for l in trace.layers if l.crdt_friendly_score >= 0.8]
   optimizer.create_distribution_plan(high_crdt)
   ```

**Full Guide:** [INTEGRATION.md](INTEGRATION.md)

---

## Supported Models

### Vision Models (torchvision)
- ResNet: 18, 34, 50, 101
- VGG: 16
- MobileNet: V2
- EfficientNet: B0

### Language Models (transformers)
- BERT: base, large
- GPT-2: base, medium
- DistilBERT

### Adding New Models

```python
# In PyTorchTracer._load_model()
elif model_name == "your-model":
    from transformers import YourModel
    model = YourModel.from_pretrained("your-model-name")
    return model.to(device)
```

---

## Output Formats

### JSON
**Use:** Human-readable, small traces
```bash
trace.json          # Limited cache lines (default)
trace_full.json     # All cache lines
```

### HDF5
**Use:** Large traces, research
```bash
trace.h5           # Compressed, efficient
```

### CSV
**Use:** Quick analysis, spreadsheets
```bash
trace.csv          # Summary statistics
```

---

## Testing

### Test Coverage

| Test Type | Description | File |
|-----------|-------------|------|
| **Unit Tests** | Component testing | [test_pytorch_tracer.py](test_pytorch_tracer.py) |
| **Integration Tests** | End-to-end workflows | [test_pytorch_tracer.py](test_pytorch_tracer.py#L400) |
| **Performance Tests** | Overhead and memory | [test_pytorch_tracer.py](test_pytorch_tracer.py#L450) |

### Running Tests

```bash
# Run all tests
pytest test_pytorch_tracer.py -v

# Run specific test
pytest test_pytorch_tracer.py::TestLayerAnalyzer::test_compute_flops_conv2d -v

# Run with coverage
pytest test_pytorch_tracer.py --cov=. --cov-report=html
```

### Test Fixtures
- `simple_model`: Conv2d + ReLU + Pooling
- `linear_model`: Linear + ReLU layers
- `temp_output_dir`: Isolated test outputs

---

## Performance

### Overhead

| Component | Overhead | Notes |
|-----------|----------|-------|
| Hook registration | ~1ms | One-time cost |
| Metric computation | ~5% | Per layer |
| Cache line analysis | ~2% | Limited to 10K elements |
| JSON export | ~100ms | After trace |
| **Total** | **~5-10%** | Acceptable for tracing |

### Memory Usage

| Model | VRAM Usage | Trace Size |
|-------|------------|------------|
| ResNet50 | ~1.2 GB | ~2 MB JSON |
| BERT-base | ~1.5 GB | ~3 MB JSON |
| GPT-2 | ~2.0 GB | ~4 MB JSON |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CUDA OOM | Use `device="cpu"` |
| Model download fails | Auto-fallback to dummy model |
| Import error | Install: `pip install -r requirements.txt` |
| Slow tracing | Normal overhead (~5-10%) |

### Getting Help

1. Check [README.md](README.md) for full documentation
2. See [QUICKSTART.md](QUICKSTART.md) for examples
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
4. Run tests: `pytest test_pytorch_tracer.py -v`

---

## File Structure

```
production/pytorch_integration/
├── pytorch_tracer.py      # Main tracer (800+ lines)
├── example_usage.py       # 6 comprehensive examples
├── test_pytorch_tracer.py # Full test suite
├── requirements.txt       # Dependencies
├── README.md             # Full documentation
├── QUICKSTART.md         # 5-minute guide
├── ARCHITECTURE.md       # System design
├── INTEGRATION.md        # Production integration
├── INDEX.md              # This file
└── traces/               # Output directory
    ├── *.json            # JSON traces
    ├── *.h5              # HDF5 traces
    └── *.csv             # CSV summaries
```

---

## Key Metrics

### Metrics Captured

| Metric | Description | Use Case |
|--------|-------------|----------|
| **FLOPs** | Floating point operations | Compute analysis |
| **Memory** | Read/write in MB | Bandwidth analysis |
| **Time** | Execution time (ms) | Performance profiling |
| **Cache Lines** | 64-byte accesses | Cache simulation |
| **CRDT Score** | Distributability (0-1) | Optimization |

### Layer Types

| Type | Count | Avg FLOPs | Avg CRDT |
|------|-------|-----------|----------|
| Conv2d | ~20 | 100M | 0.85 |
| Linear | ~10 | 50M | 0.70 |
| ReLU | ~15 | 5M | 0.95 |
| BatchNorm | ~5 | 3M | 0.60 |

---

## Best Practices

### 1. Trace Organization
- Group by model family (vision/, language/)
- Use descriptive filenames
- Maintain trace index

### 2. Version Control
- Tag with model version
- Include hardware config
- Record training data hash

### 3. Performance
- Use HDF5 for large traces
- Batch process multiple models
- Cache traces in memory

### 4. Validation
- Cross-check with profilers
- Verify FLOP calculations
- Validate cache line addresses

---

## Future Enhancements

### Planned Features
- [ ] Dynamic shape support
- [ ] Training loop tracing
- [ ] Multi-GPU tracing
- [ ] Real-time tracing API
- [ ] ONNX model support
- [ ] Hardware counter integration

### Contributions
Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit PR

---

## References

### External Resources
- [PyTorch Documentation](https://pytorch.org/docs/stable/)
- [Transformers Library](https://huggingface.co/docs/transformers/)
- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [CRDT Research](https://hal.inria.fr/hal-00955301/document)

### Internal Documents
- Production Simulation Framework
- Cache Simulator Documentation
- CRDT Optimization Guide

---

## Changelog

### Version 1.0.0 (2026-03-13)
- Initial release
- Support for ResNet, BERT, GPT-2
- JSON, HDF5, CSV export
- Comprehensive test suite
- Full documentation

---

## License

Part of the SuperInstance Papers project.
https://github.com/SuperInstance/SuperInstance-papers

---

**Last Updated:** 2026-03-13
**Version:** 1.0.0
**Maintainer:** SuperInstance Production Team
