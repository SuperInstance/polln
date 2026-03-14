# Raspberry Pi HAT AI Accelerator - Component Pricing Research

## Executive Summary

This document provides realistic, grounded pricing estimates for manufacturing a Raspberry Pi HAT form-factor AI accelerator board with a custom 28nm ASIC (2B parameters, mask-locked). All pricing is based on industry-standard cost models, public disclosures, and typical foundry/memory vendor pricing as of 2024-2025.

---

## 1. 28nm ASIC Die Pricing

### 1.1 MPW (Multi-Project Wafer) Costs

**Source Grounding**: MPW pricing is well-documented through shuttle services like MOSIS, CMP, and direct foundry quotes.

| Foundry | Node | MPW Price (per run) | Dies Included | Effective $/mm² |
|---------|------|---------------------|---------------|-----------------|
| **TSMC** | 28nm HPM | $250,000 - $400,000 | ~50-100 dies (depends on design size) | $15-25/mm² |
| **GlobalFoundries** | 22FDX (FD-SOI) | $150,000 - $250,000 | ~50-100 dies | $10-18/mm² |
| **SMIC** | 28nm Poly/SiON | $100,000 - $180,000 | ~50-100 dies | $8-15/mm² |

**Key Sources**:
- MOSIS MPW pricing schedule (publicly available)
- CMP (French multi-project service) published rates
- SkyWater/Google open-source shuttle pricing (180nm reference: ~$15K, scales with node)

### 1.2 Typical Die Size for 2B Parameter Mask-Locked Chip

**Calculations** (based on published AI accelerator specs):

| Parameter | Value | Source |
|-----------|-------|--------|
| Parameters | 2B | Spec requirement |
| INT8 MAC units needed | ~500-1000 | Based on Eyeriss v2, NVDLA sizing |
| SRAM for weights (partial) | 2-4 MB | On-chip weight cache |
| Die size estimate | **25-40 mm²** | Scaling from comparable designs |

**Comparable chips**:
- Google Edge TPU (28nm): ~30 mm² (4 TOPS INT8)
- Hailo-8 (7nm): Not directly comparable but ~20 mm²
- Kendryte K210 (28nm RISC-V + AI): ~25 mm²

**Realistic estimate: 30-35 mm²** for a 2B parameter mask-locked accelerator at 28nm.

### 1.3 Yield Assumptions at 28nm

| Factor | Value | Source |
|--------|-------|--------|
| Defect density (D0) | 0.4-0.6 defects/cm² | TSMC 28nm mature process |
| Raw yield (Murphy model) | 85-92% | For 30-35 mm² die |
| After repair/redundancy | 90-95% | Typical for mature node |
| Test yield | 95-98% | After wafer sort |

**Yield formula** (simplified Murphy model):
```
Yield = (1 - e^(-D0 × A / 2)) / (D0 × A / 2)
For A = 35 mm² = 0.35 cm², D0 = 0.5:
Yield ≈ 91.5%
```

### 1.4 Per-Die Cost at Different Volumes

**Assumptions**:
- 300mm wafer
- Die size: 35 mm²
- Dies per wafer (gross): ~580
- Net dies per wafer (after yield): ~530

| Volume | Mask Set Cost | Wafer Price | Per-Die Cost | Notes |
|--------|--------------|-------------|--------------|-------|
| **100 units** | $1.2-1.8M (amortized) | $2,500-3,500 | **$12,000-18,000** | MPW or shared mask |
| **1K units** | $1.2-1.8M (amortized) | $2,500-3,500 | **$1,500-2,500** | Dedicated mask |
| **10K units** | $1.2-1.8M (amortized) | $2,000-3,000 | **$250-400** | Volume wafer discount |
| **100K units** | $1.2-1.8M (amortized) | $1,500-2,200 | **$40-70** | Full production pricing |

**Mask Set Costs at 28nm**:
- Full mask set: $1.2M - $1.8M (TSMC)
- Half-node shuttle: $400K - $800K
- Layer reduction possible: ~$800K for 28nm with fewer metal layers

**Sources**:
- IC Knowledge LLC cost model
- TSMC public earnings calls (wafer ASP references)
- Semiengineering.com cost articles

---

## 2. Memory Pricing

### 2.1 LPDDR4/LPDDR4X Pricing

