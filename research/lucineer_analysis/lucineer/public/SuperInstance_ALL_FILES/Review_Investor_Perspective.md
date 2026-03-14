# SuperInstance.AI: Venture Capital Investor Review
## Partner-Level Investment Analysis | March 2026

**Reviewer Profile:** Partner at Tier-1 VC Firm (Sequoia/a16z/Accel equivalent)  
**Investment Focus:** Deep Tech & Semiconductors  
**Track Record:** 3 semiconductor investments (2 exits, 1 unicorn), 500+ deals reviewed yearly  
**Document Classification:** Confidential Due Diligence  

---

# EXECUTIVE SUMMARY

## Investment Attractiveness Score: 5.5/10

**Recommendation:** **CONDITIONAL PASS** - Interesting technology thesis, but significant execution and market risks require substantial de-risking before Series A commitment. Would consider seed-stage investment with heavy milestone requirements.

### Score Breakdown:
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

## Investment Thesis Summary (2-3 Sentences)

SuperInstance.AI proposes a novel mask-locked inference architecture that genuinely addresses the memory bandwidth bottleneck in edge AI, achieving theoretical 4-8x efficiency gains. However, the company is pre-silicon, pre-revenue, and faces formidable competitive threats from well-funded incumbents (Hailo $400M+, Taalas $219M). The $35 price point is compelling but requires flawless execution across silicon tape-out, manufacturing scale-up, and GTM—each representing a potential company-killing risk.

---

# 1. CRITICAL INVESTMENT RISKS FOUND

## 1.1 Technology Risks (HIGH)

### Silicon Execution Risk
- **No silicon validated yet** - FPGA prototype at 94 tok/s is promising, but MPW to production silicon has 30-50% failure rate in semiconductor startups
- **28nm process constraints** - Using older process to reduce costs, but limits performance ceiling vs. competitors at 7nm/5nm
- **Mask-locked architecture = single model per chip** - Creates inventory obsolescence risk if model versions change rapidly
- **Yield uncertainty** - First silicon often 40-60% yield; margins depend on 82% yield assumption

### Critical Gap:
```
STATED: "25-35 tokens/second on 2B parameter models"
REALITY: Demonstrated on FPGA (94 tok/s on 0.73B model), not full ASIC
RISK: MPW silicon may not achieve stated performance targets
```

## 1.2 Market Risks (HIGH)

### TAM/SAM/SOM Concerns
- **TAM claims ($76.8B by 2029) are industry-wide** - Actual addressable market for sub-$100 LLM inference is a fraction
- **SAM definition includes "LLM-capable, <10W"** - But this ignores that most LLM inference happens on GPUs in data centers
- **SOM assumes 1.3% market share in Y5** - Aggressive for a hardware startup with no brand recognition

### Market Reality Check:
```
STATED SAM: $4.2B (2024) → $18.5B (2029)
MY ESTIMATE: $800M-1.2B for <$100 edge inference segment
GROWTH DRIVERS: Real (privacy, edge computing) but slower than stated
```

## 1.3 Competitive Risks (CRITICAL)

### Incumbent Response Scenarios
| Competitor | Funding | Response Likelihood | Timeline | Impact |
|------------|---------|---------------------|----------|--------|
| Hailo | $400M+ | 90% (already shipping) | Immediate | Price war |
| Taalas | $219M | 25% (different market now) | 18-24 months | Direct competition |
| NVIDIA Jetson | Infinite | 60% (protect edge share) | 6-12 months | Feature/performance war |
| Samsung | $300B market cap | 35% | 18-24 months | Existential threat |

### Key Competitive Vulnerabilities:
1. **Zero ecosystem lock-in** - New platform, no CUDA equivalent
2. **Single-model limitation** - Hailo offers reconfigurable inference; SuperInstance is fixed
3. **No software moat** - Hardware advantage can be copied; Taalas has similar architecture
4. **Patent position weak** - Only provisional patents filed, not granted

## 1.4 Supply Chain Risks (HIGH)

### Memory Crisis Exposure
- **LPDDR4 pricing up 100-140%** in Q1 2026 - Direct threat to margin assumptions
- **Single-source foundry (TSMC)** - 92% concentration in Taiwan creates existential geopolitical risk
- **No hedging strategy detailed** - Memory price volatility could eliminate margins

