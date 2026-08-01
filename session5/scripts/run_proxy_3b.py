#!/usr/bin/env python3
"""Proxy-3B: validate floors + 4k-32k context ramp on mixture weights."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "mixture_spec.json").read_text())
OUT = ROOT / "experiments" / "results" / "proxy-3b-results.json"
STEPS = 1000
RAMP = [(0.50, 4096), (0.65, 8192), (0.80, 16384), (1.00, 32768)]


def base_weights() -> dict[str, float]:
    return {lane["id"]: lane["pct"] for lane in SPEC["capability_lanes"]}


def opus_starve(w: dict[str, float]) -> dict[str, float]:
    o = dict(w)
    o["indic_multilingual"] *= 0.48
    o["conversation_cs"] *= 0.45
    o["agentic"] *= 0.48
    o["long_context"] *= 0.38
    o["web_general"] *= 1.16
    o["coding"] *= 1.11
    t = sum(o.values())
    return {k: v * 100 / t for k, v in o.items()}


def apply_floors(w: dict[str, float]) -> dict[str, float]:
    f = SPEC["always_on_floor"]
    o = dict(w)
    o["indic_multilingual"] = max(o.get("indic_multilingual", 0), f["indic_multilingual"]["pct"])
    o["agentic"] = max(o.get("agentic", 0), f["agentic"]["pct"])
    o["conversation_cs"] = max(o.get("conversation_cs", 0), f["code_switch"]["pct"])
    o["long_context"] = max(o.get("long_context", 0), f["long_context"]["pct"])
    t = sum(o.values())
    return {k: v * 100 / t for k, v in o.items()}


def context_boost(w: dict[str, float], ctx: int) -> dict[str, float]:
    o = dict(w)
    scale = max(0, math.log2(ctx / 4096))
    o["long_context"] *= 1 + 1.35 * scale
    o["reasoning"] *= 1 + 0.12 * scale
    t = sum(o.values())
    return {k: v * 100 / t for k, v in o.items()}


def lang_tail(w: dict[str, float]) -> float:
    return w.get("indic_multilingual", 0) + w.get("conversation_cs", 0) * 0.4


def needle_proxy(lc_pct: float, ctx: int) -> float:
    return round(min(0.95, 0.14 + (lc_pct / 3.0) * 0.30 + math.log2(ctx / 1024) * 0.14), 3)


def integrate(floors: bool, ramp: bool) -> dict[str, float]:
    tail, needle, agentic = 0.0, 0.0, 0.0
    for i in range(STEPS):
        p = (i + 1) / STEPS
        w = opus_starve(base_weights())
        if floors:
            w = apply_floors(w)
        ctx = 4096
        if ramp:
            for thr, c in RAMP:
                if p <= thr:
                    ctx = c
                    break
            w = context_boost(w, ctx)
        tail += lang_tail(w)
        needle += needle_proxy(w.get("long_context", 0), ctx)
        agentic += w.get("agentic", 0)
    n = STEPS
    return {
        "lang_tail_proxy": round(tail / n, 2),
        "needle_proxy": round(needle / n, 3),
        "agentic_pct": round(agentic / n, 2),
    }


def main() -> int:
    a = integrate(floors=False, ramp=False)
    b = integrate(floors=True, ramp=False)
    c = integrate(floors=True, ramp=True)
    delta_tail = round(c["lang_tail_proxy"] - a["lang_tail_proxy"], 2)
    passed = delta_tail >= 4.0 and c["needle_proxy"] >= 0.75 and c["agentic_pct"] >= a["agentic_pct"]

    result = {
        "experiment": "proxy-3b-indic-floor",
        "method": "Integrated weights + context ramp (scheduler proxy)",
        "conditions": {"A": a, "B": b, "C": c},
        "delta_C_vs_A": {"lang_tail_proxy": delta_tail, "needle_proxy": round(c["needle_proxy"] - a["needle_proxy"], 3)},
        "pass_criteria": {"lang_tail_delta_min": 4.0, "needle_min": 0.75},
        "verdict": "PASS" if passed else "FAIL",
        "floors_enforced": {k: v["pct"] for k, v in SPEC["always_on_floor"].items()},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
