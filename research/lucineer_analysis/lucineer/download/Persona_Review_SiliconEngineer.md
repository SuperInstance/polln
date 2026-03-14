# SuperInstance.AI Mask-Locked Inference Chip
## Senior Silicon Engineer Technical Review

**Reviewer Profile:** 18+ years experience at Intel, NVIDIA, and Apple. Taped out 12+ chips across 28nm, 14nm, and 7nm nodes.

**Review Date:** March 2026
**Documents Reviewed:** Executive Summary, Business Model, Competitive Analysis, Technical Specification, Kimi Swarm Research Report

---

## Executive Summary: Hard Truths

I've seen promising architectures fail at tape-out. I've seen "revolutionary" chips that never left the lab. I've seen startups burn $50M on silicon that worked—but couldn't be sold. SuperInstance.AI has a compelling vision, but the technical documentation contains **critical gaps** that could kill this project in first silicon.

**Bottom Line:** The concept is sound. The execution risk is MASSIVE. The technical specification reads like a pitch deck, not a silicon design document. This review identifies 23 specific technical issues that must be addressed before committing to MPW.

---

## 1. Mask-Locking Implementation: Show Me The Physics

### 1.1 CRITICAL GAP: Physical Design Flow Missing

**What the docs say:**
> "Weights are permanently encoded into the chip's metal interconnect layers during fabrication"

**What I need to see:**
This is a hand-wavy statement that obscures the actual implementation. How exactly do you encode weights in metal?

**Questions that must be answered:**

| Issue | Concern | Risk Level |
|-------|---------|------------|
| Metal Layer Selection | Which layers? M3-M6 claimed, but weight storage density must be calculated | HIGH |
| Via Programming | How are weight values encoded? Via presence/absence? Via stack configuration? | CRITICAL |
| Weight Matrix Organization | Systolic array with fixed interconnect? Show the floorplan. | HIGH |
| Programming Mask Flow | Design → GDSII → Mask generation flow not documented | MEDIUM |
| DRC/LVS Strategy | How do you verify weight correctness at mask level? | CRITICAL |

**Technical Reality Check:**

For a 2B parameter model at 2-bit (iFairy):
- Total weight storage: 4 billion bits = 500MB
- At 28nm M3-M6 pitch (~0.1μm): Need ~50mm² just for weight routing
- Your claimed die size: 55mm² (Technical Spec mentions "120mm² for 3B model")

**WHERE IS THE AREA BUDGET BREAKDOWN?**

### 1.2 Recommended Implementation Approach

Based on Taalas public disclosures and mask ROM principles:

```
PROPOSED PHYSICAL DESIGN FLOW:

1. Weight Extraction Pipeline
   ├── Trained model (PyTorch/ONNX)
   ├── Quantize to {+1, -1, +i, -i} (iFairy encoding)
   ├── Map to via configuration matrix
   └── Generate metal programming layer GDSII

2. Metal Stack Architecture (28nm)
   ├── M1-M2: Standard cell routing (control logic)
   ├── M3-M4: Weight matrix horizontal routing
   ├── M5-M6: Weight matrix vertical routing  
   ├── M7: Power grid
   └── Via layers: Weight encoding (V3-V6)

3. Via-Encoded Weights
   ├── Via present = logic 1
   ├── Via absent = logic 0
   ├── Via stack = multi-bit encoding (potentially)
   └── Design rule: minimum via array pitch
```

**P0 Action:** Commission a physical design consultant to produce a preliminary floorplan and area budget. This should cost $30-50K and take 4-6 weeks. DO NOT proceed to MPW without this.

---

## 2. KV Cache Architecture: The Numbers Don't Add Up

### 2.1 CRITICAL GAP: SRAM Area Budget Missing

**What the docs say:**
> "Activation SRAM: 900MB on-chip"

**Reality Check:**

| Parameter | Claimed | Reality at 28nm |
|-----------|---------|-----------------|
| KV Cache Size | 900MB | Requires ~1800mm² with 6T SRAM |
| Die Size | 55mm² | Cannot fit 900MB SRAM |
| 6T Cell Size | Not specified | ~0.15μm² at 28nm (conservative) |
| Array Efficiency | Not specified | ~70% typical |

