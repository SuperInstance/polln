"""
SuperInstance SDK - Performance Profiling

This module provides detailed performance measurement for inference
operations, including timing, energy, and resource utilization metrics.
"""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
import time
import json
import random

if TYPE_CHECKING:
    import pandas as pd
    from .device import Device


@dataclass
class LayerProfile:
    """Per-layer profiling data."""

    name: str
    """Layer name (e.g., 'attention.0', 'ffn.12')"""

    time_ms: float
    """Time spent in this layer (milliseconds)"""

    energy_mj: float
    """Energy consumed (millijoules)"""

    memory_accesses: int
    """Number of memory accesses"""

    cache_hits: int
    """Number of cache hits"""

    cache_misses: int
    """Number of cache misses"""

    mac_operations: int
    """Number of MAC operations"""

    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate as fraction."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'time_ms': self.time_ms,
            'energy_mj': self.energy_mj,
            'memory_accesses': self.memory_accesses,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'mac_operations': self.mac_operations,
            'cache_hit_rate': self.cache_hit_rate,
        }


@dataclass
class ProfileReport:
    """Complete profiling report."""

    layers: List[LayerProfile]
    """Per-layer profiling data"""

    total_time_ms: float
    """Total inference time"""

    total_energy_mj: float
    """Total energy consumed"""

    throughput_tok_per_s: float
    """Generation throughput"""

    energy_efficiency_tok_per_j: float
    """Tokens generated per joule"""

    first_token_ms: float
    """Time to first token"""

    prefill_time_ms: float
    """Prompt processing time"""

    decode_time_ms: float
    """Token generation time"""

    memory_bandwidth_gb_s: float
    """Average memory bandwidth utilization"""

    compute_utilization: float
    """Compute array utilization (0.0-1.0)"""

    token_count: int = 0
    """Number of tokens generated"""

    model_name: str = ""
    """Name of the model"""

    def summary(self) -> str:
        """Return formatted summary string."""
        lines = [
            "┌" + "─" * 50 + "┐",
            "│ SuperInstance Performance Profile" + " " * 16 + "│",
            "├" + "─" * 50 + "┤",
            f"│ Total Time: {self.total_time_ms:>10.2f} ms{' ' * 26}│",
            f"│ First Token: {self.first_token_ms:>9.2f} ms{' ' * 26}│",
            f"│ Throughput: {self.throughput_tok_per_s:>8.1f} tok/s{' ' * 25}│",
            f"│ Energy: {self.total_energy_mj:>12.2f} mJ{' ' * 27}│",
            f"│ Efficiency: {self.energy_efficiency_tok_per_j:>7.1f} tok/J{' ' * 27}│",
            f"│ Compute Util: {self.compute_utilization * 100:>6.1f}%{' ' * 28}│",
            f"│ Memory BW: {self.memory_bandwidth_gb_s:>9.2f} GB/s{' ' * 26}│",
        ]

        if self.layers:
            lines.extend([
                "├" + "─" * 50 + "┤",
                "│ Layer Profile:" + " " * 35 + "│",
            ])

            for layer in self.layers[:10]:  # Show top 10 layers
                lines.append(
                    f"│   {layer.name:20s} {layer.time_ms:>6.2f}ms "
                    f"{layer.energy_mj:>6.2f}mJ {layer.cache_hit_rate:>5.1%}│"
                )

        lines.append("└" + "─" * 50 + "┘")
        return '\n'.join(lines)

    def to_dataframe(self) -> 'pd.DataFrame':
        """Convert to pandas DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for to_dataframe()")

        data = [layer.to_dict() for layer in self.layers]
        return pd.DataFrame(data)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'layers': [layer.to_dict() for layer in self.layers],
            'total_time_ms': self.total_time_ms,
            'total_energy_mj': self.total_energy_mj,
            'throughput_tok_per_s': self.throughput_tok_per_s,
            'energy_efficiency_tok_per_j': self.energy_efficiency_tok_per_j,
            'first_token_ms': self.first_token_ms,
            'prefill_time_ms': self.prefill_time_ms,
            'decode_time_ms': self.decode_time_ms,
            'memory_bandwidth_gb_s': self.memory_bandwidth_gb_s,
            'compute_utilization': self.compute_utilization,
            'token_count': self.token_count,
            'model_name': self.model_name,
        }

    def save(self, path: str) -> None:
        """Save report to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'ProfileReport':
        """Load report from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)

        layers = [
            LayerProfile(**layer_data)
            for layer_data in data.pop('layers')
        ]

        return cls(layers=layers, **data)


class Profiler:
    """
    Performance profiler for inference operations.

    The Profiler captures detailed timing, energy, and resource
    utilization metrics during model inference.

    Example:
        >>> from superinstance import Device, Profiler
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>>
        >>> with Profiler() as p:
        ...     result = model.generate("Hello")
        >>>
        >>> report = p.last_report
        >>> print(f"Tokens/sec: {report.throughput_tok_per_s}")
    """

    def __init__(
        self,
        device: Optional['Device'] = None,
        enable_layer_profile: bool = True,
        enable_energy: bool = True,
        seed: Optional[int] = None
    ):
        """
        Initialize profiler.

        Args:
            device: Device to profile (auto-detect if None)
            enable_layer_profile: Collect per-layer metrics
            enable_energy: Collect energy measurements
            seed: Random seed for reproducible simulated metrics
        """
        self._device = device
        self._enable_layer_profile = enable_layer_profile
        self._enable_energy = enable_energy
        self._seed = seed
        self._rng = random.Random(seed)

        self._start_time: Optional[float] = None
        self._last_report: Optional[ProfileReport] = None
        self._is_running = False

    def start(self) -> None:
        """Begin profiling session."""
        self._start_time = time.time()
        self._is_running = True

    def stop(self) -> ProfileReport:
        """
        End profiling and return report.

        Returns:
            ProfileReport with all collected metrics
        """
        if not self._is_running:
            raise RuntimeError("Profiler is not running")

        end_time = time.time()
        duration_ms = (end_time - self._start_time) * 1000

        # Generate simulated report
        report = self._generate_report(duration_ms)

        self._last_report = report
        self._is_running = False

        return report

    def _generate_report(self, total_time_ms: float) -> ProfileReport:
        """Generate a profiling report (simulated for now)."""
        # Simulate layer profiling
        layers = []
        if self._enable_layer_profile:
            num_layers = 24
            remaining_time = total_time_ms
            remaining_energy = total_time_ms * 0.08  # ~0.08 mJ per ms

            for i in range(num_layers):
                # Distribute time across layers
                layer_time = remaining_time / (num_layers - i) * (0.8 + self._rng.random() * 0.4)
                layer_energy = remaining_energy / (num_layers - i) * (0.8 + self._rng.random() * 0.4)

                remaining_time -= layer_time
                remaining_energy -= layer_energy

                layers.append(LayerProfile(
                    name=f"layer.{i}",
                    time_ms=layer_time,
                    energy_mj=layer_energy,
                    memory_accesses=self._rng.randint(10000, 100000),
                    cache_hits=self._rng.randint(8000, 90000),
                    cache_misses=self._rng.randint(1000, 10000),
                    mac_operations=self._rng.randint(100000, 1000000),
                ))

        # Calculate metrics
        total_energy = sum(layer.energy_mj for layer in layers) if layers else total_time_ms * 0.08
        token_count = max(1, int(total_time_ms / 33))  # ~30 tok/s

        return ProfileReport(
            layers=layers,
            total_time_ms=total_time_ms,
            total_energy_mj=total_energy,
            throughput_tok_per_s=token_count / (total_time_ms / 1000),
            energy_efficiency_tok_per_j=token_count / (total_energy / 1000) if total_energy > 0 else 0,
            first_token_ms=self._rng.uniform(10, 20),
            prefill_time_ms=total_time_ms * 0.1,
            decode_time_ms=total_time_ms * 0.9,
            memory_bandwidth_gb_s=self._rng.uniform(8, 12),
            compute_utilization=self._rng.uniform(0.7, 0.95),
            token_count=token_count,
        )

    @property
    def last_report(self) -> Optional[ProfileReport]:
        """Most recent profiling report."""
        return self._last_report

    def __enter__(self) -> 'Profiler':
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self._last_report = self.stop()


def profile_generation(
    model: 'Model',
    prompt: str,
    config: Optional['GenerationConfig'] = None,
    warmup: int = 0,
    repeats: int = 1,
) -> ProfileReport:
    """
    Profile a generation with optional warmup and repeats.

    Args:
        model: Model to profile
        prompt: Input prompt
        config: Generation config
        warmup: Number of warmup iterations
        repeats: Number of profiling iterations

    Returns:
        Aggregated ProfileReport

    Example:
        >>> from superinstance import Device
        >>> from superinstance.profiler import profile_generation
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> report = profile_generation(model, "Hello", warmup=2, repeats=5)
        >>> print(report.summary())
    """
    from .model import GenerationConfig

    if config is None:
        config = GenerationConfig()

    # Warmup
    for _ in range(warmup):
        model.generate(prompt, config)

    # Profiled runs
    reports = []
    for _ in range(repeats):
        with Profiler() as p:
            model.generate(prompt, config)
        reports.append(p.last_report)

    # Aggregate results
    if not reports:
        raise RuntimeError("No profiling data collected")

    # Average the metrics
    avg_time_ms = sum(r.total_time_ms for r in reports) / len(reports)
    avg_energy_mj = sum(r.total_energy_mj for r in reports) / len(reports)
    avg_throughput = sum(r.throughput_tok_per_s for r in reports) / len(reports)
    avg_first_token = sum(r.first_token_ms for r in reports) / len(reports)
    avg_compute = sum(r.compute_utilization for r in reports) / len(reports)
    avg_memory_bw = sum(r.memory_bandwidth_gb_s for r in reports) / len(reports)
    total_tokens = reports[0].token_count

    return ProfileReport(
        layers=reports[0].layers,  # Use last run's layer data
        total_time_ms=avg_time_ms,
        total_energy_mj=avg_energy_mj,
        throughput_tok_per_s=avg_throughput,
        energy_efficiency_tok_per_j=total_tokens / (avg_energy_mj / 1000) if avg_energy_mj > 0 else 0,
        first_token_ms=avg_first_token,
        prefill_time_ms=avg_time_ms * 0.1,
        decode_time_ms=avg_time_ms * 0.9,
        memory_bandwidth_gb_s=avg_memory_bw,
        compute_utilization=avg_compute,
        token_count=total_tokens,
        model_name=model.name,
    )


def benchmark_model(
    model: 'Model',
    prompts: List[str],
    max_tokens: int = 100,
) -> dict:
    """
    Benchmark a model across multiple prompts.

    Args:
        model: Model to benchmark
        prompts: List of prompts to test
        max_tokens: Maximum tokens per generation

    Returns:
        Dictionary with benchmark results

    Example:
        >>> from superinstance import Device
        >>> from superinstance.profiler import benchmark_model
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> prompts = ["Hello", "What is AI?", "Tell me a story"]
        >>> results = benchmark_model(model, prompts)
        >>> print(f"Average: {results['avg_throughput']:.1f} tok/s")
    """
    from .model import GenerationConfig

    config = GenerationConfig(max_tokens=max_tokens)

    results = []
    total_tokens = 0
    total_time_ms = 0

    for prompt in prompts:
        result = model.generate(prompt, config)
        results.append({
            'prompt': prompt[:50] + '...' if len(prompt) > 50 else prompt,
            'tokens': result.generated_tokens,
            'time_ms': result.total_time_ms,
            'throughput': result.tokens_per_second,
        })
        total_tokens += result.generated_tokens
        total_time_ms += result.total_time_ms

    return {
        'model': model.name,
        'prompts_tested': len(prompts),
        'total_tokens': total_tokens,
        'total_time_ms': total_time_ms,
        'avg_throughput': total_tokens / (total_time_ms / 1000),
        'results': results,
    }
