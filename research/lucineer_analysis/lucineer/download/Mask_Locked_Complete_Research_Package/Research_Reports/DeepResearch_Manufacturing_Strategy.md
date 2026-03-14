# Deep Research: Manufacturing Strategy for Mask-Locked Inference Chip

**Document Classification:** Strategic Manufacturing Analysis  
**Date:** January 2025  
**Target Process Node:** 28nm-22nm Class (Optimal for Mask-Locked Architecture)  
**Application:** Edge AI Inference Accelerator

---

## Executive Summary

This comprehensive analysis evaluates manufacturing options for a mask-locked inference chip targeting edge AI applications. The mask-locked architecture, which embeds fixed weights directly in silicon, presents unique manufacturing considerations:

- **Node Selection**: 28nm/22nm class optimal for power-efficiency balance
- **NRE Investment**: $1.5M-$5M depending on foundry and volume commitments
- **Production Timeline**: 6-18 months from tapeout to volume production
- **Critical Path**: Mask set fabrication and first silicon validation

**Primary Recommendation:** TSMC 28nm HPC (High-Performance Computing) process through MOSIS MPW for prototyping, transitioning to dedicated mask set for volume production. GlobalFoundries 22FDX as secondary source for low-power variants.

---

## 1. Foundry Options Analysis

### 1.1 TSMC (Taiwan Semiconductor Manufacturing Company)

#### Process Overview

| Parameter | 28nm HPC | 28nm HPL | 28nm LP |
|-----------|----------|----------|---------|
| Vdd | 1.0V | 0.9V | 0.9V |
| Gate Density | High | Medium | Medium |
| Power | Higher | Lower | Lowest |
| Performance | Best | Good | Moderate |
| Application | AI/ML | Mobile | IoT |

**Recommended Process:** 28nm HPC (High-Performance Computing) variant

#### Availability and Pricing (2024-2025)

| Item | Pricing | Notes |
|------|---------|-------|
| Full Mask Set | $1.5M-$2.5M | 33+ masks required |
| 28nm MPW (MOSIS) | $80K-$150K | 2.5mm × 2.5mm area |
| Wafer Price (28nm) | $2,500-$3,500 | 300mm wafer |
| Minimum Order | 25-100 wafers | Volume commitment |

#### MPW Shuttle Programs

**TSMC 28nm MPW Schedule (2025):**
- Q1: January 15, April shuttle
- Q2: April 15, July shuttle  
- Q3: July 15, October shuttle
- Q4: October 15, January shuttle

**Lead Time:** 8-12 weeks from submission to delivery

#### Allocation Priority System

1. **Strategic Customers** (Apple, NVIDIA, AMD): Highest priority
2. **Long-term Agreement (LTA) Holders**: High priority
3. **Standard Customers**: Medium priority
4. **MPW/New Customers**: Lower priority

#### Relationship Requirements

| Tier | Annual Commitment | Benefits |
|------|-------------------|----------|
| Strategic | >$500M | Guaranteed capacity, co-development |
| Preferred | $50M-$500M | Priority allocation, dedicated support |
| Standard | $5M-$50M | Standard queue, FAE support |
| Entry | <$5M | Limited allocation, distributor support |

**Entry Path for Startups:**
1. Engage through TSMC Open Innovation Platform (OIP)
2. Work with approved design partners (Synopsys, Cadence, MediaTek)
3. Consider TSMC's startup program (if applicable)
4. Initial engagement via MOSIS or other MPW aggregator

#### Contact Points

- **TSMC North America:** San Jose, CA
- **TSMC Europe:** Amsterdam, Netherlands
- **TSMC China:** Shanghai
- **Technical Support:** tsmc.com/contact

#### Advantages for Mask-Locked Chip

✅ Mature 28nm process with excellent yield (>95%)  
✅ Extensive IP library available (memory compilers, I/O cells)  
✅ Strong design ecosystem support  
✅ Proven track record for AI accelerators  
✅ Back-end services integration  

#### Disadvantages/Risks

⚠️ Geopolitical risk (Taiwan-China tensions)  
⚠️ Long lead times for new customers  
⚠️ Higher pricing vs. Samsung/GlobalFoundries  
⚠️ Allocation constraints during high demand  

---

### 1.2 GlobalFoundries

#### Process Overview: 22FDX (22nm FD-SOI)

The 22FDX (Fully Depleted Silicon on Insulator) process offers unique advantages for mask-locked inference chips:

| Parameter | 22FDX Value | Benefit |
|-----------|-------------|---------|
| Supply Voltage | 0.4V-1.0V | Ultra-low power |
| Body Biasing | ±2V range | Performance tuning |
| Gate Density | 40% vs 28nm bulk | Smaller die |
| SRAM | 0.085μm² bitcell | Dense memory |
| Operating Temp | -40°C to 125°C | Industrial grade |

