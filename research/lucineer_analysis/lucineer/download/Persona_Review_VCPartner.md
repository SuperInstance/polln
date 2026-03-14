# SuperInstance.AI Investment Review
## Partner-Level Due Diligence Analysis | March 2026

**Reviewer Profile:** Partner, Tier-1 VC Firm (Sequoia/a16z/Accel equivalent)  
**Investment Focus:** Deep Tech & Semiconductors  
**Track Record:** 3 semiconductor investments (2 exits totaling $800M+, 1 unicorn)  
**Review Volume:** 500+ deals yearly  

---

# EXECUTIVE SUMMARY

## Investment Recommendation: **CONDITIONAL PASS - SEED STAGE ONLY**

**Overall Score: 5.5/10** — Interesting technology thesis with significant execution and market risks requiring substantial de-risking before Series A commitment.

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Technology Innovation | 8/10 | 20% | 1.6 |
| Market Opportunity | 6/10 | 20% | 1.2 |
| Competitive Moat | 5/10 | 15% | 0.75 |
| Team Execution Capability | 5/10 | 15% | 0.75 |
| Unit Economics | 6/10 | 10% | 0.6 |
| Capital Efficiency | 4/10 | 10% | 0.4 |
| Exit Clarity | 6/10 | 10% | 0.6 |
| **TOTAL** | | | **5.5/10** |

---

# 1. INVESTMENT THESIS ANALYSIS

## 1.1 Thesis Strengths

### Technical Innovation (8/10)

**The mask-locked architecture is genuinely novel and addresses a real bottleneck:**

| Innovation | Technical Merit | Validation Status |
|------------|-----------------|-------------------|
| **Ternary Weight Encoding** | 16x memory bandwidth reduction vs FP16 | Validated by Microsoft BitNet (16,010+ HuggingFace downloads) |
| **Mask-Locked Storage** | Eliminates DRAM access latency/power | FPGA prototype validated at 94 tok/s |
| **iFairy Complex Arithmetic** | Multiplication-free inference (10x power reduction) | Peking University research (arXiv:2508.05571) |
| **Kirchhoff's Law Computation** | Current-based matrix multiply | Theoretically sound, silicon validation pending |

**Why This Matters:**
- DRAM access is the #1 power consumer in edge inference (100-200 pJ/bit)
- Memory bandwidth bottleneck is the primary constraint on edge AI performance
- 28nm process at $35 price point could be genuinely disruptive if validated

### Clear Market Gap (7/10)

**Underserved segment identified:**

| Market Segment | Current Solutions | Gap |
|----------------|-------------------|-----|
| Sub-$50 LLM inference | None | **No competitor addresses this price point** |
| Sub-$100 LLM inference | Hailo-10H ($88, 9 tok/s) | Performance gap: SuperInstance claims 25-35 tok/s |
| Battery-powered LLM | Jetson Orin (7W minimum) | Power gap: SuperInstance claims 3W |

**Google Coral EOL creates immediate opportunity:**
- 500K+ devices seeking replacement
- Developer ecosystem disrupted
- SuperInstance positioned to capture transition

### Unit Economics Potential (7/10)

**Margin structure is attractive if yield assumptions hold:**

| Product | ASP | COGS | Gross Margin | Assessment |
|---------|-----|------|--------------|------------|
| Nano ($35) | $35 | $14.50 | 59% | Achievable at scale |
| Standard ($79) | $79 | $21.30 | 73% | **Requires 82% yield** |
| Pro ($149) | $149 | $35.00 | 77% | Enterprise focus |

**LTV:CAC ratios are healthy:**
- Hobbyist: 5.9:1 ✓
- Professional: 11.4:1 ✓
- Enterprise: 10.8:1 ✓
- Blended: 7.6:1 ✓

---

## 1.2 Thesis Weaknesses

### Pre-Silicon Risk (CRITICAL)

**The fundamental problem: There is no production silicon.**

