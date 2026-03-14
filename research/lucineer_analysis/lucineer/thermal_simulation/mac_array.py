"""
MAC Array Thermal Simulation
============================
Thermal modeling for Multiply-Accumulate arrays in neuromorphic chips.

Models heat generation in:
- Ternary MAC units (+1, 0, -1 operations)
- Memory cells (synaptic weights)
- Interconnect (data movement)
- Accumulation circuits

References:
[1] Horowitz, M. (2014). Computing's energy problem (ISSCC)
[2] Chen, Y.H. (2016). Eyeriss: A spatial architecture for neural networks
[3] Sze, V. (2017). Efficient processing of deep neural networks
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from core_thermal import (ThermalGrid, ThermalSolver, ThermalAnalyzer,
                          SimulationConfig, BoundaryCondition, BoundaryType,
                          HeatSource)
from materials import get_material, Material


class MACOperation(Enum):
    """MAC operation types."""
    POSITIVE = 1    # +1 operation
    ZERO = 0        # Idle
    NEGATIVE = -1   # -1 operation


@dataclass
class MACCell:
    """Single MAC cell specification."""
    x_pos: int  # Grid x position
    y_pos: int  # Grid y position
    
    # Power consumption
    power_mult: float = 0.1e-12  # 0.1 pJ per multiply
    power_accum: float = 0.05e-12  # 0.05 pJ per accumulate
    power_idle: float = 0.01e-12  # 0.01 pJ idle leakage
    
    # Geometry
    width: float = 100e-9   # 100 nm
    height: float = 100e-9  # 100 nm
    
    # Activity
    activity_factor: float = 0.5  # Fraction of time active
    
    def power_consumption(self, operation: MACOperation, frequency: float) -> float:
        """Calculate power for given operation at frequency."""
        if operation == MACOperation.ZERO:
            return self.power_idle * frequency
        else:
            return (self.power_mult + self.power_accum) * frequency


@dataclass
class MACArrayConfig:
    """Configuration for MAC array thermal simulation."""
    # Array dimensions
    n_rows: int = 32
    n_cols: int = 32
    
    # Cell spacing
    cell_pitch_x: float = 150e-9  # 150 nm pitch
    cell_pitch_y: float = 150e-9
    
    # Grid resolution
    grid_per_cell: int = 5  # Grid points per cell
    
    # Operating frequency
    clock_frequency: float = 1e9  # 1 GHz
    
    # Activity patterns
    activity_pattern: str = "uniform"  # "uniform", "burst", "random", "custom"
    burst_duty_cycle: float = 0.1  # For burst mode
    
    # Power parameters
    energy_per_mac: float = 0.1e-12  # 0.1 pJ per MAC (state-of-art)
    
    # Layer stack
    include_interconnect: bool = True
    interconnect_layers: int = 4


class MACArrayThermalModel:
    """
    Thermal model for MAC array.
    
    Models:
    - Heat generation from MAC operations
    - Interconnect heating
    - Memory access power
    - Thermal coupling between cells
    """
    
    def __init__(self, config: MACArrayConfig):
        self.config = config
        self.cells: Dict[Tuple[int, int], MACCell] = {}
        
        # Initialize cells
        for i in range(config.n_rows):
            for j in range(config.n_cols):
                self.cells[(i, j)] = MACCell(x_pos=i, y_pos=j)
        
        # Activity map
        self.activity_map = np.ones((config.n_rows, config.n_cols)) * 0.5
        
        # Power map
        self.power_map = np.zeros((config.n_rows, config.n_cols))
        
        # Initialize thermal grid
        self._init_thermal_grid()
    
    def _init_thermal_grid(self):
        """Initialize thermal simulation grid."""
        cfg = self.config
        
        # Grid size
        nx = cfg.n_cols * cfg.grid_per_cell
        ny = cfg.n_rows * cfg.grid_per_cell
        
        # Create simulation config
        sim_config = SimulationConfig(
            nx=nx,
            ny=ny,
            nz=1,
            dx=cfg.cell_pitch_x / cfg.grid_per_cell,
            dy=cfg.cell_pitch_y / cfg.grid_per_cell,
            convergence_tolerance=1e-5,
            verbose=False
        )
        
        self.thermal_grid = ThermalGrid(sim_config)
        self.thermal_solver = ThermalSolver(self.thermal_grid)
        self.thermal_analyzer = ThermalAnalyzer(self.thermal_grid)
        
        # Set boundary conditions
        self.thermal_grid.bc_bottom = BoundaryCondition(
            BoundaryType.DIRICHLET, 300.0)
        self.thermal_grid.bc_top = BoundaryCondition(
            BoundaryType.CONVECTIVE, 1e5)  # h = 1e5 W/m²K
    
    def set_activity_pattern(self, pattern: str, **kwargs):
        """Set activity pattern across the array."""
        cfg = self.config
        
        if pattern == "uniform":
            self.activity_map = np.ones((cfg.n_rows, cfg.n_cols)) * kwargs.get('activity', 0.5)
        
        elif pattern == "burst":
            # Center region has higher activity
            center_i, center_j = cfg.n_rows // 2, cfg.n_cols // 2
            radius = min(cfg.n_rows, cfg.n_cols) // 4
            
            for i in range(cfg.n_rows):
                for j in range(cfg.n_cols):
                    dist = np.sqrt((i - center_i)**2 + (j - center_j)**2)
                    if dist < radius:
                        self.activity_map[i, j] = kwargs.get('burst_activity', 0.9)
                    else:
                        self.activity_map[i, j] = kwargs.get('background_activity', 0.1)
        
        elif pattern == "random":
            self.activity_map = np.random.uniform(
                kwargs.get('min_activity', 0.1),
                kwargs.get('max_activity', 0.9),
                (cfg.n_rows, cfg.n_cols)
            )
        
        elif pattern == "gradient":
            # Activity gradient across array
            for i in range(cfg.n_rows):
                for j in range(cfg.n_cols):
                    self.activity_map[i, j] = (i + j) / (cfg.n_rows + cfg.n_cols)
        
        elif pattern == "checkerboard":
            for i in range(cfg.n_rows):
                for j in range(cfg.n_cols):
                    self.activity_map[i, j] = kwargs.get('high_activity', 0.8) if \
                        (i + j) % 2 == 0 else kwargs.get('low_activity', 0.2)
        
        elif pattern == "custom":
            self.activity_map = kwargs.get('activity_map', self.activity_map)
        
        self.config.activity_pattern = pattern
    
    def calculate_power_map(self):
        """Calculate power consumption per cell."""
        cfg = self.config
        
        for i in range(cfg.n_rows):
            for j in range(cfg.n_cols):
                activity = self.activity_map[i, j]
                power = cfg.energy_per_mac * cfg.clock_frequency * activity
                self.power_map[i, j] = power
    
    def apply_heat_sources(self):
        """Apply heat sources to thermal grid."""
        cfg = self.config
        self.thermal_grid.clear_heat_sources()
        
        for i in range(cfg.n_rows):
            for j in range(cfg.n_cols):
                # Cell position in grid
                gi = j * cfg.grid_per_cell + cfg.grid_per_cell // 2
                gj = i * cfg.grid_per_cell + cfg.grid_per_cell // 2
                
                # Add heat source
                source = HeatSource(
                    position=(gj, gi),
                    power=self.power_map[i, j],
                    shape="gaussian",
                    sigma=cfg.grid_per_cell / 2
                )
                self.thermal_grid.add_heat_source(source)
    
    def simulate(self) -> NDArray:
        """Run thermal simulation."""
        self.calculate_power_map()
        self.apply_heat_sources()
        
        # Solve steady-state
        T = self.thermal_solver.solve_steady_state_matrix()
        
        return T
    
    def simulate_transient(self, burst_profile: Optional[NDArray] = None) -> List[NDArray]:
        """
        Simulate transient thermal response.
        
        Args:
            burst_profile: Array of activity factors over time
        """
        if burst_profile is not None:
            # Time-varying activity
            def time_func(t):
                idx = int(t / self.config.clock_frequency)
                if idx < len(burst_profile):
                    return burst_profile[idx]
                return 0.0
            
            self.thermal_solver.config.save_history = True
            return self.thermal_solver.solve_transient(time_func)
        else:
            return [self.simulate()]
    
    def get_cell_temperatures(self, T: NDArray) -> NDArray:
        """Extract temperature at each cell location."""
        cfg = self.config
        cell_temps = np.zeros((cfg.n_rows, cfg.n_cols))
        
        for i in range(cfg.n_rows):
            for j in range(cfg.n_cols):
                gi = j * cfg.grid_per_cell + cfg.grid_per_cell // 2
                gj = i * cfg.grid_per_cell + cfg.grid_per_cell // 2
                
                # Average over cell area
                x_start = j * cfg.grid_per_cell
                x_end = (j + 1) * cfg.grid_per_cell
                y_start = i * cfg.grid_per_cell
                y_end = (i + 1) * cfg.grid_per_cell
                
                cell_temps[i, j] = np.mean(T[0, y_start:y_end, x_start:x_end])
        
        return cell_temps
    
    def thermal_coupling_coefficient(self, i1: int, j1: int, 
                                      i2: int, j2: int) -> float:
        """
        Calculate thermal coupling between two cells.
        
        Defined as temperature rise at cell 2 due to power at cell 1.
        """
        # Run simulation with power only at cell 1
        original_power = self.power_map.copy()
        self.power_map.fill(0)
        self.power_map[i1, j1] = original_power[i1, j1]
        
        T = self.simulate()
        
        # Temperature at cell 2
        cfg = self.config
        gj2 = i2 * cfg.grid_per_cell + cfg.grid_per_cell // 2
        gi2 = j2 * cfg.grid_per_cell + cfg.grid_per_cell // 2
        T2 = T[0, gj2, gi2] - 300.0  # Temperature rise
        
        # Restore power map
        self.power_map = original_power
        
        if self.power_map[i1, j1] > 0:
            return T2 / self.power_map[i1, j1]  # K/W
        return 0.0
    
    def thermal_coupling_matrix(self) -> NDArray:
        """Calculate full thermal coupling matrix."""
        n = self.config.n_rows * self.config.n_cols
        coupling = np.zeros((n, n))
        
        for i1 in range(self.config.n_rows):
            for j1 in range(self.config.n_cols):
                for i2 in range(self.config.n_rows):
                    for j2 in range(self.config.n_cols):
                        idx1 = i1 * self.config.n_cols + j1
                        idx2 = i2 * self.config.n_cols + j2
                        
                        if idx1 != idx2:
                            # Only calculate for nearby cells
                            dist = np.sqrt((i1-i2)**2 + (j1-j2)**2)
                            if dist < 5:  # Only nearby coupling
                                coupling[idx1, idx2] = self.thermal_coupling_coefficient(
                                    i1, j1, i2, j2)
        
        return coupling
    
    def power_density(self) -> float:
        """Calculate total power density."""
        total_power = np.sum(self.power_map)
        area = (self.config.n_rows * self.config.cell_pitch_y * 
                self.config.n_cols * self.config.cell_pitch_x)
        return total_power / area  # W/m²


class MACArrayOptimizer:
    """Optimization tools for MAC array thermal design."""
    
    def __init__(self, model: MACArrayThermalModel):
        self.model = model
    
    def optimize_spacing(self, max_temp_rise: float = 10.0) -> Dict:
        """
        Find minimum spacing to keep temperature rise below threshold.
        
        Args:
            max_temp_rise: Maximum allowed temperature rise in K
        
        Returns:
            Dictionary with optimal spacing and results
        """
        results = {
            'spacing_tested': [],
            'max_temperature': [],
            'optimal_spacing': None
        }
        
        # Test different spacing multipliers
        for multiplier in np.arange(1.0, 3.0, 0.25):
            # Update cell pitch
            original_pitch_x = self.model.config.cell_pitch_x
            original_pitch_y = self.model.config.cell_pitch_y
            
            self.model.config.cell_pitch_x = original_pitch_x * multiplier
            self.model.config.cell_pitch_y = original_pitch_y * multiplier
            
            # Re-run simulation
            T = self.model.simulate()
            max_temp = np.max(T) - 300.0
            
            results['spacing_tested'].append(multiplier)
            results['max_temperature'].append(max_temp)
            
            # Restore original pitch
            self.model.config.cell_pitch_x = original_pitch_x
            self.model.config.cell_pitch_y = original_pitch_y
            
            if max_temp < max_temp_rise:
                results['optimal_spacing'] = multiplier
                break
        
        return results
    
    def optimize_activity_distribution(self, total_activity: float) -> NDArray:
        """
        Find activity distribution that minimizes peak temperature.
        
        Uses gradient descent to optimize activity distribution.
        
        Args:
            total_activity: Sum of all activity factors
        
        Returns:
            Optimized activity map
        """
        # Initialize with uniform distribution
        n_cells = self.model.config.n_rows * self.model.config.n_cols
        uniform_activity = total_activity / n_cells
        self.model.set_activity_pattern("uniform", activity=uniform_activity)
        
        best_activity = self.model.activity_map.copy()
        T = self.model.simulate()
        best_max_temp = np.max(T) - 300.0
        
        # Iterative optimization
        for iteration in range(10):
            # Find hottest cells
            cell_temps = self.model.get_cell_temperatures(T)
            hot_cells = np.argsort(cell_temps.flatten())[::-1][:n_cells // 4]
            
            # Reduce activity in hot cells, increase in cool cells
            new_activity = self.model.activity_map.copy()
            for idx in hot_cells:
                i, j = idx // self.model.config.n_cols, idx % self.model.config.n_cols
                new_activity[i, j] *= 0.8
            
            # Normalize to maintain total activity
            new_activity = new_activity * total_activity / np.sum(new_activity)
            
            # Test new distribution
            self.model.set_activity_pattern("custom", activity_map=new_activity)
            T_new = self.model.simulate()
            max_temp_new = np.max(T_new) - 300.0
            
            if max_temp_new < best_max_temp:
                best_max_temp = max_temp_new
                best_activity = new_activity.copy()
                T = T_new
            else:
                break
        
        return best_activity


def create_mac_array_simulation():
    """Create and run MAC array thermal simulation."""
    # Configuration
    config = MACArrayConfig(
        n_rows=16,
        n_cols=16,
        cell_pitch_x=150e-9,
        cell_pitch_y=150e-9,
        grid_per_cell=4,
        clock_frequency=1e9,
        energy_per_mac=0.5e-12  # 0.5 pJ (conservative)
    )
    
    # Create model
    model = MACArrayThermalModel(config)
    
    # Set activity pattern
    model.set_activity_pattern("burst", burst_activity=0.9, background_activity=0.1)
    
    # Run simulation
    T = model.simulate()
    
    # Analyze
    print(model.thermal_analyzer.report())
    
    # Cell temperatures
    cell_temps = model.get_cell_temperatures(T)
    print(f"\nCell temperature statistics:")
    print(f"  Max: {np.max(cell_temps):.2f} K")
    print(f"  Min: {np.min(cell_temps):.2f} K")
    print(f"  Mean: {np.mean(cell_temps):.2f} K")
    print(f"  Std: {np.std(cell_temps):.2f} K")
    
    # Power density
    print(f"\nPower density: {model.power_density():.2e} W/m²")
    print(f"Power density: {model.power_density() / 1e4:.2f} W/cm²")
    
    return model, T


if __name__ == "__main__":
    model, T = create_mac_array_simulation()
