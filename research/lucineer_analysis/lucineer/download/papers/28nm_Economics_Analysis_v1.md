# 28nm Process Economics: A Deep Analysis for Edge AI Chips
## Manufacturing Cost Structure and Strategic Implications

**Research Classification**: Economic Analysis  
**Author**: SuperInstance.AI Research Team  
**Date**: March 2026  
**Version**: v1.0

---

## Executive Summary

This paper provides a comprehensive economic analysis of the 28nm semiconductor process node for Edge AI chip production. We examine wafer costs, yield economics, capital requirements, and strategic positioning relative to advanced nodes.

**Key Findings**:
- 28nm HPM offers optimal cost-per-good-die for edge AI volumes < 1M units/year
- Total investment to production: $2.5-3.5M (vs $15-25M at 7nm)
- 18-month lead time advantage over advanced nodes
- Recommended sweet spot for SuperInstance initial production

---

## 1. Process Technology Landscape

### 1.1 Node Comparison

**Cost-Performance Analysis**:

| Node | Wafer Cost | Transistor Cost | Power/Area | Volume Required |
|------|------------|-----------------|------------|-----------------|
| 180nm | $800 | Baseline | 100× | 100K+ |
| 90nm | $1,500 | 0.4× | 50× | 500K+ |
| 55nm | $2,000 | 0.3× | 25× | 1M+ |
| 40nm | $2,500 | 0.2× | 15× | 2M+ |
| **28nm** | **$3,200** | **0.15×** | **10×** | **3M+** |
| 14nm | $8,000 | 0.1× | 5× | 10M+ |
| 7nm | $17,000 | 0.08× | 3× | 50M+ |
| 5nm | $30,000 | 0.06× | 2× | 100M+ |
| 3nm | $50,000 | 0.05× | 1× | 200M+ |

**Key Insight**: 28nm represents the "sweet spot" where:
- Transistor cost is near minimum
- Power efficiency is competitive
- NRE costs are manageable
- Capacity is widely available

### 1.2 Foundry Capacity

**Global 28nm Capacity (2026)**:

| Foundry | Capacity (wafers/month) | Utilization | Pricing |
|---------|-------------------------|-------------|---------|
| TSMC | 500,000 | 85% | Premium |
| Samsung | 300,000 | 75% | Competitive |
| SMIC | 200,000 | 70% | Discount |
| GlobalFoundries | 150,000 | 80% | Mid-range |
| UMC | 100,000 | 75% | Competitive |

**Total Available**: ~1.25M wafers/month

---

## 2. Cost Structure Analysis

### 2.1 Wafer Cost Breakdown

**28nm HPM Wafer Cost Components**:

```
┌─────────────────────────────────────────────┐
│     28nm HPM Wafer Cost: $3,200            │
├─────────────────────────────────────────────┤
│                                             │
│  Silicon Substrate:        $200   (6%)     │
│  ├── 300mm wafer          │                │
│  └── Epi layer            │                │
│                                             │
│  Lithography:              $1,400  (44%)    │
│  ├── 193nm immersion      │                │
│  ├── 34 mask layers       │                │
│  └── Multi-patterning     │                │
│                                             │
│  Etch/Clean:               $400   (13%)     │
│                                             │
│  Deposition:               $350   (11%)     │
│  ├── Gate dielectric      │                │
│  ├── Interconnect         │                │
│  └── Passivation          │                │
│                                             │
│  CMP:                      $200   (6%)      │
│                                             │
│  Metrology:                $250   (8%)      │
│                                             │
│  Other:                    $400   (13%)     │
│                                             │
└─────────────────────────────────────────────┘
```

### 2.2 Mask Set Costs

**NRE (Non-Recurring Engineering)**:

| Item | Cost | Notes |
|------|------|-------|
| Design Kit License | $50,000 | TSMC 28nm HPM |
| IP Blocks (USB, PCIe) | $150,000 | Standard interfaces |
| Custom IP (RAU, PE) | $100,000 | Development |
| Mask Set (34 layers) | $1,500,000 | Full set |
| Design Verification | $200,000 | DRC, LVS, Timing |
| Test Structures | $50,000 | PCM, ESD |
| **Total NRE** | **$2,050,000** | |

**Cost Reduction Strategies**:

