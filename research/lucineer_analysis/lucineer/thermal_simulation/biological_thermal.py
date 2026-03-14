"""
Biological Thermal Mechanisms Module
====================================
Models thermal management in biological neurons and synapses,
with applications to neuromorphic chip design.

Biological Thermal Mechanisms:
1. Synaptic heat generation (ATP hydrolysis, ion pumping)
2. Dendritic spine thermal properties
3. Glial cell cooling mechanisms
4. Blood vessel proximity effects

References:
[1] Attwell, D. & Laughlin, S.B. (2001). An energy budget for signaling in the grey matter
    J. Cereb. Blood Flow Metab. 21, 1133-1145
[2] Harris, K.M. & Kater, S.B. (1994). Dendritic spines: cellular specializations
    Am. Sci. 82, 378-387
[3] Buxbaum, J.D. (2019). Thermal biology of neural circuits
    Curr. Opin. Neurobiol. 57, 1-6
[4] Jolivet, R. et al. (2009). Brain energy consumption
    Physiol. Rev. 89, 1063-1093
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

from core_thermal import (ThermalGrid, ThermalSolver, ThermalAnalyzer,
                          SimulationConfig, BoundaryCondition, BoundaryType,
                          HeatSource)
from materials import Material, get_material


class SynapseType(Enum):
    """Types of synapses with different thermal properties."""
    EXCITATORY = "excitatory"  # Glutamatergic
    INHIBITORY = "inhibitory"  # GABAergic
    NEUROMODULATORY = "neuromodulatory"  # Dopaminergic, etc.


class SpineMorphology(Enum):
    """Dendritic spine morphology types."""
    MUSHROOM = "mushroom"      # Large head, narrow neck
    THIN = "thin"              # Small head, thin neck
    STUBBY = "stubby"          # No distinct neck
    FILAPODIA = "filapodia"    # Long, thin spine


@dataclass
class BiologicalParameters:
    """Biological thermal and physiological parameters."""
    
    # ATP hydrolysis energy
    ATP_hydrolysis_energy: float = 50e-21  # 50 zJ = 12 k_BT ≈ 50 kJ/mol
    
    # Ion flux per action potential
    Na_influx_per_AP: float = 20e3  # ions per AP
    K_efflux_per_AP: float = 20e3
    Ca_influx_per_AP: float = 200  # ions per AP (voltage-gated channels)
    
    # Synaptic vesicle energetics
    vesicles_per_synapse_AP: int = 1
    neurotransmitter_per_vesicle: int = 5000  # molecules
    ATP_per_vesicle_cycle: int = 2  # Reuptake and recycling
    
    # Channel conductances
    Na_channel_conductance: float = 20e-12  # 20 pS
    K_channel_conductance: float = 10e-12   # 10 pS
    
    # Thermal properties
    brain_temperature: float = 310.15  # K (37°C)
    thermal_conductivity_cytoplasm: float = 0.6  # W/mK (water-like)
    thermal_conductivity_membrane: float = 0.2  # W/mK
    
    # Blood flow cooling
    blood_perfusion_rate: float = 50e-3  # mL/g/min (grey matter)
    blood_heat_capacity: float = 3.6e3   # J/kg/K
    blood_density: float = 1060          # kg/m³


@dataclass
class SynapseThermalModel:
    """
    Thermal model of a single biological synapse.
    
    Models heat generation from:
    - Ion pumping (Na/K ATPase)
    - Neurotransmitter recycling
    - Calcium clearance
    - Receptor activation
    """
    
    # Synapse type and morphology
    synapse_type: SynapseType = SynapseType.EXCITATORY
    spine_morphology: SpineMorphology = SpineMorphology.MUSHROOM
    
    # Geometric parameters
    spine_head_diameter: float = 500e-9  # 500 nm
    spine_neck_diameter: float = 150e-9  # 150 nm
    spine_neck_length: float = 500e-9    # 500 nm
    
    # Activity parameters
    firing_rate: float = 10.0  # Hz (average)
    release_probability: float = 0.5
    
    # Biophysical parameters
    params: BiologicalParameters = field(default_factory=BiologicalParameters)
    
    def __post_init__(self):
        # Set morphology-specific dimensions
        if self.spine_morphology == SpineMorphology.MUSHROOM:
            self.spine_head_diameter = 600e-9
            self.spine_neck_diameter = 150e-9
            self.spine_neck_length = 500e-9
        elif self.spine_morphology == SpineMorphology.THIN:
            self.spine_head_diameter = 300e-9
            self.spine_neck_diameter = 100e-9
            self.spine_neck_length = 700e-9
        elif self.spine_morphology == SpineMorphology.STUBBY:
            self.spine_head_diameter = 400e-9
            self.spine_neck_diameter = 400e-9  # Same as head
            self.spine_neck_length = 200e-9
        elif self.spine_morphology == SpineMorphology.FILAPODIA:
            self.spine_head_diameter = 200e-9
            self.spine_neck_diameter = 80e-9
            self.spine_neck_length = 1000e-9
    
    def head_volume(self) -> float:
        """Spine head volume (approximated as sphere)."""
        return (4/3) * np.pi * (self.spine_head_diameter / 2)**3
    
    def neck_volume(self) -> float:
        """Spine neck volume (approximated as cylinder)."""
        return np.pi * (self.spine_neck_diameter / 2)**2 * self.spine_neck_length
    
    def total_volume(self) -> float:
        """Total spine volume."""
        return self.head_volume() + self.neck_volume()
    
    def neck_thermal_resistance(self) -> float:
        """
        Thermal resistance of spine neck.
        R_th = L / (k * A)
        
        High neck resistance provides thermal isolation.
        """
        k = self.params.thermal_conductivity_cytoplasm
        area = np.pi * (self.spine_neck_diameter / 2)**2
        return self.spine_neck_length / (k * area)
    
    def heat_from_ion_pumping(self, activity_rate: float) -> float:
        """
        Heat from Na/K ATPase during synaptic transmission.
        
        Each action potential triggers:
        1. Na+ influx through voltage-gated channels
        2. K+ efflux through voltage-gated channels
        3. Ca2+ influx through NMDA/VGCC
        4. Na/K ATPase restores gradients (3Na out, 2K in per ATP)
        
        Returns: Heat generation rate in Watts
        """
        p = self.params
        
        # Na+ ions to pump per second
        na_pumping_rate = self.firing_rate * self.release_probability * p.Na_influx_per_AP
        
        # Ca2+ ions to clear (via plasma membrane Ca-ATPase)
        ca_pumping_rate = self.firing_rate * self.release_probability * p.Ca_influx_per_AP
        
        # ATP molecules hydrolyzed
        # Na/K ATPase: 3 Na per ATP
        # Ca-ATPase: 1 Ca per ATP
        atp_rate = na_pumping_rate / 3 + ca_pumping_rate
        
        # Heat generation
        heat_rate = atp_rate * p.ATP_hydrolysis_energy
        
        return heat_rate
    
    def heat_from_neurotransmitter_cycle(self) -> float:
        """
        Heat from neurotransmitter vesicle cycle.
        
        Includes:
        - Vesicle filling (V-ATPase)
        - Vesicle release
        - Reuptake
        - Recycling
        """
        p = self.params
        
        # Vesicle cycles per second
        vesicle_rate = self.firing_rate * self.release_probability * p.vesicles_per_synapse_AP
        
        # ATP per vesicle cycle
        atp_rate = vesicle_rate * p.ATP_per_vesicle_cycle
        
        # Heat generation
        heat_rate = atp_rate * p.ATP_hydrolysis_energy
        
        return heat_rate
    
    def total_heat_generation(self) -> float:
        """Total heat generation from all sources."""
        return (self.heat_from_ion_pumping(self.firing_rate) + 
                self.heat_from_neurotransmitter_cycle())
    
    def power_density(self) -> float:
        """Power density in W/m³."""
        return self.total_heat_generation() / self.total_volume()
    
    def temperature_rise_steady_state(self, cooling_coefficient: float = 1e-8) -> float:
        """
        Estimate steady-state temperature rise.
        
        Args:
            cooling_coefficient: Effective cooling coefficient (W/K)
        
        Returns:
            Temperature rise in Kelvin
        """
        # Heat generation vs. cooling balance
        heat_gen = self.total_heat_generation()
        return heat_gen / cooling_coefficient


@dataclass
class GlialCoolingModel:
    """
    Model of glial cell thermal management.
    
    Astrocytes provide cooling through:
    1. Spatial buffering of K+
    2. Metabolic coupling (lactate shuttle)
    3. Water movement
    4. Endfeet proximity to blood vessels
    """
    
    # Astrocyte parameters
    astrocyte_volume: float = 10e-15  # 10,000 μm³
    endfeet_area: float = 100e-12  # 100 μm² (blood vessel contact)
    
    # Cooling mechanisms
    water_perfusion_rate: float = 1e-6  # m/s through aquaporins
    metabolic_heat_removal: float = 0.1  # Fraction of heat via lactate shuttle
    
    # Thermal conductivity enhancement
    glial_thermal_k: float = 0.7  # W/mK (slightly higher than cytoplasm)
    
    def cooling_rate(self, local_temperature: float, blood_temp: float = 310.15) -> float:
        """
        Calculate cooling rate through glial mechanisms.
        
        Returns: Cooling power in Watts
        """
        delta_T = local_temperature - blood_temp
        
        # Heat removal via water movement
        # Q = ρ * c_p * v * A * ΔT
        water_cooling = (1000 * 4186 * self.water_perfusion_rate * 
                        self.endfeet_area * delta_T)
        
        # Metabolic heat removal (simplified)
        metabolic_cooling = 0  # Would require metabolic model
        
        return water_cooling
    
    def effective_thermal_conductivity(self, base_k: float = 0.6) -> float:
        """
        Effective thermal conductivity of neuron-glia composite.
        """
        # Series/parallel model
        # Neurons and glia are interspersed
        f_glia = 0.25  # Volume fraction of astrocytes
        return base_k * (1 - f_glia) + self.glial_thermal_k * f_glia


@dataclass
class BloodVesselCooling:
    """
    Model of blood vessel cooling in brain tissue.
    
    Blood provides dominant cooling mechanism in brain:
    - High specific heat
    - Continuous flow
    - Distributed network
    """
    
    # Vessel parameters
    vessel_diameter: float = 10e-6  # 10 μm capillary
    blood_velocity: float = 1e-3    # 1 mm/s in capillaries
    
    # Blood properties
    blood_temp: float = 310.15  # K (arterial)
    blood_specific_heat: float = 3.6e3  # J/kg/K
    blood_density: float = 1060  # kg/m³
    
    # Tissue properties
    thermal_conductivity_tissue: float = 0.5  # W/mK
    
    def perfusion_cooling_rate(self, tissue_temp: float, 
                               tissue_volume: float) -> float:
        """
        Calculate cooling rate from blood perfusion.
        
        Q = ρ * c_p * w * V * ΔT
        
        Args:
            tissue_temp: Local tissue temperature (K)
            tissue_volume: Tissue volume being cooled (m³)
        
        Returns:
            Cooling rate in Watts
        """
        # Perfusion rate in m³ blood / m³ tissue / s
        # Grey matter: ~50 mL/100g/min ≈ 0.0083 s⁻¹
        perfusion_rate = 0.0083
        
        delta_T = tissue_temp - self.blood_temp
        
        cooling_rate = (self.blood_density * self.blood_specific_heat * 
                       perfusion_rate * tissue_volume * delta_T)
        
        return cooling_rate
    
    def vessel_heat_transfer_coefficient(self) -> float:
        """
        Heat transfer coefficient for vessel wall.
        
        h = Nu * k / D
        """
        # Nusselt number for flow in tube (Graetz problem)
        # For fully developed flow: Nu ≈ 3.66
        Nu = 3.66
        
        h = Nu * self.thermal_conductivity_tissue / self.vessel_diameter
        return h
    
    def critical_radius(self) -> float:
        """
        Critical radius for maximum heat transfer.
        
        r_crit = k_tissue / h
        
        For insulation optimization.
        """
        h = self.vessel_heat_transfer_coefficient()
        return self.thermal_conductivity_tissue / h


class BioInspiredThermalDesign:
    """
    Translates biological thermal mechanisms to chip design principles.
    """
    
    @staticmethod
    def spine_neck_thermal_isolation(
        desired_isolation: float = 0.5,
        heat_source_power: float = 1e-6
    ) -> Dict:
        """
        Design spine-neck-inspired thermal isolation structure.
        
        Args:
            desired_isolation: Fraction of heat that should be isolated
            heat_source_power: Heat generation at source
        
        Returns:
            Dictionary with geometry recommendations
        """
        k = 0.6  # SiO2-like thermal conductivity
        
        # Thermal resistance needed
        R_needed = desired_isolation * 10  # K/W target
        
        # For a neck-like structure
        # R = L / (k * A)
        # Trade-off between L and A
        
        results = {}
        
        # Design options
        for neck_diameter in [50e-9, 100e-9, 150e-9, 200e-9]:
            area = np.pi * (neck_diameter / 2)**2
            neck_length = R_needed * k * area
            
            results[f"neck_{neck_diameter*1e9:.0f}nm"] = {
                "diameter": neck_diameter,
                "length": neck_length,
                "thermal_resistance": neck_length / (k * area),
                "aspect_ratio": neck_length / neck_diameter
            }
        
        return results
    
    @staticmethod
    def glial_cooling_analog(
        power_density: float = 1e6  # W/m²
    ) -> Dict:
        """
        Design glial-inspired cooling structures.
        
        Analogies:
        - Astrocyte endfeet → Thermal vias to heat spreader
        - Water perfusion → Microfluidic cooling
        - Metabolic coupling → Heat pipes
        
        Args:
            power_density: Target power density to cool
        
        Returns:
            Cooling structure recommendations
        """
        results = {}
        
        # Thermal via density
        # Each via can conduct: Q = k * A * ΔT / L
        k_cu = 400  # W/mK
        via_diameter = 100e-9  # 100 nm
        via_length = 10e-6    # 10 μm (through oxide)
        delta_T = 10  # K temperature budget
        
        via_conductance = k_cu * np.pi * (via_diameter/2)**2 / via_length
        
        # Number of vias needed per unit area
        via_density = power_density / (via_conductance * delta_T)
        
        results["thermal_vias"] = {
            "via_diameter": via_diameter,
            "via_length": via_length,
            "via_conductance": via_conductance,
            "via_density": via_density,
            "via_pitch": 1.0 / np.sqrt(via_density) if via_density > 0 else np.inf
        }
        
        # Heat spreader (analogous to blood vessel)
        # Spreader should have high thermal conductivity
        results["heat_spreader"] = {
            "material": "copper",
            "min_thickness": power_density * 1e-6 / k_cu,  # For ΔT < 1K per μm
            "role": "Analogous to blood vessel cooling"
        }
        
        return results
    
    @staticmethod
    def activity_dependent_thermal_budget(
        operation_energy: float = 0.5e-12,  # J per operation
        max_temp_rise: float = 10.0,  # K
        thermal_resistance: float = 100e3  # K/W (to ambient)
    ) -> Dict:
        """
        Calculate thermal budget for activity patterns.
        
        Analogous to biological adaptation of firing rates to prevent overheating.
        
        Args:
            operation_energy: Energy per operation
            max_temp_rise: Maximum allowed temperature rise
            thermal_resistance: Thermal resistance to ambient
        
        Returns:
            Activity budget recommendations
        """
        results = {}
        
        # Maximum continuous power
        max_power = max_temp_rise / thermal_resistance
        
        # Maximum continuous operation rate
        max_sustained_rate = max_power / operation_energy
        
        results["power_budget"] = {
            "max_power": max_power,
            "max_sustained_rate": max_sustained_rate,
            "max_sustained_ops_per_sec": max_sustained_rate
        }
        
        # Burst operation (higher peak, lower duty cycle)
        # Assume thermal time constant limits burst duration
        burst_results = {}
        for duty_cycle in [0.1, 0.25, 0.5]:
            # Average power = peak power * duty cycle
            # peak_power = max_power / duty_cycle
            peak_power = max_power / duty_cycle
            peak_rate = peak_power / operation_energy
            
            burst_results[f"duty_{duty_cycle}"] = {
                "peak_rate": peak_rate,
                "average_rate": peak_rate * duty_cycle,
                "burst_to_sustained_ratio": 1.0 / duty_cycle
            }
        
        results["burst_budget"] = burst_results
        
        return results


def analyze_biological_thermal_mechanisms():
    """Comprehensive analysis of biological thermal mechanisms."""
    print("=" * 70)
    print("BIOLOGICAL THERMAL MECHANISMS ANALYSIS")
    print("=" * 70)
    
    # 1. Synapse thermal model
    print("\n1. SYNAPTIC HEAT GENERATION")
    print("-" * 40)
    
    for morphology in SpineMorphology:
        synapse = SynapseThermalModel(
            spine_morphology=morphology,
            firing_rate=10.0
        )
        
        print(f"\n{morphology.value.upper()} SPINE:")
        print(f"  Head diameter: {synapse.spine_head_diameter*1e9:.0f} nm")
        print(f"  Neck diameter: {synapse.spine_neck_diameter*1e9:.0f} nm")
        print(f"  Neck length: {synapse.spine_neck_length*1e9:.0f} nm")
        print(f"  Total volume: {synapse.total_volume()*1e18:.2f} μm³")
        print(f"  Neck thermal resistance: {synapse.neck_thermal_resistance():.2e} K/W")
        print(f"  Heat generation: {synapse.total_heat_generation()*1e12:.3f} pW")
        print(f"  Power density: {synapse.power_density():.2e} W/m³")
    
    # 2. Compare with MAC unit
    print("\n2. SILICON vs BIOLOGICAL COMPARISON")
    print("-" * 40)
    
    # Biological synapse
    bio_synapse = SynapseThermalModel(firing_rate=10.0)
    bio_power = bio_synapse.total_heat_generation()
    bio_volume = bio_synapse.total_volume()
    
    # Silicon MAC unit (100nm x 100nm x 50nm)
    silicon_volume = 100e-9 * 100e-9 * 50e-9
    silicon_power = 0.5e-12 * 1e9 * 0.5  # 0.5 pJ/op at 1 GHz, 50% activity
    
    print(f"Biological synapse:")
    print(f"  Power: {bio_power*1e12:.3f} pW")
    print(f"  Volume: {bio_volume*1e18:.2f} μm³")
    print(f"  Power density: {bio_power/bio_volume:.2e} W/m³")
    
    print(f"\nSilicon MAC unit:")
    print(f"  Power: {silicon_power*1e12:.1f} pW")
    print(f"  Volume: {silicon_volume*1e18:.4f} μm³")
    print(f"  Power density: {silicon_power/silicon_volume:.2e} W/m³")
    
    print(f"\nPower density ratio (Silicon/Bio): {silicon_power/silicon_volume / (bio_power/bio_volume):.0f}x")
    
    # 3. Thermal isolation design
    print("\n3. SPINE-NECK INSPIRED THERMAL ISOLATION")
    print("-" * 40)
    
    design = BioInspiredThermalDesign.spine_neck_thermal_isolation()
    for name, specs in design.items():
        print(f"\n{name}:")
        print(f"  Diameter: {specs['diameter']*1e9:.0f} nm")
        print(f"  Length: {specs['length']*1e9:.1f} nm")
        print(f"  Thermal R: {specs['thermal_resistance']:.2e} K/W")
        print(f"  Aspect ratio: {specs['aspect_ratio']:.2f}")
    
    # 4. Activity-dependent thermal budget
    print("\n4. ACTIVITY-DEPENDENT THERMAL BUDGET")
    print("-" * 40)
    
    budget = BioInspiredThermalDesign.activity_dependent_thermal_budget()
    print(f"Max sustained power: {budget['power_budget']['max_power']*1e6:.2f} μW")
    print(f"Max sustained rate: {budget['power_budget']['max_sustained_ops_per_sec']/1e9:.2f} Gops/s")
    
    print("\nBurst operation budgets:")
    for name, specs in budget['burst_budget'].items():
        print(f"  {name}: Peak {specs['peak_rate']/1e9:.1f} Gops/s, "
              f"Avg {specs['average_rate']/1e9:.2f} Gops/s")
    
    return {
        "synapse_model": bio_synapse,
        "design_recommendations": design,
        "thermal_budget": budget
    }


if __name__ == "__main__":
    results = analyze_biological_thermal_mechanisms()
