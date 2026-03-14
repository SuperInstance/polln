# Investment Memo: SuperInstance.AI Mask-Locked Inference Chip
## Series A Investment Review

**Fund:** Tier-1 Semiconductor/AI Fund ($5B+ AUM)  
**Reviewer:** Senior Partner (Stanford PhD EE, Former Intel, 3 AI Chip Exits)  
**Date:** March 2026  
**Classification:** Confidential - Investment Committee  

---

# Executive Summary

## Investment Recommendation: **INTERESTED** (Not Lead)

SuperInstance.AI presents a technically innovative but high-risk opportunity in the emerging edge LLM inference market. The mask-locked ternary architecture represents genuine IP differentiation, but execution risks are substantial and current valuation is aggressive for pre-silicon stage.

| Dimension | Assessment | Score |
|-----------|------------|-------|
| Market Opportunity | Large TAM, well-defined SAM | 8/10 |
| Technical Differentiation | Novel architecture, validation needed | 7/10 |
| Competitive Moat | 12-18 months, not defensible long-term | 4/10 |
| Team Capability | Critical gaps, no tape-out experience evident | 4/10 |
| Unit Economics | Attractive if silicon validates | 7/10 |
| Capital Efficiency | $8M ask reasonable for milestone | 6/10 |
| Exit Potential | Multiple strategic acquirers identified | 7/10 |
| **Overall** | **High-risk, high-reward edge AI bet** | **6.1/10** |

**Recommendation:** Participate in syndicate (not lead) with milestone-based structure. Require technical validation before full commitment.

---

# Section 1: Market Analysis

## 1.1 TAM/SAM/SOM Assessment

### TAM Analysis: **CREDIBLE**

The business model presents a $28.5B (2024) → $76.8B (2029) TAM at 22% CAGR, derived from composite analyst estimates:

| Source | Estimate | Assessment |
|--------|----------|------------|
| Gartner | $26.1B → $58.9B | Conservative, methodology sound |
| IDC Edge AI Chips | $3.67B → $11.54B | Chips only, appropriate filter |
| Fortune Business | $35.8B → $385.9B | Aggressive, includes services |
| Grand View | $24.9B → $118.7B | Mid-range, reasonable |

**Verdict:** TAM is well-researched and appropriately triangulated. The 22% CAGR aligns with my edge AI thesis and is conservative relative to AI hardware market growth.

### SAM Analysis: **AGGRESSIVE BUT DEFENSIBLE**

The $4.2B SAM derivation:
- Edge inference segment: 45% of TAM ✓ Reasonable
- LLM-capable (>1B param): 35% of inference ✓ Conservative
- Low-power (<10W TDP): 85% of LLM-capable ✓ Appropriate filter
- Developer-accessible: 110% adjustment ⚠️ Weakly justified

**Concern:** The 110% "developer-accessible" adjustment lacks rigorous justification. This adds $400M+ to SAM without clear methodology.

**Verdict:** SAM is directionally correct but may be overstated by 10-15%. A more conservative SAM of $3.6B-3.8B is appropriate.

### SOM Analysis: **REALISTIC BUT EXECUTION-DEPENDENT**

Year 5 target: 1.3% SOM ($70M revenue from $24M hardware + $46M services)

**Bottom-up validation from documents:**
- 76,000 units (bottom-up) vs 460,000 units (top-down) = 6x gap
- Documents acknowledge this represents "execution-dependent ceiling"
- Conservative bottom-up validates a $12M-15M Y5 floor

**Verdict:** SOM projections are internally consistent and acknowledge the gap between floor and ceiling. I find the Y5 $70M target achievable but not conservative.

## 1.2 Market Timing Assessment

**Edge LLM Thesis: STRONG**

My fund's thesis is that edge AI represents the next major compute paradigm shift. Evidence supporting this:

1. **Privacy regulations driving edge processing** - GDPR, CCPA, emerging AI regulations
2. **Latency requirements for autonomous systems** - Robotics, vehicles, industrial
3. **Connectivity constraints** - Remote/developing markets, disconnected scenarios
4. **Cost trajectory** - Edge inference becoming viable vs cloud for long-running workloads

**Validation from research:**
- BitNet b1.58-2B-4T: 16,010 monthly downloads, 36 Spaces, 18 finetunes
- Active developer community seeking hardware acceleration
- No dominant solution in sub-$100 LLM inference category

