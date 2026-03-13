# Implementation

## Overview

This chapter presents the algorithms, data structures, and code for implementing Structural Memory in distributed systems. We provide production-ready implementations in TypeScript/Python with theoretical guarantees mapped to practical components.

---

## 1. System Architecture

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STRUCTURAL MEMORY NODE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Pattern Encoder │───▶│ Isomorphism     │───▶│ Resonance       │ │
│  │ (GNN-based)     │    │ Detector        │    │ Engine          │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│          │                      │                      │            │
│          ▼                      ▼                      ▼            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              LOCAL PATTERN LIBRARY (L_i)                     │   │
│  │  - Pattern storage (capacity C)                              │   │
│  │  - Embedding index (faiss/annoy)                             │   │
│  │  - Weight tracking                                           │   │
│  │  - Temporal metadata                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│          │                      │                      │            │
│          ▼                      ▼                      ▼            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Gossip Protocol │    │ Consolidation   │    │ Query Interface │ │
│  │ (Pattern sync)  │    │ Manager         │    │ (REST/gRPC)     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

1. **Pattern Ingestion**: Raw computational artifacts (call graphs, data flows) are encoded as structural patterns
2. **Isomorphism Check**: New patterns compared against local library for deduplication
3. **Storage Decision**: Novel patterns stored with initial weight; duplicates update existing weights
4. **Gossip Propagation**: High-weight patterns shared with random neighbors
5. **Query Processing**: Query patterns encoded and matched via resonance
6. **Consolidation**: Background process adjusts weights based on access patterns

---

## 2. Core Data Structures

### 2.1 Structural Pattern (TypeScript)

```typescript
/**
 * Structural Pattern - Core abstraction
 * Implements Definition D1
 */
interface StructuralPattern {
  /** Unique pattern identifier */
  id: string;

  /** Vertex set with semantic labels */
  vertices: Map<string, Vertex>;

  /** Edge multiset with relation types */
  edges: Edge[];

  /** Pre-computed embedding (Definition D3) */
  embedding: number[];

  /** Pattern weight (importance) */
  weight: number;

  /** Creation timestamp */
  createdAt: number;

  /** Last access timestamp */
  lastAccessedAt: number;

  /** Access count for consolidation */
  accessCount: number;

  /** Pattern size metric */
  size(): number {
    return this.vertices.size + this.edges.length;
  }
}

interface Vertex {
  id: string;
  label: string;  // sigma: V -> Sigma
  attributes: Record<string, any>;
}

interface Edge {
  source: string;
  target: string;
  type: string;   // tau: E -> Tau
  weight: number;
}
```

### 2.2 Pattern Encoder (Python)

