#!/usr/bin/env python3
"""
Simulation A3: Thermal Performance Simulation
==============================================
Thermal analysis for SuperInstance Mask-Locked Inference Chip

Inputs:
- Power budget: 5W max
- Die size: 25mm² (5mm x 5mm)
- Package: QFN-48 or similar
- Ambient temperature range: 0-70°C
- Power density distribution (PE array, memory, I/O)

Success Criteria:
- Tj < 100°C at 70°C ambient
- No active cooling required
- Thermal margin >10°C

Author: Thermal Simulation Agent
Date: 2026-03
"""

import json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

STEFAN_BOLTZMANN = 5.67e-8  # W/(m²·K⁴)
KELVIN_OFFSET = 273.15      # K to °C conversion

# ============================================================================
# MATERIAL PROPERTIES DATABASE
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

MATERIALS = {
    'silicon': MaterialProperties('Silicon', 148.0, 2329.0, 700.0),
    'silicon_dioxide': MaterialProperties('SiO2', 1.4, 2200.0, 730.0),
    'copper': MaterialProperties('Copper', 385.0, 8960.0, 385.0),
    'aluminum': MaterialProperties('Aluminum', 205.0, 2700.0, 900.0),
    'epoxy': MaterialProperties('Die Attach Epoxy', 2.5, 1800.0, 900.0),
    'mold_compound': MaterialProperties('Mold Compound', 0.8, 1800.0, 900.0),
    'tim': MaterialProperties('Thermal Interface Material', 5.0, 2500.0, 800.0),
    'tim_premium': MaterialProperties('Premium TIM', 8.0, 2800.0, 750.0),
    'air_300k': MaterialProperties('Air at 300K', 0.026, 1.16, 1007.0),
    'pcb_fr4': MaterialProperties('FR4 PCB', 0.3, 1850.0, 1100.0),
    'heatsink_al': MaterialProperties('Aluminum Heatsink', 205.0, 2700.0, 900.0),
}

# ============================================================================
# DIE CONFIGURATION
# ============================================================================

@dataclass
class DieConfiguration:
    """SuperInstance mask-locked inference die configuration"""
    name: str = "SuperInstance Mask-Locked Die"
    die_size_mm: float = 5.0          # 5mm x 5mm
    die_area_mm2: float = 25.0        # 25mm²
    die_thickness_um: float = 300.0   # 300μm standard thickness
    power_budget_w: float = 5.0       # 5W max
    package: str = "QFN-48"
    
    @property
    def dimensions_m(self) -> Tuple[float, float, float]:
        """Die dimensions in meters"""
        side = self.die_size_mm * 1e-3
        thickness = self.die_thickness_um * 1e-6
        return (side, side, thickness)
    
    @property
    def volume_m3(self) -> float:
        """Die volume [m³]"""
        L, _, t = self.dimensions_m
        return L * L * t
    
    @property
    def area_m2(self) -> float:
        """Die area [m²]"""
        L, _, _ = self.dimensions_m
        return L * L

# ============================================================================
# POWER DENSITY DISTRIBUTION
# ============================================================================

@dataclass
class PowerBlock:
    """A block of power-generating circuitry"""
    name: str
    x_mm: float          # X position (center) in mm
    y_mm: float          # Y position (center) in mm
    width_mm: float      # Width in mm
    height_mm: float     # Height in mm
    power_w: float       # Power consumption in Watts
    
    @property
    def area_mm2(self) -> float:
        return self.width_mm * self.height_mm
    
    @property
    def power_density_w_mm2(self) -> float:
        return self.power_w / self.area_mm2

@dataclass
class PowerDensityMap:
    """Power density distribution across the die"""
    blocks: List[PowerBlock] = field(default_factory=list)
    
    def add_block(self, block: PowerBlock):
        self.blocks.append(block)
    
    def get_total_power(self) -> float:
        return sum(b.power_w for b in self.blocks)
    
    def get_power_density_at(self, x_mm: float, y_mm: float) -> float:
        """Get power density at a specific location [W/mm²]"""
        density = 0.0
        for block in self.blocks:
            if (block.x_mm - block.width_mm/2 <= x_mm <= block.x_mm + block.width_mm/2 and
                block.y_mm - block.height_mm/2 <= y_mm <= block.y_mm + block.height_mm/2):
                density += block.power_density_w_mm2
        return density

def create_superinstance_power_map(total_power: float = 5.0) -> PowerDensityMap:
    """
    Create power density distribution for SuperInstance chip.
    
    Layout (5mm x 5mm die):
    - PE Array (center): ~60% of power, ~2mm x 2mm area
    - Memory/SRAM (edges): ~25% of power, distributed
    - I/O & Control (periphery): ~15% of power
    """
    power_map = PowerDensityMap()
    
    # PE Array - main compute engine (center of die)
    # 60% of power in 2mm x 2mm area = 3W
    power_map.add_block(PowerBlock(
        name="PE_Array",
        x_mm=2.5, y_mm=2.5,
        width_mm=2.0, height_mm=2.0,
        power_w=total_power * 0.60
    ))
    
    # Memory banks (SRAM/KV Cache) - distributed around PE array
    # 25% of power in 4 banks of 0.8mm x 1.5mm each
    memory_power_per_bank = total_power * 0.25 / 4
    power_map.add_block(PowerBlock(name="Memory_Bank_0", x_mm=0.5, y_mm=2.5, width_mm=0.6, height_mm=1.5, power_w=memory_power_per_bank))
    power_map.add_block(PowerBlock(name="Memory_Bank_1", x_mm=4.5, y_mm=2.5, width_mm=0.6, height_mm=1.5, power_w=memory_power_per_bank))
    power_map.add_block(PowerBlock(name="Memory_Bank_2", x_mm=2.5, y_mm=0.5, width_mm=1.5, height_mm=0.6, power_w=memory_power_per_bank))
    power_map.add_block(PowerBlock(name="Memory_Bank_3", x_mm=2.5, y_mm=4.5, width_mm=1.5, height_mm=0.6, power_w=memory_power_per_bank))
    
    # I/O and Control - periphery
    # 15% of power in ring around die
    io_power_per_side = total_power * 0.15 / 4
    power_map.add_block(PowerBlock(name="IO_Top", x_mm=2.5, y_mm=4.75, width_mm=3.0, height_mm=0.3, power_w=io_power_per_side))
    power_map.add_block(PowerBlock(name="IO_Bottom", x_mm=2.5, y_mm=0.25, width_mm=3.0, height_mm=0.3, power_w=io_power_per_side))
    power_map.add_block(PowerBlock(name="IO_Left", x_mm=0.25, y_mm=2.5, width_mm=0.3, height_mm=3.0, power_w=io_power_per_side))
    power_map.add_block(PowerBlock(name="IO_Right", x_mm=4.75, y_mm=2.5, width_mm=0.3, height_mm=3.0, power_w=io_power_per_side))
    
    return power_map

