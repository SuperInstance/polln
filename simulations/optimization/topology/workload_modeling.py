"""
Workload Modeling for POLLN Agent Colonies

Models various workload patterns and communication scenarios
for testing topology performance under realistic conditions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import networkx as nx


class TrafficPattern(Enum):
    """Traffic distribution patterns."""
    UNIFORM = "uniform"  # Uniform random traffic
    HOTSPOT = "hotspot"  # Few nodes receive most traffic
    HIERARCHICAL = "hierarchical"  # Tiered traffic patterns
    RANDOM = "random"  # Random walk traffic
    LOCALITY = "locality"  # Spatial/temporal locality


class CommunicationPattern(Enum):
    """Communication patterns."""
    POINT_TO_POINT = "point_to_point"  # Unicast
    BROADCAST = "broadcast"  # One to all
    MULTICAST = "multicast"  # One to many
    GOSSIP = "gossip"  # Epidemic spreading
    AGGREGATION = "aggregation"  # Many to one (tree)


class TemporalPattern(Enum):
    """Temporal patterns."""
    STEADY = "steady"  # Constant traffic
    BURSTY = "bursty"  # Bursts of activity
    PERIODIC = "periodic"  # Periodic spikes
    RANDOM = "random"  # Random variation


@dataclass
class WorkloadConfig:
    """Configuration for workload generation."""
    num_requests: int = 1000
    traffic_pattern: TrafficPattern = TrafficPattern.UNIFORM
    communication_pattern: CommunicationPattern = CommunicationPattern.POINT_TO_POINT
    temporal_pattern: TemporalPattern = TemporalPattern.STEADY
    message_size: Tuple[float, float] = (1.0, 10.0)  # Min, max in KB
    hotspot_ratio: float = 0.2  # Fraction of nodes that are hotspots
    locality_radius: int = 3  # Hop radius for locality
    burst_prob: float = 0.1  # Probability of burst
    burst_size: int = 10  # Messages in burst
    period: int = 100  # Period for periodic pattern


@dataclass
class MessageRequest:
    """Single message request in workload."""
    source: int
    destination: int
    size: float
    timestamp: int
    pattern: CommunicationPattern


class WorkloadGenerator:
    """Generate synthetic workloads for topology testing."""

    def __init__(self, G: nx.Graph, seed: Optional[int] = None):
        """Initialize workload generator for a topology."""
        self.G = G
        self.n = G.number_of_nodes()
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)

    def generate(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate workload based on configuration."""
        requests = []

        # Generate base sequence
        base_requests = self._generate_traffic(config)

        # Apply temporal pattern
        requests = self._apply_temporal_pattern(base_requests, config)

        return requests

    def _generate_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate traffic based on communication pattern."""
        generators = {
            CommunicationPattern.POINT_TO_POINT: self._point_to_point_traffic,
            CommunicationPattern.BROADCAST: self._broadcast_traffic,
            CommunicationPattern.MULTICAST: self._multicast_traffic,
            CommunicationPattern.GOSSIP: self._gossip_traffic,
            CommunicationPattern.AGGREGATION: self._aggregation_traffic,
        }

        return generators[config.communication_pattern](config)

    def _point_to_point_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate point-to-point traffic."""
        requests = []

        for i in range(config.num_requests):
            source, destination = self._select_source_dest(config)
            size = np.random.uniform(*config.message_size)

            requests.append(MessageRequest(
                source=source,
                destination=destination,
                size=size,
                timestamp=i,
                pattern=config.communication_pattern
            ))

        return requests

    def _broadcast_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate broadcast traffic (one to all)."""
        requests = []
        num_broadcasts = config.num_requests // self.n

        for i in range(num_broadcasts):
            source = np.random.randint(0, self.n)
            size = np.random.uniform(*config.message_size)

            # Broadcast to all other nodes
            for dest in range(self.n):
                if dest != source:
                    requests.append(MessageRequest(
                        source=source,
                        destination=dest,
                        size=size,
                        timestamp=i * self.n + dest,
                        pattern=config.communication_pattern
                    ))

        return requests[:config.num_requests]

    def _multicast_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate multicast traffic (one to many)."""
        requests = []
        num_groups = config.num_requests // 10  # 10 destinations per multicast

        for i in range(num_groups):
            source = np.random.randint(0, self.n)
            size = np.random.uniform(*config.message_size)

            # Select random subset of destinations
            num_destinations = np.random.randint(2, self.n // 2)
            destinations = np.random.choice(
                [d for d in range(self.n) if d != source],
                num_destinations,
                replace=False
            )

            for dest in destinations:
                requests.append(MessageRequest(
                    source=source,
                    destination=dest,
                    size=size,
                    timestamp=i * num_destinations + list(destinations).index(dest),
                    pattern=config.communication_pattern
                ))

        return requests[:config.num_requests]

    def _gossip_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate gossip traffic (epidemic spreading)."""
        requests = []

        # Initialize with random infected nodes
        infected = set(np.random.choice(range(self.n), size=max(1, self.n // 10), replace=False))
        messages = {}

        for i in range(config.num_requests):
            if not infected:
                infected.add(np.random.randint(0, self.n))

            # Each infected node gossips to neighbors
            new_infected = set()
            for source in infected:
                neighbors = list(self.G.neighbors(source))
                if neighbors:
                    # Gossip to random subset
                    num_targets = min(3, len(neighbors))
                    targets = np.random.choice(neighbors, num_targets, replace=False)

                    for dest in targets:
                        if dest not in infected:
                            new_infected.add(dest)

                        size = np.random.uniform(*config.message_size)
                        requests.append(MessageRequest(
                            source=source,
                            destination=dest,
                            size=size,
                            timestamp=len(requests),
                            pattern=config.communication_pattern
                        ))

            infected.update(new_infected)

            if len(requests) >= config.num_requests:
                break

        return requests[:config.num_requests]

    def _aggregation_traffic(self, config: WorkloadConfig) -> List[MessageRequest]:
        """Generate aggregation traffic (many to one)."""
        requests = []
        num_aggregations = 10

        for i in range(num_aggregations):
            # Choose aggregator (destination)
            destination = np.random.randint(0, self.n)
            size = np.random.uniform(*config.message_size)

            # All nodes send to aggregator
            for source in range(self.n):
                if source != destination:
                    requests.append(MessageRequest(
                        source=source,
                        destination=destination,
                        size=size,
                        timestamp=i * self.n + source,
                        pattern=config.communication_pattern
                    ))

        return requests[:config.num_requests]

    def _select_source_dest(self, config: WorkloadConfig) -> Tuple[int, int]:
        """Select source and destination based on traffic pattern."""
        if config.traffic_pattern == TrafficPattern.UNIFORM:
            return self._uniform_pair()
        elif config.traffic_pattern == TrafficPattern.HOTSPOT:
            return self._hotspot_pair(config.hotspot_ratio)
        elif config.traffic_pattern == TrafficPattern.HIERARCHICAL:
            return self._hierarchical_pair()
        elif config.traffic_pattern == TrafficPattern.LOCALITY:
            return self._locality_pair(config.locality_radius)
        else:  # RANDOM
            return self._random_pair()

    def _uniform_pair(self) -> Tuple[int, int]:
        """Uniform random source-destination pair."""
        source = np.random.randint(0, self.n)
        destination = np.random.randint(0, self.n)
        while destination == source:
            destination = np.random.randint(0, self.n)
        return source, destination

    def _hotspot_pair(self, hotspot_ratio: float) -> Tuple[int, int]:
        """Source-destination pair with hotspots."""
        num_hotspots = max(1, int(self.n * hotspot_ratio))
        hotspots = set(np.random.choice(range(self.n), size=num_hotspots, replace=False))

        # 80% of traffic to/from hotspots
        if np.random.random() < 0.8:
            destination = np.random.choice(list(hotspots))
        else:
            destination = np.random.randint(0, self.n)

        source = np.random.randint(0, self.n)
        while source == destination:
            source = np.random.randint(0, self.n)

        return source, destination

    def _hierarchical_pair(self) -> Tuple[int, int]:
        """Hierarchical traffic pattern."""
        # Simulate hierarchy by degree
        degrees = dict(self.G.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

        # Top 20% are "core", middle 40% are "aggregation", rest are "edge"
        core_size = max(1, int(self.n * 0.2))
        agg_size = max(1, int(self.n * 0.4))

        core = set([n for n, _ in sorted_nodes[:core_size]])
        agg = set([n for n, _ in sorted_nodes[core_size:core_size + agg_size]])
        edge = set([n for n, _ in sorted_nodes[core_size + agg_size:]])

        # Hierarchical traffic patterns
        r = np.random.random()
        if r < 0.3:
            # Edge to aggregation
            source = np.random.choice(list(edge)) if edge else np.random.randint(0, self.n)
            destination = np.random.choice(list(agg)) if agg else np.random.randint(0, self.n)
        elif r < 0.5:
            # Aggregation to core
            source = np.random.choice(list(agg)) if agg else np.random.randint(0, self.n)
            destination = np.random.choice(list(core)) if core else np.random.randint(0, self.n)
        elif r < 0.7:
            # Core to core
            source = np.random.choice(list(core)) if len(core) > 1 else np.random.randint(0, self.n)
            destination = np.random.choice(list(core)) if core else np.random.randint(0, self.n)
            while destination == source and len(core) > 1:
                destination = np.random.choice(list(core))
        else:
            # Random
            source, destination = self._uniform_pair()

        return source, destination

    def _locality_pair(self, radius: int) -> Tuple[int, int]:
        """Pair with spatial locality (within radius hops)."""
        source = np.random.randint(0, self.n)

        # Find nodes within radius
        try:
            lengths = nx.single_source_shortest_path_length(self.G, source, cutoff=radius)
            candidates = [n for n in lengths.keys() if n != source]

            if candidates:
                destination = np.random.choice(candidates)
            else:
                destination = np.random.randint(0, self.n)
                while destination == source:
                    destination = np.random.randint(0, self.n)
        except:
            source, destination = self._uniform_pair()

        return source, destination

    def _random_pair(self) -> Tuple[int, int]:
        """Random walk based pair."""
        # Start random walk
        source = np.random.randint(0, self.n)

        # Walk random number of steps
        steps = np.random.randint(1, 6)
        current = source

        for _ in range(steps):
            neighbors = list(self.G.neighbors(current))
            if neighbors:
                current = np.random.choice(neighbors)
            else:
                break

        destination = current

        return source, destination

    def _apply_temporal_pattern(self, base_requests: List[MessageRequest],
                               config: WorkloadConfig) -> List[MessageRequest]:
        """Apply temporal pattern to request sequence."""
        if config.temporal_pattern == TemporalPattern.STEADY:
            return base_requests

        elif config.temporal_pattern == TemporalPattern.BURSTY:
            return self._apply_burst_pattern(base_requests, config)

        elif config.temporal_pattern == TemporalPattern.PERIODIC:
            return self._apply_periodic_pattern(base_requests, config)

        else:  # RANDOM
            return self._apply_random_pattern(base_requests, config)

    def _apply_burst_pattern(self, requests: List[MessageRequest],
                            config: WorkloadConfig) -> List[MessageRequest]:
        """Apply burst pattern to requests."""
        result = []
        i = 0

        while i < len(requests):
            # Check if burst
            if np.random.random() < config.burst_prob:
                # Burst: many messages at once
                burst_size = min(config.burst_size, len(requests) - i)
                burst_time = requests[i].timestamp

                for j in range(burst_size):
                    req = requests[i + j]
                    req.timestamp = burst_time
                    result.append(req)

                i += burst_size
            else:
                # Normal spacing
                result.append(requests[i])
                i += 1

        return result

    def _apply_periodic_pattern(self, requests: List[MessageRequest],
                               config: WorkloadConfig) -> List[MessageRequest]:
        """Apply periodic pattern to requests."""
        result = []
        period = config.period

        for i, req in enumerate(requests):
            # Periodic spike
            if i % period < period // 4:  # First quarter of period is spike
                req.timestamp = i // period * period + (i % period)
            else:
                # Stretch out non-spike messages
                req.timestamp = i + period // 4

            result.append(req)

        return result

    def _apply_random_pattern(self, requests: List[MessageRequest],
                             config: WorkloadConfig) -> List[MessageRequest]:
        """Apply random timing variation."""
        result = []

        for req in requests:
            # Add random jitter
            jitter = np.random.randint(-5, 6)
            req.timestamp = max(0, req.timestamp + jitter)
            result.append(req)

        # Sort by timestamp
        result.sort(key=lambda r: r.timestamp)

        return result


def generate_benchmark_workloads() -> Dict[str, WorkloadConfig]:
    """Generate benchmark workload configurations."""
    return {
        'uniform_point_to_point': WorkloadConfig(
            num_requests=1000,
            traffic_pattern=TrafficPattern.UNIFORM,
            communication_pattern=CommunicationPattern.POINT_TO_POINT,
            temporal_pattern=TemporalPattern.STEADY
        ),

        'hotspot_aggregation': WorkloadConfig(
            num_requests=1000,
            traffic_pattern=TrafficPattern.HOTSPOT,
            communication_pattern=CommunicationPattern.AGGREGATION,
            temporal_pattern=TemporalPattern.BURSTY,
            hotspot_ratio=0.2
        ),

        'hierarchical_broadcast': WorkloadConfig(
            num_requests=500,
            traffic_pattern=TrafficPattern.HIERARCHICAL,
            communication_pattern=CommunicationPattern.BROADCAST,
            temporal_pattern=TemporalPattern.PERIODIC,
            period=100
        ),

        'locality_gossip': WorkloadConfig(
            num_requests=1000,
            traffic_pattern=TrafficPattern.LOCALITY,
            communication_pattern=CommunicationPattern.GOSSIP,
            temporal_pattern=TemporalPattern.STEADY,
            locality_radius=3
        ),

        'bursty_multicast': WorkloadConfig(
            num_requests=1000,
            traffic_pattern=TrafficPattern.RANDOM,
            communication_pattern=CommunicationPattern.MULTICAST,
            temporal_pattern=TemporalPattern.BURSTY,
            burst_prob=0.15,
            burst_size=15
        ),
    }


if __name__ == "__main__":
    # Example usage
    from topology_generator import TopologyGenerator, TopologyType

    # Create a test topology
    generator = TopologyGenerator(seed=42)
    G = generator.generate(TopologyType.WATTS_STROGATZ,
                          generator.TopologyParams(n=100, k=6, p=0.1))

    # Generate workload
    workload_gen = WorkloadGenerator(G, seed=42)
    configs = generate_benchmark_workloads()

    for name, config in configs.items():
        print(f"\nGenerating workload: {name}")
        requests = workload_gen.generate(config)
        print(f"  Generated {len(requests)} requests")

        # Analyze workload
        sources = [r.source for r in requests]
        destinations = [r.destination for r in requests]

        print(f"  Unique sources: {len(set(sources))}")
        print(f"  Unique destinations: {len(set(destinations))}")
        print(f"  Avg message size: {np.mean([r.size for r in requests]):.2f} KB")
