#!/usr/bin/env python3
"""
C1: Supply Chain Risk Simulation for SuperInstance Mask-Locked Inference Chip
==============================================================================

This simulation models supply chain risks and disruption scenarios using Monte Carlo
methods to quantify risk exposure and optimize mitigation strategies.

Author: Supply Chain Risk Analysis Agent
Date: January 2025
Task ID: 1-c
"""

import numpy as np
import pandas as pd
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# Data Structures and Enums
# =============================================================================

class NodeType(Enum):
    FOUNDRY = "foundry"
    OSAT = "osat"
    MEMORY = "memory"
    SUBSTRATE = "substrate"
    ASSEMBLY = "assembly"
    WAREHOUSE = "warehouse"
    CUSTOMER = "customer"

class DisruptionType(Enum):
    NATURAL_DISASTER = "natural_disaster"
    EQUIPMENT_FAILURE = "equipment_failure"
    CAPACITY_CONSTRAINT = "capacity_constraint"
    SHORTAGE = "shortage"
    GEOPOLITICAL = "geopolitical"
    QUALITY_ISSUE = "quality_issue"
    LOGISTICS_DISRUPTION = "logistics_disruption"

@dataclass
class SupplierNode:
    """Represents a supplier node in the supply chain network"""
    node_id: str
    name: str
    node_type: NodeType
    location: str
    region: str
    capacity: float  # units per month
    lead_time_mean: float  # days
    lead_time_std: float  # days
    unit_cost: float  # USD
    quality_score: float  # 0-1
    geographic_risk: float  # 0-1 (probability of disruption)
    single_source: bool = False
    
    def __post_init__(self):
        self.disruption_history: List[Dict] = []
        self.current_capacity_utilization: float = 0.0
        self.active: bool = True

@dataclass
class SupplyChainEdge:
    """Represents a dependency relationship between nodes"""
    source_id: str
    target_id: str
    dependency_weight: float  # 0-1 (how critical is this connection)
    transport_time_mean: float  # days
    transport_time_std: float
    transport_cost: float  # USD per unit
    logistics_risk: float  # 0-1

@dataclass
class DisruptionScenario:
    """Represents a disruption scenario"""
    scenario_id: str
    disruption_type: DisruptionType
    affected_nodes: List[str]
    probability: float
    duration_mean: float  # days
    duration_std: float
    capacity_impact: float  # 0-1 (fraction of capacity lost)
    cost_impact: float  # USD
    recovery_time_mean: float  # days
    recovery_time_std: float

@dataclass
class InventoryPolicy:
    """(Q, r) inventory policy parameters"""
    reorder_point: float  # r - when to reorder
    order_quantity: float  # Q - how much to order
    safety_stock: float
    service_level: float  # target fill rate
    carrying_cost_rate: float  # annual carrying cost as fraction

@dataclass
class SimulationResult:
    """Results from a single Monte Carlo iteration"""
    iteration: int
    disruption_occurred: bool
    disruption_type: Optional[str]
    affected_nodes: List[str]
    recovery_days: float
    revenue_lost: float
    extra_costs: float
    inventory_shortfall: float
    total_impact: float

# =============================================================================
# Supply Chain Network Model
# =============================================================================

