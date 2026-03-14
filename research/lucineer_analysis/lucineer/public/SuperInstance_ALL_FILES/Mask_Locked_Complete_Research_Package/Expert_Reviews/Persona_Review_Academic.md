# Academic Peer Review: SuperInstance.AI Technical Claims
## A Tenured Professor's Assessment for ISCA/MICRO/ASPLOS Readiness

**Reviewer:** Professor of Computer Science and Electrical Engineering (Anonymized)  
**Institution:** Top-Tier Research University  
**Review Date:** March 2026  
**Documents Reviewed:**
- SuperInstance_Technical_Specification_10out10.pdf
- SuperInstance_Competitive_Analysis_10out10.pdf
- Kimi_Swarm_Research_Report_v13_Complementary.md

---

## Executive Summary

This review assesses the SuperInstance.AI technical documentation from the perspective of academic rigor required for top-tier computer architecture venues (ISCA, MICRO, ASPLOS). The work presents an innovative combination of ternary neural networks, mask-locked weight storage, and complex-valued arithmetic that warrants serious academic attention. However, **the documentation in its current form would NOT pass peer review** at major architecture conferences without significant methodological additions.

**Overall Assessment: CONDITIONAL ACCEPT-MAJOR-REVISIONS (Academic Standard)**

| Criterion | Score | ISCA/MICO Threshold | Status |
|-----------|-------|---------------------|--------|
| Technical Novelty | 7/10 | 7+ | ✓ Meets threshold |
| Mathematical Rigor | 5/10 | 8+ | ✗ Requires work |
| Experimental Methodology | 4/10 | 8+ | ✗ Critical gap |
| Reproducibility | 3/10 | 9+ | ✗ Critical gap |
| Citation Quality | 5/10 | 7+ | ✗ Requires work |
| Statistical Analysis | 2/10 | 8+ | ✗ Critical gap |
| Benchmark Fairness | 5/10 | 8+ | ✗ Requires work |

---

## 1. Section-by-Section Academic Rigor Assessment

### 1.1 Architecture Overview (Section 1)

**Strengths:**
- Clear problem statement: von Neumann bottleneck at the edge
- Novel approach combining three distinct technologies
- Good visual representations of architectural concepts

**Critical Academic Concerns:**

1. **Insufficient Prior Art Comparison**
   - The claim "mask-locked architecture eliminates this bottleneck entirely" lacks rigorous comparison to prior computing-in-memory (CIM) approaches
   - Missing citations to seminal works:
     - ISAAC (ISCA 2016) - analog crossbar computation
     - PRIME (ISCA 2016) - memristive computing
     - PUMA (ISCA 2019) - RRAM-based PIM
     - Attainment: ReRAM-based DNN accelerators
   
2. **Energy Claims Without Derivation**
   - "0.1 pJ per access" for mask-locked weights - where is the SPICE simulation data?
   - Compare to: SRAM read energy at 28nm (typically 0.5-2 pJ/bit for 6T cell)
   - Need: Per-access energy breakdown with PVT variation analysis

3. **Bandwidth Claim Oversimplification**
   - "Unlimited bandwidth" is not physically accurate
   - Wire delay, capacitive loading, and clock distribution constraints apply
   - Need: Formal bandwidth analysis considering RC parasitics

**Reviewer Questions:**
- Q1: What is the actual wire capacitance per weight access?
- Q2: How does the mask-ROM approach compare to RRAM-based weight storage in energy?
- Q3: What is the worst-case access latency across all weights simultaneously?

### 1.2 Ternary Neural Network Foundation (Section 1.1.2)

**Strengths:**
- Appropriate reference to BitNet b1.58 (Microsoft Research)
- Quantitative comparison table with perplexity metrics

**Critical Academic Concerns:**

1. **Validation of BitNet Claims**
   - Document claims "8x compression" but should verify this is per-parameter, not total model
   - Embedding layer typically remains FP16 in BitNet - not addressed
   - Missing: Per-layer breakdown of memory savings

2. **Quality Degradation Not Fully Characterized**
   - Only WikiText2 perplexity reported
   - Missing standard evaluation suite: MMLU, HellaSwag, PIQA, ARC
   - Need: Statistical significance testing (t-tests, confidence intervals)

3. **Missing Citation to Critical Ternary Literature**
   - Hou et al., "ProxQuant: Quantized Neural Networks via Proximal Operators" (ICLR 2019)
   - Zhu et al., "Trained Ternary Quantization" (ICLR 2017)
   - Li et al., "Ternary Weight Networks" (arXiv 2016)

