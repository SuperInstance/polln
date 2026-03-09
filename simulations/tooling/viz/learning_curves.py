"""
POLLN Learning Curves Visualizer
================================

Plot learning progress, TD(λ) convergence, VAE loss, and value predictions.

Features:
- Publication-quality plots (PNG, PDF)
- Compare different configurations
- Multi-metric overlays
- Confidence intervals
- Learning rate analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
from dataclasses import dataclass, asdict
import pandas as pd
from scipy.interpolate import make_interp_spline
from scipy.signal import savgol_filter
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from base import EvolutionMetrics, EvolutionConfig


@dataclass
class LearningMetrics:
    """Metrics tracked during learning."""
    timestep: int
    episode: int

    # Value network metrics
    value_prediction: float
    value_error: float
    td_error: float

    # VAE/World Model metrics
    reconstruction_loss: float
    kl_divergence: float
    total_vae_loss: float

    # Agent performance
    reward: float
    success_rate: float
    avg_latency: float

    # Graph evolution metrics
    num_edges: int
    avg_weight: float
    sparsity: float

    # Optional metadata
    config_id: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass
class CurveStyle:
    """Styling configuration for learning curves."""
    line_width: float = 2.0
    alpha: float = 0.8
    marker_size: int = 4
    smooth_window: int = 10
    show_confidence: bool = True
    confidence_alpha: float = 0.2
    color_palette: str = "husl"


class LearningCurveVisualizer:
    """
    Visualize learning progress with publication-quality plots.

    Supports:
    - TD(λ) learning curves
    - VAE loss convergence
    - Value prediction accuracy
    - Multi-run comparisons
    - Confidence intervals
    """

    def __init__(self, style: Optional[CurveStyle] = None):
        self.style = style or CurveStyle()

        # Set up plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10

        # Data storage
        self.metrics_history: List[LearningMetrics] = []
        self.comparison_data: Dict[str, List[LearningMetrics]] = {}

    def add_metrics(self, metrics: LearningMetrics):
        """Add metrics point."""
        self.metrics_history.append(metrics)

    def add_comparison_run(self, config_id: str, metrics: List[LearningMetrics]):
        """Add a comparison run."""
        self.comparison_data[config_id] = metrics

    def _smooth_curve(self, y: np.ndarray, window: Optional[int] = None) -> np.ndarray:
        """Apply smoothing to curve."""
        window = window or self.style.smooth_window
        if len(y) < window:
            return y
        return savgol_filter(y, window, 3)

    def _compute_confidence_interval(self, values: List[float],
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Compute confidence interval."""
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        n = len(arr)

        # Standard error
        se = std / np.sqrt(n)

        # Confidence interval (using t-distribution)
        from scipy import stats
        t_val = stats.t.ppf((1 + confidence) / 2, n - 1)
        margin = t_val * se

        return (mean - margin, mean + margin)

    def plot_td_learning(self, output_path: Optional[Path] = None,
                        show_smoothed: bool = True,
                        show_td_error: bool = True) -> plt.Figure:
        """
        Plot TD(λ) learning curve.

        Shows value predictions and TD errors over time.
        """
        if not self.metrics_history:
            raise ValueError("No metrics data available")

        fig, axes = plt.subplots(2, 1, figsize=(12, 8),
                                gridspec_kw={'height_ratios': [2, 1]})

        # Extract data
        timesteps = [m.timestep for m in self.metrics_history]
        values = [m.value_prediction for m in self.metrics_history]
        td_errors = [m.td_error for m in self.metrics_history]

        # Plot value predictions
        ax1 = axes[0]
        ax1.plot(timesteps, values, 'o-',
                label='Raw Values',
                alpha=0.5,
                markersize=self.style.marker_size,
                color='steelblue')

        if show_smoothed:
            smoothed = self._smooth_curve(np.array(values))
            ax1.plot(timesteps, smoothed,
                    label='Smoothed',
                    linewidth=self.style.line_width,
                    color='darkblue')

        ax1.set_ylabel('Predicted Value')
        ax1.set_title('TD(λ) Value Learning')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot TD errors
        if show_td_error:
            ax2 = axes[1]
            ax2.plot(timesteps, td_errors,
                    'o-',
                    label='TD Error',
                    alpha=0.7,
                    markersize=self.style.marker_size,
                    color='coral')

            if show_smoothed:
                smoothed_errors = self._smooth_curve(np.array(td_errors))
                ax2.plot(timesteps, smoothed_errors,
                        label='Smoothed',
                        linewidth=self.style.line_width,
                        color='darkred')

            ax2.set_ylabel('TD Error')
            ax2.set_xlabel('Timestep')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_yscale('log')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved TD learning curve to {output_path}")

        return fig

    def plot_vae_loss(self, output_path: Optional[Path] = None,
                     show_components: bool = True) -> plt.Figure:
        """
        Plot VAE loss curves.

        Shows reconstruction loss, KL divergence, and total loss.
        """
        if not self.metrics_history:
            raise ValueError("No metrics data available")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract data
        timesteps = [m.timestep for m in self.metrics_history]
        recon_losses = [m.reconstruction_loss for m in self.metrics_history]
        kl_divs = [m.kl_divergence for m in self.metrics_history]
        total_losses = [m.total_vae_loss for m in self.metrics_history]

        # Plot total loss
        ax.plot(timesteps, total_losses,
               label='Total Loss',
               linewidth=self.style.line_width + 1,
               color='black',
               alpha=self.style.alpha)

        # Plot components
        if show_components:
            ax.plot(timesteps, recon_losses,
                   label='Reconstruction Loss',
                   linewidth=self.style.line_width,
                   color='blue',
                   alpha=self.style.alpha)

            ax.plot(timesteps, kl_divs,
                   label='KL Divergence',
                   linewidth=self.style.line_width,
                   color='red',
                   alpha=self.style.alpha)

        ax.set_xlabel('Timestep')
        ax.set_ylabel('Loss')
        ax.set_title('VAE Training Loss')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add annotation for convergence
        if len(total_losses) > 100:
            # Check if converged (last 10% variance < 5% of total variance)
            recent = total_losses[-len(total_losses)//10:]
            if np.std(recent) < 0.05 * np.std(total_losses):
                ax.annotate('Converged',
                           xy=(timesteps[-1], total_losses[-1]),
                           xytext=(timesteps[-len(timesteps)//4], total_losses[-1] * 1.5),
                           arrowprops=dict(arrowstyle='->', color='green'),
                           fontsize=12,
                           color='green',
                           fontweight='bold')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved VAE loss curve to {output_path}")

        return fig

    def plot_performance_metrics(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot agent performance metrics.

        Shows rewards, success rate, and latency.
        """
        if not self.metrics_history:
            raise ValueError("No metrics data available")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

        # Extract data
        timesteps = [m.timestep for m in self.metrics_history]
        rewards = [m.reward for m in self.metrics_history]
        success_rates = [m.success_rate for m in self.metrics_history]
        latencies = [m.avg_latency for m in self.metrics_history]

        # Plot rewards
        axes[0].plot(timesteps, rewards,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='green',
                    alpha=self.style.alpha)
        axes[0].set_ylabel('Reward')
        axes[0].set_title('Agent Performance Metrics')
        axes[0].grid(True, alpha=0.3)

        # Plot success rate
        axes[1].plot(timesteps, success_rates,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='purple',
                    alpha=self.style.alpha)
        axes[1].set_ylabel('Success Rate')
        axes[1].set_ylim(0, 1)
        axes[1].grid(True, alpha=0.3)

        # Plot latency
        axes[2].plot(timesteps, latencies,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='orange',
                    alpha=self.style.alpha)
        axes[2].set_ylabel('Avg Latency (ms)')
        axes[2].set_xlabel('Timestep')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved performance metrics to {output_path}")

        return fig

    def plot_graph_evolution_metrics(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Plot graph evolution metrics.

        Shows number of edges, average weight, and sparsity.
        """
        if not self.metrics_history:
            raise ValueError("No metrics data available")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

        # Extract data
        timesteps = [m.timestep for m in self.metrics_history]
        num_edges = [m.num_edges for m in self.metrics_history]
        avg_weights = [m.avg_weight for m in self.metrics_history]
        sparsities = [m.sparsity for m in self.metrics_history]

        # Plot number of edges
        axes[0].plot(timesteps, num_edges,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='steelblue',
                    alpha=self.style.alpha)
        axes[0].set_ylabel('Number of Edges')
        axes[0].set_title('Graph Evolution Metrics')
        axes[0].grid(True, alpha=0.3)

        # Plot average weight
        axes[1].plot(timesteps, avg_weights,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='darkorange',
                    alpha=self.style.alpha)
        axes[1].set_ylabel('Average Weight')
        axes[1].grid(True, alpha=0.3)

        # Plot sparsity
        axes[2].plot(timesteps, sparsities,
                    'o-',
                    linewidth=self.style.line_width,
                    markersize=self.style.marker_size,
                    color='darkgreen',
                    alpha=self.style.alpha)
        axes[2].set_ylabel('Sparsity')
        axes[2].set_xlabel('Timestep')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved graph evolution metrics to {output_path}")

        return fig

    def plot_comparison(self, metric: str,
                       output_path: Optional[Path] = None,
                       show_confidence: bool = True) -> plt.Figure:
        """
        Compare multiple configurations.

        Args:
            metric: Metric to compare ('value_error', 'total_vae_loss', etc.)
            output_path: Path to save figure
            show_confidence: Whether to show confidence intervals
        """
        if not self.comparison_data:
            raise ValueError("No comparison data available")

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = sns.color_palette(self.style.color_palette,
                                   len(self.comparison_data))

        for idx, (config_id, metrics) in enumerate(self.comparison_data.items()):
            # Extract metric values grouped by timestep
            metric_by_timestep: Dict[int, List[float]] = {}

            for m in metrics:
                if m.timestep not in metric_by_timestep:
                    metric_by_timestep[m.timestep] = []
                metric_by_timestep[m.timestep].append(getattr(m, metric))

            # Compute mean and confidence interval
            timesteps = sorted(metric_by_timestep.keys())
            means = [np.mean(metric_by_timestep[t]) for t in timesteps]

            ax.plot(timesteps, means,
                   label=config_id,
                   linewidth=self.style.line_width,
                   color=colors[idx],
                   alpha=self.style.alpha)

            if show_confidence and self.style.show_confidence:
                lower_bounds = []
                upper_bounds = []

                for t in timesteps:
                    values = metric_by_timestep[t]
                    lower, upper = self._compute_confidence_interval(values)
                    lower_bounds.append(lower)
                    upper_bounds.append(upper)

                ax.fill_between(timesteps,
                               lower_bounds,
                               upper_bounds,
                               color=colors[idx],
                               alpha=self.style.confidence_alpha)

        ax.set_xlabel('Timestep')
        ax.set_ylabel(metric.replace('_', ' ').title())
        ax.set_title(f'Configuration Comparison: {metric}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved comparison plot to {output_path}")

        return fig

    def plot_learning_summary(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Create comprehensive learning summary dashboard.

        Combines multiple metrics in a single figure.
        """
        if not self.metrics_history:
            raise ValueError("No metrics data available")

        fig = plt.figure(figsize=(16, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # Extract data
        timesteps = [m.timestep for m in self.metrics_history]
        values = [m.value_prediction for m in self.metrics_history]
        td_errors = [m.td_error for m in self.metrics_history]
        rewards = [m.reward for m in self.metrics_history]
        success_rates = [m.success_rate for m in self.metrics_history]

        # TD Learning (top row, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(timesteps, values, 'o-', alpha=0.5, markersize=3, color='steelblue')
        ax1.plot(timesteps, self._smooth_curve(np.array(values)),
                linewidth=2, color='darkblue', label='Value')
        ax1.set_ylabel('Predicted Value')
        ax1.set_title('TD(λ) Learning')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # TD Error (top row, last column)
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.plot(timesteps, td_errors, 'o-', alpha=0.5, markersize=3, color='coral')
        ax2.plot(timesteps, self._smooth_curve(np.array(td_errors)),
                linewidth=2, color='darkred')
        ax2.set_ylabel('TD Error')
        ax2.set_title('TD Error (log scale)')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)

        # Performance metrics (middle row)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(timesteps, rewards, 'o-', linewidth=2, markersize=3, color='green')
        ax3.set_ylabel('Reward')
        ax3.set_title('Cumulative Reward')
        ax3.grid(True, alpha=0.3)

        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(timesteps, success_rates, 'o-', linewidth=2, markersize=3, color='purple')
        ax4.set_ylabel('Success Rate')
        ax4.set_title('Success Rate')
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)

        # Learning statistics (middle row, right column)
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('off')

        # Compute statistics
        final_value = values[-1] if values else 0
        value_improvement = values[-1] - values[0] if len(values) > 1 else 0
        final_success_rate = success_rates[-1] if success_rates else 0
        total_reward = sum(rewards) if rewards else 0

        stats_text = f"""
        Learning Statistics

        Final Value: {final_value:.3f}
        Value Improvement: {value_improvement:.3f}
        Final Success Rate: {final_success_rate:.1%}
        Total Reward: {total_reward:.1f}

        Timesteps: {len(timesteps)}
        """

        ax5.text(0.1, 0.5, stats_text,
                fontsize=11,
                verticalalignment='center',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # VAE Loss (bottom row, spans 2 columns)
        ax6 = fig.add_subplot(gs[2, :2])
        recon_losses = [m.reconstruction_loss for m in self.metrics_history]
        kl_divs = [m.kl_divergence for m in self.metrics_history]
        total_losses = [m.total_vae_loss for m in self.metrics_history]

        ax6.plot(timesteps, total_losses, linewidth=3, color='black', alpha=0.7, label='Total')
        ax6.plot(timesteps, recon_losses, linewidth=2, color='blue', alpha=0.7, label='Reconstruction')
        ax6.plot(timesteps, kl_divs, linewidth=2, color='red', alpha=0.7, label='KL')
        ax6.set_ylabel('Loss')
        ax6.set_xlabel('Timestep')
        ax6.set_title('VAE Loss')
        ax6.legend()
        ax6.grid(True, alpha=0.3)

        # Graph metrics (bottom row, last column)
        ax7 = fig.add_subplot(gs[2, 2])
        num_edges = [m.num_edges for m in self.metrics_history]
        ax7.plot(timesteps, num_edges, 'o-', linewidth=2, markersize=3, color='steelblue')
        ax7.set_ylabel('Edges')
        ax7.set_xlabel('Timestep')
        ax7.set_title('Graph Size')
        ax7.grid(True, alpha=0.3)

        fig.suptitle('POLLN Learning Summary', fontsize=16, fontweight='bold')

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved learning summary to {output_path}")

        return fig

    def save_metrics_to_csv(self, output_path: Path):
        """Export metrics to CSV file."""
        data = [asdict(m) for m in self.metrics_history]
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Saved metrics to {output_path}")

    @classmethod
    def from_json(cls, filepath: Path) -> 'LearningCurveVisualizer':
        """Load metrics from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        visualizer = cls()

        for item in data['metrics']:
            metrics = LearningMetrics(**item)
            visualizer.add_metrics(metrics)

        return visualizer


def generate_learning_curves_demo(output_dir: Path):
    """Generate demo learning curves."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic learning data
    timesteps = list(range(0, 1000, 10))

    visualizer = LearningCurveVisualizer()

    for t in timesteps:
        # Simulate learning curves
        # Value: converges to ~0.8
        value = 0.8 * (1 - np.exp(-t / 200)) + np.random.normal(0, 0.05)

        # TD error: decreases over time
        td_error = 0.5 * np.exp(-t / 150) + np.random.normal(0, 0.02)

        # VAE losses: converge
        recon_loss = 0.3 * np.exp(-t / 100) + 0.1
        kl_div = 0.05 * np.exp(-t / 80)
        vae_loss = recon_loss + kl_div

        # Performance metrics
        reward = value * 10 + np.random.normal(0, 1)
        success_rate = np.clip(value + np.random.normal(0, 0.1), 0, 1)
        latency = 100 + 50 * np.exp(-t / 100) + np.random.normal(0, 10)

        # Graph metrics
        num_edges = int(50 + 30 * (1 - np.exp(-t / 150)))
        avg_weight = 0.5 + 0.3 * (1 - np.exp(-t / 200))
        sparsity = 1 - (num_edges / (20 * 19))

        metrics = LearningMetrics(
            timestep=t,
            episode=t // 100,
            value_prediction=value,
            value_error=abs(value - 0.8),
            td_error=abs(td_error),
            reconstruction_loss=recon_loss,
            kl_divergence=kl_div,
            total_vae_loss=vae_loss,
            reward=reward,
            success_rate=success_rate,
            avg_latency=latency,
            num_edges=num_edges,
            avg_weight=avg_weight,
            sparsity=sparsity
        )

        visualizer.add_metrics(metrics)

    # Generate all plots
    visualizer.plot_td_learning(output_dir / "td_learning.png")
    visualizer.plot_vae_loss(output_dir / "vae_loss.png")
    visualizer.plot_performance_metrics(output_dir / "performance_metrics.png")
    visualizer.plot_graph_evolution_metrics(output_dir / "graph_evolution_metrics.png")
    visualizer.plot_learning_summary(output_dir / "learning_summary.png")

    print(f"Generated demo learning curves in {output_dir}")


if __name__ == "__main__":
    # Generate demo
    output_dir = Path("../../reports/visualizations")
    generate_learning_curves_demo(output_dir)
