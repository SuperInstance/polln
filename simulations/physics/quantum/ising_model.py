"""
Ising Model and QUBO Formulation for POLLN Optimization

This module maps POLLN optimization problems to Ising models and
Quadratic Unconstrained Binary Optimization (QUBO) formulations.

Key concepts:
- Ising Hamiltonian: H = -∑h_iσ_i^z - ∑J_ijσ_i^zσ_j^z
- QUBO: E(x) = ∑_i Q_ii x_i + ∑_i<j Q_ij x_i x_j
- Coupling matrix construction
- Energy landscape analysis

Author: POLLN Quantum Team
Date: 2026-03-07
"""

import numpy as np
from typing import Tuple, List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx

from deepseek_quantum import DeepSeekQuantumDeriver, QuantumDerivation


class SpinType(Enum):
    """Spin variable types."""
    ISING = 1  # σ_i ∈ {+1, -1}
    BINARY = 2  # x_i ∈ {0, 1}


@dataclass
class IsingModel:
    """Ising model representation."""
    num_spins: int
    external_fields: np.ndarray  # h_i
    coupling_matrix: np.ndarray  # J_ij
    spin_type: SpinType = SpinType.ISING

    def energy(self, spins: np.ndarray) -> float:
        """
        Calculate energy of spin configuration.

        Args:
            spins: Spin configuration vector

        Returns:
            Energy E = -∑h_iσ_i - ∑J_ijσ_iσ_j
        """
        if self.spin_type == SpinType.ISING:
            # Ising model: σ_i ∈ {±1}
            field_term = -np.dot(self.external_fields, spins)
            interaction_term = -spins @ self.coupling_matrix @ spins
            return field_term + interaction_term
        else:
            # Binary: x_i ∈ {0, 1}
            field_term = np.dot(self.external_fields, spins)
            interaction_term = spins @ self.coupling_matrix @ spins
            return field_term + interaction_term

    def get_hamiltonian_matrix(self) -> np.ndarray:
        """
        Get full Hamiltonian matrix.

        Returns:
            2^N × 2^N Hamiltonian matrix (for small N)
        """
        if self.num_spins > 15:
            raise ValueError(f"Too many spins ({self.num_spins}) for full Hamiltonian")

        dim = 2 ** self.num_spins
        H = np.zeros((dim, dim))

        for i in range(dim):
            # Convert i to spin configuration
            if self.spin_type == SpinType.ISING:
                spins = 2 * np.array([(i >> j) & 1 for j in range(self.num_spins)]) - 1
            else:
                spins = np.array([(i >> j) & 1 for j in range(self.num_spins)])

            H[i, i] = self.energy(spins)

        return H

    def spectral_gap(self) -> float:
        """
        Calculate spectral gap (energy difference between ground and first excited state).

        Returns:
            Spectral gap Δ = E_1 - E_0
        """
        H = self.get_hamiltonian_matrix()
        eigenvalues = np.linalg.eigvalsh(H)
        return eigenvalues[1] - eigenvalues[0] if len(eigenvalues) > 1 else 0.0


@dataclass
class QUBO:
    """Quadratic Unconstrained Binary Optimization formulation."""
    num_variables: int
    Q_matrix: np.ndarray

    def energy(self, x: np.ndarray) -> float:
        """
        Calculate QUBO objective value.

        Args:
            x: Binary vector x_i ∈ {0, 1}

        Returns:
            E(x) = ∑_i Q_ii x_i + ∑_i<j Q_ij x_i x_j
        """
        return x @ self.Q_matrix @ x

    def to_ising(self) -> IsingModel:
        """
        Convert QUBO to Ising model.

        Transformation: x_i = (1 - σ_i) / 2
        σ_i ∈ {±1}, x_i ∈ {0, 1}

        Returns:
            Equivalent IsingModel
        """
        n = self.num_variables
        h = np.zeros(n)
        J = np.zeros((n, n))

        for i in range(n):
            # Linear terms
            h[i] = -0.5 * self.Q_matrix[i, i]

            # Quadratic terms
            for j in range(i + 1, n):
                J[i, j] = -0.25 * (self.Q_matrix[i, j] + self.Q_matrix[j, i])

            # Self-interaction from diagonal
            h[i] -= 0.25 * self.Q_matrix[i, i]

            for j in range(n):
                if i != j:
                    h[i] -= 0.25 * (self.Q_matrix[i, j] + self.Q_matrix[j, i])

        return IsingModel(num_spins=n, external_fields=h, coupling_matrix=J)


