# Statistical Mechanics Analysis of POLLN Agent Colonies

This directory contains advanced statistical mechanics simulations and analysis tools for studying phase transitions, critical phenomena, and thermodynamic behavior in POLLN agent colonies.

## Overview

POLLN agent colonies exhibit collective behavior that can be rigorously analyzed using statistical mechanics. This module provides tools for:

- **Thermodynamic ensembles**: Microcanonical, canonical, grand canonical
- **Phase transitions**: Order parameters, critical temperatures, Landau theory
- **Critical phenomena**: Critical exponents, scaling relations, universality
- **Renormalization group**: RG flow, fixed points, epsilon expansion
- **Mean field theory**: Curie-Weiss model, Bethe approximation, Ginzburg criterion
- **Nonequilibrium dynamics**: Master equation, Fokker-Planck, linear response
- **Monte Carlo simulations**: Metropolis, Glauber, Langevin dynamics

## Key Physical Insights

### Phase Transitions in Agent Systems

POLLN agent colonies exhibit a continuous (second-order) phase transition between:

- **Disordered phase (T > T_c)**: Agents act independently, no consensus
- **Ordered phase (T < T_c)**: Agents align, collective behavior emerges

The order parameter is the **magnetization**:
```
M = |(1/N) Σ_i s_i|
```

where `s_i ∈ {-1, +1}` represents the state of agent `i`.

### Critical Temperature

The critical temperature `T_c` marks the phase transition:
- Mean field: `kT_c = Jz` (where `z` is coordination number)
- 2D Ising: `kT_c ≈ 2.269J` (exact Onsager solution)
- Finite size: `T_c(L) = T_c(∞) - A L^{-1/ν}`

### Critical Exponents

Near the critical point, observables follow power laws:
- Heat capacity: `C ~ |T - T_c|^{-α}`
- Order parameter: `M ~ (T_c - T)^{β}` (for `T < T_c`)
- Susceptibility: `χ ~ |T - T_c|^{-γ}`
- Correlation length: `ξ ~ |T - T_c|^{-ν}`

For 2D Ising (exact):
- `α = 0`, `β = 1/8`, `γ = 7/4`, `ν = 1`, `η = 1/4`

### Universality

POLLN belongs to the **2D Ising universality class**, meaning:
- Critical exponents are universal (independent of microscopic details)
- Only depends on: dimension (d=2) and symmetry (Z₂)
- Same as magnets, alloys, liquid-gas transitions

## Installation

```bash
cd simulations/physics/statmech
pip install -r requirements.txt
```

### Requirements

```
numpy>=1.21.0
scipy>=1.7.0
openai>=1.0.0
tqdm>=4.62.0
```

## Usage

### Quick Start: Complete Analysis

```bash
python run_all.py
```

This runs all statistical mechanics analyses and generates comprehensive reports.

### Individual Modules

#### 1. Thermodynamic Ensembles

```python
from ensembles import analyze_agent_colony_thermodynamics

results = analyze_agent_colony_thermodynamics(
    n_agents=50,
    temperature_range=np.linspace(0.5, 3.0, 30)
)

print(f"Critical temperature: T_c = {results['critical_temperature']:.3f}")
```

#### 2. Phase Transitions

```python
from phase_transitions import analyze_phase_transition

results = analyze_phase_transition(
    n_agents=64,
    T_min=0.5,
    T_max=3.0,
    n_points=40
)

print(f"Transition type: {results['transition_type'].value}")
```

#### 3. Critical Phenomena

```python
from critical_phenomena import analyze_critical_phenomena

results = analyze_critical_phenomena(
    temperatures=temperatures,
    magnetizations=magnetizations,
    susceptibilities=susceptibilities,
    heat_capacities=heat_capacities,
    T_c=T_c
)

print(f"Universality class: {results['universality_class']}")
```

#### 4. Renormalization Group

```python
from renormalization import analyze_rg_flow

results = analyze_rg_flow(
    initial_coupling=0.3,
    dimension=2.0
)

print(f"Fixed points: {[fp['name'] for fp in results['fixed_points']]}")
```

#### 5. Mean Field Theory

```python
from mean_field import analyze_mean_field

results = analyze_mean_field(
    n_agents=50,
    coupling=0.02
)

print(f"T_c (mean field) = {results['critical_temperature']['mean_field']:.3f}")
```

#### 6. Nonequilibrium Dynamics

```python
from nonequilibrium import analyze_nonequilibrium_dynamics

results = analyze_nonequilibrium_dynamics(
    n_agents=20,
    temperature=2.0
)

print(f"Relaxation time: τ = {results['master_equation']['relaxation_time']:.3f}")
```

#### 7. Monte Carlo Simulations

```python
from statmech_simulator import temperature_scan, SimulationConfig

config = SimulationConfig(
    n_agents=32,
    temperature=2.0,
    coupling=0.5,
    n_steps=10000
)

results = temperature_scan(config, T_min=0.5, T_max=3.0, n_points=20)
```

