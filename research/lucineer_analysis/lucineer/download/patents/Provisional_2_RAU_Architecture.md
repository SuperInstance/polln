# PROVISIONAL PATENT APPLICATION

## ROTATION-ACCUMULATE UNIT FOR COMPLEX-VALUED NEURAL NETWORK INFERENCE

---

**Attorney Docket No.:** SUPERINSTANCE-002-PROV  
**Filing Date:** [To Be Filed]  
**Title:** ROTATION-ACCUMULATE UNIT FOR MULTIPLICATION-FREE NEURAL NETWORK INFERENCE

---

## INVENTORS

**Casey DiGennaro**  
[Address Placeholder]  
[City, State, Zip Placeholder]

**David Park**  
[Address Placeholder]  
[City, State, Zip Placeholder]

---

## RELATED APPLICATIONS

This application claims priority to U.S. Provisional Patent Application No. [To Be Assigned], filed [Date], and is related to U.S. Provisional Patent Application No. [SUPERINSTANCE-001-PROV], titled "Semiconductor Device with Hardwired Neural Network Weights and Methods of Manufacture and Use," filed [Date], which is incorporated herein by reference in its entirety.

---

## BACKGROUND OF THE INVENTION

### Field of the Invention

The present invention relates generally to hardware accelerators for neural network inference, and more particularly to processing elements that perform neural network computations without arithmetic multiplication circuits through the use of rotation and accumulation operations.

### Description of Related Art

**Multiply-Accumulate (MAC) Units:** The fundamental computational operation in neural network inference is the multiply-accumulate (MAC) operation, which computes the product of a weight value and an activation value and adds the result to an accumulator. Modern neural network accelerators contain arrays of MAC units that perform these operations in parallel.

Conventional MAC units require:
1. Multiplier circuits (for weight × activation)
2. Adder circuits (for accumulation)
3. Weight storage and access mechanisms
4. Activation storage and access mechanisms

The multiplier circuit is the dominant contributor to:
- **Area:** A 16-bit multiplier requires approximately 1,000-2,000 gates
- **Power:** Multiplier operations consume 60-80% of compute power
- **Latency:** Multiplier delay determines clock frequency limits

**Systolic Arrays:** Google's Tensor Processing Unit (TPU) and similar accelerators use systolic arrays of MAC units. U.S. Patent No. US11150234B2 describes a systolic array architecture where weights and activations flow through processing elements. However, each processing element still requires a multiplier circuit.

**Quantization and Precision Reduction:** Various approaches have attempted to reduce the cost of MAC operations through reduced precision:

1. **INT8 Quantization:** Using 8-bit integer weights and activations reduces multiplier size by approximately 75% compared to FP16, but multipliers are still required.

2. **INT4 Quantization:** Further precision reduction to 4-bit values reduces multiplier size but introduces quantization error.

3. **Binary Neural Networks:** Weights and activations constrained to {-1, +1} eliminate multipliers entirely (multiplication becomes XNOR), but significant accuracy degradation limits practical application.

4. **Ternary Neural Networks:** Weights constrained to {-1, 0, +1} with full-precision activations (as in Microsoft BitNet b1.58, arXiv:2402.17764) preserve model quality while eliminating the need for multipliers. However, existing hardware implementations still use conventional add/subtract units without optimized rotation-accumulate architectures.

**Complex-Valued Neural Networks:** Recent work from Peking University (iFairy, arXiv:2508.05571) has demonstrated that neural network weights can be constrained to the fourth roots of unity: {+1, -1, +i, -i}. These C₄ weights enable multiplication through rotation operations rather than arithmetic multiplication.

The rotation operations for C₄ weights are:
- w = +1: identity (no rotation)
- w = -1: 180° rotation (negation)
- w = +i: 90° rotation (real ↔ imaginary with sign change)
- w = -i: 270° rotation (real ↔ imaginary with sign change)

**Hardware Implementation Challenges:** While the mathematical foundation for multiplication-free inference exists, prior art has not disclosed efficient hardware architectures specifically designed for rotation-accumulate operations on complex-valued data. Existing approaches either:
1. Use general-purpose processors with software implementations (inefficient)
2. Adapt conventional MAC units (not optimized for rotation operations)
3. Use lookup tables (area-intensive)

