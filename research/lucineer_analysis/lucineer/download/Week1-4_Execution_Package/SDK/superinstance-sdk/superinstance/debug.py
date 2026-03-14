"""
SuperInstance SDK - Debug Utilities

This module provides debugging and introspection utilities for
understanding model behavior and diagnosing issues.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import json
import time

if TYPE_CHECKING:
    from .device import Device
    from .model import Model


@dataclass
class DebugInfo:
    """Debug information container."""
    device_info: Dict[str, Any]
    model_info: Dict[str, Any]
    generation_stats: Dict[str, Any]
    warnings: List[str]
    timestamp: str

    def to_dict(self) -> dict:
        return {
            'device_info': self.device_info,
            'model_info': self.model_info,
            'generation_stats': self.generation_stats,
            'warnings': self.warnings,
            'timestamp': self.timestamp,
        }

    def __str__(self) -> str:
        lines = [
            "╔" + "═" * 60 + "╗",
            "║" + "SuperInstance Debug Info".center(60) + "║",
            "╠" + "═" * 60 + "╣",
        ]

        # Device info
        lines.append("║ Device Information:" + " " * 39 + "║")
        for key, value in self.device_info.items():
            line = f"║   {key}: {value}"
            lines.append(line + " " * (60 - len(line)) + "║")

        # Model info
        lines.append("╠" + "═" * 60 + "╣")
        lines.append("║ Model Information:" + " " * 41 + "║")
        for key, value in self.model_info.items():
            line = f"║   {key}: {value}"
            lines.append(line + " " * (60 - len(line)) + "║")

        # Stats
        if self.generation_stats:
            lines.append("╠" + "═" * 60 + "╣")
            lines.append("║ Generation Statistics:" + " " * 37 + "║")
            for key, value in self.generation_stats.items():
                line = f"║   {key}: {value}"
                lines.append(line + " " * (60 - len(line)) + "║")

        # Warnings
        if self.warnings:
            lines.append("╠" + "═" * 60 + "╣")
            lines.append("║ Warnings:" + " " * 49 + "║")
            for warning in self.warnings:
                line = f"║   ⚠ {warning}"
                lines.append(line + " " * (60 - len(line)) + "║")

        lines.append("╚" + "═" * 60 + "╝")
        return '\n'.join(lines)


class Debugger:
    """
    Debug utilities for SuperInstance SDK.

    Provides methods for inspecting device state, model behavior,
    and diagnosing issues during development.

    Example:
        >>> from superinstance import Device
        >>> from superinstance.debug import Debugger
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> debugger = Debugger(device, model)
        >>> info = debugger.get_info()
        >>> print(info)
    """

    def __init__(
        self,
        device: 'Device',
        model: Optional['Model'] = None
    ):
        """
        Initialize debugger.

        Args:
            device: Connected Device instance
            model: Optional loaded Model instance
        """
        self._device = device
        self._model = model
        self._generation_count = 0
        self._total_tokens = 0
        self._total_time_ms = 0
        self._warnings: List[str] = []

    def get_info(self) -> DebugInfo:
        """
        Get comprehensive debug information.

        Returns:
            DebugInfo with device, model, and stats information
        """
        from datetime import datetime

        device_info = self._get_device_info()
        model_info = self._get_model_info() if self._model else {}
        stats = self._get_stats()

        return DebugInfo(
            device_info=device_info,
            model_info=model_info,
            generation_stats=stats,
            warnings=self._warnings.copy(),
            timestamp=datetime.now().isoformat(),
        )

    def _get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        try:
            info = self._device.info()
            return {
                'type': info.device_type.value,
                'serial': info.serial_number,
                'firmware': info.firmware_version,
                'temperature': f"{info.temperature_celsius}°C",
                'power': f"{info.power_watts}W",
                'usb_speed': info.usb_speed,
                'cartridge': info.cartridge_model or 'None',
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if not self._model:
            return {}

        try:
            return {
                'name': self._model.name,
                'version': self._model.version,
                'context_length': self._model.context_length,
                'vocab_size': self._model.vocab_size,
                'parameters': f"{self._model.parameters:,}",
                'quantization': self._model.quantization,
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        if self._generation_count == 0:
            return {}

        avg_throughput = (
            self._total_tokens / (self._total_time_ms / 1000)
            if self._total_time_ms > 0 else 0
        )

        return {
            'total_generations': self._generation_count,
            'total_tokens': self._total_tokens,
            'total_time': f"{self._total_time_ms:.2f}ms",
            'avg_throughput': f"{avg_throughput:.1f} tok/s",
        }

    def record_generation(
        self,
        tokens: int,
        time_ms: float
    ) -> None:
        """
        Record a generation for statistics.

        Args:
            tokens: Number of tokens generated
            time_ms: Time taken in milliseconds
        """
        self._generation_count += 1
        self._total_tokens += tokens
        self._total_time_ms += time_ms

    def add_warning(self, warning: str) -> None:
        """
        Add a warning to the debug info.

        Args:
            warning: Warning message
        """
        self._warnings.append(warning)

    def clear_warnings(self) -> None:
        """Clear all warnings."""
        self._warnings.clear()

    def reset_stats(self) -> None:
        """Reset generation statistics."""
        self._generation_count = 0
        self._total_tokens = 0
        self._total_time_ms = 0

    def inspect_token(
        self,
        token_id: int,
        model: Optional['Model'] = None
    ) -> Dict[str, Any]:
        """
        Inspect a single token.

        Args:
            token_id: Token ID to inspect
            model: Model to use (uses stored model if None)

        Returns:
            Dictionary with token information
        """
        model = model or self._model
        if not model:
            raise ValueError("No model available for token inspection")

        return {
            'token_id': token_id,
            'decoded': model.detokenize([token_id]),
            'is_special': token_id < 100,  # Simplified check
        }

    def compare_generations(
        self,
        prompt: str,
        config1: 'GenerationConfig',
        config2: 'GenerationConfig',
    ) -> Dict[str, Any]:
        """
        Compare two generation configurations.

        Args:
            prompt: Input prompt
            config1: First generation config
            config2: Second generation config

        Returns:
            Comparison results
        """
        if not self._model:
            raise ValueError("No model loaded")

        result1 = self._model.generate(prompt, config1)
        result2 = self._model.generate(prompt, config2)

        return {
            'prompt': prompt,
            'config1': {
                'params': config1.to_dict(),
                'output': result1.text,
                'tokens': result1.generated_tokens,
                'time_ms': result1.total_time_ms,
            },
            'config2': {
                'params': config2.to_dict(),
                'output': result2.text,
                'tokens': result2.generated_tokens,
                'time_ms': result2.total_time_ms,
            },
            'difference': {
                'tokens': result2.generated_tokens - result1.generated_tokens,
                'time_ms': result2.total_time_ms - result1.total_time_ms,
            },
        }


class TokenInspector:
    """
    Utility for inspecting tokenization and generation.

    Example:
        >>> from superinstance import Device
        >>> from superinstance.debug import TokenInspector
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> inspector = TokenInspector(model)
        >>> inspector.visualize_tokens("Hello, world!")
    """

    def __init__(self, model: 'Model'):
        """
        Initialize token inspector.

        Args:
            model: Loaded Model instance
        """
        self._model = model

    def visualize_tokens(
        self,
        text: str,
        show_ids: bool = True
    ) -> str:
        """
        Create a visualization of tokenization.

        Args:
            text: Text to tokenize
            show_ids: Show token IDs

        Returns:
            Formatted visualization string
        """
        tokens = self._model.tokenize(text)

        lines = [
            f"Text: {text}",
            f"Tokens: {len(tokens)}",
            "",
            "Visualization:",
        ]

        # Create visual representation
        visual_parts = []
        for i, token_id in enumerate(tokens):
            decoded = self._model.detokenize([token_id])
            if show_ids:
                visual_parts.append(f"[{decoded}|{token_id}]")
            else:
                visual_parts.append(f"[{decoded}]")

        lines.append("".join(visual_parts))

        return '\n'.join(lines)

    def token_frequency(
        self,
        text: str
    ) -> Dict[int, int]:
        """
        Get token frequency in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary mapping token ID to count
        """
        tokens = self._model.tokenize(text)
        frequency: Dict[int, int] = {}

        for token_id in tokens:
            frequency[token_id] = frequency.get(token_id, 0) + 1

        return frequency

    def find_repetitions(
        self,
        text: str,
        min_length: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find repeating token sequences.

        Args:
            text: Text to analyze
            min_length: Minimum sequence length

        Returns:
            List of repeating sequences
        """
        tokens = self._model.tokenize(text)
        repetitions = []

        # Find repeated n-grams
        for n in range(min_length, len(tokens) // 2 + 1):
            seen = {}
            for i in range(len(tokens) - n + 1):
                ngram = tuple(tokens[i:i + n])
                if ngram in seen:
                    if seen[ngram] not in [r['start'] for r in repetitions if r['length'] == n]:
                        repetitions.append({
                            'length': n,
                            'start': seen[ngram],
                            'repeat_start': i,
                            'tokens': list(ngram),
                            'decoded': self._model.detokenize(list(ngram)),
                        })
                else:
                    seen[ngram] = i

        return repetitions


def check_device_health(device: 'Device') -> Dict[str, Any]:
    """
    Check device health status.

    Args:
        device: Device to check

    Returns:
        Health status dictionary
    """
    info = device.info()

    issues = []

    # Check temperature
    if info.temperature_celsius > 70:
        issues.append({
            'level': 'warning',
            'message': f"High temperature: {info.temperature_celsius}°C",
        })
    elif info.temperature_celsius > 80:
        issues.append({
            'level': 'critical',
            'message': f"Critical temperature: {info.temperature_celsius}°C",
        })

    # Check power
    if info.power_watts > 3.5:
        issues.append({
            'level': 'warning',
            'message': f"High power consumption: {info.power_watts}W",
        })

    # Check cartridge
    if not info.cartridge_inserted:
        issues.append({
            'level': 'info',
            'message': "No cartridge inserted",
        })

    return {
        'healthy': len([i for i in issues if i['level'] == 'critical']) == 0,
        'device_type': info.device_type.value,
        'temperature_celsius': info.temperature_celsius,
        'power_watts': info.power_watts,
        'issues': issues,
    }


def enable_verbose_logging() -> None:
    """Enable verbose logging for debugging."""
    import logging

    # Configure logging for the superinstance package
    logger = logging.getLogger('superinstance')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.debug("Verbose logging enabled")


def disable_verbose_logging() -> None:
    """Disable verbose logging."""
    import logging

    logger = logging.getLogger('superinstance')
    logger.setLevel(logging.WARNING)