class PollnIsingMapper:
    """
    Maps POLLN optimization problems to Ising models.

    Handles:
    - Agent selection problems
    - Resource allocation
    - Task assignment
    - Network optimization
    """

    def __init__(self, use_deepseek: bool = True):
        """
        Initialize POLLN-Ising mapper.

        Args:
            use_deepseek: Whether to use DeepSeek for advanced mappings
        """
        self.use_deepseek = use_deepseek
        if use_deepseek:
            self.deriver = DeepSeekQuantumDeriver()

    def map_agent_selection(self,
                           agent_utilities: np.ndarray,
                           budget: float,
                           agent_costs: np.ndarray,
                           diversity_penalty: float = 0.1) -> IsingModel:
        """
        Map agent selection problem to Ising model.

        Problem: Select K agents to maximize utility subject to budget constraint.
        Decision variables: σ_i ∈ {±1} (select if σ_i = +1)

        Args:
            agent_utilities: Utility values for each agent [u_1, ..., u_N]
            budget: Total budget available
            agent_costs: Cost for each agent [c_1, ..., c_N]
            diversity_penalty: Penalty for selecting similar agents

        Returns:
            IsingModel for agent selection
        """
        n = len(agent_utilities)
        h = np.zeros(n)
        J = np.zeros((n, n))

        # External fields from utility and cost
        # Higher utility → prefer selection (negative h to minimize energy)
        # Higher cost → discourage selection
        for i in range(n):
            # Normalize utility and cost
            utility_term = -agent_utilities[i] / np.max(agent_utilities)
            cost_term = agent_costs[i] / np.max(agent_costs) * (budget / np.sum(agent_costs))
            h[i] = utility_term + cost_term

        # Diversity penalty as coupling
        # Agents with similar capabilities should not both be selected
        for i in range(n):
            for j in range(i + 1, n):
                J[i, j] = diversity_penalty  # Positive J discourages same spin

        return IsingModel(num_spins=n, external_fields=h, coupling_matrix=J)

    def map_resource_allocation(self,
                               resources: np.ndarray,
                               demands: np.ndarray,
                               capacities: np.ndarray) -> IsingModel:
        """
        Map resource allocation to Ising model.

        Problem: Allocate resources to tasks to meet demands while respecting capacities.

        Args:
            resources: Available resources [R_1, ..., R_M]
            demands: Task demands [D_1, ..., D_N]
            capacities: Resource capacities [C_1, ..., C_M]

        Returns:
            IsingModel for resource allocation
        """
        m, n = len(resources), len(demands)
        total_vars = m * n

        h = np.zeros(total_vars)
        J = np.zeros((total_vars, total_vars))

        # Variable encoding: x_{i,j} = 1 if resource i allocated to task j
        # Convert to linear index: idx = i * n + j

        # Demand satisfaction (external fields)
        for j in range(n):
            for i in range(m):
                idx = i * n + j
                # Prefer allocations that satisfy demand
                h[idx] = -demands[j] / np.sum(demands)

        # Capacity constraints (couplings)
        for i in range(m):
            for j1 in range(n):
                for j2 in range(j1 + 1, n):
                    idx1 = i * n + j1
                    idx2 = i * n + j2
                    # Penalize exceeding capacity
                    J[idx1, idx2] = capacities[i] / np.sum(capacities)

        return IsingModel(num_spins=total_vars, external_fields=h, coupling_matrix=J)

    def map_task_assignment(self,
                           workers: np.ndarray,
                           tasks: np.ndarray,
                           skills: np.ndarray,
                           costs: np.ndarray) -> IsingModel:
        """
        Map task assignment to Ising model.

        Problem: Assign workers to tasks to maximize skill matching while minimizing cost.

        Args:
            workers: Number of workers
            tasks: Number of tasks
            skills: Skill matrix S[i,j] = skill of worker i for task j
            costs: Cost matrix C[i,j] = cost of worker i doing task j

        Returns:
            IsingModel for task assignment
        """
        n_workers, n_tasks = len(workers), len(tasks)
        total_vars = n_workers * n_tasks

        h = np.zeros(total_vars)
        J = np.zeros((total_vars, total_vars))

        # Skill matching (external fields)
        for i in range(n_workers):
            for j in range(n_tasks):
                idx = i * n_tasks + j
                # Higher skill → prefer assignment
                h[idx] = -skills[i, j] / np.max(skills)

        # Cost penalties (external fields)
        for i in range(n_workers):
            for j in range(n_tasks):
                idx = i * n_tasks + j
                h[idx] += costs[i, j] / np.max(costs)

        # Assignment constraints
        # Each worker does at most one task
        for i in range(n_workers):
            for j1 in range(n_tasks):
                for j2 in range(j1 + 1, n_tasks):
                    idx1 = i * n_tasks + j1
                    idx2 = i * n_tasks + j2
                    J[idx1, idx2] = 10.0  # Large penalty

        # Each task done by at most one worker
        for j in range(n_tasks):
            for i1 in range(n_workers):
                for i2 in range(i1 + 1, n_workers):
                    idx1 = i1 * n_tasks + j
                    idx2 = i2 * n_tasks + j
                    J[idx1, idx2] = 10.0

        return IsingModel(num_spins=total_vars, external_fields=h, coupling_matrix=J)

    def map_network_optimization(self,
                                 adjacency_matrix: np.ndarray,
                                 flow_demands: np.ndarray,
                                 capacity_constraints: np.ndarray) -> IsingModel:
        """
        Map network optimization to Ising model.

        Problem: Optimize routing in a network to maximize flow while respecting capacities.

        Args:
            adjacency_matrix: Network adjacency matrix
            flow_demands: Flow demands between node pairs
            capacity_constraints: Link capacities

        Returns:
            IsingModel for network optimization
        """
        n_nodes = adjacency_matrix.shape[0]
        n_edges = int(np.sum(adjacency_matrix > 0) / 2)

        # One variable per edge (used or not)
        h = np.zeros(n_edges)
        J = np.zeros((n_edges, n_edges))

        # Extract edges
        edges = []
        edge_idx = 0
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if adjacency_matrix[i, j] > 0:
                    edges.append((i, j))
                    edge_idx += 1

        # Flow demands (external fields)
        for k, (i, j) in enumerate(edges):
            # Prefer edges that satisfy demand
            h[k] = -flow_demands[i, j] / np.max(flow_demands)

        # Capacity constraints (couplings)
        for k1, (i1, j1) in enumerate(edges):
            for k2, (i2, j2) in enumerate(edges):
                if k1 < k2:
                    # Shared node → capacity competition
                    if i1 in (i2, j2) or j1 in (i2, j2):
                        J[k1, k2] = capacity_constraints[i1, j1] / np.max(capacity_constraints)

        return IsingModel(num_spins=n_edges, external_fields=h, coupling_matrix=J)

    def derive_advanced_mapping(self,
                                problem_description: str,
                                problem_params: Dict) -> IsingModel:
        """
        Use DeepSeek to derive advanced Ising mapping for complex problems.

        Args:
            problem_description: Text description of the problem
            problem_params: Problem parameters

        Returns:
            Custom IsingModel from DeepSeek derivation
        """
        if not self.use_deepseek:
            raise ValueError("DeepSeek not enabled. Set use_deepseek=True.")

        # Get derivation from DeepSeek
        derivation = self.deriver.derive_ising_model(problem_description)

        # Parse derivation to extract Hamiltonian
        # This would require more sophisticated parsing
        # For now, return a placeholder
        n = problem_params.get('num_variables', 10)
        h = np.random.randn(n)
        J = np.random.randn(n, n) * 0.1
        J = (J + J.T) / 2  # Make symmetric
        np.fill_diagonal(J, 0)

        return IsingModel(num_spins=n, external_fields=h, coupling_matrix=J)


