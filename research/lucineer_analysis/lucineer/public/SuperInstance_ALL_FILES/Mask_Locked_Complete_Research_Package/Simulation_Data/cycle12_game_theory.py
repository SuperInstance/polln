#!/usr/bin/env python3
"""
Cycle 12: Game-Theoretic Resource Allocation Analysis
for Mask-Locked Inference Chip

This simulation analyzes resource allocation strategies among 1024 PEs
competing for shared resources including bandwidth, power budget, and memory access.

Key components:
1. Non-cooperative game theory: PE competition, Nash equilibrium
2. Cooperative game theory: Coalitions, Shapley value, Core stability
3. Mechanism design: VCG mechanism, truthful revelation, auctions
4. Multi-agent reinforcement learning: Distributed negotiation
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, linprog
from scipy.stats import entropy
from itertools import combinations
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# GLOBAL PARAMETERS (from Cycle 8 and design specs)
# =============================================================================

NUM_PES = 1024  # 32x32 PE array
GRID_SIZE = 32  # 32x32 grid
TOTAL_POWER_W = 5.0  # 5W total power budget
SYSTOLIC_BANDWIDTH_TBPS = 31.74  # From Cycle 8 analysis
LINK_BANDWIDTH_GBPS = 64  # Per-link bandwidth
MEMORY_BANDWIDTH_GBPS = 25.6  # LPDDR4 memory bandwidth

# Per-PE power ranges (mW)
MIN_PE_POWER = 0.1  # Idle/low activity
MAX_PE_POWER = 15.0  # Maximum activity
NOMINAL_PE_POWER = 5.0  # Average operating power

# Resource constraints
TOTAL_BANDWIDTH = SYSTOLIC_BANDWIDTH_TBPS * 1e12  # Convert to bps
MEMORY_ACCESS_LIMIT = MEMORY_BANDWIDTH_GBPS * 1e9  # Convert to bps


# =============================================================================
# PART 1: NON-COOPERATIVE GAME THEORY - PE COMPETITION
# =============================================================================

class PEResourceGame:
    """
    Non-cooperative game for PE resource competition.
    
    Each PE is a player that chooses a demand level for:
    - Power allocation
    - Bandwidth allocation  
    - Memory access frequency
    
    Nash equilibrium is computed where no PE can unilaterally improve.
    """
    
    def __init__(self, num_players: int = NUM_PES, 
                 total_power: float = TOTAL_POWER_W,
                 total_bandwidth: float = TOTAL_BANDWIDTH):
        self.num_players = num_players
        self.total_power = total_power
        self.total_bandwidth = total_bandwidth
        
        # Initialize random demands (normalized)
        self.power_demands = np.random.uniform(0.001, 0.01, num_players)
        self.bandwidth_demands = np.random.uniform(0.0001, 0.001, num_players)
        
        # Normalize to feasible region
        self._normalize_demands()
        
        # PE utility function parameters (heterogeneous)
        self.alpha = np.random.uniform(0.5, 1.5, num_players)  # Power sensitivity
        self.beta = np.random.uniform(0.3, 0.8, num_players)   # Bandwidth sensitivity
        self.gamma = np.random.uniform(0.1, 0.5, num_players)  # Fairness preference
        
    def _normalize_demands(self):
        """Ensure total demands don't exceed capacity."""
        power_sum = self.power_demands.sum()
        bw_sum = self.bandwidth_demands.sum()
        
        if power_sum > self.total_power:
            self.power_demands *= self.total_power / power_sum
        if bw_sum > self.total_bandwidth:
            self.bandwidth_demands *= self.total_bandwidth / bw_sum
    
    def utility(self, player: int, power_alloc: float, bw_alloc: float) -> float:
        """
        Cobb-Douglas utility function for each PE.
        U = power^alpha * bandwidth^beta - cost_of_demand
        """
        # Production component
        production = (power_alloc ** self.alpha[player]) * (bw_alloc ** self.beta[player])
        
        # Cost of high demand (congestion pricing)
        demand_cost = 0.01 * (power_alloc + bw_alloc * 1e-12) ** 2
        
        # Fairness bonus
        fairness_bonus = self.gamma[player] * min(power_alloc, bw_alloc * 1e-12)
        
        return production - demand_cost + fairness_bonus
    
    def compute_allocation(self) -> Tuple[np.ndarray, np.ndarray]:
        """Proportional allocation based on demands."""
        total_power_demand = self.power_demands.sum()
        total_bw_demand = self.bandwidth_demands.sum()
        
        if total_power_demand > 0:
            power_alloc = self.power_demands / total_power_demand * self.total_power
        else:
            power_alloc = np.ones(self.num_players) * self.total_power / self.num_players
            
        if total_bw_demand > 0:
            bw_alloc = self.bandwidth_demands / total_bw_demand * self.total_bandwidth
        else:
            bw_alloc = np.ones(self.num_players) * self.total_bandwidth / self.num_players
            
        return power_alloc, bw_alloc
    
    def best_response(self, player: int, other_power_demands: np.ndarray,
                      other_bw_demands: np.ndarray) -> Tuple[float, float]:
        """
        Compute best response for a single player given others' strategies.
        """
        def objective(x):
            p_demand, b_demand = x
            
            # Update demands
            power_demands = other_power_demands.copy()
            power_demands[player] = p_demand
            bw_demands = other_bw_demands.copy()
            bw_demands[player] = b_demand
            
            # Compute allocation
            total_p = power_demands.sum()
            total_b = bw_demands.sum()
            
            if total_p > 0:
                p_alloc = p_demand / total_p * self.total_power
            else:
                p_alloc = self.total_power / self.num_players
                
            if total_b > 0:
                b_alloc = b_demand / total_b * self.total_bandwidth
            else:
                b_alloc = self.total_bandwidth / self.num_players
            
            return -self.utility(player, p_alloc, b_alloc)
        
        # Bounds for demands
        bounds = [(0.0001, self.total_power * 0.1), 
                  (0.00001, self.total_bandwidth * 0.1)]
        
        result = minimize(objective, 
                         [self.power_demands[player], self.bandwidth_demands[player]],
                         bounds=bounds,
                         method='L-BFGS-B')
        
        return result.x[0], result.x[1]
    
    def find_nash_equilibrium(self, max_iterations: int = 100, 
                              tolerance: float = 1e-6) -> Dict:
        """
        Find Nash equilibrium through iterated best response.
        """
        convergence_history = []
        
        for iteration in range(max_iterations):
            old_power = self.power_demands.copy()
            old_bw = self.bandwidth_demands.copy()
            
            # Random order best response
            order = np.random.permutation(self.num_players)
            
            for player in order[:min(50, self.num_players)]:  # Sample players
                br_power, br_bw = self.best_response(
                    player, self.power_demands, self.bandwidth_demands)
                
                # Soft update
                self.power_demands[player] = 0.7 * self.power_demands[player] + 0.3 * br_power
                self.bandwidth_demands[player] = 0.7 * self.bandwidth_demands[player] + 0.3 * br_bw
            
            self._normalize_demands()
            
            # Check convergence
            power_diff = np.abs(self.power_demands - old_power).max()
            bw_diff = np.abs(self.bandwidth_demands - old_bw).max()
            convergence_history.append(max(power_diff, bw_diff))
            
            if max(power_diff, bw_diff) < tolerance:
                break
        
        power_alloc, bw_alloc = self.compute_allocation()
        
        # Compute utilities
        utilities = np.array([self.utility(i, power_alloc[i], bw_alloc[i]) 
                             for i in range(self.num_players)])
        
        return {
            'power_demands': self.power_demands,
            'bandwidth_demands': self.bandwidth_demands,
            'power_allocation': power_alloc,
            'bandwidth_allocation': bw_alloc,
            'utilities': utilities,
            'convergence': convergence_history,
            'iterations': iteration + 1,
            'converged': max(power_diff, bw_diff) < tolerance
        }


