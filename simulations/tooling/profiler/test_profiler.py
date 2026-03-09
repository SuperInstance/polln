"""
Profiling Toolkit Tests
Comprehensive tests for all profiler components.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Any

from agent_profiler import AgentProfiler, AgentProfile
from colony_profiler import ColonyProfiler, ColonyProfile
from memory_profiler import MemoryProfiler, MemoryProfile
from trace_analyzer import TraceAnalyzer, TraceEvent, TraceAnalysis
from flame_graph_generator import FlameGraphGenerator
from optimization_recommender import OptimizationRecommender, OptimizationReport
from profile_runner import ProfileRunner
from utils.metrics import MetricsCollector, MetricType


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    def test_register_counter(self):
        """Test counter registration."""
        collector = MetricsCollector()
        collector.register_counter('test_counter', labels={'agent': 'test'})
        assert collector.get_counter('test_counter') == 0

    def test_increment_counter(self):
        """Test counter increment."""
        collector = MetricsCollector()
        collector.register_counter('test_counter')
        collector.increment_counter('test_counter', 5)
        assert collector.get_counter('test_counter') == 5

    def test_register_gauge(self):
        """Test gauge registration."""
        collector = MetricsCollector()
        collector.register_gauge('test_gauge')
        gauge = collector.get_gauge('test_gauge')
        assert gauge is not None
        assert gauge.value == 0

    def test_set_gauge(self):
        """Test setting gauge value."""
        collector = MetricsCollector()
        collector.register_gauge('test_gauge')
        collector.set_gauge('test_gauge', 42.0)
        gauge = collector.get_gauge('test_gauge')
        assert gauge.value == 42.0

    def test_histogram(self):
        """Test histogram observations."""
        collector = MetricsCollector()
        collector.register_histogram('test_hist')

        # Observe some values
        for i in range(100):
            collector.observe_histogram('test_hist', i)

        stats = collector.get_histogram_stats('test_hist')
        assert stats is not None
        assert stats['count'] == 100
        assert stats['min'] == 0
        assert stats['max'] == 99
        assert 49 <= stats['avg'] <= 51  # Should be around 50

    def test_timing(self):
        """Test timing observations."""
        collector = MetricsCollector()
        collector.register_timing('test_timing')

        # Observe some timings
        for i in range(10):
            collector.observe_timing('test_timing', 0.1 * i)

        stats = collector.get_timing_stats('test_timing')
        assert stats is not None
        assert stats['count'] == 10
        assert stats['min'] == 0
        assert stats['max'] == 0.9

    def test_export_prometheus(self):
        """Test Prometheus export format."""
        collector = MetricsCollector()
        collector.register_counter('test_counter')
        collector.increment_counter('test_counter', 42)

        exported = collector.export_prometheus()
        assert 'test_counter' in exported
        assert '42' in exported


class TestAgentProfiler:
    """Tests for AgentProfiler."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock()
        agent.id = 'test-agent-1'
        agent.typeId = 'TaskAgent'
        agent.valueFunction = 0.7
        agent.successCount = 10
        agent.failureCount = 3
        return agent

    @pytest.fixture
    def mock_workload(self):
        """Create a mock workload."""
        async def workload(agent):
            await asyncio.sleep(0.01)
            return {'result': 'success'}
        return workload

    @pytest.mark.asyncio
    async def test_profile_agent(self, mock_agent, mock_workload):
        """Test profiling an agent."""
        profiler = AgentProfiler()

        profile = await profiler.profile_agent(
            mock_agent,
            mock_workload,
            iterations=3,
            warmup_iterations=1
        )

        assert profile is not None
        assert profile.agent_id == 'test-agent-1'
        assert profile.agent_type == 'TaskAgent'
        assert profile.process_count == 3
        assert profile.total_process_time > 0
        assert profile.avg_process_time > 0

    def test_track_a2a(self):
        """Test A2A tracking."""
        profiler = AgentProfiler()

        profiler.track_a2a_send('agent-1', 1024)
        profiler.track_a2a_receive('agent-2', 1024)

        # Check that tracking works (internal state)
        assert profiler._a2a_sent['agent-1'] == 1
        assert profiler._a2a_received['agent-2'] == 1

    @pytest.mark.asyncio
    async def test_generate_report(self, mock_agent, mock_workload):
        """Test report generation."""
        profiler = AgentProfiler()

        await profiler.profile_agent(mock_agent, mock_workload, iterations=2)

        # Generate JSON report
        json_path = profiler.generate_report(format='json')
        assert 'agent_profile' in json_path

        # Generate text report
        text_path = profiler.generate_report(format='text')
        assert 'agent_profile' in text_path