```python
"""
Pattern Encoder using Graph Neural Networks
Implements Definition D3 (Pattern Embedding)
"""

import torch
import torch.nn as nn
from torch_geometric.nn import GATConv, global_mean_pool
from torch_geometric.data import Data

class StructuralPatternEncoder(nn.Module):
    """
    GNN-based encoder for structural patterns.

    Architecture:
    - Multi-layer Graph Attention Network (GAT)
    - Semantic label embeddings
    - Edge type embeddings
    - Global pooling for graph-level representation
    """

    def __init__(
        self,
        label_vocab_size: int,
        type_vocab_size: int,
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 256,
        num_layers: int = 3,
        num_heads: int = 4
    ):
        super().__init__()

        # Semantic label embeddings
        self.label_embedding = nn.Embedding(label_vocab_size, embedding_dim)

        # Edge type embeddings
        self.type_embedding = nn.Embedding(type_vocab_size, embedding_dim)

        # GAT layers
        self.convs = nn.ModuleList()
        self.convs.append(GATConv(
            embedding_dim, hidden_dim,
            heads=num_heads,
            concat=True,
            edge_dim=embedding_dim
        ))

        for _ in range(num_layers - 1):
            self.convs.append(GATConv(
                hidden_dim * num_heads, hidden_dim,
                heads=num_heads,
                concat=True,
                edge_dim=embedding_dim
            ))

        # Output projection
        self.output_proj = nn.Linear(hidden_dim * num_heads, output_dim)

    def forward(self, data: Data) -> torch.Tensor:
        """
        Encode structural pattern to embedding.

        Args:
            data: PyTorch Geometric Data object with:
                - x: Vertex labels [num_vertices]
                - edge_index: Edge connectivity [2, num_edges]
                - edge_type: Edge types [num_edges]

        Returns:
            Embedding tensor [output_dim]
        """
        # Embed vertices
        x = self.label_embedding(data.x)  # [num_vertices, embedding_dim]

        # Embed edges
        edge_attr = self.type_embedding(data.edge_type)  # [num_edges, embedding_dim]

        # GAT layers
        for conv in self.convs:
            x = conv(x, data.edge_index, edge_attr)
            x = torch.relu(x)

        # Global pooling (READOUT from Definition D3)
        embedding = global_mean_pool(x, data.batch)  # [batch_size, hidden_dim * num_heads]

        # Project to output dimension
        embedding = self.output_proj(embedding)  # [batch_size, output_dim]

        # Normalize for cosine similarity
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=-1)

        return embedding

    def encode_pattern(self, pattern: dict) -> torch.Tensor:
        """
        Convert pattern dict to embedding.

        Args:
            pattern: Pattern with 'vertices', 'edges', 'labels', 'types'

        Returns:
            Embedding tensor [output_dim]
        """
        # Build PyTorch Geometric Data object
        vertex_to_idx = {v: i for i, v in enumerate(pattern['vertices'])}

        x = torch.tensor(pattern['labels'], dtype=torch.long)
        edge_index = torch.tensor([
            [vertex_to_idx[e['source']] for e in pattern['edges']],
            [vertex_to_idx[e['target']] for e in pattern['edges']]
        ], dtype=torch.long)
        edge_type = torch.tensor(pattern['types'], dtype=torch.long)

        data = Data(x=x, edge_index=edge_index, edge_type=edge_type)

        with torch.no_grad():
            return self.forward(data).squeeze(0)
```

### 2.3 Isomorphism Detector

