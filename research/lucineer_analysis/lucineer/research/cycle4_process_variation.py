#!/usr/bin/env python3
"""
Process Variation Monte Carlo Simulation - Corrected Version
==============================================================
Mask-Locked Inference Chip - Cycle 4B

Realistic power and performance modeling with process variations.

Author: Process Engineering Agent
Date: 2024
"""

import numpy as np
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import warnings
warnings.filterwarnings('ignore')

# Physical constants
K_B = 1.38e-23
Q_E = 1.602e-19
EPSILON_0 = 8.854e-12
EPSILON_OX = 3.9


@dataclass
class ChipParameters:
    """Chip-level parameters for realistic modeling."""
    # Process node
    process_node: str = "28nm"
    
    # PE array
    n_pes: int = 1024  # 32x32 systolic array
    pe_area: float = 160e-6 * 160e-6  # PE area in m²
    
    # Transistor parameters (typical 28nm)
    L_nom: float = 28e-9
    W_nom: float = 120e-9
    T_ox_nom: float = 1.2e-9
    Vth_nom: float = 0.35
    A_VT: float = 3.0e-3  # Pelgrom coefficient [V·μm]
    
    # Supply
    VDD: float = 0.9
    
    # Temperature
    T_ref: float = 300
    T_op: float = 350
    
    # Clock and timing
    target_freq: float = 1.0e9  # 1 GHz target
    pipeline_depth: int = 8
    
    # Power model parameters
    activity_factor: float = 0.15  # Average switching activity
    n_transistors_per_pe: int = 50000  # Transistors per PE
    
    # Metal stack
    metal_layers: int = 8
    via_R_nom: float = 15.0
    metal_W_nom: float = 40e-9
    
    # Spatial correlation
    pe_size: float = 160e-6
    corr_length: float = 50e-6