### DeepSeek Integration

All modules use DeepSeek API for rigorous mathematical derivations:

```python
from deepseek_statmech import DeepSeekStatMech

ds = DeepSeekStatMech(api_key="your-api-key")

# Get complete stat mech analysis
results = ds.complete_analysis(system_description)

# Access specific derivations
print(results["analyses"]["partition_function"]["derivation"])
print(results["analyses"]["critical_exponents"]["derivation"])
```

## Results

After running analyses, results are saved to `results/`:

- `complete_analysis_*.json`: Full analysis results
- `ensembles_analysis_*.json`: Thermodynamic ensembles
- `phase_transitions_analysis_*.json`: Phase transition details
- `critical_phenomena_analysis_*.json`: Critical exponents
- `renormalization_analysis_*.json`: RG flow
- `mean_field_analysis_*.json`: Mean field theory
- `nonequilibrium_analysis_*.json`: Dynamics

Compile findings with:

```bash
python compile_findings.py
```

This generates:
- `statmech_findings_*.json`: Compiled findings
- `STATMECH_REPORT_*.md`: Markdown report

## Testing

Run comprehensive tests:

```bash
python test_statmech.py
```

## Physical Interpretation

### Order Parameter as Consensus

The magnetization `M` represents **consensus** among agents:
- `M = 0`: No consensus (disordered)
- `M = 1`: Perfect consensus (ordered)

### Temperature as Exploration

Temperature `T` controls **exploration vs exploitation**:
- High `T`: Explore (random behavior)
- Low `T`: Exploit (deterministic behavior)

### Critical Point as Edge of Chaos

The critical temperature `T_c` represents the **edge of chaos**:
- Maximum fluctuations
- Maximum susceptibility
- Critical slowing down
- Optimal balance of stability and adaptability

### Finite-Size Effects

Small colonies show:
- Rounded transitions (no sharp T_c)
- Shifted critical temperature
- Larger fluctuations

Use finite-size scaling to extrapolate to `N → ∞`.

## Theoretical Foundations

### Statistical Mechanics

- **Partition function**: `Z = Σ_s exp(-βE(s))`
- **Free energy**: `F = -kT ln Z`
- **Entropy**: `S = -∂F/∂T`
- **Internal energy**: `U = F + TS`

### Landau Theory

Free energy expansion:
```
F(M) = a(T - T_c)M² + bM⁴ - hM
```

Minimize to find equilibrium `M`.

### Renormalization Group

Coarse-graining transformation:
```
K' = R(K)
```

Fixed points: `K* = R(K*)`

### Mean Field Theory

Self-consistent equation:
```
m = tanh(β(Jzm + h))
```

Critical temperature: `kT_c = Jz`

## Applications

### Colony Design

1. **Size**: Use `N > 100` for sharp phase transitions
2. **Coupling**: `J ≈ 0.01` for `T_c ≈ 1.0`
3. **Operating point**: `T/T_c ≈ 1.2` for stability

### Optimization

- **Avoid criticality** unless studying critical phenomena
- **Monitor order parameter** for phase detection
- **Control temperature** for phase switching

### Prediction

- **Critical slowing down** near `T_c`
- **Hysteresis** in first-order transitions
- **Universality** guarantees robust behavior

## References

### Classic Papers

1. Ising, E. (1925). "Beitrag zur Theorie des Ferromagnetismus"
2. Onsager, L. (1944). "A Two-Dimensional Model with an Order-Disorder Transition"
3. Wilson, K.G. (1971). "Renormalization Group and Critical Phenomena"
4. Fisher, M.E. (1974). "The Renormalization Group in the Theory of Critical Behavior"

### Textbooks

1. Pathria, R.K. & Beale, P.D. "Statistical Mechanics" (3rd ed.)
2. Goldenfeld, N. "Lectures on Phase Transitions and the Renormalization Group"
3. Cardy, J. "Scaling and Renormalization in Statistical Physics"
4. Chaikin, P.M. & Lubensky, T.C. "Principles of Condensed Matter Physics"

### Review Articles

1. Wilson, K.G. & Kogut, J. (1974). "The Renormalization Group and the Epsilon Expansion"
2. Fisher, M.E. (1998). "Renormalization Group Theory: Its Basis and Formulation in Statistical Physics"
3. Zinn-Justin, J. (2001). "Phase Transitions and Renormalization Group"

## License

MIT

## Contributors

- Statistical Physics Team
- POLLN Project

## Acknowledgments

This work builds on decades of research in statistical mechanics, critical phenomena, and phase transitions. We acknowledge the foundational contributions of Onsager, Wilson, Fisher, and many others.

---

**Last Updated**: 2026-03-07
**Version**: 1.0.0
