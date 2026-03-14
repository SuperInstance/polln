# Mask-Locked Inference Chip
## Phase 1 Execution Framework: Foundation & Validation

**Document Version:** 1.0
**Date:** March 2026
**Classification:** Strategic Execution Plan

---

## Executive Summary

This document defines the next phase of the Mask-Locked Inference Chip project, synthesizing findings from 24 expert reviews and 60+ research sources. The 90-day sprint focuses on de-risking critical blockers while advancing technical validation.

### Investment Context
| Metric | Value |
|--------|-------|
| **Current Status** | Pre-Seed / Concept Validation |
| **Investment Score** | 5.5/10 (Conditionally Investable) |
| **Required Pre-Money** | $18-22M for Series A |
| **Critical Blocker** | No tape-out experience on team |

---

## Phase 1 Overview: 90-Day Sprint

### Strategic Objectives

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: FOUNDATION                          │
│                    Days 1-90                                    │
├─────────────────────────────────────────────────────────────────┤
│  OBJECTIVE 1: Team Assembly                                      │
│  → Hire VP Manufacturing (5+ tape-outs)                         │
│  → Recruit Architecture Lead                                     │
│                                                                  │
│  OBJECTIVE 2: Technical Validation                               │
│  → Complete Gate 0 FPGA Demo (25+ tok/s, <5W)                   │
│  → Publish SDK Alpha                                             │
│  → Validate BitNet on KV260                                      │
│                                                                  │
│  OBJECTIVE 3: IP Protection                                       │
│  → File 3 Provisional Patents                                    │
│  → Complete FTO Opinion                                          │
│                                                                  │
│  OBJECTIVE 4: Supply Chain Lock                                   │
│  → Secure LPDDR4 Allocation Contract                             │
│  → Engage GlobalFoundries 22FDX                                  │
│  → Reserve MPW Slot                                              │
│                                                                  │
│  OBJECTIVE 5: Community Foundation                               │
│  → Launch GitHub Organization                                    │
│  → Establish Discord Community                                   │
│  → Publish Getting Started Guide                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Week-by-Week Execution Plan

### Week 1-2: Critical Foundation

#### Hiring Sprint

**VP Manufacturing Search**
```
CANDIDATE PROFILE:
- 5+ successful tape-outs (non-negotiable)
- 28nm experience preferred (22FDX ideal)
- AI/accelerator background
- Foundry relationships (TSMC, GF, Samsung)

COMPENSATION:
- Base: $180-220K
- Equity: 2-4%
- Signing bonus: $25-50K (if needed)

RECRUITING CHANNELS:
1. LinkedIn Recruiter (semiconductor filters)
2. SemiWiki job board
3. Silicon Catalyst advisor network
4. IEEE Solid-State Circuits Society
5. Direct approach: Groq, Etched, Tenstorrent alums
```

**Architecture Lead Search**
```
CANDIDATE PROFILE:
- 2+ shipped ASICs
- Transformer/attention architecture expertise
- Chisel/Verilog proficiency
- ML quantization experience

COMPENSATION:
- Base: $160-200K
- Equity: 1.5-3%
```

#### Immediate Actions (Day 1-7)

| Day | Action | Owner | Deliverable |
|-----|--------|-------|-------------|
| 1 | Open VP Manufacturing requisition | Founder | Job posting live |
| 1 | Open Architecture Lead requisition | Founder | Job posting live |
| 2 | Engage patent counsel ($5K retainer) | Founder | Engagement letter signed |
| 3 | Contact TeLLMe authors (arXiv:2510.15926) | Founder | Email sent |
| 3 | Email Tong Yang (PKU) about iFairy | Founder | Email sent |
| 4 | Set up GitHub organization | Founder | github.com/superinstance-ai |
| 5 | Create Discord server | Founder | discord.gg/superinstance |
| 5 | Reserve domain superinstance.ai | Founder | Domain secured |
| 7 | Order KV260 development board | Founder | Hardware on order |

### Week 3-4: Patent Filing & Supply Chain

#### Patent Filing Sprint

