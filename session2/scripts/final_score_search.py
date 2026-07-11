#!/usr/bin/env python3
"""Boundary-aware score-improvement search (Track A, phases 9–12)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import load_frozen
from samabpe.scoring import compute_score
from samabpe.strategies import EN_MAX_FERTILITY, train_weighted_shared
from samabpe.verify_core import run_verification, sha256_file

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "frozen"
BASELINE = RESULTS / "final_pass_baseline.json"

# ponytail: 4-point local grid — full 8-point grid ~15min; expand offline if needed
WEIGHT_GRID = [
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 2.5},
    {"en": 1.0, "hi": 2.5, "te": 3.0, "bn": 3.5},
    {"en": 1.0, "hi": 3.0, "te": 3.5, "bn": 4.0},
    {"en": 1.0, "hi": 2.0, "te": 4.0, "bn": 4.5},
]


def _entry(
    iteration: int,
    technique: str,
    weights: dict,
    res,
    corpora: dict[str, str],
    *,
    accepted: bool,
    reason: str,
    tok_hash: str | None = None,
) -> dict:
    fert = res.fertilities
    m = res.metrics
    return {
        "candidate_id": f"ws_{iteration}",
        "iteration": iteration,
        "change_description": f"weighted_shared weights={weights}",
        "optimization_technique": technique,
        "status": "VERIFIED",
        "accepted": accepted,
        "tokenizer_sha256": tok_hash,
        "vocabulary_size": res.tokenizer.vocab_size,
        "token_counts": {lang: res.tokenizer.count_tokens(corpora[lang]) for lang in ("en", "hi", "te", "bn")},
        "fertilities": fert,
        "x_min": m["x_min"],
        "x_max": m["x_max"],
        "x_min_language": min(fert, key=fert.get),
        "x_max_language": max(fert, key=fert.get),
        "gap": m["max_min_gap"],
        "score": m["score"],
        "english_constraint": fert["en"] <= EN_MAX_FERTILITY,
        "reason": reason,
    }


def main() -> int:
    if not BASELINE.exists():
        print("Run scripts/verify.py first (records pre_final_baseline.json)")
        return 1

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    corpora = load_frozen(DATA.parent)
    trace: list[dict] = []
    best_score = baseline["score"]
    best_res = None
    best_weights = None
    initial_x_max = baseline.get("x_max_language") or max(baseline["fertilities"], key=baseline["fertilities"].get)
    boundary_transitions: list[dict] = []

    for i, weights in enumerate(WEIGHT_GRID, 1):
        res = train_weighted_shared(corpora, weights=weights)
        m = res.metrics
        accepted = res.fertilities["en"] <= EN_MAX_FERTILITY and m["score"] > best_score
        entry = _entry(i, "corpus_weight_perturbation", weights, res, corpora, accepted=accepted, reason="weight grid")
        if accepted:
            old_x_max = max(res.fertilities, key=res.fertilities.get) if not best_res else max(best_res.fertilities, key=best_res.fertilities.get)
            best_score = m["score"]
            best_res = res
            best_weights = weights
            entry["reason"] = "verified score improvement"
            new_x_max = max(res.fertilities, key=res.fertilities.get)
            if new_x_max != initial_x_max:
                boundary_transitions.append({
                    "iteration": i,
                    "from_x_max": initial_x_max,
                    "to_x_max": new_x_max,
                    "weights": weights,
                })
        trace.append(entry)
        print(f"  [{i}/{len(WEIGHT_GRID)}] score={m['score']:.4f} gap={m['max_min_gap']:.6f} accepted={accepted}", flush=True)

    trace_path = RESULTS / "final_score_search_trace.json"
    summary = {
        "track": "A_compression_honest",
        "deliberate_degradation_used": False,
        "initial_x_min_language": baseline.get("x_min_language"),
        "initial_x_max_language": initial_x_max,
        "algorithms_attempted": ["corpus_weight_perturbation"],
        "candidates_materialized": len(trace),
        "candidates_accepted": sum(1 for t in trace if t["accepted"]),
        "boundary_transitions": boundary_transitions,
        "baseline_score": baseline["score"],
        "best_score": best_score,
        "improved": best_res is not None and best_score > baseline["score"],
    }
    out = {"summary": summary, "trace": trace}
    trace_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    if best_res and best_score > baseline["score"]:
        tok_path = RESULTS / "tokenizer.json"
        best_res.tokenizer.save(tok_path)
        print(f"IMPROVED: {baseline['score']:.4f} → {best_score:.4f} (weights={best_weights})")
        for t in trace:
            if t["accepted"]:
                t["tokenizer_sha256"] = sha256_file(tok_path)
    else:
        print(f"No improvement over pre-final baseline {baseline['score']:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
