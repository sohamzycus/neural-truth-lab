#!/usr/bin/env python3
"""Validate mixture_spec.json — ponytail: single runnable check for Session 5 plan."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "data" / "mixture_spec.json"


def main() -> int:
    spec = json.loads(SPEC.read_text())
    errors: list[str] = []

    lanes = spec["capability_lanes"]
    pct_sum = sum(l["pct"] for l in lanes)
    if abs(pct_sum - 100) > 0.01:
        errors.append(f"capability lanes sum to {pct_sum}%, expected 100%")

    active_b = spec["active_pretrain_tokens_b"]
    token_sum = sum(l["tokens_b"] for l in lanes)
    if abs(token_sum - active_b) > 0.5:
        errors.append(f"lane tokens sum to {token_sum}B, expected {active_b}B")

    for lane in lanes:
        expected = active_b * lane["pct"] / 100
        if abs(lane["tokens_b"] - expected) > 0.5:
            errors.append(f"{lane['id']}: tokens_b {lane['tokens_b']} != {expected:.1f}")

    indic = next(l for l in lanes if l["id"] == "indic_multilingual")
    tier = indic["indic_tier_split"]
    tier_pct = sum(t["pct"] for t in tier.values())
    if tier_pct != 100:
        errors.append(f"Indic tier split sums to {tier_pct}%, expected 100%")
    tier_b = sum(t["tokens_b"] for t in tier.values())
    if abs(tier_b - indic["tokens_b"]) > 0.5:
        errors.append(f"Indic tier tokens {tier_b}B != lane {indic['tokens_b']}B")

    floor = spec["always_on_floor"]
    for lid, f in floor.items():
        lane = next((l for l in lanes if l["id"] == lid), None)
        if lane and f["pct"] > lane["pct"]:
            errors.append(f"floor {lid} ({f['pct']}%) exceeds lane allocation ({lane['pct']}%)")

    phases = spec["curriculum_phases"]
    phase_pct = sum(p["token_pct"] for p in phases)
    if phase_pct != 100:
        errors.append(f"curriculum phases sum to {phase_pct}%, expected 100%")

    diff_pct = sum(b["pct"] for b in spec["difficulty_bands"])
    if diff_pct != 100:
        errors.append(f"difficulty bands sum to {diff_pct}%")

    reason_pct = sum(b["pct"] for b in spec["reasoning_bands"])
    if reason_pct != 100:
        errors.append(f"reasoning bands sum to {reason_pct}%")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS")
    print(f"  lanes={len(lanes)} active={active_b}B anneal={spec['anneal_reserve_tokens_b']}B")
    print(f"  indic_tiers: verified={tier['verified']['pct']}% unverified={tier['unverified']['pct']}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
