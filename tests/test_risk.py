"""
Tests for src/math_engine/risk.py

Validates Fine-Kinney risk calculation: Ri = P × S × E
and residual risk: Rr = Ri × (1 − ε)
"""

import pytest

from src.math_engine.schemas import RiskInput
from src.math_engine.risk import (
    assess_risk,
    calculate_initial_risk,
    calculate_residual_risk,
    _classify_risk,
)


class TestCalculateInitialRisk:
    def test_low_risk_values(self):
        inputs = RiskInput(probability=1, severity=1, exposure=1)
        assert calculate_initial_risk(inputs) == 1.0

    def test_known_medium_scenario(self):
        # P=3, S=7, E=3 → Ri=63
        inputs = RiskInput(probability=3, severity=7, exposure=3)
        assert calculate_initial_risk(inputs) == 63.0

    def test_high_risk_scenario(self):
        # P=6, S=15, E=6 → Ri=540
        inputs = RiskInput(probability=6, severity=15, exposure=6)
        assert calculate_initial_risk(inputs) == 540.0

    def test_zero_probability(self):
        inputs = RiskInput(probability=0, severity=40, exposure=10)
        assert calculate_initial_risk(inputs) == 0.0

    def test_negative_probability_raises(self):
        inputs = RiskInput(probability=-1, severity=10, exposure=5)
        with pytest.raises(ValueError, match="Probability must be non-negative"):
            calculate_initial_risk(inputs)

    def test_negative_severity_raises(self):
        inputs = RiskInput(probability=1, severity=-5, exposure=5)
        with pytest.raises(ValueError, match="Severity must be non-negative"):
            calculate_initial_risk(inputs)

    def test_negative_exposure_raises(self):
        inputs = RiskInput(probability=1, severity=5, exposure=-1)
        with pytest.raises(ValueError, match="Exposure must be non-negative"):
            calculate_initial_risk(inputs)


class TestCalculateResidualRisk:
    def test_no_control(self):
        # ε=0.0 → Rr = Ri unchanged
        assert calculate_residual_risk(270.0, 0.0) == 270.0

    def test_full_control(self):
        # ε=1.0 → Rr = 0
        assert calculate_residual_risk(270.0, 1.0) == 0.0

    def test_partial_control(self):
        # ε=0.8 → Rr = 270 × 0.2 = 54.0
        assert calculate_residual_risk(270.0, 0.8) == pytest.approx(54.0)

    def test_negative_initial_risk_raises(self):
        with pytest.raises(ValueError, match="Initial risk must be non-negative"):
            calculate_residual_risk(-10.0, 0.5)

    def test_control_above_one_raises(self):
        with pytest.raises(ValueError, match="Control efficiency must be between"):
            calculate_residual_risk(100.0, 1.1)

    def test_control_below_zero_raises(self):
        with pytest.raises(ValueError, match="Control efficiency must be between"):
            calculate_residual_risk(100.0, -0.1)


class TestClassifyRisk:
    def test_low(self):
        assert _classify_risk(10.0) == "low"

    def test_medium(self):
        assert _classify_risk(50.0) == "medium"

    def test_high(self):
        assert _classify_risk(100.0) == "high"

    def test_very_high(self):
        assert _classify_risk(300.0) == "very_high"

    def test_extreme(self):
        assert _classify_risk(500.0) == "extreme"

    def test_boundary_low_medium(self):
        assert _classify_risk(19.9) == "low"
        assert _classify_risk(20.0) == "medium"

    def test_boundary_medium_high(self):
        assert _classify_risk(69.9) == "medium"
        assert _classify_risk(70.0) == "high"


class TestAssessRisk:
    def test_full_assessment_with_control(self):
        # P=6, S=15, E=3, ε=0.8 → Ri=270, Rr=54, level=medium
        inputs = RiskInput(probability=6, severity=15, exposure=3, control_efficiency=0.8)
        result = assess_risk(inputs)
        assert result.initial_risk == pytest.approx(270.0)
        assert result.residual_risk == pytest.approx(54.0)
        assert result.risk_level == "medium"

    def test_formula_references_present(self):
        inputs = RiskInput(probability=1, severity=1, exposure=1)
        result = assess_risk(inputs)
        assert "Ri" in result.formula_initial
        assert "Rr" in result.formula_residual

    def test_extreme_risk_no_control(self):
        # P=10, S=40, E=10 → Ri=4000, level=extreme
        inputs = RiskInput(probability=10, severity=40, exposure=10, control_efficiency=0.0)
        result = assess_risk(inputs)
        assert result.initial_risk == 4000.0
        assert result.risk_level == "extreme"

    def test_invalid_input_propagates(self):
        inputs = RiskInput(probability=-1, severity=10, exposure=3)
        with pytest.raises(ValueError):
            assess_risk(inputs)
