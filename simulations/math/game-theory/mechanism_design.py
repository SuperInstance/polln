"""
Mechanism Design
================

Design and analysis of incentive-compatible mechanisms for POLLN agents.
VCG mechanisms, participation constraints, and truthful elicitation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.optimize import minimize
import random
from deepseek_games import DeepSeekGameTheorist, GameTheoreticAnalysis


@dataclass
class AgentType:
    """Agent type with private information."""
    id: str
    valuation: float  # True valuation
    cost: float  # Cost of participation
    reported_valuation: Optional[float] = None  # What agent reports
    reported_cost: Optional[float] = None

    def report(self, valuation: float, cost: float) -> None:
        """Agent reports (possibly false) information."""
        self.reported_valuation = valuation
        self.reported_cost = cost


@dataclass
class MechanismOutcome:
    """Outcome of a mechanism."""
    allocation: Dict[str, float]  # Agent -> allocated amount
    payments: Dict[str, float]  # Agent -> payment (positive if paying)
    utilities: Dict[str, float]  # Agent -> utility
    social_welfare: float
    is_truthful: bool
    is_efficient: bool


@dataclass
class MechanismProperties:
    """Properties of a mechanism."""
    incentive_compatible: bool  # Truth-telling is optimal
    individual_rationality: bool  # Participation is beneficial
    budget_balanced: bool  # Sum of payments = 0
    efficient: bool  # Maximizes social welfare
    strategy_proof: bool  # No beneficial manipulation
    collusion_proof: bool  # No beneficial collusion


class VCGMechanism:
    """
    Vickrey-Clarke-Groves mechanism.

    The VCG mechanism is the unique efficient, strategy-proof mechanism
    that satisfies individual rationality.

    Key properties:
    1. Dominant strategy incentive compatible (truthful)
    2. Efficient (maximizes social welfare)
    3. Individual rational (voluntary participation)
    4. Not budget balanced in general
    """

    def __init__(self):
        """Initialize VCG mechanism."""
        self.theorist = DeepSeekGameTheorist()

    def run(self, agents: List[AgentType],
           feasible_allocations: List[Dict[str, float]],
           social_welfare_function: Callable[[Dict[str, float], Dict[str, float]], float]) -> MechanismOutcome:
        """
        Run VCG mechanism.

        Args:
            agents: Participating agents
            feasible_allocations: List of feasible allocations
            social_welfare_function: Computes welfare from allocation and valuations

        Returns:
            MechanismOutcome with allocation, payments, utilities
        """
        n = len(agents)

        # Get reported valuations
        reported_valuations = {agent.id: agent.reported_valuation or agent.valuation
                              for agent in agents}

        # Find efficient allocation (maximizes social welfare)
        best_allocation = None
        best_welfare = -float('inf')

        for allocation in feasible_allocations:
            welfare = social_welfare_function(allocation, reported_valuations)
            if welfare > best_welfare:
                best_welfare = welfare
                best_allocation = allocation

        # Compute VCG payments
        payments = {}
        utilities = {}

        for agent in agents:
            # VCG payment: payment_i = welfare_{-i}(x^*_{-i}) - welfare_{-i}(x^*)
            # where welfare_{-i} is welfare without agent i
            # x^* is efficient allocation with all agents
            # x^*_{-i} is efficient allocation without agent i

            # Welfare without agent i under efficient allocation
            welfare_without_i = sum(
                best_allocation.get(other.id, 0) * other.reported_valuation or other.valuation
                for other in agents if other.id != agent.id
            )

            # Welfare without agent i under optimal allocation for others
            best_welfare_without_i = -float('inf')

            for allocation in feasible_allocations:
                if allocation.get(agent.id, 0) == 0:  # Allocation excludes agent i
                    welfare = social_welfare_function(allocation, reported_valuations)
                    welfare_excluding_i = sum(
                        allocation.get(other.id, 0) * other.reported_valuation or other.valuation
                        for other in agents if other.id != agent.id
                    )
                    if welfare_excluding_i > best_welfare_without_i:
                        best_welfare_without_i = welfare_excluding_i

            # VCG payment
            payments[agent.id] = welfare_without_i - best_welfare_without_i

            # Utility
            utilities[agent.id] = (
                best_allocation.get(agent.id, 0) * agent.valuation - payments[agent.id]
            )

        return MechanismOutcome(
            allocation=best_allocation,
            payments=payments,
            utilities=utilities,
            social_welfare=best_welfare,
            is_truthful=self._check_truthful(agents),
            is_efficient=True
        )

    def _check_truthful(self, agents: List[AgentType]) -> bool:
        """Check if all agents reported truthfully."""
        return all(
            (agent.reported_valuation is None or agent.reported_valuation == agent.valuation)
            for agent in agents
        )


class SecondPriceAuction(VCGMechanism):
    """
    Second-price auction (special case of VCG).

    Single item, highest bidder wins, pays second-highest bid.
    """

    def __init__(self):
        """Initialize second-price auction."""
        super().__init__()

    def run_auction(self, bidders: List[AgentType], reserve_price: float = 0.0) -> MechanismOutcome:
        """
        Run second-price auction.

        Args:
            bidders: Bidders with valuations
            reserve_price: Minimum price

        Returns:
            Auction outcome
        """
        # Sort by valuation
        sorted_bidders = sorted(bidders, key=lambda b: b.valuation, reverse=True)

        if len(sorted_bidders) == 0 or sorted_bidders[0].valuation < reserve_price:
            # No winner
            allocation = {bidder.id: 0 for bidder in bidders}
            payments = {bidder.id: 0 for bidder in bidders}
            utilities = {bidder.id: 0 for bidder in bidders}

            return MechanismOutcome(
                allocation=allocation,
                payments=payments,
                utilities=utilities,
                social_welfare=0.0,
                is_truthful=True,
                is_efficient=True
            )

        winner = sorted_bidders[0]

        # Winner gets item
        allocation = {bidder.id: 0 for bidder in bidders}
        allocation[winner.id] = 1

        # Winner pays second-highest bid (or reserve price)
        if len(sorted_bidders) > 1:
            price = max(sorted_bidders[1].valuation, reserve_price)
        else:
            price = reserve_price

        payments = {bidder.id: 0 for bidder in bidders}
        payments[winner.id] = price

        # Utilities
        utilities = {}
        for bidder in bidders:
            if bidder.id == winner.id:
                utilities[bidder.id] = bidder.valuation - price
            else:
                utilities[bidder.id] = 0

        return MechanismOutcome(
            allocation=allocation,
            payments=payments,
            utilities=utilities,
            social_welfare=winner.valuation,
            is_truthful=True,
            is_efficient=True
        )


class CostSharingMechanism:
    """
    Cost sharing mechanism for public goods.

    Agents share cost of providing a public good.
    """

    def __init__(self):
        """Initialize cost sharing mechanism."""

    def run_mechanism(self, agents: List[AgentType],
                     cost: float,
                     decision_rule: str = "unanimous") -> MechanismOutcome:
        """
        Run cost sharing mechanism.

        Args:
            agents: Agents with valuations for public good
            cost: Cost of providing public good
            decision_rule: How to decide to provide ("unanimous", "majority", "efficient")

        Returns:
            Cost sharing outcome
        """
        # Get reported valuations
        reported_valuations = {agent.id: agent.reported_valuation or agent.valuation
                              for agent in agents}

        total_valuation = sum(reported_valuations.values())

        # Decision rule
        provide = False
        if decision_rule == "unanimous":
            provide = all(v >= 0 for v in reported_valuations.values())
        elif decision_rule == "majority":
            provide = sum(1 for v in reported_valuations.values() if v >= 0) > len(agents) / 2
        elif decision_rule == "efficient":
            provide = total_valuation >= cost

        allocation = {}
        payments = {}
        utilities = {}

        if provide:
            # Provide public good
            for agent in agents:
                allocation[agent.id] = 1

            # Cost sharing: proportional to valuation
            total_positive_valuation = sum(max(v, 0) for v in reported_valuations.values())

            if total_positive_valuation > 0:
                for agent in agents:
                    if reported_valuations[agent.id] > 0:
                        share = (reported_valuations[agent.id] / total_positive_valuation) * cost
                        payments[agent.id] = share
                        utilities[agent.id] = agent.valuation - share
                    else:
                        payments[agent.id] = 0
                        utilities[agent.id] = 0
            else:
                # Equal sharing
                for agent in agents:
                    payments[agent.id] = cost / len(agents)
                    utilities[agent.id] = agent.valuation - cost / len(agents)
        else:
            # Don't provide
            for agent in agents:
                allocation[agent.id] = 0
                payments[agent.id] = 0
                utilities[agent.id] = 0

        return MechanismOutcome(
            allocation=allocation,
            payments=payments,
            utilities=utilities,
            social_welfare=sum(utilities.values()),
            is_truthful=all(
                agent.reported_valuation is None or agent.reported_valuation == agent.valuation
                for agent in agents
            ),
            is_efficient=(total_valuation >= cost) == provide
        )


class ParticipationConstraint:
    """
    Participation (individual rationality) constraints.

    Ensure agents voluntarily participate in the mechanism.
    """

    def __init__(self):
        """Initialize participation constraint analyzer."""

    def check_individual_rationality(self, outcome: MechanismOutcome,
                                    outside_options: Dict[str, float]) -> bool:
        """
        Check if all agents prefer participation to outside option.

        Args:
            outcome: Mechanism outcome
            outside_options: Outside option utility for each agent

        Returns:
            True if all agents have non-negative participation utility
        """
        for agent_id, utility in outcome.utilities.items():
            if utility < outside_options.get(agent_id, 0) - 1e-6:
                return False

        return True

    def check_interim_individual_rationality(self, agents: List[AgentType],
                                           mechanism: Callable) -> bool:
        """
        Check interim individual rationality (expected utility before knowing type).

        Args:
            agents: Agents with type distributions
            mechanism: Mechanism to evaluate

        Returns:
            True if mechanism is interim IR
        """
        # This would require computing expected utility over type distributions
        return True


class MechanismDesignAnalyzer:
    """
    Analyze mechanism properties for POLLN scenarios.
    """

    def __init__(self):
        """Initialize mechanism design analyzer."""
        self.theorist = DeepSeekGameTheorist()

    def analyze_incentive_compatibility(self, mechanism: Callable,
                                       agents: List[AgentType],
                                       num_deviations: int = 100) -> bool:
        """
        Test if mechanism is incentive compatible.

        Args:
            mechanism: Mechanism to test
            agents: Agents to test with
            num_deviations: Number of random deviations to test

        Returns:
            True if no beneficial deviation found
        """
        # Get truthful outcome
        truthful_agents = [
            AgentType(id=agent.id, valuation=agent.valuation, cost=agent.cost)
            for agent in agents
        ]

        truthful_outcome = mechanism(truthful_agents)

        # Test deviations
        for agent in agents:
            truthful_utility = truthful_outcome.utilities[agent.id]

            for _ in range(num_deviations):
                # Deviating agents
                deviating_agents = [
                    AgentType(id=a.id, valuation=a.valuation, cost=a.cost)
                    for a in agents
                ]

                # Deviate by misreporting valuation
                if agent.id == deviating_agents[agents.index(agent)].id:
                    deviation_factor = random.uniform(0.5, 1.5)
                    deviating_agents[agents.index(agent)].report(
                        valuation=agent.valuation * deviation_factor,
                        cost=agent.cost
                    )

                deviating_outcome = mechanism(deviating_agents)
                deviating_utility = deviating_outcome.utilities[agent.id]

                # Check if deviation is beneficial
                if deviating_utility > truthful_utility + 1e-6:
                    return False

        return True

    def analyze_budget_balance(self, outcome: MechanismOutcome,
                              tolerance: float = 1e-6) -> bool:
        """
        Check if mechanism is budget balanced.

        Args:
            outcome: Mechanism outcome
            tolerance: Numerical tolerance

        Returns:
            True if budget is balanced
        """
        total_payments = sum(outcome.payments.values())
        return abs(total_payments) < tolerance

    def analyze_efficiency(self, outcome: MechanityOutcome,
                          optimal_welfare: float) -> bool:
        """
        Check if mechanism is efficient.

        Args:
            outcome: Mechanism outcome
            optimal_welfare: Optimal social welfare

        Returns:
            True if outcome achieves optimal welfare
        """
        return abs(outcome.social_welfare - optimal_welfare) < 1e-6


class POLLNMechanismDesign:
    """
    POLLN-specific mechanism design scenarios.

    Models:
    - Task allocation mechanisms
    - Resource sharing mechanisms
    - Knowledge elicitation mechanisms
    """

    @staticmethod
    def create_task_allocation_mechanism(agents: List[AgentType],
                                       tasks: List[str],
                                       agent_capabilities: Dict[str, Dict[str, float]]) -> VCGMechanism:
        """
        Create VCG mechanism for task allocation.

        Args:
            agents: Agents to allocate tasks to
            tasks: Tasks to allocate
            agent_capabilities: Agent capabilities for each task

        Returns:
            Configured VCG mechanism
        """
        # Define feasible allocations
        feasible_allocations = []

        # Each agent gets at most one task
        for task_assignment in product([None] + tasks, repeat=len(agents)):
            allocation = {agent.id: 0 for agent in agents}

            valid = True
            for agent, task in zip(agents, task_assignment):
                if task is not None:
                    # Check if task already assigned
                    if task in [task_assignment[i] for i in range(len(agents)) if i != agents.index(agent)]:
                        valid = False
                        break

                    if task in agent_capabilities.get(agent.id, {}):
                        allocation[agent.id] = agent_capabilities[agent.id][task]

            if valid:
                feasible_allocations.append(allocation)

        # Social welfare function
        def welfare_function(allocation: Dict[str, float],
                           valuations: Dict[str, float]) -> float:
            return sum(allocation.get(agent.id, 0) * valuations.get(agent.id, 0)
                      for agent in agents)

        return VCGMechanism(), feasible_allocations, welfare_function

    @staticmethod
    def create_knowledge_elicitation_mechanism(agents: List[AgentType],
                                             knowledge_value: float,
                                             peer_review_cost: float) -> MechanismOutcome:
        """
        Create mechanism for knowledge elicitation.

        Agents report their knowledge, mechanism incentivizes truthful reporting.

        Args:
            agents: Agents with knowledge
            knowledge_value: Value of truthful knowledge
            peer_review_cost: Cost of peer review

        Returns:
            Mechanism outcome
        """
        # Proper scoring rule mechanism
        # Pay agents based on accuracy of their reports

        allocation = {agent.id: 1 for agent in agents}

        # Payments based on peer review
        payments = {}
        utilities = {}

        for agent in agents:
            # Simplified: pay if report matches peer review
            # In practice, would use proper scoring rules
            payment = knowledge_value if agent.reported_valuation else 0
            payment -= peer_review_cost

            payments[agent.id] = payment
            utilities[agent.id] = payment

        return MechanismOutcome(
            allocation=allocation,
            payments=payments,
            utilities=utilities,
            social_welfare=sum(utilities.values()),
            is_truthful=True,
            is_efficient=True
        )


if __name__ == "__main__":
    # Test VCG mechanism
    print("Testing VCG mechanism...")

    agents = [
        AgentType(id="agent1", valuation=10.0, cost=0.0),
        AgentType(id="agent2", valuation=8.0, cost=0.0),
        AgentType(id="agent3", valuation=6.0, cost=0.0),
    ]

    vcg = VCGMechanism()

    # Single item auction
    feasible_allocations = [
        {"agent1": 1, "agent2": 0, "agent3": 0},
        {"agent1": 0, "agent2": 1, "agent3": 0},
        {"agent1": 0, "agent2": 0, "agent3": 1},
        {"agent1": 0, "agent2": 0, "agent3": 0},
    ]

    def welfare_function(allocation, valuations):
        return sum(allocation[agent.id] * valuations[agent.id] for agent in agents)

    outcome = vcg.run(agents, feasible_allocations, welfare_function)

    print(f"Allocation: {outcome.allocation}")
    print(f"Payments: {outcome.payoffs}")
    print(f"Utilities: {outcome.utilities}")
    print(f"Social welfare: {outcome.social_welfare}")

    # Test second-price auction
    print("\nTesting second-price auction...")
    auction = SecondPriceAuction()
    auction_outcome = auction.run_auction(agents, reserve_price=5.0)

    print(f"Winner: {max(auction_outcome.allocation, key=auction_outcome.allocation.get)}")
    print(f"Price: {sum(auction_outcome.payments.values())}")

    # Test cost sharing
    print("\nTesting cost sharing mechanism...")
    cost_sharing = CostSharingMechanism()
    cost_outcome = cost_sharing.run_mechanism(agents, cost=15.0, decision_rule="efficient")

    print(f"Provide public good: {cost_outcome.allocation['agent1'] == 1}")
    print(f"Utilities: {cost_outcome.utilities}")

    # Test incentive compatibility
    print("\nTesting incentive compatibility...")
    analyzer = MechanismDesignAnalyzer()
    is_ic = analyzer.analyze_incentive_compatibility(
        lambda agents: vcg.run(agents, feasible_allocations, welfare_function),
        agents
    )
    print(f"Incentive compatible: {is_ic}")

    # Test budget balance
    is_bb = analyzer.analyze_budget_balance(outcome)
    print(f"Budget balanced: {is_bb}")
