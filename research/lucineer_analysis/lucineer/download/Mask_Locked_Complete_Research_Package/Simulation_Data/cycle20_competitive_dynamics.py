#!/usr/bin/env python3
"""
Cycle 20: Competitive Dynamics and Market Response Analysis
for Mask-Locked Inference Chip

This simulation analyzes competitive dynamics using game theory,
market evolution modeling, and strategic response analysis.

Key components:
1. Competitor Response Modeling: NVIDIA, Google, Intel, Qualcomm, Startups
2. Market Dynamics Game Theory: Prisoner's Dilemma, Stackelberg, etc.
3. Technology Roadmap Timing Analysis
4. Defensive Strategy Optimization
5. Scenario Analysis: Bull/Base/Bear/Black Swan
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, linprog
from scipy.stats import truncnorm, beta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# GLOBAL PARAMETERS - Market and Competition
# =============================================================================

# Market parameters (from previous research)
EDGE_AI_TAM_2025 = 3.67  # $B
EDGE_AI_TAM_2030 = 11.54  # $B
CAGR = 0.257  # 25.7% CAGR

# SuperInstance parameters
SUPERINSTANCE_PRICE = 49  # $ per unit
SUPERINSTANCE_COGS = 34  # $ per unit
SUPERINSTANCE_MARGIN = 0.31  # 31% gross margin
FIRST_MOVER_WINDOW_MONTHS = 24  # First-mover advantage window

# Simulation time horizon
SIMULATION_YEARS = 5
TIME_STEPS = 60  # Monthly time steps

# =============================================================================
# DATA CLASSES FOR COMPETITORS AND MARKET
# =============================================================================

class CompetitorType(Enum):
    TIER1_INCUMBENT = "tier1_incumbent"  # NVIDIA, Intel
    TIER1_STRATEGIC = "tier1_strategic"  # Google, Qualcomm
    STARTUP_WELLFUNDED = "startup_wellfunded"  # Etched, Taalas
    STARTUP_NICHE = "startup_niche"  # Hailo, Groq

@dataclass
class Competitor:
    """Represents a competitor in the edge AI market."""
    name: str
    competitor_type: CompetitorType
    market_share_2025: float  # Current market share (0-1)
    technology_level: float  # 0-1 relative to state-of-art
    funding_b: float  # Funding in $B
    reaction_speed: float  # 0-1, how fast they respond
    innovation_rate: float  # 0-1, R&D effectiveness
    price_aggressiveness: float  # 0-1, willingness to cut prices
    niche_overlap: float  # 0-1, overlap with SuperInstance niche
    strategic_priority: float  # 0-1, importance of edge AI to them
    
    # Derived attributes
    response_threshold: float = 0.0  # Market share that triggers response
    capability_gap: float = 0.0  # Technology gap to SuperInstance

# =============================================================================
# COMPETITOR DATABASE
# =============================================================================

def create_competitor_database() -> Dict[str, Competitor]:
    """Create database of all relevant competitors."""
    
    competitors = {
        'NVIDIA': Competitor(
            name='NVIDIA',
            competitor_type=CompetitorType.TIER1_INCUMBENT,
            market_share_2025=0.85,  # 85% of edge AI GPU market
            technology_level=0.95,
            funding_b=65.0,  # Cash on hand
            reaction_speed=0.7,
            innovation_rate=0.9,
            price_aggressiveness=0.3,  # Premium positioning
            niche_overlap=0.3,  # Jetson overlaps partially
            strategic_priority=0.4,  # Focus on datacenter
        ),
        'Google': Competitor(
            name='Google',
            competitor_type=CompetitorType.TIER1_STRATEGIC,
            market_share_2025=0.05,  # TPU/Coral limited
            technology_level=0.90,
            funding_b=110.0,
            reaction_speed=0.5,
            innovation_rate=0.85,
            price_aggressiveness=0.4,
            niche_overlap=0.25,  # Coral overlaps
            strategic_priority=0.3,  # Focus on cloud
        ),
        'Intel': Competitor(
            name='Intel',
            competitor_type=CompetitorType.TIER1_INCUMBENT,
            market_share_2025=0.03,  # NPU/Mobileye
            technology_level=0.75,
            funding_b=25.0,
            reaction_speed=0.4,
            innovation_rate=0.5,
            price_aggressiveness=0.6,
            niche_overlap=0.2,
            strategic_priority=0.5,  # Seeking growth
        ),
        'Qualcomm': Competitor(
            name='Qualcomm',
            competitor_type=CompetitorType.TIER1_STRATEGIC,
            market_share_2025=0.04,  # AI Engine
            technology_level=0.85,
            funding_b=15.0,
            reaction_speed=0.8,
            innovation_rate=0.8,
            price_aggressiveness=0.5,
            niche_overlap=0.35,  # Significant overlap
            strategic_priority=0.7,  # Mobile + Edge
        ),
        'Taalas': Competitor(
            name='Taalas',
            competitor_type=CompetitorType.STARTUP_WELLFUNDED,
            market_share_2025=0.0,  # Pre-product
            technology_level=0.8,  # Promising but unproven
            funding_b=0.219,  # $219M raised
            reaction_speed=0.9,
            innovation_rate=0.85,
            price_aggressiveness=0.7,
            niche_overlap=0.9,  # Direct competitor
            strategic_priority=1.0,  # Core business
        ),
        'Etched': Competitor(
            name='Etched',
            competitor_type=CompetitorType.STARTUP_WELLFUNDED,
            market_share_2025=0.0,
            technology_level=0.85,
            funding_b=0.620,  # $120M + $500M
            reaction_speed=0.7,
            innovation_rate=0.9,
            price_aggressiveness=0.6,
            niche_overlap=0.5,  # Transformer-focused
            strategic_priority=1.0,
        ),
        'Hailo': Competitor(
            name='Hailo',
            competitor_type=CompetitorType.STARTUP_NICHE,
            market_share_2025=0.02,
            technology_level=0.80,
            funding_b=0.350,
            reaction_speed=0.6,
            innovation_rate=0.7,
            price_aggressiveness=0.5,
            niche_overlap=0.7,  # Direct edge AI
            strategic_priority=1.0,
        ),
        'Groq': Competitor(
            name='Groq',
            competitor_type=CompetitorType.STARTUP_NICHE,
            market_share_2025=0.01,
            technology_level=0.88,
            funding_b=0.350,  # Before NVIDIA acquisition
            reaction_speed=0.8,
            innovation_rate=0.85,
            price_aggressiveness=0.4,
            niche_overlap=0.4,  # Inference-focused
            strategic_priority=1.0,
        ),
    }
    
    # Calculate derived attributes
    for name, comp in competitors.items():
        # Response threshold: larger companies need bigger threat
        if comp.competitor_type == CompetitorType.TIER1_INCUMBENT:
            comp.response_threshold = 0.05  # 5% market share
        elif comp.competitor_type == CompetitorType.TIER1_STRATEGIC:
            comp.response_threshold = 0.03
        else:
            comp.response_threshold = 0.01  # Startups react to any threat
            
        # Capability gap relative to SuperInstance mask-locked approach
        # SuperInstance has novel architecture, so gap is positive for incumbents
        comp.capability_gap = 1.0 - comp.technology_level + 0.1 * (1 - comp.niche_overlap)
    
    return competitors


# =============================================================================
# PART 1: COMPETITOR RESPONSE MODELING
# =============================================================================

class CompetitorResponseModel:
    """
    Model how competitors respond to SuperInstance market entry.
    
    Response types:
    1. Price Competition: Cut prices to maintain share
    2. Product Enhancement: Accelerate R&D
    3. Market Segmentation: Focus on different segments
    4. Acquisition: Buy competitors
    5. Litigation: Patent attacks
    """
    
    def __init__(self, competitors: Dict[str, Competitor]):
        self.competitors = competitors
        
    def response_probability(self, competitor: Competitor, 
                            superinstance_share: float,
                            time_elapsed_months: int) -> Dict[str, float]:
        """
        Calculate probability of each response type.
        
        Returns dict mapping response_type -> probability
        """
        # Base probability of any response
        base_prob = min(1.0, superinstance_share / competitor.response_threshold)
        
        # Adjust for time (earlier = less certain response)
        time_factor = 1 - np.exp(-time_elapsed_months / 12)
        
        # Adjust for strategic priority
        priority_factor = competitor.strategic_priority
        
        # Adjust for niche overlap
        overlap_factor = competitor.niche_overlap
        
        # Combined response probability
        response_prob = base_prob * time_factor * priority_factor * overlap_factor
        
        # Distribute across response types
        responses = {
            'price_cut': response_prob * competitor.price_aggressiveness * 0.5,
            'product_enhancement': response_prob * competitor.innovation_rate * 0.8,
            'market_segmentation': response_prob * (1 - competitor.niche_overlap) * 0.6,
            'acquisition': response_prob * (competitor.funding_b / 10) * 0.1,
            'litigation': response_prob * (1 - competitor.innovation_rate) * 0.2,
            'ignore': 1 - response_prob
        }
        
        # Normalize
        total = sum(responses.values())
        return {k: v/total for k, v in responses.items()}
    
    def response_impact(self, competitor: Competitor, 
                       response_type: str,
                       superinstance_share: float) -> Dict[str, float]:
        """
        Calculate impact of competitor response on SuperInstance.
        
        Returns: {
            'market_share_loss': float,
            'price_pressure': float,
            'innovation_pressure': float,
            'legal_cost': float
        }
        """
        impact = {
            'market_share_loss': 0.0,
            'price_pressure': 0.0,
            'innovation_pressure': 0.0,
            'legal_cost': 0.0
        }
        
        if response_type == 'price_cut':
            # Price war impact
            impact['market_share_loss'] = 0.02 * competitor.market_share_2025
            impact['price_pressure'] = 0.1 * competitor.price_aggressiveness
            
        elif response_type == 'product_enhancement':
            # R&D competition
            impact['market_share_loss'] = 0.01 * competitor.innovation_rate
            impact['innovation_pressure'] = 0.2 * competitor.innovation_rate
            
        elif response_type == 'market_segmentation':
            # Competitor retreats to other segments
            impact['market_share_loss'] = -0.005  # SuperInstance gains
            
        elif response_type == 'acquisition':
            # Competitor buys rivals
            impact['market_share_loss'] = 0.03
            impact['innovation_pressure'] = 0.1
            
        elif response_type == 'litigation':
            # Patent/legal attack
            impact['legal_cost'] = 0.5  # $500K typical defense
            impact['market_share_loss'] = 0.01
            
        return impact
    
    def simulate_competitive_response(self, 
                                     superinstance_share_trajectory: np.ndarray,
                                     time_months: np.ndarray) -> Dict:
        """Simulate competitor responses over time."""
        
        results = {
            'responses': {},
            'cumulative_impact': {
                'market_share_loss': np.zeros(len(time_months)),
                'price_pressure': np.zeros(len(time_months)),
                'innovation_pressure': np.zeros(len(time_months)),
                'legal_cost': np.zeros(len(time_months))
            }
        }
        
        for name, comp in self.competitors.items():
            comp_responses = []
            
            for t, (share, month) in enumerate(zip(superinstance_share_trajectory, time_months)):
                probs = self.response_probability(comp, share, month)
                
                # Sample response
                response = np.random.choice(
                    list(probs.keys()),
                    p=list(probs.values())
                )
                
                impact = self.response_impact(comp, response, share)
                
                comp_responses.append({
                    'month': month,
                    'response': response,
                    'impact': impact
                })
                
                # Accumulate impacts
                for key in results['cumulative_impact']:
                    if key in impact:
                        results['cumulative_impact'][key][t] += impact[key]
            
            results['responses'][name] = comp_responses
        
        return results


# =============================================================================
# PART 2: MARKET DYNAMICS GAME THEORY
# =============================================================================

class MarketGameTheory:
    """
    Game-theoretic analysis of market dynamics.
    
    Games analyzed:
    1. Prisoner's Dilemma: Price war vs innovation
    2. Stackelberg Competition: First-mover advantage
    3. Differentiation Game: Positioning strategies
    4. Network Effects Game: Ecosystem competition
    """
    
    def __init__(self):
        self.strategies = {
            'superinstance': ['innovate', 'price_compete', 'differentiate', 'partner'],
            'competitor': ['innovate', 'price_compete', 'differentiate', 'ignore']
        }
        
    def prisoners_dilemma_payoff(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prisoner's Dilemma for Price War vs Innovation.
        
        Payoff structure:
        - Both innovate: High profits, market grows
        - Both price compete: Low profits, market stagnant
        - One innovates, other price competes: Price competitor gains share
        
        Returns: (superinstance_payoff_matrix, competitor_payoff_matrix)
        """
        # Payoffs: (SuperInstance, Competitor)
        # Strategies: [Innovate, Price Compete]
        
        # Base profits
        base_profit = 1.0
        innovation_cost = 0.2
        price_war_cost = 0.4
        market_growth = 0.3
        
        payoff_si = np.array([
            [base_profit + market_growth - innovation_cost, base_profit - price_war_cost],
            [base_profit + price_war_cost * 0.5, base_profit - price_war_cost - innovation_cost * 0.3]
        ])
        
        payoff_comp = np.array([
            [base_profit + market_growth - innovation_cost, base_profit - price_war_cost],
            [base_profit - price_war_cost - innovation_cost * 0.3, base_profit - price_war_cost]
        ])
        
        return payoff_si, payoff_comp
    
    def find_nash_equilibrium(self, payoff1: np.ndarray, payoff2: np.ndarray) -> Dict:
        """Find Nash equilibrium in mixed strategies."""
        n_strategies = payoff1.shape[0]
        
        # Best response dynamics
        p1 = np.ones(n_strategies) / n_strategies
        p2 = np.ones(n_strategies) / n_strategies
        
        for _ in range(1000):
            # Player 1 best response
            expected1 = payoff1 @ p2
            br1 = np.zeros(n_strategies)
            br1[np.argmax(expected1)] = 1.0
            p1 = 0.99 * p1 + 0.01 * br1
            
            # Player 2 best response
            expected2 = payoff2.T @ p1
            br2 = np.zeros(n_strategies)
            br2[np.argmax(expected2)] = 1.0
            p2 = 0.99 * p2 + 0.01 * br2
        
        return {
            'p1_mixed_strategy': p1,
            'p2_mixed_strategy': p2,
            'p1_expected_payoff': p1 @ payoff1 @ p2,
            'p2_expected_payoff': p1 @ payoff2 @ p2,
            'is_pure_equilibrium': np.max(p1) > 0.99 or np.max(p2) > 0.99
        }
    
    def stackelberg_competition(self, 
                               first_mover_advantage: float = 0.3,
                               market_size: float = 1.0) -> Dict:
        """
        Stackelberg competition with SuperInstance as first mover.
        
        First mover commits to quantity/capacity, follower responds.
        """
        # First mover (SuperInstance) chooses quantity q1
        # Follower (Competitor) chooses q2 after observing q1
        
        # Inverse demand: P = a - b*(q1 + q2)
        a = 1.0  # Maximum price
        b = 0.5  # Price sensitivity
        
        # Costs
        c_si = 0.3  # SuperInstance marginal cost
        c_comp = 0.4  # Competitor marginal cost (higher)
        
        # Solve by backward induction
        # Follower's best response: q2 = (a - c2 - b*q1) / (2*b)
        # First mover maximizes: pi1 = (a - b*(q1 + q2)) * q1 - c1 * q1
        
        def follower_response(q1):
            return max(0, (a - c_comp - b * q1) / (2 * b))
        
        def first_mover_profit(q1):
            q2 = follower_response(q1)
            price = a - b * (q1 + q2)
            return (price - c_si) * q1
        
        # Optimize first mover quantity
        result = minimize(lambda q: -first_mover_profit(q[0]), 
                         [0.5], bounds=[(0, 2)])
        q1_opt = result.x[0]
        q2_opt = follower_response(q1_opt)
        
        # Calculate payoffs
        price_eq = a - b * (q1_opt + q2_opt)
        profit_si = (price_eq - c_si) * q1_opt
        profit_comp = (price_eq - c_comp) * q2_opt
        
        # Apply first mover advantage
        profit_si *= (1 + first_mover_advantage)
        
        return {
            'q_first_mover': q1_opt,
            'q_follower': q2_opt,
            'equilibrium_price': price_eq,
            'profit_first_mover': profit_si,
            'profit_follower': profit_comp,
            'market_share_first_mover': q1_opt / (q1_opt + q2_opt) if q1_opt + q2_opt > 0 else 0,
            'first_mover_advantage': first_mover_advantage
        }
    
    def differentiation_game(self) -> Dict:
        """
        Product differentiation game.
        
        Strategies:
        - Cost Leadership: Lower price, basic features
        - Differentiation: Premium features, higher price
        - Focus: Niche market segment
        """
        strategies = ['cost_leadership', 'differentiation', 'focus']
        n = len(strategies)
        
        # Payoff matrices (SuperInstance x Competitor)
        # Higher values = better outcome
        
        payoff_si = np.array([
            [0.4, 0.5, 0.6],  # SI: Cost Leadership
            [0.6, 0.3, 0.5],  # SI: Differentiation
            [0.7, 0.6, 0.4]   # SI: Focus (mask-locked niche)
        ])
        
        payoff_comp = np.array([
            [0.3, 0.6, 0.5],  # Comp: Cost Leadership
            [0.5, 0.4, 0.6],  # Comp: Differentiation
            [0.4, 0.5, 0.3]   # Comp: Focus
        ])
        
        nash = self.find_nash_equilibrium(payoff_si, payoff_comp)
        
        return {
            'strategies': strategies,
            'payoff_si': payoff_si,
            'payoff_comp': payoff_comp,
            'nash_equilibrium': nash,
            'optimal_si_strategy': strategies[np.argmax(nash['p1_mixed_strategy'])],
            'optimal_comp_strategy': strategies[np.argmax(nash['p2_mixed_strategy'])]
        }
    
    def network_effects_game(self, 
                            superinstance_users: int = 0,
                            competitor_users: int = 1000,
                            network_strength: float = 0.1) -> Dict:
        """
        Network effects in developer ecosystem.
        
        Value to user = standalone_value + network_strength * log(users)
        """
        standalone_si = 1.0  # Superior hardware
        standalone_comp = 0.7
        
        def value_si(users_si):
            return standalone_si + network_strength * np.log(users_si + 1)
        
        def value_comp(users_comp):
            return standalone_comp + network_strength * np.log(users_comp + 1)
        
        # Simulate user growth with network effects
        months = np.arange(60)
        users_si = np.zeros(60)
        users_comp = np.zeros(60)
        
        users_si[0] = superinstance_users
        users_comp[0] = competitor_users
        
        for t in range(1, 60):
            # User acquisition rate proportional to value differential
            v_si = value_si(users_si[t-1])
            v_comp = value_comp(users_comp[t-1])
            
            total_value = v_si + v_comp
            
            # New users this month (market growth)
            new_users = 100 * (1.02 ** t)  # 2% monthly growth
            
            # Split by value
            users_si[t] = users_si[t-1] + new_users * (v_si / total_value)
            users_comp[t] = users_comp[t-1] + new_users * (v_comp / total_value)
        
        return {
            'months': months,
            'users_si': users_si,
            'users_comp': users_comp,
            'value_si': value_si(users_si[-1]),
            'value_comp': value_comp(users_comp[-1]),
            'network_tipping_point': network_strength / (standalone_si - standalone_comp) if standalone_si > standalone_comp else None
        }


