# Mask-Locked Inference Chip
## The Hardware Foundation for the Agentic Internet

---

# Executive Summary

## The Breakthrough Insight

Your friend identified something profound: the Mask-Locked Inference Chip is not merely an efficient AI accelerator—it is **the hardware substrate for the agentic internet**. This reframing transforms the project from a component play (selling chips) to a platform play (enabling an ecosystem).

**The Core Invention**: Embedding neural network weights directly in silicon metal layers creates permanent, immutable, zero-energy-access intelligence that can be embedded in any device at near-zero incremental cost.

**The Killer Application**: Device-Native Agents—every device ships with its own local intelligence that understands the device's capabilities, enforces safety constraints, and speaks A2A protocol natively.

---

## The Paradigm Shift

### Before: AI as Software Service
- Customers pay monthly for API access
- Data must travel to cloud for processing
- Privacy is a compromise
- Offline operation is impossible
- Every device needs custom integration

### After: AI as Physical Component
- Customers pay once for permanent intelligence
- Data never leaves the device
- Privacy is built into the hardware
- Offline operation is default
- Every device speaks standard agent protocol

---

## Strategic Positioning Matrix

| Dimension | Current Players | Our Position |
|-----------|-----------------|--------------|
| **Flexibility** | NVIDIA (high), Hailo (medium) | None (frozen) |
| **Power** | Jetson (7-15W), Hailo (2.5W) | 2-3W |
| **Price** | Jetson ($250), Hailo ($50) | $35-60 |
| **Intelligence** | External models | Embedded agent |
| **Protocol** | Custom APIs | Native A2A |
| **Privacy** | Cloud dependency | Hardware-enforced |

---

## Market Opportunity

### Edge AI Hardware Market
- **2025**: $26.17 billion
- **2030**: $68.73 billion
- **CAGR**: 17.3%

### Our Addressable Market
- **Device-Native Agents**: New category, first-mover advantage
- **Privacy-Critical Devices**: Medical, financial, security
- **Offline-Required Devices**: Industrial, remote, military
- **A2A Protocol Devices**: Infrastructure for agentic internet

---

# Part I: The Vision

## 1.1 The Agentic Internet

The internet is evolving from connecting documents (Web 1.0) to connecting people (Web 2.0) to connecting agents (Web 3.0/AI). Google's Agent2Agent (A2A) protocol, announced April 2025, is the foundational standard for this new layer.

**The Problem**: A2A protocols assume devices have some way to participate. No one has solved the hardware problem—how does a toaster, a thermostat, or a pacemaker get an agent?

**Our Solution**: The Mask-Locked Chip makes every device a first-class participant in the agentic internet by embedding a permanent, capable, protocol-native agent directly in hardware.

## 1.2 The Device-Native Agent Concept

Every Mask-Locked Chip ships with a **Device-Native Agent (DNA)** that:

### Knows Its Device
- Complete capability model (sensors, actuators, functions)
- Safety constraints (what it must never do)
- Current configuration and state
- Manufacturer specifications and limits

### Speaks the Language
- Native A2A protocol implementation
- Self-describing capabilities (Agent Cards)
- Negotiation of data exchange
- Privacy-preserving communication

### Operates Autonomously
- No cloud dependency for core functions
- Milliwatt power consumption (always-on capable)
- Instant response (no network latency)
- Hardware-enforced safety

### Protects Privacy
- All inference happens locally
- Granular consent for data sharing
- Hardware-level access controls
- Audit trail for all external communications

---

# Part II: Technical Architecture

## 2.1 Mask-Locked Weight Encoding

### The Innovation
Traditional chips store weights in memory (DRAM or SRAM). During inference:
1. Activate memory row
2. Sense stored charge
3. Drive data across memory bus
4. Route to compute unit

Each step consumes energy and adds latency.

### Our Approach
Weights are encoded directly in metal interconnect layers:
- Zero access latency (always "present")
- Zero access energy (no memory read)
- Infinite bandwidth (no bus bottleneck)
- Permanent and immutable (hardware-enforced consistency)