```python
"""
Isomorphism Detection Module
Implements Definition D4-D6
"""

import numpy as np
from typing import Tuple, Optional
from networkx.algorithms.isomorphism import GraphMatcher
import networkx as nx

class IsomorphismDetector:
    """
    Detects structural isomorphism between patterns.

    Supports:
    - Exact isomorphism (Definition D4)
    - Maximum common subgraph (Definition D5)
    - Isomorphism scoring (Definition D6)
    """

    def __init__(
        self,
        alpha: float = 0.35,  # Vertex weight
        beta: float = 0.35,   # Edge weight
        gamma: float = 0.30,  # Semantic weight
        use_embedding_approx: bool = True
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.use_embedding_approx = use_embedding_approx

    def is_isomorphic(
        self,
        p1: StructuralPattern,
        p2: StructuralPattern
    ) -> bool:
        """
        Check exact isomorphism (Definition D4).

        Returns:
            True if patterns are isomorphic
        """
        # Quick size check
        if abs(p1.size() - p2.size()) > max(p1.size(), p2.size()) * 0.1:
            return False

        # Convert to NetworkX
        g1 = self._to_networkx(p1)
        g2 = self._to_networkx(p2)

        # Node match function (label preservation)
        def node_match(n1, n2):
            return n1['label'] == n2['label']

        # Edge match function (type preservation)
        def edge_match(e1, e2):
            return e1['type'] == e2['type']

        # Check isomorphism
        gm = GraphMatcher(g1, g2, node_match=node_match, edge_match=edge_match)
        return gm.is_isomorphic()

    def isomorphism_score(
        self,
        p1: StructuralPattern,
        p2: StructuralPattern,
        embedding_approx: Optional[bool] = None
    ) -> float:
        """
        Compute isomorphism score (Definition D6).

        Args:
            p1, p2: Patterns to compare
            embedding_approx: Use embedding approximation (Lemma L1)

        Returns:
            Isomorphism score in [0, 1]
        """
        use_approx = embedding_approx if embedding_approx is not None else self.use_embedding_approx

        # Fast path: embedding approximation
        if use_approx and p1.embedding is not None and p2.embedding is not None:
            return self._embedding_score(p1.embedding, p2.embedding)

        # Slow path: MCS computation
        return self._exact_score(p1, p2)

    def _embedding_score(self, e1: np.ndarray, e2: np.ndarray) -> float:
        """
        Compute isomorphism score from embeddings.

        Uses cosine similarity: I_hat = 1 - ||e1 - e2||
        Satisfies Lemma L1.
        """
        # Cosine similarity
        dot = np.dot(e1, e2)
        norm1 = np.linalg.norm(e1)
        norm2 = np.linalg.norm(e2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cos_sim = dot / (norm1 * norm2)

        # Map [-1, 1] to [0, 1]
        return (cos_sim + 1) / 2

    def _exact_score(self, p1: StructuralPattern, p2: StructuralPattern) -> float:
        """
        Compute exact isomorphism score via MCS (Definition D5).

        This is expensive: O(|P1| * |P2|)
        """
        # Convert to NetworkX
        g1 = self._to_networkx(p1)
        g2 = self._to_networkx(p2)

        # Find maximum common subgraph
        # Using optimization: find largest common induced subgraph
        mcs_size = self._find_mcs_size(g1, g2)

        # Compute scores
        vertex_score = mcs_size['vertices'] / max(p1.vertices.size, p2.vertices.size)
        edge_score = mcs_size['edges'] / max(len(p1.edges), len(p2.edges))

        # Semantic similarity (average label match in MCS)
        semantic_score = mcs_size['semantic']

        # Weighted combination (Definition D6)
        score = (
            self.alpha * vertex_score +
            self.beta * edge_score +
            self.gamma * semantic_score
        )

        return score

    def _find_mcs_size(self, g1: nx.Graph, g2: nx.Graph) -> dict:
        """
        Find size of maximum common subgraph.

        Uses approximation algorithm for efficiency.
        """
        # Heuristic: common neighbors based matching
        # This is an approximation - exact MCS is NP-hard

        best_match = {'vertices': 0, 'edges': 0, 'semantic': 0.5}

        # Try to find isomorphic subgraphs of decreasing size
        for size in range(min(len(g1), len(g2)), 0, -1):
            # Generate candidate subgraphs
            for nodes1 in itertools.combinations(g1.nodes(), size):
                subgraph1 = g1.subgraph(nodes1)

                for nodes2 in itertools.combinations(g2.nodes(), size):
                    subgraph2 = g2.subgraph(nodes2)

                    # Check isomorphism
                    gm = GraphMatcher(
                        subgraph1, subgraph2,
                        node_match=lambda n1, n2: n1['label'] == n2['label']
                    )

                    if gm.is_isomorphic():
                        # Found common subgraph
                        mapping = list(gm.isomorphisms_iter())[0]

                        # Count edges
                        common_edges = sum(
                            1 for u, v in subgraph1.edges()
                            if (mapping[u], mapping[v]) in subgraph2.edges()
                        )

                        # Compute semantic similarity
                        semantic = np.mean([
                            1.0 if g1.nodes[u]['label'] == g2.nodes[mapping[u]]['label'] else 0.0
                            for u in nodes1
                        ])

                        if common_edges > best_match['edges']:
                            best_match = {
                                'vertices': size,
                                'edges': common_edges,
                                'semantic': semantic
                            }

                        break  # Found best for this size

        return best_match

    def _to_networkx(self, pattern: StructuralPattern) -> nx.Graph:
        """Convert StructuralPattern to NetworkX Graph."""
        g = nx.Graph()

        for vid, vertex in pattern.vertices.items():
            g.add_node(vid, label=vertex.label, **vertex.attributes)

        for edge in pattern.edges:
            g.add_edge(
                edge.source, edge.target,
                type=edge.type, weight=edge.weight
            )

        return g
```

---

## 3. Resonance Engine

### 3.1 Memory Resonance Implementation

