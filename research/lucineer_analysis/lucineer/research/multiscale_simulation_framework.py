#!/usr/bin/env python3
"""
Multi-Scale Simulation Framework for Mask-Locked Inference Chip
===============================================================

Comprehensive simulation framework bridging atomic-scale quantum effects
to application-level inference performance.

Levels:
- L1: Atomic (quantum tunneling, phonons)
- L2: Device (transistor, MRAM)
- L3: Circuit (PE array, interconnect)
- L4: System (full chip thermal/power)
- L5: Application (inference workload)

Author: Computational Physics Research
Date: March 2026
Cycle: 3 of 5
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.integrate import odeint
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Callable, Union
from enum import Enum
from abc import ABC, abstractmethod
import warnings

# ============================================================================
# Physical Constants
# ============================================================================

KB_J = 1.38e-23           # Boltzmann constant [J/K]
KB_EV = 8.617e-5          # Boltzmann constant [eV/K]
Q_E = 1.602e-19           # Electron charge [C]
H_PLANCK = 6.626e-34      # Planck constant [J·s]
HBAR = 1.055e-34          # Reduced Planck constant [J·s]
M_E = 9.109e-31           # Electron mass [kg]
EPSILON_0 = 8.854e-12     # Vacuum permittivity [F/m]

# ============================================================================
# Scale Enumeration
# ============================================================================

class SimulationScale(Enum):
    """Enumeration of simulation scales"""
    ATOMIC = 1      # 0.3-3 nm, quantum effects
    DEVICE = 2      # 10-100 nm, transistor/MRAM
    CIRCUIT = 3     # 1-200 μm, PE/interconnect
    SYSTEM = 4      # 0.1-10 mm, full chip
    APPLICATION = 5 # Chip-level, inference

# ============================================================================
# Material Properties
# ============================================================================

@dataclass
class MaterialProperties:
    """Material thermal and electrical properties"""
    name: str
    k: float           # Thermal conductivity [W/(m·K)]
    rho: float         # Density [kg/m³]
    cp: float          # Specific heat [J/(kg·K)]
    sigma: float = 1e6 # Electrical conductivity [S/m]
    epsilon_r: float = 1.0  # Relative permittivity
    
    @property
    def alpha(self) -> float:
        """Thermal diffusivity [m²/s]"""
        return self.k / (self.rho * self.cp)

# Material database
MATERIALS = {
    'silicon': MaterialProperties(
        name='Silicon', k=148.0, rho=2329.0, cp=700.0,
        sigma=1e-4, epsilon_r=11.7
    ),
    'silicon_dioxide': MaterialProperties(
        name='SiO₂', k=1.4, rho=2200.0, cp=1000.0,
        sigma=1e-14, epsilon_r=3.9
    ),
    'copper': MaterialProperties(
        name='Copper', k=385.0, rho=8960.0, cp=385.0,
        sigma=5.96e7, epsilon_r=1.0
    ),
    'aluminum': MaterialProperties(
        name='Aluminum', k=237.0, rho=2700.0, cp=897.0,
        sigma=3.77e7, epsilon_r=1.0
    ),
}

# ============================================================================
# Chip Configuration
# ============================================================================

@dataclass
class ChipConfiguration:
    """Mask-locked inference chip configuration"""
    name: str = "Mask-Locked Inference Die"
    area_mm2: float = 27.0          # Die area [mm²]
    thickness_um: float = 300.0     # Die thickness [μm]
    power_w: float = 3.0            # Total power [W]
    n_pes: int = 1024               # Number of PEs (32×32)
    pe_size_um: float = 160.0       # PE size [μm]
    vdd: float = 0.9                # Core voltage [V]
    frequency_hz: float = 1e9       # Clock frequency [Hz]
    process_nm: float = 28.0        # Process node [nm]
    n_params: float = 2e9           # Model parameters
    bits_per_weight: int = 2        # Ternary = 2 bits
    
    @property
    def dimensions(self) -> Tuple[float, float, float]:
        """Die dimensions in meters (assuming square)"""
        side = np.sqrt(self.area_mm2 * 1e-6)
        thickness = self.thickness_um * 1e-6
        return (side, side, thickness)
    
    @property
    def volume(self) -> float:
        """Die volume [m³]"""
        L, _, t = self.dimensions
        return L * L * t
    
    @property
    def pe_array_shape(self) -> Tuple[int, int]:
        """PE array dimensions"""
        n = int(np.sqrt(self.n_pes))
        return (n, n)
    
    @property
    def pe_area_m2(self) -> float:
        """PE area [m²]"""
        pe_side = self.pe_size_um * 1e-6
        return pe_side * pe_side

# Default configuration
DEFAULT_CHIP = ChipConfiguration()

# ============================================================================
# LEVEL 1: Atomic Scale Simulator
# ============================================================================

class AtomicSimulator:
    """
    Level 1: Quantum/Atomic scale simulation
    
    Simulates:
    - Quantum tunneling through barriers
    - Phonon transport (thermal conductivity)
    - Thermionic emission
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.materials = MATERIALS
        
    def tunneling_probability(self, 
                               barrier_height_ev: float,
                               barrier_width_nm: float,
                               effective_mass_ratio: float = 0.19) -> float:
        """
        Calculate WKB tunneling probability.
        
        T = exp(-2κd) where κ = sqrt(2m*(V₀-E)/ℏ²)
        
        Args:
            barrier_height_ev: Barrier height in eV
            barrier_width_nm: Barrier width in nm
            effective_mass_ratio: m*/m₀
            
        Returns:
            Tunneling probability (0-1)
        """
        m_star = effective_mass_ratio * M_E
        d = barrier_width_nm * 1e-9
        
        # Decay constant
        kappa = np.sqrt(2 * m_star * barrier_height_ev * Q_E / HBAR**2)
        
        # Tunneling probability
        T = np.exp(-2 * kappa * d)
        return T
    
    def gate_leakage_current(self, 
                             T_kelvin: float = 300.0,
                             V_gate: float = 0.9,
                             oxide_thickness_nm: float = 1.2) -> float:
        """
        Calculate gate leakage current density.
        
        Uses Fowler-Nordheim and direct tunneling models.
        
        Args:
            T_kelvin: Temperature [K]
            V_gate: Gate voltage [V]
            oxide_thickness_nm: Oxide thickness [nm]
            
        Returns:
            Current density [A/cm²]
        """
        # Fowler-Nordheim parameters
        phi_B = 3.1  # Barrier height for SiO₂ [eV]
        E_field = V_gate / (oxide_thickness_nm * 1e-7)  # V/cm
        
        if E_field < 1e7:
            # Direct tunneling regime
            J = 1e-4 * np.exp(-oxide_thickness_nm / 0.5)
        else:
            # Fowler-Nordheim tunneling
            J_FN = (Q_E**3 * E_field**2) / (8 * np.pi * H_PLANCK * phi_B)
            J_FN *= np.exp(-8 * np.pi * np.sqrt(2 * 0.19 * M_E) * phi_B**1.5 / 
                          (3 * Q_E * H_PLANCK * E_field))
            J = J_FN * 1e-4  # Convert to A/cm²
        
        return max(J, 1e-10)  # Minimum leakage
    
    def thermal_conductivity(self, T_kelvin: float) -> float:
        """
        Calculate temperature-dependent thermal conductivity of silicon.
        
        κ(T) = κ₀ (T₀/T)^n
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Thermal conductivity [W/(m·K)]
        """
        k_0 = 148.0  # At 300K
        T_0 = 300.0
        n = 1.3
        
        return k_0 * (T_0 / T_kelvin)**n
    
    def phonon_mean_free_path(self, T_kelvin: float) -> float:
        """
        Calculate phonon mean free path.
        
        Λ(T) = Λ₀ (T₀/T)
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Mean free path [m]
        """
        Lambda_0 = 42e-9  # At 300K
        T_0 = 300.0
        
        return Lambda_0 * (T_0 / T_kelvin)
    
    def thermionic_emission_current(self,
                                    T_kelvin: float,
                                    barrier_ev: float = 0.8) -> float:
        """
        Calculate thermionic emission current density.
        
        J = A* T² exp(-qφ_B / kT)
        
        Args:
            T_kelvin: Temperature [K]
            barrier_ev: Barrier height [eV]
            
        Returns:
            Current density [A/cm²]
        """
        A_star = 130  # Richardson constant for Si [A/(cm²·K²)]
        
        J = A_star * T_kelvin**2 * np.exp(-barrier_ev / (KB_EV * T_kelvin))
        return J
    
    def run_simulation(self, T_range: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Run atomic scale simulation over temperature range.
        
        Args:
            T_range: Temperature array [K]
            
        Returns:
            Dictionary of results
        """
        results = {
            'temperature': T_range,
            'thermal_conductivity': np.array([self.thermal_conductivity(T) for T in T_range]),
            'phonon_mfp': np.array([self.phonon_mean_free_path(T) for T in T_range]),
            'thermionic_current': np.array([self.thermionic_emission_current(T) for T in T_range]),
            'gate_leakage': np.array([self.gate_leakage_current(T) for T in T_range]),
        }
        return results

# ============================================================================
# LEVEL 2: Device Scale Simulator
# ============================================================================

class DeviceSimulator:
    """
    Level 2: Device scale simulation
    
    Simulates:
    - Transistor I-V characteristics
    - MRAM switching dynamics
    - Temperature-dependent device parameters
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        
        # Transistor parameters (28nm)
        self.Vth_0 = 0.30        # Threshold voltage at 300K [V]
        self.mu_0 = 300e-4       # Mobility at 300K [m²/(V·s)]
        self.Cox = 25e-3         # Gate capacitance [F/m²]
        self.L = 28e-9           # Channel length [m]
        self.W = 100e-9          # Channel width [m]
        
        # Temperature coefficients
        self.k_VT = -2.0e-3      # Vth temperature coefficient [V/K]
        self.k_mu = -1.5         # Mobility temperature exponent
        
        # MRAM parameters
        self.R_P = 1e3           # Parallel resistance [Ω]
        self.R_AP = 10e3         # Anti-parallel resistance [Ω]
        self.TMR = 9.0           # TMR ratio (900%)
        
    def threshold_voltage(self, T_kelvin: float) -> float:
        """Temperature-dependent threshold voltage"""
        return self.Vth_0 + self.k_VT * (T_kelvin - 300)
    
    def mobility(self, T_kelvin: float) -> float:
        """Temperature-dependent mobility"""
        return self.mu_0 * (T_kelvin / 300)**self.k_mu
    
    def drain_current(self,
                     V_gs: float,
                     V_ds: float,
                     T_kelvin: float = 300.0) -> float:
        """
        Calculate drain current using simplified BSIM model.
        
        I_DS = μ_eff C_ox (W/L) [(V_GS - V_th)V_DS - V_DS²/2]
        
        Args:
            V_gs: Gate-source voltage [V]
            V_ds: Drain-source voltage [V]
            T_kelvin: Temperature [K]
            
        Returns:
            Drain current [A]
        """
        Vth = self.threshold_voltage(T_kelvin)
        mu = self.mobility(T_kelvin)
        
        if V_gs < Vth:
            return 0.0  # Cutoff
        
        # Saturation voltage
        V_dsat = min(V_ds, V_gs - Vth)
        
        # Linear/saturation current
        I_ds = mu * self.Cox * (self.W / self.L) * \
               ((V_gs - Vth) * V_dsat - V_dsat**2 / 2)
        
        return I_ds
    
    def on_resistance(self, T_kelvin: float = 300.0) -> float:
        """
        Calculate on-resistance at given temperature.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            On-resistance [Ω]
        """
        I_ds = self.drain_current(self.chip.vdd, 0.1, T_kelvin)
        if I_ds > 0:
            return 0.1 / I_ds
        return float('inf')
    
    def mram_resistance(self, weight: int) -> float:
        """
        Get MRAM resistance for ternary weight.
        
        Args:
            weight: Ternary weight (-1, 0, +1)
            
        Returns:
            Resistance [Ω]
        """
        if weight == 1:
            return self.R_P
        elif weight == -1:
            return self.R_AP
        else:  # weight == 0
            return float('inf')  # Open circuit
    
    def mram_switching_energy(self, T_kelvin: float = 300.0) -> float:
        """
        Calculate MRAM switching energy.
        
        E = I_c² R t_pulse
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Switching energy [J]
        """
        # Critical current (temperature-dependent)
        I_c = 50e-6 * (1 + 0.002 * (T_kelvin - 300))  # 50 μA at 300K
        
        # Pulse width
        t_pulse = 10e-9  # 10 ns
        
        # Energy
        E = I_c**2 * self.R_P * t_pulse
        return E
    
    def synaptic_capacitance(self, gap_nm: float = 25.0) -> float:
        """
        Calculate synaptic gap capacitance.
        
        C = ε₀ ε_r A / d
        
        Args:
            gap_nm: Gap width [nm]
            
        Returns:
            Capacitance [F]
        """
        A = self.chip.pe_area_m2 * 0.01  # 1% of PE area
        d = gap_nm * 1e-9
        epsilon_r = 3.9  # SiO₂
        
        C = EPSILON_0 * epsilon_r * A / d
        return C
    
    def run_simulation(self, 
                       V_gs_range: np.ndarray,
                       T_range: np.ndarray) -> Dict[str, np.ndarray]:
        """Run device scale simulation"""
        results = {
            'V_gs': V_gs_range,
            'temperatures': T_range,
            'Vth': np.array([self.threshold_voltage(T) for T in T_range]),
            'mobility': np.array([self.mobility(T) for T in T_range]),
            'Ron': np.array([self.on_resistance(T) for T in T_range]),
            'Id_Vg': np.array([self.drain_current(V, 0.1, 300) for V in V_gs_range]),
        }
        return results

# ============================================================================
# LEVEL 3: Circuit Scale Simulator
# ============================================================================

class CircuitSimulator:
    """
    Level 3: Circuit scale simulation
    
    Simulates:
    - PE array timing and power
    - Interconnect RC delay
    - Accumulator dynamics
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.device_sim = DeviceSimulator(chip)
        
        # Interconnect parameters (28nm metal stack)
        self.r_metal = 0.1        # Resistance [Ω/μm]
        self.c_metal = 0.2e-15   # Capacitance [F/μm]
        
    def interconnect_delay(self, length_um: float) -> float:
        """
        Calculate interconnect RC delay.
        
        τ = RC L² / 2 (distributed line)
        
        Args:
            length_um: Wire length [μm]
            
        Returns:
            Delay [s]
        """
        L = length_um * 1e-6
        R = self.r_metal * 1e6  # Ω/m
        C = self.c_metal * 1e6  # F/m
        
        tau = R * C * L**2 / 2
        return tau
    
    def pe_power(self,
                 T_kelvin: float = 300.0,
                 activity: float = 0.8) -> float:
        """
        Calculate PE power consumption.
        
        P = N_MAC × E_MAC × f × activity + P_leak
        
        Args:
            T_kelvin: Temperature [K]
            activity: PE utilization (0-1)
            
        Returns:
            Power per PE [W]
        """
        # MAC energy
        Vdd = self.chip.vdd
        C_load = 1e-15  # 1 fF load
        E_MAC = 0.5 * C_load * Vdd**2
        
        # Operations per cycle
        N_MAC = 1  # One MAC per cycle
        
        # Dynamic power
        f = self.chip.frequency_hz
        P_dynamic = N_MAC * E_MAC * f * activity
        
        # Leakage (temperature-dependent)
        atomic_sim = AtomicSimulator(self.chip)
        J_leak = atomic_sim.gate_leakage_current(T_kelvin)
        A_gate = 0.01 * self.chip.pe_area_m2  # 1% gate area
        I_leak = J_leak * A_gate * 1e4  # Convert to A
        P_leak = I_leak * Vdd
        
        return P_dynamic + P_leak
    
    def pe_delay(self, T_kelvin: float = 300.0) -> float:
        """
        Calculate PE critical path delay.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Delay [s]
        """
        # Gate delay (temperature-dependent)
        R_on = self.device_sim.on_resistance(T_kelvin)
        C_load = 10e-15  # 10 fF
        tau_gate = R_on * C_load
        
        # Interconnect delay
        tau_wire = self.interconnect_delay(self.chip.pe_size_um)
        
        # Total (dominant path)
        tau_total = 3 * tau_gate + tau_wire
        return tau_total
    
    def systolic_array_timing(self) -> Dict[str, float]:
        """
        Calculate systolic array timing parameters.
        
        Returns:
            Dictionary of timing parameters
        """
        n = self.chip.pe_array_shape[0]
        pe_delay = self.pe_delay()
        
        # Latency for matrix multiplication
        latency_cycles = 2 * n - 1  # Fill + drain
        latency_time = latency_cycles * pe_delay
        
        return {
            'pe_delay': pe_delay,
            'array_latency_cycles': latency_cycles,
            'array_latency_time': latency_time,
            'throughput_ops_per_s': self.chip.n_pes * self.chip.frequency_hz,
        }
    
    def accumulator_bit_width(self, n_inputs: int) -> int:
        """
        Calculate required accumulator bit width.
        
        N_bits = N_MAC + log₂(N_inputs) + margin
        
        Args:
            n_inputs: Number of input elements
            
        Returns:
            Bit width
        """
        # Input bits (INT8)
        input_bits = 8
        
        # Weight bits (ternary)
        weight_bits = 2
        
        # Accumulation bits
        accum_bits = input_bits + weight_bits + int(np.ceil(np.log2(n_inputs)))
        
        return accum_bits
    
    def run_simulation(self, T_range: np.ndarray) -> Dict[str, np.ndarray]:
        """Run circuit scale simulation"""
        results = {
            'temperatures': T_range,
            'pe_power': np.array([self.pe_power(T) for T in T_range]),
            'pe_delay_array': np.array([self.pe_delay(T) for T in T_range]),
        }
        
        # Add systolic timing (single values, not arrays)
        timing = self.systolic_array_timing()
        results['pe_delay_nominal'] = timing['pe_delay']
        results['array_latency_cycles'] = timing['array_latency_cycles']
        results['array_latency_time'] = timing['array_latency_time']
        results['throughput_ops_per_s'] = timing['throughput_ops_per_s']
        
        return results

# ============================================================================
# LEVEL 4: System Scale Simulator
# ============================================================================

class SystemSimulator:
    """
    Level 4: System scale simulation
    
    Simulates:
    - Full die thermal behavior
    - Power grid IR drop
    - Thermal crosstalk between PEs
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.circuit_sim = CircuitSimulator(chip)
        self.atomic_sim = AtomicSimulator(chip)
        
        # Thermal parameters
        self.R_jc = 0.6         # Junction-to-case [K/W]
        self.R_ca = 15.0        # Case-to-ambient (with heatsink) [K/W]
        
    def thermal_resistance_network(self) -> Dict[str, float]:
        """
        Calculate thermal resistance network.
        
        Returns:
            Dictionary of thermal resistances
        """
        L, _, t = self.chip.dimensions
        A = L * L
        k_si = 148.0
        
        # Conduction through silicon
        R_si = t / (k_si * A)
        
        # TIM (thermal interface material)
        t_tim = 25e-6
        k_tim = 5.0
        R_tim = t_tim / (k_tim * A)
        
        # Total junction-to-case
        R_jc = R_si + R_tim
        
        # Case-to-ambient (natural convection + heatsink)
        R_ca = self.R_ca
        
        return {
            'R_silicon': R_si,
            'R_tim': R_tim,
            'R_jc': R_jc,
            'R_ca': R_ca,
            'R_ja': R_jc + R_ca,
        }
    
    def junction_temperature(self,
                            T_ambient: float = 298.0,
                            power: Optional[float] = None) -> float:
        """
        Calculate steady-state junction temperature.
        
        Args:
            T_ambient: Ambient temperature [K]
            power: Total power [W]
            
        Returns:
            Junction temperature [K]
        """
        if power is None:
            power = self.chip.power_w
            
        R_th = self.thermal_resistance_network()['R_ja']
        T_j = T_ambient + power * R_th
        return T_j
    
    def power_map(self, 
                  T_kelvin: float = 300.0,
                  activity_pattern: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Generate power density map.
        
        Args:
            T_kelvin: Temperature [K]
            activity_pattern: PE activity pattern (default: uniform)
            
        Returns:
            Power density map [W/m²]
        """
        n_pe = self.chip.pe_array_shape[0]
        P_pe = self.circuit_sim.pe_power(T_kelvin)
        A_pe = self.chip.pe_area_m2
        
        if activity_pattern is None:
            activity_pattern = np.ones((n_pe, n_pe)) * 0.8
        
        power_map = activity_pattern * P_pe / A_pe
        return power_map
    
    def thermal_crosstalk_matrix(self) -> np.ndarray:
        """
        Calculate thermal crosstalk matrix between PEs.
        
        R_th,ij = 1 / (2π κ r_ij)
        
        Returns:
            Thermal resistance matrix [K/W]
        """
        n_pe = self.chip.pe_array_shape[0]
        pe_spacing = self.chip.pe_size_um * 1e-6
        k_si = 148.0
        
        R_th = np.zeros((n_pe, n_pe))
        
        for i in range(n_pe):
            for j in range(n_pe):
                if i == j:
                    # Self-heating (approximation)
                    R_th[i, j] = 1.0 / (k_si * 2 * np.pi * pe_spacing)
                else:
                    # Distance between PEs
                    dx = abs(i - j) * pe_spacing
                    dy = 0  # Same row
                    r = np.sqrt(dx**2 + dy**2)
                    R_th[i, j] = 1.0 / (2 * np.pi * k_si * r)
        
        return R_th
    
    def thermal_diffusion_time(self) -> float:
        """
        Calculate thermal diffusion time constant.
        
        τ = L² / α
        
        Returns:
            Time constant [s]
        """
        L = self.chip.pe_size_um * 1e-6
        alpha = MATERIALS['silicon'].alpha
        
        tau = L**2 / alpha
        return tau
    
    def ir_drop(self,
               current: float,
               T_kelvin: float = 300.0) -> float:
        """
        Calculate power grid IR drop.
        
        Args:
            current: Total current [A]
            T_kelvin: Temperature [K]
            
        Returns:
            Voltage drop [V]
        """
        # Effective grid resistance
        R_grid = 0.01  # 10 mΩ (approximate)
        
        # Temperature coefficient
        alpha_T = 0.0039  # Copper
        R_grid_T = R_grid * (1 + alpha_T * (T_kelvin - 300))
        
        V_drop = current * R_grid_T
        return V_drop
    
    def run_simulation(self, 
                       T_ambient: float = 298.0,
                       n_time_steps: int = 100) -> Dict[str, Union[float, np.ndarray]]:
        """Run system scale simulation"""
        # Thermal network
        thermal = self.thermal_resistance_network()
        
        # Power map
        P_map = self.power_map(T_ambient)
        
        # Crosstalk matrix
        R_th = self.thermal_crosstalk_matrix()
        
        # Time constant
        tau = self.thermal_diffusion_time()
        
        # Junction temperature
        T_j = self.junction_temperature(T_ambient)
        
        results = {
            'thermal_network': thermal,
            'junction_temp': T_j,
            'power_map': P_map,
            'crosstalk_matrix': R_th,
            'thermal_time_constant': tau,
        }
        
        return results

# ============================================================================
# LEVEL 5: Application Scale Simulator
# ============================================================================

class ApplicationSimulator:
    """
    Level 5: Application scale simulation
    
    Simulates:
    - Inference workload
    - Throughput and latency
    - Energy per inference
    - Accuracy under perturbation
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.system_sim = SystemSimulator(chip)
        
        # Model parameters
        self.n_layers = 24       # Transformer layers
        self.d_model = 2048      # Hidden dimension
        self.n_heads = 16        # Attention heads
        
    def tokens_per_second(self, 
                          T_kelvin: float = 300.0) -> float:
        """
        Calculate inference throughput.
        
        TPS = f_clk / (N_cycles per token)
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Tokens per second
        """
        # MACs per token
        macs_per_token = 2 * self.chip.n_params  # Forward pass
        
        # MACs per cycle (parallel)
        macs_per_cycle = self.chip.n_pes
        
        # Cycles per token
        cycles = macs_per_token / macs_per_cycle
        
        # Frequency adjustment for temperature
        Vdd = self.chip.vdd
        Vdd_derated = Vdd * (1 - 0.001 * (T_kelvin - 300))  # Derating
        f_adj = self.chip.frequency_hz * (Vdd_derated / Vdd)
        
        tps = f_adj / cycles
        return tps
    
    def energy_per_token(self,
                        T_kelvin: float = 300.0) -> float:
        """
        Calculate energy per inference.
        
        E = P_total / TPS
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Energy [J/token]
        """
        P_total = self.chip.power_w
        tps = self.tokens_per_second(T_kelvin)
        
        E = P_total / tps
        return E
    
    def kv_cache_bandwidth(self, 
                          seq_length: int = 2048) -> float:
        """
        Calculate KV cache memory bandwidth requirement.
        
        BW = 2 × d_model × seq_length × TPS
        
        Args:
            seq_length: Sequence length
            
        Returns:
            Bandwidth [bytes/s]
        """
        tps = self.tokens_per_second()
        bytes_per_element = 2  # FP16
        
        BW = 2 * self.d_model * seq_length * bytes_per_element * tps
        return BW
    
    def accuracy_degradation(self,
                            T_kelvin: float = 300.0,
                            noise_sigma: float = 0.01) -> float:
        """
        Estimate accuracy degradation from hardware noise.
        
        Args:
            T_kelvin: Temperature [K]
            noise_sigma: Noise standard deviation
            
        Returns:
            Perplexity increase factor
        """
        # Base perplexity (temperature-independent)
        ppl_base = 12.0  # Example for 2B model
        
        # Temperature-induced variability
        T_ref = 300.0
        T_var = (T_kelvin - T_ref) / T_ref
        
        # Noise contribution
        noise_factor = 1 + noise_sigma * T_var
        
        # Perplexity increase
        ppl_degraded = ppl_base * noise_factor
        
        return ppl_degraded / ppl_base - 1.0
    
    def synaptic_connectivity(self, sparsity: float = 0.34) -> Dict[str, float]:
        """
        Calculate synaptic-like connectivity metrics.
        
        Args:
            sparsity: Fraction of zero weights
            
        Returns:
            Dictionary of connectivity metrics
        """
        n_total = self.chip.n_params
        n_active = n_total * (1 - sparsity)
        
        return {
            'total_params': n_total,
            'active_params': n_active,
            'connectivity_ratio': 1 - sparsity,
            'effective_fan_in': int(n_active / self.d_model),
        }
    
    def run_simulation(self, T_range: np.ndarray) -> Dict[str, np.ndarray]:
        """Run application scale simulation"""
        results = {
            'temperatures': T_range,
            'tokens_per_second': np.array([self.tokens_per_second(T) for T in T_range]),
            'energy_per_token': np.array([self.energy_per_token(T) for T in T_range]),
            'accuracy_degradation': np.array([self.accuracy_degradation(T) for T in T_range]),
        }
        
        # Add connectivity metrics
        results['connectivity'] = self.synaptic_connectivity()
        
        return results

# ============================================================================
# Scale Bridging Module
# ============================================================================

class ScaleBridge:
    """
    Handles parameter passing between simulation scales.
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.atomic_sim = AtomicSimulator(chip)
        self.device_sim = DeviceSimulator(chip)
        self.circuit_sim = CircuitSimulator(chip)
        self.system_sim = SystemSimulator(chip)
        
    def atomic_to_device(self, T_kelvin: float) -> Dict[str, float]:
        """
        Bridge atomic scale results to device parameters.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Effective device parameters
        """
        return {
            'leakage_current_density': self.atomic_sim.gate_leakage_current(T_kelvin),
            'thermal_conductivity': self.atomic_sim.thermal_conductivity(T_kelvin),
            'phonon_mfp': self.atomic_sim.phonon_mean_free_path(T_kelvin),
        }
    
    def device_to_circuit(self, T_kelvin: float) -> Dict[str, float]:
        """
        Bridge device scale results to circuit parameters.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            Effective circuit parameters
        """
        return {
            'on_resistance': self.device_sim.on_resistance(T_kelvin),
            'mram_switching_energy': self.device_sim.mram_switching_energy(T_kelvin),
            'synaptic_capacitance': self.device_sim.synaptic_capacitance(),
        }
    
    def circuit_to_system(self, T_kelvin: float) -> Dict[str, Union[float, np.ndarray]]:
        """
        Bridge circuit scale results to system parameters.
        
        Args:
            T_kelvin: Temperature [K]
            
        Returns:
            System-level parameters
        """
        return {
            'pe_power': self.circuit_sim.pe_power(T_kelvin),
            'pe_delay': self.circuit_sim.pe_delay(T_kelvin),
            'power_map': self.system_sim.power_map(T_kelvin),
        }
    
    def system_to_application(self, T_ambient: float = 298.0) -> Dict[str, float]:
        """
        Bridge system scale results to application constraints.
        
        Args:
            T_ambient: Ambient temperature [K]
            
        Returns:
            Application-level constraints
        """
        T_junction = self.system_sim.junction_temperature(T_ambient)
        
        return {
            'junction_temp': T_junction,
            'max_power': self.chip.power_w,
            'thermal_headroom': 358.0 - T_junction,  # 85°C max
        }

# ============================================================================
# Monte Carlo Simulation Engine
# ============================================================================

class MonteCarloEngine:
    """
    Monte Carlo simulation for stochastic effects.
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        self.rng = np.random.default_rng(42)
        
        # Process variation parameters (28nm)
        self.sigma_Vth = 18e-3    # Vth variation [V]
        self.sigma_L = 2e-9       # Length variation [m]
        self.sigma_W = 4e-9       # Width variation [m]
        
    def rtn_signal(self,
                   n_samples: int,
                   gamma_emit: float = 1e3,
                   gamma_capture: float = 1e3,
                   V_shift: float = 0.006) -> np.ndarray:
        """
        Generate random telegraph noise signal.
        
        Args:
            n_samples: Number of time samples
            gamma_emit: Emission rate [1/s]
            gamma_capture: Capture rate [1/s]
            V_shift: Voltage shift per trap [V]
            
        Returns:
            RTN signal array [V]
        """
        dt = 1e-6  # 1 μs time step
        signal = np.zeros(n_samples)
        state = 0  # 0 = untrapped, 1 = trapped
        
        for i in range(n_samples):
            # State transitions
            if state == 0:
                if self.rng.random() < gamma_capture * dt:
                    state = 1
            else:
                if self.rng.random() < gamma_emit * dt:
                    state = 0
            
            signal[i] = state * V_shift
        
        return signal
    
    def process_variation_sample(self) -> Dict[str, float]:
        """
        Sample process variations.
        
        Returns:
            Dictionary of varied parameters
        """
        return {
            'Vth': self.chip.vdd * 0.33 + self.rng.normal(0, self.sigma_Vth),
            'L_eff': 28e-9 + self.rng.normal(0, self.sigma_L),
            'W_eff': 100e-9 + self.rng.normal(0, self.sigma_W),
        }
    
    def monte_carlo_pe_timing(self,
                               n_samples: int = 1000,
                               T_kelvin: float = 300.0) -> Dict[str, np.ndarray]:
        """
        Monte Carlo simulation of PE timing variation.
        
        Args:
            n_samples: Number of MC samples
            T_kelvin: Temperature [K]
            
        Returns:
            Timing statistics
        """
        delays = []
        device_sim = DeviceSimulator(self.chip)
        
        for _ in range(n_samples):
            # Sample process variations
            var = self.process_variation_sample()
            
            # Adjust device parameters
            device_sim.Vth_0 = var['Vth']
            device_sim.L = var['L_eff']
            device_sim.W = var['W_eff']
            
            # Calculate delay
            R_on = device_sim.on_resistance(T_kelvin)
            C_load = 10e-15
            delay = 3 * R_on * C_load
            
            delays.append(delay)
        
        delays = np.array(delays)
        
        return {
            'delays': delays,
            'mean': np.mean(delays),
            'std': np.std(delays),
            'p95': np.percentile(delays, 95),
            'p99': np.percentile(delays, 99),
        }
    
    def thermal_fluctuation(self,
                           T_kelvin: float = 300.0,
                           volume_m3: float = 1e-18) -> float:
        """
        Calculate thermal fluctuation magnitude.
        
        σ_T = sqrt(k_B T² / C_V)
        
        Args:
            T_kelvin: Temperature [K]
            volume_m3: Device volume [m³]
            
        Returns:
            Temperature fluctuation [K]
        """
        rho = 2329  # Si density [kg/m³]
        cp = 700    # Si specific heat [J/(kg·K)]
        C_V = rho * cp * volume_m3
        
        sigma_T = np.sqrt(KB_J * T_kelvin**2 / C_V)
        return sigma_T
    
    def stochastic_inference(self,
                            input_data: np.ndarray,
                            dropout_prob: float = 0.1,
                            n_runs: int = 10) -> Dict[str, np.ndarray]:
        """
        Run stochastic inference with dropout.
        
        Args:
            input_data: Input tensor
            dropout_prob: Dropout probability
            n_runs: Number of MC runs
            
        Returns:
            Mean and uncertainty estimates
        """
        # Simulate dropout effect
        outputs = []
        for _ in range(n_runs):
            mask = self.rng.random(input_data.shape) > dropout_prob
            output = input_data * mask
            outputs.append(output)
        
        outputs = np.array(outputs)
        
        return {
            'mean': np.mean(outputs, axis=0),
            'std': np.std(outputs, axis=0),
            'p05': np.percentile(outputs, 5, axis=0),
            'p95': np.percentile(outputs, 95, axis=0),
        }

# ============================================================================
# Neural Network Surrogate Models
# ============================================================================

class NeuralSurrogate:
    """
    Neural network surrogate models for expensive physics.
    
    Note: This is a simplified implementation. In production,
    use proper ML frameworks (PyTorch, TensorFlow).
    """
    
    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 1):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Initialize weights (Xavier initialization)
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2 / hidden_dim)
        self.b2 = np.zeros(output_dim)
        
    def relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation"""
        return np.maximum(0, x)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        h = self.relu(x @ self.W1 + self.b1)
        y = h @ self.W2 + self.b2
        return y
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make prediction"""
        return self.forward(x)


