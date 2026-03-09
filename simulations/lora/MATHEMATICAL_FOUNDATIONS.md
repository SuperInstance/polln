# Mathematical Foundations of LoRA Composition

This document provides the rigorous mathematical foundation for POLLN's LoRA Library concept and the validation simulations.

## Core Mathematical Framework

### LoRA Decomposition

For a neural network layer with weight matrix W ∈ ℝ^(d×d), LoRA expresses a fine-tuned model as:

```
W' = W_frozen + ΔW = W_frozen + BA
```

Where:
- W_frozen ∈ ℝ^(d×d): Pre-trained frozen weights
- B ∈ ℝ^(d×r): Down-projection matrix
- A ∈ ℝ^(r×d): Up-projection matrix
- r << d: Low-rank dimension

**Parameter Count**: 2×r×d vs d² for full fine-tuning.

### Composition of Multiple LoRAs

When composing N LoRA adapters:

```
W_total = W_base + Σ(i=1 to N) w_i · (B_i @ A_i)
```

Where w_i ∈ ℝ are composition weights.

**Key Insight**: The sum of low-rank matrices is not guaranteed to be low-rank, but has bounded rank:

```
rank(Σ w_i B_i A_i) ≤ Σ rank(B_i A_i) = N·r
```

However, for compatible LoRAs, the effective rank is much lower due to subspace overlap.

---

## Hypothesis H1: Rank Decomposition

### Theoretical Statement

For expertise domain E with expert weights W_E, the perturbation ΔW = W_E - W_base has low-rank structure:

```
rank(ΔW) ≤ r_min(E)
```

**Claim**: r_min(E) ≈ 64 for most domains (code, writing, analysis, research).

### Mathematical Justification

1. **Spectral Decay**
   Empirical observation: Singular values of ΔW decay rapidly:

   ```
   σ_1 ≥ σ_2 ≥ ... ≥ σ_d
   σ_k / σ_1 ≈ exp(-λk) for some λ > 0
   ```

   This suggests top-k capture most information.

2. **Capture Efficiency**
   For rank-r approximation:

   ```
   ||ΔW - ΔW_r||_F / ||ΔW||_F = sqrt(Σ(i=r+1 to d) σ_i²) / sqrt(Σ(i=1 to d) σ_i²)
   ```

   For exponential decay, this is ≈ exp(-λr).

3. **Domain-Specific Structure**
   - **Code**: Structured syntax → low-rank
   - **Writing**: Smooth patterns → low-rank
   - **Analysis**: Mid-rank reasoning
   - **Research**: Higher-rank cross-domain connections

### Validation Methodology

**Metric**: Reconstruction error
```python
error(r) = ||ΔW - B_r A_r||_F / ||ΔW||_F
```

**Success Criterion**: Find r_95 such that error(r_95) ≤ 0.05 (95% variance captured).

### Expected Results

| Domain | Expected r_95 | Expected r_99 |
|--------|---------------|---------------|
| Code   | 32-48        | 48-64        |
| Writing| 48-64        | 64-80        |
| Analysis| 56-72      | 72-96        |
| Research| 64-80      | 80-128       |

---

## Hypothesis H2: Composition Linearity

### Theoretical Statement

For compatible LoRAs L_1, L_2:

```
(L_1 ⊕ L_2)(x) ≈ L_1(x) + L_2(x) - L_1∩L_2(x)
```

Where L_1∩L_2 represents the interference term.

### Compatibility Condition

Two LoRAs are compatible if their perturbation subspaces have small overlap:

```
γ(L_1, L_2) = ||U_1^T U_2||_F / r < threshold
```

Where U_i are top-r singular vectors of B_i A_i.

### Linearity Error Analysis

**Decomposition**:
```
L_1 ⊕ L_2 = W_base + w_1 B_1 A_1 + w_2 B_2 A_2
```

**Linearity breakdown occurs when**:
1. Subspaces overlap significantly
2. Higher-order interactions emerge
3. Gradient conflicts occur during training

