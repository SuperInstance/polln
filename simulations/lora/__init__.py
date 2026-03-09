"""
LoRA Composition Mathematics Validation Suite

This package validates the mathematical foundations of POLLN's LoRA Library concept:
- Small base models + interchangeable LoRA adapters = expert agents
- Mathematical validation of rank decomposition, interference, and composition
"""

__version__ = "0.1.0"
__author__ = "POLLN Research Team"

from .rank_analysis import RankSufficiencyAnalyzer
from .interference import InterferenceDetector
from .composition import CompositionOptimizer
from .scaling_laws import ScalingLawAnalyzer

__all__ = [
    "RankSufficiencyAnalyzer",
    "InterferenceDetector",
    "CompositionOptimizer",
    "ScalingLawAnalyzer",
]
