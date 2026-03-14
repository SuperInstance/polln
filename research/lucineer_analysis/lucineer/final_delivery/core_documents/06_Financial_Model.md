# Financial Model & Unit Economics
## Mask-Locked Inference Chip Business Case

**Document Version**: Final 1.0
**Date**: March 2026

---

# Part I: Unit Economics

## Manufacturing Cost Breakdown

### Die Cost (28nm, 40 mm²)

| Component | Cost |
|-----------|------|
| Wafer cost (300mm) | $3,000 |
| Dies per wafer | 1,360 |
| Yield | 80% |
| **Die cost** | **$2.21** |

### Packaging & Test

| Component | Cost |
|-----------|------|
| BGA package (15×15mm) | $1.50 |
| Assembly | $1.00 |
| Test | $0.50 |
| **Subtotal** | **$3.00** |

### External Memory Options

| Configuration | Memory Cost | Total COGS |
|---------------|-------------|------------|
| On-chip SRAM only | $0 | $5.21 |
| + LPDDR4 256MB | $7 | $12.21 |
| + LPDDR4 512MB | $11 | $16.21 |

### Gross Margin Analysis

| Config | COGS | ASP | Gross Margin |
|--------|------|-----|--------------|
| Minimal | $5.21 | $35 | 85% |
| Standard | $12.21 | $49 | 75% |
| Extended | $16.21 | $69 | 77% |

---

# Part II: Development Costs

## NRE (Non-Recurring Engineering)

| Item | 28nm | Notes |
|------|------|-------|
| Mask set | $2-3M | Full production |
| MPW prototype | $50K | 20-40 units |
| Design & verification | $2-4M | Team for 18 months |
| Software/SDK | $500K | Drivers, tools |
| **Total NRE** | **$4.5-7.5M** | |

## Funding Requirements

| Stage | Amount | Timeline | Use |
|-------|--------|----------|-----|
| Pre-seed | $150K | Month 0-3 | Architecture, prototype |
| Seed | $500K | Month 1-6 | Team, FPGA validation |
| Series A | $3M | Month 7-18 | Design, MPW |
| Series B | $10M | Month 19+ | Production scaling |

---

# Part III: Revenue Projections

## 5-Year Model

| Year | Units | Revenue | COGS | Gross Profit | OpEx | Net Income |
|------|-------|---------|------|--------------|------|------------|
| 1 | 5K | $175K | $26K | $149K | $800K | ($651K) |
| 2 | 50K | $1.75M | $260K | $1.49M | $2M | ($510K) |
| 3 | 200K | $7M | $1.05M | $5.95M | $3M | $2.95M |
| 4 | 500K | $17.5M | $2.6M | $14.9M | $5M | $9.9M |
| 5 | 1M | $35M | $5.2M | $29.8M | $8M | $21.8M |

## Assumptions
- Average ASP: $35 (Year 1-2), $32 (Year 3-5) due to price pressure
- COGS: $5.21 (on-chip only, volume benefits)
- Gross margin: 85% declining to 70% by Year 5

---

# Part IV: Sensitivity Analysis

## Price Sensitivity

| ASP | Units Needed for $10M Revenue |
|-----|------------------------------|
| $25 | 400,000 |
| $35 | 286,000 |
| $49 | 204,000 |
| $69 | 145,000 |

## COGS Sensitivity

| COGS | Gross Margin at $35 ASP |
|------|------------------------|
| $5 | 86% |
| $10 | 71% |
| $15 | 57% |
| $20 | 43% |

## Memory Price Risk

LPDDR4 prices increased 132% in 3 months (2025). Risk scenarios:

| Scenario | Memory Cost | COGS Impact |
|----------|-------------|-------------|
| Best case | $8/512MB | $13.21 |
| Base case | $11/512MB | $16.21 |
| Worst case | $18/512MB | $23.21 |

**Mitigation**: On-chip only version eliminates this risk.

---

# Part V: Break-Even Analysis

