#!/usr/bin/env python3
"""Generate verified submission data for UI and audit artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.submission_audit import build_verified_submission

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "final-audit"
WEB_OUT = ROOT / "web" / "public" / "data" / "verifiedSubmission.json"


def main() -> int:
    verified = build_verified_submission()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "verified_submission.json").write_text(
        json.dumps(verified, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "fertility_examples.json").write_text(
        json.dumps(verified["fertilityExamples"], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "tokenizer_architecture.json").write_text(
        json.dumps(verified["tokenizer"], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "vocabulary_composition.json").write_text(
        json.dumps(verified["vocabularyComposition"], indent=2), encoding="utf-8"
    )
    (OUT_DIR / "vocabulary_utilization.json").write_text(
        json.dumps(verified["vocabularyUtilization"], indent=2), encoding="utf-8"
    )
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT.write_text(json.dumps(verified, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {WEB_OUT}")
    if not verified["tokenizer"]["verified"]:
        print("ERROR: tokenizer architecture not verified")
        return 1
    if not verified["vocabularyComposition"]["sum_matches_vocab_size"]:
        print("ERROR: vocabulary composition sum mismatch")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
