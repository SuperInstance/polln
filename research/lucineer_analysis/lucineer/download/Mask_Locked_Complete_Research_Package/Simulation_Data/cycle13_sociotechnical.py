#!/usr/bin/env python3
"""
Cycle 13: Sociotechnical Manufacturing Systems Analysis
=========================================================

Comprehensive simulation integrating:
1. Supply chain network dynamics (multi-tier suppliers, disruption propagation, resilience)
2. Human-technology interaction (operator skills, training, error rates, automation)
3. Organizational network analysis (information flow, decision hierarchies, trust networks)
4. Economic modeling (cost drivers, economies of scale, learning curves, make vs buy)

Key Parameters:
- 28nm foundry ecosystem (TSMC, GlobalFoundries, Samsung)
- 36-month development timeline
- $8-12M capital requirements
- Key personnel requirements

Author: Simulation Agent
Date: January 2025
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import networkx as nx
from scipy import stats
from scipy.optimize import minimize, linprog
from scipy.special import softmax
import json
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SECTION 1: SUPPLY CHAIN NETWORK DYNAMICS
# =============================================================================

class SupplierTier(Enum):
    TIER_1_FOUNDRY = "tier_1_foundry"
    TIER_1_MEMORY = "tier_1_memory"
    TIER_1_OSAT = "tier_1_osat"
    TIER_2_SUBSTRATE = "tier_2_substrate"
    TIER_2_CHEMICALS = "tier_2_chemicals"
    TIER_3_EQUIPMENT = "tier_3_equipment"
    TIER_3_RAW_MATERIALS = "tier_3_raw_materials"

@dataclass
class Supplier:
    """Represents a supplier in the network"""
    name: str
    tier: SupplierTier
    location: str
    lead_time_weeks: float
    quality_score: float  # 0-1
    capacity_units_per_month: float
    current_utilization: float  # 0-1
    disruption_probability: float
    recovery_time_weeks: float
    cost_per_unit: float
    geographic_risk: float  # 0-1
    single_source_risk: bool = False
    relationships: List[str] = field(default_factory=list)
    
    def effective_capacity(self) -> float:
        """Calculate effective capacity accounting for utilization"""
        return self.capacity_units_per_month * (1 - self.current_utilization)
    
    def disruption_risk_score(self) -> float:
        """Calculate overall disruption risk"""
        return self.disruption_probability * (1 + self.geographic_risk)

@dataclass
class SupplyChainNode:
    """Node in supply chain network"""
    supplier: Supplier
    inventory_level: float = 0.0
    safety_stock: float = 0.0
    in_transit: float = 0.0
    demand_forecast: List[float] = field(default_factory=list)
    
class SupplyChainNetwork:
    """
    Multi-tier supply chain network model with disruption propagation
    
    Models:
    - Supplier relationships and dependencies
    - Disruption cascade effects
    - Inventory optimization
    - Resilience metrics
    """
    
    def __init__(self):
        self.nodes: Dict[str, SupplyChainNode] = {}
        self.edges: List[Tuple[str, str, Dict]] = []
        self.network = nx.DiGraph()
        self.disruption_history: List[Dict] = []
        
    def add_supplier(self, supplier: Supplier, initial_inventory: float = 0):
        """Add supplier to network"""
        node = SupplyChainNode(supplier=supplier, inventory_level=initial_inventory)
        self.nodes[supplier.name] = node
        self.network.add_node(supplier.name, data=supplier)
        
    def add_relationship(self, from_supplier: str, to_supplier: str, 
                         volume_per_month: float, dependency: float = 1.0):
        """Add supply relationship between suppliers"""
        edge_data = {
            'volume': volume_per_month,
            'dependency': dependency,  # How critical this relationship is
            'lead_time': self.nodes[from_supplier].supplier.lead_time_weeks
        }
        self.edges.append((from_supplier, to_supplier, edge_data))
        self.network.add_edge(from_supplier, to_supplier, **edge_data)
        
        # Track relationships
        self.nodes[from_supplier].supplier.relationships.append(to_supplier)
        self.nodes[to_supplier].supplier.relationships.append(from_supplier)
    
    def calculate_resilience_metrics(self) -> Dict[str, float]:
        """Calculate supply chain resilience metrics"""
        metrics = {
            'network_density': nx.density(self.network),
            'average_clustering': nx.average_clustering(self.network.to_undirected()),
            'strongly_connected': nx.is_strongly_connected(self.network),
            'critical_nodes': [],
            'bottleneck_suppliers': [],
            'geographic_concentration': 0.0,
            'single_source_count': 0
        }
        
        # Identify critical nodes (high betweenness centrality)
        betweenness = nx.betweenness_centrality(self.network)
        metrics['critical_nodes'] = [
            (node, score) for node, score in sorted(betweenness.items(), 
                                                     key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Count single-source dependencies
        for node_name, node in self.nodes.items():
            if node.supplier.single_source_risk:
                metrics['single_source_count'] += 1
                
        # Calculate geographic concentration
        locations = [node.supplier.location for node in self.nodes.values()]
        location_counts = pd.Series(locations).value_counts(normalize=True)
        metrics['geographic_concentration'] = location_counts.max()
        
        return metrics
    
    def simulate_disruption_propagation(self, disrupted_supplier: str, 
                                        duration_weeks: int) -> Dict:
        """
        Simulate how a disruption propagates through the network
        
        Uses Susceptible-Infected-Recovered (SIR) model adapted for supply chains
        """
        results = {
            'origin': disrupted_supplier,
            'duration': duration_weeks,
            'affected_suppliers': [],
            'total_impact_days': 0,
            'recovery_timeline': {},
            'cascading_failures': 0
        }
        
        # States: 0 = Normal, 1 = Disrupted, 2 = Recovering
        states = {name: 0 for name in self.nodes.keys()}
        states[disrupted_supplier] = 1
        
        # Disruption propagation parameters
        transmission_rate = 0.3  # Probability of disruption spreading to dependent
        recovery_rate = 1 / self.nodes[disrupted_supplier].supplier.recovery_time_weeks
        
        affected = [disrupted_supplier]
        week = 0
        
        while week < duration_weeks + 26:  # Max 26 weeks simulation
            new_states = states.copy()
            
            for supplier_name, state in states.items():
                if state == 1:  # Disrupted - check if recovery starts
                    if np.random.random() < recovery_rate:
                        new_states[supplier_name] = 2
                        results['recovery_timeline'][supplier_name] = week
                        
                elif state == 0:  # Normal - check for disruption spread
                    # Check if any connected supplier is disrupted
                    for predecessor in self.network.predecessors(supplier_name):
                        if states[predecessor] == 1:
                            edge_data = self.network[predecessor][supplier_name]
                            if np.random.random() < transmission_rate * edge_data['dependency']:
                                new_states[supplier_name] = 1
                                if supplier_name not in affected:
                                    affected.append(supplier_name)
                                    results['cascading_failures'] += 1
                                break
                                
            states = new_states
            week += 1
            
            # Check if all recovered
            if all(s != 1 for s in states.values()):
                break
        
        results['affected_suppliers'] = affected
        results['total_impact_days'] = len(affected) * duration_weeks * 7
        
        self.disruption_history.append(results)
        return results
    
    def optimize_inventory(self, service_level: float = 0.95) -> Dict[str, Dict]:
        """
        Optimize inventory levels across the network
        
        Uses multi-echelon inventory theory with safety stock optimization
        """
        recommendations = {}
        
        for name, node in self.nodes.items():
            supplier = node.supplier
            
            # Calculate safety stock using standard formula
            # SS = z * sigma * sqrt(LT) where z = service factor
            z = stats.norm.ppf(service_level)
            
            # Assume demand variability based on capacity utilization
            demand_std = supplier.capacity_units_per_month * 0.2  # 20% variability
            lead_time_months = supplier.lead_time_weeks / 4.33
            
            safety_stock = z * demand_std * np.sqrt(lead_time_months)
            
            # Reorder point
            avg_demand = supplier.capacity_units_per_month * supplier.current_utilization
            reorder_point = avg_demand * lead_time_months + safety_stock
            
            # Economic order quantity
            # Assume ordering cost and holding cost
            ordering_cost = 500  # $ per order
            holding_cost_rate = 0.25  # 25% per year
            
            if supplier.cost_per_unit > 0:
                holding_cost = holding_cost_rate * supplier.cost_per_unit / 12
                if holding_cost > 0:
                    eoq = np.sqrt(2 * avg_demand * ordering_cost / holding_cost)
                else:
                    eoq = avg_demand
            else:
                eoq = avg_demand
            
            recommendations[name] = {
                'safety_stock': safety_stock,
                'reorder_point': reorder_point,
                'economic_order_quantity': eoq,
                'suggested_inventory': safety_stock * 1.5,  # Target inventory
                'current_inventory': node.inventory_level,
                'gap': safety_stock * 1.5 - node.inventory_level
            }
        
        return recommendations
    
    def monte_carlo_resilience(self, n_simulations: int = 1000) -> Dict:
        """
        Monte Carlo simulation of supply chain resilience
        
        Returns probability distribution of supply chain performance
        """
        results = {
            'successful_deliveries': [],
            'total_delay_days': [],
            'disruption_count': [],
            'recovery_time_days': []
        }
        
        for _ in range(n_simulations):
            total_delay = 0
            disruptions = 0
            deliveries_ok = True
            
            for name, node in self.nodes.items():
                supplier = node.supplier
                
                # Check if disruption occurs
                if np.random.random() < supplier.disruption_probability:
                    disruptions += 1
                    delay = np.random.exponential(supplier.recovery_time_weeks) * 7
                    total_delay += delay
                    
                    if delay > 14:  # More than 2 weeks is critical
                        deliveries_ok = False
            
            results['successful_deliveries'].append(1 if deliveries_ok else 0)
            results['total_delay_days'].append(total_delay)
            results['disruption_count'].append(disruptions)
            
            if disruptions > 0:
                results['recovery_time_days'].append(total_delay / disruptions)
            else:
                results['recovery_time_days'].append(0)
        
        return {
            'delivery_reliability': np.mean(results['successful_deliveries']),
            'expected_delay_days': np.mean(results['total_delay_days']),
            'disruption_probability': np.mean([1 if d > 0 else 0 for d in results['disruption_count']]),
            'p95_delay': np.percentile(results['total_delay_days'], 95),
            'mean_recovery_time': np.mean([r for r in results['recovery_time_days'] if r > 0]) if any(results['recovery_time_days']) else 0
        }


def create_28nm_foundry_network() -> SupplyChainNetwork:
    """Create supply chain network for 28nm mask-locked chip"""
    network = SupplyChainNetwork()
    
    # Tier 1: Foundries
    network.add_supplier(Supplier(
        name="TSMC_28nm",
        tier=SupplierTier.TIER_1_FOUNDRY,
        location="Taiwan",
        lead_time_weeks=16,
        quality_score=0.98,
        capacity_units_per_month=50000,
        current_utilization=0.90,
        disruption_probability=0.05,
        recovery_time_weeks=8,
        cost_per_unit=2.5,  # Per mm²
        geographic_risk=0.85,
        single_source_risk=True
    ), initial_inventory=0)
    
    network.add_supplier(Supplier(
        name="GlobalFoundries_22FDX",
        tier=SupplierTier.TIER_1_FOUNDRY,
        location="USA",
        lead_time_weeks=12,
        quality_score=0.95,
        capacity_units_per_month=30000,
        current_utilization=0.75,
        disruption_probability=0.03,
        recovery_time_weeks=6,
        cost_per_unit=2.2,
        geographic_risk=0.15,
        single_source_risk=False
    ), initial_inventory=0)
    
    network.add_supplier(Supplier(
        name="Samsung_28LPP",
        tier=SupplierTier.TIER_1_FOUNDRY,
        location="Korea",
        lead_time_weeks=14,
        quality_score=0.96,
        capacity_units_per_month=40000,
        current_utilization=0.85,
        disruption_probability=0.04,
        recovery_time_weeks=7,
        cost_per_unit=2.4,
        geographic_risk=0.35,
        single_source_risk=False
    ), initial_inventory=0)
    
    # Tier 1: Memory
    network.add_supplier(Supplier(
        name="Micron_LPDDR4",
        tier=SupplierTier.TIER_1_MEMORY,
        location="Taiwan/Singapore",
        lead_time_weeks=20,
        quality_score=0.97,
        capacity_units_per_month=100000,
        current_utilization=0.92,
        disruption_probability=0.06,
        recovery_time_weeks=10,
        cost_per_unit=10.0,  # Current LPDDR4 price
        geographic_risk=0.50,
        single_source_risk=False
    ), initial_inventory=10000)
    
    network.add_supplier(Supplier(
        name="Samsung_Memory",
        tier=SupplierTier.TIER_1_MEMORY,
        location="Korea",
        lead_time_weeks=18,
        quality_score=0.98,
        capacity_units_per_month=200000,
        current_utilization=0.88,
        disruption_probability=0.04,
        recovery_time_weeks=8,
        cost_per_unit=11.0,
        geographic_risk=0.35,
        single_source_risk=False
    ), initial_inventory=5000)
    
    # Tier 1: OSAT
    network.add_supplier(Supplier(
        name="ASE_Packaging",
        tier=SupplierTier.TIER_1_OSAT,
        location="Taiwan",
        lead_time_weeks=3,
        quality_score=0.97,
        capacity_units_per_month=150000,
        current_utilization=0.80,
        disruption_probability=0.04,
        recovery_time_weeks=4,
        cost_per_unit=0.12,
        geographic_risk=0.80,
        single_source_risk=True
    ), initial_inventory=0)
    
    network.add_supplier(Supplier(
        name="Amkor_US",
        tier=SupplierTier.TIER_1_OSAT,
        location="USA",
        lead_time_weeks=4,
        quality_score=0.95,
        capacity_units_per_month=80000,
        current_utilization=0.70,
        disruption_probability=0.03,
        recovery_time_weeks=3,
        cost_per_unit=0.15,
        geographic_risk=0.10,
        single_source_risk=False
    ), initial_inventory=0)
    
    # Tier 2: Substrates
    network.add_supplier(Supplier(
        name="Ibiden_Substrate",
        tier=SupplierTier.TIER_2_SUBSTRATE,
        location="Japan",
        lead_time_weeks=8,
        quality_score=0.96,
        capacity_units_per_month=50000,
        current_utilization=0.85,
        disruption_probability=0.05,
        recovery_time_weeks=6,
        cost_per_unit=0.30,
        geographic_risk=0.25,
        single_source_risk=True
    ), initial_inventory=0)
    
    # Add relationships
    # Foundry -> OSAT relationships
    network.add_relationship("TSMC_28nm", "ASE_Packaging", 30000, 0.9)
    network.add_relationship("GlobalFoundries_22FDX", "Amkor_US", 20000, 0.7)
    network.add_relationship("Samsung_28LPP", "ASE_Packaging", 25000, 0.6)
    
    # Memory -> OSAT relationships
    network.add_relationship("Micron_LPDDR4", "ASE_Packaging", 50000, 0.8)
    network.add_relationship("Samsung_Memory", "ASE_Packaging", 40000, 0.7)
    
    # Substrate -> OSAT relationships
    network.add_relationship("Ibiden_Substrate", "ASE_Packaging", 40000, 0.95)
    network.add_relationship("Ibiden_Substrate", "Amkor_US", 20000, 0.80)
    
    return network


# =============================================================================
# SECTION 2: HUMAN-TECHNOLOGY INTERACTION
# =============================================================================

@dataclass
class SkillRequirement:
    """Skill requirement for manufacturing operation"""
    name: str
    category: str  # technical, process, management
    importance: float  # 0-1
    scarcity: float  # 0-1, how hard to find
    training_weeks: float
    certification_required: bool = False
    
@dataclass
class Operator:
    """Manufacturing operator profile"""
    id: str
    role: str
    experience_years: float
    skills: Dict[str, float]  # skill_name -> proficiency 0-1
    error_rate_base: float
    training_completed: List[str] = field(default_factory=list)
    
    def effective_error_rate(self, task_complexity: float = 0.5) -> float:
        """Calculate error rate for a given task"""
        # Error rate decreases with experience and relevant skills
        experience_factor = np.exp(-0.1 * self.experience_years)
        return self.error_rate_base * experience_factor * (0.5 + 0.5 * task_complexity)

class HumanTechnologySystem:
    """
    Models human-technology interaction in semiconductor manufacturing
    
    Includes:
    - Operator skill requirements
    - Training time estimates
    - Error rate modeling
    - Automation level decisions
    """
    
    def __init__(self):
        self.skill_requirements: List[SkillRequirement] = []
        self.operators: Dict[str, Operator] = {}
        self.automation_decisions: Dict[str, Dict] = {}
        
    def add_skill_requirement(self, skill: SkillRequirement):
        """Add a skill requirement"""
        self.skill_requirements.append(skill)
        
    def add_operator(self, operator: Operator):
        """Add an operator to the system"""
        self.operators[operator.id] = operator
        
    def calculate_training_needs(self, target_skills: List[str]) -> Dict:
        """Calculate training requirements to achieve target skill levels"""
        requirements = {}
        
        for skill_name in target_skills:
            skill_req = next((s for s in self.skill_requirements if s.name == skill_name), None)
            if not skill_req:
                continue
                
            current_avg = np.mean([op.skills.get(skill_name, 0) for op in self.operators.values()])
            gap = 1.0 - current_avg
            
            requirements[skill_name] = {
                'current_level': current_avg,
                'target_level': 1.0,
                'gap': gap,
                'training_weeks': skill_req.training_weeks * gap,
                'scarcity': skill_req.scarcity,
                'importance': skill_req.importance,
                'certification_needed': skill_req.certification_required
            }
            
        return requirements
    
    def model_error_rates(self, n_simulations: int = 10000) -> Dict:
        """
        Model error rates across different manufacturing stages
        
        Returns error probability distributions for each stage
        """
        stages = {
            'design_verification': {'complexity': 0.8, 'automation': 0.7},
            'mask_preparation': {'complexity': 0.9, 'automation': 0.85},
            'wafer_processing': {'complexity': 0.7, 'automation': 0.95},
            'testing': {'complexity': 0.6, 'automation': 0.90},
            'packaging': {'complexity': 0.5, 'automation': 0.80},
            'quality_inspection': {'complexity': 0.4, 'automation': 0.60}
        }
        
        results = {}
        
        for stage, params in stages.items():
            complexity = params['complexity']
            automation = params['automation']
            
            # Human error contribution
            human_error_rates = []
            for op in self.operators.values():
                human_error_rates.append(op.effective_error_rate(complexity))
            
            avg_human_error = np.mean(human_error_rates) if human_error_rates else 0.02
            
            # Combined error with automation
            # Automation catches most errors but has its own failure rate
            automation_failure_rate = 0.001 * (1 - automation)  # Higher automation = lower failure
            
            # Total error rate considering human-machine interaction
            # Error occurs if: (human error AND automation fails) OR automation fails independently
            total_error = avg_human_error * (1 - automation) + automation_failure_rate
            
            # Monte Carlo simulation
            errors = []
            for _ in range(n_simulations):
                human_err = np.random.random() < avg_human_error
                auto_catch = np.random.random() < automation if human_err else True
                auto_fail = np.random.random() < automation_failure_rate
                
                errors.append(1 if (human_err and not auto_catch) or auto_fail else 0)
            
            results[stage] = {
                'human_error_rate': avg_human_error,
                'automation_level': automation,
                'total_error_rate': np.mean(errors),
                'p95_error_rate': np.percentile(errors, 95) * 0.01,
                'contribution_human': avg_human_error * (1 - automation) / total_error if total_error > 0 else 0
            }
            
        return results
    
    def automation_decision_analysis(self, task: str, 
                                      human_cost_per_hour: float = 75,
                                      automation_capex: float = 500000) -> Dict:
        """
        Analyze make vs automate decision for a task
        
        Uses cost-benefit analysis considering:
        - Human labor costs
        - Automation capital costs
        - Error rates and rework costs
        - Flexibility requirements
        """
        # Task characteristics
        task_params = {
            'design_verification': {'hours_per_unit': 2, 'volume_per_year': 1000, 'error_cost': 50000},
            'mask_preparation': {'hours_per_unit': 8, 'volume_per_year': 50, 'error_cost': 200000},
            'wafer_testing': {'hours_per_unit': 0.5, 'volume_per_year': 50000, 'error_cost': 100},
            'packaging': {'hours_per_unit': 0.1, 'volume_per_year': 100000, 'error_cost': 5},
            'quality_inspection': {'hours_per_unit': 0.2, 'volume_per_year': 100000, 'error_cost': 50}
        }
        
        if task not in task_params:
            return {'error': f'Unknown task: {task}'}
            
        params = task_params[task]
        
        # Human-only costs
        human_labor_cost = params['hours_per_unit'] * human_cost_per_hour * params['volume_per_year']
        human_error_rate = 0.02  # Base human error rate
        human_error_cost = human_error_rate * params['error_cost'] * params['volume_per_year']
        total_human_cost = human_labor_cost + human_error_cost
        
        # Automated costs
        automation_efficiency = 0.1  # Automation takes 10% of human time
        automated_labor_cost = params['hours_per_unit'] * automation_efficiency * human_cost_per_hour * params['volume_per_year']
        automation_error_rate = 0.002  # Automation error rate
        automation_error_cost = automation_error_rate * params['error_cost'] * params['volume_per_year']
        
        # Depreciation of automation equipment (5-year life)
        annual_depreciation = automation_capex / 5
        maintenance_cost = automation_capex * 0.1  # 10% annual maintenance
        
        total_automated_cost = (automated_labor_cost + automation_error_cost + 
                                annual_depreciation + maintenance_cost)
        
        # Payback period
        annual_savings = total_human_cost - (automated_labor_cost + automation_error_cost)
        payback_years = automation_capex / annual_savings if annual_savings > 0 else float('inf')
        
        return {
            'task': task,
            'human_total_cost': total_human_cost,
            'automated_total_cost': total_automated_cost,
            'annual_savings': total_human_cost - total_automated_cost,
            'payback_years': payback_years,
            'recommendation': 'AUTOMATE' if payback_years < 3 else 'HUMAN',
            'confidence': 'HIGH' if payback_years < 2 or payback_years > 5 else 'MEDIUM'
        }
    
    def calculate_team_requirements(self, target_capacity: int,
                                     development_timeline_months: int = 36) -> Dict:
        """
        Calculate team size and composition for manufacturing
        
        Based on:
        - Target production capacity
        - Development phases
        - Skill requirements
        """
        phases = {
            'Phase 1 - Design': {
                'duration_months': 8,
                'key_roles': ['RTL Designer', 'Verification Engineer', 'Architecture Lead'],
                'team_size': 4
            },
            'Phase 2 - Prototype': {
                'duration_months': 12,
                'key_roles': ['Design Engineer', 'Test Engineer', 'Process Engineer', 'QA Lead'],
                'team_size': 8
            },
            'Phase 3 - Production': {
                'duration_months': 16,
                'key_roles': ['Manufacturing Engineer', 'Yield Engineer', 'Supply Chain Manager', 
                             'Quality Engineer', 'Test Engineer'],
                'team_size': 12
            }
        }
        
        # Calculate FTE requirements
        total_fte = 0
        role_requirements = {}
        
        for phase, details in phases.items():
            phase_fte = details['team_size'] * (details['duration_months'] / 12)
            total_fte += phase_fte
            
            for role in details['key_roles']:
                if role not in role_requirements:
                    role_requirements[role] = {
                        'phase': phase,
                        'fte_months': details['duration_months'],
                        'scarcity': self._get_role_scarcity(role),
                        'avg_salary': self._get_role_salary(role)
                    }
        
        # Critical hire analysis
        critical_hires = [
            {'role': 'VP Manufacturing', 'required': True, 'timeline': 'Month 1-2', 
             'scarcity': 0.9, 'critical_reason': '5+ tapeouts experience mandatory'},
            {'role': 'Design Lead', 'required': True, 'timeline': 'Month 1-3',
             'scarcity': 0.7, 'critical_reason': 'Mask-locked architecture expertise'},
            {'role': 'Test Engineer', 'required': True, 'timeline': 'Month 6-9',
             'scarcity': 0.5, 'critical_reason': 'Production test development'},
            {'role': 'Supply Chain Manager', 'required': True, 'timeline': 'Month 3-6',
             'scarcity': 0.6, 'critical_reason': 'Memory allocation, foundry relationship'}
        ]
        
        return {
            'total_fte_years': total_fte,
            'phases': phases,
            'role_requirements': role_requirements,
            'critical_hires': critical_hires,
            'annual_labor_cost': sum(
                r['avg_salary'] for r in role_requirements.values()
            ),
            'hiring_timeline': self._calculate_hiring_timeline(critical_hires)
        }
    
    def _get_role_scarcity(self, role: str) -> float:
        """Get scarcity rating for a role"""
        scarcity_map = {
            'VP Manufacturing': 0.9,
            'RTL Designer': 0.4,
            'Verification Engineer': 0.5,
            'Architecture Lead': 0.7,
            'Design Engineer': 0.4,
            'Test Engineer': 0.5,
            'Process Engineer': 0.6,
            'QA Lead': 0.4,
            'Manufacturing Engineer': 0.5,
            'Yield Engineer': 0.7,
            'Supply Chain Manager': 0.6,
            'Quality Engineer': 0.4
        }
        return scarcity_map.get(role, 0.5)
    
    def _get_role_salary(self, role: str) -> float:
        """Get average salary for a role"""
        salary_map = {
            'VP Manufacturing': 280000,
            'RTL Designer': 160000,
            'Verification Engineer': 155000,
            'Architecture Lead': 200000,
            'Design Engineer': 150000,
            'Test Engineer': 140000,
            'Process Engineer': 145000,
            'QA Lead': 135000,
            'Manufacturing Engineer': 140000,
            'Yield Engineer': 160000,
            'Supply Chain Manager': 145000,
            'Quality Engineer': 130000
        }
        return salary_map.get(role, 140000)
    
    def _calculate_hiring_timeline(self, critical_hires: List[Dict]) -> Dict:
        """Calculate realistic hiring timeline"""
        timeline = {}
        
        for hire in critical_hires:
            role = hire['role']
            scarcity = hire['scarcity']
            
            # Time to hire increases with scarcity
            base_time_weeks = 4  # Minimum 4 weeks
            scarcity_factor = 1 + scarcity * 3  # Up to 4x longer for scarce roles
            
            time_to_hire = base_time_weeks * scarcity_factor
            
            timeline[role] = {
                'time_to_hire_weeks': time_to_hire,
                'ramp_up_weeks': 8,  # Time to become productive
                'total_time_weeks': time_to_hire + 8,
                'probability_90_day_success': 0.8 - 0.2 * scarcity  # Lower success for scarce roles
            }
            
        return timeline


def create_chip_manufacturing_hts() -> HumanTechnologySystem:
    """Create human-technology system for chip manufacturing"""
    hts = HumanTechnologySystem()
    
    # Add skill requirements
    skills = [
        SkillRequirement("Mask Design", "technical", 0.95, 0.7, 12, True),
        SkillRequirement("RTL Verification", "technical", 0.90, 0.5, 8, True),
        SkillRequirement("Ternary Arithmetic", "technical", 0.85, 0.9, 16, False),
        SkillRequirement("DFT/BIST", "technical", 0.80, 0.6, 6, True),
        SkillRequirement("Yield Analysis", "process", 0.85, 0.7, 10, False),
        SkillRequirement("Foundry Interface", "process", 0.90, 0.8, 4, False),
        SkillRequirement("Test Development", "technical", 0.85, 0.5, 8, True),
        SkillRequirement("Supply Chain Mgmt", "management", 0.80, 0.6, 4, False),
        SkillRequirement("Quality Systems", "process", 0.75, 0.4, 6, True),
        SkillRequirement("Team Leadership", "management", 0.85, 0.7, 8, False)
    ]
    
    for skill in skills:
        hts.add_skill_requirement(skill)
    
    # Add initial operators
    operators = [
        Operator("OP001", "Design Lead", 8, {"Mask Design": 0.9, "RTL Verification": 0.85}, 0.015),
        Operator("OP002", "Verification Eng", 5, {"RTL Verification": 0.8, "DFT/BIST": 0.7}, 0.02),
        Operator("OP003", "Test Engineer", 4, {"Test Development": 0.75, "Quality Systems": 0.6}, 0.025),
        Operator("OP004", "Process Eng", 6, {"Yield Analysis": 0.8, "Foundry Interface": 0.7}, 0.02),
        Operator("OP005", "Supply Chain", 5, {"Supply Chain Mgmt": 0.8}, 0.03)
    ]
    
    for op in operators:
        hts.add_operator(op)
    
    return hts


# =============================================================================
# SECTION 3: ORGANIZATIONAL NETWORK ANALYSIS
# =============================================================================

@dataclass
class OrganizationalNode:
    """Node in organizational network"""
    name: str
    role: str
    department: str
    decision_authority: float  # 0-1
    information_access: float  # 0-1
    ip_access_level: str  # 'none', 'basic', 'full'
    
@dataclass
class InformationFlow:
    """Information flow between nodes"""
    source: str
    target: str
    flow_type: str  # 'decision', 'technical', 'coordination', 'ip_sensitive'
    frequency: float  # interactions per week
    importance: float  # 0-1

class OrganizationalNetwork:
    """
    Organizational network analysis for semiconductor manufacturing
    
    Models:
    - Information flow patterns
    - Decision-making hierarchies
    - Coordination mechanisms
    - Trust networks for IP protection
    """
    
    def __init__(self):
        self.nodes: Dict[str, OrganizationalNode] = {}
        self.flows: List[InformationFlow] = []
        self.network = nx.DiGraph()
        
    def add_node(self, node: OrganizationalNode):
        """Add organizational node"""
        self.nodes[node.name] = node
        self.network.add_node(node.name, **node.__dict__)
        
    def add_flow(self, flow: InformationFlow):
        """Add information flow"""
        self.flows.append(flow)
        self.network.add_edge(flow.source, flow.target, 
                              flow_type=flow.flow_type,
                              frequency=flow.frequency,
                              importance=flow.importance)
        
    def analyze_information_flow(self) -> Dict:
        """Analyze information flow patterns"""
        metrics = {
            'centralization': 0.0,
            'bottlenecks': [],
            'information_overload': [],
            'coordination_efficiency': 0.0,
            'decision_latency': 0.0
        }
        
        # Calculate degree centrality for information flow
        in_degree = dict(self.network.in_degree())
        out_degree = dict(self.network.out_degree())
        
        total_possible = len(self.nodes) - 1
        
        # Centralization index
        max_degree = max(out_degree.values()) if out_degree else 0
        centralization = sum(max_degree - d for d in out_degree.values())
        centralization /= ((len(self.nodes) - 1) * (len(self.nodes) - 2)) if len(self.nodes) > 2 else 1
        
        metrics['centralization'] = centralization
        
        # Identify bottlenecks (high betweenness)
        betweenness = nx.betweenness_centrality(self.network)
        metrics['bottlenecks'] = [
            (node, score) for node, score in sorted(betweenness.items(), 
                                                      key=lambda x: x[1], reverse=True)[:3]
        ]
        
        # Information overload (nodes with high in-degree)
        threshold = np.mean(list(in_degree.values())) + np.std(list(in_degree.values()))
        metrics['information_overload'] = [
            node for node, degree in in_degree.items() if degree > threshold
        ]
        
        # Coordination efficiency
        # Ratio of actual to required communication paths
        actual_paths = len(self.flows)
        required_paths = len(self.nodes) * (len(self.nodes) - 1) / 2  # Complete graph
        metrics['coordination_efficiency'] = actual_paths / required_paths if required_paths > 0 else 0
        
        return metrics
    
    def analyze_decision_hierarchy(self) -> Dict:
        """Analyze decision-making structure"""
        # Build decision tree based on authority levels
        authority_levels = {}
        
        for name, node in self.nodes.items():
            level = int(node.decision_authority * 10)  # 0-10 scale
            if level not in authority_levels:
                authority_levels[level] = []
            authority_levels[level].append(name)
        
        # Calculate span of control
        spans = {}
        for name, node in self.nodes.items():
            # Count direct reports (nodes with lower authority that this node points to)
            reports = [n for n in self.network.successors(name) 
                      if self.nodes[n].decision_authority < node.decision_authority]
            spans[name] = len(reports)
        
        # Decision latency model
        # Average path length for decisions
        try:
            avg_path_length = nx.average_shortest_path_length(self.network.to_undirected())
        except:
            avg_path_length = 0
            
        return {
            'authority_levels': authority_levels,
            'span_of_control': spans,
            'avg_span': np.mean(list(spans.values())) if spans else 0,
            'decision_layers': len(authority_levels),
            'avg_decision_path_length': avg_path_length,
            'hierarchy_efficiency': 1 / (1 + avg_path_length) if avg_path_length > 0 else 1
        }
    
    def analyze_trust_network(self) -> Dict:
        """Analyze trust network for IP protection"""
        # Define trust levels based on IP access
        trust_scores = {}
        
        for name, node in self.nodes.items():
            if node.ip_access_level == 'full':
                trust_scores[name] = 1.0
            elif node.ip_access_level == 'basic':
                trust_scores[name] = 0.6
            else:
                trust_scores[name] = 0.2
        
        # Analyze IP-sensitive communication paths
        sensitive_flows = [f for f in self.flows if f.flow_type == 'ip_sensitive']
        
        # Identify potential IP leak paths
        leak_risks = []
        
        for flow in sensitive_flows:
            source_trust = trust_scores.get(flow.source, 0)
            target_trust = trust_scores.get(flow.target, 0)
            
            if target_trust < source_trust:
                leak_risks.append({
                    'from': flow.source,
                    'to': flow.target,
                    'trust_drop': source_trust - target_trust,
                    'frequency': flow.frequency
                })
        
        # Calculate network trust score
        avg_trust = np.mean(list(trust_scores.values()))
        trust_variance = np.var(list(trust_scores.values()))
        
        return {
            'average_trust_score': avg_trust,
            'trust_variance': trust_variance,
            'high_trust_nodes': [n for n, t in trust_scores.items() if t > 0.8],
            'ip_sensitive_flows': len(sensitive_flows),
            'potential_leak_risks': leak_risks,
            'ip_protection_score': avg_trust * (1 - trust_variance)
        }
    
    def calculate_coordination_cost(self) -> Dict:
        """Calculate coordination costs using Brooks' Law principles"""
        n = len(self.nodes)
        
        # Communication paths = n(n-1)/2
        communication_paths = n * (n - 1) / 2
        
        # Assume average coordination overhead per path
        avg_coord_time_hours_per_week = 0.5
        hourly_cost = 75  # Average loaded hourly cost
        
        weekly_coordination_cost = communication_paths * avg_coord_time_hours_per_week * hourly_cost
        
        # Add project overhead
        project_overhead = n * 2 * hourly_cost  # 2 hours/week project overhead per person
        
        return {
            'num_people': n,
            'communication_paths': communication_paths,
            'weekly_coordination_hours': communication_paths * avg_coord_time_hours_per_week,
            'weekly_coordination_cost': weekly_coordination_cost + project_overhead,
            'annual_coordination_cost': (weekly_coordination_cost + project_overhead) * 52,
            'coordination_efficiency': 1 / np.sqrt(n)  # Brooks' Law scaling
        }
    
    def simulate_communication_failure(self, failed_node: str) -> Dict:
        """Simulate impact of communication failure with a node"""
        # Find all paths through this node
        affected_downstream = list(self.network.successors(failed_node))
        affected_upstream = list(self.network.predecessors(failed_node))
        
        # Calculate impact based on flow importance
        impact_score = 0
        impacted_flows = []
        
        for flow in self.flows:
            if flow.source == failed_node or flow.target == failed_node:
                impact_score += flow.importance * flow.frequency
                impacted_flows.append(flow)
        
        # Recovery time estimation
        recovery_time_days = len(impacted_flows) * 0.5  # Half day per impacted flow
        
        return {
            'failed_node': failed_node,
            'downstream_affected': affected_downstream,
            'upstream_affected': affected_upstream,
            'impact_score': impact_score,
            'impacted_flows': len(impacted_flows),
            'estimated_recovery_days': recovery_time_days,
            'criticality': 'HIGH' if impact_score > 5 else 'MEDIUM' if impact_score > 2 else 'LOW'
        }


