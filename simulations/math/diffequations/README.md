# POLLN Differential Equations Simulations

Advanced mathematical analysis of POLLN dynamics using partial differential equations (PDEs) and stochastic differential equations (SDEs). This package provides rigorous mathematical derivations via DeepSeek API and comprehensive numerical simulations.

## Overview

This package implements five major mathematical frameworks for analyzing POLLN (Pattern-Organized Large Language Network):

1. **Fokker-Planck Equation** - Agent state evolution in continuous probability space
2. **Information Fluid Dynamics** - A2A communication modeled as Navier-Stokes fluid flow
3. **Reaction-Diffusion System** - Turing pattern formation in value networks
4. **Hamilton-Jacobi-Bellman Equation** - Optimal control for agent policies
5. **Stochastic Differential Equations** - Agent dynamics with exploration noise

## Installation

```bash
# Install dependencies
cd polln
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- numpy
- scipy
- matplotlib
- openai (for DeepSeek API)
- pytest (for testing)

## Quick Start

### Run All Simulations

```bash
# Run all simulations with DeepSeek derivations
python simulations/math/diffequations/run_all.py

# Run without derivations (simulations only)
python simulations/math/diffequations/run_all.py --no-derive

# Run specific simulations
python simulations/math/diffequations/run_all.py --simulations fokker_planck reaction_diffusion
```

### Run Individual Simulations

```python
from simulations.math.diffequations import fokker_planck

# Run Fokker-Planck simulation
api_key = "your-deepseek-api-key"
solver = fokker_planck.run_simulation(
    api_key=api_key,
    n_steps=500,
    plot_results=True
)
```

## Modules

### 1. Fokker-Planck Equation (`fokker_planck.py`)

Models probability density evolution of agent states:

```python
∂ρ/∂t = -∇·(ρμ) + ∇·(D∇ρ)
```

**Features:**
- Finite difference solver (Crank-Nicolson)
- Stationary distribution computation
- KL divergence convergence metrics
- Boundary condition handling

**Usage:**
```python
from simulations.math.diffequations.fokker_planck import FokkerPlanckSolver

solver = FokkerPlanckSolver(
    state_dim=1,
    domain_size=10.0,
    grid_points=200,
    dt=0.01
)

solver.initialize_gaussian(mean=0.0, std=0.5)
solver.step(method="crank_nicolson")
```

### 2. Information Fluid Dynamics (`information_fluid.py`)

Models A2A communication as fluid flow:

```python
∂ρ/∂t + ∇·(ρu) = 0
∂u/∂t + (u·∇)u = -∇p/ρ + ν∇²u
∇·u = 0
```

**Features:**
- Navier-Stokes solver (projection method)
- Reynolds number computation
- Flow regime detection (laminar/transitional/turbulent)
- Vorticity analysis

**Usage:**
```python
from simulations.math.diffequations.information_fluid import InformationFluidSolver

solver = InformationFluidSolver(
    domain_size=1.0,
    grid_points=64,
    viscosity=0.01,
    dt=0.001
)

solver.initialize_source(x0=0.5, y0=0.5, radius=0.1)
solver.initialize_velocity_field(flow_type="vortex")
solver.step()
```

### 3. Reaction-Diffusion System (`reaction_diffusion.py`)

Models value propagation as activator-inhibitor system:

```python
∂u/∂t = a - u + u²v + Du∇²u
∂v/∂t = b - u²v + Dv∇²v
```

**Features:**
- Schnakenberg kinetics
- Turing instability analysis
- Pattern wavelength prediction
- Spectral method solver

**Usage:**
```python
from simulations.math.diffequations.reaction_diffusion import ReactionDiffusionSolver

solver = ReactionDiffusionSolver(
    domain_size=100.0,
    grid_points=128,
    dt=0.1,
    Du=1.0,
    Dv=40.0
)

solver.initialize_random(noise_level=0.01)
stability = solver.linear_stability_analysis()
```

### 4. HJB Optimal Control (`hjb_optimal_control.py`)

Solves for optimal agent policies using dynamic programming:

```python
-∂V/∂t = min_u [c(x,u) + ∇V·f(x,u)]
```

**Features:**
- Value function iteration
- Optimal policy extraction
- Trajectory simulation
- Optimality verification

**Usage:**
```python
from simulations.math.diffequations.hjb_optimal_control import HJBSolver

solver = HJBSolver(
    state_dim=1,
    domain_size=5.0,
    grid_points=100,
    dt=0.01,
    discount=0.95
)

solver.solve_value_iteration(max_iter=1000)
states, controls = solver.simulate_trajectory(x0=1.0, T=5.0)
```

### 5. Stochastic Dynamics (`stochastic_dynamics.py`)

Models agent behavior with SDEs:

```python
dX_t = μ(X_t,t)dt + σ(X_t,t)dW_t
```

**Features:**
- Itô and Stratonovich calculus
- Euler-Maruyama and Milstein integration
- Exit time analysis
- Fokker-Planck approximation

**Usage:**
```python
from simulations.math.diffequations.stochastic_dynamics import SDEIntegrator

integrator = SDEIntegrator(dim=1, dt=0.01)
x0 = np.array([1.0])

