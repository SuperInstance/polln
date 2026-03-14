<p align="center">
  <img src="docs/images/logo.png" alt="TernaryAir Logo" width="200">
</p>

<h1 align="center">TernaryAir</h1>

<p align="center">
  <strong>Open Source Air-Gapped Ternary Inference Hardware</strong>
</p>

<p align="center">
  <em>The hardware boundary between you and AI.</em>
</p>

<p align="center">
  <a href="https://github.com/superinstance/ternaryair/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/superinstance/ternaryair" alt="License">
  </a>
  <a href="https://github.com/superinstance/ternaryair/actions">
    <img src="https://github.com/superinstance/ternaryair/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/ternaryair/">
    <img src="https://img.shields.io/pypi/v/ternaryair" alt="PyPI">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/ternaryair" alt="Python Version">
  </a>
</p>

<p align="center">
  <a href="#-what-is-this">What is This</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-why-it-matters">Why It Matters</a> •
  <a href="#-learning-center">Learning Center</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## 🎯 What Is This?

TernaryAir is an **open-source ternary inference engine** — complete hardware and software for running AI models locally, privately, and securely.

**Three core principles:**

| Principle | What It Means |
|-----------|---------------|
| 🔒 **Air-Gapped Security** | No network. No internet. No data leakage possible. |
| 🪨 **Immutable Weights** | Model frozen in silicon. Cannot be modified or stolen. |
| 🛡️ **Agent Isolation** | Hardware boundary between AI and your system. |

**Target Specifications:**

| Metric | Target |
|--------|--------|
| Retail Price | $99 |
| Performance | 100+ tokens/second |
| Power | 3-5W (USB powered) |
| Security | Hardware-enforced, air-gapped |

---

## ⚡ Quick Start

### Installation

```bash
pip install ternaryair
```

### Basic Usage

```python
from ternaryair import TernaryAir

# Connect to device (or use simulator)
device = TernaryAir()

# Generate text
response = device.generate("Hello, how are you?")
print(response)
# Output: "I'm doing well, thank you for asking! How can I help you today?"

# Streaming
for token in device.stream("Tell me a story about"):
    print(token, end='', flush=True)
```

### Simulation (No Hardware Required)

```python
from ternaryair import TernaryAir, Simulator

# Use software simulator
device = TernaryAir(backend=Simulator())
response = device.generate("What is machine learning?")
```

### RTL Simulation

```bash
# Clone the repository
git clone https://github.com/superinstance/ternaryair.git
cd ternaryair

# Run behavioral simulation (requires Icarus Verilog)
cd hardware/rtl
iverilog -g2012 -o sim *.sv
vvp sim
```

---

## 🔐 Security Model