# =============================================================================
# PART 3: TECHNOLOGY ROADMAP TIMING
# =============================================================================

class TechnologyRoadmapTiming:
    """
    Analyze optimal timing for technology transitions and product launches.
    
    Factors:
    - First-mover advantage window
    - Patent cliff timing
    - Process node transitions
    - Competitor product cycles
    """
    
    def __init__(self):
        self.process_nodes = {
            '28nm': {'maturity': 0.9, 'cost_per_mm2': 0.15, 'availability': 0.95},
            '22nm': {'maturity': 0.85, 'cost_per_mm2': 0.18, 'availability': 0.90},
            '14nm': {'maturity': 0.7, 'cost_per_mm2': 0.25, 'availability': 0.70},
            '7nm': {'maturity': 0.4, 'cost_per_mm2': 0.45, 'availability': 0.40}
        }
        
        self.patent_cliff_years = {
            'iFairy': 2040,  # Apache 2.0, no cliff
            'BitNet': 2040,  # MIT, no cliff
            'NVIDIA': 2035,  # Key patents expire
            'TSMC_28nm': 2028  # Process patents
        }
        
    def first_mover_window_analysis(self, 
                                    competitor_reaction_months: int = 18,
                                    development_months: int = 30) -> Dict:
        """
        Analyze first-mover advantage window.
        """
        # Time to market for SuperInstance
        ttm_si = development_months
        
        # Time for competitor to respond
        # Includes: detection, decision, development, production
        ttm_response = competitor_reaction_months
        
        # First mover window
        window = max(0, ttm_response)
        
        # Market share captured during window
        monthly_market_growth = 0.02
        market_during_window = (1 + monthly_market_growth) ** window - 1
        
        # First mover advantage coefficient
        # Decreases exponentially with time as competitors catch up
        fma_coefficient = 0.3 * np.exp(-window / 24)  # 30% initial, decays over 24 months
        
        return {
            'time_to_market_si': ttm_si,
            'competitor_response_time': ttm_response,
            'first_mover_window_months': window,
            'market_capture_during_window': market_during_window,
            'first_mover_advantage_coefficient': fma_coefficient,
            'recommended_launch_timing': 'asap' if window > 12 else 'strategic'
        }
    
    def process_node_transition_analysis(self, 
                                        die_area_mm2: float = 25,
                                        volume_k: float = 100) -> Dict:
        """
        Analyze optimal process node for production.
        """
        results = {}
        
        for node, specs in self.process_nodes.items():
            # Cost calculation
            wafer_cost = specs['cost_per_mm2'] * 700  # Approximate wafer area
            dies_per_wafer = 700 / die_area_mm2 * 0.8  # 80% yield
            cost_per_die = wafer_cost / dies_per_wafer
            
            # Total cost for volume
            total_cost = cost_per_die * volume_k * 1000
            
            # Risk assessment
            risk = (1 - specs['maturity']) * (1 - specs['availability'])
            
            results[node] = {
                'cost_per_die': cost_per_die,
                'total_cost': total_cost,
                'risk_score': risk,
                'availability_score': specs['availability'],
                'maturity_score': specs['maturity'],
                'expected_yield': specs['maturity'] * 0.85  # Adjusted yield
            }
        
        # Find optimal node
        # Weight cost vs risk
        scores = {
            node: (1 - r['risk_score']) * 0.6 + (1 - r['cost_per_die']/0.5) * 0.4
            for node, r in results.items()
        }
        optimal_node = max(scores, key=scores.get)
        
        return {
            'node_analysis': results,
            'optimal_node': optimal_node,
            'scores': scores
        }
    
    def patent_cliff_timing(self) -> Dict:
        """
        Analyze patent landscape timing for strategic decisions.
        """
        current_year = 2025
        
        cliffs = []
        for patent_holder, expiry_year in self.patent_cliff_years.items():
            years_to_expiry = expiry_year - current_year
            
            if years_to_expiry > 0:
                impact = 'low' if years_to_expiry > 10 else ('medium' if years_to_expiry > 5 else 'high')
            else:
                impact = 'expired'
            
            cliffs.append({
                'holder': patent_holder,
                'expiry_year': expiry_year,
                'years_to_expiry': years_to_expiry,
                'impact': impact,
                'opportunity': years_to_expiry < 5 and patent_holder != 'iFairy'
            })
        
        return {
            'patent_cliffs': cliffs,
            'strategic_window': any(c['opportunity'] for c in cliffs),
            'fto_improvement_timeline': min(c['years_to_expiry'] for c in cliffs if c['years_to_expiry'] > 0)
        }


