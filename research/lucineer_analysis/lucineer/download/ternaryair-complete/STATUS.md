# TernaryAir Project Status

**Last Updated:** March 2026  
**Version:** 0.1.0 (Early Development)

---

## Current State Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Python Simulator | 🟢 Working | Basic inference simulation works |
| REST API Server | 🟡 Partial | OpenAI-compatible endpoints, uses simulator backend |
| RTL (SystemVerilog) | 🟡 Partial | Core modules written, missing testbenches |
| FPGA Synthesis | 🔴 Blocked | RTL needs completion first |
| ASIC Silicon | 🔴 Future | No timeline |

---

## Detailed Component Status

### Python Simulator

| Feature | Status |
|---------|--------|
| Basic inference | ✅ Working |
| Streaming output | ✅ Working |
| Chat mode | ✅ Working |
| Embeddings | ✅ Working (simulated) |
| Real model weights | ❌ Not included |
| Accurate output | ❌ Simplified simulation |
| Performance matching hardware | ❌ No hardware yet |

**What works:**
```python
from ternaryair import Simulator
sim = Simulator()
print(sim.generate("Hello!"))  # Returns text
```

**What doesn't:**
- Output is not from a real ternary model
- No actual model weights included
- Performance doesn't match target hardware

### RTL Source Code

| Module | RTL Written | Testbench | Synthesizes | Timing Closed |
|--------|-------------|-----------|-------------|---------------|
| `rau.sv` | ✅ Yes | ❌ No | ❓ Untested | ❌ No |
| `synaptic_array.sv` | ✅ Yes | ❌ No | ❓ Untested | ❌ No |
| `weight_rom.sv` | 🟡 Partial | ❌ No | ❓ Untested | ❌ No |
| `kv_cache.sv` | ✅ Yes | ❌ No | ❓ Untested | ❌ No |
| `top_level.sv` | 🟡 Partial | ❌ No | ❌ Missing deps | ❌ No |
| `attention.sv` | ❌ Missing | ❌ No | - | - |
| `feedforward.sv` | ❌ Missing | ❌ No | - | - |
| `layer_norm.sv` | ❌ Missing | ❌ No | - | - |
| `softmax.sv` | ❌ Missing | ❌ No | - | - |
| `embedding.sv` | ❌ Missing | ❌ No | - | - |

**Critical gaps:**
1. No testbenches - zero verification
2. Missing core modules (attention, FFN, softmax)
3. `top_level.sv` references non-existent modules
4. No synthesis scripts or constraints

**What's needed for FPGA synthesis:**
- Complete all missing modules
- Add testbenches for each module
- Create synthesis constraints (.xdc)
- Add Makefile for FPGA toolchain

---

## Performance Claims vs Reality

| Metric | Claimed | Demonstrated | Notes |
|--------|---------|--------------|-------|
| Throughput | 100+ tok/s | 100 tok/s (sim) | Simulator speed, not hardware |
| Latency | <50ms first token | ~10ms (sim) | CPU-based, not meaningful |
| Power | 3-5W | N/A | No hardware exists |
| Price | $99 | N/A | No hardware exists |

**Important:** All performance claims are **targets**, not demonstrated results. There is no hardware to measure.

---

## What's Real vs Aspirational

### ✅ Real (Works Today)

1. **Python package installs** - `pip install ternaryair` works
2. **Simulator runs** - Returns text from prompts
3. **REST API** - OpenAI-compatible server works
4. **RTL concept** - RAU code demonstrates the idea
5. **Documentation** - Website explains the concepts

### ❌ Not Real (Aspirational)

1. **Hardware device** - No physical product exists
2. **Real ternary model** - Using simplified simulation
3. **100 tok/s on 3W** - No hardware to measure
4. **$99 price** - No manufacturing, no cost basis
5. **Shipping timeline** - No commitment

---

## Honest Roadmap

### Phase 1: Foundation (Current)
- [x] Python simulator works
- [ ] Complete RTL modules
- [ ] Add testbenches
- [ ] FPGA synthesis demo

### Phase 2: Validation (Future)
- [ ] Run real ternary model weights
- [ ] FPGA prototype running live
- [ ] Accuracy benchmarks published
- [ ] Power measurements on FPGA

### Phase 3: Production (Uncertain)
- [ ] ASIC design complete
- [ ] MPW shuttle tapeout
- [ ] Working silicon samples
- [ ] Manufacturing partner

**Timeline:** No commitments. This is open-source development.

---

## How You Can Help

### RTL Development
- Complete missing modules
- Add testbenches
- Create FPGA synthesis flow

### Model Weights
- Convert BitNet weights to TernaryAir format
- Create weight encoding tools
- Benchmark accuracy

### Documentation
- Write tutorials
- Create video demos
- Translate to other languages

### Testing
- Try the simulator
- Report bugs
- Suggest improvements

---

## Competitors (Honest Comparison)

| Product | Status | Price | Performance |
|---------|--------|-------|-------------|
| **TernaryAir** | 🔴 Dev | TBD | TBD |
| Hailo-10H | ✅ Shipping | $70 | 9 tok/s (Qwen-1.5B) |
| Jetson Orin Nano | ✅ Shipping | $250 | 30 tok/s |
| Ollama (CPU) | ✅ Free | $0 | 5-20 tok/s |
| Groq Cloud | ✅ Available | Pay/use | 300+ tok/s |

**Why consider TernaryAir?** Only if you want to:
- Contribute to open-source AI hardware
- Learn about ternary inference
- Experiment with the architecture

**For production today:** Use Hailo, Jetson, or cloud services.

---

## Contact

- **GitHub:** [github.com/superinstance/ternaryair](https://github.com/superinstance/ternaryair)
- **Issues:** [github.com/superinstance/ternaryair/issues](https://github.com/superinstance/ternaryair/issues)
- **Discussions:** [github.com/superinstance/ternaryair/discussions](https://github.com/superinstance/ternaryair/discussions)

---

*This is a living document. Status will be updated as development progresses.*