# ============================================================================
# PACKAGE THERMAL RESISTANCE
# ============================================================================

@dataclass
class PackageThermalModel:
    """Thermal model for IC packages"""
    name: str
    package_type: str
    pin_count: int
    body_size_mm: Tuple[float, float]  # (width, length)
    exposed_pad_mm2: float              # Exposed pad area
    R_jc: float                        # Junction-to-case resistance [K/W]
    R_jb: float                        # Junction-to-board resistance [K/W]
    
    def R_ja_natural(self, h_natural: float = 10.0, pcb_area_mm2: float = 1000.0) -> float:
        """
        Calculate junction-to-ambient thermal resistance for natural convection.
        
        Args:
            h_natural: Natural convection coefficient [W/(m²·K)]
            pcb_area_mm2: PCB heat spreading area [mm²]
        """
        # Board-to-ambient resistance
        A_pcb = pcb_area_mm2 * 1e-6  # m²
        R_ba = 1.0 / (h_natural * A_pcb)
        
        # Total junction-to-ambient
        return self.R_jc + self.R_jb + R_ba
    
    def R_ja_heatsink(self, R_heatsink: float = 15.0) -> float:
        """Junction-to-ambient with heatsink"""
        return self.R_jc + R_heatsink
    
    def R_ja_thermal_pad(self, R_pad: float = 2.0, h_enhanced: float = 20.0, 
                         pcb_area_mm2: float = 1000.0) -> float:
        """Junction-to-ambient with thermal pad to PCB"""
        A_pcb = pcb_area_mm2 * 1e-6
        R_ba_enhanced = 1.0 / (h_enhanced * A_pcb)
        return self.R_jc + R_pad + self.R_jb * 0.7 + R_ba_enhanced

# Standard package thermal models
PACKAGE_MODELS = {
    'QFN-48': PackageThermalModel(
        name='QFN-48 (7x7mm)',
        package_type='QFN',
        pin_count=48,
        body_size_mm=(7.0, 7.0),
        exposed_pad_mm2=25.0,
        R_jc=8.0,   # K/W - good thermal path through exposed pad
        R_jb=12.0,  # K/W - through pins to board
    ),
    'QFN-48_thermally_enhanced': PackageThermalModel(
        name='QFN-48 Thermally Enhanced (8x8mm)',
        package_type='QFN',
        pin_count=48,
        body_size_mm=(8.0, 8.0),
        exposed_pad_mm2=36.0,
        R_jc=5.0,
        R_jb=10.0,
    ),
    'QFN-64': PackageThermalModel(
        name='QFN-64 (9x9mm)',
        package_type='QFN',
        pin_count=64,
        body_size_mm=(9.0, 9.0),
        exposed_pad_mm2=49.0,
        R_jc=4.5,
        R_jb=9.0,
    ),
    'BGA-144': PackageThermalModel(
        name='BGA-144 (10x10mm)',
        package_type='BGA',
        pin_count=144,
        body_size_mm=(10.0, 10.0),
        exposed_pad_mm2=36.0,
        R_jc=6.0,
        R_jb=15.0,
    ),
    'CSP-48': PackageThermalModel(
        name='CSP-48 (6x6mm)',
        package_type='CSP',
        pin_count=48,
        body_size_mm=(6.0, 6.0),
        exposed_pad_mm2=25.0,
        R_jc=10.0,
        R_jb=15.0,
    ),
}

# ============================================================================
# FINITE DIFFERENCE THERMAL SOLVER
# ============================================================================

