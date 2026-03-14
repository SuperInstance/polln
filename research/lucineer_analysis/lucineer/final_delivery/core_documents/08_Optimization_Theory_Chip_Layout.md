# Optimization Theory for Chip Floorplanning and Resource Allocation
## Complete Mathematical Framework for SuperInstance.AI

**Document Version**: 1.0  
**Date**: March 2026  
**Classification**: Technical Reference Document  
**Author**: Optimization Theory Specialist

---

# Table of Contents

1. [Floorplanning Optimization Problem](#1-floorplanning-optimization-problem)
2. [Thermal-Aware Placement Equations](#2-thermal-aware-placement-equations)
3. [Memory Allocation Optimization](#3-memory-allocation-optimization)
4. [Yield Optimization Framework](#4-yield-optimization-framework)
5. [Power Distribution Optimization](#5-power-distribution-optimization)
6. [Routing Optimization](#6-routing-optimization)
7. [References and Solution Methods](#7-references-and-solution-methods)

---

# 1. Floorplanning Optimization Problem

## 1.1 Mixed-Integer Programming Formulation

### 1.1.1 Decision Variables

**Block Position Variables:**
```
Let B = {1, 2, ..., n} be the set of functional blocks

For each block i ∈ B:
  - (x_i, y_i) ∈ ℝ² : Lower-left corner coordinates
  - (w_i, h_i) ∈ ℝ² : Width and height (discrete choices)
  - r_i ∈ {0, 1} : Rotation flag (0 = original, 1 = rotated 90°)
  - m_i ∈ {0, 1, 2, 3} : Orientation for iFairy RAU (4 rotations)
```

**Effective dimensions after rotation:**
```
w̃_i = w_i · (1 - r_i) + h_i · r_i
h̃_i = h_i · (1 - r_i) + w_i · r_i
```

**Binary variables for non-overlap:**
```
For each pair (i, j) where i < j:
  - a_ij ∈ {0, 1} : i is to the left of j
  - b_ij ∈ {0, 1} : i is below j
  - c_ij ∈ {0, 1} : i is to the right of j  
  - d_ij ∈ {0, 1} : i is above j
```

### 1.1.2 Constraints

**Non-overlap Constraints:**
```
For all i < j:

x_i + w̃_i ≤ x_j + M · (1 - a_ij)     (i left of j)
y_i + h̃_i ≤ y_j + M · (1 - b_ij)     (i below j)
x_j + w̃_j ≤ x_i + M · (1 - c_ij)     (j left of i)
y_j + h̃_j ≤ y_i + M · (1 - d_ij)     (j below i)

a_ij + b_ij + c_ij + d_ij ≥ 1        (at least one must hold)

where M is a sufficiently large constant (Big-M method)
```

**Boundary Constraints:**
```
x_i ≥ 0                              ∀i ∈ B
y_i ≥ 0                              ∀i ∈ B
x_i + w̃_i ≤ W_die                    ∀i ∈ B
y_i + h̃_i ≤ H_die                    ∀i ∈ B
```

**Aspect Ratio Constraints:**
```
α_min · H_die ≤ W_die ≤ α_max · H_die
```

**Area Constraint:**
```
W_die · H_die ≤ A_max
```

**Timing Constraints (Critical Path):**
```
For each timing arc from block i to block j:

d_ij + δ_i + τ_ij ≤ T_clock         (setup time constraint)

where:
  d_ij = Manhattan distance between i and j
  δ_i = intrinsic delay of block i
  τ_ij = propagation delay on wire between i and j
  T_clock = clock period
```

**Wirelength Estimation:**
```
For each net k connecting blocks {i₁, i₂, ..., i_m}:

HPWL_k = (max_i x_i - min_i x_i) + (max_i y_i - min_i y_i)

Total: WL = Σ_k HPWL_k
```

### 1.1.3 Objective Function

**Multi-objective Formulation:**
```
minimize:  λ₁ · (W_die · H_die)           // Area
         + λ₂ · WL                         // Wirelength
         + λ₃ · P_thermal                  // Thermal penalty
         + λ₄ · Y_loss                     // Yield loss

subject to all constraints above

where λ₁, λ₂, λ₃, λ₄ are Pareto weights
```

### 1.1.4 Complete MIP Formulation

$$
\begin{aligned}
\min \quad & \lambda_1 \cdot A_{die} + \lambda_2 \cdot \sum_{k \in N} HPWL_k + \lambda_3 \cdot P_{thermal} + \lambda_4 \cdot Y_{loss} \\
\text{s.t.} \quad & x_i \geq 0, \quad y_i \geq 0 \quad \forall i \in B \\
& x_i + \tilde{w}_i \leq W_{die} \quad \forall i \in B \\
& y_i + \tilde{h}_i \leq H_{die} \quad \forall i \in B \\
& x_i + \tilde{w}_i \leq x_j + M(1 - a_{ij}) \quad \forall i < j \\
& y_i + \tilde{h}_i \leq y_j + M(1 - b_{ij}) \quad \forall i < j \\
& a_{ij} + b_{ij} + c_{ij} + d_{ij} \geq 1 \quad \forall i < j \\
& \alpha_{min} \leq \frac{W_{die}}{H_{die}} \leq \alpha_{max} \\
& \text{Timing constraints} \\
& \text{Thermal constraints}
\end{aligned}
$$

## 1.2 Slicing Tree Representation (Alternative)

For hierarchical floorplanning with guaranteed non-overlap:

```
Slicing Tree:
  - Internal nodes: {H, V} representing horizontal/vertical cuts
  - Leaf nodes: Block identifiers
  - Each cut has an associated position (ratio of parent dimension)

Encoding: Polish expression (post-order traversal)

Example: 12H3V4H = 
  Vertical slice of (Horizontal slice of 1,2) and (Horizontal slice of 3,4)
```

**Slicing Tree Optimization:**
```
minimize:  Area + α · Wirelength + β · AspectRatioDeviation

Decision variables:
  - Tree topology (discrete)
  - Cut positions r_i ∈ [0, 1] (continuous)

This is a mixed discrete-continuous optimization problem.
```

## 1.3 Sequence Pair Representation

**Definition:**
```
A sequence pair (Γ₊, Γ₋) encodes relative positions:
  - Γ₊ : Sequence of blocks
  - Γ₋ : Sequence of blocks

Relationships:
  - i precedes j in both → i is left of j
  - i precedes j in Γ₊ only → i is below j
  - i precedes j in Γ₋ only → i is above j
```

**Constraint Graph Formulation:**
```
Horizontal constraint graph G_H:
  - Edge i → j with weight w_i if i is left of j
  - Longest path gives x-coordinates

Vertical constraint graph G_V:
  - Edge i → j with weight h_i if i is below j
  - Longest path gives y-coordinates
```

---

# 2. Thermal-Aware Placement Equations

## 2.1 Thermal Model

### 2.1.1 Heat Equation Discretization

**Steady-state heat conduction:**
```
∇ · (k ∇T) + Q = 0

Discretized on uniform grid:
  k[(T_{i+1,j} - 2T_{i,j} + T_{i-1,j})/Δx² + (T_{i,j+1} - 2T_{i,j} + T_{i,j-1})/Δy²] + Q_{i,j} = 0
```

**Matrix form:**
```
A · T = Q

where:
  A = Thermal conductance matrix (sparse, symmetric positive definite)
  T = Temperature vector (unknown)
  Q = Power dissipation vector
```

### 2.1.2 Compact Thermal Model

**Resistor network equivalent:**
```
For each thermal node i:

(T_i - T_j)/R_{ij} + P_i = 0    ∀j ∈ neighbors(i)

In matrix form:
  G · T = P + T_amb · g_amb

where:
  G = Thermal conductance matrix
  P = Power vector
  T_amb = Ambient temperature
  g_amb = Vector of ambient conductances
```

**Block-level thermal model:**
```
For block i with power P_i:

T_i = T_amb + R_{th,i} · P_i + Σ_j R_{th,ij} · P_j

where:
  R_{th,i} = Self-heating thermal resistance
  R_{th,ij} = Coupling thermal resistance between blocks i and j
```

## 2.2 Thermal Cost Function

### 2.2.1 Temperature-Aware Wirelength

**Weighted wirelength:**
```
For each net k with pins {i₁, ..., i_m}:

HPWL_k^T = Σ_{p,q ∈ pins} w(T_p, T_q) · |x_p - x_q| + |y_p - y_q|

where w(T_p, T_q) = 1 + γ · max(T_p, T_q)/T_max

Higher temperature regions have higher routing cost.
```

### 2.2.2 Thermal Gradient Penalty

```
Thermal gradient penalty:

G_thermal = Σ_{adjacent cells i,j} (T_i - T_j)²

Minimizing this smooths temperature distribution.
```

### 2.2.3 Peak Temperature Constraint

```
T_peak = max_i T_i ≤ T_max

Soft constraint formulation:
  P_temp = max(0, T_peak - T_max)²

This is non-differentiable at T_peak = T_max.
Use log-sum-exp approximation:
  T_peak ≈ μ · log(Σ_i exp(T_i/μ))  as μ → 0
```

## 2.3 Gradient-Based Placement Optimization

### 2.3.1 Analytical Placement Formulation

**Quadratic placement with thermal:**
```
minimize:  Σ_{nets k} Σ_{pins i,j ∈ k} w_{ij} · [(x_i - x_j)² + (y_i - y_j)²]
         + α · Σ_i (T_i - T_target)²

The wirelength term is quadratic, temperature term is coupled through power density.
```

**Force-directed formulation:**
```
F_x = -∇_x WL + F_spreading + F_thermal

F_spreading: Forces to spread cells uniformly
  F_spreading = -β · (ρ(x,y) - ρ_target) · n̂

F_thermal: Force to move cells away from hot spots
  F_thermal = -γ · ∇T(x,y)
```

### 2.3.2 Optimization Algorithm

**Simulated Annealing for Thermal-Aware Placement:**

```
Algorithm: Thermal-Aware SA Placement

Input: Initial placement P₀, Initial temperature T_SA, Cooling schedule
Output: Optimized placement P*

1. P ← P₀
2. T_current ← T_SA
3. while not frozen:
4.   for iteration = 1 to L:
5.     P' ← Neighbor(P)  // Single cell move or swap
6.     ΔC ← Cost(P') - Cost(P)
7.     if ΔC < 0 or random() < exp(-ΔC/T_current):
8.       P ← P'
9.   T_current ← α · T_current  // Cooling
10. return P

Cost function:
  C(P) = λ₁ · WL(P) + λ₂ · Area(P) + λ₃ · Thermal(P) + λ₄ · Congestion(P)

Thermal cost:
  Thermal(P) = max_i T_i(P) + η · Σ_i T_i(P)²
```

### 2.3.3 Thermally-Aware Force Calculation

**Power density map:**
```
ρ_power(x,y) = Σ_{blocks i} P_i / (w_i · h_i) · 𝟙_{(x,y) ∈ block_i}
```

**Temperature-dependent timing derating:**
```
Delay multiplier: M_delay(T) = 1 + κ · (T - T_nom)

For timing-critical paths:
  τ_eff = τ_nom · M_delay(T)
```

## 2.4 Global vs. Detailed Placement Trade-offs

### 2.4.1 Global Placement

**Objective:** Find approximate positions minimizing wirelength and thermal

```
minimize:  WL + α · Thermal

Methods:
  1. Quadratic placement with spreading forces
  2. Force-directed placement
  3. Analytical placement (ePoise, APlace)
```

### 2.4.2 Detailed Placement

**Objective:** Legalize and refine global placement

```
minimize:  ΔWL + ΔThermal

subject to:
  - Row alignment
  - Site constraints
  - Non-overlap

Methods:
  1. Greedy cell swapping
  2. Optimal interleaving
  3. Branch-and-bound for small regions
```

### 2.4.3 Trade-off Analysis

| Aspect | Global Placement | Detailed Placement |
|--------|------------------|-------------------|
| **Runtime** | O(n log n) to O(n²) | O(n) to O(n²) |
| **Solution Quality** | Near-optimal | Local optimum |
| **Thermal Awareness** | Can include | Limited |
| **Scalability** | Good for large designs | Each block handled locally |

---

# 3. Memory Allocation Optimization

## 3.1 KV Cache SRAM Allocation Problem

### 3.1.1 Problem Definition

**Given:**
```
- Total die area A_total
- SRAM density D_SRAM (bits/mm²)
- KV cache requirement per token: B_token bytes
- Target context length L_ctx tokens
- Power budget P_budget
```

**Decision Variables:**
```
A_SRAM : Area allocated to SRAM
A_compute : Area allocated to compute
n_channels : Number of memory channels
C_bandwidth : External memory bandwidth
```

### 3.1.2 Knapsack Formulation

**Memory tier selection as knapsack:**

```
Items: Different memory configurations
  - Item j: (Capacity_j, Cost_j, Latency_j, Bandwidth_j)

Maximize: Total utility = Σ_j x_j · U_j

Subject to:
  Σ_j x_j · Cost_j ≤ Budget
  Σ_j x_j · Capacity_j ≥ KV_cache_requirement
  Σ_j x_j · Bandwidth_j ≥ Bandwidth_requirement
  x_j ∈ {0, 1}

where:
  U_j = w₁ · Capacity_j - w₂ · Latency_j + w₃ · Bandwidth_j
```

### 3.1.3 Assignment Problem for Multi-Tier Memory

**KV cache assignment to memory tiers:**

```
Let:
  T = {SRAM, LPDDR4, LPDDR5} : Memory tiers
  K = {k₁, k₂, ..., k_n} : KV cache segments (by recency)

Decision variables:
  x_{kt} ∈ {0,1} : Segment k assigned to tier t

Optimization:
  minimize: Σ_{k,t} x_{kt} · (α · Latency_t + β · Energy_t · Access_freq_k)
  
  subject to:
    Σ_t x_{kt} = 1                           ∀k ∈ K     (each segment assigned)
    Σ_k x_{kt} · Size_k ≤ Capacity_t         ∀t ∈ T     (capacity constraint)
    x_{kt} ∈ {0,1}                           ∀k,t

This is a Generalized Assignment Problem (GAP).
```

### 3.1.4 Streaming vs On-Chip Trade-off

**Mathematical Analysis:**

```
On-chip SRAM approach:
  - KV_Size = 2 × L × d × W × b
  - For W = 512, L = 24, d = 2560, b = 2:
    KV_Size = 125 MB (FP16) → 31 MB (INT4)
  - Area = 31 MB / D_SRAM ≈ 124 mm² at 28nm

Streaming approach (sliding window):
  - Fixed memory = 2 × L × d × W_sliding × b
  - Infinite context supported
  - Quality trade-off: Attention mass captured

Decision criterion:
  if A_SRAM_available > A_required_for_full_ctx:
      Use on-chip only
  elif Quality_acceptable(sliding_window):
      Use streaming
  else:
      Use hybrid SRAM + LPDDR
```

## 3.2 Optimal Partition of Die Area

### 3.2.1 Formulation

```
Variables:
  A_SRAM : SRAM area
  A_compute : Compute area  
  A_io : I/O pad area
  A_routing : Routing overhead

Constraint:
  A_SRAM + A_compute + A_io + A_routing ≤ A_die

Relationships:
  Throughput ∝ √A_compute         (systolic array)
  Context_len ∝ A_SRAM            (linear)
  Power ∝ A_compute + A_SRAM × access_rate

Multi-objective:
  maximize: [Throughput, Context_len, -Power]

Pareto frontier: Set of non-dominated (A_SRAM, A_compute) pairs
```

### 3.2.2 Lagrangian Relaxation

```
Original problem:
  maximize: Throughput(A_compute) + γ · Context(A_SRAM)
  subject to: A_SRAM + A_compute = A_available

Lagrangian:
  L(A_SRAM, A_compute, λ) = Throughput(A_compute) + γ · Context(A_SRAM) 
                           + λ · (A_available - A_SRAM - A_compute)

Optimality conditions:
  ∂L/∂A_SRAM = γ · ∂Context/∂A_SRAM - λ = 0
  ∂L/∂A_compute = ∂Throughput/∂A_compute - λ = 0
  
Solution:
  γ · ∂Context/∂A_SRAM = ∂Throughput/∂A_compute
  
At optimum: Marginal benefit per unit area is equal.
```

### 3.2.3 Specific Values for SuperInstance.AI

```
Given:
  A_die = 40 mm²
  D_SRAM = 6 Mbit/mm² = 0.75 MB/mm²
  Compute density = 1000 PE/mm² (at 150 gates/PE, 1.5M gates/mm²)

Compute area calculation:
  N_PE = 1024 PEs
  A_compute = 1024 / 1000 = 1.0 mm²

KV cache area calculation:
  Target: 512 context, INT4
  KV_Size = 42 MB / 4 = 10.5 MB (after INT4)
  A_SRAM = 10.5 / 0.75 = 14 mm²

Remaining:
  A_remaining = 40 - 1 - 14 = 25 mm²
  (Control, routing, pads, overhead)

Optimization:
  Increase context: +256 tokens → +14 mm² → exceeds die
  Increase compute: +512 PEs → +0.5 mm² → feasible
  
Decision: Keep 512 context, increase compute for higher throughput.
```

---

# 4. Yield Optimization Framework

## 4.1 Binning Strategy as Optimization Problem

### 4.1.1 Problem Definition

**Given:**
```
- N dies from production wafer
- Test results: {frequency_i, power_i, functionality_i}
- Market segments: {S_1, S_2, ..., S_m} with prices {p_1, ..., p_m}
- Segment requirements: {f_min_j, P_max_j, features_j}
```

**Decision:**
```
Assign each die i to exactly one segment j (or discard)
```

### 4.1.2 Mathematical Formulation

```
Binary decision variables:
  x_{ij} ∈ {0,1} : Die i assigned to segment j

Maximize revenue:
  R = Σ_i Σ_j x_{ij} · p_j

Subject to:
  Σ_j x_{ij} ≤ 1                              ∀i (each die at most one bin)
  
  x_{ij} = 0 if f_i < f_min_j                 ∀i,j (frequency requirement)
  x_{ij} = 0 if P_i > P_max_j                 ∀i,j (power requirement)
  
  Σ_i x_{ij} ≥ Demand_j                       ∀j (meet demand)
  
  x_{ij} ∈ {0,1}
```

### 4.1.3 Revenue Maximization Under Yield Constraints

**Yield model:**
```
Poisson defect model:
  Y = exp(-D_0 · A_die · (1 + (α · log(1/α))))

where:
  D_0 = Defect density (defects/cm²)
  A_die = Die area (cm²)
  α = Clustering parameter
```

**Bin-specific yield:**
```
Y_j = P(die meets requirements for segment j)

Y_j = Y_func · P(f ≥ f_min_j | functional) · P(P ≤ P_max_j | functional, f)
```

**Expected revenue:**
```
E[R] = N_total · Σ_j Y_j · p_j

If binning is optimal:
  E[R] = N_total · Σ_j (Y_j - Y_{j+1}) · p_j  (sorted by p_j)
```

### 4.1.4 Dynamic Programming for Tier Assignment

**State definition:**
```
DP(i, d₁, d₂, ..., d_m) : Maximum revenue from dies 1..i 
                           with d_j assigned to segment j

Recurrence:
  DP(i, d₁, ..., d_m) = max over all valid j:
    DP(i-1, d₁, ..., d_j-1, ..., d_m) + p_j
  
  where valid j satisfies:
    - die i meets segment j requirements
    - d_j < Demand_j

Base case:
  DP(0, 0, ..., 0) = 0

Answer:
  max_{d_j ≤ Demand_j} DP(N, d₁, ..., d_m)
```

**Complexity reduction:**
```
For large N, use greedy approximation:
  1. Sort dies by "quality score" Q_i
  2. For each die i (highest quality first):
     - Assign to highest-price segment j where requirements are met
     - And demand not yet satisfied
```

## 4.2 Pareto Frontier of Yield vs Revenue

### 4.2.1 Trade-off Curve

```
Points on Pareto frontier:
  (Yield, Revenue) pairs where:
  - Cannot increase yield without decreasing revenue
  - Cannot increase revenue without decreasing yield

Compute via parametric optimization:
  max Revenue
  s.t. Yield ≥ Y_target

  Vary Y_target from 0 to Y_max
```

### 4.2.2 SuperInstance.AI Binning Example

```
Segments:

| Segment | Price | f_min (MHz) | P_max (W) | Context |
|---------|-------|-------------|-----------|---------|
| Premium | $69   | 280         | 2.5       | 2048    |
| Standard| $49   | 250         | 3.0       | 1024    |
| Value   | $35   | 200         | 4.0       | 512     |

Yield estimates (at 28nm, 40 mm²):
  Y_Premium = 60%  (aggressive frequency)
  Y_Standard = 80% (nominal frequency)
  Y_Value = 95%    (relaxed frequency)
  
Optimal binning:
  - Dies with f ≥ 280 MHz → Premium (60%)
  - Dies with 250 ≤ f < 280 MHz → Standard (20%)
  - Dies with 200 ≤ f < 250 MHz → Value (15%)
  - Dies with f < 200 MHz → Discard (5%)

Expected revenue per 100 dies:
  R = 60 × $69 + 20 × $49 + 15 × $35 = $4,140 + $980 + $525 = $5,645
  
Average revenue per die: $56.45
```

---

# 5. Power Distribution Optimization

## 5.1 Power Grid Sizing Problem

### 5.1.1 Network Model

**Power grid as resistive network:**
```
Nodes: {VDD source, tap points, load points}
Edges: Metal segments with resistance R_ij

At each load point k:
  I_k = Current draw
  V_k = Voltage at load
```

**Kirchhoff's laws:**
```
Current balance at node i:
  Σ_j (V_i - V_j)/R_ij = I_i

In matrix form:
  G · V = I

where G is the conductance matrix (graph Laplacian with conductances)
```

### 5.1.2 IR Drop Minimization

**Optimization formulation:**
```
Variables:
  w_e : Width of power grid edge e

Minimize: Total metal area
  Σ_e w_e · L_e

Subject to:
  V_k ≥ VDD - IR_max            ∀ load points k
  w_min ≤ w_e ≤ w_max           ∀ edges e
  Current density: I_e/w_e ≤ J_max  ∀ edges e

This is a convex optimization problem (specifically, a Second-Order Cone Program)
```

**Sensitivity-based approach:**
```
IR drop sensitivity to width change:
  ∂V_k/∂w_e = -I_e² · R_e / (w_e² · V_k)

Greedy optimization:
  1. Solve for voltages with current widths
  2. Identify load with worst IR drop
  3. Increase width of edge with highest sensitivity
  4. Repeat until all IR constraints satisfied
```

### 5.1.3 Electromigration Constraints

```
Mean Time To Failure (MTTF):
  MTTF = A · (J · w)^{-n} · exp(E_a / kT)

where:
  J = Current density
  w = Wire width
  n = 1.5-2 (empirical)
  E_a = Activation energy

Constraint:
  MTTF ≥ 10 years
  → J · w ≤ J_crit
  
For wire carrying current I:
  I/w ≤ J_crit
  w ≥ I/J_crit
```

## 5.2 Decap Placement Optimization

### 5.2.1 Problem Definition

```
Given:
  - Power grid with N nodes
  - Current waveforms I_i(t) at each load
  - M potential decap locations
  - Total decap budget C_total

Decision:
  - Decap value c_j at each candidate location j

Objective:
  Minimize peak voltage droop: max_{i,t} |VDD - V_i(t)|
```

### 5.2.2 Convex Formulation

**Frequency domain analysis:**
```
Impedance at node i:
  Z_i(f) = V_i(f) / I_i(f)

With decaps:
  Z_i(f, c) = Z_i^0(f) + Σ_j ΔZ_ij(f) · c_j

Approximation (small decap values):
  Z_i(f, c) ≈ Z_i^0(f) + Σ_j ∂Z_i/∂c_j · c_j
```

**Optimization:**
```
Minimize: max_{i,f} |Z_i(f, c) · I_i(f)|

Subject to:
  Σ_j c_j ≤ C_total
  c_j ≥ 0

This is a convex problem (can use SOCP or geometric programming)
```

### 5.2.3 Greedy Decap Insertion

```
Algorithm: Greedy Decap Placement

Input: Power grid, current profiles, decap budget C_total
Output: Decap placement c*

1. c ← 0
2. while Σ_j c_j < C_total:
3.   Solve power grid: V_i for all i
4.   Find worst droop: k = argmax_i (VDD - V_i)
5.   Find most effective decap: j* = argmax_j |∂V_k/∂c_j|
6.   c_j* ← c_j* + Δc
7. return c

The sensitivity ∂V_k/∂c_j is computed using adjoint analysis.
```

## 5.3 Power-Area Trade-off

```
Relationship between power grid metal and IR drop:

IR ∝ 1/√(metal_percentage)

Metal allocation:
  - Power/ground: 10-20% of metal layers
  - Signal routing: 40-50%
  - Clock: 5-10%
  - Spacing/overhead: remaining

Optimal allocation for SuperInstance.AI:
  - P/G ratio: 15% (conservative for low power design)
  - Dedicated M1-M2 for power (thick metals)
  - M3-M4 for signal routing
```

---

# 6. Routing Optimization

## 6.1 Global Routing as Flow Problem

### 6.1.1 Graph Model

**Routing graph:**
```
G = (V, E)

V = Global routing cells (GCells)
E = Adjacent GCell boundaries (routing edges)

Each edge e has:
  - Capacity cap_e: Number of tracks available
  - Demand dem_e: Number of tracks used
  - Cost cost_e: Routing cost
```

**Net as commodity:**
```
For net k with terminals {t₁, ..., t_m}:
  - Source s_k: One terminal (arbitrary)
  - Sinks: Other terminals
  - Flow demand: 1 (connectivity)

Multi-terminal net → Steiner tree problem
```

### 6.1.2 Multi-Commodity Flow Formulation

```
Variables:
  f_e^k : Flow of net k on edge e

Minimize: Σ_{k,e} cost_e · f_e^k

Subject to:
  Flow conservation: Σ_{e∈δ+(v)} f_e^k = Σ_{e∈δ-(v)} f_e^k    ∀v ∉ {s_k, t_k}
  
  Source/sink: Σ_{e∈δ+(s_k)} f_e^k - Σ_{e∈δ-(s_k)} f_e^k = 1
  
  Capacity: Σ_k f_e^k ≤ cap_e                                  ∀e
  
  Binary (for integer flow): f_e^k ∈ {0,1}                    ∀k,e
```

### 6.1.3 Approximation via Linear Programming

**Relaxation:**
```
Allow fractional flow: 0 ≤ f_e^k ≤ 1

Solve LP relaxation, then apply randomized rounding:

  Pr(f_e^k = 1) = f_e^k*

Expected overflow: E[Σ_k f_e^k] = Σ_k f_e^k* ≤ cap_e

With high probability, overflow is bounded by O(log n / log log n)
```

## 6.2 Weight Routing to MAC Units

### 6.2.1 Mask-Locked Weight Distribution

**Problem:** Route weight values from mask-ROM to MAC units

```
Given:
  - Weight matrix W ∈ {-1, 0, +1}^{m×n}
  - MAC units at positions {(x_i, y_i)}
  - Weight sources at fixed locations

Objective:
  Minimize total routing length while ensuring each MAC receives its weight
```

**Formulation as assignment:**
```
For weight value w at position (r, c):
  Must connect to MAC at position (r, c) in systolic array
  
Weight routing is deterministic (design-time):
  - No optimization needed for dynamic routing
  - Physical design: Metal patterns encode weight values
```

### 6.2.2 Optimal Weight Encoding Layout

```
For iFairy RAU with weights in {±1, ±i}:

Encode as 2-bit value:
  00 → +1
  01 → -1  
  10 → +i
  11 → -i

Metal layer encoding:
  M1: Bit 0 of weight
  M2: Bit 1 of weight
  M3: Routing to RAU control

Each RAU has dedicated weight lines:
  - No sharing (deterministic latency)
  - No arbitration needed
```

## 6.3 Congestion Minimization

### 6.3.1 Congestion Metrics

```
Edge congestion:
  cong_e = dem_e / cap_e

Global congestion:
  G_cong = max_e cong_e

Smooth approximation:
  G_cong ≈ (Σ_e cong_e^p)^{1/p}  as p → ∞
```

### 6.3.2 Congestion-Driven Placement

**Add congestion penalty to placement:**
```
minimize: WL + α · Σ_e (dem_e/cap_e)²

This penalizes routes through congested regions.

Implementation:
  1. Initial placement
  2. Estimate congestion from placement
  3. Update placement cost with congestion
  4. Iterate until convergence
```

### 6.3.3 Rip-Up and Reroute

```
Algorithm: Iterative Rip-Up and Reroute

Input: Initial global routing
Output: Congestion-free routing (or minimum overflow)

1. while congestion exists:
2.   Identify overflow edges: O = {e : dem_e > cap_e}
3.   for each net k using edges in O:
4.     Rip up net k
5.     Reroute k avoiding O (use Dijkstra with modified costs)
6.     cost_e' = cost_e · exp(β · (dem_e/cap_e - 1))
7.   Update demands
8. return routing
```

## 6.4 Timing-Driven Routing Equations

### 6.4.1 Elmore Delay Model

```
For RC tree rooted at source:

Delay at node i:
  T_i = Σ_{k in path(source→i)} R_k · C_downstream(k)

where C_downstream(k) = total capacitance in subtree rooted at k
```

### 6.4.2 Buffered Routing

**Buffer insertion optimization:**
```
Given:
  - Wire segment with length L
  - Per-unit resistance r, capacitance c
  - Buffer delay T_buf, input cap C_in, output resistance R_out

Optimal buffer locations for minimum delay:

Unbuffered delay:
  T_unbuf = 0.5 · r · c · L²

Buffered delay (with n buffers):
  T_buf(n) = (n+1) · T_buf + 0.5 · r · c · (L/(n+1))²

Optimal n:
  n* = L · √(r·c / (2·T_buf)) - 1

Optimal spacing:
  L_seg = √(2·T_buf / (r·c))
```

### 6.4.3 Timing-Driven Tree Construction

```
Objective: Construct Steiner tree minimizing max delay

minimize: max_{sinks i} T_i

subject to: Connectivity

Approach: Elmore-Steiner algorithm
  1. Start with source
  2. At each step, add sink with minimum incremental delay
  3. Consider both direct connection and Steiner points
  4. Insert buffers where beneficial
```

---

# 7. References and Solution Methods

## 7.1 DAC/ICCAD Papers on Physical Design Optimization

### 7.1.1 Floorplanning

1. **"Floorplanning with Temperature-Aware Objective"** - DAC 2006
   - Introduces thermal cost into floorplanning
   - Simulated annealing with thermal evaluation

2. **"Thermal-Aware Floorplanning Using Genetic Algorithm"** - ICCAD 2007
   - Multi-objective GA for thermal optimization
   - Pareto frontier generation

3. **"Modern Floorplanning with Boundary Constraints"** - DAC 2019
   - MIP formulation for constrained floorplanning
   - Branch-and-bound solver

### 7.1.2 Thermal-Aware Placement

1. **"Thermal Placement in 3D ICs"** - DAC 2006
   - Compact thermal model for placement
   - Gradient-based optimization

2. **"HotSpot: A Compact Thermal Modeling Methodology"** - ISCA 2004
   - Foundation for thermal analysis
   - Block-level thermal resistance network

3. **"Thermal-Aware Global Placement"** - ICCAD 2004
   - Force-directed placement with thermal forces
   - Analytical formulation

### 7.1.3 Yield Optimization

1. **"Yield Optimization in VLSI Circuits"** - IEEE TCAD 1988
   - Statistical yield analysis
   - Design centering

2. **"Bin Assignment for Profit Maximization"** - DAC 2010
   - Revenue optimization formulation
   - Greedy and DP algorithms

### 7.1.4 Power Distribution

1. **"Optimal Decoupling Capacitor Sizing and Placement"** - ISPD 2007
   - Convex optimization formulation
   - Sensitivity-based methods

2. **"Power Grid Sizing for IR Drop Minimization"** - ICCAD 2006
   - SOCP formulation
   - Efficient solvers

### 7.1.5 Routing

1. **"Global Routing via Flow Decomposition"** - DAC 2003
   - Multi-commodity flow formulation
   - Approximation algorithms

2. **"Timing-Driven Routing"** - IEEE TCAD 1993
   - Elmore delay minimization
   - Steiner tree construction

## 7.2 Solution Methods Summary

### 7.2.1 Exact Methods

| Problem Type | Method | Complexity |
|--------------|--------|------------|
| Floorplanning (MIP) | Branch-and-Bound | Exponential (worst case) |
| Assignment | Hungarian Algorithm | O(n³) |
| Min-Cost Flow | Network Simplex | O(V²E log(VC)) |
| Convex Programs | Interior Point | Polynomial |

### 7.2.2 Heuristic Methods

| Problem Type | Method | Typical Quality |
|--------------|--------|-----------------|
| Floorplanning | Simulated Annealing | 5-15% from optimal |
| Placement | Force-Directed | 10-20% from optimal |
| Global Routing | Rip-Up Reroute | 5-10% from optimal |
| Buffer Insertion | Dynamic Programming | Optimal for given topology |

### 7.2.3 Implementation Tools

```
Commercial:
  - Cadence Innovus: Full physical design flow
  - Synopsys ICC: Placement and routing
  - Ansys RedHawk: Thermal and power analysis

Open Source:
  - OpenROAD: Complete RTL-to-GDSII flow
  - OpenDP: Detailed placement
  - FastRoute: Global routing

Optimization Solvers:
  - Gurobi: MIP solver (commercial)
  - CPLEX: LP/MIP solver (commercial)
  - GLPK: LP/MIP solver (open source)
  - CVXPY: Convex optimization modeling
```

## 7.3 SuperInstance.AI Specific Recommendations

### 7.3.1 Floorplanning Strategy

```
Given deterministic weight routing:
  1. Place compute array (systolic array) first - fixed position
  2. Place KV cache SRAM - adjacent to compute
  3. Place I/O pads - fixed by package
  4. Place control logic - remaining space

Thermal considerations:
  - Compute array generates most heat
  - SRAM is heat-sensitive
  - Thermal separation via routing channels
```

### 7.3.2 Power Grid Design

```
For 2-3W target power:
  - Conservative IR drop budget: 5% of VDD
  - Dedicated M1-M2 for power delivery
  - Distributed decaps near compute array

Power network estimation:
  I_max = P_max / VDD = 3W / 1.0V = 3A
  IR_drop_max = 50 mV
  R_grid_max = IR_drop_max / I_max = 16.7 mΩ
  
Required metal:
  R_sheet = 0.03 Ω/□ (M2 at 28nm)
  Width for 16.7 mΩ over 5mm: w ≈ 10 μm
```

### 7.3.3 Routing Priorities

```
Priority order (highest first):
  1. Power/ground network (preroute)
  2. Clock distribution (if synchronous)
  3. Weight distribution (mask-locked, fixed)
  4. Activation data flow (systolic)
  5. Control signals
  6. KV cache interface

Special considerations:
  - Weight routing is static → optimize at design time
  - Systolic dataflow → regular patterns
  - KV cache access → high bandwidth requirement
```

---

# Appendix A: Mathematical Notation

| Symbol | Meaning |
|--------|---------|
| $\mathbb{R}$ | Set of real numbers |
| $\mathbb{Z}$ | Set of integers |
| $\{0,1\}$ | Binary values |
| $\forall$ | For all |
| $\exists$ | There exists |
| $\sum$ | Summation |
| $\prod$ | Product |
| $\nabla$ | Gradient |
| $\partial$ | Partial derivative |
| $\alpha, \beta, \gamma$ | Greek letters for parameters |
| $\lambda$ | Lagrange multiplier |
| $\infty$ | Infinity |

---

# Appendix B: Key Formulas Quick Reference

## Floorplanning
```
Area: A = W × H
Wirelength: WL = Σ_k HPWL_k
Non-overlap: (x_i + w_i ≤ x_j) ∨ (x_j + w_j ≤ x_i) ∨ (y_i + h_i ≤ y_j) ∨ (y_j + h_j ≤ y_i)
```

## Thermal
```
Heat equation: ∇ · (k ∇T) + Q = 0
Thermal resistance: R_th = L / (k × A)
Temperature rise: ΔT = P × R_th
```

## Memory
```
KV cache: KV_size = 2 × L × d × S × b
Bandwidth: BW = KV_size × tok/s
SRAM area: A_SRAM = Size / Density
```

## Power
```
IR drop: V_drop = I × R
Decap energy: E = 0.5 × C × V²
MTTF: MTTF = A × J^{-n} × exp(E_a / kT)
```

## Routing
```
Edge congestion: cong = demand / capacity
Elmore delay: T = Σ R_k × C_downstream(k)
Buffer spacing: L_seg = √(2 × T_buf / (r × c))
```

---

*Document Version 1.0 - Optimization Theory for SuperInstance.AI*