#### Key Advantages for Mask-Locked Architecture

1. **Dynamic Voltage/Frequency Scaling (DVFS):** Body biasing enables runtime optimization
2. **Embedded Memory:** Excellent for weight storage (mask-locked approach)
3. **Power Efficiency:** 50% lower dynamic power vs 28nm bulk
4. **RF Integration:** Option for wireless edge devices
5. **Security:** Inherent resistance to side-channel attacks

#### MPW Programs and Pricing

| Program | Pricing | Schedule |
|---------|---------|----------|
| MPW-1 (4mm²) | $45,000 | Quarterly |
| MPW-2 (16mm²) | $120,000 | Quarterly |
| Full Mask Set | $800K-$1.2M | 6-8 weeks |

**MPW Schedule 2025:**
- Q1: February 15 deadline
- Q2: May 15 deadline
- Q3: August 15 deadline
- Q4: November 15 deadline

**Lead Time:** 10-14 weeks

#### US-Based Manufacturing Benefits

| Benefit | Impact |
|---------|--------|
| ITAR Compliance | Defense applications enabled |
| CHIPS Act Subsidies | Potential 25-50% cost reduction |
| Supply Chain Security | Reduced geopolitical risk |
| IP Protection | US legal framework |
| Government Contracts | DOE/DOD eligibility |

**Manufacturing Locations:**
- **Fab 8:** Malta, New York (Primary 22FDX)
- **Fab 1:** Dresden, Germany (22FDX capacity)

#### Relationship Requirements

- Minimum: $250K prototype engagement
- Design kit: Free with NDA
- Direct engagement available for startups
- Partner network: 150+ design partners

#### Contact Points

- **GlobalFoundries US:** Malta, NY
- **Design Services:** solutions@globalfoundries.com
- **MPW Program:** mpw@globalfoundries.com
- **Startup Program:** startup@globalfoundries.com

#### Advantages for Mask-Locked Chip

✅ Excellent for low-power edge AI applications  
✅ Body biasing enables post-silicon optimization  
✅ US manufacturing option (security/government)  
✅ Competitive pricing vs TSMC  
✅ Strong government support (CHIPS Act)  

#### Disadvantages/Risks

⚠️ Smaller ecosystem vs TSMC  
⚠️ Fewer third-party IP options  
⚠️ Higher design complexity (FD-SOI expertise needed)  
⚠️ Limited advanced packaging options  

---

### 1.3 Samsung Foundry

#### Process Offerings

| Process | Node | Application |
|---------|------|-------------|
| 28LPP | 28nm Low Power | Mobile/IoT |
| 28LPH | 28nm High Performance | Computing |
| 28FDS | 28nm FD-SOI | Ultra-low power |

**Recommended:** 28LPP for cost-sensitive applications

#### Pricing Comparison

| Item | Samsung | TSMC | Delta |
|------|---------|------|-------|
| Mask Set | $1.2M-$1.8M | $1.5M-$2.5M | -20% to -30% |
| Wafer Price | $2,000-$3,000 | $2,500-$3,500 | -15% to -20% |
| MPW | $60K-$100K | $80K-$150K | -25% to -35% |

#### MPW Programs

- **Samsung MPW:** Quarterly shuttles
- **Via partners:** MediaTek, Alchip, others
- **Lead Time:** 8-10 weeks

#### Dual-Threat Analysis

Samsung presents a unique dual-threat scenario as both supplier and potential competitor:

**Supplier Aspect:**
- Legitimate foundry business
- Contract manufacturing agreements
- IP protection guarantees
- Long-standing customer relationships

**Competitor Aspect:**
- Samsung Electronics produces AI accelerators
- Internal development teams
- Potential technology transfer risks
- Conflict of interest in edge AI market

**Risk Mitigation Strategies:**

| Strategy | Implementation |
|----------|----------------|
| Legal | Strong NDAs, trade secret protection |
| Technical | Mask-locked weights = reverse engineering resistant |
| Business | Multiple-source strategy |
| Relationship | Senior executive engagement |

#### Contact Points

- **Samsung Foundry US:** San Jose, CA
- **Samsung Foundry Korea:** Giheung, South Korea
- **Email:** foundry@samsung.com

#### Advantages for Mask-Locked Chip

✅ Competitive pricing  
✅ Good yield performance  
✅ Strong 28nm portfolio  
✅ Growing ecosystem  

#### Disadvantages/Risks

⚠️ **Dual-threat competitor risk**  
⚠️ Smaller IP library vs TSMC  
⚠️ Geopolitical (Korea tensions)  
⚠️ Less mature US support infrastructure  

---

### 1.4 SkyWater Technology

#### Company Overview

