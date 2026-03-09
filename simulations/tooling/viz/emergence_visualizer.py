"""
POLLN Emergence Visualizer
==========================

Visualize emergence detection, pressure maps, flow patterns,
and synergy metrics in POLLN agent networks.

Features:
- Pressure map heatmaps
- Flow pattern animations
- Synergy metric visualizations
- Time-lapse emergence animations
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import json
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from base import AgentGraph, EvolutionConfig, AgentNode


@dataclass
class EmergenceMetrics:
    """Metrics for detecting emergence."""
    timestamp: float

    # Pressure metrics
    pressure_variance: float
    pressure_entropy: float
    pressure_skew: float

    # Flow metrics
    flow_coherence: float
    flow_diversity: float
    flow_velocity: float

    # Synergy metrics
    mutual_information: float
    integration: float
    segregation: float

    # Emergence indicators
    emergence_strength: float
    phase_transition_detected: bool
    critical_point: bool


@dataclass
class PressureMap:
    """Pressure map data for visualization."""
    agent_pressures: Dict[str, float]
    spatial_coords: Dict[str, Tuple[float, float]]
    pressure_gradients: Dict[str, Tuple[float, float]]


@dataclass
class FlowPattern:
    """Flow pattern data."""
    source: str
    target: str
    flow_rate: float
    pressure_diff: float
    resistance: float


class EmergenceVisualizer:
    """
    Visualize emergence in POLLN agent networks.

    Detects and visualizes:
    - Pressure gradients
    - Information flow
    - Synergy patterns
    - Phase transitions
    """

    def __init__(self, graph: AgentGraph):
        self.graph = graph
        self.G = graph.graph

        # Emergence history
        self.metrics_history: List[EmergenceMetrics] = []

        # Pre-compute agent embeddings
        self.agent_embeddings = self._compute_agent_embeddings()

    def _compute_agent_embeddings(self) -> Dict[str, np.ndarray]:
        """Compute low-dimensional embeddings for agents."""
        # Use agent capabilities as features
        features = []
        agent_ids = []

        for agent_id in self.G.nodes():
            node = self.graph.nodes.get(agent_id)
            if node:
                # Capability vector
                caps = node.capabilities
                feature = np.array([caps.get(k, 0) for k in sorted(caps.keys())])
                features.append(feature)
                agent_ids.append(agent_id)

        if not features:
            return {}

        features = np.array(features)

        # Use t-SNE for 2D embedding
        if len(features) > 2:
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(features)-1))
            embeddings_2d = tsne.fit_transform(features)
        else:
            embeddings_2d = features

        # Create mapping
        embeddings = {}
        for i, agent_id in enumerate(agent_ids):
            embeddings[agent_id] = embeddings_2d[i]

        return embeddings

    def compute_pressure_map(self) -> PressureMap:
        """
        Compute pressure map based on agent activity and value functions.

        Pressure represents the "influence" or "activation potential" of each agent.
        """
        pressures = {}
        spatial_coords = {}

        # Compute pressures
        for agent_id in self.G.nodes():
            node = self.graph.nodes.get(agent_id)
            if node:
                # Pressure = combination of value function, activation, and centrality
                value = node.value_function
                activation = node.get_avg_activation()
                centrality = self.graph.nodes[agent_id].centrality

                pressure = 0.4 * value + 0.3 * activation + 0.3 * centrality
                pressures[agent_id] = pressure

                # Use t-SNE embedding as spatial coordinates
                if agent_id in self.agent_embeddings:
                    spatial_coords[agent_id] = tuple(self.agent_embeddings[agent_id])
                else:
                    spatial_coords[agent_id] = (0, 0)

        # Compute pressure gradients
        gradients = {}
        for agent_id in self.G.nodes():
            if agent_id not in spatial_coords:
                continue

            x, y = spatial_coords[agent_id]
            grad_x, grad_y = 0.0, 0.0

            # Compute gradient from neighbors
            for neighbor in self.G.neighbors(agent_id):
                if neighbor in spatial_coords and neighbor in pressures:
                    nx_pos, ny_pos = spatial_coords[neighbor]
                    pressure_diff = pressures[neighbor] - pressures[agent_id]

                    # Direction vector
                    dx = nx_pos - x
                    dy = ny_pos - y
                    dist = np.sqrt(dx**2 + dy**2) + 1e-6

                    # Gradient contribution
                    grad_x += pressure_diff * dx / dist
                    grad_y += pressure_diff * dy / dist

            gradients[agent_id] = (grad_x, grad_y)

        return PressureMap(
            agent_pressures=pressures,
            spatial_coords=spatial_coords,
            pressure_gradients=gradients
        )

    def compute_flow_patterns(self, pressure_map: PressureMap) -> List[FlowPattern]:
        """
        Compute flow patterns based on pressure gradients.
        """
        flows = []

        for source, target in self.G.edges():
            if source in pressure_map.agent_pressures and target in pressure_map.agent_pressures:
                source_pressure = pressure_map.agent_pressures[source]
                target_pressure = pressure_map.agent_pressures[target]

                # Flow driven by pressure difference
                pressure_diff = source_pressure - target_pressure

                # Resistance from edge weight (inverse)
                edge_data = self.G.get_edge_data(source, target)
                resistance = 1.0 / (edge_data.get('weight', 0.5) + 0.01)

                # Flow rate (Ohm's law analog)
                flow_rate = pressure_diff / resistance

                flows.append(FlowPattern(
                    source=source,
                    target=target,
                    flow_rate=flow_rate,
                    pressure_diff=pressure_diff,
                    resistance=resistance
                ))

        return flows

    def compute_synergy_metrics(self) -> Tuple[float, float, float]:
        """
        Compute synergy metrics: mutual information, integration, segregation.
        """
        # Get agent states as feature matrix
        features = []
        for agent_id in self.G.nodes():
            node = self.graph.nodes.get(agent_id)
            if node:
                caps = node.capabilities
                feature = np.array([caps.get(k, 0) for k in sorted(caps.keys())])
                features.append(feature)

        if not features:
            return 0.0, 0.0, 0.0

        features = np.array(features)

        # Mutual information (approximated by correlation)
        if features.shape[0] > 1:
            corr_matrix = np.corrcoef(features.T)
            mutual_info = np.mean(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        else:
            mutual_info = 0.0

        # Integration: variance of mean vs mean of variance
        if len(features) > 1:
            mean_vector = np.mean(features, axis=0)
            variance_of_mean = np.var(mean_vector)
            mean_of_variance = np.mean(np.var(features, axis=0))
            integration = variance_of_mean / (mean_of_variance + 1e-6)
        else:
            integration = 0.0

        # Segregation: how distinct are agents from each other
        if len(features) > 1:
            distances = pdist(features, metric='euclidean')
            segregation = np.mean(distances)
        else:
            segregation = 0.0

        return mutual_info, integration, segregation

    def detect_emergence(self) -> EmergenceMetrics:
        """
        Detect emergence by computing various metrics.
        """
        pressure_map = self.compute_pressure_map()
        flows = self.compute_flow_patterns(pressure_map)
        mutual_info, integration, segregation = self.compute_synergy_metrics()

        # Pressure statistics
        pressures = list(pressure_map.agent_pressures.values())
        pressure_variance = np.var(pressures)
        pressure_entropy = -np.sum([p * np.log(p + 1e-10) for p in pressures if p > 0])
        pressure_skew = float(pd.Series(pressures).skew()) if len(pressures) > 2 else 0.0

        # Flow statistics
        flow_rates = [f.flow_rate for f in flows]
        if flow_rates:
            flow_coherence = np.std(flow_rates) / (np.mean(np.abs(flow_rates)) + 1e-6)
            flow_diversity = len(set([f.source for f in flows])) / self.G.number_of_nodes()
            flow_velocity = np.mean(np.abs(flow_rates))
        else:
            flow_coherence = 0.0
            flow_diversity = 0.0
            flow_velocity = 0.0

        # Emergence strength (composite metric)
        emergence_strength = (
            0.3 * flow_coherence +
            0.3 * mutual_info +
            0.2 * integration +
            0.2 * flow_diversity
        )

        # Detect phase transition (sharp change in emergence)
        phase_transition = False
        critical_point = False

        if self.metrics_history:
            prev_emergence = self.metrics_history[-1].emergence_strength
            delta = abs(emergence_strength - prev_emergence)
            if delta > 0.2:  # Threshold for phase transition
                phase_transition = True
            if emergence_strength > 0.8:  # Threshold for critical point
                critical_point = True

        metrics = EmergenceMetrics(
            timestamp=time.time(),
            pressure_variance=pressure_variance,
            pressure_entropy=pressure_entropy,
            pressure_skew=pressure_skew,
            flow_coherence=flow_coherence,
            flow_diversity=flow_diversity,
            flow_velocity=flow_velocity,
            mutual_information=mutual_info,
            integration=integration,
            segregation=segregation,
            emergence_strength=emergence_strength,
            phase_transition_detected=phase_transition,
            critical_point=critical_point
        )

        self.metrics_history.append(metrics)
        return metrics

    def visualize_pressure_map(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize pressure map as heatmap.
        """
        pressure_map = self.compute_pressure_map()

        fig, ax = plt.subplots(figsize=(12, 10))

        # Get coordinates and pressures
        coords = list(pressure_map.spatial_coords.values())
        pressures = list(pressure_map.agent_pressures.values())

        if not coords:
            print("No spatial coordinates available")
            return fig

        coords = np.array(coords)

        # Create triangulation for contour plot
        from scipy.spatial import Delaunay
        try:
            tri = Delaunay(coords)

            # Create regular grid for interpolation
            x_min, x_min = coords.min(axis=0)
            x_max, y_max = coords.max(axis=0)

            # Plot pressure contour
            from scipy.interpolate import griddata
            grid_x, grid_y = np.mgrid[x_min:x_max:100j, x_min:y_max:100j]
            grid_z = griddata(coords, pressures, (grid_x, grid_y), method='cubic')

            # Contour plot
            contour = ax.contourf(grid_x, grid_y, grid_z, levels=20, cmap='RdYlBu_r', alpha=0.8)
            plt.colorbar(contour, ax=ax, label='Pressure')

            # Plot agents
            ax.scatter(coords[:, 0], coords[:, 1],
                      c=pressures,
                      s=200,
                      cmap='RdYlBu_r',
                      edgecolors='black',
                      linewidth=2)

            # Add agent labels
            for agent_id, (x, y) in pressure_map.spatial_coords.items():
                ax.annotate(agent_id, (x, y),
                           fontsize=8,
                           ha='center',
                           va='center',
                           weight='bold')

            # Plot pressure gradients (quiver)
            grad_x = []
            grad_y = []
            grad_coords = []

            for agent_id, (gx, gy) in pressure_map.pressure_gradients.items():
                if agent_id in pressure_map.spatial_coords:
                    x, y = pressure_map.spatial_coords[agent_id]
                    grad_coords.append([x, y])
                    grad_x.append(gx)
                    grad_y.append(gy)

            if grad_coords:
                grad_coords = np.array(grad_coords)
                ax.quiver(grad_coords[:, 0], grad_coords[:, 1],
                         grad_x, grad_y,
                         alpha=0.5,
                         width=0.005,
                         scale=50,
                         color='black')

        except Exception as e:
            print(f"Error creating pressure map: {e}")
            # Fallback to simple scatter
            ax.scatter(coords[:, 0], coords[:, 1],
                      c=pressures,
                      s=200,
                      cmap='RdYlBu_r',
                      edgecolors='black',
                      linewidth=2)

        ax.set_title('POLLN Pressure Map', fontsize=16, fontweight='bold')
        ax.set_xlabel('Embedding Dimension 1')
        ax.set_ylabel('Embedding Dimension 2')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved pressure map to {output_path}")

        return fig

    def visualize_flow_patterns(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize flow patterns.
        """
        pressure_map = self.compute_pressure_map()
        flows = self.compute_flow_patterns(pressure_map)

        fig, ax = plt.subplots(figsize=(12, 10))

        # Get positions
        pos = pressure_map.spatial_coords

        # Draw edges with flow-based styling
        for flow in flows:
            if flow.source in pos and flow.target in pos:
                x1, y1 = pos[flow.source]
                x2, y2 = pos[flow.target]

                # Color based on flow direction
                if flow.flow_rate > 0:
                    color = 'green'
                    alpha = min(abs(flow.flow_rate) / 5, 1.0)
                else:
                    color = 'red'
                    alpha = min(abs(flow.flow_rate) / 5, 1.0)

                # Line width based on flow magnitude
                width = min(abs(flow.flow_rate), 5)

                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->',
                                         color=color,
                                         alpha=alpha,
                                         lw=width))

        # Draw nodes
        coords = np.array(list(pos.values()))
        pressures = [pressure_map.agent_pressures[agent_id]
                    for agent_id in pos.keys()]

        ax.scatter(coords[:, 0], coords[:, 1],
                  c=pressures,
                  s=200,
                  cmap='RdYlBu_r',
                  edgecolors='black',
                  linewidth=2,
                  zorder=10)

        # Add labels
        for agent_id, (x, y) in pos.items():
            ax.annotate(agent_id, (x, y),
                       fontsize=8,
                       ha='center',
                       va='center',
                       weight='bold',
                       zorder=11)

        ax.set_title('POLLN Information Flow Patterns', fontsize=16, fontweight='bold')
        ax.set_xlabel('Embedding Dimension 1')
        ax.set_ylabel('Embedding Dimension 2')
        ax.grid(True, alpha=0.3)

        # Add colorbar for pressure
        sm = plt.cm.ScalarMappable(cmap='RdYlBu_r',
                                   norm=plt.Normalize(vmin=min(pressures),
                                                    vmax=max(pressures)))
        sm.set_array([])
        plt.colorbar(sm, ax=ax, label='Pressure')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved flow patterns to {output_path}")

        return fig

    def visualize_synergy_metrics(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize synergy metrics over time.
        """
        if not self.metrics_history:
            print("No emergence metrics history available")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available',
                   ha='center', va='center', fontsize=14)
            return fig

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        timestamps = [m.timestamp - self.metrics_history[0].timestamp
                     for m in self.metrics_history]

        # Mutual Information
        axes[0, 0].plot(timestamps, [m.mutual_information for m in self.metrics_history],
                       'b-', linewidth=2)
        axes[0, 0].set_title('Mutual Information')
        axes[0, 0].set_ylabel('MI')
        axes[0, 0].grid(True, alpha=0.3)

        # Integration
        axes[0, 1].plot(timestamps, [m.integration for m in self.metrics_history],
                       'g-', linewidth=2)
        axes[0, 1].set_title('Integration')
        axes[0, 1].set_ylabel('Integration')
        axes[0, 1].grid(True, alpha=0.3)

        # Segregation
        axes[1, 0].plot(timestamps, [m.segregation for m in self.metrics_history],
                       'r-', linewidth=2)
        axes[1, 0].set_title('Segregation')
        axes[1, 0].set_ylabel('Segregation')
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].grid(True, alpha=0.3)

        # Emergence strength
        axes[1, 1].plot(timestamps, [m.emergence_strength for m in self.metrics_history],
                       'purple', linewidth=2)

        # Mark phase transitions
        for i, m in enumerate(self.metrics_history):
            if m.phase_transition_detected:
                axes[1, 1].axvline(timestamps[i], color='orange',
                                  linestyle='--', alpha=0.5, label='Phase Transition')
            if m.critical_point:
                axes[1, 1].axvline(timestamps[i], color='red',
                                  linestyle=':', alpha=0.5, label='Critical Point')

        axes[1, 1].set_title('Emergence Strength')
        axes[1, 1].set_ylabel('Strength')
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].grid(True, alpha=0.3)

        # Remove duplicate labels
        handles, labels = axes[1, 1].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        axes[1, 1].legend(by_label.values(), by_label.keys(), loc='best')

        plt.suptitle('POLLN Synergy Metrics', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved synergy metrics to {output_path}")

        return fig

    def create_emergence_animation(self, output_path: Path,
                                  num_frames: int = 100,
                                  interval: int = 100) -> None:
        """
        Create animated visualization of emergence over time.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        def update(frame):
            # Update emergence metrics
            metrics = self.detect_emergence()

            # Clear axes
            for ax in axes.flat:
                ax.clear()

            # Pressure map
            ax1 = axes[0, 0]
            pressure_map = self.compute_pressure_map()
            coords = np.array(list(pressure_map.spatial_coords.values()))
            pressures = list(pressure_map.agent_pressures.values())

            if len(coords) > 0:
                scatter = ax1.scatter(coords[:, 0], coords[:, 1],
                                    c=pressures, s=200,
                                    cmap='RdYlBu_r',
                                    edgecolors='black',
                                    linewidth=2,
                                    vmin=0, vmax=1)
            ax1.set_title(f'Pressure Map (Frame {frame})')
            ax1.grid(True, alpha=0.3)

            # Flow patterns
            ax2 = axes[0, 1]
            flows = self.compute_flow_patterns(pressure_map)
            pos = pressure_map.spatial_coords

            for flow in flows[:10]:  # Limit to top 10 flows
                if flow.source in pos and flow.target in pos:
                    x1, y1 = pos[flow.source]
                    x2, y2 = pos[flow.target]
                    color = 'green' if flow.flow_rate > 0 else 'red'
                    ax2.annotate('', xy=(x2, y2), xytext=(x1, y1),
                               arrowprops=dict(arrowstyle='->',
                                             color=color,
                                             alpha=0.6,
                                             lw=2))

            ax2.set_title('Flow Patterns')
            ax2.grid(True, alpha=0.3)

            # Emergence strength
            ax3 = axes[1, 0]
            if self.metrics_history:
                timestamps = [m.timestamp - self.metrics_history[0].timestamp
                            for m in self.metrics_history]
                strengths = [m.emergence_strength for m in self.metrics_history]
                ax3.plot(timestamps, strengths, 'b-', linewidth=2)
                ax3.set_ylim(0, 1)
            ax3.set_title('Emergence Strength')
            ax3.grid(True, alpha=0.3)

            # Metrics summary
            ax4 = axes[1, 1]
            ax4.axis('off')
            summary = f"""
            Emergence Metrics (Frame {frame})

            Strength: {metrics.emergence_strength:.3f}
            Mutual Info: {metrics.mutual_information:.3f}
            Integration: {metrics.integration:.3f}
            Segregation: {metrics.segregation:.3f}

            Flow Coherence: {metrics.flow_coherence:.3f}
            Flow Velocity: {metrics.flow_velocity:.3f}

            Phase Transition: {'YES' if metrics.phase_transition_detected else 'No'}
            Critical Point: {'YES' if metrics.critical_point else 'No'}
            """
            ax4.text(0.1, 0.5, summary,
                   fontsize=10,
                   verticalalignment='center',
                   family='monospace',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.suptitle('POLLN Emergence Animation', fontsize=16, fontweight='bold')

        anim = animation.FuncAnimation(fig, update, frames=num_frames,
                                      interval=interval, repeat=False)

        # Save as MP4
        try:
            anim.save(output_path, writer='ffmpeg', fps=10, dpi=100)
            print(f"Saved emergence animation to {output_path}")
        except Exception as e:
            print(f"Could not save MP4 (ffmpeg not available): {e}")
            print("Saving as GIF instead...")
            output_path_gif = output_path.with_suffix('.gif')
            anim.save(output_path_gif, writer='pillow', fps=10)
            print(f"Saved emergence animation as GIF to {output_path_gif}")

        plt.close()


import time


if __name__ == "__main__":
    # Demo
    from base import AgentGraph, EvolutionConfig, PruningStrategy, GraftingStrategy

    print("Creating emergence visualization demo...")

    config = EvolutionConfig(
        pruning_strategy=PruningStrategy.COMBINED,
        grafting_strategy=GraftingStrategy.HEURISTIC
    )
    graph = AgentGraph(num_agents=15, config=config)

    visualizer = EmergenceVisualizer(graph)

    # Run some evolution to get interesting dynamics
    for i in range(10):
        visualizer.detect_emergence()

    # Generate visualizations
    output_dir = Path("../../reports/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    visualizer.visualize_pressure_map(output_dir / "pressure_map.png")
    visualizer.visualize_flow_patterns(output_dir / "flow_patterns.png")
    visualizer.visualize_synergy_metrics(output_dir / "synergy_metrics.png")

    # Create animation
    visualizer.create_emergence_animation(
        output_dir / "emergence_animation.mp4",
        num_frames=50
    )

    print("Emergence visualizations complete!")
