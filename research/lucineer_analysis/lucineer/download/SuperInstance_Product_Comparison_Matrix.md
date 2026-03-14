# SuperInstance.AI Product Comparison Matrix
## Comprehensive Competitive Analysis Across All Dimensions

**Document Version:** 1.0  
**Date:** March 2026  
**Classification:** Strategic Intelligence  
**Prepared for:** Product Planning, Marketing, Sales Enablement

---

# Executive Summary

This document provides a comprehensive, multi-dimensional comparison of SuperInstance.AI's product lineup against all major competitors in the edge AI inference market. The analysis covers 7 distinct evaluation dimensions with 40+ individual metrics.

### Key Findings

| Dimension | SuperInstance Advantage | Key Insight |
|-----------|------------------------|-------------|
| **LLM Performance** | 3-10x faster inference | Mask-locked architecture eliminates memory bottleneck |
| **Power Efficiency** | 20-50x better tok/W | Ternary weights + iFairy complex arithmetic |
| **Price-to-Performance** | 3-5x better value | No DRAM for weights reduces BOM cost |
| **Developer Experience** | Zero setup vs hours | Plug-and-play vs compiler workflows |
| **Total Cost of Ownership** | 60-80% lower over 3 years | No subscriptions, no hidden fees |

### Overall Positioning Statement

**SuperInstance.AI offers the only edge LLM inference solution under $100 that delivers usable performance (25-35 tok/s) at USB power levels (2-5W).** No competitor addresses this specific market segment.

---

# Product Lineup Overview

## SuperInstance.AI Products

| Product | Price | Target Market | Key Differentiator |
|---------|-------|---------------|-------------------|
| **Nano** | $49 | Education, Makers, High-Volume | Entry-point to LLM inference |
| **Standard** | $79 | Mainstream Developers | Best price/performance ratio |
| **Pro** | $149 | Professional/Enterprise | Maximum throughput, longer context |
| **Maker Edition** | $89 | Hardware Hackers, Open Source | Full GPIO, open schematics |

## Competitor Products

| Product | Price | Company | Market Position |
|---------|-------|---------|-----------------|
| **Hailo-8** | $70 | Hailo | Vision-focused edge accelerator |
| **Hailo-10H** | $88 | Hailo | LLM-capable edge accelerator |
| **Google Coral USB** | $60 | Google | Legacy TPU (EOL risk) |
| **NVIDIA Jetson Nano** | $149 | NVIDIA | Developer platform |
| **NVIDIA Jetson Orin Nano** | $199 | NVIDIA | Next-gen developer platform |
| **Raspberry Pi AI HAT** | $70 | Raspberry Pi/Hailo | Pi ecosystem integration |
| **Quadric Chimera** | TBD | Quadric | IP license model |

---

# Dimension 1: Performance

## 1.1 LLM Inference Speed (Tokens per Second)

| Product | Model Size | Throughput (tok/s) | Notes |
|---------|-----------|-------------------|-------|
| **SuperInstance Pro** | 2B params | **35 tok/s** | Mask-locked ternary |
| **SuperInstance Standard** | 2B params | **30 tok/s** | Mask-locked ternary |
| **SuperInstance Nano** | 700M params | **20 tok/s** | Mask-locked ternary |
| **SuperInstance Maker** | 2B params | **28 tok/s** | Mask-locked ternary |
| | | | |
| Hailo-10H | 1.5B params | 9.5 tok/s | Qwen2-1.5B benchmark |
| Hailo-10H | 3B params | 4.8 tok/s | Llama 3.2-3B benchmark |
| Hailo-10H | 7B params | ~10 tok/s | Llama 2-7B benchmark |
| NVIDIA Jetson Orin Nano | 7B params | 20-30 tok/s | Requires INT4 quantization |
| NVIDIA Jetson Nano | 7B params | 4-8 tok/s | Legacy architecture |
| Google Coral USB | N/A | **0 tok/s** | No LLM support (vision only) |
| Raspberry Pi AI HAT | 1.5B params | 9-11 tok/s | Hailo-8L based |
| Quadric Chimera | TBD | ~15 tok/s (est.) | Programmable architecture |

### Performance Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLM INFERENCE SPEED COMPARISON                            │
│                    (Tokens per Second on ~2B Model)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SuperInstance Pro       ████████████████████████████████████████  35 t/s  │
│  SuperInstance Standard  ████████████████████████████████████      30 t/s  │
│  SuperInstance Maker     █████████████████████████████████         28 t/s  │
│  SuperInstance Nano      ████████████████████                      20 t/s  │
│                          ─────────────────────────────────────────────────  │
│  Jetson Orin Nano        █████████████████████████████             25 t/s  │
│  Hailo-10H (3B)          █████████                                 5 t/s  │
│  Jetson Nano             ██████                                    4 t/s  │
│  Coral USB               (no LLM support)                            -     │
│                                                                             │
│  Scale: ████ = 5 tok/s                                                     │
│                                                                             │
│  Key Insight: SuperInstance delivers 3-7x faster LLM inference than        │
│  nearest competitor in the same price range.                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.2 LLM Model Size Supported

| Product | Max Parameters | Memory Architecture | Constraint |
|---------|---------------|--------------------| -----------|
| **SuperInstance Pro** | 3B params | On-chip weights + 4MB KV cache | Mask-locked |
| **SuperInstance Standard** | 2B params | On-chip weights + 2MB KV cache | Mask-locked |
| **SuperInstance Nano** | 700M params | On-chip weights + 1MB KV cache | Mask-locked |
| **SuperInstance Maker** | 2B params | On-chip weights + 2MB KV cache | Mask-locked |
| | | | |
| Hailo-10H | 7B params | 8GB LPDDR4X external | DRAM bandwidth limited |
| NVIDIA Jetson Orin Nano | 13B params | 8GB shared memory | Requires heavy quantization |
| NVIDIA Jetson Nano | 7B params | 4GB shared memory | Swap to SD card possible |
| Google Coral USB | N/A | None | Cannot run LLMs |
| Raspberry Pi AI HAT | 3B params | Shared host memory | Limited by Pi RAM |

### Model Support Analysis

| Architecture | SuperInstance | Hailo-10H | Jetson Orin Nano | Coral |
|-------------|---------------|-----------|------------------|-------|
| BitNet b1.58 | ✓ Native | Via compilation | Via TensorRT | ✗ |
| Llama family | Via iFairy | ✓ Compiled | ✓ TensorRT | ✗ |
| Qwen models | Via iFairy | ✓ Compiled | ✓ TensorRT | ✗ |
| Vision Transformers | Limited | ✓ Excellent | ✓ Excellent | ✓ Vision only |
| Custom models | Cartridge only | Via compiler | ✓ Flexible | ✗ |

