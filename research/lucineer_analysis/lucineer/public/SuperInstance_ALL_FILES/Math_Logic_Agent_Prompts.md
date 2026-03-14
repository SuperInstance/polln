# Math & Logic Specialist Agent Prompts
## Mask-Locked Inference Chip Technical Deep Dive

**Document Purpose**: This file contains detailed prompts and context for math/logic specialists to explore unconventional optimization opportunities for the mask-locked inference chip architecture.

---

## SECTION 1: CORE ARCHITECTURE CONCEPT

### What You Need to Understand

The **Mask-Locked Inference Chip** is a radical departure from traditional AI hardware:

**Traditional Approach**:
- Weights stored in memory (DRAM/SRAM)
- During inference: fetch weights → compute → repeat
- Memory bandwidth is the bottleneck
- Power consumed by memory access (10-25 pJ/bit for DRAM)

**Mask-Locked Approach**:
- Weights encoded directly in silicon metal interconnect layers
- Weights are "always present" at compute units
- Zero access latency, zero access energy, infinite bandwidth
- Tradeoff: changing weights requires fabricating a new chip

### The Target Application

- **Model**: BitNet b1.58-2B-4T (ternary weights: -1, 0, +1) OR iFairy (complex-valued: ±1, ±i)
- **Precision**: 1.58-bit (ternary) to 2-bit (complex)
- **Power Target**: 2-3W total
- **Performance Target**: 25-80 tokens/second
- **Price Target**: $35-60 retail
- **Process Node**: 28nm (mature, low NRE)

---

## SECTION 2: PRIMARY MATHEMATICAL EXPLORATION PROMPTS

### PROMPT A: Ternary Weight Arithmetic Optimization

**Context**: BitNet b1.58 uses ternary weights {-1, 0, +1}. This is NOT standard quantization—it's a fundamentally different representation.

**Questions to Explore**:

1. **Multiplication Elimination**: With ternary weights, a weight × activation multiplication becomes:
   - If w = +1: result = activation (identity)
   - If w = 0: result = 0 (no computation needed)
   - If w = -1: result = -activation (negation)

   **What is the mathematical foundation for optimizing this?** Can we design circuits that:
   - Never perform actual multiplication?
   - Use only addition, subtraction, and data routing?
   - What percentage of operations can be eliminated with proper sparsity exploitation?

2. **Sparsity Patterns**: In ternary networks, approximately 30-50% of weights are zero.
   - How can we mathematically model the optimal skipping strategy?
   - What is the theoretical minimum number of additions required for a layer with N inputs and M outputs given ternary weight matrix W?
   - Can we derive a closed-form expression for operations saved?

3. **Matrix Decomposition for Ternary**: 
   - Can a ternary matrix be decomposed into operations that are simpler than matrix multiplication?
   - Are there properties of {-1, 0, +1} matrices that allow O(N²) instead of O(N³) operations?
   - Explore the relationship between ternary matrices and signed binary representations.

**Deliverable**: Mathematical framework for computing ternary matrix-vector products with minimum operations.

---

### PROMPT B: Complex-Valued LLM (iFairy) Hardware Implications

**Context**: iFairy from Peking University uses weights from {±1, ±i} (fourth roots of unity). This is 2-bit but uses complex numbers.

**The Claim**: "Multiplication-free inference" — only additions and element swaps needed.

**Questions to Explore**:

1. **Complex Multiplication Decomposition**: 
   - Standard complex multiplication: (a+bi)(c+di) = (ac-bd) + (ad+bc)i
   - This requires 4 multiplications and 2 additions
   - With weights ∈ {±1, ±i}, show mathematically why this reduces to only additions/swaps

2. **Hermitian Inner Product Analysis**:
   - iFairy uses Hermitian inner product: ⟨x, w⟩ = x · w̄ (conjugate transpose)
   - With w ∈ {±1, ±i}, what operations are actually needed?
   - Prove or disprove the "multiplication-free" claim rigorously

3. **Hardware Resource Comparison**:
   - Ternary (BitNet): weights {-1, 0, +1}, requires add/subtract/skip
   - Complex 2-bit (iFairy): weights {±1, ±i}, requires add/swap
   - Which is more efficient? Derive formulas for:
     - Operations per MAC (multiply-accumulate)
     - Memory bandwidth requirements
     - Circuit complexity (gate count estimate)

