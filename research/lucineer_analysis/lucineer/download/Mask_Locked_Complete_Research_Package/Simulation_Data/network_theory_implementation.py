"""
Network-Theoretic Framework for Transformer Inference
======================================================

This module provides a complete implementation of flow network analysis
for transformer inference systems, including:
- Max-flow min-cut analysis for throughput optimization
- Queueing theory for latency modeling
- KV cache analysis as flow storage
- Parallelism speedup calculations
- Reliability analysis
- Scheduling optimization

Author: Network Theory Framework
"""

import numpy as np
from scipy.optimize import linprog, minimize, brentq
from scipy.special import comb
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
import warnings

# ============================================================================
# Data Structures
# ============================================================================

class ComputeRegime(Enum):
    COMPUTE_BOUND = "compute_bound"
    MEMORY_BOUND = "memory_bound"
    BALANCED = "balanced"


@dataclass
class LayerConfig:
    """Configuration for a transformer layer."""
    d_model: int
    d_ffn: int
    n_heads: int
    d_head: int
    seq_len: int = 512
    cache_len: int = 0
    dropout_prob: float = 0.0
    
    @property
    def attention_params(self) -> int:
        """Number of attention parameters."""
        # Q, K, V, O projections
        return 4 * self.d_model * self.d_model
    
    @property
    def ffn_params(self) -> int:
        """Number of FFN parameters."""
        # Up and down projections
        return 2 * self.d_model * self.d_ffn


@dataclass
class HardwareConfig:
    """Hardware configuration for inference."""
    flops: float  # Peak FLOPS
    hbm_bw: float  # HBM bandwidth GB/s
    pcie_bw: float  # PCIe/interconnect bandwidth GB/s
    memory: float  # Total memory GB
    dtype_bytes: int = 2  # FP16 = 2 bytes
    
    @property
    def arithmetic_intensity_threshold(self) -> float:
        """Threshold between compute-bound and memory-bound."""
        return self.flops / (self.hbm_bw * 1e9)


@dataclass
class FlowEdge:
    """Edge in the flow network."""
    source: str
    target: str
    capacity: float
    flow: float = 0.0
    
    @property
    def residual_capacity(self) -> float:
        return self.capacity - self.flow


@dataclass
class QueueState:
    """State of a queueing node."""
    arrival_rate: float
    service_rate: float
    queue_length: float = 0.0
    
    @property
    def utilization(self) -> float:
        return self.arrival_rate / self.service_rate
    
    @property
    def is_stable(self) -> bool:
        return self.utilization < 1.0
    
    @property
    def avg_wait_time(self) -> float:
        """Average wait time in M/M/1 queue."""
        if not self.is_stable:
            return float('inf')
        return self.utilization / (self.service_rate * (1 - self.utilization))
    
    @property
    def avg_system_time(self) -> float:
        """Average time in system (wait + service)."""
        if not self.is_stable:
            return float('inf')
        return 1 / (self.service_rate - self.arrival_rate)


# ============================================================================
# Flow Network Model
# ============================================================================