class RealisticMonteCarlo:
    """
    Monte Carlo simulation with realistic power and performance models.
    """
    
    def __init__(self, n_samples: int = 10000, seed: int = 42):
        self.n_samples = n_samples
        np.random.seed(seed)
        self.params = ChipParameters()
        
        # Variation magnitudes
        self.variations = {
            'vth_rdf': 18e-3,
            'vth_ler': 5e-3,
            'vth_wid': 15e-3,
            'vth_d2d': 25e-3,
            'L_eff': 0.05,
            'L_wid': 2e-9,
            'L_d2d': 3e-9,
            'T_ox': 0.02,
            'metal_W': 0.10,
            'via_R': 0.20,
        }
        
        # Setup spatial model
        self._setup_spatial_correlation()
        
    def _setup_spatial_correlation(self):
        """Pre-compute spatial correlation for within-die variations."""
        side = int(np.sqrt(self.params.n_pes))
        x = (np.arange(self.params.n_pes) % side + 0.5) * self.params.pe_size
        y = (np.arange(self.params.n_pes) // side + 0.5) * self.params.pe_size
        positions = np.column_stack([x, y])
        
        dist_matrix = squareform(pdist(positions))
        self.corr_matrix = np.exp(-dist_matrix / self.params.corr_length)
        
        try:
            self.chol = np.linalg.cholesky(self.corr_matrix + 1e-10 * np.eye(self.params.n_pes))
        except:
            eigvals, eigvecs = np.linalg.eigh(self.corr_matrix)
            eigvals = np.maximum(eigvals, 1e-10)
            self.chol = eigvecs @ np.diag(np.sqrt(eigvals))
    
    def generate_spatial_correlated(self, n: int) -> np.ndarray:
        """Generate spatially correlated random variables."""
        z = np.random.randn(self.params.n_pes, n)
        return self.chol @ z
    
    def compute_pe_delay_variation(self, vth_eff: np.ndarray, L_eff: np.ndarray,
                                    T_ox_eff: np.ndarray) -> np.ndarray:
        """
        Compute delay variation using alpha-power model.
        
        τ ∝ C·VDD / I_ds where I_ds ∝ μ·C_ox·(W/L)·(Vgs-Vth)^α
        
        Returns delay in multiples of nominal (normalized).
        """
        # Effective parameters
        C_ox = EPSILON_0 * EPSILON_OX / T_ox_eff  # F/m²
        Vov = np.maximum(self.params.VDD - vth_eff, 0.05)
        
        # Alpha-power model (velocity saturation)
        alpha = 1.3
        
        # Mobility temperature dependence
        mu_factor = (self.params.T_op / self.params.T_ref) ** (-1.5)
        
        # Normalized delay: τ/τ_nom ∝ L/(Vov^α)
        # Base case: Vth_nom = 0.35, Vov_nom = 0.55
        Vov_nom = self.params.VDD - self.params.Vth_nom
        delay_factor = (L_eff / self.params.L_nom) * (Vov_nom / Vov) ** alpha / mu_factor
        
        return delay_factor
    
    def compute_power(self, vth_eff: np.ndarray, delay_factor: np.ndarray) -> np.ndarray:
        """
        Compute total chip power in Watts.
        
        P_total = P_dynamic + P_leakage
        
        Dynamic: P_dyn = α·C·V²·f (switching power)
        Leakage: P_leak = VDD·I_leak (subthreshold + gate leakage)
        """
        n_pes = self.params.n_pes
        n_trans = self.params.n_transistors_per_pe
        
        # --- Dynamic Power ---
        # Capacitance per transistor (simplified model)
        # C_gate = C_ox * W * L (intrinsic) + C_parasitic
        C_gate_per_trans = 2e-15  # ~2 fF per transistor at 28nm
        C_total = n_pes * n_trans * C_gate_per_trans
        
        # Effective frequency (scaled by delay variation)
        # When delay increases, max frequency decreases
        # f_eff = f_target / delay_factor (averaged over PEs)
        avg_delay_factor = np.mean(delay_factor, axis=0)
        f_eff = self.params.target_freq / avg_delay_factor
        
        # Dynamic power
        P_dyn = (self.params.activity_factor * C_total * self.params.VDD**2 * f_eff)
        
        # --- Leakage Power ---
        # Subthreshold leakage: I_sub = I_0 * exp(-q·Vth/nkT)
        # Temperature coefficient
        T = self.params.T_op
        n_factor = 1.5  # Subthreshold slope factor
        thermal_voltage = K_B * T / Q_E  # ~30 mV at 350K
        
        # Reference leakage current at nominal Vth
        I_leak_ref = 1e-10  # 100 pA per transistor at nominal
        
        # Leakage current dependence on Vth
        # I_leak ∝ exp(-Vth / (n * V_T))
        vth_nom = self.params.Vth_nom
        leakage_factor = np.exp((vth_nom - vth_eff) / (n_factor * thermal_voltage))
        
        # Total leakage current
        I_leak_total = n_pes * n_trans * I_leak_ref * leakage_factor
        
        # Leakage power
        P_leak = self.params.VDD * I_leak_total
        
        # Total power
        P_total = P_dyn + P_leak
        
        return P_total
    
    def compute_throughput(self, delay_factor: np.ndarray) -> np.ndarray:
        """
        Compute inference throughput in tokens/second.
        
        Throughput = f_clk / cycles_per_token
        cycles_per_token depends on matrix multiply operations
        """
        # Effective clock frequency
        avg_delay_factor = np.mean(delay_factor, axis=0)
        f_clk = self.params.target_freq / avg_delay_factor
        
        # Transformer inference parameters
        d_model = 768  # Model dimension (GPT-2 small)
        n_layers = 12
        
        # MACs per token for one layer: 2 * d_model² (attention) + 2 * d_model * 4*d_model (FFN)
        # Simplified: ~10 * d_model² MACs per layer
        macs_per_layer = 10 * d_model ** 2
        
        # With 1024 PEs at 1 GHz, we can do ~10^9 MACs/second
        # PE utilization with systolic array: ~70%
        pe_efficiency = 0.70
        
        # Throughput calculation
        # tokens/s = (PEs * f_clk * efficiency) / MACs_per_layer / n_layers
        throughput = (self.params.n_pes * f_clk * pe_efficiency) / (macs_per_layer * n_layers)
        
        return throughput
    
    def run_corner(self, corner: str) -> Dict:
        """Run Monte Carlo simulation for a single corner."""
        n = self.n_samples
        n_pes = self.params.n_pes
        
        # Corner Vth shifts
        corner_shifts = {
            'TT': 0, 'FF': -3 * self.variations['vth_wid'], 
            'SS': 3 * self.variations['vth_wid'],
            'FS': -1.5 * self.variations['vth_wid'],
            'SF': 1.5 * self.variations['vth_wid'],
        }
        
        # === Sample variations ===
        
        # Die-to-die (global) variations
        vth_d2d = np.random.normal(0, self.variations['vth_d2d'], n)
        L_d2d = np.random.normal(0, self.variations['L_d2d'], n)
        
        # Within-die (spatially correlated) variations
        vth_wid = self.generate_spatial_correlated(n) * self.variations['vth_wid']
        L_wid = self.generate_spatial_correlated(n) * self.variations['L_wid']
        
        # Random (uncorrelated) variations
        vth_rdf = np.random.normal(0, self.variations['vth_rdf'], (n_pes, n))
        vth_ler = np.random.normal(0, self.variations['vth_ler'], (n_pes, n))
        L_var = np.random.normal(0, self.variations['L_eff'], (n_pes, n))
        T_ox_var = np.random.normal(0, self.variations['T_ox'], (n_pes, n))
        
        # === Effective parameters ===
        
        # Vth: nominal + corner + d2d + wid + rdf + ler
        vth_eff = (self.params.Vth_nom + 
                   corner_shifts[corner] +
                   vth_d2d + 
                   vth_wid + 
                   vth_rdf + 
                   vth_ler)
        
        # L_eff: nominal * (1 + var) + d2d + wid
        L_eff = self.params.L_nom * (1 + L_var) + L_d2d + L_wid
        L_eff = np.maximum(L_eff, self.params.L_nom * 0.8)
        
        # T_ox: nominal * (1 + var)
        T_ox_eff = self.params.T_ox_nom * (1 + T_ox_var)
        T_ox_eff = np.maximum(T_ox_eff, self.params.T_ox_nom * 0.9)
        
        # === Compute performance ===
        
        delay_factor = self.compute_pe_delay_variation(vth_eff, L_eff, T_ox_eff)
        throughput = self.compute_throughput(delay_factor)
        power = self.compute_power(vth_eff, delay_factor)
        
        # === Statistics ===
        
        return {
            'corner': corner,
            'throughput_mean': float(np.mean(throughput)),
            'throughput_std': float(np.std(throughput)),
            'throughput_min': float(np.min(throughput)),
            'throughput_max': float(np.max(throughput)),
            'throughput_p5': float(np.percentile(throughput, 5)),
            'throughput_p95': float(np.percentile(throughput, 95)),
            'power_mean': float(np.mean(power)),
            'power_std': float(np.std(power)),
            'power_min': float(np.min(power)),
            'power_max': float(np.max(power)),
            'power_p5': float(np.percentile(power, 5)),
            'power_p95': float(np.percentile(power, 95)),
            'vth_mean': float(np.mean(vth_eff)),
            'vth_std': float(np.std(vth_eff)),
            'delay_factor_mean': float(np.mean(delay_factor)),
        }
    
    def compute_yield(self, throughput: np.ndarray, power: np.ndarray,
                      throughput_min: float, power_max: float) -> Dict:
        """Compute yield metrics."""
        return {
            'throughput_yield': float(np.mean(throughput >= throughput_min)),
            'power_yield': float(np.mean(power <= power_max)),
            'combined_yield': float(np.mean((throughput >= throughput_min) & 
                                           (power <= power_max))),
        }
    
    def sensitivity_analysis(self) -> Dict:
        """Analyze sensitivity of throughput to each variation source."""
        n = 2000
        results = {}
        
        # Base case
        base_throughput = self._run_sensitivity_run(n, use_all=True)
        base_var = np.var(base_throughput)
        
        # Individual sensitivities
        sensitivity_params = [
            ('vth_all', {'use_vth': False}),
            ('L_all', {'use_L': False}),
            ('T_ox', {'use_Tox': False}),
            ('vth_rdf_only', {'use_vth_rdf': False}),
            ('vth_wid_only', {'use_vth_wid': False}),
            ('vth_d2d_only', {'use_vth_d2d': False}),
        ]
        
        for name, flags in sensitivity_params:
            throughput = self._run_sensitivity_run(n, **flags)
            variance_reduction = 1 - np.var(throughput) / base_var
            results[name] = max(0, min(1, variance_reduction))
        
        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'sensitivities': results,
            'ranked': ranked,
            'dominant': ranked[0][0],
            'base_variance': float(base_var),
        }
    
    def _run_sensitivity_run(self, n: int, use_all: bool = True,
                              use_vth: bool = True, use_L: bool = True, 
                              use_Tox: bool = True,
                              use_vth_rdf: bool = True, use_vth_wid: bool = True,
                              use_vth_d2d: bool = True) -> np.ndarray:
        """Run sensitivity sample with selective variation sources."""
        n_pes = self.params.n_pes
        
        # Vth variations
        vth_d2d = np.random.normal(0, self.variations['vth_d2d'], n) if (use_vth and use_vth_d2d) else np.zeros(n)
        vth_wid = self.generate_spatial_correlated(n) * self.variations['vth_wid'] if (use_vth and use_vth_wid) else np.zeros((n_pes, n))
        vth_rdf = np.random.normal(0, self.variations['vth_rdf'], (n_pes, n)) if (use_vth and use_vth_rdf) else np.zeros((n_pes, n))
        vth_ler = np.random.normal(0, self.variations['vth_ler'], (n_pes, n)) if use_vth else np.zeros((n_pes, n))
        
        # L variations
        L_var = np.random.normal(0, self.variations['L_eff'], (n_pes, n)) if use_L else np.zeros((n_pes, n))
        L_d2d = np.random.normal(0, self.variations['L_d2d'], n) if use_L else np.zeros(n)
        L_wid = self.generate_spatial_correlated(n) * self.variations['L_wid'] if use_L else np.zeros((n_pes, n))
        
        # T_ox variations
        T_ox_var = np.random.normal(0, self.variations['T_ox'], (n_pes, n)) if use_Tox else np.zeros((n_pes, n))
        
        # Effective parameters
        vth_eff = self.params.Vth_nom + vth_d2d + vth_wid + vth_rdf + vth_ler
        L_eff = np.maximum(self.params.L_nom * (1 + L_var) + L_d2d + L_wid, self.params.L_nom * 0.8)
        T_ox_eff = np.maximum(self.params.T_ox_nom * (1 + T_ox_var), self.params.T_ox_nom * 0.9)
        
        delay_factor = self.compute_pe_delay_variation(vth_eff, L_eff, T_ox_eff)
        throughput = self.compute_throughput(delay_factor)
        
        return throughput