class FiniteDifferenceThermalSolver:
    """
    3D finite difference heat equation solver for thermal analysis.
    
    Uses explicit scheme for time-domain simulation and iterative
    relaxation for steady-state solutions.
    """
    
    def __init__(self,
                 die: DieConfiguration,
                 power_map: PowerDensityMap,
                 nx: int = 50,
                 ny: int = 50,
                 nz: int = 10):
        """
        Initialize the thermal solver.
        
        Args:
            die: Die configuration
            power_map: Power density distribution
            nx, ny, nz: Grid resolution
        """
        self.die = die
        self.power_map = power_map
        self.nx, self.ny, self.nz = nx, ny, nz
        
        # Grid dimensions
        Lx, Ly, Lz = die.dimensions_m
        self.Lx, self.Ly, self.Lz = Lx, Ly, Lz
        
        # Grid spacing
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        self.dz = Lz / (nz - 1)
        
        # Material properties
        self.mat = MATERIALS['silicon']
        
        # Stability criterion for explicit scheme
        self.dt_max = 0.25 / (self.mat.alpha * 
                             (1/self.dx**2 + 1/self.dy**2 + 1/self.dz**2))
        
        # Initialize temperature field (in Kelvin)
        self.T = np.ones((nx, ny, nz)) * 298.15  # 25°C initial
        
        # Heat source array [W/m³]
        self.Q = np.zeros((nx, ny, nz))
        
        # Coordinate arrays
        self.x = np.linspace(0, Lx * 1000, nx)  # in mm
        self.y = np.linspace(0, Ly * 1000, ny)  # in mm
        self.z = np.linspace(0, Lz * 1000, nz)  # in mm
        
        self._setup_heat_sources()
    
    def _setup_heat_sources(self):
        """Set up heat source distribution based on power map"""
        Lx_mm = self.Lx * 1000
        Ly_mm = self.Ly * 1000
        
        # Map power blocks to grid
        for i, x in enumerate(self.x):
            for j, y in enumerate(self.y):
                density = self.power_map.get_power_density_at(x, y)
                if density > 0:
                    # Convert W/mm² to W/m³ (assuming heat generated in top 10μm)
                    active_thickness = 10e-6  # 10 μm active layer
                    Q_density = density * 1e6 / active_thickness  # W/m³
                    # Apply to top layers of grid
                    for k in range(min(3, self.nz)):
                        self.Q[i, j, k] = Q_density
    
    def set_boundary_conditions(self, T_ambient: float = 298.15, 
                                h_convection: float = 10.0,
                                with_heatsink: bool = False,
                                R_heatsink: float = 15.0):
        """
        Set boundary conditions.
        
        Args:
            T_ambient: Ambient temperature [K]
            h_convection: Convection coefficient [W/(m²·K)]
            with_heatsink: Whether heatsink is attached
            R_heatsink: Heatsink thermal resistance [K/W]
        """
        self.T_ambient = T_ambient
        self.h_convection = h_convection
        self.with_heatsink = with_heatsink
        self.R_heatsink = R_heatsink
    
    def solve_steady_state(self, 
                          max_iterations: int = 50000,
                          tolerance: float = 1e-8,
                          relaxation: float = 1.5) -> Dict:
        """
        Solve for steady-state temperature distribution using SOR.
        
        Returns convergence info and temperature field.
        """
        alpha = self.mat.alpha
        rho_cp = self.mat.rho * self.mat.cp
        
        for iteration in range(max_iterations):
            T_old = self.T.copy()
            
            # Update interior points using SOR
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    for k in range(1, self.nz - 1):
                        # Second derivatives (Laplacian)
                        d2T_dx2 = (self.T[i+1, j, k] - 2*self.T[i, j, k] + 
                                  self.T[i-1, j, k]) / self.dx**2
                        d2T_dy2 = (self.T[i, j+1, k] - 2*self.T[i, j, k] + 
                                  self.T[i, j-1, k]) / self.dy**2
                        d2T_dz2 = (self.T[i, j, k+1] - 2*self.T[i, j, k] + 
                                  self.T[i, j, k-1]) / self.dz**2
                        
                        # Heat equation with source term
                        laplacian = d2T_dx2 + d2T_dy2 + d2T_dz2
                        T_new = self.T[i, j, k] + (alpha * laplacian + 
                                                    self.Q[i, j, k] / rho_cp) * 1e-6
                        
                        # Apply relaxation
                        self.T[i, j, k] = self.T[i, j, k] + relaxation * (T_new - self.T[i, j, k])
            
            # Apply boundary conditions
            self._apply_bc()
            
            # Check convergence
            max_change = np.max(np.abs(self.T - T_old))
            if max_change < tolerance:
                return {
                    'converged': True,
                    'iterations': iteration + 1,
                    'max_change': max_change
                }
        
        return {
            'converged': False,
            'iterations': max_iterations,
            'max_change': max_change
        }
    
    def _apply_bc(self):
        """Apply boundary conditions to temperature field"""
        # Bottom surface: fixed temperature (exposed pad connection)
        self.T[:, :, 0] = self.T_ambient
        
        # Top surface: convection
        k = self.mat.k
        h = self.h_convection
        q_conv = h * (self.T[:, :, -1] - self.T_ambient)
        self.T[:, :, -1] = self.T[:, :, -2] - q_conv * self.dz / k
        
        # Side surfaces: adiabatic (Neumann zero)
        self.T[0, :, :] = self.T[1, :, :]
        self.T[-1, :, :] = self.T[-2, :, :]
        self.T[:, 0, :] = self.T[:, 1, :]
        self.T[:, -1, :] = self.T[:, -2, :]
    
    def solve_transient(self, 
                       time_s: float,
                       dt: float = None,
                       power_profile: List[Tuple[float, float]] = None) -> Dict:
        """
        Solve transient thermal behavior.
        
        Args:
            time_s: Total simulation time [s]
            dt: Time step [s] (auto-calculated if None)
            power_profile: List of (time, power) tuples for time-varying power
        
        Returns temperature history.
        """
        if dt is None:
            dt = 0.9 * self.dt_max
        
        n_steps = int(time_s / dt)
        T_history = np.zeros((n_steps, self.nx, self.ny))
        time_points = np.linspace(0, time_s, n_steps)
        
        for step in range(n_steps):
            # Apply time-varying power if specified
            if power_profile:
                t = step * dt
                power_factor = self._get_power_factor(t, power_profile)
                Q_current = self.Q * power_factor
            else:
                Q_current = self.Q
            
            # Time integration (explicit scheme)
            alpha = self.mat.alpha
            rho_cp = self.mat.rho * self.mat.cp
            
            T_new = self.T.copy()
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    for k in range(1, self.nz - 1):
                        d2T_dx2 = (self.T[i+1, j, k] - 2*self.T[i, j, k] + 
                                  self.T[i-1, j, k]) / self.dx**2
                        d2T_dy2 = (self.T[i, j+1, k] - 2*self.T[i, j, k] + 
                                  self.T[i, j-1, k]) / self.dy**2
                        d2T_dz2 = (self.T[i, j, k+1] - 2*self.T[i, j, k] + 
                                  self.T[i, j, k-1]) / self.dz**2
                        
                        T_new[i, j, k] = self.T[i, j, k] + dt * (
                            alpha * (d2T_dx2 + d2T_dy2 + d2T_dz2) +
                            Q_current[i, j, k] / rho_cp
                        )
            
            self.T = T_new
            self._apply_bc()
            
            # Store surface temperature
            T_history[step] = self.T[:, :, -1]
        
        return {
            'time_points': time_points,
            'T_history': T_history,
            'T_final': self.T.copy()
        }
    
    def _get_power_factor(self, t: float, profile: List[Tuple[float, float]]) -> float:
        """Get power factor at time t from power profile"""
        for i, (t_event, power) in enumerate(profile):
            if t < t_event:
                if i == 0:
                    return power
                return profile[i-1][1]
        return profile[-1][1]
    
    def get_hotspot_info(self) -> Dict:
        """Identify hotspots and calculate thermal gradients"""
        # Surface temperature (top of die)
        T_surface = self.T[:, :, -1]
        
        # Find maximum temperature location
        max_idx = np.unravel_index(np.argmax(T_surface), T_surface.shape)
        T_max = T_surface[max_idx]
        
        # Average temperature
        T_avg = np.mean(T_surface)
        
        # Hotspot temperature rise
        dT_hotspot = T_max - T_avg
        
        # Thermal gradient (K/mm)
        gradient_x = np.max(np.abs(np.diff(T_surface, axis=0))) / (self.dx * 1000)
        gradient_y = np.max(np.abs(np.diff(T_surface, axis=1))) / (self.dy * 1000)
        
        # Hotspot location in mm
        x_mm = self.x[max_idx[0]]
        y_mm = self.y[max_idx[1]]
        
        return {
            'T_max_K': T_max,
            'T_max_C': T_max - KELVIN_OFFSET,
            'T_avg_K': T_avg,
            'T_avg_C': T_avg - KELVIN_OFFSET,
            'dT_hotspot_K': dT_hotspot,
            'gradient_x_K_mm': gradient_x,
            'gradient_y_K_mm': gradient_y,
            'hotspot_x_mm': x_mm,
            'hotspot_y_mm': y_mm,
        }

