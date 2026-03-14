# SuperInstance.AI Financial Consistency Audit Report
## Prepared by Jennifer Walsh, Finance Lead
**Date**: March 2026
**Classification**: Confidential - Internal Use Only

---

# Executive Summary

This audit reviewed 5 core documents for financial and operational consistency:
- Technical Specification Document
- Business Model & Financial Projections
- Executive Summary
- Competitive Analysis
- GTM & Operations Plan

**Overall Assessment**: **MODERATE RISK** - Several material discrepancies require immediate correction before investor presentations.

---

# Part I: Consistency Matrix

## 1.1 Performance Claims (Tok/s, Power)

| Metric | Tech Spec | Exec Summary | Competitive | GTM Plan | Status |
|--------|-----------|--------------|-------------|----------|--------|
| **Throughput (tok/s)** | 80-150 | 80-150 | 80-150 | 80-150 | ✅ CONSISTENT |
| **Power (W)** | 2-3W | 2-3W | 2-3W | 2-3W | ✅ CONSISTENT |
| **Tokens/Watt** | 50 (Consumer) / 37.5 (Pro) | 27-50 | 27-50 | 27-50 | ✅ CONSISTENT |
| **First Token Latency** | <50ms | - | - | - | ⚠️ NOT MENTIONED ELSEWHERE |

## 1.2 Pricing & COGS

| Metric | Tech Spec | Business Model | Exec Summary | GTM Plan | Status |
|--------|-----------|----------------|--------------|----------|--------|
| **Price Range** | $35-60 | $35-149 (4 tiers) | $35-60 | $35-69 (3 tiers) | ❌ DISCREPANCY |
| **COGS (base)** | - | $7-45 (tiered) | $5-8 | $7 | ⚠️ PARTIAL MATCH |
| **COGS (with memory)** | - | $15-45 | $15-19 | $15-19 | ✅ CONSISTENT |
| **Gross Margin** | - | 65-80% | 60-80% | 70-80% | ⚠️ MINOR VARIANCE |

### Detailed Pricing Discrepancy

| Product Tier | Business Model | GTM Plan | Difference |
|--------------|----------------|----------|------------|
| Entry | $35 (Nano) | $35 (SI-100) | ✅ MATCH |
| Mid | $49 (Micro) | $49 (SI-200) | ✅ MATCH |
| Standard | $79 (Standard) | $69 (SI-300) | ❌ $10 DIFF |
| Pro | $149 (Pro) | NOT LISTED | ❌ MISSING |

## 1.3 Revenue Projections

| Metric | Business Model | Exec Summary | GTM Plan | Status |
|--------|----------------|--------------|----------|--------|
| **Year 1 Revenue** | $240K | $175K | - | ⚠️ VARIANCE |
| **Year 2 Revenue** | $2.875M | $1.75M | $3.5M (Phase 1) | ❌ 2x VARIANCE |
| **Year 3 Revenue** | $11.2M | $7M | $35M (Phase 2) | ❌ 3-5x VARIANCE |
| **Year 5 Revenue** | $70M | $35M | $350M (Phase 3) | ❌ 10x VARIANCE |

### Critical Revenue Discrepancy Analysis

| Year | Business Model | Exec Summary | GTM Plan | Recommendation |
|------|----------------|--------------|----------|----------------|
| Y1 | $240K | $175K | - | **Use Business Model ($240K)** |
| Y2 | $2.875M | $1.75M | $3.5M | **ALIGN TO: $2.875M** |
| Y3 | $11.2M | $7M | $35M | **ALIGN TO: $11.2M** |
| Y5 | $70M | $35M | $350M | **ALIGN TO: $70M** |

## 1.4 Unit Volume Projections

| Year | Business Model | Exec Summary | Status |
|------|----------------|--------------|--------|
| Year 1 | 4,600 units | 5,000 units | ✅ CLOSE |
| Year 2 | 57,000 units | 50,000 units | ✅ CLOSE |
| Year 3 | 185,000 units | 200,000 units | ✅ CLOSE |
| Year 4 | 330,000 units | 500,000 units | ❌ 1.5x VARIANCE |
| Year 5 | 460,000 units | 1,000,000 units | ❌ 2x VARIANCE |

## 1.5 Market Size (TAM/SAM/SOM)

| Source | 2025 | 2030 | CAGR | Document |
|--------|------|------|------|----------|
| **IDC Edge AI Silicon** | $7.08B | $19.9B | 23% | Competitive Analysis |
| **Gartner Edge AI Chips** | $5.99B | $15.3B | 21% | Competitive Analysis |
| **McKinsey Edge Inference** | $3.67B | $11.54B | 26% | Exec Summary (implied) |
| **No source cited** | $3.67B | $11.54B | - | Executive Summary |

