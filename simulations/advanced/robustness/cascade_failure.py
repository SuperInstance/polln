"""
POLLN Robustness Simulation: Cascading Failure
==============================================

This simulation tests POLLN's resilience against cascading failures where
the failure of one component triggers failures in dependent components.

Failure Types:
1. Agent crash: Single agent stops responding
2. Network partition: Communication breakdown between subsets
3. Resource exhaustion: CPU, memory, or network saturation
4. Dependency failure: Downstream service fails
5. Load surge: Sudden spike in requests

Containment Strategies:
1. Circuit breaking: Stop propagating failures
2. Rate limiting: Prevent overload
3. Bulkheading: Isolate failures to compartments
4. Timeouts: Fail fast on hung requests
5. Retry with exponential backoff: Handle transient failures

Metrics:
- Failure propagation rate
- Containment effectiveness
- System recovery time
- Percentage of agents affected
- Final system state
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import defaultdict, deque
import networkx as nx
from dataclasses import dataclass


class FailureType(Enum):
    """Types of failures that can occur"""
    AGENT_CRASH = "agent_crash"                   # Agent stops responding
    NETWORK_PARTITION = "network_partition"       # Communication breakdown
    RESOURCE_EXHAUSTION = "resource_exhaustion"   # CPU/memory/network saturation
    DEPENDENCY_FAILURE = "dependency_failure"     # Downstream service fails
    LOAD_SURGE = "load_surge"                     # Sudden request spike
    TIMEOUT = "timeout"                           # Request timeout


class ContainmentStrategy(Enum):
    """Strategies to contain cascading failures"""
    CIRCUIT_BREAKER = "circuit_breaker"          # Open circuit on failures
    RATE_LIMITING = "rate_limiting"              # Limit request rate
    BULKHEADING = "bulkheading"                  # Isolate compartments
    TIMEOUT = "timeout"                          # Fail fast
    RETRY_BACKOFF = "retry_backoff"              # Exponential backoff
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Reduce quality


class AgentStatus(Enum):
    """Status of an agent"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    ISOLATED = "isolated"


@dataclass
class FailureEvent:
    """A failure event in the system"""
    timestamp: float
    agent_id: str
    failure_type: FailureType
    triggered_by: Optional[str] = None  # Agent that triggered this failure
    cascade_depth: int = 0


@dataclass
class AgentState:
    """State of a single agent"""
    id: str
    status: AgentStatus
    load: float  # 0-1 scale
    failure_threshold: float  # Load threshold for failure
    connections: Set[str]  # Connected agents
    circuit_breaker_open: bool = False
    circuit_breaker_count: int = 0
    last_failure_time: Optional[float] = None


@dataclass
class CascadeMetrics:
    """Metrics for cascading failure simulation"""
    total_failures: int = 0
    cascade_depth: int = 0
    agents_affected: int = 0
    failure_propagation_rate: float = 0.0
    containment_effectiveness: float = 0.0
    recovery_time_ms: float = 0.0
    final_healthy_percentage: float = 0.0


