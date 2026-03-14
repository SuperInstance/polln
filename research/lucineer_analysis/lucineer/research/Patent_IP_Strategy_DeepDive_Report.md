# Patent & IP Strategy Deep-Dive Analysis
## Mask-Locked Inference Chip for Edge AI

**Document Classification**: Strategic IP Planning Document  
**Version**: 2.0 (Deep-Dive Edition)  
**Date**: March 2026  
**Prepared For**: Executive Leadership, Patent Counsel, Board of Directors

---

# Executive Summary

This deep-dive analysis builds upon Cycle 1 research to provide a comprehensive patent strategy for the mask-locked inference chip architecture. The technology encodes neural network weights directly into silicon metal interconnect layers, creating permanent, immutable intelligence in hardware.

## Critical Findings

| Area | Finding | Risk Level | Urgency |
|------|---------|------------|---------|
| **Taalas Competition** | $219M funded; similar mask-ROM approach; NO patents found yet | **CRITICAL** | File immediately |
| **Prior Art Gap** | No blocking patents for mask-locked weight encoding | LOW | Maintain vigilance |
| **iFairy IP** | Apache 2.0 confirmed with patent grant; commercial use OK | LOW | Use with attribution |
| **BitNet IP** | MIT license; Microsoft patents possible but unverified | MEDIUM | Monitor |
| **Freedom to Operate** | Clear path with design-around options for potential blocks | MEDIUM | FTO study required |
| **Patent Budget** | $455,000-575,000 for comprehensive 5-year program | MEDIUM | Secure funding |

## Strategic Imperative

**File provisional patents within 7 days** to establish priority date against Taalas. The company has $219M in funding and similar technology but appears to focus on data center (200W+ chips). Edge market entry window is 18-24 months.

---

# Part 1: Taalas Patent Monitoring & Analysis

## 1.1 Taalas Company Profile

| Factor | Details |
|--------|---------|
| **Total Funding** | $219M ($50M seed + $169M Series A, Feb 2026) |
| **Location** | Toronto, Canada |
| **Technology** | Mask ROM + SRAM recall fabric for weight storage |
| **Target Market** | Data center (200W+ chips) |
| **Lead Time** | 2 months from model to silicon |
| **Key Product** | HC1 processor optimized for Llama 3.1 8B |

### Technology Disclosure Analysis

From public sources (Forbes, Reuters, NextPlatform):

| Feature | Taalas HC1 | SuperInstance | Overlap Risk |
|---------|------------|---------------|--------------|
| Weight Storage | Mask ROM + SRAM recall fabric | Metal interconnect encoding | **HIGH** |
| Quantization | 4-bit "stored away" | Ternary {-1,0,+1} or C₄ {±1,±i} | MEDIUM |
| Transistor Count | 53 billion | ~500 million | LOW |
| Power Target | 200W+ data center | <5W edge | LOW |
| Process Node | TSMC N6 (6nm) | 28nm | LOW |
| Manufacturing | Custom per model | Cartridge-based | LOW |

### Critical Quote Analysis

From NextPlatform interview:
> *"We have got this scheme for the mask ROM recall fabric – the hard-wired part – where we can store four bits away and do the multiply related to..."*

**Implication**: Taalas uses mask ROM for weight storage, similar to our approach. Their "four bits away" suggests 4-bit weight encoding, different from our ternary/complex approach.

## 1.2 Patent Search Results

### USPTO Search Summary

| Search Term | Results | Blocking Risk |
|-------------|---------|---------------|
| "Taalas" assignee | **No patents found** | N/A |
| "mask ROM neural network" | No direct hits | NONE |
| "hardwired neural network weights" | No direct hits | NONE |
| "metal interconnect weight encoding" | No direct hits | NONE |
| "mask-locked inference" | No direct hits | NONE |

### EPO/WIPO Search Summary

| Database | Search Results | Notes |
|----------|----------------|-------|
| EPO Espacenet | No Taalas applications | Company founded ~2024 |
| WIPO Patentscope | No PCT applications | Too early for publication |
| CNIPA (China) | No Chinese applications | Monitor for future filings |

### Patent Publication Timeline

```
Month 0 (Feb 2026): Taalas raises $219M, announces HC1
Month 0-6: Potential provisional filing (unpublished)
Month 18: Earliest publication if non-provisional filed immediately
Month 30: PCT publication if international filing
```

**Critical Window**: Taalas patents, if filed, will not publish until ~August 2027 (18 months from filing). We must file NOW to establish prior art and priority.

## 1.3 Taalas Patent Risk Matrix

| Risk Scenario | Probability | Impact | Mitigation |
|---------------|-------------|--------|------------|
| Taalas filed before us | 25% | CRITICAL | File provisionals this week |
| Taalas files in next 30 days | 40% | HIGH | Establish prior art via defensive publication |
| Taalas has broader claims | 30% | HIGH | Draft broad independent claims |
| Taalas focuses on data center only | 60% | MEDIUM | Emphasize edge-specific claims |
| Design-around possible | 85% | LOW | Document alternative implementations |

