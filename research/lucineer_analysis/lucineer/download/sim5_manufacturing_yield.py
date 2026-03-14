#!/usr/bin/env python3
"""
TernaryAir Simulation Framework
Iteration 5: Manufacturing Yield Simulation

Simulates manufacturing yield at 28nm:
- Defect density analysis
- Yield prediction for different die sizes
- Cost modeling for volume production
- Risk assessment

Author: Casey DiGennaro
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

@dataclass
class ProcessNode:
    """28nm process node parameters"""
    name: str = "28nm"
    defect_density_per_cm2: float = 0.5  # Average defects per cm²
    wafer_diameter_mm: float = 300
    wafer_cost_usd: float = 3000
    mask_cost_usd: float = 2500000
    min_feature_nm: int = 28
    metal_layers: int = 6
    
@dataclass
class DieConfig:
    """Die configuration"""
    name: str
    width_mm: float
    height_mm: float
    sram_kb: float
    logic_mm2: float

# Target die configurations
DIE_CONFIGS = {
    'nano_1b': DieConfig('Nano (1B)', 3.5, 3.5, 256, 8.0),
    'micro_2b': DieConfig('Micro (2B)', 5.0, 5.0, 512, 17.0),
    'standard_4b': DieConfig('Standard (4B)', 7.0, 7.0, 1024, 35.0),
}

class YieldSimulator:
    """Simulates manufacturing yield"""
    
    def __init__(self, process: ProcessNode):
        self.process = process
    
    def calculate_die_area(self, die: DieConfig) -> float:
        """Calculate total die area in mm²"""
        return die.width_mm * die.height_mm
    
    def calculate_gross_dies_per_wafer(self, die: DieConfig) -> int:
        """Calculate gross dies per wafer (no yield loss)"""
        wafer_radius = self.process.wafer_diameter_mm / 2
        die_width = die.width_mm
        die_height = die.height_mm
        
        # Approximate formula: N = π * R² / (W * H) * efficiency_factor
        # Efficiency factor accounts for edge losses
        efficiency = 0.85  # Typical for rectangular dies
        
        gross_dies = int(np.pi * wafer_radius**2 / (die_width * die_height) * efficiency)
        return gross_dies
    
    def calculate_yield_murphy(self, die: DieConfig) -> float:
        """
        Calculate yield using Murphy's model
        
        Y = ((1 - e^(-D0*A)) / (D0*A))²
        
        Where D0 = defect density, A = die area in cm²
        """
        die_area_cm2 = self.calculate_die_area(die) / 100  # mm² to cm²
        D0 = self.process.defect_density_per_cm2
        
        if D0 * die_area_cm2 < 0.01:
            return 0.99  # Near-perfect yield for very small dies
        
        exponent = D0 * die_area_cm2
        yield_rate = ((1 - np.exp(-exponent)) / exponent) ** 2
        return yield_rate
    
    def calculate_yield_poisson(self, die: DieConfig) -> float:
        """
        Calculate yield using Poisson model
        
        Y = e^(-D0*A)
        
        More conservative than Murphy for larger dies
        """
        die_area_cm2 = self.calculate_die_area(die) / 100
        D0 = self.process.defect_density_per_cm2
        
        yield_rate = np.exp(-D0 * die_area_cm2)
        return yield_rate
    
    def calculate_yield_seeds(self, die: DieConfig, alpha: float = 2.0) -> float:
        """
        Calculate yield using Seeds model
        
        Y = 1 / (1 + D0*A)^α
        
        Good for mature processes with clustering
        """
        die_area_cm2 = self.calculate_die_area(die) / 100
        D0 = self.process.defect_density_per_cm2
        
        yield_rate = 1 / (1 + D0 * die_area_cm2) ** alpha
        return yield_rate
    
    def simulate_yield_distribution(self, die: DieConfig, n_wafers: int = 100) -> Dict:
        """Simulate yield distribution across wafers"""
        gross_dies = self.calculate_gross_dies_per_wafer(die)
        base_yield = self.calculate_yield_murphy(die)
        
        # Model variation in defect density across wafers
        # Use gamma distribution to model clustering
        shape, scale = 2.0, self.process.defect_density_per_cm2 / 2
        
        yields = []
        good_dies = []
        
        for _ in range(n_wafers):
            # Random defect density for this wafer
            D0 = np.random.gamma(shape, scale)
            
            # Calculate yield for this wafer
            die_area_cm2 = self.calculate_die_area(die) / 100
            wafer_yield = np.exp(-D0 * die_area_cm2)
            
            # Binomial distribution for actual good dies
            good = np.random.binomial(gross_dies, wafer_yield)
            
            yields.append(wafer_yield)
            good_dies.append(good)
        
        return {
            'mean_yield': np.mean(yields),
            'std_yield': np.std(yields),
            'min_yield': np.min(yields),
            'max_yield': np.max(yields),
            'mean_good_dies': np.mean(good_dies),
            'total_good_dies': sum(good_dies),
            'gross_dies_per_wafer': gross_dies,
        }


class CostSimulator:
    """Simulates manufacturing costs"""
    
    def __init__(self, process: ProcessNode, yield_sim: YieldSimulator):
        self.process = process
        self.yield_sim = yield_sim
    
    def calculate_cost_per_die(self, die: DieConfig, volume_wafers: int) -> Dict:
        """Calculate cost per good die"""
        
        gross_dies = self.yield_sim.calculate_gross_dies_per_wafer(die)
        yield_rate = self.yield_sim.calculate_yield_murphy(die)
        good_dies_per_wafer = int(gross_dies * yield_rate)
        total_good_dies = good_dies_per_wafer * volume_wafers
        
        # Wafer cost component
        wafer_cost = self.process.wafer_cost_usd * volume_wafers
        
        # Mask amortization (over production volume)
        mask_amort_per_wafer = self.process.mask_cost_usd / volume_wafers
        
        # Packaging and test cost per die
        pkg_test_cost = 2.50  # USD per die
        
        # Total cost
        total_cost = wafer_cost + self.process.mask_cost_usd + (pkg_test_cost * total_good_dies)
        cost_per_good_die = total_cost / total_good_dies
        
        return {
            'wafer_cost_per_die': self.process.wafer_cost_usd / good_dies_per_wafer,
            'mask_amort_per_die': mask_amort_per_wafer / yield_rate,
            'pkg_test_cost': pkg_test_cost,
            'total_cost_per_die': cost_per_good_die,
            'good_dies_per_wafer': good_dies_per_wafer,
            'total_good_dies': total_good_dies,
        }
    
    def analyze_volume_scenarios(self, die: DieConfig) -> Dict:
        """Analyze cost at different volume levels"""
        volumes = {
            'prototype': 10,
            'pilot': 50,
            'low_volume': 200,
            'medium_volume': 1000,
            'high_volume': 5000,
        }
        
        results = {}
        for scenario, n_wafers in volumes.items():
            results[scenario] = self.calculate_cost_per_die(die, n_wafers)
        
        return results


def run_iteration_5():
    """Run manufacturing yield simulation"""
    
    print("=" * 70)
    print("TERNARYAIR SIMULATION FRAMEWORK")
    print("Iteration 5: Manufacturing Yield Simulation")
    print("=" * 70)
    
    process = ProcessNode()
    yield_sim = YieldSimulator(process)
    cost_sim = CostSimulator(process, yield_sim)
    
    results = {
        'process': {
            'name': process.name,
            'defect_density_per_cm2': process.defect_density_per_cm2,
            'wafer_diameter_mm': process.wafer_diameter_mm,
            'wafer_cost_usd': process.wafer_cost_usd,
            'mask_cost_usd': process.mask_cost_usd,
        },
        'dies': {},
        'volume_analysis': {},
    }
    
    # Analyze each die configuration
    print(f"\n📊 Process Node: {process.name}")
    print(f"   Defect Density: {process.defect_density_per_cm2} defects/cm²")
    print(f"   Wafer Size: {process.wafer_diameter_mm}mm")
    print(f"   Wafer Cost: ${process.wafer_cost_usd:,}")
    print(f"   Mask Set Cost: ${process.mask_cost_usd:,}")
    
    print("\n" + "=" * 80)
    print("DIE CONFIGURATION ANALYSIS")
    print("=" * 80)
    
    for die_key, die in DIE_CONFIGS.items():
        print(f"\n📋 {die.name}")
        print("-" * 50)
        
        die_area = yield_sim.calculate_die_area(die)
        gross_dies = yield_sim.calculate_gross_dies_per_wafer(die)
        
        yield_murphy = yield_sim.calculate_yield_murphy(die)
        yield_poisson = yield_sim.calculate_yield_poisson(die)
        yield_seeds = yield_sim.calculate_yield_seeds(die)
        
        good_dies_murphy = int(gross_dies * yield_murphy)
        
        print(f"   Die Size: {die.width_mm} × {die.height_mm} mm = {die_area:.1f} mm²")
        print(f"   Gross Dies/Wafer: {gross_dies}")
        print(f"   Yield (Murphy): {yield_murphy*100:.1f}%")
        print(f"   Yield (Poisson): {yield_poisson*100:.1f}%")
        print(f"   Yield (Seeds): {yield_seeds*100:.1f}%")
        print(f"   Good Dies/Wafer: {good_dies_murphy}")
        
        # Cost analysis
        volume_analysis = cost_sim.analyze_volume_scenarios(die)
        
        print(f"\n   💰 Cost per Good Die:")
        for scenario, costs in volume_analysis.items():
            print(f"      {scenario:20s}: ${costs['total_cost_per_die']:.2f}")
        
        # Yield distribution simulation
        yield_dist = yield_sim.simulate_yield_distribution(die, n_wafers=100)
        
        results['dies'][die_key] = {
            'name': die.name,
            'area_mm2': die_area,
            'gross_dies_per_wafer': gross_dies,
            'yield_murphy': yield_murphy,
            'yield_poisson': yield_poisson,
            'yield_seeds': yield_seeds,
            'good_dies_per_wafer': good_dies_murphy,
            'yield_distribution': yield_dist,
            'volume_analysis': volume_analysis,
        }
    
    # Target die (Micro 2B) detailed analysis
    target_die = DIE_CONFIGS['micro_2b']
    print("\n" + "=" * 80)
    print("TARGET DIE: MICRO (2B) - DETAILED ANALYSIS")
    print("=" * 80)
    
    # Breakeven analysis
    target_results = results['dies']['micro_2b']
    retail_price = 99
    
    print(f"\n📈 Breakeven Analysis (${retail_price} retail price)")
    print("-" * 50)
    
    for scenario, costs in target_results['volume_analysis'].items():
        cost = costs['total_cost_per_die']
        margin = (retail_price - cost) / retail_price * 100
        print(f"   {scenario:20s}: Cost ${cost:.2f} | Margin {margin:.1f}%")
    
    # Generate visualizations
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Yield models comparison
    ax1 = axes[0, 0]
    die_names = [DIE_CONFIGS[k].name for k in DIE_CONFIGS.keys()]
    x = np.arange(len(die_names))
    width = 0.25
    
    yields_murphy = [results['dies'][k]['yield_murphy'] * 100 for k in DIE_CONFIGS.keys()]
    yields_poisson = [results['dies'][k]['yield_poisson'] * 100 for k in DIE_CONFIGS.keys()]
    yields_seeds = [results['dies'][k]['yield_seeds'] * 100 for k in DIE_CONFIGS.keys()]
    
    ax1.bar(x - width, yields_murphy, width, label='Murphy', color='#3498DB')
    ax1.bar(x, yields_poisson, width, label='Poisson', color='#E74C3C')
    ax1.bar(x + width, yields_seeds, width, label='Seeds', color='#2ECC71')
    
    ax1.set_ylabel('Yield (%)')
    ax1.set_title('Yield Model Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(die_names)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # 2. Cost per die vs volume
    ax2 = axes[0, 1]
    volumes = list(target_results['volume_analysis'].keys())
    costs = [target_results['volume_analysis'][v]['total_cost_per_die'] for v in volumes]
    
    colors = ['#E74C3C', '#F39C12', '#F1C40F', '#2ECC71', '#27AE60']
    bars = ax2.bar(volumes, costs, color=colors)
    ax2.axhline(y=retail_price * 0.4, color='green', linestyle='--', label='60% margin threshold')
    ax2.axhline(y=retail_price * 0.3, color='orange', linestyle='--', label='70% margin threshold')
    
    ax2.set_ylabel('Cost per Die ($)')
    ax2.set_title('Micro (2B) Cost vs Production Volume')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, cost in zip(bars, costs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'${cost:.2f}', 
                ha='center', va='bottom', fontsize=10)
    
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=15, ha='right')
    
    # 3. Yield distribution histogram
    ax3 = axes[1, 0]
    yield_dist = target_results['yield_distribution']
    
    # Simulate yield values for histogram
    yields = np.random.normal(yield_dist['mean_yield'], yield_dist['std_yield'], 1000)
    yields = np.clip(yields, 0, 1) * 100
    
    ax3.hist(yields, bins=30, color='#3498DB', alpha=0.7, edgecolor='white')
    ax3.axvline(x=yield_dist['mean_yield']*100, color='red', linestyle='-', linewidth=2, 
                label=f"Mean: {yield_dist['mean_yield']*100:.1f}%")
    ax3.axvline(x=yield_dist['min_yield']*100, color='orange', linestyle='--', 
                label=f"Min: {yield_dist['min_yield']*100:.1f}%")
    
    ax3.set_xlabel('Yield (%)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Yield Distribution (100 Wafers Simulation)')
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # 4. Good dies per wafer
    ax4 = axes[1, 1]
    die_keys = list(DIE_CONFIGS.keys())
    gross = [results['dies'][k]['gross_dies_per_wafer'] for k in die_keys]
    good = [int(results['dies'][k]['gross_dies_per_wafer'] * results['dies'][k]['yield_murphy']) for k in die_keys]
    bad = [g - gd for g, gd in zip(gross, good)]
    
    x = np.arange(len(die_keys))
    ax4.bar(x, gross, label='Gross Dies', color='#95A5A6', alpha=0.5)
    ax4.bar(x, good, label='Good Dies', color='#2ECC71')
    
    ax4.set_ylabel('Dies per Wafer')
    ax4.set_title('Dies per Wafer by Configuration')
    ax4.set_xticks(x)
    ax4.set_xticklabels([DIE_CONFIGS[k].name for k in die_keys])
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # Add yield percentages on bars
    for i, (g, gd) in enumerate(zip(gross, good)):
        yield_pct = gd / g * 100
        ax4.text(i, gd + 5, f'{yield_pct:.0f}%', ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/sim5_manufacturing_yield.png', dpi=150)
    print("\n✅ Saved: /home/z/my-project/download/sim5_manufacturing_yield.png")
    
    # Save JSON
    with open('/home/z/my-project/download/sim5_manufacturing_yield.json', 'w') as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else str(x))
    print("✅ Saved: /home/z/my-project/download/sim5_manufacturing_yield.json")
    
    # Key findings
    print("\n🔬 Key Findings:")
    print("-" * 50)
    print(f"Micro (2B) at medium volume (1000 wafers):")
    print(f"  - Yield: {target_results['yield_murphy']*100:.1f}%")
    print(f"  - Good dies/wafer: {target_results['good_dies_per_wafer']}")
    print(f"  - Cost per die: ${target_results['volume_analysis']['medium_volume']['total_cost_per_die']:.2f}")
    print(f"  - Margin at $99 retail: {(99 - target_results['volume_analysis']['medium_volume']['total_cost_per_die'])/99*100:.1f}%")
    
    return results


if __name__ == "__main__":
    run_iteration_5()