class SupplyChainNetwork:
    """
    Builds and manages the supply chain network model for the SuperInstance chip.
    """
    
    def __init__(self):
        self.nodes: Dict[str, SupplierNode] = {}
        self.edges: List[SupplyChainEdge] = []
        self.adjacency: Dict[str, List[str]] = {}
        self._build_network()
    
    def _build_network(self):
        """Build the supply chain network for mask-locked inference chip"""
        
        # Foundry Nodes (TSMC, GlobalFoundries, Samsung)
        foundries = [
            SupplierNode(
                node_id="TSMC_28nm",
                name="TSMC 28nm HPC+",
                node_type=NodeType.FOUNDRY,
                location="Hsinchu, Taiwan",
                region="Taiwan",
                capacity=50000,  # wafers/month (shared capacity)
                lead_time_mean=126,  # 18 weeks
                lead_time_std=21,
                unit_cost=3000,  # per wafer
                quality_score=0.98,
                geographic_risk=0.08,  # Taiwan geopolitical risk
                single_source=False
            ),
            SupplierNode(
                node_id="GF_22FDX",
                name="GlobalFoundries 22FDX",
                node_type=NodeType.FOUNDRY,
                location="Malta, NY, USA",
                region="US",
                capacity=30000,  # wafers/month
                lead_time_mean=112,  # 16 weeks
                lead_time_std=14,
                unit_cost=2600,  # per wafer (lower cost)
                quality_score=0.95,
                geographic_risk=0.02,
                single_source=False
            ),
            SupplierNode(
                node_id="Samsung_28LPP",
                name="Samsung 28LPP",
                node_type=NodeType.FOUNDRY,
                location="Giheung, South Korea",
                region="Korea",
                capacity=25000,
                lead_time_mean=119,  # 17 weeks
                lead_time_std=17,
                unit_cost=2850,
                quality_score=0.96,
                geographic_risk=0.03,
                single_source=False
            )
        ]
        
        # Memory Suppliers (LPDDR4)
        memory_suppliers = [
            SupplierNode(
                node_id="Micron_LPDDR4",
                name="Micron LPDDR4",
                node_type=NodeType.MEMORY,
                location="Singapore/Taiwan",
                region="APAC",
                capacity=200000,  # units/month
                lead_time_mean=140,  # 20 weeks (allocated)
                lead_time_std=28,
                unit_cost=10.0,  # per 512MB unit
                quality_score=0.97,
                geographic_risk=0.05,
                single_source=False
            ),
            SupplierNode(
                node_id="Samsung_LPDDR4",
                name="Samsung LPDDR4",
                node_type=NodeType.MEMORY,
                location="Hwaseong, Korea",
                region="Korea",
                capacity=150000,
                lead_time_mean=126,
                lead_time_std=21,
                unit_cost=9.50,
                quality_score=0.98,
                geographic_risk=0.03,
                single_source=False
            ),
            SupplierNode(
                node_id="SKHynix_LPDDR4",
                name="SK Hynix LPDDR4",
                node_type=NodeType.MEMORY,
                location="Icheon, Korea",
                region="Korea",
                capacity=80000,  # Limited allocation
                lead_time_mean=154,  # 22 weeks
                lead_time_std=28,
                unit_cost=9.80,
                quality_score=0.96,
                geographic_risk=0.03,
                single_source=False
            )
        ]
        
        # OSAT (Packaging/Assembly)
        osat_suppliers = [
            SupplierNode(
                node_id="ASE_Taiwan",
                name="ASE Group Kaohsiung",
                node_type=NodeType.OSAT,
                location="Kaohsiung, Taiwan",
                region="Taiwan",
                capacity=100000,  # units/month
                lead_time_mean=21,  # 3 weeks
                lead_time_std=7,
                unit_cost=0.12,  # per unit packaging
                quality_score=0.97,
                geographic_risk=0.08,
                single_source=False
            ),
            SupplierNode(
                node_id="Amkor_US",
                name="Amkor Technology Arizona",
                node_type=NodeType.OSAT,
                location="Tempe, AZ, USA",
                region="US",
                capacity=50000,
                lead_time_mean=28,  # 4 weeks
                lead_time_std=7,
                unit_cost=0.15,  # +15-20% premium
                quality_score=0.95,
                geographic_risk=0.02,
                single_source=False
            )
        ]
        
        # Substrate Suppliers
        substrate_suppliers = [
            SupplierNode(
                node_id="Ibiden_Substrate",
                name="Ibiden Package Substrate",
                node_type=NodeType.SUBSTRATE,
                location="Ogaki, Japan",
                region="Japan",
                capacity=80000,
                lead_time_mean=42,  # 6 weeks
                lead_time_std=14,
                unit_cost=0.50,
                quality_score=0.97,
                geographic_risk=0.04,
                single_source=False
            ),
            SupplierNode(
                node_id="Unimicron_Substrate",
                name="Unimicron Substrate",
                node_type=NodeType.SUBSTRATE,
                location="Taoyuan, Taiwan",
                region="Taiwan",
                capacity=60000,
                lead_time_mean=35,
                lead_time_std=10,
                unit_cost=0.45,
                quality_score=0.95,
                geographic_risk=0.08,
                single_source=False
            )
        ]
        
        # Assembly/Warehouse
        assembly_nodes = [
            SupplierNode(
                node_id="Final_Assembly",
                name="Final Assembly & Test",
                node_type=NodeType.ASSEMBLY,
                location="Shenzhen, China",
                region="China",
                capacity=150000,
                lead_time_mean=14,
                lead_time_std=3,
                unit_cost=0.30,
                quality_score=0.94,
                geographic_risk=0.06,
                single_source=False
            )
        ]
        
        # Add all nodes
        all_nodes = foundries + memory_suppliers + osat_suppliers + substrate_suppliers + assembly_nodes
        for node in all_nodes:
            self.nodes[node.node_id] = node
        
        # Build edges (dependencies)
        self._build_edges(foundries, memory_suppliers, osat_suppliers, substrate_suppliers)
    
    def _build_edges(self, foundries, memory_suppliers, osat_suppliers, substrate_suppliers):
        """Build dependency edges between nodes"""
        
        # Foundry -> OSAT dependencies
        for foundry in foundries:
            for osat in osat_suppliers:
                self.edges.append(SupplyChainEdge(
                    source_id=foundry.node_id,
                    target_id=osat.node_id,
                    dependency_weight=0.9,  # Critical dependency
                    transport_time_mean=7 if "Taiwan" in foundry.location else 14,
                    transport_time_std=2,
                    transport_cost=0.05,
                    logistics_risk=0.03
                ))
        
        # Memory -> OSAT dependencies
        for memory in memory_suppliers:
            for osat in osat_suppliers:
                self.edges.append(SupplyChainEdge(
                    source_id=memory.node_id,
                    target_id=osat.node_id,
                    dependency_weight=0.85,
                    transport_time_mean=5 if osat.node_id == "ASE_Taiwan" else 10,
                    transport_time_std=2,
                    transport_cost=0.02,
                    logistics_risk=0.02
                ))
        
        # Substrate -> OSAT dependencies
        for substrate in [self.nodes["Ibiden_Substrate"], self.nodes["Unimicron_Substrate"]]:
            for osat in osat_suppliers:
                self.edges.append(SupplyChainEdge(
                    source_id=substrate.node_id,
                    target_id=osat.node_id,
                    dependency_weight=0.7,
                    transport_time_mean=7,
                    transport_time_std=2,
                    transport_cost=0.01,
                    logistics_risk=0.02
                ))
        
        # OSAT -> Final Assembly
        for osat in osat_suppliers:
            self.edges.append(SupplyChainEdge(
                source_id=osat.node_id,
                target_id="Final_Assembly",
                dependency_weight=0.95,
                transport_time_mean=10,
                transport_time_std=3,
                transport_cost=0.03,
                logistics_risk=0.04
            ))
        
        # Build adjacency list
        for edge in self.edges:
            if edge.source_id not in self.adjacency:
                self.adjacency[edge.source_id] = []
            self.adjacency[edge.source_id].append(edge.target_id)
    
    def get_single_source_nodes(self) -> List[SupplierNode]:
        """Identify single-point-of-failure nodes"""
        # In reality, check which nodes have no alternatives
        single_source = []
        
        # TSMC has highest concentration risk
        if self.nodes["TSMC_28nm"].geographic_risk > 0.05:
            single_source.append(self.nodes["TSMC_28nm"])
        
        # LPDDR4 is allocated/shortage - treat as quasi-single-source
        for node_id in ["Micron_LPDDR4", "Samsung_LPDDR4"]:
            node = self.nodes[node_id]
            if node.lead_time_mean > 120:  # Long lead time indicates allocation
                single_source.append(node)
        
        return single_source
    
    def get_critical_path(self) -> List[str]:
        """Identify the critical path through the supply chain"""
        # Critical path: Foundry -> OSAT -> Assembly
        return ["TSMC_28nm", "ASE_Taiwan", "Final_Assembly"]

