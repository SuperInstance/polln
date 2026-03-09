# POLLN Visualization Tools

Comprehensive visualization suite for understanding POLLN behavior and performance.

## Overview

The POLLN visualization tools provide interactive, publication-quality visualizations for analyzing agent communication graphs, learning progress, emergence patterns, and topology evolution.

## Installation

```bash
# Install dependencies
pip install numpy matplotlib seaborn networkx scipy scikit-learn pandas plotly

# Optional: For animations
pip install ffmpeg-python pillow

# Optional: For statistical analysis
pip install powerlaw
```

## Tools

### 1. Graph Visualizer (`graph_visualizer.py`)

Visualize agent communication graphs, colony topology, and community structure.

**Features:**
- Interactive D3.js force-directed graphs
- Community detection and visualization
- Multiple layout algorithms
- Communication flow diagrams
- Subsumption layer visualization

**Usage:**
```python
from graph_visualizer import GraphVisualizer, GraphVisualizationConfig
from base import AgentGraph, EvolutionConfig

# Create graph
config = EvolutionConfig()
graph = AgentGraph(num_agents=20, config=config)

# Create visualizer
viz_config = GraphVisualizationConfig(
    layout="spring",
    node_size_scale="degree",
    show_labels=True
)
visualizer = GraphVisualizer(graph, viz_config)

# Generate visualizations
visualizer.visualize_matplotlib("output/graph.png", color_by="community")
visualizer.visualize_interactive("output/graph.html")
```

### 2. Learning Curves (`learning_curves.py`)

Plot learning progress, TD(λ) convergence, VAE loss, and value predictions.

**Features:**
- TD(λ) learning curves
- VAE loss convergence plots
- Performance metrics tracking
- Multi-configuration comparisons
- Confidence intervals

**Usage:**
```python
from learning_curves import LearningCurveVisualizer, LearningMetrics

# Create visualizer
visualizer = LearningCurveVisualizer()

# Add metrics
for t in range(100):
    metrics = LearningMetrics(
        timestep=t,
        episode=t // 10,
        value_prediction=0.7 * (1 - np.exp(-t / 50)),
        # ... other metrics
    )
    visualizer.add_metrics(metrics)

# Generate plots
visualizer.plot_td_learning("output/td_learning.png")
visualizer.plot_vae_loss("output/vae_loss.png")
visualizer.plot_learning_summary("output/summary.png")
```

### 3. Metrics Dashboard (`metrics_dashboard.py`)

Real-time metrics dashboard for monitoring POLLN system metrics.

**Features:**
- Auto-refresh display
- Live throughput, latency, error rates
- Resource usage monitoring
- Historical comparison views
- Alert system for anomalies

**Usage:**
```python
from metrics_dashboard import MetricsDashboard, SystemMetrics

# Create dashboard
dashboard = MetricsDashboard(
    update_interval=1.0,
    history_window=300
)

# Set metrics callback
def fetch_metrics():
    return SystemMetrics(
        timestamp=time.time(),
        throughput=50.0,
        avg_latency=100.0,
        # ... other metrics
    )

dashboard.set_metrics_callback(fetch_metrics)

# Start dashboard
dashboard.start()

# Export HTML dashboard
dashboard.export_html("output/dashboard.html")
```

### 4. Emergence Visualizer (`emergence_visualizer.py`)

Visualize emergence detection, pressure maps, flow patterns, and synergy metrics.

**Features:**
- Pressure map heatmaps
- Information flow patterns
- Synergy metric visualization
- Phase transition detection
- Time-lapse animations

**Usage:**
```python
from emergence_visualizer import EmergenceVisualizer

# Create visualizer
visualizer = EmergenceVisualizer(graph)

# Detect emergence
metrics = visualizer.detect_emergence()

# Generate visualizations
visualizer.visualize_pressure_map("output/pressure_map.png")
visualizer.visualize_flow_patterns("output/flow_patterns.png")
visualizer.visualize_synergy_metrics("output/synergy.png")

# Create animation
visualizer.create_emergence_animation("output/emergence.mp4")
```

### 5. Topology Evolution (`topology_evolution.py`)

Animate and visualize graph topology changes over time.

**Features:**
- Animated graph evolution
- Before/after comparisons
- Metrics over time
- Pruning/grafting event highlights
- Degree distribution evolution

**Usage:**
```python
from topology_evolution import TopologyEvolutionVisualizer

# Create visualizer
visualizer = TopologyEvolutionVisualizer(graph)

# Take snapshots during evolution
for gen in range(10):
    events = simulator.run_generation()
    visualizer.take_snapshot(gen, events)

# Generate visualizations
visualizer.visualize_evolution_timeline("output/timeline.png")
visualizer.visualize_before_after(0, 9, "output/before_after.png")

# Create animation
visualizer.create_evolution_animation("output/evolution.mp4")
```

