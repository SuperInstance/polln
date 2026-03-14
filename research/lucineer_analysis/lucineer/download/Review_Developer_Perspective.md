# SuperInstance.AI: Senior Developer Technical Review
## Mask-Locked Inference Architecture Assessment

**Reviewer Profile:** 15+ years experience at Google, NVIDIA, and Apple  
**Focus:** ML inference systems, embedded systems, chip design  
**Date:** March 2026  
**Classification:** Technical Due Diligence

---

## OVERALL DEVELOPER TRUST SCORE: 5.5/10

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Technical Feasibility | 7/10 | 25% | 1.75 |
| SDK/API Design | 4/10 | 20% | 0.80 |
| Documentation Quality | 5/10 | 15% | 0.75 |
| Benchmark Methodology | 5/10 | 15% | 0.75 |
| Manufacturing Risk | 4/10 | 15% | 0.60 |
| Developer Ecosystem | 6/10 | 10% | 0.60 |
| **TOTAL** | | **100%** | **5.25/10** |

**Verdict:** Technically innovative but significant gaps in execution plan for developer adoption. The core architecture is sound, but the path from prototype to production-ready SDK is underspecified.

---

## 1. CRITICAL TECHNICAL GAPS FOUND

### 1.1 The iFairy Complex Weight Integration Risk

**What the docs claim:**
- iFairy architecture enables "multiplication-free inference" using C4 group weights {±1, ±i}
- 175-350× fewer gates than traditional MAC units
- Paper cited: arXiv:2508.05571 (Peking University)

**What's missing:**
```
CRITICAL GAP: No working reference implementation of iFairy on any hardware platform.

The TeLLMe FPGA paper (arXiv:2510.15926) validates TERNARY weights, not iFairy complex weights.
The architecture diagrams show iFairy RAUs, but:

1. Has anyone actually synthesized an iFairy layer to RTL?
2. What's the verification strategy for complex-valued attention?
3. How do you handle the imaginary component through softmax/LayerNorm?
4. Where's the SPICE-level power analysis for the RAU?
```

**Developer concern:** If iFairy fails in silicon, you fall back to standard ternary which is 2× less efficient. This is a major technical risk that could invalidate the business model.

**Required deliverable:** A working FPGA implementation of a single iFairy transformer layer before committing to ASIC.

---

### 1.2 KV Cache Architecture Reality Check

**What the docs claim:**
- 42 MB KV cache in on-chip SRAM
- 512-token sliding window + 4 attention sinks
- 2K context achievable at 25 tok/s

**Technical analysis:**
```
KV Cache Size Verification:
- 32 layers × 2560 hidden dim × 512 ctx × 2 (K+V) × 0.5 bytes (INT4)
- = 32 × 2560 × 512 × 2 × 0.5 = 41,943,040 bytes = 42 MB ✓

BUT: The math assumes INT4 KV cache quantization.

PROBLEMS:
1. INT4 KV cache degrades attention quality significantly
   - Paper reference (Liu et al.) shows 10-15% perplexity increase
   - No quantification provided in SuperInstance docs

2. SRAM area at 28nm: 42 MB × 1.5 Mbit/mm² = 224 mm²
   - This EXCEEDS the 55 mm² target die size in the specs
   - The "10 MB SRAM" in specs contradicts "42 MB KV cache"

3. No mention of KV cache prefetch/double-buffering strategy
   - At 25 tok/s, you have 40ms per token
   - KV access pattern is sequential, but needs careful scheduling
```

**Developer concern:** The KV cache numbers don't add up. Either context length is overestimated, or die size/cost is underestimated.

**Required deliverable:** Revised memory budget with:
- Area breakdown by SRAM bank
- Power per access cycle
- Bandwidth calculation at target throughput
- Quality degradation from INT4 KV quantization

---

### 1.3 Mask-Locked Weight Encoding Details

**What the docs claim:**
- Weights encoded in metal layers
- "Zero access latency, infinite bandwidth"
- 2 bits per weight using iFairy encoding

**What's missing:**
```
CRITICAL GAPS:

1. How do you route 2 billion 2-bit weights to 1024 PEs?
   - Metal routing congestion estimate: NOT PROVIDED
   - Is there a hierarchical distribution network?
   - What's the RC delay from weight "storage" to PE?

2. How do you handle weight-dependent control?
   - Ternary MAC requires conditional: add, subtract, or skip
   - The "skip" case means conditional clock gating
   - Have you verified the clock tree handles this?

3. Weight encoding during physical design:
   - Standard P&R tools expect RTL constants
   - How do you inject post-training weights at P&R time?
   - What's the flow for weight updates (for next silicon spin)?

4. Process variation tolerance:
   - Metal resistance varies ±20% across process corners
   - Does this affect weight encoding?
   - Any analysis of PVT sensitivity?
```