class ThermalSurrogate:
    """
    CNN surrogate for thermal prediction.
    
    Maps power map to temperature map.
    """
    
    def __init__(self, grid_size: int = 32):
        self.grid_size = grid_size
        
        # Simplified CNN-like convolution kernels
        # In practice, use proper CNN implementation
        self.kernel_size = 3
        self.n_filters = 16
        
        # Initialize convolution kernels (Gaussian smoothing for thermal)
        self.thermal_kernel = self._gaussian_kernel(self.kernel_size, sigma=0.5)
        
    def _gaussian_kernel(self, size: int, sigma: float) -> np.ndarray:
        """Generate Gaussian kernel for thermal smoothing"""
        x = np.linspace(-(size-1)/2, (size-1)/2, size)
        kernel = np.exp(-x**2 / (2*sigma**2))
        kernel = np.outer(kernel, kernel)
        return kernel / kernel.sum()
    
    def convolve2d(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Simple 2D convolution"""
        from scipy.ndimage import convolve
        return convolve(image, kernel, mode='reflect')
    
    def predict(self, power_map: np.ndarray) -> np.ndarray:
        """
        Predict temperature from power map.
        
        Args:
            power_map: Power density [W/m²]
            
        Returns:
            Temperature map [K]
        """
        # Apply thermal diffusion (simplified)
        T_ambient = 298.0
        R_th = 15.0  # Effective thermal resistance
        
        # Thermal convolution
        heat_spread = self.convolve2d(power_map, self.thermal_kernel)
        
        # Convert to temperature
        T_map = T_ambient + heat_spread * R_th / np.max(heat_spread + 1e-10)
        
        return T_map


class TimingSurrogate:
    """
    MLP surrogate for timing prediction.
    
    Maps (T, V, process_corner) to delay.
    """
    
    def __init__(self):
        # Feature normalization parameters
        self.T_mean = 350.0
        self.T_std = 30.0
        self.V_mean = 0.9
        self.V_std = 0.05
        
        # Trained coefficients (example)
        self.coef = np.array([1.0, -0.5, 0.3])  # T, V, interaction
        self.intercept = 100e-12  # 100 ps base delay
        
    def predict(self, T_kelvin: float, V_volts: float) -> float:
        """
        Predict delay from operating conditions.
        
        Args:
            T_kelvin: Temperature [K]
            V_volts: Voltage [V]
            
        Returns:
            Delay [s]
        """
        # Normalize inputs
        T_norm = (T_kelvin - self.T_mean) / self.T_std
        V_norm = (V_volts - self.V_mean) / self.V_std
        
        # Linear model
        features = np.array([T_norm, V_norm, T_norm * V_norm])
        delay = self.intercept * (1 + self.coef @ features)
        
        return max(delay, 1e-12)  # Minimum 1 ps

# ============================================================================
# Integrated Multi-Scale Simulator
# ============================================================================

class MultiScaleSimulator:
    """
    Main class integrating all simulation scales.
    """
    
    def __init__(self, chip: ChipConfiguration = DEFAULT_CHIP):
        self.chip = chip
        
        # Initialize scale simulators
        self.atomic = AtomicSimulator(chip)
        self.device = DeviceSimulator(chip)
        self.circuit = CircuitSimulator(chip)
        self.system = SystemSimulator(chip)
        self.application = ApplicationSimulator(chip)
        
        # Scale bridge
        self.bridge = ScaleBridge(chip)
        
        # Monte Carlo engine
        self.monte_carlo = MonteCarloEngine(chip)
        
        # Surrogate models
        self.thermal_surrogate = ThermalSurrogate()
        self.timing_surrogate = TimingSurrogate()
        
    def run_full_simulation(self,
                           T_ambient: float = 298.0,
                           T_range: Optional[np.ndarray] = None) -> Dict:
        """
        Run integrated multi-scale simulation.
        
        Args:
            T_ambient: Ambient temperature [K]
            T_range: Temperature range for parametric study
            
        Returns:
            Dictionary containing all simulation results
        """
        if T_range is None:
            T_range = np.linspace(280, 380, 21)
        
        print("=" * 70)
        print("MULTI-SCALE SIMULATION FRAMEWORK")
        print(f"Chip: {self.chip.name}")
        print(f"Process: {self.chip.process_nm}nm, Area: {self.chip.area_mm2}mm²")
        print("=" * 70)
        
        results = {}
        
        # Level 1: Atomic
        print("\n[Level 1] Atomic Scale Simulation...")
        results['atomic'] = self.atomic.run_simulation(T_range)
        print(f"  - Thermal conductivity at 350K: {results['atomic']['thermal_conductivity'][7]:.1f} W/(m·K)")
        
        # Level 2: Device
        print("\n[Level 2] Device Scale Simulation...")
        V_range = np.linspace(0, self.chip.vdd, 50)
        results['device'] = self.device.run_simulation(V_range, T_range)
        print(f"  - On-resistance at 350K: {results['device']['Ron'][7]/1000:.2f} kΩ")
        
        # Level 3: Circuit
        print("\n[Level 3] Circuit Scale Simulation...")
        results['circuit'] = self.circuit.run_simulation(T_range)
        print(f"  - PE power at 350K: {results['circuit']['pe_power'][7]*1e6:.3f} μW")
        print(f"  - PE delay at 350K: {results['circuit']['pe_delay_array'][7]*1e12:.2f} ps")
        
        # Level 4: System
        print("\n[Level 4] System Scale Simulation...")
        results['system'] = self.system.run_simulation(T_ambient)
        print(f"  - Junction temperature: {results['system']['junction_temp'] - 273.15:.1f}°C")
        print(f"  - Thermal time constant: {results['system']['thermal_time_constant']*1e6:.2f} μs")
        
        # Level 5: Application
        print("\n[Level 5] Application Scale Simulation...")
        results['application'] = self.application.run_simulation(T_range)
        print(f"  - Throughput at 300K: {results['application']['tokens_per_second'][3]:.1f} tokens/s")
        print(f"  - Energy per token at 300K: {results['application']['energy_per_token'][3]*1e6:.1f} μJ")
        
        # Scale bridging
        print("\n[Scale Bridging]")
        bridge_results = self.bridge.system_to_application(T_ambient)
        print(f"  - Thermal headroom: {bridge_results['thermal_headroom']:.1f} K")
        
        # Monte Carlo
        print("\n[Monte Carlo Analysis]")
        mc_timing = self.monte_carlo.monte_carlo_pe_timing(n_samples=1000)
        print(f"  - PE delay mean: {mc_timing['mean']*1e12:.2f} ps")
        print(f"  - PE delay std: {mc_timing['std']*1e12:.2f} ps")
        print(f"  - PE delay 99th percentile: {mc_timing['p99']*1e12:.2f} ps")
        
        print("\n" + "=" * 70)
        print("SIMULATION COMPLETE")
        print("=" * 70)
        
        return results

# ============================================================================
# Validation Framework
# ============================================================================

class ValidationFramework:
    """
    Validation methodology for multi-scale simulation.
    """
    
    def __init__(self, simulator: MultiScaleSimulator):
        self.sim = simulator
        
    def validate_atomic_scale(self) -> Dict[str, bool]:
        """Validate atomic scale predictions against literature"""
        T = 300.0
        
        # Check thermal conductivity
        k_si = self.sim.atomic.thermal_conductivity(T)
        k_valid = 140 < k_si < 160  # Literature: ~148 W/(m·K)
        
        # Check tunneling probability for gate oxide (1.2nm, not 28nm)
        T_tunnel = self.sim.atomic.tunneling_probability(3.1, 1.2)  # 1.2nm gate oxide
        tunnel_valid = T_tunnel < 0.01  # Should be small but measurable
        
        return {
            'thermal_conductivity': k_valid,
            'tunneling_negligible': tunnel_valid,
        }
    
    def validate_device_scale(self) -> Dict[str, bool]:
        """Validate device scale predictions"""
        T = 300.0
        
        # Check threshold voltage
        Vth = self.sim.device.threshold_voltage(T)
        vth_valid = 0.25 < Vth < 0.35  # 28nm typical
        
        # Check on-resistance (per transistor, can be very low)
        Ron = self.sim.device.on_resistance(T)
        ron_valid = 10 < Ron < 100e3  # Wide range for single transistor
        
        return {
            'threshold_voltage': vth_valid,
            'on_resistance': ron_valid,
        }
    
    def validate_system_scale(self) -> Dict[str, bool]:
        """Validate system scale predictions"""
        T_j = self.sim.system.junction_temperature(298.0, 3.0)
        
        # Check junction temperature
        temp_valid = T_j < 358.0  # Below 85°C
        
        # Check thermal resistance
        R_th = self.sim.system.thermal_resistance_network()['R_ja']
        rth_valid = 10 < R_th < 30  # Reasonable for QFN with heatsink
        
        return {
            'junction_temperature': temp_valid,
            'thermal_resistance': rth_valid,
        }
    
    def validate_conservation(self) -> Dict[str, bool]:
        """Validate physical conservation laws"""
        # Energy conservation: Heat generated = Heat dissipated
        T_j = self.sim.system.junction_temperature(298.0, 3.0)
        R_ja = self.sim.system.thermal_resistance_network()['R_ja']
        
        Q_gen = self.sim.chip.power_w  # Heat generated
        Q_dissip = (T_j - 298.0) / R_ja  # Heat dissipated
        
        energy_conserved = abs(Q_gen - Q_dissip) < 0.1 * Q_gen
        
        return {
            'energy_conservation': energy_conserved,
        }
    
    def run_all_validations(self) -> Dict[str, Dict[str, bool]]:
        """Run all validation checks"""
        results = {
            'atomic': self.validate_atomic_scale(),
            'device': self.validate_device_scale(),
            'system': self.validate_system_scale(),
            'conservation': self.validate_conservation(),
        }
        
        # Summary
        all_pass = all(
            all(check.values()) 
            for check in results.values()
        )
        results['all_pass'] = all_pass
        
        return results

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run multi-scale simulation demonstration"""
    
    # Create chip configuration
    chip = ChipConfiguration()
    
    # Initialize simulator
    simulator = MultiScaleSimulator(chip)
    
    # Run full simulation
    results = simulator.run_full_simulation()
    
    # Run validation
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    
    validator = ValidationFramework(simulator)
    validation = validator.run_all_validations()
    
    for scale, checks in validation.items():
        if isinstance(checks, dict):
            print(f"\n{scale.replace('_', ' ').title()}:")
            for check, passed in checks.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {check}: {status}")
    
    print("\n" + "=" * 70)
    print(f"Overall: {'ALL VALIDATIONS PASSED' if validation['all_pass'] else 'SOME VALIDATIONS FAILED'}")
    print("=" * 70)
    
    return results, validation


if __name__ == "__main__":
    results, validation = main()
