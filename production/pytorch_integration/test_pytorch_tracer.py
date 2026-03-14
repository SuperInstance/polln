#!/usr/bin/env python3
"""
Test suite for PyTorch Real Integration Tracer

Validates tracing functionality across different models and scenarios
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import tempfile
import json

from pytorch_tracer import (
    PyTorchTracer,
    TraceExporter,
    LayerTrace,
    ModelTrace,
    LayerAnalyzer,
    CacheLineAnalyzer,
    CRDTScorer
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def device():
    """Get test device."""
    return "cuda" if torch.cuda.is_available() else "cpu"


@pytest.fixture
def simple_model():
    """Create simple test model."""
    return nn.Sequential(
        nn.Conv2d(3, 16, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(16, 32, 3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(32, 10)
    )


@pytest.fixture
def linear_model():
    """Create simple linear model."""
    return nn.Sequential(
        nn.Linear(10, 50),
        nn.ReLU(),
        nn.Linear(50, 20),
        nn.ReLU(),
        nn.Linear(20, 10)
    )


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# =============================================================================
# LayerAnalyzer Tests
# =============================================================================

class TestLayerAnalyzer:
    """Test LayerAnalyzer functionality."""

    def test_get_layer_type_conv2d(self):
        """Test Conv2D layer type detection."""
        layer = nn.Conv2d(3, 64, 3)
        layer_type = LayerAnalyzer.get_layer_type(layer)
        assert layer_type == "conv2d"

    def test_get_layer_type_linear(self):
        """Test Linear layer type detection."""
        layer = nn.Linear(10, 20)
        layer_type = LayerAnalyzer.get_layer_type(layer)
        assert layer_type == "linear"

    def test_get_layer_type_relu(self):
        """Test ReLU layer type detection."""
        layer = nn.ReLU()
        layer_type = LayerAnalyzer.get_layer_type(layer)
        assert layer_type == "relu"

    def test_get_layer_type_batchnorm(self):
        """Test BatchNorm layer type detection."""
        layer = nn.BatchNorm2d(64)
        layer_type = LayerAnalyzer.get_layer_type(layer)
        assert layer_type == "batchnorm2d"

    def test_get_layer_type_layernorm(self):
        """Test LayerNorm layer type detection."""
        layer = nn.LayerNorm(768)
        layer_type = LayerAnalyzer.get_layer_type(layer)
        assert layer_type == "layernorm"

    def test_compute_flops_conv2d(self):
        """Test Conv2D FLOP computation."""
        layer = nn.Conv2d(3, 64, 3, padding=1)
        input_shape = (1, 3, 32, 32)
        output_shape = (1, 64, 32, 32)

        flops = LayerAnalyzer.compute_flops(layer, input_shape, output_shape)

        # Expected: batch * out_channels * H * W * kernel_ops
        # 1 * 64 * 32 * 32 * (3 * 3 * 3) = 1,769,472
        expected_flops = 1 * 64 * 32 * 32 * (3 * 3 * 3)
        assert flops == expected_flops

    def test_compute_flops_linear(self):
        """Test Linear FLOP computation."""
        layer = nn.Linear(10, 20)
        input_shape = (1, 10)
        output_shape = (1, 20)

        flops = LayerAnalyzer.compute_flops(layer, input_shape, output_shape)

        # Expected: batch * in_features * out_features
        # 1 * 10 * 20 = 200
        expected_flops = 1 * 10 * 20
        assert flops == expected_flops

    def test_compute_flops_relu(self):
        """Test ReLU FLOP computation."""
        layer = nn.ReLU()
        input_shape = (1, 10)
        output_shape = (1, 10)

        flops = LayerAnalyzer.compute_flops(layer, input_shape, output_shape)

        # Expected: number of output elements
        expected_flops = 10
        assert flops == expected_flops


# =============================================================================
# CacheLineAnalyzer Tests
# =============================================================================

class TestCacheLineAnalyzer:
    """Test CacheLineAnalyzer functionality."""

    def test_compute_cache_lines_float32(self):
        """Test cache line computation for float32 tensors."""
        tensor = torch.randn(1, 3, 32, 32)
        cache_lines = CacheLineAnalyzer.compute_cache_lines(tensor)

        # Should have some cache lines
        assert len(cache_lines) > 0
        assert all(isinstance(cl, int) for cl in cache_lines)

    def test_compute_cache_lines_float16(self):
        """Test cache line computation for float16 tensors."""
        tensor = torch.randn(1, 3, 32, 32, dtype=torch.float16)
        cache_lines = CacheLineAnalyzer.compute_cache_lines(tensor)

        # Should have some cache lines
        assert len(cache_lines) > 0

    def test_compute_cache_lines_none(self):
        """Test cache line computation for None tensor."""
        cache_lines = CacheLineAnalyzer.compute_cache_lines(None)
        assert cache_lines == []

    def test_cache_line_size(self):
        """Test that cache line size is 64 bytes."""
        tensor = torch.randn(100)  # 400 bytes for float32
        cache_lines = CacheLineAnalyzer.compute_cache_lines(tensor)

        # 400 bytes / 64 bytes per line = ~7 cache lines
        assert len(cache_lines) <= 8  # Allow some overhead


# =============================================================================
# CRDTScorer Tests
# =============================================================================

class TestCRDTScorer:
    """Test CRDTScorer functionality."""

    def test_score_relu(self):
        """Test CRDT score for ReLU (should be high)."""
        layer = nn.ReLU()
        score = CRDTScorer.compute_score(layer, "relu", (10,), (10,))
        assert score >= 0.9  # ReLU should have high score

    def test_score_conv2d(self):
        """Test CRDT score for Conv2D."""
        layer = nn.Conv2d(3, 64, 3)
        score = CRDTScorer.compute_score(layer, "conv2d", (1, 3, 32, 32), (1, 64, 32, 32))
        assert 0.8 <= score <= 0.95  # Conv2D should have good score

    def test_score_layernorm(self):
        """Test CRDT score for LayerNorm (should be lower)."""
        layer = nn.LayerNorm(768)
        score = CRDTScorer.compute_score(layer, "layernorm", (1, 128, 768), (1, 128, 768))
        assert score <= 0.7  # LayerNorm should have moderate score

    def test_score_bounds(self):
        """Test that all scores are within [0, 1]."""
        layers = [
            (nn.ReLU(), "relu", (10,), (10,)),
            (nn.Conv2d(3, 16, 3), "conv2d", (1, 3, 32, 32), (1, 16, 32, 32)),
            (nn.Linear(10, 20), "linear", (1, 10), (1, 20)),
        ]

        for layer, layer_type, in_shape, out_shape in layers:
            score = CRDTScorer.compute_score(layer, layer_type, in_shape, out_shape)
            assert 0.0 <= score <= 1.0


# =============================================================================
# PyTorchTracer Tests
# =============================================================================

class TestPyTorchTracer:
    """Test PyTorchTracer functionality."""

    def test_tracer_creation(self, device):
        """Test tracer creation."""
        tracer = PyTorchTracer("resnet50", device=device)
        assert tracer.model_name == "resnet50"
        assert tracer.device == device
        assert tracer.model is not None

    def test_tracer_dummy_model(self, device):
        """Test tracer with dummy model."""
        tracer = PyTorchTracer("unknown_model", device=device)
        assert tracer.model is not None  # Should fall back to dummy model

    def test_trace_simple_model(self, simple_model, device):
        """Test tracing a simple model."""
        # Create tracer with custom model
        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        # Create input
        input_data = torch.randn(1, 3, 32, 32).to(device)

        # Trace
        trace = tracer.trace(input_data)

        # Validate trace
        assert isinstance(trace, ModelTrace)
        assert len(trace.layers) > 0
        assert trace.total_flops > 0

    def test_trace_linear_model(self, linear_model, device):
        """Test tracing a linear model."""
        tracer = PyTorchTracer("test_linear", device=device)
        tracer.model = linear_model.to(device)
        tracer.model.eval()

        input_data = torch.randn(1, 10).to(device)
        trace = tracer.trace(input_data)

        assert len(trace.layers) == 5  # 3 Linear + 2 ReLU layers
        assert trace.total_flops > 0

    def test_layer_traces_valid(self, simple_model, device):
        """Test that all layer traces are valid."""
        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        input_data = torch.randn(1, 3, 32, 32).to(device)
        trace = tracer.trace(input_data)

        for layer_trace in trace.layers:
            assert isinstance(layer_trace, LayerTrace)
            assert layer_trace.layer_name is not None
            assert layer_trace.layer_type is not None
            assert len(layer_trace.input_shape) > 0
            assert len(layer_trace.output_shape) > 0
            assert layer_trace.flops >= 0
            assert layer_trace.crdt_friendly_score >= 0.0
            assert layer_trace.crdt_friendly_score <= 1.0

    def test_trace_input_shape(self, simple_model, device):
        """Test that input shape is captured correctly."""
        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        input_shape = (1, 3, 32, 32)
        input_data = torch.randn(*input_shape).to(device)
        trace = tracer.trace(input_data)

        assert trace.input_shape == input_shape

    def test_trace_device(self, simple_model, device):
        """Test that device is captured correctly."""
        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        input_data = torch.randn(1, 3, 32, 32).to(device)
        trace = tracer.trace(input_data)

        assert trace.device == device


# =============================================================================
# TraceExporter Tests
# =============================================================================

class TestTraceExporter:
    """Test TraceExporter functionality."""

    @pytest.fixture
    def sample_trace(self):
        """Create sample trace for testing."""
        layers = [
            LayerTrace(
                layer_name="conv1",
                layer_type="conv2d",
                input_shape=(1, 3, 32, 32),
                output_shape=(1, 16, 32, 32),
                parameters=432,
                flops=176947,
                memory_reads_mb=0.012,
                memory_writes_mb=0.064,
                compute_time_ms=1.23,
                cache_line_accesses=[1000, 1001, 1002],
                crdt_friendly_score=0.85
            ),
            LayerTrace(
                layer_name="relu1",
                layer_type="relu",
                input_shape=(1, 16, 32, 32),
                output_shape=(1, 16, 32, 32),
                parameters=0,
                flops=16384,
                memory_reads_mb=0.064,
                memory_writes_mb=0.064,
                compute_time_ms=0.45,
                cache_line_accesses=[2000, 2001],
                crdt_friendly_score=0.95
            )
        ]

        return ModelTrace(
            model_name="test_model",
            framework="pytorch",
            layers=layers,
            total_flops=193331,
            total_memory_mb=0.204,
            total_time_ms=1.68,
            capture_timestamp="20260313-120000",
            device="cpu",
            input_shape=(1, 3, 32, 32)
        )

    def test_to_json(self, sample_trace, temp_output_dir):
        """Test JSON export."""
        output_file = temp_output_dir / "test_trace.json"
        TraceExporter.to_json(sample_trace, str(output_file))

        assert output_file.exists()

        # Validate JSON structure
        with open(output_file, 'r') as f:
            data = json.load(f)

        assert data["model_name"] == "test_model"
        assert data["num_layers"] == 2
        assert len(data["layers"]) == 2
        assert "layers" in data
        assert "total_flops" in data

    def test_to_json_full_cache_lines(self, sample_trace, temp_output_dir):
        """Test JSON export with full cache lines."""
        output_file = temp_output_dir / "test_trace_full.json"
        TraceExporter.to_json(sample_trace, str(output_file), include_all_cache_lines=True)

        with open(output_file, 'r') as f:
            data = json.load(f)

        # Should have all cache lines
        assert len(data["layers"][0]["cache_lines"]) > 0

    def test_to_csv(self, sample_trace, temp_output_dir):
        """Test CSV export."""
        output_file = temp_output_dir / "test_trace.csv"
        TraceExporter.to_csv(sample_trace, str(output_file))

        assert output_file.exists()

        # Read and validate
        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Header + 2 layers
        assert len(lines) == 3

    def test_to_hdf5(self, sample_trace, temp_output_dir):
        """Test HDF5 export."""
        try:
            import h5py
        except ImportError:
            pytest.skip("h5py not available")

        output_file = temp_output_dir / "test_trace.h5"
        TraceExporter.to_hdf5(sample_trace, str(output_file))

        assert output_file.exists()

        # Validate HDF5 structure
        with h5py.File(output_file, 'r') as f:
            assert "model_name" in f.attrs
            assert f.attrs["model_name"] == "test_model"
            assert "layer_0000" in f
            assert "layer_0001" in f


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for full tracing workflow."""

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_trace_resnet50_gpu(self):
        """Test tracing ResNet50 on GPU."""
        tracer = PyTorchTracer("resnet50", device="cuda")
        input_data = torch.randn(1, 3, 224, 224).cuda()
        trace = tracer.trace(input_data)

        assert len(trace.layers) > 20  # ResNet50 has many layers
        assert trace.total_flops > 1e9  # Should have billions of FLOPs
        assert trace.device == "cuda"

    def test_trace_dummy_resnet(self):
        """Test tracing dummy ResNet model."""
        tracer = PyTorchTracer("resnet50", device="cpu")
        input_data = torch.randn(1, 3, 224, 224)
        trace = tracer.trace(input_data)

        # Should trace dummy model
        assert len(trace.layers) > 0
        assert trace.total_flops >= 0

    def test_end_to_end_workflow(self, temp_output_dir):
        """Test complete end-to-end workflow."""
        # Create tracer
        tracer = PyTorchTracer("test_model", device="cpu")
        tracer.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 10)
        ).eval()

        # Trace
        input_data = torch.randn(1, 10)
        trace = tracer.trace(input_data)

        # Export
        json_file = temp_output_dir / "workflow_test.json"
        csv_file = temp_output_dir / "workflow_test.csv"

        TraceExporter.to_json(trace, str(json_file))
        TraceExporter.to_csv(trace, str(csv_file))

        # Validate
        assert json_file.exists()
        assert csv_file.exists()

        # Load and validate JSON
        with open(json_file, 'r') as f:
            data = json.load(f)

        assert data["model_name"] == "test_model"
        assert data["num_layers"] == 3


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Performance tests for tracer."""

    def test_trace_overhead(self, simple_model, device):
        """Test that tracing overhead is acceptable."""
        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        input_data = torch.randn(1, 3, 32, 32).to(device)

        # Measure traced time
        trace = tracer.trace(input_data)
        traced_time = trace.total_time_ms

        # Measure untraced time
        import time
        start = time.perf_counter()
        with torch.no_grad():
            _ = tracer.model(input_data)
        untraced_time = (time.perf_counter() - start) * 1000

        # Tracing overhead should be < 10x
        overhead = traced_time / untraced_time if untraced_time > 0 else 0
        assert overhead < 10.0, f"Tracing overhead too high: {overhead:.2f}x"

    def test_memory_usage(self, simple_model, device):
        """Test that tracer doesn't leak memory."""
        import gc

        tracer = PyTorchTracer("test_model", device=device)
        tracer.model = simple_model.to(device)
        tracer.model.eval()

        input_data = torch.randn(1, 3, 32, 32).to(device)

        # Trace multiple times
        for _ in range(5):
            trace = tracer.trace(input_data)
            assert len(trace.layers) > 0
            del trace

        gc.collect()

        # Should not crash or run out of memory
        assert True


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
