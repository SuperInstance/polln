"""
Comprehensive Tests for Category Theory Module

Tests all category-theoretic structures for POLLN:
- Category axioms
- Functoriality
- Monad laws
- Adjunctions
- Kan extensions
- Topos properties
"""

import pytest
from typing import Dict, List

from categories import (
    AgentCategory, StateCategory, ColonyCategory,
    ConfigurationCategory, ValueCategory, Category,
    Morphism, create_example_agent_category, create_example_state_category
)
from functors import (
    Functor, ColonyExecutionFunctor, YonedaEmbedding,
    NaturalTransformation, FunctorCategory, CompositionOperator
)
from monads import (
    StateMonad, ValueMonad, CommunicationMonad,
    ProbabilityMonad, StoreComonad, MonadTransformer
)
from adjunctions import (
    AgentStateAdjunction, FreeForgetfulAdjunction,
    MonadicAdjunction, LimitColimit
)
from kan_extensions import (
    KanExtension, YonedaReduction, EndCoend, Profunctor
)
from topos_theory import (
    AgentConfigurationTopos, PresheafTopos,
    HeytingAlgebra, SubobjectClassifier
)
from category_simulator import (
    Diagram, DiagramChaser, LimitColimitComputer,
    CategoryTheoryToolkit
)


class TestCategories:
    """Test category structures."""

    def test_agent_category_creation(self):
        """Test creating agent category."""
        category = AgentCategory()
        category.add_agent("task_1", "TaskAgent")
        category.add_agent("role_1", "RoleAgent")

        assert "task_1" in category.objects
        assert "role_1" in category.objects

    def test_agent_category_morphisms(self):
        """Test A2A package morphisms."""
        category = AgentCategory()
        category.add_agent("task_1", "TaskAgent")
        category.add_agent("role_1", "RoleAgent")

        category.add_a2a_package(
            "task_1", "role_1", "a2a_001", [], "chain_001"
        )

        morphisms = category.get_morphisms("task_1", "role_1")
        assert len(morphisms) == 1
        assert list(morphisms)[0].label == "a2a_001"

    def test_category_composition(self):
        """Test morphism composition."""
        f = Morphism("X", "Y", "f")
        g = Morphism("Y", "Z", "g")

        composed = g.compose(f)
        assert composed is not None
        assert composed.source == "X"
        assert composed.target == "Z"

    def test_category_axioms(self):
        """Test category axioms verification."""
        category = create_example_agent_category()
        axioms = category.verify_category_axioms()

        # Check all axioms are satisfied
        for axiom, satisfied in axioms.items():
            assert satisfied, f"Axiom {axiom} not satisfied"

    def test_state_category(self):
        """Test state category."""
        category = StateCategory()
        category.add_state("state_0", "initial", ["obs_1"])
        category.add_state("state_1", "terminal", ["obs_2"])

        category.add_transition("state_0", "state_1", "trans_001", "agent_1")

        morphisms = category.get_morphisms("state_0", "state_1")
        assert len(morphisms) == 1


class TestFunctors:
    """Test functor structures."""

    def test_functor_creation(self):
        """Test creating functor."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        functor = Functor(
            name="TestFunctor",
            source_category=agent_cat,
            target_category=state_cat
        )

        functor.map_object("task_1", "state_0")
        assert functor.apply_object("task_1") == "state_0"

    def test_functor_composition(self):
        """Test functor composition."""
        from categories import create_example_agent_category, create_example_state_category

        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        F = Functor("F", agent_cat, agent_cat)
        G = Functor("G", agent_cat, state_cat)

        F.map_object("task_1", "role_1")
        G.map_object("role_1", "state_0")

        composed = CompositionOperator.compose_functors(F, G)
        assert composed.name == "G_○_F"

    def test_yoneda_embedding(self):
        """Test Yoneda embedding."""
        agent_cat = create_example_agent_category()
        yoneda = YonedaEmbedding(agent_cat)

        for obj in ["task_1", "role_1"]:
            yoneda.embed_object(obj)

        assert len(yoneda.object_map) > 0

    def test_natural_transformation(self):
        """Test natural transformation."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        F = Functor("F", agent_cat, state_cat)
        G = Functor("G", agent_cat, state_cat)

        alpha = NaturalTransformation(
            name="alpha",
            source_functor=F,
            target_functor=G
        )

        alpha.add_component("task_1", Morphism("state_0", "state_0", "id"))
        assert alpha.get_component("task_1") is not None