### Supply Chain Risk Score:
```
Wafer Supply:     CRITICAL (Taiwan concentration)
Memory Supply:    HIGH (Price volatility, allocation)
Packaging:        MEDIUM (OSAT capacity available)
Substrates:       HIGH (Taiwan concentration again)
OVERALL:          HIGH - Requires 8-12% COGS risk budget
```

## 1.5 Team Risks (MEDIUM-HIGH)

### Solo Founder Pattern (if applicable)
- **Solo founder semiconductor exits are rare** - 20-30% valuation discount vs. team-founded competitors
- **Team depth unclear** - CTO/VP Engineering credentials strong but execution track record on their own?

### Team Gap Analysis:
| Role | Current | Gap | Risk |
|------|---------|-----|------|
| CEO | Silicon experience (Apple, Qualcomm) | None | LOW |
| CTO | Deep architecture expertise | None | LOW |
| VP Eng | Manufacturing experience | None | LOW |
| VP Sales | **NOT FILLED** | CRITICAL | HIGH |
| CFO | **NOT FILLED** | HIGH | MEDIUM |

## 1.6 Capital Structure Risks (HIGH)

### Funding Requirements Reality
```
STATED: $500K seed + $8M Series A
REALITY: Semiconductor startups typically need $15-40M to reach volume production
MY ESTIMATE: $25-50M total capital required to meaningful revenue
```

### Capital Efficiency Concerns:
- **Tape-out costs alone**: $2-5M for MPW, $10-30M for production mask set
- **Working capital**: 6-12 months inventory at scale
- **Burn rate**: Stated $28K/month is unrealistically low for semiconductor company

---

# 2. WHAT'S ATTRACTIVE FROM INVESTOR VIEW

## 2.1 Genuine Technical Innovation (8/10)

### The Mask-Locked Architecture is Novel
- **Memory bottleneck elimination** is real - DRAM access is the #1 power consumer in edge inference
- **Ternary weight encoding** validated by Microsoft BitNet research
- **iFairy complex arithmetic** enables multiplication-free inference (10x power reduction)
- **Kirchhoff's law computation** - Analog-inspired approach is innovative

### Scientific Validation:
```
BitNet b1.58: Microsoft Research validated, 16,010+ HuggingFace downloads
TeLLMe FPGA: Published in arXiv:2510.15926, peer-reviewed
iFairy: Peking University research, arXiv:2508.05571
```

## 2.2 Clear Market Gap (7/10)

### Underserved Segment
- **No sub-$50 LLM inference solution** exists - This is genuinely underserved
- **Google Coral EOL** creates 500K+ device replacement opportunity
- **Raspberry Pi ecosystem** is massive (40M+ devices) and lacks LLM capability

### Customer Pain Point is Real:
```
"73% of edge AI projects fail at prototype stage"
"$127,000 average cost of failed deployment"
"340 hours wasted on SDK integration per project"
```

## 2.3 Attractive Unit Economics Potential (7/10)

### Margin Structure
| Product | ASP | COGS | Margin | Assessment |
|---------|-----|------|--------|------------|
| Nano ($35) | $35 | $14.50 | 59% | Achievable at scale |
| Standard ($79) | $79 | $21.30 | 73% | Requires yield >80% |
| Pro ($149) | $149 | $35.00 | 77% | Enterprise focused |

### LTV:CAC Analysis:
```
Hobbyist LTV: $205, CAC: $35, Ratio: 5.9:1 ✓
Professional LTV: $965, CAC: $85, Ratio: 11.4:1 ✓
Enterprise LTV: $19,900, CAC: $1,850, Ratio: 10.8:1 ✓
Blended Ratio: 7.6:1 ✓
```

## 2.4 Strong Advisory Network (6/10)

### Notable Advisors:
- Stanford EE Professor (technical validation)
- Former NVIDIA VP Edge Computing (market access)
- Y Combinator Partner (fundraising support)
- Former TSMC VP Manufacturing (supply chain)

## 2.5 Exit Optionality (6/10)

### Multiple Exit Paths:
| Acquirer | Likelihood | Valuation Range | Timeline |
|----------|------------|-----------------|----------|
| Qualcomm | 50-60% | $200-500M | Post-revenue |
| Apple | 30-40% | $80-150M | Team/IP value |
| MediaTek | 35-45% | $100-250M | Working silicon |
| NVIDIA | 15-25% | $150-300M | Licensing model |

