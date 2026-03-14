# QSPEC and Speculative Decoding for Edge Deployment: Comprehensive Research Report

## Executive Summary

This report analyzes QSPEC (arXiv:2410.11305) and alternative speculative decoding approaches for edge deployment scenarios. QSPEC presents a novel approach using "complementary quantization" but has significant limitations for single-user edge devices. Alternative approaches like Medusa, EAGLE, and traditional draft-model speculative decoding offer different trade-offs.

---

## 1. QSPEC Paper Analysis

### 1.1 Paper Details
- **Title**: "QSpec: Speculative Decoding with Complementary Quantization Schemes"
- **Authors**: Juntao Zhao, Wenhao Lu, Sheng Wang, Lingpeng Kong, Chuan Wu (HKU)
- **Venue**: EMNLP 2025 (Main Conference)
- **arXiv**: 2410.11305
- **Code**: https://github.com/hku-netexplo-lab/QSpec

### 1.2 What is "Complementary Quantization"?

QSPEC's key innovation is combining **two quantization schemes** via speculative decoding:

1. **Low-Precision Joint Quantization (Draft Phase)**
   - Activation-weight joint quantization (e.g., W4A8, INT4 weights with INT8 activations)
   - Very fast inference but suffers quality degradation on reasoning tasks
   - Used for fast drafting of candidate tokens

2. **High-Precision Weight-Only Quantization (Verification Phase)**
   - Weight-only quantization (e.g., W8A16, INT8 weights with FP16 activations)
   - Higher quality but slower
   - Used for accurate verification of draft tokens

**Key Insight**: The same model weights are stored in both quantized formats, but the KV cache is shared between phases, minimizing memory overhead.

### 1.3 How Does QSPEC Achieve "Zero Memory Overhead"?

The "near-zero-cost switching" claim is based on:

1. **Shared KV Cache**: Both draft and verification phases use the same KV cache, avoiding duplication
2. **Same Model, Different Quantization**: No separate draft model needed - the same model is quantized two ways
3. **No Retraining Required**: Works with existing quantized models plug-and-play

**Reality Check**: There IS memory overhead:
- Need to store weights in both quantized formats (e.g., ~1.5-2x weight storage)
- The "zero overhead" refers to avoiding a separate smaller draft model's parameters
- For a 7B model: ~7GB (W4A8) + ~14GB (W8A16) ≈ 21GB total vs 14GB for single-precision

### 1.4 Speedup Claims

| Model | Baseline | QSpec Speedup | Batch Size |
|-------|----------|---------------|------------|
| LLaMA-2-7B | W8A16 | 1.64x | Batch=1 |
| LLaMA-2-13B | W8A16 | 1.52x | Batch=1 |
| LLaMA-2-70B | W8A16 | 1.55x | Batch=1 |

**Key Result**: Outperforms state-of-the-art speculative decoding by up to 1.55x in batched settings.

### 1.5 Limitations

1. **Memory Overhead**: Requires storing 2 quantized versions of weights
2. **Batch-Dependent Performance**: Gains diminish at small batch sizes (edge scenario)
3. **Quantization Method Dependent**: Requires compatible quantization schemes
4. **No Quality Improvement**: Only speed - doesn't fix quantization quality issues
5. **Hardware Dependent**: Benefits vary significantly based on memory bandwidth vs compute ratio

---

## 2. Edge Deployment Suitability Analysis

### 2.1 Does QSPEC Work for Single-User Edge Devices?

**Short Answer: Not optimally.**

**Detailed Analysis**:

| Factor | QSPEC Behavior | Edge Implication |
|--------|----------------|------------------|
| Batch Size | Optimized for batch > 1 | Edge typically batch=1 |
| Memory Bandwidth | High bandwidth benefit | Edge devices have limited bandwidth |
| Memory Capacity | 1.5-2x weight storage | Edge devices are memory-constrained |
| Acceptance Rate | Lower at batch=1 | Less speedup opportunity |

### 2.2 Batch Size Requirements

**QSPEC is optimized for server-side batched inference**:

- **Best Performance**: Batch sizes 4-32
- **Diminishing Returns**: Batch < 4
- **Edge Reality**: Single-user devices typically batch=1

**Why This Matters**:
- Speculative decoding benefits from parallel verification
- At batch=1, the memory-bound verification phase dominates
- Draft generation overhead becomes proportionally larger

### 2.3 True Memory Overhead

For a 7B parameter model on edge device:

| Configuration | Memory Required | Notes |
|--------------|-----------------|-------|
| FP16 Baseline | 14 GB | Full precision |
| INT8 Weight-Only | 7 GB | Standard quantization |
| INT4 Joint Quant | 3.5 GB | Aggressive quantization |
| **QSPEC (W4 + W8)** | ~10.5 GB | Both formats |

