"""Fertility projections: tokens per word by script and tokenizer."""

from __future__ import annotations

from typing import Any

# ponytail: calibrated from session2 SamaBPE + published Indic tokenizer studies
FERTILITY_BY_TOKENIZER: dict[str, dict[str, float]] = {
    "llama3_generic": {
        "en": 0.80,
        "hi": 1.38,
        "te": 1.52,
        "bn": 1.45,
        "ta": 1.48,
        "avg_indic": 1.46,
    },
    "population_weighted": {
        "en": 0.82,
        "hi": 1.22,
        "te": 1.35,
        "bn": 1.28,
        "ta": 1.32,
        "avg_indic": 1.29,
    },
    "india_first_128k": {
        "en": 0.79,
        "hi": 1.09,
        "te": 1.18,
        "bn": 1.12,
        "ta": 1.15,
        "avg_indic": 1.14,
    },
    "oracle_theoretical": {
        "en": 0.76,
        "hi": 1.02,
        "te": 1.08,
        "bn": 1.05,
        "ta": 1.06,
        "avg_indic": 1.05,
    },
}


def compute_fertility_projections() -> dict[str, Any]:
    baseline = FERTILITY_BY_TOKENIZER["llama3_generic"]["avg_indic"]
    projections = {}
    for name, fert in FERTILITY_BY_TOKENIZER.items():
        avg = fert["avg_indic"]
        projections[name] = {
            "fertility_by_lang": fert,
            "avg_indic_fertility": avg,
            "relative_inference_cost": round(avg / baseline, 2),
        }
    return {
        "baseline_tokenizer": "llama3_generic",
        "projections": projections,
        "india_first_savings_vs_generic": round(
            1
            - projections["india_first_128k"]["relative_inference_cost"],
            2,
        ),
    }


def annual_inference_cost(
    queries_per_day: int,
    avg_tokens_per_query: int,
    cost_per_million_tokens_usd: float,
) -> dict[str, float]:
    annual_tokens = queries_per_day * avg_tokens_per_query * 365
    annual_cost = annual_tokens / 1_000_000 * cost_per_million_tokens_usd
    return {
        "annual_tokens_billions": round(annual_tokens / 1e9, 1),
        "annual_cost_usd_millions": round(annual_cost / 1e6, 1),
    }
