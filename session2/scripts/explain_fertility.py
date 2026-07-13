#!/usr/bin/env python3
"""Explain faithful-unit fertility for a text string."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from tokenizers import Tokenizer

from samabpe.evaluator_contract import REVIEWER_SAMPLE
from samabpe.submission_audit import explain_fertility

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOK = ROOT / "submission" / "tokenizer.json"


def main() -> int:
    p = argparse.ArgumentParser(description="Explain fertility for input text")
    p.add_argument("text", nargs="?", default=REVIEWER_SAMPLE)
    p.add_argument("--tokenizer", type=Path, default=DEFAULT_TOK)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    tok = Tokenizer.from_file(str(args.tokenizer))
    out = explain_fertility(tok, args.text)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    print("Original text:")
    print(out["original_text"])
    print("\nFaithful units:")
    print(out["faithful_units"])
    print(f"\nFaithful-unit count: {out['faithful_unit_count']}")
    print("\nBPE tokens:")
    print(out["bpe_tokens"])
    print("\nToken IDs:")
    print(out["token_ids"])
    print(f"\nBPE token count: {out['bpe_token_count']}")
    print("\nDecoded text:")
    print(out["decoded_text"])
    status = "PASS" if out["visible_roundtrip_nfkc"] else "FAIL"
    print(f"\nVisible round-trip status: {status}")
    print(f"Fertility = {out['bpe_token_count']} / {out['faithful_unit_count']} = {out['fertility']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
