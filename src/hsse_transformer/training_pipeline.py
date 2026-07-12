"""
Mega HSSE Transformer — Training Data Pipeline

Phase 3: Dataset Population and Training Data Creation

Implements the deterministic pipeline for converting HSSE source records
across all four dataset layers into split JSONL files ready for model training.

Pipeline:
    HSSE Documents (01–04 layers)
        → Load all records via manifest
        → Validate each record against open_training_schema contract
        → Assign train / validation / test splits
        → Write train.jsonl, validation.jsonl, test.jsonl

Output directory:  <dataset_root>/04_AI_DATA/training/  (default)

Split assignment rules (deterministic, seed-controlled):
    - Records pre-labelled split="train"       → train.jsonl
    - Records pre-labelled split="validation"  → validation.jsonl
    - Records pre-labelled split="test"        → test.jsonl
    - Records pre-labelled split="benchmark"   → test.jsonl (normalised)
    - Records without a pre-assigned split     → auto-split (train_ratio / validation_ratio / remainder)

JSONL format: one JSON object per line, UTF-8 encoded.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.hsse_transformer.open_framework import (
    TrainingRecord,
    ingest_dataset_layers,
    load_training_records,
)


SPLIT_TRAIN = "train"
SPLIT_VALIDATION = "validation"
SPLIT_TEST = "test"

# Splits that are treated as test data
_TEST_EQUIVALENT_SPLITS = {"test", "benchmark"}


def _record_to_dict(record: TrainingRecord) -> Dict[str, Any]:
    """Serialise a TrainingRecord to a JSON-compatible dict.

    Normalises the 'benchmark' split label to 'test' in the output.
    """
    d = asdict(record)
    if d.get("split") == "benchmark":
        d["split"] = SPLIT_TEST
    return d


def _assign_splits(
    records: List[TrainingRecord],
    train_ratio: float,
    validation_ratio: float,
    seed: int,
) -> Tuple[List[TrainingRecord], List[TrainingRecord], List[TrainingRecord]]:
    """Route records into train / validation / test buckets.

    Records that already carry a valid split label are routed directly.
    Any remaining records are auto-split using a seeded shuffle so the
    result is reproducible across runs.

    Args:
        records: All loaded training records.
        train_ratio: Fraction of unassigned records for training.
        validation_ratio: Fraction of unassigned records for validation.
            Test receives the remainder.
        seed: Integer seed for reproducible shuffling.

    Returns:
        Three lists: (train_records, validation_records, test_records).
    """
    pre_train: List[TrainingRecord] = []
    pre_validation: List[TrainingRecord] = []
    pre_test: List[TrainingRecord] = []
    unassigned: List[TrainingRecord] = []

    for record in records:
        if record.split == SPLIT_TRAIN:
            pre_train.append(record)
        elif record.split == SPLIT_VALIDATION:
            pre_validation.append(record)
        elif record.split in _TEST_EQUIVALENT_SPLITS:
            pre_test.append(record)
        else:
            unassigned.append(record)

    if unassigned:
        rng = random.Random(seed)
        shuffled = list(unassigned)
        rng.shuffle(shuffled)
        n = len(shuffled)

        if n == 1:
            n_train, n_val = 1, 0
        elif n == 2:
            n_train, n_val = 1, 1
        else:
            n_train = max(1, int(n * train_ratio))
            n_val = max(1, int(n * validation_ratio))
            # Make sure train + val don't consume everything
            if n_train + n_val >= n:
                n_val = max(0, n - n_train - 1)

        pre_train.extend(shuffled[:n_train])
        pre_validation.extend(shuffled[n_train : n_train + n_val])
        pre_test.extend(shuffled[n_train + n_val :])

    return pre_train, pre_validation, pre_test


def _write_jsonl(records: List[TrainingRecord], path: Path) -> None:
    """Write a list of TrainingRecord objects to a JSONL file.

    Creates parent directories as needed. Overwrites existing file.

    Args:
        records: Records to serialise.
        path: Destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(_record_to_dict(record), ensure_ascii=False) + "\n")


def build_training_splits(
    dataset_root: str | Path,
    output_dir: str | Path | None = None,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run the Phase 3 training data pipeline.

    Loads all records from the dataset manifest, assigns train / validation /
    test splits, and writes JSONL files to the output directory.

    Args:
        dataset_root: Path to the dataset root directory containing the 01–04
            layer folders and the 04_AI_DATA/manifest.json.
        output_dir: Directory for JSONL output files.  Defaults to
            ``<dataset_root>/04_AI_DATA/training/``.
        train_ratio: Fraction of *unassigned* records to allocate to training.
            Must be in (0, 1). Default 0.70.
        validation_ratio: Fraction of *unassigned* records for validation.
            Must be in (0, 1). Test receives the remainder. Default 0.15.
        seed: Seed for the deterministic split of unassigned records.
            Default 42.

    Returns:
        Summary dict containing total record count, per-split counts, output
        file paths, and dataset ingestion summary.

    Raises:
        ValueError: If ratio values are invalid or if train_ratio +
            validation_ratio >= 1.0.
        FileNotFoundError: If dataset root or manifest is missing.
    """
    if not (0.0 < train_ratio < 1.0):
        raise ValueError(
            f"train_ratio must be in (0, 1), got {train_ratio}"
        )
    if not (0.0 < validation_ratio < 1.0):
        raise ValueError(
            f"validation_ratio must be in (0, 1), got {validation_ratio}"
        )
    if train_ratio + validation_ratio >= 1.0:
        raise ValueError(
            f"train_ratio + validation_ratio must be < 1.0, "
            f"got {train_ratio + validation_ratio:.4f}"
        )

    root = Path(dataset_root)
    out_dir = Path(output_dir) if output_dir is not None else root / "04_AI_DATA" / "training"

    records = load_training_records(root)
    ingestion = ingest_dataset_layers(root)

    train_records, val_records, test_records = _assign_splits(
        records, train_ratio, validation_ratio, seed
    )

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "validation.jsonl"
    test_path = out_dir / "test.jsonl"

    _write_jsonl(train_records, train_path)
    _write_jsonl(val_records, val_path)
    _write_jsonl(test_records, test_path)

    return {
        "pipeline": "mega_hsse_training_pipeline_v1",
        "dataset_root": str(root),
        "total_records": len(records),
        "splits": {
            "train": len(train_records),
            "validation": len(val_records),
            "test": len(test_records),
        },
        "output_files": {
            "train": str(train_path),
            "validation": str(val_path),
            "test": str(test_path),
        },
        "ingestion_summary": {
            "knowledge_library_files": ingestion.knowledge_library_files,
            "technical_library_files": ingestion.technical_library_files,
            "general_knowledge_files": ingestion.general_knowledge_files,
            "ai_data_files": ingestion.ai_data_files,
        },
    }