**Let me do the math:**
```
900MB = 900 × 8 = 7,200 Mbits
6T SRAM cell at 28nm: 0.12-0.18 μm²
Array efficiency: 70%
Peripheral overhead: 30%

Total SRAM Area = 7,200 × 10^6 × 0.15μm² × (1/0.7) × 1.3
                = 2,000 mm²

This is 36x larger than the claimed die size.
```

**This is a FATAL ERROR in the specification.**

### 2.2 Realistic KV Cache Sizing

For Llama-2-7B inference at reasonable context lengths:

```
KV Cache Calculation:
- Hidden dim: 4096
- Num layers: 32
- Num heads: 32
- Context length: 2048 (realistic for edge)
- KV precision: INT8

KV Cache = 2 × L × H × D × C × precision
         = 2 × 32 × 32 × 4096 × 2048 × 1 byte
         = 16 GB (FP16) → 4 GB (INT4 quantized)

This STILL doesn't fit on 55mm².
```

### 2.3 Proposed Solutions (Pick One)

**Option A: Streaming KV Cache (Recommended)**
- Store only current token's KV vectors on-chip
- Stream previous KV from external LPDDR4
- Requires 4-8GB external memory (kills zero-DRAM claim)
- Area: ~10MB on-chip buffer

**Option B: Sliding Window Attention**
- Limit context to 512 tokens
- Degrades model quality for long-context tasks
- KV Cache: ~256MB → 64MB at INT4
- Area: ~15-20mm² (achievable)

**Option C: Multi-Query Attention / Grouped Query Attention**
- Reduce KV heads by 4-8x
- Supported by Llama-3 architecture
- KV Cache reduced proportionally
- Requires model architecture change

**P0 Action:** Immediately revise technical specification with realistic KV cache sizing. The 900MB claim destroys credibility with any silicon reviewer.

---

## 3. iFairy Complex Arithmetic: Novel but Unproven

### 3.1 Technical Validation

**What the docs say:**
> "C4 Group Weights: Four discrete weight values {+1, -1, +i, -i} eliminate the need for floating-point multiplication"

**Good News:** The iFairy paper (arXiv:2508.05571) is legitimate. Peking University research is credible.

**Critical Concerns:**

| Issue | Risk | Mitigation |
|-------|------|------------|
| Has ANYONE synthesized this to RTL? | CRITICAL | Contact PKU team directly |
| Complex arithmetic → 2x real operations? | HIGH | Verify "addition-only" claim |
| Phase rotation circuits | MEDIUM | May need specialized hardware |
| Training pipeline compatibility | MEDIUM | Custom PyTorch backend needed |

### 3.2 iFairy Implementation Challenges

The C4 group {+1, -1, +i, -i} means:

```
Complex Multiplication Simplification:
(±1 ± i) × (±1 ± i) = Real multiplication only?

Actually:
(a + bi) × (c + di) = (ac - bd) + (ad + bc)i

For C4 weights where values are in {1, -1, i, -i}:
- Multiplication by +1: No change
- Multiplication by -1: Negation (adder with invert)
- Multiplication by +i: Swap real/imaginary, negate imaginary
- Multiplication by -i: Swap real/imaginary, negate real

HARDWARE IMPLEMENTATION:
- No multipliers needed (CORRECT)
- Need: adders, subtractors, 2:1 muxes for swap
- Per-MAC overhead: ~4 adders + control logic
```

**This IS achievable.** But the documentation lacks any RTL architecture description.

### 3.3 Required Verification

**P0 Actions:**
1. Contact Prof. Tong Yang at PKU (tongyang@pku.edu.cn) for collaboration
2. Build a reference iFairy inference engine in Verilog
3. Synthesize to 28nm standard cells, get area/power estimates
4. Verify the "addition-only" claim holds for full transformer architecture

**Estimated effort:** 2-3 months, 1 senior RTL engineer
**Estimated cost:** $150-200K (including consultant time)

---

## 4. Power Analysis: Where's The Data?

### 4.1 CRITICAL GAP: No Post-Layout Power Simulation

