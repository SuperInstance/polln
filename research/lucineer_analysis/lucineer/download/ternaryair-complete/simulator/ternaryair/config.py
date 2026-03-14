"""
Configuration for TernaryAir models
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for a TernaryAir model"""
    
    name: str
    params: str
    layers: int
    dim: int
    vocab_size: int = 32000
    max_context: int = 4096
    num_heads: int = 12
    
    @classmethod
    def tiny(cls) -> "ModelConfig":
        """Tiny model configuration"""
        return cls(
            name="tiny",
            params="500M",
            layers=12,
            dim=512,
            vocab_size=16000,
            max_context=2048,
            num_heads=8,
        )
    
    @classmethod
    def small(cls) -> "ModelConfig":
        """Small model configuration"""
        return cls(
            name="small",
            params="1.5B",
            layers=18,
            dim=768,
            vocab_size=32000,
            max_context=4096,
            num_heads=12,
        )
    
    @classmethod
    def medium(cls) -> "ModelConfig":
        """Medium model configuration"""
        return cls(
            name="medium",
            params="3B",
            layers=24,
            dim=1024,
            vocab_size=32000,
            max_context=4096,
            num_heads=16,
        )


# Registry of available models
MODEL_REGISTRY = {
    "debug-tiny": ModelConfig("debug-tiny", "125M", 6, 384, 8000, 512, 4),
    "tiny": ModelConfig.tiny(),
    "small": ModelConfig.small(),
    "medium": ModelConfig.medium(),
}


def get_config(model_name: str) -> ModelConfig:
    """Get model configuration by name"""
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Available: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[model_name]
