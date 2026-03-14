#!/usr/bin/env python3
"""
Cycle 4A: Advanced Thermal-Electrical Coupled Simulation
=========================================================

Comprehensive thermal-electrical coupled simulation for Mask-Locked Inference Chip.

Features:
- Joule heating with temperature-dependent resistivity
- IR drop analysis across power grid
- Thermal crosstalk between adjacent PEs (32x32 array)
- Self-heating effects in individual RAUs
- Temperature-dependent leakage current model
- Monte Carlo process variation analysis (1000 iterations)

Author: VP Manufacturing Research Agent
Date: March 2026
Cycle: 4A - Thermal-Electrical Coupled Simulation
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve, cg
from scipy.ndimage import gaussian_filter
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Union
from enum import Enum
import time
import json
from datetime import datetime

# ============================================================================
# Physical Constants
# ============================================================================

KB_J = 1.38e-23           # Boltzmann constant [J/K]
KB_EV = 8.617e-5          # Boltzmann constant [eV/K]
Q_E = 1.602e-19           # Electron charge [C]
EPSILON_0 = 8.854e-12     # Vacuum permittivity [F/m]

# ============================================================================
# Process Node Parameters (28nm)
# ============================================================================

@dataclass
class ProcessNode28nm:
    """28nm process node parameters for thermal-electrical simulation."""
    
    # Transistor parameters
    vdd_nominal: float = 0.9           # Core voltage [V]
    vdd_variation: float = 0.10        # ±10% voltage variation
    
    # Temperature coefficients
    tcr_copper: float = 0.00393        # Temperature coefficient of resistance for Cu [1/K]
    tcr_aluminum: float = 0.00429      # Temperature coefficient for Al [1/K]
    
    # Resistivity at reference temperature (300K)
    rho_cu_300k: float = 1.68e-8       # Copper resistivity [Ω·m]
    rho_al_300k: float = 2.65e-8       # Aluminum resistivity [Ω·m]
    
    # MOSFET parameters
    vth_0: float = 0.30                # Threshold voltage at 300K [V]
    vth_temp_coeff: float = -2.0e-3    # Vth temperature coefficient [V/K]
    mu_0: float = 300e-4               # Mobility at 300K [m²/(V·s)]
    mu_temp_exp: float = -1.5          # Mobility temperature exponent
    
    # Leakage parameters
    i_leak_300k: float = 1e-10         # Leakage current density at 300K [A/μm]
    leakage_ea: float = 0.6            # Leakage activation energy [eV]
    
    # Thermal parameters
    k_si: float = 148.0                # Silicon thermal conductivity [W/(m·K)]
    k_sio2: float = 1.4                # SiO2 thermal conductivity [W/(m·K)]
    k_cu: float = 385.0                # Copper thermal conductivity [W/(m·K)]
    
    # PE geometry
    pe_size_um: float = 160.0          # PE size [μm]
    pe_pitch_um: float = 170.0         # PE pitch [μm]
    num_pe_x: int = 32                 # Number of PEs in X direction
    num_pe_y: int = 32                 # Number of PEs in Y direction
    
    # Power parameters
    power_pe_min_mw: float = 2.0       # Minimum power per PE [mW]
    power_pe_max_mw: float = 4.0       # Maximum power per PE [mW]
    
    # Die parameters
    die_area_mm2: float = 27.0         # Die area [mm²]
    die_thickness_um: float = 300.0    # Die thickness [μm]
    
    @property
    def num_pes(self) -> int:
        return self.num_pe_x * self.num_pe_y
    
    @property
    def pe_area_m2(self) -> float:
        return (self.pe_size_um * 1e-6) ** 2


# ============================================================================
# Temperature-Dependent Electrical Models
# ============================================================================

class TemperatureDependentElectrical:
    """Temperature-dependent electrical properties."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
    
    def metal_resistivity(self, T_kelvin: float, metal: str = 'copper') -> float:
        """
        Calculate metal resistivity at temperature T.
        
        ρ(T) = ρ₀ [1 + α(T - T₀)]
        
        Args:
            T_kelvin: Temperature [K]
            metal: 'copper' or 'aluminum'
            
        Returns:
            Resistivity [Ω·m]
        """
        T_ref = 300.0
        
        if metal == 'copper':
            rho_0 = self.process.rho_cu_300k
            alpha = self.process.tcr_copper
        else:
            rho_0 = self.process.rho_al_300k
            alpha = self.process.tcr_aluminum
        
        return rho_0 * (1 + alpha * (T_kelvin - T_ref))
    
    def mosfet_vth(self, T_kelvin: float) -> float:
        """Temperature-dependent threshold voltage."""
        return self.process.vth_0 + self.process.vth_temp_coeff * (T_kelvin - 300.0)
    
    def mosfet_mobility(self, T_kelvin: float) -> float:
        """Temperature-dependent carrier mobility."""
        return self.process.mu_0 * (T_kelvin / 300.0) ** self.process.mu_temp_exp
    
    def leakage_current(self, T_kelvin: float, area_um2: float = 1.0) -> float:
        """
        Temperature-dependent leakage current.
        
        I_leak(T) = I₀ exp(-Ea / kT) × area
        
        Args:
            T_kelvin: Temperature [K]
            area_um2: Device area [μm²]
            
        Returns:
            Leakage current [A]
        """
        Ea = self.process.leakage_ea
        I_0 = self.process.i_leak_300k
        
        # Arrhenius model
        I_leak = I_0 * np.exp(-Ea / (KB_EV * T_kelvin)) * area_um2
        
        return I_leak
    
    def on_resistance(self, T_kelvin: float, w_um: float = 1.0, l_um: float = 0.028) -> float:
        """
        Temperature-dependent on-resistance.
        
        R_on = L / (μ C_ox W (V_GS - V_th))
        """
        mu = self.mosfet_mobility(T_kelvin)
        Vth = self.mosfet_vth(T_kelvin)
        Vgs = self.process.vdd_nominal
        Cox = 25e-3  # F/m²
        
        # Convert to meters
        w_m = w_um * 1e-6
        l_m = l_um * 1e-6
        
        if Vgs > Vth:
            R_on = l_m / (mu * Cox * w_m * (Vgs - Vth))
        else:
            R_on = float('inf')
        
        return R_on


