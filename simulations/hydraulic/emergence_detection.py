"""
Emergence Detection Simulation for POLLN Hydraulic Metaphor

This module detects and quantifies emergent behavior in agent networks:
- Synergy detection: When whole > sum(parts)
- Phase transition identification: Critical thresholds for emergence
- Novel capability discovery: Unexpected behaviors from agent combinations

Mathematical Model:
    emergence = complexity_joint - sum(complexity_individual) - sum(complexity_pairwise)

    synergy = Σ I(X_i; X_j|S) - Σ I(X_i)  [conditional mutual information]

Where:
    I(X;Y) = mutual information
    S = system state
    complexity = Kolmogorov complexity (approximated via compression)

Key insights:
- Emergence occurs when information integration exceeds expected
- Phase transitions happen at critical network densities
- Synergy scales with network topology and agent diversity
"""

import numpy as np
import networkx as nx
from scipy.stats import entropy
from scipy.integrate import odeint
from sklearn.cluster import DBSCAN
from sklearn.metrics import mutual_info_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional, Set
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from collections import defaultdict
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')


@dataclass
class EmergenceMetrics:
    """Metrics for emergence detection"""
    synergy: float  # Whole > sum(parts)
    integration: float  # Information integration
    complexity: float  # System complexity
    phase: str  # 'subcritical', 'critical', 'supercritical'
    novel_capabilities: List[str]  # Detected novel behaviors
    critical_threshold: float  # Threshold for phase transition


@dataclass
class AgentState:
    """State of an individual agent"""
    id: int
    capabilities: np.ndarray  # Capability vector
    behavior: np.ndarray  # Behavior pattern
    connections: Set[int]  # Connected agents


