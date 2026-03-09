"""
Pressure Dynamics Simulation for POLLN Hydraulic Metaphor

This module simulates pressure propagation through agent networks, modeling:
- Pressure = (demand × complexity) / (capacity × time)
- Pressure waves through agent graph
- Congestion detection and pressure-based routing

Mathematical Model:
    P = ρgh (hydrostatic pressure analogy)
    ∂P/∂t + v·∇P = D∇²P + S (pressure diffusion equation)

Where:
    P = cognitive pressure at node
    v = information velocity
    D = diffusion coefficient (communication efficiency)
    S = source/sink terms (task arrivals/departures)
"""

import numpy as np
import networkx as nx
from scipy.integrate import odeint
from scipy.spatial.distance import pdist, squareform
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns


@dataclass
class AgentNode:
    """Represents an agent in the hydraulic network"""
    id: int
    capacity: float  # Processing capacity (units/time)
    current_pressure: float  # Current cognitive load
    position: Tuple[float, float, float]  # 3D position
    connectivity: float  # Connection strength to neighbors


@dataclass
class TaskDemand:
    """Represents external task demand"""
    arrival_rate: float  # Tasks per time unit
    complexity_distribution: str  # 'uniform', 'normal', 'exponential'
    mean_complexity: float
    std_complexity: float = 0.3


