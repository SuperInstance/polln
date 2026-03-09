"""
Kan Extensions for POLLN

This module defines Kan extensions, providing:
- Left and right Kan extensions
- Yoneda reduction
- Ends and coends
- Optimization via universal properties

Kan extensions provide:
1. Generalized limits/colimits
2. Optimal extensions of functors
3. Density and density comonads
4. Profunctor composition
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from categories import Category, Morphism
from functors import Functor, NaturalTransformation
from deepseek_category import DeepSeekCategoryDeriver, DerivationType, get_deriver


class KanExtensionType(Enum):
    """Types of Kan extensions"""
    LEFT = "left"  # Left Kan extension (colimit)
    RIGHT = "right"  # Right Kan extension (limit)
    LAN = "lan"  # Left Kan notation
    RAN = "ran"  # Right Kan notation
    DENSITY = "density"  # Density comonad
    PROFUNCTOR = "profunctor"  # Profunctor composition


@dataclass
class KanExtension:
    """
    A Kan extension extends a functor along another functor.

    Left Kan Extension: Lan_K F
    - Given: K: C → D, F: C → E
    - Result: Lan_K F: D → E
    - Universal: For any G: D → E with natural trans. α: F ⇒ GK,
      exists unique β: Lan_K F ⇒ G with α = βK ∘ ε

    Right Kan Extension: Ran_K F
    - Given: K: C → D, F: C → E
    - Result: Ran_K F: D → E
    - Universal: For any G: D → E with natural trans. α: GK ⇒ F,
      exists unique β: G ⇒ Ran_K F with α = ε ∘ βK

    Formulas (when exist):
    - (Lan_K F)(d) = colim^(K↓d) F ∘ π
    - (Ran_K F)(d) = lim_(d↓K) F ∘ π
    """

    name: str
    K: Functor  # K: C → D
    F: Functor  # F: C → E
    extension: Functor  # Lan_K F or Ran_K F
    extension_type: KanExtensionType
    epsilon: Optional[NaturalTransformation] = None  # ε: F ⇒ (Lan_K F)K or (Ran_K F)K ⇒ F
    derivation: Optional[str] = None
    derivation_result: Optional[Any] = None

    def derive_structure(self, deriver: DeepSeekCategoryDeriver):
        """Use DeepSeek to derive Kan extension."""
        result = deriver.derive_kan_extension(
            functors=(self.K.name, self.F.name),
            extension_type=self.extension_type.value
        )
        self.derivation = result.raw_response
        self.derivation_result = result
        return result

    def compute_left_kan(
        self,
        d: str,
        comma_category: Optional[Category] = None
    ) -> str:
        """
        Compute left Kan extension: (Lan_K F)(d) = colim^(K↓d) F ∘ π

        Args:
            d: Object in D
            comma_category: Comma category K↓d (optional)

        Returns:
            Object representing (Lan_K F)(d)
        """
        # Simplified: create colimit object
        lan_id = f"lan_{self.F.name}_{self.K.name}_at_{d}"

        # Add to target category
        target_cat = self.extension.target_category
        target_cat.add_object(lan_id)

        return lan_id

    def compute_right_kan(
        self,
        d: str,
        comma_category: Optional[Category] = None
    ) -> str:
        """
        Compute right Kan extension: (Ran_K F)(d) = lim_(d↓K) F ∘ π

        Args:
            d: Object in D
            comma_category: Comma category d↓K (optional)

        Returns:
            Object representing (Ran_K F)(d)
        """
        # Simplified: create limit object
        ran_id = f"ran_{self.F.name}_{self.K.name}_at_{d}"

        # Add to target category
        target_cat = self.extension.target_category
        target_cat.add_object(ran_id)

        return ran_id


class YonedaReduction:
    """
    Yoneda reduction via Kan extensions.

    Yoneda Lemma: Nat(C(-, X), F) ≅ F(X)

    This gives:
    - F ≅ Ran_y 1 (where y is Yoneda embedding)
    - Density: Small projective = dense
    - Cauchy completeness: Idempotent complete
    """

    @staticmethod
    def yoneda_embedding(category: Category) -> Functor:
        """
        Yoneda embedding: y: C^op → [C, Set]

        y(X) = Hom_C(-, X): C^op → Set
        y(X)(Y) = Hom_C(Y, X)
        """
        from functors import YonedaEmbedding

        yoneda = YonedaEmbedding(category)

        # Embed each object
        for obj in category.objects:
            yoneda.embed_object(obj)

        return yoneda

    @staticmethod
    def yoneda_lemma_application(
        functor: Functor,
        obj: str
    ) -> Dict[str, Any]:
        """
        Apply Yoneda lemma: Nat(C(-, X), F) ≅ F(X)

        Args:
            functor: F: C → Set
            obj: Object X in C

        Returns:
            Isomorphism data
        """
        # Get representable functor Hom(-, X)
        hom_minus_x = f"Hom(-, {obj})"

        # Get F(X)
        fx = functor.apply_object(obj)

        return {
            "representable": hom_minus_x,
            "functor_value": fx,
            "natural_transformations": f"Nat({hom_minus_x}, {functor.name})",
            "isomorphic": f"F({obj}) = {fx}"
        }

    @staticmethod
    def density(
        functor: Functor,
        category: Category
    ) -> bool:
        """
        Check if functor is dense (small projective).

        F is dense if Yoneda reduction: F ≅ Lan_F 1

        Args:
            functor: F to check
            category: Source category

        Returns:
            True if dense
        """
        # Simplified check
        # F is dense if every object is a colimit of objects in F's image
        return True  # Placeholder


class EndCoend:
    """
    Ends and coends (weighted limits/colimits).

    End: ∫_c F(c, c) = limit over diagonal
    Coend: ∫^c F(c, c) = colimit over diagonal

    For functor F: C^op × C → D:
    - ∫_c F(c, c) is the end (limit)
    - ∫^c F(c, c) is the coend (colimit)

    Dinatural transformations:
    α_c: F(c, c) → X satisfies dinaturality:
    For f: c → c': α_c' ∘ F(f, id_c') = α_c ∘ F(id_c, f)
    """

    @staticmethod
    def end(
        category: Category,
        functor_data: Dict[Tuple[str, str], str]
    ) -> str:
        """
        Compute end: ∫_c F(c, c)

        Args:
            category: Category C
            functor_data: F(c1, c2) -> object mapping

        Returns:
            End object
        """
        end_id = f"end_{'_'.join(str(k) for k in functor_data.keys())}"

        # Add end object to category
        category.add_object(end_id)

        return end_id

    @staticmethod
    def coend(
        category: Category,
        functor_data: Dict[Tuple[str, str], str]
    ) -> str:
        """
        Compute coend: ∫^c F(c, c)

        Args:
            category: Category C
            functor_data: F(c1, c2) -> object mapping

        Returns:
            Coend object
        """
        coend_id = f"coend_{'_'.join(str(k) for k in functor_data.keys())}"

        # Add coend object to category
        category.add_object(coend_id)

        return coend_id

    @staticmethod
    def dinatural_transformation(
        source_data: Dict[str, str],
        target: str
    ) -> Dict[str, Morphism]:
        """
        Create dinatural transformation.

        Args:
            source_data: F(c, c) for each c
            target: Target object X

        Returns:
            Components α_c: F(c, c) → X
        """
        components = {}

        for c, fc in source_data.items():
            components[c] = Morphism(
                source=fc,
                target=target,
                label=f"alpha_{c}"
            )

        return components


class Profunctor:
    """
    Profunctor (distributor): P: C^op × D → Set

    Think of P as "C-shaped objects in D" or "relations from C to D"

    Composition: P ∘ Q where P: C^op × D → Set, Q: D^op × E → Set
    (P ∘ Q)(c, e) = ∫^d P(c, d) × Q(d, e)

    Applications:
    - Optics (lenses, prisms, traversals)
    - Actegories
    - Bimodules
    """

    def __init__(self, name: str, source_cat: Category, target_cat: Category):
        self.name = name
        self.source_cat = source_cat  # C
        self.target_cat = target_cat  # D
        self.data: Dict[Tuple[str, str], Set[Any]] = {}  # P(c, d)

    def add_mapping(self, c: str, d: str, values: Set[Any]):
        """Add P(c, d) mapping."""
        self.data[(c, d)] = values

    def compose(self, other: 'Profunctor') -> 'Profunctor':
        """
        Compose profunctors: P ∘ Q

        (P ∘ Q)(c, e) = ∫^d P(c, d) × Q(d, e)

        Args:
            other: Q: D^op × E → Set

        Returns:
            P ∘ Q: C^op × E → Set
        """
        composed = Profunctor(
            name=f"{self.name}_○_{other.name}",
            source_cat=self.source_cat,
            target_cat=other.target_cat
        )

        # Compute coend composition
        for (c, d1), p_values in self.data.items():
            for (d2, e), q_values in other.data.items():
                if d1 == d2:
                    # Cartesian product P(c, d) × Q(d, e)
                    for p in p_values:
                        for q in q_values:
                            key = (c, e)
                            if key not in composed.data:
                                composed.data[key] = set()
                            composed.data[key].add((p, q))

        return composed

    def to_functor(self, d: str) -> Functor:
        """
        Fix second argument to get functor: P(-, d): C^op → Set

        Args:
            d: Object in D

        Returns:
            Functor C^op → Set
        """
        functor = Functor(
            name=f"{self.name}(-, {d})",
            source_category=self.source_cat,
            target_category=self.source_cat  # Simplified
        )

        for c in self.source_cat.objects:
            if (c, d) in self.data:
                values = self.data[(c, d)]
                functor.map_object(c, f"Set({len(values)} items)")

        return functor


class DensityComonad:
    """
    Density comonad induced by a functor.

    For small projective (dense) functor P: C → D:
    - Density comonad: D → D
    - D(X) = ∫^c D(Pc, X) ⊗ Pc

    Properties:
    - Idempotent: D² ≅ D
    - Admits left adjoint: D ⊣ D
    - Cauchy completion
    """

    def __init__(self, functor: Functor, category: Category):
        self.functor = functor
        self.category = category
        self.comonad_data: Dict[str, str] = {}

    def compute_density(self, x: str) -> str:
        """
        Compute density: D(X) = ∫^c D(Pc, X) ⊗ Pc

        Args:
            x: Object X in D

        Returns:
            D(X) object
        """
        dx = f"density_{self.functor.name}_of_{x}"
        self.comonad_data[x] = dx
        return dx

    def counit(self, x: str) -> Morphism:
        """Counit: D(X) → X"""
        dx = self.comonad_data.get(x)
        if dx:
            return Morphism(source=dx, target=x, label=f"epsilon_{x}")
        return None

    def duplicate(self, x: str) -> Morphism:
        """Duplication: D(X) → D²(X)"""
        dx = self.comonad_data.get(x)
        ddx = f"density_{self.functor.name}_of_{dx}"
        if dx:
            return Morphism(source=dx, target=ddx, label=f"delta_{x}")
        return None


class KanOptimizer:
    """
    Optimization via Kan extensions.

    Applications:
    - Agent specialization (Left Kan)
    - Agent generalization (Right Kan)
    - Optimal composition
    - Resource allocation
    """

    def __init__(self, deriver: Optional[DeepSeekCategoryDeriver] = None):
        self.deriver = deriver or get_deriver()

    def specialize_agent(
        self,
        agent_category: Category,
        task_category: Category,
        specialization_functor: Functor
    ) -> KanExtension:
        """
        Specialize agent for task via Left Kan extension.

        Lan_K F gives "best approximation from the left"

        Args:
            agent_category: Category of agents
            task_category: Category of tasks
            specialization_functor: K mapping agents to tasks

        Returns:
            Left Kan extension for specialization
        """
        kan = KanExtension(
            name="AgentSpecialization",
            K=specialization_functor,
            F=Functor(
                name="Identity",
                source_category=agent_category,
                target_category=agent_category
            ),
            extension=Functor(
                name="SpecializedAgent",
                source_category=task_category,
                target_category=agent_category
            ),
            extension_type=KanExtensionType.LEFT
        )

        kan.derive_structure(self.deriver)
        return kan

    def generalize_agent(
        self,
        agent_category: Category,
        environment_category: Category,
        generalization_functor: Functor
    ) -> KanExtension:
        """
        Generalize agent across environments via Right Kan extension.

        Ran_K F gives "best approximation from the right"

        Args:
            agent_category: Category of agents
            environment_category: Category of environments
            generalization_functor: K mapping agents to environments

        Returns:
            Right Kan extension for generalization
        """
        kan = KanExtension(
            name="AgentGeneralization",
            K=generalization_functor,
            F=Functor(
                name="Identity",
                source_category=agent_category,
                target_category=agent_category
            ),
            extension=Functor(
                name="GeneralizedAgent",
                source_category=environment_category,
                target_category=agent_category
            ),
            extension_type=KanExtensionType.RIGHT
        )

        kan.derive_structure(self.deriver)
        return kan


class CommaCategory(Category):
    """
    Comma category K↓d (d↓K).

    For functor K: C → D and object d in D:
    - Objects: Pairs (c in C, f: K(c) → d)
    - Morphisms: h: c₁ → c₂ with K(h) ∘ f₁ = f₂

    This is used to compute Kan extensions:
    - (Lan_K F)(d) = colim^(K↓d) F ∘ π
    - (Ran_K F)(d) = lim_(d↓K) F ∘ π
    """

    def __init__(self, K: Functor, d: str, comma_type: str = "left"):
        super().__init__(f"Comma_{K.name}_down_{d}")

        self.K = K
        self.d = d
        self.comma_type = comma_type  # "left" for K↓d, "right" for d↓K

        # Build comma category
        self._build_comma_category()

    def _build_comma_category(self):
        """Build comma category objects and morphisms."""
        source_cat = self.K.source_category
        target_cat = self.K.target_category

        # Objects: (c in C, f: K(c) → d) or (f: d → K(c))
        for c in source_cat.objects:
            kc = self.K.apply_object(c)

            if self.comma_type == "left":
                # K↓d: morphisms K(c) → d
                morphisms = target_cat.get_morphisms(kc or "", self.d)
                for m in morphisms:
                    obj_id = f"({c}, {m.label})"
                    self.add_object(obj_id)
            else:
                # d↓K: morphisms d → K(c)
                morphisms = target_cat.get_morphisms(self.d, kc or "")
                for m in morphisms:
                    obj_id = f"({c}, {m.label})"
                    self.add_object(obj_id)


def create_example_kan_extension() -> KanExtension:
    """Create example Kan extension for demonstration."""
    from categories import create_example_agent_category, create_example_state_category

    agent_cat = create_example_agent_category()
    state_cat = create_example_state_category()

    # Create functors
    K = Functor(
        name="AgentToState",
        source_category=agent_cat,
        target_category=state_cat
    )
    K.map_object("task_1", "state_0")
    K.map_object("role_1", "state_1")

    F = Functor(
        name="StateToValue",
        source_category=state_cat,
        target_category=state_cat
    )
    F.map_object("state_0", "value_0")
    F.map_object("state_1", "value_1")

    # Create Kan extension
    lan = KanExtension(
        name="LeftKan_Example",
        K=K,
        F=F,
        extension=Functor(
            name="Lan_AgentToValue",
            source_category=agent_cat,
            target_category=state_cat
        ),
        extension_type=KanExtensionType.LEFT
    )

    return lan


if __name__ == "__main__":
    print("Creating Kan Extension...")
    kan = create_example_kan_extension()
    print(f"Kan Extension: {kan.name}")
    print(f"K: {kan.K.name}")
    print(f"F: {kan.F.name}")
    print(f"Extension: {kan.extension.name}")
    print(f"Type: {kan.extension_type.value}")

    print("\n" + "="*60)

    print("\nYoneda Reduction...")
    from categories import create_example_agent_category

    agent_cat = create_example_agent_category()
    yoneda = YonedaReduction.yoneda_embedding(agent_cat)
    print(f"Yoneda embedding: {yoneda.name}")

    print("\nYoneda Lemma Application:")
    result = YonedaReduction.yoneda_lemma_application(yoneda, "task_1")
    for key, value in result.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)

    print("\nEnds and Coends...")
    end_obj = EndCoend.end(agent_cat, {("task_1", "task_1"): "value_1"})
    print(f"End: {end_obj}")

    coend_obj = EndCoend.coend(agent_cat, {("task_1", "task_1"): "value_1"})
    print(f"Coend: {coend_obj}")

    print("\n" + "="*60)

    print("\nProfunctor Composition...")
    profunctor1 = Profunctor("P", agent_cat, state_cat)
    profunctor1.add_mapping("task_1", "state_0", {"a", "b"})

    profunctor2 = Profunctor("Q", state_cat, agent_cat)
    profunctor2.add_mapping("state_0", "role_1", {"c"})

    composed = profunctor1.compose(profunctor2)
    print(f"Composed profunctor: {composed.name}")
    print(f"Mappings: {list(composed.data.keys())}")
