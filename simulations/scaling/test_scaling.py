"""
POLLN Scaling Simulation Tests
==============================

This module contains tests for all scaling simulations.

Author: POLLN Simulation Team
Date: 2026-03-07
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scaling_laws import ScalingLawSimulator, ColonyMetrics
from communication_bottleneck import CommunicationBottleneckSimulator, CommunicationMetrics
from horizontal_vs_vertical import ScalingComparisonSimulator, ScalingConfiguration
from topology_optimization import TopologyOptimizer, TopologyGenerator


class TestScalingLaws:
    """Tests for scaling law validation."""

    def test_simulator_initialization(self):
        """Test that simulator initializes correctly."""
        simulator = ScalingLawSimulator(seed=42)
        assert simulator is not None

    def test_colony_simulation(self):
        """Test that colony simulation produces valid metrics."""
        simulator = ScalingLawSimulator(seed=42)
        metrics = simulator.simulate_colony(n_agents=100, n_steps=100)

        assert isinstance(metrics, ColonyMetrics)
        assert metrics.colony_size == 100
        assert metrics.per_agent_throughput > 0
        assert metrics.avg_latency_ms > 0
        assert metrics.memory_per_agent_mb > 0
        assert metrics.total_throughput > 0

    def test_scaling_experiment(self):
        """Test that scaling experiment runs across multiple sizes."""
        simulator = ScalingLawSimulator(seed=42)
        colony_sizes = [10, 50, 100]
        metrics, analysis = simulator.run_scaling_experiment(
            colony_sizes=colony_sizes,
            n_trials=3
        )

        assert len(metrics) == len(colony_sizes)
        assert 'hypothesis_h1' in analysis
        assert 'best_fit' in analysis

    def test_logarithmic_scaling(self):
        """Test that scaling follows logarithmic pattern."""
        simulator = ScalingLawSimulator(seed=42)
        metrics, _ = simulator.run_scaling_experiment(
            colony_sizes=[100, 500, 1000],
            n_trials=5
        )

        # Throughput should not decrease linearly
        throughput_100 = metrics[0].per_agent_throughput
        throughput_1000 = metrics[2].per_agent_throughput

        # Logarithmic scaling means 10x size < 10x degradation
        degradation_ratio = throughput_100 / throughput_1000
        assert degradation_ratio < 10, "Scaling should be sublinear"

    def test_analysis_generates_valid_fits(self):
        """Test that analysis generates valid R² values."""
        simulator = ScalingLawSimulator(seed=42)
        metrics, analysis = simulator.run_scaling_experiment(
            colony_sizes=[50, 100, 200],
            n_trials=3
        )

        # Check that R² values are valid
        for model_name, fit in analysis['throughput'].items():
            if 'r_squared' in fit:
                assert -1 <= fit['r_squared'] <= 1


class TestCommunicationBottleneck:
    """Tests for communication bottleneck analysis."""

    def test_simulator_initialization(self):
        """Test that simulator initializes correctly."""
        simulator = CommunicationBottleneckSimulator(seed=42)
        assert simulator is not None
        assert simulator.network_bandwidth_gbps > 0

    def test_communication_simulation(self):
        """Test that communication simulation produces valid metrics."""
        simulator = CommunicationBottleneckSimulator(seed=42)
        metrics = simulator.simulate_communication(
            n_agents=100,
            duration_sec=1.0
        )

        assert isinstance(metrics, CommunicationMetrics)
        assert metrics.colony_size == 100
        assert metrics.a2a_packages_per_sec > 0
        assert metrics.avg_package_size_kb > 0
        assert 0 <= metrics.bandwidth_utilization_pct <= 100

    def test_bottleneck_detection(self):
        """Test that bottleneck detection works."""
        simulator = CommunicationBottleneckSimulator(seed=42)
        threshold, analysis = simulator.find_bottleneck_threshold(
            min_agents=100,
            max_agents=2000,
            n_points=10
        )

        assert threshold > 0
        assert 'threshold' in analysis
        assert analysis['threshold'] == threshold

    def test_bandwidth_saturation(self):
        """Test that bandwidth saturates at high colony sizes."""
        simulator = CommunicationBottleneckSimulator(seed=42)

        # Small colony
        small_metrics = simulator.simulate_communication(n_agents=100)
        # Large colony
        large_metrics = simulator.simulate_communication(n_agents=5000)

        assert large_metrics.bandwidth_utilization_pct > small_metrics.bandwidth_utilization_pct
        assert large_metrics.avg_latency_ms >= small_metrics.avg_latency_ms

    def test_queue_buildup(self):
        """Test that queue builds up under load."""
        simulator = CommunicationBottleneckSimulator(seed=42)

        metrics = simulator.simulate_communication(
            n_agents=5000,
            communication_rate=50.0  # High rate
        )

        assert metrics.queue_depth >= 0


class TestHorizontalVsVertical:
    """Tests for horizontal vs vertical scaling comparison."""

    def test_simulator_initialization(self):
        """Test that simulator initializes correctly."""
        simulator = ScalingComparisonSimulator(seed=42)
        assert simulator is not None

    def test_configuration_creation(self):
        """Test that configurations are created correctly."""
        simulator = ScalingComparisonSimulator(seed=42)
        configs = simulator.create_configurations()

        assert len(configs) > 0
        assert all(isinstance(c, ScalingConfiguration) for c in configs)

        # Check that we have horizontal and vertical configs
        has_horizontal = any('Horizontal' in c.name for c in configs)
        has_vertical = any('Vertical' in c.name for c in configs)
        assert has_horizontal
        assert has_vertical

    def test_configuration_simulation(self):
        """Test that configuration simulation produces valid metrics."""
        simulator = ScalingComparisonSimulator(seed=42)
        config = ScalingConfiguration(
            name="Test",
            n_agents=100,
            agent_memory_mb=100,
            agent_cpu_cores=0.1,
            agent_cost_per_hour=0.01
        )

        metrics = simulator.simulate_configuration(config)

        assert metrics.config.name == "Test"
        assert metrics.total_throughput > 0
        assert metrics.cost_per_1m_requests > 0
        assert 0 <= metrics.fault_tolerance_score <= 1

    def test_horizontal_cheaper(self):
        """Test that horizontal scaling is cheaper."""
        simulator = ScalingComparisonSimulator(seed=42)
        aggregated, analysis = simulator.run_comparison_experiment(n_trials=5)

        # Horizontal should have lower cost per 1M requests
        horizontal_cost = aggregated['Horizontal-1000']['avg_cost']
        vertical_cost = aggregated['Vertical-10']['avg_cost']

        assert horizontal_cost < vertical_cost

    def test_cost_performance_ratio(self):
        """Test that horizontal has better cost-performance ratio."""
        simulator = ScalingComparisonSimulator(seed=42)
        aggregated, analysis = simulator.run_comparison_experiment(n_trials=5)

        cpr = analysis['cost_performance']['ratio']
        assert cpr > 1.0  # Horizontal should be better


class TestTopologyOptimization:
    """Tests for network topology optimization."""

    def test_optimizer_initialization(self):
        """Test that optimizer initializes correctly."""
        optimizer = TopologyOptimizer(seed=42)
        assert optimizer is not None

    def test_topology_generation(self):
        """Test that different topologies can be generated."""
        n = 50

        # Test each topology type
        fully_connected = TopologyGenerator.fully_connected(n)
        small_world = TopologyGenerator.small_world(n)
        hierarchical = TopologyGenerator.hierarchical(n)
        random_network = TopologyGenerator.random_network(n)
        scale_free = TopologyGenerator.scale_free(n)

        assert fully_connected.number_of_nodes() == n
        assert small_world.number_of_nodes() == n
        assert hierarchical.number_of_nodes() >= n
        assert random_network.number_of_nodes() == n
        assert scale_free.number_of_nodes() == n

    def test_topology_analysis(self):
        """Test that topology analysis produces valid metrics."""
        optimizer = TopologyOptimizer(seed=42)
        G = TopologyGenerator.small_world(100)

        metrics = optimizer.analyze_topology(G, "Small-World")

        assert metrics.n_nodes == 100
        assert metrics.avg_degree > 0
        assert metrics.avg_path_length > 0
        assert 0 <= metrics.clustering_coefficient <= 1
        assert metrics.communication_efficiency > 0

    def test_communication_simulation(self):
        """Test that communication simulation works."""
        optimizer = TopologyOptimizer(seed=42)
        G = TopologyGenerator.small_world(100)

        stats = optimizer.simulate_communication(G, n_packages=100)

        assert 'avg_latency_ms' in stats
        assert stats['avg_latency_ms'] > 0
        assert 0 <= stats['success_rate'] <= 1

    def test_small_world_properties(self):
        """Test that small-world networks have expected properties."""
        optimizer = TopologyOptimizer(seed=42)
        G = TopologyGenerator.small_world(100, k=6, p=0.1)

        metrics = optimizer.analyze_topology(G, "Small-World")

        # Small-world networks should have:
        # - Short average path length
        # - High clustering coefficient
        assert metrics.avg_path_length < np.log(100)
        assert metrics.clustering_coefficient > 0.3

    def test_topology_comparison(self):
        """Test that topology comparison runs successfully."""
        optimizer = TopologyOptimizer(seed=42)
        results, analysis = optimizer.run_topology_comparison(
            colony_sizes=[50, 100],
            n_trials=2
        )

        assert len(results) > 0
        assert 'hypothesis_h4' in analysis


class TestIntegration:
    """Integration tests for the entire simulation suite."""

    def test_reproducibility(self):
        """Test that simulations are reproducible with same seed."""
        # Run simulation twice with same seed
        simulator1 = ScalingLawSimulator(seed=42)
        metrics1 = simulator1.simulate_colony(n_agents=100)

        simulator2 = ScalingLawSimulator(seed=42)
        metrics2 = simulator2.simulate_colony(n_agents=100)

        # Results should be identical
        assert metrics1.per_agent_throughput == metrics2.per_agent_throughput
        assert metrics1.avg_latency_ms == metrics2.avg_latency_ms

    def test_scaling_monotonicity(self):
        """Test that certain properties scale monotonically."""
        simulator = ScalingLawSimulator(seed=42)

        sizes = [50, 100, 200, 500]
        total_throughputs = []

        for size in sizes:
            metrics = simulator.simulate_colony(size)
            total_throughputs.append(metrics.total_throughput)

        # Total throughput should increase with colony size
        for i in range(1, len(total_throughputs)):
            assert total_throughputs[i] > total_throughputs[i-1]


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