class EmergenceDetector:
    """
    Detects emergent phenomena in multi-agent systems.

    Core principles:
    1. Emergence = non-additive information integration
    2. Synergy = conditional mutual information
    3. Phase transitions at critical connectivity
    """

    def __init__(
        self,
        num_agents: int = 50,
        capability_dim: int = 10
    ):
        """
        Initialize detector.

        Args:
            num_agents: Number of agents
            capability_dim: Dimension of capability space
        """
        self.num_agents = num_agents
        self.capability_dim = capability_dim
        self.agents = []
        self.network = nx.Graph()

        # Emergence history
        self.synergy_history = []
        self.complexity_history = []
        self.phase_history = []

    def initialize_agents(
        self,
        diversity: float = 1.0,
        specialization: float = 0.5
    ):
        """
        Initialize agent population.

        Args:
            diversity: Diversity of capabilities (0-1)
            specialization: Degree of specialization (0-1)
        """
        self.agents = []

        for i in range(self.num_agents):
            # Generate capability vector
            if specialization > 0:
                # Specialized: peak in one dimension
                capabilities = np.random.rand(self.capability_dim) * diversity
                peak_dim = np.random.randint(self.capability_dim)
                capabilities[peak_dim] += specialization
            else:
                # Generalized: uniform capabilities
                capabilities = np.random.rand(self.capability_dim) * diversity

            # Generate initial behavior pattern
            behavior = self._generate_behavior(capabilities)

            agent = AgentState(
                id=i,
                capabilities=capabilities,
                behavior=behavior,
                connections=set()
            )

            self.agents.append(agent)
            self.network.add_node(i)

    def _generate_behavior(
        self,
        capabilities: np.ndarray,
        noise_level: float = 0.1
    ) -> np.ndarray:
        """
        Generate behavior pattern from capabilities.

        Args:
            capabilities: Capability vector
            noise_level: Random noise level

        Returns:
            Behavior pattern
        """
        # Behavior is capability-based with noise
        behavior = capabilities + np.random.randn(len(capabilities)) * noise_level
        return behavior

    def connect_agents(
        self,
        topology: str = 'small_world',
        connection_prob: float = 0.1,
        avg_degree: int = 6
    ):
        """
        Connect agents according to topology.

        Args:
            topology: Network topology
            connection_prob: Connection probability
            avg_degree: Average degree for small-world
        """
        self.network.clear_edges()

        if topology == 'random':
            # Erdős-Rényi random graph
            for i, j in combinations(range(self.num_agents), 2):
                if np.random.random() < connection_prob:
                    self.network.add_edge(i, j)
                    self.agents[i].connections.add(j)
                    self.agents[j].connections.add(i)

        elif topology == 'small_world':
            # Watts-Strogatz small world
            k = avg_degree
            for i in range(self.num_agents):
                # Connect to k nearest neighbors
                for offset in range(1, k // 2 + 1):
                    j = (i + offset) % self.num_agents
                    self.network.add_edge(i, j)
                    self.agents[i].connections.add(j)
                    self.agents[j].connections.add(i)

            # Rewire with probability p
            edges = list(self.network.edges())
            for i, j in edges:
                if np.random.random() < connection_prob:
                    # Rewire
                    self.network.remove_edge(i, j)
                    self.agents[i].connections.discard(j)
                    self.agents[j].connections.discard(i)

                    # New connection
                    new_j = np.random.randint(self.num_agents)
                    if new_j != i and not self.network.has_edge(i, new_j):
                        self.network.add_edge(i, new_j)
                        self.agents[i].connections.add(new_j)
                        self.agents[new_j].connections.add(i)

        elif topology == 'scale_free':
            # Barabási-Albert scale-free
            m = max(1, avg_degree // 2)
            self.network = nx.barabasi_albert_graph(self.num_agents, m)

            # Update agent connections
            for i, j in self.network.edges():
                self.agents[i].connections.add(j)
                self.agents[j].connections.add(i)

    def compute_mutual_information(
        self,
        x: np.ndarray,
        y: np.ndarray,
        bins: int = 10
    ) -> float:
        """
        Compute mutual information between two variables.

        I(X;Y) = H(X) + H(Y) - H(X,Y)

        Args:
            x: First variable
            y: Second variable
            bins: Number of bins for discretization

        Returns:
            Mutual information
        """
        # Discretize
        x_discrete = np.digitize(x, bins=np.linspace(x.min(), x.max(), bins))
        y_discrete = np.digitize(y, bins=np.linspace(y.min(), y.max(), bins))

        # Compute mutual information
        mi = mutual_info_score(x_discrete, y_discrete)

        return mi

    def compute_synergy(
        self,
        agent_subset: Optional[List[int]] = None
    ) -> float:
        """
        Compute synergy: information beyond individual and pairwise.

        synergy = I(X_1; X_2; ...; X_n) - Σ I(X_i) - Σ I(X_i; X_j)

        Args:
            agent_subset: Subset of agents to analyze (default: all)

        Returns:
            Synergy score
        """
        if agent_subset is None:
            agent_subset = list(range(self.num_agents))

        n = len(agent_subset)
        if n < 2:
            return 0.0

        # Get behavior patterns
        behaviors = np.array([self.agents[i].behavior for i in agent_subset])

        # Individual entropies
        individual_mi = 0.0
        for i in range(n):
            individual_mi += entropy(
                np.histogram(behaviors[i], bins=10, density=True)[0] + 1e-10
            )

        # Pairwise mutual information
        pairwise_mi = 0.0
        for i, j in combinations(range(n), 2):
            pairwise_mi += self.compute_mutual_information(behaviors[i], behaviors[j])

        # Joint information (multi-information)
        joint_behavior = behaviors.flatten()
        joint_mi = entropy(
            np.histogram(joint_behavior, bins=10, density=True)[0] + 1e-10
        )

        # Synergy = joint - individual - pairwise
        synergy = joint_mi - individual_mi - pairwise_mi

        return max(0, synergy)  # Non-negative

    def compute_integration(
        self,
        agent_subset: Optional[List[int]] = None
    ) -> float:
        """
        Compute information integration (Φ).

        Measures the degree to which system cannot be decomposed
        into independent parts.

        Args:
            agent_subset: Subset of agents to analyze

        Returns:
            Integration score
        """
        if agent_subset is None:
            agent_subset = list(range(self.num_agents))

        n = len(agent_subset)
        if n < 2:
            return 0.0

        # Get behaviors
        behaviors = np.array([self.agents[i].behavior for i in agent_subset])

        # Compute covariance matrix
        cov_matrix = np.cov(behaviors)

        # Integration = determinant of correlation matrix
        # High determinant = high integration
        try:
            corr_matrix = np.corrcoef(behaviors)
            integration = np.linalg.det(corr_matrix)
            integration = max(0, integration)  # Non-negative
        except:
            integration = 0.0

        return integration

    def compute_complexity(
        self,
        agent_subset: Optional[List[int]] = None
    ) -> float:
        """
        Compute system complexity.

        Complexity = integration × differentiation
        - Integration: how connected the system is
        - Differentiation: how diverse the components are

        Args:
            agent_subset: Subset of agents to analyze

        Returns:
            Complexity score
        """
        if agent_subset is None:
            agent_subset = list(range(self.num_agents))

        n = len(agent_subset)
        if n < 2:
            return 0.0

        # Integration
        integration = self.compute_integration(agent_subset)

        # Differentiation (variance in capabilities)
        capabilities = np.array([self.agents[i].capabilities for i in agent_subset])
        differentiation = np.mean(np.std(capabilities, axis=0))

        # Complexity
        complexity = integration * differentiation

        return complexity

    def detect_phase_transition(
        self,
        metric: str = 'synergy'
    ) -> Tuple[str, float]:
        """
        Detect if system is at phase transition.

        Phase transitions occur when metrics show sudden changes
        or critical slowing down.

        Args:
            metric: Metric to analyze ('synergy', 'complexity', 'integration')

        Returns:
            Tuple of (phase, critical_value)
        """
        if metric == 'synergy':
            values = self.synergy_history
        elif metric == 'complexity':
            values = self.complexity_history
        else:
            values = []

        if len(values) < 10:
            return 'subcritical', 0.0

        # Compute derivative (rate of change)
        if len(values) > 1:
            derivatives = np.diff(values)

            # Detect phase transition based on derivative variance
            derivative_var = np.var(derivatives)

            # High variance indicates phase transition
            if derivative_var > np.mean(derivatives)**2 + 0.1:
                phase = 'critical'
            elif values[-1] > np.mean(values):
                phase = 'supercritical'
            else:
                phase = 'subcritical'

            critical_value = values[-1]
        else:
            phase = 'subcritical'
            critical_value = values[0] if values else 0.0

        return phase, critical_value

    def detect_novel_capabilities(
        self,
        agent_subset: Optional[List[int]] = None,
        threshold: float = 2.0
    ) -> List[str]:
        """
        Detect novel capabilities emerging from agent interactions.

        A capability is novel if it cannot be explained by individual
        agent capabilities.

        Args:
            agent_subset: Agents to analyze
            threshold: Detection threshold (std deviations)

        Returns:
            List of novel capability descriptions
        """
        if agent_subset is None:
            agent_subset = list(range(self.num_agents))

        novel_capabilities = []

        # Compute collective behavior
        collective_behavior = np.mean([
            self.agents[i].behavior
            for i in agent_subset
        ], axis=0)

        # Compute expected behavior (sum of individuals)
        expected_behavior = np.sum([
            self.agents[i].capabilities
            for i in agent_subset
        ], axis=0) / len(agent_subset)

        # Find deviations (novel capabilities)
        deviations = collective_behavior - expected_behavior
        deviation_magnitude = np.linalg.norm(deviations)

        # Threshold for novelty
        baseline_deviation = np.mean([
            np.linalg.norm(self.agents[i].behavior - self.agents[i].capabilities)
            for i in agent_subset
        ])

        if deviation_magnitude > threshold * baseline_deviation:
            # Novel capability detected
            capability_dims = np.where(np.abs(deviations) > threshold)[0]

            for dim in capability_dims:
                novel_capabilities.append(
                    f"Capability dimension {dim}: "
                    f"collective={collective_behavior[dim]:.2f}, "
                    f"expected={expected_behavior[dim]:.2f}"
                )

        return novel_capabilities

    def compute_emergence_metrics(
        self,
        agent_subset: Optional[List[int]] = None
    ) -> EmergenceMetrics:
        """
        Compute comprehensive emergence metrics.

        Args:
            agent_subset: Agents to analyze

        Returns:
            Emergence metrics
        """
        # Compute metrics
        synergy = self.compute_synergy(agent_subset)
        integration = self.compute_integration(agent_subset)
        complexity = self.compute_complexity(agent_subset)

        # Detect phase
        phase, critical_threshold = self.detect_phase_transition('synergy')

        # Detect novel capabilities
        novel_capabilities = self.detect_novel_capabilities(agent_subset)

        metrics = EmergenceMetrics(
            synergy=synergy,
            integration=integration,
            complexity=complexity,
            phase=phase,
            novel_capabilities=novel_capabilities,
            critical_threshold=critical_threshold
        )

        # Store history
        self.synergy_history.append(synergy)
        self.complexity_history.append(complexity)
        self.phase_history.append(phase)

        return metrics

    def simulate_step(
        self,
        interaction_strength: float = 0.1,
        noise_level: float = 0.05
    ):
        """
        Simulate one step of agent interaction.

        Args:
            interaction_strength: Strength of agent influence
            noise_level: Random noise level
        """
        # Update behaviors based on interactions
        new_behaviors = []

        for agent in self.agents:
            # Get neighbors' behaviors
            neighbors = list(agent.connections)
            if neighbors:
                neighbor_behaviors = np.array([
                    self.agents[n].behavior for n in neighbors
                ])
                neighbor_influence = np.mean(neighbor_behaviors, axis=0)
            else:
                neighbor_influence = np.zeros_like(agent.behavior)

            # Update behavior
            # New behavior = old behavior + interaction influence + noise
            new_behavior = (
                agent.behavior +
                interaction_strength * (neighbor_influence - agent.behavior) +
                np.random.randn(len(agent.behavior)) * noise_level
            )

            # Normalize
            new_behavior = new_behavior / (np.linalg.norm(new_behavior) + 1e-10)

            new_behaviors.append(new_behavior)

        # Update agents
        for i, agent in enumerate(self.agents):
            agent.behavior = new_behaviors[i]

    def find_critical_threshold(
        self,
        topology: str = 'small_world',
        connection_probs: Optional[List[float]] = None,
        num_steps: int = 100
    ) -> Dict[str, float]:
        """
        Find critical threshold for emergence (phase transition).

        Args:
            topology: Network topology
            connection_probs: Connection probabilities to test
            num_steps: Simulation steps per probability

        Returns:
            Critical threshold information
        """
        if connection_probs is None:
            connection_probs = np.linspace(0.01, 0.5, 20)

        results = {
            'connection_probs': connection_probs,
            'synergies': [],
            'complexities': [],
            'phases': []
        }

        for conn_prob in connection_probs:
            # Reset and connect
            self.initialize_agents()
            self.connect_agents(topology=topology, connection_prob=conn_prob)

            # Simulate
            for _ in range(num_steps):
                self.simulate_step()

            # Compute metrics
            metrics = self.compute_emergence_metrics()

            results['synergies'].append(metrics.synergy)
            results['complexities'].append(metrics.complexity)
            results['phases'].append(metrics.phase)

        # Find critical point (maximum derivative)
        synergies = np.array(results['synergies'])
        if len(synergies) > 1:
            derivatives = np.diff(synergies)
            critical_idx = np.argmax(derivatives)
            critical_threshold = connection_probs[critical_idx]
        else:
            critical_threshold = connection_probs[0]

        results['critical_threshold'] = critical_threshold

        return results

    def visualize_emergence(
        self,
        metrics: EmergenceMetrics,
        save_path: Optional[str] = None
    ):
        """
        Visualize emergence metrics.

        Args:
            metrics: Emergence metrics
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Synergy history
        ax = axes[0, 0]
        if self.synergy_history:
            ax.plot(self.synergy_history, linewidth=2, label='Synergy')
            ax.axhline(np.mean(self.synergy_history), color='red',
                     linestyle='--', label='Mean')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Synergy')
        ax.set_title('Synergy Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Complexity history
        ax = axes[0, 1]
        if self.complexity_history:
            ax.plot(self.complexity_history, linewidth=2, color='purple',
                   label='Complexity')
            ax.axhline(np.mean(self.complexity_history), color='red',
                     linestyle='--', label='Mean')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Complexity')
        ax.set_title('Complexity Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Phase distribution
        ax = axes[1, 0]
        if self.phase_history:
            phase_counts = defaultdict(int)
            for phase in self.phase_history:
                phase_counts[phase] += 1

            ax.bar(phase_counts.keys(), phase_counts.values(), alpha=0.7)
            ax.set_ylabel('Count')
            ax.set_title('Phase Distribution')
            ax.tick_params(axis='x', rotation=45)

        # 4. Current metrics summary
        ax = axes[1, 1]
        ax.axis('off')

        summary_text = f"Current Metrics\n\n"
        summary_text += f"Synergy: {metrics.synergy:.4f}\n"
        summary_text += f"Integration: {metrics.integration:.4f}\n"
        summary_text += f"Complexity: {metrics.complexity:.4f}\n"
        summary_text += f"Phase: {metrics.phase}\n"
        summary_text += f"Critical Threshold: {metrics.critical_threshold:.4f}\n\n"

        if metrics.novel_capabilities:
            summary_text += "Novel Capabilities:\n"
            for cap in metrics.novel_capabilities[:5]:  # Show first 5
                summary_text += f"  - {cap}\n"
        else:
            summary_text += "No novel capabilities detected.\n"

        ax.text(0.1, 0.5, summary_text, fontsize=10, family='monospace')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_phase_transition(
        self,
        results: Dict[str, float],
        save_path: Optional[str] = None
    ):
        """
        Visualize phase transition analysis.

        Args:
            results: Results from find_critical_threshold
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        conn_probs = results['connection_probs']

        # 1. Synergy vs connection probability
        ax = axes[0, 0]
        ax.plot(conn_probs, results['synergies'], linewidth=2, marker='o')
        ax.axvline(results['critical_threshold'], color='red',
                  linestyle='--', label=f"Critical: {results['critical_threshold']:.3f}")
        ax.set_xlabel('Connection Probability')
        ax.set_ylabel('Synergy')
        ax.set_title('Synergy vs Connectivity')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Complexity vs connection probability
        ax = axes[0, 1]
        ax.plot(conn_probs, results['complexities'], linewidth=2,
               marker='s', color='purple')
        ax.axvline(results['critical_threshold'], color='red',
                  linestyle='--', label=f"Critical: {results['critical_threshold']:.3f}")
        ax.set_xlabel('Connection Probability')
        ax.set_ylabel('Complexity')
        ax.set_title('Complexity vs Connectivity')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Phase regions
        ax = axes[1, 0]
        phase_colors = {'subcritical': 'blue', 'critical': 'red', 'supercritical': 'green'}
        for i, phase in enumerate(results['phases']):
            ax.scatter(conn_probs[i], 0, c=phase_colors.get(phase, 'gray'),
                      s=100, alpha=0.6)
        ax.axvline(results['critical_threshold'], color='red',
                  linestyle='--', alpha=0.5)
        ax.set_xlabel('Connection Probability')
        ax.set_yticks([])
        ax.set_title('Phase Regions')
        ax.grid(True, alpha=0.3, axis='x')

        # 4. Derivative (rate of change)
        ax = axes[1, 1]
        if len(results['synergies']) > 1:
            derivatives = np.diff(results['synergies'])
            ax.plot(conn_probs[:-1], derivatives, linewidth=2, color='orange')
            ax.axhline(0, color='black', linestyle='-', alpha=0.3)
            ax.axvline(results['critical_threshold'], color='red',
                     linestyle='--', alpha=0.5)
        ax.set_xlabel('Connection Probability')
        ax.set_ylabel('d(Synergy)/d(Connection)')
        ax.set_title('Rate of Change')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_network_3d(
        self,
        metrics: EmergenceMetrics,
        save_path: Optional[str] = None
    ):
        """
        Visualize network in 3D with emergence information.

        Args:
            metrics: Emergence metrics
            save_path: Path to save figure
        """
        fig = plt.figure(figsize=(15, 10))

        # 3D network plot
        ax = fig.add_subplot(111, projection='3d')

        # Get positions
        pos = nx.spring_layout(self.network, dim=3, seed=42)

        # Extract coordinates
        xs = [pos[node][0] for node in self.network.nodes()]
        ys = [pos[node][1] for node in self.network.nodes()]
        zs = [pos[node][2] for node in self.network.nodes()]

        # Node colors based on capability diversity
        capabilities = np.array([agent.capabilities for agent in self.agents])
        diversity = np.std(capabilities, axis=1)

        # Plot nodes
        scatter = ax.scatter(xs, ys, zs, c=diversity, cmap='viridis',
                           s=100, alpha=0.8)

        # Plot edges
        for edge in self.network.edges():
            i, j = edge
            x_line = [pos[i][0], pos[j][0]]
            y_line = [pos[i][1], pos[j][1]]
            z_line = [pos[i][2], pos[j][2]]

            ax.plot(x_line, y_line, z_line, c='gray', alpha=0.3, linewidth=1)

        # Colorbar
        plt.colorbar(scatter, ax=ax, label='Capability Diversity')

        # Labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'3D Network Visualization\nPhase: {metrics.phase}, '
                    f'Synergy: {metrics.synergy:.4f}')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """Run demonstration simulations"""
    print("=" * 60)
    print("EMERGENCE DETECTION SIMULATION")
    print("=" * 60)

    # Create detector
    detector = EmergenceDetector(num_agents=50, capability_dim=10)

    print(f"\nConfiguration:")
    print(f"  Agents: {detector.num_agents}")
    print(f"  Capability dimensions: {detector.capability_dim}")

    # Initialize agents
    print("\nInitializing agents...")
    detector.initialize_agents(diversity=1.0, specialization=0.5)

    # Connect agents
    print("Connecting agents (small-world topology)...")
    detector.connect_agents(topology='small_world', connection_prob=0.1, avg_degree=6)

    # Simulate interactions
    print("Simulating agent interactions...")
    for step in range(100):
        detector.simulate_step(interaction_strength=0.1, noise_level=0.05)

        if step % 10 == 0:
            metrics = detector.compute_emergence_metrics()
            print(f"  Step {step}: Synergy={metrics.synergy:.4f}, "
                  f"Complexity={metrics.complexity:.4f}, Phase={metrics.phase}")

    # Final metrics
    final_metrics = detector.compute_emergence_metrics()
    print(f"\nFinal Metrics:")
    print(f"  Synergy: {final_metrics.synergy:.4f}")
    print(f"  Integration: {final_metrics.integration:.4f}")
    print(f"  Complexity: {final_metrics.complexity:.4f}")
    print(f"  Phase: {final_metrics.phase}")
    print(f"  Novel capabilities: {len(final_metrics.novel_capabilities)}")

    # Visualize emergence
    print("\nGenerating visualizations...")
    detector.visualize_emergence(final_metrics)
    detector.visualize_network_3d(final_metrics)

    # Find critical threshold
    print("\nFinding critical threshold...")
    threshold_results = detector.find_critical_threshold(
        topology='small_world',
        connection_probs=np.linspace(0.01, 0.3, 15),
        num_steps=50
    )

    print(f"\nCritical threshold: {threshold_results['critical_threshold']:.4f}")
    detector.visualize_phase_transition(threshold_results)

    print("\nSimulation complete!")


if __name__ == '__main__':
    main()
