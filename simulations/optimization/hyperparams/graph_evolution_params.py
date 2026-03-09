"""
Graph Evolution Parameters Optimization

Optimizes thresholds and rates for graph evolution in agent networks.
Finds optimal pruning thresholds, grafting rates, and clustering resolutions.

Optimization Targets:
- Pruning threshold: Remove weak connections [0.1, 0.2, 0.3, 0.4, 0.5]
  - Lower: More aggressive pruning (sparser graph)
  - Higher: More conservative (denser graph)

- Grafting rate: Add new connections [0.01, 0.05, 0.1, 0.2]
  - Higher: More exploration (faster graph growth)
  - Lower: More conservative (slower growth)

- Clustering resolution: Community detection granularity [0.5, 1.0, 1.5, 2.0]
  - Lower: Fewer, larger clusters
  - Higher: More, smaller clusters

Metrics:
- Graph Efficiency: Average shortest path / optimal path (lower is better)
- Communication Cost: Total messages per episode (lower is better)
- Emergence Quality: Novel behavior patterns discovered (higher is better)
- Stability: Rate of graph topology changes (lower is better)
"""

import numpy as np
import json
from typing import Dict, Tuple, List
from skopt import gp_minimize
from skopt.space import Real, Categorical
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict


# ============================================================================
# Graph Simulation Environment
# ============================================================================

class AgentGraph:
    """
    Simulates an evolving agent communication graph.
    """

    def __init__(self, n_agents: int = 50, initial_density: float = 0.1):
        self.n_agents = n_agents

        # Adjacency matrix (connection weights)
        self.adjacency = np.random.rand(n_agents, n_agents)
        self.adjacency = (self.adjacency < initial_density).astype(float)

        # Remove self-connections
        np.fill_diagonal(self.adjacency, 0)

        # Agent specializations (for clustering)
        self.specializations = np.random.randint(0, 5, n_agents)

        # Track evolution metrics
        self.topology_changes = 0
        self.messages_sent = 0

    def get_connections(self, agent: int) -> List[int]:
        """Get list of agents connected to given agent"""
        return np.where(self.adjacency[agent] > 0)[0].tolist()

    def add_edge(self, i: int, j: int):
        """Add edge between agents"""
        if self.adjacency[i, j] == 0:
            self.adjacency[i, j] = 1
            self.adjacency[j, i] = 1
            self.topology_changes += 1

    def remove_edge(self, i: int, j: int):
        """Remove edge between agents"""
        if self.adjacency[i, j] > 0:
            self.adjacency[i, j] = 0
            self.adjacency[j, i] = 0
            self.topology_changes += 1

    def prune_edges(self, threshold: float, activity_weights: np.ndarray):
        """
        Remove edges with weights below threshold.

        Args:
            threshold: Pruning threshold
            activity_weights: Recent activity level for each edge
        """
        n = self.n_agents
        for i in range(n):
            for j in range(i+1, n):
                if self.adjacency[i, j] > 0 and activity_weights[i, j] < threshold:
                    self.remove_edge(i, j)

    def graft_edges(self, rate: float):
        """
        Add new random edges based on grafting rate.

        Args:
            rate: Probability of adding new edge per agent pair
        """
        n = self.n_agents
        for i in range(n):
            for j in range(i+1, n):
                if self.adjacency[i, j] == 0 and np.random.rand() < rate:
                    # Prefer connecting to similar specializations
                    if self.specializations[i] == self.specializations[j]:
                        if np.random.rand() < 0.7:  # 70% prefer same specialization
                            self.add_edge(i, j)
                    else:
                        if np.random.rand() < 0.3:  # 30% cross-specialization
                            self.add_edge(i, j)

    def detect_communities(self, resolution: float = 1.0) -> Dict[int, int]:
        """
        Detect communities using simplified label propagation.

        Args:
            resolution: Clustering resolution parameter

        Returns:
            Dictionary mapping agent to community label
        """
        n = self.n_agents

        # Initialize with specializations
        labels = self.specializations.copy()

        # Label propagation iterations
        for _ in range(10):
            new_labels = labels.copy()
            for i in range(n):
                neighbors = self.get_connections(i)
                if neighbors:
                    # Count neighbor labels
                    neighbor_labels = [labels[n] for n in neighbors]
                    most_common = max(set(neighbor_labels), key=neighbor_labels.count)

                    # Resolution affects whether to change
                    if np.random.rand() < resolution:
                        new_labels[i] = most_common

            labels = new_labels

        return {i: labels[i] for i in range(n)}

    def compute_efficiency(self) -> float:
        """
        Compute graph efficiency (global efficiency).

        Returns:
            Average inverse shortest path length
        """
        n = self.n_agents

        # Compute all-pairs shortest paths
        distances = np.full((n, n), np.inf)
        np.fill_diagonal(distances, 0)

        # Initialize direct edges
        for i in range(n):
            for j in range(n):
                if self.adjacency[i, j] > 0:
                    distances[i, j] = 1

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if distances[i, k] + distances[k, j] < distances[i, j]:
                        distances[i, j] = distances[i, k] + distances[k, j]

        # Compute efficiency (average inverse distance)
        efficiency = 0
        count = 0
        for i in range(n):
            for j in range(n):
                if i != j and distances[i, j] < np.inf:
                    efficiency += 1.0 / distances[i, j]
                    count += 1

        return efficiency / count if count > 0 else 0

    def simulate_communication(self, n_steps: int = 100) -> int:
        """
        Simulate message passing through the graph.

        Returns:
            Total messages sent
        """
        total_messages = 0

        for _ in range(n_steps):
            # Random agent initiates communication
            source = np.random.randint(0, self.n_agents)

            # Message propagates to neighbors
            visited = {source}
            frontier = self.get_connections(source)

            while frontier:
                total_messages += len(frontier)
                new_frontier = []

                for agent in frontier:
                    neighbors = self.get_connections(agent)
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            new_frontier.append(neighbor)

                frontier = new_frontier

        self.messages_sent = total_messages
        return total_messages


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(
    pruning_threshold: float,
    grafting_rate: float,
    clustering_resolution: float,
    n_agents: int = 50,
    n_episodes: int = 100,
    seed: int = None
) -> Dict[str, float]:
    """
    Run graph evolution simulation with given parameters.

    Returns metrics on efficiency, communication cost, and emergence.
    """

    if seed is not None:
        np.random.seed(seed)

    # Create graph
    graph = AgentGraph(n_agents=n_agents, initial_density=0.1)

    # Track metrics over episodes
    efficiency_history = []
    communication_history = []
    stability_history = []

    # Run evolution
    for episode in range(n_episodes):
        # Generate random activity weights
        activity_weights = np.random.rand(n_agents, n_agents)

        # Prune edges
        graph.prune_edges(pruning_threshold, activity_weights)

        # Graft new edges
        graph.graft_edges(rafting_rate)

        # Detect communities
        communities = graph.detect_communities(resolution=clustering_resolution)

        # Compute metrics
        efficiency = graph.compute_efficiency()
        messages = graph.simulate_communication(n_steps=50)

        efficiency_history.append(efficiency)
        communication_history.append(messages)

        # Stability: rate of topology change
        if episode > 0:
            stability = graph.topology_changes / episode
            stability_history.append(stability)

    # Calculate final metrics
    avg_efficiency = np.mean(efficiency_history[-20:])
    avg_communication = np.mean(communication_history[-20:])
    avg_stability = np.mean(stability_history[-20:]) if stability_history else 0

    # Emergence quality: diversity of communities
    final_communities = graph.detect_communities(resolution=clustering_resolution)
    community_diversity = len(set(final_communities.values()))
    emergence_quality = community_diversity / 5.0  # Normalize by max communities

    return {
        'graph_efficiency': avg_efficiency,
        'communication_cost': avg_communication,
        'emergence_quality': emergence_quality,
        'stability': avg_stability,
        'final_edges': np.sum(graph.adjacency) / 2  # Divide by 2 for undirected
    }