## Units to Break-Even

| NRE Investment | At $35 ASP, $5 COGS |
|----------------|---------------------|
| $3M | 100,000 units |
| $5M | 167,000 units |
| $7M | 233,000 units |

## Time to Break-Even

| Ramp Rate | Units/Year | Time to 167K |
|-----------|------------|--------------|
| Conservative | 50K | 3+ years |
| Base case | 100K | 2 years |
| Aggressive | 200K | 1 year |

---

# Part VI: Valuation Analysis

## Comparable Valuations

| Company | Stage | Valuation | Multiple |
|---------|-------|-----------|----------|
| Etched | Series A | $245M raised | N/A (pre-revenue) |
| Taalas | Series A | $219M raised | N/A (pre-revenue) |
| Hailo | Series C | $300M+ raised | ~8x revenue |
| Groq (exit) | Acquired | $20B | Licensing + team |

## Expected Valuation Path

| Milestone | Valuation Range |
|-----------|-----------------|
| Post-Gate 0 | $10-20M |
| Post-Gate 1 | $20-40M |
| Post-Gate 2 (first silicon) | $40-80M |
| Post-Gate 3 (revenue) | $80-200M |

## Exit Valuation

| Revenue | Acquisition Value |
|---------|-------------------|
| $5M | $50-100M |
| $20M | $100-200M |
| $50M | $200-400M |

---

# Part VII: Funding Strategy

## Government Grants

| Program | Amount | Timeline |
|---------|--------|----------|
| NSF SBIR Phase I | $275K | 6 months |
| NSF SBIR Phase II | $1M | 24 months |
| CHIPS Act R&D | $2-5M | Competitive |
| DARPA AI | $1-3M | Competitive |

**Strategy**: Pursue SBIR simultaneously with equity funding.

## Dilution Analysis

| Round | Raise | Pre-money | Post-money | Dilution |
|-------|-------|-----------|------------|----------|
| Pre-seed | $150K | $1M | $1.15M | 13% |
| Seed | $500K | $5M | $5.5M | 9% |
| Series A | $3M | $20M | $23M | 13% |
| Series B | $10M | $50M | $60M | 17% |

**Founder ownership at Series B**: ~50% (assuming no other dilution)

---

# Part VIII: Cash Flow Model

## Monthly Burn (Post-Seed)

| Category | Monthly |
|----------|---------|
| Salaries (5 FTE) | $50K |
| Office/Equipment | $5K |
| EDA Tools | $10K |
| Contractors | $10K |
| **Total Burn** | **$75K/month** |

## Runway Analysis

| Funding | Runway (at $75K/mo) |
|---------|---------------------|
| $500K | 6-7 months |
| $1M | 12-13 months |
| $2M | 24-26 months |

---

# Part IX: Investment Return Analysis

## Seed Investment ($500K)

| Scenario | Exit Value | Return | Multiple |
|----------|------------|--------|----------|
| Bear | $50M | $4.3M | 8.6x |
| Base | $150M | $13M | 26x |
| Bull | $400M | $35M | 70x |

## Series A Investment ($3M)

| Scenario | Exit Value | Return | Multiple |
|----------|------------|--------|----------|
| Bear | $50M | $6.5M | 2.2x |
| Base | $150M | $19.5M | 6.5x |
| Bull | $400M | $52M | 17x |

---

# Appendix: Key Assumptions

| Assumption | Value | Source |
|------------|-------|--------|
| 28nm wafer cost | $3,000 | Industry standard |
| Die yield | 80% | Conservative for mature node |
| Package cost | $1.50 | BGA 15×15mm |
| LPDDR4 512MB | $11 | Current market (volatile) |
| ASP Year 1 | $35 | Market gap analysis |
| Gross margin target | 70%+ | Hardware standard |
| Team cost | $150K/FTE/year | SF Bay Area rates |

---

*Financial model is conservative. Upside scenarios exceed projections significantly.*