**What the docs say:**
> "Power: 3W target" (various mentions throughout)

**What's missing:**
- No RTL power estimation
- No gate-level power simulation
- No post-layout parasitic extraction
- No PVT corner analysis
- No switching activity factor assumptions

**This is unacceptable for a chip targeting production.**

### 4.2 Power Breakdown Requirements

At minimum, provide:

| Component | Target Power | Estimation Method |
|-----------|--------------|-------------------|
| Weight Matrix (hardwired) | ? W | Wire capacitance only |
| Activation SRAM | ? W | C × V² × f × activity |
| MAC Units (iFairy) | ? W | Standard cell library data |
| Control FSM | ? W | Low, but quantify |
| I/O (USB 3.0) | ? W | Spec compliance |
| Clock Distribution | ? W | ~10-15% of total |
| Leakage (28nm) | ? W | Temperature dependent |

### 4.3 Power Reality Check for USB Form Factor

USB 3.0 specification:
- Maximum power: 4.5W (900mA at 5V)
- Thermal limit in USB stick: ~2-3W continuous (no heatsink)

**3W in USB form factor is at the thermal limit.**

Required analysis:
```
THERMAL ANALYSIS NEEDED:

1. Package thermal resistance (θJA)
   - Typical USB stick: 40-60°C/W
   - Ambient: 25°C
   - Target junction: 85°C max

   Tj = Ta + P × θJA
   85 = 25 + 3 × θJA
   θJA_max = 20°C/W

   This requires ACTIVE COOLING or very careful package design.
```

### 4.4 P0 Actions

1. **Immediate:** Build RTL and run gate-level simulation with switching activity
2. **Pre-tapeout:** Post-layout power analysis with extracted parasitics
3. **Thermal simulation:** FloTHERM or similar, full USB assembly

---

## 5. Verification Strategy: What's The Plan?

### 5.1 CRITICAL GAP: No Verification Methodology Documented

**What the docs say:**
> "Gate 0 Prototype: FPGA demo" → "Gate 1: First silicon"

**What's missing:**
- UVM testbench architecture
- Coverage model definition
- Formal verification strategy
- Post-silicon validation plan
- Model accuracy verification methodology

**Industry standard practice:**
- 60-70% of silicon development effort is verification
- Without proper verification, first silicon success rate <20%

### 5.2 Recommended Verification Architecture

```
VERIFICATION HIERARCHY:

Level 1: Unit-Level Verification
├── iFairy MAC unit
│   ├── Directed tests (all C4 combinations)
│   ├── Formal property checking
│   └── Code coverage >95%
├── SRAM controller
├── USB interface
└── Control FSM

Level 2: Subsystem Verification
├── Weight matrix subsystem
├── KV cache subsystem
├── Inference pipeline
└── UVM agent for each interface

Level 3: Chip-Level Verification
├── Full inference test cases
├── Regression suite (1000+ tests)
├── Functional coverage model
└── Power-aware simulation

Level 4: Emulation
├── FPGA prototyping (Gate 0)
├── Traffic generators
├── Real model inference tests
└── Performance validation

Level 5: Post-Silicon
├── ATE test program
├── BIST for SRAM
├── Functional validation board
└── Model accuracy validation
```

### 5.3 Model Accuracy Verification

**Critical Question:** How do you verify that mask-locked weights produce correct inference results?

**Required methodology:**
1. Golden model in PyTorch/ONNX
2. Bit-accurate C++ reference model
3. RTL simulation against reference
4. Coverage of weight value combinations
5. End-to-end test vectors (input → output tokens)

**P0 Action:** Hire or contract a verification lead with UVM experience. Budget: $200-300K for verification infrastructure.

---

## 6. Process Corner Analysis: PVT Sensitivity

### 6.1 CRITICAL GAP: No PVT Analysis

Mask-locked weights have unique PVT challenges:

| Factor | Impact on Mask-Locked Weights |
|--------|-------------------------------|
| Process (SS/TT/FF) | Wire resistance variation affects delay |
| Voltage (±10%) | Timing margin, power variation |
| Temperature (-40°C to 85°C) | Wire delay, leakage power |