states, time = integrator.euler_maruyama(x0, T=10.0, interpretation="ito")
```

## DeepSeek Integration

### Mathematical Derivations

The package uses DeepSeek API to derive rigorous mathematical equations:

```python
from simulations.math.diffequations.deepseek_math import DeepSeekMath

math_engine = DeepSeekMath(api_key="your-api-key")

# Derive PDE for a concept
result = math_engine.derive_pde("Agent state evolution in POLLN")

# Access derivation
print(result.final_equation)
print(result.assumptions)
print(result.existence_proof)
```

### API Call Management

```python
# Check usage
print(math_engine.get_usage_report())

# Derive multiple concepts
concepts = [
    "Fokker-Planck equation for agent states",
    "Navier-Stokes for information flow",
    # ... more concepts
]
results = math_engine.derive_multiple(concepts)
```

## Numerical Methods

### Finite Difference Methods

- **Forward Euler**: First-order explicit, conditionally stable
- **Backward Euler**: First-order implicit, unconditionally stable
- **Crank-Nicolson**: Second-order implicit, unconditionally stable

### Spectral Methods

- FFT-based for reaction-diffusion
- High accuracy for smooth solutions
- Periodic boundary conditions

### Stochastic Integration

- **Euler-Maruyama**: Strong order 0.5
- **Milstein**: Strong order 1.0
- Itô and Stratonovich interpretations

## Testing

```bash
# Run all tests
pytest simulations/math/diffequations/test_diffequations.py -v

# Run specific test class
pytest simulations/math/diffequations/test_diffequations.py::TestFokkerPlanck -v

# Run with coverage
pytest simulations/math/diffequations/test_diffequations.py --cov=simulations/math/diffequations
```

## Output Files

After running simulations, the following files are generated:

- `fokker_planck_evolution.png` - Probability density evolution
- `information_fluid_flow.png` - Velocity field and vorticity
- `reaction_diffusion_patterns.png` - Turing pattern formation
- `hjb_optimal_control.png` - Value function and optimal policy
- `stochastic_dynamics.png` - SDE trajectories and distributions
- `api_usage_report.txt` - DeepSeek API usage statistics
- `all_derivations.json` - All mathematical derivations
- `MATHEMATICAL_REPORT.md` - Comprehensive findings report

## API Usage

The orchestrator manages up to 1000 DeepSeek API calls:

```bash
# Check current usage
python -c "from simulations.math.diffequations.deepseek_math import APICallTracker; print(APICallTracker().total_calls)"
```

## Examples

### Example 1: Agent State Distribution

```python
from simulations.math.diffequations.fokker_planck import FokkerPlanckSolver

# Create solver
solver = FokkerPlanckSolver(state_dim=1, domain_size=5.0, grid_points=200)

# Initialize with narrow Gaussian
solver.initialize_gaussian(mean=0.0, std=0.5)

# Evolve to stationary distribution
for _ in range(500):
    solver.step(method="crank_nicolson")

# Compute statistics
stats = solver.compute_statistics()
print(f"Mean: {stats['mean']:.3f}")
print(f"Std: {stats['std']:.3f}")
print(f"Entropy: {stats['entropy']:.3f}")
```

### Example 2: Value Network Patterns

```python
from simulations.math.diffequations.reaction_diffusion import ReactionDiffusionSolver

# Create solver with high diffusion ratio
solver = ReactionDiffusionSolver(
    domain_size=100.0,
    grid_points=128,
    Du=1.0,
    Dv=40.0  # High ratio for Turing patterns
)

# Initialize with small noise
solver.initialize_random(noise_level=0.01)

# Analyze stability
stability = solver.linear_stability_analysis()
print(f"Turing patterns possible: {stability['turing_instability']['turing_patterns_possible']}")

# Evolve patterns
for _ in range(500):
    solver.step(method="rk4")

# Analyze emerged patterns
stats = solver.compute_pattern_statistics()
print(f"Pattern wavelength: {stats['pattern_wavelength']:.2f}")
print(f"Pattern amplitude: {stats['amplitude']:.3f}")
```

### Example 3: Optimal Agent Policy

```python
from simulations.math.diffequations.hjb_optimal_control import HJBSolver

# Create solver
solver = HJBSolver(state_dim=1, domain_size=5.0, discount=0.95)

# Solve for optimal value function
solver.solve_value_iteration(max_iter=1000)

# Test optimal policy
x0 = 2.0
states, controls = solver.simulate_trajectory(x0, T=5.0)

# Compute cost-to-go
cost = solver.compute_cost_to_go(x0)
print(f"Cost-to-go from x0={x0}: {cost:.3f}")
```

## Documentation

- `DERIVATIONS.md` - Complete mathematical derivations from DeepSeek
- `NUMERICAL_METHODS.md` - Detailed numerical solution techniques
- `RESULTS.md` - Summary of findings and insights

## Contributing

When adding new PDE solvers:

1. Inherit from `PDESolver` base class
2. Implement required methods: `step()`, `initial_condition()`
3. Add comprehensive tests
4. Include DeepSeek derivation support
5. Document mathematical rigor

## License

MIT License - See LICENSE file for details

## Citation

```bibtex
@misc{polln_diffequations,
  title={POLLN Differential Equations Analysis},
  author={POLLN Development Team},
  year={2026},
  url={https://github.com/SuperInstance/polln}
}
```

## Contact

For questions or issues, please open a GitHub issue or contact the development team.