**Developer concern:** The mask-locking concept is elegant but the implementation details are hand-wavy. This is the core innovation—it needs silicon-proven methodology.

**Required deliverable:** 
- Physical design flow diagram showing weight injection
- RC extraction results for weight routing
- Process corner analysis

---

### 1.4 TeLLMe FPGA Reference Limitations

**What the docs claim:**
- TeLLMe validates the ternary approach
- 25 tok/s on KV260 at 4.8W
- "Scaling to 2B: LUTs 98K → 241K (doesn't fit)"

**Critical missing context:**
```
The TeLLMe paper is for BitNet 0.73B, not 2B:

MODEL SIZE GAP:
- TeLLMe: 0.73B parameters
- SuperInstance target: 2B parameters
- Scale factor: 2.7×

WHAT TECKME DIDN'T DO:
1. No KV cache optimization (offloaded to external memory)
2. LM head offloaded to ARM (9ms overhead per token)
3. Single-batch inference only
4. No continuous batching

IF YOU SCALE TO 2B:
- 2.7× more MAC operations per token
- 2.7× more weight storage
- KV cache grows from ~10MB to ~40MB
- Power scales sub-linearly but still 2-3×

THE 4.8W RESULT IS NOT REPRODUCIBLE FOR 2B:
- TeLLMe's 0.73B at 25 tok/s = 20 GOPS
- 2B at 25 tok/s = 55 GOPS
- Same KV260 can't sustain 2.7× throughput
```

**Developer concern:** The reference implementation validates architecture concepts but doesn't prove the performance claims for the target model size.

---

## 2. WHAT'S AWESOME FROM ENGINEERING VIEW

### 2.1 The Fundamental Insight is Correct

The core observation—eliminating weight memory access transforms the inference problem—is mathematically sound:

```
Energy Analysis (28nm):
- DRAM access: 100-200 pJ/bit
- SRAM access: 1-5 pJ/bit
- Hardwired metal: ~0.1 pJ/bit (capacitance only)

For 2B INT4 weights:
- DRAM fetch: 2B × 2 bits × 150 pJ = 600 mJ per inference pass
- Hardwired: 2B × 2 bits × 0.1 pJ = 0.4 mJ per inference pass
- Reduction: 1500× ✓

This is the real innovation. The math holds up.
```

### 2.2 Table-Lookup MatMul is Validated

The TLMM approach for ternary weights is proven:

```
TeLLMe results (peer-reviewed):
- LUT-based MAC: single-cycle, no DSP
- 98K LUTs for 0.73B model
- Resource utilization: 73% (realistic)

Translation to ASIC:
- LUT → dedicated gates: 5-10× area reduction
- Fixed function → no configuration overhead
- Predictable timing → simpler verification

This is good engineering that builds on proven concepts.
```

### 2.3 The Business Model Has Technical Merit

The "hardware-as-intelligence" model solves real problems:

```
From developer perspective:

PROBLEM: "I want to add AI to my device"
CURRENT SOLUTIONS:
- Jetson Orin: $250, 7-15W, weeks of CUDA setup
- Hailo-8: $70, 2.5W, CNN only, no LLM support
- Cloud API: Privacy issues, latency, recurring cost

SUPERINSTANCE VALUE PROP:
- $35-89, 2-3W, plug-and-play
- Zero setup: USB/SD card interface
- Privacy-by-design: weights never leave silicon

The market gap is real. The value proposition is clear.
```

### 2.4 Mathematical Foundation is Rigorous

The documentation includes proper theorems:

```
Theorem 1 (Ternary Reduction): ✓ Correct
- Proof is sound
- Hardware consequence is accurate

Theorem 4 (iFairy Multiplication-Free): ✓ Potentially correct
- Proof by case analysis is valid
- BUT: requires complex-valued operations not yet proven in silicon

Theorem 8 (Arithmetic Intensity): ✓ Excellent insight
- 7937× increase is correctly calculated
- Roofline analysis is sound

This is better technical documentation than most startup pitches.
```

---