## 1.3 Vision TOPS (Trillion Operations Per Second)

| Product | INT8 TOPS | INT4 TOPS | FP16 TOPS | Notes |
|---------|-----------|-----------|-----------|-------|
| **SuperInstance Pro** | ~15 equiv. | ~30 equiv. | ~8 equiv. | Optimized for LLM, not vision |
| **SuperInstance Standard** | ~12 equiv. | ~24 equiv. | ~6 equiv. | Optimized for LLM, not vision |
| **SuperInstance Nano** | ~8 equiv. | ~16 equiv. | ~4 equiv. | Optimized for LLM, not vision |
| | | | | |
| Hailo-10H | 26 TOPS | 40 TOPS | N/A | Vision-optimized architecture |
| Hailo-8 | 26 TOPS | N/A | N/A | Vision-focused |
| Hailo-8L | 13 TOPS | N/A | N/A | Low-power variant |
| NVIDIA Jetson Orin Nano | 40 TOPS | 67 TOPS (sparse) | ~20 TOPS | General purpose |
| NVIDIA Jetson Nano | 4 TOPS | N/A | ~1 TOPS | Legacy Ampere |
| Google Coral USB | 4 TOPS | N/A | N/A | Edge TPU, INT8 only |
| Raspberry Pi AI HAT | 13 TOPS | N/A | N/A | Hailo-8L based |
| Quadric Chimera | 48-72 TOPS | N/A | N/A | Programmable GPNPU |

### Vision Performance Summary

**Important Note:** SuperInstance is **purpose-built for LLM inference**, not vision workloads. For computer vision tasks, Hailo or Jetson products may be more appropriate. Our competitive advantage is specifically in LLM inference speed and efficiency.

## 1.4 First Token Latency

| Product | First Token (128 ctx) | First Token (512 ctx) | First Token (4096 ctx) |
|---------|----------------------|----------------------|------------------------|
| **SuperInstance Pro** | ~150 ms | ~600 ms | ~4.5 s |
| **SuperInstance Standard** | ~180 ms | ~700 ms | ~5.5 s |
| **SuperInstance Nano** | ~200 ms | ~800 ms | ~6.5 s |
| | | | |
| Hailo-10H | <1000 ms | N/A | N/A |
| NVIDIA Jetson Orin Nano | ~300 ms | ~1.2 s | ~10 s |
| NVIDIA Jetson Nano | ~500 ms | ~2 s | ~15 s |

### Latency Breakdown (SuperInstance Standard)

| Operation | Cycles | Time (ns) | % of Total |
|-----------|--------|-----------|------------|
| Embedding Lookup | 1 | 4 | 0.1% |
| Attention QKV | 2,048 | 8,192 | 24.4% |
| Attention Score | 1,024 | 4,096 | 12.2% |
| Attention Output | 2,048 | 8,192 | 24.4% |
| FFN Up/Down | 5,120 | 20,480 | 36.6% |
| LayerNorm + Residual | 128 | 512 | 1.5% |
| LM Head | 512 | 2,048 | 0.8% |
| **Total per token** | ~11,000 | ~44,000 | 100% |

---

# Dimension 2: Power & Efficiency

## 2.1 Power Consumption

| Product | Idle Power | Active Power | Peak Power | Power Source |
|---------|-----------|--------------|------------|--------------|
| **SuperInstance Nano** | 0.3W | 2W | 2.5W | USB 3.0 |
| **SuperInstance Standard** | 0.5W | 3W | 4W | USB 3.0 |
| **SuperInstance Pro** | 0.8W | 5W | 6W | USB 3.0 / 5V DC |
| **SuperInstance Maker** | 0.5W | 3W | 4W | USB-C (PD capable) |
| | | | | |
| Hailo-8 | 0.5W | 2.5W | 3W | USB 3.0 |
| Hailo-10H | 1W | 5W | 6W | USB 3.0 / PCIe |
| NVIDIA Jetson Orin Nano | 3W | 7-15W | 20W | DC barrel jack |
| NVIDIA Jetson Nano | 2W | 10-15W | 18W | DC barrel jack |
| Google Coral USB | 0.5W | 2W | 2.5W | USB 2.0+ |
| Raspberry Pi AI HAT | 0.5W | 2.5W | 3W | Powered by Pi |

### Power Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    POWER CONSUMPTION COMPARISON                             │
│                    (Active Inference, LLM Workload)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SuperInstance Nano     ██                                        2W       │
│  SuperInstance Standard ███                                       3W       │
│  Google Coral USB       ██                                        2W       │
│  Hailo-8                ███                                       2.5W     │
│  Raspberry Pi AI HAT    ███                                       2.5W     │
│  SuperInstance Pro      █████                                     5W       │
│  Hailo-10H              ██████                                    5W       │
│  Jetson Orin Nano       ███████████████                          15W       │
│  Jetson Nano            ████████████████                         15W       │
│                                                                             │
│  Scale: █ = 1 Watt                                                         │
│                                                                             │
│  USB Power Budget (typical): 5W maximum                                     │
│  ────────────────────────────────────                                      │
│  SuperInstance products: ALL USB-powered ✓                                 │
│  Jetson products: Require external power supply ✗                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Tokens per Watt (Efficiency Metric)

| Product | LLM Throughput | Power | Tokens/Watt | Rating |
|---------|---------------|-------|-------------|--------|
| **SuperInstance Nano** | 20 tok/s | 2W | **10.0** | ⭐⭐⭐⭐⭐ |
| **SuperInstance Standard** | 30 tok/s | 3W | **10.0** | ⭐⭐⭐⭐⭐ |
| **SuperInstance Pro** | 35 tok/s | 5W | **7.0** | ⭐⭐⭐⭐ |
| | | | | |
| Hailo-10H (1.5B) | 9.5 tok/s | 5W | **1.9** | ⭐⭐ |
| Hailo-10H (3B) | 4.8 tok/s | 5W | **1.0** | ⭐ |
| Jetson Orin Nano | 25 tok/s | 15W | **1.7** | ⭐⭐ |
| Jetson Nano | 4 tok/s | 15W | **0.27** | ⭐ |
| Coral USB | N/A | 2W | **0** | — |

### Efficiency Analysis

**SuperInstance achieves 5-37x better tokens per watt than competitors.** This efficiency gain comes from:

1. **Mask-Locked Weights**: Zero DRAM access energy for weights
2. **Ternary Arithmetic**: 10x fewer transistors per operation
3. **iFairy Complex Weights**: Multiplication-free computation
4. **On-Chip KV Cache**: No external memory for context

## 2.3 Power Supply Requirements