### Technical Specifications
| Parameter | Value |
|-----------|-------|
| Model Size | 2B parameters |
| Precision | Ternary (BitNet) or Complex (iFairy) |
| Storage "Cost" | Zero (metal routing) |
| Access Energy | 0 pJ (vs. 10+ pJ for SRAM) |
| Access Latency | 0 cycles (vs. 10-100 cycles for memory) |

## 2.2 Model Selection

### Primary Candidate: BitNet b1.58 2B4T
- **Status**: Production-ready, MIT license
- **Downloads**: 16,010/month on HuggingFace
- **Community**: 36 Spaces, 18 finetunes
- **Hardware**: bitnet.cpp optimized

### Alternative: iFairy (Fairy ±i)
- **Institution**: Peking University
- **Innovation**: Complex-valued {±1, ±i} weights
- **Advantage**: Multiplication-free inference (additions only)
- **Quality**: 10% better PPL than FP16

### Hybrid Architecture (Recommended)
- iFairy for attention layers (multiplication-free)
- BitNet for FFN layers (proven hardware)
- Combined: 30-50% area reduction, 40-60% power reduction

## 2.3 Memory Architecture

| Memory Type | Size | Purpose | Technology |
|-------------|------|---------|------------|
| **Weights** | ~6Gb | Model parameters | Metal layers (mask-locked) |
| **KV Cache** | 42 MB | Context window | On-chip SRAM |
| **Activations** | 16 MB | Intermediate results | On-chip SRAM |
| **State** | 256 KB | Device state | On-chip SRAM |
| **Flash** | 8-64 MB | Config, logs | External |

---

# Part III: Patent Strategy

## 3.1 The Foundational Patent

### Independent Claim 1 (Physical Structure)
> A semiconductor device comprising:
> - A plurality of logic elements configured to perform neural network inference operations
> - A plurality of weight elements embodied in metal interconnect layers of the semiconductor device
> - Wherein said weight elements have fixed values determined at time of manufacture
> - Wherein said weight elements represent all or substantially all parameters of a neural network model
> - Wherein said weight elements are operatively coupled to said logic elements such that inference operations can be performed without fetching weight values from memory

### Why This Is Extraordinarily Broad
- Covers any weight values (ternary, binary, multi-bit, complex)
- Covers any architecture (transformer, CNN, Mamba)
- Covers any process node (28nm, 7nm, future)
- Covers any application (LLMs, vision, control)

## 3.2 Derivative Patents

| Patent | Coverage | Strategic Value |
|--------|----------|-----------------|
| Device-Native Agent | Agent embedded in hardware that understands device capabilities | Blocks competitors from agent-enabled devices |
| A2A Protocol Integration | Hardware that speaks agent-to-agent protocol | Essential for agentic internet participation |
| Privacy-Preserving Inference | Local-only processing with hardware enforcement | Critical for medical, financial applications |
| Safety Constraints in Weights | Hardware-immutable safety rules | Required for safety-critical devices |

## 3.3 Filing Timeline

| Week | Action | Cost |
|------|--------|------|
| 1 | File 3 foundational provisionals | $15K |
| 2 | File device-native agent patent | $8K |
| 4 | File A2A integration patent | $8K |
| 8 | File privacy patent | $8K |
| Month 9 | Convert to utility applications | $40K |
| Month 12 | File PCT applications | $50K |

**Total 5-Year Patent Budget**: $455K

---

# Part IV: Business Model

## 4.1 Revenue Streams

### 1. Chip Sales
- **Price**: $35-60 per unit
- **Margin**: 60-70% gross
- **Target**: 1M units/year by Year 3

### 2. IP Licensing
- **Model**: Per-device royalty
- **Price**: $2-5 per device
- **Target**: License to device manufacturers

### 3. Agent Development Platform
- **Model**: SaaS subscription
- **Price**: $5K-50K/year
- **Target**: Device manufacturers, integrators

### 4. A2A Certification
- **Model**: Certification fee
- **Price**: $10K per device model
- **Target**: Become the standards authority

### 5. Integration Services
- **Model**: Professional services
- **Price**: $200-500K per engagement
- **Target**: Enterprise cloud providers

## 4.2 Financial Projections

