#!/usr/bin/env python3
"""Reproduce tokenizer training for submission package."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "python"))

from samabpe.hf_bpe_trainer import DEFAULT_WEIGHTS, load_faithful_corpora, train_hf_bpe  # noqa: E402


def main() -> int:
    corpus_dir = HERE / "corpus"
    corpora = load_faithful_corpora(corpus_dir)
    out = HERE / "tokenizer.json"
    tok, meta = train_hf_bpe(corpora, weights=DEFAULT_WEIGHTS, output_path=out)
    print(json.dumps(meta, indent=2))
    print(f"Saved {out} vocab={tok.get_vocab_size(with_added_tokens=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