**Market timing score: 8/10** - Edge LLM is entering early mainstream adoption.

---

# Section 2: Competitive Analysis

## 2.1 Competitive Landscape

### Direct Competitors

| Company | Funding | Focus | Threat Level |
|---------|---------|-------|--------------|
| **Taalas** | $219M total | Data center mask-locked | LOW (different segment) |
| **Quadric** | $72M total | Edge LLM IP, programmable NPU | HIGH (direct competitor) |
| **Axelera AI** | $250M+ | Edge vision + GenAI, 214 TOPS | MEDIUM-HIGH |
| **Hailo** | $300M+ | Vision-focused, weak LLM | MEDIUM |
| **EnCharge AI** | $100M+ | Analog in-memory | MEDIUM |

### Key Competitive Insight

**Taalas validates the mask-locked approach but confirms NO edge/mobile signals:**
- $169M raised Feb 2026
- HC1 chip at 200W, data center only
- Job postings: NONE for mobile/embedded/edge
- Estimated time to edge product: 18-24 months minimum

**This creates a 12-18 month window for SuperInstance.AI to establish edge market position.**

### Competitive Moat Duration Assessment

| Moat Source | Duration | Assessment |
|-------------|----------|------------|
| Mask-locked architecture | 12-18 months | Taalas can pivot to edge |
| Ternary-native silicon | 18-24 months | Competitors adopting quantization |
| Price-performance | 12-18 months | FPGA improvements, new entrants |
| Model ecosystem | 24-36 months | Requires community investment |

**Critical concern:** The 12-18 month moat duration is insufficient for venture-scale returns. As the VC Partner persona noted: "12-18 months is NOT defensible."

**Moat score: 4/10** - Innovation is real but barriers to entry are lower than founders believe.

## 2.2 Technology Risk vs. Market Risk

### Technology Risk: **HIGH**

| Risk Factor | Probability | Impact | Mitigation |
|-------------|-------------|--------|------------|
| Silicon performance gap (20%+ below target) | 35% | High | FPGA demo mitigates partially |
| Power budget miss (>6W actual) | 25% | High | 28nm is mature process |
| Yield issues (<70%) | 30% | Medium | MPW provides data |
| Thermal throttling | 20% | Medium | Simulation data needed |

**Key validation from Kimi Swarm Report:**
- TeLLMe FPGA demonstrates 25 tok/s at 4.8W on KV260 platform
- This is the CRITICAL reference implementation
- Target performance (25-35 tok/s) is achievable but not differentiated

### Market Risk: **MEDIUM**

| Risk Factor | Probability | Impact | Mitigation |
|-------------|-------------|--------|------------|
| Model obsolescence (Llama-4, new architectures) | 40% | Critical | Hybrid architecture proposal |
| Developer adoption below projections | 30% | High | Zero-setup value prop strong |
| Memory price spike | 60% | Medium | Lock contracts now |
| Competitive entry accelerates | 50% | High | Speed to market |

**Market risk is lower than technology risk**, but the model obsolescence risk is underappreciated in the business model.

---

# Section 3: Unit Economics Analysis

## 3.1 Hardware Unit Economics

### Claimed Margins

| SKU | Price | COGS | Margin |
|-----|-------|------|--------|
| Nano | $35 | $14.50 | 59% |
| Standard | $79 | $21.30 | 73% |
| Pro | $149 | $35.00 | 77% |

### Reality Check from Kimi Swarm Report

**Critical finding:** LPDDR4 512MB at $10-12 (not $5 as assumed in COGS model)

| Component | Business Model | Actual (Mar 2026) | Variance |
|-----------|---------------|-------------------|----------|
| Memory (LPDDR4) | $3.00 | $10-12 | +233% |
| Die Cost (28nm) | $6.80 | $6.80 | 0% |
| Other components | $11.50 | $11.50 | 0% |
| **Revised COGS** | **$21.30** | **$28.30-30.30** | **+33-42%** |

### Revised Margin Analysis

| SKU | Price | Revised COGS | Revised Margin |
|-----|-------|--------------|----------------|
| Nano | $35 | $21.50-23.50 | **35-40%** (not 59%) |
| Standard | $79 | $28.30-30.30 | **62-64%** (not 73%) |
| Pro | $149 | $42.00-44.00 | **70-72%** (not 77%) |

**Verdict:** Nano margin is critically thin. Standard and Pro margins remain attractive but 10-15% lower than projected.