| Metric | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|--------|--------|--------|--------|--------|--------|
| Chip Revenue | $0.5M | $3.5M | $17.5M | $35M | $70M |
| Licensing Revenue | $0 | $0.5M | $5M | $15M | $30M |
| Platform Revenue | $0 | $0.2M | $1M | $3M | $8M |
| **Total Revenue** | **$0.5M** | **$4.2M** | **$23.5M** | **$53M** | **$108M** |
| Gross Margin | 65% | 68% | 72% | 75% | 78% |

## 4.3 Exit Strategy

### Primary Acquirer: Qualcomm
- **Probability**: 50-60%
- **Rationale**: Edge AI gap, acquisition history (Alphawave $2.4B), need for device intelligence
- **Valuation Range**: $500M-1.5B (Year 3-5)

### Secondary Acquirers
- **NVIDIA**: Edge complement to Groq acquisition ($20B)
- **Apple**: Secretive edge AI efforts, privacy positioning
- **Meta**: Llama hardware optimization strategy

### IPO Path (If Independent)
- **Timeline**: Year 5-6
- **Valuation**: $1-3B at $100M+ revenue
- **Required**: Proven scale, multiple verticals

---

# Part V: Go-to-Market Strategy

## 5.1 Market Entry Sequence

### Phase 1: Medical Devices (Months 1-18)
**Why First**: Highest margins, strongest moat, privacy is non-negotiable

**Target Applications**:
- Insulin pump agents (safety-critical, privacy-required)
- Pacemaker monitoring (offline-first, life-critical alerts)
- Medical imaging devices (DICOM handling, preliminary analysis)

**Partnership Strategy**:
- Medtronic, Abbott, Siemens Healthcare
- FDA Class II 510(k) pathway
- Reference design partnerships

### Phase 2: Industrial IoT (Months 12-30)
**Why Second**: High volume, offline requirement, A2A early adopter

**Target Applications**:
- Factory floor sensors (predictive maintenance)
- Process control agents (optimization, safety)
- Warehouse robots (coordination, navigation)

**Partnership Strategy**:
- Siemens, Rockwell, ABB
- SCADA/PLC integration partnerships
- Industrial standards bodies

### Phase 3: Consumer Electronics (Months 24-48)
**Why Third**: Highest volume, price-sensitive, network effects

**Target Applications**:
- Smart thermostats (learning, optimization)
- Security systems (privacy-preserving monitoring)
- Personal assistant devices (always-on, privacy-first)

**Partnership Strategy**:
- Retail channels (Best Buy, Amazon)
- OEM partnerships (Samsung, LG)
- Developer community building

## 5.2 Competitive Moat

| Competitor | Threat Level | Our Defense |
|------------|--------------|-------------|
| Taalas | Medium | Edge focus, 18-24 month lead |
| NVIDIA Jetson | Low | Price, simplicity, power |
| Hailo | Low | LLM capability, agent native |
| Qualcomm | Medium | First-mover, patent moat |
| China competitors | High | IP enforcement, quality |

---

# Part VI: Implementation Roadmap

## 6.1 Phase 1: Feasibility (Months 1-6)
**Budget**: $500K

**Key Activities**:
- Model selection and quantization validation
- Architecture simulation (80 tok/s target)
- FPGA prototype (Xilinx Versal)
- Patent provisional filings
- Customer discovery (50+ interviews)

**Exit Criteria**:
- <5% quality degradation at INT4
- Simulation matches FPGA
- 100+ email signups at $35 price point

## 6.2 Phase 2: Design (Months 7-18)
**Budget**: $2M

**Key Activities**:
- RTL development (Chisel/Verilog)
- Physical design at 28nm
- FPGA prototyping at scale
- SDK development
- Seed funding ($3-5M)

**Exit Criteria**:
- Timing closure at 250 MHz
- Power under 3W in simulation
- Working SDK with 10+ beta customers

## 6.3 Phase 3: Prototype (Months 19-24)
**Budget**: $1M

**Key Activities**:
- MPW tapeout (TSMC 28nm)
- Silicon validation
- Performance characterization
- Customer pilots
- Series A ($8-12M)