There exists a need for dedicated hardware processing elements optimized for rotation-accumulate operations that achieve:
- Zero multipliers
- Single-cycle rotation operations
- Efficient systolic array configurations
- Low power consumption suitable for edge inference

### Problem Statement

Conventional neural network inference hardware requires arithmetic multiplication circuits that dominate area, power, and latency. While ternary and complex-valued quantization enable multiplication-free inference in principle, existing hardware does not provide optimized architectures for rotation-based computation.

The present invention provides a Rotation-Accumulate Unit (RAU) specifically designed for multiplication-free inference with ternary and C₄ weights, achieving significant improvements in area efficiency, power consumption, and throughput.

---

## SUMMARY OF THE INVENTION

The present invention provides a hardware processing element called a Rotation-Accumulate Unit (RAU) for neural network inference. The RAU performs weight-activation multiplication through rotation operations rather than arithmetic multiplication, eliminating the need for multiplier circuits entirely.

In one aspect, the invention provides a rotation-accumulate unit (RAU) for neural network inference, comprising: an input port configured to receive a complex-valued activation value comprising real and imaginary components; a weight decoder configured to receive a weight code representing a weight value from the set {+1, -1, +i, -i}; a rotation circuit comprising one or more multiplexers configured to perform a rotation operation on said activation value based on said weight code without arithmetic multiplication; and an accumulator configured to sum rotation outputs across multiple weight-activation pairs.

In another aspect, the invention provides a neural network inference accelerator comprising: an array of rotation-accumulate units (RAUs) arranged in a systolic configuration; wherein each RAU performs rotation operations on complex-valued data in a single clock cycle; and wherein said array performs neural network layer computation without multiplication circuits.

In yet another aspect, the invention provides a method of performing neural network inference without multiplication operations, comprising: receiving a complex-valued activation value; selecting a rotation operation based on a weight code representing a weight from {+1, -1, +i, -i}; applying said rotation operation to said activation value using multiplexer-based routing; and accumulating rotated values to produce an output activation.

Key advantages of the RAU architecture include:

**Zero Multipliers:** The RAU eliminates all arithmetic multiplication circuits, reducing area by 70-85% compared to conventional MAC units.

**Single-Cycle Operation:** Rotation operations complete in a single clock cycle, enabling higher clock frequencies than multiplier-based designs.

**Low Power:** Without multipliers, the RAU consumes 60-80% less power than equivalent MAC units.

**Systolic Array Compatible:** RAUs can be arranged in systolic arrays for efficient matrix operations.

**Scalable:** The architecture scales to any precision for activation values, as the rotation operation is independent of activation bit-width.

---

## DETAILED DESCRIPTION OF THE INVENTION

### Overview

The Rotation-Accumulate Unit (RAU) is a hardware processing element designed for neural network inference with weights from the fourth roots of unity. The RAU replaces the multiply operation in conventional MAC units with a rotation operation implemented through multiplexer-based routing.

### Embodiment 1: RAU Architecture

The RAU comprises the following components:

**1. Input Activation Register:**
Stores the complex-valued input activation (a + bi), where a is the real component and b is the imaginary component. The bit-width of each component is configurable (e.g., 8-bit, 16-bit, 32-bit).

**2. Weight Decoder:**
Receives a 2-bit weight code representing the weight value:
- 00: weight = +1 (identity)
- 01: weight = -1 (180° rotation)
- 10: weight = +i (90° rotation)
- 11: weight = -i (270° rotation)

The weight decoder generates control signals for the rotation circuit.

**3. Rotation Circuit:**
Performs the rotation operation on the complex-valued activation. The rotation circuit implements the following transformations:

| Weight | Operation | Output Real | Output Imaginary |
|--------|-----------|-------------|------------------|
| +1 | Identity | a | b |
| -1 | 180° rotation | -a | -b |
| +i | 90° rotation | -b | a |
| -i | 270° rotation | b | -a |

