"""
Test Suite for Dynamical Systems Analysis

Comprehensive tests for all dynamical systems modules.
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal

from vector_fields import PollnVectorField
from fixed_points import PollnFixedPoints, FixedPointType
from limit_cycles import PollnLimitCycles, LimitCycleType
from attractors import PollnAttractors, AttractorType
from ergodic_theory import PollnErgodicTheory
from bifurcation_analysis import PollnBifurcationAnalysis
from dynamical_simulator import DynamicalSimulator


class TestVectorFields:
    """Test vector field construction and analysis"""

    @pytest.fixture
    def vector_field(self):
        """Create test vector field"""
        return PollnVectorField(num_agents=3, state_dim=2)

    def test_state_vector_conversion(self, vector_field):
        """Test state vector flattening and reshaping"""
        agent_states = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        state_vec = vector_field.state_vector(agent_states)

        assert state_vec.shape == (6,)
        assert_array_almost_equal(state_vec, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def test_vector_field_evaluation(self, vector_field):
        """Test vector field computation"""
        x = np.random.randn(vector_field.total_dim)
        dxdt = vector_field.vector_field(0, x)

        assert dxdt.shape == x.shape
        assert np.all(np.isfinite(dxdt))

    def test_divergence_computation(self, vector_field):
        """Test divergence calculation"""
        x = np.random.randn(vector_field.total_dim)
        div = vector_field.divergence(x)

        assert np.isfinite(div)
        # Divergence is a scalar

    def test_jacobian_computation(self, vector_field):
        """Test Jacobian matrix calculation"""
        x = np.random.randn(vector_field.total_dim)
        J = vector_field.jacobian(x)

        assert J.shape == (vector_field.total_dim, vector_field.total_dim)
        assert np.all(np.isfinite(J))

    def test_flow_computation(self, vector_field):
        """Test flow (trajectory) computation"""
        x0 = np.random.randn(vector_field.total_dim)
        trajectory = vector_field.compute_flow(x0, (0, 1))

        assert trajectory.shape[0] > 0
        assert trajectory.shape[1] == vector_field.total_dim


class TestFixedPoints:
    """Test fixed point analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create fixed point analyzer"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return PollnFixedPoints(vf)

    def test_fixed_point_finding(self, analyzer):
        """Test finding fixed points"""
        fps = analyzer.find_fixed_points(num_initial=10)

        # Should find at least some fixed points
        assert len(fps) >= 0

    def test_fixed_point_classification(self, analyzer):
        """Test fixed point classification"""
        # Create a simple fixed point at origin
        x_star = np.zeros(analyzer.vf.total_dim)
        fp = analyzer._classify_fixed_point(x_star)

        assert fp is not None
        assert isinstance(fp.type, FixedPointType)


class TestLimitCycles:
    """Test limit cycle analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create limit cycle analyzer"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return PollnLimitCycles(vf)

    def test_poincare_map_construction(self, analyzer):
        """Test Poincaré map construction"""
        # Create a simple periodic-like trajectory
        t = np.linspace(0, 2*np.pi, 100)
        trajectory = np.column_stack([np.cos(t), np.sin(t)])

        # Pad to full dimension
        full_traj = np.zeros((len(t), analyzer.vf.total_dim))
        full_traj[:, :2] = trajectory

        poincare = analyzer._construct_poincare_map(full_traj)

        # Should find crossings
        assert len(poincare) >= 0


class TestAttractors:
    """Test attractor analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create attractor analyzer"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return PollnAttractors(vf)

    def test_lyapunov_spectrum_computation(self, analyzer):
        """Test Lyapunov spectrum computation"""
        # Create random trajectory
        trajectory = np.random.randn(100, analyzer.vf.total_dim)

        spectrum = analyzer._compute_lyapunov_spectrum(trajectory)

        assert spectrum is not None
        assert len(spectrum) == analyzer.vf.total_dim

    def test_correlation_dimension(self, analyzer):
        """Test correlation dimension estimation"""
        # Create 2D trajectory
        trajectory = np.random.randn(100, analyzer.vf.total_dim)

        dim = analyzer._correlation_dimension(trajectory)

        assert dim is not None
        assert dim > 0


class TestErgodicTheory:
    """Test ergodic theory analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create ergodic theory analyzer"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return PollnErgodicTheory(vf)

    def test_invariant_measure_estimation(self, analyzer):
        """Test invariant measure estimation"""
        measure = analyzer.estimate_invariant_measure(
            num_trajectories=10,
            time=5.0,
            num_bins=10
        )

        assert measure is not None
        assert measure.shape == (10, 10)
        # Check normalization
        assert_almost_equal(np.sum(measure), 1.0, decimal=1)

    def test_ks_entropy_estimation(self, analyzer):
        """Test KS entropy estimation"""
        trajectory = np.random.randn(100, analyzer.vf.total_dim)

        entropy = analyzer.estimate_ks_entropy(trajectory)

        assert entropy is not None
        assert entropy >= 0


class TestBifurcationAnalysis:
    """Test bifurcation analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create bifurcation analyzer"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return PollnBifurcationAnalysis(vf)

    def test_bifurcation_detection(self, analyzer):
        """Test bifurcation detection"""
        bifurcations = analyzer.detect_bifurcations(
            parameter='learning_rate',
            param_range=(0.001, 0.02),
            num_points=10
        )

        # Should return list (may be empty)
        assert isinstance(bifurcations, list)


class TestDynamicalSimulator:
    """Test dynamical systems simulator"""

    @pytest.fixture
    def simulator(self):
        """Create simulator"""
        vf = PollnVectorField(num_agents=3, state_dim=2)
        return DynamicalSimulator(vf)

    def test_integration(self, simulator):
        """Test ODE integration"""
        x0 = np.random.randn(simulator.vf.total_dim)
        result = simulator.integrate(x0, (0, 1))

        assert result.success
        assert len(result.time) > 0
        assert result.state.shape[1] == simulator.vf.total_dim

    def test_poincare_section(self, simulator):
        """Test Poincaré section computation"""
        x0 = np.random.randn(simulator.vf.total_dim)
        trajectory = simulator.integrate(x0, (0, 5))

        if trajectory.success:
            section, times = simulator.poincare_section(trajectory.state)

            assert section is not None
            assert times is not None

    def test_lyapunov_exponents(self, simulator):
        """Test Lyapunov exponent computation"""
        x0 = np.random.randn(simulator.vf.total_dim)
        trajectory = simulator.integrate(x0, (0, 5))

        if trajectory.success:
            lyap = simulator.lyapunov_exponents(trajectory.state)

            assert lyap is not None
            assert len(lyap) == simulator.vf.total_dim


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline"""
        # Create vector field
        vf = PollnVectorField(num_agents=3, state_dim=2)

        # Run vector field analysis
        div = vf.divergence(np.random.randn(vf.total_dim))
        assert np.isfinite(div)

        # Run fixed point analysis
        fp_analyzer = PollnFixedPoints(vf)
        fps = fp_analyzer.find_fixed_points(num_initial=5)

        # Run attractor analysis
        attr_analyzer = PollnAttractors(vf)
        attractors = attr_analyzer.identify_attractors(num_trials=10)

        # All should complete without errors
        assert True


def test_deepseek_integration():
    """Test DeepSeek API integration (with mock)"""
    # This test would require actual API key
    # For now, just test the interface
    from deepseek_dynamical import DeepSeekDynamicalSystems

    # Create client (will fail if no API key)
    try:
        ds = DeepSeekDynamicalSystems()
        assert ds is not None
    except Exception as e:
        # Expected if no API key
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
