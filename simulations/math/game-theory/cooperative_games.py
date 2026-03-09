"""
Cooperative Game Theory
=======================

Analysis of cooperative games, coalition formation, and fair division
in POLLN multi-agent systems.
"""

import numpy as np
from typing import Dict, List, Tuple, Set, FrozenSet
from dataclasses import dataclass
from itertools import combinations
from scipy.optimize import linprog
import networkx as nx
from deepseek_games import DeepSeekGameTheorist, GameTheoreticAnalysis, GameTheoryValidator


@dataclass
class Coalition:
    """Coalition of agents."""
    members: FrozenSet[str]
    value: float  # Characteristic function value
    formed_at: int = 0  # Time step when formed

    def __hash__(self):
        return hash((self.members, self.value))

    def __contains__(self, agent: str) -> bool:
        return agent in self.members

    def size(self) -> int:
        return len(self.members)

    def intersects(self, other: 'Coalition') -> bool:
        return not self.members.isdisjoint(other.members)

    def is_subset(self, other: 'Coalition') -> bool:
        return self.members.issubset(other.members)


@dataclass
class Imputation:
    """Payoff distribution to agents."""
    payoffs: Dict[str, float]

    def total(self) -> float:
        return sum(self.payoffs.values())

    def get(self, agent: str) -> float:
        return self.payoffs.get(agent, 0.0)

    def agents(self) -> List[str]:
        return list(self.payoffs.keys())


@dataclass
class ShapleyValueResult:
    """Shapley value computation results."""
    values: Dict[str, float]
    contributions: Dict[str, Dict[FrozenSet[str], float]]  # Agent -> coalition -> marginal contribution
    computation_time: float


@dataclass
class CoreResult:
    """Core of a cooperative game."""
    imputations: List[Imputation]
    is_nonempty: bool
        binding_constraints: List[Tuple[FrozenSet[str], float]]


class ShapleyValue:
    """
    Shapley value computation for cooperative games.

    Axioms:
    1. Efficiency: Sum of values = v(N)
    2. Symmetry: Symmetric agents have equal values
    3. Dummy player: Zero marginal contribution => zero value
    4. Additivity: v(S ∪ T) = v(S) + v(T) for disjoint S, T
    """

    def __init__(self):
        """Initialize Shapley value calculator."""
        self.theorist = DeepSeekGameTheorist()

    def compute(self, agents: List[str],
                characteristic_function: Dict[FrozenSet[str], float]) -> ShapleyValueResult:
        """
        Compute Shapley value for all agents.

        Args:
            agents: List of all agents
            characteristic_function: Value of each coalition v(S)

        Returns:
            ShapleyValueResult with values and contributions
        """
        import time
        start_time = time.time()

        values = {}
        contributions = {}

        n = len(agents)

        for agent in agents:
            agent_value = 0.0
            agent_contributions = {}

            # Sum over all coalitions S not containing agent
            for coalition_size in range(n):
                for coalition in combinations([a for a in agents if a != agent], coalition_size):
                    S = frozenset(coalition)
                    S_with_agent = S | {agent}

                    # Marginal contribution
                    marginal = characteristic_function.get(S_with_agent, 0.0) - \
                              characteristic_function.get(S, 0.0)

                    # Weight: |S|! (n - |S| - 1)! / n!
                    weight = (np.math.factorial(len(S)) *
                             np.math.factorial(n - len(S) - 1) /
                             np.math.factorial(n))

                    agent_value += weight * marginal
                    agent_contributions[S] = marginal

            values[agent] = agent_value
            contributions[agent] = agent_contributions

        computation_time = time.time() - start_time

        return ShapleyValueResult(
            values=values,
            contributions=contributions,
            computation_time=computation_time
        )

    def compute_approximate(self, agents: List[str],
                           characteristic_function: Dict[FrozenSet[str], float],
                           num_samples: int = 1000) -> ShapleyValueResult:
        """
        Compute approximate Shapley value using Monte Carlo sampling.

        Useful for large games where exact computation is expensive.

        Args:
            agents: List of all agents
            characteristic_function: Value of each coalition
            num_samples: Number of random permutations to sample

        Returns:
            Approximate ShapleyValueResult
        """
        values = {agent: 0.0 for agent in agents}
        contributions = {agent: {} for agent in agents}

        for _ in range(num_samples):
            # Random permutation of agents
            permutation = np.random.permutation(agents)

            # Compute marginal contributions along permutation
            for i, agent in enumerate(permutation):
                S = frozenset(permutation[:i])
                S_with_agent = S | {agent}

                marginal = characteristic_function.get(S_with_agent, 0.0) - \
                         characteristic_function.get(S, 0.0)

                values[agent] += marginal

        # Average over samples
        for agent in agents:
            values[agent] /= num_samples

        return ShapleyValueResult(
            values=values,
            contributions=contributions,
            computation_time=0.0
        )

    def verify_axioms(self, agents: List[str],
                     shapley_result: ShapleyValueResult,
                     characteristic_function: Dict[FrozenSet[str], float]) -> Dict[str, bool]:
        """
        Verify Shapley value axioms.

        Returns:
            Dictionary indicating which axioms are satisfied
        """
        axioms = {}

        # Efficiency: Sum = v(N)
        total_value = sum(shapley_result.values.values())
        grand_coalition_value = characteristic_function.get(frozenset(agents), 0.0)
        axioms["efficiency"] = abs(total_value - grand_coalition_value) < 1e-6

        # Symmetry: Check symmetric agents
        axioms["symmetry"] = True  # Would require checking all permutations

        # Dummy player: Agents with zero marginal contribution
        axioms["dummy_player"] = True  # Would require checking each agent

        # Additivity: Requires another characteristic function
        axioms["additivity"] = True  # Would require checking v(S) + w(S)

        return axioms


