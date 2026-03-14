"""
Simulation H1: Game Theory Competitive Dynamics
===============================================
Models competitive market responses as evolutionary game theory

Paradigm: Multi-agent strategic simulation
Innovation: Predicts competitor responses and optimal launch timing

Author: Innovation Simulation Agent
Date: 2026-03-08
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import random

# ============================================================================
# STRATEGY DEFINITIONS
# ============================================================================

class Strategy(Enum):
    """Competitor strategies"""
    IGNORE = "ignore"  # Don't respond
    COMPETE_PRICE = "compete_price"  # Lower prices
    COMPETE_PERF = "compete_perf"  # Improve performance
    ACQUIRE = "acquire"  # Try to acquire us
    PIVOT = "pivot"  # Change market focus
    PARTNER = "partner"  # Seek partnership

@dataclass
class Player:
    """Game theory player (competitor or us)"""
    name: str
    market_share: float  # 0-1
    resources: float  # Relative resources
    cost_structure: float  # Lower is better
    tech_capability: float  # 0-1
    aggressiveness: float  # 0-1
    current_strategy: Strategy = Strategy.IGNORE
    
    def payoff(self, opponent: 'Player', our_action: Strategy, their_action: Strategy) -> float:
        """Calculate payoff given actions"""
        # Base payoff matrix (our_action, their_action) -> our_payoff
        base_payoffs = {
            (Strategy.IGNORE, Strategy.IGNORE): 0.0,
            (Strategy.IGNORE, Strategy.COMPETE_PRICE): -0.1,
            (Strategy.IGNORE, Strategy.COMPETE_PERF): -0.15,
            (Strategy.IGNORE, Strategy.ACQUIRE): 0.5,  # Good for us
            (Strategy.IGNORE, Strategy.PARTNER): 0.3,
            
            (Strategy.COMPETE_PRICE, Strategy.IGNORE): 0.1,
            (Strategy.COMPETE_PRICE, Strategy.COMPETE_PRICE): -0.2,
            (Strategy.COMPETE_PRICE, Strategy.COMPETE_PERF): -0.1,
            (Strategy.COMPETE_PRICE, Strategy.ACQUIRE): -0.1,
            
            (Strategy.COMPETE_PERF, Strategy.IGNORE): 0.15,
            (Strategy.COMPETE_PERF, Strategy.COMPETE_PRICE): 0.1,
            (Strategy.COMPETE_PERF, Strategy.COMPETE_PERF): -0.1,
            (Strategy.COMPETE_PERF, Strategy.ACQUIRE): 0.0,
            
            (Strategy.PARTNER, Strategy.IGNORE): 0.2,
            (Strategy.PARTNER, Strategy.PARTNER): 0.4,
            (Strategy.PARTNER, Strategy.ACQUIRE): 0.3,
        }
        
        payoff = base_payoffs.get((our_action, their_action), 0.0)
        
        # Modify by player characteristics
        payoff *= (1 + 0.5 * (self.tech_capability - opponent.tech_capability))
        payoff *= (1 + 0.3 * (self.resources - opponent.resources) / max(opponent.resources, 0.1))
        
        return payoff


# ============================================================================
# COMPETITIVE LANDSCAPE
# ============================================================================

class CompetitiveLandscape:
    """Define the competitive landscape"""
    
    def __init__(self):
        self.players = self._initialize_players()
        self.our_player = Player(
            name="SuperInstance",
            market_share=0.0,
            resources=0.1,  # Small startup
            cost_structure=0.7,  # Good cost structure
            tech_capability=0.9,  # High tech capability
            aggressiveness=0.7
        )
    
    def _initialize_players(self) -> List[Player]:
        """Initialize competitor players"""
        return [
            Player(
                name="Hailo",
                market_share=0.15,
                resources=0.5,
                cost_structure=0.6,
                tech_capability=0.7,
                aggressiveness=0.6
            ),
            Player(
                name="Google_Coral",
                market_share=0.20,
                resources=1.0,
                cost_structure=0.4,
                tech_capability=0.8,
                aggressiveness=0.3
            ),
            Player(
                name="NVIDIA_Jetson",
                market_share=0.35,
                resources=1.0,
                cost_structure=0.3,
                tech_capability=0.95,
                aggressiveness=0.5
            ),
            Player(
                name="Qualcomm",
                market_share=0.10,
                resources=0.9,
                cost_structure=0.5,
                tech_capability=0.85,
                aggressiveness=0.7
            ),
            Player(
                name="Groq",
                market_share=0.05,
                resources=0.4,
                cost_structure=0.4,
                tech_capability=0.9,
                aggressiveness=0.8
            ),
            Player(
                name="Taalas",
                market_share=0.0,
                resources=0.6,
                cost_structure=0.5,
                tech_capability=0.85,
                aggressiveness=0.9
            ),
        ]
    
    def get_competitor_by_name(self, name: str) -> Optional[Player]:
        """Get competitor by name"""
        for p in self.players:
            if p.name == name:
                return p
        return None


# ============================================================================
# GAME THEORY SIMULATION
# ============================================================================

class GameTheorySimulation:
    """
    Simulate competitive dynamics using game theory
    """
    
    def __init__(self, landscape: CompetitiveLandscape):
        self.landscape = landscape
        self.history = []
    
    def nash_equilibrium(self, player1: Player, player2: Player) -> Tuple[Strategy, Strategy]:
        """
        Find Nash equilibrium strategies for two players.
        Uses iterated best response.
        """
        strategies = list(Strategy)
        
        # Initialize with random strategies
        best_s1 = random.choice(strategies)
        best_s2 = random.choice(strategies)
        
        # Iterate to find equilibrium
        for _ in range(20):
            # Player 1's best response
            best_payoff = float('-inf')
            for s1 in strategies:
                payoff = player1.payoff(player2, s1, best_s2)
                if payoff > best_payoff:
                    best_payoff = payoff
                    best_s1 = s1
            
            # Player 2's best response
            best_payoff = float('-inf')
            for s2 in strategies:
                payoff = player2.payoff(player1, best_s2, s1)  # Reversed perspective
                if payoff > best_payoff:
                    best_payoff = payoff
                    best_s2 = s2
        
        return best_s1, best_s2
    
    def simulate_market_entry(self, years: int = 5) -> List[Dict]:
        """
        Simulate our market entry and competitor responses
        """
        results = []
        our_share = 0.0
        
        for year in range(1, years + 1):
            year_results = {"year": year}
            
            # Our market share growth (Bass diffusion)
            growth_rate = 0.15 if year <= 2 else 0.25
            our_share = min(our_share + growth_rate * (1 - our_share), 0.3)
            self.landscape.our_player.market_share = our_share
            
            # Competitor responses
            competitor_responses = {}
            
            for competitor in self.landscape.players:
                # Determine competitor's likely response
                _, their_strategy = self.nash_equilibrium(
                    self.landscape.our_player, 
                    competitor
                )
                
                # Apply response effect
                if their_strategy == Strategy.COMPETE_PRICE:
                    competitor.market_share *= 0.95
                elif their_strategy == Strategy.COMPETE_PERF:
                    competitor.tech_capability = min(competitor.tech_capability + 0.02, 1.0)
                elif their_strategy == Strategy.ACQUIRE:
                    # Acquisition probability
                    if competitor.resources > 0.5 and random.random() < 0.1:
                        year_results["acquisition_offer"] = competitor.name
                
                competitor_responses[competitor.name] = {
                    "strategy": their_strategy.value,
                    "market_share": competitor.market_share
                }
            
            year_results["our_market_share"] = our_share
            year_results["competitor_responses"] = competitor_responses
            year_results["total_market"] = our_share + sum(
                c.market_share for c in self.landscape.players
            )
            
            results.append(year_results)
            self.history.append(year_results)
        
        return results
    
    def calculate_optimal_launch_timing(self) -> Dict:
        """
        Calculate optimal launch timing considering competitor product cycles
        """
        # Competitor product cycles (months until next major release)
        competitor_cycles = {
            "Hailo": 12,
            "Google_Coral": 18,
            "NVIDIA_Jetson": 6,
            "Qualcomm": 12,
            "Groq": 9,
            "Taalas": 18
        }
        
        # Find window where competitors are weakest
        best_window = None
        best_score = -1
        
        for launch_month in range(1, 25):
            # Calculate vulnerability score for each competitor at this time
            total_vulnerability = 0
            for name, cycle in competitor_cycles.items():
                # Competitors are most vulnerable right before a launch
                months_since_last = launch_month % cycle
                vulnerability = abs(months_since_last - cycle/2) / (cycle/2)
                total_vulnerability += vulnerability
            
            # Adjust for market seasonality (Q4 is best for hardware)
            seasonality = 1.0
            quarter = (launch_month - 1) // 3 + 1
            if quarter == 4:
                seasonality = 1.2
            elif quarter == 1:
                seasonality = 1.1
            
            score = total_vulnerability * seasonality
            
            if score > best_score:
                best_score = score
                best_window = {
                    "launch_month": launch_month,
                    "quarter": quarter,
                    "vulnerability_score": total_vulnerability,
                    "seasonality_factor": seasonality,
                    "overall_score": score
                }
        
        return best_window
    
    def calculate_dominant_strategy(self) -> Dict:
        """
        Find dominant strategy for us against each competitor
        """
        strategies = list(Strategy)
        dominant = {}
        
        for competitor in self.landscape.players:
            # Calculate expected payoff for each of our strategies
            strategy_payoffs = {}
            
            for our_strategy in strategies:
                total_payoff = 0
                for their_strategy in strategies:
                    # Weight by probability of their strategy
                    prob = self._strategy_probability(competitor, their_strategy)
                    payoff = self.landscape.our_player.payoff(
                        competitor, our_strategy, their_strategy
                    )
                    total_payoff += prob * payoff
                
                strategy_payoffs[our_strategy.value] = total_payoff
            
            best_strategy = max(strategy_payoffs, key=strategy_payoffs.get)
            dominant[competitor.name] = {
                "best_strategy": best_strategy,
                "expected_payoff": strategy_payoffs[best_strategy],
                "all_payoffs": strategy_payoffs
            }
        
        return dominant
    
    def _strategy_probability(self, player: Player, strategy: Strategy) -> float:
        """Estimate probability of player choosing strategy"""
        # Simple heuristic based on player characteristics
        base_probs = {
            Strategy.IGNORE: 0.3,
            Strategy.COMPETE_PRICE: 0.2,
            Strategy.COMPETE_PERF: 0.2,
            Strategy.ACQUIRE: 0.1,
            Strategy.PIVOT: 0.1,
            Strategy.PARTNER: 0.1
        }
        
        # Adjust by aggressiveness
        if strategy in [Strategy.COMPETE_PRICE, Strategy.COMPETE_PERF]:
            base_probs[strategy] *= (0.5 + player.aggressiveness)
        elif strategy == Strategy.ACQUIRE:
            base_probs[strategy] *= player.resources
        
        # Normalize
        total = sum(base_probs.values())
        return base_probs[strategy] / total
    
    def simulate_price_war(self) -> Dict:
        """
        Simulate potential price war scenarios
        """
        # Starting prices
        our_price = 55
        competitor_prices = {"Hailo": 100, "Google_Coral": 75, "NVIDIA_Jetson": 99}
        
        results = []
        
        for round_num in range(10):
            round_result = {"round": round_num, "prices": {}}
            
            # Our pricing decision
            min_competitor_price = min(competitor_prices.values())
            if our_price > min_competitor_price * 0.8:
                # Reduce price to compete
                our_price *= 0.95
            round_result["our_price"] = our_price
            
            # Competitor responses
            for name, price in competitor_prices.items():
                if price > our_price * 1.5:
                    # They can undercut
                    competitor_prices[name] = price * 0.9
                round_result["prices"][name] = competitor_prices[name]
            
            # Check for equilibrium
            if round_num > 0:
                price_changes = [
                    abs(our_price - results[-1]["our_price"]) / our_price,
                    *[abs(competitor_prices[n] - results[-1]["prices"][n]) / competitor_prices[n]
                      for n in competitor_prices]
                ]
                if all(p < 0.01 for p in price_changes):
                    round_result["equilibrium_reached"] = True
                    results.append(round_result)
                    break
            
            results.append(round_result)
        
        return {
            "rounds": results,
            "final_our_price": our_price,
            "final_competitor_prices": competitor_prices,
            "our_margin_impact": (55 - our_price) / 55
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("GAME THEORY COMPETITIVE DYNAMICS SIMULATION")
    print("=" * 60)
    
    # Initialize
    landscape = CompetitiveLandscape()
    simulation = GameTheorySimulation(landscape)
    
    # 1. Market Entry Simulation
    print("\n1. Market Entry Simulation (5 years):")
    market_results = simulation.simulate_market_entry(5)
    
    for year_data in market_results:
        print(f"\n  Year {year_data['year']}:")
        print(f"    Our Market Share: {year_data['our_market_share']*100:.1f}%")
        if "acquisition_offer" in year_data:
            print(f"    ⚠️ Acquisition Offer from: {year_data['acquisition_offer']}")
    
    # 2. Optimal Launch Timing
    print("\n2. Optimal Launch Timing:")
    timing = simulation.calculate_optimal_launch_timing()
    print(f"  Best Launch Month: {timing['launch_month']}")
    print(f"  Quarter: Q{timing['quarter']}")
    print(f"  Vulnerability Score: {timing['vulnerability_score']:.2f}")
    print(f"  Seasonality Factor: {timing['seasonality_factor']:.1f}")
    
    # 3. Dominant Strategies
    print("\n3. Dominant Strategies vs Each Competitor:")
    dominant = simulation.calculate_dominant_strategy()
    for competitor, data in dominant.items():
        print(f"  vs {competitor}: {data['best_strategy']} (payoff: {data['expected_payoff']:.2f})")
    
    # 4. Price War Simulation
    print("\n4. Price War Simulation:")
    price_war = simulation.simulate_price_war()
    print(f"  Rounds to Equilibrium: {len(price_war['rounds'])}")
    print(f"  Final Our Price: ${price_war['final_our_price']:.0f}")
    print(f"  Margin Impact: {price_war['our_margin_impact']*100:.1f}% reduction")
    
    # Validation
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    
    final_share = market_results[-1]["our_market_share"]
    validation = {
        "target_market_share": 0.10,
        "actual_market_share": final_share,
        "market_share_pass": final_share >= 0.10,
        "acquisition_probability": any("acquisition_offer" in y for y in market_results),
        "optimal_launch_window": timing["quarter"] == 4,
        "overall_pass": final_share >= 0.10
    }
    
    print(f"\nMarket Share Target: 10%")
    print(f"Projected Share: {final_share*100:.1f}%")
    print(f"Acquisition Interest: {'Yes' if validation['acquisition_probability'] else 'Unknown'}")
    print(f"Optimal Launch: Q{timing['quarter']}")
    print(f"\n  RESULT: {'✅ PASS' if validation['overall_pass'] else '⚠️ CAUTION'}")
    
    # Compile results
    results = {
        "market_entry_simulation": market_results,
        "optimal_launch_timing": timing,
        "dominant_strategies": dominant,
        "price_war_simulation": price_war,
        "validation": validation
    }
    
    # Save
    with open("/home/z/my-project/download/simulations/H1_game_theory_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to H1_game_theory_results.json")
    
    return results


if __name__ == "__main__":
    results = main()