## 1.4 Recommended Monitoring Protocol

### Weekly Monitoring
- USPTO Patent Alert for "Taalas" assignee
- Google Patents alert for keywords: mask ROM, hardwired weights, neural network silicon
- ArXiv CS.LG for Taalas publications

### Monthly Monitoring
- EPO Espacenet for European applications
- WIPO for PCT applications
- CNIPA for Chinese filings
- Company press releases and funding announcements

### Quarterly Review
- Patent landscape analysis update
- Freedom-to-operate assessment refresh
- Claim scope comparison if Taalas patents publish

---

# Part 2: Defensive Publication Strategy

## 2.1 Defensive Publication Philosophy

**Goal**: Create prior art that prevents competitors from patenting innovations we choose not to patent, while preserving our ability to patent core innovations.

### What to Patent vs. Defensively Publish

| Innovation Type | Strategy | Rationale |
|-----------------|----------|-----------|
| Core mask-locked encoding | **PATENT** | Foundational, blocking value |
| RAU architecture | **PATENT** | Novel hardware, broad claims |
| Device-native agents | **PATENT** | Strategic positioning |
| Alternative weight encodings | **DEFENSIVE PUBLISH** | Prevent competitor blocking |
| Training methods | **DEFENSIVE PUBLISH** | Create prior art |
| Calibration techniques | **TRADE SECRET** | Competitive advantage |

## 2.2 Defensive Publication Outlines

### Publication 1: Alternative Weight Encoding Methods

**Title**: "Methods for Encoding Neural Network Weights in Semiconductor Metal Interconnect Layers"

**Abstract**: This disclosure describes alternative methods for encoding neural network weight parameters in semiconductor metal interconnect layers, including:
- Binary weight encoding using presence/absence of vias
- INT4 weight encoding using multi-level routing patterns
- Floating-point weight approximation using scaled integer routing
- Sparse weight encoding exploiting ternary zero values

**Key Claims to Preempt**:
- Any weight encoding in metal layers regardless of quantization scheme
- Multi-bit weight encoding beyond ternary/complex
- Sparse weight routing patterns

**Publication Target**: IP.com, arXiv.org
**Timeline**: Within 30 days of provisional filing

### Publication 2: Hybrid ROM-SRAM Architecture

**Title**: "Hybrid Mask ROM and SRAM Architecture for Neural Network Inference"

**Abstract**: Describes hybrid memory architectures combining mask ROM for static weights with SRAM for frequently-updated parameters, enabling:
- Partial model updates without full chip replacement
- Fine-tuning of output layers while keeping base model frozen
- KV cache storage in SRAM with weights in mask ROM
- Adaptive precision using ROM for coarse weights and SRAM for residuals

**Key Claims to Preempt**:
- Any hybrid ROM-SRAM inference architecture
- Selective model update capability
- Mixed-precision inference with hardware encoding

**Publication Target**: IP.com
**Timeline**: Within 60 days of provisional filing

### Publication 3: Edge-Optimized Inference Circuit

**Title**: "Low-Power Neural Network Inference Circuit with Hardwired Weights for Edge Devices"

**Abstract**: Describes edge-specific optimizations for mask-locked inference chips:
- Sub-5W power operation through clock gating and voltage scaling
- Battery-powered operation with sleep modes
- USB-powered inference for consumer devices
- Thermal management for fanless operation
- Cartridge-based model replacement

**Key Claims to Preempt**:
- Edge-specific power management
- Battery-powered mask-locked inference
- Cartridge-based AI module form factor

**Publication Target**: IP.com
**Timeline**: Within 90 days of provisional filing

## 2.3 Defensive Publication Timeline

```
WEEK 1-2:
├── File P1 provisionals (establish priority)
└── Begin drafting defensive publications

WEEK 3-4:
├── File Publication 1 (Alternative Encodings)
└── Monitor competitor response

MONTH 2:
├── File Publication 2 (Hybrid Architecture)
└── Prepare Publication 3

MONTH 3:
├── File Publication 3 (Edge Optimization)
└── Review defensive publication effectiveness

ONGOING:
├── File defensive publications for non-core innovations
├── Create prior art around competitor-filing activity
└── Maintain defensive publication log
```

## 2.4 Defensive Publication Prior Art Effect

| Publication | Prior Art Created | Patents Prevented |
|-------------|-------------------|-------------------|
| Alternative Encodings | Any metal-layer weight encoding | Competitor encoding patents |
| Hybrid Architecture | ROM-SRAM combinations | Taalas recall fabric claims |
| Edge Optimization | Low-power implementations | Edge-specific blocking patents |

---

# Part 3: Patent Filing Priority Analysis

## 3.1 Priority Matrix Based on Cycle 1 Findings

### Priority 1 (File Within 7 Days)