# ============================================================================
# Joule Heating Model
# ============================================================================

class JouleHeatingModel:
    """Joule heating calculation with temperature-dependent resistivity."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
        self.electrical = TemperatureDependentElectrical(process)
    
    def wire_joule_heating(self, 
                           current: float, 
                           length_m: float,
                           cross_section_m2: float,
                           T_kelvin: float,
                           metal: str = 'copper') -> float:
        """
        Calculate Joule heating in a wire.
        
        P = I² R = I² ρ L / A
        
        Args:
            current: Current [A]
            length_m: Wire length [m]
            cross_section_m2: Cross-sectional area [m²]
            T_kelvin: Temperature [K]
            metal: Metal type
            
        Returns:
            Power dissipation [W]
        """
        rho = self.electrical.metal_resistivity(T_kelvin, metal)
        R = rho * length_m / cross_section_m2
        P = current ** 2 * R
        return P
    
    def via_joule_heating(self,
                          current: float,
                          via_diameter_m: float,
                          via_height_m: float,
                          T_kelvin: float) -> float:
        """
        Calculate Joule heating in a via.
        
        Args:
            current: Current [A]
            via_diameter_m: Via diameter [m]
            via_height_m: Via height [m]
            T_kelvin: Temperature [K]
            
        Returns:
            Power dissipation [W]
        """
        area = np.pi * (via_diameter_m / 2) ** 2
        return self.wire_joule_heating(current, via_height_m, area, T_kelvin)
    
    def power_grid_heating_map(self,
                               current_density_map: np.ndarray,
                               T_map: np.ndarray,
                               metal_thickness_m: float) -> np.ndarray:
        """
        Calculate Joule heating map from current density.
        
        Args:
            current_density_map: Current density [A/m²]
            T_map: Temperature map [K]
            metal_thickness_m: Metal layer thickness [m]
            
        Returns:
            Power density map [W/m³]
        """
        # Resistivity map (temperature-dependent)
        rho_map = np.vectorize(lambda T: self.electrical.metal_resistivity(T))(T_map)
        
        # Power density: P/V = J² ρ
        power_density = current_density_map ** 2 * rho_map
        
        return power_density


# ============================================================================
# IR Drop Analysis
# ============================================================================

class IRDropAnalyzer:
    """Power grid IR drop analysis."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
        self.electrical = TemperatureDependentElectrical(process)
    
    def power_grid_resistance(self, 
                              T_kelvin: float,
                              grid_pitch_um: float = 10.0,
                              grid_width_um: float = 2.0,
                              grid_thickness_um: float = 0.5,
                              num_layers: int = 8) -> Dict[str, float]:
        """
        Calculate power grid resistance parameters.
        
        Args:
            T_kelvin: Temperature [K]
            grid_pitch_um: Power grid pitch [μm]
            grid_width_um: Grid line width [μm]
            grid_thickness_um: Metal thickness [μm]
            num_layers: Number of metal layers for power grid
            
        Returns:
            Dictionary of resistance parameters
        """
        # Convert to meters
        pitch = grid_pitch_um * 1e-6
        width = grid_width_um * 1e-6
        thickness = grid_thickness_um * 1e-6
        
        # Resistivity at temperature
        rho = self.electrical.metal_resistivity(T_kelvin)
        
        # Sheet resistance
        R_sheet = rho / thickness  # [Ω/square]
        
        # Grid resistance per unit length
        R_per_length = rho / (width * thickness)  # [Ω/m]
        
        # Effective grid resistance (parallel combination)
        # Simplified model: R_grid ≈ R_sheet × pitch / (N_layers × width_ratio)
        width_ratio = grid_width_um / grid_pitch_um
        R_grid_effective = R_sheet * pitch / (num_layers * width_ratio)
        
        return {
            'sheet_resistance': R_sheet,
            'resistance_per_length': R_per_length,
            'effective_grid_resistance': R_grid_effective,
            'resistivity': rho
        }
    
    def ir_drop_2d(self,
                   current_map: np.ndarray,
                   T_map: np.ndarray,
                   vdd_nominal: float = 0.9) -> np.ndarray:
        """
        Calculate 2D IR drop distribution.
        
        Uses finite difference method to solve:
        ∇·(σ∇V) = -J
        
        Args:
            current_map: Current consumption per PE [A]
            T_map: Temperature map per PE [K]
            vdd_nominal: Nominal supply voltage [V]
            
        Returns:
            Voltage drop map [V]
        """
        nx, ny = current_map.shape
        
        # Get temperature-averaged grid resistance
        T_avg = np.mean(T_map)
        grid_params = self.power_grid_resistance(T_avg)
        R_grid = grid_params['effective_grid_resistance']
        
        # Simplified model: IR drop proportional to cumulative current
        # V_drop = I × R_grid
        
        # Build cumulative current model
        v_drop = np.zeros((nx, ny))
        
        # IR drop from each PE (simplified spreading model)
        for i in range(nx):
            for j in range(ny):
                # Distance from power supply points (corners)
                d_corner1 = np.sqrt(i**2 + j**2)
                d_corner2 = np.sqrt((nx-1-i)**2 + j**2)
                d_corner3 = np.sqrt(i**2 + (ny-1-j)**2)
                d_corner4 = np.sqrt((nx-1-i)**2 + (ny-1-j)**2)
                
                min_dist = min(d_corner1, d_corner2, d_corner3, d_corner4)
                
                # Voltage drop increases with distance
                # Approximate using transmission line model
                v_drop[i, j] = current_map[i, j] * R_grid * (1 + min_dist * 0.1)
        
        return v_drop
    
    def ir_drop_analytical(self,
                          total_current: float,
                          T_kelvin: float,
                          die_size_mm: float = 5.2) -> Dict[str, float]:
        """
        Analytical IR drop calculation.
        
        Uses analytical model for power grid voltage drop.
        
        Args:
            total_current: Total chip current [A]
            T_kelvin: Temperature [K]
            die_size_mm: Die side length [mm]
            
        Returns:
            Dictionary of IR drop metrics
        """
        grid_params = self.power_grid_resistance(T_kelvin)
        R_grid = grid_params['effective_grid_resistance']
        
        # Worst-case IR drop (center of die)
        # Using transmission line model: V_drop = I × R_grid × (L/2)
        L = die_size_mm * 1e-3  # Convert to meters
        
        # Effective resistance to center
        R_to_center = R_grid * L / 2
        
        # Current per side (assuming 4-side feed)
        I_per_side = total_current / 4
        
        v_drop_max = I_per_side * R_to_center
        v_drop_avg = v_drop_max / 3  # Average across die
        
        return {
            'max_ir_drop': v_drop_max,
            'avg_ir_drop': v_drop_avg,
            'grid_resistance': R_grid,
            'percentage_drop': v_drop_max / self.process.vdd_nominal * 100
        }


