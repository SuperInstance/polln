"""
Master Orchestrator for Topology Optimization

Runs all topology simulations and generates comprehensive catalogs.
This is the main entry point for discovering optimal topologies.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time

from topology_generator import TopologyGenerator, TopologyType, TopologyParams, generate_benchmark_topologies
from topology_evaluator import TopologyEvaluator, TopologyMetrics
from workload_modeling import WorkloadGenerator, generate_benchmark_workloads, WorkloadConfig
from topology_optimizer import TopologyOptimizer, ScenarioOptimizer, optimize_for_colony_sizes
from template_generator import TemplateGenerator, TypeScriptExporter, generate_default_templates


class TopologySimulationOrchestrator:
    """Orchestrate entire topology optimization pipeline."""

    def __init__(self, output_dir: str = "output", seed: int = 42):
        """Initialize orchestrator."""
        self.output_dir = Path(output_dir)
        self.seed = seed

        # Create output directories
        self.topologies_dir = self.output_dir / "topologies"
        self.metrics_dir = self.output_dir / "metrics"
        self.results_dir = self.output_dir / "results"
        self.templates_dir = self.output_dir / "templates"

        for dir_path in [self.topologies_dir, self.metrics_dir,
                         self.results_dir, self.templates_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.generator = TopologyGenerator(seed=seed)
        self.evaluator = TopologyEvaluator(parallel=True)
        self.template_gen = TemplateGenerator()
        self.exporter = TypeScriptExporter()

    def run_full_pipeline(self,
                         colony_sizes: List[int] = [10, 50, 100, 500, 1000],
                         iterations: int = 50) -> Dict[str, any]:
        """Run complete topology optimization pipeline."""
        print("="*70)
        print("POLLN TOPOLOGY OPTIMIZATION PIPELINE")
        print("="*70)

        results = {
            'metadata': {
                'colony_sizes': colony_sizes,
                'iterations': iterations,
                'seed': self.seed,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        # Phase 1: Generate baseline topologies
        print("\n[PHASE 1] Generating baseline topologies...")
        baseline_results = self._generate_baseline_topologies(colony_sizes)
        results['baseline'] = baseline_results

        # Phase 2: Evaluate all topologies
        print("\n[PHASE 2] Evaluating topologies...")
        evaluation_results = self._evaluate_topologies(baseline_results)
        results['evaluations'] = evaluation_results

        # Phase 3: Optimize for workloads
        print("\n[PHASE 3] Optimizing for workloads...")
        optimization_results = self._optimize_for_workloads(colony_sizes, iterations)
        results['optimizations'] = optimization_results

        # Phase 4: Generate templates
        print("\n[PHASE 4] Generating production templates...")
        template_results = self._generate_templates(optimization_results)
        results['templates'] = template_results

        # Phase 5: Generate catalog
        print("\n[PHASE 5] Generating topology catalog...")
        catalog = self._generate_catalog(results)
        results['catalog'] = catalog

        # Save results
        self._save_results(results)

        print("\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)

        return results

    def _generate_baseline_topologies(self, colony_sizes: List[int]) -> Dict:
        """Generate baseline topologies for all colony sizes."""
        results = {}

        for size in colony_sizes:
            print(f"\n  Generating topologies for size {size}...")

            size_dir = self.topologies_dir / str(size)
            size_dir.mkdir(exist_ok=True)

            topologies = generate_benchmark_topologies(size, seed=self.seed)
            results[size] = {}

            for name, (G, topo_type, params) in topologies.items():
                # Export topology
                graphml_path = size_dir / f"{name}.graphml"
                json_path = size_dir / f"{name}.json"

                self.generator.export_graphml(G, str(graphml_path))
                self.generator.export_json(G, str(json_path), topo_type, params)

                results[size][name] = {
                    'type': topo_type.value,
                    'params': params.__dict__,
                    'num_nodes': G.number_of_nodes(),
                    'num_edges': G.number_of_edges(),
                    'files': {
                        'graphml': str(graphml_path),
                        'json': str(json_path)
                    }
                }

                print(f"    {name}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        return results

    def _evaluate_topologies(self, baseline_results: Dict) -> Dict:
        """Evaluate all generated topologies."""
        results = {}

        for size, topologies in baseline_results.items():
            print(f"\n  Evaluating topologies for size {size}...")

            size_dir = self.metrics_dir / str(size)
            size_dir.mkdir(exist_ok=True)

            results[size] = {}

            for name, topology_data in topologies.items():
                # Load topology
                G, topo_type, params = self.generator.load_json(topology_data['files']['json'])

                # Evaluate
                metrics = self.evaluator.evaluate(G)

                # Save metrics
                metrics_path = size_dir / f"{name}_metrics.json"
                self.evaluator.export_metrics(metrics, str(metrics_path))

                results[size][name] = {
                    'metrics_file': str(metrics_path),
                    'avg_path_length': metrics.avg_path_length,
                    'clustering_coefficient': metrics.clustering_coefficient,
                    'global_efficiency': metrics.global_efficiency,
                    'attack_tolerance': metrics.attack_tolerance,
                    'edge_cost': metrics.edge_cost,
                }

                print(f"    {name}: Score={self.evaluator.calculate_score(metrics):.3f}")

        return results

    def _optimize_for_workloads(self, colony_sizes: List[int], iterations: int) -> Dict:
        """Optimize topologies for different workloads."""
        workload_configs = generate_benchmark_workloads()

        scenario_optimizer = ScenarioOptimizer(
            colony_sizes=colony_sizes,
            workload_configs=workload_configs,
            seed=self.seed
        )

        results = scenario_optimizer.optimize_all_scenarios(
            iterations_per_scenario=iterations
        )

        # Generate recommendations
        recommendations = scenario_optimizer.generate_recommendations(results)

        # Save detailed results
        results_dir = self.results_dir / "optimizations"
        results_dir.mkdir(exist_ok=True)

        for scenario, scenario_results in results.items():
            scenario_file = results_dir / f"{scenario}.json"

            # Convert to serializable format
            serializable_results = []
            for result in scenario_results[:10]:  # Top 10
                serializable_results.append({
                    'topology_type': result.topology_type.value,
                    'params': result.params.__dict__,
                    'score': result.score,
                    'pareto_rank': result.pareto_rank,
                    'metrics': {
                        'avg_path_length': result.metrics.avg_path_length,
                        'clustering_coefficient': result.metrics.clustering_coefficient,
                        'global_efficiency': result.metrics.global_efficiency,
                        'attack_tolerance': result.metrics.attack_tolerance,
                        'edge_cost': result.metrics.edge_cost,
                    }
                })

            with open(scenario_file, 'w') as f:
                json.dump(serializable_results, f, indent=2)

        return {
            'recommendations': {
                scenario: {
                    'topology_type': rec.topology_type.value,
                    'score': rec.score,
                    'params': rec.params.__dict__,
                }
                for scenario, rec in recommendations.items()
            }
        }

    def _generate_templates(self, optimization_results: Dict) -> Dict:
        """Generate production templates from optimization results."""
        # Generate default templates
        templates = generate_default_templates()

        # Export to TypeScript
        typescript_dir = "../../src/core/topology/templates"
        self.exporter.export_templates(templates, typescript_dir)

        # Export JSON
        templates_file = self.templates_dir / "templates.json"
        templates_data = {name: template.__dict__ for name, template in templates.items()}

        with open(templates_file, 'w') as f:
            json.dump(templates_data, f, indent=2)

        return {
            'typescript_dir': typescript_dir,
            'json_file': str(templates_file),
            'templates': list(templates.keys())
        }

    def _generate_catalog(self, results: Dict) -> Dict:
        """Generate comprehensive topology catalog."""
        catalog = {
            'colony_sizes': results['metadata']['colony_sizes'],
            'topology_types': [
                'erdos_renyi',
                'watts_strogatz',
                'barabasi_albert',
                'modular',
                'two_tier',
                'three_tier',
                'hierarchical',
                'hybrid_small_world_sf'
            ],
            'workload_patterns': [
                'uniform_point_to_point',
                'hotspot_aggregation',
                'hierarchical_broadcast',
                'locality_gossip',
                'bursty_multicast'
            ],
            'recommendations': results['templates'],
            'baseline_results': results['evaluations'],
            'optimization_results': results['optimizations']
        }

        # Save catalog
        catalog_file = self.output_dir / "TOPOLOGY_CATALOG.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)

        return catalog

    def _save_results(self, results: Dict) -> None:
        """Save complete results."""
        results_file = self.output_dir / "complete_results.json"

        # Convert to serializable format
        serializable = self._make_serializable(results)

        with open(results_file, 'w') as f:
            json.dump(serializable, f, indent=2)

        print(f"\nResults saved to {results_file}")

    def _make_serializable(self, obj) -> any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)

    def generate_quick_report(self, results: Dict) -> str:
        """Generate quick summary report."""
        report = []
        report.append("="*70)
        report.append("TOPOLOGY OPTIMIZATION SUMMARY REPORT")
        report.append("="*70)
        report.append("")

        # Metadata
        report.append("Metadata:")
        report.append(f"  Colony Sizes: {results['metadata']['colony_sizes']}")
        report.append(f"  Iterations: {results['metadata']['iterations']}")
        report.append(f"  Timestamp: {results['metadata']['timestamp']}")
        report.append("")

        # Baseline results
        report.append("Baseline Topologies:")
        for size, topologies in results['baseline'].items():
            report.append(f"  Size {size}:")
            for name, data in topologies.items():
                report.append(f"    {name}: {data['num_edges']} edges")
        report.append("")

        # Top performers
        report.append("Top Performers by Size:")
        for size, evaluations in results['evaluations'].items():
            sorted_topos = sorted(evaluations.items(),
                                 key=lambda x: x[1].get('avg_path_length', 999))

            if sorted_topos:
                best_name, best_data = sorted_topos[0]
                report.append(f"  Size {size}: {best_name}")
                report.append(f"    Avg Path Length: {best_data['avg_path_length']:.3f}")
                report.append(f"    Clustering: {best_data['clustering_coefficient']:.3f}")
        report.append("")

        # Templates generated
        report.append("Templates Generated:")
        for template_name in results['templates'].get('templates', []):
            report.append(f"  - {template_name}")
        report.append("")

        report.append("="*70)

        return '\n'.join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="POLLN Topology Optimization Simulator"
    )

    parser.add_argument(
        '--sizes',
        type=int,
        nargs='+',
        default=[10, 50, 100, 500, 1000],
        help="Colony sizes to simulate"
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=50,
        help="Iterations per optimization scenario"
    )

    parser.add_argument(
        '--output',
        type=str,
        default="output",
        help="Output directory"
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help="Random seed"
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help="Quick run with reduced iterations"
    )

    args = parser.parse_args()

    # Adjust for quick run
    if args.quick:
        args.sizes = [10, 50, 100]
        args.iterations = 10
        print("Running in quick mode...")

    # Run orchestrator
    orchestrator = TopologySimulationOrchestrator(
        output_dir=args.output,
        seed=args.seed
    )

    results = orchestrator.run_full_pipeline(
        colony_sizes=args.sizes,
        iterations=args.iterations
    )

    # Print report
    print("\n")
    report = orchestrator.generate_quick_report(results)
    print(report)

    print(f"\nFull results saved to: {args.output}/")


if __name__ == "__main__":
    main()
