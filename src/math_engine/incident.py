"""
Mega HSSE Transformer — Incident / Failure Probability Module

Implements the combined failure probability calculation for Root Cause
Analysis (RCA) and fault tree analysis.

Formula reference:
    Pf = 1 − Π(1 − Pj),   j = 1..n

    Where:
        Pj = Individual failure probability for component/event j
        n  = Number of independent failure modes or events
        Pf = Combined probability that at least one failure occurs

This models the OR gate in fault tree analysis: the system fails if
ANY one of the n independent failure modes occurs.

If Pf exceeds the defined threshold, the CAPA (Corrective and Preventive
Action) module is triggered to reset safety barriers.

Reference:
    IEC 61025 — Fault Tree Analysis (FTA)
    IEC 60812 — Failure Mode and Effects Analysis (FMEA)
    OSHA Process Safety Management Guidelines (29 CFR 1910.119)

Research Status: Foundation Built — Validation Pending
"""

import math

from src.math_engine.schemas import IncidentInput, IncidentOutput


def calculate_failure_probability(inputs: IncidentInput) -> IncidentOutput:
    """Calculate combined failure probability using Boolean OR gate logic.

    Formula: Pf = 1 − Π(1 − Pj)

    Models the probability that at least one failure mode in a set of
    independent events occurs.

    Args:
        inputs: IncidentInput dataclass with a list of individual failure
                probabilities and a combined failure threshold.

    Returns:
        IncidentOutput dataclass with combined probability, pass/fail status,
        CAPA trigger flag, and formula reference.

    Raises:
        ValueError: If probabilities list is empty, any probability is outside
                    [0.0, 1.0], or threshold is outside [0.0, 1.0].

    Example:
        >>> from src.math_engine.schemas import IncidentInput
        >>> inputs = IncidentInput(probabilities=[0.1, 0.05, 0.02], threshold=0.1)
        >>> result = calculate_failure_probability(inputs)
        >>> round(result.combined_probability, 6)
        0.163
        >>> result.status
        'EXCEEDS_THRESHOLD'
        >>> result.capa_required
        True
    """
    probabilities = inputs.probabilities
    threshold = inputs.threshold

    if not probabilities:
        raise ValueError("Probabilities list must not be empty.")

    if not (0.0 <= threshold <= 1.0):
        raise ValueError(
            f"Threshold must be between 0.0 and 1.0, got {threshold}."
        )

    for i, p in enumerate(probabilities):
        if not (0.0 <= p <= 1.0):
            raise ValueError(
                f"Probability at index {i} must be between 0.0 and 1.0, got {p}."
            )

    # Pf = 1 − Π(1 − Pj)
    product_of_survivals = math.prod(1.0 - p for p in probabilities)
    combined_probability = 1.0 - product_of_survivals

    capa_required = combined_probability > threshold
    status = "EXCEEDS_THRESHOLD" if capa_required else "ACCEPTABLE"

    return IncidentOutput(
        combined_probability=combined_probability,
        status=status,
        threshold=threshold,
        capa_required=capa_required,
    )