**Required Additions:**
```
Table: Extended Quality Metrics
| Benchmark | FP16 | INT8 | Ternary | Δ% | p-value | n (runs) |
|-----------|------|------|---------|-----|---------|----------|
| WikiText2 PPL | 12.5 | 12.7 | 12.8 | +2.4% | TBD | TBD |
| MMLU (5-shot) | ? | ? | ? | ? | ? | ? |
| HellaSwag | ? | ? | ? | ? | ? | ? |
| ARC-Challenge | ? | ? | ? | ? | ? | ? |
```

### 1.3 iFairy Complex Weight Architecture (Section 2.1)

**Strengths:**
- References recent arXiv paper (arXiv:2508.05571)
- Interesting C4 group mathematical framework
- Hardware implications clearly articulated

**Critical Academic Concerns:**

1. **Mathematical Rigor Deficiencies**
   
   The C4 group multiplication table is presented, but critical mathematical details are missing:
   
   - **Proof of closure**: The C4 group is indeed closed, but where is the formal proof that complex-valued attention preserves the group structure through the transformer layers?
   
   - **Gradient flow analysis**: Complex-valued networks have non-holomorphic activation functions - how does backpropagation work? Need citation to:
     - Trabelsi et al., "Deep Complex Networks" (ICLR 2018)
     - Guberman, "On Complex Valued Convolutional Neural Networks" (2016)
   
   - **Attention mechanism**: "Hermitian inner product real part" mentioned but not derived:
     ```
     Standard attention: Attention(Q,K,V) = softmax(QK^T/√d)V
     iFairy attention: ??? (needs formal definition)
     ```

2. **Kirchhoff's Law Computation Claims**
   
   The claim that MAC operations become passive current summation requires rigorous justification:
   
   - What is the required conductance precision?
   - How are negative weights (-1, -i) implemented? (Requires differential signaling or current sources)
   - What is the ADC resolution required for accumulation?
   - Where is the circuit schematic and SPICE simulation?
   
   **Missing Citation:** Reck et al., "Experimental realization of any discrete unitary operator" (Optics Letters 1994) - foundational work on linear optical computing

3. **Perplexity Improvement Claim**
   
   "iFairy shows BETTER perplexity than FP16" - this extraordinary claim requires:
   - Statistical significance testing
   - Multiple random seeds (n ≥ 5)
   - Comparison on identical training data and compute budget
   - Potential confounding factors analysis

### 1.4 Table-Lookup Matrix Multiply (TLMM) (Section 2.2)

**Strengths:**
- Concrete reference implementation (TeLLMe paper)
- Resource utilization provided

**Critical Academic Concerns:**

1. **Scalability Analysis Missing**
   - 98K LUTs for 0.73B model → what is the scaling factor for 2B?
   - Linear? Quadratic? Memory-bound?
   - Need: Roofline model analysis

2. **Timing Analysis Incomplete**
   - "1 cycle lookup vs 4 cycle multiply" - which FPGA? What speed grade?
   - Critical path analysis missing
   - Need: Post-place-and-route timing reports

3. **Missing Prior Art in LUT-Based Computing**
   - LUT-based neural network inference is not novel:
     - Nurvitadhi et al., "Can FPGAs Beat GPUs in Accelerating Next-Generation Deep Neural Networks?" (FPGA 2017)
     - Li et al., "LUT-based Efficient GPU Inference" (2023)

### 1.5 System Architecture (Section 3)

**Strengths:**
- Detailed block diagrams
- Memory hierarchy clearly specified

**Critical Academic Concerns:**

1. **Power Budget Breakdown Lacks Validation**
   - "TLMM Array: 2.0W (40%)" - based on what analysis?
   - Need: Gate-level power simulation with switching activity
   - Need: SPICE-based extraction for analog components

2. **SRAM Sizing Justification**
   - "KV Cache: 2MB SRAM" - how was this derived?
   - For 24 layers, 4096 context, 2B model:
     ```
     Per layer KV: 2 × hidden_dim × seq_len × 2 (K+V)
     = 2 × 2048 × 4096 × 2 = 32MB for FP16
     After quantization: ??? (derivation needed)
     ```
   - The numbers don't add up - clarify the calculation

3. **Missing Interconnect Analysis**
   - No NoC (Network-on-Chip) analysis for data movement between arrays
   - For 512 parallel lanes, what is the interconnect topology?
   - Need: Communication/computation overlap analysis

