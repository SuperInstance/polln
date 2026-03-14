# Implementation Roadmap
## Mask-Locked Inference Chip Development Gates

**Document Version**: Final 1.0
**Date**: March 2026

---

# Overview

This document defines the four development gates required to bring the mask-locked inference chip from concept to production. Each gate has specific deliverables, success criteria, and budget requirements.

---

# Gate 0: FPGA Prototype (Month 1-3)

## Objective
Validate the arithmetic architecture and power estimates on FPGA before committing to silicon.

## Deliverables

| Item | Description | Success Criteria |
|------|-------------|------------------|
| RAU Implementation | iFairy RAU in Verilog/Chisel | Synthesizes at 250 MHz |
| FPGA Demo | KV260 running BitNet/iFairy | 25 tok/s minimum |
| Power Measurement | Actual vs. estimated | Within 2× of estimate |
| Quality Benchmark | MMLU, GSM8K vs. bitnet.cpp | Within 5% of baseline |
| Technical Report | Architecture decisions | Complete documentation |

## Budget: $50,000

| Item | Cost |
|------|------|
| Architecture consultant | $25,000 |
| ML engineer (contract) | $15,000 |
| Hardware & tools | $5,000 |
| Contingency | $5,000 |

## Key Technical Decisions

1. **Model Selection**: Verify iFairy 700M/1.3B vs BitNet 2B quality
2. **KV Strategy**: Test sliding window sizes (256, 512, 1024)
3. **Precision**: Validate INT4 vs INT8 for KV cache
4. **Array Size**: Confirm 32×32 systolic is sufficient

## Exit Criteria
- [ ] Working FPGA demo
- [ ] Quality within 5% of baseline
- [ ] Power estimate validated
- [ ] 5 customer LOIs collected

---

# Gate 1: Architecture Freeze (Month 4-6)

## Objective
Finalize all design decisions and complete pre-silicon validation.

## Deliverables

| Item | Description | Success Criteria |
|------|-------------|------------------|
| Cycle-Accurate Simulator | Full chip model | Matches FPGA within 10% |
| Power Analysis | PrimeTime results | <3W at 80 tok/s |
| Synthesis Report | Gate count, timing | Timing met at 250 MHz |
| Floorplan | Initial placement | Area < 50 mm² |
| Patent Applications | Provisional filed | 3+ applications |

## Budget: $100,000

| Item | Cost |
|------|------|
| RTL Designer | $40,000 |
| Verification Engineer | $30,000 |
| EDA Tools (Synopsys) | $15,000 |
| Patent Attorney | $15,000 |

## Key Technical Decisions

1. **Final Die Size**: Confirm < 50 mm²
2. **Memory Configuration**: On-chip only vs. external LPDDR4
3. **I/O Interface**: USB 3.0 vs. PCIe vs. M.2
4. **Package Selection**: BGA size, thermal considerations

## Exit Criteria
- [ ] Architecture frozen
- [ ] Simulation validates targets
- [ ] Patents filed
- [ ] 15 customer LOIs

---

# Gate 2: MPW Tapeout (Month 7-12)

## Objective
Produce first silicon and validate in hardware.

## Deliverables

| Item | Description | Success Criteria |
|------|-------------|------------------|
| GDSII Files | Complete layout | DRC clean, LVS clean |
| MPW Submission | TSMC 28nm shuttle | Accepted for fabrication |
| Silicon Samples | 20-40 units | Functional at specification |
| Test Report | Characterization data | Within 20% of targets |
| Customer Samples | Beta testing | 5+ customers testing |

## Budget: $150,000

| Item | Cost |
|------|------|
| MPW Slot (TSMC 28nm) | $50,000 |
| Design Services | $40,000 |
| Packaging | $20,000 |
| Test Development | $25,000 |
| Contingency | $15,000 |

## Key Milestones

| Week | Milestone |
|------|-----------|
| 1-8 | Physical design complete |
| 9-12 | Tapeout submitted |
| 13-20 | Fabrication |
| 21-24 | Packaging, bring-up |
| 25-28 | Characterization |

## Exit Criteria
- [ ] First silicon functional
- [ ] Performance within 20% of target
- [ ] 30 customer LOIs
- [ ] Series A term sheet received

