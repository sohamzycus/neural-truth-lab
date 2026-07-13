#!/usr/bin/env python3
"""Export playground parity fixtures from authoritative submission encoder."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
TOK = ROOT / "submission" / "tokenizer.json"
OUT = ROOT / "web" / "public" / "data" / "playground_parity.json"
GATE_CASES_OUT = ROOT / "results" / "gate-playground-cases.json"

# Required gate cases + legacy coverage cases
SAMPLES = [
    "India's population is 1,428,627,663.",
    "भारत एक विशाल देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "India भारत తెలుగు বাংলা",
    "https://en.wikipedia.org/wiki/India",
    "[India](https://en.wikipedia.org/wiki/India)",
    "don't can't won't",
    "1,428,627,663.50",
    "(parentheses) [brackets] {braces}",
    "pipe | underscore _ test",
    "colon: semicolon;",
    "path/to/file?x=1&y=2#anchor",
    "«unicode» — em-dash … ellipsis",
    "EN हिंदी తెలుగు বাংলা mixed",
    "word   with   repeated   spaces",
    "Table | Header | Value",
    "## Markdown heading",
    "COVID-19 pandemic",
    "₹100 and $50",
    "see https://example.com/path for info",
    "India",
    "भारत",
    "తెలుగు",
    "বাংলা",
    "India भारत భారతదేశం ভারত",
    "India is a diverse country.",
    "भारत एक विविध देश है।",
    "mixed EN हिंदी తెలుగు বাংলা text",
]


def main() -> int:
    if not TOK.exists():
        print(f"Missing {TOK}")
        return 1
    tok = Tokenizer.from_file(str(TOK))
    cases = []
    for text in SAMPLES:
        enc = tok.encode(text)
        dec = tok.decode(enc.ids)
        cases.append(
            {
                "text": text,
                "tokens": enc.tokens,
                "ids": enc.ids,
                "count": len(enc.ids),
                "decoded": dec,
            }
        )
    payload = {
        "tokenizer_sha256": hashlib.sha256(TOK.read_bytes()).hexdigest(),
        "cases": cases,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    GATE_CASES_OUT.parent.mkdir(parents=True, exist_ok=True)
    GATE_CASES_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(cases)} parity cases → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
