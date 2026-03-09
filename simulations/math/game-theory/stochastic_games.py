"""
Stochastic Games Simulation
============================

Modeling POLLN agent interactions as stochastic games with state transitions,
stage games, and equilibrium analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from scipy.optimize import minimize
import networkx as nx
from deepseek_games import DeepSeekGameTheorist, GameTheoreticAnalysis


@dataclass
class Agent:
    """Agent in stochastic game."""
    id: str
    type: str  # TaskAgent, RoleAgent, CoreAgent
    state_space: List[str]
    action_space: List[str]
    policy: Optional[np.ndarray] = None  # Policy over actions
    value_function: Optional[np.ndarray] = None  # State value function


@dataclass
class GameState:
    """State of the multi-agent system."""
    timestamp: int
    active_agents: Set[str]
    coordination_state: str  # "coordinated", "conflicting", "exploring"
    resource_allocation: Dict[str, float]
    agent_states: Dict[str, str]


@dataclass
class StageGame:
    """Stage game at a particular state."""
    state: str
    players: List[str]
    action_spaces: Dict[str, List[str]]
    payoff_tensor: np.ndarray  # N-dimensional array of payoffs


@dataclass
class TransitionKernel:
    """State transition dynamics."""
    transition_probs: Dict[Tuple[str, Tuple[str, ...], str], float]
    # (current_state, (action_1, ..., action_n), next_state) -> probability


class StochasticGame:
    """
    Multi-agent stochastic game for POLLN.

    Formally defined as:
    - Agents: N = {1, ..., n}
    - States: S (finite or continuous)
    - Actions: A_i(s) for each agent i in state s
    - Transition: P(s' | s, a_1, ..., a_n)
    - Rewards: R_i(s, a_1, ..., a_n) for each agent i
    - Discount: γ in [0, 1]
    """

    def __init__(self, agents: List[Agent], states: List[str], gamma: float = 0.95):
        """
        Initialize stochastic game.

        Args:
            agents: List of agents
            states: State space
            gamma: Discount factor
        """
        self.agents = agents
        self.agent_map = {agent.id: agent for agent in agents}
        self.states = states
        self.state_map = {state: i for i, state in enumerate(states)}
        self.gamma = gamma

        self.stage_games: Dict[str, StageGame] = {}
        self.transition_kernel = TransitionKernel({})
        self.current_state: str = states[0]

        self.theorist = DeepSeekGameTheorist()

    def add_stage_game(self, stage_game: StageGame) -> None:
        """Add stage game for a state."""
        self.stage_games[stage_game.state] = stage_game

    def set_transition_dynamics(self, transitions: Dict) -> None:
        """Set state transition probabilities."""
        for key, prob in transitions.items():
            self.transition_kernel.transition_probs[key] = prob

    def compute_equilibrium(self, state: str) -> GameTheoreticAnalysis:
        """
        Compute Nash equilibrium for stage game at state.

        Uses DeepSeek to derive equilibrium strategies.
        """
        if state not in self.stage_games:
            raise ValueError(f"No stage game for state {state}")

        stage_game = self.stage_games[state]

        # Use DeepSeek to analyze equilibrium
        analysis = self.theorist.derive_nash_equilibrium(
            stage_game.payoff_tensor,
            f"Stage game at state {state}"
        )

        return analysis

    def solve_markov_game(self, max_iterations: int = 1000,
                          tolerance: float = 1e-6) -> Dict[str, np.ndarray]:
        """
        Solve for Markov perfect equilibrium.

        Uses value iteration or policy iteration to find equilibrium
        in the stochastic game.

        Args:
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Policy for each agent in each state
        """
        # Initialize value functions
        V = {
            agent.id: np.zeros(len(self.states))
            for agent in self.agents
        }

        # Value iteration
        for iteration in range(max_iterations):
            V_new = V.copy()

            for state in self.states:
                if state not in self.stage_games:
                    continue

                stage_game = self.stage_games[state]

                # Compute equilibrium for this stage game
                # This is simplified - full solution requires Nash equilibrium computation
                for agent in self.agents:
                    if agent.id not in stage_game.players:
                        continue

                    # Bellman equation for stochastic games
                    # V_i(s) = max_{a_i} sum_{a_{-i}} sigma_{-i}(a_{-i}) *
                    #           [R_i(s, a) + gamma * sum_{s'} P(s'|s,a) * V_i(s')]

                    agent_idx = stage_game.players.index(agent.id)

                    # Simplified: assume uniform randomization over actions
                    expected_payoff = 0.0
                    for action_idx, action in enumerate(agent.action_space):
                        action_payoff = self._compute_action_payoff(
                            stage_game, agent_idx, action_idx, V
                        )
                        expected_payoff += action_payoff / len(agent.action_space)

                    V_new[agent.id][self.state_map[state]] = expected_payoff

            # Check convergence
            max_diff = max(
                np.max(np.abs(V_new[agent.id] - V[agent.id]))
                for agent in self.agents
            )

            V = V_new

            if max_diff < tolerance:
                print(f"Converged after {iteration} iterations")
                break

        return V

    def _compute_action_payoff(self, stage_game: StageGame,
                               agent_idx: int, action_idx: int,
                               V: Dict[str, np.ndarray]) -> float:
        """Compute expected payoff for an action."""
        # This is a simplified computation
        # In full implementation, need to integrate over other agents' strategies
        # and transition probabilities

        payoff = stage_game.payoff_tensor[tuple([action_idx] * len(stage_game.players))]
        return payoff

    def simulate_episode(self, horizon: int = 100) -> List[Dict]:
        """
        Simulate an episode of the stochastic game.

        Args:
            horizon: Episode length

        Returns:
            List of state-action-reward trajectories
        """
        trajectory = []
        state = self.current_state

        for t in range(horizon):
            # Get stage game for current state
            if state not in self.stage_games:
                break

            stage_game = self.stage_games[state]

            # Sample actions (simplified - should use equilibrium strategies)
            actions = {}
            for agent_id in stage_game.players:
                agent = self.agent_map[agent_id]
                if agent.policy is not None:
                    # Sample from policy
                    action_idx = np.random.choice(
                        len(agent.action_space),
                        p=agent.policy
                    )
                    actions[agent_id] = agent.action_space[action_idx]
                else:
                    # Uniform random
                    actions[agent_id] = np.random.choice(agent.action_space)

            # Get payoffs
            payoffs = self._get_payoffs(stage_game, actions)

            # Record trajectory
            trajectory.append({
                "t": t,
                "state": state,
                "actions": actions.copy(),
                "payoffs": payoffs.copy()
            })

            # Transition to next state
            state = self._transition(state, actions)

        return trajectory

    def _get_payoffs(self, stage_game: StageGame,
                     actions: Dict[str, str]) -> Dict[str, float]:
        """Get payoffs for action profile."""
        payoffs = {}
        action_indices = [
            stage_game.action_spaces[agent_id].index(actions[agent_id])
            for agent_id in stage_game.players
        ]

        for i, agent_id in enumerate(stage_game.players):
            payoffs[agent_id] = stage_game.payoff_tensor[tuple(action_indices)][i]

        return payoffs

    def _transition(self, state: str, actions: Dict[str, str]) -> str:
        """Transition to next state."""
        action_tuple = tuple(actions.get(agent_id, "") for agent_id in self.agents)

        # Get transition probabilities
        probs = {}
        for next_state in self.states:
            key = (state, action_tuple, next_state)
            probs[next_state] = self.transition_kernel.transition_probs.get(key, 0.0)

        # Normalize and sample
        total = sum(probs.values())
        if total > 0:
            probs = {k: v/total for k, v in probs.items()}
            next_state = np.random.choice(list(probs.keys()), p=list(probs.values()))
        else:
            next_state = state

        return next_state

    def analyze_price_of_anarchy(self) -> Dict[str, float]:
        """
        Analyze price of anarchy for the stochastic game.

        Compares welfare at equilibrium vs socially optimal outcome.
        """
        # Get equilibrium strategies
        equilibrium_analysis = self.compute_equilibrium(self.current_state)

        # Compute social welfare at equilibrium
        equilibrium_welfare = self._compute_social_welfare(
            self.current_state, {}
        )

        # Compute socially optimal welfare
        optimal_welfare = self._compute_optimal_welfare(self.current_state)

        if equilibrium_welfare > 0:
            poa = optimal_welfare / equilibrium_welfare
        else:
            poa = float('inf')

        return {
            "equilibrium_welfare": equilibrium_welfare,
            "optimal_welfare": optimal_welfare,
            "price_of_anarchy": poa
        }

    def _compute_social_welfare(self, state: str, strategies: Dict) -> float:
        """Compute social welfare for given strategies."""
        # Simplified computation
        if state not in self.stage_games:
            return 0.0

        stage_game = self.stage_games[state]
        # Average payoff across all action profiles
        return np.mean(stage_game.payoff_tensor)

    def _compute_optimal_welfare(self, state: str) -> float:
        """Compute socially optimal welfare."""
        if state not in self.stage_games:
            return 0.0

        stage_game = self.stage_games[state]
        # Maximum sum of payoffs across all action profiles
        return np.max(stage_game.payoff_tensor.sum(axis=-1))


class POLLNStochasticGame(StochasticGame):
    """
    POLLN-specific stochastic game.

    Models:
    - Task execution coordination
    - Resource allocation
    - Agent communication
    """

    @staticmethod
    def create_from_colony(agents: List[Agent], tasks: List[str]) -> 'POLLNStochasticGame':
        """
        Create stochastic game from POLLN colony.

        Args:
            agents: List of POLLN agents
            tasks: Available tasks

        Returns:
            Configured stochastic game
        """
        # States represent different coordination scenarios
        states = [
            "idle", "coordinating", "executing", "conflicting", "learning"
        ]

        game = POLLNStochasticGame(agents, states)

        # Create stage games for each state
        for state in states:
            stage_game = POLLNStochasticGame._create_stage_game(
                state, agents, tasks
            )
            game.add_stage_game(stage_game)

        # Set transition dynamics
        game._set_polln_transitions(agents)

        return game

    @staticmethod
    def _create_stage_game(state: str, agents: List[Agent],
                          tasks: List[str]) -> StageGame:
        """Create stage game for a state."""
        # Action space: choose a task or abstain
        action_spaces = {
            agent.id: tasks + ["abstain"]
            for agent in agents
        }

        # Payoff tensor: N-dimensional array
        num_actions = len(tasks) + 1
        payoff_shape = tuple([num_actions] * len(agents))
        payoff_tensor = np.zeros(payoff_shape + (len(agents),))

        # Fill in payoffs based on state
        for idx in np.ndindex(payoff_shape[:-1]):
            actions = [
                action_spaces[agents[i].id][idx[i]]
                for i in range(len(agents))
            ]

            payoffs = POLLNStochasticGame._compute_payoffs(
                state, agents, actions, tasks
            )

            payoff_tensor[idx + (slice(None),)] = payoffs

        return StageGame(
            state=state,
            players=[agent.id for agent in agents],
            action_spaces=action_spaces,
            payoff_tensor=payoff_tensor
        )

    @staticmethod
    def _compute_payoffs(state: str, agents: List[Agent],
                        actions: List[str], tasks: List[str]) -> List[float]:
        """Compute payoffs for action profile."""
        payoffs = []

        # Task assignments
        task_assignments = {}
        for i, action in enumerate(actions):
            if action in tasks:
                if action not in task_assignments:
                    task_assignments[action] = []
                task_assignments[action].append(agents[i].id)

        for i, agent in enumerate(agents):
            action = actions[i]

            if state == "idle":
                # Prefer coordinating on tasks
                if action in tasks:
                    if len(task_assignments[action]) == 1:
                        payoffs.append(1.0)  # Solo execution
                    else:
                        payoffs.append(0.5)  # Shared execution
                else:
                    payoffs.append(0.0)

            elif state == "coordinating":
                # Reward coordination
                if action in tasks and len(task_assignments[action]) > 1:
                    payoffs.append(2.0)  # Coordinated execution
                elif action in tasks:
                    payoffs.append(1.0)
                else:
                    payoffs.append(0.0)

            elif state == "conflicting":
                # Penalize conflicts
                if action in tasks:
                    if len(task_assignments[action]) > 1:
                        payoffs.append(-1.0)  # Conflict
                    else:
                        payoffs.append(0.5)
                else:
                    payoffs.append(0.0)

            elif state == "executing":
                # Reward execution
                if action in tasks:
                    payoffs.append(1.0)
                else:
                    payoffs.append(-0.5)

            else:  # learning
                # Reward exploration
                payoffs.append(0.1)

        return payoffs

    def _set_polln_transitions(self, agents: List[Agent]) -> None:
        """Set POLLN-specific transition dynamics."""
        # Simplified transition dynamics
        # In practice, these would depend on agent actions and outcomes

        for state in self.states:
            for next_state in self.states:
                # Create action tuple placeholder
                action_tuple = tuple([""] * len(agents))

                # Transition probabilities
                if state == next_state:
                    prob = 0.7  # High self-transition
                elif (state == "idle" and next_state == "coordinating") or \
                     (state == "coordinating" and next_state == "executing"):
                    prob = 0.2
                else:
                    prob = 0.1 / (len(self.states) - 1)

                self.transition_kernel.transition_probs[(state, action_tuple, next_state)] = prob


if __name__ == "__main__":
    # Test stochastic game
    agents = [
        Agent("agent1", "TaskAgent", ["s1", "s2"], ["task_a", "task_b", "abstain"]),
        Agent("agent2", "TaskAgent", ["s1", "s2"], ["task_a", "task_b", "abstain"]),
    ]

    game = POLLNStochasticGame.create_from_colony(agents, ["task_a", "task_b"])

    # Analyze equilibrium
    print("Computing equilibrium...")
    analysis = game.compute_equilibrium("idle")
    print(f"Equilibria found: {len(analysis.equilibria)}")

    # Simulate episode
    print("\nSimulating episode...")
    trajectory = game.simulate_episode(horizon=10)
    for step in trajectory[:3]:
        print(f"t={step['t']}: {step['state']} -> {step['actions']}")
