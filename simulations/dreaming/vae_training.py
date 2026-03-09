"""
VAE Training Simulation
=======================

Proves that VAE learns compact representations sufficient for dreaming.

Mathematical Foundation:
    Encoder: z ~ q_φ(z|x) = N(μ_φ(x), σ_φ²(x))
    Decoder: x ~ p_θ(x|z) = N(μ_θ(z), σ_θ²(z))
    Loss: L = ||x - x_reconstructed||² + β·KL(q(z|x) || p(z))

Key Hypotheses:
    H1: Reconstruction loss decreases with training
    H2: KL divergence stays bounded (no collapse)
    H3: Optimal latent dimension exists for each MDP
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple, Dict, List
import matplotlib.pyplot as plt
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class VAEConfig:
    """Configuration for VAE training"""
    input_dim: int = 64
    hidden_dim: int = 256
    latent_dim: int = 64
    beta: float = 0.1  # KL divergence weight
    learning_rate: float = 1e-3
    batch_size: int = 32
    epochs: int = 100


class VAE(nn.Module):
    """
    Variational Autoencoder for learning compact state representations.

    Architecture:
        Encoder: input -> hidden -> (mean, log_var)
        Decoder: latent -> hidden -> output
    """

    def __init__(self, config: VAEConfig):
        super().__init__()
        self.config = config

        # Encoder: q(z|x)
        self.encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.ReLU(),
        )

        self.fc_mean = nn.Linear(config.hidden_dim, config.latent_dim)
        self.fc_logvar = nn.Linear(config.hidden_dim, config.latent_dim)

        # Decoder: p(x|z)
        self.decoder = nn.Sequential(
            nn.Linear(config.latent_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.input_dim),
            nn.Tanh(),  # Normalize to [-1, 1]
        )

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode observation to latent distribution.

        Args:
            x: Input observation [batch, input_dim]

        Returns:
            mean, log_var: Latent distribution parameters
        """
        h = self.encoder(x)
        mean = self.fc_mean(h)
        log_var = self.fc_logvar(h)
        return mean, log_var

    def reparameterize(self, mean: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        """
        Reparameterization trick: z = μ + σ·ε where ε ~ N(0, I)

        Args:
            mean: Latent mean [batch, latent_dim]
            log_var: Latent log variance [batch, latent_dim]

        Returns:
            z: Sampled latent vector
        """
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mean + eps * std

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decode latent to observation.

        Args:
            z: Latent vector [batch, latent_dim]

        Returns:
            x_recon: Reconstructed observation
        """
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through VAE.

        Args:
            x: Input observation

        Returns:
            x_recon, mean, log_var
        """
        mean, log_var = self.encode(x)
        z = self.reparameterize(mean, log_var)
        x_recon = self.decode(z)
        return x_recon, mean, log_var

    def loss_function(
        self,
        x: torch.Tensor,
        x_recon: torch.Tensor,
        mean: torch.Tensor,
        log_var: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute VAE loss: L = reconstruction + β * KL

        Args:
            x: Original input
            x_recon: Reconstructed input
            mean: Latent mean
            log_var: Latent log variance

        Returns:
            total_loss, reconstruction_loss, kl_loss
        """
        # Reconstruction loss (MSE)
        recon_loss = F.mse_loss(x_recon, x, reduction='mean')

        # KL divergence: KL(q(z|x) || p(z)) where p(z) = N(0, I)
        # KL = -0.5 * Σ(1 + log(σ²) - μ² - σ²)
        kl_loss = -0.5 * torch.sum(1 + log_var - mean.pow(2) - log_var.exp())
        kl_loss = kl_loss / x.size(0)  # Average over batch

        # Total loss
        total_loss = recon_loss + self.config.beta * kl_loss

        return total_loss, recon_loss, kl_loss


class MDPTrajectoryCollector:
    """
    Collect trajectories from MDPs for VAE training.

    Simulates simple grid-world and cartpole-like environments.
    """

    @staticmethod
    def collect_gridworld_trajectories(
        num_trajectories: int = 1000,
        trajectory_length: int = 50,
        grid_size: int = 8
    ) -> np.ndarray:
        """
        Collect trajectories from grid world.

        State: [x, y, goal_x, goal_y, obstacles...] normalized
        """
        trajectories = []

        for _ in range(num_trajectories):
            # Random start and goal
            start_x = np.random.randint(0, grid_size)
            start_y = np.random.randint(0, grid_size)
            goal_x = np.random.randint(0, grid_size)
            goal_y = np.random.randint(0, grid_size)

            x, y = start_x, start_y

            for _ in range(trajectory_length):
                # State representation
                state = np.zeros(64)
                state[0] = x / grid_size
                state[1] = y / grid_size
                state[2] = goal_x / grid_size
                state[3] = goal_y / grid_size

                # Random action (up, down, left, right)
                action = np.random.randint(4)
                if action == 0 and x < grid_size - 1:
                    x += 1
                elif action == 1 and x > 0:
                    x -= 1
                elif action == 2 and y < grid_size - 1:
                    y += 1
                elif action == 3 and y > 0:
                    y -= 1

                trajectories.append(state)

        return np.array(trajectories)

    @staticmethod
    def collect_cartpole_trajectories(
        num_trajectories: int = 1000,
        trajectory_length: int = 50
    ) -> np.ndarray:
        """
        Collect trajectories from CartPole-like dynamics.

        State: [x, x_dot, theta, theta_dot, ...] normalized
        """
        trajectories = []

        for _ in range(num_trajectories):
            # Random initial state
            x = np.random.uniform(-2.4, 2.4)
            x_dot = np.random.uniform(-1, 1)
            theta = np.random.uniform(-0.2, 0.2)
            theta_dot = np.random.uniform(-1, 1)

            for _ in range(trajectory_length):
                # State representation
                state = np.zeros(64)
                state[0] = x / 2.4
                state[1] = x_dot
                state[2] = theta / 0.2
                state[3] = theta_dot

                # Simple physics update (random action)
                action = np.random.choice([-1, 1])
                force = action * 10
                x_dot += force * 0.02 - x * 0.1
                x += x_dot * 0.02
                theta_dot += (x * 0.1 + force * 0.01) * 0.02
                theta += theta_dot * 0.02

                # Clip
                x = np.clip(x, -2.4, 2.4)
                theta = np.clip(theta, -0.2, 0.2)

                trajectories.append(state)

        return np.array(trajectories)


class VAETrainer:
    """
    Train VAE on MDP trajectories and analyze latent space.
    """

    def __init__(self, config: VAEConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = VAE(config).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate)

        # Training history
        self.history = {
            'train_loss': [],
            'recon_loss': [],
            'kl_loss': [],
        }

    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        epoch_losses = {'total': 0, 'recon': 0, 'kl': 0}

        for batch in dataloader:
            x = batch[0].to(self.device)

            # Forward pass
            x_recon, mean, log_var = self.model(x)

            # Compute loss
            total_loss, recon_loss, kl_loss = self.model.loss_function(x, x_recon, mean, log_var)

            # Backward pass
            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()

            epoch_losses['total'] += total_loss.item()
            epoch_losses['recon'] += recon_loss.item()
            epoch_losses['kl'] += kl_loss.item()

        # Average over batches
        num_batches = len(dataloader)
        return {
            'total_loss': epoch_losses['total'] / num_batches,
            'recon_loss': epoch_losses['recon'] / num_batches,
            'kl_loss': epoch_losses['kl'] / num_batches,
        }

    def train(
        self,
        train_data: np.ndarray,
        val_data: np.ndarray = None,
        verbose: bool = True
    ) -> Dict[str, List[float]]:
        """
        Train VAE on trajectory data.

        Args:
            train_data: Training trajectories [N, input_dim]
            val_data: Validation trajectories
            verbose: Print progress

        Returns:
            Training history
        """
        # Create dataloaders
        train_dataset = TensorDataset(
            torch.FloatTensor(train_data)
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True
        )

        # Validation
        val_loader = None
        if val_data is not None:
            val_dataset = TensorDataset(torch.FloatTensor(val_data))
            val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size)

        # Training loop
        for epoch in range(self.config.epochs):
            # Train
            train_metrics = self.train_epoch(train_loader)

            # Validate
            if val_loader is not None:
                val_metrics = self.evaluate(val_loader)
            else:
                val_metrics = {}

            # Record history
            self.history['train_loss'].append(train_metrics['total_loss'])
            self.history['recon_loss'].append(train_metrics['recon_loss'])
            self.history['kl_loss'].append(train_metrics['kl_loss'])

            # Print progress
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{self.config.epochs}")
                print(f"  Train Loss: {train_metrics['total_loss']:.4f}")
                print(f"  Recon Loss: {train_metrics['recon_loss']:.4f}")
                print(f"  KL Loss: {train_metrics['kl_loss']:.4f}")
                if val_metrics:
                    print(f"  Val Loss: {val_metrics['total_loss']:.4f}")

        return self.history

    def evaluate(self, dataloader: DataLoader) -> Dict[str, float]:
        """Evaluate on validation data"""
        self.model.eval()
        epoch_losses = {'total': 0, 'recon': 0, 'kl': 0}

        with torch.no_grad():
            for batch in dataloader:
                x = batch[0].to(self.device)
                x_recon, mean, log_var = self.model(x)
                total_loss, recon_loss, kl_loss = self.model.loss_function(
                    x, x_recon, mean, log_var
                )

                epoch_losses['total'] += total_loss.item()
                epoch_losses['recon'] += recon_loss.item()
                epoch_losses['kl'] += kl_loss.item()

        num_batches = len(dataloader)
        return {
            'total_loss': epoch_losses['total'] / num_batches,
            'recon_loss': epoch_losses['recon'] / num_batches,
            'kl_loss': epoch_losses['kl'] / num_batches,
        }

    def analyze_latent_space(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Analyze latent space properties.

        Returns:
            Dictionary with latent statistics
        """
        self.model.eval()
        dataset = TensorDataset(torch.FloatTensor(data))
        loader = DataLoader(dataset, batch_size=32, shuffle=False)

        all_means = []
        all_log_vars = []
        all_latents = []

        with torch.no_grad():
            for batch in loader:
                x = batch[0].to(self.device)
                mean, log_var = self.model.encode(x)
                z = self.model.reparameterize(mean, log_var)

                all_means.append(mean.cpu().numpy())
                all_log_vars.append(log_var.cpu().numpy())
                all_latents.append(z.cpu().numpy())

        all_means = np.concatenate(all_means, axis=0)
        all_log_vars = np.concatenate(all_log_vars, axis=0)
        all_latents = np.concatenate(all_latents, axis=0)

        return {
            'means': all_means,
            'log_vars': all_log_vars,
            'latents': all_latents,
            'mean_mean': np.mean(all_means, axis=0),
            'mean_std': np.std(all_means, axis=0),
            'mean_log_var': np.mean(all_log_vars, axis=0),
        }


def run_latent_dimension_experiment():
    """
    Experiment: Find optimal latent dimension for different MDPs.

    Hypothesis: Each MDP has a minimum sufficient latent dimension.
    """
    print("=" * 60)
    print("H1: Latent Sufficiency Experiment")
    print("=" * 60)

    latent_dims = [8, 16, 32, 64, 128, 256]
    results = {
        'gridworld': [],
        'cartpole': [],
    }

    # Collect data
    print("\nCollecting trajectories...")
    gridworld_data = MDPTrajectoryCollector.collect_gridworld_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )
    cartpole_data = MDPTrajectoryCollector.collect_cartpole_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )

    # Train VAE with different latent dimensions
    for latent_dim in latent_dims:
        print(f"\n{'=' * 60}")
        print(f"Training with latent_dim = {latent_dim}")
        print(f"{'=' * 60}")

        # GridWorld
        print("\nGridWorld:")
        config = VAEConfig(latent_dim=latent_dim, epochs=50, beta=0.1)
        trainer = VAETrainer(config)
        history = trainer.train(gridworld_data, verbose=False)

        final_loss = history['train_loss'][-1]
        final_kl = history['kl_loss'][-1]
        results['gridworld'].append({
            'latent_dim': latent_dim,
            'final_loss': final_loss,
            'final_kl': final_kl,
        })
        print(f"  Final Loss: {final_loss:.4f}, KL: {final_kl:.4f}")

        # CartPole
        print("\nCartPole:")
        config = VAEConfig(latent_dim=latent_dim, epochs=50, beta=0.1)
        trainer = VAETrainer(config)
        history = trainer.train(cartpole_data, verbose=False)

        final_loss = history['train_loss'][-1]
        final_kl = history['kl_loss'][-1]
        results['cartpole'].append({
            'latent_dim': latent_dim,
            'final_loss': final_loss,
            'final_kl': final_kl,
        })
        print(f"  Final Loss: {final_loss:.4f}, KL: {final_kl:.4f}")

    # Find optimal dimensions
    print("\n" + "=" * 60)
    print("Results: Optimal Latent Dimensions")
    print("=" * 60)

    for env_name, env_results in results.items():
        # Find elbow point (dim where improvement plateaus)
        losses = [r['final_loss'] for r in env_results]
        improvements = [losses[i] - losses[i+1] for i in range(len(losses)-1)]

        # Optimal is where improvement < 10% of initial improvement
        initial_improvement = improvements[0]
        optimal_idx = 0
        for i, imp in enumerate(improvements):
            if imp < 0.1 * initial_improvement:
                optimal_idx = i
                break

        optimal_dim = latent_dims[optimal_idx]
        print(f"\n{env_name.upper()}:")
        print(f"  Optimal Latent Dim: {optimal_dim}")
        print(f"  Final Loss at optimal: {losses[optimal_idx]:.4f}")

    return results


