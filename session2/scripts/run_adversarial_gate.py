#!/usr/bin/env python3
"""Adversarial Unicode submission gate — corpus coverage, block probe, byte fallback."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.adversarial_unicode import write_adversarial_artifacts
from samabpe.submission_audit import ROOT, SUBMISSION, load_submission_corpora
from samabpe.visible_character_regression import write_visible_character_report

RESULTS = ROOT / "results"


def main() -> int:
    corpora = load_submission_corpora()
    tok_path = SUBMISSION / "tokenizer.json"
    vis = write_visible_character_report(tok_path, corpora, RESULTS / "final-visible-character-roundtrip.json")
    paths = write_adversarial_artifacts(tok_path, corpora, RESULTS)

    corpus_cov = json.loads(paths["corpus_coverage"].read_text(encoding="utf-8"))
    probe = json.loads(paths["unicode_probe"].read_text(encoding="utf-8"))
    byte_fb = json.loads(paths["byte_fallback"].read_text(encoding="utf-8"))

    print("=== Adversarial Unicode Gate ===")
    print(f"Regression cases: {vis['total_cases']}")
    print(f"  NFKC pass: {vis['nfkc_passed']}/{vis['total_cases']}")
    print(f"  Strict pass: {vis['strict_passed']}/{vis['total_cases']}")
    print(f"  Critical unk deletions: {vis['critical_unk_deletion_failures']}")
    print(f"Corpus symbols: {corpus_cov['unique_visible_symbols_discovered']} unique, blocker={corpus_cov['submission_blocker']}")
    print(f"Unicode block probe: {probe['nfkc_passes']}/{probe['total_probed']} NFKC pass")
    print(f"Byte fallback: {byte_fb['verdict']}")

    blocker = (
        vis["critical_unk_deletion_failures"] > 0
        or vis.get("submission_blocker")
        or corpus_cov.get("submission_blocker")
    )
    return 1 if blocker else 0


if __name__ == "__main__":
    raise SystemExit(main())
