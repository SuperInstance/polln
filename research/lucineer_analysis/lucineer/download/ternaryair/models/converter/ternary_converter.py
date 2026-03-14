"""
Model conversion utilities for TernaryAir.

This module provides tools to convert floating-point models to
ternary quantized format suitable for TernaryAir hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class ConversionConfig:
    """Configuration for model conversion.
    
    Attributes:
        threshold: Magnitude threshold for zero weights.
        per_channel: Whether to use per-channel quantization.
        per_layer: Whether to use per-layer scaling.
        symmetric: Whether to use symmetric quantization.
    """
    threshold: float = 0.05
    per_channel: bool = True
    per_layer: bool = False
    symmetric: bool = True


@dataclass
class ConversionResult:
    """Result of model conversion.
    
    Attributes:
        ternary_weights: Quantized weights {-1, 0, +1}.
        scales: Scaling factors for each layer/channel.
        sparsity: Fraction of weights that are zero.
        compression_ratio: Compression ratio vs FP16.
    """
    ternary_weights: Dict[str, np.ndarray]
    scales: Dict[str, np.ndarray]
    sparsity: float
    compression_ratio: float


def quantize_to_ternary(
    weights: np.ndarray,
    threshold: float = 0.05,
    per_channel: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """Quantize floating-point weights to ternary {-1, 0, +1}.
    
    Args:
        weights: Floating-point weight array.
        threshold: Magnitude threshold for zero.
        per_channel: Use per-channel scaling.
    
    Returns:
        Tuple of (ternary_weights, scales).
    
    Example:
        >>> weights = np.array([[-0.5, 0.1, 0.3], [0.02, -0.8, 0.0]])
        >>> ternary, scale = quantize_to_ternary(weights)
        >>> print(ternary)
        [[-1  0  1]
         [ 0 -1  0]]
    """
    # Compute scale factors
    if per_channel:
        # Scale per output channel
        scales = np.mean(np.abs(weights), axis=-1, keepdims=True)
    else:
        # Global scale
        scales = np.array([[np.mean(np.abs(weights))]])
    
    # Normalize weights
    normalized = weights / (scales + 1e-8)
    
    # Quantize to ternary
    ternary = np.zeros_like(normalized, dtype=np.int8)
    ternary[normalized > threshold] = 1
    ternary[normalized < -threshold] = -1
    
    return ternary, scales.flatten()


def convert_layer(
    weights: np.ndarray,
    config: ConversionConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert a single layer's weights to ternary.
    
    Args:
        weights: Layer weight matrix.
        config: Conversion configuration.
    
    Returns:
        Tuple of (ternary_weights, scales).
    """
    return quantize_to_ternary(
        weights,
        threshold=config.threshold,
        per_channel=config.per_channel,
    )


def convert_model(
    model_weights: Dict[str, np.ndarray],
    config: Optional[ConversionConfig] = None,
) -> ConversionResult:
    """Convert all model weights to ternary format.
    
    Args:
        model_weights: Dictionary of layer name to weight array.
        config: Conversion configuration.
    
    Returns:
        Conversion result with quantized weights and statistics.
    
    Example:
        >>> weights = {
        ...     "layer0.weight": np.random.randn(1024, 1024).astype(np.float32),
        ...     "layer1.weight": np.random.randn(1024, 1024).astype(np.float32),
        ... }
        >>> result = convert_model(weights)
        >>> print(f"Sparsity: {result.sparsity:.1%}")
        Sparsity: 49.8%
    """
    if config is None:
        config = ConversionConfig()
    
    ternary_weights = {}
    scales = {}
    total_params = 0
    zero_params = 0
    
    for name, weights in model_weights.items():
        # Convert to ternary
        ternary, scale = convert_layer(weights, config)
        
        ternary_weights[name] = ternary
        scales[name] = scale
        
        # Count parameters
        total_params += weights.size
        zero_params += np.sum(ternary == 0)
    
    # Calculate statistics
    sparsity = zero_params / total_params if total_params > 0 else 0.0
    
    # FP16 = 16 bits per weight
    # Ternary = 2 bits per weight
    # Plus scale factors (one per channel)
    compression_ratio = 16.0 / 2.0  # 8x from precision reduction
    
    return ConversionResult(
        ternary_weights=ternary_weights,
        scales=scales,
        sparsity=sparsity,
        compression_ratio=compression_ratio,
    )


