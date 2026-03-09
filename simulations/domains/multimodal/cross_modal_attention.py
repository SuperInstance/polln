"""
Cross-Modal Attention Optimization for POLLN

Tests different fusion strategies for multi-modal inputs:
- Early fusion: combine embeddings at input layer
- Late fusion: process separately, combine at output layer
- Hierarchical fusion: progressive combination at multiple layers

Measures:
- Attention efficiency (computation vs quality tradeoff)
- Alignment quality (how well modalities are aligned)
- Fusion effectiveness (quality improvement from fusion)
- Scalability (performance with more modalities)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
import json
import time


class FusionStrategy(Enum):
    EARLY = "early"
    LATE = "late"
    HIERARCHICAL = "hierarchical"
    CO_ATTENTION = "co_attention"
    TRANSFORMER_FUSION = "transformer_fusion"


@dataclass
class AttentionConfig:
    """Configuration for attention mechanism"""
    strategy: FusionStrategy
    n_heads: int = 8
    dim_per_head: int = 64
    dropout: float = 0.1
    temperature: float = 1.0
    n_layers: int = 2


@dataclass
class AttentionMetrics:
    """Metrics for attention evaluation"""
    fusion_quality: float  # 0-1, improvement over unimodal
    alignment_score: float  # 0-1, cross-modal alignment
    attention_entropy: float  # entropy of attention weights
    computation_flops: float  # computational cost
    memory_mb: float  # memory usage
    latency_ms: float  # inference time
    modality_importance: Dict[str, float] = field(default_factory=dict)


class CrossModalAttention:
    """Simulates cross-modal attention mechanisms"""

    def __init__(self, config: AttentionConfig):
        self.config = config
        self.embedding_dim = config.n_heads * config.dim_per_head

    def compute_attention(
        self,
        query_modality: str,
        key_modalities: Dict[str, np.ndarray],
        value_modalities: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Compute cross-modal attention"""

        if self.config.strategy == FusionStrategy.EARLY:
            return self._early_fusion(key_modalities, value_modalities)
        elif self.config.strategy == FusionStrategy.LATE:
            return self._late_fusion(key_modalities, value_modalities)
        elif self.config.strategy == FusionStrategy.HIERARCHICAL:
            return self._hierarchical_fusion(key_modalities, value_modalities)
        elif self.config.strategy == FusionStrategy.CO_ATTENTION:
            return self._co_attention(key_modalities, value_modalities)
        else:
            return self._transformer_fusion(key_modalities, value_modalities)

    def _early_fusion(
        self,
        keys: Dict[str, np.ndarray],
        values: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Early fusion: concatenate and project"""
        # Concatenate all modalities
        all_embeddings = np.concatenate(list(values.values()))
        # Simulate projection
        fused = np.mean(list(values.values()), axis=0)

        # Equal importance for early fusion
        importance = {k: 1.0 / len(values) for k in values.keys()}
        return fused, importance

    def _late_fusion(
        self,
        keys: Dict[str, np.ndarray],
        values: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Late fusion: process separately, combine at output"""
        # Simulate separate processing
        processed = {}
        for modality, embedding in values.items():
            # Simulate modality-specific processing
            processed[modality] = embedding * (1 + np.random.randn() * 0.1)

        # Learned attention weights
        attention_weights = np.random.rand(len(processed))
        attention_weights = np.softmax(attention_weights / self.config.temperature)

        # Combine with attention
        fused = np.zeros_like(list(processed.values())[0])
        importance = {}
        for (modality, embedding), weight in zip(processed.items(), attention_weights):
            fused += embedding * weight
            importance[modality] = weight

        return fused, importance

    def _hierarchical_fusion(
        self,
        keys: Dict[str, np.ndarray],
        values: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Hierarchical fusion: progressive combination"""
        modalities = list(values.keys())
        n_levels = self.config.n_layers

        # Build hierarchy
        current_embeddings = values.copy()
        importance = {k: 0.0 for k in modalities}

        for level in range(n_levels):
            if len(current_embeddings) <= 1:
                break

            # Pairwise fusion
            new_embeddings = {}
            pairs = list(current_embeddings.items())

            for i in range(0, len(pairs), 2):
                if i + 1 < len(pairs):
                    mod1, emb1 = pairs[i]
                    mod2, emb2 = pairs[i + 1]

                    # Fuse pair
                    weight = np.random.rand()
                    fused_emb = emb1 * weight + emb2 * (1 - weight)
                    new_name = f"{mod1}+{mod2}"
                    new_embeddings[new_name] = fused_emb

                    # Accumulate importance
                    importance[mod1] += weight / n_levels
                    importance[mod2] += (1 - weight) / n_levels
                else:
                    # Odd one out
                    mod, emb = pairs[i]
                    new_embeddings[mod] = emb
                    importance[mod] += 1.0 / n_levels

            current_embeddings = new_embeddings

        # Final fusion
        fused = np.mean(list(current_embeddings.values()), axis=0)
        return fused, importance

    def _co_attention(
        self,
        keys: Dict[str, np.ndarray],
        values: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Co-attention: bidirectional attention between modalities"""
        modalities = list(values.keys())

        # Simulate co-attention matrix
        n_modalities = len(modalities)
        co_attention_matrix = np.random.rand(n_modalities, n_modalities)

        # Normalize row-wise
        co_attention_matrix = co_attention_matrix / co_attention_matrix.sum(axis=1, keepdims=True)

        # Apply co-attention
        attended = {}
        for i, modality in enumerate(modalities):
            attended[modality] = np.zeros_like(values[modality])
            for j, other_mod in enumerate(modalities):
                attended[modality] += values[other_mod] * co_attention_matrix[i, j]

        # Combine attended representations
        fused = np.mean(list(attended.values()), axis=0)

        # Importance from attention matrix
        importance = {}
        for i, modality in enumerate(modalities):
            importance[modality] = co_attention_matrix[i].sum()

        return fused, importance

    def _transformer_fusion(
        self,
        keys: Dict[str, np.ndarray],
        values: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Transformer-style cross-attention"""
        # Stack embeddings
        embeddings_list = list(values.values())
        stacked = np.stack(embeddings_list, axis=0)  # (n_modalities, dim)

        # Multi-head attention simulation
        n_heads = self.config.n_heads
        dim_per_head = self.config.dim_per_head

        # Simulate attention weights
        attention_weights = np.random.rand(len(values), n_heads)
        attention_weights = attention_weights / attention_weights.sum(axis=0, keepdims=True)

        # Apply attention
        fused = np.zeros(self.embedding_dim)
        importance = {}

        for i, (modality, embedding) in enumerate(values.items()):
            head_weights = attention_weights[i]
            # Simulate multi-head processing
            head_contributions = []
            for h in range(n_heads):
                head_dim = dim_per_head
                head_embedding = embedding[:head_dim] * head_weights[h]
                head_contributions.append(head_embedding)

            # Concatenate heads
            multi_head = np.concatenate(head_contributions)
            fused += multi_head
            importance[modality] = head_weights.mean()

        return fused / len(values), importance


class AttentionBenchmark:
    """Benchmark different attention/fusion strategies"""

    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials

    def benchmark_strategy(
        self,
        config: AttentionConfig,
        modality_sets: List[List[str]]
    ) -> AttentionMetrics:
        """Benchmark a specific fusion strategy"""
        attention = CrossModalAttention(config)

        fusion_scores = []
        alignment_scores = []
        entropies = []
        latencies = []
        modality_importance = {m: [] for m in
                              ['text', 'image', 'audio', 'code']}

        for trial in range(self.n_trials):
            for modalities in modality_sets:
                # Simulate multi-modal input
                embeddings = self._generate_mock_embeddings(modalities)

                # Compute attention
                start_time = time.time()
                query = modalities[0] if modalities else 'text'
                fused, importance = attention.compute_attention(
                    query, embeddings, embeddings
                )
                latency = (time.time() - start_time) * 1000

                # Measure fusion quality
                fusion_quality = self._measure_fusion_quality(embeddings, fused)

                # Measure alignment
                alignment = self._measure_alignment(embeddings)

                # Compute attention entropy
                entropy = self._compute_entropy(importance)

                fusion_scores.append(fusion_quality)
                alignment_scores.append(alignment)
                entropies.append(entropy)
                latencies.append(latency)

                for mod, imp in importance.items():
                    if mod in modality_importance:
                        modality_importance[mod].append(imp)

        # Compute averages
        avg_fusion = np.mean(fusion_scores)
        avg_alignment = np.mean(alignment_scores)
        avg_entropy = np.mean(entropies)
        avg_latency = np.mean(latencies)
        avg_importance = {k: np.mean(v) for k, v in modality_importance.items() if v}

        # Estimate computation
        flops = self._estimate_flops(config)
        memory = self._estimate_memory(config)

        return AttentionMetrics(
            fusion_quality=avg_fusion,
            alignment_score=avg_alignment,
            attention_entropy=avg_entropy,
            computation_flops=flops,
            memory_mb=memory,
            latency_ms=avg_latency,
            modality_importance=avg_importance
        )

    def _generate_mock_embeddings(self, modalities: List[str]) -> Dict[str, np.ndarray]:
        """Generate mock embeddings for modalities"""
        embeddings = {}
        for modality in modalities:
            # Different dimensions for different modalities
            if modality == 'image':
                dim = 512
            elif modality == 'audio':
                dim = 384
            else:
                dim = 768
            embeddings[modality] = np.random.randn(dim) * 0.1
        return embeddings

    def _measure_fusion_quality(
        self,
        embeddings: Dict[str, np.ndarray],
        fused: np.ndarray
    ) -> float:
        """Measure how well fusion preserves information"""
        # Correlation with individual modalities
        correlations = []
        for embedding in embeddings.values():
            # Pad to same size
            max_len = max(len(fused), len(embedding))
            fused_padded = np.pad(fused, (0, max_len - len(fused)))
            emb_padded = np.pad(embedding, (0, max_len - len(embedding)))

            corr = abs(np.corrcoef(fused_padded, emb_padded)[0, 1])
            correlations.append(corr)

        # Fusion quality: high correlation with all modalities
        return np.mean(correlations) if correlations else 0.5

    def _measure_alignment(self, embeddings: Dict[str, np.ndarray]) -> float:
        """Measure cross-modal alignment"""
        if len(embeddings) < 2:
            return 1.0

        embeddings_list = list(embeddings.values())
        correlations = []
        for i in range(len(embeddings_list)):
            for j in range(i + 1, len(embeddings_list)):
                max_len = max(len(embeddings_list[i]), len(embeddings_list[j]))
                emb_i = np.pad(embeddings_list[i], (0, max_len - len(embeddings_list[i])))
                emb_j = np.pad(embeddings_list[j], (0, max_len - len(embeddings_list[j])))

                corr = abs(np.corrcoef(emb_i, emb_j)[0, 1])
                correlations.append(corr)

        return np.mean(correlations) if correlations else 0.5

    def _compute_entropy(self, importance: Dict[str, float]) -> float:
        """Compute entropy of attention weights"""
        weights = np.array(list(importance.values()))
        # Normalize
        weights = weights / weights.sum()
        # Entropy
        entropy = -np.sum(weights * np.log(weights + 1e-10))
        return entropy

    def _estimate_flops(self, config: AttentionConfig) -> float:
        """Estimate computational cost in FLOPs"""
        base_flops = config.n_heads * config.dim_per_head * config.n_layers

        if config.strategy == FusionStrategy.EARLY:
            return base_flops * 1.0
        elif config.strategy == FusionStrategy.LATE:
            return base_flops * 1.2
        elif config.strategy == FusionStrategy.HIERARCHICAL:
            return base_flops * 1.5
        elif config.strategy == FusionStrategy.CO_ATTENTION:
            return base_flops * 2.0
        else:  # transformer
            return base_flops * 1.8

    def _estimate_memory(self, config: AttentionConfig) -> float:
        """Estimate memory usage in MB"""
        embedding_dim = config.n_heads * config.dim_per_head
        base_memory = embedding_dim * 4 / 1024 / 1024  # float32

        if config.strategy == FusionStrategy.EARLY:
            return base_memory * 1.0
        elif config.strategy == FusionStrategy.LATE:
            return base_memory * 1.3
        elif config.strategy == FusionStrategy.HIERARCHICAL:
            return base_memory * 1.5
        elif config.strategy == FusionStrategy.CO_ATTENTION:
            return base_memory * 2.5
        else:  # transformer
            return base_memory * 2.0


def find_optimal_fusion(
    n_modalities: int,
    requirements: Dict[str, float]
) -> Tuple[AttentionConfig, AttentionMetrics]:
    """Find optimal fusion strategy"""
    benchmark = AttentionBenchmark(n_trials=50)

    # Define fusion strategies to test
    strategies = [
        FusionStrategy.EARLY,
        FusionStrategy.LATE,
        FusionStrategy.HIERARCHICAL,
        FusionStrategy.CO_ATTENTION,
        FusionStrategy.TRANSFORMER_FUSION
    ]

    # Define modality sets
    modality_sets = [
        ['text', 'image'],
        ['text', 'audio'],
        ['text', 'image', 'audio'],
        ['text', 'image', 'audio', 'code']
    ][:n_modalities]

    results = []
    for strategy in strategies:
        config = AttentionConfig(
            strategy=strategy,
            n_heads=8,
            dim_per_head=64,
            dropout=0.1,
            temperature=1.0,
            n_layers=2
        )

        metrics = benchmark.benchmark_strategy(config, modality_sets)
        results.append((config, metrics))

        print(f"\n{strategy.value}:")
        print(f"  Fusion Quality: {metrics.fusion_quality:.3f}")
        print(f"  Alignment: {metrics.alignment_score:.3f}")
        print(f"  Entropy: {metrics.attention_entropy:.3f}")
        print(f"  Latency: {metrics.latency_ms:.2f}ms")
        print(f"  FLOPs: {metrics.computation_flops:.2e}")
        print(f"  Memory: {metrics.memory_mb:.2f}MB")

    # Select best based on requirements
    best_config, best_metrics = select_best_fusion(results, requirements)

    return best_config, best_metrics


def select_best_fusion(
    results: List[Tuple[AttentionConfig, AttentionMetrics]],
    requirements: Dict[str, float]
) -> Tuple[AttentionConfig, AttentionMetrics]:
    """Select best fusion strategy"""
    def score(config: AttentionConfig, metrics: AttentionMetrics) -> float:
        score = 0
        if "quality" in requirements:
            score += metrics.fusion_quality * requirements["quality"]
        if "alignment" in requirements:
            score += metrics.alignment_score * requirements["alignment"]
        if "latency" in requirements:
            max_latency = requirements["latency"]
            latency_score = max(0, 1 - metrics.latency_ms / max_latency)
            score += latency_score * requirements.get("latency_weight", 0.5)
        if "memory" in requirements:
            max_memory = requirements["memory"]
            memory_score = max(0, 1 - metrics.memory_mb / max_memory)
            score += memory_score * requirements.get("memory_weight", 0.3)
        return score

    scored = [(score(c, m), c, m) for c, m in results]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1], scored[0][2]


def run_comprehensive_benchmark():
    """Run comprehensive cross-modal attention benchmark"""
    print("=" * 80)
    print("CROSS-MODAL ATTENTION OPTIMIZATION")
    print("=" * 80)

    # Test with different numbers of modalities
    n_modalities_list = [2, 3, 4]

    # Task requirements
    requirements = {
        "quality": 0.4,
        "alignment": 0.3,
        "latency": 50.0,
        "latency_weight": 0.2,
        "memory": 200.0,
        "memory_weight": 0.1
    }

    all_results = {}

    for n_modalities in n_modalities_list:
        print(f"\n{'='*80}")
        print(f"Testing with {n_modalities} modalities")
        print('='*80)

        best_config, best_metrics = find_optimal_fusion(n_modalities, requirements)

        all_results[str(n_modalities)] = {
            'config': {
                'strategy': best_config.strategy.value,
                'n_heads': best_config.n_heads,
                'dim_per_head': best_config.dim_per_head,
                'dropout': best_config.dropout,
                'temperature': best_config.temperature,
                'n_layers': best_config.n_layers
            },
            'metrics': {
                'fusion_quality': best_metrics.fusion_quality,
                'alignment_score': best_metrics.alignment_score,
                'attention_entropy': best_metrics.attention_entropy,
                'computation_flops': best_metrics.computation_flops,
                'memory_mb': best_metrics.memory_mb,
                'latency_ms': best_metrics.latency_ms,
                'modality_importance': best_metrics.modality_importance
            }
        }

        print(f"\nBest strategy for {n_modalities} modalities: {best_config.strategy.value}")

    # Save results
    output_file = "simulations/domains/multimodal/results/attention_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {output_file}")
    return all_results


if __name__ == "__main__":
    results = run_comprehensive_benchmark()
