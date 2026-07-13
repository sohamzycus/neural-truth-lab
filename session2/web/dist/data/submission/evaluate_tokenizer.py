#!/usr/bin/env python3
"""Standalone evaluator for reviewer reproduction."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from evaluator_contract import LANGS, count_wordish_units, compute_evaluator_metrics  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    tok_path = HERE / "tokenizer.json"
    corpus_dir = HERE / "corpus"
    if not tok_path.exists():
        print("ERROR: tokenizer.json not found")
        return 1
    tok = Tokenizer.from_file(str(tok_path))
    print("SamaBPE Evaluator-Compatible Verification")
    print("=" * 41)
    vocab_size = tok.get_vocab_size(with_added_tokens=True)
    sha = sha256_file(tok_path)
    print(f"\nTokenizer format: Hugging Face BPE")
    print(f"Vocabulary size: {vocab_size}")
    print(f"Tokenizer SHA-256: {sha}")

    token_counts = {}
    wordish_counts = {}
    labels = {"en": "English", "hi": "Hindi", "te": "Telugu", "bn": "Bengali"}
    for lang in LANGS:
        text = (corpus_dir / f"{lang}.faithful.md").read_text(encoding="utf-8")
        wu = count_wordish_units(text)
        tc = len(tok.encode(text).ids)
        wordish_counts[lang] = wu
        token_counts[lang] = tc
        fert = tc / wu
        print(f"\n{labels[lang]}")
        print(f"  Word-ish units: {wu}")
        print(f"  Encoded tokens: {tc}")
        print(f"  Fertility: {fert}")

    m = compute_evaluator_metrics(token_counts, wordish_counts)
    print(f"\nXmin: {m.x_min}")
    print(f"Xmax: {m.x_max}")
    print(f"Spread: {m.spread}")
    print(f"\nRaw score: {m.raw_score}")
    print(f"Hindi fertility: {m.fertilities['hi']}")
    print(f"Hindi penalty: {m.hindi_penalty:.4f}x")
    print(f"\nFINAL GRADE: {m.final_grade}")
    print(f"\nPASS: One standard executable tokenizer")
    print(f"PASS: Vocabulary <= 10000" if vocab_size <= 10000 else "FAIL: Vocabulary")
    print("PASS: Four complete faithful corpora encoded")

    out = {
        "tokenizer": {"format": "huggingface-tokenizers", "vocab_size": vocab_size, "sha256": sha},
        "languages": {
            lang: {
                "wordish_units": wordish_counts[lang],
                "tokens": token_counts[lang],
                "fertility": m.fertilities[lang],
            }
            for lang in LANGS
        },
        "scoring": {
            "x_min": m.x_min,
            "x_max": m.x_max,
            "spread": m.spread,
            "raw_score": m.raw_score,
            "hindi_penalty": m.hindi_penalty,
            "final_grade": m.final_grade,
        },
    }
    (HERE / "metrics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