**Edge Device Reality**:
- Mobile devices: 4-8 GB RAM total
- Edge AI accelerators: 8-16 GB dedicated
- QSPEC's 10.5 GB for a 7B model is challenging

---

## 3. Alternative Speculative Decoding Approaches

### 3.1 Traditional Draft Model Approach

**Papers**: "Fast Inference from Transformers via Speculative Decoding" (Leviathan et al., 2023)

**Mechanism**:
- Small draft model (e.g., 7B drafting for 70B target)
- Draft generates K tokens
- Target model verifies all K tokens in parallel
- Accept/reject based on probability distribution match

**Edge Suitability**:
| Pros | Cons |
|------|------|
| Well-understood | Need separate draft model |
| Good acceptance rates | 2x memory for models |
| Lossless speedup | Draft model must be tuned |

**Speedup**: 2-3x for well-matched draft/target pairs

### 3.2 Medusa Heads (arXiv:2401.10774)

**Paper**: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"

**Mechanism**:
- Add multiple decoding heads on top of the model
- Each head predicts tokens at different positions (t+1, t+2, t+3...)
- Tree-based attention for parallel verification
- No separate draft model needed

**Key Features**:
- **Medusa-1**: Fine-tune heads only (frozen backbone)
- **Medusa-2**: Fine-tune heads + backbone together
- Self-distillation when no training data available

**Edge Suitability**:
| Pros | Cons |
|------|------|
| No separate model | Requires fine-tuning |
| 2.2-3.6x speedup | Additional head parameters |
| Tree attention efficient | Complex implementation |

**Memory Overhead**: ~10-20% extra parameters for heads

**Speedup Results**:
- Medusa-1: 2.2x speedup
- Medusa-2: 2.3-3.6x speedup

### 3.3 EAGLE (arXiv:2401.15077)

**Paper**: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty"

**Mechanism**:
- Operates at feature level (second-to-top-layer), not token level
- Uses token sequence advanced by one step to reduce uncertainty
- Lightweight draft network for feature prediction
- Only 1 decoder layer + embedding as draft model

**Key Innovation**:
- Feature-level autoregression is simpler than token-level
- Resolves uncertainty by conditioning on advanced token sequence

**Edge Suitability**:
| Pros | Cons |
|------|------|
| Very lightweight draft | Requires feature extraction |
| 2.7-3.5x speedup | Needs training |
| Works with MoE models | Model-specific implementation |

**Speedup Results**:
- LLaMA2-Chat 70B: 2.7x-3.5x speedup
- Doubles throughput
- Maintains output distribution

### 3.4 Lookahead Decoding / N-gram Speculation

**Mechanism**:
- Use n-gram patterns to predict future tokens
- No neural draft model required
- Verify predicted tokens in parallel

**Edge Suitability**:
| Pros | Cons |
|------|------|
| Zero memory overhead | Lower acceptance rates |
| No training required | Domain-dependent |
| Simple implementation | Limited speedup (1.2-1.5x) |

### 3.5 Comparison Table

| Approach | Memory Overhead | Training Required | Speedup | Edge Suitability |
|----------|-----------------|-------------------|---------|------------------|
| **QSPEC** | 50-100% (2 quantizations) | No | 1.5-1.6x | Poor (batch-dependent) |
| **Draft Model** | 50-200% (separate model) | Yes (draft training) | 2-3x | Moderate |
| **Medusa** | 10-20% (extra heads) | Yes (fine-tuning) | 2.2-3.6x | Good |
| **EAGLE** | 5-10% (1 decoder layer) | Yes (light training) | 2.7-3.5x | Good |
| **N-gram** | 0% | No | 1.2-1.5x | Excellent |
| **Self-Speculation** | 0% | No | 1.3-1.7x | Excellent |

---

## 4. Implementation Complexity Analysis

### 4.1 SDK Changes Required

#### QSPEC Implementation Requirements:

```python
# Conceptual SDK changes needed
class QSpecInference:
    def __init__(self, model):
        self.w4a8_weights = quantize_joint(model, W4A8)  # Draft
        self.w8a16_weights = quantize_weight_only(model, W8A16)  # Verify
        self.shared_kv_cache = KVCache()
    
    def forward(self, tokens):
        # 1. Draft phase with low-precision
        draft_tokens = self.draft_forward(tokens)
        
        # 2. Verify phase with high-precision
        accepted = self.verify_forward(tokens, draft_tokens)
        
        # 3. KV cache shared between phases
        return accepted
```

**SDK Components**:
1. Multi-precision weight management
2. Quantization scheme switching
3. Shared KV cache handling
4. Accept/reject sampling logic

#### Medusa Implementation Requirements:

```python
class MedusaModel:
    def __init__(self, backbone, num_heads=4):
        self.backbone = backbone  # Frozen
        self.medusa_heads = [Linear(head_dim, vocab_size) 
                            for _ in range(num_heads)]
    
    def forward(self, tokens):
        hidden = self.backbone(tokens)
        # Parallel predictions at different positions
        predictions = [head(hidden) for head in self.medusa_heads]
        return self.tree_attention(predictions)
```

