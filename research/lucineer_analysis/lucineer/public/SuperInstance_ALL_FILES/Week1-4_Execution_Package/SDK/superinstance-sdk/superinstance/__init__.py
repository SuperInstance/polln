"""
SuperInstance SDK - Hardware for Intelligence

A simple, powerful interface for running large language model (LLM) inference
on SuperInstance mask-locked inference hardware.

Example:
    >>> from superinstance import Device, Model
    >>> device = Device()  # Auto-detect and connect
    >>> model = device.load_cartridge()
    >>> print(model.generate("Hello, I am").text)

License: Apache 2.0
"""

__version__ = "0.1.0"
__author__ = "SuperInstance.AI"
__license__ = "Apache-2.0"

from superinstance.device import Device, DeviceInfo, DeviceType
from superinstance.model import Model, GenerationConfig, GenerationResult
from superinstance.exceptions import (
    SuperInstanceError,
    DeviceNotFoundError,
    DeviceBusyError,
    DeviceConnectionError,
    DeviceClosedError,
    NoCartridgeError,
    CartridgeReadError,
    IncompatibleModelError,
    GenerationError,
    ContextLengthExceededError,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core classes
    "Device",
    "DeviceInfo",
    "DeviceType",
    "Model",
    "GenerationConfig",
    "GenerationResult",
    # Exceptions
    "SuperInstanceError",
    "DeviceNotFoundError",
    "DeviceBusyError",
    "DeviceConnectionError",
    "DeviceClosedError",
    "NoCartridgeError",
    "CartridgeReadError",
    "IncompatibleModelError",
    "GenerationError",
    "ContextLengthExceededError",
]