class PayoffMatrix:
    """
    Compute payoff matrices for simplified PE game.
    For tractability, we consider a reduced game with representative PE types.
    """
    
    def __init__(self, num_types: int = 4):
        self.num_types = num_types
        self.strategies = ['low', 'medium', 'high']  # Demand levels
        self.strategy_values = {'low': 0.1, 'medium': 0.5, 'high': 1.0}
        
    def compute_payoff_matrix(self, total_resource: float = 1.0) -> np.ndarray:
        """
        Compute 3x3 payoff matrix for two-player simplified game.
        """
        n_strategies = len(self.strategies)
        payoff_matrix = np.zeros((n_strategies, n_strategies))
        
        for i, s1 in enumerate(self.strategies):
            for j, s2 in enumerate(self.strategies):
                d1 = self.strategy_values[s1]
                d2 = self.strategy_values[s2]
                
                # Proportional allocation
                total_demand = d1 + d2
                a1 = d1 / total_demand * total_resource
                a2 = d2 / total_demand * total_resource
                
                # Utility (log utility with congestion)
                u1 = np.log(a1 + 0.01) - 0.1 * d1**2
                u2 = np.log(a2 + 0.01) - 0.1 * d2**2
                
                payoff_matrix[i, j] = u1
        
        return payoff_matrix
    
    def find_nash_equilibrium_2player(self, payoff_matrix: np.ndarray) -> Dict:
        """
        Find mixed strategy Nash equilibrium for 2-player game.
        """
        n = payoff_matrix.shape[0]
        
        # For symmetric game, find equilibrium probability distribution
        # Solve: p^T @ A = v (constant), sum(p) = 1
        
        # Simplified: find best response dynamics equilibrium
        p = np.ones(n) / n  # Start uniform
        
        for _ in range(1000):
            expected_payoffs = payoff_matrix @ p
            best_response = np.zeros(n)
            best_response[np.argmax(expected_payoffs)] = 1.0
            
            # Soft update
            p = 0.99 * p + 0.01 * best_response
        
        return {
            'mixed_strategy': p,
            'expected_payoff': p @ payoff_matrix @ p,
            'best_pure_strategy': self.strategies[np.argmax(p)]
        }


# =============================================================================
# PART 2: COOPERATIVE GAME THEORY - COALITIONS AND SHAPLEY VALUE
# =============================================================================

