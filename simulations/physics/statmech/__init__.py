"""
Statistical Mechanics Analysis for POLLN

This package provides advanced statistical mechanics tools for analyzing
phase transitions, critical phenomena, and thermodynamic behavior in
POLLN agent colonies.
"""

__version__ = "1.0.0"
__author__ = "POLLN Project"
__license__ = "MIT"

# Core modules
from .deepseek_statmech import DeepSeekStatMech
from .ensembles import (
    CanonicalEnsemble,
    MicrocanonicalEnsemble,
    GrandCanonicalEnsemble,
    analyze_agent_colony_thermodynamics
)
from .phase_transitions import (
    PhaseTransitionAnalyzer,
    LandauTheory,
    analyze_phase_transition
)
from .critical_phenomena import (
    CriticalPhenomenaAnalyzer,
    UniversalityClass,
    analyze_critical_phenomena
)
from .renormalization import (
    MomentumShellRG,
    RealSpaceRG,
    analyze_rg_flow
)
from .mean_field import (
    CurieWeissModel,
    BetheApproximation,
    GinzburgCriterion,
    analyze_mean_field
)
from .nonequilibrium import (
    MasterEquation,
    FokkerPlanckEquation,
    LinearResponseTheory,
    analyze_nonequilibrium_dynamics
)
from .statmech_simulator import (
    MetropolisMonteCarlo,
    GlauberDynamics,
    LangevinDynamics,
    temperature_scan
)

__all__ = [
    # DeepSeek integration
    "DeepSeekStatMech",

    # Ensembles
    "CanonicalEnsemble",
    "MicrocanonicalEnsemble",
    "GrandCanonicalEnsemble",
    "analyze_agent_colony_thermodynamics",

    # Phase transitions
    "PhaseTransitionAnalyzer",
    "LandauTheory",
    "analyze_phase_transition",

    # Critical phenomena
    "CriticalPhenomenaAnalyzer",
    "UniversalityClass",
    "analyze_critical_phenomena",

    # Renormalization
    "MomentumShellRG",
    "RealSpaceRG",
    "analyze_rg_flow",

    # Mean field
    "CurieWeissModel",
    "BetheApproximation",
    "GinzburgCriterion",
    "analyze_mean_field",

    # Nonequilibrium
    "MasterEquation",
    "FokkerPlanckEquation",
    "LinearResponseTheory",
    "analyze_nonequilibrium_dynamics",

    # Simulations
    "MetropolisMonteCarlo",
    "GlauberDynamics",
    "LangevinDynamics",
    "temperature_scan",
]
