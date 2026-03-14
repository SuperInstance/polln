# Production Framework Integration Guide

## Overview

This guide explains how to integrate **real PyTorch traces** into the production simulation framework, replacing synthetic workload traces with actual model execution data.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Simulation Framework              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │  PyTorch Tracer  │──────│  Trace Database  │                │
│  │  (Real Traces)   │      │  (JSON/HDF5)     │                │
│  └──────────────────┘      └──────────────────┘                │
│                                      │                           │
│                                      ▼                           │
│  ┌──────────────────────────────────────────────────┐           │
│  │           Workload Trace Processor                │           │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │           │
│  │  │   Cache    │  │    CRDT    │  │  Scheduling│ │           │
│  │  │ Simulator  │  │ Optimizer  │  │   Engine   │ │           │
│  │  └────────────┘  └────────────┘  └────────────┘ │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Workflow

### 1. Generate Real Traces

```python
from pytorch_tracer import PyTorchTracer, TraceExporter
import torch

# Trace production model
tracer = PyTorchTracer("resnet50", device="cuda")
input_data = torch.randn(1, 3, 224, 224).cuda()
trace = tracer.trace(input_data)

# Export to production trace database
TraceExporter.to_json(trace, "production/traces/resnet50.json")
```

### 2. Load Traces in Simulation

```python
from production.simulation import WorkloadTrace, TraceLoader

# Load real trace
trace_loader = TraceLoader("production/traces")
workload = trace_loader.load("resnet50")

# Use in simulation
from production.cache import CacheSimulator
cache_sim = CacheSimulator(size_mb=8)

results = cache_sim.simulate(workload)
print(f"Cache hit rate: {results.hit_rate:.2%}")
```

## Data Mapping

### PyTorch Trace → Workload Trace

```python
class TraceConverter:
    """Convert PyTorch traces to workload traces."""

    @staticmethod
    def to_workload_trace(pytorch_trace: ModelTrace) -> WorkloadTrace:
        """Convert PyTorch ModelTrace to WorkloadTrace."""

        operations = []

        for layer in pytorch_trace.layers:
            # Convert cache line accesses to memory operations
            for cache_line in layer.cache_line_accesses:
                op = MemoryOperation(
                    address=cache_line,
                    size_bytes=64,
                    operation_type="read_write",
                    timestamp_us=layer.compute_time_ms * 1000,
                    layer_name=layer.layer_name,
                    crdt_friendly=layer.crdt_friendly_score >= 0.8
                )
                operations.append(op)

        return WorkloadTrace(
            name=pytorch_trace.model_name,
            operations=operations,
            total_flops=pytorch_trace.total_flops,
            total_memory_mb=pytorch_trace.total_memory_mb,
            metadata={
                "framework": pytorch_trace.framework,
                "device": pytorch_trace.device,
                "capture_timestamp": pytorch_trace.capture_timestamp
            }
        )
```

### Layer Type Mapping

| PyTorch Layer | Simulation Operation | Properties |
|---------------|---------------------|------------|
| Conv2d | Compute + Memory Read/Write | High spatial locality |
| Linear | Compute + Memory Read/Write | Matrix multiplication |
| ReLU | Compute (element-wise) | High CRDT score |
| LayerNorm | Compute + Reduction | Lower CRDT score |
| Attention | Compute + Memory | Complex pattern |

## Cache Simulation Integration

### Real Cache Line Accesses

```python
from production.cache import CacheSimulator

# Load PyTorch trace with cache line data
with open("production/traces/resnet50.json", 'r') as f:
    trace_data = json.load(f)

# Simulate with real cache line accesses
cache_sim = CacheSimulator(
    size_mb=4,
    line_size=64,  # Match PyTorch tracer
    associativity=4
)

# Process each layer's cache accesses
for layer in trace_data["layers"]:
    for cache_line in layer["cache_lines"]:
        cache_sim.access(cache_line)

print(f"Hit rate: {cache_sim.get_hit_rate():.2%}")
print(f"Total accesses: {cache_sim.get_total_accesses()}")
```

### Per-Layer Cache Analysis