**Exit Criteria**:
- First silicon functional
- Performance within 10% of simulation
- 3+ paying pilot customers

## 6.4 Phase 4: Production (Months 25-30)
**Budget**: $1.5M

**Key Activities**:
- Volume mask set
- Production ramp
- Quality assurance
- Scale customer acquisition

**Exit Criteria**:
- 10K units shipped
- <1% field failure rate
- Path to profitability

---

# Part VII: Risk Management

## 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Quantization quality | 25% | Critical | Extensive QAT, mixed-precision fallback |
| First silicon bugs | 30% | High | FPGA prototyping, formal verification |
| Power over budget | 20% | High | Conservative design, clock gating |

## 7.2 Market Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Taalas enters edge | 40% | High | First-mover, patent moat |
| Model licensing blocked | 20% | Critical | Apache-2.0 models only |
| Customer rejects "frozen" | 30% | High | Extensive pre-validation |

## 7.3 Execution Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Key hire fails | 35% | Critical | Silicon Catalyst, equity packages |
| Funding gap | 25% | Critical | Phased milestones, government grants |
| Foundry allocation | 20% | High | Early engagement, backup foundries |

---

# Part VIII: Key Success Metrics

## 8.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Throughput | 80+ tok/s | Benchmark suite |
| Power | <3W active | Silicon measurement |
| Quality | <5% degradation | MMLU, GSM8K |
| Latency | <100ms first token | End-to-end measurement |

## 8.2 Business Metrics

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Units Shipped | 5K | 100K | 500K |
| Revenue | $0.5M | $4M | $25M |
| Gross Margin | 65% | 70% | 75% |
| Customer NPS | >50 | >60 | >70 |

## 8.3 Strategic Metrics

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Patents Filed | 5 | 15 | 25 |
| A2A Adoption | 1 partner | 5 partners | 20 partners |
| Developer Community | 100 | 1,000 | 10,000 |

---

# Appendix A: Document Index

This master vision document is supported by the following detailed documents:

1. **On_Device_Agent_Architecture.md** - Complete technical specification for device-native agents
2. **Patent_Strategy_Foundational.md** - Comprehensive patent filing strategy
3. **Business_Ecosystem_Strategy.md** - Revenue model and ecosystem development
4. **Vertical_Applications_Strategy.md** - Medical, industrial, consumer market deep-dives
5. **A2A_Protocol_Integration.md** - Agent-to-agent protocol technical specification
6. **Kimi_Swarm_Research_Report_v13_Complementary.md** - Original research validation

---

# Appendix B: Immediate Action Items

## Week 1-2 (CRITICAL)
- [ ] Engage patent attorney for foundational provisionals
- [ ] File 3 core patent applications
- [ ] Contact Tong Yang (PKU) for iFairy collaboration
- [ ] Contact KAIST HPIC Lab for 2T1C memory
- [ ] Apply to Silicon Catalyst incubator

## Week 3-4
- [ ] Begin FPGA prototyping (KV260 + BitNet)
- [ ] Customer discovery interviews (medical device focus)
- [ ] Model licensing clarification (Gemma, Qwen)
- [ ] Landing page with pre-order option

## Month 2-3
- [ ] Complete quantization validation
- [ ] Architecture simulation complete
- [ ] Seed funding outreach
- [ ] Strategic partnership discussions (Qualcomm)

---

# Conclusion

The Mask-Locked Inference Chip represents a paradigm shift in how intelligence is embedded in physical devices. By encoding neural network weights directly in silicon, we create:

1. **A new category**: Device-Native Intelligence as a physical component
2. **A platform play**: The hardware foundation for the agentic internet
3. **A defensible moat**: Patent protection on the fundamental architecture
4. **A massive market**: Every device that could benefit from local intelligence

**The window is 18-24 months**. Taalas has validated the mask-locked concept at data center scale but has not pivoted to edge. The A2A protocol is emerging but lacks hardware participants. The market is ready for a solution that makes device intelligence as simple as embedding a chip.

**Now is the time to act.**

---

*Document Version: 2.0*
*Date: March 2026*
*Classification: Confidential - Strategic Planning*