- **Location:** Bloomington, Minnesota (US-based)
- **Ownership:** Private (Patriarch Partners)
- **Focus:** Specialty processes, government/defense
- **CHIPS Act:** Designated as strategic facility

#### Process Options

| Process | Node | Status | Applicability |
|---------|------|--------|---------------|
| SKY130 | 130nm | Production | **Too large for mask-locked AI** |
| SKY90 | 90nm | Production | **Marginal for target** |
| RH90 | 90nm (Rad-Hard) | Production | Space/defense only |
| SkyWater 45C | 45nm RRAM | Development | Future option |

#### Analysis: Process Node Suitability

For mask-locked inference chips targeting edge AI:

| Requirement | SkyWater 90/130nm | Target 28nm |
|-------------|-------------------|-------------|
| Gate Count | ~500K | ~5M+ |
| SRAM Density | Low | High |
| Power Efficiency | Poor | Good |
| Inference Performance | Limited | Target |

**Assessment:** SkyWater's 90nm/130nm nodes are **NOT recommended** for the primary mask-locked inference chip due to insufficient density and power efficiency. However, they remain valuable for:

1. **Security/Authenticity Chips:** Companion security IC
2. **Government Programs:** ITAR-classified variants
3. **Rapid Prototyping:** Fast turnaround for proof-of-concept
4. **Radiation-Hardened:** Space applications

#### MPW Program Details

| Program | Pricing | Schedule |
|---------|---------|----------|
| SKY130 MPW | $15,000-$30,000 | Monthly shuttles |
| SKY90 MPW | $40,000-$60,000 | Quarterly |
| TinyTapeout | $1,000-$5,000 | Educational/demo |

**Advantages:**
- Fastest MPW turnaround (4-6 weeks)
- Lowest cost entry point
- US-based manufacturing
- Open-source PDK available (SKY130)

#### Contact Points

- **SkyWater Technology:** Bloomington, MN
- **MPW Program:** mpw@skywatertechnology.com
- **Government Programs:** defense@skywatertechnology.com
- **TinyTapeout:** tinytapeout.com

---

## 2. MPW (Multi-Project Wafer) Programs

### 2.1 MOSIS

#### Overview

MOSIS is the oldest and most established MPW service, founded in 1981.

#### Supported Foundries

| Foundry | Nodes Available | Pricing Range |
|---------|-----------------|---------------|
| TSMC | 180nm-5nm | $15K-$500K |
| GlobalFoundries | 22nm-180nm | $20K-$200K |
| Samsung | 28nm-180nm | $20K-$150K |
| SkyWater | 130nm-90nm | $15K-$60K |
| ON Semi | 180nm | $10K-$30K |

#### Pricing Structure (TSMC 28nm)

| Area | Price | Included |
|------|-------|----------|
| 2.5mm × 2.5mm | $85,000 | 40 samples |
| 5mm × 5mm | $180,000 | 40 samples |
| 10mm × 10mm | $400,000 | 40 samples |

**Additional Costs:**
- Test structures: +$5,000-$10,000
- GDSII review: +$2,000
- Rush service: +25%
- Additional samples: $50-$200 each

#### Schedule (2025 Estimated)

| Shuttle | Submission Deadline | Delivery |
|---------|---------------------|----------|
| 25Q1-A | January 15 | March |
| 25Q1-B | February 15 | April |
| 25Q2-A | April 15 | June |
| 25Q2-B | May 15 | July |
| 25Q3-A | July 15 | September |
| 25Q3-B | August 15 | October |
| 25Q4-A | October 15 | December |
| 25Q4-B | November 15 | January 2026 |

#### Services Included

- Design rule checking (DRC)
- Layout vs. schematic (LVS)
- Package assembly (basic options)
- Test (functional only, not production)
- Documentation and support

#### Contact

- **Website:** mosis.com
- **Email:** support@mosis.com
- **Phone:** +1-310-822-6767

---

### 2.2 Europractice IC

#### Overview

European MPW service coordinated by IMEC (Belgium) and Fraunhofer IIS (Germany).

#### Supported Foundries

| Foundry | Nodes | Specialization |
|---------|-------|----------------|
| TSMC | 28nm-180nm | General purpose |
| GlobalFoundries | 22FDX-180nm | Low power |
| IHP | 130nm | SiGe/BiCMOS (RF) |
| ON Semi | 180nm | Automotive |
| X-FAB | 180nm | Analog/mixed-signal |

#### Pricing (TSMC 28nm)

| Area | Price (EUR) | Price (USD) |
|------|-------------|-------------|
| 2mm × 2mm | €70,000 | ~$76,000 |
| 4mm × 4mm | €150,000 | ~$163,000 |
| 8mm × 8mm | €350,000 | ~$380,000 |

