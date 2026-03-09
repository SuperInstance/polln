"""
Flow Optimization Simulation for POLLN Hydraulic Metaphor

This module simulates information flow through agent networks, modeling:
- Flow = √(2 × pressure_difference / resistance)
- Network topology optimization
- Bottleneck detection and resolution

Mathematical Model:
    Q = A·v = A·√(2ΔP/ρ) (Bernoulli's equation)
    ∇·v = 0 (incompressible flow)

Where:
    Q = flow rate
    v = information velocity
    P = pressure
    ρ = information density (resistance)
"""

import numpy as np
import networkx as nx
from scipy.optimize import minimize
from scipy.spatial.distance import cdist
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from collections import defaultdict


@dataclass
class FlowMetrics:
    """Metrics for flow analysis"""
    throughput: float  # Total information flow
    avg_latency: float  # Average path delay
    bottleneck_nodes: List[int]  # Congested nodes
    bottleneck_edges: List[Tuple[int, int]]  # Congested edges
    efficiency: float  # Flow efficiency (actual/max)
    robustness: float  # Resilience to failures


class NetworkTopology:
    """Represents a network topology"""

    TOPOLOGIES = ['star', 'mesh', 'hierarchical', 'small_world', 'scale_free']

    @staticmethod
    def create(
        num_agents: int,
        topology: str,
        **kwargs
    ) -> nx.Graph:
        """Create network topology"""
        if topology == 'star':
            return NetworkTopology._star_topology(num_agents)
        elif topology == 'mesh':
            return NetworkTopology._mesh_topology(num_agents)
        elif topology == 'hierarchical':
            return NetworkTopology._hierarchical_topology(num_agents)
        elif topology == 'small_world':
            k = kwargs.get('avg_degree', 6)
            p = kwargs.get('rewire_prob', 0.1)
            return nx.watts_strogatz_graph(num_agents, k, p)
        elif topology == 'scale_free':
            m = kwargs.get('avg_degree', 6) // 2
            return nx.barabasi_albert_graph(num_agents, m)
        else:
            raise ValueError(f"Unknown topology: {topology}")

    @staticmethod
    def _star_topology(n: int) -> nx.Graph:
        """Star topology (one central hub)"""
        G = nx.star_graph(n - 1)
        return G

    @staticmethod
    def _mesh_topology(n: int) -> nx.Graph:
        """Mesh topology (fully connected)"""
        G = nx.complete_graph(n)
        return G

    @staticmethod
    def _hierarchical_topology(n: int) -> nx.Graph:
        """Hierarchical (tree-based) topology"""
        num_levels = int(np.log2(n))
        nodes_per_level = n // num_levels

        G = nx.Graph()
        node_id = 0
        prev_level = []

        for level in range(num_levels):
            current_level = []

            for _ in range(nodes_per_level):
                if node_id < n:
                    G.add_node(node_id, level=level)

                    if prev_level:
                        parent = np.random.choice(prev_level)
                        G.add_edge(node_id, parent)

                    current_level.append(node_id)
                    node_id += 1

            # Add shortcuts within level
            for i in range(len(current_level)):
                for j in range(i + 1, min(i + 3, len(current_level))):
                    if np.random.random() < 0.3:
                        G.add_edge(current_level[i], current_level[j])

            prev_level = current_level

        return G


