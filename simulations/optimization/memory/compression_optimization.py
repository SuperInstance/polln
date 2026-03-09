"""
KV-Cache Compression Optimization for POLLN

This script simulates different compression strategies for KV-caches to find
optimal compression ratios, methods, and parameters for different cache types.

Compression strategies tested:
- SVD (Singular Value Decomposition)
- Quantization (8-bit, 4-bit, 2-bit)
- Sparsification (magnitude-based thresholding)
- Product Quantization (PQ)
- Hybrid approaches

Output: Optimal compression configuration for kvanchor.ts
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import time

class CacheType(Enum):
    """Types of KV-cache data"""
    ATTENTION = "attention"  # Key/Value matrices from attention layers
    MLP = "mlp"              # MLP intermediate activations
    EMBEDDING = "embedding"  # Token embeddings
    FFN = "ffn"              # Feed-forward network states

class CompressionMethod(Enum):
    """Compression methods"""
    SVD = "svd"
    QUANTIZATION_8BIT = "quant_8bit"
    QUANTIZATION_4BIT = "quant_4bit"
    QUANTIZATION_2BIT = "quant_2bit"
    SPARSIFICATION = "sparsification"
    PRODUCT_QUANTIZATION = "pq"
    HYBRID_SVD_QUANT = "hybrid_svd_quant"
    HYBRID_PQ_QUANT = "hybrid_pq_quant"

@dataclass
class CompressionResult:
    """Results from compression experiment"""
    method: CompressionMethod
    cache_type: CacheType
    compression_ratio: float
    reconstruction_error: float
    retrieval_quality: float
    compression_time: float
    decompression_time: float
    memory_saved: float
    parameters: Dict[str, Any]

class KVCacheCompressor:
    """Simulates KV-cache compression with various strategies"""

    def __init__(self, seed: int = 42):
        """Initialize compressor with random seed"""
        np.random.seed(seed)

    def generate_synthetic_kv_cache(
        self,
        cache_type: CacheType,
        num_tokens: int = 2048,
        hidden_dim: int = 4096,
        num_heads: int = 32,
        head_dim: int = 128
    ) -> Dict[str, np.ndarray]:
        """
        Generate synthetic KV-cache data mimicking real transformer caches

        Args:
            cache_type: Type of cache to generate
            num_tokens: Number of tokens in sequence
            hidden_dim: Hidden dimension size
            num_heads: Number of attention heads
            head_dim: Dimension per head

        Returns:
            Dictionary with 'key' and 'value' matrices
        """
        if cache_type == CacheType.ATTENTION:
            # Attention keys/values have structured patterns
            key = np.random.randn(num_tokens, num_heads, head_dim).astype(np.float32) * 0.1
            value = np.random.randn(num_tokens, num_heads, head_dim).astype(np.float32) * 0.1

            # Add position-based structure (more realistic)
            for t in range(num_tokens):
                key[t] += np.sin(np.outer(np.arange(num_heads), np.arange(head_dim) * 0.1) + t * 0.01) * 0.05
                value[t] += np.cos(np.outer(np.arange(num_heads), np.arange(head_dim) * 0.1) + t * 0.01) * 0.05

        elif cache_type == CacheType.MLP:
            # MLP activations are more sparse
            key = np.random.randn(num_tokens, hidden_dim).astype(np.float32) * 0.5
            value = np.random.randn(num_tokens, hidden_dim).astype(np.float32) * 0.5

            # Add sparsity (70% zeros)
            mask = np.random.rand(*key.shape) > 0.7
            key = key * mask
            value = value * mask

        elif cache_type == CacheType.EMBEDDING:
            # Embeddings are more uniform
            key = np.random.randn(num_tokens, hidden_dim).astype(np.float32) * 0.3
            value = np.random.randn(num_tokens, hidden_dim).astype(np.float32) * 0.3

            # Add semantic clustering structure
            num_clusters = 16
            cluster_centers = np.random.randn(num_clusters, hidden_dim).astype(np.float32)
            cluster_assignments = np.random.randint(0, num_clusters, num_tokens)

            for t in range(num_tokens):
                key[t] += cluster_centers[cluster_assignments[t]] * 0.2
                value[t] += cluster_centers[cluster_assignments[t]] * 0.2

        elif cache_type == CacheType.FFN:
            # FFN states are dense but low-rank
            rank = min(hidden_dim // 4, 512)
            U = np.random.randn(num_tokens, rank).astype(np.float32)
            V = np.random.randn(rank, hidden_dim).astype(np.float32)

            key = (U @ V).astype(np.float32)
            value = (U @ V).astype(np.float32)

        return {
            'key': key,
            'value': value
        }

    def svd_compress(
        self,
        data: np.ndarray,
        target_ratio: float
    ) -> Tuple[np.ndarray, List, float]:
        """
        Compress using SVD (Singular Value Decomposition)

        Args:
            data: Input data matrix
            target_ratio: Target compression ratio

        Returns:
            Compressed data, singular values, actual ratio
        """
        original_size = data.nbytes

        # Flatten if needed
        if len(data.shape) > 2:
            data_2d = data.reshape(data.shape[0], -1)
        else:
            data_2d = data

        # Compute SVD
        U, s, Vt = np.linalg.svd(data_2d, full_matrices=False)

        # Determine rank for target compression
        original_elements = data_2d.shape[0] * data_2d.shape[1]
        target_elements = int(original_elements * target_ratio)

        # Approximate rank (simplified)
        rank = max(1, min(target_elements // (data_2d.shape[0] + data_2d.shape[1]), len(s)))

        # Truncate
        U_k = U[:, :rank]
        s_k = s[:rank]
        Vt_k = Vt[:rank, :]

        # Calculate actual compression
        compressed_size = (U_k.nbytes + s_k.nbytes + Vt_k.nbytes)
        actual_ratio = compressed_size / original_size

        return (U_k, s_k, Vt_k), actual_ratio

    def svd_decompress(
        self,
        compressed: Tuple[np.ndarray, np.ndarray, np.ndarray],
        original_shape: Tuple[int, ...]
    ) -> np.ndarray:
        """Decompress SVD-compressed data"""
        U_k, s_k, Vt_k = compressed
        reconstructed = U_k @ np.diag(s_k) @ Vt_k
        return reconstructed.reshape(original_shape)

    def quantize(
        self,
        data: np.ndarray,
        bits: int
    ) -> Tuple[np.ndarray, float, float]:
        """
        Quantize data to specified bits

        Args:
            data: Input data
            bits: Number of bits (8, 4, or 2)

        Returns:
            Quantized data, scale, zero_point
        """
        # Find min/max
        min_val = np.min(data)
        max_val = np.max(data)

        # Calculate scale and zero point
        qmin = 0
        qmax = (1 << bits) - 1

        scale = (max_val - min_val) / (qmax - qmin)
        zero_point = qmin - min_val / scale

        # Quantize
        quantized = np.clip(np.round(data / scale + zero_point), qmin, qmax).astype(np.uint8)

        return quantized, scale, zero_point

    def dequantize(
        self,
        quantized: np.ndarray,
        scale: float,
        zero_point: float
    ) -> np.ndarray:
        """Dequantize data"""
        return (quantized.astype(np.float32) - zero_point) * scale

    def sparsify(
        self,
        data: np.ndarray,
        sparsity: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sparsify data by keeping top-k magnitude values

        Args:
            data: Input data
            sparsity: Target sparsity (0.0 = dense, 1.0 = all zeros)

        Returns:
            Sparse values, indices
        """
        flat_data = data.flatten()
        num_keep = int(len(flat_data) * (1 - sparsity))

        # Get top-k indices by magnitude
        indices = np.argsort(np.abs(flat_data))[-num_keep:]
        values = flat_data[indices]

        return values, indices

    def densify(
        self,
        values: np.ndarray,
        indices: np.ndarray,
        original_shape: Tuple[int, ...]
    ) -> np.ndarray:
        """Reconstruct sparse data"""
        dense = np.zeros(np.prod(original_shape), dtype=np.float32)
        dense[indices] = values
        return dense.reshape(original_shape)

    def product_quantize(
        self,
        data: np.ndarray,
        n_subvectors: int = 8,
        n_bits: int = 8
    ) -> Tuple[List, List, List]:
        """
        Product Quantization

        Args:
            data: Input data (2D)
            n_subvectors: Number of subvectors
            n_bits: Number of bits per codebook

        Returns:
            Codebooks, encodings, subvector sizes
        """
        n_samples, dim = data.shape
        subvec_dim = dim // n_subvectors

        codebooks = []
        encodings = []
        subvec_sizes = []

        # Number of codewords per subvector
        n_codewords = 1 << n_bits

        for i in range(n_subvectors):
            start = i * subvec_dim
            end = start + subvec_dim if i < n_subvectors - 1 else dim

            # Extract subvector
            subvec = data[:, start:end]

            # K-means clustering (simplified)
            np.random.seed(42 + i)
            centroids = np.random.randn(n_codewords, subvec_dim).astype(np.float32)

            # Assign to nearest centroid
            distances = np.zeros((n_samples, n_codewords))
            for j in range(n_codewords):
                diff = subvec - centroids[j]
                distances[:, j] = np.sum(diff ** 2, axis=1)

            encoding = np.argmin(distances, axis=1)

            codebooks.append(centroids)
            encodings.append(encoding)
            subvec_sizes.append(end - start)

        return codebooks, encodings, subvec_sizes

    def pq_decode(
        self,
        codebooks: List,
        encodings: List,
        subvec_sizes: List
    ) -> np.ndarray:
        """Decode product-quantized data"""
        n_samples = len(encodings[0])
        dim = sum(subvec_sizes)
        reconstructed = np.zeros((n_samples, dim), dtype=np.float32)

        offset = 0
        for i, (codebook, encoding, size) in enumerate(zip(codebooks, encodings, subvec_sizes)):
            reconstructed[:, offset:offset + size] = codebook[encoding]
            offset += size

        return reconstructed

    def hybrid_svd_quant(
        self,
        data: np.ndarray,
        svd_ratio: float,
        quant_bits: int
    ) -> Tuple:
        """
        Hybrid: SVD + Quantization
        """
        # First apply SVD
        (U, s, Vt), _ = self.svd_compress(data, svd_ratio)

        # Then quantize U and Vt
        U_q, U_scale, U_zp = self.quantize(U, quant_bits)
        Vt_q, Vt_scale, Vt_zp = self.quantize(Vt, quant_bits)

        return (U_q, s, Vt_q, U_scale, U_zp, Vt_scale, Vt_zp)

    def hybrid_svd_quant_decode(
        self,
        compressed: Tuple,
        original_shape: Tuple[int, ...]
    ) -> np.ndarray:
        """Decode hybrid SVD + quantization"""
        U_q, s, Vt_q, U_scale, U_zp, Vt_scale, Vt_zp = compressed

        # Dequantize
        U = self.dequantize(U_q, U_scale, U_zp)
        Vt = self.dequantize(Vt_q, Vt_scale, Vt_zp)

        # Reconstruct
        reconstructed = U @ np.diag(s) @ Vt
        return reconstructed.reshape(original_shape)

    def evaluate_compression(
        self,
        original: np.ndarray,
        reconstructed: np.ndarray,
        compression_time: float,
        decompression_time: float,
        method: CompressionMethod,
        cache_type: CacheType,
        parameters: Dict[str, Any]
    ) -> CompressionResult:
        """
        Evaluate compression quality
        """
        # Compression ratio
        original_size = original.nbytes
        compressed_size = parameters.get('compressed_size', original_size)
        compression_ratio = compressed_size / original_size
        memory_saved = 1 - compression_ratio

        # Reconstruction error (MSE)
        mse = np.mean((original - reconstructed) ** 2)

        # Retrieval quality (cosine similarity)
        original_flat = original.flatten()
        reconstructed_flat = reconstructed.flatten()

        cosine_sim = np.dot(original_flat, reconstructed_flat) / (
            np.linalg.norm(original_flat) * np.linalg.norm(reconstructed_flat) + 1e-8
        )

        return CompressionResult(
            method=method,
            cache_type=cache_type,
            compression_ratio=compression_ratio,
            reconstruction_error=float(mse),
            retrieval_quality=float(cosine_sim),
            compression_time=compression_time,
            decompression_time=decompression_time,
            memory_saved=memory_saved,
            parameters=parameters
        )

    def run_compression_experiment(
        self,
        cache_type: CacheType,
        target_ratios: List[float] = [0.1, 0.15, 0.2, 0.25, 0.3]
    ) -> List[CompressionResult]:
        """
        Run full compression experiment for a cache type
        """
        print(f"\n{'='*60}")
        print(f"Testing {cache_type.value.upper()} cache compression")
        print(f"{'='*60}")

        results = []

        # Generate synthetic data
        data = self.generate_synthetic_kv_cache(cache_type)
        key_data = data['key']
        value_data = data['value']

        # Combine for compression
        if len(key_data.shape) > 2:
            combined = np.concatenate([key_data.flatten(), value_data.flatten()])
        else:
            combined = np.concatenate([key_data, value_data], axis=0)

        original_shape = key_data.shape

        for target_ratio in target_ratios:
            print(f"\n--- Target Ratio: {target_ratio:.2f} ---")

            # SVD
            print("Testing SVD...")
            start = time.time()
            compressed, actual_ratio = self.svd_compress(combined, target_ratio)
            compress_time = time.time() - start

            start = time.time()
            reconstructed = self.svd_decompress(compressed, combined.shape)
            decompress_time = time.time() - start

            result = self.evaluate_compression(
                combined,
                reconstructed,
                compress_time,
                decompress_time,
                CompressionMethod.SVD,
                cache_type,
                {'target_ratio': target_ratio, 'actual_ratio': actual_ratio}
            )
            results.append(result)
            print(f"  Ratio: {actual_ratio:.3f}, MSE: {result.reconstruction_error:.4f}, "
                  f"Quality: {result.retrieval_quality:.4f}")

            # Quantization 8-bit
            print("Testing 8-bit quantization...")
            start = time.time()
            quantized, scale, zp = self.quantize(combined, 8)
            compress_time = time.time() - start

            start = time.time()
            reconstructed = self.dequantize(quantized, scale, zp)
            decompress_time = time.time() - start

            compressed_size = quantized.nbytes + 8  # scale + zp
            result = self.evaluate_compression(
                combined,
                reconstructed,
                compress_time,
                decompress_time,
                CompressionMethod.QUANTIZATION_8BIT,
                cache_type,
                {'bits': 8, 'compressed_size': compressed_size}
            )
            results.append(result)
            print(f"  Ratio: {result.compression_ratio:.3f}, MSE: {result.reconstruction_error:.4f}, "
                  f"Quality: {result.retrieval_quality:.4f}")

            # Quantization 4-bit
            print("Testing 4-bit quantization...")
            start = time.time()
            quantized, scale, zp = self.quantize(combined, 4)
            compress_time = time.time() - start

            start = time.time()
            reconstructed = self.dequantize(quantized, scale, zp)
            decompress_time = time.time() - start

            compressed_size = quantized.nbytes // 2 + 8  # 4 bits = half of 8 bits
            result = self.evaluate_compression(
                combined,
                reconstructed,
                compress_time,
                decompress_time,
                CompressionMethod.QUANTIZATION_4BIT,
                cache_type,
                {'bits': 4, 'compressed_size': compressed_size}
            )
            results.append(result)
            print(f"  Ratio: {result.compression_ratio:.3f}, MSE: {result.reconstruction_error:.4f}, "
                  f"Quality: {result.retrieval_quality:.4f}")

            # Sparsification (if applicable)
            if cache_type in [CacheType.MLP, CacheType.FFN]:
                sparsity = 1 - target_ratio
                print(f"Testing sparsification ({sparsity:.2f})...")
                start = time.time()
                values, indices = self.sparsify(combined, sparsity)
                compress_time = time.time() - start

                start = time.time()
                reconstructed = self.densify(values, indices, combined.shape)
                decompress_time = time.time() - start

                compressed_size = values.nbytes + indices.nbytes
                result = self.evaluate_compression(
                    combined,
                    reconstructed,
                    compress_time,
                    decompress_time,
                    CompressionMethod.SPARSIFICATION,
                    cache_type,
                    {'sparsity': sparsity, 'compressed_size': compressed_size}
                )
                results.append(result)
                print(f"  Ratio: {result.compression_ratio:.3f}, MSE: {result.reconstruction_error:.4f}, "
                      f"Quality: {result.retrieval_quality:.4f}")

            # Product Quantization
            print("Testing Product Quantization...")
            start = time.time()
            codebooks, encodings, subvec_sizes = self.product_quantize(combined.reshape(-1, 1))
            compress_time = time.time() - start

            start = time.time()
            reconstructed = self.pq_decode(codebooks, encodings, subvec_sizes)
            decompress_time = time.time() - start

            compressed_size = sum([cb.nbytes for cb in codebooks]) + sum([enc.nbytes for enc in encodings])
            result = self.evaluate_compression(
                combined,
                reconstructed,
                compress_time,
                decompress_time,
                CompressionMethod.PRODUCT_QUANTIZATION,
                cache_type,
                {'n_subvectors': len(codebooks), 'compressed_size': compressed_size}
            )
            results.append(result)
            print(f"  Ratio: {result.compression_ratio:.3f}, MSE: {result.reconstruction_error:.4f}, "
                  f"Quality: {result.retrieval_quality:.4f}")

        return results

    def find_optimal_strategy(
        self,
        results: List[CompressionResult],
        quality_threshold: float = 0.90
    ) -> Dict[str, Any]:
        """
        Find optimal compression strategy for each cache type

        Args:
            results: List of compression results
            quality_threshold: Minimum retrieval quality (cosine similarity)

        Returns:
            Optimal configuration
        """
        # Filter by quality threshold
        valid_results = [r for r in results if r.retrieval_quality >= quality_threshold]

        if not valid_results:
            print(f"Warning: No results meet quality threshold {quality_threshold}")
            valid_results = results

        # Sort by compression ratio (lower is better)
        valid_results.sort(key=lambda x: x.compression_ratio)

        best = valid_results[0]

        return {
            'method': best.method.value,
            'compression_ratio': best.compression_ratio,
            'quality': best.retrieval_quality,
            'mse': best.reconstruction_error,
            'parameters': best.parameters
        }

