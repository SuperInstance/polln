"""
Unit tests for TernaryAir SDK.
"""

import pytest
from unittest.mock import Mock, patch

from ternaryair import TernaryAir, Simulator, Config
from ternaryair.exceptions import (
    TernaryAirError,
    DeviceNotFoundError,
    ConnectionError,
    InferenceError,
)


class TestConfig:
    """Tests for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.max_tokens == 256
        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.top_k == 40
        assert config.repeat_penalty == 1.1
    
    def test_config_validation_temperature(self):
        """Test temperature validation."""
        with pytest.raises(ValueError):
            Config(temperature=-0.1)
        
        with pytest.raises(ValueError):
            Config(temperature=2.1)
    
    def test_config_validation_top_p(self):
        """Test top_p validation."""
        with pytest.raises(ValueError):
            Config(top_p=-0.1)
        
        with pytest.raises(ValueError):
            Config(top_p=1.1)
    
    def test_config_validation_top_k(self):
        """Test top_k validation."""
        with pytest.raises(ValueError):
            Config(top_k=-1)
    
    def test_config_validation_repeat_penalty(self):
        """Test repeat_penalty validation."""
        with pytest.raises(ValueError):
            Config(repeat_penalty=0.9)
    
    def test_config_presets(self):
        """Test configuration presets."""
        creative = Config.creative()
        assert creative.temperature == 1.0
        
        precise = Config.precise()
        assert precise.temperature == 0.3
        
        deterministic = Config.deterministic()
        assert deterministic.temperature == 0.0
        assert deterministic.top_k == 1


class TestSimulator:
    """Tests for Simulator class."""
    
    def test_connect_disconnect(self):
        """Test connection lifecycle."""
        sim = Simulator()
        
        assert not sim.is_connected()
        
        sim.connect()
        assert sim.is_connected()
        
        sim.disconnect()
        assert not sim.is_connected()
    
    def test_get_info(self):
        """Test device info retrieval."""
        sim = Simulator()
        sim.connect()
        
        info = sim.get_info()
        
        assert info.model == "TernaryAir-350M-SIM"
        assert info.firmware_version == "1.0.0-sim"
        assert info.memory_mb == 512
        assert info.max_tokens == 4096
    
    def test_get_status(self):
        """Test status retrieval."""
        sim = Simulator()
        sim.connect()
        
        status = sim.get_status()
        
        assert status.is_ready
        assert 40.0 <= status.temperature_c <= 50.0
        assert 3.0 <= status.power_w <= 5.0
    
    def test_inference(self):
        """Test inference functionality."""
        sim = Simulator()
        sim.connect()
        
        response = sim.infer(
            prompt="Hello",
            max_tokens=50,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_streaming(self):
        """Test streaming functionality."""
        sim = Simulator()
        sim.connect()
        
        tokens = list(sim.stream(
            prompt="Hello",
            max_tokens=20,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
        ))
        
        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)


class TestTernaryAir:
    """Tests for TernaryAir class."""
    
    def test_initialization_with_simulator(self):
        """Test initialization with simulator backend."""
        device = TernaryAir(backend=Simulator())
        
        assert device._backend is not None
        assert device._backend.is_connected()
    
    def test_generate(self):
        """Test text generation."""
        device = TernaryAir(backend=Simulator())
        
        response = device.generate("Hello, world!")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_with_params(self):
        """Test generation with custom parameters."""
        device = TernaryAir(backend=Simulator())
        
        response = device.generate(
            "Hello",
            max_tokens=50,
            temperature=0.5,
            top_p=0.8,
        )
        
        assert isinstance(response, str)
    
    def test_stream(self):
        """Test streaming generation."""
        device = TernaryAir(backend=Simulator())
        
        tokens = list(device.stream("Hello", max_tokens=20))
        
        assert len(tokens) > 0
    
    def test_batch_generate(self):
        """Test batch generation."""
        device = TernaryAir(backend=Simulator())
        
        prompts = ["Hello", "World", "Test"]
        responses = device.batch_generate(prompts, max_tokens=20)
        
        assert len(responses) == 3
        assert all(isinstance(r, str) for r in responses)
    
    def test_conversation(self):
        """Test conversation mode."""
        device = TernaryAir(backend=Simulator())
        
        with device.conversation() as chat:
            response1 = chat.send("Hello")
            response2 = chat.send("How are you?")
            
            assert isinstance(response1, str)
            assert isinstance(response2, str)
    
    def test_context_manager(self):
        """Test context manager usage."""
        with TernaryAir(backend=Simulator()) as device:
            response = device.generate("Hello")
            assert isinstance(response, str)
        
        # Device should be disconnected after context exit
        assert not device._backend.is_connected()
    
    def test_device_info(self):
        """Test device info property."""
        device = TernaryAir(backend=Simulator())
        
        info = device.info
        
        assert info.model == "TernaryAir-350M-SIM"
    
    def test_device_status(self):
        """Test device status property."""
        device = TernaryAir(backend=Simulator())
        
        status = device.status
        
        assert status.is_ready


class TestExceptions:
    """Tests for exception classes."""
    
    def test_base_exception(self):
        """Test base exception."""
        e = TernaryAirError("Test error")
        assert str(e) == "Test error"
        
        e = TernaryAirError("Test error", "Details here")
        assert "Details here" in str(e)
    
    def test_device_not_found(self):
        """Test DeviceNotFoundError."""
        e = DeviceNotFoundError()
        assert "No TernaryAir device found" in str(e)
    
    def test_connection_error(self):
        """Test ConnectionError."""
        e = ConnectionError("Failed to connect")
        assert "Failed to connect" in str(e)
    
    def test_inference_error(self):
        """Test InferenceError."""
        e = InferenceError("Inference failed")
        assert "Inference failed" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
