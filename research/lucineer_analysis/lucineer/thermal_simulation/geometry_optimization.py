"""
Geometry Optimization for Thermal Performance
=============================================
Optimization algorithms for thermal-aware design of synapse-inspired structures.

Optimization Objectives:
1. Minimize peak temperature
2. Maximize thermal isolation between units
3. Optimize power density packing
4. Balance heat spreading vs heat confinement

Methods:
- Gradient-based optimization
- Genetic algorithms
- Surrogate modeling
- Multi-objective Pareto optimization

References:
[1] Queipo, N.V. et al. (2005). Surrogate-based analysis and optimization
    Prog. Aerosp. Sci. 41, 1-28
[2] Deb, K. et al. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II
    IEEE Trans. Evol. Comput. 6, 182-197
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

from core_thermal import (ThermalGrid, ThermalSolver, ThermalAnalyzer,
                          SimulationConfig, BoundaryCondition, BoundaryType,
                          HeatSource)
from materials import get_material, Material
from spine_geometry import SpineGeometry, SpineThermalSimulator


class OptimizationObjective(Enum):
    """Optimization objectives."""
    MINIMIZE_PEAK_TEMPERATURE = "min_peak_temp"
    MAXIMIZE_ISOLATION = "max_isolation"
    MAXIMIZE_POWER_DENSITY = "max_power_density"
    MINIMIZE_THERMAL_RESISTANCE = "min_rth"
    MULTI_OBJECTIVE = "multi"


@dataclass
class OptimizationConstraints:
    """Constraints for geometry optimization."""
    
    # Geometric constraints
    min_neck_width: float = 40e-9      # Fabrication limit
    max_neck_width: float = 300e-9
    min_neck_height: float = 50e-9
    max_neck_height: float = 1000e-9
    
    min_head_width: float = 100e-9
    max_head_width: float = 600e-9
    
    min_spacing: float = 100e-9
    max_spacing: float = 2000e-9
    
    # Thermal constraints
    max_temperature: float = 350.0     # K
    min_isolation: float = 0.3         # Fraction
    max_thermal_resistance: float = 1e6  # K/W
    
    # Performance constraints
    min_power_density: float = 1e4     # W/m²
    target_power: float = 1e-6         # W per unit


@dataclass
class GeometryParameters:
    """Parameterized geometry for optimization."""
    
    # Neck parameters
    neck_width: float = 100e-9
    neck_height: float = 200e-9
    neck_material: str = "sio2"
    
    # Head parameters
    head_width: float = 300e-9
    head_height: float = 200e-9
    head_material: str = "silicon"
    
    # Base parameters
    base_width: float = 200e-9
    base_height: float = 50e-9
    base_material: str = "copper"
    
    # Array parameters
    cell_pitch_x: float = 500e-9
    cell_pitch_y: float = 500e-9
    
    def to_vector(self) -> NDArray:
        """Convert to optimization vector."""
        return np.array([
            self.neck_width,
            self.neck_height,
            self.head_width,
            self.head_height,
            self.base_width,
            self.base_height,
            self.cell_pitch_x,
            self.cell_pitch_y
        ])
    
    @classmethod
    def from_vector(cls, vector: NDArray) -> 'GeometryParameters':
        """Create from optimization vector."""
        return cls(
            neck_width=vector[0],
            neck_height=vector[1],
            head_width=vector[2],
            head_height=vector[3],
            base_width=vector[4],
            base_height=vector[5],
            cell_pitch_x=vector[6],
            cell_pitch_y=vector[7]
        )
    
    def to_spine_geometry(self) -> SpineGeometry:
        """Convert to SpineGeometry object."""
        return SpineGeometry(
            geometry_type=SpineGeometry.GeometryType.CUSTOM,
            neck_width=self.neck_width,
            neck_height=self.neck_height,
            neck_material=self.neck_material,
            head_width=self.head_width,
            head_height=self.head_height,
            head_material=self.head_material,
            base_width=self.base_width,
            base_height=self.base_height,
            base_material=self.base_material
        )


@dataclass
class OptimizationResult:
    """Result of geometry optimization."""
    
    best_parameters: GeometryParameters
    best_objective: float
    objective_history: List[float]
    parameter_history: List[GeometryParameters]
    n_iterations: int
    converged: bool
    constraint_violations: List[str]


class ThermalObjectiveEvaluator:
    """Evaluates thermal objectives for geometry optimization."""
    
    def __init__(self, power: float = 1e-6, config: Optional[SimulationConfig] = None):
        self.power = power
        self.config = config or SimulationConfig(
            nx=80, ny=80, nz=1, dx=5e-9, dy=5e-9,
            convergence_tolerance=1e-4, verbose=False
        )
    
    def evaluate(self, params: GeometryParameters) -> Dict[str, float]:
        """
        Evaluate all thermal metrics for given geometry.
        
        Returns:
            Dictionary of metric names to values
        """
        geometry = params.to_spine_geometry()
        
        # Create simulator
        simulator = SpineThermalSimulator(geometry, self.config)
        
        # Run simulation
        T = simulator.simulate(self.power)
        
        # Extract metrics
        metrics = {
            'peak_temperature': np.max(T),
            'head_temperature': simulator.head_temperature(T),
            'base_temperature': simulator.base_temperature(T),
            'temperature_rise': np.max(T) - 300.0,
            'isolation_efficiency': simulator.thermal_isolation_efficiency(T),
            'thermal_resistance': geometry.neck_thermal_resistance(),
            'power_density': self.power / (params.cell_pitch_x * params.cell_pitch_y),
            'aspect_ratio': geometry.aspect_ratio(),
            'packing_efficiency': (params.head_width * params.head_height) / \
                                  (params.cell_pitch_x * params.cell_pitch_y)
        }
        
        return metrics
    
    def objective_function(self, params: GeometryParameters,
                          objective: OptimizationObjective) -> float:
        """
        Compute single objective value for optimization.
        
        Args:
            params: Geometry parameters
            objective: Optimization objective
        
        Returns:
            Objective value (to be minimized)
        """
        metrics = self.evaluate(params)
        
        if objective == OptimizationObjective.MINIMIZE_PEAK_TEMPERATURE:
            return metrics['peak_temperature']
        
        elif objective == OptimizationObjective.MAXIMIZE_ISOLATION:
            return -metrics['isolation_efficiency']  # Negative for minimization
        
        elif objective == OptimizationObjective.MAXIMIZE_POWER_DENSITY:
            return -metrics['power_density']
        
        elif objective == OptimizationObjective.MINIMIZE_THERMAL_RESISTANCE:
            return metrics['thermal_resistance']
        
        elif objective == OptimizationObjective.MULTI_OBJECTIVE:
            # Weighted sum approach
            weights = {
                'temperature_rise': 0.4,
                'isolation_efficiency': -0.3,  # Maximize
                'power_density': -0.2,  # Maximize
                'packing_efficiency': -0.1
            }
            
            objective_value = 0.0
            for key, weight in weights.items():
                objective_value += weight * metrics[key]
            
            return objective_value
        
        return metrics['peak_temperature']


class GradientDescentOptimizer:
    """Gradient descent geometry optimizer."""
    
    def __init__(self, evaluator: ThermalObjectiveEvaluator,
                 constraints: OptimizationConstraints):
        self.evaluator = evaluator
        self.constraints = constraints
    
    def optimize(self, initial_params: GeometryParameters,
                 objective: OptimizationObjective,
                 learning_rate: float = 1e-8,
                 max_iterations: int = 100,
                 tolerance: float = 1e-6) -> OptimizationResult:
        """
        Run gradient descent optimization.
        
        Args:
            initial_params: Starting geometry
            objective: Optimization objective
            learning_rate: Step size
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
        
        Returns:
            Optimization result
        """
        params = initial_params
        vector = params.to_vector()
        
        objective_history = []
        parameter_history = []
        
        best_objective = float('inf')
        best_params = params
        
        for iteration in range(max_iterations):
            # Evaluate current point
            current_obj = self.evaluator.objective_function(params, objective)
            objective_history.append(current_obj)
            parameter_history.append(GeometryParameters.from_vector(vector.copy()))
            
            if current_obj < best_objective:
                best_objective = current_obj
                best_params = GeometryParameters.from_vector(vector.copy())
            
            # Compute numerical gradient
            gradient = self._compute_gradient(vector, objective)
            
            # Update parameters
            new_vector = vector - learning_rate * gradient
            
            # Apply constraints
            new_vector = self._apply_constraints(new_vector)
            
            # Check convergence
            if np.linalg.norm(new_vector - vector) < tolerance:
                return OptimizationResult(
                    best_parameters=best_params,
                    best_objective=best_objective,
                    objective_history=objective_history,
                    parameter_history=parameter_history,
                    n_iterations=iteration,
                    converged=True,
                    constraint_violations=[]
                )
            
            vector = new_vector
            params = GeometryParameters.from_vector(vector)
        
        return OptimizationResult(
            best_parameters=best_params,
            best_objective=best_objective,
            objective_history=objective_history,
            parameter_history=parameter_history,
            n_iterations=max_iterations,
            converged=False,
            constraint_violations=[]
        )
    
    def _compute_gradient(self, vector: NDArray, objective: OptimizationObjective,
                          delta: float = 1e-9) -> NDArray:
        """Compute numerical gradient using central differences."""
        gradient = np.zeros_like(vector)
        
        for i in range(len(vector)):
            # Forward perturbation
            v_forward = vector.copy()
            v_forward[i] += delta
            params_forward = GeometryParameters.from_vector(v_forward)
            obj_forward = self.evaluator.objective_function(params_forward, objective)
            
            # Backward perturbation
            v_backward = vector.copy()
            v_backward[i] -= delta
            params_backward = GeometryParameters.from_vector(v_backward)
            obj_backward = self.evaluator.objective_function(params_backward, objective)
            
            gradient[i] = (obj_forward - obj_backward) / (2 * delta)
        
        return gradient
    
    def _apply_constraints(self, vector: NDArray) -> NDArray:
        """Apply constraint bounds to parameter vector."""
        bounds = [
            (self.constraints.min_neck_width, self.constraints.max_neck_width),
            (self.constraints.min_neck_height, self.constraints.max_neck_height),
            (self.constraints.min_head_width, self.constraints.max_head_width),
            (50e-9, 500e-9),  # head_height
            (50e-9, 500e-9),  # base_width
            (20e-9, 200e-9),  # base_height
            (self.constraints.min_spacing, self.constraints.max_spacing),
            (self.constraints.min_spacing, self.constraints.max_spacing)
        ]
        
        for i, (lower, upper) in enumerate(bounds):
            vector[i] = np.clip(vector[i], lower, upper)
        
        return vector


class GeneticOptimizer:
    """Genetic algorithm geometry optimizer."""
    
    def __init__(self, evaluator: ThermalObjectiveEvaluator,
                 constraints: OptimizationConstraints):
        self.evaluator = evaluator
        self.constraints = constraints
    
    def optimize(self, objective: OptimizationObjective,
                 population_size: int = 20,
                 generations: int = 30,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7) -> OptimizationResult:
        """
        Run genetic algorithm optimization.
        
        Args:
            objective: Optimization objective
            population_size: Population size
            generations: Number of generations
            mutation_rate: Mutation probability
            crossover_rate: Crossover probability
        
        Returns:
            Optimization result
        """
        # Initialize population
        population = self._initialize_population(population_size)
        
        objective_history = []
        parameter_history = []
        best_objective = float('inf')
        best_params = None
        
        for gen in range(generations):
            # Evaluate fitness
            fitness = []
            for individual in population:
                obj = self.evaluator.objective_function(individual, objective)
                fitness.append(obj)
                
                if obj < best_objective:
                    best_objective = obj
                    best_params = GeometryParameters.from_vector(individual.to_vector())
            
            objective_history.append(min(fitness))
            parameter_history.append(best_params)
            
            # Selection (tournament)
            new_population = []
            for _ in range(population_size // 2):
                parent1 = self._tournament_selection(population, fitness)
                parent2 = self._tournament_selection(population, fitness)
                
                # Crossover
                if random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                # Mutation
                child1 = self._mutate(child1, mutation_rate)
                child2 = self._mutate(child2, mutation_rate)
                
                new_population.extend([child1, child2])
            
            # Elitism: keep best individual
            new_population[0] = best_params
            population = new_population
        
        return OptimizationResult(
            best_parameters=best_params,
            best_objective=best_objective,
            objective_history=objective_history,
            parameter_history=parameter_history,
            n_iterations=generations,
            converged=True,
            constraint_violations=[]
        )
    
    def _initialize_population(self, size: int) -> List[GeometryParameters]:
        """Initialize random population within constraints."""
        population = []
        
        for _ in range(size):
            params = GeometryParameters(
                neck_width=random.uniform(self.constraints.min_neck_width,
                                         self.constraints.max_neck_width),
                neck_height=random.uniform(self.constraints.min_neck_height,
                                          self.constraints.max_neck_height),
                head_width=random.uniform(self.constraints.min_head_width,
                                         self.constraints.max_head_width),
                head_height=random.uniform(100e-9, 400e-9),
                base_width=random.uniform(100e-9, 400e-9),
                base_height=random.uniform(30e-9, 100e-9),
                cell_pitch_x=random.uniform(300e-9, 1000e-9),
                cell_pitch_y=random.uniform(300e-9, 1000e-9)
            )
            population.append(params)
        
        return population
    
    def _tournament_selection(self, population: List[GeometryParameters],
                             fitness: List[float],
                             tournament_size: int = 3) -> GeometryParameters:
        """Tournament selection."""
        indices = random.sample(range(len(population)), tournament_size)
        best_idx = min(indices, key=lambda i: fitness[i])
        return population[best_idx]
    
    def _crossover(self, parent1: GeometryParameters,
                   parent2: GeometryParameters) -> Tuple[GeometryParameters, GeometryParameters]:
        """Uniform crossover."""
        v1 = parent1.to_vector()
        v2 = parent2.to_vector()
        
        child1 = []
        child2 = []
        
        for i in range(len(v1)):
            if random.random() < 0.5:
                child1.append(v1[i])
                child2.append(v2[i])
            else:
                child1.append(v2[i])
                child2.append(v1[i])
        
        return (GeometryParameters.from_vector(np.array(child1)),
                GeometryParameters.from_vector(np.array(child2)))
    
    def _mutate(self, individual: GeometryParameters,
                rate: float) -> GeometryParameters:
        """Gaussian mutation."""
        vector = individual.to_vector()
        
        for i in range(len(vector)):
            if random.random() < rate:
                vector[i] *= random.gauss(1.0, 0.1)
        
        return GeometryParameters.from_vector(vector)


class SpacingOptimizer:
    """Optimize spacing between thermal units."""
    
    def __init__(self, evaluator: ThermalObjectiveEvaluator):
        self.evaluator = evaluator
    
    def find_minimum_spacing(self,
                            target_coupling: float = 0.1,
                            max_spacing: float = 2000e-9) -> Dict:
        """
        Find minimum spacing for acceptable thermal coupling.
        
        Args:
            target_coupling: Maximum acceptable coupling coefficient
            max_spacing: Maximum spacing to search
        
        Returns:
            Optimal spacing and analysis results
        """
        results = {
            'tested_spacings': [],
            'optimal_spacing': None
        }
        
        spacings = np.linspace(200e-9, max_spacing, 20)
        
        for spacing in spacings:
            params = GeometryParameters(cell_pitch_x=spacing, cell_pitch_y=spacing)
            
            # Approximate coupling from thermal analysis
            metrics = self.evaluator.evaluate(params)
            
            # Estimate coupling (temperature rise ratio)
            coupling = metrics['base_temperature'] / metrics['head_temperature'] if \
                       metrics['head_temperature'] > 300 else 0
            
            results['tested_spacings'].append({
                'spacing': spacing,
                'coupling': coupling,
                'head_temp': metrics['head_temperature'],
                'base_temp': metrics['base_temperature']
            })
            
            if coupling < target_coupling and results['optimal_spacing'] is None:
                results['optimal_spacing'] = spacing
        
        return results
    
    def optimize_for_packing_density(self,
                                    max_temperature: float = 350.0,
                                    power_per_cell: float = 1e-6) -> Dict:
        """
        Find maximum packing density within thermal limits.
        
        Args:
            max_temperature: Maximum allowed temperature
            power_per_cell: Power per cell
        
        Returns:
            Optimal packing configuration
        """
        results = {
            'tested_configs': [],
            'optimal_config': None,
            'max_packing_density': 0.0
        }
        
        spacings = np.linspace(200e-9, 1000e-9, 15)
        
        for spacing in spacings:
            params = GeometryParameters(cell_pitch_x=spacing, cell_pitch_y=spacing)
            metrics = self.evaluator.evaluate(params)
            
            # Packing density (cells per unit area)
            packing_density = 1.0 / (spacing ** 2)
            
            valid = metrics['peak_temperature'] < max_temperature
            
            results['tested_configs'].append({
                'spacing': spacing,
                'packing_density': packing_density,
                'peak_temp': metrics['peak_temperature'],
                'valid': valid
            })
            
            if valid and packing_density > results['max_packing_density']:
                results['max_packing_density'] = packing_density
                results['optimal_config'] = {
                    'spacing': spacing,
                    'packing_density': packing_density,
                    'cells_per_mm2': packing_density * 1e12
                }
        
        return results


def run_geometry_optimization():
    """Run comprehensive geometry optimization."""
    print("=" * 70)
    print("GEOMETRY OPTIMIZATION FOR THERMAL PERFORMANCE")
    print("=" * 70)
    
    # Initialize
    constraints = OptimizationConstraints()
    evaluator = ThermalObjectiveEvaluator(power=1e-6)
    
    # 1. Gradient descent optimization
    print("\n1. GRADIENT DESCENT OPTIMIZATION")
    print("-" * 40)
    
    initial_params = GeometryParameters()
    gd_optimizer = GradientDescentOptimizer(evaluator, constraints)
    
    gd_result = gd_optimizer.optimize(
        initial_params,
        OptimizationObjective.MINIMIZE_PEAK_TEMPERATURE,
        learning_rate=5e-9,
        max_iterations=50
    )
    
    print(f"Initial peak temperature: {gd_result.objective_history[0]:.2f} K")
    print(f"Final peak temperature: {gd_result.best_objective:.2f} K")
    print(f"Iterations: {gd_result.n_iterations}")
    print(f"Converged: {gd_result.converged}")
    
    print("\nOptimal parameters:")
    print(f"  Neck: {gd_result.best_parameters.neck_width*1e9:.0f} x "
          f"{gd_result.best_parameters.neck_height*1e9:.0f} nm")
    print(f"  Head: {gd_result.best_parameters.head_width*1e9:.0f} x "
          f"{gd_result.best_parameters.head_height*1e9:.0f} nm")
    print(f"  Pitch: {gd_result.best_parameters.cell_pitch_x*1e9:.0f} x "
          f"{gd_result.best_parameters.cell_pitch_y*1e9:.0f} nm")
    
    # 2. Genetic algorithm optimization
    print("\n2. GENETIC ALGORITHM OPTIMIZATION")
    print("-" * 40)
    
    ga_optimizer = GeneticOptimizer(evaluator, constraints)
    
    ga_result = ga_optimizer.optimize(
        OptimizationObjective.MULTI_OBJECTIVE,
        population_size=15,
        generations=20
    )
    
    print(f"Best objective: {ga_result.best_objective:.4f}")
    print(f"Generations: {ga_result.n_iterations}")
    
    # Evaluate final design
    final_metrics = evaluator.evaluate(ga_result.best_parameters)
    print("\nFinal design metrics:")
    for key, value in final_metrics.items():
        if 'temp' in key.lower():
            print(f"  {key}: {value:.2f} K")
        elif 'density' in key.lower():
            print(f"  {key}: {value:.2e} W/m²")
        else:
            print(f"  {key}: {value:.4f}")
    
    # 3. Spacing optimization
    print("\n3. SPACING OPTIMIZATION")
    print("-" * 40)
    
    spacing_optimizer = SpacingOptimizer(evaluator)
    
    spacing_result = spacing_optimizer.find_minimum_spacing(target_coupling=0.1)
    
    print(f"{'Spacing (nm)':<15} {'Coupling':<15} {'Head T (K)':<15} {'Base T (K)':<15}")
    print("-" * 60)
    for r in spacing_result['tested_spacings'][:10]:
        print(f"{r['spacing']*1e9:<15.0f} {r['coupling']:<15.3f} "
              f"{r['head_temp']:<15.2f} {r['base_temp']:<15.2f}")
    
    if spacing_result['optimal_spacing']:
        print(f"\nOptimal spacing for <10% coupling: "
              f"{spacing_result['optimal_spacing']*1e9:.0f} nm")
    
    # 4. Packing density optimization
    print("\n4. PACKING DENSITY OPTIMIZATION")
    print("-" * 40)
    
    packing_result = spacing_optimizer.optimize_for_packing_density(
        max_temperature=350.0
    )
    
    print(f"{'Spacing (nm)':<15} {'Cells/mm²':<15} {'Peak T (K)':<15} {'Valid':<10}")
    print("-" * 55)
    for r in packing_result['tested_configs']:
        print(f"{r['spacing']*1e9:<15.0f} {r['packing_density']*1e12:<15.0f} "
              f"{r['peak_temp']:<15.2f} {str(r['valid']):<10}")
    
    if packing_result['optimal_config']:
        opt = packing_result['optimal_config']
        print(f"\nMaximum packing density: {opt['cells_per_mm2']:.0f} cells/mm²")
        print(f"  At spacing: {opt['spacing']*1e9:.0f} nm")
    
    return {
        'gradient_descent': gd_result,
        'genetic_algorithm': ga_result,
        'spacing_optimization': spacing_result,
        'packing_optimization': packing_result
    }


if __name__ == "__main__":
    results = run_geometry_optimization()