4. **Information Capacity**: 
   - Ternary: log₂(3) ≈ 1.58 bits per weight
   - Complex 2-bit: exactly 2 bits per weight
   - Is the extra 0.42 bits worth the potential hardware complexity?

**Deliverable**: Rigorous comparison of ternary vs. complex-valued representation for hardware implementation.

---

### PROMPT C: KV Cache Bandwidth Optimization

**Context**: The KV (Key-Value) cache is the PRIMARY memory bandwidth bottleneck in autoregressive LLM inference.

**The Problem**:
- Each generated token requires reading the entire KV cache
- KV cache grows with context length: O(sequence_length × num_layers × hidden_dim)
- For 2B model, 4K context: ~768MB KV cache in FP16
- Memory bandwidth: 768MB × tokens/second → this dominates power consumption

**Questions to Explore**:

1. **Mathematical Analysis of KV Necessity**:
   - What is the minimum information that MUST be stored per layer?
   - Can we derive lower bounds on KV cache size from information theory?
   - Are there redundancies in the KV representation that can be exploited?

2. **KV Cache Compression**:
   - Can KV cache be quantized to INT4/INT8 without quality loss?
   - What's the mathematical relationship between KV precision and attention quality?
   - Derive error bounds for quantized attention: Attn(Q, K', V') vs. Attn(Q, K, V)

3. **Alternative Attention Mechanisms**:
   - Linear attention: O(N) instead of O(N²) complexity
   - Can linear attention work with ternary weights?
   - What's the mathematical formulation for ternary linear attention?

4. **Sliding Window Attention**:
   - Limit context to recent W tokens (fixed memory)
   - What's the mathematical impact on model capability?
   - Can we derive optimal window size for different tasks?

**Deliverable**: Mathematical framework for minimizing KV cache bandwidth while preserving model quality.

---

### PROMPT D: Mask-Locked Weight Encoding Geometry

**Context**: Weights are encoded in metal interconnect layers of the chip. The physical layout matters.

**The Constraint**:
- Metal routing has fixed pitch (minimum wire spacing)
- Each weight value must be represented by a physical pattern
- The encoding affects: area, power, noise immunity, manufacturability

**Questions to Explore**:

1. **Information Density in Metal**:
   - How many bits can be encoded per unit area in metal interconnect?
   - What's the theoretical maximum vs. practical encoding schemes?
   - Compare: binary encoding (2 patterns), ternary (3 patterns), quaternary (4 patterns)

2. **Noise Immunity Analysis**:
   - Metal patterns are subject to manufacturing variation
   - What encoding scheme maximizes Hamming distance between weight values?
   - Derive optimal encoding for ternary {-1, 0, +1} in presence of noise

3. **Routing Optimization**:
   - In standard chips, weights are data routed to compute units
   - In mask-locked, weights ARE the routing
   - What's the mathematical relationship between weight matrix structure and routing complexity?
   - Can we prove lower bounds on routing area for specific weight matrices?

4. **Weight Matrix Partitioning**:
   - Large weight matrices must be tiled across the chip
   - How should we partition weights to minimize inter-tile communication?
   - What's the optimal tiling strategy for transformer attention matrices?

**Deliverable**: Mathematical framework for optimal weight encoding in silicon metal layers.

---

### PROMPT E: Systolic Array Optimization for Fixed Weights

**Context**: Systolic arrays are the standard architecture for matrix operations in AI accelerators (Google TPU, etc.).

**Standard Systolic Array**:
- Weights pre-loaded into processing elements (PEs)
- Activations flow through the array
- Each PE performs: accumulate += weight × input

**Mask-Locked Systolic Array**:
- Weights permanently wired into PEs
- No weight loading phase
- Different PE design possible (simpler?)

**Questions to Explore**:

1. **Optimal Array Dimension**:
   - For a fixed weight matrix W (N×M), what's the optimal systolic array shape?
   - Square array (√N × √M)? Rectangular? Something else?
   - Derive the relationship between array shape and throughput/latency