### IP Licensing Backup:
- ARM-style licensing model possible
- 1-3% royalty on chip ASP
- Alternative if hardware business struggles

---

# 3. WHAT'S CONCERNING FROM INVESTOR VIEW

## 3.1 Pre-Revenue Hardware Startup (CRITICAL)

### Revenue Timeline:
```
Y1: $240K (essentially pre-revenue)
Y2: $2.9M (requires everything to go right)
Y3: $11.2M (assumes 3.9x growth)
Y5: $70M (assumes 291x growth from Y1)
```

### Reality Check:
- **Hardware startups rarely hit Y1 projections** - 50-70% miss rate
- **Semiconductor startups often 3-4 years to meaningful revenue**
- **$70M Y5 assumes category creation** - Very risky bet

## 3.2 Competitive Response Underestimated (HIGH)

### Hailo Specifically:
- **Already shipping with Raspberry Pi partnership** - Installed base advantage
- **$400M+ funding** - Can out-spend SuperInstance 10x
- **Price war scenario**: Hailo could drop prices 40% and still be profitable

### Taalas Threat:
- **$169M raised Feb 2026** - 10x SuperInstance's ask
- **Same mask-locked architecture** - Direct technology competitor
- **Currently datacenter-focused** - But could pivot to edge in 18-24 months

## 3.3 Patent Position Weak (HIGH)

### Current Status:
```
FILED: Provisional patents (Feb 2026)
GRANTED: ZERO
PROSECUTION TIMELINE: 2-3 years to grant
PRIOR ART RISK: Taalas filed similar patents in 2024-2025
```

### Risk Assessment:
- **12-18 month technology moat** - Can be copied
- **Patent moat uncertain** - Depends on prosecution success
- **No defensive patent portfolio** - Vulnerable to IP litigation

## 3.4 Model Lock-In Creates Inventory Risk (MEDIUM-HIGH)

### The Fundamental Problem:
```
Each chip = One model baked into silicon
Model versions change every 3-6 months
Inventory obsolescence risk: HIGH
```

### Scenarios:
1. **Llama-4 releases** - SuperInstance Llama-3 chips lose value
2. **Quantization improves** - Fixed INT4 chips become obsolete
3. **New architecture emerges** - Transformer replacement

### Mitigation Unclear:
- Document mentions "model cartridges" but how does this work with mask-locked silicon?
- Appears to be a fundamental contradiction in the business model

## 3.5 GTM Strategy Underdeveloped (MEDIUM)

### Channel Assumptions:
| Partner | Timeline | Volume Assumption | Risk |
|---------|----------|-------------------|------|
| Digi-Key | Month 18 | 2,000 units Y1 | Medium - requires proven product |
| Mouser | Month 20 | 1,500 units Y1 | Medium |
| SparkFun | Month 15 | 1,000 units Y1 | High - maker channel unpredictable |

### Missing Elements:
- **No enterprise sales strategy** until Month 37
- **No OEM design-in pipeline** detailed
- **No reference customers** named

## 3.6 Financial Projections Aggressive (HIGH)

### Growth Assumptions:
```
Y1→Y2: 12x growth (2,900%)
Y2→Y3: 3.9x growth (290%)
Y3→Y4: 2.6x growth (160%)
Y4→Y5: 2.4x growth (140%)
```

### Reality Check:
- **Hardware growth rarely exceeds 2-3x annually** at scale
- **Semiconductor startups hit 5x in early years, not 12x**
- **Market share assumptions (1.3% in Y5)** require category leadership

---

# 4. DUE DILIGENCE QUESTIONS (20+ Tough Questions)

## Technology & Engineering

1. **What is your detailed MPW-to-production timeline, and what are the key technical milestones at each stage?**

2. **What is your expected first silicon yield, and what is your contingency if yield is below 50%?**

3. **How do you handle model version changes when weights are mask-locked into silicon? Specifically, if Llama-4 is released 6 months after you ship Llama-3 chips, what happens to your inventory?**

4. **Your FPGA prototype shows 94 tok/s on 0.73B model. What is your confidence level for achieving 80-150 tok/s on 3B model in production silicon? Show your PPA (Power-Performance-Area) analysis.**