class TransformerFlowNetwork:
    """
    Flow network model for transformer inference.
    
    Models transformer layers as a directed acyclic graph with:
    - Vertices: attention and FFN processing nodes
    - Edges: data movement with capacity constraints
    - Flow: token throughput
    
    Key theorems:
    - Max-flow equals min-cut capacity
    - Bottleneck layers are identified by min-cut
    """
    
    def __init__(self, layers: List[LayerConfig], hw: HardwareConfig):
        self.layers = layers
        self.hw = hw
        self.n_layers = len(layers)
        self._build_network()
    
    def _build_network(self):
        """Build the flow network graph."""
        self.edges: Dict[str, FlowEdge] = {}
        self.nodes: List[str] = ['source', 'sink']
        
        for i in range(self.n_layers):
            attn_node = f'layer_{i}_attn'
            ffn_node = f'layer_{i}_ffn'
            self.nodes.extend([attn_node, ffn_node])
            
            # Edge from source/input to first attention
            if i == 0:
                self.edges[f'source->{attn_node}'] = FlowEdge(
                    'source', attn_node, 
                    self._compute_edge_capacity(i, 'input')
                )
            
            # Edge from attention to FFN
            self.edges[f'{attn_node}->{ffn_node}'] = FlowEdge(
                attn_node, ffn_node,
                self._compute_edge_capacity(i, 'attn')
            )
            
            # Edge from FFN to next layer or sink
            if i < self.n_layers - 1:
                next_attn = f'layer_{i+1}_attn'
                self.edges[f'{ffn_node}->{next_attn}'] = FlowEdge(
                    ffn_node, next_attn,
                    self._compute_edge_capacity(i, 'ffn_to_attn')
                )
            else:
                self.edges[f'{ffn_node}->sink'] = FlowEdge(
                    ffn_node, 'sink',
                    self._compute_edge_capacity(i, 'output')
                )
    
    def _attention_flops(self, layer: LayerConfig) -> float:
        """Compute FLOPs per token for attention."""
        # Q·K^T: n_heads * seq_len * d_head * (seq_len + cache_len)
        # Softmax: negligible
        # Attn·V: n_heads * (seq_len + cache_len) * d_head
        # Per token: we're computing for one position
        total_seq = layer.seq_len + layer.cache_len
        
        # Q projection: d_model -> n_heads * d_head
        q_proj = layer.d_model * layer.n_heads * layer.d_head
        
        # K, V projections for current token
        kv_proj = 2 * layer.d_model * layer.n_heads * layer.d_head
        
        # Attention computation: Q·K^T for one query position
        attn_score = layer.n_heads * layer.d_head * total_seq
        
        # Attention output: attn·V
        attn_output = layer.n_heads * total_seq * layer.d_head
        
        # Output projection
        out_proj = layer.n_heads * layer.d_head * layer.d_model
        
        return 2 * (q_proj + kv_proj + attn_score + attn_output + out_proj)
    
    def _ffn_flops(self, layer: LayerConfig) -> float:
        """Compute FLOPs per token for FFN."""
        # Up projection: d_model -> d_ffn
        # Down projection: d_ffn -> d_model
        # Activation (GELU): negligible
        return 2 * (layer.d_model * layer.d_ffn + layer.d_ffn * layer.d_model)
    
    def _attention_memory_bytes(self, layer: LayerConfig) -> float:
        """Compute memory bytes transferred for attention."""
        # Weight reads
        weight_bytes = layer.attention_params * self.hw.dtype_bytes
        
        # KV cache reads (for each of K and V)
        cache_bytes = 2 * layer.n_heads * layer.d_head * layer.cache_len * self.hw.dtype_bytes
        
        # Activation memory (input, output)
        activation_bytes = 2 * layer.d_model * self.hw.dtype_bytes
        
        return weight_bytes + cache_bytes + activation_bytes
    
    def _ffn_memory_bytes(self, layer: LayerConfig) -> float:
        """Compute memory bytes transferred for FFN."""
        # Weight reads
        weight_bytes = layer.ffn_params * self.hw.dtype_bytes
        
        # Activation memory
        activation_bytes = (layer.d_model + layer.d_ffn) * self.hw.dtype_bytes
        
        return weight_bytes + activation_bytes
    
    def _compute_edge_capacity(self, layer_idx: int, edge_type: str) -> float:
        """Compute edge capacity (tokens/sec)."""
        layer = self.layers[layer_idx]
        
        if edge_type == 'input':
            # Embedding layer capacity
            mem_bytes = layer.d_model * self.hw.dtype_bytes
            return self.hw.hbm_bw * 1e9 / mem_bytes
        
        elif edge_type == 'attn':
            # Attention capacity
            compute_cap = self.hw.flops / self._attention_flops(layer)
            memory_cap = self.hw.hbm_bw * 1e9 / self._attention_memory_bytes(layer)
            return min(compute_cap, memory_cap)
        
        elif edge_type == 'ffn_to_attn':
            # FFN capacity (transition to next attention)
            compute_cap = self.hw.flops / self._ffn_flops(layer)
            memory_cap = self.hw.hbm_bw * 1e9 / self._ffn_memory_bytes(layer)
            return min(compute_cap, memory_cap)
        
        elif edge_type == 'output':
            # Output layer capacity
            mem_bytes = layer.d_model * self.hw.dtype_bytes
            return self.hw.hbm_bw * 1e9 / mem_bytes
        
        return float('inf')
    
    def compute_regime(self, layer_idx: int, op: str) -> ComputeRegime:
        """Determine if layer operation is compute or memory bound."""
        layer = self.layers[layer_idx]
        
        if op == 'attn':
            flops = self._attention_flops(layer)
            bytes_accessed = self._attention_memory_bytes(layer)
        else:
            flops = self._ffn_flops(layer)
            bytes_accessed = self._ffn_memory_bytes(layer)
        
        arithmetic_intensity = flops / bytes_accessed
        threshold = self.hw.arithmetic_intensity_threshold
        
        if arithmetic_intensity > 1.1 * threshold:
            return ComputeRegime.COMPUTE_BOUND
        elif arithmetic_intensity < 0.9 * threshold:
            return ComputeRegime.MEMORY_BOUND
        else:
            return ComputeRegime.BALANCED
    
    def max_flow_min_cut(self) -> Tuple[float, List[FlowEdge]]:
        """
        Compute maximum flow and identify min-cut edges.
        
        Returns:
            Tuple of (max_throughput, bottleneck_edges)
        """
        # For a DAG representing a pipeline, max flow equals min edge capacity
        # The min-cut is the set of edges with minimum capacity
        
        min_capacity = float('inf')
        min_cut_edges = []
        
        for edge in self.edges.values():
            if edge.capacity < min_capacity:
                min_capacity = edge.capacity
                min_cut_edges = [edge]
            elif np.isclose(edge.capacity, min_capacity):
                min_cut_edges.append(edge)
        
        return min_capacity, min_cut_edges
    
    def throughput_at_latency(self, target_latency: float) -> float:
        """
        Compute achievable throughput given latency constraint.
        
        Uses queueing theory to model the relationship between
        throughput and latency.
        """
        max_throughput, _ = self.max_flow_min_cut()
        
        # Binary search for throughput that achieves target latency
        if self.latency(0) > target_latency:
            warnings.warn("Target latency below minimum possible")
            return 0.0
        
        def latency_exceeds(throughput):
            return self.latency(throughput) - target_latency
        
        try:
            result = brentq(latency_exceeds, 0, max_throughput * 0.999)
            return result
        except ValueError:
            return max_throughput
    
    def latency(self, throughput: float) -> float:
        """
        Compute end-to-end latency using queueing model.
        
        Each layer is modeled as an M/M/1 queue.
        """
        total_latency = 0.0
        
        for i, layer in enumerate(self.layers):
            # Attention queue
            attn_capacity = self._compute_edge_capacity(i, 'attn')
            if throughput >= attn_capacity:
                return float('inf')
            
            # M/M/1 system time
            attn_time = 1.0 / (attn_capacity - throughput)
            total_latency += attn_time
            
            # FFN queue
            ffn_capacity = self._compute_edge_capacity(i, 'ffn_to_attn')
            if throughput >= ffn_capacity:
                return float('inf')
            
            ffn_time = 1.0 / (ffn_capacity - throughput)
            total_latency += ffn_time
        
        return total_latency
    
    def optimal_batch_size(self, max_memory: float) -> int:
        """
        Compute optimal batch size given memory constraint.
        
        Uses memory model to find largest batch that fits.
        """
        # Memory per token per layer
        mem_per_token = 0
        for layer in self.layers:
            mem_per_token += self._attention_memory_bytes(layer)
            mem_per_token += self._ffn_memory_bytes(layer)
        
        # Parameter memory (shared across batch)
        param_memory = sum(
            layer.attention_params + layer.ffn_params 
            for layer in self.layers
        ) * self.hw.dtype_bytes
        
        # Activation memory scales with batch size
        available_for_batch = (max_memory * 1e9) - param_memory
        
        return max(1, int(available_for_batch / mem_per_token))