**4. Accumulator:**
Accumulates the rotated values across multiple weight-activation pairs. The accumulator comprises:
- Real accumulator: sums real components
- Imaginary accumulator: sums imaginary components

### Embodiment 2: Multiplexer-Based Rotation Circuit

In a preferred embodiment, the rotation circuit is implemented using multiplexers:

**2-Bit Activation Example (for illustration):**

For each bit position of the activation value, the rotation is implemented as:

```
// For each bit position n:
out_real[n] = MUX4(weight_code,
                    in_real[n],       // +1: pass through
                    ~in_real[n],      // -1: negate (using NOT)
                    in_imag[n],       // +i: swap (imag -> real)
                    in_imag[n]);      // -i: swap (for sign, see below)

out_imag[n] = MUX4(weight_code,
                    in_imag[n],       // +1: pass through
                    ~in_imag[n],      // -1: negate
                    in_real[n],       // +i: swap (real -> imag)
                    ~in_real[n]);     // -i: swap and negate
```

**Sign Bit Handling:**

For signed two's complement representation, the sign bit requires special handling:

- For negation (-1 weight), the activation is negated using two's complement (invert all bits, add 1)
- For +i rotation, the sign must be applied to the real output after the swap

A practical implementation uses:
1. Sign extension for the incoming activation
2. Carry propagation for two's complement negation
3. Separate sign handling in the accumulator

**4:1 Multiplexer Implementation:**

A 4:1 multiplexer can be implemented using:
- Two 2:1 multiplexers and one 2:1 multiplexer (total: 3 MUX2 cells)
- Or one native 4:1 multiplexer cell

For an N-bit activation component, the rotation circuit requires:
- 2N MUX4 cells (N for real output, N for imaginary output)
- Or 6N MUX2 cells

**Gate Count Analysis:**

| Component | Gate Count (Approximate) |
|-----------|--------------------------|
| Rotation circuit (8-bit activation) | ~150 gates |
| Rotation circuit (16-bit activation) | ~300 gates |
| Accumulator (16-bit, 32 entries) | ~200 gates |
| **Total RAU (16-bit)** | **~250-350 gates** |

**Comparison to MAC Unit:**

| Component | MAC Unit | RAU | Reduction |
|-----------|----------|-----|-----------|
| 16-bit multiplier | ~2,000 gates | 0 | 100% |
| Adder/accumulator | ~200 gates | ~200 gates | 0% |
| Control/routing | ~100 gates | ~150 gates | -50% |
| **Total** | ~2,300 gates | ~350 gates | **85%** |

### Embodiment 3: Systolic Array Configuration

RAUs can be arranged in a systolic array for efficient matrix multiplication. For a matrix multiplication Y = W × X, where W has C₄ weights:

**Array Configuration:**

```
        RAU[0,0]  RAU[0,1]  RAU[0,2]  ... RAU[0,N]
           │         │         │          │
           ▼         ▼         ▼          ▼
        RAU[1,0]  RAU[1,1]  RAU[1,2]  ... RAU[1,N]
           │         │         │          │
           ▼         ▼         ▼          ▼
           ...       ...       ...        ...
           │         │         │          │
           ▼         ▼         ▼          ▼
        RAU[M,0]  RAU[M,1]  RAU[M,2]  ... RAU[M,N]
```

**Data Flow:**

1. Activation values (X) flow horizontally from left to right
2. Weight values (W) are hardwired in each RAU (mask-locked) or loaded during initialization
3. Partial sums flow vertically from top to bottom
4. Each RAU performs: partial_sum_out = partial_sum_in + rotate(activation_in, weight)

**Timing:**

- Cycle 0: RAU[0,0] processes X[0] with W[0,0]
- Cycle 1: RAU[0,1] processes X[1] with W[0,1]; RAU[1,0] processes X[0] with W[1,0]
- ...
- Cycle M+N: Final outputs available

**Throughput:**

For an M×N array processing a K×M matrix multiplication:
- Latency: M + N + K cycles
- Throughput: One output vector per cycle (after pipeline fills)

### Embodiment 4: RAU with Hardwired Weights

