# TernaryAir: Open Source Mask-Locked Inference Chip

**$99 Retail | 100+ tok/s | 3-5W USB Power | MIT License**

By Casey DiGennaro | Commercial Fisherman | Edge Hardware Designer

GitHub: [github.com/superinstance/ternaryair](https://github.com/superinstance/ternaryair)

---

## Why This Exists

I commercial fish for a living. Out on the water, miles from cell towers and WiFi, I need intelligence that works without the internet. This isn't a hypothetical use case dreamed up in a Silicon Valley boardroom. This is my life. The frustration of needing AI assistance in places where cloud connectivity is impossible led to TernaryAir.

The foundational toolkits to make affordable, open-source inference chips must never be closed off to anyone wanting to further the science and design. Open source creates the fastest path from concept to silicon.

---

## What's In This Package

### Documentation (`/docs`)

| Document | Description |
|----------|-------------|
| `TernaryAir_Manifesto.docx` | Foundational philosophy, origin story, vision for offline AI |
| `TernaryAir_Technical_Architecture.docx` | Complete RTL implementation guide, specifications, manufacturing |

### RTL Source (`/rtl`)

| Module | Description |
|--------|-------------|
| `rau.sv` | Rotation-Accumulate Unit (core compute element) |
| `synaptic_array.sv` | Parallel RAU array for matrix operations |
| `weight_rom.sv` | Storage for non-ternary parameters |
| `kv_cache.sv` | KV cache controller for attention |
| `top_level.sv` | Complete inference engine integration |

---

## Key Specifications

| Parameter | Value |
|-----------|-------|
| **Retail Price** | $99 (Maker Edition $79) |
| **Inference Speed** | 100+ tokens/second |
| **Power Consumption** | 3-5W USB power |
| **Process Node** | 28nm (mature, affordable) |
| **License** | MIT (fully open source) |
| **Model Support** | BitNet b1.58-2B-4T, iFairy variants |

---

## The Core Innovation

Traditional AI chips are computers that run AI software. TernaryAir is AI embodied in silicon. The weights aren't loaded from memory—they're hardwired into the metal interconnect layers.

The **Rotation-Accumulate Unit (RAU)** is our core innovation:

- **Traditional MAC**: ~150 gates for INT8 multiplication
- **TernaryAir RAU**: ~15 gates for ternary rotation

By encoding weights as {-1, 0, +1}, multiplication reduces to:
- +1: identity (pass through)
- 0: zero (return zero)
- -1: negate (rotation)

This enables **90% gate reduction** while maintaining inference accuracy through proven ternary quantization techniques.

---

## Building Your Own

### FPGA Prototype (Gate 0)

Target platform: AMD Kria KV260 (XCK26)

```bash
# Clone repository
git clone https://github.com/superinstance/ternaryair

# Run simulation
cd ternaryair/rtl
make sim

# Synthesize for KV260
make fpga
```

### ASIC Tapeout

1. **RTL Freeze**: Complete verification, formal checks
2. **Synthesis**: Target 28nm PDK (TSMC, GlobalFoundries, Samsung)
3. **Place & Route**: Weight routing becomes metal pattern
4. **MPW Shuttle**: Prototype via MOSIS/Europractice (~$50K)
5. **Volume Production**: Dedicated mask set ($2-3M)

---

## Cost Structure

| Component | NRE Cost | Per-Unit @ 10K |
|-----------|----------|----------------|
| Mask Set (28nm) | $2-3M | - |
| Design & Verification | $2-4M | - |
| Die (25mm²) | - | $5-8 |
| Packaging & Test | - | $3-5 |
| Memory (LPDDR4) | - | $10-12 |
| **Total COGS** | **$4-7M** | **$20-30** |

At $99 retail with ~$25 COGS: **~60% gross margin**

---

## Software SDK

```python
import ternaryair

# Initialize device
device = ternaryair.connect()

# Synchronous inference
response = device.infer("Your prompt here")

# Streaming inference
for token in device.infer_stream("Your prompt here"):
    print(token, end='', flush=True)
```

Zero configuration. No model loading. No CUDA. Just inference.

---

## Second Generation: LOG Architecture

The next generation uses **Logic-Orientation-Geometry**:

- **Origin (all zeros)** = simulated state
- **Input congruence** = what matches the expected pattern
- **Attention output** = vector of differences
- **Coordinate system** = geometric base-12

This inverts the traditional model-prompt-stabilization architecture into code-first inference with induction parallel to CPU deduction.

---

## How to Contribute

1. **Hardware Engineers**: RTL improvements, verification, FPGA prototypes
2. **ML Researchers**: Better ternary training, architecture optimizations
3. **Edge Developers**: Applications, SDK extensions
4. **Manufacturers**: Tapeout partnerships, volume production

---

## License

MIT License - use, modify, distribute, sell. No restrictions.

The goal isn't to capture value—it's to accelerate development of affordable inference hardware for the edge cases the industry ignores.

---

## Contact

**Casey DiGennaro**

- GitHub: [github.com/superinstance](https://github.com/superinstance)
- Related Project: [github.com/superinstance/POLLN](https://github.com/superinstance/POLLN)

---

*Intelligence without internet isn't a luxury. It's infrastructure.*
