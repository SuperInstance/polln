"""
Tests for Device module.
"""

import pytest
from superinstance import Device, DeviceType, DeviceInfo
from superinstance.errors import DeviceNotFoundError, DeviceClosedError


class TestDeviceDetection:
    """Tests for device detection."""

    def test_list_devices_returns_list(self):
        """list_devices should return a list."""
        devices = Device.list_devices()
        assert isinstance(devices, list)

    def test_list_devices_not_empty_in_simulation(self):
        """In simulation mode, there should be at least one device."""
        devices = Device.list_devices()
        assert len(devices) >= 1


class TestDeviceConnection:
    """Tests for device connection."""

    def test_auto_connect(self):
        """Should auto-connect to first available device."""
        device = Device()
        assert device is not None

    def test_device_info(self):
        """Should return device info."""
        device = Device()
        info = device.info()
        assert isinstance(info, DeviceInfo)
        assert info.device_type in list(DeviceType)
        assert info.firmware_version is not None

    def test_device_context_manager(self):
        """Context manager should work correctly."""
        with Device() as device:
            info = device.info()
            assert info is not None

    def test_device_close(self):
        """Closing device should work."""
        device = Device()
        info = device.info()  # Should work
        device.close()
        with pytest.raises(DeviceClosedError):
            device.info()  # Should fail after close

    def test_device_repr(self):
        """Repr should be informative."""
        device = Device()
        repr_str = repr(device)
        assert "SuperInstance" in repr_str
        assert "open" in repr_str or "closed" in repr_str


class TestDeviceInfo:
    """Tests for DeviceInfo."""

    def test_device_info_to_dict(self):
        """to_dict should return a dictionary."""
        device = Device()
        info = device.info()
        d = info.to_dict()
        assert isinstance(d, dict)
        assert 'device_type' in d
        assert 'firmware_version' in d

    def test_device_info_str(self):
        """String representation should be formatted."""
        device = Device()
        info = device.info()
        s = str(info)
        assert "SuperInstance" in s
        assert "Temperature" in s


class TestCartridge:
    """Tests for cartridge loading."""

    def test_load_cartridge(self):
        """Should load a cartridge."""
        device = Device()
        model = device.load_cartridge()
        assert model is not None
        assert model.name is not None

    def test_load_cartridge_returns_model(self):
        """load_cartridge should return a Model instance."""
        from superinstance import Model
        device = Device()
        model = device.load_cartridge()
        assert isinstance(model, Model)