# =============================================================================
# PART 4: DEFENSIVE STRATEGIES
# =============================================================================

class DefensiveStrategies:
    """
    Analyze and optimize defensive strategies for SuperInstance.
    
    Strategies:
    1. Patent Fortress: Build patent portfolio
    2. Ecosystem Lock-in: SDK, tools, community
    3. Customer Moats: Relationships, switching costs
    4. Open Source: Defensive publication
    """
    
    def __init__(self, initial_budget: float = 2.0):  # $2M budget
        self.budget = initial_budget
        
    def patent_fortress_optimization(self) -> Dict:
        """
        Optimize patent portfolio investment.
        
        Categories:
        - Core patents: Protect key innovations
        - Defensive patents: Block competitors
        - Licensing patents: Revenue potential
        """
        categories = {
            'core': {
                'patents': 5,
                'cost_per_patent': 25,  # $K
                'protection_value': 500,  # $K
                'defense_value': 300
            },
            'defensive': {
                'patents': 15,
                'cost_per_patent': 15,
                'protection_value': 200,
                'defense_value': 400
            },
            'licensing': {
                'patents': 10,
                'cost_per_patent': 20,
                'protection_value': 100,
                'defense_value': 150,
                'licensing_revenue': 50  # $K/year
            }
        }
        
        # Optimize allocation
        total_cost = sum(
            cat['patents'] * cat['cost_per_patent'] 
            for cat in categories.values()
        )
        
        total_value = sum(
            cat['protection_value'] + cat['defense_value'] + 
            cat.get('licensing_revenue', 0) * 5  # 5-year NPV
            for cat in categories.values()
        )
        
        roi = (total_value - total_cost) / total_cost
        
        return {
            'categories': categories,
            'total_patents': sum(c['patents'] for c in categories.values()),
            'total_cost_k': total_cost,
            'total_value_k': total_value,
            'roi': roi,
            'recommendation': 'invest' if roi > 3 else 'selective'
        }
    
    def ecosystem_lockin_analysis(self, 
                                  sdk_investment: float = 200,
                                  tools_investment: float = 100,
                                  community_investment: float = 150) -> Dict:
        """
        Analyze ecosystem lock-in strategy.
        
        Lock-in mechanisms:
        - SDK quality and completeness
        - Developer tools integration
        - Community engagement
        - Educational content
        """
        # SDK investment impact
        sdk_quality = min(1.0, sdk_investment / 300)  # $300K for top quality
        sdk_switching_cost = sdk_quality * 0.3  # 30% switching cost at max quality
        
        # Tools investment impact
        tools_integration = min(1.0, tools_investment / 150)
        tools_lockin = tools_integration * 0.2
        
        # Community investment impact
        community_reach = min(1.0, community_investment / 200)
        community_network_effect = community_reach * 0.25
        
        # Combined lock-in
        total_investment = sdk_investment + tools_investment + community_investment
        lockin_coefficient = sdk_switching_cost + tools_lockin + community_network_effect
        
        # Customer retention impact
        base_retention = 0.7
        retention_with_lockin = base_retention + lockin_coefficient * 0.5
        
        return {
            'total_investment_k': total_investment,
            'sdk_quality': sdk_quality,
            'tools_integration': tools_integration,
            'community_reach': community_reach,
            'lockin_coefficient': lockin_coefficient,
            'customer_retention': retention_with_lockin,
            'switching_cost_to_competitor': lockin_coefficient,
            'roi': (retention_with_lockin - base_retention) * 10 / (total_investment / 1000)
        }
    
    def customer_moat_analysis(self,
                               enterprise_ratio: float = 0.3,
                               design_win_cycle_months: int = 9) -> Dict:
        """
        Analyze customer relationship moats.
        
        Enterprise design wins create strong moats due to:
        - Long qualification cycles
        - Technical integration
        - Trust building
        """
        # Time-value of design wins
        design_win_value = {
            'enterprise': 50,  # $K LTV
            'smb': 10,
            'hobbyist': 1
        }
        
        # Switching costs
        switching_costs = {
            'enterprise': 0.4,  # 40% of LTV
            'smb': 0.2,
            'hobbyist': 0.05
        }
        
        # Calculate moat strength
        segments = ['enterprise', 'smb', 'hobbyist']
        mix = [enterprise_ratio, 1 - enterprise_ratio - 0.3, 0.3]
        
        moat_strength = sum(
            mix[i] * switching_costs[segments[i]]
            for i in range(3)
        )
        
        # Design win timeline moat
        timeline_moat = min(1.0, design_win_cycle_months / 12)
        
        return {
            'customer_mix': dict(zip(segments, mix)),
            'moat_strength': moat_strength,
            'timeline_moat': timeline_moat,
            'avg_ltv_k': sum(mix[i] * design_win_value[segments[i]] for i in range(3)),
            'design_win_cycle_months': design_win_cycle_months,
            'recommendation': 'focus_enterprise' if enterprise_ratio < 0.4 else 'balance'
        }
    
    def open_source_strategy(self, 
                            core_open: bool = False,
                            sdk_open: bool = True,
                            tools_open: bool = True) -> Dict:
        """
        Analyze open-source defensive strategy.
        
        Benefits:
        - Defensive publication (prior art)
        - Community adoption
        - Ecosystem growth
        
        Risks:
        - Competitor copying
        - Revenue cannibalization
        """
        benefits = 0
        risks = 0
        
        # Core IP open source
        if core_open:
            benefits += 0.2  # Prior art benefit
            risks += 0.5  # High copy risk
        
        # SDK open source
        if sdk_open:
            benefits += 0.4  # Adoption boost
            risks += 0.1  # Low copy risk
        
        # Tools open source
        if tools_open:
            benefits += 0.3  # Community building
            risks += 0.1
        
        net_benefit = benefits - risks
        
        # Community growth factor
        community_growth = (1 + benefits) ** 12 - 1  # 12-month projection
        
        return {
            'core_open': core_open,
            'sdk_open': sdk_open,
            'tools_open': tools_open,
            'total_benefit': benefits,
            'total_risk': risks,
            'net_benefit': net_benefit,
            'community_growth_potential': community_growth,
            'recommendation': 'hybrid' if not core_open else 'full_open'
        }


