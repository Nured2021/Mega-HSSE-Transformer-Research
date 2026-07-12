"""
Mega HSSE Transformer — Input/Output Schema Definitions

All calculation functions in the math engine use these typed dataclasses
for explicit, self-documenting input/output structures.

Research Status: Foundation Built — Validation Pending
"""

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Risk (Fine-Kinney)
# ---------------------------------------------------------------------------


@dataclass
class RiskInput:
    """Input parameters for Fine-Kinney risk calculation.

    Formula: Ri = P × S × E

    Attributes:
        probability: Likelihood of hazard occurrence (standard Fine-Kinney scale).
            Typical values: 0.1 (almost impossible) to 10 (certain).
        severity: Consequence severity (standard Fine-Kinney scale).
            Typical values: 1 (minor first aid) to 40 (catastrophic/multiple fatalities).
        exposure: Frequency of exposure to the hazard (standard Fine-Kinney scale).
            Typical values: 0.5 (rarely) to 10 (continuously).
        control_efficiency: Effectiveness of applied controls as a fraction (0.0–1.0).
            0.0 means no control, 1.0 means perfect elimination.
    """

    probability: float
    severity: float
    exposure: float
    control_efficiency: float = 0.0


@dataclass
class RiskOutput:
    """Output from Fine-Kinney risk calculation.

    Attributes:
        initial_risk: Computed initial risk score (Ri = P × S × E).
        residual_risk: Risk after applying controls (Rr = Ri × (1 − ε)).
        risk_level: Categorical classification of residual risk.
        formula_initial: Human-readable formula used for initial risk.
        formula_residual: Human-readable formula used for residual risk.
    """

    initial_risk: float
    residual_risk: float
    risk_level: str
    formula_initial: str = "Ri = P × S × E"
    formula_residual: str = "Rr = Ri × (1 − ε)"


# ---------------------------------------------------------------------------
# Exposure (TWA)
# ---------------------------------------------------------------------------


@dataclass
class ExposureInput:
    """Input parameters for Time-Weighted Average (TWA) calculation.

    Formula: TWA = Σ(Ci × Ti) / 8 hours

    Attributes:
        concentrations: List of hazard concentrations for each exposure period (Ci).
            Units depend on hazard type (e.g., ppm, mg/m³, dB).
        durations: List of exposure durations in hours for each period (Ti).
            Must have the same length as concentrations.
    """

    concentrations: List[float]
    durations: List[float]


@dataclass
class ExposureOutput:
    """Output from Time-Weighted Average calculation.

    Attributes:
        twa_value: Computed TWA value over an 8-hour reference period.
        total_hours: Sum of all exposure durations provided.
        formula: Human-readable formula used.
    """

    twa_value: float
    total_hours: float
    formula: str = "TWA = Σ(Ci × Ti) / 8"


# ---------------------------------------------------------------------------
# Lifting Safety Factor
# ---------------------------------------------------------------------------


@dataclass
class LiftingInput:
    """Input parameters for lifting safety factor calculation.

    Formula: SF = Breaking_Strength / (Applied_Load × Dynamic_Factor)

    Attributes:
        breaking_strength: Rated breaking/working load limit of the lifting equipment
            (same units as applied_load, e.g., tonnes, kN).
        applied_load: Actual weight of the load to be lifted.
        dynamic_factor: Amplification factor accounting for dynamic forces
            such as acceleration, wind, or shock loading. Must be > 0.
        minimum_sf: Minimum acceptable safety factor for the lift type.
            Default 5.0 is the standard for critical offshore lifts.
    """

    breaking_strength: float
    applied_load: float
    dynamic_factor: float
    minimum_sf: float = 5.0


@dataclass
class LiftingOutput:
    """Output from lifting safety factor calculation.

    Attributes:
        safety_factor: Computed safety factor (SF).
        status: "PASS" if SF ≥ minimum_sf, "FAIL" if SF < minimum_sf.
        minimum_required: The minimum SF threshold used in the assessment.
        decision: Human-readable decision string.
        formula: Human-readable formula used.
    """

    safety_factor: float
    status: str
    minimum_required: float
    decision: str
    formula: str = "SF = Breaking_Strength / (Applied_Load × Dynamic_Factor)"


# ---------------------------------------------------------------------------
# Incident / Failure Probability
# ---------------------------------------------------------------------------


@dataclass
class IncidentInput:
    """Input parameters for combined failure probability calculation.

    Formula: Pf = 1 − Π(1 − Pj), j = 1..n

    This models the probability that at least one of n independent failure
    modes occurs (Boolean OR gate / fault tree analysis).

    Attributes:
        probabilities: List of individual component/event failure probabilities (Pj).
            Each value must be in the range [0.0, 1.0].
        threshold: Maximum acceptable combined failure probability.
            If Pf exceeds this, CAPA (Corrective Action) is triggered.
    """

    probabilities: List[float]
    threshold: float = 0.1


@dataclass
class IncidentOutput:
    """Output from combined failure probability calculation.

    Attributes:
        combined_probability: Computed combined failure probability (Pf).
        status: "ACCEPTABLE" if Pf ≤ threshold, "EXCEEDS_THRESHOLD" otherwise.
        threshold: The threshold value used.
        capa_required: True if CAPA corrective action is triggered.
        formula: Human-readable formula used.
    """

    combined_probability: float
    status: str
    threshold: float
    capa_required: bool
    formula: str = "Pf = 1 − Π(1 − Pj)"