class CooperativeGame:
    """
    Cooperative game theory analysis for PE coalitions.
    
    Analyzes:
    - Coalition formation
    - Shapley value for contribution measurement
    - Core stability of allocations
    - Pareto optimal resource distribution
    """
    
    def __init__(self, num_players: int = NUM_PES):
        self.num_players = num_players
        self.player_indices = list(range(num_players))
        
        # Player characteristics (computational capacity)
        self.capacities = np.random.uniform(0.8, 1.2, num_players)
        
        # Pre-compute characteristic function for subsets
        self._coalition_values = {}
        
    def characteristic_function(self, coalition: set) -> float:
        """
        Value of a coalition: v(S)
        
        Value increases with coalition size but with diminishing returns.
        Also considers complementarity (synergies).
        """
        if len(coalition) == 0:
            return 0.0
            
        coalition_key = frozenset(coalition)
        if coalition_key in self._coalition_values:
            return self._coalition_values[coalition_key]
        
        # Sum of individual capacities
        base_value = sum(self.capacities[i] for i in coalition)
        
        # Synergy bonus (superadditivity)
        # Larger coalitions have synergy from coordination
        synergy = 0.1 * len(coalition) ** 0.5
        
        # Communication overhead penalty
        if len(coalition) > 1:
            # Diameter-based communication cost
            # For a subset of PEs, estimate communication distance
            comm_cost = 0.01 * len(coalition) ** 1.5
        else:
            comm_cost = 0
        
        value = base_value + synergy - comm_cost
        self._coalition_values[coalition_key] = value
        return value
    
    def shapley_value(self, player: int) -> float:
        """
        Compute Shapley value for a player.
        
        φ_i = Σ [|S|!(n-|S|-1)!/n!] * [v(S∪{i}) - v(S)]
        
        For large n, use Monte Carlo approximation.
        """
        n = self.num_players
        other_players = [j for j in self.player_indices if j != player]
        
        # Monte Carlo approximation
        num_samples = min(1000, 2**min(15, n-1))
        shapley_sum = 0.0
        
        for _ in range(num_samples):
            # Random permutation
            perm = np.random.permutation(other_players)
            coalition = set(perm[:np.random.randint(len(perm) + 1)])
            
            marginal_contribution = (self.characteristic_function(coalition | {player}) - 
                                    self.characteristic_function(coalition))
            shapley_sum += marginal_contribution
        
        return shapley_sum / num_samples
    
    def compute_all_shapley_values(self) -> np.ndarray:
        """Compute Shapley values for all players using approximation."""
        shapley_values = np.zeros(self.num_players)
        
        for i in range(self.num_players):
            shapley_values[i] = self.shapley_value(i)
        
        return shapley_values
    
    def is_in_core(self, allocation: np.ndarray) -> bool:
        """
        Check if allocation is in the core.
        
        Core conditions:
        1. Individual rationality: x_i ≥ v({i})
        2. Coalitional rationality: Σ_i∈S x_i ≥ v(S) for all S
        3. Efficiency: Σ_i x_i = v(N)
        """
        total_value = self.characteristic_function(set(self.player_indices))
        
        # Efficiency check
        if abs(allocation.sum() - total_value) > 1e-6:
            return False
        
        # Individual rationality
        for i in self.player_indices:
            if allocation[i] < self.characteristic_function({i}) - 1e-6:
                return False
        
        # Sample coalition rationality checks
        for _ in range(100):
            coalition_size = np.random.randint(2, min(50, self.num_players))
            coalition = set(np.random.choice(self.player_indices, coalition_size, replace=False))
            
            if allocation[list(coalition)].sum() < self.characteristic_function(coalition) - 1e-6:
                return False
        
        return True
    
    def find_core_allocation(self) -> np.ndarray:
        """
        Find an allocation in the core using linear programming.
        
        For the grand coalition:
        - Maximize minimum player utility (egalitarian)
        - Subject to core constraints
        """
        n = self.num_players
        total_value = self.characteristic_function(set(self.player_indices))
        
        # Simplified: proportional allocation with Shapley-like weights
        weights = self.capacities / self.capacities.sum()
        allocation = weights * total_value
        
        # Verify core membership (approximate)
        if not self.is_in_core(allocation):
            # Fall back to egalitarian allocation
            allocation = np.ones(n) * total_value / n
        
        return allocation
    
    def pareto_frontier(self, num_points: int = 100) -> List[np.ndarray]:
        """
        Generate Pareto frontier for resource allocation.
        
        Trade-off between efficiency and fairness.
        """
        total_value = self.characteristic_function(set(self.player_indices))
        frontier = []
        
        # Sample random allocations on the simplex
        for _ in range(num_points):
            # Dirichlet distribution for random point on simplex
            weights = np.random.dirichlet(np.ones(self.num_players))
            allocation = weights * total_value
            frontier.append(allocation)
        
        return frontier


class CoalitionFormation:
    """
    Analyze optimal coalition formation among PEs.
    """
    
    def __init__(self, num_players: int = 64):  # Reduced for tractability
        self.num_players = num_players
        self.coop_game = CooperativeGame(num_players)
        
    def find_stable_partition(self) -> List[set]:
        """
        Find a stable partition using the hedonic game framework.
        
        Players form coalitions based on preferences.
        """
        # Initialize: each player in singleton
        partition = [{i} for i in range(self.num_players)]
        
        for iteration in range(100):
            improved = False
            
            for i in range(self.num_players):
                current_coalition = next(c for c in partition if i in c)
                current_value = self.coop_game.characteristic_function(current_coalition) / len(current_coalition)
                
                # Try joining other coalitions
                best_coalition = current_coalition
                best_value = current_value
                
                for coalition in partition:
                    if i in coalition:
                        continue
                    
                    # Value per player in merged coalition
                    merged = coalition | {i}
                    merged_value = self.coop_game.characteristic_function(merged) / len(merged)
                    
                    if merged_value > best_value:
                        best_value = merged_value
                        best_coalition = coalition
                
                if best_coalition != current_coalition:
                    # Move player
                    partition.remove(current_coalition)
                    current_coalition.discard(i)
                    if current_coalition:
                        partition.append(current_coalition)
                    
                    partition.remove(best_coalition)
                    best_coalition.add(i)
                    partition.append(best_coalition)
                    improved = True
            
            if not improved:
                break
        
        return partition


# =============================================================================
# PART 3: MECHANISM DESIGN - VCG AND AUCTIONS
# =============================================================================

