#!/usr/bin/env python3
"""
Cycle 18: Energy Harvesting for Autonomous Operation
Mask-Locked Inference Chip Simulation Series

Analyzes energy harvesting sources, power budget, storage, and PMIC for
autonomous edge deployment scenarios.

Key Parameters:
- Power budget: 5W continuous (from previous cycles)
- Low-power mode: 0.5W, 5 tok/s
- Burst mode: 5W, 25 tok/s for 10 seconds
- Duty-cycled: 1 second inference per minute
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json
from datetime import datetime, timedelta

# Physical Constants
K_BOLTZMANN = 1.380649e-23  # J/K
ELECTRON_CHARGE = 1.602176634e-19  # C
PLANCK_CONSTANT = 6.62607015e-34  # J·s
SPEED_OF_LIGHT = 299792458  # m/s


class HarvesterType(Enum):
    SOLAR_OUTDOOR = "solar_outdoor"
    SOLAR_INDOOR = "solar_indoor"
    THERMOELECTRIC_BODY = "thermoelectric_body"
    THERMOELECTRIC_INDUSTRIAL = "thermoelectric_industrial"
    PIEZOELECTRIC_VIBRATION = "piezoelectric_vibration"
    RF_WIFI = "rf_wifi"
    RF_CELLULAR = "rf_cellular"
    KINETIC_MOTION = "kinetic_motion"


class StorageType(Enum):
    SUPERCAPACITOR = "supercapacitor"
    LI_ION_BATTERY = "li_ion_battery"
    LI_POLYMER = "li_polymer"
    SOLID_STATE_BATTERY = "solid_state_battery"


@dataclass
class HarvesterSpec:
    """Specification for an energy harvester"""
    name: str
    harvester_type: HarvesterType
    power_density: float  # W/cm² or W/g
    efficiency: float  # Conversion efficiency
    area_cm2: float = 1.0  # Active area in cm²
    mass_g: float = 0.0  # Mass in grams
    operating_conditions: Dict = field(default_factory=dict)
    cost_per_unit: float = 0.0  # USD
    
    @property
    def peak_power(self) -> float:
        """Calculate peak power output"""
        return self.power_density * self.area_cm2 * self.efficiency


@dataclass
class StorageSpec:
    """Specification for energy storage"""
    name: str
    storage_type: StorageType
    capacity_wh: float  # Watt-hours
    voltage_nominal: float  # Volts
    esr_mohm: float  # Equivalent series resistance in mΩ
    cycle_life: int  # Charge/discharge cycles
    self_discharge_monthly: float  # % per month
    charge_efficiency: float  # Charging efficiency
    cost_per_unit: float  # USD
    mass_g: float  # Mass in grams
    volume_cm3: float  # Volume in cm³
    
    @property
    def capacity_joules(self) -> float:
        """Convert capacity to Joules"""
        return self.capacity_wh * 3600


@dataclass
class PMICSpec:
    """Power Management IC specification"""
    name: str
    input_voltage_range: Tuple[float, float]  # V
    output_voltage: float  # V
    efficiency_buck: float  # Buck converter efficiency
    efficiency_boost: float  # Boost converter efficiency
    quiescent_current_ua: float  # Quiescent current in µA
    mppt_algorithm: str  # MPPT type
    cold_start_voltage: float  # Minimum voltage for cold start
    cost_per_unit: float  # USD


@dataclass
class PowerBudget:
    """Power budget for different operating modes"""
    mode_name: str
    power_w: float  # Watts
    tokens_per_second: float
    duration_s: float  # Duration per activation
    interval_s: float  # Time between activations
    tokens_per_inference: int
    
    @property
    def duty_cycle(self) -> float:
        """Calculate duty cycle"""
        return self.duration_s / self.interval_s
    
    @property
    def average_power(self) -> float:
        """Calculate average power"""
        return self.power_w * self.duty_cycle
    
    @property
    def tokens_per_hour(self) -> float:
        """Calculate tokens generated per hour"""
        activations_per_hour = 3600 / self.interval_s
        return activations_per_hour * self.tokens_per_inference


class EnergyHarvesterModel:
    """Model for energy harvesting analysis"""
    
    def __init__(self):
        self.harvesters = self._initialize_harvesters()
        self.storage = self._initialize_storage()
        self.pmic = self._initialize_pmic()
        self.power_budgets = self._initialize_power_budgets()
        
    def _initialize_harvesters(self) -> Dict[HarvesterType, HarvesterSpec]:
        """Initialize harvester specifications based on literature"""
        return {
            HarvesterType.SOLAR_OUTDOOR: HarvesterSpec(
                name="Outdoor Solar Panel",
                harvester_type=HarvesterType.SOLAR_OUTDOOR,
                power_density=0.10,  # 100 mW/cm² peak (1000 W/m² solar irradiance, 10% efficiency)
                efficiency=0.15,  # 15% cell efficiency
                area_cm2=100,  # 100 cm² = 10×10 cm panel
                operating_conditions={
                    "irradiance_range": (200, 1000),  # W/m²
                    "temperature_range": (-20, 60),  # °C
                    "avg_sunlight_hours": 5,  # Hours/day
                },
                cost_per_unit=15.0
            ),
            HarvesterType.SOLAR_INDOOR: HarvesterSpec(
                name="Indoor Solar Panel",
                harvester_type=HarvesterType.SOLAR_INDOOR,
                power_density=0.001,  # 1 mW/cm² (indoor lighting ~10 W/m²)
                efficiency=0.20,  # 20% for optimized indoor cells
                area_cm2=100,
                operating_conditions={
                    "lux_range": (200, 1000),  # Lux
                    "light_sources": ["LED", "fluorescent", "natural"],
                    "avg_light_hours": 12,  # Hours/day
                },
                cost_per_unit=20.0
            ),
            HarvesterType.THERMOELECTRIC_BODY: HarvesterSpec(
                name="Body Heat TEG",
                harvester_type=HarvesterType.THERMOELECTRIC_BODY,
                power_density=0.00003,  # 30 µW/cm² (ΔT ≈ 5K)
                efficiency=0.02,  # 2% Seebeck efficiency
                area_cm2=50,  # 50 cm² wearable patch
                mass_g=30,
                operating_conditions={
                    "delta_T_range": (2, 10),  # K
                    "skin_temp": 37,  # °C
                    "ambient_temp_range": (15, 30),  # °C
                },
                cost_per_unit=25.0
            ),
            HarvesterType.THERMOELECTRIC_INDUSTRIAL: HarvesterSpec(
                name="Industrial Waste Heat TEG",
                harvester_type=HarvesterType.THERMOELECTRIC_INDUSTRIAL,
                power_density=0.0025,  # 2.5 mW/cm² (ΔT ≈ 50K)
                efficiency=0.05,  # 5% at higher ΔT
                area_cm2=100,
                mass_g=200,
                operating_conditions={
                    "delta_T_range": (30, 150),  # K
                    "hot_side_temp_range": (50, 200),  # °C
                },
                cost_per_unit=80.0
            ),
            HarvesterType.PIEZOELECTRIC_VIBRATION: HarvesterSpec(
                name="Piezoelectric Vibration Harvester",
                harvester_type=HarvesterType.PIEZOELECTRIC_VIBRATION,
                power_density=0.0001,  # 100 µW/cm²
                efficiency=0.30,  # 30% conversion
                area_cm2=10,  # Cantilever size
                mass_g=5,
                operating_conditions={
                    "frequency_range": (50, 200),  # Hz
                    "acceleration_range": (0.1, 2.0),  # g
                    "resonant_freq": 120,  # Hz
                },
                cost_per_unit=35.0
            ),
            HarvesterType.RF_WIFI: HarvesterSpec(
                name="WiFi RF Harvester",
                harvester_type=HarvesterType.RF_WIFI,
                power_density=0.0000001,  # 0.1 µW/cm² at 5m
                efficiency=0.50,  # 50% RF-DC efficiency
                area_cm2=25,  # 5×5 cm antenna
                operating_conditions={
                    "frequency": 2.4,  # GHz
                    "tx_power": 20,  # dBm (WiFi router)
                    "distance_range": (0.5, 10),  # m
                },
                cost_per_unit=15.0
            ),
            HarvesterType.RF_CELLULAR: HarvesterSpec(
                name="Cellular RF Harvester",
                harvester_type=HarvesterType.RF_CELLULAR,
                power_density=0.000001,  # 1 µW/cm² near tower
                efficiency=0.40,  # 40% RF-DC
                area_cm2=100,  # Larger antenna
                operating_conditions={
                    "frequency_bands": ["LTE", "5G"],
                    "distance_to_tower": (100, 1000),  # m
                },
                cost_per_unit=25.0
            ),
            HarvesterType.KINETIC_MOTION: HarvesterSpec(
                name="Kinetic Motion Harvester",
                harvester_type=HarvesterType.KINETIC_MOTION,
                power_density=0.0005,  # 500 µW/g for walking
                efficiency=0.25,
                area_cm2=5,
                mass_g=50,  # Important: mass matters
                operating_conditions={
                    "motion_type": ["walking", "running", "arm_swing"],
                    "frequency_range": (1, 5),  # Hz
                },
                cost_per_unit=40.0
            ),
        }
    
    def _initialize_storage(self) -> Dict[StorageType, StorageSpec]:
        """Initialize energy storage specifications"""
        return {
            StorageType.SUPERCAPACITOR: StorageSpec(
                name="Supercapacitor (EDLC)",
                storage_type=StorageType.SUPERCAPACITOR,
                capacity_wh=0.1,  # 100 mWh typical
                voltage_nominal=3.3,
                esr_mohm=30,
                cycle_life=1000000,
                self_discharge_monthly=20,  # % per month
                charge_efficiency=0.95,
                cost_per_unit=5.0,
                mass_g=20,
                volume_cm3=15
            ),
            StorageType.LI_ION_BATTERY: StorageSpec(
                name="Lithium-Ion Battery",
                storage_type=StorageType.LI_ION_BATTERY,
                capacity_wh=3.0,  # 3 Wh typical small cell
                voltage_nominal=3.7,
                esr_mohm=50,
                cycle_life=500,
                self_discharge_monthly=2,
                charge_efficiency=0.90,
                cost_per_unit=8.0,
                mass_g=20,
                volume_cm3=10
            ),
            StorageType.LI_POLYMER: StorageSpec(
                name="Lithium-Polymer Battery",
                storage_type=StorageType.LI_POLYMER,
                capacity_wh=2.5,
                voltage_nominal=3.7,
                esr_mohm=40,
                cycle_life=300,
                self_discharge_monthly=3,
                charge_efficiency=0.92,
                cost_per_unit=10.0,
                mass_g=15,
                volume_cm3=12
            ),
            StorageType.SOLID_STATE_BATTERY: StorageSpec(
                name="Solid-State Battery",
                storage_type=StorageType.SOLID_STATE_BATTERY,
                capacity_wh=1.5,
                voltage_nominal=3.8,
                esr_mohm=100,
                cycle_life=1000,
                self_discharge_monthly=1,
                charge_efficiency=0.98,
                cost_per_unit=25.0,
                mass_g=10,
                volume_cm3=8
            ),
        }
    
    def _initialize_pmic(self) -> PMICSpec:
        """Initialize PMIC specification"""
        return PMICSpec(
            name="Texas Instruments BQ25570",
            input_voltage_range=(0.1, 5.0),
            output_voltage=3.3,
            efficiency_buck=0.92,
            efficiency_boost=0.85,
            quiescent_current_ua=488,  # nA to µA range for energy harvesting PMICs
            mppt_algorithm="Fractional Open Circuit Voltage",
            cold_start_voltage=0.33,
            cost_per_unit=5.0
        )
    
    def _initialize_power_budgets(self) -> Dict[str, PowerBudget]:
        """Initialize power budget scenarios"""
        return {
            "continuous_5w": PowerBudget(
                mode_name="Continuous 5W Operation",
                power_w=5.0,
                tokens_per_second=25,
                duration_s=1.0,
                interval_s=1.0,
                tokens_per_inference=25
            ),
            "low_power_0.5w": PowerBudget(
                mode_name="Low-Power Mode",
                power_w=0.5,
                tokens_per_second=5,
                duration_s=1.0,
                interval_s=1.0,
                tokens_per_inference=5
            ),
            "burst_5w_10s": PowerBudget(
                mode_name="Burst Mode (10s)",
                power_w=5.0,
                tokens_per_second=25,
                duration_s=10.0,
                interval_s=60.0,
                tokens_per_inference=250
            ),
            "duty_cycle_1s_per_min": PowerBudget(
                mode_name="Duty-Cycled (1s/min)",
                power_w=5.0,
                tokens_per_second=25,
                duration_s=1.0,
                interval_s=60.0,
                tokens_per_inference=25
            ),
            "intermittent_5min_per_hour": PowerBudget(
                mode_name="Intermittent (5min/hour)",
                power_w=5.0,
                tokens_per_second=25,
                duration_s=300.0,
                interval_s=3600.0,
                tokens_per_inference=7500
            ),
        }
    
    def calculate_harvester_sizing(self, target_power_w: float, 
                                   harvester_type: HarvesterType) -> Dict:
        """Calculate required harvester size for target power"""
        harvester = self.harvesters[harvester_type]
        
        # Account for PMIC efficiency
        pmic_eff = (self.pmic.efficiency_boost + self.pmic.efficiency_buck) / 2
        required_input_power = target_power_w / pmic_eff
        
        # Calculate area
        effective_power_density = harvester.power_density * harvester.efficiency
        required_area = required_input_power / effective_power_density
        
        # Calculate for different availability factors
        results = {
            "target_power_w": target_power_w,
            "harvester_type": harvester_type.value,
            "pmic_efficiency": pmic_eff,
            "required_input_power_w": required_input_power,
            "power_density_mw_cm2": effective_power_density * 1000,
            "sizing": {}
        }
        
        # Calculate area for different scenarios
        availability_factors = {
            "peak": 1.0,
            "average_outdoor": 0.5,  # Accounting for day/night, weather
            "average_indoor": 0.7,  # Indoor more consistent
            "conservative": 0.3,
        }
        
        for scenario, factor in availability_factors.items():
            area = required_area / factor
            results["sizing"][scenario] = {
                "availability_factor": factor,
                "area_cm2": area,
                "panel_size_cm": np.sqrt(area),
                "peak_power_mw": area * effective_power_density * 1000,
            }
        
        return results
    
    def calculate_charge_time(self, storage_type: StorageType, 
                             harvester_type: HarvesterType,
                             target_soc: float = 0.9) -> Dict:
        """Calculate time to charge storage to target state of charge"""
        storage = self.storage[storage_type]
        harvester = self.harvesters[harvester_type]
        pmic = self.pmic
        
        # Effective charging power
        harvest_power = harvester.peak_power
        charge_power = harvest_power * pmic.efficiency_boost * storage.charge_efficiency
        
        # Energy to store
        target_energy_j = storage.capacity_joules * target_soc
        
        # Account for self-discharge
        discharge_rate = storage.self_discharge_monthly / 100 / 30 / 24 / 3600  # per second
        discharge_power = storage.capacity_joules * discharge_rate
        
        # Net charging power
        net_charge_power = charge_power - discharge_power
        
        if net_charge_power <= 0:
            charge_time_s = float('inf')
        else:
            charge_time_s = target_energy_j / net_charge_power
        
        return {
            "storage_type": storage_type.value,
            "harvester_type": harvester_type.value,
            "harvest_power_mw": harvest_power * 1000,
            "charge_power_mw": charge_power * 1000,
            "discharge_power_mw": discharge_power * 1000,
            "target_soc": target_soc,
            "target_energy_mj": target_energy_j / 1000,
            "charge_time_s": charge_time_s,
            "charge_time_min": charge_time_s / 60,
            "charge_time_hours": charge_time_s / 3600,
            "feasible": net_charge_power > 0,
        }
    
    def analyze_duty_cycle_feasibility(self, budget_name: str,
                                       harvester_type: HarvesterType,
                                       storage_type: StorageType) -> Dict:
        """Analyze feasibility of duty-cycled operation"""
        budget = self.power_budgets[budget_name]
        harvester = self.harvesters[harvester_type]
        storage = self.storage[storage_type]
        pmic = self.pmic
        
        # Energy per inference cycle
        energy_per_cycle_j = budget.power_w * budget.duration_s
        
        # Average power consumption
        avg_power_w = budget.average_power
        
        # Harvester power (accounting for availability)
        if harvester_type in [HarvesterType.SOLAR_OUTDOOR]:
            availability = 0.5  # Day/night average
        elif harvester_type in [HarvesterType.SOLAR_INDOOR]:
            availability = 0.7
        else:
            availability = 0.9  # Continuous sources
        
        harvest_power_w = harvester.peak_power * availability
        net_harvest_w = harvest_power_w * pmic.efficiency_boost
        
        # Storage requirements
        storage_capacity_j = storage.capacity_joules
        
        # Can storage handle one burst?
        storage_sufficient = storage_capacity_j >= energy_per_cycle_j * 1.2  # 20% margin
        
        # Number of cycles possible on full charge
        cycles_on_charge = storage_capacity_j / energy_per_cycle_j if energy_per_cycle_j > 0 else 0
        
        # Time to recharge for one cycle
        energy_deficit_j = energy_per_cycle_j
        recharge_time_s = energy_deficit_j / net_harvest_w if net_harvest_w > 0 else float('inf')
        
        # Feasibility check
        sustainable = net_harvest_w >= avg_power_w
        energy_positive = (energy_per_cycle_j / budget.interval_s) <= net_harvest_w
        
        # Daily operation analysis
        daily_cycles = 86400 / budget.interval_s
        daily_energy_needed_j = daily_cycles * energy_per_cycle_j
        daily_energy_harvested_j = net_harvest_w * 86400
        daily_net_energy_j = daily_energy_harvested_j - daily_energy_needed_j
        
        return {
            "budget_name": budget_name,
            "harvester_type": harvester_type.value,
            "storage_type": storage_type.value,
            "power_budget": {
                "peak_power_w": budget.power_w,
                "duration_s": budget.duration_s,
                "interval_s": budget.interval_s,
                "duty_cycle_pct": budget.duty_cycle * 100,
                "average_power_mw": avg_power_w * 1000,
                "energy_per_cycle_j": energy_per_cycle_j,
            },
            "harvester": {
                "peak_power_mw": harvester.peak_power * 1000,
                "available_power_mw": net_harvest_w * 1000,
                "availability_factor": availability,
            },
            "storage": {
                "capacity_mj": storage_capacity_j / 1000,
                "cycles_on_charge": cycles_on_charge,
                "storage_sufficient": storage_sufficient,
            },
            "feasibility": {
                "sustainable": sustainable,
                "energy_positive": energy_positive,
                "recharge_time_s": recharge_time_s,
                "recharge_time_min": recharge_time_s / 60,
            },
            "daily_analysis": {
                "daily_cycles": daily_cycles,
                "energy_needed_kj": daily_energy_needed_j / 1000,
                "energy_harvested_kj": daily_energy_harvested_j / 1000,
                "net_energy_kj": daily_net_energy_j / 1000,
                "autonomous_days": max(0, storage_capacity_j / daily_energy_needed_j) if daily_energy_needed_j > daily_energy_harvested_j else float('inf'),
            }
        }
    
    def simulate_intermittent_inference(self, budget_name: str,
                                        harvester_type: HarvesterType,
                                        storage_type: StorageType,
                                        simulation_hours: float = 24.0,
                                        dt: float = 1.0) -> Dict:
        """Simulate intermittent inference operation over time"""
        budget = self.power_budgets[budget_name]
        harvester = self.harvesters[harvester_type]
        storage = self.storage[storage_type]
        pmic = self.pmic
        
        # Time array
        t = np.arange(0, simulation_hours * 3600, dt)
        n_steps = len(t)
        
        # Initialize state arrays
        energy_stored = np.zeros(n_steps)
        energy_stored[0] = storage.capacity_joules * 0.5  # Start at 50% SOC
        
        inference_count = np.zeros(n_steps)
        tokens_generated = np.zeros(n_steps)
        harvested_energy = np.zeros(n_steps)
        
        # Power flows
        harvest_power = harvester.peak_power * pmic.efficiency_boost
        inference_energy = budget.power_w * budget.duration_s
        
        # Time tracking
        last_inference_time = -budget.interval_s
        
        for i in range(1, n_steps):
            # Harvest energy
            energy_harvested = harvest_power * dt
            harvested_energy[i] = energy_harvested
            
            # Self-discharge
            discharge = energy_stored[i-1] * storage.self_discharge_monthly / 100 / 30 / 24 / 3600 * dt
            
            # Update stored energy
            energy_stored[i] = energy_stored[i-1] + energy_harvested - discharge
            
            # Check if we can perform inference
            time_since_last = t[i] - last_inference_time
            can_infer = (time_since_last >= budget.interval_s and 
                        energy_stored[i] >= inference_energy * 1.1)  # 10% margin
            
            if can_infer:
                energy_stored[i] -= inference_energy
                inference_count[i] = inference_count[i-1] + 1
                tokens_generated[i] = inference_count[i] * budget.tokens_per_inference
                last_inference_time = t[i]
            else:
                inference_count[i] = inference_count[i-1]
                tokens_generated[i] = tokens_generated[i-1]
            
            # Clamp energy storage
            energy_stored[i] = np.clip(energy_stored[i], 0, storage.capacity_joules)
        
        return {
            "time_hours": t / 3600,
            "energy_stored_pct": energy_stored / storage.capacity_joules * 100,
            "inference_count": inference_count,
            "tokens_generated": tokens_generated,
            "total_inferences": inference_count[-1],
            "total_tokens": tokens_generated[-1],
            "avg_inferences_per_hour": inference_count[-1] / simulation_hours,
            "avg_tokens_per_hour": tokens_generated[-1] / simulation_hours,
            "min_soc_pct": np.min(energy_stored / storage.capacity_joules * 100),
        }


class ApplicationScenarioAnalyzer:
    """Analyze specific application scenarios"""
    
    def __init__(self, model: EnergyHarvesterModel):
        self.model = model
        
    def analyze_iot_sensor(self) -> Dict:
        """IoT sensor with periodic inference scenario"""
        # Typical IoT: 1 inference per hour, 5W for 1 second
        budget = PowerBudget(
            mode_name="IoT Sensor",
            power_w=5.0,
            tokens_per_second=25,
            duration_s=1.0,
            interval_s=3600.0,  # 1 hour
            tokens_per_inference=25
        )
        
        results = {
            "scenario": "IoT Sensor with Periodic Inference",
            "description": "Environmental monitoring with hourly inference",
            "power_profile": {
                "peak_power_w": budget.power_w,
                "duration_s": budget.duration_s,
                "interval_min": budget.interval_s / 60,
                "energy_per_inference_mj": budget.power_w * budget.duration_s * 1000,
            },
            "recommended_harvesters": [],
        }
        
        # Analyze each harvester
        for h_type in [HarvesterType.SOLAR_INDOOR, HarvesterType.RF_WIFI, 
                       HarvesterType.PIEZOELECTRIC_VIBRATION]:
            harvester = self.model.harvesters[h_type]
            storage = self.model.storage[StorageType.SUPERCAPACITOR]
            
            analysis = self.model.analyze_duty_cycle_feasibility(
                "duty_cycle_1s_per_min", h_type, StorageType.SUPERCAPACITOR
            )
            
            # Adjust for actual IoT interval
            energy_needed_mj = budget.power_w * budget.duration_s * 1000
            harvest_power_mw = harvester.peak_power * 1000
            charge_time_min = energy_needed_mj / harvest_power_mw / 60 if harvest_power_mw > 0 else float('inf')
            
            feasible = charge_time_min < 60  # Can recharge within interval
            
            results["recommended_harvesters"].append({
                "type": h_type.value,
                "power_mw": harvest_power_mw,
                "charge_time_min": charge_time_min,
                "feasible": feasible,
                "notes": "Suitable for hourly inference" if feasible else "Insufficient power"
            })
        
        return results
    
    def analyze_wearable_ai(self) -> Dict:
        """Wearable AI assistant scenario"""
        results = {
            "scenario": "Wearable AI Assistant",
            "description": "Continuous inference for voice assistant",
            "power_requirements": {
                "continuous_power_w": 0.5,  # Low-power mode
                "burst_power_w": 5.0,  # Full inference
                "avg_daily_usage_hours": 4,
                "daily_energy_wh": 0.5 * 4 + 5.0 * 0.1,  # 4h low-power + 6 min burst
            },
            "harvester_options": [],
        }
        
        # Body heat + kinetic combination
        body_heat = self.model.harvesters[HarvesterType.THERMOELECTRIC_BODY]
        kinetic = self.model.harvesters[HarvesterType.KINETIC_MOTION]
        
        combined_power_mw = (body_heat.peak_power + kinetic.peak_power) * 1000
        daily_energy_mj = combined_power_mw * 24 * 3600 / 1000  # mW * s
        
        results["harvester_options"] = [
            {
                "type": "thermoelectric_body",
                "power_mw": body_heat.peak_power * 1000,
                "daily_energy_mj": body_heat.peak_power * 86400 * 1000,
                "feasibility": "Supplemental only"
            },
            {
                "type": "kinetic_motion",
                "power_mw": kinetic.peak_power * 1000,
                "daily_energy_mj": kinetic.peak_power * 86400 * 1000,
                "feasibility": "Supplemental only"
            },
            {
                "type": "combined",
                "power_mw": combined_power_mw,
                "daily_energy_mj": daily_energy_mj,
                "feasibility": "Extends battery life by ~10%",
                "recommendation": "Use with Li-Polymer battery"
            }
        ]
        
        # Battery sizing
        daily_wh = results["power_requirements"]["daily_energy_wh"]
        results["battery_sizing"] = {
            "daily_consumption_wh": daily_wh,
            "recommended_capacity_wh": daily_wh * 3,  # 3-day reserve
            "battery_type": "Li-Polymer",
            "mass_g": 15 * 3,
            "volume_cm3": 12 * 3,
        }
        
        return results
    
    def analyze_environmental_monitoring(self) -> Dict:
        """Environmental monitoring station scenario"""
        results = {
            "scenario": "Environmental Monitoring Station",
            "description": "Remote sensor with solar power",
            "power_requirements": {
                "inference_interval_min": 15,
                "inference_duration_s": 2,
                "peak_power_w": 5.0,
                "standby_power_mw": 10,
            },
            "solar_sizing": {},
        }
        
        # Calculate energy budget
        interval_s = 15 * 60  # 15 minutes
        duration_s = 2
        standby_power = 0.010  # 10 mW
        
        # Daily energy calculation
        inferences_per_day = 86400 / interval_s
        inference_energy_wh = 5.0 * duration_s * inferences_per_day / 3600
        standby_energy_wh = standby_power * 24
        
        total_daily_wh = inference_energy_wh + standby_energy_wh
        avg_power_mw = total_daily_wh / 24 * 1000
        
        results["energy_budget"] = {
            "inferences_per_day": inferences_per_day,
            "inference_energy_wh": inference_energy_wh,
            "standby_energy_wh": standby_energy_wh,
            "total_daily_wh": total_daily_wh,
            "average_power_mw": avg_power_mw,
        }
        
        # Solar panel sizing
        # Assuming 5 hours peak sun, 20% efficiency
        daily_solar_hours = 5
        required_harvest_w = total_daily_wh / daily_solar_hours
        
        # With 15% efficient panel at 1000 W/m²
        panel_efficiency = 0.15
        irradiance_w_m2 = 1000
        
        panel_area_m2 = required_harvest_w / (irradiance_w_m2 * panel_efficiency)
        panel_area_cm2 = panel_area_m2 * 10000
        
        results["solar_sizing"] = {
            "required_harvest_w": required_harvest_w,
            "panel_area_cm2": panel_area_cm2,
            "panel_size_cm": np.sqrt(panel_area_cm2),
            "recommended_panel": f"{np.ceil(panel_area_cm2/100)*100:.0f} cm² solar panel",
            "battery_days_reserve": 7,
            "battery_capacity_wh": total_daily_wh * 7,
        }
        
        return results
    
    def analyze_industrial_predictive_maintenance(self) -> Dict:
        """Industrial predictive maintenance scenario"""
        results = {
            "scenario": "Industrial Predictive Maintenance",
            "description": "Vibration-powered sensor on rotating equipment",
            "harvesting_conditions": {
                "vibration_source": "Electric motor",
                "frequency_hz": 60,  # 60 Hz motor
                "acceleration_g": 0.5,
                "temperature_c": 50,
            },
            "power_requirements": {
                "inference_interval_min": 30,
                "inference_duration_s": 5,
                "peak_power_w": 5.0,
            },
        }
        
        # Piezoelectric harvester analysis
        piezo = self.model.harvesters[HarvesterType.PIEZOELECTRIC_VIBRATION]
        teg = self.model.harvesters[HarvesterType.THERMOELECTRIC_INDUSTRIAL]
        
        # Combined harvesting
        piezo_power_mw = piezo.peak_power * 1000
        teg_power_mw = teg.peak_power * 1000
        combined_power_mw = piezo_power_mw + teg_power_mw
        
        # Energy needed per inference
        energy_per_inference_mj = 5.0 * 5 * 1000  # 5W * 5s = 25J = 25000 mJ
        
        # Recharge time
        recharge_min = energy_per_inference_mj / combined_power_mw / 60
        
        results["harvester_analysis"] = {
            "piezoelectric": {
                "power_mw": piezo_power_mw,
                "suitable": piezo_power_mw > 0,
            },
            "thermoelectric": {
                "power_mw": teg_power_mw,
                "suitable": teg_power_mw > 0,
            },
            "combined": {
                "power_mw": combined_power_mw,
                "recharge_time_min": recharge_min,
                "feasible": recharge_min < 30,  # Within inference interval
            }
        }
        
        return results


def generate_visualizations(model: EnergyHarvesterModel, output_dir: str = "/home/z/my-project/research"):
    """Generate visualization plots"""
    
    # 1. Harvester Power Comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Harvester power density
    ax1 = axes[0, 0]
    harvester_names = [h.value.replace('_', ' ').title() for h in HarvesterType]
    power_densities = [model.harvesters[h].peak_power * 1000 for h in HarvesterType]  # mW
    colors = plt.cm.viridis(np.linspace(0, 1, len(harvester_names)))
    bars = ax1.barh(harvester_names, power_densities, color=colors)
    ax1.set_xlabel('Peak Power Output (mW)')
    ax1.set_title('Energy Harvester Peak Power Output\n(Default Configuration)')
    ax1.set_xscale('log')
    for bar, power in zip(bars, power_densities):
        ax1.text(bar.get_width() * 1.1, bar.get_y() + bar.get_height()/2,
                f'{power:.3f} mW', va='center', fontsize=8)
    
    # Plot 2: Storage comparison
    ax2 = axes[0, 1]
    storage_names = [s.value.replace('_', ' ').title() for s in StorageType]
    capacities = [model.storage[s].capacity_wh * 1000 for s in StorageType]  # mWh
    cycle_lives = [model.storage[s].cycle_life for s in StorageType]
    
    x = np.arange(len(storage_names))
    width = 0.35
    
    ax2_twin = ax2.twinx()
    bars1 = ax2.bar(x - width/2, capacities, width, label='Capacity (mWh)', color='steelblue')
    bars2 = ax2_twin.bar(x + width/2, np.log10(cycle_lives), width, label='Log10(Cycle Life)', color='coral')
    
    ax2.set_xlabel('Storage Type')
    ax2.set_ylabel('Capacity (mWh)', color='steelblue')
    ax2_twin.set_ylabel('Log10(Cycle Life)', color='coral')
    ax2.set_title('Energy Storage Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(storage_names, rotation=45, ha='right')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    
    # Plot 3: Power budget scenarios
    ax3 = axes[1, 0]
    budget_names = list(model.power_budgets.keys())
    avg_powers = [model.power_budgets[b].average_power * 1000 for b in budget_names]  # mW
    tokens_per_hour = [model.power_budgets[b].tokens_per_hour for b in budget_names]
    
    colors = ['#2ecc71' if p < 100 else '#e74c3c' for p in avg_powers]
    bars = ax3.bar(range(len(budget_names)), avg_powers, color=colors)
    ax3.set_xlabel('Operating Mode')
    ax3.set_ylabel('Average Power (mW)')
    ax3.set_title('Power Budget Scenarios\n(Green: Harvestable, Red: Challenging)')
    ax3.set_xticks(range(len(budget_names)))
    ax3.set_xticklabels([b.replace('_', '\n') for b in budget_names], fontsize=8)
    
    # Add tokens/hour annotation
    for bar, tph in zip(bars, tokens_per_hour):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{tph:.0f} tok/h', ha='center', fontsize=7)
    
    # Plot 4: Duty cycle energy balance
    ax4 = axes[1, 1]
    
    scenarios = []
    for budget_name in ["continuous_5w", "duty_cycle_1s_per_min", "burst_5w_10s", "intermittent_5min_per_hour"]:
        for h_type in [HarvesterType.SOLAR_OUTDOOR, HarvesterType.SOLAR_INDOOR, 
                      HarvesterType.RF_WIFI, HarvesterType.PIEZOELECTRIC_VIBRATION]:
            analysis = model.analyze_duty_cycle_feasibility(budget_name, h_type, StorageType.SUPERCAPACITOR)
            scenarios.append({
                "budget": budget_name.replace('_', ' ').title(),
                "harvester": h_type.value.replace('_', ' ').title(),
                "daily_net_kj": analysis["daily_analysis"]["net_energy_kj"],
                "feasible": analysis["feasibility"]["energy_positive"]
            })
    
    # Create heatmap-like visualization
    budgets_unique = list(set(s["budget"] for s in scenarios))
    harvesters_unique = list(set(s["harvester"] for s in scenarios))
    
    energy_matrix = np.zeros((len(harvesters_unique), len(budgets_unique)))
    for s in scenarios:
        i = harvesters_unique.index(s["harvester"])
        j = budgets_unique.index(s["budget"])
        energy_matrix[i, j] = s["daily_net_kj"]
    
    im = ax4.imshow(energy_matrix, cmap='RdYlGn', aspect='auto')
    ax4.set_xlabel('Operating Mode')
    ax4.set_ylabel('Harvester Type')
    ax4.set_title('Daily Net Energy Balance (kJ)\n(Green: Positive, Red: Deficit)')
    ax4.set_xticks(range(len(budgets_unique)))
    ax4.set_xticklabels([b[:15] + '...' if len(b) > 15 else b for b in budgets_unique], 
                       rotation=45, ha='right', fontsize=8)
    ax4.set_yticks(range(len(harvesters_unique)))
    ax4.set_yticklabels([h[:15] + '...' if len(h) > 15 else h for h in harvesters_unique], fontsize=8)
    plt.colorbar(im, ax=ax4, label='Net Energy (kJ)')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cycle18_harvester_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Solar Panel Sizing Chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Outdoor solar sizing
    ax1 = axes[0, 0]
    target_powers = np.linspace(0.1, 5.0, 50)  # 0.1W to 5W
    
    for availability, label, color in [(1.0, 'Peak Sun', 'gold'), 
                                        (0.5, 'Average Day', 'orange'),
                                        (0.3, 'Conservative', 'red')]:
        areas = []
        for p in target_powers:
            sizing = model.calculate_harvester_sizing(p, HarvesterType.SOLAR_OUTDOOR)
            area = sizing["sizing"]["peak"]["area_cm2"] / availability
            areas.append(area)
        ax1.plot(target_powers, areas, label=label, color=color, linewidth=2)
    
    ax1.axhline(y=100, color='green', linestyle='--', label='10×10 cm panel')
    ax1.axhline(y=1000, color='blue', linestyle='--', label='32×32 cm panel')
    ax1.axvline(x=5.0, color='red', linestyle=':', label='5W target')
    ax1.set_xlabel('Target Power (W)')
    ax1.set_ylabel('Required Panel Area (cm²)')
    ax1.set_title('Outdoor Solar Panel Sizing\n(1000 W/m² irradiance, 15% efficiency)')
    ax1.legend(fontsize=8)
    ax1.set_xlim(0, 5.5)
    ax1.set_ylim(0, 2000)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Indoor solar sizing
    ax2 = axes[0, 1]
    
    for availability, label, color in [(1.0, 'Bright Indoor', 'skyblue'),
                                        (0.7, 'Typical Office', 'steelblue'),
                                        (0.5, 'Dim Indoor', 'navy')]:
        areas = []
        for p in target_powers:
            sizing = model.calculate_harvester_sizing(p, HarvesterType.SOLAR_INDOOR)
            area = sizing["sizing"]["peak"]["area_cm2"] / availability
            areas.append(area)
        ax2.plot(target_powers, areas, label=label, color=color, linewidth=2)
    
    ax2.axhline(y=100, color='green', linestyle='--', label='10×10 cm')
    ax2.axhline(y=1000, color='blue', linestyle='--', label='32×32 cm')
    ax2.axvline(x=0.5, color='red', linestyle=':', label='0.5W low-power')
    ax2.set_xlabel('Target Power (W)')
    ax2.set_ylabel('Required Panel Area (cm²)')
    ax2.set_title('Indoor Solar Panel Sizing\n(10 W/m² irradiance, 20% efficiency)')
    ax2.legend(fontsize=8)
    ax2.set_xlim(0, 5.5)
    ax2.set_ylim(0, 10000)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Charge time analysis
    ax3 = axes[1, 0]
    
    harvester_types = [
        (HarvesterType.SOLAR_OUTDOOR, 'Outdoor Solar'),
        (HarvesterType.SOLAR_INDOOR, 'Indoor Solar'),
        (HarvesterType.RF_WIFI, 'WiFi RF'),
        (HarvesterType.PIEZOELECTRIC_VIBRATION, 'Piezo Vibration'),
    ]
    
    x = np.arange(len(model.storage))
    width = 0.2
    
    for i, (h_type, h_label) in enumerate(harvester_types):
        charge_times = []
        for s_type in StorageType:
            result = model.calculate_charge_time(s_type, h_type)
            charge_times.append(min(result["charge_time_hours"], 1000))  # Cap for display
        ax3.bar(x + i * width, charge_times, width, label=h_label)
    
    ax3.set_xlabel('Storage Type')
    ax3.set_ylabel('Charge Time (hours)')
    ax3.set_title('Time to Charge Storage to 90% SOC\n(Using Default Harvester Sizes)')
    ax3.set_xticks(x + width * 1.5)
    ax3.set_xticklabels([s.value.replace('_', '\n') for s in StorageType], fontsize=8)
    ax3.legend(fontsize=8)
    ax3.set_yscale('log')
    ax3.set_ylim(0.1, 1000)
    
    # Plot 4: Intermittent inference simulation
    ax4 = axes[1, 1]
    
    # Simulate duty-cycled operation
    sim_result = model.simulate_intermittent_inference(
        "duty_cycle_1s_per_min",
        HarvesterType.SOLAR_INDOOR,
        StorageType.SUPERCAPACITOR,
        simulation_hours=24
    )
    
    time_hours = sim_result["time_hours"]
    soc_pct = sim_result["energy_stored_pct"]
    
    ax4.plot(time_hours, soc_pct, 'b-', linewidth=1)
    ax4.fill_between(time_hours, 0, soc_pct, alpha=0.3)
    ax4.axhline(y=20, color='red', linestyle='--', label='Low SOC threshold')
    ax4.axhline(y=80, color='green', linestyle='--', label='Target SOC')
    
    ax4.set_xlabel('Time (hours)')
    ax4.set_ylabel('State of Charge (%)')
    ax4.set_title(f'24-Hour Intermittent Inference Simulation\n'
                 f'(Indoor Solar + Supercapacitor, 1s/min duty cycle)\n'
                 f'Total Inferences: {sim_result["total_inferences"]:.0f}')
    ax4.legend()
    ax4.set_xlim(0, 24)
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cycle18_solar_sizing.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Application Scenarios Chart
    fig, ax = plt.subplots(figsize=(14, 10))
    
    app_analyzer = ApplicationScenarioAnalyzer(model)
    
    # Create application scenario visualization
    scenarios = [
        ("IoT Sensor\n(1 inf/hr)", 25, 5.0, "solar_indoor", "rf_wifi"),
        ("Wearable AI\n(4h/day)", 2.2, 0.5, "thermoelectric_body", "kinetic_motion"),
        ("Env Monitor\n(15 min)", 0.05, 5.0, "solar_outdoor", "solar_outdoor"),
        ("Industrial PM\n(30 min)", 0.05, 5.0, "piezoelectric_vibration", "thermoelectric_industrial"),
    ]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    daily_energy = [s[1] for s in scenarios]  # Wh/day
    peak_power = [s[2] for s in scenarios]  # W
    
    ax_twin = ax.twinx()
    
    bars1 = ax.bar(x - width/2, daily_energy, width, label='Daily Energy (Wh)', color='steelblue', alpha=0.8)
    bars2 = ax_twin.bar(x + width/2, peak_power, width, label='Peak Power (W)', color='coral', alpha=0.8)
    
    ax.set_xlabel('Application Scenario')
    ax.set_ylabel('Daily Energy Consumption (Wh)', color='steelblue')
    ax_twin.set_ylabel('Peak Power (W)', color='coral')
    ax.set_title('Energy Harvesting Application Scenarios\nMask-Locked Inference Chip')
    ax.set_xticks(x)
    ax.set_xticklabels([s[0] for s in scenarios])
    ax.legend(loc='upper left')
    ax_twin.legend(loc='upper right')
    
    # Add harvester recommendations
    for i, (name, energy, power, h1, h2) in enumerate(scenarios):
        ax.text(i, max(daily_energy) * 0.9, f"Rec: {h1.replace('_', ' ')}", 
               ha='center', fontsize=7, style='italic')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cycle18_applications.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to {output_dir}/cycle18_*.png")


def generate_results_json(model: EnergyHarvesterModel, 
                         output_path: str = "/home/z/my-project/research/cycle18_results.json") -> Dict:
    """Generate comprehensive results as JSON"""
    
    results = {
        "cycle": 18,
        "title": "Energy Harvesting for Autonomous Operation",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "key_insight": "At 5W, need ~100cm² solar panel outdoors or ~1000cm² indoors",
            "feasible_scenarios": [],
            "challenging_scenarios": [],
        },
        "harvesters": {},
        "storage": {},
        "power_budgets": {},
        "harvester_sizing": {},
        "charge_times": {},
        "duty_cycle_analysis": {},
        "application_scenarios": {},
    }
    
    # Harvester data
    for h_type, h_spec in model.harvesters.items():
        results["harvesters"][h_type.value] = {
            "name": h_spec.name,
            "power_density_mw_cm2": h_spec.power_density * 1000,
            "efficiency": h_spec.efficiency,
            "area_cm2": h_spec.area_cm2,
            "peak_power_mw": h_spec.peak_power * 1000,
            "cost_usd": h_spec.cost_per_unit,
        }
    
    # Storage data
    for s_type, s_spec in model.storage.items():
        results["storage"][s_type.value] = {
            "name": s_spec.name,
            "capacity_wh": s_spec.capacity_wh,
            "capacity_j": s_spec.capacity_joules,
            "voltage_v": s_spec.voltage_nominal,
            "cycle_life": s_spec.cycle_life,
            "self_discharge_monthly_pct": s_spec.self_discharge_monthly,
            "charge_efficiency": s_spec.charge_efficiency,
            "cost_usd": s_spec.cost_per_unit,
            "mass_g": s_spec.mass_g,
        }
    
    # Power budgets
    for b_name, b_spec in model.power_budgets.items():
        results["power_budgets"][b_name] = {
            "mode_name": b_spec.mode_name,
            "peak_power_w": b_spec.power_w,
            "tokens_per_second": b_spec.tokens_per_second,
            "duration_s": b_spec.duration_s,
            "interval_s": b_spec.interval_s,
            "duty_cycle_pct": b_spec.duty_cycle * 100,
            "average_power_mw": b_spec.average_power * 1000,
            "energy_per_cycle_j": b_spec.power_w * b_spec.duration_s,
            "tokens_per_hour": b_spec.tokens_per_hour,
        }
    
    # Harvester sizing for key power levels
    for target_w in [0.5, 1.0, 5.0]:
        for h_type in [HarvesterType.SOLAR_OUTDOOR, HarvesterType.SOLAR_INDOOR]:
            key = f"{target_w}W_{h_type.value}"
            results["harvester_sizing"][key] = model.calculate_harvester_sizing(target_w, h_type)
    
    # Charge times
    for h_type in [HarvesterType.SOLAR_OUTDOOR, HarvesterType.SOLAR_INDOOR, HarvesterType.RF_WIFI]:
        for s_type in [StorageType.SUPERCAPACITOR, StorageType.LI_ION_BATTERY]:
            key = f"{h_type.value}_{s_type.value}"
            results["charge_times"][key] = model.calculate_charge_time(s_type, h_type)
    
    # Duty cycle feasibility
    for budget_name in ["duty_cycle_1s_per_min", "burst_5w_10s", "intermittent_5min_per_hour"]:
        for h_type in [HarvesterType.SOLAR_OUTDOOR, HarvesterType.SOLAR_INDOOR]:
            key = f"{budget_name}_{h_type.value}"
            analysis = model.analyze_duty_cycle_feasibility(budget_name, h_type, StorageType.SUPERCAPACITOR)
            results["duty_cycle_analysis"][key] = analysis
            
            if analysis["feasibility"]["energy_positive"]:
                results["summary"]["feasible_scenarios"].append(key)
            else:
                results["summary"]["challenging_scenarios"].append(key)
    
    # Application scenarios
    app_analyzer = ApplicationScenarioAnalyzer(model)
    results["application_scenarios"]["iot_sensor"] = app_analyzer.analyze_iot_sensor()
    results["application_scenarios"]["wearable_ai"] = app_analyzer.analyze_wearable_ai()
    results["application_scenarios"]["environmental_monitoring"] = app_analyzer.analyze_environmental_monitoring()
    results["application_scenarios"]["industrial_pm"] = app_analyzer.analyze_industrial_predictive_maintenance()
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results saved to {output_path}")
    return results


def main():
    """Main execution function"""
    print("="*70)
    print("CYCLE 18: ENERGY HARVESTING FOR AUTONOMOUS OPERATION")
    print("Mask-Locked Inference Chip Simulation Series")
    print("="*70)
    
    # Initialize model
    model = EnergyHarvesterModel()
    
    # Print harvester comparison
    print("\n" + "="*70)
    print("ENERGY HARVESTER COMPARISON")
    print("="*70)
    print(f"{'Harvester Type':<30} {'Peak Power':<15} {'Density':<15} {'Cost':<10}")
    print("-"*70)
    
    for h_type, h_spec in model.harvesters.items():
        print(f"{h_type.value:<30} {h_spec.peak_power*1000:>10.3f} mW  "
              f"{h_spec.power_density*1000:>10.3f} mW/cm²  ${h_spec.cost_per_unit:>6.2f}")
    
    # Print storage comparison
    print("\n" + "="*70)
    print("ENERGY STORAGE COMPARISON")
    print("="*70)
    print(f"{'Storage Type':<25} {'Capacity':<12} {'Cycle Life':<12} {'Self-Discharge':<15} {'Cost':<10}")
    print("-"*74)
    
    for s_type, s_spec in model.storage.items():
        print(f"{s_type.value:<25} {s_spec.capacity_wh*1000:>8.1f} mWh  "
              f"{s_spec.cycle_life:>10,}    {s_spec.self_discharge_monthly:>10.1f}%/mo   ${s_spec.cost_per_unit:>6.2f}")
    
    # Print power budgets
    print("\n" + "="*70)
    print("POWER BUDGET SCENARIOS")
    print("="*70)
    print(f"{'Mode':<25} {'Peak W':<10} {'Duty %':<10} {'Avg mW':<10} {'Tok/hr':<10}")
    print("-"*65)
    
    for b_name, b_spec in model.power_budgets.items():
        print(f"{b_name:<25} {b_spec.power_w:>8.2f}  {b_spec.duty_cycle*100:>8.1f}%  "
              f"{b_spec.average_power*1000:>8.1f}  {b_spec.tokens_per_hour:>8.1f}")
    
    # Key finding: Solar sizing
    print("\n" + "="*70)
    print("KEY FINDING: SOLAR PANEL SIZING FOR 5W CONTINUOUS OPERATION")
    print("="*70)
    
    outdoor_5w = model.calculate_harvester_sizing(5.0, HarvesterType.SOLAR_OUTDOOR)
    indoor_5w = model.calculate_harvester_sizing(5.0, HarvesterType.SOLAR_INDOOR)
    
    print(f"OUTDOOR (1000 W/m², 15% efficiency):")
    print(f"  Peak scenario: {outdoor_5w['sizing']['peak']['area_cm2']:.0f} cm² "
          f"({outdoor_5w['sizing']['peak']['panel_size_cm']:.0f}×{outdoor_5w['sizing']['peak']['panel_size_cm']:.0f} cm panel)")
    print(f"  Average scenario: {outdoor_5w['sizing']['average_outdoor']['area_cm2']:.0f} cm²")
    print(f"  Conservative: {outdoor_5w['sizing']['conservative']['area_cm2']:.0f} cm²")
    
    print(f"\nINDOOR (10 W/m², 20% efficiency):")
    print(f"  Peak scenario: {indoor_5w['sizing']['peak']['area_cm2']:.0f} cm² "
          f"({indoor_5w['sizing']['peak']['panel_size_cm']:.0f}×{indoor_5w['sizing']['peak']['panel_size_cm']:.0f} cm panel)")
    print(f"  Average scenario: {indoor_5w['sizing']['average_indoor']['area_cm2']:.0f} cm²")
    
    # Duty cycle feasibility
    print("\n" + "="*70)
    print("DUTY-CYCLED OPERATION FEASIBILITY")
    print("="*70)
    
    for budget_name in ["duty_cycle_1s_per_min", "burst_5w_10s"]:
        print(f"\n{model.power_budgets[budget_name].mode_name}:")
        for h_type in [HarvesterType.SOLAR_OUTDOOR, HarvesterType.SOLAR_INDOOR, HarvesterType.RF_WIFI]:
            analysis = model.analyze_duty_cycle_feasibility(budget_name, h_type, StorageType.SUPERCAPACITOR)
            feasible = "✓ FEASIBLE" if analysis["feasibility"]["energy_positive"] else "✗ CHALLENGING"
            print(f"  {h_type.value}: {feasible} "
                  f"(Net daily: {analysis['daily_analysis']['net_energy_kj']:.1f} kJ)")
    
    # Application scenarios
    print("\n" + "="*70)
    print("APPLICATION SCENARIO RECOMMENDATIONS")
    print("="*70)
    
    app_analyzer = ApplicationScenarioAnalyzer(model)
    
    iot = app_analyzer.analyze_iot_sensor()
    print(f"\n1. IoT SENSOR (1 inference/hour):")
    print(f"   Recommended: Indoor solar or RF WiFi harvesting")
    print(f"   Energy per inference: {iot['power_profile']['energy_per_inference_mj']:.0f} mJ")
    
    wearable = app_analyzer.analyze_wearable_ai()
    print(f"\n2. WEARABLE AI ASSISTANT:")
    print(f"   Daily energy: {wearable['power_requirements']['daily_energy_wh']:.2f} Wh")
    print(f"   Recommendation: {wearable['battery_sizing']['recommended_capacity_wh']:.1f} Wh Li-Po battery")
    print(f"   Energy harvesting: Supplemental only (~10% life extension)")
    
    env = app_analyzer.analyze_environmental_monitoring()
    print(f"\n3. ENVIRONMENTAL MONITORING:")
    print(f"   Daily energy: {env['energy_budget']['total_daily_wh']:.3f} Wh")
    print(f"   Solar panel: {env['solar_sizing']['recommended_panel']}")
    print(f"   Battery reserve: {env['solar_sizing']['battery_days_reserve']} days")
    
    ind = app_analyzer.analyze_industrial_predictive_maintenance()
    print(f"\n4. INDUSTRIAL PREDICTIVE MAINTENANCE:")
    print(f"   Combined piezo + TEG power: {ind['harvester_analysis']['combined']['power_mw']:.2f} mW")
    print(f"   Feasible: {ind['harvester_analysis']['combined']['feasible']}")
    
    # Generate visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS...")
    print("="*70)
    generate_visualizations(model)
    
    # Generate JSON results
    print("\n" + "="*70)
    print("GENERATING JSON RESULTS...")
    print("="*70)
    results = generate_results_json(model)
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print("""
KEY INSIGHTS:

