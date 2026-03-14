# PyTorch Real Integration - API Reference

Complete API reference for the PyTorch Real Integration system.

## Table of Contents

- [PyTorchTracer](#pytorchtracer)
- [LayerAnalyzer](#layeranalyzer)
- [CacheLineAnalyzer](#cachelineanalyzer)
- [CRDTScorer](#crdtscorer)
- [TraceExporter](#traceexporter)
- [Data Structures](#data-structures)

---

## PyTorchTracer

Main tracing engine for capturing real model execution.

### Class Definition

```python
class PyTorchTracer:
    """Capture real execution traces from PyTorch models."""

    AVAILABLE_MODELS = {
        "resnet18": "torchvision.models.resnet18",
        "resnet34": "torchvision.models.resnet34",
        "resnet50": "torchvision.models.resnet50",
        "resnet101": "torchvision.models.resnet101",
        "vgg16": "torchvision.models.vgg16",
        "mobilenet_v2": "torchvision.models.mobilenet_v2",
        "efficientnet_b0": "torchvision.models.efficientnet_b0",
        "bert-base": "transformers.BertModel",
        "bert-large": "transformers.BertModel",
        "gpt2": "transformers.GPT2Model",
        "gpt2-medium": "transformers.GPT2Model",
        "distilbert": "transformers.DistilBertModel",
    }
```

### Constructor

```python
def __init__(self, model_name: str, device: str = "cuda"):
    """
    Initialize PyTorch tracer.

    Args:
        model_name: Name of pre-trained model to trace
        device: Device to run on ("cuda" or "cpu")

    Raises:
        ValueError: If model_name is not recognized
        RuntimeError: If CUDA requested but not available
    """
```

**Example:**
```python
# Trace ResNet50 on GPU
tracer = PyTorchTracer("resnet50", device="cuda")

# Trace BERT on CPU
tracer = PyTorchTracer("bert-base", device="cpu")
```

### Methods

#### trace()

```python
def trace(self, input_data: Union[torch.Tensor, Dict[str, torch.Tensor]]) -> ModelTrace:
    """
    Trace model inference.

    Args:
        input_data: Input tensor or dict of tensors for model

    Returns:
        Complete ModelTrace with all layer data

    Raises:
        RuntimeError: If model execution fails
    """
```

**Example:**
```python
# Vision model
tracer = PyTorchTracer("resnet50", device="cuda")
input_data = torch.randn(1, 3, 224, 224).cuda()
trace = tracer.trace(input_data)

# Language model
tracer = PyTorchTracer("bert-base", device="cuda")
input_data = {
    "input_ids": torch.randint(0, 30000, (1, 128)).cuda(),
    "attention_mask": torch.ones(1, 128).cuda()
}
trace = tracer.trace(input_data)
```

---

## LayerAnalyzer

Analyzes layer characteristics and computes metrics.

### Class Definition

```python
class LayerAnalyzer:
    """Analyze layer characteristics and compute metrics."""

    LAYER_TYPE_MAP = {
        nn.Conv2d: "conv2d",
        nn.Linear: "linear",
        nn.ReLU: "relu",
        # ... (see full list in source)
    }
```

### Static Methods

#### get_layer_type()

```python
@staticmethod
def get_layer_type(layer: nn.Module) -> str:
    """
    Get layer type string.

    Args:
        layer: PyTorch layer module

    Returns:
        String identifier for layer type (e.g., "conv2d", "linear")
    """
```

**Example:**
```python
layer = nn.Conv2d(3, 64, 3)
layer_type = LayerAnalyzer.get_layer_type(layer)
print(layer_type)  # "conv2d"
```

#### compute_flops()

```python
@staticmethod
def compute_flops(layer: nn.Module,
                  input_shape: Tuple[int, ...],
                  output_shape: Tuple[int, ...]) -> int:
    """
    Compute FLOPs for a layer.

    Args:
        layer: PyTorch layer module
        input_shape: Input tensor shape
        output_shape: Output tensor shape

    Returns:
        Number of floating point operations
    """
```

**Example:**
```python
layer = nn.Conv2d(3, 64, 3)
input_shape = (1, 3, 32, 32)
output_shape = (1, 64, 32, 32)
flops = LayerAnalyzer.compute_flops(layer, input_shape, output_shape)
print(f"FLOPs: {flops:,}")
```

#### FLOP Computation Methods

```python
@staticmethod
def _conv2d_flops(layer: nn.Conv2d,
                  input_shape: Tuple[int, ...],
                  output_shape: Tuple[int, ...]) -> int:
    """
    Compute FLOPs for Conv2D layer.

    Formula: batch * out_channels * H * W * (kernel_h * kernel_w * in_channels)
    """

@staticmethod
def _linear_flops(layer: nn.Linear,
                  input_shape: Tuple[int, ...],
                  output_shape: Tuple[int, ...]) -> int:
    """
    Compute FLOPs for Linear layer.

    Formula: batch * in_features * out_features
    """

@staticmethod
def _attention_flops(layer: nn.MultiheadAttention,
                     input_shape: Tuple[int, ...]) -> int:
    """
    Compute FLOPs for MultiheadAttention layer.

    Formula: 3 * batch * seq * embed^2 + batch * heads * seq^2 * head_dim
    """
```

---

## CacheLineAnalyzer

Analyzes cache line access patterns.

### Class Definition

```python
class CacheLineAnalyzer:
    """Analyze cache line access patterns."""

    CACHE_LINE_SIZE = 64  # bytes
```

### Static Methods

#### compute_cache_lines()

```python
@staticmethod
def compute_cache_lines(tensor: torch.Tensor) -> List[int]:
    """
    Compute which cache lines are accessed by a tensor.

    Args:
        tensor: PyTorch tensor to analyze

    Returns:
        List of unique cache line addresses
    """
```

**Example:**
```python
tensor = torch.randn(1, 3, 224, 224)
cache_lines = CacheLineAnalyzer.compute_cache_lines(tensor)
print(f"Cache lines accessed: {len(cache_lines)}")
```

#### analyze_tensor_memory()

```python
@staticmethod
def analyze_tensor_memory(tensor: torch.Tensor,
                          layer_name: str,
                          access_type: str = "read") -> List[CacheLineAccess]:
    """
    Analyze detailed memory access patterns.

    Args:
        tensor: PyTorch tensor to analyze
        layer_name: Name of the layer accessing the tensor
        access_type: Type of access ("read", "write", "read_write")

    Returns:
        List of CacheLineAccess objects
    """
```

**Example:**
```python
tensor = torch.randn(1, 512)
accesses = CacheLineAnalyzer.analyze_tensor_memory(
    tensor,
    layer_name="linear1",
    access_type="read_write"
)
for access in accesses[:10]:
    print(f"Cache line: {access.cache_line_addr}, Type: {access.access_type}")
```

---

## CRDTScorer

Computes CRDT-friendliness scores for layers.

### Class Definition

```python
class CRDTScorer:
    """Compute CRDT-friendliness scores for layers."""

    BASE_SCORES = {
        "conv2d": 0.85,
        "linear": 0.70,
        "relu": 0.95,
        # ... (see full list in source)
    }
```

### Static Methods

#### compute_score()

```python
@staticmethod
def compute_score(layer: nn.Module,
                  layer_type: str,
                  input_shape: Tuple[int, ...],
                  output_shape: Tuple[int, ...]) -> float:
    """
    Compute CRDT-friendly score for a layer.

    Args:
        layer: PyTorch layer module
        layer_type: String identifier for layer type
        input_shape: Input tensor shape
        output_shape: Output tensor shape

    Returns:
        Score between 0.0 and 1.0
    """
```

**Example:**
```python
layer = nn.ReLU()
score = CRDTScorer.compute_score(layer, "relu", (100,), (100,))
print(f"CRDT score: {score:.3f}")  # 0.950
```

---

## TraceExporter

Exports traces in various formats.

### Static Methods

#### to_json()

```python
@staticmethod
def to_json(trace: ModelTrace,
             filepath: str,
             include_all_cache_lines: bool = False):
    """
    Export trace to JSON.

    Args:
        trace: ModelTrace to export
        filepath: Output file path
        include_all_cache_lines: Whether to include all cache line data

    Example:
        TraceExporter.to_json(trace, "resnet50.json")
        TraceExporter.to_json(trace, "resnet50_full.json", include_all_cache_lines=True)
    """
```

#### to_hdf5()

```python
@staticmethod
def to_hdf5(trace: ModelTrace, filepath: str):
    """
    Export trace to HDF5 for large datasets.

    Args:
        trace: ModelTrace to export
        filepath: Output file path

    Requires:
        h5py

    Example:
        TraceExporter.to_hdf5(trace, "resnet50.h5")
    """
```

#### to_csv()

```python
@staticmethod
def to_csv(trace: ModelTrace, filepath: str):
    """
    Export trace summary to CSV.

    Args:
        trace: ModelTrace to export
        filepath: Output file path

    Example:
        TraceExporter.to_csv(trace, "resnet50.csv")
    """
```

#### print_summary()

```python
@staticmethod
def print_summary(trace: ModelTrace):
    """
    Print trace summary to console.

    Args:
        trace: ModelTrace to print

    Example:
        TraceExporter.print_summary(trace)
    """
```

**Output Example:**
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
...
```

---

## Data Structures

### LayerTrace

```python
@dataclass
class LayerTrace:
    """Trace data for a single layer."""

    layer_name: str                    # Name of the layer
    layer_type: str                    # Type identifier
    input_shape: Tuple[int, ...]       # Input tensor shape
    output_shape: Tuple[int, ...]      # Output tensor shape
    parameters: int                    # Number of parameters
    flops: int                         # Floating point operations
    memory_reads_mb: float             # Memory read in MB
    memory_writes_mb: float            # Memory written in MB
    compute_time_ms: float             # Execution time in ms
    cache_line_accesses: List[int]     # Cache line addresses
    crdt_friendly_score: float         # CRDT score (0-1)
    layer_depth: int                   # Depth in model hierarchy
    parent_name: str                   # Parent module name
```

### ModelTrace

```python
@dataclass
class ModelTrace:
    """Complete trace of model inference."""

    model_name: str                    # Model identifier
    framework: str                     # "pytorch" or "tensorflow"
    layers: List[LayerTrace]           # Layer traces
    total_flops: int                   # Total FLOPs
    total_memory_mb: float             # Total memory in MB
    total_time_ms: float               # Total execution time
    capture_timestamp: str             # Capture timestamp
    device: str                        # Device used
    input_shape: Tuple[int, ...]       # Input shape

    def add_layer(self, layer: LayerTrace) -> None:
        """Add a layer trace and update totals."""

    def summary(self) -> str:
        """Generate summary string."""
```

### CacheLineAccess

```python
@dataclass
class CacheLineAccess:
    """Detailed cache line access information."""

    cache_line_addr: int               # Cache line address
    access_type: str                   # "read", "write", "read_write"
    timestamp_us: float                # Timestamp in microseconds
    layer_name: str                    # Layer accessing the line
    tensor_size_bytes: int             # Size of tensor
```

---

## Usage Patterns

### Basic Tracing

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Create tracer
tracer = PyTorchTracer("resnet50", device="cuda")

# Trace inference
input_data = torch.randn(1, 3, 224, 224).cuda()
trace = tracer.trace(input_data)

# Export
TraceExporter.to_json(trace, "resnet50.json")
```

### Batch Processing

```python
models = ["resnet50", "bert-base", "gpt2"]

for model_name in models:
    tracer = PyTorchTracer(model_name, device="cuda")
    input_data = create_input_data(model_name, "cuda")
    trace = tracer.trace(input_data)
    TraceExporter.to_json(trace, f"traces/{model_name}.json")
```

### Custom Analysis

```python
# Trace model
tracer = PyTorchTracer("resnet50", device="cuda")
trace = tracer.trace(torch.randn(1, 3, 224, 224).cuda())

# Analyze CRDT scores
high_crdt = [l for l in trace.layers if l.crdt_friendly_score >= 0.8]
print(f"High-CRDT layers: {len(high_crdt)}/{len(trace.layers)}")

# Analyze FLOPs
total_flops = sum(l.flops for l in trace.layers)
print(f"Total FLOPs: {total_flops:,}")

# Find bottlenecks
bottlenecks = sorted(trace.layers, key=lambda l: l.compute_time_ms, reverse=True)
for layer in bottlenecks[:5]:
    print(f"{layer.layer_name}: {layer.compute_time_ms:.2f}ms")
```

---

## Error Handling

### Common Exceptions

```python
# Model not found
try:
    tracer = PyTorchTracer("unknown_model")
except ValueError as e:
    print(f"Unknown model: {e}")

# CUDA not available
try:
    tracer = PyTorchTracer("resnet50", device="cuda")
except RuntimeError as e:
    print("CUDA not available, using CPU")
    tracer = PyTorchTracer("resnet50", device="cpu")

# Export failure
try:
    TraceExporter.to_json(trace, "/invalid/path/trace.json")
except IOError as e:
    print(f"Export failed: {e}")
```

---

## Type Hints

All functions use Python type hints for better IDE support:

```python
from typing import Dict, List, Tuple, Optional, Union, Any
import torch
from torch import nn

def trace(self,
          input_data: Union[torch.Tensor, Dict[str, torch.Tensor]]
         ) -> ModelTrace:
    ...

@staticmethod
def compute_flops(layer: nn.Module,
                  input_shape: Tuple[int, ...],
                  output_shape: Tuple[int, ...]
                 ) -> int:
    ...
```

---

## Constants

```python
# CacheLineAnalyzer
CACHE_LINE_SIZE = 64  # bytes

# CRDTScorer
BASE_SCORES = {
    "conv2d": 0.85,
    "linear": 0.70,
    "relu": 0.95,
    # ... (see source for full list)
}

# PyTorchTracer
AVAILABLE_MODELS = {
    "resnet18": "torchvision.models.resnet18",
    # ... (see source for full list)
}
```

---

## Performance Considerations

### Memory Usage

- Cache line tracking limited to 10,000 elements per tensor
- Hooks capture metadata only (not tensor data)
- Export after trace completion

### Overhead

- Hook registration: ~1ms (one-time)
- Metric computation: ~5% per layer
- Cache line analysis: ~2% per layer
- **Total: ~5-10%** overhead

### Optimization Tips

1. **Use HDF5 for large traces**
   ```python
   TraceExporter.to_hdf5(trace, "large_model.h5")
   ```

2. **Limit cache lines in JSON**
   ```python
   TraceExporter.to_json(trace, "output.json")  # First 100 only
   ```

3. **Batch process multiple models**
   ```python
   for model in models:
       trace_and_export(model)
   ```

---

## See Also

- [README.md](README.md) - User guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [INTEGRATION.md](INTEGRATION.md) - Production integration
- [example_usage.py](example_usage.py) - Code examples

---

**Version:** 1.0.0
**Last Updated:** 2026-03-13