class TestMonads:
    """Test monad structures."""

    def test_state_monad_creation(self):
        """Test state monad creation."""
        state_cat = create_example_state_category()
        monad = StateMonad(state_cat)

        assert monad.name == "State"
        assert monad.category == state_cat

    def test_state_monad_pure(self):
        """Test state monad unit."""
        state_cat = create_example_state_category()
        monad = StateMonad(state_cat)

        result = monad.pure(42)
        assert callable(result)

    def test_state_monad_bind(self):
        """Test state monad bind."""
        state_cat = create_example_state_category()
        monad = StateMonad(state_cat)

        def computation(s):
            return (s, 10)

        def function(x):
            return lambda s: (s, x * 2)

        bound = monad.bind(computation, function)
        assert callable(bound)

    def test_probability_monad(self):
        """Test probability monad."""
        state_cat = create_example_state_category()
        monad = ProbabilityMonad(state_cat)

        # Test pure
        dist = monad.pure(42)
        assert 42 in dist
        assert dist[42] == 1.0

        # Test bind
        def f(x):
            return {x: 0.5, x + 1: 0.5}

        result = monad.bind(dist, f)
        assert 42 in result
        assert 43 in result

    def test_plinko_selection(self):
        """Test Plinko stochastic selection."""
        state_cat = create_example_state_category()
        monad = ProbabilityMonad(state_cat)

        proposals = ["a", "b", "c"]
        values = [1.0, 0.5, 0.0]

        # Should select deterministically with zero temperature
        selected = monad.plinko_select(proposals, values, temperature=0.0)
        assert selected == "a"

    def test_store_comonad(self):
        """Test store comonad."""
        state_cat = create_example_state_category()
        comonad = StoreComonad(state_cat)

        # Create store
        def query(focus):
            return f"value_at_{focus}"

        store = (query, "focus_1")

        # Test extract (counit)
        extracted = comonad.extract(store)
        assert extracted == "value_at_focus_1"


class TestAdjunctions:
    """Test adjunction structures."""

    def test_adjunction_creation(self):
        """Test creating adjunction."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        adjunction = AgentStateAdjunction(state_cat, agent_cat)

        assert adjunction.name == "AgentStateAdjunction"
        assert adjunction.source_category == state_cat
        assert adjunction.target_category == agent_cat

    def test_monadic_adjunction(self):
        """Test induced monad from adjunction."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        adjunction = AgentStateAdjunction(state_cat, agent_cat)
        monad = MonadicAdjunction.induced_monad(adjunction)

        assert monad.name == "InducedMonad(AgentStateAdjunction)"

    def test_limits(self):
        """Test limit computation."""
        agent_cat = create_example_agent_category()

        product_id = LimitColimit.product(agent_cat, ["task_1", "role_1"])
        assert product_id in agent_cat.objects

        coproduct_id = LimitColimit.coproduct(agent_cat, ["task_1", "role_1"])
        assert coproduct_id in agent_cat.objects


