"""
Mega HSSE Transformer — Lifting Safety Factor Module

Implements the Safety Factor calculation for lifting and rigging operations.

Formula reference:
    SF = Breaking_Strength / (Applied_Load × Dynamic_Factor)

    Where:
        Breaking_Strength = Rated breaking/working load limit of lifting equipment
        Applied_Load      = Actual weight of the load to be lifted
        Dynamic_Factor    = Amplification factor for dynamic forces
                           (movement, wind, shock loading, etc.)

Minimum Safety Factor Requirements (standard reference values):
    - Standard industrial lifts:       SF ≥ 3.0 (typical minimum)
    - Critical lifts (general):        SF ≥ 4.0
    - Critical lifts (offshore):       SF ≥ 5.0 (standard for offshore operations)
    - Lifts over personnel:            SF ≥ 7.0

Reference:
    ASME B30.9 — Slings (American Society of Mechanical Engineers)
    DNV-OS-H205 — Lifting Operations (Det Norske Veritas)
    OSHA 29 CFR 1926.753 — Overhead hoists

Research Status: Foundation Built — Validation Pending
"""

from src.math_engine.schemas import LiftingInput, LiftingOutput


def calculate_safety_factor(inputs: LiftingInput) -> LiftingOutput:
    """Calculate the safety factor for a lifting operation.

    Formula: SF = Breaking_Strength / (Applied_Load × Dynamic_Factor)

    The result is assessed against the minimum_sf threshold to determine
    if the lift is safe to proceed. A FAIL result should trigger
    STOP WORK AUTHORITY per safety management protocols.

    Args:
        inputs: LiftingInput dataclass with breaking strength, applied load,
                dynamic factor, and minimum required safety factor.

    Returns:
        LiftingOutput dataclass with computed SF, pass/fail status,
        decision string, and formula reference.

    Raises:
        ValueError: If breaking_strength, applied_load, or dynamic_factor
                    are not positive, or if minimum_sf is not positive.

    Example (from Mega HSSE Transformer scenario):
        >>> from src.math_engine.schemas import LiftingInput
        >>> inputs = LiftingInput(breaking_strength=250, applied_load=50,
        ...                       dynamic_factor=1.5, minimum_sf=5.0)
        >>> result = calculate_safety_factor(inputs)
        >>> round(result.safety_factor, 2)
        3.33
        >>> result.status
        'FAIL'
        >>> result.decision
        'STOP WORK AUTHORITY — Insufficient Safety Factor'
    """
    if inputs.breaking_strength <= 0:
        raise ValueError(
            f"Breaking strength must be positive, got {inputs.breaking_strength}."
        )
    if inputs.applied_load <= 0:
        raise ValueError(
            f"Applied load must be positive, got {inputs.applied_load}."
        )
    if inputs.dynamic_factor <= 0:
        raise ValueError(
            f"Dynamic factor must be positive, got {inputs.dynamic_factor}."
        )
    if inputs.minimum_sf <= 0:
        raise ValueError(
            f"Minimum safety factor must be positive, got {inputs.minimum_sf}."
        )

    sf = inputs.breaking_strength / (inputs.applied_load * inputs.dynamic_factor)

    if sf >= inputs.minimum_sf:
        status = "PASS"
        decision = "Lift may proceed — Safety Factor within acceptable limits"
    else:
        status = "FAIL"
        decision = "STOP WORK AUTHORITY — Insufficient Safety Factor"

    return LiftingOutput(
        safety_factor=sf,
        status=status,
        minimum_required=inputs.minimum_sf,
        decision=decision,
    )
