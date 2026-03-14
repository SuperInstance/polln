# Implementation Priority Matrix
## Mask-Locked Inference Chip - Actionable Development Guide

**Document Version**: 1.0
**Date**: March 2026
**Purpose**: Prioritize mathematical principles for immediate implementation

---

## Decision Framework

Each principle is evaluated on three dimensions:
1. **Impact** (1-10): How much improvement does this provide?
2. **Confidence** (1-10): How certain are we of the math?
3. **Effort** (1-10): How difficult is implementation?

**Priority Score** = Impact × Confidence / Effort

---

## Tier 1: IMPLEMENT IMMEDIATELY (Priority Score > 5)

### 1. iFairy Rotation-Accumulate Units (Score: 9.0)

| Metric | Value |
|--------|-------|
| Impact | 10 |
| Confidence | 9 |
| Effort | 10 |
| **Priority** | **9.0** |

**What**: Replace all MAC units with RAUs that use {±1, ±i} weights.

**Why**: Eliminates multipliers entirely, reducing gate count by 95%.

**How**:
```
RAU Implementation:
1. 2-bit weight decoder (4 states: +1, -1, +i, -i)
2. 4:1 MUX for real part (select from: a, -a, b, -b)
3. 4:1 MUX for imaginary part
4. 8-bit adder for accumulation
5. Total: ~150 gates per RAU
```

**Timeline**: Design complete in 4 weeks, FPGA prototype in 8 weeks.

**Risks**: Requires iFairy model training or conversion from BitNet.

**Action Items**:
- [ ] Verify iFairy models available on HuggingFace (700M, 1.3B)
- [ ] Create RAU RTL in Verilog/Chisel
- [ ] Compare gate count vs ternary MAC
- [ ] Benchmark iFairy vs BitNet quality

---

### 2. Sliding Window KV Cache (Score: 8.1)

| Metric | Value |
|--------|-------|
| Impact | 9 |
| Confidence | 9 |
| Effort | 10 |
| **Priority** | **8.1** |

**What**: Limit context to recent W tokens with permanent attention sinks.

**Why**: Reduces KV cache from O(sequence length) to O(window size). Enables on-chip storage.

**How**:
```
Cache Structure:
- Permanent: First 4 tokens (attention sinks)
- Sliding: Most recent 508 tokens
- Total: 512 tokens per layer

Storage:
- INT4 quantization: 21 MB total
- On-chip SRAM at 28nm: ~14 mm²
```

**Timeline**: Implement immediately. No model changes needed.

**Risks**: May reduce performance on tasks requiring long context.

**Action Items**:
- [ ] Quantify attention sink behavior in BitNet
- [ ] Test quality degradation with different window sizes
- [ ] Design SRAM organization
- [ ] Implement FIFO eviction logic

---

### 3. Ternary MAC with Skip Logic (Score: 7.5)

| Metric | Value |
|--------|-------|
| Impact | 8 |
| Confidence | 10 |
| Effort | 10.7 |
| **Priority** | **7.5** |

**What**: Standard ternary MAC with sparsity-aware operation skipping.

**Why**: 33% of weights are zero, enabling power gating and cycle skipping.

**How**:
```
Ternary PE:
1. Read weight w ∈ {-1, 0, +1}
2. If w == 0: skip (no computation)
3. If w == +1: accumulate += activation
4. If w == -1: accumulate -= activation

Power Gating:
- Disable PE clock when w == 0
- Estimated power reduction: 30-40%
```

**Timeline**: Baseline implementation. Ready now.

**Risks**: None. This is the standard approach.

**Action Items**:
- [ ] Implement in FPGA prototype
- [ ] Measure actual power savings
- [ ] Compare with iFairy approach

---

## Tier 2: IMPLEMENT SHORT-TERM (Priority Score 3-5)

### 4. Bit-Serial Ternary MAC (Score: 4.5)

| Metric | Value |
|--------|-------|
| Impact | 6 |
| Confidence | 8 |
| Effort | 10.7 |
| **Priority** | **4.5** |

**What**: Process activations one bit at a time over 8 cycles.

**Why**: Simpler routing (1-bit vs 8-bit buses), lower switching power.

**How**:
```
Bit-Serial PE:
- Input: Single bit per cycle
- Operation: Accumulate with shift
- 8 cycles per MAC
- Trade throughput for efficiency
```

**Decision**: Only implement if routing congestion becomes severe.

**Action Items**:
- [ ] Prototype on FPGA
- [ ] Measure routing density vs parallel
- [ ] Evaluate throughput impact

---

### 5. Mixed Precision Layer Allocation (Score: 4.0)

| Metric | Value |
|--------|-------|
| Impact | 7 |
| Confidence | 6 |
| Effort | 10.5 |
| **Priority** | **4.0** |

**What**: Use iFairy for sensitive layers, ternary for others.

**Why**: Optimize quality/area trade-off by allocating precision where needed.

**How**:
```
Analysis Required:
1. Compute layer-wise sensitivity (Hessian trace or weight distribution)
2. Identify layers requiring higher precision
3. Allocate iFairy vs ternary accordingly
```

**Decision**: Implement after baseline iFairy design is validated.

**Action Items**:
- [ ] Perform sensitivity analysis on BitNet weights
- [ ] Determine layer precision requirements
- [ ] Design dual-mode PE architecture

---

### 6. RNS Accumulation (Score: 3.5)

| Metric | Value |
|--------|-------|
| Impact | 5 |
| Confidence | 7 |
| Effort | 10 |
| **Priority** | **3.5** |

