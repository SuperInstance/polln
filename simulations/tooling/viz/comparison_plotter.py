"""
POLLN Comparison Plotter
========================

Compare multiple configurations, algorithms, and parameter settings.

Features:
- Grouped bar charts
- Heatmaps
- Radar charts
- Statistical comparison
- Publication-quality reports
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from scipy import stats
from sklearn.preprocessing import StandardScaler
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from base import EvolutionMetrics, EvolutionConfig


@dataclass
class ComparisonConfig:
    """Configuration for comparison run."""
    config_id: str
    display_name: str
    config: EvolutionConfig
    metrics: List[EvolutionMetrics]

    # Performance summary
    final_performance: float
    convergence_time: int
    stability_score: float


@dataclass
class StatisticalTest:
    """Result of statistical test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    effect_size: float


class ComparisonPlotter:
    """
    Create comparison visualizations for POLLN configurations.

    Generates:
    - Grouped bar charts
    - Heatmaps
    - Radar charts
    - Statistical comparisons
    """

    def __init__(self):
        self.comparisons: Dict[str, ComparisonConfig] = {}

        # Set up plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10

    def add_comparison(self, config: ComparisonConfig):
        """Add a configuration for comparison."""
        self.comparisons[config.config_id] = config

    def plot_grouped_bar_chart(self, metric: str,
                               output_path: Optional[Path] = None,
                               title: Optional[str] = None) -> plt.Figure:
        """
        Create grouped bar chart comparing configurations.

        Args:
            metric: Metric to compare (e.g., 'total_edges', 'clustering_coefficient')
            output_path: Path to save figure
            title: Custom title
        """
        if not self.comparisons:
            raise ValueError("No comparison data available")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract data
        config_ids = list(self.comparisons.keys())
        display_names = [self.comparisons[cid].display_name for cid in config_ids]

        # Get final values for each config
        values = []
        errors = []

        for cid in config_ids:
            config = self.comparisons[cid]
            metric_values = [getattr(m, metric) for m in config.metrics]

            values.append(np.mean(metric_values))
            errors.append(np.std(metric_values))

        # Create bar chart
        x = np.arange(len(config_ids))
        width = 0.6

        bars = ax.bar(x, values, width, yerr=errors,
                     capsize=5, alpha=0.8,
                     color=sns.color_palette("husl", len(config_ids)))

        # Add value labels
        for i, (bar, val, err) in enumerate(zip(bars, values, errors)):
            ax.text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + err,
                   f'{val:.3f}',
                   ha='center', va='bottom',
                   fontsize=9)

        ax.set_ylabel(metric.replace('_', ' ').title())
        ax.set_title(title or f'{metric.replace("_", " ").title()} Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(display_names, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved grouped bar chart to {output_path}")

        return fig

    def plot_heatmap(self, metrics: List[str],
                    output_path: Optional[Path] = None,
                    normalize: bool = True) -> plt.Figure:
        """
        Create heatmap comparing multiple metrics.

        Args:
            metrics: List of metrics to compare
            output_path: Path to save figure
            normalize: Whether to normalize values per row
        """
        if not self.comparisons:
            raise ValueError("No comparison data available")

        # Build data matrix
        config_ids = list(self.comparisons.keys())
        display_names = [self.comparisons[cid].display_name for cid in config_ids]

        data_matrix = []
        for cid in config_ids:
            config = self.comparisons[cid]
            row = []
            for metric in metrics:
                metric_values = [getattr(m, metric) for m in config.metrics]
                row.append(np.mean(metric_values))
            data_matrix.append(row)

        data_matrix = np.array(data_matrix)

        # Normalize if requested
        if normalize:
            scaler = StandardScaler()
            data_matrix = scaler.fit_transform(data_matrix)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(len(metrics)))
        ax.set_yticks(np.arange(len(config_ids)))
        ax.set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=0)
        ax.set_yticklabels(display_names)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Normalized Value' if normalize else 'Value')

        # Add text annotations
        for i in range(len(config_ids)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{data_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=9)

        ax.set_title('POLLN Configuration Comparison Heatmap',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved heatmap to {output_path}")

        return fig

    def plot_radar_chart(self, metrics: List[str],
                        output_path: Optional[Path] = None) -> plt.Figure:
        """
        Create radar chart comparing configurations.

        Args:
            metrics: List of metrics to compare
            output_path: Path to save figure
        """
        if not self.comparisons:
            raise ValueError("No comparison data available")

        # Number of variables
        num_vars = len(metrics)

        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]  # Complete the circle

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Plot each configuration
        colors = sns.color_palette("husl", len(self.comparisons))

        for idx, (cid, config) in enumerate(self.comparisons.items()):
            # Get values
            values = []
            for metric in metrics:
                metric_values = [getattr(m, metric) for m in config.metrics]
                values.append(np.mean(metric_values))

            # Normalize to 0-1 range
            values = np.array(values)
            min_val = values.min()
            max_val = values.max()
            if max_val > min_val:
                values = (values - min_val) / (max_val - min_val)

            # Complete the circle
            values = list(values) + [values[0]]

            # Plot
            ax.plot(angles, values, 'o-', linewidth=2,
                   label=config.display_name, color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])

        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([m.replace('_', '\n') for m in metrics])

        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        # Add grid
        ax.grid(True)
        ax.set_ylim(0, 1)

        plt.title('POLLN Configuration Comparison - Radar Chart',
                 fontsize=14, fontweight='bold', pad=20)

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved radar chart to {output_path}")

        return fig

    def plot_performance_summary(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Create performance summary comparison.
        """
        if not self.comparisons:
            raise ValueError("No comparison data available")

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        config_ids = list(self.comparisons.keys())
        display_names = [self.comparisons[cid].display_name for cid in config_ids]

        # Final performance
        final_perf = [self.comparisons[cid].final_performance for cid in config_ids]
        axes[0, 0].bar(display_names, final_perf,
                      color=sns.color_palette("husl", len(config_ids)))
        axes[0, 0].set_title('Final Performance')
        axes[0, 0].set_ylabel('Performance Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3, axis='y')

        # Convergence time
        conv_times = [self.comparisons[cid].convergence_time for cid in config_ids]
        axes[0, 1].bar(display_names, conv_times,
                      color=sns.color_palette("husl", len(config_ids)))
        axes[0, 1].set_title('Convergence Time')
        axes[0, 1].set_ylabel('Timesteps')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # Stability score
        stability = [self.comparisons[cid].stability_score for cid in config_ids]
        axes[1, 0].bar(display_names, stability,
                      color=sns.color_palette("husl", len(config_ids)))
        axes[1, 0].set_title('Stability Score')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # Efficiency (performance / time)
        efficiency = [p / (t + 1) for p, t in zip(final_perf, conv_times)]
        axes[1, 1].bar(display_names, efficiency,
                      color=sns.color_palette("husl", len(config_ids)))
        axes[1, 1].set_title('Efficiency (Performance / Time)')
        axes[1, 1].set_ylabel('Efficiency')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.suptitle('POLLN Configuration Performance Summary',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved performance summary to {output_path}")

        return fig

    def perform_statistical_tests(self, metric: str,
                                 baseline_id: Optional[str] = None) -> Dict[str, StatisticalTest]:
        """
        Perform statistical tests comparing configurations.

        Args:
            metric: Metric to test
            baseline_id: Configuration to use as baseline (default: first)

        Returns:
            Dictionary of test results
        """
        if not self.comparisons:
            raise ValueError("No comparison data available")

        baseline_id = baseline_id or list(self.comparisons.keys())[0]
        baseline = self.comparisons[baseline_id]
        baseline_values = [getattr(m, metric) for m in baseline.metrics]

        results = {}

        for cid, config in self.comparisons.items():
            if cid == baseline_id:
                continue

            config_values = [getattr(m, metric) for m in config.metrics]

            # T-test
            t_stat, t_p = stats.ttest_ind(baseline_values, config_values)

            # Mann-Whitney U test (non-parametric)
            u_stat, u_p = stats.mannwhitneyu(baseline_values, config_values)

            # Effect size (Cohen's d)
            pooled_std = np.sqrt(
                (np.std(baseline_values)**2 + np.std(config_values)**2) / 2
            )
            cohens_d = (np.mean(baseline_values) - np.mean(config_values)) / (pooled_std + 1e-6)

            results[cid] = StatisticalTest(
                test_name="t-test",
                statistic=t_stat,
                p_value=t_p,
                significant=t_p < 0.05,
                effect_size=cohens_d
            )

        return results

    def plot_statistical_comparison(self, metric: str,
                                    output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize statistical comparison results.
        """
        # Perform tests
        test_results = self.perform_statistical_tests(metric)

        if not test_results:
            raise ValueError("Not enough configurations for comparison")

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        config_ids = list(test_results.keys())
        display_names = [self.comparisons[cid].display_name for cid in config_ids]

        # P-values
        p_values = [test_results[cid].p_value for cid in config_ids]
        colors = ['green' if p < 0.05 else 'gray' for p in p_values]

        axes[0].bar(display_names, p_values, color=colors, alpha=0.7)
        axes[0].axhline(0.05, color='red', linestyle='--', label='α = 0.05')
        axes[0].set_title(f'Statistical Significance ({metric})')
        axes[0].set_ylabel('P-value')
        axes[0].set_yscale('log')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')

        # Effect sizes
        effect_sizes = [test_results[cid].effect_size for cid in config_ids]
        effect_colors = ['red' if abs(e) > 0.8 else 'orange' if abs(e) > 0.5 else 'blue'
                        for e in effect_sizes]

        axes[1].bar(display_names, effect_sizes, color=effect_colors, alpha=0.7)
        axes[1].axhline(0, color='black', linewidth=0.5)
        axes[1].set_title("Effect Size (Cohen's d)")
        axes[1].set_ylabel("Effect Size")
        axes[1].axhline(0.8, color='red', linestyle='--', alpha=0.5, label='Large effect')
        axes[1].axhline(0.5, color='orange', linestyle='--', alpha=0.5, label='Medium effect')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.suptitle(f'Statistical Comparison: {metric.replace("_", " ").title()}',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved statistical comparison to {output_path}")

        return fig

    def generate_comparison_report(self, output_path: Path) -> None:
        """
        Generate comprehensive comparison report.
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate all plots
        metrics_to_compare = [
            'total_nodes',
            'total_edges',
            'avg_degree',
            'sparsity',
            'clustering_coefficient',
            'modularity',
            'avg_path_length'
        ]

        self.plot_grouped_bar_chart('clustering_coefficient',
                                   output_dir / 'comparison_clustering.png')
        self.plot_grouped_bar_chart('modularity',
                                   output_dir / 'comparison_modularity.png')
        self.plot_heatmap(metrics_to_compare,
                         output_dir / 'comparison_heatmap.png')
        self.plot_radar_chart(metrics_to_compare[:5],
                             output_dir / 'comparison_radar.png')
        self.plot_performance_summary(output_dir / 'comparison_performance.png')
        self.plot_statistical_comparison('clustering_coefficient',
                                        output_dir / 'comparison_statistical.png')

        # Generate HTML report
        self._generate_html_report(output_dir / 'comparison_report.html',
                                  metrics_to_compare)

        print(f"Generated comparison report in {output_dir}")

    def _generate_html_report(self, output_path: Path, metrics: List[str]):
        """Generate HTML comparison report."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLLN Configuration Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin-top: 0;
            color: #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .plot {{
            margin: 30px 0;
            text-align: center;
        }}
        .plot img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .significant {{
            color: #27ae60;
            font-weight: bold;
        }}
        .not-significant {{
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <h1>POLLN Configuration Comparison Report</h1>
    <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>Executive Summary</h2>
    <div class="summary">
"""

        # Add summary cards for each config
        for cid, config in self.comparisons.items():
            html += f"""
        <div class="summary-card">
            <h3>{config.display_name}</h3>
            <p><strong>Final Performance:</strong> <span class="metric-value">{config.final_performance:.3f}</span></p>
            <p><strong>Convergence Time:</strong> {config.convergence_time} timesteps</p>
            <p><strong>Stability Score:</strong> {config.stability_score:.3f}</p>
        </div>
"""

        html += """
    </div>

    <h2>Configuration Details</h2>
    <table>
        <tr>
            <th>Configuration</th>
            <th>Pruning Strategy</th>
            <th>Grafting Strategy</th>
            <th>Pruning Threshold</th>
            <th>Grafting Probability</th>
        </tr>
"""

        for cid, config in self.comparisons.items():
            html += f"""
        <tr>
            <td><strong>{config.display_name}</strong></td>
            <td>{config.config.pruning_strategy.value}</td>
            <td>{config.config.grafting_strategy.value}</td>
            <td>{config.config.pruning_threshold}</td>
            <td>{config.config.grafting_probability}</td>
        </tr>
"""

        html += """
    </table>

    <h2>Visualizations</h2>

    <div class="plot">
        <h3>Performance Comparison</h3>
        <img src="comparison_performance.png" alt="Performance Comparison">
    </div>

    <div class="plot">
        <h3>Clustering Coefficient Comparison</h3>
        <img src="comparison_clustering.png" alt="Clustering Coefficient">
    </div>

    <div class="plot">
        <h3>Modularity Comparison</h3>
        <img src="comparison_modularity.png" alt="Modularity">
    </div>

    <div class="plot">
        <h3>Metric Heatmap</h3>
        <img src="comparison_heatmap.png" alt="Metric Heatmap">
    </div>

    <div class="plot">
        <h3>Radar Chart Comparison</h3>
        <img src="comparison_radar.png" alt="Radar Chart">
    </div>

    <div class="plot">
        <h3>Statistical Analysis</h3>
        <img src="comparison_statistical.png" alt="Statistical Comparison">
    </div>

    <h2>Conclusions</h2>
"""

        # Add simple conclusions based on performance
        best_config = max(self.comparisons.items(),
                         key=lambda x: x[1].final_performance)
        fastest_config = min(self.comparisons.items(),
                            key=lambda x: x[1].convergence_time)
        most_stable = max(self.comparisons.items(),
                         key=lambda x: x[1].stability_score)

        html += f"""
    <ul>
        <li><strong>Best Performance:</strong> {best_config[1].display_name}
            (score: {best_config[1].final_performance:.3f})</li>
        <li><strong>Fastest Convergence:</strong> {fastest_config[1].display_name}
            ({fastest_config[1].convergence_time} timesteps)</li>
        <li><strong>Most Stable:</strong> {most_stable[1].display_name}
            (score: {most_stable[1].stability_score:.3f})</li>
    </ul>

</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)


if __name__ == "__main__":
    # Demo
    print("Creating comparison plotter demo...")

    plotter = ComparisonPlotter()

    # Add demo configurations
    for i, (pruning, grafting) in enumerate([
        ('combined', 'heuristic'),
        ('threshold', 'random'),
        ('activity', 'similarity')
    ]):
        config_id = f"config_{i}"
        display_name = f"{pruning.capitalize()} / {grafting.capitalize()}"

        # Generate synthetic metrics
        metrics = []
        for gen in range(50):
            metrics.append(EvolutionMetrics(
                generation=gen,
                total_nodes=20,
                total_edges=50 + i * 10 + gen,
                avg_degree=5 + i * 0.5,
                sparsity=0.8 - i * 0.05,
                clustering_coefficient=0.3 + i * 0.1 + np.random.normal(0, 0.05),
                modularity=0.4 + i * 0.1,
                avg_path_length=3.0 - i * 0.2,
                diameter=6,
                pruned_this_cycle=np.random.randint(0, 5),
                grafted_this_cycle=np.random.randint(0, 5),
                small_world_sigma=1.5 + i * 0.2,
                degree_assortativity=0.1 + i * 0.05,
                spectral_gap=0.5 + i * 0.1,
                power_law_alpha=2.0 + i * 0.2,
                power_law_ks_distance=0.1
            ))

        comp_config = ComparisonConfig(
            config_id=config_id,
            display_name=display_name,
            config=EvolutionConfig(),
            metrics=metrics,
            final_performance=0.7 + i * 0.1,
            convergence_time=100 - i * 10,
            stability_score=0.6 + i * 0.1
        )

        plotter.add_comparison(comp_config)

    # Generate report
    output_dir = Path("../../reports/visualizations")
    plotter.generate_comparison_report(output_dir / 'comparison_report.html')

    print("Comparison report complete!")
