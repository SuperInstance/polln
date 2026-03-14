# SuperInstance.AI Due Diligence Checklist
## Comprehensive Investor Due Diligence Framework

**Document Version:** 1.0  
**Prepared For:** Prospective Investors  
**Classification:** Confidential  
**Last Updated:** March 2026

---

# Executive Summary

This due diligence checklist addresses all investor concerns identified through multi-persona reviews by VC Partners, Hardware CEOs, and industry experts. The checklist is organized into six major categories with specific deliverables, responsible parties, timelines, success criteria, and red flags to monitor.

**Key Risk Categories Requiring Immediate Attention:**
| Category | Risk Level | Primary Concern |
|----------|------------|-----------------|
| Technical | CRITICAL | Pre-silicon status, yield assumptions |
| Commercial | HIGH | Competitive response, channel validation |
| Financial | HIGH | Unrealistic projections, capital requirements |
| Team | MEDIUM-HIGH | Key role vacancies (VP Sales, VP Manufacturing) |
| Legal | HIGH | Patent position weak, prior art concerns |
| Market | MEDIUM | TAM/SAM validation needed |

---

# 1. Technical Due Diligence

## 1.1 FPGA Demo Validation Requirements

### Purpose
Validate that FPGA prototype performance (94 tok/s on 0.73B model) translates to production ASIC targets (25-35 tok/s on 2B model).

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.1.1** FPGA Demo Replication | Independent 3rd party benchmark report | External Lab | Week 1-2 | ≥90 tok/s on 0.73B model replicated | Inability to replicate claimed performance |
| **T1.1.2** Model Scaling Analysis | PPA (Power-Performance-Area) scaling report from 0.73B to 2B model | CTO | Week 2-4 | Linear or better scaling demonstrated | Non-linear degradation in scaling |
| **T1.1.3** Power Measurement Protocol | Detailed power measurement methodology document | VP Engineering | Week 2 | Industry-standard methodology (JEDEC) | Power measured under unrealistic conditions |
| **T1.1.4** Benchmark Conditions Disclosure | Full disclosure of benchmark conditions (temperature, voltage, clock) | CTO | Week 1 | All conditions documented | Conditions not disclosed or unrealistic |
| **T1.1.5** Source Code/RTL Access | Access to FPGA demo RTL for technical review | CTO | Week 1 | Full RTL provided under NDA | Reluctance to provide source access |

### Additional Verification Steps
- [ ] Request oscilloscope traces of power consumption during inference
- [ ] Verify model weights are truly frozen in mask-locked approach
- [ ] Confirm FPGA platform used (Xilinx KV260 or equivalent)
- [ ] Validate token counting methodology matches industry standard

---

## 1.2 Power Measurement Requirements

### Purpose
Validate claimed 3-5W total power consumption for inference operations.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.2.1** Power Budget Breakdown | Component-level power analysis (compute, memory, I/O, idle) | VP Engineering | Week 2-4 | Detailed breakdown totaling ≤5W | Power budget exceeds claims |
| **T1.2.2** Dynamic Power Profiling | Power waveform during inference operation | Hardware Lead | Week 3-4 | Peak power ≤6W, average ≤4W | Spikes exceeding thermal limits |
| **T1.2.3** Thermal Design Power (TDP) | TDP specification for each product tier | VP Engineering | Week 4 | TDP matches marketing claims | TDP significantly higher than stated |
| **T1.2.4** Memory Power Budget | LPDDR4 power consumption analysis | Hardware Lead | Week 3 | Memory power within budget | Memory consumes >50% of power budget |
| **T1.2.5** Idle Power Measurement | Standby power consumption measurement | Hardware Lead | Week 3 | Idle power <0.5W | High idle power drains battery |

### Power Validation Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    Power Validation Hierarchy               │
├─────────────────────────────────────────────────────────────┤
│  Level 1: Simulation Estimates (Current Status)             │
│  Level 2: FPGA Proxy Measurements (In Progress)             │
│  Level 3: Silicon Validation (Required for Series A)        │
│  Level 4: Production Validation (Required for Scale)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 1.3 RTL Review Checklist

### Purpose
Verify that RTL design is production-ready and meets performance targets.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.3.1** Code Coverage Report | 100% code coverage achieved | Verification Lead | Week 4 | 100% toggle, line, branch coverage | Coverage gaps in critical paths |
| **T1.3.2** Functional Coverage Report | 100% functional coverage | Verification Lead | Week 4 | All features exercised | Untested corner cases |
| **T1.3.3** Assertion Coverage | ≥95% assertion coverage | Verification Lead | Week 4 | Assertions cover all critical paths | Missing assertions on interfaces |
| **T1.3.4** Lint Report | Clean lint report with waiver documentation | Design Lead | Week 3 | Zero critical warnings, documented waivers | Undocumented waivers |
| **T1.3.5** CDC (Clock Domain Crossing) Report | Clean CDC analysis | Design Lead | Week 3 | All CDC paths properly constrained | Unconstrained CDC paths |
| **T1.3.6** Synthesis Constraints | Validated timing constraints | Physical Design Lead | Week 4 | All constraints documented and validated | Missing or invalid constraints |
| **T1.3.7** Gate-Level Simulation | GLS passing at target frequency | Verification Lead | Week 6 | All tests pass at 1.1x margin | Timing violations at margin |
| **T1.3.8** Formal Verification | Formal equivalence checking complete | Design Lead | Week 5 | RTL matches gate-level | Equivalence failures |

---

## 1.4 Thermal Simulation Requirements

