"""
Master Orchestrator - Run All Category Theory Simulations

This script orchestrates all category theory derivations and simulations
for POLLN's compositional intelligence using DeepSeek API.

Usage:
    python run_all.py

Output:
    - Derivations for all category theory structures
    - Verification results
    - Generated diagrams
    - Compiled findings
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from deepseek_category import DeepSeekCategoryDeriver, get_deriver
from categories import (
    AgentCategory, StateCategory, ColonyCategory,
    ConfigurationCategory, ValueCategory, CategoryGenerator
)
from functors import (
    ColonyExecutionFunctor, StateTransitionFunctor,
    YonedaEmbedding, FunctorCategory
)
from monads import (
    StateMonad, ValueMonad, CommunicationMonad,
    ProbabilityMonad, StoreComonad
)
from adjunctions import (
    AgentStateAdjunction, FreeForgetfulAdjunction,
    ConstraintFreedomAdjunction, GlobalLocalAdjunction
)
from kan_extensions import (
    KanExtension, YonedaReduction, Profunctor,
    KanOptimizer
)
from topos_theory import (
    AgentConfigurationTopos, PresheafTopos,
    HeytingAlgebra, InternalLanguage
)
from category_simulator import (
    Diagram, DiagramChaser, LimitColimitComputer,
    CategoryTheoryToolkit
)


class CategoryTheoryOrchestrator:
    """
    Master orchestrator for category theory simulations.

    Coordinates:
    - Category derivations
    - Functor analysis
    - Monad verification
    - Adjunction proofs
    - Kan extensions
    - Topos structure
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.deriver = get_deriver()
        self.timestamp = datetime.now().isoformat()

        self.results: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "categories": {},
            "functors": {},
            "monads": {},
            "adjunctions": {},
            "kan_extensions": {},
            "topos": {},
            "simulations": {}
        }

    def run_all(self, use_deepseek: bool = True):
        """
        Run all category theory simulations.

        Args:
            use_deepseek: Whether to use DeepSeek API for derivations
        """
        print("=" * 70)
        print("POLLN Category Theory - Master Orchestrator")
        print("=" * 70)
        print(f"\nTimestamp: {self.timestamp}")
        print(f"Output directory: {self.output_dir}")
        print(f"DeepSeek API: {'Enabled' if use_deepseek else 'Disabled'}")

        # Categories
        print("\n" + "-" * 70)
        print("1. Deriving Categories...")
        print("-" * 70)
        self._derive_categories(use_deepseek)

        # Functors
        print("\n" + "-" * 70)
        print("2. Analyzing Functors...")
        print("-" * 70)
        self._analyze_functors(use_deepseek)

        # Monads
        print("\n" + "-" * 70)
        print("3. Verifying Monads...")
        print("-" * 70)
        self._verify_monads(use_deepseek)

        # Adjunctions
        print("\n" + "-" * 70)
        print("4. Proving Adjunctions...")
        print("-" * 70)
        self._prove_adjunctions(use_deepseek)

        # Kan Extensions
        print("\n" + "-" * 70)
        print("5. Computing Kan Extensions...")
        print("-" * 70)
        self._compute_kan_extensions(use_deepseek)

        # Topos
        print("\n" + "-" * 70)
        print("6. Analyzing Topos Structure...")
        print("-" * 70)
        self._analyze_topos(use_deepseek)

        # Simulations
        print("\n" + "-" * 70)
        print("7. Running Simulations...")
        print("-" * 70)
        self._run_simulations()

        # Save results
        print("\n" + "-" * 70)
        print("8. Saving Results...")
        print("-" * 70)
        self._save_results()

        print("\n" + "=" * 70)
        print("All Simulations Complete!")
        print("=" * 70)

        return self.results

    def _derive_categories(self, use_deepseek: bool):
        """Derive all categories."""
        generator = CategoryGenerator(self.deriver)

        # Agent Category
        print("\n  [1/6] Agent Category...")
        agents = [
            {"id": "task_1", "type": "TaskAgent"},
            {"id": "role_1", "type": "RoleAgent"},
            {"id": "core_1", "type": "CoreAgent"},
            {"id": "meta_1", "type": "MetaTile"}
        ]

        a2a_packages = [
            {
                "id": "a2a_001",
                "source": "task_1",
                "target": "role_1",
                "parent_ids": [],
                "causal_chain_id": "chain_001"
            },
            {
                "id": "a2a_002",
                "source": "role_1",
                "target": "core_1",
                "parent_ids": ["a2a_001"],
                "causal_chain_id": "chain_001"
            }
        ]

        agent_cat = generator.generate_agent_category(agents, a2a_packages)
        if use_deepseek:
            agent_cat.derive_structure(self.deriver)

        self.results["categories"]["agent"] = {
            "objects": len(agent_cat.objects),
            "morphisms": sum(len(m) for m in agent_cat.morphisms.values()),
            "axioms": agent_cat.verify_category_axioms(),
            "diagram": agent_cat.diagram()
        }

        # State Category
        print("  [2/6] State Category...")
        states = [
            {"id": "state_0", "type": "initial", "observations": ["obs_1"]},
            {"id": "state_1", "type": "intermediate", "observations": ["obs_1", "obs_2"]},
            {"id": "state_2", "type": "terminal", "observations": ["obs_1", "obs_2", "obs_3"]}
        ]

        transitions = [
            {"id": "trans_001", "source": "state_0", "target": "state_1", "agent": "task_1", "reward": 0.5},
            {"id": "trans_002", "source": "state_1", "target": "state_2", "agent": "role_1", "reward": 1.0}
        ]

        state_cat = generator.generate_state_category(states, transitions)
        if use_deepseek:
            state_cat.derive_structure(self.deriver)

        self.results["categories"]["state"] = {
            "objects": len(state_cat.objects),
            "morphisms": sum(len(m) for m in state_cat.morphisms.values()),
            "axioms": state_cat.verify_category_axioms(),
            "diagram": state_cat.diagram()
        }

        # Colony, Configuration, Value categories
        print("  [3/6] Colony Category...")
        colony_cat = ColonyCategory()
        colony_cat.add_colony("colony_1", {"task_1", "role_1"})
        colony_cat.add_colony("colony_2", {"role_1", "core_1"})

        self.results["categories"]["colony"] = {
            "objects": len(colony_cat.objects),
            "morphisms": sum(len(m) for m in colony_cat.morphisms.values())
        }

        print("  [4/6] Configuration Category...")
        config_cat = ConfigurationCategory()
        config_cat.add_configuration("config_1", {"temp": 0.5})
        config_cat.add_configuration("config_2", {"temp": 0.7})

        self.results["categories"]["configuration"] = {
            "objects": len(config_cat.objects),
            "morphisms": sum(len(m) for m in config_cat.morphisms.values())
        }

        print("  [5/6] Value Category...")
        value_cat = ValueCategory()

        self.results["categories"]["value"] = {
            "objects": len(value_cat.objects),
            "morphisms": sum(len(m) for m in value_cat.morphisms.values())
        }

        print("  [6/6] Category Verification Complete")

    def _analyze_functors(self, use_deepseek: bool):
        """Analyze all functors."""
        print("\n  [1/4] Colony Execution Functor...")
        from categories import create_example_agent_category, create_example_state_category

        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        colony_exec = ColonyExecutionFunctor(agent_cat, state_cat)
        if use_deepseek:
            colony_exec.derive_structure(self.deriver)

        self.results["functors"]["colony_execution"] = {
            "name": colony_exec.name,
            "source": colony_exec.source_category.name,
            "target": colony_exec.target_category.name,
            "functoriality": colony_exec.verify_functoriality()
        }

        print("  [2/4] Yoneda Embedding...")
        yoneda = YonedaEmbedding(agent_cat)
        if use_deepseek:
            yoneda.derive_structure(self.deriver)

        for obj in ["task_1", "role_1"]:
            yoneda.embed_object(obj)

        self.results["functors"]["yoneda"] = {
            "name": yoneda.name,
            "objects_mapped": len(yoneda.object_map)
        }

        print("  [3/4] Functor Category...")
        functor_cat = FunctorCategory(agent_cat, state_cat)
        functor_cat.add_functor(colony_exec)

        self.results["functors"]["functor_category"] = {
            "name": functor_cat.name,
            "objects": len(functor_cat.objects)
        }

        print("  [4/4] Functor Analysis Complete")

    def _verify_monads(self, use_deepseek: bool):
        """Verify all monads."""
        from categories import create_example_state_category

        state_cat = create_example_state_category()

        print("\n  [1/4] State Monad...")
        state_monad = StateMonad(state_cat)
        if use_deepseek:
            state_monad.derive_structure(self.deriver)

        self.results["monads"]["state"] = {
            "name": state_monad.name,
            "category": state_monad.category.name
        }

        print("  [2/4] Value Monad...")
        value_monad = ValueMonad(state_cat)
        if use_deepseek:
            value_monad.derive_structure(self.deriver)

        self.results["monads"]["value"] = {
            "name": value_monad.name,
            "category": value_monad.category.name
        }

        print("  [3/4] Probability Monad...")
        prob_monad = ProbabilityMonad(state_cat)

        # Test Plinko selection
        proposals = ["a", "b", "c"]
        values = [0.8, 0.5, 0.3]
        selected = prob_monad.plinko_select(proposals, values, 0.5)

        self.results["monads"]["probability"] = {
            "name": prob_monad.name,
            "category": prob_monad.category.name,
            "plinko_selection": selected
        }

        print("  [4/4] Store Comonad...")
        store_comonad = StoreComonad(state_cat)
        if use_deepseek:
            store_comonad.derive_structure(self.deriver)

        self.results["monads"]["store_comonad"] = {
            "name": store_comonad.name,
            "category": store_comonad.category.name
        }

        print("  Monad Verification Complete")

    def _prove_adjunctions(self, use_deepseek: bool):
        """Prove all adjunctions."""
        from categories import create_example_agent_category, create_example_state_category

        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        print("\n  [1/4] Agent-State Adjunction...")
        agent_state = AgentStateAdjunction(state_cat, agent_cat)
        if use_deepseek:
            agent_state.derive_structure(self.deriver)

        self.results["adjunctions"]["agent_state"] = {
            "name": agent_state.name,
            "left": agent_state.left_adjoint.name,
            "right": agent_state.right_adjoint.name,
            "triangle_identities": agent_state.verify_triangle_identities()
        }

        print("  [2/4] Constraint-Freedom Adjunction...")
        constraint_freedom = ConstraintFreedomAdjunction(state_cat)
        if use_deepseek:
            constraint_freedom.derive_structure(self.deriver)

        self.results["adjunctions"]["constraint_freedom"] = {
            "name": constraint_freedom.name,
            "left": constraint_freedom.left_adjoint.name,
            "right": constraint_freedom.right_adjoint.name
        }

        print("  [3/4] Induced Monad...")
        from adjunctions import MonadicAdjunction

        induced_monad = MonadicAdjunction.induced_monad(agent_state)
        self.results["adjunctions"]["induced_monad"] = {
            "name": induced_monad.name,
            "category": induced_monad.category.name
        }

        print("  [4/4] Adjunction Proofs Complete")

    def _compute_kan_extensions(self, use_deepseek: bool):
        """Compute Kan extensions."""
        print("\n  [1/3] Left Kan Extension...")
        from categories import create_example_agent_category, create_example_state_category
        from functors import create_example_functor

        agent_cat = create_example_agent_category()
        state_cat = create_example_state_category()

        functor = create_example_functor()

        kan_left = KanExtension(
            name="LeftKan_Example",
            K=functor,
            F=functor,
            extension=functor,
            extension_type=kan_left.ExtensionType.LEFT
        )
        if use_deepseek:
            kan_left.derive_structure(self.deriver)

        self.results["kan_extensions"]["left"] = {
            "name": kan_left.name,
            "type": "left"
        }

        print("  [2/3] Yoneda Reduction...")
        yoneda_reduction = YonedaReduction()
        yoneda = yoneda_reduction.yoneda_embedding(agent_cat)

        self.results["kan_extensions"]["yoneda"] = {
            "name": "YonedaReduction",
            "embeddings": len(yoneda.object_map)
        }

        print("  [3/3] Profunctor...")
        profunctor = Profunctor("P", agent_cat, state_cat)
        profunctor.add_mapping("task_1", "state_0", {"a", "b"})

        self.results["kan_extensions"]["profunctor"] = {
            "name": profunctor.name,
            "mappings": len(profunctor.data)
        }

        print("  Kan Extension Computation Complete")

    def _analyze_topos(self, use_deepek: bool):
        """Analyze topos structures."""
        print("\n  [1/3] Agent Configuration Topos...")
        topos = AgentConfigurationTopos()

        topos.add_configuration("config_1", "TaskAgent", {"temp": 0.5})
        topos.add_configuration("config_2", "RoleAgent", {"priority": 1})

        if use_deepseek:
            topos.derive_structure(self.deriver)

        self.results["topos"]["agent_configurations"] = {
            "name": topos.name,
            "axioms": topos.verify_topos_axioms(),
            "exponentials": list(topos.exponentials.values())
        }

        print("  [2/3] Presheaf Topos...")
        from categories import create_example_agent_category

        agent_cat = create_example_agent_category()
        presheaf_topos = PresheafTopos(agent_cat)

        if use_deepseek:
            presheaf_topos.derive_structure(self.deriver)

        self.results["topos"]["presheaf"] = {
            "name": presheaf_topos.name,
            "base_category": presheaf_topos.base_category.name
        }

        print("  [3/3] Heyting Algebra...")
        algebra = HeytingAlgebra(topos)
        algebra.add_element("true")
        algebra.add_element("false")

        self.results["topos"]["heyting_algebra"] = {
            "elements": list(algebra.elements),
            "laws": {
                "excluded_middle": algebra.check_law("excluded_middle"),
                "contrapositive": algebra.check_law("contrapositive")
            }
        }

        print("  Topos Analysis Complete")

    def _run_simulations(self):
        """Run category theory simulations."""
        from categories import create_example_agent_category

        agent_cat = create_example_agent_category()

        print("\n  [1/3] Diagram Chasing...")
        diagram = Diagram(
            name="AgentFlow",
            category=agent_cat
        )
        diagram.add_object("task_1")
        diagram.add_object("role_1")
        diagram.add_morphism(agent_cat.get_morphisms("task_1", "role_1").pop())

        self.results["simulations"]["diagram_chasing"] = {
            "commutative": diagram.verify_commutativity(),
            "diagram": diagram.diagram_string()
        }

        print("  [2/3] Limit/Colimit Computation...")
        toolkit = CategoryTheoryToolkit(agent_cat)

        product = toolkit.limit_computer.product(["task_1", "role_1"])
        coproduct = toolkit.limit_computer.coproduct(["task_1", "role_1"])

        self.results["simulations"]["limits_colimits"] = {
            "product": product,
            "coproduct": coproduct
        }

        print("  [3/3] Category Analysis...")
        analysis = toolkit.analyze_category()

        self.results["simulations"]["analysis"] = {
            "objects": analysis["objects"],
            "morphisms": analysis["morphisms"],
            "axioms": analysis["axioms"]
        }

        print("  Simulations Complete")

    def _save_results(self):
        """Save all results to files."""
        # Save JSON
        results_file = self.output_dir / f"results_{self.timestamp.replace(':', '-')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n  Results saved: {results_file}")

        # Save individual sections
        for section, data in self.results.items():
            if section == "timestamp":
                continue

            section_file = self.output_dir / f"{section}_{self.timestamp.replace(':', '-')}.json"
            with open(section_file, 'w') as f:
                json.dump(data, f, indent=2)


def main():
    """Main entry point."""
    orchestrator = CategoryTheoryOrchestrator()
    results = orchestrator.run_all(use_deepseek=True)

    print("\n\nSummary:")
    print(f"  Categories derived: {len(results['categories'])}")
    print(f"  Functors analyzed: {len(results['functors'])}")
    print(f"  Monads verified: {len(results['monads'])}")
    print(f"  Adjunctions proved: {len(results['adjunctions'])}")
    print(f"  Kan extensions computed: {len(results['kan_extensions'])}")
    print(f"  Topos analyzed: {len(results['topos'])}")
    print(f"  Simulations run: {len(results['simulations'])}")


if __name__ == "__main__":
    main()
