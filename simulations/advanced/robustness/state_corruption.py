"""
POLLN Robustness Simulation: State Corruption Recovery
======================================================

This simulation tests POLLN's ability to detect and recover from various
types of state corruption across different system components.

Corruption Types:
1. Value network corruption: Incorrect value predictions
2. World model corruption: Distorted state representations
3. Communication history corruption: Poisoned message history
4. Synaptic weight corruption: Altered connection strengths
5. Reputation corruption: Manipulated trust scores

Recovery Strategies:
1. Checkpoint rollback: Revert to last known good state
2. Peer validation: Cross-validate state with peers
3. Consensus recovery: Use majority voting to recover
4. Redundancy recovery: Use redundant backups
5. anomaly detection: Detect and correct corrupted values

Metrics:
- Corruption detection rate
- Recovery success rate
- Recovery time
- Data loss percentage
- False positive rate
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import random
import hashlib
from collections import defaultdict
import copy


class CorruptionType(Enum):
    """Types of state corruption"""
    VALUE_NETWORK = "value_network"           # Incorrect value predictions
    WORLD_MODEL = "world_model"               # Distorted state representations
    COMMUNICATION_HISTORY = "communication_history"  # Poisoned message history
    SYNAPTIC_WEIGHTS = "synaptic_weights"     # Altered connection strengths
    REPUTATION = "reputation"                 # Manipulated trust scores
    EMBEDDINGS = "embeddings"                 # Corrupted embedding vectors


class RecoveryStrategy(Enum):
    """Strategies for recovering from corruption"""
    CHECKPOINT_ROLLBACK = "checkpoint_rollback"      # Revert to last good state
    PEER_VALIDATION = "peer_validation"              # Cross-validate with peers
    CONSENSUS_RECOVERY = "consensus_recovery"        # Majority voting
    REDUNDANCY_RECOVERY = "redundancy_recovery"      # Use redundant backups
    ANOMALY_DETECTION = "anomaly_detection"          # Detect and correct


class ComponentStatus(Enum):
    """Status of a system component"""
    HEALTHY = "healthy"
    CORRUPTED = "corrupted"
    RECOVERING = "recovering"
    RECOVERED = "recovered"


@dataclass
class CorruptionEvent:
    """A corruption event"""
    timestamp: float
    component_type: CorruptionType
    component_id: str
    corruption_severity: float  # 0-1 scale
    detected: bool = False
    recovered: bool = False
    recovery_time_ms: Optional[float] = None


@dataclass
class Checkpoint:
    """A system checkpoint"""
    id: str
    timestamp: float
    state_hash: str
    state_data: Dict[str, Any]


@dataclass
class RecoveryMetrics:
    """Metrics for corruption recovery simulation"""
    total_corruptions: int = 0
    detected_corruptions: int = 0
    recovered_corruptions: int = 0
    detection_rate: float = 0.0
    recovery_success_rate: float = 0.0
    avg_recovery_time_ms: float = 0.0
    data_loss_percentage: float = 0.0
    false_positive_rate: float = 0.0


class StateCorruptionSimulator:
    """
    Simulates state corruption and recovery in POLLN

    Features:
    - Multiple corruption types
    - Various recovery strategies
    - Checkpoint system
    - Peer validation
    - Consensus mechanisms
    - Anomaly detection
    """

    def __init__(
        self,
        num_agents: int = 50,
        checkpoint_frequency: int = 10,
        corruption_fraction: float = 0.2,
        recovery_strategies: List[RecoveryStrategy] = None,
        seed: int = 42
    ):
        """
        Initialize the state corruption simulator

        Args:
            num_agents: Number of agents in the system
            checkpoint_frequency: How often to create checkpoints
            corruption_fraction: Fraction of components to corrupt
            recovery_strategies: List of recovery strategies to employ
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)

        self.num_agents = num_agents
        self.checkpoint_frequency = checkpoint_frequency
        self.corruption_fraction = corruption_fraction
        self.recovery_strategies = recovery_strategies or [
            RecoveryStrategy.CHECKPOINT_ROLLBACK,
            RecoveryStrategy.PEER_VALIDATION,
        ]

        # Initialize system state
        self.value_network = self._initialize_value_network()
        self.world_model = self._initialize_world_model()
        self.communication_history = self._initialize_communication_history()
        self.synaptic_weights = self._initialize_synaptic_weights()
        self.reputations = self._initialize_reputations()
        self.embeddings = self._initialize_embeddings()

        # Checkpoints
        self.checkpoints: List[Checkpoint] = []
        self.current_checkpoint_id = 0

        # Corruption events
        self.corruption_events: List[CorruptionEvent] = []
        self.metrics = RecoveryMetrics()

        # Current time
        self.current_time = 0.0

        # Redundant backups
        self.redundant_backups = {}

    def _initialize_value_network(self) -> Dict[str, float]:
        """Initialize value network"""
        return {
            f"agent_{i}": np.random.uniform(0, 1)
            for i in range(self.num_agents)
        }

    def _initialize_world_model(self) -> Dict[str, np.ndarray]:
        """Initialize world model"""
        return {
            f"state_{i}": np.random.randn(128)
            for i in range(100)
        }

    def _initialize_communication_history(self) -> List[Dict]:
        """Initialize communication history"""
        return [
            {
                'id': f"msg_{i}",
                'sender': f"agent_{i % self.num_agents}",
                'receiver': f"agent_{(i + 1) % self.num_agents}",
                'content': f"Message {i}",
                'timestamp': i,
            }
            for i in range(1000)
        ]

    def _initialize_synaptic_weights(self) -> Dict[Tuple[str, str], float]:
        """Initialize synaptic weights"""
        weights = {}
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    weights[(f"agent_{i}", f"agent_{j}")] = np.random.uniform(0.1, 1.0)
        return weights

    def _initialize_reputations(self) -> Dict[str, float]:
        """Initialize reputations"""
        return {
            f"agent_{i}": np.random.uniform(0.5, 1.0)
            for i in range(self.num_agents)
        }

    def _initialize_embeddings(self) -> Dict[str, np.ndarray]:
        """Initialize embeddings"""
        return {
            f"embedding_{i}": np.random.randn(256)
            for i in range(200)
        }

    def _create_checkpoint(self) -> Checkpoint:
        """Create a checkpoint of current state"""
        state_data = {
            'value_network': copy.deepcopy(self.value_network),
            'world_model': {k: v.copy() for k, v in self.world_model.items()},
            'communication_history': copy.deepcopy(self.communication_history),
            'synaptic_weights': copy.deepcopy(self.synaptic_weights),
            'reputations': copy.deepcopy(self.reputations),
            'embeddings': {k: v.copy() for k, v in self.embeddings.items()},
        }

        # Create hash of state
        state_str = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.sha256(state_str.encode()).hexdigest()

        checkpoint = Checkpoint(
            id=f"checkpoint_{self.current_checkpoint_id}",
            timestamp=self.current_time,
            state_hash=state_hash,
            state_data=state_data,
        )

        self.checkpoints.append(checkpoint)
        self.current_checkpoint_id += 1

        # Maintain limited checkpoints
        if len(self.checkpoints) > 10:
            self.checkpoints.pop(0)

        return checkpoint

    def _corrupt_value_network(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt value network"""
        events = []
        num_corrupt = int(len(self.value_network) * corruption_fraction)

        for _ in range(num_corrupt):
            agent_id = random.choice(list(self.value_network.keys()))

            # Corrupt value (set to invalid range)
            original_value = self.value_network[agent_id]
            self.value_network[agent_id] = np.random.uniform(-1, 0)  # Invalid: should be 0-1

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.VALUE_NETWORK,
                component_id=agent_id,
                corruption_severity=abs(self.value_network[agent_id] - original_value),
            ))

        return events

    def _corrupt_world_model(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt world model"""
        events = []
        num_corrupt = int(len(self.world_model) * corruption_fraction)

        for _ in range(num_corrupt):
            state_id = random.choice(list(self.world_model.keys()))

            # Corrupt state vector (add large noise)
            original_state = self.world_model[state_id].copy()
            corruption = np.random.randn(128) * 10  # Large corruption
            self.world_model[state_id] = original_state + corruption

            severity = np.linalg.norm(corruption) / np.linalg.norm(original_state)

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.WORLD_MODEL,
                component_id=state_id,
                corruption_severity=min(severity, 1.0),
            ))

        return events

    def _corrupt_communication_history(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt communication history"""
        events = []
        num_corrupt = int(len(self.communication_history) * corruption_fraction)

        for _ in range(num_corrupt):
            msg_idx = random.randint(0, len(self.communication_history) - 1)

            # Corrupt message
            original_content = self.communication_history[msg_idx]['content']
            self.communication_history[msg_idx]['content'] = "CORRUPTED: " + original_content[::-1]

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.COMMUNICATION_HISTORY,
                component_id=self.communication_history[msg_idx]['id'],
                corruption_severity=1.0,
            ))

        return events

    def _corrupt_synaptic_weights(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt synaptic weights"""
        events = []
        num_corrupt = int(len(self.synaptic_weights) * corruption_fraction)

        for _ in range(num_corrupt):
            synapse_id = random.choice(list(self.synaptic_weights.keys()))

            # Corrupt weight (set to invalid range)
            original_weight = self.synaptic_weights[synapse_id]
            self.synaptic_weights[synapse_id] = np.random.uniform(-1, 0)  # Invalid: should be 0.1-1.0

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.SYNAPTIC_WEIGHTS,
                component_id=str(synapse_id),
                corruption_severity=abs(self.synaptic_weights[synapse_id] - original_weight),
            ))

        return events

    def _corrupt_reputations(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt reputations"""
        events = []
        num_corrupt = int(len(self.reputations) * corruption_fraction)

        for _ in range(num_corrupt):
            agent_id = random.choice(list(self.reputations.keys()))

            # Corrupt reputation (set to invalid range)
            original_reputation = self.reputations[agent_id]
            self.reputations[agent_id] = np.random.uniform(1.5, 2.0)  # Invalid: should be 0-1

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.REPUTATION,
                component_id=agent_id,
                corruption_severity=abs(self.reputations[agent_id] - original_reputation),
            ))

        return events

    def _corrupt_embeddings(self, corruption_fraction: float) -> List[CorruptionEvent]:
        """Corrupt embeddings"""
        events = []
        num_corrupt = int(len(self.embeddings) * corruption_fraction)

        for _ in range(num_corrupt):
            embedding_id = random.choice(list(self.embeddings.keys()))

            # Corrupt embedding vector
            original_embedding = self.embeddings[embedding_id].copy()
            corruption = np.random.randn(256) * 5
            self.embeddings[embedding_id] = original_embedding + corruption

            severity = np.linalg.norm(corruption) / np.linalg.norm(original_embedding)

            events.append(CorruptionEvent(
                timestamp=self.current_time,
                component_type=CorruptionType.EMBEDDINGS,
                component_id=embedding_id,
                corruption_severity=min(severity, 1.0),
            ))

        return events

    def _detect_corruption_value_network(self) -> List[str]:
        """Detect corruption in value network"""
        corrupted = []

        for agent_id, value in self.value_network.items():
            # Check if value is in valid range [0, 1]
            if value < 0 or value > 1:
                corrupted.append(agent_id)

        return corrupted

    def _detect_corruption_world_model(self) -> List[str]:
        """Detect corruption in world model"""
        corrupted = []

        for state_id, state_vector in self.world_model.items():
            # Check for statistical anomalies
            mean = np.mean(state_vector)
            std = np.std(state_vector)

            # Corrupted states have unusual statistics
            if abs(mean) > 5 or std > 10:
                corrupted.append(state_id)

        return corrupted

    def _detect_corruption_communication_history(self) -> List[str]:
        """Detect corruption in communication history"""
        corrupted = []

        for msg in self.communication_history:
            # Check for corruption markers
            if msg['content'].startswith('CORRUPTED:'):
                corrupted.append(msg['id'])

        return corrupted

    def _detect_corruption_synaptic_weights(self) -> List[str]:
        """Detect corruption in synaptic weights"""
        corrupted = []

        for synapse_id, weight in self.synaptic_weights.items():
            # Check if weight is in valid range [0.1, 1.0]
            if weight < 0.1 or weight > 1.0:
                corrupted.append(str(synapse_id))

        return corrupted

    def _detect_corruption_reputations(self) -> List[str]:
        """Detect corruption in reputations"""
        corrupted = []

        for agent_id, reputation in self.reputations.items():
            # Check if reputation is in valid range [0, 1]
            if reputation < 0 or reputation > 1:
                corrupted.append(agent_id)

        return corrupted

    def _detect_corruption_embeddings(self) -> List[str]:
        """Detect corruption in embeddings"""
        corrupted = []

        for embedding_id, embedding in self.embeddings.items():
            # Check for statistical anomalies
            mean = np.mean(embedding)
            std = np.std(embedding)

            # Corrupted embeddings have unusual statistics
            if abs(mean) > 3 or std > 8:
                corrupted.append(embedding_id)

        return corrupted

    def _recover_checkpoint_rollback(self, event: CorruptionEvent) -> bool:
        """Recover using checkpoint rollback"""
        if not self.checkpoints:
            return False

        # Get most recent checkpoint
        checkpoint = self.checkpoints[-1]

        # Restore from checkpoint based on component type
        if event.component_type == CorruptionType.VALUE_NETWORK:
            self.value_network = copy.deepcopy(checkpoint.state_data['value_network'])
        elif event.component_type == CorruptionType.WORLD_MODEL:
            self.world_model = {k: v.copy() for k, v in checkpoint.state_data['world_model'].items()}
        elif event.component_type == CorruptionType.COMMUNICATION_HISTORY:
            self.communication_history = copy.deepcopy(checkpoint.state_data['communication_history'])
        elif event.component_type == CorruptionType.SYNAPTIC_WEIGHTS:
            self.synaptic_weights = copy.deepcopy(checkpoint.state_data['synaptic_weights'])
        elif event.component_type == CorruptionType.REPUTATION:
            self.reputations = copy.deepcopy(checkpoint.state_data['reputations'])
        elif event.component_type == CorruptionType.EMBEDDINGS:
            self.embeddings = {k: v.copy() for k, v in checkpoint.state_data['embeddings'].items()}

        return True

    def _recover_peer_validation(self, event: CorruptionEvent) -> bool:
        """Recover using peer validation"""
        # In a real system, this would validate state with peer agents
        # Here we simulate by resetting to expected values

        if event.component_type == CorruptionType.VALUE_NETWORK:
            # Reset to valid range
            if event.component_id in self.value_network:
                self.value_network[event.component_id] = np.random.uniform(0, 1)
                return True

        elif event.component_type == CorruptionType.REPUTATION:
            # Reset to valid range
            if event.component_id in self.reputations:
                self.reputations[event.component_id] = np.random.uniform(0.5, 1.0)
                return True

        return False

    def _recover_consensus(self, event: CorruptionEvent) -> bool:
        """Recover using consensus"""
        # In a real system, this would use majority voting
        # Here we simulate by taking median of peer values

        if event.component_type == CorruptionType.VALUE_NETWORK:
            # Get median value
            values = list(self.value_network.values())
            median_value = np.median(values)

            if event.component_id in self.value_network:
                self.value_network[event.component_id] = median_value
                return True

        return False

    def _recover_anomaly_detection(self, event: CorruptionEvent) -> bool:
        """Recover using anomaly detection and correction"""
        # Detect anomaly and correct to expected range

        if event.component_type == CorruptionType.VALUE_NETWORK:
            if event.component_id in self.value_network:
                value = self.value_network[event.component_id]
                # Clip to valid range
                self.value_network[event.component_id] = np.clip(value, 0, 1)
                return True

        elif event.component_type == CorruptionType.REPUTATION:
            if event.component_id in self.reputations:
                reputation = self.reputations[event.component_id]
                # Clip to valid range
                self.reputations[event.component_id] = np.clip(reputation, 0, 1)
                return True

        return False

    def _detect_and_recover(self, event: CorruptionEvent) -> bool:
        """Detect and recover from a corruption event"""
        detected = False
        recovered = False
        recovery_start = time.time()

        # Detect corruption
        if event.component_type == CorruptionType.VALUE_NETWORK:
            corrupted_ids = self._detect_corruption_value_network()
            detected = event.component_id in corrupted_ids

        elif event.component_type == CorruptionType.WORLD_MODEL:
            corrupted_ids = self._detect_corruption_world_model()
            detected = event.component_id in corrupted_ids

        elif event.component_type == CorruptionType.COMMUNICATION_HISTORY:
            corrupted_ids = self._detect_corruption_communication_history()
            detected = event.component_id in corrupted_ids

        elif event.component_type == CorruptionType.SYNAPTIC_WEIGHTS:
            corrupted_ids = self._detect_corruption_synaptic_weights()
            detected = event.component_id in corrupted_ids

        elif event.component_type == CorruptionType.REPUTATION:
            corrupted_ids = self._detect_corruption_reputations()
            detected = event.component_id in corrupted_ids

        elif event.component_type == CorruptionType.EMBEDDINGS:
            corrupted_ids = self._detect_corruption_embeddings()
            detected = event.component_id in corrupted_ids

        event.detected = detected

        # Recover if detected
        if detected:
            for strategy in self.recovery_strategies:
                if strategy == RecoveryStrategy.CHECKPOINT_ROLLBACK:
                    recovered = self._recover_checkpoint_rollback(event)
                elif strategy == RecoveryStrategy.PEER_VALIDATION:
                    recovered = self._recover_peer_validation(event)
                elif strategy == RecoveryStrategy.CONSENSUS_RECOVERY:
                    recovered = self._recover_consensus(event)
                elif strategy == RecoveryStrategy.ANOMALY_DETECTION:
                    recovered = self._recover_anomaly_detection(event)

                if recovered:
                    break

        event.recovered = recovered
        event.recovery_time_ms = (time.time() - recovery_start) * 1000

        return recovered

    def run_simulation(self, num_steps: int = 100) -> RecoveryMetrics:
        """
        Run complete corruption and recovery simulation

        Args:
            num_steps: Number of simulation steps

        Returns:
            RecoveryMetrics with aggregated results
        """
        print("Starting State Corruption Recovery Simulation...")
        print(f"Agents: {self.num_agents}")
        print(f"Corruption fraction: {self.corruption_fraction:.1%}")
        print(f"Recovery strategies: {[s.value for s in self.recovery_strategies]}")
        print()

        for step in range(num_steps):
            self.current_time = step

            # Create checkpoint periodically
            if step % self.checkpoint_frequency == 0:
                self._create_checkpoint()

            # Inject corruption
            all_events = []

            # Corrupt different components
            all_events.extend(self._corrupt_value_network(self.corruption_fraction / 6))
            all_events.extend(self._corrupt_world_model(self.corruption_fraction / 6))
            all_events.extend(self._corrupt_communication_history(self.corruption_fraction / 6))
            all_events.extend(self._corrupt_synaptic_weights(self.corruption_fraction / 6))
            all_events.extend(self._corrupt_reputations(self.corruption_fraction / 6))
            all_events.extend(self._corrupt_embeddings(self.corruption_fraction / 6))

            # Detect and recover
            for event in all_events:
                self._detect_and_recover(event)
                self.corruption_events.append(event)

            if step % 10 == 0:
                print(f"Step {step}: {len(all_events)} corruptions injected")

        # Calculate metrics
        self._calculate_metrics()

        return self.metrics

    def _calculate_metrics(self) -> None:
        """Calculate aggregated metrics"""
        self.metrics.total_corruptions = len(self.corruption_events)
        self.metrics.detected_corruptions = sum(1 for e in self.corruption_events if e.detected)
        self.metrics.recovered_corruptions = sum(1 for e in self.corruption_events if e.recovered)

        if self.metrics.total_corruptions > 0:
            self.metrics.detection_rate = self.metrics.detected_corruptions / self.metrics.total_corruptions
            self.metrics.recovery_success_rate = self.metrics.recovered_corruptions / self.metrics.total_corruptions

        recovery_times = [e.recovery_time_ms for e in self.corruption_events if e.recovery_time_ms is not None]
        self.metrics.avg_recovery_time_ms = np.mean(recovery_times) if recovery_times else 0.0

        # Calculate data loss (events that weren't recovered)
        data_loss = sum(1 for e in self.corruption_events if e.detected and not e.recovered)
        self.metrics.data_loss_percentage = data_loss / self.metrics.total_corruptions if self.metrics.total_corruptions > 0 else 0.0

    def print_metrics(self) -> None:
        """Print formatted metrics"""
        print("\n" + "="*60)
        print("STATE CORRUPTION RECOVERY SIMULATION RESULTS")
        print("="*60)
        print(f"\nTotal Corruptions:     {self.metrics.total_corruptions}")
        print(f"Detected:              {self.metrics.detected_corruptions} ({self.metrics.detection_rate*100:.1f}%)")
        print(f"Recovered:             {self.metrics.recovered_corruptions} ({self.metrics.recovery_success_rate*100:.1f}%)")
        print(f"\nData Loss:             {self.metrics.data_loss_percentage*100:.1f}%")
        print(f"Avg Recovery Time:     {self.metrics.avg_recovery_time_ms:.2f} ms")
        print("="*60 + "\n")

    def generate_resilience_config(self) -> Dict:
        """
        Generate state protection configuration

        Returns:
            Dictionary with configuration recommendations
        """
        recommendations = {
            'state_protection': {
                'checksum_validation': True,
                'peer_validation': RecoveryStrategy.PEER_VALIDATION in self.recovery_strategies,
                'checkpoint_frequency': self.checkpoint_frequency,
                'rollback_on_corruption': RecoveryStrategy.CHECKPOINT_ROLLBACK in self.recovery_strategies,
            },
            'checkpoint': {
                'enabled': True,
                'frequency': self.checkpoint_frequency,
                'max_checkpoints': 10,
                'compression': True,
            },
            'validation': {
                'checksum_enabled': True,
                'peer_validation_enabled': RecoveryStrategy.PEER_VALIDATION in self.recovery_strategies,
                'anomaly_detection_enabled': RecoveryStrategy.ANOMALY_DETECTION in self.recovery_strategies,
            },
            'recommendations': []
        }

        # Add specific recommendations
        if self.metrics.detection_rate < 0.9:
            recommendations['recommendations'].append(
                "Detection rate below 90%. Implement stronger validation mechanisms."
            )

        if self.metrics.recovery_success_rate < 0.8:
            recommendations['recommendations'].append(
                "Recovery success rate below 80%. Add redundant recovery strategies."
            )

        if self.metrics.data_loss_percentage > 0.1:
            recommendations['recommendations'].append(
                "Data loss above 10%. Increase checkpoint frequency."
            )

        if self.metrics.avg_recovery_time_ms > 100:
            recommendations['recommendations'].append(
                f"Recovery time high ({self.metrics.avg_recovery_time_ms:.1f}ms). Optimize recovery algorithms."
            )

        return recommendations

    def save_results(self, filepath: str) -> None:
        """Save simulation results to JSON file"""
        # Get corruption type breakdown
        corruption_breakdown = defaultdict(lambda: {
            'total': 0,
            'detected': 0,
            'recovered': 0,
        })

        for event in self.corruption_events:
            corruption_breakdown[event.component_type.value]['total'] += 1
            if event.detected:
                corruption_breakdown[event.component_type.value]['detected'] += 1
            if event.recovered:
                corruption_breakdown[event.component_type.value]['recovered'] += 1

        results_data = {
            'configuration': {
                'num_agents': self.num_agents,
                'checkpoint_frequency': self.checkpoint_frequency,
                'corruption_fraction': self.corruption_fraction,
                'recovery_strategies': [s.value for s in self.recovery_strategies],
            },
            'metrics': {
                'total_corruptions': self.metrics.total_corruptions,
                'detected_corruptions': self.metrics.detected_corruptions,
                'recovered_corruptions': self.metrics.recovered_corruptions,
                'detection_rate': self.metrics.detection_rate,
                'recovery_success_rate': self.metrics.recovery_success_rate,
                'avg_recovery_time_ms': self.metrics.avg_recovery_time_ms,
                'data_loss_percentage': self.metrics.data_loss_percentage,
            },
            'corruption_breakdown': dict(corruption_breakdown),
            'resilience_config': self.generate_resilience_config(),
        }

        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to {filepath}")


def main():
    """Main entry point for the simulation"""
    import time

    print("POLLN State Corruption Recovery Simulation")
    print("="*60)

    # Create simulator
    simulator = StateCorruptionSimulator(
        num_agents=50,
        checkpoint_frequency=10,
        corruption_fraction=0.2,
        recovery_strategies=[
            RecoveryStrategy.CHECKPOINT_ROLLBACK,
            RecoveryStrategy.PEER_VALIDATION,
            RecoveryStrategy.ANOMALY_DETECTION,
        ],
    )

    # Run simulation
    metrics = simulator.run_simulation(num_steps=100)

    # Print results
    simulator.print_metrics()

    # Generate config
    config = simulator.generate_resilience_config()
    print("\nState Protection Configuration:")
    print(json.dumps(config, indent=2))

    # Save results
    simulator.save_results('simulations/advanced/robustness/results/state_corruption_results.json')

    return metrics


if __name__ == '__main__':
    main()
