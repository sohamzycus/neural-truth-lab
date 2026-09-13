"""Controlled comparison validator — central novelty."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CONTROL_FIELDS = [
    "model",
    "initialization",
    "data",
    "data_order",
    "seed_policy",
    "optimizer",
    "batch_size",
    "grad_accumulation",
    "dtype",
    "grad_clip",
    "weight_decay",
    "total_steps",
]


@dataclass
class RunConfig:
    controls: dict[str, Any]
    changed_variable: str
    run_id: str = "A"


@dataclass
class ComparisonResult:
    valid: bool
    mismatches: list[str]
    status: str  # VALID or INVALID_EXPERIMENT


def validate_comparison(run_a: RunConfig, run_b: RunConfig) -> ComparisonResult:
    """Verify only intended variable differs between two runs."""
    mismatches: list[str] = []
    allowed_diff = {run_a.changed_variable, run_b.changed_variable}
    # Both runs should change the same independent variable
    if run_a.changed_variable != run_b.changed_variable:
        mismatches.append(
            f"changed_variable mismatch: {run_a.changed_variable} vs {run_b.changed_variable}"
        )

    all_keys = set(run_a.controls) | set(run_b.controls)
    for key in sorted(all_keys):
        va = run_a.controls.get(key)
        vb = run_b.controls.get(key)
        if va != vb and key not in allowed_diff:
            mismatches.append(f"control '{key}' differs: {va!r} vs {vb!r}")

    if mismatches:
        return ComparisonResult(valid=False, mismatches=mismatches, status="INVALID_EXPERIMENT")
    return ComparisonResult(valid=True, mismatches=[], status="VALID")


def build_controls(cfg_dict: dict[str, Any]) -> dict[str, Any]:
    """Extract comparison controls from a LabConfig dict."""
    return {
        "model": cfg_dict.get("model"),
        "initialization": cfg_dict.get("initialization_seed"),
        "data": cfg_dict.get("data"),
        "data_order": cfg_dict.get("data_order_policy"),
        "seed_policy": cfg_dict.get("seed_policy"),
        "optimizer": cfg_dict.get("optimizer"),
        "batch_size": cfg_dict.get("batch_size"),
        "grad_accumulation": cfg_dict.get("grad_accumulation"),
        "dtype": cfg_dict.get("dtype"),
        "grad_clip": cfg_dict.get("grad_clip"),
        "weight_decay": cfg_dict.get("weight_decay"),
        "total_steps": cfg_dict.get("total_steps"),
    }