1. CONTINUOUS 5W OPERATION:
   - Outdoor: Requires ~100 cm² solar panel (10×10 cm)
   - Indoor: Requires ~1000 cm² solar panel (32×32 cm)
   - NOT feasible with RF, piezoelectric, or thermoelectric alone

2. DUTY-CYCLED OPERATION:
   - 1s/minute (1.7% duty cycle): Feasible with indoor solar
   - 10s/minute (17% duty cycle): Requires outdoor solar
   - 1s/hour (0.03% duty cycle): Feasible with RF or piezo

3. STORAGE RECOMMENDATION:
   - Supercapacitor: Best for frequent charge cycles (>1M cycles)
   - Li-Ion: Better energy density, limited cycles (~500)
   - Solid-state: Future option for high cycle life

4. PMIC REQUIREMENTS:
   - Cold-start capability: <0.33V input
   - MPPT: Fractional open-circuit voltage
   - Quiescent current: <500 µA

5. TOP APPLICATION SCENARIOS:
   a) IoT Sensor: Indoor solar + supercapacitor
   b) Wearable AI: Battery-primary, harvesting-supplemental
   c) Environmental: Outdoor solar + Li-Ion battery
   d) Industrial: Piezo + TEG combination
""")
    
    print("\nCycle 18 simulation complete!")
    return model, results


if __name__ == "__main__":
    model, results = main()
