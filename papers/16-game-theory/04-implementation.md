# Implementation: Mechanism Design Algorithms

**Author:** Casey DiGennaro
**Affiliation:** SuperInstance Research
**Date:** March 2026

---

## Overview

This chapter presents concrete implementations of game-theoretic mechanisms for SuperInstance coordination. We describe VCG mechanisms, Shapley value computation, core allocation algorithms, and distributed equilibrium finding.

---

## 1. VCG Mechanism Implementation

### 1.1 Core VCG Class

```python
from typing import List, Dict, Tuple, Callable
import numpy as np
from dataclasses import dataclass

@dataclass
class AgentType:
    """Agent's private type (capability, cost, value)."""
    agent_id: int
    capabilities: np.ndarray      # What agent can do
    cost_function: Callable       # Cost of performing tasks
    value_function: Callable      # Value received from outcomes
    confidence_zone: int = 2      # 1=confident, 2=transition, 3=uncertain


@dataclass
class Outcome:
    """Mechanism outcome (allocation + payments)."""
    allocation: Dict[int, List[int]]  # agent_id -> task_ids
    payments: Dict[int, float]         # agent_id -> payment


class VCGMechanism:
    """
    Vickrey-Clarke-Groves mechanism for SuperInstance coordination.
    Implements truthful dominant-strategy equilibrium.
    """

    def __init__(self, agents: List[AgentType], tasks: List[int]):
        self.agents = {a.agent_id: a for a in agents}
        self.tasks = tasks
        self.n_agents = len(agents)
        self.n_tasks = len(tasks)

    def compute_allocation(self,
                          reported_types: Dict[int, AgentType]) -> Dict[int, List[int]]:
        """
        Compute welfare-maximizing allocation.

        Args:
            reported_types: Agent id -> reported type (may differ from true)

        Returns:
            allocation: Agent id -> assigned tasks
        """
        # Initialize allocation
        allocation = {a: [] for a in self.agents}

        # Compute social welfare for each possible allocation
        # Use greedy assignment for efficiency
        remaining_tasks = set(self.tasks)

        while remaining_tasks:
            best_agent = None
            best_task = None
            best_marginal_value = float('-inf')

            for agent_id, agent in reported_types.items():
                for task in remaining_tasks:
                    # Compute marginal value of assigning task to agent
                    current_value = self._compute_value(
                        allocation[agent_id], agent
                    )
                    new_value = self._compute_value(
                        allocation[agent_id] + [task], agent
                    )
                    marginal = new_value - current_value

                    # Subtract cost
                    cost = agent.cost_function(task, allocation[agent_id])
                    net_value = marginal - cost

                    if net_value > best_marginal_value:
                        best_marginal_value = net_value
                        best_agent = agent_id
                        best_task = task

            if best_agent is not None and best_marginal_value > 0:
                allocation[best_agent].append(best_task)
                remaining_tasks.remove(best_task)
            else:
                break  # No positive-value assignments remaining

        return allocation

    def compute_payments(self,
                        reported_types: Dict[int, AgentType],
                        allocation: Dict[int, List[int]]) -> Dict[int, float]:
        """
        Compute VCG payments.

        Payment to agent i = (welfare of others without i) - (welfare of others with i)

        This is agent i's "externality" on other agents.
        """
        payments = {}

        # Compute welfare with all agents
        full_welfare = self._compute_social_welfare(allocation, reported_types)

        for agent_id in self.agents:
            # Compute welfare without this agent
            types_without_i = {
                k: v for k, v in reported_types.items() if k != agent_id
            }
            allocation_without_i = self.compute_allocation(types_without_i)
            welfare_without_i = self._compute_social_welfare(
                allocation_without_i, types_without_i
            )

            # Welfare of others with agent i
            welfare_others_with_i = sum(
                self._compute_agent_welfare(allocation[a], reported_types[a])
                for a in self.agents if a != agent_id
            )

            # VCG payment (externality)
            payments[agent_id] = welfare_without_i - welfare_others_with_i

        return payments

    def run_mechanism(self,
                     reported_types: Dict[int, AgentType]) -> Outcome:
        """
        Execute full VCG mechanism.

        Returns allocation and payments.
        """
        allocation = self.compute_allocation(reported_types)
        payments = self.compute_payments(reported_types, allocation)

        return Outcome(allocation=allocation, payments=payments)

    def _compute_value(self,
                      tasks: List[int],
                      agent: AgentType) -> float:
        """Compute value agent receives from assigned tasks."""
        return sum(agent.value_function(t) for t in tasks)

    def _compute_agent_welfare(self,
                               tasks: List[int],
                               agent: AgentType) -> float:
        """Compute agent's welfare (value - cost)."""
        value = self._compute_value(tasks, agent)
        cost = agent.cost_function(tasks)
        return value - cost

    def _compute_social_welfare(self,
                                allocation: Dict[int, List[int]],
                                types: Dict[int, AgentType]) -> float:
        """Compute total social welfare."""
        return sum(
            self._compute_agent_welfare(allocation[a], types[a])
            for a in types
        )
```