**Specific concerns for mask-locked inference:**

```
PVT ANALYSIS NEEDED:

1. Weight Matrix Timing
   - Hardwired connections have fixed delay
   - Process variation affects wire RC
   - Temperature affects resistance
   - Must meet timing at SS, 0.9V, 85°C

2. Clock Skew Analysis
   - Large weight matrix = long distances
   - Clock tree synthesis critical
   - Useful skew may be needed

3. Signal Integrity
   - Long wires in weight matrix
   - Crosstalk analysis needed
   - Shielding requirements?

4. Variation Analysis
   - Monte Carlo simulation
   - Corner extraction
   - Guard-banding methodology
```

### 6.2 Recommended PVT Strategy

1. **Timing closure at worst corner:** SS, 0.9V, 85°C
2. **Power analysis at fast corner:** FF, 1.1V, -40°C
3. **Monte Carlo timing:** 1000+ runs, determine yield impact
4. **Guard-band methodology:** Document in design spec

**P1 Action:** Include PVT analysis in gate-level signoff criteria.

---

## 7. Thermal Management: USB Form Factor Reality

### 7.1 CRITICAL ISSUE: Thermal Limits Ignored

**USB stick thermal characteristics:**
- No active cooling
- Plastic enclosure (poor thermal conductor)
- Small surface area for convection
- Adjacent USB devices may block airflow

**3W continuous in this form factor is THERMALLY CHALLENGING.**

### 7.2 Thermal Analysis Required

```
THERMAL SIMULATION CHECKLIST:

1. Package Selection
   ├── QFN package: θJA ~30-40°C/W
   ├── BGA package: θJA ~20-30°C/W
   └── Custom thermal-enhanced: θJA ~15-20°C/W

2. Enclosure Effects
   ├── Plastic enclosure adds 5-10°C/W
   ├── Ventilation holes (if allowed)
   └── Metal insert for heat spreading

3. Operating Scenarios
   ├── Continuous inference (worst case)
   ├── Burst inference (duty cycle analysis)
   ├── Idle power (leakage at temperature)
   └── USB bus-powered only constraint

4. Thermal Throttling
   ├── Temperature sensor required
   ├── Clock scaling strategy
   ├── Graceful degradation
   └── User notification mechanism
```

### 7.3 Mitigation Strategies

**Strategy A: Reduced Power Target**
- Target 1.5-2W instead of 3W
- May require lower clock frequency
- Reduces inference speed proportionally

**Strategy B: Burst Operation**
- Allow 3W for 10-30 seconds
- Thermal throttle to 1W for cooling
- Suitable for interactive use cases
- Requires thermal model in firmware

**Strategy C: Metal Enclosure**
- Aluminum housing acts as heatsink
- Adds cost ($1-2 per unit)
- Professional appearance
- θJA improvement: 10-15°C/W

**P0 Action:** Commission thermal simulation. Budget: $20-30K. Timeline: 4 weeks.

---

## 8. Development Roadmap: Aggressive But Achievable?

### 8.1 Timeline Analysis

| Milestone | Claimed | Realistic | Risk |
|-----------|---------|-----------|------|
| Gate 0 (FPGA) | Month 6 | Month 6-8 | MEDIUM |
| Gate 1 (MPW) | Month 12 | Month 14-18 | HIGH |
| Gate 2 (Volume) | Month 18 | Month 24-30 | CRITICAL |
| Gate 3 (100K units) | Month 24 | Month 36+ | HIGH |

**Concerns:**

1. **MPW to Volume in 6 months:** Unrealistic. First silicon typically requires 3-6 months for debug and characterization before volume commitment.

2. **No silicon debug time allocated:** First silicon ALWAYS has bugs. Where's the respin budget?

3. **Volume ramp assumes perfect yield:** 28nm yield is good, but not guaranteed on first run.

### 8.2 Recommended Revised Timeline

