"""
Mega HSSE Transformer — Risk Calculation Module

Implements the Fine-Kinney risk assessment model for initial and residual
risk quantification.

Formula references:
    Initial Risk:   Ri = P × S × E
    Residual Risk:  Rr = Ri × (1 − ε)

    Where:
        P  = Probability of hazard occurrence
        S  = Severity of consequence
        E  = Exposure frequency
        ε  = Control efficiency factor (0.0 = no control, 1.0 = full elimination)

Reference: Kinney, G.F. & Wiruth, A.D. (1976). Practical Risk Analysis for Safety
Management. NWC Technical Publication 5865, Naval Weapons Center, China Lake, CA.

Research Status: Foundation Built — Validation Pending
"""

from src.math_engine.schemas import RiskInput, RiskOutput


# Fine-Kinney risk classification thresholds (standard scale)
_RISK_LEVELS = [
    (20, "low"),
    (70, "medium"),
    (200, "high"),
    (400, "very_high"),
    (float("inf"), "extreme"),
]


def _classify_risk(score: float) -> str:
    """Classify a risk score using the Fine-Kinney standard scale.

    Args:
        score: Numeric risk score (Ri or Rr).

    Returns:
        Risk level string: 'low', 'medium', 'high', 'very_high', or 'extreme'.
    """
    for threshold, level in _RISK_LEVELS:
        if score < threshold:
            return level
    return "extreme"


def calculate_initial_risk(inputs: RiskInput) -> float:
    """Calculate initial Fine-Kinney risk score.

    Formula: Ri = P × S × E

    Args:
        inputs: RiskInput dataclass with probability, severity, and exposure values.

    Returns:
        Initial risk score as a float.

    Raises:
        ValueError: If any input parameter is negative.
    """
    if inputs.probability < 0:
        raise ValueError(
            f"Probability must be non-negative, got {inputs.probability}"
        )
    if inputs.severity < 0:
        raise ValueError(
            f"Severity must be non-negative, got {inputs.severity}"
        )
    if inputs.exposure < 0:
        raise ValueError(
            f"Exposure must be non-negative, got {inputs.exposure}"
        )

    return inputs.probability * inputs.severity * inputs.exposure


def calculate_residual_risk(initial_risk: float, control_efficiency: float) -> float:
    """Calculate residual risk after applying safety controls.

    Formula: Rr = Ri × (1 − ε)

    Args:
        initial_risk: Initial risk score (Ri), must be non-negative.
        control_efficiency: Control efficiency factor (ε), in range [0.0, 1.0].
            0.0 = no control applied; 1.0 = hazard fully eliminated.

    Returns:
        Residual risk score as a float.

    Raises:
        ValueError: If initial_risk is negative or control_efficiency is outside [0, 1].
    """
    if initial_risk < 0:
        raise ValueError(
            f"Initial risk must be non-negative, got {initial_risk}"
        )
    if not (0.0 <= control_efficiency <= 1.0):
        raise ValueError(
            f"Control efficiency must be between 0.0 and 1.0, got {control_efficiency}"
        )

    return initial_risk * (1.0 - control_efficiency)


def assess_risk(inputs: RiskInput) -> RiskOutput:
    """Perform a complete Fine-Kinney risk assessment.

    Calculates both initial risk (Ri = P × S × E) and residual risk
    (Rr = Ri × (1 − ε)), then classifies the residual risk level.

    Args:
        inputs: RiskInput dataclass with all required parameters.

    Returns:
        RiskOutput dataclass containing initial risk, residual risk,
        risk level classification, and formula references.

    Raises:
        ValueError: If any input parameter is invalid.

    Example:
        >>> from src.math_engine.schemas import RiskInput
        >>> inputs = RiskInput(probability=6, severity=15, exposure=3,
        ...                    control_efficiency=0.8)
        >>> result = assess_risk(inputs)
        >>> result.initial_risk
        270.0
        >>> result.residual_risk
        54.0
        >>> result.risk_level
        'medium'
    """
    initial_risk = calculate_initial_risk(inputs)
    residual_risk = calculate_residual_risk(initial_risk, inputs.control_efficiency)
    risk_level = _classify_risk(residual_risk)

    return RiskOutput(
        initial_risk=initial_risk,
        residual_risk=residual_risk,
        risk_level=risk_level,
    )
