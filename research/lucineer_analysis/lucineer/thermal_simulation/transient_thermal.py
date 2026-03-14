"""
Transient Thermal Response Simulation
=====================================
Analysis of thermal dynamics during inference bursts and activity patterns.

Models:
- Thermal time constants of different structures
- Burst heating and cooling dynamics
- Thermal accumulation during sustained activity
- Activity-dependent temperature modulation

References:
[1] Cahill, D.G. et al. (2014). Nanoscale thermal transport. II. 2003-2012
    Appl. Phys. Rev. 1, 011305
[2] Cahill, D.G. (1990). Thermal conductivity measurement from 30 to 750 K
    Rev. Sci. Instrum. 61, 802
[3] Costescu, R.M. et al. (2003). Thermal conductance of epitaxial interfaces
    Phys. Rev. B 67, 054302
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

from core_thermal import (ThermalGrid, ThermalSolver, ThermalAnalyzer,
                          SimulationConfig, BoundaryCondition, BoundaryType,
                          HeatSource)
from materials import Material, get_material, calculate_thermal_capacitance


@dataclass
class ThermalTimeConstants:
    """Thermal time constants for a structure."""
    
    # Time constants at different scales
    tau_local: float = 1e-9    # Local heating (nm scale)
    tau_cell: float = 1e-6     # Cell level (μm scale)
    tau_array: float = 1e-3    # Array level (mm scale)
    tau_chip: float = 1.0      # Chip level (cm scale)
    
    @classmethod
    def from_geometry(cls, dimensions: Tuple[float, float, float],
                      thermal_diffusivity: float = 1e-4) -> 'ThermalTimeConstants':
        """
        Estimate time constants from geometry.
        
        τ = L² / (π² α) for 1D diffusion
        τ = L² / (4α) for half-space heating
        
        Args:
            dimensions: (L_x, L_y, L_z) in meters
            thermal_diffusivity: α in m²/s
        """
        L_x, L_y, L_z = dimensions
        alpha = thermal_diffusivity
        
        # Characteristic times for each dimension
        tau_x = L_x**2 / (np.pi**2 * alpha)
        tau_y = L_y**2 / (np.pi**2 * alpha)
        tau_z = L_z**2 / (np.pi**2 * alpha)
        
        # Combined time constant (approximate)
        tau = 1.0 / (1.0/tau_x + 1.0/tau_y + 1.0/tau_z)
        
        return cls(tau_local=tau/1000, tau_cell=tau, tau_array=tau*1000, tau_chip=tau*1e6)


@dataclass
class BurstProfile:
    """Burst activity profile specification."""
    
    burst_duration: float = 1e-6    # seconds
    burst_power: float = 1e-6       # Watts
    idle_duration: float = 9e-6     # seconds
    idle_power: float = 0.1e-6      # Watts
    
    n_bursts: int = 10
    
    def generate_profile(self, dt: float, total_time: float) -> NDArray:
        """Generate time-dependent power profile."""
        n_steps = int(total_time / dt)
        profile = np.zeros(n_steps)
        
        t = 0.0
        for i in range(n_steps):
            t = i * dt
            
            # Find position in burst cycle
            cycle_time = t % (self.burst_duration + self.idle_duration)
            
            if cycle_time < self.burst_duration:
                profile[i] = self.burst_power
            else:
                profile[i] = self.idle_power
        
        return profile
    
    def duty_cycle(self) -> float:
        """Calculate duty cycle."""
        return self.burst_duration / (self.burst_duration + self.idle_duration)
    
    def average_power(self) -> float:
        """Calculate average power."""
        return (self.burst_power * self.burst_duration + 
                self.idle_power * self.idle_duration) / (self.burst_duration + self.idle_duration)


class TransientThermalSimulator:
    """Simulator for transient thermal response."""
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        if config is None:
            config = SimulationConfig(
                nx=50,
                ny=50,
                nz=1,
                dx=10e-9,
                dy=10e-9,
                time_step=1e-9,
                total_time=1e-4,
                save_history=True,
                verbose=False
            )
        
        self.config = config
        self.grid = ThermalGrid(config)
        
        # Set default boundary conditions
        self.grid.bc_bottom = BoundaryCondition(BoundaryType.DIRICHLET, 300.0)
        self.grid.bc_top = BoundaryCondition(BoundaryType.CONVECTIVE, 1e5)
    
    def add_central_heat_source(self, power: float, sigma: float = 3.0):
        """Add Gaussian heat source at center."""
        center_i = self.config.nx // 2
        center_j = self.config.ny // 2
        
        source = HeatSource(
            position=(center_j, center_i),
            power=power,
            shape="gaussian",
            sigma=sigma
        )
        self.grid.add_heat_source(source)
    
    def simulate_step_response(self, power: float = 1e-6) -> Tuple[NDArray, NDArray]:
        """
        Simulate thermal step response.
        
        Power is applied instantaneously and maintained.
        
        Returns:
            Tuple of (time_array, temperature_array)
        """
        self.grid.T.fill(300.0)  # Start at ambient
        self.add_central_heat_source(power)
        
        solver = ThermalSolver(self.grid)
        solver.config.save_history = True
        
        history = solver.solve_transient()
        
        # Extract center temperature over time
        center_i = self.config.nx // 2
        center_j = self.config.ny // 2
        
        times = np.linspace(0, self.config.total_time, len(history))
        temperatures = np.array([h[0, center_j, center_i] for h in history])
        
        return times, temperatures
    
    def simulate_burst_response(self, burst_profile: BurstProfile) -> Tuple[NDArray, NDArray, NDArray]:
        """
        Simulate thermal response to burst activity.
        
        Returns:
            Tuple of (time_array, temperature_array, power_array)
        """
        # Update time parameters
        total_time = burst_profile.n_bursts * (burst_profile.burst_duration + 
                                                burst_profile.idle_duration)
        self.config.total_time = total_time
        self.grid.T.fill(300.0)
        
        # Generate power profile
        power_profile = burst_profile.generate_profile(self.config.time_step, total_time)
        
        # Set up initial heat source (power will be modulated)
        self.add_central_heat_source(1.0)  # Unit power, scaled by profile
        
        # Run transient with time-varying power
        def time_func(t):
            idx = int(t / self.config.time_step)
            if idx < len(power_profile):
                return power_profile[idx]
            return 0.0
        
        solver = ThermalSolver(self.grid)
        solver.config.save_history = True
        
        history = solver.solve_transient(time_func)
        
        # Extract results
        center_i = self.config.nx // 2
        center_j = self.config.ny // 2
        
        times = np.linspace(0, total_time, len(history))
        temperatures = np.array([h[0, center_j, center_i] for h in history])
        
        return times, temperatures, power_profile
    
    def estimate_time_constant(self, times: NDArray, temperatures: NDArray) -> float:
        """
        Estimate thermal time constant from step response.
        
        Fit to: T(t) = T_inf * (1 - exp(-t/τ))
        Or use 63.2% rise time.
        """
        T_initial = temperatures[0]
        T_final = temperatures[-1]
        T_range = T_final - T_initial
        
        # Find time to reach 63.2% of final value
        target_temp = T_initial + 0.632 * T_range
        
        # Find first crossing
        idx = np.argmax(temperatures >= target_temp)
        if idx > 0:
            tau = times[idx]
        else:
            # Curve fitting fallback
            def step_response(t, tau, T_inf):
                return T_initial + T_inf * (1 - np.exp(-t / tau))
            
            try:
                popt, _ = curve_fit(step_response, times, temperatures, 
                                   p0=[1e-6, T_range], maxfev=5000)
                tau = popt[0]
            except:
                tau = 1e-6  # Default
        
        return tau


class ThermalAccumulationAnalyzer:
    """Analyze thermal accumulation over sustained operation."""
    
    def __init__(self, simulator: TransientThermalSimulator):
        self.simulator = simulator
    
    def analyze_sustained_operation(self, 
                                    power_levels: List[float],
                                    durations: List[float]) -> Dict:
        """
        Analyze temperature accumulation under sustained operation.
        
        Args:
            power_levels: Power at each phase
            durations: Duration of each phase
        
        Returns:
            Analysis results including peak temperatures
        """
        results = {
            'phases': [],
            'peak_temperature': 0.0,
            'thermal_overshoot': 0.0
        }
        
        T_ambient = 300.0
        T_current = T_ambient
        
        for power, duration in zip(power_levels, durations):
            # Simulate this phase
            self.simulator.grid.T.fill(T_current)
            self.simulator.grid.clear_heat_sources()
            self.simulator.add_central_heat_source(power)
            self.simulator.config.total_time = duration
            
            solver = ThermalSolver(self.simulator.grid)
            solver.config.save_history = True
            
            history = solver.solve_transient()
            
            # Extract temperatures
            center_i = self.simulator.config.nx // 2
            center_j = self.simulator.config.ny // 2
            temps = [h[0, center_j, center_i] for h in history]
            
            phase_result = {
                'power': power,
                'duration': duration,
                'start_temp': temps[0],
                'end_temp': temps[-1],
                'max_temp': max(temps),
                'min_temp': min(temps)
            }
            
            results['phases'].append(phase_result)
            results['peak_temperature'] = max(results['peak_temperature'], max(temps))
            
            # Update current temperature for next phase
            T_current = temps[-1]
        
        # Calculate thermal overshoot (ratio of peak to steady-state)
        steady_state_power = power_levels[-1] if power_levels else 0
        # Approximate steady-state temperature
        results['thermal_overshoot'] = results['peak_temperature'] - T_current
        
        return results
    
    def find_safe_operating_limits(self,
                                   max_temperature: float = 350.0,
                                   power_range: Tuple[float, float] = (1e-6, 1e-3),
                                   duration_range: Tuple[float, float] = (1e-6, 1e-3)) -> Dict:
        """
        Find safe operating limits that keep temperature below threshold.
        
        Args:
            max_temperature: Maximum allowed temperature
            power_range: Range of powers to test (W)
            duration_range: Range of durations to test (s)
        
        Returns:
            Safe operating region
        """
        results = {
            'safe_region': [],
            'limit_curve': []
        }
        
        powers = np.logspace(np.log10(power_range[0]), np.log10(power_range[1]), 10)
        durations = np.logspace(np.log10(duration_range[0]), np.log10(duration_range[1]), 10)
        
        for power in powers:
            for duration in durations:
                # Simulate this operating point
                self.simulator.config.total_time = duration * 2  # Include cooling
                self.simulator.grid.T.fill(300.0)
                self.simulator.grid.clear_heat_sources()
                self.simulator.add_central_heat_source(power)
                
                # Burst at this power for duration
                profile = BurstProfile(
                    burst_duration=duration,
                    burst_power=power,
                    idle_duration=duration,
                    idle_power=0,
                    n_bursts=1
                )
                
                times, temps, _ = self.simulator.simulate_burst_response(profile)
                peak_temp = max(temps)
                
                safe = peak_temp < max_temperature
                
                results['safe_region'].append({
                    'power': power,
                    'duration': duration,
                    'peak_temp': peak_temp,
                    'safe': safe
                })
                
                if safe and len(results['limit_curve']) < len(powers):
                    # Find boundary
                    pass
        
        return results


class ActivityThermalOptimizer:
    """Optimize activity patterns for thermal management."""
    
    def __init__(self, simulator: TransientThermalSimulator):
        self.simulator = simulator
    
    def optimize_duty_cycle(self,
                           total_power_budget: float,
                           max_temperature: float = 350.0,
                           target_operations: float = 1e9) -> Dict:
        """
        Find optimal duty cycle for maximum operations within thermal budget.
        
        Args:
            total_power_budget: Total power available
            max_temperature: Maximum temperature constraint
            target_operations: Target operations per second
        
        Returns:
            Optimal duty cycle and burst parameters
        """
        results = {
            'tested_duty_cycles': [],
            'optimal': None
        }
        
        duty_cycles = np.linspace(0.1, 1.0, 10)
        
        for duty in duty_cycles:
            # Burst parameters for this duty cycle
            burst_duration = 1e-6  # 1 μs burst
            idle_duration = burst_duration * (1.0/duty - 1.0)
            
            # Peak power during burst
            burst_power = total_power_budget / duty
            
            profile = BurstProfile(
                burst_duration=burst_duration,
                burst_power=burst_power,
                idle_duration=idle_duration,
                idle_power=total_power_budget * 0.1,  # 10% idle power
                n_bursts=100
            )
            
            # Simulate
            times, temps, powers = self.simulator.simulate_burst_response(profile)
            peak_temp = max(temps)
            
            # Operations achieved (proportional to burst power * duty)
            ops_factor = burst_power * duty / total_power_budget
            
            results['tested_duty_cycles'].append({
                'duty_cycle': duty,
                'burst_power': burst_power,
                'peak_temperature': peak_temp,
                'ops_factor': ops_factor,
                'meets_temp_constraint': peak_temp < max_temperature
            })
        
        # Find best duty cycle
        valid = [r for r in results['tested_duty_cycles'] if r['meets_temp_constraint']]
        if valid:
            best = max(valid, key=lambda x: x['ops_factor'])
            results['optimal'] = best
        
        return results
    
    def suggest_cooling_periods(self,
                                activity_pattern: NDArray,
                                max_temperature: float = 350.0) -> List[int]:
        """
        Suggest optimal cooling period insertion points.
        
        Args:
            activity_pattern: Array of activity factors over time
            max_temperature: Maximum temperature constraint
        
        Returns:
            Indices where cooling periods should be inserted
        """
        # Simulate without cooling
        self.simulator.config.total_time = len(activity_pattern) * self.simulator.config.time_step
        
        # Run simulation tracking temperature
        # Insert cooling when temperature approaches limit
        
        cooling_points = []
        T = 300.0
        tau = 1e-6  # Approximate time constant
        
        for i, activity in enumerate(activity_pattern):
            # Simple thermal model
            power = activity * 1e-6  # Scale to power
            dT = (power * 1e5 - (T - 300) / 0.01) * self.simulator.config.time_step
            T += dT
            
            if T > max_temperature * 0.95:
                cooling_points.append(i)
                T = max(300, T - 5)  # Insert cooling
        
        return cooling_points


def run_transient_analysis():
    """Run comprehensive transient thermal analysis."""
    print("=" * 70)
    print("TRANSIENT THERMAL RESPONSE ANALYSIS")
    print("=" * 70)
    
    # 1. Thermal time constants
    print("\n1. THERMAL TIME CONSTANTS")
    print("-" * 40)
    
    dimensions = (500e-9, 500e-9, 100e-9)  # Synapse cell dimensions
    alpha_si = get_material('silicon').thermal_diffusivity
    alpha_sio2 = get_material('sio2').thermal_diffusivity
    
    tc_si = ThermalTimeConstants.from_geometry(dimensions, alpha_si)
    tc_sio2 = ThermalTimeConstants.from_geometry(dimensions, alpha_sio2)
    
    print(f"Silicon cell ({dimensions[0]*1e9:.0f} x {dimensions[1]*1e9:.0f} x {dimensions[2]*1e9:.0f} nm):")
    print(f"  τ_cell = {tc_si.tau_cell:.2e} s = {tc_si.tau_cell*1e6:.2f} μs")
    
    print(f"\nSiO2 region:")
    print(f"  τ_cell = {tc_sio2.tau_cell:.2e} s = {tc_sio2.tau_cell*1e6:.2f} μs")
    
    # 2. Step response
    print("\n2. STEP RESPONSE ANALYSIS")
    print("-" * 40)
    
    simulator = TransientThermalSimulator()
    simulator.config.total_time = 1e-4
    simulator.config.time_step = 1e-9
    
    times, temps = simulator.simulate_step_response(power=1e-6)
    
    tau_measured = simulator.estimate_time_constant(times, temps)
    
    print(f"Applied power: 1 μW")
    print(f"Initial temperature: {temps[0]:.2f} K")
    print(f"Final temperature: {temps[-1]:.2f} K")
    print(f"Temperature rise: {temps[-1] - temps[0]:.2f} K")
    print(f"Time constant (measured): {tau_measured:.2e} s = {tau_measured*1e6:.2f} μs")
    
    # 3. Burst response
    print("\n3. BURST ACTIVITY RESPONSE")
    print("-" * 40)
    
    burst_profile = BurstProfile(
        burst_duration=1e-6,
        burst_power=5e-6,
        idle_duration=9e-6,
        idle_power=0.5e-6,
        n_bursts=20
    )
    
    simulator.config.total_time = burst_profile.n_bursts * (burst_profile.burst_duration + 
                                                             burst_profile.idle_duration)
    
    times, temps, powers = simulator.simulate_burst_response(burst_profile)
    
    print(f"Burst parameters:")
    print(f"  Burst duration: {burst_profile.burst_duration*1e6:.1f} μs")
    print(f"  Burst power: {burst_profile.burst_power*1e6:.1f} μW")
    print(f"  Idle duration: {burst_profile.idle_duration*1e6:.1f} μs")
    print(f"  Duty cycle: {burst_profile.duty_cycle():.1%}")
    print(f"  Average power: {burst_profile.average_power()*1e6:.2f} μW")
    print(f"\nThermal response:")
    print(f"  Peak temperature: {max(temps):.2f} K")
    print(f"  Temperature swing: {max(temps) - min(temps):.2f} K")
    
    # 4. Safe operating limits
    print("\n4. SAFE OPERATING LIMITS (T_max = 350 K)")
    print("-" * 40)
    
    analyzer = ThermalAccumulationAnalyzer(simulator)
    limits = analyzer.find_safe_operating_limits(
        max_temperature=350.0,
        power_range=(1e-7, 1e-4),
        duration_range=(1e-6, 1e-3)
    )
    
    safe_ops = [r for r in limits['safe_region'] if r['safe']]
    unsafe_ops = [r for r in limits['safe_region'] if not r['safe']]
    
    print(f"Safe operating points tested: {len(safe_ops)}")
    print(f"Unsafe operating points tested: {len(unsafe_ops)}")
    
    if safe_ops:
        max_power = max(r['power'] for r in safe_ops)
        max_duration = max(r['duration'] for r in safe_ops)
        print(f"Maximum safe power: {max_power*1e6:.2f} μW")
        print(f"Maximum safe burst duration: {max_duration*1e6:.2f} μs")
    
    # 5. Duty cycle optimization
    print("\n5. DUTY CYCLE OPTIMIZATION")
    print("-" * 40)
    
    optimizer = ActivityThermalOptimizer(simulator)
    duty_results = optimizer.optimize_duty_cycle(
        total_power_budget=1e-5,
        max_temperature=350.0
    )
    
    print(f"{'Duty Cycle':<15} {'Burst Power':<15} {'Peak Temp':<15} {'Valid':<10}")
    print("-" * 55)
    for r in duty_results['tested_duty_cycles']:
        print(f"{r['duty_cycle']:<15.1%} {r['burst_power']*1e6:<15.2f} μW "
              f"{r['peak_temperature']:<15.2f} K {str(r['meets_temp_constraint']):<10}")
    
    if duty_results['optimal']:
        opt = duty_results['optimal']
        print(f"\nOptimal duty cycle: {opt['duty_cycle']:.1%}")
        print(f"  Peak power during burst: {opt['burst_power']*1e6:.2f} μW")
        print(f"  Peak temperature: {opt['peak_temperature']:.2f} K")
    
    return {
        'time_constants': {'silicon': tc_si, 'sio2': tc_sio2},
        'step_response': {'times': times, 'temps': temps, 'tau': tau_measured},
        'burst_response': {'times': times, 'temps': temps, 'powers': powers},
        'duty_optimization': duty_results
    }


if __name__ == "__main__":
    results = run_transient_analysis()
