#!/usr/bin/env python3
"""
Scientific Simulation Suite for Mask-Locked Inference Chip
==========================================================

This module provides comprehensive physics-based simulations for:
1. Thermal Physics - Heat distribution, thermal resistance
2. Circuit Physics - Ternary logic, RAU units
3. Electromagnetic - Interconnect parasitics, signal integrity
4. Quantum Noise - Thermal, shot, flicker noise
5. Statistical Mechanics - Weight distributions, network dynamics
6. Materials Science - Metal interconnect properties

Author: Mask-Locked Chip Research Team
Date: March 2026
"""

import numpy as np
from scipy import constants
from scipy.integrate import odeint, solve_ivp
from scipy.fft import fft, fftfreq
from scipy.stats import norm, gamma
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict
import json

# Physical Constants
K_B = constants.Boltzmann  # 1.380649e-23 J/K
Q_E = constants.e  # 1.602176634e-19 C
H_BAR = constants.hbar  # 1.054571817e-34 J·s
EPSILON_0 = constants.epsilon_0  # 8.854187817e-12 F/m
MU_0 = constants.mu_0  # 4π × 10^-7 H/m

# Process Parameters (28nm)
@dataclass
class ProcessParams28nm:
    """28nm Process Design Kit Parameters"""
    # Transistor
    vdd: float = 1.0  # V
    vth_n: float = 0.35  # V
    vth_p: float = -0.35  # V
    cox: float = 2.5e-6  # F/cm² (gate oxide capacitance)
    tox: float = 1.2e-9  # m (oxide thickness)
    
    # Interconnect (M1-M8)
    metal_pitch_m1: float = 90e-9  # m
    metal_pitch_m6: float = 200e-9  # m
    metal_thickness_m1: float = 100e-9  # m
    metal_thickness_m6: float = 400e-9  # m
    
    # Resistivity
    rho_cu: float = 2.2e-8  # Ω·m (copper, effective with barrier)
    rho_w: float = 5.6e-8  # Ω·m (tungsten, local interconnect)
    
    # Dielectric
    k_sio2: float = 4.2  # SiO₂ relative permittivity
    k_lowk: float = 2.5  # Low-k dielectric
    
    # Thermal
    thermal_conductivity_si: float = 150  # W/(m·K)
    thermal_conductivity_sio2: float = 1.4  # W/(m·K)
    thermal_conductivity_cu: float = 400  # W/(m·K)


