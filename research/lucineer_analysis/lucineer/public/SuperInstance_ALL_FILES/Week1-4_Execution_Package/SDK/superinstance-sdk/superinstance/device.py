"""
SuperInstance SDK Device Module

Device detection, connection management, and model loading.
"""

import os
import time
import platform
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from superinstance.model import Model

from superinstance.exceptions import (
    DeviceNotFoundError,
    DeviceBusyError,
    DeviceConnectionError,
    DeviceClosedError,
    NoCartridgeError,
    CartridgeReadError,
    IncompatibleModelError,
    FeatureNotSupportedError,
)


class DeviceType(Enum):
    """SuperInstance device types."""
    NANO = "nano"
    STANDARD = "standard"
    PRO = "pro"
    MAKER_EDITION = "maker"


@dataclass
class DeviceInfo:
    """
    Device information structure.

    Contains metadata about the connected SuperInstance device,
    including hardware status and cartridge information.
    """

    device_type: DeviceType
    firmware_version: str
    serial_number: str
    cartridge_inserted: bool
    cartridge_model: Optional[str] = None
    cartridge_version: Optional[str] = None
    temperature_celsius: float = 0.0
    power_watts: float = 0.0
    uptime_seconds: int = 0
    total_inferences: int = 0
    total_tokens_generated: int = 0
    usb_speed: str = "usb3.0"

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "device_type": self.device_type.value,
            "firmware_version": self.firmware_version,
            "serial_number": self.serial_number,
            "cartridge_inserted": self.cartridge_inserted,
            "cartridge_model": self.cartridge_model,
            "cartridge_version": self.cartridge_version,
            "temperature_celsius": self.temperature_celsius,
            "power_watts": self.power_watts,
            "uptime_seconds": self.uptime_seconds,
            "total_inferences": self.total_inferences,
            "total_tokens_generated": self.total_tokens_generated,
            "usb_speed": self.usb_speed,
        }

    def __str__(self) -> str:
        """Human-readable device summary."""
        lines = [
            "┌─────────────────────────────────────────┐",
            f"│ SuperInstance {self.device_type.value.upper():24s} │",
            f"│ Serial: {self.serial_number:31s} │",
            f"│ Firmware: {self.firmware_version:30s} │",
            f"│ USB: {self.usb_speed:33s} │",
            "├─────────────────────────────────────────┤",
        ]

        if self.cartridge_inserted and self.cartridge_model:
            lines.append(f"│ Cartridge: {self.cartridge_model:28s} │")
            if self.cartridge_version:
                lines.append(f"│ Version: {self.cartridge_version:30s} │")
        else:
            lines.append("│ Cartridge: None                         │")

        lines.extend([
            f"│ Temperature: {self.temperature_celsius:.1f}°C{' ':22s} │",
            f"│ Power: {self.power_watts:.1f}W{' ':28s} │",
            f"│ Uptime: {self._format_uptime():30s} │",
            f"│ Inferences: {self.total_inferences:,}{' ':24s} │",
            f"│ Tokens: {self.total_tokens_generated:,}{' ':27s} │",
            "└─────────────────────────────────────────┘",
        ])
        return "\n".join(lines)

    def _format_uptime(self) -> str:
        """Format uptime in human-readable format."""
        seconds = self.uptime_seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class Device:
    """
    Represents a SuperInstance inference device.

    The Device class is the main entry point for interacting with
    SuperInstance hardware. It provides methods for device detection,
    connection management, and model loading.

    Example:
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> result = model.generate("Hello")
    """

    # Class-level registry of connected devices
    _connected_devices: dict = {}

    def __init__(
        self,
        device_path: Optional[str] = None,
        device_index: Optional[int] = None,
        timeout_ms: int = 5000
    ):
        """
        Connect to a SuperInstance device.

        Args:
            device_path: Specific device path to connect to.
                        If None, auto-detects first available device.
            device_index: Index of device to connect to (0-based).
                         If both path and index are None, auto-detects.
            timeout_ms: Connection timeout in milliseconds.
                       Default: 5000ms

        Raises:
            DeviceNotFoundError: No SuperInstance device detected
            DeviceBusyError: Device is in use by another process
            DeviceConnectionError: Failed to establish connection
        """
        self._closed = False
        self._device_path: Optional[str] = None
        self._timeout_ms = timeout_ms
        self._info: Optional[DeviceInfo] = None
        self._model: Optional["Model"] = None

        # Determine device path
        if device_path is not None:
            self._device_path = device_path
        elif device_index is not None:
            devices = self.list_devices()
            if device_index >= len(devices):
                raise DeviceNotFoundError(
                    f"Device index {device_index} out of range. "
                    f"Found {len(devices)} device(s)."
                )
            self._device_path = devices[device_index]
        else:
            # Auto-detect first available device
            devices = self.list_devices()
            if not devices:
                raise DeviceNotFoundError()
            self._device_path = devices[0]

        # Check if device is already in use
        if self._device_path in self._connected_devices:
            raise DeviceBusyError(
                f"Device {self._device_path} is already in use."
            )

        # Connect to device
        self._connect()

        # Register this device
        self._connected_devices[self._device_path] = self

    @staticmethod
    def list_devices() -> List[str]:
        """
        List available device paths.

        Returns:
            List of device path strings (e.g., ['/dev/superinstance0'])

        Example:
            >>> devices = Device.list_devices()
            >>> if not devices:
            ...     print("No SuperInstance devices found")
        """
        devices = []

        system = platform.system()

        if system == "Linux":
            # Check for USB serial devices or hidraw devices
            for i in range(16):
                paths = [
                    f"/dev/superinstance{i}",
                    f"/dev/hidraw{i}",
                ]
                for path in paths:
                    if os.path.exists(path):
                        devices.append(path)

            # Also check USB serial devices with our VID:PID
            for i in range(256):
                tty_path = f"/dev/ttyUSB{i}"
                if os.path.exists(tty_path):
                    # In production, we'd check VID:PID here
                    # For now, add as potential device
                    pass

        elif system == "Darwin":  # macOS
            # Check for USB serial devices
            for i in range(256):
                paths = [
                    f"/dev/tty.usbserial-{i}",
                    f"/dev/cu.usbserial-{i}",
                    f"/dev/tty.SuperInstance{i}",
                    f"/dev/cu.SuperInstance{i}",
                ]
                for path in paths:
                    if os.path.exists(path):
                        devices.append(path)

            # Check for HID devices
            hid_path = "/dev/hid"
            if os.path.exists(hid_path):
                for entry in os.listdir(hid_path):
                    devices.append(os.path.join(hid_path, entry))

        elif system == "Windows":
            # On Windows, we'd use pywin32 to enumerate USB devices
            # For the skeleton, we'll check for COM ports
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            for port in ports:
                # In production, check VID:PID = 0x???? : 0x????
                # For now, we'll simulate finding our devices
                if "SuperInstance" in port.description or "USB Serial" in port.description:
                    devices.append(port.device)

        # For development/demo purposes, add a simulated device if none found
        if not devices:
            # Check for SIMULATION environment variable
            if os.environ.get("SUPERINSTANCE_SIMULATE", "0") == "1":
                devices.append("/dev/superinstance-sim0")

        return devices

    def _connect(self) -> None:
        """
        Establish connection to the device.

        In production, this would:
        - Open the USB device
        - Initialize the communication protocol
        - Read device information

        For the skeleton, we simulate this.
        """
        if self._simulate_mode():
            # Simulated connection
            self._info = DeviceInfo(
                device_type=DeviceType.PRO,
                firmware_version="1.0.0",
                serial_number="SI-PRO-2026-DEMO",
                cartridge_inserted=True,
                cartridge_model="bitnet-2b-chat",
                cartridge_version="1.0.0",
                temperature_celsius=42.3,
                power_watts=2.1,
                uptime_seconds=12462,
                total_inferences=1247,
                total_tokens_generated=312450,
                usb_speed="usb4",
            )
        else:
            # Real device connection would happen here
            # For now, raise error if not simulated
            raise DeviceConnectionError(
                "No physical device found. Set SUPERINSTANCE_SIMULATE=1 "
                "environment variable to use simulation mode."
            )

    def _simulate_mode(self) -> bool:
        """Check if running in simulation mode."""
        return (
            os.environ.get("SUPERINSTANCE_SIMULATE", "0") == "1" or
            "sim" in (self._device_path or "")
        )

    def info(self) -> DeviceInfo:
        """
        Get device information.

        Returns:
            DeviceInfo object containing device metadata.

        Raises:
            DeviceClosedError: Device has been closed

        Example:
            >>> info = device.info()
            >>> print(f"Temperature: {info.temperature_celsius}°C")
        """
        self._check_not_closed()

        # Update dynamic values in simulation
        if self._simulate_mode() and self._info:
            # Simulate some activity
            import random
            self._info.temperature_celsius = 40.0 + random.uniform(0, 5)
            self._info.power_watts = 1.5 + random.uniform(0, 1.5)

        return self._info

    def load_cartridge(self) -> "Model":
        """
        Load model from inserted cartridge.

        The device must have a cartridge inserted. The model is loaded
        from the cartridge's mask-locked weights and onboard memory.

        Returns:
            Model object ready for inference.

        Raises:
            DeviceClosedError: Device has been closed
            NoCartridgeError: No cartridge inserted
            CartridgeReadError: Failed to read cartridge data
            IncompatibleModelError: Cartridge requires newer firmware

        Example:
            >>> model = device.load_cartridge()
            >>> print(f"Loaded model: {model.name}")
        """
        self._check_not_closed()

        if not self._info or not self._info.cartridge_inserted:
            raise NoCartridgeError()

        # Import here to avoid circular import
        from superinstance.model import Model

        self._model = Model(device=self, simulate=self._simulate_mode())
        return self._model

    def load_model(self, path: str) -> "Model":
        """
        Load model from file path.

        This method is only available on Pro and Maker Edition devices.
        It allows loading custom model modules from storage.

        Args:
            path: Path to model module file (.simod)

        Returns:
            Model object ready for inference.

        Raises:
            DeviceClosedError: Device has been closed
            FeatureNotSupportedError: Device doesn't support custom models
            FileNotFoundError: Model file not found

        Availability:
            Pro Edition, Maker Edition only
        """
        self._check_not_closed()

        # Check device type
        if self._info and self._info.device_type not in (DeviceType.PRO, DeviceType.MAKER_EDITION):
            raise FeatureNotSupportedError(
                "custom model loading",
                self._info.device_type.value
            )

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        from superinstance.model import Model
        self._model = Model(device=self, model_path=path, simulate=self._simulate_mode())
        return self._model

    def reset(self) -> None:
        """
        Reset device to initial state.

        Clears all cached data and resets hardware state. The device
        remains connected after reset.

        Raises:
            DeviceClosedError: Device has been closed
        """
        self._check_not_closed()

        if self._model:
            self._model._reset()
            self._model = None

        # Reset would happen here on real device
        if self._simulate_mode() and self._info:
            self._info.total_inferences = 0
            self._info.total_tokens_generated = 0

    def close(self) -> None:
        """
        Release device resources.

        Should be called when done using the device. Using the device
        after close() will raise DeviceClosedError.

        Example:
            >>> device = Device()
            >>> # ... use device ...
            >>> device.close()
        """
        if self._closed:
            return

        if self._model:
            self._model._reset()

        if self._device_path and self._device_path in self._connected_devices:
            del self._connected_devices[self._device_path]

        self._closed = True

    def _check_not_closed(self) -> None:
        """Check that device is not closed, raise if it is."""
        if self._closed:
            raise DeviceClosedError()

    def __enter__(self) -> "Device":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - automatically closes device."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        if self._closed:
            return "<Device [closed]>"

        device_type = self._info.device_type.value if self._info else "unknown"
        path = self._device_path or "unknown"
        return f"<Device type={device_type} path={path}>"
