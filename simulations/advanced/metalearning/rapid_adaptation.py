"""
Rapid Adaptation Strategies for POLLN

Tests various rapid adaptation methods:
1. Fine-tuning: Standard gradient descent
2. LoRA: Low-rank adaptation (efficient)
3. Adapter modules: Lightweight adaptation layers
4. Prompting: Learnable prompts for LLMs

Measures:
- Adaptation speed
- Parameter efficiency
- Performance stability
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Callable, Any, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import time


@dataclass
class AdaptationConfig:
    """Adaptation strategy configuration"""
    strategy: str = 'lora'         # finetune, lora, adapter, prompt

    # LoRA parameters
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1

    # Adapter parameters
    adapter_dim: int = 64
    adapter_layers: int = 2

    # Prompt parameters
    prompt_length: int = 10
    prompt_dim: int = 128

    # Optimization
    learning_rate: float = 0.001
    adaptation_steps: int = 10
    batch_size: int = 32


class LoRALayer(nn.Module):
    """
    LoRA (Low-Rank Adaptation) layer

    Efficient adaptation by learning low-rank decomposition:
    W' = W + BA where B ∈ R^(d×r), A ∈ R^(r×d), r << d
    """

    def __init__(
        self,
        original_layer: nn.Linear,
        rank: int,
        alpha: int,
        dropout: float = 0.1
    ):
        super().__init__()
        self.original_layer = original_layer
        self.rank = rank
        self.alpha = alpha

        # Low-rank matrices
        in_features = original_layer.in_features
        out_features = original_layer.out_features

        self.lora_A = nn.Parameter(torch.randn(rank, in_features) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))

        # Scaling
        self.scaling = alpha / rank

        # Dropout
        self.lora_dropout = nn.Dropout(dropout)

        # Freeze original layer
        for param in self.original_layer.parameters():
            param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Original output
        original_out = self.original_layer(x)

        # LoRA output
        lora_out = torch.matmul(
            torch.matmul(x, self.lora_A.t()),
            self.lora_B.t()
        ) * self.scaling

        lora_out = self.lora_dropout(lora_out)

        return original_out + lora_out


class AdapterLayer(nn.Module):
    """
    Adapter layer for lightweight adaptation

    Adds small bottleneck layers between original layers.
    """

    def __init__(
        self,
        original_dim: int,
        adapter_dim: int,
        dropout: float = 0.1
    ):
        super().__init__()

        # Down-projection
        self.down = nn.Linear(original_dim, adapter_dim)

        # Activation
        self.activation = nn.ReLU()

        # Up-projection
        self.up = nn.Linear(adapter_dim, original_dim)

        # Dropout
        self.dropout = nn.Dropout(dropout)

        # Initialize with near-zero
        nn.init.zeros_(self.up.weight)
        nn.init.zeros_(self.up.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Adapter pathway
        adapted = self.down(x)
        adapted = self.activation(adapted)
        adapted = self.up(adapted)
        adapted = self.dropout(adapted)

        # Residual connection
        return x + adapted


class PromptLayer(nn.Module):
    """
    Learnable prompt layer for LLM adaptation

    Prepends learnable prompt tokens to input.
    """

    def __init__(
        self,
        prompt_length: int,
        prompt_dim: int,
        input_dim: int
    ):
        super().__init__()
        self.prompt_length = prompt_length
        self.prompt_dim = prompt_dim

        # Learnable prompts
        self.prompts = nn.Parameter(
            torch.randn(prompt_length, prompt_dim) * 0.02
        )

        # Projection if needed
        self.projection = nn.Linear(prompt_dim, input_dim) if prompt_dim != input_dim else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)

        # Expand prompts for batch
        prompts = self.prompts.unsqueeze(0).expand(batch_size, -1, -1)
        prompts = self.projection(prompts)

        # Concatenate prompts with input
        # Assuming x is (batch, seq_len, dim)
        return torch.cat([prompts, x], dim=1)


class RapidAdaptationModel(nn.Module):
    """
    Base model with rapid adaptation strategies
    """

    def __init__(
        self,
        state_dim: int = 128,
        hidden_dim: int = 256,
        config: AdaptationConfig = None
    ):
        super().__init__()
        self.config = config or AdaptationConfig()

        # Base model
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.value_head = nn.Linear(hidden_dim, 1)

        # Adaptation modules
        self.adaptation_modules = nn.ModuleDict()
        self._setup_adaptation(state_dim, hidden_dim)

    def _setup_adaptation(self, state_dim: int, hidden_dim: int):
        """Setup adaptation strategy"""
        if self.config.strategy == 'lora':
            # Replace linear layers with LoRA
            self.adaptation_modules['lora_1'] = LoRALayer(
                self.encoder[0],
                rank=self.config.lora_rank,
                alpha=self.config.lora_alpha,
                dropout=self.config.lora_dropout
            )
            self.adaptation_modules['lora_2'] = LoRALayer(
                self.encoder[2],
                rank=self.config.lora_rank,
                alpha=self.config.lora_alpha,
                dropout=self.config.lora_dropout
            )

        elif self.config.strategy == 'adapter':
            # Add adapter layers
            self.adaptation_modules['adapter_1'] = AdapterLayer(
                hidden_dim,
                self.config.adapter_dim
            )
            self.adaptation_modules['adapter_2'] = AdapterLayer(
                hidden_dim,
                self.config.adapter_dim
            )

        elif self.config.strategy == 'prompt':
            # Add prompt layer
            self.adaptation_modules['prompt'] = PromptLayer(
                self.config.prompt_length,
                self.config.prompt_dim,
                state_dim
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Apply adaptation
        if self.config.strategy == 'lora':
            x = self.adaptation_modules['lora_1'](x)
            x = self.encoder[1](x)  # ReLU
            x = self.adaptation_modules['lora_2'](x)
            x = self.encoder[3](x)  # ReLU

        elif self.config.strategy == 'adapter':
            x = self.encoder[0](x)
            x = self.encoder[1](x)  # ReLU
            x = self.adaptation_modules['adapter_1'](x)
            x = self.encoder[2](x)
            x = self.encoder[3](x)  # ReLU
            x = self.adaptation_modules['adapter_2'](x)

        elif self.config.strategy == 'prompt':
            # Reshape for prompt layer (add sequence dimension)
            if x.dim() == 2:
                x = x.unsqueeze(1)  # (batch, 1, dim)
            x = self.adaptation_modules['prompt'](x)
            x = x.squeeze(1)  # Back to (batch, dim)
            x = self.encoder(x)

        else:  # finetune
            x = self.encoder(x)

        return self.value_head(x).squeeze(-1)

    def get_adaptation_params(self) -> List[nn.Parameter]:
        """Get parameters that should be adapted"""
        if self.config.strategy == 'finetune':
            return list(self.parameters())
        else:
            return list(self.adaptation_modules.parameters())

    def count_adaptation_params(self) -> int:
        """Count number of trainable parameters"""
        return sum(p.numel() for p in self.get_adaptation_params() if p.requires_grad)

    def count_total_params(self) -> int:
        """Count total parameters"""
        return sum(p.numel() for p in self.parameters())


class AdaptationEvaluator:
    """
    Evaluates rapid adaptation strategies
    """

    def __init__(self):
        self.results = {
            'finetune': {},
            'lora': {},
            'adapter': {},
            'prompt': {}
        }

    def evaluate_strategy(
        self,
        strategy: str,
        model: nn.Module,
        tasks: List[Dict[str, torch.Tensor]],
        config: AdaptationConfig
    ) -> Dict[str, Any]:
        """Evaluate a single adaptation strategy"""
        print(f"\nEvaluating {strategy.upper()} adaptation...")

        results = {
            'losses': [],
            'adaptation_times': [],
            'param_counts': [],
            'convergence_speeds': []
        }

        for task in tasks:
            # Create model copy
            model_copy = RapidAdaptationModel(config=AdaptationConfig(strategy=strategy))
            model_copy.load_state_dict(model.state_dict())

            # Measure adaptation
            start_time = time.time()

            # Adapt to task
            adapted_model = self._adapt(model_copy, task, config)

            adaptation_time = time.time() - start_time

            # Evaluate
            with torch.no_grad():
                predictions = adapted_model(task['query_x'])
                loss = nn.functional.mse_loss(predictions, task['query_y'])

            results['losses'].append(loss.item())
            results['adaptation_times'].append(adaptation_time)
            results['param_counts'].append(model_copy.count_adaptation_params())

            # Measure convergence
            steps = self._measure_convergence(model_copy, task, config)
            results['convergence_speeds'].append(steps)

        # Aggregate results
        return {
            'loss_mean': np.mean(results['losses']),
            'loss_std': np.std(results['losses']),
            'adaptation_time_mean': np.mean(results['adaptation_times']),
            'adaptation_params': results['param_counts'][0],
            'convergence_speed': np.mean(results['convergence_speeds']),
            'param_efficiency': results['param_counts'][0] / model_copy.count_total_params()
        }

    def _adapt(
        self,
        model: nn.Module,
        task: Dict,
        config: AdaptationConfig
    ) -> nn.Module:
        """Adapt model to task"""
        # Only optimize adaptation parameters
        optimizer = optim.Adam(
            model.get_adaptation_params(),
            lr=config.learning_rate
        )

        for _ in range(config.adaptation_steps):
            optimizer.zero_grad()

            predictions = model(task['support_x'])
            loss = nn.functional.mse_loss(predictions, task['support_y'])

            loss.backward()
            optimizer.step()

        return model

    def _measure_convergence(
        self,
        model: nn.Module,
        task: Dict,
        config: AdaptationConfig,
        threshold: float = 0.01
    ) -> int:
        """Measure steps to convergence"""
        optimizer = optim.Adam(
            model.get_adaptation_params(),
            lr=config.learning_rate
        )

        prev_loss = float('inf')

        for step in range(50):
            optimizer.zero_grad()

            predictions = model(task['support_x'])
            loss = nn.functional.mse_loss(predictions, task['support_y'])

            if abs(prev_loss - loss.item()) < threshold:
                return step

            prev_loss = loss.item()

            loss.backward()
            optimizer.step()

        return 50


def compare_strategies():
    """
    Compare all rapid adaptation strategies

    Tests:
    1. Adaptation speed
    2. Parameter efficiency
    3. Performance quality
    4. Stability across tasks
    """
    print("\n" + "=" * 60)
    print("Rapid Adaptation Strategy Comparison")
    print("=" * 60)

    # Generate test tasks
    tasks = [generate_mock_task() for _ in range(20)]

    strategies = ['finetune', 'lora', 'adapter', 'prompt']
    evaluator = AdaptationEvaluator()

    results = {}

    for strategy in strategies:
        config = AdaptationConfig(strategy=strategy)
        model = RapidAdaptationModel(config=config)

        results[strategy] = evaluator.evaluate_strategy(
            strategy, model, tasks, config
        )

        print(f"\n{strategy.upper()} Results:")
        print(f"  Loss: {results[strategy]['loss_mean']:.4f} ± {results[strategy]['loss_std']:.4f}")
        print(f"  Adaptation Time: {results[strategy]['adaptation_time_mean']*1000:.2f}ms")
        print(f"  Adaptation Params: {results[strategy]['adaptation_params']:,}")
        print(f"  Param Efficiency: {results[strategy]['param_efficiency']*100:.2f}%")
        print(f"  Convergence: {results[strategy]['convergence_speed']:.1f} steps")

    # Plot comparison
    plot_strategy_comparison(results)

    return results


def plot_strategy_comparison(results: Dict[str, Dict[str, float]]):
    """Plot strategy comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    strategies = list(results.keys())

    # 1. Loss comparison
    ax = axes[0, 0]
    losses = [results[s]['loss_mean'] for s in strategies]
    errors = [results[s]['loss_std'] for s in strategies]
    ax.bar(strategies, losses, yerr=errors, alpha=0.7, capsize=5)
    ax.set_ylabel('Loss')
    ax.set_title('Performance Quality')
    ax.set_yscale('log')

    # 2. Parameter efficiency
    ax = axes[0, 1]
    param_efficiency = [results[s]['param_efficiency'] * 100 for s in strategies]
    ax.bar(strategies, param_efficiency, alpha=0.7, color='green')
    ax.set_ylabel('Trainable Parameters (%)')
    ax.set_title('Parameter Efficiency')

    # 3. Adaptation speed
    ax = axes[1, 0]
    times = [results[s]['adaptation_time_mean'] * 1000 for s in strategies]
    ax.bar(strategies, times, alpha=0.7, color='orange')
    ax.set_ylabel('Adaptation Time (ms)')
    ax.set_title('Adaptation Speed')

    # 4. Convergence speed
    ax = axes[1, 1]
    convergence = [results[s]['convergence_speed'] for s in strategies]
    ax.bar(strategies, convergence, alpha=0.7, color='purple')
    ax.set_ylabel('Steps to Convergence')
    ax.set_title('Convergence Speed')

    plt.tight_layout()
    plt.savefig('simulations/advanced/metalearning/rapid_adaptation_comparison.png', dpi=150)
    plt.close()

    print("\nSaved strategy comparison to rapid_adaptation_comparison.png")


