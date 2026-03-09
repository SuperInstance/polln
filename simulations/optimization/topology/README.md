# POLLN Topology Optimization Simulator

A comprehensive Python simulation suite for discovering optimal network topologies for POLLN agent communication using graph theory and network science.

## Overview

This simulator uses graph theory, network science, and optimization algorithms to discover optimal network topologies for different colony sizes and workload patterns. It generates production-ready topology templates that can be directly used in POLLN deployments.

## Features

- **10 Topology Types**: Erdős-Rényi, Watts-Strogatz, Barabási-Albert, modular, hierarchical, and more
- **Comprehensive Metrics**: 20+ graph metrics including efficiency, robustness, and cost
- **Workload Modeling**: 5+ communication patterns (broadcast, gossip, aggregation, etc.)
- **Optimization Engine**: Simulated annealing with Pareto frontier analysis
- **Production Templates**: Auto-generated TypeScript templates for POLLN core

## Installation

```bash
# Navigate to topology simulator directory
cd simulations/optimization/topology

# Install dependencies
pip install networkx numpy matplotlib powerlaw

# Optional: For parallel processing
pip install multiprocess
```

## Quick Start

### 1. Generate a Topology

```bash
python generate_topology.py generate -n 100 -t watts_strogatz -k 6 -p 0.1 -v
```

### 2. Compare Topologies

```bash
python generate_topology.py compare -n 100
```

### 3. Get Recommendation

```bash
python generate_topology.py recommend -n 100 --robustness
```

### 4. Run Full Optimization

```bash
python run_all.py --sizes 10 50 100 --iterations 50
```

## Command-Line Interface

### Generate Command

Generate and visualize a topology:

```bash
python generate_topology.py generate [OPTIONS]

Options:
  -n, --size INT          Number of agents (nodes) [required]
  -t, --type TYPE         Topology type [required]
  -k, --degree INT        Mean degree
  -p, --probability FLOAT Rewiring/edge probability
  -m, --edges-per-step INT Edges per step (BA)
  --modules INT           Number of modules
  --levels INT            Hierarchy levels
  -s, --seed INT          Random seed (default: 42)
  -o, --output FILE       Output file (GraphML/JSON)
  -v, --visualize         Visualize topology
  --format FORMAT         Output format (graphml/json)
```

### Evaluate Command

Evaluate a topology's metrics:

```bash
python generate_topology.py evaluate -n 100 -t watts_strogatz -k 6 -p 0.1
```

### Compare Command

Compare multiple topologies:

```bash
python generate_topology.py compare -n 100 --topologies watts_strogatz barabasi_albert modular
```

### List Command

List available topology types:

```bash
python generate_topology.py list
```

### Benchmark Command

Generate benchmark suite:

```bash
python generate_topology.py benchmark -n 100 -o output/ -v
```

### Recommend Command

Get topology recommendation:

```bash
python generate_topology.py recommend -n 100 --efficiency
python generate_topology.py recommend -n 100 --robustness
python generate_topology.py recommend -n 100 --low-cost
```

## Python API

### Generate Topologies

```python
from topology_generator import TopologyGenerator, TopologyType, TopologyParams

generator = TopologyGenerator(seed=42)
params = TopologyParams(n=100, k=6, p=0.1)

G = generator.generate(TopologyType.WATTS_STROGATZ, params)
```

### Evaluate Topologies

```python
from topology_evaluator import TopologyEvaluator

evaluator = TopologyEvaluator(parallel=True)
metrics = evaluator.evaluate(G)

print(f"Avg Path Length: {metrics.avg_path_length}")
print(f"Clustering: {metrics.clustering_coefficient}")
print(f"Global Efficiency: {metrics.global_efficiency}")
```

### Generate Workloads

```python
from workload_modeling import WorkloadGenerator, WorkloadConfig

workload_gen = WorkloadGenerator(G, seed=42)
config = WorkloadConfig(num_requests=1000)

requests = workload_gen.generate(config)
```

### Optimize Topologies

```python
from topology_optimizer import TopologyOptimizer

optimizer = TopologyOptimizer(colony_size=100, workload_config=config)
results = optimizer.optimize(iterations=50)

best = results[0]
print(f"Best: {best.topology_type} (score: {best.score})")
```

## Topology Types

### 1. Erdős-Rényi (erdos_renyi)
Random graph where each edge exists with probability p.

**Best for**: Unpredictable communication patterns, baseline comparisons