def main():
    """Main execution."""
    print("=" * 70)
    print("Process Variation Monte Carlo Simulation")
    print("Mask-Locked Inference Chip - Cycle 4B")
    print("=" * 70)
    
    # Initialize
    mc = RealisticMonteCarlo(n_samples=10000, seed=42)
    
    # Pelgrom model verification
    area_um2 = mc.params.W_nom * 1e6 * mc.params.L_nom * 1e6
    sigma_vth = mc.params.A_VT / np.sqrt(area_um2)
    print(f"\nPelgrom Model Verification:")
    print(f"  Process: {mc.params.process_node}")
    print(f"  Channel W × L = {mc.params.W_nom*1e9:.0f} × {mc.params.L_nom*1e9:.0f} nm")
    print(f"  σ(Vth) = {sigma_vth*1e3:.2f} mV")
    
    # Run all corners
    print("\n" + "=" * 70)
    print(f"Running Monte Carlo ({mc.n_samples:,} samples per corner)...")
    print("=" * 70)
    
    corners = ['TT', 'FF', 'SS', 'FS', 'SF']
    results = {}
    
    for corner in corners:
        print(f"  Corner {corner}...", end=" ", flush=True)
        results[corner] = mc.run_corner(corner)
        print(f"Done! (yield: {results[corner]['power_mean']:.2f}W)")
    
    # Sensitivity analysis
    print("\nRunning sensitivity analysis...", end=" ", flush=True)
    sensitivity = mc.sensitivity_analysis()
    print("Done!")
    
    # Specifications
    THROUGHPUT_MIN = 100  # tok/s
    POWER_MAX = 5.0       # W
    
    # Print results
    print("\n" + "=" * 70)
    print("YIELD ANALYSIS RESULTS")
    print("=" * 70)
    print(f"\nSpecifications: throughput ≥ {THROUGHPUT_MIN} tok/s, power ≤ {POWER_MAX} W")
    
    yield_summary = {}
    for corner in corners:
        r = results[corner]
        
        # Recompute yield with actual samples
        # We need to re-run to get samples - use stored statistics
        # Approximate yield using lognormal distribution
        t_mean, t_std = r['throughput_mean'], r['throughput_std']
        p_mean, p_std = r['power_mean'], r['power_std']
        
        # Use Chebyshev for robust yield estimate
        # At least (1 - 1/k²) samples within k std deviations
        throughput_yield = 1.0 if t_mean - 3*t_std >= THROUGHPUT_MIN else 0.99
        power_yield = 1.0 if p_mean + 3*p_std <= POWER_MAX else max(0, 1 - (p_mean - POWER_MAX)**2 / (9 * p_std**2))
        
        # More accurate: estimate from normal distribution
        throughput_yield = 1 - stats.norm.cdf(THROUGHPUT_MIN, t_mean, t_std)
        power_yield = stats.norm.cdf(POWER_MAX, p_mean, p_std)
        combined_yield = throughput_yield * power_yield
        
        yield_summary[corner] = {
            'throughput_yield': throughput_yield,
            'power_yield': power_yield,
            'combined_yield': combined_yield,
        }
        
        print(f"\n--- Corner {corner} ---")
        print(f"  Throughput: {t_mean:.1f} ± {t_std:.1f} tok/s")
        print(f"    Range: [{r['throughput_min']:.1f}, {r['throughput_max']:.1f}]")
        print(f"    5th-95th percentile: [{r['throughput_p5']:.1f}, {r['throughput_p95']:.1f}]")
        print(f"  Power: {p_mean:.2f} ± {p_std:.2f} W")
        print(f"    Range: [{r['power_min']:.2f}, {r['power_max']:.2f}]")
        print(f"    5th-95th percentile: [{r['power_p5']:.2f}, {r['power_p95']:.2f}]")
        print(f"  Yield (throughput): {throughput_yield*100:.2f}%")
        print(f"  Yield (power): {power_yield*100:.2f}%")
        print(f"  Combined Yield: {combined_yield*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS")
    print("=" * 70)
    print("  Variation contribution to throughput variance:")
    for var, sens in sensitivity['ranked']:
        print(f"    {var}: {sens*100:.1f}%")
    print(f"\n  Dominant variation: {sensitivity['dominant']}")
    
    print("\n" + "=" * 70)
    print("WORST-CASE ANALYSIS")
    print("=" * 70)
    for corner in corners:
        r = results[corner]
        print(f"  Corner {corner}:")
        print(f"    Min Throughput: {r['throughput_min']:.1f} tok/s")
        print(f"    Max Power: {r['power_max']:.2f} W")
        print(f"    Vth shift: {r['vth_mean']*1e3 - 350:.1f} mV")
    
    # Compile final report
    report = {
        'simulation_parameters': {
            'n_samples': mc.n_samples,
            'seed': 42,
            'process_node': mc.params.process_node,
            'n_pes': mc.params.n_pes,
            'target_frequency_ghz': mc.params.target_freq / 1e9,
            'supply_voltage_v': mc.params.VDD,
            'operating_temperature_k': mc.params.T_op,
            'pelgrom_coefficient': mc.params.A_VT,
            'spatial_correlation_length_um': mc.params.corr_length * 1e6,
        },
        'pelgrom_verification': {
            'channel_width_nm': mc.params.W_nom * 1e9,
            'channel_length_nm': mc.params.L_nom * 1e9,
            'sigma_vth_mv': sigma_vth * 1e3,
            'formula': 'σ(Vth) = A_VT / sqrt(WL)',
        },
        'specifications': {
            'throughput_min_tok_per_s': THROUGHPUT_MIN,
            'power_max_watts': POWER_MAX,
        },
        'yield_analysis': yield_summary,
        'corner_results': {
            corner: {
                'throughput_mean': r['throughput_mean'],
                'throughput_std': r['throughput_std'],
                'throughput_min': r['throughput_min'],
                'throughput_max': r['throughput_max'],
                'throughput_p5': r['throughput_p5'],
                'throughput_p95': r['throughput_p95'],
                'power_mean': r['power_mean'],
                'power_std': r['power_std'],
                'power_min': r['power_min'],
                'power_max': r['power_max'],
                'power_p5': r['power_p5'],
                'power_p95': r['power_p95'],
                'vth_mean_v': r['vth_mean'],
                'vth_std_v': r['vth_std'],
                'delay_factor_mean': r['delay_factor_mean'],
            }
            for corner, r in results.items()
        },
        'sensitivity_analysis': sensitivity,
        'worst_case': {
            corner: {
                'throughput': results[corner]['throughput_min'],
                'power': results[corner]['power_max'],
                'vth_v': results[corner]['vth_mean'],
            }
            for corner in corners
        },
        'variation_sources': {
            'threshold_voltage': {
                'sigma_rdf_mv': 18,
                'sigma_ler_mv': 5,
                'sigma_wid_mv': 15,
                'sigma_d2d_mv': 25,
            },
            'channel_length': {
                'delta_L_percent': 5,
                'sigma_wid_nm': 2,
                'sigma_d2d_nm': 3,
            },
            'oxide_thickness': {'delta_percent': 2},
            'metal_width': {'delta_percent': 10},
            'via_resistance': {'delta_percent': 20},
        },
    }
    
    # Save results
    output_path = '/home/z/my-project/research/cycle4_yield_results.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n\nResults saved to: {output_path}")
    
    return report


if __name__ == "__main__":
    results = main()