```python
def analyze_layer_cache_behavior(trace_data: dict):
    """Analyze cache behavior per layer."""

    cache_stats = {}

    for layer in trace_data["layers"]:
        layer_name = layer["layer_name"]
        cache_lines = layer["cache_lines"]

        # Unique cache lines
        unique_lines = set(cache_lines)

        # Spatial locality (reuse)
        reuse_factor = len(cache_lines) / len(unique_lines) if unique_lines else 0

        cache_stats[layer_name] = {
            "total_accesses": len(cache_lines),
            "unique_cache_lines": len(unique_lines),
            "reuse_factor": reuse_factor,
            "spatial_locality": reuse_factor > 1.5
        }

    return cache_stats
```

## CRDT Optimization Integration

### Identify Distribution Opportunities

```python
from production.crdt import CRDTOptimizer

def find_crdt_optimizations(trace_data: dict):
    """Find layers suitable for CRDT distribution."""

    optimizer = CRDTOptimizer()

    # High-CRDT layers (easy wins)
    high_crdt = [
        layer for layer in trace_data["layers"]
        if layer["crdt_friendly_score"] >= 0.8
    ]

    # Medium-CRDT layers (requires analysis)
    medium_crdt = [
        layer for layer in trace_data["layers"]
        if 0.6 <= layer["crdt_friendly_score"] < 0.8
    ]

    # Generate distribution plan
    plan = optimizer.create_distribution_plan(
        distributable=high_crdt + medium_crdt,
        constraints={"max_replicas": 4}
    )

    return plan
```

### FLOP Distribution Analysis

```python
def analyze_flop_distribution(trace_data: dict):
    """Analyze FLOP distribution by CRDT score."""

    # Group FLOPs by CRDT score ranges
    ranges = {
        "high": [0, 0],      # [count, total_flops]
        "medium": [0, 0],
        "low": [0, 0]
    }

    for layer in trace_data["layers"]:
        score = layer["crdt_friendly_score"]
        flops = layer["flops"]

        if score >= 0.8:
            ranges["high"][0] += 1
            ranges["high"][1] += flops
        elif score >= 0.6:
            ranges["medium"][0] += 1
            ranges["medium"][1] += flops
        else:
            ranges["low"][0] += 1
            ranges["low"][1] += flops

    return ranges
```

## Performance Prediction Integration

### Use Real Traces for Prediction

```python
from production.prediction import PerformancePredictor

def predict_performance(model_name: str, hardware_config: dict):
    """Predict performance using real traces."""

    # Load real trace
    with open(f"production/traces/{model_name}.json", 'r') as f:
        trace_data = json.load(f)

    # Initialize predictor
    predictor = PerformancePredictor(hardware_config)

    # Predict using real FLOPs and memory
    predictions = predictor.predict({
        "total_flops": trace_data["total_flops"],
        "total_memory_mb": trace_data["total_memory_mb"],
        "layer_count": trace_data["num_layers"],
        "avg_crdt_score": np.mean([
            l["crdt_friendly_score"] for l in trace_data["layers"]
        ])
    })

    return predictions
```

## Batch Processing Pipeline

### Process Multiple Models

```python
from pathlib import Path
import json

def batch_trace_models(models: list, output_dir: Path):
    """Trace multiple models and build trace database."""

    output_dir.mkdir(parents=True, exist_ok=True)

    traces = {}

    for model_name in models:
        print(f"Tracing {model_name}...")

        # Trace model
        tracer = PyTorchTracer(model_name, device="cuda")
        input_data = create_input_data(model_name, "cuda")
        trace = tracer.trace(input_data)

        # Export trace
        trace_file = output_dir / f"{model_name}.json"
        TraceExporter.to_json(trace, str(trace_file))

        # Store metadata
        traces[model_name] = {
            "file": str(trace_file),
            "flops": trace.total_flops,
            "memory_mb": trace.total_memory_mb,
            "time_ms": trace.total_time_ms,
            "num_layers": len(trace.layers)
        }

    # Save trace database index
    with open(output_dir / "trace_index.json", 'w') as f:
        json.dump(traces, f, indent=2)

    return traces
```

## Real-Time Integration

### On-Demand Tracing Service

```python
from flask import Flask, request, jsonify
import tempfile

app = Flask(__name__)

@app.route('/trace', methods=['POST'])
def trace_model():
    """Trace model on demand."""

    data = request.json
    model_name = data["model_name"]
    input_shape = data["input_shape"]

    # Trace model
    tracer = PyTorchTracer(model_name, device="cuda")
    input_data = create_input_from_shape(input_shape).cuda()
    trace = tracer.trace(input_data)

    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        TraceExporter.to_json(trace, f.name)
        trace_file = f.name

    return jsonify({
        "status": "success",
        "trace_file": trace_file,
        "flops": trace.total_flops,
        "memory_mb": trace.total_memory_mb
    })

if __name__ == '__main__':
    app.run(port=5000)
```