# ============================================================================
# Bayesian Optimization
# ============================================================================

# Parameter search space
search_space = [
    Real(0.1, 0.5, name='pruning_threshold'),
    Real(0.01, 0.2, name='grafting_rate'),
    Real(0.5, 2.0, name='clustering_resolution')
]


@use_named_args(search_space)
def objective(**params) -> float:
    """Objective function for Bayesian optimization"""

    # Run simulation with 3 different random seeds
    results = []
    for seed in range(3):
        result = run_simulation(
            pruning_threshold=params['pruning_threshold'],
            grafting_rate=params['grafting_rate'],
            clustering_resolution=params['clustering_resolution'],
            n_agents=50,
            n_episodes=100,
            seed=seed
        )
        results.append(result)

    # Average results
    avg_efficiency = np.mean([r['graph_efficiency'] for r in results])
    avg_communication = np.mean([r['communication_cost'] for r in results])
    avg_emergence = np.mean([r['emergence_quality'] for r in results])
    avg_stability = np.mean([r['stability'] for r in results])

    # Weighted objective (lower is better)
    objective = (
        0.3 * (1.0 - avg_efficiency) +          # Efficiency (30% weight, maximize)
        0.3 * (avg_communication / 1000) +       # Communication (30% weight, minimize)
        0.2 * (1.0 - avg_emergence) +            # Emergence (20% weight, maximize)
        0.2 * avg_stability                      # Stability (20% weight, minimize)
    )

    return objective


def run_optimization(n_calls: int = 50) -> Tuple[Dict, Dict]:
    """Run Bayesian optimization to find optimal evolution parameters"""

    print("Starting Graph Evolution Parameters Optimization...")
    print(f"Running {n_calls} iterations of Bayesian optimization...")

    result = gp_minimize(
        objective,
        search_space,
        n_calls=n_calls,
        n_initial_points=15,
        random_state=42,
        verbose=True
    )

    best_params = {
        'pruning_threshold': result.x[0],
        'grafting_rate': result.x[1],
        'clustering_resolution': result.x[2]
    }

    print("\nOptimization complete!")
    print(f"Best parameters found:")
    print(f"  Pruning threshold: {best_params['pruning_threshold']:.4f}")
    print(f"  Grafting rate: {best_params['grafting_rate']:.4f}")
    print(f"  Clustering resolution: {best_params['clustering_resolution']:.4f}")
    print(f"  Objective value: {result.fun:.6f}")

    return best_params, result


