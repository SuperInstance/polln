# SuperInstance Research Platform - User Guide

## Getting Started

The SuperInstance Research Platform provides a unified interface for running simulations, validating results, and preparing publications across all SuperInstance papers.

### Quick Start

1. **Install Dependencies:**
```bash
cd research/phase8_platform
pip install -r requirements.txt
```

2. **Start the Platform:**
```bash
python web_interface.py
```

3. **Access the API:**
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## Core Concepts

### Experiments

An **experiment** is a self-contained simulation run with:
- Unique identifier
- Configuration parameters
- Simulation type
- Validation requirements
- Result data

### Backends

The platform supports multiple execution backends:

| Backend | Description | Use When |
|---------|-------------|----------|
| **Local GPU** | GPU acceleration using CuPy | Large-scale simulations, matrix operations |
| **Local CPU** | CPU computation using NumPy | Small simulations, no GPU available |
| **Cloud** | Cloud execution via DeepInfra | Very large simulations, LLM-based tasks |
| **Hybrid** | GPU + Cloud combination | Mixed workloads |
| **Auto** | Automatic selection | Let platform decide |

### Simulation Types

Available simulation types:

```python
HYBRID_MULTI_PAPER      # Multi-paper integration (P12+P13+P19+P20+P27)
HARDWARE_ACCURATE       # Realistic hardware modeling
IMPOSSIBLE_SIMULATION   # Theoretical edge cases
NOVEL_ALGORITHM         # New algorithm discovery
EMERGENCE_PREDICTION    # Emergence detection
GPU_ACCELERATED         # GPU-optimized workloads
CLOUD_ENHANCED          # Cloud LLM integration
ADAPTIVE_LEARNING       # Learning optimization
PRODUCTION_BENCHMARK    # Production validation
```

## Python API Usage

### Basic Example

```python
import asyncio
from unified_platform import (
    create_platform,
    create_experiment,
    Backend,
    SimulationType,
    ValidationType
)

async def main():
    # Create platform
    platform = create_platform()

    # Create experiment
    experiment = create_experiment(
        experiment_id="demo_001",
        name="My First Experiment",
        simulation_type=SimulationType.HYBRID_MULTI_PAPER,
        parameters={
            "num_agents": 100,
            "timesteps": 1000,
            "papers": ["P12", "P13", "P19"]
        },
        backend_preference=Backend.AUTO,
        validation_types=[
            ValidationType.STATISTICAL,
            ValidationType.SANITY
        ]
    )

    # Run simulation
    result = await platform.run_simulation(experiment)

    # Check results
    print(f"Status: {result.status.name}")
    print(f"Backend: {result.backend_used}")
    print(f"Execution Time: {result.execution_time_ms}ms")

    # Access data
    if result.data:
        print(f"Results: {result.data}")

    # Cleanup
    await platform.shutdown()

asyncio.run(main())
```

### Advanced Configuration

```python
from unified_platform import PlatformConfig

# Custom configuration
config = PlatformConfig(
    data_dir=Path("/custom/data/path"),
    max_concurrent_experiments=10,
    max_gpu_memory_gb=5.0,
    cloud_api_key="your-api-key",
    enable_auto_validation=True,
    enable_realtime_viz=True
)

platform = create_platform(config)
```

### Asynchronous Execution

```python
# Submit experiment and get ID immediately
experiment_id = await platform.run_simulation_async(experiment)

# Check status later
status = await platform.get_experiment_status(experiment_id)
print(f"Status: {status['status']}")

# Get results when complete
result = platform.data.load_results(experiment_id)
```

### Comparing Experiments

```python
# Compare multiple experiments
comparison = await platform.compare_results(
    experiment_ids=["exp_001", "exp_002", "exp_003"],
    comparison_type="performance"
)

print(f"Winner: {comparison.winner}")
print(f"Insights: {comparison.insights}")
```

## REST API Usage

### Run Simulation

**POST** `/simulate`

```bash
curl -X POST "http://localhost:8000/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "demo_001",
    "name": "Demo Experiment",
    "simulation_type": "hybrid_multi_paper",
    "parameters": {
      "num_agents": 100,
      "timesteps": 1000
    },
    "backend_preference": "auto",
    "validation_types": ["statistical", "sanity"]
  }'
```

**Response:**
```json
{
  "experiment_id": "demo_001",
  "status": "COMPLETED",
  "data": {...},
  "metadata": {...},
  "figures": [],
  "validation_results": [...],
  "backend_used": "local_gpu",
  "execution_time_ms": 1234.56,
  "cost_usd": 0.0
}
```