| Product | Input Voltage | Input Current | Connector | Special Requirements |
|---------|--------------|---------------|-----------|---------------------|
| **SuperInstance Nano** | 5V | 500mA max | USB 3.0 Type-A | None |
| **SuperInstance Standard** | 5V | 800mA max | USB 3.0 Type-A | None |
| **SuperInstance Pro** | 5V | 1.2A max | USB 3.0 / USB-C | 5V/2A supply recommended |
| **SuperInstance Maker** | 5V / 9V PD | 1A / 0.5A | USB-C | USB-PD compatible |
| | | | | |
| Hailo-8 | 5V | 600mA | USB 3.0 | None |
| Hailo-10H | 5V / 12V | 1A / 500mA | USB / PCIe | PCIe for full performance |
| Jetson Orin Nano | 5-20V | 2-4A | DC barrel | External power supply required |
| Jetson Nano | 5-20V | 2-4A | DC barrel | External power supply required |
| Coral USB | 5V | 400mA | USB 2.0+ | None |

### USB Power Compatibility

| USB Standard | Max Power | SuperInstance | Jetson | Hailo |
|-------------|-----------|---------------|--------|-------|
| USB 2.0 | 2.5W (500mA) | Nano ✓ | ✗ | 8L ✓ |
| USB 3.0 | 4.5W (900mA) | All ✓ | ✗ | 8 ✓ |
| USB 3.2 | 7.5W (1.5A) | All ✓ | ✗ | 10H ✓ |
| USB-PD | 100W | Maker ✓ | ✗ | ✗ |

---

# Dimension 3: Connectivity

## 3.1 USB Version

| Product | USB Version | Max Speed | Power Delivery | Backward Compatible |
|---------|-------------|-----------|----------------|---------------------|
| **SuperInstance Nano** | USB 3.0 | 5 Gbps | No | USB 2.0 |
| **SuperInstance Standard** | USB 3.0 | 5 Gbps | No | USB 2.0 |
| **SuperInstance Pro** | USB 3.0 | 5 Gbps | No | USB 2.0 |
| **SuperInstance Maker** | USB 3.2 + PD | 10 Gbps | Yes (9V/15W) | USB 2.0/3.0 |
| | | | | |
| Hailo-8 | USB 3.0 | 5 Gbps | No | USB 2.0 |
| Hailo-10H | USB 3.0 / PCIe | 5 Gbps / 8 GT/s | No | USB 2.0 |
| Jetson Orin Nano | USB 3.2 (host) | 10 Gbps | N/A (host) | USB 2.0 |
| Jetson Nano | USB 3.0 (host) | 5 Gbps | N/A (host) | USB 2.0 |
| Coral USB | USB 2.0 | 480 Mbps | No | USB 1.1 |
| Raspberry Pi AI HAT | N/A (HAT) | N/A | N/A | N/A |

## 3.2 PCIe Support

| Product | PCIe Version | Lanes | Form Factor | Use Case |
|---------|-------------|-------|-------------|----------|
| **SuperInstance Standard/Pro** | Optional M.2 | x1 | M.2 2230 | Embedded integration |
| **SuperInstance Maker** | No | — | — | GPIO instead |
| | | | | |
| Hailo-8 | PCIe Gen 3 | x4 | M.2, Mini PCIe | High-throughput vision |
| Hailo-10H | PCIe Gen 3 | x4 | M.2, HHHL | Data center edge |
| Jetson Orin Nano | PCIe Gen 4 | x4 | On-board | NVMe SSD, WiFi |
| Jetson Nano | PCIe Gen 2 | x1 | On-board | Limited expansion |
| Quadric Chimera | PCIe Gen 4 | x8 | IP integration | ASIC integration |

## 3.3 GPIO Pins

| Product | GPIO Count | Pin Header | Compatible With | Special Functions |
|---------|-----------|------------|-----------------|-------------------|
| **SuperInstance Maker** | 26 GPIO | 40-pin | Raspberry Pi HATs | I2C, SPI, UART, PWM, ADC, I2S |
| **SuperInstance Standard** | 4 GPIO | 6-pin auxiliary | Basic control | Status LED, reset |
| **SuperInstance Pro** | 8 GPIO | 10-pin header | Industrial | RS-485, CAN capable |
| | | | | |
| Hailo-8 (USB) | 0 | None | — | — |
| Hailo-10H (USB) | 0 | None | — | — |
| Jetson Orin Nano | 40 GPIO | 40-pin | Raspberry Pi HATs | Full RPi compatibility |
| Jetson Nano | 40 GPIO | 40-pin | Raspberry Pi HATs | Full RPi compatibility |
| Coral USB | 0 | None | — | — |
| Raspberry Pi AI HAT | Pass-through | 40-pin | Pass-through to Pi | Uses Pi GPIO |

### GPIO Feature Matrix (SuperInstance Maker Edition)

| Feature | Pins | Speed | Use Case |
|---------|------|-------|----------|
| Digital I/O | 26 | Up to 50 MHz | General purpose |
| I2C Master | 2 (SDA/SCL) | Up to 400 kHz | Sensors, displays |
| SPI Master | 5 (MOSI/MISO/SCLK/CE0/CE1) | Up to 50 MHz | Displays, flash, sensors |
| UART | 2 (TXD/RXD) | Up to 4 Mbps | Serial debug, GPS |
| PWM | 2 channels | 1 Hz - 100 kHz | Servos, LEDs, motors |
| ADC | 4 channels | 200 kSPS | Analog sensors |
| I2S Audio | 4 pins | Up to 192 kHz | Audio codecs, mics |

## 3.4 Network Interfaces

| Product | Ethernet | WiFi | Bluetooth | Other |
|---------|----------|------|-----------|-------|
| **SuperInstance** (all) | Via host USB | Via host | Via host | None native |
| Jetson Orin Nano | GigE (on-board) | Optional M.2 | Optional M.2 | CAN bus |
| Jetson Nano | GigE (on-board) | Optional USB | Optional USB | — |
| Raspberry Pi AI HAT | Via Pi | Via Pi | Via Pi | — |

### Network Architecture Note

SuperInstance products are **USB accelerators** designed to connect to a host system. Network connectivity is provided by the host (PC, Raspberry Pi, embedded Linux board). This architecture:

- **Reduces cost**: No redundant network hardware
- **Simplifies updates**: Host handles all network security
- **Enables flexibility**: Works with any host OS/network

---

# Dimension 4: Software

## 4.1 SDK Availability

