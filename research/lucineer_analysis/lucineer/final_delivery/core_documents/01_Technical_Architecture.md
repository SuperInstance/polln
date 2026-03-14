# Mask-Locked Inference Chip
## Complete Technical Specification & Development Plan

**Document Version**: Final 1.0
**Date**: March 2026
**Classification**: Technical Reference Document

---

# Part I: Project Overview

## 1.1 The Core Proposition

The Mask-Locked Inference Chip is a new category of semiconductor product that physically embeds neural network weights into silicon metal interconnect layers. Unlike existing AI chips that load models into memory, our approach bakes model parameters directly into the hardware fabric.

**Key Innovation**: By sacrificing the ability to run arbitrary models, we gain order-of-magnitude improvements in power efficiency, cost, and simplicity—making local AI inference practical for billions of devices that cannot currently support it.

### Target Specifications

| Parameter | Target | Rationale |
|-----------|--------|-----------|
| Model Size | 1-3B parameters | Fits in reasonable die area |
| Power | 2-3W | USB-powered, passive cooling |
| Throughput | 80-150 tok/s | Usable for real-time chat |
| Price | $35-60 | Market gap below Jetson ($250) |
| Process Node | 28nm | Low NRE ($2-3M masks) |
| Setup Time | Zero | Plug-and-play, no software stack |

## 1.2 Market Opportunity

The edge AI chip market is projected to grow from $3.67 billion (2025) to $11.54 billion (2030). Current solutions force developers to choose between:

- **Expensive general-purpose hardware** (Jetson at $250, 10-15W)
- **Severely limited microcontrollers** (Coral EOL, Hailo weak on LLMs)

Our product fills the gap: affordable, power-efficient LLM inference for edge devices.

---

# Part II: Technical Architecture

## 2.1 The Mask-Locked Concept

### Traditional Approach
```
Weight stored in memory → Fetch from memory → Compute → Repeat
Problem: Memory bandwidth is bottleneck
Power: DRAM access ~50-100 pJ/bit
```

### Mask-Locked Approach
```
Weight encoded in metal interconnect → Always present at compute unit
Benefit: Zero access latency, zero access energy, infinite bandwidth
Tradeoff: Changing weights requires fabricating new chip
```

### Mathematical Foundation

For a ternary weight matrix **W** ∈ {-1, 0, +1}:

```
Standard MAC: result += w × a
Ternary MAC:
  - w = +1: result += a (addition only)
  - w = 0:  skip (no operation)
  - w = -1: result -= a (subtraction only)
```

This eliminates multiplication hardware entirely.

## 2.2 iFairy Complex-Valued Extension

### Fourth Roots of Unity

iFairy (Peking University, arXiv:2508.05571) uses weights from {+1, -1, +i, -i}. Complex multiplication becomes permutation:

| Weight | Real Output | Imaginary Output | Operation |
|--------|-------------|------------------|-----------|
| +1 | a | b | Identity |
| -1 | -a | -b | Negate both |
| +i | -b | a | Swap + negate real |
| -i | b | -a | Swap + negate imag |

### Rotation-Accumulate Unit (RAU)

Each RAU requires:
- 4:1 multiplexer for real output
- 4:1 multiplexer for imaginary output
- 2-bit weight decoder
- 8-bit accumulator

**Gate count**: ~150 gates (vs ~6000 for complex FP16 multiplier)

**Energy per operation**: ~0.1-0.15 pJ (vs ~5-10 pJ for digital multiplier)

## 2.3 Weight Representation Comparison

| Approach | Values | Bits/Weight | Hardware | Quality |
|----------|--------|-------------|----------|---------|
| BitNet Ternary | {-1,0,+1} | 1.58 | Add/Sub only | Good |
| iFairy Complex | {±1,±i} | 2.0 | Add/Swap only | Better |
| INT4 Quantization | {-8..+7} | 4.0 | Small multiplier | Best |

**Recommendation**: iFairy for optimal efficiency/quality balance

---

# Part III: KV Cache Architecture

## 3.1 The Memory Bottleneck