### 1.6 Performance Specifications (Section 4)

**Strengths:**
- Detailed latency breakdown per operation
- First-token latency analysis

**Critical Academic Concerns:**

1. **The "25 tokens/s" Claim Is NOT Novel**
   - TeLLMe already achieves 25 tok/s on KV260 FPGA
   - The target (25-35 tok/s) shows only marginal improvement
   - Where is the ASIC-specific advantage quantified?

2. **Statistical Rigor Completely Absent**
   - No error bars on any performance numbers
   - No confidence intervals
   - No variance across multiple runs
   - No sensitivity analysis to temperature, voltage, process corner

3. **Missing ISO-Standard Benchmarking**
   - Use MLPerf Inference benchmark for fair comparison
   - Use standardized prompt sets (e.g., ShareGPT)
   - Report: mean, median, 95th percentile, 99th percentile latencies

**Required Format:**
```
| Metric | Mean | Std Dev | 95% CI | n | Conditions |
|--------|------|---------|--------|---|------------|
| Throughput (tok/s) | 25.0 | ±? | [?,?] | ? | 25°C, nominal V |
| Latency (ms/token) | 40 | ±? | [?,?] | ? | 25°C, nominal V |
| Power (W) | 4.8 | ±? | [?,?] | ? | 25°C, nominal V |
```

### 1.7 Competitive Benchmarking (Section 5)

**Strengths:**
- Multiple competitors analyzed
- Power/throughput positioning matrix

**Critical Academic Concerns:**

1. **Benchmark Methodology Fatally Flawed**
   
   The document admits: "SuperInstance.AI simulated based on TeLLMe FPGA reference"
   
   **This is unacceptable for academic publication.** Direct hardware comparison on identical:
   - Model weights
   - Input prompts
   - Quantization scheme
   - Output verification
   
   is required.

2. **Different Models Across Competitors**
   - Hailo tested on Qwen2-1.5B, Llama 3.2-3B
   - Jetson tested on Llama 2-7B
   - SuperInstance claims based on BitNet 2B
   - These are NOT comparable!

3. **Missing Fair Comparison Framework**
   - Standardize on: perplexity-normalized throughput
   - Report: tokens/watt at iso-perplexity
   - Account for: model quality differences

### 1.8 Process Technology (Section 6)

**Strengths:**
- 28nm node selection justified
- Yield analysis using Murphy's model

**Critical Academic Concerns:**

1. **Yield Model Oversimplified**
   - Murphy's model assumes random defect distribution
   - For large ROM arrays, systematic defects dominate
   - Need: Critical area analysis for ROM-specific failures

2. **Missing Process Variation Analysis**
   - No Monte Carlo simulation for process corners
   - For ternary logic, Vth variation is critical
   - Need: Sensitivity of ternary threshold to Vth spread

3. **No Mask ROM Density Justification**
   - "0.15 μm²/bit" claimed - for which ROM architecture?
   - NOR ROM? NAND ROM? Register file ROM?
   - Need: Layout analysis and area breakdown

### 1.9 Quantization Strategy (Section 7)

**Strengths:**
- Systematic quantization framework
- KV cache quantization addressed

**Critical Academic Concerns:**

1. **Calibration Dataset Not Specified**
   - "512-sample calibration dataset" - what dataset?
   - C4? WikiText? Custom?
   - Calibration methodology (min/max vs percentile vs entropy) not specified

2. **Scale Factor Optimization**
   - "Minimize KL divergence" - show the math:
     ```
     KL(P||Q) = Σ P(x) log(P(x)/Q(x))
     ```
     What are P and Q? FP16 and quantized distributions?

3. **Missing Accuracy-Efficiency Pareto Analysis**
   - Academic standard: show tradeoff curve
   - X-axis: compression ratio or bit-width
   - Y-axis: perplexity or accuracy
   - This paper shows only one operating point

---

## 2. Peer Review Simulation: What Reviewers Would Ask

### Reviewer 1 (Architecture Expert)

**Major Comments:**

1. "The mask-locked weight storage concept is interesting, but I'm concerned about the lack of comparison to prior computing-in-memory architectures. The authors should compare to ISAAC, PRIME, and more recent RRAM-based accelerators in terms of:
   - Energy per MAC operation
   - Area per bit of storage
   - Effective memory bandwidth"