class PressureDynamicsSimulator:
    """
    Simulates pressure dynamics in agent networks using hydraulic principles.

    Key equations:
    1. Pressure at node: P_i = (demand_i × complexity_i) / (capacity_i × Δt)
    2. Pressure propagation: ∂P/∂t = -∇·(vP) + D∇²P + S
    3. Flow rate: Q = A·v = A·√(2ΔP/ρ)
    """

    def __init__(
        self,
        num_agents: int = 50,
        topology: str = 'small_world',
        avg_degree: int = 6,
        spatial_dim: int = 3
    ):
        """
        Initialize simulator.

        Args:
            num_agents: Number of agents in network
            topology: 'small_world', 'scale_free', 'random', 'hierarchical'
            avg_degree: Average node degree
            spatial_dim: Spatial dimension for positioning
        """
        self.num_agents = num_agents
        self.topology = topology
        self.avg_degree = avg_degree
        self.spatial_dim = spatial_dim

        # Initialize network
        self.graph = self._create_topology()
        self.agents = self._initialize_agents()

        # Physics parameters
        self.diffusion_coeff = 0.1  # Communication efficiency
        self.damping = 0.05  # Pressure dissipation
        self.wave_speed = 1.0  # Information wave speed

        # Simulation state
        self.time = 0
        self.pressure_history = []
        self.flow_history = []

    def _create_topology(self) -> nx.Graph:
        """Create network topology"""
        if self.topology == 'small_world':
            G = nx.watts_strogatz_graph(self.num_agents, self.avg_degree, 0.1)
        elif self.topology == 'scale_free':
            G = nx.barabasi_albert_graph(self.num_agents, self.avg_degree // 2)
        elif self.topology == 'random':
            G = nx.erdos_renyi_graph(self.num_agents, self.avg_degree / self.num_agents)
        elif self.topology == 'hierarchical':
            G = self._create_hierarchical_topology()
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

        return G

    def _create_hierarchical_topology(self) -> nx.Graph:
        """Create hierarchical (tree-like) topology with shortcuts"""
        G = nx.Graph()

        # Build tree structure
        num_levels = int(np.log2(self.num_agents))
        nodes_per_level = self.num_agents // num_levels

        node_id = 0
        prev_level_nodes = []

        for level in range(num_levels):
            level_nodes = []
            for _ in range(nodes_per_level):
                if node_id < self.num_agents:
                    G.add_node(node_id, level=level)
                    level_nodes.append(node_id)

                    # Connect to previous level
                    if prev_level_nodes:
                        parent = prev_level_nodes[np.random.randint(len(prev_level_nodes))]
                        G.add_edge(node_id, parent)

                    node_id += 1

            # Add shortcuts within level
            for i in range(len(level_nodes)):
                for j in range(i+1, min(i+3, len(level_nodes))):
                    if np.random.random() < 0.3:
                        G.add_edge(level_nodes[i], level_nodes[j])

            prev_level_nodes = level_nodes

        return G

    def _initialize_agents(self) -> List[AgentNode]:
        """Initialize agent nodes with capacities and positions"""
        agents = []

        # Generate positions (3D spatial layout)
        if self.spatial_dim == 3:
            positions = np.random.randn(self.num_agents, 3)
            # Scale positions
            positions = positions / np.linalg.norm(positions, axis=1)[:, np.newaxis]
        else:
            positions = np.random.randn(self.num_agents, self.spatial_dim)

        for i in range(self.num_agents):
            # Capacity follows power law (few high-capacity agents)
            capacity = np.random.pareto(2.0) + 1.0

            # Initial pressure
            pressure = 0.0

            agent = AgentNode(
                id=i,
                capacity=capacity,
                current_pressure=pressure,
                position=tuple(positions[i]),
                connectivity=self.graph.degree[i]
            )
            agents.append(agent)

        return agents

    def compute_pressure(
        self,
        demands: np.ndarray,
        complexities: np.ndarray,
        dt: float = 1.0
    ) -> np.ndarray:
        """
        Compute pressure at each node.

        P_i = (demand_i × complexity_i) / (capacity_i × Δt)

        Args:
            demands: Task demand at each node
            complexities: Task complexity at each node
            dt: Time step

        Returns:
            Pressure array
        """
        capacities = np.array([agent.capacity for agent in self.agents])

        # Core pressure equation
        pressure = (demands * complexities) / (capacities * dt + 1e-6)

        # Update agent pressures
        for i, agent in enumerate(self.agents):
            agent.current_pressure = pressure[i]

        return pressure

    def propagate_pressure(
        self,
        pressure: np.ndarray,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Propagate pressure through network using diffusion equation.

        ∂P/∂t = D∇²P - dP + S

        Where:
            D = diffusion coefficient
            d = damping coefficient
            S = source/sink terms

        Args:
            pressure: Current pressure distribution
            dt: Time step

        Returns:
            Updated pressure distribution
        """
        n = self.num_agents
        laplacian = nx.laplacian_matrix(self.graph).toarray()

        # Diffusion term: D∇²P
        diffusion = self.diffusion_coeff * (laplacian @ pressure)

        # Damping term: -dP
        damping = -self.damping * pressure

        # Wave equation: ∂²P/∂t² = c²∇²P
        # Using finite difference approximation
        d2p_dt2 = self.wave_speed**2 * (laplacian @ pressure)

        # Update pressure
        new_pressure = pressure + dt * (diffusion + damping)

        # Ensure non-negative pressure
        new_pressure = np.maximum(new_pressure, 0)

        return new_pressure

    def compute_flow(
        self,
        pressure: np.ndarray
    ) -> Dict[Tuple[int, int], float]:
        """
        Compute flow between connected nodes.

        Q_ij = A_ij * √(2|P_i - P_j| / ρ)

        Args:
            pressure: Pressure at each node

        Returns:
            Dictionary mapping edges to flow rates
        """
        flows = {}

        for edge in self.graph.edges():
            i, j = edge
            pressure_diff = pressure[i] - pressure[j]

            # Flow rate (from high to low pressure)
            flow = np.sign(pressure_diff) * np.sqrt(2 * abs(pressure_diff))

            flows[edge] = flow

        return flows

    def detect_congestion(
        self,
        pressure: np.ndarray,
        threshold: float = 2.0
    ) -> List[int]:
        """
        Detect congested nodes (high pressure).

        Args:
            pressure: Pressure distribution
            threshold: Congestion threshold (std deviations above mean)

        Returns:
            List of congested node IDs
        """
        mean_pressure = np.mean(pressure)
        std_pressure = np.std(pressure)

        congestion_threshold = mean_pressure + threshold * std_pressure

        congested = np.where(pressure > congestion_threshold)[0]

        return congested.tolist()

    def simulate_step(
        self,
        task_demand: TaskDemand,
        dt: float = 0.01
    ) -> Dict[str, np.ndarray]:
        """
        Simulate one time step.

        Args:
            task_demand: Task demand parameters
            dt: Time step

        Returns:
            Dictionary with pressure, flow, and congestion data
        """
        # Generate new task demands
        if task_demand.complexity_distribution == 'uniform':
            complexities = np.random.uniform(
                task_demand.mean_complexity - task_demand.std_complexity,
                task_demand.mean_complexity + task_demand.std_complexity,
                self.num_agents
            )
        elif task_demand.complexity_distribution == 'normal':
            complexities = np.random.normal(
                task_demand.mean_complexity,
                task_demand.std_complexity,
                self.num_agents
            )
        else:  # exponential
            complexities = np.random.exponential(
                task_demand.mean_complexity,
                self.num_agents
            )

        # Poisson arrivals for demands
        demands = np.random.poisson(
            task_demand.arrival_rate,
            self.num_agents
        ).astype(float)

        # Compute pressure
        pressure = self.compute_pressure(demands, complexities, dt=1.0)

        # Propagate pressure
        pressure = self.propagate_pressure(pressure, dt)

        # Compute flows
        flows = self.compute_flow(pressure)

        # Detect congestion
        congested = self.detect_congestion(pressure)

        # Store history
        self.pressure_history.append(pressure.copy())
        self.flow_history.append(flows)
        self.time += dt

        return {
            'pressure': pressure,
            'flows': flows,
            'congested': congested,
            'demands': demands,
            'complexities': complexities
        }

    def run_simulation(
        self,
        num_steps: int = 1000,
        task_demand: Optional[TaskDemand] = None,
        dt: float = 0.01
    ) -> Dict[str, List]:
        """
        Run full simulation.

        Args:
            num_steps: Number of time steps
            task_demand: Task demand parameters
            dt: Time step

        Returns:
            Simulation history
        """
        if task_demand is None:
            task_demand = TaskDemand(
                arrival_rate=5.0,
                complexity_distribution='normal',
                mean_complexity=1.0,
                std_complexity=0.3
            )

        history = {
            'pressure': [],
            'congested': [],
            'max_pressure': [],
            'mean_pressure': [],
            'std_pressure': []
        }

        for step in range(num_steps):
            result = self.simulate_step(task_demand, dt)

            history['pressure'].append(result['pressure'])
            history['congested'].append(result['congested'])
            history['max_pressure'].append(np.max(result['pressure']))
            history['mean_pressure'].append(np.mean(result['pressure']))
            history['std_pressure'].append(np.std(result['pressure']))

        return history

    def analyze_pressure_distribution(
        self,
        history: Dict[str, List]
    ) -> Dict[str, float]:
        """
        Analyze pressure distribution statistics.

        Args:
            history: Simulation history

        Returns:
            Statistical metrics
        """
        final_pressure = history['pressure'][-1]

        metrics = {
            'mean_pressure': np.mean(final_pressure),
            'std_pressure': np.std(final_pressure),
            'max_pressure': np.max(final_pressure),
            'min_pressure': np.min(final_pressure),
            'pressure_entropy': self._compute_entropy(final_pressure),
            'gini_coefficient': self._compute_gini(final_pressure),
            'congestion_frequency': np.mean([
                len(c) for c in history['congested']
            ]),
            'pressure_volatility': np.std(history['mean_pressure'])
        }

        return metrics

    def _compute_entropy(self, pressure: np.ndarray) -> float:
        """Compute entropy of pressure distribution"""
        # Normalize to probabilities
        p = pressure / (np.sum(pressure) + 1e-10)
        p = p[p > 0]
        return -np.sum(p * np.log(p))

    def _compute_gini(self, pressure: np.ndarray) -> float:
        """Compute Gini coefficient (inequality measure)"""
        sorted_p = np.sort(pressure)
        n = len(pressure)
        cumsum = np.cumsum(sorted_p)
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n

    def visualize_pressure_network(
        self,
        pressure: np.ndarray,
        congested: List[int],
        save_path: Optional[str] = None
    ):
        """
        Visualize pressure distribution on network.

        Args:
            pressure: Pressure at each node
            congested: List of congested nodes
            save_path: Path to save figure
        """
        fig = plt.figure(figsize=(15, 10))

        # Get positions (use 3D if available)
        pos_3d = {agent.id: agent.position for agent in self.agents}

        # 2D projection
        pos_2d = {k: (v[0], v[1]) for k, v in pos_3d.items()}

        # Create subplots
        gs = fig.add_gridspec(2, 2)

        # 1. Network with pressure heatmap
        ax1 = fig.add_subplot(gs[0, 0])
        nx.draw_networkx(
            self.graph,
            pos=pos_2d,
            node_color=pressure,
            cmap='RdYlBu_r',
            node_size=300,
            with_labels=False,
            ax=ax1
        )
        ax1.set_title('Network Pressure Distribution')
        plt.colorbar(plt.cm.ScalarMappable(cmap='RdYlBu_r'), ax=ax1, label='Pressure')

        # 2. Pressure histogram
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(pressure, bins=30, edgecolor='black', alpha=0.7)
        ax2.axvline(np.mean(pressure), color='red', linestyle='--', label='Mean')
        ax2.axvline(np.median(pressure), color='green', linestyle='--', label='Median')
        ax2.set_xlabel('Pressure')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Pressure Distribution')
        ax2.legend()

        # 3. Congestion nodes
        ax3 = fig.add_subplot(gs[1, 0])
        node_colors = ['red' if i in congested else 'blue' for i in range(self.num_agents)]
        nx.draw_networkx(
            self.graph,
            pos=pos_2d,
            node_color=node_colors,
            node_size=300,
            with_labels=False,
            ax=ax3
        )
        ax3.set_title(f'Congested Nodes (Red: {len(congested)} nodes)')

        # 4. Pressure vs Capacity
        ax4 = fig.add_subplot(gs[1, 1])
        capacities = np.array([agent.capacity for agent in self.agents])
        ax4.scatter(capacities, pressure, alpha=0.6)
        ax4.set_xlabel('Agent Capacity')
        ax4.set_ylabel('Pressure')
        ax4.set_title('Pressure vs Capacity')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_pressure_evolution(
        self,
        history: Dict[str, List],
        save_path: Optional[str] = None
    ):
        """
        Visualize pressure evolution over time.

        Args:
            history: Simulation history
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        time_steps = range(len(history['pressure']))

        # 1. Mean pressure over time
        axes[0, 0].plot(time_steps, history['mean_pressure'], linewidth=2)
        axes[0, 0].fill_between(
            time_steps,
            np.array(history['mean_pressure']) - np.array(history['std_pressure']),
            np.array(history['mean_pressure']) + np.array(history['std_pressure']),
            alpha=0.3
        )
        axes[0, 0].set_xlabel('Time Step')
        axes[0, 0].set_ylabel('Pressure')
        axes[0, 0].set_title('Mean Pressure Evolution')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Max pressure over time
        axes[0, 1].plot(time_steps, history['max_pressure'], color='red', linewidth=2)
        axes[0, 1].set_xlabel('Time Step')
        axes[0, 1].set_ylabel('Max Pressure')
        axes[0, 1].set_title('Peak Pressure Evolution')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Congestion frequency
        congestion_counts = [len(c) for c in history['congested']]
        axes[1, 0].plot(time_steps, congestion_counts, color='orange', linewidth=2)
        axes[1, 0].set_xlabel('Time Step')
        axes[1, 0].set_ylabel('Number of Congested Nodes')
        axes[1, 0].set_title('Congestion Over Time')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Pressure volatility
        axes[1, 1].plot(
            time_steps[1:],
            np.diff(history['mean_pressure']),
            color='purple',
            linewidth=2
        )
        axes[1, 1].axhline(0, color='black', linestyle='--', alpha=0.5)
        axes[1, 1].set_xlabel('Time Step')
        axes[1, 1].set_ylabel('Pressure Change')
        axes[1, 1].set_title('Pressure Volatility')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def compare_topologies(
        self,
        topologies: List[str],
        num_steps: int = 500,
        num_trials: int = 10
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare different network topologies.

        Args:
            topologies: List of topology names
            num_steps: Simulation steps per trial
            num_trials: Number of trials per topology

        Returns:
            Comparison metrics
        """
        results = {}

        for topology in topologies:
            # Create simulator with this topology
            sim = PressureDynamicsSimulator(
                num_agents=self.num_agents,
                topology=topology,
                avg_degree=self.avg_degree
            )

            trial_metrics = []

            for _ in range(num_trials):
                task_demand = TaskDemand(
                    arrival_rate=5.0,
                    complexity_distribution='normal',
                    mean_complexity=1.0,
                    std_complexity=0.3
                )

                history = sim.run_simulation(num_steps, task_demand)
                metrics = sim.analyze_pressure_distribution(history)
                trial_metrics.append(metrics)

            # Aggregate metrics
            results[topology] = {
                metric: np.mean([m[metric] for m in trial_metrics])
                for metric in trial_metrics[0].keys()
            }

            # Add standard errors
            for metric in trial_metrics[0].keys():
                results[topology][f'{metric}_se'] = np.std(
                    [m[metric] for m in trial_metrics]
                ) / np.sqrt(num_trials)

        return results


def main():
    """Run demonstration simulations"""
    print("=" * 60)
    print("PRESSURE DYNAMICS SIMULATION")
    print("=" * 60)

    # Create simulator
    sim = PressureDynamicsSimulator(
        num_agents=50,
        topology='small_world',
        avg_degree=6
    )

    print(f"\nNetwork: {sim.topology} with {sim.num_agents} agents")
    print(f"Average degree: {sim.avg_degree}")
    print(f"Edges: {sim.graph.number_of_edges()}")

    # Run simulation
    print("\nRunning simulation...")
    task_demand = TaskDemand(
        arrival_rate=5.0,
        complexity_distribution='normal',
        mean_complexity=1.0,
        std_complexity=0.3
    )

    history = sim.run_simulation(num_steps=500, task_demand=task_demand)

    # Analyze results
    print("\nAnalyzing results...")
    metrics = sim.analyze_pressure_distribution(history)

    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # Visualize
    print("\nGenerating visualizations...")
    final_pressure = history['pressure'][-1]
    final_congested = history['congested'][-1]

    sim.visualize_pressure_network(final_pressure, final_congested)
    sim.visualize_pressure_evolution(history)

    # Compare topologies
    print("\nComparing topologies...")
    topologies = ['small_world', 'scale_free', 'random', 'hierarchical']
    comparison = sim.compare_topologies(topologies, num_steps=200, num_trials=5)

    print("\nTopology Comparison:")
    for topo, topo_metrics in comparison.items():
        print(f"\n{topo}:")
        for key, value in topo_metrics.items():
            if not key.endswith('_se'):
                print(f"  {key}: {value:.4f} ± {topo_metrics[f'{key}_se']:.4f}")

    print("\nSimulation complete!")


if __name__ == '__main__':
    main()