def analyze_energy_landscape(model: IsingModel,
                            num_samples: int = 1000) -> Dict[str, Any]:
    """
    Analyze the energy landscape of an Ising model.

    Args:
        model: Ising model to analyze
        num_samples: Number of random configurations to sample

    Returns:
        Dictionary with landscape statistics
    """
    if model.num_spins > 20:
        # Use sampling for large systems
        energies = []
        for _ in range(num_samples):
            if model.spin_type == SpinType.ISING:
                spins = np.random.choice([-1, 1], size=model.num_spins)
            else:
                spins = np.random.choice([0, 1], size=model.num_spins)
            energies.append(model.energy(spins))

        energies = np.array(energies)
    else:
        # Exact enumeration for small systems
        dim = 2 ** model.num_spins
        energies = []
        for i in range(dim):
            if model.spin_type == SpinType.ISING:
                spins = 2 * np.array([(i >> j) & 1 for j in range(model.num_spins)]) - 1
            else:
                spins = np.array([(i >> j) & 1 for j in range(model.num_spins)])
            energies.append(model.energy(spins))
        energies = np.array(energies)

    return {
        'min_energy': np.min(energies),
        'max_energy': np.max(energies),
        'mean_energy': np.mean(energies),
        'std_energy': np.std(energies),
        'energy_range': np.max(energies) - np.min(energies),
        'num_minima': np.sum(np.isclose(energies, np.min(energies))),
        'ruggedness': np.std(np.diff(np.sort(energies)[:100])) if len(energies) > 1 else 0
    }