### 6. Comparison Plotter (`comparison_plotter.py`)

Compare multiple configurations, algorithms, and parameter settings.

**Features:**
- Grouped bar charts
- Heatmaps
- Radar charts
- Statistical comparisons
- Publication-quality reports

**Usage:**
```python
from comparison_plotter import ComparisonPlotter, ComparisonConfig

# Create plotter
plotter = ComparisonPlotter()

# Add configurations
for i in range(3):
    config = ComparisonConfig(
        config_id=f"config_{i}",
        display_name=f"Configuration {i+1}",
        config=evolution_config,
        metrics=metrics_list,
        final_performance=0.7 + i * 0.1,
        convergence_time=100 - i * 10,
        stability_score=0.6 + i * 0.1
    )
    plotter.add_comparison(config)

# Generate comparison plots
plotter.plot_grouped_bar_chart('clustering_coefficient')
plotter.plot_heatmap(['total_edges', 'avg_degree', 'clustering_coefficient'])
plotter.plot_radar_chart(['total_edges', 'avg_degree', 'clustering'])
plotter.generate_comparison_report("output/comparison_report.html")
```

### 7. Visualization Generator (`viz_generator.py`)

Master visualization generator that runs all tools and creates comprehensive reports.

**Usage:**
```bash
# Generate all visualizations
python viz_generator.py --data-dir simulations/data --output-dir reports/visualizations

# Skip specific visualizations
python viz_generator.py --data-dir simulations/data --output-dir reports/visualizations \
    --no-evolution --no-comparison

# Skip dashboard
python viz_generator.py --data-dir simulations/data --output-dir reports/visualizations \
    --no-dashboard
```

## Output Structure

```
reports/visualizations/
├── graph_topology.html         # Interactive D3.js graph
├── graph_topology.png          # Static graph visualization
├── learning_curves.png         # Learning progress
├── metrics_dashboard.html      # Real-time dashboard
├── pressure_map.png            # Emergence pressure map
├── flow_patterns.png           # Information flow
├── synergy_metrics.png         # Synergy over time
├── emergence_animation.mp4     # Emergence animation
├── topology_evolution.mp4      # Graph evolution
├── comparison_report.html      # Scenario comparison
└── comprehensive_dashboard.html # All visualizations
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest test_viz.py -v

# Run specific test class
pytest test_viz.py::TestGraphVisualizer -v

# Run demonstration
python test_viz.py --demo
```

## Examples

See the `examples/` directory for complete examples:

- `basic_graph_viz.py` - Basic graph visualization
- `learning_analysis.py` - Learning curve analysis
- `emergence_detection.py` - Emergence visualization
- `config_comparison.py` - Configuration comparison

## API Reference

### GraphVisualizationConfig

```python
@dataclass
class GraphVisualizationConfig:
    layout: str = "spring"              # spring, circular, kamada_kawai, etc.
    node_size_base: int = 500
    node_size_scale: str = "degree"     # degree, value, activation
    node_color_scheme: str = "viridis"
    edge_width_base: float = 1.0
    show_labels: bool = True
    show_clusters: bool = True
    dpi: int = 150
    figure_size: Tuple[int, int] = (16, 12)
```

### CurveStyle

```python
@dataclass
class CurveStyle:
    line_width: float = 2.0
    alpha: float = 0.8
    smooth_window: int = 10
    show_confidence: bool = True
    color_palette: str = "husl"
```

### SystemMetrics

```python
@dataclass
class SystemMetrics:
    timestamp: float
    throughput: float
    avg_latency: float
    p95_latency: float
    p99_latency: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    active_agents: int
    avg_value: float
    # ... and more
```

## Tips

1. **For publication-quality plots**: Set `dpi=300` in configuration
2. **For interactive exploration**: Use D3.js HTML visualizations
3. **For monitoring**: Use the real-time metrics dashboard
4. **For presentations**: Use the comprehensive dashboard
5. **For analysis**: Export data to CSV and use external tools

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the `simulations/` directory:

```bash
cd simulations/tooling/viz
python graph_visualizer.py
```

### Missing Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

### Animation Export Issues

If MP4 export fails, ensure ffmpeg is installed:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

The visualizer will fall back to GIF export if MP4 fails.

## Contributing

To add new visualization tools:

1. Create a new file in `simulations/tooling/viz/`
2. Follow the existing patterns for configuration and output
3. Add tests to `test_viz.py`
4. Update this README

## License

MIT License - See LICENSE file for details.