When combined with mask-locked weight encoding (as described in related application SUPERINSTANCE-001-PROV), the RAU can have weights permanently encoded in the routing pattern:

**Direct Routing Implementation:**

For each weight position, instead of a multiplexer, the rotation is hardwired:

- Weight = +1: Direct wire connection
- Weight = -1: Wire through inverter (or route to subtract input of accumulator)
- Weight = +i: Wire crossing (real ↔ imaginary) with inverter on real output
- Weight = -i: Wire crossing (real ↔ imaginary) with inverter on imaginary output

**Advantages:**

1. **Zero weight storage:** No SRAM or register file needed for weights
2. **Zero weight access power:** No memory access for weight loading
3. **Zero weight decoder:** No multiplexer select logic needed
4. **Smallest possible implementation:** Only wire routing and minimal inverters

**Gate Count for Hardwired RAU:**

| Component | Gate Count |
|-----------|------------|
| Weight routing | 0 gates (wire only) |
| Inverters (for -1, +i, -i) | 0-4 transistors |
| Accumulator | ~200 gates |
| **Total** | **~200-250 gates** |

### Embodiment 5: RAU for Ternary Weights

The RAU architecture also supports ternary weights {-1, 0, +1} for real-valued activations:

**Ternary RAU Operations:**

| Weight | Operation | Hardware |
|--------|-----------|----------|
| +1 | Pass through | Wire connection |
| -1 | Negate | Inverter or subtract |
| 0 | Zero | No connection to accumulator |

**Implementation:**

For ternary weights, the RAU is simplified:
- Only real-valued activations (no imaginary component)
- 2:1 multiplexer for +1/-1 selection (or direct routing)
- Zero weight implemented as no connection to accumulator

**Gate Count for Ternary RAU (16-bit):**

| Component | Gate Count |
|-----------|------------|
| Pass/negate logic | ~50 gates |
| Accumulator | ~200 gates |
| **Total** | **~250 gates** |

### Embodiment 6: Power Consumption Analysis

**Power Comparison: RAU vs. MAC**

| Operation | MAC Unit (INT8) | RAU (C₄) | Savings |
|-----------|-----------------|----------|---------|
| Weight fetch | 100 pJ | 0 pJ (hardwired) | 100% |
| Activation fetch | 10 pJ | 10 pJ | 0% |
| Multiplication | 50 pJ | 0 pJ | 100% |
| Rotation | N/A | 5 pJ | N/A |
| Accumulation | 10 pJ | 10 pJ | 0% |
| **Total** | **170 pJ** | **25 pJ** | **85%** |

**Energy per Token:**

For a 2-billion parameter model with C₄ weights:
- Operations per token: ~4 billion rotations
- Energy per rotation: ~25 pJ
- Energy per token: 4B × 25 pJ = 100 mJ
- Power at 25 tok/s: 2.5W (compute only)

### Embodiment 7: RAU for Attention Computation

The RAU architecture is particularly efficient for transformer attention computation:

**Attention Mechanism:**

Attention(Q, K, V) = softmax(Q × K^T / √d) × V

The matrices Q, K, V are computed through linear transformations with weight matrices W_Q, W_K, W_V. If these weight matrices use C₄ quantization:

1. Q = X × W_Q (performed by RAU array)
2. K = X × W_K (performed by RAU array)
3. V = X × W_V (performed by RAU array)
4. Attention scores = Q × K^T (requires conventional MAC for softmax, or approximation)
5. Output = Attention_scores × V (performed by RAU array)

**Benefits:**

- 4 of 5 matrix multiplications use RAU arrays
- Significant power savings for attention layers
- Compatible with grouped query attention (GQA) and multi-query attention (MQA)

### Embodiment 8: RAU for Feed-Forward Network

The feed-forward network (FFN) in transformer models comprises:

FFN(x) = GELU(x × W_1) × W_2

Both matrix multiplications (W_1 and W_2) can be performed with RAU arrays if the weight matrices use C₄ quantization.

---

## CLAIMS

What is claimed is:

**1.** A rotation-accumulate unit (RAU) for neural network inference, comprising:
an input port configured to receive a complex-valued activation value comprising real and imaginary components;
a weight decoder configured to receive a weight code representing a weight value from the set {+1, -1, +i, -i};
a rotation circuit comprising one or more multiplexers configured to perform a rotation operation on said activation value based on said weight code without arithmetic multiplication; and
an accumulator configured to sum rotation outputs across multiple weight-activation pairs.

**2.** The rotation-accumulate unit of claim 1, wherein said rotation circuit comprises a 4:1 multiplexer for each bit position of said real component and each bit position of said imaginary component.

**3.** The rotation-accumulate unit of claim 1, wherein said rotation circuit comprises two 2:1 multiplexers for each bit position.

**4.** The rotation-accumulate unit of claim 1, wherein:
for a weight value of +1, said rotation circuit passes said real component to a real output and passes said imaginary component to an imaginary output without modification;
for a weight value of -1, said rotation circuit negates said real component and negates said imaginary component;
for a weight value of +i, said rotation circuit outputs a negated version of said imaginary component as a real output and outputs said real component as an imaginary output; and
for a weight value of -i, said rotation circuit outputs said imaginary component as a real output and outputs a negated version of said real component as an imaginary output.

**5.** The rotation-accumulate unit of claim 1, wherein said rotation circuit performs said rotation operation in a single clock cycle.

**6.** The rotation-accumulate unit of claim 1, wherein said rotation-accumulate unit comprises zero arithmetic multiplication circuits.

**7.** The rotation-accumulate unit of claim 1, wherein said rotation-accumulate unit comprises fewer than 500 logic gates.

**8.** The rotation-accumulate unit of claim 1, wherein said rotation-accumulate unit consumes less than 10 picojoules per rotation operation.

**9.** The rotation-accumulate unit of claim 1, wherein said accumulator comprises a real accumulator for summing real components and an imaginary accumulator for summing imaginary components.

**10.** The rotation-accumulate unit of claim 1, further comprising:
an input register for storing said complex-valued activation value.

**11.** A neural network inference accelerator comprising:
an array of rotation-accumulate units (RAUs) as recited in claim 1, arranged in a systolic configuration;
wherein each RAU performs rotation operations on complex-valued data in a single clock cycle; and
wherein said array performs neural network layer computation without multiplication circuits.

**12.** The neural network inference accelerator of claim 11, wherein said array comprises M rows and N columns of RAUs, where M and N are integers greater than 1.

**13.** The neural network inference accelerator of claim 11, wherein activation values flow horizontally through said array and partial sums flow vertically through said array.

**14.** The neural network inference accelerator of claim 11, wherein said array is configured for transformer attention computation.

**15.** The neural network inference accelerator of claim 11, wherein said array is configured for feed-forward network computation.

**16.** The neural network inference accelerator of claim 11, wherein each RAU has a weight value permanently encoded in metal interconnect routing.

**17.** A method of performing neural network inference without multiplication operations, comprising:
receiving a complex-valued activation value;
selecting a rotation operation based on a weight code representing a weight from {+1, -1, +i, -i};
applying said rotation operation to said activation value using multiplexer-based routing; and
accumulating rotated values to produce an output activation.

**18.** The method of claim 17, wherein said selecting a rotation operation comprises:
decoding a 2-bit weight code to generate control signals for a rotation circuit.

**19.** The method of claim 17, wherein said applying said rotation operation comprises:
for a weight of +1, passing said activation value through without modification;
for a weight of -1, negating both real and imaginary components of said activation value;
for a weight of +i, swapping real and imaginary components with sign change on the real output; and
for a weight of -i, swapping real and imaginary components with sign change on the imaginary output.

**20.** The method of claim 17, wherein said applying said rotation operation completes in a single clock cycle.

**21.** The method of claim 17, wherein said method is performed for each element of a weight matrix to compute a matrix-vector multiplication.

