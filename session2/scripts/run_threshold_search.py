#!/usr/bin/env python3
"""Threshold-aware weight search → constrained winner selection → freeze."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.hf_bpe_trainer import evaluate_tokenizer, load_faithful_corpora, sha256_file, train_hf_bpe
from samabpe.weight_optimizer import (
    CandidateResult,
    WeightConfig,
    pick_winner,
    pick_winner_constrained,
    threshold_grid,
    threshold_neighbor_configs,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "faithful"
CAND = ROOT / "results" / "resubmission" / "candidates"
PRIOR_REG = ROOT / "results" / "resubmission" / "experiments.json"
REGISTRY = ROOT / "results" / "resubmission" / "experiments.json"
COMPARISON = ROOT / "results" / "resubmission" / "comparison.json"
BASELINE_METRICS = ROOT / "results" / "resubmission" / "baseline" / "metrics.json"
FINAL = ROOT / "results" / "resubmission" / "final"


def _record_to_candidate(rec: dict) -> CandidateResult:
    w = WeightConfig(**rec["weights"]).canonical()
    return CandidateResult(
        weights=w,
        tokenizer_path=rec.get("tokenizer_path", f"results/resubmission/candidates/weights_{w.key()}.json"),
        vocab_size=rec.get("vocab_size", 10000),
        fertilities=rec["fertilities"],
        spread=rec["spread"],
        raw_score=rec["raw_score"],
        hindi_penalty=rec["hindi_penalty"],
        final_grade=rec.get("final_grade", rec.get("adjusted_score", 0)),
        tokenizer_sha256=rec.get("tokenizer_sha256", ""),
        experiment_id=rec.get("experiment_id", ""),
        status=rec.get("status", "MEASURED"),
    )


def _train_and_measure(
    corpora: dict[str, str],
    weights: WeightConfig,
    experiment_id: str,
) -> CandidateResult:
    path = CAND / f"weights_{weights.key()}.json"
    if path.exists():
        from tokenizers import Tokenizer

        tok = Tokenizer.from_file(str(path))
    else:
        tok, _ = train_hf_bpe(corpora, weights=weights.as_dict(), output_path=path)
    ev = evaluate_tokenizer(tok, corpora)
    return CandidateResult(
        weights=weights,
        tokenizer_path=str(path.relative_to(ROOT)),
        vocab_size=tok.get_vocab_size(with_added_tokens=True),
        fertilities=ev["fertilities"],
        spread=ev["spread"],
        raw_score=ev["raw_score"],
        hindi_penalty=ev["hindi_penalty"],
        final_grade=ev["final_grade"],
        tokenizer_sha256=sha256_file(path),
        experiment_id=experiment_id,
    )


def main() -> int:
    if not (CORPUS / "en.faithful.md").exists():
        print("Run scripts/build_wiki_faithful_markdown.py first")
        return 1

    CAND.mkdir(parents=True, exist_ok=True)
    corpora = load_faithful_corpora(CORPUS)

    by_key: dict[str, CandidateResult] = {}
    if PRIOR_REG.exists():
        prior = json.loads(PRIOR_REG.read_text(encoding="utf-8"))
        for rec in prior.get("experiments", []):
            c = _record_to_candidate(rec)
            by_key[c.weights.key()] = c
        print(f"Warm-start: {len(by_key)} prior measured configs")

    grid = threshold_grid()
    new_configs = [w for w in grid if w.key() not in by_key]
    print(f"Threshold grid: {len(grid)} unique configs, {len(new_configs)} new to train")

    n_id = len(by_key) + 1
    trained_new = 0
    for i, w in enumerate(new_configs, start=1):
        c = _train_and_measure(corpora, w, f"hf-threshold-{n_id:04d}")
        by_key[w.key()] = c
        n_id += 1
        trained_new += 1
        if i % 50 == 0:
            best_a = max(
                (x for x in by_key.values() if x.constraint_class == "A"),
                key=lambda x: x.final_grade,
                default=None,
            )
            msg = f"best A {best_a.final_grade:.2f}" if best_a else "no Class A yet"
            print(f"  {i}/{len(new_configs)} new… {msg}")

    # Neighbors around configs closest to EN/HI threshold
    ranked = sorted(
        by_key.values(),
        key=lambda c: max(c.fertilities["en"] - 1.2, 0) + max(c.fertilities["hi"] - 1.2, 0),
    )
    seen_keys = set(by_key)
    print("Threshold neighbors around near-valid configs…")
    for base in ranked[:12]:
        for w in threshold_neighbor_configs(base.weights):
            if w.key() in seen_keys:
                continue
            seen_keys.add(w.key())
            c = _train_and_measure(corpora, w, f"hf-threshold-{n_id:04d}")
            by_key[w.key()] = c
            n_id += 1
            trained_new += 1

    candidates = list(by_key.values())
    winner, selection = pick_winner_constrained(candidates)
    best_unconstrained = pick_winner(candidates)

    records = [c.to_experiment_record() for c in sorted(candidates, key=lambda x: x.final_grade, reverse=True)]
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "objective": "constrained_adjusted_score",
                "fertility_threshold": 1.2,
                "experiments": records,
                "winner_experiment_id": winner.experiment_id,
                "winner_selection": selection,
                "new_tokenizers_trained": trained_new,
                "total_measured": len(candidates),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    baseline_row = None
    if BASELINE_METRICS.exists():
        bm = json.loads(BASELINE_METRICS.read_text(encoding="utf-8"))
        baseline_row = {
            "label": "Baseline",
            "weights": {"en": 3, "hi": 4, "te": 4, "bn": 2},
            "fertilities": bm["fertilities"],
            "spread": bm["scoring"]["spread"],
            "adjusted_score": bm["scoring"]["final_grade"],
            "status": "Baseline",
        }

    bu = selection["best_unconstrained"]
    comparison = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": [
            baseline_row,
            {
                "label": "Best unconstrained",
                "weights": bu["weights"],
                "fertilities": bu["fertilities"],
                "spread": bu["spread"],
                "adjusted_score": bu["final_grade"],
                "status": "High-score experiment",
                "constraint_class": bu.get("constraint_class", "C"),
            },
            {
                "label": "Final submission",
                "weights": winner.weights.as_dict(),
                "fertilities": winner.fertilities,
                "spread": winner.spread,
                "adjusted_score": winner.final_grade,
                "status": "Threshold-aware winner",
                "constraint_class": winner.constraint_class,
                "english_threshold_pass": winner.english_threshold_pass,
                "hindi_threshold_pass": winner.hindi_threshold_pass,
            },
        ],
        "selection": selection,
    }
    COMPARISON.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    FINAL.mkdir(parents=True, exist_ok=True)
    src = ROOT / winner.tokenizer_path
    dst = FINAL / "tokenizer.json"
    dst.write_bytes(src.read_bytes())
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "evaluate_hf_tokenizer.py"),
            "--tokenizer",
            str(dst),
            "--corpus-dir",
            str(CORPUS),
            "--output",
            str(FINAL / "metrics.json"),
        ]
    )
    provenance = {
        "strategy": "threshold-aware-weight-search",
        "weights": winner.weights.as_dict(),
        "constraint_class": winner.constraint_class,
        "english_threshold_pass": winner.english_threshold_pass,
        "hindi_threshold_pass": winner.hindi_threshold_pass,
        "selection_reason": selection["selection_reason"],
        "tokenizer_sha256": sha256_file(dst),
        "experiment_id": winner.experiment_id,
        "new_tokenizers_trained": trained_new,
        "evaluation_command": "python scripts/evaluate_hf_tokenizer.py --tokenizer results/resubmission/final/tokenizer.json --corpus-dir data/faithful --output results/resubmission/final/metrics.json",
        "training_command": "python scripts/run_threshold_search.py",
    }
    try:
        provenance["git_commit"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        )
    except Exception:
        provenance["git_commit"] = "unknown"
    (FINAL / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    print(f"\nTrained {trained_new} new tokenizers ({len(candidates)} total measured)")
    print(f"Class A: {selection['class_a_count']} | B: {selection['class_b_count']} | C: {selection['class_c_count']}")
    print(f"Winner {winner.experiment_id} class={winner.constraint_class} weights={winner.weights.as_dict()}")
    print(f"  EN={winner.fertilities['en']:.4f} HI={winner.fertilities['hi']:.4f} adjusted={winner.final_grade:.2f}")
    print(f"  reason: {selection['selection_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