```
REVISED ROADMAP:

Month 6: Gate 0 Complete
├── FPGA prototype at 25+ tok/s
├── RTL frozen
├── Testbench complete
└── Preliminary timing/power analysis

Month 10: Gate 0.5 (Pre-MPW)
├── Gate-level simulation complete
├── Post-synthesis timing clean
├── Power analysis complete
├── DRC/LVS clean on synthesized netlist
└── MPW commitment

Month 14: MPW Silicon Return
├── Package assembly
├── ATE test program execution
├── Bring-up lab ready
└── Debug engineers allocated

Month 16: First Silicon Validation
├── Functional validation
├── Performance measurement
├── Bug list prioritization
└── Go/No-Go for volume mask

Month 18: Volume Mask Commitment (if Go)
├── Design fixes incorporated
├── Mask set ordered ($2-3M)
├── Production test program
└── Assembly partner locked

Month 24: Volume Production
├── First production wafers
├── Yield ramp
├── Customer shipments
└── Revenue recognition
```

### 8.3 Respin Budget

**Industry standard:** Allocate 30-40% probability of respin.

**Budget requirement:**
- Second mask set: $2-3M
- Additional engineering: $500K-1M
- Schedule delay: 3-4 months

**P0 Action:** Include respin budget in financial model. Add $3-4M contingency.

---

## 9. Manufacturing Strategy: Foundry Reality

### 9.1 TSMC 28nm Capacity

**Current situation (2026):**
- TSMC 28nm capacity is constrained
- Lead times: 16-24 weeks for MPW, 20-30 weeks for volume
- Allocation required for volume commitment

**Mitigation:**
- Establish relationship with TSMC NOW
- Consider Samsung Foundry 28nm as backup
- SkyWater 130nm is NOT suitable for this design (too slow)

### 9.2 Assembly and Test

**OSAT Selection:**
- ASE, SPIL, Amkor are primary options
- USB form factor requires custom packaging
- Test development: 3-4 months lead time

**BIST Strategy:**
```
BUILT-IN SELF-TEST REQUIREMENTS:

1. SRAM BIST
   ├── March algorithm
   ├── At-speed testing
   └── Repair logic (redundant rows/columns?)

2. Logic BIST
   ├── Weight matrix connectivity test
   ├── MAC unit logic test
   └── Control FSM state coverage

3. I/O BIST
   ├── USB PHY loopback
   ├── Speed negotiation test
   └── Power management test
```

### 9.3 Yield Strategy

**28nm yield expectations:**
- Mature process: 80-85% achievable
- Defect density: ~0.5 defects/cm²
- Die size impact: Larger die = lower yield

**Yield model for 55mm² die:**
```
Y = e^(-D × A)
D = 0.5 defects/cm²
A = 0.55 cm²
Y = e^(-0.5 × 0.55) = 76%

At 120mm² (3B model):
Y = e^(-0.5 × 1.2) = 55%

This is MARGINAL for profitability.
```

**P1 Action:** Add 15% SRAM redundancy for repair. Target yield: 80%+.

---

## 10. Risk Register: What Can Kill This Project

### 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| KV cache doesn't fit | 90% | CRITICAL | External DRAM or model redesign | NOT ADDRESSED |
| Power exceeds 3W | 40% | HIGH | Conservative design, throttling | PARTIALLY ADDRESSED |
| Thermal throttling required | 70% | MEDIUM | Metal enclosure, burst mode | NOT ADDRESSED |
| iFairy RTL issues | 30% | HIGH | PKU collaboration, reference design | PARTIALLY ADDRESSED |
| First silicon bugs | 80% | HIGH | Verification investment, respin budget | NOT ADDRESSED |
| Yield below target | 30% | MEDIUM | Design for yield, redundancy | NOT ADDRESSED |

### 10.2 Schedule Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| TSMC allocation delay | 40% | HIGH | Early commitment, backup foundry | NOT ADDRESSED |
| MPW return delayed | 30% | MEDIUM | Schedule buffer | NOT ADDRESSED |
| Verification incomplete | 50% | CRITICAL | Hire verification lead NOW | NOT ADDRESSED |
| Assembly qualification delay | 25% | MEDIUM | Early OSAT engagement | NOT ADDRESSED |

