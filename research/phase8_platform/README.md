# SuperInstance Research Platform

A unified, production-ready research platform integrating all simulation systems from the SuperInstance papers project (Phases 1-7).

## Features

- **Unified API**: Single interface for all simulation types
- **Multi-Backend Support**: Local GPU (CuPy), Local CPU (NumPy), Cloud (DeepInfra), Hybrid
- **Intelligent Orchestration**: Automatic backend selection and resource allocation
- **Validation Framework**: Statistical, cross-validation, regression detection
- **Real-Time Visualization**: Interactive dashboards and publication-quality figures
- **Publication Ready**: Automated paper preparation with figures and tables
- **Scalable**: Async/await architecture with concurrent experiment support
- **RESTful API**: Complete HTTP API with OpenAPI documentation
- **Production Ready**: Docker and Kubernetes deployment configs

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/SuperInstance/SuperInstance-papers.git
cd SuperInstance-papers/research/phase8_platform

# Install dependencies
pip install -r requirements.txt

# Optional: Install GPU support (CuPy)
pip install cupy-cuda12x  # For CUDA 12.x
# or
pip install cupy-cuda11x  # For CUDA 11.x
```

### Start the Platform

```bash
# Development server with auto-reload
python web_interface.py

# Or using uvicorn directly
uvicorn web_interface:app --reload --host 0.0.0.0 --port 8000
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Python Usage

```python
import asyncio
from unified_platform import (
    create_platform,
    create_experiment,
    SimulationType,
    ValidationType
)

async def main():
    # Create platform
    platform = create_platform()

    # Create experiment
    experiment = create_experiment(
        experiment_id="demo_001",
        name="My Experiment",
        simulation_type=SimulationType.HYBRID_MULTI_PAPER,
        parameters={
            "num_agents": 100,
            "timesteps": 1000,
            "papers": ["P12", "P13", "P19", "P20"]
        },
        validation_types=[ValidationType.STATISTICAL]
    )

    # Run simulation
    result = await platform.run_simulation(experiment)

    print(f"Status: {result.status.name}")
    print(f"Execution Time: {result.execution_time_ms}ms")

    # Cleanup
    await platform.shutdown()

asyncio.run(main())
```

## REST API Usage

### Run Simulation

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
    "backend_preference": "auto"
  }'
```

### Check Status

```bash
curl "http://localhost:8000/status/demo_001"
```

### Get Results

```bash
curl "http://localhost:8000/results/demo_001"
```

## Documentation

- **[Platform Architecture](PLATFORM_ARCHITECTURE.md)** - System design and components
- **[User Guide](USER_GUIDE.md)** - Comprehensive usage guide
- **[API Reference](API_REFERENCE.md)** - Complete API documentation

## Supported Simulation Types

| Type | Description | Optimal Backend |
|------|-------------|-----------------|
| `HYBRID_MULTI_PAPER` | Multi-paper integration | GPU/Cloud |
| `HARDWARE_ACCURATE` | Realistic hardware modeling | GPU |
| `IMPOSSIBLE_SIMULATION` | Theoretical edge cases | Cloud |
| `NOVEL_ALGORITHM` | New algorithm discovery | Cloud |
| `EMERGENCE_PREDICTION` | Emergence detection | GPU |
| `GPU_ACCELERATED` | GPU-optimized workloads | GPU |
| `CLOUD_ENHANCED` | Cloud LLM integration | Cloud |
| `ADAPTIVE_LEARNING` | Learning optimization | Hybrid |
| `PRODUCTION_BENCHMARK` | Production validation | GPU |

## Backends

### Local GPU (CuPy)
- NVIDIA GPU with CUDA support
- CuPy 14.0.1+
- Best for: Large-scale simulations, matrix operations

### Local CPU (NumPy)
- Automatic fallback if GPU unavailable
- Best for: Small simulations, development

### Cloud (DeepInfra)
- Requires API key
- Best for: Very large simulations, LLM tasks

### Hybrid
- Automatic workload splitting
- Best for: Mixed workloads

## Validation Types

- `STATISTICAL`: Statistical significance testing
- `CROSS_VALIDATION`: Historical comparison
- `GPU_CLOUD_CROSS`: Backend consistency
- `REGRESSION`: Performance regression
- `SANITY`: Basic sanity checks

## Deployment

### Docker

```bash
# Build image
docker build -f deployment/docker/Dockerfile -t superinstance-platform .

# Run container
docker run -p 8000:8000 superinstance-platform
```

### Docker Compose

```bash
cd deployment/docker
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f deployment/kubernetes/deployment.yaml
```

## Configuration

Environment variables:

```bash
# Platform
PLATFORM_DATA_DIR=/path/to/data
PLATFORM_MAX_CONCURRENT=5
PLATFORM_LOG_LEVEL=INFO

# GPU
PLATFORM_MAX_GPU_MEMORY_GB=4.0

# Cloud
DEEPINFRA_API_KEY=your_api_key
DEEPINFRA_API_BASE=https://api.deepinfra.com/v1
PLATFORM_MAX_COST_USD=10.0

# Validation
PLATFORM_ENABLE_AUTO_VALIDATION=true
PLATFORM_SIGNIFICANCE_LEVEL=0.05
```

## Examples

See the `examples/` directory:
- `basic_usage.py` - Python usage examples
- `api_examples.sh` - REST API examples

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Interface (FastAPI)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Orchestration Layer                         │
│         (Backend Selection & Resource Allocation)        │
└──────┬─────────┬─────────┬─────────┬────────────────────┘
       │         │         │         │
┌──────┴────┐ ┌──┴────┐ ┌──┴────┐ ┌──┴─────────┐
│Simulation │ │Validation│ │ Data │ │Visualization│
└──────┬────┘ └──┬────┘ └──┬────┘ └──┬─────────┘
       │         │         │         │
┌──────┴─────────┴─────────┴─────────┴──────────────────┐
│              Execution Backends                         │
│  Local GPU (CuPy) │ Local CPU (NumPy) │ Cloud          │
└────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.11+
- FastAPI 0.100+
- NumPy 1.24+
- CuPy 14.0+ (optional, for GPU support)

## Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy unified_platform.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Citation

If you use this platform in your research, please cite:

```bibtex
@software{superinstance_platform,
  title={SuperInstance Research Platform},
  author={SuperInstance Research Team},
  year={2026},
  url={https://github.com/SuperInstance/SuperInstance-papers}
}
```

## Support

- Issues: https://github.com/SuperInstance/SuperInstance-papers/issues
- Discussions: https://github.com/SuperInstance/SuperInstance-papers/discussions
- Documentation: See PLATFORM_ARCHITECTURE.md, USER_GUIDE.md, API_REFERENCE.md

## Acknowledgments

Built on research from SuperInstance Papers P1-P40, integrating:
- Phase 6: Advanced Simulations
- Phase 7: GPU & Cloud Integration
- Production Framework components

## Roadmap

- [ ] Web UI for experiment management
- [ ] Real-time experiment monitoring
- [ ] Advanced caching strategies
- [ ] Multi-user support with authentication
- [ ] Distributed execution across multiple machines
- [ ] Integration with MLflow for experiment tracking
- [ ] Automated paper generation from templates
