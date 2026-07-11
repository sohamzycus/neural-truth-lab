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
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "frozen"
RESULTS = ROOT / "results"
PUBLIC = ROOT / "web" / "public" / "data" / "results"


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
    stats = to_stats_json(result)
    manifest = to_verification_manifest(result)

    # Load vocab allocation from training artefact if present (non-score metadata)
    alloc_path = RESULTS / "vocab_allocation.json"
    if alloc_path.exists():
        stats["vocab_allocation"] = json.loads(alloc_path.read_text(encoding="utf-8"))
        stats["vocab_attribution"] = json.loads(alloc_path.read_text(encoding="utf-8"))

    (RESULTS / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    (RESULTS / "verification_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (RESULTS / "verification.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    (PUBLIC / "verification_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    assert result.vocab_pass, f"Vocabulary {result.vocabulary_size} exceeds {VOCAB_BUDGET}"
    assert result.english_pass, f"English fertility {result.fertilities['en']} exceeds {EN_MAX_FERTILITY}"
    print("\nAll assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