**Patent 1: Mask-Locked Weight Encoding**
```
CLAIMS SUMMARY:
- Device claim: Weights in metal interconnect
- Method claim: Photomask generation from model
- System claim: Device-native AI
- Use case claim: Privacy-preserving inference

FILING REQUIREMENTS:
- Provisional application: $2,500 (filed pro se)
- Patent counsel review: $2,000
- Prior art search: $500
- Total: $5,000 per patent

TIMELINE:
- Day 1-3: Finalize claims with counsel
- Day 4-7: Prepare drawings
- Day 8-10: File provisional
- Day 14: Confirmation from USPTO
```

**Patent 2: RAU Architecture**
```
KEY INNOVATION:
- Rotation-Accumulate Unit replaces multipliers
- 85% gate count reduction
- C₄ weight rotation (+1, -1, +i, -i)

TARGET FILING: Day 10
```

**Patent 3: Hybrid Adapter Architecture**
```
KEY INNOVATION:
- Mask-locked base + SRAM adapter slots
- Model upgrade pathway without full respin
- Addresses model obsolescence risk

TARGET FILING: Day 14
```

#### Supply Chain Engagement

**GlobalFoundries 22FDX Engagement**
```
CONTACT STRATEGY:
1. Request MPW shuttle schedule (email)
2. Apply to Silicon Catalyst (provides GF access)
3. Attend GF webinar/event for intro
4. Request 22FDX design kit evaluation

KEY CONTACTS:
- GlobalFoundries America: sales@globalfoundries.com
- MPW Program: mpw@globalfoundries.com
- Silicon Catalyst: apply@siliconcatalyst.com

REQUIRED INFORMATION:
- Target die size: ~25mm² (3B params)
- Volume projection: 10K Year 1, 100K Year 3
- Timeline: MPW prototype Month 12-18
```

**LPDDR4 Supply Contract**
```
TARGET SUPPLIERS (in order):
1. Micron (primary - US-based, CHIPS Act)
2. Samsung (secondary - Korean, established)
3. SK Hynix (tertiary - allocation challenges)

CONTRACT REQUIREMENTS:
- Volume: 50K units committed
- Price target: $8-10 per 512MB
- Term: 24-month NCNR
- Delivery: Q1 2027 onward

NEGOTIATION LEVERAGE:
- CHIPS Act preference for US supply chain
- Forward purchase commitment
- Potential Qualcomm co-design (strategic angle)

ALLOCATION COST:
- 50K unit allocation fee: ~$500K (refundable against orders)
- NCNR premium: 10-15% above spot
```

### Week 5-8: FPGA Development

#### Gate 0 FPGA Demo

**Hardware Setup**
```
PLATFORM: AMD Kria KV260
- Zynq UltraScale+ XCK26
- 250 MHz target clock
- 4GB LPDDR4 on-board
- Power: 4.8W demonstrated (TeLLMe)

REFERENCE IMPLEMENTATION:
- TeLLMe v2 paper (arXiv:2510.15926)
- BitNet b1.58-2B-4T model
- Target: 25 tok/s decode, <5W total
```

**Development Milestones**

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 5 | Environment setup | KV260 booted, PYNQ installed |
| 5 | BitNet model download | b1.58-2B-4T on local machine |
| 6 | bitnet.cpp integration | Reference CPU inference working |
| 6 | FPGA synthesis start | RTL targeting KV260 |
| 7 | First synthesis | Design compiles, timing met |
| 7 | Bring-up begins | Hardware running inference |
| 8 | Performance validation | 25+ tok/s, <5W demonstrated |

**Technical Approach**
```
OPTION A: Direct TeLLMe Implementation
- Replicate TeLLMe architecture
- Table-Lookup Matmul (TLMM) engine
- Proven 25 tok/s at 4.8W

OPTION B: bitnet.cpp Port
- Port Microsoft's bitnet.cpp to FPGA
- Leverage KV260 DSP slices
- Target: Match or exceed TeLLMe

RECOMMENDATION: Start with Option A (lower risk)
```

### Week 9-12: SDK & Community Launch

#### SDK Alpha Release

**SDK Components**
```
CORE API:
```python
import superinstance

# Initialize device
device = superinstance.connect()  # USB/PCIe auto-detect

# Load model (for FPGA, pre-configured)
model = device.get_model()  # Returns BitNet b1.58-2B