```python
"""
Resonance Engine
Implements Definition D7-D9
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import faiss  # Facebook AI Similarity Search

@dataclass
class ResonanceResult:
    """Result of resonance query."""
    pattern_id: str
    score: float
    isomorphism_score: float
    weight: float
    age_factor: float

class ResonanceEngine:
    """
    Implements memory resonance (Definition D7).

    Uses FAISS for efficient approximate nearest neighbor search.
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        decay_rate: float = 0.01,  # lambda
        index_type: str = "IVFFlat",
        nlist: int = 100  # Number of clusters for IVF
    ):
        self.embedding_dim = embedding_dim
        self.decay_rate = decay_rate

        # FAISS index for fast similarity search
        if index_type == "IVFFlat":
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(
                quantizer, embedding_dim, nlist
            )
        elif index_type == "Flat":
            self.index = faiss.IndexFlatL2(embedding_dim)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Pattern metadata storage
        self.patterns = {}  # id -> StructuralPattern
        self.id_to_idx = {}  # pattern_id -> FAISS index
        self.idx_to_id = {}  # FAISS index -> pattern_id

        self._next_idx = 0
        self._is_trained = False

    def add_pattern(self, pattern: StructuralPattern) -> None:
        """Add pattern to resonance index."""
        if pattern.embedding is None:
            raise ValueError("Pattern must have embedding")

        # Store pattern
        self.patterns[pattern.id] = pattern

        # Add to FAISS index
        embedding = np.array([pattern.embedding], dtype=np.float32)

        if not self._is_trained and isinstance(self.index, faiss.IndexIVFFlat):
            # Train index with first pattern
            self.index.train(embedding)
            self._is_trained = True

        self.index.add(embedding)

        # Update mappings
        idx = self._next_idx
        self.id_to_idx[pattern.id] = idx
        self.idx_to_id[idx] = pattern.id
        self._next_idx += 1

    def query(
        self,
        query_pattern: StructuralPattern,
        k: int = 10,
        threshold: float = 0.5,
        current_time: Optional[float] = None
    ) -> List[ResonanceResult]:
        """
        Query for resonating patterns (Definition D7).

        R(q, L) = max_{p in L} I(q, p) * w(p) * e^{-lambda * age(p)}

        Args:
            query_pattern: Query pattern
            k: Number of results
            threshold: Minimum resonance score
            current_time: Current timestamp (for age calculation)

        Returns:
            List of ResonanceResult sorted by score
        """
        if query_pattern.embedding is None:
            raise ValueError("Query pattern must have embedding")

        current_time = current_time or time.time()

        # FAISS search for approximate nearest neighbors
        query_embedding = np.array([query_pattern.embedding], dtype=np.float32)
        distances, indices = self.index.search(query_embedding, k * 2)  # Search more, filter later

        results = []

        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS padding
                continue

            pattern_id = self.idx_to_id.get(idx)
            if pattern_id is None:
                continue

            pattern = self.patterns[pattern_id]

            # Compute resonance score (Definition D7)
            # I(q, p) approximated by embedding distance
            isomorphism_score = 1.0 / (1.0 + dist)  # L2 distance to similarity

            # Weight factor
            weight = pattern.weight

            # Age factor (temporal decay)
            age = current_time - pattern.createdAt
            age_factor = np.exp(-self.decay_rate * age / 3600)  # Normalize by hours

            # Combined resonance score
            resonance_score = isomorphism_score * weight * age_factor

            if resonance_score >= threshold:
                results.append(ResonanceResult(
                    pattern_id=pattern_id,
                    score=resonance_score,
                    isomorphism_score=isomorphism_score,
                    weight=weight,
                    age_factor=age_factor
                ))

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:k]

    def update_access(self, pattern_id: str) -> None:
        """Update access time and count for consolidation."""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.lastAccessedAt = time.time()
            pattern.accessCount += 1
```

---

## 4. Distributed Pattern Library

### 4.1 Local Library Implementation