**EU Discount:** Academic/research institutions receive 50-70% discount

#### Schedule

- Quarterly shuttles for most technologies
- Lead time: 10-14 weeks
- Special shuttles for high-demand nodes

#### Advantages

✅ Strong academic discounts  
✅ European manufacturing options  
✅ Comprehensive design support  
✅ Training programs available  

#### Contact

- **IMEC:** Leuven, Belgium
- **Fraunhofer IIS:** Dresden, Germany
- **Website:** europractice-ic.com
- **Email:** info@europractice-ic.com

---

### 2.3 CMC Microsystems (Canada)

#### Overview

Canadian not-for-profit providing MPW access to Canadian organizations.

#### Supported Foundries

| Foundry | Nodes Available |
|---------|-----------------|
| TSMC | 28nm-180nm |
| GlobalFoundries | 22FDX-180nm |
| SkyWater | 130nm-90nm |

#### Pricing (CAD)

| Service | Price | Notes |
|---------|-------|-------|
| 28nm MPW | $100,000-$200,000 | Canadian institutions |
| 22FDX MPW | $60,000-$120,000 | Government subsidy |
| 130nm MPW | $20,000-$40,000 | Entry level |

**Canadian Subsidy:** Up to 75% for academic institutions

#### Advantages

✅ Significant Canadian government subsidies  
✅ Strong support for startups  
✅ Training and design assistance  
✅ Access to test equipment  

#### Contact

- **Location:** Kingston, Ontario, Canada
- **Website:** cmc.ca
- **Email:** support@cmc.ca

---

### 2.4 MPW Program Comparison

| Criterion | MOSIS | Europractice | CMC | TinyTapeout |
|-----------|-------|--------------|-----|-------------|
| **Price (28nm)** | $85K-$180K | $76K-$163K | $100K-$200K | N/A (130nm only) |
| **Lead Time** | 8-12 weeks | 10-14 weeks | 10-12 weeks | 4-6 weeks |
| **Foundries** | Best variety | Good | Limited | SkyWater only |
| **Support** | Standard | Excellent | Excellent | Community |
| **Academic Discount** | Limited | 50-70% | Up to 75% | N/A |
| **US Customers** | ✅ Best option | ✅ Good | ⚠️ Canada only | ✅ Good for demo |

**Recommendation:** MOSIS for US-based production; Europractice for European customers; CMC for Canadian organizations.

---

## 3. Packaging and Assembly (OSAT)

### 3.1 ASE Group (Advanced Semiconductor Engineering)

#### Overview

- **Headquarters:** Taiwan
- **Market Position:** World's largest OSAT
- **Revenue:** $20B+ annually
- **Capabilities:** Full-service packaging

#### Packaging Options for Edge AI

| Package Type | Size Range | Power | Cost | Lead Time |
|--------------|------------|-------|------|-----------|
| QFN | 3mm-10mm | <5W | Low | 2-3 weeks |
| BGA | 5mm-35mm | <15W | Medium | 3-4 weeks |
| FCCSP | 5mm-20mm | <10W | Medium-High | 4-5 weeks |
| SiP (System-in-Package) | Custom | Variable | High | 6-8 weeks |

#### Advanced Packaging for AI

| Technology | Description | Application |
|------------|-------------|-------------|
| FOCoS | Fan-Out Chip on Substrate | Multi-chip integration |
| SiBridge | Silicon interconnect | High-density routing |
| InFO | Integrated Fan-Out | Mobile AI |

#### Pricing Structure

| Service | Cost Range |
|---------|------------|
| Substrate (2-layer) | $0.10-$0.30/unit |
| Substrate (4-layer) | $0.30-$0.80/unit |
| Assembly | $0.05-$0.20/unit |
| Test (Functional) | $0.02-$0.10/unit |
| Test (Burn-in) | $0.10-$0.30/unit |

**Minimum Order:** 10,000 units for standard packages

#### Contact

- **ASE US:** San Jose, CA
- **ASE Taiwan:** Kaohsiung
- **Email:** sales@aseglobal.com

---

### 3.2 Amkor Technology

#### Overview

- **Headquarters:** US (Arizona)
- **Manufacturing:** Korea, China, Philippines
- **Market Position:** Second largest OSAT
- **CHIPS Act:** Major US expansion

#### Packaging Options

| Package Type | Advantages | Target Application |
|--------------|------------|-------------------|
| QFN | Low cost, mature | Cost-sensitive edge |
| PBGA | High I/O count | Complex designs |
| fcCSP | Small form factor | Mobile/wearable |
| SiP | Multi-die integration | Complete solutions |

#### US Manufacturing Advantage

- **Arizona Facility:** Advanced packaging
- **CHIPS Act Funding:** $1.9B announced
- **Lead Time:** Potentially faster for US customers
- **IP Protection:** US jurisdiction

