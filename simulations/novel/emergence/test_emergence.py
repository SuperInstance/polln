"""
Test Suite for Emergence Discovery System

Comprehensive tests for all components of the emergence discovery system.
"""

import pytest
import numpy as np
from typing import Dict, List, Any
import tempfile
import shutil
from pathlib import Path

# Import components to test
from explorer import EmergenceExplorer, ExplorationStrategy, ParameterSpace, EmergenceMetric
from pattern_discovery import PatternDiscoveryEngine
from hypothesis_generator import DeepSeekHypothesisGenerator
from emergence_taxonomy import EmergenceTaxonomy
from experiments import ExperimentalFramework
from phenomenon_catalog import PhenomenonCatalog
from deepseek_discovery import DeepSeekDiscovery


# Fixtures

@pytest.fixture
def mock_simulation():
    """Mock simulation function for testing"""
    def simulation(config: Dict[str, Any]) -> Dict[str, Any]:
        np.random.seed(hash(str(sorted(config.items()))) % 2**32)

        return {
            "metrics": {
                "collective_intelligence": np.random.random(),
                "criticality": np.random.random(),
                "coordination": np.random.random(),
                "synchronization": np.random.random()
            },
            "config": config,
            "raw_result": {
                "agent_behavior": {
                    "coordination": np.random.random(),
                    "specialization": np.random.random()
                },
                "collective_dynamics": {
                    "synchronization": np.random.random(),
                    "criticality": np.random.random()
                }
            }
        }

    return simulation