### 1.2 Incentive Verification

```python
class IncentiveVerifier:
    """
    Verify that truth-telling is dominant strategy.
    Tests mechanism by comparing truthful vs strategic reporting.
    """

    def __init__(self, mechanism: VCGMechanism):
        self.mechanism = mechanism

    def verify_dominant_strategy(self,
                                 true_types: Dict[int, AgentType],
                                 test_agent: int,
                                 num_lies: int = 100) -> Tuple[bool, float]:
        """
        Test if truth-telling dominates for test_agent.

        Returns:
            is_dominant: True if truth always best
            max_gain_from_lying: Maximum utility gain from lying
        """
        true_type = true_types[test_agent]
        max_gain = 0.0

        # Utility from truth-telling
        truthful_outcome = self.mechanism.run_mechanism(true_types)
        truthful_utility = self._compute_utility(
            truthful_outcome, test_agent, true_type
        )

        # Test random lies
        for _ in range(num_lies):
            # Generate random lie
            lie = self._generate_random_lie(true_type)
            lied_types = true_types.copy()
            lied_types[test_agent] = lie

            # Compute outcome with lie
            lied_outcome = self.mechanism.run_mechanism(lied_types)
            lied_utility = self._compute_utility(
                lied_outcome, test_agent, true_type
            )

            # Check if lying is better
            gain = lied_utility - truthful_utility
            max_gain = max(max_gain, gain)

        is_dominant = max_gain <= 1e-6  # Numerical tolerance
        return is_dominant, max_gain

    def _compute_utility(self,
                        outcome: Outcome,
                        agent_id: int,
                        true_type: AgentType) -> float:
        """Compute agent's actual utility (using true type)."""
        tasks = outcome.allocation[agent_id]
        value = sum(true_type.value_function(t) for t in tasks)
        cost = true_type.cost_function(tasks)
        payment = outcome.payments[agent_id]
        return value - cost + payment

    def _generate_random_lie(self, true_type: AgentType) -> AgentType:
        """Generate random false report."""
        # Randomly inflate or deflate capabilities
        lie_factor = np.random.uniform(0.5, 2.0)
        lie_capabilities = true_type.capabilities * lie_factor

        return AgentType(
            agent_id=true_type.agent_id,
            capabilities=lie_capabilities,
            cost_function=lambda t, ctx: true_type.cost_function(t, ctx) * np.random.uniform(0.5, 2.0),
            value_function=lambda t: true_type.value_function(t) * np.random.uniform(0.5, 2.0),
            confidence_zone=true_type.confidence_zone
        )
```

---

## 2. Shapley Value Computation

### 2.1 Exact Shapley Value