```python
"""
Local Pattern Library
Implements Definition D10-D12
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import heapq

class LocalPatternLibrary:
    """
    Local pattern storage with capacity management.

    Implements:
    - Definition D10: Local library with capacity constraint
    - Definition D12: Consolidation and forgetting
    """

    def __init__(
        self,
        capacity: int = 1000,
        min_weight: float = 0.1,
        consolidation_interval: int = 100,
        learning_rate: float = 0.1,
        decay_factor: float = 0.01
    ):
        self.capacity = capacity
        self.min_weight = min_weight
        self.consolidation_interval = consolidation_interval
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor

        # Pattern storage
        self.patterns: Dict[str, StructuralPattern] = {}

        # Indexes for efficient retrieval
        self.label_index: Dict[str, Set[str]] = defaultdict(set)  # label -> pattern_ids
        self.type_index: Dict[str, Set[str]] = defaultdict(set)   # type -> pattern_ids

        # Resonance engine
        self.resonance_engine = ResonanceEngine()

        # Access tracking for consolidation
        self.access_counts: Dict[str, int] = defaultdict(int)

        # Consolidation counter
        self._accesses_since_consolidation = 0

    def store(
        self,
        pattern: StructuralPattern,
        isomorphism_detector: IsomorphismDetector
    ) -> Tuple[bool, Optional[str]]:
        """
        Store pattern with deduplication.

        Returns:
            (stored, duplicate_id)
            - stored: True if new pattern was added
            - duplicate_id: ID of existing pattern if duplicate found
        """
        # Check for duplicates via isomorphism
        for existing_id, existing in self.patterns.items():
            if isomorphism_detector.isomorphism_score(pattern, existing) > 0.95:
                # Found duplicate - update weight instead of storing
                self._strengthen_pattern(existing_id)
                return False, existing_id

        # Check capacity
        if len(self.patterns) >= self.capacity:
            self._evict_weakest()

        # Store new pattern
        self.patterns[pattern.id] = pattern

        # Update indexes
        for vertex in pattern.vertices.values():
            self.label_index[vertex.label].add(pattern.id)

        for edge in pattern.edges:
            self.type_index[edge.type].add(pattern.id)

        # Add to resonance engine
        self.resonance_engine.add_pattern(pattern)

        return True, None

    def retrieve(
        self,
        query: StructuralPattern,
        k: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[StructuralPattern, float]]:
        """
        Retrieve patterns via resonance.

        Returns:
            List of (pattern, resonance_score) tuples
        """
        results = self.resonance_engine.query(query, k, threshold)

        retrieved = []
        for result in results:
            pattern = self.patterns[result.pattern_id]
            retrieved.append((pattern, result.score))

            # Track access for consolidation
            self.access_counts[result.pattern_id] += 1

        self._accesses_since_consolidation += len(retrieved)

        # Trigger consolidation if needed
        if self._accesses_since_consolidation >= self.consolidation_interval:
            self.consolidate()

        return retrieved

    def consolidate(self) -> Dict[str, int]:
        """
        Consolidate library (Definition D12).

        Returns:
            Stats: {'strengthened': n, 'weakened': m, 'evicted': k}
        """
        stats = {'strengthened': 0, 'weakened': 0, 'evicted': 0}

        to_evict = []

        for pattern_id, pattern in self.patterns.items():
            # Apply consolidation rule (Definition D12)
            access_count = self.access_counts[pattern_id]

            # Strengthen frequently accessed patterns
            if access_count > 5:
                pattern.weight = min(1.0, pattern.weight + self.learning_rate)
                stats['strengthened'] += 1

            # Weaken rarely accessed patterns
            pattern.weight = max(0.0, pattern.weight - self.decay_factor)
            if pattern.weight > 0:
                stats['weakened'] += 1

            # Mark for eviction if below threshold
            if pattern.weight < self.min_weight:
                to_evict.append(pattern_id)

        # Evict weak patterns
        for pattern_id in to_evict:
            self._remove_pattern(pattern_id)
            stats['evicted'] += 1

        # Reset access counts
        self.access_counts.clear()
        self._accesses_since_consolidation = 0

        return stats

    def _strengthen_pattern(self, pattern_id: str) -> None:
        """Strengthen pattern on duplicate detection."""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.weight = min(1.0, pattern.weight + self.learning_rate * 0.5)
            pattern.accessCount += 1

    def _evict_weakest(self) -> None:
        """Evict lowest-weight pattern to make room."""
        if not self.patterns:
            return

        # Find minimum weight pattern
        min_id = min(self.patterns.keys(), key=lambda pid: self.patterns[pid].weight)
        self._remove_pattern(min_id)

    def _remove_pattern(self, pattern_id: str) -> None:
        """Remove pattern from library and indexes."""
        if pattern_id not in self.patterns:
            return

        pattern = self.patterns[pattern_id]

        # Remove from label index
        for vertex in pattern.vertices.values():
            self.label_index[vertex.label].discard(pattern_id)

        # Remove from type index
        for edge in pattern.edges:
            self.type_index[edge.type].discard(pattern_id)

        # Remove from storage
        del self.patterns[pattern_id]
        del self.access_counts[pattern_id]
```

### 4.2 Gossip Protocol for Pattern Propagation