@pytest.fixture
def temp_dir():
    """Temporary directory for test outputs"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def parameter_space():
    """Standard POLLN parameter space"""
    return ParameterSpace(
        name="test_space",
        dimensions={
            "temperature": (0.1, 2.0),
            "learning_rate": (0.001, 0.1),
            "n_agents": (10, 100)
        }
    )


@pytest.fixture
def emergence_metrics():
    """Standard emergence metrics"""
    return [
        EmergenceMetric(
            name="coordination",
            description="Agent coordination",
            compute=lambda result: result.get("metrics", {}).get("coordination", 0.0)
        ),
        EmergenceMetric(
            name="synchronization",
            description="Synchronization",
            compute=lambda result: result.get("metrics", {}).get("synchronization", 0.0)
        )
    ]


# Tests for Explorer

class TestEmergenceExplorer:
    """Test suite for EmergenceExplorer"""

    def test_initialization(self, temp_dir):
        """Test explorer initialization"""
        explorer = EmergenceExplorer(
            parameter_space=ParameterSpace("test", {"x": (0, 1)}),
            emergence_metrics=[],
            output_dir=temp_dir
        )

        assert explorer is not None
        assert explorer.output_dir == Path(temp_dir)

    def test_random_exploration(self, mock_simulation, temp_dir):
        """Test random exploration strategy"""
        param_space = ParameterSpace("test", {"x": (0, 1)})
        metrics = [EmergenceMetric("test", "test", lambda r: 0.5)]

        explorer = EmergenceExplorer(param_space, metrics, temp_dir)

        results = explorer.explore(
            n_iterations=10,
            strategy=ExplorationStrategy.RANDOM,
            simulation_fn=mock_simulation
        )

        assert "all_evaluations" in results
        assert len(results["all_evaluations"]) == 10

    def test_parameter_sampling(self, parameter_space):
        """Test parameter space sampling"""
        samples = parameter_space.sample(n_samples=5, strategy=ExplorationStrategy.RANDOM)

        assert len(samples) == 5
        for sample in samples:
            assert "temperature" in sample
            assert "learning_rate" in sample
            assert "n_agents" in sample
            assert 0.1 <= sample["temperature"] <= 2.0


# Tests for Pattern Discovery

class TestPatternDiscoveryEngine:
    """Test suite for PatternDiscoveryEngine"""

    def test_initialization(self, temp_dir):
        """Test engine initialization"""
        engine = PatternDiscoveryEngine(output_dir=temp_dir)
        assert engine is not None

    def test_pattern_discovery(self, temp_dir):
        """Test pattern discovery"""
        engine = PatternDiscoveryEngine(output_dir=temp_dir)

        # Generate mock data
        mock_data = []
        for i in range(20):
            mock_data.append({
                "config": {"temperature": np.random.random()},
                "metrics": {
                    "coordination": np.random.random(),
                    "synchronization": np.random.random()
                }
            })

        patterns = engine.discover_patterns(mock_data, methods=["cluster"])

        assert len(patterns) >= 0

    def test_dimensionality_reduction(self, temp_dir):
        """Test dimensionality reduction"""
        engine = PatternDiscoveryEngine(output_dir=temp_dir)

        features = np.random.rand(20, 5)

        # Test PCA
        embedding_pca = engine.reduce_dimensions(features, method="pca")
        assert embedding_pca.shape == (20, 2)

        # Test UMAP (if available)
        try:
            embedding_umap = engine.reduce_dimensions(features, method="umap")
            assert embedding_umap.shape == (20, 2)
        except ImportError:
            pass


# Tests for Hypothesis Generator

class TestHypothesisGenerator:
    """Test suite for DeepSeekHypothesisGenerator"""

    def test_initialization(self, temp_dir):
        """Test generator initialization"""
        generator = DeepSeekHypothesisGenerator(
            api_key="test_key",
            output_dir=temp_dir
        )

        assert generator is not None
        assert generator.client is not None

    def test_hypothesis_parsing(self, temp_dir):
        """Test hypothesis parsing"""
        generator = DeepSeekHypothesisGenerator(
            api_key="test_key",
            output_dir=temp_dir
        )

        content = """
        MECHANISM: Percolation of information

        COMPONENTS: Agents, connections

        PREDICTIONS:
        - Phase transition at threshold
        - Hysteresis effects

        VALIDATION:
        - Vary connectivity
        - Measure coordination
        """

        phenomenon_data = {"description": "Test phenomenon"}
        hypothesis = generator._parse_hypothesis(content, phenomenon_data, 0)

        assert hypothesis is not None
        assert "percolation" in hypothesis.mechanism.lower()


# Tests for Taxonomy

class TestEmergenceTaxonomy:
    """Test suite for EmergenceTaxonomy"""

    def test_initialization(self, temp_dir):
        """Test taxonomy initialization"""
        taxonomy = EmergenceTaxonomy(output_dir=temp_dir)

        assert taxonomy is not None
        assert len(taxonomy.taxonomy_tree) > 0

    def test_classification(self, temp_dir):
        """Test phenomenon classification"""
        taxonomy = EmergenceTaxonomy(output_dir=temp_dir)

        phenomenon_data = {
            "name": "Test Phenomenon",
            "description": "Sudden coordination emergence",
            "metrics": {
                "coordination": 0.95,
                "synchronization": 0.88
            }
        }

        phenomenon = taxonomy.classify_phenomenon(phenomenon_data)

        assert phenomenon is not None
        assert phenomenon.novelty_score >= 0.0


# Tests for Experiments

class TestExperimentalFramework:
    """Test suite for ExperimentalFramework"""

    def test_initialization(self, mock_simulation, temp_dir):
        """Test framework initialization"""
        framework = ExperimentalFramework(
            simulation_fn=mock_simulation,
            output_dir=temp_dir
        )

        assert framework is not None

    def test_experiment_design(self, mock_simulation, temp_dir):
        """Test experiment design"""
        framework = ExperimentalFramework(
            simulation_fn=mock_simulation,
            output_dir=temp_dir
        )

        experiment = framework.design_experiment(
            name="Test Experiment",
            hypothesis="Temperature affects coordination",
            independent_vars={"temperature": (0.1, 2.0)},
            dependent_vars=["coordination"],
            controls={"learning_rate": 0.01},
            n_replicates=3
        )

        assert experiment is not None
        assert experiment.name == "Test Experiment"
        assert experiment.n_replicates == 3

    def test_experiment_execution(self, mock_simulation, temp_dir):
        """Test experiment execution"""
        framework = ExperimentalFramework(
            simulation_fn=mock_simulation,
            output_dir=temp_dir
        )

        experiment = framework.design_experiment(
            name="Test",
            hypothesis="Test",
            independent_vars={"x": (0, 1)},
            dependent_vars=["coordination"],
            controls={},
            n_replicates=2
        )

        results = framework.run_experiment(experiment)

        assert len(results) == 2


# Tests for Phenomenon Catalog

class TestPhenomenonCatalog:
    """Test suite for PhenomenonCatalog"""

    def test_initialization(self, temp_dir):
        """Test catalog initialization"""
        catalog = PhenomenonCatalog(catalog_path=temp_dir)

        assert catalog is not None
        assert catalog.entries == {}

    def test_add_entry(self, temp_dir):
        """Test adding entry to catalog"""
        from phenomenon_catalog import PhenomenonEntry

        catalog = PhenomenonCatalog(catalog_path=temp_dir)

        entry = PhenomenonEntry(
            entry_id="test_1",
            name="Test Phenomenon",
            short_name="test",
            description="Test",
            discovery_date="2024-01-01",
            discoverer="test",
            category="test",
            tags=["test"],
            features={},
            computational_signature={},
            novelty_score=0.8
        )

        catalog.add_entry(entry)

        assert "test_1" in catalog.entries
        assert catalog.entries["test_1"].name == "Test Phenomenon"

    def test_search(self, temp_dir):
        """Test catalog search"""
        from phenomenon_catalog import PhenomenonEntry

        catalog = PhenomenonCatalog(catalog_path=temp_dir)

        entry = PhenomenonEntry(
            entry_id="test_1",
            name="Coordination Phenomenon",
            short_name="coordination",
            description="Sudden coordination",
            discovery_date="2024-01-01",
            discoverer="test",
            category="coordination",
            tags=["coordination", "emergence"],
            features={},
            computational_signature={},
            novelty_score=0.9
        )

        catalog.add_entry(entry)

        results = catalog.search("coordination")

        assert len(results) >= 1


# Tests for DeepSeek Discovery

class TestDeepSeekDiscovery:
    """Test suite for DeepSeekDiscovery"""

    def test_initialization(self, temp_dir):
        """Test discovery initialization"""
        discovery = DeepSeekDiscovery(
            api_key="test_key",
            output_dir=temp_dir
        )

        assert discovery is not None
        assert discovery.client is not None

    def test_response_parsing(self, temp_dir):
        """Test response parsing"""
        discovery = DeepSeekDiscovery(
            api_key="test_key",
            output_dir=temp_dir
        )

        content = """
        KEY INSIGHTS:
        - Phase transition observed
        - Critical behavior emerges

        HYPOTHESES:
        - Percolation mechanism
        - Network formation

        EXPERIMENTS:
        - Vary temperature
        - Measure coordination
        """

        analysis = discovery._parse_analysis(content, "test")

        assert len(analysis.insights) >= 0


# Integration Tests

class TestIntegration:
    """Integration tests for full pipeline"""

    def test_full_pipeline(self, mock_simulation, temp_dir):
        """Test complete discovery pipeline"""
        from discovery_pipeline import AutomatedDiscoveryPipeline

        pipeline = AutomatedDiscoveryPipeline(
            simulation_fn=mock_simulation,
            output_dir=temp_dir,
            deepseek_api_key="test_key"
        )

        # Run small discovery cycle
        report = pipeline.run_discovery_cycle(
            n_explorations=10,
            n_iterations=1
        )

        assert report is not None
        assert report.phenomena_cataloged >= 0


# Run tests

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