---

# Gate 3: Production (Month 13-18)

## Objective
Scale to volume manufacturing and customer shipments.

## Deliverables

| Item | Description | Success Criteria |
|------|-------------|------------------|
| Full Mask Set | Production masks | Qualified at foundry |
| Production Test | ATE program | >95% yield |
| Datasheet | Complete specs | Published |
| SDK/API | Software interface | Developer-ready |
| Volume Shipments | First 1000 units | Shipped to customers |

## Budget: $2,000,000

| Item | Cost |
|------|------|
| Full Mask Set (28nm) | $1,500,000 |
| Production Setup | $200,000 |
| Inventory | $200,000 |
| Marketing/Sales | $100,000 |

## Key Milestones

| Month | Milestone |
|-------|-----------|
| 13-14 | Mask fabrication |
| 15-16 | First production wafers |
| 17 | Qualification complete |
| 18 | Volume shipments begin |

## Exit Criteria
- [ ] Production qualified
- [ ] 1000+ units shipped
- [ ] $100K+ revenue
- [ ] Path to profitability defined

---

# Risk Mitigation Per Gate

## Gate 0 Risks

| Risk | Mitigation |
|------|------------|
| FPGA resources insufficient | Use larger device or simplify |
| Quality too low | Adjust quantization, try mixed precision |
| Power higher than expected | Identify bottleneck, optimize |

## Gate 1 Risks

| Risk | Mitigation |
|------|------------|
| Timing not met | Reduce clock, pipeline more |
| Area too large | Reduce SRAM, simplify control |
| Power too high | Aggressive clock gating |

## Gate 2 Risks

| Risk | Mitigation |
|------|------------|
| Silicon non-functional | Debug infrastructure, redundant paths |
| Performance off-target | Characterize, plan respin |
| Yield issues | Conservative design rules |

## Gate 3 Risks

| Risk | Mitigation |
|------|------------|
| Yield too low | Redundant structures, binning |
| Customer adoption slow | Developer support, reference designs |
| Competition emerges | Accelerate roadmap, file patents |

---

# Go/No-Go Decision Framework

## Gate 0 → Gate 1

| Criterion | Threshold |
|-----------|-----------|
| Quality vs baseline | >95% |
| FPGA throughput | >25 tok/s |
| Power estimate | <5W |
| Customer interest | 5+ LOIs |

## Gate 1 → Gate 2

| Criterion | Threshold |
|-----------|-----------|
| Simulated throughput | >50 tok/s |
| Simulated power | <3W |
| Die size | <50 mm² |
| Customer interest | 15+ LOIs |

## Gate 2 → Gate 3

| Criterion | Threshold |
|-----------|-----------|
| Silicon functional | Yes |
| Measured throughput | >80 tok/s |
| Measured power | <3W |
| Series A funding | Secured |

---

# Resource Requirements

## Team Size by Gate

| Role | Gate 0 | Gate 1 | Gate 2 | Gate 3 |
|------|--------|--------|--------|--------|
| Architecture Lead | 1 | 1 | 1 | 1 |
| ML Engineer | 1 | 1 | 1 | 1 |
| RTL Designer | 0 | 2 | 2 | 2 |
| Physical Design | 0 | 1 | 2 | 2 |
| Verification | 0 | 1 | 1 | 1 |
| Software | 0 | 0 | 1 | 2 |
| Operations | 0 | 0 | 0 | 1 |

## Total Headcount: 1 → 5 → 8 → 10

---

# Success Metrics Summary

| Metric | Gate 0 | Gate 1 | Gate 2 | Gate 3 |
|--------|--------|--------|--------|--------|
| Throughput | 25+ tok/s | 50+ tok/s | 80+ tok/s | 100+ tok/s |
| Power | <5W | <3W (sim) | <3W | <2.5W |
| Quality (MMLU) | 50%+ | 52%+ | 52%+ | 52%+ |
| Customer LOIs | 5 | 15 | 30 | 50+ |
| Pre-orders | 0 | 100 | 500 | 5000+ |
| Revenue | $0 | $0 | $25K | $500K+ |

---

*Roadmap is conservative. Acceleration possible if resources allow.*
