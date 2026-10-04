"""Routing summaries from training logs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def _parse_util(s: str) -> list[float]:
    if not s or s == "[]":
        return []
    return json.loads(s)


def routing_summary_from_moe_log(moe_csv: Path, conversion_entropy: float) -> dict[str, Any]:
    df = pd.read_csv(moe_csv)
    util_rows = []
    for _, row in df.iterrows():
        u = _parse_util(str(row.get("expert_utilization", "")))
        if u:
            util_rows.append(u)
    if not util_rows:
        return {}
    final = util_rows[-1]
    spread = max(final) - min(final)
    return {
        "utilization_per_expert_final": final,
        "min_utilization": min(final),
        "max_utilization": max(final),
        "mean_utilization": sum(final) / len(final),
        "utilization_spread": spread,
        "active_expert_count_final": sum(1 for x in final if x > 0),
        "router_entropy_at_conversion": conversion_entropy,
        "router_entropy_at_final_step": float(df.iloc[-1]["router_entropy"]),
    }


def routing_evolution_table(moe_csv: Path, dense_steps: int) -> dict[str, Any]:
    df = pd.read_csv(moe_csv)
    max_step = int(df["step"].max())
    targets = {
        "conversion": int(dense_steps),
        "plus_10": int(dense_steps + 10),
        "midpoint": int(dense_steps + (max_step - dense_steps) // 2),
        "final": max_step,
    }
    rows: dict[str, list[float]] = {}
    for label, step in targets.items():
        match = df[df["step"] == step]
        if match.empty:
            nearest = df.iloc[(df["step"] - step).abs().argsort()[:1]]
            match = nearest
        u = _parse_util(str(match.iloc[0]["expert_utilization"]))
        rows[label] = u
    return {"steps": targets, "expert_utilization": rows}
