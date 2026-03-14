"""
TernaryAir - Open-source ternary inference simulator

This package provides a working simulator for the TernaryAir architecture,
allowing developers to experiment with ternary neural network inference
without hardware.
"""

__version__ = "0.1.0"
__author__ = "Casey DiGennaro"
__license__ = "MIT"

from .simulator import Simulator, TernaryAir
from .demo import run as run_demo

__all__ = ["Simulator", "TernaryAir", "run_demo"]