**Parameters**: `p` (edge probability)

### 2. Watts-Strogatz (watts_strogatz)
Small-world graph with high clustering and short path lengths.

**Best for**: Most scenarios, balanced efficiency and learning

**Parameters**: `k` (mean degree), `p` (rewiring probability)

### 3. Barabási-Albert (barabasi_albert)
Scale-free network with preferential attachment.

**Best for**: Hub-and-spoke patterns, hierarchical communication

**Parameters**: `m` (edges per step)

### 4. Modular (modular)
Graph with distinct modules and bridge connections.

**Best for**: Multi-team scenarios, fault tolerance

**Parameters**: `modules` (number of modules)

### 5. Two-Tier (two_tier)
Core layer (fully connected) + edge layer.

**Best for**: High-efficiency scenarios

**Parameters**: `k` (edge connections to core)

### 6. Three-Tier (three_tier)
Core → Aggregation → Edge hierarchy.

**Best for**: Large-scale deployments

**Parameters**: None (auto-configured)

### 7. Hierarchical (hierarchical)
Multi-level hierarchy with tiered communication.

**Best for**: Organizational structures

**Parameters**: `levels` (hierarchy levels)

### 8. Hybrid Small-World + Scale-Free (hybrid_small_world_sf)
Combines small-world clustering with scale-free hubs.

**Best for**: Complex, evolving colonies

**Parameters**: `k` (mean degree), `p` (rewiring probability)

## Metrics Explained

### Structural Metrics

- **Average Path Length**: Average shortest path between all node pairs
- **Diameter**: Longest shortest path in the graph
- **Clustering Coefficient**: Tendency for nodes to cluster together
- **Transitivity**: Ratio of triangles to connected triples

### Efficiency Metrics

- **Global Efficiency**: Average inverse shortest path length
- **Local Efficiency**: Efficiency of node neighborhoods

### Robustness Metrics

- **Attack Tolerance**: Size of largest component after removing high-degree nodes
- **Failure Tolerance**: Size of largest component after random node removal
- **Node Connectivity**: Minimum nodes to remove to disconnect graph
- **Edge Connectivity**: Minimum edges to remove to disconnect graph

### Cost Metrics

- **Edge Cost**: Normalized edge count (0-1)
- **Degree Cost**: Normalized maximum degree (0-1)

## Output Structure

```
output/
├── topologies/           # Generated topologies (GraphML/JSON)
│   ├── 10/
│   ├── 50/
│   └── 100/
├── metrics/              # Evaluation metrics (JSON)
│   ├── 10/
│   ├── 50/
│   └── 100/
├── results/              # Optimization results
│   └── optimizations/
├── templates/            # Production templates
│   ├── templates.json
└── TOPOLOGY_CATALOG.json # Complete catalog
```

## Production Integration

Generated templates are exported to TypeScript:

```typescript
import {
  TOPOLOGY_TEMPLATES,
  getTemplateForSize,
  recommendTopology
} from './src/core/topology/templates';

// Get template for colony size
const template = getTemplateForSize(100);

// Get recommendation
const recommended = recommendTopology({
  colonySize: 100,
  prioritizeRobustness: true
});
```

## Running Tests

```bash
# Run all tests
pytest test_topology.py -v

# Run specific test class
pytest test_topology.py::TestTopologyGenerator -v

# Run with coverage
pytest test_topology.py --cov=. --cov-report=html
```

## Performance Tips

1. **Use parallel evaluation** for large graphs:
   ```python
   evaluator = TopologyEvaluator(parallel=True)
   ```

2. **Reduce iterations** for quick testing:
   ```bash
   python run_all.py --quick
   ```

3. **Sample large graphs** instead of full evaluation:
   ```python
   metrics = evaluator.evaluate_sample(G, sample_size=100)
   ```

## Research Background

This simulator implements established network science concepts:

- **Small-World Networks**: Watts & Strogatz (1998)
- **Scale-Free Networks**: Barabási & Albert (1999)
- **Network Efficiency**: Latora & Marchiori (2001)
- **Pareto Optimization**: Multi-objective optimization theory

## Citation

If you use this simulator in research, please cite:

```bibtex
@software{polln_topology,
  title = {POLLN Topology Optimization Simulator},
  author = {POLLN Team},
  year = {2026},
  url = {https://github.com/SuperInstance/polln}
}
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Contact

For questions or issues, please open a GitHub issue or contact the POLLN team.
