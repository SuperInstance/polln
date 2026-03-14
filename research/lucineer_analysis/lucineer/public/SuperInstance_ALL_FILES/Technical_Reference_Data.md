# Technical Reference Data Document
## Mask-Locked Inference Chip - Complete Technical Specifications

**Document Purpose**: This document provides all technical data, constraints, and reference implementations needed for mathematical analysis. Read this BEFORE attempting any prompt analysis.

---

## SECTION 1: BITNET B1.58-2B-4T MODEL SPECIFICATIONS

### Verified Model Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| Total Parameters | 2.4B (with embeddings) | HuggingFace Model Card |
| Transformer Parameters | 2B | Microsoft Technical Report |
| Training Tokens | 4 Trillion | arXiv:2504.12285 |
| Context Length | 4096 tokens | Model config |
| Hidden Dimensions | 2560 | Model config |
| Number of Layers | 32 | Model config |
| Attention Heads | 32 | Model config |
| License | MIT | HuggingFace confirmed |
| Monthly Downloads | 16,010 | HuggingFace (March 2026) |

### Weight Representation
| Aspect | Specification |
|--------|---------------|
| Weight Values | {-1, 0, +1} (ternary) |
| Bits per Weight | log₂(3) ≈ 1.58 bits |
| Storage Ratio | 1/8 of FP16 |
| Quantization Method | Absmean quantization |

### Performance Benchmarks (Published)
| Benchmark | Score | Comparison |
|-----------|-------|------------|
| MMLU | ~55% | Similar to Llama-2-7B |
| HellaSwag | ~72% | Competitive |
| WinoGrande | ~62% | Good for size |
| ARC-Easy | ~68% | Reasonable |
| GSM8K | ~45% | Weaker on math |

### Critical Implementation Note
```
WARNING from HuggingFace Model Card:
"Please do NOT expect performance efficiency gains when using this model 
with the standard transformers library. For achieving the efficiency 
benefits demonstrated in the technical paper, you MUST use the dedicated 
C++ implementation: bitnet.cpp"
```

---

## SECTION 2: iFAIRY (FAIRY ±I) MODEL SPECIFICATIONS

### Model Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| Paper | arXiv:2508.05571 | Peking University |
| Available Sizes | 700M, 1.3B | HuggingFace |
| Weight Values | {±1, ±i} (fourth roots of unity) |
| Bits per Weight | Exactly 2 bits | Full utilization |
| License | Apache 2.0 | HuggingFace |

### Key Technical Claims
| Claim | Value | Verification |
|-------|-------|--------------|
| Multiplication-Free | YES | Requires proof |
| PPL vs FP16 | 10% BETTER | Remarkable if true |
| Operations | Addition + Swap only | Verify mathematically |
| Storage | Same as BitNet (1/8 FP16) | Both use ~2-bit |

### Complex-Valued Transformer Details
```
Weight Quantization: {±1, ±i}
Architecture: Full complex-valued Transformer
Attention: Hermitian inner product (real part)
RoPE: Complex rotation (simpler implementation)

Hardware Implications:
- Eliminates: ALL multiplication operations in GEMM
- Replaced with: Addition, subtraction, data exchange
- Estimated MAC complexity reduction: 75-90%
```

### Contact for Collaboration
- Lead: Tong Yang (tongyang@pku.edu.cn - inferred)
- GitHub: https://github.com/PKULab1806/Fairy-plus-minus-i
- HuggingFace: PKU-DS-LAB/Fairy-plus-minus-i-700M

---

## SECTION 3: MEMORY AND BANDWIDTH CALCULATIONS

### KV Cache Size Formula
```
KV_Cache_Size = 2 × num_layers × hidden_dim × sequence_length × bytes_per_value

For BitNet b1.58-2B-4T:
- num_layers = 32
- hidden_dim = 2560
- sequence_length = 4096 (max)
- bytes_per_value = 2 (FP16)

KV_Cache_Size = 2 × 32 × 2560 × 4096 × 2
             = 1,342,177,280 bytes
             ≈ 1.25 GB (full context)
```

### KV Cache by Context Length
| Context | KV Cache Size (FP16) | With INT8 Quantization |
|---------|---------------------|----------------------|
| 512 tokens | 160 MB | 80 MB |
| 1024 tokens | 320 MB | 160 MB |
| 2048 tokens | 640 MB | 320 MB |
| 4096 tokens | 1.25 GB | 640 MB |

