# SuperInstance SDK

**Hardware for Intelligence** — A simple, powerful interface for running large language model (LLM) inference on SuperInstance mask-locked inference hardware.

## Features

- **Zero-setup**: Auto-detect and auto-connect to devices with no configuration required
- **Streaming-first**: All generation APIs support token streaming for real-time applications
- **Debuggable**: Built-in profiling, inspection, and error handling at every layer
- **Multi-language**: Python (P0), C/C++ (P0), Rust (P1), JavaScript (P1) bindings
- **Open**: Apache 2.0 licensed with open cartridge format specification

## Installation

```bash
pip install superinstance-sdk
```

### Requirements

- Python 3.8 or later
- Linux, macOS, or Windows 10/11
- USB 3.0+ port for hardware connection

### Verify Installation

```python
import superinstance
print(superinstance.__version__)  # Should print: 0.1.0
```

## Quick Start

### Basic Inference

```python
from superinstance import Device

# Zero-setup: auto-detect and connect
device = Device()
model = device.load_cartridge()

# Generate text
response = model.generate("Hello, I am")
print(response.text)
```

### Streaming Output

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

# Stream tokens in real-time
for token in model.generate_stream("Write a short story about a robot:"):
    print(token, end="", flush=True)
```

### Chat Application

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"},
]

response = model.chat(messages)
print(response.text)
```

### Generation Configuration

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Deterministic generation (greedy decoding)
config = GenerationConfig(temperature=0, max_tokens=100)
result = model.generate("2+2=", config)
print(result.text)  # Always consistent output

# Creative generation
config = GenerationConfig(
    temperature=1.2,
    top_p=0.95,
    max_tokens=500
)
result = model.generate("Once upon a time", config)
```

## Simulation Mode

For development without hardware, use simulation mode:

```bash
# Enable simulation mode via environment variable
export SUPERINSTANCE_SIMULATE=1

python your_script.py
```

Or in code:

```python
import os
os.environ["SUPERINSTANCE_SIMULATE"] = "1"

from superinstance import Device
device = Device()  # Will use simulation
```

## Device Management

### List Available Devices

```python
from superinstance import Device

devices = Device.list_devices()
print(f"Found {len(devices)} device(s)")
for path in devices:
    print(f"  - {path}")
```

### Device Information

```python
from superinstance import Device

with Device() as device:
    info = device.info()
    print(f"Device Type: {info.device_type.value}")
    print(f"Firmware: {info.firmware_version}")
    print(f"Cartridge: {info.cartridge_model}")
    print(f"Temperature: {info.temperature_celsius}°C")
    print(f"Power: {info.power_watts}W")
```

### Multi-Device Configuration

```python
from superinstance import Device

# Connect to specific device by index
device = Device(device_index=0)

# Connect to specific device by path
device = Device("/dev/superinstance0")
```

## API Reference

### Device Class

```python
class Device:
    def __init__(
        self,
        device_path: Optional[str] = None,
        device_index: Optional[int] = None,
        timeout_ms: int = 5000
    ): ...

    @staticmethod
    def list_devices() -> List[str]: ...

    def info(self) -> DeviceInfo: ...
    def load_cartridge(self) -> Model: ...
    def load_model(self, path: str) -> Model: ...  # Pro/Maker only
    def reset(self) -> None: ...
    def close(self) -> None: ...
```

### Model Class

```python
class Model:
    @property
    def name(self) -> str: ...
    @property
    def context_length(self) -> int: ...

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult: ...

    def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Iterator[str]: ...

    def chat(
        self,
        messages: List[dict],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult: ...

    def tokenize(self, text: str) -> List[int]: ...
    def detokenize(self, tokens: List[int]) -> str: ...
    def count_tokens(self, text: str) -> int: ...
```

### GenerationConfig

```python
@dataclass
class GenerationConfig:
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    stop_sequences: Optional[List[str]] = None
    seed: Optional[int] = None
    repetition_penalty: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
```

## Examples

See the `examples/` directory for more examples:

- `hello_world.py` - Basic usage examples
- `chat_bot.py` - Interactive chat application
- `streaming.py` - Real-time streaming output
- `profiling.py` - Performance profiling

## Error Handling

```python
from superinstance import (
    Device,
    DeviceNotFoundError,
    NoCartridgeError,
    ContextLengthExceededError,
)

try:
    device = Device()
    model = device.load_cartridge()
    result = model.generate("Hello")
except DeviceNotFoundError:
    print("No SuperInstance device found")
except NoCartridgeError:
    print("No cartridge inserted")
except ContextLengthExceededError as e:
    print(f"Prompt too long: {e.tokens} > {e.max_tokens}")
```

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Links

- **Documentation**: https://docs.superinstance.ai
- **GitHub**: https://github.com/superinstance-ai/superinstance-sdk
- **Issues**: https://github.com/superinstance-ai/superinstance-sdk/issues
- **Discord**: https://discord.gg/superinstance

## Support

- **Documentation**: https://docs.superinstance.ai
- **Community**: Join our [Discord](https://discord.gg/superinstance)
- **Issues**: Open a [GitHub issue](https://github.com/superinstance-ai/superinstance-sdk/issues)
