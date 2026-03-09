"""
Tests for Topology Optimization System

Comprehensive tests for topology generation, evaluation, and optimization.
"""

import pytest
import networkx as nx
import numpy as np
from typing import Dict, List

from topology_generator import (
    TopologyGenerator, TopologyType, TopologyParams,
    generate_benchmark_topologies
)
from topology_evaluator import TopologyEvaluator, TopologyMetrics
from workload_modeling import (
    WorkloadGenerator, WorkloadConfig,
    generate_benchmark_workloads, TrafficPattern, CommunicationPattern
)
from topology_optimizer import (
    TopologyOptimizer, OptimizationResult,
    ScenarioOptimizer, optimize_for_colony_sizes
)
from template_generator import (
    TemplateGenerator, TopologyTemplate,
    generate_default_templates
)


class TestTopologyGenerator:
    """Tests for topology generation."""

    def test_initialization(self):
        """Test generator initialization."""
        gen = TopologyGenerator(seed=42)
        assert gen.seed == 42

    def test_erdos_renyi_generation(self):
        """Test Erdős-Rényi graph generation."""
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=50, p=0.1, seed=42)
        G = gen.generate(TopologyType.ERDOS_RENYI, params)

        assert G.number_of_nodes() == 50
        assert G.number_of_edges() > 0
        assert isinstance(G, nx.Graph)

    def test_watts_strogatz_generation(self):
        """Test Watts-Strogatz graph generation."""
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=50, k=6, p=0.1, seed=42)
        G = gen.generate(TopologyType.WATTS_STROGATZ, params)

        assert G.number_of_nodes() == 50
        assert G.number_of_edges() > 0
        # All nodes should have similar degree in WS
        degrees = [d for n, d in G.degree()]
        assert np.std(degrees) < 3  # Low std dev

    def test_barabasi_albert_generation(self):
        """Test Barabási-Albert graph generation."""
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=50, m=3, seed=42)
        G = gen.generate(TopologyType.BARABASI_ALBERT, params)

        assert G.number_of_nodes() == 50
        assert G.number_of_edges() > 0
        # Should have some high-degree nodes (hubs)
        degrees = [d for n, d in G.degree()]
        assert max(degrees) > np.mean(degrees) * 2

    def test_modular_generation(self):
        """Test modular graph generation."""
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=50, modules=5, seed=42)
        G = gen.generate(TopologyType.MODULAR, params)

        assert G.number_of_nodes() == 50
        assert G.number_of_edges() > 0

    def test_hierarchical_generation(self):
        """Test hierarchical graph generation."""
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=50, levels=3, seed=42)
        G = gen.generate(TopologyType.HIERARCHICAL, params)

        assert G.number_of_nodes() == 50
        assert G.number_of_edges() > 0

    def test_export_graphml(self):
        """Test GraphML export."""
        import tempfile
        import os

        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=20, p=0.3, seed=42)
        G = gen.generate(TopologyType.ERDOS_RENYI, params)

        with tempfile.NamedTemporaryFile(suffix='.graphml', delete=False) as f:
            filepath = f.name

        try:
            gen.export_graphml(G, filepath)
            assert os.path.exists(filepath)

            # Load and verify
            G_loaded = nx.read_graphml(filepath, node_type=int)
            assert G_loaded.number_of_nodes() == G.number_of_nodes()
            assert G_loaded.number_of_edges() == G.number_of_edges()
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_export_json(self):
        """Test JSON export."""
        import tempfile
        import os

        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=20, p=0.3, seed=42)
        G = gen.generate(TopologyType.ERDOS_RENYI, params)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            gen.export_json(G, filepath, TopologyType.ERDOS_RENYI, params)
            assert os.path.exists(filepath)

            # Load and verify
            G_loaded, topo_type, params_loaded = gen.load_json(filepath)
            assert topo_type == TopologyType.ERDOS_RENYI
            assert G_loaded.number_of_nodes() == G.number_of_nodes()
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_benchmark_topologies(self):
        """Test benchmark topology generation."""
        topologies = generate_benchmark_topologies(50, seed=42)

        assert len(topologies) > 0
        assert 'watts_strogatz' in topologies
        assert 'barabasi_albert' in topologies

        for name, (G, topo_type, params) in topologies.items():
            assert G.number_of_nodes() == 50
            assert isinstance(topo_type, TopologyType)


