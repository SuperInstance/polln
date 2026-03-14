<p align="center">
  <img src="docs/assets/superinstance-logo.png" alt="SuperInstance.AI Logo" width="400">
</p>

<h1 align="center">SuperInstance.AI SDK</h1>

<p align="center">
  <strong>Run LLMs at the Edge — Zero Setup, Maximum Performance</strong>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#community">Community</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/superinstance-sdk/">
    <img src="https://img.shields.io/pypi/v/superinstance-sdk.svg" alt="PyPI Version">
  </a>
  <a href="https://github.com/superinstance-ai/superinstance-sdk/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
  </a>
  <a href="https://github.com/superinstance-ai/superinstance-sdk/actions">
    <img src="https://github.com/superinstance-ai/superinstance-sdk/workflows/CI/badge.svg" alt="Build Status">
  </a>
  <a href="https://discord.gg/superinstance">
    <img src="https://img.shields.io/discord/superinstance?color=5865F2&label=Discord&logo=discord" alt="Discord">
  </a>
</p>

---

## What is SuperInstance.AI?

SuperInstance.AI delivers **dedicated hardware for language model inference** — a USB device that runs LLMs locally at 25-35 tokens/second with just 2-5 watts of power. No cloud. No complex setup. No GPU required.

```python
from superinstance import Device

# That's it. No configuration needed.
device = Device()              # Auto-detect hardware
model = device.load_cartridge() # Load pre-installed model
print(model.generate("Hello, I am").text)
```

### Why SuperInstance?

| Feature | SuperInstance | NVIDIA Jetson | Ollama (CPU) | Cloud APIs |
|---------|--------------|---------------|--------------|------------|
| **Setup Time** | <5 minutes | 2-8 hours | 30 min | 5 min |
| **Power Draw** | 2-5W | 7-40W | 65-150W | N/A |
| **Latency** | 30-40ms TTFT | 50-200ms | 200-500ms | 200-1000ms |
| **Privacy** | 100% local | 100% local | 100% local | Data leaves device |
| **Cost** | $35-79 (once) | $150-500 | $500+ (PC) | $0.002-0.06/1K tokens |
| **Offline** | ✅ | ✅ | ✅ | ❌ |

## Installation

### Requirements
- Python 3.8 or later
- SuperInstance hardware device (NANO, Standard, PRO, or Maker Edition)
- USB 3.0+ port

### Install the SDK

```bash
pip install superinstance-sdk
```

Verify installation:

```python
import superinstance
print(superinstance.__version__)  # Should print: 1.0.0
```

## Quick Start

### 1. Basic Text Generation

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

response = model.generate("Explain quantum computing in one paragraph.")
print(response.text)
print(f"Generated {response.generated_tokens} tokens at {response.tokens_per_second:.1f} tok/s")
```

### 2. Streaming Output

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

# Real-time token streaming
for token in model.generate_stream("Write a haiku about programming:"):
    print(token, end="", flush=True)
```

### 3. Chat Applications

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "How do I read a file in Python?"},
]

response = model.chat(messages)
print(response.text)
```

### 4. Custom Generation Parameters

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Fine-tune generation behavior
config = GenerationConfig(
    temperature=0.7,           # Creativity level (0.0-2.0)
    top_p=0.9,                 # Nucleus sampling
    max_tokens=256,            # Maximum output length
    stop_sequences=["\n\n"],   # Stop generation on these strings
)

response = model.generate("Once upon a time", config)
```

## Features

### 🚀 Zero-Setup Experience
- **Auto-detection**: Plug in the device, run your code — no drivers, no configuration
- **Pre-loaded models**: Cartridges come with optimized models ready to run
- **Cross-platform**: Works on Linux, macOS, and Windows

### ⚡ Performance
- **25-35 tokens/second** sustained generation
- **30-40ms time-to-first-token** latency
- **2-5W power consumption** — runs on USB power
- **Energy efficient**: ~0.1 joules per generated token

### 🔧 Developer-Friendly API
- **Streaming-first**: All generation methods support real-time token streaming
- **Chat support**: Built-in multi-turn conversation handling
- **Tokenization**: Access to token IDs for advanced use cases
- **Profiling**: Built-in performance and energy measurement

### 🌐 Multi-Language Support
- **Python** (Primary) — `pip install superinstance-sdk`
- **C/C++** — Native library with header-only option
- **Rust** (Coming Soon) — Safe Rust bindings
- **JavaScript** (Coming Soon) — Node.js integration

### 🎯 Hardware Variants

| Edition | Target User | Key Features |
|---------|-------------|--------------|
| **NANO** | Hobbyists, Students | USB4 stick, single model cartridge |
| **Standard** | Developers | LPDDR5 memory, faster inference |
| **PRO** | Professionals | Custom model support, advanced APIs |
| **Maker Edition** | Hardware hackers | GPIO header, sensor integration |