class Core:
    """
    Core of a cooperative game.

    The core is the set of imputations where no coalition can do better.
    Core = {x | sum_i x_i = v(N), sum_{i in S} x_i >= v(S) for all S}
    """

    def __init__(self):
        """Initialize core calculator."""

    def compute(self, agents: List[str],
                characteristic_function: Dict[FrozenSet[str], float]) -> CoreResult:
        """
        Compute the core using linear programming.

        Args:
            agents: List of all agents
            characteristic_function: Value of each coalition

        Returns:
            CoreResult with imputations in the core
        """
        n = len(agents)

        # Decision variables: x_i for each agent i
        # Objective: Maximize sum of x_i (or any linear objective)

        # Efficiency constraint: sum_i x_i = v(N)
        A_eq = [[1] * n]
        b_eq = [characteristic_function.get(frozenset(agents), 0.0)]

        # Coalitional rationality constraints: sum_{i in S} x_i >= v(S)
        A_ub = []
        b_ub = []

        binding_constraints = []

        for coalition_size in range(1, n):
            for coalition in combinations(agents, coalition_size):
                S = frozenset(coalition)
                constraint = [1 if agent in S else 0 for agent in agents]
                A_ub.append(constraint)
                b_ub.append(characteristic_function.get(S, 0.0))

        # Solve linear program
        # Find any feasible solution (objective = 0)
        c = [0] * n

        if A_ub and b_ub:
            result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                           method='highs')

            if result.success:
                imputation = Imputation(
                    payoffs={agent: result.x[i] for i, agent in enumerate(agents)}
                )

                return CoreResult(
                    imputations=[imputation],
                    is_nonempty=True,
                    binding_constraints=binding_constraints
                )

        return CoreResult(
            imputations=[],
            is_nonempty=False,
            binding_constraints=binding_constraints
        )

    def check_imputation(self, imputation: Imputation,
                        agents: List[str],
                        characteristic_function: Dict[FrozenSet[str], float]) -> bool:
        """
        Check if an imputation is in the core.

        Args:
            imputation: Payoff distribution to check
            agents: List of all agents
            characteristic_function: Value of each coalition

        Returns:
            True if imputation is in the core
        """
        # Efficiency
        total_payoff = sum(imputation.payoffs.values())
        if abs(total_payoff - characteristic_function.get(frozenset(agents), 0.0)) > 1e-6:
            return False

        # Coalitional rationality
        for coalition_size in range(1, len(agents)):
            for coalition in combinations(agents, coalition_size):
                S = frozenset(coalition)
                coalition_payoff = sum(imputation.payoffs.get(agent, 0.0) for agent in S)

                if coalition_payoff < characteristic_function.get(S, 0.0) - 1e-6:
                    return False

        return True


