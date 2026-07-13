#!/usr/bin/env python3
"""Minimal executable encoder for the submitted Hugging Face BPE tokenizer."""

from __future__ import annotations

import sys
from pathlib import Path

from tokenizers import Tokenizer


class SamaBPEEncoder:
    def __init__(self, tokenizer_path: str | Path = "tokenizer.json"):
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text).ids

    def encode_tokens(self, text: str) -> list[str]:
        return self.tokenizer.encode(text).tokens


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    text = " ".join(argv) if argv else "India भारत తెలుగు বাংলা"
    here = Path(__file__).resolve().parent
    tok_path = here / "tokenizer.json"
    if not tok_path.exists():
        tok_path = here.parent / "results" / "tokenizer_hf.json"
    enc = SamaBPEEncoder(tok_path)
    tokens = enc.encode_tokens(text)
    ids = enc.encode(text)
    print("Input:")
    print(text)
    print("\nTokens:")
    print(tokens)
    print("\nToken IDs:")
    print(ids)
    print("\nToken count:")
    print(len(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