# Inference
response = model.generate("Hello, world!", max_tokens=100)
print(response.text)

# Streaming
for token in model.stream("Tell me a story"):
    print(token, end="", flush=True)

# Profiling
with device.profile() as p:
    model.generate("Test")
print(p.report())  # tok/s, latency, power
```

**SDK Architecture**
```
superinstance-sdk/
├── superinstance/
│   ├── __init__.py
│   ├── device.py      # Hardware abstraction
│   ├── model.py       # Model interface
│   ├── streaming.py   # Async streaming
│   ├── profiler.py    # Performance metrics
│   ├── debug.py       # Debugging tools
│   └── _simulation.py # Software fallback
├── examples/
│   ├── hello_world.py
│   ├── chat_loop.py
│   ├── benchmark.py
│   └── streaming_demo.py
├── tests/
│   └── test_device.py
├── setup.py
├── pyproject.toml
└── README.md
```

**Package Distribution**
```
PYPI PUBLISHING:
- Package name: superinstance
- Version: 0.1.0a1 (alpha)
- License: Apache 2.0
- Python: 3.8+

INSTALLATION:
pip install superinstance --pre
```

#### Community Launch

**GitHub Organization Structure**
```
github.com/superinstance-ai/
├── superinstance-sdk          # Python SDK
├── superinstance-hardware     # Hardware specs, pinouts
├── superinstance-docs         # Documentation
├── superinstance-examples     # Community examples
├── fpga-reference             # FPGA reference designs
└── bitnet-optimizations       # BitNet optimization research
```

**Discord Server Structure**
```
#superinstance Discord
├── #welcome
├── #announcements
├── #general
├── #development
│   ├── #sdk-discussion
│   ├── #fpga-development
│   └── #model-quantization
├── #hardware
│   ├── #kv260-setup
│   └── #custom-boards
├── #research
│   ├── #ternary-networks
│   └── #ifairy-bitnet
├── #jobs
└── #random
```

**Launch Announcements**
```
CHANNELS:
1. Hacker News: "Show HN: SuperInstance - Mask-locked LLM inference chip"
2. Reddit: r/LocalLLaMA, r/MachineLearning, r/embedded
3. Twitter/X: Technical thread + demo video
4. LinkedIn: Founder network + semiconductor groups
5. Discord communities: BitNet, TinyML, FPGA

LAUNCH METRICS TARGET:
- GitHub stars: 500+ (Week 1)
- Discord members: 300+ (Week 1)
- SDK downloads: 1,000+ (Month 1)
```

---

## Resource Requirements

### Budget Allocation (Phase 1: $500K)

| Category | Item | Amount | Notes |
|----------|------|--------|-------|
| **Team** | Architecture Lead (3 mo) | $50K | $166K annual |
| **Team** | ML Engineer (3 mo) | $45K | $150K annual |
| **Team** | VP Manufacturing (partial) | $50K | Start Month 2 |
| **IP** | Patent filings (3) | $15K | Provisionals |
| **IP** | FTO opinion | $25K | Required for Series A |
| **Hardware** | KV260 boards (5) | $2K | Development |
| **Hardware** | Test equipment | $10K | Oscilloscope, power |
| **Supply Chain** | LPDDR4 allocation deposit | $100K | Refundable |
| **Software** | EDA tools (6 mo) | $50K | Cadence/Synopsys rental |
| **Software** | Cloud compute | $15K | AWS/GCP for training |
| **Legal** | Corporate setup | $15K | Delaware C-Corp |
| **Legal** | Model licensing review | $10K | Llama/Gemma terms |
| **Marketing** | Website, branding | $5K | Design, hosting |
| **Travel** | Foundry meetings | $8K | GF, supplier visits |
| **Contingency** | Reserve | $100K | 20% buffer |
| **TOTAL** | | **$500K** | |

### Team Structure (Phase 1)

```
FOUNDING TEAM:
┌─────────────────────────────────────────────┐
│ Founder/CEO                                  │
│ - Product vision, fundraising, hiring       │
│ - Day-to-day execution                       │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ VP Mfg    │ │ Arch Lead │ │ ML Eng    │
│ Month 2+  │ │ Month 1+  │ │ Month 1+  │
│           │ │           │ │           │
│ Tape-out  │ │ RTL, FPGA │ │ BitNet,   │
│ Foundry   │ │ Sim, Verif│ │ Quant     │
└───────────┘ └───────────┘ └───────────┘