For a 2B parameter model with 4K context:

```
KV_Cache_Size = 2 × num_layers × hidden_dim × sequence_length × bytes_per_value

For BitNet 2B-4T:
= 2 × 32 × 2560 × 4096 × 2 bytes (FP16)
= 1.25 GB

Bandwidth at 80 tok/s = 100 GB/s
LPDDR4 provides only ~17 GB/s per channel → BOTTLENECK
```

## 3.2 Sliding Window Attention

### Theoretical Foundation

Attention weights decay exponentially with distance. A sliding window of W tokens captures most attention mass.

**Window Size Selection**:
- W = 512: Captures >90% attention mass
- W = 256: Captures ~80% attention mass
- W = 1024: Captures ~95% attention mass

### Attention Sinks

Transformers strongly attend to first few tokens (attention sink phenomenon). These must be permanently retained.

**Cache Structure**:
```
├── Permanent: First 4 tokens (attention sinks)
└── Sliding: Most recent 508 tokens
Total: 512 tokens per layer
```

### On-Chip Storage Feasibility

```
KV Cache Size (INT4):
= 2 × 32 × 2560 × 512 × 0.5 bytes
= 42 MB

SRAM at 28nm: ~1.5 Mbit/mm²
Area required: ~28 mm²

RESULT: Fits on-chip, eliminates external memory bandwidth
```

## 3.3 Memory Architecture Decision

| Option | Context | Memory | Bandwidth | Die Area |
|--------|---------|--------|-----------|----------|
| A: Minimal | 512 tokens | On-chip only | N/A | +28 mm² |
| B: Balanced | 2K tokens | 256MB LPDDR4 | 17 GB/s | External |
| C: Extended | 4K tokens | 512MB LPDDR4 | 17 GB/s | External |
| D: Hybrid | 512 + extend | 4MB SRAM + LPDDR4 | Flexible | +7 mm² |

**Recommendation**: Option D (Hybrid) for v1.0, Option A (On-chip only) for cost-optimized version.

---

# Part IV: Systolic Array Design

## 4.1 Array Configuration

For matrix dimensions m = n = 2560 (per layer):

**Optimal Array**: 32 × 32 = 1024 Processing Elements (PEs)

**Throughput Calculation**:
```
Cycles per layer = m/32 + n/32 - 1 = 159 cycles
At 250 MHz: 0.636 μs per layer
32 layers: 20.4 μs per token
Theoretical max: 49,000 tok/s (compute bound)
```

**Actual throughput limited by**: KV cache access, sequential layer dependencies

## 4.2 Processing Element Design

### Ternary PE
```
Input: 8-bit activation, ternary weight
Operation:
  - Read weight w
  - If w = +1: accumulate += activation
  - If w = 0: skip
  - If w = -1: accumulate -= activation
Gates: ~50 per PE
```

### iFairy RAU
```
Input: 8-bit activation (real), 8-bit activation (imag), 2-bit weight
Operation:
  - Decode weight (4 states)
  - Route a, b, -a, -b via MUX
  - Accumulate to output registers
Gates: ~150 per RAU
```

## 4.3 Dataflow

**Weight-Stationary Systolic Array**:
1. Weights pre-loaded into PEs (or hardwired)
2. Activations flow left-to-right
3. Partial sums flow top-to-bottom
4. Output collected at bottom edge

**For mask-locked**: Weights permanently wired, no load phase.

---

# Part V: Power Analysis

## 5.1 Energy Breakdown

| Component | Energy/Token | Percentage |
|-----------|--------------|------------|
| Compute (iFairy RAU) | 50-100 μJ | 15-25% |
| KV Cache Access (SRAM) | 150-200 μJ | 40-50% |
| Control/IO | 50-100 μJ | 15-25% |
| Leakage | 30-50 μJ | 10-15% |
| **Total** | **280-450 μJ** | 100% |

## 5.2 Power at Target Throughput

```
At 80 tok/s:
Power = 450 μJ × 80 = 36 mJ/s = 36 mW

At 150 tok/s:
Power = 450 μJ × 150 = 67.5 mW

HEADROOM: Massive - design limited by architecture, not power
```