5. **What is your total development cost to achieve production-ready silicon, including NRE, mask costs, and IP licensing? Be specific.**

6. **How does your iFairy complex weight architecture handle the output layer, which typically requires full-precision computation?**

## Market & Competition

7. **Hailo has $400M+ in funding, Raspberry Pi partnership, and shipping products. Why will developers choose SuperInstance over Hailo-10H? Be specific about your 3-5x performance claim validation.**

8. **What is your detailed competitive response plan if Hailo drops prices by 40%? Show your margin sensitivity analysis.**

9. **Taalas raised $169M in Feb 2026 for similar mask-locked architecture. How do you differentiate? What is your defense if they enter the edge market?**

10. **Your TAM/SAM/SOM analysis shows $76.8B TAM. What percentage of this is actually addressable for sub-$100 edge inference? Show your bottom-up calculation.**

11. **Google Coral has 500K+ devices deployed and is EOL. What is your specific capture strategy for this installed base? What is your conversion rate assumption?**

12. **What are the top 3 enterprise accounts in your pipeline? What stage are they at (evaluation, POC, LOI, contract)?**

## Team & Execution

13. **Who is your VP of Sales? What is your enterprise go-to-market team plan?**

14. **Your burn rate is stated at $28K/month. This seems unrealistically low for a semiconductor company. Provide a detailed 18-month operating budget.**

15. **What is your hiring plan for the next 18 months? What key roles are unfilled?**

16. **Who owns the customer relationships at your target accounts? What is your track record selling into the edge AI market?**

## Financial & Unit Economics

17. **Your COGS assumes 82% yield. What is your break-even yield? What happens to margins at 60% yield?**

18. **LPDDR4 pricing is up 100-140% in 2026. How does this impact your $21.30 COGS for the Standard product? Show your sensitivity analysis.**

19. **What is your total capital requirement to reach $10M ARR? Include working capital, inventory, and R&D.**

20. **You project 12x revenue growth from Y1 to Y2 ($240K to $2.9M). What specific customer contracts or LOIs support this?**

## Intellectual Property

21. **You have filed provisional patents. What is your prior art search results? Specifically, how do you distinguish from Taalas patents filed in 2024-2025?**

22. **What is your IP budget for patent prosecution over the next 3 years? Are you filing internationally?**

## Exit & Valuation

23. **What are the specific milestones that would trigger M&A interest from Qualcomm or Apple? What metrics do they use to evaluate acquisitions?**

24. **If you fail to achieve product-market fit, what is your IP monetization strategy? What is the value of your patent portfolio in a distressed sale?**

25. **Your ask is $500K at $4M cap. What is your path to Series A? What are the specific milestones required?**

---

# 5. SUGGESTED IMPROVEMENTS TO PITCH/INVESTMENT MATERIALS

## 5.1 Critical Additions Required

### Technical Documentation
1. **Add silicon PPA (Power-Performance-Area) analysis** - Show projected vs. demonstrated metrics
2. **Include first silicon failure contingency** - What happens if MPW fails?
3. **Detail model update strategy** - How do you handle model version changes?
4. **Add competitive benchmark methodology** - Independent third-party validation

### Market Analysis
1. **Bottom-up TAM calculation** - Developer counts × conversion × ASP
2. **Named customer pipeline** - Specific accounts, not generic segments
3. **Competitive response scenarios** - Detailed Hailo/NVIDIA response playbooks
4. **Pricing sensitivity analysis** - Impact of competitor price drops

### Financial Projections
1. **Realistic burn rate** - Semiconductor startup burn is typically $200-500K/month
2. **Working capital requirements** - Inventory, receivables, prepayments
3. **Sensitivity analysis** - What if yield is 50%? What if memory prices double?
4. **Capital efficiency metrics** - Revenue per dollar invested

## 5.2 Pitch Deck Improvements

### Current Weaknesses:
- **No competitive response scenario** - Ignores incumbent retaliation
- **Unrealistic growth projections** - 12x Y1→Y2 growth is not credible
- **No named customers** - Generic segments, not specific accounts
- **Patent position overstated** - Provisional patents ≠ granted patents

### Suggested Additions:
1. **Competitive moat slide** - Duration, defensibility, response scenarios
2. **Risk mitigation slide** - Key risks and specific mitigation strategies
3. **Realistic financials slide** - Conservative, base, aggressive scenarios
4. **Customer pipeline slide** - Named accounts with stage indicators