# =============================================================================
# PART 5: SCENARIO ANALYSIS
# =============================================================================

class ScenarioAnalysis:
    """
    Simulate market evolution under different scenarios.
    
    Scenarios:
    - Bull: Competitors ignore niche, SuperInstance dominates
    - Base: Targeted competition from startups
    - Bear: NVIDIA launches competing product
    - Black Swan: Major breakthrough by competitor
    """
    
    def __init__(self, competitors: Dict[str, Competitor]):
        self.competitors = competitors
        
    def simulate_scenario(self, 
                         scenario: str,
                         years: int = 5) -> Dict:
        """
        Run Monte Carlo simulation for a given scenario.
        """
        months = years * 12
        
        # Scenario parameters
        params = {
            'bull': {
                'competitor_response_prob': 0.1,
                'market_growth_rate': 0.35,
                'superinstance_advantage': 0.8,
                'price_pressure': 0.05
            },
            'base': {
                'competitor_response_prob': 0.4,
                'market_growth_rate': 0.25,
                'superinstance_advantage': 0.5,
                'price_pressure': 0.15
            },
            'bear': {
                'competitor_response_prob': 0.8,
                'market_growth_rate': 0.20,
                'superinstance_advantage': 0.2,
                'price_pressure': 0.35
            },
            'black_swan': {
                'competitor_response_prob': 0.9,
                'market_growth_rate': 0.15,
                'superinstance_advantage': -0.1,
                'price_pressure': 0.50,
                'disruption_event': True
            }
        }
        
        p = params[scenario]
        
        # Initialize trajectories
        market_size = np.zeros(months + 1)
        market_size[0] = EDGE_AI_TAM_2025
        
        superinstance_share = np.zeros(months + 1)
        superinstance_share[0] = 0.001  # Start at 0.1%
        
        revenue = np.zeros(months + 1)
        price = np.zeros(months + 1)
        price[0] = SUPERINSTANCE_PRICE
        
        # Simulate
        for t in range(1, months + 1):
            # Market growth
            market_size[t] = market_size[t-1] * (1 + p['market_growth_rate'] / 12)
            
            # SuperInstance share growth (logistic)
            growth_rate = 0.1 * p['superinstance_advantage']
            share_growth = growth_rate * superinstance_share[t-1] * (1 - superinstance_share[t-1] / 0.3)
            
            # Competitor response reduces growth
            if np.random.random() < p['competitor_response_prob']:
                share_growth *= 0.5
            
            superinstance_share[t] = superinstance_share[t-1] + share_growth / 12
            superinstance_share[t] = max(0, min(0.5, superinstance_share[t]))  # Cap at 50%
            
            # Price pressure
            price[t] = price[t-1] * (1 - p['price_pressure'] / 12)
            price[t] = max(SUPERINSTANCE_COGS * 1.2, price[t])  # Floor at 20% margin
            
            # Revenue
            revenue[t] = market_size[t] * 1e9 * superinstance_share[t] * price[t] / SUPERINSTANCE_PRICE
        
        # Calculate outcomes
        cumulative_revenue = revenue.sum()
        final_share = superinstance_share[-1]
        avg_price = price.mean()
        final_market_cap = market_size[-1]
        
        return {
            'scenario': scenario,
            'months': np.arange(months + 1),
            'market_size': market_size,
            'superinstance_share': superinstance_share,
            'revenue': revenue,
            'price': price,
            'cumulative_revenue': cumulative_revenue,
            'final_share': final_share,
            'avg_price': avg_price,
            'final_market_size': final_market_cap,
            'parameters': p
        }
    
    def monte_carlo_simulation(self, 
                              scenario: str,
                              n_simulations: int = 1000) -> Dict:
        """
        Run Monte Carlo simulation for risk assessment.
        """
        results = []
        
        for _ in range(n_simulations):
            np.random.seed()  # Random seed for each simulation
            result = self.simulate_scenario(scenario)
            results.append({
                'cumulative_revenue': result['cumulative_revenue'],
                'final_share': result['final_share'],
                'avg_price': result['avg_price']
            })
        
        revenues = [r['cumulative_revenue'] for r in results]
        shares = [r['final_share'] for r in results]
        prices = [r['avg_price'] for r in results]
        
        return {
            'scenario': scenario,
            'n_simulations': n_simulations,
            'revenue_stats': {
                'mean': np.mean(revenues),
                'std': np.std(revenues),
                'p5': np.percentile(revenues, 5),
                'p50': np.percentile(revenues, 50),
                'p95': np.percentile(revenues, 95)
            },
            'share_stats': {
                'mean': np.mean(shares),
                'std': np.std(shares),
                'p5': np.percentile(shares, 5),
                'p50': np.percentile(shares, 50),
                'p95': np.percentile(shares, 95)
            },
            'price_stats': {
                'mean': np.mean(prices),
                'std': np.std(prices),
                'p5': np.percentile(prices, 5),
                'p50': np.percentile(prices, 50),
                'p95': np.percentile(prices, 95)
            }
        }
    
    def run_all_scenarios(self, n_simulations: int = 100) -> Dict:
        """Run all scenarios and compare."""
        scenarios = ['bull', 'base', 'bear', 'black_swan']
        
        results = {}
        for scenario in scenarios:
            results[scenario] = {
                'trajectory': self.simulate_scenario(scenario),
                'monte_carlo': self.monte_carlo_simulation(scenario, n_simulations)
            }
        
        # Calculate scenario probabilities and expected value
        probabilities = {
            'bull': 0.20,
            'base': 0.45,
            'bear': 0.25,
            'black_swan': 0.10
        }
        
        expected_revenue = sum(
            probabilities[s] * results[s]['monte_carlo']['revenue_stats']['mean']
            for s in scenarios
        )
        
        expected_share = sum(
            probabilities[s] * results[s]['monte_carlo']['share_stats']['mean']
            for s in scenarios
        )
        
        results['summary'] = {
            'probabilities': probabilities,
            'expected_cumulative_revenue': expected_revenue,
            'expected_final_share': expected_share,
            'risk_adjusted_value': expected_revenue * 0.8  # 20% risk discount
        }
        
        return results