class FlowOptimizer:
    """
    Optimizes information flow through agent networks.

    Key principles:
    1. Flow follows pressure gradients
    2. Minimize resistance (maximize conductance)
    3. Balance load across network
    4. Detect and resolve bottlenecks
    """

    def __init__(
        self,
        graph: nx.Graph,
        node_capacities: Optional[np.ndarray] = None,
        edge_resistances: Optional[Dict[Tuple[int, int], float]] = None
    ):
        """
        Initialize flow optimizer.

        Args:
            graph: Network topology
            node_capacities: Processing capacity of each node
            edge_resistances: Resistance of each edge
        """
        self.graph = graph
        self.num_nodes = graph.number_of_nodes()

        # Initialize node capacities
        if node_capacities is None:
            # Power law distribution
            self.node_capacities = np.random.pareto(2.0, self.num_nodes) + 1.0
        else:
            self.node_capacities = node_capacities

        # Initialize edge resistances
        if edge_resistances is None:
            # Resistance inversely proportional to edge betweenness
            betweenness = nx.edge_betweenness_centrality(graph)
            self.edge_resistances = {
                edge: 1.0 / (bet + 0.1)
                for edge, bet in betweenness.items()
            }
        else:
            self.edge_resistances = edge_resistances

        # Flow state
        self.pressure = np.zeros(self.num_nodes)
        self.flow = {}

    def compute_flow(
        self,
        source: int,
        sink: int,
        source_pressure: float = 10.0,
        sink_pressure: float = 0.0
    ) -> Dict[Tuple[int, int], float]:
        """
        Compute flow from source to sink using pressure-driven model.

        Q_ij = (P_i - P_j) / R_ij

        Args:
            source: Source node
            sink: Sink node
            source_pressure: Pressure at source
            sink_pressure: Pressure at sink

        Returns:
            Flow on each edge
        """
        # Set boundary conditions
        self.pressure[:] = 0
        self.pressure[source] = source_pressure
        self.pressure[sink] = sink_pressure

        # Solve for pressure distribution using network flow equations
        # For each internal node: Σ Q_ij = 0 (flow conservation)
        self._solve_pressure_distribution(source, sink)

        # Compute flow on each edge
        flow = {}
        for edge in self.graph.edges():
            i, j = edge
            pressure_diff = self.pressure[i] - self.pressure[j]
            resistance = self.edge_resistances.get(edge, 1.0)
            flow[edge] = pressure_diff / resistance

        self.flow = flow
        return flow

    def _solve_pressure_distribution(
        self,
        source: int,
        sink: int,
        max_iter: int = 1000,
        tol: float = 1e-6
    ):
        """
        Solve for pressure distribution using iterative method.

        For each internal node i:
            Σ_j (P_i - P_j) / R_ij = 0

        This is equivalent to solving a linear system Ax = b
        """
        n = self.num_nodes
        pressure = self.pressure.copy()

        for iteration in range(max_iter):
            old_pressure = pressure.copy()

            # Update pressure at each node (except source and sink)
            for i in range(n):
                if i == source or i == sink:
                    continue

                # Get neighbors
                neighbors = list(self.graph.neighbors(i))

                # Weighted average of neighbor pressures
                numerator = 0.0
                denominator = 0.0

                for j in neighbors:
                    resistance = self.edge_resistances.get(
                        tuple(sorted((i, j))), 1.0
                    )
                    weight = 1.0 / resistance
                    numerator += weight * pressure[j]
                    denominator += weight

                if denominator > 0:
                    pressure[i] = numerator / denominator

            # Check convergence
            diff = np.max(np.abs(pressure - old_pressure))
            if diff < tol:
                break

        self.pressure = pressure

    def compute_throughput(self, flow: Dict[Tuple[int, int], float]) -> float:
        """
        Compute total throughput.

        Args:
            flow: Flow on each edge

        Returns:
            Total throughput
        """
        # Sum of absolute flows entering/leaving network
        total_flow = sum(abs(f) for f in flow.values())
        return total_flow / 2  # Divide by 2 (each edge counted twice)

    def compute_latency(self, source: int, sink: int) -> float:
        """
        Compute average latency from source to sink.

        Args:
            source: Source node
            sink: Sink node

        Returns:
            Average latency
        """
        # Find shortest path
        try:
            path = nx.shortest_path(self.graph, source, sink)

            # Compute latency along path
            latency = 0.0
            for i in range(len(path) - 1):
                edge = tuple(sorted((path[i], path[i + 1])))
                resistance = self.edge_resistances.get(edge, 1.0)
                flow = self.flow.get(edge, 0.0)

                # Latency increases with flow (congestion)
                latency += resistance * (1 + abs(flow))

            return latency

        except nx.NetworkXNoPath:
            return float('inf')

    def detect_bottlenecks(
        self,
        threshold: float = 0.8
    ) -> Tuple[List[int], List[Tuple[int, int]]]:
        """
        Detect bottlenecks in the network.

        Node bottleneck: capacity utilization > threshold
        Edge bottleneck: flow/capacity > threshold

        Args:
            threshold: Bottleneck detection threshold

        Returns:
            Tuple of (bottleneck nodes, bottleneck edges)
        """
        # Node bottlenecks
        node_loads = defaultdict(float)
        for edge, flow in self.flow.items():
            i, j = edge
            node_loads[i] += abs(flow)
            node_loads[j] += abs(flow)

        bottleneck_nodes = [
            node for node in range(self.num_nodes)
            if node_loads[node] / (2 * self.node_capacities[node]) > threshold
        ]

        # Edge bottlenecks
        bottleneck_edges = [
            edge for edge, flow in self.flow.items()
            if abs(flow) > threshold * self.node_capacities[edge[0]]
        ]

        return bottleneck_nodes, bottleneck_edges

    def compute_efficiency(
        self,
        throughput: float,
        max_throughput: Optional[float] = None
    ) -> float:
        """
        Compute flow efficiency.

        Args:
            throughput: Actual throughput
            max_throughput: Maximum possible throughput

        Returns:
            Efficiency (0-1)
        """
        if max_throughput is None:
            # Estimate max throughput (sum of capacities)
            max_throughput = np.sum(self.node_capacities)

        return throughput / max_throughput if max_throughput > 0 else 0

    def compute_robustness(
        self,
        num_failures: int = 5
    ) -> float:
        """
        Compute network robustness to node failures.

        Args:
            num_failures: Number of random node failures to test

        Returns:
            Robustness score (0-1)
        """
        if self.num_nodes <= num_failures:
            return 0.0

        original_size = nx.connected_components(self.graph)

        # Test random failures
        surviving_fractions = []
        for _ in range(100):  # Monte Carlo samples
            # Randomly remove nodes
            test_graph = self.graph.copy()
            nodes_to_remove = np.random.choice(
                list(test_graph.nodes()),
                num_failures,
                replace=False
            )
            test_graph.remove_nodes_from(nodes_to_remove)

            # Check connectivity
            if test_graph.number_of_nodes() > 0:
                largest_component = max(
                    nx.connected_components(test_graph),
                    key=len
                )
                surviving_fraction = len(largest_component) / self.num_nodes
                surviving_fractions.append(surviving_fraction)

        return np.mean(surviving_fractions)