# =============================================================================
# Disruption Scenarios
# =============================================================================

class DisruptionScenarioGenerator:
    """Generates disruption scenarios based on historical data and risk analysis"""
    
    def __init__(self, network: SupplyChainNetwork):
        self.network = network
        self.scenarios = self._generate_scenarios()
    
    def _generate_scenarios(self) -> List[DisruptionScenario]:
        """Generate comprehensive disruption scenarios"""
        scenarios = []
        
        # Fab Outage Scenarios
        scenarios.extend([
            # Natural Disaster - Taiwan Earthquake
            DisruptionScenario(
                scenario_id="FAB_ND_001",
                disruption_type=DisruptionType.NATURAL_DISASTER,
                affected_nodes=["TSMC_28nm", "ASE_Taiwan", "Unimicron_Substrate"],
                probability=0.02,  # 2% annual probability
                duration_mean=30,  # 30 days
                duration_std=15,
                capacity_impact=0.8,  # 80% capacity loss
                cost_impact=5000000,  # $5M emergency costs
                recovery_time_mean=90,  # 90 days to full recovery
                recovery_time_std=30
            ),
            # Equipment Failure - TSMC
            DisruptionScenario(
                scenario_id="FAB_EF_001",
                disruption_type=DisruptionType.EQUIPMENT_FAILURE,
                affected_nodes=["TSMC_28nm"],
                probability=0.05,
                duration_mean=14,
                duration_std=7,
                capacity_impact=0.3,
                cost_impact=500000,
                recovery_time_mean=21,
                recovery_time_std=7
            ),
            # Equipment Failure - GlobalFoundries
            DisruptionScenario(
                scenario_id="FAB_EF_002",
                disruption_type=DisruptionType.EQUIPMENT_FAILURE,
                affected_nodes=["GF_22FDX"],
                probability=0.04,
                duration_mean=10,
                duration_std=5,
                capacity_impact=0.25,
                cost_impact=300000,
                recovery_time_mean=14,
                recovery_time_std=5
            ),
        ])
        
        # Geopolitical Disruptions
        scenarios.extend([
            # Taiwan Blockade Scenario
            DisruptionScenario(
                scenario_id="GEO_001",
                disruption_type=DisruptionType.GEOPOLITICAL,
                affected_nodes=["TSMC_28nm", "ASE_Taiwan", "Unimicron_Substrate"],
                probability=0.01,  # 1% 5-year probability
                duration_mean=60,
                duration_std=30,
                capacity_impact=1.0,  # Complete loss
                cost_impact=20000000,  # $20M
                recovery_time_mean=180,
                recovery_time_std=60
            ),
            # Export Controls
            DisruptionScenario(
                scenario_id="GEO_002",
                disruption_type=DisruptionType.GEOPOLITICAL,
                affected_nodes=["Samsung_28LPP", "Samsung_LPDDR4", "SKHynix_LPDDR4"],
                probability=0.03,
                duration_mean=30,
                duration_std=14,
                capacity_impact=0.5,
                cost_impact=2000000,
                recovery_time_mean=60,
                recovery_time_std=21
            ),
        ])
        
        # Memory Shortage Scenarios
        scenarios.extend([
            # LPDDR4 Allocation Crisis
            DisruptionScenario(
                scenario_id="MEM_001",
                disruption_type=DisruptionType.SHORTAGE,
                affected_nodes=["Micron_LPDDR4", "Samsung_LPDDR4", "SKHynix_LPDDR4"],
                probability=0.15,  # High probability
                duration_mean=45,
                duration_std=20,
                capacity_impact=0.4,
                cost_impact=1500000,  # Premium pricing
                recovery_time_mean=60,
                recovery_time_std=21
            ),
            # Single Supplier Memory Disruption
            DisruptionScenario(
                scenario_id="MEM_002",
                disruption_type=DisruptionType.EQUIPMENT_FAILURE,
                affected_nodes=["Micron_LPDDR4"],
                probability=0.08,
                duration_mean=21,
                duration_std=10,
                capacity_impact=0.6,
                cost_impact=800000,
                recovery_time_mean=35,
                recovery_time_std=14
            ),
        ])
        
        # OSAT Capacity Constraints
        scenarios.extend([
            # ASE Capacity Constraint
            DisruptionScenario(
                scenario_id="OSAT_001",
                disruption_type=DisruptionType.CAPACITY_CONSTRAINT,
                affected_nodes=["ASE_Taiwan"],
                probability=0.12,
                duration_mean=14,
                duration_std=7,
                capacity_impact=0.3,
                cost_impact=200000,
                recovery_time_mean=21,
                recovery_time_std=7
            ),
            # Amkor Quality Issue
            DisruptionScenario(
                scenario_id="OSAT_002",
                disruption_type=DisruptionType.QUALITY_ISSUE,
                affected_nodes=["Amkor_US"],
                probability=0.06,
                duration_mean=10,
                duration_std=5,
                capacity_impact=0.2,
                cost_impact=150000,
                recovery_time_mean=14,
                recovery_time_std=5
            ),
        ])
        
        # Substrate Shortage
        scenarios.append(
            DisruptionScenario(
                scenario_id="SUB_001",
                disruption_type=DisruptionType.SHORTAGE,
                affected_nodes=["Ibiden_Substrate", "Unimicron_Substrate"],
                probability=0.10,
                duration_mean=28,
                duration_std=14,
                capacity_impact=0.35,
                cost_impact=400000,
                recovery_time_mean=42,
                recovery_time_std=14
            )
        )
        
        # Logistics Disruption
        scenarios.append(
            DisruptionScenario(
                scenario_id="LOG_001",
                disruption_type=DisruptionType.LOGISTICS_DISRUPTION,
                affected_nodes=["Final_Assembly"],
                probability=0.08,
                duration_mean=10,
                duration_std=5,
                capacity_impact=0.25,
                cost_impact=250000,
                recovery_time_mean=14,
                recovery_time_std=5
            )
        )
        
        return scenarios
    
    def get_annual_probability_scenarios(self) -> Dict[str, float]:
        """Calculate annual probability of each scenario type"""
        prob_by_type = {}
        for scenario in self.scenarios:
            dtype = scenario.disruption_type.value
            if dtype not in prob_by_type:
                prob_by_type[dtype] = 0
            prob_by_type[dtype] += scenario.probability
        return prob_by_type