**What**: Use Residue Number System for carry-free addition.

**Why**: Eliminates carry propagation, enables faster clock or lower voltage.

**How**:
```
Moduli Set: {3, 4, 5, 7, 11, 13, 17, 19}
- Product: ~9.7M (covers 19-bit range)
- Each adder: 2-4 bits
- Final CRT conversion: ROM lookup
```

**Decision**: Low priority. Standard adder trees are sufficient.

**Action Items**:
- [ ] Simulate RNS vs binary adder timing
- [ ] Evaluate area trade-off

---

## Tier 3: RESEARCH PHASE (Priority Score < 3)

### 7. 2T1C In-Memory Attention (Score: 2.5)

| Metric | Value |
|--------|-------|
| Impact | 10 |
| Confidence | 5 |
| Effort | 20 |
| **Priority** | **2.5** |

**What**: Use DRAM cells for analog attention score computation.

**Why**: 1000× energy reduction for attention, eliminates KV bandwidth.

**How**:
```
Implementation:
1. Store keys as analog voltages in 2T1C array
2. Apply query as wordline voltages
3. Bitline output = attention scores
4. ADC conversion for softmax
```

**Decision**: Long-term research. Requires collaboration with KAIST.

**Action Items**:
- [ ] Contact KAIST HPIC Lab
- [ ] Fund SPICE simulation study
- [ ] Prototype small array

**Timeline**: 2-3 year development cycle.

---

### 8. Learned Sparse Attention Masks (Score: 2.3)

| Metric | Value |
|--------|-------|
| Impact | 8 |
| Confidence | 4 |
| Effort | 14 |
| **Priority** | **2.3** |

**What**: Train model with fixed sparse attention pattern.

**Why**: Enables precomputed cache lifetimes and eviction schedules.

**How**:
```
Training:
1. Add sparsity regularization during training
2. Hard-threshold to binary mask
3. Fine-tune with fixed mask
4. Hardwire mask into silicon
```

**Decision**: Requires model retraining. Medium-term research.

**Action Items**:
- [ ] Experiment with sparse attention training
- [ ] Validate quality preservation

---

### 9. KV Projection Compression (Score: 2.0)

| Metric | Value |
|--------|-------|
| Impact | 6 |
| Confidence | 3 |
| Effort | 9 |
| **Priority** | **2.0** |

**What**: Learn lower-dimensional projection for KV storage.

**Why**: 8× compression could enable longer contexts.

**Decision**: High risk. Quality impact unknown.

---

### 10. Stochastic Computing (Score: 1.5)

| Metric | Value |
|--------|-------|
| Impact | 4 |
| Confidence | 5 |
| Effort | 13.3 |
| **Priority** | **1.5** |

**What**: Use probability bitstreams for arithmetic.

**Why**: Minimal hardware (AND gates for multiplication).

**Decision**: Not feasible for high-throughput inference. Latency too high.

---

## Implementation Timeline

```
Month 1-3 (Gate 0):
├── IMPLEMENT: Ternary MAC (baseline)
├── IMPLEMENT: Sliding Window KV Cache
└── VALIDATE: FPGA prototype at 25 tok/s

Month 4-6 (Gate 1):
├── IMPLEMENT: iFairy RAU (if quality validated)
├── EVALUATE: Bit-serial vs parallel
└── DESIGN: On-chip SRAM organization

Month 7-12 (Gate 2):
├── TAPEOUT: 28nm MPW
├── VALIDATE: Silicon measurements
└── RESEARCH: 2T1C analog compute

Month 13-18 (Gate 3):
├── PRODUCTION: Full mask set
├── RESEARCH: Learned sparse masks
└── SHIP: Customer samples
```

---

## Decision Tree

```
                    ┌─────────────────┐
                    │ START: BitNet   │
                    │ Ternary Weights │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼─────┐               ┌───────▼───────┐
        │ iFairy    │               │ Stay Ternary  │
        │ Complex   │               │               │
        │ (2-bit)   │               │ (1.58-bit)    │
        └─────┬─────┘               └───────┬───────┘
              │                             │
     ┌────────┴────────┐          ┌────────┴────────┐
     │ Better quality  │          │ Simpler HW      │
     │ Same gate count │          │ More mature     │
     │ (RAU ≈ MAC)     │          │                 │
     └─────────────────┘          └─────────────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │ SLIDING WINDOW  │
                    │ KV CACHE        │
                    │ (Always)        │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼─────┐               ┌───────▼───────┐
        │ On-chip   │               │ External      │
        │ SRAM only │               │ LPDDR4        │
        │ (21 MB)   │               │ (512 MB)      │
        └─────┬─────┘               └───────┬───────┘
              │                             │
     ┌────────┴────────┐          ┌────────┴────────┐
     │ Lower power     │          │ Longer context  │
     │ Limited context │          │ Higher BW       │
     └─────────────────┘          └─────────────────┘
```

---

## Summary: Top 3 Actions

### 1. Implement iFairy RAU Architecture
- Highest impact per gate
- Multiplication-free operation
- Comparable gate count to ternary MAC
- Better quality potential

### 2. Deploy Sliding Window KV Cache
- Enables on-chip storage
- Eliminates memory bottleneck
- Attention sinks preserve quality
- Immediate implementation possible

### 3. Prepare 28nm MPW Tapeout
- Leverage mature process
- Validate silicon behavior
- 12-18 month timeline
- Target $35-60 ASP

---

*Document prepared for: Mask-Locked Development Team*
*Next Review: After Gate 0 completion*
