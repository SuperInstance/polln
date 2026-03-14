"""
SuperInstance SDK - Custom Exceptions

This module defines all custom exceptions used throughout the SuperInstance SDK.
All exceptions inherit from SuperInstanceError for easy catching.
"""


class SuperInstanceError(Exception):
    """Base exception for all SuperInstance SDK errors."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


# =============================================================================
# Device Errors
# =============================================================================

class DeviceError(SuperInstanceError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """No SuperInstance device detected."""

    def __init__(self, message: str = "No SuperInstance device found", details: str = None):
        super().__init__(message, details)


class DeviceBusyError(DeviceError):
    """Device is in use by another process."""

    def __init__(self, message: str = "Device is busy", details: str = None):
        super().__init__(message, details)


class DeviceConnectionError(DeviceError):
    """Failed to establish connection to device."""

    def __init__(self, message: str = "Failed to connect to device", details: str = None):
        super().__init__(message, details)


class DeviceClosedError(DeviceError):
    """Operation on closed device."""

    def __init__(self, message: str = "Device has been closed", details: str = None):
        super().__init__(message, details)


class DeviceResetError(DeviceError):
    """Device reset failed."""

    def __init__(self, message: str = "Device reset failed", details: str = None):
        super().__init__(message, details)


# =============================================================================
# Cartridge Errors
# =============================================================================

class CartridgeError(SuperInstanceError):
    """Base exception for cartridge-related errors."""
    pass


class NoCartridgeError(CartridgeError):
    """No cartridge inserted."""

    def __init__(self, message: str = "No cartridge inserted", details: str = None):
        super().__init__(message, details)


class CartridgeReadError(CartridgeError):
    """Failed to read cartridge data."""

    def __init__(self, message: str = "Failed to read cartridge", details: str = None):
        super().__init__(message, details)


# =============================================================================
# Model Errors
# =============================================================================

class ModelError(SuperInstanceError):
    """Base exception for model-related errors."""
    pass


class ModelLoadError(ModelError):
    """Failed to load model."""

    def __init__(self, message: str = "Failed to load model", details: str = None):
        super().__init__(message, details)


class IncompatibleModelError(ModelError):
    """Model incompatible with device/firmware."""

    def __init__(self, message: str = "Model is incompatible", details: str = None):
        super().__init__(message, details)


class ContextLengthExceededError(ModelError):
    """Prompt exceeds context length."""

    def __init__(self, tokens: int, max_tokens: int):
        message = f"Context length exceeded: {tokens} tokens > {max_tokens} max"
        super().__init__(message)
        self.tokens = tokens
        self.max_tokens = max_tokens


class GenerationError(ModelError):
    """Generation failed."""

    def __init__(self, message: str = "Generation failed", details: str = None):
        super().__init__(message, details)


class InvalidMessageFormatError(ModelError):
    """Invalid chat message format."""

    def __init__(self, message: str = "Invalid message format", details: str = None):
        super().__init__(message, details)


# =============================================================================
# Feature Errors
# =============================================================================

class FeatureNotSupportedError(SuperInstanceError):
    """Feature not supported by device edition."""

    def __init__(self, feature: str, edition: str = None):
        message = f"Feature '{feature}' is not supported"
        details = f"Requires {edition} edition" if edition else None
        super().__init__(message, details)
        self.feature = feature
        self.edition = edition


# =============================================================================
# Firmware Errors
# =============================================================================

class FirmwareError(SuperInstanceError):
    """Base exception for firmware-related errors."""
    pass


class FirmwareUpdateError(FirmwareError):
    """Firmware update failed."""

    def __init__(self, message: str = "Firmware update failed", details: str = None):
        super().__init__(message, details)


class FirmwareVersionError(FirmwareError):
    """Firmware version incompatible."""

    def __init__(self, message: str = "Incompatible firmware version", details: str = None):
        super().__init__(message, details)


# =============================================================================
# Profiler Errors
# =============================================================================

class ProfilerError(SuperInstanceError):
    """Base exception for profiler-related errors."""
    pass


class ProfilerNotRunningError(ProfilerError):
    """Profiler is not running."""

    def __init__(self):
        super().__init__("Profiler is not running")


# =============================================================================
# Export all exceptions
# =============================================================================

__all__ = [
    # Base
    'SuperInstanceError',

    # Device
    'DeviceError',
    'DeviceNotFoundError',
    'DeviceBusyError',
    'DeviceConnectionError',
    'DeviceClosedError',
    'DeviceResetError',

    # Cartridge
    'CartridgeError',
    'NoCartridgeError',
    'CartridgeReadError',

    # Model
    'ModelError',
    'ModelLoadError',
    'IncompatibleModelError',
    'ContextLengthExceededError',
    'GenerationError',
    'InvalidMessageFormatError',

    # Feature
    'FeatureNotSupportedError',

    # Firmware
    'FirmwareError',
    'FirmwareUpdateError',
    'FirmwareVersionError',

    # Profiler
    'ProfilerError',
    'ProfilerNotRunningError',
]