**Issue**: Executive Summary uses McKinsey figures without attribution.

## 1.6 Funding Requirements

| Round | Business Model | Exec Summary | GTM Plan | Status |
|-------|----------------|--------------|----------|--------|
| **Seed** | $500K | $500K | - | ✅ CONSISTENT |
| **Series A** | $3M | $3M | - | ✅ CONSISTENT |
| **Series B** | $10M | - | - | ⚠️ NOT IN EXEC SUMMARY |

## 1.7 Competitive Intelligence

| Metric | Tech Spec | Competitive Analysis | Exec Summary | Status |
|--------|-----------|---------------------|--------------|--------|
| **Taalas Funding** | $169M mentioned | $169M Series A | $219M raised | ❌ $50M DISCREPANCY |
| **Hailo Funding** | $400M+ | $400M+ | - | ✅ CONSISTENT |
| **Jetson Price** | $249 | $199-249 | $250 | ✅ CONSISTENT |
| **Hailo-10H tok/s** | 5-10 | 5-10 | 5-30 | ⚠️ MINOR VARIANCE |

---

# Part II: Material Discrepancies Requiring Correction

## CRITICAL (Must Fix Before Investor Meetings)

### 1. Taalas Funding Amount
| Document | Current Value | Correct Value | Source |
|----------|---------------|---------------|--------|
| Executive Summary | $219M | **$169M** | Reuters Feb 2026 |

**Risk**: If an investor has done their research, this $50M discrepancy will immediately undermine credibility.

**Action Required**: Update Executive Summary line 64 from "$219M" to "$169M"

---

### 2. Year 5 Revenue Projection
| Document | Current Value | Recommended Value |
|----------|---------------|-------------------|
| Executive Summary | $35M | **$70M** |
| GTM Plan Phase 3 | $350M | **$70M** |

**Risk**: The GTM Plan shows $350M for Phase 3 (which aligns with Year 4-5), while the Executive Summary shows only $35M. This 10x variance will confuse investors.

**Action Required**: 
- Update Executive Summary Y5 revenue to $70M (aligned with Business Model)
- Update GTM Plan Phase 3 revenue target to $70M (or clearly state Phase 3 = Year 5)

---

### 3. Year 5 Unit Volume
| Document | Current Value | Recommended Value |
|----------|---------------|-------------------|
| Executive Summary | 1M units | **460K units** |

**Risk**: Inflating unit volumes by 2x while showing lower revenue ($35M vs $70M) implies lower ASP, which contradicts pricing strategy.

**Action Required**: Update Executive Summary Y5 units to 460K

---

## MODERATE (Should Align for Consistency)

### 4. Product Tier Structure

**Business Model** (4 tiers):
- Nano: $35, COGS $7
- Micro: $49, COGS $15
- Standard: $79, COGS $22
- Pro: $149, COGS $45

**GTM Plan** (3 tiers):
- SI-100: $35, COGS $7
- SI-200: $49, COGS $15
- SI-300: $69, COGS $19

**Discrepancy**: Standard tier is $79 vs $69, COGS is $22 vs $19, and Pro tier is missing from GTM.

**Action Required**: Either:
- Option A: Align GTM to Business Model (add Pro tier, change SI-300 to $79)
- Option B: Align Business Model to GTM (remove Pro tier, change Standard to $69)

**Recommendation**: Option A - Business Model is more detailed and financially justified. Update GTM.

---

### 5. Gross Margin Range

| Document | Value |
|----------|-------|
| Business Model | 65-80% |
| Executive Summary | 60-80% |
| GTM Plan | 70-80% |

**Action Required**: Standardize to **65-80%** across all documents (most conservative range).

---

## MINOR (Nice to Align)

### 6. Market Size Attribution
Executive Summary uses McKinsey figures ($3.67B → $11.54B) without citation.

**Action Required**: Add "(McKinsey, 2025)" after market size figures.

---

### 7. Hailo-10H Performance
| Document | Value |
|----------|-------|
| Executive Summary | 5-30 tok/s |
| Tech Spec / Competitive | 5-10 tok/s |

**Action Required**: Correct Executive Summary to "5-10 tok/s"

---

# Part III: Master Numbers Reference Sheet

## The following numbers should be used across ALL documents:

### Product Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Throughput | **80-150 tok/s** | Consumer tier, BitNet 2B model |
| Power Consumption | **2-3W** | USB-powered operation |
| Tokens per Watt | **27-50** | Depending on tier and utilization |
| First Token Latency | **<50ms** | Cold start |
| Inter-Token Latency | **10-15ms** | Steady state |