def optimize_lora_hyperparameters():
    """
    Optimize LoRA hyperparameters

    Tests:
    1. Rank (r): How low can we go?
    2. Alpha (α): Scaling factor
    3. Dropout: Regularization
    """
    print("\n" + "=" * 60)
    print("Optimizing LoRA Hyperparameters")
    print("=" * 60)

    grid = {
        'rank': [4, 8, 16, 32],
        'alpha': [8, 16, 32, 64],
        'dropout': [0.0, 0.1, 0.2]
    }

    results = []
    best_config = None
    best_loss = float('inf')

    tasks = [generate_mock_task() for _ in range(10)]

    for _ in range(20):
        config = AdaptationConfig(
            strategy='lora',
            lora_rank=int(np.random.choice(grid['rank'])),
            lora_alpha=int(np.random.choice(grid['alpha'])),
            lora_dropout=float(np.random.choice(grid['dropout']))
        )

        model = RapidAdaptationModel(config=config)
        evaluator = AdaptationEvaluator()

        metrics = evaluator.evaluate_strategy('lora', model, tasks, config)
        results.append({
            'config': config,
            'loss': metrics['loss_mean']
        })

        if metrics['loss_mean'] < best_loss:
            best_loss = metrics['loss_mean']
            best_config = config

    print(f"\nBest LoRA Configuration:")
    print(f"  Rank: {best_config.lora_rank}")
    print(f"  Alpha: {best_config.lora_alpha}")
    print(f"  Dropout: {best_config.lora_dropout}")
    print(f"  Best Loss: {best_loss:.4f}")

    return best_config


