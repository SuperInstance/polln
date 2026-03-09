"""
POLLN Differential Equations Analysis Package

Advanced mathematical analysis of POLLN dynamics using PDEs and SDEs.
"""

__version__ = "1.0.0"
__author__ = "POLLN Development Team"

# Core modules
from . import deepseek_math
from . import fokker_planck
from . import information_fluid
from . import reaction_diffusion
from . import hjb_optimal_control
from . import stochastic_dynamics
from . import pde_solver

# Main classes
from .deepseek_math import DeepSeekMath, APICallTracker, DerivationResult
from .fokker_planck import FokkerPlanckSolver
from .information_fluid import InformationFluidSolver
from .reaction_diffusion import ReactionDiffusionSolver
from .hjb_optimal_control import HJBSolver
from .stochastic_dynamics import SDEIntegrator, ExitTimeSolver, FokkerPlanckSolver as SDE_FokkerPlanck
from .pde_solver import PDESolver, HeatEquationSolver, WaveEquationSolver, AdvectionEquationSolver

__all__ = [
    # Modules
    'deepseek_math',
    'fokker_planck',
    'information_fluid',
    'reaction_diffusion',
    'hjb_optimal_control',
    'stochastic_dynamics',
    'pde_solver',

    # DeepSeek Integration
    'DeepSeekMath',
    'APICallTracker',
    'DerivationResult',

    # Solvers
    'FokkerPlanckSolver',
    'InformationFluidSolver',
    'ReactionDiffusionSolver',
    'HJBSolver',
    'SDEIntegrator',
    'ExitTimeSolver',

    # General PDE Solver
    'PDESolver',
    'HeatEquationSolver',
    'WaveEquationSolver',
    'AdvectionEquationSolver',
]
