"""
ANN Index Parameter Tuning for POLLN

This script tunes Approximate Nearest Neighbor (ANN) index parameters
to find optimal configurations for KV-anchor matching.

ANN algorithms tested:
- HNSW (Hierarchical Navigable Small World)
- LSH (Locality Sensitive Hashing)
- Ball Tree
- IVF (Inverted File Index)

Parameters tuned:
- HNSW: M (connectivity), efConstruction, efSearch
- LSH: Number of bands, hash functions
- Ball Tree: Leaf size
- IVF: Number of clusters, nprobe

Metrics:
- Recall (fraction of true neighbors found)
- Query time (ms)
- Index size (bytes)
- Build time (s)
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import time
from collections import defaultdict

class ANNAlgorithm(Enum):
    """ANN index algorithms"""
    HNSW = "hnsw"
    LSH = "lsh"
    BALL_TREE = "ball_tree"
    IVF = "ivf"
    FAISS = "faiss"

@dataclass
class ANNResult:
    """Results from ANN experiment"""
    algorithm: ANNAlgorithm
    parameters: Dict[str, Any]
    recall: float
    query_time_ms: float
    build_time_s: float
    index_size_bytes: int
    neighbors_per_query: int
    k: int

class HNSWIndex:
    """
    Simplified HNSW (Hierarchical Navigable Small World) implementation

    Key parameters:
    - M: Max connections per node (higher = better recall, slower build)
    - efConstruction: Size of candidate list during build
    - efSearch: Size of candidate list during search
    """

    def __init__(self, M: int = 16, efConstruction: int = 200):
        """
        Initialize HNSW index

        Args:
            M: Max connections per node (default: 16)
            efConstruction: Build-time candidate list size (default: 200)
        """
        self.M = M
        self.efConstruction = efConstruction
        self.efSearch = efConstruction  # Default efSearch = efConstruction

        self.data = []
        self.graph = defaultdict(list)  # node_id -> [neighbor_ids]
        self.entry_point = None
        self.max_level = 0

    def add(self, vector: np.ndarray):
        """Add vector to index"""
        node_id = len(self.data)
        self.data.append(vector)

        # Determine max level for this node
        level = int(-np.log(np.random.random()) * 1.0) + 1
        self.max_level = max(self.max_level, level)

        if self.entry_point is None:
            self.entry_point = node_id
            return

        # Search from top down
        current = self.entry_point if self.entry_point is not None else 0

        # Greedy search at each level
        for lev in range(self.max_level, level, -1):
            current = self._search_level(vector, current, lev, 1)

        # Insert at each level up to node's level
        for lev in range(min(level, self.max_level) + 1):
            # Find closest neighbors
            candidates = self._search_level(vector, current, lev, self.efConstruction)

            # Select M closest
            distances = np.array([
                np.linalg.norm(vector - self.data[c])
                for c in candidates
            ])
            closest = candidates[np.argsort(distances)[:self.M]]

            # Add connections (bidirectional)
            for neighbor in closest:
                self.graph[(node_id, lev)].append(neighbor)
                self.graph[(neighbor, lev)].append(node_id)

                # Prune if too many connections
                if len(self.graph[(neighbor, lev)]) > self.M:
                    neighbor_dist = np.array([
                        np.linalg.norm(self.data[neighbor] - self.data[n])
                        for n in self.graph[(neighbor, lev)]
                    ])
                    keep_idx = np.argsort(neighbor_dist)[:self.M]
                    self.graph[(neighbor, lev)] = [self.graph[(neighbor, lev)][i] for i in keep_idx]

    def _search_level(
        self,
        query: np.ndarray,
        entry: int,
        level: int,
        ef: int
    ) -> List[int]:
        """Search at specific level"""
        visited = {entry}
        candidates = [(np.linalg.norm(query - self.data[entry]), entry)]
        heapq = [(np.linalg.norm(query - self.data[entry]), entry)]

        while heapq:
            dist, current = heapq[0]

            # Check if we can stop
            if len(candidates) >= ef:
                worst_dist = max(d for d, _ in candidates)
                if dist > worst_dist:
                    break

            heapq.pop(0)

            # Check neighbors at this level
            for neighbor in self.graph[(current, level)]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbor_dist = np.linalg.norm(query - self.data[neighbor])

                    if len(candidates) < ef:
                        candidates.append((neighbor_dist, neighbor))
                        heapq.append((neighbor_dist, neighbor))
                    elif neighbor_dist < max(d for d, _ in candidates):
                        # Replace worst candidate
                        worst_idx = max(range(len(candidates)), key=lambda i: candidates[i][0])
                        candidates[worst_idx] = (neighbor_dist, neighbor)
                        heapq.append((neighbor_dist, neighbor))

        return [node for _, node in candidates]

    def search(self, query: np.ndarray, k: int, efSearch: int = None) -> List[Tuple[int, float]]:
        """
        Search for k nearest neighbors

        Args:
            query: Query vector
            k: Number of neighbors to return
            efSearch: Search-time candidate list size

        Returns:
            List of (node_id, distance) tuples
        """
        if efSearch is not None:
            self.efSearch = efSearch

        if not self.data:
            return []

        # Search from top level down
        current = self.entry_point if self.entry_point is not None else 0

        for level in range(self.max_level, 0, -1):
            current = self._search_level(query, current, level, 1)[0]

        # Search at level 0
        candidates = self._search_level(query, current, 0, self.efSearch)

        # Sort by distance and return top k
        candidates_with_dist = [
            (node, np.linalg.norm(query - self.data[node]))
            for node in candidates
        ]
        candidates_with_dist.sort(key=lambda x: x[1])

        return candidates_with_dist[:k]

class LSHIndex:
    """
    Locality Sensitive Hashing index

    Key parameters:
    - nBands: Number of bands
    - nRows: Number of rows per band (hash functions)
    - More bands/rows = better precision, worse recall
    """

    def __init__(self, dim: int, nBands: int = 20, nRows: int = 5):
        """
        Initialize LSH index

        Args:
            dim: Vector dimension
            nBands: Number of bands
            nRows: Rows per band
        """
        self.dim = dim
        self.nBands = nBands
        self.nRows = nRows

        # Generate random projection vectors
        self.projections = np.random.randn(nBands, nRows, dim)
        self.offsets = np.random.rand(nBands, nRows) * 10

        # Buckets: band -> hash -> list of vector ids
        self.buckets = [defaultdict(list) for _ in range(nBands)]
        self.data = []

    def _hash(self, band: int, vector: np.ndarray) -> Tuple:
        """Compute hash for a band"""
        projections = self.projections[band]
        offsets = self.offsets[band]

        # Compute hash values
        hash_values = (np.dot(projections, vector) + offsets).astype(int)
        return tuple(hash_values)

    def add(self, vector: np.ndarray):
        """Add vector to index"""
        vector_id = len(self.data)
        self.data.append(vector)

        # Add to each band
        for band in range(self.nBands):
            hash_key = self._hash(band, vector)
            self.buckets[band][hash_key].append(vector_id)

    def search(self, query: np.ndarray, k: int = None) -> List[Tuple[int, float]]:
        """
        Search for nearest neighbors

        Args:
            query: Query vector
            k: Number of neighbors (ignored for LSH, returns all candidates)

        Returns:
            List of (vector_id, distance) tuples
        """
        candidates = set()

        # Query each band
        for band in range(self.nBands):
            hash_key = self._hash(band, query)
            candidates.update(self.buckets[band][hash_key])

        # Compute exact distances for candidates
        results = [
            (vector_id, np.linalg.norm(query - self.data[vector_id]))
            for vector_id in candidates
        ]
        results.sort(key=lambda x: x[1])

        return results

class BallTreeNode:
    """Node in Ball Tree"""

    def __init__(self, indices: List[int], center: np.ndarray, radius: float):
        self.indices = indices
        self.center = center
        self.radius = radius
        self.left = None
        self.right = None

class BallTreeIndex:
    """
    Ball Tree index

    Key parameters:
    - leafSize: Number of points per leaf
    """

    def __init__(self, leafSize: int = 40):
        """
        Initialize Ball Tree

        Args:
            leafSize: Maximum points per leaf node
        """
        self.leafSize = leafSize
        self.data = []
        self.root = None

    def add(self, vector: np.ndarray):
        """Add vector to index"""
        self.data.append(vector)

    def build(self):
        """Build the tree after all vectors added"""
        if not self.data:
            return

        indices = list(range(len(self.data)))
        self.root = self._build(indices)

    def _build(self, indices: List[int]) -> BallTreeNode:
        """Build subtree"""
        if len(indices) <= self.leafSize:
            # Leaf node
            vectors = np.array([self.data[i] for i in indices])
            center = np.mean(vectors, axis=0)
            radius = np.max([np.linalg.norm(v - center) for v in vectors])
            return BallTreeNode(indices, center, radius)

        # Find dimension with max variance
        vectors = np.array([self.data[i] for i in indices])
        variances = np.var(vectors, axis=0)
        split_dim = np.argmax(variances)

        # Split on median
        sorted_indices = sorted(indices, key=lambda i: self.data[i][split_dim])
        mid = len(sorted_indices) // 2

        left_indices = sorted_indices[:mid]
        right_indices = sorted_indices[mid:]

        # Build children
        left = self._build(left_indices)
        right = self._build(right_indices)

        # Compute bounding ball
        center = np.mean(vectors, axis=0)
        radius = np.max([np.linalg.norm(v - center) for v in vectors])

        node = BallTreeNode(indices, center, radius)
        node.left = left
        node.right = right

        return node

    def search(
        self,
        query: np.ndarray,
        k: int,
        node: BallTreeNode = None
    ) -> List[Tuple[int, float]]:
        """
        Search for k nearest neighbors

        Args:
            query: Query vector
            k: Number of neighbors
            node: Current node (internal use)

        Returns:
            List of (vector_id, distance) tuples
        """
        if node is None:
            node = self.root

        if node is None:
            return []

        # Leaf node - check all points
        if node.left is None and node.right is None:
            results = [
                (idx, np.linalg.norm(query - self.data[idx]))
                for idx in node.indices
            ]
            results.sort(key=lambda x: x[1])
            return results[:k]

        # Check which child to search
        dist_to_center = np.linalg.norm(query - node.center)

        results = []

        # Search nearer child first
        dist_to_left = np.linalg.norm(query - node.left.center) if node.left else float('inf')
        dist_to_right = np.linalg.norm(query - node.right.center) if node.right else float('inf')

        if dist_to_left < dist_to_right:
            results.extend(self.search(query, k, node.left))

            # Check if we need to search other child
            if len(results) < k or dist_to_right < max(r[1] for r in results):
                results.extend(self.search(query, k, node.right))
        else:
            results.extend(self.search(query, k, node.right))

            if len(results) < k or dist_to_left < max(r[1] for r in results):
                results.extend(self.search(query, k, node.left))

        # Sort and return top k
        results.sort(key=lambda x: x[1])
        return results[:k]

class IVFIndex:
    """
    Inverted File Index

    Key parameters:
    - nClusters: Number of clusters (Voronoi cells)
    - nProbe: Number of clusters to search
    """

    def __init__(self, dim: int, nClusters: int = 100, nProbe: int = 5):
        """
        Initialize IVF index

        Args:
            dim: Vector dimension
            nClusters: Number of clusters
            nProbe: Clusters to search
        """
        self.dim = dim
        self.nClusters = nClusters
        self.nProbe = nProbe

        # Cluster centers
        self.centroids = None

        # Inverted lists: cluster_id -> list of vector ids
        self.inverted_lists = defaultdict(list)
        self.data = []

    def train(self, vectors: np.ndarray):
        """Train clustering on data"""
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=self.nClusters, random_state=42)
        kmeans.fit(vectors)
        self.centroids = kmeans.cluster_centers_

    def add(self, vector: np.ndarray):
        """Add vector to index"""
        if self.centroids is None:
            raise ValueError("Must train index before adding vectors")

        vector_id = len(self.data)
        self.data.append(vector)

        # Find nearest centroid
        distances = np.array([
            np.linalg.norm(vector - centroid)
            for centroid in self.centroids
        ])
        nearest_cluster = np.argmin(distances)

        # Add to inverted list
        self.inverted_lists[nearest_cluster].append(vector_id)

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """
        Search for k nearest neighbors

        Args:
            query: Query vector
            k: Number of neighbors

        Returns:
            List of (vector_id, distance) tuples
        """
        if self.centroids is None:
            return []

        # Find nProbe nearest clusters
        distances = np.array([
            np.linalg.norm(query - centroid)
            for centroid in self.centroids
        ])
        nearest_clusters = np.argsort(distances)[:self.nProbe]

        # Search in those clusters
        candidates = []
        for cluster_id in nearest_clusters:
            candidates.extend(self.inverted_lists[cluster_id])

        # Compute exact distances
        results = [
            (vector_id, np.linalg.norm(query - self.data[vector_id]))
            for vector_id in candidates
        ]
        results.sort(key=lambda x: x[1])

        return results[:k]

def generate_kv_anchors(
    num_anchors: int = 10000,
    dim: int = 128
) -> np.ndarray:
    """
    Generate synthetic KV-anchor embeddings

    Args:
        num_anchors: Number of anchors
        dim: Embedding dimension

    Returns:
        Array of anchor vectors
    """
    # Generate with some structure
    np.random.seed(42)

    # Create clusters (conversation topics)
    num_clusters = 50
    anchors = []

    for i in range(num_anchors):
        cluster_id = i % num_clusters
        cluster_center = np.random.randn(dim) * 0.5

        # Add anchor with noise
        anchor = cluster_center + np.random.randn(dim) * 0.2
        anchors.append(anchor)

    return np.array(anchors, dtype=np.float32)

def run_ann_tuning() -> Dict[str, List[ANNResult]]:
    """
    Run ANN parameter tuning experiments

    Returns:
        Dictionary of results by algorithm
    """
    print("="*70)
    print("ANN INDEX PARAMETER TUNING")
    print("="*70)

    # Generate data
    print("\nGenerating synthetic KV-anchors...")
    num_anchors = 5000
    dim = 128
    anchors = generate_kv_anchors(num_anchors, dim)

    # Split into train/test
    train_anchors = anchors[:4000]
    test_anchors = anchors[4000:]

    results = defaultdict(list)

    # Test HNSW
    print("\n" + "="*70)
    print("Testing HNSW")
    print("="*70)

    for M in [8, 16, 24, 32]:
        for efConstruction in [100, 200, 400]:
            for efSearch in [20, 50, 100, 200]:
                print(f"\nM={M}, efConstruction={efConstruction}, efSearch={efSearch}")

                # Build index
                start = time.time()
                index = HNSWIndex(M=M, efConstruction=efConstruction)
                for anchor in train_anchors:
                    index.add(anchor)
                build_time = time.time() - start

                # Search
                start = time.time()
                total_recall = 0
                total_time = 0

                for query in test_anchors[:100]:  # Test on subset
                    # Get ANN results
                    start_q = time.time()
                    ann_results = index.search(query, k=10, efSearch=efSearch)
                    query_time = time.time() - start_q
                    total_time += query_time

                    # Get ground truth (brute force)
                    distances = np.array([
                        np.linalg.norm(query - train_anchor)
                        for train_anchor in train_anchors
                    ])
                    ground_truth = set(np.argsort(distances)[:10])

                    # Calculate recall
                    ann_ids = set([r[0] for r in ann_results])
                    recall = len(ann_ids & ground_truth) / 10
                    total_recall += recall

                avg_recall = total_recall / 100
                avg_query_time = (total_time / 100) * 1000  # Convert to ms

                # Estimate index size
                index_size = len(train_anchors) * dim * 4 * M  # Rough estimate

                result = ANNResult(
                    algorithm=ANNAlgorithm.HNSW,
                    parameters={
                        'M': M,
                        'efConstruction': efConstruction,
                        'efSearch': efSearch
                    },
                    recall=avg_recall,
                    query_time_ms=avg_query_time,
                    build_time_s=build_time,
                    index_size_bytes=index_size,
                    neighbors_per_query=10,
                    k=10
                )

                results['hnsw'].append(result)

                print(f"  Recall: {avg_recall:.3f}, Query Time: {avg_query_time:.2f}ms")

    # Test LSH
    print("\n" + "="*70)
    print("Testing LSH")
    print("="*70)

    for nBands in [10, 20, 30, 40]:
        for nRows in [3, 5, 7, 10]:
            print(f"\nnBands={nBands}, nRows={nRows}")

            # Build index
            start = time.time()
            index = LSHIndex(dim=dim, nBands=nBands, nRows=nRows)
            for anchor in train_anchors:
                index.add(anchor)
            build_time = time.time() - start

            # Search
            start = time.time()
            total_recall = 0
            total_time = 0

            for query in test_anchors[:100]:
                start_q = time.time()
                ann_results = index.search(query, k=10)
                query_time = time.time() - start_q
                total_time += query_time

                # Ground truth
                distances = np.array([
                    np.linalg.norm(query - train_anchor)
                    for train_anchor in train_anchors
                ])
                ground_truth = set(np.argsort(distances)[:10])

                ann_ids = set([r[0] for r in ann_results[:10]])
                recall = len(ann_ids & ground_truth) / 10
                total_recall += recall

            avg_recall = total_recall / 100
            avg_query_time = (total_time / 100) * 1000

            index_size = nBands * nRows * dim * 4  # Projection matrices

            result = ANNResult(
                algorithm=ANNAlgorithm.LSH,
                parameters={
                    'nBands': nBands,
                    'nRows': nRows
                },
                recall=avg_recall,
                query_time_ms=avg_query_time,
                build_time_s=build_time,
                index_size_bytes=index_size,
                neighbors_per_query=10,
                k=10
            )

            results['lsh'].append(result)

            print(f"  Recall: {avg_recall:.3f}, Query Time: {avg_query_time:.2f}ms")

    # Test Ball Tree
    print("\n" + "="*70)
    print("Testing Ball Tree")
    print("="*70)

    for leafSize in [20, 40, 80, 160]:
        print(f"\nleafSize={leafSize}")

        # Build index
        start = time.time()
        index = BallTreeIndex(leafSize=leafSize)
        for anchor in train_anchors:
            index.add(anchor)
        index.build()
        build_time = time.time() - start

        # Search
        total_recall = 0
        total_time = 0

        for query in test_anchors[:100]:
            start_q = time.time()
            ann_results = index.search(query, k=10)
            query_time = time.time() - start_q
            total_time += query_time

            # Ground truth
            distances = np.array([
                np.linalg.norm(query - train_anchor)
                for train_anchor in train_anchors
            ])
            ground_truth = set(np.argsort(distances)[:10])

            ann_ids = set([r[0] for r in ann_results])
            recall = len(ann_ids & ground_truth) / 10
            total_recall += recall

        avg_recall = total_recall / 100
        avg_query_time = (total_time / 100) * 1000

        index_size = len(train_anchors) * dim * 4  # All vectors stored

        result = ANNResult(
            algorithm=ANNAlgorithm.BALL_TREE,
            parameters={'leafSize': leafSize},
            recall=avg_recall,
            query_time_ms=avg_query_time,
            build_time_s=build_time,
            index_size_bytes=index_size,
            neighbors_per_query=10,
            k=10
        )

        results['ball_tree'].append(result)

        print(f"  Recall: {avg_recall:.3f}, Query Time: {avg_query_time:.2f}ms")

    # Test IVF
    print("\n" + "="*70)
    print("Testing IVF")
    print("="*70)

    for nClusters in [50, 100, 200]:
        for nProbe in [1, 5, 10]:
            print(f"\nnClusters={nClusters}, nProbe={nProbe}")

            # Train and build
            start = time.time()
            index = IVFIndex(dim=dim, nClusters=nClusters, nProbe=nProbe)
            index.train(train_anchors)
            for anchor in train_anchors:
                index.add(anchor)
            build_time = time.time() - start

            # Search
            total_recall = 0
            total_time = 0

            for query in test_anchors[:100]:
                start_q = time.time()
                ann_results = index.search(query, k=10)
                query_time = time.time() - start_q
                total_time += query_time

                # Ground truth
                distances = np.array([
                    np.linalg.norm(query - train_anchor)
                    for train_anchor in train_anchors
                ])
                ground_truth = set(np.argsort(distances)[:10])

                ann_ids = set([r[0] for r in ann_results])
                recall = len(ann_ids & ground_truth) / 10
                total_recall += recall

            avg_recall = total_recall / 100
            avg_query_time = (total_time / 100) * 1000

            index_size = nClusters * dim * 4 + len(train_anchors) * 4  # Centroids + ids

            result = ANNResult(
                algorithm=ANNAlgorithm.IVF,
                parameters={
                    'nClusters': nClusters,
                    'nProbe': nProbe
                },
                recall=avg_recall,
                query_time_ms=avg_query_time,
                build_time_s=build_time,
                index_size_bytes=index_size,
                neighbors_per_query=10,
                k=10
            )

            results['ivf'].append(result)

            print(f"  Recall: {avg_recall:.3f}, Query Time: {avg_query_time:.2f}ms")

    return results

def find_pareto_frontier(results: Dict[str, List[ANNResult]]) -> Dict[str, Any]:
    """
    Find Pareto-optimal configurations (best recall/time tradeoff)

    Args:
        results: Experiment results

    Returns:
        Pareto frontier configurations
    """
    print("\n" + "="*70)
    print("FINDING PARETO FRONTIER")
    print("="*70)

    pareto_by_algorithm = {}

    for algorithm, algorithm_results in results.items():
        # Sort by recall (ascending)
        sorted_results = sorted(algorithm_results, key=lambda r: r.recall)

        # Find Pareto frontier
        pareto = []
        min_query_time = float('inf')

        for result in reversed(sorted_results):
            if result.query_time_ms < min_query_time:
                pareto.append(result)
                min_query_time = result.query_time_ms

        # Keep only Pareto-optimal
        pareto_sorted = sorted(pareto, key=lambda r: r.recall, reverse=True)
        pareto_by_algorithm[algorithm] = pareto_sorted[:5]  # Top 5

        print(f"\n{algorithm.upper()} Pareto Frontier:")
        for i, r in enumerate(pareto_sorted[:5]):
            print(f"  {i+1}. Recall: {r.recall:.3f}, Time: {r.query_time_ms:.2f}ms")
            print(f"     Params: {r.parameters}")

    return pareto_by_algorithm

def main():
    """Main optimization loop"""
    import os
    os.makedirs('simulations/optimization/memory/results', exist_ok=True)

    # Run experiments
    results = run_ann_tuning()

    # Find Pareto frontier
    pareto = find_pareto_frontier(results)

    # Find overall best
    all_results = []
    for algorithm_results in results.values():
        all_results.extend(algorithm_results)

    # Sort by F1 score (harmonic mean of normalized recall and speed)
    max_recall = max(r.recall for r in all_results)
    min_time = min(r.query_time_ms for r in all_results)

    for r in all_results:
        norm_recall = r.recall / max_recall
        norm_speed = min_time / r.query_time_ms
        r.f1 = 2 * (norm_recall * norm_speed) / (norm_recall + norm_speed + 1e-8)

    best = max(all_results, key=lambda r: r.f1)

    print("\n" + "="*70)
    print("*** OVERALL OPTIMAL CONFIGURATION ***")
    print("="*70)
    print(f"Algorithm: {best.algorithm.value}")
    print(f"Parameters: {best.parameters}")
    print(f"Recall: {best.recall:.3f}")
    print(f"Query Time: {best.query_time_ms:.2f}ms")
    print(f"F1 Score: {best.f1:.3f}")

    # Save results
    output = {
        'results': {
            algorithm: [
                {
                    'algorithm': r.algorithm.value,
                    'parameters': r.parameters,
                    'recall': r.recall,
                    'query_time_ms': r.query_time_ms,
                    'build_time_s': r.build_time_s,
                    'index_size_bytes': r.index_size_bytes,
                    'f1_score': r.f1 if hasattr(r, 'f1') else None
                }
                for r in algorithm_results
            ]
            for algorithm, algorithm_results in results.items()
        },
        'pareto_frontier': {
            algorithm: [
                {
                    'algorithm': r.algorithm.value,
                    'parameters': r.parameters,
                    'recall': r.recall,
                    'query_time_ms': r.query_time_ms
                }
                for r in frontier
            ]
            for algorithm, frontier in pareto.items()
        },
        'optimal': {
            'algorithm': best.algorithm.value,
            'parameters': best.parameters,
            'recall': best.recall,
            'query_time_ms': best.query_time_ms,
            'f1_score': best.f1
        }
    }

    with open('simulations/optimization/memory/results/ann_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to: simulations/optimization/memory/results/ann_results.json")

    return {
        'algorithm': best.algorithm.value,
        'parameters': best.parameters
    }

if __name__ == '__main__':
    main()