# =============================================================================
# Monte Carlo Simulation
# =============================================================================

class MonteCarloSimulator:
    """Monte Carlo simulation for supply chain risk quantification"""
    
    def __init__(self, network: SupplyChainNetwork, scenarios: List[DisruptionScenario],
                 n_iterations: int = 10000):
        self.network = network
        self.scenarios = scenarios
        self.n_iterations = n_iterations
        self.results: List[SimulationResult] = []
        
        # Business parameters
        self.monthly_demand = 10000  # units
        self.unit_revenue = 79  # USD (Standard product)
        self.monthly_revenue = self.monthly_demand * self.unit_revenue
        self.cogs_per_unit = 34.44  # USD
    
    def run_simulation(self) -> List[SimulationResult]:
        """Run Monte Carlo simulation"""
        print(f"Running {self.n_iterations} Monte Carlo iterations...")
        
        self.results = []
        
        for i in range(self.n_iterations):
            result = self._run_single_iteration(i)
            self.results.append(result)
        
        return self.results
    
    def _run_single_iteration(self, iteration: int) -> SimulationResult:
        """Run a single simulation iteration"""
        
        disruption_occurred = False
        disruption_type = None
        affected_nodes = []
        recovery_days = 0
        revenue_lost = 0
        extra_costs = 0
        inventory_shortfall = 0
        
        # Check each scenario
        for scenario in self.scenarios:
            if np.random.random() < scenario.probability:
                disruption_occurred = True
                disruption_type = scenario.disruption_type.value
                
                # Sample duration from lognormal distribution
                duration = np.random.lognormal(
                    mean=np.log(scenario.duration_mean),
                    sigma=0.3
                )
                duration = max(1, duration)  # At least 1 day
                
                # Sample recovery time
                recovery = np.random.lognormal(
                    mean=np.log(scenario.recovery_time_mean),
                    sigma=0.3
                )
                recovery = max(duration, recovery)
                
                # Calculate impact
                capacity_loss = scenario.capacity_impact * np.random.uniform(0.7, 1.0)
                
                # Revenue lost (based on duration and capacity loss)
                daily_revenue = self.monthly_revenue / 30
                revenue_impact = daily_revenue * duration * capacity_loss
                revenue_lost += revenue_impact
                
                # Extra costs
                cost_impact = scenario.cost_impact * np.random.uniform(0.5, 1.5)
                extra_costs += cost_impact
                
                # Recovery time
                recovery_days = max(recovery_days, recovery)
                
                # Affected nodes
                affected_nodes.extend(scenario.affected_nodes)
        
        # Remove duplicates
        affected_nodes = list(set(affected_nodes))
        
        total_impact = revenue_lost + extra_costs
        
        return SimulationResult(
            iteration=iteration,
            disruption_occurred=disruption_occurred,
            disruption_type=disruption_type,
            affected_nodes=affected_nodes,
            recovery_days=recovery_days,
            revenue_lost=revenue_lost,
            extra_costs=extra_costs,
            inventory_shortfall=inventory_shortfall,
            total_impact=total_impact
        )
    
    def calculate_risk_metrics(self) -> Dict:
        """Calculate risk metrics from simulation results"""
        
        total_impacts = [r.total_impact for r in self.results]
        disruptions = [r for r in self.results if r.disruption_occurred]
        
        # Expected Value at Risk (EVaR)
        var_95 = np.percentile(total_impacts, 95)
        var_99 = np.percentile(total_impacts, 99)
        
        # Expected Shortfall (Conditional VaR)
        es_95 = np.mean([x for x in total_impacts if x >= var_95])
        es_99 = np.mean([x for x in total_impacts if x >= var_99])
        
        # Annual disruption probability
        disruption_prob = len(disruptions) / self.n_iterations
        
        # Expected annual loss
        expected_annual_loss = np.mean(total_impacts)
        
        # Recovery time statistics
        recovery_times = [r.recovery_days for r in disruptions] if disruptions else [0]
        mean_recovery = np.mean(recovery_times)
        max_recovery = np.max(recovery_times) if recovery_times else 0
        
        # Impact by disruption type
        impact_by_type = {}
        for r in disruptions:
            dtype = r.disruption_type or "none"
            if dtype not in impact_by_type:
                impact_by_type[dtype] = []
            impact_by_type[dtype].append(r.total_impact)
        
        impact_by_type_stats = {
            k: {"count": len(v), "mean_impact": np.mean(v), "total_impact": sum(v)}
            for k, v in impact_by_type.items()
        }
        
        return {
            "expected_annual_loss": expected_annual_loss,
            "var_95": var_95,
            "var_99": var_99,
            "expected_shortfall_95": es_95,
            "expected_shortfall_99": es_99,
            "disruption_probability": disruption_prob,
            "mean_recovery_days": mean_recovery,
            "max_recovery_days": max_recovery,
            "impact_by_disruption_type": impact_by_type_stats,
            "percentile_50": np.percentile(total_impacts, 50),
            "percentile_75": np.percentile(total_impacts, 75),
            "percentile_90": np.percentile(total_impacts, 90),
            "max_impact": max(total_impacts),
            "min_impact": min(total_impacts)
        }