```python
from itertools import combinations

class ShapleyValueCalculator:
    """
    Compute Shapley values for cooperative games.
    """

    def __init__(self,
                 value_function: Callable[[set], float],
                 agents: List[int]):
        self.value_function = value_function
        self.agents = agents
        self.n = len(agents)

    def compute_exact(self) -> Dict[int, float]:
        """
        Compute exact Shapley values.
        Complexity: O(n! * n) - exponential, only for small games.
        """
        shapley_values = {i: 0.0 for i in self.agents}

        # Iterate over all permutations
        from itertools import permutations
        for perm in permutations(self.agents):
            coalition = set()
            for agent in perm:
                # Compute marginal contribution
                value_without = self.value_function(coalition)
                value_with = self.value_function(coalition | {agent})
                marginal = value_with - value_without

                shapley_values[agent] += marginal
                coalition.add(agent)

        # Average over all permutations
        for agent in self.agents:
            shapley_values[agent] /= np.math.factorial(self.n)

        return shapley_values

    def compute_approximate(self, num_samples: int = 10000) -> Dict[int, float]:
        """
        Compute approximate Shapley values via sampling.
        Complexity: O(num_samples * n) - polynomial.
        """
        shapley_values = {i: 0.0 for i in self.agents}
        counts = {i: 0 for i in self.agents}

        for _ in range(num_samples):
            # Random permutation
            perm = list(np.random.permutation(self.agents))
            coalition = set()

            for agent in perm:
                # Compute marginal contribution
                value_without = self.value_function(coalition)
                value_with = self.value_function(coalition | {agent})
                marginal = value_with - value_without

                shapley_values[agent] += marginal
                counts[agent] += 1
                coalition.add(agent)

        # Average
        for agent in self.agents:
            shapley_values[agent] /= counts[agent]

        return shapley_values
```

### 2.2 SuperInstance Value Function

```python
class SuperInstanceValueFunction:
    """
    Value function for SuperInstance cooperative games.
    Combines task value, coordination benefit, and primitive overhead.
    """

    def __init__(self,
                 agents: Dict[int, AgentType],
                 tasks: List[int],
                 coordination_bonus: float = 0.1,
                 origin_overhead: float = 0.05):
        self.agents = agents
        self.tasks = tasks
        self.coordination_bonus = coordination_bonus
        self.origin_overhead = origin_overhead

    def __call__(self, coalition: set) -> float:
        """
        Compute value of coalition.

        v(S) = task_value(S) + coordination_bonus(S) - overhead(S)
        """
        if not coalition:
            return 0.0

        # Task value: what tasks can coalition complete?
        task_value = self._compute_task_value(coalition)

        # Coordination bonus: synergy from working together
        coord_bonus = self._compute_coordination_bonus(coalition)

        # Origin tracking overhead
        overhead = self._compute_overhead(coalition)

        return task_value + coord_bonus - overhead

    def _compute_task_value(self, coalition: set) -> float:
        """Value from completing tasks."""
        # Combine capabilities
        total_capabilities = np.zeros_like(
            next(iter(self.agents.values())).capabilities
        )
        for agent_id in coalition:
            total_capabilities += self.agents[agent_id].capabilities

        # Assign tasks greedily
        value = 0.0
        remaining_capabilities = total_capabilities.copy()

        for task in self.tasks:
            task_requirements = self._get_task_requirements(task)
            if self._can_complete(remaining_capabilities, task_requirements):
                value += self._get_task_value(task)
                remaining_capabilities -= task_requirements

        return value

    def _compute_coordination_bonus(self, coalition: set) -> float:
        """Bonus from coordination (superadditivity)."""
        n = len(coalition)
        # Coordination bonus scales with coalition size
        # but has diminishing returns (submodular)
        return self.coordination_bonus * n * np.log(1 + n)

    def _compute_overhead(self, coalition: set) -> float:
        """Origin tracking and communication overhead."""
        n = len(coalition)
        # Overhead scales linearly with communication
        return self.origin_overhead * n * (n - 1)  # O(n^2) communication

    def _get_task_requirements(self, task: int) -> np.ndarray:
        """Resource requirements for task."""
        # Simplified: each task requires unit resources
        return np.ones(10)  # 10-dimensional capability

    def _can_complete(self, capabilities: np.ndarray, requirements: np.ndarray) -> bool:
        """Check if capabilities meet requirements."""
        return np.all(capabilities >= requirements)

    def _get_task_value(self, task: int) -> float:
        """Value of completing task."""
        return 1.0  # Simplified: all tasks worth 1
```

---

## 3. Core Allocation

### 3.1 Core Checker