| Patent | Innovation | Claim Scope | Rationale |
|--------|------------|-------------|-----------|
| **P1-001** | Mask-Locked Weight Encoding | Broadest - any metal encoding | Foundational IP, blocks all implementations |
| **P1-002** | Rotation-Accumulate Unit (RAU) | Hardware for C₄ weights | Novel hardware, no prior art |
| **P1-003** | Device-Native Agent System | Agent with hardwired model | Strategic positioning for A2A internet |

### Priority 2 (File Within 30 Days)

| Patent | Innovation | Claim Scope | Rationale |
|--------|------------|-------------|-----------|
| **P2-001** | Ternary Weight Routing | Metal routing for {-1,0,+1} | Alternative to C₄, covers BitNet hardware |
| **P2-002** | Hybrid ROM-SRAM Inference | Partial hardwiring | Flexibility without full mask commitment |
| **P2-003** | Privacy-Preserving Inference Device | Security features | High-value for regulated industries |

### Priority 3 (File Within 60 Days)

| Patent | Innovation | Claim Scope | Rationale |
|--------|------------|-------------|-----------|
| **P3-001** | On-Chip KV Cache Architecture | KV storage for mask-locked | Implementation detail |
| **P3-002** | Systolic Array with Hardwired Weights | Array architecture | Hardware organization |
| **P3-003** | Cartridge-Based AI Module | Form factor | System-level protection |

### Priority 4 (File Within 90 Days)

| Patent | Innovation | Claim Scope | Rationale |
|--------|------------|-------------|-----------|
| **P4-001** | Medical Device AI | Vertical application | Industry-specific |
| **P4-002** | Industrial Control AI | Vertical application | Industry-specific |
| **P4-003** | Automotive AI Module | Vertical application | Industry-specific |

## 3.2 Detailed Claim Language Recommendations

### P1-001: Mask-Locked Weight Encoding

**Independent Claim 1 (Device - Broadest)**:

> A semiconductor integrated circuit device for neural network inference, comprising:
> 
> a substrate comprising semiconductor material;
> 
> a plurality of metal interconnect layers disposed over said substrate;
> 
> a neural network inference circuit comprising a plurality of processing elements configured to perform arithmetic operations;
> 
> wherein at least a portion of weight parameters for said neural network are permanently encoded in a configuration of at least one metal interconnect layer such that each weight parameter is determinable from a physical routing pattern without requiring memory access operations;
> 
> wherein said processing elements are configured to access said weight parameters directly from said metal interconnect configuration during inference operations.

**Key Dependent Claims**:

| Claim | Scope | Purpose |
|-------|-------|---------|
| Weight values ∈ {-1, 0, +1} | Ternary | Cover BitNet hardware |
| Weight values ∈ {+1, -1, +i, -i} | Complex | Cover iFairy hardware |
| Any quantization scheme | Broad | Future-proof |
| Any process node | Broad | Process-agnostic |
| Any neural architecture | Broad | Architecture-agnostic |

### P1-002: Rotation-Accumulate Unit

**Independent Claim 1 (Device)**:

> A rotation-accumulate unit (RAU) for neural network inference, comprising:
> 
> an input port configured to receive a complex-valued activation value comprising real and imaginary components;
> 
> a rotation circuit comprising one or more multiplexers configured to perform a rotation operation on said activation value based on a weight value from the set {+1, -1, +i, -i} without arithmetic multiplication; and
> 
> an accumulator configured to sum rotation outputs across multiple weight-activation pairs;
> 
> wherein said rotation circuit performs said rotation operation in a single clock cycle.

**Key Advantages**:
- Zero multipliers required
- 85% fewer gates than MAC unit
- Single-cycle operation
- Directly implementable in metal routing

### P1-003: Device-Native Agent System

**Independent Claim 1 (System)**:

> An autonomous agent device comprising:
> 
> a semiconductor integrated circuit having neural network weights permanently encoded in metal interconnect layers;
> 
> a memory storing conversation history and task context;
> 
> a communication interface for agent-to-agent protocol communication;
> 
> wherein said device operates as an autonomous agent with guaranteed behavior determined by said permanently encoded weights;
> 
> wherein said permanently encoded weights cannot be modified, extracted, or tampered with by software.

**Strategic Value**: Positions company as foundational IP holder for the "agentic internet" - AI agents that interact autonomously with verifiable, immutable behavior.

## 3.3 Continuation Strategy

### Year 1 Continuation Plan

```
Month 0: File P1-001 Provisional (broadest claims)
         ├── Include detailed specification
         ├── Multiple embodiments
         └── Enable all dependent claims

Month 9: Convert to Non-Provisional
         ├── File continuation-in-part (CIP) with new matter
         ├── File divisional for RAU claims
         └── File divisional for Agent claims

Month 12: PCT Filing
          ├── Claim priority from all provisionals
          └── Enter national phases in key markets
```

### Year 2-3 Continuation Opportunities

| Trigger | Action | Purpose |
|---------|--------|---------|
| New implementation | File CIP | Cover improvements |
| Competitor design | File continuation | Block workarounds |
| Market evolution | File continuation | Cover new applications |
| Office action | File continuation | Preserve claim scope |