## 3. WHAT'S CONCERNING FROM ENGINEERING VIEW

### 3.1 Team Credential Gaps

The deep research document on tape-out experience shows:

```
SUCCESS FACTOR: Team with 15+ combined tape-outs

CRITICAL ROLES FOR SERIES A:
| Role | Required | SuperInstance Status |
|------|----------|---------------------|
| CTO (5+ tape-outs) | Must have | NOT SPECIFIED |
| Physical Design Lead (5+ at node) | Must have | NOT SPECIFIED |
| Verification Lead (3+ full chip) | Must have | NOT SPECIFIED |

FAILURE RATE FOR FIRST-TIME TEAMS:
- First silicon functional: 30-40%
- Full respin required: 40-60%

The documentation doesn't address team composition at all.
```

**This is the #1 risk factor.** Technical architecture means nothing without execution capability.

### 3.2 Supply Chain Risks Are Severe

From the Deep Research supply chain analysis:

```
CRITICAL COMPONENT RISKS:

LPDDR4 Memory:
- Price increased 132% in 2025
- SK Hynix: 10% capacity allocation to LPDDR4
- Lead time: 16-24 weeks
- Spot price: $10-12/512MB (vs $6 assumed in COGS)

TSMC Foundry:
- 92% of advanced node capacity in Taiwan
- Geopolitical risk: 5-10% conflict probability over 5 years
- Startup access: MOSIS/Europractice only, limited allocation

The $21 COGS estimate assumes stable pricing.
Reality: Memory alone could add $10-15 to unit cost.
```

### 3.3 SDK/API Design Is Underspecified

**What developers actually need:**

```
MISSING FROM DOCUMENTATION:

1. Software Stack Architecture
   - Host driver for USB/SPI interface?
   - Token serialization format?
   - Error handling and recovery?
   - Firmware update mechanism?

2. Developer Tools
   - How do I integrate with my existing codebase?
   - Python SDK? C library? REST API?
   - Debug/profiling tools?
   - Example applications?

3. Model Customization Path
   - "Can I use my fine-tuned model?"
   - Answer seems to be: "Buy a different chip"
   - Where's the compilation pipeline?
   - How do customers verify their model quality before committing to silicon?

4. Quantization Tooling
   - Document claims <3% quality degradation
   - How do I verify this for MY use case?
   - Is there a quantization simulator?
   - Can I test INT4 vs INT2 before ordering 10K units?
```

**The current documentation treats software as an afterthought.** For developer adoption, this is fatal.

### 3.4 Benchmark Methodology Is Inconsistent

```
PERFORMANCE CLAIMS ANALYSIS:

Claim: "25-35 tok/s on 2B model"
- Source: TeLLMe FPGA on 0.73B, scaled
- Scaling methodology: NOT DOCUMENTED
- Confidence: MEDIUM

Claim: "3-5× faster than Hailo-10H"
- Hailo tested on: Qwen2-1.5B, Llama3.2-3B
- SuperInstance tested on: ???
- Same model comparison: NOT PROVIDED
- Confidence: LOW

Claim: "4-8× higher tokens per watt"
- Calculated from: Power estimates, not measured
- Measurement methodology: NOT SPECIFIED
- Confidence: LOW

PROBLEM: Claims are made without standardized testing.
Competitors will dispute. Developers will be skeptical.
```

### 3.5 No Clear Verification Strategy

```
ASIC VERIFICATION REQUIREMENTS (not addressed):

1. Functional Verification
   - UVM testbench? Coverage model?
   - Formal verification of control FSM?
   - How many test cases per layer?

2. Performance Verification
   - Cycle-accurate simulator?
   - FPGA prototype correlation?
   - Timing closure margin?

3. Post-Silicon Validation
   - Bring-up plan?
   - Test vectors?
   - Quality assurance pipeline?

4. Manufacturing Test
   - DFT strategy?
   - Scan chains? BIST?
   - Test time budget?

A startup without verification expertise is a startup that burns money on respins.
```

---

## 4. SPECIFIC, ACTIONABLE SUGGESTIONS

### Priority 1: Before Asking for Money (0-3 months)

**S1. Build and Release FPGA Reference Implementation**

