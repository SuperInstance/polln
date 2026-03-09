"""
Rank Sufficiency Analysis for LoRA Composition

Validates H1: Rank Decomposition
For expertise E: rank(W_E - W_base) ≤ r_min
Question: Is r_min ≈ 64 for most domains?

Measures:
- reconstruction_error = ||W_expert - (W_base + BA)||_F
- Spectral norm analysis
- Cumulative explained variance
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
import json


@dataclass
class RankAnalysisResult:
    """Results from rank sufficiency analysis"""
    rank: int
    reconstruction_error: float
    spectral_error: float
    explained_variance: float
    frobenius_norm_ratio: float
    compression_ratio: float


class SyntheticModelGenerator:
    """Generate synthetic model weights for different expertise domains"""

    def __init__(self, base_dim: int = 4096, seed: int = 42):
        self.base_dim = base_dim
        self.rng = np.random.RandomState(seed)

    def generate_base_model(self) -> torch.Tensor:
        """Generate frozen base model weights"""
        # Base model: roughly low-rank structure
        W_base = torch.randn(self.base_dim, self.base_dim) * 0.02
        # Add some structure
        for i in range(5):
            u = torch.randn(self.base_dim, 1)
            v = torch.randn(1, self.base_dim)
            W_base += 0.1 * (u @ v)

        return W_base

    def generate_expert_weights(
        self,
        base_weights: torch.Tensor,
        domain: str,
        expertise_strength: float = 0.3
    ) -> torch.Tensor:
        """
        Generate expert model weights by perturbing base model

        Domains:
        - code: Structured, sparse perturbations
        - writing: Smooth, dense perturbations
        - analysis: Mid-rank perturbations
        - research: High-rank, complex perturbations
        """
        W_expert = base_weights.clone()
        dim = self.base_dim

        if domain == "code":
            # Code expertise: Structured, low-rank changes
            # Localized patterns, syntax trees
            rank_perturb = 8
            for i in range(rank_perturb):
                u = torch.randn(dim, 1) * 0.1
                v = torch.randn(1, dim) * 0.1
                W_expert += expertise_strength * (u @ v)

        elif domain == "writing":
            # Writing expertise: Smooth, semi-local patterns
            # Attention pattern shifts
            for i in range(20):
                u = torch.randn(dim, 1) * 0.05
                v = torch.randn(1, dim) * 0.05
                W_expert += expertise_strength * 0.5 * (u @ v)

        elif domain == "analysis":
            # Analysis expertise: Mid-rank reasoning patterns
            rank_perturb = 32
            for i in range(rank_perturb):
                u = torch.randn(dim, 1) * 0.08
                v = torch.randn(1, dim) * 0.08
                W_expert += expertise_strength * 0.7 * (u @ v)

        elif domain == "research":
            # Research expertise: High-rank, complex patterns
            # Cross-domain connections
            rank_perturb = 64
            for i in range(rank_perturb):
                u = torch.randn(dim, 1) * 0.06
                v = torch.randn(1, dim) * 0.06
                W_expert += expertise_strength * 0.8 * (u @ v)

        return W_expert


class LoRADecomposer:
    """Decompose expertise difference into low-rank LoRA matrices"""

    def __init__(self, rank: int):
        self.rank = rank

    def decompose(
        self,
        W_base: torch.Tensor,
        W_expert: torch.Tensor,
        method: str = "svd"
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Decompose ΔW = W_expert - W_base into B @ A

        Methods:
        - svd: Optimal SVD decomposition
        - random: Random projection (for comparison)
        - nystrom: Nyström approximation (faster)
        """
        delta_W = W_expert - W_base

        if method == "svd":
            # Optimal low-rank approximation via SVD
            U, S, V = torch.linalg.svd(delta_W)
            B = U[:, :self.rank] @ torch.diag(S[:self.rank])
            A = V[:, :self.rank].T
            return B, A

        elif method == "random":
            # Random projection (baseline)
            A = torch.randn(self.rank, delta_W.shape[1]) * 0.01
            # Solve for B: minimize ||delta_W - BA||²
            B = delta_W @ A.T @ torch.inverse(A @ A.T)
            return B, A

        elif method == "nystrom":
            # Nyström method (faster approximation)
            k = self.rank
            # Sample columns
            indices = torch.randperm(delta_W.shape[1])[:k]
            W_k = delta_W[:, indices]
            # Solve
            C = delta_W @ delta_W[:, indices].T
            W_k_pinv = torch.pinverse(W_k)
            B = C @ W_k_pinv.T
            A = delta_W[:, indices].T
            return B, A

        else:
            raise ValueError(f"Unknown decomposition method: {method}")

    def reconstruct(self, B: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
        """Reconstruct ΔW from LoRA matrices"""
        return B @ A


class RankSufficiencyAnalyzer:
    """
    Analyze rank sufficiency for LoRA decomposition

    Validates: What rank r is needed to capture expertise?
    """

    def __init__(
        self,
        base_dim: int = 4096,
        max_rank: int = 256,
        domains: List[str] = None
    ):
        self.base_dim = base_dim
        self.max_rank = max_rank
        self.domains = domains or ["code", "writing", "analysis", "research"]

        self.model_gen = SyntheticModelGenerator(base_dim)
        self.W_base = self.model_gen.generate_base_model()

        # Store results
        self.results: Dict[str, List[RankAnalysisResult]] = {}

    def analyze_domain(
        self,
        domain: str,
        ranks: List[int] = None,
        expertise_strength: float = 0.3,
        method: str = "svd"
    ) -> List[RankAnalysisResult]:
        """
        Analyze rank sufficiency for a specific domain

        Returns reconstruction errors for each rank
        """
        if ranks is None:
            ranks = list(range(1, self.max_rank + 1, 4))

        # Generate expert weights
        W_expert = self.model_gen.generate_expert_weights(
            self.W_base, domain, expertise_strength
        )

        # Ground truth: actual rank of perturbation
        delta_W = W_expert - self.W_base
        true_rank = torch.matrix_rank(delta_W).item()
        total_norm = torch.norm(delta_W, 'fro').item()

        results = []

        for rank in ranks:
            decomposer = LoRADecomposer(rank)
            B, A = decomposer.decompose(self.W_base, W_expert, method=method)
            delta_W_reconstructed = decomposer.reconstruct(B, A)

            # Metrics
            reconstruction_error = torch.norm(
                delta_W - delta_W_reconstructed, 'fro'
            ).item()

            spectral_error = torch.norm(
                delta_W - delta_W_reconstructed, 2
            ).item()

            # Explained variance
            explained_variance = 1.0 - (reconstruction_error ** 2) / (total_norm ** 2)

            # Compression ratio
            original_params = self.base_dim ** 2
            lora_params = 2 * rank * self.base_dim
            compression_ratio = original_params / lora_params

            results.append(RankAnalysisResult(
                rank=rank,
                reconstruction_error=reconstruction_error,
                spectral_error=spectral_error,
                explained_variance=explained_variance,
                frobenius_norm_ratio=reconstruction_error / total_norm,
                compression_ratio=compression_ratio
            ))

        self.results[domain] = results
        return results

    def find_sufficient_rank(
        self,
        domain: str,
        threshold: float = 0.95
    ) -> int:
        """
        Find minimum rank that captures threshold% of expertise

        threshold: Fraction of variance to explain (default 0.95)
        """
        if domain not in self.results:
            self.analyze_domain(domain)

        for result in self.results[domain]:
            if result.explained_variance >= threshold:
                return result.rank

        return self.max_rank

    def compute_spectral_decay(
        self,
        domain: str,
        expertise_strength: float = 0.3
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute singular value decay rate

        Returns: (singular_values, cumulative_variance)
        """
        W_expert = self.model_gen.generate_expert_weights(
            self.W_base, domain, expertise_strength
        )
        delta_W = W_expert - self.W_base

        # Full SVD
        U, S, V = torch.linalg.svd(delta_W)
        S_np = S.cpu().numpy()

        # Cumulative explained variance
        total_variance = np.sum(S_np ** 2)
        cumulative_variance = np.cumsum(S_np ** 2) / total_variance

        return S_np, cumulative_variance

    def generate_phase_diagram(
        self,
        output_path: Optional[Path] = None
    ) -> Dict[str, np.ndarray]:
        """
        Generate phase diagram: error vs rank for all domains

        Phase diagram shows:
        - X-axis: Rank
        - Y-axis: Reconstruction error (log scale)
        - Different lines for different domains
        """
        ranks = np.arange(1, self.max_rank + 1, 4)
        phase_diagram = {}

        for domain in self.domains:
            results = self.analyze_domain(domain, ranks.tolist())
            errors = [r.reconstruction_error for r in results]
            phase_diagram[domain] = np.array(errors)

        if output_path:
            self._plot_phase_diagram(phase_diagram, ranks, output_path)

        return phase_diagram

    def _plot_phase_diagram(
        self,
        phase_diagram: Dict[str, np.ndarray],
        ranks: np.ndarray,
        output_path: Path
    ):
        """Plot phase diagram"""
        plt.figure(figsize=(12, 8))

        for domain, errors in phase_diagram.items():
            plt.loglog(ranks, errors, 'o-', label=domain, linewidth=2)

        # Add theoretical scaling lines
        x_ref = np.array([ranks[0], ranks[-1]])
        plt.loglog(x_ref, errors[0] * (ranks[0] / x_ref), '--',
                   label='1/r scaling', alpha=0.5, color='gray')
        plt.loglog(x_ref, errors[0] * np.exp(-0.1 * (x_ref - ranks[0])), '--',
                   label='exp(-r) scaling', alpha=0.5, color='black')

        plt.xlabel('LoRA Rank r', fontsize=14)
        plt.ylabel('Reconstruction Error ||ΔW - BA||_F', fontsize=14)
        plt.title('Rank Sufficiency Phase Diagram\nLoRA Rank vs Reconstruction Error',
                  fontsize=16)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def run_full_analysis(
        self,
        output_dir: Path = Path("./simulations/lora/results")
    ) -> Dict:
        """
        Run complete rank sufficiency analysis

        Returns comprehensive results dictionary
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Analyze all domains
        print("Analyzing rank sufficiency across domains...")
        for domain in self.domains:
            print(f"  {domain}...")
            self.analyze_domain(domain)

        # 2. Find sufficient ranks
        print("\nFinding sufficient ranks (95% variance)...")
        sufficient_ranks = {}
        for domain in self.domains:
            rank = self.find_sufficient_rank(domain, threshold=0.95)
            sufficient_ranks[domain] = rank
            print(f"  {domain}: r_min = {rank}")

        # 3. Generate phase diagram
        print("\nGenerating phase diagram...")
        phase_diagram_path = output_dir / "phase_diagram.png"
        phase_diagram = self.generate_phase_diagram(phase_diagram_path)
        print(f"  Saved: {phase_diagram_path}")

        # 4. Compute spectral decays
        print("\nComputing spectral decay rates...")
        spectral_data = {}
        for domain in self.domains:
            S, cum_var = self.compute_spectral_decay(domain)
            spectral_data[domain] = {
                "singular_values": S.tolist(),
                "cumulative_variance": cum_var.tolist()
            }

        # 5. Save results
        results = {
            "sufficient_ranks": sufficient_ranks,
            "phase_diagram": {
                domain: errors.tolist()
                for domain, errors in phase_diagram.items()
            },
            "spectral_data": spectral_data,
            "detailed_results": {
                domain: [
                    {
                        "rank": r.rank,
                        "reconstruction_error": r.reconstruction_error,
                        "spectral_error": r.spectral_error,
                        "explained_variance": r.explained_variance,
                        "compression_ratio": r.compression_ratio
                    }
                    for r in results
                ]
                for domain, results in self.results.items()
            }
        }

        results_path = output_dir / "rank_analysis_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results: {results_path}")

        return results

    def test_hypothesis_h1(self) -> Dict[str, bool]:
        """
        Test Hypothesis H1: Rank Decomposition
        Is r_min ≈ 64 for most domains?

        Returns: {domain: is_r64_sufficient}
        """
        print("\nTesting Hypothesis H1: Rank Decomposition")
        print("=" * 60)

        results = {}
        for domain in self.domains:
            r_95 = self.find_sufficient_rank(domain, threshold=0.95)
            r_99 = self.find_sufficient_rank(domain, threshold=0.99)

            # Test if r=64 is sufficient
            sufficient_at_95 = r_95 <= 64
            sufficient_at_99 = r_99 <= 64

            results[domain] = {
                "r_95": r_95,
                "r_99": r_99,
                "sufficient_at_95": sufficient_at_95,
                "sufficient_at_99": sufficient_at_99,
                "h1_holds": sufficient_at_95  # Conservative test
            }

            print(f"\n{domain.upper()}:")
            print(f"  r_95 = {r_95}, r_99 = {r_99}")
            print(f"  H1 holds (r ≤ 64 for 95%): {sufficient_at_95}")

        # Overall assessment
        h1_overall = all(r["h1_holds"] for r in results.values())
        print(f"\n{'=' * 60}")
        print(f"OVERALL H1 VALIDATION: {h1_overall}")
        print(f"Rank r=64 is sufficient for 95% variance in all domains: {h1_overall}")

        return results


def main():
    """Run rank sufficiency analysis"""
    print("=" * 60)
    print("LoRA Rank Sufficiency Analysis")
    print("=" * 60)

    analyzer = RankSufficiencyAnalyzer(
        base_dim=1024,  # Smaller for faster testing
        max_rank=128,
        domains=["code", "writing", "analysis", "research"]
    )

    # Run full analysis
    results = analyzer.run_full_analysis()

    # Test hypothesis H1
    h1_results = analyzer.test_hypothesis_h1()

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
