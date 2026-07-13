#!/usr/bin/env python3
"""Export playground parity fixtures from authoritative submission encoder."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
TOK = ROOT / "submission" / "tokenizer.json"
OUT = ROOT / "web" / "public" / "data" / "playground_parity.json"

SAMPLES = [
    "India",
    "भारत",
    "తెలుగు",
    "বাংলা",
    "India भारत భారతదేశం ভারত",
    "India is a diverse country.",
    "भारत एक विविध देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "भारत India বাংলা తెలుగు",
    "see https://example.com/path for info",
    "India, Bharat! বাংলা | తెలుగు [link](url)",
    "１２３",
    "COVID-19 pandemic",
    "1,234,567",
    "New Delhi",
    "हिन्दी",
    "తెలుగు భాష",
    "কলকাতা",
    "mixed EN हिंदी తెలుగు বাংলা text",
    "The quick brown fox jumps over 42 lazy dogs.",
    "![image](https://upload.wikimedia.org/wikipedia/commons/a/a4/Flag_of_India.svg)",
    "Table | Header | Value",
    "संयुक्त अक्षर",
    "అచ్చులు",
    "যুক্তাক্ষর",
]


def main() -> int:
    if not TOK.exists():
        print(f"Missing {TOK}")
        return 1
    tok = Tokenizer.from_file(str(TOK))
    cases = []
    for text in SAMPLES:
        enc = tok.encode(text)
        cases.append({"text": text, "tokens": enc.tokens, "ids": enc.ids, "count": len(enc.ids)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "tokenizer_sha256": __import__("hashlib").sha256(TOK.read_bytes()).hexdigest(),
                "cases": cases,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(cases)} parity cases → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