### Product Pricing (4-Tier Model)

| Tier | SKU | Target Market | COGS | ASP | Margin |
|------|-----|---------------|------|-----|--------|
| Nano | SI-100 | Hobbyist/Education | **$7** | **$35** | **80%** |
| Micro | SI-200 | IoT Integration | **$15** | **$49** | **69%** |
| Standard | SI-300 | Professional Dev | **$22** | **$79** | **72%** |
| Pro | SI-400 | Enterprise Edge | **$45** | **$149** | **70%** |

### Cartridge Pricing

| Type | Model Size | COGS | ASP | Margin |
|------|------------|------|-----|--------|
| Discovery | 1.5B params | **$3** | **$19** | **84%** |
| Standard | 2.4B params | **$5** | **$29** | **83%** |
| Premium | 4B params | **$8** | **$49** | **84%** |
| Enterprise | 8B params | **$15** | **$89** | **83%** |

### Financial Projections (5-Year)

| Year | Units | Revenue | Gross Profit | Operating Income |
|------|-------|---------|--------------|------------------|
| Year 1 | **4,600** | **$240K** | $169K | ($931K) |
| Year 2 | **57,000** | **$2.9M** | $2.2M | ($758K) |
| Year 3 | **185,000** | **$11.2M** | $8.9M | $2.9M |
| Year 4 | **330,000** | **$28.9M** | $23.2M | $12.9M |
| Year 5 | **460,000** | **$70M** | $57M | $41M |

### Funding Requirements

| Round | Amount | Timing | Key Milestone |
|-------|--------|--------|---------------|
| Seed | **$500K** | Month 1-6 | FPGA prototype, 25 tok/s |
| Series A | **$3M** | Month 7-18 | First silicon, 30 LOIs |
| Series B | **$10M** | Month 19-36 | 100K+ units shipped |

### Market Size

| Metric | Value | Source |
|--------|-------|--------|
| TAM (Edge AI Silicon) | **$19.9B (2030)** | IDC, 23% CAGR |
| SAM (LLM-Capable Edge) | **$11.5B (2030)** | McKinsey, 26% CAGR |
| SOM (Sub-$100 LLM Inference) | **$500M-$1B (2030)** | Internal estimate |

### Competitive Intelligence (Verified)

| Competitor | Funding | Price | Power | LLM Performance |
|------------|---------|-------|-------|-----------------|
| Taalas HC1 | **$169M** | API model | 200W+ | 14,000-17,000 tok/s |
| Hailo-10H | **$400M+** | $70-90 | 5W | **5-10 tok/s** |
| Jetson Orin Nano | - | **$199-249** | 10-15W | 20-30 tok/s |
| Google Coral | - | $60-70 | 2W | N/A (vision only) |

### Unit Economics at Scale

| Metric | Value |
|--------|-------|
| Blended COGS (100K units) | **$18-22** |
| Blended ASP (Year 3) | **$45-52** |
| Contribution Margin | **65%** |
| Break-Even Units | **167,000** |
| Break-Even Timeline | **Month 30** |

### Key Assumptions

| Assumption | Value | Source |
|------------|-------|--------|
| 28nm wafer cost | $3,000 | Industry standard |
| Die size | 40 mm² | Architecture analysis |
| Mature yield | 85% | Conservative for 28nm |
| Learning curve | 85% | Industry standard |
| Churn rate (subscription) | 1.5-5%/month | Hardware lock-in benefit |
| CAC (blended) | $25-400 | Channel dependent |

---

# Part IV: Due Diligence Risk Assessment

## High Risk Items (Will Be Challenged)

### 1. Revenue Projection Inconsistency
**Risk Level**: 🔴 HIGH

An investor comparing the Executive Summary ($35M Y5) against the Business Model ($70M Y5) will immediately question the credibility of both documents.

**Mitigation**: Standardize all projections to Business Model figures before any investor meeting.

---

### 2. Taalas Funding Amount
**Risk Level**: 🔴 HIGH

The $50M variance ($169M vs $219M) suggests inadequate competitive intelligence research. If an investor has done better research, this is embarrassing.

**Mitigation**: Update all documents to $169M (Reuters Feb 2026).

---

### 3. GTM Phase 3 Target ($350M)
**Risk Level**: 🔴 HIGH

The GTM Plan shows $350M for Phase 3, which contradicts the Business Model's Year 5 projection of $70M. This 5x variance will raise questions about whether the team is aligned on strategy.

