"""
Software simulator for TernaryAir (for development without hardware).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Generator

from ternaryair.device import Backend, DeviceInfo, DeviceStatus


# Predefined responses for simulation
SIMULATION_RESPONSES = [
    "I understand your question. Let me think about that for a moment. Based on my training, I can provide you with a helpful response that addresses your needs.",
    "That's an interesting topic! There are many aspects to consider when discussing this subject. Let me share some insights that might be useful for you.",
    "Great question! This is something that many people wonder about. I'll do my best to provide a clear and informative answer.",
    "I appreciate you asking this. It's important to approach such topics thoughtfully. Here's what I can tell you about it.",
    "Thank you for your input! I'm here to help with any questions or tasks you have. Let me provide a useful response.",
]

# Token-by-token streaming simulation
STREAMING_WORDS = [
    "Hello", "there", "!", "I", "am", "TernaryAir", ",", "your", "local", "AI",
    "assistant", ".", "I", "run", "entirely", "on", "hardware", "with", "no",
    "internet", "connection", "needed", ".", "Your", "data", "stays", "private",
    "and", "is", "never", "stored", "or", "transmitted", ".", "How", "can",
    "I", "help", "you", "today", "?",
]


@dataclass
class SimulatorConfig:
    """Configuration for the simulator.
    
    Attributes:
        simulate_delay: Whether to simulate inference delay.
        tokens_per_second: Simulated generation speed.
        power_watts: Simulated power consumption.
        temperature_c: Simulated junction temperature.
    """
    simulate_delay: bool = True
    tokens_per_second: float = 100.0
    power_watts: float = 4.0
    temperature_c: float = 45.0


class Simulator(Backend):
    """Software simulator for TernaryAir.
    
    This simulator allows development and testing without physical hardware.
    It mimics the behavior of the actual device including timing and responses.
    
    Args:
        config: Simulator configuration.
    
    Example:
        >>> from ternaryair import TernaryAir, Simulator
        >>> device = TernaryAir(backend=Simulator())
        >>> response = device.generate("Hello!")
    """
    
    def __init__(self, config: Optional[SimulatorConfig] = None) -> None:
        """Initialize simulator."""
        self._config = config or SimulatorConfig()
        self._connected = False
        self._tokens_generated = 0
        self._inference_count = 0
        self._start_time: Optional[float] = None
    
    def connect(self) -> None:
        """Connect to simulated device."""
        self._connected = True
        self._start_time = time.time()
    
    def disconnect(self) -> None:
        """Disconnect from simulated device."""
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    def get_info(self) -> DeviceInfo:
        """Get simulated device info."""
        return DeviceInfo(
            model="TernaryAir-350M-SIM",
            firmware_version="1.0.0-sim",
            serial_number="SIM-00000000",
            memory_mb=512,
            max_tokens=4096,
        )
    
    def get_status(self) -> DeviceStatus:
        """Get simulated device status."""
        uptime = time.time() - self._start_time if self._start_time else 0.0
        return DeviceStatus(
            is_ready=self._connected,
            temperature_c=self._config.temperature_c + random.uniform(-2, 2),
            power_w=self._config.power_watts + random.uniform(-0.5, 0.5),
            tokens_generated=self._tokens_generated,
            inference_count=self._inference_count,
            uptime_s=uptime,
        )
    
    def infer(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repeat_penalty: float,
    ) -> str:
        """Run simulated inference."""
        if not self._connected:
            raise RuntimeError("Not connected")
        
        self._inference_count += 1
        
        # Generate a response
        if temperature < 0.1:
            # Deterministic mode - always same response
            response = SIMULATION_RESPONSES[0][:max_tokens * 4]
        else:
            # Random selection
            response = random.choice(SIMULATION_RESPONSES)
        
        # Simulate timing
        if self._config.simulate_delay:
            token_count = min(len(response.split()), max_tokens)
            delay = token_count / self._config.tokens_per_second
            time.sleep(delay)
        
        self._tokens_generated += min(len(response.split()), max_tokens)
        
        return response
    
    def stream(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repeat_penalty: float,
    ) -> Generator[str, None, None]:
        """Stream simulated output."""
        if not self._connected:
            raise RuntimeError("Not connected")
        
        self._inference_count += 1
        
        # Use predefined streaming words, repeating as needed
        words_to_generate = (STREAMING_WORDS * ((max_tokens // len(STREAMING_WORDS)) + 1))[:max_tokens]
        
        for word in words_to_generate:
            # Simulate token timing
            if self._config.simulate_delay:
                time.sleep(1.0 / self._config.tokens_per_second)
            
            self._tokens_generated += 1
            yield word + " "