2. "The claim of 'unlimited bandwidth' is physically incorrect. Please provide:
   - Wire delay analysis for worst-case weight access
   - RC parasitic extraction from layout
   - Clock distribution power for synchronous weight read"

3. "The scalability of TLMM to larger models (70B+) is not addressed. Please add:
   - Roofline model analysis
   - Memory bandwidth requirements scaling
   - Resource utilization projection"

**Minor Comments:**
- Figure 1 caption should explain "von Neumann bottleneck" for broader audience
- Table 1 should include confidence intervals
- Reference [TBD] needs actual citation

### Reviewer 2 (Machine Learning Expert)

**Major Comments:**

1. "The iFairy complex-valued network claims are extraordinary ('better perplexity than FP16') but lack rigorous validation. I require:
   - Multiple random seed results (n≥5)
   - Statistical significance testing
   - Comparison on identical training compute budget
   - Downstream task evaluation (MMLU, HellaSwag, ARC)"

2. "The interaction between ternary weights (BitNet) and complex weights (iFairy) is not explained. Are these competing or complementary approaches? If combined, what is the joint quantization scheme?"

3. "Quality degradation analysis is insufficient. Only WikiText2 perplexity is reported. Standard evaluation suite including MMLU, HellaSwag, PIQA, ARC-Easy, ARC-Challenge is expected."

**Minor Comments:**
- BitNet citation should be to published paper, not HuggingFace card
- Missing citation to Ternary Weight Networks (Li et al., 2016)
- Calibration dataset should be specified

### Reviewer 3 (Circuit Design Expert)

**Major Comments:**

1. "The Kirchhoff's Law computation scheme requires detailed circuit analysis:
   - Schematic of resistive network
   - Required resistor matching precision
   - ADC resolution and energy for accumulation readout
   - SPICE simulation results across PVT corners"

2. "Power breakdown claims (40% TLMM, 20% SRAM) lack validation. I expect:
   - Gate-level power simulation with switching activity factor
   - SPICE simulation for custom circuits
   - Measurement-based validation from silicon"

3. "Ternary logic noise margin analysis is missing:
   - For 1.1V VDD, ternary levels are 0V, 0.55V, 1.1V
   - What is the noise margin at intermediate level?
   - How does process variation affect ternary thresholds?
   - Monte Carlo analysis is expected"

**Minor Comments:**
- Add eye diagram simulation for ternary signaling
- Include layout parasitic extraction results
- Specify ESD protection scheme

---

## 3. Missing Methodology Sections

### 3.1 Experimental Setup (Required for Academic Paper)

```
Missing Section: Experimental Methodology

3.X Experimental Setup

3.X.1 Hardware Configuration
- FPGA board: AMD Kria KV260 (Zynq UltraScale+ XCK26)
- Power measurement: Yokogawa WT310, 1mW resolution
- Temperature: 25°C ± 2°C ambient, 50°C max die
- Host PC: Ubuntu 22.04, Python 3.10, PyTorch 2.0

3.X.2 Model Configuration
- BitNet b1.58-2B-4T (Microsoft Research)
- Checkpoint: [exact hash/version]
- Tokenizer: LLaMA tokenizer
- Context length: 4096 tokens

3.X.3 Benchmark Prompts
- Dataset: ShareGPT subset (1000 prompts)
- Input length: 128-512 tokens
- Output length: 128 tokens (decode phase)
- Temperature: 1.0, top-p: 0.9

3.X.4 Measurement Protocol
- Warmup: 100 tokens generation
- Measurement: 1000 tokens, 10 runs, report mean ± std
- Power: Average over generation period
- Latency: Per-token, excluding first-token latency

3.X.5 Statistical Analysis
- Significance level: α = 0.05
- Confidence interval: 95%
- Multiple comparison correction: Bonferroni
- Effect size: Cohen's d
```

### 3.2 Theoretical Analysis (Required for Academic Paper)

```
Missing Section: Theoretical Foundations

3.Y Mathematical Framework

3.Y.1 Ternary Arithmetic Properties
Theorem 1: Ternary multiplication can be implemented with O(1) LUT lookup.
Proof: [Formal proof required]

3.Y.2 C4 Group Properties
Theorem 2: The C4 group is closed under multiplication and enables 
multiplication-free inference.
Proof: [Formal proof required]
Lemma 2.1: Complex multiplication in C4 reduces to element permutation.
Proof: [Formal proof required]

3.Y.3 Memory Bandwidth Analysis
Theorem 3: Mask-locked weight storage eliminates weight bandwidth bottleneck
for layer i with Wi weights if:
    Wi × sizeof(weight) < Activation_size_i
Proof: [Formal proof with bandwidth calculations]

3.Y.4 Energy Analysis
Proposition: Energy per inference scales as O(n × d) where n is sequence
length and d is hidden dimension.
Derivation: [Show calculation]
```

