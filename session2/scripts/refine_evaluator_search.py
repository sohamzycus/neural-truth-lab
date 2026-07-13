#!/usr/bin/env python3
"""Focused refinement — push Hindi toward 1.2 while maximizing adjusted score."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.hf_bpe import evaluate_hf_tokenizer, load_faithful_corpora, train_hf_bpe

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "results" / "evaluator_candidates"
OUT = ROOT / "results" / "evaluator_refine_search.json"


def main() -> int:
    corpora = load_faithful_corpora(ROOT / "corpus")
    grids = {
        "en": [6, 8, 10, 12, 15],
        "hi": [4, 5, 6, 7, 8],
        "te": [4, 5, 6],
        "bn": [2, 3, 4],
    }
    results = []
    for en, hi, te, bn in itertools.product(*grids.values()):
        w = {"en": en, "hi": hi, "te": te, "bn": bn}
        path = CAND / f"refine_{en}_{hi}_{te}_{bn}.json"
        if path.exists():
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(path))
        else:
            tok = train_hf_bpe(corpora, weights=w, output_path=path)
        m = evaluate_hf_tokenizer(tok, corpora)
        results.append({"weights": w, **m.to_dict(), "path": str(path.relative_to(ROOT))})
    results.sort(key=lambda r: r["adjusted_score"], reverse=True)
    best = results[0]
    OUT.write_text(json.dumps({"candidates": results[:20], "best": best}, indent=2), encoding="utf-8")
    print(f"Best refine: {best['weights']} adj={best['adjusted_score']:.2f} hi={best['fertilities']['hi']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