### Purpose
Validate thermal performance in target form factors (USB dongle, PCIe card, embedded module).

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.4.1** Thermal Model | CFD (Computational Fluid Dynamics) thermal model | Mechanical Engineer | Week 4-6 | Model validated against measurements | Model doesn't match measurements |
| **T1.4.2** Junction Temperature Analysis | Max junction temp under all operating conditions | Hardware Lead | Week 4 | Tj < 100°C at 45°C ambient | Thermal throttling required |
| **T1.4.3** Thermal Solution Design | Heatsink/thermal pad specification | Mechanical Engineer | Week 6 | Passive cooling sufficient | Active cooling required |
| **T1.4.4** Form Factor Thermal Validation | Thermal analysis for each product form factor | Hardware Lead | Week 6 | All form factors meet spec | USB form factor thermally limited |
| **T1.4.5** Thermal Throttling Behavior | Throttling curve documentation | Hardware Lead | Week 5 | Throttling behavior documented | Unexpected throttling behavior |

---

## 1.5 Memory Architecture Validation

### Purpose
Validate mask-locked memory approach and compatibility with LPDDR4 external memory.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.5.1** Mask-Locked Storage Architecture | Detailed architecture document showing weight storage in metal layers | CTO | Week 2 | Architecture clearly documented | Architecture unclear or inconsistent |
| **T1.5.2** Memory Bandwidth Analysis | Bandwidth requirements vs. available bandwidth | Hardware Lead | Week 3 | Requirements ≤80% of available | Bandwidth bottleneck identified |
| **T1.5.3** Weight Mapping Verification | How model weights are mapped to physical silicon | CTO | Week 3 | Clear mapping methodology | Mapping methodology unclear |
| **T1.5.4** LPDDR4 Interface Validation | Memory controller simulation results | Hardware Lead | Week 4 | Controller validated at target frequency | Interface timing issues |
| **T1.5.5** Model Cartridge Explanation | Technical explanation of how "model cartridges" work with mask-locked silicon | CTO | Week 2 | Clear technical explanation | Contradiction with mask-locked approach |

### Critical Question to Resolve
> **Question:** How do "model cartridges" work when weights are mask-locked into silicon metal layers? This appears to be a fundamental contradiction that requires clear technical explanation.

---

## 1.6 Patent/IP Review

### Purpose
Validate strength and defensibility of patent position.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.6.1** Patent Portfolio Summary | List of all filed patents with status | Legal Counsel | Week 1 | Complete inventory provided | Incomplete patent inventory |
| **T1.6.2** Patent Prosecution Timeline | Timeline from provisional to utility to grant | Patent Attorney | Week 2 | Realistic timeline (2-3 years) | Unrealistic timeline claims |
| **T1.6.3** Patent Claims Review | Independent review of patent claims by IP counsel | External IP Counsel | Week 3 | Claims appear novel and non-obvious | Claims appear weak or obvious |
| **T1.6.4** IP Assignment Verification | All IP assigned to company | Legal Counsel | Week 1 | All assignments recorded | Unassigned IP from founders/advisors |
| **T1.6.5** Trade Secret Inventory | List of trade secrets and protection measures | Legal Counsel | Week 2 | Trade secrets documented | Trade secrets not protected |

---

## 1.7 Prior Art Search

### Purpose
Identify potential prior art that could invalidate patent claims.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T1.7.1** Comprehensive Prior Art Search | Professional prior art search report | Patent Attorney | Week 2-4 | No blocking prior art identified | Blocking prior art found |
| **T1.7.2** Taalas Patent Analysis | Analysis of Taalas patents and applications | IP Counsel | Week 2-3 | Clear differentiation from Taalas IP | Overlap with Taalas patents |
| **T1.7.3** Academic Literature Review | Search of academic papers on mask-locked inference | Technical Advisor | Week 2-3 | No prior academic work blocking | Prior academic publication |
| **T1.7.4** Freedom to Operate Opinion | FTO opinion from IP counsel | External IP Counsel | Week 4-6 | Positive FTO opinion | FTO concerns identified |
| **T1.7.5** iFairy IP Review | Review of iFairy (Peking University) IP status | Legal Counsel | Week 2 | Clear license or ownership | IP ownership unclear |

### Key Prior Art Concerns

| Source | Risk Level | Action Required |
|--------|------------|-----------------|
| Taalas (Feb 2026, $169M raised) | HIGH | Detailed patent comparison |
| Microsoft BitNet | MEDIUM | Ensure no blocking claims |
| Peking University iFairy | MEDIUM | Verify licensing rights |
| Academic papers (arXiv) | MEDIUM | Check publication dates vs. filing dates |

---

# 2. Commercial Due Diligence

## 2.1 Customer Discovery Interview Plan

### Purpose
Validate market demand through structured customer interviews.

### Interview Targets

| Segment | Target Interviews | Contact Method | Timeline | Key Questions |
|---------|-------------------|----------------|----------|---------------|
| Maker/Hobbyist | 20 interviews | Online survey + calls | Week 1-3 | Price sensitivity, model preferences |
| Professional Developer | 15 interviews | Direct outreach | Week 2-4 | Integration complexity, performance needs |
| Enterprise Buyer | 10 interviews | LinkedIn outreach | Week 3-5 | Compliance requirements, volume needs |
| Embedded Engineer | 15 interviews | Technical forums | Week 2-4 | Power constraints, form factor needs |

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **C2.1.1** Interview Script | Standardized interview questionnaire | Product Marketing | Week 1 | Script validated by sales | Leading questions only |
| **C2.1.2** Interview Recordings | Recorded interviews (with consent) | Sales Team | Week 1-5 | 50+ interviews completed | Low response rate |
| **C2.1.3** Interview Analysis | Thematic analysis of responses | Product Marketing | Week 4-6 | Key insights documented | Contradictory feedback |
| **C2.1.4** Willingness-to-Pay Study | WTP analysis by segment | Product Marketing | Week 4-6 | Price points validated | WTP below target price |
| **C2.1.5** Feature Prioritization | Kano model analysis of features | Product Manager | Week 4-6 | Must-have features identified | Missing critical features |