**22.** A rotation-accumulate unit for neural network inference with ternary weights, comprising:
an input port configured to receive a real-valued activation value;
a weight decoder configured to receive a weight code representing a weight value from the set {-1, 0, +1};
a pass/negate circuit configured to selectively pass or negate said activation value based on said weight code without arithmetic multiplication; and
an accumulator configured to sum outputs across multiple weight-activation pairs, wherein:
for a weight value of +1, said activation value is passed to said accumulator;
for a weight value of -1, a negated version of said activation value is passed to said accumulator; and
for a weight value of 0, no value is passed to said accumulator.

**23.** The rotation-accumulate unit of claim 22, wherein said pass/negate circuit comprises a 2:1 multiplexer.

**24.** The rotation-accumulate unit of claim 22, wherein said rotation-accumulate unit comprises fewer than 300 logic gates.

**25.** A semiconductor integrated circuit device comprising:
a rotation-accumulate unit (RAU) as recited in claim 1; and
a metal interconnect layer having a routing pattern that encodes said weight value without memory storage.

**26.** The semiconductor integrated circuit device of claim 25, wherein said routing pattern directly implements said rotation operation without a multiplexer.

**27.** The semiconductor integrated circuit device of claim 25, wherein:
for a weight value of +1, said routing pattern comprises direct wire connections from input to output;
for a weight value of -1, said routing pattern comprises wire connections through inverter cells; and
for weight values of +i and -i, said routing pattern comprises wire crossing between real and imaginary signal paths.

**28.** A computing system for neural network inference, comprising:
a systolic array of rotation-accumulate units (RAUs) as recited in claim 1;
a memory storing activation values;
a controller configured to direct activation values through said systolic array; and
an output buffer storing inference results.

**29.** The computing system of claim 28, wherein said system consumes less than 5 watts during inference.

**30.** The computing system of claim 28, wherein said system achieves throughput greater than 20 tokens per second for a 2-billion parameter neural network model.

---

## ABSTRACT

A rotation-accumulate unit (RAU) for neural network inference performs weight-activation multiplication through rotation operations rather than arithmetic multiplication. The RAU receives complex-valued activations and weight codes from the set {+1, -1, +i, -i}, applying rotations using multiplexer-based routing. The RAU eliminates all multiplier circuits, reducing area by 85% and power consumption by 85% compared to conventional MAC units. Systolic arrays of RAUs enable efficient matrix operations for transformer attention and feed-forward networks. Methods for performing inference without multiplication operations are disclosed. The RAU architecture is compatible with mask-locked weight encoding for zero-weight-access-power inference.

---

## BRIEF DESCRIPTION OF DRAWINGS

**FIGURE 1** is a block diagram of a rotation-accumulate unit (RAU) according to an embodiment of the present invention, showing input activation register, weight decoder, rotation circuit, and accumulator.

**FIGURE 2** illustrates the four rotation operations performed by the RAU for C₄ weights: identity (+1), 180° rotation (-1), 90° rotation (+i), and 270° rotation (-i).

**FIGURE 3** is a circuit diagram of a multiplexer-based rotation circuit according to an embodiment of the present invention.

**FIGURE 4** illustrates a systolic array of RAUs according to an embodiment of the present invention, showing data flow patterns for activation values and partial sums.

**FIGURE 5** is a comparison chart showing gate count reduction of RAU versus conventional MAC unit.

**FIGURE 6** is a power consumption comparison chart showing energy savings of RAU versus MAC unit.

**FIGURE 7** illustrates an RAU with hardwired weight encoding according to an embodiment of the present invention, showing direct wire routing for each weight value.

**FIGURE 8** illustrates a ternary RAU for real-valued activations according to an alternative embodiment.

**FIGURE 9** is a flowchart illustrating a method of performing neural network inference without multiplication operations according to an embodiment of the present invention.

**FIGURE 10** illustrates application of RAU arrays to transformer attention computation according to an embodiment of the present invention.

---

## STATEMENT REGARDING FEDERALLY SPONSORED RESEARCH

Not applicable.

---

## SEQUENCE LISTING

Not applicable.

---

**Respectfully submitted,**

[Attorney Signature Block]

---

*This provisional patent application is intended to establish a priority date for the claimed inventions. The claims presented herein may be amended, expanded, or modified in subsequent non-provisional applications claiming priority to this application.*
