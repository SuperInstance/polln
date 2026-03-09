"""
Pareto Optimization: Speed vs Quality Frontier

Finds optimal configurations balancing:
- Minimize latency (batch processing, parallelism, caching)
- Maximize quality (response quality, coherence, accuracy)

Uses NSGA-II for multiobjective optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class SpeedConfiguration:
    """Configuration for speed/quality optimization."""
    model_size: int  # Parameters (millions)
    batch_size: int  # Batch size
    max_parallel_requests: int  # Parallel processing
    kv_cache_size_mb: int  # KV-cache for speed
    compression_level: float  # 0-1, affects speed/quality tradeoff
    use_speculative_decoding: bool  # Speculative decoding
    use_quantization: bool  # Quantization for speed
    temperature: float  # Sampling temperature
    top_p: float  # Nucleus sampling
    max_tokens: int  # Maximum tokens per response

    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_size': self.model_size,
            'batch_size': self.batch_size,
            'max_parallel_requests': self.max_parallel_requests,
            'kv_cache_size_mb': self.kv_cache_size_mb,
            'compression_level': self.compression_level,
            'use_speculative_decoding': self.use_speculative_decoding,
            'use_quantization': self.use_quantization,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens
        }


class SpeedQualityEvaluator:
    """Evaluates latency and quality for speed-optimized configurations."""

    # Latency factors (ms per token, empirical)
    BASE_LATENCY_PER_TOKEN = 10  # ms per token
    MODEL_SIZE_LATENCY_FACTOR = 0.01  # Additional ms per 1M params
    BATCH_EFFICIENCY = 0.7  # Batch processing efficiency

    # Quality factors
    BASE_QUALITY = 0.8
    SPECULATIVE_QUALITY_PENALTY = 0.02
    QUANTIZATION_QUALITY_PENALTY = 0.03
    COMPRESSION_QUALITY_PENALTY = 0.05

    def __init__(self, avg_tokens_per_request: int = 500):
        self.avg_tokens_per_request = avg_tokens_per_request

    def estimate_latency_ms(self, config: SpeedConfiguration) -> float:
        """Estimate per-request latency in milliseconds."""
        # Base compute time
        compute_time = (self.BASE_LATENCY_PER_TOKEN +
                       config.model_size * self.MODEL_SIZE_LATENCY_FACTOR)
        total_latency = compute_time * self.avg_tokens_per_request

        # Batch efficiency (larger batches = better throughput)
        batch_efficiency = 1 - (1 - self.BATCH_EFFICIENCY) * np.exp(-config.batch_size / 10)
        total_latency /= batch_efficiency

        # KV-cache speedup
        cache_hit_rate = min(0.8, config.kv_cache_size_mb / 2048)  # Up to 80% hit rate
        total_latency *= (1 - 0.5 * cache_hit_rate)  # 50% faster on cache hits

        # Quantization speedup (2x faster, but quality loss)
        if config.use_quantization:
            total_latency *= 0.5

        # Speculative decoding speedup (1.5x faster, but quality loss)
        if config.use_speculative_decoding:
            total_latency *= 0.67

        # Compression speedup
        total_latency *= (1 - 0.2 * config.compression_level)

        # Parallel processing contention
        contention_factor = 1 + 0.1 * np.log(config.max_parallel_requests)
        total_latency *= contention_factor

        return total_latency

    def estimate_quality(self, config: SpeedConfiguration) -> float:
        """Estimate response quality (0-1)."""
        quality = self.BASE_QUALITY

        # Model size impact (diminishing returns)
        quality += 0.1 * (1 - np.exp(-config.model_size / 100))

        # Temperature penalty (higher temp = less coherent)
        quality *= (1 - 0.05 * config.temperature)

        # Top-p penalty (lower top_p = more deterministic = higher quality)
        quality *= (0.8 + 0.2 * config.top_p)

        # Speculative decoding penalty
        if config.use_speculative_decoding:
            quality *= (1 - self.SPECULATIVE_QUALITY_PENALTY)

        # Quantization penalty
        if config.use_quantization:
            quality *= (1 - self.QUANTIZATION_QUALITY_PENALTY)

        # Compression penalty
        quality *= (1 - self.COMPRESSION_QUALITY_PENALTY * config.compression_level)

        # Max tokens penalty (longer responses can lose coherence)
        length_penalty = min(0.05, config.max_tokens / 10000)
        quality *= (1 - length_penalty)

        return min(0.98, quality)

    def estimate_throughput(self, config: SpeedConfiguration) -> float:
        """Estimate requests per second."""
        latency_seconds = self.estimate_latency_ms(config) / 1000
        parallel_capacity = config.max_parallel_requests
        return parallel_capacity / latency_seconds


class NSGA2Optimizer:
    """NSGA-II optimizer specialized for speed/quality."""

    def __init__(self, population_size: int = 100, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.15
        self.crossover_rate = 0.8

    def dominates(self, obj1: Tuple[float, float], obj2: Tuple[float, float]) -> bool:
        """Check if obj1 dominates obj2 (minimize latency, maximize quality)."""
        lat1, qual1 = obj1
        lat2, qual2 = obj2
        return (lat1 <= lat2 and qual1 >= qual2) and (lat1 < lat2 or qual1 > qual2)

    def fast_non_dominated_sort(self, population: List[SpeedConfiguration],
                                evaluator: SpeedQualityEvaluator) -> List[List[SpeedConfiguration]]:
        """Sort population into Pareto fronts."""
        objectives = [(evaluator.estimate_latency_ms(ind),
                      evaluator.estimate_quality(ind))
                     for ind in population]

        domination_count = [0] * len(population)
        dominated_solutions = [[] for _ in range(len(population))]

        for i in range(len(population)):
            for j in range(len(population)):
                if i != j:
                    if self.dominates(objectives[i], objectives[j]):
                        dominated_solutions[i].append(j)
                    elif self.dominates(objectives[j], objectives[i]):
                        domination_count[i] += 1

        fronts = []
        current_front = [i for i in range(len(population)) if domination_count[i] == 0]

        fronts.append([population[i] for i in current_front])

        while current_front:
            next_front = []
            for i in current_front:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)

            if next_front:
                fronts.append([population[i] for i in next_front])
            current_front = next_front

        return fronts

    def crowding_distance(self, front: List[SpeedConfiguration],
                         evaluator: SpeedQualityEvaluator) -> List[float]:
        """Calculate crowding distance."""
        if len(front) <= 2:
            return [float('inf')] * len(front)

        latencies = [evaluator.estimate_latency_ms(ind) for ind in front]
        qualities = [evaluator.estimate_quality(ind) for ind in front]

        distances = [0.0] * len(front)

        # Latency distance
        lat_sorted = sorted(range(len(front)), key=lambda i: latencies[i])
        lat_range = latencies[lat_sorted[-1]] - latencies[lat_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = lat_sorted[i]
            distances[idx] += (latencies[lat_sorted[i + 1]] -
                             latencies[lat_sorted[i - 1]]) / lat_range

        # Quality distance
        qual_sorted = sorted(range(len(front)), key=lambda i: qualities[i])
        qual_range = qualities[qual_sorted[-1]] - qualities[qual_sorted[0]] + 1e-10

        for i in range(1, len(front) - 1):
            idx = qual_sorted[i]
            distances[idx] += (qualities[qual_sorted[i + 1]] -
                             qualities[qual_sorted[i - 1]]) / qual_range

        return distances

    def mutate(self, config: SpeedConfiguration) -> SpeedConfiguration:
        """Apply mutation."""
        def mutate_int(value: int, min_val: int, max_val: int) -> int:
            if np.random.random() < self.mutation_rate:
                delta = np.random.randint(-max_val // 10, max_val // 10 + 1)
                return np.clip(value + delta, min_val, max_val)
            return value

        def mutate_float(value: float, min_val: float, max_val: float) -> float:
            if np.random.random() < self.mutation_rate:
                delta = np.random.uniform(-0.1, 0.1)
                return np.clip(value + delta, min_val, max_val)
            return value

        def mutate_bool(value: bool) -> bool:
            if np.random.random() < self.mutation_rate:
                return not value
            return value

        return SpeedConfiguration(
            model_size=mutate_int(config.model_size, 10, 500),
            batch_size=mutate_int(config.batch_size, 1, 128),
            max_parallel_requests=mutate_int(config.max_parallel_requests, 1, 64),
            kv_cache_size_mb=mutate_int(config.kv_cache_size_mb, 128, 4096),
            compression_level=mutate_float(config.compression_level, 0.0, 1.0),
            use_speculative_decoding=mutate_bool(config.use_speculative_decoding),
            use_quantization=mutate_bool(config.use_quantization),
            temperature=mutate_float(config.temperature, 0.1, 1.5),
            top_p=mutate_float(config.top_p, 0.5, 1.0),
            max_tokens=mutate_int(config.max_tokens, 100, 4000)
        )

    def crossover(self, parent1: SpeedConfiguration, parent2: SpeedConfiguration) -> SpeedConfiguration:
        """Crossover between parents."""
        if np.random.random() > self.crossover_rate:
            return parent1

        return SpeedConfiguration(
            model_size=parent1.model_size if np.random.random() < 0.5 else parent2.model_size,
            batch_size=parent1.batch_size if np.random.random() < 0.5 else parent2.batch_size,
            max_parallel_requests=parent1.max_parallel_requests if np.random.random() < 0.5 else parent2.max_parallel_requests,
            kv_cache_size_mb=parent1.kv_cache_size_mb if np.random.random() < 0.5 else parent2.kv_cache_size_mb,
            compression_level=parent1.compression_level if np.random.random() < 0.5 else parent2.compression_level,
            use_speculative_decoding=parent1.use_speculative_decoding if np.random.random() < 0.5 else parent2.use_speculative_decoding,
            use_quantization=parent1.use_quantization if np.random.random() < 0.5 else parent2.use_quantization,
            temperature=parent1.temperature if np.random.random() < 0.5 else parent2.temperature,
            top_p=parent1.top_p if np.random.random() < 0.5 else parent2.top_p,
            max_tokens=parent1.max_tokens if np.random.random() < 0.5 else parent2.max_tokens
        )

    def optimize(self, evaluator: SpeedQualityEvaluator) -> List[SpeedConfiguration]:
        """Run NSGA-II optimization."""
        # Initialize population
        population = []
        for _ in range(self.population_size):
            population.append(SpeedConfiguration(
                model_size=np.random.randint(10, 500),
                batch_size=np.random.randint(1, 128),
                max_parallel_requests=np.random.randint(1, 64),
                kv_cache_size_mb=np.random.randint(128, 4096),
                compression_level=np.random.uniform(0.0, 1.0),
                use_speculative_decoding=np.random.choice([True, False]),
                use_quantization=np.random.choice([True, False]),
                temperature=np.random.uniform(0.1, 1.5),
                top_p=np.random.uniform(0.5, 1.0),
                max_tokens=np.random.randint(100, 4000)
            ))

        # Evolution
        for generation in range(self.generations):
            fronts = self.fast_non_dominated_sort(population, evaluator)

            offspring = []
            while len(offspring) < self.population_size:
                parent1 = population[np.random.randint(0, len(fronts[0]))]
                parent2 = population[np.random.randint(0, len(fronts[0]))]
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                offspring.append(child)

            population += offspring
            fronts = self.fast_non_dominated_sort(population, evaluator)

            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend(front)
                else:
                    distances = self.crowding_distance(front, evaluator)
                    sorted_by_distance = sorted(zip(front, distances),
                                              key=lambda x: x[1], reverse=True)
                    remaining = self.population_size - len(new_population)
                    new_population.extend([x[0] for x in sorted_by_distance[:remaining]])
                    break

            population = new_population[:self.population_size]

            if (generation + 1) % 10 == 0:
                print(f"Generation {generation + 1}/{self.generations}")

        fronts = self.fast_non_dominated_sort(population, evaluator)
        return fronts[0]


def plot_speed_quality_frontier(pareto_front: List[SpeedConfiguration],
                               evaluator: SpeedQualityEvaluator,
                               save_path: str = None):
    """Plot speed vs quality frontier."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    latencies = [evaluator.estimate_latency_ms(c) for c in pareto_front]
    qualities = [evaluator.estimate_quality(c) for c in pareto_front]
    throughputs = [evaluator.estimate_throughput(c) for c in pareto_front]

    # Plot 1: Latency vs Quality
    scatter = ax1.scatter(latencies, qualities, c=throughputs, cmap='RdYlGn', s=50, alpha=0.6)
    ax1.set_xlabel('Latency (ms)')
    ax1.set_ylabel('Quality Score')
    ax1.set_title('Pareto Frontier: Latency vs Quality')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Throughput (req/s)')

    # Plot 2: Model Size vs Batch Size
    model_sizes = [c.model_size for c in pareto_front]
    batch_sizes = [c.batch_size for c in pareto_front]
    ax2.scatter(model_sizes, batch_sizes, c=qualities, cmap='viridis', s=50, alpha=0.6)
    ax2.set_xlabel('Model Size (M params)')
    ax2.set_ylabel('Batch Size')
    ax2.set_title('Configuration Space (colored by quality)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(ax2.collections[0], ax=ax2, label='Quality')

    # Plot 3: Latency tiers
    sorted_by_latency = sorted(zip(latencies, qualities), key=lambda x: x[0])
    latency_tiers = {
        'Real-time (<100ms)': [l for l in latencies if l < 100],
        'Interactive (100-500ms)': [l for l in latencies if 100 <= l < 500],
        'Batch (500-2000ms)': [l for l in latencies if 500 <= l < 2000],
        'Slow (>2000ms)': [l for l in latencies if l >= 2000]
    }
    ax3.bar(latency_tiers.keys(), [len(v) for v in latency_tiers.values()])
    ax3.set_ylabel('Number of Configurations')
    ax3.set_title('Configurations by Latency Tier')
    ax3.tick_params(axis='x', rotation=45)

    # Plot 4: Throughput vs Quality
    ax4.scatter(throughputs, qualities, c=latencies, cmap='coolwarm', s=50, alpha=0.6)
    ax4.set_xlabel('Throughput (requests/second)')
    ax4.set_ylabel('Quality Score')
    ax4.set_title('Throughput vs Quality (colored by latency)')
    ax4.grid(True, alpha=0.3)
    plt.colorbar(ax4.collections[0], ax=ax4, label='Latency (ms)')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()


def generate_latency_tier_configs(pareto_front: List[SpeedConfiguration],
                                 evaluator: SpeedQualityEvaluator,
                                 output_dir: str) -> Dict[str, Dict]:
    """Generate configurations for different latency tiers."""
    results = []
    for config in pareto_front:
        results.append({
            'config': config,
            'latency_ms': evaluator.estimate_latency_ms(config),
            'quality': evaluator.estimate_quality(config),
            'throughput': evaluator.estimate_throughput(config)
        })

    # Define latency tiers
    tiers = {
        'REALTIME': None,   # < 100ms
        'INTERACTIVE': None,  # 100-500ms
        'FAST': None,        # 500-1000ms
        'STANDARD': None,    # 1000-2000ms
        'BATCH': None        # > 2000ms
    }

    # Find best quality config in each tier
    for tier, max_latency in [
        ('REALTIME', 100),
        ('INTERACTIVE', 500),
        ('FAST', 1000),
        ('STANDARD', 2000),
        ('BATCH', float('inf'))
    ]:
        tier_configs = [r for r in results if r['latency_ms'] < max_latency]
        if tier_configs:
            # Pick best quality
            best = max(tier_configs, key=lambda x: x['quality'])
            tiers[tier] = best

    # Generate configs
    configs = {}
    for tier_name, tier_data in tiers.items():
        if tier_data is None:
            continue

        config = tier_data['config']
        configs[tier_name] = {
            'model_size': f"{config.model_size}M",
            'batch_size': config.batch_size,
            'max_parallel_requests': config.max_parallel_requests,
            'kv_cache_size': f"{config.kv_cache_size_mb}MB",
            'compression_level': round(config.compression_level, 2),
            'use_speculative_decoding': config.use_speculative_decoding,
            'use_quantization': config.use_quantization,
            'temperature': round(config.temperature, 2),
            'top_p': round(config.top_p, 2),
            'max_tokens': config.max_tokens,
            'expected_latency_ms': round(tier_data['latency_ms'], 1),
            'expected_quality': round(tier_data['quality'], 3),
            'expected_throughput': round(tier_data['throughput'], 1),
            'target': 'speed_quality_balance'
        }

    # Save
    output_path = Path(output_dir) / 'speed_quality_tiers.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)

    print(f"Generated {len(configs)} latency tier configs")
    print(f"Saved to {output_path}")

    return configs


def main():
    """Main optimization pipeline."""
    print("=" * 60)
    print("Pareto Optimization: Speed vs Quality")
    print("=" * 60)

    evaluator = SpeedQualityEvaluator(avg_tokens_per_request=500)
    optimizer = NSGA2Optimizer(population_size=100, generations=50)

    print("\nRunning NSGA-II optimization...")
    pareto_front = optimizer.optimize(evaluator)
    print(f"\nFound {len(pareto_front)} Pareto-optimal configurations")

    # Statistics
    latencies = [evaluator.estimate_latency_ms(c) for c in pareto_front]
    qualities = [evaluator.estimate_quality(c) for c in pareto_front]

    print(f"\nLatency range: {min(latencies):.1f} - {max(latencies):.1f} ms")
    print(f"Quality range: {min(qualities):.3f} - {max(qualities):.3f}")

    # Plot
    output_dir = Path(__file__).parent.parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / 'pareto_speed_quality.png'
    plot_speed_quality_frontier(pareto_front, evaluator, str(plot_path))

    # Generate tier configs
    config_dir = Path(__file__).parent.parent.parent / '..' / 'src' / 'core' / 'config' / 'tiers'
    tier_configs = generate_latency_tier_configs(pareto_front, evaluator, str(config_dir))

    # Print summaries
    print("\n" + "=" * 60)
    print("Latency Tier Summaries:")
    print("=" * 60)
    for tier, config in tier_configs.items():
        print(f"\n{tier}:")
        print(f"  Latency: {config['expected_latency_ms']:.1f}ms")
        print(f"  Quality: {config['expected_quality']:.3f}")
        print(f"  Throughput: {config['expected_throughput']:.1f} req/s")
        print(f"  Model: {config['model_size']}, Batch: {config['batch_size']}")

    return pareto_front, tier_configs


if __name__ == '__main__':
    main()