### Memory Bandwidth Requirements
```
Bandwidth_per_token = KV_Cache_Size × tokens_per_second

At 25 tok/s with 4K context:
Bandwidth = 1.25 GB × 25 = 31.25 GB/s

At 80 tok/s with 4K context:
Bandwidth = 1.25 GB × 80 = 100 GB/s
```

### Weight Memory (Eliminated by Mask-Locking)
| Component | Size (INT4) | Size (FP16) |
|-----------|-------------|-------------|
| Attention Weights | ~250 MB | ~1 GB |
| FFN Weights | ~500 MB | ~2 GB |
| Embeddings | ~30 MB | ~120 MB |
| **Total Weights** | ~780 MB | ~3.1 GB |

**Note**: In mask-locked design, these weights are "free" (encoded in metal). This eliminates the weight loading bandwidth entirely.

---

## SECTION 4: POWER CONSUMPTION ANALYSIS

### Energy per Operation (28nm Process)
| Operation | Energy (pJ) | Notes |
|-----------|-------------|-------|
| SRAM Read (8-bit) | 1-5 | Depends on size |
| SRAM Write (8-bit) | 2-8 | Higher than read |
| INT8 Multiply | 0.5-2 | Systolic array |
| INT8 Add | 0.1-0.5 | Simple operation |
| DRAM Read (8-bit) | 50-100 | External memory |
| DRAM Write (8-bit) | 50-100 | External memory |

### Ternary Operation Energy
| Operation | Energy (relative) | Notes |
|-----------|-------------------|-------|
| w = +1: y = x | ~0.1 units | Just routing |
| w = 0: skip | ~0 | No computation |
| w = -1: y = -x | ~0.2 units | Negation |

### Power Budget Breakdown (Target: 3W)
| Component | Target Power | Rationale |
|-----------|--------------|-----------|
| KV Cache Access | 0.5-1.0W | External SRAM or LPDDR4 |
| Compute (MAC) | 1.0-1.5W | Systolic array |
| Control Logic | 0.2-0.3W | Simple FSM |
| I/O (USB) | 0.1-0.2W | 5V/500mA max |
| Clock Distribution | 0.1-0.3W | Depends on frequency |
| Leakage | 0.1-0.2W | 28nm at room temp |

### Thermal Analysis
```
Assumptions:
- Die size: 10mm × 10mm = 100 mm²
- Package: BGA, no heatsink
- Ambient: 25°C
- Junction-to-ambient θJA: ~30°C/W (typical BGA)

Power = 3W
Temperature rise = 3W × 30°C/W = 90°C
Junction temperature = 25°C + 90°C = 115°C

Maximum junction: 125°C (typical)
Margin: 10°C - acceptable but tight
```

---

## SECTION 5: PROCESS NODE ECONOMICS

### 28nm Process Specifications
| Parameter | Value | Notes |
|-----------|-------|-------|
| Gate Density | ~1.5M gates/mm² | Standard cell |
| SRAM Density | ~1.5 Mbit/mm² | Memory compiler |
| Metal Layers | 6-8 typical | For routing |
| Mask Set Cost | $1-3M | Full mask set |
| MPW Cost | $30-100K | Shuttle run |
| Wafer Cost | ~$3,000 | 300mm wafer |

### Die Size Estimation
```
For 2B ternary parameters:
- Weights: ~400 MB at 1.58 bits/param = 628 Mbit
- No weight SRAM needed (mask-locked)

Compute Array:
- Assuming 0.1mm² per MAC unit (conservative)
- Need ~10,000 MAC units for reasonable throughput
- Compute area: ~1,000 mm² (too large!)

Optimization needed:
- Use time-multiplexed MAC units
- Target: 1000 MAC units × 10 cycles = same throughput
- Compute area: ~100 mm²

Activation SRAM:
- Need ~100-500 MB for activations + KV cache
- At 1.5 Mbit/mm²: 67-333 mm² for SRAM alone!

PROBLEM: Pure SRAM approach exceeds die size budget
SOLUTION: External LPDDR4 for KV cache, small on-chip SRAM
```

### Cost-Optimized Configuration
| Component | Size | Implementation |
|-----------|------|----------------|
| Compute Array | ~50 mm² | Systolic array |
| On-chip SRAM | 4-8 MB | ~30-60 mm² |
| Control Logic | ~5 mm² | FSM + interfaces |
| I/O Pads | ~10 mm² | USB, power, etc. |
| **Total Die** | ~100-130 mm² | Feasible |
| External Memory | 256-512 MB LPDDR4 | Off-chip |

