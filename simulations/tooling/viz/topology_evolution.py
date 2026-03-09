"""
POLLN Topology Evolution Visualizer
===================================

Animate and visualize graph topology changes over time.

Features:
- Animated graph evolution
- Before/after comparisons
- Metrics over time visualization
- Pruning and grafting event highlights
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from base import AgentGraph, EvolutionMetrics, EvolutionConfig, PruningStrategy, GraftingStrategy


@dataclass
class EvolutionEvent:
    """Record of a graph evolution event."""
    generation: int
    event_type: str  # 'pruned', 'grafted', 'cluster_merged', 'cluster_split'
    source: Optional[str]
    target: Optional[str]
    weight: Optional[float]
    reason: str


@dataclass
class GraphSnapshot:
    """Snapshot of graph state at a point in time."""
    generation: int
    nodes: Dict[str, Dict[str, Any]]
    edges: Dict[Tuple[str, str], Dict[str, Any]]
    metrics: EvolutionMetrics
    events: List[EvolutionEvent]


class TopologyEvolutionVisualizer:
    """
    Visualize topology evolution of POLLN agent graphs.

    Creates animations and comparisons showing how the graph
    structure changes over generations.
    """

    def __init__(self, graph: AgentGraph):
        self.graph = graph
        self.G = graph.graph

        # Evolution history
        self.snapshots: List[GraphSnapshot] = []
        self.events: List[EvolutionEvent] = []

    def take_snapshot(self, generation: int,
                     events: List[EvolutionEvent]) -> GraphSnapshot:
        """
        Take a snapshot of current graph state.
        """
        # Capture node states
        nodes = {}
        for node_id in self.G.nodes():
            node = self.graph.nodes.get(node_id)
            if node:
                nodes[node_id] = {
                    'capabilities': node.capabilities,
                    'value_function': node.value_function,
                    'activation': node.get_avg_activation(),
                    'cluster': node.cluster,
                    'centrality': node.centrality
                }

        # Capture edge states
        edges = {}
        for u, v in self.G.edges():
            edge_data = self.G.get_edge_data(u, v)
            edge = self.graph.edges.get((u, v))
            if edge:
                edges[(u, v)] = {
                    'weight': edge.weight,
                    'age': edge.age,
                    'activity': edge.activity_level
                }

        # Get metrics
        metrics = self.graph.compute_metrics(generation)

        snapshot = GraphSnapshot(
            generation=generation,
            nodes=nodes,
            edges=edges,
            metrics=metrics,
            events=events
        )

        self.snapshots.append(snapshot)
        self.events.extend(events)

        return snapshot

    def visualize_evolution_timeline(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize evolution metrics over time.
        """
        if not self.snapshots:
            raise ValueError("No snapshots available. Call take_snapshot() first.")

        fig, axes = plt.subplots(3, 2, figsize=(14, 10))

        generations = [s.generation for s in self.snapshots]

        # Nodes and edges
        axes[0, 0].plot(generations, [s.metrics.total_nodes for s in self.snapshots],
                       'o-', label='Nodes', linewidth=2, markersize=4)
        axes[0, 0].plot(generations, [s.metrics.total_edges for s in self.snapshots],
                       's-', label='Edges', linewidth=2, markersize=4)
        axes[0, 0].set_title('Graph Size')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Sparsity and clustering
        ax2 = axes[0, 1]
        ax2_twin = ax2.twinx()
        line1 = ax2.plot(generations, [s.metrics.sparsity for s in self.snapshots],
                        'o-', color='blue', label='Sparsity', linewidth=2)
        line2 = ax2_twin.plot(generations, [s.metrics.clustering_coefficient for s in self.snapshots],
                             's-', color='red', label='Clustering', linewidth=2)
        ax2.set_title('Sparsity & Clustering')
        ax2.set_ylabel('Sparsity', color='blue')
        ax2_twin.set_ylabel('Clustering Coefficient', color='red')
        ax2.legend(handles=line1 + line2, loc='best')
        ax2.grid(True, alpha=0.3)

        # Path length and diameter
        axes[1, 0].plot(generations, [s.metrics.avg_path_length for s in self.snapshots],
                       'o-', label='Avg Path Length', linewidth=2, markersize=4)
        axes[1, 0].plot(generations, [s.metrics.diameter for s in self.snapshots],
                       's-', label='Diameter', linewidth=2, markersize=4)
        axes[1, 0].set_title('Path Metrics')
        axes[1, 0].set_ylabel('Length')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Modularity and small-world
        ax4 = axes[1, 1]
        ax4_twin = ax4.twinx()
        line1 = ax4.plot(generations, [s.metrics.modularity for s in self.snapshots],
                        'o-', color='green', label='Modularity', linewidth=2)
        line2 = ax4_twin.plot(generations, [s.metrics.small_world_sigma for s in self.snapshots],
                             's-', color='purple', label='Small-World σ', linewidth=2)
        ax4.set_title('Community Structure')
        ax4.set_ylabel('Modularity', color='green')
        ax4_twin.set_ylabel('Small-World σ', color='purple')
        ax4.legend(handles=line1 + line2, loc='best')
        ax4.grid(True, alpha=0.3)

        # Pruning and grafting events
        pruned = [s.metrics.pruned_this_cycle for s in self.snapshots]
        grafted = [s.metrics.grafted_this_cycle for s in self.snapshots]

        x = np.arange(len(generations))
        width = 0.35

        axes[2, 0].bar(x - width/2, pruned, width, label='Pruned', color='red', alpha=0.7)
        axes[2, 0].bar(x + width/2, grafted, width, label='Grafted', color='green', alpha=0.7)
        axes[2, 0].set_title('Evolution Events')
        axes[2, 0].set_ylabel('Count')
        axes[2, 0].set_xticks(x)
        axes[2, 0].set_xticklabels(generations, rotation=45)
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3, axis='y')

        # Power law metrics
        axes[2, 1].plot(generations, [s.metrics.power_law_alpha for s in self.snapshots],
                       'o-', label='Power Law α', linewidth=2, markersize=4)
        axes[2, 1].axhline(2.0, color='red', linestyle='--', alpha=0.5, label='Scale-free threshold')
        axes[2, 1].set_title('Power Law Exponent')
        axes[2, 1].set_ylabel('α')
        axes[2, 1].set_xlabel('Generation')
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)

        plt.suptitle('POLLN Topology Evolution', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved evolution timeline to {output_path}")

        return fig

    def visualize_before_after(self, before_gen: int, after_gen: int,
                               output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize graph structure before and after evolution.
        """
        # Find snapshots
        before_snap = next((s for s in self.snapshots if s.generation == before_gen), None)
        after_snap = next((s for s in self.snapshots if s.generation == after_gen), None)

        if not before_snap or not after_snap:
            raise ValueError(f"Snapshots not found for generations {before_gen} and {after_gen}")

        fig, axes = plt.subplots(1, 2, figsize=(16, 8))

        # Reconstruct graphs from snapshots
        G_before = self._reconstruct_graph(before_snap)
        G_after = self._reconstruct_graph(after_snap)

        # Layout
        pos_before = nx.spring_layout(G_before, seed=42)
        pos_after = nx.spring_layout(G_after, seed=42)

        # Before
        self._draw_graph_on_axis(axes[0], G_before, pos_before, before_snap,
                                 f"Generation {before_gen}")

        # After
        self._draw_graph_on_axis(axes[1], G_after, pos_after, after_snap,
                                 f"Generation {after_gen}")

        # Highlight changes
        self._highlight_changes(axes[0], axes[1], before_snap, after_snap,
                               pos_before, pos_after)

        plt.suptitle('Topology Evolution: Before/After Comparison',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved before/after comparison to {output_path}")

        return fig

    def _reconstruct_graph(self, snapshot: GraphSnapshot) -> nx.DiGraph:
        """Reconstruct NetworkX graph from snapshot."""
        G = nx.DiGraph()

        # Add nodes
        for node_id, data in snapshot.nodes.items():
            G.add_node(node_id, **data)

        # Add edges
        for (u, v), data in snapshot.edges.items():
            G.add_edge(u, v, **data)

        return G

    def _draw_graph_on_axis(self, ax, G, pos, snapshot, title):
        """Draw graph on axis with proper styling."""
        # Get node colors by cluster
        clusters = [snapshot.nodes.get(n, {}).get('cluster', 0) for n in G.nodes()]
        num_clusters = len(set(clusters)) if clusters else 1

        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax,
                              edge_color='gray',
                              alpha=0.5,
                              arrows=True,
                              arrowsize=20,
                              width=1)

        # Draw nodes
        cmap = plt.cm.get_cmap('viridis', num_clusters)
        nx.draw_networkx_nodes(G, pos, ax=ax,
                              node_color=clusters,
                              cmap=cmap,
                              node_size=300,
                              alpha=0.9)

        # Draw labels
        nx.draw_networkx_labels(G, pos, ax=ax,
                              font_size=8,
                              font_weight='bold')

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')

    def _highlight_changes(self, ax_before, ax_after, before_snap, after_snap,
                          pos_before, pos_after):
        """Highlight nodes and edges that changed."""
        # Find added/removed nodes
        before_nodes = set(before_snap.nodes.keys())
        after_nodes = set(after_snap.nodes.keys())

        added_nodes = after_nodes - before_nodes
        removed_nodes = before_nodes - after_nodes

        # Find added/removed edges
        before_edges = set(before_snap.edges.keys())
        after_edges = set(after_snap.edges.keys())

        added_edges = after_edges - before_edges
        removed_edges = before_edges - after_edges

        # Draw added edges in green on after
        G_after = self._reconstruct_graph(after_snap)
        for u, v in added_edges:
            if u in pos_after and v in pos_after:
                x1, y1 = pos_after[u]
                x2, y2 = pos_after[v]
                ax_after.plot([x1, x2], [y1, y2],
                             color='green', linewidth=3, alpha=0.7, zorder=0)

        # Draw removed edges in red on before (dashed)
        G_before = self._reconstruct_graph(before_snap)
        for u, v in removed_edges:
            if u in pos_before and v in pos_before:
                x1, y1 = pos_before[u]
                x2, y2 = pos_before[v]
                ax_before.plot([x1, x2], [y1, y2],
                              color='red', linewidth=2, alpha=0.5,
                              linestyle='--', zorder=0)

    def create_evolution_animation(self, output_path: Path,
                                  interval: int = 500) -> None:
        """
        Create animated visualization of graph evolution.
        """
        if not self.snapshots:
            raise ValueError("No snapshots available. Call take_snapshot() first.")

        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        plt.suptitle('POLLN Topology Evolution Animation',
                    fontsize=16, fontweight='bold')

        def update(frame):
            ax_graph, ax_metrics = axes

            # Clear axes
            ax_graph.clear()
            ax_metrics.clear()

            snapshot = self.snapshots[frame]

            # Reconstruct graph
            G = self._reconstruct_graph(snapshot)

            # Layout
            pos = nx.spring_layout(G, seed=42)

            # Draw graph
            clusters = [snapshot.nodes.get(n, {}).get('cluster', 0) for n in G.nodes()]
            num_clusters = len(set(clusters)) if clusters else 1
            cmap = plt.cm.get_cmap('viridis', num_clusters)

            nx.draw_networkx_edges(G, pos, ax=ax_graph,
                                  edge_color='gray', alpha=0.5,
                                  arrows=True, arrowsize=20)
            nx.draw_networkx_nodes(G, pos, ax=ax_graph,
                                  node_color=clusters,
                                  cmap=cmap,
                                  node_size=300,
                                  alpha=0.9)
            nx.draw_networkx_labels(G, pos, ax=ax_graph,
                                  font_size=8,
                                  font_weight='bold')

            ax_graph.set_title(f"Generation {snapshot.generation}", fontweight='bold')
            ax_graph.axis('off')

            # Plot metrics up to this frame
            generations = [s.generation for s in self.snapshots[:frame+1]]

            # Nodes and edges
            ax_metrics.plot(generations,
                           [s.metrics.total_nodes for s in self.snapshots[:frame+1]],
                           'o-', label='Nodes', linewidth=2, markersize=4)
            ax_metrics.plot(generations,
                           [s.metrics.total_edges for s in self.snapshots[:frame+1]],
                           's-', label='Edges', linewidth=2, markersize=4)
            ax_metrics.axvline(snapshot.generation, color='red',
                              linestyle='--', alpha=0.5)

            ax_metrics.set_title('Graph Size Over Time')
            ax_metrics.set_xlabel('Generation')
            ax_metrics.set_ylabel('Count')
            ax_metrics.legend()
            ax_metrics.grid(True, alpha=0.3)

            # Display events
            events_text = "\n".join([
                f"{e.event_type}: {e.source} -> {e.target}"
                for e in snapshot.events[:5]
            ]) or "No events"

            fig.text(0.02, 0.02, f"Events:\n{events_text}",
                    fontsize=8, family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        anim = animation.FuncAnimation(fig, update, frames=len(self.snapshots),
                                      interval=interval, repeat=True)

        # Save
        try:
            anim.save(output_path, writer='ffmpeg', fps=2, dpi=100)
            print(f"Saved evolution animation to {output_path}")
        except Exception as e:
            print(f"Could not save MP4 (ffmpeg not available): {e}")
            print("Saving as GIF instead...")
            output_path_gif = output_path.with_suffix('.gif')
            anim.save(output_path_gif, writer='pillow', fps=2)
            print(f"Saved evolution animation as GIF to {output_path_gif}")

        plt.close()

    def create_degree_distribution_animation(self, output_path: Path,
                                           interval: int = 500) -> None:
        """
        Create animated degree distribution visualization.
        """
        if not self.snapshots:
            raise ValueError("No snapshots available")

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        plt.suptitle('Degree Distribution Evolution',
                    fontsize=16, fontweight='bold')

        def update(frame):
            ax_dist, ax_cdf = axes
            ax_dist.clear()
            ax_cdf.clear()

            snapshot = self.snapshots[frame]
            G = self._reconstruct_graph(snapshot)

            # Get degrees
            degrees = [d for n, d in G.degree()]

            # Plot histogram
            ax_dist.hist(degrees, bins='auto', alpha=0.7, color='steelblue', edgecolor='black')
            ax_dist.set_title(f"Generation {snapshot.generation} - Distribution", fontweight='bold')
            ax_dist.set_xlabel('Degree')
            ax_dist.set_ylabel('Frequency')
            ax_dist.grid(True, alpha=0.3)

            # Plot CDF
            sorted_degrees = np.sort(degrees)
            cdf = np.arange(1, len(sorted_degrees) + 1) / len(sorted_degrees)

            ax_cdf.plot(sorted_degrees, cdf, 'o-', linewidth=2, markersize=4)
            ax_cdf.set_title('Cumulative Distribution', fontweight='bold')
            ax_cdf.set_xlabel('Degree')
            ax_cdf.set_ylabel('CDF')
            ax_cdf.grid(True, alpha=0.3)

            # Add power law fit annotation
            if snapshot.metrics.power_law_alpha > 0:
                ax_cdf.text(0.95, 0.05, f'Power law α: {snapshot.metrics.power_law_alpha:.2f}',
                           transform=ax_cdf.transAxes,
                           ha='right', va='bottom',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

        anim = animation.FuncAnimation(fig, update, frames=len(self.snapshots),
                                      interval=interval, repeat=True)

        # Save
        try:
            anim.save(output_path, writer='ffmpeg', fps=2, dpi=100)
            print(f"Saved degree distribution animation to {output_path}")
        except Exception as e:
            print(f"Could not save MP4: {e}")
            output_path_gif = output_path.with_suffix('.gif')
            anim.save(output_path_gif, writer='pillow', fps=2)
            print(f"Saved as GIF to {output_path_gif}")

        plt.close()


if __name__ == "__main__":
    # Demo
    from evolution import GraphEvolutionSimulator

    print("Creating topology evolution visualization demo...")

    config = EvolutionConfig(
        pruning_strategy=PruningStrategy.COMBINED,
        grafting_strategy=GraftingStrategy.HEURISTIC
    )
    graph = AgentGraph(num_agents=20, config=config)

    visualizer = TopologyEvolutionVisualizer(graph)

    # Run evolution and take snapshots
    simulator = GraphEvolutionSimulator(graph)

    for gen in range(10):
        events = simulator.run_generation()

        # Create evolution events from pruning/grafting
        evolution_events = []

        # This would be populated by the actual simulator
        # For demo, we'll create placeholder events

        visualizer.take_snapshot(gen, evolution_events)

    # Generate visualizations
    output_dir = Path("../../reports/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    visualizer.visualize_evolution_timeline(output_dir / "evolution_timeline.png")

    if len(visualizer.snapshots) >= 2:
        visualizer.visualize_before_after(
            visualizer.snapshots[0].generation,
            visualizer.snapshots[-1].generation,
            output_dir / "evolution_before_after.png"
        )

    # Create animations
    visualizer.create_evolution_animation(
        output_dir / "topology_evolution.mp4"
    )

    visualizer.create_degree_distribution_animation(
        output_dir / "degree_distribution_evolution.mp4"
    )

    print("Topology evolution visualizations complete!")