### 3.3 Limitations Section (Required for Academic Paper)

```
Missing Section: Limitations

6. Limitations

6.1 Model Flexibility
Our mask-locked architecture fixes weights at manufacturing time, limiting
deployment to a single model variant. We quantify this limitation as:
- Market segment addressable: X% (estimated from survey data)
- Model re-spin cost: $100K per variant (2 metal layer change)
- Time to new model: 2 months minimum

6.2 Ternary Quantization
Ternary quantization may not be suitable for all model architectures:
- Vision models: [citations showing degradation]
- Audio models: [citations showing degradation]
- Multimodal models: Not evaluated

6.3 Scalability
Our analysis focuses on 2B parameter models. Extension to larger models
(70B+) requires:
- Multi-chip architecture (not addressed)
- Inter-chip communication bandwidth (not analyzed)
- Power scaling beyond 5W budget (not addressed)

6.4 Silicon Validation
All performance claims are based on FPGA emulation and SPICE simulation.
Final silicon validation is required for:
- Actual power consumption
- Thermal behavior under sustained load
- Manufacturing yield at volume
```

---

## 4. Reproducibility Checklist

Following the ACM SIGARCH reproducibility guidelines, the following are MISSING:

### 4.1 Artifacts Not Provided

| Artifact | Status | Required for Reproducibility |
|----------|--------|------------------------------|
| FPGA bitstream | ✗ Missing | Required to replicate experiments |
| RTL source code | ✗ Missing | Required to understand implementation |
| SPICE netlists | ✗ Missing | Required to verify energy claims |
| Model checkpoints | ✗ Missing (public) | BitNet available, iFairy checkpoint version not specified |
| Benchmark prompts | ✗ Missing | Required for identical evaluation |
| Scripts for experiments | ✗ Missing | Required to automate evaluation |
| Power measurement raw data | ✗ Missing | Required to verify power claims |

### 4.2 Reproducibility Statement Template

The paper should include:

```
Reproducibility Statement

To facilitate reproducibility of our results, we provide:

1. Code availability:
   - FPGA implementation: [GitHub URL]
   - RTL design: [GitHub URL] (upon publication)
   - Evaluation scripts: [GitHub URL]
   - License: MIT

2. Hardware availability:
   - FPGA demo available for loan to researchers
   - Contact: [email]

3. Model availability:
   - BitNet b1.58-2B-4T: HuggingFace [link]
   - Checkpoint hash: [SHA256]

4. Benchmark availability:
   - Prompts: [URL]
   - Evaluation metrics: [standard metrics]

5. Computational requirements:
   - FPGA synthesis: 4 hours on Xilinx server
   - SPICE simulation: 48 hours on 16-core workstation
   - Model training: Not performed (pre-trained model used)
```

### 4.3 Currently Unreproducible Claims

| Claim | Why Unreproducible | Fix Required |
|-------|-------------------|--------------|
| "0.1 pJ per weight access" | No SPICE netlist provided | Provide circuit schematic and simulation |
| "25 tok/s at 4.8W" | FPGA bitstream not provided | Provide bitstream and measurement protocol |
| "94% yield" | No defect density justification | Provide foundry data or assumption validation |
| "5W total power" | No breakdown methodology | Provide gate-level simulation or silicon measurement |

---

## 5. Suggested Experiments for Validation

### 5.1 Critical Experiments (Required for Publication)

**Experiment 1: Direct Hardware Comparison**
```
Objective: Compare SuperInstance to competitors under identical conditions

Setup:
- Acquire: Hailo-10H, Jetson Nano, Coral Edge TPU
- Model: BitNet b1.58-2B-4T (convert to INT8 for competitors)
- Prompts: ShareGPT benchmark (1000 prompts)
- Metrics: Throughput, power, perplexity

Expected Results Table:
| Platform | Throughput (tok/s) | Power (W) | tok/J | PPL | Setup Time |
|----------|-------------------|-----------|-------|-----|------------|
| SuperInstance | ? | ? | ? | 12.8 | ? |
| Hailo-10H | ? | ? | ? | ? | ? |
| Jetson Nano | ? | ? | ? | ? | ? |

Statistical Analysis:
- 10 runs per platform
- Report: mean, std, 95% CI
- ANOVA for significance testing
```