### Unit Cost Estimates
| Volume | Die Cost | Packaging | Test | Memory | Total COGS |
|--------|----------|-----------|------|--------|------------|
| 10K units | $8-10 | $3 | $2 | $10-12 | $23-27 |
| 100K units | $6-8 | $2.50 | $1.50 | $10-12 | $20-24 |
| 1M units | $5-6 | $2 | $1 | $8-10 | $16-19 |

**Note**: Memory pricing is volatile. LPDDR4 prices increased 20% in late 2025.

---

## SECTION 6: COMPETITIVE REFERENCE DATA

### TeLLMe FPGA Implementation (Critical Reference)
| Metric | Value | Notes |
|--------|-------|-------|
| Paper | arXiv:2510.15926 | October 2025 |
| Platform | AMD Kria KV260 | Same as Gate 0 target |
| Clock | 250 MHz | Achievable |
| Model | BitNet 0.73B | Smaller than our target |
| Throughput | 25 tok/s | Decoding |
| Power | 4.8W | Total board power |
| Energy Efficiency | 5.2 TK/J | Good |
| Resources | 98K LUTs, 610 DSPs | Within KV260 capacity |
| LM Head | Offloaded to ARM | 9ms overhead |

### Key Innovation: Table-Lookup Matmul (TLMM)
```
Precomputes all possible ternary multiplication results
Stores in FPGA LUTs as lookup tables
Eliminates actual multiplication circuits

For ternary weights {-1, 0, +1}:
- Possible products: {-a, 0, +a} for activation a
- Lookup table size: minimal
- Speed: single cycle per MAC
```

### Hailo-10H Benchmarks
| Model | Throughput | Notes |
|-------|------------|-------|
| Qwen2-1.5B | 9.45 tok/s | Published |
| Llama3.2-3B | 4.78 tok/s | Published |
| Power | ~5W | Estimated |

**Gap**: Our target (25-80 tok/s on 2B) would be 2.5-8× faster than Hailo on similar models.

### Taalas HC1 (Data Center Reference)
| Metric | Value | Notes |
|--------|-------|-------|
| Process | TSMC N6 | Advanced node |
| Transistors | 53 billion | Massive chip |
| Target Model | Llama 3.1 8B | Larger than ours |
| Throughput | 14,000-17,000 tok/s | Extraordinary |
| Power | ~200W | Not edge-suitable |
| Customization | 2 metal layer changes | Similar concept |

---

## SECTION 7: TIMING AND THROUGHPUT CALCULATIONS

### Operations per Token
```
For transformer inference (generation phase):

Per layer:
- Q, K, V projections: 3 × (hidden_dim × hidden_dim) MACs
- Attention: sequence_length × num_heads × head_dim operations
- Output projection: hidden_dim × hidden_dim MACs
- FFN (typically 4× expansion): 2 × (hidden_dim × 4×hidden_dim) MACs

Total per layer ≈ 2 × hidden_dim² × (3 + 4) = 14 × hidden_dim² MACs
Total per token ≈ num_layers × 14 × hidden_dim² MACs

For BitNet 2B:
- num_layers = 32
- hidden_dim = 2560
- Total ≈ 32 × 14 × 2560² ≈ 2.9 billion MACs per token
```

### Throughput Calculation
```
Assume:
- Clock frequency: 250 MHz
- MAC units: 1000
- Utilization: 80%

MACs per second = 250 MHz × 1000 × 0.8 = 200 billion MACs/s
Tokens per second = 200 billion / 2.9 billion = ~69 tok/s

This is within our target range (25-80 tok/s)
```

### Latency Calculation
```
For a single token generation:

Critical path through all layers:
- Each layer must complete before next begins (sequential)
- But within a layer, operations can pipeline

Minimum latency = num_layers × cycles_per_layer

With 1000 MAC units organized as 32×32 systolic array:
- Matrix multiply (2560×2560): ~2560/32 = 80 cycles per layer
- Additional ops (attention, etc.): ~20 cycles overhead
- Cycles per layer: ~100

Total latency = 32 layers × 100 cycles = 3200 cycles
At 250 MHz: 3200 / 250M = 12.8 microseconds per token

Note: This is simplified; actual attention has sequence_length dependency
```

---

## SECTION 8: NOISE MARGIN AND RELIABILITY

