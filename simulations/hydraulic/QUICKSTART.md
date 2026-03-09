# Quick Start Guide - POLLN Hydraulic Simulations

Get up and running with the hydraulic metaphor simulations in 5 minutes.

## Installation

```bash
# Navigate to simulations directory
cd simulations/hydraulic

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy, scipy, networkx, matplotlib, sklearn; print('All dependencies installed!')"
```

## Run Individual Simulations

### 1. Pressure Dynamics

```bash
python pressure_dynamics.py
```

**What you'll see**:
- Pressure propagation through agent network
- Congestion detection and visualization
- Topology comparison (small-world, scale-free, random, hierarchical)

**Key outputs**:
- Mean pressure, pressure entropy, Gini coefficient
- Congestion frequency and volatility metrics
- 2D network visualizations with pressure heatmaps

### 2. Flow Optimization

```bash
python flow_optimization.py
```

**What you'll see**:
- Flow through different network topologies
- Bottleneck detection (nodes and edges)
- 3D flow field visualizations

**Key outputs**:
- Throughput, latency, efficiency, robustness metrics
- Topology comparison charts
- Optimal topology for each metric

### 3. Valve Control Theory

```bash
python valve_control.py
```

**What you'll see**:
- Gumbel-softmax stochastic routing
- Temperature annealing schedules (exponential, linear, cosine)
- Exploration-exploitation trade-off

**Key outputs**:
- Optimal temperature for given task complexity
- Best annealing schedule comparison
- Adaptive temperature control performance

### 4. Emergence Detection

```bash
python emergence_detection.py
```

**What you'll see**:
- Synergy computation (whole > sum of parts)
- Phase transition detection
- Novel capability discovery

**Key outputs**:
- Synergy, integration, complexity metrics
- Critical connectivity threshold
- Phase diagram visualization

## Run Complete Validation Suite

```bash
python run_all_simulations.py
```

This runs all four modules and generates:
- **Validation Report**: `VALIDATION_REPORT.txt`
- **Summary Visualization**: `validation_summary.png`
- **Mathematical proofs** of all key theorems

## Python API Usage

### Basic Example

```python
from simulations.hydraulic import PressureDynamicsSimulator, TaskDemand

# Create simulator
sim = PressureDynamicsSimulator(
    num_agents=50,
    topology='small_world'
)

# Define task demand
task_demand = TaskDemand(
    arrival_rate=5.0,
    complexity_distribution='normal',
    mean_complexity=1.0
)

# Run simulation
history = sim.run_simulation(num_steps=500, task_demand=task_demand)

# Analyze results
metrics = sim.analyze_pressure_distribution(history)
print(f"Mean pressure: {metrics['mean_pressure']:.4f}")
print(f"Congestion frequency: {metrics['congestion_frequency']:.4f}")
```

### Flow Comparison

```python
from simulations.hydraulic import FlowSimulation

# Create simulation
sim = FlowSimulation(num_agents=50)

# Compare topologies
results = sim.compare_topologies(
    topologies=['small_world', 'scale_free', 'hierarchical'],
    num_trials=100
)

# Find optimal topology
best_topo, score = sim.find_optimal_topology('efficiency')
print(f"Best topology: {best_topo}")
print(f"Efficiency score: {score:.4f}")
```

### Emergence Analysis

```python
from simulations.hydraulic import EmergenceDetector

# Create detector
detector = EmergenceDetector(num_agents=50, capability_dim=10)

# Initialize agents
detector.initialize_agents(diversity=1.0, specialization=0.5)
detector.connect_agents(topology='small_world', connection_prob=0.15)

# Simulate interactions
for _ in range(100):
    detector.simulate_step(interaction_strength=0.1)

# Compute emergence metrics
metrics = detector.compute_emergence_metrics()
print(f"Synergy: {metrics.synergy:.4f}")
print(f"Phase: {metrics.phase}")
print(f"Novel capabilities: {len(metrics.novel_capabilities)}")
```

## Understanding the Output

### Pressure Metrics

| Metric | Meaning | Good Range |
|--------|---------|------------|
| `mean_pressure` | Average cognitive load | 0.5 - 2.0 |
| `pressure_entropy` | Distribution uniformity | 1.5 - 3.0 |
| `gini_coefficient` | Inequality (0=equal, 1=unequal) | 0.2 - 0.5 |
| `congestion_frequency` | Avg congested nodes | < 5 |

### Flow Metrics

| Metric | Meaning | Optimal |
|--------|---------|---------|
| `throughput` | Total information flow | Maximize |
| `latency` | Average path delay | Minimize |
| `efficiency` | Flow/capacity ratio | > 0.7 |
| `robustness` | Failure tolerance | > 0.8 |

### Emergence Metrics

| Metric | Meaning | Interpretation |
|--------|---------|----------------|
| `synergy` | Non-additive information | > 0 = emergence |
| `integration` | Information correlation | 0 - 1 |
| `complexity` | Integration × diversity | Higher = better |
| `phase` | System state | subcritical/critical/supercritical |

## Customization

### Adjust Network Size

```python
# Small network (fast testing)
sim = PressureDynamicsSimulator(num_agents=20)

# Medium network (balanced)
sim = PressureDynamicsSimulator(num_agents=50)

# Large network (production)
sim = PressureDynamicsSimulator(num_agents=200)
```

### Change Topology

```python
# Available: 'small_world', 'scale_free', 'random', 'hierarchical', 'star', 'mesh'
sim = PressureDynamicsSimulator(num_agents=50, topology='scale_free')
```

### Modify Task Complexity

```python
# Simple tasks
task_demand = TaskDemand(arrival_rate=3.0, mean_complexity=0.5)

# Complex tasks
task_demand = TaskDemand(arrival_rate=10.0, mean_complexity=2.0)

# Variable complexity
task_demand = TaskDemand(
    arrival_rate=5.0,
    complexity_distribution='exponential',
    mean_complexity=1.0
)
```

## Troubleshooting

### Issue: Import Errors

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: Slow Simulation

```python
# Solution: Reduce network size or simulation steps
sim = PressureDynamicsSimulator(num_agents=20)  # Instead of 50
history = sim.run_simulation(num_steps=100)     # Instead of 500
```

### Issue: No Emergence Detected

```python
# Solution: Increase connectivity or interaction strength
detector.connect_agents(connection_prob=0.3)  # Increase from 0.1
detector.simulate_step(interaction_strength=0.2)  # Increase from 0.1
```

## Next Steps

1. **Read the full documentation**: `MATHEMATICAL_FOUNDATIONS.md`
2. **Explore examples**: Check the `__main__` sections in each module
3. **Customize parameters**: Experiment with different configurations
4. **Integrate with POLLN**: Use simulations to validate real agent behavior

## Key Equations Reference

### Pressure
```
P_i = (demand_i × complexity_i) / (capacity_i × Δt)
∂P/∂t = D∇²P - dP + S
```

### Flow
```
Q_ij = (P_i - P_j) / R_ij
Throughput = Σ |Q_ij| / 2
```

### Valve (Gumbel-Softmax)
```
π_i = exp((l_i + g_i)/τ) / Σ exp((l_j + g_j)/τ)
```

### Emergence
```
Synergy = I(X_1,...,X_n) - Σ I(X_i) - Σ I(X_i,X_j)
Complexity = Integration × Differentiation
```

## Support

- **Documentation**: `README.md`, `MATHEMATICAL_FOUNDATIONS.md`
- **Examples**: See `__main__` sections in each module
- **Issues**: Report bugs at GitHub repository

---

**Ready to explore emergent intelligence through fluid dynamics! 🌊**
