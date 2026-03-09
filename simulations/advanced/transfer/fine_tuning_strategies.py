"""
POLLN Fine-Tuning Strategy Optimization
========================================

Simulates and optimizes fine-tuning strategies for transfer learning.
Tests different approaches (full, LoRA, adapters, prompt tuning) to find
optimal configurations for different task similarity levels.

Key Metrics:
- Transfer speed: Time/flops to convergence
- Final performance: Accuracy/quality after fine-tuning
- Catastrophic forgetting: Performance degradation on source task
- Parameter efficiency: Number of trainable parameters
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import matplotlib.pyplot as plt
import seaborn as sns


class FineTuningMethod(Enum):
    """Different fine-tuning approaches"""
    FULL_FINETUNE = "full_finetune"  # Update all parameters
    LORA = "lora"  # Low-rank adaptation
    ADAPTERS = "adapters"  # Adapter layers
    PROMPT_TUNING = "prompt_tuning"  # Learnable prompts
    SELECTIVE = "selective"  # Update only selected layers
    BITFIT = "bitfit"  # Update only biases
    PREFIX_TUNING = "prefix_tuning"  # Learnable prefix tokens


@dataclass
class FineTuningConfig:
    """Configuration for a fine-tuning strategy"""
    method: FineTuningMethod
    learning_rate: float
    epochs: int
    batch_size: int
    warmup_ratio: float
    weight_decay: float

    # Method-specific parameters
    rank: Optional[int] = None  # For LoRA
    alpha: Optional[float] = None  # For LoRA
    adapter_dim: Optional[int] = None  # For adapters
    prompt_length: Optional[int] = None  # For prompt/prefix tuning
    freeze_layers: Optional[List[str]] = None  # For selective

    # Training parameters
    optimizer: str = "adamw"
    scheduler: str = "cosine"
    gradient_clip: float = 1.0

    def to_dict(self) -> dict:
        data = {
            'method': self.method.value,
            'learning_rate': self.learning_rate,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'warmup_ratio': self.warmup_ratio,
            'weight_decay': self.weight_decay,
            'optimizer': self.optimizer,
            'scheduler': self.scheduler,
            'gradient_clip': self.gradient_clip
        }

        # Add method-specific params
        if self.rank is not None:
            data['rank'] = self.rank
        if self.alpha is not None:
            data['alpha'] = self.alpha
        if self.adapter_dim is not None:
            data['adapter_dim'] = self.adapter_dim
        if self.prompt_length is not None:
            data['prompt_length'] = self.prompt_length
        if self.freeze_layers is not None:
            data['freeze_layers'] = self.freeze_layers

        return data


@dataclass
class FineTuningResult:
    """Results from a fine-tuning run"""
    config: FineTuningConfig
    task_similarity: float

    # Performance metrics
    target_performance: float  # Performance on target task
    source_performance_after: float  # Source task performance after transfer
    forgetting_ratio: float  # (source_before - source_after) / source_before

    # Efficiency metrics
    trainable_params: int
    total_params: int
    param_efficiency: float  # trainable / total
    flops: int  # Total floating point operations
    training_time: float  # In seconds

    # Convergence metrics
    epochs_to_convergence: int
    final_loss: float

    def to_dict(self) -> dict:
        return {
            'config': self.config.to_dict(),
            'task_similarity': self.task_similarity,
            'target_performance': self.target_performance,
            'source_performance_after': self.source_performance_after,
            'forgetting_ratio': self.forgetting_ratio,
            'trainable_params': self.trainable_params,
            'total_params': self.total_params,
            'param_efficiency': self.param_efficiency,
            'flops': self.flops,
            'training_time': self.training_time,
            'epochs_to_convergence': self.epochs_to_convergence,
            'final_loss': self.final_loss
        }


class FineTuningSimulator:
    """Simulates fine-tuning with different strategies"""

    def __init__(self, base_params: int = 7_000_000_000):  # 7B model
        self.base_params = base_params
        self.flops_per_param = 3  # Rough estimate
        self.results: List[FineTuningResult] = []

    def estimate_trainable_params(self, config: FineTuningConfig) -> int:
        """Estimate number of trainable parameters for a method"""

        if config.method == FineTuningMethod.FULL_FINETUNE:
            return self.base_params

        elif config.method == FineTuningMethod.LORA:
            # LoRA: rank * (2 * hidden_dim) per layer
            # Simplified: rank * 2 * (hidden_dim * num_layers)
            hidden_dim = 4096  # Assume 7B model
            num_layers = 32
            lora_params = config.rank * 2 * hidden_dim * num_layers
            return lora_params

        elif config.method == FineTuningMethod.ADAPTERS:
            # Adapters: adapter_dim^2 per layer (bottleneck)
            # Plus residual projections
            hidden_dim = 4096
            num_layers = 32
            adapter_params = 2 * config.adapter_dim * hidden_dim * num_layers
            return adapter_params

        elif config.method == FineTuningMethod.PROMPT_TUNING:
            # Prompt tuning: prompt_length * vocab_size * hidden_dim
            vocab_size = 50000
            hidden_dim = 4096
            prompt_params = config.prompt_length * vocab_size * hidden_dim
            return prompt_params

        elif config.method == FineTuningMethod.PREFIX_TUNING:
            # Prefix tuning: num_layers * prefix_length * hidden_dim * 2
            num_layers = 32
            prefix_params = num_layers * config.prompt_length * hidden_dim * 2
            return prefix_params

        elif config.method == FineTuningMethod.BITFIT:
            # BitFit: only bias parameters
            # Roughly 10% of total params
            return int(self.base_params * 0.1)

        elif config.method == FineTuningMethod.SELECTIVE:
            # Selective: fraction of layers
            # Assume 50% of params are trainable
            return int(self.base_params * 0.5)

        return self.base_params

    def simulate_finetuning(
        self,
        config: FineTuningConfig,
        task_similarity: float,
        source_performance: float = 0.85
    ) -> FineTuningResult:
        """Simulate fine-tuning with given configuration"""

        trainable_params = self.estimate_trainable_params(config)
        param_efficiency = trainable_params / self.base_params

        # Simulate performance based on similarity and method
        # Higher similarity = better transfer
        base_transfer_quality = task_similarity

        # Method-specific transfer effectiveness
        method_bonus = {
            FineTuningMethod.FULL_FINETUNE: 0.10,
            FineTuningMethod.LORA: 0.05,
            FineTuningMethod.ADAPTERS: 0.03,
            FineTuningMethod.PROMPT_TUNING: 0.02,
            FineTuningMethod.SELECTIVE: 0.07,
            FineTuningMethod.BITFIT: 0.01,
            FineTuningMethod.PREFIX_TUNING: 0.02,
        }

        # Noise and randomness
        noise = np.random.normal(0, 0.02)

        # Target performance
        transfer_boost = base_transfer_quality * 0.3 + method_bonus[config.method]
        target_performance = np.clip(
            0.5 + transfer_boost + noise,
            0.0, 1.0
        )

        # Catastrophic forgetting
        # More aggressive methods (full) have higher forgetting risk
        forgetting_risk = {
            FineTuningMethod.FULL_FINETUNE: 0.15,
            FineTuningMethod.LORA: 0.05,
            FineTuningMethod.ADAPTERS: 0.03,
            FineTuningMethod.PROMPT_TUNING: 0.01,
            FineTuningMethod.SELECTIVE: 0.08,
            FineTuningMethod.BITFIT: 0.02,
            FineTuningMethod.PREFIX_TUNING: 0.01,
        }

        # Lower similarity = higher forgetting
        forgetting = forgetting_risk[config.method] * (1 - task_similarity)
        source_performance_after = source_performance * (1 - forgetting)
        forgetting_ratio = forgetting

        # Training efficiency
        # Fewer params = faster training
        flops = trainable_params * config.epochs * self.flops_per_param

        # Convergence speed depends on similarity
        # High similarity = faster convergence
        base_epochs = config.epochs
        convergence_factor = 0.5 + 0.5 * task_similarity
        epochs_to_convergence = int(base_epochs * convergence_factor)

        # Training time (rough estimate)
        # Assume 1 TFLOP/s = 10^12 flops/s
        training_time = flops / 1e12

        # Final loss
        final_loss = (1 - target_performance) + np.random.normal(0, 0.05)

        result = FineTuningResult(
            config=config,
            task_similarity=task_similarity,
            target_performance=target_performance,
            source_performance_after=source_performance_after,
            forgetting_ratio=forgetting_ratio,
            trainable_params=trainable_params,
            total_params=self.base_params,
            param_efficiency=param_efficiency,
            flops=int(flops),
            training_time=training_time,
            epochs_to_convergence=epochs_to_convergence,
            final_loss=final_loss
        )

        self.results.append(result)
        return result

    def run_strategy_sweep(
        self,
        strategies: List[FineTuningConfig],
        similarities: List[float],
        trials_per_combination: int = 5
    ) -> List[FineTuningResult]:
        """Run fine-tuning simulations across all strategies and similarities"""

        all_results = []

        for strategy in strategies:
            for similarity in similarities:
                print(f"   Testing {strategy.method.value} at similarity {similarity:.2f}")
                for trial in range(trials_per_combination):
                    result = self.simulate_finetuning(strategy, similarity)
                    all_results.append(result)

        self.results.extend(all_results)
        return all_results


class FineTuningOptimizer:
    """Analyzes results and finds optimal strategies"""

    def __init__(self, results: List[FineTuningResult]):
        self.results = results
        self.df = pd.DataFrame([r.to_dict() for r in results])

    def find_best_strategy_for_similarity(
        self,
        similarity: float,
        metric: str = 'target_performance',
        constraint: Optional[Dict[str, float]] = None
    ) -> FineTuningResult:
        """Find best strategy for a given similarity level"""

        # Filter results by similarity
        tolerance = 0.05
        filtered = self.df[
            (self.df['task_similarity'] >= similarity - tolerance) &
            (self.df['task_similarity'] <= similarity + tolerance)
        ].copy()

        # Apply constraints
        if constraint:
            if 'max_forgetting' in constraint:
                filtered = filtered[filtered['forgetting_ratio'] <= constraint['max_forgetting']]
            if 'max_param_efficiency' in constraint:
                filtered = filtered[filtered['param_efficiency'] <= constraint['max_param_efficiency']]
            if 'max_training_time' in constraint:
                filtered = filtered[filtered['training_time'] <= constraint['max_training_time']]

        if filtered.empty:
            # Return best overall if no results match constraints
            filtered = self.df[
                (self.df['task_similarity'] >= similarity - tolerance) &
                (self.df['task_similarity'] <= similarity + tolerance)
            ].copy()

        # Find best by metric
        best_idx = filtered[metric].idxmax()
        best_row = filtered.loc[best_idx]

        return self._row_to_result(best_row)

    def get_optimal_strategies_by_similarity(
        self,
        similarity_bins: List[Tuple[float, float]]
    ) -> Dict[str, FineTuningConfig]:
        """Get optimal strategy for each similarity bin"""

        optimal_strategies = {}

        for i, (low, high) in enumerate(similarity_bins):
            mid_similarity = (low + high) / 2
            bin_name = f"{low:.1f}-{high:.1f}"

            # Find best strategy for this bin
            best = self.find_best_strategy_for_similarity(
                mid_similarity,
                metric='target_performance',
                constraint={'max_forgetting': 0.15}
            )

            optimal_strategies[bin_name] = best.config

        return optimal_strategies

    def analyze_tradeoffs(self) -> Dict[str, pd.DataFrame]:
        """Analyze tradeoffs between different metrics"""

        tradeoffs = {}

        # Group by method
        for method in self.df['config'].apply(lambda x: x['method']).unique():
            method_results = self.df[
                self.df['config'].apply(lambda x: x['method']) == method
            ]

            tradeoffs[method] = method_results.groupby('task_similarity').agg({
                'target_performance': ['mean', 'std'],
                'forgetting_ratio': ['mean', 'std'],
                'param_efficiency': 'mean',
                'training_time': 'mean'
            })

        return tradeoffs

    def visualize_results(self, save_path: Optional[str] = None):
        """Visualize fine-tuning results"""

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Performance vs Similarity by Method
        ax1 = axes[0, 0]
        for method in self.df['config'].apply(lambda x: x['method']).unique():
            method_data = self.df[
                self.df['config'].apply(lambda x: x['method']) == method
            ]
            grouped = method_data.groupby('task_similarity')['target_performance'].mean()
            ax1.plot(grouped.index, grouped.values, marker='o', label=method)

        ax1.set_xlabel('Task Similarity')
        ax1.set_ylabel('Target Performance')
        ax1.set_title('Transfer Performance vs Similarity')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Forgetting vs Similarity by Method
        ax2 = axes[0, 1]
        for method in self.df['config'].apply(lambda x: x['method']).unique():
            method_data = self.df[
                self.df['config'].apply(lambda x: x['method']) == method
            ]
            grouped = method_data.groupby('task_similarity')['forgetting_ratio'].mean()
            ax2.plot(grouped.index, grouped.values, marker='o', label=method)

        ax2.set_xlabel('Task Similarity')
        ax2.set_ylabel('Forgetting Ratio')
        ax2.set_title('Catastrophic Forgetting vs Similarity')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Parameter Efficiency
        ax3 = axes[1, 0]
        for method in self.df['config'].apply(lambda x: x['method']).unique():
            method_data = self.df[
                self.df['config'].apply(lambda x: x['method']) == method
            ]
            grouped = method_data.groupby('task_similarity')['param_efficiency'].mean()
            ax3.plot(grouped.index, grouped.values, marker='o', label=method)

        ax3.set_xlabel('Task Similarity')
        ax3.set_ylabel('Parameter Efficiency')
        ax3.set_title('Parameter Efficiency (lower is better)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')

        # 4. Training Time
        ax4 = axes[1, 1]
        for method in self.df['config'].apply(lambda x: x['method']).unique():
            method_data = self.df[
                self.df['config'].apply(lambda x: x['method']) == method
            ]
            grouped = method_data.groupby('task_similarity')['training_time'].mean()
            ax4.plot(grouped.index, grouped.values, marker='o', label=method)

        ax4.set_xlabel('Task Similarity')
        ax4.set_ylabel('Training Time (seconds)')
        ax4.set_title('Training Time vs Similarity')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def _row_to_result(self, row: pd.Series) -> FineTuningResult:
        """Convert DataFrame row back to FineTuningResult"""

        config_dict = row['config']
        config = FineTuningConfig(
            method=FineTuningMethod(config_dict['method']),
            learning_rate=config_dict['learning_rate'],
            epochs=config_dict['epochs'],
            batch_size=config_dict['batch_size'],
            warmup_ratio=config_dict['warmup_ratio'],
            weight_decay=config_dict['weight_decay'],
            rank=config_dict.get('rank'),
            alpha=config_dict.get('alpha'),
            adapter_dim=config_dict.get('adapter_dim'),
            prompt_length=config_dict.get('prompt_length'),
            freeze_layers=config_dict.get('freeze_layers'),
            optimizer=config_dict.get('optimizer', 'adamw'),
            scheduler=config_dict.get('scheduler', 'cosine'),
            gradient_clip=config_dict.get('gradient_clip', 1.0)
        )

        return FineTuningResult(
            config=config,
            task_similarity=row['task_similarity'],
            target_performance=row['target_performance'],
            source_performance_after=row['source_performance_after'],
            forgetting_ratio=row['forgetting_ratio'],
            trainable_params=row['trainable_params'],
            total_params=row['total_params'],
            param_efficiency=row['param_efficiency'],
            flops=row['flops'],
            training_time=row['training_time'],
            epochs_to_convergence=row['epochs_to_convergence'],
            final_loss=row['final_loss']
        )


def create_standard_strategies() -> List[FineTuningConfig]:
    """Create standard fine-tuning strategies to test"""

    return [
        # Full fine-tuning
        FineTuningConfig(
            method=FineTuningMethod.FULL_FINETUNE,
            learning_rate=0.0001,
            epochs=50,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01
        ),

        # LoRA (rank 8)
        FineTuningConfig(
            method=FineTuningMethod.LORA,
            learning_rate=0.001,
            epochs=30,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            rank=8,
            alpha=16
        ),

        # LoRA (rank 16)
        FineTuningConfig(
            method=FineTuningMethod.LORA,
            learning_rate=0.001,
            epochs=30,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            rank=16,
            alpha=32
        ),

        # Adapters (dim 64)
        FineTuningConfig(
            method=FineTuningMethod.ADAPTERS,
            learning_rate=0.001,
            epochs=40,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            adapter_dim=64
        ),

        # Prompt tuning
        FineTuningConfig(
            method=FineTuningMethod.PROMPT_TUNING,
            learning_rate=0.01,
            epochs=20,
            batch_size=32,
            warmup_ratio=0.0,
            weight_decay=0.0,
            prompt_length=10
        ),

        # BitFit
        FineTuningConfig(
            method=FineTuningMethod.BITFIT,
            learning_rate=0.001,
            epochs=60,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01
        ),

        # Selective (freeze embeddings)
        FineTuningConfig(
            method=FineTuningMethod.SELECTIVE,
            learning_rate=0.0005,
            epochs=40,
            batch_size=32,
            warmup_ratio=0.1,
            weight_decay=0.01,
            freeze_layers=['embedding']
        ),
    ]


def main():
    """Main simulation"""
    print("=" * 70)
    print("POLLN Fine-Tuning Strategy Optimization")
    print("=" * 70)

    # Create strategies
    print("\n1. Creating fine-tuning strategies...")
    strategies = create_standard_strategies()
    print(f"   Created {len(strategies)} strategies")
    for strategy in strategies:
        print(f"      - {strategy.method.value}")

    # Create simulator
    simulator = FineTuningSimulator()

    # Define similarity levels to test
    similarities = [0.1, 0.3, 0.5, 0.7, 0.9]

    # Run simulations
    print("\n2. Running fine-tuning simulations...")
    results = simulator.run_strategy_sweep(
        strategies=strategies,
        similarities=similarities,
        trials_per_combination=10
    )
    print(f"   Completed {len(results)} simulations")

    # Analyze results
    print("\n3. Analyzing results...")
    optimizer = FineTuningOptimizer(results)

    # Find optimal strategies for similarity bins
    print("\n4. Optimal strategies by similarity level:")
    similarity_bins = [(0.0, 0.3), (0.3, 0.6), (0.6, 1.0)]

    optimal = optimizer.get_optimal_strategies_by_similarity(similarity_bins)

    for bin_name, config in optimal.items():
        print(f"\n   Similarity {bin_name}:")
        print(f"      Method: {config.method.value}")
        print(f"      Learning rate: {config.learning_rate}")
        print(f"      Epochs: {config.epochs}")

        # Add method-specific info
        if config.rank:
            print(f"      Rank: {config.rank}")
        if config.adapter_dim:
            print(f"      Adapter dim: {config.adapter_dim}")
        if config.prompt_length:
            print(f"      Prompt length: {config.prompt_length}")

    # Generate transfer configuration
    print("\n5. Generating transfer configuration...")

    transfer_config = {
        'fine_tuning': {
            'high': {
                'method': optimal.get('0.6-1.0', FineTuningConfig(
                    method=FineTuningMethod.LORA,
                    learning_rate=0.001,
                    epochs=10,
                    batch_size=32,
                    warmup_ratio=0.1,
                    weight_decay=0.01,
                    rank=8,
                    alpha=16
                )).to_dict()
            },
            'medium': {
                'method': optimal.get('0.3-0.6', FineTuningConfig(
                    method=FineTuningMethod.FULL_FINETUNE,
                    learning_rate=0.0001,
                    epochs=50,
                    batch_size=32,
                    warmup_ratio=0.1,
                    weight_decay=0.01
                )).to_dict()
            },
            'low': {
                'method': optimal.get('0.0-0.3', FineTuningConfig(
                    method=FineTuningMethod.FULL_FINETUNE,
                    learning_rate=0.0005,
                    epochs=100,
                    batch_size=32,
                    warmup_ratio=0.1,
                    weight_decay=0.01
                )).to_dict()
            }
        },
        'thresholds': {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }
    }

    # Save configuration
    with open("simulations/advanced/transfer/finetuning_config.json", 'w') as f:
        json.dump(transfer_config, f, indent=2)

    print("   Saved transfer configuration")

    # Visualize results
    print("\n6. Generating visualizations...")
    optimizer.visualize_results("simulations/advanced/transfer/finetuning_results.png")
    print("   Saved visualizations")

    # Save results
    print("\n7. Saving results...")
    results_df = pd.DataFrame([r.to_dict() for r in results])
    results_df.to_csv("simulations/advanced/transfer/finetuning_results.csv", index=False)
    print("   Saved results CSV")

    print("\n" + "=" * 70)
    print("Simulation complete!")
    print("=" * 70)

    # Summary statistics
    print("\nSummary Statistics:")
    print(f"   Total simulations: {len(results)}")
    print(f"   Average target performance: {results_df['target_performance'].mean():.3f}")
    print(f"   Average forgetting: {results_df['forgetting_ratio'].mean():.3f}")
    print(f"   Best method: {results_df.groupby('config').apply(lambda x: x['target_performance'].mean()).idxmax()}")


if __name__ == "__main__":
    main()
