"""
Functors and Natural Transformations for POLLN

This module defines functors between POLLN categories and natural transformations
between functors, enabling structural mappings and compositional reasoning.

Key concepts:
- Functors: Structure-preserving mappings between categories
- Natural transformations: Morphisms between functors
- Functor categories: Categories of functors and natural transformations
- Yoneda embedding: Representing objects as presheaves
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import json
from categories import Category, Morphism, AgentCategory, StateCategory, ColonyCategory
from deepseek_category import DeepSeekCategoryDeriver, DerivationType, get_deriver


class FunctorType(Enum):
    """Types of functors in POLLN"""
    COLONY_EXECUTION = "colony_execution"  # Maps agent pairs to execution results
    STATE_TRANSITION = "state_transition"  # Maps agents to state transitions
    LEARNING_UPDATE = "learning_update"  # Maps reward pairs to weight updates
    CONFIGURATION_EVOLUTION = "config_evolution"  # Maps time to configurations
    VALUE_PROPAGATION = "value_propagation"  # Maps states to value predictions
    FORGETFUL = "forgetful"  # Forgets structure
    FREE = "free"  # Free construction
    REPRESENTABLE = "representable"  # Yoneda embedding
    CONSTANT = "constant"  # Constant functor


@dataclass
class Functor:
    """
    A functor F: C → D between categories.

    Functor Requirements:
    1. Object mapping: Maps each object X in C to F(X) in D
    2. Morphism mapping: Maps each morphism f in C to F(f) in D
    3. Functoriality:
       - F(id_X) = id_F(X) (preserves identities)
       - F(g ∘ f) = F(g) ∘ F(f) (preserves composition)
    """

    name: str
    source_category: Category
    target_category: Category
    object_map: Dict[str, str] = field(default_factory=dict)  # X -> F(X)
    morphism_map: Dict[str, Morphism] = field(default_factory=dict)  # f -> F(f)
    derivation: Optional[str] = None
    derivation_result: Optional[Any] = None

    def map_object(self, source_obj: str, target_obj: str):
        """Map object from source to target category."""
        self.object_map[source_obj] = target_obj

    def map_morphism(self, source_morph: Morphism, target_morph: Morphism):
        """Map morphism from source to target category."""
        key = f"{source_morph.source}_{source_morph.label}_{source_morph.target}"
        self.morphism_map[key] = target_morph

    def apply_object(self, obj: str) -> Optional[str]:
        """Apply functor to object."""
        return self.object_map.get(obj)

    def apply_morphism(self, morph: Morphism) -> Optional[Morphism]:
        """Apply functor to morphism."""
        key = f"{morph.source}_{morph.label}_{morph.target}"
        return self.morphism_map.get(key)

    def verify_functoriality(self) -> Dict[str, bool]:
        """
        Verify functor laws.

        Returns:
            Dict with functoriality verification results
        """
        results = {
            "preserves_identities": self._verify_identity_preservation(),
            "preserves_composition": self._verify_composition_preservation()
        }
        return results

    def _verify_identity_preservation(self) -> bool:
        """Verify F(id_X) = id_F(X)."""
        for obj in self.source_category.objects:
            id_x = self.source_category.get_identity(obj)
            if id_x:
                f_id_x = self.apply_morphism(id_x)
                f_x = self.apply_object(obj)
                if f_x:
                    id_f_x = self.target_category.get_identity(f_x)
                    if f_id_x and id_f_x:
                        if f_id_x.label != id_f_x.label:
                            return False
        return True

    def _verify_composition_preservation(self) -> bool:
        """Verify F(g ∘ f) = F(g) ∘ F(f)."""
        # Sample check on representative morphisms
        for (x, y), morphisms_xy in list(self.source_category.morphisms.items())[:3]:
            for f in list(morphisms_xy)[:2]:
                for (y, z), morphisms_yz in list(self.source_category.morphisms.items())[:3]:
                    if y == f.target:
                        for g in list(morphisms_yz)[:2]:
                            # Check F(g ∘ f) = F(g) ∘ F(f)
                            gf = f.compose(g)
                            if gf:
                                f_gf = self.apply_morphism(gf)
                                f_f = self.apply_morphism(f)
                                f_g = self.apply_morphism(g)

                                if f_f and f_g:
                                    composed = f_f.compose(f_g)
                                    if f_gf and composed:
                                        if f_gf.label != composed.label:
                                            return False
        return True

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive functor structure."""
        result = deriver.derive_functor(
            source_category=self.source_category.name,
            target_category=self.target_category.name,
            mapping_description=f"Functor {self.name} mapping objects and morphisms"
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


@dataclass
class NaturalTransformation:
    """
    A natural transformation α: F ⇒ G between functors F, G: C → D.

    Naturality Condition:
    For every morphism f: X → Y in C:
    G(f) ∘ α_X = α_Y ∘ F(f)

    This is represented by a commutative square:
        F(X) --α_X--> G(X)
         |              |
        F(f)           G(f)
         |              |
         v              v
        F(Y) --α_Y--> G(Y)
    """

    name: str
    source_functor: Functor
    target_functor: Functor
    components: Dict[str, Morphism] = field(default_factory=dict)  # X -> α_X: F(X) -> G(X)
    derivation: Optional[str] = None
    derivation_result: Optional[Any] = None

    def add_component(self, obj: str, component: Morphism):
        """
        Add component α_X: F(X) → G(X).

        Args:
            obj: Object X in source category
            component: Morphism α_X from F(X) to G(X)
        """
        self.components[obj] = component

    def get_component(self, obj: str) -> Optional[Morphism]:
        """Get component α_X."""
        return self.components.get(obj)

    def verify_naturality(self, category: Category) -> Dict[str, bool]:
        """
        Verify naturality condition.

        For every f: X → Y, check: G(f) ∘ α_X = α_Y ∘ F(f)

        Returns:
            Dict with naturality verification for each morphism
        """
        results = {}

        for (x, y), morphisms in category.morphisms.items():
            if x != y:  # Skip identities
                for f in morphisms:
                    # Get components
                    alpha_x = self.get_component(x)
                    alpha_y = self.get_component(y)

                    if alpha_x and alpha_y:
                        # Get functor images
                        f_f = self.source_functor.apply_morphism(f)
                        f_g = self.target_functor.apply_morphism(f)

                        if f_f and f_g:
                            # Check naturality: G(f) ∘ α_X = α_Y ∘ F(f)
                            left = alpha_x.compose(f_g)
                            right = f_f.compose(alpha_y)

                            # Compare compositions
                            if left and right:
                                results[f.label] = (left.label == right.label)
                            else:
                                results[f.label] = False
                        else:
                            results[f.label] = False

        return results

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive natural transformation structure."""
        result = deriver.derive_natural_transformation(
            functors=(self.source_functor.name, self.target_functor.name),
            component_description=f"Natural transformation {self.name} components"
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class ColonyExecutionFunctor(Functor):
    """
    Functor mapping agent pairs to their execution results.

    F: Agent × Agent → State
    F(Agent1, Agent2) = Resulting state after Agent1 → Agent2 execution
    """

    def __init__(self, agent_cat: AgentCategory, state_cat: StateCategory):
        super().__init__(
            name="ColonyExecution",
            source_category=agent_cat,
            target_category=state_cat
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive structure."""
        result = deriver.derive_functor(
            source_category="Agent × Agent",
            target_category="State",
            mapping_description="""
            Maps pairs of agents (source, target) to the state resulting
            from A2A package execution from source to target.

            Object mapping: (Agent1, Agent2) -> State_after_A2A
            Morphism mapping: (A2A1, A2A2) -> State transition
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class StateTransitionFunctor(Functor):
    """
    Functor mapping agents to state transition functions.

    F: Agent → State^State (endofunctor on State)
    F(Agent) = State transition function induced by agent
    """

    def __init__(self, agent_cat: AgentCategory, state_cat: StateCategory):
        super().__init__(
            name="StateTransition",
            source_category=agent_cat,
            target_category=state_cat
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive structure."""
        result = deriver.derive_functor(
            source_category="Agent",
            target_category="State^State",
            mapping_description="""
            Maps each agent to its induced state transition function.

            Object mapping: Agent -> Transition function
            Morphism mapping: Agent morphism -> Function composition
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class LearningUpdateFunctor(Functor):
    """
    Functor mapping (state, reward) pairs to configuration updates.

    F: State × Reward → Configuration
    F(state, reward) = Updated configuration after learning
    """

    def __init__(self, state_cat: StateCategory, config_cat: Category):
        super().__init__(
            name="LearningUpdate",
            source_category=state_cat,
            target_category=config_cat
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive structure."""
        result = deriver.derive_functor(
            source_category="State × Reward",
            target_category="Configuration",
            mapping_description="""
            Maps (state, reward) pairs to configuration updates via
            Hebbian learning or value function updates.

            Object mapping: (state, reward) -> Updated config
            Morphism mapping: (transition, reward change) -> Config delta
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class ForgetConnectionFunctor(Functor):
    """
    Forgetful functor that forgets synaptic connections.

    F: Colony → Agent
    F(Colony) = Set of agents (forgetting connections)
    """

    def __init__(self, colony_cat: ColonyCategory, agent_cat: AgentCategory):
        super().__init__(
            name="ForgetConnection",
            source_category=colony_cat,
            target_category=agent_cat
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive structure."""
        result = deriver.derive_functor(
            source_category="Colony",
            target_category="Agent",
            mapping_description="""
            Forgetful functor that maps colonies to their underlying
            sets of agents, forgetting synaptic connections.

            Object mapping: Colony -> Set of agents
            Morphism mapping: Colony map -> Function on agent sets
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class YonedaEmbedding(Functor):
    """
    Yoneda embedding: y: C^op → [C, Set]

    Maps each object X to the representable functor Hom(-, X).
    This is a full and faithful embedding.

    y(X) = Hom_C(-, X): C^op → Set
    y(X)(Y) = Hom_C(Y, X) = Set of morphisms Y → X
    """

    def __init__(self, category: Category):
        # Create presheaf category [C, Set]
        presheaf_cat = Category(f"Presheaf({category.name})")
        super().__init__(
            name="Yoneda",
            source_category=category,
            target_category=presheaf_cat
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive Yoneda embedding."""
        result = deriver.derive_yoneda_lemma(
            functor=f"Yoneda embedding for {self.source_category.name}"
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def embed_object(self, obj: str) -> str:
        """
        Embed object X as representable functor Hom(-, X).

        Args:
            obj: Object X to embed

        Returns:
            Identifier for representable functor
        """
        functor_id = f"Hom(-, {obj})"
        self.map_object(obj, functor_id)

        # For each Y, Hom(Y, X) is the set of morphisms Y → X
        for y in self.source_category.objects:
            morphisms = self.source_category.get_morphisms(y, obj)
            # Store: Hom(Y, X) = {morphisms Y → X}
            self.target_category.add_object(f"{functor_id}({y})")

        return functor_id


class FunctorCategory(Category):
    """
    Category of functors [C, D].

    Objects: Functors F: C → D
    Morphisms: Natural transformations α: F ⇒ G
    Composition: Vertical composition of natural transformations
    Identity: Identity natural transformation

    This forms a 2-category when considering C, D as 2-categories.
    """

    def __init__(self, source_cat: Category, target_cat: Category):
        super().__init__(f"Functor({source_cat.name}, {target_cat.name})")
        self.source_cat = source_cat
        self.target_cat = target_cat

    def add_functor(self, functor: Functor):
        """Add functor as object."""
        self.add_object(functor.name)
        # Store functor reference
        self.functors = getattr(self, 'functors', {})
        self.functors[functor.name] = functor

    def add_natural_transformation(
        self,
        nt: NaturalTransformation
    ):
        """Add natural transformation as morphism."""
        self.add_morphism(
            source=nt.source_functor.name,
            target=nt.target_functor.name,
            label=nt.name,
            data={"components": {k: v.label for k, v in nt.components.items()}}
        )

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive functor category structure."""
        result = deriver.derive_category_theoretic(
            f"Functor Category [{self.source_cat.name}, {self.target_cat.name}]",
            DerivationType.CATEGORY,
            f"""
            Functor Category Details:
            - Objects: Functors F: {self.source_cat.name} → {self.target_cat.name}
            - Morphisms: Natural transformations between functors
            - Composition: Vertical composition
            - Identity: Identity natural transformation
            - 2-category structure: 2-morphisms are modifications
            """
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result


class CompositionOperator:
    """
    Composition operators for functors and natural transformations.

    Implements:
    - Functor composition: G ∘ F
    - Vertical composition: β ∘ α (natural transformations)
    - Horizontal composition: α * β (Godement calculus)
    - Whiskering: F ∘ α and α ∘ G
    """

    @staticmethod
    def compose_functors(F: Functor, G: Functor) -> Functor:
        """
        Compose functors: G ∘ F

        Args:
            F: Functor C → D
            G: Functor D → E

        Returns:
            Functor G ∘ F: C → E
        """
        composed = Functor(
            name=f"{G.name}_○_{F.name}",
            source_category=F.source_category,
            target_category=G.target_category
        )

        # Compose object mappings: (G ∘ F)(X) = G(F(X))
        for x, fx in F.object_map.items():
            gfx = G.apply_object(fx)
            if gfx:
                composed.map_object(x, gfx)

        # Compose morphism mappings: (G ∘ F)(f) = G(F(f))
        for key, fmorph in F.morphism_map.items():
            gfmorph = G.apply_morphism(fmorph)
            if gfmorph:
                composed.map_morphism(fmorph, gfmorph)

        return composed

    @staticmethod
    def vertical_composition(
        alpha: NaturalTransformation,
        beta: NaturalTransformation
    ) -> NaturalTransformation:
        """
        Vertical composition: β ∘ α

        Requires: α: F ⇒ G, β: G ⇒ H
        Result: β ∘ α: F ⇒ H

        Component: (β ∘ α)_X = β_X ∘ α_X
        """
        if alpha.target_functor.name != beta.source_functor.name:
            raise ValueError("Cannot compose: target of α must match source of β")

        composed = NaturalTransformation(
            name=f"{beta.name}_○_{alpha.name}",
            source_functor=alpha.source_functor,
            target_functor=beta.target_functor
        )

        # Compose components: (β ∘ α)_X = β_X ∘ α_X
        for obj in alpha.components:
            alpha_x = alpha.get_component(obj)
            beta_x = beta.get_component(obj)

            if alpha_x and beta_x:
                composed_x = alpha_x.compose(beta_x)
                if composed_x:
                    composed.add_component(obj, composed_x)

        return composed

    @staticmethod
    def horizontal_composition(
        alpha: NaturalTransformation,
        beta: NaturalTransformation
    ) -> NaturalTransformation:
        """
        Horizontal composition (Godement product): α * β

        Requires: α: F ⇒ G, β: H ⇒ K
        Result: α * β: HF ⇒ KG

        Component: (α * β)_X = K(α_X) ∘ β_{F(X)} = β_{G(X)} ∘ H(α_X)
        """
        composed = NaturalTransformation(
            name=f"{alpha.name}_*_{beta.name}",
            source_functor=Functor(
                name=f"{beta.source_functor.name}_○_{alpha.source_functor.name}",
                source_category=alpha.source_functor.source_category,
                target_category=alpha.source_functor.target_category
            ),
            target_functor=Functor(
                name=f"{beta.target_functor.name}_○_{alpha.target_functor.name}",
                source_category=alpha.target_functor.source_category,
                target_category=alpha.target_functor.target_category
            )
        )

        # Interchange law: (β' ∘ α') * (β ∘ α) = (β' * β) ∘ (α' * α)
        for obj in alpha.components:
            # K(α_X) ∘ β_{F(X)}
            alpha_x = alpha.get_component(obj)
            if alpha_x:
                k_alpha_x = beta.target_functor.apply_morphism(alpha_x)
                beta_fx = beta.get_component(alpha.source_functor.apply_object(obj) or "")

                if k_alpha_x and beta_fx:
                    composed_x = beta_fx.compose(k_alpha_x)
                    if composed_x:
                        composed.add_component(obj, composed_x)

        return composed

    @staticmethod
    def whisker_left(F: Functor, alpha: NaturalTransformation) -> NaturalTransformation:
        """
        Left whiskering: F ∘ α

        Given α: G ⇒ H, produces Fα: FG ⇒ FH
        """
        whiskered = NaturalTransformation(
            name=f"{F.name}_○_{alpha.name}",
            source_functor=Functor(
                name=f"{F.name}_○_{alpha.source_functor.name}",
                source_category=alpha.source_functor.source_category,
                target_category=alpha.source_functor.target_category
            ),
            target_functor=Functor(
                name=f"{F.name}_○_{alpha.target_functor.name}",
                source_category=alpha.target_functor.source_category,
                target_category=alpha.target_functor.target_category
            )
        )

        for obj, alpha_x in alpha.components.items():
            f_alpha_x = F.apply_morphism(alpha_x)
            if f_alpha_x:
                whiskered.add_component(obj, f_alpha_x)

        return whiskered

    @staticmethod
    def whisker_right(alpha: NaturalTransformation, G: Functor) -> NaturalTransformation:
        """
        Right whiskering: α ∘ G

        Given α: F ⇒ G, produces αG: FH ⇒ GH
        """
        whiskered = NaturalTransformation(
            name=f"{alpha.name}_○_{G.name}",
            source_functor=alpha.source_functor,
            target_functor=alpha.target_functor
        )

        for obj, alpha_x in alpha.components.items():
            # Apply G to domain/codomain
            whiskered.add_component(obj, alpha_x)

        return whiskered


def create_example_functor() -> ColonyExecutionFunctor:
    """Create example functor for demonstration."""
    from categories import create_example_agent_category, create_example_state_category

    agent_cat = create_example_agent_category()
    state_cat = create_example_state_category()

    functor = ColonyExecutionFunctor(agent_cat, state_cat)

    # Map agent pairs to states
    functor.map_object("task_1", "state_0")
    functor.map_object("role_1", "state_1")
    functor.map_object("core_1", "state_2")

    # Map A2A packages to transitions
    a2a_001 = Morphism("task_1", "role_1", "a2a_001")
    trans_001 = Morphism("state_0", "state_1", "trans_001")
    functor.map_morphism(a2a_001, trans_001)

    return functor


if __name__ == "__main__":
    # Create example functor
    print("Creating Colony Execution Functor...")
    functor = create_example_functor()
    print(f"Functor: {functor.name}")
    print(f"Source: {functor.source_category.name}")
    print(f"Target: {functor.target_category.name}")
    print(f"\nObject mappings: {functor.object_map}")
    print(f"Morphism mappings: {list(functor.morphism_map.keys())}")
    print(f"\nFunctoriality verification:")
    print(functor.verify_functoriality())

    print("\n" + "="*60)

    # Test natural transformation
    print("\nCreating Natural Transformation...")
    from categories import create_example_agent_category

    agent_cat = create_example_agent_category()
    state_cat = create_example_state_category()

    F = ColonyExecutionFunctor(agent_cat, state_cat)
    G = ColonyExecutionFunctor(agent_cat, state_cat)
    G.name = "AlternativeExecution"

    # Create natural transformation α: F ⇒ G
    alpha = NaturalTransformation(
        name="ExecutionOptimization",
        source_functor=F,
        target_functor=G
    )

    # Add components
    alpha.add_component("task_1", Morphism("state_0", "state_0", "id_task_1"))
    alpha.add_component("role_1", Morphism("state_1", "state_1", "id_role_1"))

    print(f"Natural transformation: {alpha.name}")
    print(f"Components: {list(alpha.components.keys())}")