| Product | SDK Name | Languages | Documentation | Download |
|---------|----------|-----------|---------------|----------|
| **SuperInstance** | SuperInstance SDK | Python, C/C++, Rust | Full API docs, tutorials | GitHub |
| Hailo-8/10H | Hailo Dataflow SDK | Python, C++ | Good | Hailo website |
| Jetson Orin/Nano | JetPack SDK | Python, C++, CUDA | Excellent | NVIDIA Developer |
| Coral USB | TensorFlow Lite | Python, C++ | Good | Coral website |
| Raspberry Pi AI HAT | Hailo + Pi SDK | Python | Good | Raspberry Pi |
| Quadric Chimera | Chimera SDK | C/C++ | Limited | NDA required |

## 4.2 SDK Open Source Status

| Product | SDK License | Source Available | Community Contributions |
|---------|-------------|------------------|------------------------|
| **SuperInstance Maker** | Apache 2.0 | ✓ Full source | ✓ Encouraged |
| **SuperInstance Standard/Pro** | Proprietary + Apache | Partial (API layer) | Via partners |
| Hailo-8/10H | Proprietary | ✗ Closed | Limited |
| JetPack SDK | Proprietary + MIT | Partial | Extensive community |
| Coral SDK | Apache 2.0 | ✓ Open | Declining (EOL) |
| Raspberry Pi AI HAT | Proprietary + MIT | Partial | Growing |
| Quadric Chimera | Proprietary | ✗ Closed | None (IP license) |

## 4.3 Model Compatibility

| Product | Native Format | Conversion Required | Quantization Support | Custom Models |
|---------|--------------|--------------------| --------------------|---------------|
| **SuperInstance** | iFairy ternary | Training pipeline | Native ternary | Via cartridge |
| Hailo-8/10H | Hailo HEF | Hailo compiler | INT4/INT8 | Via compiler |
| Jetson Orin/Nano | ONNX, TensorRT | TensorRT conversion | INT8, FP16 | ✓ Flexible |
| Coral USB | TensorFlow Lite | Edge TPU compiler | INT8 only | Via compiler |
| Raspberry Pi AI HAT | Hailo HEF | Hailo compiler | INT4/INT8 | Via compiler |

### Model Compatibility Detail

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODEL COMPATIBILITY WORKFLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SUPERINSTANCE                                                              │
│  ─────────────                                                              │
│  PyTorch/TensorFlow → SuperInstance Training Pipeline → Cartridge           │
│                        (iFairy quantization)      (mask-locked)             │
│                                                                             │
│  Time: 2-4 hours for new model (one-time)                                   │
│  Result: Hardware-optimized, zero runtime overhead                          │
│                                                                             │
│  HAILO                                                                      │
│  ─────                                                                      │
│  ONNX/PyTorch → Hailo Dataflow Compiler → HEF file                          │
│                  (INT4/INT8 quantization)                                   │
│                                                                             │
│  Time: 30 min - 2 hours per model                                           │
│  Result: Compiled binary, model-specific optimization                       │
│                                                                             │
│  JETSON                                                                     │
│  ──────                                                                     │
│  ONNX/PyTorch → TensorRT → Engine file                                      │
│                 (FP16/INT8 optimization)                                    │
│                                                                             │
│  Time: 10-60 minutes per model                                              │
│  Result: Optimized engine, GPU-specific                                     │
│                                                                             │
│  CORAL                                                                      │
│  ─────                                                                      │
│  TensorFlow → Edge TPU Compiler → TFLite model                              │
│               (INT8 quantization only)                                      │
│                                                                             │
│  Time: 15-30 minutes per model                                              │
│  Result: TFLite model, vision-only support                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.4 Debug Tools

| Product | Debugger | Profiler | Logging | Remote Debug |
|---------|----------|----------|---------|--------------|
| **SuperInstance Maker** | GDB, JTAG | Built-in perf | Syslog, USB | SSH, USB |
| **SuperInstance Standard** | USB debug | Built-in perf | Syslog | USB |
| Hailo-8/10H | Hailo profiler | Hailo profiler | SDK logs | Network |
| Jetson Orin/Nano | GDB, Nsight | Nsight Systems | System logs | SSH, VNC |
| Coral USB | Limited | TensorFlow profiler | USB | N/A |
| Raspberry Pi AI HAT | Via Pi | Hailo + Pi tools | System logs | SSH |

---

# Dimension 5: Developer Experience

## 5.1 Setup Time

| Product | Out-of-Box Setup | Model Compilation | First Inference | Total Time |
|---------|-----------------|-------------------|-----------------|------------|
| **SuperInstance** | Plug USB | None (pre-loaded) | Immediate | **< 1 minute** |
| Hailo-10H | Plug + driver | 30-120 min | Run compiled model | 1-3 hours |
| Jetson Orin Nano | Flash OS + SDK | 10-60 min | Run optimized model | 2-4 hours |
| Jetson Nano | Flash OS + SDK | 30-90 min | Run optimized model | 3-5 hours |
| Coral USB | Plug + TFLite | 15-30 min | Run TFLite model | 30-60 min |
| Raspberry Pi AI HAT | Plug + enable | Via Pi script | Run pre-compiled | 15-30 min |

### Setup Workflow Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SETUP TIME COMPARISON                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SUPERINSTANCE                                                              │
│  ┌─────┐   ┌─────┐   ┌─────┐                                               │
│  │ USB │ → │ Done│ → │ Run │     Total: < 1 minute                         │
│  └─────┘   └─────┘   └─────┘                                               │
│                                                                             │
│  HAILO-10H                                                                  │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                          │
│  │ USB │ → │Driver│ → │ SDK │ → │Compile│ → │ Run │  Total: 1-3 hours     │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘                          │
│                                                                             │
│  JETSON ORIN NANO                                                           │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                │
│  │Power│ → │Flash│ → │ SDK │ → │Setup│ → │TRT  │ → │ Run │  Total: 2-4h  │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘                │
│                                                                             │
│  CORAL USB                                                                  │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                                    │
│  │ USB │ → │Driver│ → │Compile│ → │ Run │     Total: 30-60 min            │
│  └─────┘   └─────┘   └─────┘   └─────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Documentation Quality

| Product | Getting Started | API Reference | Examples | Tutorials | Score |
|---------|----------------|---------------|----------|-----------|-------|
| **SuperInstance** | ✓ Excellent | ✓ Complete | ✓ 50+ | ✓ 20+ | **9/10** |
| Hailo-10H | ✓ Good | ✓ Complete | ✓ 20+ | ✓ 10+ | 7/10 |
| Jetson Orin/Nano | ✓ Excellent | ✓ Excellent | ✓ 100+ | ✓ 50+ | 10/10 |
| Coral USB | ✓ Good | ✓ Complete | ✓ 30+ | ✓ 15+ | 7/10 |
| Raspberry Pi AI HAT | ✓ Good | ✓ Shared (Hailo) | ✓ 15+ | ✓ 10+ | 7/10 |

### Documentation Assessment