# =============================================================================
# Inventory Optimization (Q, r) Model
# =============================================================================

class InventoryOptimizer:
    """Optimize inventory policy using (Q, r) continuous review model"""
    
    def __init__(self, network: SupplyChainNetwork, demand_mean: float = 10000,
                 demand_std: float = 2000, carrying_cost_rate: float = 0.20):
        self.network = network
        self.demand_mean = demand_mean  # monthly demand
        self.demand_std = demand_std
        self.carrying_cost_rate = carrying_cost_rate  # 20% annually
        self.setup_cost = 5000  # Order setup cost
        self.stockout_cost = 50  # Cost per unit stockout
    
    def optimize(self, service_level: float = 0.95) -> InventoryPolicy:
        """
        Optimize (Q, r) inventory policy
        
        Q = Order quantity (EOQ)
        r = Reorder point
        
        For supply chain risk, we need higher safety stock than standard EOQ.
        """
        
        # Convert to daily demand
        daily_demand = self.demand_mean / 30
        daily_demand_std = self.demand_std / 30
        
        # Lead time (weighted average across suppliers)
        lead_times = []
        for node in self.network.nodes.values():
            if node.node_type in [NodeType.FOUNDRY, NodeType.MEMORY]:
                lead_times.append(node.lead_time_mean)
        
        avg_lead_time = np.mean(lead_times) if lead_times else 120  # days
        lead_time_std = 14  # Standard deviation of lead time
        
        # Calculate EOQ
        # Q* = sqrt(2 * D * S / H)
        # where D = annual demand, S = setup cost, H = holding cost per unit
        
        annual_demand = self.demand_mean * 12
        unit_cost = 34.44  # COGS
        holding_cost = unit_cost * self.carrying_cost_rate
        
        Q = np.sqrt(2 * annual_demand * self.setup_cost / holding_cost)
        
        # Safety stock calculation
        # SS = z * sqrt(L * σd² + d² * σL²)
        # where z = service factor, L = lead time, σd = demand std, d = avg demand, σL = lead time std
        
        z = self._get_z_score(service_level)
        safety_stock = z * np.sqrt(
            avg_lead_time * (daily_demand_std ** 2) +
            (daily_demand ** 2) * (lead_time_std ** 2)
        )
        
        # Reorder point
        # r = d * L + SS
        r = daily_demand * avg_lead_time + safety_stock
        
        # Adjust for supply chain risk (increase safety stock)
        # Calculate weighted risk factor
        risk_factor = self._calculate_risk_factor()
        adjusted_safety_stock = safety_stock * (1 + risk_factor)
        r_adjusted = daily_demand * avg_lead_time + adjusted_safety_stock
        
        return InventoryPolicy(
            reorder_point=r_adjusted,
            order_quantity=Q,
            safety_stock=adjusted_safety_stock,
            service_level=service_level,
            carrying_cost_rate=self.carrying_cost_rate
        )
    
    def _get_z_score(self, service_level: float) -> float:
        """Get z-score for service level"""
        from scipy import stats
        return stats.norm.ppf(service_level)
    
    def _calculate_risk_factor(self) -> float:
        """Calculate supply chain risk adjustment factor"""
        # Weighted risk based on supplier geographic risk
        total_risk = 0
        total_weight = 0
        
        for node in self.network.nodes.values():
            weight = node.capacity * node.unit_cost
            total_risk += node.geographic_risk * weight
            total_weight += weight
        
        avg_risk = total_risk / total_weight if total_weight > 0 else 0.1
        
        # Convert to adjustment factor (0-1 range)
        return min(1.0, avg_risk * 5)
    
    def calculate_inventory_cost(self, policy: InventoryPolicy) -> Dict:
        """Calculate total inventory costs"""
        
        unit_cost = 34.44
        annual_demand = self.demand_mean * 12
        
        # Annual ordering cost
        orders_per_year = annual_demand / policy.order_quantity
        ordering_cost = orders_per_year * self.setup_cost
        
        # Annual holding cost
        avg_inventory = policy.order_quantity / 2 + policy.safety_stock
        holding_cost = avg_inventory * unit_cost * policy.carrying_cost_rate
        
        # Safety stock cost
        safety_stock_cost = policy.safety_stock * unit_cost * policy.carrying_cost_rate
        
        total_cost = ordering_cost + holding_cost
        
        # As percentage of revenue
        annual_revenue = annual_demand * 79
        cost_pct = (total_cost / annual_revenue) * 100
        
        return {
            "annual_ordering_cost": ordering_cost,
            "annual_holding_cost": holding_cost,
            "safety_stock_cost": safety_stock_cost,
            "total_inventory_cost": total_cost,
            "avg_inventory_units": avg_inventory,
            "orders_per_year": orders_per_year,
            "cost_as_pct_of_revenue": cost_pct
        }

