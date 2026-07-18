#!/usr/bin/env python3
"""Assert report key numbers match derived JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"


def load(name: str) -> dict:
    return json.loads((DERIVED / name).read_text())


def check_language_weights() -> None:
    lw = load("language_weights.json")
    hi = lw["weights_percent"]["hi"]
    assert 16 <= hi <= 20, f"Hindi weight {hi}% out of expected range"
    assert lw["hindi_mcda_vs_population"]["delta_pp"] < 0, "Hindi should be below population share"


def check_vocab() -> None:
    v = load("vocab_allocation.json")
    assert v["total_vocab"] == 128_000
    assert sum(v["buckets"].values()) == 128_000


def check_data_mix() -> None:
    dm = load("data_mix.json")
    assert dm["synthetic_cap_percent"] == 6.0
    assert dm["slice_tokens_billions"]["code"] == 144.0


def check_training_budget() -> None:
    tb = load("training_budget.json")
    assert tb["total_budget_usd_m"] == 100


def check_report_mentions() -> None:
    report = (ROOT / "report" / "REPORT.md").read_text()
    lw = load("language_weights.json")
    hi_pct = lw["weights_percent"]["hi"]
    assert f"{hi_pct}%" in report or f"{hi_pct:.0f}%" in report, "Report missing Hindi MCDA weight"


def check_cleaning() -> None:
    cp = load("cleaning_pipeline.json")
    assert cp["stage_count"] == 16
    assert 20 <= cp["composite_yield_percent"] <= 35


def check_vocab_tradeoff() -> None:
    vt = load("vocab_size_tradeoff.json")
    assert vt["decision"] == 128_000
    assert vt["winner_by_score"] == "128k"


def check_capability_data() -> None:
    cd = load("capability_data.json")
    assert cd["capability_count"] == 10


def main() -> None:
    if not DERIVED.exists():
        print("Run derive_all.py first", file=sys.stderr)
        sys.exit(1)

    check_vocab()
    check_language_weights()
    check_data_mix()
    check_training_budget()
    check_cleaning()
    check_vocab_tradeoff()
    check_capability_data()
    check_report_mentions()
    print("verify.py: all checks passed")


if __name__ == "__main__":
    main()