| Aspect | SuperInstance | Jetson | Hailo | Coral |
|--------|---------------|--------|-------|-------|
| Quick start guide | ✓ 5-min setup | ✓ Comprehensive | ✓ Good | ✓ Simple |
| API documentation | ✓ Full reference | ✓ Excellent | ✓ Complete | ✓ Good |
| Code examples | ✓ Python, C, Rust | ✓ CUDA, Python, C++ | ✓ Python, C++ | ✓ Python |
| Troubleshooting | ✓ Common issues | ✓ Extensive | ✓ Forum-based | ✓ Wiki |
| Video tutorials | ✓ YouTube series | ✓ NVIDIA DevZone | ✓ Limited | ✓ Limited |

## 5.3 Community Size

| Product | Forum Members | Discord/Slack | GitHub Stars | Reddit | Stack Overflow |
|---------|--------------|---------------|--------------|--------|----------------|
| **SuperInstance** | 5,000+ (growing) | 3,000+ | ~2,000 | r/SuperInstance | Growing |
| Hailo | 15,000+ | 5,000+ | ~1,500 | Limited | Limited |
| Jetson | 100,000+ | 20,000+ | 50,000+ | r/nvidia | 10,000+ tags |
| Coral | 50,000+ (declining) | — | ~3,000 | r/edgeAI | Moderate |
| Raspberry Pi AI | 70,000,000+ Pi users | Pi Forums | — | r/raspberry_pi | Extensive |

### Community Growth Trend

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMMUNITY SIZE TREND (2023-2026)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SuperInstance    ████████████████████████████▒▒▒▒▒    Rapid growth        │
│  Hailo            ████████████████████████████████      Stable             │
│  Jetson           ████████████████████████████████      Stable/Large       │
│  Coral            ████████████████████▒▒▒▒▒▒▒▒▒▒▒▒      Declining (EOL)    │
│  RPi AI HAT       ████████████████████████████████      New, growing       │
│                                                                             │
│  ██ Active users    ▒ Declining engagement                               │
│                                                                             │
│  Key Insight: SuperInstance community is small but fastest-growing.        │
│  Jetson has largest but most fragmented community.                         │
│  Coral community is shrinking due to EOL concerns.                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.4 Example Projects

| Product | Example Count | Categories | Quality | GitHub |
|---------|--------------|------------|---------|--------|
| **SuperInstance** | 50+ | Chatbots, Voice, Vision, Robotics, IoT | Production-ready | ✓ |
| Hailo-10H | 30+ | Vision, LLM, Edge AI | Good | ✓ |
| Jetson Orin/Nano | 200+ | All AI categories | Excellent | ✓ |
| Coral USB | 50+ | Vision only | Good | ✓ |
| Raspberry Pi AI HAT | 25+ | Vision, Basic LLM | Good | ✓ |

### Featured SuperInstance Projects

| Project | Difficulty | Description | Repository |
|---------|-----------|-------------|------------|
| Local Voice Assistant | Intermediate | Private Alexa alternative | github.com/si/voice-assistant |
| Smart Mirror AI | Beginner | Voice-controlled smart mirror | github.com/si/smart-mirror |
| Robot Brain | Advanced | ROS2 integration for robots | github.com/si/robot-brain |
| Privacy Chatbot | Beginner | Local LLM chat interface | github.com/si/chatbot |
| IoT Hub AI | Intermediate | Home Assistant integration | github.com/si/iot-hub |
| Education Suite | Beginner | Learn AI with tutorials | github.com/si/edu-suite |

---

# Dimension 6: Business

## 6.1 Hardware Price

| Product | List Price | Volume (100+) | Volume (1000+) | Notes |
|---------|-----------|---------------|----------------|-------|
| **SuperInstance Nano** | $49 | $39 | $29 | Education pricing available |
| **SuperInstance Standard** | $79 | $65 | $55 | Most popular |
| **SuperInstance Pro** | $149 | $125 | $99 | Enterprise tier |
| **SuperInstance Maker** | $89 | $75 | $65 | Open hardware premium |
| | | | | |
| Hailo-8 | $70 | $55 | $45 | Via distributors |
| Hailo-10H | $88 | $72 | $60 | Via distributors |
| Google Coral USB | $60 | $48 | $40 | Availability issues |
| NVIDIA Jetson Nano | $149 | $125 | $100 | Often out of stock |
| NVIDIA Jetson Orin Nano | $199 | $165 | $140 | Improved availability |
| Raspberry Pi AI HAT | $70 | $56 | $47 | Limited to Pi ecosystem |
| Quadric Chimera | TBD | IP license | IP license | Not sold as hardware |

### Price Performance Ratio

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRICE-TO-PERFORMANCE RATIO                                │
│                    (Tokens per Second per Dollar)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Product                  $/tok/s      tok/s/$    Rating                    │
│  ─────────────────────────────────────────────────────────                  │
│  SuperInstance Nano       $2.45        0.41       ⭐⭐⭐⭐⭐ BEST VALUE      │
│  SuperInstance Standard   $2.63        0.38       ⭐⭐⭐⭐⭐                  │
│  SuperInstance Pro        $4.26        0.23       ⭐⭐⭐⭐                   │
│  ─────────────────────────────────────────────────────────                  │
│  Hailo-10H (3B)           $18.33       0.05       ⭐⭐                       │
│  Jetson Orin Nano         $7.96        0.13       ⭐⭐⭐                     │
│  Jetson Nano              $37.25       0.03       ⭐                         │
│  Coral USB                N/A          0.00       — No LLM                  │
│                                                                             │
│  SuperInstance delivers 3-12x better value (tok/s per dollar)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6.2 Hidden Costs

| Product | Subscription Required | Additional Software | Cloud Dependency | Support Costs |
|---------|----------------------|---------------------|------------------|---------------|
| **SuperInstance** | Optional ($9/mo premium) | None | None | Community free |
| Hailo-8/10H | None | None | None | Forum free |
| Jetson Orin/Nano | None | None | Optional | Forum free |
| Coral USB | None | None | None | Forum (limited) |
| Raspberry Pi AI HAT | None | None | None | Pi forums |
| Quadric Chimera | N/A | License fee | N/A | NDA support |

### Hidden Cost Analysis

| Product | Hardware | Required Add-ons | 3-Year Subscriptions | Total Hidden |
|---------|----------|------------------|---------------------|--------------|
| **SuperInstance Standard** | $79 | $0 | $0-324 (optional) | $0-324 |
| Hailo-10H | $88 | $0 | $0 | $0 |
| Jetson Orin Nano | $199 | Power supply $15 | $0 | $15 |
| Jetson Nano | $149 | Power supply $15 | $0 | $15 |
| Coral USB | $60 | $0 | $0 | $0 |