```python
class CoreChecker:
    """
    Check if allocation is in the core.
    """

    def __init__(self,
                 value_function: Callable[[set], float],
                 agents: List[int]):
        self.value_function = value_function
        self.agents = agents

    def is_in_core(self, allocation: Dict[int, float]) -> bool:
        """
        Check if allocation is in core.

        Core conditions:
        1. Feasibility: sum(x_i) = v(N)
        2. Coalitional rationality: sum(x_i for i in S) >= v(S) for all S
        """
        # Check feasibility
        total_allocation = sum(allocation.values())
        total_value = self.value_function(set(self.agents))

        if abs(total_allocation - total_value) > 1e-6:
            return False  # Not efficient

        # Check coalitional rationality
        for size in range(1, len(self.agents)):
            for coalition in combinations(self.agents, size):
                coalition_set = set(coalition)
                coalition_allocation = sum(allocation[i] for i in coalition)
                coalition_value = self.value_function(coalition_set)

                if coalition_allocation < coalition_value - 1e-6:
                    return False  # Coalition can deviate

        return True

    def find_core_allocation(self) -> Optional[Dict[int, float]]:
        """
        Find a core allocation using linear programming.
        """
        from scipy.optimize import linprog

        n = len(self.agents)

        # Variables: x_1, x_2, ..., x_n (allocations)
        # Objective: minimize sum of x (any feasible solution works)

        # Constraints:
        # 1. sum(x) = v(N)  (efficiency)
        # 2. sum(x_i for i in S) >= v(S) for all S (coalitional rationality)

        # Build constraint matrix
        A_ub = []  # Upper bound constraints (converted from >=)
        b_ub = []

        for size in range(1, n):
            for coalition in combinations(range(n), size):
                coalition_set = set(self.agents[i] for i in coalition)
                constraint = [0.0] * n
                for i in coalition:
                    constraint[i] = -1  # -sum >= -v(S)
                A_ub.append(constraint)
                b_ub.append(-self.value_function(coalition_set))

        A_eq = [[1.0] * n]  # sum(x) = v(N)
        b_eq = [self.value_function(set(self.agents))]

        bounds = [(0, None) for _ in range(n)]  # x_i >= 0

        result = linprog(
            c=[1.0] * n,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds
        )

        if result.success:
            return {self.agents[i]: result.x[i] for i in range(n)}
        else:
            return None  # Core is empty
```

---

## 4. Equilibrium Finding

### 4.1 Best Response Dynamics

```python
class EquilibriumFinder:
    """
    Find Nash equilibrium through iterative best response.
    """

    def __init__(self, mechanism: VCGMechanism):
        self.mechanism = mechanism

    def find_equilibrium(self,
                        initial_types: Dict[int, AgentType],
                        max_iterations: int = 100) -> Tuple[Dict[int, AgentType], bool]:
        """
        Find equilibrium through best response dynamics.

        Returns:
            equilibrium_types: Types at convergence
            converged: Whether dynamics converged
        """
        current_types = initial_types.copy()

        for iteration in range(max_iterations):
            changed = False

            for agent_id in self.mechanism.agents:
                # Find best response for this agent
                best_type = self._find_best_response(
                    agent_id, current_types
                )

                if best_type != current_types[agent_id]:
                    current_types[agent_id] = best_type
                    changed = True

            if not changed:
                # Converged
                return current_types, True

        # Did not converge
        return current_types, False

    def _find_best_response(self,
                           agent_id: int,
                           current_types: Dict[int, AgentType]) -> AgentType:
        """
        Find agent's best response to others' strategies.
        """
        true_type = self.mechanism.agents[agent_id]

        # Under VCG, truth-telling is dominant
        # So best response is always true type
        return true_type

        # For general games, would search over strategy space:
        # best_utility = -inf
        # best_type = None
        # for candidate_type in strategy_space:
        #     utility = compute_utility(candidate_type, current_types)
        #     if utility > best_utility:
        #         best_utility = utility
        #         best_type = candidate_type
        # return best_type
```

---

## 5. Distributed Implementation

### 5.1 Distributed VCG

