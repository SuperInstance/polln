# Mask-Locked Inference Chip: Deep Dive v2.0
## Comprehensive Technical Architecture, Competitive Landscape & Risk Analysis

**Document Classification:** Technical Deep Dive - Confidential  
**Version:** 2.0 (Master Synthesis)  
**Date:** March 2026  
**Prepared For:** Technical Leadership, Engineering Team, Due Diligence

---

# Executive Summary

This deep dive document provides comprehensive technical analysis of the mask-locked inference chip architecture, synthesizing all research from Cycles 1 and 2. The analysis validates the technical feasibility of the approach while identifying critical implementation details and risk mitigation strategies.

## Key Technical Findings

| Finding | Status | Confidence |
|---------|--------|------------|
| **BitNet b1.58-2B validated** | Production-ready model available | HIGH |
| **Ternary inference practical** | TeLLMe proves 25 tok/s at 4.8W | HIGH |
| **iFairy multiplication-free** | Addition-only operations proven | HIGH |
| **No blocking patents** | Freedom-to-operate confirmed | MEDIUM |
| **28nm optimal process** | Cost-performance balance validated | HIGH |
| **18-24 month moat** | Competitive window identified | MEDIUM |

---

# Part 1: Technical Architecture Deep Dive

## 1.1 The Mask-Locked Concept

### Fundamental Principle

Traditional AI chips load neural network weights from memory during inference, creating a fundamental bottleneck:
- Memory bandwidth limits throughput
- Memory access consumes significant power
- Flexibility overhead increases cost and complexity

**Mask-locked architecture** eliminates this bottleneck by encoding weights directly into silicon metal interconnect layers.

### Weight Stationary Comparison

| Architecture | Weight Storage | Access Energy | Flexibility |
|--------------|---------------|---------------|-------------|
| **Traditional GPU/NPU** | External DRAM | ~25 pJ/bit/access | Full |
| **SRAM-based (Groq)** | On-chip SRAM | ~10 pJ/bit/access | Model-swappable |
| **Architecture-ASIC (Etched)** | External HBM | ~7 pJ/bit/access | Architecture-fixed |
| **Mask-Locked** | Metal interconnect | ~0.1 pJ/bit/access | None |

### Technical Implementation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Mask-Locked Ternary Chip Architecture           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Metal Interconnect Layers                   │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │   │
│  │  │ W₁₁ │ │ W₁₂ │ │ W₁₃ │ │ ... │ │Wₙₘ₋₁│ │ Wₙₘ │ │Fixed│ │   │
│  │  │ =+1 │ │ = 0 │ │ =-1 │ │     │ │     │ │     │ │     │ │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Ternary Processing Elements                 │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │
│  │  │ PE[0,0] │  │ PE[0,1] │  │ PE[0,2] │  │   ...   │       │   │
│  │  │  Adder  │  │  Adder  │  │  Adder  │  │         │       │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               Activation SRAM (Mutable State)               │   │
│  │   ├── KV Cache (2K context): ~4 MB                         │   │
│  │   ├── Input Buffer: ~256 KB                                │   │
│  │   └── Output Buffer: ~256 KB                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    I/O Interface                            │   │
│  │   USB 3.0 / PCIe / M.2 (Simple token in/out)              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 1.2 BitNet b1.58 Architecture Analysis

### Weight Quantization

| Property | Value |
|----------|-------|
| **Weight Values** | {-1, 0, +1} |
| **Bits per Weight** | log₂(3) ≈ 1.585 bits |
| **Quantization Method** | AbsMean with learned scale |
| **Quality vs FP16** | Equivalent (perplexity) |

### BitLinear Layer Implementation

```python
# Conceptual implementation of BitLinear
class BitLinear(nn.Linear):
    def forward(self, x):
        # Quantize weights to {-1, 0, +1}
        scale = torch.mean(torch.abs(W)) + 1e-8
        W_q = torch.round(W / scale)
        W_q = torch.clamp(W_q, -1, 1)
        
        # Ternary matrix multiplication (multiplication-free)
        # For W ∈ {-1, 0, +1}:
        # y = x @ W_q becomes:
        # - Sum of x where W_q = +1
        # - Minus sum of x where W_q = -1
        # - Zero contribution where W_q = 0
```

### Performance Benchmarks (bitnet.cpp v1.0)

