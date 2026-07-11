#!/usr/bin/env python3
"""Track A: lightweight weight search for verified score improvement."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import load_frozen
from samabpe.strategies import EN_MAX_FERTILITY, train_weighted_shared
from samabpe.verify_core import run_verification

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "frozen"
BASELINE = RESULTS / "baseline_verification.json"

# Small grid — each train ~30-60s
WEIGHT_GRID = [
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 2.5},
    {"en": 1.0, "hi": 2.5, "te": 3.0, "bn": 3.0},
    {"en": 1.0, "hi": 3.0, "te": 3.0, "bn": 3.5},
    {"en": 1.0, "hi": 2.0, "te": 3.5, "bn": 3.5},
]


def main() -> int:
    if not BASELINE.exists():
        print("Run scripts/verify.py first to record baseline")
        return 1

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    corpora = load_frozen(DATA.parent)
    trace: list[dict] = []
    best_score = baseline["score"]
    best_res = None

    for i, weights in enumerate(WEIGHT_GRID, 1):
        res = train_weighted_shared(corpora, weights=weights)
        entry = {
            "iteration": i,
            "strategy": f"weighted_shared_{weights}",
            "status": "VERIFIED",
            "accepted": False,
            "vocabulary_size": res.tokenizer.vocab_size,
            "fertilities": res.fertilities,
            "x_min": res.metrics["x_min"],
            "x_max": res.metrics["x_max"],
            "gap": res.metrics["max_min_gap"],
            "score": res.metrics["score"],
            "english_constraint": res.fertilities["en"] <= EN_MAX_FERTILITY,
            "reason": "weight grid search Track A",
        }
        if res.fertilities["en"] <= EN_MAX_FERTILITY and res.metrics["score"] > best_score:
            best_score = res.metrics["score"]
            best_res = res
            entry["accepted"] = True
            entry["reason"] = "verified score improvement"
        trace.append(entry)
        print(f"  weights={weights} score={res.metrics['score']:.4f} accepted={entry['accepted']}")

    trace_path = RESULTS / "score_search_trace.json"
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    if best_res and best_score > baseline["score"]:
        best_res.tokenizer.save(RESULTS / "tokenizer.json")
        print(f"IMPROVED: {baseline['score']:.4f} → {best_score:.4f}")
        run_verification(RESULTS / "tokenizer.json", DATA)  # caller runs verify.py
    else:
        print(f"No improvement over baseline {baseline['score']:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