## Documentation

- **[Getting Started Guide](docs/getting-started.md)** — 5-minute quickstart tutorial
- **[Installation Guide](docs/installation.md)** — Detailed setup instructions
- **[API Reference](docs/api-reference.md)** — Complete SDK documentation
- **[Examples Gallery](docs/examples.md)** — Sample projects and code
- **[Troubleshooting](docs/troubleshooting.md)** — Common issues and solutions
- **[Roadmap](docs/roadmap.md)** — What's coming next

## Examples

### Build a Voice Assistant

```python
from superinstance import Device, GenerationConfig
import speech_recognition as sr
import pyttsx3

device = Device()
model = device.load_cartridge()

recognizer = sr.Recognizer()
engine = pyttsx3.init()

with sr.Microphone() as source:
    print("Listening...")
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
    
    print(f"You: {text}")
    response = model.chat([
        {"role": "system", "content": "You are a helpful voice assistant."},
        {"role": "user", "content": text}
    ])
    
    print(f"Assistant: {response.text}")
    engine.say(response.text)
    engine.runAndWait()
```

### Integrate with Home Assistant

```python
# custom_components/superinstance/__init__.py
from superinstance import Device

async def async_setup(hass, config):
    device = Device()
    model = device.load_cartridge()
    
    async def handle_generate(call):
        prompt = call.data.get("prompt", "")
        response = model.generate(prompt)
        hass.states.async_set("sensor.llm_response", response.text)
    
    hass.services.async_register("superinstance", "generate", handle_generate)
    return True
```

### Create a RAG System

```python
from superinstance import Device
import chromadb

device = Device()
model = device.load_cartridge()
client = chromadb.Client()
collection = client.create_collection("documents")

def rag_query(query: str, k: int = 3):
    # Retrieve relevant documents
    results = collection.query(query_texts=[query], n_results=k)
    context = "\n".join(results["documents"][0])
    
    # Generate response with context
    prompt = f"""Context: {context}
    
Question: {query}

Answer based on the context above:"""
    
    return model.generate(prompt).text
```

See [Examples Gallery](docs/examples.md) for more projects!

## Community

Join our growing community of developers building the future of edge AI:

- **[Discord](https://discord.gg/superinstance)** — Real-time chat, support, and announcements
- **[GitHub Discussions](https://github.com/superinstance-ai/superinstance-sdk/discussions)** — Q&A and feature requests
- **[Twitter](https://twitter.com/SuperInstanceAI)** — News and updates
- **[YouTube](https://youtube.com/@SuperInstanceAI)** — Tutorials and demos

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we need help:
- 📖 Documentation improvements
- 🐛 Bug fixes and testing
- 🎨 Example projects and tutorials
- 🌐 Language bindings (Rust, JavaScript)
- 🔌 Integrations (LangChain, LlamaIndex, etc.)

### Project Structure

```
superinstance-ai/
├── superinstance/           # Core SDK package
│   ├── __init__.py
│   ├── device.py           # Device management
│   ├── model.py            # Model inference
│   ├── profiler.py         # Performance profiling
│   └── errors.py           # Exception classes
├── examples/               # Example projects
│   ├── chat-bot/
│   ├── voice-assistant/
│   ├── home-assistant/
│   └── rag-system/
├── docs/                   # Documentation
├── tests/                  # Test suite
└── bindings/               # Language bindings
    ├── cpp/
    ├── rust/
    └── js/
```

## Roadmap

### v1.0 (Current)
- ✅ Python SDK with streaming support
- ✅ Chat API with multi-turn conversations
- ✅ Built-in profiling and energy measurement
- ✅ Linux, macOS, Windows support

### v1.1 (Q2 2026)
- 🔲 C/C++ SDK release
- 🔲 Rust bindings
- 🔲 JavaScript/Node.js SDK
- 🔲 VS Code extension

### v1.2 (Q3 2026)
- 🔲 GPIO API for Maker Edition
- 🔲 ROS2 integration
- 🔲 LangChain integration
- 🔲 Model comparison tools

### v2.0 (Q4 2026)
- 🔲 Multi-device parallel inference
- 🔲 Custom model compilation
- 🔲 Fine-tuning support
- 🔲 Enterprise features

See [Roadmap](docs/roadmap.md) for details.

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.

## Acknowledgments

SuperInstance.AI is inspired by the simplicity of Arduino, the power of NVIDIA Jetson, and the accessibility of Raspberry Pi. We believe AI hardware should be as easy to use as a USB drive.

---

<p align="center">
  Made with ❤️ by the SuperInstance.AI team
</p>

<p align="center">
  <a href="https://superinstance.ai">Website</a> •
  <a href="https://docs.superinstance.ai">Documentation</a> •
  <a href="https://discord.gg/superinstance">Discord</a> •
  <a href="https://twitter.com/SuperInstanceAI">Twitter</a>
</p>