# =============================================================================
# PART 6: MARKET SHARE EVOLUTION MODEL
# =============================================================================

class MarketShareEvolution:
    """
    Model market share evolution using Lotka-Volterra dynamics.
    
    Treats competitors as species competing for resources (market).
    """
    
    def __init__(self, competitors: Dict[str, Competitor]):
        self.competitors = competitors
        self.n_players = len(competitors) + 1  # +1 for SuperInstance
        
    def lotka_volterra_market(self, 
                              time_years: int = 5,
                              dt: float = 0.01) -> Dict:
        """
        Simulate market share evolution using competitive dynamics.
        
        dx_i/dt = r_i * x_i * (1 - sum(x_j) / K) - sum(beta_ij * x_i * x_j)
        
        Where:
        - x_i: market share of player i
        - r_i: intrinsic growth rate
        - K: market capacity (1.0 for normalized share)
        - beta_ij: competition coefficient
        """
        n_steps = int(time_years / dt)
        time = np.linspace(0, time_years, n_steps)
        
        # Initialize shares
        shares = np.zeros((n_steps, self.n_players))
        
        # SuperInstance starts small
        shares[0, 0] = 0.001
        
        # Competitors start with current shares
        for i, (name, comp) in enumerate(self.competitors.items()):
            shares[0, i+1] = comp.market_share_2025
        
        # Normalize
        shares[0] /= shares[0].sum()
        
        # Growth rates
        r = np.zeros(self.n_players)
        r[0] = 0.5  # SuperInstance growth rate
        for i, (name, comp) in enumerate(self.competitors.items()):
            r[i+1] = 0.1 * comp.innovation_rate + 0.05
        
        # Competition coefficients (how much each player affects others)
        beta = np.zeros((self.n_players, self.n_players))
        
        # SuperInstance is most affected by high-overlap competitors
        for i, (name, comp) in enumerate(self.competitors.items()):
            beta[0, i+1] = 0.5 * comp.niche_overlap  # Effect on SuperInstance
            beta[i+1, 0] = 0.3 * comp.innovation_rate  # Effect on competitor
        
        # Competitor-competitor interactions
        for i, (name_i, comp_i) in enumerate(self.competitors.items()):
            for j, (name_j, comp_j) in enumerate(self.competitors.items()):
                if i != j:
                    beta[i+1, j+1] = 0.1 * (comp_i.niche_overlap + comp_j.niche_overlap) / 2
        
        # Simulate
        for t in range(1, n_steps):
            for i in range(self.n_players):
                # Logistic growth
                growth = r[i] * shares[t-1, i] * (1 - shares[t-1].sum())
                
                # Competition
                competition = sum(beta[i, j] * shares[t-1, i] * shares[t-1, j] 
                                for j in range(self.n_players) if j != i)
                
                shares[t, i] = shares[t-1, i] + (growth - competition) * dt
                shares[t, i] = max(0, shares[t, i])  # No negative shares
        
        return {
            'time': time,
            'shares': shares,
            'player_names': ['SuperInstance'] + list(self.competitors.keys()),
            'final_shares': shares[-1],
            'superinstance_peak_share': shares[:, 0].max(),
            'time_to_peak_share': time[np.argmax(shares[:, 0])]
        }
    
    def bass_diffusion_model(self, 
                            innovators: float = 0.01,
                            imitators: float = 0.4,
                            market_potential: float = 1.0) -> Dict:
        """
        Bass diffusion model for SuperInstance adoption.
        
        dN/dt = p*(M - N) + q*(N/M)*(M - N)
        
        Where:
        - N: cumulative adopters
        - M: market potential
        - p: innovation coefficient
        - q: imitation coefficient
        """
        years = 5
        dt = 0.01
        n_steps = int(years / dt)
        
        time = np.linspace(0, years, n_steps)
        N = np.zeros(n_steps)
        N[0] = 0.001  # Initial adopters
        
        for t in range(1, n_steps):
            # Bass model equation
            dN = (innovators * (market_potential - N[t-1]) + 
                  imitators * (N[t-1] / market_potential) * (market_potential - N[t-1]))
            N[t] = N[t-1] + dN * dt
            N[t] = min(market_potential, N[t])
        
        # Peak adoption rate
        adoption_rate = np.gradient(N, time)
        peak_adoption_time = time[np.argmax(adoption_rate)]
        
        return {
            'time': time,
            'cumulative_adopters': N,
            'adoption_rate': adoption_rate,
            'peak_adoption_time': peak_adoption_time,
            'peak_adoption_rate': adoption_rate.max(),
            'saturation_level': N[-1] / market_potential
        }


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_visualizations(results: Dict, output_path: str):
    """Create comprehensive visualization of competitive dynamics."""
    
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Prisoner's Dilemma Payoff Matrix
    ax1 = fig.add_subplot(4, 3, 1)
    payoff_si, payoff_comp = results['game_theory']['prisoners_dilemma']
    im = ax1.imshow(payoff_si, cmap='RdYlGn', aspect='auto')
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(['Innovate', 'Price Compete'])
    ax1.set_yticklabels(['Innovate', 'Price Compete'])
    ax1.set_xlabel('Competitor Strategy')
    ax1.set_ylabel('SuperInstance Strategy')
    ax1.set_title('Prisoner\'s Dilemma: SuperInstance Payoffs')
    for i in range(2):
        for j in range(2):
            ax1.text(j, i, f'{payoff_si[i,j]:.2f}', ha='center', va='center', fontsize=12)
    plt.colorbar(im, ax=ax1, label='Payoff')
    
    # 2. Stackelberg Competition
    ax2 = fig.add_subplot(4, 3, 2)
    stackelberg = results['game_theory']['stackelberg']
    strategies = ['First Mover\n(SuperInstance)', 'Follower\n(Competitor)']
    quantities = [stackelberg['q_first_mover'], stackelberg['q_follower']]
    profits = [stackelberg['profit_first_mover'], stackelberg['profit_follower']]
    x = np.arange(len(strategies))
    width = 0.35
    ax2.bar(x - width/2, quantities, width, label='Quantity', color='steelblue')
    ax2.bar(x + width/2, profits, width, label='Profit', color='coral')
    ax2.set_xlabel('Player')
    ax2.set_ylabel('Value')
    ax2.set_title('Stackelberg Competition Results')
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategies)
    ax2.legend()
    ax2.set_ylim(0, max(max(quantities), max(profits)) * 1.2)
    
    # 3. Differentiation Game Nash Equilibrium
    ax3 = fig.add_subplot(4, 3, 3)
    diff_game = results['game_theory']['differentiation']
    strategies_diff = diff_game['strategies']
    p1_mixed = diff_game['nash_equilibrium']['p1_mixed_strategy']
    ax3.bar(strategies_diff, p1_mixed, color='purple', alpha=0.7)
    ax3.set_xlabel('Strategy')
    ax3.set_ylabel('Probability')
    ax3.set_title('SuperInstance Nash Equilibrium Strategy')
    ax3.set_ylim(0, 1)
    
    # 4. Network Effects Growth
    ax4 = fig.add_subplot(4, 3, 4)
    network = results['game_theory']['network_effects']
    ax4.plot(network['months'], network['users_si'], 'b-', label='SuperInstance', linewidth=2)
    ax4.plot(network['months'], network['users_comp'], 'r--', label='Competitor', linewidth=2)
    ax4.set_xlabel('Months')
    ax4.set_ylabel('Users')
    ax4.set_title('Network Effects: User Growth')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Scenario Comparison - Market Share
    ax5 = fig.add_subplot(4, 3, 5)
    scenarios = ['bull', 'base', 'bear', 'black_swan']
    colors = ['green', 'blue', 'orange', 'red']
    for scenario, color in zip(scenarios, colors):
        traj = results['scenarios'][scenario]['trajectory']
        ax5.plot(traj['months']/12, traj['superinstance_share'] * 100, 
                color=color, label=scenario.capitalize(), linewidth=2)
    ax5.set_xlabel('Years')
    ax5.set_ylabel('Market Share (%)')
    ax5.set_title('SuperInstance Market Share by Scenario')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Scenario Comparison - Revenue
    ax6 = fig.add_subplot(4, 3, 6)
    for scenario, color in zip(scenarios, colors):
        traj = results['scenarios'][scenario]['trajectory']
        ax6.plot(traj['months']/12, traj['revenue']/1e6, 
                color=color, label=scenario.capitalize(), linewidth=2)
    ax6.set_xlabel('Years')
    ax6.set_ylabel('Revenue ($M/month)')
    ax6.set_title('Revenue Evolution by Scenario')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # 7. Process Node Comparison
    ax7 = fig.add_subplot(4, 3, 7)
    process = results['roadmap']['process_node']
    nodes = list(process['node_analysis'].keys())
    costs = [process['node_analysis'][n]['cost_per_die'] for n in nodes]
    risks = [process['node_analysis'][n]['risk_score'] for n in nodes]
    x = np.arange(len(nodes))
    ax7.bar(x - 0.2, costs, 0.4, label='Cost/Die ($)', color='steelblue')
    ax7.bar(x + 0.2, risks, 0.4, label='Risk Score', color='coral')
    ax7.axhline(y=process['node_analysis'][process['optimal_node']]['cost_per_die'], 
               color='green', linestyle='--', label=f'Optimal: {process["optimal_node"]}')
    ax7.set_xlabel('Process Node')
    ax7.set_ylabel('Value')
    ax7.set_title('Process Node Cost vs Risk')
    ax7.set_xticks(x)
    ax7.set_xticklabels(nodes)
    ax7.legend()
    
    # 8. Defensive Strategy ROI
    ax8 = fig.add_subplot(4, 3, 8)
    defensive = results['defensive']
    strategies = ['Patent\nFortress', 'Ecosystem\nLock-in', 'Customer\nMoats', 'Open\nSource']
    rois = [
        defensive['patent_fortress']['roi'],
        defensive['ecosystem_lockin']['roi'],
        defensive['customer_moat']['moat_strength'] * 10,  # Scaled
        defensive['open_source']['net_benefit'] * 5  # Scaled
    ]
    colors_def = ['green' if r > 1 else 'red' for r in rois]
    ax8.bar(strategies, rois, color=colors_def, alpha=0.7)
    ax8.axhline(y=1, color='black', linestyle='--', label='Breakeven')
    ax8.set_xlabel('Strategy')
    ax8.set_ylabel('ROI / Value')
    ax8.set_title('Defensive Strategy Effectiveness')
    ax8.legend()
    
    # 9. Monte Carlo Distribution - Revenue
    ax9 = fig.add_subplot(4, 3, 9)
    for scenario, color in zip(scenarios, colors):
        mc = results['scenarios'][scenario]['monte_carlo']
        revenues = np.random.normal(mc['revenue_stats']['mean'], mc['revenue_stats']['std'], 1000)
        ax9.hist(revenues/1e9, bins=30, alpha=0.5, color=color, label=scenario.capitalize())
    ax9.set_xlabel('Cumulative Revenue ($B)')
    ax9.set_ylabel('Frequency')
    ax9.set_title('Monte Carlo Revenue Distribution')
    ax9.legend()
    
    # 10. Market Share Evolution (Lotka-Volterra)
    ax10 = fig.add_subplot(4, 3, 10)
    lv = results['market_evolution']['lotka_volterra']
    for i, name in enumerate(lv['player_names'][:5]):  # Top 5 players
        if 'SuperInstance' in name:
            ax10.plot(lv['time'], lv['shares'][:, i] * 100, 
                     linewidth=3, label=name, color='blue')
        else:
            ax10.plot(lv['time'], lv['shares'][:, i] * 100, 
                     linewidth=1, alpha=0.5, label=name)
    ax10.set_xlabel('Years')
    ax10.set_ylabel('Market Share (%)')
    ax10.set_title('Market Share Evolution (Lotka-Volterra)')
    ax10.legend(loc='upper right')
    ax10.grid(True, alpha=0.3)
    
    # 11. Bass Diffusion Model
    ax11 = fig.add_subplot(4, 3, 11)
    bass = results['market_evolution']['bass_diffusion']
    ax11_twin = ax11.twinx()
    l1 = ax11.plot(bass['time'], bass['cumulative_adopters'] * 100, 'b-', 
                  label='Cumulative Adopters', linewidth=2)
    l2 = ax11_twin.plot(bass['time'], bass['adoption_rate'] * 100, 'r--', 
                        label='Adoption Rate', linewidth=2)
    ax11.axvline(x=bass['peak_adoption_time'], color='green', linestyle=':', 
                label=f'Peak: {bass["peak_adoption_time"]:.1f} years')
    ax11.set_xlabel('Years')
    ax11.set_ylabel('Cumulative Adopters (%)', color='blue')
    ax11_twin.set_ylabel('Adoption Rate (%/year)', color='red')
    ax11.set_title('Bass Diffusion Model')
    lines = l1 + l2
    ax11.legend(lines, [l.get_label() for l in lines], loc='center right')
    ax11.grid(True, alpha=0.3)
    
    # 12. Summary: Expected Value by Scenario
    ax12 = fig.add_subplot(4, 3, 12)
    summary = results['scenarios']['summary']
    probs = list(summary['probabilities'].values())
    scenarios_list = list(summary['probabilities'].keys())
    expected_values = [results['scenarios'][s]['monte_carlo']['revenue_stats']['mean']/1e9 
                      for s in scenarios_list]
    weighted_values = [p * v for p, v in zip(probs, expected_values)]
    
    bars = ax12.bar(scenarios_list, weighted_values, color=colors, alpha=0.7)
    ax12.set_xlabel('Scenario')
    ax12.set_ylabel('Probability-Weighted Revenue ($B)')
    ax12.set_title('Expected Revenue Contribution by Scenario')
    
    # Add probability labels
    for bar, prob in zip(bars, probs):
        ax12.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                 f'{prob*100:.0f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved visualization to {output_path}")