def visualize_energy_landscape(model: IsingModel,
                               dims_to_plot: int = 2,
                               grid_size: int = 100) -> plt.Figure:
    """
    Visualize energy landscape (for low-dimensional projections).

    Args:
        model: Ising model
        dims_to_plot: Number of dimensions to plot (2 or 3)
        grid_size: Resolution of grid

    Returns:
        Matplotlib figure
    """
    if model.num_spins < 2:
        raise ValueError("Need at least 2 spins to visualize")

    # Fix all but 2 spins to their mean value
    # and vary the remaining 2

    fig = plt.figure(figsize=(12, 5))

    if dims_to_plot == 2:
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122, projection='3d')

        # 2D contour plot
        if model.num_spins >= 2:
            x = np.linspace(-1, 1, grid_size)
            y = np.linspace(-1, 1, grid_size)
            X, Y = np.meshgrid(x, y)

            Z = np.zeros_like(X)
            for i in range(grid_size):
                for j in range(grid_size):
                    spins = np.zeros(model.num_spins)
                    spins[0] = X[i, j]
                    spins[1] = Y[i, j]
                    # Set other spins to 0 (mean)
                    Z[i, j] = model.energy(spins)

            # Contour plot
            contour = ax1.contourf(X, Y, Z, levels=20, cmap='viridis')
            ax1.set_xlabel('Spin 1')
            ax1.set_ylabel('Spin 2')
            ax1.set_title('Energy Landscape (Contour)')
            plt.colorbar(contour, ax=ax1, label='Energy')

            # 3D surface plot
            surf = ax2.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax2.set_xlabel('Spin 1')
            ax2.set_ylabel('Spin 2')
            ax2.set_zlabel('Energy')
            ax2.set_title('Energy Landscape (3D)')
            plt.colorbar(surf, ax=ax2, label='Energy')

    plt.tight_layout()
    return fig


def visualize_coupling_network(model: IsingModel) -> plt.Figure:
    """
    Visualize coupling matrix as a network graph.

    Args:
        model: Ising model

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create network graph
    G = nx.Graph()

    # Add nodes
    for i in range(model.num_spins):
        G.add_node(i, field=model.external_fields[i])

    # Add edges for significant couplings
    threshold = np.std(model.coupling_matrix)
    for i in range(model.num_spins):
        for j in range(i + 1, model.num_spins):
            if abs(model.coupling_matrix[i, j]) > threshold:
                G.add_edge(i, j, weight=model.coupling_matrix[i, j])

    # Layout
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes
    node_colors = [model.external_fields[i] for i in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          cmap='coolwarm', node_size=500,
                          alpha=0.8, ax=ax)

    # Draw edges
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=2,
                          edge_color=edge_weights,
                          edge_cmap='coolwarm', ax=ax)

    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax)

    ax.set_title('Ising Model Coupling Network')
    ax.axis('off')

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap='coolwarm',
                               norm=plt.Normalize(vmin=min(node_colors),
                                                vmax=max(node_colors)))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='External Field')

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Example: Agent selection problem
    print("Creating Ising model for POLLN agent selection...")

    mapper = PollnIsingMapper(use_deepseek=True)

    # Generate synthetic data
    n_agents = 10
    utilities = np.random.rand(n_agents)
    costs = np.random.rand(n_agents) * 100
    budget = 500

    # Map to Ising model
    ising_model = mapper.map_agent_selection(
        agent_utilities=utilities,
        budget=budget,
        agent_costs=costs,
        diversity_penalty=0.1
    )

    print(f"\nIsing Model:")
    print(f"  Number of spins: {ising_model.num_spins}")
    print(f"  External fields: {ising_model.external_fields[:5]}...")
    print(f"  Coupling matrix shape: {ising_model.coupling_matrix.shape}")

    # Analyze energy landscape
    print("\nAnalyzing energy landscape...")
    landscape = analyze_energy_landscape(ising_model)
    for key, value in landscape.items():
        print(f"  {key}: {value:.4f}")

    # Calculate spectral gap
    if ising_model.num_spins <= 10:
        gap = ising_model.spectral_gap()
        print(f"\nSpectral gap: {gap:.4f}")

    # Visualize
    print("\nGenerating visualizations...")
    os.makedirs("results", exist_ok=True)

    # Energy landscape
    fig1 = visualize_energy_landscape(ising_model)
    fig1.savefig("results/ising_energy_landscape.png")
    plt.close(fig1)

    # Coupling network
    fig2 = visualize_coupling_network(ising_model)
    fig2.savefig("results/ising_coupling_network.png")
    plt.close(fig2)

    print("\nVisualizations saved to results/")

    # Test QUBO conversion
    print("\nTesting QUBO conversion...")
    qubo = QUBO(num_variables=n_agents, Q_matrix=ising_model.coupling_matrix)
    converted_ising = qubo.to_ising()
    print(f"  Converted Ising model spins: {converted_ising.num_spins}")

    print("\nDone!")
