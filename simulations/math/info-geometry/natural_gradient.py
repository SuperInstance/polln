"""
Natural Gradient Descent Implementation

This module implements Amari's natural gradient descent, which uses the
Fisher information matrix to precondition the gradient, following the
geometry of the information manifold.

Key Idea:
    θ_{t+1} = θ_t - α F(θ_t)^{-1} ∇L(θ_t)

where F(θ) is the Fisher information matrix. This performs gradient
descent in the Riemannian manifold of probability distributions.
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Optional, Dict, Any, Tuple, Callable
from pathlib import Path
import json
import time

from .fisher_metric import FisherMetricCalculator
from .deepseek_geometry import DeepSeekGeometer


class NaturalGradientOptimizer:
    """
    Natural gradient descent optimizer using Fisher information.

    Natural gradient accounts for the geometry of the parameter space
    by using the Fisher metric to measure distance.
    """

    def __init__(self,
                 model: nn.Module,
                 lr: float = 1e-3,
                 fisher_mode: str = "diagonal",
                 eps: float = 1e-8,
                 update_frequency: int = 100):
        """
        Initialize natural gradient optimizer.

        Args:
            model: Neural network model
            lr: Learning rate
            fisher_mode: How to approximate Fisher ('diagonal', 'block', 'full')
            eps: Damping factor for matrix inversion
            update_frequency: How often to update Fisher estimate
        """
        self.model = model
        self.lr = lr
        self.fisher_mode = fisher_mode
        self.eps = eps
        self.update_frequency = update_frequency

        self.device = next(model.parameters()).device
        self.fisher_calculator = FisherMetricCalculator(model, eps=eps)
        self.geometer = DeepSeekGeometer()

        # Fisher matrix estimate
        self.fisher_estimate = None
        self.fisher_inv_estimate = None

        # Training statistics
        self.step_count = 0
        self.fisher_update_count = 0

        # Get theoretical derivation
        self.theory = self.geometer.get_natural_gradient_formulation()

    def compute_fisher(self, data_loader: DataLoader, n_samples: int = 1000):
        """
        Compute and update Fisher information matrix.

        Args:
            data_loader: Data for Fisher computation
            n_samples: Number of samples for estimation
        """
        print(f"Updating Fisher estimate (mode: {self.fisher_mode})...")

        if self.fisher_mode == "diagonal":
            self.fisher_estimate = self.fisher_calculator.get_fisher_diagonal(
                data_loader, n_samples
            )
            self.fisher_inv_estimate = 1.0 / (self.fisher_estimate + self.eps)

        elif self.fisher_mode == "full":
            fisher = self.fisher_calculator.get_fisher_matrix(data_loader, n_samples)
            self.fisher_estimate = fisher
            # Use Cholesky for stable inversion
            L = torch.linalg.cholesky(fisher + self.eps * torch.eye(fisher.size(0), device=self.device))
            self.fisher_inv_estimate = torch.cholesky_inverse(L)

        self.fisher_update_count += 1

    def step(self, loss: torch.Tensor):
        """
        Perform one natural gradient step.

        Args:
            loss: Loss tensor (already computed)
        """
        # Compute vanilla gradient
        loss.backward()

        # Update Fisher if needed
        if self.step_count % self.update_frequency == 0:
            # Note: In practice, you'd pass data_loader here
            # For now, skip if we don't have one
            pass

        # Apply natural gradient preconditioning
        if self.fisher_inv_estimate is not None:
            with torch.no_grad():
                for i, param in enumerate(param for param in self.model.parameters()
                                          if param.grad is not None):
                    flat_grad = param.grad.flatten()

                    if self.fisher_mode == "diagonal":
                        # Diagonal preconditioning
                        start_idx = sum(p.numel() for p in self.model.parameters() if p.grad is None
                                      or p is param and list(self.model.parameters()).index(p) < i)
                        end_idx = start_idx + param.numel()

                        preconditioned_grad = flat_grad * self.fisher_inv_estimate[start_idx:end_idx]
                        param.grad = preconditioned_grad.reshape(param.grad.shape)

                    elif self.fisher_mode == "full":
                        # Full preconditioning (more expensive)
                        start_idx = sum(p.numel() for p in self.model.parameters() if p.grad is None
                                      or p is param and list(self.model.parameters()).index(p) < i)
                        end_idx = start_idx + param.numel()

                        fisher_inv_block = self.fisher_inv_estimate[start_idx:end_idx, start_idx:end_idx]
                        preconditioned_grad = torch.mm(fisher_inv_block, flat_grad.unsqueeze(1)).squeeze()
                        param.grad = preconditioned_grad.reshape(param.grad.shape)

        # Update parameters
        with torch.no_grad():
            for param in self.model.parameters():
                if param.grad is not None:
                    param -= self.lr * param.grad

        self.step_count += 1

    def zero_grad(self):
        """Zero out gradients."""
        self.model.zero_grad()


class VanillaGradientOptimizer:
    """Standard vanilla gradient descent for comparison."""

    def __init__(self, model: nn.Module, lr: float = 1e-3):
        """
        Initialize vanilla optimizer.

        Args:
            model: Neural network model
            lr: Learning rate
        """
        self.model = model
        self.lr = lr
        self.step_count = 0

    def step(self, loss: torch.Tensor):
        """Perform vanilla gradient step."""
        loss.backward()

        with torch.no_grad():
            for param in self.model.parameters():
                if param.grad is not None:
                    param -= self.lr * param.grad

        self.step_count += 1

    def zero_grad(self):
        """Zero out gradients."""
        self.model.zero_grad()


def compare_optimizers(model_fn: Callable,
                      data_loader: DataLoader,
                      test_loader: DataLoader,
                      n_epochs: int = 10,
                      lr: float = 1e-3) -> Dict[str, Any]:
    """
    Compare natural gradient vs vanilla gradient descent.

    Args:
        model_fn: Function that creates a fresh model
        data_loader: Training data
        test_loader: Test data
        n_epochs: Number of training epochs
        lr: Learning rate

    Returns:
        Dictionary with comparison results
    """
    results = {
        "vanilla": {"losses": [], "times": [], "test_accuracies": []},
        "natural": {"losses": [], "times": [], "test_accuracies": []}
    }

    # Train with vanilla gradient
    print("\nTraining with vanilla gradient descent...")
    model_vanilla = model_fn()
    optimizer_vanilla = VanillaGradientOptimizer(model_vanilla, lr=lr)

    for epoch in range(n_epochs):
        epoch_start = time.time()
        epoch_loss = 0.0

        for x, y in data_loader:
            optimizer_vanilla.zero_grad()

            output = model_vanilla(x)
            loss = nn.CrossEntropyLoss()(output, y)

            epoch_loss += loss.item()
            optimizer_vanilla.step(loss)

        epoch_time = time.time() - epoch_start
        avg_loss = epoch_loss / len(data_loader)

        # Test accuracy
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in test_loader:
                output = model_vanilla(x)
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        accuracy = correct / total

        results["vanilla"]["losses"].append(avg_loss)
        results["vanilla"]["times"].append(epoch_time)
        results["vanilla"]["test_accuracies"].append(accuracy)

        print(f"Epoch {epoch+1}/{n_epochs}: loss={avg_loss:.4f}, acc={accuracy:.4f}, time={epoch_time:.2f}s")

    # Train with natural gradient
    print("\nTraining with natural gradient descent...")
    model_natural = model_fn()
    optimizer_natural = NaturalGradientOptimizer(model_natural, lr=lr, fisher_mode="diagonal")

    # Initialize Fisher
    optimizer_natural.compute_fisher(data_loader, n_samples=500)

    for epoch in range(n_epochs):
        epoch_start = time.time()
        epoch_loss = 0.0

        for x, y in data_loader:
            optimizer_natural.zero_grad()

            output = model_natural(x)
            loss = nn.CrossEntropyLoss()(output, y)

            epoch_loss += loss.item()
            optimizer_natural.step(loss)

        epoch_time = time.time() - epoch_start
        avg_loss = epoch_loss / len(data_loader)

        # Test accuracy
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in test_loader:
                output = model_natural(x)
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        accuracy = correct / total

        results["natural"]["losses"].append(avg_loss)
        results["natural"]["times"].append(epoch_time)
        results["natural"]["test_accuracies"].append(accuracy)

        print(f"Epoch {epoch+1}/{n_epochs}: loss={avg_loss:.4f}, acc={accuracy:.4f}, time={epoch_time:.2f}s")

        # Update Fisher periodically
        if (epoch + 1) % 5 == 0:
            optimizer_natural.compute_fisher(data_loader, n_samples=500)

    return results


def analyze_convergence(results: Dict[str, Any]) -> Dict[str, float]:
    """
    Analyze convergence rates of different optimizers.

    Args:
        results: Results from compare_optimizers

    Returns:
        Dictionary with convergence analysis
    """
    analysis = {}

    for optimizer_name, opt_results in results.items():
        losses = np.array(opt_results["losses"])

        # Fit exponential decay: L(t) ≈ L₀ * exp(-λt)
        # log L(t) = log L₀ - λt
        log_losses = np.log(losses + 1e-10)
        t = np.arange(len(losses))

        # Linear regression
        coeffs = np.polyfit(t, log_losses, 1)
        convergence_rate = -coeffs[0]  # λ

        # Final performance
        final_loss = losses[-1]
        final_accuracy = opt_results["test_accuracies"][-1]

        # Total training time
        total_time = sum(opt_results["times"])

        analysis[optimizer_name] = {
            "convergence_rate": convergence_rate,
            "final_loss": final_loss,
            "final_accuracy": final_accuracy,
            "total_time": total_time
        }

    # Compute speedup
    if "vanilla" in analysis and "natural" in analysis:
        vanilla_time = analysis["vanilla"]["total_time"]
        natural_time = analysis["natural"]["total_time"]
        analysis["speedup_factor"] = vanilla_time / natural_time

        vanilla_acc = analysis["vanilla"]["final_accuracy"]
        natural_acc = analysis["natural"]["final_accuracy"]
        analysis["accuracy_improvement"] = natural_acc - vanilla_acc

    return analysis


class PreconditioningAnalyzer:
    """Analyze the preconditioning matrix and its effects."""

    def __init__(self, fisher: torch.Tensor):
        """
        Initialize analyzer.

        Args:
            fisher: Fisher information matrix
        """
        self.fisher = fisher

    def get_preconditioning_matrix(self) -> torch.Tensor:
        """
        Get the preconditioning matrix F^{-1}.

        Returns:
            Inverse Fisher matrix (or diagonal approximation)
        """
        if self.fisher.dim() == 1:
            # Diagonal approximation
            return 1.0 / (self.fisher + 1e-8)
        else:
            # Full matrix
            return torch.inverse(self.fisher + 1e-8 * torch.eye(self.fisher.size(0)))

    def analyze_effectiveness(self,
                            gradient: torch.Tensor) -> Dict[str, float]:
        """
        Analyze how preconditioning affects gradient.

        Args:
            gradient: Vanilla gradient vector

        Returns:
            Dictionary with analysis
        """
        prec = self.get_preconditioning_matrix()

        # Compute preconditioned gradient
        if self.fisher.dim() == 1:
            natural_grad = gradient * prec
        else:
            natural_grad = torch.mm(prec, gradient.unsqueeze(1)).squeeze()

        # Compare magnitudes
        vanilla_norm = torch.norm(gradient).item()
        natural_norm = torch.norm(natural_grad).item()

        # Angle between gradients
        cosine_similarity = torch.dot(gradient, natural_grad) / (vanilla_norm * natural_norm + 1e-10)
        angle = torch.acos(torch.clamp(cosine_similarity, -1.0, 1.0)).item()

        # Directional statistics
        vanilla_flattened = gradient.flatten()
        natural_flattened = natural_grad.flatten()

        return {
            "vanilla_norm": vanilla_norm,
            "natural_norm": natural_norm,
            "norm_ratio": natural_norm / vanilla_norm,
            "cosine_similarity": cosine_similarity.item(),
            "angle_degrees": angle * 180 / np.pi,
            "vanilla_std": vanilla_flattened.std().item(),
            "natural_std": natural_flattened.std().item()
        }

    def visualize_preconditioning(self, save_path: Optional[Path] = None):
        """
        Visualize the preconditioning matrix.

        Args:
            save_path: Path to save plot
        """
        import matplotlib.pyplot as plt

        prec = self.get_preconditioning_matrix()

        if prec.dim() == 1:
            # Diagonal case: plot values
            plt.figure(figsize=(12, 6))
            plt.plot(prec.cpu().numpy())
            plt.xlabel('Parameter Index')
            plt.ylabel('Preconditioning Value')
            plt.title('Diagonal Natural Gradient Preconditioning')
            plt.grid(True, alpha=0.3)
        else:
            # Full matrix: heatmap
            plt.figure(figsize=(12, 10))
            plt.imshow(prec.cpu().numpy(), cmap='RdBu_r', aspect='auto')
            plt.colorbar(label='Preconditioning Value')
            plt.title('Natural Gradient Preconditioning Matrix')
            plt.xlabel('Parameter Index')
            plt.ylabel('Parameter Index')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
        else:
            plt.show()


def main():
    """Test natural gradient descent."""
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader

    # Create simple data
    torch.manual_seed(42)
    X_train = torch.randn(1000, 10)
    y_train = torch.randint(0, 2, (1000,))
    X_test = torch.randn(200, 10)
    y_test = torch.randint(0, 2, (200,))

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    def create_model():
        return nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 2)
        )

    # Compare optimizers
    results = compare_optimizers(
        model_fn=create_model,
        data_loader=train_loader,
        test_loader=test_loader,
        n_epochs=5,
        lr=1e-3
    )

    # Analyze convergence
    analysis = analyze_convergence(results)

    print("\n" + "="*70)
    print("CONVERGENCE ANALYSIS:")
    print("="*70)
    for opt_name, stats in analysis.items():
        if isinstance(stats, dict):
            print(f"\n{opt_name.upper()}:")
            for key, value in stats.items():
                print(f"  {key}: {value:.6f}")
        else:
            print(f"{opt_name}: {stats:.6f}")

    # Get theoretical background
    print("\n" + "="*70)
    print("THEORETICAL BACKGROUND (from DeepSeek):")
    print("="*70)
    optimizer = NaturalGradientOptimizer(create_model())
    print(optimizer.theory[:1000] + "...")


if __name__ == "__main__":
    main()