def run_beta_experiment():
    """
    Experiment: Effect of KL weight (β) on VAE training.

    Hypothesis: Optimal β balances reconstruction and KL.
    """
    print("\n" + "=" * 60)
    print("H2: KL Weight (β) Experiment")
    print("=" * 60)

    betas = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
    results = []

    # Collect data
    gridworld_data = MDPTrajectoryCollector.collect_gridworld_trajectories(
        num_trajectories=500,
        trajectory_length=50
    )

    for beta in betas:
        print(f"\nTraining with β = {beta}")
        config = VAEConfig(latent_dim=64, epochs=50, beta=beta)
        trainer = VAETrainer(config)
        history = trainer.train(gridworld_data, verbose=False)

        final_recon = history['recon_loss'][-1]
        final_kl = history['kl_loss'][-1]
        final_total = history['train_loss'][-1]

        results.append({
            'beta': beta,
            'recon_loss': final_recon,
            'kl_loss': final_kl,
            'total_loss': final_total,
        })

        print(f"  Recon: {final_recon:.4f}, KL: {final_kl:.4f}, Total: {final_total:.4f}")

    # Find optimal beta
    print("\n" + "=" * 60)
    print("Results: Optimal β")
    print("=" * 60)

    best_beta = min(results, key=lambda x: x['total_loss'])
    print(f"\nOptimal β: {best_beta['beta']}")
    print(f"  Recon Loss: {best_beta['recon_loss']:.4f}")
    print(f"  KL Loss: {best_beta['kl_loss']:.4f}")
    print(f"  Total Loss: {best_beta['total_loss']:.4f}")

    return results


