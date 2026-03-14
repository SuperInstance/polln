# PyTorch Real Integration - Production Tracer

## Overview

This module provides **real PyTorch model tracing** for the production simulation framework. It captures actual execution traces from pre-trained models (ResNet, BERT, GPT-2) replacing synthetic traces with production data.

## Hardware Configuration

- **GPU:** NVIDIA RTX 4050 (6GB VRAM)
- **CUDA:** 13.1.1
- **PyTorch:** 2.5+
- **CuPy:** 14.0.1 (for GPU acceleration)

## Features

### 1. Real Model Tracing
- Loads actual pre-trained models from:
  - **torchvision:** ResNet18/34/50/101, VGG16, MobileNetV2, EfficientNet
  - **transformers:** BERT-base/large, GPT-2, DistilBERT
- Registers forward hooks on all layers
- Captures execution metrics at layer granularity

### 2. Comprehensive Metrics

For each layer, the tracer captures:
- **Layer type** (conv2d, linear, attention, etc.)
- **Input/output shapes**
- **Parameter count**
- **FLOPs** (floating point operations)
- **Memory accesses** (read/write in MB)
- **Compute time** (milliseconds)
- **Cache line accesses** (64-byte granularity)
- **CRDT-friendly score** (0-1, higher = more distributable)

### 3. Cache Line Analysis

Computes cache line accesses at 64-byte granularity:
```python
element_size = tensor.element_size()  # 4 bytes (float32) or 2 bytes (float16)
elements_per_line = 64 // element_size
cache_line = tensor.data_ptr() // 64
```

### 4. CRDT-Friendly Scoring

Layers are scored on their suitability for CRDT distribution:
- **High scores (>0.8):** Element-wise operations (ReLU, Dropout)
- **Medium scores (0.6-0.8):** Shared weight layers (Conv2D, Embedding)
- **Lower scores (<0.6):** Reduction operations (LayerNorm, Softmax)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For CUDA support (adjust CUDA version as needed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Usage

### Basic Tracing

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Create tracer
tracer = PyTorchTracer("resnet50", device="cuda")

# Create input data
input_data = torch.randn(1, 3, 224, 224).cuda()

# Trace inference
trace = tracer.trace(input_data)

# Print summary
TraceExporter.print_summary(trace)

# Export to JSON
TraceExporter.to_json(trace, "resnet50_trace.json")

# Export to HDF5 (for large datasets)
TraceExporter.to_hdf5(trace, "resnet50_trace.h5")
```

### Command Line

```bash
# Trace all default models
python pytorch_tracer.py

# Trace specific models (modify the script)
models_to_trace = ["resnet50", "bert-base", "gpt2"]
```

## Output Formats

### JSON Format
```json
{
  "model_name": "resnet50",
  "framework": "pytorch",
  "device": "cuda",
  "total_flops": 4130000000,
  "total_memory_mb": 102.4,
  "total_time_ms": 45.2,
  "layers": [
    {
      "layer_name": "conv1",
      "layer_type": "conv2d",
      "input_shape": [1, 3, 224, 224],
      "output_shape": [1, 64, 112, 112],
      "flops": 118000000,
      "crdt_friendly_score": 0.85,
      "cache_lines": [12345, 12346, ...]
    }
  ]
}
```

### HDF5 Format
Hierarchical data format for large datasets:
- Metadata stored as attributes
- Layer data organized in groups
- Cache line data compressed with gzip

### CSV Format
Summary statistics for quick analysis:
```csv
layer_name,layer_type,depth,parameters,flops,memory_read_mb,memory_write_mb,time_ms,cache_line_count,crdt_score
conv1,conv2d,1,9408,118000000,0.576,1.126,2.345,1024,0.850
```

## Layer Type Support

### Fully Supported
- **Convolutional:** Conv2d
- **Linear:** Linear (Dense/Fully Connected)
- **Activations:** ReLU, ReLU6, LeakyReLU, ELU, GELU, Sigmoid, Tanh, Softmax
- **Normalization:** BatchNorm1d, BatchNorm2d, LayerNorm
- **Pooling:** MaxPool2d, AvgPool2d, AdaptiveAvgPool2d
- **Other:** Dropout, Embedding, Flatten

### Partially Supported
- **Attention:** MultiheadAttention (estimated FLOPs)
- **Transformers:** BERT/GPT blocks (module-level tracing)

## CRDT-Friendly Scoring

The CRDT-friendly score indicates how well a layer's operations can be distributed:

| Score Range | Interpretation | Examples |
|-------------|----------------|----------|
| 0.9-1.0 | Excellent | Element-wise ops, reshape |
| 0.8-0.9 | Very Good | Convolution, Embedding |
| 0.6-0.8 | Good | Linear, Pooling |
| 0.4-0.6 | Moderate | Attention, BatchNorm |
| 0.0-0.4 | Challenging | Reduction operations |

## Performance Considerations

### Memory Usage
- Cache line tracking is limited to 10,000 elements per tensor
- Use `include_all_cache_lines=False` for JSON export to reduce file size
- HDF5 format uses compression for large datasets

### GPU Memory
- RTX 4050 has 6GB VRAM
- Large models (BERT-large) may require:
  - Gradient checkpointing
  - Reduced batch sizes
  - CPU fallback

## Tracing vs. Synthetic Data

| Aspect | Synthetic Traces | Real Tracing |
|--------|------------------|--------------|
| Accuracy | Approximate | Exact |
| Overhead | None | ~5-10% slowdown |
| Setup | Simple | Requires models |
| Use Case | Prototyping | Production |

## Troubleshooting

### CUDA Out of Memory
```python
# Use CPU fallback
tracer = PyTorchTracer("bert-base", device="cpu")
```

### Model Download Issues
```python
# Models fall back to dummy versions automatically
# Or pre-download:
from transformers import BertModel
BertModel.from_pretrained("bert-base-uncased")
```

### Missing Dependencies
```bash
# Install transformers for BERT/GPT
pip install transformers>=4.30.0

# Install h5py for HDF5 export
pip install h5py>=3.8.0
```

## File Structure

```
production/pytorch_integration/
├── pytorch_tracer.py      # Main tracer implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── traces/               # Output directory
    ├── resnet50_*.json   # JSON traces
    ├── resnet50_*.h5     # HDF5 traces
    ├── bert-base_*.json  # BERT traces
    └── gpt2_*.json       # GPT-2 traces
```

## Integration with Production Framework

The trace output integrates with:
- **Workload Traces:** Real execution patterns
- **Cache Simulation:** Actual cache line accesses
- **CRDT Optimization:** Layer-friendly distribution scores
- **Performance Modeling:** FLOPs and memory metrics

## Future Extensions

- [ ] Multi-GPU tracing
- [ ] Dynamic shape support
- [ ] Profiler integration (torch.profiler)
- [ ] ONNX model export
- [ ] Real-time tracing during training

## References

- PyTorch: https://pytorch.org/docs/stable/
- Transformers: https://huggingface.co/docs/transformers/
- CUDA: https://developer.nvidia.com/cuda-toolkit

## License

Part of the SuperInstance Papers project.
https://github.com/SuperInstance/SuperInstance-papers
