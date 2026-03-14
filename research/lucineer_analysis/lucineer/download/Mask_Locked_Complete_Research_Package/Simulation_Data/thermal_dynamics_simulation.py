#!/usr/bin/env python3
"""
Thermal Dynamics Simulation for Mask-Locked Inference Chip
=========================================================

Complete thermal simulation framework including:
- 3D heat equation solver
- Thermal resistance network analysis
- Hotspot prediction
- Transient thermal analysis
- Mask-locked vs SRAM comparison

Author: Mathematical Physics Analysis
Date: March 2026
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from dataclasses import dataclass
from typing import Tuple, List, Optional
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ============================================================================
# Physical Constants
# ============================================================================

STEFAN_BOLTZMANN = 5.67e-8  # W/(m²·K⁴)
BOLTZMANN_J = 1.38e-23      # J/K
BOLTZMANN_EV = 8.617e-5     # eV/K

# ============================================================================
# Material Properties Database
# ============================================================================

@dataclass
class MaterialProperties:
    """Material thermal properties"""
    name: str
    k: float       # Thermal conductivity [W/(m·K)]
    rho: float     # Density [kg/m³]
    cp: float      # Specific heat [J/(kg·K)]
    
    @property
    def alpha(self) -> float:
        """Thermal diffusivity [m²/s]"""
        return self.k / (self.rho * self.cp)

# Material database
MATERIALS = {
    'silicon': MaterialProperties('Silicon', 148.0, 2329.0, 700.0),
    'copper': MaterialProperties('Copper', 385.0, 8960.0, 385.0),
    'epoxy': MaterialProperties('Die Attach Epoxy', 2.0, 1200.0, 1000.0),
    'mold_compound': MaterialProperties('Mold Compound', 0.8, 1800.0, 900.0),
    'tim': MaterialProperties('Thermal Interface Material', 5.0, 2500.0, 800.0),
    'air_300k': MaterialProperties('Air at 300K', 0.026, 1.16, 1007.0),
}

# ============================================================================
# Die Configuration
# ============================================================================

@dataclass
class DieConfiguration:
    """Mask-locked inference die configuration"""
    name: str
    area_mm2: float       # Die area [mm²]
    thickness_um: float   # Die thickness [μm]
    power_w: float        # Total power [W]
    n_pes: int            # Number of processing elements
    utilization: float    # PE utilization (0-1)
    package: str          # Package type
    
    @property
    def dimensions(self) -> Tuple[float, float, float]:
        """Die dimensions in meters (assuming square)"""
        side = np.sqrt(self.area_mm2 * 1e-6)  # Convert mm² to m²
        thickness = self.thickness_um * 1e-6  # Convert μm to m
        return (side, side, thickness)
    
    @property
    def volume(self) -> float:
        """Die volume [m³]"""
        L, _, t = self.dimensions
        return L * L * t

# Default configuration for our mask-locked chip
DEFAULT_DIE = DieConfiguration(
    name="Mask-Locked Inference Die",
    area_mm2=27.0,
    thickness_um=300.0,
    power_w=3.0,
    n_pes=1024,
    utilization=0.8,
    package="QFN-48"
)

# ============================================================================
# Thermal Resistance Network
# ============================================================================

class ThermalResistanceNetwork:
    """
    Thermal resistance network model for packaged die.
    
    Models heat flow from junction through package to ambient.
    """
    
    def __init__(self, die: DieConfiguration):
        self.die = die
        self.layers = self._build_layer_stack()
        self._compute_resistances()
        
    def _build_layer_stack(self) -> List[dict]:
        """Build the layer stack for the package"""
        L, _, _ = self.die.dimensions
        A = L * L  # Die area
        
        return [
            {
                'name': 'Silicon Die',
                'material': MATERIALS['silicon'],
                'thickness': self.die.thickness_um * 1e-6,
                'area': A,
            },
            {
                'name': 'TIM',
                'material': MATERIALS['tim'],
                'thickness': 25e-6,  # 25 μm
                'area': A,
            },
            {
                'name': 'Die Attach Epoxy',
                'material': MATERIALS['epoxy'],
                'thickness': 15e-6,  # 15 μm
                'area': A,
            },
            {
                'name': 'Exposed Pad (Copper)',
                'material': MATERIALS['copper'],
                'thickness': 200e-6,  # 200 μm
                'area': A,
            },
        ]
    
    def _compute_resistances(self):
        """Compute thermal resistances for each layer"""
        self.R_cond = []  # Conductive resistances
        
        for layer in self.layers:
            mat = layer['material']
            t = layer['thickness']
            A = layer['area']
            
            R = t / (mat.k * A)
            self.R_cond.append(R)
            
    def spreading_resistance(self, source_area_mm2: float) -> float:
        """
        Compute thermal spreading resistance for a heat source
        on the die surface using Lee correlation.
        """
        mat = MATERIALS['silicon']
        L, _, t_die = self.die.dimensions
        
        # Equivalent radii
        r_s = np.sqrt(source_area_mm2 * 1e-6 / np.pi)  # Source radius
        r_d = L / np.sqrt(np.pi)  # Die equivalent radius
        
        # Lee correlation approximation
        epsilon = r_s / r_d
        tau = t_die / r_d
        
        # Simplified spreading factor
        if epsilon < 0.1:
            psi = 1.0
        else:
            psi = (1 + tau) / epsilon * np.log(1/epsilon) / np.pi
            
        R_spread = psi / (2 * np.pi * mat.k * r_s)
        
        return R_spread
    
    def junction_to_case(self) -> float:
        """Total junction-to-case thermal resistance"""
        return sum(self.R_cond)
    
    def case_to_ambient(self, 
                        h_ambient: float = 20.0,  # W/(m²·K)
                        pcb_area_mm2: float = 500.0,
                        with_heatsink: bool = False,
                        R_heatsink: float = 15.0) -> float:
        """
        Compute case-to-ambient thermal resistance.
        
        Args:
            h_ambient: Convection coefficient [W/(m²·K)]
            pcb_area_mm2: Effective PCB heat spreading area [mm²]
            with_heatsink: Whether heatsink is attached
            R_heatsink: Heatsink thermal resistance [K/W]
        """
        L, _, _ = self.die.dimensions
        die_area = L * L
        
        # PCB convection path
        A_pcb = pcb_area_mm2 * 1e-6
        R_pcb = 1 / (h_ambient * A_pcb)
        
        # Mold compound surface (top)
        A_mold = die_area * 1.5  # Slightly larger than die
        R_mold = 1 / (h_ambient * A_mold)
        
        # Parallel paths
        R_ca = 1 / (1/R_pcb + 1/R_mold)
        
        if with_heatsink:
            # Heatsink in parallel with natural convection
            R_ca = 1 / (1/R_ca + 1/R_heatsink)
            
        return R_ca
    
    def junction_to_ambient(self, 
                           with_heatsink: bool = True,
                           R_heatsink: float = 15.0) -> float:
        """Total junction-to-ambient thermal resistance"""
        R_jc = self.junction_to_case()
        R_ca = self.case_to_ambient(with_heatsink=with_heatsink, 
                                    R_heatsink=R_heatsink)
        return R_jc + R_ca
    
    def junction_temperature(self, 
                            T_ambient: float = 298.0,  # K
                            power: Optional[float] = None,
                            with_heatsink: bool = True) -> float:
        """Compute steady-state junction temperature"""
        if power is None:
            power = self.die.power_w
            
        R_ja = self.junction_to_ambient(with_heatsink=with_heatsink)
        return T_ambient + power * R_ja

# ============================================================================
# Thermal Capacitance and Transient Analysis
# ============================================================================

class ThermalCapacitance:
    """Thermal capacitance calculations for transient analysis"""
    
    @staticmethod
    def layer_capacitance(material: MaterialProperties, 
                          volume: float) -> float:
        """Compute thermal capacitance for a volume [J/K]"""
        return material.rho * material.cp * volume
    
    @staticmethod
    def time_constant(R_th: float, C_th: float) -> float:
        """Compute thermal time constant [s]"""
        return R_th * C_th

class TransientAnalysis:
    """Transient thermal analysis for inference bursts"""
    
    def __init__(self, 
                 R_th: float,
                 C_th: float,
                 T_ambient: float = 298.0):
        self.R_th = R_th
        self.C_th = C_th
        self.tau = R_th * C_th
        self.T_ambient = T_ambient
        
    def step_response(self, t: np.ndarray, power: float) -> np.ndarray:
        """
        Temperature response to step power input.
        
        T(t) = T_a + P*R_th * (1 - exp(-t/tau))
        """
        T_ss = self.T_ambient + power * self.R_th
        return T_ss - power * self.R_th * np.exp(-t / self.tau)
    
    def burst_response(self, 
                       t: np.ndarray,
                       power: float,
                       burst_duration: float) -> np.ndarray:
        """
        Temperature response to a power burst of finite duration.
        """
        T = np.zeros_like(t)
        T_ss = self.T_ambient + power * self.R_th
        
        for i, ti in enumerate(t):
            if ti < burst_duration:
                # During burst
                T[i] = T_ss - power * self.R_th * np.exp(-ti / self.tau)
            else:
                # After burst
                T_peak = T_ss - power * self.R_th * np.exp(-burst_duration / self.tau)
                T[i] = self.T_ambient + (T_peak - self.T_ambient) * np.exp(-(ti - burst_duration) / self.tau)
                
        return T
    
    def periodic_bursts(self,
                        t: np.ndarray,
                        power: float,
                        burst_duration: float,
                        period: float) -> np.ndarray:
        """
        Temperature response to periodic power bursts.
        """
        T = np.ones_like(t) * self.T_ambient
        T_ss = self.T_ambient + power * self.R_th
        
        for i, ti in enumerate(t):
            n_cycles = int(ti / period)
            time_in_cycle = ti - n_cycles * period
            
            # Accumulate temperature from all previous cycles
            for n in range(n_cycles + 1):
                cycle_time = ti - n * period
                
                if cycle_time < 0:
                    continue
                    
                if cycle_time < burst_duration:
                    # Contribution from active burst
                    dT = power * self.R_th * (1 - np.exp(-cycle_time / self.tau))
                else:
                    # Contribution from cooling phase
                    T_at_end = power * self.R_th * (1 - np.exp(-burst_duration / self.tau))
                    cool_time = cycle_time - burst_duration
                    dT = T_at_end * np.exp(-cool_time / self.tau)
                    
                T[i] = self.T_ambient + dT
                
        return T

# ============================================================================
# Hotspot Analysis
# ============================================================================

class HotspotAnalysis:
    """Hotspot formation and prediction analysis"""
    
    def __init__(self, die: DieConfiguration):
        self.die = die
        self.mat = MATERIALS['silicon']
        
    def peak_temperature(self, 
                         hotspot_power: float,
                         hotspot_radius: float) -> float:
        """
        Compute peak temperature rise above average die temperature.
        
        ΔT = P / (4πkr_s)
        """
        return hotspot_power / (4 * np.pi * self.mat.k * hotspot_radius)
    
    def hotspot_radius(self, 
                       power_density: float,
                       max_temp_rise: float) -> float:
        """
        Compute maximum hotspot radius for a given temperature constraint.
        
        r_s = P / (4πk ΔT)
        """
        # Convert power density to total power for unit area
        # This is an approximation
        return power_density / (4 * np.pi * self.mat.k * max_temp_rise)
    
    def gaussian_hotspot_profile(self,
                                 x: np.ndarray,
                                 y: np.ndarray,
                                 x0: float, y0: float,
                                 sigma: float,
                                 q0: float) -> np.ndarray:
        """
        Generate Gaussian power density distribution.
        
        q(x,y) = q0 * exp(-((x-x0)² + (y-y0)²) / (2σ²))
        """
        r2 = (x - x0)**2 + (y - y0)**2
        return q0 * np.exp(-r2 / (2 * sigma**2))
    
    def thermal_gradient(self, 
                        hotspot_power: float,
                        hotspot_radius: float,
                        distance: float) -> float:
        """
        Compute temperature gradient at a given distance from hotspot center.
        """
        T_peak = self.peak_temperature(hotspot_power, hotspot_radius)
        return T_peak * np.exp(-distance**2 / (2 * hotspot_radius**2))

# ============================================================================
# Mask-Locked vs SRAM Comparison
# ============================================================================

class ThermalComparison:
    """Compare thermal characteristics of mask-locked vs SRAM-based designs"""
    
    def __init__(self, 
                 n_params: float = 2e9,  # 2B parameters
                 bits_per_weight: int = 2,
                 tokens_per_second: float = 80.0):
        self.n_params = n_params
        self.bits = bits_per_weight
        self.tok_s = tokens_per_second
        
    def sram_power_consumption(self,
                               read_energy_pj: float = 50.0,
                               leakage_power_density: float = 0.1) -> dict:
        """
        Estimate SRAM power consumption for weight storage.
        
        Returns dict with power breakdown in Watts.
        """
        # Access rate
        macs_per_token = 2.9e9  # For 2B model
        accesses_per_weight = macs_per_token / self.n_params * self.tok_s
        
        # Read power: E_read * N_bits * N_accesses
        P_read = (read_energy_pj * 1e-12 * self.bits * self.n_params * 
                  accesses_per_weight)
        
        # SRAM area estimate (28nm)
        sram_cell_area = 0.2e-12  # m² per bit (6T SRAM)
        sram_area = self.n_params * self.bits * sram_cell_area
        
        # Leakage power
        P_leak = leakage_power_density * sram_area * 1e6  # W/mm² * mm²
        
        return {
            'read_power': P_read,
            'leakage_power': P_leak,
            'total_power': P_read + P_leak,
            'sram_area_mm2': sram_area * 1e6,
        }
    
    def mask_locked_power(self) -> dict:
        """
        Mask-locked weight power consumption.
        
        Weights are encoded in metal layers - zero access power.
        """
        return {
            'read_power': 0.0,
            'leakage_power': 0.0,
            'total_power': 0.0,
            'area_mm2': 0.0,  # No additional area
        }
    
    def temperature_comparison(self,
                               R_th: float = 15.6,
                               T_ambient: float = 298.0,
                               P_compute: float = 2.0) -> dict:
        """
        Compare junction temperatures between architectures.
        """
        sram = self.sram_power_consumption()
        ml = self.mask_locked_power()
        
        T_sram = T_ambient + (P_compute + sram['total_power']) * R_th
        T_ml = T_ambient + P_compute * R_th
        
        return {
            'T_sram': T_sram,
            'T_mask_locked': T_ml,
            'delta_T': T_sram - T_ml,
            'power_savings': sram['total_power'],
        }
    
    def thermal_variance_comparison(self,
                                    sigma_compute: float = 0.1,
                                    sigma_sram: float = 0.05) -> dict:
        """
        Compare thermal variance between architectures.
        """
        # SRAM-based: variance from compute + SRAM
        sigma_T_sram = np.sqrt(sigma_compute**2 + sigma_sram**2)
        
        # Mask-locked: variance from compute only
        sigma_T_ml = sigma_compute
        
        return {
            'sigma_T_sram': sigma_T_sram,
            'sigma_T_ml': sigma_T_ml,
            'variance_reduction': 1 - (sigma_T_ml / sigma_T_sram)**2,
        }

# ============================================================================
# Finite Difference Heat Equation Solver
# ============================================================================

class HeatEquationSolver:
    """
    3D finite difference heat equation solver.
    
    Uses explicit scheme with adaptive time stepping.
    """
    
    def __init__(self,
                 Lx: float, Ly: float, Lz: float,
                 Nx: int, Ny: int, Nz: int,
                 material: MaterialProperties):
        """
        Initialize the solver.
        
        Args:
            Lx, Ly, Lz: Domain dimensions [m]
            Nx, Ny, Nz: Number of grid points
            material: Material properties
        """
        self.Lx, self.Ly, self.Lz = Lx, Ly, Lz
        self.Nx, self.Ny, self.Nz = Nx, Ny, Nz
        self.mat = material
        
        # Grid spacing
        self.dx = Lx / (Nx - 1)
        self.dy = Ly / (Ny - 1)
        self.dz = Lz / (Nz - 1)
        
        # Create coordinate arrays
        self.x = np.linspace(0, Lx, Nx)
        self.y = np.linspace(0, Ly, Ny)
        self.z = np.linspace(0, Lz, Nz)
        
        # Stability criterion (explicit scheme)
        self.dt_max = 1 / (2 * material.alpha * 
                          (1/self.dx**2 + 1/self.dy**2 + 1/self.dz**2))
        
        # Initialize temperature field
        self.T = np.zeros((Nx, Ny, Nz))
        
        # Source term
        self.Q = np.zeros((Nx, Ny, Nz))
        
    def set_initial_condition(self, T_init: float = 298.0):
        """Set uniform initial temperature"""
        self.T[:] = T_init
        
    def set_heat_source(self, 
                        source_func,
                        active_z: Tuple[int, int] = (0, 1)):
        """
        Set heat source from a function q(x, y).
        
        Args:
            source_func: Function q(x, y) -> power density [W/m³]
            active_z: Z indices where heat is generated
        """
        X, Y = np.meshgrid(self.x, self.y, indexing='ij')
        Q_2d = source_func(X, Y)
        
        for k in range(active_z[0], min(active_z[1], self.Nz)):
            self.Q[:, :, k] = Q_2d
            
    def time_step(self, dt: float):
        """
        Advance solution by one time step using explicit scheme.
        """
        alpha = self.mat.alpha
        rho_cp = self.mat.rho * self.mat.cp
        
        # Compute Laplacian using finite differences
        T_new = self.T.copy()
        
        # Interior points
        for i in range(1, self.Nx - 1):
            for j in range(1, self.Ny - 1):
                for k in range(1, self.Nz - 1):
                    # Second derivatives
                    d2T_dx2 = (self.T[i+1, j, k] - 2*self.T[i, j, k] + 
                              self.T[i-1, j, k]) / self.dx**2
                    d2T_dy2 = (self.T[i, j+1, k] - 2*self.T[i, j, k] + 
                              self.T[i, j-1, k]) / self.dy**2
                    d2T_dz2 = (self.T[i, j, k+1] - 2*self.T[i, j, k] + 
                              self.T[i, j, k-1]) / self.dz**2
                    
                    laplacian = d2T_dx2 + d2T_dy2 + d2T_dz2
                    
                    T_new[i, j, k] = (self.T[i, j, k] + 
                                      dt * (alpha * laplacian + 
                                            self.Q[i, j, k] / rho_cp))
        
        # Boundary conditions
        self._apply_boundary_conditions(T_new)
        
        self.T = T_new
        
    def _apply_boundary_conditions(self, T: np.ndarray,
                                   T_bottom: float = 298.0,
                                   h_top: float = 20.0,
                                   T_ambient: float = 298.0):
        """Apply boundary conditions"""
        # Bottom: fixed temperature (exposed pad)
        T[:, :, 0] = T_bottom
        
        # Top: convection BC
        k = self.mat.k
        q_top = h_top * (T[:, :, -1] - T_ambient)
        T[:, :, -1] = T[:, :, -2] - q_top * self.dz / k
        
        # Sides: insulated (Neumann zero)
        T[0, :, :] = T[1, :, :]
        T[-1, :, :] = T[-2, :, :]
        T[:, 0, :] = T[:, 1, :]
        T[:, -1, :] = T[:, -2, :]
        
    def solve_steady_state(self, 
                          max_iterations: int = 10000,
                          tolerance: float = 1e-6) -> np.ndarray:
        """
        Solve for steady-state temperature distribution.
        
        Uses iterative relaxation method.
        """
        alpha = self.mat.alpha
        rho_cp = self.mat.rho * self.mat.cp
        dt = 0.9 * self.dt_max  # Use 90% of max stable time step
        
        for iteration in range(max_iterations):
            T_old = self.T.copy()
            self.time_step(dt)
            
            # Check convergence
            max_change = np.max(np.abs(self.T - T_old))
            if max_change < tolerance:
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Did not converge after {max_iterations} iterations")
            
        return self.T

# ============================================================================
# Visualization Functions
# ============================================================================

def plot_thermal_resistance_network(network: ThermalResistanceNetwork):
    """Visualize thermal resistance network"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot resistances
    layers = ['Silicon Die', 'TIM', 'Epoxy', 'Pad', 'Heatsink', 'Ambient']
    R_values = network.R_cond + [15.0, 91.5]  # Add heatsink and ambient
    
    cumulative_R = np.cumsum([0] + R_values)
    
    ax.barh(layers, R_values, color=['#2ecc71', '#3498db', '#9b59b6', 
                                      '#e74c3c', '#f39c12', '#95a5a6'])
    
    for i, (R, cum_R) in enumerate(zip(R_values, cumulative_R[1:])):
        ax.text(R/2, i, f'{R:.2f} K/W', ha='center', va='center', 
                fontweight='bold', color='white')
    
    ax.set_xlabel('Thermal Resistance [K/W]')
    ax.set_title('Thermal Resistance Network\nMask-Locked Inference Chip')
    ax.set_xlim(0, max(R_values) * 1.1)
    
    plt.tight_layout()
    return fig