### Key Questions to Ask
1. "What would you pay for a $35 LLM inference chip running Llama-2-7B at 20 tok/s?"
2. "How important is model flexibility vs. performance?"
3. "What is your current solution for edge LLM inference?"
4. "What would make you switch from Hailo/Jetson?"
5. "How do you handle model updates currently?"

---

## 2.2 Competitive Benchmarking Requirements

### Purpose
Validate competitive positioning and differentiation claims.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **C2.2.1** Hailo Competitive Analysis | Detailed Hailo-10H benchmark comparison | Hardware Lead | Week 2-4 | Performance comparison documented | Performance claims not validated |
| **C2.2.2** Jetson Competitive Analysis | NVIDIA Jetson Orin Nano benchmark comparison | Hardware Lead | Week 3-5 | Performance/watt comparison | Inferior to Jetson on key metrics |
| **C2.2.3** Google Coral Analysis | Analysis of Coral EOL installed base | Market Research | Week 2 | Replacement opportunity quantified | Coral users not interested |
| **C2.2.4** Taalas Threat Assessment | Analysis of Taalas technology and market positioning | Technical Advisor | Week 3-5 | Differentiation clear | Taalas has superior technology |
| **C2.2.5** Price/Performance Matrix | Competitive price/performance matrix | Product Marketing | Week 4 | Superior positioning documented | Positioning unclear |

### Competitive Benchmark Requirements

| Competitor | Metrics to Benchmark | Data Source |
|------------|---------------------|-------------|
| Hailo-10H | tok/s, power, setup time, price | Independent lab |
| Jetson Orin Nano | tok/s, power, SDK complexity, price | Published specs + independent test |
| Coral Edge TPU | EOL impact, migration path | Customer interviews |
| RK3588 (Rockchip) | Performance, price, Chinese market | Technical specs |
| Taalas HC1 | Architecture comparison, timeline | Public information |

---

## 2.3 Channel Validation Checklist

### Purpose
Validate distributor and reseller channel assumptions.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **C2.3.1** Digi-Key Interest | LOI or term sheet from Digi-Key | VP Sales | Week 4-8 | Distribution agreement in principle | Distributor not interested |
| **C2.3.2** Mouser Interest | LOI or term sheet from Mouser | VP Sales | Week 4-8 | Distribution agreement in principle | Distributor not interested |
| **C2.3.3** SparkFun Partnership | Partnership terms with SparkFun | VP Sales | Week 3-6 | Co-marketing agreement signed | SparkFun prefers competitors |
| **C2.3.4** Seeed Studio Partnership | White-label or distribution agreement | VP Sales | Week 4-8 | Agreement signed | Seeed not interested |
| **C2.3.5** Amazon Marketplace | Amazon seller account setup plan | E-commerce Lead | Week 4 | Plan documented | Amazon selling not planned |

### Channel Timeline Verification

```
STATED TIMELINE:
- Month 15: SparkFun partnership
- Month 18: Digi-Key distribution
- Month 20: Mouser distribution

INDUSTRY REALITY:
- Distributor onboarding: 6-12 months
- First PO to revenue: 3-6 months
- Volume scaling: 12-18 months

GAP: Channel development timeline may be underestimated by 6-12 months
```

---

## 2.4 Supply Chain Verification

### Purpose
Validate supply chain assumptions and identify risks.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **C2.4.1** TSMC Allocation Status | Current allocation status and forecast | VP Manufacturing | Week 2 | Allocation confirmed | Allocation at risk |
| **C2.4.2** TSMC Backup Plan | Samsung foundry qualification timeline | VP Manufacturing | Week 4 | Backup plan documented | No backup plan |
| **C2.4.3** Memory Supply Agreement | LPDDR4 supply contract terms | Supply Chain Manager | Week 4 | Contract signed or LOI | No supply agreement |
| **C2.4.4** OSAT Partner Verification | Assembly/test partner capability confirmation | VP Manufacturing | Week 3 | Multiple OSAT partners confirmed | Single OSAT dependency |
| **C2.4.5** Memory Price Hedging | Memory price hedging strategy | CFO | Week 4 | Strategy documented | No hedging strategy |
| **C2.4.6** Dual-Source Strategy | Component dual-source qualification plan | Supply Chain Manager | Week 6 | Plan for critical components | Single-source dependencies |

### Supply Chain Risk Assessment

| Component | Risk Level | Primary Supplier | Backup | Lead Time | Action Required |
|-----------|------------|------------------|--------|-----------|-----------------|
| Wafers (28nm) | CRITICAL | TSMC | Samsung (unqualified) | 12-16 weeks | Qualify Samsung |
| LPDDR4 Memory | HIGH | Samsung/SK Hynix | Micron | 8-12 weeks | Lock pricing |
| Package Substrate | HIGH | ASE/Amkor | SPIL | 6-8 weeks | Dual-source |
| PCB Assembly | MEDIUM | Multiple | Multiple | 2-4 weeks | Standard lead time |
| Passive Components | LOW | Multiple | Multiple | 1-2 weeks | Standard lead time |