| Platform | Speedup | Energy Reduction |
|----------|---------|------------------|
| **x86 CPU (Intel)** | 2.37x - 6.17x | 71.9% - 82.2% |
| **ARM CPU (Apple M2)** | 1.37x - 5.07x | 55.4% - 70.0% |

## 1.3 iFairy Complex-Valued LLM

### Technical Innovation

**Paper:** arXiv:2508.05571  
**Institution:** Peking University  
**License:** Apache 2.0

| Property | Value |
|----------|-------|
| **Weight Values** | {+1, -1, +i, -i} |
| **Bits per Weight** | Exactly 2 bits |
| **Inference Operations** | Additions + swaps only |
| **Multipliers Needed** | ZERO |

### Multiplication Elimination

```
Traditional Complex Multiply:
(a + bi) × (c + di) = (ac - bd) + (ad + bc)i
Requires: 4 multipliers + 2 adders

iFairy Complex Multiply (w ∈ {±1, ±i}):
X × {+1} = X         → Just pass through
X × {-1} = -X        → Just negate  
X × {+i} = iX        → Swap real/imag, negate one
X × {-i} = -iX       → Swap real/imag, negate both
Requires: 0 multipliers, only adders and swaps
```

### Hardware Savings Estimate

| Component | Traditional | iFairy | Savings |
|-----------|-------------|--------|---------|
| **MAC Units** | Multipliers + Accumulators | Adders + Swaps | 75-90% area reduction |
| **Power** | ~100 units/MAC | ~10 units/MAC | 90% reduction |
| **Latency** | Multiple cycles | Single cycle | 2-4× faster |

## 1.4 TeLLMe FPGA Reference Design

### Architecture Overview (arXiv:2510.15926)

| Component | Specification |
|-----------|--------------|
| **Platform** | AMD Kria KV260 (Zynq UltraScale+ XCK26) |
| **Model** | BitNet 0.73B |
| **Core Innovation** | Table-Lookup MatMul (TLMM) |
| **Clock** | 250 MHz |
| **Throughput** | 25 tokens/s (decoding) |
| **Power** | 4.8W |

### TLMM Engine Design

**Principle:** Pre-compute all possible ternary multiplication results and store in FPGA LUTs.

```
Ternary Weight Encoding:
┌─────────────────────────────────┐
│ Weight Value │ 2-bit Encoding   │
├──────────────┼──────────────────┤
│     -1       │      00          │ → Negate input
│      0       │      01          │ → Zero output  
│     +1       │      10          │ → Pass input
│   Reserved   │      11          │ → Unused
└─────────────────────────┬───────┘
                          │
                          ▼
┌─────────────────────────────────┐
│  Activation Dequantization      │
│  4-bit index → 16-level lookup  │
│  Symmetric quantization around 0│
└─────────────────────────────────┘
```

### Resource Utilization

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| **LUTs** | 98,303 | 117,120 | 84% |
| **FFs** | 136,721 | 234,240 | 28% |
| **DSPs** | 610 | 1,240 | 49% |
| **BRAM** | 98.5 | 144 | 68% |
| **URAM** | 60 | 64 | 94% |

---

# Part 2: Memory Architecture

## 2.1 Memory Requirements Analysis

### BitNet-2B Layer Memory Requirements

| Layer Type | Parameters | Ternary Storage | BRAM (36Kb) |
|------------|------------|-----------------|-------------|
| **Attention Q/K/V** | 3 × 2048 × 2048 | 1.5 MB each | 43 each |
| **Attention Output** | 2048 × 2048 | 0.5 MB | 14 |
| **FFN Up** | 2048 × 8192 | 2 MB | 57 |
| **FFN Down** | 8192 × 2048 | 2 MB | 57 |
| **FFN Gate** | 2048 × 8192 | 2 MB | 57 |
| **Embedding** | 32000 × 2048 | 0.5 MB (INT8) | 14 |
| **Total** | ~2.4B | ~8.5 MB | ~300 |

### KV Cache Requirements

| Configuration | Memory Required | BRAM Usage |
|---------------|-----------------|------------|
| **512 context** | 32 BRAMs | ✅ Fits KV260 |
| **1024 context** | 64 BRAMs | ✅ Fits KV260 |
| **2048 context** | 128 BRAMs | ✅ Fits KV260 (95%) |
| **4096 context** | 256 BRAMs | ❌ Requires DDR4 |

## 2.2 Memory Technology Selection

