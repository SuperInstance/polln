"""
Core Thermal Simulation Module
==============================
Finite element thermal model for MAC arrays and synapse-inspired structures.

Implements:
- 2D/3D finite difference heat equation solver
- Steady-state and transient analysis
- Boundary condition handling
- Heat source modeling

References:
[1] Incropera, F.P. (2007). Fundamentals of Heat and Mass Transfer
[2] Patankar, S.V. (1980). Numerical Heat Transfer and Fluid Flow
[3] Cahill, D.G. (2003). Nanoscale thermal transport. Rev. Mod. Phys. 75, 1263
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable, Dict
from enum import Enum
import time
from scipy import sparse
from scipy.sparse.linalg import spsolve, cg, gmres
from scipy.ndimage import gaussian_filter

# Import materials
from materials import Material, get_material, calculate_thermal_resistance


class BoundaryType(Enum):
    """Boundary condition types."""
    DIRICHLET = "fixed_temperature"      # Fixed temperature
    NEUMANN = "fixed_flux"               # Fixed heat flux
    CONVECTIVE = "convection"            # Convective cooling
    PERIODIC = "periodic"                # Periodic boundary


@dataclass
class BoundaryCondition:
    """Boundary condition specification."""
    boundary_type: BoundaryType
    value: float  # Temperature (K), flux (W/m²), or h (W/m²K)
    ambient_temp: float = 300.0  # For convective BC


@dataclass
class HeatSource:
    """Heat source specification."""
    position: Tuple[int, ...]  # Grid position
    power: float  # Power in Watts
    shape: str = "point"  # "point", "gaussian", "uniform"
    sigma: float = 1.0  # For Gaussian sources


@dataclass
class SimulationConfig:
    """Configuration for thermal simulation."""
    # Grid parameters
    nx: int = 100
    ny: int = 100
    nz: int = 1  # 1 for 2D, >1 for 3D
    dx: float = 10e-9  # Grid spacing in meters
    dy: float = 10e-9
    dz: float = 10e-9
    
    # Physical parameters
    ambient_temp: float = 300.0  # K
    
    # Solver parameters
    max_iterations: int = 10000
    convergence_tolerance: float = 1e-6
    relaxation_factor: float = 1.0  # For SOR
    
    # Time parameters (for transient)
    time_step: float = 1e-9  # seconds
    total_time: float = 1e-6  # seconds
    
    # Output
    verbose: bool = True
    save_history: bool = False


class ThermalGrid:
    """Grid structure for thermal simulation."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.nx = config.nx
        self.ny = config.ny
        self.nz = config.nz
        
        # Temperature field
        self.T = np.ones((self.nz, self.ny, self.nx)) * config.ambient_temp
        
        # Thermal conductivity field (can be spatially varying)
        self.k = np.ones((self.nz, self.ny, self.nx)) * 148.0  # Default Si
        
        # Heat source field
        self.Q = np.zeros((self.nz, self.ny, self.nx))
        
        # Thermal diffusivity field
        self.alpha = np.ones((self.nz, self.ny, self.nx)) * 9.0e-5  # Si
        
        # Boundary conditions
        self.bc_left: BoundaryCondition = BoundaryCondition(
            BoundaryType.NEUMANN, 0.0)  # Adiabatic
        self.bc_right: BoundaryCondition = BoundaryCondition(
            BoundaryType.NEUMANN, 0.0)
        self.bc_top: BoundaryCondition = BoundaryCondition(
            BoundaryType.CONVECTIVE, 1e5)  # h = 1e5 W/m²K
        self.bc_bottom: BoundaryCondition = BoundaryCondition(
            BoundaryType.DIRICHLET, config.ambient_temp)
        
        # Front/back for 3D
        if self.nz > 1:
            self.bc_front: BoundaryCondition = BoundaryCondition(
                BoundaryType.NEUMANN, 0.0)
            self.bc_back: BoundaryCondition = BoundaryCondition(
                BoundaryType.NEUMANN, 0.0)
    
    def set_material_region(self, material: Material, 
                            x_range: Tuple[int, int],
                            y_range: Tuple[int, int],
                            z_range: Tuple[int, int] = (0, None)):
        """Set material properties in a region."""
        z_start, z_end = z_range
        if z_end is None:
            z_end = self.nz
        
        self.k[z_start:z_end, y_range[0]:y_range[1], x_range[0]:x_range[1]] = \
            material.thermal_conductivity
        self.alpha[z_start:z_end, y_range[0]:y_range[1], x_range[0]:x_range[1]] = \
            material.thermal_diffusivity
    
    def add_heat_source(self, source: HeatSource):
        """Add a heat source to the grid."""
        if len(source.position) == 2:
            j, i = source.position
            k = 0
        else:
            k, j, i = source.position
        
        if source.shape == "point":
            self.Q[k, j, i] += source.power
        elif source.shape == "gaussian":
            # Create Gaussian distributed source
            for di in range(-3, 4):
                for dj in range(-3, 4):
                    for dk in range(-3, 4) if self.nz > 1 else [0]:
                        ii, jj, kk = i + di, j + dj, k + dk
                        if 0 <= ii < self.nx and 0 <= jj < self.ny and 0 <= kk < self.nz:
                            r2 = di**2 + dj**2 + dk**2
                            weight = np.exp(-r2 / (2 * source.sigma**2))
                            self.Q[kk, jj, ii] += source.power * weight
        elif source.shape == "uniform":
            # Uniform source over region (use directly)
            self.Q[k, j, i] += source.power
    
    def add_volumetric_heat(self, power_density: float,
                           x_range: Tuple[int, int],
                           y_range: Tuple[int, int],
                           z_range: Tuple[int, int] = (0, None)):
        """Add volumetric heat generation in a region."""
        z_start, z_end = z_range
        if z_end is None:
            z_end = self.nz
        
        # power_density in W/m³
        cell_volume = self.config.dx * self.config.dy * self.config.dz
        power_per_cell = power_density * cell_volume
        
        self.Q[z_start:z_end, y_range[0]:y_range[1], x_range[0]:x_range[1]] += power_per_cell
    
    def clear_heat_sources(self):
        """Clear all heat sources."""
        self.Q.fill(0.0)


