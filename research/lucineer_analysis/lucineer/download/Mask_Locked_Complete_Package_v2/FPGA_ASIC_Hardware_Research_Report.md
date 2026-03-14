# FPGA/ASIC Hardware Architecture Research Report
## AI Inference Accelerators for LLMs - Deep Technical Analysis

**Research Date:** January 2025
**Focus Areas:** TeLLMe FPGA Implementation, Systolic Arrays, FPGA LLM Acceleration, Mask-Locked Implementation, Open-Source ASIC Design

---

## 1. Executive Summary of Key Findings

### Critical Discoveries:

1. **TeLLMe v2 Breakthrough**: First end-to-end ternary LLM accelerator achieving 25 tokens/s at 4.8W on AMD KV260 (edge FPGA), with table-lookup matmul (TLMM) engine reducing LUT usage by 46% compared to naive selection-based approaches.

2. **TENET Architecture**: Microsoft Research's LUT-centric ASIC achieves 2.7× speedup over A100 GPU with 21.1× better energy efficiency for ternary LLMs, demonstrating ASIC viability for edge deployment.

3. **FlightLLM High-End Performance**: 153 tokens/s on Alveo U280 with 6× higher energy efficiency than NVIDIA V100S, proving FPGA competitiveness for LLM inference.

4. **Open-Source ASIC Maturity**: Basilisk SoC achieves 77 MHz (2.3× improvement) using OpenROAD flow with IHP 130nm PDK, validating open-source EDA for production designs.

5. **Ternary Quantization Dominance**: BitNet b1.58 achieves best Intelligence-Per-Joule (IPJ) metric, enabling 1.58-bit weight representation with minimal accuracy loss.

---

## 2. TeLLMe Implementation Analysis

### 2.1 Paper Reference
- **arXiv:2510.15926** - "TeLLMe v2: An Efficient End-to-End Ternary LLM Prefill and Decode Accelerator with Table-Lookup Matmul on Edge FPGAs"
- Authors: Ye Qiao, Zhiheng Chen, Yifan Zhang, Yian Wang, Sitao Huang (UC Irvine)
- Published: October 2025

### 2.2 Key Technical Innovations

#### Table-Lookup Matmul (TLMM) Engine
The TLMM engine is the core innovation enabling efficient ternary weight processing:

**Design Principle:**
- Ternary weights {-1, 0, +1} require only selection operations, not multiplication
- Grouped activations (G=3) with online precomputation
- Precompute tree reduces LUT consumption from 43,176 to 23,082 (46% reduction)

**Mathematical Formulation:**
```
For grouped activations with G elements:
- 27 possible combinations (3^G for ternary)
- Full Storage Table Lookup stores all 27 combinations
- Symmetric precomputation exploits weight value symmetry
```

**Resource Optimization:**
| Design Method | LUT Usage | Reduction |
|---------------|-----------|-----------|
| Naive Selection (Method 1) | 43,176 | Baseline |
| Partial Storage (Method 2) | 35,200 | 18% |
| Full Storage (Ours) | 23,082 | 46% |

### 2.3 Resource Utilization on AMD KV260

| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUT | 98,303 | 117,120 | **84%** |
| FF | 136,721 | 234,240 | 28% |
| DSP | 610 | 1,240 | **49%** |
| BRAM | 98.5 | 144 | **68%** |
| URAM | 60 | 64 | **94%** |

**Breakdown by Module:**
- TLMM-FUSE Unit: 43,137 LUTs, 320 DSPs
- RPA Unit (Prefill Attention): 18,072 LUTs, 115 DSPs
- DA Unit (Decoding Attention): 9,570 LUTs, 123 DSPs
- WBMU Unit: 6,885 LUTs, 48 URAMs

### 2.4 Performance Metrics

| Metric | Value | Context |
|--------|-------|---------|
| Decoding Throughput | **25 tokens/s** | Max at short prompts |
| Prefill Throughput | **143 tokens/s** | Peak performance |
| TTFT (64-128 tokens) | 0.45-0.96 s | Time-to-first-token |
| Power Consumption | **4.8W** | Under 5W budget |
| Energy Efficiency | **5.2 TK/J** | Tokens per Joule |
| Clock Frequency | ~250 MHz | Edge FPGA optimized |

### 2.5 Weight Buffer Management Unit (WBMU)

