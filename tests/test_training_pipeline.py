"""
Tests for src/hsse_transformer/training_pipeline.py

Validates Phase 3 training data pipeline: split assignment, JSONL output,
error handling, and CLI integration.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.hsse_transformer.training_pipeline import (
    SPLIT_TEST,
    SPLIT_TRAIN,
    SPLIT_VALIDATION,
    _assign_splits,
    _record_to_dict,
    _write_jsonl,
    build_training_splits,
)
from src.hsse_transformer.open_framework import (
    INSUFFICIENT_INFO_DECISION,
    TrainingRecord,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_record(
    scenario_id: str,
    split: str = "train",
    hsse_areas: list[int] | None = None,
    uncertainty_required: bool = False,
) -> TrainingRecord:
    """Create a minimal valid TrainingRecord for testing."""
    return TrainingRecord(
        scenario_id=scenario_id,
        scenario=f"Test scenario for {scenario_id}",
        inputs={"oxygen_percent": 21.0},
        expected_decision="Safe to proceed",
        evidence_sources=["Test reference"],
        hsse_areas=hsse_areas or [5],
        uncertainty_required=uncertainty_required,
        split=split,
        suite="general",
    )


def _create_full_dataset(root: Path) -> Path:
    """Create a complete dataset fixture covering all 4 layers."""
    dataset_root = root / "dataset"
    for folder in [
        "01_KNOWLEDGE_LIBRARY",
        "02_TECHNICAL_LIBRARY",
        "03_GENERAL_KNOWLEDGE",
        "04_AI_DATA",
    ]:
        (dataset_root / folder).mkdir(parents=True, exist_ok=True)

    # Populate source layers with stub files
    (dataset_root / "01_KNOWLEDGE_LIBRARY" / "regulations.json").write_text(
        '{"type": "regulation"}', encoding="utf-8"
    )
    (dataset_root / "02_TECHNICAL_LIBRARY" / "engineering.json").write_text(
        '{"type": "engineering"}', encoding="utf-8"
    )
    (dataset_root / "03_GENERAL_KNOWLEDGE" / "safety_basics.json").write_text(
        '{"type": "general"}', encoding="utf-8"
    )

    # Training records with pre-assigned splits
    train_records = [
        {
            "scenario_id": "train_001",
            "scenario": "Fire in process area.",
            "inputs": {"gas_lel_percent": 12.0},
            "expected_decision": "STOP WORK AUTHORITY — Lower Explosive Limit Threshold Exceeded",
            "evidence_sources": ["OSHA 1910.119"],
            "hsse_areas": [25],
            "uncertainty_required": False,
            "split": "train",
            "suite": "unsafe_detection",
        },
        {
            "scenario_id": "train_002",
            "scenario": "Confined space entry check.",
            "inputs": {"oxygen_percent": 16.0},
            "expected_decision": "ENTRY DENIED — Unsafe Atmospheric Condition",
            "evidence_sources": ["OSHA 1910.146"],
            "hsse_areas": [35],
            "uncertainty_required": False,
            "split": "train",
            "suite": "unsafe_detection",
        },
    ]
    validation_records = [
        {
            "scenario_id": "val_001",
            "scenario": "High risk score validation.",
            "inputs": {"risk_score": 450.0},
            "expected_decision": "STOP WORK — Extreme Risk Level Detected",
            "evidence_sources": ["Fine-Kinney Risk Assessment"],
            "hsse_areas": [5],
            "uncertainty_required": False,
            "split": "validation",
            "suite": "expert_comparison",
            "expert_decision": "STOP WORK — Extreme Risk Level Detected",
        },
    ]
    test_records = [
        {
            "scenario_id": "test_001",
            "scenario": "Unknown chemical test.",
            "inputs": {"question": "chemical compatibility"},
            "expected_decision": INSUFFICIENT_INFO_DECISION,
            "evidence_sources": ["SDS required"],
            "hsse_areas": [28],
            "uncertainty_required": True,
            "split": "test",
            "suite": "no_guessing",
        },
        {
            "scenario_id": "benchmark_001",
            "scenario": "Lifting with insufficient SF.",
            "inputs": {"safety_factor": 3.0},
            "expected_decision": "STOP WORK AUTHORITY — Insufficient Safety Factor",
            "evidence_sources": ["ASME B30.9"],
            "hsse_areas": [37],
            "uncertainty_required": False,
            "split": "benchmark",
            "suite": "unsafe_detection",
        },
    ]

    (dataset_root / "04_AI_DATA" / "train_data.json").write_text(
        json.dumps(train_records, indent=2), encoding="utf-8"
    )
    (dataset_root / "04_AI_DATA" / "val_data.json").write_text(
        json.dumps(validation_records, indent=2), encoding="utf-8"
    )
    (dataset_root / "04_AI_DATA" / "test_data.json").write_text(
        json.dumps(test_records, indent=2), encoding="utf-8"
    )
    (dataset_root / "04_AI_DATA" / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_name": "test",
                "version": "1.0.0",
                "ai_data_records": ["train_data.json", "val_data.json", "test_data.json"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return dataset_root


# ---------------------------------------------------------------------------
# Tests: _record_to_dict
# ---------------------------------------------------------------------------


class TestRecordToDict:
    def test_benchmark_split_normalised_to_test(self):
        record = _make_record("r1", split="benchmark")
        d = _record_to_dict(record)
        assert d["split"] == SPLIT_TEST

    def test_train_split_preserved(self):
        record = _make_record("r2", split="train")
        d = _record_to_dict(record)
        assert d["split"] == SPLIT_TRAIN

    def test_validation_split_preserved(self):
        record = _make_record("r3", split="validation")
        d = _record_to_dict(record)
        assert d["split"] == SPLIT_VALIDATION

    def test_all_required_fields_present(self):
        record = _make_record("r4", split="train")
        d = _record_to_dict(record)
        for field in [
            "scenario_id", "scenario", "inputs", "expected_decision",
            "evidence_sources", "hsse_areas", "uncertainty_required", "split",
        ]:
            assert field in d


# ---------------------------------------------------------------------------
# Tests: _assign_splits
# ---------------------------------------------------------------------------


class TestAssignSplits:
    def test_pre_assigned_train_routes_to_train(self):
        records = [_make_record("r1", split="train")]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(t) == 1
        assert len(v) == 0
        assert len(te) == 0

    def test_pre_assigned_validation_routes_correctly(self):
        records = [_make_record("r1", split="validation")]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(v) == 1
        assert len(t) == 0

    def test_benchmark_routes_to_test(self):
        records = [_make_record("r1", split="benchmark")]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(te) == 1
        assert len(t) == 0

    def test_test_split_routes_to_test(self):
        records = [_make_record("r1", split="test")]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(te) == 1

    def test_mixed_pre_assigned(self):
        records = [
            _make_record("r1", split="train"),
            _make_record("r2", split="validation"),
            _make_record("r3", split="test"),
            _make_record("r4", split="benchmark"),
        ]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(t) == 1
        assert len(v) == 1
        assert len(te) == 2

    def test_unassigned_single_record_goes_to_train(self):
        records = [_make_record("r1", split="general")]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(t) == 1
        assert len(v) == 0
        assert len(te) == 0

    def test_unassigned_two_records_split_train_val(self):
        records = [_make_record(f"r{i}", split="general") for i in range(2)]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(t) == 1
        assert len(v) == 1
        assert len(te) == 0

    def test_unassigned_ten_records_correct_proportions(self):
        records = [_make_record(f"r{i}", split="general") for i in range(10)]
        t, v, te = _assign_splits(records, 0.7, 0.15, 42)
        assert len(t) + len(v) + len(te) == 10
        assert len(t) >= 6
        assert len(v) >= 1
        assert len(te) >= 1

    def test_deterministic_with_same_seed(self):
        records = [_make_record(f"r{i}", split="general") for i in range(20)]
        t1, v1, te1 = _assign_splits(records, 0.7, 0.15, 42)
        t2, v2, te2 = _assign_splits(records, 0.7, 0.15, 42)
        assert [r.scenario_id for r in t1] == [r.scenario_id for r in t2]
        assert [r.scenario_id for r in v1] == [r.scenario_id for r in v2]

    def test_different_seeds_may_differ(self):
        records = [_make_record(f"r{i}", split="general") for i in range(20)]
        t1, _, _ = _assign_splits(records, 0.7, 0.15, 42)
        t2, _, _ = _assign_splits(records, 0.7, 0.15, 99)
        # Different seeds should yield different orderings (extremely unlikely to match)
        ids1 = [r.scenario_id for r in t1]
        ids2 = [r.scenario_id for r in t2]
        assert ids1 != ids2


# ---------------------------------------------------------------------------
# Tests: _write_jsonl
# ---------------------------------------------------------------------------


class TestWriteJsonl:
    def test_creates_file(self, tmp_path):
        records = [_make_record("r1", split="train")]
        path = tmp_path / "output.jsonl"
        _write_jsonl(records, path)
        assert path.exists()

    def test_creates_parent_dirs(self, tmp_path):
        records = [_make_record("r1")]
        path = tmp_path / "subdir" / "nested" / "out.jsonl"
        _write_jsonl(records, path)
        assert path.exists()

    def test_one_line_per_record(self, tmp_path):
        records = [_make_record(f"r{i}") for i in range(5)]
        path = tmp_path / "out.jsonl"
        _write_jsonl(records, path)
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 5

    def test_each_line_is_valid_json(self, tmp_path):
        records = [_make_record(f"r{i}") for i in range(3)]
        path = tmp_path / "out.jsonl"
        _write_jsonl(records, path)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line)
                assert isinstance(obj, dict)

    def test_benchmark_normalised_in_output(self, tmp_path):
        records = [_make_record("r1", split="benchmark")]
        path = tmp_path / "out.jsonl"
        _write_jsonl(records, path)
        obj = json.loads(path.read_text(encoding="utf-8").strip())
        assert obj["split"] == SPLIT_TEST

    def test_empty_list_produces_empty_file(self, tmp_path):
        path = tmp_path / "empty.jsonl"
        _write_jsonl([], path)
        assert path.exists()
        assert path.read_text(encoding="utf-8").strip() == ""


# ---------------------------------------------------------------------------
# Tests: build_training_splits
# ---------------------------------------------------------------------------


class TestBuildTrainingSplits:
    def test_returns_summary_dict(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        result = build_training_splits(dataset_root, output_dir=tmp_path / "out")
        assert isinstance(result, dict)
        assert "total_records" in result
        assert "splits" in result
        assert "output_files" in result

    def test_output_files_created(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        out_dir = tmp_path / "out"
        build_training_splits(dataset_root, output_dir=out_dir)
        assert (out_dir / "train.jsonl").exists()
        assert (out_dir / "validation.jsonl").exists()
        assert (out_dir / "test.jsonl").exists()

    def test_split_counts_sum_to_total(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        result = build_training_splits(dataset_root, output_dir=tmp_path / "out")
        splits = result["splits"]
        assert splits["train"] + splits["validation"] + splits["test"] == result["total_records"]

    def test_pre_assigned_records_routed_correctly(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        out_dir = tmp_path / "out"
        result = build_training_splits(dataset_root, output_dir=out_dir)
        # 2 pre-assigned train + 1 pre-assigned validation + 2 pre-assigned test(benchmark)
        assert result["splits"]["train"] == 2
        assert result["splits"]["validation"] == 1
        assert result["splits"]["test"] == 2

    def test_default_output_dir_is_training_subdir(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        result = build_training_splits(dataset_root)
        expected_dir = dataset_root / "04_AI_DATA" / "training"
        assert result["output_files"]["train"] == str(expected_dir / "train.jsonl")

    def test_jsonl_content_is_valid(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        out_dir = tmp_path / "out"
        build_training_splits(dataset_root, output_dir=out_dir)
        for fname in ["train.jsonl", "validation.jsonl", "test.jsonl"]:
            content = (out_dir / fname).read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.strip():
                    obj = json.loads(line)
                    assert "scenario_id" in obj
                    assert "hsse_areas" in obj

    def test_invalid_train_ratio_raises(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        with pytest.raises(ValueError, match="train_ratio"):
            build_training_splits(dataset_root, train_ratio=1.1)

    def test_invalid_validation_ratio_raises(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        with pytest.raises(ValueError, match="validation_ratio"):
            build_training_splits(dataset_root, validation_ratio=0.0)

    def test_ratio_sum_too_large_raises(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        with pytest.raises(ValueError, match="train_ratio.*validation_ratio"):
            build_training_splits(dataset_root, train_ratio=0.8, validation_ratio=0.3)

    def test_missing_dataset_root_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build_training_splits(tmp_path / "nonexistent_dataset")

    def test_ingestion_summary_included(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        result = build_training_splits(dataset_root, output_dir=tmp_path / "out")
        ingestion = result["ingestion_summary"]
        assert "knowledge_library_files" in ingestion
        assert "technical_library_files" in ingestion
        assert "ai_data_files" in ingestion
        assert ingestion["knowledge_library_files"] >= 1
        assert ingestion["technical_library_files"] >= 1
        assert ingestion["general_knowledge_files"] >= 1

    def test_pipeline_name_in_result(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        result = build_training_splits(dataset_root, output_dir=tmp_path / "out")
        assert result["pipeline"] == "mega_hsse_training_pipeline_v1"

    def test_reproducible_with_same_seed(self, tmp_path):
        dataset_root = _create_full_dataset(tmp_path)
        out1 = tmp_path / "out1"
        out2 = tmp_path / "out2"
        build_training_splits(dataset_root, output_dir=out1, seed=42)
        build_training_splits(dataset_root, output_dir=out2, seed=42)
        assert (out1 / "train.jsonl").read_text() == (out2 / "train.jsonl").read_text()
        assert (out1 / "validation.jsonl").read_text() == (out2 / "validation.jsonl").read_text()


# ---------------------------------------------------------------------------
# Tests: CLI pipeline subcommand
# ---------------------------------------------------------------------------


class TestCLIPipeline:
    def test_pipeline_subcommand_runs(self, tmp_path):
        from src.math_engine.cli import main

        dataset_root = _create_full_dataset(tmp_path)
        out_dir = tmp_path / "cli_out"
        main([
            "pipeline",
            "--dataset-root", str(dataset_root),
            "--output-dir", str(out_dir),
        ])
        assert (out_dir / "train.jsonl").exists()
        assert (out_dir / "validation.jsonl").exists()
        assert (out_dir / "test.jsonl").exists()

    def test_pipeline_with_custom_ratios(self, tmp_path):
        from src.math_engine.cli import main

        dataset_root = _create_full_dataset(tmp_path)
        out_dir = tmp_path / "cli_out2"
        main([
            "pipeline",
            "--dataset-root", str(dataset_root),
            "--output-dir", str(out_dir),
            "--train-ratio", "0.60",
            "--validation-ratio", "0.20",
            "--seed", "7",
        ])
        assert (out_dir / "train.jsonl").exists()

    def test_pipeline_invalid_ratios_exits(self, tmp_path, capsys):
        from src.math_engine.cli import main

        dataset_root = _create_full_dataset(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            main([
                "pipeline",
                "--dataset-root", str(dataset_root),
                "--train-ratio", "0.9",
                "--validation-ratio", "0.9",
            ])
        assert exc_info.value.code == 1
