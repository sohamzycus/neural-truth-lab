#!/usr/bin/env python3
"""Analyze vocabulary composition and corpus utilization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from tokenizers import Tokenizer

from samabpe.submission_audit import (
    analyze_vocabulary,
    analyze_vocabulary_utilization,
    load_submission_corpora,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final-audit"
TOK = ROOT / "submission" / "tokenizer.json"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(TOK))
    corpora = load_submission_corpora()
    texts = {lang: corpora[lang]["text"] for lang in corpora}
    comp = analyze_vocabulary(TOK)
    util = analyze_vocabulary_utilization(tok, texts)
    (OUT / "vocabulary_composition.json").write_text(json.dumps(comp, indent=2), encoding="utf-8")
    (OUT / "vocabulary_utilization.json").write_text(json.dumps(util, indent=2), encoding="utf-8")
    print(json.dumps({"composition": comp, "utilization": util}, indent=2))
    return 0 if comp["sum_matches_vocab_size"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