**SDK Components**:
1. Multiple decoding heads
2. Tree-based attention mechanism
3. Typical acceptance scheme
4. Fine-tuning pipeline

### 4.2 Hardware RTL Implementation

#### QSPEC Hardware Requirements:

| Component | Description | Complexity |
|-----------|-------------|------------|
| Dual Quantization Units | INT4 and INT8 compute paths | High |
| Weight Memory Controller | Manage 2 weight formats | Medium |
| Shared KV Cache | Single cache interface | Low |
| Quantization Switcher | Fast format switching | Medium |

**RTL Challenges**:
- Need separate INT4 and INT8 MAC units
- Memory bandwidth for loading different weight formats
- Synchronization between draft and verify phases

#### Medusa/EAGLE Hardware Requirements:

| Component | Description | Complexity |
|-----------|-------------|------------|
| Extra Head Compute | Small linear layers | Low |
| Tree Attention | Parallel attention computation | Medium |
| Feature Buffer | Store intermediate features | Low |

**RTL Advantages**:
- Simpler compute path (single precision)
- Better memory utilization
- More regular memory access patterns

### 4.3 Development Effort Estimation

| Approach | SDK Effort | RTL Effort | Testing Effort | Total (Person-Months) |
|----------|------------|------------|----------------|----------------------|
| **QSPEC** | 2-3 months | 3-4 months | 2 months | 7-9 months |
| **Medusa** | 1-2 months | 2-3 months | 1 month | 4-6 months |
| **EAGLE** | 1-2 months | 2-3 months | 1 month | 4-6 months |
| **N-gram** | 0.5 months | 0.5 months | 0.5 months | 1.5 months |
| **Self-Speculation** | 1 month | 1-2 months | 1 month | 3-4 months |

---

## 5. Recommendations for Edge Deployment

### 5.1 Priority Ranking for Edge

1. **Self-Speculation / Layer Skip** (Best)
   - Zero memory overhead
   - No training required
   - 1.3-1.7x speedup sufficient for edge
   - Example: CLaSp (arXiv:2505.24196)

2. **N-gram Lookahead** (Good)
   - Zero overhead
   - Simple implementation
   - Combine with other methods

3. **EAGLE** (Good if training feasible)
   - Minimal overhead (~5-10%)
   - Best speedup-to-overhead ratio
   - Requires feature extraction support

4. **Medusa** (Moderate)
   - Higher overhead but no separate model
   - Requires fine-tuning

5. **QSPEC** (Not Recommended for Edge)
   - Memory overhead too high
   - Batch-dependent performance
   - Better suited for server deployment

### 5.2 Hybrid Approach Recommendation

For edge deployment, consider combining approaches:

```
Self-Speculation (Layer Skip) + N-gram Lookahead
├── Use layer skipping for drafting
├── Use n-gram patterns for additional predictions
├── Single model, no training required
└── Expected speedup: 1.5-2x with minimal overhead
```

---

## 6. Paper Citations

### Primary Papers

1. **QSPEC**: Zhao et al. "QSpec: Speculative Decoding with Complementary Quantization Schemes" EMNLP 2025. arXiv:2410.11305

2. **Medusa**: Cai et al. "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads" ICML 2024. arXiv:2401.10774

3. **EAGLE**: Li et al. "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty" arXiv:2401.15077

4. **Original Speculative Decoding**: Leviathan et al. "Fast Inference from Transformers via Speculative Decoding" ICML 2023

### Related Papers

5. **VocabTrim**: Goel et al. "VOCABTRIM: Vocabulary Pruning for Efficient Speculative Decoding in LLMs" ICML 2025 Workshop

6. **CLaSp**: Chen et al. "CLaSp: In-Context Layer Skip for Self-Speculative Decoding" ACL 2025

7. **Quasar**: Huang & Wen. "Quasar: Quantized Self-Speculative Acceleration for Rapid Inference" arXiv:2603.01399

8. **Mirror-SD**: Bhendawade et al. "Mirror Speculative Decoding: Breaking the Serial Barrier in LLM Inference" arXiv:2510.13161

---

## 7. Conclusion

QSPEC presents an innovative approach to speculative decoding by leveraging complementary quantization schemes. However, for **edge deployment**, its memory overhead (1.5-2x weight storage) and batch-dependent performance make it **suboptimal**.

For edge scenarios with single-user inference (batch=1), **self-speculation methods** (layer skipping) combined with **n-gram lookahead** offer the best trade-off between speedup (1.5-2x) and memory overhead (near-zero).

If higher speedup is required and training is feasible, **EAGLE** provides the best speedup-to-overhead ratio with minimal memory overhead (~5-10%).

---

*Report Generated: Research Analysis on Speculative Decoding for Edge Deployment*