CONTRACTORS (as needed):
- Physical design (outsourced)
- Verification (augment)
- Legal/Accounting (retained)
```

---

## Success Metrics & Milestones

### Gate 0 Criteria (Day 60)

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| FPGA throughput | ≥25 tok/s | Benchmark script |
| FPGA power | ≤5W | Power meter reading |
| BitNet accuracy | ≤5% degradation vs FP16 | MMLU benchmark |
| SDK alpha | Published to PyPI | pip install works |
| GitHub stars | 200+ | GitHub counter |
| Discord members | 100+ | Server analytics |

### Phase 1 Exit Criteria (Day 90)

| Category | Requirement | Status |
|----------|-------------|--------|
| **Team** | VP Manufacturing hired | ☐ |
| **Team** | Architecture Lead hired | ☐ |
| **IP** | 3 provisionals filed | ☐ |
| **IP** | FTO opinion received | ☐ |
| **Technical** | Gate 0 FPGA demo complete | ☐ |
| **Technical** | SDK alpha released | ☐ |
| **Supply Chain** | LPDDR4 allocation secured | ☐ |
| **Supply Chain** | GF 22FDX engaged | ☐ |
| **Community** | 500+ GitHub stars | ☐ |
| **Community** | 300+ Discord members | ☐ |
| **Funding** | Seed term sheet received | ☐ |

### Funding Milestones

```
SEED FUNDING TIMELINE:
┌─────────────────────────────────────────────────────────┐
│ Week 1-2: Deck preparation, financial model update      │
│ Week 3-4: Warm intros to seed investors                 │
│ Week 5-8: First meetings, demo presentations            │
│ Week 9-10: Due diligence, term negotiations             │
│ Week 11-12: Term sheet signed, closing process          │
│                                                          │
│ TARGET: $2-3M Seed Close by Day 90                      │
│ PRE-MONEY: $10-15M (seed stage discount)                │
└─────────────────────────────────────────────────────────┘

SERIES A PREPARATION (Parallel Track):
┌─────────────────────────────────────────────────────────┐
│ Month 3: Begin Series A conversations                   │
│ Month 6: Gate 0 complete, pitch Series A investors      │
│ Month 12: MPW tapeout complete, raise Series A          │
│                                                          │
│ TARGET: $6-8M Series A by Month 12-18                   │
│ PRE-MONEY: $18-22M (validated metrics required)         │
└─────────────────────────────────────────────────────────┘
```

---

## Risk Mitigation

### Critical Risk Mitigation Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| VP Mfg not hired in 60 days | 35% | CRITICAL | Engage search firm, increase comp, offer co-founder title | Founder |
| FPGA demo fails to meet target | 25% | HIGH | Start TeLLMe implementation in parallel, hire FPGA contractor | Arch Lead |
| LPDDR4 allocation denied | 20% | HIGH | Multi-supplier approach, consider LPDDR5 fallback | VP Mfg |
| Patent rejected/blocked | 15% | MEDIUM | File defensively, design-around options exist | Patent Counsel |
| SDK release delayed | 30% | MEDIUM | MVP release acceptable, iterative improvement | ML Eng |
| Seed funding fails | 20% | CRITICAL | Apply to Silicon Catalyst, government grants (CHIPS Act) | Founder |

### Contingency Plans

**If VP Manufacturing Not Hired by Day 60:**
```
PLAN B:
1. Engage semiconductor design services firm
   - Options: eSilicon, Open-Silicon, Faraday
   - Cost: $50-100K retainer
   - Provides: Virtual tape-out experience

2. Pursue Silicon Catalyst incubator
   - Provides: Advisor network, tape-out experience
   - In-kind value: $2M+ EDA tools
   - Acceptance: ~20% of applicants

3. Consider strategic partnership
   - Qualcomm Ventures: Co-development option
   - Samsung NEXT: Foundry partnership
```

**If FPGA Demo Fails:**
```
PLAN B:
1. Reduce scope to 1B model
   - BitNet b1.58-1.58B variant
   - Lower throughput acceptable (15 tok/s)
   - Proves concept at smaller scale