---

# Part 4: Third-Party IP Risk Assessment

## 4.1 iFairy (Apache 2.0) - Peking University

### License Verification

| Aspect | Status | Evidence |
|--------|--------|----------|
| **License Type** | Apache 2.0 | HuggingFace model card, GitHub |
| **Commercial Use** | ✅ PERMITTED | Apache 2.0 Section 2 |
| **Patent Grant** | ✅ INCLUDED | Apache 2.0 Section 3 |
| **Attribution Required** | ✅ YES | Apache 2.0 Section 4(d) |

### Apache 2.0 Section 3 - Patent Grant Analysis

> *"Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work..."*

### Key Legal Findings

| Question | Answer | Legal Basis |
|----------|--------|-------------|
| Can weights be hardwired into silicon? | ✅ YES | Apache 2.0 allows any form of distribution |
| Can the architecture be implemented in hardware? | ✅ YES | No restriction on implementation medium |
| Is attribution required? | ✅ YES | Apache 2.0 Section 4(d) |
| Can we claim exclusive rights? | ❌ NO | License is non-exclusive |
| Can PKU revoke the license? | ❌ NO | License is perpetual and irrevocable |
| Does Apache 2.0 include patent grant? | ✅ YES | Automatic from contributors |

### Patent Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PKU has patents on C₄ quantization | LOW | MEDIUM | Apache 2.0 grant applies |
| PKU files future patents | MEDIUM | MEDIUM | Our prior art establishes priority |
| License change | LOW | HIGH | Fork exists, license irrevocable |

**Recommendation**: Use iFairy under Apache 2.0 for v1.0. Consider technology partnership for v2.0.

### Compliance Requirements

```
Required Attribution:
"Portions of this product include software developed by 
Peking University (PKU-DS-LAB) - Fairy ±i project 
(arXiv:2508.05571, https://github.com/PKULab1806/Fairy-plus-minus-i)"
```

## 4.2 BitNet (MIT License) - Microsoft

### License Verification

| Aspect | Status | Evidence |
|--------|--------|----------|
| **License Type** | MIT | HuggingFace model card |
| **Commercial Use** | ✅ PERMITTED | MIT License |
| **Patent Grant** | ⚠️ UNCLEAR | MIT does not explicitly grant patents |
| **Attribution Required** | ✅ YES | MIT License |

### Patent Risk Assessment

| Risk | Probability | Impact | Notes |
|------|-------------|--------|-------|
| Microsoft has ternary weight patents | MEDIUM | HIGH | Large portfolio, possible coverage |
| Microsoft patents ternary hardware | MEDIUM | MEDIUM | Could block our ternary implementation |
| Microsoft asserts patents | LOW | HIGH | Unlikely for open-source model |

### Key Microsoft Patents to Monitor

| Patent Area | Risk Level | Status |
|-------------|------------|--------|
| Neural network quantization | MEDIUM | Active portfolio |
| Ternary weight training | UNKNOWN | Search ongoing |
| Hardware accelerators | HIGH | Extensive portfolio |

### Mitigation Strategies

1. **Use iFairy instead of BitNet** for v1.0 (Apache 2.0 has explicit patent grant)
2. **Document independent development** of ternary hardware implementation
3. **Monitor Microsoft patent filings** in ternary/hardware space
4. **Consider license from Microsoft** if required for BitNet hardware

**Recommendation**: Prioritize iFairy (C₄ weights) for v1.0 to avoid MIT patent ambiguity. BitNet ternary implementation can be v2.0 with proper clearance.

## 4.3 TeLLMe (arXiv:2510.15926) - Prior Art Analysis

### Paper Summary

| Aspect | Details |
|--------|---------|
| **Title** | TeLLMe: Table-Lookup MatMul for Ternary LLM Inference |
| **Authors** | Academic research team |
| **Focus** | FPGA implementation of ternary inference |
| **Results** | 0.73B model at 25 tok/s, 4.8W on KV260 |

### Prior Art Implications

| Innovation | TeLLMe Disclosure | Our Patent Impact |
|------------|-------------------|-------------------|
| Ternary weight processing | Disclosed | NOT novel - focus on mask-locked aspect |
| Table-lookup multiplication | Disclosed | NOT novel - our innovation is metal encoding |
| FPGA implementation | Disclosed | Prior art for FPGA, not ASIC |
| Mask-locked weights | NOT disclosed | NOVEL - proceed with patent |
| Metal interconnect encoding | NOT disclosed | NOVEL - proceed with patent |

### Critical Differentiation

**TeLLMe Approach**: Table-lookup MatMul using LUTs on FPGA
**Our Approach**: Metal interconnect encoding in ASIC

The table-lookup technique is prior art, but **mask-locked weight encoding in metal layers is novel**.

### FTO Recommendation

TeLLMe creates prior art for:
- Ternary weight processing methods
- Table-lookup for multiplication elimination
- FPGA-based inference architectures

