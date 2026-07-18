"""Pretrain data mix: NL, code, math, synthetic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from india40b.language_weights import allocate_tokens


def load_data_mix(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "data_mix.json").read_text())


def compute_data_mix(inputs_dir: Path | None = None) -> dict[str, Any]:
    mix = load_data_mix(inputs_dir)
    total = mix["total_tokens"]
    slices = mix["slices"]

    slice_tokens = {k: round(total * v) for k, v in slices.items()}
    nl_tokens = slice_tokens["natural_language"]
    lang_allocation = allocate_tokens(nl_tokens, inputs_dir)

    code_total = slice_tokens["code"]
    code_breakdown = {
        lang: round(code_total * pct)
        for lang, pct in mix["code_languages"].items()
    }

    return {
        "total_tokens": total,
        "slices": slices,
        "slice_tokens_billions": {k: round(v / 1e9, 1) for k, v in slice_tokens.items()},
        "language_allocation_billions": {k: round(v / 1e9, 1) for k, v in lang_allocation.items()},
        "code_breakdown_billions": {k: round(v / 1e9, 1) for k, v in code_breakdown.items()},
        "synthetic_cap_percent": slices["synthetic_cap"] * 100,
        "synthetic_quality_gate": mix["synthetic_quality_gate"],
        "rejected_synthetic_above_percent": mix["synthetic_diversity_collapse_threshold"] * 100,
    }
