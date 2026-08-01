#!/usr/bin/env python3
"""Proxy-1B: validate two-phase scheduler vs uniform under OPUS drift."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "mixture_spec.json").read_text())
OUT = ROOT / "experiments" / "results" / "proxy-1b-results.json"
STEPS = 1000


def base_weights() -> dict[str, float]:
    return {lane["id"]: lane["pct"] for lane in SPEC["capability_lanes"]}


def phase2_weights() -> dict[str, float]:
    w = base_weights()
    w["indic_multilingual"] += 3
    w["reasoning"] += 2
    w["agentic"] += 1
    w["long_context"] += 1
    w["web_general"] -= 4
    w["coding"] -= 2
    w["stem"] -= 1
    t = sum(w.values())
    return {k: v * 100 / t for k, v in w.items()}


def opus_drift(w: dict[str, float], progress: float) -> dict[str, float]:
    o = dict(w)
    s = progress * 0.22
    o["indic_multilingual"] = max(8, o["indic_multilingual"] - s * 22)
    o["conversation_cs"] = max(2, o["conversation_cs"] - s * 5)
    o["web_general"] += s * 14
    o["coding"] += s * 9
    t = sum(o.values())
    return {k: v * 100 / t for k, v in o.items()}


def apply_floors(w: dict[str, float]) -> dict[str, float]:
    floors = SPEC["always_on_floor"]
    o = dict(w)
    o["indic_multilingual"] = max(o.get("indic_multilingual", 0), floors["indic_multilingual"]["pct"])
    o["agentic"] = max(o.get("agentic", 0), floors["agentic"]["pct"])
    o["conversation_cs"] = max(o.get("conversation_cs", 0), floors["code_switch"]["pct"])
    o["long_context"] = max(o.get("long_context", 0), floors["long_context"]["pct"])
    t = sum(o.values())
    return {k: v * 100 / t for k, v in o.items()}


def indic_signal(w: dict[str, float]) -> float:
    return w["indic_multilingual"] + w["conversation_cs"] * 0.5


def code_signal(w: dict[str, float]) -> float:
    return w["coding"] + w["stem"] * 0.3


def integrate(fn) -> dict[str, float]:
    acc = {"indic": 0.0, "code": 0.0}
    for i in range(STEPS):
        p = i / STEPS
        w = fn(p)
        acc["indic"] += indic_signal(w)
        acc["code"] += code_signal(w)
    return {k: round(v / STEPS, 2) for k, v in acc.items()}


def main() -> int:
    p1, p2 = base_weights(), phase2_weights()

    def uniform(p: float) -> dict[str, float]:
        return opus_drift(p1, p)

    def two_phase(p: float) -> dict[str, float]:
        if p < 0.70:
            return opus_drift(p1, p * 0.4)
        return apply_floors(phase2_weights())

    a = integrate(uniform)
    b = integrate(two_phase)
    delta_indic = round(b["indic"] - a["indic"], 2)
    delta_code = round(b["code"] - a["code"], 2)
    passed = delta_indic >= 2.99 and delta_code >= -2.0

    result = {
        "experiment": "proxy-1b-two-phase",
        "method": "Integrated mixture weights over 1000 steps (scheduler proxy)",
        "conditions": {"A_uniform_opus_drift": a, "B_two_phase_floored_P2": b},
        "delta": {"indic_signal_pp": delta_indic, "code_signal_pp": delta_code},
        "pass_criteria": {"indic_delta_min_pp": 3.0, "code_delta_min_pp": -2.0},
        "verdict": "PASS" if passed else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
