# SuperInstance.AI Master Numbers Reference
## Single Source of Truth for All Documents

**Version**: 1.0  
**Last Updated**: March 2026  
**Owner**: Jennifer Walsh, Finance Lead  
**Status**: APPROVED - Use these numbers in ALL documents

---

> ⚠️ **IMPORTANT**: When creating or updating any investor-facing document, ALWAYS reference this sheet. Any changes to these numbers must be approved by Finance.

---

# Product Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Throughput** | 80-150 tok/s | Consumer tier, BitNet 2B model |
| **Power Consumption** | 2-3W | USB-powered operation |
| **Tokens per Watt** | 27-50 | Depending on tier and utilization |
| **First Token Latency** | <50ms | Cold start |
| **Inter-Token Latency** | 10-15ms | Steady state |

---

# Product Pricing (4-Tier Model)

| Tier | SKU | Target Market | COGS | ASP | Gross Margin |
|------|-----|---------------|------|-----|--------------|
| **Nano** | SI-100 | Hobbyist/Education | **$7** | **$35** | **80%** |
| **Micro** | SI-200 | IoT Integration | **$15** | **$49** | **69%** |
| **Standard** | SI-300 | Professional Dev | **$22** | **$79** | **72%** |
| **Pro** | SI-400 | Enterprise Edge | **$45** | **$149** | **70%** |

**Blended ASP**: $52 (Year 1) declining to $42 (Year 5)  
**Blended COGS**: $18 (Year 3)  
**Blended Gross Margin**: 65-80%

---

# Cartridge Pricing

| Type | Model Size | COGS | ASP | Gross Margin |
|------|------------|------|-----|--------------|
| **Discovery** | 1.5B params | **$3** | **$19** | **84%** |
| **Standard** | 2.4B params | **$5** | **$29** | **83%** |
| **Premium** | 4B params | **$8** | **$49** | **84%** |
| **Enterprise** | 8B params | **$15** | **$89** | **83%** |

---

# Financial Projections (5-Year)

## Revenue Summary

| Year | Units | Revenue | Gross Profit | Operating Income |
|------|-------|---------|--------------|------------------|
| **Year 1** | 4,600 | **$240K** | $169K | ($931K) |
| **Year 2** | 57,000 | **$2.9M** | $2.2M | ($758K) |
| **Year 3** | 185,000 | **$11.2M** | $8.9M | $2.9M |
| **Year 4** | 330,000 | **$28.9M** | $23.2M | $12.9M |
| **Year 5** | 460,000 | **$70M** | $57M | $41M |

## Revenue by Stream (Year 5)

| Stream | Revenue | % of Total | Gross Margin |
|--------|---------|------------|--------------|
| Hardware - Base | $24.5M | 35% | 68% |
| Hardware - Cartridges | $14M | 20% | 72% |
| Subscriptions | $17.5M | 25% | 85% |
| Platform Revenue | $8.4M | 12% | 95% |
| Enterprise Licensing | $5.6M | 8% | 90% |
| **Total** | **$70M** | 100% | **74% blended** |

---

# Funding Requirements

| Round | Amount | Timing | Key Milestone |
|-------|--------|--------|---------------|
| **Seed** | $500K | Month 1-6 | FPGA prototype, 25 tok/s |
| **Series A** | $3M | Month 7-18 | First silicon, 30 LOIs |
| **Series B** | $10M | Month 19-36 | 100K+ units shipped |

## Dilution Analysis

| Round | Pre-Money | Post-Money | Dilution | Founder % |
|-------|-----------|------------|----------|-----------|
| Seed | $4M | $4.5M | 11% | 89% |
| Series A | $18M | $21M | 14% | 77% |
| Series B | $50M | $60M | 17% | 64% |

---

# Market Size

| Metric | Value | Source |
|--------|-------|--------|
| **TAM** (Edge AI Silicon) | $19.9B (2030) | IDC, 23% CAGR |
| **SAM** (LLM-Capable Edge) | $11.5B (2030) | McKinsey, 26% CAGR |
| **SOM** (Sub-$100 LLM Inference) | $500M-$1B (2030) | Internal estimate |

---

# Competitive Intelligence (Verified)

| Competitor | Funding | Price | Power | LLM Performance | Target Market |
|------------|---------|-------|-------|-----------------|---------------|
| **Taalas HC1** | $169M | API model | 200W+ | 14,000-17,000 tok/s | Data Center |
| **Hailo-10H** | $400M+ | $70-90 | 5W | 5-10 tok/s | Pi Ecosystem |
| **Jetson Orin Nano** | - | $199-249 | 10-15W | 20-30 tok/s | Development |
| **Google Coral** | - | $60-70 | 2W | N/A (vision only) | Maker (EOL) |

**Key Differentiator**: No competitor targets $35-60 price point for LLM inference.

---

# Unit Economics

| Metric | Value |
|--------|-------|
| Break-Even Units | **167,000** |
| Break-Even Timeline | **Month 30** (base case) |
| LTV (Hardware Customer) | $95-$1,870 (by segment) |
| LTV:CAC Ratio | 8:1 (hardware) / 15:1 (subscription) |
| Churn Rate (Subscription) | 1.5-5%/month |

## Contribution Margin by Tier

| Product | Selling Price | Variable Cost | Contribution | CM Ratio |
|---------|---------------|---------------|--------------|----------|
| Nano | $35 | $7 | $28 | 80% |
| Micro | $49 | $15 | $34 | 69% |
| Standard | $79 | $22 | $57 | 72% |
| Pro | $149 | $45 | $104 | 70% |
| **Blended** | **$52** | **$18** | **$34** | **65%** |

---

# Manufacturing Costs

| Component | Nano | Micro | Standard | Pro |
|-----------|------|-------|----------|-----|
| Die (28nm) | $2.50 | $4.00 | $6.00 | $12.00 |
| Package (BGA) | $0.50 | $1.00 | $1.50 | $3.00 |
| On-chip SRAM | $2.00 | $4.00 | $6.00 | $10.00 |
| External Memory | $0 | $2.00 | $4.00 | $8.00 |
| PCB + Assembly | $1.00 | $2.00 | $2.50 | $4.00 |
| Connectors/Thermal | $0.50 | $1.00 | $1.00 | $4.00 |
| Test & QA | $0.50 | $1.00 | $1.00 | $4.00 |
| **Total COGS** | **$7.00** | **$15.00** | **$22.00** | **$45.00** |

---

# Key Assumptions

| Assumption | Value | Source |
|------------|-------|--------|
| 28nm wafer cost | $3,000 | Industry standard (TSMC) |
| Die size | 40 mm² | Architecture analysis |
| Mature yield | 85% | Conservative for 28nm |
| Learning curve | 85% | Industry standard |
| Engineer salary (Bay Area) | $150K/year | Market rate |
| EDA tool cost | $150K/year/team | Cadence/Synopsys |
| Subscription attach rate | 15-40% | Hardware + software typical |
| Customer acquisition cost | $25-400 | Channel dependent |
| Churn rate | 1.5-5%/month | Hardware lock-in benefit |

---

# Change Log

| Date | Version | Changed By | Change Description |
|------|---------|------------|-------------------|
| March 2026 | 1.0 | J. Walsh | Initial release |

---

# Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Finance Lead | Jennifer Walsh | March 2026 | ✓ |
| CEO | TBD | - | - |
| CTO | Dr. Michael Torres | - | - |

---

*This document is the single source of truth for all financial numbers in SuperInstance.AI investor materials. Any changes must be approved through the Finance team.*