### 10.3 Business Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| Memory price spike | 40% | MEDIUM | Mask-locked advantage | MITIGATED |
| Competitor launches first | 30% | HIGH | Speed to market | BEING ADDRESSED |
| Model accuracy issues | 25% | HIGH | Extensive QAT pipeline | PARTIALLY ADDRESSED |
| Customer adoption slow | 30% | MEDIUM | Developer community investment | BEING ADDRESSED |

---

## 11. Novel Solutions to Technical Challenges

### 11.1 KV Cache Compression

**Proposed innovation:**

Instead of storing full KV cache, implement **Streaming KV with Token Pruning**:

```
STREAMING KV ARCHITECTURE:

1. On-Chip Buffer (Realistic Size)
   ├── Current token KV: 2 × L × H × D = 256KB
   ├── Recent token cache: 512 tokens × 256KB = 128MB
   └── Total: ~130MB (fits on 55mm² with INT4)

2. Streaming from External Flash
   ├── Offload older KV to external SPI flash
   ├── Flash bandwidth: 100MB/s (adequate)
   ├── Latency: acceptable for batch decode
   └── Cost: $1-2 for 256MB flash

3. Token Importance Pruning
   ├── Prune low-attention tokens
   ├── Keep recent tokens + high-importance tokens
   ├── Reduces KV cache by 50-70%
   └── Paper: "H2O: Heavy-Hitter Oracle" (arXiv:2306.14048)
```

**Benefits:**
- Fits in realistic die area
- Enables long context (2048+ tokens)
- Low cost external memory

### 11.2 Adaptive Power Management

**Proposed innovation:**

```
ADAPTIVE POWER SYSTEM:

1. Thermal Monitor
   ├── On-die temperature sensor
   ├── Real-time power estimation
   └── Predictive thermal model

2. Operating Modes
   ├── Burst Mode: 3W, 100 tok/s, 30 second limit
   ├── Sustained Mode: 1.5W, 50 tok/s, unlimited
   └── Idle Mode: 0.1W, USB keepalive only

3. User API
   ├── Application hints for mode selection
   ├── Power budget reporting
   └── Thermal status notification

4. Hardware Implementation
   ├── Clock frequency scaling (500MHz → 250MHz)
   ├── Voltage scaling if supported (optional)
   └── Power gating for unused blocks
```

### 11.3 Weight Matrix Verification by Design

**Proposed innovation:**

Use **Formal Equivalence Checking** between trained model and mask-programmed weights:

```
FORMAL VERIFICATION FLOW:

1. Extract weights from trained model
2. Generate expected via configuration
3. Formal proof: via configuration ↔ weight values
4. Automated DRC check on weight regions
5. Post-mask verification: test pattern matching

Tools:
├── Synopsys Formality
├── Cadence Conformal
└── Custom scripts for weight extraction
```

This eliminates an entire class of bugs: incorrect weight encoding.

---

## 12. Priority-Ranked Action Items

### P0: CRITICAL (Must complete before MPW commitment)

| # | Action | Owner | Budget | Timeline |
|---|--------|-------|--------|----------|
| 1 | Produce detailed area budget showing weight matrix + KV cache fit | Design Lead | $50K | 4 weeks |
| 2 | Build iFairy MAC unit RTL and synthesize to 28nm | RTL Lead | $100K | 6 weeks |
| 3 | Revise KV cache strategy with realistic sizing | Arch Lead | $25K | 2 weeks |
| 4 | Commission thermal simulation for USB form factor | Mechanical | $30K | 4 weeks |
| 5 | Hire verification lead and define UVM testbench | Verification | $200K | 8 weeks |
| 6 | Engage PKU iFairy team for technical collaboration | CEO | Travel | 2 weeks |
| 7 | Run gate-level power estimation on critical paths | Design Lead | $25K | 2 weeks |

**Total P0 Budget:** $430K
**Total P0 Timeline:** 8 weeks

### P1: HIGH (Must complete before tape-out)