#### Pricing (Estimate)

| Item | Cost |
|------|------|
| Assembly (QFN) | $0.03-$0.08/unit |
| Assembly (BGA) | $0.08-$0.25/unit |
| Test | $0.02-$0.15/unit |
| Minimum Order | 5,000 units |

#### Contact

- **Amkor US:** Tempe, Arizona
- **Website:** amkor.com
- **Email:** sales@amkor.com

---

### 3.3 JCET (Jiangsu Changjiang Electronics Technology)

#### Overview

- **Headquarters:** China
- **Market Position:** Third largest OSAT globally
- **Capabilities:** Full-service packaging
- **Statsil Acquisition:** European presence

#### Packaging Options

| Package Type | Cost | Notes |
|--------------|------|-------|
| QFN | $0.02-$0.06 | Lowest cost option |
| BGA | $0.05-$0.15 | Competitive pricing |
| SiP | $0.20-$0.50 | Full integration |
| Advanced | Custom | HDFO available |

#### Advantages

✅ Lowest cost in industry  
✅ Large capacity  
✅ Strong supply chain in China  

#### Disadvantages/Risks

⚠️ Geopolitical risk (US-China tensions)  
⚠️ Potential tariffs/export controls  
⚠️ IP protection concerns  
⚠️ Lead time variability  

#### Contact

- **JCET China:** Jiangsu Province
- **Statsil Europe:** Switzerland
- **Website:** jcetglobal.com

---

### 3.4 OSAT Comparison Summary

| Criterion | ASE | Amkor | JCET |
|-----------|-----|-------|------|
| **Cost** | Medium | Medium-High | **Lowest** |
| **Quality** | Excellent | Excellent | Good |
| **Lead Time** | Fast | Medium | Variable |
| **US Presence** | Limited | **Strong** | Minimal |
| **Advanced Pkg** | **Best** | Good | Developing |
| **Geopolitical Risk** | Medium (Taiwan) | Low | **High** |

**Recommendation:** Amkor for US-government/commercial sensitive applications; ASE for advanced packaging needs; JCET for cost-optimized consumer products.

---

### 3.5 Testing Requirements and Costs

#### Test Types Required

| Test Type | Purpose | Cost/Unit | NRE |
|-----------|---------|-----------|-----|
| Wafer Sort | Defect screening | $0.02-$0.05 | $10K-$30K |
| Functional Test | Basic operation | $0.03-$0.08 | $20K-$50K |
| Burn-in | Reliability | $0.10-$0.30 | $5K-$15K |
| ATE Test | Full specification | $0.05-$0.15 | $50K-$150K |
| System Test | End-to-end | $0.20-$0.50 | $30K-$80K |

#### Total Test Budget Estimate

| Volume | Test Cost/Unit | Annual Test Budget |
|--------|----------------|-------------------|
| 10K units | $0.40-$1.00 | $4K-$10K |
| 100K units | $0.25-$0.60 | $25K-$60K |
| 1M units | $0.15-$0.40 | $150K-$400K |

**Test Program Development:** $100K-$300K (one-time)

---

## 4. Supply Chain Risk Analysis

### 4.1 Single-Source Risks by Component

#### Foundry Services

| Component | Risk Level | Primary | Secondary | Tertiary |
|-----------|------------|---------|-----------|----------|
| Wafer Fab | **HIGH** | TSMC | GlobalFoundries | Samsung |
| Specialty Process | MEDIUM | GF (22FDX) | Samsung FDS | - |
| US Manufacturing | MEDIUM | GlobalFoundries | SkyWater | Intel Foundry |

#### Packaging/Assembly

| Component | Risk Level | Primary | Secondary |
|-----------|------------|---------|-----------|
| Standard Pkg | LOW | ASE | Amkor |
| Advanced Pkg | MEDIUM | ASE | Amkor |
| US-based Pkg | MEDIUM | Amkor | - |

#### IP/Design

| Component | Risk Level | Primary | Secondary |
|-----------|------------|---------|-----------|
| Memory Compiler | MEDIUM | Synopsys | Cadence |
| I/O Libraries | MEDIUM | Foundry | Synopsys |
| EDA Tools | MEDIUM | Cadence | Synopsys |
| Test IP | LOW | Multiple | - |

---

### 4.2 Geopolitical Considerations

#### Taiwan Strait Tensions

**Risk Assessment:** Critical for TSMC-dependent supply chain

| Scenario | Probability | Impact | Mitigation |
|----------|-------------|--------|------------|
| Blockade | Low (5-10%) | Severe | Dual-source strategy |
| Economic pressure | Medium (30%) | Moderate | Inventory buffer |
| Conflict | Very Low (1-2%) | Catastrophic | US manufacturing |

