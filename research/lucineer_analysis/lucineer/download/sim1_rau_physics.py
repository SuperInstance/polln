#!/usr/bin/env python3
"""
TernaryAir Simulation Framework
Iteration 1: RAU Gate-Level Physics Simulation

Simulates the Rotation-Accumulate Unit at the transistor/gate level:
- Power consumption (dynamic + static)
- Timing analysis (critical path)
- Area estimation at 28nm
- Energy per operation comparison vs traditional MAC

Author: Casey DiGennaro
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt

@dataclass
class GateModel:
    """28nm gate model parameters"""
    name: str
    input_capacitance_ff: float  # femtofarads
    delay_ps: float              # picoseconds
    dynamic_power_uW_per_MHz: float
    leakage_power_nW: float
    area_um2: float

# 28nm Gate Library (based on typical foundry data)
GATE_LIBRARY = {
    'INV_X1': GateModel('INV_X1', 0.5, 8, 0.05, 2, 0.4),
    'INV_X2': GateModel('INV_X2', 1.0, 6, 0.08, 3, 0.6),
    'NAND2_X1': GateModel('NAND2_X1', 0.6, 12, 0.06, 3, 0.5),
    'NOR2_X1': GateModel('NOR2_X1', 0.6, 14, 0.06, 4, 0.5),
    'MUX2_X1': GateModel('MUX2_X1', 1.0, 18, 0.08, 5, 0.8),
    'XOR2_X1': GateModel('XOR2_X1', 1.2, 22, 0.10, 6, 1.0),
    'DFF_X1': GateModel('DFF_X1', 1.5, 15, 0.12, 15, 2.5),
    'FULL_ADDER': GateModel('FULL_ADDER', 2.5, 35, 0.25, 20, 3.5),
}

class RAUSimulator:
    """
    Rotation-Accumulate Unit Physics Simulator
    
    RAU implements ternary multiplication:
      w=+1: result = x (identity)
      w=0:  result = 0 (zero)
      w=-1: result = -x (negation)
    
    Implementation:
      - 2:1 MUX for routing
      - XOR for conditional negation
      - Full adder chain for accumulation
    """
    
    def __init__(self, activation_width: int = 8, accumulator_width: int = 24):
        self.act_width = activation_width
        self.acc_width = accumulator_width
        self.gates = []
        self._build_gate_netlist()
    
    def _build_gate_netlist(self):
        """Build the gate-level netlist for RAU"""
        self.gates = []
        
        # Input buffer (1 INV per bit)
        for i in range(self.act_width):
            self.gates.append(('INV_X1', f'act_buf_{i}'))
        
        # Weight decoder (2 INV + 1 NAND for each ternary state)
        self.gates.append(('INV_X1', 'weight_dec_inv1'))
        self.gates.append(('INV_X1', 'weight_dec_inv2'))
        self.gates.append(('NAND2_X1', 'weight_dec_nand'))
        
        # Rotation logic per bit (1 MUX2 + 1 XOR2)
        for i in range(self.act_width):
            # MUX2: select between 0, x, -x based on weight
            self.gates.append(('MUX2_X1', f'rot_mux_{i}'))
            # XOR2: conditional negation
            self.gates.append(('XOR2_X1', f'rot_xor_{i}'))
        
        # Accumulator (full adder chain)
        for i in range(self.acc_width):
            self.gates.append(('FULL_ADDER', f'acc_fa_{i}'))
            self.gates.append(('DFF_X1', f'acc_dff_{i}'))
        
        # Output buffer
        for i in range(self.acc_width):
            self.gates.append(('INV_X2', f'out_buf_{i}'))
    
    def calculate_total_area(self) -> float:
        """Calculate total area in um²"""
        total_area = 0
        for gate_type, _ in self.gates:
            total_area += GATE_LIBRARY[gate_type].area_um2
        return total_area
    
    def calculate_critical_path_delay(self) -> float:
        """Calculate critical path delay in ps"""
        # Critical path: input → rotation → accumulation MSB → output
        path_gates = [
            'INV_X1',      # Input buffer
            'MUX2_X1',     # Rotation select
            'XOR2_X1',     # Conditional negate
            'FULL_ADDER',  # MSB adder
            'INV_X2'       # Output buffer
        ]
        
        # Account for adder chain ripple
        adder_chain_delay = GATE_LIBRARY['FULL_ADDER'].delay_ps * min(self.acc_width, 8)
        
        total_delay = sum(GATE_LIBRARY[g].delay_ps for g in path_gates[:3])
        total_delay += adder_chain_delay
        total_delay += GATE_LIBRARY['INV_X2'].delay_ps
        
        return total_delay
    
    def calculate_dynamic_power(self, frequency_mhz: float, activity_factor: float = 0.5) -> float:
        """Calculate dynamic power in uW"""
        total_power = 0
        for gate_type, _ in self.gates:
            gate = GATE_LIBRARY[gate_type]
            total_power += gate.dynamic_power_uW_per_MHz * frequency_mhz * activity_factor
        return total_power
    
    def calculate_static_power(self) -> float:
        """Calculate static/leakage power in nW"""
        total_power = 0
        for gate_type, _ in self.gates:
            total_power += GATE_LIBRARY[gate_type].leakage_power_nW
        return total_power
    
    def calculate_energy_per_op(self, frequency_mhz: float = 250) -> float:
        """Calculate energy per operation in pJ"""
        dynamic_power_uw = self.calculate_dynamic_power(frequency_mhz)
        static_power_nw = self.calculate_static_power()
        total_power_uw = dynamic_power_uw + static_power_nw / 1000
        
        # Energy = Power × Time
        op_time_ns = 1000 / frequency_mhz  # 1 operation per cycle
        energy_pj = total_power_uw * op_time_ns / 1000
        
        return energy_pj
    
    def get_gate_count(self) -> int:
        return len(self.gates)


class MACSimulator:
    """
    Traditional Multiply-Accumulate Unit for comparison
    Implements INT8 multiplication
    """
    
    def __init__(self, activation_width: int = 8, weight_width: int = 8, accumulator_width: int = 24):
        self.act_width = activation_width
        self.weight_width = weight_width
        self.acc_width = accumulator_width
        self.gates = []
        self._build_gate_netlist()
    
    def _build_gate_netlist(self):
        """Build gate-level netlist for MAC"""
        self.gates = []
        
        # Multiplier (array multiplier): ~8×8 = 64 partial products
        # Each partial product: 1 AND gate
        for i in range(self.act_width * self.weight_width):
            self.gates.append(('NAND2_X1', f'pp_{i}'))
        
        # Full adders for partial product reduction
        # Wallace tree: ~act_width × weight_width full adders
        for i in range(self.act_width * self.weight_width):
            self.gates.append(('FULL_ADDER', f'mult_fa_{i}'))
        
        # Accumulator adder
        for i in range(self.acc_width):
            self.gates.append(('FULL_ADDER', f'acc_fa_{i}'))
            self.gates.append(('DFF_X1', f'acc_dff_{i}'))
        
        # Output buffer
        for i in range(self.acc_width):
            self.gates.append(('INV_X2', f'out_buf_{i}'))
    
    def calculate_total_area(self) -> float:
        total_area = 0
        for gate_type, _ in self.gates:
            total_area += GATE_LIBRARY[gate_type].area_um2
        return total_area
    
    def calculate_critical_path_delay(self) -> float:
        # Multiplier + accumulator chain
        mult_delay = GATE_LIBRARY['FULL_ADDER'].delay_ps * max(self.act_width, self.weight_width) * 2
        acc_delay = GATE_LIBRARY['FULL_ADDER'].delay_ps * 8
        return mult_delay + acc_delay + 50  # 50ps buffer
    
    def calculate_dynamic_power(self, frequency_mhz: float, activity_factor: float = 0.5) -> float:
        total_power = 0
        for gate_type, _ in self.gates:
            gate = GATE_LIBRARY[gate_type]
            total_power += gate.dynamic_power_uW_per_MHz * frequency_mhz * activity_factor
        return total_power
    
    def calculate_static_power(self) -> float:
        total_power = 0
        for gate_type, _ in self.gates:
            total_power += GATE_LIBRARY[gate_type].leakage_power_nW
        return total_power
    
    def calculate_energy_per_op(self, frequency_mhz: float = 250) -> float:
        dynamic_power_uw = self.calculate_dynamic_power(frequency_mhz)
        static_power_nw = self.calculate_static_power()
        total_power_uw = dynamic_power_uw + static_power_nw / 1000
        op_time_ns = 1000 / frequency_mhz
        return total_power_uw * op_time_ns / 1000
    
    def get_gate_count(self) -> int:
        return len(self.gates)


def run_iteration_1():
    """Run RAU vs MAC comparison simulation"""
    
    print("=" * 70)
    print("TERNARYAIR SIMULATION FRAMEWORK")
    print("Iteration 1: RAU Gate-Level Physics Simulation")
    print("=" * 70)
    
    # Initialize simulators
    rau = RAUSimulator(activation_width=8, accumulator_width=24)
    mac = MACSimulator(activation_width=8, weight_width=8, accumulator_width=24)
    
    # Collect results
    results = {
        'rau': {
            'gate_count': rau.get_gate_count(),
            'area_um2': rau.calculate_total_area(),
            'critical_path_ps': rau.calculate_critical_path_delay(),
            'dynamic_power_250mhz_uW': rau.calculate_dynamic_power(250),
            'static_power_nW': rau.calculate_static_power(),
            'energy_per_op_pJ': rau.calculate_energy_per_op(250),
        },
        'mac': {
            'gate_count': mac.get_gate_count(),
            'area_um2': mac.calculate_total_area(),
            'critical_path_ps': mac.calculate_critical_path_delay(),
            'dynamic_power_250mhz_uW': mac.calculate_dynamic_power(250),
            'static_power_nW': mac.calculate_static_power(),
            'energy_per_op_pJ': mac.calculate_energy_per_op(250),
        }
    }
    
    # Calculate improvements
    improvements = {
        'gate_reduction': (1 - results['rau']['gate_count'] / results['mac']['gate_count']) * 100,
        'area_reduction': (1 - results['rau']['area_um2'] / results['mac']['area_um2']) * 100,
        'power_reduction': (1 - results['rau']['dynamic_power_250mhz_uW'] / results['mac']['dynamic_power_250mhz_uW']) * 100,
        'energy_reduction': (1 - results['rau']['energy_per_op_pJ'] / results['mac']['energy_per_op_pJ']) * 100,
        'max_freq_rau_mhz': 1000000 / results['rau']['critical_path_ps'],
        'max_freq_mac_mhz': 1000000 / results['mac']['critical_path_ps'],
    }
    
    results['improvements'] = improvements
    
    # Print results
    print("\n📊 RAU vs Traditional MAC Comparison")
    print("-" * 50)
    print(f"{'Metric':<30} {'RAU':>12} {'MAC':>12}")
    print("-" * 50)
    print(f"{'Gate Count':<30} {results['rau']['gate_count']:>12} {results['mac']['gate_count']:>12}")
    print(f"{'Area (μm²)':<30} {results['rau']['area_um2']:>12.1f} {results['mac']['area_um2']:>12.1f}")
    print(f"{'Critical Path (ps)':<30} {results['rau']['critical_path_ps']:>12.1f} {results['mac']['critical_path_ps']:>12.1f}")
    print(f"{'Dynamic Power @250MHz (μW)':<30} {results['rau']['dynamic_power_250mhz_uW']:>12.2f} {results['mac']['dynamic_power_250mhz_uW']:>12.2f}")
    print(f"{'Static Power (nW)':<30} {results['rau']['static_power_nW']:>12.1f} {results['mac']['static_power_nW']:>12.1f}")
    print(f"{'Energy per Op (pJ)':<30} {results['rau']['energy_per_op_pJ']:>12.3f} {results['mac']['energy_per_op_pJ']:>12.3f}")
    
    print("\n📈 RAU Improvements")
    print("-" * 50)
    print(f"Gate Reduction: {improvements['gate_reduction']:.1f}%")
    print(f"Area Reduction: {improvements['area_reduction']:.1f}%")
    print(f"Power Reduction: {improvements['power_reduction']:.1f}%")
    print(f"Energy Reduction: {improvements['energy_reduction']:.1f}%")
    print(f"Max Frequency RAU: {improvements['max_freq_rau_mhz']:.0f} MHz")
    print(f"Max Frequency MAC: {improvements['max_freq_mac_mhz']:.0f} MHz")
    
    # Generate visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Gate count comparison
    ax1 = axes[0, 0]
    bars = ax1.bar(['RAU', 'MAC (INT8)'], [results['rau']['gate_count'], results['mac']['gate_count']], 
                   color=['#2ECC71', '#E74C3C'])
    ax1.set_ylabel('Gate Count')
    ax1.set_title('Gate Count Comparison')
    for bar, val in zip(bars, [results['rau']['gate_count'], results['mac']['gate_count']]):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'{val}', 
                ha='center', va='bottom', fontsize=11)
    
    # Area comparison
    ax2 = axes[0, 1]
    bars = ax2.bar(['RAU', 'MAC (INT8)'], [results['rau']['area_um2'], results['mac']['area_um2']], 
                   color=['#2ECC71', '#E74C3C'])
    ax2.set_ylabel('Area (μm²)')
    ax2.set_title('Silicon Area Comparison')
    for bar, val in zip(bars, [results['rau']['area_um2'], results['mac']['area_um2']]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, f'{val:.0f}', 
                ha='center', va='bottom', fontsize=11)
    
    # Energy per operation
    ax3 = axes[1, 0]
    bars = ax3.bar(['RAU', 'MAC (INT8)'], [results['rau']['energy_per_op_pJ'], results['mac']['energy_per_op_pJ']], 
                   color=['#2ECC71', '#E74C3C'])
    ax3.set_ylabel('Energy (pJ/op)')
    ax3.set_title('Energy per Operation')
    for bar, val in zip(bars, [results['rau']['energy_per_op_pJ'], results['mac']['energy_per_op_pJ']]):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f'{val:.2f}', 
                ha='center', va='bottom', fontsize=11)
    
    # Power breakdown
    ax4 = axes[1, 1]
    x = np.arange(2)
    width = 0.35
    ax4.bar(x - width/2, [results['rau']['dynamic_power_250mhz_uW'], results['rau']['static_power_nW']/1000], 
            width, label='RAU', color='#2ECC71')
    ax4.bar(x + width/2, [results['mac']['dynamic_power_250mhz_uW'], results['mac']['static_power_nW']/1000], 
            width, label='MAC', color='#E74C3C')
    ax4.set_ylabel('Power (μW)')
    ax4.set_title('Power Consumption @ 250MHz')
    ax4.set_xticks(x)
    ax4.set_xticklabels(['Dynamic', 'Static'])
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/download/sim1_rau_physics.png', dpi=150)
    print("\n✅ Saved: /home/z/my-project/download/sim1_rau_physics.png")
    
    # Save JSON results
    with open('/home/z/my-project/download/sim1_rau_physics.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✅ Saved: /home/z/my-project/download/sim1_rau_physics.json")
    
    return results


if __name__ == "__main__":
    run_iteration_1()
