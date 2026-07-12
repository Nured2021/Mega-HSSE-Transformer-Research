"""
Mega HSSE Transformer — Deterministic Verification Layer

This package provides a rule-based verification system that enforces
deterministic safety constraints on computed outputs and AI-generated
decisions.

Architecture concept:
    RC = Softmax(QKᵀ/√dk) · V · Logic Gate(G)

    Where G is this verification layer — a deterministic safety constraint
    gate that overrides probabilistic outputs when physical safety rules
    are violated.

Modules:
    rules  — Safety constraint rule definitions
    engine — Rule application engine

Research Status: Foundation Scaffold Built — Extension Required
"""

from src.verification.rules import RULES, SafetyRule, RuleResult
from src.verification.engine import apply_rules, check_rule

__all__ = [
    "RULES",
    "SafetyRule",
    "RuleResult",
    "apply_rules",
    "check_rule",
]