### Memory Price Sensitivity Analysis

| LPDDR4 Price ($/512MB) | Memory COGS Impact | Total COGS (Standard) | Gross Margin | Risk Level |
|-----------------------|--------------------|----------------------|--------------|------------|
| $5.00 (baseline) | $3.00 | $21.30 | 73% | LOW |
| $10.00 (current spot) | $6.00 | $24.30 | 69% | MEDIUM |
| $15.00 (shortage) | $9.00 | $27.30 | 65% | HIGH |
| $18.00 (extreme) | $10.80 | $29.10 | 63% | CRITICAL |

---

# 3. Financial Due Diligence

## 3.1 Cap Table Verification

### Purpose
Verify capitalization structure and ownership percentages.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **F3.1.1** Current Cap Table | Fully diluted cap table | CFO/Legal | Week 1 | Complete cap table provided | Cap table not provided |
| **F3.1.2** Option Pool | Option pool size and allocation | CFO | Week 1 | Option pool documented | Unusually small/large option pool |
| **F3.1.3** SAFEs/Convertibles | Outstanding SAFEs and conversion terms | Legal Counsel | Week 1 | All instruments documented | Undisclosed SAFEs |
| **F3.1.4** Preferred Stock Terms | Terms of any preferred stock | Legal Counsel | Week 1 | Terms documented | Unusual terms |
| **F3.1.5** Founder Vesting | Founder vesting schedules | Legal Counsel | Week 1 | 4-year vesting, 1-year cliff | Founders fully vested |

### Cap Table Verification Points
- [ ] Total shares authorized vs. issued
- [ ] Treasury shares held
- [ ] Warrants outstanding
- [ ] Convertible notes with maturity dates
- [ ] Pro forma cap table post-funding

---

## 3.2 Revenue Model Stress Tests

### Purpose
Validate revenue projections under various scenarios.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **F3.2.1** Revenue Model Documentation | Detailed revenue model with assumptions | CFO | Week 2 | Model provided with all assumptions | Model not shared |
| **F3.2.2** Conservative Scenario | Revenue projection with pessimistic assumptions | CFO | Week 3 | Conservative scenario documented | Only optimistic scenario |
| **F3.2.3** Base Scenario | Revenue projection with realistic assumptions | CFO | Week 3 | Base scenario documented | Unrealistic assumptions |
| **F3.2.4** Aggressive Scenario | Revenue projection with optimistic assumptions | CFO | Week 3 | Aggressive scenario documented | Aggressive scenario treated as base |
| **F3.2.5** Sensitivity Analysis | Revenue sensitivity to key variables | CFO | Week 4 | Sensitivity matrix provided | No sensitivity analysis |

### Revenue Model Reality Check

| Metric | Company Projection | Industry Benchmark | Assessment |
|--------|-------------------|-------------------|------------|
| Y1 Revenue | $240K | N/A (first year variable) | Reasonable |
| Y1→Y2 Growth | 12x (1,200%) | 2-3x typical for hardware | AGGRESSIVE |
| Y2→Y3 Growth | 3.9x (290%) | 2-3x typical | AGGRESSIVE |
| Y5 Revenue | $70M | Varies widely | AGGRESSIVE |

### Recommended Financial Planning Approach
```
Plan for CONSERVATIVE scenario
Budget for BASE scenario
Hope for AGGRESSIVE scenario

Conservative Y5 Target: $15-20M
Base Y5 Target: $28-35M
Aggressive Y5 Target: $45-60M

Note: Original $70M projection is 2x aggressive scenario
```

---

## 3.3 Burn Rate Analysis

### Purpose
Validate operating expense assumptions and runway calculations.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **F3.3.1** Monthly Burn Rate | Detailed monthly burn rate breakdown | CFO | Week 1 | Burn rate ≤$50K/month initially | Burn rate >$100K/month pre-revenue |
| **F3.3.2** 18-Month Budget | Detailed 18-month operating budget | CFO | Week 2 | Budget provided with justification | Budget not provided |
| **F3.3.3** Hiring Plan Costs | Cost of planned hires | CFO | Week 2 | Hiring costs included in budget | Hiring costs excluded |
| **F3.3.4** R&D Budget | R&D spending plan | VP Engineering | Week 2 | R&D budget realistic for semiconductor | R&D budget too low |
| **F3.3.5** Runway Calculation | Runway calculation under various scenarios | CFO | Week 2 | 18+ months runway | <12 months runway |

### Burn Rate Reality Check

| Category | Company Statement | Industry Benchmark | Recommended |
|----------|------------------|-------------------|-------------|
| Monthly Burn | $28K/month | $200-500K/month for semiconductor startup | $100-200K/month |
| Team Size | Small | 10-20 employees for semiconductor startup | Plan for growth |
| R&D Spending | Unclear | 50-70% of expenses for hardware startup | Must be detailed |

### Critical Burn Rate Questions
1. "Your burn rate of $28K/month seems unrealistically low. Can you provide a detailed breakdown?"
2. "What is your burn rate after hiring VP Manufacturing and VP Sales?"
3. "What is your burn rate during MPW tape-out phase?"
4. "How much working capital do you need for inventory?"

---

## 3.4 Manufacturing Cost Validation

