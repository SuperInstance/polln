"""
SuperInstance SDK - Hardware Simulation Backend

This module provides a simulated hardware backend for development and testing
without physical SuperInstance hardware. It simulates device detection,
model loading, and inference with realistic timing and behavior.
"""

import random
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Iterator, Any
from contextlib import contextmanager


class SimulatedDeviceType(Enum):
    """Simulated device types."""
    NANO = "nano"
    STANDARD = "standard"
    PRO = "pro"
    MAKER_EDITION = "maker"


@dataclass
class SimulatedDeviceInfo:
    """Simulated device information."""
    device_type: SimulatedDeviceType
    firmware_version: str
    serial_number: str
    cartridge_inserted: bool
    cartridge_model: Optional[str]
    cartridge_version: Optional[str]
    temperature_celsius: float
    power_watts: float
    uptime_seconds: int
    total_inferences: int
    total_tokens_generated: int
    usb_speed: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'device_type': self.device_type.value,
            'firmware_version': self.firmware_version,
            'serial_number': self.serial_number,
            'cartridge_inserted': self.cartridge_inserted,
            'cartridge_model': self.cartridge_model,
            'cartridge_version': self.cartridge_version,
            'temperature_celsius': self.temperature_celsius,
            'power_watts': self.power_watts,
            'uptime_seconds': self.uptime_seconds,
            'total_inferences': self.total_inferences,
            'total_tokens_generated': self.total_tokens_generated,
            'usb_speed': self.usb_speed,
        }


@dataclass
class SimulatedCartridge:
    """Simulated model cartridge."""
    name: str
    version: str
    context_length: int
    vocab_size: int
    parameters: int
    quantization: str


# Predefined simulated cartridges
AVAILABLE_CARTRIDGES = {
    'bitnet-2b-chat': SimulatedCartridge(
        name='bitnet-2b-chat',
        version='1.0.0',
        context_length=4096,
        vocab_size=32000,
        parameters=2_000_000_000,
        quantization='ternary'
    ),
    'bitnet-3b-instruct': SimulatedCartridge(
        name='bitnet-3b-instruct',
        version='1.1.0',
        context_length=8192,
        vocab_size=32000,
        parameters=3_000_000_000,
        quantization='ternary'
    ),
    'tinyllama-1.1b': SimulatedCartridge(
        name='tinyllama-1.1b',
        version='2.0.0',
        context_length=2048,
        vocab_size=32000,
        parameters=1_100_000_000,
        quantization='int4'
    ),
}


class SimulatedTokenizer:
    """Simple simulated tokenizer for development."""

    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self._token_cache: Dict[str, List[int]] = {}

    def encode(self, text: str) -> List[int]:
        """Convert text to simulated token IDs."""
        if text in self._token_cache:
            return self._token_cache[text]

        # Simple simulation: roughly 4 characters per token
        tokens = []
        i = 0
        while i < len(text):
            # Use hash of substring for deterministic tokenization
            chunk = text[i:i+4]
            token_id = int(hashlib.md5(chunk.encode()).hexdigest()[:8], 16) % (self.vocab_size - 100) + 50
            tokens.append(token_id)
            i += 4

        self._token_cache[text] = tokens
        return tokens

    def decode(self, tokens: List[int]) -> str:
        """Convert token IDs back to text (simulated)."""
        # For simulation, we just return a placeholder
        # In real implementation, this would use the actual vocabulary
        return f"<decoded_{len(tokens)}_tokens>"

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encode(text))


