"""Training FLOPs, GPU-hours, and $100M budget allocation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_hardware(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "hardware_assumptions.json").read_text())


def compute_training_cost(inputs_dir: Path | None = None) -> dict[str, Any]:
    hw = load_hardware(inputs_dir)
    n = hw["parameters"]
    d = hw["total_tokens"]
    flops = 6 * n * d
    throughput = hw["h100_flops_per_second"]
    raw_seconds = flops / throughput
    raw_gpu_hours = raw_seconds / 3600
    billable = raw_gpu_hours * hw["cluster_overhead_multiplier"]
    cost_one_run = billable * hw["h100_cost_per_hour_usd"]

    budget_lines = {
        "pretrain_ablations": {"usd_m": 22, "gpu_hours_m": 1.85},
        "post_train_sft": {"usd_m": 8, "gpu_hours_m": 0.42},
        "alignment_dpo_rlhf": {"usd_m": 12, "gpu_hours_m": 0.65},
        "eval_red_team": {"usd_m": 8, "gpu_hours_m": 0.30},
        "data_acquisition_cleaning": {"usd_m": 15, "gpu_hours_m": 0},
        "engineering_research": {"usd_m": 20, "gpu_hours_m": 0},
        "inference_pilot_india": {"usd_m": 5, "gpu_hours_m": 0.15},
        "contingency": {"usd_m": 10, "gpu_hours_m": 0.40},
    }
    total_usd = sum(v["usd_m"] for v in budget_lines.values())
    total_gpu = sum(v["gpu_hours_m"] for v in budget_lines.values())

    return {
        "parameters": n,
        "total_tokens": d,
        "flops": f"{flops:.2e}",
        "h100_effective_throughput": throughput,
        "raw_gpu_hours_one_run": round(raw_gpu_hours),
        "billable_gpu_hours_one_run": round(billable),
        "cost_one_full_pretrain_run_usd": round(cost_one_run),
        "budget_allocation_usd_m": budget_lines,
        "total_budget_usd_m": total_usd,
        "total_gpu_hours_m": round(total_gpu, 2),
        "timeline_months": 18,
    }