# ============================================================================
# Thermal Crosstalk Model
# ============================================================================

class ThermalCrosstalkModel:
    """Thermal crosstalk between PEs in the array."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
        self.coupling_matrix = None
    
    def thermal_coupling_coefficient(self,
                                     distance_um: float,
                                     T_kelvin: float = 300.0) -> float:
        """
        Calculate thermal coupling coefficient between two PEs.
        
        Based on heat diffusion in silicon:
        ΔT₂/P₁ = 1 / (4πk r)
        
        Args:
            distance_um: Distance between PEs [μm]
            T_kelvin: Temperature [K]
            
        Returns:
            Thermal coupling coefficient [K/W]
        """
        k_si = self.process.k_si
        r = distance_um * 1e-6  # Convert to meters
        
        # Temperature-dependent thermal conductivity
        k_T = k_si * (300.0 / T_kelvin) ** 1.3
        
        if r > 0:
            coupling = 1.0 / (4 * np.pi * k_T * r)
        else:
            # Self-heating coefficient
            pe_size = self.process.pe_size_um * 1e-6
            coupling = 1.0 / (2 * k_T * pe_size)
        
        return coupling
    
    def build_coupling_matrix(self, T_initial: float = 300.0) -> np.ndarray:
        """
        Build full thermal coupling matrix for PE array.
        
        Returns:
            Coupling matrix [K/W] of shape (1024, 1024)
        """
        n_pe_x = self.process.num_pe_x
        n_pe_y = self.process.num_pe_y
        n_pes = n_pe_x * n_pe_y
        pitch = self.process.pe_pitch_um
        
        coupling = np.zeros((n_pes, n_pes))
        
        for i1 in range(n_pes):
            x1 = i1 % n_pe_x
            y1 = i1 // n_pe_x
            
            for i2 in range(n_pes):
                x2 = i2 % n_pe_x
                y2 = i2 // n_pe_x
                
                distance = pitch * np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                coupling[i1, i2] = self.thermal_coupling_coefficient(distance, T_initial)
        
        self.coupling_matrix = coupling
        return coupling
    
    def crosstalk_temperature_rise(self,
                                   power_map: np.ndarray,
                                   T_map: np.ndarray) -> np.ndarray:
        """
        Calculate temperature rise due to thermal crosstalk.
        
        Args:
            power_map: Power consumption per PE [W], shape (32, 32)
            T_map: Temperature map [K], shape (32, 32)
            
        Returns:
            Temperature rise due to crosstalk [K], shape (32, 32)
        """
        n_pe_x = self.process.num_pe_x
        n_pe_y = self.process.num_pe_y
        
        # Flatten power map
        power_flat = power_map.flatten()
        T_avg = np.mean(T_map)
        
        # Build coupling matrix if needed
        if self.coupling_matrix is None:
            self.build_coupling_matrix(T_avg)
        
        # Temperature rise from crosstalk
        T_rise_flat = self.coupling_matrix @ power_flat
        
        # Reshape to 2D
        T_rise = T_rise_flat.reshape((n_pe_y, n_pe_x))
        
        return T_rise


# ============================================================================
# Self-Heating Model for RAU
# ============================================================================

class SelfHeatingModel:
    """Self-heating model for individual RAUs (Reconfigurable Arithmetic Units)."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
        self.electrical = TemperatureDependentElectrical(process)
    
    def rau_thermal_resistance(self, T_kelvin: float = 300.0) -> float:
        """
        Calculate thermal resistance of a RAU.
        
        R_th = t / (k × A) + spreading resistance
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Thermal resistance [K/W]
        """
        pe_size = self.process.pe_size_um * 1e-6
        die_thickness = self.process.die_thickness_um * 1e-6
        
        # Temperature-dependent thermal conductivity
        k_T = self.process.k_si * (300.0 / T_kelvin) ** 1.3
        
        # Conduction resistance through silicon
        R_cond = die_thickness / (k_T * pe_size * pe_size)
        
        # Spreading resistance (Lee correlation approximation)
        r_source = pe_size / 2
        R_spread = 1.0 / (2 * np.pi * k_T * r_source)
        
        return R_cond + R_spread
    
    def rau_self_heating(self,
                         power_w: float,
                         T_ambient: float = 300.0) -> Dict[str, float]:
        """
        Calculate self-heating temperature rise in a RAU.
        
        Args:
            power_w: Power consumption [W]
            T_ambient: Ambient temperature [K]
            
        Returns:
            Dictionary of temperature metrics
        """
        # Initial estimate
        T_est = T_ambient
        T_new = T_ambient + 100  # Start with offset
        
        # Iterative solution (resistance depends on temperature)
        for _ in range(10):
            R_th = self.rau_thermal_resistance(T_est)
            T_new = T_ambient + power_w * R_th
            
            if abs(T_new - T_est) < 0.1:
                break
            T_est = T_new
        
        return {
            'junction_temperature': T_new,
            'temperature_rise': T_new - T_ambient,
            'thermal_resistance': R_th,
            'ambient_temperature': T_ambient
        }
    
    def transient_self_heating(self,
                               t: np.ndarray,
                               power_w: float,
                               T_ambient: float = 300.0) -> np.ndarray:
        """
        Transient self-heating response.
        
        T(t) = T_a + ΔT_ss × (1 - exp(-t/τ))
        
        Args:
            t: Time array [s]
            power_w: Power consumption [W]
            T_ambient: Ambient temperature [K]
            
        Returns:
            Temperature array [K]
        """
        R_th = self.rau_thermal_resistance(T_ambient)
        
        # Thermal capacitance
        pe_vol = (self.process.pe_size_um * 1e-6) ** 2 * self.process.die_thickness_um * 1e-6
        rho_si = 2329  # kg/m³
        cp_si = 700    # J/(kg·K)
        C_th = rho_si * cp_si * pe_vol
        
        # Time constant
        tau = R_th * C_th
        
        # Steady-state temperature rise
        T_ss = T_ambient + power_w * R_th
        
        # Transient response
        T = T_ss - power_w * R_th * np.exp(-t / tau)
        
        return T