# ============================================================================
# Results Analysis and Visualization
# ============================================================================

def plot_parameter_importance(result, output_dir: str):
    """Plot parameter importance based on optimization convergence"""

    # Extract parameter values and scores
    pruning_thresholds = [x[0] for x in result.x_iters]
    grafting_rates = [x[1] for x in result.x_iters]
    clustering_resolutions = [x[2] for x in result.x_iters]
    scores = result.func_vals

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Pruning threshold vs objective
    axes[0].scatter(pruning_thresholds, scores, alpha=0.6)
    axes[0].set_xlabel('Pruning Threshold')
    axes[0].set_ylabel('Objective Value')
    axes[0].set_title('Pruning Threshold Sensitivity')
    axes[0].grid(True, alpha=0.3)

    # Grafting rate vs objective
    axes[1].scatter(grafting_rates, scores, alpha=0.6)
    axes[1].set_xlabel('Grafting Rate')
    axes[1].set_ylabel('Objective Value')
    axes[1].set_title('Grafting Rate Sensitivity')
    axes[1].grid(True, alpha=0.3)

    # Clustering resolution vs objective
    axes[2].scatter(clustering_resolutions, scores, alpha=0.6)
    axes[2].set_xlabel('Clustering Resolution')
    axes[2].set_ylabel('Objective Value')
    axes[2].set_title('Clustering Resolution Sensitivity')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/graph_evolution_parameter_importance.png",
                dpi=300, bbox_inches='tight')
    print(f"Saved parameter importance plot to {output_dir}/graph_evolution_parameter_importance.png")


def plot_evolution_dynamics(best_params: Dict, output_dir: str):
    """Plot graph evolution dynamics with best parameters"""

    # Run detailed simulation
    np.random.seed(42)
    graph = AgentGraph(n_agents=50, initial_density=0.1)

    n_episodes = 100
    efficiency_history = []
    edges_history = []
    communities_history = []

    for episode in range(n_episodes):
        activity_weights = np.random.rand(50, 50)
        graph.prune_edges(best_params['pruning_threshold'], activity_weights)
        graph.graft_edges(best_params['grafting_rate'])

        efficiency = graph.compute_efficiency()
        n_edges = np.sum(graph.adjacency) / 2
        communities = graph.detect_communities(resolution=best_params['clustering_resolution'])
        n_communities = len(set(communities.values()))

        efficiency_history.append(efficiency)
        edges_history.append(n_edges)
        communities_history.append(n_communities)

    # Plot evolution
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    episodes = range(1, n_episodes + 1)

    axes[0].plot(episodes, efficiency_history, 'b-', linewidth=2)
    axes[0].set_ylabel('Graph Efficiency')
    axes[0].set_title('Graph Evolution with Optimized Parameters')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(episodes, edges_history, 'g-', linewidth=2)
    axes[1].set_ylabel('Number of Edges')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(episodes, communities_history, 'r-', linewidth=2)
    axes[2].set_ylabel('Number of Communities')
    axes[2].set_xlabel('Episode')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/graph_evolution_dynamics.png",
                dpi=300, bbox_inches='tight')
    print(f"Saved evolution dynamics plot to {output_dir}/graph_evolution_dynamics.png")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""

    # Create results directory
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Run optimization
    best_params, result = run_optimization(n_calls=50)

    # Validate best parameters
    print("\nValidating best parameters with multiple trials...")
    validation_results = []
    for seed in range(10):
        result_dict = run_simulation(
            pruning_threshold=best_params['pruning_threshold'],
            grafting_rate=best_params['grafting_rate'],
            clustering_resolution=best_params['clustering_resolution'],
            n_agents=50,
            n_episodes=100,
            seed=seed
        )
        validation_results.append(result_dict)

    # Calculate validation statistics
    metrics = ['graph_efficiency', 'communication_cost', 'emergence_quality',
               'stability', 'final_edges']
    validation_stats = {}

    for metric in metrics:
        values = [r[metric] for r in validation_results]
        validation_stats[metric] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }

    print("\nValidation Statistics:")
    for metric, stat in validation_stats.items():
        print(f"  {metric}: {stat['mean']:.4f} (+/- {stat['std']:.4f})")

    # Generate visualizations
    plot_parameter_importance(result, str(results_dir))
    plot_evolution_dynamics(best_params, str(results_dir))

    # Save results to JSON
    output = {
        'best_parameters': best_params,
        'optimization_objective': float(result.fun),
        'validation_statistics': validation_stats,
        'n_iterations': len(result.x_iters),
        'timestamp': str(pd.Timestamp.now())
    }

    output_path = results_dir / 'graph_evolution_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return best_params, validation_stats


if __name__ == '__main__':
    import pandas as pd  # For timestamp

    best_params, stats = main()
