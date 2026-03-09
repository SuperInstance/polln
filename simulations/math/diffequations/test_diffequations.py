"""
Test Suite for POLLN Differential Equations Simulations

Comprehensive tests for all PDE/SDE solvers and numerical methods.
"""

import pytest
import numpy as np
import numpy.testing as npt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulations.math.diffequations import (
    fokker_planck,
    information_fluid,
    reaction_diffusion,
    hjb_optimal_control,
    stochastic_dynamics,
    pde_solver
)


class TestFokkerPlanck:
    """Tests for Fokker-Planck solver"""

    def test_initialization(self):
        """Test solver initialization"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=10.0,
            grid_points=100,
            dt=0.01
        )
        assert solver.state_dim == 1
        assert solver.N == 100
        assert solver.dt == 0.01

    def test_gaussian_initialization(self):
        """Test Gaussian initialization"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=100
        )
        solver.initialize_gaussian(mean=0.0, std=1.0)

        # Check normalization
        total = np.trapz(solver.rho, solver.x)
        npt.assert_almost_equal(total, 1.0, decimal=5)

    def test_single_time_step(self):
        """Test single time step"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=50
        )
        solver.initialize_gaussian()
        solver.step(method="forward_euler")

        # Check probability is conserved
        total = np.trapz(solver.rho, solver.x)
        npt.assert_almost_equal(total, 1.0, decimal=3)

    def test_crank_nicolson_stability(self):
        """Test Crank-Nicolson stability"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=50,
            dt=0.1  # Large time step
        )
        solver.initialize_gaussian()

        # Should not blow up
        for _ in range(10):
            solver.step(method="crank_nicolson")

        assert np.all(np.isfinite(solver.rho))
        assert np.all(solver.rho >= 0)

    def test_stationary_distribution(self):
        """Test stationary distribution computation"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=100
        )
        solver.initialize_gaussian()

        rho_star = solver.compute_stationary_distribution(tol=1e-3, max_iter=100)

        # Check it's normalized
        total = np.trapz(rho_star, solver.x)
        npt.assert_almost_equal(total, 1.0, decimal=3)

        # Check it's non-negative
        assert np.all(rho_star >= 0)


class TestInformationFluid:
    """Tests for information fluid dynamics solver"""

    def test_initialization(self):
        """Test solver initialization"""
        solver = information_fluid.InformationFluidSolver(
            domain_size=1.0,
            grid_points=32,
            viscosity=0.01,
            dt=0.001
        )
        assert solver.N == 32
        assert solver.nu == 0.01

    def test_source_initialization(self):
        """Test information source initialization"""
        solver = information_fluid.InformationFluidSolver(
            domain_size=1.0,
            grid_points=32
        )
        solver.initialize_source(x0=0.5, y0=0.5, radius=0.1)

        # Check total information is finite
        assert np.all(np.isfinite(solver.rho))

    def test_reynolds_number(self):
        """Test Reynolds number computation"""
        solver = information_fluid.InformationFluidSolver(
            domain_size=1.0,
            grid_points=32,
            viscosity=0.01
        )
        solver.initialize_source(0.5, 0.5)
        solver.initialize_velocity_field("uniform")

        Re = solver.compute_reynolds_number()
        assert Re >= 0
        assert np.isfinite(Re)

    def test_flow_regime_detection(self):
        """Test flow regime detection"""
        solver = information_fluid.InformationFluidSolver(
            domain_size=1.0,
            grid_points=32,
            viscosity=0.01
        )
        solver.initialize_source(0.5, 0.5)
        solver.initialize_velocity_field("uniform")

        regime = solver.get_flow_regime()
        assert isinstance(regime, str)

    def test_single_time_step(self):
        """Test single time step"""
        solver = information_fluid.InformationFluidSolver(
            domain_size=1.0,
            grid_points=32,
            dt=0.001
        )
        solver.initialize_source(0.5, 0.5)
        solver.initialize_velocity_field("uniform")

        solver.step()

        # Check fields are finite
        assert np.all(np.isfinite(solver.u))
        assert np.all(np.isfinite(solver.v))
        assert np.all(np.isfinite(solver.rho))


class TestReactionDiffusion:
    """Tests for reaction-diffusion solver"""

    def test_initialization(self):
        """Test solver initialization"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=100.0,
            grid_points=64,
            dt=0.1,
            Du=1.0,
            Dv=40.0
        )
        assert solver.N == 64
        assert solver.Du == 1.0
        assert solver.Dv == 40.0

    def test_random_initialization(self):
        """Test random initialization"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=100.0,
            grid_points=64
        )
        solver.initialize_random(noise_level=0.01)

        # Check concentrations are non-negative
        assert np.all(solver.u >= 0)
        assert np.all(solver.v >= 0)

    def test_reaction_kinetics(self):
        """Test reaction rate computation"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=100.0,
            grid_points=32
        )
        solver.initialize_random()

        f, g = solver.reaction_rate(solver.u, solver.v)

        assert f.shape == solver.u.shape
        assert g.shape == solver.v.shape
        assert np.all(np.isfinite(f))
        assert np.all(np.isfinite(g))

    def test_linear_stability_analysis(self):
        """Test linear stability analysis"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=100.0,
            grid_points=64
        )
        solver.initialize_random()

        stability = solver.linear_stability_analysis()

        # Check required keys
        assert 'steady_state' in stability
        assert 'max_growth_rate' in stability
        assert 'is_unstable' in stability
        assert 'turing_instability' in stability

    def test_single_time_step(self):
        """Test single time step"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=100.0,
            grid_points=32
        )
        solver.initialize_random()

        solver.step(method="euler")

        # Check concentrations remain non-negative
        assert np.all(solver.u >= 0)
        assert np.all(solver.v >= 0)


