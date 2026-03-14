#!/usr/bin/env python3
"""
Cycle 19: Multi-Chip Scaling Architecture Simulation
=====================================================

This simulation analyzes multi-chip scaling architecture for mask-locked inference chips,
including inter-chip communication, scaling topologies, parallelism strategies,
performance scaling efficiency, and cost-performance tradeoffs.

Key Parameters:
- Single chip: 2.4B weights, 25 tok/s
- Target scaling: 10B, 70B, 175B parameter models
- Inter-chip bandwidth: 10-100 Gbps per link

Author: Multi-Chip Scaling Research Agent
Date: Cycle 19
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Literal
from enum import Enum
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Single chip baseline parameters
SINGLE_CHIP_WEIGHTS = 2.4e9  # 2.4B parameters
SINGLE_CHIP_THROUGHPUT = 25  # tokens/second
SINGLE_CHIP_POWER = 5.0  # Watts
SINGLE_CHIP_MEMORY_BW = 31.74e12  # 31.74 TB/s internal
SINGLE_CHIP_DIE_SIZE = 42  # mm²
SINGLE_CHIP_COST = 35  # USD (target)

# Target model sizes
MODEL_SIZES = {
    '10B': 10e9,
    '70B': 70e9,
    '175B': 175e9,
    '540B': 540e9,
    '1T': 1e12
}

# Interconnect technologies
INTERCONNECT_TECH = {
    'SERDES_10G': {'bandwidth': 10e9, 'latency_ns': 50, 'pins': 4, 'power_mW': 150},
    'SERDES_25G': {'bandwidth': 25e9, 'latency_ns': 30, 'pins': 4, 'power_mW': 250},
    'SERDES_56G': {'bandwidth': 56e9, 'latency_ns': 20, 'pins': 4, 'power_mW': 400},
    'LVDS_1G': {'bandwidth': 1e9, 'latency_ns': 5, 'pins': 2, 'power_mW': 50},
    'LVDS_5G': {'bandwidth': 5e9, 'latency_ns': 8, 'pins': 2, 'power_mW': 100},
    'PARALLEL_32BIT': {'bandwidth': 32e9, 'latency_ns': 2, 'pins': 64, 'power_mW': 200},
}

# GPU comparison data
GPU_DATA = {
    'H100': {
        'memory': 80e9,  # 80GB HBM3
        'memory_bw': 3.35e12,  # 3.35 TB/s
        'tflops': 989,  # FP8 TFLOPS
        'power': 700,
        'cost': 30000,
        'throughput_70b': 30  # tokens/s (approximate)
    },
    'A100': {
        'memory': 80e9,
        'memory_bw': 2.0e12,
        'tflops': 312,
        'power': 400,
        'cost': 15000,
        'throughput_70b': 15
    },
    'H200': {
        'memory': 141e9,
        'memory_bw': 4.8e12,
        'tflops': 989,
        'power': 700,
        'cost': 40000,
        'throughput_70b': 40
    }
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TopologyType(Enum):
    LINEAR_CHAIN = "linear_chain"
    RING = "ring"
    GRID_2x2 = "grid_2x2"
    GRID_4x4 = "grid_4x4"
    TORUS = "torus"
    TREE = "tree"
    FULLY_CONNECTED = "fully_connected"

class ParallelismType(Enum):
    LAYER_WISE = "layer_wise"  # Pipeline parallelism
    TENSOR = "tensor"  # Split attention heads
    EXPERT = "expert"  # MoE expert parallelism
    DATA = "data"  # Batch parallelism

@dataclass
class InterconnectSpec:
    """Specification for inter-chip interconnect."""
    name: str
    bandwidth_gbps: float
    latency_ns: float
    pins_per_link: int
    power_mw_per_link: float
    max_distance_mm: float = 100.0
    
    @property
    def bandwidth_bytes_per_sec(self) -> float:
        return self.bandwidth_gbps * 1e9 / 8

@dataclass
class ChipConfig:
    """Configuration for a single chip instance."""
    weights: float
    throughput_tps: float
    power_w: float
    memory_bw_bytes: float
    die_size_mm2: float
    cost_usd: float
    io_links: int = 4
    io_bandwidth_per_link_gbps: float = 25.0

@dataclass
class TopologyConfig:
    """Configuration for a multi-chip topology."""
    topology_type: TopologyType
    num_chips: int
    interconnect: InterconnectSpec
    links_per_chip: int
    
    @property
    def total_bandwidth_gbps(self) -> float:
        return self.links_per_chip * self.interconnect.bandwidth_gbps

@dataclass
class ParallelismConfig:
    """Configuration for parallelism strategy."""
    strategy: ParallelismType
    num_chips: int
    model_size: float
    communication_ratio: float  # Fraction of computation requiring communication
    
@dataclass
class ScalingResult:
    """Results from scaling simulation."""
    num_chips: int
    model_size: float
    topology: TopologyType
    parallelism: ParallelismType
    ideal_speedup: float
    actual_speedup: float
    efficiency: float
    throughput_tps: float
    latency_ms: float
    communication_overhead: float
    total_power_w: float
    total_cost_usd: float
    cost_per_token: float

@dataclass
class AmdahlAnalysis:
    """Amdahl's Law analysis results."""
    parallel_fraction: float
    serial_fraction: float
    max_speedup: float
    efficiency_at_n: Dict[int, float]

# ============================================================================
# INTER-CHIP COMMUNICATION MODEL
# ============================================================================

class InterChipCommunication:
    """Models inter-chip communication characteristics."""
    
    def __init__(self, interconnect: InterconnectSpec):
        self.interconnect = interconnect
        
    def calculate_latency(self, message_size_bytes: float, hops: int = 1) -> float:
        """Calculate total latency for message transfer."""
        # Latency = serialization + propagation + routing
        serialization = message_size_bytes / self.interconnect.bandwidth_bytes_per_sec
        propagation = self.interconnect.latency_ns * 1e-9 * hops
        routing_overhead = 10e-9 * hops  # 10ns per hop routing
        return serialization + propagation + routing_overhead
    
    def calculate_bandwidth_efficiency(self, topology: TopologyType, 
                                        traffic_pattern: str = "all_to_all") -> float:
        """Calculate effective bandwidth considering topology contention."""
        if traffic_pattern == "nearest_neighbor":
            return 0.95  # High efficiency for local communication
        elif traffic_pattern == "all_to_all":
            # Bisection bandwidth limits
            if topology == TopologyType.LINEAR_CHAIN:
                return 0.25  # Poor - single link bottleneck
            elif topology == TopologyType.RING:
                return 0.5  # Better - two paths
            elif topology == TopologyType.GRID_2x2:
                return 0.7  # Good bisection bandwidth
            elif topology == TopologyType.GRID_4x4:
                return 0.6
            elif topology == TopologyType.TORUS:
                return 0.85  # Best for all-to-all
            else:
                return 0.8
        return 1.0
    
    def calculate_io_pin_requirements(self, num_links: int) -> int:
        """Calculate total I/O pins needed for interconnect."""
        return num_links * self.interconnect.pins_per_link
    
    def calculate_power_for_links(self, num_links: int, utilization: float = 0.5) -> float:
        """Calculate power consumption for interconnect links."""
        # Base power + dynamic power based on utilization
        base_power = num_links * self.interconnect.power_mw_per_link
        dynamic_power = base_power * utilization * 0.5  # Activity factor
        return (base_power * 0.3 + dynamic_power) / 1000  # Watts