**URAM Optimization:**
- URAM size: 72-bit width × 4096 depth
- Equivalent to 16 BRAM18K blocks
- Fine-grained cyclic partitioning for parallel access

**Parameter Selection Formula:**
```
T = floor(72 × c_URAM / B_idx)

Where:
- T = Number of TL tables
- c_URAM = Cascade factor
- B_idx = Index bit width
```

**AXI Interface Configuration:**
- 3 High-Performance ports (HP0, HP1, HP3)
- 256-bit data width
- Burst size: 16
- Combined bandwidth: 768 bits/cycle

### 2.6 Comparison with Alternatives

| Platform | Model | Power | Throughput | Energy Eff. |
|----------|-------|-------|------------|-------------|
| TeLLMe (KV260) | BitNet 0.73B | 4.8W | 25 tok/s | 5.2 TK/J |
| MEADOW (ZCU102) | OPT 1.3B | 10W | 2 tok/s | 0.20 TK/J |
| LLaMAF (ZCU102) | TinyLLaMA 1.1B | 5.1W | 1.5 tok/s | 0.29 TK/J |
| Jetson Orin Nano | TinyLLaMA 1.1B | 25W | 67.6 tok/s | 2.70 TK/J |
| Raspberry Pi 5 | Qwen 0.6B | 7.8W | 16.6 tok/s | 2.12 TK/J |

---

## 3. Systolic Array Design Options

### 3.1 Google TPU Architecture Reference

**Flex-TPU (arXiv:2407.08700):**
- Runtime reconfigurable dataflow architecture
- Dynamically switches between input/output/weight stationary
- 2.75× performance improvement over fixed dataflow
- Minor area/power overheads

**Traditional TPU Dataflows:**
| Dataflow | Best For | Limitation |
|----------|----------|------------|
| Weight Stationary | Conv layers | High input reuse needed |
| Input Stationary | Low reuse ops | Output accumulation |
| Output Stationary | Batch processing | Weight reloading |

### 3.2 Ternary-Network-Specific Systolic Designs

#### Weight-Stationary for Ternary Weights:
- Ternary weights eliminate multiplication entirely
- Only addition/subtraction/zero operations needed
- Row of PEs shares single weight value
- Activations stream through array

**Optimization Strategies:**
1. **Hardwired Weight Matrix**: Fixed weights in metal layers
2. **Compressed Weight Streaming**: 2-bit encoding per weight
3. **Sparse Matrix Handling**: Skip zero-weight operations

### 3.3 SiTe CiM: Signed Ternary Compute-in-Memory

**arXiv:2408.13617** - Ternary DNN accelerator:

| Memory Type | Area Overhead | CiM Latency | Energy Savings |
|-------------|---------------|-------------|----------------|
| 8T-SRAM | 18-34% | 88% reduction | 78% savings |
| 3T-eDRAM | 6% | Moderate | Good |
| FEMFET | Variable | Fast | High |

**Key Features:**
- Cross-coupled bit cells for signed ternary operations
- Two flavors: SiTe CiM I (fast) and SiTe CiM II (compact)
- 7× throughput boost vs near-memory computing

---

## 4. FPGA LLM Acceleration (2024-2025)

### 4.1 High-End FPGA Solutions

#### FlightLLM (arXiv:2401.03868)
**Platform:** Xilinx Alveo U280 / Versal VHK158

| Metric | Value |
|--------|-------|
| Throughput (LLaMA2-7B) | **153 tokens/s** |
| Energy Efficiency | 6× vs NVIDIA V100S |
| Cost Efficiency | 1.8× vs GPU |
| vs A100 GPU | 1.2× higher throughput |

**Key Techniques:**
- Configurable sparse DSP chain
- Always-on-chip decode scheme
- Mixed-precision support
- Length-adaptive compilation

### 4.2 Edge FPGA Solutions

#### TENET (arXiv:2509.13765)
**Microsoft Research - FPGA and ASIC implementations:**

| Platform | Speedup vs A100 | Energy Efficiency |
|----------|-----------------|-------------------|
| TENET-FPGA | 1.8× | 4.3× improvement |
| TENET-ASIC | **2.7×** | **21.1× improvement** |

**Architecture:**
- Sparse Ternary LUT (STL) Core
- Dynamic Activation N:M Sparsity
- LUT-based 64B:80B weight decompression
- Heterogeneous accelerator design