### Run Asynchronous Simulation

**POST** `/simulate/async`

```bash
curl -X POST "http://localhost:8000/simulate/async" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "demo_002",
    "name": "Async Demo",
    "simulation_type": "gpu_accelerated",
    "parameters": {...}
  }'
```

**Response:**
```json
{
  "experiment_id": "demo_002",
  "status": "submitted",
  "message": "Experiment running in background"
}
```

### Check Status

**GET** `/status/{experiment_id}`

```bash
curl "http://localhost:8000/status/demo_002"
```

**Response:**
```json
{
  "experiment_id": "demo_002",
  "status": "running",
  "done": false
}
```

### Get Results

**GET** `/results/{experiment_id}`

```bash
curl "http://localhost:8000/results/demo_001"
```

### List Experiments

**GET** `/experiments?tag=hybrid&status=COMPLETED`

```bash
curl "http://localhost:8000/experiments"
curl "http://localhost:8000/experiments?tag=demo"
curl "http://localhost:8000/experiments?status=COMPLETED"
```

### Validate Results

**POST** `/validate`

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": "demo_001",
    "validation_types": ["statistical", "regression"]
  }'
```

### Compare Experiments

**POST** `/compare`

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_ids": ["exp_001", "exp_002"],
    "comparison_type": "performance"
  }'
```

### Get Statistics

**GET** `/stats`

```bash
curl "http://localhost:8000/stats"
```

**Response:**
```json
{
  "total_experiments": 42,
  "status_breakdown": {
    "COMPLETED": 38,
    "RUNNING": 2,
    "FAILED": 2
  },
  "active_experiments": 2,
  "gpu_available": true
}
```

## Common Workflows

### Workflow 1: Single Experiment with Validation

```python
# 1. Create experiment
experiment = create_experiment(
    experiment_id="workflow_001",
    name="Single Experiment",
    simulation_type=SimulationType.EMERGENCE_PREDICTION,
    parameters={
        "network_size": 1000,
        "timesteps": 5000
    },
    validation_types=[
        ValidationType.STATISTICAL,
        ValidationType.SANITY
    ]
)

# 2. Run simulation
result = await platform.run_simulation(experiment)

# 3. Check validation
for report in result.validation_results:
    print(f"{report['validation_type']}: {report['passed']}")

# 4. Access figures
for figure_path in result.figures:
    print(f"Figure: {figure_path}")
```

### Workflow 2: Batch Experiments

```python
# Run parameter sweep
parameters = []
for num_agents in [50, 100, 200, 400]:
    for learning_rate in [0.01, 0.05, 0.1]:
        parameters.append({
            "num_agents": num_agents,
            "learning_rate": learning_rate
        })

# Submit all experiments
experiment_ids = []
for i, params in enumerate(parameters):
    experiment = create_experiment(
        experiment_id=f"sweep_{i:03d}",
        name=f"Parameter Sweep {i}",
        simulation_type=SimulationType.ADAPTIVE_LEARNING,
        parameters=params
    )
    eid = await platform.run_simulation_async(experiment)
    experiment_ids.append(eid)

# Wait for completion and collect results
results = []
for eid in experiment_ids:
    result = platform.data.load_results(eid)
    while result is None or result.status == ExperimentStatus.RUNNING:
        await asyncio.sleep(1)
        result = platform.data.load_results(eid)
    results.append(result)

# Analyze results
for r in results:
    print(f"{r.experiment_id}: {r.execution_time_ms}ms")
```

### Workflow 3: Compare Backends

```python
# Same experiment, different backends
backends = [Backend.LOCAL_GPU, Backend.LOCAL_CPU, Backend.CLOUD]
results = {}

base_params = {
    "num_agents": 1000,
    "timesteps": 10000
}

for backend in backends:
    experiment = create_experiment(
        experiment_id=f"backend_test_{backend.value}",
        name=f"Backend Test: {backend.value}",
        simulation_type=SimulationType.GPU_ACCELERATED,
        parameters=base_params,
        backend_preference=backend
    )

    result = await platform.run_simulation(experiment)
    results[backend.value] = result

# Compare performance
for backend_name, result in results.items():
    print(f"{backend_name}: {result.execution_time_ms}ms, ${result.cost_usd:.4f}")
```

### Workflow 4: Publication Preparation