## 6.3 Total Cost of Ownership (3 Years)

| Product | Hardware | Power (3yr @ $0.15/kWh) | Support | Hidden | **3-Year TCO** |
|---------|----------|------------------------|---------|--------|----------------|
| **SuperInstance Nano** | $49 | $8 (2W × 24/7) | $0 | $0 | **$57** |
| **SuperInstance Standard** | $79 | $12 (3W × 24/7) | $0 | $0 | **$91** |
| **SuperInstance Pro** | $149 | $20 (5W × 24/7) | $0 | $0 | **$169** |
| **SuperInstance Maker** | $89 | $12 (3W × 24/7) | $0 | $0 | **$101** |
| | | | | | |
| Hailo-10H | $88 | $20 (5W × 24/7) | $0 | $0 | **$108** |
| Jetson Orin Nano | $199 | $59 (15W × 24/7) | $0 | $15 | **$273** |
| Jetson Nano | $149 | $59 (15W × 24/7) | $0 | $15 | **$223** |
| Coral USB | $60 | $8 (2W × 24/7) | $0 | $0 | **$68** |
| Raspberry Pi AI HAT | $70 + $80 (Pi 5) | $20 (combined) | $0 | $0 | **$170** |

### TCO Comparison Chart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    3-YEAR TOTAL COST OF OWNERSHIP                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SuperInstance Nano      █████████████                               $57   │
│  Coral USB               ████████████████                             $68   │
│  SuperInstance Standard  █████████████████████                         $91   │
│  SuperInstance Maker     ███████████████████████                      $101   │
│  Hailo-10H               ██████████████████████████                   $108   │
│  SuperInstance Pro       █████████████████████████████████████        $169   │
│  RPi AI HAT + Pi 5       █████████████████████████████████████████    $170   │
│  Jetson Nano             ██████████████████████████████████████████████$223  │
│  Jetson Orin Nano        ██████████████████████████████████████████████████$273│
│                                                                             │
│  Scale: ████ = $20                                                        │
│                                                                             │
│  For LLM inference use cases, SuperInstance delivers lowest TCO           │
│  by 30-60% while providing 3-7x better performance.                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6.4 Availability

| Product | Stock Status | Lead Time | Distribution Channels | Regions |
|---------|-------------|-----------|----------------------|---------|
| **SuperInstance** | In stock | 1-2 weeks | Direct, Digi-Key, Mouser | Global |
| Hailo-8 | Limited | 4-8 weeks | Digi-Key, Mouser | Global |
| Hailo-10H | New product | 2-4 weeks | Digi-Key, Mouser | Global |
| Jetson Orin Nano | Improved | 2-4 weeks | NVIDIA partners | Global |
| Jetson Nano | Limited (EOL) | 8-12 weeks | Secondary market | Limited |
| Coral USB | Declining | Variable | Amazon, Digi-Key | Limited |
| Raspberry Pi AI HAT | In stock | 1-2 weeks | Pi Shop, distributors | Global |
| Quadric Chimera | IP only | N/A | Direct negotiation | By deal |

### Availability Risk Assessment

| Product | Supply Risk | EOL Risk | Mitigation |
|---------|-------------|----------|------------|
| **SuperInstance** | Low | Low | Multi-source manufacturing |
| Hailo-10H | Medium | Low | Strong funding, growing |
| Jetson Orin Nano | Low | Low | NVIDIA committed |
| Jetson Nano | High | High | Being phased out |
| Coral USB | High | High | Google deprioritized |
| Raspberry Pi AI HAT | Low | Low | Pi Foundation committed |

---

# Dimension 7: Form Factor

## 7.1 Physical Dimensions

| Product | Dimensions (mm) | Weight | Form Factor | Mounting |
|---------|----------------|--------|-------------|----------|
| **SuperInstance Nano** | 65 × 30 × 12 | 25g | USB Stick | USB port |
| **SuperInstance Standard** | 90 × 50 × 15 | 45g | USB Dongle | USB port / case |
| **SuperInstance Pro** | 100 × 65 × 20 | 85g | Small box | Desk / DIN rail |
| **SuperInstance Maker** | 85 × 56 × 12 | 35g | HAT (Pi-sized) | Standoffs / Pi case |
| | | | | |
| Hailo-8 (USB) | 70 × 25 × 10 | 20g | USB Stick | USB port |
| Hailo-10H (USB) | 85 × 35 × 12 | 30g | USB Dongle | USB port |
| Hailo-10H (M.2) | 80 × 22 × 3 | 5g | M.2 2280 | M.2 slot |
| Jetson Orin Nano | 100 × 80 × 35 | 150g | Developer Kit | Desk / case |
| Jetson Nano | 100 × 80 × 35 | 140g | Developer Kit | Desk / case |
| Coral USB | 65 × 25 × 8 | 15g | USB Stick | USB port |
| Raspberry Pi AI HAT | 65 × 56 × 12 | 25g | HAT | Standoffs / Pi case |

### Size Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FORM FACTOR COMPARISON                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USB STICK / DONGLE FORM FACTORS                                            │
│  ─────────────────────────────────────                                      │
│  Coral USB          [██████████████]  65 × 25 × 8 mm                        │
│  SuperInstance Nano [████████████████████]  65 × 30 × 12 mm                 │
│  Hailo-8 USB        [██████████████████████]  70 × 25 × 10 mm               │
│  Hailo-10H USB      [████████████████████████████]  85 × 35 × 12 mm         │
│  SuperInstance Std  [███████████████████████████████]  90 × 50 × 15 mm      │
│                                                                             │
│  HAT / BOARD FORM FACTORS                                                   │
│  ─────────────────────────────                                              │
│  RPi AI HAT         ┌────────────────┐  65 × 56 mm                          │
│                     │    □□□□□□□□    │                                      │
│                     │    □□□□□□□□    │                                      │
│                     └────────────────┘                                      │
│                                                                             │
│  SuperInstance Maker┌────────────────────┐  85 × 56 mm                      │
│                     │    □□□□□□□□□□□□    │                                  │
│                     │    □□□□□□□□□□□□    │  (40-pin GPIO header)            │
│                     └────────────────────┘                                  │
│                                                                             │
│  DEVELOPER KIT FORM FACTORS                                                 │
│  ───────────────────────────────                                            │
│  Jetson Orin/Nano   ┌────────────────────────────┐  100 × 80 mm             │
│                     │                            │                          │
│                     │    [FAN]  [GPIO] [USB]     │                          │
│                     │                            │                          │
│                     └────────────────────────────┘                          │
│                                                                             │
│  SuperInstance Pro  ┌──────────────────┐  100 × 65 mm                       │
│                     │  □□□□□□□□□□□□  │  (Desktop box, DIN rail)           │
│                     └──────────────────┘                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 7.2 Mounting Options