```
Deliverable: Open-source FPGA implementation of 1B ternary inference

Requirements:
- Target: KV260 or PYNQ-Z2 (~$200 developer boards)
- Model: BitNet 0.73B (validated by TeLLMe, easy baseline)
- Interface: USB or Ethernet, text-in/text-out
- Metrics: Actual measured throughput, power, quality

Why this matters:
- Proves the architecture works in real hardware
- Gives developers something to evaluate today
- Creates community engagement before silicon
- De-risks technical execution dramatically

Estimated effort: 2-3 months for 1 experienced FPGA engineer
Cost: $50K (salary + equipment)
```

**S2. Publish SDK Specification v0.1**

```
Deliverable: Developer interface documentation

Required sections:
1. Host Interface Protocol
   - USB endpoint configuration
   - Command packet format
   - Response packet format
   - Error codes

2. Token Streaming API
   - Input token format (UTF-8? BPE tokens?)
   - Output token format
   - Streaming vs batch mode
   - Stop conditions

3. Configuration Interface
   - Temperature, top_p, etc.
   - Context length setting
   - System prompt injection

4. Software SDK
   - Python library (pip install superinstance)
   - C library for embedded
   - REST API server
   - Example applications

Why this matters:
- Developers evaluate products by reading docs first
- Bad docs = no adoption regardless of hardware quality
- Shows you understand the customer is a programmer

Estimated effort: 1 month
Cost: $20K (technical writer + review)
```

**S3. Quantization Quality Report**

```
Deliverable: Comprehensive quantization analysis

Required content:
1. Model quality at each quantization level
   - FP16 baseline
   - INT8: MMLU, GSM8K, HumanEval scores
   - INT4: same benchmarks
   - INT4 + KV quantization: same benchmarks

2. Layer-wise sensitivity analysis
   - Which layers lose most from quantization?
   - Mixed-precision recommendation

3. Per-task degradation
   - Code generation (worst case)
   - Conversation (medium case)
   - Simple QA (best case)

4. Reproducible methodology
   - Datasets used
   - Evaluation scripts (open-source)
   - Random seeds, hardware config

Why this matters:
- "3% degradation" claim needs proof
- Developers need to know if their use case works
- Academic credibility for investor pitches

Estimated effort: 1 month
Cost: Compute time + 1 ML engineer month = $30K
```

### Priority 2: Technical Validation (3-6 months)

**S4. Revised Memory Architecture**

```
Current plan: 42 MB SRAM, 2K context
Problem: Doesn't fit in die budget

Recommendation: Hybrid approach
```

| Component | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| KV Cache | 42 MB on-chip | 8 MB on-chip + LPDDR4 | 8 MB = 512 tokens INT4 on-chip |
| Context | 2K fixed | 512 hot + 8K cold | Hot cache for recent tokens |
| External Memory | None | 256 MB LPDDR4 | $10 BOM, supports full context |
| Architecture | Pure SRAM | 2-tier hierarchy | Industry-standard approach |

```
Impact on value proposition:
- Still 10× more efficient than Jetson
- Adds $10-15 to COGS
- Enables longer context (market advantage)
- Simplifies physical design
```

**S5. Physical Design Flow Documentation**

```
Deliverable: Complete PD flow specification

Required documents:
1. Weight Injection Methodology
   - How are weights represented in RTL?
   - How are they converted to physical routing?
   - What tools are used?

2. Timing Closure Strategy
   - Clock tree architecture
   - Timing constraints at each stage
   - Margin allocation

3. Power Analysis Methodology
   - Activity factors used
   - Switching power estimation
   - Leakage modeling

4. DFT Architecture
   - Scan chain insertion
   - Memory BIST
   - JTAG/Debug interface

Why this matters:
- Investors need to see execution competence
- Manufacturing partners need this for quotes
- Shows you're not just "I have an idea"

Estimated effort: 2 months (Physical Design Lead)
```

**S6. Competitive Benchmark Suite**

```
Deliverable: Reproducible benchmark methodology

Standard test configuration:
| Parameter | Value |
|-----------|-------|
| Input prompt | 128 tokens (standardized) |
| Output length | 128 tokens |
| Temperature | 0.7 |
| Model | BitNet 2B (common baseline) |
| Quantization | INT4 |

Measurements required:
1. Time-to-first-token (TTFT)
2. Tokens per second (average)
3. Token latency variance (p50, p99)
4. Power consumption (active, idle)
5. Quality metrics (perplexity on WikiText2)

Comparison targets:
- Jetson Orin Nano ($199, INT4)
- Hailo-10H ($88, INT4)  
- Raspberry Pi 5 + AI Kit ($120)

Publish as open-source benchmark repository.
```

