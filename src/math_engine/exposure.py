"""
Mega HSSE Transformer — Occupational Exposure Module (TWA)

Implements the Time-Weighted Average (TWA) calculation for occupational
exposure assessment.

Formula reference:
    TWA = Σ(Ci × Ti) / 8 hours

    Where:
        Ci = Concentration of the hazard during exposure period i
        Ti = Duration of exposure period i (hours)
        8  = Reference workday in hours (standard NIOSH/OSHA 8-hour period)

The TWA normalizes exposure to an 8-hour reference period, enabling
comparison with Occupational Exposure Limits (OEL), Permissible Exposure
Limits (PEL), and Threshold Limit Values (TLV).

Reference:
    NIOSH Pocket Guide to Chemical Hazards (NPG), DHHS Publication No. 2005-149.
    OSHA 29 CFR 1910.1000 Air Contaminants.

Research Status: Foundation Built — Validation Pending
"""

from typing import List

from src.math_engine.schemas import ExposureInput, ExposureOutput

# Standard 8-hour reference workday (hours)
_REFERENCE_HOURS = 8.0


def calculate_twa(inputs: ExposureInput) -> ExposureOutput:
    """Calculate the Time-Weighted Average (TWA) occupational exposure.

    Formula: TWA = Σ(Ci × Ti) / 8

    The concentrations and durations lists must have the same length.
    Total exposure duration may be less than 8 hours (the remaining
    period is treated as zero exposure, which is standard OSHA practice).

    Args:
        inputs: ExposureInput dataclass with concentrations and durations lists.

    Returns:
        ExposureOutput dataclass with TWA value, total hours, and formula reference.

    Raises:
        ValueError: If inputs are empty, lists have different lengths,
                    any concentration is negative, any duration is negative,
                    or total duration exceeds 24 hours.

    Example:
        >>> from src.math_engine.schemas import ExposureInput
        >>> inputs = ExposureInput(concentrations=[50.0, 30.0], durations=[4.0, 4.0])
        >>> result = calculate_twa(inputs)
        >>> result.twa_value
        40.0
        >>> result.total_hours
        8.0
    """
    concentrations: List[float] = inputs.concentrations
    durations: List[float] = inputs.durations

    if not concentrations:
        raise ValueError("Concentrations list must not be empty.")
    if len(concentrations) != len(durations):
        raise ValueError(
            f"Concentrations and durations must have the same length. "
            f"Got {len(concentrations)} concentrations and {len(durations)} durations."
        )

    for i, c in enumerate(concentrations):
        if c < 0:
            raise ValueError(
                f"Concentration at index {i} must be non-negative, got {c}."
            )

    for i, t in enumerate(durations):
        if t < 0:
            raise ValueError(
                f"Duration at index {i} must be non-negative, got {t}."
            )

    total_hours = sum(durations)
    if total_hours > 24.0:
        raise ValueError(
            f"Total exposure duration cannot exceed 24 hours, got {total_hours}."
        )

    weighted_sum = sum(c * t for c, t in zip(concentrations, durations))
    twa_value = weighted_sum / _REFERENCE_HOURS

    return ExposureOutput(
        twa_value=twa_value,
        total_hours=total_hours,
    )