# =============================================================================
# Mitigation Strategies
# =============================================================================

class MitigationStrategyOptimizer:
    """Design and optimize supply chain mitigation strategies"""
    
    def __init__(self, network: SupplyChainNetwork, scenarios: List[DisruptionScenario],
                 risk_metrics: Dict):
        self.network = network
        self.scenarios = scenarios
        self.risk_metrics = risk_metrics
    
    def analyze_dual_sourcing(self) -> Dict:
        """Analyze dual sourcing strategy benefits"""
        
        # Identify single-source risks
        single_source = self.network.get_single_source_nodes()
        
        strategies = []
        
        # TSMC -> GF 22FDX dual sourcing
        strategies.append({
            "component": "Foundry (Wafers)",
            "primary": "TSMC 28nm",
            "secondary": "GlobalFoundries 22FDX",
            "qualification_cost": 150000,  # $150K to qualify second source
            "annual_savings": self.risk_metrics["expected_annual_loss"] * 0.3,
            "implementation_time": "6-12 months",
            "risk_reduction": 0.4,  # 40% reduction in foundry-related risk
            "roi_months": 18
        })
        
        # Memory dual sourcing
        strategies.append({
            "component": "LPDDR4 Memory",
            "primary": "Micron",
            "secondary": "Samsung + SK Hynix",
            "qualification_cost": 75000,  # $75K to qualify additional sources
            "annual_savings": self.risk_metrics["expected_annual_loss"] * 0.2,
            "implementation_time": "3-6 months",
            "risk_reduction": 0.25,
            "roi_months": 12
        })
        
        # OSAT dual sourcing
        strategies.append({
            "component": "Packaging (OSAT)",
            "primary": "ASE Taiwan",
            "secondary": "Amkor US",
            "qualification_cost": 50000,
            "annual_savings": self.risk_metrics["expected_annual_loss"] * 0.15,
            "implementation_time": "3-6 months",
            "risk_reduction": 0.2,
            "roi_months": 8
        })
        
        return {
            "strategies": strategies,
            "total_qualification_cost": sum(s["qualification_cost"] for s in strategies),
            "total_risk_reduction": sum(s["risk_reduction"] for s in strategies) / len(strategies)
        }
    
    def analyze_geographic_diversification(self) -> Dict:
        """Analyze geographic diversification strategy"""
        
        current_exposure = {
            "Taiwan": 0.0,
            "Korea": 0.0,
            "US": 0.0,
            "Japan": 0.0,
            "China": 0.0
        }
        
        # Calculate current exposure by region
        total_weight = 0
        for node in self.network.nodes.values():
            weight = node.capacity
            total_weight += weight
            
            if node.region == "Taiwan":
                current_exposure["Taiwan"] += weight
            elif node.region == "Korea":
                current_exposure["Korea"] += weight
            elif node.region == "US":
                current_exposure["US"] += weight
            elif node.region == "Japan":
                current_exposure["Japan"] += weight
            elif node.region == "China":
                current_exposure["China"] += weight
        
        # Convert to percentages
        for region in current_exposure:
            current_exposure[region] = (current_exposure[region] / total_weight) * 100
        
        # Target diversified exposure
        target_exposure = {
            "Taiwan": 25,  # Reduce from ~40% to 25%
            "Korea": 20,
            "US": 30,  # Increase US presence
            "Japan": 15,
            "China": 10
        }
        
        # Recommendations
        recommendations = [
            {
                "action": "Primary Foundry Switch to GlobalFoundries",
                "current_region": "Taiwan",
                "target_region": "US",
                "cost": 2500000,  # Mask set + qualification
                "risk_reduction": 0.35,
                "timeline": "12-18 months"
            },
            {
                "action": "Add Amkor as Secondary OSAT",
                "current_region": "Taiwan",
                "target_region": "US",
                "cost": 50000,
                "risk_reduction": 0.15,
                "timeline": "3-6 months"
            },
            {
                "action": "Qualify Ibiden as Primary Substrate",
                "current_region": "Taiwan",
                "target_region": "Japan",
                "cost": 30000,
                "risk_reduction": 0.1,
                "timeline": "3 months"
            }
        ]
        
        return {
            "current_exposure": current_exposure,
            "target_exposure": target_exposure,
            "recommendations": recommendations,
            "geopolitical_risk_score": current_exposure["Taiwan"] * 0.08 + 
                                        current_exposure["Korea"] * 0.03 +
                                        current_exposure["China"] * 0.06
        }
    
    def optimize_safety_stock(self) -> Dict:
        """Optimize safety stock levels by component"""
        
        components = {
            "LPDDR4 Memory": {
                "unit_cost": 10.0,
                "lead_time_days": 140,
                "lead_time_var": 0.2,
                "criticality": 0.9,
                "current_stock_months": 1
            },
            "Wafers (WIP)": {
                "unit_cost": 3000,
                "lead_time_days": 126,
                "lead_time_var": 0.15,
                "criticality": 0.95,
                "current_stock_months": 0.5
            },
            "Package Substrate": {
                "unit_cost": 0.50,
                "lead_time_days": 42,
                "lead_time_var": 0.3,
                "criticality": 0.7,
                "current_stock_months": 1
            },
            "Finished Goods": {
                "unit_cost": 34.44,
                "lead_time_days": 0,
                "lead_time_var": 0,
                "criticality": 1.0,
                "current_stock_months": 1
            }
        }
        
        recommendations = []
        monthly_demand = 10000
        
        for component, params in components.items():
            # Optimal safety stock = z * σ_demand * sqrt(L) * criticality
            daily_demand = monthly_demand / 30
            demand_std = daily_demand * 0.2  # 20% demand variability
            
            z = 1.65  # 95% service level
            lead_time = params["lead_time_days"] / 30  # Convert to months
            
            optimal_stock_months = z * 0.2 * np.sqrt(lead_time) * params["criticality"] + 1
            optimal_stock_months = min(6, optimal_stock_months)  # Cap at 6 months
            
            stock_value = optimal_stock_months * monthly_demand * params["unit_cost"]
            carrying_cost = stock_value * 0.20  # 20% annual carrying cost
            
            recommendations.append({
                "component": component,
                "current_stock_months": params["current_stock_months"],
                "recommended_stock_months": round(optimal_stock_months, 1),
                "stock_value_usd": round(stock_value, 2),
                "annual_carrying_cost": round(carrying_cost, 2),
                "risk_reduction": params["criticality"] * 0.3
            })
        
        total_value = sum(r["stock_value_usd"] for r in recommendations)
        total_carrying = sum(r["annual_carrying_cost"] for r in recommendations)
        
        return {
            "recommendations": recommendations,
            "total_inventory_value": total_value,
            "total_annual_carrying_cost": total_carrying,
            "carrying_cost_pct_of_cogs": (total_carrying / (monthly_demand * 12 * 34.44)) * 100
        }
    
    def calculate_mitigation_roi(self) -> Dict:
        """Calculate ROI for all mitigation strategies"""
        
        baseline_loss = self.risk_metrics["expected_annual_loss"]
        
        strategies = [
            {
                "name": "Dual Sourcing - Foundry",
                "investment": 150000,
                "risk_reduction_pct": 0.4,
                "ongoing_cost": 25000,  # Annual
                "implementation_months": 12
            },
            {
                "name": "Dual Sourcing - Memory",
                "investment": 75000,
                "risk_reduction_pct": 0.25,
                "ongoing_cost": 10000,
                "implementation_months": 6
            },
            {
                "name": "Geographic Diversification",
                "investment": 500000,
                "risk_reduction_pct": 0.35,
                "ongoing_cost": 50000,
                "implementation_months": 18
            },
            {
                "name": "Increased Safety Stock",
                "investment": 200000,
                "risk_reduction_pct": 0.2,
                "ongoing_cost": 40000,  # Carrying cost
                "implementation_months": 1
            },
            {
                "name": "Supply Chain Insurance",
                "investment": 0,
                "risk_reduction_pct": 0.15,  # Transfer, not reduce
                "ongoing_cost": 75000,
                "implementation_months": 1
            }
        ]
        
        roi_analysis = []
        
        for s in strategies:
            risk_reduction = baseline_loss * s["risk_reduction_pct"]
            net_benefit = risk_reduction - s["ongoing_cost"]
            
            if s["investment"] > 0:
                payback_months = s["investment"] / (net_benefit / 12) if net_benefit > 0 else float('inf')
                roi = (net_benefit / s["investment"]) * 100 if s["investment"] > 0 else 0
            else:
                payback_months = 0
                roi = float('inf') if net_benefit > 0 else 0
            
            roi_analysis.append({
                "strategy": s["name"],
                "investment": s["investment"],
                "annual_risk_reduction": risk_reduction,
                "ongoing_annual_cost": s["ongoing_cost"],
                "net_annual_benefit": net_benefit,
                "payback_months": round(payback_months, 1) if payback_months != float('inf') else "N/A",
                "roi_pct": round(roi, 1) if roi != float('inf') else "N/A",
                "implementation_months": s["implementation_months"]
            })
        
        return {
            "strategies": roi_analysis,
            "total_investment": sum(s["investment"] for s in strategies),
            "total_annual_risk_reduction": sum(s["annual_risk_reduction"] for s in roi_analysis),
            "recommended_priorities": sorted(roi_analysis, key=lambda x: x["net_annual_benefit"], reverse=True)[:3]
        }

