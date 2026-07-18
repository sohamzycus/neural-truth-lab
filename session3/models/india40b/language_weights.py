"""7-factor MCDA language weight calculator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_language_signals(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "language_signals.json").read_text())


def compute_mcda_weights(inputs_dir: Path | None = None) -> dict[str, Any]:
    signals = load_language_signals(inputs_dir)
    factors = signals["factors"]
    languages = signals["languages"]

    raw_scores: dict[str, float] = {}
    for lang_id, lang in languages.items():
        score = sum(factors[f] * lang[f] for f in factors)
        raw_scores[lang_id] = score

    # ponytail: squared scores sharpen India-first leaders without pure population weighting
    sharpened = {k: v**2.8 for k, v in raw_scores.items()}
    total = sum(sharpened.values())
    weights = {k: v / total for k, v in sharpened.items()}

    # Population-proportional baseline for comparison
    pop_total = sum(lang["population_share"] for lang in languages.values())
    pop_weights = {k: lang["population_share"] / pop_total for k, lang in languages.items()}

    return {
        "method": "7-factor MCDA",
        "factors": factors,
        "weights": {k: round(v, 4) for k, v in weights.items()},
        "weights_percent": {k: round(v * 100, 1) for k, v in weights.items()},
        "population_baseline_percent": {k: round(v * 100, 1) for k, v in pop_weights.items()},
        "hindi_mcda_vs_population": {
            "mcda_percent": round(weights["hi"] * 100, 1),
            "population_percent": round(pop_weights["hi"] * 100, 1),
            "delta_pp": round((weights["hi"] - pop_weights["hi"]) * 100, 1),
        },
        "dravidian_collective_mcda": round(
            sum(weights.get(k, 0) for k in ("te", "ta", "kn", "ml")) * 100, 1
        ),
        "dravidian_collective_population": round(
            sum(pop_weights.get(k, 0) for k in ("te", "ta", "kn", "ml")) * 100, 1
        ),
    }


def allocate_tokens(
    natural_language_tokens: float,
    inputs_dir: Path | None = None,
) -> dict[str, Any]:
    weights = compute_mcda_weights(inputs_dir)["weights"]
    return {
        lang: round(natural_language_tokens * w, 1)
        for lang, w in weights.items()
    }
