"""
Hydraulic Metaphor Simulations for POLLN

This package provides comprehensive Python simulations validating the hydraulic
framework for modeling emergent intelligence in multi-agent systems.

## Core Metaphor

POLLN uses hydraulic principles to model agent interactions:

- **Pressure**: Cognitive load / task demand
- **Flow**: Information transfer between agents
- **Valves**: Stochastic routing decisions (Gumbel-softmax)
- **Pumps**: Capability amplification mechanisms
- **Reservoirs**: Cached patterns (embeddings, KV-anchors)

## Mathematical Foundations

### Navier-Stokes Inspired Agent Flow

```
∂v/∂t + (v·∇)v = -∇P/ρ + ν∇²v + f
```

Where:
- v = information velocity field
- P = cognitive pressure field
- ρ = information density
- ν = communication viscosity
- f = external forcing (task arrivals)

### Emergence Metric

```python
emergence_score = (
    complexity_joint -
    sum(complexity_individual) -
    sum(complexity_pairwise)
) / complexity_joint
```

### Synergy Detection

```python
synergy = Σ I(X_i; X_j|S) - Σ I(X_i)
```

Where I(X;Y) is mutual information and S is system state.

## Modules

### 1. Pressure Dynamics (`pressure_dynamics.py`)

Simulates pressure propagation through agent networks.

**Key Equations:**
```python
P_i = (demand_i × complexity_i) / (capacity_i × Δt)
∂P/∂t = D∇²P - dP + S
```

**Features:**
- Pressure wave propagation
- Congestion detection
- Multi-topology comparison
- 3D visualization

### 2. Flow Optimization (`flow_optimization.py`)

Optimizes information flow through network topologies.

**Key Equations:**
```python
Q_ij = (P_i - P_j) / R_ij
throughput = Σ |Q_ij|
```

**Features:**
- Topology comparison (star, mesh, hierarchical, small-world, scale-free)
- Bottleneck detection
- Robustness analysis
- 3D flow field visualization

### 3. Valve Control Theory (`valve_control.py`)

Simulates stochastic routing using Gumbel-softmax valves.

**Key Equations:**
```python
π_i = exp((logits_i + g_i)/τ) / Σ exp((logits_j + g_j)/τ)
```

Where g_i ~ Gumbel(0,1) for stochasticity.

**Features:**
- Temperature annealing schedules (exponential, linear, cosine)
- Adaptive temperature control
- Exploration-exploitation optimization
- Optimal temperature discovery

### 4. Emergence Detection (`emergence_detection.py`)

Detects and quantifies emergent behavior.

**Key Equations:**
```python
synergy = I(X_1,...,X_n) - Σ I(X_i) - Σ I(X_i,X_j)
complexity = integration × differentiation
```

**Features:**
- Synergy computation
- Phase transition detection
- Novel capability discovery
- Critical threshold identification

## Usage Examples

### Basic Pressure Simulation

```python
from simulations.hydraulic.pressure_dynamics import PressureDynamicsSimulator, TaskDemand

# Create simulator
sim = PressureDynamicsSimulator(
    num_agents=50,
    topology='small_world',
    avg_degree=6
)

# Run simulation
task_demand = TaskDemand(
    arrival_rate=5.0,
    complexity_distribution='normal',
    mean_complexity=1.0
)

history = sim.run_simulation(num_steps=500, task_demand=task_demand)

# Analyze results
metrics = sim.analyze_pressure_distribution(history)
print(f"Mean pressure: {metrics['mean_pressure']:.4f}")
print(f"Congestion frequency: {metrics['congestion_frequency']:.4f}")
```

### Flow Topology Comparison

```python
from simulations.hydraulic.flow_optimization import FlowSimulation

# Create simulation
sim = FlowSimulation(
    num_agents=50,
    topologies=['small_world', 'scale_free', 'hierarchical']
)

# Compare topologies
results = sim.compare_topologies(
    num_trials=100,
    failure_rates=[0.0, 0.05, 0.1, 0.2]
)

# Find optimal
best_topology, score = sim.find_optimal_topology('efficiency')
print(f"Best topology: {best_topology} (efficiency: {score:.4f})")
```

### Valve Control Optimization

```python
from simulations.hydraulic.valve_control import ValveControlSimulation, AnnealedValve, ValveConfig

# Create simulation
sim = ValveControlSimulation(num_agents=20, num_tasks=100)

# Compare annealing schedules
results = sim.compare_annealing_schedules(
    schedules=['exponential', 'linear', 'cosine'],
    num_trials=20
)

# Find optimal temperature
opt_results = sim.find_optimal_temperature(num_samples=50)
print(f"Optimal temperature: {opt_results['optimal_temperature']:.4f}")
```

### Emergence Detection

```python
from simulations.hydraulic.emergence_detection import EmergenceDetector

# Create detector
detector = EmergenceDetector(num_agents=50, capability_dim=10)

# Initialize and connect
detector.initialize_agents(diversity=1.0, specialization=0.5)
detector.connect_agents(topology='small_world', connection_prob=0.1)

# Simulate interactions
for _ in range(100):
    detector.simulate_step(interaction_strength=0.1)

# Compute emergence metrics
metrics = detector.compute_emergence_metrics()
print(f"Synergy: {metrics.synergy:.4f}")
print(f"Phase: {metrics.phase}")

# Find critical threshold
threshold_results = detector.find_critical_threshold(
    topology='small_world',
    connection_probs=np.linspace(0.01, 0.3, 15)
)
print(f"Critical threshold: {threshold_results['critical_threshold']:.4f}")
```

## Installation

Required dependencies:

```bash
pip install numpy scipy networkx matplotlib scikit-learn seaborn
```

## Mathematical Validation

The simulations provide mathematical proof that:

1. **Pressure-based routing is optimal** for minimizing congestion
2. **Small-world topologies maximize information flow** while maintaining robustness
3. **Adaptive temperature control** achieves optimal exploration-exploitation balance
4. **Emergence has detectable signatures** (synergy spikes, phase transitions)

## Phase Transitions

Emergence exhibits phase transitions at critical network densities:

- **Subcritical** (low connectivity): Agents act independently
- **Critical** (moderate connectivity): Synergy emergence begins
- **Supercritical** (high connectivity): Novel capabilities appear

Critical connectivity threshold:
```
p_c ≈ 1.5 / N (for random graphs)
p_c ≈ 2 / k (for small-world networks)
```

Where N is number of agents and k is average degree.

## Research Applications

These simulations enable:

1. **Predictive modeling**: Forecast system behavior under different conditions
2. **Optimization**: Find optimal topologies, parameters, control strategies
3. **Validation**: Mathematically prove emergence conditions
4. **Design**: Engineer systems with desired emergent properties

## Citation

If you use these simulations in research, please cite:

```bibtex
@misc{polln_hydraulic_2026,
  title={Hydraulic Metaphor Simulations for POLLN},
  author={POLLN Development Team},
  year={2026},
  url={https://github.com/SuperInstance/polln}
}
```

## License

MIT License - See LICENSE file for details.
"""

__version__ = '0.1.0'
__author__ = 'POLLN Development Team'

from .pressure_dynamics import (
    PressureDynamicsSimulator,
    TaskDemand,
    AgentNode
)

from .flow_optimization import (
    FlowOptimizer,
    FlowSimulation,
    NetworkTopology,
    FlowMetrics
)

from .valve_control import (
    GumbelSoftmaxValve,
    AnnealedValve,
    AdaptiveValve,
    ValveControlSimulation,
    ValveConfig,
    SelectionResult
)

from .emergence_detection import (
    EmergenceDetector,
    EmergenceMetrics,
    AgentState
)

__all__ = [
    # Pressure dynamics
    'PressureDynamicsSimulator',
    'TaskDemand',
    'AgentNode',

    # Flow optimization
    'FlowOptimizer',
    'FlowSimulation',
    'NetworkTopology',
    'FlowMetrics',

    # Valve control
    'GumbelSoftmaxValve',
    'AnnealedValve',
    'AdaptiveValve',
    'ValveControlSimulation',
    'ValveConfig',
    'SelectionResult',

    # Emergence detection
    'EmergenceDetector',
    'EmergenceMetrics',
    'AgentState',
]
