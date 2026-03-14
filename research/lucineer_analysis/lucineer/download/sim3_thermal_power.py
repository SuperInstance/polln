#!/usr/bin/env python3
"""
TernaryAir Simulation Framework
Iteration 3: Thermal/Power Dynamics Simulation

Simulates chip-level thermal and power behavior:
- Thermal dynamics under various workloads
- Power consumption patterns
- Thermal throttling analysis
- Cooling solution requirements

Author: Casey DiGennaro
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import List, Dict
import matplotlib.pyplot as plt

@dataclass
class ThermalModel:
    """Thermal model parameters for 28nm chip"""
    die_area_mm2: float = 25.0
    thickness_um: float = 300
    silicon_thermal_conductivity: float = 150  # W/mK
    junction_to_ambient_C_per_W: float = 35  # °C/W (no heatsink)
    junction_to_case_C_per_W: float = 2.5
    thermal_mass_J_per_K: float = 0.015  # J/K for silicon die
    max_junction_temp_C: float = 125.0
    ambient_temp_C: float = 25.0

@dataclass
class PowerModel:
    """Power model parameters"""
    tdp_w: float = 4.0
    leakage_w: float = 0.05
    dynamic_range: tuple = (0.1, 1.0)  # Fraction of TDP

class ThermalSimulator:
    """Simulates thermal dynamics of the chip"""
    
    def __init__(self, thermal: ThermalModel, power: PowerModel):
        self.thermal = thermal
        self.power = power
        self.temp_history = []
        self.power_history = []
    
    def simulate_transient(self, duration_ms: float = 1000, dt_ms: float = 1,
                          workload_profile: List[float] = None) -> Dict:
        """
        Simulate transient thermal behavior
        
        workload_profile: list of power fractions (0.0 to 1.0) over time
        """
        if workload_profile is None:
            # Default: idle → burst → sustained → idle
            workload_profile = (
                [0.1] * 100 +           # Idle
                [1.0] * 50 +            # Burst
                [0.8] * 300 +           # Sustained
                [0.1] * 100 +           # Idle
                [0.6] * 200 +           # Medium load
                [0.1] * 250             # Cool down
            )
        
        n_steps = int(duration_ms / dt_ms)
        temps = np.zeros(n_steps)
        powers = np.zeros(n_steps)
        temps[0] = self.thermal.ambient_temp_C
        
        for i in range(1, n_steps):
            # Get workload fraction
            workload_idx = min(i, len(workload_profile) - 1)
            workload_frac = workload_profile[workload_idx]
            
            # Calculate power
            dynamic_power = self.power.tdp_w * workload_frac * self.power.dynamic_range[1]
            static_power = self.power.leakage_w
            total_power = dynamic_power + static_power
            powers[i] = total_power
            
            # Thermal dynamics (lumped capacitance model)
            # dT/dt = (P - (T - T_amb)/R_th) / C_th
            heat_generated = total_power
            heat_dissipated = (temps[i-1] - self.thermal.ambient_temp_C) / self.thermal.junction_to_ambient_C_per_W
            temp_rate = (heat_generated - heat_dissipated) / self.thermal.thermal_mass_J_per_K
            
            temps[i] = temps[i-1] + temp_rate * (dt_ms / 1000)
        
        return {
            'time_ms': np.arange(n_steps) * dt_ms,
            'temperature_C': temps,
            'power_W': powers,
            'workload': np.array([workload_profile[min(i, len(workload_profile)-1)] for i in range(n_steps)]),
            'max_temp': np.max(temps),
            'steady_state_temp': temps[-100:].mean(),
            'throttling_required': np.max(temps) > self.thermal.max_junction_temp_C,
        }
    
    def analyze_cooling_requirements(self, target_temp_C: float = 85) -> Dict:
        """Analyze cooling solution requirements"""
        # Required thermal resistance
        power_budget = self.power.tdp_w
        temp_rise = target_temp_C - self.thermal.ambient_temp_C
        required_theta = temp_rise / power_budget
        
        # Current vs required
        current_theta = self.thermal.junction_to_ambient_C_per_W
        
        return {
            'target_temp_C': target_temp_C,
            'required_theta_JA_C_per_W': required_theta,
            'current_theta_JA_C_per_W': current_theta,
            'improvement_needed': current_theta - required_theta,
            'heatsink_required': current_theta > required_theta,
            'recommended_solution': self._recommend_cooling(required_theta),
        }
    
    def _recommend_cooling(self, required_theta: float) -> str:
        if required_theta >= 25:
            return "Passive PCB cooling sufficient"
        elif required_theta >= 15:
            return "Small aluminum heatsink recommended"
        elif required_theta >= 8:
            return "Medium heatsink + thermal pad required"
        else:
            return "Active cooling (fan) recommended"


class PowerSimulator:
    """Simulates power consumption patterns"""
    
    def __init__(self, tdp_w: float = 4.0):
        self.tdp_w = tdp_w
    
    def analyze_inference_power(self, tokens_per_second: int = 100) -> Dict:
        """Analyze power consumption during inference"""
        # Power breakdown
        rau_power = self.tdp_w * 0.40  # 40% for RAU array
        sram_power = self.tdp_w * 0.25  # 25% for SRAM
        io_power = self.tdp_w * 0.15    # 15% for I/O
        control_power = self.tdp_w * 0.10  # 10% for control
        leakage = self.tdp_w * 0.10     # 10% leakage
        
        # Energy per token
        energy_per_token_mj = self.tdp_w / tokens_per_second * 1000
        
        return {
            'total_power_W': self.tdp_w,
            'power_breakdown': {
                'rau_array_W': rau_power,
                'sram_W': sram_power,
                'io_W': io_power,
                'control_W': control_power,
                'leakage_W': leakage,
            },
            'tokens_per_second': tokens_per_second,
            'energy_per_token_mJ': energy_per_token_mj,
            'energy_per_token_uJ': energy_per_token_mj * 1000,
        }
    
    def analyze_usb_power_budget(self) -> Dict:
        """Analyze USB power budget compatibility"""
        usb_2_5W = 2.5
        usb_3_4_5W = 4.5
        usb_pd_5W = 5.0
        usb_pd_9W = 9.0
        
        return {
            'chip_tdp_W': self.tdp_w,
            'usb_2_0_5V': {
                'available_W': usb_2_5W,
                'sufficient': self.tdp_w <= usb_2_5W,
                'headroom_W': usb_2_5W - self.tdp_w,
            },
            'usb_3_0_5V': {
                'available_W': usb_3_4_5W,
                'sufficient': self.tdp_w <= usb_3_4_5W,
                'headroom_W': usb_3_4_5W - self.tdp_w,
            },
            'usb_pd_5V': {
                'available_W': usb_pd_5W,
                'sufficient': self.tdp_w <= usb_pd_5W,
                'headroom_W': usb_pd_5W - self.tdp_w,
            },
            'recommended_usb': 'USB 3.0 (5V, 900mA)' if self.tdp_w <= 4.5 else 'USB PD (5V, 1A)',
        }


def run_iteration_3():
    """Run thermal/power dynamics simulation"""
    
    print("=" * 70)
    print("TERNARYAIR SIMULATION FRAMEWORK")
    print("Iteration 3: Thermal/Power Dynamics Simulation")
    print("=" * 70)
    
    # Initialize models
    thermal_model = ThermalModel()
    power_model = PowerModel(tdp_w=4.0)
    
    # Run thermal simulation
    thermal_sim = ThermalSimulator(thermal_model, power_model)
    transient_result = thermal_sim.simulate_transient(duration_ms=1000)
    
    # Power analysis
    power_sim = PowerSimulator(tdp_w=4.0)
    inference_power = power_sim.analyze_inference_power(tokens_per_second=100)
    usb_analysis = power_sim.analyze_usb_power_budget()
    
    # Cooling analysis
    cooling_analysis = thermal_sim.analyze_cooling_requirements(target_temp_C=85)
    
    # Compile results
    results = {
        'thermal_transient': {
            'max_temp_C': float(transient_result['max_temp']),
            'steady_state_temp_C': float(transient_result['steady_state_temp']),
            'throttling_required': transient_result['throttling_required'],
        },
        'power_analysis': inference_power,
        'usb_power_budget': usb_analysis,
        'cooling_requirements': cooling_analysis,
    }
    
    # Print results
    print("\n📊 Thermal Analysis Results")
    print("-" * 50)
    print(f"Max Temperature: {transient_result['max_temp']:.1f}°C")
    print(f"Steady State Temperature: {transient_result['steady_state_temp']:.1f}°C")
    print(f"Max Junction Temp Limit: {thermal_model.max_junction_temp_C}°C")
    print(f"Throttling Required: {'Yes ⚠️' if transient_result['throttling_required'] else 'No ✅'}")
    
    print("\n🔋 Power Breakdown")
    print("-" * 50)
    tdp = power_model.tdp_w
    for component, power in inference_power['power_breakdown'].items():
        print(f"{component.replace('_', ' ').title():<20}: {power:.2f} W ({power/tdp*100:.0f}%)")
    print(f"{'Total TDP':<20}: {tdp:.2f} W")
    print(f"\nEnergy per Token: {inference_power['energy_per_token_uJ']:.1f} μJ")
    
    print("\n🔌 USB Power Budget Analysis")
    print("-" * 50)
    print(f"Chip TDP: {tdp} W")
    print(f"USB 2.0 (5V, 500mA): {usb_analysis['usb_2_0_5V']['sufficient'] and '✅ Sufficient' or '❌ Insufficient'}")
    print(f"USB 3.0 (5V, 900mA): {usb_analysis['usb_3_0_5V']['sufficient'] and '✅ Sufficient' or '❌ Insufficient'}")
    print(f"Recommended: {usb_analysis['recommended_usb']}")
    
    print("\n❄️ Cooling Requirements")
    print("-" * 50)
    print(f"Target Temperature: {cooling_analysis['target_temp_C']}°C")
    print(f"Current θ_JA: {cooling_analysis['current_theta_JA_C_per_W']:.1f} °C/W")
    print(f"Required θ_JA: {cooling_analysis['required_theta_JA_C_per_W']:.1f} °C/W")
    print(f"Heatsink Required: {'Yes' if cooling_analysis['heatsink_required'] else 'No'}")
    print(f"Recommendation: {cooling_analysis['recommended_solution']}")
    
    # Generate visualizations
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Temperature transient
    ax1 = axes[0, 0]
    time = transient_result['time_ms']
    temp = transient_result['temperature_C']
    ax1.plot(time, temp, 'r-', linewidth=2, label='Junction Temp')
    ax1.axhline(y=thermal_model.max_junction_temp_C, color='darkred', linestyle='--', label=f'Max Limit ({thermal_model.max_junction_temp_C}°C)')
    ax1.axhline(y=85, color='orange', linestyle='--', label='Target (85°C)')
    ax1.fill_between(time, 0, temp, alpha=0.3, color='red')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Junction Temperature Transient')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_xlim(0, time[-1])
    ax1.set_ylim(0, 100)
    
    # 2. Power breakdown pie
    ax2 = axes[0, 1]
    labels = list(inference_power['power_breakdown'].keys())
    sizes = list(inference_power['power_breakdown'].values())
    colors = ['#3498DB', '#2ECC71', '#E74C3C', '#9B59B6', '#F39C12']
    explode = (0.05, 0, 0, 0, 0)
    ax2.pie(sizes, explode=explode, labels=[l.replace('_', '\n') for l in labels], 
            colors=colors, autopct='%1.0f%%', startangle=90)
    ax2.set_title(f'Power Distribution (Total: {tdp}W)')
    
    # 3. Workload and power
    ax3 = axes[1, 0]
    ax3_twin = ax3.twinx()
    
    ax3.fill_between(time, 0, transient_result['workload'] * 100, alpha=0.3, color='blue', label='Workload')
    ax3.set_ylabel('Workload (%)', color='blue')
    ax3.tick_params(axis='y', labelcolor='blue')
    ax3.set_ylim(0, 110)
    
    ax3_twin.plot(time, transient_result['power_W'], 'r-', linewidth=2, label='Power')
    ax3_twin.set_ylabel('Power (W)', color='red')
    ax3_twin.tick_params(axis='y', labelcolor='red')
    ax3_twin.set_ylim(0, 5)
    
    ax3.set_xlabel('Time (ms)')
    ax3.set_title('Workload and Power Consumption')
    ax3.grid(alpha=0.3)
    
    # 4. USB power budget
    ax4 = axes[1, 1]
    usb_types = ['USB 2.0\n(500mA)', 'USB 3.0\n(900mA)', 'USB PD\n(1A)', 'USB PD\n(1.8A)']
    usb_power = [2.5, 4.5, 5.0, 9.0]
    colors_usb = ['#E74C3C', '#2ECC71', '#2ECC71', '#2ECC71']
    
    bars = ax4.bar(usb_types, usb_power, color=colors_usb, alpha=0.7, label='Available')
    ax4.axhline(y=tdp, color='red', linestyle='-', linewidth=2, label=f'Chip TDP ({tdp}W)')
    
    for bar, power in zip(bars, usb_power):
        status = '✓' if power >= tdp else '✗'
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                f'{power}W {status}', ha='center', va='bottom', fontsize=10)
    
    ax4.set_ylabel('Power (W)')
    ax4.set_title('USB Power Budget Compatibility')
    ax4.legend()
    ax4.set_ylim(0, 10)
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/sim3_thermal_power.png', dpi=150)
    print("\n✅ Saved: /home/z/my-project/download/sim3_thermal_power.png")
    
    # Save JSON
    with open('/home/z/my-project/download/sim3_thermal_power.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✅ Saved: /home/z/my-project/download/sim3_thermal_power.json")
    
    return results


if __name__ == "__main__":
    run_iteration_3()