class TestColonyProfiler:
    """Tests for ColonyProfiler."""

    @pytest.fixture
    def mock_colony(self):
        """Create a mock colony."""
        colony = Mock()
        colony.id = 'test-colony-1'
        colony.agents = {
            'agent-1': {'status': 'active'},
            'agent-2': {'status': 'active'},
            'agent-3': {'status': 'dormant'},
        }
        colony.config = Mock()
        colony.config.resourceBudget = Mock()
        colony.config.resourceBudget.totalCompute = 100
        colony.config.resourceBudget.totalMemory = 1000
        colony.config.resourceBudget.totalNetwork = 10000

        # Mock getStats
        colony.getStats = AsyncMock(return_value={
            'shannonDiversity': 0.8,
            'avgConnections': 3.5,
            'maxConnections': 10,
        })

        return colony

    @pytest.mark.asyncio
    async def test_start_stop_profiling(self, mock_colony):
        """Test starting and stopping profiling."""
        profiler = ColonyProfiler(sample_interval=0.1)

        await profiler.start_profiling(mock_colony)
        assert profiler._is_profiling is True

        await asyncio.sleep(0.3)  # Let it collect a few samples

        profile = await profiler.stop_profiling()
        assert profiler._is_profiling is False
        assert profile is not None
        assert profile.total_agents == 3
        assert profile.active_agents == 2

    def test_track_metrics(self):
        """Test metric tracking."""
        profiler = ColonyProfiler()

        profiler.track_request()
        profiler.track_a2a_package(1024)
        profiler.track_agent_spawn()
        profiler.track_agent_kill()
        profiler.track_topology_change()
        profiler.record_latency(0.5)
        profiler.record_queue_depth(5)

        assert profiler._request_count == 1
        assert profiler._a2a_count == 1
        assert profiler._bytes_sent == 1024
        assert profiler._agents_spawned == 1
        assert profiler._agents_killed == 1

    def test_generate_report(self, mock_colony):
        """Test report generation."""
        profiler = ColonyProfiler()

        # Manually create a profile for testing
        from colony_profiler import ColonyProfile
        profile = ColonyProfile(
            colony_id='test',
            timestamp=time.time(),
            total_agents=3,
            active_agents=2,
            dormant_agents=1,
            hibernating_agents=0,
            error_agents=0,
            total_compute=100,
            total_memory=1000,
            total_network=10000,
            avg_compute_per_agent=33.33,
            avg_memory_per_agent=333.33,
            requests_per_second=10,
            a2a_packages_per_second=5,
            bytes_per_second=1024,
            p50_latency=0.1,
            p90_latency=0.2,
            p95_latency=0.25,
            p99_latency=0.3,
            max_latency=0.35,
            avg_queue_depth=2.5,
            max_queue_depth=5,
            queue_depth_percentiles={'p50': 2, 'p90': 4, 'p95': 5},
            shannon_diversity=0.8,
            avg_connections_per_agent=3.5,
            max_connections_per_agent=10,
            agents_spawned=1,
            agents_killed=0,
            topology_changes=0,
            duration_seconds=10,
        )

        json_path = profiler.generate_report(profile, format='json')
        assert 'colony_profile' in json_path


class TestMemoryProfiler:
    """Tests for MemoryProfiler."""

    @pytest.mark.asyncio
    async def test_start_stop_profiling(self):
        """Test starting and stopping profiling."""
        profiler = MemoryProfiler(snapshot_interval=0.1)

        await profiler.start_profiling(track_allocations=False)
        assert profiler._is_profiling is True

        await asyncio.sleep(0.3)

        profile = await profiler.stop_profiling()
        assert profiler._is_profiling is False
        assert profile is not None
        assert profile.duration_seconds > 0

    def test_track_kv_cache(self):
        """Test KV-cache tracking."""
        profiler = MemoryProfiler()

        profiler.track_kv_cache_allocation(1024 * 1024)  # 1MB
        profiler.track_kv_cache_allocation(2048 * 1024)  # 2MB

        assert len(profiler._kv_cache_sizes) == 2
        assert profiler._kv_cache_sizes[-1][1] == 2048 * 1024

    def test_get_realtime_stats(self):
        """Test real-time stats."""
        profiler = MemoryProfiler()
        stats = profiler.get_realtime_stats()

        assert 'rss_bytes' in stats
        assert 'rss_mb' in stats
        assert stats['rss_mb'] > 0


class TestTraceAnalyzer:
    """Tests for TraceAnalyzer."""

    def test_add_event(self):
        """Test adding trace events."""
        analyzer = TraceAnalyzer()

        event = TraceEvent(
            timestamp=time.time(),
            event_type='send',
            agent_id='agent-1',
            package_id='pkg-1',
            causal_chain_id='chain-1',
            parent_ids=[],
        )

        analyzer.add_event(event)

        assert 'pkg-1' in analyzer._traces
        assert len(analyzer._traces['pkg-1']) == 1

    def test_analyze(self):
        """Test trace analysis."""
        analyzer = TraceAnalyzer()

        # Add some trace events
        now = time.time()
        events = [
            TraceEvent(now, 'send', 'agent-1', 'pkg-1', 'chain-1', []),
            TraceEvent(now + 0.01, 'receive', 'agent-2', 'pkg-1', 'chain-1', []),
            TraceEvent(now + 0.05, 'process_start', 'agent-2', 'pkg-1', 'chain-1', []),
            TraceEvent(now + 0.10, 'process_end', 'agent-2', 'pkg-1', 'chain-1', []),
        ]

        for event in events:
            analyzer.add_event(event)

        analysis = analyzer.analyze()

        assert analysis is not None
        assert analysis.total_traces == 1
        assert analysis.avg_trace_duration > 0


