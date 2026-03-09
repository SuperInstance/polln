"""
Composition Optimization for LoRA Library

Validates optimal weight strategies for combining LoRAs

Mathematical formulation:
loss = ||W_target - W_base - Σ w_i(B_iA_i)||² + λΣw_i²

Key questions:
1. What are optimal composition weights?
2. How do learned weights compare to heuristics?
3. Does 1/√N weighting work?
4. Linear vs non-linear composition
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy.optimize import minimize
from sklearn.model_selection import train_test_split


@dataclass
class CompositionResult:
    """Results from composition optimization"""
    method: str
    weights: np.ndarray
    reconstruction_error: float
    regularization_penalty: float
    total_loss: float
    performance: float
    convergence_iterations: int


class CompositionStrategy:
    """Different strategies for composing LoRAs"""

    @staticmethod
    def uniform(n_loras: int) -> np.ndarray:
        """Uniform weights: w_i = 1/N"""
        return np.ones(n_loras) / n_loras

    @staticmethod
    def inverse_sqrt(n_loras: int) -> np.ndarray:
        """Inverse square root: w_i = 1/√N"""
        w = 1.0 / np.sqrt(n_loras)
        return np.ones(n_loras) * w

    @staticmethod
    def rank_weighted(loras: List[Tuple[torch.Tensor, torch.Tensor]]) -> np.ndarray:
        """
        Weight by rank: w_i ∝ rank_i / Σ rank_j
        Higher rank = more capacity = higher weight
        """
        ranks = np.array([A.shape[0] for _, A in loras])
        return ranks / ranks.sum()

    @staticmethod
    def norm_weighted(loras: List[Tuple[torch.Tensor, torch.Tensor]]) -> np.ndarray:
        """
        Weight by Frobenius norm: w_i ∝ ||BA||_F / Σ ||BA||_F
        Larger effect = higher weight
        """
        norms = np.array([
            torch.norm(B @ A, 'fro').item()
            for B, A in loras
        ])
        return norms / (norms.sum() + 1e-8)

    @staticmethod
    def learned(
        loras: List[Tuple[torch.Tensor, torch.Tensor]],
        W_target: torch.Tensor,
        W_base: torch.Tensor,
        lambda_reg: float = 0.01,
        max_iter: int = 1000
    ) -> np.ndarray:
        """
        Learned weights via gradient descent

        Minimize: ||W_target - W_base - Σ w_i(B_iA_i)||² + λΣw_i²
        """
        n_loras = len(loras)

        # Initialize weights
        w = torch.ones(n_loras, requires_grad=True) / n_loras
        optimizer = torch.optim.Adam([w], lr=0.1)

        # Precompute LoRA matrices
        delta_Ws = [B @ A for B, A in loras]

        # Flatten target for efficiency
        delta_target = (W_target - W_base).flatten()

        losses = []
        for i in range(max_iter):
            optimizer.zero_grad()

            # Combined LoRA
            delta_combined = sum(w[i] * delta_Ws[i].flatten() for i in range(n_loras))

            # Reconstruction loss
            recon_loss = torch.norm(delta_target - delta_combined) ** 2

            # Regularization
            reg_loss = lambda_reg * torch.sum(w ** 2)

            # Total loss
            loss = recon_loss + reg_loss
            losses.append(loss.item())

            # Optimize
            loss.backward()
            optimizer.step()

            # Project to valid weights (non-negative, sum=1)
            with torch.no_grad():
                w.data = torch.clamp(w.data, min=0)
                w.data = w.data / (w.data.sum() + 1e-8)

            # Early stopping
            if len(losses) > 50 and np.std(losses[-50:]) < 1e-6:
                break

        return w.detach().cpu().numpy()

    @staticmethod
    def closed_form(
        loras: List[Tuple[torch.Tensor, torch.Tensor]],
        W_target: torch.Tensor,
        W_base: torch.Tensor,
        lambda_reg: float = 0.01
    ) -> np.ndarray:
        """
        Closed-form solution (analytical)

        For L2-regularized least squares:
        w* = (X^T X + λI)^(-1) X^T y

        Where X is flattened LoRA matrices
        """
        n_loras = len(loras)

        # Flatten all LoRA matrices
        delta_target = (W_target - W_base).flatten().cpu().numpy()
        X = np.stack([
            (B @ A).flatten().cpu().numpy()
            for B, A in loras
        ]).T  # Shape: (d^2, n_loras)

        # Closed-form solution
        # w = (X^T X + λI)^(-1) X^T y
        XtX = X.T @ X
        Xty = X.T @ delta_target

        # Add regularization
        XtX_reg = XtX + lambda_reg * np.eye(n_loras)

        # Solve
        w = np.linalg.solve(XtX_reg, Xty)

        # Ensure non-negative and normalize
        w = np.maximum(w, 0)
        w = w / (w.sum() + 1e-8)

        return w


class CompositionOptimizer:
    """
    Optimize LoRA composition weights

    Compare different strategies:
    - Heuristics (uniform, 1/√N, rank-weighted, norm-weighted)
    - Learned (gradient descent)
    - Closed-form (analytical)
    """

    def __init__(
        self,
        base_dim: int = 1024,
        lambda_reg: float = 0.01
    ):
        self.base_dim = base_dim
        self.lambda_reg = lambda_reg
        self.strategy = CompositionStrategy()

    def generate_composition_scenario(
        self,
        n_loras: int = 5,
        ranks: List[int] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, List[Tuple[torch.Tensor, torch.Tensor]]]:
        """
        Generate a scenario for composition testing

        Returns:
        - W_target: Target combined expertise
        - W_base: Base model weights
        - loras: List of (B_i, A_i) tuples
        """
        from .rank_analysis import SyntheticModelGenerator, LoRADecomposer

        if ranks is None:
            ranks = np.random.randint(8, 64, size=n_loras).tolist()

        # Generate base model
        model_gen = SyntheticModelGenerator(self.base_dim)
        W_base = model_gen.generate_base_model()

        # Generate target by combining expert models
        domains = ["code", "writing", "analysis", "research"]
        selected_domains = np.random.choice(domains, n_loras, replace=True)

        # Create LoRAs
        loras = []
        W_target = W_base.clone()

        for domain, rank in zip(selected_domains, ranks):
            W_expert = model_gen.generate_expert_weights(
                W_base, domain, expertise_strength=0.3
            )

            decomposer = LoRADecomposer(rank)
            B, A = decomposer.decompose(W_base, W_expert)
            loras.append((B, A))

            # Add to target (with random weight)
            weight = np.random.uniform(0.5, 1.5)
            W_target += weight * (B @ A)

        return W_target, W_base, loras

    def evaluate_composition(
        self,
        weights: np.ndarray,
        loras: List[Tuple[torch.Tensor, torch.Tensor]],
        W_target: torch.Tensor,
        W_base: torch.Tensor,
        X_test: Optional[torch.Tensor] = None,
        y_test: Optional[torch.Tensor] = None
    ) -> CompositionResult:
        """
        Evaluate a composition strategy

        Returns reconstruction error and performance
        """
        # Reconstruct
        delta_combined = sum(
            w * (B @ A) for w, (B, A) in zip(weights, loras)
        )
        W_combined = W_base + delta_combined

        # Reconstruction error
        recon_error = torch.norm(W_target - W_combined, 'fro').item()

        # Regularization penalty
        reg_penalty = self.lambda_reg * np.sum(weights ** 2)

        # Total loss
        total_loss = recon_error + reg_penalty

        # Performance (if test data provided)
        if X_test is not None and y_test is not None:
            pred = X_test @ W_combined.T
            performance = -torch.mean((pred - y_test) ** 2).item()
        else:
            performance = 0.0

        return CompositionResult(
            method="",
            weights=weights,
            reconstruction_error=recon_error,
            regularization_penalty=reg_penalty,
            total_loss=total_loss,
            performance=performance,
            convergence_iterations=0
        )

    def compare_strategies(
        self,
        n_scenarios: int = 20,
        n_loras_range: Tuple[int, int] = (2, 8)
    ) -> Dict[str, List[CompositionResult]]:
        """
        Compare all composition strategies across scenarios

        Returns results for each strategy
        """
        results = {
            "uniform": [],
            "inverse_sqrt": [],
            "rank_weighted": [],
            "norm_weighted": [],
            "learned": [],
            "closed_form": []
        }

        for scenario_idx in range(n_scenarios):
            n_loras = np.random.randint(*n_loras_range)

            # Generate scenario
            W_target, W_base, loras = self.generate_composition_scenario(n_loras)

            # Generate test data
            X_test = torch.randn(100, self.base_dim)
            y_test = X_test @ W_target.T + torch.randn(100, self.base_dim) * 0.1

            # Evaluate each strategy
            # 1. Uniform
            w_uniform = self.strategy.uniform(n_loras)
            result_uniform = self.evaluate_composition(
                w_uniform, loras, W_target, W_base, X_test, y_test
            )
            result_uniform.method = "uniform"
            results["uniform"].append(result_uniform)

            # 2. Inverse sqrt
            w_inv_sqrt = self.strategy.inverse_sqrt(n_loras)
            result_inv_sqrt = self.evaluate_composition(
                w_inv_sqrt, loras, W_target, W_base, X_test, y_test
            )
            result_inv_sqrt.method = "inverse_sqrt"
            results["inverse_sqrt"].append(result_inv_sqrt)

            # 3. Rank weighted
            w_rank = self.strategy.rank_weighted(loras)
            result_rank = self.evaluate_composition(
                w_rank, loras, W_target, W_base, X_test, y_test
            )
            result_rank.method = "rank_weighted"
            results["rank_weighted"].append(result_rank)

            # 4. Norm weighted
            w_norm = self.strategy.norm_weighted(loras)
            result_norm = self.evaluate_composition(
                w_norm, loras, W_target, W_base, X_test, y_test
            )
            result_norm.method = "norm_weighted"
            results["norm_weighted"].append(result_norm)

            # 5. Learned
            w_learned = self.strategy.learned(
                loras, W_target, W_base, self.lambda_reg
            )
            result_learned = self.evaluate_composition(
                w_learned, loras, W_target, W_base, X_test, y_test
            )
            result_learned.method = "learned"
            result_learned.convergence_iterations = 1000  # Approximate
            results["learned"].append(result_learned)

            # 6. Closed form
            w_closed = self.strategy.closed_form(
                loras, W_target, W_base, self.lambda_reg
            )
            result_closed = self.evaluate_composition(
                w_closed, loras, W_target, W_base, X_test, y_test
            )
            result_closed.method = "closed_form"
            results["closed_form"].append(result_closed)

        return results

    def analyze_linearity(
        self,
        n_loras: int = 3,
        n_test_points: int = 50
    ) -> Dict[str, np.ndarray]:
        """
        Test linearity of composition

        For compatible LoRAs: (L1 ⊕ L2)(x) ≈ L1(x) + L2(x) - L1∩L2(x)

        When does linearity break down?
        """
        # Generate scenario
        W_target, W_base, loras = self.generate_composition_scenario(n_loras)

        # Test input
        X = torch.randn(n_test_points, self.base_dim)

        # Individual outputs
        outputs = []
        for B, A in loras:
            W_lora = W_base + B @ A
            output = X @ W_lora.T
            outputs.append(output)

        # Linear combination
        weights = np.random.dirichlet(np.ones(n_loras))
        output_linear = sum(w * out for w, out in zip(weights, outputs))

        # Actual combined
        delta_combined = sum(w * (B @ A) for w, (B, A) in zip(weights, loras))
        W_combined = W_base + delta_combined
        output_combined = X @ W_combined.T

        # Linearity error
        linearity_error = torch.norm(output_linear - output_combined, 'fro').item()
        linearity_error_norm = linearity_error / (torch.norm(output_linear, 'fro').item() + 1e-8)

        return {
            "linearity_error": linearity_error,
            "linearity_error_norm": linearity_error_norm,
            "weights": weights,
            "output_linear": output_linear.cpu().numpy(),
            "output_combined": output_combined.cpu().numpy()
        }

    def optimize_nonlinear_composition(
        self,
        loras: List[Tuple[torch.Tensor, torch.Tensor]],
        W_target: torch.Tensor,
        W_base: torch.Tensor,
        method: str = "gradient"
    ) -> np.ndarray:
        """
        Optimize non-linear composition

        Methods:
        - gradient: Direct gradient optimization
        - gating: Learned gating mechanism
        - attention: Attention-based composition
        """
        if method == "gradient":
            # Optimize with non-linear interaction terms
            n_loras = len(loras)

            # Parameters: weights + interaction coefficients
            params = torch.randn(n_loras + n_loras * (n_loras - 1) // 2, requires_grad=True)
            optimizer = torch.optim.Adam([params], lr=0.1)

            delta_target = (W_target - W_base).flatten()
            delta_Ws = [(B @ A).flatten() for B, A in loras]

            losses = []
            for i in range(2000):
                optimizer.zero_grad()

                # Extract weights and interactions
                weights = torch.softmax(params[:n_loras], dim=0)
                interactions = params[n_loras:]

                # Linear combination
                delta_linear = sum(weights[i] * delta_Ws[i] for i in range(n_loras))

                # Add interaction terms (simplified)
                idx = 0
                for i in range(n_loras):
                    for j in range(i + 1, n_loras):
                        # Element-wise interaction (simplified)
                        delta_linear += interactions[idx] * (
                            delta_Ws[i] * delta_Ws[j]
                        ) * 0.01  # Scale down
                        idx += 1

                # Loss
                loss = torch.norm(delta_target - delta_linear) ** 2
                losses.append(loss.item())

                loss.backward()
                optimizer.step()

                if len(losses) > 100 and np.std(losses[-100:]) < 1e-6:
                    break

            return weights.detach().cpu().numpy()

        else:
            raise ValueError(f"Unknown non-linear method: {method}")

    def run_full_analysis(
        self,
        output_dir: Path = Path("./simulations/lora/results")
    ) -> Dict:
        """
        Run complete composition optimization analysis

        Returns comprehensive results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("LoRA Composition Optimization Analysis")
        print("=" * 60)

        # 1. Compare strategies
        print("\nComparing composition strategies...")
        results = self.compare_strategies(n_scenarios=50, n_loras_range=(2, 6))

        # Compute summary statistics
        summary = {}
        for strategy, strategy_results in results.items():
            errors = [r.reconstruction_error for r in strategy_results]
            performances = [r.performance for r in strategy_results]

            summary[strategy] = {
                "mean_error": float(np.mean(errors)),
                "std_error": float(np.std(errors)),
                "mean_performance": float(np.mean(performances)),
                "std_performance": float(np.std(performances)),
                "best_error": float(np.min(errors)),
                "worst_error": float(np.max(errors))
            }

        print("\nStrategy Comparison (Reconstruction Error):")
        print("-" * 60)
        sorted_strategies = sorted(
            summary.items(),
            key=lambda x: x[1]["mean_error"]
        )

        for strategy, stats in sorted_strategies:
            print(f"{strategy:20s}: {stats['mean_error']:10.4f} ± {stats['std_error']:8.4f}")

        # 2. Test 1/√N hypothesis
        print("\nTesting 1/√N weighting hypothesis...")
        uniform_errors = [r.reconstruction_error for r in results["uniform"]]
        inv_sqrt_errors = [r.reconstruction_error for r in results["inverse_sqrt"]]

        t_stat, p_value = scipy.stats.ttest_rel(inv_sqrt_errors, uniform_errors)
        print(f"  1/√N better than uniform: p = {p_value:.4f}")
        print(f"  Mean improvement: {(np.mean(uniform_errors) - np.mean(inv_sqrt_errors)) / np.mean(uniform_errors) * 100:.2f}%")

        # 3. Analyze linearity
        print("\nAnalyzing composition linearity...")
        linearity_results = []
        for _ in range(20):
            result = self.analyze_linearity(n_loras=3)
            linearity_results.append(result["linearity_error_norm"])

        print(f"  Mean linearity error: {np.mean(linearity_results):.6f}")
        print(f"  Std linearity error: {np.std(linearity_results):.6f}")

        # 4. Visualize
        print("\nGenerating visualizations...")
        self._plot_strategy_comparison(summary, output_dir)
        self._plot_linearity_analysis(linearity_results, output_dir)

        # 5. Save results
        final_results = {
            "strategy_comparison": summary,
            "inverse_sqrt_hypothesis": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "mean_improvement_percent": float(
                    (np.mean(uniform_errors) - np.mean(inv_sqrt_errors)) / np.mean(uniform_errors) * 100
                )
            },
            "linearity_analysis": {
                "mean_error": float(np.mean(linearity_results)),
                "std_error": float(np.std(linearity_results)),
                "all_errors": [float(e) for e in linearity_results]
            }
        }

        results_path = output_dir / "composition_results.json"
        with open(results_path, 'w') as f:
            json.dump(final_results, f, indent=2)
        print(f"\nSaved results: {results_path}")

        return final_results

    def _plot_strategy_comparison(
        self,
        summary: Dict,
        output_dir: Path
    ):
        """Plot strategy comparison"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        strategies = list(summary.keys())
        errors = [summary[s]["mean_error"] for s in strategies]
        error_stds = [summary[s]["std_error"] for s in strategies]

        # Sort by error
        sorted_indices = np.argsort(errors)
        strategies = [strategies[i] for i in sorted_indices]
        errors = [errors[i] for i in sorted_indices]
        error_stds = [error_stds[i] for i in sorted_indices]

        # Error plot
        ax1.bar(range(len(strategies)), errors, yerr=error_stds, capsize=5, alpha=0.7)
        ax1.set_xticks(range(len(strategies)))
        ax1.set_xticklabels(strategies, rotation=45, ha='right')
        ax1.set_ylabel('Mean Reconstruction Error')
        ax1.set_title('Composition Strategy Comparison\n(Lower is Better)')
        ax1.grid(axis='y', alpha=0.3)

        # Performance plot
        performances = [summary[s]["mean_performance"] for s in strategies]
        perf_stds = [summary[s]["std_performance"] for s in strategies]

        ax2.bar(range(len(strategies)), performances, yerr=perf_stds, capsize=5, alpha=0.7)
        ax2.set_xticks(range(len(strategies)))
        ax2.set_xticklabels(strategies, rotation=45, ha='right')
        ax2.set_ylabel('Mean Performance')
        ax2.set_title('Performance by Strategy\n(Higher is Better)')
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "strategy_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_linearity_analysis(
        self,
        linearity_errors: List[float],
        output_dir: Path
    ):
        """Plot linearity analysis"""
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(linearity_errors, bins=20, alpha=0.7, edgecolor='black')
        ax.axvline(np.mean(linearity_errors), color='red', linestyle='--',
                   label=f'Mean: {np.mean(linearity_errors):.6f}')
        ax.set_xlabel('Normalized Linearity Error')
        ax.set_ylabel('Frequency')
        ax.set_title('Composition Linearity Error Distribution')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "linearity_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Run composition optimization analysis"""
    import scipy.stats

    optimizer = CompositionOptimizer(
        base_dim=512,
        lambda_reg=0.01
    )

    results = optimizer.run_full_analysis()

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