**Experiment 2: Energy Breakdown Validation**
```
Objective: Validate claimed energy breakdown

Setup:
- SPICE simulation of TLMM array (using TSMC 28nm PDK)
- Gate-level simulation of control logic
- Post-layout extraction for interconnect

Deliverables:
- Per-component energy breakdown
- Sensitivity to VDD (0.8V, 0.9V, 1.0V)
- Sensitivity to temperature (0°C, 25°C, 85°C)
- Comparison to claimed 2.0W TLMM, 1.0W SRAM, etc.
```

**Experiment 3: Ternary Logic Noise Margin**
```
Objective: Validate ternary circuit reliability

Setup:
- Monte Carlo SPICE simulation (1000 runs)
- Process corners: TT, FF, SS, FS, SF
- Temperature: -40°C to 85°C
- VDD: 0.9V ± 10%

Metrics:
- Noise margin at VDD/2 level
- Probability of correct ternary detection
- Required minimum VDD for 99.99% correct detection

Expected Result:
- If 50mV margin claimed, show probability of failure < 10^-6
```

**Experiment 4: iFairy vs BitNet Quality**
```
Objective: Rigorously compare quantization schemes

Setup:
- Train both models on identical data (4T tokens)
- Identical compute budget
- 5 random seeds per model

Evaluation:
- WikiText2 perplexity
- MMLU (5-shot)
- HellaSwag (10-shot)
- ARC-Easy, ARC-Challenge
- PIQA

Statistical Analysis:
- Paired t-test for significance
- Effect size (Cohen's d)
- 95% confidence intervals

Expected Format:
| Metric | BitNet | iFairy | Δ% | p-value | d |
|--------|--------|--------|-----|---------|---|
| WikiText2 | 12.8±0.1 | 11.2±0.1 | -12.5% | <0.001 | 2.1 |
| MMLU | 35.2±0.5 | 36.1±0.5 | +2.6% | 0.04 | 0.3 |
```

### 5.2 Extended Experiments (Recommended)

**Experiment 5: Scalability Analysis**
```
Objective: Demonstrate scalability to larger models

Setup:
- Evaluate on BitNet b1.58 variants: 0.73B, 2B, 4B (if available)
- Project resource requirements for 7B, 13B, 70B

Metrics:
- LUT/CLB scaling factor
- SRAM scaling factor
- Power scaling factor
- Throughput scaling factor
```

**Experiment 6: KV Cache Scaling**
```
Objective: Validate context length claims

Setup:
- Test context lengths: 512, 1024, 2048, 4096, 8192
- Measure: latency, power, memory usage

Expected Result:
- Linear scaling of KV cache memory
- Minimal latency impact for on-chip KV
- Power overhead for extended context
```

---

## 6. Novel Research Directions

Based on my review, I identify the following genuinely novel contributions and suggest extensions:

### 6.1 Truly Novel Contributions

1. **First Mask-Locked Edge LLM Chip** (Novel)
   - Prior work: Taalas (datacenter, 200W+)
   - This work: Edge-appropriate, 5W
   - Contribution: Bringing mask-locking to power-constrained edge

2. **Ternary + Complex-Valued Combination** (Novel)
   - Prior work: BitNet (ternary), iFairy (complex)
   - This work: Potential combination
   - Contribution: 2-bit complex-valued with ternary-like efficiency

3. **Kirchhoff's Law for LLM Inference** (Potentially Novel)
   - Prior work: Analog CIM for CNNs
   - This work: Application to transformer attention
   - Contribution: Novel compute paradigm for attention

### 6.2 Suggested Research Extensions

**Extension 1: Hybrid Architecture**
```
Investigate: Can mask-locked weights be combined with small SRAM
for fine-tuning or adapter layers?

Research Questions:
- What adapter size is needed for task adaptation?
- Energy overhead of SRAM adapters?
- Quality impact of hybrid approach?

Potential Contribution:
"Mask-Locked Base with Adapter Fine-Tuning: A Hybrid Edge LLM Architecture"
```

**Extension 2: Multi-Model Chiplet**
```
Investigate: Can multiple mask-locked models be tiled on one chip?

Research Questions:
- Optimal chiplet interconnect for model selection?
- Overhead of model selection multiplexing?
- Business model for multi-model deployment?

Potential Contribution:
"Chiplet-Based Multi-Model Edge Inference with Mask-Locked Weights"
```