**Source Grounding**: Spot prices from Digi-Key, Mouser, and distributor quotes. Volume pricing from OEM negotiations.

| Capacity | Type | Package | 1K Price | 10K Price | 100K Price |
|----------|------|---------|----------|-----------|------------|
| **512MB (4Gb)** | LPDDR4 | Discrete FBGA | $1.80-2.50 | $1.40-1.90 | $1.10-1.50 |
| **512MB (4Gb)** | LPDDR4X | Discrete FBGA | $2.00-2.80 | $1.50-2.10 | $1.20-1.60 |
| **1GB (8Gb)** | LPDDR4 | Discrete FBGA | $3.20-4.50 | $2.50-3.50 | $2.00-2.80 |
| **1GB (8Gb)** | LPDDR4X | Discrete FBGA | $3.50-5.00 | $2.80-4.00 | $2.20-3.20 |

**Major Vendors**:
| Vendor | Part Number Example | Notes |
|--------|---------------------|-------|
| Micron | MT53E512M32D2NP | LPDDR4X, 512MB |
| Samsung | KMDP6001DA-B425 | LPDDR4X, 512MB |
| SK Hynix | H9HCNNNCPMULXR | LPDDR4X, 512MB |

**Sources**:
- Digi-Key pricing (checked for Micron MT53 series)
- Octopart price history
- Memory spot market reports (DRAMeXchange, now TrendForce)

### 2.2 Package-on-Package (PoP) vs Discrete Memory Costs

| Configuration | Cost Premium | Notes |
|---------------|--------------|-------|
| **Discrete BGA** | Baseline | Standard PCB mounting |
| **PoP (Memory on top)** | +15-25% | Requires PoP-compatible package |
| **SiP (Integrated)** | +30-50% | Custom integration, higher NRE |

**PoP-specific costs**:
- PoP-capable substrate: +$0.50-1.00 vs standard
- Assembly complexity: +$0.20-0.40 per unit
- Yield impact: -2-5%

**Recommendation**: For HAT form factor, **discrete memory** is more cost-effective and simpler. PoP is typically used for smartphones where space is critical.

### 2.3 Volume Discounts

| Volume | Discount from 1K |
|--------|------------------|
| 1K | Baseline |
| 10K | 20-30% |
| 100K | 35-45% |
| 1M+ | 45-55% |

---

## 3. PCB and Assembly

### 3.1 4-Layer PCB Pricing (HAT Size: 65x56mm)

**Source Grounding**: PCB manufacturer quotes (JLCPCB, PCBWay, Seeed Studio, US fabs)

| Manufacturer | Location | 100 pcs | 1K pcs | 10K pcs |
|--------------|----------|---------|--------|---------|
| **JLCPCB** | China | $0.80-1.20/pc | $0.50-0.80/pc | $0.30-0.50/pc |
| **PCBWay** | China | $1.00-1.50/pc | $0.60-0.90/pc | $0.40-0.60/pc |
| **Seeed Studio** | China | $1.20-1.80/pc | $0.70-1.00/pc | $0.45-0.70/pc |
| **US Fab (avg)** | USA | $5.00-8.00/pc | $3.00-5.00/pc | $1.50-3.00/pc |

**4-layer specs**:
- FR-4, 1.6mm thickness
- 1oz copper outer, 0.5oz inner
- ENIG finish (for BGA)
- Green soldermask, white silkscreen

### 3.2 SMT Assembly Costs

| Service | Cost Model | Notes |
|---------|------------|-------|
| **Pick & Place setup** | $20-50 per SMT part | One-time NRE |
| **Stencils** | $20-50 | One-time |
| **Assembly labor** | $0.02-0.05 per component | Volume dependent |
| **Reflow** | $0.10-0.30 per board | |
| **AOI test** | $0.05-0.15 per board | |
| **Functional test** | $0.20-0.50 per board | Custom fixture needed |

**Total Assembly Cost Estimate**:
| Volume | Per-Board Assembly |
|--------|-------------------|
| 100 pcs | $3.00-5.00 |
| 1K pcs | $1.50-2.50 |
| 10K pcs | $0.80-1.50 |
| 100K pcs | $0.50-1.00 |

**Sources**:
- JLCPCB SMT assembly calculator
- PCBWay assembly pricing page
- MacroFab instant quote tool

### 3.3 Connector Costs

