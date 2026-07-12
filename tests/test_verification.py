"""
Tests for src/verification/rules.py and src/verification/engine.py

Validates deterministic safety rule enforcement.
"""

import pytest

from src.verification.rules import RULES, RULES_BY_ID, SafetyRule, RuleResult
from src.verification.engine import apply_rules, check_rule, any_violated


class TestRuleRegistry:
    def test_rules_list_not_empty(self):
        assert len(RULES) > 0

    def test_oxygen_rule_exists(self):
        assert "oxygen_threshold" in RULES_BY_ID

    def test_lifting_rule_exists(self):
        assert "lifting_sf_critical" in RULES_BY_ID

    def test_twa_rule_exists(self):
        assert "twa_exceedance" in RULES_BY_ID

    def test_extreme_risk_rule_exists(self):
        assert "extreme_risk" in RULES_BY_ID

    def test_lel_rule_exists(self):
        assert "lel_threshold" in RULES_BY_ID

    def test_unprotected_energized_rule_exists(self):
        assert "unprotected_energized_work" in RULES_BY_ID

    def test_noise_dose_rule_exists(self):
        assert "noise_dose_exceedance" in RULES_BY_ID

    def test_all_rules_have_required_fields(self):
        for rule in RULES:
            assert rule.rule_id, f"Rule missing rule_id: {rule}"
            assert rule.context_key, f"Rule '{rule.rule_id}' missing context_key"
            assert rule.decision, f"Rule '{rule.rule_id}' missing decision"
            assert rule.standard, f"Rule '{rule.rule_id}' missing standard"


class TestCheckRule:
    def test_oxygen_below_threshold_violated(self):
        rule = RULES_BY_ID["oxygen_threshold"]
        result = check_rule(rule, {"oxygen_percent": 18.0})
        assert result is not None
        assert result.violated is True
        assert "ENTRY DENIED" in result.decision
        assert result.context_value == 18.0
        assert result.threshold == 19.5

    def test_oxygen_above_threshold_not_violated(self):
        rule = RULES_BY_ID["oxygen_threshold"]
        result = check_rule(rule, {"oxygen_percent": 20.9})
        assert result is not None
        assert result.violated is False
        assert result.decision is None

    def test_oxygen_exactly_at_threshold_not_violated(self):
        # 19.5% is exactly at threshold — lt operator means <19.5 is violated
        rule = RULES_BY_ID["oxygen_threshold"]
        result = check_rule(rule, {"oxygen_percent": 19.5})
        assert result is not None
        assert result.violated is False

    def test_missing_context_key_returns_none(self):
        rule = RULES_BY_ID["oxygen_threshold"]
        result = check_rule(rule, {"safety_factor": 3.3})
        assert result is None

    def test_lifting_sf_fail(self):
        rule = RULES_BY_ID["lifting_sf_critical"]
        result = check_rule(rule, {"safety_factor": 3.33})
        assert result is not None
        assert result.violated is True
        assert "STOP WORK" in result.decision

    def test_lifting_sf_pass(self):
        rule = RULES_BY_ID["lifting_sf_critical"]
        result = check_rule(rule, {"safety_factor": 6.0})
        assert result is not None
        assert result.violated is False

    def test_extreme_risk_triggered(self):
        rule = RULES_BY_ID["extreme_risk"]
        result = check_rule(rule, {"risk_score": 400.0})
        assert result is not None
        assert result.violated is True

    def test_extreme_risk_not_triggered(self):
        rule = RULES_BY_ID["extreme_risk"]
        result = check_rule(rule, {"risk_score": 399.9})
        assert result is not None
        assert result.violated is False

    def test_invalid_operator_raises(self):
        bad_rule = SafetyRule(
            rule_id="bad_rule",
            context_key="some_value",
            threshold=10.0,
            operator="invalid_op",
            decision="FAIL",
            reason="test",
            standard="test",
        )
        with pytest.raises(ValueError, match="Unsupported operator"):
            check_rule(bad_rule, {"some_value": 5.0})

    def test_lel_at_threshold_violated(self):
        rule = RULES_BY_ID["lel_threshold"]
        result = check_rule(rule, {"gas_lel_percent": 10.0})
        assert result is not None
        assert result.violated is True
        assert "STOP WORK" in result.decision
        assert result.threshold == 10.0

    def test_lel_below_threshold_not_violated(self):
        rule = RULES_BY_ID["lel_threshold"]
        result = check_rule(rule, {"gas_lel_percent": 9.9})
        assert result is not None
        assert result.violated is False
        assert result.decision is None

    def test_unprotected_voltage_above_zero_violated(self):
        rule = RULES_BY_ID["unprotected_energized_work"]
        result = check_rule(rule, {"unprotected_voltage_kv": 0.4})
        assert result is not None
        assert result.violated is True
        assert "LOTO" in result.decision

    def test_unprotected_voltage_zero_not_violated(self):
        rule = RULES_BY_ID["unprotected_energized_work"]
        result = check_rule(rule, {"unprotected_voltage_kv": 0.0})
        assert result is not None
        assert result.violated is False

    def test_noise_dose_at_pel_violated(self):
        rule = RULES_BY_ID["noise_dose_exceedance"]
        result = check_rule(rule, {"noise_dose_percent": 100.0})
        assert result is not None
        assert result.violated is True
        assert "CORRECTIVE ACTION" in result.decision

    def test_noise_dose_below_pel_not_violated(self):
        rule = RULES_BY_ID["noise_dose_exceedance"]
        result = check_rule(rule, {"noise_dose_percent": 99.9})
        assert result is not None
        assert result.violated is False