**Extension 3: On-Chip Learning**
```
Investigate: Can inference-time adaptation be done within power budget?

Research Questions:
- Minimal compute for LoRA-style adaptation?
- Energy cost of on-chip gradient accumulation?
- Privacy/latency benefits of on-device learning?

Potential Contribution:
"Privacy-Preserving On-Device Adaptation for Mask-Locked LLMs"
```

### 6.3 Publication Venues

Based on the technical content, I recommend:

| Venue | Fit | Timeline | Requirements |
|-------|-----|----------|--------------|
| ISCA 2027 | Excellent | Submit Nov 2026 | Add experiments, fix methodology |
| MICRO 2027 | Excellent | Submit Apr 2027 | More silicon validation |
| ASPLOS 2027 | Good | Submit Aug 2026 | Add software stack contribution |
| DAC 2027 | Good | Submit Nov 2026 | Focus on circuit innovations |
| ISSCC 2027 | Excellent | Submit Sep 2026 | Requires silicon measurements |

---

## 7. Curriculum Integration Opportunities

As an educator, I see excellent pedagogical value in this work:

### 7.1 Graduate Course: "Efficient ML Hardware"

**Module: Ternary Neural Networks (2 weeks)**
```
Lecture 1: Quantization Fundamentals
- FP32 → INT8 → INT4 → Ternary → Binary
- Trade-offs: quality vs efficiency
- Lab: Quantize a model using GPTQ

Lecture 2: Ternary Arithmetic Hardware
- LUT-based multiplication
- MAC unit design
- Lab: Implement ternary MAC in Verilog

Lecture 3: BitNet Architecture Deep Dive
- Paper analysis: BitNet b1.58
- Training considerations
- Lab: Run BitNet inference on FPGA

Lecture 4: Complex-Valued Neural Networks
- C4 group mathematics
- iFairy architecture
- Lab: Compare iFairy vs BitNet quality
```

**Assignments:**
1. Implement TLMM unit in SystemVerilog
2. Quantize LLaMA-7B to ternary, measure perplexity
3. Design mask-ROM layout for small weight matrix
4. Compare energy: SRAM read vs Mask-ROM read

### 7.2 Undergraduate Course: "Introduction to AI Hardware"

**Lab: Edge LLM Inference Comparison**
```
Week 1: Setup and baseline
- Install bitnet.cpp
- Run on CPU, measure throughput/power

Week 2: FPGA implementation (KV260)
- Flash TeLLMe bitstream
- Measure throughput/power
- Compare to CPU baseline

Week 3: Analysis and report
- Calculate tokens/joule
- Analyze bottleneck
- Propose optimization
```

### 7.3 Seminar Course: "Current Topics in AI Hardware"

**Week 6: Mask-Locked Inference**
```
Reading:
- Taalas: "Hard-coded AI chips" (SDxCentral article)
- SuperInstance.AI: This technical specification
- TeLLMe: arXiv:2510.15926

Discussion Questions:
1. Is single-model chip viable in fast-moving LLM landscape?
2. How does mask-locking compare to optical computing?
3. What business models enable mask-locked chip economics?

Student Project:
Design a mask-locked architecture for a different model class
(e.g., Stable Diffusion, Whisper)
```

### 7.4 Industry Workshop Content

**Workshop: "Building Your First Edge LLM Chip"**
```
Day 1: Architecture Fundamentals
- von Neumann bottleneck
- Ternary neural networks
- Mask-ROM vs SRAM trade-offs

Day 2: Hands-on FPGA Implementation
- TeLLMe reference architecture
- KV260 setup and demo
- Performance optimization

Day 3: Path to Silicon
- 28nm design flow
- Mask-ROM encoding
- Cost analysis

Day 4: Business Considerations
- Market sizing
- Competitive landscape
- Funding requirements

Day 5: Final Project
- Teams design their own variant
- Present to mock investment committee
```

---

## 8. Final Recommendations

### 8.1 For Academic Publication

**Priority 1 (Must Fix):**
1. Add statistical rigor: error bars, confidence intervals, significance tests
2. Standardize benchmarks: same model, same prompts across all comparisons
3. Provide reproducibility artifacts: code, scripts, raw data
4. Fix citation quality: inline citations, recent prior art

**Priority 2 (Should Fix):**
1. Add SPICE simulation validation for energy claims
2. Include Monte Carlo analysis for process variation
3. Address scalability to larger models
4. Add limitations section