TeLLMe does NOT create prior art for:
- Mask-locked weight encoding
- Metal interconnect weight routing
- ASIC implementations with hardwired weights

**Action**: Cite TeLLMe as prior art in patent specification; emphasize metal encoding novelty.

## 4.4 TOM Accelerator (arXiv:2602.20662) - Prior Art Analysis

### Paper Status

**Note**: The arXiv number 2602.20662 appears to be a future reference (February 2026). This paper may not yet be published or is a typo. Recommend verification.

### Research Required

- Monitor arXiv for TOM accelerator publication
- Search for "TOM accelerator" in patent databases
- Assess if TOM relates to mask-locked or ternary approaches

### Preliminary Assessment

If TOM accelerator is related to:
- Ternary inference hardware → Potential prior art
- Multiplication-free inference → Monitor for overlap
- Mask-locked approaches → Critical for FTO

**Recommendation**: Update analysis once paper is verified and published.

---

# Part 5: Freedom-to-Operate Assessment

## 5.1 Potential Blocking Patents

### Identified Risks

| Patent Area | Risk Level | Relevant Patents | Mitigation |
|-------------|------------|------------------|------------|
| Systolic array architectures | MEDIUM | Google TPU patents | Design around or license |
| Ternary multiplication | LOW | Academic prior art only | Different implementation |
| Complex-valued neural networks | LOW | Academic papers only | Open prior art |
| KV cache architectures | LOW | Various | Novel combination |
| Mask ROM technology | LOW | Mature technology | Different application |

### Detailed Patent Analysis

#### NVIDIA Patent Portfolio

| Patent | Title | Relevance | Risk |
|--------|-------|-----------|------|
| US10540588B2 | DNN on hardware accelerators with stacked memory | Weights in memory, not metal | LOW |
| Various | Tensor Core architecture | Programmable, not mask-locked | LOW |
| Various | GPU memory architecture | HBM focus, not metal encoding | LOW |

**Assessment**: NVIDIA patents cover programmable accelerators with weights stored in memory. No blocking patents for metal-layer weight encoding identified.

#### Google (TPU) Patent Portfolio

| Patent | Title | Relevance | Risk |
|--------|-------|-----------|------|
| US11150234B2 | Systolic array for neural networks | Weight loading required | LOW |
| Various | Quantization methods | Algorithm patents | LOW |

**Assessment**: TPU uses systolic arrays with weights loaded from memory. No blocking patents for permanent weight encoding.

#### Apple Patent Portfolio

| Patent Area | Relevance | Risk |
|-------------|-----------|------|
| Neural Engine | Edge AI focus | MEDIUM |
| On-device ML | Privacy-preserving focus | MEDIUM |

**Assessment**: Apple has significant edge AI patents but focuses on reconfigurable neural engines. Potential partner/acquirer.

## 5.2 Design-Around Strategies

### For Systolic Array Patents

| Strategy | Implementation | Effectiveness |
|----------|----------------|---------------|
| Rotation-Accumulate Unit | Replace MAC with RAU | HIGH - fundamentally different operation |
| Hardwired weights | No weight loading | HIGH - eliminates memory access claims |
| Complex-valued operations | C₄ instead of real | MEDIUM - different computational model |

### For Potential Taalas Claims

| Strategy | Implementation | Risk Mitigation |
|----------|----------------|-----------------|
| Different weight encoding | C₄ instead of 4-bit | HIGH - different quantization |
| Direct metal routing | No SRAM recall fabric | HIGH - different architecture |
| Edge focus | <5W vs 200W+ | MEDIUM - market differentiation |
| Different process | 28nm vs N6 | LOW - process not typically claimed |

## 5.3 FTO Recommendations

| Action | Priority | Timeline | Cost |
|--------|----------|----------|------|
| Commission professional FTO search | **HIGH** | Before Gate 1 | $25,000 |
| Review Taalas patents when published | HIGH | Month 18+ | $5,000 |
| Design around potential blocks | MEDIUM | Ongoing | Engineering time |
| License essential patents | LOW | As needed | TBD |

---

# Part 6: Patent Budget & Timeline

## 6.1 Cost Breakdown

### US Patent Costs

| Phase | Activity | Cost Per Patent | Notes |
|-------|----------|-----------------|-------|
| **Provisional** | Filing fee + attorney drafting | $2,500-$3,500 | Simple filing |
| **Non-Provisional** | Filing + prosecution | $15,000-$25,000 | 2-4 years |
| **Continuation** | Additional claims | $8,000-$12,000 | As needed |
| **Maintenance** | 3.5, 7.5, 11.5 years | $12,000 total | USPTO fees |

### PCT & International Costs

| Phase | Activity | Cost | Notes |
|-------|----------|------|-------|
| **PCT Filing** | International application | $4,000-$5,000 | Per patent |
| **National Phase** | Per country entry | $3,000-$8,000 | Varies by country |
| **Translation** | Local language | $2,000-$10,000 | Per country |