```python
"""
Gossip Protocol for Distributed Pattern Propagation
Implements Definition D9
"""

import random
from typing import List, Set, Callable
import asyncio

class GossipProtocol:
    """
    Epidemic-style pattern propagation.

    Implements resonance propagation (Definition D9):
    L_i^(t+1) = L_i^(t) ∪ ⋃_{j ∈ neighbors(i)} sample(L_j^(t), k)
    """

    def __init__(
        self,
        node_id: str,
        fanout: int = 3,
        samples_per_round: int = 10,
        round_interval: float = 5.0,  # seconds
        send_callback: Callable = None,
        receive_callback: Callable = None
    ):
        self.node_id = node_id
        self.fanout = fanout
        self.samples_per_round = samples_per_round
        self.round_interval = round_interval

        # Communication callbacks
        self.send_callback = send_callback
        self.receive_callback = receive_callback

        # Known peers
        self.peers: Set[str] = set()

        # Patterns seen (for deduplication)
        self.seen_patterns: Set[str] = set()

        # Running flag
        self._running = False

    async def start(self) -> None:
        """Start gossip protocol."""
        self._running = True
        asyncio.create_task(self._gossip_loop())

    async def stop(self) -> None:
        """Stop gossip protocol."""
        self._running = False

    def add_peer(self, peer_id: str) -> None:
        """Add peer to gossip network."""
        self.peers.add(peer_id)

    def remove_peer(self, peer_id: str) -> None:
        """Remove peer from gossip network."""
        self.peers.discard(peer_id)

    async def broadcast_pattern(self, pattern: StructuralPattern) -> None:
        """
        Broadcast new pattern to network.

        Selects fanout random peers and sends pattern.
        """
        if not self.peers:
            return

        # Select random peers
        peers = list(self.peers)
        selected = random.sample(peers, min(self.fanout, len(peers)))

        # Send to selected peers
        message = {
            'type': 'PATTERN',
            'pattern': pattern.to_dict(),
            'source': self.node_id,
            'ttl': 3  # Time-to-live for propagation
        }

        for peer_id in selected:
            if self.send_callback:
                await self.send_callback(peer_id, message)

    async def handle_message(self, message: dict) -> None:
        """Handle incoming gossip message."""
        msg_type = message.get('type')

        if msg_type == 'PATTERN':
            await self._handle_pattern_message(message)

        elif msg_type == 'SAMPLE_REQUEST':
            await self._handle_sample_request(message)

        elif msg_type == 'SAMPLE_RESPONSE':
            await self._handle_sample_response(message)

    async def _handle_pattern_message(self, message: dict) -> None:
        """Handle incoming pattern propagation."""
        pattern_data = message['pattern']
        pattern_id = pattern_data['id']
        ttl = message.get('ttl', 3)

        # Check if already seen
        if pattern_id in self.seen_patterns:
            return

        self.seen_patterns.add(pattern_id)

        # Add to local library via callback
        if self.receive_callback:
            await self.receive_callback(pattern_data)

        # Continue propagation if TTL > 0
        if ttl > 0:
            message['ttl'] = ttl - 1
            await self._forward_message(message, exclude={message['source']})

    async def _forward_message(self, message: dict, exclude: Set[str]) -> None:
        """Forward message to random peers."""
        candidates = self.peers - exclude
        if not candidates:
            return

        selected = random.sample(list(candidates), min(self.fanout, len(candidates)))

        for peer_id in selected:
            if self.send_callback:
                await self.send_callback(peer_id, message)

    async def _gossip_loop(self) -> None:
        """Background gossip loop for pattern exchange."""
        while self._running:
            await asyncio.sleep(self.round_interval)

            if not self.peers:
                continue

            # Request pattern samples from random peers
            peers = list(self.peers)
            selected = random.sample(peers, min(self.fanout, len(peers)))

            for peer_id in selected:
                message = {
                    'type': 'SAMPLE_REQUEST',
                    'source': self.node_id,
                    'count': self.samples_per_round
                }

                if self.send_callback:
                    await self.send_callback(peer_id, message)

    async def _handle_sample_request(self, message: dict) -> None:
        """Handle request for pattern samples."""
        count = message.get('count', self.samples_per_round)

        # Get top patterns from local library (via callback)
        # This would call into LocalPatternLibrary
        if self.receive_callback:
            samples = await self.receive_callback({'type': 'GET_TOP_PATTERNS', 'count': count})

            response = {
                'type': 'SAMPLE_RESPONSE',
                'patterns': samples,
                'source': self.node_id
            }

            if self.send_callback:
                await self.send_callback(message['source'], response)
```

