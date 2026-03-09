"""
TD(λ) Learning Simulations

This package provides mathematical validation of TD(λ) learning convergence
for the POLLN value network system.

Mathematical Foundation:
    TD(λ): δ_t = r_t + γ V(s_{t+1}) - V(s_t)
    V(s) ← V(s) + α × δ_t × e(s)
    e(s) ← γλe(s) + 1(s=s_t)

Theorems to Prove:
    T1: TD Convergence - TD(0) converges with probability 1 if Σα² < ∞
    T2: Optimism Initialization - Optimistic values encourage exploration
    T3: Eligibility Traces - Trace effects on convergence rate
"""

__version__ = "1.0.0"
__author__ = "POLLN Research Team"

from .td_lambda_convergence import TDConvergenceSimulator
from .function_approx import FunctionApproxSimulator
from .off_policy import OffPolicySimulator
from .credit_assignment import CreditAssignmentSimulator

__all__ = [
    "TDConvergenceSimulator",
    "FunctionApproxSimulator",
    "OffPolicySimulator",
    "CreditAssignmentSimulator",
]