**ASIC Implementation:**
- 28nm CMOS technology
- 500 MHz clock
- HBM2 memory (512 GB/s)

#### PD-Swap (arXiv:2512.11550)
**Dynamic Partial Reconfiguration for LLMs:**

| Feature | Benefit |
|---------|---------|
| Prefill-Decode Disaggregation | Phase-specialized architectures |
| Time-Multiplexed Attention | Reduced area duplication |
| Roofline-Inspired DSE | Optimal reconfiguration |
| Performance | 27 tok/s (1.3-2.1× vs SOTA) |

### 4.3 AMD Versal AI Engine Solutions

**Versal ACAP Architecture:**
- AI Engines (AIEs) for vectorized compute
- Programmable Logic for custom operators
- Integrated memory hierarchy

**Performance (VCK5000):**
- 2× performance vs Alveo U280 for stencil operations
- AIE limitations for HPC workloads
- Best for vector-parallel operations

### 4.4 Intel FPGA Solutions

**Intel Stratix 10 MX:**
- Used in TENET-FPGA prototype
- 400 MHz operation
- HBM2 memory support

---

## 5. FPGA vs ASIC Trade-off Analysis

### 5.1 Performance Comparison

| Metric | FPGA (Edge) | FPGA (High-End) | ASIC (28nm) |
|--------|-------------|-----------------|-------------|
| Throughput | 25 tok/s | 153 tok/s | ~400 tok/s* |
| Energy Efficiency | 5.2 TK/J | 15-20 TK/J | 100+ TK/J |
| Power | 4.8W | 50W+ | 5-10W |
| Development Cost | Low | Medium | High |
| Time-to-Market | Weeks | Months | 6-18 months |
| Flexibility | High | High | None |
| Unit Cost (volume) | $200-500 | $10,000+ | $10-50 |

*Estimated based on TENET-ASIC scaling

### 5.2 Resource Efficiency

**FPGA Advantages:**
- Reconfigurability for model updates
- Rapid prototyping
- Lower NRE cost
- Deterministic latency

**ASIC Advantages:**
- 5-10× better energy efficiency
- Higher maximum frequency
- Smaller area for same function
- Lower unit cost at volume

### 5.3 Decision Matrix

| Criteria | Choose FPGA | Choose ASIC |
|----------|-------------|-------------|
| Volume | < 10K units | > 100K units |
| Time-to-Market | Critical | Flexible |
| Model Stability | Changing frequently | Fixed model |
| Power Budget | > 5W acceptable | < 5W required |
| Performance | Moderate | Maximum needed |
| Budget | Limited NRE | Can invest $1M+ |

---

## 6. Mask-Locked Implementation Feasibility

### 6.1 Concept Overview

**Mask-Locked/Hardwired Weights:**
- Encode neural network weights in fixed metal layers
- Eliminates weight memory and loading overhead
- Ultimate compression: zero storage bits for weights

### 6.2 Implementation Approaches

#### Approach 1: Via Pattern Customization
- Use specific via patterns to encode {-1, 0, +1}
- One metal layer per bit position
- Cross-point customization

#### Approach 2: Transistor Sizing
- Strong/weaker/zero transistor paths
- Analog computation style
- Process variation sensitivity

#### Approach 3: Structured ASIC
- Pre-designed base layers
- 2-3 custom metal layers for weights
- Balance of flexibility and efficiency

### 6.3 Technical Considerations

| Factor | Impact |
|--------|--------|
| Process Node | 28nm-40nm optimal for mask cost |
| Weight Precision | Ternary ideal (3 patterns) |
| Model Size | Practical limit ~1B parameters |
| Design Flow | Custom DRC rules needed |
| Testing | BIST essential (no reconfigurability) |

### 6.4 Cost Analysis

**Mask Set Costs (approximate):**
| Node | Full Mask Set | 2-3 Layer Custom |
|------|---------------|------------------|
| 180nm | $50K | $10K |
| 40nm | $500K | $100K |
| 28nm | $1M | $200K |
| 14nm | $5M | $1M |
| 7nm | $15M+ | $3M+ |

**Structured ASIC Alternative:**
- Gate array base layer: $50K-200K
- Custom metal layers: $20K-50K each
- NRE savings: 70-80%