## Validation and Verification

### Compare Real vs. Synthetic

```python
def validate_synthetic_traces(real_trace: dict, synthetic_trace: dict):
    """Validate synthetic traces against real ones."""

    validation_results = {
        "flops_error": 0.0,
        "memory_error": 0.0,
        "layer_count_match": False,
        "cache_pattern_similarity": 0.0
    }

    # Compare FLOPs
    real_flops = real_trace["total_flops"]
    synth_flops = synthetic_trace["total_flops"]
    validation_results["flops_error"] = abs(real_flops - synth_flops) / real_flops

    # Compare memory
    real_mem = real_trace["total_memory_mb"]
    synth_mem = synthetic_trace["total_memory_mb"]
    validation_results["memory_error"] = abs(real_mem - synth_mem) / real_mem

    # Compare layer counts
    validation_results["layer_count_match"] = (
        real_trace["num_layers"] == synthetic_trace["num_layers"]
    )

    # Compare cache patterns (simplified)
    real_patterns = extract_cache_patterns(real_trace)
    synth_patterns = extract_cache_patterns(synthetic_trace)
    validation_results["cache_pattern_similarity"] = (
        compute_pattern_similarity(real_patterns, synth_patterns)
    )

    return validation_results
```

## Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile for PyTorch Tracer
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install torch torchvision transformers h5py

COPY pytorch_tracer.py /app/
COPY production/ /app/production/

WORKDIR /app

ENTRYPOINT ["python3", "pytorch_tracer.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pytorch-tracer
spec:
  template:
    spec:
      containers:
      - name: tracer
        image: pytorch-tracer:latest
        resources:
          limits:
            nvidia.com/gpu: 1
        command: ["python3", "pytorch_tracer.py"]
        volumeMounts:
        - name: trace-storage
          mountPath: /app/traces
      volumes:
      - name: trace-storage
        persistentVolumeClaim:
          claimName: trace-pvc
      restartPolicy: Never
```

## Monitoring and Logging

### Trace Metrics

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pytorch_tracer")

def trace_with_monitoring(model_name: str):
    """Trace model with monitoring."""

    logger.info(f"Starting trace for {model_name}")

    try:
        tracer = PyTorchTracer(model_name, device="cuda")
        trace = tracer.trace(input_data)

        # Log metrics
        logger.info(f"Trace completed: {len(trace.layers)} layers")
        logger.info(f"Total FLOPs: {trace.total_flops:,}")
        logger.info(f"Total memory: {trace.total_memory_mb:.2f} MB")
        logger.info(f"Average CRDT score: {np.mean([l.crdt_friendly_score for l in trace.layers]):.3f}")

        return trace

    except Exception as e:
        logger.error(f"Trace failed for {model_name}: {e}")
        raise
```

## Best Practices

### 1. Trace Management

- **Organize traces by model family**
  ```
  traces/
  ├── vision/
  │   ├── resnet50.json
  │   └── vgg16.json
  ├── language/
  │   ├── bert-base.json
  │   └── gpt2.json
  └── index.json
  ```

### 2. Version Control

- **Tag traces with model version**
- **Include training data hash**
- **Record hardware configuration**

### 3. Performance Optimization

- **Batch trace multiple models**
- **Use HDF5 for large traces**
- **Cache traces in memory for repeated access**

### 4. Validation

- **Cross-check with profilers**
- **Verify FLOP calculations**
- **Validate cache line addresses**

## Troubleshooting

### Common Integration Issues

**Issue:** Trace format mismatch
```python
# Solution: Use converter
workload = TraceConverter.to_workload_trace(pytorch_trace)
```

**Issue:** Missing dependencies
```bash
# Solution: Install all requirements
pip install -r requirements.txt
```

**Issue:** CUDA out of memory
```python
# Solution: Use CPU or smaller batch
tracer = PyTorchTracer(model_name, device="cpu")
```

## Next Steps

1. **Set up trace database** in production
2. **Implement batch processing** pipeline
3. **Create API** for on-demand tracing
4. **Validate** against existing simulations
5. **Deploy** monitoring and alerting

For more details, see:
- `README.md` - Full documentation
- `ARCHITECTURE.md` - Design details
- `QUICKSTART.md` - Quick start guide