def create_chip_organization() -> OrganizationalNetwork:
    """Create organizational network for chip startup"""
    org = OrganizationalNetwork()
    
    # Add organizational nodes
    nodes = [
        OrganizationalNode("CEO", "Chief Executive", "Executive", 1.0, 1.0, "full"),
        OrganizationalNode("CTO", "Chief Technology", "Executive", 0.9, 1.0, "full"),
        OrganizationalNode("VP_Mfg", "VP Manufacturing", "Manufacturing", 0.85, 0.9, "full"),
        OrganizationalNode("VP_Eng", "VP Engineering", "Engineering", 0.85, 0.9, "full"),
        OrganizationalNode("Design_Lead", "Design Lead", "Engineering", 0.6, 0.8, "full"),
        OrganizationalNode("Test_Lead", "Test Lead", "Engineering", 0.55, 0.7, "basic"),
        OrganizationalNode("Process_Eng", "Process Engineer", "Manufacturing", 0.5, 0.6, "basic"),
        OrganizationalNode("Yield_Eng", "Yield Engineer", "Manufacturing", 0.5, 0.6, "basic"),
        OrganizationalNode("SC_Manager", "Supply Chain Manager", "Operations", 0.5, 0.5, "none"),
        OrganizationalNode("QA_Lead", "QA Lead", "Quality", 0.45, 0.4, "basic"),
        OrganizationalNode("Foundry_Liaison", "Foundry Liaison", "Manufacturing", 0.4, 0.5, "basic"),
        OrganizationalNode("Design_Eng1", "Design Engineer", "Engineering", 0.3, 0.6, "full"),
        OrganizationalNode("Design_Eng2", "Design Engineer", "Engineering", 0.3, 0.6, "full"),
        OrganizationalNode("Test_Eng", "Test Engineer", "Engineering", 0.3, 0.5, "basic"),
        OrganizationalNode("Ops_Analyst", "Operations Analyst", "Operations", 0.25, 0.3, "none")
    ]
    
    for node in nodes:
        org.add_node(node)
    
    # Add information flows
    flows = [
        # Executive communications
        InformationFlow("CEO", "CTO", "decision", 5, 0.9),
        InformationFlow("CEO", "VP_Mfg", "decision", 3, 0.8),
        InformationFlow("CEO", "VP_Eng", "decision", 3, 0.8),
        InformationFlow("CTO", "VP_Eng", "technical", 8, 0.9),
        InformationFlow("CTO", "VP_Mfg", "technical", 4, 0.7),
        
        # Engineering flows
        InformationFlow("VP_Eng", "Design_Lead", "decision", 10, 0.85),
        InformationFlow("VP_Eng", "Test_Lead", "decision", 8, 0.75),
        InformationFlow("Design_Lead", "Design_Eng1", "technical", 20, 0.9),
        InformationFlow("Design_Lead", "Design_Eng2", "technical", 20, 0.9),
        InformationFlow("Design_Lead", "Test_Lead", "coordination", 8, 0.7),
        
        # Manufacturing flows
        InformationFlow("VP_Mfg", "Process_Eng", "decision", 8, 0.8),
        InformationFlow("VP_Mfg", "Yield_Eng", "decision", 8, 0.8),
        InformationFlow("VP_Mfg", "Foundry_Liaison", "coordination", 12, 0.9),
        InformationFlow("VP_Mfg", "SC_Manager", "decision", 6, 0.7),
        
        # IP-sensitive flows
        InformationFlow("CTO", "Design_Lead", "ip_sensitive", 4, 0.95),
        InformationFlow("Design_Lead", "Design_Eng1", "ip_sensitive", 10, 0.9),
        InformationFlow("Design_Lead", "Design_Eng2", "ip_sensitive", 10, 0.9),
        InformationFlow("VP_Eng", "Design_Lead", "ip_sensitive", 6, 0.9),
        
        # Cross-functional coordination
        InformationFlow("Design_Lead", "Process_Eng", "coordination", 5, 0.6),
        InformationFlow("Test_Lead", "Yield_Eng", "coordination", 6, 0.7),
        InformationFlow("Process_Eng", "Foundry_Liaison", "technical", 15, 0.8),
        InformationFlow("SC_Manager", "Foundry_Liaison", "coordination", 8, 0.6),
        InformationFlow("QA_Lead", "Test_Lead", "coordination", 4, 0.5),
        InformationFlow("QA_Lead", "Yield_Eng", "coordination", 4, 0.5),
        
        # Operations
        InformationFlow("SC_Manager", "Ops_Analyst", "decision", 10, 0.5),
        InformationFlow("SC_Manager", "VP_Mfg", "technical", 5, 0.6)
    ]
    
    for flow in flows:
        org.add_flow(flow)
    
    return org