# ============================================================================
# KV Cache Analysis
# ============================================================================

class KVCacheFlowModel:
    """
    KV Cache analysis using flow storage model.
    
    Models the cache as a reservoir with:
    - Inflow: tokens being generated
    - Outflow: tokens being evicted (if applicable)
    - Storage: current cache contents
    """
    
    def __init__(
        self, 
        cache_capacity: int, 
        n_layers: int,
        d_model: int,
        eviction_policy: str = 'lru'
    ):
        self.capacity = cache_capacity
        self.n_layers = n_layers
        self.d_model = d_model
        self.eviction_policy = eviction_policy
        
        # Per-layer cache
        self.per_layer_capacity = cache_capacity // n_layers
    
    def cache_size_bytes(self, n_tokens: int) -> int:
        """Compute cache size for n tokens."""
        # K and V for each layer
        return 2 * self.n_layers * n_tokens * self.d_model * 2  # FP16
    
    def working_set_model(
        self, 
        sequence_length: int,
        locality_param: float = 0.8
    ) -> Dict[str, float]:
        """
        Model working set and cache performance.
        
        Args:
            sequence_length: Total sequence length
            locality_param: Zipf parameter for access pattern
        
        Returns:
            Dictionary with cache metrics
        """
        # Working set is the sequence length for autoregressive
        working_set = sequence_length
        
        # Hit rate using LRU model with locality
        if working_set <= self.capacity:
            hit_rate = 1.0
        else:
            # Probability of cache hit decreases with working set size
            hit_rate = 1.0 - (working_set / self.capacity) ** locality_param
        
        # Miss rate
        miss_rate = 1.0 - hit_rate
        
        # Effective throughput considering cache
        # On miss, need to recompute KV (expensive)
        miss_penalty = 10.0  # Relative cost of miss vs hit
        
        return {
            'working_set': working_set,
            'hit_rate': hit_rate,
            'miss_rate': miss_rate,
            'effective_speedup': 1.0 / (hit_rate + miss_rate * miss_penalty),
            'cache_pressure': working_set / self.capacity
        }
    
    def streaming_cache_dynamics(
        self,
        generation_rate: float,
        eviction_rate: float = 0.0,
        initial_cache: int = 0
    ) -> Callable[[float], float]:
        """
        Model streaming cache dynamics.
        
        Returns function that gives cache size at time t.
        """
        def cache_size(t: float) -> float:
            # Differential equation: dS/dt = gen_rate - evict_rate
            # Solution: S(t) = S(0) + (gen - evict) * t
            # But capped at capacity
            size = initial_cache + (generation_rate - eviction_rate) * t
            return min(size, self.capacity)
        
        return cache_size
    
    def optimal_cache_allocation(
        self,
        layer_importance: List[float]
    ) -> List[int]:
        """
        Optimal cache allocation across layers.
        
        Args:
            layer_importance: Importance weight for each layer
        
        Returns:
            Cache allocation per layer
        """
        # Allocate proportionally to importance
        total_importance = sum(layer_importance)
        
        if total_importance == 0:
            return [self.capacity // self.n_layers] * self.n_layers
        
        allocation = [
            int(self.capacity * imp / total_importance)
            for imp in layer_importance
        ]
        
        # Ensure at least 1 token per layer
        allocation = [max(1, a) for a in allocation]
        
        # Adjust for total capacity
        diff = sum(allocation) - self.capacity
        if diff > 0:
            # Reduce from largest allocations
            for i in np.argsort(allocation)[::-1][:diff]:
                allocation[i] -= 1
        
        return allocation


# ============================================================================
# Parallelism Analysis
# ============================================================================

class ParallelismModel:
    """
    Parallelism analysis using network theory.
    
    Models:
    - Pipeline parallelism
    - Data parallelism
    - Tensor parallelism
    """
    
    def __init__(
        self,
        n_layers: int,
        layer_time: float,
        param_size: float,  # GB
        activation_size: float,  # GB per token
        interconnect_bw: float  # GB/s
    ):
        self.n_layers = n_layers
        self.layer_time = layer_time
        self.param_size = param_size
        self.activation_size = activation_size
        self.interconnect_bw = interconnect_bw
    
    def pipeline_speedup(
        self, 
        n_stages: int, 
        n_microbatches: int
    ) -> float:
        """
        Compute pipeline parallelism speedup.
        
        Uses bubble analysis to account for pipeline inefficiency.
        """
        # Ideal speedup
        ideal_speedup = n_stages
        
        # Pipeline bubble fraction
        bubble_fraction = (n_stages - 1) / (n_stages + n_microbatches - 1)
        
        # Effective speedup
        effective_speedup = ideal_speedup * (1 - bubble_fraction)
        
        return effective_speedup
    
    def pipeline_optimal_microbatches(self, n_stages: int) -> int:
        """
        Compute optimal number of microbatches for pipeline.
        
        Balances bubble overhead against scheduling complexity.
        """
        # Optimal m ≈ 4 * p for good efficiency
        return 4 * n_stages
    
    def data_parallel_speedup(
        self,
        n_workers: int,
        communication_coefficient: float = 0.01
    ) -> float:
        """
        Compute data parallelism speedup.
        
        Uses extended Amdahl's law with communication overhead.
        """
        # Communication overhead scales logarithmically (tree all-reduce)
        # or linearly (ring all-reduce)
        
        # Time for all-reduce (ring)
        allreduce_time = self.param_size / self.interconnect_bw * 2 * (n_workers - 1) / n_workers
        
        # Time per step
        step_time = self.n_layers * self.layer_time
        
        # Communication fraction
        comm_fraction = allreduce_time / (step_time + allreduce_time)
        
        # Speedup with communication
        speedup = n_workers / (1 + comm_fraction * (n_workers - 1))
        
        return speedup
    
    def tensor_parallel_speedup(
        self,
        n_workers: int,
        communication_coefficient: float = 0.1
    ) -> float:
        """
        Compute tensor parallelism speedup.
        
        Models communication within attention and FFN layers.
        """
        # Tensor parallelism has more communication than data parallelism
        # Communication within each layer
        
        # Ideal speedup
        ideal = n_workers
        
        # Communication overhead per layer
        # All-reduce after attention and FFN
        comm_per_layer = 2 * self.activation_size / self.interconnect_bw
        
        # Compute time per layer
        compute_per_layer = self.layer_time
        
        # Communication fraction
        comm_fraction = comm_per_layer / (compute_per_layer + comm_per_layer)
        
        # Speedup
        speedup = n_workers / (1 + communication_coefficient * (n_workers - 1))
        
        return speedup
    
    def optimal_parallelism(
        self,
        max_workers: int,
        parallel_type: str = 'hybrid'
    ) -> Dict[str, int]:
        """
        Find optimal parallelism configuration.
        
        Returns:
            Dictionary with pipeline_stages, data_parallel_workers, tensor_parallel_workers
        """
        best_speedup = 0
        best_config = {'pipeline_stages': 1, 'data_parallel': 1, 'tensor_parallel': 1}
        
        for pp in range(1, max_workers + 1):
            for dp in range(1, max_workers // pp + 1):
                for tp in range(1, max_workers // (pp * dp) + 1):
                    total = pp * dp * tp
                    if total > max_workers:
                        continue
                    
                    # Combined speedup
                    pp_speedup = self.pipeline_speedup(pp, 4 * pp)
                    dp_speedup = self.data_parallel_speedup(dp)
                    tp_speedup = self.tensor_parallel_speedup(tp)
                    
                    combined = pp_speedup * dp_speedup * tp_speedup
                    
                    if combined > best_speedup:
                        best_speedup = combined
                        best_config = {
                            'pipeline_stages': pp,
                            'data_parallel': dp,
                            'tensor_parallel': tp
                        }
        
        best_config['speedup'] = best_speedup
        return best_config


# ============================================================================
# Reliability Analysis
# ============================================================================

class ReliabilityModel:
    """
    Reliability analysis for inference systems.
    
    Models:
    - Component failures
    - System availability
    - Graceful degradation
    """
    
    def __init__(
        self,
        n_components: int,
        failure_rate: float,  # failures per hour
        repair_rate: float = 1.0,  # repairs per hour
        redundancy_config: Optional[Dict[int, int]] = None
    ):
        self.n_components = n_components
        self.failure_rate = failure_rate
        self.repair_rate = repair_rate
        self.redundancy = redundancy_config or {}
    
    def component_reliability(self, t: float) -> float:
        """Reliability of single component at time t."""
        return np.exp(-self.failure_rate * t)
    
    def system_reliability(self, t: float) -> float:
        """System reliability (series of components)."""
        R = 1.0
        for i in range(self.n_components):
            if i in self.redundancy:
                # N-modular redundancy
                n = self.redundancy[i]
                R_i = self.component_reliability(t)
                # Majority voting reliability
                R = R * self._nmr_reliability(R_i, n)
            else:
                R = R * self.component_reliability(t)
        return R
    
    def _nmr_reliability(self, R: float, n: int) -> float:
        """N-modular redundancy reliability (majority voting)."""
        majority = (n + 1) // 2
        reliability = 0.0
        for k in range(majority, n + 1):
            reliability += comb(n, k, exact=True) * (R ** k) * ((1 - R) ** (n - k))
        return reliability
    
    def mtbf(self) -> float:
        """Mean time between failures."""
        effective_failure_rate = self.n_components * self.failure_rate
        return 1.0 / effective_failure_rate
    
    def availability(self) -> float:
        """System availability."""
        mtbf = self.mtbf()
        mttr = 1.0 / self.repair_rate
        return mtbf / (mtbf + mttr)
    
    def graceful_degradation_capacity(
        self,
        n_failed: int,
        original_capacity: float
    ) -> float:
        """
        Compute remaining capacity with failed components.
        
        Assumes uniform component contribution.
        """
        operational = self.n_components - n_failed
        return original_capacity * (operational / self.n_components)
    
    def optimal_redundancy(
        self,
        target_reliability: float,
        time_horizon: float,
        max_redundancy: int = 5
    ) -> Dict[int, int]:
        """
        Find optimal redundancy allocation for critical components.
        
        Returns mapping of component_index -> redundancy_level
        """
        redundancy_allocation = {}
        
        for i in range(self.n_components):
            R = self.component_reliability(time_horizon)
            
            if R >= target_reliability:
                redundancy_allocation[i] = 1
                continue
            
            # Find minimum redundancy to meet target
            for n in range(2, max_redundancy + 1):
                R_nmr = self._nmr_reliability(R, n)
                if R_nmr >= target_reliability:
                    redundancy_allocation[i] = n
                    break
            else:
                redundancy_allocation[i] = max_redundancy
        
        return redundancy_allocation


# ============================================================================
# Scheduling Theory
# ============================================================================

class SchedulingOptimizer:
    """
    Optimal scheduling for layer execution.
    
    Implements:
    - Johnson's rule for two-machine flow shop
    - Latency minimization
    - Throughput optimization
    """
    
    def __init__(
        self,
        n_layers: int,
        attention_time: float,  # seconds per token
        ffn_time: float,  # seconds per token
        batch_size: int = 1
    ):
        self.n_layers = n_layers
        self.attn_time = attention_time
        self.ffn_time = ffn_time
        self.batch_size = batch_size
    
    def johnson_sequence(self) -> List[int]:
        """
        Johnson's rule for two-machine flow shop.
        
        Returns optimal sequence for minimizing makespan.
        """
        # Create list of (attn_time, ffn_time) for each layer
        jobs = [(i, self.attn_time, self.ffn_time) for i in range(self.n_layers)]
        
        front = []
        back = []
        
        while jobs:
            # Find job with minimum processing time
            min_job = min(jobs, key=lambda x: min(x[1], x[2]))
            jobs.remove(min_job)
            
            idx, attn, ffn = min_job
            
            if attn <= ffn:
                front.append(idx)
            else:
                back.append(idx)
        
        return front + back[::-1]
    
    def makespan(self, sequence: List[int]) -> float:
        """Compute makespan for given sequence."""
        attn_complete = 0.0
        ffn_complete = 0.0
        
        for idx in sequence:
            attn_complete += self.attn_time
            ffn_complete = max(ffn_complete, attn_complete) + self.ffn_time
        
        return ffn_complete
    
    def optimal_makespan(self) -> float:
        """Compute optimal makespan using Johnson's sequence."""
        seq = self.johnson_sequence()
        return self.makespan(seq)
    
    def latency_components(self) -> Dict[str, float]:
        """
        Compute latency components for inference.
        
        Returns TTFT and ITL estimates.
        """
        # Time to first token (prefill)
        # Assumes parallel processing of prompt
        prefill_time = self.n_layers * (self.attn_time + self.ffn_time)
        
        # Inter-token latency (decode)
        decode_time = self.n_layers * (self.attn_time + self.ffn_time)
        
        return {
            'ttft': prefill_time,
            'itl': decode_time,
            'total_for_n_tokens': lambda n: prefill_time + n * decode_time
        }
    
    def batch_latency_model(self, batch_size: int) -> Dict[str, float]:
        """
        Latency model with batching.
        
        Models how latency scales with batch size.
        """
        # Attention time scales with batch (parallel processing)
        # but KV cache access may cause slowdown
        
        # Memory-bound scaling
        memory_factor = 1 + 0.1 * np.log(batch_size)
        
        # Compute-bound scaling (near-linear)
        compute_factor = batch_size
        
        # Effective scaling depends on which regime we're in
        # Assume memory-bound for now
        scaled_attn = self.attn_time * memory_factor
        scaled_ffn = self.ffn_time * memory_factor
        
        return {
            'per_token_latency': self.n_layers * (scaled_attn + scaled_ffn),
            'throughput': batch_size / (self.n_layers * (scaled_attn + scaled_ffn)),
            'batch_size': batch_size
        }


# ============================================================================
# Integrated Network Model
# ============================================================================

class IntegratedNetworkModel:
    """
    Integrated model combining all network theory components.
    """
    
    def __init__(
        self,
        layers: List[LayerConfig],
        hw: HardwareConfig,
        cache_capacity: int,
        failure_rate: float = 1e-6
    ):
        self.flow_model = TransformerFlowNetwork(layers, hw)
        self.cache_model = KVCacheFlowModel(
            cache_capacity, len(layers), layers[0].d_model
        )
        self.reliability_model = ReliabilityModel(
            len(layers) * 2,  # attention + FFN per layer
            failure_rate
        )
        
        # Scheduling model
        max_throughput, _ = self.flow_model.max_flow_min_cut()
        attn_time = 1.0 / (max_throughput * 2)
        ffn_time = 1.0 / (max_throughput * 2)
        self.scheduling_model = SchedulingOptimizer(
            len(layers), attn_time, ffn_time
        )
    
    def analyze(self, target_latency: float = None) -> Dict:
        """
        Comprehensive analysis of the inference system.
        """
        max_throughput, bottlenecks = self.flow_model.max_flow_min_cut()
        
        if target_latency:
            achievable_throughput = self.flow_model.throughput_at_latency(target_latency)
        else:
            achievable_throughput = max_throughput
        
        latency = self.flow_model.latency(achievable_throughput)
        
        cache_metrics = self.cache_model.working_set_model(
            self.flow_model.layers[0].seq_len + 100  # Assume some generation
        )
        
        reliability = self.reliability_model.system_reliability(3600)  # 1 hour
        mtbf = self.reliability_model.mtbf()
        availability = self.reliability_model.availability()
        
        optimal_seq = self.scheduling_model.johnson_sequence()
        makespan = self.scheduling_model.optimal_makespan()
        
        return {
            'throughput': {
                'max': max_throughput,
                'achievable': achievable_throughput,
                'unit': 'tokens/sec'
            },
            'latency': {
                'end_to_end': latency,
                'unit': 'seconds'
            },
            'bottlenecks': [
                {'edge': f"{e.source}->{e.target}", 'capacity': e.capacity}
                for e in bottlenecks
            ],
            'cache': cache_metrics,
            'reliability': {
                'system_reliability_1hr': reliability,
                'mtbf_hours': mtbf,
                'availability': availability
            },
            'scheduling': {
                'optimal_sequence': optimal_seq,
                'optimal_makespan': makespan
            }
        }


# ============================================================================
# Example Usage
# ============================================================================

def create_gpt2_model():
    """Create a GPT-2 like model configuration."""
    # GPT-2 small: 12 layers, 768 hidden, 12 heads
    layers = [LayerConfig(
        d_model=768,
        d_ffn=3072,  # 4x hidden
        n_heads=12,
        d_head=64,
        seq_len=1024,
        cache_len=2048
    ) for _ in range(12)]
    
    return layers


def create_a100_hardware():
    """Create A100-like hardware configuration."""
    return HardwareConfig(
        flops=312e12,  # 312 TFLOPS (tensor cores)
        hbm_bw=2039,   # 2 TB/s HBM2e
        pcie_bw=64,    # 64 GB/s PCIe 4.0
        memory=80,     # 80 GB
        dtype_bytes=2  # FP16
    )


def main():
    """Demonstrate the network theory framework."""
    print("=" * 60)
    print("Network-Theoretic Framework for Transformer Inference")
    print("=" * 60)
    
    # Create model
    layers = create_gpt2_model()
    hw = create_a100_hardware()
    
    # Build integrated model
    model = IntegratedNetworkModel(
        layers=layers,
        hw=hw,
        cache_capacity=100000,  # 100k tokens
        failure_rate=1e-6
    )
    
    # Run analysis
    results = model.analyze(target_latency=0.1)
    
    print("\n1. THROUGHPUT ANALYSIS")
    print("-" * 40)
    print(f"Maximum throughput: {results['throughput']['max']:.2f} tokens/sec")
    print(f"Achievable throughput (100ms target): {results['throughput']['achievable']:.2f} tokens/sec")
    
    print("\n2. BOTTLENECK IDENTIFICATION (Min-Cut)")
    print("-" * 40)
    for b in results['bottlenecks']:
        print(f"Edge: {b['edge']}, Capacity: {b['capacity']:.2f} tokens/sec")
    
    print("\n3. LATENCY ANALYSIS")
    print("-" * 40)
    print(f"End-to-end latency: {results['latency']['end_to_end']*1000:.2f} ms")
    
    print("\n4. CACHE ANALYSIS")
    print("-" * 40)
    for k, v in results['cache'].items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    
    print("\n5. RELIABILITY ANALYSIS")
    print("-" * 40)
    print(f"System reliability (1 hour): {results['reliability']['system_reliability_1hr']:.6f}")
    print(f"MTBF: {results['reliability']['mtbf_hours']:.2f} hours")
    print(f"Availability: {results['reliability']['availability']:.6f}")
    
    print("\n6. SCHEDULING OPTIMIZATION")
    print("-" * 40)
    print(f"Optimal sequence (Johnson's rule): {results['scheduling']['optimal_sequence']}")
    print(f"Optimal makespan: {results['scheduling']['optimal_makespan']*1000:.2f} ms")
    
    # Parallelism analysis
    print("\n7. PARALLELISM ANALYSIS")
    print("-" * 40)
    parallel = ParallelismModel(
        n_layers=12,
        layer_time=0.001,
        param_size=0.5,  # 500 MB
        activation_size=0.001,  # 1 MB per token
        interconnect_bw=64  # GB/s
    )
    
    for n in [2, 4, 8]:
        speedup = parallel.pipeline_speedup(n, 4*n)
        print(f"Pipeline parallelism (p={n}): {speedup:.2f}x speedup")
    
    for n in [2, 4, 8]:
        speedup = parallel.data_parallel_speedup(n)
        print(f"Data parallelism (d={n}): {speedup:.2f}x speedup")
    
    optimal = parallel.optimal_parallelism(8)
    print(f"\nOptimal configuration for 8 workers:")
    print(f"  Pipeline stages: {optimal['pipeline_stages']}")
    print(f"  Data parallel: {optimal['data_parallel']}")
    print(f"  Tensor parallel: {optimal['tensor_parallel']}")
    print(f"  Combined speedup: {optimal['speedup']:.2f}x")


if __name__ == "__main__":
    main()