### Priority 3: Developer Ecosystem (6-12 months)

**S7. Developer Preview Program**

```
Structure:
- $99 "Explorer Kit" (FPGA prototype)
- Pre-order priority for first silicon
- Direct Slack/Discord access to engineering team
- Quarterly roadmap updates

Goal: 500-1000 developers committed before silicon
Value: Validates market demand, provides feedback, builds community
```

**S8. Model Partner Program**

```
Offer: "We'll put your model on a chip"

Target partners:
1. Open-source model creators (Mistral, Qwen)
   - Revenue share per chip
   - Marketing partnership

2. Vertical application developers (medical, legal)
   - Custom chip development
   - Regulatory-friendly frozen model

3. Closed-source model providers (OpenAI, Anthropic)
   - IP protection via mask-locking
   - Edge deployment without weight extraction risk

Each partnership validates a market segment.
```

**S9. Documentation Portal**

```
Required content hierarchy:

Getting Started (30 minutes)
├── Hardware setup guide
├── First inference tutorial
└── Troubleshooting common issues

Developer Guide (2 hours)
├── SDK reference
├── API documentation
├── Performance optimization
└── Integration patterns

Advanced Topics (as needed)
├── Custom model compilation
├── Quantization guidelines
├── System integration
└── Production deployment

Reference
├── Architecture specification
├── Electrical specifications
├── Mechanical drawings
└── Compliance certifications

Target: Parity with Jetson documentation quality
```

**S10. Open Source Strategy**

```
Open source:
- Python SDK (Apache 2.0)
- Quantization tools
- Example applications
- Benchmark suite

Keep proprietary:
- RTL design
- Physical design database
- Weight encoding methodology
- DFT infrastructure

Rationale:
- Open SDK builds trust and adoption
- Proprietary core protects competitive advantage
- Community contributions improve SDK quality
```

### Priority 4: Risk Mitigation (Ongoing)

**S11. Technical Advisory Board**

```
Recruit 3-5 advisors with:
- Jim Keller-tier credibility (optional, maximum impact)
- AI accelerator architecture experience (required)
- 28nm physical design experience (required)
- Edge deployment experience (important)

Equity commitment: 0.1-0.25% each

Why this matters more than anything:
- Credibility with investors
- Access to hiring network
- Architecture review prevents mistakes
- Mentorship for first-time founders
```

**S12. Manufacturing Partner Qualification**

```
Required partnerships:
1. Foundry: TSMC OR GlobalFoundries
   - MPW slot reservation
   - Full mask set quote
   - Design rule documentation

2. OSAT: ASE OR Amkor
   - Package design
   - Test program development
   - Volume pricing

3. Memory: Micron (US-based, lower geopolitical risk)
   - LPDDR4 allocation
   - Long-term pricing

Get written quotes, not verbal estimates.
```

**S13. Contingency Plans**

```
If iFairy fails in silicon:
- Fallback to ternary-only (BitNet compatible)
- 2× power increase but still competitive
- Document this as Plan B

If LPDDR4 allocation denied:
- Design for LPDDR5 (more available)
- Higher bandwidth, different controller
- Slight BOM increase

If first silicon has bugs:
- FPGA prototype is the backup product
- Sell FPGA solution while fixing ASIC
- "Developer Kit" becomes primary product temporarily
```

### Priority 5: Go-to-Market Technical Readiness

**S14. Production Test Strategy**

```
Required for volume manufacturing:
1. Test chip design
   - Scan chains for digital logic
   - Memory BIST for SRAM
   - Boundary scan for I/O

2. Test program
   - Functional test patterns
   - Speed binning
   - Power measurement

3. Test time budget
   - Target: <5 seconds per unit
   - Tester platform selection
   - Probe card design

4. Quality targets
   - 99.5% yield at speed
   - <500 DPM defect rate
   - ESD protection verified

Cost: $100-200K NRE for test development
```

**S15. Compliance Certification Plan**

```
Required certifications:
| Certification | Cost | Timeline |
|---------------|------|----------|
| FCC (US) | $10-20K | 2-3 months |
| CE (EU) | $5-15K | 1-2 months |
| RoHS | $2-5K | 1 month |
| USB-IF | $5K | 1-2 months |

Strategy:
- Use certified USB controller IP
- Pre-compliance testing before submission
- Modular certification (chip vs module vs device)
```

---

## 5. QUESTIONS TECHNICAL DUE DILIGENCE WOULD ASK