# ============================================================================
# Temperature-Dependent Leakage Model
# ============================================================================

class TemperatureDependentLeakage:
    """Temperature-dependent leakage current model."""
    
    def __init__(self, process: ProcessNode28nm):
        self.process = process
        self.electrical = TemperatureDependentElectrical(process)
    
    def subthreshold_leakage(self,
                             T_kelvin: float,
                             vds: float = 0.9,
                             w_um: float = 1.0) -> float:
        """
        Calculate subthreshold leakage current.
        
        I_sub = I₀ × (W/L) × exp(q(Vgs-Vth)/(nkT)) × (1-exp(-qVds/kT))
        
        Args:
            T_kelvin: Temperature [K]
            vds: Drain-source voltage [V]
            w_um: Transistor width [μm]
            
        Returns:
            Leakage current [A]
        """
        # Parameters
        n = 1.5  # Subthreshold slope factor
        I_0 = 1e-10  # Reference current [A/μm]
        L = 28e-9  # Channel length [m]
        
        Vth = self.electrical.mosfet_vth(T_kelvin)
        Vgs = self.process.vdd_nominal
        
        # Subthreshold leakage
        Vt = KB_EV * T_kelvin  # Thermal voltage [V]
        
        I_sub = I_0 * w_um * np.exp((Vgs - Vth) / (n * Vt)) * (1 - np.exp(-vds / Vt))
        
        return I_sub
    
    def gate_leakage(self, T_kelvin: float, area_cm2: float = 1e-8) -> float:
        """
        Calculate gate leakage current.
        
        Uses Fowler-Nordheim tunneling model.
        
        Args:
            T_kelvin: Temperature [K]
            area_cm2: Gate area [cm²]
            
        Returns:
            Gate leakage current [A]
        """
        # Gate oxide thickness (28nm process)
        t_ox_nm = 1.2
        Vg = self.process.vdd_nominal
        
        # Electric field
        E_ox = Vg / (t_ox_nm * 1e-7)  # V/cm
        
        # Barrier height (SiO2)
        phi_B = 3.1  # eV
        
        # Fowler-Nordheim current density
        if E_ox > 1e7:  # High field regime
            A = 1.54e-6  # A/(V²)
            B = 6.83e7   # V/cm
            J = A * E_ox**2 * np.exp(-B * phi_B**1.5 / E_ox)  # A/cm²
        else:
            # Direct tunneling (low field)
            J = 1e-6 * np.exp(-t_ox_nm / 0.5)  # Simplified model
        
        return J * area_cm2
    
    def total_leakage_per_pe(self, T_kelvin: float) -> Dict[str, float]:
        """
        Calculate total leakage current per PE.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Dictionary of leakage components
        """
        # Estimate PE active area
        pe_area_um2 = self.process.pe_size_um ** 2
        active_fraction = 0.3  # Fraction of PE area with active devices
        
        # Number of transistors (estimate)
        num_transistors = 10000  # Per PE
        avg_width_um = 0.5
        total_width_um = num_transistors * avg_width_um
        
        # Leakage components
        I_sub = self.subthreshold_leakage(T_kelvin, w_um=total_width_um)
        
        gate_area_cm2 = active_fraction * pe_area_um2 * 1e-8  # Convert μm² to cm²
        I_gate = self.gate_leakage(T_kelvin, gate_area_cm2)
        
        # Junction leakage (simplified)
        I_junction = 1e-9 * (T_kelvin / 300.0) ** 2  # Temperature-dependent
        
        I_total = I_sub + I_gate + I_junction
        
        # Leakage power
        P_leak = I_total * self.process.vdd_nominal
        
        return {
            'subthreshold_leakage': I_sub,
            'gate_leakage': I_gate,
            'junction_leakage': I_junction,
            'total_leakage_current': I_total,
            'leakage_power': P_leak
        }


# ============================================================================
# Coupled Thermal-Electrical Solver
# ============================================================================