# ============================================================================
# TOPOLOGY ANALYSIS
# ============================================================================

class TopologyAnalyzer:
    """Analyzes different multi-chip topologies."""
    
    def __init__(self, chip: ChipConfig, interconnect: InterconnectSpec):
        self.chip = chip
        self.interconnect = interconnect
        self.comm = InterChipCommunication(interconnect)
    
    def get_topology_properties(self, topology_type: TopologyType, 
                                 num_chips: int) -> Dict:
        """Get properties for a specific topology."""
        if topology_type == TopologyType.LINEAR_CHAIN:
            return self._linear_chain_props(num_chips)
        elif topology_type == TopologyType.RING:
            return self._ring_props(num_chips)
        elif topology_type == TopologyType.GRID_2x2:
            return self._grid_props(2, 2)
        elif topology_type == TopologyType.GRID_4x4:
            return self._grid_props(4, 4)
        elif topology_type == TopologyType.TORUS:
            return self._torus_props(num_chips)
        elif topology_type == TopologyType.TREE:
            return self._tree_props(num_chips)
        else:
            return self._fully_connected_props(num_chips)
    
    def _linear_chain_props(self, n: int) -> Dict:
        """Linear chain: Chips connected in sequence."""
        return {
            'diameter': n - 1,
            'avg_hops': (n + 1) / 3,
            'bisection_bandwidth': 1,
            'links_per_chip': 2 if n > 1 else 0,
            'total_links': n - 1,
            'redundancy': 0.0,  # No redundancy
            'cost_per_link': 1.0,
            'max_faults': 0
        }
    
    def _ring_props(self, n: int) -> Dict:
        """Ring: Linear chain with wrap-around."""
        return {
            'diameter': n // 2,
            'avg_hops': n / 4,
            'bisection_bandwidth': 2,
            'links_per_chip': 2,
            'total_links': n,
            'redundancy': 1.0 / n,  # One alternate path
            'cost_per_link': 1.0,
            'max_faults': 1
        }
    
    def _grid_props(self, rows: int, cols: int) -> Dict:
        """2D Mesh grid topology."""
        n = rows * cols
        return {
            'diameter': (rows - 1) + (cols - 1),
            'avg_hops': (rows + cols) / 3,
            'bisection_bandwidth': min(rows, cols),
            'links_per_chip': 4 if n > 1 else 0,  # Up to 4 neighbors
            'total_links': (rows - 1) * cols + (cols - 1) * rows,
            'redundancy': 0.5,  # Multiple paths exist
            'cost_per_link': 1.0,
            'max_faults': min(rows, cols) - 1
        }
    
    def _torus_props(self, n: int) -> Dict:
        """Torus: Grid with wrap-around links."""
        side = int(np.sqrt(n))
        if side * side != n:
            side = int(np.ceil(np.sqrt(n)))
        return {
            'diameter': side // 2,
            'avg_hops': side / 4,
            'bisection_bandwidth': 2 * side,
            'links_per_chip': 4,
            'total_links': 2 * n,
            'redundancy': 2.0,  # Two paths in each dimension
            'cost_per_link': 1.2,  # Extra for wrap-around routing
            'max_faults': 2 * side - 2
        }
    
    def _tree_props(self, n: int) -> Dict:
        """Tree topology for hierarchical communication."""
        depth = int(np.ceil(np.log2(n)))
        return {
            'diameter': 2 * depth,
            'avg_hops': 2 * depth / 3,
            'bisection_bandwidth': 1,  # Root is bottleneck
            'links_per_chip': 3,  # Parent + 2 children max
            'total_links': n - 1,
            'redundancy': 0.0,
            'cost_per_link': 0.8,  # Simpler routing
            'max_faults': 0
        }
    
    def _fully_connected_props(self, n: int) -> Dict:
        """Fully connected (all-to-all)."""
        return {
            'diameter': 1,
            'avg_hops': 1,
            'bisection_bandwidth': n * n // 4,
            'links_per_chip': n - 1,
            'total_links': n * (n - 1) // 2,
            'redundancy': n - 2,  # n-2 alternate paths
            'cost_per_link': float(n - 1),  # Scales poorly
            'max_faults': n - 2
        }
    
    def calculate_total_latency(self, topology_type: TopologyType, 
                                 num_chips: int, message_per_inference: float) -> float:
        """Calculate total communication latency per inference."""
        props = self.get_topology_properties(topology_type, num_chips)
        avg_hops = props['avg_hops']
        
        # Average message size for weight/activation transfer
        # For tensor parallelism: ~1MB per layer for activations
        # For pipeline parallelism: ~10MB per stage boundary
        avg_message_size = 1e6  # 1MB
        
        latency_per_msg = self.comm.calculate_latency(avg_message_size, int(avg_hops))
        total_latency = latency_per_msg * message_per_inference
        
        return total_latency
    
    def calculate_bandwidth_requirements(self, model_size: float, 
                                          batch_size: int,
                                          parallelism: ParallelismType) -> float:
        """Calculate required inter-chip bandwidth for given configuration."""
        # Activation size per token (approximate)
        hidden_size = int(np.sqrt(model_size) * 0.5)  # Rough estimate
        activation_bytes = hidden_size * 2  # FP16
        
        # Communication volume depends on parallelism strategy
        if parallelism == ParallelismType.TENSOR:
            # All-reduce for each layer
            comm_per_layer = activation_bytes * batch_size
            num_layers = int(model_size / (hidden_size * hidden_size * 12))
            total_comm = comm_per_layer * num_layers
        elif parallelism == ParallelismType.LAYER_WISE:
            # Send activations between stages
            total_comm = activation_bytes * batch_size * 2  # Forward + backward
        elif parallelism == ParallelismType.EXPERT:
            # Router communication
            total_comm = activation_bytes * batch_size * 0.1  # 10% routed
        else:  # DATA
            total_comm = activation_bytes * batch_size * 0.01  # Minimal
        
        # Required bandwidth = total communication / time per token
        time_per_token = 1.0 / SINGLE_CHIP_THROUGHPUT  # seconds
        required_bw = total_comm / time_per_token
        
        return required_bw

# ============================================================================
# PARALLELISM STRATEGIES
# ============================================================================

