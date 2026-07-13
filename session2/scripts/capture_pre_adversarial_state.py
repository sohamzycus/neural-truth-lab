#!/usr/bin/env python3
"""Freeze tokenizer/metrics/parity state before adversarial gate changes."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.evaluator_contract import compute_evaluator_metrics, faithful_units
from samabpe.experiment_deep_check import run_deep_check
from samabpe.submission_audit import (
    ROOT,
    SUBMISSION,
    build_verified_submission,
    inspect_tokenizer_architecture,
    load_submission_corpora,
    sha256_file,
)
from tokenizers import Tokenizer

RESULTS = ROOT / "results"
OUT = RESULTS / "pre-adversarial-gate-state.json"


def _load_metrics() -> dict:
    p = SUBMISSION / "metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _fresh_metrics(tok: Tokenizer, corpora: dict) -> dict:
    token_counts = {lang: len(tok.encode(corpora[lang]["text"]).ids) for lang in corpora}
    unit_counts = {lang: faithful_units(corpora[lang]["text"]) for lang in corpora}
    return compute_evaluator_metrics(token_counts, unit_counts).to_dict()


def _parity_summary() -> dict:
    play = RESULTS / "final-playground-parity.json"
    art = RESULTS / "final-artifact-parity.json"
    out: dict = {}
    if play.exists():
        d = json.loads(play.read_text(encoding="utf-8"))
        out["playground"] = {
            "total_cases": d.get("total_cases"),
            "passed": d.get("passed"),
            "all_pass": d.get("all_pass"),
        }
    if art.exists():
        d = json.loads(art.read_text(encoding="utf-8"))
        out["artifact"] = {
            "all_tokenizer_copies_match": d.get("all_tokenizer_copies_match"),
            "all_corpus_copies_match": d.get("all_corpus_copies_match"),
            "submission_sha256": d.get("submission_tokenizer_sha256"),
        }
    return out


def main() -> int:
    corpora = load_submission_corpora()
    tok_path = SUBMISSION / "tokenizer.json"
    tok = Tokenizer.from_file(str(tok_path))
    arch = inspect_tokenizer_architecture(tok_path)
    metrics_file = _load_metrics()
    fresh = _fresh_metrics(tok, corpora)
    prov = json.loads((SUBMISSION / "provenance.json").read_text(encoding="utf-8")) if (SUBMISSION / "provenance.json").exists() else {}

    deep_path = RESULTS / "final-experiment-integrity-deep-check.json"
    exp_integrity = json.loads(deep_path.read_text(encoding="utf-8")) if deep_path.exists() else run_deep_check()

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Before-state snapshot for absolute final adversarial submission gate",
        "tokenizer_path": str(tok_path.relative_to(ROOT)),
        "tokenizer_sha256": sha256_file(tok_path),
        "tokenizer_type": arch.get("model_type"),
        "vocabulary_size": arch.get("vocab_size"),
        "normalizer": arch.get("normalizer"),
        "pretokenizer": arch.get("pretokenizer"),
        "decoder": arch.get("decoder"),
        "winner_weights": prov.get("weights", {}),
        "fertilities": fresh["fertilities"],
        "spread": fresh["spread"],
        "raw_score": fresh["raw_score"],
        "hindi_penalty": fresh["hindi_penalty"],
        "adjusted_self_score": fresh["adjusted_score"],
        "thresholds": fresh["thresholds"],
        "metrics_file": metrics_file,
        "corpus_hashes": {lang: corpora[lang]["sha256"] for lang in corpora},
        "playground_parity": _parity_summary().get("playground"),
        "artifact_parity": _parity_summary().get("artifact"),
        "experiment_integrity": {
            "verified_2570_claim": exp_integrity.get("verified_2570_claim"),
            "total_records": exp_integrity.get("total_records"),
            "unique_weight_configurations": exp_integrity.get("unique_weight_configurations"),
        },
        "hardening": prov.get("hardening"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"SHA: {state['tokenizer_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
