"""
POLLN Visualization Tools
========================

Comprehensive visualization suite for understanding POLLN behavior and performance.

Main modules:
- graph_visualizer: Agent graph visualization
- learning_curves: Learning progress visualization
- metrics_dashboard: Real-time metrics dashboard
- emergence_visualizer: Emergence detection visualization
- topology_evolution: Topology evolution animation
- comparison_plotter: Multi-scenario comparison
- viz_generator: Master visualization generator

Usage:
    from tooling.viz import GraphVisualizer, LearningCurveVisualizer

    viz = GraphVisualizer(graph)
    viz.visualize_matplotlib("output.png")
"""

__version__ = "0.1.0"

from .graph_visualizer import (
    GraphVisualizer,
    GraphVisualizationConfig,
    visualize_graph_from_file
)

from .learning_curves import (
    LearningCurveVisualizer,
    LearningMetrics,
    CurveStyle,
    generate_learning_curves_demo
)

from .metrics_dashboard import (
    MetricsDashboard,
    SystemMetrics,
    AlertConfig,
    Alert,
    MetricsBuffer,
    generate_synthetic_metrics
)

from .emergence_visualizer import (
    EmergenceVisualizer,
    EmergenceMetrics,
    PressureMap,
    FlowPattern
)

from .topology_evolution import (
    TopologyEvolutionVisualizer,
    EvolutionEvent,
    GraphSnapshot
)

from .comparison_plotter import (
    ComparisonPlotter,
    ComparisonConfig,
    StatisticalTest
)

from .viz_generator import VisualizationGenerator

__all__ = [
    # Graph Visualization
    'GraphVisualizer',
    'GraphVisualizationConfig',
    'visualize_graph_from_file',

    # Learning Curves
    'LearningCurveVisualizer',
    'LearningMetrics',
    'CurveStyle',
    'generate_learning_curves_demo',

    # Metrics Dashboard
    'MetricsDashboard',
    'SystemMetrics',
    'AlertConfig',
    'Alert',
    'MetricsBuffer',
    'generate_synthetic_metrics',

    # Emergence Visualization
    'EmergenceVisualizer',
    'EmergenceMetrics',
    'PressureMap',
    'FlowPattern',

    # Topology Evolution
    'TopologyEvolutionVisualizer',
    'EvolutionEvent',
    'GraphSnapshot',

    # Comparison Plotting
    'ComparisonPlotter',
    'ComparisonConfig',
    'StatisticalTest',

    # Master Generator
    'VisualizationGenerator',
]
