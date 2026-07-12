"""
Tests for src/math_engine/lifting.py

Validates lifting safety factor: SF = Breaking_Strength / (Applied_Load × Dynamic_Factor)
"""

import pytest

from src.math_engine.schemas import LiftingInput
from src.math_engine.lifting import calculate_safety_factor


class TestCalculateSafetyFactor:
    def test_mega_hsse_reference_scenario(self):
        # Reference scenario from Mega HSSE Transformer concept:
        # SF = 250 / (50 × 1.5) = 250 / 75 = 3.333...
        inputs = LiftingInput(
            breaking_strength=250,
            applied_load=50,
            dynamic_factor=1.5,
            minimum_sf=5.0,
        )
        result = calculate_safety_factor(inputs)
        assert result.safety_factor == pytest.approx(3.333, rel=1e-3)
        assert result.status == "FAIL"
        assert result.minimum_required == 5.0
        assert "STOP WORK" in result.decision

    def test_passing_safety_factor(self):
        # SF = 500 / (50 × 1.5) = 6.667 > 5.0 → PASS
        inputs = LiftingInput(
            breaking_strength=500,
            applied_load=50,
            dynamic_factor=1.5,
            minimum_sf=5.0,
        )
        result = calculate_safety_factor(inputs)
        assert result.safety_factor == pytest.approx(6.667, rel=1e-3)
        assert result.status == "PASS"
        assert "proceed" in result.decision.lower()

    def test_exact_minimum_sf_passes(self):
        # SF exactly equal to minimum should PASS
        # 375 / (50 × 1.5) = 375 / 75 = 5.0 → PASS
        inputs = LiftingInput(
            breaking_strength=375,
            applied_load=50,
            dynamic_factor=1.5,
            minimum_sf=5.0,
        )
        result = calculate_safety_factor(inputs)
        assert result.safety_factor == pytest.approx(5.0)
        assert result.status == "PASS"

    def test_standard_lift_lower_threshold(self):
        # Standard industrial lift: minimum SF = 3.0
        # SF = 150 / (50 × 1.0) = 3.0 → PASS
        inputs = LiftingInput(
            breaking_strength=150,
            applied_load=50,
            dynamic_factor=1.0,
            minimum_sf=3.0,
        )
        result = calculate_safety_factor(inputs)
        assert result.safety_factor == pytest.approx(3.0)
        assert result.status == "PASS"

    def test_formula_reference_present(self):
        inputs = LiftingInput(
            breaking_strength=250, applied_load=50, dynamic_factor=1.5
        )
        result = calculate_safety_factor(inputs)
        assert "SF" in result.formula

    def test_zero_breaking_strength_raises(self):
        inputs = LiftingInput(
            breaking_strength=0, applied_load=50, dynamic_factor=1.5
        )
        with pytest.raises(ValueError, match="Breaking strength must be positive"):
            calculate_safety_factor(inputs)

    def test_negative_applied_load_raises(self):
        inputs = LiftingInput(
            breaking_strength=250, applied_load=-50, dynamic_factor=1.5
        )
        with pytest.raises(ValueError, match="Applied load must be positive"):
            calculate_safety_factor(inputs)

    def test_zero_dynamic_factor_raises(self):
        inputs = LiftingInput(
            breaking_strength=250, applied_load=50, dynamic_factor=0
        )
        with pytest.raises(ValueError, match="Dynamic factor must be positive"):
            calculate_safety_factor(inputs)

    def test_negative_minimum_sf_raises(self):
        inputs = LiftingInput(
            breaking_strength=250, applied_load=50, dynamic_factor=1.5, minimum_sf=-1.0
        )
        with pytest.raises(ValueError, match="Minimum safety factor must be positive"):
            calculate_safety_factor(inputs)
