# SuperInstance SDK

**The fastest way to run LLM inference at the edge**

SuperInstance is a hardware-accelerated inference SDK for the mask-locked neural network chip. Get 25-35 tokens/second at 2-5 watts with zero setup.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Discord](https://img.shields.io/discord/1234567890?color=7289da&label=Discord)](https://discord.gg/superinstance)

## 🚀 Quick Start

### Installation

```bash
pip install superinstance-sdk
```

### Hello World (3 lines)

```python
from superinstance import Device

device = Device()  # Auto-detect, zero config
model = device.load_cartridge()  # Use inserted cartridge

# Generate text
result = model.generate("The future of AI is")
print(result.text)
# Output: "The future of AI is local, private, and efficient..."
```

### Streaming Output

```python
# Stream tokens in real-time
for token in model.generate_stream("Tell me a story"):
    print(token, end="", flush=True)
```

### Chat Interface

```python
# OpenAI-compatible chat format
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is edge AI?"}
]

response = model.chat(messages)
print(response.text)
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Zero Setup** | Plug in device, run code. No CUDA, no drivers, no configuration |
| **Streaming** | Real-time token generation with `generate_stream()` |
| **Profiling** | Built-in performance and power analysis |
| **Debug Mode** | Layer-by-layer inspection for development |
| **Multi-language** | Python (P0), C/C++ (P0), Rust (P1), JavaScript (P1) |

## 📊 Performance

| Metric | SuperInstance | Jetson Orin Nano | Hailo-10H |
|--------|---------------|------------------|-----------|
| Throughput | 25-35 tok/s | 15-25 tok/s | 5-10 tok/s |
| Power | 2-5W | 7-15W | 6W |
| Setup Time | <5 min | 2-8 hours | 1-2 hours |
| Price | $35-79 | $149-199 | $70-90 |

## 🔧 Requirements

- Python 3.8 or higher
- SuperInstance device (Micro, Standard, or Maker Edition)
- USB 3.0 port (or USB-C for newer models)
- Linux, macOS, or Windows

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md) - 5-minute quickstart
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Examples](docs/examples.md) - Real-world use cases
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🛠️ Development Mode

No hardware? No problem. Use simulation mode:

```bash
export SUPERINSTANCE_SIMULATE=1
python your_script.py
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- 🐛 [Report a bug](https://github.com/superinstance-ai/sdk/issues/new?template=bug_report.md)
- 💡 [Request a feature](https://github.com/superinstance-ai/sdk/issues/new?template=feature_request.md)
- ❓ [Ask a question](https://github.com/superinstance-ai/sdk/issues/new?template=question.md)

## 📜 License

Apache 2.0 - see [LICENSE](LICENSE) for details.

## 🌟 Star History

If you find SuperInstance useful, please consider giving us a star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=superinstance-ai/sdk&type=Date)](https://star-history.com/#superinstance-ai/sdk&Date)

## 📞 Connect

- **Discord**: [Join our community](https://discord.gg/superinstance)
- **Twitter**: [@SuperInstanceAI](https://twitter.com/SuperInstanceAI)
- **Email**: hello@superinstance.ai

---

Made with ❤️ by the SuperInstance team
