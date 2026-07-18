"""India deployment inference cost model."""

from __future__ import annotations

from typing import Any


def compute_inference_costs() -> dict[str, Any]:
    base_throughput_tok_s = 85
    gpu_cost_inr_hr = 125
    gpu_cost_usd_hr = 1.50
    tokens_per_hour = base_throughput_tok_s * 3600
    cost_per_million = (gpu_cost_usd_hr / tokens_per_hour) * 1_000_000

    configs = {
        "40b_int4_baseline": {
            "cost_per_million_tokens_usd": round(cost_per_million, 2),
            "throughput_tok_s": base_throughput_tok_s,
        },
        "40b_speculative_7b_draft": {
            "cost_per_million_tokens_usd": 3.15,
            "throughput_tok_s": 130,
        },
        "blended_8b_40b_80_20": {
            "cost_per_million_tokens_usd": 1.85,
            "throughput_tok_s": 220,
        },
    }

    # Year-2 scale: 30M queries/day, 1200 tokens/query
    scale = {"queries_per_day": 30_000_000, "avg_tokens": 1200}
    annual_tokens = scale["queries_per_day"] * scale["avg_tokens"] * 365

    tco = {}
    for name, cfg in configs.items():
        annual = annual_tokens / 1e6 * cfg["cost_per_million_tokens_usd"]
        tco[name] = round(annual / 1e6, 1)

    return {
        "serving_config": "40B INT4 GQA, 2× L40S per replica (Mumbai/Chennai)",
        "gpu_cost_india": {"inr_per_hr": gpu_cost_inr_hr, "usd_per_hr": gpu_cost_usd_hr},
        "configs": configs,
        "year2_scale": scale,
        "annual_tco_usd_millions": tco,
        "india_tokenizer_savings_vs_generic_usd_m": round(tco["40b_int4_baseline"] - tco["40b_int4_baseline"] * 0.79, 1),
    }
