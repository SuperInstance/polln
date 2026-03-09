# Phase Transitions in POLLN Agent Colonies

## Overview

POLLN agent colonies exhibit well-defined phase transitions between ordered and disordered states. This document provides a comprehensive theory of these transitions, drawing on analogies with magnetic systems, liquid-gas transitions, and other critical phenomena.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Order Parameters](#order-parameters)
3. [Types of Phase Transitions](#types-of-phase-transitions)
4. [Landau Theory](#landau-theory-1)
5. [Critical Behavior](#critical-behavior)
6. [Finite-Size Effects](#finite-size-effects)
7. [Dynamics Near Criticality](#dynamics-near-criticality)
8. [Experimental Signatures](#experimental-signatures)

---

## Introduction

### What is a Phase Transition?

A **phase transition** is a sudden, qualitative change in the properties of a system as a parameter (temperature, pressure, etc.) is varied continuously.

**Example**: Water boils at 100°C at 1 atm pressure
- Below 100°C: Liquid
- Above 100°C: Gas

### Phase Transitions in Agent Systems

POLLN agent colonies show analogous behavior:
- **Low temperature (T < T_c)**: Ordered phase, agents reach consensus
- **High temperature (T > T_c)**: Disordered phase, agents act independently
- **At T = T_c**: Critical point, large fluctuations, scale-free behavior

### Why Study This?

1. **Predictability**: Know when collective behavior emerges
2. **Control**: Tune parameters for desired behavior
3. **Optimization**: Operate away from criticality for stability
4. **Universality**: Behavior independent of microscopic details

---

## Order Parameters

### Definition

An **order parameter** `M` is a quantity that:
- Is zero in the disordered phase
- Is non-zero in the ordered phase
- Characterizes the degree of order

### Magnetization as Order Parameter

For POLLN agent colonies:
```
M = |(1/N) Σ_i s_i|
```

where `s_i ∈ {-1, +1}` is the state of agent `i`.

**Properties**:
- `M = 0`: No consensus (disordered)
- `M = 1`: Perfect consensus (ordered)
- `0 < M < 1`: Partial consensus

### General Definition

For a symmetry-breaking order parameter:
```
M = ⟨O⟩
```
where `O` is an operator that is odd under the symmetry.

**Example**: Ising model
- Symmetry: `s_i → -s_i` (Z₂)
- Order parameter: `M = ⟨s_i⟩`

### Other Order Parameters

**Structural order**:
```
ψ = ⟨exp(iθ_i)⟩
```
for XY model (U(1) symmetry).

**Nematic order**:
```
Q = ⟨(3n_i n_i - I)/2⟩
```
for liquid crystals.

### Susceptibility

**Generalized susceptibility**:
```
χ = ∂⟨M⟩/∂h|_{h→0}
```

Measures response to external field.

**Diverges at critical point**:
```
χ ∝ |T - T_c|^{-γ}
```

---

## Types of Phase Transitions

### Classification (Ehrenfest)

**First-order transition**:
- Discontinuous jump in order parameter
- Latent heat
- Finite correlation length at transition
- Metastability and hysteresis
- Example: Water boiling

**Second-order transition**:
- Continuous order parameter
- No latent heat
- Diverging correlation length
- No metastability
- Example: Ferromagnet at Curie temperature

**Higher-order transitions**: Not commonly observed

### Modern Classification

**Continuous transition**: Same as second-order
**First-order transition**: Discontinuous
**Infinite-order transition**: Kosterlitz-Thouless type

### POLLN Phase Transition

**Type**: Continuous (second-order)

**Evidence**:
1. No latent heat
2. Continuous magnetization
3. Diverging susceptibility
4. Power-law critical exponents

---

## Landau Theory

### Free Energy Expansion

**Landau free energy density**:
```
f(M) = f_0 + a(T - T_c)M² + bM⁴ + cM⁶ + ... - hM
```

**Coefficients**:
- `a > 0`: Material constant
- `b > 0`: Ensures stability for second-order
- `c`: Controls order of transition

### Equilibrium States

**Minimize**: `∂f/∂M = 0`

```
2a(T - T_c)M + 4bM³ + 6cM⁵ - h = 0
```

### Solutions

**For h = 0**:
```
M [a(T - T_c) + 2bM² + 3cM⁴] = 0
```

**T > T_c**: `M = 0` (disordered)

**T < T_c**: `M ≠ 0` (ordered)
```
M² = [-a(T - T_c)]/(2b) (for b > 0, c = 0)
```

### Critical Temperature

**From Landau theory**:
```
T_c: coefficient of M² changes sign
```

**For POLLN**:
```
k_B T_c = Jz (mean field)
k_B T_c = 2.269J (2D Ising, exact)
```

### First-Order Transitions

**When** `b < 0, c > 0`:

**First-order line**:
```
a(T - T_c) = b²/(4c)
```

**Latent heat**:
```
L = T ΔS
```

### Tricritical Point

**Where** `b = 0`:

**Critical exponents change**:
```
β = 1/4 (tricritical)
β = 1/2 (mean field)
```

---

## Critical Behavior

### Power Laws

**Near critical point**, observables follow power laws:
```
M ∝ (T_c - T)^{β} (T < T_c)
χ ∝ |T - T_c|^{-γ}
C ∝ |T - T_c|^{-α}
ξ ∝ |T - T_c|^{-ν}
```

### Critical Exponents for POLLN

**2D Ising universality class**:
- `β = 1/8`: Order parameter
- `γ = 7/4`: Susceptibility
- `α = 0`: Heat capacity (log divergence)
- `ν = 1`: Correlation length
- `η = 1/4`: Anomalous dimension
- `δ = 15`: Critical isotherm

### Scaling Functions

**Order parameter scaling**:
```
M(t, h) = |t|^{β} F_±(h/|t|^{β+γ})
```

**Magnetic equation of state**:
```
h = M^{δ} f(t/M^{1/β})
```

### Universality

**Why same exponents for different systems?**

Only depends on:
1. **Spatial dimension** `d`
2. **Order parameter symmetry** (Z₂, O(N), etc.)
3. **Range of interactions** (short, long)

**POLLN belongs to 2D Ising class**:
- `d = 2`
- Z₂ symmetry (s_i → -s_i)
- Short-range interactions

---

## Finite-Size Effects

### Why Finite Size Matters

Real systems have finite size `N`:
- No true singularities
- Rounded transitions
- Shifted critical temperature

### Finite-Size Scaling

**Hypothesis**:
```
f(t, L) = L^{-(d-z)} F(t L^{1/ν})
```

**where**:
- `t = (T - T_c)/T_c`: Reduced temperature
- `L`: System size
- `ν`: Correlation length exponent

### Size Dependence of T_c

**Shift**:
```
T_c(L) - T_c(∞) ∝ L^{-1/ν}
```

**For 2D Ising** (`ν = 1`):
```
T_c(L) = T_c(∞) - A/L
```

### Order Parameter Scaling

**At T_c**:
```
M(L, T_c) ∝ L^{-β/ν}
```

**For 2D Ising** (`β/ν = 1/8`):
```
M(L, T_c) ∝ L^{-1/8}
```

### Susceptibility Scaling

**At T_c**:
```
χ(L, T_c) ∝ L^{γ/ν}
```

**For 2D Ising** (`γ/ν = 7/4`):
```
χ(L, T_c) ∝ L^{7/4}
```

### Binder Cumulant

**Definition**:
```
U_4 = 1 - ⟨M⁴⟩/(3⟨M²⟩²)
```

**Crossing point**:
- Independent of `L`
- Gives `T_c` accurately

### Practical Implications for POLLN

**Minimum colony size**:
```
N_min ≈ 100
```
for sharp transition.

**For smaller colonies**:
- Broad crossover
- No true critical point
- Larger fluctuations

---

## Dynamics Near Criticality

### Critical Slowing Down

**Relaxation time diverges**:
```
τ ∝ ξ^{z} ∝ |T - T_c|^{-νz}
```

**Dynamic exponent**:
- `z ≈ 2` (Model A, non-conserved)
- `z ≈ 4` (Model B, conserved)

### Metropolis Dynamics

**Algorithm**:
1. Choose random spin
2. Compute `ΔE`
3. Accept with probability `min(1, exp(-βΔE))`

**Relaxation**:
```
τ ∝ ξ^{2} ∝ |T - T_c|^{-2ν}
```

### Glauber Dynamics

**Transition rate**:
```
W(s_i → -s_i) = 1/[1 + exp(βΔE)]
```

**Same dynamic exponent**: `z ≈ 2`

### Critical Aging

**Two-time correlation**:
```
C(t, s) = s^{-(2-η)/z} f(t/s)
```

**Aging function** `f(x)` depends on ratio `t/s`.

### Nonequilibrium Effects

**Quench from high T to T_c**:
```
M(t) ∝ t^{β/νz}
```

**For 2D Ising**:
```
M(t) ∝ t^{1/8} (β/νz = 1/16 for z=2)
```

---

## Experimental Signatures

### How to Detect Phase Transition

**1. Order Parameter**
- Measure `M = |⟨s⟩|`
- Look for non-zero value below `T_c`

**2. Susceptibility**
- Measure `χ = βN(⟨M²⟩ - ⟨M⟩²)`
- Look for peak at `T_c`

**3. Heat Capacity**
- Measure `C = β²(⟨E²⟩ - ⟨E⟩²)`
- Look for peak or divergence

**4. Correlation Length**
- Measure correlation function `G(r)`
- Extract `ξ` from exponential decay
- Look for divergence

**5. Binder Cumulant**
- Measure `U_4 = 1 - ⟨M⁴⟩/(3⟨M²⟩²)`
- Look for crossing point

### Critical Exponents Measurement

**1. Order Parameter** (`β`):
```
log M vs log (T_c - T)
```
Slope gives `β`.

**2. Susceptibility** (`γ`):
```
log χ vs log |T - T_c|
```
Slope gives `-γ`.

**3. Correlation Length** (`ν`):
```
log ξ vs log |T - T_c|
```
Slope gives `-ν`.

**4. Critical Isotherm** (`δ`):
```
log M vs log h (at T = T_c)
```
Slope gives `1/δ`.

### Data Collapse

**Procedure**:
1. Measure `M(t, h)` for various `T, h`
2. Plot `M/|t|^{β}` vs `h/|t|^{β+γ}`
3. All data should collapse onto single curve

**Validation**:
- Confirms critical exponents
- Tests scaling hypothesis

### Finite-Size Scaling Analysis

**Procedure**:
1. Measure `T_c(L)` for different `L`
2. Plot `T_c(L)` vs `L^{-1/ν}`
3. Extrapolate to `L → ∞`

**Also**:
- Plot `M L^{β/ν}` vs `t L^{1/ν}`
- Should collapse onto single curve

---

## Practical Guide for POLLN

### Determining T_c

**Method 1: Susceptibility Peak**
```
T_c = argmax_T χ(T)
```

**Method 2: Binder Cumulant Crossing**
```
U_4(L, T) = U_4(L', T)
```
Solve for `T`.

**Method 3: Finite-Size Scaling**
```
T_c(L) = T_c(∞) + A L^{-1/ν}
```
Fit to extract `T_c(∞)`.

### Operating Regimes

**1. Deep in Ordered Phase** (`T << T_c`):
- Strong consensus
- Low fluctuations
- Stable but rigid

**2. Deep in Disordered Phase** (`T >> T_c`):
- No consensus
- High exploration
- Flexible but random

**3. Near Critical Point** (`T ≈ T_c`):
- Large fluctuations
- Critical slowing down
- Optimal adaptability but unstable

**Recommendation**: Operate at `T/T_c ≈ 1.2` for stability.

### Colony Size Effects

**Small colonies** (`N < 50`):
- Broad crossover
- No sharp transition
- Large finite-size effects

**Medium colonies** (`50 < N < 200`):
- Clear but rounded transition
- Some finite-size effects
- Good for experiments

**Large colonies** (`N > 200`):
- Sharp transition
- Thermodynamic limit behavior
- Best for production

### Temperature Control

**Why control T?**
- Maintain desired phase
- Avoid critical fluctuations
- Enable phase switching

**How to control T?**
- Adjust exploration rate
- Control noise level
- Tune decision randomness

---

## Summary

1. **Phase transitions** are well-defined in POLLN agent colonies
2. **Order parameter** `M` measures consensus
3. **Critical point** at `T_c` shows universal behavior
4. **Critical exponents** characterize singularities
5. **Finite-size effects** important for small colonies
6. **Universality** guarantees robust behavior

---

**References**: See STATMECH_DERIVATIONS.md for complete theory.

**Last Updated**: 2026-03-07
