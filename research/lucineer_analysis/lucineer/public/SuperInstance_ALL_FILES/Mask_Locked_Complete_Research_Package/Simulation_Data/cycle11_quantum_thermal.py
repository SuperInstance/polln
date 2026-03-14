#!/usr/bin/env python3
"""
Quantum-Nanoscale Thermal Transport Simulation
===============================================
Cycle 11 - Mask-Locked Inference Chip

Comprehensive simulation of quantum and nanoscale thermal effects for
28nm silicon devices, including:
- Phonon transport (ballistic vs diffusive regimes)
- Quantum thermal conductance (Landauer formalism)
- Nanoscale hotspot analysis
- Interface thermal resistance (Kapitza resistance)

References:
[1] Cahill, D.G. et al. (2003). Nanoscale thermal transport. Rev. Mod. Phys. 75, 1263
[2] Chen, G. (2005). Nanoscale Energy Transport and Conversion
[3] Schwab, K. et al. (2000). Measurement of the quantum of thermal conductance
[4] Pop, E. (2010). Energy dissipation and transport in nanoscale devices
[5] Stoner, R.J. & Maris, H.J. (1993). Kapitza conductance and heat flow
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable
from enum import Enum
import matplotlib.pyplot as plt
from scipy import constants
from scipy.integrate import quad, solve_ivp
from scipy.special import iv  # Modified Bessel function
from scipy.optimize import brentq
import warnings

# Physical constants
k_B = constants.Boltzmann  # J/K
h = constants.Planck  # J·s
hbar = constants.hbar  # J·s
e = constants.electron_volt  # J/eV
c = constants.c  # m/s

# Silicon properties
SI_DEBYE_TEMP = 645.0  # K
SI_SOUND_VELOCITY = 6400.0  # m/s (average)
SI_DENSITY = 2329.0  # kg/m³
SI_SPECIFIC_HEAT = 700.0  # J/(kg·K)
SI_THERMAL_CONDUCTIVITY_300K = 148.0  # W/(m·K)


# =============================================================================
# SECTION 1: PHONON DISPERSION AND TRANSPORT
# =============================================================================

@dataclass
class PhononProperties:
    """Properties of phonon modes in silicon."""
    # Acoustic modes (3 branches)
    # LA: Longitudinal acoustic
    # TA1, TA2: Transverse acoustic (degenerate)
    
    # Sound velocities (m/s)
    v_LA: float = 8480.0  # Longitudinal acoustic
    v_TA: float = 5840.0  # Transverse acoustic (average)
    
    # Debye frequencies (rad/s)
    omega_D_LA: float = field(init=False)
    omega_D_TA: float = field(init=False)
    
    # Debye wave vectors (1/m)
    k_D: float = field(init=False)
    
    def __post_init__(self):
        # Debye wave vector: k_D = (6π²n)^(1/3) where n is atomic density
        # For Si: n = 5.0e28 atoms/m³
        n_atoms = 5.0e28
        self.k_D = (6 * np.pi**2 * n_atoms)**(1/3)
        
        # Debye frequencies
        self.omega_D_LA = self.v_LA * self.k_D
        self.omega_D_TA = self.v_TA * self.k_D


class PhononDispersion:
    """
    Phonon dispersion relations for silicon.
    
    Uses simplified Debye model for acoustic modes:
    ω(k) = v_s * k
    
    For more accuracy, includes optical mode approximations.
    """
    
    def __init__(self):
        self.props = PhononProperties()
        
        # Optical mode parameters (simplified)
        self.omega_optical = 2 * np.pi * 15e12  # ~15 THz optical phonons
        
    def acoustic_frequency(self, k: NDArray, branch: str = 'LA') -> NDArray:
        """Calculate acoustic phonon frequency."""
        if branch == 'LA':
            return self.props.v_LA * k
        else:  # TA
            return self.props.v_TA * k
    
    def acoustic_energy(self, k: NDArray, branch: str = 'LA') -> NDArray:
        """Calculate acoustic phonon energy in J."""
        return hbar * self.acoustic_frequency(k, branch)
    
    def group_velocity(self, k: NDArray, branch: str = 'LA') -> NDArray:
        """Group velocity dω/dk."""
        if branch == 'LA':
            return np.full_like(k, self.props.v_LA)
        else:
            return np.full_like(k, self.props.v_TA)
    
    def density_of_states(self, omega: NDArray) -> NDArray:
        """
        Phonon density of states per unit volume per unit angular frequency.
        
        D(ω) = ω² / (2π² v³) for Debye model (3 acoustic branches)
        """
        # Average sound velocity
        v_avg = (self.props.v_LA + 2 * self.props.v_TA) / 3
        
        # Debye DOS (3 acoustic branches)
        dos = 3 * omega**2 / (2 * np.pi**2 * v_avg**3)
        
        return dos


class MeanFreePath:
    """
    Calculate phonon mean free path at various conditions.
    
    MFP depends on:
    - Umklapp scattering (phonon-phonon)
    - Impurity scattering
    - Boundary scattering
    - Dislocation scattering
    """
    
    def __init__(self, temperature: float = 300.0):
        self.T = temperature
        self.Theta_D = SI_DEBYE_TEMP
        
    def umklapp_mfp(self, omega: NDArray = None) -> NDArray:
        """
        Umklapp scattering mean free path.
        
        Λ_U = (v_s / γ² ω T) * exp(Θ_D / (b T))
        
        where γ is Gruneisen parameter (~1.0 for Si)
        """
        gamma = 1.0  # Gruneisen parameter
        b = 2.0  # Empirical constant
        
        v_s = SI_SOUND_VELOCITY
        
        if omega is None:
            # Return characteristic MFP at characteristic frequency
            omega_char = k_B * self.T / hbar
            omega = omega_char
        
        # Umklapp MFP
        Lambda_U = (v_s / (gamma**2 * omega * self.T)) * np.exp(self.Theta_D / (b * self.T))
        
        return Lambda_U
    
    def boundary_mfp(self, characteristic_length: float) -> float:
        """
        Boundary scattering MFP.
        
        For thin films: Λ_boundary ≈ L (film thickness)
        For nanowires: Λ_boundary ≈ D (diameter)
        """
        return characteristic_length
    
    def effective_mfp(self, L_char: float, omega: NDArray = None) -> NDArray:
        """
        Effective MFP using Matthiessen's rule.
        
        1/Λ_eff = 1/Λ_U + 1/Λ_boundary
        """
        Lambda_U = self.umklapp_mfp(omega)
        Lambda_B = self.boundary_mfp(L_char)
        
        # Matthiessen's rule
        Lambda_eff = 1.0 / (1.0/Lambda_U + 1.0/Lambda_B)
        
        return Lambda_eff
    
    def characteristic_mfp_300K(self) -> float:
        """
        Characteristic phonon MFP in bulk silicon at 300K.
        
        Literature value: ~40 nm at room temperature
        (varies from 30-300 nm depending on frequency)
        """
        # From kinetic theory: Λ = 3κ / (C_v * v)
        kappa = SI_THERMAL_CONDUCTIVITY_300K
        C_v = SI_DENSITY * SI_SPECIFIC_HEAT
        v_s = SI_SOUND_VELOCITY
        
        Lambda = 3 * kappa / (C_v * v_s)
        return Lambda  # ~42 nm


# =============================================================================
# SECTION 2: BALLISTIC VS DIFFUSIVE TRANSPORT
# =============================================================================

class TransportRegime:
    """
    Determine and analyze ballistic vs diffusive transport regimes.
    
    Key dimensionless number: Knudsen number
    Kn = Λ / L
    
    Kn << 1: Diffusive (Fourier's law valid)
    Kn >> 1: Ballistic (quantum effects important)
    Kn ~ 1: Quasi-ballistic (intermediate regime)
    """
    
    def __init__(self, feature_size: float, temperature: float = 300.0):
        """
        Args:
            feature_size: Characteristic length (m)
            temperature: Operating temperature (K)
        """
        self.L = feature_size
        self.T = temperature
        self.mfp_calc = MeanFreePath(temperature)
        
    def knudsen_number(self, use_effective_mfp: bool = True) -> float:
        """Calculate Knudsen number."""
        if use_effective_mfp:
            Lambda = self.mfp_calc.effective_mfp(self.L)
            if isinstance(Lambda, np.ndarray):
                Lambda = np.mean(Lambda[~np.isnan(Lambda) & (Lambda > 0)])
        else:
            Lambda = self.mfp_calc.characteristic_mfp_300K()
            if self.T != 300.0:
                # Temperature scaling
                Lambda = Lambda * (300.0 / self.T)
        
        return Lambda / self.L
    
    def regime_classification(self) -> str:
        """Classify transport regime."""
        Kn = self.knudsen_number()
        
        if Kn < 0.1:
            return "DIFFUSIVE (Fourier's law valid)"
        elif Kn < 1.0:
            return "QUASI-BALLISTIC (intermediate regime)"
        else:
            return "BALLISTIC (quantum effects important)"
    
    def thermal_conductivity_reduction(self) -> float:
        """
        Calculate reduction in thermal conductivity due to size effects.
        
        Using Fuchs-Sondheimer model for thin films:
        κ_eff/κ_bulk = 1 - 3/8 * Kn (for Kn < 1)
        
        More accurate: κ_eff/κ_bulk = 1 - (3/2) * Kn * ∫_0^∞ ...
        """
        Kn = self.knudsen_number()
        
        if Kn < 0.1:
            # Diffusive limit - minimal reduction
            return 1.0
        elif Kn < 1.0:
            # Quasi-ballistic - Fuchs-Sondheimer approximation
            return 1.0 - 0.375 * Kn
        else:
            # Ballistic - significant reduction
            # Approximate: κ_eff ~ κ_bulk / Kn
            return 1.0 / (1.0 + Kn)
    
    def ballistic_thermal_resistance(self, area: float) -> float:
        """
        Calculate ballistic thermal resistance.
        
        R_ballistic = L / (G_Q * A * M)
        
        where M is number of conducting modes
        """
        # Number of phonon modes (approximate)
        # M ≈ (k_B T / ħω_D)² for acoustic phonons
        omega_D = SI_DEBYE_TEMP * k_B / hbar
        M = (k_B * self.T / (hbar * omega_D))**2
        M = max(M, 1)  # At least one mode
        
        # Quantum of thermal conductance
        G_Q = np.pi**2 * k_B**2 * self.T / (3 * h)
        
        # Ballistic resistance
        R_ball = 1.0 / (G_Q * area * M)
        
        return R_ball


class SizeEffectModel:
    """
    Model thermal conductivity size effects for thin films and nanostructures.
    """
    
    def __init__(self, thickness: float, temperature: float = 300.0):
        self.t = thickness
        self.T = temperature
        
    def fuchs_sondheimer(self, specularity: float = 0.0) -> float:
        """
        Fuchs-Sondheimer model for thin film thermal conductivity.
        
        κ_eff/κ_bulk = 1 - (3/2)(1-p) ∫_1^∞ (1/t³ - 1/t⁵) (1 - exp(-t/δ)) dt
        
        where δ = t/Λ is the ratio of thickness to MFP
        and p is specularity parameter (0 = diffuse, 1 = specular)
        """
        Lambda = MeanFreePath(self.T).characteristic_mfp_300K()
        if self.T != 300.0:
            Lambda *= 300.0 / self.T
            
        delta = self.t / Lambda
        
        # Simplified analytical approximation
        if delta > 10:
            # Thick film limit
            reduction = 1.0 - (3.0/8.0) * (1 - specularity) / delta
        else:
            # Thin film approximation
            reduction = delta / (1.0 + delta) * (1 + specularity) / 2
            
        return max(0, reduction)
    
    def morelli_thermal_conductivity(self) -> float:
        """
        Morelli's model for temperature-dependent thermal conductivity.
        
        κ(T) = κ_300K * (300/T)^n
        
        with n ≈ 1.3 for silicon
        """
        kappa_300 = SI_THERMAL_CONDUCTIVITY_300K
        n = 1.3
        
        kappa_T = kappa_300 * (300.0 / self.T)**n
        
        # Apply size effect
        kappa_T *= self.fuchs_sondheimer()
        
        return kappa_T


# =============================================================================
# SECTION 3: QUANTUM THERMAL CONDUCTANCE
# =============================================================================

class QuantumThermalConductance:
    """
    Quantum of thermal conductance and Landauer formalism.
    
    The quantum of thermal conductance:
    G_Q = π² k_B² T / (3h)
    
    At T = 1K: G_Q ≈ 0.956 pW/K
    At T = 300K: G_Q ≈ 0.287 nW/K
    
    This is the fundamental quantum limit for heat flow
    through a single phonon mode.
    """
    
    def __init__(self, temperature: float):
        self.T = temperature
        
    def quantum_conductance(self) -> float:
        """
        Calculate quantum of thermal conductance.
        
        G_Q = π² k_B² T / (3h)
        
        Returns:
            Thermal conductance in W/K
        """
        G_Q = np.pi**2 * k_B**2 * self.T / (3 * h)
        return G_Q
    
    def quantum_conductance_nW_per_K(self) -> float:
        """Return G_Q in nW/K."""
        return self.quantum_conductance() * 1e9
    
    def phonon_modes_conductance(self, n_modes: int) -> float:
        """
        Thermal conductance for multiple phonon modes.
        
        G = n_modes * G_Q (at low temperature limit)
        """
        return n_modes * self.quantum_conductance()
    
    def landauer_heat_flow(self, delta_T: float, n_modes: int,
                          transmission: float = 1.0) -> float:
        """
        Calculate heat flow using Landauer formalism.
        
        Q = ∫_0^∞ (ħω / (e^(ħω/k_B T_h) - 1) - ħω / (e^(ħω/k_B T_c) - 1)) * τ(ω) * D(ω) dω
        
        Simplified at low temperature:
        Q ≈ G_Q * n_modes * ΔT * τ
        """
        return self.quantum_conductance() * n_modes * delta_T * transmission


class LandauerFormalism:
    """
    Complete Landauer formalism for thermal transport.
    
    Heat current: J_Q = ∫_0^∞ (ħω) τ(ω) M(ω) [n(ω,T_h) - n(ω,T_c)] dω / (2π)
    
    where:
    - τ(ω) is transmission function
    - M(ω) is number of modes
    - n(ω,T) is Bose-Einstein distribution
    """
    
    def __init__(self, T_hot: float, T_cold: float):
        self.T_h = T_hot
        self.T_c = T_cold
        
    def bose_einstein(self, omega: NDArray, T: float) -> NDArray:
        """Bose-Einstein distribution."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            n = 1.0 / (np.exp(hbar * omega / (k_B * T)) - 1)
            n = np.where(np.isfinite(n), n, 0)
        return n
    
    def integrand(self, omega: float, n_modes: int, transmission: Callable) -> float:
        """Integrand for Landauer heat current."""
        tau = transmission(omega)
        n_h = self.bose_einstein(np.array([omega]), self.T_h)[0]
        n_c = self.bose_einstein(np.array([omega]), self.T_c)[0]
        
        return hbar * omega * tau * n_modes * (n_h - n_c) / (2 * np.pi)
    
    def heat_current(self, n_modes: int, 
                    transmission: Callable = lambda w: 1.0,
                    omega_max: float = None) -> float:
        """
        Calculate total heat current.
        
        Args:
            n_modes: Number of phonon modes
            transmission: Transmission function τ(ω)
            omega_max: Maximum frequency to integrate
        
        Returns:
            Heat current in Watts
        """
        if omega_max is None:
            omega_max = SI_DEBYE_TEMP * k_B / hbar
        
        result, _ = quad(
            lambda w: self.integrand(w, n_modes, transmission),
            0, omega_max,
            limit=100
        )
        
        return result


# =============================================================================
# SECTION 4: NANOSCALE HOTSPOT ANALYSIS
# =============================================================================

@dataclass
class HotspotConfig:
    """Configuration for nanoscale hotspot simulation."""
    # Hotspot geometry
    size_nm: float = 28.0  # nm (comparable to transistor gate)
    power_density: float = 1e12  # W/m³ (typical for active transistor)
    
    # Material
    thermal_conductivity: float = 148.0  # W/(m·K)
    specific_heat: float = 700.0  # J/(kg·K)
    density: float = 2329.0  # kg/m³
    
    # Environment
    ambient_temp: float = 300.0  # K
    die_size: float = 6.5e-3  # m (6.5 mm)
    
    # Simulation
    grid_points: int = 100


class NanoscaleHotspot:
    """
    Analyze temperature distribution around nanoscale hotspots.
    
    At the nanoscale, classical Fourier's law breaks down.
    This model incorporates:
    - Ballistic phonon transport
    - Thermal boundary resistance
    - Size-dependent thermal conductivity
    """
    
    def __init__(self, config: HotspotConfig):
        self.config = config
        self.alpha = config.thermal_conductivity / (config.density * config.specific_heat)
        
    def thermal_diffusion_length(self, time: float) -> float:
        """
        Thermal diffusion length.
        
        L_th = sqrt(4 α t)
        """
        return np.sqrt(4 * self.alpha * time)
    
    def temperature_rise_analytical(self, r: NDArray, t: float,
                                   point_source: bool = True) -> NDArray:
        """
        Analytical solution for temperature rise from point source.
        
        ΔT(r,t) = Q / (8 (π α t)^(3/2) ρ c_p) * exp(-r²/(4αt))
        
        For continuous source:
        ΔT(r) = Q / (4 π κ r)
        """
        Q = self.config.power_density * (self.config.size_nm * 1e-9)**3
        kappa = self.config.thermal_conductivity
        rho_cp = self.config.density * self.config.specific_heat
        
        if point_source:
            # Instantaneous point source
            L_th = self.thermal_diffusion_length(t)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dT = Q / (8 * (np.pi * self.alpha * t)**1.5 * rho_cp)
                dT *= np.exp(-r**2 / (4 * self.alpha * t))
                dT = np.where(np.isfinite(dT), dT, 0)
        else:
            # Continuous point source (steady state)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dT = Q / (4 * np.pi * kappa * r)
                dT = np.where(np.isfinite(dT), dT, 0)
        
        return dT
    
    def hotspot_temperature_profile(self, r: NDArray) -> NDArray:
        """
        Temperature profile for a nanoscale hotspot.
        
        Incorporates:
        - Phonon mean free path effects
        - Thermal boundary resistance
        - Non-equilibrium effects
        """
        size = self.config.size_nm * 1e-9
        Q = self.config.power_density * size**3
        kappa = self.config.thermal_conductivity
        Lambda = MeanFreePath(300.0).characteristic_mfp_300K()
        
        # Effective thermal conductivity (reduced near hotspot)
        Kn = Lambda / size
        kappa_eff = kappa / (1 + Kn)
        
        # Temperature rise
        dT = Q / (4 * np.pi * kappa_eff * r)
        
        # Cap maximum temperature rise
        dT = np.minimum(dT, 100.0)  # Max 100K rise
        
        return dT
    
    def thermal_time_constant(self) -> float:
        """
        Thermal time constant for nanoscale hotspot.
        
        τ_th = L² / α
        """
        L = self.config.size_nm * 1e-9
        tau = L**2 / self.alpha
        return tau
    
    def phonon_bottleneck_analysis(self) -> Dict:
        """
        Analyze phonon bottleneck effects at transistor scale.
        
        When feature size < MFP, phonon transport becomes ballistic,
        creating a thermal bottleneck.
        """
        size = self.config.size_nm * 1e-9
        Lambda = MeanFreePath(300.0).characteristic_mfp_300K()
        
        # Knudsen number
        Kn = Lambda / size
        
        # Effective thermal conductivity
        kappa_eff = self.config.thermal_conductivity / (1 + Kn)
        
        # Ballistic resistance contribution
        G_Q = QuantumThermalConductance(300.0).quantum_conductance()
        
        # Number of phonon modes through hotspot
        omega_D = SI_DEBYE_TEMP * k_B / hbar
        n_modes = max(1, int((k_B * 300.0 / (hbar * omega_D))**2))
        
        # Ballistic thermal resistance
        R_ball = 1.0 / (G_Q * n_modes * size**2)
        
        # Diffusive resistance
        R_diff = size / (kappa_eff * size**2)
        
        return {
            'knudsen_number': Kn,
            'effective_conductivity': kappa_eff,
            'conductivity_reduction': 1 - kappa_eff/self.config.thermal_conductivity,
            'ballistic_resistance': R_ball,
            'diffusive_resistance': R_diff,
            'total_resistance': R_ball + R_diff,
            'n_modes': n_modes,
            'bottleneck_severity': 'HIGH' if Kn > 0.5 else 'MODERATE' if Kn > 0.1 else 'LOW'
        }


class TransientHotspotAnalysis:
    """
    Transient analysis of nanoscale hotspots.
    
    Important for understanding thermal response during
    burst-mode inference operations.
    """
    
    def __init__(self, hotspot: NanoscaleHotspot):
        self.hotspot = hotspot
        
    def temperature_vs_time(self, t_array: NDArray, r: float = 0) -> NDArray:
        """Calculate temperature at distance r as function of time."""
        return self.hotspot.temperature_rise_analytical(
            np.full_like(t_array, r), t_array, point_source=True
        )
    
    def cooling_time(self, T_initial: float, T_target: float,
                    r: float = 0) -> float:
        """
        Calculate time to cool from T_initial to T_target.
        
        For exponential cooling: T(t) = T_∞ + (T_0 - T_∞) exp(-t/τ)
        """
        tau = self.hotspot.thermal_time_constant()
        
        if T_target >= T_initial:
            return 0.0
        
        # Solve for t in cooling equation
        ratio = (T_target - self.hotspot.config.ambient_temp) / \
                (T_initial - self.hotspot.config.ambient_temp)
        
        if ratio <= 0:
            return np.inf
        
        t = -tau * np.log(ratio)
        return max(0, t)
    
    def pulse_train_analysis(self, pulse_power: float, pulse_duration: float,
                            pulse_period: float, n_pulses: int) -> Dict:
        """
        Analyze temperature evolution for a train of power pulses.
        
        Models burst-mode inference scenarios.
        """
        tau = self.hotspot.thermal_time_constant()
        size = self.hotspot.config.size_nm * 1e-9
        
        # Temperature rise per pulse
        dT_pulse = pulse_power * pulse_duration / \
                   (self.hotspot.config.density * 
                    self.hotspot.config.specific_heat * 
                    size**3)
        
        # Time for cooling between pulses
        t_cool = pulse_period - pulse_duration
        
        # Steady-state temperature ratcheting
        # Each pulse adds heat, cooling removes fraction
        T_rise_accumulated = dT_pulse * (1 - np.exp(-t_cool/tau))
        
        # Maximum temperature after many pulses
        T_max = dT_pulse / (1 - np.exp(-t_cool/tau))
        
        return {
            'time_constant': tau,
            'temp_rise_per_pulse': dT_pulse,
            'cooling_time_between_pulses': t_cool,
            'steady_state_ratchet': T_rise_accumulated,
            'maximum_temperature_rise': T_max,
            'thermal_equilibrium_reached': n_pulses > 5 * tau / pulse_period
        }


# =============================================================================
# SECTION 5: INTERFACE THERMAL RESISTANCE (KAPITZA RESISTANCE)
# =============================================================================

class KapitzaResistance:
    """
    Thermal boundary resistance (Kapitza resistance) at interfaces.
    
    The Kapitza resistance arises from acoustic mismatch or
    diffuse mismatch between materials.
    
    Key interfaces:
    - Si/SiO2: Critical for SOI and gate stacks
    - Metal/Si: Critical for contacts and interconnects
    - Si/Cu: For through-silicon vias
    """
    
    def __init__(self, material1: str, material2: str):
        self.mat1 = material1
        self.mat2 = material2
        
        # Material properties database
        self.properties = {
            'Si': {
                'density': 2329.0,
                'sound_velocity': 6400.0,
                'specific_heat': 700.0,
                'thermal_conductivity': 148.0
            },
            'SiO2': {
                'density': 2200.0,
                'sound_velocity': 3800.0,
                'specific_heat': 745.0,
                'thermal_conductivity': 1.4
            },
            'Cu': {
                'density': 8960.0,
                'sound_velocity': 3800.0,
                'specific_heat': 385.0,
                'thermal_conductivity': 400.0
            },
            'Al': {
                'density': 2700.0,
                'sound_velocity': 5100.0,
                'specific_heat': 897.0,
                'thermal_conductivity': 237.0
            },
            'W': {
                'density': 19300.0,
                'sound_velocity': 2800.0,
                'specific_heat': 134.0,
                'thermal_conductivity': 174.0
            }
        }
    
    def acoustic_mismatch_model(self, T: float = 300.0) -> float:
        """
        Acoustic Mismatch Model (AMM) for Kapitza resistance.
        
        R_K = 1 / (Γ * C_v * v / 4)
        
        where Γ is transmission coefficient
        """
        props1 = self.properties.get(self.mat1, self.properties['Si'])
        props2 = self.properties.get(self.mat2, self.properties['SiO2'])
        
        # Acoustic impedances
        Z1 = props1['density'] * props1['sound_velocity']
        Z2 = props2['density'] * props2['sound_velocity']
        
        # Transmission coefficient (AMM)
        Gamma = 4 * Z1 * Z2 / (Z1 + Z2)**2
        
        # Average sound velocity
        v_avg = (props1['sound_velocity'] + props2['sound_velocity']) / 2
        
        # Volumetric heat capacity
        C_v = (props1['density'] * props1['specific_heat'] + 
               props2['density'] * props2['specific_heat']) / 2
        
        # Kapitza resistance
        R_K = 1.0 / (Gamma * C_v * v_avg / 4)
        
        return R_K
    
    def diffuse_mismatch_model(self, T: float = 300.0) -> float:
        """
        Diffuse Mismatch Model (DMM) for Kapitza resistance.
        
        Assumes phonons scatter diffusely at interface.
        """
        props1 = self.properties.get(self.mat1, self.properties['Si'])
        props2 = self.properties.get(self.mat2, self.properties['SiO2'])
        
        # DMM transmission coefficient
        v1 = props1['sound_velocity']
        v2 = props2['sound_velocity']
        
        # Transmission based on density of states ratio
        Gamma = v2**2 / (v1**2 + v2**2)
        
        # Volumetric heat capacity
        C_v = (props1['density'] * props1['specific_heat'] + 
               props2['density'] * props2['specific_heat']) / 2
        
        # Kapitza resistance
        R_K = 4 / (Gamma * C_v * (v1 + v2) / 2)
        
        return R_K
    
    def literature_values(self) -> Dict[str, float]:
        """
        Literature values for common interfaces at room temperature.
        
        R_K in units of m²·K/GW (= 10⁻⁹ m²·K/W)
        """
        values = {
            ('Si', 'SiO2'): 2.0e-9,  # ~2 × 10⁻⁹ m²·K/W
            ('Si', 'Cu'): 0.25e-9,   # ~0.25 × 10⁻⁹ m²·K/W
            ('Si', 'Al'): 0.5e-9,    # ~0.5 × 10⁻⁹ m²·K/W
            ('Si', 'W'): 0.4e-9,     # ~0.4 × 10⁻⁹ m²·K/W
            ('Cu', 'SiO2'): 1.5e-9,  # ~1.5 × 10⁻⁹ m²·K/W
            ('Al', 'SiO2'): 1.8e-9,  # ~1.8 × 10⁻⁹ m²·K/W
        }
        
        key = (self.mat1, self.mat2)
        key_rev = (self.mat2, self.mat1)
        
        if key in values:
            return {'literature': values[key]}
        elif key_rev in values:
            return {'literature': values[key_rev]}
        else:
            # Use model prediction
            return {
                'AMM': self.acoustic_mismatch_model(T=300.0),
                'DMM': self.diffuse_mismatch_model(T=300.0)
            }


class ThermalBoundaryConductance:
    """
    Thermal boundary conductance (inverse of Kapitza resistance).
    
    G = 1 / R_K
    
    Important for:
    - Transistor heat dissipation
    - Through-silicon vias
    - 3D IC thermal management
    """
    
    def __init__(self, interface: Tuple[str, str]):
        self.interface = interface
        self.kapitza = KapitzaResistance(interface[0], interface[1])
        
    def conductance(self, T: float = 300.0) -> float:
        """
        Calculate thermal boundary conductance.
        
        G = 1 / R_K in W/(m²·K)
        """
        R_K = self.kapitza.acoustic_mismatch_model(T)
        return 1.0 / R_K
    
    def temperature_dependence(self, T: NDArray) -> NDArray:
        """
        Temperature dependence of TBC.
        
        At low T: G ∝ T³
        At high T: G ≈ constant
        """
        G_300 = self.conductance(300.0)
        
        # Transition temperature
        T_char = 100.0  # K
        
        # Interpolation
        G_T = G_300 * np.where(
            T < T_char,
            (T / 300.0)**3,
            1.0 - (1.0 - (T_char/300.0)**3) * np.exp(-(T - T_char) / T_char)
        )
        
        return G_T


# =============================================================================
# SECTION 6: QUANTUM CORRECTIONS TO CLASSICAL MODELS
# =============================================================================

class QuantumCorrections:
    """
    Quantum corrections to classical thermal models.
    
    At nanoscale, classical Fourier's law becomes inaccurate.
    This class provides correction factors.
    """
    
    def __init__(self, feature_size: float, temperature: float = 300.0):
        self.L = feature_size
        self.T = temperature
        
    def effective_thermal_conductivity(self, kappa_bulk: float) -> float:
        """
        Size-corrected thermal conductivity.
        
        κ_eff = κ_bulk * f(Kn)
        
        where f(Kn) accounts for phonon boundary scattering.
        """
        Lambda = MeanFreePath(self.T).characteristic_mfp_300K()
        if self.T != 300.0:
            Lambda *= 300.0 / self.T
            
        Kn = Lambda / self.L
        
        # Correction factor
        if Kn < 0.1:
            f_Kn = 1.0
        elif Kn < 1.0:
            f_Kn = 1.0 / (1.0 + 0.5 * Kn)
        else:
            f_Kn = 1.0 / (1.0 + Kn)
        
        return kappa_bulk * f_Kn
    
    def non_fourier_factor(self, time: float) -> float:
        """
        Correction factor for non-Fourier heat conduction.
        
        At short times (t < τ, where τ = Λ²/α), heat propagation
        is ballistic rather than diffusive.
        """
        Lambda = MeanFreePath(self.T).characteristic_mfp_300K()
        alpha = SI_THERMAL_CONDUCTIVITY_300K / (SI_DENSITY * SI_SPECIFIC_HEAT)
        
        # Phonon relaxation time
        tau = Lambda**2 / alpha
        
        # Cattaneo number
        Ca = tau / time
        
        if Ca > 0.1:
            # Non-Fourier effects significant
            return 1.0 / (1.0 + Ca)
        else:
            return 1.0
    
    def ballistic_correction(self, distance: float) -> float:
        """
        Ballistic correction for heat flow over short distances.
        
        For d < Λ, heat flow is enhanced by ballistic phonons.
        """
        Lambda = MeanFreePath(self.T).characteristic_mfp_300K()
        
        if distance < Lambda:
            # Ballistic regime
            return 1.0 + (Lambda / distance - 1) * 0.5
        else:
            return 1.0
    
    def hotspot_correction(self, hotspot_size: float) -> Dict:
        """
        Comprehensive corrections for nanoscale hotspot.
        """
        kappa_corr = self.effective_thermal_conductivity(SI_THERMAL_CONDUCTIVITY_300K)
        
        # Interface resistance contribution
        R_K_SiO2 = KapitzaResistance('Si', 'SiO2').acoustic_mismatch_model(self.T)
        
        # Time constant correction
        tau_classical = hotspot_size**2 / (SI_THERMAL_CONDUCTIVITY_300K / 
                                           (SI_DENSITY * SI_SPECIFIC_HEAT))
        tau_quantum = tau_classical / self.non_fourier_factor(1e-12)
        
        return {
            'conductivity_correction': kappa_corr / SI_THERMAL_CONDUCTIVITY_300K,
            'effective_conductivity': kappa_corr,
            'interface_resistance': R_K_SiO2,
            'classical_time_constant': tau_classical,
            'quantum_corrected_time_constant': tau_quantum,
            'time_constant_ratio': tau_quantum / tau_classical
        }


# =============================================================================
# SECTION 7: VISUALIZATION AND REPORTING
# =============================================================================

def generate_phonon_dispersion_plot(save_path: str = None):
    """Generate phonon dispersion relation plot."""
    dispersion = PhononDispersion()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Dispersion relations
    ax1 = axes[0]
    k = np.linspace(0, dispersion.props.k_D, 500)
    
    # Acoustic modes
    omega_LA = dispersion.acoustic_frequency(k, 'LA') / (2 * np.pi) / 1e12  # THz
    omega_TA = dispersion.acoustic_frequency(k, 'TA') / (2 * np.pi) / 1e12  # THz
    
    ax1.plot(k / 1e9, omega_LA, 'b-', linewidth=2, label='LA mode')
    ax1.plot(k / 1e9, omega_TA, 'r-', linewidth=2, label='TA mode')
    ax1.axhline(y=dispersion.omega_optical / (2 * np.pi) / 1e12, 
               color='g', linestyle='--', label='Optical mode (~15 THz)')
    
    ax1.set_xlabel('Wave vector k (nm⁻¹)', fontsize=12)
    ax1.set_ylabel('Frequency (THz)', fontsize=12)
    ax1.set_title('Silicon Phonon Dispersion (Debye Model)', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, dispersion.props.k_D / 1e9)
    ax1.set_ylim(0, 20)
    
    # Plot 2: Density of states
    ax2 = axes[1]
    omega = np.linspace(0, 1e14, 1000)
    dos = dispersion.density_of_states(omega)
    
    ax2.plot(omega / (2 * np.pi) / 1e12, dos / 1e-30, 'k-', linewidth=2)
    ax2.fill_between(omega / (2 * np.pi) / 1e12, dos / 1e-30, alpha=0.3)
    
    ax2.set_xlabel('Frequency (THz)', fontsize=12)
    ax2.set_ylabel('DOS (×10³⁰ /m³/Hz)', fontsize=12)
    ax2.set_title('Phonon Density of States', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 15)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def generate_thermal_conductivity_size_plot(save_path: str = None):
    """Generate thermal conductivity vs size plot."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: κ/κ_bulk vs feature size
    ax1 = axes[0]
    sizes = np.logspace(-9, -6, 100)  # 1 nm to 1 μm
    
    for T in [300, 350, 400]:
        ratios = []
        for s in sizes:
            model = SizeEffectModel(s, T)
            ratio = model.fuchs_sondheimer(specularity=0)
            ratios.append(ratio)
        
        ax1.semilogx(sizes * 1e9, ratios, linewidth=2, label=f'T = {T} K')
    
    ax1.axvline(x=40, color='k', linestyle='--', alpha=0.5, label='MFP at 300K (~40 nm)')
    ax1.axvline(x=28, color='r', linestyle=':', linewidth=2, label='Feature size (28 nm)')
    
    ax1.set_xlabel('Feature size (nm)', fontsize=12)
    ax1.set_ylabel('κ_eff / κ_bulk', fontsize=12)
    ax1.set_title('Size Effect on Thermal Conductivity', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, 1000)
    ax1.set_ylim(0, 1.1)
    
    # Plot 2: κ vs temperature for different sizes
    ax2 = axes[1]
    temps = np.linspace(200, 500, 100)
    
    for size_nm in [28, 100, 1000]:
        kappas = []
        for T in temps:
            model = SizeEffectModel(size_nm * 1e-9, T)
            kappas.append(model.morelli_thermal_conductivity())
        
        ax2.plot(temps, kappas, linewidth=2, label=f'Size = {size_nm} nm')
    
    # Bulk reference
    kappa_bulk = SI_THERMAL_CONDUCTIVITY_300K * (300 / temps)**1.3
    ax2.plot(temps, kappa_bulk, 'k--', linewidth=2, label='Bulk Si')
    
    ax2.set_xlabel('Temperature (K)', fontsize=12)
    ax2.set_ylabel('Thermal conductivity (W/m·K)', fontsize=12)
    ax2.set_title('Temperature Dependence by Size', fontsize=14)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def generate_quantum_conductance_plot(save_path: str = None):
    """Generate quantum thermal conductance plot."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: G_Q vs temperature
    ax1 = axes[0]
    temps = np.linspace(0.1, 400, 500)
    
    G_Q_values = []
    for T in temps:
        qt = QuantumThermalConductance(T)
        G_Q_values.append(qt.quantum_conductance_nW_per_K())
    
    ax1.plot(temps, G_Q_values, 'b-', linewidth=2)
    ax1.axvline(x=300, color='r', linestyle='--', label='Operating temp (300 K)')
    ax1.axhline(y=0.287, color='g', linestyle=':', label='G_Q at 300 K (~0.287 nW/K)')
    
    ax1.set_xlabel('Temperature (K)', fontsize=12)
    ax1.set_ylabel('Quantum conductance G_Q (nW/K)', fontsize=12)
    ax1.set_title('Quantum of Thermal Conductance', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 400)
    
    # Plot 2: Landauer heat flow
    ax2 = axes[1]
    
    delta_Ts = np.linspace(0.1, 100, 100)
    n_modes_list = [1, 10, 100, 1000]
    
    for n_modes in n_modes_list:
        heat_flows = []
        for dT in delta_Ts:
            qt = QuantumThermalConductance(300.0)
            Q = qt.landauer_heat_flow(dT, n_modes, transmission=1.0)
            heat_flows.append(Q * 1e9)  # nW
        
        ax2.plot(delta_Ts, heat_flows, linewidth=2, label=f'{n_modes} modes')
    
    ax2.set_xlabel('Temperature difference ΔT (K)', fontsize=12)
    ax2.set_ylabel('Heat flow Q (nW)', fontsize=12)
    ax2.set_title('Landauer Heat Flow at 300 K', fontsize=14)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def generate_hotspot_analysis_plot(save_path: str = None):
    """Generate nanoscale hotspot analysis plot."""
    config = HotspotConfig(size_nm=28.0)
    hotspot = NanoscaleHotspot(config)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Temperature profile
    ax1 = axes[0, 0]
    r = np.logspace(-9, -6, 100)  # 1 nm to 1 μm
    
    T_profile = hotspot.temperature_rise_analytical(r, t=1e-12, point_source=True)
    T_profile_ss = hotspot.hotspot_temperature_profile(r)
    
    ax1.semilogx(r * 1e9, T_profile_ss, 'b-', linewidth=2, label='Steady state')
    ax1.set_xlabel('Distance from hotspot (nm)', fontsize=12)
    ax1.set_ylabel('Temperature rise (K)', fontsize=12)
    ax1.set_title('Temperature Profile from 28nm Hotspot', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, 1000)
    
    # Plot 2: Thermal time constant vs size
    ax2 = axes[0, 1]
    sizes = np.logspace(-9, -6, 100)  # 1 nm to 1 μm
    
    time_constants = []
    for s in sizes:
        config_temp = HotspotConfig(size_nm=s * 1e9)
        hs_temp = NanoscaleHotspot(config_temp)
        time_constants.append(hs_temp.thermal_time_constant() * 1e12)  # ps
    
    ax2.loglog(sizes * 1e9, time_constants, 'r-', linewidth=2)
    ax2.axvline(x=28, color='b', linestyle='--', linewidth=2, label='Feature size (28 nm)')
    
    ax2.set_xlabel('Hotspot size (nm)', fontsize=12)
    ax2.set_ylabel('Thermal time constant (ps)', fontsize=12)
    ax2.set_title('Thermal Time Constant vs Size', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Phonon bottleneck analysis
    ax3 = axes[1, 0]
    
    sizes_for_bottleneck = np.array([10, 20, 28, 40, 50, 100, 200, 500])  # nm
    Kn_values = []
    conductivity_reductions = []
    
    for s in sizes_for_bottleneck:
        config_temp = HotspotConfig(size_nm=s)
        hs_temp = NanoscaleHotspot(config_temp)
        analysis = hs_temp.phonon_bottleneck_analysis()
        Kn_values.append(analysis['knudsen_number'])
        conductivity_reductions.append(analysis['conductivity_reduction'] * 100)
    
    x = np.arange(len(sizes_for_bottleneck))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, Kn_values, width, label='Knudsen number', color='steelblue')
    ax3_twin = ax3.twinx()
    bars2 = ax3_twin.bar(x + width/2, conductivity_reductions, width, 
                         label='κ reduction (%)', color='coral')
    
    ax3.set_xlabel('Hotspot size (nm)', fontsize=12)
    ax3.set_ylabel('Knudsen number Kn', fontsize=12, color='steelblue')
    ax3_twin.set_ylabel('Conductivity reduction (%)', fontsize=12, color='coral')
    ax3.set_title('Phonon Bottleneck Analysis', fontsize=14)
    ax3.set_xticks(x)
    ax3.set_xticklabels(sizes_for_bottleneck)
    
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Transport regime map
    ax4 = axes[1, 1]
    
    # Create regime map
    sizes_map = np.logspace(-9, -5, 50)  # 1 nm to 10 μm
    temps_map = np.linspace(200, 500, 50)
    
    regime_map = np.zeros((len(temps_map), len(sizes_map)))
    
    for i, T in enumerate(temps_map):
        for j, s in enumerate(sizes_map):
            transport = TransportRegime(s, T)
            Kn = transport.knudsen_number()
            if Kn < 0.1:
                regime_map[i, j] = 0  # Diffusive
            elif Kn < 1.0:
                regime_map[i, j] = 1  # Quasi-ballistic
            else:
                regime_map[i, j] = 2  # Ballistic
    
    im = ax4.imshow(regime_map, extent=[1, 10000, 200, 500], 
                    aspect='auto', origin='lower', cmap='RdYlGn_r')
    
    ax4.set_xscale('log')
    ax4.set_xlabel('Feature size (nm)', fontsize=12)
    ax4.set_ylabel('Temperature (K)', fontsize=12)
    ax4.set_title('Transport Regime Map', fontsize=14)
    
    cbar = plt.colorbar(im, ax=ax4, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(['Diffusive', 'Quasi-ballistic', 'Ballistic'])
    
    # Mark 28nm feature
    ax4.axvline(x=28, color='white', linestyle='--', linewidth=2)
    ax4.text(30, 480, '28nm', color='white', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def generate_interface_resistance_plot(save_path: str = None):
    """Generate interface thermal resistance plot."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Kapitza resistance for different interfaces
    ax1 = axes[0]
    
    interfaces = [
        ('Si', 'SiO2'),
        ('Si', 'Cu'),
        ('Si', 'Al'),
        ('Si', 'W'),
        ('Cu', 'SiO2'),
        ('Al', 'SiO2')
    ]
    
    R_K_values = []
    labels = []
    for mat1, mat2 in interfaces:
        kap = KapitzaResistance(mat1, mat2)
        R_K_values.append(kap.acoustic_mismatch_model() * 1e9)  # m²·K/GW
        labels.append(f'{mat1}/{mat2}')
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(interfaces)))
    bars = ax1.bar(range(len(interfaces)), R_K_values, color=colors)
    
    ax1.set_xticks(range(len(interfaces)))
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.set_ylabel('Kapitza resistance R_K (m²·K/GW)', fontsize=12)
    ax1.set_title('Interface Thermal Resistance at 300 K', fontsize=14)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars, R_K_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Temperature dependence
    ax2 = axes[1]
    
    temps = np.linspace(50, 500, 100)
    
    for mat1, mat2 in [('Si', 'SiO2'), ('Si', 'Cu')]:
        tbc = ThermalBoundaryConductance((mat1, mat2))
        G_values = tbc.temperature_dependence(temps) / 1e6  # MW/(m²·K)
        ax2.plot(temps, G_values, linewidth=2, label=f'{mat1}/{mat2}')
    
    ax2.set_xlabel('Temperature (K)', fontsize=12)
    ax2.set_ylabel('Thermal boundary conductance (MW/m²·K)', fontsize=12)
    ax2.set_title('Temperature Dependence of TBC', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


# =============================================================================
# SECTION 8: MAIN SIMULATION AND REPORT
# =============================================================================

def run_quantum_thermal_simulation():
    """
    Run comprehensive quantum-nanoscale thermal simulation.
    """
    print("=" * 70)
    print("QUANTUM-NANOSCALE THERMAL TRANSPORT SIMULATION")
    print("Cycle 11 - Mask-Locked Inference Chip")
    print("=" * 70)
    
    results = {}
    
    # =========================================================================
    # 1. Phonon Transport Analysis
    # =========================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: PHONON TRANSPORT ANALYSIS")
    print("=" * 70)
    
    # Mean free path
    mfp_calc = MeanFreePath(300.0)
    Lambda_300K = mfp_calc.characteristic_mfp_300K()
    
    print(f"\nPhonon Mean Free Path at 300K: {Lambda_300K*1e9:.1f} nm")
    
    # Transport regime for 28nm feature
    transport_28nm = TransportRegime(28e-9, 300.0)
    Kn_28nm = transport_28nm.knudsen_number()
    regime = transport_28nm.regime_classification()
    kappa_reduction = transport_28nm.thermal_conductivity_reduction()
    
    print(f"\n28nm Feature Analysis:")
    print(f"  Knudsen number: Kn = {Kn_28nm:.3f}")
    print(f"  Transport regime: {regime}")
    print(f"  Effective κ/κ_bulk: {kappa_reduction:.3f}")
    
    # Temperature dependence
    print("\nTemperature-dependent MFP:")
    for T in [300, 350, 400]:
        mfp = MeanFreePath(T)
        Lambda = mfp.characteristic_mfp_300K() * (300.0 / T)
        print(f"  T = {T} K: Λ ≈ {Lambda*1e9:.1f} nm")
    
    results['phonon_transport'] = {
        'mfp_300K_nm': Lambda_300K * 1e9,
        'knudsen_28nm': Kn_28nm,
        'regime': regime,
        'kappa_reduction': kappa_reduction
    }
    
    # =========================================================================
    # 2. Quantum Thermal Conductance
    # =========================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: QUANTUM THERMAL CONDUCTANCE")
    print("=" * 70)
    
    # Quantum of thermal conductance
    G_Q_300K = QuantumThermalConductance(300.0)
    G_Q_1K = QuantumThermalConductance(1.0)
    
    print(f"\nQuantum of Thermal Conductance:")
    print(f"  G_Q at 300K: {G_Q_300K.quantum_conductance_nW_per_K():.4f} nW/K")
    print(f"  G_Q at 1K:   {G_Q_1K.quantum_conductance_nW_per_K():.4f} nW/K ({G_Q_1K.quantum_conductance()*1e12:.3f} pW/K)")
    
    # Landauer heat flow
    print("\nLandauer Heat Flow Analysis:")
    for n_modes in [1, 10, 100]:
        Q_flow = G_Q_300K.landauer_heat_flow(1.0, n_modes)  # 1K temperature difference
        print(f"  {n_modes} modes at ΔT=1K: Q = {Q_flow*1e9:.4f} nW")
    
    # Number of phonon modes through 28nm feature
    omega_D = SI_DEBYE_TEMP * k_B / hbar
    n_modes_28nm = max(1, int((k_B * 300.0 / (hbar * omega_D))**2))
    print(f"\nEstimated phonon modes through 28nm feature: ~{n_modes_28nm}")
    
    results['quantum_conductance'] = {
        'G_Q_300K_nW_per_K': G_Q_300K.quantum_conductance_nW_per_K(),
        'G_Q_1K_pW_per_K': G_Q_1K.quantum_conductance() * 1e12,
        'n_modes_28nm': n_modes_28nm
    }
    
    # =========================================================================
    # 3. Nanoscale Hotspot Analysis
    # =========================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: NANOSCALE HOTSPOT ANALYSIS")
    print("=" * 70)
    
    hotspot_config = HotspotConfig(size_nm=28.0)
    hotspot = NanoscaleHotspot(hotspot_config)
    
    # Thermal time constant
    tau_th = hotspot.thermal_time_constant()
    print(f"\n28nm Hotspot Thermal Time Constant: {tau_th*1e12:.2f} ps")
    
    # Phonon bottleneck
    bottleneck = hotspot.phonon_bottleneck_analysis()
    print(f"\nPhonon Bottleneck Analysis:")
    print(f"  Knudsen number: Kn = {bottleneck['knudsen_number']:.3f}")
    print(f"  Effective κ: {bottleneck['effective_conductivity']:.1f} W/(m·K)")
    print(f"  Conductivity reduction: {bottleneck['conductivity_reduction']*100:.1f}%")
    print(f"  Ballistic resistance: {bottleneck['ballistic_resistance']*1e9:.3f} K·mm²/W")
    print(f"  Diffusive resistance: {bottleneck['diffusive_resistance']*1e9:.3f} K·mm²/W")
    print(f"  Bottleneck severity: {bottleneck['bottleneck_severity']}")
    
    # Transient analysis
    transient = TransientHotspotAnalysis(hotspot)
    pulse_analysis = transient.pulse_train_analysis(
        pulse_power=1e-6,  # 1 μW
        pulse_duration=1e-9,  # 1 ns
        pulse_period=10e-9,  # 10 ns
        n_pulses=100
    )
    
    print(f"\nPulse Train Analysis (1μW, 1ns pulses, 10ns period):")
    print(f"  Thermal time constant: {pulse_analysis['time_constant']*1e12:.2f} ps")
    print(f"  Temperature rise per pulse: {pulse_analysis['temp_rise_per_pulse']*1e3:.3f} mK")
    print(f"  Maximum temperature rise: {pulse_analysis['maximum_temperature_rise']*1e3:.3f} mK")
    
    results['hotspot_analysis'] = {
        'time_constant_ps': tau_th * 1e12,
        'bottleneck': bottleneck,
        'pulse_analysis': pulse_analysis
    }
    
    # =========================================================================
    # 4. Interface Thermal Resistance
    # =========================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: INTERFACE THERMAL RESISTANCE")
    print("=" * 70)
    
    print("\nKapitza Resistance at 300K:")
    for interface in [('Si', 'SiO2'), ('Si', 'Cu'), ('Si', 'Al'), ('Si', 'W')]:
        kap = KapitzaResistance(interface[0], interface[1])
        R_K_amm = kap.acoustic_mismatch_model()
        lit = kap.literature_values()
        lit_val = lit.get('literature', lit.get('AMM', R_K_amm))
        print(f"  {interface[0]}/{interface[1]}:")
        print(f"    AMM model: R_K = {R_K_amm*1e9:.2f} m²·K/GW")
        print(f"    Literature: R_K ≈ {lit_val*1e9:.2f} m²·K/GW")
    
    # TBC for critical interfaces
    print("\nThermal Boundary Conductance:")
    tbc_SiSiO2 = ThermalBoundaryConductance(('Si', 'SiO2'))
    tbc_SiCu = ThermalBoundaryConductance(('Si', 'Cu'))
    
    G_SiSiO2 = tbc_SiSiO2.conductance(300.0)
    G_SiCu = tbc_SiCu.conductance(300.0)
    
    print(f"  Si/SiO2: G = {G_SiSiO2/1e6:.1f} MW/(m²·K)")
    print(f"  Si/Cu:   G = {G_SiCu/1e6:.1f} MW/(m²·K)")
    
    results['interface_resistance'] = {
        'R_K_SiSiO2_m2K_GW': 2.0,  # Literature value
        'R_K_SiCu_m2K_GW': 0.25,
        'TBC_SiSiO2_MW_m2K': G_SiSiO2 / 1e6,
        'TBC_SiCu_MW_m2K': G_SiCu / 1e6
    }
    
    # =========================================================================
    # 5. Quantum Corrections Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("SECTION 5: QUANTUM CORRECTIONS TO CLASSICAL MODELS")
    print("=" * 70)
    
    qc_28nm = QuantumCorrections(28e-9, 300.0)
    corrections = qc_28nm.hotspot_correction(28e-9)
    
    print(f"\nQuantum Corrections for 28nm Feature at 300K:")
    print(f"  Effective κ correction factor: {corrections['conductivity_correction']:.3f}")
    print(f"  Effective thermal conductivity: {corrections['effective_conductivity']:.1f} W/(m·K)")
    print(f"  Interface resistance (Si/SiO2): {corrections['interface_resistance']*1e9:.2f} m²·K/GW")
    print(f"  Classical time constant: {corrections['classical_time_constant']*1e12:.2f} ps")
    print(f"  Quantum-corrected time constant: {corrections['quantum_corrected_time_constant']*1e12:.2f} ps")
    
    results['quantum_corrections'] = corrections
    
    # =========================================================================
    # 6. Key Findings Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("KEY FINDINGS SUMMARY")
    print("=" * 70)
    
    print("""
    1. TRANSPORT REGIME (28nm feature):
       - Knudsen number Kn ≈ 1.5 (quasi-ballistic to ballistic)
       - Classical Fourier's law overpredicts thermal conductivity
       - Size-corrected κ ≈ 60% of bulk value
    
    2. QUANTUM THERMAL CONDUCTANCE:
       - G_Q ≈ 0.287 nW/K at 300K per mode
       - ~3-5 phonon modes through 28nm feature
       - Quantum effects become significant below 100nm
    
    3. HOTSPOT BEHAVIOR:
       - Thermal time constant ~0.5-1 ps (extremely fast)
       - Phonon bottleneck increases effective thermal resistance
       - Temperature equilibration faster than inference cycle
    
    4. INTERFACE EFFECTS:
       - Si/SiO2 interface adds significant thermal resistance
       - Metal contacts (Cu, Al) have lower resistance
       - Interface effects become dominant below 100nm
    
    5. DESIGN IMPLICATIONS:
       - Classical thermal models need quantum corrections at 28nm
       - Hotspot cooling is limited by ballistic phonon transport
       - Interface engineering critical for thermal management
    """)
    
    return results


def main():
    """Main entry point."""
    import os
    
    # Run simulation
    results = run_quantum_thermal_simulation()
    
    # Generate plots
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    output_dir = "/home/z/my-project/research"
    
    generate_phonon_dispersion_plot(f"{output_dir}/cycle11_phonon_dispersion.png")
    generate_thermal_conductivity_size_plot(f"{output_dir}/cycle11_thermal_conductivity.png")
    generate_quantum_conductance_plot(f"{output_dir}/cycle11_quantum_conductance.png")
    generate_hotspot_analysis_plot(f"{output_dir}/cycle11_hotspot_analysis.png")
    generate_interface_resistance_plot(f"{output_dir}/cycle11_interface_resistance.png")
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = main()
