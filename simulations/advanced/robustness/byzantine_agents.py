"""
POLLN Robustness Simulation: Byzantine Fault Tolerance
======================================================

This simulation tests POLLN's resilience against Byzantine (malicious) agents
that may send false information, collude, or attempt to manipulate the system.

Attack Types:
1. Liar agents: Send false values to manipulate outcomes
2. Flipper agents: Randomly flip decisions
3. Colluding agents: Coordinate attacks
4. Sybil agents: Create multiple identities
5. Gradient manipulation: Attempt to poison learning

Aggregation Strategies:
- Simple mean
- Median (robust to outliers)
- Trimmed mean (removes extremes)
- WELS (Weighted Elastic Least Squares)
- Clipping-based aggregation

Metrics:
- System performance vs attack fraction
- Convergence rate
- Final accuracy
- Detection rate of malicious agents
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import defaultdict
from scipy import stats


class AgentType(Enum):
    """Types of agents in the system"""
    HONEST = "honest"           # Normal, truthful agents
    LIAR = "liar"               # Always sends false values
    FLIPPER = "flipper"         # Randomly flips decisions
    COLLUDER = "colluder"       # Coordinates with other malicious agents
    SYBIL = "sybil"             # Multiple identities controlled by one attacker


class AggregationStrategy(Enum):
    """Strategies for aggregating agent outputs"""
    MEAN = "mean"                           # Simple average
    MEDIAN = "median"                       # Median value
    TRIMMED_MEAN = "trimmed_mean"           # Mean with outliers removed
    WELS = "wels"                           # Weighted Elastic Least Squares
    CLIPPING = "clipping"                   # Clip values to range
    WEIGHTED_MEDIAN = "weighted_median"     # Median with weights


@dataclass
class AgentState:
    """State of a single agent"""
    id: str
    agent_type: AgentType
    honest_value: float                     # True value if honest
    malicious_value: Optional[float]        # False value if malicious
    reputation: float = 1.0                 # Reputation score (0-1)
    weight: float = 1.0                     # Aggregation weight
    collusion_group: Optional[str] = None   # For colluding agents


@dataclass
class SimulationRound:
    """Results of a single simulation round"""
    round_number: int
    agent_values: List[float]
    aggregated_value: float
    true_value: float
    error: float
    detected_malicious: List[str]
    false_positives: List[str]


@dataclass
class ByzantineMetrics:
    """Overall metrics for Byzantine simulation"""
    total_rounds: int = 0
    avg_error: float = 0.0
    final_error: float = 0.0
    malicious_detection_rate: float = 0.0
    false_positive_rate: float = 0.0
    convergence_round: Optional[int] = None
    resilience_threshold: float = 0.0       # Max malicious fraction tolerated


class ByzantineSimulator:
    """
    Simulates Byzantine fault tolerance in POLLN agent networks

    Features:
    - Multiple attack types (liar, flipper, colluder, sybil)
    - Various aggregation strategies
    - Reputation tracking
    - Detection mechanisms
    - Resilience threshold analysis
    """

    def __init__(
        self,
        num_agents: int = 100,
        malicious_fraction: float = 0.2,
        aggregation_strategy: AggregationStrategy = AggregationStrategy.TRIMMED_MEAN,
        seed: int = 42
    ):
        """
        Initialize the Byzantine simulator

        Args:
            num_agents: Total number of agents
            malicious_fraction: Fraction of agents that are malicious
            aggregation_strategy: Strategy for aggregating agent outputs
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)

        self.num_agents = num_agents
        self.malicious_fraction = malicious_fraction
        self.aggregation_strategy = aggregation_strategy

        # Initialize agents
        self.agents = self._initialize_agents()

        # Simulation state
        self.rounds: List[SimulationRound] = []
        self.metrics = ByzantineMetrics()

        # Detection thresholds
        self.detection_threshold = 2.0  # Standard deviations from mean
        self.reputation_decay = 0.1     # How fast reputation decays

    def _initialize_agents(self) -> List[AgentState]:
        """Initialize agents with types and values"""
        agents = []

        # Calculate number of malicious agents
        num_malicious = int(self.num_agents * self.malicious_fraction)
        num_honest = self.num_agents - num_malicious

        # Create honest agents
        for i in range(num_honest):
            agents.append(AgentState(
                id=f"honest_{i}",
                agent_type=AgentType.HONEST,
                honest_value=np.random.normal(0, 1),
                malicious_value=None,
            ))

        # Create malicious agents
        malicious_types = [
            AgentType.LIAR,
            AgentType.FLIPPER,
            AgentType.COLLUDER,
        ]

        for i in range(num_malicious):
            agent_type = random.choice(malicious_types)
            honest_value = np.random.normal(0, 1)

            # Malicious value is opposite of honest value
            malicious_value = -honest_value + np.random.normal(0, 0.5)

            agent = AgentState(
                id=f"malicious_{i}",
                agent_type=agent_type,
                honest_value=honest_value,
                malicious_value=malicious_value,
                collusion_group=f"group_{i % 3}" if agent_type == AgentType.COLLUDER else None,
            )

            agents.append(agent)

        # Shuffle agents
        random.shuffle(agents)

        return agents

    def _get_agent_value(self, agent: AgentState, round_num: int) -> float:
        """Get the value an agent reports in a given round"""
        if agent.agent_type == AgentType.HONEST:
            # Add small noise
            return agent.honest_value + np.random.normal(0, 0.1)

        elif agent.agent_type == AgentType.LIAR:
            # Always report malicious value
            return agent.malicious_value + np.random.normal(0, 0.1)

        elif agent.agent_type == AgentType.FLIPPER:
            # Randomly flip between honest and malicious
            if random.random() < 0.5:
                return agent.honest_value + np.random.normal(0, 0.1)
            else:
                return agent.malicious_value + np.random.normal(0, 0.1)

        elif agent.agent_type == AgentType.COLLUDER:
            # Coordinate with collusion group
            # All colluders report similar values
            group_bias = {
                'group_0': 2.0,
                'group_1': -2.0,
                'group_2': 3.0,
            }.get(agent.collusion_group or '', 0.0)

            return agent.malicious_value + group_bias + np.random.normal(0, 0.1)

        return agent.honest_value

    def _aggregate_mean(self, values: List[float]) -> float:
        """Simple mean aggregation"""
        return np.mean(values)

    def _aggregate_median(self, values: List[float]) -> float:
        """Median aggregation (robust to outliers)"""
        return np.median(values)

    def _aggregate_trimmed_mean(self, values: List[float], trim_fraction: float = 0.2) -> float:
        """Trimmed mean aggregation (removes outliers)"""
        return stats.trim_mean(values, trim_fraction)

    def _aggregate_wels(self, values: List[float], weights: List[float]) -> float:
        """Weighted Elastic Least Squares aggregation"""
        # Normalize weights
        weights = np.array(weights) / np.sum(weights)

        # Weighted mean
        return np.average(values, weights=weights)

    def _aggregate_clipping(self, values: List[float]) -> float:
        """Clipping-based aggregation (clip to valid range)"""
        # Calculate mean and std
        mean = np.mean(values)
        std = np.std(values)

        # Clip values to [mean - 2*std, mean + 2*std]
        clipped = [np.clip(v, mean - 2*std, mean + 2*std) for v in values]

        return np.mean(clipped)

    def _aggregate_weighted_median(self, values: List[float], weights: List[float]) -> float:
        """Weighted median aggregation"""
        # Sort by value
        sorted_indices = np.argsort(values)
        sorted_values = [values[i] for i in sorted_indices]
        sorted_weights = [weights[i] for i in sorted_indices]

        # Find weighted median
        total_weight = sum(sorted_weights)
        cumulative_weight = 0

        for i, weight in enumerate(sorted_weights):
            cumulative_weight += weight
            if cumulative_weight >= total_weight / 2:
                return sorted_values[i]

        return sorted_values[-1]

    def _aggregate(self, values: List[float]) -> float:
        """Aggregate values using configured strategy"""
        if self.aggregation_strategy == AggregationStrategy.MEAN:
            return self._aggregate_mean(values)

        elif self.aggregation_strategy == AggregationStrategy.MEDIAN:
            return self._aggregate_median(values)

        elif self.aggregation_strategy == AggregationStrategy.TRIMMED_MEAN:
            return self._aggregate_trimmed_mean(values)

        elif self.aggregation_strategy == AggregationStrategy.WELS:
            weights = [agent.weight for agent in self.agents]
            return self._aggregate_wels(values, weights)

        elif self.aggregation_strategy == AggregationStrategy.CLIPPING:
            return self._aggregate_clipping(values)

        elif self.aggregation_strategy == AggregationStrategy.WEIGHTED_MEDIAN:
            weights = [agent.reputation for agent in self.agents]
            return self._aggregate_weighted_median(values, weights)

        return self._aggregate_mean(values)

    def _detect_malicious(self, values: List[float]) -> List[str]:
        """Detect potentially malicious agents"""
        detected = []

        if len(values) < 3:
            return detected

        # Calculate statistics
        mean = np.mean(values)
        std = np.std(values)

        # Detect outliers (more than threshold std from mean)
        for i, (agent, value) in enumerate(zip(self.agents, values)):
            if abs(value - mean) > self.detection_threshold * std:
                detected.append(agent.id)

        return detected

    def _update_reputations(self, values: List[float], detected: List[str]) -> None:
        """Update agent reputations based on behavior"""
        mean = np.mean(values)

        for agent, value in zip(self.agents, values):
            if agent.id in detected:
                # Decay reputation of detected agents
                agent.reputation *= (1 - self.reputation_decay)
            else:
                # Slightly boost reputation of non-detected agents
                agent.reputation = min(1.0, agent.reputation * 1.01)

            # Update weight based on reputation
            agent.weight = agent.reputation

    def simulate_round(self, round_num: int) -> SimulationRound:
        """Simulate a single round of agent interaction"""
        # Get values from all agents
        agent_values = [self._get_agent_value(agent, round_num) for agent in self.agents]

        # Aggregate values
        aggregated_value = self._aggregate(agent_values)

        # Calculate true value (mean of honest agents)
        honest_agents = [a for a in self.agents if a.agent_type == AgentType.HONEST]
        true_value = np.mean([a.honest_value for a in honest_agents])

        # Calculate error
        error = abs(aggregated_value - true_value)

        # Detect malicious agents
        detected_malicious = self._detect_malicious(agent_values)

        # Check for false positives (honest agents detected as malicious)
        false_positives = [
            agent_id for agent_id in detected_malicious
            if any(a.id == agent_id and a.agent_type == AgentType.HONEST for a in self.agents)
        ]

        # Update reputations
        self._update_reputations(agent_values, detected_malicious)

        return SimulationRound(
            round_number=round_num,
            agent_values=agent_values,
            aggregated_value=aggregated_value,
            true_value=true_value,
            error=error,
            detected_malicious=detected_malicious,
            false_positives=false_positives,
        )

    def run_simulation(self, num_rounds: int = 100) -> ByzantineMetrics:
        """
        Run complete simulation

        Args:
            num_rounds: Number of rounds to simulate

        Returns:
            ByzantineMetrics with aggregated results
        """
        print(f"Starting Byzantine Fault Tolerance Simulation...")
        print(f"Agents: {self.num_agents}")
        print(f"Malicious fraction: {self.malicious_fraction:.1%}")
        print(f"Aggregation strategy: {self.aggregation_strategy.value}")
        print(f"Rounds: {num_rounds}")
        print()

        self.rounds = []

        for round_num in range(num_rounds):
            round_result = self.simulate_round(round_num)
            self.rounds.append(round_result)

            # Check for convergence (error < threshold for 5 consecutive rounds)
            if round_num >= 5:
                recent_errors = [r.error for r in self.rounds[-5:]]
                if all(e < 0.1 for e in recent_errors):
                    self.metrics.convergence_round = round_num
                    break

        # Calculate metrics
        self._calculate_metrics()

        return self.metrics

    def _calculate_metrics(self) -> None:
        """Calculate aggregated metrics"""
        self.metrics.total_rounds = len(self.rounds)

        # Average error
        errors = [r.error for r in self.rounds]
        self.metrics.avg_error = np.mean(errors)

        # Final error
        self.metrics.final_error = self.rounds[-1].error

        # Malicious detection rate
        malicious_agents = [a for a in self.agents if a.agent_type != AgentType.HONEST]
        detected_malicious = set()

        for round_result in self.rounds:
            for agent_id in round_result.detected_malicious:
                if any(a.id == agent_id and a.agent_type != AgentType.HONEST for a in self.agents):
                    detected_malicious.add(agent_id)

        if len(malicious_agents) > 0:
            self.metrics.malicious_detection_rate = len(detected_malicious) / len(malicious_agents)

        # False positive rate
        total_detections = sum(len(r.detected_malicious) for r in self.rounds)
        total_false_positives = sum(len(r.false_positives) for r in self.rounds)

        if total_detections > 0:
            self.metrics.false_positive_rate = total_false_positives / total_detections

    def print_metrics(self) -> None:
        """Print formatted metrics"""
        print("\n" + "="*60)
        print("BYZANTINE FAULT TOLERANCE SIMULATION RESULTS")
        print("="*60)
        print(f"\nTotal Rounds:          {self.metrics.total_rounds}")
        print(f"Average Error:         {self.metrics.avg_error:.4f}")
        print(f"Final Error:           {self.metrics.final_error:.4f}")
        print(f"\nMalicious Detection:   {self.metrics.malicious_detection_rate:.1%}")
        print(f"False Positive Rate:   {self.metrics.false_positive_rate:.1%}")
        print(f"\nConvergence Round:     {self.metrics.convergence_round or 'Not converged'}")
        print("="*60 + "\n")

    def find_resilience_threshold(self) -> float:
        """
        Find maximum malicious fraction that system can tolerate

        Returns:
            Maximum malicious fraction where system still converges
        """
        print("\nFinding resilience threshold...")

        malicious_fractions = np.linspace(0.0, 0.5, 11)
        results = []

        for fraction in malicious_fractions:
            # Create new simulator with this fraction
            simulator = ByzantineSimulator(
                num_agents=self.num_agents,
                malicious_fraction=fraction,
                aggregation_strategy=self.aggregation_strategy,
            )

            # Run simulation
            metrics = simulator.run_simulation(num_rounds=50)

            # Check if converged
            converged = metrics.final_error < 0.5
            results.append((fraction, converged))

            print(f"  Malicious fraction: {fraction:.1%}, Converged: {converged}")

        # Find threshold (last fraction that converged)
        threshold = 0.0
        for fraction, converged in results:
            if converged:
                threshold = fraction

        self.metrics.resilience_threshold = threshold

        print(f"\nResilience threshold: {threshold:.1%}")
        print("System can tolerate up to this fraction of malicious agents")

        return threshold

    def generate_byzantine_config(self) -> Dict:
        """
        Generate Byzantine-resilient configuration recommendations

        Returns:
            Dictionary with configuration recommendations
        """
        recommendations = {
            'byzantine_tolerance': {
                'enabled': True,
                'max_malicious': self.metrics.resilience_threshold,
                'detection_enabled': True,
                'reputation_tracking': True,
            },
            'aggregation_strategy': self.aggregation_strategy.value,
            'detection_threshold': self.detection_threshold,
            'reputation_decay': self.reputation_decay,
            'recommendations': []
        }

        # Add specific recommendations
        if self.metrics.malicious_detection_rate < 0.8:
            recommendations['recommendations'].append(
                "Malicious detection rate below 80%. Consider tightening detection thresholds."
            )

        if self.metrics.false_positive_rate > 0.2:
            recommendations['recommendations'].append(
                "False positive rate above 20%. Consider relaxing detection thresholds."
            )

        if self.metrics.avg_error > 0.5:
            recommendations['recommendations'].append(
                "Average error high. Consider using more robust aggregation strategy (median, trimmed_mean)."
            )

        if self.metrics.resilience_threshold < 0.2:
            recommendations['recommendations'].append(
                "Resilience threshold below 20%. Increase agent diversity or use stronger aggregation."
            )

        # Strategy-specific recommendations
        if self.aggregation_strategy == AggregationStrategy.MEAN:
            recommendations['recommendations'].append(
                "Consider using MEDIAN or TRIMMED_MEAN for better Byzantine resilience."
            )

        return recommendations

    def save_results(self, filepath: str) -> None:
        """Save simulation results to JSON file"""
        results_data = {
            'configuration': {
                'num_agents': self.num_agents,
                'malicious_fraction': self.malicious_fraction,
                'aggregation_strategy': self.aggregation_strategy.value,
            },
            'metrics': {
                'total_rounds': self.metrics.total_rounds,
                'avg_error': self.metrics.avg_error,
                'final_error': self.metrics.final_error,
                'malicious_detection_rate': self.metrics.malicious_detection_rate,
                'false_positive_rate': self.metrics.false_positive_rate,
                'convergence_round': self.metrics.convergence_round,
                'resilience_threshold': self.metrics.resilience_threshold,
            },
            'agent_breakdown': self._get_agent_breakdown(),
            'byzantine_config': self.generate_byzantine_config(),
        }

        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to {filepath}")

    def _get_agent_breakdown(self) -> Dict:
        """Get breakdown of agent types"""
        breakdown = defaultdict(int)
        for agent in self.agents:
            breakdown[agent.agent_type.value] += 1
        return dict(breakdown)