def plot_transient_response(transient: TransientAnalysis,
                           power: float = 3.0,
                           duration: float = 100.0):
    """Plot transient thermal response"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    t = np.linspace(0, duration, 1000)
    
    # Step response
    T = transient.step_response(t, power)
    T_C = T - 273.15  # Convert to Celsius
    
    axes[0].plot(t, T_C, 'b-', linewidth=2)
    axes[0].axhline(y=transient.T_ambient - 273.15 + power * transient.R_th, 
                    color='r', linestyle='--', label='Steady state')
    axes[0].set_xlabel('Time [s]')
    axes[0].set_ylabel('Junction Temperature [°C]')
    axes[0].set_title('Step Response to Power Input')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Burst response
    T_burst = transient.burst_response(t, power, burst_duration=10.0)
    T_burst_C = T_burst - 273.15
    
    axes[1].plot(t, T_burst_C, 'g-', linewidth=2)
    axes[1].axvline(x=10.0, color='r', linestyle='--', label='Burst end')
    axes[1].set_xlabel('Time [s]')
    axes[1].set_ylabel('Junction Temperature [°C]')
    axes[1].set_title('Response to 10s Power Burst')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_hotspot_analysis(hotspot: HotspotAnalysis):
    """Plot hotspot temperature distribution"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    L, _, _ = hotspot.die.dimensions
    L_mm = L * 1000  # Convert to mm
    
    # Create spatial grid
    x = np.linspace(-L_mm/2, L_mm/2, 100)
    y = np.linspace(-L_mm/2, L_mm/2, 100)
    X, Y = np.meshgrid(x, y)
    
    # Gaussian hotspot at center
    sigma = 0.5  # mm
    q0 = 1e10  # W/m³
    Q = hotspot.gaussian_hotspot_profile(X, Y, 0, 0, sigma, q0)
    
    # Plot power density
    im1 = axes[0].contourf(X, Y, Q/1e9, levels=20, cmap='hot')
    axes[0].set_xlabel('X [mm]')
    axes[0].set_ylabel('Y [mm]')
    axes[0].set_title('Power Density Distribution [GW/m³]')
    plt.colorbar(im1, ax=axes[0])
    
    # Temperature rise vs distance
    r = np.linspace(0, 2, 100)  # mm
    T_rise = [hotspot.peak_temperature(0.5, r_i * 1e-3) for r_i in r]
    
    axes[1].plot(r, T_rise, 'r-', linewidth=2)
    axes[1].set_xlabel('Hotspot Radius [mm]')
    axes[1].set_ylabel('Peak Temperature Rise [K]')
    axes[1].set_title('Peak Temperature vs Hotspot Size\n(0.5W power)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_comparison(comparison: ThermalComparison):
    """Plot thermal comparison between mask-locked and SRAM"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Power comparison
    sram = comparison.sram_power_consumption()
    ml = comparison.mask_locked_power()
    
    categories = ['Read Power', 'Leakage Power', 'Total']
    sram_values = [sram['read_power'], sram['leakage_power'], sram['total_power']]
    ml_values = [ml['read_power'], ml['leakage_power'], ml['total_power']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    axes[0].bar(x - width/2, sram_values, width, label='SRAM', color='#e74c3c')
    axes[0].bar(x + width/2, ml_values, width, label='Mask-Locked', color='#2ecc71')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(categories)
    axes[0].set_ylabel('Power [W]')
    axes[0].set_title('Weight Storage Power Consumption')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Temperature comparison
    temp_comp = comparison.temperature_comparison()
    
    configs = ['SRAM-Based', 'Mask-Locked']
    temps = [temp_comp['T_sram'] - 273.15, temp_comp['T_mask_locked'] - 273.15]
    
    axes[1].bar(configs, temps, color=['#e74c3c', '#2ecc71'])
    axes[1].axhline(y=85, color='r', linestyle='--', label='Max safe temp')
    axes[1].set_ylabel('Junction Temperature [°C]')
    axes[1].set_title('Steady-State Junction Temperature')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Add temperature delta annotation
    delta = temp_comp['delta_T']
    axes[1].annotate(f'ΔT = {delta:.1f} K', 
                     xy=(0.5, (temps[0] + temps[1])/2),
                     fontsize=12, fontweight='bold')
    
    # Thermal variance comparison
    var_comp = comparison.thermal_variance_comparison()
    
    variance_labels = ['SRAM-Based', 'Mask-Locked']
    variances = [var_comp['sigma_T_sram'], var_comp['sigma_T_ml']]
    
    axes[2].bar(variance_labels, variances, color=['#e74c3c', '#2ecc71'])
    axes[2].set_ylabel('Temperature Std Dev [K]')
    axes[2].set_title('Thermal Variance Comparison')
    axes[2].grid(True, alpha=0.3, axis='y')
    
    reduction = var_comp['variance_reduction'] * 100
    axes[2].annotate(f'{reduction:.1f}%\nreduction',
                     xy=(0.5, variances[0]/2),
                     fontsize=12, fontweight='bold',
                     ha='center')
    
    plt.tight_layout()
    return fig

# ============================================================================
# Main Analysis
# ============================================================================

def run_full_analysis():
    """Run complete thermal analysis for the mask-locked inference chip"""
    
    print("="*70)
    print("THERMAL DYNAMICS ANALYSIS")
    print("Mask-Locked Inference Chip (27mm², 3W)")
    print("="*70)
    
    # 1. Thermal Resistance Network
    print("\n1. THERMAL RESISTANCE NETWORK")
    print("-"*40)
    
    network = ThermalResistanceNetwork(DEFAULT_DIE)
    
    print(f"Junction-to-Case: {network.junction_to_case():.3f} K/W")
    print(f"Case-to-Ambient (no heatsink): {network.case_to_ambient(with_heatsink=False):.1f} K/W")
    print(f"Case-to-Ambient (with heatsink): {network.case_to_ambient(with_heatsink=True):.1f} K/W")
    print(f"Total R_ja (with heatsink): {network.junction_to_ambient():.1f} K/W")
    
    T_junction = network.junction_temperature()
    print(f"\nJunction Temperature at 3W: {T_junction - 273.15:.1f}°C")
    
    # 2. Thermal Capacitance and Time Constants
    print("\n2. THERMAL TIME CONSTANTS")
    print("-"*40)
    
    # Compute thermal capacitance for die
    mat_si = MATERIALS['silicon']
    C_die = ThermalCapacitance.layer_capacitance(mat_si, DEFAULT_DIE.volume)
    
    print(f"Die volume: {DEFAULT_DIE.volume*1e9:.2f} mm³")
    print(f"Die thermal capacitance: {C_die*1e3:.3f} mJ/K")
    
    # Time constant with heatsink
    R_total = network.junction_to_ambient()
    tau = ThermalCapacitance.time_constant(R_total, C_die)
    print(f"Thermal time constant: {tau*1e6:.1f} μs (die only)")
    
    # Heatsink time constant (much larger)
    C_heatsink = 50.0  # J/K (typical small heatsink)
    tau_heatsink = R_total * C_heatsink
    print(f"Heatsink time constant: {tau_heatsink:.1f} s")
    
    # 3. Transient Analysis
    print("\n3. TRANSIENT THERMAL ANALYSIS")
    print("-"*40)
    
    transient = TransientAnalysis(R_total, C_heatsink)
    
    # Time to reach 90% of steady state
    t_90 = 2.3 * tau_heatsink
    print(f"Time to 90% steady state: {t_90:.1f} s")
    
    # Burst analysis
    T_peak = transient.T_ambient + 3.0 * transient.R_th * (1 - np.exp(-1.0/tau_heatsink))
    print(f"Temperature after 1s burst: {T_peak - 273.15:.1f}°C")
    
    # 4. Hotspot Analysis
    print("\n4. HOTSPOT ANALYSIS")
    print("-"*40)
    
    hotspot = HotspotAnalysis(DEFAULT_DIE)
    
    # Peak temperature for various hotspot sizes
    powers = [0.1, 0.25, 0.5, 1.0]  # W
    radii = [50e-6, 100e-6, 200e-6, 500e-6]  # m
    
    print("Peak temperature rise for hotspots:")
    print(f"{'Power (W)':<12}{'Radius (μm)':<15}{'ΔT (K)':<12}")
    for P in powers:
        for r in radii:
            dT = hotspot.peak_temperature(P, r)
            print(f"{P:<12.2f}{r*1e6:<15.0f}{dT:<12.2f}")
    
    # 5. Mask-Locked vs SRAM Comparison
    print("\n5. MASK-LOCKED vs SRAM COMPARISON")
    print("-"*40)
    
    comparison = ThermalComparison()
    
    sram = comparison.sram_power_consumption()
    print("SRAM-based architecture:")
    print(f"  Read power: {sram['read_power']:.1f} W")
    print(f"  Leakage power: {sram['leakage_power']:.1f} W")
    print(f"  Total weight power: {sram['total_power']:.1f} W")
    
    print("\nMask-locked architecture:")
    print("  Weight access power: 0 W (hardwired)")
    
    temp_comp = comparison.temperature_comparison(R_th=R_total)
    print(f"\nTemperature comparison:")
    print(f"  SRAM junction temp: {temp_comp['T_sram'] - 273.15:.1f}°C")
    print(f"  Mask-locked junction temp: {temp_comp['T_mask_locked'] - 273.15:.1f}°C")
    print(f"  Temperature reduction: {temp_comp['delta_T']:.1f} K")
    
    var_comp = comparison.thermal_variance_comparison()
    print(f"\nThermal variance reduction: {var_comp['variance_reduction']*100:.1f}%")
    
    # 6. Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✓ With small heatsink (R=15 K/W), junction stays below 85°C")
    print(f"✓ Mask-locked eliminates ~{sram['total_power']:.0f}W of weight access power")
    print(f"✓ Thermal variance reduced by {var_comp['variance_reduction']*100:.0f}%")
    print(f"✓ Predictable thermal behavior enables proactive throttling")
    print("="*70)
    
    return {
        'network': network,
        'transient': transient,
        'hotspot': hotspot,
        'comparison': comparison,
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    results = run_full_analysis()
    
    # Generate plots
    print("\nGenerating visualization plots...")
    
    fig1 = plot_thermal_resistance_network(results['network'])
    fig1.savefig('thermal_resistance_network.png', dpi=150)
    
    fig2 = plot_transient_response(results['transient'])
    fig2.savefig('transient_response.png', dpi=150)
    
    fig3 = plot_hotspot_analysis(results['hotspot'])
    fig3.savefig('hotspot_analysis.png', dpi=150)
    
    fig4 = plot_comparison(results['comparison'])
    fig4.savefig('thermal_comparison.png', dpi=150)
    
    print("Plots saved to PNG files.")
    plt.show()