2. **Dataflow Analysis**:
   - Weight-stationary: weights stay, activations flow (standard for inference)
   - Input-stationary: inputs stay, weights flow (not applicable for mask-locked)
   - Output-stationary: outputs stay, both flow
   - For mask-locked, can we design a new dataflow that exploits fixed weights?

3. **Partial Sum Accumulation**:
   - Matrix multiplication produces partial sums that must be reduced
   - For ternary weights, partial sums are sums of signed activations
   - Can we derive optimal reduction tree depth for specific weight patterns?

4. **Throughput Modeling**:
   - Derive formula for tokens/second given:
     - Clock frequency f
     - Array dimensions (R, C)
     - Model dimensions (hidden_dim, num_layers)
     - Sequence length S
   - What's the theoretical maximum throughput?

**Deliverable**: Mathematical model for systolic array design with mask-locked weights.

---

## SECTION 3: ADVANCED EXPLORATION PROMPTS

### PROMPT F: Information-Theoretic Analysis

**Context**: We're making a chip that runs ONE model forever. What are the theoretical limits?

**Questions**:

1. **Model Capacity vs. Chip Capacity**:
   - A chip with N transistors can represent how many bits of model?
   - What's the Landauer limit for computation at temperature T?
   - How close can we get to thermodynamic minimum energy per inference?

2. **Rate-Distortion for Ternary Networks**:
   - What's the optimal ternary approximation of a full-precision network?
   - Derive rate-distortion curve: bits per weight vs. accuracy loss
   - Where does BitNet b1.58 sit on this curve?

3. **Entropy of Output Distribution**:
   - Each token generated is a sample from probability distribution
   - What's the entropy of typical LLM output?
   - Can we derive minimum compute required to generate that entropy?

**Deliverable**: Information-theoretic bounds on inference efficiency.

---

### PROMPT G: Power Modeling and Optimization

**Context**: Target is 2-3W total power for 2B ternary model at 25-80 tok/s.

**Power Breakdown** (typical AI accelerator):
- Memory access: 60-70% of total power
- Computation: 20-30%
- Control/IO: 10%

**For mask-locked**:
- Memory access for weights: 0% (eliminated)
- Memory access for KV cache: still present
- Computation: same
- Control: potentially simpler (fixed function)

**Questions**:

1. **Derive Power Equation**:
   - P_total = P_KV_access + P_compute + P_control + P_IO
   - Model each term mathematically
   - What's the dominant term for mask-locked?

2. **Energy per Token**:
   - Derive formula: Energy/token = f(model_size, sequence_length, process_node)
   - Compare theoretical minimum vs. practical implementation
   - What's the efficiency gap?

3. **Thermal Analysis**:
   - At 3W in a small package (assume 10mm × 10mm die)
   - What's the junction temperature rise?
   - Derive thermal constraints on sustained operation

**Deliverable**: Mathematical power model with optimization levers.

---

### PROMPT H: Parallelism and Pipelining Analysis

**Context**: LLM inference has inherent sequential nature (token n depends on token n-1).

**Questions**:

1. **Parallelism Limits**:
   - What operations WITHIN a token can be parallelized?
   - What's the critical path through the transformer?
   - Derive minimum latency per token (not throughput)

2. **Pipelining Opportunities**:
   - Can we pipeline across layers? (Layer 2 starts before Layer 1 finishes)
   - What's the pipeline efficiency η = (useful work) / (total time)?
   - Derive optimal pipeline depth

3. **Speculative Execution**:
   - Can we predict future tokens and compute ahead?
   - What's the mathematical framework for speculative decoding?
   - How does speculation interact with mask-locked architecture?

**Deliverable**: Analysis of parallelism opportunities in mask-locked inference.

---

## SECTION 4: NOVEL DIRECTION PROMPTS

### PROMPT I: Unconventional Computing Paradigms

**Context**: Traditional inference does: Load → Compute → Store → Repeat

**Question**: What if we rethought the entire paradigm?

**Ideas to Explore**:

1. **Analog Computation**:
   - Can ternary weights be represented as voltage levels?
   - What's the SNR requirement for equivalent accuracy?
   - Would analog be more power-efficient than digital for inference?

2. **In-Memory Computing**:
   - 2T1C DRAM from KAIST claims ADC-free MAC operations
   - How would this work with ternary weights?
   - Derive the mathematical operation of ternary MAC in DRAM