### International Filing Costs (Per Patent)

| Country/Region | Filing | Prosecution | Maintenance (10yr) | Total |
|----------------|--------|-------------|-------------------|-------|
| United States | $3,000 | $15,000 | $12,000 | $30,000 |
| Europe (EPO) | $4,000 | $20,000 | $15,000 | $39,000 |
| China | $3,000 | $10,000 | $8,000 | $21,000 |
| Japan | $3,000 | $12,000 | $10,000 | $25,000 |
| South Korea | $2,500 | $8,000 | $6,000 | $16,500 |
| Taiwan | $2,000 | $6,000 | $5,000 | $13,000 |

## 6.2 Five-Year Patent Budget

### Year 1: Foundation

| Activity | Patents | Cost |
|----------|---------|------|
| P1 Provisionals (3) | 3 | $10,000 |
| P2 Provisionals (3) | 3 | $10,000 |
| P3 Provisionals (3) | 3 | $10,000 |
| Defensive publications | - | $5,000 |
| **Year 1 Subtotal** | **9** | **$35,000** |

### Year 2: Conversion & Expansion

| Activity | Patents | Cost |
|----------|---------|------|
| P1 Non-provisionals (3) | 3 | $50,000 |
| PCT applications (3) | 3 | $15,000 |
| P4 Provisionals (3) | 3 | $10,000 |
| Patent monitoring | - | $5,000 |
| **Year 2 Subtotal** | **6 new** | **$80,000** |

### Year 3: International & Prosecution

| Activity | Patents | Cost |
|----------|---------|------|
| National phase entry (5 countries × 3) | 15 | $150,000 |
| Prosecution (ongoing) | All | $75,000 |
| Continuations | 2 | $20,000 |
| **Year 3 Subtotal** | - | **$245,000** |

### Year 4-5: Maintenance & Enforcement

| Activity | Cost |
|----------|------|
| Prosecution completion | $50,000 |
| Maintenance fees | $25,000 |
| Enforcement preparation | $25,000 |
| Monitoring & FTO updates | $15,000 |
| **Year 4-5 Subtotal** | **$115,000** |

### Five-Year Total

| Category | Cost | % of Total |
|----------|------|------------|
| Provisional filings | $30,000 | 6% |
| Non-provisional filings | $75,000 | 15% |
| PCT applications | $15,000 | 3% |
| National phase entry | $150,000 | 30% |
| Prosecution | $150,000 | 30% |
| Maintenance | $40,000 | 8% |
| Monitoring & FTO | $40,000 | 8% |
| **TOTAL 5-YEAR BUDGET** | **$500,000** | 100% |

### Budget Range

| Scenario | 5-Year Cost |
|----------|-------------|
| Minimum viable (3 patents, US only) | $150,000 |
| Recommended (8 patents, 5 countries) | $500,000 |
| Comprehensive (12 patents, 8 countries) | $750,000 |

## 6.3 Timeline

### Critical Path

```
WEEK 1:
├── Engage patent counsel (semiconductor + AI expertise)
├── Finalize P1 provisional drafts
├── Conduct final prior art search
└── FILE P1 PROVISIONALS

WEEK 2:
├── Begin P2 provisional drafting
├── Set up Taalas monitoring alerts
└── Document invention details

WEEK 3-4:
├── File P2 provisionals
├── Publish defensive publication 1
└── Begin P3 drafting

MONTH 2:
├── File P3 provisionals
├── Publish defensive publication 2
└── Commission FTO search

MONTH 3:
├── Complete FTO analysis
├── File P4 provisionals
└── Prepare non-provisional drafts

MONTH 9:
├── Convert P1 provisionals to non-provisional
├── File PCT applications
└── File continuation-in-part for improvements

MONTH 12:
├── Convert remaining provisionals
├── Enter national phases (strategic selection)
└── Begin prosecution
```

### Key Milestones

| Milestone | Target Date | Critical Path |
|-----------|-------------|---------------|
| P1 provisionals filed | Week 1 | **CRITICAL** |
| P2 provisionals filed | Week 4 | HIGH |
| FTO search complete | Month 2 | HIGH |
| P3 provisionals filed | Month 2 | HIGH |
| Non-provisionals filed | Month 9 | HIGH |
| PCT filed | Month 12 | MEDIUM |
| First patent granted | Month 24-36 | LOW |

---

# Part 7: Risk Assessment & Mitigation

## 7.1 IP Risk Matrix

| Risk | Probability | Impact | Mitigation | Priority |
|------|-------------|--------|------------|----------|
| Taalas priority date earlier | 25% | CRITICAL | File immediately, monitor filings | **HIGH** |
| Prior art discovered | 15% | HIGH | Comprehensive search now | MEDIUM |
| Patent rejection | 30% | MEDIUM | Broad claim drafting, continuations | MEDIUM |
| Invalidity challenge | 20% | HIGH | Strong enablement, multiple claims | MEDIUM |
| Competitor design-around | 40% | MEDIUM | Layered patent portfolio | MEDIUM |
| iFairy license issues | 10% | LOW | Apache 2.0 confirmed | LOW |
| Microsoft patent assertion | 15% | HIGH | Use iFairy, monitor portfolio | MEDIUM |