# =============================================================================
# SECTION 4: ECONOMIC MODELING
# =============================================================================

@dataclass
class CostDriver:
    """Cost driver for economic analysis"""
    name: str
    category: str  # 'fixed', 'variable', 'semi-variable'
    base_cost: float
    volume_dependency: float  # 0 = fixed, 1 = fully variable
    learning_rate: float  # Cost reduction per doubling of volume
    
class EconomicModel:
    """
    Economic modeling for semiconductor manufacturing
    
    Includes:
    - Cost drivers analysis
    - Economies of scale
    - Learning curve effects
    - Make vs buy decisions
    """
    
    def __init__(self, initial_capex: float = 10_000_000):
        self.capex = initial_capex
        self.cost_drivers: List[CostDriver] = []
        self.production_volumes: List[int] = []
        self.unit_costs: List[float] = []
        
    def add_cost_driver(self, driver: CostDriver):
        """Add a cost driver"""
        self.cost_drivers.append(driver)
        
    def calculate_unit_cost(self, volume: int, cumulative_volume: int = None) -> Dict:
        """
        Calculate unit cost at given production volume
        
        Includes:
        - Fixed cost allocation
        - Variable costs
        - Learning curve effects
        """
        if cumulative_volume is None:
            cumulative_volume = volume
            
        costs = {}
        
        for driver in self.cost_drivers:
            if driver.category == 'fixed':
                # Fixed cost allocated over volume
                cost = driver.base_cost / volume
                
            elif driver.category == 'variable':
                # Variable cost with learning curve
                learning_factor = cumulative_volume ** (-driver.learning_rate)
                cost = driver.base_cost * learning_factor
                
            else:  # semi-variable
                # Combination of fixed and variable
                fixed_portion = driver.base_cost * (1 - driver.volume_dependency) / volume
                variable_portion = driver.base_cost * driver.volume_dependency
                learning_factor = cumulative_volume ** (-driver.learning_rate)
                cost = fixed_portion + variable_portion * learning_factor
            
            costs[driver.name] = cost
            
        total_unit_cost = sum(costs.values())
        
        return {
            'volume': volume,
            'cumulative_volume': cumulative_volume,
            'cost_breakdown': costs,
            'total_unit_cost': total_unit_cost,
            'gross_margin_at_price': lambda price: (price - total_unit_cost) / price
        }
    
    def calculate_economies_of_scale(self, volumes: List[int]) -> Dict:
        """Calculate economies of scale across production volumes"""
        results = []
        
        for volume in volumes:
            cost = self.calculate_unit_cost(volume)
            results.append({
                'volume': volume,
                'unit_cost': cost['total_unit_cost'],
                'fixed_per_unit': sum(v for k, v in cost['cost_breakdown'].items() 
                                     if any(d.name == k and d.category == 'fixed' 
                                           for d in self.cost_drivers)),
                'variable_per_unit': sum(v for k, v in cost['cost_breakdown'].items() 
                                        if any(d.name == k and d.category == 'variable' 
                                              for d in self.cost_drivers))
            })
            
        # Calculate scale elasticity
        if len(results) >= 2:
            cost_ratio = results[-1]['unit_cost'] / results[0]['unit_cost']
            volume_ratio = results[-1]['volume'] / results[0]['volume']
            scale_elasticity = np.log(cost_ratio) / np.log(volume_ratio)
        else:
            scale_elasticity = 0
            
        return {
            'volume_analysis': results,
            'scale_elasticity': scale_elasticity,
            'minimum_efficient_scale': self._find_mes(results)
        }
    
    def _find_mes(self, results: List[Dict]) -> int:
        """Find minimum efficient scale (MES)"""
        if not results:
            return 0
            
        # MES is where unit cost is within 10% of minimum
        min_cost = min(r['unit_cost'] for r in results)
        
        for result in results:
            if result['unit_cost'] <= min_cost * 1.1:
                return result['volume']
                
        return results[-1]['volume']
    
    def calculate_learning_curve(self, initial_cost: float, 
                                  learning_rate: float,
                                  volumes: List[int]) -> Dict:
        """
        Calculate learning curve effects
        
        Wright's learning curve model:
        C_n = C_1 * n^(-b) where b = -log2(learning_rate)
        """
        b = -np.log2(learning_rate)
        
        results = []
        cumulative = 0
        
        for volume in volumes:
            cumulative += volume
            
            # Average cost for this batch
            if cumulative == volume:  # First batch
                avg_cost = initial_cost * volume ** (-b)
            else:
                # Total cost of batch
                prev_cumulative = cumulative - volume
                total_cost = (initial_cost / (1 - b)) * (
                    cumulative ** (1 - b) - prev_cumulative ** (1 - b)
                )
                avg_cost = total_cost / volume
            
            results.append({
                'batch_volume': volume,
                'cumulative_volume': cumulative,
                'average_cost': avg_cost,
                'cost_reduction_pct': (1 - avg_cost / initial_cost) * 100
            })
            
        return {
            'initial_cost': initial_cost,
            'learning_rate': learning_rate,
            'exponent': b,
            'curve_data': results
        }
    
    def make_vs_buy_analysis(self, component: str,
                              internal_cost: float,
                              external_cost: float,
                              volume: int,
                              strategic_importance: float = 0.5) -> Dict:
        """
        Make vs buy decision analysis
        
        Considers:
        - Cost comparison
        - Strategic importance
        - Quality control
        - IP protection
        - Supply chain risk
        """
        # Total costs
        internal_total = internal_cost * volume
        external_total = external_cost * volume
        
        # Strategic factors
        factors = {
            'cost': {
                'internal': internal_total,
                'external': external_total,
                'advantage': 'internal' if internal_total < external_total else 'external'
            },
            'quality_control': {
                'internal': 0.95,  # High control
                'external': 0.75,  # Lower control
                'advantage': 'internal'
            },
            'ip_protection': {
                'internal': 0.90,
                'external': 0.50,
                'advantage': 'internal'
            },
            'flexibility': {
                'internal': 0.70,
                'external': 0.85,
                'advantage': 'external'
            },
            'capacity_utilization': {
                'internal': 0.80,
                'external': 1.0,  # No capacity impact
                'advantage': 'external'
            }
        }
        
        # Weighted decision score
        weights = {
            'cost': 0.40,
            'quality_control': 0.15,
            'ip_protection': strategic_importance * 0.20,
            'flexibility': 0.10,
            'capacity_utilization': 0.15 - strategic_importance * 0.10
        }
        
        internal_score = sum(
            factors[f]['internal'] * weights[f] for f in factors
        )
        external_score = sum(
            factors[f]['external'] * weights[f] for f in factors
        )
        
        # Normalize scores
        total_score = internal_score + external_score
        internal_prob = internal_score / total_score if total_score > 0 else 0.5
        
        return {
            'component': component,
            'volume': volume,
            'internal_cost_total': internal_total,
            'external_cost_total': external_total,
            'cost_difference': external_total - internal_total,
            'factors': factors,
            'internal_score': internal_score,
            'external_score': external_score,
            'recommendation': 'MAKE' if internal_prob > 0.55 else 'BUY' if internal_prob < 0.45 else 'PARTNER',
            'confidence': abs(internal_prob - 0.5) * 2
        }
    
    def calculate_capital_requirements(self, timeline_months: int = 36) -> Dict:
        """Calculate detailed capital requirements"""
        # Phase-based capital allocation
        phases = {
            'Phase 1 (Month 1-8)': {
                'activities': ['Design', 'FPGA prototype', 'Patent filing', 'Team building'],
                'capex': 500_000,
                'opex_per_month': 150_000,
                'months': 8
            },
            'Phase 2 (Month 9-20)': {
                'activities': ['MPW tapeout', 'Silicon validation', 'Test development', 'SDK development'],
                'capex': 1_500_000,
                'opex_per_month': 250_000,
                'months': 12
            },
            'Phase 3 (Month 21-36)': {
                'activities': ['Production mask', 'Yield optimization', 'Volume ramp', 'Sales/Marketing'],
                'capex': 3_000_000,
                'opex_per_month': 400_000,
                'months': 16
            }
        }
        
        total_capex = 0
        total_opex = 0
        cash_flow = []
        cumulative = 0
        
        for phase, details in phases.items():
            phase_capex = details['capex']
            phase_opex = details['opex_per_month'] * details['months']
            
            total_capex += phase_capex
            total_opex += phase_opex
            
            # Monthly cash flow within phase
            for month in range(details['months']):
                monthly_capex = phase_capex / details['months']
                cumulative += details['opex_per_month'] + monthly_capex
                cash_flow.append({
                    'month': len(cash_flow) + 1,
                    'capex': monthly_capex,
                    'opex': details['opex_per_month'],
                    'total': details['opex_per_month'] + monthly_capex,
                    'cumulative': cumulative
                })
        
        # Funding requirements
        safety_margin = 0.20
        total_required = (total_capex + total_opex) * (1 + safety_margin)
        
        return {
            'phases': phases,
            'total_capex': total_capex,
            'total_opex': total_opex,
            'total_required': total_required,
            'safety_margin': safety_margin,
            'monthly_cash_flow': cash_flow,
            'peak_cash_requirement': max(c['cumulative'] for c in cash_flow),
            'funding_rounds': self._calculate_funding_rounds(total_required)
        }
    
    def _calculate_funding_rounds(self, total: float) -> List[Dict]:
        """Calculate funding round structure"""
        return [
            {
                'round': 'Seed',
                'amount': 2_500_000,
                'timing': 'Month 1',
                'use': ['Team building', 'FPGA prototype', 'Patents', 'Initial design'],
                'runway_months': 12
            },
            {
                'round': 'Series A',
                'amount': 6_000_000,
                'timing': 'Month 12',
                'use': ['MPW tapeout', 'Test development', 'Team expansion', 'Production prep'],
                'runway_months': 18
            },
            {
                'round': 'Series B',
                'amount': 4_000_000,
                'timing': 'Month 24',
                'use': ['Volume production', 'Sales/Marketing', 'Working capital'],
                'runway_months': 12
            }
        ]
    
    def calculate_npv_irr(self, cash_flows: List[float], 
                          discount_rate: float = 0.15) -> Dict:
        """Calculate NPV and IRR for the investment"""
        # NPV calculation
        npv = sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows))
        
        # IRR calculation using numpy
        try:
            irr = np.irr(cash_flows)
        except:
            irr = None
            
        # Payback period
        cumulative = 0
        payback_period = None
        for t, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative > 0 and payback_period is None:
                # Linear interpolation
                prev_cumulative = cumulative - cf
                payback_period = t - 1 + (-prev_cumulative) / cf
                break
        
        return {
            'npv': npv,
            'irr': irr,
            'payback_period_months': payback_period * 12 if payback_period else None,
            'discount_rate': discount_rate,
            'investment_grade': 'A' if npv > 0 and irr and irr > discount_rate else 'B' if npv > 0 else 'C'
        }