class VCGMechanism:
    """
    Vickrey-Clarke-Groves mechanism for truthful resource allocation.
    
    Key property: Truth-telling is a dominant strategy.
    """
    
    def __init__(self, num_agents: int = NUM_PES,
                 total_power: float = TOTAL_POWER_W,
                 total_bandwidth: float = TOTAL_BANDWIDTH):
        self.num_agents = num_agents
        self.total_power = total_power
        self.total_bandwidth = total_bandwidth
        
        # True valuations (unknown to mechanism)
        self.true_power_values = np.random.uniform(1, 10, num_agents)
        self.true_bandwidth_values = np.random.uniform(1e12, 1e13, num_agents)
        
        # Reported valuations (may differ from true)
        self.reported_power = self.true_power_values.copy()
        self.reported_bandwidth = self.true_bandwidth_values.copy()
        
    def social_welfare_maximization(self, reported_values: np.ndarray,
                                   total_resource: float) -> np.ndarray:
        """
        Solve for allocation that maximizes reported social welfare.
        
        max Σ v_i * a_i
        s.t. Σ a_i ≤ total_resource
             a_i ≥ 0
        """
        # For linear objective with one constraint, greedy works
        # Allocate to highest valuations first
        sorted_indices = np.argsort(reported_values)[::-1]
        allocation = np.zeros_like(reported_values)
        
        remaining = total_resource
        for i in sorted_indices:
            # Allocate proportionally based on value
            alloc = min(remaining, reported_values[i] / reported_values.sum() * total_resource)
            allocation[i] = alloc
            remaining -= alloc
            if remaining <= 0:
                break
        
        return allocation
    
    def vcg_payment(self, agent: int, reported_values: np.ndarray,
                   total_resource: float) -> float:
        """
        Compute VCG payment for agent i.
        
        p_i = SW_{-i}(optimal without i) - SW_{-i}(optimal with i)
        """
        # Social welfare with all agents
        allocation_with = self.social_welfare_maximization(reported_values, total_resource)
        sw_with = (reported_values * allocation_with).sum() - reported_values[agent] * allocation_with[agent]
        
        # Social welfare without agent i
        values_without = reported_values.copy()
        values_without[agent] = 0
        allocation_without = self.social_welfare_maximization(values_without, total_resource)
        sw_without = (reported_values * allocation_without).sum()
        
        # VCG payment
        payment = sw_without - sw_with
        
        return max(0, payment)  # Payment must be non-negative
    
    def run_vcg_auction(self, resource_type: str = 'power') -> Dict:
        """
        Run VCG mechanism for resource allocation.
        """
        if resource_type == 'power':
            values = self.reported_power
            total = self.total_power
        else:
            values = self.reported_bandwidth
            total = self.total_bandwidth
        
        # Compute allocations
        allocation = self.social_welfare_maximization(values, total)
        
        # Compute payments
        payments = np.array([self.vcg_payment(i, values, total) 
                           for i in range(self.num_agents)])
        
        # Compute utilities
        if resource_type == 'power':
            true_vals = self.true_power_values
        else:
            true_vals = self.true_bandwidth_values
            
        utilities = true_vals * allocation - payments
        
        return {
            'allocation': allocation,
            'payments': payments,
            'utilities': utilities,
            'total_welfare': (true_vals * allocation).sum(),
            'total_revenue': payments.sum()
        }
    
    def verify_truthfulness(self, num_tests: int = 100) -> float:
        """
        Verify that truth-telling is indeed optimal.
        
        Returns percentage of cases where truth-telling was optimal.
        """
        truth_optimal_count = 0
        
        for _ in range(num_tests):
            agent = np.random.randint(self.num_agents)
            
            # True report utility
            true_report = self.true_power_values.copy()
            alloc_true = self.social_welfare_maximization(true_report, self.total_power)
            payment_true = self.vcg_payment(agent, true_report, self.total_power)
            utility_true = self.true_power_values[agent] * alloc_true[agent] - payment_true
            
            # Misreport
            misreport = self.true_power_values.copy()
            misreport[agent] = np.random.uniform(0.5, 2.0) * self.true_power_values[agent]
            alloc_mis = self.social_welfare_maximization(misreport, self.total_power)
            payment_mis = self.vcg_payment(agent, misreport, self.total_power)
            utility_mis = self.true_power_values[agent] * alloc_mis[agent] - payment_mis
            
            if utility_true >= utility_mis:
                truth_optimal_count += 1
        
        return truth_optimal_count / num_tests


class AuctionMechanism:
    """
    Various auction mechanisms for bandwidth allocation.
    """
    
    def __init__(self, num_bidders: int = 256, total_bandwidth: float = 1e13):
        self.num_bidders = num_bidders
        self.total_bandwidth = total_bandwidth
        
        # Private valuations
        self.valuations = np.random.uniform(1e9, 1e11, num_bidders)
        
    def first_price_sealed_bid(self, bids: np.ndarray) -> Dict:
        """
        First-price sealed-bid auction.
        Winner pays their bid.
        """
        # Sort by bid (descending)
        sorted_indices = np.argsort(bids)[::-1]
        
        # Allocate to top bidders
        allocation = np.zeros(self.num_bidders)
        payments = np.zeros(self.num_bidders)
        
        remaining = self.total_bandwidth
        for i, idx in enumerate(sorted_indices):
            if remaining <= 0:
                break
            # Allocate proportionally
            alloc = min(remaining, self.total_bandwidth / (i + 1))
            allocation[idx] = alloc
            payments[idx] = alloc * bids[idx] / self.total_bandwidth
            remaining -= alloc
        
        utilities = self.valuations * allocation / self.total_bandwidth - payments
        
        return {
            'allocation': allocation,
            'payments': payments,
            'utilities': utilities,
            'revenue': payments.sum()
        }
    
    def second_price_auction(self, bids: np.ndarray) -> Dict:
        """
        Second-price (Vickrey) auction.
        Winner pays second-highest bid.
        """
        sorted_indices = np.argsort(bids)[::-1]
        
        allocation = np.zeros(self.num_bidders)
        payments = np.zeros(self.num_bidders)
        
        remaining = self.total_bandwidth
        for i, idx in enumerate(sorted_indices):
            if remaining <= 0:
                break
            
            # Second price = next highest bid
            if i < len(sorted_indices) - 1:
                second_price = bids[sorted_indices[i + 1]]
            else:
                second_price = bids[idx] * 0.5
            
            alloc = min(remaining, self.total_bandwidth / (i + 1))
            allocation[idx] = alloc
            payments[idx] = alloc * second_price / self.total_bandwidth
            remaining -= alloc
        
        utilities = self.valuations * allocation / self.total_bandwidth - payments
        
        return {
            'allocation': allocation,
            'payments': payments,
            'utilities': utilities,
            'revenue': payments.sum()
        }
    
    def proportional_allocation(self, bids: np.ndarray) -> Dict:
        """
        Proportional allocation mechanism.
        Each bidder gets share proportional to their bid.
        """
        total_bids = bids.sum()
        if total_bids == 0:
            allocation = np.ones(self.num_bidders) * self.total_bandwidth / self.num_bidders
            payments = np.zeros(self.num_bidders)
        else:
            allocation = bids / total_bids * self.total_bandwidth
            payments = bids  # Pay what you bid
        
        utilities = self.valuations * allocation / self.total_bandwidth - payments / self.total_bandwidth
        
        return {
            'allocation': allocation,
            'payments': payments,
            'utilities': utilities,
            'revenue': payments.sum()
        }


# =============================================================================
# PART 4: MULTI-AGENT REINFORCEMENT LEARNING
# =============================================================================