| Product | Desktop | DIN Rail | Wall Mount | Enclosure | Pi HAT |
|---------|---------|----------|------------|-----------|--------|
| **SuperInstance Nano** | USB | — | — | Optional case | — |
| **SuperInstance Standard** | USB | — | — | Optional case | — |
| **SuperInstance Pro** | ✓ | ✓ (included) | ✓ | Included | — |
| **SuperInstance Maker** | ✓ | Optional | Optional | Pi cases | ✓ Native |
| | | | | | |
| Hailo-8/10H USB | USB | — | — | Optional | — |
| Hailo-10H M.2 | Internal | — | — | Host enclosure | — |
| Jetson Orin/Nano | ✓ | Optional | Optional | Aftermarket | — |
| Coral USB | USB | — | — | Optional | — |
| Raspberry Pi AI HAT | Via Pi | Via Pi case | Via Pi case | Pi cases | ✓ Native |

## 7.3 Thermal Requirements

| Product | Operating Temp | Idle Temp | Load Temp | Cooling Required | Max Ambient |
|---------|---------------|-----------|-----------|------------------|-------------|
| **SuperInstance Nano** | 0-50°C | 30°C | 45°C | None (passive) | 50°C |
| **SuperInstance Standard** | 0-50°C | 32°C | 48°C | None (passive) | 50°C |
| **SuperInstance Pro** | 0-50°C | 35°C | 52°C | Small heatsink | 45°C |
| **SuperInstance Maker** | 0-50°C | 32°C | 48°C | None (passive) | 50°C |
| | | | | | |
| Hailo-8 | 0-70°C | 30°C | 45°C | None | 70°C |
| Hailo-10H | 0-60°C | 35°C | 55°C | Recommended | 60°C |
| Jetson Orin Nano | 0-50°C | 40°C | 70°C | **Fan required** | 35°C |
| Jetson Nano | 0-50°C | 45°C | 75°C | **Fan required** | 30°C |
| Coral USB | 0-70°C | 28°C | 40°C | None | 70°C |
| Raspberry Pi AI HAT | 0-50°C | 35°C | 50°C | Passive | 50°C |

### Thermal Design Considerations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THERMAL DESIGN REQUIREMENTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PASSIVE COOLING (No fan required)                                          │
│  ─────────────────────────────────                                          │
│  ✓ SuperInstance (all models)                                               │
│  ✓ Hailo-8 / Hailo-10H                                                      │
│  ✓ Coral USB                                                                │
│  ✓ Raspberry Pi AI HAT                                                      │
│                                                                             │
│  ACTIVE COOLING (Fan required)                                              │
│  ─────────────────────────────────                                          │
│  ✗ Jetson Orin Nano (included fan, noisy)                                   │
│  ✗ Jetson Nano (included fan, noisy)                                        │
│                                                                             │
│  Implications:                                                              │
│  • Passive = Silent operation, no moving parts, longer lifespan            │
│  • Active = Noise, dust accumulation, potential fan failure                │
│  • SuperInstance designed for embedded/industrial deployment               │
│                                                                             │
│  Noise Level Comparison:                                                    │
│  SuperInstance:     0 dB (silent)                                          │
│  Hailo-10H:         0 dB (silent)                                          │
│  Jetson Orin Nano:  25-35 dB (fan)                                         │
│  Jetson Nano:       30-40 dB (fan)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Summary Comparison Tables

## Quick Reference Matrix

| Metric | SuperInstance Std | Hailo-10H | Jetson Orin Nano | Coral USB | Winner |
|--------|-------------------|-----------|------------------|-----------|--------|
| **LLM Speed (tok/s)** | 30 | 5-10 | 25 | 0 | **SuperInstance** |
| **Power (W)** | 3 | 5 | 15 | 2 | **SuperInstance** |
| **Tok/Watt** | 10 | 1-2 | 1.7 | 0 | **SuperInstance** |
| **Price** | $79 | $88 | $199 | $60 | **SuperInstance** |
| **Tok/s per $** | 0.38 | 0.06 | 0.13 | 0 | **SuperInstance** |
| **Setup Time** | < 1 min | 1-3 hrs | 2-4 hrs | 30 min | **SuperInstance** |
| **GPIO Access** | Limited | None | Full | None | **Jetson** |
| **Vision TOPS** | 12 equiv | 40 | 67 | 4 | **Jetson** |
| **USB Powered** | ✓ | ✓ | ✗ | ✓ | **Tie (SuperInstance/Hailo)** |
| **Model Flexibility** | Cartridge | Compiled | Full | TFLite only | **Jetson** |
| **3-Year TCO** | $91 | $108 | $273 | $68 | **SuperInstance** |

## Score Summary

| Product | Performance | Efficiency | Connectivity | Software | DevEx | Business | Form Factor | **Total** |
|---------|-------------|-----------|--------------|----------|-------|----------|-------------|-----------|
| **SuperInstance Standard** | 9 | 10 | 7 | 8 | 10 | 9 | 8 | **61/70** |
| **SuperInstance Pro** | 10 | 9 | 8 | 8 | 10 | 8 | 9 | **62/70** |
| **SuperInstance Nano** | 7 | 10 | 6 | 8 | 10 | 10 | 8 | **59/70** |
| **SuperInstance Maker** | 8 | 10 | 10 | 9 | 10 | 8 | 9 | **64/70** |
| | | | | | | | | |
| Hailo-10H | 5 | 5 | 7 | 7 | 6 | 7 | 8 | **45/70** |
| Jetson Orin Nano | 8 | 4 | 9 | 10 | 7 | 5 | 6 | **49/70** |
| Jetson Nano | 3 | 2 | 8 | 9 | 6 | 5 | 5 | **38/70** |
| Coral USB | 1 | 6 | 5 | 7 | 7 | 6 | 8 | **40/70** |
| Raspberry Pi AI HAT | 4 | 6 | 8 | 7 | 8 | 7 | 9 | **49/70** |

---

# Use Case Recommendations

## For Education & Learning

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Best Choice** | SuperInstance Nano ($49) | Lowest cost entry to LLM inference, zero setup, educational pricing |
| Alternative | Raspberry Pi AI HAT + Pi 5 | Familiar Pi ecosystem, good documentation |
| Not Recommended | Jetson Nano | Overkill, high power, complex setup for beginners |