### Purpose
Validate COGS assumptions and margin calculations.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **F3.4.1** COGS Breakdown | Detailed COGS breakdown by component | VP Manufacturing | Week 2 | Complete breakdown provided | COGS breakdown not provided |
| **F3.4.2** Yield Assumptions | Yield assumptions with justification | VP Manufacturing | Week 2 | Yield >80% with justification | Yield assumptions unclear |
| **F3.4.3** Yield Sensitivity | COGS sensitivity to yield variations | VP Manufacturing | Week 3 | Sensitivity analysis provided | No sensitivity analysis |
| **F3.4.4** Volume Pricing | Volume pricing from suppliers | Supply Chain Manager | Week 3 | Quotes from suppliers | Pricing estimated only |
| **F3.4.5** NRE Costs | Non-recurring engineering costs | VP Engineering | Week 2 | NRE costs documented | NRE costs not included |

### Yield Sensitivity Analysis

| Yield Rate | COGS Impact (Standard) | Gross Margin | Viability |
|------------|----------------------|--------------|-----------|
| 82% (assumed) | $21.30 | 73% | VIABLE |
| 70% | $24.90 | 68% | VIABLE |
| 60% | $29.05 | 63% | MARGINAL |
| 50% | $34.86 | 56% | AT RISK |
| 40% | $43.58 | 45% | NOT VIABLE |

### Critical Manufacturing Questions
1. "What is your break-even yield rate?"
2. "What happens to margins if yield is 50%?"
3. "Have you received quotes from TSMC for 28nm MPW?"
4. "What is your mask cost estimate for production masks?"

---

## 3.5 Sensitivity Analysis Requirements

### Purpose
Understand impact of key variables on financial performance.

### Required Sensitivity Analyses

| Variable | Range to Test | Impact Metric | Timeline |
|----------|---------------|---------------|----------|
| Yield Rate | 40% - 90% | Gross Margin | Week 3 |
| Memory Price | $5 - $18/512MB | COGS, Margin | Week 3 |
| Volume | 10K - 500K units | Revenue, Margin | Week 3 |
| ASP | $30 - $100 | Revenue, Market Share | Week 3 |
| Competition Entry | Month 6 - 24 | Revenue, Margin | Week 4 |
| Time to Market | Month 12 - 24 | Revenue, Runway | Week 4 |

### Deliverable
- [ ] Sensitivity matrix showing impact of each variable
- [ ] Break-even analysis for each key variable
- [ ] Scenario planning document

---

# 4. Team Due Diligence

## 4.1 Reference Check Requirements

### Purpose
Validate team capabilities through reference checks.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T4.1.1** Founder References | 5+ reference checks on founders | HR/Investor | Week 1-2 | Positive references | Negative references |
| **T4.1.2** Technical Advisor References | Reference checks on technical advisors | HR/Investor | Week 2 | Advisors actively engaged | Advisors not engaged |
| **T4.1.3** Prior Employer References | References from prior employers | HR/Investor | Week 2 | Positive feedback | Performance issues |
| **T4.1.4** Co-worker References | References from former co-workers | HR/Investor | Week 2 | Positive collaboration history | Collaboration issues |
| **T4.1.5** Customer References | References from any prior customers | Sales | Week 3 | Positive customer feedback | Customer complaints |

### Reference Check Questions
1. "How would you describe [founder]'s technical capabilities?"
2. "Have you worked with them on a tape-out before? What was the outcome?"
3. "How do they handle pressure and setbacks?"
4. "Would you invest in a company led by them?"
5. "What are their weaknesses?"

---

## 4.2 Technical Interview Plan

### Purpose
Validate technical depth through structured interviews.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T4.2.1** CTO Technical Interview | Technical deep-dive with CTO | Technical Advisor | Week 1-2 | Demonstrates deep expertise | Knowledge gaps |
| **T4.2.2** VP Engineering Interview | Technical interview with VP Engineering | Technical Advisor | Week 1-2 | Strong manufacturing experience | Limited manufacturing experience |
| **T4.2.3** Architecture Review | Technical review of chip architecture | External Expert | Week 2-3 | Architecture sound | Architecture concerns |
| **T4.2.4** Tape-Out Experience | Verification of claimed tape-out experience | HR/Technical Advisor | Week 2 | Experience verified | Experience overstated |
| **T4.2.5** Technical Team Assessment | Assessment of technical team depth | Technical Advisor | Week 2-3 | Team has necessary skills | Skill gaps identified |

### Technical Interview Topics

| Role | Topics to Cover |
|------|-----------------|
| CTO | Mask-locked architecture, ternary weights, iFairy complex arithmetic |
| VP Engineering | TSMC process, yield optimization, DFM, packaging |
| Hardware Lead | RTL design, verification methodology, timing closure |
| Software Lead | Compiler optimization, SDK design, model quantization |

---

## 4.3 Background Check Requirements

### Purpose
Verify background information and identify any concerns.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T4.3.1** Criminal Background Check | Clean criminal record | Background Check Firm | Week 1-2 | No criminal history | Criminal history found |
| **T4.3.2** Education Verification | Verify claimed degrees | Background Check Firm | Week 1 | Degrees verified | Education misstated |
| **T4.3.3** Employment Verification | Verify prior employment | Background Check Firm | Week 1-2 | Employment verified | Employment misstated |
| **T4.3.4** Credit Check | Credit history review (executives) | Background Check Firm | Week 1-2 | Acceptable credit | Significant credit issues |
| **T4.3.5** Litigation Search | Search for litigation history | Legal Counsel | Week 1-2 | No significant litigation | Litigation history found |

---

## 4.4 Employment Verification

