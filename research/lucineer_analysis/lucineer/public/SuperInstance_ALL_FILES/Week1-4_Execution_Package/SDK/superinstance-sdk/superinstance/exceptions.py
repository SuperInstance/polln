"""
SuperInstance SDK Exceptions

Custom exceptions for the SuperInstance SDK.
"""


class SuperInstanceError(Exception):
    """Base exception for all SuperInstance SDK errors."""
    pass


class DeviceNotFoundError(SuperInstanceError):
    """Raised when no SuperInstance device is detected."""

    def __init__(self, message: str = "No SuperInstance device found. Please ensure the device is connected via USB."):
        self.message = message
        super().__init__(self.message)


class DeviceBusyError(SuperInstanceError):
    """Raised when the device is in use by another process."""

    def __init__(self, message: str = "Device is busy. Another process is using this device."):
        self.message = message
        super().__init__(self.message)


class DeviceConnectionError(SuperInstanceError):
    """Raised when connection to the device fails."""

    def __init__(self, message: str = "Failed to connect to device. Check USB connection."):
        self.message = message
        super().__init__(self.message)


class DeviceClosedError(SuperInstanceError):
    """Raised when trying to use a closed device."""

    def __init__(self, message: str = "Device has been closed. Create a new Device instance to continue."):
        self.message = message
        super().__init__(self.message)


class NoCartridgeError(SuperInstanceError):
    """Raised when no cartridge is inserted in the device."""

    def __init__(self, message: str = "No cartridge inserted. Please insert a model module."):
        self.message = message
        super().__init__(self.message)


class CartridgeReadError(SuperInstanceError):
    """Raised when reading cartridge data fails."""

    def __init__(self, message: str = "Failed to read cartridge. Cartridge may be damaged."):
        self.message = message
        super().__init__(self.message)


class IncompatibleModelError(SuperInstanceError):
    """Raised when the model requires newer firmware."""

    def __init__(self, message: str = "Model incompatible with device firmware. Please update firmware."):
        self.message = message
        super().__init__(self.message)


class GenerationError(SuperInstanceError):
    """Raised when text generation fails."""

    def __init__(self, message: str = "Generation failed. Check device status and try again."):
        self.message = message
        super().__init__(self.message)


class ContextLengthExceededError(SuperInstanceError):
    """Raised when prompt exceeds maximum context length."""

    def __init__(self, tokens: int, max_tokens: int, message: str = None):
        self.tokens = tokens
        self.max_tokens = max_tokens
        if message is None:
            message = f"Prompt has {tokens} tokens, exceeds maximum of {max_tokens}."
        self.message = message
        super().__init__(self.message)


class InvalidMessageFormatError(SuperInstanceError):
    """Raised when chat message format is invalid."""

    def __init__(self, message: str = "Invalid message format. Expected list of dicts with 'role' and 'content'."):
        self.message = message
        super().__init__(self.message)


class FeatureNotSupportedError(SuperInstanceError):
    """Raised when a feature is not supported by the device."""

    def __init__(self, feature: str, device_type: str):
        self.feature = feature
        self.device_type = device_type
        self.message = f"Feature '{feature}' not supported on {device_type} device."
        super().__init__(self.message)