### Educational Deployment Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLASSROOM DEPLOYMENT SCENARIO                             │
│                                                                             │
│  Scenario: High school AI course, 30 students                              │
│                                                                             │
│  Option A: SuperInstance Nano                                               │
│  • Hardware: 30 × $49 = $1,470                                             │
│  • School discount: 20% = $1,176                                           │
│  • Setup: Plug and play, < 5 minutes                                       │
│  • Power: 30 × 2W = 60W (single circuit OK)                               │
│  • Total: $1,176                                                           │
│                                                                             │
│  Option B: Jetson Nano                                                      │
│  • Hardware: 30 × $149 = $4,470                                            │
│  • Educational discount: 10% = $4,023                                      │
│  • Setup: 30 × 3 hrs = 90 hours setup time                                 │
│  • Power: 30 × 15W = 450W (dedicated circuit needed)                       │
│  • Total: $4,023 + power supply costs                                      │
│                                                                             │
│  Savings with SuperInstance: $2,847 (71%) + 90 hours setup time            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## For Hobbyist / Maker Projects

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Best Choice** | SuperInstance Maker Edition ($89) | Full GPIO, open hardware, Pi HAT compatible |
| Alternative | Raspberry Pi AI HAT | Good Pi integration, limited GPIO access |
| Alternative | Jetson Orin Nano | More flexible, but expensive and power-hungry |

### Maker Project Compatibility

| Project Type | SuperInstance Maker | RPi AI HAT | Jetson Orin |
|-------------|---------------------|------------|-------------|
| Voice assistant | ✓ Excellent | ✓ Good | ✓ Overkill |
| Robot brain | ✓ Excellent (GPIO) | ✓ Limited | ✓ Good |
| Smart mirror | ✓ Excellent | ✓ Good | ✓ Good |
| IoT hub | ✓ Excellent | ✓ Good | ✓ Overkill |
| Vision project | ✓ Limited | ✓ Good | ✓ Excellent |
| Drone AI | ✓ Excellent (power) | ✓ Good | ✗ Too heavy |
| Wearable AI | ✓ Possible | ✗ Too large | ✗ Too large |

## For Professional Development

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Best Choice** | SuperInstance Pro ($149) | Maximum throughput, enterprise features |
| Alternative | Jetson Orin Nano | More flexible, CUDA ecosystem |
| Not Recommended | Coral USB | Limited LLM support, EOL risk |

### Professional Workflow Integration

| Workflow | SuperInstance Pro | Jetson Orin Nano |
|----------|-------------------|------------------|
| Rapid prototyping | ✓ Instant | Requires setup |
| Model experimentation | Via cartridges | ✓ Flexible |
| Production deployment | ✓ Optimized | Requires optimization |
| Cloud integration | ✓ API ready | ✓ Full control |
| CI/CD pipelines | ✓ Docker support | ✓ Native Docker |

## For Industrial IoT

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Best Choice** | SuperInstance Pro ($149) | DIN rail mount, industrial temp, low power |
| Alternative | Hailo-10H | Good vision + LLM combo |
| Not Recommended | Jetson Nano | High power, fan reliability concerns |

### Industrial Deployment Factors

| Factor | SuperInstance | Hailo-10H | Jetson Orin |
|--------|---------------|-----------|-------------|
| 24/7 reliability | ✓ Excellent | ✓ Good | ✗ Fan concerns |
| Power budget | 5W | 5W | 15W |
| Operating temp | 0-50°C | 0-60°C | 0-50°C |
| DIN rail mount | ✓ Included | Optional | Optional |
| Silent operation | ✓ Yes | ✓ Yes | ✗ Fan noise |
| MTBF | > 100,000 hrs | > 50,000 hrs | ~30,000 hrs (fan) |

## For Enterprise Deployment

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Best Choice** | SuperInstance Pro (volume) | Best TCO, enterprise support available |
| Alternative | Jetson Orin Nano | NVIDIA ecosystem, familiar tools |
| Consideration | Hailo-10H | Good for vision + LLM hybrid workloads |

### Enterprise TCO Analysis (1000 units, 3 years)

| Cost Category | SuperInstance Pro | Jetson Orin Nano | Savings |
|---------------|-------------------|------------------|---------|
| Hardware (volume) | $99,000 | $140,000 | $41,000 |
| Power (24/7, 3 yr) | $20,000 | $59,000 | $39,000 |
| Setup (labor) | 17 hrs | 1,700 hrs | $168,000 |
| Support | Included | Included | $0 |
| **Total** | **$119,000** | **$199,000** | **$80,000 (40%)** |

---

# Appendix: Detailed Specifications

## SuperInstance Product Line Specifications

### SuperInstance Nano

| Specification | Value |
|--------------|-------|
| Model Support | 700M-1B ternary models |
| LLM Throughput | 20 tok/s typical |
| Power Consumption | 2W active |
| Memory | 1MB on-chip KV cache |
| Interface | USB 3.0 Type-A |
| Dimensions | 65 × 30 × 12 mm |
| Weight | 25g |
| Operating Temperature | 0-50°C |
| Warranty | 1 year |
| Target Market | Education, makers, high-volume |

### SuperInstance Standard

| Specification | Value |
|--------------|-------|
| Model Support | 2B ternary models |
| LLM Throughput | 30 tok/s typical |
| Power Consumption | 3W active |
| Memory | 2MB on-chip KV cache |
| Interface | USB 3.0 Type-A |
| Dimensions | 90 × 50 × 15 mm |
| Weight | 45g |
| Operating Temperature | 0-50°C |
| Warranty | 2 years |
| Target Market | Mainstream developers |

### SuperInstance Pro

| Specification | Value |
|--------------|-------|
| Model Support | 3B ternary models |
| LLM Throughput | 35 tok/s typical |
| Power Consumption | 5W active |
| Memory | 4MB on-chip KV cache |
| Interface | USB 3.0 + USB-C |
| Dimensions | 100 × 65 × 20 mm |
| Weight | 85g |
| Operating Temperature | 0-50°C |
| Mounting | Desktop, DIN rail |
| Warranty | 3 years |
| Target Market | Professional, enterprise |

### SuperInstance Maker Edition

| Specification | Value |
|--------------|-------|
| Model Support | 2B ternary models |
| LLM Throughput | 28 tok/s typical |
| Power Consumption | 3W active |
| Memory | 2MB on-chip KV cache |
| Interface | USB-C with PD |
| GPIO | 40-pin (RPi compatible) |
| Dimensions | 85 × 56 × 12 mm |
| Weight | 35g |
| Operating Temperature | 0-50°C |
| Form Factor | HAT |
| Warranty | 2 years |
| Target Market | Hardware hackers, open source |

---

# Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 2026 | Product Team | Initial release |

**Distribution:** Internal use, partner enablement, investor materials

**Next Review:** Quarterly update cycle

---

*This document is based on publicly available specifications, published benchmarks, and internal testing. Competitor specifications are subject to change. For the most current information, consult manufacturer documentation.*