### Purpose
Verify that all team members are properly employed and committed.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **T4.4.1** Employment Agreements | All employees have signed agreements | Legal Counsel | Week 1 | All agreements on file | Missing employment agreements |
| **T4.4.2** IP Assignment Clauses | All employees have assigned IP to company | Legal Counsel | Week 1 | All IP assigned | IP not assigned |
| **T4.4.3** Non-Compete Agreements | Founders/key employees have non-competes | Legal Counsel | Week 1 | Non-competes signed | No non-competes |
| **T4.4.4** Vesting Schedules | Founder vesting schedules documented | Legal Counsel | Week 1 | 4-year vesting, 1-year cliff | Unusual vesting terms |
| **T4.4.5** Key Person Insurance | Key person insurance on founders | CFO | Week 4 | Insurance in place | No key person insurance |

---

# 5. Legal Due Diligence

## 5.1 IP Assignment Verification

### Purpose
Verify all IP is properly assigned to the company.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **L5.1.1** Founder IP Assignment | All founder IP assigned to company | Legal Counsel | Week 1 | Assignment documents signed | IP not assigned |
| **L5.1.2** Advisor IP Assignment | All advisor IP assigned to company | Legal Counsel | Week 1 | Assignment documents signed | IP not assigned |
| **L5.1.3** University IP | Any university IP properly licensed | Legal Counsel | Week 2 | License agreements in place | University IP not licensed |
| **L5.1.4** Third-Party IP | All third-party IP licensed | Legal Counsel | Week 2 | License agreements documented | Unlicensed IP used |
| **L5.1.5** Open Source Compliance | Open source license compliance documented | Legal Counsel | Week 3 | All licenses compliant | License violations |

---

## 5.2 Contract Review Checklist

### Purpose
Review all material contracts and agreements.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **L5.2.1** Customer Contracts | All customer contracts reviewed | Legal Counsel | Week 2-4 | No unusual terms | Unusual terms found |
| **L5.2.2** Supplier Contracts | All supplier contracts reviewed | Legal Counsel | Week 2-4 | Reasonable terms | Unfavorable terms |
| **L5.2.3** Partnership Agreements | All partnership agreements reviewed | Legal Counsel | Week 2-4 | Agreements documented | Undocumented partnerships |
| **L5.2.4** Employment Contracts | All employment contracts reviewed | Legal Counsel | Week 2 | Standard terms | Unusual terms |
| **L5.2.5** Lease Agreements | All lease agreements reviewed | Legal Counsel | Week 2 | Reasonable terms | Unfavorable lease terms |

---

## 5.3 Regulatory Compliance

### Purpose
Verify compliance with relevant regulations.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **L5.3.1** FCC Certification | FCC certification plan for wireless products | Compliance Officer | Week 4 | Plan documented | No certification plan |
| **L5.3.2** CE Marking | CE marking plan for EU market | Compliance Officer | Week 4 | Plan documented | No EU compliance plan |
| **L5.3.3** RoHS Compliance | RoHS compliance verification | Compliance Officer | Week 3 | Compliance verified | Non-compliant components |
| **L5.3.4** REACH Compliance | REACH compliance verification | Compliance Officer | Week 3 | Compliance verified | Non-compliant substances |
| **L5.3.5** Industry-Specific Regulations | Compliance with target industry regulations | Legal Counsel | Week 4 | Compliance verified | Regulatory gaps |

---

## 5.4 Export Control Considerations

### Purpose
Identify and address export control requirements.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **L5.4.1** ECCN Classification | Export Control Classification Number for product | Legal Counsel | Week 3-4 | Classification determined | Classification unclear |
| **L5.4.2** De Minimis Analysis | Analysis of foreign content for re-export | Legal Counsel | Week 4 | Analysis complete | De minimis issues |
| **L5.4.3** License Requirements | Export license requirements identified | Legal Counsel | Week 4 | Requirements documented | Unknown requirements |
| **L5.4.4** China Market Strategy | Strategy for China market (35-40% of edge AI) | Legal Counsel | Week 4 | Strategy documented | No China strategy |
| **L5.4.5** Entity List Check | Check against US entity list | Legal Counsel | Week 2 | No entity list issues | Entity list concerns |

### Semiconductor Export Control Note
> **Note:** Semiconductor products and technology are subject to significant export controls. 28nm technology is currently below the most restrictive thresholds, but regulations are evolving rapidly. Any advanced packaging or AI-specific features may trigger additional controls.

---

# 6. Market Due Diligence

## 6.1 Market Sizing Methodology Verification

### Purpose
Validate TAM/SAM/SOM calculations.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **M6.1.1** TAM Definition | Clear definition and calculation of TAM | Market Research | Week 2 | TAM justified | TAM inflated |
| **M6.1.2** SAM Definition | Clear definition and calculation of SAM | Market Research | Week 2 | SAM realistic | SAM includes unreachable markets |
| **M6.1.3** SOM Definition | Clear definition and calculation of SOM | Market Research | Week 2 | SOM achievable | SOM aggressive |
| **M6.1.4** Bottom-Up Calculation | Bottom-up market sizing from customer counts | Market Research | Week 3 | Bottom-up matches top-down | Significant gap between methods |
| **M6.1.5** Growth Rate Justification | Justification for assumed growth rates | Market Research | Week 2 | Growth rates documented | Growth rates unsubstantiated |

### Market Sizing Reality Check

| Metric | Company Claim | Investor Assessment | Gap |
|--------|---------------|---------------------|-----|
| TAM (2029) | $76.8B | Industry-wide figure | TAM includes all AI inference |
| SAM (2029) | $18.5B | $800M - $1.2B for sub-$100 edge | ~10-20x difference |
| SOM (2029) | $1.85B (1.3% market share) | Realistic if execution perfect | Market share aggressive |