def plot_results(results: Dict, save_path: str = None):
    """Plot training results"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Latent dimension experiment
    if 'gridworld' in results:
        ax = axes[0, 0]
        latent_dims = [r['latent_dim'] for r in results['gridworld']]
        losses_grid = [r['final_loss'] for r in results['gridworld']]
        losses_cart = [r['final_loss'] for r in results['cartpole']]

        ax.plot(latent_dims, losses_grid, 'o-', label='GridWorld')
        ax.plot(latent_dims, losses_cart, 's-', label='CartPole')
        ax.set_xlabel('Latent Dimension')
        ax.set_ylabel('Final Loss')
        ax.set_title('H1: Latent Sufficiency')
        ax.legend()
        ax.set_xscale('log')
        ax.set_yscale('log')

    # Beta experiment
    if len(results) > 0 and 'beta' in results[0]:
        ax = axes[0, 1]
        betas = [r['beta'] for r in results]
        recon_losses = [r['recon_loss'] for r in results]
        kl_losses = [r['kl_loss'] for r in results]

        ax.plot(betas, recon_losses, 'o-', label='Reconstruction')
        ax.plot(betas, kl_losses, 's-', label='KL')
        ax.set_xlabel('β (KL Weight)')
        ax.set_ylabel('Loss')
        ax.set_title('H2: KL Weight Effect')
        ax.legend()
        ax.set_xscale('log')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"\nPlot saved to {save_path}")

    plt.show()


def main():
    """Run all VAE training experiments"""
    print("=" * 60)
    print("VAE TRAINING SIMULATIONS")
    print("Proving VAE learns compact representations for dreaming")
    print("=" * 60)

    # Run experiments
    latent_results = run_latent_dimension_experiment()
    beta_results = run_beta_experiment()

    # Save results
    output_dir = Path("C:/Users/casey/polln/simulations/dreaming/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "vae_latent_dim_results.json", 'w') as f:
        json.dump(latent_results, f, indent=2)

    with open(output_dir / "vae_beta_results.json", 'w') as f:
        json.dump(beta_results, f, indent=2)

    print("\n" + "=" * 60)
    print("Results saved to simulations/dreaming/results/")
    print("=" * 60)

    # Plot
    plot_results(latent_results, save_path=output_dir / "vae_training_plots.png")

    return latent_results, beta_results


if __name__ == "__main__":
    main()
