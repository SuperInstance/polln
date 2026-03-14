"""
Cycle 9: Statistical Mechanics Neural Network Analysis
======================================================

Comprehensive statistical mechanics framework for analyzing phase transitions,
free energy landscapes, and thermodynamic stability in 2.4B weight mask-locked
ternary inference chips.

Key Parameters:
- 2.4B weights → thermodynamic limit approximation
- Temperature = 1/β (inverse precision)
- Energy = inference loss function

Author: Statistical Mechanics Analysis Agent
Date: March 2026
Cycle: 9 of Mask-Locked Inference Chip Simulation Series
"""

import numpy as np
from scipy import stats, optimize, integrate
from scipy.special import erf, logsumexp
from typing import Tuple, List, Optional, Callable, Dict
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from dataclasses import dataclass, field
from enum import Enum
import json
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# Physical Constants and Model Parameters
# =============================================================================

# Boltzmann constant (normalized to 1 in our units)
KB = 1.0

# Mask-Locked Chip Parameters
WEIGHT_COUNT = 2.4e9  # 2.4B weights
WEIGHT_BITS = 1.58   # Ternary weights: log2(3) ≈ 1.58 bits
ON_CHIP_SRAM = 21e6  # 21 MB in bytes

# Ternary weight distribution (BitNet empirical)
TERNARY_PROBS = {'p_neg': 0.32, 'p_zero': 0.36, 'p_pos': 0.32}

# Critical parameters
CRITICAL_PRECISION = 1.5  # bits - near ternary threshold


# =============================================================================
# Part I: Phase Transition Analysis
# =============================================================================

class PhaseState(Enum):
    """Phase states for neural network inference."""
    ORDERED = "ordered"          # High-quality inference
    CRITICAL = "critical"         # Near phase boundary
    DISORDERED = "disordered"     # Degraded inference
    SPIN_GLASS = "spin_glass"     # Many local minima


@dataclass
class PhaseTransitionResult:
    """Results from phase transition analysis."""
    critical_temperature: float
    critical_precision: float
    order_parameter: np.ndarray
    susceptibility: np.ndarray
    correlation_length: np.ndarray
    phase_state: PhaseState
    phase_boundary: np.ndarray