class TestHJB:
    """Tests for HJB solver"""

    def test_initialization(self):
        """Test solver initialization"""
        solver = hjb_optimal_control.HJBSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=100,
            dt=0.01,
            discount=0.95
        )
        assert solver.N == 100
        assert solver.gamma == 0.95

    def test_hamiltonian(self):
        """Test Hamiltonian computation"""
        solver = hjb_optimal_control.HJBSolver(
            state_dim=1,
            domain_size=5.0,
            grid_points=50
        )

        x = np.array([0.5])
        p = np.array([0.1])

        H, u_star = solver.hamiltonian(x, p)

        assert np.isfinite(H)
        assert np.isfinite(u_star)

    def test_value_iteration(self):
        """Test value iteration"""
        solver = hjb_optimal_control.HJBSolver(
            state_dim=1,
            domain_size=3.0,
            grid_points=30
        )

        solver.solve_value_iteration(max_iter=10, tol=1e-2)

        # Check value function is finite
        assert np.all(np.isfinite(solver.V))

    def test_trajectory_simulation(self):
        """Test trajectory simulation"""
        solver = hjb_optimal_control.HJBSolver(
            state_dim=1,
            domain_size=3.0,
            grid_points=30
        )
        solver.solve_value_iteration(max_iter=10)

        states, controls = solver.simulate_trajectory(x0=1.0, T=1.0)

        assert len(states) > 0
        assert len(controls) > 0
        assert np.all(np.isfinite(states))
        assert np.all(np.isfinite(controls))