### Quantifying Interference

**Weight-level interference**:
```
I_weight = corr(vec(B_1 A_1), vec(B_2 A_2))
```

**Gradient-level interference**:
```
I_gradient = E[cos(∇_1 L, ∇_2 L)]
```

**Performance interference**:
```
I_perf = perf(L_1) - perf(L_1 ⊕ L_2)
```

### Non-linear Composition

When linearity breaks down, use gating:

```
W_total = W_base + Σ g_i(x) · B_i A_i
```

Where g_i(x) are learned gating functions.

---

## Hypothesis H3: Library Efficiency

### Theoretical Statement

LoRA library is more parameter-efficient than single large model when:

```
N · 2 · r · d < S_large - S_base
```

Where:
- N: Number of LoRAs
- r: Rank per LoRA
- d: Model dimension
- S_large: Large model parameters
- S_base: Base model parameters

### Break-even Analysis

**Parameter comparison**:
```
S_library = S_base + N · 2 · r · d
S_single = S_large
```

**Performance comparison** (using scaling laws):
```
acc_library = a + b·log(S_library) + c·N - d·I
acc_single = a + b·log(S_single)
```

**Break-even condition**:
```
acc_library ≥ acc_single
⇒ c·N - d·I ≥ b·log(S_single / S_library)
```

### Efficiency Frontier

The efficiency frontier is where:

```
∂acc_library/∂N = ∂acc_library/∂r
```

This gives optimal (N*, r*) for fixed parameter budget.

### Communication Efficiency

For distributed systems, LoRA library has communication advantage:

```
Comm_single = O(S_large)
Comm_library = O(S_base) + N·O(2·r·d)
```

With caching and reuse:
```
Comm_library_effective ≈ O(S_base) + O(2·r·d)
```

---

## Composition Optimization

### Optimal Weights (L2 Regularized)

**Problem**:
```
min_w ||W_target - W_base - Σ w_i B_i A_i||²_F + λ Σ w_i²
```

**Closed-form solution**:
```
w* = (X^T X + λI)^(-1) X^T y
```

Where:
- X = [vec(B_1 A_1), ..., vec(B_N A_N)]
- y = vec(W_target - W_base)

### Weighting Heuristics

1. **Uniform**: w_i = 1/N
   - Simple, no prior knowledge

2. **Inverse Square Root**: w_i = 1/√N
   - Accounts for interference
   - Theoretical justification from random matrix theory

3. **Rank-weighted**: w_i ∝ rank_i
   - Higher capacity → higher weight

4. **Norm-weighted**: w_i ∝ ||B_i A_i||_F
   - Larger effect → higher weight

5. **Learned**: Optimize via gradient descent
   - Most flexible, requires validation data

### Composition Strategies

**Sequential**: Apply LoRAs one after another
```
W_0 = W_base
W_{i+1} = W_i + w_{i+1} B_{i+1} A_{i+1}
```

**Parallel**: Apply all at once
```
W_total = W_base + Σ w_i B_i A_i
```

**Hierarchical**: Compose groups, then combine
```
W_group1 = W_base + Σ(i∈G1) w_i B_i A_i
W_group2 = W_base + Σ(i∈G2) w_i B_i A_i
W_total = W_group1 + W_group2 - W_base
```

---

## Scaling Laws

### General Form

```
accuracy = a + b·log(S) + c·N - d·I(N)
```

Where:
- S: Total parameters
- N: Number of LoRAs
- I(N): Interference penalty (typically ~ αN)

### Coefficient Interpretation

- **a**: Base performance (intercept)
- **b**: Returns to scale (log parameters)
- **c**: Complementarity benefit (per LoRA)
- **d**: Interference penalty coefficient

### Diminishing Returns

**Marginal benefit of Nth LoRA**:
```
∂accuracy/∂N = c - d·∂I/∂N
```

Set to zero for optimal N:
```
c = d·∂I/∂N*
```

For linear interference I = αN:
```
N* = c / (d·α)
```

