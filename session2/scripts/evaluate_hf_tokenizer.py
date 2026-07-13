#!/usr/bin/env python3
"""Canonical Hugging Face tokenizer evaluator — fresh metrics only."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from tokenizers import Tokenizer

from samabpe.evaluator_contract import LANGS, count_wordish_units, compute_evaluator_metrics
from samabpe.hf_bpe_trainer import sha256_file

ROOT = Path(__file__).resolve().parents[1]


def evaluate(tokenizer_path: Path, corpus_dir: Path) -> dict:
    tok = Tokenizer.from_file(str(tokenizer_path))
    languages = {}
    token_counts = {}
    wordish_counts = {}
    corpus_sha = {}
    for lang in LANGS:
        text = (corpus_dir / f"{lang}.faithful.md").read_text(encoding="utf-8")
        corpus_sha[lang] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        wu = count_wordish_units(text)
        tc = len(tok.encode(text).ids)
        wordish_counts[lang] = wu
        token_counts[lang] = tc
        languages[lang] = {
            "wordish_units": wu,
            "tokens": tc,
            "fertility": tc / wu if wu else float("inf"),
        }
    metrics = compute_evaluator_metrics(token_counts, wordish_counts)
    vocab_size = tok.get_vocab_size(with_added_tokens=True)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tokenizer": {
            "format": "huggingface-tokenizers",
            "path": str(tokenizer_path),
            "vocab_size": vocab_size,
            "sha256": sha256_file(tokenizer_path),
            "vocab_constraint_pass": vocab_size <= 10_000,
        },
        "corpus_dir": str(corpus_dir),
        "corpus_sha256": corpus_sha,
        "languages": languages,
        "scoring": {
            "x_min": metrics.x_min,
            "x_max": metrics.x_max,
            "spread": metrics.spread,
            "raw_score": metrics.raw_score,
            "hindi_penalty": metrics.hindi_penalty,
            "final_grade": metrics.final_grade,
            "adjusted_score": metrics.final_grade,
        },
        "token_counts": metrics.token_counts,
        "wordish_counts": metrics.wordish_counts,
        "fertilities": metrics.fertilities,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tokenizer", type=Path, required=True)
    p.add_argument("--corpus-dir", type=Path, default=ROOT / "data" / "faithful")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if not args.tokenizer.exists():
        print(f"ERROR: missing {args.tokenizer}")
        return 1
    if not (args.corpus_dir / "en.faithful.md").exists():
        print(f"ERROR: missing faithful corpus in {args.corpus_dir}")
        return 1
    result = evaluate(args.tokenizer, args.corpus_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"  final_grade={result['scoring']['final_grade']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