1. **Multi-Project Wafer (MPW)**:
   - Share mask costs with other designs
   - Cost: $150-250K for prototype run
   - Trade-off: Limited dies, longer queue

2. **Layer Sharing**:
   - Some metal layers can be shared across variants
   - Reduces mask costs by 20-30%
   - Enables product derivatives

3. **E-Beam for Low Volume**:
   - Direct write eliminates masks
   - Cost: $10K setup + $500/wafer
   - Trade-off: 10× longer cycle time

### 2.3 Die Cost Calculation

**SuperInstance Edge-500 Die Cost**:

```
Given:
─────────────────────────────────────────
Die Size: 25 mm² (5mm × 5mm)
Wafer: 300mm diameter
Edge Exclusion: 3mm
Process: 28nm HPM
─────────────────────────────────────────

Gross Dies Per Wafer (DPW):
DPW = π × (R - ee)² / A
    = π × (150 - 3)² / 25
    = π × 147² / 25
    = 67,929 / 25
    = 2,717 dies

Yield Model (Murphy Model):
Y = (1 - e^(-D₀A)) / (D₀A)²
Where D₀ = 0.5 defects/cm²

Y = (1 - e^(-0.5×0.25)) / (0.5×0.25)
  = (1 - e^(-0.125)) / 0.125
  = 0.118 / 0.125
  = 94.4%

Net Good Dies:
2,717 × 94.4% = 2,565 dies

Die Cost:
$3,200 / 2,565 = $1.25/die
```

### 2.4 Assembly and Test

**Packaging Cost Breakdown**:

| Item | Cost | Notes |
|------|------|-------|
| Substrate | $0.30 | 4-layer organic |
| Die Attach | $0.05 | Epoxy |
| Wire Bond | $0.15 | 256 bonds |
| Mold Compound | $0.10 | EMC |
| Marking | $0.02 | Laser |
| Singulation | $0.03 | Saw |
| **Subtotal** | **$0.65** | |

**Test Cost**:

| Test Stage | Cost | Time |
|------------|------|------|
| Wafer Sort (WS) | $0.10 | 0.5s |
| Final Test (FT) | $0.15 | 1.0s |
| Burn-In | $0.20 | 24h |
| System Test | $0.10 | 2.0s |
| **Total Test** | **$0.55** | |

**Total Assembly & Test**: $1.20

---

## 3. Unit Economics

### 3.1 Complete BOM

**SuperInstance Edge-500 BOM**:

| Component | Cost | Source |
|-----------|------|--------|
| Die (28nm) | $1.25 | TSMC |
| LPDDR4 (512MB) | $10.00 | SK Hynix |
| Package (BGA-256) | $0.65 | Amkor |
| Test | $0.55 | ASE |
| Assembly | $0.30 | Amkor |
| PCB (reference) | $1.50 | Shenzhen |
| Passives | $0.25 | Generic |
| **Total BOM** | **$14.50** | |

**At 10K Volume**:

```
COGS Calculation:
─────────────────────────────────────────
BOM:                      $14.50
NRE Amortization:         $2.05M / 10K = $205
Overship (10%):           $1.45
─────────────────────────────────────────
Total COGS:               $221/die

Note: NRE dominates at low volume
```

**At 100K Volume**:

```
COGS Calculation:
─────────────────────────────────────────
BOM:                      $14.50
NRE Amortization:         $2.05M / 100K = $20.50
Overship (10%):           $1.45
Learning Curve:           -$0.50
─────────────────────────────────────────
Total COGS:               $35.95/die

Competitive with Hailo-8
```

### 3.2 Pricing Strategy

**Recommended Pricing**:

| Volume Tier | COGS | ASP | Margin | Market Position |
|-------------|------|-----|--------|-----------------|
| 1K-5K | $221 | $75 | -66% | Development kit |
| 5K-20K | $89 | $65 | 27% | Early adopter |
| 20K-100K | $45 | $55 | 18% | Volume pricing |
| 100K+ | $35 | $50 | 30% | Competitive |

**Price Elasticity Analysis**:

```
Demand Model: Q = A × P^(-ε)

Where:
Q = Quantity demanded
P = Price
ε = Price elasticity (estimated 1.8 for edge AI chips)

At P = $55: Q = 50,000 units
At P = $45: Q = 50,000 × (55/45)^1.8 = 72,000 units
At P = $65: Q = 50,000 × (55/65)^1.8 = 35,000 units

Optimal Price:
P* = MC × (ε / (ε-1))
   = $35 × (1.8 / 0.8)
   = $79

But competitive pressure limits to $50-55 range
```