class CascadingFailureSimulator:
    """
    Simulates cascading failures in POLLN agent networks

    Features:
    - Agent dependency graph
    - Multiple failure types
    - Various containment strategies
    - Circuit breaking
    - Rate limiting
    - Bulkheading
    """

    def __init__(
        self,
        num_agents: int = 100,
        graph_type: str = "scale_free",  # "scale_free", "random", "small_world"
        initial_failure_rate: float = 0.05,
        containment_strategies: List[ContainmentStrategy] = None,
        seed: int = 42
    ):
        """
        Initialize the cascading failure simulator

        Args:
            num_agents: Number of agents in the system
            graph_type: Type of dependency graph
            initial_failure_rate: Fraction of agents that initially fail
            containment_strategies: List of containment strategies to employ
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)

        self.num_agents = num_agents
        self.initial_failure_rate = initial_failure_rate
        self.containment_strategies = containment_strategies or [
            ContainmentStrategy.CIRCUIT_BREAKER,
            ContainmentStrategy.RATE_LIMITING,
        ]

        # Build agent dependency graph
        self.graph = self._build_graph(graph_type)

        # Initialize agents
        self.agents = self._initialize_agents()

        # Simulation state
        self.failure_events: List[FailureEvent] = []
        self.metrics = CascadeMetrics()

        # Containment parameters
        self.circuit_breaker_threshold = 5  # Failures before opening circuit
        self.circuit_breaker_timeout = 10.0  # Seconds before closing circuit
        self.rate_limit = 100  # Max requests per second
        self.bulkhead_compartments = 5  # Number of isolated compartments

        # Current time
        self.current_time = 0.0

    def _build_graph(self, graph_type: str) -> nx.Graph:
        """Build agent dependency graph"""
        if graph_type == "scale_free":
            # Scale-free network (few highly connected hubs)
            graph = nx.barabasi_albert_graph(self.num_agents, 3)
        elif graph_type == "random":
            # Random graph
            graph = nx.erdos_renyi_graph(self.num_agents, 0.1)
        elif graph_type == "small_world":
            # Small-world network
            graph = nx.watts_strogatz_graph(self.num_agents, 6, 0.1)
        else:
            graph = nx.erdos_renyi_graph(self.num_agents, 0.1)

        return graph

    def _initialize_agents(self) -> Dict[str, AgentState]:
        """Initialize agent states"""
        agents = {}

        for node in self.graph.nodes():
            connections = set(self.graph.neighbors(node))

            agents[str(node)] = AgentState(
                id=str(node),
                status=AgentStatus.HEALTHY,
                load=random.uniform(0.1, 0.5),
                failure_threshold=random.uniform(0.7, 0.9),
                connections=connections,
            )

        return agents

    def _trigger_initial_failures(self) -> List[str]:
        """Trigger initial failures"""
        num_failures = int(self.num_agents * self.initial_failure_rate)
        failed_agents = random.sample(list(self.agents.keys()), num_failures)

        for agent_id in failed_agents:
            self._fail_agent(agent_id, FailureType.AGENT_CRASH, None, 0)

        return failed_agents

    def _fail_agent(
        self,
        agent_id: str,
        failure_type: FailureType,
        triggered_by: Optional[str],
        cascade_depth: int
    ) -> None:
        """Mark an agent as failed"""
        agent = self.agents[agent_id]

        if agent.status == AgentStatus.FAILED:
            return  # Already failed

        agent.status = AgentStatus.FAILED

        # Record failure event
        event = FailureEvent(
            timestamp=self.current_time,
            agent_id=agent_id,
            failure_type=failure_type,
            triggered_by=triggered_by,
            cascade_depth=cascade_depth,
        )

        self.failure_events.append(event)
        self.metrics.total_failures += 1

        # Update cascade depth
        self.metrics.cascade_depth = max(self.metrics.cascade_depth, cascade_depth)

    def _propagate_failure(self, failed_agent_id: str) -> List[str]:
        """Propagate failure to connected agents"""
        newly_failed = []

        agent = self.agents[failed_agent_id]

        # Check containment strategies
        if ContainmentStrategy.CIRCUIT_BREAKER in self.containment_strategies:
            if self._should_open_circuit_breaker(failed_agent_id):
                # Circuit breaker open - don't propagate
                return newly_failed

        # Propagate to connected agents
        for connected_id in agent.connections:
            connected_agent = self.agents[connected_id]

            if connected_agent.status == AgentStatus.HEALTHY:
                # Increase load on connected agent
                connected_agent.load += 0.2

                # Check if agent should fail
                if connected_agent.load > connected_agent.failure_threshold:
                    # Determine cascade depth
                    cascade_depth = 0
                    if failed_agent_id in [e.agent_id for e in self.failure_events]:
                        last_event = [e for e in self.failure_events if e.agent_id == failed_agent_id][-1]
                        cascade_depth = last_event.cascade_depth + 1

                    # Fail the agent
                    self._fail_agent(
                        connected_id,
                        FailureType.DEPENDENCY_FAILURE,
                        failed_agent_id,
                        cascade_depth,
                    )

                    newly_failed.append(connected_id)

                    # Apply circuit breaker
                    if ContainmentStrategy.CIRCUIT_BREAKER in self.containment_strategies:
                        connected_agent.circuit_breaker_count += 1
                        if connected_agent.circuit_breaker_count >= self.circuit_breaker_threshold:
                            connected_agent.circuit_breaker_open = True

        return newly_failed

    def _should_open_circuit_breaker(self, agent_id: str) -> bool:
        """Check if circuit breaker should be opened"""
        agent = self.agents[agent_id]

        # Check if circuit breaker is already open
        if agent.circuit_breaker_open:
            # Check if timeout has passed
            if agent.last_failure_time:
                if self.current_time - agent.last_failure_time > self.circuit_breaker_timeout:
                    # Close circuit breaker
                    agent.circuit_breaker_open = False
                    agent.circuit_breaker_count = 0
                    return False
            return True

        return False

    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to prevent overload"""
        if ContainmentStrategy.RATE_LIMITING not in self.containment_strategies:
            return

        for agent in self.agents.values():
            if agent.status == AgentStatus.HEALTHY:
                # Rate limit: cap load at threshold
                if agent.load > agent.failure_threshold * 0.8:
                    agent.load = agent.failure_threshold * 0.8

    def _apply_bulkheading(self) -> None:
        """Apply bulkheading to isolate failures"""
        if ContainmentStrategy.BULKHEADING not in self.containment_strategies:
            return

        # Divide agents into compartments
        compartment_size = self.num_agents // self.bulkhead_compartments

        for i in range(self.bulkhead_compartments):
            start_idx = i * compartment_size
            end_idx = start_idx + compartment_size if i < self.bulkhead_compartments - 1 else self.num_agents

            # Get agents in this compartment
            compartment_agents = [
                str(j) for j in range(start_idx, end_idx)
            ]

            # Check if any agent in compartment is failed
            compartment_failed = any(
                self.agents[agent_id].status == AgentStatus.FAILED
                for agent_id in compartment_agents
            )

            # If compartment has failures, isolate it
            if compartment_failed:
                for agent_id in compartment_agents:
                    if self.agents[agent_id].status == AgentStatus.HEALTHY:
                        self.agents[agent_id].status = AgentStatus.ISOLATED

    def _simulate_step(self) -> bool:
        """Simulate one step of cascade propagation"""
        newly_failed = []

        # Get failed agents from this step
        failed_agents = [
            agent_id for agent_id, agent in self.agents.items()
            if agent.status == AgentStatus.FAILED
        ]

        # Propagate failures
        for failed_agent_id in failed_agents:
            propagated = self._propagate_failure(failed_agent_id)
            newly_failed.extend(propagated)

        # Apply containment strategies
        self._apply_rate_limiting()
        self._apply_bulkheading()

        # Update time
        self.current_time += 1.0

        # Check if cascade has stopped
        return len(newly_failed) > 0

    def run_simulation(self, max_steps: int = 100) -> CascadeMetrics:
        """
        Run complete cascading failure simulation

        Args:
            max_steps: Maximum number of simulation steps

        Returns:
            CascadeMetrics with aggregated results
        """
        print("Starting Cascading Failure Simulation...")
        print(f"Agents: {self.num_agents}")
        print(f"Initial failure rate: {self.initial_failure_rate:.1%}")
        print(f"Containment strategies: {[s.value for s in self.containment_strategies]}")
        print()

        # Trigger initial failures
        initial_failures = self._trigger_initial_failures()
        print(f"Initial failures: {len(initial_failures)} agents")

        # Simulate cascade propagation
        cascade_active = True
        step = 0

        while cascade_active and step < max_steps:
            cascade_active = self._simulate_step()
            step += 1

            if step % 10 == 0:
                failed_count = sum(
                    1 for agent in self.agents.values()
                    if agent.status == AgentStatus.FAILED
                )
                print(f"Step {step}: {failed_count} agents failed")

        print(f"\nCascade stopped after {step} steps")

        # Calculate metrics
        self._calculate_metrics()

        return self.metrics

    def _calculate_metrics(self) -> None:
        """Calculate aggregated metrics"""
        # Count affected agents
        affected_count = sum(
            1 for agent in self.agents.values()
            if agent.status in [AgentStatus.FAILED, AgentStatus.ISOLATED]
        )

        self.metrics.agents_affected = affected_count

        # Calculate failure propagation rate
        if self.metrics.total_failures > 1:
            self.metrics.failure_propagation_rate = (
                self.metrics.total_failures / self.metrics.cascade_depth
                if self.metrics.cascade_depth > 0
                else 0
            )

        # Calculate containment effectiveness
        # High effectiveness = low propagation rate and few affected agents
        max_possible_failures = self.num_agents
        containment_score = 1.0 - (affected_count / max_possible_failures)
        self.metrics.containment_effectiveness = containment_score

        # Calculate final healthy percentage
        healthy_count = sum(
            1 for agent in self.agents.values()
            if agent.status == AgentStatus.HEALTHY
        )

        self.metrics.final_healthy_percentage = healthy_count / self.num_agents

        # Recovery time (proportional to cascade depth)
        self.metrics.recovery_time_ms = self.metrics.cascade_depth * 100

    def print_metrics(self) -> None:
        """Print formatted metrics"""
        print("\n" + "="*60)
        print("CASCADING FAILURE SIMULATION RESULTS")
        print("="*60)
        print(f"\nTotal Failures:        {self.metrics.total_failures}")
        print(f"Agents Affected:       {self.metrics.agents_affected} ({self.metrics.agents_affected/self.num_agents:.1%})")
        print(f"Cascade Depth:         {self.metrics.cascade_depth}")
        print(f"Propagation Rate:      {self.metrics.failure_propagation_rate:.2f} failures/level")
        print(f"Containment Effective: {self.metrics.containment_effectiveness:.1%}")
        print(f"Final Healthy:         {self.metrics.final_healthy_percentage:.1%}")
        print(f"Recovery Time:         {self.metrics.recovery_time_ms:.0f} ms")
        print("="*60 + "\n")

    def generate_cascade_config(self) -> Dict:
        """
        Generate cascade prevention configuration

        Returns:
            Dictionary with configuration recommendations
        """
        recommendations = {
            'cascade_prevention': {
                'rate_limiting': ContainmentStrategy.RATE_LIMITING in self.containment_strategies,
                'circuit_breaking': ContainmentStrategy.CIRCUIT_BREAKER in self.containment_strategies,
                'bulkheading': ContainmentStrategy.BULKHEADING in self.containment_strategies,
                'max_cascade_depth': self.metrics.cascade_depth,
            },
            'circuit_breaker': {
                'enabled': True,
                'failure_threshold': self.circuit_breaker_threshold,
                'timeout_ms': int(self.circuit_breaker_timeout * 1000),
                'half_open_attempts': 3,
            },
            'rate_limiter': {
                'enabled': True,
                'max_requests_per_second': self.rate_limit,
                'burst_size': self.rate_limit * 2,
            },
            'bulkhead': {
                'enabled': ContainmentStrategy.BULKHEADING in self.containment_strategies,
                'compartments': self.bulkhead_compartments,
                'max_per_compartment': self.num_agents // self.bulkhead_compartments,
            },
            'recommendations': []
        }

        # Add specific recommendations
        if self.metrics.containment_effectiveness < 0.7:
            recommendations['recommendations'].append(
                "Containment effectiveness below 70%. Add more containment strategies."
            )

        if self.metrics.agents_affected > self.num_agents * 0.5:
            recommendations['recommendations'].append(
                "More than 50% of agents affected. Implement bulkheading to isolate failures."
            )

        if self.metrics.cascade_depth > 10:
            recommendations['recommendations'].append(
                f"Cascade depth ({self.metrics.cascade_depth}) too high. Implement circuit breakers."
            )

        if self.metrics.final_healthy_percentage < 0.5:
            recommendations['recommendations'].append(
                "Less than 50% agents remaining healthy. Review failure thresholds and add redundancy."
            )

        return recommendations

    def save_results(self, filepath: str) -> None:
        """Save simulation results to JSON file"""
        # Get status breakdown
        status_breakdown = defaultdict(int)
        for agent in self.agents.values():
            status_breakdown[agent.status.value] += 1

        results_data = {
            'configuration': {
                'num_agents': self.num_agents,
                'initial_failure_rate': self.initial_failure_rate,
                'containment_strategies': [s.value for s in self.containment_strategies],
            },
            'metrics': {
                'total_failures': self.metrics.total_failures,
                'cascade_depth': self.metrics.cascade_depth,
                'agents_affected': self.metrics.agents_affected,
                'failure_propagation_rate': self.metrics.failure_propagation_rate,
                'containment_effectiveness': self.metrics.containment_effectiveness,
                'recovery_time_ms': self.metrics.recovery_time_ms,
                'final_healthy_percentage': self.metrics.final_healthy_percentage,
            },
            'status_breakdown': dict(status_breakdown),
            'cascade_config': self.generate_cascade_config(),
        }

        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to {filepath}")