# ============================================================================
# THERMAL TIME CONSTANT ANALYSIS
# ============================================================================

class ThermalTimeConstant:
    """Calculate thermal time constants for the system"""
    
    def __init__(self, die: DieConfiguration, package: PackageThermalModel):
        self.die = die
        self.package = package
        self.mat = MATERIALS['silicon']
    
    def die_thermal_capacitance(self) -> float:
        """Calculate die thermal capacitance [J/K]"""
        return self.mat.rho * self.mat.cp * self.die.volume_m3
    
    def package_thermal_capacitance(self) -> float:
        """Estimate package thermal capacitance [J/K]"""
        # Approximate package as copper+epoxy+mold compound
        # Typical QFN package: ~0.5g effective thermal mass
        mass_kg = 0.5e-3  # 0.5 grams
        cp_avg = 600.0    # J/(kg·K) average specific heat
        return mass_kg * cp_avg
    
    def time_constant_die(self, R_ja: float) -> float:
        """Die-level time constant [s]"""
        C_die = self.die_thermal_capacitance()
        return R_ja * C_die
    
    def time_constant_package(self, R_ja: float) -> float:
        """Package-level time constant [s]"""
        C_pkg = self.package_thermal_capacitance()
        return R_ja * C_pkg
    
    def time_to_steady_state(self, R_ja: float, percent: float = 95.0) -> float:
        """Time to reach given percentage of steady state [s]"""
        tau = self.time_constant_package(R_ja)
        # For 1st order system: t = -tau * ln(1 - percent/100)
        target = percent / 100
        return -tau * np.log(1 - target)

# ============================================================================
# COOLING OPTION ANALYSIS
# ============================================================================

@dataclass
class CoolingOption:
    """Cooling solution analysis"""
    name: str
    description: str
    R_thermal: float          # Additional thermal resistance [K/W]
    cost_usd: float           # Cost per unit
    volume_mm3: float         # Volume requirement
    requires_power: bool      # Whether active cooling
    reliability_factor: float # Relative reliability (1.0 = baseline)

COOLING_OPTIONS = [
    CoolingOption(
        name="Natural Convection Only",
        description="No additional cooling, PCB as heatsink",
        R_thermal=0.0,
        cost_usd=0.0,
        volume_mm3=0,
        requires_power=False,
        reliability_factor=1.0
    ),
    CoolingOption(
        name="Thermal Pad to PCB",
        description="Silicone thermal pad, 1mm thick",
        R_thermal=2.0,
        cost_usd=0.15,
        volume_mm3=25,  # Minimal
        requires_power=False,
        reliability_factor=1.0
    ),
    CoolingOption(
        name="Premium TIM + PCB",
        description="High-performance thermal interface material",
        R_thermal=1.0,
        cost_usd=0.50,
        volume_mm3=25,
        requires_power=False,
        reliability_factor=1.0
    ),
    CoolingOption(
        name="Small Heatsink (15 K/W)",
        description="Stamped aluminum heatsink, 15x15x10mm",
        R_thermal=-5.0,  # Reduces total R_ja
        cost_usd=1.50,
        volume_mm3=2250,
        requires_power=False,
        reliability_factor=0.98  # Slight derating for attachment
    ),
    CoolingOption(
        name="Medium Heatsink (10 K/W)",
        description="Extruded aluminum heatsink, 25x25x15mm",
        R_thermal=-8.0,
        cost_usd=3.00,
        volume_mm3=9375,
        requires_power=False,
        reliability_factor=0.97
    ),
    CoolingOption(
        name="Large Heatsink (5 K/W)",
        description="Extruded aluminum heatsink, 40x40x20mm",
        R_thermal=-12.0,
        cost_usd=5.00,
        volume_mm3=32000,
        requires_power=False,
        reliability_factor=0.96
    ),
]