---

## 4. Capital Requirements

### 4.1 Investment Timeline

**Phase-Based Investment**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Investment Timeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: Validation (Months 1-6)                          │
│  ─────────────────────────────────                         │
│  FPGA development:        $100,000                          │
│  Prototype boards:        $50,000                           │
│  Customer validation:     $50,000                           │
│  Team (3 engineers):      $150,000                          │
│  ─────────────────────────────────                         │
│  Subtotal:                $350,000                          │
│                                                             │
│  Phase 2: Design (Months 7-12)                             │
│  ─────────────────────────────────                         │
│  Design team (5):         $250,000                          │
│  IP licenses:             $200,000                          │
│  EDA tools:               $100,000                          │
│  MPW run:                 $200,000                          │
│  ─────────────────────────────────                         │
│  Subtotal:                $750,000                          │
│                                                             │
│  Phase 3: Production (Months 13-18)                        │
│  ─────────────────────────────────                         │
│  Mask set:                $1,500,000                        │
│  Test development:        $100,000                          │
│  Qualification:           $100,000                          │
│  Production ramp:         $200,000                          │
│  ─────────────────────────────────                         │
│  Subtotal:                $1,900,000                        │
│                                                             │
│  TOTAL INVESTMENT:        $3,000,000                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Cash Flow Projection

**5-Year Financial Model**:

| Year | Revenue | COGS | OpEx | EBITDA | Cash Position |
|------|---------|------|------|--------|----------------|
| 0 | $0 | $0 | $500K | -$500K | $3M (raised) |
| 1 | $275K | $221K | $800K | -$746K | $2.25M |
| 2 | $1.65M | $660K | $1.2M | -$210K | $2.04M |
| 3 | $5.5M | $1.65M | $2.0M | $1.85M | $3.89M |
| 4 | $12M | $3.0M | $3.5M | $5.5M | $9.39M |
| 5 | $25M | $6.25M | $6.0M | $12.75M | $22.14M |

**Breakeven**: Month 28

### 4.3 Funding Strategy

**Recommended Funding Path**:

```
Seed Round (Month 0):
─────────────────────────────────────────
Amount:      $500K
Type:        Convertible Note
Valuation:   $5M cap
Use:         Phase 1 validation
─────────────────────────────────────────

Series A (Month 6):
─────────────────────────────────────────
Amount:      $2.5M
Type:        Equity
Valuation:   $15M pre-money
Use:         Design + initial masks
─────────────────────────────────────────

Series B (Month 18):
─────────────────────────────────────────
Amount:      $10M
Type:        Equity
Valuation:   $50M pre-money
Use:         Scale production, team growth
─────────────────────────────────────────
```

---

## 5. Competitive Positioning

### 5.1 Cost vs. Competition

**Unit Cost Comparison at 100K Volume**:

| Competitor | Process | COGS | ASP | Margin |
|------------|---------|------|-----|--------|
| Hailo-8 | 7nm | $35 | $100 | 65% |
| Google Coral | 28nm | $25 | $75 | 67% |
| NVIDIA Jetson Nano | 20nm | $45 | $99 | 55% |
| **SuperInstance** | **28nm** | **$36** | **$55** | **35%** |

**Strategic Implication**:
- Lower margin but higher efficiency value proposition
- Volume ramp faster due to price advantage
- Gross margin improves at scale

### 5.2 Process Migration Path

**Future Node Considerations**:

```
Current State (28nm HPM):
─────────────────────────────────────────
✓ Low NRE ($2M)
✓ Available capacity
✓ Mature yield models
✓ Multiple foundries
✗ Higher power

Future Migration Options:
─────────────────────────────────────────
22nm FD-SOI:
  - 30% power reduction
  - 50% higher NRE
  - Back-biasing for performance tuning

14nm FinFET:
  - 50% power reduction
  - 3× NRE ($6M)
  - Limited capacity

12nm FDSOI (GlobalFoundries):
  - 40% power reduction
  - 2× NRE ($4M)
  - Good for edge AI
```

**Recommendation**: Stay at 28nm for first product. Plan 22nm FD-SOI migration at 500K+ volume.

