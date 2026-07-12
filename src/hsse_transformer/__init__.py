"""Open training scaffold for the Mega HSSE Transformer."""

from src.hsse_transformer.domain_map import HEAD_DOMAIN_MAP, all_head_names, head_name
from src.hsse_transformer.open_framework import (
    INSUFFICIENT_INFO_DECISION,
    TrainingRecord,
    ingest_dataset_layers,
    load_training_records,
    run_benchmark_evaluation,
    train_open_framework,
)

__all__ = [
    "HEAD_DOMAIN_MAP",
    "all_head_names",
    "head_name",
    "INSUFFICIENT_INFO_DECISION",
    "TrainingRecord",
    "ingest_dataset_layers",
    "load_training_records",
    "run_benchmark_evaluation",
    "train_open_framework",
]