class TestTopologyEvaluator:
    """Tests for topology evaluation."""

    def test_initialization(self):
        """Test evaluator initialization."""
        eval = TopologyEvaluator(parallel=False)
        assert eval.parallel == False

    def test_basic_properties(self):
        """Test basic property calculation."""
        G = nx.complete_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        assert metrics.num_nodes == 10
        assert metrics.num_edges == 45
        assert metrics.avg_degree == 9
        assert metrics.density == 1.0

    def test_path_metrics(self):
        """Test path metric calculation."""
        G = nx.path_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        assert metrics.avg_path_length > 0
        assert metrics.diameter == 9

    def test_clustering_metrics(self):
        """Test clustering metric calculation."""
        # Complete graph has clustering = 1
        G = nx.complete_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        assert metrics.clustering_coefficient == 1.0
        assert metrics.transitivity == 1.0

    def test_efficiency_metrics(self):
        """Test efficiency metric calculation."""
        G = nx.complete_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        # Complete graph has maximum efficiency
        assert metrics.global_efficiency == 1.0

    def test_robustness_metrics(self):
        """Test robustness metric calculation."""
        G = nx.complete_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        # Complete graph is very robust
        assert metrics.attack_tolerance > 0.5
        assert metrics.failure_tolerance > 0.5

    def test_score_calculation(self):
        """Test score calculation."""
        G = nx.complete_graph(10)
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        score = eval.calculate_score(metrics)
        assert 0 <= score <= 1


class TestWorkloadModeling:
    """Tests for workload modeling."""

    def test_workload_generator_initialization(self):
        """Test workload generator initialization."""
        G = nx.complete_graph(10)
        gen = WorkloadGenerator(G, seed=42)
        assert gen.G.number_of_nodes() == 10

    def test_uniform_traffic(self):
        """Test uniform traffic generation."""
        G = nx.complete_graph(10)
        gen = WorkloadGenerator(G, seed=42)

        config = WorkloadConfig(
            num_requests=100,
            traffic_pattern=TrafficPattern.UNIFORM,
            communication_pattern=CommunicationPattern.POINT_TO_POINT
        )

        requests = gen.generate(config)
        assert len(requests) == 100

        # Check traffic is distributed
        sources = [r.source for r in requests]
        assert len(set(sources)) > 5  # Multiple sources

    def test_hotspot_traffic(self):
        """Test hotspot traffic generation."""
        G = nx.complete_graph(10)
        gen = WorkloadGenerator(G, seed=42)

        config = WorkloadConfig(
            num_requests=100,
            traffic_pattern=TrafficPattern.HOTSPOT,
            communication_pattern=CommunicationPattern.POINT_TO_POINT,
            hotspot_ratio=0.2
        )

        requests = gen.generate(config)
        assert len(requests) == 100

    def test_broadcast_traffic(self):
        """Test broadcast traffic generation."""
        G = nx.complete_graph(10)
        gen = WorkloadGenerator(G, seed=42)

        config = WorkloadConfig(
            num_requests=50,
            communication_pattern=CommunicationPattern.BROADCAST
        )

        requests = gen.generate(config)
        assert len(requests) > 0

        # All requests should be broadcasts
        for req in requests:
            assert req.pattern == CommunicationPattern.BROADCAST

    def test_gossip_traffic(self):
        """Test gossip traffic generation."""
        G = nx.watts_strogatz_graph(20, 4, 0.1)
        gen = WorkloadGenerator(G, seed=42)

        config = WorkloadConfig(
            num_requests=100,
            communication_pattern=CommunicationPattern.GOSSIP
        )

        requests = gen.generate(config)
        assert len(requests) > 0

    def test_bursty_temporal_pattern(self):
        """Test bursty temporal pattern."""
        G = nx.complete_graph(10)
        gen = WorkloadGenerator(G, seed=42)

        config = WorkloadConfig(
            num_requests=100,
            temporal_pattern='bursty',
            burst_prob=0.2,
            burst_size=10
        )

        requests = gen.generate(config)
        assert len(requests) == 100

    def test_benchmark_workloads(self):
        """Test benchmark workload generation."""
        configs = generate_benchmark_workloads()

        assert len(configs) > 0
        assert 'uniform_point_to_point' in configs
        assert 'hotspot_aggregation' in configs