### Architecture & Design

1. **Show me the RTL.** Not diagrams—actual Verilog/Chisel code for the compute array.

2. **What's your timing closure strategy?** At 250MHz in 28nm, what's your margin? How do you handle clock distribution across a 25mm² die with 1024 PEs?

3. **How do weights get from PyTorch to silicon?** Walk me through the exact tool flow: model checkpoint → weight encoding → physical design → mask data.

4. **What happens when iFairy doesn't work?** What's the fallback? How much re-design is needed?

5. **Show me the verification plan.** How many test cases? What coverage model? What formal proofs?

### Memory & Bandwidth

6. **How does 42MB SRAM fit in 55mm² die?** The math doesn't work at 1.5 Mbit/mm² density.

7. **What's your KV cache prefetch strategy?** You have 40ms per token. Where's the scheduling analysis?

8. **INT4 KV cache quality impact?** Where are the perplexity numbers?

9. **Why not use LPDDR4 for KV cache?** External memory would solve the area problem. What's the power penalty?

### Power & Thermal

10. **Where does the 5W budget come from?** Break it down by component. Include clock distribution, I/O drivers, leakage.

11. **What's your thermal solution?** 3W in a USB/SD form factor requires a heatsink. How does that work?

12. **Power gating strategy?** How do you handle the "skip" case for zero weights? Clock gating? Power gating?

### Manufacturing

13. **What's your yield model?** 28nm mature yield is good, but large SRAM arrays have defect sensitivity.

14. **Who's your packaging partner?** What package type? Wire bond or flip-chip? Thermal considerations?

15. **What's the test strategy?** Test time per unit? ATE platform? Test cost per unit?

### Software

16. **What does the developer download?** A 10MB SDK? A Docker container? Give me the installation steps.

17. **How do I debug?** Is there a simulator? Emulator? Hardware debugger?

18. **What's the host driver architecture?** USB bulk transfers? How do you handle flow control?

19. **Error handling?** What happens when the chip overheats? Runs out of context? Receives malformed input?

### Competitive Positioning

20. **Why wouldn't I use Jetson at $199?** Your $89 chip saves $110. But Jetson runs any model. Quantify the tradeoff.

21. **How do you respond to Hailo's next product?** They're funded at $400M+. If they add LLM support, what's your moat?

22. **What's the upgrade path?** Customer buys v1.0 with BitNet 2B. Six months later, BitNet 3B releases. What do they do?

---

## 6. SDK/API REQUIREMENTS I'D DEMAND

### Minimum Viable SDK

```python
# This is what developers expect as baseline:

from superinstance import Chip

# Basic usage
chip = Chip()  # Auto-detect connected device
response = chip.generate(
    prompt="Hello, I am",
    max_tokens=100,
    temperature=0.7
)
print(response.text)

# Streaming
for token in chip.stream(prompt="Write a story"):
    print(token, end="", flush=True)

# Configuration
chip.set_system_prompt("You are a helpful assistant.")
chip.set_context_length(2048)

# Batch inference (if supported)
responses = chip.batch([
    "What is AI?",
    "What is ML?",
    "What is deep learning?"
])
```

### Advanced Features Needed

```python
# Token-level control
tokens = chip.tokenize("Hello world")
logits = chip.forward(tokens)  # For custom sampling

# Context management
chip.clear_context()
chip.load_context(previous_conversation)

# Performance monitoring
stats = chip.get_stats()
# stats = {
#     "tokens_generated": 100,
#     "tokens_per_second": 28.5,
#     "time_to_first_token_ms": 45,
#     "power_watts": 2.8
# }

# Multi-chip (future)
chips = Chip.enumerate()
chip0 = Chip(device_id=0)
chip1 = Chip(device_id=1)
```

### C API for Embedded

```c
// Required for embedded deployment

#include <superinstance.h>

// Initialize
si_handle_t chip = si_open(SI_AUTO_DETECT);
if (chip == SI_INVALID_HANDLE) {
    // Handle error
}

// Generate
si_config_t config = {
    .max_tokens = 100,
    .temperature = 0.7f,
    .top_p = 0.9f
};

si_result_t result = si_generate(chip, "Hello", &config);
if (result.status == SI_OK) {
    printf("%s\n", result.text);
    si_free_result(&result);
}

// Cleanup
si_close(chip);
```

### Host Interface Protocol

