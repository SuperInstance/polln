"""
Category Definitions for POLLN

This module defines the fundamental categories that model POLLN's compositional intelligence:
- Agent categories with A2A morphisms
- State categories with transition morphisms
- Colony categories with composition
- Configuration categories with learning

Uses DeepSeek API to derive rigorous category-theoretic formulations.
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import json
from deepseek_category import DeepSeekCategoryDeriver, DerivationType, get_deriver


class CategoryType(Enum):
    """Types of categories in POLLN"""
    AGENT = "agent"  # Objects: agents, Morphisms: A2A packages
    STATE = "state"  # Objects: states, Morphisms: transitions
    COLONY = "colony"  # Objects: colonies, Morphisms: colony maps
    CONFIGURATION = "configuration"  # Objects: configs, Morphisms: updates
    LEARNING = "learning"  # Objects: learning states, Morphisms: updates
    COMMUNICATION = "communication"  # Objects: message spaces, Morphisms: protocols
    TILE = "tile"  # Objects: tiles, Morphisms: transformations
    VALUE = "value"  # Objects: value states, Morphisms: updates


@dataclass
class Morphism:
    """
    A morphism in a category.

    In POLLN, morphisms represent:
    - A2A packages (in Agent category)
    - State transitions (in State category)
    - Colony maps (in Colony category)
    """
    source: str
    target: str
    label: str
    data: Dict[str, Any] = field(default_factory=dict)

    def compose(self, other: 'Morphism') -> Optional['Morphism']:
        """
        Compose this morphism with another: g ∘ f

        Args:
            other: Morphism g where g.target = self.source

        Returns:
            Composed morphism if composable, None otherwise
        """
        if other.target != self.source:
            return None

        return Morphism(
            source=other.source,
            target=self.target,
            label=f"{other.label};{self.label}",
            data={
                "composition": [other.data, self.data],
                "components": [other.label, self.label]
            }
        )

    def __repr__(self):
        return f"Morphism({self.label}: {self.source} → {self.target})"


@dataclass
class Category:
    """
    A category with objects, morphisms, composition, and identities.

    Category Axioms:
    1. Composition: For f: X → Y and g: Y → Z, exists g ∘ f: X → Z
    2. Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
    3. Identity: For each object X, exists id_X: X → X where:
       - f ∘ id_X = f for all f: X → Y
       - id_Y ∘ f = f for all f: X → Y
    """

    name: str
    objects: Set[str] = field(default_factory=set)
    morphisms: Dict[Tuple[str, str], Set[Morphism]] = field(default_factory=dict)
    identity_map: Dict[str, Morphism] = field(default_factory=dict)
    derivation: Optional[str] = None

    def add_object(self, obj: str):
        """Add object to category with identity morphism."""
        self.objects.add(obj)
        if obj not in self.identity_map:
            id_morphism = Morphism(source=obj, target=obj, label=f"id_{obj}")
            self.identity_map[obj] = id_morphism
            self._add_morphism(id_morphism)

    def add_morphism(self, source: str, target: str, label: str, data: Optional[Dict] = None):
        """Add morphism to category."""
        morphism = Morphism(source=source, target=target, label=label, data=data or {})
        self._add_morphism(morphism)

    def _add_morphism(self, morphism: Morphism):
        """Internal method to add morphism."""
        key = (morphism.source, morphism.target)
        if key not in self.morphisms:
            self.morphisms[key] = set()
        self.morphisms[key].add(morphism)

    def compose(self, f: Morphism, g: Morphism) -> Optional[Morphism]:
        """
        Compose morphisms: g ∘ f

        Args:
            f: First morphism (X → Y)
            g: Second morphism (Y → Z)

        Returns:
            Composed morphism (X → Z) if composable
        """
        return f.compose(g)

    def get_identity(self, obj: str) -> Optional[Morphism]:
        """Get identity morphism for object."""
        return self.identity_map.get(obj)

    def verify_category_axioms(self) -> Dict[str, bool]:
        """
        Verify category axioms.

        Returns:
            Dict with axiom verification results
        """
        results = {
            "composition_closed": self._verify_composition_closure(),
            "associativity": self._verify_associativity(),
            "identity_left": self._verify_identity_left(),
            "identity_right": self._verify_identity_right()
        }
        return results

    def _verify_composition_closure(self) -> bool:
        """Verify composition is closed."""
        for (x, y), morphisms_xy in self.morphisms.items():
            for f in morphisms_xy:
                for (y, z), morphisms_yz in self.morphisms.items():
                    if y == self.target_match(y):
                        for g in morphisms_yz:
                            if g.target == self.target_match(z)[0]:
                                composed = f.compose(g)
                                if composed is None:
                                    return False
        return True

    def target_match(self, target: str) -> Tuple[bool, str]:
        """Helper to match targets."""
        for (src, tgt), morphs in self.morphisms.items():
            if tgt == target:
                return (True, src)
        return (False, "")

    def _verify_associativity(self) -> bool:
        """Verify associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)."""
        # Sample check on representative morphisms
        for (x, y), morphisms_xy in list(self.morphisms.items())[:5]:
            for f in list(morphisms_xy)[:3]:
                for (y, z), morphisms_yz in list(self.morphisms.items())[:5]:
                    if y == f.target:
                        for g in list(morphisms_yz)[:3]:
                            for (z, w), morphisms_zw in list(self.morphisms.items())[:5]:
                                if z == g.target:
                                    for h in list(morphisms_zw)[:3]:
                                        # Check (h ∘ g) ∘ f = h ∘ (g ∘ f)
                                        left = self.compose(self.compose(g, h), f)
                                        right = self.compose(g, self.compose(f, h))
                                        if left != right:
                                            return False
        return True

    def _verify_identity_left(self) -> bool:
        """Verify left identity: id_Y ∘ f = f."""
        for (x, y), morphisms in self.morphisms.items():
            for f in morphisms:
                id_y = self.get_identity(y)
                if id_y:
                    composed = self.compose(f, id_y)
                    if composed != f:
                        return False
        return True

    def _verify_identity_right(self) -> bool:
        """Verify right identity: f ∘ id_X = f."""
        for (x, y), morphisms in self.morphisms.items():
            for f in morphisms:
                id_x = self.get_identity(x)
                if id_x:
                    composed = id_x.compose(f)
                    if composed != f:
                        return False
        return True

    def get_morphisms(self, source: str, target: str) -> Set[Morphism]:
        """Get all morphisms from source to target."""
        return self.morphisms.get((source, target), set())

    def diagram(self) -> str:
        """Generate ASCII diagram of category structure."""
        lines = [f"Category: {self.name}", "=" * 50]
        lines.append(f"Objects: {len(self.objects)}")
        lines.append(f"Morphisms: {sum(len(m) for m in self.morphisms.values())}")
        lines.append("\nObjects:")
        for obj in sorted(self.objects):
            lines.append(f"  • {obj}")
        lines.append("\nMorphisms:")
        for (src, tgt), morphs in sorted(self.morphisms.items()):
            if src != tgt:  # Skip identities
                for m in morphs:
                    lines.append(f"  {src} --[{m.label}]--> {tgt}")
        return "\n".join(lines)


class AgentCategory(Category):
    """
    Category of POLLN agents.

    Objects: Agents (TaskAgent, RoleAgent, CoreAgent, META Tile)
    Morphisms: A2A packages (communication artifacts)
    Composition: Sequential A2A package execution
    Identity: No-op A2A package

    Derived using DeepSeek API.
    """

    def __init__(self):
        super().__init__("Agent")
        self.derivation_result = None

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive category structure."""
        result = deriver.derive_category_theoretic(
            "Agent Category - Objects: POLLN agents, Morphisms: A2A packages",
            DerivationType.CATEGORY,
            """
            POLLN Agent Category Details:
            - Objects: TaskAgent, RoleAgent, CoreAgent, MetaTile
            - Morphisms: A2A packages with parentIds and causalChainId
            - Composition: Sequential A2A execution (causally linked)
            - Identity: Empty A2A package (no-op)
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def add_agent(self, agent_id: str, agent_type: str):
        """Add agent object to category."""
        self.add_object(f"{agent_type}:{agent_id}")

    def add_a2a_package(
        self,
        source_agent: str,
        target_agent: str,
        package_id: str,
        parent_ids: List[str],
        causal_chain_id: str
    ):
        """Add A2A package morphism."""
        self.add_morphism(
            source=source_agent,
            target=target_agent,
            label=package_id,
            data={
                "type": "A2A",
                "parentIds": parent_ids,
                "causalChainId": causal_chain_id
            }
        )


class StateCategory(Category):
    """
    Category of agent states.

    Objects: Agent states (configurations with observations)
    Morphisms: State transitions (agent executions)
    Composition: Sequential state transitions
    Identity: Identity transition (no state change)

    Derived using DeepSeek API.
    """

    def __init__(self):
        super().__init__("State")
        self.state_types = {}  # Map state_id -> state_type

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive category structure."""
        result = deriver.derive_category_theoretic(
            "State Category - Objects: Agent states, Morphisms: Transitions",
            DerivationType.CATEGORY,
            """
            POLLN State Category Details:
            - Objects: Agent states (observations, memories, config)
            - Morphisms: State transitions via agent execution
            - Composition: Sequential transitions
            - Identity: Identity transition (null agent)
            - Monoidal: Tensor product for parallel composition
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def add_state(self, state_id: str, state_type: str, observations: List[str]):
        """Add state object to category."""
        self.add_object(state_id)
        self.state_types[state_id] = {
            "type": state_type,
            "observations": observations
        }

    def add_transition(
        self,
        source_state: str,
        target_state: str,
        transition_id: str,
        agent_id: str,
        reward: Optional[float] = None
    ):
        """Add state transition morphism."""
        self.add_morphism(
            source=source_state,
            target=target_state,
            label=transition_id,
            data={
                "type": "transition",
                "agent": agent_id,
                "reward": reward
            }
        )


class ColonyCategory(Category):
    """
    Category of agent colonies.

    Objects: Colonies (collections of agents with connections)
    Morphisms: Colony maps (agent inclusion, structure preservation)
    Composition: Composition of colony maps
    Identity: Identity colony map

    Derived using DeepSeek API.
    """

    def __init__(self):
        super().__init__("Colony")
        self.colony_compositions = {}  # Map colony_id -> set of agent_ids

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive category structure."""
        result = deriver.derive_category_theoretic(
            "Colony Category - Objects: Agent colonies, Morphisms: Colony maps",
            DerivationType.CATEGORY,
            """
            POLLN Colony Category Details:
            - Objects: Colonies (sets of agents with synaptic weights)
            - Morphisms: Colony maps (structure-preserving functions)
            - Composition: Function composition
            - Identity: Identity map on colony
            - Limits/Colimits: Colony union, intersection, quotient
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def add_colony(self, colony_id: str, agent_ids: Set[str]):
        """Add colony object to category."""
        self.add_object(colony_id)
        self.colony_compositions[colony_id] = agent_ids

    def add_colony_map(
        self,
        source_colony: str,
        target_colony: str,
        map_id: str,
        agent_mapping: Dict[str, str]
    ):
        """Add colony map morphism."""
        self.add_morphism(
            source=source_colony,
            target=target_colony,
            label=map_id,
            data={
                "type": "colony_map",
                "agent_mapping": agent_mapping
            }
        )


class ConfigurationCategory(Category):
    """
    Category of agent configurations.

    Objects: Agent configurations (parameters, hyperparameters)
    Morphisms: Configuration updates (learning steps)
    Composition: Sequential configuration updates
    Identity: No-op configuration update

    Derived using DeepSeek API.
    """

    def __init__(self):
        super().__init__("Configuration")
        self.configurations = {}  # Map config_id -> config_data

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive category structure."""
        result = deriver.derive_category_theoretic(
            "Configuration Category - Objects: Agent configs, Morphisms: Updates",
            DerivationType.CATEGORY,
            """
            POLLN Configuration Category Details:
            - Objects: Configurations (parameters, learning rates, etc.)
            - Morphisms: Configuration updates (Hebbian learning, evolution)
            - Composition: Sequential updates
            - Identity: Null update
            - Monoidal: Configuration merge
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def add_configuration(self, config_id: str, params: Dict[str, Any]):
        """Add configuration object."""
        self.add_object(config_id)
        self.configurations[config_id] = params

    def add_update(
        self,
        source_config: str,
        target_config: str,
        update_id: str,
        update_type: str,
        delta: Dict[str, Any]
    ):
        """Add configuration update morphism."""
        self.add_morphism(
            source=source_config,
            target=target_config,
            label=update_id,
            data={
                "type": "config_update",
                "update_type": update_type,
                "delta": delta
            }
        )


class ValueCategory(Category):
    """
    Category of value states for TD(λ) learning.

    Objects: Value states (value function parameters)
    Morphisms: Value updates (TD errors)
    Composition: Sequential value updates
    Identity: No-op value update

    Derived using DeepSeek API.
    """

    def __init__(self):
        super().__init__("Value")

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive category structure."""
        result = deriver.derive_category_theoretic(
            "Value Category - Objects: Value states, Morphisms: TD updates",
            DerivationType.CATEGORY,
            """
            POLLN Value Category Details:
            - Objects: Value states (V(s) for all states)
            - Morphisms: TD(λ) updates (value function updates)
            - Composition: Sequential TD updates
            - Identity: No update (TD error = 0)
            - Monoidal: Value averaging
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def add_value_state(self, state_id: str, values: Dict[str, float]):
        """Add value state object."""
        self.add_object(state_id)

    def add_td_update(
        self,
        source_value: str,
        target_value: str,
        update_id: str,
        td_error: float,
        lambda_param: float
    ):
        """Add TD update morphism."""
        self.add_morphism(
            source=source_value,
            target=target_value,
            label=update_id,
            data={
                "type": "td_update",
                "td_error": td_error,
                "lambda": lambda_param
            }
        )


class CategoryGenerator:
    """
    Generate POLLN categories from system descriptions.

    Uses DeepSeek API to derive rigorous category-theoretic formulations
    and then constructs executable category structures.
    """

    def __init__(self, deriver: Optional[DeepSeekCategoryDeriver] = None):
        self.deriver = deriver or get_deriver()

    def generate_agent_category(
        self,
        agents: List[Dict[str, str]],
        a2a_packages: List[Dict[str, Any]]
    ) -> AgentCategory:
        """Generate Agent category from POLLN data."""
        category = AgentCategory()
        category.derive_structure(self.deriver)

        # Add agents as objects
        for agent in agents:
            category.add_agent(agent["id"], agent["type"])

        # Add A2A packages as morphisms
        for package in a2a_packages:
            category.add_a2a_package(
                source_agent=package["source"],
                target_agent=package["target"],
                package_id=package["id"],
                parent_ids=package["parent_ids"],
                causal_chain_id=package["causal_chain_id"]
            )

        return category

    def generate_state_category(
        self,
        states: List[Dict[str, Any]],
        transitions: List[Dict[str, Any]]
    ) -> StateCategory:
        """Generate State category from POLLN data."""
        category = StateCategory()
        category.derive_structure(self.deriver)

        # Add states as objects
        for state in states:
            category.add_state(
                state_id=state["id"],
                state_type=state["type"],
                observations=state["observations"]
            )

        # Add transitions as morphisms
        for transition in transitions:
            category.add_transition(
                source_state=transition["source"],
                target_state=transition["target"],
                transition_id=transition["id"],
                agent_id=transition["agent"],
                reward=transition.get("reward")
            )

        return category

    def verify_all_categories(self, *categories: Category) -> Dict[str, Dict[str, bool]]:
        """Verify category axioms for all categories."""
        results = {}
        for category in categories:
            results[category.name] = category.verify_category_axioms()
        return results


def create_example_agent_category() -> AgentCategory:
    """Create example Agent category with sample data."""
    category = AgentCategory()

    # Add agents
    category.add_agent("task_1", "TaskAgent")
    category.add_agent("role_1", "RoleAgent")
    category.add_agent("core_1", "CoreAgent")
    category.add_agent("meta_1", "MetaTile")

    # Add A2A packages
    category.add_a2a_package(
        source_agent="task_1",
        target_agent="role_1",
        package_id="a2a_001",
        parent_ids=[],
        causal_chain_id="chain_001"
    )

    category.add_a2a_package(
        source_agent="role_1",
        target_agent="core_1",
        package_id="a2a_002",
        parent_ids=["a2a_001"],
        causal_chain_id="chain_001"
    )

    return category


def create_example_state_category() -> StateCategory:
    """Create example State category with sample data."""
    category = StateCategory()

    # Add states
    category.add_state(
        state_id="state_0",
        state_type="initial",
        observations=["obs_1", "obs_2"]
    )

    category.add_state(
        state_id="state_1",
        state_type="intermediate",
        observations=["obs_1", "obs_2", "obs_3"]
    )

    category.add_state(
        state_id="state_2",
        state_type="terminal",
        observations=["obs_1", "obs_2", "obs_3", "obs_4"]
    )

    # Add transitions
    category.add_transition(
        source_state="state_0",
        target_state="state_1",
        transition_id="trans_001",
        agent_id="task_1",
        reward=0.5
    )

    category.add_transition(
        source_state="state_1",
        target_state="state_2",
        transition_id="trans_002",
        agent_id="role_1",
        reward=1.0
    )

    return category


if __name__ == "__main__":
    # Create example categories
    print("Creating Agent Category...")
    agent_cat = create_example_agent_category()
    print(agent_cat.diagram())
    print("\nAxiom verification:")
    print(agent_cat.verify_category_axioms())

    print("\n" + "="*60 + "\n")

    print("Creating State Category...")
    state_cat = create_example_state_category()
    print(state_cat.diagram())
    print("\nAxiom verification:")
    print(state_cat.verify_category_axioms())
