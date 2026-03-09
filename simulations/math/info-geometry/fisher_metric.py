"""
Fisher Information Metric Analysis for POLLN

This module implements the Fisher-Rao metric for analyzing the information-
theoretic structure of POLLN's parameter spaces. The Fisher metric provides
a Riemannian metric on the statistical manifold of probability distributions.

Mathematical Foundation:
    g_ij(θ) = E_θ[∂_i log p(x|θ) ∂_j log p(x|θ)]
           = -E_θ[∂_i ∂_j log p(x|θ)]

where θ are parameters, and g_ij is the metric tensor.
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, Optional, Callable
from pathlib import Path
import json

from .deepseek_geometry import DeepSeekGeometer


class FisherMetricCalculator:
    """
    Compute Fisher information metric for neural network parameter spaces.

    The Fisher metric measures the amount of information that observable
    random variables carry about an unknown parameter θ.
    """

    def __init__(self, model: nn.Module, eps: float = 1e-8):
        """
        Initialize Fisher metric calculator.

        Args:
            model: Neural network model
            eps: Small constant for numerical stability
        """
        self.model = model
        self.eps = eps
        self.device = next(model.parameters()).device
        self.geometer = DeepSeekGeometer()

        # Get theoretical derivation from DeepSeek
        self.theory = self.geometer.get_fisher_metric_formulation()

    def get_fisher_matrix(self,
                         data_loader: torch.utils.data.DataLoader,
                         n_samples: int = 1000) -> torch.Tensor:
        """
        Compute empirical Fisher information matrix.

        Uses Monte Carlo estimation:
        F(θ) ≈ (1/N) Σ_i ∇_θ log p(y_i|x_i,θ) ∇_θ log p(y_i|x_i,θ)^T

        Args:
            data_loader: DataLoader with (x, y) pairs
            n_samples: Maximum number of samples to use

        Returns:
            Fisher information matrix F(θ)
        """
        self.model.eval()

        # Get gradients for each sample
        gradients = []
        n_params = sum(p.numel() for p in self.model.parameters())

        sample_count = 0
        for x, y in data_loader:
            if sample_count >= n_samples:
                break

            x, y = x.to(self.device), y.to(self.device)

            # Forward pass
            output = self.model(x)
            log_prob = torch.nn.functional.log_softmax(output, dim=-1)

            # Get gradient for each sample in batch
            for i in range(x.size(0)):
                if sample_count >= n_samples:
                    break

                # Compute gradient of log-likelihood
                log_likelihood = log_prob[i, y[i]]
                self.model.zero_grad()
                log_likelihood.backward(retain_graph=True)

                # Collect gradients
                grad = torch.cat([
                    p.grad.flatten().detach()
                    for p in self.model.parameters()
                    if p.grad is not None
                ])

                gradients.append(grad)
                sample_count += 1

        if not gradients:
            raise ValueError("No gradients computed. Check data loader.")

        # Stack gradients
        grad_matrix = torch.stack(gradients)  # (N, D)

        # Compute Fisher matrix
        fisher = torch.mm(grad_matrix.T, grad_matrix) / len(gradients)

        # Add small regularization
        fisher += self.eps * torch.eye(fisher.size(0), device=self.device)

        return fisher

    def get_fisher_diagonal(self,
                           data_loader: torch.utils.data.DataLoader,
                           n_samples: int = 1000) -> torch.Tensor:
        """
        Compute diagonal approximation of Fisher matrix (more scalable).

        F_ii(θ) ≈ (1/N) Σ_i (∂_i log p(y|x,θ))^2

        Args:
            data_loader: DataLoader with (x, y) pairs
            n_samples: Maximum number of samples

        Returns:
            Diagonal of Fisher information matrix
        """
        self.model.eval()

        # Accumulate squared gradients
        fisher_diag = None
        sample_count = 0

        for x, y in data_loader:
            if sample_count >= n_samples:
                break

            x, y = x.to(self.device), y.to(self.device)

            output = self.model(x)
            log_prob = torch.nn.functional.log_softmax(output, dim=-1)

            for i in range(x.size(0)):
                if sample_count >= n_samples:
                    break

                log_likelihood = log_prob[i, y[i]]
                self.model.zero_grad()
                log_likelihood.backward(retain_graph=True)

                # Get squared gradients
                if fisher_diag is None:
                    fisher_diag = torch.cat([
                        p.grad.flatten() ** 2
                        for p in self.model.parameters()
                        if p.grad is not None
                    ])
                else:
                    fisher_diag += torch.cat([
                        p.grad.flatten() ** 2
                        for p in self.model.parameters()
                        if p.grad is not None
                    ])

                sample_count += 1

        # Average and add regularization
        fisher_diag = fisher_diag / sample_count + self.eps

        return fisher_diag

    def get_kfisher_blocks(self,
                          data_loader: torch.utils.data.DataLoader,
                          n_samples: int = 1000,
                          block_size: int = 100) -> torch.Tensor:
        """
        Compute block-diagonal approximation of Fisher matrix.

        More accurate than diagonal but more scalable than full matrix.

        Args:
            data_loader: DataLoader
            n_samples: Maximum samples
            block_size: Size of blocks

        Returns:
            Block-diagonal Fisher matrix
        """
        full_fisher = self.get_fisher_matrix(data_loader, n_samples)

        # Zero out off-block elements
        n_params = full_fisher.size(0)
        block_fisher = full_fisher.clone()

        for i in range(n_params):
            block_start = (i // block_size) * block_size
            block_end = block_start + block_size

            for j in range(n_params):
                if not (block_start <= j < block_end):
                    block_fisher[i, j] = 0.0

        return block_fisher

    def get_eigenvalues(self, fisher: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute eigenvalues and eigenvectors of Fisher matrix.

        Eigenvalues λ_i represent the information content in each
        principal direction of parameter space.

        Args:
            fisher: Fisher information matrix

        Returns:
            Tuple of (eigenvalues, eigenvectors)
        """
        eigenvalues, eigenvectors = torch.linalg.eigh(fisher)

        # Sort by eigenvalue magnitude
        sorted_indices = torch.argsort(eigenvalues, descending=True)
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices]

        return eigenvalues, eigenvectors

    def get_curvature(self,
                     fisher: torch.Tensor,
                     metric_derivative: Optional[torch.Tensor] = None) -> Dict[str, float]:
        """
        Compute Riemannian curvature quantities from Fisher metric.

        For diagonal metric g_ii, Gaussian curvature:
        K = -1/(2√g) ∂_i ∂_j (g_ii / √g)

        Args:
            fisher: Fisher metric tensor
            metric_derivative: Derivative of metric (optional)

        Returns:
            Dictionary with curvature measures
        """
        # For now, compute scalar curvature for diagonal metric
        if metric_derivative is None:
            # Use finite difference approximation
            return self._compute_curvature_finite_difference(fisher)

        # Full curvature computation
        n = fisher.size(0)

        # Compute Christoffel symbols: Γ^k_ij = (1/2) g^kl (∂_i g_jl + ∂_j g_il - ∂_l g_ij)
        g_inv = torch.inverse(fisher + self.eps * torch.eye(n, device=fisher.device))

        christoffel = torch.zeros(n, n, n, device=fisher.device)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    for l in range(n):
                        term = (metric_derivative[i, j, l] +
                               metric_derivative[j, i, l] -
                               metric_derivative[l, i, j])
                        christoffel[k, i, j] += 0.5 * g_inv[k, l] * term

        # Compute Riemann curvature tensor: R^l_ijk = ∂_j Γ^l_ik - ∂_k Γ^l_ij + Γ^l_jm Γ^m_ik - Γ^l_km Γ^m_ij
        # This is complex; for now return placeholder
        return {
            "ricci_scalar": 0.0,
            "gaussian_curvature": 0.0,
            "note": "Full curvature computation requires metric derivatives"
        }

    def _compute_curvature_finite_difference(self,
                                           fisher: torch.Tensor) -> Dict[str, float]:
        """
        Compute curvature using finite difference approximation.

        Args:
            fisher: Fisher metric tensor

        Returns:
            Dictionary with approximate curvature measures
        """
        # Extract diagonal
        diag = torch.diag(fisher)

        # Scalar curvature approximation
        # R ~ -Σ_i ∂^2/∂θ_i^2 log(λ_i)
        log_eigenvalues = torch.log(torch.abs(diag) + self.eps)
        laplacian = torch.gradient(log_eigenvalues)[0]
        laplacian = torch.gradient(laplacian)[0]

        scalar_curvature = -torch.sum(laplacian).item()

        return {
            "ricci_scalar": scalar_curvature,
            "log_determinant": torch.logdet(fisher + self.eps * torch.eye(fisher.size(0))).item(),
            "condition_number": (torch.max(diag) / (torch.min(diag) + self.eps)).item(),
            "effective_dimension": (torch.sum(diag > self.eps)).item()
        }

    def geodesic_distance(self,
                         fisher: torch.Tensor,
                         theta1: torch.Tensor,
                         theta2: torch.Tensor) -> float:
        """
        Compute Riemannian geodesic distance between two parameter vectors.

        d(θ1, θ2)^2 = (θ1 - θ2)^T F(θ) (θ1 - θ2)

        For exact geodesics, need to solve geodesic ODE.

        Args:
            fisher: Fisher metric at a point
            theta1: First parameter vector
            theta2: Second parameter vector

        Returns:
            Geodesic distance
        """
        delta = theta1 - theta2
        distance_squared = torch.mm(delta.unsqueeze(0), torch.mm(fisher, delta.unsqueeze(1)))
        return torch.sqrt(distance_squared + self.eps).item()

    def cramér_rao_bound(self, fisher: torch.Tensor) -> torch.Tensor:
        """
        Compute Cramér-Rao lower bound.

        Var(θ̂) ≥ F(θ)^(-1)

        Any unbiased estimator has covariance at least the inverse Fisher information.

        Args:
            fisher: Fisher information matrix

        Returns:
            Cramér-Rao lower bound matrix
        """
        return torch.inverse(fisher + self.eps * torch.eye(fisher.size(0), device=fisher.device))

    def information_distance(self,
                            p1: torch.Tensor,
                            p2: torch.Tensor,
                            fisher: torch.Tensor) -> float:
        """
        Compute information distance (Rao distance).

        This is the geodesic distance on the statistical manifold.

        Args:
            p1: First probability distribution
            p2: Second probability distribution
            fisher: Fisher metric

        Returns:
            Information distance
        """
        # For multivariate normal, can compute analytically
        # For general case, use numerical integration
        delta = p1 - p2
        return torch.sqrt(torch.mm(delta.unsqueeze(0), torch.mm(fisher, delta.unsqueeze(1))) + self.eps).item()

    def analyze_landscape(self,
                         fisher: torch.Tensor,
                         eigenvalues: torch.Tensor) -> Dict[str, Any]:
        """
        Analyze the information geometry landscape.

        Args:
            fisher: Fisher information matrix
            eigenvalues: Eigenvalues of Fisher matrix

        Returns:
            Dictionary with landscape analysis
        """
        # Rank of Fisher matrix (effective dimensionality)
        rank = torch.sum(eigenvalues > self.eps).item()

        # Condition number (anisotropy)
        condition_number = (eigenvalues[0] / (eigenvalues[-1] + self.eps)).item()

        # Volume (determinant)
        volume = torch.exp(torch.logdet(fisher + self.eps * torch.eye(fisher.size(0)))).item()

        # Entropy (log determinant)
        entropy = torch.logdet(fisher + self.eps * torch.eye(fisher.size(0))).item()

        # Shannon information
        shannon_info = 0.5 * entropy

        return {
            "rank": rank,
            "full_dimension": fisher.size(0),
            "condition_number": condition_number,
            "volume": volume,
            "entropy": entropy,
            "shannon_information": shannon_info,
            "effective_rank_ratio": rank / fisher.size(0),
            "spectral_flatness": torch.exp(torch.mean(torch.log(eigenvalues + self.eps))).item() / torch.mean(eigenvalues).item()
        }

    def save_analysis(self, analysis: Dict[str, Any], output_path: Path):
        """
        Save analysis results to JSON.

        Args:
            analysis: Analysis results dictionary
            output_path: Path to save JSON
        """
        # Convert tensors to lists for JSON serialization
        serializable = {}
        for key, value in analysis.items():
            if isinstance(value, torch.Tensor):
                serializable[key] = value.tolist()
            elif isinstance(value, (np.ndarray, list)):
                serializable[key] = value
            else:
                serializable[key] = value

        with open(output_path, 'w') as f:
            json.dump(serializable, f, indent=2)

    def get_theoretical_background(self) -> str:
        """
        Get the theoretical background from DeepSeek.

        Returns:
            Markdown-formatted theory
        """
        return self.theory