### 6.5 Area Estimation Methodology

**For Ternary Weight Matrix:**
```
Area_per_MAC = 
  Multiplexer Area + Accumulator Area + Control Logic

For N×M matrix with hardwired weights:
Total_Area ≈ N × M × Area_per_MAC × Routing_Factor

Routing_Factor ≈ 2-3× for structured routing
```

**Example: BitNet 0.73B**
- 730M parameters at 1.58 bits
- ~144M effective ternary values
- At 28nm: ~0.5-1 mm² compute array
- Plus: attention, normalization, control logic
- Total estimate: 2-5 mm²

---

## 7. Open-Source ASIC Design Flow

### 7.1 OpenROAD Project

**Capabilities:**
- Complete RTL-to-GDSII flow
- Synthesis, placement, routing, timing
- Support for multiple PDKs
- Active community development

**Basilisk SoC (arXiv:2405.03523):**
- RISC-V Linux-capable SoC
- IHP 130nm open PDK
- 77 MHz achieved (2.3× improvement)
- 55% core utilization
- Demonstrates production-readiness

### 7.2 Open-Source PDKs

| PDK | Node | Provider | Status |
|-----|------|----------|--------|
| SkyWater SKY130 | 130nm | SkyWater | Production-ready |
| GF180MCU | 180nm | GlobalFoundries | Production-ready |
| IHP SG13G2 | 130nm | IHP | Production-ready |
| OpenFASOC | Variable | OpenFASOC | Research |

**SkyWater SKY130 Features:**
- 130nm bulk CMOS
- Supported by OpenROAD, OpenLane
- MPW shuttle available ($15K/design)
- Digital + analog + RF support

### 7.3 MPW Shuttle Services

| Provider | PDK | Cost | Schedule |
|----------|-----|------|----------|
| Google/SkyWater | SKY130 | $15K | Quarterly |
| Efabless | Multiple | $10-50K | Varies |
| IHP | SG13G2 | ~€20K | Bi-annual |
| TinyTapeout | Various | $100-1K | Monthly |

### 7.4 EDA Tool Alternatives

| Function | Commercial | Open-Source |
|----------|------------|-------------|
| Synthesis | DC, Genus | Yosys |
| Placement | ICC, Innovus | OpenROAD |
| Routing | ICC, Innovus | OpenROAD |
| Timing | PrimeTime | OpenSTA |
| Verification | VCS, Xcelium | Verilator, Icarus |
| Physical Verification | Calibre | KLayout, Magic |

### 7.5 Design Flow for Ternary Accelerator

**Recommended Open-Source Flow:**
```
1. RTL Design (Verilog/SystemVerilog)
   └── VSCode + Verilator

2. Synthesis
   └── Yosys + ABC

3. Floorplanning
   └── OpenROAD

4. Placement
   └── OpenROAD (global + detailed)

5. Clock Tree Synthesis
   └── OpenROAD

6. Routing
   └── OpenROAD (global + detailed)

7. Physical Verification
   └── Magic + KLayout

8. Timing Signoff
   └── OpenSTA

9. GDS Generation
   └── KLayout
```

---

## 8. Cost Analysis and Recommendations

### 8.1 FPGA Development Costs

| Item | Edge FPGA | High-End FPGA |
|------|-----------|---------------|
| Development Board | $200-500 | $5,000-15,000 |
| Software License | Free-$2K/yr | $5K-20K/yr |
| Engineering Time | 3-6 months | 6-12 months |
| Total NRE | $50K-150K | $200K-500K |
| Unit Cost | $200-500 | $10,000+ |

### 8.2 ASIC Development Costs

| Item | 180nm | 40nm | 28nm |
|------|-------|------|------|
| Design | $200K | $500K | $1M |
| Mask Set | $50K | $500K | $1M |
| MPW (prototype) | $15K | $100K | $200K |
| Test/Validation | $50K | $100K | $200K |
| Total NRE | $300K | $1.2M | $2.4M |
| Unit Cost (@10K) | $5-10 | $3-5 | $2-4 |

### 8.3 ROI Analysis

**Break-Even Point (ASIC vs FPGA):**
```
Break_Even_Volume = NRE_ASIC / (Unit_FPGA - Unit_ASIC)

For 28nm ASIC vs Edge FPGA:
Break_Even = $2.4M / ($300 - $3) ≈ 8,000 units

For 180nm ASIC vs Edge FPGA:
Break_Even = $300K / ($300 - $7) ≈ 1,000 units
```