class PEAgent:
    """
    Individual PE agent with learning capability.
    """
    
    def __init__(self, agent_id: int, num_actions: int = 10):
        self.agent_id = agent_id
        self.num_actions = num_actions
        
        # Q-table for state-action values
        # State: discretized resource level (10 levels)
        # Action: demand level (10 levels)
        self.q_table = np.zeros((10, num_actions))
        
        # Learning parameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        
    def get_state(self, resource_level: float) -> int:
        """Discretize resource level to state index."""
        return min(9, int(resource_level * 10))
    
    def select_action(self, state: int) -> int:
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            return np.argmax(self.q_table[state])
    
    def update(self, state: int, action: int, reward: float, next_state: int):
        """Q-learning update."""
        self.q_table[state, action] += self.alpha * (
            reward + self.gamma * np.max(self.q_table[next_state]) - self.q_table[state, action]
        )


class MultiAgentResourceGame:
    """
    Multi-agent reinforcement learning for resource negotiation.
    """
    
    def __init__(self, num_agents: int = 100, total_resource: float = 1.0):
        self.num_agents = num_agents
        self.total_resource = total_resource
        
        # Create agents
        self.agents = [PEAgent(i) for i in range(num_agents)]
        
        # Resource preferences (heterogeneous)
        self.preferences = np.random.uniform(0.5, 1.5, num_agents)
        
    def get_allocation(self, demands: np.ndarray) -> np.ndarray:
        """Proportional allocation based on demands."""
        total_demand = demands.sum()
        if total_demand == 0:
            return np.ones(self.num_agents) * self.total_resource / self.num_agents
        return demands / total_demand * self.total_resource
    
    def get_reward(self, agent_id: int, allocation: float, demand: float) -> float:
        """
        Reward function for agent.
        Combines utility and fairness.
        """
        # Utility from allocation
        utility = self.preferences[agent_id] * np.log(allocation + 0.01)
        
        # Penalty for greedy demand
        demand_penalty = -0.01 * demand ** 2
        
        return utility + demand_penalty
    
    def run_episode(self) -> Tuple[np.ndarray, np.ndarray]:
        """Run one episode of the game."""
        # Global resource state
        remaining_resource = self.total_resource
        
        demands = np.zeros(self.num_agents)
        actions = np.zeros(self.num_agents, dtype=int)
        
        # Each agent acts
        for i, agent in enumerate(self.agents):
            state = agent.get_state(remaining_resource / self.total_resource)
            action = agent.select_action(state)
            actions[i] = action
            
            # Convert action to demand
            demand = (action + 1) / self.num_agents * 0.1  # Max 10% of total each
            demands[i] = demand
        
        # Compute allocation
        allocation = self.get_allocation(demands)
        
        # Compute rewards and update
        rewards = np.zeros(self.num_agents)
        for i, agent in enumerate(self.agents):
            reward = self.get_reward(i, allocation[i], demands[i])
            rewards[i] = reward
            
            next_state = agent.get_state(allocation[i] / self.total_resource)
            agent.update(agent.get_state(self.total_resource), actions[i], reward, next_state)
        
        return demands, rewards
    
    def train(self, num_episodes: int = 1000) -> Dict:
        """Train agents over multiple episodes."""
        demand_history = []
        reward_history = []
        welfare_history = []
        
        for episode in range(num_episodes):
            demands, rewards = self.run_episode()
            demand_history.append(demands.copy())
            reward_history.append(rewards.copy())
            welfare_history.append(rewards.sum())
        
        return {
            'demand_history': np.array(demand_history),
            'reward_history': np.array(reward_history),
            'welfare_history': np.array(welfare_history),
            'final_demands': demands,
            'final_rewards': rewards
        }


# =============================================================================
# PART 5: FAIRNESS VS EFFICIENCY ANALYSIS
# =============================================================================

class FairnessEfficiencyAnalysis:
    """
    Analyze trade-offs between fairness and efficiency in resource allocation.
    """
    
    def __init__(self, num_players: int = 1024):
        self.num_players = num_players
        self.allocations = None
        
    def jain_fairness_index(self, allocation: np.ndarray) -> float:
        """
        Jain's fairness index.
        J = (Σx_i)^2 / (n * Σx_i^2)
        
        J = 1: Perfect fairness
        J = 1/n: Maximum unfairness
        """
        if allocation.sum() == 0:
            return 0.0
        return (allocation.sum() ** 2) / (self.num_players * (allocation ** 2).sum())
    
    def gini_coefficient(self, allocation: np.ndarray) -> float:
        """
        Gini coefficient for inequality measurement.
        G = 0: Perfect equality
        G = 1: Maximum inequality
        """
        sorted_alloc = np.sort(allocation)
        n = len(allocation)
        index = np.arange(1, n + 1)
        return (2 * (index * sorted_alloc).sum() - (n + 1) * sorted_alloc.sum()) / (n * sorted_alloc.sum())
    
    def nash_social_welfare(self, allocation: np.ndarray) -> float:
        """
        Nash social welfare (geometric mean).
        NSW = Π x_i^(1/n)
        """
        # Add small constant to avoid log(0)
        return np.exp(np.mean(np.log(allocation + 1e-10)))
    
    def utilitarian_welfare(self, allocation: np.ndarray, utilities: np.ndarray) -> float:
        """Sum of utilities."""
        return (allocation * utilities).sum()
    
    def max_min_fairness(self, allocation: np.ndarray) -> float:
        """Maximin welfare - minimum allocation."""
        return allocation.min()
    
    def generate_allocation_spectrum(self, total_resource: float = 1.0,
                                    num_points: int = 100) -> Dict:
        """
        Generate allocations across fairness-efficiency spectrum.
        """
        allocations = []
        fairness_scores = []
        efficiency_scores = []
        
        # Random utilities for efficiency measurement
        utilities = np.random.uniform(0.5, 1.5, self.num_players)
        
        for _ in range(num_points):
            # Generate random allocation on simplex
            params = np.random.dirichlet(np.ones(self.num_players))
            alloc = params * total_resource
            
            allocations.append(alloc)
            fairness_scores.append(self.jain_fairness_index(alloc))
            efficiency_scores.append(self.utilitarian_welfare(alloc, utilities))
        
        return {
            'allocations': np.array(allocations),
            'fairness': np.array(fairness_scores),
            'efficiency': np.array(efficiency_scores)
        }
    
    def find_pareto_optimal(self, allocations: np.ndarray, 
                           fairness: np.ndarray, 
                           efficiency: np.ndarray) -> np.ndarray:
        """Identify Pareto optimal allocations."""
        is_pareto = np.ones(len(allocations), dtype=bool)
        
        for i in range(len(allocations)):
            for j in range(len(allocations)):
                if i != j:
                    # j dominates i if j is better in both dimensions
                    if fairness[j] >= fairness[i] and efficiency[j] >= efficiency[i]:
                        if fairness[j] > fairness[i] or efficiency[j] > efficiency[i]:
                            is_pareto[i] = False
                            break
        
        return is_pareto