class TestTopologyOptimizer:
    """Tests for topology optimization."""

    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        from workload_modeling import generate_benchmark_workloads

        configs = generate_benchmark_workloads()
        config = list(configs.values())[0]

        optimizer = TopologyOptimizer(
            colony_size=50,
            workload_config=config,
            seed=42
        )

        assert optimizer.colony_size == 50
        assert optimizer.workload_config == config

    def test_optimization(self):
        """Test topology optimization."""
        from workload_modeling import generate_benchmark_workloads

        configs = generate_benchmark_workloads()
        config = configs['uniform_point_to_point']

        optimizer = TopologyOptimizer(
            colony_size=30,
            workload_config=config,
            seed=42
        )

        results = optimizer.optimize(iterations=5)

        assert len(results) > 0
        assert all(isinstance(r, OptimizationResult) for r in results)

        # Check results are sorted by score
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_pareto_frontier(self):
        """Test Pareto frontier extraction."""
        from workload_modeling import generate_benchmark_workloads

        configs = generate_benchmark_workloads()
        config = configs['uniform_point_to_point']

        optimizer = TopologyOptimizer(
            colony_size=30,
            workload_config=config,
            seed=42
        )

        results = optimizer.optimize(iterations=5)
        pareto = optimizer.find_pareto_frontier(results)

        assert len(pareto) >= 1
        assert all(r.pareto_rank == 0 for r in pareto)


class TestScenarioOptimizer:
    """Tests for scenario optimization."""

    def test_scenario_optimizer_initialization(self):
        """Test scenario optimizer initialization."""
        from workload_modeling import generate_benchmark_workloads

        configs = generate_benchmark_workloads()

        optimizer = ScenarioOptimizer(
            colony_sizes=[10, 20],
            workload_configs=configs,
            seed=42
        )

        assert optimizer.colony_sizes == [10, 20]
        assert len(optimizer.workload_configs) > 0

    def test_scenario_optimization(self):
        """Test multi-scenario optimization."""
        from workload_modeling import generate_benchmark_workloads

        configs = {
            'test': WorkloadConfig(
                num_requests=50,
                traffic_pattern=TrafficPattern.UNIFORM,
                communication_pattern=CommunicationPattern.POINT_TO_POINT
            )
        }

        optimizer = ScenarioOptimizer(
            colony_sizes=[10, 20],
            workload_configs=configs,
            seed=42
        )

        results = optimizer.optimize_all_scenarios(iterations_per_scenario=3)

        assert len(results) > 0

        # Check each scenario has results
        for size in [10, 20]:
            for workload in configs.keys():
                key = f"{size}_{workload}"
                if key in results:
                    assert len(results[key]) >= 0


class TestTemplateGenerator:
    """Tests for template generation."""

    def test_template_generator_initialization(self):
        """Test template generator initialization."""
        gen = TemplateGenerator()
        assert len(gen.templates) == 0

    def test_generate_default_templates(self):
        """Test default template generation."""
        templates = generate_default_templates()

        assert len(templates) > 0
        assert 'SMALL_COLONY' in templates
        assert 'MEDIUM_COLONY' in templates
        assert 'LARGE_COLONY' in templates

        # Check template structure
        for name, template in templates.items():
            assert isinstance(template, TopologyTemplate)
            assert template.name
            assert template.description
            assert template.topology_type
            assert template.expected_metrics

    def test_template_characteristics(self):
        """Test template characteristics inference."""
        templates = generate_default_templates()

        for template in templates.values():
            # Check characteristics are valid
            assert template.characteristics['network_type'] in ['small_world', 'scale_free', 'community', 'random']
            assert template.characteristics['efficiency'] in ['high', 'medium', 'low']
            assert template.characteristics['robustness'] in ['high', 'medium', 'low']
            assert template.characteristics['cost'] in ['high', 'medium', 'low']


class TestIntegration:
    """Integration tests."""

    def test_full_pipeline_small(self):
        """Test full pipeline with small topology."""
        # Generate
        gen = TopologyGenerator(seed=42)
        params = TopologyParams(n=20, k=4, p=0.1, seed=42)
        G = gen.generate(TopologyType.WATTS_STROGATZ, params)

        # Evaluate
        eval = TopologyEvaluator(parallel=False)
        metrics = eval.evaluate(G)

        # Check metrics are reasonable
        assert metrics.num_nodes == 20
        assert metrics.avg_path_length > 0
        assert 0 <= metrics.clustering_coefficient <= 1
        assert 0 <= metrics.global_efficiency <= 1

    def test_topology_comparison(self):
        """Test comparing multiple topologies."""
        gen = TopologyGenerator(seed=42)
        eval = TopologyEvaluator(parallel=False)

        topologies = []
        for topo_type in [TopologyType.ERDOS_RENYI, TopologyType.WATTS_STROGATZ]:
            params = TopologyParams(n=30, seed=42)
            if topo_type == TopologyType.WATTS_STROGATZ:
                params = TopologyParams(n=30, k=4, p=0.1, seed=42)

            G = gen.generate(topo_type, params)
            metrics = eval.evaluate(G)
            score = eval.calculate_score(metrics)

            topologies.append((topo_type.value, score))

        assert len(topologies) == 2
        assert all(isinstance(score, float) for _, score in topologies)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