def create_payoff_matrices_visualization(results: Dict, output_path: str):
    """Create detailed payoff matrix visualizations."""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. SuperInstance Prisoner's Dilemma
    ax = axes[0, 0]
    payoff_si, _ = results['game_theory']['prisoners_dilemma']
    im = ax.imshow(payoff_si, cmap='RdYlGn', aspect='auto', vmin=0.4, vmax=1.0)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Innovate', 'Price Compete'])
    ax.set_yticklabels(['Innovate', 'Price Compete'])
    ax.set_xlabel('Competitor Strategy')
    ax.set_ylabel('SuperInstance Strategy')
    ax.set_title('Prisoner\'s Dilemma\nSuperInstance Payoffs')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{payoff_si[i,j]:.3f}', ha='center', va='center', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Payoff')
    
    # 2. Competitor Prisoner's Dilemma
    ax = axes[0, 1]
    _, payoff_comp = results['game_theory']['prisoners_dilemma']
    im = ax.imshow(payoff_comp, cmap='RdYlGn', aspect='auto', vmin=0.4, vmax=1.0)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Innovate', 'Price Compete'])
    ax.set_yticklabels(['Innovate', 'Price Compete'])
    ax.set_xlabel('SuperInstance Strategy')
    ax.set_ylabel('Competitor Strategy')
    ax.set_title('Prisoner\'s Dilemma\nCompetitor Payoffs')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{payoff_comp[i,j]:.3f}', ha='center', va='center', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Payoff')
    
    # 3. Differentiation Game - SuperInstance
    ax = axes[0, 2]
    diff_game = results['game_theory']['differentiation']
    im = ax.imshow(diff_game['payoff_si'], cmap='RdYlGn', aspect='auto')
    strategies = ['Cost\nLeader', 'Differentiate', 'Focus']
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(strategies)
    ax.set_yticklabels(strategies)
    ax.set_xlabel('Competitor Strategy')
    ax.set_ylabel('SuperInstance Strategy')
    ax.set_title('Differentiation Game\nSuperInstance Payoffs')
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f'{diff_game["payoff_si"][i,j]:.2f}', ha='center', va='center', fontsize=12)
    plt.colorbar(im, ax=ax, label='Payoff')
    
    # 4. Differentiation Game - Competitor
    ax = axes[1, 0]
    im = ax.imshow(diff_game['payoff_comp'], cmap='RdYlGn', aspect='auto')
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(strategies)
    ax.set_yticklabels(strategies)
    ax.set_xlabel('SuperInstance Strategy')
    ax.set_ylabel('Competitor Strategy')
    ax.set_title('Differentiation Game\nCompetitor Payoffs')
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f'{diff_game["payoff_comp"][i,j]:.2f}', ha='center', va='center', fontsize=12)
    plt.colorbar(im, ax=ax, label='Payoff')
    
    # 5. Nash Equilibrium Summary
    ax = axes[1, 1]
    nash_pd = results['game_theory']['nash_pd']
    nash_diff = diff_game['nash_equilibrium']
    
    games = ['Prisoner\'s\nDilemma', 'Differentiation\nGame']
    si_strategies = ['Price Compete', 'Focus']  # Dominant strategies
    comp_strategies = ['Price Compete', 'Focus']
    
    y_pos = np.arange(len(games))
    width = 0.35
    
    # Strategy probabilities
    ax.barh(y_pos - width/2, [nash_pd['p1_mixed_strategy'][1], nash_diff['p1_mixed_strategy'][2]], 
           width, label='SuperInstance', color='steelblue')
    ax.barh(y_pos + width/2, [nash_pd['p2_mixed_strategy'][1], nash_diff['p2_mixed_strategy'][2]], 
           width, label='Competitor', color='coral')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(games)
    ax.set_xlabel('Probability of Aggressive Strategy')
    ax.set_title('Nash Equilibrium Strategies')
    ax.legend()
    ax.set_xlim(0, 1)
    
    # 6. Payoff Comparison
    ax = axes[1, 2]
    games = ['PD\n(Innovate/Innovate)', 'PD\n(Price/Price)', 'Diff\n(Focus/Focus)', 
             'Stackelberg\n(First Mover)', 'Stackelberg\n(Follower)']
    payoffs = [
        payoff_si[0, 0], payoff_si[1, 1], diff_game['payoff_si'][2, 2],
        results['game_theory']['stackelberg']['profit_first_mover'],
        results['game_theory']['stackelberg']['profit_follower']
    ]
    colors = ['green', 'red', 'blue', 'purple', 'orange']
    ax.bar(games, payoffs, color=colors, alpha=0.7)
    ax.set_ylabel('Payoff')
    ax.set_title('Equilibrium Payoff Comparison')
    ax.set_ylim(0, max(payoffs) * 1.2)
    for i, v in enumerate(payoffs):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved payoff matrices to {output_path}")


