"""
Tests for src/math_engine/incident.py

Validates failure probability: Pf = 1 − Π(1 − Pj)
"""

import pytest

from src.math_engine.schemas import IncidentInput
from src.math_engine.incident import calculate_failure_probability


class TestCalculateFailureProbability:
    def test_single_event(self):
        # Pf = 1 − (1 − 0.1) = 0.1
        inputs = IncidentInput(probabilities=[0.1], threshold=0.2)
        result = calculate_failure_probability(inputs)
        assert result.combined_probability == pytest.approx(0.1)
        assert result.status == "ACCEPTABLE"
        assert not result.capa_required

    def test_three_events_reference_scenario(self):
        # Pf = 1 − (0.9 × 0.95 × 0.98)
        # = 1 − 0.8379 = 0.1621 (approx)
        inputs = IncidentInput(probabilities=[0.1, 0.05, 0.02], threshold=0.1)
        result = calculate_failure_probability(inputs)
        assert result.combined_probability == pytest.approx(0.1621, rel=1e-3)
        assert result.status == "EXCEEDS_THRESHOLD"
        assert result.capa_required is True

    def test_zero_probabilities(self):
        # All components perfectly reliable → Pf = 0
        inputs = IncidentInput(probabilities=[0.0, 0.0, 0.0], threshold=0.05)
        result = calculate_failure_probability(inputs)
        assert result.combined_probability == pytest.approx(0.0)
        assert result.status == "ACCEPTABLE"

    def test_certain_failure(self):
        # One component guaranteed to fail → Pf = 1.0
        inputs = IncidentInput(probabilities=[1.0], threshold=0.5)
        result = calculate_failure_probability(inputs)
        assert result.combined_probability == pytest.approx(1.0)
        assert result.status == "EXCEEDS_THRESHOLD"
        assert result.capa_required is True

    def test_exactly_at_threshold_is_acceptable(self):
        # Pf exactly equal to threshold → ACCEPTABLE (not EXCEEDS)
        inputs = IncidentInput(probabilities=[0.1], threshold=0.1)
        result = calculate_failure_probability(inputs)
        assert result.combined_probability == pytest.approx(0.1)
        assert result.status == "ACCEPTABLE"
        assert not result.capa_required

    def test_threshold_stored_in_output(self):
        inputs = IncidentInput(probabilities=[0.05], threshold=0.15)
        result = calculate_failure_probability(inputs)
        assert result.threshold == 0.15

    def test_formula_reference_present(self):
        inputs = IncidentInput(probabilities=[0.05], threshold=0.1)
        result = calculate_failure_probability(inputs)
        assert "Pf" in result.formula

    def test_empty_probabilities_raises(self):
        inputs = IncidentInput(probabilities=[], threshold=0.1)
        with pytest.raises(ValueError, match="must not be empty"):
            calculate_failure_probability(inputs)

    def test_probability_above_one_raises(self):
        inputs = IncidentInput(probabilities=[1.1], threshold=0.1)
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            calculate_failure_probability(inputs)

    def test_negative_probability_raises(self):
        inputs = IncidentInput(probabilities=[-0.05], threshold=0.1)
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            calculate_failure_probability(inputs)

    def test_invalid_threshold_raises(self):
        inputs = IncidentInput(probabilities=[0.1], threshold=1.5)
        with pytest.raises(ValueError, match="Threshold must be between"):
            calculate_failure_probability(inputs)