**Mitigation**: Either:
- Clarify that Phase 3 = Year 6+, or
- Reduce Phase 3 target to $70M

---

## Medium Risk Items (May Be Questioned)

### 4. Gross Margin Claims (65-80%)
**Risk Level**: 🟡 MEDIUM

Hardware gross margins of 65-80% are aggressive compared to industry benchmarks (NVIDIA: 64-67%, Apple hardware: 36-38%). An investor will want detailed justification.

**Mitigation**: Be prepared to explain cartridge economics (80-85% margin) and subscription revenue (85% margin) which drive blended margins.

---

### 5. Unit Volume Ramp (460K units in Y5)
**Risk Level**: 🟡 MEDIUM

The volume ramp from 4,600 (Y1) to 460,000 (Y5) represents 100x growth. Comparable hardware companies (Fitbit, GoPro, Sonos) achieved similar ramps, but this will be scrutinized.

**Mitigation**: Reference comparable company S-1 filings included in Business Model.

---

### 6. Break-Even Timeline (Month 30)
**Risk Level**: 🟡 MEDIUM

Break-even at 167K units is aggressive. If volumes fall short, the company will need additional funding.

**Mitigation**: Sensitivity analysis in Business Model shows bear case (Month 42) - reference this.

---

## Low Risk Items (Unlikely to Be Challenged)

### 7. Technical Performance Claims
**Risk Level**: 🟢 LOW

The 80-150 tok/s, 2-3W, $35-60 claims are consistent across all documents and technically plausible given the iFairy architecture.

---

### 8. Competitive Positioning
**Risk Level**: 🟢 LOW

The competitive analysis is thorough and well-sourced. The positioning against Hailo-10H and Jetson is defensible.

---

# Part V: Recommended Actions

## Immediate (Before Any Investor Meeting)

| Priority | Action | Owner | Document |
|----------|--------|-------|----------|
| 1 | Correct Taalas funding to $169M | Doc Owner | Executive Summary |
| 2 | Standardize Y5 revenue to $70M | Doc Owner | Executive Summary, GTM |
| 3 | Standardize Y5 units to 460K | Doc Owner | Executive Summary |
| 4 | Align product tiers (4 tiers) | Doc Owner | GTM Plan |
| 5 | Standardize gross margin to 65-80% | Doc Owner | All documents |

## Near-Term (Before Series A)

| Priority | Action | Owner |
|----------|--------|-------|
| 1 | Add market size citations to Exec Summary | Doc Owner |
| 2 | Clarify GTM Phase timeline (which years) | Doc Owner |
| 3 | Add Hailo-10H benchmark to Tech Spec | Doc Owner |
| 4 | Create single source of truth spreadsheet | Finance |

## Process Improvements

| Action | Owner | Timeline |
|--------|-------|----------|
| Create Master Numbers spreadsheet in Google Sheets | Finance | Week 1 |
| Require all doc updates to reference Master Numbers | All | Ongoing |
| Quarterly consistency audit | Finance | Ongoing |
| Pre-meeting doc review checklist | Finance | Ongoing |

---

# Appendix A: Document Version Control

| Document | Version | Date | Status |
|----------|---------|------|--------|
| Technical Specification | 1.0 | March 2026 | Needs update (Taalas) |
| Business Model | 1.0 | March 2025 | **MASTER REFERENCE** |
| Executive Summary | 1.0 | March 2026 | Needs updates |
| Competitive Analysis | 2.0 | March 2026 | Current |
| GTM Operations Plan | 1.0 | March 2026 | Needs updates |

---

# Appendix B: Financial Model Cross-Reference

## Year 5 P&L Verification

| Line Item | Business Model | Exec Summary | Variance |
|-----------|----------------|--------------|----------|
| Revenue | $70M | $35M | **$35M** |
| COGS | $13M | $7M | **$6M** |
| Gross Profit | $57M | $28M | **$29M** |
| Operating Income | $41M | ? | Unknown |

**Note**: Executive Summary does not provide Y5 operating income, making verification impossible.

---

# Appendix C: Competitive Data Verification

## Taalas Funding Timeline

| Source | Date | Amount | Notes |
|--------|------|--------|-------|
| Reuters | Feb 2026 | $169M | Series A |
| TechCrunch | Not found | - | No mention |
| Company website | - | - | Not disclosed |

**Verified Amount**: $169M (Reuters Feb 2026 is most recent)

---

*This audit was prepared by Jennifer Walsh, Finance Lead. All findings should be reviewed with document owners before distribution.*

**Next Steps**: Schedule document correction meeting with all owners.
