"""
Mega HSSE Transformer — Safety Constraint Rule Definitions

Defines deterministic safety rules that enforce physical safety constraints.
These rules act as the Logic Gate (G) in the Transformer reasoning chain:

    RC = Softmax(QKᵀ/√dk) · V · Logic Gate(G)

Each rule specifies:
    - A unique rule ID
    - The context key it checks
    - A threshold value
    - A comparison operator
    - The decision to return when violated
    - The standard or regulation it references

This module is an initial scaffold. Additional rules should be added for
all 60 HSSE core areas as the research project progresses.

Research Status: Foundation Scaffold Built — Extension Required
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SafetyRule:
    """Defines a single deterministic safety constraint rule.

    Attributes:
        rule_id: Unique identifier for the rule (e.g., 'oxygen_threshold').
        context_key: The key in the context dict that this rule evaluates.
        threshold: The boundary value for the safety constraint.
        operator: Comparison operator string: 'lt', 'lte', 'gt', 'gte', 'eq'.
            The rule is *violated* when: context_value <operator> threshold.
        decision: Decision string returned when the rule is violated.
        reason: Explanation of why the rule was violated.
        standard: Regulatory standard or reference for the rule.
        hsse_area: HSSE area item number(s) this rule applies to.
    """

    rule_id: str
    context_key: str
    threshold: float
    operator: str
    decision: str
    reason: str
    standard: str
    hsse_area: str = ""


@dataclass
class RuleResult:
    """Result from evaluating a single safety rule.

    Attributes:
        rule_id: ID of the rule that was evaluated.
        violated: True if the safety constraint was violated.
        decision: The decision string (set when violated, None otherwise).
        reason: Explanation of the violation (set when violated, None otherwise).
        context_key: The context key that was checked.
        context_value: The value that was evaluated.
        threshold: The threshold that was compared against.
        standard: The regulatory standard referenced.
    """

    rule_id: str
    violated: bool
    decision: Optional[str]
    reason: Optional[str]
    context_key: str
    context_value: float
    threshold: float
    standard: str


# ---------------------------------------------------------------------------
# Initial Safety Rule Registry
#
# Rules below represent core deterministic safety constraints for the
# Mega HSSE Transformer verification layer.
#
# To add a new rule: define a SafetyRule and append it to RULES.
# ---------------------------------------------------------------------------

RULES: list[SafetyRule] = [
    SafetyRule(
        rule_id="oxygen_threshold",
        context_key="oxygen_percent",
        threshold=19.5,
        operator="lt",
        decision="ENTRY DENIED — Unsafe Atmospheric Condition",
        reason=(
            "Oxygen concentration is below the minimum safe level of 19.5%. "
            "Entry is prohibited until atmospheric conditions are corrected, "
            "monitored, and a valid Permit to Work is issued."
        ),
        standard="OSHA 1910.146 — Permit-Required Confined Spaces",
        hsse_area="Item 35: Confined Space Safety",
    ),
    SafetyRule(
        rule_id="lifting_sf_critical",
        context_key="safety_factor",
        threshold=5.0,
        operator="lt",
        decision="STOP WORK AUTHORITY — Insufficient Safety Factor",
        reason=(
            "Computed safety factor is below the minimum required value of 5.0 "
            "for critical lifting operations. The lift must not proceed until "
            "rigging configuration is revised to meet the minimum safety factor."
        ),
        standard="DNV-OS-H205 / ASME B30.9 — Critical Lifting Operations",
        hsse_area="Item 37: Lifting and Rigging",
    ),
    SafetyRule(
        rule_id="twa_exceedance",
        context_key="twa_ratio",
        threshold=1.0,
        operator="gte",
        decision="CORRECTIVE ACTION REQUIRED — TWA Exceeds Occupational Exposure Limit",
        reason=(
            "Time-Weighted Average exposure meets or exceeds the Occupational "
            "Exposure Limit (OEL). Engineering controls, administrative controls, "
            "or respiratory protective equipment must be implemented immediately."
        ),
        standard="OSHA 29 CFR 1910.1000 / NIOSH REL",
        hsse_area="Item 41: Industrial Hygiene",
    ),
    SafetyRule(
        rule_id="extreme_risk",
        context_key="risk_score",
        threshold=400.0,
        operator="gte",
        decision="STOP WORK — Extreme Risk Level Detected",
        reason=(
            "Risk score is at or above the extreme threshold of 400 "
            "(Fine-Kinney scale). Immediate work cessation is required. "
            "Risk must be reduced to an acceptable level before work resumes."
        ),
        standard="Fine-Kinney Risk Assessment (Kinney & Wiruth, 1976)",
        hsse_area="Item 5: Risk Management Framework",
    ),
    SafetyRule(
        rule_id="lel_threshold",
        context_key="gas_lel_percent",
        threshold=10.0,
        operator="gte",
        decision="STOP WORK AUTHORITY — Lower Explosive Limit Threshold Exceeded",
        reason=(
            "Gas concentration has reached or exceeded 10% of the Lower Explosive "
            "Limit (LEL). The area must be immediately evacuated and ventilated. "
            "Re-entry and ignition sources are prohibited until gas levels fall "
            "below 10% LEL and a valid Permit to Work is issued."
        ),
        standard="OSHA 1910.119 — Process Safety Management; API RP 505",
        hsse_area="Item 25: Fire Safety",
    ),
    SafetyRule(
        rule_id="unprotected_energized_work",
        context_key="unprotected_voltage_kv",
        threshold=0.0,
        operator="gt",
        decision="LOTO REQUIRED — Stop Work on Energized Equipment",
        reason=(
            "Electrical work on energized equipment without Lockout/Tagout (LOTO) "
            "has been detected. All energy sources must be isolated, locked, and "
            "tagged before work proceeds. Re-energisation is prohibited until LOTO "
            "is correctly applied and verified."
        ),
        standard="OSHA 29 CFR 1910.333 — Electrical Safety; NFPA 70E",
        hsse_area="Item 33: Electrical Safety",
    ),
    SafetyRule(
        rule_id="noise_dose_exceedance",
        context_key="noise_dose_percent",
        threshold=100.0,
        operator="gte",
        decision="CORRECTIVE ACTION REQUIRED — Noise Dose Exceeds Permissible Exposure Limit",
        reason=(
            "Worker noise dose has reached or exceeded 100% of the Permissible "
            "Exposure Limit (PEL) for the 8-hour shift. Engineering controls, "
            "administrative controls, or mandatory hearing protection must be "
            "implemented immediately to prevent noise-induced hearing loss."
        ),
        standard="OSHA 29 CFR 1910.95 — Occupational Noise Exposure; NIOSH REL 85 dBA",
        hsse_area="Item 29: Noise and Vibration",
    ),
]

# Index rules by ID for fast lookup
RULES_BY_ID: Dict[str, SafetyRule] = {rule.rule_id: rule for rule in RULES}
