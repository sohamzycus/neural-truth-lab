"""Derive 128k vocabulary allocation from script inventory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_vocab_budget(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "vocab_budget.json").read_text())


def derive_vocab_allocation(inputs_dir: Path | None = None) -> dict[str, Any]:
    budget = load_vocab_budget(inputs_dir)
    buckets = budget["buckets"]
    total = sum(buckets.values())
    target = budget["total_vocab"]
    assert total == target, f"Bucket sum {total} != target {target}"

    embedding_params = target * 40_000_000_000  # vocab × hidden (approx for 40B)
    embedding_gb = embedding_params * 2 / (1024**3)  # bf16

    return {
        "total_vocab": target,
        "algorithm": budget["algorithm"],
        "buckets": buckets,
        "exposure_weights": budget["tokenizer_exposure_weights"],
        "embedding_table_params": embedding_params,
        "embedding_table_gb_bf16": round(embedding_gb, 2),
        "derivation": (
            "V_total = S_special + S_byte + Σ(script_allocation) + S_code + S_math + S_learned_shared"
        ),
    }
