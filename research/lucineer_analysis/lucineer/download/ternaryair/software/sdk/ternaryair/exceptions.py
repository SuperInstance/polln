"""
Custom exceptions for TernaryAir SDK.
"""

from typing import Optional


class TernaryAirError(Exception):
    """Base exception for all TernaryAir errors."""
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class DeviceNotFoundError(TernaryAirError):
    """Raised when no TernaryAir device is found."""
    
    def __init__(self, message: str = "No TernaryAir device found", 
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class ConnectionError(TernaryAirError):
    """Raised when connection to device fails."""
    
    def __init__(self, message: str = "Failed to connect to device",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class InferenceError(TernaryAirError):
    """Raised when inference fails."""
    
    def __init__(self, message: str = "Inference failed",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class TimeoutError(TernaryAirError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str = "Operation timed out",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class BufferOverflowError(TernaryAirError):
    """Raised when the device buffer overflows."""
    
    def __init__(self, message: str = "Device buffer overflow",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class SequenceTooLongError(TernaryAirError):
    """Raised when the input sequence is too long."""
    
    def __init__(self, message: str = "Sequence too long",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class ThermalThrottlingError(TernaryAirError):
    """Raised when the device is thermal throttling."""
    
    def __init__(self, message: str = "Device is thermal throttling",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)


class PowerLimitError(TernaryAirError):
    """Raised when power limit is exceeded."""
    
    def __init__(self, message: str = "Power limit exceeded",
                 details: Optional[str] = None) -> None:
        super().__init__(message, details)