def analyze_cooling_options(die: DieConfiguration, 
                           package: PackageThermalModel,
                           power_w: float,
                           T_ambient_c: float) -> List[Dict]:
    """Analyze all cooling options and return junction temperatures"""
    results = []
    T_ambient_k = T_ambient_c + KELVIN_OFFSET
    
    for option in COOLING_OPTIONS:
        # Calculate effective R_ja
        if "Heatsink" in option.name:
            R_ja = package.R_ja_heatsink(R_heatsink=abs(option.R_thermal) + 5.0)
        else:
            R_ja_base = package.R_ja_natural(h_natural=15.0)  # Enhanced convection
            R_ja = R_ja_base + option.R_thermal
        
        # Calculate junction temperature
        T_junction_k = T_ambient_k + power_w * R_ja
        T_junction_c = T_junction_k - KELVIN_OFFSET
        
        # Check if meets criteria
        meets_criteria = T_junction_c < 100.0  # Tj < 100°C
        thermal_margin = 100.0 - T_junction_c
        margin_ok = thermal_margin > 10.0
        
        results.append({
            'name': option.name,
            'description': option.description,
            'R_ja_K_per_W': R_ja,
            'T_junction_C': T_junction_c,
            'meets_criteria': meets_criteria,
            'thermal_margin_C': thermal_margin,
            'margin_ok': margin_ok,
            'cost_usd': option.cost_usd,
            'active_cooling': option.requires_power,
            'recommended': meets_criteria and margin_ok and not option.requires_power
        })
    
    return results

# ============================================================================
# THERMAL MAP VISUALIZATION
# ============================================================================

def create_thermal_map(solver: FiniteDifferenceThermalSolver, 
                       save_path: str = None) -> plt.Figure:
    """Create thermal map visualization"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Get temperature data
    T_surface = solver.T[:, :, -1] - KELVIN_OFFSET  # Convert to Celsius
    T_cross_section = solver.T[solver.nx//2, :, :] - KELVIN_OFFSET
    
    # 1. Surface temperature map
    ax1 = axes[0, 0]
    X, Y = np.meshgrid(solver.x, solver.y, indexing='ij')
    im1 = ax1.contourf(X, Y, T_surface, levels=30, cmap='hot')
    ax1.set_xlabel('X Position [mm]')
    ax1.set_ylabel('Y Position [mm]')
    ax1.set_title(f'Die Surface Temperature Map\nMax: {T_surface.max():.1f}°C, Avg: {T_surface.mean():.1f}°C')
    plt.colorbar(im1, ax=ax1, label='Temperature [°C]')
    
    # Mark power blocks
    for block in solver.power_map.blocks:
        rect = plt.Rectangle(
            (block.x_mm - block.width_mm/2, block.y_mm - block.height_mm/2),
            block.width_mm, block.height_mm,
            fill=False, edgecolor='cyan', linewidth=1, linestyle='--'
        )
        ax1.add_patch(rect)
    
    # 2. Cross-section temperature
    ax2 = axes[0, 1]
    Z, Y_cs = np.meshgrid(solver.z * 1000, solver.y)  # z in μm
    im2 = ax2.contourf(Y_cs, Z, T_cross_section.T, levels=30, cmap='hot')
    ax2.set_xlabel('Y Position [mm]')
    ax2.set_ylabel('Z Position [μm]')
    ax2.set_title('Cross-Section Temperature (X=2.5mm)')
    plt.colorbar(im2, ax=ax2, label='Temperature [°C]')
    
    # 3. Temperature profile along X
    ax3 = axes[1, 0]
    T_center_x = T_surface[:, solver.ny//2]
    T_center_y = T_surface[solver.nx//2, :]
    ax3.plot(solver.x, T_center_x, 'r-', linewidth=2, label='Y=2.5mm (center)')
    ax3.plot(solver.y, T_center_y, 'b--', linewidth=2, label='X=2.5mm (center)')
    ax3.axhline(y=100, color='r', linestyle=':', label='Max limit (100°C)')
    ax3.set_xlabel('Position [mm]')
    ax3.set_ylabel('Temperature [°C]')
    ax3.set_title('Temperature Profiles Through Die Center')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Power density distribution
    ax4 = axes[1, 1]
    power_density = np.zeros((solver.nx, solver.ny))
    for i, x in enumerate(solver.x):
        for j, y in enumerate(solver.y):
            power_density[i, j] = solver.power_map.get_power_density_at(x, y)
    
    im4 = ax4.contourf(X, Y, power_density * 1000, levels=20, cmap='YlOrRd')
    ax4.set_xlabel('X Position [mm]')
    ax4.set_ylabel('Y Position [mm]')
    ax4.set_title(f'Power Density Distribution\nTotal: {solver.power_map.get_total_power():.1f}W')
    plt.colorbar(im4, ax=ax4, label='Power Density [mW/mm²]')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Thermal map saved to {save_path}")
    
    return fig

def create_transient_plot(time_points: np.ndarray, 
                         T_history: np.ndarray,
                         T_ambient_c: float,
                         save_path: str = None) -> plt.Figure:
    """Create transient thermal response plot"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Get max temperature over time
    T_max = np.max(T_history, axis=(1, 2)) - KELVIN_OFFSET
    T_avg = np.mean(T_history, axis=(1, 2)) - KELVIN_OFFSET
    
    # 1. Temperature vs time
    ax1 = axes[0]
    ax1.plot(time_points, T_max, 'r-', linewidth=2, label='Max Temperature')
    ax1.plot(time_points, T_avg, 'b--', linewidth=2, label='Avg Temperature')
    ax1.axhline(y=100, color='r', linestyle=':', label='Max limit (100°C)')
    ax1.axhline(y=T_ambient_c, color='g', linestyle='-.', label=f'Ambient ({T_ambient_c}°C)')
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Temperature [°C]')
    ax1.set_title('Transient Thermal Response')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Temperature rise rate
    ax2 = axes[1]
    dT_dt = np.gradient(T_max, time_points)
    ax2.plot(time_points, dT_dt, 'g-', linewidth=2)
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Temperature Rise Rate [°C/s]')
    ax2.set_title('Temperature Change Rate')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Transient plot saved to {save_path}")
    
    return fig