## 3.2 Customer Economics

### LTV:CAC Analysis

| Segment | Claimed LTV | Claimed CAC | Claimed Ratio | My Assessment |
|---------|-------------|-------------|---------------|---------------|
| Hobbyist | $205 | $35 | 5.9:1 | Realistic |
| Professional | $965 | $85 | 11.4:1 | Aggressive |
| Enterprise | $19,900 | $1,850 | 10.8:1 | Unsupported |

**Concerns:**
1. Professional segment assumes 24-month subscription retention - no data to support
2. Enterprise LTV assumes 10-unit hardware purchase - no LOIs presented
3. CAC estimates for community-led growth appear optimistic ($35-85)

### Payback Period

| Segment | Claimed | My Estimate | Risk |
|---------|---------|-------------|------|
| Hobbyist | 1.5 months | 3-4 months | Medium |
| Professional | 2.1 months | 6-9 months | High |
| Enterprise | 3 months | 12-18 months | High |

**Verdict:** Unit economics are directionally attractive but founder projections are 30-50% more optimistic than my estimates. I would model payback periods 2x longer than claimed.

---

# Section 4: Team Capability Assessment

## 4.1 Critical Gaps Identified

From cross-persona synthesis and my experience:

| Role | Required Experience | Current Status | Gap Severity |
|------|--------------------|----------------|--------------|
| VP Manufacturing | 3+ tape-outs, foundry relationships | NOT MENTIONED | **CRITICAL** |
| Silicon Validation Lead | 5+ chip bring-ups | NOT MENTIONED | **HIGH** |
| Software Lead | SDK development, developer tools | Mentioned, unclear experience | MEDIUM |
| VP Sales/BD | Channel development, distributor relationships | NOT MENTIONED | HIGH |
| Thermal/Mechanical | Edge product design | NOT MENTIONED | MEDIUM |

**Critical insight from Hardware CEO persona:**
> "VP Manufacturing is CRITICAL — hire now"

### Team Tape-Out Experience

**Required for Series A hardware:** At least 2 team members with 3+ successful tape-outs.

**Evidence from documents:** None. No team bios or experience summaries provided.

**This is a deal-breaker concern** that must be addressed in due diligence.

## 4.2 Team Score: 4/10

Significant gaps in critical roles. Would require senior hires before or concurrent with funding.

---

# Section 5: Valuation Analysis

## 5.1 Asking Valuation

**Ask:** $8M Series A at $40M pre-money ($48M post-money)

## 5.2 Comparable Analysis

### Pre-Revenue Hardware Comparables

| Company | Stage | Pre-Money | Key Differentiator |
|---------|-------|-----------|-------------------|
| Quadric Series A | Pre-silicon, IP only | $80M | Ex-Intel founding team |
| Axelera Series A | Pre-silicon | $100M | Imperial College pedigree |
| EnCharge Series A | Pre-silicon | $60M | Princeton research spin-out |
| Taalas Seed | Pre-silicon | $50M | Pierre Lamond backing |

### Pre-Silicon Valuation Drivers

| Driver | Value Range | SuperInstance Status |
|--------|-------------|---------------------|
| Working FPGA demo | +$10-20M | ✓ TeLLMe validates |
| Patent portfolio (granted) | +$5-15M per patent | Only provisional |
| Fortune 500 LOIs | +$10-30M | Not mentioned |
| Ex-NVIDIA/Intel team | +$20-40M | Not demonstrated |
| Novel architecture IP | +$10-30M | ✓ Ternary + iFairy |

### My Valuation Assessment

| Methodology | Valuation Range |
|-------------|-----------------|
| Comparable pre-silicon | $25-45M pre-money |
| Risk-adjusted DCF | $20-35M pre-money |
| Cost-to-recreate | $15-25M pre-money |
| **Blended** | **$25-35M pre-money** |

**Verdict:** The $40M pre-money ask is at the top of my acceptable range for pre-silicon with no tape-out experience on team. A $30-35M pre-money would be more appropriate.

## 5.3 Funding Structure Recommendation

**Proposed Structure:** Milestone-based tranched investment

| Tranche | Amount | Milestone | Timeline |
|---------|--------|-----------|----------|
| 1 | $2M | Gate 0 FPGA demo ≥25 tok/s | Month 6 |
| 2 | $3M | RTL complete, timing clean | Month 10 |
| 3 | $3M | MPW silicon functional | Month 18 |
| **Total** | **$8M** | | |