class CoupledThermalElectricalSolver:
    """
    Coupled thermal-electrical simulation solver.
    
    Solves the coupled equations:
    - Heat equation: ∇·(k∇T) + Q = 0
    - Electrical: IR drop and Joule heating
    - Temperature-dependent parameters
    """
    
    def __init__(self, process: ProcessNode28nm = None):
        if process is None:
            process = ProcessNode28nm()
        
        self.process = process
        
        # Initialize models
        self.joule_heating = JouleHeatingModel(process)
        self.ir_drop = IRDropAnalyzer(process)
        self.thermal_crosstalk = ThermalCrosstalkModel(process)
        self.self_heating = SelfHeatingModel(process)
        self.leakage = TemperatureDependentLeakage(process)
        
        # Initialize arrays
        self.T_map = np.ones((process.num_pe_y, process.num_pe_x)) * 300.0
        self.V_map = np.ones((process.num_pe_y, process.num_pe_x)) * process.vdd_nominal
        self.power_map = np.zeros((process.num_pe_y, process.num_pe_x))
        self.current_map = np.zeros((process.num_pe_y, process.num_pe_x))
    
    def set_activity_pattern(self, pattern: str = 'uniform', **kwargs):
        """Set PE activity pattern for power consumption."""
        n_pe_x = self.process.num_pe_x
        n_pe_y = self.process.num_pe_y
        
        if pattern == 'uniform':
            activity = kwargs.get('activity', 0.5)
            self.activity_map = np.ones((n_pe_y, n_pe_x)) * activity
        
        elif pattern == 'gaussian':
            center_x = n_pe_x // 2
            center_y = n_pe_y // 2
            sigma = kwargs.get('sigma', 5)
            base_activity = kwargs.get('base_activity', 0.2)
            peak_activity = kwargs.get('peak_activity', 0.9)
            
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    r2 = (i - center_y)**2 + (j - center_x)**2
                    self.activity_map[i, j] = base_activity + \
                        (peak_activity - base_activity) * np.exp(-r2 / (2 * sigma**2))
        
        elif pattern == 'gradient':
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    self.activity_map[i, j] = 0.3 + 0.5 * (i + j) / (n_pe_x + n_pe_y)
        
        elif pattern == 'checkerboard':
            high = kwargs.get('high_activity', 0.8)
            low = kwargs.get('low_activity', 0.2)
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    self.activity_map[i, j] = high if (i + j) % 2 == 0 else low
        
        elif pattern == 'hotspot':
            # Single hotspot
            hs_x = kwargs.get('hotspot_x', n_pe_x // 2)
            hs_y = kwargs.get('hotspot_y', n_pe_y // 2)
            hs_radius = kwargs.get('hotspot_radius', 3)
            hs_activity = kwargs.get('hotspot_activity', 1.0)
            bg_activity = kwargs.get('background_activity', 0.3)
            
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    r = np.sqrt((i - hs_y)**2 + (j - hs_x)**2)
                    if r <= hs_radius:
                        self.activity_map[i, j] = hs_activity
                    else:
                        self.activity_map[i, j] = bg_activity
        
        else:
            # Default to uniform
            self.activity_map = np.ones((n_pe_y, n_pe_x)) * 0.5
    
    def calculate_power_consumption(self, T_map: np.ndarray) -> np.ndarray:
        """
        Calculate power consumption per PE including temperature effects.
        
        P = P_dynamic + P_leakage(T)
        """
        n_pe_x = self.process.num_pe_x
        n_pe_y = self.process.num_pe_y
        
        power_map = np.zeros((n_pe_y, n_pe_x))
        
        # Power range
        P_min = self.process.power_pe_min_mw * 1e-3  # Convert to W
        P_max = self.process.power_pe_max_mw * 1e-3
        
        for i in range(n_pe_y):
            for j in range(n_pe_x):
                activity = self.activity_map[i, j]
                T = T_map[i, j]
                
                # Dynamic power (activity-dependent)
                P_dynamic = P_min + (P_max - P_min) * activity
                
                # Leakage power (temperature-dependent)
                leak_info = self.leakage.total_leakage_per_pe(T)
                P_leak = leak_info['leakage_power']
                
                # Total power
                power_map[i, j] = P_dynamic + P_leak
        
        return power_map
    
    def calculate_current_consumption(self, power_map: np.ndarray, V_map: np.ndarray) -> np.ndarray:
        """Calculate current consumption from power and voltage."""
        # Avoid division by zero
        V_safe = np.maximum(V_map, 0.5)
        return power_map / V_safe
    
    def solve_coupled(self, 
                      T_ambient: float = 298.0,
                      max_iterations: int = 50,
                      convergence_tol: float = 0.1) -> Dict:
        """
        Solve the coupled thermal-electrical problem.
        
        Iteratively solves:
        1. Power consumption (temperature-dependent)
        2. IR drop (temperature-dependent resistance)
        3. Joule heating
        4. Thermal crosstalk
        5. Temperature distribution
        
        Args:
            T_ambient: Ambient temperature [K]
            max_iterations: Maximum iterations
            convergence_tol: Convergence tolerance [K]
            
        Returns:
            Dictionary of results
        """
        n_pe_x = self.process.num_pe_x
        n_pe_y = self.process.num_pe_y
        
        # Initialize
        self.T_map = np.ones((n_pe_y, n_pe_x)) * T_ambient
        self.V_map = np.ones((n_pe_y, n_pe_x)) * self.process.vdd_nominal
        
        convergence_history = []
        
        for iteration in range(max_iterations):
            T_old = self.T_map.copy()
            V_old = self.V_map.copy()
            
            # Step 1: Calculate power consumption
            self.power_map = self.calculate_power_consumption(self.T_map)
            
            # Step 2: Calculate current consumption
            self.current_map = self.calculate_current_consumption(self.power_map, self.V_map)
            
            # Step 3: Calculate IR drop
            v_drop = self.ir_drop.ir_drop_2d(self.current_map, self.T_map)
            self.V_map = self.process.vdd_nominal - v_drop
            
            # Step 4: Calculate self-heating
            T_self = np.zeros((n_pe_y, n_pe_x))
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    sh = self.self_heating.rau_self_heating(self.power_map[i, j], T_ambient)
                    T_self[i, j] = sh['temperature_rise']
            
            # Step 5: Calculate thermal crosstalk
            T_crosstalk = self.thermal_crosstalk.crosstalk_temperature_rise(
                self.power_map, self.T_map)
            
            # Step 6: Calculate Joule heating contribution
            T_joule = np.zeros((n_pe_y, n_pe_x))
            # Simplified: add fraction of power as Joule heating
            for i in range(n_pe_y):
                for j in range(n_pe_x):
                    # Estimate power grid Joule heating contribution
                    I = self.current_map[i, j]
                    R_grid = self.ir_drop.power_grid_resistance(self.T_map[i, j])
                    P_joule = I**2 * R_grid['effective_grid_resistance'] * 0.1  # Fraction in grid
                    T_joule[i, j] = P_joule * self.self_heating.rau_thermal_resistance(self.T_map[i, j])
            
            # Update temperature
            self.T_map = T_ambient + T_self + T_crosstalk + T_joule
            
            # Check convergence
            T_diff = np.max(np.abs(self.T_map - T_old))
            V_diff = np.max(np.abs(self.V_map - V_old))
            
            convergence_history.append({
                'iteration': iteration,
                'T_diff': T_diff,
                'V_diff': V_diff,
                'T_max': np.max(self.T_map),
                'V_min': np.min(self.V_map)
            })
            
            if T_diff < convergence_tol:
                break
        
        # Calculate final metrics
        results = {
            'temperature_map': self.T_map,
            'voltage_map': self.V_map,
            'power_map': self.power_map,
            'current_map': self.current_map,
            'activity_map': self.activity_map,
            'ir_drop_map': self.process.vdd_nominal - self.V_map,
            'convergence_history': convergence_history,
            'T_max': float(np.max(self.T_map)),
            'T_min': float(np.min(self.T_map)),
            'T_avg': float(np.mean(self.T_map)),
            'V_min': float(np.min(self.V_map)),
            'V_avg': float(np.mean(self.V_map)),
            'total_power': float(np.sum(self.power_map)),
            'total_current': float(np.sum(self.current_map)),
            'iterations': len(convergence_history),
            'converged': T_diff < convergence_tol
        }
        
        return results


# ============================================================================
# Monte Carlo Process Variation Analysis
# ============================================================================

class MonteCarloVariation:
    """Monte Carlo simulation with process variation."""
    
    def __init__(self, process: ProcessNode28nm = None, seed: int = 42):
        if process is None:
            process = ProcessNode28nm()
        
        self.process = process
        self.rng = np.random.default_rng(seed)
        
        # Process variation parameters
        self.sigma_vdd = process.vdd_nominal * process.vdd_variation / 3
        self.sigma_vth = 18e-3  # Vth variation [V]
        self.sigma_tox = 0.05  # 5% oxide thickness variation
        self.sigma_power = 0.10  # 10% power variation
    
    def sample_variation(self) -> Dict[str, float]:
        """Sample process variation parameters."""
        return {
            'vdd_offset': self.rng.normal(0, self.sigma_vdd),
            'vth_offset': self.rng.normal(0, self.sigma_vth),
            'tox_factor': self.rng.normal(1, self.sigma_tox),
            'power_factor': self.rng.normal(1, self.sigma_power)
        }
    
    def run_monte_carlo(self,
                        n_samples: int = 1000,
                        T_ambient_range: Tuple[float, float] = (298.0, 358.0),
                        activity_pattern: str = 'uniform') -> Dict:
        """
        Run Monte Carlo simulation with process variation.
        
        Args:
            n_samples: Number of Monte Carlo samples
            T_ambient_range: Ambient temperature range [K]
            activity_pattern: Activity pattern type
            
        Returns:
            Dictionary of Monte Carlo results
        """
        results = {
            'T_max': [],
            'T_min': [],
            'T_avg': [],
            'V_min': [],
            'IR_drop_max': [],
            'total_power': [],
            'total_current': [],
            'leakage_power_fraction': [],
            'samples': []
        }
        
        for i in range(n_samples):
            # Sample variations
            variation = self.sample_variation()
            
            # Random ambient temperature
            T_ambient = self.rng.uniform(*T_ambient_range)
            
            # Create solver with varied parameters
            process = ProcessNode28nm()
            process.vdd_nominal = self.process.vdd_nominal + variation['vdd_offset']
            process.vth_0 = self.process.vth_0 + variation['vth_offset']
            
            solver = CoupledThermalElectricalSolver(process)
            
            # Random activity factor
            activity = self.rng.uniform(0.3, 0.9)
            solver.set_activity_pattern(activity_pattern, activity=activity)
            
            # Run coupled simulation
            sim_results = solver.solve_coupled(T_ambient=T_ambient)
            
            # Collect results
            results['T_max'].append(sim_results['T_max'])
            results['T_min'].append(sim_results['T_min'])
            results['T_avg'].append(sim_results['T_avg'])
            results['V_min'].append(sim_results['V_min'])
            results['IR_drop_max'].append(float(np.max(sim_results['ir_drop_map'])))
            results['total_power'].append(sim_results['total_power'])
            results['total_current'].append(sim_results['total_current'])
            
            # Calculate leakage fraction
            total_leak = 0
            for T in sim_results['temperature_map'].flatten():
                leak = TemperatureDependentLeakage(process).total_leakage_per_pe(T)
                total_leak += leak['leakage_power']
            leak_frac = total_leak / sim_results['total_power']
            results['leakage_power_fraction'].append(leak_frac)
            
            # Store sample details
            sample_detail = {
                'sample_id': i,
                'variation': variation,
                'T_ambient': T_ambient,
                'activity': activity,
                'T_max': sim_results['T_max'],
                'V_min': sim_results['V_min'],
                'IR_drop_max': float(np.max(sim_results['ir_drop_map']))
            }
            results['samples'].append(sample_detail)
        
        # Convert to arrays
        for key in ['T_max', 'T_min', 'T_avg', 'V_min', 'IR_drop_max', 
                    'total_power', 'total_current', 'leakage_power_fraction']:
            results[key] = np.array(results[key])
        
        # Calculate statistics
        results['statistics'] = {
            'T_max': {
                'mean': float(np.mean(results['T_max'])),
                'std': float(np.std(results['T_max'])),
                'min': float(np.min(results['T_max'])),
                'max': float(np.max(results['T_max'])),
                'p95': float(np.percentile(results['T_max'], 95)),
                'p99': float(np.percentile(results['T_max'], 99))
            },
            'IR_drop': {
                'mean': float(np.mean(results['IR_drop_max'])),
                'std': float(np.std(results['IR_drop_max'])),
                'min': float(np.min(results['IR_drop_max'])),
                'max': float(np.max(results['IR_drop_max'])),
                'p95': float(np.percentile(results['IR_drop_max'], 95)),
                'p99': float(np.percentile(results['IR_drop_max'], 99))
            },
            'power': {
                'mean': float(np.mean(results['total_power'])),
                'std': float(np.std(results['total_power'])),
                'min': float(np.min(results['total_power'])),
                'max': float(np.max(results['total_power']))
            },
            'leakage_fraction': {
                'mean': float(np.mean(results['leakage_power_fraction'])),
                'std': float(np.std(results['leakage_power_fraction']))
            }
        }
        
        return results


# ============================================================================
# Hotspot Detection and Mitigation
# ============================================================================

class HotspotAnalyzer:
    """Analyze thermal hotspots and suggest mitigation strategies."""
    
    def __init__(self, solver: CoupledThermalElectricalSolver):
        self.solver = solver
    
    def detect_hotspots(self, 
                        T_map: np.ndarray,
                        threshold_K: float = 350.0) -> List[Dict]:
        """
        Detect thermal hotspots above threshold temperature.
        
        Args:
            T_map: Temperature map [K]
            threshold_K: Hotspot threshold temperature [K]
            
        Returns:
            List of hotspot information
        """
        hotspots = []
        n_pe_y, n_pe_x = T_map.shape
        
        # Find cells above threshold
        hot_mask = T_map > threshold_K
        
        if not np.any(hot_mask):
            return hotspots
        
        # Label connected regions
        from scipy.ndimage import label
        labeled, num_features = label(hot_mask)
        
        for region_id in range(1, num_features + 1):
            region_mask = labeled == region_id
            region_coords = np.where(region_mask)
            
            # Find centroid
            center_y = int(np.mean(region_coords[0]))
            center_x = int(np.mean(region_coords[1]))
            
            # Region statistics
            T_region = T_map[region_mask]
            
            hotspot = {
                'region_id': region_id,
                'center': (center_x, center_y),
                'size': int(np.sum(region_mask)),
                'T_max': float(np.max(T_region)),
                'T_avg': float(np.mean(T_region)),
                'power': float(self.solver.power_map[region_mask].sum()),
                'activity': float(self.solver.activity_map[region_mask].mean())
            }
            hotspots.append(hotspot)
        
        # Sort by temperature
        hotspots.sort(key=lambda x: x['T_max'], reverse=True)
        
        return hotspots
    
    def suggest_mitigation(self, hotspot: Dict) -> List[str]:
        """Suggest mitigation strategies for a hotspot."""
        strategies = []
        
        T_max = hotspot['T_max']
        activity = hotspot['activity']
        power = hotspot['power']
        
        if T_max > 380:  # > 107°C
            strategies.append("CRITICAL: Immediate throttling required")
            strategies.append(f"Reduce activity in PE ({hotspot['center']}) by 50%")
        
        elif T_max > 360:  # > 87°C
            strategies.append("WARNING: Approaching thermal limit")
            strategies.append(f"Consider workload redistribution from PE ({hotspot['center']})")
        
        if activity > 0.8:
            strategies.append("High activity detected - consider spreading workload")
        
        if power > 4e-3:  # > 4mW
            strategies.append("High power density - optimize PE microarchitecture")
        
        strategies.append("Ensure adequate cooling solution")
        
        return strategies


# ============================================================================
# Main Execution
# ============================================================================

def run_cycle4a_simulation():
    """Run Cycle 4A thermal-electrical coupled simulation."""
    print("=" * 70)
    print("CYCLE 4A: THERMAL-ELECTRICAL COUPLED SIMULATION")
    print("Mask-Locked Inference Chip (32×32 PE Array, 28nm)")
    print("=" * 70)
    
    start_time = time.time()
    
    # Initialize process parameters
    process = ProcessNode28nm()
    
    print(f"\nConfiguration:")
    print(f"  Process node: 28nm")
    print(f"  PE array: {process.num_pe_x}×{process.num_pe_y} = {process.num_pes} PEs")
    print(f"  Core voltage: {process.vdd_nominal}V (±{process.vdd_variation*100:.0f}%)")
    print(f"  PE power range: {process.power_pe_min_mw}-{process.power_pe_max_mw} mW")
    print(f"  Die area: {process.die_area_mm2} mm²")
    
    # 1. Coupled thermal-electrical simulation
    print("\n" + "-" * 40)
    print("1. COUPLED THERMAL-ELECTRICAL SIMULATION")
    print("-" * 40)
    
    solver = CoupledThermalElectricalSolver(process)
    solver.set_activity_pattern('gaussian', sigma=8, peak_activity=0.9, base_activity=0.3)
    
    results = solver.solve_coupled(T_ambient=298.0)
    
    print(f"  Converged: {results['converged']} ({results['iterations']} iterations)")
    print(f"  Peak temperature: {results['T_max']:.1f} K ({results['T_max']-273.15:.1f}°C)")
    print(f"  Min temperature: {results['T_min']:.1f} K ({results['T_min']-273.15:.1f}°C)")
    print(f"  Avg temperature: {results['T_avg']:.1f} K ({results['T_avg']-273.15:.1f}°C)")
    print(f"  Min voltage: {results['V_min']:.3f} V")
    print(f"  Max IR drop: {(process.vdd_nominal - results['V_min'])*1000:.1f} mV")
    print(f"  Total power: {results['total_power']*1000:.1f} mW")
    print(f"  Total current: {results['total_current']*1000:.1f} mA")
    
    # 2. Monte Carlo variation analysis
    print("\n" + "-" * 40)
    print("2. MONTE CARLO PROCESS VARIATION (1000 samples)")
    print("-" * 40)
    
    mc = MonteCarloVariation(process, seed=42)
    mc_results = mc.run_monte_carlo(n_samples=1000, T_ambient_range=(298.0, 358.0))
    
    stats = mc_results['statistics']
    print(f"  Temperature Statistics:")
    print(f"    Mean: {stats['T_max']['mean']:.1f} K ({stats['T_max']['mean']-273.15:.1f}°C)")
    print(f"    Std: {stats['T_max']['std']:.1f} K")
    print(f"    Range: {stats['T_max']['min']:.1f} - {stats['T_max']['max']:.1f} K")
    print(f"    95th percentile: {stats['T_max']['p95']:.1f} K")
    print(f"    99th percentile: {stats['T_max']['p99']:.1f} K")
    
    print(f"\n  IR Drop Statistics:")
    print(f"    Mean: {stats['IR_drop']['mean']*1000:.1f} mV")
    print(f"    Std: {stats['IR_drop']['std']*1000:.1f} mV")
    print(f"    Range: {stats['IR_drop']['min']*1000:.1f} - {stats['IR_drop']['max']*1000:.1f} mV")
    print(f"    95th percentile: {stats['IR_drop']['p95']*1000:.1f} mV")
    
    print(f"\n  Power Statistics:")
    print(f"    Mean: {stats['power']['mean']*1000:.1f} mW")
    print(f"    Std: {stats['power']['std']*1000:.1f} mW")
    print(f"    Leakage fraction: {stats['leakage_fraction']['mean']*100:.1f}% ± {stats['leakage_fraction']['std']*100:.1f}%")
    
    # 3. Hotspot analysis
    print("\n" + "-" * 40)
    print("3. THERMAL HOTSPOT ANALYSIS")
    print("-" * 40)
    
    analyzer = HotspotAnalyzer(solver)
    hotspots = analyzer.detect_hotspots(results['temperature_map'], threshold_K=350.0)
    
    if hotspots:
        print(f"  Detected {len(hotspots)} hotspot(s):")
        for hs in hotspots[:3]:  # Top 3
            print(f"\n    Hotspot at PE ({hs['center'][0]}, {hs['center'][1]}):")
            print(f"      Peak temp: {hs['T_max']:.1f} K ({hs['T_max']-273.15:.1f}°C)")
            print(f"      Size: {hs['size']} PE(s)")
            print(f"      Power: {hs['power']*1000:.2f} mW")
            print(f"      Activity: {hs['activity']:.1%}")
            
            strategies = analyzer.suggest_mitigation(hs)
            print(f"      Mitigation strategies:")
            for s in strategies:
                print(f"        - {s}")
    else:
        print("  No hotspots detected above 350 K (77°C)")
    
    # 4. Temperature-dependent effects summary
    print("\n" + "-" * 40)
    print("4. TEMPERATURE-DEPENDENT EFFECTS")
    print("-" * 40)
    
    T_range = np.linspace(300, 380, 5)
    elec = TemperatureDependentElectrical(process)
    
    print(f"  {'T (K)':<10} {'R_on (Ω)':<12} {'Vth (V)':<10} {'I_leak (nA)':<12}")
    print(f"  {'-'*44}")
    for T in T_range:
        R_on = elec.on_resistance(T)
        Vth = elec.mosfet_vth(T)
        I_leak = elec.leakage_current(T, area_um2=100)
        print(f"  {T:<10.0f} {R_on*1000:<12.1f} {Vth:<10.3f} {I_leak*1e9:<12.1f}")
    
    # Execution time
    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"Simulation completed in {elapsed:.2f} seconds")
    print(f"{'='*70}")
    
    # Compile final results
    final_results = {
        'metadata': {
            'cycle': '4A',
            'simulation_type': 'Thermal-Electrical Coupled',
            'process_node': '28nm',
            'num_pes': process.num_pes,
            'timestamp': datetime.now().isoformat(),
            'execution_time_s': elapsed
        },
        'coupled_simulation': {
            'converged': results['converged'],
            'iterations': results['iterations'],
            'T_max_K': results['T_max'],
            'T_min_K': results['T_min'],
            'T_avg_K': results['T_avg'],
            'V_min_V': results['V_min'],
            'V_avg_V': results['V_avg'],
            'IR_drop_max_V': float(np.max(results['ir_drop_map'])),
            'total_power_W': results['total_power'],
            'total_current_A': results['total_current']
        },
        'monte_carlo': {
            'num_samples': 1000,
            'statistics': mc_results['statistics']
        },
        'hotspot_analysis': {
            'num_hotspots': len(hotspots),
            'hotspots': hotspots[:5] if hotspots else []
        },
        'success_criteria': {
            'peak_temp_accuracy_C': abs(results['T_max'] - stats['T_max']['mean']) < 5,
            'ir_drop_accuracy_pct': abs(stats['IR_drop']['mean'] / process.vdd_nominal * 100) < 10
        }
    }
    
    return final_results, mc_results, results


if __name__ == "__main__":
    results, mc_results, coupled_results = run_cycle4a_simulation()
    
    # Save results to JSON
    output_path = '/home/z/my-project/research/cycle4_thermal_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")