class TestFlameGraphGenerator:
    """Tests for FlameGraphGenerator."""

    def test_generate_cpu_flame_graph(self):
        """Test CPU flame graph generation."""
        generator = FlameGraphGenerator()

        profile_data = {
            'hotspots': [
                {
                    'function': 'test_function',
                    'calls': 100,
                    'total_time': 1.5,
                    'per_call': 0.015,
                    'cumulative_time': 2.0,
                }
            ]
        }

        html_path = generator.generate_cpu_flame_graph(profile_data)
        assert 'flame_graph_cpu' in html_path

    def test_generate_memory_flame_graph(self):
        """Test memory flame graph generation."""
        generator = FlameGraphGenerator()

        memory_data = [
            {
                'trace': 'test.py:10: allocate_memory',
                'size_bytes': 1024 * 1024,
                'count': 100,
            }
        ]

        html_path = generator.generate_memory_flame_graph(memory_data)
        assert 'flame_graph_memory' in html_path


class TestOptimizationRecommender:
    """Tests for OptimizationRecommender."""

    def test_add_profiles(self):
        """Test adding profiling data."""
        recommender = OptimizationRecommender()

        recommender.add_agent_profile({'hotspots': []})
        recommender.add_colony_profile({'total_agents': 10})
        recommender.add_memory_profile({'suspected_leaks': []})

        assert len(recommender._agent_profiles) == 1
        assert len(recommender._colony_profiles) == 1
        assert len(recommender._memory_profiles) == 1

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        recommender = OptimizationRecommender()

        # Add some problematic profiles
        recommender.add_agent_profile({
            'hotspots': [
                {
                    'function': 'slow_function',
                    'calls': 1000,
                    'total_time': 2.0,  # 2 seconds - critical
                }
            ]
        })

        recommender.add_memory_profile({
            'suspected_leaks': [
                {
                    'object_type': 'LargeObject',
                    'growth_rate': 5000,  # 5KB/sec
                    'total_bytes': 10 * 1024 * 1024,
                }
            ],
            'fragmentation_ratio': 0.4,
        })

        report = recommender.generate_recommendations()

        assert report is not None
        assert report.total_recommendations > 0
        assert len(report.quick_wins) + len(report.strategic_changes) > 0


class TestProfileRunner:
    """Tests for ProfileRunner."""

    @pytest.fixture
    def mock_colony(self):
        """Create a mock colony for testing."""
        colony = Mock()
        colony.agents = {}
        return colony

    @pytest.fixture
    def mock_workload(self):
        """Create a mock workload."""
        async def workload(colony):
            await asyncio.sleep(0.01)
        return workload

    @pytest.mark.asyncio
    async def test_run_benchmark(self, mock_colony, mock_workload):
        """Test benchmark running."""
        runner = ProfileRunner()

        results = await runner.run_benchmark(
            mock_colony,
            mock_workload,
            'test_benchmark',
            iterations=5
        )

        assert 'benchmark' in results
        assert results['benchmark'] == 'test_benchmark'
        assert results['iterations'] == 5
        assert results['successful'] > 0
        assert 'avg_time' in results


# Integration tests
class TestIntegration:
    """Integration tests for the full profiling toolkit."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_profiling_workflow(self):
        """Test the complete profiling workflow."""
        # Create mock agent and colony
        mock_agent = Mock()
        mock_agent.id = 'integration-test-agent'
        mock_agent.typeId = 'TaskAgent'
        mock_agent.valueFunction = 0.5
        mock_agent.successCount = 5
        mock_agent.failureCount = 1

        async def workload(agent):
            await asyncio.sleep(0.01)
            return {'result': 'ok'}

        # Run agent profiler
        agent_profiler = AgentProfiler()
        agent_profile = await agent_profiler.profile_agent(
            mock_agent,
            workload,
            iterations=3
        )
        assert agent_profile is not None

        # Run memory profiler
        memory_profiler = MemoryProfiler()
        await memory_profiler.start_profiling(track_allocations=False)
        await asyncio.sleep(0.2)
        memory_profile = await memory_profiler.stop_profiling()
        assert memory_profile is not None

        # Run trace analyzer
        trace_analyzer = TraceAnalyzer()
        event = TraceEvent(
            timestamp=time.time(),
            event_type='send',
            agent_id='agent-1',
            package_id='pkg-1',
            causal_chain_id='chain-1',
        )
        trace_analyzer.add_event(event)
        trace_analysis = trace_analyzer.analyze()
        assert trace_analysis is not None

        # Generate recommendations
        recommender = OptimizationRecommender()
        recommender.add_agent_profile({
            'hotspots': agent_profile.hotspots
        })
        recommender.add_memory_profile({
            'suspected_leaks': memory_profile.suspected_leaks
        })
        recommendations = recommender.generate_recommendations()
        assert recommendations is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