This structure protects investor capital while providing runway for technical validation.

---

# Section 6: Exit Scenarios

## 6.1 Strategic Acquirers

### Primary Targets

| Acquirer | Rationale | Probability | Est. Exit Value |
|----------|-----------|-------------|-----------------|
| **Qualcomm** | Edge AI expansion, acquired Alphawave ($2.4B), Arduino | 35% | $200-500M |
| **Intel** | Habana Labs ($2B), edge strategy | 20% | $150-300M |
| **NVIDIA** | Edge inference portfolio | 15% | $300-600M |
| **MediaTek** | Mobile edge AI | 15% | $150-250M |
| **Apple** | On-device AI | 10% | $200-400M |
| **AMD** | Xilinx edge strategy | 5% | $100-200M |

### Secondary Targets

| Acquirer | Rationale | Est. Exit Value |
|----------|-----------|-----------------|
| Samsung | Mobile processor division | $100-200M |
| Synaptics | Edge AI expansion | $80-150M |
| NXP | Automotive edge AI | $100-180M |

## 6.2 Exit Timing Analysis

### Scenario Modeling

| Scenario | Timeline | Exit Multiple | Exit Value | IRR |
|----------|----------|---------------|------------|-----|
| Bull case | Year 4 | 8x revenue ($560M) | $560M | 85% |
| Base case | Year 5 | 5x revenue ($350M) | $350M | 48% |
| Bear case | Year 6 | 3x revenue ($210M) | $210M | 28% |
| Distressed | Year 3 | Acqui-hire | $50M | 2% |

### Exit Probability Distribution

| Outcome | Probability | Return to Fund |
|---------|-------------|----------------|
| >5x return | 20% | $40M+ on $8M |
| 2-5x return | 35% | $16-40M |
| 1-2x return | 25% | $8-16M |
| Partial loss | 15% | $2-8M |
| Total loss | 5% | $0 |

**Expected value: $21M on $8M investment = 2.6x gross multiple**

---

# Section 7: Key Risks Ranked by Severity

## Severity Ranking

| Rank | Risk | Severity | Probability | Mitigatable |
|------|------|----------|-------------|-------------|
| 1 | **Team tape-out experience gap** | CRITICAL | 90% | Yes - hire |
| 2 | **Silicon performance miss (>20%)** | CRITICAL | 35% | Partial - FPGA demo |
| 3 | **Model obsolescence risk** | HIGH | 40% | Yes - hybrid architecture |
| 4 | **Competitive entry (Quadric, Axelera)** | HIGH | 50% | Partial - speed |
| 5 | **Memory pricing impact on margins** | HIGH | 60% | Yes - contracts, pricing |
| 6 | **Pre-silicon funding risk** | HIGH | 40% | Yes - tranches |
| 7 | **12-18 month moat duration** | MEDIUM | 80% | No - inherent |
| 8 | **Developer adoption below plan** | MEDIUM | 30% | Yes - community investment |
| 9 | **Thermal/power budget miss** | MEDIUM | 25% | Yes - design margin |
| 10 | **Manufacturing yield issues** | MEDIUM | 30% | Partial - MPW data |

---

# Section 8: Red Flags and Deal-Breakers

## 8.1 Critical Red Flags

### 🔴 RED FLAG #1: No Tape-Out Experience on Team

**Finding:** Documents do not mention any team member with silicon tape-out experience. The Silicon Engineer persona rated "Team execution capability 6/10" with "execution unknown."

**Impact:** First silicon failure rate for inexperienced teams exceeds 40%. This could result in 12-18 month delays and $5M+ additional spend.

**Requirement:** Must hire VP Manufacturing and Silicon Validation Lead with 3+ successful tape-outs BEFORE MPW commitment.

### 🔴 RED FLAG #2: Memory Pricing Crisis

**Finding:** LPDDR4 512MB at $10-12 (not $5), with SK Hynix forecasting tight supply through 2028.

**Impact:** 
- Nano margin drops from 59% to 35-40%
- Nano may be unprofitable at $35 price point
- Total COGS impact: +33-42%

**Requirement:** Must lock LPDDR4 supply contracts immediately and consider $99 price point for mainstream product.

### 🔴 RED FLAG #3: KV Cache Architecture Unrealistic

**Finding:** Silicon Engineer persona noted "900MB SRAM impossible" - the specification claims 2MB on-chip KV cache supporting 4096 token context.