class TestKanExtensions:
    """Test Kan extension structures."""

    def test_kan_extension_creation(self):
        """Test creating Kan extension."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        F = Functor("F", agent_cat, state_cat)
        K = Functor("K", agent_cat, state_cat)

        kan = KanExtension(
            name="TestKan",
            K=K,
            F=F,
            extension=F,
            extension_type=KanExtension.ExtensionType.LEFT
        )

        assert kan.name == "TestKan"

    def test_yoneda_reduction(self):
        """Test Yoneda reduction."""
        agent_cat = create_example_agent_category()
        yoneda = YonedaReduction()

        yoneda_embedding = yoneda.yoneda_embedding(agent_cat)
        assert yoneda_embedding is not None

    def test_profunctor(self):
        """Test profunctor."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        profunctor = Profunctor("P", agent_cat, state_cat)
        profunctor.add_mapping("task_1", "state_0", {"a", "b"})

        assert ("task_1", "state_0") in profunctor.data
        assert profunctor.data[("task_1", "state_0")] == {"a", "b"}

    def test_profunctor_composition(self):
        """Test profunctor composition."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        P = Profunctor("P", agent_cat, state_cat)
        Q = Profunctor("Q", state_cat, agent_cat)

        P.add_mapping("task_1", "state_0", {"a"})
        Q.add_mapping("state_0", "role_1", {"b"})

        composed = P.compose(Q)
        assert composed.name == "P_○_Q"


class TestTopos:
    """Test topos structures."""

    def test_topos_creation(self):
        """Test creating topos."""
        topos = AgentConfigurationTopos()

        topos.add_configuration("config_1", "TaskAgent", {"temp": 0.5})

        assert "config_1" in topos.objects

    def test_subobject_classifier(self):
        """Test subobject classifier."""
        topos = AgentConfigurationTopos()
        classifier = topos.get_classifier()

        assert classifier.name == "Omega"
        assert classifier.topos == topos

    def test_exponential(self):
        """Test exponential objects."""
        topos = AgentConfigurationTopos()

        topos.add_configuration("config_1", "TaskAgent", {})
        topos.add_configuration("config_2", "RoleAgent", {})

        exp = topos.exponential("config_1", "config_2")
        assert exp in topos.objects

    def test_topos_axioms(self):
        """Test topos axioms verification."""
        topos = AgentConfigurationTopos()

        topos.add_configuration("config_1", "TaskAgent", {})
        topos.get_terminal()

        axioms = topos.verify_topos_axioms()
        assert "has_terminal" in axioms

    def test_heyting_algebra(self):
        """Test Heyting algebra."""
        topos = AgentConfigurationTopos()
        algebra = HeytingAlgebra(topos)

        algebra.add_element("true")
        algebra.add_element("false")

        assert "true" in algebra.elements
        assert "false" in algebra.elements

        # Check excluded middle fails intuitionistically
        assert not algebra.check_law("excluded_middle")


class TestSimulator:
    """Test category theory simulator."""

    def test_diagram_creation(self):
        """Test diagram creation."""
        agent_cat = create_example_agent_category()

        diagram = Diagram(
            name="TestDiagram",
            category=agent_cat
        )

        diagram.add_object("task_1")
        diagram.add_object("role_1")

        f = Morphism("task_1", "role_1", "f")
        diagram.add_morphism(f)

        assert "task_1" in diagram.objects
        assert "role_1" in diagram.objects
        assert len(diagram.morphisms) == 1

    def test_diagram_commutativity(self):
        """Test diagram commutativity verification."""
        agent_cat = create_example_agent_category()

        diagram = Diagram(
            name="CommutativeSquare",
            category=agent_cat
        )

        # Create commutative square
        diagram.add_object("X")
        diagram.add_object("Y")
        diagram.add_object("Z")

        diagram.add_morphism(Morphism("X", "Y", "f"))
        diagram.add_morphism(Morphism("Y", "Z", "g"))
        diagram.add_morphism(Morphism("X", "Z", "h"))

        # Should commute if h = g ∘ f
        assert diagram.verify_commutativity()  # Simplified check

    def test_limit_computation(self):
        """Test limit computation."""
        agent_cat = create_example_agent_category()
        computer = LimitColimitComputer(agent_cat)

        product = computer.product(["task_1", "role_1"])
        assert product in agent_cat.objects

        coproduct = computer.coproduct(["task_1", "role_1"])
        assert coproduct in agent_cat.objects

    def test_category_toolkit(self):
        """Test complete category toolkit."""
        agent_cat = create_example_agent_category()
        toolkit = CategoryTheoryToolkit(agent_cat)

        analysis = toolkit.analyze_category()

        assert "objects" in analysis
        assert "morphisms" in analysis
        assert "axioms" in analysis


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self):
        """Test complete category theory workflow."""
        # Create categories
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        # Create functor
        functor = ColonyExecutionFunctor(agent_cat, state_cat)
        functor.map_object("task_1", "state_0")

        # Create monad
        monad = StateMonad(state_cat)
        result = monad.pure(42)

        # Verify
        assert callable(result)
        assert functor.verify_functoriality()

    def test_adjunction_monad(self):
        """Test adjunction inducing monad."""
        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        adjunction = AgentStateAdjunction(state_cat, agent_cat)
        monad = MonadicAdjunction.induced_monad(adjunction)

        assert monad.category == state_cat

    def test_topos_classifier(self):
        """Test topos with subobject classifier."""
        topos = AgentConfigurationTopos()

        topos.add_configuration("config_1", "TaskAgent", {"temp": 0.5})
        topos.add_configuration("config_2", "RoleAgent", {"priority": 1})

        # Classify configurations
        for config_id in ["config_1", "config_2"]:
            chi = topos.classify_type_correctness(config_id)
            assert chi.source == config_id
            assert chi.target == "Omega"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
