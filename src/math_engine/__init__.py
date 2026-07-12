"""
Mega HSSE Transformer — Mathematical Safety Engine

This package provides deterministic, formula-based safety calculations
for core HSSE domains. All functions produce explicit, traceable outputs
with formula references.

Research Status: Foundation Built — Validation Pending

Modules:
    schemas   — Typed input/output dataclasses
    risk      — Fine-Kinney risk calculation
    exposure  — Time-Weighted Average (TWA) exposure
    lifting   — Lifting safety factor
    incident  — Combined failure probability
    cli       — Command-line interface
"""

from src.math_engine.risk import calculate_initial_risk, calculate_residual_risk
from src.math_engine.exposure import calculate_twa
from src.math_engine.lifting import calculate_safety_factor
from src.math_engine.incident import calculate_failure_probability

__all__ = [
    "calculate_initial_risk",
    "calculate_residual_risk",
    "calculate_twa",
    "calculate_safety_factor",
    "calculate_failure_probability",
]
