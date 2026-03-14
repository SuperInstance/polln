"""
Spine-Inspired Geometry Models
==============================
Thermal analysis of synapse-inspired geometries for neuromorphic chips.

Compares thermal performance of:
1. Mushroom spine cells (large head, narrow neck)
2. Thin spine cells (small head, thin long neck)
3. Stubby spine cells (short, wide)
4. Optimized hybrid geometries

The spine neck provides thermal isolation - heat is confined to the active
region (head) while the neck limits spread to neighboring structures.

References:
[1] Harris, K.M. (1999). Structure, development, and plasticity of dendritic spines
    Curr. Opin. Neurobiol. 9, 343-348
[2] Bourne, J.N. & Harris, K.M. (2008). Balancing structure and function at synapses
    Trends Neurosci. 31, 667-673
[3] Tonnesen, J. & Nagerl, U.V. (2016). Spine neck plasticity regulates compartmentalization
    Nat. Neurosci. 19, 1576-1583
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.collections import PatchCollection

from core_thermal import (ThermalGrid, ThermalSolver, ThermalAnalyzer,
                          SimulationConfig, BoundaryCondition, BoundaryType,
                          HeatSource)
from materials import Material, get_material


class GeometryType(Enum):
    """Spine-inspired geometry types."""
    MUSHROOM = "mushroom"
    THIN = "thin"
    STUBBY = "stubby"
    FILAPODIA = "filapodia"
    CUSTOM = "custom"


@dataclass
class SpineGeometry:
    """
    Geometric specification of a spine-inspired cell structure.
    
    The geometry consists of:
    - Head: Active region (heat source)
    - Neck: Thermal isolation region
    - Base: Connection to substrate
    """
    
    geometry_type: GeometryType = GeometryType.MUSHROOM
    
    # Head dimensions
    head_width: float = 300e-9   # 300 nm
    head_height: float = 200e-9  # 200 nm
    
    # Neck dimensions
    neck_width: float = 100e-9   # 100 nm
    neck_height: float = 150e-9  # 150 nm
    
    # Base dimensions
    base_width: float = 200e-9   # 200 nm
    base_height: float = 50e-9   # 50 nm
    
    # Materials (by name)
    head_material: str = "silicon"
    neck_material: str = "sio2"  # Low-k for isolation
    base_material: str = "copper"  # Heat spreading
    
    @classmethod
    def mushroom_spine(cls, scale: float = 1.0) -> 'SpineGeometry':
        """Create mushroom spine geometry (large head, narrow neck)."""
        return cls(
            geometry_type=GeometryType.MUSHROOM,
            head_width=400e-9 * scale,
            head_height=300e-9 * scale,
            neck_width=100e-9 * scale,
            neck_height=200e-9 * scale,
            base_width=300e-9 * scale,
            base_height=50e-9 * scale,
            neck_material="sio2"  # Thermal isolation
        )
    
    @classmethod
    def thin_spine(cls, scale: float = 1.0) -> 'SpineGeometry':
        """Create thin spine geometry (small head, long thin neck)."""
        return cls(
            geometry_type=GeometryType.THIN,
            head_width=200e-9 * scale,
            head_height=150e-9 * scale,
            neck_width=60e-9 * scale,
            neck_height=400e-9 * scale,
            base_width=200e-9 * scale,
            base_height=50e-9 * scale,
            neck_material="sio2_porous"  # Even lower k
        )
    
    @classmethod
    def stubby_spine(cls, scale: float = 1.0) -> 'SpineGeometry':
        """Create stubby spine geometry (short, no distinct neck)."""
        return cls(
            geometry_type=GeometryType.STUBBY,
            head_width=300e-9 * scale,
            head_height=200e-9 * scale,
            neck_width=250e-9 * scale,
            neck_height=50e-9 * scale,
            base_width=300e-9 * scale,
            base_height=50e-9 * scale,
            neck_material="silicon"  # Good thermal conduction
        )
    
    @classmethod
    def filapodia_spine(cls, scale: float = 1.0) -> 'SpineGeometry':
        """Create filapodia-like geometry (very long, thin)."""
        return cls(
            geometry_type=GeometryType.FILAPODIA,
            head_width=150e-9 * scale,
            head_height=100e-9 * scale,
            neck_width=40e-9 * scale,
            neck_height=600e-9 * scale,
            base_width=150e-9 * scale,
            base_height=50e-9 * scale,
            neck_material="sio2_porous"
        )
    
    def total_height(self) -> float:
        """Total structure height."""
        return self.head_height + self.neck_height + self.base_height
    
    def max_width(self) -> float:
        """Maximum structure width."""
        return max(self.head_width, self.neck_width, self.base_width)
    
    def head_volume(self) -> float:
        """Head volume (active region)."""
        return self.head_width * self.head_height * self.head_width  # Approx as box
    
    def neck_volume(self) -> float:
        """Neck volume."""
        return self.neck_width * self.neck_height * self.neck_width
    
    def neck_thermal_resistance(self) -> float:
        """
        Thermal resistance of neck.
        R_th = L / (k * A)
        """
        mat = get_material(self.neck_material)
        area = self.neck_width * self.neck_width  # Square cross-section
        return self.neck_height / (mat.thermal_conductivity * area)
    
    def aspect_ratio(self) -> float:
        """Height-to-width aspect ratio."""
        return self.total_height() / self.max_width()
    
    def isolation_factor(self) -> float:
        """
        Thermal isolation factor.
        Higher values indicate better heat confinement in head.
        
        Defined as: R_neck / (R_head + R_neck)
        """
        head_mat = get_material(self.head_material)
        neck_mat = get_material(self.neck_material)
        
        # Approximate thermal resistances
        R_head = self.head_height / (head_mat.thermal_conductivity * 
                                     self.head_width * self.head_width)
        R_neck = self.neck_thermal_resistance()
        
        return R_neck / (R_head + R_neck)


@dataclass
class SpineArrayConfig:
    """Configuration for array of spine-inspired cells."""
    
    # Array dimensions
    n_x: int = 4
    n_y: int = 4
    
    # Cell spacing
    pitch_x: float = 500e-9  # 500 nm
    pitch_y: float = 500e-9
    
    # Geometry (all cells same type, or specify per-cell)
    geometry: SpineGeometry = field(default_factory=SpineGeometry.mushroom_spine)
    
    # Substrate
    substrate_thickness: float = 1e-6  # 1 μm
    substrate_material: str = "silicon"
    
    # Heat spreading layer
    heat_spreader: bool = True
    spreader_thickness: float = 200e-9
    spreader_material: str = "copper"


class SpineThermalSimulator:
    """
    Thermal simulator for spine-inspired structures.
    """
    
    def __init__(self, geometry: SpineGeometry, config: Optional[SimulationConfig] = None):
        self.geometry = geometry
        
        # Default configuration
        if config is None:
            config = SimulationConfig(
                nx=100,
                ny=100,
                nz=1,
                dx=5e-9,  # 5 nm resolution
                dy=5e-9,
                convergence_tolerance=1e-5,
                verbose=False
            )
        
        self.config = config
        self._setup_grid()
    
    def _setup_grid(self):
        """Set up thermal grid based on geometry."""
        self.grid = ThermalGrid(self.config)
        
        # Calculate geometry placement
        total_width = self.geometry.max_width() + 100e-9  # Margin
        center_x = self.config.nx * self.config.dx / 2
        center_y = self.config.ny * self.config.dy / 2
        
        # Convert dimensions to grid units
        def to_grid(dimension):
            return int(dimension / self.config.dx)
        
        # Set up material regions
        # Base
        base_half_w = to_grid(self.geometry.base_width / 2)
        base_h = to_grid(self.geometry.base_height)
        base_y_start = self.config.ny // 2 - base_h // 2 - to_grid(self.geometry.neck_height) - to_grid(self.geometry.head_height) // 2
        
        # Neck
        neck_half_w = to_grid(self.geometry.neck_width / 2)
        neck_h = to_grid(self.geometry.neck_height)
        
        # Head
        head_half_w = to_grid(self.geometry.head_width / 2)
        head_h = to_grid(self.geometry.head_height)
        
        # Set materials
        center_i = self.config.nx // 2
        center_j = self.config.ny // 2
        
        # Background (oxide)
        self.grid.k.fill(get_material('sio2').thermal_conductivity)
        
        # Base (heat spreader connection)
        base_mat = get_material(self.geometry.base_material)
        self.grid.k[0:base_h, 
                   center_j - base_half_w//2:center_j + base_half_w//2,
                   center_i - base_half_w:center_i + base_half_w] = base_mat.thermal_conductivity
        
        # Neck
        neck_mat = get_material(self.geometry.neck_material)
        neck_start = base_h
        neck_end = base_h + neck_h
        self.grid.k[neck_start:neck_end,
                   center_j - neck_half_w//2:center_j + neck_half_w//2,
                   center_i - neck_half_w:center_i + neck_half_w] = neck_mat.thermal_conductivity
        
        # Head
        head_mat = get_material(self.geometry.head_material)
        head_start = neck_end
        head_end = head_start + head_h
        self.grid.k[head_start:head_end,
                   center_j - head_half_w//2:center_j + head_half_w//2,
                   center_i - head_half_w:center_i + head_half_w] = head_mat.thermal_conductivity
        
        # Store region boundaries for heat source placement
        self.head_region = {
            'i_start': center_i - head_half_w,
            'i_end': center_i + head_half_w,
            'j_start': head_start,
            'j_end': head_end
        }
        
        self.neck_region = {
            'i_start': center_i - neck_half_w,
            'i_end': center_i + neck_half_w,
            'j_start': neck_start,
            'j_end': neck_end
        }
        
        self.base_region = {
            'i_start': center_i - base_half_w,
            'i_end': center_i + base_half_w,
            'j_start': 0,
            'j_end': base_h
        }
        
        # Set boundary conditions
        # Bottom: fixed temperature (substrate)
        self.grid.bc_bottom = BoundaryCondition(BoundaryType.DIRICHLET, 300.0)
        # Top: convective cooling
        self.grid.bc_top = BoundaryCondition(BoundaryType.CONVECTIVE, 1e5)
        # Sides: adiabatic
        self.grid.bc_left = BoundaryCondition(BoundaryType.NEUMANN, 0.0)
        self.grid.bc_right = BoundaryCondition(BoundaryType.NEUMANN, 0.0)
    
    def add_heat_source(self, power: float):
        """Add heat source in head region."""
        region = self.head_region
        
        # Volumetric heat generation
        volume = ((region['i_end'] - region['i_start']) * self.config.dx *
                 (region['j_end'] - region['j_start']) * self.config.dy)
        
        power_density = power / volume
        
        self.grid.add_volumetric_heat(
            power_density,
            (region['i_start'], region['i_end']),
            (region['j_start'], region['j_end'])
        )
    
    def simulate(self, power: float = 1e-6) -> NDArray:
        """Run thermal simulation."""
        self.grid.clear_heat_sources()
        self.add_heat_source(power)
        
        solver = ThermalSolver(self.grid)
        T = solver.solve_steady_state_matrix()
        
        return T
    
    def head_temperature(self, T: NDArray) -> float:
        """Average temperature in head region."""
        region = self.head_region
        return np.mean(T[0, region['j_start']:region['j_end'],
                        region['i_start']:region['i_end']])
    
    def base_temperature(self, T: NDArray) -> float:
        """Average temperature at base."""
        region = self.base_region
        return np.mean(T[0, region['j_start']:region['j_end'],
                        region['i_start']:region['i_end']])
    
    def thermal_isolation_efficiency(self, T: NDArray) -> float:
        """
        Thermal isolation efficiency.
        
        Measures how well heat is confined to head vs spreading through neck.
        High efficiency = most heat flows up (to cooling) rather than down (to neighbors).
        """
        T_head = self.head_temperature(T)
        T_base = self.base_temperature(T)
        T_ambient = 300.0
        
        # Temperature drop across neck
        delta_T_neck = T_head - T_base
        
        # Total temperature rise
        delta_T_total = T_head - T_ambient
        
        if delta_T_total > 0:
            # Higher isolation = more temperature drop across neck
            return delta_T_neck / delta_T_total
        return 0.0


def compare_spine_geometries(power: float = 1e-6) -> Dict:
    """
    Compare thermal performance of different spine geometries.
    
    Args:
        power: Heat generation power in Watts
    
    Returns:
        Dictionary with comparison results
    """
    results = {}
    
    geometries = {
        'mushroom': SpineGeometry.mushroom_spine(),
        'thin': SpineGeometry.thin_spine(),
        'stubby': SpineGeometry.stubby_spine(),
        'filapodia': SpineGeometry.filapodia_spine()
    }
    
    for name, geometry in geometries.items():
        print(f"Simulating {name} spine...")
        
        simulator = SpineThermalSimulator(geometry)
        T = simulator.simulate(power)
        
        results[name] = {
            'geometry': geometry,
            'temperature_field': T,
            'head_temp': simulator.head_temperature(T),
            'base_temp': simulator.base_temperature(T),
            'max_temp': np.max(T),
            'isolation_efficiency': simulator.thermal_isolation_efficiency(T),
            'neck_thermal_resistance': geometry.neck_thermal_resistance(),
            'aspect_ratio': geometry.aspect_ratio()
        }
    
    return results


def optimize_neck_geometry(
    target_isolation: float = 0.7,
    max_neck_height: float = 500e-9,
    min_neck_width: float = 40e-9
) -> Dict:
    """
    Find optimal neck dimensions for target thermal isolation.
    
    Args:
        target_isolation: Desired isolation factor
        max_neck_height: Maximum neck height constraint
        min_neck_width: Minimum neck width (fabrication limit)
    
    Returns:
        Optimal geometry parameters
    """
    results = {
        'tested': [],
        'optimal': None
    }
    
    # Parameter sweep
    neck_widths = np.linspace(min_neck_width, 200e-9, 10)
    neck_heights = np.linspace(50e-9, max_neck_height, 10)
    
    best_isolation = 0
    best_params = None
    
    for width in neck_widths:
        for height in neck_heights:
            geometry = SpineGeometry(
                geometry_type=GeometryType.CUSTOM,
                head_width=300e-9,
                head_height=200e-9,
                neck_width=width,
                neck_height=height,
                neck_material="sio2"
            )
            
            isolation = geometry.isolation_factor()
            
            results['tested'].append({
                'neck_width': width,
                'neck_height': height,
                'isolation': isolation,
                'aspect_ratio': height / width
            })
            
            if isolation > best_isolation:
                best_isolation = isolation
                best_params = {
                    'neck_width': width,
                    'neck_height': height,
                    'isolation': isolation
                }
            
            if isolation >= target_isolation:
                # Found geometry meeting target
                results['optimal'] = best_params
                return results
    
    results['optimal'] = best_params
    return results


def analyze_thermal_coupling_between_spines(
    spacing: float = 500e-9,
    power: float = 1e-6
) -> Dict:
    """
    Analyze thermal coupling between adjacent spine cells.
    
    Args:
        spacing: Center-to-center spacing between cells
        power: Heat generation in each cell
    
    Returns:
        Coupling analysis results
    """
    # Create a grid with two spine cells
    total_width = int(3 * spacing / 5e-9)  # Grid points
    
    config = SimulationConfig(
        nx=total_width,
        ny=total_width,
        nz=1,
        dx=5e-9,
        dy=5e-9,
        convergence_tolerance=1e-5,
        verbose=False
    )
    
    grid = ThermalGrid(config)
    grid.bc_bottom = BoundaryCondition(BoundaryType.DIRICHLET, 300.0)
    grid.bc_top = BoundaryCondition(BoundaryType.CONVECTIVE, 1e5)
    
    # Background material
    grid.k.fill(get_material('sio2').thermal_conductivity)
    
    # Place two cells
    spacing_grid = int(spacing / config.dx)
    cell_size = 30  # Grid points for head
    
    center1_i = total_width // 2 - spacing_grid // 2
    center2_i = total_width // 2 + spacing_grid // 2
    center_j = total_width // 2
    
    # Set up first cell (hot)
    grid.k[center_j - cell_size//2:center_j + cell_size//2,
           center1_i - cell_size//2:center1_i + cell_size//2] = get_material('silicon').thermal_conductivity
    
    # Set up second cell (observed)
    grid.k[center_j - cell_size//2:center_j + cell_size//2,
           center2_i - cell_size//2:center2_i + cell_size//2] = get_material('silicon').thermal_conductivity
    
    # Add heat source to first cell only
    cell_volume = cell_size**2 * config.dx * config.dy
    power_density = power / cell_volume
    
    grid.add_volumetric_heat(
        power_density,
        (center1_i - cell_size//2, center1_i + cell_size//2),
        (center_j - cell_size//2, center_j + cell_size//2)
    )
    
    # Solve
    solver = ThermalSolver(grid)
    T = solver.solve_steady_state_matrix()
    
    # Extract temperatures
    T_cell1 = np.mean(T[0, center_j - cell_size//2:center_j + cell_size//2,
                       center1_i - cell_size//2:center1_i + cell_size//2])
    T_cell2 = np.mean(T[0, center_j - cell_size//2:center_j + cell_size//2,
                       center2_i - cell_size//2:center2_i + cell_size//2])
    
    # Coupling coefficient
    coupling = (T_cell2 - 300.0) / (T_cell1 - 300.0) if T_cell1 > 300 else 0
    
    return {
        'spacing': spacing,
        'T_cell1': T_cell1,
        'T_cell2': T_cell2,
        'coupling_coefficient': coupling,
        'temperature_field': T
    }


def run_spine_geometry_analysis():
    """Run comprehensive spine geometry thermal analysis."""
    print("=" * 70)
    print("SPINE-INSPIRED GEOMETRY THERMAL ANALYSIS")
    print("=" * 70)
    
    # 1. Compare geometries
    print("\n1. GEOMETRY COMPARISON")
    print("-" * 40)
    
    results = compare_spine_geometries(power=1e-6)
    
    print(f"\n{'Geometry':<12} {'Head T (K)':<12} {'Base T (K)':<12} "
          f"{'Max T (K)':<12} {'Isolation':<12} {'R_neck (K/W)':<15}")
    print("-" * 75)
    
    for name, data in results.items():
        print(f"{name:<12} {data['head_temp']:<12.2f} {data['base_temp']:<12.2f} "
              f"{data['max_temp']:<12.2f} {data['isolation_efficiency']:<12.2%} "
              f"{data['neck_thermal_resistance']:<15.2e}")
    
    # 2. Find optimal isolation geometry
    print("\n2. OPTIMAL NECK GEOMETRY FOR ISOLATION")
    print("-" * 40)
    
    opt_results = optimize_neck_geometry(target_isolation=0.7)
    
    if opt_results['optimal']:
        opt = opt_results['optimal']
        print(f"Optimal neck width: {opt['neck_width']*1e9:.0f} nm")
        print(f"Optimal neck height: {opt['neck_height']*1e9:.0f} nm")
        print(f"Achieved isolation: {opt['isolation']:.2%}")
    
    # 3. Thermal coupling analysis
    print("\n3. THERMAL COUPLING BETWEEN ADJACENT CELLS")
    print("-" * 40)
    
    spacings = [300e-9, 400e-9, 500e-9, 600e-9, 800e-9, 1000e-9]
    
    print(f"\n{'Spacing (nm)':<15} {'T_cell1 (K)':<15} {'T_cell2 (K)':<15} "
          f"{'Coupling':<15}")
    print("-" * 60)
    
    for spacing in spacings:
        coupling_result = analyze_thermal_coupling_between_spines(spacing)
        print(f"{spacing*1e9:<15.0f} {coupling_result['T_cell1']:<15.2f} "
              f"{coupling_result['T_cell2']:<15.2f} "
              f"{coupling_result['coupling_coefficient']:<15.3f}")
    
    # 4. Design recommendations
    print("\n4. DESIGN RECOMMENDATIONS")
    print("-" * 40)
    
    # Find best geometry for different objectives
    best_isolation = max(results.items(), key=lambda x: x[1]['isolation_efficiency'])
    lowest_temp = min(results.items(), key=lambda x: x[1]['max_temp'])
    
    print(f"Best thermal isolation: {best_isolation[0]} "
          f"(isolation = {best_isolation[1]['isolation_efficiency']:.2%})")
    print(f"Lowest peak temperature: {lowest_temp[0]} "
          f"(T_max = {lowest_temp[1]['max_temp']:.2f} K)")
    
    return results


if __name__ == "__main__":
    results = run_spine_geometry_analysis()