def main():
    """Main optimization loop"""
    print("="*60)
    print("KV-CACHE COMPRESSION OPTIMIZATION")
    print("="*60)

    compressor = KVCacheCompressor()
    all_results = {}
    optimal_configs = {}

    # Test each cache type
    cache_types = [
        CacheType.ATTENTION,
        CacheType.MLP,
        CacheType.EMBEDDING,
        CacheType.FFN
    ]

    for cache_type in cache_types:
        results = compressor.run_compression_experiment(cache_type)
        all_results[cache_type.value] = results

        # Find optimal strategy
        optimal = compressor.find_optimal_strategy(results, quality_threshold=0.92)
        optimal_configs[cache_type.value] = optimal

        print(f"\n*** OPTIMAL for {cache_type.value} ***")
        print(f"Method: {optimal['method']}")
        print(f"Compression Ratio: {optimal['compression_ratio']:.3f}")
        print(f"Quality: {optimal['quality']:.4f}")
        print(f"MSE: {optimal['mse']:.6f}")

    # Save results
    output = {
        'all_results': {
            cache_type: [
                {
                    'method': r.method.value,
                    'compression_ratio': r.compression_ratio,
                    'reconstruction_error': r.reconstruction_error,
                    'retrieval_quality': r.retrieval_quality,
                    'compression_time': r.compression_time,
                    'decompression_time': r.decompression_time,
                    'memory_saved': r.memory_saved,
                    'parameters': r.parameters
                }
                for r in results
            ]
            for cache_type, results in all_results.items()
        },
        'optimal_configs': optimal_configs
    }

    with open('simulations/optimization/memory/results/compression_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*60)
    print("Results saved to: simulations/optimization/memory/results/compression_results.json")
    print("="*60)

    return optimal_configs

if __name__ == '__main__':
    main()