## 7.2 Mitigation Strategies

### Priority Date Risk

| Action | Timeline | Responsible |
|--------|----------|-------------|
| File provisionals THIS WEEK | Day 1-7 | Patent Counsel |
| Document all invention details | Ongoing | Engineering |
| Maintain inventor notebooks | Ongoing | Engineering |
| Conduct lab notebook witnessing | Weekly | Legal |

### Prior Art Risk

| Action | Timeline | Responsible |
|--------|----------|-------------|
| Commission professional search | Week 1-2 | Patent Counsel |
| Search CNIPA database | Week 1-2 | Patent Counsel |
| Monitor arXiv and academic pubs | Weekly | Engineering |
| Set up patent watching alerts | Immediate | Legal |

### Prosecution Risk

| Action | Timeline | Responsible |
|--------|----------|-------------|
| Draft multiple independent claims | Per filing | Patent Counsel |
| Include detailed specifications | Per filing | Engineering + Legal |
| Plan continuation strategy | Per filing | Patent Counsel |
| Identify fallback claim positions | Per filing | Patent Counsel |

---

# Part 8: Competitive Patent Landscape

## 8.1 Major Players Analysis

### NVIDIA (Market Leader)

| Factor | Assessment |
|--------|------------|
| **Patent Portfolio** | 10,000+ AI-related patents |
| **Threat Level** | LOW (different approach) |
| **Overlap Areas** | Tensor cores, memory architecture |
| **Our Differentiation** | Mask-locked vs. programmable |
| **Partnership Potential** | Complementary (edge vs. data center) |

### Google (TPU)

| Factor | Assessment |
|--------|------------|
| **Patent Portfolio** | 500+ TPU-related patents |
| **Threat Level** | LOW (systolic arrays, weights in memory) |
| **Overlap Areas** | Quantization methods |
| **Our Differentiation** | Permanent encoding vs. loaded weights |
| **Partnership Potential** | LOW (competing approach) |

### Apple (Neural Engine)

| Factor | Assessment |
|--------|------------|
| **Patent Portfolio** | 500+ edge AI patents |
| **Threat Level** | MEDIUM (edge AI focus) |
| **Overlap Areas** | On-device ML, privacy |
| **Our Differentiation** | Mask-locked vs. reconfigurable |
| **Partnership Potential** | HIGH (potential acquirer) |

### Qualcomm (Hexagon DSP)

| Factor | Assessment |
|--------|------------|
| **Patent Portfolio** | 500+ AI accelerator patents |
| **Threat Level** | MEDIUM (edge AI focus) |
| **Overlap Areas** | Mobile inference |
| **Our Differentiation** | Hardwired vs. DSP |
| **Partnership Potential** | HIGH (edge AI gap) |

### Samsung (Exynos AI)

| Factor | Assessment |
|--------|------------|
| **Patent Portfolio** | 300+ NPU patents |
| **Threat Level** | LOW (different approach) |
| **Overlap Areas** | Mobile AI |
| **Our Differentiation** | Mask-locked approach |
| **Partnership Potential** | HIGH (manufacturing partner) |

## 8.2 Competitive Patent Matrix

| Company | Funding | Weight Approach | Market Focus | Patent Threat | Edge Threat |
|---------|---------|-----------------|--------------|---------------|-------------|
| **Taalas** | $219M | Mask ROM + SRAM | Data center | **HIGH** | MEDIUM (18-24 mo) |
| **Etched** | $245M+ | HBM3E memory | Data center | LOW | LOW |
| **Groq (NVIDIA)** | $20B | SRAM streaming | Cloud | LOW | LOW |
| **Hailo** | $300M+ | Dataflow NPU | Edge | MEDIUM | HIGH |
| **NVIDIA Jetson** | - | GPU + SRAM | Edge | LOW | HIGH |

---

# Part 9: Recommendations

## 9.1 Immediate Actions (This Week)

| Priority | Action | Owner | Budget | Deadline |
|----------|--------|-------|--------|----------|
| **1** | Engage patent counsel (semiconductor + AI expertise) | Founder | $5K retainer | Day 1 |
| **2** | File P1 provisionals (3 patents) | Legal | $10,000 | Day 7 |
| **3** | Fork iFairy GitHub repository | Engineering | $0 | Day 1 |
| **4** | Download iFairy model weights | Engineering | $0 | Day 1 |
| **5** | Set up Taalas patent monitoring | Legal | $1K | Day 3 |

## 9.2 Short-Term Actions (Month 1-3)