### Bottom-Up Market Sizing Framework
```
Addressable Developer Base:
- Global edge AI developers: ~1.2M
- Target segment (sub-$100 LLM inference): ~200K
- Penetration rate (Y5): 3-5%
- Target customers: 6,000-10,000

Revenue Calculation:
- Average selling price: $52
- Repeat purchase rate: 40%
- Y5 revenue: $8-15M (conservative)
- Y5 revenue: $20-30M (optimistic)
```

---

## 6.2 Competitor Research Requirements

### Purpose
Comprehensive competitor analysis and monitoring.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **M6.2.1** Competitor Profiles | Detailed profiles of top 10 competitors | Market Research | Week 2-4 | Profiles complete | Incomplete profiles |
| **M6.2.2** Competitive Matrix | Feature/price/performance comparison matrix | Product Marketing | Week 3-4 | Matrix complete | Missing competitors |
| **M6.2.3** Funding Analysis | Competitor funding history and runway | Market Research | Week 2 | Analysis complete | Missing funding data |
| **M6.2.4** Product Roadmaps | Competitive product roadmaps | Market Research | Week 3-4 | Roadmaps documented | Roadmap intelligence missing |
| **M6.2.5** Pricing Intelligence | Competitive pricing and discounting practices | Market Research | Week 3 | Pricing documented | Pricing not available |

### Key Competitors to Analyze

| Competitor | Funding | Market Position | Threat Level | Key Intelligence Needed |
|------------|---------|-----------------|--------------|------------------------|
| Hailo | $400M+ | Raspberry Pi partner, shipping | CRITICAL | Pricing strategy, roadmap |
| NVIDIA Jetson | Infinite | Market leader | HIGH | Edge product roadmap |
| Taalas | $169M | Same architecture, datacenter | HIGH | Edge expansion plans |
| Samsung | $300B MC | Foundry + chip design | HIGH | Edge LLM plans |
| Rockchip | Public | Chinese market leader | MEDIUM | LLM-specific products |
| Espressif | Public | Maker market dominance | MEDIUM | LLM co-processor plans |

---

## 6.3 Customer Validation Metrics

### Purpose
Establish metrics to validate customer demand and traction.

### Checklist Items

| Item | Required Deliverable | Responsible Party | Timeline | Success Criteria | Red Flags |
|------|---------------------|-------------------|----------|------------------|-----------|
| **M6.3.1** Customer Pipeline | Named customer pipeline with stages | VP Sales | Week 2-4 | Pipeline documented | No named customers |
| **M6.3.2** LOI Collection | Letters of Intent from potential customers | VP Sales | Week 4-8 | $200K+ in LOIs | No LOIs |
| **M6.3.3** Beta Customer Program | Beta customer program design | Product Manager | Week 3 | Program designed | No beta program |
| **M6.3.4** Customer Success Metrics | Metrics for measuring customer success | Product Manager | Week 4 | Metrics defined | No success metrics |
| **M6.3.5** NPS/CSAT Tracking | Plan for tracking customer satisfaction | Product Manager | Week 4 | Tracking plan | No satisfaction tracking |

### Customer Pipeline Stages

| Stage | Definition | Target Volume | Conversion Rate |
|-------|------------|---------------|-----------------|
| Awareness | Knows about product | 1,000+ | N/A |
| Interest | Requested information | 200+ | 20% |
| Evaluation | Testing/evaluating | 50+ | 25% |
| Commitment | LOI or pre-order | 20+ | 40% |
| Closed | Purchased | 10+ | 50% |

---

# 7. Summary: Critical Path Items

## Must Complete Before Investment (Seed Stage)

| Priority | Item | Category | Timeline | Blocker Risk |
|----------|------|----------|----------|--------------|
| 1 | FPGA Demo Independent Validation | Technical | Week 1-2 | HIGH |
| 2 | Patent Prior Art Search | Legal | Week 2-4 | HIGH |
| 3 | Founder Reference Checks | Team | Week 1-2 | MEDIUM |
| 4 | IP Assignment Verification | Legal | Week 1 | HIGH |
| 5 | Burn Rate Reality Check | Financial | Week 1-2 | HIGH |
| 6 | TSMC Allocation Confirmation | Commercial | Week 2 | HIGH |
| 7 | Memory Supply Agreement | Commercial | Week 4 | MEDIUM |

## Must Complete Before Series A

| Priority | Item | Category | Timeline | Blocker Risk |
|----------|------|----------|----------|--------------|
| 1 | MPW Silicon Validated | Technical | Month 14 | CRITICAL |
| 2 | Independent Performance Benchmarks | Technical | Month 14 | CRITICAL |
| 3 | Customer LOIs ($500K+) | Commercial | Month 14 | HIGH |
| 4 | VP Sales Hired | Team | Month 3-6 | HIGH |
| 5 | Utility Patents Filed | Legal | Month 6 | HIGH |
| 6 | Manufacturing Cost Validated | Financial | Month 12 | HIGH |
| 7 | Distribution Agreements | Commercial | Month 12 | MEDIUM |

---

# 8. Red Flag Summary Matrix

## Critical Red Flags (Must Resolve)

| Red Flag | Category | Detection Method | Resolution Path |
|----------|----------|------------------|-----------------|
| No production silicon | Technical | FPGA demo only | MPW tape-out |
| Patent position weak | Legal | Prior art search | Utility patents filed |
| Model lock-in contradiction | Technical | Architecture review | Clear explanation needed |
| Competitive response underestimated | Commercial | Scenario analysis | Competitive playbook |
| Unrealistic financial projections | Financial | Model review | Revised projections |

