# Getting Started with SuperInstance

**Time to first inference: 5 minutes** ⏱️

This guide will get you running your first LLM inference on SuperInstance hardware in under 5 minutes.

## Prerequisites

Before you start, make sure you have:

- ✅ SuperInstance device (Micro, Standard, or Maker Edition)
- ✅ USB cable (included with device)
- ✅ Computer with USB 3.0 port
- ✅ Python 3.8 or higher

## Step 1: Install the SDK (30 seconds)

```bash
pip install superinstance-sdk
```

## Step 2: Connect Your Device (30 seconds)

1. Plug your SuperInstance device into a USB 3.0 port
2. Wait for the LED to turn solid green (ready state)
3. Verify detection:

```bash
python -c "from superinstance import Device; print(Device.list_devices())"
```

You should see output like:
```
[DeviceInfo(name='SuperInstance Micro', serial='SI-2024-XXXX', status='ready')]
```

## Step 3: Your First Inference (1 minute)

Create a file called `hello.py`:

```python
from superinstance import Device

# Auto-detect and connect to device
device = Device()
print(f"Connected to: {device.name}")

# Load the model from the inserted cartridge
model = device.load_cartridge()
print(f"Model loaded: {model.model_name}")

# Generate text
result = model.generate("Hello, I am an AI assistant")
print(result.text)
```

Run it:
```bash
python hello.py
```

## Step 4: Try Streaming (1 minute)

Streaming gives you real-time token output:

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

print("AI: ", end="")
for token in model.generate_stream("Tell me a short story about a robot"):
    print(token, end="", flush=True)
print()
```

## Step 5: Chat Mode (1 minute)

For conversational applications:

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a Python function to reverse a string"}
]

response = model.chat(messages)
print(response.text)
```

## Common Options

### Generation Configuration

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

config = GenerationConfig(
    max_tokens=100,
    temperature=0.7,
    top_p=0.9,
    stop_sequences=["\n\n"]
)

result = model.generate("Write a haiku", config=config)
```

### Device Selection

If you have multiple devices:

```python
from superinstance import Device

# List all devices
devices = Device.list_devices()
for d in devices:
    print(f"{d.serial}: {d.name} ({d.status})")

# Connect to specific device
device = Device(serial="SI-2024-XXXX")
```

### Performance Profiling

```python
from superinstance import Device, Profiler

device = Device()
model = device.load_cartridge()

with Profiler() as p:
    result = model.generate("Explain quantum computing")

print(p.report())
# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Total time:     1.24s
# Tokens:         45
# Throughput:     36.3 tok/s
# Power avg:      3.2W
# Energy/token:   0.088 mJ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Troubleshooting

### Device Not Found

```bash
# Check USB connection
lsusb | grep -i super

# Check permissions (Linux)
sudo usermod -a -G superinstance $USER
# Log out and back in
```

### Import Error

```bash
# Reinstall
pip uninstall superinstance-sdk
pip install superinstance-sdk

# Verify installation
python -c "import superinstance; print(superinstance.__version__)"
```

### Slow Performance

- Ensure USB 3.0 port (blue connector)
- Close other USB-heavy applications
- Check power supply if using USB hub

## Next Steps

- 📖 Read the [API Reference](api-reference.md)
- 🎯 Try [Example Projects](examples.md)
- 🐛 [Report Issues](https://github.com/superinstance-ai/sdk/issues)
- 💬 [Join Discord](https://discord.gg/superinstance)

---

**Need help?** Join our [Discord](https://discord.gg/superinstance) or open a [GitHub issue](https://github.com/superinstance-ai/sdk/issues).
