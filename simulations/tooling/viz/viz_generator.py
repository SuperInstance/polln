"""
POLLN Visualization Generator
==============================

Master visualization generator that runs all visualization tools
and creates a comprehensive dashboard.

Usage:
    python viz_generator.py --data-dir <path> --output-dir <path>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """
    Master visualization generator for POLLN.

    Runs all visualization tools and creates comprehensive reports.
    """

    def __init__(self, data_dir: Path, output_dir: Path):
        """
        Initialize generator.

        Args:
            data_dir: Directory containing simulation data
            output_dir: Directory to save visualizations
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories for different visualizations
        self.graphs_dir = self.output_dir / "graphs"
        self.learning_dir = self.output_dir / "learning"
        self.metrics_dir = self.output_dir / "metrics"
        self.emergence_dir = self.output_dir / "emergence"
        self.evolution_dir = self.output_dir / "evolution"
        self.comparison_dir = self.output_dir / "comparison"

        for dir_path in [self.graphs_dir, self.learning_dir, self.metrics_dir,
                        self.emergence_dir, self.evolution_dir, self.comparison_dir]:
            dir_path.mkdir(exist_ok=True)

        # Track generated files
        self.generated_files: List[Path] = []

        logger.info(f"Visualization Generator initialized")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Output directory: {self.output_dir}")

    def discover_data_files(self) -> Dict[str, List[Path]]:
        """
        Discover data files in the data directory.

        Returns:
            Dictionary mapping data type to list of files
        """
        discovered = {
            'metrics': [],
            'graphs': [],
            'learning': [],
            'emergence': [],
            'comparisons': []
        }

        # Look for JSON files
        for json_file in self.data_dir.rglob("*.json"):
            filename = json_file.stem.lower()

            if 'metrics' in filename or 'evolution' in filename:
                discovered['metrics'].append(json_file)
            elif 'graph' in filename or 'topology' in filename:
                discovered['graphs'].append(json_file)
            elif 'learning' in filename or 'value' in filename or 'vae' in filename:
                discovered['learning'].append(json_file)
            elif 'emergence' in filename or 'synergy' in filename:
                discovered['emergence'].append(json_file)
            elif 'comparison' in filename:
                discovered['comparisons'].append(json_file)

        logger.info(f"Discovered data files:")
        for data_type, files in discovered.items():
            logger.info(f"  {data_type}: {len(files)} files")

        return discovered

    def generate_all(self,
                    generate_graphs: bool = True,
                    generate_learning: bool = True,
                    generate_emergence: bool = True,
                    generate_evolution: bool = True,
                    generate_comparison: bool = True,
                    create_dashboard: bool = True) -> None:
        """
        Generate all visualizations.

        Args:
            generate_graphs: Whether to generate graph visualizations
            generate_learning: Whether to generate learning curves
            generate_emergence: Whether to generate emergence visualizations
            generate_evolution: Whether to generate topology evolution animations
            generate_comparison: Whether to generate comparison plots
            create_dashboard: Whether to create comprehensive dashboard
        """
        start_time = time.time()

        logger.info("Starting visualization generation...")

        # Discover data files
        data_files = self.discover_data_files()

        try:
            # Graph visualizations
            if generate_graphs:
                logger.info("Generating graph visualizations...")
                self._generate_graph_visualizations(data_files)

            # Learning curves
            if generate_learning:
                logger.info("Generating learning curves...")
                self._generate_learning_curves(data_files)

            # Emergence visualizations
            if generate_emergence:
                logger.info("Generating emergence visualizations...")
                self._generate_emergence_visualizations(data_files)

            # Evolution animations
            if generate_evolution:
                logger.info("Generating topology evolution animations...")
                self._generate_evolution_animations(data_files)

            # Comparison plots
            if generate_comparison:
                logger.info("Generating comparison plots...")
                self._generate_comparison_plots(data_files)

            # Comprehensive dashboard
            if create_dashboard:
                logger.info("Creating comprehensive dashboard...")
                self._create_comprehensive_dashboard()

            elapsed = time.time() - start_time
            logger.info(f"Visualization generation complete in {elapsed:.2f}s")
            logger.info(f"Generated {len(self.generated_files)} files")

            # Save summary
            self._save_summary()

        except Exception as e:
            logger.error(f"Error during visualization generation: {e}")
            raise

    def _generate_graph_visualizations(self, data_files: Dict[str, List[Path]]):
        """Generate graph topology visualizations."""
        try:
            from graph_visualizer import GraphVisualizer, visualize_graph_from_file
        except ImportError:
            logger.warning("graph_visualizer not available")
            return

        # Process metrics files
        for metrics_file in data_files['metrics'][:5]:  # Limit to 5 for demo
            try:
                output_subdir = self.graphs_dir / metrics_file.stem
                output_subdir.mkdir(exist_ok=True)

                visualizer = visualize_graph_from_file(metrics_file, output_subdir)

                self.generated_files.extend(list(output_subdir.glob("*.png")))
                self.generated_files.extend(list(output_subdir.glob("*.html")))

            except Exception as e:
                logger.warning(f"Could not process {metrics_file}: {e}")

    def _generate_learning_curves(self, data_files: Dict[str, List[Path]]):
        """Generate learning curve visualizations."""
        try:
            from learning_curves import LearningCurveVisualizer
        except ImportError:
            logger.warning("learning_curves not available")
            return

        for learning_file in data_files['learning'][:5]:
            try:
                output_file = self.learning_dir / f"{learning_file.stem}_summary.png"

                visualizer = LearningCurveVisualizer.from_json(learning_file)
                visualizer.plot_learning_summary(output_file)

                self.generated_files.append(output_file)

            except Exception as e:
                logger.warning(f"Could not process {learning_file}: {e}")

    def _generate_emergence_visualizations(self, data_files: Dict[str, List[Path]]):
        """Generate emergence visualizations."""
        try:
            from emergence_visualizer import EmergenceVisualizer
        except ImportError:
            logger.warning("emergence_visualizer not available")
            return

        # This would require graph state, not just metrics
        # For now, skip if no graph data available
        logger.info("Emergence visualizations require graph state data")

    def _generate_evolution_animations(self, data_files: Dict[str, List[Path]]):
        """Generate topology evolution animations."""
        try:
            from topology_evolution import TopologyEvolutionVisualizer
        except ImportError:
            logger.warning("topology_evolution not available")
            return

        # This requires snapshot data
        logger.info("Evolution animations require snapshot data")

    def _generate_comparison_plots(self, data_files: Dict[str, List[Path]]):
        """Generate comparison plots."""
        try:
            from comparison_plotter import ComparisonPlotter
        except ImportError:
            logger.warning("comparison_plotter not available")
            return

        if not data_files['comparisons']:
            logger.info("No comparison data found")
            return

        # Generate comparison report
        try:
            # This would need actual comparison data loading
            logger.info("Comparison plots require comparison configuration")
        except Exception as e:
            logger.warning(f"Could not generate comparison plots: {e}")

    def _create_comprehensive_dashboard(self) -> None:
        """Create comprehensive HTML dashboard."""
        dashboard_path = self.output_dir / "comprehensive_dashboard.html"

        # Generate HTML dashboard
        html = self._generate_dashboard_html()

        with open(dashboard_path, 'w') as f:
            f.write(html)

        self.generated_files.append(dashboard_path)
        logger.info(f"Created comprehensive dashboard: {dashboard_path}")

    def _generate_dashboard_html(self) -> str:
        """Generate HTML for comprehensive dashboard."""
        # Count files in each directory
        file_counts = {
            'graphs': len(list(self.graphs_dir.glob("*"))) if self.graphs_dir.exists() else 0,
            'learning': len(list(self.learning_dir.glob("*"))) if self.learning_dir.exists() else 0,
            'emergence': len(list(self.emergence_dir.glob("*"))) if self.emergence_dir.exists() else 0,
            'evolution': len(list(self.evolution_dir.glob("*"))) if self.evolution_dir.exists() else 0,
            'comparison': len(list(self.comparison_dir.glob("*"))) if self.comparison_dir.exists() else 0,
        }

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POLLN Visualization Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }}

        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 14px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .card h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .file-list {{
            list-style: none;
        }}

        .file-list li {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}

        .file-list li:last-child {{
            border-bottom: none;
        }}

        .file-list a {{
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
        }}

        .file-list a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        .file-icon {{
            margin-right: 10px;
        }}

        .empty {{
            color: #999;
            font-style: italic;
        }}

        footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #666;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>POLLN Visualization Dashboard</h1>
            <p class="subtitle">Pattern-Organized Large Language Network - Comprehensive Analysis</p>
            <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(self.generated_files)}</div>
                    <div class="stat-label">Total Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{file_counts['graphs']}</div>
                    <div class="stat-label">Graph Visualizations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{file_counts['learning']}</div>
                    <div class="stat-label">Learning Curves</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{file_counts['emergence']}</div>
                    <div class="stat-label">Emergence Analyses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{file_counts['evolution']}</div>
                    <div class="stat-label">Evolution Animations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{file_counts['comparison']}</div>
                    <div class="stat-label">Comparisons</div>
                </div>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <h2>Graph Topology Visualizations</h2>
                {self._generate_file_list(self.graphs_dir)}
            </div>

            <div class="card">
                <h2>Learning Curves</h2>
                {self._generate_file_list(self.learning_dir)}
            </div>

            <div class="card">
                <h2>Emergence Analysis</h2>
                {self._generate_file_list(self.emergence_dir)}
            </div>

            <div class="card">
                <h2>Topology Evolution</h2>
                {self._generate_file_list(self.evolution_dir)}
            </div>

            <div class="card">
                <h2>Configuration Comparisons</h2>
                {self._generate_file_list(self.comparison_dir)}
            </div>

            <div class="card">
                <h2>About POLLN</h2>
                <p><strong>POLLN</strong> (Pattern-Organized Large Language Network) is a distributed intelligence system where simple, specialized agents produce intelligent behavior through emergent coordination.</p>
                <br>
                <p><strong>Key Features:</strong></p>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>Subsumption architecture for layered processing</li>
                    <li>Hebbian learning for adaptive connections</li>
                    <li>TD(λ) value networks for decision evaluation</li>
                    <li>Graph evolution for topology optimization</li>
                    <li>KV-cache communication for efficiency</li>
                </ul>
            </div>
        </div>

        <footer>
            <p>POLLN Visualization Dashboard | Generated by Visualization Generator</p>
            <p>Repository: https://github.com/SuperInstance/polln</p>
        </footer>
    </div>
