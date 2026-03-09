"""
POLLN Robustness Testing Suite
===============================

Comprehensive adversarial testing framework for validating POLLN's
resilience under attack conditions.

Modules:
- prompt_injection: Adversarial input testing
- byzantine_agents: Byzantine fault tolerance
- cascade_failure: Cascading failure simulation
- state_corruption: State corruption recovery
- resource_exhaustion: Resource stress testing
- hardening_generator: Configuration generation
- test_robustness: Unit tests

Usage:
    python run_all.py --quick --generate-config
"""

from .prompt_injection import PromptInjectionSimulator
from .byzantine_agents import ByzantineSimulator, AggregationStrategy
from .cascade_failure import CascadingFailureSimulator, ContainmentStrategy
from .state_corruption import StateCorruptionSimulator, RecoveryStrategy
from .resource_exhaustion import ResourceExhaustionSimulator, MitigationStrategy

__version__ = "1.0.0"
__author__ = "POLLN Team"

__all__ = [
    "PromptInjectionSimulator",
    "ByzantineSimulator",
    "AggregationStrategy",
    "CascadingFailureSimulator",
    "ContainmentStrategy",
    "StateCorruptionSimulator",
    "RecoveryStrategy",
    "ResourceExhaustionSimulator",
    "MitigationStrategy",
]