## 5.3 Business Model Refinements

### Current Gap:
The "model cartridge" concept contradicts the mask-locked architecture. If weights are in silicon, how do cartridges work?

### Suggested Resolution:
1. **Clarify product architecture** - Is it one model per chip, or modular?
2. **Explain inventory strategy** - How do you avoid obsolescence?
3. **Consider licensing model** - Hardware + annual model update subscription?

---

# 6. COMPARABLE COMPANY ANALYSIS GAPS

## 6.1 Missing Comparables

### Should Have Analyzed:

| Company | Relevance | Lesson |
|---------|-----------|--------|
| **Graphcore** | Failed AI chip startup | $500M distressed sale after $700M+ raised |
| **Groq** | Inference-focused | $20B NVIDIA licensing deal - BUT required massive scale |
| **Mythic** | Analog AI inference | Struggled with yield, pivoted multiple times |
| **SambaNova** | Dataflow architecture | $5B valuation but struggling with adoption |
| **Etched** | Transformer-specific ASIC | $5B valuation pre-revenue - comparable valuation benchmark |

## 6.2 Valuation Benchmarking

### Current Comparable Valuations:
| Company | Stage | Revenue | Valuation | Multiple |
|---------|-------|---------|-----------|----------|
| Hailo | Growth | ~$60M | $1.2B | 20x |
| Etched | Pre-revenue | $0 | $5B | N/A |
| Axelera | Series B | ~$10M | $400M | 40x |
| Quadric | Series B | ~$5M | $200M | 40x |

### SuperInstance Positioning:
```
STATED ASK: $500K at $4M cap
REALISTIC SEED: $1-2M at $8-15M cap
SERIES A TARGET: $5-10M at $30-50M cap (requires working silicon + LOIs)
```

## 6.3 Missing Market Data

### Should Include:
1. **AI chip startup failure rate** - Estimated 70-80% fail to reach Series B
2. **Average time to revenue** - 3-4 years for semiconductor startups
3. **Capital intensity metrics** - $15-40M to reach $10M ARR
4. **Exit multiples by stage** - Pre-revenue vs. revenue-generating

---

# 7. DEAL STRUCTURE CONSIDERATIONS

## 7.1 If I Were to Invest

### Seed Round Structure (Recommended):
```
Instrument: SAFE with MFN and valuation cap
Amount: $500K (part of $1-1.5M round)
Valuation Cap: $8-12M (not $4M)
Pro Rata: Strong pro rata rights for Series A
Milestones: Tied to MPW silicon success + customer LOIs
```

### Milestone Requirements:
| Milestone | Timeline | Failure Consequence |
|-----------|----------|---------------------|
| MPW silicon validated | Month 14 | Automatic conversion to equity at lower cap |
| First customer shipment | Month 18 | No further investment |
| $200K LOV | Month 18 | Series A trigger |
| Patent prosecution | Ongoing | Quarterly IP review |

## 7.2 Terms I Would Require

### Protective Provisions:
1. **Board seat** - Observer at minimum, full seat if >$1M invested
2. **Information rights** - Monthly financials, quarterly board meetings
3. **Key person insurance** - On founders, company-paid
4. **IP assignment verification** - All IP assigned to company
5. **Founder vesting** - 4-year vesting, 1-year cliff
6. **Non-compete** - Founders restricted during employment + 1 year

### Governance:
1. **Budget approval** - Any spend >$50K requires board approval
2. **Hiring approval** - Any hire >$100K salary requires investor consent
3. **Related party transactions** - Any related party deal requires board approval

## 7.3 Series A Requirements

### Before I Would Lead Series A:
1. **Working silicon** - Production-quality silicon validated
2. **Performance benchmarks** - Independent third-party validation
3. **Customer LOIs** - $500K+ in non-binding LOIs
4. **Patents granted** - At least 2-3 patents issued (not just filed)
5. **Team expansion** - VP Sales hired, engineering team doubled
6. **Clear path to revenue** - Specific customer contracts, not just LOIs

---

# 8. RED FLAGS THAT NEED ADDRESSING

## 8.1 Critical Red Flags (Must Resolve)

### 1. Pre-Silicon Status
- **No production silicon validated**
- **FPGA prototype is not sufficient proof of production capability**
- **Resolution required:** MPW silicon success before Series A

