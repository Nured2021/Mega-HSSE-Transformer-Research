"""Tests for open HSSE transformer training and benchmark scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.hsse_transformer.domain_map import HEAD_DOMAIN_MAP, all_head_names, head_name
from src.hsse_transformer.open_framework import (
    INSUFFICIENT_INFO_DECISION,
    apply_deterministic_gate,
    build_rule_context,
    ingest_dataset_layers,
    load_training_records,
    run_benchmark_evaluation,
    select_attention_heads,
    train_open_framework,
)


def _create_dataset_fixture(root: Path) -> Path:
    dataset_root = root / "dataset"
    for folder in [
        "01_KNOWLEDGE_LIBRARY",
        "02_TECHNICAL_LIBRARY",
        "03_GENERAL_KNOWLEDGE",
        "04_AI_DATA",
    ]:
        (dataset_root / folder).mkdir(parents=True, exist_ok=True)

    (dataset_root / "01_KNOWLEDGE_LIBRARY" / "iso45001.txt").write_text("ISO", encoding="utf-8")
    (dataset_root / "02_TECHNICAL_LIBRARY" / "sds.txt").write_text("SDS", encoding="utf-8")
    (dataset_root / "03_GENERAL_KNOWLEDGE" / "ih.txt").write_text("IH", encoding="utf-8")

    records = [
        {
            "scenario_id": "unsafe_oxygen_001",
            "scenario": "Confined space entry requested with oxygen at 18%.",
            "inputs": {"oxygen_percent": 18.0},
            "expected_decision": "ENTRY DENIED — Unsafe Atmospheric Condition",
            "evidence_sources": ["OSHA 1910.146"],
            "hsse_areas": [35],
            "uncertainty_required": False,
            "split": "benchmark",
            "suite": "unsafe_detection",
        },
        {
            "scenario_id": "no_guess_001",
            "scenario": "Unknown chemical compatibility without SDS.",
            "inputs": {"question": "mix chemicals"},
            "expected_decision": INSUFFICIENT_INFO_DECISION,
            "evidence_sources": ["SDS required"],
            "hsse_areas": [28],
            "uncertainty_required": True,
            "split": "benchmark",
            "suite": "no_guessing",
        },
        {
            "scenario_id": "domain_001",
            "scenario": "Silica dust exposure during concrete cutting.",
            "inputs": {"hazard": "silica dust"},
            "expected_decision": "Apply industrial hygiene controls",
            "evidence_sources": ["OSHA silica"],
            "hsse_areas": [41, 19],
            "multi_domain_link": True,
            "uncertainty_required": False,
            "split": "benchmark",
            "suite": "technical_selection",
        },
    ]

    (dataset_root / "04_AI_DATA" / "benchmark_cases.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    (dataset_root / "04_AI_DATA" / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_name": "test",
                "version": "1.0.0",
                "ai_data_records": ["benchmark_cases.json"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return dataset_root


class TestDomainMap:
    def test_has_60_heads(self):
        assert len(HEAD_DOMAIN_MAP) == 60
        assert all_head_names()[0] == "head_01"
        assert all_head_names()[-1] == "head_60"
        assert head_name(35) == "head_35"


class TestOpenFramework:
    def test_ingest_dataset_layers_counts_files(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        summary = ingest_dataset_layers(dataset_root)
        assert summary.knowledge_library_files == 1
        assert summary.technical_library_files == 1
        assert summary.general_knowledge_files == 1
        assert summary.ai_data_files == 2

    def test_load_training_records(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        records = load_training_records(dataset_root)
        assert len(records) == 3
        assert records[0].scenario_id == "unsafe_oxygen_001"

    def test_multi_domain_requires_link(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        bad_records = [
            {
                "scenario_id": "bad",
                "scenario": "multi domain without link",
                "inputs": {},
                "expected_decision": "x",
                "evidence_sources": ["y"],
                "hsse_areas": [40, 31],
                "uncertainty_required": False,
            }
        ]
        (dataset_root / "04_AI_DATA" / "bad.json").write_text(json.dumps(bad_records), encoding="utf-8")
        (dataset_root / "04_AI_DATA" / "manifest.json").write_text(
            json.dumps({"dataset_name": "test", "version": "1", "ai_data_records": ["bad.json"]}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="multi_domain_link"):
            load_training_records(dataset_root)

    def test_select_attention_heads_prefers_relevant_domain(self):
        heads = select_attention_heads("Confined space oxygen check", {"oxygen_percent": 18.0})
        assert 35 in heads

    def test_build_rule_context_from_twa(self):
        context = build_rule_context({"twa_value": 120.0, "twa_oel": 100.0})
        assert context["twa_ratio"] == pytest.approx(1.2)

    def test_apply_deterministic_gate_uncertainty(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        record = load_training_records(dataset_root)[1]
        decision = apply_deterministic_gate(record, fallback_decision="fallback")
        assert decision == INSUFFICIENT_INFO_DECISION

    def test_apply_deterministic_gate_rule_violation(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        record = load_training_records(dataset_root)[0]
        decision = apply_deterministic_gate(record, fallback_decision="fallback")
        assert "ENTRY DENIED" in decision

    def test_train_open_framework_generates_artifact(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        output = tmp_path / "artifacts" / "open_model.json"
        artifact = train_open_framework(dataset_root, output)
        assert artifact["record_count"] == 3
        assert output.exists()
        assert "head_35" in artifact["head_usage"]

    def test_benchmark_evaluation_generates_report(self, tmp_path: Path):
        dataset_root = _create_dataset_fixture(tmp_path)
        output = tmp_path / "artifacts" / "benchmark_report.json"
        report = run_benchmark_evaluation(dataset_root, output)
        assert report["total_cases"] == 3
        assert "suite_scores" in report
        assert "validation_requirements" in report
        assert report["validation_requirements"]["hazard_detection_verified"] is True
        assert report["validation_requirements"]["uncertainty_handled_safely"] is True
        assert report["validation_requirements"]["expert_comparison_completed"] is False
        assert report["deployment_ready"] is False
        assert "information_capacity_tracking" in report
        assert output.exists()
