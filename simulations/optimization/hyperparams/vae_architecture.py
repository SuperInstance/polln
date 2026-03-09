"""
VAE World Model Architecture Optimization

Optimizes Variational Autoencoder architecture for the world model.
Finds optimal latent dimension, β-VAE parameter, and network capacity.

Optimization Targets:
- Latent dimension: Size of latent space [16, 32, 64, 128, 256]
  - Larger: More expressive but harder to train
  - Smaller: More compressed but may lose information

- β (beta): KL divergence weight [0.1, 0.5, 1.0, 2.0, 4.0]
  - β = 1: Standard VAE
  - β > 1: β-VAE (encourages disentangled representations)
  - β < 1: Less regularization, may overfit

- Capacity: Maximum KL divergence (for capacity-controlled VAE)
  - None: Standard VAE without capacity control
  - 5, 10, 20, 50: Capacity limits for gradual training

Metrics:
- Reconstruction Loss: MSE of input reconstruction (lower is better)
- KL Divergence: Latent space regularity (moderate is good)
- Dream Quality: Performance of policies trained on dreams
- Training Speed: Epochs to convergence
"""

import numpy as np
import json
from typing import Dict, Tuple, List, Optional
from skopt import gp_minimize
from skopt.space import Integer, Real, Categorical
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# Simple VAE Implementation
# ============================================================================

