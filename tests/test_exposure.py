"""
Tests for src/math_engine/exposure.py

Validates Time-Weighted Average calculation: TWA = Σ(Ci × Ti) / 8
"""

import pytest

from src.math_engine.schemas import ExposureInput
from src.math_engine.exposure import calculate_twa


class TestCalculateTWA:
    def test_equal_split_exposure(self):
        # 50 ppm × 4 h + 30 ppm × 4 h = 320 / 8 = 40 ppm
        inputs = ExposureInput(concentrations=[50.0, 30.0], durations=[4.0, 4.0])
        result = calculate_twa(inputs)
        assert result.twa_value == pytest.approx(40.0)
        assert result.total_hours == pytest.approx(8.0)

    def test_single_full_shift(self):
        # 100 ppm × 8 h = 800 / 8 = 100 ppm
        inputs = ExposureInput(concentrations=[100.0], durations=[8.0])
        result = calculate_twa(inputs)
        assert result.twa_value == pytest.approx(100.0)
        assert result.total_hours == pytest.approx(8.0)

    def test_partial_exposure(self):
        # 200 ppm × 2 h = 400 / 8 = 50 ppm
        inputs = ExposureInput(concentrations=[200.0], durations=[2.0])
        result = calculate_twa(inputs)
        assert result.twa_value == pytest.approx(50.0)
        assert result.total_hours == pytest.approx(2.0)

    def test_zero_concentration(self):
        # 0 ppm × 4 h + 80 ppm × 4 h = 320 / 8 = 40 ppm
        inputs = ExposureInput(concentrations=[0.0, 80.0], durations=[4.0, 4.0])
        result = calculate_twa(inputs)
        assert result.twa_value == pytest.approx(40.0)

    def test_multiple_periods(self):
        # 100 ppm × 2h + 50 ppm × 3h + 10 ppm × 2h = 370 / 8 = 46.25
        inputs = ExposureInput(
            concentrations=[100.0, 50.0, 10.0],
            durations=[2.0, 3.0, 2.0],
        )
        result = calculate_twa(inputs)
        assert result.twa_value == pytest.approx(46.25)
        assert result.total_hours == pytest.approx(7.0)

    def test_formula_reference_present(self):
        inputs = ExposureInput(concentrations=[10.0], durations=[8.0])
        result = calculate_twa(inputs)
        assert "TWA" in result.formula

    def test_empty_concentrations_raises(self):
        inputs = ExposureInput(concentrations=[], durations=[])
        with pytest.raises(ValueError, match="must not be empty"):
            calculate_twa(inputs)

    def test_mismatched_lengths_raises(self):
        inputs = ExposureInput(concentrations=[10.0, 20.0], durations=[4.0])
        with pytest.raises(ValueError, match="same length"):
            calculate_twa(inputs)

    def test_negative_concentration_raises(self):
        inputs = ExposureInput(concentrations=[-5.0], durations=[4.0])
        with pytest.raises(ValueError, match="non-negative"):
            calculate_twa(inputs)

    def test_negative_duration_raises(self):
        inputs = ExposureInput(concentrations=[50.0], durations=[-2.0])
        with pytest.raises(ValueError, match="non-negative"):
            calculate_twa(inputs)

    def test_total_duration_over_24_raises(self):
        inputs = ExposureInput(concentrations=[10.0] * 3, durations=[10.0, 10.0, 10.0])
        with pytest.raises(ValueError, match="24 hours"):
            calculate_twa(inputs)