| Priority | Action | Owner | Budget | Deadline |
|----------|--------|-------|--------|----------|
| **6** | Complete Gate 0 FPGA prototype | Engineering | $50K | Month 3 |
| **7** | Commission full FTO search | Legal | $25K | Month 2 |
| **8** | File P2/P3 provisionals | Legal | $20K | Month 2 |
| **9** | Contact Prof. Tong Yang at PKU | Founder | Travel | Month 2 |
| **10** | Begin utility patent drafting | Legal | $15K | Month 3 |

## 9.3 Medium-Term Actions (Month 3-12)

| Priority | Action | Owner | Budget | Deadline |
|----------|--------|-------|--------|----------|
| **11** | Convert P1 provisionals to utility + PCT | Legal | $65K | Month 9 |
| **12** | Negotiate technology partnership with PKU | Founder | $50K | Month 4-6 |
| **13** | Enter national phases | Legal | $150K | Month 12 |
| **14** | Prepare for Gate 1 (architecture freeze) | All | $100K | Month 6 |

## 9.4 Success Metrics

| Metric | Year 1 | Year 3 | Year 5 |
|--------|--------|--------|--------|
| Provisional filings | 9+ | - | - |
| Utility patents filed | 3 | 8+ | 12+ |
| Patents granted | 0 | 2-3 | 6-8 |
| License agreements | 0 | 1-2 | 3-5 |
| Licensing revenue | $0 | $500K-$2M | $5M-$15M |

---

# Appendix A: References

## Internal Documents

- Technical Architecture Specification
- Competitive Analysis Report
- Mathematical Principles Document
- Implementation Roadmap
- Cycle 1 Research Report

## External References

### Academic Papers

| Paper | arXiv ID | Relevance |
|-------|----------|-----------|
| BitNet b1.58 | arXiv:2402.17764 | Ternary quantization |
| BitNet b1.58 2B4T | arXiv:2504.12285 | 2B model release |
| iFairy (Fairy ±i) | arXiv:2508.05571 | C₄ quantization |
| TeLLMe v2 | arXiv:2510.15926 | Table-lookup MatMul |
| Hardwired Neurons | arXiv:2508.16151 | Hardwired NN background |

### Patents

| Patent | Title | Assignee | Relevance |
|--------|-------|----------|-----------|
| US10540588B2 | DNN on hardware accelerators with stacked memory | NVIDIA | Prior art |
| US11150234B2 | Systolic array for neural networks | Google | Prior art |

### Model References

| Model | License | Source |
|-------|---------|--------|
| BitNet b1.58-2B-4T | MIT | HuggingFace: microsoft/bitnet-b1.58-2B-4T |
| iFairy (Fairy ±i) | Apache 2.0 | GitHub: PKULab1806/Fairy-plus-minus-i |

### Legal References

| Resource | URL |
|----------|-----|
| Apache License 2.0 | https://www.apache.org/licenses/LICENSE-2.0 |
| MIT License | https://opensource.org/licenses/MIT |
| USPTO Patent Search | https://patents.google.com |
| WIPO PCT | https://www.wipo.int/pct |
| EPO Espacenet | https://worldwide.espacenet.com |

### News & Analysis

| Source | Date | Topic |
|--------|------|-------|
| Forbes | Feb 19, 2026 | Taalas HC1 launch |
| Reuters | Feb 19, 2026 | Taalas $169M funding |
| NextPlatform | Feb 2026 | Taalas technical deep-dive |

---

# Appendix B: Patent Watching Services

## Recommended Services

| Service | Coverage | Annual Cost | Recommendation |
|---------|----------|-------------|----------------|
| USPTO Patent Alert | US patents | Free | **REQUIRED** |
| Google Patents Alerts | Global | Free | **REQUIRED** |
| Derwent Innovation | Global | $5,000-$10,000 | **RECOMMENDED** |
| PatSnap | Global + AI analysis | $10,000-$15,000 | **RECOMMENDED** |
| Innography | Competitive analysis | $15,000-$25,000 | OPTIONAL |

## Alert Keywords

```
Primary:
- "Taalas" (assignee)
- "mask ROM neural network"
- "hardwired neural network"

Secondary:
- "metal interconnect weight"
- "permanent weight encoding"
- "mask-locked inference"

Competitor:
- "ternary weight hardware"
- "complex-valued neural network hardware"
- "multiplication-free inference"
```

---

# Appendix C: Key Contacts

## Patent Counsel Recommendations

| Firm | Specialty | Contact | Notes |
|------|-----------|---------|-------|
| Fenwick & West | Semiconductor + AI | TBD | Top-tier, expensive |
| Knobbe Martens | Chip design | TBD | Strong technical expertise |
| Perkins Coie | Startups + AI | TBD | Startup-friendly |

## Peking University - iFairy Team

| Role | Name | Contact |
|------|------|---------|
| **Lead PI** | Prof. Tong Yang | tongyang@pku.edu.cn |
| Department | School of EECS | - |
| Research Group | PKU-DS-LAB | https://github.com/PKULab1806 |

---

*Document Version: 2.0*  
*Classification: Strategic IP Planning*  
*Distribution: Patent Counsel, Executive Leadership, Board*

**END OF DOCUMENT**