def compare_strategies():
    """Compare different aggregation strategies"""
    print("\n" + "="*60)
    print("COMPARING AGGREGATION STRATEGIES")
    print("="*60 + "\n")

    strategies = [
        AggregationStrategy.MEAN,
        AggregationStrategy.MEDIAN,
        AggregationStrategy.TRIMMED_MEAN,
        AggregationStrategy.WELS,
        AggregationStrategy.CLIPPING,
    ]

    results = {}

    for strategy in strategies:
        print(f"\nTesting {strategy.value}...")

        simulator = ByzantineSimulator(
            num_agents=100,
            malicious_fraction=0.2,
            aggregation_strategy=strategy,
        )

        metrics = simulator.run_simulation(num_rounds=50)
        results[strategy.value] = {
            'avg_error': metrics.avg_error,
            'final_error': metrics.final_error,
        }

        simulator.print_metrics()

    # Print comparison
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    print(f"{'Strategy':<20} {'Avg Error':<15} {'Final Error':<15}")
    print("-"*60)

    for strategy, metrics in results.items():
        print(f"{strategy:<20} {metrics['avg_error']:<15.4f} {metrics['final_error']:<15.4f}")

    print("="*60 + "\n")

    return results


def main():
    """Main entry point for the simulation"""
    print("POLLN Byzantine Fault Tolerance Simulation")
    print("="*60)

    # Create simulator
    simulator = ByzantineSimulator(
        num_agents=100,
        malicious_fraction=0.2,
        aggregation_strategy=AggregationStrategy.TRIMMED_MEAN,
    )

    # Run simulation
    metrics = simulator.run_simulation(num_rounds=100)

    # Print results
    simulator.print_metrics()

    # Find resilience threshold
    threshold = simulator.find_resilience_threshold()

    # Generate config
    config = simulator.generate_byzantine_config()
    print("\nByzantine Configuration Recommendations:")
    print(json.dumps(config, indent=2))

    # Save results
    simulator.save_results('simulations/advanced/robustness/results/byzantine_results.json')

    return metrics


if __name__ == '__main__':
    main()
