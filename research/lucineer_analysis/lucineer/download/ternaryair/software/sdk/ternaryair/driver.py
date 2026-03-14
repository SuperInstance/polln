"""
USB driver for TernaryAir hardware.
"""

from __future__ import annotations

import struct
import time
from typing import Generator, Optional

from ternaryair.config import Config
from ternaryair.device import Backend, DeviceInfo, DeviceStatus
from ternaryair.exceptions import ConnectionError, DeviceNotFoundError

# USB identifiers
VENDOR_ID = 0x1A86  # TernaryAir vendor ID
PRODUCT_ID = 0x7523  # TernaryAir product ID

# Command codes
CMD_INFERENCE_START = 0x01
CMD_INFERENCE_TOKEN = 0x02
CMD_INFERENCE_END = 0x03
CMD_GET_STATUS = 0x04
CMD_GET_TEMPERATURE = 0x05
CMD_SET_MAX_TOKENS = 0x06
CMD_RESET = 0xFF

# Response codes
RESP_SUCCESS = 0x00000000
RESP_BUFFER_OVERFLOW = 0x00000001
RESP_SEQUENCE_TOO_LONG = 0x00000002
RESP_THERMAL_THROTTLING = 0x00000003
RESP_POWER_LIMIT = 0x00000004


class HardwareBackend(Backend):
    """Hardware backend for TernaryAir device.
    
    This class provides the low-level USB interface to TernaryAir
    hardware devices.
    
    Args:
        config: Device configuration.
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize hardware backend."""
        self._config = config
        self._device = None
        self._connected = False
        self._info: Optional[DeviceInfo] = None
    
    def connect(self) -> None:
        """Connect to hardware device."""
        try:
            import usb.core
            import usb.util
        except ImportError:
            raise ConnectionError(
                "USB library not installed",
                "Install with: pip install pyusb"
            )
        
        # Find device
        device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if device is None:
            raise DeviceNotFoundError(
                "No TernaryAir device found",
                "Check that the device is connected and drivers are installed"
            )
        
        self._device = device
        
        # Configure device
        try:
            if self._device.is_kernel_driver_active(0):
                self._device.detach_kernel_driver(0)
            usb.util.claim_interface(self._device, 0)
        except Exception as e:
            raise ConnectionError("Failed to claim USB interface", str(e))
        
        self._connected = True
        self._info = DeviceInfo(
            model="TernaryAir-350M",
            firmware_version=self._get_firmware_version(),
            serial_number=self._get_serial(),
        )
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self._device:
            try:
                import usb.util
                usb.util.release_interface(self._device, 0)
            except Exception:
                pass
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    def get_info(self) -> DeviceInfo:
        """Get device info."""
        if not self._info:
            raise ConnectionError("Not connected")
        return self._info
    
    def get_status(self) -> DeviceStatus:
        """Get device status."""
        if not self._connected:
            raise ConnectionError("Not connected")
        
        # Query device status
        response = self._send_command(CMD_GET_STATUS)
        
        # Parse response
        is_ready = response[0] != 0
        temperature = struct.unpack('<H', response[1:3])[0] / 10.0
        power = struct.unpack('<H', response[3:5])[0] / 100.0
        tokens = struct.unpack('<I', response[5:9])[0]
        inferences = struct.unpack('<I', response[9:13])[0]
        uptime = struct.unpack('<I', response[13:17])[0] / 1000.0
        
        return DeviceStatus(
            is_ready=is_ready,
            temperature_c=temperature,
            power_w=power,
            tokens_generated=tokens,
            inference_count=inferences,
            uptime_s=uptime,
        )
    
    def infer(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repeat_penalty: float,
    ) -> str:
        """Run inference."""
        if not self._connected:
            raise ConnectionError("Not connected")
        
        # Start inference session
        self._send_command(CMD_INFERENCE_START, struct.pack('<H', max_tokens))
        
        # Send prompt in chunks
        prompt_bytes = prompt.encode('utf-8')
        for i in range(0, len(prompt_bytes), 64):
            chunk = prompt_bytes[i:i+64]
            self._send_command(CMD_INFERENCE_TOKEN, chunk)
        
        # End prompt and wait for response
        response = self._send_command(CMD_INFERENCE_END)
        
        return response.decode('utf-8')
    
    def stream(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repeat_penalty: float,
    ) -> Generator[str, None, None]:
        """Stream inference output."""
        # For streaming, we run inference and then parse tokens
        # In a real implementation, the hardware would support token-by-token output
        result = self.infer(
            prompt, max_tokens, temperature, top_p, top_k, repeat_penalty
        )
        
        # Yield word by word
        for word in result.split():
            yield word + " "
    
    def _send_command(self, cmd: int, data: bytes = b'') -> bytes:
        """Send command to device and get response."""
        if not self._device:
            raise ConnectionError("Not connected")
        
        # Build command packet
        packet = struct.pack('<II', cmd, len(data)) + data
        
        # Send to device
        self._device.write(0x02, packet, timeout=int(self._config.timeout * 1000))
        
        # Read response
        response = self._device.read(0x81, 4096, timeout=int(self._config.timeout * 1000))
        
        # Parse response header
        resp_cmd, status, length = struct.unpack('<III', response[:12])
        
        if status != RESP_SUCCESS:
            self._handle_error(status)
        
        return response[12:12+length]
    
    def _handle_error(self, status: int) -> None:
        """Handle device error codes."""
        from ternaryair.exceptions import (
            BufferOverflowError,
            SequenceTooLongError,
            ThermalThrottlingError,
            PowerLimitError,
        )
        
        error_map = {
            RESP_BUFFER_OVERFLOW: BufferOverflowError,
            RESP_SEQUENCE_TOO_LONG: SequenceTooLongError,
            RESP_THERMAL_THROTTLING: ThermalThrottlingError,
            RESP_POWER_LIMIT: PowerLimitError,
        }
        
        error_class = error_map.get(status, ConnectionError)
        raise error_class()
    
    def _get_firmware_version(self) -> str:
        """Get firmware version from device."""
        try:
            # Read from device descriptor
            if self._device:
                return f"{self._device.bcdDevice >> 8}.{self._device.bcdDevice & 0xFF}"
        except Exception:
            pass
        return "1.0.0"
    
    def _get_serial(self) -> str:
        """Get serial number from device."""
        try:
            if self._device:
                import usb.util
                return usb.util.get_string(self._device, self._device.iSerialNumber)
        except Exception:
            pass
        return "UNKNOWN"