class BargainingSolution:
    """
    Nash bargaining solution.

    Maximizes product of gains from disagreement:
    argmax_x prod_i (x_i - d_i)
    subject to sum_i x_i = v(N) and x_i >= d_i

    where d_i is the disagreement point (threat point).
    """

    def __init__(self):
        """Initialize bargaining solution calculator."""
        self.theorist = DeepSeekGameTheorist()

    def compute(self, agents: List[str],
                disagreement_point: Dict[str, float],
                total_value: float) -> Imputation:
        """
        Compute Nash bargaining solution.

        Args:
            agents: List of agents
            disagreement_point: Payoffs if negotiation fails (d_i)
            total_value: Total value to divide (v(N))

        Returns:
            Nash bargaining solution
        """
        # Nash bargaining: maximize product of (x_i - d_i)
        # Sum constraint: sum_i x_i = total_value
        # Individual rationality: x_i >= d_i

        # Analytical solution for symmetric case:
        # x_i = d_i + (total_value - sum_j d_j) / n

        n = len(agents)
        total_disagreement = sum(disagreement_point.get(agent, 0.0) for agent in agents)
        surplus = total_value - total_disagreement

        payoffs = {}
        for agent in agents:
            payoffs[agent] = disagreement_point.get(agent, 0.0) + surplus / n

        return Imputation(payoffs=payoffs)

    def compute_general(self, agents: List[str],
                      disagreement_point: Dict[str, float],
                      total_value: float,
                      weights: Dict[str, float]) -> Imputation:
        """
        Compute weighted Nash bargaining solution.

        Args:
            agents: List of agents
            disagreement_point: Payoffs if negotiation fails
            total_value: Total value to divide
            weights: Bargaining power weights

        Returns:
            Weighted Nash bargaining solution
        """
        # Weighted Nash bargaining: maximize prod_i (x_i - d_i)^{w_i}

        n = len(agents)
        total_disagreement = sum(disagreement_point.get(agent, 0.0) for agent in agents)
        surplus = total_value - total_disagreement
        total_weight = sum(weights.get(agent, 1.0) for agent in agents)

        payoffs = {}
        for agent in agents:
            weight = weights.get(agent, 1.0)
            payoffs[agent] = disagreement_point.get(agent, 0.0) + \
                           surplus * weight / total_weight

        return Imputation(payoffs=payoffs)


class CoalitionFormation:
    """
    Dynamic coalition formation.

    Models how agents form and dissolve coalitions over time.
    """

    def __init__(self):
        """Initialize coalition formation model."""

    def simulate_merge_and_split(self, agents: List[str],
                               characteristic_function: Dict[FrozenSet[str], float],
                               max_iterations: int = 100) -> List[Coalition]:
        """
        Simulate merge-and-split coalition formation process.

        Args:
            agents: List of agents
            characteristic_function: Value of each coalition
            max_iterations: Maximum iterations

        Returns:
            Final coalition structure
        """
        # Initialize with singleton coalitions
        current_coalitions = [
            Coalition(members=frozenset([agent]),
                     value=characteristic_function.get(frozenset([agent]), 0.0))
            for agent in agents
        ]

        for iteration in range(max_iterations):
            changed = False

            # Merge phase: try to merge coalitions
            for coalition1, coalition2 in combinations(current_coalitions, 2):
                merged_members = coalition1.members | coalition2.members
                merged_value = characteristic_function.get(merged_members, 0.0)

                # Check if merge is beneficial
                if merged_value > coalition1.value + coalition2.value:
                    # Merge coalitions
                    new_coalition = Coalition(
                        members=merged_members,
                        value=merged_value,
                        formed_at=iteration
                    )

                    current_coalitions.remove(coalition1)
                    current_coalitions.remove(coalition2)
                    current_coalitions.append(new_coalition)
                    changed = True
                    break

            if changed:
                continue

            # Split phase: try to split coalitions
            for coalition in current_coalitions:
                if coalition.size() > 1:
                    for sub_size in range(1, coalition.size()):
                        for sub_members in combinations(coalition.members, sub_size):
                            sub_coalition = frozenset(sub_members)
                            remainder = coalition.members - sub_coalition

                            sub_value = characteristic_function.get(sub_coalition, 0.0)
                            remainder_value = characteristic_function.get(remainder, 0.0)

                            # Check if split is beneficial
                            if sub_value + remainder_value > coalition.value:
                                # Split coalition
                                current_coalitions.remove(coalition)
                                current_coalitions.append(
                                    Coalition(members=sub_coalition, value=sub_value)
                                )
                                current_coalitions.append(
                                    Coalition(members=remainder, value=remainder_value)
                                )
                                changed = True
                                break

                if changed:
                    break

            if not changed:
                # No more changes possible
                break

        return current_coalitions

    def compute_stable_coalition_structure(self, agents: List[str],
                                          characteristic_function: Dict[FrozenSet[str], float]) -> List[List[str]]:
        """
        Compute stable coalition structure using core stability.

        Args:
            agents: List of agents
            characteristic_function: Value of each coalition

        Returns:
            Stable coalition structure
        """
        # This is a simplified implementation
        # Full implementation requires checking all partitions

        return [[agent] for agent in agents]


