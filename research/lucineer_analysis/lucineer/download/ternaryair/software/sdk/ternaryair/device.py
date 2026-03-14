"""
TernaryAir device interface.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, List, Optional, Protocol, Union

from ternaryair.config import Config
from ternaryair.exceptions import (
    ConnectionError,
    DeviceNotFoundError,
    InferenceError,
    TimeoutError,
)

if TYPE_CHECKING:
    from ternaryair.simulator import Simulator


@dataclass
class DeviceInfo:
    """Information about a TernaryAir device.
    
    Attributes:
        model: Model name (e.g., "TernaryAir-350M").
        firmware_version: Firmware version string.
        serial_number: Unique device serial number.
        memory_mb: Total on-chip memory in megabytes.
        max_tokens: Maximum context length.
    """
    model: str
    firmware_version: str
    serial_number: str
    memory_mb: int = 512
    max_tokens: int = 4096


@dataclass
class DeviceStatus:
    """Current status of a TernaryAir device.
    
    Attributes:
        is_ready: Whether device is ready for inference.
        temperature_c: Junction temperature in Celsius.
        power_w: Current power consumption in watts.
        tokens_generated: Total tokens generated since boot.
        inference_count: Number of inferences since boot.
        uptime_s: Uptime in seconds.
    """
    is_ready: bool
    temperature_c: float
    power_w: float
    tokens_generated: int
    inference_count: int
    uptime_s: float


class Backend(Protocol):
    """Protocol for TernaryAir backends (hardware or simulator)."""
    
    def connect(self) -> None:
        """Connect to the device."""
        ...
    
    def disconnect(self) -> None:
        """Disconnect from the device."""
        ...
    
    def is_connected(self) -> bool:
        """Check if connected to the device."""
        ...
    
    def get_info(self) -> DeviceInfo:
        """Get device information."""
        ...
    
    def get_status(self) -> DeviceStatus:
        """Get current device status."""
        ...
    
    def infer(self, prompt: str, max_tokens: int, temperature: float,
              top_p: float, top_k: int, repeat_penalty: float) -> str:
        """Run inference."""
        ...
    
    def stream(self, prompt: str, max_tokens: int, temperature: float,
               top_p: float, top_k: int, repeat_penalty: float) -> Generator[str, None, None]:
        """Stream inference output."""
        ...


class TernaryAir:
    """Main interface for TernaryAir inference.
    
    This class provides a high-level interface for running inference on
    TernaryAir hardware devices or software simulators.
    
    Args:
        config: Configuration for the device. Uses defaults if not provided.
        backend: Backend to use (Simulator for software simulation).
        device_path: Direct path to device (overrides config).
    
    Example:
        >>> device = TernaryAir()
        >>> response = device.generate("Hello!")
        >>> print(response)
        
        >>> # With simulator (no hardware needed)
        >>> from ternaryair import Simulator
        >>> device = TernaryAir(backend=Simulator())
        >>> response = device.generate("Hello!")
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        backend: Optional[Union[Simulator, Backend]] = None,
        device_path: Optional[str] = None,
    ) -> None:
        """Initialize TernaryAir interface."""
        self._config = config or Config.default()
        if device_path:
            self._config.device_path = device_path
        
        self._backend: Optional[Backend] = None
        self._conversation_context: List[str] = []
        
        if backend is not None:
            self._backend = backend
            self._backend.connect()
        else:
            self._connect_hardware()
    
    def _connect_hardware(self) -> None:
        """Connect to hardware device."""
        # Try to find and connect to TernaryAir device
        try:
            from ternaryair.driver import HardwareBackend
            self._backend = HardwareBackend(self._config)
            self._backend.connect()
        except ImportError:
            raise DeviceNotFoundError(
                "Hardware driver not available",
                "Install with: pip install ternaryair[hardware]"
            )
        except Exception as e:
            raise ConnectionError("Failed to connect to device", str(e))
    
    def _ensure_connected(self) -> None:
        """Ensure backend is connected."""
        if self._backend is None or not self._backend.is_connected():
            raise ConnectionError("Not connected to device")
    
    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    @property
    def config(self) -> Config:
        """Get current configuration."""
        return self._config
    
    @property
    def info(self) -> DeviceInfo:
        """Get device information."""
        self._ensure_connected()
        return self._backend.get_info()
    
    @property
    def status(self) -> DeviceStatus:
        """Get current device status."""
        self._ensure_connected()
        return self._backend.get_status()
    
    # -------------------------------------------------------------------------
    # Core Methods
    # -------------------------------------------------------------------------
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None,
    ) -> str:
        """Generate text completion for the given prompt.
        
        Args:
            prompt: Input prompt to complete.
            max_tokens: Maximum tokens to generate (uses config default if None).
            temperature: Sampling temperature (uses config default if None).
            top_p: Nucleus sampling probability (uses config default if None).
            top_k: Top-k sampling parameter (uses config default if None).
            repeat_penalty: Penalty for repeated tokens (uses config default if None).
        
        Returns:
            Generated text completion.
        
        Raises:
            ConnectionError: If not connected to device.
            InferenceError: If inference fails.
        
        Example:
            >>> device = TernaryAir()
            >>> response = device.generate("What is AI?", max_tokens=50)
        """
        self._ensure_connected()
        
        # Use config defaults for missing parameters
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        top_p = top_p if top_p is not None else self._config.top_p
        top_k = top_k if top_k is not None else self._config.top_k
        repeat_penalty = repeat_penalty if repeat_penalty is not None else self._config.repeat_penalty
        
        try:
            return self._backend.infer(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
            )
        except Exception as e:
            raise InferenceError("Inference failed", str(e))
    
    def stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """Stream text generation token by token.
        
        Args:
            prompt: Input prompt to complete.
            max_tokens: Maximum tokens to generate (uses config default if None).
            temperature: Sampling temperature (uses config default if None).
            top_p: Nucleus sampling probability (uses config default if None).
            top_k: Top-k sampling parameter (uses config default if None).
            repeat_penalty: Penalty for repeated tokens (uses config default if None).
        
        Yields:
            Generated tokens one at a time.
        
        Example:
            >>> device = TernaryAir()
            >>> for token in device.stream("Tell me a story"):
            ...     print(token, end='', flush=True)
        """
        self._ensure_connected()
        
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        top_p = top_p if top_p is not None else self._config.top_p
        top_k = top_k if top_k is not None else self._config.top_k
        repeat_penalty = repeat_penalty if repeat_penalty is not None else self._config.repeat_penalty
        
        yield from self._backend.stream(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
        )
    
    def batch_generate(
        self,
        prompts: List[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> List[str]:
        """Generate completions for multiple prompts.
        
        Args:
            prompts: List of input prompts.
            max_tokens: Maximum tokens per generation.
            temperature: Sampling temperature.
        
        Returns:
            List of generated completions, one per prompt.
        
        Example:
            >>> device = TernaryAir()
            >>> prompts = ["What is AI?", "What is ML?", "What is DL?"]
            >>> responses = device.batch_generate(prompts)
        """
        results = []
        for prompt in prompts:
            result = self.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            results.append(result)
        return results
    
    # -------------------------------------------------------------------------
    # Conversation Mode
    # -------------------------------------------------------------------------
    
    def conversation(self) -> "Conversation":
        """Start a conversation session.
        
        In conversation mode, the device maintains context between
        messages. Context is lost when the session ends.
        
        Returns:
            Conversation context manager.
        
        Example:
            >>> device = TernaryAir()
            >>> with device.conversation() as chat:
            ...     chat.send("My name is Alice")
            ...     response = chat.send("What's my name?")
            ...     # Device remembers "Alice" from previous message
        """
        return Conversation(self)
    
    # -------------------------------------------------------------------------
    # Context Manager Support
    # -------------------------------------------------------------------------
    
    def __enter__(self) -> "TernaryAir":
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and disconnect."""
        self.disconnect()
    
    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._backend and self._backend.is_connected():
            self._backend.disconnect()
    
    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.disconnect()


class Conversation:
    """Conversation session with context retention.
    
    This class provides a context manager for multi-turn conversations
    where the device remembers previous messages within the session.
    
    Note:
        Context is stored in volatile SRAM and lost when:
        - Session ends (context manager exits)
        - Device loses power
        - reset() is called
    """
    
    def __init__(self, device: TernaryAir) -> None:
        """Initialize conversation session."""
        self._device = device
        self._messages: List[str] = []
    
    def send(
        self,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a message in the conversation.
        
        Args:
            message: Message to send.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
        
        Returns:
            Generated response.
        """
        # Build context from previous messages
        context = "\n".join(self._messages) + "\n" + message if self._messages else message
        
        response = self._device.generate(
            context,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Store this exchange
        self._messages.append(f"User: {message}")
        self._messages.append(f"Assistant: {response}")
        
        return response
    
    def reset(self) -> None:
        """Reset the conversation context."""
        self._messages.clear()
    
    def __enter__(self) -> "Conversation":
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and clear context."""
        self._messages.clear()