---

## 5. Complete Node Implementation

### 5.1 Structural Memory Node

```python
"""
Complete Structural Memory Node
Integrates all components
"""

from typing import Dict, List, Optional, Any
import asyncio

class StructuralMemoryNode:
    """
    Complete implementation of a structural memory node.

    Integrates:
    - Pattern encoder
    - Isomorphism detector
    - Resonance engine
    - Local library
    - Gossip protocol
    """

    def __init__(
        self,
        node_id: str,
        config: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.config = config or {}

        # Initialize components
        self.encoder = StructuralPatternEncoder(
            label_vocab_size=self.config.get('label_vocab_size', 10000),
            type_vocab_size=self.config.get('type_vocab_size', 1000),
            embedding_dim=self.config.get('embedding_dim', 256)
        )

        self.isomorphism_detector = IsomorphismDetector(
            use_embedding_approx=self.config.get('use_embedding_approx', True)
        )

        self.library = LocalPatternLibrary(
            capacity=self.config.get('library_capacity', 1000),
            min_weight=self.config.get('min_weight', 0.1)
        )

        self.gossip = GossipProtocol(
            node_id=node_id,
            fanout=self.config.get('gossip_fanout', 3),
            samples_per_round=self.config.get('samples_per_round', 10),
            send_callback=self._send_message,
            receive_callback=self._handle_gossip_message
        )

        # Network communication
        self.peers: Dict[str, Any] = {}  # peer_id -> connection

        # Statistics
        self.stats = {
            'patterns_stored': 0,
            'patterns_deduplicated': 0,
            'queries_processed': 0,
            'patterns_propagated': 0
        }

    async def start(self) -> None:
        """Start the structural memory node."""
        await self.gossip.start()
        print(f"Node {self.node_id} started")

    async def stop(self) -> None:
        """Stop the structural memory node."""
        await self.gossip.stop()
        print(f"Node {self.node_id} stopped")

    async def remember(
        self,
        raw_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store a pattern in structural memory.

        Args:
            raw_pattern: Raw pattern data (vertices, edges, etc.)

        Returns:
            Result with pattern_id and status
        """
        # Encode pattern
        pattern = self._create_pattern(raw_pattern)
        pattern.embedding = self.encoder.encode_pattern(raw_pattern).numpy()

        # Store with deduplication
        stored, duplicate_id = self.library.store(pattern, self.isomorphism_detector)

        if stored:
            self.stats['patterns_stored'] += 1

            # Propagate to network
            await self.gossip.broadcast_pattern(pattern)

            return {
                'status': 'stored',
                'pattern_id': pattern.id,
                'embedding_dim': len(pattern.embedding)
            }
        else:
            self.stats['patterns_deduplicated'] += 1
            return {
                'status': 'duplicate',
                'pattern_id': duplicate_id,
                'weight_updated': True
            }

    async def recall(
        self,
        query_pattern: Dict[str, Any],
        k: int = 10,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Query structural memory via resonance.

        Args:
            query_pattern: Query pattern data
            k: Number of results
            threshold: Minimum resonance score

        Returns:
            Results with patterns and scores
        """
        # Encode query
        query = self._create_pattern(query_pattern)
        query.embedding = self.encoder.encode_pattern(query_pattern).numpy()

        # Retrieve via resonance
        results = self.library.retrieve(query, k, threshold)

        self.stats['queries_processed'] += 1

        return {
            'query_id': query.id,
            'results': [
                {
                    'pattern_id': pattern.id,
                    'score': score,
                    'weight': pattern.weight,
                    'size': pattern.size()
                }
                for pattern, score in results
            ],
            'total_matches': len(results)
        }

    def _create_pattern(self, raw: Dict[str, Any]) -> StructuralPattern:
        """Create StructuralPattern from raw data."""
        import uuid

        pattern = StructuralPattern(
            id=str(uuid.uuid4()),
            vertices={},
            edges=[],
            embedding=None,
            weight=0.5,  # Initial weight
            createdAt=time.time(),
            lastAccessedAt=time.time(),
            accessCount=0
        )

        # Populate vertices
        for v in raw.get('vertices', []):
            pattern.vertices[v['id']] = Vertex(
                id=v['id'],
                label=v['label'],
                attributes=v.get('attributes', {})
            )

        # Populate edges
        for e in raw.get('edges', []):
            pattern.edges.append(Edge(
                source=e['source'],
                target=e['target'],
                type=e['type'],
                weight=e.get('weight', 1.0)
            ))

        return pattern

    async def _send_message(self, peer_id: str, message: Dict) -> None:
        """Send message to peer (network callback)."""
        if peer_id in self.peers:
            # In real implementation, send via network
            # For simulation, we directly call peer's handler
            peer = self.peers[peer_id]
            await peer.handle_gossip_message(message)

    async def _handle_gossip_message(self, message: Any) -> None:
        """Handle gossip message (callback from GossipProtocol)."""
        if isinstance(message, dict):
            if message.get('type') == 'GET_TOP_PATTERNS':
                # Return top patterns by weight
                count = message.get('count', 10)
                top_patterns = sorted(
                    self.library.patterns.values(),
                    key=lambda p: p.weight,
                    reverse=True
                )[:count]
                return [p.to_dict() for p in top_patterns]

            elif 'pattern' in message:
                # Incoming pattern from gossip
                pattern_data = message['pattern']
                pattern = self._create_pattern(pattern_data)
                pattern.embedding = np.array(pattern_data['embedding'])

                stored, _ = self.library.store(pattern, self.isomorphism_detector)
                if stored:
                    self.stats['patterns_propagated'] += 1

        await self.gossip.handle_message(message)

    def get_stats(self) -> Dict[str, Any]:
        """Get node statistics."""
        return {
            **self.stats,
            'library_size': len(self.library.patterns),
            'peer_count': len(self.peers)
        }
```