### LPDDR5X Analysis

| Specification | Value |
|---------------|-------|
| **Speed** | 8.5 Gbps |
| **Bandwidth (32-bit)** | 68 GB/s |
| **Price (1GB)** | $6-8 |
| **Power** | Low-power optimized |
| **Availability** | Good (Samsung, SK Hynix, Micron) |

### On-Chip SRAM Requirements

| Component | Size | Purpose |
|-----------|------|---------|
| **KV Cache** | 4-8 MB | Context storage |
| **Weight Buffer** | 2-4 MB | Layer streaming |
| **Activation Buffer** | 1-2 MB | Intermediate results |
| **Total** | 8-16 MB | On-chip SRAM |

## 2.3 Memory Bandwidth Analysis

### Bandwidth Requirements for 50 tok/s

| Operation | Data Moved | Bandwidth Required |
|-----------|------------|-------------------|
| **Weight streaming** | 400 MB/layer | 8 GB/s |
| **KV Cache read** | 0.5 MB/token | 25 MB/s |
| **Activation IO** | 2 MB/token | 100 MB/s |
| **Total** | ~8 GB/s | 61% LPDDR5X utilization |

---

# Part 3: Process Node Selection

## 3.1 Node Comparison

| Node | Mask Cost | Wafer Cost | Density | Power | Recommendation |
|------|-----------|------------|---------|-------|----------------|
| **130nm** | $50-100K | $800-1,200 | Low | High | ❌ Too large |
| **40nm** | $500K-1M | $2,500-3,500 | Medium | Medium | ⚠️ Alternative |
| **28nm** | $1.2-1.8M | $3,500-4,500 | Good | Good | ✅ **Recommended** |
| **14nm** | $4-6M | $6,000-8,000 | High | Low | ❌ Too expensive |
| **7nm** | $12-15M | $10,000+ | Very High | Very Low | ❌ Overkill |

## 3.2 Die Size Estimation

### 2B Ternary Model at 28nm

| Component | Area (mm²) | Notes |
|-----------|------------|-------|
| **Ternary Weight ROM** | 15-25 mm² | Dense ROM synthesis |
| **Compute Array** | 8-12 mm² | Adder-only MAC |
| **Activation SRAM** | 6-10 mm² | 6T SRAM |
| **Control Logic** | 3-5 mm² | FSM + counters |
| **I/O & Pad Ring** | 4-6 mm² | 64-128 pins |
| **Total** | **36-58 mm²** | Target: 50 mm² |

### Yield Analysis

| Die Size | Defect Density | Yield | Good Dies/Wafer |
|----------|---------------|-------|-----------------|
| **30 mm²** | 0.3/cm² | 92% | ~480 |
| **50 mm²** | 0.3/cm² | 86% | ~260 |
| **70 mm²** | 0.3/cm² | 81% | ~165 |

---

# Part 4: Competitive Landscape Analysis

## 4.1 Direct Competitor Analysis

### Taalas Corporation

| Attribute | Detail |
|-----------|--------|
| **Total Funding** | $219M ($50M seed + $169M Series A, Feb 2026) |
| **Technology** | Mask ROM + SRAM recall fabric |
| **Process** | TSMC N6 (6nm) |
| **Target Market** | Datacenter (200W+ chips) |
| **Performance** | 14,000-17,000 tok/s (Llama 3.1 8B) |
| **Edge Signals** | **NONE detected** |
| **Threat Level** | LOW (different market, 18-24 month window) |

### Hailo

| Attribute | Detail |
|-----------|--------|
| **Total Funding** | $400M+ (Series C extended) |
| **Key Product** | Hailo-10H AI HAT+ |
| **LLM Performance** | 5-10 tok/s (Qwen2-1.5B, Llama3.2-3B) |
| **Power** | ~5W |
| **Price** | $70-90 |
| **Partnership** | Raspberry Pi (exclusive AI HAT) |
| **Threat Level** | HIGH (shipping products, but poor LLM performance) |

### Quadric

| Attribute | Detail |
|-----------|--------|
| **Total Funding** | $72M ($30M Series C, Jan 2026) |
| **Technology** | Chimera GPNPU (programmable NPU) |
| **Focus** | Edge LLM inference IP |
| **Differentiation** | Runs any model (flexibility) |
| **Threat Level** | MEDIUM (IP competitor, not silicon) |

### Axelera AI

