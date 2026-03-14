"""
Material Properties for Thermal Simulation
===========================================
Thermal properties of materials used in synapse-inspired chip structures.
Based on literature values and experimental data.

References:
[1] King, J.A. (2004). Thermal Conductivity: Theory, Properties, and Applications
[2] Lee, S.M. (1997). Thermal conductivity of silicon nanomaterials
[3] Cahill, D.G. (2003). Nanoscale thermal transport
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

@dataclass
class Material:
    """Material thermal and physical properties."""
    name: str
    thermal_conductivity: float  # W/mK
    specific_heat: float  # J/kgK
    density: float  # kg/m³
    thermal_diffusivity: float  # m²/s (calculated)
    
    def __post_init__(self):
        self.thermal_diffusivity = self.thermal_conductivity / (self.density * self.specific_heat)


# Standard Materials Database
MATERIALS: Dict[str, Material] = {
    # Silicon and semiconductors
    'silicon': Material(
        name='Silicon',
        thermal_conductivity=148.0,  # Bulk Si at 300K
        specific_heat=700.0,
        density=2329.0,
        thermal_diffusivity=0.0  # Calculated
    ),
    'silicon_thin_film': Material(
        name='Silicon Thin Film (100nm)',
        thermal_conductivity=50.0,  # Reduced due to phonon boundary scattering
        specific_heat=700.0,
        density=2329.0,
        thermal_diffusivity=0.0
    ),
    'silicon_on_insulator': Material(
        name='SOI Device Layer',
        thermal_conductivity=30.0,  # Further reduced in SOI
        specific_heat=700.0,
        density=2329.0,
        thermal_diffusivity=0.0
    ),
    
    # Dielectrics
    'sio2': Material(
        name='Silicon Dioxide',
        thermal_conductivity=1.4,  # Thermal oxide
        specific_heat=745.0,
        density=2200.0,
        thermal_diffusivity=0.0
    ),
    'sio2_porous': Material(
        name='Porous SiO2 (Low-k)',
        thermal_conductivity=0.25,  # Low-k dielectric
        specific_heat=745.0,
        density=1200.0,  # Reduced density
        thermal_diffusivity=0.0
    ),
    'si3n4': Material(
        name='Silicon Nitride',
        thermal_conductivity=30.0,
        specific_heat=700.0,
        density=3270.0,
        thermal_diffusivity=0.0
    ),
    'hfo2': Material(
        name='Hafnium Dioxide',
        thermal_conductivity=1.0,  # High-k dielectric
        specific_heat=280.0,
        density=9680.0,
        thermal_diffusivity=0.0
    ),
    
    # Metals
    'copper': Material(
        name='Copper',
        thermal_conductivity=400.0,  # Bulk Cu
        specific_heat=385.0,
        density=8960.0,
        thermal_diffusivity=0.0
    ),
    'copper_damascene': Material(
        name='Copper Damascene',
        thermal_conductivity=300.0,  # Reduced due to grain boundaries
        specific_heat=385.0,
        density=8960.0,
        thermal_diffusivity=0.0
    ),
    'aluminum': Material(
        name='Aluminum',
        thermal_conductivity=237.0,
        specific_heat=897.0,
        density=2700.0,
        thermal_diffusivity=0.0
    ),
    'tungsten': Material(
        name='Tungsten',
        thermal_conductivity=174.0,
        specific_heat=134.0,
        density=19300.0,
        thermal_diffusivity=0.0
    ),
    'titanium': Material(
        name='Titanium',
        thermal_conductivity=21.9,
        specific_heat=523.0,
        density=4500.0,
        thermal_diffusivity=0.0
    ),
    
    # Phase change materials (for neuromorphic synapses)
    'gst': Material(
        name='Ge2Sb2Te5 (GST)',
        thermal_conductivity=0.5,  # Amorphous
        specific_heat=210.0,
        density=6000.0,
        thermal_diffusivity=0.0
    ),
    'gst_crystalline': Material(
        name='GST Crystalline',
        thermal_conductivity=2.0,  # Crystalline phase
        specific_heat=210.0,
        density=6000.0,
        thermal_diffusivity=0.0
    ),
    
    # Biological analogs (for comparison)
    'cytoplasm': Material(
        name='Cytoplasm',
        thermal_conductivity=0.6,  # Water-like
        specific_heat=4186.0,
        density=1000.0,
        thermal_diffusivity=0.0
    ),
    'lipid_membrane': Material(
        name='Lipid Membrane',
        thermal_conductivity=0.2,
        specific_heat=2000.0,
        density=900.0,
        thermal_diffusivity=0.0
    ),
    
    # Interfacial materials
    'tim': Material(
        name='Thermal Interface Material',
        thermal_conductivity=5.0,  # Typical TIM
        specific_heat=1000.0,
        density=2500.0,
        thermal_diffusivity=0.0
    ),
}


def get_material(name: str) -> Material:
    """Retrieve material properties by name."""
    if name not in MATERIALS:
        raise ValueError(f"Material '{name}' not found. Available: {list(MATERIALS.keys())}")
    return MATERIALS[name]


def calculate_thermal_resistance(material: Material, thickness: float, area: float) -> float:
    """
    Calculate thermal resistance R_th = t / (k * A)
    
    Args:
        material: Material properties
        thickness: Thickness in meters
        area: Cross-sectional area in m²
    
    Returns:
        Thermal resistance in K/W
    """
    return thickness / (material.thermal_conductivity * area)


def calculate_thermal_capacitance(material: Material, volume: float) -> float:
    """
    Calculate thermal capacitance C_th = ρ * c_p * V
    
    Args:
        material: Material properties
        volume: Volume in m³
    
    Returns:
        Thermal capacitance in J/K
    """
    return material.density * material.specific_heat * volume


def effective_thermal_conductivity(k1: float, k2: float, 
                                    f1: float, f2: float,
                                    parallel: bool = True) -> float:
    """
    Calculate effective thermal conductivity of composite.
    
    Args:
        k1, k2: Thermal conductivities of components
        f1, f2: Volume fractions (f1 + f2 = 1)
        parallel: If True, use parallel model; else series model
    
    Returns:
        Effective thermal conductivity
    """
    if parallel:
        # Wiener upper bound (parallel)
        return f1 * k1 + f2 * k2
    else:
        # Wiener lower bound (series)
        return 1.0 / (f1/k1 + f2/k2)


class LayeredStructure:
    """Model thermal properties of layered structures."""
    
    def __init__(self):
        self.layers = []
    
    def add_layer(self, material_name: str, thickness: float):
        """Add a layer to the stack."""
        material = get_material(material_name)
        self.layers.append({
            'material': material,
            'thickness': thickness
        })
    
    def total_thickness(self) -> float:
        """Total thickness of the stack."""
        return sum(layer['thickness'] for layer in self.layers)
    
    def through_plane_resistance(self, area: float) -> float:
        """
        Calculate through-plane thermal resistance.
        Layers in series (heat flows perpendicular to layers).
        """
        R_total = 0.0
        for layer in self.layers:
            R_layer = calculate_thermal_resistance(
                layer['material'], layer['thickness'], area
            )
            R_total += R_layer
        return R_total
    
    def in_plane_conductivity(self) -> float:
        """
        Calculate in-plane effective thermal conductivity.
        Layers in parallel (heat flows parallel to layers).
        """
        total_thickness = self.total_thickness()
        k_eff = 0.0
        for layer in self.layers:
            fraction = layer['thickness'] / total_thickness
            k_eff += fraction * layer['material'].thermal_conductivity
        return k_eff


if __name__ == "__main__":
    # Test material properties
    print("Material Properties Test")
    print("=" * 50)
    
    for name, mat in MATERIALS.items():
        print(f"{mat.name}: k = {mat.thermal_conductivity:.1f} W/mK, "
              f"α = {mat.thermal_diffusivity:.2e} m²/s")
    
    # Test layered structure
    print("\nLayered Structure Example:")
    stack = LayeredStructure()
    stack.add_layer('silicon', 100e-9)  # 100nm Si
    stack.add_layer('sio2', 50e-9)      # 50nm SiO2
    stack.add_layer('copper', 200e-9)   # 200nm Cu
    
    print(f"Total thickness: {stack.total_thickness()*1e9:.1f} nm")
    print(f"In-plane k_eff: {stack.in_plane_conductivity():.1f} W/mK")
    print(f"Through-plane R: {stack.through_plane_resistance(1e-12):.2f} K/W (per μm²)")