class TestStochasticDynamics:
    """Tests for stochastic dynamics solver"""

    def test_integrator_initialization(self):
        """Test SDE integrator initialization"""
        integrator = stochastic_dynamics.SDEIntegrator(dim=1, dt=0.01)
        assert integrator.dim == 1
        assert integrator.dt == 0.01

    def test_euler_maruyama(self):
        """Test Euler-Maruyama integration"""
        integrator = stochastic_dynamics.SDEIntegrator(dim=1, dt=0.01)
        x0 = np.array([1.0])

        states, time = integrator.euler_maruyama(x0, T=1.0, interpretation="ito")

        assert len(states) > 0
        assert len(time) > 0
        assert np.all(np.isfinite(states))

    def test_milstein(self):
        """Test Milstein integration"""
        integrator = stochastic_dynamics.SDEIntegrator(dim=1, dt=0.01)
        x0 = np.array([1.0])

        states, time = integrator.milstein(x0, T=1.0, interpretation="ito")

        assert len(states) > 0
        assert np.all(np.isfinite(states))

    def test_ensemble_simulation(self):
        """Test ensemble simulation"""
        integrator = stochastic_dynamics.SDEIntegrator(dim=1, dt=0.01)
        x0 = np.array([1.0])

        all_states, time = integrator.run_ensemble(
            x0, T=1.0, n_trajectories=10,
            method="euler_maruyama"
        )

        assert all_states.shape[1] == 10
        assert np.all(np.isfinite(all_states))

    def test_exit_time_solver(self):
        """Test exit time solver"""
        solver = stochastic_dynamics.ExitTimeSolver(
            lower_bound=-3.0,
            upper_bound=3.0
        )

        exit_time, boundary = solver.simulate_exit_time(x0=0.0, dt=0.001)

        assert exit_time > 0
        assert boundary in ['lower', 'upper', 'none']


class TestPDESolver:
    """Tests for general PDE solver"""

    def test_heat_equation(self):
        """Test heat equation solver"""
        def ic(x):
            return np.exp(-x**2 / 0.1)

        solver, solution = pde_solver.solve_pde(
            pde_type='heat',
            domain_bounds=(-5, 5),
            grid_points=100,
            dt=0.001,
            n_steps=100,
            initial_condition=ic,
            alpha=1.0
        )

        assert np.all(np.isfinite(solution))
        assert solver.time > 0

    def test_advection_equation(self):
        """Test advection equation solver"""
        def ic(x):
            return np.exp(-x**2 / 0.1)

        solver, solution = pde_solver.solve_pde(
            pde_type='advection',
            domain_bounds=(0, 10),
            grid_points=100,
            dt=0.01,
            n_steps=50,
            initial_condition=ic,
            velocity=1.0
        )

        assert np.all(np.isfinite(solution))

    def test_laplacian(self):
        """Test Laplacian computation"""
        solver = pde_solver.PDESolver(
            domain_bounds=(-1, 1),
            grid_points=50,
            dt=0.01
        )

        def ic(x):
            return np.sin(np.pi * x)

        solver.initial_condition(ic)
        lap = solver.laplacian(solver.u)

        # For sin(πx), Laplacian should be -π²sin(πx)
        expected = -np.pi**2 * np.sin(np.pi * solver.X)
        npt.assert_allclose(lap[1:-1], expected[1:-1], rtol=0.1)

    def test_gradient(self):
        """Test gradient computation"""
        solver = pde_solver.PDESolver(
            domain_bounds=(0, 1),
            grid_points=50,
            dt=0.01
        )

        def ic(x):
            return x**2

        solver.initial_condition(ic)
        grad = solver.gradient(solver.u)

        # For x², gradient should be 2x
        expected = 2 * solver.X
        npt.assert_allclose(grad[0][1:-1], expected[1:-1], rtol=0.1)


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_fokker_planck_workflow(self):
        """Test complete Fokker-Planck workflow"""
        solver = fokker_planck.FokkerPlanckSolver(
            state_dim=1,
            domain_size=3.0,
            grid_points=50,
            dt=0.01
        )

        solver.initialize_gaussian(mean=0.0, std=0.5)

        # Evolve
        for _ in range(50):
            solver.step(method="crank_nicolson")

        # Compute statistics
        stats = solver.compute_statistics()

        assert 'mean' in stats
        assert 'std' in stats
        assert 'entropy' in stats

    def test_reaction_diffusion_workflow(self):
        """Test complete reaction-diffusion workflow"""
        solver = reaction_diffusion.ReactionDiffusionSolver(
            domain_size=50.0,
            grid_points=32,
            dt=0.1
        )

        solver.initialize_random()

        # Evolve
        for _ in range(50):
            solver.step(method="euler")

        # Analyze patterns
        stats = solver.compute_pattern_statistics()

        assert 'mean_u' in stats
        assert 'amplitude' in stats


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