## 5.3 Actual Power Consumers

| Component | Power | Notes |
|-----------|-------|-------|
| Compute array | ~0.5W | At 250 MHz, 1000 PEs |
| SRAM access | ~0.8W | 21 MB, 80 tok/s |
| I/O (USB) | ~0.3W | 5V/500mA budget |
| Leakage (28nm) | ~0.2W | Room temperature |
| Control logic | ~0.2W | FSM, routing |
| **Total** | **~2W** | **Within 3W budget** |

---

# Part VI: Die Economics

## 6.1 Die Area Estimation

| Component | Area | Notes |
|-----------|------|-------|
| Compute (1024 PEs) | 0.5 mm² | 150 gates/PE |
| SRAM (21 MB) | 28 mm² | 1.5 Mbit/mm² |
| Control logic | 2 mm² | FSM, interfaces |
| I/O pads | 5 mm² | USB, power, test |
| Routing overhead | 5 mm² | Estimated |
| **Total** | **~40 mm²** | Conservative |

## 6.2 Cost Analysis

**28nm Process**:
- Wafer cost: ~$3,000 (300mm)
- Dies per wafer: ~1,400 (at 40 mm², 80% yield)
- Die cost: ~$2.14

**Packaging & Test**: ~$3-5 per unit

**External Memory (if needed)**:
- LPDDR4 512MB: $10-12 (current market)

**Total COGS**:
- On-chip only: $5-7 per unit
- With LPDDR4: $15-19 per unit

## 6.3 Gross Margin Analysis

| Configuration | COGS | Target ASP | Gross Margin |
|---------------|------|------------|--------------|
| On-chip only | $7 | $35 | 80% |
| With LPDDR4 | $19 | $49 | 61% |
| Premium config | $25 | $69 | 64% |

---

# Part VII: Process Node Selection

## 7.1 Node Comparison

| Node | Mask Cost | Wafer Cost | Density | Availability |
|------|-----------|------------|---------|--------------|
| 40nm | $1-1.5M | $2,500 | 1.0 Mbit/mm² | Excellent |
| 28nm | $2-3M | $3,000 | 1.5 Mbit/mm² | Good |
| 22nm | $4-5M | $4,500 | 2.0 Mbit/mm² | Limited |
| 14nm | $8-12M | $8,000 | 3.0 Mbit/mm² | Allocated |

**Recommendation**: 28nm for optimal cost/availability balance

## 7.2 Foundry Options

| Foundry | 28nm Status | Notes |
|---------|-------------|-------|
| TSMC | Available | Industry standard, MPW access |
| Samsung | Available | Alternative, competitive pricing |
| GlobalFoundries | Available | US-based, government contracts |
| SMIC | Restricted | Export control issues |

**Recommendation**: TSMC via MOSIS or Europractice for MPW

---

# Part VIII: Competitive Positioning

## 8.1 Competitive Matrix

| Product | Power | Throughput | Price | Setup |
|---------|-------|------------|-------|-------|
| **This Chip** | 2-3W | 80-150 tok/s | $35-60 | Zero |
| Jetson Orin Nano | 10-15W | 20-30 tok/s | $250 | High |
| Hailo-10H | 5W | 5-10 tok/s | $88 | Moderate |
| Coral TPU | 2W | N/A (CNN only) | $60 | Moderate |

## 8.2 Differentiation

1. **Multiplication-free**: iFairy architecture eliminates multipliers
2. **On-chip KV cache**: Eliminates memory bandwidth bottleneck
3. **Zero setup**: No CUDA, no drivers, no software stack
4. **Price**: 4-7× cheaper than nearest competitor

## 8.3 Defensibility

| Moat | Description |
|------|-------------|
| Architecture | iFairy RAU requires model-specific training |
| Physical design | Weight routing optimization is non-trivial |
| Patents | File on RAU, on-chip KV, combined architecture |
| First-mover | 12-18 month window before Taalas pivots to edge |

---

# Part IX: Implementation Roadmap

