# Mask-Locked Inference Chip
## Executive Summary for Investors & Partners

**Date**: March 2026 | **Status**: Pre-Seed | **Ask**: $500K Seed

---

## The Opportunity

**Problem**: Running LLMs at the edge is prohibitively expensive. The NVIDIA Jetson Orin Nano costs $250, consumes 10-15W, and requires days of software setup. There is no affordable, plug-and-play solution for LLM inference on edge devices.

**Solution**: A mask-locked inference chip that embeds neural network weights directly in silicon. No software stack, no drivers, no memory bottleneck. Plug it in, get AI output.

**Market**: Edge AI chip market growing from $3.67B (2025) to $11.54B (2030).

---

## Key Metrics

| Metric | Our Product | Nearest Competitor |
|--------|-------------|-------------------|
| **Price** | $35-60 | $88 (Hailo) / $250 (Jetson) |
| **Power** | 2-3W | 5-15W |
| **Throughput** | 80-150 tok/s | 5-30 tok/s |
| **Setup Time** | Zero | Days |
| **Tokens/Watt** | 27-50 | 1-2 |

---

## Technical Breakthrough

### Innovation #1: Multiplication-Free Inference

Using iFairy complex weights {±1, ±i}, matrix multiplication becomes permutation:
- No multipliers needed
- 95% gate reduction vs. FP16
- 0.1 pJ per operation (vs. 5-10 pJ)

### Innovation #2: On-Chip KV Cache

Sliding window attention fits KV cache in 21 MB on-chip SRAM:
- Eliminates external memory bottleneck
- Removes bandwidth constraint
- Reduces power by 50%+

### Innovation #3: Mask-Locked Weights

Weights encoded in metal interconnect:
- Zero weight access energy
- Infinite bandwidth
- True plug-and-play

---

## Competitive Moat

| Advantage | Sustainability |
|-----------|----------------|
| iFairy architecture | 2-3 years (patents pending) |
| On-chip KV cache | 12-18 months (first-mover) |
| Price/efficiency | Ongoing (process advantage) |
| Zero-setup | Unique (fixed-function) |

**Competitor Analysis**: Taalas ($219M raised) targets data center, not edge. No edge signals detected. Window: 12-18 months.

---

## Financial Model

### Unit Economics

| Item | Cost |
|------|------|
| Die (28nm, 40 mm²) | $2-3 |
| Packaging + Test | $3-5 |
| COGS (on-chip only) | $5-8 |
| COGS (with LPDDR4) | $15-19 |
| Target ASP | $35-60 |
| Gross Margin | 60-80% |

### 5-Year Projection

| Year | Units | Revenue | Gross Profit |
|------|-------|---------|--------------|
| 1 | 5K | $175K | $140K |
| 2 | 50K | $1.75M | $1.4M |
| 3 | 200K | $7M | $5.6M |
| 4 | 500K | $17.5M | $14M |
| 5 | 1M | $35M | $28M |

---

## Funding Requirements

### Seed Round: $500K (Month 1-6)

**Use of Funds**:
- Architecture lead: $150K
- ML engineer: $100K
- FPGA prototype: $50K
- Patent filing: $50K
- Tools/infrastructure: $50K
- Runway buffer: $100K

**Milestones**:
- Gate 0: FPGA prototype at 25 tok/s
- 5 customer LOIs
- Provisional patents filed

### Series A: $3M (Month 7-18)

**Use of Funds**:
- Complete design team
- MPW tapeout
- Production preparation

---

## Exit Potential

| Acquirer | Rationale | Estimated Value |
|----------|-----------|-----------------|
| Qualcomm | Edge AI portfolio | $150-300M |
| NVIDIA | Complement Groq acquisition | $200-400M |
| Apple | On-device AI strategy | $250-500M |
| Intel | Edge inference | $150-300M |

**Reference**: NVIDIA paid $20B for Groq (cloud inference). Edge inference is the next frontier.

---

## Team Requirements

| Role | Status | Priority |
|------|--------|----------|
| Architecture Lead | Open | CRITICAL |
| ML Engineer | Open | HIGH |
| RTL Designer | Open | HIGH |
| Physical Design | Open | MEDIUM |
| Verification | Open | MEDIUM |

**Note**: Open to hiring experienced consultants for Gate 0-1.

---

## Risk Summary

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Technical failure | 20% | FPGA prototype validates approach |
| Competition | 25% | 18-month first-mover window |
| Funding gap | 25% | Government grants, SBIR |
| Market rejection | 30% | Customer validation before silicon |

**Overall Success Probability**: 35-40% (typical for semiconductor startups)

---

## The Ask

We are seeking **$500K in seed funding** to complete Gate 0 (FPGA prototype) and Gate 1 (architecture freeze). This de-risks the technical approach before committing to the $2-3M MPW tapeout.

**Investor Profile**: Hardware-focused VCs, semiconductor incubators, strategic corporate investors.

**Timeline to Revenue**: 18-24 months (after production silicon).

---

## Contact

**Next Steps**: Schedule technical deep-dive, review FPGA prototype plan, discuss term sheet.

---

*This summary is confidential and intended for qualified investors only.*
