"""
Simulation Registry - Integration with Existing Frameworks
==========================================================

Registry that connects the unified platform with existing simulation
frameworks from Phase 6 and Phase 7.

Author: SuperInstance Research Team
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Type, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Add parent directories to path for imports
phase6_path = Path(__file__).parent.parent.parent / "phase6_advanced_simulations"
phase7_path = Path(__file__).parent.parent.parent / "phase7_gpu_simulations"
prod_path = Path(__file__).parent.parent.parent / "production_simulation_framework"

for path in [phase6_path, phase7_path, prod_path]:
    if path.exists():
        sys.path.append(str(path))

logger = logging.getLogger(__name__)


class SimulationSource(Enum):
    """Source of simulation implementation."""
    PLATFORM = "platform"          # Built-in platform implementation
    PHASE6 = "phase6"              # Phase 6 advanced simulations
    PHASE7 = "phase7"              # Phase 7 GPU/cloud simulations
    PRODUCTION = "production"      # Production framework
    CUSTOM = "custom"              # Custom user implementation


@dataclass
class SimulationImplementation:
    """Metadata about a simulation implementation."""
    name: str
    source: SimulationSource
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    description: str = ""
    parameters: Dict[str, Any] = None
    default_backend: str = "auto"

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class SimulationRegistry:
    """
    Registry for all simulation implementations.

    Maps simulation types to their actual implementations across
    Phase 6, Phase 7, and the production framework.
    """

    def __init__(self):
        self._implementations: Dict[str, SimulationImplementation] = {}
        self._lazy_imports: Dict[str, Callable] = {}
        self._register_builtin_implementations()
        self._register_phase6_implementations()
        self._register_phase7_implementations()
        self._register_production_implementations()

    def _register_builtin_implementations(self):
        """Register platform built-in implementations."""
        # Generic GPU execution
        self.register(
            simulation_type="gpu_accelerated_generic",
            implementation=SimulationImplementation(
                name="Generic GPU Execution",
                source=SimulationSource.PLATFORM,
                description="Generic GPU execution using CuPy",
                default_backend="local_gpu"
            )
        )

        # Generic CPU execution
        self.register(
            simulation_type="cpu_generic",
            implementation=SimulationImplementation(
                name="Generic CPU Execution",
                source=SimulationSource.PLATFORM,
                description="Generic CPU execution using NumPy",
                default_backend="local_cpu"
            )
        )

    def _register_phase6_implementations(self):
        """Register Phase 6 simulation implementations."""
        # Hybrid multi-paper simulation
        try:
            from hybrid_simulations import HybridSimulator, run_hybrid_simulation
            self.register(
                simulation_type="hybrid_multi_paper",
                implementation=SimulationImplementation(
                    name="Hybrid Multi-Paper Simulation",
                    source=SimulationSource.PHASE6,
                    module_path="hybrid_simulations",
                    function_name="run_hybrid_simulation",
                    description="Integration of P12, P13, P19, P20, P27",
                    default_backend="hybrid"
                )
            )
            logger.info("Registered: Hybrid Multi-Paper Simulation")
        except ImportError as e:
            logger.warning(f"Could not register Phase 6 hybrid simulations: {e}")

        # Hardware accurate simulation
        try:
            from hardware_accurate_simulation import HardwareAccurateSimulator
            self.register(
                simulation_type="hardware_accurate",
                implementation=SimulationImplementation(
                    name="Hardware Accurate Simulation",
                    source=SimulationSource.PHASE6,
                    module_path="hardware_accurate_simulation",
                    class_name="HardwareAccurateSimulator",
                    description="Realistic hardware modeling with RTX 4050",
                    default_backend="local_gpu"
                )
            )
            logger.info("Registered: Hardware Accurate Simulation")
        except ImportError as e:
            logger.warning(f"Could not register Phase 6 hardware simulations: {e}")

        # Novel algorithm discovery
        try:
            from novel_algorithm_discovery import NovelAlgorithmDiscovery
            self.register(
                simulation_type="novel_algorithm",
                implementation=SimulationImplementation(
                    name="Novel Algorithm Discovery",
                    source=SimulationSource.PHASE6,
                    module_path="novel_algorithm_discovery",
                    class_name="NovelAlgorithmDiscovery",
                    description="Discover new algorithms through search",
                    default_backend="cloud"
                )
            )
            logger.info("Registered: Novel Algorithm Discovery")
        except ImportError as e:
            logger.warning(f"Could not register Phase 6 algorithm discovery: {e}")

        # Emergence prediction
        try:
            from emergence_prediction import EmergencePredictor
            self.register(
                simulation_type="emergence_prediction",
                implementation=SimulationImplementation(
                    name="Emergence Prediction",
                    source=SimulationSource.PHASE6,
                    module_path="emergence_prediction",
                    class_name="EmergencePredictor",
                    description="Predict emergence before it happens",
                    default_backend="local_gpu"
                )
            )
            logger.info("Registered: Emergence Prediction")
        except ImportError as e:
            logger.warning(f"Could not register Phase 6 emergence prediction: {e}")

    def _register_phase7_implementations(self):
        """Register Phase 7 simulation implementations."""
        # Local GPU simulation
        try:
            from local_gpu_simulations import run_gpu_simulation
            self.register(
                simulation_type="local_gpu_sim",
                implementation=SimulationImplementation(
                    name="Local GPU Simulation",
                    source=SimulationSource.PHASE7,
                    module_path="local_gpu_simulations",
                    function_name="run_gpu_simulation",
                    description="GPU-accelerated simulation with CuPy",
                    default_backend="local_gpu"
                )
            )
            logger.info("Registered: Local GPU Simulation")
        except ImportError as e:
            logger.warning(f"Could not register Phase 7 GPU simulations: {e}")

        # Cloud enhanced simulation
        try:
            from deepinfra_integration import DeepInfraSimulator
            self.register(
                simulation_type="cloud_enhanced",
                implementation=SimulationImplementation(
                    name="Cloud Enhanced Simulation",
                    source=SimulationSource.PHASE7,
                    module_path="deepinfra_integration",
                    class_name="DeepInfraSimulator",
                    description="Cloud LLM integration via DeepInfra",
                    default_backend="cloud"
                )
            )
            logger.info("Registered: Cloud Enhanced Simulation")
        except ImportError as e:
            logger.warning(f"Could not register Phase 7 cloud simulations: {e}")

        # Adaptive learning
        try:
            from adaptive_learning import AdaptiveLearningSimulator
            self.register(
                simulation_type="adaptive_learning",
                implementation=SimulationImplementation(
                    name="Adaptive Learning Simulation",
                    source=SimulationSource.PHASE7,
                    module_path="adaptive_learning",
                    class_name="AdaptiveLearningSimulator",
                    description="Learning optimization system",
                    default_backend="hybrid"
                )
            )
            logger.info("Registered: Adaptive Learning Simulation")
        except ImportError as e:
            logger.warning(f"Could not register Phase 7 adaptive learning: {e}")

        # Hybrid orchestrator
        try:
            from hybrid_orchestrator import HybridOrchestrator
            self.register(
                simulation_type="hybrid_orchestrator",
                implementation=SimulationImplementation(
                    name="Hybrid Orchestrator",
                    source=SimulationSource.PHASE7,
                    module_path="hybrid_orchestrator",
                    class_name="HybridOrchestrator",
                    description="Intelligent GPU + Cloud orchestration",
                    default_backend="hybrid"
                )
            )
            logger.info("Registered: Hybrid Orchestrator")
        except ImportError as e:
            logger.warning(f"Could not register Phase 7 hybrid orchestrator: {e}")

    def _register_production_implementations(self):
        """Register production framework implementations."""
        try:
            from production_simulation_framework.framework import ProductionFramework
            self.register(
                simulation_type="production_benchmark",
                implementation=SimulationImplementation(
                    name="Production Benchmark",
                    source=SimulationSource.PRODUCTION,
                    module_path="production_simulation_framework.framework",
                    class_name="ProductionFramework",
                    description="Production-grade validation",
                    default_backend="local_gpu"
                )
            )
            logger.info("Registered: Production Benchmark")
        except ImportError as e:
            logger.warning(f"Could not register production framework: {e}")

    def register(
        self,
        simulation_type: str,
        implementation: SimulationImplementation
    ):
        """
        Register a simulation implementation.

        Args:
            simulation_type: Type identifier
            implementation: Implementation metadata
        """
        self._implementations[simulation_type] = implementation
        logger.debug(f"Registered simulation: {simulation_type}")

    def get(self, simulation_type: str) -> Optional[SimulationImplementation]:
        """
        Get simulation implementation by type.

        Args:
            simulation_type: Type identifier

        Returns:
            SimulationImplementation or None if not found
        """
        return self._implementations.get(simulation_type)

    def list_all(self) -> Dict[str, SimulationImplementation]:
        """Get all registered implementations."""
        return self._implementations.copy()

    def list_by_source(self, source: SimulationSource) -> Dict[str, SimulationImplementation]:
        """List implementations by source."""
        return {
            k: v for k, v in self._implementations.items()
            if v.source == source
        }

    def import_implementation(self, simulation_type: str):
        """
        Dynamically import simulation implementation.

        Args:
            simulation_type: Type to import

        Returns:
            Imported module/class/function

        Raises:
            ImportError: If implementation cannot be imported
        """
        impl = self.get(simulation_type)
        if not impl:
            raise ValueError(f"Unknown simulation type: {simulation_type}")

        if impl.source == SimulationSource.PLATFORM:
            # Built-in, no import needed
            return None

        # Import module
        if impl.module_path:
            try:
                module = __import__(impl.module_path, fromlist=[impl.class_name or impl.function_name])

                if impl.class_name:
                    return getattr(module, impl.class_name)
                elif impl.function_name:
                    return getattr(module, impl.function_name)
                else:
                    return module
            except ImportError as e:
                logger.error(f"Failed to import {impl.module_path}: {e}")
                raise

        return None

    def execute_simulation(
        self,
        simulation_type: str,
        parameters: Dict[str, Any],
        backend: str = "auto"
    ) -> Any:
        """
        Execute a simulation using registered implementation.

        Args:
            simulation_type: Type of simulation
            parameters: Simulation parameters
            backend: Backend to use

        Returns:
            Simulation results
        """
        impl = self.get(simulation_type)
        if not impl:
            raise ValueError(f"Unknown simulation type: {simulation_type}")

        # Import implementation
        sim_obj = self.import_implementation(simulation_type)

        # Execute based on implementation type
        if impl.function_name:
            # Function-based execution
            return sim_obj(**parameters)
        elif impl.class_name:
            # Class-based execution
            instance = sim_obj()
            if hasattr(instance, 'run'):
                return instance.run(**parameters)
            elif hasattr(instance, 'simulate'):
                return instance.simulate(**parameters)
            else:
                raise AttributeError(f"No run/simulate method on {impl.class_name}")
        else:
            # Module-based execution
            if hasattr(sim_obj, 'run_simulation'):
                return sim_obj.run_simulation(**parameters)
            else:
                raise AttributeError(f"No run_simulation function in {impl.module_path}")


# Global registry instance
_registry = None


def get_registry() -> SimulationRegistry:
    """Get global simulation registry instance."""
    global _registry
    if _registry is None:
        _registry = SimulationRegistry()
    return _registry


def register_custom_simulation(
    simulation_type: str,
    implementation: SimulationImplementation
):
    """Register a custom simulation implementation."""
    registry = get_registry()
    registry.register(simulation_type, implementation)


if __name__ == "__main__":
    # Test registry
    logging.basicConfig(level=logging.INFO)

    registry = get_registry()

    print("\nRegistered Simulations:")
    print("=" * 60)

    for source in SimulationSource:
        impls = registry.list_by_source(source)
        if impls:
            print(f"\n{source.value.upper()}:")
            for sim_type, impl in impls.items():
                print(f"  - {sim_type}: {impl.name}")
                print(f"    Backend: {impl.default_backend}")
                print(f"    Description: {impl.description}")