```
┌──────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                           │
│  [Files] [Network] [Apps] [AI Agents]                        │
└──────────────────────────────────────────────────────────────┘
                         │ USB
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    TERNARYAIR DEVICE                         │
│                                                              │
│   ✗ No file access        (no filesystem)                   │
│   ✗ No network access     (no network hardware)             │
│   ✗ No memory persistence (volatile SRAM only)              │
│   ✗ No self-modification  (weights in ROM)                  │
│   ✗ No code execution     (fixed-function hardware)         │
│                                                              │
│   It's a FUNCTION, not a PROGRAM.                           │
│   Input → Inference → Output. Nothing else.                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**This is your hardware boundary between AI agents and your life.**

---

## 💡 Why It Matters

### The Problem

| Risk | Cloud AI | Local GPU | TernaryAir |
|------|----------|-----------|------------|
| Your data leaves device | ✅ Yes | ❌ No | ❌ No |
| Model can be modified | ✅ Yes | ✅ Yes | ❌ **No** |
| Agent can access files | ✅ Yes | ✅ Yes | ❌ **No** |
| Agent can access network | ✅ Yes | ⚠️ Maybe | ❌ **No** |
| Remembers your inputs | ✅ Yes | ✅ Yes | ❌ **No** |
| Costs $500+ | ✅ Often | ✅ Often | ❌ **$99** |
| Open source | ❌ No | ❌ No | ✅ **MIT** |

### The Solution

AI agents run as software. Software can be compromised.

TernaryAir runs inference as **hardware**. The model is frozen in silicon. It cannot be modified, cannot access your files, cannot reach the network, cannot remember what you typed.

**Hardware-enforced security that no software can bypass.**

---

## 🎓 Learning Center

**New to AI hardware? Start here:** [Learning Center →](docs/LEARNING_CENTER/README.md)

We've created a comprehensive educational resource with 5 levels:

| Level | Audience | Time | Focus |
|-------|----------|------|-------|
| [Beginner](docs/LEARNING_CENTER/beginner/README.md) | Everyone | 30 min | Stories, visuals, intuition |
| [Intermediate](docs/LEARNING_CENTER/intermediate/README.md) | Tech users | 45 min | Analogies, examples, concepts |
| [Advanced](docs/LEARNING_CENTER/advanced/README.md) | Developers | 60 min | Code, architecture, API |
| [Expert](docs/LEARNING_CENTER/expert/README.md) | Hardware eng. | 90 min | RTL, physics, fabrication |
| [Researcher](docs/LEARNING_CENTER/researcher/README.md) | Academics | 120 min | Math, papers, citations |

**[5-Minute Guided Tour →](docs/LEARNING_CENTER/GUIDED_TOUR.md)**

---

## 📚 Documentation

### For Users
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get up and running
- **[API Reference](docs/api/README.md)** - SDK documentation
- **[Examples](software/examples/)** - Code samples and tutorials

### For Developers
- **[Architecture](docs/ARCHITECTURE.md)** - Technical deep dive
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Security Model](security/SECURITY_MODEL.md)** - Security documentation

### For Hardware Engineers
- **[RTL Source](hardware/rtl/)** - SystemVerilog implementation
- **[FPGA Guide](hardware/fpga/README.md)** - FPGA prototyping
- **[Reference Design](hardware/reference/)** - PCB, BOM, enclosure

---

## 🏗️ Repository Structure

```
ternaryair/
├── LICENSE              ← MIT License
├── README.md            ← This file
├── CHANGELOG.md         ← Version history
├── CONTRIBUTING.md      ← How to contribute
├── SECURITY.md          ← Security policy
│
├── hardware/
│   ├── rtl/             ← SystemVerilog source (production-ready)
│   │   ├── top_level.sv      - Main inference engine
│   │   ├── synaptic_array.sv - PE array implementation
│   │   ├── rau.sv            - Rotation-Accumulate Unit
│   │   ├── weight_rom.sv     - Mask-locked weight storage
│   │   └── kv_cache.sv       - Key-value cache
│   │
│   ├── fpga/            ← FPGA prototype files
│   │   ├── bitstreams/  - Pre-built bitstreams
│   │   ├── constraints/ - Timing constraints
│   │   └── scripts/     - Build scripts
│   │
│   └── reference/       ← Reference designs
│       ├── pcb/         - KiCad PCB files
│       ├── bom/         - Bill of materials
│       └── enclosure/   - 3D printable case
│
├── software/
│   ├── sdk/             ← Python SDK (ternaryair package)
│   ├── drivers/         ← USB drivers
│   └── examples/        ← Example applications
│
├── models/
│   ├── converter/       ← FP16 → Ternary conversion
│   ├── pretrained/      ← Ready-to-use models
│   └── training/        ← Training ternary models
│
├── security/
│   └── SECURITY_MODEL.md ← Security analysis
│
└── docs/
    ├── LEARNING_CENTER/ ← Educational content
    ├── ARCHITECTURE.md  ← Technical deep dive
    └── API.md           ← Interface specification
```

---

## 🔧 Key Innovation: The RAU

The Rotation-Accumulate Unit replaces multiplication with sign manipulation:

```
Traditional MAC:  result = activation × weight
                  Gates: ~500 per bit, Power: High

TernaryAir RAU:   result = activation ⊕ weight
                  Gates: ~50 total, Power: Low

Ternary weights {-1, 0, +1} mean:
  +1: Pass activation through
   0: Zero output
  -1: Negate activation

No multiplier needed. 90% gate reduction.
```

---

## 📖 Origin Story

> I'm a fisherman and a developer.
>
> I needed AI that works on a boat, in the middle of nowhere, with no internet and limited power. Cloud AI doesn't work there. Local LLMs needed expensive GPUs I couldn't justify.
>
> So I designed my own architecture — efficient enough for USB power, cheap enough for anyone to afford, and secure enough that it can't be compromised.
>
> The mask-locked design started as a cost optimization (no external memory for weights). But I realized it's also the most secure AI architecture possible — the model is literally frozen in silicon. It can't be modified, can't be extracted, can't phone home.
>
> That's the hardware boundary between you and AI agents.
>
> I'm releasing everything under MIT license. Build your own. Improve it. Use it for whatever you want.
>
> AI should work for you, not the other way around.

**— Casey DiGennaro, SuperInstance.AI**

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

| Type | How |
|------|-----|
| Bug fixes | Submit a PR |
| Features | Open an issue first |
| Documentation | Always needed |
| Security research | Please audit and publish findings |
| Applications | Share what you built |

---

## 📜 License

MIT License

Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)

Free to use, modify, and distribute. No royalties. No restrictions.

---

## 🔗 Links

- **Repository:** [github.com/superinstance/ternaryair](https://github.com/superinstance/ternaryair)
- **Author:** [Casey DiGennaro](https://github.com/caseydigennaro)
- **Organization:** [SuperInstance.AI](https://github.com/SuperInstance-AI)
- **Issues:** [GitHub Issues](https://github.com/superinstance/ternaryair/issues)
- **Discussions:** [GitHub Discussions](https://github.com/superinstance/ternaryair/discussions)

---

**If you believe in private, affordable, secure AI — star ⭐ this repo.**
