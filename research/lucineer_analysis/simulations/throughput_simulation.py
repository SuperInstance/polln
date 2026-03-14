"""
Lucineer Throughput Simulation
==============================

This simulation tests the claimed throughput of 80-150 tokens/second for
BitNet-b1.58-2B-4T architecture using TLMM (Table-Lookup MatMul) on FPGA.

Key Factors Modeled:
- LUT-based matrix multiplication performance
- Memory bandwidth constraints (DDR4 vs HBM)
- Batch size effects on throughput
- Sequence length impact
- Quantization (1.58-bit ternary weights)

Author: Throughput Benchmark Specialist
Date: 2026-03-13
"""

import numpy as np
import math
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
from enum import Enum


class MemoryType(Enum):
    """Memory configuration types"""
    DDR4_2400 = "DDR4-2400"  # 19.2 GB/s per channel
    DDR4_3200 = "DDR4-3200"  # 25.6 GB/s per channel
    HBM2 = "HBM2"           # 256 GB/s per stack
    HBM3 = "HBM3"           # 677 GB/s per stack


@dataclass
class HardwareConfig:
    """Hardware configuration parameters"""
    luts_available: int = 900_000  # Versal Premium VP180
    dsp_slices: int = 4_000
    memory_type: MemoryType = MemoryType.HBM2
    memory_channels: int = 2
    clock_frequency_mhz: int = 450
    pipeline_depth: int = 8


@dataclass
class ModelConfig:
    """BitNet-b1.58-2B-4T model configuration"""
    num_layers: int = 28
    hidden_dim: int = 2560
    intermediate_dim: int = 6912
    num_heads: int = 32
    head_dim: int = 80
    num_key_value_heads: int = 8
    vocab_size: int = 50_432
    bits_per_weight: float = 1.58  # Ternary: -1, 0, +1
    max_sequence_length: int = 4096


@dataclass
class ThroughputResult:
    """Simulation result"""
    tokens_per_second: float
    luts_used: int
    dsp_slices_used: int
    memory_bandwidth_gb_s: float
    utilization: float
    bottleneck: str
    confidence_interval: Tuple[float, float]