## 9.1 Gate 0: FPGA Prototype (Month 1-3)

**Objective**: Validate arithmetic and estimate power

**Deliverables**:
- iFairy RAU on KV260 FPGA
- 25 tok/s minimum throughput
- Power measurement vs. simulation
- Quality comparison vs. bitnet.cpp

**Budget**: $50K (consultant + hardware)

## 9.2 Gate 1: Architecture Freeze (Month 4-6)

**Objective**: Finalize design for tapeout

**Deliverables**:
- Cycle-accurate simulator
- Power analysis (PrimeTime)
- Synthesis results
- Provisional patents filed

**Budget**: $100K (tools + legal)

## 9.3 Gate 2: MPW Tapeout (Month 7-12)

**Objective**: First silicon validation

**Deliverables**:
- 20-40 prototype units
- Silicon validation data
- Customer sampling

**Budget**: $150K (MPW + packaging)

## 9.4 Gate 3: Production (Month 13-18)

**Objective**: Volume manufacturing

**Deliverables**:
- Full mask set
- Production qualification
- 10K+ units capacity

**Budget**: $2-3M (masks + volume production)

---

# Part X: Risk Register

## 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| iFairy quality insufficient | 20% | Critical | Mixed-precision fallback |
| First silicon bugs | 30% | High | FPGA prototyping, formal verification |
| Timing closure issues | 15% | Medium | Conservative clock (250 MHz) |

## 10.2 Market Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Taalas enters edge | 25% | High | First-mover advantage |
| LPDDR4 price spike | 40% | Medium | On-chip option, lock contracts |
| Customer rejects frozen model | 30% | High | Clear upgrade path messaging |

## 10.3 Execution Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Team assembly fails | 30% | Critical | Silicon Catalyst incubator |
| Funding gap | 25% | Critical | Government grants (CHIPS Act) |
| Foundry allocation delay | 15% | Medium | Multiple foundry options |

---

# Part XI: Success Metrics

## 11.1 Technical Milestones

| Metric | Gate 0 | Gate 1 | Gate 2 | Gate 3 |
|--------|--------|--------|--------|--------|
| Throughput | 25 tok/s | 50 tok/s | 80 tok/s | 100+ tok/s |
| Power | <5W | <3W (sim) | <3W | <2.5W |
| Quality (MMLU) | >50% | >52% | >52% | >52% |

## 11.2 Business Milestones

| Metric | Gate 0 | Gate 1 | Gate 2 | Gate 3 |
|--------|--------|--------|--------|--------|
| Customer LOIs | 5 | 15 | 30 | 50+ |
| Pre-orders | 0 | 100 | 500 | 5000+ |
| Revenue | $0 | $0 | $25K | $500K+ |

---

# Appendix A: Reference Implementations

## TeLLMe FPGA (Baseline)

| Metric | Value |
|--------|-------|
| Platform | AMD Kria KV260 |
| Model | BitNet 0.73B |
| Throughput | 25 tok/s |
| Power | 4.8W |
| Innovation | Table-Lookup Matmul |

## BitNet Model Specifications

| Parameter | Value |
|-----------|-------|
| Parameters | 2.4B total |
| Training tokens | 4T |
| Context length | 4096 |
| License | MIT |
| HuggingFace downloads | 16,010/month |

## iFairy Model Specifications

| Parameter | Value |
|-----------|-------|
| Available sizes | 700M, 1.3B |
| Weights | {±1, ±i} |
| License | Apache 2.0 |
| PPL vs FP16 | 10% better (claimed) |

---

# Appendix B: Key Contacts

| Entity | Contact | Purpose |
|--------|---------|---------|
| Peking University (iFairy) | tongyang@pku.edu.cn | Model collaboration |
| KAIST HPIC Lab | hpic-lab.github.io | 2T1C DRAM research |
| TeLLMe Authors | via arXiv | FPGA reference |
| Silicon Catalyst | siliconcatalyst.com | Incubator, tools |
| MOSIS | mosis.com | MPW service |

---

*Document prepared for: Mask-Locked Inference Chip Development*
*Version: Final 1.0*
