# PyTorch Real Integration - Quick Start Guide

Get up and running with PyTorch model tracing in 5 minutes.

## Installation

### 1. Install Dependencies

```bash
# Navigate to the integration directory
cd C:/Users/casey/polln/production/pytorch_integration

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Check PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Expected output:
# PyTorch: 2.5.0
# CUDA: True
```

## Basic Usage

### Quick Example (3 lines)

```python
from pytorch_tracer import PyTorchTracer, TraceExporter

# 1. Create tracer
tracer = PyTorchTracer("resnet50", device="cuda")

# 2. Trace model
trace = tracer.trace(torch.randn(1, 3, 224, 224).cuda())

# 3. Export results
TraceExporter.to_json(trace, "resnet50_trace.json")
```

## Common Workflows

### 1. Trace Image Classification Model

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Create tracer
tracer = PyTorchTracer("resnet50", device="cuda")

# Create image input (batch=1, channels=3, height=224, width=224)
input_data = torch.randn(1, 3, 224, 224).cuda()

# Trace inference
trace = tracer.trace(input_data)

# Print summary
TraceExporter.print_summary(trace)

# Export trace
TraceExporter.to_json(trace, "traces/resnet50.json")
```

### 2. Trace BERT Model

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Create tracer
tracer = PyTorchTracer("bert-base", device="cuda")

# Create BERT input
input_data = {
    "input_ids": torch.randint(0, 30000, (1, 128)).cuda(),
    "attention_mask": torch.ones(1, 128).cuda()
}

# Trace inference
trace = tracer.trace(input_data)

# Export trace
TraceExporter.to_json(trace, "traces/bert_base.json")
```

### 3. Trace GPT-2 Model

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Create tracer
tracer = PyTorchTracer("gpt2", device="cuda")

# Create GPT-2 input (token IDs)
input_data = torch.randint(0, 50257, (1, 128)).cuda()

# Trace inference
trace = tracer.trace(input_data)

# Export trace
TraceExporter.to_json(trace, "traces/gpt2.json")
```

### 4. Batch Tracing Multiple Models

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch
from pathlib import Path

models = ["resnet50", "bert-base", "gpt2"]
output_dir = Path("traces")
output_dir.mkdir(exist_ok=True)

for model_name in models:
    print(f"Tracing {model_name}...")
    tracer = PyTorchTracer(model_name, device="cuda")

    # Create appropriate input
    if "resnet" in model_name:
        input_data = torch.randn(1, 3, 224, 224).cuda()
    elif "bert" in model_name:
        input_data = {
            "input_ids": torch.randint(0, 30000, (1, 128)).cuda(),
            "attention_mask": torch.ones(1, 128).cuda()
        }
    else:  # gpt2
        input_data = torch.randint(0, 50257, (1, 128)).cuda()

    # Trace and export
    trace = tracer.trace(input_data)
    TraceExporter.to_json(trace, output_dir / f"{model_name}.json")
    print(f"Saved {model_name}")
```

## Understanding the Output

### JSON Trace Structure

```json
{
  "model_name": "resnet50",
  "framework": "pytorch",
  "device": "cuda",
  "total_flops": 4130000000,
  "total_memory_mb": 102.4,
  "total_time_ms": 45.2,
  "num_layers": 50,
  "layers": [
    {
      "layer_name": "conv1",
      "layer_type": "conv2d",
      "layer_depth": 1,
      "input_shape": [1, 3, 224, 224],
      "output_shape": [1, 64, 112, 112],
      "parameters": 9408,
      "flops": 118000000,
      "memory_reads_mb": 0.576,
      "memory_writes_mb": 1.126,
      "compute_time_ms": 2.345,
      "cache_line_count": 1024,
      "cache_lines": [12345, 12346, ...],
      "crdt_friendly_score": 0.85
    }
  ]
}
```

### Key Metrics Explained

