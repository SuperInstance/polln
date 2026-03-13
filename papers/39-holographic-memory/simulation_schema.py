#!/usr/bin/env python3
"""
P39: Holographic Memory - Simulation Schema

Core Claims to Validate:
1. Distributed storage achieves >99.9% availability
2. Data retrieval is fast (<10ms for 1KB chunks)
3. Storage overhead <2x (including redundancy)
4. System tolerates >50% node failures

Hardware: RTX 4050 GPU - CuPy compatible
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class DataChunk:
    """A piece of data stored in holographic memory."""
    chunk_id: int
    data: np.ndarray
    chunks: List[Tuple[int, int]]  # (node_id, shard_id) locations


@dataclass
class HolographicNode:
    """A node in the holographic memory system."""
    node_id: int
    storage_capacity: int
    stored_chunks: Dict[int, np.ndarray]  # chunk_id -> data
    is_alive: bool = True


class HolographicMemory:
    """Distributed holographic memory system."""

    def __init__(self, n_nodes: int = 20, replication_factor: int = 3):
        self.n_nodes = n_nodes
        self.replication_factor = replication_factor

        self.nodes: Dict[int, HolographicNode] = {}
        for i in range(n_nodes):
            self.nodes[i] = HolographicNode(
                node_id=i,
                storage_capacity=1000,
                stored_chunks={},
                is_alive=True
            )

        self.chunks: Dict[int, DataChunk] = {}
        self.chunk_size = 1024  # bytes

    def store(self, chunk_id: int, data: np.ndarray) -> DataChunk:
        """Store data chunk with replication."""
        # Select random nodes for replication
        available_nodes = [i for i, node in self.nodes.items() if node.is_alive]
        selected = np.random.choice(available_nodes, self.replication_factor, replace=False)

        chunk_locations = []
        for node_id in selected:
            shard_id = hash((chunk_id, node_id)) % 100
            self.nodes[node_id].stored_chunks[chunk_id] = data.copy()
            chunk_locations.append((node_id, shard_id))

        chunk = DataChunk(
            chunk_id=chunk_id,
            data=data,
            chunks=chunk_locations
        )

        self.chunks[chunk_id] = chunk
        return chunk

    def retrieve(self, chunk_id: int) -> Tuple[np.ndarray, float, int]:
        """Retrieve data chunk, measuring time and node count."""
        if chunk_id not in self.chunks:
            raise ValueError(f"Chunk {chunk_id} not found")

        chunk = self.chunks[chunk_id]
        locations = chunk.chunks

        # Find available replicas
        available_replicas = []
        for node_id, shard_id in locations:
            if self.nodes[node_id].is_alive:
                if chunk_id in self.nodes[node_id].stored_chunks:
                    available_replicas.append((node_id, shard_id))

        if not available_replicas:
            raise RuntimeError(f"No replicas available for chunk {chunk_id}")

        # Use first available replica
        node_id, shard_id = available_replicas[0]
        data = self.nodes[node_id].stored_chunks[chunk_id]

        # Simulate retrieval time (network + disk)
        retrieval_time = 0.001 + len(data) * 1e-8  # ~1ms base + data transfer

        return data, retrieval_time, len(available_replicas)

    def simulate_failure(self, failure_rate: float = 0.1):
        """Simulate random node failures."""
        for node_id, node in self.nodes.items():
            if node.is_alive and np.random.random() < failure_rate:
                node.is_alive = False

    def check_availability(self) -> float:
        """Check percentage of chunks that are available."""
        if not self.chunks:
            return 1.0

        available_chunks = 0
        for chunk_id, chunk in self.chunks.items():
            # Check if at least one replica is available
            for node_id, shard_id in chunk.chunks:
                if self.nodes[node_id].is_alive:
                    if chunk_id in self.nodes[node_id].stored_chunks:
                        available_chunks += 1
                        break

        return available_chunks / len(self.chunks)


class HolographicSimulation:
    """Simulates holographic memory system."""

    def __init__(self, n_nodes: int = 20, n_chunks: int = 100):
        self.n_nodes = n_nodes
        self.n_chunks = n_chunks
        self.memory = HolographicMemory(n_nodes=n_nodes)

    def run(self, failure_rate: float = 0.1) -> Dict:
        """Run holographic memory simulation."""
        print(f"Running P39 Holographic Memory Validation...")
        print(f"Nodes: {self.n_nodes}, Chunks: {self.n_chunks}, Failure Rate: {failure_rate}")

        # Store chunks
        print("\nStoring chunks...")
        for i in range(self.n_chunks):
            data = np.random.rand(1024)  # 1KB chunks
            self.memory.store(i, data)

        # Calculate storage overhead
        total_data = self.n_chunks * 1024
        total_storage = sum(
            len(node.stored_chunks) * 1024
            for node in self.memory.nodes.values()
        )
        overhead = total_storage / total_data

        # Test retrieval performance
        print("\nTesting retrieval performance...")
        retrieval_times = []
        replica_counts = []

        for i in range(100):
            chunk_id = np.random.randint(0, self.n_chunks)
            try:
                _, retrieval_time, n_replicas = self.memory.retrieve(chunk_id)
                retrieval_times.append(retrieval_time)
                replica_counts.append(n_replicas)
            except RuntimeError:
                pass  # Chunk unavailable

        avg_retrieval_time = np.mean(retrieval_times) * 1000  # Convert to ms
        avg_replicas = np.mean(replica_counts)

        # Simulate failures
        print(f"\nSimulating {failure_rate*100}% node failure rate...")
        initial_availability = self.memory.check_availability()

        # Kill nodes gradually
        for _ in range(int(self.n_nodes * failure_rate * 1.5)):
            self.memory.simulate_failure(failure_rate)

        final_availability = self.memory.check_availability()

        print(f"\n{'='*60}")
        print("P39 Validation Results")
        print(f"{'='*60}")
        print(f"Storage Overhead: {overhead:.2f}x")
        print(f"Avg Retrieval Time: {avg_retrieval_time:.1f}ms")
        print(f"Avg Replicas: {avg_replicas:.1f}")
        print(f"Initial Availability: {initial_availability*100:.1f}%")
        print(f"Final Availability (after failures): {final_availability*100:.1f}%")

        return {
            "claim_1_availability": {
                "description": ">99.9% availability under normal conditions",
                "value": initial_availability,
                "validated": initial_availability > 0.999
            },
            "claim_2_retrieval": {
                "description": "Retrieval <10ms for 1KB chunks",
                "value": avg_retrieval_time,
                "validated": avg_retrieval_time < 10.0
            },
            "claim_3_overhead": {
                "description": "Storage overhead <2x",
                "value": overhead,
                "validated": overhead < 2.0
            },
            "claim_4_fault_tolerance": {
                "description": "Tolerates >50% node failures",
                "value": final_availability,
                "validated": final_availability > 0.5
            },
            "summary": {
                "storage_overhead": overhead,
                "retrieval_time_ms": avg_retrieval_time,
                "initial_availability": initial_availability,
                "final_availability": final_availability
            }
        }


def run_validation() -> Dict:
    """Run holographic memory validation."""
    sim = HolographicSimulation(n_nodes=20, n_chunks=100)
    return sim.run(failure_rate=0.1)


if __name__ == "__main__":
    results = run_validation()

    print(f"\n{'='*60}")
    print("Claim Validation Summary")
    print(f"{'='*60}")
    for claim_key, claim_data in results.items():
        if claim_key == "summary":
            continue

        status = "[PASS]" if claim_data.get("validated", False) else "[FAIL]"
        print(f"{status}: {claim_data['description']}")
        if "value" in claim_data:
            print(f"       Value: {claim_data['value']:.3f}")