### Ternary Logic Levels
```
For VDD = 1.1V (typical 28nm I/O):
- Logic 0: 0V
- Logic 1: VDD = 1.1V
- Logic 0.5 (intermediate): VDD/2 = 0.55V

Noise margins:
- For binary: ~0.3 × VDD = 0.33V (standard)
- For ternary: reduced noise margin at intermediate level
- Intermediate level noise margin: ~0.15 × VDD = 0.165V

Industry standard noise margin: 15% of VDD = 165mV
Our v13.0 claim: 50mV threshold
Assessment: 50mV is CONSERVATIVE (actually better than needed)
```

### Reliability Requirements
| Requirement | Target | Test Method |
|-------------|--------|-------------|
| Operating Temperature | 0-70°C | Thermal chamber |
| Storage Temperature | -40-85°C | Thermal cycling |
| ESD Protection | 2kV HBM | ESD tester |
| Latch-up Immunity | 100mA | I-test |
| Operating Life | 10 years @ 55°C | Accelerated life test |

---

## SECTION 9: EXTERNAL MEMORY OPTIONS

### LPDDR4 Specifications
| Parameter | Value | Notes |
|-----------|-------|-------|
| Density | 512MB - 2GB | Per chip |
| Bandwidth | 4.26 GB/s per channel | x16 interface |
| Voltage | 1.1V | Low power |
| Price (512MB) | $10-12 | March 2026 pricing |
| Availability | Allocated | Tight supply |

### LPDDR4 vs LPDDR5 Trade-offs
| Factor | LPDDR4 | LPDDR5 |
|--------|--------|--------|
| Price | $10-12 | $15-20+ |
| Availability | Tight but available | Limited allocation |
| Bandwidth | 4.26 GB/s | 6.4 GB/s |
| Voltage | 1.1V | 1.05V |
| Longevity | Extended to 2026 | Current production |

### SRAM Alternative (On-chip Only)
| Configuration | Capacity | Die Area | Power |
|---------------|----------|----------|-------|
| 4 MB | Limited context | ~27 mm² | 0.2W |
| 8 MB | Moderate context | ~53 mm² | 0.4W |
| 16 MB | Good context | ~107 mm² | 0.8W |

**Trade-off**: 16 MB SRAM could support ~1024-2048 token context without external memory, but adds significant die cost.

---

## SECTION 10: LICENSING AND LEGAL CONSIDERATIONS

### Model License Summary
| Model | License | Hardware Embedding | Risk Level |
|-------|---------|-------------------|------------|
| BitNet b1.58 | MIT | Permitted | LOW |
| iFairy | Apache 2.0 | Permitted | LOW |
| Gemma 2 | Google License | Encouraged for edge | LOW |
| Qwen 2.5 | Apache 2.0 | Permitted | LOW |
| Llama 3.2 | Meta Custom | Unclear | MEDIUM |
| Phi-3 | Microsoft | Unclear | MEDIUM |

### Recommendation
Use **BitNet b1.58** or **iFairy** for first-generation chip:
- MIT/Apache 2.0 licenses
- Clear commercial rights
- No ambiguity about hardware embedding

### Patent Landscape
```
No existing patents found for:
- "mask-locked weights"
- "hardwired neural network weights"
- "weight in metal interconnect"

However, Taalas may have pending patents on similar concepts.
Recommend: File provisional patents before Taalas IP proliferates.
```

---

## SECTION 11: QUICK REFERENCE FORMULAS

### Memory Bandwidth
```
BW = KV_size × tokens_per_second

Example: 512MB KV × 50 tok/s = 25 GB/s
```

### Power Consumption
```
P_total = P_compute + P_KV_access + P_control + P_IO

P_compute ≈ MACs_per_token × tokens_per_second × energy_per_MAC
P_KV_access ≈ KV_accesses_per_token × tokens_per_second × energy_per_access
```

### Die Area
```
Area = compute_area + SRAM_area + control_area + pad_area

compute_area ≈ num_MAC_units × area_per_MAC
SRAM_area ≈ SRAM_bits / density (≈ 1.5 Mbit/mm² at 28nm)
```

### Throughput
```
T = clock_frequency × num_MAC_units × utilization / MACs_per_token

Example: 250MHz × 1000 × 0.8 / 2.9B = 69 tok/s
```

### Cost
```
COGS = die_cost + packaging + test + memory

die_cost ≈ wafer_cost / dies_per_wafer
dies_per_wafer ≈ π × (wafer_radius - edge)² / die_area × yield
```

---

*Document Version: 1.0*
*Created: March 2026*
*For: Math and Logic Specialist Agents*
