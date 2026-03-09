"""
CLI Tool for Interactive Topology Generation

Provides interactive command-line interface for generating and
visualizing network topologies for POLLN agent colonies.
"""

import argparse
import sys
import json
from typing import Optional, List
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from topology_generator import (
    TopologyGenerator, TopologyType, TopologyParams,
    generate_benchmark_topologies
)
from topology_evaluator import TopologyEvaluator, TopologyMetrics
from workload_modeling import WorkloadGenerator, generate_benchmark_workloads


class TopologyCLI:
    """Interactive CLI for topology generation."""

    def __init__(self):
        """Initialize CLI."""
        self.generator = TopologyGenerator()
        self.evaluator = TopologyEvaluator()

    def run(self, args: List[str] = None) -> None:
        """Run CLI with given arguments."""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Execute command
        if hasattr(self, f'_cmd_{parsed_args.command}'):
            getattr(self, f'_cmd_{parsed_args.command}')(parsed_args)
        else:
            parser.print_help()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="POLLN Topology Generator CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Generate and visualize a topology
  python generate_topology.py generate -n 100 -t watts_strogatz -k 6 -p 0.1

  # Evaluate a topology
  python generate_topology.py evaluate -n 100 -t watts_strogatz -k 6 -p 0.1

  # Compare topologies
  python generate_topology.py compare -n 100

  # List available topologies
  python generate_topology.py list

  # Generate benchmark suite
  python generate_topology.py benchmark -n 100
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Command to run')

        # Generate command
        gen_parser = subparsers.add_parser('generate', help='Generate a topology')
        gen_parser.add_argument('-n', '--size', type=int, required=True,
                               help='Number of agents (nodes)')
        gen_parser.add_argument('-t', '--type',
                               choices=[t.value for t in TopologyType],
                               required=True,
                               help='Topology type')
        gen_parser.add_argument('-k', '--degree', type=int,
                               help='Mean degree')
        gen_parser.add_argument('-p', '--probability', type=float,
                               help='Rewiring/edge probability')
        gen_parser.add_argument('-m', '--edges-per-step', type=int,
                               help='Edges per step (for Barabasi-Albert)')
        gen_parser.add_argument('--modules', type=int,
                               help='Number of modules')
        gen_parser.add_argument('--levels', type=int,
                               help='Hierarchy levels')
        gen_parser.add_argument('-s', '--seed', type=int, default=42,
                               help='Random seed')
        gen_parser.add_argument('-o', '--output', type=str,
                               help='Output file (GraphML or JSON)')
        gen_parser.add_argument('-v', '--visualize', action='store_true',
                               help='Visualize topology')
        gen_parser.add_argument('--format', choices=['graphml', 'json'],
                               default='graphml',
                               help='Output format')

        # Evaluate command
        eval_parser = subparsers.add_parser('evaluate', help='Evaluate a topology')
        eval_parser.add_argument('-n', '--size', type=int, required=True,
                                help='Number of agents')
        eval_parser.add_argument('-t', '--type',
                                choices=[t.value for t in TopologyType],
                                required=True,
                                help='Topology type')
        eval_parser.add_argument('-k', '--degree', type=int,
                                help='Mean degree')
        eval_parser.add_argument('-p', '--probability', type=float,
                                help='Rewiring/edge probability')
        eval_parser.add_argument('-s', '--seed', type=int, default=42,
                                help='Random seed')

        # Compare command
        comp_parser = subparsers.add_parser('compare', help='Compare topologies')
        comp_parser.add_argument('-n', '--size', type=int, required=True,
                                help='Number of agents')
        comp_parser.add_argument('--topologies',
                                choices=[t.value for t in TopologyType],
                                nargs='+',
                                help='Topologies to compare')
        comp_parser.add_argument('-s', '--seed', type=int, default=42,
                                help='Random seed')

        # List command
        list_parser = subparsers.add_parser('list', help='List available topologies')

        # Benchmark command
        bench_parser = subparsers.add_parser('benchmark', help='Generate benchmark suite')
        bench_parser.add_argument('-n', '--size', type=int, required=True,
                                 help='Number of agents')
        bench_parser.add_argument('-s', '--seed', type=int, default=42,
                                 help='Random seed')
        bench_parser.add_argument('-o', '--output', type=str,
                                 help='Output directory')
        bench_parser.add_argument('-v', '--visualize', action='store_true',
                                 help='Visualize all topologies')

        # Recommend command
        rec_parser = subparsers.add_parser('recommend', help='Get topology recommendation')
        rec_parser.add_argument('-n', '--size', type=int, required=True,
                               help='Number of agents')
        rec_parser.add_argument('--efficiency', action='store_true',
                               help='Prioritize efficiency')
        rec_parser.add_argument('--robustness', action='store_true',
                               help='Prioritize robustness')
        rec_parser.add_argument('--low-cost', action='store_true',
                               help='Prioritize low cost')

        return parser

    def _cmd_generate(self, args: argparse.Namespace) -> None:
        """Generate topology command."""
        print(f"Generating {args.type} topology with {args.size} nodes...")

        # Create generator with seed
        generator = TopologyGenerator(seed=args.seed)

        # Build parameters
        params = TopologyParams(n=args.size, k=args.degree, p=args.probability,
                               m=args.edges_per_step, modules=args.modules,
                               levels=args.levels, seed=args.seed)

        # Generate topology
        try:
            G = generator.generate(TopologyType(args.type), params)

            print(f"  Generated: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

            # Save if output specified
            if args.output:
                if args.format == 'graphml':
                    generator.export_graphml(G, args.output)
                else:
                    generator.export_json(G, args.output, TopologyType(args.type), params)
                print(f"  Saved to {args.output}")

            # Visualize if requested
            if args.visualize:
                self._visualize_topology(G, args.type, args.size)

        except Exception as e:
            print(f"Error generating topology: {e}")
            sys.exit(1)

    def _cmd_evaluate(self, args: argparse.Namespace) -> None:
        """Evaluate topology command."""
        print(f"Evaluating {args.type} topology with {args.size} nodes...")

        # Generate topology
        generator = TopologyGenerator(seed=args.seed)
        params = TopologyParams(n=args.size, k=args.degree, p=args.probability, seed=args.seed)

        try:
            G = generator.generate(TopologyType(args.type), params)

            # Evaluate
            evaluator = TopologyEvaluator(parallel=False)
            metrics = evaluator.evaluate(G)

            # Print results
            print("\nTopology Metrics:")
            print(f"  Basic Properties:")
            print(f"    Nodes: {metrics.num_nodes}")
            print(f"    Edges: {metrics.num_edges}")
            print(f"    Avg Degree: {metrics.avg_degree:.2f}")
            print(f"    Density: {metrics.density:.4f}")

            print(f"\n  Path Metrics:")
            print(f"    Avg Path Length: {metrics.avg_path_length:.3f}")
            print(f"    Diameter: {metrics.diameter}")
            print(f"    Radius: {metrics.radius}")

            print(f"\n  Clustering:")
            print(f"    Clustering Coefficient: {metrics.clustering_coefficient:.3f}")
            print(f"    Transitivity: {metrics.transitivity:.3f}")

            print(f"\n  Efficiency:")
            print(f"    Global Efficiency: {metrics.global_efficiency:.3f}")
            print(f"    Local Efficiency: {metrics.local_efficiency:.3f}")

            print(f"\n  Robustness:")
            print(f"    Attack Tolerance: {metrics.attack_tolerance:.3f}")
            print(f"    Failure Tolerance: {metrics.failure_tolerance:.3f}")

            print(f"\n  Cost:")
            print(f"    Edge Cost: {metrics.edge_cost:.3f}")
            print(f"    Degree Cost: {metrics.degree_cost:.3f}")

            # Calculate score
            score = evaluator.calculate_score(metrics)
            print(f"\n  Overall Score: {score:.3f}")

        except Exception as e:
            print(f"Error evaluating topology: {e}")
            sys.exit(1)

    def _cmd_compare(self, args: argparse.Namespace) -> None:
        """Compare topologies command."""
        print(f"Comparing topologies for {args.size} nodes...")

        # Determine which topologies to compare
        if args.topologies:
            topo_types = [TopologyType(t) for t in args.topologies]
        else:
            topo_types = [
                TopologyType.ERDOS_RENYI,
                TopologyType.WATTS_STROGATZ,
                TopologyType.BARABASI_ALBERT,
                TopologyType.MODULAR,
                TopologyType.TWO_TIER,
            ]

        # Generate and evaluate
        results = []

        for topo_type in topo_types:
            print(f"\n  Evaluating {topo_type.value}...")

            generator = TopologyGenerator(seed=args.seed)

            # Use appropriate default parameters
            if topo_type == TopologyType.WATTS_STROGATZ:
                params = TopologyParams(n=args.size, k=max(4, int(np.log2(args.size))), p=0.1, seed=args.seed)
            elif topo_type == TopologyType.BARABASI_ALBERT:
                params = TopologyParams(n=args.size, m=max(2, int(np.log2(args.size))), seed=args.seed)
            elif topo_type == TopologyType.MODULAR:
                params = TopologyParams(n=args.size, modules=max(3, int(np.sqrt(args.size))), seed=args.seed)
            else:
                params = TopologyParams(n=args.size, seed=args.seed)

            try:
                G = generator.generate(topo_type, params)
                evaluator = TopologyEvaluator(parallel=False)
                metrics = evaluator.evaluate(G)

                results.append({
                    'type': topo_type.value,
                    'metrics': metrics,
                    'score': evaluator.calculate_score(metrics)
                })

            except Exception as e:
                print(f"    Error: {e}")

        # Print comparison table
        if results:
            print("\n" + "="*80)
            print(f"{'Topology':<20} {'Path':<8} {'Clustering':<10} {'Efficiency':<10} {'Robustness':<10} {'Score':<8}")
            print("="*80)

            for result in sorted(results, key=lambda x: x['score'], reverse=True):
                m = result['metrics']
                robustness = (m.attack_tolerance + m.failure_tolerance) / 2
                print(f"{result['type']:<20} "
                      f"{m.avg_path_length:<8.3f} "
                      f"{m.clustering_coefficient:<10.3f} "
                      f"{m.global_efficiency:<10.3f} "
                      f"{robustness:<10.3f} "
                      f"{result['score']:<8.3f}")

            print("="*80)

    def _cmd_list(self, args: argparse.Namespace) -> None:
        """List available topologies command."""
        print("Available Topology Types:")
        print()

        descriptions = {
            'erdos_renyi': 'Erdős-Rényi random graph',
            'watts_strogatz': 'Watts-Strogatz small-world graph',
            'barabasi_albert': 'Barabási-Albert scale-free graph',
            'regular_lattice': 'Regular lattice (grid)',
            'random_geometric': 'Random geometric graph',
            'hybrid_small_world_sf': 'Hybrid small-world + scale-free',
            'hierarchical': 'Hierarchical topology',
            'modular': 'Modular topology',
            'two_tier': 'Two-tier (core + edge)',
            'three_tier': 'Three-tier (core + agg + edge)',
        }

        for topo_type in TopologyType:
            desc = descriptions.get(topo_type.value, '')
            print(f"  {topo_type.value:<25} {desc}")

    def _cmd_benchmark(self, args: argparse.Namespace) -> None:
        """Generate benchmark suite command."""
        print(f"Generating benchmark suite for {args.size} nodes...")

        # Generate benchmark topologies
        topologies = generate_benchmark_topologies(args.size, seed=args.seed)

        print(f"\nGenerated {len(topologies)} benchmark topologies:")

        for name, (G, topo_type, params) in topologies.items():
            print(f"  {name}:")
            print(f"    Type: {topo_type.value}")
            print(f"    Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

            # Save if output specified
            if args.output:
                import os
                out_dir = os.path.join(args.output, str(args.size))
                os.makedirs(out_dir, exist_ok=True)

                generator = TopologyGenerator(seed=args.seed)
                generator.export_graphml(G, os.path.join(out_dir, f"{name}.graphml"))
                generator.export_json(G, os.path.join(out_dir, f"{name}.json"), topo_type, params)

            # Visualize if requested
            if args.visualize:
                self._visualize_topology(G, name, args.size)

    def _cmd_recommend(self, args: argparse.Namespace) -> None:
        """Recommend topology command."""
        print(f"Getting topology recommendation for {args.size} agents...")

        # Simple recommendation logic
        if args.size <= 20:
            recommendation = {
                'type': 'watts_strogatz',
                'params': {'k': 4, 'p': 0.1},
                'reason': 'Small colony: simple small-world topology'
            }
        elif args.size <= 100:
            if args.efficiency:
                recommendation = {
                    'type': 'two_tier',
                    'params': {'k': 8},
                    'reason': 'Medium colony prioritizing efficiency'
                }
            elif args.robustness:
                recommendation = {
                    'type': 'modular',
                    'params': {'modules': 5},
                    'reason': 'Medium colony prioritizing robustness'
                }
            else:
                recommendation = {
                    'type': 'watts_strogatz',
                    'params': {'k': 6, 'p': 0.2},
                    'reason': 'Medium colony: balanced topology'
                }
        else:
            if args.robustness:
                recommendation = {
                    'type': 'modular',
                    'params': {'modules': 10},
                    'reason': 'Large colony prioritizing robustness'
                }
            elif args.low_cost:
                recommendation = {
                    'type': 'hierarchical',
                    'params': {'levels': 3},
                    'reason': 'Large colony with low cost'
                }
            else:
                recommendation = {
                    'type': 'modular',
                    'params': {'modules': 7},
                    'reason': 'Large colony: robust modular topology'
                }

        print(f"\nRecommendation: {recommendation['type']}")
        print(f"Parameters: {recommendation['params']}")
        print(f"Reason: {recommendation['reason']}")

    def _visualize_topology(self, G: nx.Graph, name: str, size: int) -> None:
        """Visualize topology using matplotlib."""
        plt.figure(figsize=(12, 8))

        # Choose layout based on size and type
        if size <= 50:
            pos = nx.spring_layout(G, seed=42)
        elif size <= 200:
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G, seed=42, k=1/np.sqrt(size))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=100, node_color='lightblue')

        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.3)

        # Draw labels for small graphs
        if size <= 20:
            nx.draw_networkx_labels(G, pos)

        plt.title(f"{name} ({size} nodes, {G.number_of_edges()} edges)")
        plt.axis('off')

        filename = f"{name}_{size}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  Visualization saved to {filename}")
        plt.close()


def main():
    """Main entry point."""
    cli = TopologyCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