```
STATED: "25-35 tokens/second on 2B parameter models at 3W"
REALITY: Demonstrated on FPGA (94 tok/s on 0.73B model)
GAP: MPW silicon may not achieve stated performance targets

Industry Statistics:
- First silicon functional: 60-70% (experienced teams) vs 30-40% (first-time teams)
- First silicon meeting all specs: 40-50% (experienced) vs 10-20% (first-time)
- Full respin required: 15-25% (experienced) vs 40-60% (first-time)
```

**What keeps me up at night:**
- 28nm process constraints limit performance ceiling vs competitors at 7nm/5nm
- Yield uncertainty: margins depend on 82% yield assumption
- First silicon often has 40-60% yield initially

### Model Lock-In Creates Inventory Risk (HIGH)

**The fundamental business model contradiction:**

```
ARCHITECTURE: Each chip = One model baked into silicon via photolithographic masks
REALITY: Model versions change every 3-6 months
RISK: Inventory obsolescence

Example Scenario:
- Month 0: Ship Llama-3 chip at $79
- Month 6: Llama-4 released with improved architecture
- Month 6+: Llama-3 chips lose significant value
- Customer reaction: "Why buy now when better version coming?"
```

**The "Obsolescence Anxiety" Problem:**
1. Customer thinks: "This $50 chip runs LLM-X v2.1 today"
2. "In 6 months, LLM-X v3.0 will be released"
3. "My chip can't run v3.0"
4. "My $50 investment is now worthless"
5. → Purchase hesitation or delay

**Mitigation Unclear:** Document mentions "model cartridges" but this contradicts mask-locked architecture. How do cartridges work if weights are in metal layers?

### Competitive Moat Duration (MEDIUM-HIGH)

**12-18 month claimed moat is not defensible:**

| Threat | Timeline | Probability | Impact |
|--------|----------|-------------|--------|
| **Taalas** | 18-24 months | 25% | Direct technology competitor, $169M raised |
| **Hailo price response** | Immediate | 90% | Price war erodes margins |
| **NVIDIA Jetson refresh** | 6-12 months | 60% | Feature/performance competition |
| **Samsung entry** | 18-24 months | 35% | Existential threat (foundry + design) |