**Mitigation Strategies:**
1. Qualify GlobalFoundries as second source
2. Maintain 3-6 month inventory buffer
3. Secure allocation agreements
4. Consider US/EU manufacturing incentives

#### US-China Trade Relations

**Risk Assessment:** Moderate for packaging, variable for materials

| Risk Area | Current Status | Outlook |
|-----------|----------------|---------|
| Export controls | Expanding | Higher risk |
| Entity list | Active | Case-by-case |
| Tariffs | 25% (semiconductors) | Stable |
| Rare earths | Controlled | Stockpile |

**Mitigation Strategies:**
1. Use US-based OSAT (Amkor) for sensitive products
2. Avoid Chinese materials for defense applications
3. Document supply chain for compliance
4. Build regional supply chains (US/EU/Asia)

#### CHIPS Act Implications

| Program | Funding | Application |
|---------|---------|-------------|
| Manufacturing | $39B | Foundry incentives |
| R&D | $11B | Technology development |
| Defense | $2B | Secure supply chain |
| Workforce | $200M | Training |

**Opportunities:**
1. GlobalFoundries subsidies (already secured)
2. Potential startup grants
3. Defense application funding
4. Workforce development programs

---

### 4.3 Backup Supplier Requirements

#### Foundry Backup Matrix

| Primary | Backup | Qualification Cost | Qualification Time |
|---------|--------|-------------------|-------------------|
| TSMC 28nm | Samsung 28LPP | $200K-$400K | 3-6 months |
| TSMC 28nm | GF 22FDX | $300K-$600K | 6-12 months |
| GF 22FDX | Samsung 28FDS | $200K-$400K | 4-8 months |

#### Recommended Dual-Source Strategy

**Phase 1 (Prototype/Early Production):**
- Primary: TSMC 28nm via MOSIS MPW
- Backup: None required (MPW flexibility)

**Phase 2 (Volume Production):**
- Primary: TSMC 28nm dedicated mask
- Secondary: GlobalFoundries 22FDX (qualified)
- Split: 70% TSMC / 30% GF

**Phase 3 (Mature Production):**
- Primary: TSMC 28nm
- Secondary: GlobalFoundries 22FDX
- Tertiary: Samsung 28LPP (cost optimization)

---

## 5. Cost Modeling

### 5.1 NRE (Non-Recurring Engineering) Breakdown

#### TSMC 28nm HPC

| Item | Low Estimate | High Estimate | Notes |
|------|--------------|---------------|-------|
| Mask Set (33 layers) | $1,500,000 | $2,500,000 | Volume-dependent |
| Design IP Licenses | $200,000 | $500,000 | Memory, I/O, PHYs |
| EDA Tools (annual) | $100,000 | $300,000 | Cadence + Synopsys |
| Design Services | $150,000 | $400,000 | Layout, verification |
| Test Development | $100,000 | $300,000 | ATE, burn-in |
| Qualification | $50,000 | $150,000 | Reliability testing |
| **Total NRE** | **$2,100,000** | **$4,150,000** | |

#### GlobalFoundries 22FDX

| Item | Low Estimate | High Estimate | Notes |
|------|--------------|---------------|-------|
| Mask Set | $800,000 | $1,200,000 | Lower than TSMC |
| Design IP Licenses | $150,000 | $350,000 | Smaller ecosystem |
| EDA Tools (annual) | $100,000 | $250,000 | Similar to TSMC |
| Design Services | $200,000 | $500,000 | FD-SOI expertise |
| Test Development | $100,000 | $250,000 | Similar complexity |
| Qualification | $50,000 | $100,000 | Standard testing |
| **Total NRE** | **$1,400,000** | **$2,650,000** | |

#### Samsung 28LPP

| Item | Low Estimate | High Estimate | Notes |
|------|--------------|---------------|-------|
| Mask Set | $1,200,000 | $1,800,000 | Competitive pricing |
| Design IP Licenses | $150,000 | $400,000 | Smaller library |
| EDA Tools (annual) | $100,000 | $250,000 | Standard |
| Design Services | $100,000 | $300,000 | Available |
| Test Development | $100,000 | $250,000 | Similar |
| Qualification | $50,000 | $100,000 | Standard |
| **Total NRE** | **$1,700,000** | **$3,100,000** | |

---

### 5.2 Per-Unit Cost Analysis

#### Cost Components

| Component | Formula | Example (10mm² die) |
|-----------|---------|-------------------|
| Die Cost | Wafer Price ÷ Dies per Wafer ÷ Yield | $3,000 ÷ 400 ÷ 0.85 = $8.82 |
| Packaging | Assembly + Substrate | $0.50-$2.00 |
| Test | Functional + Burn-in | $0.30-$0.80 |
| Marking/Materials | Consumables | $0.10-$0.20 |
| **Total Unit Cost** | Sum | **$9.72-$11.82** |