def create_package_comparison_chart(package_results: Dict, 
                                    save_path: str = None) -> plt.Figure:
    """Create package thermal resistance comparison chart"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. R_ja comparison
    ax1 = axes[0]
    packages = list(package_results.keys())
    R_ja_values = [package_results[p]['R_ja'] for p in packages]
    T_junction_values = [package_results[p]['T_junction_C'] for p in packages]
    
    colors = ['green' if t < 100 else 'red' for t in T_junction_values]
    bars = ax1.bar(packages, R_ja_values, color=colors, alpha=0.7)
    ax1.set_ylabel('R_ja [K/W]')
    ax1.set_title('Thermal Resistance by Package')
    ax1.axhline(y=20, color='orange', linestyle='--', label='Target R_ja')
    ax1.legend()
    
    # Add value labels
    for bar, val in zip(bars, R_ja_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. Junction temperature comparison
    ax2 = axes[1]
    bars2 = ax2.bar(packages, T_junction_values, color=colors, alpha=0.7)
    ax2.axhline(y=100, color='red', linestyle='--', label='Max limit (100°C)')
    ax2.axhline(y=90, color='orange', linestyle=':', label='Target with margin')
    ax2.set_ylabel('Junction Temperature [°C]')
    ax2.set_title('Junction Temperature @ 5W, 70°C Ambient')
    ax2.legend()
    
    # Add value labels
    for bar, val in zip(bars2, T_junction_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}°C', ha='center', va='bottom', fontsize=9)
    
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Package comparison chart saved to {save_path}")
    
    return fig

# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_thermal_simulation() -> Dict:
    """Run complete A3 thermal simulation"""
    
    print("="*70)
    print("A3: THERMAL PERFORMANCE SIMULATION")
    print("SuperInstance Mask-Locked Inference Chip")
    print("="*70)
    
    # Initialize configuration
    die = DieConfiguration()
    power_map = create_superinstance_power_map(total_power=5.0)
    
    results = {
        'simulation_id': 'A3_thermal',
        'die_configuration': {
            'name': die.name,
            'die_size_mm': die.die_size_mm,
            'die_area_mm2': die.die_area_mm2,
            'die_thickness_um': die.die_thickness_um,
            'power_budget_w': die.power_budget_w,
            'package': die.package,
        },
        'power_distribution': {},
        'package_analysis': {},
        'steady_state': {},
        'transient': {},
        'cooling_options': {},
        'validation': {},
    }
    
    # =========================================================================
    # STEP 1: Power Density Distribution
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 1: POWER DENSITY DISTRIBUTION")
    print("="*70)
    
    power_info = {
        'total_power_w': power_map.get_total_power(),
        'blocks': []
    }
    
    print(f"\nTotal Power: {power_map.get_total_power():.2f} W")
    print("\nPower Distribution:")
    print(f"{'Block':<20} {'Position (mm)':<15} {'Size (mm)':<15} {'Power (W)':<10} {'Density (W/mm²)':<15}")
    print("-"*75)
    
    for block in power_map.blocks:
        block_info = {
            'name': block.name,
            'position': (block.x_mm, block.y_mm),
            'size': (block.width_mm, block.height_mm),
            'power_w': block.power_w,
            'power_density_w_mm2': block.power_density_w_mm2
        }
        power_info['blocks'].append(block_info)
        
        print(f"{block.name:<20} ({block.x_mm:.1f}, {block.y_mm:.1f}){'':>5} "
              f"{block.width_mm:.1f}x{block.height_mm:.1f}{'':>5} "
              f"{block.power_w:<10.3f} {block.power_density_w_mm2:<15.4f}")
    
    results['power_distribution'] = power_info
    
    # =========================================================================
    # STEP 2: Package Thermal Resistance Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 2: THERMAL RESISTANCE ANALYSIS (RθJA)")
    print("="*70)
    
    package_analysis = {}
    
    print("\nThermal Resistance for Different Packages:")
    print(f"{'Package':<25} {'R_jc [K/W]':<12} {'R_jb [K/W]':<12} {'R_ja [K/W]':<12} {'Tj @ 5W [°C]':<15}")
    print("-"*75)
    
    for pkg_name, pkg in PACKAGE_MODELS.items():
        # Calculate R_ja for natural convection
        R_ja = pkg.R_ja_natural(h_natural=12.0, pcb_area_mm2=1000.0)
        
        # Junction temperature at 70°C ambient, 5W power
        T_ambient_c = 70.0
        T_junction_c = T_ambient_c + die.power_budget_w * R_ja
        
        package_analysis[pkg_name] = {
            'package_name': pkg.name,
            'R_jc': pkg.R_jc,
            'R_jb': pkg.R_jb,
            'R_ja': R_ja,
            'T_junction_C': T_junction_c,
            'meets_criteria': T_junction_c < 100.0
        }
        
        status = "✓" if T_junction_c < 100.0 else "✗"
        print(f"{pkg.name:<25} {pkg.R_jc:<12.1f} {pkg.R_jb:<12.1f} "
              f"{R_ja:<12.1f} {T_junction_c:<15.1f} {status}")
    
    results['package_analysis'] = package_analysis
    
    # Identify best package
    best_package_name = min(package_analysis.keys(), 
                           key=lambda x: package_analysis[x]['T_junction_C'])
    best_package = PACKAGE_MODELS[best_package_name]
    print(f"\n✓ Recommended Package: {best_package.name}")
    print(f"  R_ja = {package_analysis[best_package_name]['R_ja']:.1f} K/W")
    
    # =========================================================================
    # STEP 3: Finite Difference Thermal Model
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 3: FINITE DIFFERENCE THERMAL MODEL")
    print("="*70)
    
    # Create solver with fine grid
    solver = FiniteDifferenceThermalSolver(die, power_map, nx=50, ny=50, nz=15)
    
    # Solve steady-state at worst case (70°C ambient)
    T_ambient_k = 70.0 + KELVIN_OFFSET
    solver.set_boundary_conditions(T_ambient=T_ambient_k, h_convection=12.0)
    
    print("\nSolving steady-state temperature distribution...")
    convergence = solver.solve_steady_state(max_iterations=20000)
    
    print(f"  Convergence: {'Yes' if convergence['converged'] else 'No'}")
    print(f"  Iterations: {convergence['iterations']}")
    
    hotspot = solver.get_hotspot_info()
    
    print("\nSteady-State Results:")
    print(f"  Maximum Junction Temperature: {hotspot['T_max_C']:.1f}°C")
    print(f"  Average Junction Temperature: {hotspot['T_avg_C']:.1f}°C")
    print(f"  Hotspot Temperature Rise: {hotspot['dT_hotspot_K']:.1f} K")
    print(f"  Hotspot Location: ({hotspot['hotspot_x_mm']:.2f}, {hotspot['hotspot_y_mm']:.2f}) mm")
    print(f"  Thermal Gradient: {max(hotspot['gradient_x_K_mm'], hotspot['gradient_y_K_mm']):.1f} K/mm")
    
    results['steady_state'] = {
        'convergence': convergence,
        'T_max_C': hotspot['T_max_C'],
        'T_avg_C': hotspot['T_avg_C'],
        'dT_hotspot_K': hotspot['dT_hotspot_K'],
        'hotspot_location_mm': (hotspot['hotspot_x_mm'], hotspot['hotspot_y_mm']),
        'thermal_gradient_K_mm': max(hotspot['gradient_x_K_mm'], hotspot['gradient_y_K_mm']),
    }
    
    # =========================================================================
    # STEP 4: Transient Thermal Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 4: TRANSIENT THERMAL ANALYSIS")
    print("="*70)
    
    # Reset solver for transient analysis
    solver.T[:] = T_ambient_k
    
    # Calculate thermal time constants
    time_const = ThermalTimeConstant(die, best_package)
    
    C_die = time_const.die_thermal_capacitance()
    C_pkg = time_const.package_thermal_capacitance()
    R_ja = package_analysis[best_package_name]['R_ja']
    
    tau_die = time_const.time_constant_die(R_ja)
    tau_pkg = time_const.time_constant_package(R_ja)
    t_90 = time_const.time_to_steady_state(R_ja, 90.0)
    
    print(f"\nThermal Capacitance:")
    print(f"  Die: {C_die*1e3:.4f} mJ/K")
    print(f"  Package: {C_pkg*1e3:.1f} mJ/K")
    
    print(f"\nTime Constants:")
    print(f"  Die-level: {tau_die*1e6:.2f} μs")
    print(f"  Package-level: {tau_pkg:.2f} s")
    print(f"  Time to 90% steady state: {t_90:.1f} s")
    
    # Run transient simulation
    print("\nRunning transient simulation (30s burst)...")
    transient_result = solver.solve_transient(time_s=30.0)
    
    # Get temperature at key times
    T_history = transient_result['T_history']
    T_max_at_1s = np.max(T_history[len(T_history)//30]) - KELVIN_OFFSET
    T_max_at_10s = np.max(T_history[len(T_history)//3]) - KELVIN_OFFSET
    T_max_final = np.max(T_history[-1]) - KELVIN_OFFSET
    
    print(f"\nTransient Results:")
    print(f"  T_max at 1s: {T_max_at_1s:.1f}°C")
    print(f"  T_max at 10s: {T_max_at_10s:.1f}°C")
    print(f"  T_max at 30s (steady): {T_max_final:.1f}°C")
    
    results['transient'] = {
        'die_capacitance_mJ_K': C_die * 1e3,
        'package_capacitance_mJ_K': C_pkg * 1e3,
        'time_constant_die_us': tau_die * 1e6,
        'time_constant_package_s': tau_pkg,
        'time_to_90_percent_s': t_90,
        'T_max_1s_C': T_max_at_1s,
        'T_max_10s_C': T_max_at_10s,
        'T_max_final_C': T_max_final,
    }
    
    # =========================================================================
    # STEP 5: Cooling Options Evaluation
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 5: COOLING OPTIONS EVALUATION")
    print("="*70)
    
    cooling_results = analyze_cooling_options(
        die, best_package, 
        power_w=die.power_budget_w,
        T_ambient_c=70.0
    )
    
    print(f"\n{'Cooling Option':<30} {'R_ja [K/W]':<12} {'Tj [°C]':<10} {'Margin [°C]':<12} {'Cost':<10} {'Status':<10}")
    print("-"*85)
    
    recommended_options = []
    for opt in cooling_results:
        status = "✓ OK" if opt['recommended'] else ("⚠ MARGINAL" if opt['meets_criteria'] else "✗ FAIL")
        print(f"{opt['name']:<30} {opt['R_ja_K_per_W']:<12.1f} {opt['T_junction_C']:<10.1f} "
              f"{opt['thermal_margin_C']:<12.1f} ${opt['cost_usd']:<9.2f} {status:<10}")
        
        if opt['recommended']:
            recommended_options.append(opt['name'])
    
    results['cooling_options'] = cooling_results
    
    # =========================================================================
    # STEP 6: VALIDATION
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 6: VALIDATION AGAINST SUCCESS CRITERIA")
    print("="*70)
    
    # Check all ambient temperatures
    ambient_temps_c = [0.0, 25.0, 45.0, 70.0]
    
    print("\nJunction Temperature at Different Ambient Temperatures:")
    print(f"{'Ambient [°C]':<15} {'Tj [°C]':<15} {'Margin to 100°C':<20} {'Status':<15}")
    print("-"*65)
    
    validation_results = {
        'temperatures': [],
        'Tj_below_100_at_70C': False,
        'no_active_cooling': True,
        'thermal_margin_over_10C': False,
        'overall_pass': False
    }
    
    best_R_ja = package_analysis[best_package_name]['R_ja']
    
    for T_amb in ambient_temps_c:
        T_j = T_amb + die.power_budget_w * best_R_ja
        margin = 100.0 - T_j
        status = "✓ PASS" if margin > 10.0 else ("⚠ MARGINAL" if T_j < 100.0 else "✗ FAIL")
        
        print(f"{T_amb:<15.0f} {T_j:<15.1f} {margin:<20.1f} {status:<15}")
        
        validation_results['temperatures'].append({
            'T_ambient_C': T_amb,
            'T_junction_C': T_j,
            'margin_C': margin
        })
    
    # Final validation checks
    Tj_at_70C = 70.0 + die.power_budget_w * best_R_ja
    validation_results['Tj_below_100_at_70C'] = Tj_at_70C < 100.0
    validation_results['thermal_margin_over_10C'] = (100.0 - Tj_at_70C) > 10.0
    
    # Check if passive cooling works
    passive_options = [opt for opt in cooling_results 
                      if opt['recommended'] and not opt['active_cooling']]
    validation_results['no_active_cooling'] = len(passive_options) > 0
    
    # Overall pass
    validation_results['overall_pass'] = (
        validation_results['Tj_below_100_at_70C'] and
        validation_results['no_active_cooling'] and
        validation_results['thermal_margin_over_10C']
    )
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"  ✓ Tj < 100°C at 70°C ambient: {'PASS' if validation_results['Tj_below_100_at_70C'] else 'FAIL'}")
    print(f"  ✓ No active cooling required: {'PASS' if validation_results['no_active_cooling'] else 'FAIL'}")
    print(f"  ✓ Thermal margin >10°C: {'PASS' if validation_results['thermal_margin_over_10C'] else 'FAIL'}")
    print(f"\n  OVERALL: {'✅ PASS' if validation_results['overall_pass'] else '❌ FAIL'}")
    
    # If not passing with default package, recommend solution
    if not validation_results['thermal_margin_over_10C']:
        print("\n" + "-"*70)
        print("RECOMMENDATION: Upgrade to QFN-64 or add small heatsink")
        for opt in cooling_results:
            if opt['recommended']:
                print(f"  → {opt['name']}: Tj = {opt['T_junction_C']:.1f}°C")
    
    results['validation'] = validation_results
    
    # =========================================================================
    # DESIGN RECOMMENDATIONS
    # =========================================================================
    results['recommendations'] = {
        'recommended_package': best_package.name,
        'recommended_cooling': recommended_options[0] if recommended_options else "Small Heatsink (15 K/W)",
        'key_findings': [
            f"PE Array generates 60% of total power in 4mm² area",
            f"Hotspot located at die center with {hotspot['dT_hotspot_K']:.1f}°C rise above average",
            f"Thermal gradient across die: {max(hotspot['gradient_x_K_mm'], hotspot['gradient_y_K_mm']):.1f} K/mm",
            f"Time to thermal steady state: ~{t_90:.0f}s",
            f"Natural convection alone {'insufficient' if Tj_at_70C > 90 else 'sufficient'} for 70°C ambient",
        ],
        'thermal_budget': {
            'R_ja_max_for_10C_margin': (100.0 - 10.0 - 70.0) / die.power_budget_w,
            'current_R_ja': best_R_ja,
            'margin': (100.0 - 10.0 - 70.0) / die.power_budget_w - best_R_ja,
        }
    }
    
    print("\n" + "="*70)
    print("THERMAL SIMULATION COMPLETE")
    print("="*70)
    
    return results


def main():
    """Main entry point"""
    # Run simulation
    results = run_thermal_simulation()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # Initialize for visualization
    die = DieConfiguration()
    power_map = create_superinstance_power_map()
    solver = FiniteDifferenceThermalSolver(die, power_map, nx=50, ny=50, nz=15)
    solver.set_boundary_conditions(T_ambient=70.0 + KELVIN_OFFSET, h_convection=12.0)
    solver.solve_steady_state(max_iterations=20000)
    
    # Thermal map
    create_thermal_map(solver, "A3_thermal_map.png")
    
    # Transient response
    solver.T[:] = 70.0 + KELVIN_OFFSET
    transient = solver.solve_transient(time_s=30.0)
    create_transient_plot(transient['time_points'], transient['T_history'], 70.0, 
                         "A3_transient_response.png")
    
    # Package comparison
    create_package_comparison_chart(results['package_analysis'], 
                                   "A3_package_comparison.png")
    
    # Save results to JSON
    output_path = "A3_thermal_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")
    
    return results


if __name__ == "__main__":
    results = main()
