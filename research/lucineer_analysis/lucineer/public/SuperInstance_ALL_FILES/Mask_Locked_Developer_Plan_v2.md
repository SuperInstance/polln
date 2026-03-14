# Mask-Locked Inference Chip: Developer Execution Plan v2.0
## Comprehensive Implementation Roadmap & Execution Guide

**Document Classification:** Technical Execution - Confidential  
**Version:** 2.0 (Master Synthesis)  
**Date:** March 2026  
**Prepared For:** Engineering Team, Project Management, Operations

---

# Executive Overview

This developer execution plan provides a comprehensive implementation roadmap for the mask-locked inference chip, synthesizing all technical and strategic research from Cycles 1 and 2. The plan is structured around a milestone-gated approach with clear deliverables and decision points.

## Project Overview

| Parameter | Specification |
|-----------|--------------|
| **Target Model** | BitNet b1.58-2B-4T or iFairy 2B |
| **Target Throughput** | 80-150 tokens/second |
| **Target Power** | 2-3W active |
| **Target Price** | $35-60 retail |
| **Target Process** | TSMC 28nm HPC |
| **Total Timeline** | 24-30 months |
| **Total Budget** | $2.0M - $3.5M |

---

# Part 1: Project Organization

## 1.1 Team Structure

### Core Team (Phase 1: Months 1-6)

| Role | Count | Key Responsibilities | Cost/Year |
|------|-------|---------------------|-----------|
| **Architecture Lead** | 1 | System architecture, technical decisions, performance modeling | $250K |
| **ML Engineer** | 1 | Model quantization, training/fine-tuning, accuracy validation | $180K |
| **RTL Designer** | 1 | Verilog/Chisel development, microarchitecture, simulation | $200K |
| **Project Manager** | 0.5 | Schedule, vendor coordination, risk management | $100K (50%) |

**Phase 1 Total:** ~$365K/year

### Extended Team (Phase 2: Months 7-18)

| Role | Count | Key Responsibilities | Cost/Year |
|------|-------|---------------------|-----------|
| **Architecture Lead** | 1 | (continuing) | $250K |
| **ML Engineer** | 2 | (add 1 for iFairy evaluation) | $360K |
| **RTL Designers** | 2 | (add 1 for verification) | $400K |
| **Physical Design Lead** | 1 | Synthesis, P&R, timing closure | $220K |
| **Verification Engineer** | 1 | Testbenches, formal verification | $170K |
| **Software Engineer** | 1 | Driver, SDK, host tools | $150K |
| **Project Manager** | 1 | Full-time | $150K |

**Phase 2 Total:** ~$1.7M/year

## 1.2 Governance Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      Board of Directors                     │
│                  (Quarterly Review, Major Decisions)        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Technical Advisory Board                 │
│           (Architecture Review, Risk Assessment)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Project Steering Committee               │
│     (Founder, Architecture Lead, Project Manager)           │
│                  (Monthly Review)                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │ Hardware │    │ Software │    │ ML/AI    │
     │   Team   │    │   Team   │    │   Team   │
     └──────────┘    └──────────┘    └──────────┘
```

## 1.3 Decision Framework

| Decision Type | Authority | Review Frequency |
|---------------|-----------|------------------|
| **Technical Architecture** | Architecture Lead + Founder | Monthly |
| **Budget < $50K** | Founder | Ad-hoc |
| **Budget > $50K** | Steering Committee | Monthly |
| **Milestone Gate** | Steering Committee + Advisory | Per milestone |
| **Hiring Decisions** | Founder | Ad-hoc |
| **IP/Patent Strategy** | Founder + Legal | Monthly |

---

# Part 2: Milestone-Gated Development Roadmap

## 2.1 Overview

```
Month:  │ 1-2 │ 3-4 │ 5-6 │ 7-8 │ 9-10 │ 11-12 │ 13-15 │ 16-18 │ 19-21 │ 22-24 │
        ├─────┴─────┴─────┴─────┴──────┴───────┴───────┴───────┴───────┴───────┤
        │  GATE 0   │   GATE 1   │    GATE 2    │    GATE 3    │   GATE 4     │
        │  FPGA     │   RTL      │    MPW       │   Production│   Volume     │
        │  Prototype│   Freeze   │    Tapeout   │   Validation│   Ramp       │
        └───────────┴────────────┴──────────────┴─────────────┴──────────────┘