# =============================================================================
# MAIN SIMULATION AND VISUALIZATION
# =============================================================================

def run_full_simulation():
    """Run all game-theoretic analyses."""
    print("=" * 70)
    print("Cycle 12: Game-Theoretic Resource Allocation Analysis")
    print("=" * 70)
    
    results = {}
    
    # Part 1: Non-cooperative game
    print("\n[1/5] Running Nash Equilibrium Analysis...")
    pe_game = PEResourceGame(num_players=NUM_PES)
    nash_results = pe_game.find_nash_equilibrium(max_iterations=50)
    results['nash_equilibrium'] = nash_results
    print(f"   Converged: {nash_results['converged']} in {nash_results['iterations']} iterations")
    print(f"   Mean Power Allocation: {nash_results['power_allocation'].mean()*1000:.4f} mW")
    print(f"   Mean Bandwidth Allocation: {nash_results['bandwidth_allocation'].mean()/1e9:.2f} Gbps")
    
    # Part 2: Payoff matrix
    print("\n[2/5] Computing Payoff Matrices...")
    payoff = PayoffMatrix(num_types=4)
    payoff_matrix = payoff.compute_payoff_matrix()
    nash_2player = payoff.find_nash_equilibrium_2player(payoff_matrix)
    results['payoff_matrix'] = payoff_matrix
    results['nash_2player'] = nash_2player
    print(f"   Nash Equilibrium Strategy: {nash_2player['best_pure_strategy']}")
    print(f"   Expected Payoff: {nash_2player['expected_payoff']:.4f}")
    
    # Part 3: Cooperative game
    print("\n[3/5] Running Cooperative Game Analysis...")
    coop_game = CooperativeGame(num_players=64)  # Reduced for tractability
    shapley_values = coop_game.compute_all_shapley_values()
    core_allocation = coop_game.find_core_allocation()
    is_core = coop_game.is_in_core(core_allocation)
    results['shapley_values'] = shapley_values
    results['core_allocation'] = core_allocation
    results['is_in_core'] = is_core
    print(f"   Shapley Value Range: [{shapley_values.min():.4f}, {shapley_values.max():.4f}]")
    print(f"   Core Allocation Sum: {core_allocation.sum():.4f}")
    print(f"   Is in Core: {is_core}")
    
    # Coalition formation
    coalition_game = CoalitionFormation(num_players=64)
    stable_partition = coalition_game.find_stable_partition()
    results['stable_partition'] = stable_partition
    print(f"   Stable Coalitions Found: {len(stable_partition)}")
    print(f"   Mean Coalition Size: {np.mean([len(c) for c in stable_partition]):.1f}")
    
    # Part 4: Mechanism design
    print("\n[4/5] Running Mechanism Design Analysis...")
    vcg = VCGMechanism(num_agents=256)
    vcg_power = vcg.run_vcg_auction('power')
    truthfulness = vcg.verify_truthfulness(num_tests=50)
    results['vcg_power'] = vcg_power
    results['vcg_truthfulness'] = truthfulness
    print(f"   VCG Total Welfare: {vcg_power['total_welfare']:.4f}")
    print(f"   VCG Total Revenue: {vcg_power['total_revenue']:.4f}")
    print(f"   Truthfulness Rate: {truthfulness*100:.1f}%")
    
    # Auction comparison
    auction = AuctionMechanism(num_bidders=256)
    truthful_bids = auction.valuations
    
    fp_auction = auction.first_price_sealed_bid(truthful_bids)
    sp_auction = auction.second_price_auction(truthful_bids)
    prop_alloc = auction.proportional_allocation(truthful_bids)
    
    results['auctions'] = {
        'first_price': fp_auction,
        'second_price': sp_auction,
        'proportional': prop_alloc
    }
    print(f"   First-Price Revenue: {fp_auction['revenue']/1e12:.4f} Tbps-value")
    print(f"   Second-Price Revenue: {sp_auction['revenue']/1e12:.4f} Tbps-value")
    print(f"   Proportional Revenue: {prop_alloc['revenue']/1e12:.4f} Tbps-value")
    
    # Part 5: Multi-agent RL
    print("\n[5/5] Running Multi-Agent RL Training...")
    ma_game = MultiAgentResourceGame(num_agents=100)
    ma_results = ma_game.train(num_episodes=500)
    results['multiagent_rl'] = ma_results
    print(f"   Initial Welfare: {ma_results['welfare_history'][0]:.4f}")
    print(f"   Final Welfare: {ma_results['welfare_history'][-1]:.4f}")
    print(f"   Welfare Improvement: {(ma_results['welfare_history'][-1]/ma_results['welfare_history'][0]-1)*100:.1f}%")
    
    # Part 6: Fairness vs Efficiency
    print("\n[6/6] Analyzing Fairness-Efficiency Tradeoffs...")
    fe_analysis = FairnessEfficiencyAnalysis(num_players=256)
    fe_results = fe_analysis.generate_allocation_spectrum(num_points=200)
    pareto_mask = fe_analysis.find_pareto_optimal(
        fe_results['allocations'], fe_results['fairness'], fe_results['efficiency'])
    results['fairness_efficiency'] = fe_results
    results['pareto_mask'] = pareto_mask
    
    # Compute specific allocations
    uniform_alloc = np.ones(256) / 256
    proportional_alloc = np.random.exponential(1, 256)
    proportional_alloc /= proportional_alloc.sum()
    
    results['specific_allocations'] = {
        'uniform': {
            'jain': fe_analysis.jain_fairness_index(uniform_alloc),
            'gini': fe_analysis.gini_coefficient(uniform_alloc),
            'nash_welfare': fe_analysis.nash_social_welfare(uniform_alloc)
        },
        'proportional': {
            'jain': fe_analysis.jain_fairness_index(proportional_alloc),
            'gini': fe_analysis.gini_coefficient(proportional_alloc),
            'nash_welfare': fe_analysis.nash_social_welfare(proportional_alloc)
        }
    }
    print(f"   Uniform Allocation - Jain Index: {results['specific_allocations']['uniform']['jain']:.4f}")
    print(f"   Proportional Allocation - Jain Index: {results['specific_allocations']['proportional']['jain']:.4f}")
    print(f"   Pareto Optimal Points: {pareto_mask.sum()}")
    
    return results