| Attribute | Detail |
|-----------|--------|
| **Total Funding** | $250M+ (Series B) |
| **Product** | Metis AIPU (214 TOPS, ~10W) |
| **Technology** | Digital In-Memory Computing |
| **Focus** | Vision + GenAI (not LLM-optimized) |
| **Threat Level** | MEDIUM (different focus) |

## 4.2 Competitive Positioning Matrix

```
                        Flexibility
                   Low ←────────────→ High
                     │                │
        ┌────────────┼────────────────┼────────────┐
        │            │                │            │
   H    │  SUPERINSTANCE│              │   Jetson   │
   i    │  (Best Value) │              │  Orin Nano │
   g    │  80-150 t/s   │              │  20-30 t/s │
   h    │  $35-60       │              │  $250+     │
        │            │                │            │
   P    ├────────────┼────────────────┼────────────┤
   r    │            │                │            │
   i    │  Hailo     │                │   Quadric  │
   c    │  5-10 t/s  │                │  Unknown   │
   e    │  $70-90    │                │  $100+     │
        │            │                │            │
   L    ├────────────┼────────────────┼────────────┤
   o    │            │                │            │
   w    │  Coral     │                │   Groq     │
        │  (EOL)     │                │  (Cloud)   │
        │  No LLM    │                │  300+ t/s  │
        │            │                │            │
        └────────────┴────────────────┴────────────┘
```

---

# Part 5: Risk Assessment

## 5.1 Technical Risk Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Model Obsolescence** | 40% | HIGH | Target stable models (BitNet, Gemma); design for model variants |
| **Quantization Quality** | 25% | HIGH | Extensive QAT; mixed-precision fallback; layer-specific quantization |
| **First-Silicon Bugs** | 30% | HIGH | Comprehensive FPGA prototype; formal verification; conservative timing |
| **Memory Supply Shortage** | 20% | MEDIUM | Lock contracts early; multi-supplier strategy; design flexibility |
| **Yield Issues** | 10% | MEDIUM | Mature node; established PDK; conservative design rules |

## 5.2 Competitive Risk Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Taalas Edge Pivot** | 25% | HIGH | First-mover advantage; patent protection; customer relationships |
| **Hailo LLM Optimization** | 40% | MEDIUM | Architecture advantage (ternary-native); price differentiation |
| **New Well-Funded Entrant** | 30% | MEDIUM | Speed to market; IP portfolio; brand building |
| **NVIDIA Price Pressure** | 15% | MEDIUM | Zero-setup value prop; power efficiency; different customer segment |

## 5.3 Execution Risk Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Team Assembly Failure** | 40% | CRITICAL | Silicon Catalyst incubator; competitive equity packages |
| **Funding Gap** | 35% | CRITICAL | Milestone-based execution; government grants; early investor relationships |
| **Foundry Allocation** | 25% | HIGH | Early engagement; MPW first; multi-foundry design |
| **Schedule Overrun** | 60% | MEDIUM | Conservative estimates; parallel paths; risk budget |

---

# Part 6: Implementation Considerations

## 6.1 Design Flow Recommendation

```
┌─────────────────────────────────────────────────────────────────┐
│                    Recommended Design Flow                       │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: FPGA Prototype (Months 1-6)                          │
│  ├── Implement TLMM-based inference on KV260                   │
│  ├── Validate 25+ tok/s throughput                             │
│  ├── Verify <5W power consumption                              │
│  └── Gate 0 milestone                                          │
│                                                                 │
│  Phase 2: RTL Development (Months 7-12)                        │
│  ├── Chisel/Scala parameterized design                         │
│  ├── Weight-to-Verilog conversion tools                        │
│  ├── Comprehensive testbenches                                 │
│  └── Gate 1 milestone (architecture freeze)                    │
│                                                                 │
│  Phase 3: Physical Design (Months 13-18)                       │
│  ├── Synthesis to 28nm                                         │
│  ├── Place & route                                             │
│  ├── Timing closure                                            │
│  └── MPW tapeout                                               │
│                                                                 │
│  Phase 4: Validation (Months 19-24)                            │
│  ├── Silicon bring-up                                          │
│  ├── Performance characterization                              │
│  └── Volume production ramp                                    │
└─────────────────────────────────────────────────────────────────┘
```

## 6.2 Tool Recommendations

