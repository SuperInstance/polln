# Model Conversion Guide

This guide explains how to convert models for use with TernaryAir.

## Overview

TernaryAir uses ternary quantized weights {-1, 0, +1}, which provides:
- 8× compression vs FP16
- 90% reduction in compute (no multiplication)
- Hardware-friendly representation

## Supported Architectures

| Architecture | Support | Notes |
|--------------|---------|-------|
| BitNet b1.58 | ✅ Native | Primary target |
| LLaMA (converted) | ✅ Supported | Requires conversion |
| GPT-2 (converted) | ✅ Supported | Requires conversion |
| BERT (converted) | ⚠️ Experimental | May need fine-tuning |

## Quick Start

### Convert PyTorch Model

```python
from ternaryair.models.converter import convert_pytorch_model, ConversionConfig

# Load your model
model = MyModel.load("model.pt")

# Configure conversion
config = ConversionConfig(
    threshold=0.05,     # Values below this become 0
    per_channel=True,   # Scale per output channel
)

# Convert to ternary
result = convert_pytorch_model(model, config)

print(f"Sparsity: {result.sparsity:.1%}")
print(f"Compression: {result.compression_ratio:.1f}x")
```

### Export for Hardware

```python
from ternaryair.models.converter import export_for_hardware

# Export converted weights
export_for_hardware(result, "model_weights.bin")
```

## Conversion Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FP16 → TERNARY CONVERSION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Step 1: Compute Scale Factor                                         │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   scale = mean(|W|) for each output channel                           │
│                                                                         │
│   Step 2: Normalize Weights                                            │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   W_normalized = W / scale                                             │
│                                                                         │
│   Step 3: Quantize to Ternary                                          │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│           ⎧  +1,  if W_normalized > +threshold                        │
│   W_ternary = ⎨   0,  if |W_normalized| ≤ threshold                   │
│           ⎩  -1,  if W_normalized < -threshold                        │
│                                                                         │
│   Step 4: Pack and Export                                              │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                         │
│   Pack 4 ternary values per byte (2 bits each)                        │
│   Store scale factors separately                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quality Evaluation

```python
from ternaryair.models.converter import evaluate_quality

# Evaluate quantization quality
quality = evaluate_quality(
    original_weights,
    result.ternary_weights,
    result.scales
)

print(f"MSE: {quality['global_mse']:.6f}")

for layer, metrics in quality['layers'].items():
    print(f"{layer}: MSE={metrics['mse']:.6f}")
```

## Fine-Tuning for Ternary

For best results, fine-tune the model after conversion:

```python
from ternaryair.models.training import TernaryTrainer

trainer = TernaryTrainer(
    model=model,
    learning_rate=1e-5,
    quantization_aware=True
)

# Fine-tune with ternary quantization
trainer.train(
    train_data=train_dataset,
    epochs=10,
    eval_data=eval_dataset
)
```

## Pre-trained Models

Download pre-converted models:

| Model | Parameters | Download |
|-------|------------|----------|
| TernaryAir-125M | 125M | `models download ternaryair-125m` |
| TernaryAir-350M | 350M | `models download ternaryair-350m` |

## Troubleshooting

### High Quality Loss

- Reduce threshold (more non-zero weights)
- Enable per-channel scaling
- Fine-tune after conversion

### Low Sparsity

- Increase threshold (more zeros)
- Check weight distribution
- Consider training with ternary constraints

### Export Errors

- Verify all layers are convertible
- Check for unsupported operations
- Ensure scale factors are finite