def create_chip_economic_model() -> EconomicModel:
    """Create economic model for chip manufacturing"""
    model = EconomicModel(initial_capex=10_000_000)
    
    # Add cost drivers
    drivers = [
        # Fixed costs
        CostDriver("Mask Set", "fixed", 1_500_000, 0, 0),
        CostDriver("Test Development", "fixed", 200_000, 0, 0),
        CostDriver("NRE (Non-Recurring Engineering)", "fixed", 500_000, 0, 0),
        
        # Variable costs
        CostDriver("Wafer Cost", "variable", 2.5, 1, 0.1),  # $/mm² with 10% learning
        CostDriver("LPDDR4 Memory", "variable", 10.0, 1, 0.05),  # $/unit with 5% learning
        CostDriver("Packaging", "variable", 0.12, 1, 0.15),
        CostDriver("Test", "variable", 0.05, 1, 0.12),
        
        # Semi-variable costs
        CostDriver("Quality Control", "semi-variable", 0.02, 0.3, 0.08),
        CostDriver("Logistics", "semi-variable", 0.15, 0.7, 0.05),
    ]
    
    for driver in drivers:
        model.add_cost_driver(driver)
    
    return model


# =============================================================================
# SECTION 5: INTEGRATED SIMULATION
# =============================================================================

