#!/usr/bin/env python3
"""
PyTorch Real Integration - Production Tracer

Captures real workload traces from actual PyTorch models
Replaces synthetic traces with production data

Hardware: RTX 4050 GPU - PyTorch 2.5+, CUDA 13.1

Author: SuperInstance Production Team
Date: 2026-03-13
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
from collections import defaultdict
import numpy as np
import sys

# =============================================================================
# 1. Trace Data Structures
# =============================================================================

@dataclass
class LayerTrace:
    """Trace data for a single layer."""
    layer_name: str
    layer_type: str  # "conv2d", "linear", "attention", etc.
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    parameters: int
    flops: int
    memory_reads_mb: float
    memory_writes_mb: float
    compute_time_ms: float
    cache_line_accesses: List[int] = field(default_factory=list)
    crdt_friendly_score: float = 0.0
    layer_depth: int = 0
    parent_name: str = ""

    def __repr__(self) -> str:
        return (f"LayerTrace(name={self.layer_name}, type={self.layer_type}, "
                f"flops={self.flops:,}, crdt_score={self.crdt_friendly_score:.2f})")


@dataclass
class ModelTrace:
    """Complete trace of model inference."""
    model_name: str
    framework: str  # "pytorch", "tensorflow"
    layers: List[LayerTrace] = field(default_factory=list)
    total_flops: int = 0
    total_memory_mb: float = 0.0
    total_time_ms: float = 0.0
    capture_timestamp: str = ""
    device: str = "cpu"
    input_shape: Tuple[int, ...] = ()

    def add_layer(self, layer: LayerTrace) -> None:
        """Add a layer trace and update totals."""
        self.layers.append(layer)
        self.total_flops += layer.flops
        self.total_memory_mb += (layer.memory_reads_mb + layer.memory_writes_mb)

    def summary(self) -> str:
        """Generate summary string."""
        return (f"ModelTrace({self.model_name}): "
                f"{len(self.layers)} layers, "
                f"{self.total_flops:,} FLOPs, "
                f"{self.total_memory_mb:.2f} MB, "
                f"{self.total_time_ms:.2f} ms")


@dataclass
class CacheLineAccess:
    """Detailed cache line access information."""
    cache_line_addr: int
    access_type: str  # "read", "write", "read_write"
    timestamp_us: float
    layer_name: str
    tensor_size_bytes: int


# =============================================================================
# 2. Layer Type Detectors and FLOP Calculators
# =============================================================================

class LayerAnalyzer:
    """Analyze layer characteristics and compute metrics."""

    LAYER_TYPE_MAP = {
        nn.Conv2d: "conv2d",
        nn.Linear: "linear",
        nn.ReLU: "relu",
        nn.ReLU6: "relu6",
        nn.LeakyReLU: "leaky_relu",
        nn.ELU: "elu",
        nn.GELU: "gelu",
        nn.Sigmoid: "sigmoid",
        nn.Tanh: "tanh",
        nn.Softmax: "softmax",
        nn.BatchNorm1d: "batchnorm1d",
        nn.BatchNorm2d: "batchnorm2d",
        nn.LayerNorm: "layernorm",
        nn.Dropout: "dropout",
        nn.MaxPool2d: "maxpool2d",
        nn.AvgPool2d: "avgpool2d",
        nn.AdaptiveAvgPool2d: "adaptive_avgpool2d",
        nn.Embedding: "embedding",
        nn.Flatten: "flatten",
    }

    @classmethod
    def get_layer_type(cls, layer: nn.Module) -> str:
        """Get layer type string."""
        # Check direct type mapping
        for layer_cls, type_str in cls.LAYER_TYPE_MAP.items():
            if isinstance(layer, layer_cls):
                return type_str

        # Check for attention layers
        if "MultiheadAttention" in str(type(layer)):
            return "multihead_attention"
        if "TransformerEncoderLayer" in str(type(layer)):
            return "transformer_encoder"
        if "TransformerDecoderLayer" in str(type(layer)):
            return "transformer_decoder"

        # Check for specific transformer blocks
        if "BertLayer" in str(type(layer)):
            return "bert_layer"
        if "GPT2Block" in str(type(layer)):
            return "gpt2_block"

        # Default to class name
        return type(layer).__name__

    @classmethod
    def compute_flops(cls, layer: nn.Module, input_shape: Tuple[int, ...],
                     output_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for a layer."""
        layer_type = cls.get_layer_type(layer)

        if isinstance(layer, nn.Conv2d):
            return cls._conv2d_flops(layer, input_shape, output_shape)
        elif isinstance(layer, nn.Linear):
            return cls._linear_flops(layer, input_shape, output_shape)
        elif layer_type in ["relu", "relu6", "leaky_relu", "elu", "gelu", "sigmoid", "tanh"]:
            return cls._activation_flops(output_shape)
        elif isinstance(layer, (nn.BatchNorm1d, nn.BatchNorm2d)):
            return cls._batchnorm_flops(layer, input_shape)
        elif isinstance(layer, nn.LayerNorm):
            return cls._layernorm_flops(layer, input_shape)
        elif "MultiheadAttention" in str(type(layer)):
            return cls._attention_flops(layer, input_shape)
        elif isinstance(layer, nn.Embedding):
            return cls._embedding_flops(layer, input_shape)
        elif isinstance(layer, (nn.MaxPool2d, nn.AvgPool2d)):
            return cls._pool_flops(layer, input_shape, output_shape)
        else:
            # Default estimate
            return 0

    @staticmethod
    def _conv2d_fops(layer: nn.Conv2d, input_shape: Tuple[int, ...],
                    output_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for Conv2D layer."""
        batch_size = input_shape[0]
        output_height = output_shape[2]
        output_width = output_shape[3]
        in_channels = layer.in_channels
        out_channels = layer.out_channels
        kernel_h, kernel_w = layer.kernel_size

        # FLOPs per output element
        flops_per_element = kernel_h * kernel_w * in_channels

        # Total FLOPs
        total_flops = batch_size * out_channels * output_height * output_width * flops_per_element

        # Add bias if present
        if layer.bias is not None:
            total_flops += batch_size * out_channels * output_height * output_width

        return total_flops

    @staticmethod
    def _linear_flops(layer: nn.Linear, input_shape: Tuple[int, ...],
                     output_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for Linear layer."""
        batch_size = input_shape[0]
        in_features = layer.in_features
        out_features = layer.out_features

        # Matrix multiplication: in_features * out_features
        matmul_flops = batch_size * in_features * out_features

        # Add bias if present
        bias_flops = batch_size * out_features if layer.bias is not None else 0

        return matmul_flops + bias_flops

    @staticmethod
    def _activation_flops(output_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for activation layer."""
        return int(np.prod(output_shape))

    @staticmethod
    def _batchnorm_flops(layer: Union[nn.BatchNorm1d, nn.BatchNorm2d],
                        input_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for BatchNorm."""
        # BatchNorm requires 2 operations per element (mean, var)
        return 2 * int(np.prod(input_shape))

    @staticmethod
    def _layernorm_flops(layer: nn.LayerNorm, input_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for LayerNorm."""
        # LayerNorm requires ~5 operations per element
        return 5 * int(np.prod(input_shape))

    @staticmethod
    def _attention_flops(layer: nn.MultiheadAttention,
                        input_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for MultiheadAttention."""
        batch_size, seq_len, embed_dim = input_shape
        num_heads = layer.num_heads
        head_dim = embed_dim // num_heads

        # Q, K, V projections: 3 * seq_len * embed_dim * embed_dim
        qkv_flops = 3 * batch_size * seq_len * embed_dim * embed_dim

        # Attention scores: batch_size * num_heads * seq_len * seq_len * head_dim
        attn_flops = batch_size * num_heads * seq_len * seq_len * head_dim

        # Output projection: batch_size * seq_len * embed_dim * embed_dim
        out_flops = batch_size * seq_len * embed_dim * embed_dim

        return qkv_flops + attn_flops + out_flops

    @staticmethod
    def _embedding_flops(layer: nn.Embedding, input_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for Embedding layer."""
        # Embedding is just lookup, minimal computation
        return int(np.prod(input_shape))

    @staticmethod
    def _pool_flops(layer: Union[nn.MaxPool2d, nn.AvgPool2d],
                   input_shape: Tuple[int, ...],
                   output_shape: Tuple[int, ...]) -> int:
        """Compute FLOPs for Pooling layer."""
        # Pooling requires comparison (max) or averaging
        return int(np.prod(input_shape))


# =============================================================================
# 3. Cache Line Analyzer
# =============================================================================

class CacheLineAnalyzer:
    """Analyze cache line access patterns."""

    CACHE_LINE_SIZE = 64  # bytes

    @classmethod
    def compute_cache_lines(cls, tensor: torch.Tensor) -> List[int]:
        """
        Compute which cache lines are accessed by a tensor.

        Args:
            tensor: PyTorch tensor to analyze

        Returns:
            List of cache line addresses
        """
        if tensor is None:
            return []

        element_size = tensor.element_size()
        elements_per_line = cls.CACHE_LINE_SIZE // element_size

        # Get memory address
        base_addr = tensor.data_ptr()

        # Compute cache line indices
        num_elements = min(tensor.numel(), 10000)  # Limit for performance
        cache_lines = set()

        for i in range(0, num_elements, elements_per_line):
            offset = i * element_size
            cache_line = (base_addr + offset) // cls.CACHE_LINE_SIZE
            cache_lines.add(int(cache_line))

        return sorted(cache_lines)

    @classmethod
    def analyze_tensor_memory(cls, tensor: torch.Tensor,
                             layer_name: str,
                             access_type: str = "read") -> List[CacheLineAccess]:
        """
        Analyze detailed memory access patterns.

        Args:
            tensor: PyTorch tensor to analyze
            layer_name: Name of the layer accessing the tensor
            access_type: Type of access ("read", "write", "read_write")

        Returns:
            List of CacheLineAccess objects
        """
        if tensor is None:
            return []

        element_size = tensor.element_size()
        elements_per_line = cls.CACHE_LINE_SIZE // element_size
        base_addr = tensor.data_ptr()
        tensor_size = tensor.numel() * element_size

        accesses = []
        num_elements = min(tensor.numel(), 10000)

        for i in range(0, num_elements, elements_per_line):
            offset = i * element_size
            cache_line = (base_addr + offset) // cls.CACHE_LINE_SIZE

            access = CacheLineAccess(
                cache_line_addr=int(cache_line),
                access_type=access_type,
                timestamp_us=time.time() * 1e6,
                layer_name=layer_name,
                tensor_size_bytes=tensor_size
            )
            accesses.append(access)

        return accesses


# =============================================================================
# 4. CRDT-Friendly Scoring
# =============================================================================

class CRDTScorer:
    """Compute CRDT-friendliness scores for layers."""

    # Base scores for different layer types
    BASE_SCORES = {
        "conv2d": 0.85,           # Shared weights, spatial locality
        "linear": 0.70,           # Matrix operations, moderate parallelism
        "multihead_attention": 0.65,  # QKV can be parallel, some reduction
        "transformer_encoder": 0.60,
        "transformer_decoder": 0.60,
        "bert_layer": 0.60,
        "gpt2_block": 0.60,
        "layernorm": 0.55,        # Reduction operations
        "batchnorm1d": 0.60,      # Statistics, but can be batched
        "batchnorm2d": 0.60,
        "relu": 0.95,             # Element-wise, highly commutative
        "relu6": 0.95,
        "leaky_relu": 0.95,
        "gelu": 0.95,
        "elu": 0.95,
        "sigmoid": 0.95,
        "tanh": 0.95,
        "softmax": 0.70,          # Reduction, but differentiable
        "dropout": 0.90,          # Element-wise, random but local
        "maxpool2d": 0.80,        # Reduction over spatial regions
        "avgpool2d": 0.80,
        "adaptive_avgpool2d": 0.80,
        "embedding": 0.90,        # Lookup, highly parallelizable
        "flatten": 0.98,          # Just reshaping, no computation
    }

    @classmethod
    def compute_score(cls, layer: nn.Module, layer_type: str,
                     input_shape: Tuple[int, ...],
                     output_shape: Tuple[int, ...]) -> float:
        """
        Compute CRDT-friendly score for a layer.

        Higher scores indicate more CRDT-friendly operations:
        - Commutative operations
        - No shared state dependencies
        - Spatial locality
        - Parallelizable computations

        Args:
            layer: PyTorch layer module
            layer_type: String identifier for layer type
            input_shape: Input tensor shape
            output_shape: Output tensor shape

        Returns:
            Score between 0.0 and 1.0
        """
        # Get base score
        base_score = cls.BASE_SCORES.get(layer_type, 0.50)

        # Adjust based on layer characteristics
        adjustments = 0.0

        # Size adjustment: Larger tensors benefit more from distribution
        output_size = np.prod(output_shape) if output_shape else 0
        if output_size > 1000000:
            adjustments += 0.05  # Large tensors benefit from CRDT distribution
        elif output_size < 1000:
            adjustments -= 0.05  # Small tensors have overhead

        # Depth adjustment: Deeper layers may have more dependencies
        # (This would be passed in from the tracer)

        # Parameter sharing adjustment
        num_params = sum(p.numel() for p in layer.parameters())
        if num_params > 1000000:
            adjustments += 0.03  # Shared parameters benefit from CRDT caching

        # Final score with bounds
        final_score = max(0.0, min(1.0, base_score + adjustments))

        return final_score


# =============================================================================
# 5. PyTorch Tracer
# =============================================================================

class PyTorchTracer:
    """Capture real execution traces from PyTorch models."""

    # Available pre-trained models
    AVAILABLE_MODELS = {
        "resnet18": "torchvision.models.resnet18",
        "resnet34": "torchvision.models.resnet34",
        "resnet50": "torchvision.models.resnet50",
        "resnet101": "torchvision.models.resnet101",
        "vgg16": "torchvision.models.vgg16",
        "mobilenet_v2": "torchvision.models.mobilenet_v2",
        "efficientnet_b0": "torchvision.models.efficientnet_b0",
        "bert-base": "transformers.BertModel",
        "bert-large": "transformers.BertModel",
        "gpt2": "transformers.GPT2Model",
        "gpt2-medium": "transformers.GPT2Model",
        "distilbert": "transformers.DistilBertModel",
    }

    def __init__(self, model_name: str, device: str = "cuda"):
        """
        Initialize PyTorch tracer.

        Args:
            model_name: Name of pre-trained model to trace
            device: Device to run on ("cuda" or "cpu")
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = self._load_model(model_name)
        self.model.eval()

        self.hooks = []
        self.layer_traces = []
        self.layer_depth_map = {}
        self._compute_layer_depths()

    def _get_device(self, requested_device: str) -> str:
        """Get available device."""
        if requested_device == "cuda" and torch.cuda.is_available():
            return "cuda"
        elif torch.cuda.is_available():
            print(f"Warning: CUDA requested but not available, using CPU")
            return "cpu"
        return "cpu"

    def _load_model(self, model_name: str) -> nn.Module:
        """
        Load pre-trained model.

        Args:
            model_name: Name of model to load

        Returns:
            Loaded PyTorch model
        """
        try:
            # Vision models from torchvision
            if model_name.startswith("resnet") or model_name in ["vgg16", "mobilenet_v2", "efficientnet_b0"]:
                from torchvision import models
                model_fn = getattr(models, model_name)
                model = model_fn(pretrained=True)

            # BERT models
            elif model_name.startswith("bert"):
                from transformers import BertModel
                size = "base" if "base" in model_name else "large"
                model = BertModel.from_pretrained(f"bert-{size}-uncased")

            # GPT-2 models
            elif model_name.startswith("gpt2"):
                from transformers import GPT2Model
                if model_name == "gpt2-medium":
                    model = GPT2Model.from_pretrained("gpt2-medium")
                else:
                    model = GPT2Model.from_pretrained("gpt2")

            # DistilBERT
            elif model_name == "distilbert":
                from transformers import DistilBertModel
                model = DistilBertModel.from_pretrained("distilbert-base-uncased")

            else:
                raise ValueError(f"Unknown model: {model_name}")

            print(f"Successfully loaded {model_name}")
            return model.to(self.device)

        except Exception as e:
            print(f"Warning: Could not load {model_name}: {e}")
            print("Falling back to dummy model for testing")
            return self._create_dummy_model(model_name)

    def _create_dummy_model(self, model_name: str) -> nn.Module:
        """Create dummy model for testing when real model unavailable."""
        print(f"Creating dummy model for {model_name}")

        if "resnet" in model_name or model_name in ["vgg16", "mobilenet", "efficientnet"]:
            # CNN architecture
            return nn.Sequential(
                nn.Conv2d(3, 64, 7, stride=2, padding=3),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, 3, padding=1),
                nn.ReLU(),
                nn.Conv2d(128, 256, 3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(256, 1000)
            )

        elif "bert" in model_name or model_name in ["distilbert"]:
            # BERT-like architecture
            return nn.Sequential(
                nn.Linear(768, 768),
                nn.ReLU(),
                nn.Linear(768, 768),
                nn.LayerNorm(768)
            )

        elif "gpt" in model_name:
            # GPT-like architecture
            return nn.Sequential(
                nn.Linear(768, 768),
                nn.GELU(),
                nn.Linear(768, 768),
                nn.LayerNorm(768)
            )

        else:
            # Simple model
            return nn.Sequential(
                nn.Linear(10, 50),
                nn.ReLU(),
                nn.Linear(50, 10)
            )

    def _compute_layer_depths(self):
        """Compute depth of each layer in the model hierarchy."""
        self.layer_depth_map = {}

        def compute_depth(module, name, depth=0):
            self.layer_depth_map[name] = depth
            for child_name, child_module in module.named_children():
                compute_depth(child_module, f"{name}.{child_name}", depth + 1)

        compute_depth(self.model, "model")

    def _get_layer_depth(self, layer_name: str) -> int:
        """Get depth of layer in model hierarchy."""
        return self.layer_depth_map.get(layer_name, 0)

    def _should_trace(self, layer: nn.Module) -> bool:
        """
        Determine if a layer should be traced.

        Args:
            layer: PyTorch layer module

        Returns:
            True if layer should be traced
        """
        # Skip container modules (Sequential, ModuleList, etc.)
        if len(list(layer.children())) > 0:
            return False

        # Trace leaf modules
        traceable_types = (
            nn.Conv2d, nn.Linear, nn.ReLU, nn.ReLU6, nn.LeakyReLU,
            nn.ELU, nn.GELU, nn.Sigmoid, nn.Tanh, nn.Softmax,
            nn.BatchNorm1d, nn.BatchNorm2d, nn.LayerNorm,
            nn.Dropout, nn.MaxPool2d, nn.AvgPool2d,
            nn.AdaptiveAvgPool2d, nn.Embedding, nn.Flatten
        )

        return isinstance(layer, traceable_types) or \
               "MultiheadAttention" in str(type(layer)) or \
               "Transformer" in str(type(layer)) or \
               "BertLayer" in str(type(layer)) or \
               "GPT2Block" in str(type(layer))

    def _create_hook(self, layer_name: str, layer: nn.Module):
        """
        Create forward hook for a layer.

        Args:
            layer_name: Name of the layer
            layer: PyTorch layer module

        Returns:
            Hook function
        """
        def hook(module, input, output):
            start_time = time.perf_counter()

            # Get layer type
            layer_type = LayerAnalyzer.get_layer_type(module)

            # Extract shapes
            input_shape = self._extract_shape(input[0]) if input and len(input) > 0 else ()
            output_shape = self._extract_shape(output) if output is not None else ()

            # Count parameters
            parameters = sum(p.numel() for p in module.parameters())

            # Compute FLOPs
            flops = LayerAnalyzer.compute_flops(module, input_shape, output_shape)

            # Estimate memory (in MB)
            mem_read = self._estimate_memory_read(input)
            mem_write = self._estimate_memory_write(output)

            # Compute cache line accesses
            cache_accesses = []
            if output is not None:
                cache_accesses = CacheLineAnalyzer.compute_cache_lines(output)

            # CRDT-friendly score
            crdt_score = CRDTScorer.compute_score(module, layer_type, input_shape, output_shape)

            # Get layer depth
            layer_depth = self._get_layer_depth(layer_name)

            # Create trace
            trace = LayerTrace(
                layer_name=layer_name,
                layer_type=layer_type,
                input_shape=input_shape,
                output_shape=output_shape,
                parameters=parameters,
                flops=flops,
                memory_reads_mb=mem_read,
                memory_writes_mb=mem_write,
                compute_time_ms=0.0,  # Will be updated after forward pass
                cache_line_accesses=cache_accesses,
                crdt_friendly_score=crdt_score,
                layer_depth=layer_depth,
                parent_name=".".join(layer_name.split(".")[:-1]) or "root"
            )

            self.layer_traces.append(trace)

            # Update compute time
            compute_time = (time.perf_counter() - start_time) * 1000
            trace.compute_time_ms = compute_time

        return hook

    def _extract_shape(self, tensor: Any) -> Tuple[int, ...]:
        """Extract shape from tensor or tuple of tensors."""
        if tensor is None:
            return ()
        elif isinstance(tensor, torch.Tensor):
            return tuple(tensor.shape)
        elif isinstance(tensor, tuple):
            # Return first tensor's shape
            return self._extract_shape(tensor[0])
        else:
            return ()

    def _estimate_memory_read(self, input: Any) -> float:
        """Estimate memory read in MB."""
        if input is None:
            return 0.0

        tensors = input if isinstance(input, tuple) else (input,)
        total_bytes = 0

        for tensor in tensors:
            if isinstance(tensor, torch.Tensor):
                total_bytes += tensor.numel() * tensor.element_size()

        return total_bytes / (1024 ** 2)

    def _estimate_memory_write(self, output: Any) -> float:
        """Estimate memory written in MB."""
        if output is None:
            return 0.0

        tensors = output if isinstance(output, tuple) else (output,)
        total_bytes = 0

        for tensor in tensors:
            if isinstance(tensor, torch.Tensor):
                total_bytes += tensor.numel() * tensor.element_size()

        return total_bytes / (1024 ** 2)

    def trace(self, input_data: Union[torch.Tensor, Dict[str, torch.Tensor]]) -> ModelTrace:
        """
        Trace model inference.

        Args:
            input_data: Input tensor or dict of tensors for model

        Returns:
            Complete ModelTrace with all layer data
        """
        print(f"Tracing {self.model_name} on {self.device}...")

        # Clear previous traces
        self.hooks = []
        self.layer_traces = []

        # Register hooks
        for name, layer in self.model.named_modules():
            if self._should_trace(layer):
                handle = layer.register_forward_hook(self._create_hook(name, layer))
                self.hooks.append(handle)

        # Prepare input
        if isinstance(input_data, dict):
            input_data = {k: v.to(self.device) for k, v in input_data.items()}
        else:
            input_data = input_data.to(self.device)

        # Extract input shape
        input_shape = self._extract_shape(input_data)

        # Run inference
        start_time = time.perf_counter()
        with torch.no_grad():
            _ = self.model(input_data)
        total_time = (time.perf_counter() - start_time) * 1000

        # Remove hooks
        for handle in self.hooks:
            handle.remove()

        # Build trace
        trace = ModelTrace(
            model_name=self.model_name,
            framework="pytorch",
            layers=self.layer_traces,
            total_flops=sum(l.flops for l in self.layer_traces),
            total_memory_mb=sum(l.memory_reads_mb + l.memory_writes_mb
                              for l in self.layer_traces),
            total_time_ms=total_time,
            capture_timestamp=time.strftime("%Y%m%d-%H%M%S"),
            device=self.device,
            input_shape=input_shape
        )

        print(f"Traced {len(trace.layers)} layers in {total_time:.2f} ms")

        return trace


# =============================================================================
# 6. Trace Exporter
# =============================================================================

class TraceExporter:
    """Export traces in various formats."""

    @staticmethod
    def to_json(trace: ModelTrace, filepath: str, include_all_cache_lines: bool = False):
        """
        Export trace to JSON.

        Args:
            trace: ModelTrace to export
            filepath: Output file path
            include_all_cache_lines: Whether to include all cache line data
        """
        data = {
            "model_name": trace.model_name,
            "framework": trace.framework,
            "device": trace.device,
            "input_shape": list(trace.input_shape),
            "total_flops": trace.total_flops,
            "total_memory_mb": trace.total_memory_mb,
            "total_time_ms": trace.total_time_ms,
            "capture_timestamp": trace.capture_timestamp,
            "num_layers": len(trace.layers),
            "layers": [
                {
                    "layer_name": l.layer_name,
                    "layer_type": l.layer_type,
                    "layer_depth": l.layer_depth,
                    "parent_name": l.parent_name,
                    "input_shape": list(l.input_shape),
                    "output_shape": list(l.output_shape),
                    "parameters": l.parameters,
                    "flops": l.flops,
                    "memory_reads_mb": l.memory_reads_mb,
                    "memory_writes_mb": l.memory_writes_mb,
                    "compute_time_ms": l.compute_time_ms,
                    "cache_line_count": len(l.cache_line_accesses),
                    "cache_lines": l.cache_line_accesses if include_all_cache_lines
                                  else l.cache_line_accesses[:100],
                    "crdt_friendly_score": l.crdt_friendly_score
                }
                for l in trace.layers
            ]
        }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported JSON trace to {filepath}")

    @staticmethod
    def to_hdf5(trace: ModelTrace, filepath: str):
        """
        Export trace to HDF5 for large datasets.

        Args:
            trace: ModelTrace to export
            filepath: Output file path
        """
        try:
            import h5py
        except ImportError:
            print("Warning: h5py not available, skipping HDF5 export")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with h5py.File(filepath, 'w') as f:
            # Metadata
            f.attrs["model_name"] = trace.model_name
            f.attrs["framework"] = trace.framework
            f.attrs["device"] = trace.device
            f.attrs["input_shape"] = list(trace.input_shape)
            f.attrs["total_flops"] = trace.total_flops
            f.attrs["total_memory_mb"] = trace.total_memory_mb
            f.attrs["total_time_ms"] = trace.total_time_ms
            f.attrs["capture_timestamp"] = trace.capture_timestamp
            f.attrs["num_layers"] = len(trace.layers)

            # Layer data
            for i, layer in enumerate(trace.layers):
                grp = f.create_group(f"layer_{i:04d}")
                grp.attrs["name"] = layer.layer_name
                grp.attrs["type"] = layer.layer_type
                grp.attrs["depth"] = layer.layer_depth
                grp.attrs["parent"] = layer.parent_name
                grp.attrs["input_shape"] = list(layer.input_shape)
                grp.attrs["output_shape"] = list(layer.output_shape)
                grp.attrs["parameters"] = layer.parameters
                grp.attrs["flops"] = layer.flops
                grp.attrs["memory_reads_mb"] = layer.memory_reads_mb
                grp.attrs["memory_writes_mb"] = layer.memory_writes_mb
                grp.attrs["compute_time_ms"] = layer.compute_time_ms
                grp.attrs["crdt_friendly_score"] = layer.crdt_friendly_score

                # Cache line data
                if layer.cache_line_accesses:
                    grp.create_dataset("cache_lines",
                                      data=np.array(layer.cache_line_accesses),
                                      compression="gzip")

        print(f"Exported HDF5 trace to {filepath}")

    @staticmethod
    def to_csv(trace: ModelTrace, filepath: str):
        """
        Export trace summary to CSV.

        Args:
            trace: ModelTrace to export
            filepath: Output file path
        """
        import csv

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "layer_name", "layer_type", "depth", "parameters", "flops",
                "memory_read_mb", "memory_write_mb", "time_ms",
                "cache_line_count", "crdt_score"
            ])

            for l in trace.layers:
                writer.writerow([
                    l.layer_name, l.layer_type, l.layer_depth,
                    l.parameters, l.flops,
                    f"{l.memory_reads_mb:.4f}", f"{l.memory_writes_mb:.4f}",
                    f"{l.compute_time_ms:.4f}",
                    len(l.cache_line_accesses), f"{l.crdt_friendly_score:.4f}"
                ])

        print(f"Exported CSV trace to {filepath}")

    @staticmethod
    def print_summary(trace: ModelTrace):
        """Print trace summary to console."""
        print("\n" + "=" * 80)
        print(f"Model Trace Summary: {trace.model_name}")
        print("=" * 80)
        print(f"Framework: {trace.framework}")
        print(f"Device: {trace.device}")
        print(f"Input Shape: {trace.input_shape}")
        print(f"Layers Traced: {len(trace.layers)}")
        print(f"Total FLOPs: {trace.total_flops:,}")
        print(f"Total Memory: {trace.total_memory_mb:.2f} MB")
        print(f"Total Time: {trace.total_time_ms:.2f} ms")
        print(f"Capture Time: {trace.capture_timestamp}")
        print("\n" + "-" * 80)
        print(f"{'Layer Name':<40} {'Type':<20} {'FLOPs':>12} {'CRDT':>6}")
        print("-" * 80)

        for layer in trace.layers:
            print(f"{layer.layer_name:<40} {layer.layer_type:<20} "
                  f"{layer.flops:>12,} {layer.crdt_friendly_score:>6.3f}")

        print("-" * 80)
        print(f"Average CRDT Score: {np.mean([l.crdt_friendly_score for l in trace.layers]):.3f}")
        print("=" * 80 + "\n")


# =============================================================================
# 7. Main Entry Point
# =============================================================================

def create_input_data(model_name: str, device: str) -> Union[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Create appropriate input data for a model.

    Args:
        model_name: Name of the model
        device: Device to create tensors on

    Returns:
        Input tensor or dict of tensors
    """
    # Vision models
    if any(name in model_name for name in ["resnet", "vgg", "mobilenet", "efficientnet"]):
        return torch.randn(1, 3, 224, 224).to(device)

    # BERT models
    elif "bert" in model_name or model_name == "distilbert":
        return {
            "input_ids": torch.randint(0, 30000, (1, 128)).to(device),
            "attention_mask": torch.ones(1, 128).to(device)
        }

    # GPT models
    elif "gpt" in model_name:
        return torch.randint(0, 50257, (1, 128)).to(device)

    # Default
    else:
        return torch.randn(1, 10).to(device)


def main():
    """Run PyTorch tracing."""
    print("=" * 80)
    print("PyTorch Real Integration - Production Tracer")
    print("=" * 80)

    # Check PyTorch and CUDA
    print(f"\nPyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # Tracer configuration
    models_to_trace = ["resnet50", "bert-base", "gpt2"]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Output directory
    output_dir = Path("C:/Users/casey/polln/production/pytorch_integration/traces")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Trace each model
    for model_name in models_to_trace:
        print(f"\n{'=' * 80}")
        print(f"Tracing: {model_name}")
        print(f"{'=' * 80}")

        try:
            # Create tracer
            tracer = PyTorchTracer(model_name, device=device)

            # Create input data
            input_data = create_input_data(model_name, device)

            # Trace inference
            trace = tracer.trace(input_data)

            # Print summary
            TraceExporter.print_summary(trace)

            # Export traces
            base_name = f"{model_name}_{trace.capture_timestamp}"

            # JSON export (default: limited cache lines)
            json_file = output_dir / f"{base_name}.json"
            TraceExporter.to_json(trace, str(json_file), include_all_cache_lines=False)

            # JSON export (full cache lines)
            json_full_file = output_dir / f"{base_name}_full.json"
            TraceExporter.to_json(trace, str(json_full_file), include_all_cache_lines=True)

            # HDF5 export
            hdf5_file = output_dir / f"{base_name}.h5"
            TraceExporter.to_hdf5(trace, str(hdf5_file))

            # CSV export
            csv_file = output_dir / f"{base_name}.csv"
            TraceExporter.to_csv(trace, str(csv_file))

        except Exception as e:
            print(f"Error tracing {model_name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("Tracing complete!")
    print(f"Traces saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