**Impact:** Performance claims may not be achievable. Context length may be limited to 512-1024 tokens without architecture revision.

**Requirement:** Must present detailed memory architecture with realistic sizing before investment.

### 🔴 RED FLAG #4: Model Lock-In Creates Inventory Risk

**Finding:** Mask-locked weights cannot be updated. If Llama-4 or new architectures emerge, inventory becomes obsolete.

**Impact:** Every persona identified this as a critical concern. VC Partner noted "Inventory obsolescence risk."

**Requirement:** Must adopt hybrid architecture proposal with adapter slots.

## 8.2 Deal-Breakers (Would Cause Pass)

| Condition | Status |
|-----------|--------|
| No hire of VP Manufacturing with tape-out experience | **DEAL-BREAKER** |
| No FPGA demo ≥20 tok/s before full commitment | **DEAL-BREAKER** |
| No mitigation plan for model obsolescence | **DEAL-BREAKER** |
| Valuation above $45M pre-money | **DEAL-BREAKER** |
| No LPDDR4 supply contract before volume | **DEAL-BREAKER** |

---

# Section 9: Due Diligence Requirements

## 9.1 Technical Due Diligence

| Item | Requirement | Owner | Timeline |
|------|-------------|-------|----------|
| FPGA demo validation | Third-party benchmark ≥25 tok/s | External lab | 4 weeks |
| Power measurement | Independent verification ≤5W | External lab | 4 weeks |
| RTL review | Architecture assessment | Fund technical advisor | 2 weeks |
| Thermal simulation | CFD analysis, <70°C at 25°C ambient | Fund technical advisor | 2 weeks |
| Memory architecture | Realistic KV cache sizing | Fund technical advisor | 2 weeks |
| Patent search | Freedom to operate, prior art | Legal counsel | 4 weeks |
| IP assignment | Confirm ownership of all IP | Legal counsel | 2 weeks |

## 9.2 Commercial Due Diligence

| Item | Requirement | Owner | Timeline |
|------|-------------|-------|----------|
| Customer discovery | 20+ interviews with target developers | Fund BD team | 4 weeks |
| Competitive benchmarking | Detailed comparison vs Hailo, Jetson | Fund analyst | 2 weeks |
| Channel validation | Discussions with Digi-Key, SparkFun | Fund BD team | 3 weeks |
| Memory supply contract | Draft agreement with supplier | Fund ops | 4 weeks |

## 9.3 Financial Due Diligence

| Item | Requirement | Owner | Timeline |
|------|-------------|-------|----------|
| Cap table verification | Confirm all shareholders | Legal counsel | 2 weeks |
| Revenue model stress test | Sensitivity analysis | Fund analyst | 2 weeks |
| Burn rate analysis | Detailed 18-month cash flow | Fund CFO | 2 weeks |
| Manufacturing cost validation | Third-party COGS estimate | External consultant | 3 weeks |

## 9.4 Team Due Diligence

| Item | Requirement | Owner | Timeline |
|------|-------------|-------|----------|
| Reference checks | 5+ references per key hire | Fund team | 3 weeks |
| Technical interviews | Deep-dive with architecture lead | Fund technical advisor | 2 weeks |
| Background checks | All founders and key hires | External firm | 3 weeks |
| Employment verification | Confirm claimed experience | External firm | 2 weeks |

---

# Section 10: Milestone Requirements for Next Round

## Series A → Series B Milestones

### Technical Milestones (Must Achieve)

| Milestone | Target | Timeline | Verification |
|-----------|--------|----------|--------------|
| MPW silicon functional | Power-on, inference running | Month 14 | Investor demo |
| Performance validation | ≥20 tok/s, ≤6W | Month 16 | Third-party benchmark |
| Yield characterization | >65% yield at foundry | Month 16 | Manufacturing report |
| Volume mask commitment | Qualified for production | Month 18 | Foundry contract |

### Commercial Milestones (Must Achieve)

| Milestone | Target | Timeline | Verification |
|-----------|--------|----------|--------------|
| Beta customers | 100+ paying customers | Month 12 | Revenue recognition |
| Distributor signing | 1+ tier-1 distributor | Month 14 | Signed agreement |
| Community growth | 5,000+ Discord, 500+ GitHub stars | Month 12 | Platform analytics |
| Revenue | $500K+ ARR | Month 18 | Financial statements |

### Team Milestones (Must Achieve)

