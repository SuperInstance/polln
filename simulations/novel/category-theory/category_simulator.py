"""
Category Theory Simulator - Toolkit for POLLN

This module provides computational tools for category theory operations:
- Diagram chasing
- Limit/colimit computation
- Natural transformation checking
- Monad operations
- Functor composition
- Adjunction verification
- Kan extension computation
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

from categories import Category, Morphism
from functors import Functor, NaturalTransformation
from monads import Monad, Comonad
from adjunctions import Adjunction
from kan_extensions import KanExtension
from topos_theory import Topos


class DiagramType(Enum):
    """Types of diagrams"""
    COMMUTATIVE = "commutative"  # All paths equal
    COEQUALIZER = "coequalizer"  # Colimit of parallel pair
    EQUALIZER = "equalizer"  # Limit of parallel pair
    PULLBACK = "pullback"  # Limit of cospan
    PUSHOUT = "pushout"  # Colimit of span
    PRODUCT = "product"  # Limit of discrete diagram
    COPRODUCT = "coproduct"  # Colimit of discrete diagram


@dataclass
class Diagram:
    """
    A diagram in a category.

    A diagram is a functor from a small index category J to C.
    This represents a shape of objects and morphisms in C.
    """

    name: str
    category: Category
    objects: Set[str] = field(default_factory=set)
    morphisms: List[Morphism] = field(default_factory=list)
    diagram_type: DiagramType = DiagramType.COMMUTATIVE

    def add_object(self, obj: str):
        """Add object to diagram."""
        self.objects.add(obj)

    def add_morphism(self, morphism: Morphism):
        """Add morphism to diagram."""
        self.morphisms.append(morphism)

    def verify_commutativity(self) -> bool:
        """
        Verify diagram commutes: all paths with same source/target are equal.

        Returns:
            True if diagram commutes
        """
        # Get all pairs of objects
        for source in self.objects:
            for target in self.objects:
                if source == target:
                    continue

                # Find all paths from source to target
                paths = self._find_paths(source, target)

                # Check all paths have same composite morphism
                if paths:
                    first_composition = self._compose_path(paths[0])
                    for path in paths[1:]:
                        if self._compose_path(path) != first_composition:
                            return False

        return True

    def _find_paths(
        self,
        source: str,
        target: str,
        max_length: int = 5
    ) -> List[List[Morphism]]:
        """Find all paths from source to target."""
        paths = []
        self._dfs(source, target, [], paths, max_length)
        return paths

    def _dfs(
        self,
        current: str,
        target: str,
        path: List[Morphism],
        paths: List[List[Morphism]],
        max_length: int
    ):
        """Depth-first search for paths."""
        if len(path) > max_length:
            return

        if current == target and path:
            paths.append(path.copy())
            return

        # Find outgoing morphisms
        for morphism in self.morphisms:
            if morphism.source == current:
                path.append(morphism)
                self._dfs(morphism.target, target, path, paths, max_length)
                path.pop()

    def _compose_path(self, path: List[Morphism]) -> str:
        """Compose path into single morphism label."""
        if not path:
            return ""
        if len(path) == 1:
            return path[0].label
        return ";".join(m.label for m in reversed(path))

    def diagram_string(self) -> str:
        """Generate ASCII diagram."""
        lines = [f"Diagram: {self.name}", "=" * 50]
        lines.append(f"Type: {self.diagram_type.value}")
        lines.append(f"\nObjects: {', '.join(sorted(self.objects))}")
        lines.append(f"\nMorphisms:")
        for m in self.morphisms:
            lines.append(f"  {m.source} --[{m.label}]--> {m.target}")
        return "\n".join(lines)


class DiagramChaser:
    """
    Diagram chasing toolkit.

    Techniques:
    - Element chasing (in concrete categories)
    - Generalized elements
    - Yoneda lemma
    - Comma categories
    """

    def __init__(self, category: Category):
        self.category = category

    def chase(
        self,
        diagram: Diagram,
        start: str,
        end: str
    ) -> List[List[Morphism]]:
        """
        Chase all paths from start to end in diagram.

        Args:
            diagram: Diagram to chase
            start: Starting object
            end: Ending object

        Returns:
            List of paths (each path is list of morphisms)
        """
        return diagram._find_paths(start, end)

    def verify_commutative_square(
        self,
        f: Morphism,
        g: Morphism,
        h: Morphism,
        k: Morphism
    ) -> bool:
        """
        Verify commutative square:
            X --f--> Y
            |         |
            h         k
            |         |
            v         v
            Z --g--> W

        Commutes if: g ∘ h = k ∘ f
        """
        # Compose g ∘ h
        gh = h.compose(g)
        # Compose k ∘ f
        kf = f.compose(k)

        return gh == kf


class LimitColimitComputer:
    """
    Compute limits and colimits.

    Limits:
    - Product: × (conjunction)
    - Pullback: ×_ (fibered product)
    - Equalizer: Eq(f,g)
    - Terminal: 1

    Colimits:
    - Coproduct: + (disjunction)
    - Pushout: +_ (fibered coproduct)
    - Coequalizer: Coeq(f,g)
    - Initial: 0
    """

    def __init__(self, category: Category):
        self.category = category

    def product(self, objects: List[str]) -> str:
        """
        Compute product ∏ objects.

        Universal cone with projections.
        """
        product_id = f"product_{'_'.join(sorted(objects))}"

        # Add product object
        self.category.add_object(product_id)

        # Add projections
        for i, obj in enumerate(objects):
            self.category.add_morphism(
                source=product_id,
                target=obj,
                label=f"pi_{i+1}",
                data={"type": "projection"}
            )

        return product_id

    def coproduct(self, objects: List[str]) -> str:
        """
        Compute coproduct ∐ objects.

        Universal cocone with inclusions.
        """
        coproduct_id = f"coproduct_{'_'.join(sorted(objects))}"

        # Add coproduct object
        self.category.add_object(coproduct_id)

        # Add inclusions
        for i, obj in enumerate(objects):
            self.category.add_morphism(
                source=obj,
                target=coproduct_id,
                label=f"iota_{i+1}",
                data={"type": "inclusion"}
            )

        return coproduct_id

    def equalizer(
        self,
        f: Morphism,
        g: Morphism
    ) -> str:
        """
        Compute equalizer Eq(f, g).

        Largest subobject where f = g.
        """
        if f.source != g.source or f.target != g.target:
            raise ValueError("Morphisms must have same domain and codomain")

        eq_id = f"equalizer_{f.label}_{g.label}"
        self.category.add_object(eq_id)

        # Inclusion morphism
        self.category.add_morphism(
            source=eq_id,
            target=f.source,
            label=f"eq_{f.label}_{g.label}",
            data={"type": "equalizer_inclusion"}
        )

        return eq_id

    def coequalizer(
        self,
        f: Morphism,
        g: Morphism
    ) -> str:
        """
        Compute coequalizer Coeq(f, g).

        Largest quotient where f = g.
        """
        if f.source != g.source or f.target != g.target:
            raise ValueError("Morphisms must have same domain and codomain")

        coeq_id = f"coequalizer_{f.label}_{g.label}"
        self.category.add_object(coeq_id)

        # Projection morphism
        self.category.add_morphism(
            source=f.target,
            target=coeq_id,
            label=f"coeq_{f.label}_{g.label}",
            data={"type": "coequalizer_projection"}
        )

        return coeq_id

    def pullback(
        self,
        f: Morphism,
        g: Morphism
    ) -> str:
        """
        Compute pullback of cospan:

            B --g--> D
            ^         ^
            |         |
            f         |
            |         |
            A         C

        Pullback: A ×_D B
        """
        if f.target != g.target:
            raise ValueError("Morphisms must share codomain")

        pb_id = f"pullback_{f.source}_×_{g.source}_over_{f.target}"
        self.category.add_object(pb_id)

        # Projections
        self.category.add_morphism(
            source=pb_id,
            target=f.source,
            label=f"p1",
            data={"type": "pullback_projection"}
        )

        self.category.add_morphism(
            source=pb_id,
            target=g.source,
            label=f"p2",
            data={"type": "pullback_projection"}
        )

        return pb_id

    def pushout(
        self,
        f: Morphism,
        g: Morphism
    ) -> str:
        """
        Compute pushout of span:

            C <--f-- A
            ^        ^
            |        |
            g        |
            |        |
            B        D

        Pushout: B +_A D
        """
        if f.source != g.source:
            raise ValueError("Morphisms must share domain")

        po_id = f"pushout_{f.target}_+_{g.target}_over_{f.source}"
        self.category.add_object(po_id)

        # Inclusions
        self.category.add_morphism(
            source=f.target,
            target=po_id,
            label=f"i1",
            data={"type": "pushout_inclusion"}
        )

        self.category.add_morphism(
            source=g.target,
            target=po_id,
            label=f"i2",
            data={"type": "pushout_inclusion"}
        )

        return po_id

    def terminal(self) -> str:
        """Compute terminal object 1."""
        terminal_id = "terminal"
        self.category.add_object(terminal_id)

        # Add unique morphism from each object to terminal
        for obj in self.category.objects:
            if obj != terminal_id:
                self.category.add_morphism(
                    source=obj,
                    target=terminal_id,
                    label=f"!_{obj}",
                    data={"type": "terminal_map"}
                )

        return terminal_id

    def initial(self) -> str:
        """Compute initial object 0."""
        initial_id = "initial"
        self.category.add_object(initial_id)

        # Add unique morphism from initial to each object
        for obj in self.category.objects:
            if obj != initial_id:
                self.category.add_morphism(
                    source=initial_id,
                    target=obj,
                    label=f"!_{obj}",
                    data={"type": "initial_map"}
                )

        return initial_id


class NaturalTransformationChecker:
    """
    Check naturality conditions.

    For α: F ⇒ G, verify: G(f) ∘ α_X = α_Y ∘ F(f)
    """

    def __init__(self, category: Category):
        self.category = category

    def verify_naturality(
        self,
        transformation: NaturalTransformation
    ) -> Dict[str, bool]:
        """
        Verify naturality condition for all morphisms.

        Returns:
            Dict mapping morphism labels to naturality status
        """
        results = {}

        for (x, y), morphisms in self.category.morphisms.items():
            if x != y:  # Skip identities
                for f in morphisms:
                    naturality_holds = self._check_naturality_for_morphism(
                        transformation, f
                    )
                    results[f.label] = naturality_holds

        return results

    def _check_naturality_for_morphism(
        self,
        transformation: NaturalTransformation,
        f: Morphism
    ) -> bool:
        """
        Check naturality: G(f) ∘ α_X = α_Y ∘ F(f)

        Args:
            transformation: α: F ⇒ G
            f: Morphism X → Y

        Returns:
            True if naturality holds
        """
        # Get components
        alpha_x = transformation.get_component(f.source)
        alpha_y = transformation.get_component(f.target)

        if not alpha_x or not alpha_y:
            return False

        # Get functor images
        f_f = transformation.source_functor.apply_morphism(f)
        f_g = transformation.target_functor.apply_morphism(f)

        if not f_f or not f_g:
            return False

        # Check naturality: G(f) ∘ α_X = α_Y ∘ F(f)
        left = alpha_x.compose(f_g)
        right = f_f.compose(alpha_y)

        return left == right


class MonadOperator:
    """
    Monad operations.

    Operations:
    - Kleisli composition: >=> (fish operator)
    - Monad composition: ○
    - Monad transformers
    """

    @staticmethod
    def kleisli_compose(
        monad: Monad,
        f: Callable[[Any], Any],
        g: Callable[[Any], Any]
    ) -> Callable[[Any], Any]:
        """
        Kleisli composition: f >=> g

        (f >=> g)(x) = f(x) >>= g
        """
        def composed(x):
            fx = f(x)
            # Apply monadic bind
            return monad.bind(fx, g)

        return composed

    @staticmethod
    def kleisli_identity(monad: Monad, obj: str) -> Callable[[Any], Any]:
        """
        Kleisli identity: return

        return = η (unit of monad)
        """
        def identity(x):
            return monad.unit.get(obj, lambda y: y)(x)

        return identity

    @staticmethod
    def fish_operator(
        monad: Monad,
        f: Callable[[Any], Any],
        g: Callable[[Any], Any]
    ) -> Callable[[Any], Any]:
        """
        Fish operator: f >=> g

        Same as Kleisli composition.
        """
        return MonadOperator.kleisli_compose(monad, f, g)


class FunctorCompositionTool:
    """
    Functor composition utilities.
    """

    @staticmethod
    def compose(F: Functor, G: Functor) -> Functor:
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

        # Compose object mappings
        for x, fx in F.object_map.items():
            gfx = G.apply_object(fx)
            if gfx:
                composed.map_object(x, gfx)

        return composed

    @staticmethod
    def identity_functor(category: Category) -> Functor:
        """
        Identity functor: 1_C: C → C

        Maps each object/morphism to itself.
        """
        id_functor = Functor(
            name="Identity",
            source_category=category,
            target_category=category
        )

        for obj in category.objects:
            id_functor.map_object(obj, obj)

        return id_functor


class AdjunctionVerifier:
    """
    Verify adjunction properties.
    """

    @staticmethod
    def verify_unit_counit(adjunction: Adjunction) -> Dict[str, bool]:
        """
        Verify unit and counit satisfy triangle identities.

        Returns:
            Dict with verification results
        """
        return adjunction.verify_triangle_identities()

    @staticmethod
    def verify_hom_set_isomorphism(
        adjunction: Adjunction,
        fx: str,
        y: str
    ) -> bool:
        """
        Verify hom-set isomorphism: Hom_D(FX, Y) ≅ Hom_C(X, GY)

        Returns:
            True if isomorphic
        """
        hom_d, hom_c = adjunction.hom_set_isomorphism(fx, y)
        return len(hom_d) == len(hom_c)


class KanExtensionComputer:
    """
    Compute Kan extensions.
    """

    def __init__(self, category: Category):
        self.category = category

    def left_kan(
        self,
        K: Functor,
        F: Functor,
        d: str
    ) -> str:
        """
        Compute left Kan extension: (Lan_K F)(d)

        Formula: colim^(K↓d) F ∘ π
        """
        lan_id = f"lan_{F.name}_along_{K.name}_at_{d}"
        self.category.add_object(lan_id)
        return lan_id

    def right_kan(
        self,
        K: Functor,
        F: Functor,
        d: str
    ) -> str:
        """
        Compute right Kan extension: (Ran_K F)(d)

        Formula: lim_(d↓K) F ∘ π
        """
        ran_id = f"ran_{F.name}_along_{K.name}_at_{d}"
        self.category.add_object(ran_id)
        return ran_id


class CategoryTheoryToolkit:
    """
    Complete toolkit for category theory computations.
    """

    def __init__(self, category: Category):
        self.category = category
        self.diagram_chaser = DiagramChaser(category)
        self.limit_computer = LimitColimitComputer(category)
        self.nt_checker = NaturalTransformationChecker(category)
        self.monad_operator = MonadOperator()
        self.adjunction_verifier = AdjunctionVerifier()
        self.kan_computer = KanExtensionComputer(category)

    def analyze_category(self) -> Dict[str, Any]:
        """
        Comprehensive category analysis.

        Returns:
            Dict with category properties and structures
        """
        return {
            "name": self.category.name,
            "objects": len(self.category.objects),
            "morphisms": sum(len(m) for m in self.category.morphisms.values()),
            "axioms": self.category.verify_category_axioms(),
            "has_terminal": self._find_terminal(),
            "has_initial": self._find_initial(),
            "products": self._compute_all_products(),
            "coproducts": self._compute_all_coproducts()
        }

    def _find_terminal(self) -> Optional[str]:
        """Find terminal object if exists."""
        # Check if object has unique incoming morphism from all objects
        for obj in self.category.objects:
            has_unique_from_all = True
            for other in self.category.objects:
                if other != obj:
                    morphs = self.category.get_morphisms(other, obj)
                    if len(morphs) != 1:
                        has_unique_from_all = False
                        break
            if has_unique_from_all:
                return obj
        return None

    def _find_initial(self) -> Optional[str]:
        """Find initial object if exists."""
        # Check if object has unique outgoing morphism to all objects
        for obj in self.category.objects:
            has_unique_to_all = True
            for other in self.category.objects:
                if other != obj:
                    morphs = self.category.get_morphisms(obj, other)
                    if len(morphs) != 1:
                        has_unique_to_all = False
                        break
            if has_unique_to_all:
                return obj
        return None

    def _compute_all_products(self) -> Dict[Tuple[str, str], str]:
        """Compute all binary products."""
        products = {}
        objects = list(self.category.objects)

        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                key = (objects[i], objects[j])
                products[key] = self.limit_computer.product([objects[i], objects[j]])

        return products

    def _compute_all_coproducts(self) -> Dict[Tuple[str, str], str]:
        """Compute all binary coproducts."""
        coproducts = {}
        objects = list(self.category.objects)

        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                key = (objects[i], objects[j])
                coproducts[key] = self.limit_computer.coproduct([objects[i], objects[j]])

        return coproducts


if __name__ == "__main__":
    from categories import create_example_agent_category

    print("Creating Category Theory Toolkit...")
    agent_cat = create_example_agent_category()
    toolkit = CategoryTheoryToolkit(agent_cat)

    print("\nCategory Analysis:")
    analysis = toolkit.analyze_category()
    for key, value in analysis.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print("\n" + "="*60)

    print("\nDiagram Chasing...")
    diagram = Diagram(
        name="AgentFlow",
        category=agent_cat,
        diagram_type=DiagramType.COMMUTATIVE
    )

    # Add objects
    diagram.add_object("task_1")
    diagram.add_object("role_1")
    diagram.add_object("core_1")

    # Add morphisms
    diagram.add_morphism(Morphism("task_1", "role_1", "a2a_001"))
    diagram.add_morphism(Morphism("role_1", "core_1", "a2a_002"))

    print(f"\nDiagram: {diagram.name}")
    print(f"Commutative: {diagram.verify_commutativity()}")
    print(diagram.diagram_string())

    print("\n" + "="*60)

    print("\nLimit and Colimit Computation...")
    product = toolkit.limit_computer.product(["task_1", "role_1"])
    print(f"Product: {product}")

    coproduct = toolkit.limit_computer.coproduct(["task_1", "role_1"])
    print(f"Coproduct: {coproduct}")

    print("\n" + "="*60)

    print("\nFunctor Composition...")
    from functors import create_example_functor

    functor = create_example_functor()
    id_functor = FunctorCompositionTool.identity_functor(agent_cat)

    composed = FunctorCompositionTool.compose(id_functor, functor)
    print(f"Identity ○ F = {composed.name}")
    print(f"Objects: {list(composed.object_map.keys())}")