class SimulatedGenerator:
    """Simulated text generator with realistic behavior."""

    # Sample responses for different prompt types
    RESPONSE_TEMPLATES = {
        'greeting': [
            "Hello! I'm a language model running on SuperInstance hardware. How can I help you today?",
            "Hi there! I'm running on dedicated inference hardware. What would you like to know?",
            "Greetings! I'm powered by SuperInstance's mask-locked chip. Feel free to ask me anything.",
        ],
        'question': [
            "That's an interesting question. Let me explain...",
            "Great question! Here's what I know about that topic...",
            "I'd be happy to help with that. The answer involves...",
        ],
        'story': [
            "Once upon a time, in a world where AI ran on dedicated hardware...",
            "In a small workshop, a developer discovered the power of specialized inference...",
            "The year was 2026, and everything changed when the first mask-locked chip arrived...",
        ],
        'code': [
            "Here's a Python example:\n\n```python\ndef hello_world():\n    print('Hello from SuperInstance!')\n```",
            "Sure, here's some code:\n\n```python\nimport superinstance\n\ndevice = superinstance.Device()\nmodel = device.load_cartridge()\n```",
        ],
        'default': [
            "I understand what you're asking. Let me provide a helpful response based on my training.",
            "That's an interesting point. Here's my perspective on this matter...",
            "Thanks for your input! I'd like to share my thoughts on this topic.",
        ]
    }

    def __init__(
        self,
        tokenizer: SimulatedTokenizer,
        tokens_per_second: float = 30.0,
        first_token_latency_ms: float = 15.0,
        energy_per_token_mj: float = 0.08,
        seed: Optional[int] = None
    ):
        self.tokenizer = tokenizer
        self.tokens_per_second = tokens_per_second
        self.first_token_latency_ms = first_token_latency_ms
        self.energy_per_token_mj = energy_per_token_mj
        self.rng = random.Random(seed)

    def _classify_prompt(self, prompt: str) -> str:
        """Classify prompt type for response selection."""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(word in prompt_lower for word in ['story', 'once upon', 'tell me a tale']):
            return 'story'
        elif any(word in prompt_lower for word in ['code', 'python', 'function', 'example']):
            return 'code'
        elif '?' in prompt:
            return 'question'
        return 'default'

    def generate_response(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate a complete response."""
        prompt_type = self._classify_prompt(prompt)
        templates = self.RESPONSE_TEMPLATES.get(prompt_type, self.RESPONSE_TEMPLATES['default'])
        return self.rng.choice(templates)

    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> Iterator[Tuple[str, float]]:
        """
        Stream tokens with realistic timing.

        Yields:
            Tuple of (token, time_ms) for each token
        """
        response = self.generate_response(prompt, max_tokens)
        tokens = self.tokenizer.encode(response)

        # Limit to max_tokens
        tokens = tokens[:max_tokens]

        for i, token_id in enumerate(tokens):
            # First token has higher latency
            if i == 0:
                delay_ms = self.first_token_latency_ms
            else:
                # Subsequent tokens at tokens_per_second rate
                delay_ms = 1000.0 / self.tokens_per_second

            # Add some jitter
            delay_ms *= (0.9 + self.rng.random() * 0.2)

            # Simulate processing time
            time.sleep(delay_ms / 1000.0)

            # Generate a token-like string
            token_str = self._token_to_string(token_id, i, response)
            yield token_str, delay_ms

    def _token_to_string(self, token_id: int, position: int, full_response: str) -> str:
        """Convert token ID to string representation."""
        words = full_response.split()
        if position < len(words):
            return words[position] + ' '
        return ''


class SimulatedDevice:
    """Simulated SuperInstance hardware device."""

    def __init__(
        self,
        device_type: SimulatedDeviceType = SimulatedDeviceType.PRO,
        cartridge_name: str = 'bitnet-2b-chat',
        tokens_per_second: float = 30.0,
        seed: Optional[int] = None
    ):
        self.device_type = device_type
        self._cartridge_name = cartridge_name
        self._tokens_per_second = tokens_per_second
        self._seed = seed
        self._rng = random.Random(seed)

        self._uptime = 0
        self._inferences = 0
        self._tokens_generated = 0
        self._is_open = False
        self._model_loaded = False
        self._temperature_base = 35.0
        self._power_base = 0.5

        self._cartridge: Optional[SimulatedCartridge] = None
        self._generator: Optional[SimulatedGenerator] = None
        self._tokenizer: Optional[SimulatedTokenizer] = None

    def open(self) -> None:
        """Open connection to simulated device."""
        if self._is_open:
            raise RuntimeError("Device already open")
        self._is_open = True
        self._uptime = int(time.time())  # Simulate uptime start

    def close(self) -> None:
        """Close connection to simulated device."""
        self._is_open = False
        self._model_loaded = False

    def get_info(self) -> SimulatedDeviceInfo:
        """Get simulated device information."""
        if not self._is_open:
            raise RuntimeError("Device not open")

        # Simulate realistic device stats
        elapsed = int(time.time()) - self._uptime if self._uptime else 0
        temp = self._temperature_base + self._rng.uniform(-2, 5) + (self._inferences * 0.001)
        power = self._power_base + self._rng.uniform(0.1, 0.5) + (self._inferences * 0.0001)

        return SimulatedDeviceInfo(
            device_type=self.device_type,
            firmware_version='1.2.3',
            serial_number=f'SI-{self.device_type.value.upper()}-2026-{self._rng.randint(100000, 999999)}',
            cartridge_inserted=self._cartridge_name is not None,
            cartridge_model=self._cartridge.name if self._cartridge else None,
            cartridge_version=self._cartridge.version if self._cartridge else None,
            temperature_celsius=round(temp, 1),
            power_watts=round(power, 2),
            uptime_seconds=elapsed,
            total_inferences=self._inferences,
            total_tokens_generated=self._tokens_generated,
            usb_speed=self._get_usb_speed()
        )

    def _get_usb_speed(self) -> str:
        """Get USB speed based on device type."""
        speeds = {
            SimulatedDeviceType.NANO: 'usb3.0',
            SimulatedDeviceType.STANDARD: 'usb3.2',
            SimulatedDeviceType.PRO: 'usb4',
            SimulatedDeviceType.MAKER_EDITION: 'usb4',
        }
        return speeds.get(self.device_type, 'usb3.0')

    def load_cartridge(self) -> SimulatedCartridge:
        """Load the simulated cartridge."""
        if not self._is_open:
            raise RuntimeError("Device not open")

        if self._cartridge_name is None:
            raise RuntimeError("No cartridge inserted")

        if self._cartridge_name not in AVAILABLE_CARTRIDGES:
            raise RuntimeError(f"Unknown cartridge: {self._cartridge_name}")

        self._cartridge = AVAILABLE_CARTRIDGES[self._cartridge_name]
        self._tokenizer = SimulatedTokenizer(self._cartridge.vocab_size)
        self._generator = SimulatedGenerator(
            tokenizer=self._tokenizer,
            tokens_per_second=self._tokens_per_second,
            seed=self._seed
        )
        self._model_loaded = True
        return self._cartridge

    def get_tokenizer(self) -> SimulatedTokenizer:
        """Get the tokenizer for the loaded model."""
        if not self._model_loaded:
            raise RuntimeError("Model not loaded")
        return self._tokenizer

    def get_generator(self) -> SimulatedGenerator:
        """Get the generator for the loaded model."""
        if not self._model_loaded:
            raise RuntimeError("Model not loaded")
        return self._generator

    def record_inference(self, tokens_generated: int) -> None:
        """Record an inference for statistics."""
        self._inferences += 1
        self._tokens_generated += tokens_generated


# Simulated device detection
def detect_simulated_devices() -> List[str]:
    """
    Detect simulated devices.

    Returns:
        List of simulated device paths
    """
    # In simulation, we always return one device
    return ['/dev/superinstance0-sim']


def create_simulated_device(
    device_path: str = None,
    device_type: SimulatedDeviceType = SimulatedDeviceType.PRO,
    **kwargs
) -> SimulatedDevice:
    """Create a simulated device instance."""
    return SimulatedDevice(device_type=device_type, **kwargs)