### 2. Patent Position
- **Only provisional patents filed**
- **Taalas prior art could challenge novelty**
- **Resolution required:** Utility patent filings + prior art clearance opinion

### 3. Competitive Underestimation
- **Hailo response not adequately planned**
- **Taalas threat minimized**
- **Resolution required:** Detailed competitive response playbook

### 4. Model Lock-In Contradiction
- **Mask-locked silicon incompatible with "model cartridges"**
- **Inventory obsolescence risk ignored**
- **Resolution required:** Clear product architecture explanation

## 8.2 Major Red Flags (Should Resolve)

### 5. Unrealistic Financial Projections
- **12x Y1→Y2 growth not credible**
- **$28K/month burn rate unrealistically low**
- **Resolution required:** Revised financial model with sensitivity analysis

### 6. Team Gaps
- **No VP Sales identified**
- **No CFO for semiconductor company**
- **Resolution required:** Key hire plan with timelines

### 7. Supply Chain Risk
- **TSMC concentration not adequately addressed**
- **Memory price volatility ignored**
- **Resolution required:** Dual-source strategy + hedging plan

### 8. Capital Requirements
- **$500K is insufficient for semiconductor startup**
- **Likely need $15-40M total to meaningful revenue**
- **Resolution required:** Realistic capital plan with milestones

## 8.3 Moderate Red Flags (Monitor)

### 9. Market Size Claims
- **TAM/SAM/SOM definitions overly optimistic**
- **Bottom-up validation weak**
- **Monitor:** Customer pipeline development

### 10. Ecosystem Building
- **No CUDA-equivalent lock-in strategy**
- **Developer community building is slow**
- **Monitor:** Community growth metrics

---

# 9. FINAL INVESTMENT DECISION

## Decision Matrix

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

## Investment Decision: **CONDITIONAL PASS**

### If Investing:
```
Stage: Seed (not Series A)
Amount: $500K participation in $1.5M round
Instrument: SAFE with $10M cap, MFN
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
1. ✅ **Working FPGA prototype** (achieved)
2. ❌ **MPW silicon validated** (not achieved)
3. ❌ **Independent performance benchmarks** (not achieved)
4. ❌ **Customer LOIs ($200K+)** (not achieved)
5. ❌ **Patent prosecution initiated** (only provisional filed)

### Nice to Haves:
1. Named enterprise customer in pilot
2. Hailo competitive benchmark comparison
3. Dual-source foundry strategy
4. VP Sales hired
5. Realistic financial model

---

# 10. APPENDIX: KEY METRICS TO TRACK

## Monthly Dashboard Required:
| Metric | Target | Frequency |
|--------|--------|-----------|
| MPW tape-out progress | On schedule | Monthly |
| FPGA prototype performance | 80+ tok/s | Monthly |
| Customer LOIs | $200K by M18 | Monthly |
| Patent prosecution status | Utility filed by M6 | Monthly |
| Burn rate | <$50K/month | Monthly |
| Team hiring | 2 key hires by M12 | Monthly |

## Quarterly Business Review:
1. Technical milestone review
2. Customer pipeline review
3. Competitive landscape update
4. Financial model update
5. Supply chain risk assessment

---

**Document Prepared By:** VC Partner (Deep Tech/Semiconductor Focus)  
**Date:** March 2026  
**Classification:** Confidential - Due Diligence  
**Next Review:** Post-MPW Silicon Results  

---

# SUMMARY STATEMENT

SuperInstance.AI represents an interesting but high-risk investment opportunity in edge AI inference. The mask-locked architecture is technically innovative and addresses a genuine market gap for sub-$100 LLM inference. However, the company is pre-silicon, pre-revenue, and faces formidable competitive threats from well-funded incumbents.

**I would consider a seed-stage investment at appropriate terms, but would not recommend Series A commitment until silicon validation and customer traction are demonstrated.**

The key risks—silicon execution, competitive response, and model obsolescence—are not adequately mitigated in the current pitch materials. With improved documentation, realistic financial projections, and clearer competitive strategy, this could become an attractive Series A opportunity in 12-18 months.

**Investment Thesis:** High-risk, high-reward bet on novel edge inference architecture. Appropriate for deep tech portfolio allocation but not as core position.

---

*End of Investor Review*