class FlowSimulation:
    """Comprehensive flow simulation and optimization"""

    def __init__(
        self,
        num_agents: int = 50,
        topologies: Optional[List[str]] = None
    ):
        """
        Initialize flow simulation.

        Args:
            num_agents: Number of agents
            topologies: Topologies to compare
        """
        self.num_agents = num_agents

        if topologies is None:
            topologies = NetworkTopology.TOPOLOGIES

        self.topologies = topologies
        self.networks = {}

        # Create networks
        for topo in topologies:
            graph = NetworkTopology.create(num_agents, topo)
            self.networks[topo] = graph

        self.results = defaultdict(dict)

    def simulate_topology(
        self,
        topology: str,
        num_trials: int = 100,
        failure_rate: float = 0.1
    ) -> FlowMetrics:
        """
        Simulate flow for a specific topology.

        Args:
            topology: Topology name
            num_trials: Number of random source-sink pairs
            failure_rate: Probability of edge failure

        Returns:
            Flow metrics
        """
        graph = self.networks[topology]
        optimizer = FlowOptimizer(graph)

        throughputs = []
        latencies = []
        bottleneck_counts = []
        efficiencies = []

        for trial in range(num_trials):
            # Random source-sink pair
            source, sink = np.random.choice(
                self.num_agents, 2, replace=False
            )

            # Random edge failures
            test_graph = graph.copy()
            edges = list(test_graph.edges())
            num_failures = int(failure_rate * len(edges))

            if num_failures > 0:
                edges_to_remove = np.random.choice(
                    len(edges),
                    num_failures,
                    replace=False
                )
                for idx in edges_to_remove:
                    test_graph.remove_edge(*edges[idx])

            # Skip if disconnected
            if not nx.has_path(test_graph, source, sink):
                continue

            # Create optimizer with test graph
            test_optimizer = FlowOptimizer(test_graph)

            # Compute flow
            flow = test_optimizer.compute_flow(source, sink)

            # Compute metrics
            throughput = test_optimizer.compute_throughput(flow)
            latency = test_optimizer.compute_latency(source, sink)
            bottleneck_nodes, bottleneck_edges = test_optimizer.detect_bottlenecks()
            efficiency = test_optimizer.compute_efficiency(throughput)

            throughputs.append(throughput)
            latencies.append(latency)
            bottleneck_counts.append(
                len(bottleneck_nodes) + len(bottleneck_edges)
            )
            efficiencies.append(efficiency)

        # Compute aggregate metrics
        metrics = FlowMetrics(
            throughput=np.mean(throughputs),
            avg_latency=np.mean(latencies),
            bottleneck_nodes=[],
            bottleneck_edges=[],
            efficiency=np.mean(efficiencies),
            robustness=optimizer.compute_robustness()
        )

        return metrics

    def compare_topologies(
        self,
        num_trials: int = 100,
        failure_rates: List[float] = None
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Compare all topologies.

        Args:
            num_trials: Number of trials per topology
            failure_rates: List of failure rates to test

        Returns:
            Comparison results
        """
        if failure_rates is None:
            failure_rates = [0.0, 0.05, 0.1, 0.2, 0.3]

        results = defaultdict(lambda: defaultdict(list))

        for topology in self.topologies:
            print(f"\nSimulating {topology}...")

            for failure_rate in failure_rates:
                metrics = self.simulate_topology(
                    topology,
                    num_trials=num_trials,
                    failure_rate=failure_rate
                )

                results[topology]['failure_rates'].append(failure_rate)
                results[topology]['throughput'].append(metrics.throughput)
                results[topology]['latency'].append(metrics.avg_latency)
                results[topology]['efficiency'].append(metrics.efficiency)
                results[topology]['robustness'].append(metrics.robustness)

        return dict(results)

    def find_optimal_topology(
        self,
        metric: str = 'efficiency',
        failure_rate: float = 0.1
    ) -> Tuple[str, float]:
        """
        Find optimal topology for given metric.

        Args:
            metric: Metric to optimize ('throughput', 'latency', 'efficiency', 'robustness')
            failure_rate: Failure rate to test

        Returns:
            Tuple of (topology name, metric value)
        """
        best_topo = None
        best_value = -np.inf if metric != 'latency' else np.inf

        for topology in self.topologies:
            metrics = self.simulate_topology(
                topology,
                num_trials=100,
                failure_rate=failure_rate
            )

            value = getattr(metrics, metric)

            if metric == 'latency':
                if value < best_value:
                    best_value = value
                    best_topo = topology
            else:
                if value > best_value:
                    best_value = value
                    best_topo = topology

        return best_topo, best_value

    def optimize_network(
        self,
        topology: str,
        optimization_target: str = 'throughput',
        max_iterations: int = 100
    ) -> nx.Graph:
        """
        Optimize network structure for given target.

        Args:
            topology: Initial topology
            optimization_target: Target metric
            max_iterations: Optimization iterations

        Returns:
            Optimized graph
        """
        graph = self.networks[topology].copy()
        optimizer = FlowOptimizer(graph)

        best_graph = graph.copy()
        best_score = 0

        for iteration in range(max_iterations):
            # Randomly add or remove edges
            action = np.random.choice(['add', 'remove'])

            if action == 'add' and graph.number_of_edges() < self.num_agents * (self.num_agents - 1) // 2:
                # Add random edge
                nodes = list(graph.nodes())
                i, j = np.random.choice(nodes, 2, replace=False)
                if not graph.has_edge(i, j):
                    graph.add_edge(i, j)

            elif action == 'remove' and graph.number_of_edges() > self.num_agents - 1:
                # Remove random edge
                edges = list(graph.edges())
                edge = np.random.choice(len(edges))
                graph.remove_edge(*edges[edge])

            # Evaluate
            test_optimizer = FlowOptimizer(graph)
            source, sink = np.random.choice(self.num_agents, 2, replace=False)

            if nx.has_path(graph, source, sink):
                flow = test_optimizer.compute_flow(source, sink)
                score = test_optimizer.compute_throughput(flow)

                if score > best_score:
                    best_score = score
                    best_graph = graph.copy()

        return best_graph

    def visualize_comparison(
        self,
        results: Dict[str, Dict[str, List[float]]],
        save_path: Optional[str] = None
    ):
        """
        Visualize topology comparison.

        Args:
            results: Comparison results
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        failure_rates = list(results.values())[0]['failure_rates']

        # 1. Throughput vs failure rate
        ax = axes[0, 0]
        for topo, data in results.items():
            ax.plot(
                data['failure_rates'],
                data['throughput'],
                marker='o',
                label=topo,
                linewidth=2
            )
        ax.set_xlabel('Failure Rate')
        ax.set_ylabel('Throughput')
        ax.set_title('Throughput vs Failure Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Latency vs failure rate
        ax = axes[0, 1]
        for topo, data in results.items():
            ax.plot(
                data['failure_rates'],
                data['latency'],
                marker='s',
                label=topo,
                linewidth=2
            )
        ax.set_xlabel('Failure Rate')
        ax.set_ylabel('Latency')
        ax.set_title('Latency vs Failure Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Efficiency vs failure rate
        ax = axes[1, 0]
        for topo, data in results.items():
            ax.plot(
                data['failure_rates'],
                data['efficiency'],
                marker='^',
                label=topo,
                linewidth=2
            )
        ax.set_xlabel('Failure Rate')
        ax.set_ylabel('Efficiency')
        ax.set_title('Efficiency vs Failure Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 4. Robustness comparison (bar chart)
        ax = axes[1, 1]
        topos = list(results.keys())
        robustness = [results[t]['robustness'][0] for t in topos]
        ax.bar(topos, robustness, alpha=0.7)
        ax.set_xlabel('Topology')
        ax.set_ylabel('Robustness')
        ax.set_title('Robustness Comparison')
        ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_3d_flow(
        self,
        topology: str,
        source: int,
        sink: int,
        save_path: Optional[str] = None
    ):
        """
        Visualize 3D flow field.

        Args:
            topology: Topology name
            source: Source node
            sink: Sink node
            save_path: Path to save figure
        """
        graph = self.networks[topology]
        optimizer = FlowOptimizer(graph)

        # Compute flow
        flow = optimizer.compute_flow(source, sink)

        # Get node positions (3D)
        pos = nx.spring_layout(graph, dim=3, seed=42)

        # Create 3D plot
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Extract coordinates
        xs = [pos[node][0] for node in graph.nodes()]
        ys = [pos[node][1] for node in graph.nodes()]
        zs = [pos[node][2] for node in graph.nodes()]

        # Plot nodes
        ax.scatter(xs, ys, zs, c=optimizer.pressure, cmap='RdYlBu_r', s=100, alpha=0.8)

        # Plot edges with flow magnitude
        for edge, flow_value in flow.items():
            i, j = edge
            x_line = [pos[i][0], pos[j][0]]
            y_line = [pos[i][1], pos[j][1]]
            z_line = [pos[i][2], pos[j][2]]

            # Line width proportional to flow
            linewidth = 1 + 5 * abs(flow_value) / (max(abs(f) for f in flow.values()) + 1e-6)

            ax.plot(
                x_line, y_line, z_line,
                c='red' if flow_value > 0 else 'blue',
                linewidth=linewidth,
                alpha=0.5
            )

        # Highlight source and sink
        ax.scatter(
            [pos[source][0]], [pos[source][1]], [pos[source][2]],
            c='green', s=200, marker='s', label='Source'
        )
        ax.scatter(
            [pos[sink][0]], [pos[sink][1]], [pos[sink][2]],
            c='black', s=200, marker='^', label='Sink'
        )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'3D Flow Field - {topology} Topology')
        ax.legend()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """Run demonstration simulations"""
    print("=" * 60)
    print("FLOW OPTIMIZATION SIMULATION")
    print("=" * 60)

    # Create simulation
    sim = FlowSimulation(
        num_agents=50,
        topologies=['star', 'mesh', 'hierarchical', 'small_world', 'scale_free']
    )

    print(f"\nSimulating {len(sim.topologies)} topologies with {sim.num_agents} agents")

    # Compare topologies
    print("\nComparing topologies...")
    results = sim.compare_topologies(
        num_trials=50,
        failure_rates=[0.0, 0.05, 0.1, 0.2]
    )

    # Visualize comparison
    print("\nGenerating visualizations...")
    sim.visualize_comparison(results)

    # Find optimal topology
    print("\nFinding optimal topologies...")
    for metric in ['throughput', 'latency', 'efficiency', 'robustness']:
        topo, value = sim.find_optimal_topology(metric, failure_rate=0.1)
        print(f"  Best {metric}: {topo} ({value:.4f})")

    # Visualize 3D flow
    print("\nGenerating 3D flow visualization...")
    sim.visualize_3d_flow('small_world', source=0, sink=25)

    print("\nSimulation complete!")


if __name__ == '__main__':
    main()
