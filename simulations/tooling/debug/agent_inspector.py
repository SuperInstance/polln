#!/usr/bin/env python3
"""
Agent Inspector - Inspect and debug agent state in POLLN colonies.

This tool provides comprehensive inspection of agent state, value networks,
synapses, META tile state, and helps debug agent hangs, incorrect behavior,
and state corruption.
"""

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
from collections import defaultdict
import time


@dataclass
class AgentStateSnapshot:
    """Snapshot of an agent's state at a point in time."""
    agent_id: str
    agent_type: str
    timestamp: float
    status: str  # 'dormant', 'active', 'hibernating', 'error'
    last_active: float

    # Value function
    value_function: float
    success_count: int
    failure_count: int
    success_rate: float
    avg_latency_ms: float

    # State data
    state_snapshot: Dict[str, Any]

    # Synapses
    incoming_synapse_count: int
    outgoing_synapse_count: int
    strongest_synapse: Optional[Dict[str, Any]]

    # META tile data (if applicable)
    is_meta: bool
    meta_potential: Optional[float]
    differentiation_signals: Optional[List[str]]

    # Health indicators
    is_hung: bool
    is_corrupted: bool
    error_message: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SynapseInspection:
    """Inspection of a synapse between agents."""
    source_id: str
    target_id: str
    weight: float
    coactivation_count: int
    last_coactivated: float
    age_seconds: float
    health_score: float  # 0-1 based on weight and activity

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ValueNetworkState:
    """State of an agent's value network."""
    agent_id: str
    current_value: float
    value_history: List[float]
    eligibility_traces: Dict[str, float]
    learning_rate: float
    discount_factor: float
    convergence_score: float  # How stable the value is
    trend: str  # 'improving', 'declining', 'stable', 'oscillating'

    def to_dict(self) -> Dict:
        return asdict(self)