3. **Stochastic Computing**:
   - Represent numbers as probability of 1 in a bit stream
   - Multiplication becomes AND gate
   - Addition becomes MUX
   - Can ternary operations be mapped to stochastic computing?

4. **Reversible Computing**:
   - Landauer's principle: bit erasure costs kT ln(2) energy
   - Reversible computing avoids bit erasure
   - Is there a reversible formulation of matrix multiplication?

**Deliverable**: Analysis of at least one unconventional paradigm applied to mask-locked inference.

---

### PROMPT J: Model Architecture Co-Design

**Context**: We're not running arbitrary models—we can design models specifically for mask-locked hardware.

**Questions**:

1. **Hardware-Friendly Architecture**:
   - What transformer modifications reduce KV cache size?
   - Are there architectures that naturally fit ternary weights better?
   - Derive the relationship between architecture choice and hardware efficiency

2. **Sparse Attention Patterns**:
   - Not all attention heads are equally important
   - Can we design fixed sparse attention patterns that maintain quality?
   - What's the optimal sparsity pattern for ternary weights?

3. **Layer-wise Precision**:
   - Not all layers need same precision
   - Can we derive which layers need INT8 vs INT4 vs ternary?
   - What's the mathematical criterion for precision allocation?

**Deliverable**: Model architecture recommendations optimized for mask-locked hardware.

---

## SECTION 5: VALIDATION AND BENCHMARKS

### Required Outputs from Each Agent

1. **Mathematical Derivations**: Show your work, state assumptions clearly
2. **Numerical Estimates**: Where applicable, compute actual values for our target configuration:
   - Model: 2B parameters, ternary
   - Context: 4K tokens (reduce if necessary)
   - Power: 3W
   - Process: 28nm

3. **Comparison to Baseline**: Always compare to:
   - Traditional GPU inference
   - Groq LPU approach
   - Etched Sohu approach

4. **Implementation Feasibility**: Comment on whether your optimization is:
   - Theoretical only (requires future research)
   - Near-term feasible (could implement in 1-2 years)
   - Ready now (well-understood, just needs engineering)

---

## SECTION 6: KEY CONSTRAINTS AND PARAMETERS

### Fixed Parameters (Do Not Change)
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Target Price | $35-60 | Market gap below Jetson |
| Target Power | 2-3W | USB-powered, passive cooling |
| Process Node | 28nm | Low NRE, mature supply chain |
| Model Size | 1-3B params | Fits in reasonable die area |
| Target Throughput | 25-80 tok/s | Usable for real-time chat |

### Flexible Parameters (Optimize These)
| Parameter | Range | Tradeoffs |
|-----------|-------|-----------|
| Weight Precision | Ternary to INT8 | Area vs. quality |
| KV Cache Precision | INT4 to FP16 | Bandwidth vs. quality |
| Context Length | 512 to 4096 | Memory vs. utility |
| Clock Frequency | 200-500 MHz | Power vs. throughput |
| SRAM Size | 4-16 MB | Cost vs. context |

### Reference Implementations
| System | Performance | Power | Relevance |
|--------|-------------|-------|-----------|
| TeLLMe FPGA (KV260) | 25 tok/s | 4.8W | Achievable baseline |
| Hailo-10H | 9.5 tok/s (1.5B) | ~5W | Competitive benchmark |
| Jetson Orin Nano | 20-30 tok/s (7B) | 10-15W | Mainstream alternative |
| Taalas HC1 | 14,000 tok/s (8B) | ~200W | Data center reference |

---

## SECTION 7: OUTPUT FORMAT REQUESTED

Please structure your findings as:

```
# Analysis: [PROMPT LETTER] - [TITLE]

## Summary
[2-3 sentence key finding]

## Mathematical Framework
[Derivations, equations, proofs]

## Numerical Results
[Specific calculations for our parameters]

## Comparison to Baseline
[How does this compare to existing approaches?]

## Implementation Recommendation
[Is this feasible? What's the path to implementation?]

## Open Questions
[What remains unknown or requires further investigation?]
```

---

*Document Version: 1.0*
*Created: March 2026*
*For: Math and Logic Specialist Agents*