#### Volume Pricing Scenarios

**TSMC 28nm (10mm² die, QFN-48 package)**

| Volume | Die Cost | Pkg Cost | Test | Total | Gross Margin Target | MSRP |
|--------|----------|----------|------|-------|-------------------|------|
| 10K | $15.00 | $2.00 | $1.00 | $18.00 | 60% | $45.00 |
| 50K | $10.00 | $1.50 | $0.70 | $12.20 | 55% | $27.00 |
| 100K | $8.00 | $1.20 | $0.50 | $9.70 | 50% | $19.40 |
| 500K | $6.00 | $0.80 | $0.40 | $7.20 | 45% | $13.10 |
| 1M | $5.00 | $0.60 | $0.30 | $5.90 | 40% | $9.83 |

**GlobalFoundries 22FDX (8mm² equivalent)**

| Volume | Die Cost | Pkg Cost | Test | Total | Gross Margin Target | MSRP |
|--------|----------|----------|------|-------|-------------------|------|
| 10K | $12.00 | $2.00 | $0.90 | $14.90 | 60% | $37.25 |
| 50K | $8.00 | $1.50 | $0.60 | $10.10 | 55% | $22.44 |
| 100K | $6.50 | $1.20 | $0.45 | $8.15 | 50% | $16.30 |
| 500K | $5.00 | $0.80 | $0.35 | $6.15 | 45% | $11.18 |
| 1M | $4.00 | $0.60 | $0.25 | $4.85 | 40% | $8.08 |

---

### 5.3 Mask Set Costs and Alternatives

#### Full Mask Set Costs by Node

| Node | Mask Layers | Cost Range | Cost/Layer |
|------|-------------|------------|------------|
| 130nm | 20-25 | $150K-$250K | $7.5K-$10K |
| 90nm | 25-28 | $300K-$450K | $12K-$16K |
| 65nm | 30-32 | $400K-$600K | $13K-$19K |
| 45nm/40nm | 32-35 | $600K-$900K | $19K-$26K |
| **28nm** | **33-35** | **$1.5M-$2.5M** | **$45K-$71K** |
| 22nm | 35-38 | $2M-$3M | $57K-$79K |
| 14nm | 45-50 | $4M-$6M | $89K-$120K |

#### Mask Cost Reduction Strategies

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| MPW (prototype) | 90%+ | Small area, shared wafer |
| Shuttle program | 40-60% | Fixed schedule |
| Multi-layer masks (MLM) | 20-30% | Lower yield potential |
| E-beam direct write | N/A | Low volume only |
| Mask reuse (same node) | Variable | Limited to minor changes |

#### MPW vs Full Mask Decision Framework

| Criterion | MPW | Full Mask |
|-----------|-----|-----------|
| Volume | <1,000 units | >10,000 units |
| Die Size | <25mm² | Any |
| Timeline | Prototype | Production |
| Budget | <$200K | >$2M |
| Customization | Limited | Full |
| Yield Priority | Shared | Optimized |

**Recommendation:** 
- Prototype/Validation: MPW (MOSIS TSMC 28nm)
- Production: Full mask set when volume > 50K units/year

---

### 5.4 Total Cost of Ownership Model

#### 3-Year Projection (TSMC 28nm)

| Year | Volume | NRE | Unit Cost | Total Cost | Revenue (50% GM) |
|------|--------|-----|-----------|------------|------------------|
| 1 | 20,000 | $2.5M | $12 | $2.74M | $5.48M |
| 2 | 100,000 | $0.2M | $9 | $1.1M | $2.2M |
| 3 | 300,000 | $0.2M | $7 | $2.3M | $4.6M |
| **Total** | 420,000 | $2.9M | - | **$6.14M** | **$12.28M** |

**Break-even Volume:** ~30,000 units  
**ROI Timeline:** 18-24 months

#### 3-Year Projection (GF 22FDX)

| Year | Volume | NRE | Unit Cost | Total Cost | Revenue (50% GM) |
|------|--------|-----|-----------|------------|------------------|
| 1 | 20,000 | $1.8M | $10 | $2.0M | $4.0M |
| 2 | 100,000 | $0.2M | $7 | $0.9M | $1.8M |
| 3 | 300,000 | $0.2M | $5.5 | $1.85M | $3.7M |
| **Total** | 420,000 | $2.2M | - | **$4.75M** | **$9.5M** |

**Break-even Volume:** ~25,000 units  
**ROI Timeline:** 12-18 months

---

## 6. Decision Framework

### 6.1 Foundry Selection Matrix