class AgentInspector:
    """
    Comprehensive agent state inspection and debugging.

    Features:
    - Live agent state inspection
    - Historical state replay
    - Value network analysis
    - Synapse health checks
    - META tile differentiation tracking
    - Agent hang detection
    - State corruption detection
    """

    def __init__(self, colony_id: str, output_dir: str = "reports/diagnostics"):
        self.colony_id = colony_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.agent_snapshots: Dict[str, List[AgentStateSnapshot]] = defaultdict(list)
        self.current_snapshots: Dict[str, AgentStateSnapshot] = {}
        self.synapse_inspections: Dict[Tuple[str, str], SynapseInspection] = {}
        self.value_network_states: Dict[str, ValueNetworkState] = {}

        # Health tracking
        self.hung_agents: Set[str] = set()
        self.corrupted_agents: Set[str] = set()
        self.error_agents: Dict[str, str] = {}

    def inspect_agent(self, agent_data: Dict[str, Any],
                     timestamp: Optional[float] = None) -> AgentStateSnapshot:
        """
        Inspect an agent's current state.

        Args:
            agent_data: Dictionary containing agent state
            timestamp: Optional timestamp (defaults to now)

        Returns:
            AgentStateSnapshot: Snapshot of the agent's state
        """
        if timestamp is None:
            timestamp = time.time()

        agent_id = agent_data.get('id', 'unknown')
        status = agent_data.get('status', 'unknown')

        # Calculate success rate
        success_count = agent_data.get('successCount', 0)
        failure_count = agent_data.get('failureCount', 0)
        total = success_count + failure_count
        success_rate = success_count / total if total > 0 else 0.0

        # Check if agent is hung (no recent activity)
        last_active = agent_data.get('lastActive', 0)
        is_hung = (time.time() - last_active) > 300  # 5 minutes

        # Check for state corruption
        is_corrupted = self._detect_corruption(agent_data)

        snapshot = AgentStateSnapshot(
            agent_id=agent_id,
            agent_type=agent_data.get('typeId', 'unknown'),
            timestamp=timestamp,
            status=status,
            last_active=last_active,
            value_function=agent_data.get('valueFunction', 0.5),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            avg_latency_ms=agent_data.get('avgLatencyMs', 0),
            state_snapshot=agent_data.get('stateSnapshot', {}),
            incoming_synapse_count=len(agent_data.get('incomingSynapses', [])),
            outgoing_synapse_count=len(agent_data.get('outgoingSynapses', [])),
            strongest_synapse=self._find_strongest_synapse(agent_data),
            is_meta=agent_data.get('isMeta', False),
            meta_potential=agent_data.get('metaPotential'),
            differentiation_signals=agent_data.get('differentiationSignals', []),
            is_hung=is_hung,
            is_corrupted=is_corrupted,
            error_message=agent_data.get('errorMessage')
        )

        # Store snapshot
        self.agent_snapshots[agent_id].append(snapshot)
        self.current_snapshots[agent_id] = snapshot

        # Track health issues
        if is_hung:
            self.hung_agents.add(agent_id)
        if is_corrupted:
            self.corrupted_agents.add(agent_id)
        if status == 'error' and snapshot.error_message:
            self.error_agents[agent_id] = snapshot.error_message

        return snapshot

    def inspect_synapse(self, source_id: str, target_id: str,
                       synapse_data: Dict[str, Any]) -> SynapseInspection:
        """
        Inspect a synapse between two agents.

        Args:
            source_id: Source agent ID
            target_id: Target agent ID
            synapse_data: Dictionary containing synapse state

        Returns:
            SynapseInspection: Inspection results
        """
        weight = synapse_data.get('weight', 0.0)
        last_coactivated = synapse_data.get('lastCoactivated', 0)
        age = time.time() - last_coactivated

        # Calculate health score based on weight and recency
        recency_factor = max(0, 1 - age / 86400)  # Decay over 24 hours
        health_score = weight * 0.7 + recency_factor * 0.3

        inspection = SynapseInspection(
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            coactivation_count=synapse_data.get('coactivationCount', 0),
            last_coactivated=last_coactivated,
            age_seconds=age,
            health_score=health_score
        )

        self.synapse_inspections[(source_id, target_id)] = inspection
        return inspection

    def inspect_value_network(self, agent_id: str,
                             value_data: Dict[str, Any]) -> ValueNetworkState:
        """
        Inspect an agent's value network state.

        Args:
            agent_id: Agent ID
            value_data: Dictionary containing value network data

        Returns:
            ValueNetworkState: Value network state
        """
        current_value = value_data.get('currentValue', 0.5)
        value_history = value_data.get('valueHistory', [current_value])
        eligibility_traces = value_data.get('eligibilityTraces', {})

        # Calculate convergence score (variance of recent values)
        recent_values = value_history[-10:] if len(value_history) >= 10 else value_history
        if len(recent_values) > 1:
            mean = sum(recent_values) / len(recent_values)
            variance = sum((v - mean) ** 2 for v in recent_values) / len(recent_values)
            convergence_score = 1.0 - min(1.0, variance)
        else:
            convergence_score = 0.0

        # Determine trend
        trend = self._calculate_trend(value_history)

        state = ValueNetworkState(
            agent_id=agent_id,
            current_value=current_value,
            value_history=value_history,
            eligibility_traces=eligibility_traces,
            learning_rate=value_data.get('learningRate', 0.1),
            discount_factor=value_data.get('discountFactor', 0.99),
            convergence_score=convergence_score,
            trend=trend
        )

        self.value_network_states[agent_id] = state
        return state

    def get_agent_history(self, agent_id: str,
                         start_time: Optional[float] = None,
                         end_time: Optional[float] = None) -> List[AgentStateSnapshot]:
        """
        Get historical state snapshots for an agent.

        Args:
            agent_id: Agent ID
            start_time: Optional start timestamp
            end_time: Optional end timestamp

        Returns:
            List of snapshots within the time range
        """
        snapshots = self.agent_snapshots.get(agent_id, [])

        if start_time is not None:
            snapshots = [s for s in snapshots if s.timestamp >= start_time]

        if end_time is not None:
            snapshots = [s for s in snapshots if s.timestamp <= end_time]

        return snapshots

    def detect_hung_agents(self, timeout_seconds: float = 300.0) -> List[str]:
        """
        Detect agents that haven't been active recently.

        Args:
            timeout_seconds: Time threshold for considering an agent hung

        Returns:
            List of hung agent IDs
        """
        current_time = time.time()
        hung = []

        for agent_id, snapshot in self.current_snapshots.items():
            if current_time - snapshot.last_active > timeout_seconds:
                if snapshot.status in ['active', 'hibernating']:
                    hung.append(agent_id)

        return hung

    def detect_value_convergence_issues(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect agents with value network convergence issues.

        Returns:
            Dictionary mapping agent IDs to issue details
        """
        issues = {}

        for agent_id, state in self.value_network_states.items():
            issue = {}

            # Check for oscillation
            if state.trend == 'oscillating' and state.convergence_score < 0.3:
                issue['type'] = 'oscillation'
                issue['severity'] = 'warning'
                issue['message'] = f'Agent {agent_id} value network is oscillating'
                issue['convergence_score'] = state.convergence_score

            # Check for divergence
            elif state.trend == 'declining' and state.current_value < 0.2:
                issue['type'] = 'divergence'
                issue['severity'] = 'critical'
                issue['message'] = f'Agent {agent_id} value network is diverging'
                issue['current_value'] = state.current_value

            # Check for slow convergence
            elif state.convergence_score < 0.5 and len(state.value_history) > 100:
                issue['type'] = 'slow_convergence'
                issue['severity'] = 'info'
                issue['message'] = f'Agent {agent_id} converging slowly'
                issue['convergence_score'] = state.convergence_score

            if issue:
                issues[agent_id] = issue

        return issues

    def analyze_synapse_health(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the health of synapses.

        Args:
            agent_id: Optional agent ID to filter by

        Returns:
            Dictionary with synapse health statistics
        """
        synapses = []
        for (source, target), inspection in self.synapse_inspections.items():
            if agent_id is None or source == agent_id or target == agent_id:
                synapses.append(inspection)

        if not synapses:
            return {'error': 'No synapses found'}

        health_scores = [s.health_score for s in synapses]
        weak_synapses = [s for s in synapses if s.health_score < 0.3]
        stale_synapses = [s for s in synapses if s.age_seconds > 86400]

        return {
            'total_synapses': len(synapses),
            'avg_health_score': sum(health_scores) / len(health_scores),
            'min_health_score': min(health_scores),
            'max_health_score': max(health_scores),
            'weak_synapse_count': len(weak_synapses),
            'stale_synapse_count': len(stale_synapses),
            'weak_synapses': [
                {'source': s.source_id, 'target': s.target_id, 'score': s.health_score}
                for s in weak_synapses
            ]
        }

    def _detect_corruption(self, agent_data: Dict[str, Any]) -> bool:
        """Detect potential state corruption."""
        # Check for NaN/Infinity in value function
        value = agent_data.get('valueFunction', 0.5)
        if not isinstance(value, (int, float)) or value != value:  # NaN check
            return True

        # Check for negative counts
        if agent_data.get('successCount', 0) < 0 or agent_data.get('failureCount', 0) < 0:
            return True

        # Check for out-of-range values
        if value < 0 or value > 1:
            return True

        return False

    def _find_strongest_synapse(self, agent_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the strongest synapse for an agent."""
        synapses = agent_data.get('outgoingSynapses', [])

        if not synapses:
            return None

        strongest = max(synapses, key=lambda s: s.get('weight', 0))
        return {
            'target_id': strongest.get('targetAgentId'),
            'weight': strongest.get('weight', 0),
            'coactivation_count': strongest.get('coactivationCount', 0)
        }

    def _calculate_trend(self, value_history: List[float]) -> str:
        """Calculate the trend of value function over time."""
        if len(value_history) < 3:
            return 'stable'

        recent = value_history[-10:] if len(value_history) >= 10 else value_history

        # Calculate trend line
        n = len(recent)
        x = list(range(n))
        y = recent

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        # Check for oscillation
        if len(recent) >= 5:
            changes = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
            avg_change = sum(changes) / len(changes)
            if avg_change > 0.1:  # High volatility
                return 'oscillating'

        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'

    def generate_inspection_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive inspection report.

        Returns:
            Dictionary containing all inspection data and analysis
        """
        hung_agents = self.detect_hung_agents()
        convergence_issues = self.detect_value_convergence_issues()
        synapse_health = self.analyze_synapse_health()

        report = {
            'colony_id': self.colony_id,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_agents': len(self.current_snapshots),
                'hung_agents': len(hung_agents),
                'corrupted_agents': len(self.corrupted_agents),
                'error_agents': len(self.error_agents),
                'convergence_issues': len(convergence_issues),
                'total_synapses': len(self.synapse_inspections)
            },
            'agent_snapshots': {
                agent_id: [s.to_dict() for s in snapshots]
                for agent_id, snapshots in self.agent_snapshots.items()
            },
            'current_snapshots': {
                agent_id: s.to_dict()
                for agent_id, s in self.current_snapshots.items()
            },
            'value_network_states': {
                agent_id: s.to_dict()
                for agent_id, s in self.value_network_states.items()
            },
            'synapse_inspections': {
                f"{source}_{target}": s.to_dict()
                for (source, target), s in self.synapse_inspections.items()
            },
            'health_issues': {
                'hung_agents': hung_agents,
                'corrupted_agents': list(self.corrupted_agents),
                'error_agents': self.error_agents,
                'convergence_issues': convergence_issues,
                'synapse_health': synapse_health
            }
        }

        return report

    def save_inspection_report(self, filename: str = "agent_states.json") -> str:
        """
        Save inspection report to file.

        Args:
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        report = self.generate_inspection_report()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Inspection report saved to: {output_path}")
        return str(output_path)

    def print_agent_summary(self, agent_id: str) -> None:
        """Print a summary of an agent's current state."""
        if agent_id not in self.current_snapshots:
            print(f"Agent {agent_id} not found")
            return

        snapshot = self.current_snapshots[agent_id]

        print(f"\n{'=' * 80}")
        print(f"Agent Summary: {agent_id}")
        print(f"{'=' * 80}")
        print(f"Type: {snapshot.agent_type}")
        print(f"Status: {snapshot.status}")
        print(f"Value Function: {snapshot.value_function:.3f}")
        print(f"Success Rate: {snapshot.success_rate:.1%}")
        print(f"Avg Latency: {snapshot.avg_latency_ms:.1f}ms")
        print(f"Success/Failure: {snapshot.success_count}/{snapshot.failure_count}")
        print(f"Incoming Synapses: {snapshot.incoming_synapse_count}")
        print(f"Outgoing Synapses: {snapshot.outgoing_synapse_count}")

        if snapshot.is_hung:
            print("⚠️  WARNING: Agent appears to be HUNG")
        if snapshot.is_corrupted:
            print("⚠️  WARNING: Agent state appears to be CORRUPTED")
        if snapshot.error_message:
            print(f"⚠️  ERROR: {snapshot.error_message}")

        if snapshot.is_meta:
            print(f"META Tile - Potential: {snapshot.meta_potential:.3f}")
            print(f"Differentiation Signals: {len(snapshot.differentiation_signals or [])}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python agent_inspector.py <colony_id> [command]")
        print("\nCommands:")
        print("  inspect <agent_file>      - Inspect agents from JSON file")
        print("  report                    - Generate inspection report")
        print("  summary <agent_id>        - Print agent summary")
        print("  hung [timeout]            - Detect hung agents")
        sys.exit(1)

    colony_id = sys.argv[1]
    inspector = AgentInspector(colony_id)

    if len(sys.argv) < 3:
        print("No command specified")
        sys.exit(1)

    command = sys.argv[2]

    if command == "inspect" and len(sys.argv) >= 4:
        # Load and inspect agents from file
        agent_file = sys.argv[3]
        with open(agent_file, 'r') as f:
            agents = json.load(f)

        for agent_data in agents:
            inspector.inspect_agent(agent_data)

            # Inspect value network if data available
            if 'valueNetwork' in agent_data:
                inspector.inspect_value_network(
                    agent_data['id'],
                    agent_data['valueNetwork']
                )

            # Inspect synapses if data available
            if 'synapses' in agent_data:
                for syn_data in agent_data['synapses']:
                    inspector.inspect_synapse(
                        agent_data['id'],
                        syn_data['targetAgentId'],
                        syn_data
                    )

        print(f"Inspected {len(agents)} agents")

    elif command == "report":
        inspector.save_inspection_report()

    elif command == "summary" and len(sys.argv) >= 4:
        inspector.print_agent_summary(sys.argv[3])

    elif command == "hung":
        timeout = float(sys.argv[3]) if len(sys.argv) >= 4 else 300.0
        hung = inspector.detect_hung_agents(timeout)
        print(f"Hung agents ({len(hung)}):")
        for agent_id in hung:
            print(f"  - {agent_id}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