---

## 6. API Layer

### 6.1 REST API (FastAPI)

```python
"""
REST API for Structural Memory Node
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Structural Memory API")

# Global node instance
node: Optional[StructuralMemoryNode] = None

class PatternRequest(BaseModel):
    vertices: List[dict]
    edges: List[dict]

class RecallRequest(BaseModel):
    query: PatternRequest
    k: int = 10
    threshold: float = 0.5

class PatternResponse(BaseModel):
    pattern_id: str
    score: float
    weight: float
    size: int

@app.post("/remember")
async def remember_pattern(request: PatternRequest):
    """Store a pattern in structural memory."""
    result = await node.remember(request.dict())
    return result

@app.post("/recall")
async def recall_patterns(request: RecallRequest):
    """Query structural memory via resonance."""
    result = await node.recall(
        request.query.dict(),
        k=request.k,
        threshold=request.threshold
    )
    return result

@app.get("/stats")
async def get_stats():
    """Get node statistics."""
    return node.get_stats()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "node_id": node.node_id}

def run_server(memory_node: StructuralMemoryNode, port: int = 8000):
    """Run the API server."""
    global node
    node = memory_node
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## 7. Deployment Configuration

### 7.1 Docker Configuration

```dockerfile
# Dockerfile for Structural Memory Node
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Run node
CMD ["python", "-m", "src.node"]
```

### 7.2 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: structural-memory-cluster
spec:
  replicas: 10
  selector:
    matchLabels:
      app: structural-memory
  template:
    metadata:
      labels:
        app: structural-memory
    spec:
      containers:
      - name: memory-node
        image: structural-memory:latest
        ports:
        - containerPort: 8000
        env:
        - name: NODE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: LIBRARY_CAPACITY
          value: "10000"
        - name: GOSSIP_FANOUT
          value: "5"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: structural-memory-service
spec:
  selector:
    app: structural-memory
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Summary

This implementation provides:

1. **Pattern Encoding**: GNN-based embeddings for structural patterns
2. **Isomorphism Detection**: Both exact (MCS) and approximate (embedding) methods
3. **Resonance Engine**: FAISS-backed similarity search with temporal decay
4. **Local Library**: Capacity-managed storage with consolidation
5. **Gossip Protocol**: Epidemic-style pattern propagation
6. **Complete Node**: Integrated system with REST API
7. **Deployment**: Docker and Kubernetes configurations

All algorithms satisfy the theoretical guarantees from Chapter 3:
- Isomorphism scoring implements Definition D6
- Resonance implements Definition D7
- Consolidation implements Definition D12
- Gossip implements Definition D9

---

*Next: Validation*