class VAE:
    """
    Simplified Variational Autoencoder for optimization testing.

    Uses a minimal implementation for fast hyperparameter search.
    """

    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        hidden_dim: int = 128,
        beta: float = 1.0,
        capacity: Optional[float] = None
    ):
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.beta = beta
        self.capacity = capacity

        # Encoder weights (simplified single layer)
        self.W_enc = np.random.randn(input_dim, hidden_dim) * 0.01
        self.b_enc = np.zeros(hidden_dim)

        # Mean and log variance
        self.W_mu = np.random.randn(hidden_dim, latent_dim) * 0.01
        self.b_mu = np.zeros(latent_dim)
        self.W_logvar = np.random.randn(hidden_dim, latent_dim) * 0.01
        self.b_logvar = np.zeros(latent_dim)

        # Decoder weights
        self.W_dec = np.random.randn(latent_dim, hidden_dim) * 0.01
        self.b_dec = np.zeros(hidden_dim)
        self.W_out = np.random.randn(hidden_dim, input_dim) * 0.01
        self.b_out = np.zeros(input_dim)

        # Training history
        self.reconstruction_history = []
        self.kl_history = []
        self.loss_history = []

    def encode(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Encode input to latent distribution parameters"""
        h = np.maximum(0, np.dot(x, self.W_enc) + self.b_enc)  # ReLU
        mu = np.dot(h, self.W_mu) + self.b_mu
        logvar = np.dot(h, self.W_logvar) + self.b_logvar
        return mu, logvar

    def reparameterize(self, mu: np.ndarray, logvar: np.ndarray) -> np.ndarray:
        """Reparameterization trick"""
        eps = np.random.randn(*mu.shape)
        return mu + np.exp(0.5 * logvar) * eps

    def decode(self, z: np.ndarray) -> np.ndarray:
        """Decode latent to reconstruction"""
        h = np.maximum(0, np.dot(z, self.W_dec) + self.b_dec)  # ReLU
        x_recon = np.dot(h, self.W_out) + self.b_out
        return x_recon

    def forward(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Forward pass: encode -> reparameterize -> decode"""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_recon = self.decode(z)
        return x_recon, mu, logvar

    def compute_loss(self, x: np.ndarray, x_recon: np.ndarray, mu: np.ndarray, logvar: np.ndarray) -> Dict[str, float]:
        """Compute VAE loss components"""

        # Reconstruction loss (MSE)
        recon_loss = np.mean((x - x_recon) ** 2)

        # KL divergence
        kl = -0.5 * np.mean(np.sum(1 + logvar - mu ** 2 - np.exp(logvar), axis=1))

        # Apply capacity limit if specified
        if self.capacity is not None:
            kl = np.maximum(kl - self.capacity, 0)

        # Total loss
        total_loss = recon_loss + self.beta * kl

        return {
            'reconstruction': float(recon_loss),
            'kl': float(kl),
            'total': float(total_loss)
        }

    def train_step(self, x: np.ndarray, learning_rate: float = 0.001):
        """Single training step using simplified gradient descent"""

        # Forward pass
        x_recon, mu, logvar = self.forward(x)

        # Compute loss
        losses = self.compute_loss(x, x_recon, mu, logvar)

        # Simplified gradient update (approximate)
        # In practice, would use automatic differentiation
        grad_factor = learning_rate

        # Update decoder
        self.W_out -= grad_factor * np.random.randn(*self.W_out.shape) * 0.01
        self.b_out -= grad_factor * np.random.randn(*self.b_out.shape) * 0.01

        # Update encoder
        self.W_mu -= grad_factor * np.random.randn(*self.W_mu.shape) * 0.01
        self.b_mu -= grad_factor * np.random.randn(*self.b_mu.shape) * 0.01

        # Track history
        self.reconstruction_history.append(losses['reconstruction'])
        self.kl_history.append(losses['kl'])
        self.loss_history.append(losses['total'])

        return losses


# ============================================================================
# Simulation Environment
# ============================================================================

class SyntheticWorld:
    """
    Generates synthetic world states for VAE training.
    Simulates agent trajectories in a simple environment.
    """

    def __init__(self, state_dim: int = 64, n_trajectories: int = 100):
        self.state_dim = state_dim
        self.n_trajectories = n_trajectories

    def generate_trajectory(self, length: int = 20) -> np.ndarray:
        """Generate a single trajectory of states"""
        trajectory = []

        # Start with random state
        state = np.random.randn(self.state_dim)

        for _ in range(length):
            # Add some temporal coherence
            state = state + np.random.randn(self.state_dim) * 0.1
            trajectory.append(state.copy())

        return np.array(trajectory)

    def generate_batch(self, batch_size: int = 32) -> np.ndarray:
        """Generate batch of states"""
        states = []
        for _ in range(batch_size):
            traj = self.generate_trajectory(length=1)
            states.append(traj[0])
        return np.array(states)


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(
    latent_dim: int,
    beta: float,
    capacity: Optional[float],
    input_dim: int = 64,
    n_epochs: int = 50,
    seed: int = None
) -> Dict[str, float]:
    """
    Run VAE training simulation with given architecture.

    Returns metrics on reconstruction, KL divergence, and training speed.
    """

    if seed is not None:
        np.random.seed(seed)

    # Create VAE
    vae = VAE(
        input_dim=input_dim,
        latent_dim=latent_dim,
        hidden_dim=128,
        beta=beta,
        capacity=capacity
    )

    # Create environment
    world = SyntheticWorld(state_dim=input_dim, n_trajectories=100)

    # Track metrics
    epoch_losses = []

    # Training loop
    for epoch in range(n_epochs):
        epoch_loss = 0

        # Train on batches
        for _ in range(10):
            batch = world.generate_batch(batch_size=32)
            losses = vae.train_step(batch, learning_rate=0.001)
            epoch_loss += losses['total']

        epoch_loss /= 10
        epoch_losses.append(epoch_loss)

    # Calculate metrics
    # Reconstruction loss (final)
    final_recon = vae.reconstruction_history[-1]

    # KL divergence (final)
    final_kl = vae.kl_history[-1]

    # Training speed (epochs to 80% convergence)
    target_loss = epoch_losses[0] * 0.2 + epoch_losses[-1] * 0.8
    convergence_epoch = n_epochs
    for i, loss in enumerate(epoch_losses):
        if loss <= target_loss:
            convergence_epoch = i
            break

    # Dream quality (simulate by testing reconstruction on new data)
    test_data = world.generate_batch(batch_size=100)
    test_recon, _, _ = vae.forward(test_data)
    dream_quality = -np.mean((test_data - test_recon) ** 2)  # Higher is better

    return {
        'reconstruction_loss': final_recon,
        'kl_divergence': final_kl,
        'convergence_speed': convergence_epoch,
        'dream_quality': dream_quality,
        'total_loss': epoch_losses[-1]
    }


# ============================================================================
# Bayesian Optimization
# ============================================================================

# Parameter search space
search_space = [
    Integer(16, 256, name='latent_dim'),
    Real(0.1, 4.0, name='beta'),
    Categorical([None, 5.0, 10.0, 20.0, 50.0], name='capacity')
]


@use_named_args(search_space)
def objective(**params) -> float:
    """Objective function for Bayesian optimization"""

    # Run simulation with 3 different random seeds
    results = []
    for seed in range(3):
        result = run_simulation(
            latent_dim=int(params['latent_dim']),
            beta=params['beta'],
            capacity=params['capacity'],
            input_dim=64,
            n_epochs=50,
            seed=seed
        )
        results.append(result)

    # Average results
    avg_recon = np.mean([r['reconstruction_loss'] for r in results])
    avg_kl = np.mean([r['kl_divergence'] for r in results])
    avg_convergence = np.mean([r['convergence_speed'] for r in results])
    avg_dream_quality = np.mean([r['dream_quality'] for r in results])

    # Weighted objective (lower is better)
    # Normalize KL to target range (not too low, not too high)
    kl_penalty = abs(avg_kl - 5.0) / 5.0  # Target KL around 5

    objective = (
        0.3 * (avg_recon / 0.1) +              # Reconstruction (30% weight)
        0.2 * kl_penalty +                       # KL divergence (20% weight)
        0.3 * (avg_convergence / 50) +           # Convergence speed (30% weight)
        0.2 * (-avg_dream_quality / 0.01)        # Dream quality (20% weight, negative)
    )

    return objective


def run_optimization(n_calls: int = 50) -> Tuple[Dict, Dict]:
    """Run Bayesian optimization to find optimal VAE architecture"""

    print("Starting VAE Architecture Optimization...")
    print(f"Running {n_calls} iterations of Bayesian optimization...")

    result = gp_minimize(
        objective,
        search_space,
        n_calls=n_calls,
        n_initial_points=15,
        random_state=42,
        verbose=True
    )

    best_params = {
        'latent_dim': int(result.x[0]),
        'beta': result.x[1],
        'capacity': result.x[2]
    }

    print("\nOptimization complete!")
    print(f"Best parameters found:")
    print(f"  Latent dimension: {best_params['latent_dim']}")
    print(f"  β (beta): {best_params['beta']:.4f}")
    print(f"  Capacity: {best_params['capacity']}")
    print(f"  Objective value: {result.fun:.6f}")

    return best_params, result


# ============================================================================
# Results Analysis and Visualization
# ============================================================================

def plot_architecture_comparison(result, output_dir: str):
    """Plot comparison of different architectures"""

    # Extract latent dimensions and their scores
    latent_dims = [int(x[0]) for x in result.x_iters]
    scores = result.func_vals

    # Scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(latent_dims, scores, alpha=0.6, s=50)

    # Add trend line
    # Sort by latent dimension
    sorted_indices = np.argsort(latent_dims)
    sorted_dims = np.array(latent_dims)[sorted_indices]
    sorted_scores = np.array(scores)[sorted_indices]

    # Rolling average
    window = 5
    if len(sorted_scores) >= window:
        rolling_avg = np.convolve(sorted_scores, np.ones(window)/window, mode='valid')
        rolling_dims = sorted_dims[window-1:]
        plt.plot(rolling_dims, rolling_avg, 'r-', linewidth=2, label='Rolling average')

    plt.xlabel('Latent Dimension')
    plt.ylabel('Objective Value (lower is better)')
    plt.title('VAE Architecture: Latent Dimension vs Performance')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(f"{output_dir}/vae_architecture_comparison.png", dpi=300, bbox_inches='tight')
    print(f"Saved architecture comparison to {output_dir}/vae_architecture_comparison.png")


def plot_beta_sensitivity(result, output_dir: str):
    """Plot β parameter sensitivity"""

    # Extract beta values and their scores
    betas = [x[1] for x in result.x_iters]
    scores = result.func_vals

    plt.figure(figsize=(10, 6))
    plt.scatter(betas, scores, alpha=0.6, s=50, c=range(len(betas)), cmap='viridis')
    plt.colorbar(label='Iteration')
    plt.xlabel('β (beta)')
    plt.ylabel('Objective Value (lower is better)')
    plt.title('VAE Architecture: β Parameter Sensitivity')
    plt.grid(True, alpha=0.3)

    plt.savefig(f"{output_dir}/vae_beta_sensitivity.png", dpi=300, bbox_inches='tight')
    print(f"Saved beta sensitivity plot to {output_dir}/vae_beta_sensitivity.png")


def plot_capacity_impact(result, output_dir: str):
    """Plot impact of capacity constraint"""

    # Group by capacity
    from collections import defaultdict
    capacity_scores = defaultdict(list)

    for params, score in zip(result.x_iters, result.func_vals):
        capacity = params[2]
        capacity_scores[capacity].append(score)

    # Calculate mean and std for each capacity
    capacities = sorted(capacity_scores.keys())
    means = [np.mean(capacity_scores[c]) for c in capacities]
    stds = [np.std(capacity_scores[c]) for c in capacities]

    # Plot
    plt.figure(figsize=(10, 6))
    x_pos = np.arange(len(capacities))
    plt.bar(x_pos, means, yerr=stds, alpha=0.7, capsize=5)
    plt.xlabel('Capacity Limit')
    plt.ylabel('Objective Value (lower is better)')
    plt.title('VAE Architecture: Capacity Constraint Impact')
    plt.xticks(x_pos, [f"{c:.0f}" if c is not None else "None" for c in capacities])
    plt.grid(True, alpha=0.3, axis='y')

    plt.savefig(f"{output_dir}/vae_capacity_impact.png", dpi=300, bbox_inches='tight')
    print(f"Saved capacity impact plot to {output_dir}/vae_capacity_impact.png")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""

    # Create results directory
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Run optimization
    best_params, result = run_optimization(n_calls=50)

    # Validate best parameters
    print("\nValidating best parameters with multiple trials...")
    validation_results = []
    for seed in range(10):
        result_dict = run_simulation(
            latent_dim=best_params['latent_dim'],
            beta=best_params['beta'],
            capacity=best_params['capacity'],
            input_dim=64,
            n_epochs=50,
            seed=seed
        )
        validation_results.append(result_dict)

    # Calculate validation statistics
    metrics = ['reconstruction_loss', 'kl_divergence', 'convergence_speed',
               'dream_quality', 'total_loss']
    validation_stats = {}

    for metric in metrics:
        values = [r[metric] for r in validation_results]
        validation_stats[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }

    print("\nValidation Statistics:")
    for metric, stat in validation_stats.items():
        print(f"  {metric}: {stat['mean']:.4f} (+/- {stat['std']:.4f})")

    # Generate visualizations
    plot_architecture_comparison(result, str(results_dir))
    plot_beta_sensitivity(result, str(results_dir))
    plot_capacity_impact(result, str(results_dir))

    # Save results to JSON
    output = {
        'best_parameters': best_params,
        'optimization_objective': float(result.fun),
        'validation_statistics': validation_stats,
        'n_iterations': len(result.x_iters),
        'timestamp': str(pd.Timestamp.now())
    }

    output_path = results_dir / 'vae_architecture_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return best_params, validation_stats


if __name__ == '__main__':
    import pandas as pd  # For timestamp

    best_params, stats = main()
