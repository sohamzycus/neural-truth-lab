#!/usr/bin/env python3
"""Independent evaluator — recomputes all metrics from tokenizer + faithful corpora."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

# Allow running from submission/ or session2/
HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "corpus").exists() else HERE.parent
sys.path.insert(0, str(ROOT / "python"))

from samabpe.evaluator_scoring import LANGS, compute_evaluator_metrics
from samabpe.evaluator_text import count_wordish_units
from samabpe.hf_bpe import count_tokens_hf, load_faithful_corpora


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(tokenizer_path: Path, corpus_dir: Path) -> dict:
    tok = Tokenizer.from_file(str(tokenizer_path))
    corpora = load_faithful_corpora(corpus_dir)
    token_counts = {lang: count_tokens_hf(tok, corpora[lang]) for lang in LANGS}
    wordish_counts = {lang: count_wordish_units(corpora[lang]) for lang in LANGS}
    metrics = compute_evaluator_metrics(token_counts, wordish_counts)
    vocab_size = tok.get_vocab_size(with_added_tokens=True)
    return {
        "tokenizer_path": str(tokenizer_path),
        "tokenizer_sha256": sha256_file(tokenizer_path),
        "vocabulary_size": vocab_size,
        "corpus_dir": str(corpus_dir),
        **metrics.to_dict(),
    }


def main() -> int:
    tok_path = HERE / "tokenizer.json"
    corpus_dir = HERE / "corpus"
    if not tok_path.exists():
        tok_path = ROOT / "results" / "tokenizer_hf.json"
    if not corpus_dir.exists():
        corpus_dir = ROOT / "corpus"
    if not tok_path.exists():
        print("ERROR: tokenizer.json not found")
        return 1
    if not (corpus_dir / "en.faithful.md").exists():
        print("ERROR: faithful corpora missing — run build_wiki_faithful_markdown.py")
        return 1

    result = evaluate(tok_path, corpus_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    metrics_path = HERE / "metrics.json"
    metrics_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {metrics_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
