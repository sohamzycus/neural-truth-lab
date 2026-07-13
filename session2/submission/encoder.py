#!/usr/bin/env python3
"""Standalone encoder/decode CLI for submission tokenizer."""

from __future__ import annotations

import sys
from pathlib import Path

from tokenizers import Tokenizer

from evaluator_contract import REVIEWER_SAMPLE, verify_roundtrip

TOKENIZER_PATH = Path(__file__).parent / "tokenizer.json"


class SamaBPEEncoder:
    def __init__(self, tokenizer_path: Path | str = TOKENIZER_PATH):
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text).ids

    def encode_tokens(self, text: str) -> list[str]:
        return self.tokenizer.encode(text).tokens

    def decode(self, token_ids: list[int]) -> str:
        return self.tokenizer.decode(token_ids)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    text = " ".join(argv) if argv else REVIEWER_SAMPLE
    enc = SamaBPEEncoder()
    tokens = enc.encode_tokens(text)
    ids = enc.encode(text)
    decoded = enc.decode(ids)
    ok = verify_roundtrip(enc.tokenizer, text)
    print("Original:")
    print(text)
    print("\nTokens:")
    print(tokens)
    print("\nToken IDs:")
    print(ids)
    print("\nDecoded:")
    print(decoded)
    print("\nVisible round-trip:")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
