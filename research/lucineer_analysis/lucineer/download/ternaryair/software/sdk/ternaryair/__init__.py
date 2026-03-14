"""
TernaryAir - Open Source Air-Gapped Ternary Inference Hardware SDK

This package provides a Python interface for TernaryAir hardware devices
and a software simulator for development and testing.

Example:
    >>> from ternaryair import TernaryAir
    >>> device = TernaryAir()
    >>> response = device.generate("Hello, world!")
    >>> print(response)
"""

from ternaryair.device import TernaryAir, DeviceInfo, DeviceStatus
from ternaryair.simulator import Simulator
from ternaryair.config import Config
from ternaryair.exceptions import (
    TernaryAirError,
    DeviceNotFoundError,
    ConnectionError,
    InferenceError,
)

__version__ = "1.0.0"
__author__ = "Casey DiGennaro"
__email__ = "casey@superinstance.ai"
__license__ = "MIT"

__all__ = [
    # Main classes
    "TernaryAir",
    "Simulator",
    "Config",
    # Data classes
    "DeviceInfo",
    "DeviceStatus",
    # Exceptions
    "TernaryAirError",
    "DeviceNotFoundError",
    "ConnectionError",
    "InferenceError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