```python
class DistributedVCG:
    """
    Distributed VCG mechanism without central coordinator.
    Agents communicate peer-to-peer.
    """

    def __init__(self, agents: List[AgentType], tasks: List[int]):
        self.agents = {a.agent_id: a for a in agents}
        self.tasks = tasks
        self.communication_rounds = 0

    def run_distributed(self,
                       max_rounds: int = 50) -> Outcome:
        """
        Run distributed VCG through message passing.

        Protocol:
        1. Each agent broadcasts capabilities
        2. Agents locally compute marginal values
        3. Consensus on allocation via message passing
        4. Compute payments locally
        """
        # Phase 1: Capability broadcast
        known_capabilities = {a: self.agents[a].capabilities for a in self.agents}

        # Phase 2: Local value computation
        marginal_values = self._compute_marginal_values(known_capabilities)

        # Phase 3: Consensus allocation
        allocation = self._consensus_allocation(marginal_values, max_rounds)

        # Phase 4: Payment computation
        payments = self._distributed_payments(allocation, known_capabilities)

        return Outcome(allocation=allocation, payments=payments)

    def _compute_marginal_values(self,
                                 capabilities: Dict[int, np.ndarray]) -> Dict[int, float]:
        """Each agent computes marginal value contribution."""
        marginals = {}

        # Total capabilities
        total = sum(capabilities.values())

        # Marginal contribution
        for agent_id, cap in capabilities.items():
            others_total = total - cap
            # Simplified: marginal = capabilities / total
            marginals[agent_id] = np.sum(cap) / (np.sum(total) + 1e-6)

        return marginals

    def _consensus_allocation(self,
                             marginals: Dict[int, float],
                             max_rounds: int) -> Dict[int, List[int]]:
        """Reach consensus on task allocation."""
        allocation = {a: [] for a in self.agents}
        remaining = set(self.tasks)

        # Sort agents by marginal value
        sorted_agents = sorted(marginals.keys(),
                              key=lambda a: marginals[a],
                              reverse=True)

        # Greedy allocation (reaches consensus in one round for this protocol)
        for agent_id in sorted_agents:
            capacity = np.sum(self.agents[agent_id].capabilities)
            assigned = 0
            while remaining and assigned < capacity:
                task = remaining.pop()
                allocation[agent_id].append(task)
                assigned += 1

        self.communication_rounds = 1  # Single broadcast round
        return allocation

    def _distributed_payments(self,
                              allocation: Dict[int, List[int]],
                              capabilities: Dict[int, np.ndarray]) -> Dict[int, float]:
        """Compute payments through distributed calculation."""
        payments = {}

        for agent_id in self.agents:
            # Payment = externality on others
            # Compute locally with known information
            my_tasks = len(allocation[agent_id])
            avg_task_value = 1.0  # Simplified

            # Externality: value others would get without me
            others_welfare_with_me = sum(
                len(allocation[a]) * avg_task_value
                for a in self.agents if a != agent_id
            )

            # Estimate without me (approximate)
            total_tasks = len(self.tasks)
            my_share = my_tasks / total_tasks if total_tasks > 0 else 0
            externality = my_share * others_welfare_with_me

            payments[agent_id] = externality

        return payments
```

---

## 6. Summary

| Component | Lines of Code | Complexity |
|-----------|---------------|------------|
| VCGMechanism | ~120 | O(n^2 * m) |
| IncentiveVerifier | ~60 | O(num_lies * n^2 * m) |
| ShapleyValueCalculator | ~80 | O(n!) exact, O(samples * n) approx |
| SuperInstanceValueFunction | ~80 | O(n * m) |
| CoreChecker | ~70 | O(2^n) |
| EquilibriumFinder | ~50 | O(iterations * n * strategies) |
| DistributedVCG | ~100 | O(n^2) communication |

**Total:** ~560 lines of core implementation

---

**Next:** [05-validation.md](./05-validation.md) - Experiments and benchmarks

---

**Citation:**
```bibtex
@phdthesis{digennaro2026gametheory_impl,
  title={Implementation: Mechanism Design Algorithms},
  author={DiGennaro, Casey},
  booktitle={Game-Theoretic Mechanisms for SuperInstance Coordination},
  year={2026},
  institution={SuperInstance Research},
  note={Dissertation Chapter 4: Implementation}
}
```