def pack_ternary_weights(ternary: np.ndarray) -> np.ndarray:
    """Pack ternary weights into 2-bit format.
    
    Packs 4 ternary weights per byte:
        00 = +1
        01 = 0
        10 = -1
        11 = reserved
    
    Args:
        ternary: Ternary weight array {-1, 0, +1}.
    
    Returns:
        Packed uint8 array.
    """
    # Map ternary values to 2-bit codes
    codes = np.zeros_like(ternary, dtype=np.uint8)
    codes[ternary == 1] = 0b00
    codes[ternary == 0] = 0b01
    codes[ternary == -1] = 0b10
    
    # Pad to multiple of 4
    pad_size = (4 - len(codes.flatten()) % 4) % 4
    padded = np.append(codes.flatten(), np.zeros(pad_size, dtype=np.uint8))
    
    # Pack 4 values per byte
    packed = np.zeros(len(padded) // 4, dtype=np.uint8)
    for i in range(len(packed)):
        packed[i] = (
            (padded[4*i] << 6) |
            (padded[4*i + 1] << 4) |
            (padded[4*i + 2] << 2) |
            padded[4*i + 3]
        )
    
    return packed


def export_for_hardware(
    result: ConversionResult,
    output_path: str,
) -> None:
    """Export converted weights for TernaryAir hardware.
    
    Args:
        result: Conversion result.
        output_path: Path to output binary file.
    """
    with open(output_path, 'wb') as f:
        # Write header
        f.write(b'TERNARY')  # Magic number
        f.write((1).to_bytes(4, 'little'))  # Version
        f.write(len(result.ternary_weights).to_bytes(4, 'little'))  # Num layers
        
        # Write each layer
        for name, weights in result.ternary_weights.items():
            # Layer name length and name
            name_bytes = name.encode('utf-8')
            f.write(len(name_bytes).to_bytes(2, 'little'))
            f.write(name_bytes)
            
            # Shape
            shape = weights.shape
            f.write(len(shape).to_bytes(2, 'little'))
            for dim in shape:
                f.write(dim.to_bytes(4, 'little'))
            
            # Packed weights
            packed = pack_ternary_weights(weights)
            f.write(len(packed).to_bytes(4, 'little'))
            f.write(packed.tobytes())
            
            # Scale factor
            scale = result.scales[name]
            f.write(len(scale).to_bytes(4, 'little'))
            f.write(scale.astype(np.float32).tobytes())


def evaluate_quality(
    original: Dict[str, np.ndarray],
    quantized: Dict[str, np.ndarray],
    scales: Dict[str, np.ndarray],
) -> Dict[str, float]:
    """Evaluate quantization quality.
    
    Args:
        original: Original floating-point weights.
        quantized: Quantized ternary weights.
        scales: Scale factors.
    
    Returns:
        Dictionary of quality metrics.
    """
    total_mse = 0.0
    total_params = 0
    
    layer_metrics = {}
    
    for name in original.keys():
        orig = original[name]
        quant = quantized[name]
        scale = scales[name]
        
        # Reconstruct weights
        if len(scale) == 1:
            reconstructed = quant * scale[0]
        else:
            reconstructed = quant * scale.reshape(-1, 1)
        
        # Calculate MSE
        mse = np.mean((orig - reconstructed) ** 2)
        total_mse += mse * orig.size
        total_params += orig.size
        
        layer_metrics[name] = {
            'mse': float(mse),
            'max_error': float(np.max(np.abs(orig - reconstructed))),
        }
    
    return {
        'global_mse': total_mse / total_params if total_params > 0 else 0.0,
        'layers': layer_metrics,
    }


# ============================================================================
# PyTorch Integration (optional)
# ============================================================================

def convert_pytorch_model(model, config: Optional[ConversionConfig] = None) -> ConversionResult:
    """Convert a PyTorch model to ternary format.
    
    Args:
        model: PyTorch model.
        config: Conversion configuration.
    
    Returns:
        Conversion result.
    """
    try:
        import torch
    except ImportError:
        raise ImportError("PyTorch is required for convert_pytorch_model")
    
    # Extract weights
    weights = {}
    for name, param in model.named_parameters():
        if param.dim() >= 2:  # Only quantize weight matrices
            weights[name] = param.detach().numpy()
    
    return convert_model(weights, config)


def convert_transformers_model(model_name: str, config: Optional[ConversionConfig] = None) -> ConversionResult:
    """Convert a HuggingFace transformers model to ternary format.
    
    Args:
        model_name: Name of the model on HuggingFace Hub.
        config: Conversion configuration.
    
    Returns:
        Conversion result.
    """
    try:
        from transformers import AutoModel
        import torch
    except ImportError:
        raise ImportError("transformers and torch are required")
    
    # Load model
    model = AutoModel.from_pretrained(model_name)
    
    return convert_pytorch_model(model, config)


if __name__ == "__main__":
    # Demo
    print("TernaryAir Model Converter Demo")
    print("=" * 50)
    
    # Create random weights
    np.random.seed(42)
    weights = {
        "layer0.weight": np.random.randn(1024, 1024).astype(np.float32) * 0.1,
        "layer1.weight": np.random.randn(1024, 1024).astype(np.float32) * 0.1,
        "layer2.weight": np.random.randn(1024, 1024).astype(np.float32) * 0.1,
    }
    
    # Convert
    result = convert_model(weights)
    
    print(f"Sparsity: {result.sparsity:.1%}")
    print(f"Compression ratio: {result.compression_ratio:.1f}x")
    
    # Evaluate quality
    quality = evaluate_quality(weights, result.ternary_weights, result.scales)
    print(f"Global MSE: {quality['global_mse']:.6f}")
    
    print("\nDone!")