| Component | Qty | 1K Price | 10K Price | Source |
|-----------|-----|----------|-----------|--------|
| **40-pin GPIO header (2x20, 2.54mm)** | 1 | $0.15-0.25 | $0.08-0.15 | Digi-Key S1011E-40-ND |
| **Surface mount version** | 1 | $0.20-0.35 | $0.10-0.20 | Samtec, Harwin |
| **Thru-hole (standard)** | 1 | $0.10-0.20 | $0.05-0.12 | Generic |

**Additional HAT hardware**:
- Standoffs/spacers: $0.10-0.30 per set
- Screws: $0.02-0.05 each

---

## 4. Packaging

### 4.1 Plastic QFN/BGA Package Costs

**Source Grounding**: OSAT (Outsourced Semiconductor Assembly and Test) pricing from ASE, Amkor, SPIL

| Package Type | Pin Count | 1K Price | 10K Price | 100K Price |
|--------------|-----------|----------|-----------|------------|
| **QFN-48** | 48 | $0.08-0.12 | $0.05-0.08 | $0.03-0.05 |
| **QFN-64** | 64 | $0.10-0.15 | $0.06-0.10 | $0.04-0.06 |
| **BGA-256** | 256 | $0.35-0.50 | $0.25-0.35 | $0.15-0.25 |
| **BGA-484** | 484 | $0.50-0.80 | $0.35-0.50 | $0.20-0.35 |

**For 30-35mm² AI accelerator**:
- Likely needs BGA-256 to BGA-484 for I/O density
- Estimate: **$0.20-0.40 per unit at volume**

### 4.2 Leadframe Pricing

| Material | Price per unit (10K+) | Notes |
|----------|----------------------|-------|
| **Copper alloy** | $0.02-0.05 | QFN leadframes |
| **Alloy 42** | $0.03-0.06 | BGA substrates |
| **Organic substrate** | $0.10-0.25 | BGA, finer pitch |

**Wire bonding** (included in assembly):
- Gold wire: $0.01-0.03 per wire
- Copper wire: $0.005-0.015 per wire
- Typical chip: 50-200 wires

---

## 5. Certification

### 5.1 FCC Part 15 Class B Test Lab Costs

**Source Grounding**: FCC-listed test lab quotes (UL, TÜV, Intertek, NTS)

| Service | Cost | Timeline |
|---------|------|----------|
| **Pre-scan/consultation** | $500-1,500 | 1-2 days |
| **Full EMC testing (Class B)** | $5,000-15,000 | 3-5 days |
| **Report preparation** | $1,000-2,500 | 3-5 days |
| **FCC filing (SDOC)** | $0-500 | Self-declaration |
| **FCC filing (Certification)** | $1,000-3,000 | Via TCB |

**Total FCC Class B**: **$6,500-19,000**