---

## 6. Risk Analysis

### 6.1 Supply Chain Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Capacity shortage | Medium | High | Multi-foundry strategy |
| Price increase | Medium | Medium | Long-term contracts |
| Geopolitical (China-Taiwan) | Low | Critical | SMIC as backup |
| Equipment sanctions | Low | High | Qualify mature tools |

### 6.2 Financial Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Yield lower than expected | Medium | Medium | Conservative design rules |
| Volume ramp slower | High | Medium | Flexible supply contracts |
| Price pressure | High | Medium | Efficiency differentiation |
| Customer concentration | Medium | High | Diversify target markets |

---

## 7. Strategic Recommendations

### 7.1 Make vs. Buy Analysis

**In-House vs. Outsourced**:

| Function | In-House | Outsourced | Decision |
|----------|----------|------------|----------|
| Design | Core competency | - | ✓ In-house |
| Mask design | Tools/license | Service | In-house |
| Wafer fab | $5B+ investment | Foundry | ✓ Outsource |
| Assembly | $50M+ investment | OSAT | ✓ Outsource |
| Test | $5M investment | OSAT | Hybrid |

### 7.2 Foundry Selection

**Evaluation Matrix**:

| Foundry | Cost | Quality | Capacity | Support | Score |
|---------|------|---------|----------|---------|-------|
| TSMC | 3 | 5 | 5 | 4 | 17 |
| Samsung | 4 | 4 | 4 | 4 | 16 |
| SMIC | 5 | 3 | 4 | 3 | 15 |
| GlobalFoundries | 4 | 4 | 3 | 4 | 15 |
| UMC | 4 | 4 | 3 | 3 | 14 |

**Recommendation**: 
- Primary: TSMC (quality + support)
- Backup: Samsung (cost + capacity)

### 7.3 Volume Commitment Strategy

**Optimal Commitment**:

```
Year 1: Pay-as-you-go (no commitment)
─────────────────────────────────────────
- Higher unit cost ($3,500/wafer)
- Maximum flexibility
- Learning period

Year 2: Soft commit (100 wafers/month)
─────────────────────────────────────────
- 10% discount ($3,150/wafer)
- 3-month cancellation notice
- Volume validation

Year 3+: Hard commit (500+ wafers/month)
─────────────────────────────────────────
- 20% discount ($2,800/wafer)
- Capacity reservation
- Priority in allocation
```

---

## 8. Conclusions

### 8.1 Key Takeaways

1. **28nm is optimal for first product**: Low NRE, mature process, available capacity
2. **Total investment: $3M to production**: Manageable for seed/Series A
3. **Breakeven at 50K units**: Achievable within 3 years
4. **Gross margin expands with volume**: From 35% to 45%+
5. **Process migration path exists**: 22nm FD-SOI when volume justifies

### 8.2 Action Items

**Immediate (Month 1-3)**:
- [ ] Negotiate MPW slot with TSMC/Samsung
- [ ] Secure EDA tool licenses
- [ ] Build design team

**Short-term (Month 4-12)**:
- [ ] Complete RTL design
- [ ] Run MPW for silicon validation
- [ ] Begin customer engagement

**Medium-term (Month 13-18)**:
- [ ] Commit to production masks
- [ ] Finalize test program
- [ ] Plan volume ramp

---

## Appendix A: Yield Model Details

**Murphy Yield Model**:

```
Y = [(1 - e^(-AD))/(AD)]²

Where:
A = Die area (cm²)
D = Defect density (defects/cm²)

For SuperInstance Edge-500:
A = 0.25 cm²
D = 0.5 (28nm typical)

Y = [(1 - e^(-0.125))/(0.125)]²
  = [0.882/0.125]² × 0.882
  = 0.944 (94.4%)
```

## Appendix B: Competitive Intelligence

**Hailo-8 Cost Structure (Estimated)**:

```
Process: 7nm (TSMC)
Die Size: ~15 mm²
Wafer Cost: $17,000
DPW: ~4,500
Yield: ~80%
Good Dies: ~3,600

Die Cost: $17,000 / 3,600 = $4.72
Package + Memory: ~$25
Total COGS: ~$30

ASP: $100
Margin: 70%
```

---

*Document Version: 1.0*  
*Contact: finance@superinstance.ai*