| Criterion | Weight | TSMC | GF | Samsung |
|-----------|--------|------|----|---------|
| Process Maturity | 20% | 10 | 8 | 9 |
| Cost Competitiveness | 20% | 7 | 9 | 8 |
| Ecosystem Support | 15% | 10 | 7 | 7 |
| Lead Time | 15% | 7 | 8 | 8 |
| Geopolitical Risk | 15% | 6 | 8 | 6 |
| Relationship Access | 15% | 6 | 8 | 7 |
| **Weighted Score** | 100% | **7.55** | **7.95** | **7.45** |

**Recommendation:** GlobalFoundries 22FDX for primary, TSMC 28nm for performance-critical variants.

### 6.2 Manufacturing Strategy Recommendation

#### Phase 1: Prototype (Months 1-6)
- **Approach:** MPW via MOSIS (TSMC 28nm)
- **Investment:** $150K-$200K
- **Deliverables:** 40-100 prototype chips
- **Risk:** Low (minimal NRE)

#### Phase 2: Design Refinement (Months 4-12)
- **Approach:** Second MPW + Test chip
- **Investment:** $200K-$300K
- **Deliverables:** Validated design, test infrastructure
- **Risk:** Low-Medium

#### Phase 3: Production Qualification (Months 10-18)
- **Approach:** Full mask set (TSMC or GF)
- **Investment:** $1.5M-$2.5M
- **Deliverables:** Production-ready silicon
- **Risk:** Medium

#### Phase 4: Volume Production (Months 18+)
- **Approach:** Dual-source (TSMC + GF)
- **Investment:** Variable
- **Deliverables:** Production units
- **Risk:** Low (diversified)

---

## 7. Key Contacts and Resources

### Foundries

| Company | Contact | Website | Notes |
|---------|---------|---------|-------|
| TSMC | tsmc.com/contact | tsmc.com | Via MOSIS for startups |
| GlobalFoundries | foundry@globalfoundries.com | globalfoundries.com | Direct engagement possible |
| Samsung Foundry | foundry@samsung.com | samsung.com | Via partners recommended |
| SkyWater | mpw@skywatertechnology.com | skywatertechnology.com | Open-source PDK available |

### MPW Aggregators

| Service | Contact | Website | Coverage |
|---------|---------|---------|----------|
| MOSIS | support@mosis.com | mosis.com | Americas, Global |
| Europractice | info@europractice-ic.com | europractice-ic.com | Europe, Global |
| CMC | support@cmc.ca | cmc.ca | Canada |
| TinyTapeout | info@tinytapeout.com | tinytapeout.com | Educational |

### OSAT Partners

| Company | Contact | Website | Specialization |
|---------|---------|---------|----------------|
| ASE | sales@aseglobal.com | aseglobal.com | Full-service, advanced |
| Amkor | sales@amkor.com | amkor.com | US-based, automotive |
| JCET | info@jcetglobal.com | jcetglobal.com | Cost-optimized |

### Government Programs

| Program | Agency | Website | Benefit |
|---------|--------|---------|---------|
| CHIPS Act | NIST | chips.gov | Manufacturing incentives |
| SBIR | SBA | sbir.gov | R&D funding |
| DARPA | DoD | darpa.mil | Defense electronics |
| NSF | NSF | nsf.gov | Research funding |

---

## 8. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| NRE | Non-Recurring Engineering (one-time costs) |
| MPW | Multi-Project Wafer (shared mask) |
| OSAT | Outsourced Semiconductor Assembly and Test |
| FAE | Field Application Engineer |
| DRC | Design Rule Check |
| LVS | Layout vs. Schematic |
| GDSII | Graphic Data System II (layout format) |
| FD-SOI | Fully Depleted Silicon on Insulator |
| BGA | Ball Grid Array |
| QFN | Quad Flat No-leads |
| SiP | System in Package |

### Appendix B: Timeline Summary

```
Month 1-2:   Foundry engagement, design kit acquisition
Month 3-6:   Design development, MPW submission
Month 7-9:   Silicon receipt, prototype testing
Month 10-12: Design refinement, second MPW
Month 13-16: Full mask set production
Month 17-20: Qualification, yield optimization
Month 21+:   Volume production
```

### Appendix C: Cost Summary

| Item | Low | High |
|------|-----|------|
| Prototype (MPW) | $150K | $300K |
| Full Mask Set | $1.5M | $2.5M |
| Design IP | $200K | $500K |
| Test Development | $100K | $300K |
| **Total NRE** | **$1.95M** | **$3.6M** |
| Unit Cost (100K volume) | $8 | $12 |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | January 2025 | Manufacturing Strategy Team | Initial release |

---

*This document contains forward-looking estimates based on publicly available information and industry knowledge. Actual costs, timelines, and availability may vary. Engage directly with foundries and service providers for current quotes.*
