# POLLN Visualization Guide

Complete guide to creating and interpreting POLLN visualizations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Graph Visualizations](#graph-visualizations)
3. [Learning Analysis](#learning-analysis)
4. [Emergence Detection](#emergence-detection)
5. [Real-Time Monitoring](#real-time-monitoring)
6. [Configuration Comparison](#configuration-comparison)
7. [Best Practices](#best-practices)
8. [Interpreting Results](#interpreting-results)

## Getting Started

### Quick Start

```python
from graph_visualizer import GraphVisualizer
from base import AgentGraph, EvolutionConfig

# Create a sample graph
config = EvolutionConfig(
    pruning_strategy="combined",
    grafting_strategy="heuristic"
)
graph = AgentGraph(num_agents=20, config=config)

# Visualize
viz = GraphVisualizer(graph)
viz.visualize_matplotlib("my_graph.png")
```

### Installation

```bash
cd simulations/tooling/viz
pip install -r requirements.txt
```

## Graph Visualizations

### Understanding Graph Topology

**What it shows**: The structure of connections between agents

**Key metrics**:
- **Degree Centrality**: How connected an agent is
- **Betweenness Centrality**: How often an agent lies on shortest paths
- **Clustering Coefficient**: How connected an agent's neighbors are
- **Modularity**: How well the graph divides into communities

### Layout Options

| Layout | Best For | Notes |
|--------|----------|-------|
| `spring` | General use | Force-directed, minimizes edge crossings |
| `circular` | Small graphs | Agents arranged in circle |
| `kamada_kawai` | Community detection | Minimizes stress in layout |
| `spectral` | Large graphs | Fast, based on eigenvectors |

### Coloring Schemes

```python
# By community (detects groups)
viz.visualize_matplotlib("graph.png", color_by="community")

# By degree (shows influence)
viz.visualize_matplotlib("graph.png", color_by="degree")

# By value function (shows success)
viz.visualize_matplotlib("graph.png", color_by="value")

# By activation (shows activity)
viz.visualize_matplotlib("graph.png", color_by="activation")
```

### Interactive Graphs

```python
# Generate D3.js interactive visualization
viz.visualize_interactive("graph.html")

# Features:
# - Drag nodes to rearrange
# - Zoom and pan
# - Hover for agent details
# - Filter by community
```

## Learning Analysis

### TD(λ) Learning Curves

**What they show**: How the value function improves over time

**Key patterns**:
- **Converging curve**: Learning is stabilizing
- **Oscillations**: High exploration or unstable learning
- **Plateau**: Local optimum or insufficient exploration

**Interpreting TD Error**:
- Decreasing = Learning is working
- Stable at low value = Converged
- Increasing = Diverging (bad!)

### VAE Loss Curves

**What they show**: World model training progress

**Components**:
- **Reconstruction Loss**: How well VAE reconstructs input
- **KL Divergence**: How well latent distribution matches prior
- **Total Loss**: Combined metric

**Good signs**:
- Both metrics decreasing
- Stable convergence
- Reconstruction loss < 0.2

### Performance Metrics

```python
# Generate comprehensive learning summary
viz.plot_learning_summary("summary.png")

# Shows:
# - Value predictions over time
# - TD error trends
# - Reward accumulation
# - Success rate
# - Learning statistics
```

## Emergence Detection

### Pressure Maps

**What they show**: Influence/activation gradients across agents

**Interpretation**:
- **High pressure (red)**: High influence, often central agents
- **Low pressure (blue)**: Peripheral or inactive agents
- **Gradients**: Direction of information flow

**Use cases**:
- Identify bottlenecks
- Find critical agents
- Detect load imbalances

### Flow Patterns

**What they show**: Information flow between agents

**Arrow size**: Flow magnitude
**Arrow color**: Flow direction (green=positive, red=negative)

**Patterns to look for**:
- **Star patterns**: Central coordinator
- **Chain patterns**: Sequential processing
- **Mesh patterns**: Peer-to-peer coordination

### Synergy Metrics

| Metric | What it Measures | Good Range |
|--------|-----------------|------------|
| Mutual Information | Shared information | 0.3 - 0.7 |
| Integration | Global coherence | 0.2 - 0.6 |
| Segregation | Agent distinctness | 0.1 - 0.4 |
| Emergence Strength | Overall emergence | 0.5 - 0.9 |

**Phase transitions**: Sudden jumps in emergence strength indicate reorganization

## Real-Time Monitoring

### Dashboard Metrics

**Performance Metrics**:
- Throughput: Requests per second
- Latency: Average, P95, P99
- Error Rate: Percentage of failures

**Resource Metrics**:
- CPU Usage: Percentage
- Memory Usage: Percentage
- Network Usage: MB/s

**Agent Metrics**:
- Active Agents: Currently processing
- Queued Tasks: Waiting
- Avg Value: Recent performance

### Alert Thresholds

```python
from metrics_dashboard import AlertConfig

alerts = AlertConfig(
    avg_latency_threshold=500.0,     # ms
    p99_latency_threshold=1000.0,    # ms
    error_rate_threshold=5.0,        # percent
    cpu_threshold=90.0,              # percent
    memory_threshold=90.0,           # percent
    throughput_min=10.0              # req/s
)
```

### Exporting Dashboards

```python
# Live monitoring
dashboard.start()

# Export static HTML
dashboard.export_html("dashboard.html")

# Save snapshot
dashboard.save_snapshot("snapshot.png")
```

## Configuration Comparison

### Setting Up Comparisons

```python
from comparison_plotter import ComparisonPlotter, ComparisonConfig

plotter = ComparisonPlotter()

# Add configurations to compare
for config in configs:
    comp = ComparisonConfig(
        config_id="unique_id",
        display_name="Human Readable Name",
        config=config,
        metrics=metrics_list,
        final_performance=0.75,
        convergence_time=100,
        stability_score=0.65
    )
    plotter.add_comparison(comp)
```

### Comparison Visualizations

**Grouped Bar Charts**: Compare single metric across configs
**Heatmaps**: Compare multiple metrics simultaneously
**Radar Charts**: Compare multi-dimensional performance
**Statistical Tests**: Determine if differences are significant

### Statistical Analysis

```python
# Perform t-tests
results = plotter.perform_statistical_tests('clustering_coefficient')

# Check significance
for config_id, result in results.items():
    if result.significant:
        print(f"{config_id}: Significant (p={result.p_value:.4f})")
        print(f"  Effect size: {result.effect_size:.2f}")
```

## Best Practices

### For Research Papers

1. **Use high DPI**: `dpi=300` in configuration
2. **Vector graphics**: Use PDF output when possible
3. **Consistent styling**: Use same color scheme across figures
4. **Clear labels**: Include axis labels and legends
5. **Statistical rigor**: Include confidence intervals

### For Presentations

1. **High contrast**: Use distinct colors
2. **Large fonts**: `fontsize=14` or larger
3. **Simplified**: Remove unnecessary details
4. **Interactive**: Use HTML visualizations when possible
5. **Annotations**: Highlight key features

### For Monitoring

1. **Real-time updates**: 1-5 second refresh
2. **Alert thresholds**: Set based on baselines
3. **Historical context**: Show last N timesteps
4. **Trend indicators**: Show rate of change
5. **Actionable alerts**: Include remediation suggestions

### For Debugging

1. **Detailed logging**: Include timestamps and agent IDs
2. **Traceability**: Show causal chains
3. **State snapshots**: Save full state at key points
4. **Comparisons**: Compare before/after changes
5. **Animations**: Show evolution over time

## Interpreting Results

### Graph Metrics

| Metric | Low Value Means | High Value Means | Target |
|--------|----------------|------------------|--------|
| Clustering Coefficient | Random connections | Local clusters | 0.3 - 0.7 |
| Modularity | No communities | Strong communities | 0.4 - 0.8 |
| Path Length | Efficient communication | Slower propagation | 2 - 4 |
| Degree Assortativity | Disassortative | Assortative | -0.1 - 0.1 |

### Learning Indicators

**Healthy Learning**:
- Monotonically decreasing loss
- Stable TD error at low values
- Increasing success rate
- Converging value predictions

**Problematic Learning**:
- Oscillating metrics
- Diverging loss
- Decreasing success rate
- Unstable value predictions

### Emergence Patterns

**Weak Emergence**:
- Low mutual information
- Low integration
- High segregation
- Emergence strength < 0.3

**Strong Emergence**:
- High mutual information
- High integration
- Balanced segregation
- Emergence strength > 0.7

**Phase Transition**:
- Sudden jump in emergence strength
- Reorganization of communities
- Changes in flow patterns
- New synergies emerge

## Common Issues

### Issue: Graph is too dense to visualize

**Solution**: Filter edges by weight or use hierarchical layout
```python
# Keep only top 20% edges
threshold = np.percentile([G[u][v]['weight'] for u, v in G.edges()], 80)
G_filtered = G.edge_subgraph([(u, v) for u, v in G.edges() if G[u][v]['weight'] > threshold])
```

### Issue: Learning curves are noisy

**Solution**: Apply smoothing or aggregate multiple runs
```python
# Smooth curves
viz = LearningCurveVisualizer(
    style=CurveStyle(smooth_window=20)
)
```

### Issue: Dashboard is slow

**Solution**: Reduce history window or update frequency
```python
dashboard = MetricsDashboard(
    update_interval=5.0,      # Update every 5 seconds
    history_window=60         # Show only last 60 seconds
)
```

### Issue: Animations are too large

**Solution**: Reduce frame rate or resolution
```python
visualizer.create_emergence_animation(
    output_path="animation.mp4",
    num_frames=50,           # Fewer frames
    interval=200             # Slower playback
)
```

## Advanced Usage

### Custom Color Schemes

```python
import matplotlib.cm as cm

# Use custom colormap
config = GraphVisualizationConfig(
    node_color_scheme="plasma",
    edge_color_scheme="coolwarm"
)
```

### Custom Metrics

```python
# Define custom metric
def custom_metric(graph):
    # Your computation here
    return value

# Use in visualizations
metrics = [custom_metric(g) for g in graphs]
```

### Batch Processing

```python
from viz_generator import VisualizationGenerator

# Process multiple simulations
generator = VisualizationGenerator(
    data_dir="simulations/data",
    output_dir="reports/visualizations"
)

generator.generate_all(
    generate_graphs=True,
    generate_learning=True,
    generate_emergence=False,
    create_dashboard=True
)
```

## Resources

- [POLLN Documentation](../../README.md)
- [API Reference](README.md#api-reference)
- [Examples](../../examples/)
- [Research Papers](../../docs/research/)

## Support

For issues or questions:
- GitHub: https://github.com/SuperInstance/polln
- Documentation: https://docs.polln.ai
- Community: https://discord.gg/polln