```

## 2.2 Gate 0: FPGA Prototype (Months 1-6)

### Objective
Validate ternary inference on AMD KV260, achieving 25+ tok/s at <5W.

### Milestones

| Milestone | Week | Deliverable | Success Criteria |
|-----------|------|-------------|------------------|
| **G0.1: Environment Setup** | 1-2 | Development environment ready | Toolchain installed, KV260 bootable |
| **G0.2: TLMM Core Design** | 3-6 | TLMM PE module verified | 250 MHz timing closure |
| **G0.3: Weight Extraction** | 7-8 | BitNet weights extracted | COE files for first layer |
| **G0.4: Systolic Array** | 9-12 | 16×16 array operational | Simulated 50+ tok/s |
| **G0.5: KV Cache** | 13-16 | 2K context KV cache | Memory verified |
| **G0.6: Integration** | 17-20 | Full pipeline on FPGA | 25+ tok/s measured |
| **G0.7: Power Validation** | 21-24 | Power measurement complete | <5W confirmed |

### Budget Allocation

| Category | Amount |
|----------|--------|
| **Personnel (6 months)** | $180K |
| **Hardware (KV260, tools)** | $5K |
| **Consultants** | $20K |
| **Travel/Meetings** | $5K |
| **Contingency (10%)** | $21K |
| **Gate 0 Total** | **$231K** |

### Go/No-Go Criteria

| Criteria | Threshold | Measurement |
|----------|-----------|-------------|
| **Throughput** | ≥25 tok/s | Benchmark suite |
| **Power** | ≤5W | Power meter |
| **Quality** | <5% MMLU degradation | Benchmark suite |
| **Stability** | 1 hour continuous run | Stress test |

## 2.3 Gate 1: RTL Freeze (Months 7-12)

### Objective
Complete RTL design ready for synthesis, with comprehensive verification.

### Milestones

| Milestone | Week | Deliverable | Success Criteria |
|-----------|------|-------------|------------------|
| **G1.1: Architecture Refinement** | 25-28 | Final architecture spec | Reviewed and approved |
| **G1.2: RTL Implementation** | 29-36 | Complete RTL code | 100% code coverage |
| **G1.3: Weight Integration Tools** | 37-40 | Weight-to-Verilog pipeline | Tested on multiple models |
| **G1.4: Functional Verification** | 41-44 | Testbench complete | 100% functional coverage |
| **G1.5: Formal Verification** | 45-48 | Critical paths proven | No deadlocks/livelocks |
| **G1.6: FPGA Re-validation** | 49-52 | Updated FPGA prototype | Match Gate 0 performance |

### Budget Allocation

| Category | Amount |
|----------|--------|
| **Personnel (6 months)** | $500K |
| **EDA Tools (if not free)** | $50K |
| **Consultants** | $30K |
| **Legal (patent filings)** | $40K |
| **Contingency (10%)** | $62K |
| **Gate 1 Total** | **$682K** |

## 2.4 Gate 2: MPW Tapeout (Months 13-18)

### Objective
Successful MPW tapeout with functional silicon samples.

### Milestones

| Milestone | Week | Deliverable | Success Criteria |
|-----------|------|-------------|------------------|
| **G2.1: Synthesis** | 53-56 | Gate-level netlist | Timing met |
| **G2.2: Floorplanning** | 57-60 | Physical design started | Area within budget |
| **G2.3: Place & Route** | 61-66 | Layout complete | DRC/LVS clean |
| **G2.4: Timing Closure** | 67-70 | Final timing | All corners met |
| **G2.5: Tapeout Submission** | 71-72 | GDSII submitted | Deadline met |
| **G2.6: Silicon Receipt** | 90-96 | MPW chips received | 10+ good samples |

### Budget Allocation

| Category | Amount |
|----------|--------|
| **Personnel (6 months)** | $500K |
| **MPW Shuttle** | $200K |
| **Physical Design Tools** | $100K (if needed) |
| **Consultants** | $50K |
| **Contingency (15%)** | $128K |
| **Gate 2 Total** | **$978K** |

## 2.5 Gate 3: Production Validation (Months 19-24)

### Objective
Validated production silicon ready for volume manufacturing.

### Milestones

| Milestone | Week | Deliverable | Success Criteria |
|-----------|------|-------------|------------------|
| **G3.1: Silicon Bring-up** | 97-100 | Basic functionality | Chip powers on |
| **G3.2: Functional Test** | 101-104 | Full test suite pass | 100% features verified |
| **G3.3: Performance Characterization** | 105-108 | Specs confirmed | All specs met |
| **G3.4: Reliability Testing** | 109-112 | Reliability report | Pass all tests |
| **G3.5: Production Mask Order** | 113-116 | Full mask commitment | Order placed |
| **G3.6: Production Ramp** | 117-120 | First production lot | 1000+ units |

### Budget Allocation

| Category | Amount |
|----------|--------|
| **Personnel (6 months)** | $500K |
| **Full Mask Set** | $1.2M |
| **Test Development** | $100K |
| **Packaging/Assembly** | $50K |
| **Contingency (15%)** | $278K |
| **Gate 3 Total** | **$2.13M** |

---

# Part 3: Detailed Technical Implementation

## 3.1 FPGA Prototype Implementation

### Platform Selection

| Platform | LUTs | BRAM | Price | Recommendation |
|----------|------|------|-------|----------------|
| **AMD KV260** | 117K | 135 | $199 | ✅ **Primary** |
| **ZCU104** | 274K | 312 | $895 | Secondary backup |
| **ZCU102** | 600K | 630 | $1,995 | High-end backup |

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│              FPGA Development Environment                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vivado     │  │   PYNQ       │  │   Vitis AI   │      │
│  │   MLSD       │  │   Framework  │  │   (Optional) │      │
│  │   (Free)     │  │   (Free)     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Target Design                      │   │
│  │  ┌─────────────┐  ┌─────────────────────────────┐   │   │
│  │  │  TLMM Core  │  │  Weight Manager (BRAM/DDR) │   │   │
│  │  │  (Verilog)  │  │  (Streaming from DDR)      │   │   │
│  │  └─────────────┘  └─────────────────────────────┘   │   │
│  │  ┌─────────────┐  ┌─────────────────────────────┐   │   │
│  │  │  KV Cache   │  │  Layer Controller          │   │   │
│  │  │  (BRAM)     │  │  (FSM)                     │   │   │
│  │  └─────────────┘  └─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Weight Extraction Pipeline

```python
# Weight extraction for BitNet to FPGA BRAM
import numpy as np
import torch
from transformers import AutoModelForCausalLM