```
USB Device Configuration:
- VID/PID: Registered with USB-IF
- Class: Vendor-specific (or CDC-ACM for serial emulation)
- Endpoints:
  - EP1 OUT: Command input (512 byte max)
  - EP1 IN: Response output (512 byte max)
  - EP2 IN: Streaming tokens (64 byte packets)

Command Format:
struct __attribute__((packed)) si_command {
    uint8_t cmd;           // Command type
    uint8_t flags;         // Options
    uint16_t prompt_len;   // Prompt length
    uint16_t max_tokens;   // Max generation
    float temperature;     // Sampling temperature
    float top_p;          // Nucleus sampling
    uint8_t prompt[];     // Variable-length prompt
};

Response Format:
struct __attribute__((packed)) si_response {
    uint8_t status;        // OK, error, etc.
    uint8_t flags;         // More data, end, etc.
    uint16_t token_count;  // Tokens in this response
    uint8_t tokens[];      // Generated tokens
};
```

---

## 7. DOCUMENTATION IMPROVEMENTS NEEDED

### Add: Technical Architecture Deep Dive

```
Required content:
1. Detailed block diagram with:
   - Exact data widths
   - Pipeline stages
   - Buffer sizes

2. Weight encoding specification:
   - Bit format in metal
   - Routing strategy
   - Process corner handling

3. Compute array details:
   - PE microarchitecture
   - Interconnect topology
   - Accumulator precision

4. Control flow:
   - Inference state machine
   - Layer scheduling
   - Attention mechanism implementation
```

### Add: Developer Integration Guide

```
Required content:
1. Hardware setup:
   - Power requirements
   - Connector pinouts
   - Thermal recommendations

2. Software installation:
   - Driver installation (Windows, Linux, macOS)
   - SDK installation
   - First inference tutorial

3. Integration patterns:
   - Real-time chat application
   - Batch processing pipeline
   - Edge device integration

4. Troubleshooting:
   - Common errors and solutions
   - Performance debugging
   - Hardware diagnostics
```

### Add: Quantization Guidelines

```
Required content:
1. Model preparation:
   - Supported architectures
   - Layer requirements
   - Pre-quantization optimization

2. Quality evaluation:
   - Benchmark recommendations
   - Task-specific evaluation
   - Degradation thresholds

3. Custom quantization:
   - Layer-wise precision selection
   - Mixed-precision guidelines
   - Fine-tuning after quantization
```

### Add: Production Deployment Guide

```
Required content:
1. Hardware integration:
   - PCB design guidelines
   - Power supply design
   - Thermal management

2. Software architecture:
   - Production deployment patterns
   - Error handling strategies
   - Monitoring and logging

3. Reliability:
   - MTBF expectations
   - Failure modes
   - Maintenance procedures

4. Security:
   - Physical security
   - Firmware integrity
   - Update mechanisms
```

---

## CONCLUSION

### What's Good

The core technical insight—mask-locked weights eliminate the memory bottleneck—is sound and potentially transformative. The mathematical framework is rigorous. The market positioning identifies a real gap. The documentation shows deep understanding of the problem space.

### What Needs Work

1. **Execution capability is unproven.** No team, no RTL, no silicon. Technical ideas are worthless without execution.

2. **SDK is an afterthought.** For a developer-focused product, this is fatal. Developers evaluate products by playing with them, not reading marketing materials.

3. **Memory architecture doesn't add up.** The KV cache sizing contradicts the die area budget. This needs resolution before silicon.

4. **iFairy is unproven in hardware.** The entire efficiency claim rests on complex-valued weights that have never been synthesized. This is high-risk.

5. **Supply chain risks are ignored.** Memory pricing and foundry allocation could kill the business model before launch.

### My Recommendation

**Conditional Proceed.**

The concept is worth pursuing, but not in its current form. Before committing significant capital:

1. Build the FPGA reference implementation (de-risks architecture)
2. Publish SDK v0.1 (de-risks developer adoption)
3. Recruit a CTO with 5+ tape-outs (de-risks execution)
4. Resolve the KV cache sizing contradiction (de-risks silicon)
5. Get written quotes for memory and foundry (de-risks supply chain)

If these five items are addressed, I'd raise my trust score to 7/10 and recommend proceeding to MPW tapeout.

Until then, this remains an elegant idea that hasn't proven it can execute.

---

*Review prepared by: Senior Technical Reviewer*  
*Date: March 2026*  
*Classification: Developer Due Diligence*