```python
# 1. Run experiments for paper
experiments = []
for i in range(10):
    exp = create_experiment(
        experiment_id=f"paper_p24_exp_{i}",
        name=f"P24 Experiment {i}",
        simulation_type=SimulationType.HYBRID_MULTI_PAPER,
        parameters={...}
    )
    result = await platform.run_simulation(exp)
    experiments.append(exp.experiment_id)

# 2. Prepare publication package
package = platform.prepare_publication(
    paper_id="P24",
    experiment_ids=experiments
)

# 3. Access compiled materials
print(f"Figures: {len(package['figures'])}")
print(f"Tables: {len(package['tables'])}")
```

## Error Handling

### Common Errors

**1. GPU Out of Memory:**
```
Error: CUDA out of memory
Solution: Reduce batch size or use cloud backend
```

**2. Invalid Simulation Type:**
```
Error: Invalid simulation_type: unknown_type
Solution: Use valid simulation type from SimulationType enum
```

**3. Experiment Not Found:**
```
Error: Results not found for experiment: exp_123
Solution: Check experiment_id is correct and experiment completed
```

**4. Cloud API Error:**
```
Error: Cloud API request failed
Solution: Check API key and network connection
```

### Retry Logic

```python
from unified_platform import ExperimentStatus

async def run_with_retry(experiment, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await platform.run_simulation(experiment)
            if result.status == ExperimentStatus.COMPLETED:
                return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Best Practices

### 1. Experiment Naming

Use descriptive, hierarchical names:
```python
experiment_id = "P24_emergence_network_small_001"
```

### 2. Parameter Documentation

Always document parameters:
```python
parameters = {
    "num_agents": 100,      # Number of agents in simulation
    "timesteps": 1000,      # Number of timesteps to run
    "learning_rate": 0.01,  # Learning rate for optimization
    "seed": 42              # Random seed for reproducibility
}
```

### 3. Tagging

Use tags for organization:
```python
tags = ["P24", "emergence", "production", "v1.0"]
```

### 4. Validation

Always enable validation for production experiments:
```python
validation_types = [
    ValidationType.STATISTICAL,
    ValidationType.SANITY,
    ValidationType.REGRESSION
]
```

### 5. Backend Selection

Let platform decide unless you have specific requirements:
```python
backend_preference = Backend.AUTO  # Recommended
```

## Troubleshooting

### Issue: Platform won't start

**Solution:**
```bash
# Check if port 8000 is available
netstat -an | grep 8000

# Use different port
uvicorn web_interface:app --port 8001
```

### Issue: GPU not detected

**Solution:**
```bash
# Check CuPy installation
python -c "import cupy; print(cupy.cuda.is_available())"

# Check CUDA
nvidia-smi

# Reinstall CuPy
pip install cupy-cuda12x  # Adjust for your CUDA version
```

### Issue: Slow performance

**Solutions:**
- Use GPU backend for large simulations
- Enable caching
- Reduce data logging
- Use async execution for multiple experiments

### Issue: High cloud costs

**Solutions:**
- Set cost limits in config
- Use hybrid mode to split workload
- Cache results to avoid re-computation
- Monitor costs with `/stats` endpoint

## Tips and Tricks

### Tip 1: Use Python Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def platform_session(config=None):
    platform = create_platform(config)
    try:
        yield platform
    finally:
        await platform.shutdown()

# Usage
async with platform_session() as platform:
    result = await platform.run_simulation(experiment)
```

### Tip 2: Stream Results

For long-running simulations, use polling:

```python
async def stream_results(experiment_id):
    while True:
        status = await platform.get_experiment_status(experiment_id)
        if status['done']:
            result = platform.data.load_results(experiment_id)
            return result
        await asyncio.sleep(5)
```

### Tip 3: Batch API Requests

Use asyncio.gather for concurrent requests:

```python
results = await asyncio.gather(
    platform.run_simulation(exp1),
    platform.run_simulation(exp2),
    platform.run_simulation(exp3)
)
```

### Tip 4: Custom Validation

Create custom validation logic:

```python
async def custom_validation(result, experiment):
    # Your validation logic
    passed = True
    score = 0.95
    return ValidationReport(
        validation_type=ValidationType.STATISTICAL,
        passed=passed,
        score=score,
        metrics={"custom_metric": 1.0},
        details="Custom validation passed"
    )
```

## Resources

- **API Documentation:** http://localhost:8000/docs
- **Architecture:** PLATFORM_ARCHITECTURE.md
- **API Reference:** API_REFERENCE.md
- **Examples:** `examples/` directory

## Support

For issues and questions:
1. Check the logs: `research/phase8_platform/platform.log`
2. Review error messages carefully
3. Consult the architecture documentation
4. Check example code in `examples/`
