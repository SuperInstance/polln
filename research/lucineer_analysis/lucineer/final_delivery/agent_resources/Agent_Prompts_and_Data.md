# Agent Resources Package
## Prompts and Data for Math/Logic Specialists

**Document Version**: Final 1.0
**Purpose**: Enable other specialists to continue deep mathematical analysis

---

# Part I: Agent Prompts

## PROMPT A: Ternary Weight Arithmetic Optimization

**Context**: BitNet b1.58 uses ternary weights {-1, 0, +1}. This is NOT standard quantization—it's a fundamentally different representation.

**Questions to Explore**:

1. **Multiplication Elimination**: With ternary weights, weight × activation multiplication becomes:
   - w = +1: result = activation (identity)
   - w = 0: result = 0 (no computation)
   - w = -1: result = -activation (negation)

   What is the mathematical foundation for optimizing this? Can we design circuits that never perform actual multiplication?

2. **Sparsity Patterns**: In ternary networks, ~30-50% of weights are zero. How can we mathematically model the optimal skipping strategy?

3. **Matrix Decomposition**: Can a ternary matrix be decomposed into operations simpler than matrix multiplication?

**Deliverable**: Mathematical framework for computing ternary matrix-vector products with minimum operations.

---

## PROMPT B: Complex-Valued LLM (iFairy) Analysis

**Context**: iFairy uses weights from {±1, ±i} (fourth roots of unity). Claims "multiplication-free inference."

**Questions to Explore**:

1. **Complex Multiplication Decomposition**: With weights ∈ {±1, ±i}, prove why multiplication reduces to only additions/swaps.

2. **Hermitian Inner Product**: iFairy uses Hermitian inner product. With w ∈ {±1, ±i}, what operations are actually needed?

3. **Hardware Resource Comparison**:
   - Ternary (BitNet): weights {-1, 0, +1}, requires add/subtract/skip
   - Complex 2-bit (iFairy): weights {±1, ±i}, requires add/swap
   - Which is more efficient?

**Deliverable**: Rigorous comparison of ternary vs. complex-valued representation.

---

## PROMPT C: KV Cache Bandwidth Optimization

**Context**: KV cache is the PRIMARY memory bandwidth bottleneck in autoregressive LLM inference.

**Questions to Explore**:

1. **Mathematical Analysis of KV Necessity**: What is the minimum information that MUST be stored per layer? Can we derive lower bounds from information theory?

2. **KV Cache Compression**: Can KV cache be quantized to INT4/INT8 without quality loss? Derive error bounds.

3. **Alternative Attention Mechanisms**: Can linear attention work with ternary weights?

**Deliverable**: Mathematical framework for minimizing KV cache bandwidth.

---

## PROMPT D: Mask-Locked Weight Encoding Geometry

**Context**: Weights encoded in metal interconnect layers. Physical layout matters.

**Questions to Explore**:

1. **Information Density**: How many bits can be encoded per unit area in metal interconnect?

2. **Noise Immunity**: What encoding scheme maximizes Hamming distance between weight values?

3. **Routing Optimization**: What's the mathematical relationship between weight matrix structure and routing complexity?

**Deliverable**: Mathematical framework for optimal weight encoding in silicon.

---

## PROMPT E: Systolic Array Optimization

**Context**: Systolic arrays are standard for matrix operations in AI accelerators.

**Questions to Explore**:

1. **Optimal Array Dimension**: For fixed weight matrix W (N×M), what's the optimal systolic array shape?

2. **Throughput Modeling**: Derive formula for tokens/second given clock, array dimensions, model dimensions.

**Deliverable**: Mathematical model for systolic array design with mask-locked weights.

---

# Part II: Technical Reference Data

## BitNet b1.58-2B-4T Specifications

| Parameter | Value |
|-----------|-------|
| Total Parameters | 2.4B |
| Transformer Parameters | 2B |
| Training Tokens | 4T |
| Context Length | 4096 |
| Hidden Dimensions | 2560 |
| Number of Layers | 32 |
| Attention Heads | 32 |
| License | MIT |

## iFairy Specifications

| Parameter | Value |
|-----------|-------|
| Paper | arXiv:2508.05571 |
| Available Sizes | 700M, 1.3B |
| Weight Values | {±1, ±i} |
| Bits per Weight | 2 bits |
| License | Apache 2.0 |

## Memory Calculations

```
KV_Cache_Size = 2 × num_layers × hidden_dim × sequence_length × bytes_per_value

For BitNet 2B, 4K context, FP16:
= 2 × 32 × 2560 × 4096 × 2
= 1.25 GB

For 512-token sliding window, INT4:
= 2 × 32 × 2560 × 512 × 0.5
= 42 MB
```

## Power Estimates

| Operation | Energy (28nm) |
|-----------|---------------|
| SRAM Read (8-bit) | 1-5 pJ |
| INT8 Multiply | 0.5-2 pJ |
| INT8 Add | 0.1-0.5 pJ |
| Ternary MAC (add/sub only) | 0.02-0.15 pJ |
| iFairy RAU | 0.1-0.15 pJ |

---

# Part III: Open Questions

## Critical Unresolved Questions

1. **Column Ordering Optimization**: Is there a polynomial-time algorithm for minimizing interval count in ternary matrix column ordering?

2. **Information-Theoretic KV Bounds**: What is the exact minimum storage required from rate-distortion theory?

3. **2T1C Precision Limit**: Can 16-bit precision be achieved with larger capacitors or calibration?

4. **Layer Sensitivity**: Which transformer layers benefit most from iFairy vs ternary?

5. **Attention Mask Learning**: What training methods produce optimal hardware-friendly sparse patterns?

---

# Part IV: Output Format

For each analysis, provide:

```markdown
# Analysis: [PROMPT LETTER] - [TITLE]

## Summary
[2-3 sentence key finding]

## Mathematical Framework
[Derivations, equations, proofs]

## Numerical Results
[Specific calculations for target parameters]

## Implementation Recommendation
[Feasibility and path to implementation]

## Open Questions
[What remains unknown]
```

---

# Part V: Key Contacts

| Entity | Contact | Purpose |
|--------|---------|---------|
| Peking University (iFairy) | tongyang@pku.edu.cn | Model collaboration |
| KAIST HPIC Lab | hpic-lab.github.io | 2T1C DRAM research |
| Microsoft BitNet Team | via GitHub | Model development |

---

*Resources provided for continuation of mathematical analysis.*