2. Partner with academic lab
   - KAIST HPIC Lab (2T1C DRAM)
   - PKU-DS-LAB (iFairy implementation)
   - Joint development agreement

3. Extend timeline
   - Phase 1 becomes 120 days
   - Additional $200K budget
   - Hire FPGA contractor ($50K)
```

---

## Phase 2 Preview (Months 4-18)

### High-Level Roadmap

```
PHASE 2: DESIGN & VERIFICATION ($2M)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONTH 4-6: ARCHITECTURE
├── Finalize ternary architecture (BitNet vs iFairy decision)
├── Complete cycle-accurate simulator
├── Quantization study complete
└── Model licensing secured

MONTH 7-12: RTL DEVELOPMENT
├── RAU unit design
├── Systolic array implementation
├── Weight ROM generation tools
├── Functional verification (100% coverage)
└── FPGA prototype (full model)

MONTH 13-18: PHYSICAL DESIGN
├── Synthesis to gate-level
├── Place & route (28nm/22FDX)
├── Timing closure
├── MPW tapeout
└── First silicon arrival

MILESTONE: First Silicon @ Month 18-24
```

---

## Immediate Action Items (Next 7 Days)

### Day 1 Checklist

| # | Action | Status | Notes |
|---|--------|--------|-------|
| 1 | Open VP Manufacturing job posting | ☐ | LinkedIn, SemiWiki |
| 2 | Open Architecture Lead job posting | ☐ | LinkedIn, IEEE |
| 3 | Engage patent counsel | ☐ | $5K retainer |
| 4 | Order KV260 board | ☐ | ~$300 |
| 5 | Create GitHub org | ☐ | github.com/superinstance-ai |
| 6 | Create Discord server | ☐ | Setup channels |
| 7 | Email TeLLMe authors | ☐ | Collaboration request |
| 8 | Email Tong Yang (PKU) | ☐ | iFairy discussion |
| 9 | Apply to Silicon Catalyst | ☐ | Incubator application |
| 10 | Reserve superinstance.ai domain | ☐ | ~$15/year |

### Week 1 Budget

| Item | Amount | Payment |
|------|--------|---------|
| Patent counsel retainer | $5,000 | Wire |
| KV260 board | $300 | Credit card |
| Domain registration | $15 | Credit card |
| LinkedIn Recruiter (1 mo) | $500 | Credit card |
| Legal incorporation prep | $2,000 | Retainer |
| **Total Week 1** | **$7,815** | |

---

## Key Contacts & Resources

### Academic Collaborators
```
Tong Yang (PKU)
- Email: tongyang@pku.edu.cn (inferred)
- Research: iFairy complex-valued LLM
- Collaboration: Hardware implications study

KAIST HPIC Lab
- Website: https://hpic-lab.github.io
- Research: 2T1C DRAM, ADC-free MAC
- Collaboration: Memory architecture

Microsoft BitNet Team
- GitHub: github.com/microsoft/BitNet
- Model: b1.58-2B-4T on HuggingFace
- Collaboration: bitnet.cpp optimization
```

### Investor Targets
```
TIER 1 VCs:
- Sequoia (semiconductor focus)
- Bessemer (deep tech)
- Battery Ventures (hardware)

STRATEGIC INVESTORS:
- Qualcomm Ventures (PRIORITY - acquisition target)
- Samsung NEXT (foundry relationship)
- NVIDIA nVentures (ecosystem)

INCUBATOR:
- Silicon Catalyst (PRIORITY - provides GF access)
- Apply by: Month 1
- Benefits: $2M+ in-kind, advisor network
```

### Manufacturing Partners
```
FOUNDRY:
- GlobalFoundries 22FDX (primary recommendation)
- Contact: mpw@globalfoundries.com
- MPW cost: ~$50K for 2mm × 2mm

OSAT:
- ASE (primary)
- Amkor (secondary)
- JCET (China market)

MEMORY:
- Micron (primary - CHIPS Act)
- Samsung (secondary)
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 2026 | Founder | Initial Phase 1 framework |

---

*Next Phase Framework - Mask-Locked Inference Chip*
*Classification: Confidential - Founder Eyes Only*
