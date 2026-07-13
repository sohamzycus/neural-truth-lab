"""Visible-character round-trip regression suite (150+ deterministic cases)."""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tokenizers import Tokenizer

from samabpe.adversarial_unicode import _classify_failure, roundtrip_case
from samabpe.evaluator_contract import LANGS, REVIEWER_SAMPLE, visible_nfkc, visible_non_whitespace

STRESS_STRING = "«unicode» — em-dash … ellipsis"

ASCII_PUNCT = list('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
TYPO_PUNCT = list("‘’“”‚„«»‹›–—―…′″•·‧※")
CURRENCY = list("$€£¥₹₩₽₿¢")
MATH = list("+−×÷=≠<>≤≥±∞√∑∏∫≈≡∂∆")
ARROWS = list("←→↑↓↔⇒⇐⇔↗↘↙↖")
COMMON_SYMBOLS = list("©®™§¶†‡✓✔✗✘★☆♠♣♥♦⚠⚡☀☁☂☃☕")
GREEK = list("αβγδπΩΔλμ")
EMOJI = list("😀😃😂❤️👍🚀🌍🔥🎉💡🇮🇳")
INDIC_PUNCT = ["।", "॥"]

ADVERSARIAL_SENTENCES = [
    "Price: ₹1,428.50 — approximately €15.99.",
    "Warning ⚠: [India™](https://example.com?q=भारत&x=1)",
    "Math: 2×3=6, x≤10, ∞≠0.",
    "Weather: ☀→☁→☂.",
    "Emoji: India 🇮🇳 and rocket 🚀.",
    "Symbols: ©2026 Example™ — all rights reserved®.",
    "English हिन्दी తెలుగు বাংলা — four scripts, one tokenizer.",
]

URL_CASES = [
    "https://en.wikipedia.org/wiki/India",
    "https://example.com/search?q=भारत&lang=hi",
    "https://example.com/a_b-c?q=తెలుగు&x=1#section",
    "https://user@example.com/path?a=1&b=2",
]

MARKDOWN_CASES = [
    "[India](https://en.wikipedia.org/wiki/India)",
    "**bold** _italic_ `code`",
    "| Language | Fertility |\n|---|---:|\n| Hindi | 0.8297 |",
    "## Heading\n- list item\n1. numbered",
]

NUMBER_CASES = [
    "1,428,627,663",
    "₹1,428.50",
    "€15.99",
    "42,650.36",
    "50%",
    "-42",
    "1.5e10",
    "3.14159",
]

MIXED_SCRIPT = [
    "India भारत తెలుగు বাংলা",
    "English: India | हिन्दी: भारत | తెలుగు: భారతదేశం | বাংলা: ভারত",
]


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
    flags = _classify_failure(text, dec, strict_ok=strict_ok, nfkc_ok=nfkc_ok, unk_used=unk_used)
    stored_input = text if len(text) <= 500 else f"{text[:200]}…[{len(text)} chars total]"
    failure_class = None
    if not nfkc_ok:
        if unk_used and flags["visible_deletion"]:
            failure_class = "unk_deletion"
        elif flags["visible_substitution"]:
            failure_class = "visible_substitution"
        else:
            failure_class = "other"
    elif not strict_ok:
        failure_class = "nfkc_normalization"
    return {
        "category": category,
        "input": stored_input,
        "input_length": len(text),
        "normalized_nfkc": unicodedata.normalize("NFKC", text)[:500],
        "tokens": enc.tokens if len(enc.tokens) <= 50 else enc.tokens[:50] + [f"…+{len(enc.tokens)-50} more"],
        "token_ids": enc.ids if len(enc.ids) <= 50 else enc.ids[:50] + [f"…+{len(enc.ids)-50} more"],
        "decoded": dec if len(dec) <= 500 else f"{dec[:200]}…[{len(dec)} chars total]",
        "visible_original": vo[:200],
        "visible_decoded": vd[:200],
        "strict_pass": strict_ok,
        "nfkc_pass": nfkc_ok,
        "unk_emitted": unk_used,
        "visible_deletion": flags["visible_deletion"],
        "visible_substitution": flags["visible_substitution"],
        "normalization_only_difference": flags["normalization_only_difference"],
        "char_diffs": [] if strict_ok else _char_diff(text, dec)[:20],
        "failure_class": failure_class,
    }


def _add_isolated(cases: list[dict[str, Any]], tok: Tokenizer, chars: list[str], category: str) -> None:
    seen: set[str] = set()
    for ch in chars:
        if ch in seen:
            continue
        seen.add(ch)
        label = f"{category}_U+{ord(ch):04X}"
        if category.endswith("_punct") or category in {"ascii_punct", "typographic_punct", "currency", "math", "arrows", "common_symbols", "greek", "emoji", "indic_punct"}:
            cases.append(_case(tok, ch, f"{category}_isolated"))
            cases.append(_case(tok, f"A{ch}B", f"{category}_in_context"))
        else:
            cases.append(_case(tok, ch, category))


def build_regression_cases(tok: Tokenizer, corpora: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(cat: str, text: str) -> None:
        cases.append(_case(tok, text, cat))

    add("reviewer", REVIEWER_SAMPLE)
    add("stress", STRESS_STRING)

    _add_isolated(cases, tok, ASCII_PUNCT, "ascii_punct")
    _add_isolated(cases, tok, TYPO_PUNCT, "typographic_punct")
    _add_isolated(cases, tok, CURRENCY, "currency")
    _add_isolated(cases, tok, MATH, "math")
    _add_isolated(cases, tok, ARROWS, "arrows")
    _add_isolated(cases, tok, COMMON_SYMBOLS, "common_symbols")
    _add_isolated(cases, tok, GREEK, "greek")
    _add_isolated(cases, tok, EMOJI, "emoji")
    _add_isolated(cases, tok, INDIC_PUNCT, "indic_punct")

    for text in URL_CASES:
        add("url", text)
    for text in MARKDOWN_CASES:
        add("markdown", text)
    for text in NUMBER_CASES:
        add("numbers", text)
    for text in MIXED_SCRIPT:
        add("mixed_script", text)
    for text in ADVERSARIAL_SENTENCES:
        add("adversarial_sentence", text)

    add("ascii_apostrophe", "don't")
    add("typographic_apostrophe", "don\u2019t")
    add("guillemets", "\u00abunicode\u00bb")
    add("currency_mix", "\u20b9100 and $50")
    add("email_at", "email@test.org")

    for lang in LANGS:
        text = corpora[lang]["text"]
        add(f"corpus_{lang}_full", text)
        for line in text.splitlines():
            if any(ord(c) > 127 for c in line) and len(line.strip()) > 40:
                add(f"corpus_{lang}_sample", line[:300])
                break

    return cases


def build_visible_character_report(tok: Tokenizer, corpora: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cases = build_regression_cases(tok, corpora)
    strict_pass = sum(1 for c in cases if c["strict_pass"])
    nfkc_pass = sum(1 for c in cases if c["nfkc_pass"])
    failures = [c for c in cases if not c["nfkc_pass"]]
    critical = [c for c in cases if c["failure_class"] == "unk_deletion"]
    nfkc_only = [c for c in cases if c["failure_class"] == "nfkc_normalization"]
    substitutions = [c for c in cases if c["failure_class"] == "visible_substitution"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluator_contract": {
            "canonical": "visible_non_whitespace(NFKC(decoded)) == visible_non_whitespace(NFKC(original))",
            "source_file": "python/samabpe/evaluator_contract.py",
            "function": "verify_roundtrip",
        },
        "stress_string": STRESS_STRING,
        "total_cases": len(cases),
        "strict_passed": strict_pass,
        "strict_failed": len(cases) - strict_pass,
        "nfkc_passed": nfkc_pass,
        "nfkc_failed": len(cases) - nfkc_pass,
        "critical_unk_deletion_failures": len(critical),
        "visible_substitution_failures": len(substitutions),
        "nfkc_only_strict_failures": len(nfkc_only),
        "submission_blocker": len(critical) > 0,
        "cases": cases,
        "failure_summary": [
            {
                "category": c["category"],
                "input": c["input"][:80],
                "failure_class": c["failure_class"],
                "unk_emitted": c["unk_emitted"],
                "visible_deletion": c["visible_deletion"],
            }
            for c in failures
        ],
    }


def write_visible_character_report(tok_path: Path, corpora: dict[str, dict[str, Any]], out_path: Path) -> dict[str, Any]:
    tok = Tokenizer.from_file(str(tok_path))
    report = build_visible_character_report(tok, corpora)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
