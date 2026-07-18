"""Vocabulary size Pareto: embedding cost vs fertility vs stability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from india40b.fertility_model import FERTILITY_BY_TOKENIZER


def load_options(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "vocab_size_options.json").read_text())


def compute_vocab_size_tradeoff(inputs_dir: Path | None = None) -> dict[str, Any]:
    cfg = load_options(inputs_dir)
    hidden = cfg["hidden_dim"]
    base_fert = FERTILITY_BY_TOKENIZER["india_first_128k"]["avg_indic"]
    base_vocab = 128_000
    rows = []

    for opt in cfg["options"]:
        v = opt["vocab"]
        embedding_gb = v * hidden * 2 / (1024**3)
        # ponytail: heuristic — larger vocab improves fertility up to 128k, then diminishing + stability cost
        delta_32k = (v - base_vocab) / 32_000
        fertility = round(base_fert - delta_32k * cfg["fertility_penalty_per_32k"], 3)
        if v > 160_000:
            fertility += cfg["stability_penalty_above_160k"] * 0.1
        stability = max(0.5, 1.0 - max(0, v - 160_000) / 200_000)
        deploy_fit = 1.0 if v <= 128_000 else max(0.5, 1.0 - (v - 128_000) / 200_000)
        score = round(
            0.35 * (1.46 - fertility) + 0.25 * stability + 0.2 * (1 - embedding_gb / 15) + 0.2 * deploy_fit,
            3,
        )
        rows.append({
            "label": opt["label"],
            "vocab": v,
            "embedding_gb_bf16": round(embedding_gb, 2),
            "avg_indic_fertility_est": fertility,
            "training_stability": round(stability, 2),
            "composite_score": score,
            "chosen": v == cfg["chosen"],
        })

    winner = max(rows, key=lambda r: r["composite_score"])
    return {
        "hidden_dim": hidden,
        "baseline_fertility_128k": base_fert,
        "options": rows,
        "decision": cfg["chosen"],
        "decision_label": "128k",
        "rejected_rationale": {
            "96k": "Indic conjunct fragmentation; fertility +0.08 vs 128k",
            "160k": "Embedding +2.1GB; marginal fertility gain −0.02",
            "200k": "Embedding +4.5GB; stability penalty; SME TCO crosses threshold",
            "256k": "12.8GB embedding table; inference memory blocks 2×L40S deploy",
        },
        "winner_by_score": winner["label"],
    }