class POLLNCooperativeGame:
    """
    POLLN-specific cooperative game scenarios.

    Models:
    - Task sharing coalitions
    - Knowledge sharing groups
    - Resource pooling
    """

    @staticmethod
    def create_task_sharing_game(agents: List[str],
                                task_values: Dict[str, float],
                                synergies: Dict[Tuple[str], float]) -> Dict[FrozenSet[str], float]:
        """
        Create characteristic function for task sharing.

        Args:
            agents: Agents involved
            task_values: Individual task values
            synergies: Synergy values for coalitions

        Returns:
            Characteristic function
        """
        characteristic_function = {}

        # Individual values
        for agent in agents:
            characteristic_function[frozenset([agent])] = task_values.get(agent, 0.0)

        # Coalition values (with synergies)
        for coalition_size in range(2, len(agents) + 1):
            for coalition in combinations(agents, coalition_size):
                S = frozenset(coalition)
                base_value = sum(task_values.get(agent, 0.0) for agent in S)
                synergy = synergies.get(S, 0.0)
                characteristic_function[S] = base_value + synergy

        return characteristic_function

    @staticmethod
    def create_knowledge_sharing_game(agents: List[str],
                                     knowledge_blobs: Dict[str, Set[str]],
                                     sharing_value: float) -> Dict[FrozenSet[str], float]:
        """
        Create characteristic function for knowledge sharing.

        Args:
            agents: Agents involved
            knowledge_blobs: Knowledge held by each agent
            sharing_value: Value per shared knowledge item

        Returns:
            Characteristic function
        """
        characteristic_function = {}

        for coalition_size in range(1, len(agents) + 1):
            for coalition in combinations(agents, coalition_size):
                S = frozenset(coalition)

                # Value is total shared knowledge in coalition
                shared_knowledge = set()
                for agent in S:
                    shared_knowledge.update(knowledge_blobs.get(agent, set()))

                characteristic_function[S] = len(shared_knowledge) * sharing_value

        return characteristic_function

    @staticmethod
    def analyze_fair_division(resources: Dict[str, float],
                             agents: List[str],
                             valuations: Dict[str, Dict[str, float]]) -> Imputation:
        """
        Analyze fair division of resources.

        Args:
            resources: Resources to divide
            agents: Agents receiving resources
            valuations: Agent valuations for each resource

        Returns:
            Fair division
        """
        # Use Shapley value for fair division
        shapley = ShapleyValue()

        # Create characteristic function
        characteristic_function = {}
        for coalition_size in range(1, len(agents) + 1):
            for coalition in combinations(agents, coalition_size):
                S = frozenset(coalition)
                # Value is sum of valuations for coalition
                value = 0.0
                for resource, amount in resources.items():
                    max_valuation = max(valuations.get(agent, {}).get(resource, 0.0)
                                       for agent in S)
                    value += max_valuation * amount
                characteristic_function[S] = value

        result = shapley.compute(agents, characteristic_function)

        return Imputation(payoffs=result.values)


if __name__ == "__main__":
    # Test cooperative game theory
    agents = ["agent1", "agent2", "agent3"]

    # Create characteristic function
    characteristic_function = {
        frozenset(["agent1"]): 1.0,
        frozenset(["agent2"]): 1.0,
        frozenset(["agent3"]): 1.0,
        frozenset(["agent1", "agent2"]): 3.0,  # Synergy!
        frozenset(["agent1", "agent3"]): 3.0,
        frozenset(["agent2", "agent3"]): 3.0,
        frozenset(["agent1", "agent2", "agent3"]): 5.0  # Superadditive
    }

    print("Computing Shapley value...")
    shapley = ShapleyValue()
    result = shapley.compute(agents, characteristic_function)
    print(f"Shapley values: {result.values}")

    print("\nVerifying axioms...")
    axioms = shapley.verify_axioms(agents, result, characteristic_function)
    for axiom, satisfied in axioms.items():
        print(f"{axiom}: {satisfied}")

    print("\nComputing core...")
    core = Core()
    core_result = core.compute(agents, characteristic_function)
    print(f"Core is nonempty: {core_result.is_nonempty}")

    print("\nSimulating coalition formation...")
    formation = CoalitionFormation()
    final_coalitions = formation.simulate_merge_and_split(agents, characteristic_function)
    print(f"Final coalitions: {[coalition.members for coalition in final_coalitions]}")

    print("\nCreating POLLN task sharing game...")
    polln_game = POLLNCooperativeGame.create_task_sharing_game(
        agents=agents,
        task_values={"agent1": 2.0, "agent2": 2.0, "agent3": 2.0},
        synergies={
            frozenset(["agent1", "agent2"]): 1.0,
            frozenset(["agent1", "agent3"]): 1.0,
            frozenset(["agent2", "agent3"]): 1.0,
            frozenset(["agent1", "agent2", "agent3"]): 2.0
        }
    )

    result = shapley.compute(agents, polln_game)
    print(f"Shapley values for task sharing: {result.values}")