### 8.4 Recommendations by Use Case

#### Research/Prototyping Phase:
- **Platform:** Edge FPGA (AMD KV260, $248)
- **Design Flow:** Vivado MLSD (free)
- **Timeline:** 2-4 months
- **Cost:** <$50K

#### Pilot Production (100-1000 units):
- **Platform:** High-end FPGA or MPW ASIC
- **Design:** Open-source flow (OpenROAD)
- **Timeline:** 6-12 months
- **Cost:** $100K-300K

#### Volume Production (>10K units):
- **Platform:** Full-custom ASIC
- **Process:** 40nm or 28nm
- **Design:** Commercial EDA + OpenROAD hybrid
- **Timeline:** 12-18 months
- **Cost:** $1-3M NRE

---

## 9. References and URLs

### 9.1 Primary Papers

1. **TeLLMe v2** - arXiv:2510.15926
   - https://arxiv.org/abs/2510.15926
   - PDF: https://arxiv.org/pdf/2510.15926

2. **TeLLMe v1** - arXiv:2504.16266
   - https://arxiv.org/abs/2504.16266

3. **BitNet b1.58** - arXiv:2402.17764
   - https://arxiv.org/abs/2402.17764

4. **FlightLLM** - arXiv:2401.03868
   - https://arxiv.org/abs/2401.03868

5. **TENET** - arXiv:2509.13765
   - https://arxiv.org/abs/2509.13765

6. **Platinum** - arXiv:2511.21910
   - https://arxiv.org/abs/2511.21910

7. **PD-Swap** - arXiv:2512.11550
   - https://arxiv.org/abs/2512.11550

### 9.2 Architecture Papers

8. **Flex-TPU** - arXiv:2407.08700
   - https://arxiv.org/abs/2407.08700

9. **SiTe CiM** - arXiv:2408.13617
   - https://arxiv.org/abs/2408.13617

### 9.3 Open-Source ASIC Papers

10. **Basilisk** - arXiv:2405.03523
    - https://arxiv.org/abs/2405.03523

11. **Open3DBench** - arXiv:2503.12946
    - https://arxiv.org/abs/2503.12946

### 9.4 FPGA Survey Papers

12. **FPGA AI Review** - arXiv:2509.04153
    - https://arxiv.org/abs/2509.04153

13. **FPGA Strategic Role** - arXiv:2511.11614
    - https://arxiv.org/abs/2511.11614

### 9.5 Open-Source Resources

- **OpenROAD Project:** https://github.com/The-OpenROAD-Project
- **SkyWater PDK:** https://github.com/google/skywater-pdk
- **OpenLane Flow:** https://github.com/The-OpenROAD-Project/OpenLane
- **Efabless MPW:** https://efabless.com/
- **TinyTapeout:** https://tinytapeout.com/

### 9.6 Vendor Resources

- **AMD Xilinx:** https://www.xilinx.com/products/boards-and-kits.html
- **Intel FPGA:** https://www.intel.com/content/www/us/en/products/programmable.html
- **SkyWater Foundry:** https://skywatertechnologyinc.com/

---

## 10. Conclusion

The TeLLMe v2 implementation demonstrates that ternary LLM inference on edge FPGAs is now practical, achieving 25 tokens/s at 4.8W. The table-lookup matmul approach provides a 46% reduction in LUT usage compared to naive implementations, making efficient use of the limited resources on edge FPGAs.

For production deployment, the choice between FPGA and ASIC depends primarily on volume and time-to-market requirements. For research and prototyping, the AMD KV260 provides an excellent platform at $248. For volume production above 10,000 units, a custom ASIC at 28nm or 40nm becomes economically viable.

The open-source ASIC design flow has matured significantly, with OpenROAD and SkyWater PDK enabling complete RTL-to-GDSII implementation with minimal NRE investment. The Basilisk SoC demonstrates that competitive performance (77 MHz) can be achieved using open-source tools.

**Key Recommendation:** Start with FPGA prototype using TeLLMe/TLMM architecture, then evaluate ASIC migration path based on volume projections and performance requirements.

---

*Report compiled from arXiv papers, vendor documentation, and open-source project resources.*
