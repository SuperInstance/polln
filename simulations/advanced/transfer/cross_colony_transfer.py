"""
POLLN Cross-Colony Knowledge Transfer
======================================

Simulates federated knowledge sharing between multiple colonies.
Tests different federation strategies (averaging, parameter mixing, ensemble)
to measure cross-colony performance improvements.

Key Metrics:
- Cross-colony boost: Performance improvement from federation
- Knowledge diversity: Unique knowledge contributed by each colony
- Federation efficiency: Cost/benefit of federation
- Convergence speed: How quickly colonies reach consensus
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict


class FederationMethod(Enum):
    """Federated learning strategies"""
    WEIGHTED_AVERAGING = "weighted_averaging"  # Weight by colony performance/size
    PARAMETER_MIXING = "parameter_mixing"  # Mix parameters at layer level
    ENSEMBLE_DISTILLATION = "ensemble_distillation"  # Distill from ensemble
    KNOWLEDGE_DISTILLATION = "knowledge_distillation"  # Transfer best knowledge
    ADAPTIVE_MIXING = "adaptive_mixing"  # Adaptive mixing based on similarity


@dataclass
class ColonyKnowledge:
    """Knowledge from a single colony"""
    colony_id: str
    task_specialization: str  # What task this colony specializes in

    # Performance metrics
    performance: float
    data_size: int
    diversity_score: float

    # Knowledge representation
    parameters: Dict[str, np.ndarray]  # Layer weights
    patterns: Dict[str, float]  # Learned patterns

    # Metadata
    age: int  # Number of training iterations
    confidence: float  # How confident in its knowledge

    def to_dict(self) -> dict:
        return {
            'colony_id': self.colony_id,
            'task_specialization': self.task_specialization,
            'performance': self.performance,
            'data_size': self.data_size,
            'diversity_score': self.diversity_score,
            'age': self.age,
            'confidence': self.confidence,
            'num_layers': len(self.parameters),
            'num_patterns': len(self.patterns)
        }


@dataclass
class FederationConfig:
    """Configuration for federated learning"""
    method: FederationMethod

    # Participation
    min_colonies: int = 2
    min_performance: float = 0.5
    min_similarity: float = 0.3

    # Weighting
    weight_by_performance: bool = True
    weight_by_size: bool = False
    weight_by_diversity: bool = True

    # Aggregation
    aggregation_frequency: int = 10  # Every N rounds
    max_rounds: int = 100

    # Distillation (for ensemble methods)
    distillation_temperature: float = 3.0
    distillation_epochs: int = 20

    # Validation
    validate_before_transfer: bool = True
    rollback_on_degradation: bool = True

    def to_dict(self) -> dict:
        return {
            'method': self.method.value,
            'min_colonies': self.min_colonies,
            'min_performance': self.min_performance,
            'min_similarity': self.min_similarity,
            'weight_by_performance': self.weight_by_performance,
            'weight_by_size': self.weight_by_size,
            'weight_by_diversity': self.weight_by_diversity,
            'aggregation_frequency': self.aggregation_frequency,
            'max_rounds': self.max_rounds,
            'distillation_temperature': self.distillation_temperature,
            'distillation_epochs': self.distillation_epochs,
            'validate_before_transfer': self.validate_before_transfer,
            'rollback_on_degradation': self.rollback_on_degradation
        }


@dataclass
class FederationResult:
    """Results from a federation round"""
    config: FederationConfig
    colony_performances_before: Dict[str, float]
    colony_performances_after: Dict[str, float]

    # Federation metrics
    performance_boost: float  # Average improvement
    best_colony_boost: float  # Improvement for best colony
    worst_colony_boost: float  # Improvement for worst colony

    # Knowledge metrics
    knowledge_diversity: float
    unique_contributions: Dict[str, float]  # Per colony

    # Efficiency
    rounds_to_convergence: int
    communication_cost: float  # Total parameters transferred
    computation_cost: float  # FLOPs for aggregation

    # Consensus
    consensus_score: float  # How similar colonies became

    def to_dict(self) -> dict:
        return {
            'config': self.config.to_dict(),
            'colony_performances_before': self.colony_performances_before,
            'colony_performances_after': self.colony_performances_after,
            'performance_boost': self.performance_boost,
            'best_colony_boost': self.best_colony_boost,
            'worst_colony_boost': self.worst_colony_boost,
            'knowledge_diversity': self.knowledge_diversity,
            'unique_contributions': self.unique_contributions,
            'rounds_to_convergence': self.rounds_to_convergence,
            'communication_cost': self.communication_cost,
            'computation_cost': self.computation_cost,
            'consensus_score': self.consensus_score
        }


class CrossColonySimulator:
    """Simulates cross-colony knowledge transfer"""

    def __init__(self):
        self.results: List[FederationResult] = []

    def create_colony(
        self,
        colony_id: str,
        task_specialization: str,
        base_performance: float = 0.7
    ) -> ColonyKnowledge:
        """Create a synthetic colony"""

        # Create layer parameters
        num_layers = 12
        parameters = {}
        for i in range(num_layers):
            layer_name = f"layer_{i}"
            # Random weights with some structure based on specialization
            weights = np.random.randn(768, 768) * 0.1
            parameters[layer_name] = weights

        # Create patterns
        num_patterns = np.random.randint(500, 1500)
        patterns = {}
        for i in range(num_patterns):
            pattern_id = f"pattern_{i}"
            patterns[pattern_id] = np.random.random()

        # Diversity based on specialization uniqueness
        specializations = [
            "code_review", "code_generation", "text_summarization",
            "question_answering", "math_problems", "sentiment_analysis",
            "translation", "retrieval"
        ]
        diversity = 1.0 - (specializations.index(task_specialization) % 3) * 0.1

        return ColonyKnowledge(
            colony_id=colony_id,
            task_specialization=task_specialization,
            performance=base_performance + np.random.normal(0, 0.05),
            data_size=np.random.randint(10000, 100000),
            diversity_score=diversity,
            parameters=parameters,
            patterns=patterns,
            age=np.random.randint(100, 1000),
            confidence=np.random.uniform(0.6, 0.9)
        )

    def compute_colony_similarity(
        self,
        colony1: ColonyKnowledge,
        colony2: ColonyKnowledge
    ) -> float:
        """Compute similarity between two colonies"""

        # Task similarity
        if colony1.task_specialization == colony2.task_specialization:
            task_sim = 1.0
        else:
            task_sim = 0.3

        # Parameter similarity (cosine of mean weights)
        params1 = np.concatenate([w.flatten() for w in colony1.parameters.values()])
        params2 = np.concatenate([w.flatten() for w in colony2.parameters.values()])

        # Normalize
        params1_norm = params1 / (np.linalg.norm(params1) + 1e-8)
        params2_norm = params2 / (np.linalg.norm(params2) + 1e-8)

        param_sim = np.dot(params1_norm, params2_norm)

        # Pattern overlap
        patterns1 = set(colony1.patterns.keys())
        patterns2 = set(colony2.patterns.keys())
        pattern_sim = len(patterns1 & patterns2) / len(patterns1 | patterns2)

        # Weighted combination
        similarity = (
            0.5 * task_sim +
            0.3 * param_sim +
            0.2 * pattern_sim
        )

        return float(similarity)

    def weighted_averaging(
        self,
        colonies: List[ColonyKnowledge],
        config: FederationConfig
    ) -> Dict[str, float]:
        """Federated averaging with weighting"""

        # Compute weights
        weights = []
        total_weight = 0

        for colony in colonies:
            weight = 1.0

            if config.weight_by_performance:
                weight *= colony.performance

            if config.weight_by_size:
                weight *= colony.data_size / 100000  # Normalize

            if config.weight_by_diversity:
                weight *= colony.diversity_score

            weights.append(weight)
            total_weight += weight

        # Normalize weights
        weights = [w / total_weight for w in weights]

        # Weighted average of performances
        avg_performance = sum(w * c.performance for w, c in zip(weights, colonies))

        # Colony improvements based on averaging
        improvements = {}
        for colony in colonies:
            # Improvement proportional to weight and diversity
            idx = colonies.index(colony)
            base_improvement = 0.1 * weights[idx] * colony.diversity_score

            # Diminishing returns for high-performance colonies
            if colony.performance > 0.8:
                base_improvement *= 0.5

            improvements[colony.colony_id] = base_improvement

        return improvements

    def parameter_mixing(
        self,
        colonies: List[ColonyKnowledge],
        config: FederationConfig
    ) -> Dict[str, float]:
        """Layer-wise parameter mixing"""

        improvements = {}

        for colony in colonies:
            # Find similar colonies
            similar_colonies = [
                c for c in colonies
                if c.colony_id != colony.colony_id and
                self.compute_colony_similarity(colony, c) >= config.min_similarity
            ]

            if similar_colonies:
                # Mix with similar colonies
                avg_similar_perf = np.mean([c.performance for c in similar_colonies])
                improvement = 0.15 * (avg_similar_perf - colony.performance) * colony.diversity_score
                improvement = max(0, improvement)  # Only positive improvements
            else:
                # No similar colonies, minimal improvement
                improvement = 0.02

            improvements[colony.colony_id] = improvement

        return improvements

    def ensemble_distillation(
        self,
        colonies: List[ColonyKnowledge],
        config: FederationConfig
    ) -> Dict[str, float]:
        """Distill knowledge from ensemble of colonies"""

        # Create ensemble prediction (weighted average)
        ensemble_weights = [
            c.performance * c.diversity_score
            for c in colonies
        ]
        total_weight = sum(ensemble_weights)
        ensemble_weights = [w / total_weight for w in ensemble_weights]

        ensemble_performance = sum(
            w * c.performance
            for w, c in zip(ensemble_weights, colonies)
        )

        improvements = {}
        for colony in colonies:
            # Distillation from ensemble
            idx = colonies.index(colony)

            # Benefit inversely proportional to current performance
            # (lower performance colonies benefit more)
            performance_gap = ensemble_performance - colony.performance
            improvement = 0.2 * performance_gap * ensemble_weights[idx]

            improvements[colony.colony_id] = max(0, improvement)

        return improvements

    def adaptive_mixing(
        self,
        colonies: List[ColonyKnowledge],
        config: FederationConfig
    ) -> Dict[str, float]:
        """Adaptive mixing based on colony similarity and performance"""

        improvements = {}

        for colony in colonies:
            # Compute similarity to all other colonies
            similarities = []
            for other in colonies:
                if other.colony_id != colony.colony_id:
                    sim = self.compute_colony_similarity(colony, other)
                    similarities.append((other, sim))

            # Group by similarity
            high_sim = [c for c, s in similarities if s >= 0.7]
            med_sim = [c for c, s in similarities if 0.3 <= s < 0.7]
            low_sim = [c for c, s in similarities if s < 0.3]

            # Adaptive strategy
            if high_sim:
                # Strong mixing with similar colonies
                avg_perf = np.mean([c.performance for c in high_sim])
                improvement = 0.12 * (avg_perf - colony.performance)
            elif med_sim:
                # Moderate mixing
                avg_perf = np.mean([c.performance for c in med_sim])
                improvement = 0.08 * (avg_perf - colony.performance)
            else:
                # Low similarity, minimal transfer
                improvement = 0.02

            improvements[colony.colony_id] = max(0, improvement)

        return improvements

    def simulate_federation(
        self,
        colonies: List[ColonyKnowledge],
        config: FederationConfig
    ) -> FederationResult:
        """Simulate a federation round"""

        # Record performances before
        performances_before = {
            colony.colony_id: colony.performance
            for colony in colonies
        }

        # Filter colonies by minimum performance
        eligible_colonies = [
            c for c in colonies
            if c.performance >= config.min_performance
        ]

        if len(eligible_colonies) < config.min_colonies:
            # Not enough eligible colonies, minimal improvement
            improvements = {c.colony_id: 0.01 for c in colonies}
        else:
            # Apply federation method
            if config.method == FederationMethod.WEIGHTED_AVERAGING:
                improvements = self.weighted_averaging(eligible_colonies, config)
            elif config.method == FederationMethod.PARAMETER_MIXING:
                improvements = self.parameter_mixing(eligible_colonies, config)
            elif config.method == FederationMethod.ENSEMBLE_DISTILLATION:
                improvements = self.ensemble_distillation(eligible_colonies, config)
            elif config.method == FederationMethod.ADAPTIVE_MIXING:
                improvements = self.adaptive_mixing(eligible_colonies, config)
            else:
                improvements = {c.colony_id: 0.01 for c in colonies}

        # Apply improvements
        performances_after = {}
        for colony in colonies:
            if colony.colony_id in improvements:
                new_perf = colony.performance + improvements[colony.colony_id]
                performances_after[colony.colony_id] = min(new_perf, 0.98)  # Cap at 0.98
            else:
                performances_after[colony.colony_id] = colony.performance

        # Compute metrics
        boost = np.mean(list(performances_after.values())) - np.mean(list(performances_before.values()))

        perfs_before_list = list(performances_before.values())
        perfs_after_list = list(performances_after.values())

        best_boost = max(perfs_after_list) - max(perfs_before_list)
        worst_boost = min(perfs_after_list) - min(perfs_before_list)

        # Knowledge diversity
        diversity = np.mean([c.diversity_score for c in colonies])

        # Unique contributions
        unique_contributions = {
            c.colony_id: improvements.get(c.colony_id, 0.01) * c.diversity_score
            for c in colonies
        }

        # Communication cost (total parameters)
        total_params = sum(len(c.parameters) * 768 * 768 for c in colonies)
        comm_cost = total_params * 4 / 1e9  # GB (float32)

        # Computation cost
        comp_cost = total_params * 10 / 1e12  # TFLOPs

        # Consensus score
        if len(colonies) > 1:
            similarities = []
            for i, c1 in enumerate(colonies):
                for c2 in colonies[i+1:]:
                    similarities.append(self.compute_colony_similarity(c1, c2))
            consensus = np.mean(similarities) if similarities else 0
        else:
            consensus = 1.0

        result = FederationResult(
            config=config,
            colony_performances_before=performances_before,
            colony_performances_after=performances_after,
            performance_boost=boost,
            best_colony_boost=best_boost,
            worst_colony_boost=worst_boost,
            knowledge_diversity=diversity,
            unique_contributions=unique_contributions,
            rounds_to_convergence=10,  # Simplified
            communication_cost=comm_cost,
            computation_cost=comp_cost,
            consensus_score=consensus
        )

        self.results.append(result)
        return result

    def run_method_comparison(
        self,
        num_colonies: int = 5,
        trials: int = 10
    ) -> List[FederationResult]:
        """Compare different federation methods"""

        all_results = []
        task_specializations = [
            "code_review", "code_generation", "text_summarization",
            "question_answering", "math_problems", "sentiment_analysis",
            "translation", "retrieval"
        ]

        methods = [
            FederationMethod.WEIGHTED_AVERAGING,
            FederationMethod.PARAMETER_MIXING,
            FederationMethod.ENSEMBLE_DISTILLATION,
            FederationMethod.ADAPTIVE_MIXING,
        ]

        for method in methods:
            print(f"   Testing {method.value}...")

            for trial in range(trials):
                # Create colonies
                colonies = []
                for i in range(num_colonies):
                    task = task_specializations[i % len(task_specializations)]
                    colony = self.create_colony(
                        colony_id=f"colony_{i}",
                        task_specialization=task,
                        base_performance=0.6 + np.random.random() * 0.2
                    )
                    colonies.append(colony)

                # Create config
                config = FederationConfig(
                    method=method,
                    min_colonies=2,
                    min_performance=0.5,
                    min_similarity=0.3,
                    weight_by_performance=True,
                    weight_by_diversity=True
                )

                # Simulate federation
                result = self.simulate_federation(colonies, config)
                all_results.append(result)

        self.results.extend(all_results)
        return all_results


class FederationAnalyzer:
    """Analyzes federation results"""

    def __init__(self, results: List[FederationResult]):
        self.results = results
        self.df = pd.DataFrame([r.to_dict() for r in results])

    def compare_methods(self) -> pd.DataFrame:
        """Compare federation methods"""

        comparison = self.df.groupby(
            self.df['config'].apply(lambda x: x['method'])
        ).agg({
            'performance_boost': ['mean', 'std'],
            'best_colony_boost': 'mean',
            'worst_colony_boost': 'mean',
            'knowledge_diversity': 'mean',
            'consensus_score': 'mean',
            'communication_cost': 'mean'
        })

        return comparison

    def analyze_diversity_impact(self) -> pd.DataFrame:
        """Analyze impact of knowledge diversity"""

        diversity_bins = pd.cut(
            self.df['knowledge_diversity'],
            bins=[0, 0.5, 0.7, 1.0],
            labels=['Low', 'Medium', 'High']
        )

        binned = self.df.groupby(diversity_bins).agg({
            'performance_boost': ['mean', 'std'],
            'unique_contributions': lambda x: np.mean([sum(v.values()) for v in x])
        })

        return binned

    def visualize_results(self, save_path: Optional[str] = None):
        """Visualize federation results"""

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Performance boost by method
        ax1 = axes[0, 0]
        methods = self.df['config'].apply(lambda x: x['method']).unique()
        boost_data = [
            self.df[
                self.df['config'].apply(lambda x: x['method'] == method)
            ]['performance_boost'].values
            for method in methods
        ]
        ax1.boxplot(boost_data, labels=methods)
        ax1.set_ylabel('Performance Boost')
        ax1.set_title('Cross-Colony Performance Boost')
        ax1.tick_params(axis='x', rotation=45)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)

        # 2. Best vs worst colony boost
        ax2 = axes[0, 1]
        for method in methods:
            method_data = self.df[
                self.df['config'].apply(lambda x: x['method'] == method)
            ]
            ax2.scatter(
                method_data['best_colony_boost'],
                method_data['worst_colony_boost'],
                label=method, alpha=0.5
            )
        ax2.plot([0, 0.2], [0, 0.2], 'k--', label='Equal benefit')
        ax2.set_xlabel('Best Colony Boost')
        ax2.set_ylabel('Worst Colony Boost')
        ax2.set_title('Equitability of Federation Benefits')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Consensus vs boost
        ax3 = axes[1, 0]
        ax3.scatter(
            self.df['consensus_score'],
            self.df['performance_boost'],
            alpha=0.5
        )
        ax3.set_xlabel('Consensus Score')
        ax3.set_ylabel('Performance Boost')
        ax3.set_title('Consensus vs Performance')
        ax3.grid(True, alpha=0.3)

        # 4. Communication cost
        ax4 = axes[1, 1]
        cost_data = [
            self.df[
                self.df['config'].apply(lambda x: x['method'] == method)
            ]['communication_cost'].values
            for method in methods
        ]
        ax4.boxplot(cost_data, labels=methods)
        ax4.set_ylabel('Communication Cost (GB)')
        ax4.set_title('Communication Cost by Method')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def main():
    """Main simulation"""
    print("=" * 70)
    print("POLLN Cross-Colony Knowledge Transfer")
    print("=" * 70)

    # Create simulator
    simulator = CrossColonySimulator()

    # Test federation methods
    print("\n1. Testing federation methods...")
    results = simulator.run_method_comparison(
        num_colonies=5,
        trials=20
    )

    print(f"   Completed {len(results)} trials")

    # Analyze results
    print("\n2. Analyzing results...")
    analyzer = FederationAnalyzer(results)

    comparison = analyzer.compare_methods()
    print("\n   Method Comparison:")
    print(comparison)

    # Test different colony counts
    print("\n3. Testing different colony counts...")

    for num_colonies in [3, 5, 7, 10]:
        colonies = []
        task_specializations = [
            "code_review", "code_generation", "text_summarization",
            "question_answering", "math_problems", "sentiment_analysis",
            "translation", "retrieval", "classification", "reasoning"
        ]

        for i in range(num_colonies):
            task = task_specializations[i % len(task_specializations)]
            colony = simulator.create_colony(
                colony_id=f"colony_{i}",
                task_specialization=task
            )
            colonies.append(colony)

        config = FederationConfig(
            method=FederationMethod.WEIGHTED_AVERAGING,
            weight_by_performance=True,
            weight_by_diversity=True
        )

        result = simulator.simulate_federation(colonies, config)

        print(f"   {num_colonies} colonies: {result.performance_boost:.3f} boost")

    # Visualize
    print("\n4. Generating visualizations...")
    analyzer.visualize_results("simulations/advanced/transfer/federation_results.png")
    print("   Saved visualizations")

    # Generate federation configuration
    print("\n5. Generating federation configuration...")

    federation_config = {
        'method': 'weighted_averaging',
        'min_colonies': 2,
        'min_performance': 0.5,
        'min_similarity': 0.5,
        'weight_by_performance': True,
        'weight_by_diversity': True,
        'validation': {
            'enabled': True,
            'min_improvement': 0.02,
            'rollback_on_degradation': True
        },
        'aggregation': {
            'frequency': 10,
            'max_rounds': 100
        }
    }

    with open("simulations/advanced/transfer/federation_config.json", 'w') as f:
        json.dump(federation_config, f, indent=2)

    print("   Saved federation configuration")

    # Save results
    print("\n6. Saving results...")
    results_df = pd.DataFrame([r.to_dict() for r in results])
    results_df.to_csv("simulations/advanced/transfer/federation_results.csv", index=False)
    print("   Saved results CSV")

    print("\n" + "=" * 70)
    print("Simulation complete!")
    print("=" * 70)

    # Summary
    print("\nSummary:")
    print(f"   Total trials: {len(results)}")
    print(f"   Average boost: {results_df['performance_boost'].mean():.3f}")
    print(f"   Best method: {comparison['performance_boost']['mean'].idxmax()}")


if __name__ == "__main__":
    main()
