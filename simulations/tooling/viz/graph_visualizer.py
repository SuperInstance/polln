"""
POLLN Graph Visualizer
======================

Interactive visualization of agent communication graphs, colony topology,
and community structure.

Features:
- Zoom, pan, filter capabilities
- Highlight communication paths
- Interactive D3.js HTML visualizations
- Community detection visualization
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, List, Set, Tuple, Optional, Any
import json
from pathlib import Path
from dataclasses import dataclass, asdict
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from base import AgentGraph, EvolutionMetrics, EvolutionConfig


@dataclass
class GraphVisualizationConfig:
    """Configuration for graph visualization."""
    # Layout algorithm
    layout: str = "spring"  # spring, circular, kamada_kawai, spectral, random
    layout_iterations: int = 50

    # Node styling
    node_size_base: int = 500
    node_size_scale: str = "degree"  # degree, value, activation, none
    node_color_scheme: str = "viridis"  # viridis, plasma, inferno, magma

    # Edge styling
    edge_width_base: float = 1.0
    edge_width_scale: str = "weight"  # weight, activity, none
    edge_opacity: float = 0.6
    edge_color_scheme: str = "coolwarm"

    # Labels
    show_labels: bool = True
    label_font_size: int = 8
    label_color: str = "black"

    # Clustering
    show_clusters: bool = True
    cluster_outline_width: int = 2

    # Interactive features
    enable_zoom: bool = True
    enable_pan: bool = True
    enable_tooltip: bool = True

    # Output
    dpi: int = 150
    figure_size: Tuple[int, int] = (16, 12)
    background_color: str = "white"


class GraphVisualizer:
    """
    Interactive visualization of POLLN agent graphs.

    Supports both static matplotlib plots and interactive D3.js visualizations.
    """

    def __init__(self, graph: AgentGraph, config: Optional[GraphVisualizationConfig] = None):
        self.graph = graph
        self.config = config or GraphVisualizationConfig()
        self.G = graph.graph

        # Compute network metrics for visualization
        self._compute_visualization_metrics()

    def _compute_visualization_metrics(self):
        """Pre-compute metrics for visualization styling."""
        # Degree centrality
        self.degree_centrality = nx.degree_centrality(self.G)

        # Betweenness centrality
        self.betweenness_centrality = nx.betweenness_centrality(self.G)

        # Closeness centrality
        self.closeness_centrality = nx.closeness_centrality(self.G)

        # PageRank
        self.pagerank = nx.pagerank(self.G)

        # Community detection (Louvain)
        try:
            import community as community_louvain
            self.communities = community_louvain.best_partition(self.G.to_undirected())
        except ImportError:
            # Fallback to label propagation
            self.communities = nx.community.label_propagation_communities(self.G.to_undirected())
            self.communities = {node: i for i, comm in enumerate(self.communities) for node in comm}

        # Strongly connected components
        self.sccs = list(nx.strongly_connected_components(self.G))

        # Node degrees
        self.degrees = dict(self.G.degree())

        # Edge betweenness
        self.edge_betweenness = nx.edge_betweenness_centrality(self.G)

    def _get_node_colors(self, color_by: str = "community") -> np.ndarray:
        """Get node colors based on specified metric."""
        if color_by == "community":
            # Color by community
            num_communities = len(set(self.communities.values()))
            cmap = plt.cm.get_cmap(self.config.node_color_scheme, num_communities)
            colors = np.array([cmap(self.communities[node]) for node in self.G.nodes()])
        elif color_by == "degree":
            # Color by degree centrality
            values = [self.degree_centrality[node] for node in self.G.nodes()]
            cmap = plt.cm.get_cmap(self.config.node_color_scheme)
            colors = cmap(values)
        elif color_by == "value":
            # Color by value function
            values = [self.graph.nodes[node].value_function for node in self.G.nodes()]
            cmap = plt.cm.get_cmap(self.config.node_color_scheme)
            # Normalize
            if max(values) > min(values):
                values = [(v - min(values)) / (max(values) - min(values)) for v in values]
            colors = cmap(values)
        elif color_by == "activation":
            # Color by average activation
            values = [self.graph.nodes[node].get_avg_activation() for node in self.G.nodes()]
            cmap = plt.cm.get_cmap(self.config.node_color_scheme)
            if max(values) > min(values):
                values = [(v - min(values)) / (max(values) - min(values)) for v in values]
            colors = cmap(values)
        else:
            # Default coloring
            colors = np.array([plt.cm.get_cmap(self.config.node_color_scheme)(0.5)
                             for _ in self.G.nodes()])

        return colors

    def _get_node_sizes(self) -> np.ndarray:
        """Get node sizes based on configuration."""
        if self.config.node_size_scale == "degree":
            sizes = np.array([self.degrees[node] for node in self.G.nodes()])
        elif self.config.node_size_scale == "value":
            sizes = np.array([self.graph.nodes[node].value_function for node in self.G.nodes()])
        elif self.config.node_size_scale == "activation":
            sizes = np.array([self.graph.nodes[node].get_avg_activation() for node in self.G.nodes()])
        else:
            sizes = np.ones(len(self.G.nodes()))

        # Scale and apply base size
        if sizes.max() > 0:
            sizes = (sizes / sizes.max()) * self.config.node_size_base * 2 + self.config.node_size_base
        else:
            sizes = np.full(len(sizes), self.config.node_size_base)

        return sizes

    def _get_edge_widths(self) -> np.ndarray:
        """Get edge widths based on configuration."""
        if self.config.edge_width_scale == "weight":
            widths = np.array([self.G[u][v].get('weight', 0.5) for u, v in self.G.edges()])
        elif self.config.edge_width_scale == "activity":
            widths = np.array([self.graph.edges.get((u, v), AgentEdge(u, v)).activity_level
                             if (u, v) in self.graph.edges else 0
                             for u, v in self.G.edges()])
        else:
            widths = np.ones(self.G.number_of_edges())

        # Scale
        if widths.max() > 0:
            widths = (widths / widths.max()) * 3 + 0.5

        return widths

    def _get_edge_colors(self) -> np.ndarray:
        """Get edge colors based on weights."""
        weights = [self.G[u][v].get('weight', 0.5) for u, v in self.G.edges()]
        cmap = plt.cm.get_cmap(self.config.edge_color_scheme)
        colors = cmap(weights)
        # Set alpha
        colors[:, 3] = self.config.edge_opacity
        return colors

    def visualize_matplotlib(self, output_path: Optional[Path] = None,
                            color_by: str = "community",
                            title: str = "POLLN Agent Graph") -> plt.Figure:
        """
        Create static matplotlib visualization.

        Args:
            output_path: Path to save figure
            color_by: How to color nodes (community, degree, value, activation)
            title: Figure title

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self.config.figure_size,
                              dpi=self.config.dpi)

        # Compute layout
        if self.config.layout == "spring":
            pos = nx.spring_layout(self.G, iterations=self.config.layout_iterations)
        elif self.config.layout == "circular":
            pos = nx.circular_layout(self.G)
        elif self.config.layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(self.G)
        elif self.config.layout == "spectral":
            pos = nx.spectral_layout(self.G)
        else:
            pos = nx.random_layout(self.G)

        # Get styling
        node_colors = self._get_node_colors(color_by)
        node_sizes = self._get_node_sizes()
        edge_widths = self._get_edge_widths()
        edge_colors = self._get_edge_colors()

        # Draw edges
        nx.draw_networkx_edges(self.G, pos,
                              width=edge_widths,
                              edge_color=edge_colors,
                              ax=ax,
                              alpha=self.config.edge_opacity)

        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              ax=ax,
                              alpha=0.9)

        # Draw labels
        if self.config.show_labels:
            nx.draw_networkx_labels(self.G, pos,
                                   font_size=self.config.label_font_size,
                                   font_color=self.config.label_color,
                                   ax=ax)

        # Draw cluster outlines if enabled
        if self.config.show_clusters and color_by == "community":
            self._draw_cluster_outlines(pos, ax)

        # Styling
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.axis('off')

        # Add legend
        self._add_legend(ax, color_by)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
            print(f"Saved visualization to {output_path}")

        return fig

    def _draw_cluster_outlines(self, pos: Dict, ax: plt.Axes):
        """Draw outlines around communities."""
        # Group nodes by community
        community_nodes = {}
        for node, comm_id in self.communities.items():
            if comm_id not in community_nodes:
                community_nodes[comm_id] = []
            community_nodes[comm_id].append(node)

        # Draw convex hull for each community
        from scipy.spatial import ConvexHull

        for comm_id, nodes in community_nodes.items():
            if len(nodes) >= 3:
                points = np.array([pos[node] for node in nodes])
                try:
                    hull = ConvexHull(points)
                    for simplex in hull.simplices:
                        ax.plot(points[simplex, 0], points[simplex, 1],
                               'k-', linewidth=self.config.cluster_outline_width,
                               alpha=0.3)
                except:
                    pass

    def _add_legend(self, ax: plt.Axes, color_by: str):
        """Add legend to plot."""
        if color_by == "community":
            # Community legend
            num_communities = len(set(self.communities.values()))
            cmap = plt.cm.get_cmap(self.config.node_color_scheme, num_communities)
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                         markerfacecolor=cmap(i),
                                         markersize=10,
                                         label=f'Community {i}')
                             for i in range(num_communities)]
            ax.legend(handles=legend_elements, loc='upper right',
                     title="Communities")

    def visualize_interactive(self, output_path: Path,
                            color_by: str = "community") -> str:
        """
        Create interactive D3.js visualization.

        Generates HTML file with D3.js force-directed graph.

        Args:
            output_path: Path to save HTML file
            color_by: How to color nodes

        Returns:
            HTML string
        """
        # Prepare data for D3.js
        nodes = []
        for node in self.G.nodes():
            node_data = {
                "id": node,
                "community": self.communities.get(node, 0),
                "degree": self.degrees.get(node, 0),
                "degree_centrality": self.degree_centrality.get(node, 0),
                "betweenness": self.betweenness_centrality.get(node, 0),
                "pagerank": self.pagerank.get(node, 0),
                "value": self.graph.nodes[node].value_function,
                "activation": self.graph.nodes[node].get_avg_activation(),
            }
            nodes.append(node_data)

        links = []
        for u, v in self.G.edges():
            link_data = {
                "source": u,
                "target": v,
                "weight": self.G[u][v].get('weight', 0.5),
                "betweenness": self.edge_betweenness.get((u, v), 0)
            }
            links.append(link_data)

        data = {
            "nodes": nodes,
            "links": links,
            "config": {
                "nodeSizeBase": self.config.node_size_base,
                "edgeWidthBase": self.config.edge_width_base,
                "colorScheme": self.config.node_color_scheme
            }
        }

        # Generate HTML
        html = self._generate_d3_html(data, color_by)

        # Save to file
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"Saved interactive visualization to {output_path}")
        return html

    def _generate_d3_html(self, data: Dict, color_by: str) -> str:
        """Generate D3.js HTML visualization."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLLN Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: {self.config.background_color};
        }}
        #graph {{
            width: 100vw;
            height: 100vh;
        }}
        .node {{
            stroke: #fff;
            stroke-width: 1.5px;
            cursor: pointer;
        }}
        .node:hover {{
            stroke: #000;
            stroke-width: 2.5px;
        }}
        .link {{
            stroke-opacity: {self.config.edge_opacity};
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            pointer-events: none;
            font-size: 12px;
        }}
        .controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .legend {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div id="graph"></div>

    <div class="controls">
        <label>
            <input type="checkbox" id="showLabels" checked>
            Show Labels
        </label><br>
        <label>
            <input type="checkbox" id="showCommunities" checked>
            Show Communities
        </label><br>
        <button id="resetZoom">Reset Zoom</button>
    </div>

    <div class="legend" id="legend"></div>

    <script>
        const data = {json.dumps(data)};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(d3.zoom().on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }}));

        const g = svg.append("g");

        const colorScale = d3.scaleSequential(d3.interpolateViridis)
            .domain([0, d3.max(data.nodes, d => d.community)]);

        const sizeScale = d3.scaleLinear()
            .domain([0, d3.max(data.nodes, d => d.degree)])
            .range([5, 20]);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links)
                .id(d => d.id)
                .distance(d => 100 / d.weight))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => sizeScale(d.degree) + 2));

        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", d => {{
                const weight = d.weight;
                return weight > 0.7 ? "#ff6b6b" : weight > 0.4 ? "#4ecdc4" : "#95a5a6";
            }})
            .attr("stroke-width", d => d.weight * 3);

        const node = g.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => sizeScale(d.degree))
            .attr("fill", d => colorScale(d.community))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = g.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .text(d => d.id)
            .attr("font-size", 10)
            .attr("dx", 12)
            .attr("dy", 4);

        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        node.on("mouseover", function(event, d) {{
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(`
                <strong>${d.id}</strong><br/>
                Community: ${{d.community}}<br/>
                Degree: ${{d.degree}}<br/>
                Value: ${{d.value.toFixed(3)}}<br/>
                Activation: ${{d.activation.toFixed(3)}}
            `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }}).on("mouseout", function(d) {{
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }});

        // Update legend
        const communities = [...new Set(data.nodes.map(d => d.community))];
        const legend = d3.select("#legend");
        legend.append("text").text("Communities:").style("font-weight", "bold");
        communities.forEach(comm => {{
            legend.append("div")
                .style("display", "flex")
                .style("align-items", "center")
                .html(`
                    <svg width="15" height="15">
                        <circle cx="7.5" cy="7.5" r="6" fill="${{colorScale(comm)}}"/>
                    </svg>
                    <span style="margin-left: 5px;">${{comm}}</span>
                `);
        }});

        // Controls
        d3.select("#showLabels").on("change", function() {{
            label.style("display", this.checked ? "block" : "none");
        }});

        d3.select("#resetZoom").on("click", function() {{
            svg.transition().duration(750).call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
        }});

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""

    def visualize_communication_flow(self, communication_log: List[Dict],
                                     output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize communication patterns as a flow diagram.

        Args:
            communication_log: List of communication events
            output_path: Path to save figure

        Returns:
            matplotlib Figure object
        """
        # Count communications between agents
        comm_counts = {}
        for comm in communication_log:
            key = (comm['source'], comm['target'])
            comm_counts[key] = comm_counts.get(key, 0) + 1

        # Create directed graph with communication weights
        G_comm = nx.DiGraph()
        for (source, target), count in comm_counts.items():
            G_comm.add_edge(source, target, weight=count)

        fig, ax = plt.subplots(figsize=(14, 10), dpi=self.config.dpi)

        # Layout
        pos = nx.spring_layout(G_comm, k=2, iterations=50)

        # Edge widths based on communication count
        edge_widths = [G_comm[u][v]['weight'] for u, v in G_comm.edges()]
        max_width = max(edge_widths) if edge_widths else 1
        edge_widths = [w / max_width * 5 for w in edge_widths]

        # Draw edges
        nx.draw_networkx_edges(G_comm, pos,
                              width=edge_widths,
                              edge_color='gray',
                              alpha=0.6,
                              ax=ax,
                              arrowsize=20,
                              arrowstyle='->,head_length=0.4,head_width=0.2')

        # Draw nodes
        nx.draw_networkx_nodes(G_comm, pos,
                              node_size=1000,
                              node_color='lightblue',
                              alpha=0.9,
                              ax=ax)

        # Draw labels
        nx.draw_networkx_labels(G_comm, pos,
                              font_size=10,
                              font_weight='bold',
                              ax=ax)

        # Add edge labels with counts
        edge_labels = {(u, v): f'{d["weight"]}' for u, v, d in G_comm.edges(data=True)}
        nx.draw_networkx_edge_labels(G_comm, pos,
                                     edge_labels=edge_labels,
                                     font_size=8,
                                     ax=ax)

        ax.set_title("POLLN Communication Flow", fontsize=16, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
            print(f"Saved communication flow to {output_path}")

        return fig

    def visualize_subsumption_layers(self, output_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize agents grouped by subsumption layer.

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(16, 10), dpi=self.config.dpi)

        # Group agents by layer (this would need layer info from agent state)
        # For now, create random assignment for demonstration
        layers = {
            'SAFETY': [],
            'REFLEX': [],
            'HABITUAL': [],
            'DELIBERATE': []
        }

        for node in self.G.nodes():
            # Random assignment for demo
            import random
            layer = random.choice(list(layers.keys()))
            layers[layer].append(node)

        # Position nodes by layer
        pos = {}
        layer_height = 3
        y_offset = 0

        for layer_name, nodes in layers.items():
            for i, node in enumerate(nodes):
                x = (i - len(nodes) / 2) * 2
                y = y_offset
                pos[node] = (x, y)
            y_offset += layer_height

        # Layer colors
        layer_colors = {
            'SAFETY': '#ff6b6b',
            'REFLEX': '#4ecdc4',
            'HABITUAL': '#45b7d1',
            'DELIBERATE': '#96ceb4'
        }

        # Draw edges
        nx.draw_networkx_edges(self.G, pos,
                              edge_color='gray',
                              alpha=0.3,
                              ax=ax,
                              arrows=True,
                              arrowsize=20)

        # Draw nodes by layer
        for layer_name, nodes in layers.items():
            nx.draw_networkx_nodes(self.G, pos,
                                  nodelist=nodes,
                                  node_color=layer_colors[layer_name],
                                  node_size=800,
                                  label=layer_name,
                                  alpha=0.9,
                                  ax=ax)

        # Draw labels
        nx.draw_networkx_labels(self.G, pos,
                              font_size=8,
                              ax=ax)

        # Add layer labels
        y_offset = 0
        for layer_name, nodes in layers.items():
            ax.text(-15, y_offset, layer_name,
                   fontsize=12, fontweight='bold',
                   verticalalignment='center')
            y_offset += layer_height

        ax.set_title("POLLN Subsumption Architecture", fontsize=16, fontweight='bold')
        ax.legend(loc='upper right')
        ax.axis('off')
        ax.set_xlim(-20, 20)
        ax.set_ylim(-2, 15)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
            print(f"Saved subsumption visualization to {output_path}")

        return fig


def visualize_graph_from_file(metrics_file: Path,
                               output_dir: Optional[Path] = None) -> GraphVisualizer:
    """
    Load graph from metrics file and create visualizations.

    Args:
        metrics_file: Path to JSON metrics file
        output_dir: Directory to save visualizations

    Returns:
        GraphVisualizer instance
    """
    import json

    with open(metrics_file, 'r') as f:
        data = json.load(f)

    # Recreate graph
    config = EvolutionConfig(
        pruning_strategy=data['config'].get('pruning_strategy', 'combined'),
        grafting_strategy=data['config'].get('grafting_strategy', 'heuristic'),
        pruning_threshold=data['config'].get('pruning_threshold', 0.05),
        max_pruning_rate=data['config'].get('max_pruning_rate', 0.1),
        grafting_probability=data['config'].get('grafting_probability', 0.01)
    )

    # Note: This would need the actual graph structure, not just metrics
    # For now, create a new graph with same number of agents
    num_agents = data['metrics'][-1]['total_nodes']
    graph = AgentGraph(num_agents, config)

    visualizer = GraphVisualizer(graph)

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate all visualizations
        visualizer.visualize_matplotlib(
            output_dir / "graph_topology.png",
            color_by="community"
        )

        visualizer.visualize_matplotlib(
            output_dir / "graph_by_degree.png",
            color_by="degree"
        )

        visualizer.visualize_matplotlib(
            output_dir / "graph_by_value.png",
            color_by="value"
        )

        visualizer.visualize_interactive(
            output_dir / "graph_topology.html"
        )

    return visualizer


if __name__ == "__main__":
    # Demo usage
    print("Creating demo graph visualization...")

    # Create sample graph
    config = EvolutionConfig(
        pruning_strategy=PruningStrategy.COMBINED,
        grafting_strategy=GraftingStrategy.HEURISTIC
    )
    graph = AgentGraph(num_agents=20, config=config)

    # Run some evolution to get interesting structure
    from evolution import GraphEvolutionSimulator
    simulator = GraphEvolutionSimulator(graph)
    simulator.run_generation()

    # Create visualizer
    viz = GraphVisualizer(graph)

    # Generate visualizations
    output_dir = Path("../../reports/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    viz.visualize_matplotlib(
        output_dir / "graph_topology.png",
        color_by="community",
        title="POLLN Agent Graph - Community Structure"
    )

    viz.visualize_interactive(
        output_dir / "graph_topology.html"
    )

    viz.visualize_subsumption_layers(
        output_dir / "subsumption_layers.png"
    )

    print("Graph visualizations complete!")