class ThermalSolver:
    """Finite difference thermal solver."""
    
    def __init__(self, grid: ThermalGrid):
        self.grid = grid
        self.config = grid.config
        self.iteration_count = 0
        self.residual_history = []
    
    def solve_steady_state(self) -> NDArray:
        """
        Solve steady-state heat equation using iterative method.
        
        ∇·(k∇T) + Q = 0
        
        For constant k: ∇²T + Q/k = 0
        """
        T = self.grid.T.copy()
        Q = self.grid.Q
        k = self.grid.k
        alpha = self.grid.alpha
        
        dx, dy, dz = self.config.dx, self.config.dy, self.config.dz
        nx, ny, nz = self.grid.nx, self.grid.ny, self.grid.nz
        
        # Coefficients
        dx2, dy2, dz2 = dx**2, dy**2, dz**2
        
        omega = self.config.relaxation_factor
        
        if self.config.verbose:
            print(f"Solving steady-state thermal problem...")
            print(f"Grid size: {nz} x {ny} x {nx}")
        
        for iteration in range(self.config.max_iterations):
            T_old = T.copy()
            max_residual = 0.0
            
            # Interior points
            for k_idx in range(nz):
                for j in range(1, ny - 1):
                    for i in range(1, nx - 1):
                        # Local thermal conductivity (harmonic mean for interfaces)
                        k_local = k[k_idx, j, i]
                        
                        # Neighboring temperatures
                        T_w = T[k_idx, j, i-1] if i > 0 else T[k_idx, j, i]
                        T_e = T[k_idx, j, i+1] if i < nx-1 else T[k_idx, j, i]
                        T_s = T[k_idx, j-1, i] if j > 0 else T[k_idx, j, i]
                        T_n = T[k_idx, j+1, i] if j < ny-1 else T[k_idx, j, i]
                        
                        if nz > 1:
                            T_f = T[k_idx-1, j, i] if k_idx > 0 else T[k_idx, j, i]
                            T_b = T[k_idx+1, j, i] if k_idx < nz-1 else T[k_idx, j, i]
                        else:
                            T_f, T_b = T[k_idx, j, i], T[k_idx, j, i]
                        
                        # Laplacian
                        d2T_dx2 = (T_w - 2*T[k_idx,j,i] + T_e) / dx2
                        d2T_dy2 = (T_s - 2*T[k_idx,j,i] + T_n) / dy2
                        
                        if nz > 1:
                            d2T_dz2 = (T_f - 2*T[k_idx,j,i] + T_b) / dz2
                        else:
                            d2T_dz2 = 0.0
                        
                        # Heat equation
                        heat_term = Q[k_idx, j, i] / (k_local * self.grid.k[k_idx, j, i] / k_local)
                        
                        T_new = (d2T_dx2 + d2T_dy2 + d2T_dz2) * k_local / (
                            k[k_idx, j, i-1] + 2*k_local + k[k_idx, j, i+1]
                        ) / 4 * dx2
                        
                        # Simplified update
                        denom = 2.0 * (1/dx2 + 1/dy2)
                        if nz > 1:
                            denom += 2.0 / dz2
                        
                        T_new = ((T_w + T_e) / dx2 + (T_s + T_n) / dy2 + 
                                (T_f + T_b) / dz2 + Q[k_idx,j,i]/k_local) / denom
                        
                        # SOR update
                        T[k_idx, j, i] = (1 - omega) * T[k_idx, j, i] + omega * T_new
                        
                        residual = abs(T[k_idx, j, i] - T_old[k_idx, j, i])
                        max_residual = max(max_residual, residual)
            
            # Apply boundary conditions
            self._apply_boundary_conditions(T)
            
            self.residual_history.append(max_residual)
            
            if iteration % 100 == 0 and self.config.verbose:
                print(f"  Iteration {iteration}: max residual = {max_residual:.2e}")
            
            if max_residual < self.config.convergence_tolerance:
                if self.config.verbose:
                    print(f"  Converged after {iteration} iterations")
                break
        
        self.grid.T = T
        self.iteration_count = iteration
        return T
    
    def solve_steady_state_matrix(self) -> NDArray:
        """
        Solve steady-state using sparse matrix methods.
        More efficient for large problems.
        """
        nx, ny, nz = self.grid.nx, self.grid.ny, self.grid.nz
        n = nx * ny * nz
        
        # Build sparse matrix
        A = sparse.lil_matrix((n, n))
        b = np.zeros(n)
        
        dx, dy, dz = self.config.dx, self.config.dy, self.config.dz
        dx2, dy2, dz2 = dx**2, dy**2, dz**2
        
        def idx(k, j, i):
            return k * ny * nx + j * nx + i
        
        for k_idx in range(nz):
            for j in range(ny):
                for i in range(nx):
                    row = idx(k_idx, j, i)
                    k_local = self.grid.k[k_idx, j, i]
                    
                    # Diagonal coefficient
                    coeff = 2.0 * (1/dx2 + 1/dy2)
                    if nz > 1:
                        coeff += 2.0 / dz2
                    
                    A[row, row] = coeff
                    
                    # Neighbors
                    if i > 0:
                        A[row, idx(k_idx, j, i-1)] = -1.0 / dx2
                    if i < nx - 1:
                        A[row, idx(k_idx, j, i+1)] = -1.0 / dx2
                    if j > 0:
                        A[row, idx(k_idx, j-1, i)] = -1.0 / dy2
                    if j < ny - 1:
                        A[row, idx(k_idx, j+1, i)] = -1.0 / dy2
                    if nz > 1:
                        if k_idx > 0:
                            A[row, idx(k_idx-1, j, i)] = -1.0 / dz2
                        if k_idx < nz - 1:
                            A[row, idx(k_idx+1, j, i)] = -1.0 / dz2
                    
                    # Source term
                    b[row] = self.grid.Q[k_idx, j, i] / k_local
        
        # Apply boundary conditions
        self._apply_bc_matrix(A, b, nx, ny, nz)
        
        # Solve
        A_csr = A.tocsr()
        T_flat = spsolve(A_csr, b)
        
        T = T_flat.reshape((nz, ny, nx))
        self.grid.T = T
        
        return T
    
    def solve_transient(self, time_profile: Optional[Callable] = None) -> List[NDArray]:
        """
        Solve transient heat equation using explicit finite difference.
        
        ∂T/∂t = α∇²T + Q/(ρc_p)
        
        Args:
            time_profile: Function(t) -> power_factor, modifies heat sources over time
        
        Returns:
            List of temperature fields at each time step
        """
        T = self.grid.T.copy()
        Q = self.grid.Q.copy()
        alpha = self.grid.alpha
        
        dt = self.config.time_step
        total_time = self.config.total_time
        n_steps = int(total_time / dt)
        
        dx, dy, dz = self.config.dx, self.config.dy, self.config.dz
        dx2, dy2, dz2 = dx**2, dy**2, dz**2
        
        nx, ny, nz = self.grid.nx, self.grid.ny, self.grid.nz
        
        # Stability check (CFL condition)
        dt_max = 0.5 / (alpha.max() * (1/dx2 + 1/dy2 + (1/dz2 if nz > 1 else 0)))
        if dt > dt_max:
            print(f"Warning: dt = {dt:.2e} > dt_max = {dt_max:.2e}. Solution may be unstable.")
        
        history = [T.copy()] if self.config.save_history else []
        
        if self.config.verbose:
            print(f"Solving transient problem: {n_steps} steps, dt = {dt:.2e} s")
        
        t = 0.0
        for step in range(n_steps):
            t += dt
            T_old = T.copy()
            
            # Time-dependent heat source
            if time_profile is not None:
                power_factor = time_profile(t)
                Q_current = Q * power_factor
            else:
                Q_current = Q
            
            # Update interior points
            for k_idx in range(nz):
                for j in range(1, ny - 1):
                    for i in range(1, nx - 1):
                        al = alpha[k_idx, j, i]
                        
                        # Laplacian
                        d2T_dx2 = (T_old[k_idx,j,i-1] - 2*T_old[k_idx,j,i] + 
                                  T_old[k_idx,j,i+1]) / dx2
                        d2T_dy2 = (T_old[k_idx,j-1,i] - 2*T_old[k_idx,j,i] + 
                                  T_old[k_idx,j+1,i]) / dy2
                        
                        if nz > 1:
                            d2T_dz2 = (T_old[k_idx-1,j,i] - 2*T_old[k_idx,j,i] + 
                                      T_old[k_idx+1,j,i]) / dz2
                        else:
                            d2T_dz2 = 0.0
                        
                        # Heat source term (assuming constant k for simplicity)
                        k_local = self.grid.k[k_idx, j, i]
                        source_term = Q_current[k_idx, j, i] / (
                            self.grid.k[k_idx, j, i] * alpha[k_idx, j, i] / al)
                        
                        # Forward Euler update
                        T[k_idx, j, i] = T_old[k_idx, j, i] + dt * (
                            al * (d2T_dx2 + d2T_dy2 + d2T_dz2) + 
                            Q_current[k_idx, j, i] / (k_local / al * self.grid.k[k_idx,j,i])
                        )
            
            # Apply boundary conditions
            self._apply_boundary_conditions(T)
            
            if self.config.save_history and step % 10 == 0:
                history.append(T.copy())
        
        self.grid.T = T
        return history if history else [T]
    
    def _apply_boundary_conditions(self, T: NDArray):
        """Apply boundary conditions to temperature field."""
        bc = self.grid
        
        # Left boundary (i = 0)
        if bc.bc_left.boundary_type == BoundaryType.DIRICHLET:
            T[:, :, 0] = bc.bc_left.value
        elif bc.bc_left.boundary_type == BoundaryType.NEUMANN:
            T[:, :, 0] = T[:, :, 1]  # Zero flux
        elif bc.bc_left.boundary_type == BoundaryType.CONVECTIVE:
            h = bc.bc_left.value
            T[:, :, 0] = T[:, :, 1] + bc.bc_left.ambient_temp * h * self.config.dx / self.grid.k[:, :, 0]
        
        # Right boundary (i = -1)
        if bc.bc_right.boundary_type == BoundaryType.DIRICHLET:
            T[:, :, -1] = bc.bc_right.value
        elif bc.bc_right.boundary_type == BoundaryType.NEUMANN:
            T[:, :, -1] = T[:, :, -2]
        
        # Top boundary (j = -1)
        if bc.bc_top.boundary_type == BoundaryType.DIRICHLET:
            T[:, -1, :] = bc.bc_top.value
        elif bc.bc_top.boundary_type == BoundaryType.NEUMANN:
            T[:, -1, :] = T[:, -2, :]
        elif bc.bc_top.boundary_type == BoundaryType.CONVECTIVE:
            h = bc.bc_top.value
            k = self.grid.k[:, -1, :]
            T[:, -1, :] = (T[:, -2, :] + h * self.config.dy * bc.bc_top.ambient_temp / k) / (
                1 + h * self.config.dy / k)
        
        # Bottom boundary (j = 0)
        if bc.bc_bottom.boundary_type == BoundaryType.DIRICHLET:
            T[:, 0, :] = bc.bc_bottom.value
        elif bc.bc_bottom.boundary_type == BoundaryType.NEUMANN:
            T[:, 0, :] = T[:, 1, :]
        
        # Front/back for 3D
        if T.shape[0] > 1:
            if bc.bc_front.boundary_type == BoundaryType.NEUMANN:
                T[0, :, :] = T[1, :, :]
            if bc.bc_back.boundary_type == BoundaryType.NEUMANN:
                T[-1, :, :] = T[-2, :, :]
    
    def _apply_bc_matrix(self, A, b, nx, ny, nz):
        """Apply boundary conditions to matrix formulation."""
        bc = self.grid
        dx, dy, dz = self.config.dx, self.config.dy, self.config.dz
        
        def idx(k, j, i):
            return k * ny * nx + j * nx + i
        
        # Apply bottom Dirichlet BC
        for i in range(nx):
            for k_idx in range(nz):
                row = idx(k_idx, 0, i)
                A[row, :] = 0
                A[row, row] = 1.0
                b[row] = bc.bc_bottom.value


