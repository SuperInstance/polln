#!/usr/bin/env python3
"""
Cycle 5: Thermal-Fluid Dynamics Coupled Simulation
====================================================

Comprehensive thermal-fluid dynamics simulation for Mask-Locked Inference Chip.

Features:
- Conjugate heat transfer (solid + fluid domains)
- Natural convection cooling modeling
- Forced air cooling scenarios
- Thermal interface materials (TIM) optimization
- Heat sink geometry optimization for 5W TDP

Author: Thermal-Fluid Dynamics Agent
Date: March 2026
Cycle: 5 - Thermal-Fluid Dynamics Coupled Simulation
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve, cg
from scipy.ndimage import gaussian_filter
from scipy.optimize import minimize_scalar, minimize
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Union
from enum import Enum
import time
import json
from datetime import datetime

# Physical Constants
G = 9.81                # Gravitational acceleration [m/s²]
R_AIR = 287.05          # Specific gas constant for air [J/(kg·K)]
KB_J = 1.38e-23         # Boltzmann constant [J/K]
KB_EV = 8.617e-5        # Boltzmann constant [eV/K]

# Material Properties at 300K
class MaterialProperties:
    """Material thermal and physical properties."""
    
    # Thermal conductivities [W/(m·K)]
    k_silicon = 148.0
    k_copper = 385.0
    k_aluminum = 205.0
    k_sio2 = 1.4
    k_solder = 50.0
    k_tim_generic = 4.0
    k_tim_phase_change = 6.0
    k_tim_graphite = 15.0
    k_tim_liquid_metal = 40.0
    k_air = 0.026
    k_pcb_fr4 = 0.3
    k_plastic_qfn = 0.25
    
    # Specific heats [J/(kg·K)]
    cp_silicon = 700.0
    cp_copper = 385.0
    cp_aluminum = 900.0
    cp_air = 1005.0
    
    # Densities [kg/m³]
    rho_silicon = 2329.0
    rho_copper = 8960.0
    rho_aluminum = 2700.0
    rho_air = 1.177
    
    # Viscosity [Pa·s]
    mu_air = 1.85e-5
    
    # Thermal expansion coefficient [1/K]
    beta_air = 1.0 / 300.0  # For ideal gas
    
    # Prandtl number
    Pr_air = 0.707


@dataclass
class ThermalFluidParameters:
    """Parameters for thermal-fluid simulation."""
    
    # Chip specifications
    die_size_mm: float = 6.5
    die_thickness_um: float = 300.0
    package_type: str = "48-pin QFN"
    package_size_mm: float = 7.0
    package_height_mm: float = 1.0
    
    # Power specifications
    tdp_w: float = 5.0           # Target TDP
    power_map_type: str = "uniform"
    
    # Environmental conditions
    t_ambient_c: float = 25.0     # Ambient temperature [°C]
    t_max_junction_c: float = 85.0  # Maximum junction temperature [°C]
    
    # Cooling scenarios
    cooling_type: str = "natural_convection"
    
    # Heat sink parameters
    heatsink_base_thickness_mm: float = 2.0
    heatsink_fin_height_mm: float = 20.0
    heatsink_fin_thickness_mm: float = 0.8
    heatsink_fin_pitch_mm: float = 2.5
    heatsink_material: str = "aluminum"
    heatsink_width_mm: float = 40.0
    heatsink_length_mm: float = 40.0
    
    # TIM parameters
    tim_type: str = "phase_change"
    tim_thickness_um: float = 50.0
    
    # Simulation parameters
    grid_resolution: int = 64
    max_iterations: int = 100
    convergence_tol: float = 0.01
    
    @property
    def t_ambient_k(self) -> float:
        return self.t_ambient_c + 273.15
    
    @property
    def t_max_junction_k(self) -> float:
        return self.t_max_junction_c + 273.15
    
    @property
    def die_area_m2(self) -> float:
        return (self.die_size_mm * 1e-3) ** 2
    
    @property
    def thermal_budget_k(self) -> float:
        return self.t_max_junction_k - self.t_ambient_k


class ConjugateHeatTransfer:
    """
    Conjugate heat transfer solver for solid-fluid domains.
    """
    
    def __init__(self, params: ThermalFluidParameters):
        self.params = params
        
    def thermal_resistance_conduction(self, 
                                      thickness_m: float,
                                      area_m2: float,
                                      k: float) -> float:
        """
        Calculate thermal resistance for conduction.
        R_cond = t / (k × A)
        """
        if k > 0 and area_m2 > 0:
            return thickness_m / (k * area_m2)
        return float('inf')
    
    def thermal_resistance_tim(self,
                               tim_type: str,
                               thickness_um: float,
                               area_mm2: float) -> float:
        """
        Calculate TIM thermal resistance including contact resistance.
        """
        k_map = {
            'generic': 4.0, 'phase_change': 6.0, 'graphite': 15.0, 'liquid_metal': 40.0
        }
        R_contact_map = {
            'generic': 0.1e-4, 'phase_change': 0.05e-4, 
            'graphite': 0.03e-4, 'liquid_metal': 0.01e-4
        }
        
        k = k_map.get(tim_type.lower(), 4.0)
        t = thickness_um * 1e-6
        A = area_mm2 * 1e-6
        
        R_cond = t / (k * A)
        R_contact = R_contact_map.get(tim_type.lower(), 0.1e-4) / A
        
        return R_cond + R_contact
    
    def solve_3d_temperature(self,
                            power_w: float,
                            T_ambient: float,
                            R_heatsink: float) -> Dict:
        """
        Solve temperature distribution through package stack.
        """
        die_area = self.params.die_area_m2
        heatsink_area = (self.params.heatsink_width_mm * 1e-3) * \
                        (self.params.heatsink_length_mm * 1e-3)
        
        # Layer thermal resistances (from die to ambient)
        layers = []
        
        # Die conduction (silicon)
        R_die = self.thermal_resistance_conduction(
            self.params.die_thickness_um * 1e-6, die_area, MaterialProperties.k_silicon)
        layers.append({'name': 'die', 'R': R_die, 'material': 'silicon'})
        
        # TIM
        R_tim = self.thermal_resistance_tim(
            self.params.tim_type, self.params.tim_thickness_um,
            self.params.die_size_mm ** 2)
        layers.append({'name': 'tim', 'R': R_tim, 'material': 'tim'})
        
        # Heat spreader (copper)
        spreader_thickness = 1.0e-3
        R_spreader = self.thermal_resistance_conduction(
            spreader_thickness, heatsink_area, MaterialProperties.k_copper)
        layers.append({'name': 'spreader', 'R': R_spreader, 'material': 'copper'})
        
        # Heat sink base
        R_base = self.thermal_resistance_conduction(
            self.params.heatsink_base_thickness_mm * 1e-3,
            heatsink_area, MaterialProperties.k_aluminum)
        layers.append({'name': 'heatsink_base', 'R': R_base, 'material': 'aluminum'})
        
        # Heat sink convection (provided as input)
        layers.append({'name': 'convection', 'R': R_heatsink, 'material': 'air'})
        
        # Calculate cumulative resistances and temperatures
        R_cumulative = []
        temperatures = [T_ambient]
        T = T_ambient
        R_sum = 0
        
        for layer in reversed(layers):  # From ambient to die
            R_sum += layer['R']
            R_cumulative.append(R_sum)
            T = T_ambient + power_w * R_sum
            temperatures.append(T)
        
        T_junction = temperatures[-1]
        R_total = R_sum
        
        return {
            'T_junction': T_junction,
            'T_junction_c': T_junction - 273.15,
            'T_ambient': T_ambient,
            'R_total': R_total,
            'layers': layers,
            'temperatures': temperatures[::-1],
            'R_cumulative': R_cumulative[::-1]
        }


class NaturalConvectionModel:
    """
    Natural convection cooling model.
    """
    
    def __init__(self, params: ThermalFluidParameters):
        self.params = params
        
    def grashof_number(self, dT: float, L: float, T_film: float = 325.0) -> float:
        """Calculate Grashof number: Gr = g × β × ΔT × L³ / ν²"""
        beta = 1.0 / T_film
        nu = MaterialProperties.mu_air / (MaterialProperties.rho_air * 300.0 / T_film)
        Gr = G * beta * dT * L**3 / (nu**2)
        return Gr
    
    def rayleigh_number(self, dT: float, L: float, T_film: float = 325.0) -> float:
        """Calculate Rayleigh number: Ra = Gr × Pr"""
        Gr = self.grashof_number(dT, L, T_film)
        return Gr * MaterialProperties.Pr_air
    
    def nusselt_number(self, Ra: float) -> float:
        """Churchill-Chu correlation for vertical plate."""
        if Ra < 1e4:
            Nu = 0.59 * Ra**0.25
        elif Ra < 1e9:
            Nu = 0.59 * Ra**0.25
        else:
            Nu = 0.10 * Ra**(1.0/3.0)
        return max(Nu, 1.0)
    
    def convection_coefficient(self, dT: float, L: float, T_film: float = 325.0) -> float:
        """Calculate natural convection coefficient: h = Nu × k / L"""
        Ra = self.rayleigh_number(dT, L, T_film)
        Nu = self.nusselt_number(Ra)
        return Nu * MaterialProperties.k_air / L
    
    def heatsink_thermal_resistance(self, T_surface: float = 350.0, 
                                    T_ambient: float = 298.0) -> Dict:
        """
        Calculate thermal resistance of heatsink under natural convection.
        """
        # Geometry
        W = self.params.heatsink_width_mm * 1e-3
        L = self.params.heatsink_length_mm * 1e-3
        H = self.params.heatsink_fin_height_mm * 1e-3
        t_fin = self.params.heatsink_fin_thickness_mm * 1e-3
        pitch = self.params.heatsink_fin_pitch_mm * 1e-3
        
        dT = T_surface - T_ambient
        T_film = (T_surface + T_ambient) / 2
        
        # Number of fins
        n_fins = int(L / pitch)
        S = pitch - t_fin  # Fin spacing
        
        # Convection coefficient
        h = self.convection_coefficient(dT, H, T_film)
        
        # Fin efficiency
        k = MaterialProperties.k_aluminum
        m = np.sqrt(2 * h / (k * t_fin))
        eta_fin = np.tanh(m * H) / (m * H) if m * H > 0 else 1.0
        
        # Surface areas
        A_base = W * L - n_fins * t_fin * W  # Exposed base area
        A_fins = 2 * n_fins * H * W          # Total fin surface area
        A_total = A_base + eta_fin * A_fins
        
        # Convection thermal resistance
        R_conv = 1.0 / (h * A_total)
        
        # Spreading resistance (Lee correlation)
        r_source = np.sqrt(self.params.die_area_m2 / np.pi)
        r_sink = min(W, L) / 2
        t_base = self.params.heatsink_base_thickness_mm * 1e-3
        
        if r_source > 0 and r_sink > r_source:
            epsilon = r_source / r_sink
            Bi = h * r_sink / k
            # Simplified spreading resistance
            R_spread = 1.0 / (2 * np.pi * k * t_base) * \
                       (1 - epsilon) / epsilon
        else:
            R_spread = 0
        
        R_total = R_conv + R_spread
        
        return {
            'convection_coefficient': h,
            'fin_efficiency': eta_fin,
            'total_surface_area_m2': A_total,
            'num_fins': n_fins,
            'fin_spacing_m': S,
            'rayleigh_number': self.rayleigh_number(dT, H, T_film),
            'nusselt_number': self.nusselt_number(self.rayleigh_number(dT, H, T_film)),
            'R_convection': R_conv,
            'R_spreading': R_spread,
            'R_total': R_total
        }


class ForcedAirCoolingModel:
    """
    Forced air cooling model.
    """
    
    def __init__(self, params: ThermalFluidParameters):
        self.params = params
        
    def reynolds_number(self, velocity: float, L: float) -> float:
        """Calculate Reynolds number: Re = ρVL/μ"""
        return MaterialProperties.rho_air * velocity * L / MaterialProperties.mu_air
    
    def nusselt_number_forced(self, Re: float) -> float:
        """Nusselt number for forced convection (flat plate)."""
        Pr = MaterialProperties.Pr_air
        if Re < 5e2:
            Nu = 0.664 * Re**0.5 * Pr**(1.0/3.0)
        elif Re < 2e5:
            Nu = 0.228 * Re**0.731 * Pr**(1.0/3.0)
        else:
            Nu = 0.0296 * Re**0.8 * Pr**(1.0/3.0)
        return max(Nu, 1.0)
    
    def convection_coefficient_forced(self, velocity: float, L: float) -> float:
        """Calculate forced convection coefficient."""
        Re = self.reynolds_number(velocity, L)
        Nu = self.nusselt_number_forced(Re)
        return Nu * MaterialProperties.k_air / L
    
    def heatsink_thermal_resistance(self, velocity: float = 2.0,
                                    T_ambient: float = 298.0) -> Dict:
        """
        Calculate thermal resistance of heatsink under forced convection.
        """
        W = self.params.heatsink_width_mm * 1e-3
        L = self.params.heatsink_length_mm * 1e-3
        H = self.params.heatsink_fin_height_mm * 1e-3
        t_fin = self.params.heatsink_fin_thickness_mm * 1e-3
        pitch = self.params.heatsink_fin_pitch_mm * 1e-3
        t_base = self.params.heatsink_base_thickness_mm * 1e-3
        
        n_fins = int(L / pitch)
        S = pitch - t_fin
        
        # Forced convection coefficient
        h = self.convection_coefficient_forced(velocity, H)
        
        # Fin efficiency
        k = MaterialProperties.k_aluminum
        m = np.sqrt(2 * h / (k * t_fin))
        eta_fin = np.tanh(m * H) / (m * H) if m * H > 0 else 1.0
        
        # Surface areas
        A_base = W * L - n_fins * t_fin * W
        A_fins = 2 * n_fins * H * W
        A_total = A_base + eta_fin * A_fins
        
        # Convection thermal resistance
        R_conv = 1.0 / (h * A_total)
        
        # Spreading resistance
        r_source = np.sqrt(self.params.die_area_m2 / np.pi)
        r_sink = min(W, L) / 2
        
        if r_source > 0 and r_sink > r_source:
            epsilon = r_source / r_sink
            R_spread = 1.0 / (2 * np.pi * k * t_base) * (1 - epsilon) / epsilon
        else:
            R_spread = 0
        
        R_total = R_conv + R_spread
        
        # Pressure drop
        D_h = 2 * S * H / (S + H) if (S + H) > 0 else S
        Re_channel = self.reynolds_number(velocity, D_h) if D_h > 0 else 0
        f = 64 / Re_channel if Re_channel > 0 else 0.1
        
        rho = MaterialProperties.rho_air
        dP = f * (n_fins * W / D_h) * (rho * velocity**2 / 2) if D_h > 0 else 0
        
        # Fan power
        Q = velocity * S * H * n_fins
        P_fan = dP * Q / 0.4 if Q > 0 else 0  # 40% fan efficiency
        
        return {
            'velocity': velocity,
            'convection_coefficient': h,
            'fin_efficiency': eta_fin,
            'total_surface_area_m2': A_total,
            'num_fins': n_fins,
            'reynolds_number': self.reynolds_number(velocity, H),
            'nusselt_number': self.nusselt_number_forced(self.reynolds_number(velocity, H)),
            'R_convection': R_conv,
            'R_spreading': R_spread,
            'R_total': R_total,
            'pressure_drop_Pa': dP,
            'fan_power_W': P_fan,
            'flow_rate_m3_s': Q
        }


class TIMOptimizer:
    """Thermal Interface Material optimizer."""
    
    def __init__(self, params: ThermalFluidParameters):
        self.params = params
        
    def tim_comparison(self, power_w: float) -> List[Dict]:
        """Compare different TIM materials."""
        tim_types = [
            ('generic', 4.0, 0.1e-4, 0.50),
            ('phase_change', 6.0, 0.05e-4, 1.00),
            ('graphite', 15.0, 0.03e-4, 2.50),
            ('liquid_metal', 40.0, 0.01e-4, 5.00)
        ]
        
        results = []
        A = self.params.die_area_m2
        t = self.params.tim_thickness_um * 1e-6
        
        for name, k, R_contact_spec, cost in tim_types:
            R_cond = t / (k * A)
            R_contact = R_contact_spec / A
            R_total = R_cond + R_contact
            dT = power_w * R_total
            
            results.append({
                'type': name,
                'conductivity': k,
                'contact_resistance_m2K_W': R_contact_spec,
                'R_total_K_W': R_total,
                'temperature_drop_K': dT,
                'cost_factor': cost,
                'performance_score': 1.0 / R_total / cost
            })
        
        return sorted(results, key=lambda x: x['performance_score'], reverse=True)
    
    def optimal_thickness(self, tim_type: str, power_w: float) -> Dict:
        """Find optimal TIM thickness."""
        k_map = {'generic': 4.0, 'phase_change': 6.0, 'graphite': 15.0, 'liquid_metal': 40.0}
        R_contact_map = {'generic': 0.1e-4, 'phase_change': 0.05e-4, 
                        'graphite': 0.03e-4, 'liquid_metal': 0.01e-4}
        
        k = k_map.get(tim_type, 4.0)
        R_contact_spec = R_contact_map.get(tim_type, 0.1e-4)
        A = self.params.die_area_m2
        
        thickness_range = np.linspace(10e-6, 200e-6, 100)
        R_list = []
        
        for t in thickness_range:
            R_cond = t / (k * A)
            R_contact = R_contact_spec / A * (t / 50e-6)**0.5
            R_list.append(R_cond + R_contact)
        
        R_array = np.array(R_list)
        idx_opt = np.argmin(R_array)
        
        return {
            'optimal_thickness_um': thickness_range[idx_opt] * 1e6,
            'min_thermal_resistance_K_W': R_array[idx_opt],
            'temperature_drop_K': power_w * R_array[idx_opt]
        }


class HeatSinkOptimizer:
    """Heat sink geometry optimizer."""
    
    def __init__(self, params: ThermalFluidParameters):
        self.params = params
        
    def optimize_for_power(self, power_w: float, T_max: float, 
                          T_ambient: float, cooling_type: str = 'natural') -> Dict:
        """Optimize heatsink geometry for target power."""
        dT_budget = T_max - T_ambient
        R_target = dT_budget / power_w if power_w > 0 else float('inf')
        
        best_result = None
        best_R = float('inf')
        
        # Grid search
        for fin_height in np.linspace(10, 30, 8):
            for fin_pitch in np.linspace(1.5, 4.0, 8):
                for base_thickness in np.linspace(1.0, 4.0, 5):
                    # Temporary params
                    temp_params = ThermalFluidParameters()
                    temp_params.heatsink_fin_height_mm = fin_height
                    temp_params.heatsink_fin_pitch_mm = fin_pitch
                    temp_params.heatsink_base_thickness_mm = base_thickness
                    temp_params.die_size_mm = self.params.die_size_mm
                    temp_params.heatsink_width_mm = self.params.heatsink_width_mm
                    temp_params.heatsink_length_mm = self.params.heatsink_length_mm
                    
                    if cooling_type == 'natural':
                        model = NaturalConvectionModel(temp_params)
                        result = model.heatsink_thermal_resistance(T_max - 5, T_ambient)
                    else:
                        model = ForcedAirCoolingModel(temp_params)
                        result = model.heatsink_thermal_resistance(2.0, T_ambient)
                    
                    if result['R_total'] < best_R:
                        best_R = result['R_total']
                        best_result = {
                            'fin_height_mm': fin_height,
                            'fin_pitch_mm': fin_pitch,
                            'base_thickness_mm': base_thickness,
                            'R_total_K_W': result['R_total'],
                            'meets_target': result['R_total'] <= R_target,
                            'margin_K': dT_budget - power_w * result['R_total'],
                            **result
                        }
        
        return best_result


class ThermalFluidSimulator:
    """Main thermal-fluid simulation class."""
    
    def __init__(self, params: ThermalFluidParameters = None):
        if params is None:
            params = ThermalFluidParameters()
        self.params = params
        
        self.conjugate_ht = ConjugateHeatTransfer(params)
        self.natural_conv = NaturalConvectionModel(params)
        self.forced_conv = ForcedAirCoolingModel(params)
        self.tim_optimizer = TIMOptimizer(params)
        self.heatsink_optimizer = HeatSinkOptimizer(params)
    
    def run_full_simulation(self) -> Dict:
        """Run complete thermal-fluid simulation."""
        T_ambient = self.params.t_ambient_k
        T_max = self.params.t_max_junction_k
        power = self.params.tdp_w
        
        results = {
            'parameters': {
                'tdp_w': power,
                't_ambient_k': T_ambient,
                't_ambient_c': T_ambient - 273.15,
                't_max_junction_k': T_max,
                't_max_junction_c': T_max - 273.15,
                'die_size_mm': self.params.die_size_mm,
                'package_type': self.params.package_type
            },
            'natural_convection': {},
            'forced_air': {},
            'tim_analysis': {},
            'temperature_distribution': {},
            'recommendations': []
        }
        
        # Natural convection
        results['natural_convection'] = self.natural_conv.heatsink_thermal_resistance(T_max - 10, T_ambient)
        
        # Forced air
        forced_results = {}
        for velocity in [0.5, 1.0, 2.0, 3.0, 5.0]:
            forced_results[f'v_{velocity}m_s'] = self.forced_conv.heatsink_thermal_resistance(velocity, T_ambient)
        results['forced_air'] = forced_results
        
        # TIM
        results['tim_analysis'] = {
            'comparison': self.tim_optimizer.tim_comparison(power),
            'optimal_thickness': self.tim_optimizer.optimal_thickness(self.params.tim_type, power)
        }
        
        # Temperature distributions
        R_nat = results['natural_convection']['R_total']
        R_frc = results['forced_air']['v_2.0m_s']['R_total']
        
        results['temperature_distribution'] = {
            'natural': self.conjugate_ht.solve_3d_temperature(power, T_ambient, R_nat),
            'forced_air': self.conjugate_ht.solve_3d_temperature(power, T_ambient, R_frc)
        }
        
        # Recommendations
        T_junc_nat = results['temperature_distribution']['natural']['T_junction']
        T_junc_frc = results['temperature_distribution']['forced_air']['T_junction']
        
        recommendations = []
        
        if T_junc_nat > T_max:
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'Natural convection: T_junction={T_junc_nat-273.15:.1f}°C exceeds max {T_max-273.15:.0f}°C',
                'solution': 'Use forced air cooling or larger heatsink'
            })
        else:
            recommendations.append({
                'priority': 'INFO',
                'issue': f'Natural convection: T_junction={T_junc_nat-273.15:.1f}°C within budget',
                'solution': f'Margin: {T_max - T_junc_nat:.1f}K'
            })
        
        if T_junc_frc > T_max:
            recommendations.append({
                'priority': 'CRITICAL',
                'issue': f'Forced air (2m/s): T_junction={T_junc_frc-273.15:.1f}°C exceeds max',
                'solution': 'Reduce power or implement liquid cooling'
            })
        else:
            recommendations.append({
                'priority': 'INFO',
                'issue': f'Forced air (2m/s): T_junction={T_junc_frc-273.15:.1f}°C within budget',
                'solution': f'Margin: {T_max - T_junc_frc:.1f}K'
            })
        
        best_tim = results['tim_analysis']['comparison'][0]
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': 'TIM optimization',
            'solution': f"Best TIM: {best_tim['type']} (R={best_tim['R_total_K_W']*1000:.2f} mK/W)"
        })
        
        results['recommendations'] = recommendations
        
        return results
    
    def generate_report(self) -> str:
        """Generate text report."""
        results = self.run_full_simulation()
        
        lines = []
        lines.append("=" * 70)
        lines.append("THERMAL-FLUID DYNAMICS SIMULATION REPORT")
        lines.append("Cycle 5 - Mask-Locked Inference Chip")
        lines.append("=" * 70)
        lines.append("")
        
        p = results['parameters']
        lines.append("SIMULATION PARAMETERS")
        lines.append("-" * 40)
        lines.append(f"  TDP: {p['tdp_w']:.1f} W")
        lines.append(f"  Ambient: {p['t_ambient_c']:.1f}°C ({p['t_ambient_k']:.1f} K)")
        lines.append(f"  Max Junction: {p['t_max_junction_c']:.1f}°C ({p['t_max_junction_k']:.1f} K)")
        lines.append(f"  Die Size: {p['die_size_mm']:.1f} × {p['die_size_mm']:.1f} mm")
        lines.append(f"  Package: {p['package_type']}")
        lines.append("")
        
        lines.append("NATURAL CONVECTION COOLING")
        lines.append("-" * 40)
        nc = results['natural_convection']
        lines.append(f"  Convection Coeff: {nc['convection_coefficient']:.2f} W/(m²·K)")
        lines.append(f"  Fin Efficiency: {nc['fin_efficiency']:.3f}")
        lines.append(f"  Surface Area: {nc['total_surface_area_m2']*1e4:.1f} cm²")
        lines.append(f"  Num Fins: {nc['num_fins']}")
        lines.append(f"  Ra = {nc['rayleigh_number']:.2e}, Nu = {nc['nusselt_number']:.1f}")
        lines.append(f"  R_convection: {nc['R_convection']:.2f} K/W")
        lines.append(f"  R_spreading: {nc['R_spreading']:.3f} K/W")
        lines.append(f"  R_total: {nc['R_total']:.2f} K/W")
        lines.append("")
        
        lines.append("FORCED AIR COOLING (v=2.0 m/s)")
        lines.append("-" * 40)
        fa = results['forced_air']['v_2.0m_s']
        lines.append(f"  Convection Coeff: {fa['convection_coefficient']:.2f} W/(m²·K)")
        lines.append(f"  Re = {fa['reynolds_number']:.0f}, Nu = {fa['nusselt_number']:.1f}")
        lines.append(f"  R_total: {fa['R_total']:.2f} K/W")
        lines.append(f"  Pressure Drop: {fa['pressure_drop_Pa']:.2f} Pa")
        lines.append(f"  Fan Power: {fa['fan_power_W']*1000:.1f} mW")
        lines.append("")
        
        lines.append("TEMPERATURE DISTRIBUTION")
        lines.append("-" * 40)
        td_nat = results['temperature_distribution']['natural']
        td_frc = results['temperature_distribution']['forced_air']
        lines.append(f"  Natural Convection:")
        lines.append(f"    T_junction: {td_nat['T_junction_c']:.1f}°C")
        lines.append(f"    R_total: {td_nat['R_total']:.2f} K/W")
        lines.append(f"  Forced Air (2 m/s):")
        lines.append(f"    T_junction: {td_frc['T_junction_c']:.1f}°C")
        lines.append(f"    R_total: {td_frc['R_total']:.2f} K/W")
        lines.append("")
        
        lines.append("TIM ANALYSIS")
        lines.append("-" * 40)
        for tim in results['tim_analysis']['comparison']:
            lines.append(f"  {tim['type'].upper()}: k={tim['conductivity']:.0f} W/mK, "
                        f"R={tim['R_total_K_W']*1000:.1f} mK/W, ΔT={tim['temperature_drop_K']:.2f}K")
        lines.append("")
        
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for rec in results['recommendations']:
            lines.append(f"  [{rec['priority']}] {rec['issue']}")
            lines.append(f"    → {rec['solution']}")
        lines.append("")
        
        T_junc = td_nat['T_junction']
        status = "PASS" if T_junc <= p['t_max_junction_k'] else "FAIL"
        lines.append("=" * 70)
        lines.append(f"THERMAL STATUS: {status}")
        lines.append(f"  Junction Temp: {td_nat['T_junction_c']:.1f}°C")
        lines.append(f"  Margin: {p['t_max_junction_k'] - T_junc:.1f} K")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def create_visualizations(results: Dict, output_dir: str = "/home/z/my-project/research"):
    """Create visualization plots."""
    import matplotlib.pyplot as plt
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Figure 1: Cooling Method Comparison
    fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Thermal resistance comparison
    velocities = ['Natural\nConv.', '0.5\nm/s', '1.0\nm/s', '2.0\nm/s', '3.0\nm/s', '5.0\nm/s']
    R_values = [results['natural_convection']['R_total']]
    
    for v in [0.5, 1.0, 2.0, 3.0, 5.0]:
        R_values.append(results['forced_air'][f'v_{v}m_s']['R_total'])
    
    colors = ['#3498db'] + ['#2ecc71'] * 5
    axes[0].bar(velocities, R_values, color=colors, edgecolor='black')
    axes[0].set_ylabel('Thermal Resistance [K/W]', fontsize=12)
    axes[0].set_title('Heatsink Thermal Resistance', fontsize=14, fontweight='bold')
    axes[0].axhline(y=results['natural_convection']['R_total'], color='red', 
                   linestyle='--', alpha=0.5, label='Natural Conv. Baseline')
    
    # Junction temperature comparison
    T_ambient = results['parameters']['t_ambient_c']
    power = results['parameters']['tdp_w']
    T_junctions = [T_ambient + power * R for R in R_values]
    
    axes[1].bar(velocities, T_junctions, color=colors, edgecolor='black')
    axes[1].axhline(y=85, color='red', linestyle='--', linewidth=2, label='Max Junction (85°C)')
    axes[1].axhline(y=T_ambient, color='blue', linestyle=':', label=f'Ambient ({T_ambient:.0f}°C)')
    axes[1].set_ylabel('Junction Temperature [°C]', fontsize=12)
    axes[1].set_title('Junction Temperature', fontsize=14, fontweight='bold')
    axes[1].legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cycle5_cooling_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 2: TIM Comparison
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    tim_names = [t['type'].upper() for t in results['tim_analysis']['comparison']]
    tim_R = [t['R_total_K_W'] * 1000 for t in results['tim_analysis']['comparison']]
    tim_dT = [t['temperature_drop_K'] for t in results['tim_analysis']['comparison']]
    
    x = np.arange(len(tim_names))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, tim_R, width, label='R [mK/W]', color='#3498db')
    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(x + width/2, tim_dT, width, label='ΔT [K]', color='#e74c3c')
    
    ax2.set_xlabel('TIM Material', fontsize=12)
    ax2.set_ylabel('Thermal Resistance [mK/W]', fontsize=12, color='#3498db')
    ax2_twin.set_ylabel('Temperature Drop [K]', fontsize=12, color='#e74c3c')
    ax2.set_xticks(x)
    ax2.set_xticklabels(tim_names)
    ax2.set_title('Thermal Interface Material Comparison', fontsize=14, fontweight='bold')
    
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cycle5_tim_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 3: Temperature Profile
    fig3, ax3 = plt.subplots(figsize=(10, 7))
    
    # Package stack positions
    positions = [0, 1.6, 1.7, 2.0, 2.05, 3.05, 4.55]
    labels = ['PCB\nBottom', 'PCB\nTop', 'Solder', 'Die\n(Junction)', 'TIM', 'Spreader', 'Heatsink']
    
    # Natural convection temperatures
    T_nat = results['temperature_distribution']['natural']['temperatures']
    if len(T_nat) >= 7:
        T_nat_c = [t - 273.15 for t in T_nat[:7]]
    else:
        T_nat_c = [T_ambient] * 7
    
    ax3.plot(positions, T_nat_c, 'o-', linewidth=2, markersize=10, 
            color='#e74c3c', label='Natural Convection')
    ax3.fill_between(positions, T_ambient, T_nat_c, alpha=0.2, color='#e74c3c')
    
    # Forced air temperatures
    T_frc = results['temperature_distribution']['forced_air']['temperatures']
    if len(T_frc) >= 7:
        T_frc_c = [t - 273.15 for t in T_frc[:7]]
    else:
        T_frc_c = [T_ambient] * 7
    
    ax3.plot(positions, T_frc_c, 's-', linewidth=2, markersize=10,
            color='#2ecc71', label='Forced Air (2 m/s)')
    ax3.fill_between(positions, T_ambient, T_frc_c, alpha=0.2, color='#2ecc71')
    
    ax3.axhline(y=85, color='red', linestyle='--', linewidth=2, label='Max Temp (85°C)')
    ax3.axhline(y=T_ambient, color='blue', linestyle=':', alpha=0.7, label=f'Ambient ({T_ambient:.0f}°C)')
    
    ax3.set_xlabel('Position in Package [mm]', fontsize=12)
    ax3.set_ylabel('Temperature [°C]', fontsize=12)
    ax3.set_title('Temperature Profile Through Package Stack', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper left')
    ax3.set_xticks(positions)
    ax3.set_xticklabels(labels)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cycle5_temperature_profile.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 4: Thermal Resistance Breakdown
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    
    # Get individual layer resistances
    layers_nat = results['temperature_distribution']['natural']['layers']
    layer_names = [l['name'] for l in layers_nat]
    layer_R = [l['R'] for l in layers_nat]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e91e63']
    
    bars = ax4.barh(layer_names[::-1], layer_R[::-1], color=colors[:len(layer_names)][::-1], 
                   edgecolor='black')
    
    for bar, val in zip(bars, layer_R[::-1]):
        ax4.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.3f} K/W', va='center', fontsize=10)
    
    ax4.set_xlabel('Thermal Resistance [K/W]', fontsize=12)
    ax4.set_title('Thermal Resistance Network (Natural Convection)', fontsize=14, fontweight='bold')
    
    R_total = sum(layer_R)
    ax4.axvline(x=R_total, color='red', linestyle='--', 
               label=f'Total: {R_total:.2f} K/W')
    ax4.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cycle5_thermal_resistance_network.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Figure 5: Heatsink Parametric Study
    fig5, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Fin height study
    fin_heights = np.linspace(5, 35, 30)
    R_heights = []
    
    for h in fin_heights:
        temp_params = ThermalFluidParameters()
        temp_params.heatsink_fin_height_mm = h
        temp_params.die_size_mm = results['parameters']['die_size_mm']
        nc = NaturalConvectionModel(temp_params)
        res = nc.heatsink_thermal_resistance(350, 298)
        R_heights.append(res['R_total'])
    
    axes[0].plot(fin_heights, R_heights, 'b-', linewidth=2)
    axes[0].set_xlabel('Fin Height [mm]', fontsize=12)
    axes[0].set_ylabel('Thermal Resistance [K/W]', fontsize=12)
    axes[0].set_title('Effect of Fin Height', fontsize=14, fontweight='bold')
    axes[0].axhline(y=results['natural_convection']['R_total'], color='r', 
                   linestyle='--', label=f"Current: {results['natural_convection']['R_total']:.2f} K/W")
    axes[0].legend()
    
    # Fin pitch study
    fin_pitches = np.linspace(1.5, 5, 30)
    R_pitches = []
    n_fins_list = []
    
    for pitch in fin_pitches:
        temp_params = ThermalFluidParameters()
        temp_params.heatsink_fin_pitch_mm = pitch
        temp_params.die_size_mm = results['parameters']['die_size_mm']
        nc = NaturalConvectionModel(temp_params)
        res = nc.heatsink_thermal_resistance(350, 298)
        R_pitches.append(res['R_total'])
        n_fins_list.append(res['num_fins'])
    
    axes[1].plot(fin_pitches, R_pitches, 'g-', linewidth=2, label='R_total')
    ax1_twin = axes[1].twinx()
    ax1_twin.plot(fin_pitches, n_fins_list, 'r--', linewidth=1.5, label='Num Fins')
    
    axes[1].set_xlabel('Fin Pitch [mm]', fontsize=12)
    axes[1].set_ylabel('Thermal Resistance [K/W]', color='g', fontsize=12)
    ax1_twin.set_ylabel('Number of Fins', color='r', fontsize=12)
    axes[1].set_title('Effect of Fin Pitch', fontsize=14, fontweight='bold')
    axes[1].legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cycle5_heatsink_optimization.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to {output_dir}/")
    print("  - cycle5_cooling_comparison.png")
    print("  - cycle5_tim_comparison.png")
    print("  - cycle5_temperature_profile.png")
    print("  - cycle5_thermal_resistance_network.png")
    print("  - cycle5_heatsink_optimization.png")


def main():
    """Main execution function."""
    print("=" * 70)
    print("CYCLE 5: THERMAL-FLUID DYNAMICS COUPLED SIMULATION")
    print("Mask-Locked Inference Chip")
    print("=" * 70)
    print()
    
    params = ThermalFluidParameters()
    simulator = ThermalFluidSimulator(params)
    
    print("Running thermal-fluid simulation...")
    results = simulator.run_full_simulation()
    
    print("\n" + simulator.generate_report())
    
    print("\nGenerating visualizations...")
    create_visualizations(results)
    
    # Save results
    output_path = "/home/z/my-project/research/cycle5_thermal_fluid_results.json"
    
    def convert_to_native(obj):
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(v) for v in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        else:
            return obj
    
    with open(output_path, 'w') as f:
        json.dump(convert_to_native(results), f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    results = main()