class TLMMSimulator:
    """
    Table-Lookup MatMul (TLMM) Performance Simulator

    Models the unique characteristics of LUT-based matrix multiplication
    for ternary weights (-1, 0, +1).
    """

    def __init__(self, hardware: HardwareConfig, model: ModelConfig):
        self.hw = hardware
        self.model = model
        self.rng = np.random.default_rng(42)

    def compute_lmm_operations(
        self,
        batch_size: int,
        seq_len: int,
        layer_idx: int = 0
    ) -> Dict[str, float]:
        """
        Compute operations for a single layer's matrix multiplications.

        For BitNet-b1.58, each layer has:
        - QKV projection: hidden_dim -> 3 * hidden_dim
        - Output projection: hidden_dim -> hidden_dim
        - FFN up projection: hidden_dim -> intermediate_dim
        - FFN down projection: intermediate_dim -> hidden_dim
        """
        M = batch_size * seq_len  # Batch sequence tokens
        K = self.model.hidden_dim
        N = self.model.hidden_dim

        # Operations for each MatMul (approximate with MACs)
        # With ternary weights, we use additions/subtractions instead of multiplications
        qkv_ops = M * K * (3 * N)
        output_ops = M * N * N
        ffn_up_ops = M * K * self.model.intermediate_dim
        ffn_down_ops = M * self.model.intermediate_dim * K

        total_ops = qkv_ops + output_ops + ffn_up_ops + ffn_down_ops

        # Convert to effective operations (ternary is cheaper than FP16)
        # Multiplication: 1 op -> Addition: 0.2 ops (approx)
        ternary_efficiency = 0.3
        effective_ops = total_ops * ternary_efficiency

        return {
            "total_ops": total_ops,
            "effective_ops": effective_ops,
            "qkv_ops": qkv_ops,
            "output_ops": output_ops,
            "ffn_ops": ffn_up_ops + ffn_down_ops
        }

    def estimate_lut_usage(
        self,
        batch_size: int,
        seq_len: int
    ) -> int:
        """
        Estimate LUT usage for parallel TLMM implementation.

        LUT usage scales with:
        - Parallelization factor (batch_size * seq_len)
        - Hidden dimension
        - Pipeline depth
        """
        # Base LUT usage for single MAC unit with ternary weights
        base_mac_luts = 150  # Ternary MAC is simpler than FP16 MAC

        # Parallelization factor
        parallel_factor = min(batch_size * seq_len, 128)  # Max parallelism limit

        # LUTs for parallel MAC array
        mac_array_luts = base_mac_luts * parallel_factor * self.model.hidden_dim

        # Pipeline registers (reduces to ~30% of combinational logic)
        pipeline_luts = mac_array_luts * 0.3 * self.hw.pipeline_depth

        # Control logic and buffers
        control_luts = mac_array_luts * 0.2

        total_luts = int(mac_array_luts + pipeline_luts + control_luts)

        return min(total_luts, self.hw.luts_available)

    def estimate_memory_bandwidth(
        self,
        batch_size: int,
        seq_len: int,
        tokens_per_step: int = 1
    ) -> float:
        """
        Estimate memory bandwidth requirements in GB/s.

        For autoregressive generation with TLMM (Table-Lookup MatMul):
        - Weights are stored in on-chip BRAM/LUT (ternary: -1, 0, +1)
        - Activations stream through compute units
        - KV cache is accessed once per token per layer
        """
        # Memory transfers per token generated
        bytes_per_activation = 2  # FP16 activations
        bytes_per_kv = 2  # FP16 KV cache

        # For autoregressive generation, we process ONE new token at a time
        # The existing seq_len tokens are in KV cache and are read for attention

        # Per-layer memory access:
        # 1. Read new token activation (hidden_dim)
        # 2. Read/write KV cache for new token (2 * hidden_dim for K+V)
        # 3. Read existing KV cache for attention (2 * seq_len * hidden_dim)
        # 4. Write output activation (hidden_dim)

        # New token processing (read + write)
        new_token_bytes = (
            batch_size * tokens_per_step * self.model.hidden_dim * bytes_per_activation * 2  # Read + write
        )

        # KV cache for new token (K + V)
        kv_new_bytes = (
            batch_size * tokens_per_step * 2 * self.model.hidden_dim * bytes_per_kv
        )

        # Existing KV cache reads (for attention computation)
        # This is read once per layer
        kv_existing_bytes = (
            batch_size * seq_len * 2 * self.model.hidden_dim * bytes_per_kv
        )

        # Total per layer (all layers must access their portion)
        per_layer_bytes = new_token_bytes + kv_new_bytes + kv_existing_bytes
        total_bytes = per_layer_bytes * self.model.num_layers

        # Convert to GB/s at target throughput
        # We want: total_bytes * target_tokens_per_second = bandwidth
        # For simulation, we compute bandwidth needed for 1 token
        bytes_per_second = total_bytes * 100  # Assuming 100 tok/s target

        return bytes_per_second / 1e9  # GB/s

    def compute_compute_time_ns(
        self,
        ops: float,
        parallel_factor: int
    ) -> float:
        """
        Compute time in nanoseconds for given operations.

        With TLMM (Table-Lookup MatMul) and pipelining:
        - Ternary weights allow table-lookup instead of multiplication
        - Each MAC is essentially: activation + weight_table[activation]
        - Much faster than traditional multiplication
        """
        # With TLMM, we process multiple activations per cycle
        # Each LUT can process 1 activation per cycle (table lookup)
        # With pipelining, we can achieve throughput > 1 operation/cycle

        # Effective operations per cycle (ternary is very efficient)
        ops_per_cycle = parallel_factor * self.hw.pipeline_depth * 2  # 2x for ternary efficiency

        # Cycles needed
        cycles_needed = ops / ops_per_cycle

        # Time in nanoseconds
        time_ns = cycles_needed * (1e3 / self.hw.clock_frequency_mhz)

        return time_ns

    def simulate_throughput(
        self,
        batch_size: int,
        seq_len: int,
        num_tokens: int = 100,
        Monte_carlo_runs: int = 100
    ) -> ThroughputResult:
        """
        Simulate throughput for given configuration with Monte Carlo uncertainty.
        """
        throughput_samples = []

        for _ in range(Monte_carlo_runs):
            # Add noise to clock frequency (±10%)
            clock_variation = self.rng.normal(1.0, 0.03)

            # Add noise to memory efficiency (±5%)
            memory_efficiency = self.rng.normal(0.85, 0.02)

            # Compute operations for all layers
            total_effective_ops = 0
            for layer in range(self.model.num_layers):
                layer_ops = self.compute_lmm_operations(batch_size, seq_len, layer)
                total_effective_ops += layer_ops["effective_ops"]

            # Estimate resource usage
            luts_used = self.estimate_lut_usage(batch_size, seq_len)
            parallel_factor = min(luts_used // 1000, batch_size * seq_len)

            # Compute time (compute-bound)
            compute_time_ns = self.compute_compute_time_ns(
                total_effective_ops / num_tokens,
                parallel_factor
            )

            # Memory bandwidth requirements
            memory_bandwidth = self.estimate_memory_bandwidth(batch_size, seq_len)

            # Available bandwidth (with variation)
            available_bandwidth = (
                self.get_memory_bandwidth() * memory_efficiency
            )

            # Memory time (memory-bound)
            if memory_bandwidth > available_bandwidth:
                memory_time_ns = (
                    (memory_bandwidth / available_bandwidth) *
                    compute_time_ns
                )
            else:
                memory_time_ns = compute_time_ns

            # Total time is max of compute and memory
            total_time_ns = max(compute_time_ns, memory_time_ns)

            # Throughput
            time_per_token_seconds = (total_time_ns / 1e9) / clock_variation
            tokens_per_second = 1.0 / time_per_token_seconds if time_per_token_seconds > 0 else 0

            throughput_samples.append(tokens_per_second)

        # Compute statistics
        mean_throughput = np.mean(throughput_samples)
        std_throughput = np.std(throughput_samples)
        ci_95 = (
            mean_throughput - 1.96 * std_throughput,
            mean_throughput + 1.96 * std_throughput
        )

        # Determine bottleneck
        utilization = luts_used / self.hw.luts_available

        if memory_bandwidth > available_bandwidth * 0.9:
            bottleneck = "MEMORY_BANDWIDTH"
        elif utilization > 0.85:
            bottleneck = "LUT_CAPACITY"
        elif parallel_factor < batch_size:
            bottleneck = "PARALLELISM"
        else:
            bottleneck = "COMPUTE"

        return ThroughputResult(
            tokens_per_second=mean_throughput,
            luts_used=luts_used,
            dsp_slices_used=min(parallel_factor * 2, self.hw.dsp_slices),
            memory_bandwidth_gb_s=memory_bandwidth,
            utilization=utilization,
            bottleneck=bottleneck,
            confidence_interval=ci_95
        )

    def get_memory_bandwidth(self) -> float:
        """Get total memory bandwidth in GB/s"""
        bandwidth_per_channel = {
            MemoryType.DDR4_2400: 19.2,
            MemoryType.DDR4_3200: 25.6,
            MemoryType.HBM2: 256.0,
            MemoryType.HBM3: 677.0,
        }
        return (
            bandwidth_per_channel[self.hw.memory_type] * self.hw.memory_channels
        )

    def run_sweep(
        self,
        batch_sizes: List[int],
        seq_lengths: List[int],
        memory_types: List[MemoryType]
    ) -> Dict[str, List[ThroughputResult]]:
        """Run parameter sweep across configurations"""
        results = {}

        for mem_type in memory_types:
            self.hw.memory_type = mem_type
            results[mem_type.value] = []

            for batch_size in batch_sizes:
                for seq_len in seq_lengths:
                    result = self.simulate_throughput(batch_size, seq_len)
                    results[mem_type.value].append(result)

        return results


class BottleneckAnalyzer:
    """Analyze bottlenecks preventing target throughput"""

    def __init__(self, target_tok_s: float = 80.0):
        self.target = target_tok_s

    def analyze(self, results: List[ThroughputResult]) -> Dict[str, any]:
        """Analyze results to identify bottlenecks"""
        bottlenecks = {}
        total = len(results)

        for result in results:
            bottleneck = result.bottleneck
            if bottleneck not in bottlenecks:
                bottlenecks[bottleneck] = {
                    "count": 0,
                    "avg_throughput": 0.0,
                    "worst_case": float('inf')
                }

            bottlenecks[bottleneck]["count"] += 1
            bottlenecks[bottleneck]["avg_throughput"] += result.tokens_per_second
            bottlenecks[bottleneck]["worst_case"] = min(
                bottlenecks[bottleneck]["worst_case"],
                result.tokens_per_second
            )

        # Compute averages
        for b in bottlenecks:
            bottlenecks[b]["avg_throughput"] /= bottlenecks[b]["count"]
            bottlenecks[b]["percentage"] = (bottlenecks[b]["count"] / total) * 100

        return bottlenecks

    def identify_critical_bottlenecks(
        self,
        analyzer_results: Dict[str, any]
    ) -> List[str]:
        """Identify bottlenecks that prevent reaching target"""
        critical = []

        for bottleneck, stats in analyzer_results.items():
            if stats["avg_throughput"] < self.target:
                critical.append(
                    f"{bottleneck}: {stats['avg_throughput']:.1f} tok/s "
                    f"({stats['percentage']:.1f}% of runs, "
                    f"worst: {stats['worst_case']:.1f} tok/s)"
                )

        return critical


def print_results(results: Dict[str, List[ThroughputResult]]):
    """Print simulation results in formatted table"""
    print("\n" + "="*100)
    print("LUCINEER THROUGHPUT SIMULATION RESULTS")
    print("="*100)
    print("\nTarget: 80-150 tokens/second")
    print("Model: BitNet-b1.58-2B-4T")
    print("Hardware: Versal Premium VP180 (900K LUTs)")
    print("\n" + "-"*100)

    for mem_type, mem_results in results.items():
        print(f"\n{mem_type} Configuration:")
        print("-" * 100)
        print(f"{'Batch':<8} {'SeqLen':<8} {'Throughput':<12} {'95% CI':<20} {'LUTs':<10} {'Bottleneck':<15}")
        print("-" * 100)

        idx = 0
        batch_sizes = [1, 2, 4, 8, 16, 32]
        seq_lengths = [128, 512, 1024, 2048, 4096]

        for batch_size in batch_sizes:
            for seq_len in seq_lengths:
                if idx < len(mem_results):
                    r = mem_results[idx]
                    ci_low, ci_high = r.confidence_interval

                    # Color code based on target
                    throughput_str = f"{r.tokens_per_second:.1f} tok/s"
                    if r.tokens_per_second < 80:
                        status = "[FAIL]"
                    elif r.tokens_per_second < 150:
                        status = "[WARN]"
                    else:
                        status = "[PASS]"

                    print(
                        f"{batch_size:<8} {seq_len:<8} "
                        f"{throughput_str:<12} "
                        f"[{ci_low:.1f}, {ci_high:.1f}]  "
                        f"{r.luts_used:<10} "
                        f"{r.bottleneck:<15} {status}"
                    )

                    idx += 1

    print("\n" + "="*100)


def main():
    """Main execution - run throughput simulation"""
    print("Lucineer Throughput Simulation")
    print("="*100)

    # Configure hardware (Versal Premium VP180 with HBM2)
    hardware = HardwareConfig(
        luts_available=900_000,
        dsp_slices=4_000,
        memory_type=MemoryType.HBM2,
        memory_channels=2,
        clock_frequency_mhz=450,
        pipeline_depth=8
    )

    # Configure model (BitNet-b1.58-2B-4T)
    model = ModelConfig(
        num_layers=28,
        hidden_dim=2560,
        intermediate_dim=6912,
        bits_per_weight=1.58
    )

    print(f"\nHardware Configuration:")
    print(f"  LUTs: {hardware.luts_available:,}")
    print(f"  DSP Slices: {hardware.dsp_slices:,}")
    print(f"  Memory: {hardware.memory_type.value} x{hardware.memory_channels}")
    print(f"  Clock: {hardware.clock_frequency_mhz} MHz")
    print(f"  Pipeline Depth: {hardware.pipeline_depth}")

    print(f"\nModel Configuration:")
    print(f"  Layers: {model.num_layers}")
    print(f"  Hidden Dim: {model.hidden_dim}")
    print(f"  Intermediate Dim: {model.intermediate_dim}")
    print(f"  Weight Precision: {model.bits_per_weight} bits (ternary)")

    # Create simulator
    simulator = TLMMSimulator(hardware, model)

    # Run parameter sweep
    batch_sizes = [1, 2, 4, 8, 16, 32]
    seq_lengths = [128, 512, 1024, 2048, 4096]
    memory_types = [
        MemoryType.DDR4_3200,
        MemoryType.HBM2
    ]

    print(f"\nRunning parameter sweep:")
    print(f"  Batch sizes: {batch_sizes}")
    print(f"  Sequence lengths: {seq_lengths}")
    print(f"  Memory types: {[m.value for m in memory_types]}")
    print(f"  Monte Carlo runs per config: 100")

    results = simulator.run_sweep(batch_sizes, seq_lengths, memory_types)

    # Print results
    print_results(results)

    # Analyze bottlenecks
    print("\n" + "="*100)
    print("BOTTLENECK ANALYSIS")
    print("="*100)

    analyzer = BottleneckAnalyzer(target_tok_s=80.0)

    for mem_type, mem_results in results.items():
        print(f"\n{mem_type}:")
        bottleneck_stats = analyzer.analyze(mem_results)

        print(f"{'Bottleneck':<20} {'Frequency':<12} {'Avg Throughput':<15} {'Worst Case':<12}")
        print("-" * 70)

        for bottleneck, stats in sorted(
            bottleneck_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        ):
            print(
                f"{bottleneck:<20} "
                f"{stats['percentage']:.1f}%        "
                f"{stats['avg_throughput']:<15.1f} "
                f"{stats['worst_case']:<12.1f}"
            )

        critical = analyzer.identify_critical_bottlenecks(bottleneck_stats)
        if critical:
            print(f"\n[!] CRITICAL BOTTLENECKS (below 80 tok/s target):")
            for c in critical:
                print(f"  - {c}")
        else:
            print(f"\n[+] All configurations meet target throughput!")

    # Summary statistics
    print("\n" + "="*100)
    print("SUMMARY STATISTICS")
    print("="*100)

    for mem_type, mem_results in results.items():
        throughputs = [r.tokens_per_second for r in mem_results]
        print(f"\n{mem_type}:")
        print(f"  Mean: {np.mean(throughputs):.1f} tok/s")
        print(f"  Median: {np.median(throughputs):.1f} tok/s")
        print(f"  Std Dev: {np.std(throughputs):.1f} tok/s")
        print(f"  Min: {np.min(throughputs):.1f} tok/s")
        print(f"  Max: {np.max(throughputs):.1f} tok/s")
        print(f"  % above 80 tok/s: {100 * np.mean([t > 80 for t in throughputs]):.1f}%")
        print(f"  % above 150 tok/s: {100 * np.mean([t > 150 for t in throughputs]):.1f}%")

    print("\n" + "="*100)
    print("SIMULATION COMPLETE")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
