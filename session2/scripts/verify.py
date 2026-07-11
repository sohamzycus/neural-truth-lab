#!/usr/bin/env python3
"""Independent verification of SamaBPE tokenizer and score."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.bpe import BPETokenizer
from samabpe.scoring import compute_score
from samabpe.strategies import EN_MAX_FERTILITY, LANGS, VOCAB_BUDGET
from samabpe.word_units import count_word_units

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "frozen"
RESULTS = ROOT / "results"


def main() -> int:
    tok_path = RESULTS / "tokenizer.json"
    if not tok_path.exists():
        print("ERROR: results/tokenizer.json not found. Run scripts/train.py first.")
        return 1

    tok = BPETokenizer.load(tok_path)
    corpora = {lang: (DATA / f"{lang}_india.txt").read_text(encoding="utf-8") for lang in LANGS}

    rows = []
    fertilities = {}
    for lang in LANGS:
        text = corpora[lang]
        wu = count_word_units(text)
        tokens = tok.count_tokens(text)
        x = tokens / wu if wu else float("inf")
        fertilities[lang] = x
        rows.append((lang, len(text), wu, tokens, x))

    score_data = compute_score(fertilities)
    vocab_ok = tok.vocab_size <= VOCAB_BUDGET
    en_ok = fertilities["en"] <= EN_MAX_FERTILITY

    print("=" * 72)
    print("SamaBPE Verification")
    print("=" * 72)
    print(f"{'Lang':<6} {'Chars':>8} {'WordUnits':>10} {'Tokens':>8} {'X':>8}")
    print("-" * 72)
    for lang, chars, wu, tokens, x in rows:
        print(f"{lang:<6} {chars:>8} {wu:>10} {tokens:>8} {x:>8.4f}")
    print("-" * 72)
    print(f"Sorted X: {[round(v, 4) for v in score_data['sorted_x']]}")
    print(f"X_min: {score_data['x_min']:.4f}")
    print(f"X_max: {score_data['x_max']:.4f}")
    print(f"Max-Min gap: {score_data['max_min_gap']:.4f}")
    print(f"Score: {score_data['score']:.4f}")
    print(f"Vocabulary size: {tok.vocab_size} (limit {VOCAB_BUDGET}) -> {'PASS' if vocab_ok else 'FAIL'}")
    print(f"English X <= {EN_MAX_FERTILITY}: {fertilities['en']:.4f} -> {'PASS' if en_ok else 'FAIL'}")
    print("=" * 72)

    out = {
        "verified": vocab_ok and en_ok,
        "vocabulary_size": tok.vocab_size,
        "languages": {
            lang: {
                "characters": chars,
                "word_units": wu,
                "tokens": tokens,
                "fertility": x,
            }
            for lang, chars, wu, tokens, x in rows
        },
        "sorted_x": score_data["sorted_x"],
        "x_min": score_data["x_min"],
        "x_max": score_data["x_max"],
        "max_min_gap": score_data["max_min_gap"],
        "score": score_data["score"],
        "english_constraint_pass": en_ok,
        "vocab_constraint_pass": vocab_ok,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "verification.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    assert vocab_ok, f"Vocabulary {tok.vocab_size} exceeds {VOCAB_BUDGET}"
    assert en_ok, f"English fertility {fertilities['en']} exceeds {EN_MAX_FERTILITY}"
    print("All assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