| Milestone | Target | Timeline | Verification |
|-----------|--------|----------|--------------|
| VP Manufacturing hire | 5+ tape-outs experience | Month 4 | Signed offer |
| Silicon Validation Lead hire | 3+ chip bring-ups | Month 6 | Signed offer |
| VP Sales/BD hire | Channel experience | Month 8 | Signed offer |

## Series B Conversation Triggers

Any of the following would trigger Series B discussion:

1. MPW silicon exceeds performance targets by >15%
2. Fortune 500 LOI for >$1M deployment
3. Strategic acquisition interest
4. Revenue exceeding $1M ARR before Month 15

---

# Section 11: Investment Committee Recommendation

## Summary Position

**SuperInstance.AI represents a high-risk, high-reward opportunity that aligns with our edge AI thesis. The mask-locked ternary architecture is technically innovative and the market timing is favorable. However, execution risks are substantial, particularly around team experience and model obsolescence.**

## Recommendation: **INTERESTED (Syndicate Participant)**

### Conditions for Investment:

1. **Valuation:** Maximum $35M pre-money (not $40M)
2. **Structure:** Tranche-based with technical milestones
3. **Team:** VP Manufacturing hire required before Tranche 2
4. **Technical:** FPGA demo validation by third party
5. **Architecture:** Commit to hybrid architecture with adapters

### Recommended Investment:

| Parameter | Value |
|-----------|-------|
| Investment Size | $2-3M (syndicate participant) |
| Valuation | $30-35M pre-money |
| Structure | Preferred stock with milestone warrants |
| Board Seat | Observer rights, not full seat |
| Pro-rata Rights | Yes for Series B |

### Pass Conditions (Would Not Invest):

- Team cannot hire VP Manufacturing with tape-out experience
- FPGA demo fails to achieve ≥20 tok/s
- Founders refuse hybrid architecture approach
- Valuation insisted at $40M+
- No progress on memory supply contracts

---

# Appendix A: Key Data Points Summary

| Metric | Claimed | My Assessment | Variance |
|--------|---------|---------------|----------|
| TAM (2029) | $76.8B | $76.8B | 0% |
| SAM (2029) | $18.5B | $15-16B | -15% |
| Y5 Revenue | $70M | $40-50M | -30% |
| Hardware Gross Margin | 74% | 62-65% | -12% |
| LTV:CAC | 7.6:1 | 5-6:1 | -25% |
| Moat Duration | Not specified | 12-18 months | - |
| Time to MPW | Not specified | 14 months | - |
| Silicon Success Probability | Not specified | 60-70% | - |

---

# Appendix B: Competitive Comparison Matrix

| Company | Tech | Funding | Focus | LLM Speed | Power | Price |
|---------|------|---------|-------|-----------|-------|-------|
| **SuperInstance** | Mask-locked ternary | $8M ask | Edge LLM | 25-35 t/s | 3-5W | $35-149 |
| Hailo-10H | Dataflow NPU | $300M+ | Vision + LLM | 9.5 t/s | 2.5W | $88 |
| Jetson Orin Nano | GPU | NVIDIA funded | General AI | 15 t/s | 7W | $199 |
| Quadric Chimera | Programmable NPU | $72M | Edge LLM IP | TBD | TBD | IP license |
| Axelera Metis | In-memory compute | $250M+ | Vision + GenAI | TBD | 10W | TBD |
| Google Coral | TPU | Google funded | Edge inference | N/A (no LLM) | 2W | $60 |

**SuperInstance advantage:** 3x price-performance ratio vs. nearest competitor for LLM inference.

---

# Appendix C: Investment Thesis Alignment

| Fund Thesis Element | SuperInstance Alignment | Score |
|---------------------|------------------------|-------|
| Edge AI is next paradigm shift | ✓ Core positioning | 9/10 |
| Privacy driving edge processing | ✓ Value prop | 8/10 |
| Cost trajectory enabling new use cases | ✓ $35 price point | 9/10 |
| Technical moat required | ⚠ 12-18 months only | 4/10 |
| Experienced team | ✗ Critical gaps | 3/10 |
| Clear exit pathway | ✓ Multiple strategics | 8/10 |

**Overall thesis alignment: 7/10**

---

**Document Prepared By:** Senior Partner, Semiconductor/AI Fund  
**Investment Committee Distribution Only**  
**Next Steps:** Schedule technical deep-dive with founding team  
