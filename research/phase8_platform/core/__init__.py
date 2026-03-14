"""
SuperInstance Research Platform - Core Module
==============================================

Core platform components for integration and extension.
"""

from .simulation_registry import (
    SimulationRegistry,
    SimulationImplementation,
    SimulationSource,
    get_registry,
    register_custom_simulation
)

__all__ = [
    'SimulationRegistry',
    'SimulationImplementation',
    'SimulationSource',
    'get_registry',
    'register_custom_simulation'
]