class FisherInfoVisualizer:
    """Visualization tools for Fisher information analysis."""

    def __init__(self, save_dir: Optional[Path] = None):
        """
        Initialize visualizer.

        Args:
            save_dir: Directory to save plots
        """
        self.save_dir = save_dir or Path(__file__).parent / "visualizations"
        self.save_dir.mkdir(exist_ok=True)

    def plot_spectrum(self,
                     eigenvalues: torch.Tensor,
                     title: str = "Fisher Information Spectrum"):
        """
        Plot eigenvalue spectrum.

        Args:
            eigenvalues: Eigenvalues of Fisher matrix
            title: Plot title
        """
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.semilogy(range(len(eigenvalues)), eigenvalues.cpu().numpy(), 'b-', alpha=0.7)
        plt.xlabel('Eigenvalue Index')
        plt.ylabel('Eigenvalue (log scale)')
        plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        path = self.save_dir / "fisher_spectrum.png"
        plt.savefig(path, dpi=300)
        plt.close()

        return path

    def plot_heatmap(self,
                    fisher: torch.Tensor,
                    title: str = "Fisher Information Matrix"):
        """
        Plot Fisher matrix as heatmap.

        Args:
            fisher: Fisher information matrix
            title: Plot title
        """
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 10))
        plt.imshow(fisher.cpu().numpy(), cmap='viridis', aspect='auto')
        plt.colorbar(label='Fisher Information')
        plt.title(title)
        plt.xlabel('Parameter Index')
        plt.ylabel('Parameter Index')
        plt.tight_layout()

        path = self.save_dir / "fisher_heatmap.png"
        plt.savefig(path, dpi=300)
        plt.close()

        return path


def main():
    """Test Fisher metric calculation."""
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader

    # Create a simple model
    model = nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 10)
    )

    # Create synthetic data
    X = torch.randn(1000, 10)
    y = torch.randint(0, 10, (1000,))
    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Compute Fisher metric
    calculator = FisherMetricCalculator(model)

    print("Computing Fisher information matrix...")
    fisher = calculator.get_fisher_diagonal(loader, n_samples=100)

    print(f"Fisher diagonal shape: {fisher.shape}")
    print(f"Fisher stats: mean={fisher.mean():.6f}, std={fisher.std():.6f}")

    # Analyze landscape
    eigenvalues, eigenvectors = calculator.get_eigenvalues(torch.diag(fisher))
    analysis = calculator.analyze_landscape(torch.diag(fisher), eigenvalues)

    print("\nLandscape Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")

    # Get theoretical background
    print("\n" + "="*70)
    print("THEORETICAL BACKGROUND (from DeepSeek):")
    print("="*70)
    print(calculator.get_theoretical_background()[:1000] + "...")


if __name__ == "__main__":
    main()