def extract_ternary_weights(model_path: str, output_dir: str):
    """Extract ternary weights from BitNet model."""
    model = AutoModelForCausalLM.from_pretrained(model_path)
    
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() >= 2:
            weights = param.detach().cpu().numpy()
            
            # AbsMean quantization to {-1, 0, +1}
            scale = np.mean(np.abs(weights)) + 1e-8
            quantized = np.round(weights / scale)
            ternary = np.clip(quantized, -1, 1).astype(np.int8)
            
            # Pack 4 weights per byte (2 bits each)
            packed = pack_ternary_weights(ternary)
            
            # Generate BRAM initialization file
            generate_coe_file(packed, name, output_dir)
            
    return output_dir

def pack_ternary_weights(ternary: np.ndarray) -> np.ndarray:
    """Pack ternary weights efficiently."""
    # Encoding: 00 = -1, 01 = 0, 10 = +1
    flat = ternary.flatten()
    packed = np.zeros((len(flat) + 3) // 4, dtype=np.uint8)
    
    for i, val in enumerate(flat):
        code = { -1: 0b00, 0: 0b01, 1: 0b10 }[val]
        byte_idx = i // 4
        bit_pos = (i % 4) * 2
        packed[byte_idx] |= (code << bit_pos)
    
    return packed
```

## 3.2 RTL Design Guidelines

### Coding Standards

1. **Use Chisel/Scala for parameterization**
   - Single codebase for 1B/3B/7B variants
   - Generate Verilog for synthesis

2. **Clock Domain Crossing**
   - Single clock domain preferred
   - Use asynchronous FIFOs if multiple clocks needed

3. **Reset Strategy**
   - Synchronous reset preferred
   - Single reset signal distribution

4. **Naming Conventions**
   - `_n` for active-low signals
   - `_q` for registered signals
   - `_d` for next-state signals

### Module Hierarchy

```
mask_locked_chip_top
├── weight_rom_controller
│   └── weight_rom_bank[N]
├── compute_engine
│   ├── systolic_array[N×M]
│   │   └── processing_element
│   └── accumulator
├── activation_sram
│   ├── kv_cache
│   └── activation_buffer
├── layer_controller
└── io_interface
    ├── usb_controller
    └── axi_lite_slave
```

## 3.3 Verification Strategy

### Testbench Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Testbench Structure                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Test Sequencer                       │   │
│  │  ├── Directed Tests (Functional)                     │   │
│  │  ├── Random Tests (Corner Cases)                     │   │
│  │  └── Regression Tests (CI/CD)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   DUT Wrapper                         │   │
│  │  ├── Clock/Reset Generation                          │   │
│  │  ├── Interface Drivers (USB/AXI)                     │   │
│  │  └── Monitor/Scoreboard                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Golden Model (Python)                   │   │
│  │  ├── BitNet inference reference                      │   │
│  │  ├── Bit-exact output comparison                     │   │
│  │  └── Tolerance handling (floating point)              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Coverage Goals

| Coverage Type | Target |
|---------------|--------|
| **Code Coverage** | 100% |
| **Functional Coverage** | 100% |
| **Toggle Coverage** | 95% |
| **FSM Coverage** | 100% |

---

# Part 4: Manufacturing Strategy

## 4.1 Foundry Selection

### TSMC 28nm HPC

| Attribute | Value |
|-----------|-------|
| **Mask Cost** | $1.2M - $1.8M |
| **Wafer Price** | $3,500 - $4,500 |
| **Yield (mature)** | 85-92% |
| **Lead Time** | 10-14 weeks |
| **IP Ecosystem** | Excellent |
| **Allocation** | Through MOSIS broker |

### MPW Shuttle Schedule (2026)

| Shuttle | Deadline | Delivery | Status |
|---------|----------|----------|--------|
| **T28-2603** | May 10 | Aug 10 | Target |
| **T28-2604** | Jul 5 | Oct 5 | Backup |
| **T28-2605** | Aug 30 | Nov 30 | Final backup |

## 4.2 Packaging Options

| Package | Cost | Thermal | Pin Count | Recommendation |
|---------|------|---------|-----------|----------------|
| **QFN-64** | $0.15 | Poor | 64 | Development |
| **BGA-256** | $0.50 | Good | 256 | ✅ **Production** |
| **USB Module** | $1.00 | Good | N/A | Consumer version |

## 4.3 Test Strategy

| Test Type | Cost/Unit | Coverage |
|-----------|-----------|----------|
| **Wafer Sort** | $0.05-0.15 | Structural |
| **Functional Test** | $0.10-0.30 | Functional |
| **Burn-in** | $0.20-0.50 | Reliability |
| **Final Test** | $0.10-0.25 | System |

**Total Test Cost:** ~$0.50-1.20/unit

---

# Part 5: Software Stack

## 5.1 SDK Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Application                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 superinstance SDK                    │   │
│  │  ├── Device Management                              │   │
│  │  ├── Model Loading (N/A - fixed model)              │   │
│  │  ├── Tokenization                                   │   │
│  │  └── Inference Control                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   USB Driver                         │   │
│  │  ├── libusb (cross-platform)                        │   │
│  │  └── Native OS drivers                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│                    USB 3.0 Cable                            │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Mask-Locked Chip                       │   │
│  │  (Fixed Model - No Software Stack Needed)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 5.2 API Design

```python
# superinstance SDK API Design
from superinstance import Device, Tokenizer, Generator

# Initialize device
device = Device()  # Auto-detect USB device
tokenizer = Tokenizer("bitnet-2b")

# Simple inference
prompt = "What is the capital of France?"
tokens = tokenizer.encode(prompt)
output_tokens = device.generate(tokens, max_length=100)
output_text = tokenizer.decode(output_tokens)

# Streaming inference
for token in device.generate_stream(tokens):
    print(tokenizer.decode([token]), end="", flush=True)
```

---

# Part 6: Risk Mitigation Plan

## 6.1 Technical Risk Mitigation

| Risk | Mitigation | Owner | Trigger |
|------|------------|-------|---------|
| **Quantization quality** | Mixed-precision fallback | ML Lead | >3% MMLU degradation |
| **FPGA timing failure** | Pipeline stages | Arch Lead | <200 MHz achieved |
| **Memory bandwidth** | Weight prefetching | RTL Lead | Throughput <20 tok/s |
| **First-silicon bugs** | Debug infrastructure | Arch Lead | Post-silicon |

## 6.2 Schedule Risk Mitigation

| Risk | Mitigation | Owner | Trigger |
|------|------------|-------|---------|
| **Team gaps** | Contractor pool | Founder | Position unfilled >30 days |
| **Tool issues** | Open-source backup | RTL Lead | Tool delay >1 week |
| **MPW schedule** | Multiple shuttle targets | PM | Miss primary deadline |

## 6.3 Budget Contingency

| Gate | Base Budget | Contingency | Total |
|------|-------------|-------------|-------|
| **Gate 0** | $210K | $21K (10%) | $231K |
| **Gate 1** | $620K | $62K (10%) | $682K |
| **Gate 2** | $850K | $128K (15%) | $978K |
| **Gate 3** | $1.85M | $278K (15%) | $2.13M |
| **Total** | $3.53M | $489K | **$4.02M** |

---

# Part 7: Quality Metrics

## 7.1 Code Quality Metrics

| Metric | Target | Tool |
|--------|--------|------|
| **RTL Code Coverage** | 100% | Verilator |
| **Lint Warnings** | 0 | Verilator |
| **CDC Violations** | 0 | Custom script |
| **Synthesis Warnings** | 0 | Yosys |

## 7.2 Performance Metrics

| Metric | Gate 0 Target | Production Target |
|--------|---------------|-------------------|
| **Throughput** | 25 tok/s | 80-150 tok/s |
| **Power** | <5W | <3W |
| **TTFT (128 tokens)** | <500ms | <200ms |
| **Quality (MMLU)** | <5% degradation | <2% degradation |

## 7.3 Process Quality Metrics

| Metric | Target |
|--------|--------|
| **Yield (MPW)** | >70% |
| **Yield (Production)** | >85% |
| **DPPM** | <100 |
| **Field Returns** | <0.1% |

---

# Part 8: Appendices

## 8.1 Development Environment Setup

```bash
# FPGA Development Environment
# Ubuntu 22.04 LTS

# Install Vivado MLSD (Free)
# Download from AMD Xilinx website

# Install PYNQ
pip install pynq

# Install Verilator
sudo apt install verilator

# Install Yosys
sudo apt install yosys

# Install Python dependencies
pip install torch transformers numpy
```

## 8.2 Key Contacts

| Role | Contact | Purpose |
|------|---------|---------|
| **TSMC MPW (MOSIS)** | info@mosis.com | MPW shuttle coordination |
| **Silicon Catalyst** | apply@siliconcatalyst.com | Incubator application |
| **PKU (iFairy)** | tongyang@pku.edu.cn | Technology partnership |
| **TeLLMe Authors** | Via arXiv | Technical questions |

## 8.3 Reference Documents

| Document | Location |
|----------|----------|
| **BitNet Model Card** | huggingface.co/microsoft/bitnet-b1.58-2B-4T |
| **TeLLMe Paper** | arXiv:2510.15926 |
| **iFairy Paper** | arXiv:2508.05571 |
| **OpenROAD Docs** | openroad-flow-scripts.readthedocs.io |

---

*Document Classification: Technical Execution - Confidential*  
*Version: 2.0 (Master Synthesis)*  
*Sources: Cycles 1-2 Research, Industry Best Practices*  
*Distribution: Engineering Team, Project Management, Operations*