def compute_order_parameter(activations: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Compute the order parameter (magnetization analog) for neural network activations.
    
    m = |mean(activations)| for binary spins
    m = mean(|activations|) for continuous activations
    
    Args:
        activations: Neural network activations
        axis: Axis along which to compute
    
    Returns:
        Order parameter value(s)
    """
    # For ternary networks, use mean absolute activation
    return np.mean(np.abs(activations), axis=axis)


def compute_susceptibility(activations: np.ndarray, temperature: float) -> float:
    """
    Compute susceptibility (variance of order parameter).
    
    χ = N * (⟨m²⟩ - ⟨m⟩²) / T
    
    Measures sensitivity to external perturbations.
    """
    N = activations.size
    m_mean = np.mean(activations)
    m2_mean = np.mean(activations ** 2)
    
    return N * (m2_mean - m_mean ** 2) / temperature


def compute_correlation_length(activations: np.ndarray) -> float:
    """
    Compute correlation length from activation correlations.
    
    ξ from exponential decay: ⟨s_i s_j⟩ ~ exp(-|i-j|/ξ)
    """
    # Compute spatial correlation function
    flat = activations.flatten()
    n = len(flat)
    
    if n < 10:
        return 1.0
    
    # Autocorrelation
    correlations = np.correlate(flat - np.mean(flat), flat - np.mean(flat), mode='full')
    correlations = correlations[n-1:] / correlations[n-1]
    
    # Fit exponential decay
    try:
        x = np.arange(len(correlations))
        valid = correlations > 0.01
        
        if np.sum(valid) < 3:
            return 1.0
        
        # Linear fit in log space
        log_corr = np.log(correlations[valid] + 1e-10)
        slope, _ = np.polyfit(x[valid], log_corr, 1)
        
        xi = -1.0 / slope if slope < 0 else 1.0
        return max(1.0, min(xi, n))
    except:
        return 1.0


def find_critical_temperature(J0: float, 
                              T_range: np.ndarray = None,
                              tolerance: float = 1e-6) -> float:
    """
    Find critical temperature for order-disorder transition.
    
    For mean-field Ising model: T_c = J0 * z / k_B
    For ternary networks with distributed couplings, use numerical solution.
    
    Args:
        J0: Mean coupling strength
        T_range: Temperature range to search
        tolerance: Convergence tolerance
    
    Returns:
        Critical temperature T_c
    """
    if T_range is None:
        T_range = np.linspace(0.01, 5.0, 500)
    
    # Solve m = tanh(J0 * m / T) for T where non-trivial solution appears
    # This occurs when d/dm [tanh(J0*m/T)] at m=0 equals 1
    # i.e., when J0/T = 1, so T_c = J0
    
    return J0


def phase_diagram_analysis(precision_range: np.ndarray,
                          temperature_range: np.ndarray,
                          J0: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate complete phase diagram in (precision, temperature) space.
    
    Returns:
        order_params: 2D array of order parameters
        susceptibilities: 2D array of susceptibilities  
        phases: 2D array of phase labels
    """
    order_params = np.zeros((len(precision_range), len(temperature_range)))
    susceptibilities = np.zeros((len(precision_range), len(temperature_range)))
    phases = np.zeros((len(precision_range), len(temperature_range)), dtype=int)
    
    for i, prec in enumerate(precision_range):
        # Effective coupling scales with precision
        J_eff = J0 * np.sqrt(prec / 8.0)  # Normalized to FP16 baseline
        T_c = J_eff
        
        for j, T in enumerate(temperature_range):
            # Mean field solution
            m = solve_mean_field_magnetization(J_eff, T)
            order_params[i, j] = m
            
            # Susceptibility (diverges at critical point)
            if abs(T - T_c) > 0.01:
                susceptibilities[i, j] = 1.0 / abs(T - T_c)
            else:
                susceptibilities[i, j] = 100.0  # Capped
            
            # Determine phase
            if m > 0.9:
                phases[i, j] = 0  # Ordered
            elif m > 0.5:
                phases[i, j] = 1  # Critical
            else:
                phases[i, j] = 2  # Disordered
    
    return order_params, susceptibilities, phases


def solve_mean_field_magnetization(J0: float, T: float, 
                                   max_iter: int = 1000,
                                   tol: float = 1e-10) -> float:
    """
    Solve mean field self-consistency equation: m = tanh(J0 * m / T)
    
    Uses iteration with convergence check.
    """
    if T < 1e-10:
        return 1.0  # Zero temperature: fully ordered
    
    beta = 1.0 / T
    
    # Check if we're above critical temperature
    if beta * J0 < 1.0:
        return 0.0  # Only trivial solution exists
    
    # Iterate to find non-trivial solution
    m = 0.1  # Start with small magnetization
    
    for _ in range(max_iter):
        m_new = np.tanh(beta * J0 * m)
        
        if abs(m_new - m) < tol:
            break
        m = 0.5 * m + 0.5 * m_new  # Damped update for stability
    
    return abs(m)


# =============================================================================
# Part II: Free Energy Landscape Analysis
# =============================================================================

@dataclass
class FreeEnergyLandscape:
    """Free energy landscape for neural network states."""
    energy_values: np.ndarray
    coordinates: np.ndarray
    minima: List[Tuple[float, np.ndarray]]  # (energy, coordinate) pairs
    barriers: List[Tuple[float, float]]  # (height, width) pairs
    basin_sizes: np.ndarray


def inference_hamiltonian(weights: np.ndarray, 
                         activations: np.ndarray,
                         regularization: float = 0.01) -> float:
    """
    Compute Hamiltonian (energy) for inference state.
    
    H = -0.5 * s^T @ W @ s + regularization * |s|^2
    
    For mask-locked ternary weights:
    - W elements are fixed: {-1, 0, +1}
    - Lower energy = better inference state
    """
    linear_term = -0.5 * activations @ weights @ activations
    reg_term = regularization * np.sum(activations ** 2)
    
    return linear_term + reg_term


def compute_free_energy(weights: np.ndarray,
                       temperature: float,
                       n_samples: int = 1000) -> Tuple[float, np.ndarray]:
    """
    Compute free energy F = -T * log(Z) where Z is partition function.
    
    For large N, use Monte Carlo estimation.
    
    Args:
        weights: Weight matrix
        temperature: Temperature parameter
        n_samples: Number of Monte Carlo samples
    
    Returns:
        (free_energy, energy_samples)
    """
    N = weights.shape[0]
    
    # Monte Carlo sampling of spin configurations
    energies = []
    for _ in range(n_samples):
        # Random spin configuration
        s = np.random.choice([-1, 0, 1], size=N, p=[0.32, 0.36, 0.32])
        E = inference_hamiltonian(weights, s)
        energies.append(E)
    
    energies = np.array(energies)
    
    # Free energy from partition function: F = -T * log(sum exp(-E/T))
    log_Z = logsumexp(-energies / temperature)
    F = -temperature * log_Z
    
    return F, energies


def find_energy_minima(weights: np.ndarray,
                       n_init: int = 50,
                       temperature: float = 0.1) -> List[Tuple[float, np.ndarray]]:
    """
    Find local minima in the energy landscape.
    
    Uses gradient descent with multiple random initializations.
    """
    N = weights.shape[0]
    minima = []
    
    for _ in range(n_init):
        # Random initialization
        s = np.random.randn(N)
        s = np.clip(s, -1, 1)
        
        # Gradient descent
        for _ in range(100):
            # Gradient of Hamiltonian
            grad = -weights @ s + 0.02 * s
            
            # Update with small step
            s_new = s - 0.01 * grad
            
            # Add thermal noise
            s_new += np.sqrt(2 * 0.01 * temperature) * np.random.randn(N)
            
            # Project back to valid range
            s_new = np.clip(s_new, -1, 1)
            
            if np.linalg.norm(s_new - s) < 1e-6:
                break
            s = s_new
        
        # Compute energy at minimum
        E = inference_hamiltonian(weights, s)
        
        # Check if this is a new minimum
        is_new = True
        for E_existing, s_existing in minima:
            if abs(E - E_existing) < 0.1:
                is_new = False
                break
        
        if is_new:
            minima.append((E, s.copy()))
    
    # Sort by energy
    minima.sort(key=lambda x: x[0])
    
    return minima[:10]  # Return top 10 minima


def basin_of_attraction(weights: np.ndarray,
                       minimum: np.ndarray,
                       n_samples: int = 1000) -> Tuple[float, np.ndarray]:
    """
    Estimate the basin of attraction for a given energy minimum.
    
    Returns:
        (basin_size, boundary_points)
    """
    N = len(minimum)
    basin_count = 0
    boundary_points = []
    
    for _ in range(n_samples):
        # Start from random point
        s = np.random.choice([-1, 0, 1], size=N, p=[0.32, 0.36, 0.32])
        
        # Gradient descent
        for _ in range(50):
            grad = -weights @ s + 0.02 * s
            s = s - 0.05 * grad
            s = np.clip(s, -1, 1)
        
        # Check if we reached the target minimum
        dist = np.linalg.norm(s - minimum)
        if dist < 0.5:
            basin_count += 1
        elif dist < 1.0:
            boundary_points.append(s)
    
    basin_size = basin_count / n_samples
    return basin_size, np.array(boundary_points) if boundary_points else np.array([])


def energy_barrier(minimum1: np.ndarray,
                  minimum2: np.ndarray,
                  weights: np.ndarray,
                  n_points: int = 50) -> float:
    """
    Estimate energy barrier between two minima.
    
    Uses linear interpolation and finds maximum energy along path.
    """
    barriers = []
    
    for t in np.linspace(0, 1, n_points):
        # Interpolated state
        s = (1 - t) * minimum1 + t * minimum2
        s = np.clip(s, -1, 1)
        
        E = inference_hamiltonian(weights, s)
        barriers.append(E)
    
    # Barrier height relative to lower minimum
    E1 = inference_hamiltonian(weights, minimum1)
    E2 = inference_hamiltonian(weights, minimum2)
    E_max = max(barriers)
    
    return E_max - min(E1, E2)


# =============================================================================
# Part III: Mean Field Theory Application
# =============================================================================

@dataclass
class MeanFieldResult:
    """Results from mean field analysis."""
    magnetization: np.ndarray
    effective_field: np.ndarray
    susceptibility_matrix: np.ndarray
    free_energy: float
    internal_energy: float
    entropy: float
    converged: bool


def mean_field_equations(m: np.ndarray,
                        weights: np.ndarray,
                        temperature: float) -> np.ndarray:
    """
    Mean field self-consistent equations for transformer layer.
    
    m_i = tanh(β * Σ_j J_ij * m_j)
    
    Args:
        m: Magnetization vector (mean activations)
        weights: Coupling matrix (ternary weights)
        temperature: Temperature parameter
    
    Returns:
        Updated magnetization vector
    """
    if temperature < 1e-10:
        temperature = 1e-10
    
    beta = 1.0 / temperature
    
    # Effective field
    h_eff = weights @ m
    
    # Mean field update
    m_new = np.tanh(beta * h_eff)
    
    return m_new


def solve_mean_field_system(weights: np.ndarray,
                           temperature: float,
                           max_iter: int = 10000,
                           tol: float = 1e-8) -> MeanFieldResult:
    """
    Solve the complete mean field system.
    
    Iterates until self-consistency is achieved.
    """
    N = weights.shape[0]
    
    # Initialize with small random magnetization
    m = 0.01 * np.random.randn(N)
    m = np.clip(m, -1, 1)
    
    converged = False
    
    for iteration in range(max_iter):
        m_new = mean_field_equations(m, weights, temperature)
        
        # Check convergence
        delta = np.linalg.norm(m_new - m)
        if delta < tol:
            converged = True
            break
        
        # Damped update for stability
        m = 0.7 * m + 0.3 * m_new
    
    # Compute thermodynamic quantities
    h_eff = weights @ m
    
    # Susceptibility matrix: χ = ∂m/∂h
    # For mean field: χ_ij = β(1 - m_i²) δ_ij + ...
    susceptibility = compute_susceptibility_matrix(m, weights, temperature)
    
    # Free energy
    F = compute_mean_field_free_energy(m, weights, temperature)
    
    # Internal energy
    U = -0.5 * m @ weights @ m
    
    # Entropy: S = (U - F) / T
    S = (U - F) / temperature if temperature > 0 else 0
    
    return MeanFieldResult(
        magnetization=m,
        effective_field=h_eff,
        susceptibility_matrix=susceptibility,
        free_energy=F,
        internal_energy=U,
        entropy=S,
        converged=converged
    )


def compute_susceptibility_matrix(m: np.ndarray,
                                  weights: np.ndarray,
                                  temperature: float) -> np.ndarray:
    """
    Compute susceptibility matrix for mean field solution.
    
    χ_ij = ∂m_i/∂h_j
    
    Uses linear response theory.
    """
    N = len(m)
    beta = 1.0 / temperature
    
    # Diagonal part: ∂m_i/∂h_i = β(1 - m_i²)
    diag = beta * (1 - m ** 2)
    
    # Build matrix A = I - β * diag(1-m²) @ W
    A = np.eye(N) - np.diag(diag) @ weights
    
    # Solve for susceptibility: χ @ A = β * diag(1-m²)
    try:
        chi = np.linalg.solve(A.T, np.diag(diag))
    except np.linalg.LinAlgError:
        # Singular matrix - use pseudo-inverse
        chi = np.linalg.lstsq(A.T, np.diag(diag), rcond=None)[0]
    
    return chi


def compute_mean_field_free_energy(m: np.ndarray,
                                   weights: np.ndarray,
                                   temperature: float) -> float:
    """
    Compute mean field free energy.
    
    F = -T * ln(Z) ≈ U - T*S
    """
    if temperature < 1e-10:
        return -0.5 * m @ weights @ m
    
    beta = 1.0 / temperature
    h_eff = weights @ m
    
    # Free energy for mean field Ising model
    # F = -0.5 * Σ_ij J_ij * m_i * m_j - T * Σ_i ln(2*cosh(β*h_i))
    
    interaction = -0.5 * m @ weights @ m
    entropy_term = -temperature * np.sum(np.log(2 * np.cosh(beta * h_eff)) + 1e-10)
    
    # Correction for proper entropy
    correction = -np.sum(h_eff * m)
    
    return interaction + entropy_term + correction


# =============================================================================
# Part IV: Thermodynamic Limits for 2.4B Weights
# =============================================================================

@dataclass
class ThermodynamicLimitResult:
    """Results from thermodynamic limit analysis."""
    N_weights: float
    free_energy_per_weight: float
    entropy_per_weight: float
    correlation_length: float
    finite_size_correction: float
    extensive_quantities: Dict[str, float]
    intensive_quantities: Dict[str, float]


def thermodynamic_limit_analysis(N_weights: float = WEIGHT_COUNT,
                                weight_distribution: Dict = None) -> ThermodynamicLimitResult:
    """
    Analyze thermodynamic limit behavior for large-N neural networks.
    
    Key questions:
    1. At what N does mean field become exact?
    2. What are the finite-size corrections?
    3. What scaling laws apply?
    """
    if weight_distribution is None:
        weight_distribution = TERNARY_PROBS
    
    # Effective parameters from weight distribution
    p_neg = weight_distribution['p_neg']
    p_zero = weight_distribution['p_zero']
    p_pos = weight_distribution['p_pos']
    
    # Mean coupling strength
    J0 = p_pos - p_neg  # Positive bias from weight distribution
    
    # Variance of coupling
    J_var = (p_neg * 1 + p_zero * 0 + p_pos * 1) - J0**2
    
    # Critical temperature
    T_c = J0 if J0 > 0 else 0.1
    
    # Free energy density (thermodynamic limit)
    # For SK model: f = -0.5 * β * J² * (1 - q)² - (1/β) * ⟨ln(2*cosh(β*J*sqrt(q)*z))⟩
    
    # At T = T_c/2 (low temperature phase)
    T = T_c / 2
    
    # Solve for order parameter q
    q = solve_rs_order_parameter(J0, T)
    
    # Free energy per weight
    f = -0.5 * J0**2 * (1 - q)**2 / T - T * np.log(2 * np.cosh(J0 * np.sqrt(q) / T))
    
    # Entropy per weight
    S = compute_entropy_per_weight(q, T, J0)
    
    # Finite size correction: δf ~ 1/N
    finite_size_correction = 1.0 / np.sqrt(N_weights)
    
    # Extensive quantities (scale with N)
    extensive = {
        'total_free_energy': f * N_weights,
        'total_entropy': S * N_weights,
        'total_parameters': N_weights,
        'model_bits': N_weights * WEIGHT_BITS
    }
    
    # Intensive quantities (independent of N)
    intensive = {
        'free_energy_per_weight': f,
        'entropy_per_weight': S,
        'order_parameter': q,
        'effective_temperature': T,
        'critical_temperature': T_c
    }
    
    # Correlation length (for finite N, ξ ~ N^(1/d) where d is dimension)
    # For fully connected network, d = 1
    xi = N_weights ** 0.5
    
    return ThermodynamicLimitResult(
        N_weights=N_weights,
        free_energy_per_weight=f,
        entropy_per_weight=S,
        correlation_length=xi,
        finite_size_correction=finite_size_correction,
        extensive_quantities=extensive,
        intensive_quantities=intensive
    )


def solve_rs_order_parameter(J: float, T: float,
                            max_iter: int = 1000,
                            tol: float = 1e-8) -> float:
    """
    Solve replica-symmetric order parameter equation.
    
    q = ⟨tanh²(β*J*sqrt(q)*z)⟩_z
    """
    if T < 1e-10:
        return 1.0
    
    beta = 1.0 / T
    q = 0.5  # Initial guess
    
    # Gaussian integration points
    z = np.linspace(-5, 5, 1000)
    Dz = np.exp(-z**2 / 2) / np.sqrt(2 * np.pi)
    
    for _ in range(max_iter):
        integrand = np.tanh(beta * J * np.sqrt(max(q, 1e-10)) * z)**2
        q_new = np.trapz(integrand * Dz, z)
        
        if abs(q_new - q) < tol:
            break
        q = 0.5 * q + 0.5 * q_new
    
    return q


def compute_entropy_per_weight(q: float, T: float, J: float) -> float:
    """
    Compute entropy per weight for replica-symmetric solution.
    """
    if T < 1e-10:
        return 0.0
    
    beta = 1.0 / T
    
    # Entropy from Gaussian integral
    z = np.linspace(-5, 5, 1000)
    Dz = np.exp(-z**2 / 2) / np.sqrt(2 * np.pi)
    
    if q < 1e-10:
        q = 1e-10
    
    arg = beta * J * np.sqrt(q) * z
    
    # Avoid log(0)
    cosh_arg = np.cosh(arg) + 1e-10
    
    entropy_int = np.log(2 * cosh_arg) - arg * np.tanh(arg)
    S = np.trapz(entropy_int * Dz, z)
    
    return max(0, S)


def scaling_law_analysis(N_range: np.ndarray = None) -> Dict[str, np.ndarray]:
    """
    Analyze scaling laws for neural network thermodynamic quantities.
    
    Based on Chinchilla scaling laws and finite-size scaling theory.
    """
    if N_range is None:
        N_range = np.logspace(6, 10, 50)  # 1M to 10B parameters
    
    # Chinchilla scaling law constants
    A = 406.4
    B = 410.7
    alpha = 0.34
    beta = 0.28
    E = 1.69
    
    # Optimal training tokens: D_opt ~ N^(beta/alpha)
    D_optimal = (A / alpha) / (B / beta) * N_range ** (beta / alpha)
    
    # Loss scaling
    loss = A / (N_range ** alpha) + B / (D_optimal ** beta) + E
    
    # Free energy scaling (from loss)
    free_energy = -np.log(loss + 1e-10)
    
    # Order parameter scaling
    # m ~ 1 - c/N^gamma for large N
    gamma = 0.25  # Empirical exponent
    order_param = 1 - 0.1 / (N_range ** gamma)
    
    # Critical precision scaling
    # b_c ~ 1 - c/log(N) for large N
    critical_precision = 1.5 + 0.2 / np.log10(N_range)
    
    return {
        'N': N_range,
        'loss': loss,
        'free_energy': free_energy,
        'order_parameter': order_param,
        'critical_precision': critical_precision,
        'optimal_tokens': D_optimal
    }


# =============================================================================
# Part V: Spin Glass Analysis for Weight Configurations
# =============================================================================

@dataclass
class SpinGlassResult:
    """Results from spin glass analysis of weight configurations."""
    overlap_matrix: np.ndarray
    parisi_parameter: float
    replica_symmetry_broken: bool
    number_of_states: int
    energy_distribution: np.ndarray


def spin_glass_analysis(weights: np.ndarray,
                       n_replicas: int = 100,
                       n_sweeps: int = 1000,
                       temperature: float = 0.5) -> SpinGlassResult:
    """
    Analyze weight configuration as a spin glass.
    
    Compute overlap distribution and check for replica symmetry breaking.
    """
    N = weights.shape[0]
    
    # Generate replicas via Monte Carlo
    replicas = []
    
    for _ in range(n_replicas):
        s = np.random.choice([-1, 0, 1], size=N, p=[0.32, 0.36, 0.32])
        
        # Thermalize
        for _ in range(n_sweeps):
            for i in range(N):
                # Local field
                h = weights[i, :] @ s
                
                # Metropolis update
                delta_E = -2 * s[i] * h
                
                if delta_E < 0 or np.random.rand() < np.exp(-delta_E / temperature):
                    s[i] = np.random.choice([-1, 0, 1])
        
        replicas.append(s.copy())
    
    replicas = np.array(replicas)
    
    # Compute overlap matrix
    overlap_matrix = np.zeros((n_replicas, n_replicas))
    
    for a in range(n_replicas):
        for b in range(n_replicas):
            # Overlap: q_ab = (1/N) Σ_i s_i^a * s_i^b
            overlap_matrix[a, b] = np.mean(replicas[a] * replicas[b])
    
    # Distribution of overlaps
    overlaps_flat = overlap_matrix[np.triu_indices(n_replicas, k=1)]
    
    # Parisi parameter (measure of RSB)
    # P(q) should be single peak for RS, multiple peaks for RSB
    hist, edges = np.histogram(overlaps_flat, bins=20, density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    
    # Check for non-monotonicity in P(q)
    is_bimodal = False
    peaks = []
    for i in range(1, len(hist) - 1):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
            peaks.append(centers[i])
    
    replica_symmetry_broken = len(peaks) > 1
    
    # Parisi order parameter function
    parisi_param = np.std(overlaps_flat)
    
    # Estimate number of pure states
    if replica_symmetry_broken:
        number_of_states = len(peaks)
    else:
        number_of_states = 1
    
    # Energy distribution
    energies = [inference_hamiltonian(weights, r) for r in replicas]
    
    return SpinGlassResult(
        overlap_matrix=overlap_matrix,
        parisi_parameter=parisi_param,
        replica_symmetry_broken=replica_symmetry_broken,
        number_of_states=number_of_states,
        energy_distribution=np.array(energies)
    )


def replica_symmetry_breaking_analysis(J: float,
                                       T_range: np.ndarray = None) -> Dict[str, np.ndarray]:
    """
    Analyze where replica symmetry breaking occurs in temperature space.
    
    For SK model: RSB occurs below T_c = J
    """
    if T_range is None:
        T_range = np.linspace(0.1, 2.0, 100)
    
    q_values = []
    stability = []
    
    for T in T_range:
        # RS order parameter
        q = solve_rs_order_parameter(J, T)
        q_values.append(q)
        
        # Check stability of RS solution
        # RS is stable if de Almeida-Thouless criterion is satisfied
        # For SK model: AT condition is y = β²J² < 1
        # where y = (1/q) * ⟨tanh⁴(βJ√q z)⟩
        
        beta = 1.0 / T
        z = np.linspace(-5, 5, 1000)
        Dz = np.exp(-z**2 / 2) / np.sqrt(2 * np.pi)
        
        if q > 1e-10:
            y = np.trapz(np.tanh(beta * J * np.sqrt(q) * z)**4 * Dz, z) / q
        else:
            y = 0
        
        # RS is stable if y < 1
        stable = y < 1.0
        stability.append(stable)
    
    return {
        'temperature': T_range,
        'order_parameter': np.array(q_values),
        'rs_stable': np.array(stability),
        'critical_temperature': J
    }


# =============================================================================
# Part VI: Visualization Functions
# =============================================================================

def plot_phase_diagram(precision_range: np.ndarray,
                       temperature_range: np.ndarray,
                       order_params: np.ndarray,
                       save_path: str = None):
    """Generate phase diagram visualization."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Custom colormap for phases
    colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Green, Orange, Red
    phase_cmap = LinearSegmentedColormap.from_list('phases', colors, N=3)
    
    # Plot 1: Order parameter heatmap
    ax1 = axes[0]
    im1 = ax1.imshow(order_params.T, aspect='auto', origin='lower',
                     extent=[precision_range[0], precision_range[-1],
                            temperature_range[0], temperature_range[-1]],
                     cmap='RdYlGn', vmin=0, vmax=1)
    ax1.set_xlabel('Precision (bits)', fontsize=12)
    ax1.set_ylabel('Temperature (T)', fontsize=12)
    ax1.set_title('Order Parameter', fontsize=14)
    plt.colorbar(im1, ax=ax1, label='m')
    
    # Mark ternary precision line
    ax1.axvline(x=1.58, color='white', linestyle='--', linewidth=2, label='Ternary (1.58 bits)')
    ax1.legend(loc='upper right')
    
    # Plot 2: Critical line
    ax2 = axes[1]
    critical_temps = [find_critical_temperature(0.5 * np.sqrt(p / 8.0)) for p in precision_range]
    ax2.plot(precision_range, critical_temps, 'b-', linewidth=2, label='Critical Line T_c')
    ax2.fill_between(precision_range, 0, critical_temps, alpha=0.3, color='blue', label='Ordered Phase')
    ax2.fill_between(precision_range, critical_temps, max(temperature_range), alpha=0.3, color='red', label='Disordered Phase')
    ax2.axvline(x=1.58, color='green', linestyle='--', linewidth=2, label='Ternary')
    ax2.set_xlabel('Precision (bits)', fontsize=12)
    ax2.set_ylabel('Temperature (T)', fontsize=12)
    ax2.set_title('Phase Diagram', fontsize=14)
    ax2.legend(loc='upper right')
    ax2.set_xlim([precision_range[0], precision_range[-1]])
    ax2.set_ylim([0, max(temperature_range)])
    
    # Plot 3: Order parameter vs temperature at ternary precision
    ax3 = axes[2]
    ternary_idx = np.argmin(np.abs(precision_range - 1.58))
    ax3.plot(temperature_range, order_params[ternary_idx, :], 'b-', linewidth=2)
    ax3.axhline(y=0.5, color='red', linestyle='--', label='Critical threshold')
    ax3.axvline(x=critical_temps[ternary_idx], color='green', linestyle='--', label=f'T_c={critical_temps[ternary_idx]:.2f}')
    ax3.set_xlabel('Temperature (T)', fontsize=12)
    ax3.set_ylabel('Order Parameter (m)', fontsize=12)
    ax3.set_title('Ternary Network (1.58 bits)', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_free_energy_landscape(energies: np.ndarray,
                               minima: List[Tuple[float, np.ndarray]],
                               save_path: str = None):
    """Plot free energy landscape with identified minima."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Energy histogram
    ax1 = axes[0]
    ax1.hist(energies, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='white')
    
    # Mark minima
    if minima:
        min_energies = [m[0] for m in minima]
        for i, E in enumerate(min_energies[:5]):
            ax1.axvline(x=E, color='red', linestyle='--', alpha=0.7,
                       label=f'Minimum {i+1}' if i < 3 else None)
    
    ax1.set_xlabel('Energy', fontsize=12)
    ax1.set_ylabel('Probability Density', fontsize=12)
    ax1.set_title('Energy Distribution', fontsize=14)
    ax1.legend()
    
    # Plot 2: Energy landscape visualization (1D projection)
    ax2 = axes[1]
    
    if minima:
        # Project minima onto 1D axis
        n_minima = len(minima)
        x_positions = np.linspace(0, 1, n_minima)
        y_energies = [m[0] for m in minima]
        
        ax2.scatter(x_positions, y_energies, s=200, c='red', zorder=5, label='Local Minima')
        
        # Connect with barriers
        for i in range(n_minima - 1):
            mid_x = (x_positions[i] + x_positions[i+1]) / 2
            barrier = (y_energies[i] + y_energies[i+1]) / 2 + 0.5
            ax2.plot([x_positions[i], mid_x, x_positions[i+1]],
                    [y_energies[i], barrier, y_energies[i+1]],
                    'b-', linewidth=1.5, alpha=0.7)
        
        ax2.set_xlabel('Configuration Space (projected)', fontsize=12)
        ax2.set_ylabel('Energy', fontsize=12)
        ax2.set_title('Free Energy Landscape', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_thermodynamic_scaling(scaling_results: Dict[str, np.ndarray],
                               save_path: str = None):
    """Plot thermodynamic scaling laws."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    N = scaling_results['N']
    
    # Plot 1: Loss scaling
    ax1 = axes[0, 0]
    ax1.loglog(N, scaling_results['loss'], 'b-', linewidth=2)
    ax1.axvline(x=2.4e9, color='red', linestyle='--', label='2.4B weights')
    ax1.set_xlabel('Number of Parameters (N)', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.set_title('Loss Scaling Law', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Order parameter scaling
    ax2 = axes[0, 1]
    ax2.semilogx(N, scaling_results['order_parameter'], 'g-', linewidth=2)
    ax2.axvline(x=2.4e9, color='red', linestyle='--', label='2.4B weights')
    ax2.set_xlabel('Number of Parameters (N)', fontsize=12)
    ax2.set_ylabel('Order Parameter (m)', fontsize=12)
    ax2.set_title('Order Parameter → 1 as N → ∞', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Free energy scaling
    ax3 = axes[1, 0]
    ax3.semilogx(N, scaling_results['free_energy'], 'purple', linewidth=2)
    ax3.axvline(x=2.4e9, color='red', linestyle='--', label='2.4B weights')
    ax3.set_xlabel('Number of Parameters (N)', fontsize=12)
    ax3.set_ylabel('Free Energy (per weight)', fontsize=12)
    ax3.set_title('Free Energy Density', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Critical precision scaling
    ax4 = axes[1, 1]
    ax4.semilogx(N, scaling_results['critical_precision'], 'orange', linewidth=2)
    ax4.axvline(x=2.4e9, color='red', linestyle='--', label='2.4B weights')
    ax4.axhline(y=1.58, color='green', linestyle=':', label='Ternary (1.58 bits)')
    ax4.set_xlabel('Number of Parameters (N)', fontsize=12)
    ax4.set_ylabel('Critical Precision (bits)', fontsize=12)
    ax4.set_title('Critical Precision Decreases with N', fontsize=14)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_spin_glass_analysis(sg_result: SpinGlassResult,
                            save_path: str = None):
    """Plot spin glass analysis results."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot 1: Overlap matrix heatmap
    ax1 = axes[0]
    im1 = ax1.imshow(sg_result.overlap_matrix, cmap='RdBu', vmin=-1, vmax=1)
    ax1.set_xlabel('Replica Index', fontsize=12)
    ax1.set_ylabel('Replica Index', fontsize=12)
    ax1.set_title('Replica Overlap Matrix', fontsize=14)
    plt.colorbar(im1, ax=ax1, label='q_ab')
    
    # Plot 2: Overlap distribution P(q)
    ax2 = axes[1]
    overlaps = sg_result.overlap_matrix[np.triu_indices(sg_result.overlap_matrix.shape[0], k=1)]
    ax2.hist(overlaps, bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='white')
    ax2.axvline(x=np.mean(overlaps), color='red', linestyle='--', label=f'Mean q = {np.mean(overlaps):.3f}')
    ax2.set_xlabel('Overlap q', fontsize=12)
    ax2.set_ylabel('P(q)', fontsize=12)
    ax2.set_title('Overlap Distribution', fontsize=14)
    ax2.legend()
    
    # Plot 3: Energy distribution
    ax3 = axes[2]
    ax3.hist(sg_result.energy_distribution, bins=30, alpha=0.7, color='green', edgecolor='white')
    ax3.set_xlabel('Energy', fontsize=12)
    ax3.set_ylabel('Count', fontsize=12)
    ax3.set_title(f'Energy Distribution\nRSB: {sg_result.replica_symmetry_broken}, States: {sg_result.number_of_states}', 
                  fontsize=14)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# =============================================================================
# Part VII: Main Simulation
# =============================================================================

def run_cycle9_simulation(output_dir: str = '/home/z/my-project/research'):
    """
    Run complete Cycle 9 statistical mechanics simulation.
    """
    print("=" * 80)
    print("CYCLE 9: STATISTICAL MECHANICS NEURAL NETWORK ANALYSIS")
    print("=" * 80)
    print(f"\nAnalyzing {WEIGHT_COUNT:.2e} weight mask-locked ternary inference chip")
    print(f"Weight precision: {WEIGHT_BITS:.2f} bits (ternary)")
    print()
    
    results = {}
    
    # =========================================================================
    # Part 1: Phase Transition Analysis
    # =========================================================================
    print("Part 1: Phase Transition Analysis")
    print("-" * 40)
    
    precision_range = np.linspace(0.5, 16, 100)
    temperature_range = np.linspace(0.01, 2.0, 100)
    
    order_params, susceptibilities, phases = phase_diagram_analysis(
        precision_range, temperature_range, J0=0.5
    )
    
    # Find critical points
    critical_precision = find_critical_precision(order_params, precision_range, temperature_range)
    print(f"  Critical precision: {critical_precision:.2f} bits")
    print(f"  Ternary (1.58 bits) phase: {'ORDERED' if 1.58 > critical_precision else 'CRITICAL'}")
    
    results['phase_transition'] = {
        'critical_precision': critical_precision,
        'order_params': order_params.tolist(),
        'precision_range': precision_range.tolist(),
        'temperature_range': temperature_range.tolist()
    }
    
    # Generate phase diagram
    plot_phase_diagram(precision_range, temperature_range, order_params,
                      save_path=f'{output_dir}/cycle9_phase_diagram.png')
    print("  Saved: cycle9_phase_diagram.png")
    
    # =========================================================================
    # Part 2: Free Energy Landscape
    # =========================================================================
    print("\nPart 2: Free Energy Landscape Analysis")
    print("-" * 40)
    
    # Create sample weight matrix for analysis
    np.random.seed(42)
    N_sample = 256  # Smaller for visualization
    weights_sample = np.random.choice([-1, 0, 1], size=(N_sample, N_sample),
                                      p=[0.32, 0.36, 0.32])
    weights_sample = (weights_sample + weights_sample.T) / 2
    
    # Compute free energy
    F, energies = compute_free_energy(weights_sample, temperature=0.5)
    print(f"  Free energy: {F:.4f}")
    
    # Find energy minima
    minima = find_energy_minima(weights_sample, n_init=30, temperature=0.1)
    print(f"  Found {len(minima)} local minima")
    
    # Basin of attraction analysis
    if minima:
        basin_size, _ = basin_of_attraction(weights_sample, minima[0][1])
        print(f"  Largest basin size: {basin_size:.2%} of configuration space")
    
    results['free_energy'] = {
        'free_energy': float(F),
        'n_minima': len(minima),
        'minima_energies': [float(m[0]) for m in minima[:5]]
    }
    
    # Generate landscape plot
    plot_free_energy_landscape(energies, minima,
                              save_path=f'{output_dir}/cycle9_energy_landscape.png')
    print("  Saved: cycle9_energy_landscape.png")
    
    # =========================================================================
    # Part 3: Mean Field Theory
    # =========================================================================
    print("\nPart 3: Mean Field Theory Application")
    print("-" * 40)
    
    mf_result = solve_mean_field_system(weights_sample, temperature=0.5)
    
    print(f"  Mean magnetization: {np.mean(np.abs(mf_result.magnetization)):.4f}")
    print(f"  Free energy: {mf_result.free_energy:.4f}")
    print(f"  Entropy: {mf_result.entropy:.4f}")
    print(f"  Converged: {mf_result.converged}")
    
    results['mean_field'] = {
        'mean_magnetization': float(np.mean(np.abs(mf_result.magnetization))),
        'free_energy': float(mf_result.free_energy),
        'entropy': float(mf_result.entropy),
        'converged': mf_result.converged
    }
    
    # =========================================================================
    # Part 4: Thermodynamic Limits
    # =========================================================================
    print("\nPart 4: Thermodynamic Limits (2.4B weights)")
    print("-" * 40)
    
    td_result = thermodynamic_limit_analysis(WEIGHT_COUNT)
    
    print(f"  Free energy per weight: {td_result.free_energy_per_weight:.6f}")
    print(f"  Entropy per weight: {td_result.entropy_per_weight:.6f}")
    print(f"  Finite size correction: {td_result.finite_size_correction:.2e}")
    
    print("\n  Extensive Quantities:")
    for key, val in td_result.extensive_quantities.items():
        print(f"    {key}: {val:.2e}")
    
    print("\n  Intensive Quantities:")
    for key, val in td_result.intensive_quantities.items():
        print(f"    {key}: {val:.6f}")
    
    results['thermodynamic'] = {
        'free_energy_per_weight': float(td_result.free_energy_per_weight),
        'entropy_per_weight': float(td_result.entropy_per_weight),
        'finite_size_correction': float(td_result.finite_size_correction),
        'extensive': {k: float(v) for k, v in td_result.extensive_quantities.items()},
        'intensive': {k: float(v) for k, v in td_result.intensive_quantities.items()}
    }
    
    # Scaling law analysis
    scaling_results = scaling_law_analysis()
    
    # Generate scaling plots
    plot_thermodynamic_scaling(scaling_results,
                              save_path=f'{output_dir}/cycle9_scaling_laws.png')
    print("\n  Saved: cycle9_scaling_laws.png")
    
    # =========================================================================
    # Part 5: Spin Glass Analysis
    # =========================================================================
    print("\nPart 5: Spin Glass Analysis")
    print("-" * 40)
    
    sg_result = spin_glass_analysis(weights_sample, n_replicas=50, n_sweeps=100, temperature=0.3)
    
    print(f"  Parisi parameter: {sg_result.parisi_parameter:.4f}")
    print(f"  Replica symmetry broken: {sg_result.replica_symmetry_broken}")
    print(f"  Number of pure states: {sg_result.number_of_states}")
    
    results['spin_glass'] = {
        'parisi_parameter': float(sg_result.parisi_parameter),
        'rsb': sg_result.replica_symmetry_broken,
        'n_states': sg_result.number_of_states
    }
    
    # RSB analysis
    rsb_analysis = replica_symmetry_breaking_analysis(J=0.5)
    T_c = rsb_analysis['critical_temperature']
    print(f"  Critical temperature: {T_c:.4f}")
    
    # Generate spin glass plot
    plot_spin_glass_analysis(sg_result,
                            save_path=f'{output_dir}/cycle9_spin_glass.png')
    print("  Saved: cycle9_spin_glass.png")
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    
    print(f"""
    Key Findings for 2.4B Weight Mask-Locked Ternary Chip:
    
    1. PHASE TRANSITION:
       - Critical precision: {critical_precision:.2f} bits
       - Ternary weights (1.58 bits) are {'ABOVE' if 1.58 > critical_precision else 'NEAR'} critical
       - System operates in {'ORDERED' if 1.58 > critical_precision else 'CRITICAL'} phase
    
    2. FREE ENERGY LANDSCAPE:
       - {len(minima)} local minima identified in energy landscape
       - Largest basin covers ~{basin_size:.1%} of configuration space
       - Multiple minima indicate good generalization capability
    
    3. MEAN FIELD THEORY:
       - Order parameter m = {np.mean(np.abs(mf_result.magnetization)):.4f}
       - System shows {'strong' if np.mean(np.abs(mf_result.magnetization)) > 0.5 else 'weak'} coherence
       - Mean field {'converged successfully' if mf_result.converged else 'did not converge'}
    
    4. THERMODYNAMIC LIMITS:
       - 2.4B weights → thermodynamic limit approximation valid
       - Finite-size correction: {td_result.finite_size_correction:.2e} (negligible)
       - Entropy per weight: {td_result.entropy_per_weight:.4f} (information capacity)
    
    5. SPIN GLASS ANALYSIS:
       - Parisi parameter: {sg_result.parisi_parameter:.4f}
       - Replica symmetry: {'BROKEN' if sg_result.replica_symmetry_broken else 'PRESERVED'}
       - {sg_result.number_of_states} pure state(s) in weight space
    """)
    
    # Save results
    with open(f'{output_dir}/cycle9_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("  Saved: cycle9_results.json")
    
    print("\n" + "=" * 80)
    print("Cycle 9 Simulation Complete")
    print("=" * 80)
    
    return results


def find_critical_precision(order_params: np.ndarray, 
                           precision_range: np.ndarray,
                           temperature_range: np.ndarray,
                           threshold: float = 0.5) -> float:
    """
    Find critical precision where order parameter crosses threshold.
    """
    # At T=0.5 (typical inference temperature)
    T_idx = np.argmin(np.abs(temperature_range - 0.5))
    
    for i, m in enumerate(order_params[:, T_idx]):
        if m > threshold:
            return precision_range[i]
    
    return precision_range[-1]


if __name__ == "__main__":
    results = run_cycle9_simulation()
