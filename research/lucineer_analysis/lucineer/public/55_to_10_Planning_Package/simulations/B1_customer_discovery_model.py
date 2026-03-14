"""
Simulation B1: Customer Discovery Model
=======================================
Models customer adoption curve and validates market demand

Uses Bass Diffusion Model with competitive factors

Author: Market Simulation Agent
Date: 2026-03-08
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ============================================================================
# MARKET PARAMETERS
# ============================================================================

@dataclass
class EdgeAIMarket:
    """Edge AI Inference Market Parameters"""
    # Total Addressable Market (TAM)
    tam_usd: float = 2_000_000_000  # $2B global edge AI inference
    tam_units: int = 20_000_000  # ~20M units/year

    # Serviceable Addressable Market (SAM) - low-power inference
    sam_usd: float = 200_000_000  # $200M low-power segment
    sam_units: int = 2_000_000  # ~2M units/year

    # Serviceable Obtainable Market (SOM) - realistic target
    som_usd: float = 20_000_000  # $20M first 3 years
    som_units: int = 200_000  # ~200K units

    # Market growth rate
    cagr: float = 0.25  # 25% CAGR

    # Customer segments
    segments: Dict = None

    def __post_init__(self):
        self.segments = {
            "industrial_iot": {
                "name": "Industrial IoT",
                "size_pct": 0.35,
                "growth_rate": 0.30,
                "price_sensitivity": "medium",
                "decision_cycle_months": 6,
                "adoption_speed": "medium"
            },
            "smart_cameras": {
                "name": "Smart Cameras",
                "size_pct": 0.25,
                "growth_rate": 0.35,
                "price_sensitivity": "high",
                "decision_cycle_months": 4,
                "adoption_speed": "fast"
            },
            "robotics": {
                "name": "Robotics",
                "size_pct": 0.20,
                "growth_rate": 0.40,
                "price_sensitivity": "low",
                "decision_cycle_months": 12,
                "adoption_speed": "slow"
            },
            "maker_prosumer": {
                "name": "Maker/Prosumer",
                "size_pct": 0.15,
                "growth_rate": 0.20,
                "price_sensitivity": "very_high",
                "decision_cycle_months": 1,
                "adoption_speed": "fast"
            },
            "consumer": {
                "name": "Consumer Electronics",
                "size_pct": 0.05,
                "growth_rate": 0.15,
                "price_sensitivity": "very_high",
                "decision_cycle_months": 3,
                "adoption_speed": "fast"
            }
        }


@dataclass
class CompetitivePosition:
    """Our competitive positioning"""
    asp_usd: float = 55.0  # Average selling price
    cogs_usd: float = 15.0  # Cost of goods sold
    efficiency_advantage: float = 2.5  # 2.5x vs competition
    power_advantage: float = 2.0  # 2x lower power
    
    # Competitors
    competitors: Dict = None

    def __post_init__(self):
        self.competitors = {
            "hailo_8": {"price": 100, "power_w": 2.5, "perf": 26, "efficiency": 10.4},
            "google_coral": {"price": 75, "power_w": 2.0, "perf": 4, "efficiency": 2.0},
            "nvidia_jetson_nano": {"price": 99, "power_w": 10, "perf": 20, "efficiency": 2.0},
            "groq": {"price": 500, "power_w": 150, "perf": 1000, "efficiency": 6.7},
            "superinstance": {"price": 55, "power_w": 3.3, "perf": 153.7, "efficiency": 46.6}
        }


# ============================================================================
# BASS DIFFUSION MODEL
# ============================================================================

class BassDiffusionModel:
    """Bass diffusion model for customer adoption"""

    def __init__(self, market_size: float, p: float = 0.03, q: float = 0.38):
        """
        p: innovation coefficient (external influence)
        q: imitation coefficient (internal influence)
        market_size: total potential adopters
        """
        self.M = market_size
        self.p = p
        self.q = q

    def adoption_rate(self, t: int) -> float:
        """Calculate adoption rate at time t"""
        exp_term = np.exp(-(self.p + self.q) * t)
        numerator = (self.p + self.q) ** 2 * exp_term
        denominator = self.p + self.q * exp_term
        return self.M * numerator / (denominator ** 2)

    def cumulative_adoption(self, t: int) -> float:
        """Calculate cumulative adoption at time t"""
        exp_term = np.exp(-(self.p + self.q) * t)
        return self.M * (1 - exp_term) / (self.p + self.q * exp_term) * self.p

    def peak_adoption_time(self) -> float:
        """Calculate time of peak adoption"""
        if self.q == 0:
            return 0
        return -np.log(self.p / self.q) / (self.p + self.q)


# ============================================================================
# CUSTOMER DISCOVERY SIMULATION
# ============================================================================

class CustomerDiscoverySimulation:
    """Simulate customer discovery and adoption"""

    def __init__(self, market: EdgeAIMarket, position: CompetitivePosition):
        self.market = market
        self.position = position
        self.results = {}

    def simulate_segment_adoption(self, segment_key: str, months: int = 36) -> Dict:
        """Simulate adoption for a specific segment"""
        segment = self.market.segments[segment_key]

        # Segment market size
        segment_size = self.market.som_units * segment["size_pct"]

        # Adjust Bass parameters based on segment characteristics
        if segment["adoption_speed"] == "fast":
            p, q = 0.05, 0.45  # Faster adoption
        elif segment["adoption_speed"] == "slow":
            p, q = 0.02, 0.30  # Slower adoption
        else:
            p, q = 0.03, 0.38  # Medium adoption

        # Model adoption
        bass = BassDiffusionModel(segment_size, p, q)

        monthly_adoption = []
        cumulative = []
        for t in range(1, months + 1):
            rate = bass.adoption_rate(t)
            monthly_adoption.append(rate)
            cumulative.append(bass.cumulative_adoption(t))

        return {
            "segment_name": segment["name"],
            "segment_size": segment_size,
            "adoption_speed": segment["adoption_speed"],
            "decision_cycle_months": segment["decision_cycle_months"],
            "monthly_adoption": monthly_adoption,
            "cumulative_adoption": cumulative,
            "peak_month": bass.peak_adoption_time()
        }

    def simulate_price_sensitivity(self, asp: float) -> Dict:
        """Simulate impact of price on adoption"""
        base_price = self.position.asp_usd
        price_ratio = asp / base_price

        # Price elasticity of demand (estimated for edge AI market)
        elasticity = -1.5

        # Demand adjustment
        demand_factor = price_ratio ** elasticity

        return {
            "asp": asp,
            "price_ratio": price_ratio,
            "demand_factor": demand_factor,
            "relative_demand_pct": demand_factor * 100
        }

    def simulate_competitive_capture(self) -> Dict:
        """Simulate market share capture from competitors"""
        our_efficiency = self.position.competitors["superinstance"]["efficiency"]

        capture_rates = {}
        for comp_name, comp_data in self.position.competitors.items():
            if comp_name == "superinstance":
                continue

            # Efficiency ratio
            eff_ratio = our_efficiency / comp_data["efficiency"]

            # Price ratio
            price_ratio = comp_data["price"] / self.position.asp_usd

            # Capture rate based on value proposition
            # Higher efficiency + lower price = higher capture
            value_score = eff_ratio * price_ratio

            # Realistic capture rate (capped at 20% of competitor's market)
            capture_rate = min(0.20, value_score * 0.05)

            capture_rates[comp_name] = {
                "efficiency_ratio": eff_ratio,
                "price_ratio": price_ratio,
                "value_score": value_score,
                "capture_rate": capture_rate
            }

        return capture_rates

    def simulate_interview_outcomes(self, n_interviews: int = 50) -> Dict:
        """Simulate expected customer interview outcomes"""
        # Expected distribution of responses
        response_distribution = {
            "very_interested": 0.15,  # Would sign LOI immediately
            "interested": 0.25,       # Want to see demo/PoC
            "neutral": 0.30,          # Need more information
            "skeptical": 0.20,        # Concerns about new vendor
            "not_interested": 0.10   # Not a fit
        }

        # Simulate outcomes
        np.random.seed(42)
        outcomes = np.random.multinomial(n_interviews, list(response_distribution.values()))

        expected_lois = int(outcomes[0] * 0.8 + outcomes[1] * 0.3)  # Conversion rates
        expected_design_ins = int(outcomes[0] * 0.4)  # From very interested

        return {
            "n_interviews": n_interviews,
            "response_distribution": response_distribution,
            "simulated_outcomes": dict(zip(response_distribution.keys(), outcomes.tolist())),
            "expected_lois": expected_lois,
            "expected_design_ins": expected_design_ins,
            "loi_conversion_rate": expected_lois / n_interviews,
            "design_in_conversion_rate": expected_design_ins / n_interviews
        }

    def project_revenue(self, months: int = 36) -> Dict:
        """Project revenue over time"""
        monthly_revenue = []
        cumulative_revenue = []
        units = []

        # Aggregate across all segments
        total_monthly_units = [0] * months
        for segment_key in self.market.segments.keys():
            seg_result = self.simulate_segment_adoption(segment_key, months)
            for t in range(months):
                total_monthly_units[t] += seg_result["monthly_adoption"][t]

        # Calculate revenue
        cumulative_units = 0
        for t in range(months):
            month_units = int(total_monthly_units[t])
            month_revenue = month_units * self.position.asp_usd
            cumulative_units += month_units

            monthly_revenue.append(month_revenue)
            cumulative_revenue.append(cumulative_units * self.position.asp_usd)
            units.append(month_units)

        # Key milestones
        arr_month_12 = sum(monthly_revenue[9:12]) * 4  # Annualized from Q4
        arr_month_24 = sum(monthly_revenue[21:24]) * 4
        arr_month_36 = sum(monthly_revenue[33:36]) * 4

        return {
            "monthly_revenue": monthly_revenue,
            "cumulative_revenue": cumulative_revenue,
            "monthly_units": units,
            "total_units_36m": sum(units),
            "arr_month_12": arr_month_12,
            "arr_month_24": arr_month_24,
            "arr_month_36": arr_month_36,
            "revenue_36m": cumulative_revenue[-1]
        }

    def run_simulation(self) -> Dict:
        """Run complete customer discovery simulation"""
        # Segment adoption
        segment_results = {}
        for segment_key in self.market.segments.keys():
            segment_results[segment_key] = self.simulate_segment_adoption(segment_key)

        # Interview outcomes
        interview_results = self.simulate_interview_outcomes(50)

        # Competitive capture
        competitive_results = self.simulate_competitive_capture()

        # Revenue projection
        revenue_results = self.project_revenue()

        # Validation
        validation = {
            "target_lois": 5,
            "expected_lois": interview_results["expected_lois"],
            "loi_pass": interview_results["expected_lois"] >= 5,
            "target_design_ins": 2,
            "expected_design_ins": interview_results["expected_design_ins"],
            "design_in_pass": interview_results["expected_design_ins"] >= 2,
            "target_arr_24m": 500000,
            "projected_arr_24m": revenue_results["arr_month_24"],
            "arr_pass": revenue_results["arr_month_24"] >= 500000
        }
        validation["overall_pass"] = all([
            validation["loi_pass"],
            validation["design_in_pass"],
            validation["arr_pass"]
        ])

        self.results = {
            "market": {
                "tam": self.market.tam_usd,
                "sam": self.market.sam_usd,
                "som": self.market.som_usd,
                "segments": len(self.market.segments)
            },
            "positioning": {
                "asp": self.position.asp_usd,
                "efficiency_advantage": self.position.efficiency_advantage
            },
            "segment_adoption": segment_results,
            "interview_outcomes": interview_results,
            "competitive_capture": competitive_results,
            "revenue_projection": revenue_results,
            "validation": validation
        }

        return self.results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Initialize
    market = EdgeAIMarket()
    position = CompetitivePosition()

    # Run simulation
    sim = CustomerDiscoverySimulation(market, position)
    results = sim.run_simulation()

    # Print results
    print("=" * 60)
    print("CUSTOMER DISCOVERY SIMULATION")
    print("=" * 60)

    print(f"\nMarket Size:")
    print(f"  TAM: ${results['market']['tam']/1e9:.1f}B")
    print(f"  SAM: ${results['market']['sam']/1e6:.0f}M")
    print(f"  SOM: ${results['market']['som']/1e6:.0f}M")

    print(f"\nInterview Projections (n=50):")
    print(f"  Very Interested: {results['interview_outcomes']['simulated_outcomes']['very_interested']}")
    print(f"  Interested: {results['interview_outcomes']['simulated_outcomes']['interested']}")
    print(f"  Expected LOIs: {results['interview_outcomes']['expected_lois']}")
    print(f"  Expected Design-Ins: {results['interview_outcomes']['expected_design_ins']}")

    print(f"\nCompetitive Capture Potential:")
    for comp, data in results['competitive_capture'].items():
        print(f"  {comp}: {data['capture_rate']*100:.1f}% capture rate")

    print(f"\nRevenue Projection (36 months):")
    print(f"  Total Units: {results['revenue_projection']['total_units_36m']:,}")
    print(f"  Total Revenue: ${results['revenue_projection']['revenue_36m']/1e6:.1f}M")
    print(f"  ARR Month 12: ${results['revenue_projection']['arr_month_12']/1e3:.0f}K")
    print(f"  ARR Month 24: ${results['revenue_projection']['arr_month_24']/1e3:.0f}K")
    print(f"  ARR Month 36: ${results['revenue_projection']['arr_month_36']/1e3:.0f}K")

    print(f"\nValidation:")
    print(f"  Target: 5+ LOIs, 2+ Design-Ins, $500K ARR @ 24mo")
    print(f"  Actual: {results['validation']['expected_lois']} LOIs, {results['validation']['expected_design_ins']} Design-Ins, ${results['validation']['projected_arr_24m']/1e3:.0f}K ARR")
    print(f"\n  RESULT: {'✅ PASS' if results['validation']['overall_pass'] else '❌ FAIL'}")

    # Save
    with open("/home/z/my-project/download/simulations/B1_customer_discovery_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to B1_customer_discovery_results.json")

    return results


if __name__ == "__main__":
    results = main()