### Model Size vs LoRA Count

**Trade-off**:
```
acc(S_base + 2Nrd, N) vs acc(S_large, 0)
```

**Optimal frontier**: Solve for S_large, N such that:
```
acc(S_base + 2Nrd, N) = acc(S_large, 0)
```

---

## Simulation Validation Strategy

### Phase 1: Rank Sufficiency

1. Generate synthetic expert models for each domain
2. Compute SVD of ΔW = W_expert - W_base
3. Measure reconstruction error vs rank
4. Find r_95, r_99 for each domain
5. Validate H1

### Phase 2: Interference Detection

1. Generate LoRA pairs across domain combinations
2. Compute weight correlation, subspace overlap
3. Measure gradient conflicts
4. Train interference predictor
5. Validate prediction accuracy

### Phase 3: Composition Optimization

1. Generate scenarios with N LoRAs
2. Compare weighting strategies
3. Test linearity assumption
4. Optimize non-linear composition
5. Validate 1/√N heuristic

### Phase 4: Scaling Laws

1. Generate diverse (S, N, r) configurations
2. Fit scaling law coefficients
3. Compute break-even curves
4. Find optimal configurations
5. Derive efficiency conditions

---

## Theoretical Proofs Targeted

### Theorem 1: Rank Decomposition Bound

**Statement**: For expertise E captured by LoRA of rank r:

```
||W_E - W_base - BA||_F / ||W_E - W_base||_F ≤ ε
```

where r = O(log(1/ε)) for structured domains.

**Proof Sketch**:
1. Singular values decay exponentially for structured perturbations
2. Rank-r approximation captures 1 - exp(-λr) fraction of variance
3. For ε = 0.05, need r ≈ log(1/ε)/λ ≈ O(log(1/ε))

### Theorem 2: Composition Linearity

**Statement**: For compatible LoRAs with interference γ < threshold:

```
(L_1 ⊕ L_2)(x) = L_1(x) + L_2(x) + O(γ)
```

**Proof Sketch**:
1. Expand W_total = W_base + w_1 B_1 A_1 + w_2 B_2 A_2
2. Linear term: L_1(x) + L_2(x)
3. Error term depends on subspace overlap γ
4. For small γ, higher-order terms are negligible

### Theorem 3: Library Efficiency

**Statement**: LoRA library outperforms single model when:

```
N · 2 · r · d < S_large - S_base
and c·N > d·αN + b·log(S_large/S_library)
```

**Proof Sketch**:
1. Parameter count: direct comparison
2. Performance: Use scaling law
3. Combine for break-even condition

### Theorem 4: Optimal Composition

**Statement**: L2-regularized composition has closed-form solution:

```
w* = (X^T X + λI)^(-1) X^T y
```

**Proof Sketch**:
1. Set gradient of objective to zero
2. ∇_w ||y - Xw||² + λw² = 0
3. Solve: -2X^T(y - Xw) + 2λw = 0
4. w* = (X^T X + λI)^(-1) X^T y

---

## References

1. **LoRA Paper**: Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", 2021
2. **Scaling Laws**: Kaplan et al., "Scaling Laws for Neural Language Models", 2020
3. **Composition**: Houlsby et al., "Parameter-Efficient Transfer Learning for NLP", 2019
4. **Interference**: Mirzadeh et al., "Understanding Interference in Language Model Fine-tuning", 2024

---

## Implementation Notes

### Numerical Stability

- Use SVD for decomposition (not random projection)
- Normalize matrices before computing correlations
- Add small ε (1e-8) to denominators

### Computational Efficiency

- Cache SVD results for multiple ranks
- Use incremental SVD for large matrices
- Batch operations for multiple LoRAs

### Statistical Validation

- Use multiple random seeds
- Report mean ± std across runs
- Statistical significance testing (t-test, ANOVA)
- Cross-validation for learned models

---

*This document provides the mathematical foundation for the LoRA composition validation simulations. For implementation details, see the individual module files.*