# =============================================================================
# Main Simulation Runner
# =============================================================================

def run_supply_chain_simulation(n_iterations: int = 10000) -> Dict:
    """Run complete supply chain risk simulation"""
    
    print("=" * 70)
    print("C1: Supply Chain Risk Simulation for SuperInstance Mask-Locked Chip")
    print("=" * 70)
    
    # 1. Build Supply Chain Network
    print("\n[1/6] Building Supply Chain Network Model...")
    network = SupplyChainNetwork()
    print(f"  - Nodes: {len(network.nodes)}")
    print(f"  - Edges: {len(network.edges)}")
    print(f"  - Critical Path: {' -> '.join(network.get_critical_path())}")
    
    # 2. Generate Disruption Scenarios
    print("\n[2/6] Generating Disruption Scenarios...")
    scenario_gen = DisruptionScenarioGenerator(network)
    scenarios = scenario_gen.scenarios
    print(f"  - Total Scenarios: {len(scenarios)}")
    prob_by_type = scenario_gen.get_annual_probability_scenarios()
    for dtype, prob in prob_by_type.items():
        print(f"    - {dtype}: {prob*100:.1f}% annual probability")
    
    # 3. Run Monte Carlo Simulation
    print("\n[3/6] Running Monte Carlo Simulation...")
    simulator = MonteCarloSimulator(network, scenarios, n_iterations)
    results = simulator.run_simulation()
    risk_metrics = simulator.calculate_risk_metrics()
    
    print(f"  - Expected Annual Loss: ${risk_metrics['expected_annual_loss']:,.2f}")
    print(f"  - VaR (95%): ${risk_metrics['var_95']:,.2f}")
    print(f"  - VaR (99%): ${risk_metrics['var_99']:,.2f}")
    print(f"  - Disruption Probability: {risk_metrics['disruption_probability']*100:.1f}%")
    print(f"  - Mean Recovery Time: {risk_metrics['mean_recovery_days']:.1f} days")
    
    # 4. Optimize Inventory Policy
    print("\n[4/6] Optimizing Inventory Policy (Q, r) Model...")
    inventory_opt = InventoryOptimizer(network)
    optimal_policy = inventory_opt.optimize(service_level=0.95)
    inventory_costs = inventory_opt.calculate_inventory_cost(optimal_policy)
    
    print(f"  - Optimal Order Quantity (Q): {optimal_policy.order_quantity:.0f} units")
    print(f"  - Reorder Point (r): {optimal_policy.reorder_point:.0f} units")
    print(f"  - Safety Stock: {optimal_policy.safety_stock:.0f} units")
    print(f"  - Annual Inventory Cost: ${inventory_costs['total_inventory_cost']:,.2f}")
    print(f"  - Cost as % of Revenue: {inventory_costs['cost_as_pct_of_revenue']:.2f}%")
    
    # 5. Design Mitigation Strategies
    print("\n[5/6] Analyzing Mitigation Strategies...")
    mitigation_opt = MitigationStrategyOptimizer(network, scenarios, risk_metrics)
    
    dual_sourcing = mitigation_opt.analyze_dual_sourcing()
    geo_diversification = mitigation_opt.analyze_geographic_diversification()
    safety_stock = mitigation_opt.optimize_safety_stock()
    roi_analysis = mitigation_opt.calculate_mitigation_roi()
    
    print(f"  - Dual Sourcing Total Investment: ${dual_sourcing['total_qualification_cost']:,.2f}")
    print(f"  - Geographic Risk Score: {geo_diversification['geopolitical_risk_score']:.2f}")
    print(f"  - Total Safety Stock Value: ${safety_stock['total_inventory_value']:,.2f}")
    
    # 6. Success Criteria Check
    print("\n[6/6] Checking Success Criteria...")
    
    # Check for single-point failures
    single_source_nodes = network.get_single_source_nodes()
    spf_status = "PASS" if len(single_source_nodes) == 0 else "FAIL"
    print(f"  - Single-Point Failures: {len(single_source_nodes)} nodes ({spf_status})")
    
    # Check recovery time
    recovery_status = "PASS" if risk_metrics['mean_recovery_days'] <= 14 else "FAIL"
    print(f"  - Recovery Time < 2 weeks: {risk_metrics['mean_recovery_days']:.1f} days ({recovery_status})")
    
    # Check inventory cost
    inv_status = "PASS" if inventory_costs['cost_as_pct_of_revenue'] < 5 else "FAIL"
    print(f"  - Inventory Cost < 5% Revenue: {inventory_costs['cost_as_pct_of_revenue']:.2f}% ({inv_status})")
    
    # Compile Final Results
    results_summary = {
        "simulation_metadata": {
            "n_iterations": n_iterations,
            "random_seed": 42,
            "timestamp": "2025-01-15"
        },
        "supply_chain_network": {
            "total_nodes": len(network.nodes),
            "total_edges": len(network.edges),
            "nodes_by_type": {
                nt.value: len([n for n in network.nodes.values() if n.node_type == nt])
                for nt in NodeType
            },
            "critical_path": network.get_critical_path(),
            "single_source_nodes": [n.node_id for n in single_source_nodes]
        },
        "disruption_scenarios": {
            "total_scenarios": len(scenarios),
            "scenarios_by_type": prob_by_type,
            "high_probability_scenarios": [
                {
                    "id": s.scenario_id,
                    "type": s.disruption_type.value,
                    "probability": s.probability,
                    "affected_nodes": s.affected_nodes
                }
                for s in sorted(scenarios, key=lambda x: x.probability, reverse=True)[:5]
            ]
        },
        "risk_metrics": risk_metrics,
        "inventory_policy": {
            "order_quantity": optimal_policy.order_quantity,
            "reorder_point": optimal_policy.reorder_point,
            "safety_stock": optimal_policy.safety_stock,
            "service_level": optimal_policy.service_level,
            "carrying_cost_rate": optimal_policy.carrying_cost_rate
        },
        "inventory_costs": inventory_costs,
        "mitigation_strategies": {
            "dual_sourcing": dual_sourcing,
            "geographic_diversification": geo_diversification,
            "safety_stock_optimization": safety_stock,
            "roi_analysis": roi_analysis
        },
        "success_criteria": {
            "no_single_point_failures": {
                "status": spf_status,
                "details": f"{len(single_source_nodes)} single-source nodes identified"
            },
            "recovery_under_2_weeks": {
                "status": recovery_status,
                "details": f"{risk_metrics['mean_recovery_days']:.1f} days mean recovery"
            },
            "inventory_cost_under_5pct": {
                "status": inv_status,
                "details": f"{inventory_costs['cost_as_pct_of_revenue']:.2f}% of revenue"
            }
        },
        "recommendations": {
            "immediate_actions": [
                "Lock LPDDR4 supply contract within 90 days",
                "Qualify GlobalFoundries 22FDX as secondary foundry",
                "Increase memory safety stock to 3 months",
                "Engage Amkor as secondary OSAT"
            ],
            "medium_term_actions": [
                "Implement dual sourcing for all critical components",
                "Reduce Taiwan exposure from 40% to 25%",
                "Build 6-month memory buffer inventory",
                "Establish supply chain insurance policy"
            ],
            "risk_budget_allocation": {
                "safety_stock": 72000,
                "dual_source_qualification": 275000,
                "premium_pricing_reserve": 50000,
                "insurance": 30000,
                "total_annual": 427000
            }
        }
    }
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    
    return results_summary

# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    # Run simulation with 10,000 iterations
    results = run_supply_chain_simulation(n_iterations=10000)
    
    # Save results to JSON
    output_path = "/home/z/my-project/download/simulations/C1_supply_chain_risk_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_path}")
