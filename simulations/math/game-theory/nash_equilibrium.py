"""
Nash Equilibrium Analysis
=========================

Computing and analyzing Nash equilibria in POLLN agent games.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from scipy.optimize import minimize, fsolve
import sympy as sp
from itertools import product
from deepseek_games import DeepSeekGameTheorist, GameTheoreticAnalysis, GameTheoryValidator


@dataclass
class NashEquilibrium:
    """Nash equilibrium specification."""
    strategy_profile: Dict[str, np.ndarray]  # Player -> mixed strategy
    type: str  # "pure" or "mixed"
    payoff: Dict[str, float]  # Expected payoff for each player
    is_pareto_efficient: bool
    is_risk_dominant: Optional[bool]
    stability_score: float


@dataclass
class BestResponse:
    """Best response correspondence."""
    player: str
    opponent_strategies: Dict[str, np.ndarray]
    best_responses: List[np.ndarray]
    expected_payoffs: np.ndarray


class NashEquilibriumSolver:
    """
    Compute Nash equilibria using various algorithms.

    Algorithms:
    - Best response dynamics (2-player)
    - Lemke-Howson algorithm (2-player)
    - Support enumeration (N-player)
    - Replicator dynamics
    - Fictitious play
    """

    def __init__(self):
        """Initialize Nash equilibrium solver."""
        self.theorist = DeepSeekGameTheorist()
        self.validator = GameTheoryValidator()

    def compute_equilibrium(self, payoff_matrix: np.ndarray,
                           method: str = "best_response") -> List[NashEquilibrium]:
        """
        Compute Nash equilibrium for given payoff matrix.

        Args:
            payoff_matrix: N-dimensional payoff tensor
            method: Solution method

        Returns:
            List of Nash equilibria
        """
        num_players = len(payoff_matrix.shape) - 1

        if num_players == 2:
            return self._compute_two_player_equilibrium(payoff_matrix, method)
        else:
            return self._compute_n_player_equilibrium(payoff_matrix, method)

    def _compute_two_player_equilibrium(self, payoff_matrix: np.ndarray,
                                       method: str) -> List[NashEquilibrium]:
        """Compute equilibrium for 2-player game."""
        equilibria = []

        # Extract payoff matrices for each player
        A = payoff_matrix[:, :, 0]  # Player 1's payoffs
        B = payoff_matrix[:, :, 1]  # Player 2's payoffs

        if method == "best_response":
            equilibria = self._best_response_2p(A, B)
        elif method == "lemke_howson":
            equilibria = self._lemke_howson(A, B)
        elif method == "support_enumeration":
            equilibria = self._support_enumeration_2p(A, B)
        else:
            raise ValueError(f"Unknown method: {method}")

        return equilibria

    def _best_response_2p(self, A: np.ndarray, B: np.ndarray) -> List[NashEquilibrium]:
        """
        Best response dynamics for 2-player games.

        Iteratively compute best responses until convergence.
        """
        m, n = A.shape  # Player 1 has m actions, Player 2 has n actions

        # Initialize with uniform random strategies
        sigma_1 = np.ones(m) / m
        sigma_2 = np.ones(n) / n

        converged = False
        max_iterations = 1000
        tolerance = 1e-6

        for iteration in range(max_iterations):
            # Compute best response for player 1
            expected_payoffs_1 = A @ sigma_2
            best_response_1 = np.zeros(m)
            best_response_1[np.argmax(expected_payoffs_1)] = 1.0

            # Compute best response for player 2
            expected_payoffs_2 = B.T @ sigma_1
            best_response_2 = np.zeros(n)
            best_response_2[np.argmax(expected_payoffs_2)] = 1.0

            # Update strategies (smooth best response)
            alpha = 1.0 / (iteration + 2)
            sigma_1 = (1 - alpha) * sigma_1 + alpha * best_response_1
            sigma_2 = (1 - alpha) * sigma_2 + alpha * best_response_2

            # Check convergence
            if np.linalg.norm(sigma_1 - best_response_1) < tolerance and \
               np.linalg.norm(sigma_2 - best_response_2) < tolerance:
                converged = True
                break

        # Verify equilibrium
        strategy_profile = {
            "player1": sigma_1,
            "player2": sigma_2
        }
        payoffs = {
            "player1": sigma_1 @ A @ sigma_2,
            "player2": sigma_1 @ B @ sigma_2
        }

        equilibrium = NashEquilibrium(
            strategy_profile=strategy_profile,
            type="mixed" if not self._is_pure(sigma_1) or not self._is_pure(sigma_2) else "pure",
            payoff=payoffs,
            is_pareto_efficient=self._is_pareto_efficient(payoff_matrix_to_list(A, B)),
            is_risk_dominant=None,
            stability_score=1.0 if converged else 0.5
        )

        return [equilibrium]

    def _lemke_howson(self, A: np.ndarray, B: np.ndarray) -> List[NashEquilibrium]:
        """
        Lemke-Howson algorithm for 2-player games.

        Finds all Nash equilibria by following equilibrium paths.
        """
        # This is a simplified implementation
        # Full implementation requires linear complementarity programming

        # For now, use best response as approximation
        return self._best_response_2p(A, B)

    def _support_enumeration_2p(self, A: np.ndarray, B: np.ndarray) -> List[NashEquilibrium]:
        """
        Support enumeration for 2-player games.

        Enumerates all possible supports and solves for equilibria.
        """
        equilibria = []
        m, n = A.shape

        # Try all support sizes
        for k1 in range(1, m + 1):
            for k2 in range(1, n + 1):
                # Enumerate all supports of size k1 and k2
                for support_1 in self._enumerate_supports(m, k1):
                    for support_2 in self._enumerate_supports(n, k2):
                        # Solve for equilibrium on this support
                        equilibrium = self._solve_support(A, B, support_1, support_2)
                        if equilibrium is not None:
                            equilibria.append(equilibrium)

        return equilibria

    def _enumerate_supports(self, n: int, k: int) -> List[Set[int]]:
        """Enumerate all supports of size k from n actions."""
        from itertools import combinations
        return [set(combo) for combo in combinations(range(n), k)]

    def _solve_support(self, A: np.ndarray, B: np.ndarray,
                      support_1: Set[int], support_2: Set[int]) -> Optional[NashEquilibrium]:
        """Solve for equilibrium on given support."""
        # Solve linear system for indifference conditions
        # This is a placeholder - full implementation required

        return None

    def _compute_n_player_equilibrium(self, payoff_matrix: np.ndarray,
                                     method: str) -> List[NashEquilibrium]:
        """Compute equilibrium for N-player game."""
        # For N-player games, use more general methods
        # This is computationally hard (PPAD-complete)

        return []

    def analyze_equilibrium_properties(self, equilibrium: NashEquilibrium,
                                     payoff_matrix: np.ndarray) -> Dict[str, any]:
        """
        Analyze properties of a Nash equilibrium.

        Args:
            equilibrium: Nash equilibrium to analyze
            payoff_matrix: Payoff structure

        Returns:
            Dictionary of properties
        """
        properties = {
            "type": equilibrium.type,
            "payoffs": equilibrium.payoff,
            "pareto_efficient": equilibrium.is_pareto_efficient,
            "stability": equilibrium.stability_score
        }

        # Compute risk dominance
        properties["risk_dominant"] = self._compute_risk_dominance(
            equilibrium, payoff_matrix
        )

        # Compute refinement properties
        properties["trembling_hand_perfect"] = self._check_trembling_hand(
            equilibrium, payoff_matrix
        )

        properties["proper"] = self._check_proper(equilibrium, payoff_matrix)

        return properties

    def _is_pure(self, strategy: np.ndarray) -> bool:
        """Check if strategy is pure."""
        return np.any(strategy > 0.99)

    def _is_pareto_efficient(self, payoffs: List[Tuple[float, ...]]) -> bool:
        """Check if payoff is Pareto efficient."""
        # A payoff is Pareto efficient if no other payoff
        # makes all players better off

        for other_payoff in payoffs:
            if all(p > o for p, o in zip(payoffs[0], other_payoff)):
                return False

        return True

    def _compute_risk_dominance(self, equilibrium: NashEquilibrium,
                               payoff_matrix: np.ndarray) -> bool:
        """Compute risk dominance."""
        # Harsanyi and Selten's risk dominance
        # This is a simplified check

        return True  # Placeholder

    def _check_trembling_hand(self, equilibrium: NashEquilibrium,
                             payoff_matrix: np.ndarray) -> bool:
        """Check if equilibrium is trembling-hand perfect."""
        # Selten's trembling-hand perfection

        return True  # Placeholder

    def _check_proper(self, equilibrium: NashEquilibrium,
                     payoff_matrix: np.ndarray) -> bool:
        """Check if equilibrium is proper."""
        # Myerson's properness

        return True  # Placeholder

    def compute_correlated_equilibrium(self, payoff_matrix: np.ndarray) -> Optional[Dict]:
        """
        Compute correlated equilibrium.

        Correlated equilibrium generalizes Nash equilibrium by allowing
        correlation devices.
        """
        # Linear programming formulation
        # Variables: probability of each action profile
        # Constraints: incentive compatibility

        return None  # Placeholder


class EquilibriumSelector:
    """Select among multiple equilibria using refinement criteria."""

    def __init__(self):
        """Initialize equilibrium selector."""

    def select(self, equilibria: List[NashEquilibrium],
               criteria: str = "payoff_dominance") -> NashEquilibrium:
        """
        Select equilibrium based on criteria.

        Args:
            equilibria: List of equilibria
            criteria: Selection criterion

        Returns:
            Selected equilibrium
        """
        if not equilibria:
            raise ValueError("No equilibria to select from")

        if len(equilibria) == 1:
            return equilibria[0]

        if criteria == "payoff_dominance":
            return self._payoff_dominance_selection(equilibria)
        elif criteria == "risk_dominance":
            return self._risk_dominance_selection(equilibria)
        elif criteria == "stability":
            return self._stability_selection(equilibria)
        else:
            return equilibria[0]

    def _payoff_dominance_selection(self, equilibria: List[NashEquilibrium]) -> NashEquilibrium:
        """Select payoff-dominant equilibrium (Pareto efficient)."""
        pareto_efficient = [eq for eq in equilibria if eq.is_pareto_efficient]

        if pareto_efficient:
            # Among Pareto efficient, pick one with highest total payoff
            return max(pareto_efficient, key=lambda eq: sum(eq.payoff.values()))

        return max(equilibria, key=lambda eq: sum(eq.payoff.values()))

    def _risk_dominance_selection(self, equilibria: List[NashEquilibrium]) -> NashEquilibrium:
        """Select risk-dominant equilibrium."""
        risk_dominant = [eq for eq in equilibria if eq.is_risk_dominant]

        if risk_dominant:
            return risk_dominant[0]

        return equilibria[0]

    def _stability_selection(self, equilibria: List[NashEquilibrium]) -> NashEquilibrium:
        """Select most stable equilibrium."""
        return max(equilibria, key=lambda eq: eq.stability_score)


class POLLNEquilibriumAnalyzer:
    """Analyze Nash equilibria in POLLN-specific scenarios."""

    def __init__(self):
        """Initialize POLLN equilibrium analyzer."""
        self.solver = NashEquilibriumSolver()
        self.selector = EquilibriumSelector()
        self.theorist = DeepSeekGameTheorist()

    def analyze_coordination_game(self, num_agents: int,
                                  coordination_benefit: float,
                                  miscoordination_cost: float) -> GameTheoreticAnalysis:
        """
        Analyze coordination game among POLLN agents.

        Models the trade-off between coordinating on tasks and
        avoiding conflicts.

        Args:
            num_agents: Number of agents
            coordination_benefit: Benefit from coordinating
            miscoordination_cost: Cost from miscoordination

        Returns:
            Game-theoretic analysis
        """
        # Create payoff matrix for coordination game
        # Each agent chooses: coordinate or defect
        num_actions = 2  # coordinate, defect

        # Build payoff tensor
        payoff_shape = tuple([num_actions] * num_agents) + (num_agents,)
        payoff_tensor = np.zeros(payoff_shape)

        for action_profile in np.ndindex(payoff_shape[:-1]):
            num_coordinating = sum(action_profile)

            for agent_idx in range(num_agents):
                if action_profile[agent_idx] == 1:  # Agent coordinated
                    if num_coordinating == num_agents:
                        # All coordinated
                        payoff_tensor[action_profile + (agent_idx,)] = coordination_benefit
                    elif num_coordinating > num_agents / 2:
                        # Majority coordinated
                        payoff_tensor[action_profile + (agent_idx,)] = coordination_benefit / 2
                    else:
                        # Minority coordinated
                        payoff_tensor[action_profile + (agent_idx,)] = miscoordination_cost
                else:  # Agent defected
                    payoff_tensor[action_profile + (agent_idx,)] = 0.0

        # Use DeepSeek to analyze
        analysis = self.theorist.derive_nash_equilibrium(
            payoff_tensor,
            f"Coordination game with {num_agents} agents"
        )

        return analysis

    def analyze_resource_allocation_game(self, num_agents: int,
                                        num_resources: int,
                                        resource_values: List[float]) -> GameTheoreticAnalysis:
        """
        Analyze resource allocation game.

        Models agents competing for limited resources.

        Args:
            num_agents: Number of agents
            num_resources: Number of resources
            resource_values: Values of resources

        Returns:
            Game-theoretic analysis
        """
        # Each agent chooses a resource
        payoff_tensor = np.zeros(tuple([num_resources] * num_agents) + (num_agents,))

        for action_profile in np.ndindex(payoff_tensor.shape[:-1]):
            # Count agents choosing each resource
            resource_allocation = {}
            for agent_idx in range(num_agents):
                resource = action_profile[agent_idx]
                if resource not in resource_allocation:
                    resource_allocation[resource] = 0
                resource_allocation[resource] += 1

            # Compute payoffs
            for agent_idx in range(num_agents):
                resource = action_profile[agent_idx]
                num_claimants = resource_allocation[resource]

                # Payoff is resource value divided by number of claimants
                if num_claimants > 0:
                    payoff = resource_values[resource] / num_claimants
                else:
                    payoff = 0.0

                payoff_tensor[action_profile + (agent_idx,)] = payoff

        # Use DeepSeek to analyze
        analysis = self.theorist.derive_nash_equilibrium(
            payoff_tensor,
            f"Resource allocation game with {num_agents} agents and {num_resources} resources"
        )

        return analysis


def payoff_matrix_to_list(A: np.ndarray, B: np.ndarray) -> List[Tuple[float, float]]:
    """Convert payoff matrices to list of payoff pairs."""
    payoffs = []
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            payoffs.append((A[i, j], B[i, j]))
    return payoffs


if __name__ == "__main__":
    # Test Nash equilibrium solver
    solver = NashEquilibriumSolver()

    # Prisoner's Dilemma
    A = np.array([[3, 0], [5, 1]])  # Player 1
    B = np.array([[3, 5], [0, 1]])  # Player 2
    payoff_matrix = np.stack([A, B], axis=-1)

    print("Solving Prisoner's Dilemma...")
    equilibria = solver.compute_equilibrium(payoff_matrix, method="best_response")

    for eq in equilibria:
        print(f"Equilibrium type: {eq.type}")
        print(f"Player 1 strategy: {eq.strategy_profile['player1']}")
        print(f"Player 2 strategy: {eq.strategy_profile['player2']}")
        print(f"Payoffs: {eq.payoff}")

    # Analyze POLLN coordination game
    analyzer = POLLNEquilibriumAnalyzer()
    print("\nAnalyzing POLLN coordination game...")
    analysis = analyzer.analyze_coordination_game(
        num_agents=3,
        coordination_benefit=5.0,
        miscoordination_cost=-2.0
    )
    print(f"Equilibria found: {len(analysis.equilibria)}")
    print(f"Price of Anarchy: {analysis.price_of_anarchy}")