## Major Red Flags (Should Resolve)

| Red Flag | Category | Detection Method | Resolution Path |
|----------|----------|------------------|-----------------|
| VP Sales not hired | Team | Organization chart | Hiring plan |
| Burn rate unrealistically low | Financial | Budget review | Detailed budget |
| TSMC concentration | Commercial | Supply chain audit | Dual-source strategy |
| Memory price volatility | Commercial | Supplier analysis | Hedging strategy |
| Capital requirements underestimated | Financial | Capital plan | Revised capital plan |

## Moderate Red Flags (Monitor)

| Red Flag | Category | Detection Method | Resolution Path |
|----------|----------|------------------|-----------------|
| TAM/SAM inflated | Market | Bottom-up analysis | Revised sizing |
| Ecosystem building slow | Commercial | Community metrics | Developer relations |
| Channel timeline optimistic | Commercial | Distributor discussions | Revised timeline |
| Team depth gaps | Team | Skills assessment | Hiring plan |

---

# 9. Document Requirements Checklist

## Documents to Request

| Document | Category | Priority | Timeline |
|----------|----------|----------|----------|
| Cap table (fully diluted) | Financial | CRITICAL | Week 1 |
| Patent portfolio summary | Legal | CRITICAL | Week 1 |
| FPGA demo access | Technical | CRITICAL | Week 1 |
| 18-month budget | Financial | CRITICAL | Week 1 |
| COGS breakdown | Financial | CRITICAL | Week 2 |
| Customer pipeline | Commercial | HIGH | Week 2 |
| Competitive analysis | Commercial | HIGH | Week 2 |
| Technical architecture doc | Technical | HIGH | Week 2 |
| Employee roster | Team | HIGH | Week 1 |
| Supplier contracts | Commercial | HIGH | Week 2 |
| Partnership agreements | Commercial | MEDIUM | Week 3 |
| Board meeting minutes | Governance | MEDIUM | Week 3 |

---

# 10. Investment Decision Framework

## Go/No-Go Decision Matrix

| Factor | Weight | Score (1-10) | Weighted | Notes |
|--------|--------|--------------|----------|-------|
| Technology differentiation | 20% | | | |
| Market opportunity | 15% | | | |
| Competitive positioning | 15% | | | |
| Team execution capability | 15% | | | |
| Capital efficiency | 10% | | | |
| Exit clarity | 10% | | | |
| Risk-adjusted return | 15% | | | |
| **TOTAL** | **100%** | | | |

## Decision Thresholds

| Score | Decision | Action |
|-------|----------|--------|
| 8.0+ | Strong Invest | Lead round, board seat |
| 7.0-7.9 | Invest | Participate, observer rights |
| 6.0-6.9 | Conditional Pass | Seed only, milestone-based |
| 5.0-5.9 | Pass with Follow | Monitor, revisit after milestones |
| <5.0 | Hard Pass | Decline |

---

# 11. Contact Information for Due Diligence

## External Resources

| Resource | Purpose | Contact |
|----------|---------|---------|
| Technical Advisor | Architecture review | [To be assigned] |
| IP Counsel | Patent review | [To be assigned] |
| Market Research Firm | Customer interviews | [To be assigned] |
| Background Check Firm | Employment verification | [To be assigned] |
| Accounting Firm | Financial audit | [To be assigned] |

## Company Contacts for Due Diligence

| Role | Contact | Availability |
|------|---------|--------------|
| CEO | [Name] | Available Week 1+ |
| CTO | [Name] | Available Week 1+ |
| VP Engineering | [Name] | Available Week 1+ |
| Legal Counsel | [Name] | Available Week 1+ |

---

# Appendix A: Due Diligence Timeline

## Week-by-Week Schedule

| Week | Activities | Deliverables |
|------|------------|--------------|
| 1 | Document collection, founder interviews, cap table review | Document inventory, interview notes |
| 2 | Technical deep-dive, reference checks, market research | Technical assessment, references |
| 3 | Financial model review, competitive analysis, legal review | Financial assessment, competitive matrix |
| 4 | Customer interviews, supply chain audit, IP review | Customer insights, supply chain report |
| 5-6 | Synthesis, follow-up questions, expert consultations | Draft report |
| 7-8 | Final report, investment committee presentation | Final DD report |

---

# Appendix B: Key Metrics Dashboard

## Monthly Tracking Requirements

| Metric | Target | Frequency | Owner |
|--------|--------|-----------|-------|
| FPGA prototype performance | ≥90 tok/s | Monthly | CTO |
| MPW tape-out progress | On schedule | Monthly | VP Engineering |
| Customer LOIs | $200K by M18 | Monthly | VP Sales |
| Patent prosecution status | Utility filed by M6 | Monthly | Legal |
| Burn rate | <$50K/month initially | Monthly | CFO |
| Team hiring | VP Sales by M6 | Monthly | CEO |

## Quarterly Business Review Agenda

1. Technical milestone review
2. Customer pipeline review
3. Competitive landscape update
4. Financial model update
5. Supply chain risk assessment
6. IP status update
7. Team development review

---

**Document Prepared For:** Prospective Investors  
**Prepared By:** Due Diligence Team  
**Version:** 1.0  
**Date:** March 2026  
**Classification:** Confidential

---

*This checklist is designed to be used as a living document throughout the due diligence process. All items should be checked off and documented as they are completed.*

---

**END OF DUE DILIGENCE CHECKLIST**