| # | Action | Owner | Budget | Timeline |
|---|--------|-------|--------|----------|
| 8 | Full PVT corner analysis | Design Lead | $30K | 4 weeks |
| 9 | Clock tree synthesis strategy | Design Lead | $20K | 2 weeks |
| 10 | BIST architecture design | Test Lead | $50K | 4 weeks |
| 11 | Post-silicon validation plan | Validation Lead | $25K | 2 weeks |
| 12 | OSAT engagement and package design | Operations | $75K | 8 weeks |
| 13 | Model accuracy test suite | ML Lead | $40K | 4 weeks |
| 14 | Design-for-yield analysis (redundancy) | Design Lead | $25K | 2 weeks |

**Total P1 Budget:** $265K
**Total P1 Timeline:** 8 weeks

### P2: MEDIUM (Should complete for production)

| # | Action | Owner | Budget | Timeline |
|---|--------|-------|--------|----------|
| 15 | Streaming KV cache implementation | Arch Lead | $100K | 8 weeks |
| 16 | Adaptive power management RTL | RTL Lead | $50K | 4 weeks |
| 17 | Formal equivalence checking flow | Verification | $30K | 4 weeks |
| 18 | Yield enhancement (redundancy insertion) | Design Lead | $40K | 4 weeks |
| 19 | Production test program development | Test Lead | $100K | 12 weeks |
| 20 | Reliability qualification plan | Quality | $25K | 2 weeks |

**Total P2 Budget:** $345K
**Total P2 Timeline:** 12 weeks

---

## 13. Investment Recommendation

### 13.1 Technical Due Diligence Scorecard

| Category | Score | Comments |
|----------|-------|----------|
| Architecture Concept | 8/10 | Novel, mathematically sound |
| Implementation Detail | 3/10 | CRITICAL GAPS - area, power unproven |
| Verification Strategy | 2/10 | NOT ADDRESSED |
| Manufacturing Plan | 5/10 | Foundry relationships unclear |
| Risk Management | 4/10 | Major risks not acknowledged |
| Team Capability | 6/10 | Good on paper, execution unknown |
| **OVERALL** | **4.7/10** | **NOT READY FOR MPW** |

### 13.2 Go/No-Go Criteria for Series A

**NO-GO until:**
1. ✗ Area budget demonstrates weight matrix + KV cache fit
2. ✗ Power analysis shows <3W with margin
3. ✗ Thermal simulation validates USB form factor feasibility
4. ✗ Verification lead hired with UVM experience
5. ✗ PKU collaboration established for iFairy implementation
6. ✗ Respin budget ($3-4M) included in financial model

**GO criteria:**
1. ✓ All P0 items complete
2. ✓ FPGA prototype demonstrates 25+ tok/s
3. ✓ Gate-level timing clean at worst PVT corner
4. ✓ Customer LOIs converted to paid pilots

### 13.3 Recommended Investment Structure

**Stage 1 ($500K):** Complete P0 items, FPGA prototype
- Milestone: Working FPGA demo with realistic architecture
- Timeline: 3 months

**Stage 2 ($1.5M):** Complete P1 items, RTL freeze, verification
- Milestone: Tape-out ready design with testbench
- Timeline: 4 months after Stage 1

**Stage 3 ($3M):** MPW commitment and silicon return
- Milestone: First silicon functional
- Timeline: 6 months after Stage 2

**Stage 4 ($3M):** Volume mask and production
- Milestone: Production units shipping
- Timeline: 6 months after Stage 3

**Total:** $8M staged, with go/no-go at each stage

---

## 14. Conclusion: Tough Love

I've reviewed hundreds of chip proposals. SuperInstance.AI has a genuinely innovative concept—the mask-locked approach for edge LLM inference is compelling and addresses a real market need.

**But the technical documentation is not investment-ready.**

The 900MB SRAM claim on a 55mm² die is physically impossible. The 3W power target lacks any supporting analysis. The verification strategy is undefined. These are not minor gaps—they are fundamental architectural issues that could result in non-functional first silicon.

**The good news:** These problems are solvable with proper engineering investment. The concept is sound. The market is real. The team appears capable.

**The bad news:** Solving these problems will take time and money. The current timeline is optimistic by 6-12 months. The current budget is insufficient by $2-4M.

