# TernaryAir

**The hardware boundary between you and AI.**

---

## ⚠️ Project Status

**Current State:** Early development. This is a work-in-progress open-source project.

| Component | Status |
|-----------|--------|
| RTL Architecture | 🟡 Design phase |
| FPGA Prototype | 🔴 Not yet |
| ASIC Silicon | 🔴 Not yet |
| Python Simulator | 🟢 Working |
| REST API Server | 🟢 Working |

**Can I buy this?** Not yet. This is open-source development, not a shipping product.

**Can I test this?** Yes! Install the simulator below.

---

## 🚀 Quick Start (30 seconds)

```bash
# Install the Python package
pip install ternaryair

# Run the demo
python -c "from ternaryair import demo; demo.run()"
```

Or use the OpenAI-compatible API:

```bash
# Start the API server
ternaryair-server

# In another terminal, use with OpenAI SDK
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='none')
print(client.chat.completions.create(
    model='ternaryair',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
"
```

---

## 📦 What's In This Package

```
ternaryair/
├── README.md              # This file
├── STATUS.md              # Detailed project status
├── rtl/                   # SystemVerilog RTL (work in progress)
│   ├── rau.sv             # Rotation-Accumulate Unit
│   ├── synaptic_array.sv  # Parallel RAU array
│   ├── weight_rom.sv      # Mask-locked weight storage
│   ├── kv_cache.sv        # KV cache controller
│   └── top_level.sv       # Top-level FSM
├── simulator/             # Python simulation
├── docs/                  # Documentation
└── website/               # Website source (Next.js)
```

---

## 🎯 What TernaryAir Is

TernaryAir is an **open-source project** exploring a simple question:

> *What if AI model weights were encoded directly in silicon, rather than stored in memory?*

The core insights:

1. **Ternary Weights** {-1, 0, +1}: Neural networks can maintain accuracy with just three weight values
2. **Multiplication → Addition**: With ternary weights, multiply-accumulate becomes add/subtract/pass
3. **Mask-Locking**: Weights encoded in metal interconnects have zero access latency and zero access energy

This is **not a new idea** - it builds on:
- [BitNet b1.58](https://arxiv.org/abs/2402.17764) - Microsoft's ternary LLM
- [iFairy](https://arxiv.org/abs/2508.05571) - Peking University's complex-valued ternary networks
- [TeLLMe](https://arxiv.org/abs/2510.15926) - FPGA ternary inference

---

## 🔬 Current Capabilities

### Python Simulator

```python
from ternaryair import Simulator

# Create simulator with a small model
sim = Simulator(model="debug-tiny")  # 125M params, fast for testing

# Generate text
response = sim.generate("The meaning of life is", max_tokens=50)
print(response)

# Stream output
for token in sim.stream("Tell me a story about"):
    print(token, end="", flush=True)
```

### REST API

```bash
# Start server
ternaryair-server --port 8000

# Endpoints available:
# POST /v1/completions
# POST /v1/chat/completions
# GET /v1/models
# GET /health
```

### RTL Status

| Module | RTL | Testbench | Synthesizes | FPGA Tested |
|--------|-----|-----------|-------------|-------------|
| RAU | ✅ | 🔴 | 🔴 | 🔴 |
| Synaptic Array | ✅ | 🔴 | 🔴 | 🔴 |
| Weight ROM | 🟡 | 🔴 | 🔴 | 🔴 |
| KV Cache | ✅ | 🔴 | 🔴 | 🔴 |
| Top Level | 🟡 | 🔴 | 🔴 | 🔴 |

See [STATUS.md](STATUS.md) for detailed progress.

---

## 📊 Honest Comparison

| Feature | TernaryAir | Ollama | Hailo-10H | Jetson Orin |
|---------|------------|--------|-----------|--------------|
| Available now | 🔴 No | ✅ Yes | ✅ Yes | ✅ Yes |
| Open source | ✅ Yes | ✅ Yes | 🔴 No | 🔴 No |
| Price | TBD | Free | $70 | $249 |
| Power | Target 3-5W | Varies | 5W | 7-15W |
| Performance | TBD | Varies | 9 tok/s | 30 tok/s |

**Why choose TernaryAir?** Right now, you shouldn't - it's not ready. But if you're interested in:
- Open-source AI hardware
- Understanding ternary inference
- Contributing to early-stage research

Then welcome! We'd love your help.

---

## 🤝 Contributing

This project needs help with:

1. **RTL completion** - Complete modules, add testbenches
2. **FPGA prototyping** - Get something running on KV260
3. **Simulator accuracy** - Match real ternary inference behavior
4. **Documentation** - Tutorials, explanations, examples
5. **Benchmarks** - Real accuracy measurements

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help.

---

## 📜 License

MIT License - Open source forever.

---

## 🙋 FAQ

**Q: When can I buy a TernaryAir device?**  
A: No timeline. This is a research project. If it succeeds, hardware will follow.

**Q: Is this vaporware?**  
A: The simulator works. The RTL is incomplete. Judge for yourself.

**Q: How is this different from BitNet?**  
A: BitNet proves ternary models work. TernaryAir tries to build dedicated hardware for them.

**Q: Can I use this in production?**  
A: The simulator works for development. But there's no hardware to deploy.

**Q: Who's behind this?**  
A: Open-source contributors. Started by Casey DiGennaro.

---

*The hardware boundary between you and AI - coming soon (or not).*

**GitHub:** [github.com/superinstance/ternaryair](https://github.com/superinstance/ternaryair)