def compare_containment_strategies():
    """Compare different containment strategies"""
    print("\n" + "="*60)
    print("COMPARING CONTAINMENT STRATEGIES")
    print("="*60 + "\n")

    strategy_combinations = [
        [],  # No containment
        [ContainmentStrategy.CIRCUIT_BREAKER],
        [ContainmentStrategy.RATE_LIMITING],
        [ContainmentStrategy.BULKHEADING],
        [ContainmentStrategy.CIRCUIT_BREAKER, ContainmentStrategy.RATE_LIMITING],
        [ContainmentStrategy.CIRCUIT_BREAKER, ContainmentStrategy.BULKHEADING],
        [ContainmentStrategy.RATE_LIMITING, ContainmentStrategy.BULKHEADING],
        [ContainmentStrategy.CIRCUIT_BREAKER, ContainmentStrategy.RATE_LIMITING, ContainmentStrategy.BULKHEADING],
    ]

    results = {}

    for strategies in strategy_combinations:
        strategy_name = "+".join([s.value for s in strategies]) if strategies else "none"
        print(f"\nTesting {strategy_name}...")

        simulator = CascadingFailureSimulator(
            num_agents=100,
            initial_failure_rate=0.05,
            containment_strategies=strategies,
        )

        metrics = simulator.run_simulation(max_steps=100)
        results[strategy_name] = {
            'total_failures': metrics.total_failures,
            'agents_affected': metrics.agents_affected,
            'containment_effectiveness': metrics.containment_effectiveness,
            'final_healthy_percentage': metrics.final_healthy_percentage,
        }

        simulator.print_metrics()

    # Print comparison
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    print(f"{'Strategy':<50} {'Failures':<10} {'Affected':<10} {'Effective':<10} {'Healthy':<10}")
    print("-"*90)

    for strategy, metrics in results.items():
        print(f"{strategy:<50} {metrics['total_failures']:<10} {metrics['agents_affected']:<10} "
              f"{metrics['containment_effectiveness']:<10.1%} {metrics['final_healthy_percentage']:<10.1%}")

    print("="*90 + "\n")

    return results


def main():
    """Main entry point for the simulation"""
    print("POLLN Cascading Failure Simulation")
    print("="*60)

    # Create simulator with multiple containment strategies
    simulator = CascadingFailureSimulator(
        num_agents=100,
        initial_failure_rate=0.05,
        containment_strategies=[
            ContainmentStrategy.CIRCUIT_BREAKER,
            ContainmentStrategy.RATE_LIMITING,
            ContainmentStrategy.BULKHEADING,
        ],
    )

    # Run simulation
    metrics = simulator.run_simulation(max_steps=100)

    # Print results
    simulator.print_metrics()

    # Generate config
    config = simulator.generate_cascade_config()
    print("\nCascade Prevention Configuration:")
    print(json.dumps(config, indent=2))

    # Save results
    simulator.save_results('simulations/advanced/robustness/results/cascade_failure_results.json')

    return metrics


if __name__ == '__main__':
    main()
