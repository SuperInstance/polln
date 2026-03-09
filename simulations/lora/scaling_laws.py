"""
Scaling Laws for LoRA Libraries

Derives performance scaling relationships:
accuracy = a + b·log(params) + c·n_loras - d·interference

Key questions:
1. When is LoRA library more efficient than bigger model?
2. What is the optimal base model size for N LoRAs?
3. Where do diminishing returns occur?
4. Break-even point: N LoRAs vs single large model

Mathematical foundation:
- Chinchilla scaling laws for base models
- Interference penalties for composition
- Computation-efficiency tradeoffs
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import pandas as pd


@dataclass
class ScalingLawCoefficients:
    """Coefficients for scaling law: accuracy = a + b·log(params) + c·n_loras - d·interference"""
    a: float  # Intercept
    b: float  # Log params coefficient
    c: float  # Number of LoRAs coefficient
    d: float  # Interference penalty coefficient

    def predict(
        self,
        n_params: float,
        n_loras: int,
        interference: float
    ) -> float:
        """Predict accuracy using scaling law"""
        return self.a + self.b * np.log(n_params) + self.c * n_loras - self.d * interference


@dataclass
class EfficiencyMetrics:
    """Metrics for comparing efficiency"""
    lora_library_params: int
    single_model_params: int
    lora_library_accuracy: float
    single_model_accuracy: float
    param_ratio: float
    accuracy_ratio: float
    break_even: bool


class ScalingLawDataGenerator:
    """Generate synthetic data for fitting scaling laws"""

    def __init__(
        self,
        base_dims: List[int] = None,
        n_loras_range: Tuple[int, int] = (1, 16),
        ranks: List[int] = None
    ):
        self.base_dims = base_dims or [256, 512, 1024, 2048]
        self.n_loras_range = n_loras_range
        self.ranks = ranks or [8, 16, 32, 64]

    def count_parameters(
        self,
        base_dim: int,
        n_loras: int,
        rank: int
    ) -> int:
        """
        Count total parameters

        Total = base_params + n_loras × lora_params
        where lora_params = 2 × rank × base_dim
        """
        base_params = base_dim ** 2
        lora_params = 2 * rank * base_dim
        total_params = base_params + n_loras * lora_params
        return total_params

    def generate_scenario(
        self,
        base_dim: int,
        n_loras: int,
        rank: int,
        interference_level: float = 0.1
    ) -> Dict:
        """
        Generate a scenario with ground truth accuracy

        Uses synthetic accuracy based on scaling principles
        """
        from .rank_analysis import SyntheticModelGenerator, LoRADecomposer

        # Count parameters
        n_params = self.count_parameters(base_dim, n_loras, rank)

        # Generate synthetic accuracy (ground truth)
        # Based on Chinchilla-like scaling with LoRA improvements
        base_accuracy = 0.5 + 0.1 * np.log10(n_params / 1e6)  # Base model scaling
        lora_boost = 0.05 * np.log(n_loras + 1)  # Logarithmic boost from LoRAs
        interference_penalty = interference_level * n_loras * 0.01  # Linear penalty

        accuracy = base_accuracy + lora_boost - interference_penalty
        accuracy = np.clip(accuracy, 0, 1)  # Clip to [0, 1]

        return {
            "base_dim": base_dim,
            "n_loras": n_loras,
            "rank": rank,
            "n_params": n_params,
            "interference": interference_level * n_loras,
            "accuracy": accuracy
        }

    def generate_dataset(
        self,
        n_scenarios: int = 1000
    ) -> List[Dict]:
        """Generate diverse dataset for fitting"""
        scenarios = []

        for _ in range(n_scenarios):
            base_dim = np.random.choice(self.base_dims)
            n_loras = np.random.randint(*self.n_loras_range)
            rank = np.random.choice(self.ranks)
            interference_level = np.random.uniform(0.05, 0.3)

            scenario = self.generate_scenario(
                base_dim, n_loras, rank, interference_level
            )
            scenarios.append(scenario)

        return scenarios


class ScalingLawAnalyzer:
    """
    Analyze and fit scaling laws for LoRA libraries

    Derives: accuracy = a + b·log(params) + c·n_loras - d·interference
    """

    def __init__(self):
        self.coefficients: Optional[ScalingLawCoefficients] = None
        self.data_generator = ScalingLawDataGenerator()

    def scaling_law_function(
        self,
        X: np.ndarray,
        a: float,
        b: float,
        c: float,
        d: float
    ) -> np.ndarray:
        """
        Scaling law function for curve fitting

        X: [log_params, n_loras, interference]
        Returns: accuracy predictions
        """
        log_params, n_loras, interference = X
        return a + b * log_params + c * n_loras - d * interference

    def fit_scaling_law(
        self,
        data: List[Dict]
    ) -> ScalingLawCoefficients:
        """
        Fit scaling law coefficients from data

        Uses least squares optimization
        """
        # Prepare data
        log_params = np.array([np.log(d["n_params"]) for d in data])
        n_loras = np.array([d["n_loras"] for d in data])
        interference = np.array([d["interference"] for d in data])
        accuracy = np.array([d["accuracy"] for d in data])

        # Stack features
        X = np.vstack([log_params, n_loras, interference])

        # Fit using curve_fit
        from scipy.optimize import least_squares

        def residuals(params, X, y):
            a, b, c, d = params
            y_pred = a + b * X[0] + c * X[1] - d * X[2]
            return y - y_pred

        # Initial guess
        initial_guess = [0.5, 0.05, 0.02, 0.01]

        result = least_squares(
            residuals,
            initial_guess,
            args=(X, accuracy),
            method='lm'
        )

        a, b, c, d = result.x

        self.coefficients = ScalingLawCoefficients(a, b, c, d)

        # Compute fit quality
        y_pred = self.coefficients.predict(
            np.exp(log_params),
            n_loras,
            interference
        )
        r_squared = 1 - np.sum((accuracy - y_pred) ** 2) / np.sum((accuracy - accuracy.mean()) ** 2)

        print(f"\nScaling Law Coefficients:")
        print(f"  a (intercept): {a:.4f}")
        print(f"  b (log params): {b:.4f}")
        print(f"  c (n_loras): {c:.4f}")
        print(f"  d (interference): {d:.4f}")
        print(f"  R²: {r_squared:.4f}")

        return self.coefficients

    def predict_accuracy(
        self,
        n_params: int,
        n_loras: int,
        interference: float
    ) -> float:
        """Predict accuracy using fitted scaling law"""
        if self.coefficients is None:
            raise ValueError("Must fit scaling law first")

        return self.coefficients.predict(n_params, n_loras, interference)

    def find_optimal_configuration(
        self,
        target_accuracy: float,
        max_loras: int = 20,
        base_dims: List[int] = None,
        ranks: List[int] = None
    ) -> Dict:
        """
        Find optimal configuration for target accuracy

        Searches over base_dim, n_loras, rank combinations
        """
        if self.coefficients is None:
            raise ValueError("Must fit scaling law first")

        base_dims = base_dims or [256, 512, 1024, 2048]
        ranks = ranks or [8, 16, 32, 64]

        best_config = None
        min_params = float('inf')

        for base_dim in base_dims:
            for n_loras in range(1, max_loras + 1):
                for rank in ranks:
                    # Estimate interference
                    interference = 0.1 * n_loras

                    # Count parameters
                    n_params = self.data_generator.count_parameters(
                        base_dim, n_loras, rank
                    )

                    # Predict accuracy
                    accuracy = self.predict_accuracy(
                        n_params, n_loras, interference
                    )

                    # Check if meets target
                    if accuracy >= target_accuracy and n_params < min_params:
                        min_params = n_params
                        best_config = {
                            "base_dim": base_dim,
                            "n_loras": n_loras,
                            "rank": rank,
                            "n_params": n_params,
                            "predicted_accuracy": accuracy
                        }

        return best_config

    def compare_lora_vs_single_model(
        self,
        base_dim: int,
        n_loras: int,
        rank: int,
        single_model_params: int
    ) -> EfficiencyMetrics:
        """
        Compare LoRA library efficiency vs single large model

        Returns efficiency metrics
        """
        if self.coefficients is None:
            raise ValueError("Must fit scaling law first")

        # LoRA library metrics
        lora_params = self.data_generator.count_parameters(
            base_dim, n_loras, rank
        )
        interference = 0.1 * n_loras
        lora_accuracy = self.predict_accuracy(
            lora_params, n_loras, interference
        )

        # Single model metrics
        # Assume no interference (n_loras=0)
        single_accuracy = self.predict_accuracy(
            single_model_params, 0, 0
        )

        # Compute ratios
        param_ratio = lora_params / single_model_params
        accuracy_ratio = lora_accuracy / single_accuracy

        # Break-even: more accurate or same accuracy with fewer params
        break_even = (lora_accuracy >= single_accuracy) or (
            lora_params <= single_model_params and lora_accuracy >= 0.95 * single_accuracy
        )

        return EfficiencyMetrics(
            lora_library_params=lora_params,
            single_model_params=single_model_params,
            lora_library_accuracy=lora_accuracy,
            single_model_accuracy=single_accuracy,
            param_ratio=param_ratio,
            accuracy_ratio=accuracy_ratio,
            break_even=break_even
        )

    def compute_break_even_curve(
        self,
        base_dim: int,
        rank: int,
        max_loras: int = 20
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute break-even curve

        Returns: (n_loras, single_model_params_needed)
        """
        if self.coefficients is None:
            raise ValueError("Must fit scaling law first")

        lora_counts = np.arange(1, max_loras + 1)
        single_model_params_needed = []

        for n_loras in lora_counts:
            # LoRA library accuracy
            lora_params = self.data_generator.count_parameters(
                base_dim, n_loras, rank
            )
            interference = 0.1 * n_loras
            lora_accuracy = self.predict_accuracy(
                lora_params, n_loras, interference
            )

            # Find single model params needed for same accuracy
            # Solve: a + b*log(params) = lora_accuracy
            # log(params) = (lora_accuracy - a) / b
            log_params = (lora_accuracy - self.coefficients.a) / self.coefficients.b
            single_params = np.exp(log_params)

            single_model_params_needed.append(single_params)

        return lora_counts, np.array(single_model_params_needed)

    def find_diminishing_returns(
        self,
        base_dim: int,
        rank: int,
        threshold: float = 0.01
    ) -> int:
        """
        Find point of diminishing returns

        Returns n_loras where additional LoRAs give < threshold% improvement
        """
        if self.coefficients is None:
            raise ValueError("Must fit scaling law first")

        prev_accuracy = 0

        for n_loras in range(1, 50):
            lora_params = self.data_generator.count_parameters(
                base_dim, n_loras, rank
            )
            interference = 0.1 * n_loras
            accuracy = self.predict_accuracy(
                lora_params, n_loras, interference
            )

            if n_loras > 1:
                improvement = (accuracy - prev_accuracy) / prev_accuracy

                if improvement < threshold:
                    return n_loras - 1

            prev_accuracy = accuracy

        return 50  # Default if no diminishing returns

    def run_full_analysis(
        self,
        output_dir: Path = Path("./simulations/lora/results")
    ) -> Dict:
        """
        Run complete scaling law analysis

        Returns comprehensive results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("LoRA Scaling Laws Analysis")
        print("=" * 60)

        # 1. Generate training data
        print("\nGenerating training data...")
        data = self.data_generator.generate_dataset(n_scenarios=2000)
        print(f"  Generated {len(data)} scenarios")

        # 2. Fit scaling law
        print("\nFitting scaling law...")
        coefficients = self.fit_scaling_law(data)

        # 3. Compute break-even curves
        print("\nComputing break-even curves...")
        break_even_curves = {}

        for base_dim in [512, 1024, 2048]:
            for rank in [16, 32, 64]:
                loras, single_params = self.compute_break_even_curve(
                    base_dim, rank, max_loras=20
                )
                break_even_curves[f"{base_dim}_{rank}"] = {
                    "n_loras": loras.tolist(),
                    "single_model_params": single_params.tolist()
                }

        # 4. Find optimal configurations
        print("\nFinding optimal configurations...")
        optimal_configs = {}

        for target_acc in [0.7, 0.75, 0.8, 0.85, 0.9]:
            config = self.find_optimal_configuration(
                target_accuracy=target_acc,
                max_loras=20
            )
            optimal_configs[f"target_{target_acc}"] = config
            print(f"  Target {target_acc}: {config}")

        # 5. Find diminishing returns
        print("\nFinding diminishing returns points...")
        diminishing_returns = {}

        for base_dim in [512, 1024, 2048]:
            for rank in [16, 32, 64]:
                point = self.find_diminishing_returns(base_dim, rank)
                diminishing_returns[f"{base_dim}_{rank}"] = point

        # 6. Visualize
        print("\nGenerating visualizations...")
        self._plot_break_even_curves(break_even_curves, output_dir)
        self._plot_accuracy_surface(base_dim=1024, rank=32, output_dir=output_dir)
        self._plot_diminishing_returns(diminishing_returns, output_dir)

        # 7. Compile results
        results = {
            "coefficients": {
                "a": coefficients.a,
                "b": coefficients.b,
                "c": coefficients.c,
                "d": coefficients.d
            },
            "scaling_law": "accuracy = a + b·log(params) + c·n_loras - d·interference",
            "break_even_curves": break_even_curves,
            "optimal_configurations": optimal_configs,
            "diminishing_returns": diminishing_returns,
            "key_findings": {
                "lora_efficiency_threshold": "N LoRAs more efficient when:",
                "break_even_formula": "N_lora_params < 2 × n_loras × rank × base_dim",
                "diminishing_returns": "Additional LoRAs give <1% improvement"
            }
        }

        results_path = output_dir / "scaling_law_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results: {results_path}")

        return results

    def _plot_break_even_curves(
        self,
        break_even_curves: Dict,
        output_dir: Path
    ):
        """Plot break-even curves"""
        plt.figure(figsize=(12, 8))

        for config_name, curve_data in break_even_curves.items():
            n_loras = curve_data["n_loras"]
            single_params = curve_data["single_model_params"]

            # Convert to millions
            single_params_million = np.array(single_params) / 1e6

            plt.plot(n_loras, single_params_million, 'o-', label=config_name, linewidth=2)

        plt.xlabel('Number of LoRAs', fontsize=14)
        plt.ylabel('Single Model Parameters (millions)', fontsize=14)
        plt.title('Break-Even Curve: LoRA Library vs Single Model\nWhen is LoRA more efficient?',
                  fontsize=16)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "break_even_curves.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_accuracy_surface(
        self,
        base_dim: int,
        rank: int,
        output_dir: Path
    ):
        """Plot accuracy as function of n_loras and params"""
        if self.coefficients is None:
            return

        n_loras_range = np.arange(1, 21)
        interference_range = np.linspace(0, 2, 50)

        # Create meshgrid
        N_loras, Interference = np.meshgrid(n_loras_range, interference_range)

        # Compute accuracy surface
        Accuracy = np.zeros_like(N_loras)
        for i in range(N_loras.shape[0]):
            for j in range(N_loras.shape[1]):
                n_loras = N_loras[i, j]
                interference = Interference[i, j]
                n_params = self.data_generator.count_parameters(base_dim, n_loras, rank)

                Accuracy[i, j] = self.predict_accuracy(n_params, n_loras, interference)

        # Plot
        fig = plt.figure(figsize=(14, 6))

        # 3D surface
        ax1 = fig.add_subplot(1, 2, 1, projection='3d')
        surf = ax1.plot_surface(N_loras, Interference, Accuracy, cmap='viridis')
        ax1.set_xlabel('Number of LoRAs')
        ax1.set_ylabel('Interference')
        ax1.set_zlabel('Accuracy')
        ax1.set_title(f'Accuracy Surface\n(base_dim={base_dim}, rank={rank})')
        fig.colorbar(surf, ax=ax1, shrink=0.5)

        # Contour plot
        ax2 = fig.add_subplot(1, 2, 2)
        contour = ax2.contourf(N_loras, Interference, Accuracy, levels=20, cmap='viridis')
        ax2.set_xlabel('Number of LoRAs')
        ax2.set_ylabel('Interference')
        ax2.set_title('Accuracy Contours')
        fig.colorbar(contour, ax=ax2)

        plt.tight_layout()
        plt.savefig(output_dir / "accuracy_surface.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_diminishing_returns(
        self,
        diminishing_returns: Dict,
        output_dir: Path
    ):
        """Plot diminishing returns points"""
        fig, ax = plt.subplots(figsize=(12, 6))

        configs = list(diminishing_returns.keys())
        points = list(diminishing_returns.values())

        # Group by base_dim
        base_dims = sorted(set(int(c.split('_')[0]) for c in configs))

        x = np.arange(len(configs))
        bars = ax.bar(x, points, alpha=0.7)

        # Color by base_dim
        colors = plt.cm.viridis(np.linspace(0, 1, len(base_dims)))
        for i, config in enumerate(configs):
            base_dim = int(config.split('_')[0])
            idx = base_dims.index(base_dim)
            bars[i].set_color(colors[idx])

        ax.set_xticks(x)
        ax.set_xticklabels(configs, rotation=45, ha='right')
        ax.set_ylabel('Number of LoRAs at Diminishing Returns')
        ax.set_title('Diminishing Returns Points\n(Where additional LoRAs give <1% improvement)')
        ax.grid(axis='y', alpha=0.3)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors[i], label=f'base_dim={base_dims[i]}')
                          for i in range(len(base_dims))]
        ax.legend(handles=legend_elements)

        plt.tight_layout()
        plt.savefig(output_dir / "diminishing_returns.png", dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Run scaling laws analysis"""
    analyzer = ScalingLawAnalyzer()
    results = analyzer.run_full_analysis()

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    print("\nKey Insights:")
    print(f"1. Scaling Law: {results['scaling_law']}")
    print(f"2. Coefficients: a={results['coefficients']['a']:.4f}, "
          f"b={results['coefficients']['b']:.4f}, "
          f"c={results['coefficients']['c']:.4f}, "
          f"d={results['coefficients']['d']:.4f}")


if __name__ == "__main__":
    main()