# =============================================================================
# MAIN SIMULATION FUNCTION
# =============================================================================

def run_full_simulation():
    """Run all competitive dynamics analyses."""
    print("=" * 70)
    print("Cycle 20: Competitive Dynamics and Market Response Analysis")
    print("=" * 70)
    
    # Initialize competitors
    print("\n[1/6] Initializing Competitor Database...")
    competitors = create_competitor_database()
    print(f"   Loaded {len(competitors)} competitors")
    for name, comp in competitors.items():
        print(f"   - {name}: {comp.competitor_type.value}, overlap={comp.niche_overlap:.2f}")
    
    results = {}
    
    # Part 1: Competitor Response Modeling
    print("\n[2/6] Running Competitor Response Modeling...")
    response_model = CompetitorResponseModel(competitors)
    
    # Simulate SuperInstance market share trajectory
    months = np.arange(60)
    si_share = 0.001 * (1.15 ** months)  # 15% monthly growth initially
    si_share = np.minimum(si_share, 0.15)  # Cap at 15%
    
    response_results = response_model.simulate_competitive_response(si_share, months)
    results['competitor_response'] = response_results
    print(f"   Simulated responses from {len(competitors)} competitors")
    
    # Part 2: Game Theory Analysis
    print("\n[3/6] Running Game Theory Analysis...")
    game_theory = MarketGameTheory()
    
    # Prisoner's Dilemma
    payoff_si, payoff_comp = game_theory.prisoners_dilemma_payoff()
    nash_pd = game_theory.find_nash_equilibrium(payoff_si, payoff_comp)
    
    # Stackelberg
    stackelberg = game_theory.stackelberg_competition(first_mover_advantage=0.3)
    
    # Differentiation
    differentiation = game_theory.differentiation_game()
    
    # Network Effects
    network_effects = game_theory.network_effects_game(superinstance_users=100, competitor_users=5000)
    
    results['game_theory'] = {
        'prisoners_dilemma': (payoff_si, payoff_comp),
        'nash_pd': nash_pd,
        'stackelberg': stackelberg,
        'differentiation': differentiation,
        'network_effects': network_effects
    }
    
    print(f"   Nash Equilibrium (PD): SI={nash_pd['p1_mixed_strategy']}, Comp={nash_pd['p2_mixed_strategy']}")
    print(f"   Stackelberg: First mover profit = {stackelberg['profit_first_mover']:.3f}")
    print(f"   Differentiation: Optimal SI strategy = {differentiation['optimal_si_strategy']}")
    
    # Part 3: Technology Roadmap Timing
    print("\n[4/6] Running Technology Roadmap Timing Analysis...")
    roadmap = TechnologyRoadmapTiming()
    
    first_mover = roadmap.first_mover_window_analysis()
    process_node = roadmap.process_node_transition_analysis()
    patent_cliff = roadmap.patent_cliff_timing()
    
    results['roadmap'] = {
        'first_mover': first_mover,
        'process_node': process_node,
        'patent_cliff': patent_cliff
    }
    
    print(f"   First mover window: {first_mover['first_mover_window_months']:.0f} months")
    print(f"   Optimal process node: {process_node['optimal_node']}")
    print(f"   Patent cliff strategic window: {patent_cliff['strategic_window']}")
    
    # Part 4: Defensive Strategies
    print("\n[5/6] Running Defensive Strategy Analysis...")
    defensive = DefensiveStrategies()
    
    patent_fortress = defensive.patent_fortress_optimization()
    ecosystem_lockin = defensive.ecosystem_lockin_analysis()
    customer_moat = defensive.customer_moat_analysis()
    open_source = defensive.open_source_strategy()
    
    results['defensive'] = {
        'patent_fortress': patent_fortress,
        'ecosystem_lockin': ecosystem_lockin,
        'customer_moat': customer_moat,
        'open_source': open_source
    }
    
    print(f"   Patent fortress ROI: {patent_fortress['roi']:.2f}x")
    print(f"   Ecosystem lock-in coefficient: {ecosystem_lockin['lockin_coefficient']:.2f}")
    print(f"   Customer moat strength: {customer_moat['moat_strength']:.2f}")
    
    # Part 5: Scenario Analysis
    print("\n[6/6] Running Scenario Analysis...")
    scenario_analysis = ScenarioAnalysis(competitors)
    all_scenarios = scenario_analysis.run_all_scenarios(n_simulations=100)
    results['scenarios'] = all_scenarios
    
    print(f"   Bull scenario expected revenue: ${all_scenarios['bull']['monte_carlo']['revenue_stats']['mean']/1e9:.2f}B")
    print(f"   Base scenario expected revenue: ${all_scenarios['base']['monte_carlo']['revenue_stats']['mean']/1e9:.2f}B")
    print(f"   Bear scenario expected revenue: ${all_scenarios['bear']['monte_carlo']['revenue_stats']['mean']/1e9:.2f}B")
    print(f"   Expected cumulative revenue: ${all_scenarios['summary']['expected_cumulative_revenue']/1e9:.2f}B")
    
    # Part 6: Market Share Evolution
    print("\n[Bonus] Running Market Share Evolution Model...")
    market_evolution = MarketShareEvolution(competitors)
    
    lotka_volterra = market_evolution.lotka_volterra_market()
    bass_diffusion = market_evolution.bass_diffusion_model()
    
    results['market_evolution'] = {
        'lotka_volterra': lotka_volterra,
        'bass_diffusion': bass_diffusion
    }
    
    print(f"   SuperInstance peak share (LV model): {lotka_volterra['superinstance_peak_share']*100:.1f}%")
    print(f"   Peak adoption time (Bass model): {bass_diffusion['peak_adoption_time']:.2f} years")
    
    # Create visualizations
    print("\n[Visualization] Creating plots...")
    create_visualizations(results, '/home/z/my-project/research/cycle20_competitive_dynamics.png')
    create_payoff_matrices_visualization(results, '/home/z/my-project/research/cycle20_payoff_matrices.png')
    
    # Store results
    import json
    
    # Convert numpy arrays to lists for JSON serialization
    json_results = {
        'game_theory': {
            'nash_pd': {
                'p1_strategy': nash_pd['p1_mixed_strategy'].tolist(),
                'p2_strategy': nash_pd['p2_mixed_strategy'].tolist(),
                'p1_payoff': float(nash_pd['p1_expected_payoff']),
                'p2_payoff': float(nash_pd['p2_expected_payoff'])
            },
            'stackelberg': stackelberg,
            'differentiation': {
                'optimal_si_strategy': differentiation['optimal_si_strategy'],
                'optimal_comp_strategy': differentiation['optimal_comp_strategy']
            }
        },
        'roadmap': {
            'first_mover_window': first_mover['first_mover_window_months'],
            'optimal_process_node': process_node['optimal_node'],
            'fma_coefficient': first_mover['first_mover_advantage_coefficient']
        },
        'defensive': {
            'patent_roi': patent_fortress['roi'],
            'lockin_coefficient': ecosystem_lockin['lockin_coefficient'],
            'customer_moat': customer_moat['moat_strength'],
            'open_source_benefit': open_source['net_benefit']
        },
        'scenarios': {
            'expected_revenue_b': all_scenarios['summary']['expected_cumulative_revenue'] / 1e9,
            'expected_share': all_scenarios['summary']['expected_final_share'],
            'probabilities': all_scenarios['summary']['probabilities']
        },
        'market_evolution': {
            'peak_share': float(lotka_volterra['superinstance_peak_share']),
            'peak_time': float(lotka_volterra['time_to_peak_share']),
            'bass_peak_adoption': float(bass_diffusion['peak_adoption_time'])
        }
    }
    
    with open('/home/z/my-project/research/cycle20_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("Cycle 20 Simulation Complete")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = run_full_simulation()