| Function | Tool | Cost | Notes |
|----------|------|------|-------|
| **RTL Development** | Chisel/Scala | Free | Parameterized design |
| **Simulation** | Verilator | Free | Fast cycle-accurate simulation |
| **Synthesis** | Yosys + ABC | Free | Open-source, adequate for 28nm |
| **Place & Route** | OpenROAD | Free | Production-ready for 28nm |
| **Verification** | Verilator + Cocotb | Free | Python-based testbenches |
| **Formal Verification** | SymbiYosys | Free | Open-source formal |

**Silicon Catalyst Alternative:** Free access to Synopsys/Cadence tools worth $2M+/year.

## 6.3 MPW Strategy

| Provider | Node | Cost | Schedule |
|----------|------|------|----------|
| **MOSIS (TSMC)** | 28nm | $150K-300K | Quarterly shuttles |
| **CMP (Europractice)** | 28nm | €120K-200K | Bi-monthly |
| **Efabless** | SkyWater 130nm | $9K-15K | Monthly (too small for 2B model) |

**Recommendation:** Use MOSIS TSMC 28nm MPW for prototype, then full mask set for production.

---

# Part 7: Technical Specifications Summary

## 7.1 Target Specifications

| Parameter | Specification |
|-----------|--------------|
| **Model** | BitNet b1.58-2B-4T (or iFairy 2B) |
| **Throughput** | 80-150 tok/s |
| **Power** | 2-3W active, <0.5W idle |
| **Price** | $35-60 (retail) |
| **Process** | TSMC 28nm HPC |
| **Die Size** | ~50 mm² |
| **Package** | BGA-256 or USB module |
| **Interface** | USB 3.0 / PCIe Gen2 |

## 7.2 Performance Targets

| Metric | Target | Reference |
|--------|--------|-----------|
| **Tokens/Second** | 80-150 | TeLLMe baseline: 25 tok/s |
| **Energy/Token** | < 30 µJ/token | Hailo: ~500 µJ/token |
| **Tokens/Watt** | 27-50 | Hailo: 1-2 tok/W |
| **Latency (TTFT)** | < 200ms | For 128-token prompt |
| **Context Length** | 2048 tokens | KV cache limited |

## 7.3 Competitive Comparison

| Metric | SuperInstance | Hailo-10H | Jetson Nano | TeLLMe |
|--------|--------------|-----------|-------------|--------|
| **Throughput** | 80-150 t/s | 5-10 t/s | 20-30 t/s | 25 t/s |
| **Power** | 2-3W | 5W | 7-15W | 4.8W |
| **Tokens/Watt** | 27-50 | 1-2 | 2-3 | 5.2 |
| **Price** | $35-60 | $70-90 | $99-249 | N/A (research) |
| **Setup** | Zero | Hours | Days | Days |

---

# Part 8: Recommendations

## 8.1 Technical Recommendations

1. **Use iFairy for v2.0**: Apache 2.0 license with patent grant provides clearer IP position than BitNet's MIT license
2. **Target 28nm TSMC**: Optimal balance of cost, performance, and ecosystem support
3. **FPGA prototype first**: Validate TLMM approach on KV260 before committing to silicon
4. **Design for multiple models**: Parameterized RTL allows quick derivative chips

## 8.2 Risk Mitigation Recommendations

1. **File patents immediately**: Establish priority before Taalas potentially enters edge market
2. **Lock memory supply**: Secure LPDDR5X allocation before production ramp
3. **Build IP portfolio**: Target 10+ patents in first year for acquisition value
4. **Maintain design flexibility**: Support multiple quantization schemes (ternary, 2-bit complex, INT4)

## 8.3 Next Steps

| Priority | Action | Timeline | Owner |
|----------|--------|----------|-------|
| **CRITICAL** | File provisional patents | Week 1-2 | Founder + IP Counsel |
| **CRITICAL** | Begin FPGA prototype | Month 1-3 | Engineering Lead |
| **HIGH** | Contact TeLLMe authors | Week 1-2 | Founder |
| **HIGH** | Contact PKU (iFairy) | Week 1-2 | Founder |
| **MEDIUM** | Apply to Silicon Catalyst | Month 1 | Founder |

---

*Document Classification: Technical Deep Dive - Confidential*  
*Version: 2.0 (Master Synthesis)*  
*Sources: Cycles 1-2 Research, arXiv Papers, Vendor Specifications*  
*Distribution: Technical Leadership, Engineering Team, Due Diligence*
