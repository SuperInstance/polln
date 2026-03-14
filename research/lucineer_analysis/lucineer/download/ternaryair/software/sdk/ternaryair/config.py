"""
Configuration for TernaryAir SDK.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PowerMode(Enum):
    """Power modes for the device."""
    ACTIVE = "active"
    IDLE = "idle"
    SLEEP = "sleep"


@dataclass
class Config:
    """Configuration for TernaryAir device.
    
    Attributes:
        device_path: Path to the device (e.g., /dev/ttyUSB0 or COM3).
        baud_rate: Baud rate for serial communication.
        timeout: Timeout in seconds for operations.
        max_tokens: Maximum tokens to generate by default.
        temperature: Sampling temperature (0.0 to 2.0).
        top_p: Nucleus sampling probability.
        top_k: Top-k sampling parameter.
        repeat_penalty: Penalty for repeated tokens.
        power_mode: Power mode for the device.
        auto_reconnect: Whether to automatically reconnect on disconnect.
    """
    
    # Connection settings
    device_path: Optional[str] = None
    baud_rate: int = 115200
    timeout: float = 30.0
    
    # Generation settings
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Power management
    power_mode: PowerMode = PowerMode.ACTIVE
    
    # Behavior
    auto_reconnect: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError(f"temperature must be between 0.0 and 2.0, got {self.temperature}")
        
        if self.top_p < 0.0 or self.top_p > 1.0:
            raise ValueError(f"top_p must be between 0.0 and 1.0, got {self.top_p}")
        
        if self.top_k < 0:
            raise ValueError(f"top_k must be non-negative, got {self.top_k}")
        
        if self.repeat_penalty < 1.0:
            raise ValueError(f"repeat_penalty must be >= 1.0, got {self.repeat_penalty}")
        
        if self.max_tokens < 1:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")
    
    @classmethod
    def default(cls) -> "Config":
        """Create a default configuration."""
        return cls()
    
    @classmethod
    def creative(cls) -> "Config":
        """Create a configuration optimized for creative tasks."""
        return cls(
            temperature=1.0,
            top_p=0.95,
            top_k=50,
            repeat_penalty=1.05,
        )
    
    @classmethod
    def precise(cls) -> "Config":
        """Create a configuration optimized for precise/factual tasks."""
        return cls(
            temperature=0.3,
            top_p=0.8,
            top_k=20,
            repeat_penalty=1.2,
        )
    
    @classmethod
    def deterministic(cls) -> "Config":
        """Create a configuration for deterministic output."""
        return cls(
            temperature=0.0,
            top_p=1.0,
            top_k=1,
            repeat_penalty=1.0,
        )
