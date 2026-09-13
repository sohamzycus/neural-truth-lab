"""Result schema validation."""

from __future__ import annotations

from typing import Any


def validate_evidence_record(record: dict[str, Any]) -> list[str]:
    required = [
        "evidence_id", "experiment_id", "claim_id", "hypothesis", "controls",
        "changed_variable", "seed", "raw_artifacts", "derived_metrics",
        "decision", "confidence", "reproducibility_command", "timestamp",
        "execution_mode",
    ]
    errors = []
    for k in required:
        if k not in record:
            errors.append(f"Missing field: {k}")
    return errors
