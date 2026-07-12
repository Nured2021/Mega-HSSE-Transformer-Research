"""
Mega HSSE Transformer — Verification Rule Application Engine

Applies the deterministic safety rule registry against a context dictionary
of computed values, returning pass/fail results with full evidence traces.

This engine implements the Logic Gate (G) in the Transformer reasoning chain:

    RC = Softmax(QKᵀ/√dk) · V · Logic Gate(G)

The gate blocks or flags unsafe decisions based on physical safety constraints,
regardless of the AI model's probabilistic confidence.

Research Status: Foundation Scaffold Built — Extension Required
"""

from typing import Any, Dict, List, Optional

from src.verification.rules import RULES, RuleResult, SafetyRule

# Supported comparison operators for rule evaluation
_OPERATORS = {
    "lt": lambda val, thr: val < thr,
    "lte": lambda val, thr: val <= thr,
    "gt": lambda val, thr: val > thr,
    "gte": lambda val, thr: val >= thr,
    "eq": lambda val, thr: val == thr,
}


def check_rule(rule: SafetyRule, context: Dict[str, Any]) -> Optional[RuleResult]:
    """Evaluate a single safety rule against the provided context.

    Args:
        rule: SafetyRule defining the constraint to check.
        context: Dictionary of computed values to evaluate. If the rule's
                 context_key is not present, the rule is skipped (returns None).

    Returns:
        RuleResult with violation status and evidence trace, or None if the
        required context key is not present in the context dict.

    Raises:
        ValueError: If the rule's operator is not a supported comparison operator.
    """
    if rule.context_key not in context:
        return None

    if rule.operator not in _OPERATORS:
        raise ValueError(
            f"Unsupported operator '{rule.operator}' in rule '{rule.rule_id}'. "
            f"Supported operators: {list(_OPERATORS.keys())}"
        )

    context_value = float(context[rule.context_key])
    compare_fn = _OPERATORS[rule.operator]
    violated = compare_fn(context_value, rule.threshold)

    return RuleResult(
        rule_id=rule.rule_id,
        violated=violated,
        decision=rule.decision if violated else None,
        reason=rule.reason if violated else None,
        context_key=rule.context_key,
        context_value=context_value,
        threshold=rule.threshold,
        standard=rule.standard,
    )


def apply_rules(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply all registered safety rules to the provided context.

    Evaluates every rule in the RULES registry against the context dict.
    Rules whose context keys are absent are skipped. Returns a list of
    result dictionaries, one per applicable rule.

    Args:
        context: Dictionary of computed values to check against safety rules.
            Supported keys and their meanings:
                'oxygen_percent'   — O₂ concentration in % (oxygen_threshold rule)
                'safety_factor'    — Computed lifting SF (lifting_sf_critical rule)
                'twa_ratio'        — TWA / OEL ratio (twa_exceedance rule)
                'risk_score'       — Fine-Kinney risk score (extreme_risk rule)

    Returns:
        List of result dicts, each containing:
            - rule_id: str
            - violated: bool
            - decision: str or None
            - reason: str or None
            - context_key: str
            - context_value: float
            - threshold: float
            - standard: str

    Raises:
        ValueError: If any rule contains an unsupported operator.

    Example:
        >>> results = apply_rules({"oxygen_percent": 18.0})
        >>> results[0]["violated"]
        True
        >>> results[0]["decision"]
        'ENTRY DENIED — Unsafe Atmospheric Condition'
    """
    results = []
    for rule in RULES:
        result = check_rule(rule, context)
        if result is not None:
            results.append(
                {
                    "rule_id": result.rule_id,
                    "violated": result.violated,
                    "decision": result.decision,
                    "reason": result.reason,
                    "context_key": result.context_key,
                    "context_value": result.context_value,
                    "threshold": result.threshold,
                    "standard": result.standard,
                }
            )
    return results


def any_violated(context: Dict[str, Any]) -> bool:
    """Check if any safety rule is violated for the given context.

    Args:
        context: Dictionary of computed values to evaluate.

    Returns:
        True if at least one rule is violated, False otherwise.
    """
    results = apply_rules(context)
    return any(r["violated"] for r in results)