</body>
</html>
"""

    def _generate_file_list(self, directory: Path) -> str:
        """Generate HTML file list for a directory."""
        if not directory.exists():
            return '<p class="empty">No files available</p>'

        files = sorted(directory.glob("*"))
        if not files:
            return '<p class="empty">No files available</p>'

        html = '<ul class="file-list">'

        for file in files:
            # Get relative path from output_dir
            rel_path = file.relative_to(self.output_dir)

            # Icon based on file type
            if file.suffix == '.png':
                icon = '🖼️'
            elif file.suffix == '.html':
                icon = '📄'
            elif file.suffix in ['.mp4', '.gif']:
                icon = '🎬'
            elif file.suffix == '.json':
                icon = '📊'
            else:
                icon = '📁'

            html += f'''
                <li>
                    <a href="{rel_path}" target="_blank">
                        <span class="file-icon">{icon}</span>
                        {file.name}
                    </a>
                </li>
            '''

        html += '</ul>'
        return html

    def _save_summary(self) -> None:
        """Save summary of generated files."""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'output_directory': str(self.output_dir),
            'generated_files': [str(f.relative_to(self.output_dir)) for f in self.generated_files],
            'total_files': len(self.generated_files)
        }

        summary_path = self.output_dir / "visualization_summary.json"

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Saved summary to {summary_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='POLLN Visualization Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        required=True,
        help='Directory containing simulation data'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports/visualizations',
        help='Directory to save visualizations'
    )

    parser.add_argument(
        '--no-graphs',
        action='store_true',
        help='Skip graph visualizations'
    )

    parser.add_argument(
        '--no-learning',
        action='store_true',
        help='Skip learning curves'
    )

    parser.add_argument(
        '--no-emergence',
        action='store_true',
        help='Skip emergence visualizations'
    )

    parser.add_argument(
        '--no-evolution',
        action='store_true',
        help='Skip evolution animations'
    )

    parser.add_argument(
        '--no-comparison',
        action='store_true',
        help='Skip comparison plots'
    )

    parser.add_argument(
        '--no-dashboard',
        action='store_true',
        help='Skip comprehensive dashboard'
    )

    args = parser.parse_args()

    # Create generator
    generator = VisualizationGenerator(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir)
    )

    # Generate visualizations
    generator.generate_all(
        generate_graphs=not args.no_graphs,
        generate_learning=not args.no_learning,
        generate_emergence=not args.no_emergence,
        generate_evolution=not args.no_evolution,
        generate_comparison=not args.no_comparison,
        create_dashboard=not args.no_dashboard
    )


if __name__ == "__main__":
    main()