class SociotechnicalManufacturingSimulation:
    """
    Integrated sociotechnical manufacturing simulation
    
    Combines all models for comprehensive analysis
    """
    
    def __init__(self):
        self.supply_chain = create_28nm_foundry_network()
        self.human_tech = create_chip_manufacturing_hts()
        self.organization = create_chip_organization()
        self.economics = create_chip_economic_model()
        
        self.simulation_results = {}
        
    def run_full_simulation(self, n_monte_carlo: int = 1000) -> Dict:
        """Run comprehensive integrated simulation"""
        results = {
            'supply_chain': {},
            'human_technology': {},
            'organization': {},
            'economics': {},
            'integrated_risk': {},
            'recommendations': []
        }
        
        # Supply chain analysis
        results['supply_chain']['resilience'] = self.supply_chain.calculate_resilience_metrics()
        results['supply_chain']['monte_carlo'] = self.supply_chain.monte_carlo_resilience(n_monte_carlo)
        results['supply_chain']['inventory'] = self.supply_chain.optimize_inventory()
        
        # Simulate key disruption scenarios
        results['supply_chain']['disruptions'] = {
            'taiwan_blockade': self.supply_chain.simulate_disruption_propagation("TSMC_28nm", 12),
            'memory_crisis': self.supply_chain.simulate_disruption_propagation("Micron_LPDDR4", 8),
            'osat_failure': self.supply_chain.simulate_disruption_propagation("ASE_Packaging", 4)
        }
        
        # Human-technology analysis
        results['human_technology']['error_rates'] = self.human_tech.model_error_rates()
        results['human_technology']['training_needs'] = self.human_tech.calculate_training_needs(
            ['Mask Design', 'Ternary Arithmetic', 'Yield Analysis']
        )
        results['human_technology']['team_requirements'] = self.human_tech.calculate_team_requirements(
            target_capacity=100000
        )
        
        # Automation decisions
        results['human_technology']['automation'] = {
            'testing': self.human_tech.automation_decision_analysis('wafer_testing'),
            'packaging': self.human_tech.automation_decision_analysis('packaging'),
            'quality': self.human_tech.automation_decision_analysis('quality_inspection')
        }
        
        # Organizational analysis
        results['organization']['information_flow'] = self.organization.analyze_information_flow()
        results['organization']['decision_hierarchy'] = self.organization.analyze_decision_hierarchy()
        results['organization']['trust_network'] = self.organization.analyze_trust_network()
        results['organization']['coordination_cost'] = self.organization.calculate_coordination_cost()
        
        # Economic analysis
        results['economics']['economies_of_scale'] = self.economics.calculate_economies_of_scale(
            [10000, 50000, 100000, 250000, 500000, 1000000]
        )
        results['economics']['capital_requirements'] = self.economics.calculate_capital_requirements(36)
        
        # Learning curve for key costs
        results['economics']['learning_curves'] = {
            'wafer': self.economics.calculate_learning_curve(2.5, 0.90, 
                                                             [10000, 20000, 40000, 80000, 160000]),
            'memory': self.economics.calculate_learning_curve(10.0, 0.95,
                                                              [10000, 20000, 40000, 80000, 160000])
        }
        
        # Make vs buy decisions
        results['economics']['make_vs_buy'] = {
            'test_equipment': self.economics.make_vs_buy_analysis(
                'test_equipment', 0.08, 0.05, 100000, strategic_importance=0.3
            ),
            'packaging': self.economics.make_vs_buy_analysis(
                'packaging', 0.15, 0.12, 100000, strategic_importance=0.2
            )
        }
        
        # Integrated risk assessment
        results['integrated_risk'] = self._calculate_integrated_risk(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        self.simulation_results = results
        return results
    
    def _calculate_integrated_risk(self, results: Dict) -> Dict:
        """Calculate integrated risk score"""
        risk_factors = []
        
        # Supply chain risks
        sc_resilience = results['supply_chain']['monte_carlo']['delivery_reliability']
        risk_factors.append({
            'category': 'Supply Chain',
            'factor': 'Delivery Reliability',
            'score': 1 - sc_resilience,
            'weight': 0.25
        })
        
        sc_geographic = results['supply_chain']['resilience']['geographic_concentration']
        risk_factors.append({
            'category': 'Supply Chain',
            'factor': 'Geographic Concentration',
            'score': sc_geographic,
            'weight': 0.15
        })
        
        # Human capital risks
        training_gaps = results['human_technology']['training_needs']
        avg_gap = np.mean([t['gap'] for t in training_gaps.values()]) if training_gaps else 0
        risk_factors.append({
            'category': 'Human Capital',
            'factor': 'Skill Gap',
            'score': avg_gap,
            'weight': 0.15
        })
        
        # Organizational risks
        coord_efficiency = results['organization']['information_flow']['coordination_efficiency']
        risk_factors.append({
            'category': 'Organization',
            'factor': 'Coordination Efficiency',
            'score': 1 - coord_efficiency,
            'weight': 0.10
        })
        
        ip_protection = results['organization']['trust_network']['ip_protection_score']
        risk_factors.append({
            'category': 'Organization',
            'factor': 'IP Protection',
            'score': 1 - ip_protection,
            'weight': 0.10
        })
        
        # Economic risks
        cap_req = results['economics']['capital_requirements']
        funding_gap = cap_req['total_required'] - 12_500_000  # Assumed available funding
        risk_factors.append({
            'category': 'Economic',
            'factor': 'Funding Gap',
            'score': max(0, funding_gap / cap_req['total_required']),
            'weight': 0.15
        })
        
        scale_elasticity = abs(results['economics']['economies_of_scale']['scale_elasticity'])
        risk_factors.append({
            'category': 'Economic',
            'factor': 'Scale Sensitivity',
            'score': min(1, scale_elasticity / 0.5),  # Normalize
            'weight': 0.10
        })
        
        # Calculate weighted risk score
        total_risk = sum(f['score'] * f['weight'] for f in risk_factors)
        
        return {
            'risk_factors': risk_factors,
            'total_risk_score': total_risk,
            'risk_rating': 'HIGH' if total_risk > 0.5 else 'MEDIUM' if total_risk > 0.3 else 'LOW',
            'risk_mitigation_budget': total_risk * results['economics']['capital_requirements']['total_required'] * 0.12
        }
    
    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Supply chain recommendations
        if results['supply_chain']['monte_carlo']['delivery_reliability'] < 0.9:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Supply Chain',
                'recommendation': 'Implement dual-sourcing for critical components',
                'details': 'Establish secondary memory supplier and qualify second OSAT',
                'investment': 150_000,
                'timeline': '3-6 months'
            })
        
        if results['supply_chain']['resilience']['geographic_concentration'] > 0.5:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Supply Chain',
                'recommendation': 'Diversify geographic sourcing',
                'details': 'Prioritize GlobalFoundries 22FDX as primary foundry',
                'investment': 25_000,
                'timeline': '1-2 months'
            })
        
        # Human capital recommendations
        critical_hires = results['human_technology']['team_requirements']['critical_hires']
        for hire in critical_hires:
            if hire['required']:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Human Capital',
                    'recommendation': f"Hire {hire['role']}",
                    'details': hire['critical_reason'],
                    'investment': self.human_tech._get_role_salary(hire['role']) * 1.3,
                    'timeline': hire['timeline']
                })
        
        # Organizational recommendations
        if results['organization']['trust_network']['ip_protection_score'] < 0.7:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Organization',
                'recommendation': 'Strengthen IP protection protocols',
                'details': 'Implement need-to-know access, audit trails, and NDAs',
                'investment': 50_000,
                'timeline': '1-3 months'
            })
        
        # Economic recommendations
        mes = results['economics']['economies_of_scale']['minimum_efficient_scale']
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Economic',
            'recommendation': f'Target minimum efficient scale of {mes:,} units',
            'details': 'Plan production volumes to achieve MES within 24 months',
            'investment': 0,
            'timeline': 'Ongoing'
        })
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        if not self.simulation_results:
            self.run_full_simulation()
            
        results = self.simulation_results
        
        report = """
# Sociotechnical Manufacturing Systems Analysis
## Mask-Locked Inference Chip - Cycle 13

---

## Executive Summary

This analysis integrates supply chain dynamics, human-technology interaction, 
organizational networks, and economic modeling for the 28nm mask-locked 
inference chip manufacturing strategy.

### Key Findings

**Overall Risk Rating: {risk_rating}**
**Total Risk Score: {risk_score:.2f}

---

## 1. Supply Chain Network Analysis

### Network Resilience Metrics
- **Delivery Reliability**: {delivery_reliability:.1%}
- **Geographic Concentration**: {geo_concentration:.1%}
- **Single-Source Dependencies**: {single_source}
- **Critical Nodes**: {critical_nodes}

### Disruption Scenario Analysis

**Taiwan Blockade (TSMC disruption for 12 weeks)**:
- Affected Suppliers: {taiwan_affected}
- Cascading Failures: {taiwan_cascade}
- Total Impact: {taiwan_impact} days

**Memory Crisis (LPDDR4 shortage for 8 weeks)**:
- Affected Suppliers: {memory_affected}
- Expected Delay: {memory_delay:.0f} days

### Inventory Optimization
- **Safety Stock Recommendation**: 3-month buffer for LPDDR4
- **Reorder Points**: Calculated for all Tier 1 suppliers
- **Risk Budget**: ${risk_budget:,.0f} annually

---

## 2. Human-Technology Interaction

### Error Rate Analysis
- **Design Verification**: {design_error:.2%} error rate
- **Wafer Testing**: {test_error:.2%} error rate
- **Packaging**: {pkg_error:.2%} error rate

### Automation Decisions
| Task | Recommendation | Payback Period |
|------|---------------|----------------|
| Wafer Testing | {auto_test} | {test_payback:.1f} years |
| Packaging | {auto_pkg} | {pkg_payback:.1f} years |
| Quality Inspection | {auto_qa} | {qa_payback:.1f} years |

### Critical Team Requirements
{team_table}

---

## 3. Organizational Network Analysis

### Information Flow
- **Centralization Index**: {centralization:.2f}
- **Coordination Efficiency**: {coord_eff:.2%}
- **Bottleneck Nodes**: {bottlenecks}

### IP Protection
- **Trust Score**: {trust_score:.2f}
- **IP Sensitive Flows**: {ip_flows}
- **Potential Leak Risks**: {leak_risks}

### Coordination Costs
- **Annual Coordination Cost**: ${coord_cost:,.0f}
- **Communication Paths**: {comm_paths}

---

## 4. Economic Modeling

### Economies of Scale
- **Scale Elasticity**: {scale_elasticity:.3f}
- **Minimum Efficient Scale**: {mes:,} units
- **Unit Cost at MES**: ${mes_cost:.2f}

### Capital Requirements
- **Total Required**: ${total_cap:,.0f}
- **Peak Cash Requirement**: ${peak_cash:,.0f}
- **Funding Rounds**: Seed ($2.5M) → Series A ($6M) → Series B ($4M)

### Learning Curves
- **Wafer Cost Learning Rate**: 10% per doubling
- **Memory Cost Learning Rate**: 5% per doubling

---

## 5. Integrated Risk Assessment

{risk_table}

### Risk Mitigation Budget
**Recommended**: ${mitigation_budget:,.0f} annually (~12% of COGS)

---

## 6. Strategic Recommendations

{recommendations}

---

## Appendix: Monte Carlo Simulation Results

**Based on 1,000 simulations:**
- 95th percentile delay: {p95_delay:.0f} days
- Mean recovery time: {mean_recovery:.0f} days
- Probability of >1 disruption per year: {multi_disrupt:.1%}

---

*Generated by Sociotechnical Manufacturing Simulation*
*Cycle 13 - January 2025*
""".format(
            risk_rating=results['integrated_risk']['risk_rating'],
            risk_score=results['integrated_risk']['total_risk_score'],
            delivery_reliability=results['supply_chain']['monte_carlo']['delivery_reliability'],
            geo_concentration=results['supply_chain']['resilience']['geographic_concentration'],
            single_source=results['supply_chain']['resilience']['single_source_count'],
            critical_nodes=', '.join([n[0] for n in results['supply_chain']['resilience']['critical_nodes'][:3]]),
            taiwan_affected=len(results['supply_chain']['disruptions']['taiwan_blockade']['affected_suppliers']),
            taiwan_cascade=results['supply_chain']['disruptions']['taiwan_blockade']['cascading_failures'],
            taiwan_impact=results['supply_chain']['disruptions']['taiwan_blockade']['total_impact_days'],
            memory_affected=len(results['supply_chain']['disruptions']['memory_crisis']['affected_suppliers']),
            memory_delay=results['supply_chain']['disruptions']['memory_crisis']['total_impact_days'] / len(results['supply_chain']['disruptions']['memory_crisis']['affected_suppliers']) if results['supply_chain']['disruptions']['memory_crisis']['affected_suppliers'] else 0,
            risk_budget=results['integrated_risk']['risk_mitigation_budget'],
            design_error=results['human_technology']['error_rates']['design_verification']['total_error_rate'],
            test_error=results['human_technology']['error_rates']['testing']['total_error_rate'],
            pkg_error=results['human_technology']['error_rates']['packaging']['total_error_rate'],
            auto_test=results['human_technology']['automation']['testing']['recommendation'],
            test_payback=results['human_technology']['automation']['testing']['payback_years'],
            auto_pkg=results['human_technology']['automation']['packaging']['recommendation'],
            pkg_payback=results['human_technology']['automation']['packaging']['payback_years'],
            auto_qa=results['human_technology']['automation']['quality']['recommendation'],
            qa_payback=results['human_technology']['automation']['quality']['payback_years'],
            team_table=self._format_team_table(results['human_technology']['team_requirements']['critical_hires']),
            centralization=results['organization']['information_flow']['centralization'],
            coord_eff=results['organization']['information_flow']['coordination_efficiency'],
            bottlenecks=', '.join([b[0] for b in results['organization']['information_flow']['bottlenecks'][:3]]),
            trust_score=results['organization']['trust_network']['ip_protection_score'],
            ip_flows=results['organization']['trust_network']['ip_sensitive_flows'],
            leak_risks=len(results['organization']['trust_network']['potential_leak_risks']),
            coord_cost=results['organization']['coordination_cost']['annual_coordination_cost'],
            comm_paths=results['organization']['coordination_cost']['communication_paths'],
            scale_elasticity=results['economics']['economies_of_scale']['scale_elasticity'],
            mes=results['economics']['economies_of_scale']['minimum_efficient_scale'],
            mes_cost=results['economics']['economies_of_scale']['volume_analysis'][2]['unit_cost'] if len(results['economics']['economies_of_scale']['volume_analysis']) > 2 else 0,
            total_cap=results['economics']['capital_requirements']['total_required'],
            peak_cash=results['economics']['capital_requirements']['peak_cash_requirement'],
            risk_table=self._format_risk_table(results['integrated_risk']['risk_factors']),
            mitigation_budget=results['integrated_risk']['risk_mitigation_budget'],
            recommendations=self._format_recommendations(results['recommendations']),
            p95_delay=results['supply_chain']['monte_carlo']['p95_delay'],
            mean_recovery=results['supply_chain']['monte_carlo']['mean_recovery_time'],
            multi_disrupt=1 - (1 - results['supply_chain']['monte_carlo']['disruption_probability']) ** 2
        )
        
        return report
    
    def _format_team_table(self, hires: List[Dict]) -> str:
        """Format team requirements table"""
        lines = ["| Role | Timeline | Scarcity | Annual Cost |"]
        lines.append("|------|----------|----------|-------------|")
        for h in hires:
            lines.append(f"| {h['role']} | {h['timeline']} | {h['scarcity']:.0%} | ${self.human_tech._get_role_salary(h['role']):,} |")
        return '\n'.join(lines)
    
    def _format_risk_table(self, factors: List[Dict]) -> str:
        """Format risk factor table"""
        lines = ["| Category | Factor | Score | Weight |"]
        lines.append("|----------|--------|-------|--------|")
        for f in factors:
            lines.append(f"| {f['category']} | {f['factor']} | {f['score']:.2f} | {f['weight']:.0%} |")
        return '\n'.join(lines)
    
    def _format_recommendations(self, recs: List[Dict]) -> str:
        """Format recommendations"""
        lines = []
        for r in recs:
            lines.append(f"\n### {r['priority']}: {r['recommendation']}")
            lines.append(f"- **Category**: {r['category']}")
            lines.append(f"- **Details**: {r['details']}")
            lines.append(f"- **Investment**: ${r['investment']:,}")
            lines.append(f"- **Timeline**: {r['timeline']}")
        return '\n'.join(lines)
    
    def plot_supply_chain_network(self, save_path: str = None):
        """Visualize supply chain network"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        G = self.supply_chain.network
        
        # Position nodes by tier
        pos = {}
        tier_positions = {
            SupplierTier.TIER_1_FOUNDRY: (0.2, 0.7),
            SupplierTier.TIER_1_MEMORY: (0.5, 0.7),
            SupplierTier.TIER_1_OSAT: (0.8, 0.7),
            SupplierTier.TIER_2_SUBSTRATE: (0.5, 0.3),
        }
        
        for node_name, node in self.supply_chain.nodes.items():
            tier = node.supplier.tier
            base_pos = tier_positions.get(tier, (0.5, 0.5))
            # Add some randomness
            pos[node_name] = (base_pos[0] + np.random.uniform(-0.1, 0.1),
                             base_pos[1] + np.random.uniform(-0.1, 0.1))
        
        # Node colors by geographic risk
        node_colors = []
        for node_name in G.nodes():
            risk = self.supply_chain.nodes[node_name].supplier.geographic_risk
            node_colors.append(plt.cm.RdYlGn_r(risk))
        
        # Node sizes by capacity
        node_sizes = []
        for node_name in G.nodes():
            capacity = self.supply_chain.nodes[node_name].supplier.capacity_units_per_month
            node_sizes.append(capacity / 500)
        
        # Draw network
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                               node_size=node_sizes, alpha=0.8)
        
        # Draw edges with width based on dependency
        for (u, v, data) in G.edges(data=True):
            width = data.get('dependency', 0.5) * 3
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)],
                                   width=width, alpha=0.6,
                                   connectionstyle="arc3,rad=0.1")
        
        # Labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
        
        # Legend
        legend_elements = [
            mpatches.Patch(color=plt.cm.RdYlGn_r(0.1), label='Low Geographic Risk'),
            mpatches.Patch(color=plt.cm.RdYlGn_r(0.5), label='Medium Geographic Risk'),
            mpatches.Patch(color=plt.cm.RdYlGn_r(0.9), label='High Geographic Risk'),
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        ax.set_title('Supply Chain Network - 28nm Mask-Locked Chip\nNode size = Capacity, Color = Geographic Risk', 
                     fontsize=12, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved supply chain network to {save_path}")
            
        return fig
    
    def plot_organizational_network(self, save_path: str = None):
        """Visualize organizational network"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        G = self.organization.network
        
        # Create hierarchical layout
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Node colors by department
        dept_colors = {
            'Executive': '#FF6B6B',
            'Engineering': '#4ECDC4',
            'Manufacturing': '#45B7D1',
            'Operations': '#96CEB4',
            'Quality': '#FFEAA7'
        }
        
        node_colors = [dept_colors.get(self.organization.nodes[n].department, '#CCCCCC') 
                       for n in G.nodes()]
        
        # Node sizes by decision authority
        node_sizes = [self.organization.nodes[n].decision_authority * 2000 + 500 
                      for n in G.nodes()]
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                               node_size=node_sizes, alpha=0.8)
        
        # Draw edges with colors by flow type
        flow_colors = {
            'decision': '#FF6B6B',
            'technical': '#4ECDC4',
            'coordination': '#45B7D1',
            'ip_sensitive': '#9B59B6'
        }
        
        for (u, v, data) in G.edges(data=True):
            flow_type = data.get('flow_type', 'coordination')
            color = flow_colors.get(flow_type, '#CCCCCC')
            width = data.get('frequency', 5) / 10
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)],
                                   width=width, alpha=0.6, edge_color=color,
                                   connectionstyle="arc3,rad=0.1")
        
        # Labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=7)
        
        # Legend
        legend_elements = [
            mpatches.Patch(color=flow_colors['decision'], label='Decision Flow'),
            mpatches.Patch(color=flow_colors['technical'], label='Technical Flow'),
            mpatches.Patch(color=flow_colors['coordination'], label='Coordination'),
            mpatches.Patch(color=flow_colors['ip_sensitive'], label='IP Sensitive'),
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        ax.set_title('Organizational Network - Information Flow\nNode size = Decision Authority', 
                     fontsize=12, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved organizational network to {save_path}")
            
        return fig
    
    def plot_economic_analysis(self, save_path: str = None):
        """Visualize economic analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Economies of Scale
        ax1 = axes[0, 0]
        scale_data = self.simulation_results['economics']['economies_of_scale']['volume_analysis']
        volumes = [d['volume'] for d in scale_data]
        costs = [d['unit_cost'] for d in scale_data]
        
        ax1.plot(volumes, costs, 'b-o', linewidth=2, markersize=8)
        ax1.axhline(y=min(costs) * 1.1, color='r', linestyle='--', label='MES threshold')
        ax1.set_xlabel('Production Volume (units)')
        ax1.set_ylabel('Unit Cost ($)')
        ax1.set_title('Economies of Scale')
        ax1.set_xscale('log')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Learning Curves
        ax2 = axes[0, 1]
        for component, data in self.simulation_results['economics']['learning_curves'].items():
            cumul = [d['cumulative_volume'] for d in data['curve_data']]
            avg_cost = [d['average_cost'] for d in data['curve_data']]
            ax2.plot(cumul, avg_cost, '-o', label=component, linewidth=2, markersize=6)
        
        ax2.set_xlabel('Cumulative Volume')
        ax2.set_ylabel('Average Cost ($)')
        ax2.set_title('Learning Curve Effects')
        ax2.set_xscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Cash Flow
        ax3 = axes[1, 0]
        cash_flow = self.simulation_results['economics']['capital_requirements']['monthly_cash_flow']
        months = [c['month'] for c in cash_flow]
        cumulative = [c['cumulative'] / 1_000_000 for c in cash_flow]
        monthly = [c['total'] / 1_000_000 for c in cash_flow]
        
        ax3.bar(months, monthly, alpha=0.7, label='Monthly Burn ($M)')
        ax3.plot(months, cumulative, 'r-', linewidth=2, label='Cumulative ($M)')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Cash ($M)')
        ax3.set_title('Capital Requirements Timeline')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Risk Distribution
        ax4 = axes[1, 1]
        risk_factors = self.simulation_results['integrated_risk']['risk_factors']
        categories = [f['category'] for f in risk_factors]
        scores = [f['score'] * f['weight'] for f in risk_factors]
        
        colors = plt.cm.RdYlGn_r(np.array(scores) / max(scores) if max(scores) > 0 else scores)
        ax4.barh(categories, scores, color=colors)
        ax4.set_xlabel('Weighted Risk Score')
        ax4.set_title('Risk Factor Analysis')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved economic analysis to {save_path}")
            
        return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function"""
    print("=" * 70)
    print("Cycle 13: Sociotechnical Manufacturing Systems Analysis")
    print("=" * 70)
    
    # Initialize simulation
    sim = SociotechnicalManufacturingSimulation()
    
    # Run full simulation
    print("\n[1/4] Running integrated simulation...")
    results = sim.run_full_simulation(n_monte_carlo=1000)
    
    # Generate report
    print("[2/4] Generating analysis report...")
    report = sim.generate_report()
    
    # Save report
    report_path = "/home/z/my-project/research/cycle13_sociotechnical.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to {report_path}")
    
    # Generate visualizations
    print("[3/4] Generating visualizations...")
    
    sim.plot_supply_chain_network(
        "/home/z/my-project/research/cycle13_supply_chain_network.png"
    )
    
    sim.plot_organizational_network(
        "/home/z/my-project/research/cycle13_organizational_network.png"
    )
    
    sim.plot_economic_analysis(
        "/home/z/my-project/research/cycle13_economic_analysis.png"
    )
    
    # Save simulation results as JSON
    print("[4/4] Saving simulation data...")
    
    # Convert results to JSON-serializable format
    json_results = {
        'supply_chain': {
            'delivery_reliability': results['supply_chain']['monte_carlo']['delivery_reliability'],
            'geographic_concentration': float(results['supply_chain']['resilience']['geographic_concentration']),
            'single_source_count': results['supply_chain']['resilience']['single_source_count'],
            'p95_delay': results['supply_chain']['monte_carlo']['p95_delay'],
            'mean_recovery_time': results['supply_chain']['monte_carlo']['mean_recovery_time']
        },
        'human_technology': {
            'error_rates': {k: v['total_error_rate'] for k, v in results['human_technology']['error_rates'].items()},
            'automation_recommendations': {k: v['recommendation'] for k, v in results['human_technology']['automation'].items()}
        },
        'organization': {
            'centralization': results['organization']['information_flow']['centralization'],
            'coordination_efficiency': results['organization']['information_flow']['coordination_efficiency'],
            'ip_protection_score': results['organization']['trust_network']['ip_protection_score'],
            'annual_coordination_cost': results['organization']['coordination_cost']['annual_coordination_cost']
        },
        'economics': {
            'scale_elasticity': results['economics']['economies_of_scale']['scale_elasticity'],
            'minimum_efficient_scale': results['economics']['economies_of_scale']['minimum_efficient_scale'],
            'total_capital_required': results['economics']['capital_requirements']['total_required'],
            'peak_cash_requirement': results['economics']['capital_requirements']['peak_cash_requirement']
        },
        'integrated_risk': {
            'total_risk_score': results['integrated_risk']['total_risk_score'],
            'risk_rating': results['integrated_risk']['risk_rating'],
            'risk_mitigation_budget': results['integrated_risk']['risk_mitigation_budget']
        },
        'recommendations_count': len(results['recommendations'])
    }
    
    json_path = "/home/z/my-project/research/cycle13_results.json"
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"Simulation data saved to {json_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"\nOverall Risk Rating: {results['integrated_risk']['risk_rating']}")
    print(f"Total Risk Score: {results['integrated_risk']['total_risk_score']:.2f}")
    print(f"\nSupply Chain:")
    print(f"  - Delivery Reliability: {results['supply_chain']['monte_carlo']['delivery_reliability']:.1%}")
    print(f"  - Geographic Concentration: {results['supply_chain']['resilience']['geographic_concentration']:.1%}")
    print(f"\nHuman Capital:")
    print(f"  - Critical Hires Required: {len(results['human_technology']['team_requirements']['critical_hires'])}")
    print(f"\nEconomics:")
    print(f"  - Total Capital Required: ${results['economics']['capital_requirements']['total_required']:,.0f}")
    print(f"  - Minimum Efficient Scale: {results['economics']['economies_of_scale']['minimum_efficient_scale']:,} units")
    print(f"\nRecommendations Generated: {len(results['recommendations'])}")
    print("=" * 70)
    
    return sim, results


if __name__ == "__main__":
    sim, results = main()