class ThermalAnalyzer:
    """Analysis tools for thermal simulation results."""
    
    def __init__(self, grid: ThermalGrid):
        self.grid = grid
    
    def max_temperature(self) -> float:
        """Maximum temperature in the domain."""
        return np.max(self.grid.T)
    
    def min_temperature(self) -> float:
        """Minimum temperature in the domain."""
        return np.min(self.grid.T)
    
    def average_temperature(self) -> float:
        """Average temperature."""
        return np.mean(self.grid.T)
    
    def temperature_rise(self) -> float:
        """Maximum temperature rise above ambient."""
        return self.max_temperature() - self.grid.config.ambient_temp
    
    def hot_spot_location(self) -> Tuple[int, int, int]:
        """Location of maximum temperature."""
        k, j, i = np.unravel_index(np.argmax(self.grid.T), self.grid.T.shape)
        return (k, j, i)
    
    def thermal_resistance(self, power: float) -> float:
        """
        Calculate thermal resistance from power and temperature rise.
        R_th = ΔT / P
        """
        return self.temperature_rise() / power
    
    def heat_flux(self) -> Tuple[NDArray, NDArray, NDArray]:
        """
        Calculate heat flux components.
        q = -k ∇T
        """
        T = self.grid.T
        k = self.grid.k
        dx, dy, dz = self.grid.config.dx, self.grid.config.dy, self.grid.config.dz
        
        qx = np.zeros_like(T)
        qy = np.zeros_like(T)
        qz = np.zeros_like(T)
        
        # Central differences for interior
        qx[:, :, 1:-1] = -k[:, :, 1:-1] * (T[:, :, 2:] - T[:, :, :-2]) / (2 * dx)
        qy[:, 1:-1, :] = -k[:, 1:-1, :] * (T[:, 2:, :] - T[:, :-2, :]) / (2 * dy)
        
        if T.shape[0] > 1:
            qz[1:-1, :, :] = -k[1:-1, :, :] * (T[2:, :, :] - T[:-2, :, :]) / (2 * dz)
        
        return qx, qy, qz
    
    def isotherm_contour(self, temperature: float) -> NDArray:
        """Find isotherm contour for a given temperature."""
        from scipy import ndimage
        mask = self.grid.T > temperature
        return mask
    
    def thermal_gradient_magnitude(self) -> NDArray:
        """Calculate magnitude of thermal gradient."""
        qx, qy, qz = self.heat_flux()
        return np.sqrt(qx**2 + qy**2 + qz**2)
    
    def report(self) -> str:
        """Generate thermal analysis report."""
        lines = [
            "=" * 60,
            "THERMAL ANALYSIS REPORT",
            "=" * 60,
            f"Domain size: {self.grid.nx} x {self.grid.ny} x {self.grid.nz} cells",
            f"Physical size: {self.grid.nx * self.grid.config.dx * 1e6:.2f} x "
            f"{self.grid.ny * self.grid.config.dy * 1e6:.2f} x "
            f"{self.grid.nz * self.grid.config.dz * 1e6:.2f} μm",
            "",
            f"Maximum temperature: {self.max_temperature():.2f} K",
            f"Minimum temperature: {self.min_temperature():.2f} K",
            f"Average temperature: {self.average_temperature():.2f} K",
            f"Temperature rise: {self.temperature_rise():.2f} K",
            "",
            f"Hot spot location (k, j, i): {self.hot_spot_location()}",
            f"Total heat generated: {np.sum(self.grid.Q):.2e} W",
            "=" * 60,
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    # Test thermal simulation
    print("Thermal Simulation Test")
    print("=" * 60)
    
    # Create configuration
    config = SimulationConfig(
        nx=50,
        ny=50,
        nz=1,
        dx=10e-9,
        dy=10e-9,
        convergence_tolerance=1e-4,
        verbose=True
    )
    
    # Create grid
    grid = ThermalGrid(config)
    
    # Add heat source
    source = HeatSource(
        position=(25, 25),
        power=1e-6,  # 1 μW
        shape="gaussian",
        sigma=2.0
    )
    grid.add_heat_source(source)
    
    # Set boundary conditions
    grid.bc_bottom = BoundaryCondition(BoundaryType.DIRICHLET, 300.0)
    grid.bc_top = BoundaryCondition(BoundaryType.CONVECTIVE, 1e5)
    
    # Solve
    solver = ThermalSolver(grid)
    T = solver.solve_steady_state_matrix()
    
    # Analyze
    analyzer = ThermalAnalyzer(grid)
    print(analyzer.report())