**My recommendation:**
1. Do not commit to MPW based on current documentation
2. Fund the P0 work ($430K over 8 weeks)
3. Re-evaluate based on revised technical specification
4. Stage subsequent investment based on technical milestones

This is a project worth pursuing—but not in its current state. Fix the fundamentals, then tape out.

---

**Reviewer:** Senior Silicon Engineer
**Date:** March 2026
**Classification:** Technical Due Diligence - Confidential

---

## Appendix A: Key Equations and Calculations

### A.1 SRAM Area Calculation

```
Area = (Capacity × Cell_Size) / Array_Efficiency × Peripheral_Factor

Where:
- Capacity = 900MB = 7,200 Mbits
- Cell_Size = 0.15 μm² (6T SRAM at 28nm)
- Array_Efficiency = 0.70 (typical)
- Peripheral_Factor = 1.3 (decoders, sense amps, etc.)

Result:
Area = (7,200 × 10^6 × 0.15 μm²) / 0.70 × 1.3
     = 1,543,000,000 μm² / 0.70 × 1.3
     = 2,865,000,000 μm²
     = 2,865 mm²
```

### A.2 Power Calculation

```
Dynamic Power = α × C × V² × f

Where:
- α = Activity factor (0.1-0.3 typical)
- C = Capacitance (from extraction)
- V = Voltage (1.0V at 28nm)
- f = Frequency (500 MHz target)

Leakage Power = I_leak × V × Area

At 28nm:
- I_leak ≈ 10-50 pA/μm (temperature dependent)
- Temperature coefficient: 2x per 10°C

Thermal Calculation:
Tj = Ta + P × θJA
   = 25°C + 3W × 50°C/W
   = 175°C (EXCEEDS LIMIT)

For Tj < 85°C:
θJA_max = (85 - 25) / 3 = 20°C/W
```

### A.3 Yield Model

```
Poisson Yield Model:
Y = e^(-D × A)

Where:
- D = Defect density (defects/cm²)
- A = Die area (cm²)

For 28nm mature process:
D ≈ 0.3-0.7 defects/cm²

For 55mm² die (0.55 cm²):
Y = e^(-0.5 × 0.55) = 0.76 (76%)

For 120mm² die (1.2 cm²):
Y = e^(-0.5 × 1.2) = 0.55 (55%)

Die Per Wafer (300mm):
N = π × (R² / A) - (π × D / √(2 × A))

Where:
- R = 150mm (wafer radius)
- A = die area in mm²
- D = edge exclusion (3mm)

For 55mm² die:
N ≈ 300mm² × π / 55mm² ≈ 17,000 dies/wafer
Good dies = 17,000 × 0.76 = 12,920 per wafer
```

---

## Appendix B: Reference Implementation Notes

### B.1 TeLLMe FPGA Reference

The TeLLMe paper (arXiv:2510.15926) provides a critical reference:

| Metric | TeLLMe (KV260) | SuperInstance Target |
|--------|----------------|---------------------|
| Platform | Xilinx ZU7EV | Custom ASIC |
| Model | BitNet 0.73B | iFairy 2B |
| Throughput | 25 tok/s | 80-150 tok/s |
| Power | 4.8W | <3W |
| Implementation | Table-Lookup Matmul | Hardwired weights |

**Key learning:** TeLLMe achieves 25 tok/s on FPGA. Your target of 80-150 tok/s on ASIC is aggressive but potentially achievable with hardwired weights.

**Recommended action:** Study TeLLMe Table-Lookup Matmul architecture as reference for weight encoding strategy.

### B.2 Taalas Architecture Reference

Taalas HC1 specifications (public):

| Parameter | Taalas HC1 | SuperInstance |
|-----------|------------|---------------|
| Process | TSMC N6 | TSMC 28nm |
| Transistors | 53 billion | 5-10 billion |
| Weight Storage | Mask ROM + SRAM | Metal layers |
| Performance | 17,000 tok/s | 80-150 tok/s |
| Power | >100W | <3W |

**Key learning:** Taalas uses Mask ROM for weights, not metal layer encoding. This is a proven approach for weight storage. Consider if metal-layer encoding is necessary or if Mask ROM provides sufficient benefits.

---

*End of Technical Review*