**Taalas Specifically:**
- Raised $169M in Feb 2026 (34x SuperInstance's $5M ask)
- Same mask-locked architecture approach
- Currently datacenter-focused but could pivot to edge in 18-24 months
- Demonstrated 17,000 tokens/second on their hardware

### TAM/SAM/SOM Reality Check (MEDIUM)

**Market sizing appears inflated:**

```
STATED TAM: $76.8B by 2029
MY ASSESSMENT: Industry-wide figure, not addressable

STATED SAM: $4.2B (2024) → $18.5B (2029)
MY ASSESSMENT: $800M-1.2B for sub-$100 edge inference segment

STATED SOM: $210M (2024) → $1.85B (2029)
MY ASSESSMENT: Realistic but growth assumptions aggressive
```

**Bottom-Up Reality:**
- 1.2M edge AI developers globally
- Target penetration: 3.6% by Y5
- At $52 blended ASP = ~$2.3M hardware revenue Y5
- Gap with top-down projection: ~10x

---

# 2. CRITICAL DUE DILIGENCE QUESTIONS (27 Questions)

## Technology & Engineering (Questions 1-8)

### Q1: What is your detailed MPW-to-production timeline?

**Required:** Month-by-month milestones with technical gates

### Q2: What is your expected first silicon yield, and what is your contingency if yield is below 50%?

**Concern:** Margins assume 82% yield. What happens at 60% yield?

| Yield | COGS Impact | Gross Margin |
|-------|-------------|--------------|
| 82% (stated) | $21.30 | 73% |
| 70% | $24.90 | 68% |
| 60% | $29.05 | 63% |
| 50% | $34.86 | 56% |

### Q3: How do you handle model version changes when weights are mask-locked into silicon?

**Specific scenario:** If Llama-4 releases 6 months after you ship Llama-3 chips, what happens to your inventory?

### Q4: Your FPGA prototype shows 94 tok/s on 0.73B model. What is your confidence level for achieving 25-35 tok/s on 2B model in production silicon?

**Required:** Show PPA (Power-Performance-Area) analysis

### Q5: What is your total development cost to achieve production-ready silicon?

**My estimate:** $15-40M total to reach meaningful revenue

| Stage | Cost | Timeline |
|-------|------|----------|
| Architecture Freeze | $2-5M | Months 1-6 |
| First Silicon (MPW) | $5-10M | Months 7-14 |
| Production Masks | $10-30M | Months 15-24 |
| Working Capital | $5-15M | Ongoing |

### Q6: How does your iFairy complex weight architecture handle the output layer, which typically requires full-precision computation?

### Q7: What is your expected power consumption breakdown at 5W total budget?

**Concern:** Stated 3W for Standard product seems aggressive for inference operations

### Q8: What is your verification methodology and coverage target before tape-out?

**Industry standard:** 100% code coverage, 100% functional coverage, 95%+ assertion coverage

---

## Market & Competition (Questions 9-16)

### Q9: Hailo has $400M+ in funding, Raspberry Pi partnership, and shipping products. Why will developers choose SuperInstance over Hailo-10H?

**Required:** Be specific about 3-5x performance claim validation

### Q10: What is your detailed competitive response plan if Hailo drops prices by 40%?

**Margin sensitivity:**

| Scenario | Hailo Price | SuperInstance Price | Margin Impact |
|----------|-------------|---------------------|---------------|
| Current | $88 | $79 | 73% |
| Hailo -20% | $70 | $79 | 73% (competitive pressure) |
| Hailo -40% | $53 | $79 | Must respond or lose |

### Q11: Taalas raised $169M in Feb 2026 for similar mask-locked architecture. How do you differentiate?

**Taalas specifics:**
- 17,000 tokens/second demonstrated
- 2-month lead time from model to silicon
- 53B transistors (vs iPhone A18's 15B for GPU+CPU)

### Q12: What percentage of your TAM is actually addressable for sub-$100 edge inference?

**Required:** Bottom-up calculation, not top-down market research

### Q13: What is your specific capture strategy for Google Coral EOL installed base (500K+ devices)?

**Required:** Conversion rate assumptions, timeline, channel strategy

### Q14: What are the top 3 enterprise accounts in your pipeline?

**Required:** Specific accounts, not generic segments. Stage indicators: Evaluation / POC / LOI / Contract

### Q15: How do you plan to address the Chinese market (35-40% of edge AI device production)?

**Chinese competitors to analyze:**
- Rockchip RK3588: $75-150, widely deployed
- Horizon Robotics Journey series
- Cambricon: Listed company with edge AI chips
- Baidu Kunlun: Edge inference capabilities

### Q16: What is your total addressable market for fixed-model edge inference specifically?

**Market segmentation by flexibility need:**

| Segment | % of TAM | Addressable by Frozen |
|---------|----------|----------------------|
| High Flexibility (reject frozen) | 30% | 0% |
| Medium Flexibility (conditional) | 40% | 25% |
| Low Flexibility (ideal target) | 30% | 100% |

---

## Team & Execution (Questions 17-20)

### Q17: Who is your VP of Sales and what is your enterprise GTM team plan?

**Gap identified:** No VP Sales named in materials

### Q18: Your burn rate is stated at $28K/month. This seems unrealistically low for a semiconductor company.

**Required:** Detailed 18-month operating budget

**My estimate:** $200-500K/month burn rate for semiconductor startup

### Q19: What is your hiring plan for the next 18 months?

**Critical hires needed:**

| Role | Timeline | Salary Range | Priority |
|------|----------|--------------|----------|
| VP Sales | Month 1-3 | $180-220K | CRITICAL |
| Physical Design Lead | Month 1-6 | $200-280K | CRITICAL |
| Verification Lead | Month 1-6 | $160-220K | HIGH |
| VP Engineering | Month 6-12 | $200-280K | HIGH |
| CFO | Month 6-12 | $180-240K | MEDIUM |

### Q20: What is the combined tape-out experience of your technical leadership?

**Investor benchmark:** 15+ combined tape-outs across critical roles

| Role | Minimum Tape-Outs | Preferred |
|------|-------------------|-----------|
| CTO/Architecture Lead | 3+ full SoC | 5+ including advanced node |
| Physical Design Lead | 5+ | 10+ at target node |
| Verification Lead | 3+ full chip | 5+ |

---

## Financial & Unit Economics (Questions 21-24)

### Q21: Your COGS assumes 82% yield. What is your break-even yield?

**At what yield does the business become unprofitable?**

### Q22: LPDDR4 pricing is up 80-90% in Q1 2026. How does this impact your $21.30 COGS?

**Memory price sensitivity:**

| LPDDR4 512MB Price | Memory COGS | Total COGS | Margin |
|-------------------|-------------|------------|--------|
| $5.00 (baseline) | $3.00 | $21.30 | 73% |
| $10.00 (current) | $6.00 | $24.30 | 69% |
| $15.00 (shortage) | $9.00 | $27.30 | 65% |
| $18.00 (extreme) | $10.80 | $29.10 | 63% |

### Q23: What is your total capital requirement to reach $10M ARR?

**Required:** Include working capital, inventory, R&D

**My estimate:** $25-50M total capital required

### Q24: You project 12x revenue growth from Y1 to Y2 ($240K to $2.9M). What specific customer contracts or LOIs support this?

**Reality check:** Hardware startups rarely hit Y1 projections (50-70% miss rate)

---

## Intellectual Property & Exit (Questions 25-27)

### Q25: You have filed provisional patents. What is your prior art search results?

**Specific concern:** How do you distinguish from Taalas patents filed in 2024-2025?

### Q26: What are the specific milestones that would trigger M&A interest from Qualcomm or Apple?

**Acquirer priority matrix:**

| Acquirer | Likelihood | Valuation Range | Trigger Milestones |
|----------|------------|-----------------|-------------------|
| Qualcomm | 50-60% | $200-500M | Working silicon, $5M ARR |
| Apple | 30-40% | $80-150M | Team + IP value |
| MediaTek | 40-50% | $100-250M | Production silicon |
| NVIDIA | 15-25% | $150-300M | Licensing model |

### Q27: If you fail to achieve product-market fit, what is your IP monetization strategy?

**Distressed sale value:** $20-80M for patent portfolio

---

# 3. RISK ASSESSMENT MATRIX

## Probability × Impact Analysis

| Risk Category | Probability | Impact | Risk Score | Mitigation |
|---------------|-------------|--------|------------|------------|
| **Pre-Silicon Failure** | 35-50% | Critical | 9/10 | MPW validation before Series A |
| **Model Obsolescence** | 60% | High | 8/10 | Hybrid architecture with adapters |
| **Taalas Competition** | 25% | Critical | 7/10 | Speed to market, edge focus |
| **Hailo Price War** | 90% | Medium | 7/10 | Cost leadership position |
| **Memory Price Spike** | 40% | Medium | 6/10 | Long-term contracts, dual-source |
| **Yield Issues** | 50% | High | 7/10 | Design for yield, conservative targets |
| **Team Execution** | 40% | High | 7/10 | Hire experienced leads, advisors |
| **Capital Shortfall** | 70% | High | 8/10 | Realistic capital plan required |

## Risk Heat Map

```
IMPACT
  Critical │    ●Pre-Silicon      │         │    ●Taalas
           │                      │         │
  High     │    ●Yield           │●Memory  │    ●Capital
           │                      │         │
  Medium   │    ●Hailo Price     │         │
           │                      │         │
  Low      │                      │         │
           └──────────────────────┼─────────┼────────────
                  Low        Medium        High
                           PROBABILITY
```

---

# 4. DEAL STRUCTURE RECOMMENDATIONS

## 4.1 Seed Round Structure (Recommended)

| Parameter | Recommendation | Rationale |
|-----------|----------------|-----------|
| **Instrument** | SAFE with MFN and valuation cap | Standard for seed |
| **Amount** | $500K-1.5M total round | Sufficient for MPW validation |
| **Valuation Cap** | $10-15M (not $4M) | Reflects pre-silicon risk |
| **Pro Rata** | Strong pro rata for Series A | Protect upside |
| **Discount** | 20% | Market standard |

## 4.2 Milestone Requirements

| Milestone | Timeline | Failure Consequence |
|-----------|----------|---------------------|
| MPW silicon validated | Month 14 | Automatic conversion at lower cap |
| First customer shipment | Month 18 | No further investment |
| $200K LOV (Letters of Value) | Month 18 | Series A trigger |
| Patent prosecution initiated | Month 6 | Quarterly IP review |

## 4.3 Protective Provisions Required

**Governance:**
1. Board seat or observer (if >$1M invested)
2. Monthly financials, quarterly board meetings
3. Key person insurance on founders
4. IP assignment verification
5. 4-year founder vesting with 1-year cliff
6. Non-compete during employment + 1 year

**Operational:**
1. Any spend >$50K requires board approval
2. Any hire >$100K salary requires investor consent
3. Related party transactions require board approval

## 4.4 Series A Requirements

**Before I would lead Series A:**

| Requirement | Status | Gap |
|-------------|--------|-----|
| Working silicon | ❌ Not achieved | CRITICAL |
| Independent performance benchmarks | ❌ Not achieved | CRITICAL |
| Customer LOIs ($500K+) | ❌ Not achieved | HIGH |
| Patents granted (2-3) | ❌ Only provisional | HIGH |
| VP Sales hired | ❌ Not filled | HIGH |
| Team expansion (2x engineering) | ❌ Not achieved | MEDIUM |
| Clear path to revenue | ❌ Unclear | HIGH |

---

# 5. NOVEL FINANCING STRATEGIES

## 5.1 Strategic Investor Syndicate

**Recommended co-investors:**

| Investor Type | Target | Strategic Value |
|---------------|--------|-----------------|
| Corporate VC (Qualcomm Ventures) | $200-500K | Product roadmap alignment, potential acquirer |
| Strategic (Arm, TSMC) | $200-500K | Manufacturing relationships, IP |
| Deep Tech Fund (DCVC, Playground) | $300-500K | Technical validation |
| Angel (Semiconductor veteran) | $100-200K | Operating experience |

## 5.2 Government Grant Layering

**Applicable programs:**

| Program | Amount | Requirements |
|---------|--------|--------------|
| NSF SBIR Phase I | $275K | US-based, technical innovation |
| NSF SBIR Phase II | $1M | Phase I success |
| DARPA | $1-5M | Defense applications |
| CHIPS Act R&D | $5-50M | Manufacturing focus |

**Recommendation:** Pursue SBIR Phase I immediately to extend runway

## 5.3 Customer Prepayment Program

**Structure:**
- Early adopter program: $500 deposit for first 1,000 units
- Enterprise LOI: $10K non-refundable deposit toward first order
- Developer kit pre-orders: $99 for early access

**Potential raise:** $200-500K in non-dilutive capital

## 5.4 IP Monetization Bridge

**If cash crunch occurs:**
- License mask-locked architecture to datacenter AI companies (non-competing market)
- Potential: $1-3M upfront + 1-3% royalty
- Risk: Reduces exit valuation for strategic acquirer

---

# 6. GO/NO-GO DECISION FRAMEWORK

## 6.1 Decision Matrix

| Factor | Weight | Score (1-10) | Weighted |
|--------|--------|--------------|----------|
| Technology differentiation | 20% | 8 | 1.6 |
| Market opportunity size | 15% | 6 | 0.9 |
| Competitive positioning | 15% | 5 | 0.75 |
| Team execution capability | 15% | 5 | 0.75 |
| Capital efficiency | 10% | 4 | 0.4 |
| Exit clarity | 10% | 6 | 0.6 |
| Risk-adjusted return | 15% | 5 | 0.75 |
| **TOTAL** | **100%** | | **5.75** |

## 6.2 Decision Thresholds

| Score | Decision | Action |
|-------|----------|--------|
| 8.0+ | Strong Invest | Lead round, board seat |
| 7.0-7.9 | Invest | Participate, observer rights |
| 6.0-6.9 | Conditional Pass | Seed only, milestone-based |
| 5.0-5.9 | Pass with Follow | Monitor, revisit after milestones |
| <5.0 | Hard Pass | Decline |

**Current Score: 5.75 → CONDITIONAL PASS - SEED STAGE ONLY**

## 6.3 What Would Change My Decision

### To INVEST (7.0+):
- MPW silicon validated with performance targets met
- $500K+ in customer LOIs
- VP Sales hired with enterprise track record
- Realistic capital plan ($25-50M to scale)
- Hybrid architecture addressing model obsolescence

### To HARD PASS (<5.0):
- MPW silicon fails to meet performance targets
- Taalas announces edge-focused product
- Hailo announces sub-$50 product line
- Core team departure
- Patent rejection / prior art issues

---

# 7. MILESTONE REQUIREMENTS FOR FUNDING

## 7.1 Seed → Series A Bridge

| Milestone | Timeline | Success Criteria | Funding Trigger |
|-----------|----------|------------------|-----------------|
| FPGA prototype | Month 6 | 80+ tok/s on target model | $500K seed tranche |
| MPW tape-out | Month 10 | Design complete, sent to foundry | $500K bridge |
| First silicon | Month 14 | Functional, 80%+ of performance targets | Series A decision |
| Customer LOIs | Month 14 | $200K+ in non-binding commitments | Series A trigger |
| Patent filing | Month 6 | Utility patents filed (not just provisional) | IP validation |

## 7.2 Series A → Series B Bridge

| Milestone | Timeline | Success Criteria |
|-----------|----------|------------------|
| Production silicon | Month 24 | Yield >70%, performance validated |
| Revenue traction | Month 24 | $1M ARR |
| Customer diversity | Month 24 | >50 customers, no >20% concentration |
| Team scale | Month 24 | 15+ employees |
| Gross margin | Month 24 | >65% at production volumes |

---

# 8. RED FLAGS REQUIRING IMMEDIATE ATTENTION

## 8.1 Critical Red Flags (Must Resolve)

### 1. Pre-Silicon Status
- **No production silicon validated**
- FPGA prototype is promising but insufficient for Series A
- **Resolution required:** MPW silicon success before Series A

### 2. Model Lock-In Contradiction
- Mask-locked silicon incompatible with "model cartridges"
- Inventory obsolescence risk ignored in materials
- **Resolution required:** Clear product architecture explanation

### 3. Patent Position Weak
- Only provisional patents filed
- Taalas prior art could challenge novelty
- **Resolution required:** Utility patent filings + prior art clearance opinion

### 4. Competitive Underestimation
- Hailo response not adequately planned
- Taalas threat minimized
- **Resolution required:** Detailed competitive response playbook

## 8.2 Major Red Flags (Should Resolve)

### 5. Unrealistic Financial Projections
- 12x Y1→Y2 growth not credible
- $28K/month burn rate unrealistically low
- **Resolution required:** Revised financial model with sensitivity analysis

### 6. Team Gaps
- No VP Sales identified
- No CFO for semiconductor company
- **Resolution required:** Key hire plan with timelines

### 7. Supply Chain Risk
- TSMC concentration not adequately addressed
- Memory price volatility ignored
- **Resolution required:** Dual-source strategy + hedging plan

### 8. Capital Requirements
- $500K is insufficient for semiconductor startup
- Likely need $25-40M total to meaningful revenue
- **Resolution required:** Realistic capital plan with milestones

---

# 9. COMPARABLE TRANSACTION ANALYSIS

## 9.1 Relevant Exits

| Company | Exit Value | Revenue Multiple | Lesson |
|---------|------------|------------------|--------|
| **Graphcore** | $500M (distressed) | N/A | $700M+ raised, struggled with adoption |
| **Habana Labs** | $2B | 25x revenue | Acquired by Intel, strong IP position |
| **Xnor.ai** | $200M | N/A (pre-revenue) | Acquihire by Apple, edge AI focus |
| **DarwinAI** | $100M | N/A | Apple acquihire, edge optimization |
| **Groq** | $20B (licensing) | N/A | NVIDIA licensing deal, not acquisition |

## 9.2 Current Private Valuations

| Company | Stage | Revenue | Valuation | Multiple |
|---------|-------|---------|-----------|----------|
| Hailo | Growth | ~$60M | $1.2B | 20x |
| Etched | Pre-revenue | $0 | $5B | N/A |
| Axelera | Series B | ~$10M | $400M | 40x |

## 9.3 SuperInstance Positioning

```
STATED ASK: $500K at $4M cap
REALISTIC SEED: $1-2M at $10-15M cap
SERIES A TARGET: $5-10M at $30-50M cap (requires working silicon + LOIs)
```

---

# 10. FINAL INVESTMENT DECISION

## Investment Decision: **CONDITIONAL PASS - SEED STAGE ONLY**

### If Investing:
```
Stage: Seed (not Series A)
Amount: $500K participation in $1.5M round
Instrument: SAFE with $10-12M cap, MFN
Conditions: Board observer, milestone-based follow-on
```

### If Passing:
```
Primary Reason: Pre-silicon risk too high for Series A
Secondary Reason: Competitive response underestimated
Revisit Trigger: After MPW silicon validation + customer LOIs
```

## What Would Make Me Write a Check

### Must Haves (Non-Negotiable):
| Requirement | Status |
|-------------|--------|
| Working FPGA prototype | ✅ Achieved |
| MPW silicon validated | ❌ Not achieved |
| Independent performance benchmarks | ❌ Not achieved |
| Customer LOIs ($200K+) | ❌ Not achieved |
| Patent prosecution initiated | ❌ Only provisional filed |

### Nice to Haves:
| Requirement | Value |
|-------------|-------|
| Named enterprise customer in pilot | Validates market |
| Hailo competitive benchmark comparison | Proves differentiation |
| Dual-source foundry strategy | Reduces supply chain risk |
| VP Sales hired | Execution capability |
| Realistic financial model | Credibility |

---

# 11. SUMMARY STATEMENT

SuperInstance.AI represents an **interesting but high-risk** investment opportunity in edge AI inference. The mask-locked architecture is technically innovative and addresses a genuine market gap for sub-$100 LLM inference. However, the company is **pre-silicon, pre-revenue, and faces formidable competitive threats** from well-funded incumbents.

**Key Concerns:**
1. Pre-silicon execution risk is too high for Series A commitment
2. Model lock-in creates inventory obsolescence risk not adequately addressed
3. Taalas ($169M raised) represents existential competitive threat
4. Capital requirements likely $25-50M total, not $5.5M stated

**Key Opportunities:**
1. Genuine technical innovation (mask-locked + ternary + iFairy)
2. Clear market gap (no sub-$50 LLM inference solution)
3. Attractive unit economics if yield targets achieved
4. Multiple exit paths (Qualcomm, Apple, MediaTek, NVIDIA)

**I would consider a seed-stage investment at appropriate terms ($10-15M cap), but would not recommend Series A commitment until silicon validation and customer traction are demonstrated.**

---

**Document Prepared By:** VC Partner (Deep Tech/Semiconductor Focus)  
**Date:** March 2026  
**Classification:** Confidential - Due Diligence  
**Next Review:** Post-MPW Silicon Results  

---

*End of VC Partner Investment Review*