def create_visualizations(results: Dict):
    """Create comprehensive visualizations."""
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Nash Equilibrium Convergence
    ax1 = fig.add_subplot(3, 3, 1)
    ax1.plot(results['nash_equilibrium']['convergence'])
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Max Strategy Change')
    ax1.set_title('Nash Equilibrium Convergence')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # 2. Power Allocation Distribution
    ax2 = fig.add_subplot(3, 3, 2)
    power_alloc = results['nash_equilibrium']['power_allocation'] * 1000  # mW
    ax2.hist(power_alloc, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    ax2.axvline(power_alloc.mean(), color='red', linestyle='--', label=f'Mean: {power_alloc.mean():.3f} mW')
    ax2.set_xlabel('Power Allocation (mW)')
    ax2.set_ylabel('Number of PEs')
    ax2.set_title('Power Allocation Distribution (Nash Equilibrium)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Payoff Matrix Heatmap
    ax3 = fig.add_subplot(3, 3, 3)
    strategies = ['Low', 'Medium', 'High']
    im = ax3.imshow(results['payoff_matrix'], cmap='RdYlGn', aspect='auto')
    ax3.set_xticks(range(3))
    ax3.set_yticks(range(3))
    ax3.set_xticklabels(strategies)
    ax3.set_yticklabels(strategies)
    ax3.set_xlabel('Player 2 Strategy')
    ax3.set_ylabel('Player 1 Strategy')
    ax3.set_title('Payoff Matrix (2-Player Game)')
    for i in range(3):
        for j in range(3):
            ax3.text(j, i, f'{results["payoff_matrix"][i,j]:.2f}', 
                    ha='center', va='center', color='black')
    plt.colorbar(im, ax=ax3, label='Payoff')
    
    # 4. Shapley Value Distribution
    ax4 = fig.add_subplot(3, 3, 4)
    ax4.hist(results['shapley_values'], bins=30, color='forestgreen', edgecolor='black', alpha=0.7)
    ax4.axvline(np.mean(results['shapley_values']), color='red', linestyle='--', 
                label=f'Mean: {np.mean(results["shapley_values"]):.3f}')
    ax4.set_xlabel('Shapley Value')
    ax4.set_ylabel('Count')
    ax4.set_title('Shapley Value Distribution (PE Contribution)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Coalition Sizes
    ax5 = fig.add_subplot(3, 3, 5)
    coalition_sizes = [len(c) for c in results['stable_partition']]
    ax5.hist(coalition_sizes, bins=20, color='coral', edgecolor='black', alpha=0.7)
    ax5.set_xlabel('Coalition Size')
    ax5.set_ylabel('Count')
    ax5.set_title('Stable Coalition Size Distribution')
    ax5.axvline(np.mean(coalition_sizes), color='red', linestyle='--',
                label=f'Mean: {np.mean(coalition_sizes):.1f}')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. VCG Allocation
    ax6 = fig.add_subplot(3, 3, 6)
    vcg_alloc = results['vcg_power']['allocation']
    sorted_alloc = np.sort(vcg_alloc)[::-1]
    ax6.bar(range(len(sorted_alloc[:50])), sorted_alloc[:50], color='purple', alpha=0.7)
    ax6.set_xlabel('PE Rank')
    ax6.set_ylabel('Power Allocation (W)')
    ax6.set_title('VCG Power Allocation (Top 50 PEs)')
    ax6.grid(True, alpha=0.3)
    
    # 7. Multi-Agent RL Convergence
    ax7 = fig.add_subplot(3, 3, 7)
    welfare = results['multiagent_rl']['welfare_history']
    ax7.plot(welfare, color='darkblue', linewidth=2)
    ax7.fill_between(range(len(welfare)), welfare, alpha=0.3)
    ax7.set_xlabel('Episode')
    ax7.set_ylabel('Total Welfare')
    ax7.set_title('Multi-Agent RL: Welfare Convergence')
    ax7.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(range(len(welfare)), welfare, 1)
    p = np.poly1d(z)
    ax7.plot(range(len(welfare)), p(range(len(welfare))), 'r--', 
             label=f'Trend: +{z[0]*100:.2f}/episode')
    ax7.legend()
    
    # 8. Fairness vs Efficiency Tradeoff
    ax8 = fig.add_subplot(3, 3, 8)
    fairness = results['fairness_efficiency']['fairness']
    efficiency = results['fairness_efficiency']['efficiency']
    pareto = results['pareto_mask']
    
    ax8.scatter(fairness[~pareto], efficiency[~pareto], c='lightgray', alpha=0.5, 
                label='Dominated', s=20)
    ax8.scatter(fairness[pareto], efficiency[pareto], c='red', s=50, 
                label='Pareto Optimal', alpha=0.7)
    ax8.set_xlabel('Jain Fairness Index')
    ax8.set_ylabel('Utilitarian Welfare')
    ax8.set_title('Fairness vs Efficiency Tradeoff')
    ax8.legend()
    ax8.grid(True, alpha=0.3)
    
    # 9. Auction Revenue Comparison
    ax9 = fig.add_subplot(3, 3, 9)
    mechanisms = ['First-Price', 'Second-Price', 'Proportional']
    revenues = [
        results['auctions']['first_price']['revenue'],
        results['auctions']['second_price']['revenue'],
        results['auctions']['proportional']['revenue']
    ]
    revenues_normalized = [r/1e12 for r in revenues]  # Tbps-value
    
    bars = ax9.bar(mechanisms, revenues_normalized, color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                   edgecolor='black', alpha=0.7)
    ax9.set_ylabel('Revenue (Tbps-value)')
    ax9.set_title('Auction Mechanism Revenue Comparison')
    ax9.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, revenues_normalized):
        ax9.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/cycle12_game_theory_analysis.png', 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    # Create second figure for additional visualizations
    fig2 = plt.figure(figsize=(16, 12))
    
    # 10. Gini Coefficient Analysis
    ax10 = fig2.add_subplot(2, 2, 1)
    fe_analysis = FairnessEfficiencyAnalysis(num_players=256)
    
    allocations = results['fairness_efficiency']['allocations']
    gini_values = [fe_analysis.gini_coefficient(a) for a in allocations[:100]]
    jain_values = results['fairness_efficiency']['fairness'][:100]
    
    ax10.scatter(gini_values, jain_values, c='steelblue', alpha=0.6)
    ax10.set_xlabel('Gini Coefficient (Inequality)')
    ax10.set_ylabel('Jain Fairness Index')
    ax10.set_title('Gini vs Jain Fairness Measures')
    ax10.grid(True, alpha=0.3)
    
    # Perfect trade-off line
    ax10.plot([0, 1], [1, 0], 'r--', label='Perfect Inverse')
    ax10.legend()
    
    # 11. Nash Social Welfare Analysis
    ax11 = fig2.add_subplot(2, 2, 2)
    nash_welfare = [fe_analysis.nash_social_welfare(a) for a in allocations[:100]]
    ax11.scatter(jain_values, nash_welfare, c='forestgreen', alpha=0.6)
    ax11.set_xlabel('Jain Fairness Index')
    ax11.set_ylabel('Nash Social Welfare')
    ax11.set_title('Fairness vs Nash Social Welfare')
    ax11.grid(True, alpha=0.3)
    
    # 12. Strategy Evolution in MARL
    ax12 = fig2.add_subplot(2, 2, 3)
    demand_history = results['multiagent_rl']['demand_history']
    
    # Compute mean demand over time
    mean_demands = demand_history.mean(axis=1)
    std_demands = demand_history.std(axis=1)
    
    episodes = range(len(mean_demands))
    ax12.plot(episodes, mean_demands, 'b-', linewidth=2, label='Mean Demand')
    ax12.fill_between(episodes, 
                      mean_demands - std_demands,
                      mean_demands + std_demands,
                      alpha=0.3, color='blue')
    ax12.set_xlabel('Episode')
    ax12.set_ylabel('Mean Demand Level')
    ax12.set_title('Multi-Agent RL: Demand Strategy Evolution')
    ax12.legend()
    ax12.grid(True, alpha=0.3)
    
    # 13. Resource Utilization Heatmap
    ax13 = fig2.add_subplot(2, 2, 4)
    
    # Create PE grid utilization
    grid = np.zeros((32, 32))
    power_alloc = results['nash_equilibrium']['power_allocation']
    for i in range(32):
        for j in range(32):
            idx = i * 32 + j
            if idx < len(power_alloc):
                grid[i, j] = power_alloc[idx]
    
    im = ax13.imshow(grid, cmap='YlOrRd', aspect='equal')
    ax13.set_xlabel('PE Column')
    ax13.set_ylabel('PE Row')
    ax13.set_title('Power Allocation Heatmap (32×32 PE Array)')
    plt.colorbar(im, ax=ax13, label='Power (W)')
    
    plt.tight_layout()
    plt.savefig('/home/z/my-project/research/cycle12_game_theory_extended.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\nVisualizations saved to:")
    print("  - cycle12_game_theory_analysis.png")
    print("  - cycle12_game_theory_extended.png")


if __name__ == "__main__":
    # Run simulation
    results = run_full_simulation()
    
    # Create visualizations
    create_visualizations(results)
    
    # Save results as JSON (convert numpy arrays to lists)
    import json
    
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(i) for i in obj]
        return obj
    
    serializable_results = convert_to_serializable({
        'nash_equilibrium_summary': {
            'converged': results['nash_equilibrium']['converged'],
            'iterations': results['nash_equilibrium']['iterations'],
            'mean_power_allocation_mw': float(results['nash_equilibrium']['power_allocation'].mean() * 1000),
            'std_power_allocation_mw': float(results['nash_equilibrium']['power_allocation'].std() * 1000),
            'mean_bandwidth_allocation_gbps': float(results['nash_equilibrium']['bandwidth_allocation'].mean() / 1e9),
            'mean_utility': float(results['nash_equilibrium']['utilities'].mean())
        },
        'shapley_summary': {
            'mean_shapley': float(np.mean(results['shapley_values'])),
            'std_shapley': float(np.std(results['shapley_values'])),
            'is_core': results['is_in_core'],
            'num_coalitions': len(results['stable_partition'])
        },
        'vcg_summary': {
            'total_welfare': float(results['vcg_power']['total_welfare']),
            'total_revenue': float(results['vcg_power']['total_revenue']),
            'truthfulness_rate': float(results['vcg_truthfulness'])
        },
        'auction_summary': {
            'first_price_revenue': float(results['auctions']['first_price']['revenue']),
            'second_price_revenue': float(results['auctions']['second_price']['revenue']),
            'proportional_revenue': float(results['auctions']['proportional']['revenue'])
        },
        'marl_summary': {
            'initial_welfare': float(results['multiagent_rl']['welfare_history'][0]),
            'final_welfare': float(results['multiagent_rl']['welfare_history'][-1]),
            'improvement_pct': float((results['multiagent_rl']['welfare_history'][-1] / 
                                      results['multiagent_rl']['welfare_history'][0] - 1) * 100)
        },
        'fairness_efficiency_summary': {
            'pareto_optimal_count': int(results['pareto_mask'].sum()),
            'uniform_jain': results['specific_allocations']['uniform']['jain'],
            'uniform_gini': results['specific_allocations']['uniform']['gini'],
            'proportional_jain': results['specific_allocations']['proportional']['jain'],
            'proportional_gini': results['specific_allocations']['proportional']['gini']
        }
    })
    
    with open('/home/z/my-project/research/cycle12_results.json', 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print("\nResults saved to cycle12_results.json")
    print("\n" + "=" * 70)
    print("Cycle 12: Game-Theoretic Resource Allocation Analysis Complete")
    print("=" * 70)
