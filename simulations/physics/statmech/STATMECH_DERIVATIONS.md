# Statistical Mechanics Derivations for POLLN

This document contains complete mathematical derivations of statistical mechanics concepts applied to POLLN agent colonies.

## Table of Contents

1. [Thermodynamic Ensembles](#thermodynamic-ensembles)
2. [Partition Functions](#partition-functions)
3. [Landau Theory](#landau-theory)
4. [Critical Exponents](#critical-exponents)
5. [Renormalization Group](#renormalization-group)
6. [Mean Field Theory](#mean-field-theory)
7. [Scaling Relations](#scaling-relations)
8. [Nonequilibrium Dynamics](#nonequilibrium-dynamics)

---

## Thermodynamic Ensembles

### Microcanonical Ensemble

**Definition**: Isolated system with fixed energy `E`, volume `V`, and number of particles `N`.

**Density of states**:
```
Ω(E) = Σ_s δ(E - E(s))
```

**Entropy** (Boltzmann):
```
S(E) = k_B ln Ω(E)
```

**Temperature**:
```
1/T = ∂S/∂E
```

**Application to POLLN**:
- Microstates: All `2^N` configurations of agent states `s_i ∈ {-1, +1}`
- Energy: `E = -J Σ_{<ij>} s_i s_j - h Σ_i s_i`
- Fixed energy shell: `E ∈ [E - ΔE, E + ΔE]`

### Canonical Ensemble

**Definition**: System in thermal bath at temperature `T`.

**Partition function**:
```
Z(T) = Σ_s exp(-βE(s))
```
where `β = 1/(k_B T)`.

**Boltzmann distribution**:
```
P(s) = exp(-βE(s)) / Z
```

**Free energy** (Helmholtz):
```
F = -k_B T ln Z
```

**Internal energy**:
```
U = ⟨E⟩ = -∂ ln Z / ∂β
```

**Entropy**:
```
S = -∂F/∂T = k_B β² ∂ ln Z / ∂β
```

**Heat capacity**:
```
C = ∂U/∂T = k_B β² (⟨E²⟩ - ⟨E⟩²)
```

**Fluctuation-dissipation theorem**:
```
⟨δE²⟩ = k_B T² C
```

### Grand Canonical Ensemble

**Definition**: System exchanging energy and particles with reservoir.

**Grand partition function**:
```
Ξ(T, μ) = Σ_N exp(βμN) Z_N(T)
```

**Average particle number**:
```
⟨N⟩ = (1/β) ∂ ln Ξ / ∂μ
```

**Fugacity**:
```
z = exp(βμ)
```

**Application to POLLN**:
- Variable colony size (agents can spawn/terminate)
- Chemical potential `μ` controls population

---

## Partition Functions

### Ising Model Partition Function

**Hamiltonian**:
```
H = -J Σ_{<ij>} s_i s_j - h Σ_i s_i
```

**Partition function**:
```
Z = Σ_{s_i=±1} exp(βJ Σ_{<ij>} s_i s_j + βh Σ_i s_i)
```

### Mean Field Approximation

**Approximation**: `⟨s_i s_j⟩ ≈ ⟨s_i⟩⟨s_j⟩ = m²`

**Effective Hamiltonian**:
```
H_MF = -Jzm Σ_i s_i - h Σ_i s_i
```
where `z` is coordination number.

**Partition function**:
```
Z_MF = [2 cosh(β(Jzm + h))]^N
```

**Self-consistent equation**:
```
m = tanh(β(Jzm + h))
```

### Exact Solution (1D Ising)

**Transfer matrix method**:
```
Z = λ_+^N + λ_-^N
```

where:
```
λ_± = exp(βJ) cosh(βh) ± sqrt(exp(2βJ) sinh²(βh) + exp(-2βJ))
```

For `h = 0`:
```
Z = 2^N cosh^N(βJ)
```

**No phase transition in 1D** (Mermin-Wagner theorem for `T > 0`).

### Onsager Solution (2D Ising)

**Critical temperature**:
```
k_B T_c / J = 2 / ln(1 + sqrt(2)) ≈ 2.269
```

**Free energy per spin** (for `h = 0`):
```
f(T) = -k_B T [ln(2)/2 + (1/2π) ∫_0^π dθ ln(cosh²(2βJ) - sinh(2βJ) cos θ)]
```

**Spontaneous magnetization** (`T < T_c`):
```
M(T) = [1 - sinh^{-4}(2βJ)]^{1/8}
```

---

## Landau Theory

### Free Energy Expansion

**Landau free energy density**:
```
f(M) = f_0 + a(T - T_c)M² + bM⁴ + cM⁶ + ... - hM
```

**Coefficients**:
- `a > 0`: Material constant
- `b > 0`: Stability (for second-order)
- `c`: Tricritical point parameter

### Equilibrium Order Parameter

**Minimize**: `∂f/∂M = 0`

```
2a(T - T_c)M + 4bM³ + 6cM⁵ - h = 0
```

**For `h = 0`**:
```
M[a(T - T_c) + 2bM² + 3cM⁴] = 0
```

**Solutions**:
1. `M = 0` (disordered phase)
2. `M² = [-a(T - T_c) ± sqrt(a²(T - T_c)² - 4ab)]/(4b)` (ordered)

### Critical Temperature

**Mean field**: `k_B T_c = Jz`

**Landau**: Defined by coefficient of `M²` vanishing.

### Critical Exponents from Landau

**Order parameter** (`T < T_c`, `h = 0`):
```
M = sqrt[a(T_c - T)/(2b)] ∝ (T_c - T)^{1/2}
```
→ `β = 1/2`

**Susceptibility** (`T > T_c`):
```
χ = ∂M/∂h|_{h→0} = 1/[2a(T - T_c)] ∝ (T - T_c)^{-1}
```
→ `γ = 1`

**Critical isotherm** (`T = T_c`):
```
h = 4bM³ ∝ M³
```
→ `δ = 3`

**Heat capacity**:
```
C = -T ∂²f/∂T²
```
Discontinuity at `T_c` → `α = 0`

---

## Critical Exponents

### Definition

**Heat capacity**:
```
C ∝ |T - T_c|^{-α} (for T ≠ T_c)
```

**Order parameter**:
```
M ∝ (T_c - T)^{β} (for T < T_c)
```

**Susceptibility**:
```
χ ∝ |T - T_c|^{-γ} (for T ≠ T_c)
```

**Critical isotherm**:
```
h ∝ M^{δ} (at T = T_c)
```

**Correlation length**:
```
ξ ∝ |T - T_c|^{-ν}
```

**Correlation function** (at `T_c`):
```
G(r) ∝ r^{-(d-2+η)}
```

### 2D Ising (Exact)

- `α = 0` (logarithmic divergence)
- `β = 1/8`
- `γ = 7/4`
- `δ = 15`
- `ν = 1`
- `η = 1/4`

### 3D Ising (Numerical)

- `α = 0.110(1)`
- `β = 0.326(3)`
- `γ = 1.237(2)`
- `δ = 4.789(2)`
- `ν = 0.630(1)`
- `η = 0.036(1)`

### Mean Field

- `α = 0`
- `β = 1/2`
- `γ = 1`
- `δ = 3`
- `ν = 1/2`
- `η = 0`

---

## Scaling Relations

### Rushbrooke Scaling

```
α + 2β + γ = 2
```

**Derivation**: Thermodynamic identity `C = T(∂S/∂T)` with scaling `S ∝ ξ^{-d}`.

### Widom Scaling

```
γ = β(δ - 1)
```

**Derivation**: Equation of state scaling `h = M^{δ} f(t/M^{1/β})`.

### Fisher Scaling

```
γ = ν(2 - η)
```

**Derivation**: Fluctuation-dissipation `χ ∝ ∫ G(r) d^d r` with `G(r) ∝ r^{-(d-2+η)}`.

### Josephson Scaling (Hyperscaling)

```
α = 2 - νd
```

**Derivation**: `C ∝ ξ^{-d}` and `ξ ∝ |t|^{-ν}`.

### Correlation Scaling

```
ν = γ/(2 - η)
```

**Derivation**: From Fisher scaling.

---

## Renormalization Group

### Momentum Shell Integration (Wilson)

**Hamiltonian** (φ⁴ theory):
```
H = ∫ d^d r [ (∇φ)²/2 + rφ²/2 + uφ⁴/4 ]
```

**Momentum modes**: `0 < |k| < Λ` (cutoff)

**RG step**:
1. Integrate out high-momentum modes: `Λ/b < |k| < Λ`
2. Rescale momenta: `k' = bk`
3. Rescale fields: `φ'(k') = b^{-(d+2)/2} φ(k)`

**Beta function** (one-loop):
```
β(u) = (4 - d)u - (3/16π²)u² + O(u³)
```

### Fixed Points

**Gaussian fixed point**:
```
u* = 0
```

**Wilson-Fisher fixed point**:
```
u* = (4 - d)16π²/3 = (ε/3)(16π²)
```
where `ε = 4 - d`.

### Stability Analysis

**Linearize** around fixed point:
```
du/dl = β(u) ≈ β(u*) + β'(u*)(u - u*)
```

**Eigenvalue**: `λ = β'(u*)`

- `λ > 0`: Unstable (relevant)
- `λ < 0`: Stable (irrelevant)
- `λ = 0`: Marginal

### Epsilon Expansion

**Critical exponents** in `d = 4 - ε`:

**Correlation length exponent**:
```
ν = 1/2 + ε/12 + ε²/162 + O(ε³)
```

**Anomalous dimension**:
```
η = ε²/54 + O(ε³)
```

**Other exponents** (from scaling):
```
α = 2 - νd
β = (d - 2 + η)ν/2
γ = (2 - η)ν
δ = (d + 2 - η)/(d - 2 + η)
```

### Real-Space RG

**Block spin transformation**:
```
s_I' = sign(Σ_{i∈I} s_i)
```

**Decimation** (1D):
```
s_i' = s_{2i}
```

**Migdal-Kadanoff approximation**:
```
K' = (1/4) ln[cosh(4K)]
```

---

## Mean Field Theory

### Curie-Weiss Model

**Hamiltonian** (infinite-range):
```
H = -(J/N) Σ_{i,j} s_i s_j - h Σ_i s_i
```

**Partition function**:
```
Z = Σ_{s_i} exp(βJNm²/2 + βhNm)
```
where `m = (1/N) Σ_i s_i`.

**Saddle point approximation**:
```
Z ≈ ∫ dm exp(-Nβf(m))
```

**Free energy density**:
```
f(m) = (J/2)m² - (k_B T/2)[(1+m)ln(1+m) + (1-m)ln(1-m)] - hm
```

**Self-consistent equation**:
```
m = tanh[β(Jm + h)]
```

### Critical Temperature

**Curie-Weiss**:
```
k_B T_c = Jz
```
where `z = N - 1` for infinite-range.

### Ginzburg Criterion

**Mean field valid when**:
```
G = (ξ/a)^d (k_B T/J) << 1
```

**Upper critical dimension**: `d_u = 4`

**For d < 4**: Fluctuations important, mean field fails.

### Bethe Approximation

**Cavity fields** `x_i`:
```
x_i = (1/2) ln[tanh(β(J + Σ_{j∈∂i} x_j)) / tanh(β(-J + Σ_{j∈∂i} x_j))]
```

**Critical temperature**:
```
k_B T_c = 2J / ln[z/(z-2)]
```

---

## Nonequilibrium Dynamics

### Master Equation

**General form**:
```
dP(C)/dt = Σ_{C'} [W(C'→C)P(C') - W(C→C')P(C)]
```

**Stationary solution**:
```
W P_ss = 0
```

**Detailed balance**:
```
W(C'→C)P_eq(C') = W(C→C')P_eq(C)
```

### Metropolis Dynamics

**Transition rate**:
```
W(C'→C) = min(1, exp[-β(E(C) - E(C'))])
```

**Satisfies detailed balance** with Boltzmann distribution.

### Glauber Dynamics

**Transition rate**:
```
W(C'→C) = 1 / [1 + exp(β(E(C) - E(C')))]
```

**Also satisfies detailed balance**.

### Fokker-Planck Equation

**For continuous variable x**:
```
∂P(x,t)/∂t = -∂[μ(x)P]/∂x + (∂²/∂x²)[D(x)P]
```

**Drift coefficient**: `μ(x) = F(x)/γ`

**Diffusion coefficient**: `D = k_B T/γ`

**Steady state** (Boltzmann):
```
P_ss(x) ∝ exp[-U(x)/k_B T]
```

### Langevin Equation

**Stochastic differential equation**:
```
dx/dt = -∇U(x) + sqrt(2k_B T/γ) η(t)
```

**Noise correlation**:
```
⟨η(t)η(t')⟩ = δ(t - t')
```

### Linear Response Theory

**Response function**:
```
χ(t) = β dC(t)/dt (for t > 0)
```

**Fluctuation-dissipation theorem**:
```
χ = β⟨δA²⟩
```

**Kramers-Kronig relations**:
```
χ''(ω) = (2ω/π) P ∫_0^∞ χ'(ω')/(ω'² - ω²) dω'
```

---

## Applications to POLLN

### Mapping

| Physical System | POLLN Agent Colony |
|----------------|-------------------|
| Spin `s_i` | Agent state |
| Coupling `J` | Hebbian weight |
| Field `h` | External pressure |
| Temperature `T` | Exploration rate |
| Magnetization `M` | Consensus |
| Energy `E` | Cost function |

### Predictions

1. **Critical colony size**: `N_min ≈ 100` for sharp transition
2. **Optimal operation**: `T/T_c ≈ 1.2` for stability
3. **Relaxation time**: `τ ∝ N` (Metropolis dynamics)
4. **Finite-size shift**: `T_c(N) ≈ T_c(∞) - AN^{-1/ν}`

### Design Principles

1. **Large colonies** (`N > 100`): Sharp phase transitions
2. **Strong coupling** (`J > 0.01`): Lower `T_c`
3. **Temperature control**: Phase switching
4. **Avoid criticality**: Unless studying critical phenomena

---

**References**: See main README for complete bibliography.

**Last Updated**: 2026-03-07
