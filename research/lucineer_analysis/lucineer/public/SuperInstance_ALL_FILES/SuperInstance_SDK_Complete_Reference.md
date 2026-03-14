# SuperInstance.AI SDK Complete Reference

## Version 1.0 | March 2026 | Apache 2.0 License

**SuperInstance.AI** — Hardware for Intelligence

---

# Table of Contents

1. [Getting Started](#1-getting-started)
2. [Device API Reference](#2-device-api-reference)
3. [Model API Reference](#3-model-api-reference)
4. [Profiling API Reference](#4-profiling-api-reference)
5. [Debug API Reference](#5-debug-api-reference)
6. [Model Module Format](#6-model-module-format)
7. [Compiler Tools Reference](#7-compiler-tools-reference)
8. [Error Handling](#8-error-handling)
9. [Language Bindings](#9-language-bindings)
10. [Examples Gallery](#10-examples-gallery)

---

# 1. Getting Started

## 1.1 Overview

The SuperInstance SDK provides a simple, powerful interface for running large language model (LLM) inference on SuperInstance mask-locked inference hardware. This reference documents the complete public API across all supported languages.

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Zero-setup** | Auto-detect and auto-connect to devices with no configuration required |
| **Streaming-first** | All generation APIs support token streaming for real-time applications |
| **Debuggable** | Built-in profiling, inspection, and error handling at every layer |
| **Multi-language** | Python (P0), C/C++ (P0), Rust (P1), JavaScript (P1) bindings |
| **Open** | Apache 2.0 licensed with open cartridge format specification |

## 1.2 Installation

### Python

```bash
pip install superinstance-sdk
```

**Requirements:**
- Python 3.8 or later
- Linux, macOS, or Windows 10/11
- USB 3.0+ port for hardware connection

**Verify Installation:**

```python
import superinstance
print(superinstance.__version__)  # Should print: 1.0.0
```

### C/C++

```bash
# Linux (Debian/Ubuntu)
sudo apt-get install libsuperinstance-dev

# Linux (RHEL/CentOS)
sudo yum install superinstance-devel

# macOS (Homebrew)
brew install superinstance

# Windows (vcpkg)
vcpkg install superinstance
```

**Include in your project:**

```c
#include <superinstance/superinstance.h>
```

**Link against the library:**

```bash
gcc -lsuperinstance my_app.c -o my_app
```

### From Source

```bash
git clone https://github.com/superinstance-ai/superinstance-sdk.git
cd superinstance-sdk
mkdir build && cd build
cmake ..
make
sudo make install
```

## 1.3 Quick Start Examples

### Basic Inference

```python
from superinstance import Device, Model

# Zero-setup: auto-detect and connect
device = Device()  # Finds first available device
model = device.load_cartridge()  # Use inserted model module

# Generate text
response = model.generate("Hello, I am")
print(response.text)
# Output: "Hello, I am a language model running on dedicated hardware..."
```

### Streaming Output

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Stream tokens in real-time
for token in model.generate_stream("Write a short story about a robot:"):
    print(token, end="", flush=True)
```

### Chat Application

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"},
]

response = model.chat(messages)
print(response.text)

# Continue conversation
messages.append({"role": "assistant", "content": response.text})
messages.append({"role": "user", "content": "Can you give me an example?"})

response = model.chat(messages)
print(response.text)
```

## 1.4 Device Detection and Connection

### List Available Devices

```python
from superinstance import Device

# List all connected SuperInstance devices
devices = Device.list_devices()
print(f"Found {len(devices)} device(s)")
for path in devices:
    print(f"  - {path}")
# Output:
# Found 2 device(s)
#   - /dev/superinstance0
#   - /dev/superinstance1
```

### Connect to Specific Device

```python
from superinstance import Device

# Auto-detect (connects to first available)
device = Device()

# Connect to specific device by path
device = Device("/dev/superinstance1")

# Connect to specific device by index
device = Device(device_index=0)

# Context manager for automatic cleanup
with Device() as device:
    model = device.load_cartridge()
    print(model.generate("Hello").text)
# Device automatically closed when exiting context
```

### Device Information

```python
from superinstance import Device

device = Device()
info = device.info()

print(f"Device Type: {info.device_type}")
print(f"Firmware: {info.firmware_version}")
print(f"Cartridge: {info.cartridge_model}")
print(f"Temperature: {info.temperature_celsius}°C")
print(f"Power: {info.power_watts}W")
```

---

# 2. Device API Reference

## 2.1 Device Class

The `Device` class represents a physical SuperInstance hardware device. It handles device detection, connection management, and provides access to loaded models.

### Class Definition

```python
class Device:
    """
    Represents a SuperInstance inference device.
    
    The Device class is the main entry point for interacting with
    SuperInstance hardware. It provides methods for device detection,
    connection management, and model loading.
    
    Example:
        device = Device()
        model = device.load_cartridge()
        result = model.generate("Hello")
    """
    
    @staticmethod
    def list_devices() -> List[str]:
        """
        List available device paths.
        
        Returns:
            List of device path strings (e.g., ['/dev/superinstance0'])
            
        Example:
            devices = Device.list_devices()
            if not devices:
                print("No SuperInstance devices found")
        """
        pass
    
    def __init__(
        self,
        device_path: Optional[str] = None,
        device_index: Optional[int] = None,
        timeout_ms: int = 5000
    ):
        """
        Connect to a SuperInstance device.
        
        Args:
            device_path: Specific device path to connect to.
                        If None, auto-detects first available device.
            device_index: Index of device to connect to (0-based).
                         If both path and index are None, auto-detects.
            timeout_ms: Connection timeout in milliseconds.
                       Default: 5000ms
        
        Raises:
            DeviceNotFoundError: No SuperInstance device detected
            DeviceBusyError: Device is in use by another process
            DeviceConnectionError: Failed to establish connection
        
        Example:
            # Auto-detect
            device = Device()
            
            # Specific path
            device = Device("/dev/superinstance0")
            
            # By index
            device = Device(device_index=1)
        """
        pass
    
    def info(self) -> DeviceInfo:
        """
        Get device information.
        
        Returns:
            DeviceInfo object containing device metadata.
            
        Example:
            info = device.info()
            print(f"Temperature: {info.temperature_celsius}°C")
        """
        pass
    
    def load_cartridge(self) -> Model:
        """
        Load model from inserted cartridge.
        
        The device must have a cartridge inserted. The model is loaded
        from the cartridge's mask-locked weights and onboard memory.
        
        Returns:
            Model object ready for inference.
            
        Raises:
            NoCartridgeError: No cartridge inserted
            CartridgeReadError: Failed to read cartridge data
            IncompatibleModelError: Cartridge requires newer firmware
            
        Example:
            model = device.load_cartridge()
            print(f"Loaded model: {model.name}")
        """
        pass
    
    def load_model(self, path: str) -> Model:
        """
        Load model from file path.
        
        This method is only available on Pro and Maker Edition devices.
        It allows loading custom model modules from storage.
        
        Args:
            path: Path to model module file (.simod)
            
        Returns:
            Model object ready for inference.
            
        Raises:
            FeatureNotSupportedError: Device doesn't support custom models
            ModelLoadError: Failed to load model file
            IncompatibleModelError: Model incompatible with device
            
        Availability:
            Pro Edition, Maker Edition only
            
        Example:
            model = device.load_model("/path/to/custom-model.simod")
        """
        pass
    
    def reset(self) -> None:
        """
        Reset device to initial state.
        
        Clears all cached data and resets hardware state. The device
        remains connected after reset.
        
        Raises:
            DeviceResetError: Reset failed
            
        Example:
            device.reset()
            model = device.load_cartridge()  # Fresh load
        """
        pass
    
    def firmware_update(self, path: str) -> FirmwareUpdateResult:
        """
        Update device firmware.
        
        Args:
            path: Path to firmware file (.sifw)
            
        Returns:
            FirmwareUpdateResult with status and version info.
            
        Raises:
            FirmwareUpdateError: Update failed
            FirmwareVersionError: Firmware incompatible with device
            
        Warning:
            Do not power off device during firmware update.
            
        Example:
            result = device.firmware_update("/path/to/firmware.sifw")
            print(f"Updated to version {result.new_version}")
        """
        pass
    
    def close(self) -> None:
        """
        Release device resources.
        
        Should be called when done using the device. Using the device
        after close() will raise DeviceClosedError.
        
        Example:
            device = Device()
            # ... use device ...
            device.close()
        """
        pass
    
    def __enter__(self) -> 'Device':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - automatically closes device."""
        self.close()
```

## 2.2 DeviceInfo Data Structure

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DeviceType(Enum):
    """SuperInstance device types."""
    NANO = "nano"           # Consumer USB4 stick
    STANDARD = "standard"   # Standard edition with LPDDR5
    PRO = "pro"             # Professional with custom model support
    MAKER_EDITION = "maker" # Maker edition with GPIO header

@dataclass
class DeviceInfo:
    """
    Device information structure.
    
    Contains metadata about the connected SuperInstance device,
    including hardware status and cartridge information.
    """
    
    device_type: DeviceType
    """Device variant: NANO, STANDARD, PRO, or MAKER_EDITION"""
    
    firmware_version: str
    """Firmware version string (e.g., '1.2.3')"""
    
    serial_number: str
    """Unique device serial number"""
    
    cartridge_inserted: bool
    """True if a model module/cartridge is inserted"""
    
    cartridge_model: Optional[str]
    """Name of inserted model, or None if no cartridge"""
    
    cartridge_version: Optional[str]
    """Version of inserted cartridge, or None"""
    
    temperature_celsius: float
    """Current chip temperature in Celsius"""
    
    power_watts: float
    """Current power consumption in Watts"""
    
    uptime_seconds: int
    """Time since device was powered on, in seconds"""
    
    total_inferences: int
    """Total number of inferences since power-on"""
    
    total_tokens_generated: int
    """Total tokens generated since power-on"""
    
    usb_speed: str
    """USB connection speed: 'usb3.0', 'usb3.1', 'usb3.2', 'usb4'"""
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        pass
    
    def __str__(self) -> str:
        """Human-readable device summary."""
        pass
```

### DeviceInfo Example Output

```python
info = device.info()
print(info)
# Output:
# ┌─────────────────────────────────────────┐
# │ SuperInstance PRO                       │
# │ Serial: SI-PRO-2026-001234              │
# │ Firmware: 1.2.3                         │
# │ USB: usb4 (40 Gbps)                     │
# ├─────────────────────────────────────────┤
# │ Cartridge: bitnet-2b-chat v1.0.0        │
# │ Temperature: 42.3°C                     │
# │ Power: 2.1W                             │
# │ Uptime: 3h 27m                          │
# │ Inferences: 1,247                       │
# │ Tokens: 312,450                         │
# └─────────────────────────────────────────┘
```

## 2.3 Device Methods - Detailed Examples

### Device Detection with Fallback

```python
from superinstance import Device, DeviceNotFoundError
import time

def connect_with_retry(max_retries: int = 3, retry_delay: float = 1.0) -> Device:
    """Connect to device with automatic retry."""
    for attempt in range(max_retries):
        try:
            device = Device()
            print(f"Connected to {device.info().device_type.value}")
            return device
        except DeviceNotFoundError:
            if attempt < max_retries - 1:
                print(f"Device not found, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise
    
    raise DeviceNotFoundError("No device found after retries")

# Usage
device = connect_with_retry()
```

### Multi-Device Configuration

```python
from superinstance import Device

# List all devices
devices = Device.list_devices()
print(f"Found {len(devices)} devices")

# Connect to multiple devices
connected_devices = []
for i, path in enumerate(devices):
    device = Device(path)
    info = device.info()
    print(f"Device {i}: {info.device_type.value} - {info.cartridge_model}")
    connected_devices.append(device)

# Use devices for parallel inference
# (See Swarm API in Section 4)
```

### Device Health Monitoring

```python
from superinstance import Device
import time

def monitor_device_health(device: Device, interval: float = 1.0):
    """Monitor device temperature and power."""
    while True:
        info = device.info()
        
        # Check for thermal throttling
        if info.temperature_celsius > 70:
            print(f"⚠️  Warning: High temperature ({info.temperature_celsius}°C)")
        elif info.temperature_celsius > 80:
            print(f"🔥 Critical: Temperature exceeds safe limit!")
            break
        
        # Check power consumption
        if info.power_watts > 3.5:
            print(f"⚠️  Warning: High power draw ({info.power_watts}W)")
        
        print(f"Temp: {info.temperature_celsius}°C | Power: {info.power_watts}W")
        time.sleep(interval)

# Usage
device = Device()
# monitor_device_health(device)  # Run in separate thread
```

---

# 3. Model API Reference

## 3.1 Model Class

The `Model` class represents a loaded language model and provides methods for text generation, tokenization, and configuration.

### Class Definition

```python
from typing import Iterator, List, Optional, Callable
from dataclasses import dataclass

class Model:
    """
    Loaded language model interface.
    
    Provides methods for text generation, tokenization, and
    model introspection. Models are loaded from cartridges
    or model files via the Device class.
    """
    
    @property
    def name(self) -> str:
        """Model name from cartridge metadata."""
        pass
    
    @property
    def version(self) -> str:
        """Model version string."""
        pass
    
    @property
    def context_length(self) -> int:
        """Maximum context length in tokens."""
        pass
    
    @property
    def vocab_size(self) -> int:
        """Vocabulary size."""
        pass
    
    @property
    def parameters(self) -> int:
        """Total parameter count."""
        pass
    
    @property
    def quantization(self) -> str:
        """Quantization scheme: 'ternary', 'c4_complex', 'int4'."""
        pass
    
    # === Generation Methods ===
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        Generate complete response for prompt.
        
        Args:
            prompt: Input text prompt
            config: Generation parameters (optional)
            
        Returns:
            GenerationResult with output text and metadata
            
        Raises:
            ContextLengthExceededError: Prompt exceeds context length
            GenerationError: Generation failed
            
        Example:
            result = model.generate("What is AI?")
            print(result.text)
            print(f"Generated in {result.total_time_ms:.1f}ms")
        """
        pass
    
    def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Iterator[str]:
        """
        Stream tokens as they are generated.
        
        This method provides real-time output, yielding each token
        as it is produced by the model. Ideal for chat applications
        and interactive interfaces.
        
        Args:
            prompt: Input text prompt
            config: Generation parameters (optional)
            callback: Optional callback called with each token
            
        Yields:
            Individual tokens as strings
            
        Raises:
            ContextLengthExceededError: Prompt exceeds context length
            GenerationError: Generation failed
            
        Example:
            for token in model.generate_stream("Tell me a story:"):
                print(token, end="", flush=True)
            
            # With callback
            def on_token(token):
                websocket.send(token)
            
            list(model.generate_stream("Hello", callback=on_token))
        """
        pass
    
    def chat(
        self,
        messages: List[dict],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        Chat-style generation with message history.
        
        Supports multi-turn conversations with role-based messages.
        Messages should follow the OpenAI chat format:
        
        [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            config: Generation parameters (optional)
            
        Returns:
            GenerationResult with assistant's response
            
        Raises:
            ContextLengthExceededError: Messages exceed context length
            InvalidMessageFormatError: Message format invalid
            GenerationError: Generation failed
            
        Example:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is 2+2?"},
            ]
            response = model.chat(messages)
            print(response.text)  # "2+2 equals 4."
        """
        pass
    
    def chat_stream(
        self,
        messages: List[dict],
        config: Optional[GenerationConfig] = None
    ) -> Iterator[str]:
        """
        Streaming chat generation.
        
        Combines chat formatting with streaming output.
        
        Args:
            messages: List of message dictionaries
            config: Generation parameters (optional)
            
        Yields:
            Individual tokens as strings
        """
        pass
    
    # === Tokenization Methods ===
    
    def tokenize(self, text: str) -> List[int]:
        """
        Convert text to token IDs.
        
        Args:
            text: Input text string
            
        Returns:
            List of integer token IDs
            
        Example:
            tokens = model.tokenize("Hello, world!")
            print(tokens)  # [15496, 11, 995, 0]
        """
        pass
    
    def detokenize(self, tokens: List[int]) -> str:
        """
        Convert token IDs to text.
        
        Args:
            tokens: List of integer token IDs
            
        Returns:
            Decoded text string
            
        Example:
            text = model.detokenize([15496, 11, 995, 0])
            print(text)  # "Hello, world!"
        """
        pass
    
    def count_tokens(self, text: str) -> int:
        """
        Count number of tokens in text.
        
        Args:
            text: Input text string
            
        Returns:
            Number of tokens
            
        Example:
            count = model.count_tokens("Hello, world!")
            print(count)  # 4
        """
        pass
    
    # === Context Management ===
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set persistent system prompt.
        
        The system prompt is prepended to all subsequent generations
        until cleared or changed.
        
        Args:
            prompt: System prompt text
        """
        pass
    
    def clear_context(self) -> None:
        """Clear all context and KV cache."""
        pass
    
    def get_context_usage(self) -> ContextUsage:
        """
        Get current context usage.
        
        Returns:
            ContextUsage with token counts and utilization
        """
        pass
    
    # === Advanced Methods ===
    
    def get_logits(
        self,
        prompt: str,
        position: Optional[int] = None
    ) -> 'np.ndarray':
        """
        Get raw logits for a prompt.
        
        This is an advanced method for custom sampling strategies.
        
        Args:
            prompt: Input text
            position: Position in sequence (default: last token)
            
        Returns:
            Numpy array of shape [vocab_size] containing log probabilities
            
        Availability:
            Pro Edition, Maker Edition only
            
        Example:
            logits = model.get_logits("The capital of France is")
            top_5 = np.argsort(logits)[-5:][::-1]
            for token_id in top_5:
                print(model.detokenize([token_id]), logits[token_id])
        """
        pass
    
    def forward(
        self,
        tokens: List[int],
        return_hidden_states: bool = False
    ) -> ForwardResult:
        """
        Run forward pass on token sequence.
        
        This is an advanced method for introspection and research.
        
        Args:
            tokens: List of token IDs
            return_hidden_states: Include hidden states in result
            
        Returns:
            ForwardResult with logits and optional hidden states
            
        Availability:
            Pro Edition, Maker Edition only
        """
        pass
```

## 3.2 GenerationConfig Parameters

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GenerationConfig:
    """
    Generation parameters for text generation.
    
    Controls sampling behavior, stopping conditions, and
    output formatting for model.generate() and related methods.
    """
    
    max_tokens: int = 256
    """
    Maximum number of tokens to generate.
    
    Range: 1 - 4096 (model-dependent)
    Default: 256
    """
    
    temperature: float = 0.7
    """
    Sampling temperature.
    
    Higher values (0.8-1.5) produce more creative output.
    Lower values (0.1-0.5) produce more deterministic output.
    Set to 0 for greedy decoding (always pick most likely token).
    
    Range: 0.0 - 2.0
    Default: 0.7
    """
    
    top_p: float = 0.9
    """
    Nucleus sampling threshold.
    
    Only sample from tokens comprising the top_p probability mass.
    Lower values (0.5-0.8) reduce randomness while maintaining diversity.
    
    Range: 0.0 - 1.0
    Default: 0.9
    """
    
    top_k: int = 40
    """
    Top-k sampling parameter.
    
    Only sample from the top_k most likely tokens.
    Set to 0 to disable top-k filtering.
    
    Range: 0 - 1000
    Default: 40
    """
    
    stop_sequences: Optional[List[str]] = None
    """
    Stop generation on these sequences.
    
    Generation stops when any of these strings appear in output.
    The stop sequence is NOT included in the output.
    
    Example: ["\\n\\n", "Human:", "Assistant:"]
    Default: None
    """
    
    stop_tokens: Optional[List[int]] = None
    """
    Stop generation on these token IDs.
    
    Generation stops when any of these token IDs are produced.
    
    Default: None
    """
    
    seed: Optional[int] = None
    """
    Random seed for reproducibility.
    
    Set for deterministic outputs with the same prompt and config.
    
    Default: None (random)
    """
    
    repetition_penalty: float = 1.0
    """
    Repetition penalty factor.
    
    Values > 1.0 discourage repetition. Values < 1.0 allow more repetition.
    
    Range: 0.0 - 2.0
    Default: 1.0 (disabled)
    """
    
    frequency_penalty: float = 0.0
    """
    Frequency-based penalty.
    
    Penalizes tokens based on their frequency in the generated text.
    
    Range: 0.0 - 2.0
    Default: 0.0 (disabled)
    """
    
    presence_penalty: float = 0.0
    """
    Presence-based penalty.
    
    Penalizes tokens that have appeared in the generated text.
    
    Range: 0.0 - 2.0
    Default: 0.0 (disabled)
    """
    
    length_penalty: float = 1.0
    """
    Length-based penalty for beam search.
    
    Values > 1.0 favor longer outputs, < 1.0 favors shorter.
    
    Default: 1.0 (neutral)
    """
    
    echo: bool = False
    """
    Echo the prompt in the output.
    
    If True, the response includes the input prompt.
    
    Default: False
    """
    
    logprobs: Optional[int] = None
    """
    Return log probabilities for top N tokens.
    
    If set, GenerationResult.logprobs will contain log probabilities.
    
    Range: 0 - 20
    Default: None (disabled)
    """
```

### GenerationConfig Examples

```python
from superinstance import Device, GenerationConfig

device = Device()
model = device.load_cartridge()

# Deterministic generation (greedy decoding)
config = GenerationConfig(temperature=0, max_tokens=100)
result = model.generate("2+2=", config)
print(result.text)  # Always "4"

# Creative generation
config = GenerationConfig(
    temperature=1.2,
    top_p=0.95,
    max_tokens=500
)
result = model.generate("Once upon a time", config)

# Constrained generation with stop sequences
config = GenerationConfig(
    temperature=0.3,
    stop_sequences=["\n\n", "Q:"],
    max_tokens=200
)
result = model.generate("Q: What is Python?\nA:", config)

# Reproducible generation
config = GenerationConfig(seed=42, temperature=0.8)
result1 = model.generate("Hello", config)
result2 = model.generate("Hello", config)
assert result1.text == result2.text  # Same seed = same output

# Code generation (low temperature)
code_config = GenerationConfig(
    temperature=0.2,
    top_p=0.95,
    stop_sequences=["```", "\n\n\n"],
    max_tokens=512
)
```

## 3.3 GenerationResult Data Structure

```python
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class GenerationResult:
    """
    Result of text generation.
    
    Contains the generated text and performance metrics.
    """
    
    text: str
    """Generated text (or text with prompt if echo=True)"""
    
    tokens: List[int]
    """List of generated token IDs"""
    
    prompt_tokens: int
    """Number of tokens in the input prompt"""
    
    generated_tokens: int
    """Number of tokens generated"""
    
    tokens_per_second: float
    """Generation speed in tokens per second"""
    
    first_token_latency_ms: float
    """Time to generate first token in milliseconds"""
    
    total_time_ms: float
    """Total generation time in milliseconds"""
    
    finish_reason: str
    """Reason generation stopped: 'length', 'stop', 'eos'"""
    
    logprobs: Optional[List[dict]] = None
    """Log probabilities if logprobs was set in config"""
    
    energy_millijoules: Optional[float] = None
    """Energy consumed during generation (millijoules)"""
    
    model_name: Optional[str] = None
    """Name of model that generated this response"""
    
    def __len__(self) -> int:
        """Number of generated tokens."""
        return self.generated_tokens
    
    def __str__(self) -> str:
        """The generated text."""
        return self.text
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        pass
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        pass
```

## 3.4 Tokenization Examples

```python
from superinstance import Device

device = Device()
model = device.load_cartridge()

# Basic tokenization
text = "Hello, world!"
tokens = model.tokenize(text)
print(f"Text: {text}")
print(f"Tokens: {tokens}")
print(f"Count: {len(tokens)}")

# Detokenization
decoded = model.detokenize(tokens)
print(f"Decoded: {decoded}")

# Count tokens efficiently
long_text = "This is a longer piece of text..."
token_count = model.count_tokens(long_text)
print(f"Token count: {token_count}")

# Token-aware text truncation
def truncate_to_tokens(model, text: str, max_tokens: int) -> str:
    """Truncate text to fit within max_tokens."""
    tokens = model.tokenize(text)
    if len(tokens) <= max_tokens:
        return text
    return model.detokenize(tokens[:max_tokens])

truncated = truncate_to_tokens(model, long_text, 5)
print(f"Truncated: {truncated}")
```

---

# 4. Profiling API Reference

## 4.1 Profiler Class

The `Profiler` class provides detailed performance measurement for inference operations.

### Class Definition

```python
from dataclasses import dataclass
from typing import List, Optional
from contextlib import contextmanager

@dataclass
class LayerProfile:
    """Per-layer profiling data."""
    
    name: str
    """Layer name (e.g., 'attention.0', 'ffn.12')"""
    
    time_ms: float
    """Time spent in this layer (milliseconds)"""
    
    energy_mj: float
    """Energy consumed (millijoules)"""
    
    memory_accesses: int
    """Number of memory accesses"""
    
    cache_hits: int
    """Number of cache hits"""
    
    cache_misses: int
    """Number of cache misses"""
    
    mac_operations: int
    """Number of MAC operations"""
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate as fraction."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 1.0

@dataclass
class ProfileReport:
    """Complete profiling report."""
    
    layers: List[LayerProfile]
    """Per-layer profiling data"""
    
    total_time_ms: float
    """Total inference time"""
    
    total_energy_mj: float
    """Total energy consumed"""
    
    throughput_tok_per_s: float
    """Generation throughput"""
    
    energy_efficiency_tok_per_j: float
    """Tokens generated per joule"""
    
    first_token_ms: float
    """Time to first token"""
    
    prefill_time_ms: float
    """Prompt processing time"""
    
    decode_time_ms: float
    """Token generation time"""
    
    memory_bandwidth_gb_s: float
    """Average memory bandwidth utilization"""
    
    compute_utilization: float
    """Compute array utilization (0.0-1.0)"""
    
    def summary(self) -> str:
        """Return formatted summary string."""
        pass
    
    def to_dataframe(self) -> 'pd.DataFrame':
        """Convert to pandas DataFrame."""
        pass
    
    def save(self, path: str) -> None:
        """Save report to JSON file."""
        pass
    
    @classmethod
    def load(cls, path: str) -> 'ProfileReport':
        """Load report from JSON file."""
        pass


class Profiler:
    """
    Performance profiler for inference operations.
    
    The Profiler captures detailed timing, energy, and resource
    utilization metrics during model inference.
    
    Example:
        with Profiler() as p:
            result = model.generate("Hello")
        
        report = p.report()
        print(f"Tokens/sec: {report.throughput_tok_per_s}")
    """
    
    def __init__(
        self,
        device: Optional[Device] = None,
        enable_layer_profile: bool = True,
        enable_energy: bool = True
    ):
        """
        Initialize profiler.
        
        Args:
            device: Device to profile (auto-detect if None)
            enable_layer_profile: Collect per-layer metrics
            enable_energy: Collect energy measurements
        """
        pass
    
    def start(self) -> None:
        """Begin profiling session."""
        pass
    
    def stop(self) -> ProfileReport:
        """
        End profiling and return report.
        
        Returns:
            ProfileReport with all collected metrics
        """
        pass
    
    @contextmanager
    def profile(self) -> 'Profiler':
        """
        Context manager for profiling.
        
        Yields:
            Profiler instance
            
        Example:
            with Profiler().profile() as p:
                result = model.generate("Hello")
            report = p.last_report
        """
        self.start()
        try:
            yield self
        finally:
            self.last_report = self.stop()
    
    def __enter__(self) -> 'Profiler':
        self.start()
        return self
    
    def __exit__(self, *args) -> None:
        self.last_report = self.stop()
    
    @property
    def last_report(self) -> Optional[ProfileReport]:
        """Most recent profiling report."""
        pass
```

## 4.2 Profiling Examples

### Basic Profiling

```python
from superinstance import Device, Profiler

device = Device()
model = device.load_cartridge()

# Profile a single generation
with Profiler() as p:
    output = model.generate("Hello, I am")

report = p.last_report

print(f"Throughput: {report.throughput_tok_per_s:.1f} tok/s")
print(f"First token: {report.first_token_ms:.1f} ms")
print(f"Energy: {report.total_energy_mj:.1f} mJ")
print(f"Efficiency: {report.energy_efficiency_tok_per_j:.1f} tok/J")
```

### Layer-by-Layer Analysis

```python
from superinstance import Device, Profiler

device = Device()
model = device.load_cartridge()

with Profiler(enable_layer_profile=True) as p:
    output = model.generate("What is machine learning?", max_tokens=100)

report = p.last_report

# Print per-layer timing
print("\nLayer Profile:")
print("-" * 60)
for layer in report.layers:
    print(f"{layer.name:20s} {layer.time_ms:6.2f}ms  {layer.energy_mj:6.2f}mJ  "
          f"Cache: {layer.cache_hit_rate:.1%}")
print("-" * 60)
print(f"{'TOTAL':20s} {report.total_time_ms:6.2f}ms  {report.total_energy_mj:6.2f}mJ")
```

### Batch Performance Comparison

```python
from superinstance import Device, Profiler, GenerationConfig
import statistics

device = Device()
model = device.load_cartridge()

configs = [
    ("Greedy", GenerationConfig(temperature=0)),
    ("Low temp", GenerationConfig(temperature=0.3)),
    ("High temp", GenerationConfig(temperature=1.2)),
]

print("\nPerformance by Configuration:")
print("-" * 70)
print(f"{'Config':12s} {'tok/s':>10s} {'TTFT (ms)':>12s} {'Energy (mJ)':>12s}")
print("-" * 70)

for name, config in configs:
    with Profiler() as p:
        model.generate("Hello", config=config)
    
    report = p.last_report
    print(f"{name:12s} {report.throughput_tok_per_s:10.1f} "
          f"{report.first_token_ms:12.1f} {report.total_energy_mj:12.1f}")
```

### Export to DataFrame

```python
from superinstance import Device, Profiler

device = Device()
model = device.load_cartridge()

with Profiler(enable_layer_profile=True) as p:
    model.generate("Test prompt", max_tokens=50)

report = p.last_report

# Convert to pandas DataFrame
df = report.to_dataframe()
print(df.head())

# Export to CSV
df.to_csv("profile_report.csv", index=False)

# Save full report as JSON
report.save("profile_report.json")
```

---

# 5. Debug API Reference

## 5.1 Inspector Class

The `Inspector` class provides layer-by-layer inspection and debugging capabilities.

### Class Definition

```python
from typing import List, Optional, Tuple
import numpy as np

class Inspector:
    """
    Layer-by-layer inspection and debugging.
    
    The Inspector allows examining intermediate activations,
    attention patterns, and other internal states during
    model inference.
    
    Availability:
        Pro Edition, Maker Edition only
    
    Example:
        inspector = Inspector(device)
        inspector.set_breakpoint(layer=12)
        
        model.generate("Hello")  # Will pause at layer 12
        
        activations = inspector.get_activations(layer=12)
        inspector.step()  # Continue to next layer
    """
    
    def __init__(self, device: Device):
        """
        Initialize inspector for a device.
        
        Args:
            device: Device to inspect
        """
        pass
    
    def set_breakpoint(
        self,
        layer: Optional[int] = None,
        token: Optional[int] = None
    ) -> None:
        """
        Set a breakpoint to pause inference.
        
        Args:
            layer: Pause before this layer (0-indexed)
            token: Pause after generating this token
            
        Example:
            inspector.set_breakpoint(layer=6)  # Pause at layer 6
            inspector.set_breakpoint(token=10)  # Pause after 10th token
        """
        pass
    
    def clear_breakpoint(self) -> None:
        """Clear all breakpoints."""
        pass
    
    def step(self, n: int = 1) -> None:
        """
        Execute n steps when paused.
        
        If paused at layer breakpoint, executes n layers.
        If paused at token breakpoint, generates n tokens.
        
        Args:
            n: Number of steps to execute
        """
        pass
    
    def continue_execution(self) -> None:
        """Resume normal execution (remove pause)."""
        pass
    
    def get_activations(self, layer: int) -> np.ndarray:
        """
        Get activation tensor for a layer.
        
        Args:
            layer: Layer index (0 to num_layers-1)
            
        Returns:
            Activation array of shape [seq_len, hidden_dim]
        """
        pass
    
    def get_attention_weights(
        self,
        layer: int,
        head: Optional[int] = None
    ) -> np.ndarray:
        """
        Get attention weight matrix.
        
        Args:
            layer: Layer index
            head: Attention head index (None for all heads)
            
        Returns:
            Attention weights of shape [heads, seq_len, seq_len]
            or [seq_len, seq_len] if head is specified
        """
        pass
    
    def get_hidden_state(self, layer: int, position: int) -> np.ndarray:
        """
        Get hidden state vector at specific position.
        
        Args:
            layer: Layer index
            position: Token position in sequence
            
        Returns:
            Hidden state vector of shape [hidden_dim]
        """
        pass
    
    def get_logits(self) -> np.ndarray:
        """
        Get output logits for current token.
        
        Returns:
            Logits array of shape [vocab_size]
        """
        pass
    
    def get_layer_output(self, layer: int) -> np.ndarray:
        """
        Get output tensor from a layer.
        
        Args:
            layer: Layer index
            
        Returns:
            Output tensor of shape [seq_len, hidden_dim]
        """
        pass
    
    def inject_activation(
        self,
        layer: int,
        position: int,
        activation: np.ndarray
    ) -> None:
        """
        Inject custom activation value.
        
        This modifies the activation at the specified position
        before it's passed to the next layer.
        
        Args:
            layer: Layer index
            position: Token position
            activation: New activation values
        """
        pass
    
    def get_performance_state(self) -> dict:
        """
        Get current performance counters.
        
        Returns:
            Dictionary with cycle count, cache stats, etc.
        """
        pass
    
    def enable_trace(self, output_path: str) -> None:
        """
        Enable execution tracing.
        
        Records all layer executions to a trace file for
        later analysis.
        
        Args:
            output_path: Path to save trace file
        """
        pass
    
    def disable_trace(self) -> None:
        """Disable execution tracing."""
        pass
```

## 5.2 Debug Examples

### Basic Layer Inspection

```python
from superinstance import Device
from superinstance.debug import Inspector

device = Device()
model = device.load_cartridge()

inspector = Inspector(device)

# Run inference and capture activations
inspector.set_breakpoint(layer=12)  # Pause at layer 12

# Start generation (will pause at breakpoint)
import threading
def generate():
    model.generate("Hello, world!")

thread = threading.Thread(target=generate)
thread.start()

# Inspect at breakpoint
activations = inspector.get_activations(layer=12)
print(f"Activation shape: {activations.shape}")
print(f"Activation stats: mean={activations.mean():.4f}, std={activations.std():.4f}")

# Continue execution
inspector.continue_execution()
thread.join()
```

### Attention Visualization

```python
from superinstance import Device
from superinstance.debug import Inspector
import matplotlib.pyplot as plt

device = Device()
model = device.load_cartridge()

inspector = Inspector(device)

# Generate with attention capture
prompt = "The quick brown fox jumps over the lazy dog"
result = model.generate(prompt, max_tokens=10)

# Get attention weights for first layer
attn = inspector.get_attention_weights(layer=0)

# Visualize attention pattern
plt.figure(figsize=(10, 8))
plt.imshow(attn[0], cmap='viridis')  # First attention head
plt.colorbar()
plt.title("Attention Pattern - Layer 0, Head 0")
plt.xlabel("Key Position")
plt.ylabel("Query Position")
plt.savefig("attention_visualization.png")
```

### Step-by-Step Debugging

```python
from superinstance import Device
from superinstance.debug import Inspector

device = Device()
model = device.load_cartridge()
inspector = Inspector(device)

# Step through generation token by token
inspector.set_breakpoint(token=0)  # Pause after each token

prompt = "Count from 1 to 5:"
tokens = model.tokenize(prompt)

print(f"Prompt: {prompt}")
print(f"Prompt tokens: {tokens}")

# Generate one token at a time
for i in range(10):
    inspector.continue_execution()
    inspector.set_breakpoint(token=i+1)
    
    logits = inspector.get_logits()
    top_token = logits.argmax()
    generated = model.detokenize([top_token])
    
    print(f"Token {i+1}: {generated!r} (id={top_token})")
```

### Performance Debugging

```python
from superinstance import Device
from superinstance.debug import Inspector

device = Device()
model = device.load_cartridge()
inspector = Inspector(device)

# Enable detailed tracing
inspector.enable_trace("inference_trace.json")

# Run inference
result = model.generate("Hello", max_tokens=50)

# Get performance state
state = inspector.get_performance_state()

print("Performance Counters:")
print(f"  Total cycles: {state['cycles']:,}")
print(f"  Cache hits: {state['cache_hits']:,}")
print(f"  Cache misses: {state['cache_misses']:,}")
print(f"  Hit rate: {state['cache_hits'] / (state['cache_hits'] + state['cache_misses']):.1%}")
print(f"  Stall cycles: {state['stall_cycles']:,}")

inspector.disable_trace()
```

---

# 6. Model Module Format

## 6.1 Overview

SuperInstance uses an open model module format that allows the community to create and share models. The specification is Apache 2.0 licensed and documented publicly.

### Module Components

A model module consists of:

```
model-module/
├── module.yaml           # Module manifest
├── weights.bin           # Packed weight data
├── tokenizer.model       # SentencePiece tokenizer
├── tokenizer.json        # HuggingFace-compatible tokenizer
├── config.json           # Model architecture config
├── checksums.sha256      # Weight checksums
└── metadata.json         # Extended metadata
```

## 6.2 Module Manifest (module.yaml)

```yaml
# Module Manifest Specification
apiVersion: superinstance.io/v1
kind: ModelModule
metadata:
  name: bitnet-2b-chat
  version: "1.0.0"
  license: MIT
  author: microsoft
  description: |
    BitNet b1.58 2B parameter chat model with ternary quantization.
    Optimized for conversational AI applications.
  tags:
    - chat
    - assistant
    - english
  homepage: https://huggingface.co/microsoft/bitnet-2b
  documentation: https://docs.superinstance.ai/models/bitnet-2b-chat

spec:
  model:
    architecture: transformer
    variant: bitnet-b158  # Architecture variant
    
    parameters: 2000000000
    precision: ternary     # Values: ternary, c4_complex, int4, int8
    
    context_length: 4096
    vocab_size: 32000
    
    layers: 24
    hidden_dim: 2560
    intermediate_dim: 6912
    attention_heads: 32
    
    # Architecture-specific parameters
    attention:
      type: multi_head
      rotary_embedding: true
      rope_theta: 10000.0
    
    activation: swiglu
    
  tokenizer:
    type: sentencepiece
    vocab_file: tokenizer.model
    model_type: bpe
    byte_fallback: true
    
  weights:
    format: ternary_packed
    # 2-bit ternary packed: 4 weights per byte
    # Encoding: 00=+1, 01=-1, 10=0, 11=reserved
    packing: dense
    file: weights.bin
    size_bytes: 500000000  # ~500MB for 2B ternary weights
    checksum_sha256: "abc123def456..."
    
  generation:
    default_config:
      temperature: 0.7
      top_p: 0.9
      top_k: 40
      max_tokens: 256
      repetition_penalty: 1.0
    
    stop_tokens: [2, 32000, 32001]  # EOS, special tokens
    stop_sequences: ["\n\nHuman:", "\n\nUser:"]
    
  compatibility:
    min_firmware: "1.0.0"
    max_firmware: null  # null = any version
    devices:
      - nano
      - standard  
      - pro
      - maker_edition
    
    # Device-specific constraints
    constraints:
      nano:
        max_context: 2048  # Reduced context on nano
      standard:
        max_context: 4096
      pro:
        max_context: 8192  # Extended with external memory
        
  benchmarks:
    mmlu: 52.3
    hellaswag: 75.1
    arc_challenge: 45.2
    perlexity_wikitext2: 12.4
    
    # Throughput benchmarks
    throughput:
      nano: 80    # tok/s
      standard: 100
      pro: 120
```

## 6.3 Weight Format Specification

### Ternary Weight Encoding

```
TERNARY WEIGHT PACKING (2-bit encoding)

Each weight is encoded in 2 bits:
┌────────┬────────────────┐
│ Bits   │ Weight Value   │
├────────┼────────────────┤
│ 00     │ +1             │
│ 01     │ -1             │
│ 10     │ 0              │
│ 11     │ reserved       │
└────────┴────────────────┘

4 weights packed into 1 byte:
Byte layout: [w3:2bits | w2:2bits | w1:2bits | w0:2bits]

Example:
  Weights: [+1, -1, 0, +1]
  Packed:  0b01001000 = 0x48
```

### C₄ Complex Weight Encoding

```
C₄ COMPLEX WEIGHT PACKING (2-bit encoding)

Weights from the set {+1, -1, +i, -i}:

┌────────┬────────────────┐
│ Bits   │ Weight Value   │
├────────┼────────────────┤
│ 00     │ +1             │
│ 01     │ -1             │
│ 10     │ +i             │
│ 11     │ -i             │
└────────┴────────────────┘

Complex operations:
  - +1: identity (a + bi)
  - -1: negate (-a - bi)
  - +i: rotate +90° (-b + ai)
  - -i: rotate -90° (b - ai)
```

### Weight File Structure

```
WEIGHT FILE BINARY FORMAT

Header (32 bytes):
┌────────────────────────────────────────────────┐
│ Offset │ Size │ Description                    │
├────────┼──────┼────────────────────────────────┤
│ 0      │ 4    │ Magic: 0x53494357 ("SICW")    │
│ 4      │ 4    │ Version: 1                     │
│ 8      │ 4    │ Encoding: 1=ternary, 2=c4     │
│ 12     │ 8    │ Total parameters               │
│ 20     │ 4    │ Layer count                    │
│ 24     │ 4    │ Checksum (CRC32)               │
│ 28     │ 4    │ Reserved                       │
└────────┴──────┴────────────────────────────────┘

Layer Directory (variable):
For each layer:
┌────────────────────────────────────────────────┐
│ Offset │ Size │ Description                    │
├────────┼──────┼────────────────────────────────┤
│ 0      │ 4    │ Layer name length              │
│ 4      │ N    │ Layer name (UTF-8)             │
│ 4+N    │ 4    │ Weight count                   │
│ 8+N    │ 8    │ Data offset from file start    │
│ 16+N   │ 8    │ Data size in bytes             │
└────────┴──────┴────────────────────────────────┘

Weight Data:
Packed binary weight data for each layer
```

## 6.4 Compatibility Requirements

### Firmware Version Compatibility

```python
from superinstance import Device, IncompatibleModelError

device = Device()
info = device.info()

# Check firmware compatibility
min_required = "1.2.0"
current = info.firmware_version

def version_tuple(v):
    return tuple(map(int, v.split('.')))

if version_tuple(current) < version_tuple(min_required):
    raise IncompatibleModelError(
        f"Firmware {current} too old. Required: {min_required}"
    )
```

### Device Type Compatibility

```python
from superinstance import Device, DeviceType

device = Device()
info = device.info()

# Check device supports required features
if info.device_type == DeviceType.NANO:
    max_context = 2048  # Nano has reduced context
else:
    max_context = 4096

# Check if custom models are supported
if info.device_type not in [DeviceType.PRO, DeviceType.MAKER_EDITION]:
    print("Custom model loading not supported on this device")
```

---

# 7. Compiler Tools Reference

## 7.1 Overview

The SuperInstance SDK includes command-line tools for compiling, validating, and writing model modules.

### Available Tools

| Tool | Description |
|------|-------------|
| `sic-compile` | Compile PyTorch/SafeTensors models to module format |
| `sic-validate` | Validate module compatibility and correctness |
| `sic-write` | Write module to flash (Maker Edition) |
| `sic-info` | Display module information |
| `sic-benchmark` | Run inference benchmarks |

## 7.2 sic-compile

### Synopsis

```bash
sic-compile [OPTIONS] <input> --output <output>
```

### Description

Compile a model from PyTorch (.pt, .bin) or SafeTensors format to SuperInstance module format (.simod).

### Options

```
INPUT OPTIONS:
  -i, --input PATH         Input model file or directory
  -f, --format FORMAT      Input format: auto, pytorch, safetensors, onnx
                           Default: auto (detect from extension)

OUTPUT OPTIONS:
  -o, --output PATH        Output module path (.simod)
  --name NAME              Module name (default: from input)
  --version VERSION        Module version (default: 1.0.0)
  --author AUTHOR          Author name

QUANTIZATION OPTIONS:
  -q, --quantization TYPE  Quantization: ternary, c4_complex, int4
                           Default: ternary
  --calibration-data PATH  Calibration dataset for quantization
  --calibration-samples N  Number of calibration samples
                           Default: 512
  --mixed-precision PATH   YAML file specifying per-layer precision

OPTIMIZATION OPTIONS:
  -O, --optimize LEVEL     Optimization level: O0, O1, O2, O3
                           Default: O2
  --fuse-operations        Enable operation fusion
  --prune-zeros            Remove zero weights (default: on for ternary)
  --kv-cache-optimize      Optimize KV cache layout

VALIDATION OPTIONS:
  --validate               Run validation after compile
  --validation-data PATH   Validation dataset
  --perplexity-limit N     Max perplexity increase allowed
                           Default: 0.1 (10%)

DEBUG OPTIONS:
  -v, --verbose            Verbose output
  --debug                  Debug mode (keep intermediate files)
  --keep-temp              Keep temporary files

HELP OPTIONS:
  -h, --help               Show help message
  --version                Show version
```

### Examples

```bash
# Basic compilation
sic-compile model.pt --output model.simod

# With options
sic-compile ./llama-2b \
  --output bitnet-2b-chat.simod \
  --name "bitnet-2b-chat" \
  --version "1.0.0" \
  --author "microsoft" \
  --quantization ternary \
  --optimize O2

# With calibration
sic-compile model.pt \
  --output model.simod \
  --quantization int4 \
  --calibration-data ./calibration_data/ \
  --calibration-samples 1024

# Mixed precision
sic-compile model.pt \
  --output model.simod \
  --mixed-precision precision_config.yaml
```

### Mixed Precision Configuration

```yaml
# precision_config.yaml
default: ternary

layers:
  # Keep attention layers at higher precision
  "*.attention.*": int4
  
  # FFN can use ternary
  "*.ffn.*": ternary
  
  # Embeddings at int4
  "embed_tokens": int4
  "lm_head": int4
```

## 7.3 sic-validate

### Synopsis

```bash
sic-validate [OPTIONS] <module>
```

### Description

Validate a compiled module for correctness and compatibility.

### Options

```
MODULE OPTIONS:
  module                   Module path to validate

COMPATIBILITY OPTIONS:
  --device PATH            Check compatibility with specific device
  --min-firmware VERSION   Minimum required firmware version
  --max-context N          Maximum context length needed

VALIDATION OPTIONS:
  --checksums              Verify weight checksums
  --structure              Verify module structure
  --tokenizer              Verify tokenizer integrity
  --inference              Run inference test
  --perplexity             Measure perplexity degradation
  --reference PATH         Reference model for comparison

OUTPUT OPTIONS:
  --format FORMAT          Output format: text, json, yaml
                           Default: text
  --report PATH            Save detailed report to file

HELP OPTIONS:
  -h, --help               Show help message
```

### Examples

```bash
# Basic validation
sic-validate model.simod

# Full validation with device check
sic-validate model.simod \
  --device /dev/superinstance0 \
  --checksums \
  --structure \
  --tokenizer \
  --inference

# Compare with reference
sic-validate model.simod \
  --reference ./original_model.pt \
  --perplexity

# JSON output
sic-validate model.simod --format json
```

## 7.4 sic-write

### Synopsis

```bash
sic-write [OPTIONS] <module> --device <device>
```

### Description

Write a compiled module to device flash storage. Only available on Maker Edition devices.

### Options

```
MODULE OPTIONS:
  module                   Module path to write

DEVICE OPTIONS:
  -d, --device PATH        Device path (required)
  --force                  Skip compatibility check
  --backup                 Backup current module first

VERIFICATION OPTIONS:
  --verify                 Verify after write
  --benchmark              Run benchmark after write

HELP OPTIONS:
  -h, --help               Show help message
```

### Examples

```bash
# Write module to device
sic-write model.simod --device /dev/superinstance0

# With verification
sic-write model.simod \
  --device /dev/superinstance0 \
  --verify \
  --benchmark

# Backup existing module
sic-write model.simod \
  --device /dev/superinstance0 \
  --backup
```

## 7.5 Example Workflows

### Converting a HuggingFace Model

```bash
#!/bin/bash
# convert_huggingface.sh

MODEL_NAME="microsoft/bitnet-2b-chat"
OUTPUT_NAME="bitnet-2b-chat"

# Download model
huggingface-cli download $MODEL_NAME --local-dir ./model_cache

# Compile to SuperInstance format
sic-compile ./model_cache \
  --output ${OUTPUT_NAME}.simod \
  --name ${OUTPUT_NAME} \
  --version "1.0.0" \
  --author "microsoft" \
  --quantization ternary \
  --optimize O2 \
  --validate

# Clean up
rm -rf ./model_cache

echo "Module created: ${OUTPUT_NAME}.simod"
```

### Quality Assurance Pipeline

```bash
#!/bin/bash
# qa_pipeline.sh

MODULE=$1
REFERENCE=$2

echo "=== SuperInstance QA Pipeline ==="
echo "Module: $MODULE"
echo "Reference: $REFERENCE"

# 1. Structure validation
echo -e "\n[1/5] Structure validation..."
sic-validate $MODULE --structure || exit 1

# 2. Checksum verification
echo -e "\n[2/5] Checksum verification..."
sic-validate $MODULE --checksums || exit 1

# 3. Tokenizer test
echo -e "\n[3/5] Tokenizer test..."
sic-validate $MODULE --tokenizer || exit 1

# 4. Inference test
echo -e "\n[4/5] Inference test..."
sic-validate $MODULE --inference || exit 1

# 5. Quality comparison
echo -e "\n[5/5] Quality comparison..."
sic-validate $MODULE \
  --reference $REFERENCE \
  --perplexity \
  --perplexity-limit 0.05 \
  || exit 1

echo -e "\n=== All checks passed! ==="
```

---

# 8. Error Handling

## 8.1 Exception Hierarchy

```
SuperInstanceError (base)
├── DeviceError
│   ├── DeviceNotFoundError
│   ├── DeviceBusyError
│   ├── DeviceConnectionError
│   ├── DeviceClosedError
│   ├── DeviceResetError
│   └── FirmwareError
│       ├── FirmwareUpdateError
│       └── FirmwareVersionError
│
├── CartridgeError
│   ├── NoCartridgeError
│   ├── CartridgeReadError
│   ├── CartridgeWriteError
│   └── CartridgeCorruptError
│
├── ModelError
│   ├── ModelLoadError
│   ├── IncompatibleModelError
│   ├── ModelNotFoundError
│   └── ModelCorruptError
│
├── GenerationError
│   ├── ContextLengthExceededError
│   ├── InvalidTokenError
│   ├── GenerationTimeoutError
│   └── SamplingError
│
├── ConfigurationError
│   ├── InvalidConfigError
│   └── FeatureNotSupportedError
│
├── ThrottleError
│   └── ThermalThrottlingError
│
└── MemoryError
    ├── OutOfMemoryError
    └── KVCacheOverflowError
```

## 8.2 Exception Reference

### DeviceError

```python
class DeviceNotFoundError(SuperInstanceError):
    """
    No SuperInstance device detected.
    
    Raised when:
    - No device connected
    - Device not recognized by system
    - Driver not installed
    
    Recovery:
    1. Check USB connection
    2. Verify driver installation
    3. Try different USB port
    """
    pass

class DeviceBusyError(SuperInstanceError):
    """
    Device is in use by another process.
    
    Raised when:
    - Another process has exclusive access
    - Device is being updated
    - Previous operation not completed
    
    Recovery:
    1. Close other applications using device
    2. Wait and retry
    3. Reset device
    """
    pass

class ThermalThrottlingError(SuperInstanceError):
    """
    Device temperature exceeded safe limit.
    
    Attributes:
        temperature: Current temperature in Celsius
        limit: Safe temperature limit
        cooldown_seconds: Suggested wait time
    
    Recovery:
    1. Wait for device to cool
    2. Improve ventilation
    3. Reduce inference load
    """
    def __init__(self, temperature: float, limit: float):
        self.temperature = temperature
        self.limit = limit
        self.cooldown_seconds = int((temperature - limit) * 2)
```

### GenerationError

```python
class ContextLengthExceededError(GenerationError):
    """
    Input exceeds model context length.
    
    Attributes:
        input_tokens: Number of tokens in input
        max_tokens: Maximum allowed tokens
    
    Recovery:
    1. Truncate input
    2. Use sliding window
    3. Summarize input
    """
    def __init__(self, input_tokens: int, max_tokens: int):
        self.input_tokens = input_tokens
        self.max_tokens = max_tokens
        super().__init__(
            f"Input has {input_tokens} tokens, "
            f"maximum is {max_tokens}"
        )
```

## 8.3 Error Handling Examples

### Basic Error Handling

```python
from superinstance import (
    Device, DeviceNotFoundError, DeviceBusyError,
    NoCartridgeError, GenerationError
)

try:
    device = Device()
    model = device.load_cartridge()
    result = model.generate("Hello")
    print(result.text)
    
except DeviceNotFoundError:
    print("Error: No SuperInstance device found.")
    print("Please connect a device and try again.")
    
except DeviceBusyError:
    print("Error: Device is busy.")
    print("Close other applications using the device.")
    
except NoCartridgeError:
    print("Error: No cartridge inserted.")
    print("Please insert a model cartridge.")
    
except GenerationError as e:
    print(f"Error during generation: {e}")
```

### Advanced Error Handling

```python
from superinstance import (
    Device, DeviceNotFoundError, ThermalThrottlingError,
    ContextLengthExceededError, GenerationError
)
import time

def safe_generate(
    prompt: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> str:
    """Generate with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            device = Device()
            model = device.load_cartridge()
            
            # Check token count
            token_count = model.count_tokens(prompt)
            if token_count > model.context_length - 100:
                raise ContextLengthExceededError(
                    token_count, model.context_length
                )
            
            return model.generate(prompt).text
            
        except DeviceNotFoundError:
            if attempt < max_retries - 1:
                print(f"Device not found, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise
                
        except ThermalThrottlingError as e:
            print(f"Device overheated ({e.temperature}°C)")
            print(f"Waiting {e.cooldown_seconds}s for cooldown...")
            time.sleep(e.cooldown_seconds)
            continue
            
        except ContextLengthExceededError as e:
            print(f"Input too long: {e.input_tokens} > {e.max_tokens}")
            # Truncate and retry
            tokens = model.tokenize(prompt)[:e.max_tokens - 100]
            prompt = model.detokenize(tokens)
            continue
            
        except GenerationError as e:
            if attempt < max_retries - 1:
                print(f"Generation error: {e}, retrying...")
                time.sleep(retry_delay)
            else:
                raise
        
        finally:
            if 'device' in locals():
                device.close()
    
    raise GenerationError("Max retries exceeded")
```

## 8.4 Error Codes Reference

| Error Code | Name | Description |
|------------|------|-------------|
| 0x0001 | `DEVICE_NOT_FOUND` | No device connected |
| 0x0002 | `DEVICE_BUSY` | Device in use by another process |
| 0x0003 | `DEVICE_ERROR` | Generic device error |
| 0x0010 | `NO_CARTRIDGE` | No cartridge inserted |
| 0x0011 | `CARTRIDGE_READ_ERROR` | Failed to read cartridge |
| 0x0012 | `CARTRIDGE_CORRUPT` | Cartridge data corrupted |
| 0x0020 | `MODEL_INCOMPATIBLE` | Model incompatible with device |
| 0x0021 | `MODEL_LOAD_ERROR` | Failed to load model |
| 0x0030 | `CONTEXT_EXCEEDED` | Context length exceeded |
| 0x0031 | `GENERATION_ERROR` | Generation failed |
| 0x0040 | `THERMAL_THROTTLE` | Temperature too high |
| 0x0041 | `POWER_LIMIT` | Power limit exceeded |
| 0x0050 | `OUT_OF_MEMORY` | Memory allocation failed |
| 0x0051 | `KV_CACHE_OVERFLOW` | KV cache size exceeded |

---

# 9. Language Bindings

## 9.1 Python API (Primary)

The Python API is the primary interface for SuperInstance. All features are available through the `superinstance` package.

### Installation

```bash
pip install superinstance-sdk
```

### Complete Example

```python
from superinstance import (
    Device, DeviceType, GenerationConfig,
    Profiler
)
from superinstance.debug import Inspector

# Device management
device = Device()
info = device.info()

print(f"Device: {info.device_type.value}")
print(f"Cartridge: {info.cartridge_model}")

# Load model
model = device.load_cartridge()

# Generation
config = GenerationConfig(
    max_tokens=256,
    temperature=0.7,
    top_p=0.9
)

# Stream output
for token in model.generate_stream("Hello", config):
    print(token, end="", flush=True)

# Profile performance
with Profiler() as p:
    result = model.generate("Test prompt")

report = p.last_report
print(f"\nSpeed: {report.throughput_tok_per_s:.1f} tok/s")
```

## 9.2 C/C++ API

The C API provides low-level access for embedded systems integration.

### Header File

```c
/* superinstance.h - SuperInstance C API */

#ifndef SUPERINSTANCE_H
#define SUPERINSTANCE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Version */
#define SI_VERSION_MAJOR 1
#define SI_VERSION_MINOR 0
#define SI_VERSION_PATCH 0

/* Error codes */
typedef enum {
    SI_OK = 0,
    SI_ERROR = -1,
    SI_DEVICE_NOT_FOUND = -2,
    SI_DEVICE_BUSY = -3,
    SI_NO_CARTRIDGE = -4,
    SI_CONTEXT_EXCEEDED = -5,
    SI_GENERATION_ERROR = -6,
    SI_THERMAL_THROTTLE = -7,
    SI_OUT_OF_MEMORY = -8,
} si_error_t;

/* Device types */
typedef enum {
    SI_DEVICE_NANO,
    SI_DEVICE_STANDARD,
    SI_DEVICE_PRO,
    SI_DEVICE_MAKER_EDITION,
} si_device_type_t;

/* Handle types */
typedef struct si_device* si_handle_t;
typedef struct si_model* si_model_handle_t;
#define SI_INVALID_HANDLE NULL

/* Device info */
typedef struct {
    si_device_type_t device_type;
    char firmware_version[32];
    char serial_number[64];
    bool cartridge_inserted;
    char cartridge_model[128];
    float temperature_celsius;
    float power_watts;
    uint64_t uptime_seconds;
    uint32_t total_inferences;
} si_device_info_t;

/* Generation config */
typedef struct {
    uint32_t max_tokens;
    float temperature;
    float top_p;
    uint32_t top_k;
    int seed;
    bool echo;
} si_config_t;

/* Generation result */
typedef struct {
    char* text;
    uint32_t* tokens;
    uint32_t token_count;
    float tokens_per_second;
    float first_token_latency_ms;
    float total_time_ms;
    si_error_t status;
} si_result_t;

/* Default config */
static inline si_config_t si_config_default(void) {
    return (si_config_t){
        .max_tokens = 256,
        .temperature = 0.7f,
        .top_p = 0.9f,
        .top_k = 40,
        .seed = -1,
        .echo = false,
    };
}

/* Device functions */
si_handle_t si_open(const char* device_path);
void si_close(si_handle_t handle);
si_error_t si_device_info(si_handle_t handle, si_device_info_t* info);
char** si_list_devices(uint32_t* count);
void si_free_device_list(char** list, uint32_t count);

/* Model functions */
si_model_handle_t si_load_cartridge(si_handle_t handle);
void si_model_close(si_model_handle_t model);

/* Tokenization */
uint32_t* si_tokenize(si_model_handle_t model, const char* text, uint32_t* count);
char* si_detokenize(si_model_handle_t model, const uint32_t* tokens, uint32_t count);
uint32_t si_count_tokens(si_model_handle_t model, const char* text);

/* Generation */
si_result_t* si_generate(si_model_handle_t model, const char* prompt, const si_config_t* config);
si_error_t si_generate_stream(
    si_model_handle_t model,
    const char* prompt,
    const si_config_t* config,
    void (*callback)(const char* token, void* user_data),
    void* user_data
);

/* Memory management */
void si_free_result(si_result_t* result);
void si_free_tokens(uint32_t* tokens);
void si_free_string(char* str);

/* Error handling */
const char* si_error_string(si_error_t error);

#ifdef __cplusplus
}
#endif

#endif /* SUPERINSTANCE_H */
```

### C Example

```c
#include <stdio.h>
#include <superinstance/superinstance.h>

int main() {
    // Open device
    si_handle_t device = si_open(NULL);  // Auto-detect
    if (device == SI_INVALID_HANDLE) {
        fprintf(stderr, "Error: %s\n", si_error_string(SI_DEVICE_NOT_FOUND));
        return 1;
    }
    
    // Get device info
    si_device_info_t info;
    si_device_info(device, &info);
    printf("Device: %s\n", info.cartridge_model);
    
    // Load model
    si_model_handle_t model = si_load_cartridge(device);
    if (!model) {
        fprintf(stderr, "Error: No cartridge\n");
        si_close(device);
        return 1;
    }
    
    // Configure generation
    si_config_t config = si_config_default();
    config.max_tokens = 100;
    config.temperature = 0.7f;
    
    // Generate
    si_result_t* result = si_generate(model, "Hello, I am", &config);
    if (result->status == SI_OK) {
        printf("Response: %s\n", result->text);
        printf("Speed: %.1f tok/s\n", result->tokens_per_second);
    } else {
        fprintf(stderr, "Error: %s\n", si_error_string(result->status));
    }
    
    // Cleanup
    si_free_result(result);
    si_model_close(model);
    si_close(device);
    
    return 0;
}
```

### C++ Wrapper

```cpp
// superinstance_cpp.hpp
#pragma once

#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <stdexcept>

namespace superinstance {

class Error : public std::runtime_error {
public:
    explicit Error(const std::string& msg) : std::runtime_error(msg) {}
};

class Device;

class Model {
public:
    std::string generate(const std::string& prompt);
    void generate_stream(
        const std::string& prompt,
        std::function<void(const std::string&)> callback
    );
    
    std::vector<uint32_t> tokenize(const std::string& text);
    std::string detokenize(const std::vector<uint32_t>& tokens);
    uint32_t count_tokens(const std::string& text);
    
    uint32_t context_length() const;
    
private:
    friend class Device;
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

class Device {
public:
    Device();
    explicit Device(const std::string& path);
    ~Device();
    
    static std::vector<std::string> list_devices();
    
    struct Info {
        std::string device_type;
        std::string firmware_version;
        std::string serial_number;
        bool cartridge_inserted;
        std::string cartridge_model;
        float temperature_celsius;
        float power_watts;
    };
    
    Info info() const;
    Model load_cartridge();
    void reset();
    
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace superinstance
```

## 9.3 Rust API (Planned)

The Rust API is planned for Q3 2026.

### Planned Interface

```rust
// Planned Rust API (subject to change)

use superinstance::{Device, Model, Config, Error};

fn main() -> Result<(), Error> {
    // Connect to device
    let device = Device::open(None)?;  // Auto-detect
    
    // Get device info
    let info = device.info()?;
    println!("Device: {:?}", info.device_type);
    
    // Load model
    let model = device.load_cartridge()?;
    
    // Configure generation
    let config = Config {
        max_tokens: 100,
        temperature: 0.7,
        ..Default::default()
    };
    
    // Generate
    let result = model.generate("Hello, I am", &config)?;
    println!("Response: {}", result.text());
    
    // Streaming
    model.generate_stream("Tell me a story", &config, |token| {
        print!("{}", token);
        Ok(())
    })?;
    
    Ok(())
}
```

## 9.4 JavaScript API (Planned)

The JavaScript API is planned for Q4 2026, supporting both Node.js and browser environments.

### Planned Interface

```javascript
// Planned JavaScript API (subject to change)

import { Device, Model, Config } from 'superinstance';

async function main() {
    // Connect to device
    const device = await Device.open();
    
    // Get device info
    const info = await device.info();
    console.log(`Device: ${info.deviceType}`);
    
    // Load model
    const model = await device.loadCartridge();
    
    // Configure generation
    const config = new Config({
        maxTokens: 100,
        temperature: 0.7,
    });
    
    // Generate
    const result = await model.generate("Hello, I am", config);
    console.log(`Response: ${result.text}`);
    
    // Streaming
    for await (const token of model.generateStream("Tell me a story", config)) {
        process.stdout.write(token);
    }
    
    // Close device
    await device.close();
}

main().catch(console.error);
```

---

# 10. Examples Gallery

## 10.1 Basic Inference

```python
"""Basic inference example."""
from superinstance import Device, GenerationConfig

def main():
    # Connect to device
    device = Device()
    
    # Print device info
    info = device.info()
    print(f"Connected to {info.device_type.value}")
    print(f"Cartridge: {info.cartridge_model}")
    
    # Load model
    model = device.load_cartridge()
    
    # Simple generation
    result = model.generate("What is machine learning?")
    print(f"\nResponse: {result.text}")
    print(f"\nGenerated {result.generated_tokens} tokens")
    print(f"Speed: {result.tokens_per_second:.1f} tok/s")
    
    # Close device
    device.close()

if __name__ == "__main__":
    main()
```

## 10.2 Streaming Output

```python
"""Streaming output example."""
from superinstance import Device, GenerationConfig
import sys

def main():
    device = Device()
    model = device.load_cartridge()
    
    config = GenerationConfig(
        max_tokens=500,
        temperature=0.8,
        top_p=0.95
    )
    
    prompt = "Write a short story about a robot learning to paint:"
    
    print(f"Prompt: {prompt}\n")
    print("Response: ", end="", flush=True)
    
    # Stream tokens
    for token in model.generate_stream(prompt, config):
        print(token, end="", flush=True)
    
    print("\n")

if __name__ == "__main__":
    main()
```

## 10.3 Chat Application

```python
"""Interactive chat application."""
from superinstance import Device, GenerationConfig
import sys

def main():
    device = Device()
    model = device.load_cartridge()
    
    config = GenerationConfig(
        max_tokens=256,
        temperature=0.7,
        stop_sequences=["\nUser:", "\nHuman:"]
    )
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    
    print("SuperInstance Chat")
    print("Type 'quit' to exit, 'clear' to reset conversation\n")
    
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'clear':
            messages = [messages[0]]  # Keep system prompt
            print("Conversation cleared.\n")
            continue
        
        if not user_input:
            continue
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        print("Assistant: ", end="", flush=True)
        
        response_text = ""
        for token in model.chat_stream(messages, config):
            print(token, end="", flush=True)
            response_text += token
        
        print("\n")
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": response_text})
    
    device.close()

if __name__ == "__main__":
    main()
```

## 10.4 Integration with Home Assistant

```python
"""Home Assistant integration example."""
import json
import asyncio
from superinstance import Device, GenerationConfig

class SuperInstanceAssistant:
    """SuperInstance integration for Home Assistant."""
    
    def __init__(self, device_path: str = None):
        self.device = Device(device_path)
        self.model = self.device.load_cartridge()
        self.config = GenerationConfig(
            max_tokens=100,
            temperature=0.7
        )
    
    async def process_voice_command(self, command: str) -> dict:
        """Process a voice command and return structured response."""
        
        system_prompt = """You are a home automation assistant. 
        Respond in JSON format with actions to take.
        
        Example commands:
        - "Turn on the living room lights"
        - "Set temperature to 72 degrees"
        - "Lock the front door"
        
        Response format:
        {
            "intent": "action|query|unknown",
            "actions": [{"device": "...", "action": "...", "value": "..."}],
            "response": "Human-readable response"
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]
        
        result = self.model.chat(messages, self.config)
        
        try:
            return json.loads(result.text)
        except json.JSONDecodeError:
            return {
                "intent": "unknown",
                "actions": [],
                "response": result.text
            }
    
    async def handle_mqtt_message(self, topic: str, payload: str):
        """Handle incoming MQTT message."""
        command = json.loads(payload)
        response = await self.process_voice_command(command.get("text", ""))
        return json.dumps(response)
    
    def close(self):
        """Close device connection."""
        self.device.close()


# Home Assistant configuration.yaml example:
"""
automation:
  - alias: "SuperInstance Voice Command"
    trigger:
      - platform: mqtt
        topic: "homeassistant/voice/command"
    action:
      - service: mqtt.publish
        data:
          topic: "homeassistant/voice/response"
          payload_template: "{{ trigger.payload }}"
"""

# Integration script:
async def main():
    assistant = SuperInstanceAssistant()
    
    # Example commands
    commands = [
        "Turn on the kitchen lights",
        "What's the temperature in the living room?",
        "Set the thermostat to 70 degrees"
    ]
    
    for cmd in commands:
        print(f"\nCommand: {cmd}")
        response = await assistant.process_voice_command(cmd)
        print(f"Intent: {response['intent']}")
        print(f"Actions: {response['actions']}")
        print(f"Response: {response['response']}")
    
    assistant.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 10.5 Integration with ESP32

```cpp
/**
 * ESP32 SuperInstance Integration
 * 
 * Hardware connections:
 * - ESP32 GPIO 18, 19, 23, 25, 26, 27 to SuperInstance SPI
 * - Or USB Host Shield for USB connection
 */

#include <SPI.h>
#include <ArduinoJson.h>

#define SI_CS_PIN    5
#define SI_READY_PIN 4
#define SI_IRQ_PIN   16

class SuperInstanceClient {
private:
    SPIClass* spi;
    int cs_pin;
    int ready_pin;
    
public:
    SuperInstanceClient(SPIClass* spi_bus, int cs, int ready) 
        : spi(spi_bus), cs_pin(cs), ready_pin(ready) {
        pinMode(cs_pin, OUTPUT);
        digitalWrite(cs_pin, HIGH);
        pinMode(ready_pin, INPUT);
    }
    
    bool begin() {
        // Wait for device ready
        delay(100);
        return digitalRead(ready_pin) == HIGH;
    }
    
    String generate(const String& prompt, int max_tokens = 100) {
        // Create command packet
        StaticJsonDocument<512> cmd;
        cmd["cmd"] = "generate";
        cmd["prompt"] = prompt;
        cmd["max_tokens"] = max_tokens;
        cmd["temperature"] = 0.7;
        
        // Send command
        String cmd_str;
        serializeJson(cmd, cmd_str);
        
        spi->beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
        digitalWrite(cs_pin, LOW);
        
        // Send length prefix (2 bytes)
        uint16_t len = cmd_str.length();
        spi->transfer(len >> 8);
        spi->transfer(len & 0xFF);
        
        // Send payload
        for (size_t i = 0; i < len; i++) {
            spi->transfer(cmd_str[i]);
        }
        
        // Wait for response
        while (digitalRead(ready_pin) != HIGH) {
            delay(1);
        }
        
        // Read response length
        uint16_t resp_len = (spi->transfer(0) << 8) | spi->transfer(0);
        
        // Read response
        String response;
        for (size_t i = 0; i < resp_len; i++) {
            response += (char)spi->transfer(0);
        }
        
        digitalWrite(cs_pin, HIGH);
        spi->endTransaction();
        
        return response;
    }
};

// Main sketch
SuperInstanceClient* si_client;

void setup() {
    Serial.begin(115200);
    
    // Initialize SPI
    SPI.begin();
    
    // Create SuperInstance client
    si_client = new SuperInstanceClient(&SPI, SI_CS_PIN, SI_READY_PIN);
    
    if (si_client->begin()) {
        Serial.println("SuperInstance device ready");
    } else {
        Serial.println("SuperInstance device not found");
        while(1);
    }
}

void loop() {
    if (Serial.available()) {
        String prompt = Serial.readStringUntil('\n');
        prompt.trim();
        
        if (prompt.length() > 0) {
            Serial.print("Generating...");
            String response = si_client->generate(prompt, 100);
            Serial.println(" done.");
            Serial.println(response);
        }
    }
}
```

## 10.6 Integration with Raspberry Pi

```python
"""Raspberry Pi integration with GPIO control."""
import RPi.GPIO as GPIO
from superinstance import Device, GenerationConfig
import time
import threading

class SuperInstanceRaspberryPi:
    """SuperInstance integration for Raspberry Pi."""
    
    # GPIO pins for status indicators
    LED_READY = 17      # Green LED - device ready
    LED_THINKING = 27   # Yellow LED - processing
    LED_ERROR = 22      # Red LED - error state
    
    # GPIO pins for buttons
    BUTTON_TRIGGER = 5  # Button to trigger inference
    
    def __init__(self, device_path: str = None):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_READY, GPIO.OUT)
        GPIO.setup(self.LED_THINKING, GPIO.OUT)
        GPIO.setup(self.LED_ERROR, GPIO.OUT)
        GPIO.setup(self.BUTTON_TRIGGER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Connect to device
        try:
            self.device = Device(device_path)
            self.model = self.device.load_cartridge()
            GPIO.output(self.LED_READY, GPIO.HIGH)
            self.ready = True
        except Exception as e:
            GPIO.output(self.LED_ERROR, GPIO.HIGH)
            self.ready = False
            raise
        
        # Add button interrupt
        GPIO.add_event_detect(
            self.BUTTON_TRIGGER,
            GPIO.FALLING,
            callback=self._button_callback,
            bouncetime=300
        )
        
        self.config = GenerationConfig(
            max_tokens=50,
            temperature=0.7
        )
        
        self.prompt = "Tell me an interesting fact:"
    
    def _button_callback(self, channel):
        """Handle button press."""
        if self.ready:
            threading.Thread(target=self._run_inference).start()
    
    def _run_inference(self):
        """Run inference in background thread."""
        self.ready = False
        GPIO.output(self.LED_READY, GPIO.LOW)
        GPIO.output(self.LED_THINKING, GPIO.HIGH)
        
        try:
            result = self.model.generate(self.prompt, self.config)
            print(f"\n{result.text}\n")
            print(f"Generated in {result.total_time_ms:.0f}ms")
            print(f"Speed: {result.tokens_per_second:.1f} tok/s")
            
        except Exception as e:
            print(f"Error: {e}")
            GPIO.output(self.LED_ERROR, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(self.LED_ERROR, GPIO.LOW)
        
        finally:
            GPIO.output(self.LED_THINKING, GPIO.LOW)
            GPIO.output(self.LED_READY, GPIO.HIGH)
            self.ready = True
    
    def run_interactive(self):
        """Run interactive mode with text input."""
        print("\nSuperInstance Raspberry Pi Interface")
        print("=" * 40)
        print(f"Cartridge: {self.device.info().cartridge_model}")
        print("\nCommands:")
        print("  <text>  - Generate response")
        print("  prompt  - Set new prompt template")
        print("  temp N  - Set temperature")
        print("  stats   - Show device stats")
        print("  quit    - Exit")
        print("\nPress the button to generate with default prompt")
        print("=" * 40 + "\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if user_input.lower() == 'quit':
                    break
                    
                elif user_input.lower() == 'prompt':
                    new_prompt = input("Enter new prompt: ")
                    self.prompt = new_prompt
                    print(f"Prompt set to: {self.prompt}")
                    
                elif user_input.lower().startswith('temp '):
                    temp = float(user_input.split()[1])
                    self.config.temperature = temp
                    print(f"Temperature set to: {temp}")
                    
                elif user_input.lower() == 'stats':
                    info = self.device.info()
                    print(f"Temperature: {info.temperature_celsius}°C")
                    print(f"Power: {info.power_watts}W")
                    print(f"Uptime: {info.uptime_seconds}s")
                    print(f"Inferences: {info.total_inferences}")
                    
                elif user_input:
                    self.prompt = user_input
                    self._run_inference()
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\nGoodbye!")
    
    def close(self):
        """Cleanup resources."""
        GPIO.remove_event_detect(self.BUTTON_TRIGGER)
        GPIO.cleanup()
        if hasattr(self, 'device'):
            self.device.close()


def main():
    si = SuperInstanceRaspberryPi()
    try:
        si.run_interactive()
    finally:
        si.close()


if __name__ == "__main__":
    main()
```

## 10.7 Web Server Integration

```python
"""FastAPI web server for SuperInstance."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from superinstance import Device, GenerationConfig
import asyncio
import json

app = FastAPI(
    title="SuperInstance API",
    description="REST API for SuperInstance inference",
    version="1.0.0"
)

# Global device instance
device = None
model = None

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: int = 256
    temperature: float = 0.7
    stream: bool = False

class GenerateResponse(BaseModel):
    text: str
    tokens_generated: int
    tokens_per_second: float
    first_token_latency_ms: float

@app.on_event("startup")
async def startup():
    global device, model
    device = Device()
    model = device.load_cartridge()
    print(f"Connected to device: {device.info().cartridge_model}")

@app.on_event("shutdown")
async def shutdown():
    global device
    if device:
        device.close()

@app.get("/")
async def root():
    return {"status": "ok", "model": device.info().cartridge_model}

@app.get("/device/info")
async def device_info():
    info = device.info()
    return {
        "device_type": info.device_type.value,
        "firmware_version": info.firmware_version,
        "cartridge_model": info.cartridge_model,
        "temperature_celsius": info.temperature_celsius,
        "power_watts": info.power_watts
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    config = GenerationConfig(
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p
    )
    
    if request.stream:
        return StreamingResponse(
            generate_stream(request.prompt, config),
            media_type="text/event-stream"
        )
    
    result = model.generate(request.prompt, config)
    
    return GenerateResponse(
        text=result.text,
        tokens_generated=result.generated_tokens,
        tokens_per_second=result.tokens_per_second,
        first_token_latency_ms=result.first_token_latency_ms
    )

async def generate_stream(prompt: str, config: GenerationConfig):
    """Generate streaming response."""
    for token in model.generate_stream(prompt, config):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/chat", response_model=GenerateResponse)
async def chat(request: ChatRequest):
    config = GenerationConfig(
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    if request.stream:
        return StreamingResponse(
            chat_stream(messages, config),
            media_type="text/event-stream"
        )
    
    result = model.chat(messages, config)
    
    return GenerateResponse(
        text=result.text,
        tokens_generated=result.generated_tokens,
        tokens_per_second=result.tokens_per_second,
        first_token_latency_ms=result.first_token_latency_ms
    )

async def chat_stream(messages: list, config: GenerationConfig):
    """Generate streaming chat response."""
    for token in model.chat_stream(messages, config):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/health")
async def health():
    info = device.info()
    return {
        "status": "healthy",
        "temperature": info.temperature_celsius,
        "power": info.power_watts
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

# Appendix A: API Quick Reference

## Device API

| Method | Description |
|--------|-------------|
| `Device.list_devices()` | List available devices |
| `Device()` | Connect to device (auto-detect) |
| `Device(path)` | Connect to specific device |
| `device.info()` | Get device information |
| `device.load_cartridge()` | Load model from cartridge |
| `device.load_model(path)` | Load model from file (Pro/Maker) |
| `device.reset()` | Reset device |
| `device.close()` | Close connection |

## Model API

| Method | Description |
|--------|-------------|
| `model.generate(prompt, config)` | Generate completion |
| `model.generate_stream(prompt, config)` | Stream tokens |
| `model.chat(messages, config)` | Chat generation |
| `model.chat_stream(messages, config)` | Stream chat |
| `model.tokenize(text)` | Text to tokens |
| `model.detokenize(tokens)` | Tokens to text |
| `model.count_tokens(text)` | Count tokens |

## GenerationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_tokens` | int | 256 | Maximum tokens to generate |
| `temperature` | float | 0.7 | Sampling temperature |
| `top_p` | float | 0.9 | Nucleus sampling |
| `top_k` | int | 40 | Top-k sampling |
| `stop_sequences` | List[str] | None | Stop sequences |
| `seed` | int | None | Random seed |

---

# Appendix B: Community Resources

- **GitHub**: [github.com/superinstance-ai/superinstance-sdk](https://github.com/superinstance-ai/superinstance-sdk)
- **Documentation**: [docs.superinstance.ai](https://docs.superinstance.ai)
- **Discord**: [discord.gg/superinstance](https://discord.gg/superinstance)
- **License**: Apache 2.0

---

**Document Version**: 1.0.0  
**Last Updated**: March 2026  
**Classification**: Developer Reference Document  
**License**: Apache 2.0