**Notes**:
- SDoC (Supplier's Declaration of Conformity) is now common for Class B digital devices
- Certification via TCB (Telecommunication Certification Body) required for intentional radiators
- WiFi/Bluetooth modules require separate certification

### 5.2 CE Marking Costs

| Service | Cost | Timeline |
|---------|------|----------|
| **EMC testing (EU standards)** | $3,000-8,000 | 2-4 days |
| **LVD testing (if applicable)** | $1,500-4,000 | 2-3 days |
| **Technical documentation** | $500-2,000 | 1-2 weeks |
| **Declaration of Conformity** | Self-declaration | - |
| **Notified Body (optional)** | $2,000-5,000 | If required |

**Total CE Marking**: **$5,000-19,000** (can share EMC data with FCC if tests cover both)

### 5.3 Certification Timeline

| Phase | Duration |
|-------|----------|
| **Test lab scheduling** | 1-4 weeks |
| **Testing (FCC + CE)** | 1-2 weeks |
| **Report generation** | 1 week |
| **Filing/Registration** | 1-2 weeks |
| **Total** | **4-9 weeks** |

**Recommendations to reduce costs**:
1. Use pre-certified WiFi/BT modules
2. Combine FCC and CE testing at the same lab
3. Perform pre-compliance testing in-house
4. Use test labs in competitive markets (some savings with Asian labs)

---

## 6. Complete Bill of Materials

### 6.1 Target Volume: 10,000 Units

| Category | Component | Qty | Unit Cost | Total |
|----------|-----------|-----|-----------|-------|
| **ASIC** | 28nm AI accelerator die | 1 | $300.00 | $300.00 |
| **ASIC** | BGA-484 package | 1 | $0.35 | $0.35 |
| **Memory** | LPDDR4X 1GB (8Gb) | 1 | $3.00 | $3.00 |
| **Memory** | SPI Flash (boot) 64Mb | 1 | $0.40 | $0.40 |
| **Passives** | Capacitors (MLCC) | ~100 | $0.005 avg | $0.50 |
| **Passives** | Resistors | ~50 | $0.002 avg | $0.10 |
| **Power** | PMIC/DC-DC converters | 2 | $0.80 | $1.60 |
| **Power** | LDO regulators | 3 | $0.15 | $0.45 |
| **Clock** | Crystal oscillator | 1 | $0.25 | $0.25 |
| **Connector** | 40-pin GPIO header | 1 | $0.12 | $0.12 |
| **Connector** | USB-C (power/comm) | 1 | $0.30 | $0.30 |
| **Connector** | Other headers/connectors | - | - | $0.30 |
| **PCB** | 4-layer, 65x56mm | 1 | $0.50 | $0.50 |
| **Assembly** | SMT + test | 1 | $1.20 | $1.20 |
| **Thermal** | Heatsink + thermal pad | 1 | $0.40 | $0.40 |
| **Mechanical** | Standoffs, screws | 1 set | $0.15 | $0.15 |

**SUBTOTAL (COGS)**: **$309.62**

### 6.2 NRE (Non-Recurring Engineering) Costs

| Item | Cost |
|------|------|
| **28nm Mask Set** | $1,200,000 - $1,800,000 |
| **Design & Verification** | $500,000 - $1,500,000 |
| **Prototype builds** | $50,000 - $100,000 |
| **FCC + CE Certification** | $15,000 - $35,000 |
| **Test fixtures** | $20,000 - $50,000 |
| **TOTAL NRE** | **$1,785,000 - $3,485,000** |

### 6.3 Volume Pricing Summary

| Volume | Per-Unit COGS | With NRE Amortized |
|--------|---------------|-------------------|
| **100 units** | $500-700 | $18,000-35,000 |
| **1,000 units** | $350-450 | $2,100-3,500 |
| **10,000 units** | $300-350 | $480-700 |
| **100,000 units** | $150-200 | $180-250 |

*Note: NRE amortization assumes $2M total NRE*

---

## 7. Source Citations Summary

| Category | Primary Sources |
|----------|-----------------|
| **MPW/Foundry** | MOSIS.org, CMP, TSMC public data, IC Knowledge cost model |
| **Die sizing** | ISSCC papers, Hot Chips presentations (Edge TPU, NVDLA) |
| **Yield models** | Murphy model, TSMC defect density publications |
| **Memory pricing** | Digi-Key, Mouser, Octopart, TrendForce DRAM reports |
| **PCB/Assembly** | JLCPCB, PCBWay, MacroFab instant quotes |
| **Connectors** | Digi-Key, Mouser catalogs |
| **Packaging** | ASE, Amkor annual reports, OSAT pricing guides |
| **Certification** | UL, TÜV, Intertek quote data, FCC OET guidelines |

---

## 8. Risk Factors & Assumptions

### Cost Risks (Upward Pressure)
- Memory price volatility (±30% historical swings)
- Foundry capacity constraints (premium pricing)
- Currency fluctuations (most pricing in USD)
- Tariffs/import duties
- Yield issues in early production

### Cost Opportunities (Downward Pressure)
- Volume negotiations with foundry
- Design for manufacturability (DFM)
- Multi-sourcing memory suppliers
- Mature 28nm process stability
- Chinese foundry alternatives (SMIC, HLMC)

---

## 9. Recommendations

1. **Start with MPW**: Use TSMC or GlobalFoundries MPW for prototype (100-500 units) at ~$200K-300K
2. **Target 10K+ for production**: Per-unit costs become reasonable at 10K+ volume
3. **Use discrete memory**: PoP adds complexity without significant HAT benefit
4. **Pre-certify modules**: Use pre-certified WiFi/BT modules if connectivity needed
5. **Plan for 6-month NRE phase**: Design, verification, mask-making, prototype

---

*Document generated: March 2025*
*Pricing reflects Q4 2024 - Q1 2025 market conditions*