class ParallelismAnalyzer:
    """Analyzes different parallelism strategies."""
    
    def __init__(self, chip: ChipConfig, topology: TopologyAnalyzer):
        self.chip = chip
        self.topology = topology
    
    def analyze_layer_wise_partition(self, model_size: float, 
                                       num_chips: int,
                                       topology_type: TopologyType) -> Dict:
        """Analyze layer-wise (pipeline) parallelism."""
        layers_per_chip = self._estimate_layers(model_size) / num_chips
        
        # Pipeline bubble overhead
        num_stages = num_chips
        bubble_ratio = (num_stages - 1) / (2 * num_stages)  # For GPipe schedule
        
        # Communication: activations between stages
        hidden_size = int(np.sqrt(model_size / 12))  # Approximate
        activation_size = hidden_size * 2  # FP16 bytes
        
        # Communication overhead
        comm_per_token = activation_size * 2  # Forward + backward boundary
        comm_ratio = 0.05 * (num_stages - 1)  # ~5% per stage boundary
        
        return {
            'layers_per_chip': layers_per_chip,
            'bubble_overhead': bubble_ratio,
            'communication_ratio': comm_ratio,
            'activation_transfer_bytes': comm_per_token,
            'memory_efficiency': 1.0,  # Each chip stores subset
            'parallelism_efficiency': 1 - bubble_ratio - comm_ratio
        }
    
    def analyze_tensor_parallelism(self, model_size: float,
                                     num_chips: int,
                                     topology_type: TopologyType) -> Dict:
        """Analyze tensor parallelism (attention head splitting)."""
        hidden_size = int(np.sqrt(model_size / 12))
        num_heads = self._estimate_heads(model_size)
        heads_per_chip = num_heads / num_chips
        
        # All-reduce required after each layer
        num_layers = self._estimate_layers(model_size)
        activation_per_layer = hidden_size * 2  # FP16
        
        # Communication: All-reduce for every layer
        # Ring all-reduce: 2 * (n-1) / n messages per reduce
        allreduce_factor = 2 * (num_chips - 1) / num_chips
        comm_per_token = activation_per_layer * num_layers * allreduce_factor
        
        # Communication ratio
        comm_ratio = 0.10 * (num_chips - 1) / num_chips * num_layers / 32
        
        return {
            'heads_per_chip': heads_per_chip,
            'layers_shared': num_layers,  # All chips process all layers
            'communication_ratio': comm_ratio,
            'allreduce_bytes': comm_per_token,
            'memory_efficiency': 1.0 / num_chips,  # Weights split across chips
            'parallelism_efficiency': 1 - comm_ratio
        }
    
    def analyze_expert_parallelism(self, model_size: float,
                                     num_chips: int,
                                     num_experts: int,
                                     topology_type: TopologyType) -> Dict:
        """Analyze expert parallelism for MoE models."""
        experts_per_chip = num_experts / num_chips
        expert_size = model_size / num_experts
        
        # Router communication overhead
        router_overhead = 0.02  # 2% for routing decisions
        
        # Load imbalance (some experts busier)
        load_imbalance = 1 - 0.8 * (num_experts / (num_chips * 8))  # Improves with more experts
        
        # Communication: routed tokens to expert chips
        comm_ratio = 0.08 * np.sqrt(num_chips)  # Scales with sqrt(n) due to random routing
        
        return {
            'experts_per_chip': experts_per_chip,
            'expert_size': expert_size,
            'router_overhead': router_overhead,
            'load_imbalance_factor': load_imbalance,
            'communication_ratio': comm_ratio,
            'memory_efficiency': 1.0 / num_chips,
            'parallelism_efficiency': load_imbalance * (1 - comm_ratio)
        }
    
    def analyze_data_parallelism(self, model_size: float,
                                   num_chips: int) -> Dict:
        """Analyze data parallelism for batch inference."""
        # Each chip has full model, processes subset of batch
        if model_size > self.chip.weights:
            # Model doesn't fit on single chip - data parallelism not viable
            return {
                'viable': False,
                'reason': 'Model exceeds single chip capacity',
                'parallelism_efficiency': 0.0
            }
        
        # Gradient synchronization (not needed for inference)
        # Only useful for increasing batch throughput
        comm_ratio = 0.01  # Minimal for inference
        
        return {
            'viable': True,
            'batch_per_chip': 1,
            'communication_ratio': comm_ratio,
            'memory_efficiency': 1.0,  # Full model on each chip
            'parallelism_efficiency': 1 - comm_ratio,
            'throughput_scaling': num_chips  # Linear scaling
        }
    
    def _estimate_layers(self, model_size: float) -> int:
        """Estimate number of layers from model size."""
        # Approximate: LLM ~ 12 * hidden^2 * layers
        hidden = int(np.sqrt(model_size / 12))
        layers = int(model_size / (12 * hidden * hidden))
        return max(1, layers)
    
    def _estimate_heads(self, model_size: float) -> int:
        """Estimate number of attention heads."""
        hidden = int(np.sqrt(model_size / 12))
        # Typically hidden / 64 heads
        return max(1, hidden // 64)

# ============================================================================
# AMDAHL'S LAW ANALYSIS
# ============================================================================

class AmdahlAnalyzer:
    """Analyzes scaling limits using Amdahl's Law and extensions."""
    
    def __init__(self):
        pass
    
    def basic_amdahl(self, parallel_fraction: float, num_processors: int) -> float:
        """Calculate speedup using basic Amdahl's Law."""
        serial_fraction = 1 - parallel_fraction
        return 1 / (serial_fraction + parallel_fraction / num_processors)
    
    def gustafson_scaling(self, parallel_fraction: float, num_processors: int,
                           scaled_problem: float = 1.0) -> float:
        """Calculate speedup using Gustafson's Law (scaled speedup)."""
        serial_fraction = 1 - parallel_fraction
        # Scaled speedup: S = s + p * N
        return serial_fraction + parallel_fraction * num_processors * scaled_problem
    
    def communication_overhead_model(self, parallel_fraction: float,
                                       num_processors: int,
                                       comm_overhead: float) -> float:
        """Extended Amdahl with communication overhead."""
        serial_fraction = 1 - parallel_fraction
        # Overhead increases with number of processors
        overhead = comm_overhead * (num_processors - 1)
        return 1 / (serial_fraction + parallel_fraction / num_processors + overhead)
    
    def roofline_analysis(self, compute_intensity: float,
                           peak_flops: float,
                           memory_bw: float) -> float:
        """Roofline model: achievable performance."""
        # Compute-bound region
        compute_bound = peak_flops
        
        # Memory-bound region
        memory_bound = memory_bw * compute_intensity
        
        return min(compute_bound, memory_bound)
    
    def analyze_scaling_limits(self, parallel_fraction: float,
                                  max_chips: int = 64) -> AmdahlAnalysis:
        """Analyze scaling limits and efficiency."""
        serial_fraction = 1 - parallel_fraction
        max_speedup = 1 / serial_fraction
        
        efficiency_at_n = {}
        for n in range(1, max_chips + 1):
            speedup = self.basic_amdahl(parallel_fraction, n)
            efficiency_at_n[n] = speedup / n
        
        return AmdahlAnalysis(
            parallel_fraction=parallel_fraction,
            serial_fraction=serial_fraction,
            max_speedup=max_speedup,
            efficiency_at_n=efficiency_at_n
        )

# ============================================================================
# PERFORMANCE SCALING SIMULATION
# ============================================================================

class PerformanceScalingSimulator:
    """Simulates performance scaling across multiple chips."""
    
    def __init__(self, chip: ChipConfig):
        self.chip = chip
        self.amdahl = AmdahlAnalyzer()
    
    def simulate_scaling(self, model_size: float,
                           num_chips_list: List[int],
                           topology_type: TopologyType,
                           parallelism_type: ParallelismType) -> List[ScalingResult]:
        """Run scaling simulation for different chip counts."""
        results = []
        
        # Create interconnect
        interconnect = InterconnectSpec(
            name="SERDES_25G",
            bandwidth_gbps=25.0,
            latency_ns=30,
            pins_per_link=4,
            power_mw_per_link=250
        )
        
        topology = TopologyAnalyzer(self.chip, interconnect)
        parallelism = ParallelismAnalyzer(self.chip, topology)
        
        for n in num_chips_list:
            result = self._simulate_single_config(
                model_size, n, topology_type, parallelism_type,
                topology, parallelism, interconnect
            )
            results.append(result)
        
        return results
    
    def _simulate_single_config(self, model_size: float,
                                   num_chips: int,
                                   topology_type: TopologyType,
                                   parallelism_type: ParallelismType,
                                   topology: TopologyAnalyzer,
                                   parallelism: ParallelismAnalyzer,
                                   interconnect: InterconnectSpec) -> ScalingResult:
        """Simulate single configuration."""
        
        # Get topology properties
        topo_props = topology.get_topology_properties(topology_type, num_chips)
        
        # Get parallelism efficiency
        if parallelism_type == ParallelismType.LAYER_WISE:
            para_result = parallelism.analyze_layer_wise_partition(
                model_size, num_chips, topology_type)
        elif parallelism_type == ParallelismType.TENSOR:
            para_result = parallelism.analyze_tensor_parallelism(
                model_size, num_chips, topology_type)
        elif parallelism_type == ParallelismType.EXPERT:
            para_result = parallelism.analyze_expert_parallelism(
                model_size, num_chips, 8 * num_chips, topology_type)
        else:
            para_result = parallelism.analyze_data_parallelism(model_size, num_chips)
        
        # Calculate ideal vs actual speedup
        ideal_speedup = num_chips
        parallel_efficiency = para_result.get('parallelism_efficiency', 0.8)
        
        # Account for communication overhead
        comm_overhead = para_result.get('communication_ratio', 0.1)
        topo_overhead = 0.05 * topo_props['avg_hops'] / max(1, num_chips // 4)
        
        actual_efficiency = parallel_efficiency * (1 - topo_overhead)
        actual_speedup = ideal_speedup * actual_efficiency
        
        # Calculate throughput
        base_throughput = self.chip.throughput_tps
        if model_size <= self.chip.weights:
            # Model fits on single chip
            single_chip_throughput = base_throughput * (self.chip.weights / model_size)
        else:
            # Model requires multiple chips
            single_chip_throughput = base_throughput * (self.chip.weights / model_size)
        
        throughput = single_chip_throughput * actual_speedup
        
        # Calculate latency per token
        latency_ms = 1000 / throughput if throughput > 0 else float('inf')
        
        # Calculate power
        link_power = InterChipCommunication(interconnect).calculate_power_for_links(
            topo_props['links_per_chip'], utilization=0.5
        )
        total_power = num_chips * self.chip.power_w + link_power * num_chips
        
        # Calculate cost
        total_cost = num_chips * self.chip.cost_usd
        
        # Cost per token (amortized over 3 years, 50% utilization)
        tokens_per_year = throughput * 3600 * 24 * 365 * 0.5
        cost_per_token = total_cost / (tokens_per_year * 3) if tokens_per_year > 0 else float('inf')
        
        return ScalingResult(
            num_chips=num_chips,
            model_size=model_size,
            topology=topology_type,
            parallelism=parallelism_type,
            ideal_speedup=ideal_speedup,
            actual_speedup=actual_speedup,
            efficiency=actual_speedup / ideal_speedup,
            throughput_tps=throughput,
            latency_ms=latency_ms,
            communication_overhead=comm_overhead + topo_overhead,
            total_power_w=total_power,
            total_cost_usd=total_cost,
            cost_per_token=cost_per_token
        )

# ============================================================================
# COST-PERFORMANCE ANALYSIS
# ============================================================================

class CostPerformanceAnalyzer:
    """Analyzes cost-performance tradeoffs."""
    
    def __init__(self, chip: ChipConfig):
        self.chip = chip
    
    def compare_with_gpu(self, model_size: float,
                           num_chips: int,
                           scaling_result: ScalingResult) -> Dict:
        """Compare multi-chip solution with GPU alternatives."""
        comparisons = {}
        
        for gpu_name, gpu_spec in GPU_DATA.items():
            # Estimate GPU throughput for target model
            gpu_memory = gpu_spec['memory']
            
            if model_size * 2 <= gpu_memory:  # Model fits with KV cache
                # Use reported throughput, scale by model size
                gpu_throughput = gpu_spec.get('throughput_70b', 20)
                if model_size < 70e9:
                    gpu_throughput *= np.sqrt(70e9 / model_size)
                elif model_size > 70e9:
                    gpu_throughput *= np.sqrt(70e9 / model_size)
            else:
                # Model doesn't fit - need multiple GPUs or offloading
                num_gpus_needed = int(np.ceil(model_size * 2 / gpu_memory))
                gpu_throughput = gpu_spec.get('throughput_70b', 20) / num_gpus_needed
            
            # Cost comparison
            gpu_cost = gpu_spec['cost']
            chip_cost = scaling_result.total_cost_usd
            
            # Power comparison
            gpu_power = gpu_spec['power']
            chip_power = scaling_result.total_power_w
            
            # Throughput comparison
            chip_throughput = scaling_result.throughput_tps
            
            # Performance per dollar
            perf_per_dollar_gpu = gpu_throughput / gpu_cost
            perf_per_dollar_chip = chip_throughput / chip_cost
            
            # Performance per watt
            perf_per_watt_gpu = gpu_throughput / gpu_power
            perf_per_watt_chip = chip_throughput / chip_power if chip_power > 0 else 0
            
            comparisons[gpu_name] = {
                'gpu_throughput_tps': gpu_throughput,
                'chip_throughput_tps': chip_throughput,
                'throughput_ratio': chip_throughput / gpu_throughput if gpu_throughput > 0 else float('inf'),
                'gpu_cost': gpu_cost,
                'chip_cost': chip_cost,
                'cost_ratio': chip_cost / gpu_cost,
                'gpu_power_w': gpu_power,
                'chip_power_w': chip_power,
                'power_ratio': chip_power / gpu_power,
                'perf_per_dollar_gpu': perf_per_dollar_gpu,
                'perf_per_dollar_chip': perf_per_dollar_chip,
                'perf_per_watt_gpu': perf_per_watt_gpu,
                'perf_per_watt_chip': perf_per_watt_chip,
                'cost_advantage': perf_per_dollar_chip / perf_per_dollar_gpu if perf_per_dollar_gpu > 0 else float('inf'),
                'efficiency_advantage': perf_per_watt_chip / perf_per_watt_gpu if perf_per_watt_gpu > 0 else float('inf')
            }
        
        return comparisons
    
    def total_cost_of_ownership(self, num_chips: int,
                                   throughput: float,
                                   years: int = 5) -> Dict:
        """Calculate total cost of ownership."""
        # Hardware costs
        hardware_cost = num_chips * self.chip.cost_usd
        
        # Power costs
        power_w = num_chips * self.chip.power_w
        electricity_cost_per_kwh = 0.12  # US average
        power_cost_per_year = power_w / 1000 * 24 * 365 * electricity_cost_per_kwh
        
        # Cooling costs (typically 30-50% of power cost)
        cooling_cost_per_year = power_cost_per_year * 0.4
        
        # Maintenance (typically 5-10% of hardware cost per year)
        maintenance_per_year = hardware_cost * 0.05
        
        # Total
        total_power = power_cost_per_year * years
        total_cooling = cooling_cost_per_year * years
        total_maintenance = maintenance_per_year * years
        total_tco = hardware_cost + total_power + total_cooling + total_maintenance
        
        # Tokens produced
        tokens_per_year = throughput * 3600 * 24 * 365 * 0.7  # 70% utilization
        total_tokens = tokens_per_year * years
        
        return {
            'hardware_cost': hardware_cost,
            'power_cost_5yr': total_power,
            'cooling_cost_5yr': total_cooling,
            'maintenance_cost_5yr': total_maintenance,
            'total_tco': total_tco,
            'total_tokens': total_tokens,
            'cost_per_million_tokens': total_tco / (total_tokens / 1e6)
        }
    
    def scaling_cost_curve(self, model_sizes: List[float],
                              max_chips: int = 64) -> Dict:
        """Generate cost scaling curve for different model sizes."""
        results = {}
        
        for model_name, model_size in MODEL_SIZES.items():
            # Calculate minimum chips needed
            min_chips = int(np.ceil(model_size / self.chip.weights))
            
            if min_chips <= max_chips:
                # Calculate cost for minimum viable configuration
                cost = min_chips * self.chip.cost_usd
                
                # Estimate throughput (with efficiency penalty for larger configs)
                efficiency = 1 - 0.02 * (min_chips - 1)  # 2% loss per additional chip
                throughput = self.chip.throughput_tps * (self.chip.weights / model_size) * min_chips * efficiency
                
                results[model_name] = {
                    'model_size': model_size,
                    'min_chips': min_chips,
                    'hardware_cost': cost,
                    'estimated_throughput': max(0.1, throughput),
                    'cost_per_token': cost / (throughput * 3600 * 24 * 365) if throughput > 0 else float('inf')
                }
        
        return results

# ============================================================================
# VISUALIZATION
# ============================================================================

def create_topology_diagram(topology_type: TopologyType, num_chips: int, 
                            output_path: Path):
    """Create visual diagram of chip topology."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Chip positions based on topology
    if topology_type == TopologyType.LINEAR_CHAIN:
        positions = [(i, 0) for i in range(num_chips)]
    elif topology_type == TopologyType.RING:
        angles = np.linspace(0, 2*np.pi, num_chips, endpoint=False)
        positions = [(np.cos(a), np.sin(a)) for a in angles]
    elif topology_type == TopologyType.GRID_2x2:
        positions = [(i % 2, i // 2) for i in range(4)]
    elif topology_type == TopologyType.GRID_4x4:
        positions = [(i % 4, i // 4) for i in range(16)]
    else:
        # Default to grid layout
        side = int(np.ceil(np.sqrt(num_chips)))
        positions = [(i % side, i // side) for i in range(num_chips)]
    
    # Draw chips
    for i, (x, y) in enumerate(positions):
        chip = FancyBboxPatch((x - 0.35, y - 0.35), 0.7, 0.7,
                               boxstyle="round,pad=0.05",
                               facecolor='#3498db', edgecolor='#2c3e50',
                               linewidth=2)
        ax.add_patch(chip)
        ax.text(x, y, f'Chip {i+1}\n2.4B', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
    
    # Draw connections
    if topology_type == TopologyType.LINEAR_CHAIN:
        for i in range(num_chips - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            ax.plot([x1 + 0.35, x2 - 0.35], [y1, y2], 'k-', linewidth=2)
    elif topology_type == TopologyType.RING:
        for i in range(num_chips):
            x1, y1 = positions[i]
            x2, y2 = positions[(i + 1) % num_chips]
            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2)
    elif topology_type in [TopologyType.GRID_2x2, TopologyType.GRID_4x4]:
        # Draw grid connections
        n_side = int(np.sqrt(num_chips))
        for i in range(num_chips):
            x, y = positions[i]
            # Right neighbor
            if (i + 1) % n_side != 0:
                x2, y2 = positions[i + 1]
                ax.plot([x + 0.35, x2 - 0.35], [y, y2], 'k-', linewidth=2)
            # Bottom neighbor
            if i + n_side < num_chips:
                x2, y2 = positions[i + n_side]
                ax.plot([x, x2], [y - 0.35, y2 + 0.35], 'k-', linewidth=2)
    
    ax.set_xlim(-1.5, max(p[0] for p in positions) + 1.5)
    ax.set_ylim(-1.5, max(p[1] for p in positions) + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{topology_type.value.replace("_", " ").title()} Topology\n{num_chips} Chips',
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_scaling_plots(results_by_model: Dict[str, List[ScalingResult]],
                           output_dir: Path):
    """Create scaling efficiency and throughput plots."""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Throughput vs Number of Chips
    ax = axes[0, 0]
    for model_name, results in results_by_model.items():
        chips = [r.num_chips for r in results]
        throughput = [r.throughput_tps for r in results]
        ax.plot(chips, throughput, 'o-', label=model_name, linewidth=2, markersize=8)
    
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Throughput (tokens/s)', fontsize=12)
    ax.set_title('Throughput Scaling', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # 2. Scaling Efficiency
    ax = axes[0, 1]
    for model_name, results in results_by_model.items():
        chips = [r.num_chips for r in results]
        efficiency = [r.efficiency * 100 for r in results]
        ax.plot(chips, efficiency, 'o-', label=model_name, linewidth=2, markersize=8)
    
    ax.axhline(y=80, color='r', linestyle='--', alpha=0.5, label='Target 80%')
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Scaling Efficiency (%)', fontsize=12)
    ax.set_title('Scaling Efficiency vs Chip Count', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    
    # 3. Communication Overhead
    ax = axes[0, 2]
    for model_name, results in results_by_model.items():
        chips = [r.num_chips for r in results]
        overhead = [r.communication_overhead * 100 for r in results]
        ax.plot(chips, overhead, 'o-', label=model_name, linewidth=2, markersize=8)
    
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Communication Overhead (%)', fontsize=12)
    ax.set_title('Communication Overhead Growth', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    
    # 4. Power Consumption
    ax = axes[1, 0]
    for model_name, results in results_by_model.items():
        chips = [r.num_chips for r in results]
        power = [r.total_power_w for r in results]
        ax.plot(chips, power, 'o-', label=model_name, linewidth=2, markersize=8)
    
    ax.axhline(y=700, color='r', linestyle='--', alpha=0.5, label='H100 (700W)')
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Total Power (W)', fontsize=12)
    ax.set_title('Power Consumption', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Cost vs Throughput
    ax = axes[1, 1]
    for model_name, results in results_by_model.items():
        cost = [r.total_cost_usd for r in results]
        throughput = [r.throughput_tps for r in results]
        ax.scatter(cost, throughput, s=100, label=model_name, alpha=0.7)
        # Connect points
        sorted_pairs = sorted(zip(cost, throughput))
        ax.plot([p[0] for p in sorted_pairs], [p[1] for p in sorted_pairs], 
                '--', alpha=0.3)
    
    # Add GPU reference points
    for gpu_name, gpu_spec in GPU_DATA.items():
        ax.scatter(gpu_spec['cost'], gpu_spec['throughput_70b'], 
                  marker='s', s=150, label=f'{gpu_name} (70B)', 
                  edgecolors='black', linewidth=2)
    
    ax.set_xlabel('Total Cost (USD)', fontsize=12)
    ax.set_ylabel('Throughput (tokens/s)', fontsize=12)
    ax.set_title('Cost vs Throughput', fontsize=14, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # 6. Amdahl's Law Analysis
    ax = axes[1, 2]
    amdahl = AmdahlAnalyzer()
    
    for pf in [0.95, 0.90, 0.85, 0.80]:
        analysis = amdahl.analyze_scaling_limits(pf, max_chips=64)
        chips = list(analysis.efficiency_at_n.keys())
        efficiency = [e * 100 for e in analysis.efficiency_at_n.values()]
        ax.plot(chips, efficiency, label=f'{pf*100:.0f}% parallel', linewidth=2)
    
    ax.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% efficiency')
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Efficiency (%)', fontsize=12)
    ax.set_title("Amdahl's Law: Efficiency vs Parallel Fraction", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cycle19_scaling_analysis.png', dpi=150, 
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_parallelism_comparison_plot(parallelism_results: Dict, output_dir: Path):
    """Create comparison plot for different parallelism strategies."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Data from simulation
    strategies = list(parallelism_results.keys())
    metrics = ['memory_efficiency', 'parallelism_efficiency', 'communication_ratio']
    
    # 1. Efficiency Comparison
    ax = axes[0, 0]
    x = np.arange(len(strategies))
    width = 0.35
    
    mem_eff = [parallelism_results[s].get('memory_efficiency', 0.5) * 100 for s in strategies]
    para_eff = [parallelism_results[s].get('parallelism_efficiency', 0.8) * 100 for s in strategies]
    
    bars1 = ax.bar(x - width/2, mem_eff, width, label='Memory Efficiency', color='#3498db')
    bars2 = ax.bar(x + width/2, para_eff, width, label='Parallelism Efficiency', color='#e74c3c')
    
    ax.set_ylabel('Efficiency (%)', fontsize=12)
    ax.set_title('Parallelism Strategy Efficiency', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies], rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 110)
    
    # 2. Communication Overhead
    ax = axes[0, 1]
    comm_overhead = [parallelism_results[s].get('communication_ratio', 0.1) * 100 for s in strategies]
    
    bars = ax.bar(strategies, comm_overhead, color='#9b59b6')
    ax.set_ylabel('Communication Overhead (%)', fontsize=12)
    ax.set_title('Communication Overhead by Strategy', fontsize=14, fontweight='bold')
    ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies], rotation=45, ha='right')
    
    # 3. Memory Distribution
    ax = axes[1, 0]
    # Visualize how model weights are distributed
    labels = ['Layer-wise', 'Tensor', 'Expert', 'Data']
    sizes = [100, 25, 12.5, 100]  # Percentage of model per chip (conceptual)
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    for i, (label, size, color) in enumerate(zip(labels, sizes, colors)):
        ax.barh(i, size, color=color, alpha=0.7)
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel('Model Weights per Chip (%)', fontsize=12)
    ax.set_title('Weight Distribution Strategy', fontsize=14, fontweight='bold')
    ax.axvline(x=100, color='r', linestyle='--', alpha=0.5, label='Full Model')
    
    # 4. Recommended Strategy Matrix
    ax = axes[1, 1]
    model_sizes = ['2.4B', '10B', '70B', '175B']
    chip_counts = ['1', '4', '16', '64']
    
    # Score matrix (higher is better)
    score_matrix = np.array([
        [9, 7, 5, 3],  # 2.4B
        [5, 8, 6, 4],  # 10B
        [1, 4, 7, 6],  # 70B
        [1, 2, 5, 8],  # 175B
    ])
    
    im = ax.imshow(score_matrix, cmap='RdYlGn', aspect='auto')
    ax.set_xticks(np.arange(len(chip_counts)))
    ax.set_yticks(np.arange(len(model_sizes)))
    ax.set_xticklabels(chip_counts)
    ax.set_yticklabels(model_sizes)
    ax.set_xlabel('Number of Chips', fontsize=12)
    ax.set_ylabel('Model Size', fontsize=12)
    ax.set_title('Recommended Configuration Score', fontsize=14, fontweight='bold')
    
    # Add text annotations
    for i in range(len(model_sizes)):
        for j in range(len(chip_counts)):
            text = ax.text(j, i, score_matrix[i, j], ha="center", va="center", 
                          color="black", fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Configuration Score')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cycle19_parallelism_comparison.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

def create_cost_comparison_plot(cost_results: Dict, tco_results: Dict, 
                                 output_dir: Path):
    """Create cost-performance comparison plots."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Hardware Cost Comparison
    ax = axes[0, 0]
    configs = list(cost_results.keys())
    chip_costs = [cost_results[c]['chip_cost'] for c in configs]
    gpu_costs = [cost_results[c]['gpu_cost'] for c in configs]
    
    x = np.arange(len(configs))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, chip_costs, width, label='Multi-Chip', color='#3498db')
    bars2 = ax.bar(x + width/2, gpu_costs, width, label='GPU (H100)', color='#e74c3c')
    
    ax.set_ylabel('Hardware Cost (USD)', fontsize=12)
    ax.set_title('Hardware Cost Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.legend()
    ax.set_yscale('log')
    
    # 2. Performance per Dollar
    ax = axes[0, 1]
    perf_dollar_chip = [cost_results[c]['perf_per_dollar_chip'] for c in configs]
    perf_dollar_gpu = [cost_results[c]['perf_per_dollar_gpu'] for c in configs]
    
    bars1 = ax.bar(x - width/2, perf_dollar_chip, width, label='Multi-Chip', color='#3498db')
    bars2 = ax.bar(x + width/2, perf_dollar_gpu, width, label='GPU (H100)', color='#e74c3c')
    
    ax.set_ylabel('Throughput per Dollar (tok/s/$)', fontsize=12)
    ax.set_title('Performance per Dollar', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.legend()
    
    # 3. Performance per Watt
    ax = axes[1, 0]
    perf_watt_chip = [cost_results[c]['perf_per_watt_chip'] for c in configs]
    perf_watt_gpu = [cost_results[c]['perf_per_watt_gpu'] for c in configs]
    
    bars1 = ax.bar(x - width/2, perf_watt_chip, width, label='Multi-Chip', color='#3498db')
    bars2 = ax.bar(x + width/2, perf_watt_gpu, width, label='GPU (H100)', color='#e74c3c')
    
    ax.set_ylabel('Throughput per Watt (tok/s/W)', fontsize=12)
    ax.set_title('Power Efficiency', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.legend()
    
    # 4. Total Cost of Ownership
    ax = axes[1, 1]
    tco_labels = ['Hardware', 'Power (5yr)', 'Cooling (5yr)', 'Maintenance (5yr)']
    tco_values = [
        tco_results['hardware_cost'],
        tco_results['power_cost_5yr'],
        tco_results['cooling_cost_5yr'],
        tco_results['maintenance_cost_5yr']
    ]
    
    colors = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6']
    ax.pie(tco_values, labels=tco_labels, autopct='%1.1f%%', colors=colors,
           explode=(0.05, 0, 0, 0), shadow=True)
    ax.set_title(f'Total Cost of Ownership: ${tco_results["total_tco"]:,.0f}\n'
                 f'Cost: ${tco_results["cost_per_million_tokens"]:.3f}/M tokens',
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cycle19_cost_comparison.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_simulation():
    """Run complete multi-chip scaling simulation."""
    print("=" * 70)
    print("CYCLE 19: MULTI-CHIP SCALING ARCHITECTURE SIMULATION")
    print("=" * 70)
    
    output_dir = Path("/home/z/my-project/research")
    output_dir.mkdir(exist_ok=True)
    
    # Create chip configuration
    chip = ChipConfig(
        weights=SINGLE_CHIP_WEIGHTS,
        throughput_tps=SINGLE_CHIP_THROUGHPUT,
        power_w=SINGLE_CHIP_POWER,
        memory_bw_bytes=SINGLE_CHIP_MEMORY_BW,
        die_size_mm2=SINGLE_CHIP_DIE_SIZE,
        cost_usd=SINGLE_CHIP_COST,
        io_links=4,
        io_bandwidth_per_link_gbps=25.0
    )
    
    # Create interconnect
    interconnect = InterconnectSpec(
        name="SERDES_25G",
        bandwidth_gbps=25.0,
        latency_ns=30,
        pins_per_link=4,
        power_mw_per_link=250
    )
    
    # Initialize analyzers
    topology_analyzer = TopologyAnalyzer(chip, interconnect)
    parallelism_analyzer = ParallelismAnalyzer(chip, topology_analyzer)
    performance_sim = PerformanceScalingSimulator(chip)
    cost_analyzer = CostPerformanceAnalyzer(chip)
    
    results = {}
    
    # =========================================================================
    # 1. INTER-CHIP COMMUNICATION ANALYSIS
    # =========================================================================
    print("\n1. INTER-CHIP COMMUNICATION ANALYSIS")
    print("-" * 50)
    
    comm_results = {}
    for tech_name, tech_spec in INTERCONNECT_TECH.items():
        comm = InterChipCommunication(InterconnectSpec(
            name=tech_name,
            bandwidth_gbps=tech_spec['bandwidth'] / 1e9,
            latency_ns=tech_spec['latency_ns'],
            pins_per_link=tech_spec['pins'],
            power_mw_per_link=tech_spec['power_mW']
        ))
        
        # Test different message sizes
        message_sizes = [1e3, 1e6, 1e9]  # 1KB, 1MB, 1GB
        latencies = {}
        for size in message_sizes:
            latencies[f'{size/1e3:.0f}KB'] = comm.calculate_latency(size) * 1e6  # μs
        
        comm_results[tech_name] = {
            'bandwidth_gbps': tech_spec['bandwidth'] / 1e9,
            'latency_ns': tech_spec['latency_ns'],
            'pins_per_link': tech_spec['pins'],
            'power_mw': tech_spec['power_mW'],
            'latencies_us': latencies
        }
        
        print(f"\n{tech_name}:")
        print(f"  Bandwidth: {comm_results[tech_name]['bandwidth_gbps']:.1f} Gbps")
        print(f"  Latency: {comm_results[tech_name]['latency_ns']:.1f} ns")
        print(f"  Pins/link: {comm_results[tech_name]['pins_per_link']}")
        print(f"  Power: {comm_results[tech_name]['power_mw']:.0f} mW")
    
    results['interconnect'] = comm_results
    
    # =========================================================================
    # 2. TOPOLOGY ANALYSIS
    # =========================================================================
    print("\n2. SCALING TOPOLOGIES")
    print("-" * 50)
    
    topology_results = {}
    topologies = [
        (TopologyType.LINEAR_CHAIN, 4),
        (TopologyType.RING, 4),
        (TopologyType.GRID_2x2, 4),
        (TopologyType.GRID_4x4, 16),
        (TopologyType.TORUS, 16),
    ]
    
    for topo_type, num_chips in topologies:
        props = topology_analyzer.get_topology_properties(topo_type, num_chips)
        topology_results[topo_type.value] = {
            'num_chips': num_chips,
            'diameter': props['diameter'],
            'avg_hops': props['avg_hops'],
            'bisection_bandwidth': props['bisection_bandwidth'],
            'links_per_chip': props['links_per_chip'],
            'total_links': props['total_links'],
            'redundancy': props['redundancy'],
            'max_faults': props['max_faults']
        }
        
        print(f"\n{topo_type.value}:")
        print(f"  Chips: {num_chips}")
        print(f"  Diameter: {props['diameter']} hops")
        print(f"  Avg hops: {props['avg_hops']:.2f}")
        print(f"  Links/chip: {props['links_per_chip']}")
        print(f"  Bisection BW: {props['bisection_bandwidth']} links")
        print(f"  Fault tolerance: {props['max_faults']} faults")
        
        # Create topology diagram
        create_topology_diagram(topo_type, num_chips,
                               output_dir / f'cycle19_topology_{topo_type.value}.png')
    
    results['topologies'] = topology_results
    
    # =========================================================================
    # 3. PARALLELISM STRATEGIES
    # =========================================================================
    print("\n3. PARALLELISM STRATEGIES")
    print("-" * 50)
    
    # Test with 70B model on 16 chips
    model_size = 70e9
    num_chips = 16
    
    parallelism_results = {}
    
    # Layer-wise (Pipeline)
    layer_result = parallelism_analyzer.analyze_layer_wise_partition(
        model_size, num_chips, TopologyType.GRID_4x4)
    parallelism_results['layer_wise'] = layer_result
    print(f"\nLayer-wise (Pipeline) Parallelism:")
    print(f"  Layers per chip: {layer_result['layers_per_chip']:.1f}")
    print(f"  Bubble overhead: {layer_result['bubble_overhead']*100:.1f}%")
    print(f"  Communication ratio: {layer_result['communication_ratio']*100:.1f}%")
    print(f"  Efficiency: {layer_result['parallelism_efficiency']*100:.1f}%")
    
    # Tensor Parallelism
    tensor_result = parallelism_analyzer.analyze_tensor_parallelism(
        model_size, num_chips, TopologyType.GRID_4x4)
    parallelism_results['tensor'] = tensor_result
    print(f"\nTensor Parallelism:")
    print(f"  Heads per chip: {tensor_result['heads_per_chip']:.1f}")
    print(f"  Communication ratio: {tensor_result['communication_ratio']*100:.1f}%")
    print(f"  Memory efficiency: {tensor_result['memory_efficiency']*100:.1f}%")
    print(f"  Efficiency: {tensor_result['parallelism_efficiency']*100:.1f}%")
    
    # Expert Parallelism
    expert_result = parallelism_analyzer.analyze_expert_parallelism(
        model_size, num_chips, 64, TopologyType.GRID_4x4)
    parallelism_results['expert'] = expert_result
    print(f"\nExpert Parallelism (MoE):")
    print(f"  Experts per chip: {expert_result['experts_per_chip']:.1f}")
    print(f"  Load imbalance: {(1-expert_result['load_imbalance_factor'])*100:.1f}%")
    print(f"  Communication ratio: {expert_result['communication_ratio']*100:.1f}%")
    print(f"  Efficiency: {expert_result['parallelism_efficiency']*100:.1f}%")
    
    # Data Parallelism
    data_result = parallelism_analyzer.analyze_data_parallelism(model_size, num_chips)
    parallelism_results['data'] = data_result
    print(f"\nData Parallelism:")
    print(f"  Viable: {data_result['viable']}")
    if data_result['viable']:
        print(f"  Throughput scaling: {data_result['throughput_scaling']}x")
        print(f"  Efficiency: {data_result['parallelism_efficiency']*100:.1f}%")
    else:
        print(f"  Reason: {data_result['reason']}")
    
    results['parallelism'] = parallelism_results
    
    # Create parallelism comparison plot
    create_parallelism_comparison_plot(parallelism_results, output_dir)
    
    # =========================================================================
    # 4. PERFORMANCE SCALING
    # =========================================================================
    print("\n4. PERFORMANCE SCALING SIMULATION")
    print("-" * 50)
    
    scaling_results = {}
    results_by_model = {}
    
    for model_name, model_size in list(MODEL_SIZES.items())[:4]:  # Up to 175B
        min_chips = max(1, int(np.ceil(model_size / chip.weights)))
        chip_counts = [min_chips * m for m in [1, 2, 4, 8, 16]]
        chip_counts = [c for c in chip_counts if c <= 64]
        
        if not chip_counts:
            continue
        
        model_results = performance_sim.simulate_scaling(
            model_size, chip_counts,
            TopologyType.GRID_4x4, ParallelismType.TENSOR
        )
        
        results_by_model[model_name] = model_results
        
        print(f"\n{model_name} Model:")
        print(f"  Min chips required: {min_chips}")
        for r in model_results:
            print(f"    {r.num_chips} chips: {r.throughput_tps:.2f} tok/s, "
                  f"eff={r.efficiency*100:.1f}%, power={r.total_power_w:.1f}W")
    
    results['scaling'] = {name: [asdict(r) for r in res] 
                          for name, res in results_by_model.items()}
    
    # Create scaling plots
    create_scaling_plots(results_by_model, output_dir)
    
    # =========================================================================
    # 5. AMDAHL'S LAW ANALYSIS
    # =========================================================================
    print("\n5. AMDAHL'S LAW ANALYSIS")
    print("-" * 50)
    
    amdahl = AmdahlAnalyzer()
    amdahl_results = {}
    
    for parallel_fraction in [0.95, 0.90, 0.85, 0.80]:
        analysis = amdahl.analyze_scaling_limits(parallel_fraction, max_chips=64)
        amdahl_results[f'pf_{parallel_fraction}'] = {
            'parallel_fraction': parallel_fraction,
            'serial_fraction': analysis.serial_fraction,
            'max_speedup': analysis.max_speedup,
            'efficiency_16chips': analysis.efficiency_at_n.get(16, 0),
            'efficiency_64chips': analysis.efficiency_at_n.get(64, 0)
        }
        
        print(f"\nParallel Fraction: {parallel_fraction*100:.0f}%")
        print(f"  Max theoretical speedup: {analysis.max_speedup:.1f}x")
        print(f"  Efficiency at 16 chips: {analysis.efficiency_at_n.get(16, 0)*100:.1f}%")
        print(f"  Efficiency at 64 chips: {analysis.efficiency_at_n.get(64, 0)*100:.1f}%")
    
    results['amdahl'] = amdahl_results
    
    # =========================================================================
    # 6. COST-PERFORMANCE ANALYSIS
    # =========================================================================
    print("\n6. COST-PERFORMANCE ANALYSIS")
    print("-" * 50)
    
    # Compare 16-chip 70B configuration with GPUs
    if '70B' in results_by_model and results_by_model['70B']:
        target_result = [r for r in results_by_model['70B'] if r.num_chips >= 16][0] \
            if any(r.num_chips >= 16 for r in results_by_model['70B']) \
            else results_by_model['70B'][-1]
        
        cost_comparison = cost_analyzer.compare_with_gpu(
            70e9, target_result.num_chips, target_result
        )
        
        print("\nGPU Comparison (70B model):")
        for gpu_name, comparison in cost_comparison.items():
            print(f"\n{gpu_name}:")
            print(f"  Throughput ratio: {comparison['throughput_ratio']:.2f}x")
            print(f"  Cost ratio: {comparison['cost_ratio']:.2f}x")
            print(f"  Power ratio: {comparison['power_ratio']:.2f}x")
            print(f"  Perf/$ advantage: {comparison['cost_advantage']:.2f}x")
            print(f"  Perf/W advantage: {comparison['efficiency_advantage']:.2f}x")
        
        results['cost_comparison'] = cost_comparison
        
        # TCO Analysis
        tco_result = cost_analyzer.total_cost_of_ownership(
            target_result.num_chips, target_result.throughput_tps, years=5
        )
        
        print(f"\nTotal Cost of Ownership (5 years, {target_result.num_chips} chips):")
        print(f"  Hardware: ${tco_result['hardware_cost']:,.0f}")
        print(f"  Power: ${tco_result['power_cost_5yr']:,.0f}")
        print(f"  Cooling: ${tco_result['cooling_cost_5yr']:,.0f}")
        print(f"  Maintenance: ${tco_result['maintenance_cost_5yr']:,.0f}")
        print(f"  Total TCO: ${tco_result['total_tco']:,.0f}")
        print(f"  Cost per M tokens: ${tco_result['cost_per_million_tokens']:.4f}")
        
        results['tco'] = tco_result
        
        # Create cost comparison plots
        create_cost_comparison_plot(cost_comparison, tco_result, output_dir)
    
    # =========================================================================
    # SAVE RESULTS
    # =========================================================================
    
    # Save JSON results
    json_results = {
        'timestamp': datetime.now().isoformat(),
        'chip_config': asdict(chip),
        'interconnect': {k: {sk: float(sv) if isinstance(sv, (np.floating, float)) else sv 
                            for sk, sv in v.items()} 
                        for k, v in results['interconnect'].items()},
        'topologies': results['topologies'],
        'parallelism': {k: {sk: float(sv) if isinstance(sv, (np.floating, float)) else sv 
                           for sk, sv in v.items() if not isinstance(sv, dict)}
                       for k, v in results['parallelism'].items()},
        'amdahl': results['amdahl'],
        'scaling_summary': {k: [{'num_chips': r['num_chips'],
                                  'throughput': float(r['throughput_tps']),
                                  'efficiency': float(r['efficiency']),
                                  'power': float(r['total_power_w'])}
                                 for r in v]
                           for k, v in results['scaling'].items()}
    }
    
    with open(output_dir / 'cycle19_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput files:")
    print(f"  - {output_dir / 'cycle19_results.json'}")
    print(f"  - {output_dir / 'cycle19_scaling_analysis.png'}")
    print(f"  - {output_dir / 'cycle19_parallelism_comparison.png'}")
    print(f"  - {output_dir / 'cycle19_cost_comparison.png'}")
    print(f"  - Topology diagrams: cycle19_topology_*.png")
    
    return results

if __name__ == "__main__":
    results = run_simulation()