**Priority 3 (Nice to Have):**
1. Silicon validation (if available)
2. Extended benchmark suite (MMLU, HellaSwag, etc.)
3. Theoretical analysis section
4. Video demo of FPGA implementation

### 8.2 For Investment Due Diligence

**Technical Risks:**
1. **Model obsolescence** (40% probability within 2 years) - mitigate with flexible metal-layer redesign
2. **Competition** (Quadric, Axelera well-funded) - differentiate on efficiency
3. **Memory pricing** (confirmed risk) - design flexibility for LPDDR5

**Technical Moats:**
1. TeLLMe FPGA reference provides validated baseline
2. First-mover in edge mask-locked space
3. Potential iFairy integration for 2x efficiency gain

### 8.3 Summary Verdict

**Academic Publication Readiness: NOT READY**

The work presents genuinely novel architecture innovations that warrant academic attention. However, the current documentation lacks the methodological rigor required for ISCA/MICRO peer review.

**Estimated Effort to Publication-Ready:**
- Add experiments: 200-400 hours
- Statistical analysis: 40 hours
- Reproducibility package: 60 hours
- Writing revisions: 80 hours
- **Total: 380-580 hours (2-4 person-months)**

**Recommended Timeline:**
- Months 1-2: Run critical experiments (Section 5.1)
- Month 3: Statistical analysis and reproducibility package
- Month 4: Paper revision and submission to ISCA 2027

---

## Appendix A: Detailed Citation Corrections

### Missing Citations (Critical)

| Claim | Missing Citation | Source |
|-------|-----------------|--------|
| Computing-in-memory | ISAAC | ISCA 2016 |
| Ternary quantization | TWN | arXiv 2016 |
| Ternary training | TTQ | ICLR 2017 |
| Complex networks | Deep Complex Networks | ICLR 2018 |
| FPGA LUT computing | Nurvitadhi et al. | FPGA 2017 |
| RRAM-based inference | PUMA | ISCA 2019 |
| Analog MAC | ISAAC, PRIME | ISCA 2016 |

### Citation Format Corrections

Current: "validated by Microsoft Research and demonstrated on HuggingFace"

Correct: "The BitNet b1.58 architecture was introduced by Wang et al. [1] and achieves comparable perplexity to FP16 models with 8× memory reduction. The pre-trained model is available on HuggingFace [2] with 16,010 monthly downloads as of March 2026."

References:
[1] H. Wang et al., "BitNet b1.58: The Era of 1-bit LLMs," arXiv:2504.12285, 2025.
[2] Microsoft, "BitNet b1.58-2B-4T," HuggingFace, 2025. Available: https://huggingface.co/microsoft/bitnet-b1.58-2B-4T

---

## Appendix B: Statistical Methods Reference

For the authors' reference, here are the standard statistical methods expected:

### B.1 Confidence Intervals

For throughput/power measurements:
```python
import scipy.stats as stats
import numpy as np

def compute_ci(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - h, mean + h

# Example
throughput_runs = [24.5, 25.1, 24.8, 25.3, 24.9]  # tok/s
mean, ci_low, ci_high = compute_ci(throughput_runs)
print(f"Throughput: {mean:.1f} tok/s (95% CI: [{ci_low:.1f}, {ci_high:.1f}])")
```

### B.2 Significance Testing

For comparing SuperInstance to baseline:
```python
def significance_test(group1, group2, alpha=0.05):
    t_stat, p_value = stats.ttest_ind(group1, group2)
    cohen_d = (np.mean(group1) - np.mean(group2)) / np.sqrt(
        (np.std(group1)**2 + np.std(group2)**2) / 2
    )
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < alpha,
        'effect_size': cohen_d
    }
```

### B.3 Required Sample Sizes

For 95% confidence with 10% margin of error:
- Power measurement: n ≥ 10 runs
- Throughput measurement: n ≥ 10 runs
- Quality evaluation: n ≥ 5 random seeds

---

**Document Control**

| Version | Date | Reviewer | Status |
|---------|------|----------|--------|
| 1.0 | March 2026 | Tenured Professor (Anonymized) | Final |

---

*This review was prepared following ACM SIGARCH peer review guidelines and ISCA review criteria.*

*"The goal of peer review is to improve the work, not to reject it. My criticisms are offered in the spirit of helping the authors achieve their goal of publishing rigorous, reproducible research that advances the field of computer architecture."*