class ThermalPhysicsSimulation:
    """
    Thermal physics simulation for mask-locked inference chip.
    
    Models:
    - Heat generation from switching activity
    - Thermal resistance network
    - Heat spreading in silicon substrate
    - Temperature-dependent leakage power
    """
    
    def __init__(self, process: ProcessParams28nm = None):
        self.process = process or ProcessParams28nm()
        
    def thermal_resistance_network(self, 
                                   die_area: float = 25e-6,  # m²
                                   die_thickness: float = 780e-6,  # m
                                   package_type: str = "BGA") -> Dict:
        """
        Calculate thermal resistance network from junction to ambient.
        
        R_th = L / (k × A)
        """
        # Silicon thermal resistance (spreading)
        r_si = die_thickness / (self.process.thermal_conductivity_si * np.sqrt(die_area))
        
        # Package thermal resistance (empirical)
        package_r = {
            "BGA": 15.0,  # K/W for 15×15mm BGA
            "QFN": 25.0,  # K/W for QFN
            "WLCSP": 8.0,  # K/W for wafer-level chip-scale
        }
        
        r_pkg = package_r.get(package_type, 15.0)
        
        # Heat sink / PCB thermal resistance
        r_heatsink = 5.0  # K/W (typical PCB thermal path)
        r_ambient = 10.0  # K/W (natural convection)
        
        return {
            "r_junction_to_case": r_si + r_pkg,
            "r_case_to_heatsink": r_heatsink,
            "r_heatsink_to_ambient": r_ambient,
            "r_total": r_si + r_pkg + r_heatsink + r_ambient,
            "silicon_r": r_si,
            "package_r": r_pkg,
        }
    
    def power_density_map(self, 
                          array_size: Tuple[int, int] = (32, 32),
                          power_per_pe: float = 0.5e-3,  # W
                          hotspot_factor: float = 2.0) -> np.ndarray:
        """
        Generate power density map across the PE array.
        
        Accounts for non-uniform activity and hotspots.
        """
        power_map = np.ones(array_size) * power_per_pe
        
        # Add thermal gradients (edges run cooler)
        for i in range(array_size[0]):
            for j in range(array_size[1]):
                edge_factor = 1.0 - 0.3 * min(i, j, array_size[0]-1-i, array_size[1]-1-j) / min(array_size)
                power_map[i, j] *= edge_factor
        
        # Add hotspots (high-activity regions)
        center = (array_size[0]//2, array_size[1]//2)
        for i in range(array_size[0]):
            for j in range(array_size[1]):
                dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
                if dist < 5:
                    power_map[i, j] *= hotspot_factor * (1 - dist/5)
        
        return power_map
    
    def solve_2d_heat_equation(self,
                               power_map: np.ndarray,
                               t_ambient: float = 300.0,  # K
                               dt: float = 1e-6,  # s
                               total_time: float = 1e-3,  # s
                               die_size: float = 5e-3) -> np.ndarray:
        """
        Solve 2D heat equation with finite difference method.
        
        ∂T/∂t = α × ∇²T + Q/(ρ×c_p)
        
        Where α = k/(ρ×c_p) is thermal diffusivity.
        """
        n_steps = int(total_time / dt)
        
        # Thermal properties of silicon
        rho = 2329  # kg/m³ (silicon density)
        c_p = 700  # J/(kg·K) (specific heat)
        k = self.process.thermal_conductivity_si
        alpha = k / (rho * c_p)  # thermal diffusivity
        
        # Grid
        nx, ny = power_map.shape
        dx = die_size / nx
        dy = die_size / ny
        
        # Stability condition: α×dt/dx² < 0.5
        stability = alpha * dt / (dx**2)
        if stability > 0.5:
            dt = 0.4 * dx**2 / alpha
            n_steps = int(total_time / dt)
        
        # Initialize temperature
        T = np.ones_like(power_map) * t_ambient
        
        # Time evolution
        temperatures = [T.copy()]
        
        for _ in range(n_steps):
            T_new = T.copy()
            
            # Finite difference (5-point stencil)
            for i in range(1, nx-1):
                for j in range(1, ny-1):
                    laplacian = (T[i+1, j] + T[i-1, j] + T[i, j+1] + T[i, j-1] - 4*T[i, j]) / dx**2
                    heat_source = power_map[i, j] / (rho * c_p * dx * dy * die_size)
                    T_new[i, j] = T[i, j] + dt * (alpha * laplacian + heat_source)
            
            # Boundary conditions (convection)
            h_conv = 10  # W/(m²·K) natural convection
            T_new[0, :] = T_new[1, :] - h_conv * dx / k * (T_new[1, :] - t_ambient)
            T_new[-1, :] = T_new[-2, :] - h_conv * dx / k * (T_new[-2, :] - t_ambient)
            T_new[:, 0] = T_new[:, 1] - h_conv * dy / k * (T_new[:, 1] - t_ambient)
            T_new[:, -1] = T_new[:, -2] - h_conv * dy / k * (T_new[:, -2] - t_ambient)
            
            T = T_new
            
            if _ % (n_steps // 10) == 0:
                temperatures.append(T.copy())
        
        temperatures.append(T.copy())
        return np.array(temperatures)
    
    def temperature_dependent_leakage(self,
                                      T: np.ndarray,
                                      I_leak_300K: float = 1e-9,  # A at 300K
                                      E_a: float = 0.5) -> np.ndarray:
        """
        Calculate temperature-dependent leakage current.
        
        I_leak(T) = I_leak(T₀) × exp[(E_a/k_B) × (1/T₀ - 1/T)]
        """
        T0 = 300.0  # K
        I_leak = I_leak_300K * np.exp((E_a * Q_E / K_B) * (1/T0 - 1/T))
        return I_leak
    
    def steady_state_temperature(self,
                                 power_total: float = 3.0,  # W
                                 t_ambient: float = 300.0) -> float:
        """Calculate steady-state junction temperature."""
        r_network = self.thermal_resistance_network()
        return t_ambient + power_total * r_network["r_total"]


class CircuitPhysicsSimulation:
    """
    Circuit-level physics simulation for ternary logic and RAU.
    
    Models:
    - Ternary logic gate behavior
    - RAU (Rotation-Accumulate Unit) operation
    - Interconnect delay and power
    - Ternary weight encoding in metal
    """
    
    def __init__(self, process: ProcessParams28nm = None):
        self.process = process or ProcessParams28nm()
    
    def ternary_inverter_transfer(self, v_in: np.ndarray) -> np.ndarray:
        """
        Ternary inverter transfer characteristic.
        
        Three output levels: 0, VDD/2, VDD
        """
        vdd = self.process.vdd
        vth = self.process.vth_n
        
        v_out = np.zeros_like(v_in)
        
        for i, v in enumerate(v_in):
            if v < vth:
                v_out[i] = vdd  # Output high
            elif v < vdd - vth:
                v_out[i] = vdd / 2  # Output middle
            else:
                v_out[i] = 0  # Output low
        
        # Add smooth transitions (simplified model)
        v_out = np.convolve(v_out, np.ones(10)/10, mode='same')
        
        return v_out
    
    def ternary_weight_resistance(self,
                                  weight: int,  # -1, 0, +1
                                  wire_length: float = 1e-6,  # m
                                  wire_width: float = 100e-9) -> float:
        """
        Calculate effective resistance for ternary weight encoding.
        
        Weight encoded as interconnect routing pattern.
        """
        rho = self.process.rho_cu
        
        if weight == 0:
            # Zero weight: no connection (open circuit)
            return float('inf')
        elif weight == 1:
            # +1: direct connection
            return rho * wire_length / (wire_width * self.process.metal_thickness_m1)
        else:  # weight == -1
            # -1: inverted connection (requires additional inverter)
            r_wire = rho * wire_length / (wire_width * self.process.metal_thickness_m1)
            r_inverter = 500  # Ω (simplified inverter resistance)
            return r_wire + r_inverter
    
    def rau_energy_per_operation(self,
                                 input_bits: int = 8,
                                 clock_freq: float = 1e9) -> Dict:
        """
        Calculate energy per RAU operation.
        
        RAU performs rotation-accumulate instead of multiply-accumulate.
        """
        # Capacitance model
        c_gate = self.process.cox * (1e-6)**2  # F (per gate, 1μm²)
        c_wire = self.calculate_wire_capacitance(1e-3)  # F per mm
        
        # Dynamic energy: E = 0.5 × C × V²
        e_dynamic = 0.5 * (c_gate * 100 + c_wire) * self.process.vdd**2
        
        # Rotation energy (multiplexer switching)
        e_rotation = e_dynamic * input_bits * 0.1  # 10% of gate energy per bit
        
        # Accumulation energy (adder)
        e_accumulate = e_dynamic * input_bits * 0.5
        
        # Total per operation
        e_total = e_rotation + e_accumulate
        
        # Compare to MAC (multiply-accumulate)
        # Multiplier is ~10x more complex than rotation
        e_mac = e_total * 10
        
        return {
            "e_rotation": e_rotation,
            "e_accumulate": e_accumulate,
            "e_total_rau": e_total,
            "e_equivalent_mac": e_mac,
            "savings_ratio": e_mac / e_total,
            "power_at_1ghz": e_total * clock_freq,
        }
    
    def calculate_wire_capacitance(self, length: float) -> float:
        """
        Calculate interconnect capacitance per unit length.
        
        C = C_parallel_plate + C_fringe + C_coupling
        """
        w = self.process.metal_pitch_m1
        t = self.process.metal_thickness_m1
        h = t  # Approximate dielectric thickness
        k = self.process.k_lowk
        
        # Parallel plate capacitance
        c_pp = k * EPSILON_0 * w * length / h
        
        # Fringing capacitance (approximate)
        c_fringe = 2 * k * EPSILON_0 * t * length / (np.pi * h)
        
        # Coupling capacitance (adjacent wires)
        s = w  # Spacing
        c_coupling = k * EPSILON_0 * t * length / s
        
        return c_pp + c_fringe + c_coupling
    
    def wire_delay_rc(self, length: float) -> Dict:
        """
        Calculate RC delay for interconnect.
        
        Elmore delay: τ = R × C
        """
        # Resistance
        r = self.process.rho_cu * length / (self.process.metal_pitch_m1 * self.process.metal_thickness_m1)
        
        # Capacitance
        c = self.calculate_wire_capacitance(length)
        
        # Delay (Elmore)
        delay = r * c
        
        # Bandwidth limit
        bandwidth = 1 / (2 * np.pi * delay) if delay > 0 else float('inf')
        
        return {
            "resistance": r,
            "capacitance": c,
            "delay": delay,
            "bandwidth_hz": bandwidth,
            "delay_ps": delay * 1e12,
        }


class ElectromagneticSimulation:
    """
    Electromagnetic simulation for signal integrity and power delivery.
    
    Models:
    - Interconnect inductance
    - Power distribution network impedance
    - Crosstalk between adjacent wires
    - Simultaneous switching noise
    """
    
    def __init__(self, process: ProcessParams28nm = None):
        self.process = process or ProcessParams28nm()
    
    def wire_inductance(self, length: float, width: float = None) -> float:
        """
        Calculate interconnect inductance.
        
        L ≈ μ₀ × l × (ln(2l/w) - 1) for l >> w
        """
        w = width or self.process.metal_pitch_m1
        
        if length > 10 * w:
            return MU_0 * length * (np.log(2 * length / w) - 1)
        else:
            # Short wire approximation
            return MU_0 * length * 0.5
    
    def pdn_impedance(self,
                      freq: np.ndarray,
                      decap_values: List[float] = [1e-6, 100e-9, 10e-9]) -> np.ndarray:
        """
        Calculate power distribution network impedance vs frequency.
        
        Includes: VRM, PCB, package, on-die decoupling
        """
        z_total = np.zeros_like(freq, dtype=complex)
        
        # VRM impedance (simplified)
        r_vrm = 1e-3  # Ω
        l_vrm = 1e-6  # H
        z_vrm = r_vrm + 1j * 2 * np.pi * freq * l_vrm
        
        # PCB impedance
        r_pcb = 1e-3
        l_pcb = 1e-9
        z_pcb = r_pcb + 1j * 2 * np.pi * freq * l_pcb
        
        # Package impedance
        r_pkg = 5e-3
        l_pkg = 100e-12
        z_pkg = r_pkg + 1j * 2 * np.pi * freq * l_pkg
        
        # On-die decoupling capacitors
        z_decap = np.zeros_like(freq, dtype=complex)
        for c in decap_values:
            # Each capacitor has ESR and ESL
            esr = 0.01  # Ω
            esl = 100e-12  # H
            z_c = esr + 1j * (2 * np.pi * freq * esl - 1 / (2 * np.pi * freq * c + 1e-20))
            z_decap += 1 / (z_c + 1e-20)  # Parallel combination
        
        z_decap = 1 / z_decap if np.any(z_decap > 0) else z_decap
        
        # Total (series combination)
        z_total = z_vrm + z_pcb + z_pkg + z_decap
        
        return np.abs(z_total)
    
    def crosstalk_coefficient(self,
                              victim_length: float,
                              aggressor_length: float,
                              spacing: float = None) -> float:
        """
        Calculate crosstalk coupling coefficient.
        
        K_ct = C_coupling / (C_total + C_load)
        """
        s = spacing or self.process.metal_pitch_m1
        
        # Coupling capacitance
        k = self.process.k_lowk
        h = self.process.metal_thickness_m1
        t = self.process.metal_thickness_m1
        
        c_coupling = k * EPSILON_0 * t * min(victim_length, aggressor_length) / s
        
        # Total capacitance
        c_total = 2 * k * EPSILON_0 * victim_length * t / h + c_coupling
        
        # Coupling coefficient
        k_ct = c_coupling / (c_total + 10e-15)  # +10fF load
        
        return k_ct
    
    def simultaneous_switching_noise(self,
                                     n_switching: int,
                                     i_peak: float = 10e-3,  # A per driver
                                     l_pkg: float = 100e-12) -> float:
        """
        Calculate simultaneous switching noise (ground bounce).
        
        V_ssn = N × L × di/dt
        """
        di_dt = i_peak / 100e-12  # A/s (100ps transition)
        v_ssn = n_switching * l_pkg * di_dt
        return v_ssn


class QuantumNoiseSimulation:
    """
    Quantum and thermal noise simulation.
    
    Models:
    - Thermal (Johnson-Nyquist) noise
    - Shot noise
    - Flicker (1/f) noise
    - Random telegraph noise (RTN)
    """
    
    def __init__(self, temperature: float = 300.0):
        self.T = temperature
    
    def thermal_noise_voltage(self,
                              resistance: float,
                              bandwidth: float) -> float:
        """
        Calculate thermal noise voltage (Johnson-Nyquist).
        
        V_n = sqrt(4 × k_B × T × R × Δf)
        """
        return np.sqrt(4 * K_B * self.T * resistance * bandwidth)
    
    def thermal_noise_current(self,
                               resistance: float,
                               bandwidth: float) -> float:
        """Calculate thermal noise current."""
        return self.thermal_noise_voltage(resistance, bandwidth) / resistance
    
    def shot_noise_current(self,
                           dc_current: float,
                           bandwidth: float) -> float:
        """
        Calculate shot noise current.
        
        I_n = sqrt(2 × q × I_dc × Δf)
        """
        return np.sqrt(2 * Q_E * dc_current * bandwidth)
    
    def flicker_noise_corner_frequency(self,
                                       thermal_noise_density: float,
                                       flicker_coefficient: float = 1e-10) -> float:
        """
        Calculate 1/f noise corner frequency.
        
        f_c where thermal noise equals flicker noise.
        """
        # Flicker noise: S_v = K_f / f
        # Thermal noise: S_v = 4 k_B T R
        # Corner: f_c = K_f / (4 k_B T R)
        
        f_c = flicker_coefficient / thermal_noise_density**2 if thermal_noise_density > 0 else 1e6
        return f_c
    
    def noise_margin_degradation(self,
                                 signal_amplitude: float,
                                 noise_rms: float,
                                 ber_target: float = 1e-12) -> Dict:
        """
        Calculate noise margin and bit error rate.
        
        Assumes Gaussian noise distribution.
        """
        # Number of sigma for target BER
        sigma_required = norm.ppf(1 - ber_target)
        
        # Available noise margin
        noise_margin = signal_amplitude / 2 - sigma_required * noise_rms
        
        # Actual BER
        if noise_rms > 0:
            ber_actual = 1 - norm.cdf(signal_amplitude / (2 * noise_rms))
        else:
            ber_actual = 0
        
        return {
            "noise_margin": noise_margin,
            "noise_margin_ratio": noise_margin / signal_amplitude if signal_amplitude > 0 else 0,
            "sigma_available": signal_amplitude / (2 * noise_rms) if noise_rms > 0 else float('inf'),
            "sigma_required": sigma_required,
            "ber_actual": ber_actual,
            "ber_target_met": ber_actual <= ber_target,
        }
    
    def ternary_noise_sensitivity(self,
                                  vdd: float = 1.0,
                                  noise_rms: float = 0.01) -> Dict:
        """
        Analyze noise sensitivity of ternary logic levels.
        
        Ternary levels: 0, VDD/2, VDD
        """
        levels = [0, vdd/2, vdd]
        thresholds = [vdd/4, 3*vdd/4]
        
        results = {}
        
        for i, level in enumerate(levels):
            # Distance to nearest threshold
            if i == 0:
                dist = thresholds[0] - level
            elif i == len(levels) - 1:
                dist = level - thresholds[-1]
            else:
                dist = min(level - thresholds[0], thresholds[1] - level)
            
            # Noise margin
            nm = dist - 3 * noise_rms  # 3σ margin
            
            # Error probability
            p_error = norm.cdf(-dist / noise_rms) if noise_rms > 0 else 0
            
            results[f"level_{i}"] = {
                "voltage": level,
                "distance_to_threshold": dist,
                "noise_margin": nm,
                "error_probability": 2 * p_error,  # Two directions
            }
        
        return results


class StatisticalMechanicsSimulation:
    """
    Statistical mechanics simulation for neural network dynamics.
    
    Models:
    - Weight distribution effects on energy landscape
    - Spin glass models for ternary weights
    - Phase transitions in network behavior
    - Thermodynamic limits on computation
    """
    
    def __init__(self, n_weights: int = 1000):
        self.n_weights = n_weights
    
    def ternary_weight_distribution(self,
                                     p_minus: float = 0.25,
                                     p_zero: float = 0.50,
                                     p_plus: float = 0.25) -> np.ndarray:
        """
        Generate ternary weight distribution.
        
        Typical BitNet distribution: ~25% -1, ~50% 0, ~25% +1
        """
        weights = np.random.choice([-1, 0, 1], size=self.n_weights, 
                                   p=[p_minus, p_zero, p_plus])
        return weights
    
    def ising_energy(self,
                     weights: np.ndarray,
                     inputs: np.ndarray,
                     J: float = 1.0) -> float:
        """
        Calculate Ising-like energy for weight-input interaction.
        
        E = -J × Σ w_i × x_i
        """
        return -J * np.sum(weights * inputs)
    
    def energy_landscape(self,
                         weights: np.ndarray,
                         n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate energy landscape for random inputs.
        """
        energies = []
        
        for _ in range(n_samples):
            inputs = np.random.choice([-1, 1], size=len(weights))
            e = self.ising_energy(weights, inputs)
            energies.append(e)
        
        energies = np.array(energies)
        
        # Histogram
        hist, edges = np.histogram(energies, bins=50, density=True)
        centers = (edges[:-1] + edges[1:]) / 2
        
        return centers, hist
    
    def spin_glass_order_parameter(self,
                                   weights: np.ndarray,
                                   n_replicas: int = 100) -> float:
        """
        Calculate Edwards-Anderson order parameter.
        
        q = ⟨s_i × s_i'⟩ where s and s' are replicas.
        
        q = 0: paramagnetic (disordered)
        q = 1: ferromagnetic (ordered)
        0 < q < 1: spin glass
        """
        overlaps = []
        
        for _ in range(n_replicas):
            # Two replicas
            s1 = np.random.choice([-1, 1], size=len(weights))
            s2 = np.random.choice([-1, 1], size=len(weights))
            
            # Overlap
            q = np.mean(s1 * s2)
            overlaps.append(q)
        
        return np.mean(overlaps)
    
    def thermodynamic_computation_limit(self,
                                         temperature: float = 300.0,
                                         operations: int = 1) -> Dict:
        """
        Calculate thermodynamic limits on computation.
        
        Landauer's principle: E_min = k_B × T × ln(2) per bit erased
        """
        e_landauer = K_B * temperature * np.log(2)  # J per bit
        
        return {
            "landauer_energy_j": e_landauer,
            "landauer_energy_ev": e_landauer / Q_E,
            "landauer_power_at_1ghz": e_landauer * 1e9,  # W
            "minimum_energy_per_operation": e_landauer * operations,
            "comparison_to_cmos": 1e-15 / e_landauer,  # CMOS is ~1fJ/op
        }
    
    def phase_diagram_data(self,
                           temperature_range: np.ndarray,
                           coupling_range: np.ndarray) -> np.ndarray:
        """
        Generate phase diagram for weight network.
        
        Axes: Temperature vs Coupling strength
        Regions: Paramagnetic, Ferromagnetic, Spin glass
        """
        T, J = np.meshgrid(temperature_range, coupling_range)
        
        # Simplified phase boundaries
        # T_c ~ J (mean field)
        # Spin glass: T < J, q < 1
        
        order_param = np.zeros_like(T)
        
        for i in range(T.shape[0]):
            for j in range(T.shape[1]):
                t = T[i, j]
                j_val = J[i, j]
                
                if t > 2 * j_val:
                    # Paramagnetic
                    order_param[i, j] = 0
                elif t < j_val / 2:
                    # Ferromagnetic
                    order_param[i, j] = 1
                else:
                    # Spin glass
                    order_param[i, j] = 0.5 * (1 - t / (2 * j_val))
        
        return order_param


class MaterialsScienceSimulation:
    """
    Materials science simulation for metal interconnect properties.
    
    Models:
    - Electromigration
    - Stress migration
    - Temperature coefficient of resistance
    - Mean time to failure
    """
    
    def __init__(self, process: ProcessParams28nm = None):
        self.process = process or ProcessParams28nm()
    
    def temperature_coefficient_resistance(self,
                                           t_ref: float = 300.0,
                                           alpha_cu: float = 0.00393) -> callable:
        """
        Calculate temperature-dependent resistivity.
        
        ρ(T) = ρ₀ × [1 + α × (T - T₀)]
        """
        def resistivity(t: float) -> float:
            return self.process.rho_cu * (1 + alpha_cu * (t - t_ref))
        
        return resistivity
    
    def electromigration_mttf(self,
                              current_density: float,  # A/cm²
                              temperature: float = 350.0,  # K
                              activation_energy: float = 0.7,  # eV (Cu)
                              width: float = 100e-9) -> float:
        """
        Calculate mean time to failure due to electromigration.
        
        Black's equation: MTTF = A × (J^-n) × exp(E_a / k_B T)
        
        Typical J_max for Cu: 1-5 × 10^6 A/cm²
        """
        A = 1e5  # Empirical constant (arbitrary units)
        n = 2  # Current density exponent
        
        # Width-dependent scaling (Blech effect)
        if width < 100e-9:
            # Short line effect - threshold current
            j_threshold = 1e5  # A/cm²
            effective_j = max(0, current_density - j_threshold)
        else:
            effective_j = current_density
        
        if effective_j <= 0:
            return float('inf')  # No EM for short lines
        
        mttf = A * (effective_j**(-n)) * np.exp(activation_energy * Q_E / (K_B * temperature))
        
        return mttf  # hours
    
    def stress_migration_mttf(self,
                              temperature: float = 350.0,
                              thermal_cycles: int = 1000) -> float:
        """
        Calculate mean time to failure due to stress migration.
        
        Related to thermal cycling and CTE mismatch.
        """
        # CTE mismatch stress
        cte_si = 2.6e-6  # /K
        cte_cu = 16.5e-6  # /K
        delta_t = temperature - 300  # K
        
        strain = abs(cte_cu - cte_si) * delta_t
        
        # Stress (simplified)
        E_cu = 120e9  # Pa
        stress = E_cu * strain
        
        # Fatigue limit
        stress_limit = 200e6  # Pa
        
        if stress < stress_limit:
            return float('inf')
        
        # Cycles to failure (Basquin equation approximation)
        mttf_cycles = 1e6 * (stress_limit / stress)**4
        
        return mttf_cycles / thermal_cycles  # years


def run_all_simulations(output_dir: str = ".") -> Dict:
    """Run all scientific simulations and save results."""
    
    results = {}
    
    print("=" * 60)
    print("MASK-LOCKED INFERENCE CHIP - SCIENTIFIC SIMULATION SUITE")
    print("=" * 60)
    
    # 1. Thermal Physics
    print("\n[1/6] Running Thermal Physics Simulations...")
    thermal = ThermalPhysicsSimulation()
    
    results["thermal"] = {
        "thermal_resistance": thermal.thermal_resistance_network(),
        "steady_state_temp": thermal.steady_state_temperature(power_total=3.0),
        "power_map": thermal.power_density_map().tolist(),
    }
    print(f"   Thermal resistance: {results['thermal']['thermal_resistance']['r_total']:.2f} K/W")
    print(f"   Steady-state temp: {results['thermal']['steady_state_temp']:.2f} K")
    
    # 2. Circuit Physics
    print("\n[2/6] Running Circuit Physics Simulations...")
    circuit = CircuitPhysicsSimulation()
    
    results["circuit"] = {
        "rau_energy": circuit.rau_energy_per_operation(),
        "wire_delay_1mm": circuit.wire_delay_rc(1e-3),
    }
    print(f"   RAU energy/op: {results['circuit']['rau_energy']['e_total_rau']*1e15:.2f} fJ")
    print(f"   RAU vs MAC savings: {results['circuit']['rau_energy']['savings_ratio']:.1f}x")
    
    # 3. Electromagnetic
    print("\n[3/6] Running Electromagnetic Simulations...")
    em = ElectromagneticSimulation()
    
    freq = np.logspace(3, 10, 100)
    results["em"] = {
        "freq_hz": freq.tolist(),
        "pdn_impedance": em.pdn_impedance(freq).tolist(),
        "crosstalk_1mm": em.crosstalk_coefficient(1e-3, 1e-3),
        "ssn_32_drivers": em.simultaneous_switching_noise(32),
    }
    print(f"   Crosstalk coefficient: {results['em']['crosstalk_1mm']:.4f}")
    print(f"   SSN (32 drivers): {results['em']['ssn_32_drivers']*1e3:.2f} mV")
    
    # 4. Quantum Noise
    print("\n[4/6] Running Quantum Noise Simulations...")
    noise = QuantumNoiseSimulation(temperature=350)
    
    results["noise"] = {
        "thermal_noise_1k": noise.thermal_noise_voltage(1000, 1e9),
        "shot_noise_1ma": noise.shot_noise_current(1e-3, 1e9),
        "ternary_sensitivity": noise.ternary_noise_sensitivity(vdd=1.0, noise_rms=0.02),
    }
    print(f"   Thermal noise (1kΩ, 1GHz): {results['noise']['thermal_noise_1k']*1e6:.2f} μV")
    print(f"   Shot noise (1mA, 1GHz): {results['noise']['shot_noise_1ma']*1e9:.2f} nA")
    
    # 5. Statistical Mechanics
    print("\n[5/6] Running Statistical Mechanics Simulations...")
    stat_mech = StatisticalMechanicsSimulation(n_weights=1000)
    
    weights = stat_mech.ternary_weight_distribution()
    centers, hist = stat_mech.energy_landscape(weights)
    
    results["stat_mech"] = {
        "thermo_limit": stat_mech.thermodynamic_computation_limit(),
        "spin_glass_order": stat_mech.spin_glass_order_parameter(weights),
        "energy_landscape": {"centers": centers.tolist(), "density": hist.tolist()},
    }
    print(f"   Landauer limit: {results['stat_mech']['thermo_limit']['landauer_energy_ev']*1e3:.3f} meV/bit")
    
    # 6. Materials Science
    print("\n[6/6] Running Materials Science Simulations...")
    materials = MaterialsScienceSimulation()
    
    results["materials"] = {
        "em_mttf_1e6": materials.electromigration_mttf(1e6),
        "em_mttf_5e6": materials.electromigration_mttf(5e6),
    }
    print(f"   EM MTTF (1e6 A/cm²): {results['materials']['em_mttf_1e6']:.0f} hours")
    print(f"   EM MTTF (5e6 A/cm²): {results['materials']['em_mttf_5e6']:.0f} hours")
    
    # Summary
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    results = run_all_simulations()
    
    # Save results
    with open("scientific_simulation_results.json", "w") as f:
        # Convert any non-serializable types
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, complex):
                return {"real": obj.real, "imag": obj.imag}
            elif obj == float('inf'):
                return "infinity"
            return obj
        
        json.dump(results, f, default=convert, indent=2)
    
    print("\nResults saved to scientific_simulation_results.json")