| Metric | Description | Use Case |
|--------|-------------|----------|
| `flops` | Floating point operations | Compute bottleneck analysis |
| `memory_reads_mb` | Input memory read | Memory bandwidth analysis |
| `memory_writes_mb` | Output memory written | Memory bandwidth analysis |
| `compute_time_ms` | Layer execution time | Performance profiling |
| `cache_line_count` | Number of cache lines accessed | Cache simulation |
| `crdt_friendly_score` | Distributability score (0-1) | CRDT optimization |

### CRDT-Friendly Scores

- **0.9-1.0:** Excellent for distribution (ReLU, element-wise ops)
- **0.8-0.9:** Very good (Conv2D, Embedding)
- **0.6-0.8:** Good (Linear, Pooling)
- **0.4-0.6:** Moderate (Attention, BatchNorm)
- **0.0-0.4:** Challenging (reduction operations)

## Troubleshooting

### Problem: CUDA Out of Memory

**Solution:** Use CPU fallback
```python
tracer = PyTorchTracer("bert-base", device="cpu")
```

### Problem: Model Download Fails

**Solution:** The tracer automatically falls back to dummy models. Or pre-download:
```python
from transformers import BertModel
BertModel.from_pretrained("bert-base-uncased")
```

### Problem: Too Many Cache Lines

**Solution:** Limit cache lines in export
```python
# Default: first 100 cache lines
TraceExporter.to_json(trace, "output.json")

# All cache lines (larger file)
TraceExporter.to_json(trace, "output_full.json", include_all_cache_lines=True)
```

### Problem: Slow Tracing

**Solution:** This is normal. Tracing adds ~5-10% overhead due to hook execution.

## Available Models

### Vision Models (torchvision)
- `resnet18`, `resnet34`, `resnet50`, `resnet101`
- `vgg16`
- `mobilenet_v2`
- `efficientnet_b0`

### Language Models (transformers)
- `bert-base`, `bert-large`
- `gpt2`, `gpt2-medium`
- `distilbert`

## Next Steps

1. **Run Examples:** See `example_usage.py` for detailed examples
2. **Read Documentation:** Check `README.md` for full documentation
3. **Review Architecture:** See `ARCHITECTURE.md` for design details
4. **Run Tests:** Execute `test_pytorch_tracer.py` to verify installation

## Command Line Usage

```bash
# Trace all default models
python pytorch_tracer.py

# Run examples
python example_usage.py

# Run tests
pytest test_pytorch_tracer.py -v
```

## Tips for Production Use

1. **Use HDF5 for large traces** (better compression)
   ```python
   TraceExporter.to_hdf5(trace, "large_model.h5")
   ```

2. **Export multiple formats** for different use cases
   ```python
   TraceExporter.to_json(trace, "model.json")  # Human-readable
   TraceExporter.to_csv(trace, "model.csv")    # Quick analysis
   TraceExporter.to_hdf5(trace, "model.h5")    # Research
   ```

3. **Analyze CRDT scores** to find distribution opportunities
   ```python
   high_crdt_layers = [l for l in trace.layers if l.crdt_friendly_score >= 0.8]
   print(f"Distributable layers: {len(high_crdt_layers)}/{len(trace.layers)}")
   ```

4. **Profile bottlenecks** using compute time
   ```python
   bottlenecks = sorted(trace.layers, key=lambda l: l.compute_time_ms, reverse=True)
   for layer in bottlenecks[:5]:
       print(f"{layer.layer_name}: {layer.compute_time_ms:.2f}ms")
   ```

## Getting Help

- **Issues:** Check GitHub issues or create new one
- **Documentation:** See `README.md` and `ARCHITECTURE.md`
- **Examples:** Run `python example_usage.py`

## Example Output

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
Capture Time: 20260313-120000

--------------------------------------------------------------------------------
Layer Name                                Type                 FLOPs       CRDT
--------------------------------------------------------------------------------
conv1                                     conv2d       118,000,000  0.850
bn1                                       batchnorm2d    3,161,600  0.600
relu                                      relu           3,161,600  0.950
maxpool                                   maxpool2d      1,179,648  0.800
layer1.0.conv1                            conv2d        18,432,000  0.850
...
--------------------------------------------------------------------------------
Average CRDT Score: 0.742
================================================================================
```

Happy tracing!
