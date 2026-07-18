"""16-stage cleaning pipeline yield model."""

from __future__ import annotations

import json
from functools import reduce
from operator import mul
from pathlib import Path
from typing import Any


def load_stages(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "cleaning_stages.json").read_text())


def _composite(stages: list[dict[str, Any]], skip: set[str]) -> float:
    ys = [s["yield"] for s in stages if s["id"] not in skip]
    return reduce(mul, ys, 1.0)


def compute_cleaning_pipeline(inputs_dir: Path | None = None) -> dict[str, Any]:
    cfg = load_stages(inputs_dir)
    stages = cfg["stages"]
    # ponytail: path-dependent — code slice runs L12; web/NL skips compilation
    web_skip = {"L12"}
    code_only = set()

    web_yield = _composite(stages, web_skip)
    code_yield = _composite(stages, code_only)
    slice_weights = {"web_nl": 0.82, "code": 0.12, "math": 0.04, "synthetic": 0.02}
    composite = (
        slice_weights["web_nl"] * web_yield
        + slice_weights["code"] * code_yield
        + slice_weights["math"] * web_yield * 0.95
        + slice_weights["synthetic"] * web_yield * 0.9
    )
    over_collection = round(1 / composite, 2) if composite else 0

    return {
        "stage_count": len(stages),
        "stages": stages,
        "path_yields": {
            "web_nl_skip_L12": round(web_yield, 4),
            "code_full_pipeline": round(code_yield, 4),
        },
        "composite_yield": round(composite, 4),
        "composite_yield_percent": round(composite * 100, 1),
        "over_collection_multiplier": over_collection,
        "dedup_threshold": cfg["dedup_threshold"],
        "strictness_profile": cfg["strictness_profile"],
    }