class TestApplyRules:
    def test_oxygen_violation_detected(self):
        results = apply_rules({"oxygen_percent": 15.0})
        assert len(results) == 1
        assert results[0]["rule_id"] == "oxygen_threshold"
        assert results[0]["violated"] is True

    def test_safe_oxygen_no_violation(self):
        results = apply_rules({"oxygen_percent": 21.0})
        assert len(results) == 1
        assert results[0]["violated"] is False

    def test_multiple_violations(self):
        results = apply_rules({
            "oxygen_percent": 17.0,
            "safety_factor": 2.0,
        })
        assert len(results) == 2
        violated = [r for r in results if r["violated"]]
        assert len(violated) == 2

    def test_empty_context_returns_empty(self):
        results = apply_rules({})
        assert results == []

    def test_result_structure(self):
        results = apply_rules({"oxygen_percent": 18.0})
        r = results[0]
        assert "rule_id" in r
        assert "violated" in r
        assert "decision" in r
        assert "reason" in r
        assert "context_key" in r
        assert "context_value" in r
        assert "threshold" in r
        assert "standard" in r


class TestAnyViolated:
    def test_violated_when_oxygen_low(self):
        assert any_violated({"oxygen_percent": 10.0}) is True

    def test_not_violated_when_oxygen_safe(self):
        assert any_violated({"oxygen_percent": 21.0}) is False

    def test_not_violated_when_context_empty(self):
        assert any_violated({}) is False

    def test_violated_when_lifting_sf_low(self):
        assert any_violated({"safety_factor": 1.5}) is True

    def test_twa_exceedance_violation(self):
        # twa_ratio >= 1.0 triggers violation
        assert any_violated({"twa_ratio": 1.0}) is True

    def test_twa_below_oel_no_violation(self):
        assert any_violated({"twa_ratio": 0.8}) is False

    def test_lel_violation_detected(self):
        assert any_violated({"gas_lel_percent": 15.0}) is True

    def test_lel_below_threshold_no_violation(self):
        assert any_violated({"gas_lel_percent": 5.0}) is False

    def test_noise_dose_violation(self):
        assert any_violated({"noise_dose_percent": 110.0}) is True

    def test_energized_work_violation(self):
        assert any_violated({"unprotected_voltage_kv": 11.0}) is True
