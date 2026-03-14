# Getting Started with SuperInstance.AI

Welcome to SuperInstance.AI! This guide will get you running your first LLM inference in under 5 minutes.

## Prerequisites

Before you begin, make sure you have:

- **SuperInstance hardware device** (NANO, Standard, PRO, or Maker Edition)
- **USB 3.0+ port** on your computer
- **Python 3.8 or later**
- **Operating System**: Linux, macOS 10.15+, or Windows 10/11

## Quick Start (5 Minutes)

### Step 1: Install the SDK

Open your terminal and run:

```bash
pip install superinstance-sdk
```

### Step 2: Connect Your Device

1. Plug your SuperInstance device into a USB 3.0+ port
2. Wait for the device LED to turn solid green (ready state)
3. Verify the device is detected:

```python
from superinstance import Device

devices = Device.list_devices()
print(f"Found {len(devices)} device(s)")
```

Expected output:
```
Found 1 device(s)
```

### Step 3: Run Your First Inference

Create a file called `hello.py`:

```python
from superinstance import Device

# Connect to device (auto-detect)
device = Device()

# Load the pre-installed model from cartridge
model = device.load_cartridge()

# Generate text
response = model.generate("Hello, I am")

print(response.text)
print(f"\nGenerated {response.generated_tokens} tokens at {response.tokens_per_second:.1f} tok/s")
```

Run it:

```bash
python hello.py
```

Expected output:
```
Hello, I am a language model running on SuperInstance hardware. I can help you with a wide variety of tasks including answering questions, writing content, and assisting with programming...

Generated 45 tokens at 28.5 tok/s
```

🎉 **Congratulations!** You've just run your first LLM inference on dedicated hardware!

## Next Steps

### Try Streaming Output

Streaming provides real-time token output, perfect for chat applications:

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

print("Streaming: ", end="", flush=True)
for token in model.generate_stream("Write a short poem about AI:"):
    print(token, end="", flush=True)
print()
```

### Build a Chat Application

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
]

print("Chat with the AI (type 'quit' to exit)")
print("-" * 40)

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    response = model.chat(messages)
    messages.append({"role": "assistant", "content": response.text})
    
    print(f"AI: {response.text}")
```

### Customize Generation

Control the output with `GenerationConfig`:

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Creative generation
creative_config = GenerationConfig(
    temperature=1.2,
    top_p=0.95,
    max_tokens=200
)

# Deterministic generation (greedy)
exact_config = GenerationConfig(
    temperature=0,
    max_tokens=100
)

creative_result = model.generate("Once upon a time", creative_config)
exact_result = model.generate("2 + 2 =", exact_config)

print(f"Creative: {creative_result.text}")
print(f"Exact: {exact_result.text}")
```

## Understanding Your Device

### Device Information

Get detailed information about your SuperInstance device:

```python
from superinstance import Device

device = Device()
info = device.info()

print(f"Device Type: {info.device_type.value}")
print(f"Serial Number: {info.serial_number}")
print(f"Firmware Version: {info.firmware_version}")
print(f"Model: {info.cartridge_model}")
print(f"Temperature: {info.temperature_celsius}°C")
print(f"Power: {info.power_watts}W")
print(f"USB Speed: {info.usb_speed}")
```

### Device Types

| Device Type | Description | Features |
|-------------|-------------|----------|
| `NANO` | USB4 stick | Entry-level, single model |
| `STANDARD` | Standard edition | Faster inference, LPDDR5 |
| `PRO` | Professional | Custom models, advanced APIs |
| `MAKER` | Maker Edition | GPIO header, sensor integration |

### Context Management

Always use context managers for automatic cleanup:

```python
from superinstance import Device

# Recommended: Using context manager
with Device() as device:
    model = device.load_cartridge()
    print(model.generate("Hello").text)
# Device automatically closed

# Manual cleanup (also valid)
device = Device()
try:
    model = device.load_cartridge()
    print(model.generate("Hello").text)
finally:
    device.close()
```

## Performance Tips

### 1. Reuse Device and Model Instances

Creating new device connections has overhead. Reuse instances:

```python
# Good: Reuse instances
device = Device()
model = device.load_cartridge()

for prompt in prompts:
    response = model.generate(prompt)
    process(response)

# Avoid: Creating new instances in a loop
for prompt in prompts:
    device = Device()  # Slow!
    model = device.load_cartridge()
    response = model.generate(prompt)
```

### 2. Use Streaming for Long Outputs

Streaming provides better user experience and allows early termination:

```python
for token in model.generate_stream(long_prompt):
    print(token, end="", flush=True)
    if should_stop():
        break  # Can stop early
```

### 3. Set Appropriate max_tokens

Limit output length to prevent unnecessary generation:

```python
from superinstance import GenerationConfig

# Short answers
short_config = GenerationConfig(max_tokens=50)

# Longer content
long_config = GenerationConfig(max_tokens=1000)
```

### 4. Clear Context Between Unrelated Conversations

```python
# After a conversation ends
model.clear_context()

# Or set a new system prompt
model.set_system_prompt("You are a helpful coding assistant.")
```

## Troubleshooting

### Device Not Found

```python
DeviceNotFoundError: No SuperInstance device detected
```

**Solutions:**
1. Ensure device is plugged into USB 3.0+ port (not USB 2.0)
2. Wait for LED to turn solid green
3. Try a different USB port
4. On Linux, you may need udev rules (see [installation guide](installation.md))

### Device Busy

```python
DeviceBusyError: Device is in use by another process
```

**Solutions:**
1. Close any other applications using the device
2. Kill any orphaned Python processes
3. Unplug and reconnect the device

### Context Length Exceeded

```python
ContextLengthExceededError: Prompt exceeds maximum context length (2048 tokens)
```

**Solutions:**
1. Reduce your prompt length
2. Clear context: `model.clear_context()`
3. Use `model.count_tokens()` to check prompt size

### Slow Performance

If generation is slower than expected:

1. **Check USB speed**:
```python
info = device.info()
print(f"USB Speed: {info.usb_speed}")  # Should be usb3.0, usb3.1, usb3.2, or usb4
```

2. **Monitor device health**:
```python
info = device.info()
if info.temperature_celsius > 70:
    print("Warning: Device is throttling due to heat")
```

3. **Use appropriate power settings**:
   - USB 3.0 provides up to 4.5W (sufficient for all models)
   - Avoid USB hubs without external power

## What's Next?

- **[Installation Guide](installation.md)**: Detailed setup instructions
- **[API Reference](api-reference.md)**: Complete SDK documentation
- **[Examples Gallery](examples.md)**: Sample projects and code
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Getting Help

- **Discord**: [discord.gg/superinstance](https://discord.gg/superinstance)
- **GitHub Discussions**: [github.com/superinstance-ai/superinstance-sdk/discussions](https://github.com/superinstance-ai/superinstance-sdk/discussions)
- **Email**: [support@superinstance.ai](mailto:support@superinstance.ai)

---

Happy coding! 🚀