def generate_mock_task(
    state_dim: int = 128,
    num_support: int = 25,
    num_query: int = 15
) -> Dict[str, torch.Tensor]:
    """Generate a mock task"""
    support_x = torch.randn(num_support, state_dim)
    support_y = torch.randn(num_support)
    query_x = torch.randn(num_query, state_dim)
    query_y = torch.randn(num_query)

    return {
        'support_x': support_x,
        'support_y': support_y,
        'query_x': query_x,
        'query_y': query_y
    }


def generate_recommendations(results: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Generate rapid adaptation recommendations"""
    print("\n" + "=" * 60)
    print("Rapid Adaptation Recommendations")
    print("=" * 60)

    # Find best strategy per metric
    best_speed = min(results.items(), key=lambda x: x[1]['adaptation_time_mean'])
    best_efficiency = min(results.items(), key=lambda x: x[1]['param_efficiency'])
    best_performance = min(results.items(), key=lambda x: x[1]['loss_mean'])
    best_convergence = min(results.items(), key=lambda x: x[1]['convergence_speed'])

    recommendations = {
        'fastest_adaptation': {
            'strategy': best_speed[0],
            'time_ms': best_speed[1]['adaptation_time_mean'] * 1000
        },
        'most_efficient': {
            'strategy': best_efficiency[0],
            'params_percent': best_efficiency[1]['param_efficiency'] * 100
        },
        'best_performance': {
            'strategy': best_performance[0],
            'loss': best_performance[1]['loss_mean']
        },
        'fastest_convergence': {
            'strategy': best_convergence[0],
            'steps': best_convergence[1]['convergence_speed']
        },
        'overall_recommendation': 'lora',  # Best balance
        'scenarios': {
            'low_resource': 'adapter',
            'high_performance': 'finetune',
            'balanced': 'lora',
            'llm_finetuning': 'prompt'
        }
    }

    print("\nPer-Metric Best:")
    print(f"  Fastest: {best_speed[0].upper()} ({best_speed[1]['adaptation_time_mean']*1000:.2f}ms)")
    print(f"  Most Efficient: {best_efficiency[0].upper()} ({best_efficiency[1]['param_efficiency']*100:.2f}%)")
    print(f"  Best Performance: {best_performance[0].upper()} ({best_performance[1]['loss_mean']:.4f})")
    print(f"  Fastest Convergence: {best_convergence[0].upper()} ({best_convergence[1]['convergence_speed']:.1f} steps)")

    print("\nScenario Recommendations:")
    for scenario, strategy in recommendations['scenarios'].items():
        print(f"  {scenario}: {strategy.upper()}")

    return recommendations


def main():
    """Main execution"""
    print("=" * 60)
    print("Rapid Adaptation Strategies for POLLN")
    print("=" * 60)

    Path('simulations/advanced/metalearning').mkdir(parents=True, exist_ok=True)

    # 1. Compare strategies
    print("\n1. Strategy Comparison")
    print("-" * 60)
    results = compare_strategies()

    # 2. Optimize LoRA
    print("\n2. LoRA Optimization")
    print("-" * 60)
    lora_config = optimize_lora_hyperparameters()

    # 3. Generate recommendations
    print("\n3. Generate Recommendations")
    print("-" * 60)
    recommendations = generate_recommendations(results)

    # Save recommendations
    import json
    config = {
        'strategy': recommendations['overall_recommendation'],
        'lora': {
            'rank': lora_config.lora_rank,
            'alpha': lora_config.lora_alpha,
            'dropout': lora_config.lora_dropout
        },
        'scenarios': recommendations['scenarios']
    }

    with open('simulations/advanced/metalearning/rapid_adaptation_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("\n" + "=" * 60)
    print("Rapid adaptation testing complete!")
    print("=" * 60)

    return {
        'results': results,
        'lora_config': lora_config,
        'recommendations': recommendations
    }


if __name__ == '__main__':
    main()
