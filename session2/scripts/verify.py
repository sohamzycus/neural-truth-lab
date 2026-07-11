#!/usr/bin/env python3
"""Independent verification of SamaBPE tokenizer and score."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.strategies import EN_MAX_FERTILITY, VOCAB_BUDGET
from samabpe.verify_core import (
    run_verification,
    print_report,
    to_stats_json,
    to_verification_manifest,
    to_baseline_json,
    to_artefact_proof,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "frozen"
RESULTS = ROOT / "results"
PUBLIC = ROOT / "web" / "public" / "data" / "results"
BASELINE_PATH = RESULTS / "baseline_verification.json"
PRE_FINAL_BASELINE = RESULTS / "pre_final_baseline.json"
FINAL_PASS_BASELINE = RESULTS / "final_pass_baseline.json"

SYNC_TO_PUBLIC = (
    "stats.json",
    "verification_manifest.json",
    "artefact_proof.json",
    "final_pass_baseline.json",
    "one_tokenizer_proof.json",
    "final_boundary_analysis.json",
    "optimization_claim_audit.json",
    "objective_sensitivity.json",
    "final_score_search_trace.json",
)


def _read_winning_strategy() -> str | None:
    path = RESULTS / "strategy_comparison.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "strategies" in data:
        for s in data["strategies"]:
            if s.get("winner"):
                return s.get("id")
    return None


def main() -> int:
    tok_path = RESULTS / "tokenizer.json"
    if not tok_path.exists():
        print("ERROR: results/tokenizer.json not found. Run scripts/train.py first.")
        return 1

    result = run_verification(tok_path, DATA, winning_strategy=_read_winning_strategy())
    print_report(result)

    RESULTS.mkdir(parents=True, exist_ok=True)

    # Immutable baseline — written once only
    if not BASELINE_PATH.exists():
        baseline = to_baseline_json(result, tok_path)
        BASELINE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
        print(f"\nBaseline recorded → {BASELINE_PATH.name}")

    # Pre-final pass baseline — frozen before final optimization (phase 1)
    if not PRE_FINAL_BASELINE.exists():
        pre = to_baseline_json(result, tok_path)
        pre["label"] = "pre_final_optimization_pass"
        PRE_FINAL_BASELINE.write_text(json.dumps(pre, indent=2), encoding="utf-8")
        print(f"Pre-final baseline recorded → {PRE_FINAL_BASELINE.name}")

    # Final submission pass baseline — frozen once (phase 1)
    if not FINAL_PASS_BASELINE.exists():
        fp = to_baseline_json(result, tok_path)
        fp["label"] = "final_submission_hardening_pass"
        FINAL_PASS_BASELINE.write_text(json.dumps(fp, indent=2), encoding="utf-8")
        print(f"Final-pass baseline recorded → {FINAL_PASS_BASELINE.name}")

    artefact = to_artefact_proof(result, tok_path, ROOT)
    (RESULTS / "artefact_proof.json").write_text(json.dumps(artefact, indent=2), encoding="utf-8")

    stats = to_stats_json(result)
    manifest = to_verification_manifest(result)
    manifest["artefact_proof"] = artefact

    alloc_path = RESULTS / "vocab_allocation.json"
    if alloc_path.exists():
        stats["vocab_allocation"] = json.loads(alloc_path.read_text(encoding="utf-8"))
        stats["vocab_attribution"] = json.loads(alloc_path.read_text(encoding="utf-8"))

    audit_path = RESULTS / "optimization_audit.json"
    if audit_path.exists():
        stats["optimization_audit"] = json.loads(audit_path.read_text(encoding="utf-8"))

    (RESULTS / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    (RESULTS / "verification_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (RESULTS / "verification.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in SYNC_TO_PUBLIC:
        src = RESULTS / name
        if src.exists():
            (PUBLIC / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    assert result.vocab_pass, f"Vocabulary {result.vocabulary_size} exceeds {VOCAB_BUDGET}"
    assert result.english_pass, f"English fertility {result.fertilities['en']} exceeds {EN_MAX_FERTILITY}"
    if artefact.get("all_copies_byte_identical") is False:
        print("WARNING: Download copy SHA-256 mismatch — run npm run build:netlify and sync dist")
    print("\nAll assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
