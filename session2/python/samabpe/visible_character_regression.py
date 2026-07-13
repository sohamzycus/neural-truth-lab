"""Visible-character round-trip regression suite."""

from __future__ import annotations

import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tokenizers import Tokenizer

from samabpe.evaluator_contract import LANGS, REVIEWER_SAMPLE, visible_nfkc, visible_non_whitespace

STRESS_STRING = "«unicode» — em-dash … ellipsis"


def _char_diff(orig: str, dec: str) -> list[dict[str, Any]]:
    vo = visible_non_whitespace(orig)
    vd = visible_non_whitespace(dec)
    diffs: list[dict[str, Any]] = []
    maxlen = max(len(vo), len(vd))
    for i in range(maxlen):
        a = vo[i] if i < len(vo) else None
        b = vd[i] if i < len(vd) else None
        if a != b:
            diffs.append(
                {
                    "index": i,
                    "original": a,
                    "decoded": b,
                    "original_cp": f"U+{ord(a):04X}" if a else None,
                    "decoded_cp": f"U+{ord(b):04X}" if b else None,
                }
            )
    # multiset extras
    from collections import Counter

    for ch, n in (Counter(vo) - Counter(vd)).items():
        if not any(d.get("original") == ch for d in diffs):
            diffs.append({"original": ch, "decoded": None, "original_cp": f"U+{ord(ch):04X}", "count_lost": n})
    return diffs


def _case(tok: Tokenizer, text: str, category: str) -> dict[str, Any]:
    enc = tok.encode(text)
    dec = tok.decode(enc.ids)
    vo, vd = visible_non_whitespace(text), visible_non_whitespace(dec)
    strict_ok = vo == vd
    nfkc_ok = visible_nfkc(dec) == visible_nfkc(text)
    unk_used = "<unk>" in enc.tokens
    stored_input = text if len(text) <= 500 else f"{text[:200]}…[{len(text)} chars total]"
    vo_store = vo if len(vo) <= 200 else f"{vo[:100]}…[{len(vo)} chars]"
    vd_store = vd if len(vd) <= 200 else f"{vd[:100]}…[{len(vd)} chars]"
    return {
        "category": category,
        "input": stored_input,
        "input_length": len(text),
        "normalized_nfkc": unicodedata.normalize("NFKC", text)[:500],
        "tokens": enc.tokens if len(enc.tokens) <= 50 else enc.tokens[:50] + [f"…+{len(enc.tokens)-50} more"],
        "token_ids": enc.ids if len(enc.ids) <= 50 else enc.ids[:50] + [f"…+{len(enc.ids)-50} more"],
        "decoded": dec if len(dec) <= 500 else f"{dec[:200]}…[{len(dec)} chars total]",
        "visible_original": vo_store,
        "visible_decoded": vd_store,
        "strict_pass": strict_ok,
        "nfkc_pass": nfkc_ok,
        "unk_emitted": unk_used,
        "char_diffs": [] if strict_ok else _char_diff(text, dec)[:20],
        "failure_class": (
            None
            if strict_ok
            else ("unk_deletion" if unk_used else "nfkc_normalization" if nfkc_ok else "other")
        ),
    }


def build_regression_cases(tok: Tokenizer, corpora: dict[str, str]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(cat: str, text: str) -> None:
        cases.append(_case(tok, text, cat))

    add("reviewer", REVIEWER_SAMPLE)
    add("stress", STRESS_STRING)
    add("ascii_apostrophe", "don't")
    add("typographic_apostrophe", "don\u2019t")
    add("double_quotes", '"hello"')
    add("typographic_quotes", "\u201chello\u201d")
    add("guillemets", "\u00abunicode\u00bb")
    add("comma", "a,b")
    add("period", "a.b")
    add("colon", "a:b")
    add("semicolon", "a;b")
    add("hyphen", "a-b")
    add("en_dash", "a\u2013b")
    add("em_dash", "a\u2014b")
    add("ellipsis", "a\u2026b")
    add("parens", "(a)")
    add("brackets", "[a]")
    add("braces", "{a}")
    add("pipe", "a|b")
    add("slash", "a/b")
    add("backslash", "a\\b")
    add("underscore", "a_b")
    add("hash", "#tag")
    add("ampersand", "a&b")
    add("percent", "50%")
    add("plus", "a+b")
    add("equals", "a=b")
    add("question", "a?")
    add("exclamation", "a!")
    add("at_sign", "email@test.org")
    add("rupee", "\u20b9100")
    add("euro", "\u20ac50")
    add("pound", "\u00a310")
    add("url", "https://en.wikipedia.org/wiki/India")
    add("url_with_at", "https://user@example.com/path")
    add("markdown_link", "[India](https://en.wikipedia.org/wiki/India)")
    add("number_separators", "1,428,627,663.")
    add("mixed_script", "India \u092d\u093e\u0930\u0924 \u0c24\u0c46\u0c32\u0c41\u0c17\u0c41 \u09ac\u09be\u0982\u09b2\u09be")
    add("currency_mix", "\u20b9100 and $50")

    # Representative lines from frozen corpora (first line with each rare char class)
    for lang in LANGS:
        text = corpora[lang]
        add(f"corpus_{lang}_full", text)
        for line in text.splitlines():
            if any(ord(c) > 127 for c in line) and len(line.strip()) > 40:
                add(f"corpus_{lang}_sample", line[:300])
                break

    return cases


def build_visible_character_report(tok: Tokenizer, corpora: dict[str, str]) -> dict[str, Any]:
    cases = build_regression_cases(tok, corpora)
    strict_pass = sum(1 for c in cases if c["strict_pass"])
    nfkc_pass = sum(1 for c in cases if c["nfkc_pass"])
    failures = [c for c in cases if not c["strict_pass"]]
    critical = [c for c in failures if c["failure_class"] == "unk_deletion"]
    nfkc_only = [c for c in failures if c["failure_class"] == "nfkc_normalization"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stress_string": STRESS_STRING,
        "total_cases": len(cases),
        "strict_passed": strict_pass,
        "strict_failed": len(cases) - strict_pass,
        "nfkc_passed": nfkc_pass,
        "nfkc_failed": len(cases) - nfkc_pass,
        "critical_unk_deletion_failures": len(critical),
        "nfkc_only_strict_failures": len(nfkc_only),
        "cases": cases,
        "failure_summary": [
            {
                "category": c["category"],
                "input": c["input"][:80],
                "failure_class": c["failure_class"],
                "unk_emitted": c["unk_emitted"],
            }
            for c in failures
        ],
    }


def write_visible_character_report(tok_path: Path, corpora: dict[str, str], out_path: Path) -> dict[str, Any]:
    tok = Tokenizer.from_file(str(tok_path))
    report = build_visible_character_report(tok, corpora)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
