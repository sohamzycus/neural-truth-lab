"""Adversarial Unicode coverage: corpus scan, block probe, byte-fallback check."""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import regex
from tokenizers import Tokenizer

from samabpe.evaluator_contract import LANGS, FAITHFUL_UNIT_RE, visible_nfkc, visible_non_whitespace

# Representative visible chars per Unicode block (deterministic, not exhaustive)
UNICODE_BLOCK_SAMPLES: dict[str, list[str]] = {
    "Basic_Latin": list("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"),
    "Latin_1_Supplement": list("¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁ"),
    "General_Punctuation": list("‘’‚‛“”„‟†‡•…‰‱′″‴‹›⁇"),
    "Currency_Symbols": list("$€£¥₹₩₽₿¢"),
    "Letterlike_Symbols": list("№™℠℗℡Ω℮ℯ"),
    "Arrows": list("←↑→↓↔↕↖↗↘↙⇐⇒⇔"),
    "Mathematical_Operators": list("+−×÷=≠<≤>≥±∞√∑∏∫≈≡∂∆"),
    "Miscellaneous_Technical": list("⌂⌘⌛⌥⏎⏏⏩⏪"),
    "Enclosed_Alphanumerics": list("①②③④⑤"),
    "Geometric_Shapes": list("■□▲△●○◆◇"),
    "Miscellaneous_Symbols": list("☀☁☂☃★☆♠♣♥♦⚠⚡☕"),
    "Dingbats": list("✁✂✃✄✅✓✔✗✘"),
    "Devanagari": list("।॥"),
    "Bengali": list("।"),
    "Telugu": list("।"),
    "Greek_and_Coptic": list("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔ"),
    "Emoji_sample": list("😀😃😂❤👍🚀🌍🔥🎉💡🇮🇳"),
}


def corpus_texts(corpora: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {lang: corpora[lang]["text"] for lang in LANGS}


def extract_corpus_visible_symbols(corpora: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Unique visible non-letter/non-mark/non-number chars from frozen corpora."""
    symbols: dict[str, dict[str, Any]] = {}
    texts = corpus_texts(corpora)
    for lang, text in texts.items():
        for match in FAITHFUL_UNIT_RE.finditer(text):
            unit = match.group()
            for ch in unit:
                if regex.match(r"[\p{L}\p{M}\p{N}]", ch) or ch.isspace():
                    continue
                key = f"U+{ord(ch):04X}"
                if key not in symbols:
                    symbols[key] = {
                        "char": ch,
                        "codepoint": key,
                        "name": unicodedata.name(ch, "?"),
                        "languages": [],
                        "context_snippet": None,
                    }
                if lang not in symbols[key]["languages"]:
                    symbols[key]["languages"].append(lang)
                if symbols[key]["context_snippet"] is None:
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    symbols[key]["context_snippet"] = text[start:end].replace("\n", " ")
    return sorted(symbols.values(), key=lambda x: x["codepoint"])


def _chars_lost(orig: str, dec: str) -> list[str]:
    vo = visible_non_whitespace(orig)
    vd = visible_non_whitespace(dec)
    lost = list((Counter(vo) - Counter(vd)).elements())
    return lost


def _classify_failure(
    text: str,
    dec: str,
    *,
    strict_ok: bool,
    nfkc_ok: bool,
    unk_used: bool,
) -> dict[str, Any]:
    lost = _chars_lost(text, dec) if not strict_ok else []
    visible_deletion = bool(lost)
    visible_substitution = False
    normalization_only = False
    if not strict_ok and nfkc_ok:
        normalization_only = True
    elif not nfkc_ok and unk_used and visible_deletion:
        visible_substitution = False  # deletion via unk, not substitution
    elif not nfkc_ok and not unk_used:
        vo, vd = visible_non_whitespace(text), visible_non_whitespace(dec)
        if vo and vd and vo != vd:
            visible_substitution = True
    return {
        "strict_pass": strict_ok,
        "nfkc_pass": nfkc_ok,
        "unk_emitted": unk_used,
        "visible_deletion": visible_deletion,
        "visible_substitution": visible_substitution,
        "normalization_only_difference": normalization_only,
        "chars_lost": [f"U+{ord(c):04X}" for c in lost[:10]],
    }


def roundtrip_case(tok: Tokenizer, text: str, *, category: str, label: str = "") -> dict[str, Any]:
    enc = tok.encode(text)
    dec = tok.decode(enc.ids)
    vo, vd = visible_non_whitespace(text), visible_non_whitespace(dec)
    strict_ok = vo == vd
    nfkc_ok = visible_nfkc(dec) == visible_nfkc(text)
    unk_used = "<unk>" in enc.tokens
    flags = _classify_failure(text, dec, strict_ok=strict_ok, nfkc_ok=nfkc_ok, unk_used=unk_used)
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
        "label": label or text[:80],
        "input": text if len(text) <= 300 else f"{text[:120]}…[{len(text)} chars]",
        "tokens": enc.tokens[:30],
        "token_ids": enc.ids[:30],
        "decoded": dec if len(dec) <= 300 else f"{dec[:120]}…[{len(dec)} chars]",
        "failure_class": failure_class,
        **flags,
    }


def build_corpus_character_coverage(tok: Tokenizer, corpora: dict[str, dict[str, Any]]) -> dict[str, Any]:
    symbols = extract_corpus_visible_symbols(corpora)
    cases: list[dict[str, Any]] = []
    for sym in symbols:
        ch = sym["char"]
        cases.append(roundtrip_case(tok, ch, category="corpus_isolated", label=sym["codepoint"]))
        ctx = sym.get("context_snippet")
        if ctx:
            cases.append(roundtrip_case(tok, ctx, category="corpus_in_context", label=sym["codepoint"]))

    nfkc_pass = sum(1 for c in cases if c["nfkc_pass"])
    strict_pass = sum(1 for c in cases if c["strict_pass"])
    critical = [c for c in cases if c["failure_class"] == "unk_deletion"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "unique_visible_symbols_discovered": len(symbols),
        "symbols": symbols,
        "total_tested": len(cases),
        "strict_passes": strict_pass,
        "nfkc_visible_passes": nfkc_pass,
        "unk_occurrences": sum(1 for c in cases if c["unk_emitted"]),
        "deletions": sum(1 for c in cases if c["visible_deletion"]),
        "substitutions": sum(1 for c in cases if c["visible_substitution"]),
        "normalization_only_differences": sum(1 for c in cases if c["normalization_only_difference"]),
        "critical_unk_deletion_failures": len(critical),
        "submission_blocker": len(critical) > 0 or nfkc_pass < len(cases),
        "cases": cases,
    }


def _block_for_char(ch: str) -> str:
    cp = ord(ch)
    if cp <= 0x7F:
        return "Basic_Latin"
    if 0x80 <= cp <= 0xFF:
        return "Latin_1_Supplement"
    if 0x2000 <= cp <= 0x206F:
        return "General_Punctuation"
    if 0x20A0 <= cp <= 0x20CF:
        return "Currency_Symbols"
    if 0x2100 <= cp <= 0x214F:
        return "Letterlike_Symbols"
    if 0x2190 <= cp <= 0x21FF:
        return "Arrows"
    if 0x2200 <= cp <= 0x22FF:
        return "Mathematical_Operators"
    if 0x2300 <= cp <= 0x23FF:
        return "Miscellaneous_Technical"
    if 0x2460 <= cp <= 0x24FF:
        return "Enclosed_Alphanumerics"
    if 0x25A0 <= cp <= 0x25FF:
        return "Geometric_Shapes"
    if 0x2600 <= cp <= 0x26FF:
        return "Miscellaneous_Symbols"
    if 0x2700 <= cp <= 0x27BF:
        return "Dingbats"
    if 0x0900 <= cp <= 0x097F:
        return "Devanagari"
    if 0x0980 <= cp <= 0x09FF:
        return "Bengali"
    if 0x0C00 <= cp <= 0x0C7F:
        return "Telugu"
    if 0x0370 <= cp <= 0x03FF:
        return "Greek_and_Coptic"
    if cp >= 0x1F000:
        return "Emoji"
    return f"U+{cp:04X}"


def build_unicode_block_probe(tok: Tokenizer) -> dict[str, Any]:
    by_block: dict[str, list[dict[str, Any]]] = {}
    all_cases: list[dict[str, Any]] = []
    for block, chars in UNICODE_BLOCK_SAMPLES.items():
        deduped = list(dict.fromkeys(chars))
        block_cases = []
        for ch in deduped:
            c = roundtrip_case(tok, ch, category="unicode_block", label=f"{block}:{ch}")
            c["unicode_block"] = block
            block_cases.append(c)
            all_cases.append(c)
        by_block[block] = block_cases

    summary: dict[str, Any] = {}
    for block, cases in by_block.items():
        fails = [c for c in cases if not c["nfkc_pass"]]
        summary[block] = {
            "sampled": len(cases),
            "nfkc_pass": sum(1 for c in cases if c["nfkc_pass"]),
            "strict_pass": sum(1 for c in cases if c["strict_pass"]),
            "unk_deletions": sum(1 for c in fails if c["failure_class"] == "unk_deletion"),
            "nfkc_normalization_only": sum(1 for c in fails if c["failure_class"] == "nfkc_normalization"),
            "visible_substitution": sum(1 for c in fails if c["failure_class"] == "visible_substitution"),
            "other_failures": sum(1 for c in fails if c["failure_class"] == "other"),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Deterministic samples from common Unicode blocks — not universal coverage.",
        "total_probed": len(all_cases),
        "nfkc_passes": sum(1 for c in all_cases if c["nfkc_pass"]),
        "strict_passes": sum(1 for c in all_cases if c["strict_pass"]),
        "by_block": summary,
        "cases": all_cases,
    }


def build_byte_fallback_report(tok: Tokenizer, tok_path: Path) -> dict[str, Any]:
    import json as _json

    raw = _json.loads(tok_path.read_text(encoding="utf-8"))
    configured = bool(raw.get("model", {}).get("byte_fallback"))
    probes = [
        "«",
        "€",
        "×",
        "∞",
        "⚠",
        "😀",
        "🇮🇳",
        "A☃B",
        "\u024B",  # Latin Extended-B — not in seeded alphabet
    ]
    results = []
    byte_token_hits = 0
    unk_hits = 0
    nfkc_preserves = 0
    for s in probes:
        enc = tok.encode(s)
        dec = tok.decode(enc.ids)
        has_byte = any(t.startswith("<0x") or (len(t) == 1 and ord(t) < 256 and t not in s) for t in enc.tokens)
        has_unk = "<unk>" in enc.tokens
        if has_byte:
            byte_token_hits += 1
        if has_unk:
            unk_hits += 1
        if visible_nfkc(dec) == visible_nfkc(s):
            nfkc_preserves += 1
        results.append(
            {
                "input": s,
                "tokens": enc.tokens,
                "token_ids": enc.ids,
                "decoded": dec,
                "byte_tokens_used": has_byte,
                "unk_emitted": has_unk,
                "nfkc_pass": visible_nfkc(dec) == visible_nfkc(s),
                "visible_deletion": bool(_chars_lost(s, dec)),
            }
        )

    unseeded = [r for r in results if r["input"] == "\u024B"][0]
    if configured and byte_token_hits == 0 and unseeded["unk_emitted"]:
        verdict = "PARTIALLY EFFECTIVE"
        explanation = (
            "byte_fallback=True is configured but unseen visible characters still route to <unk> "
            "instead of byte tokens; preservation depends on initial_alphabet seeding, not byte fallback alone."
        )
    elif configured and byte_token_hits > 0:
        verdict = "YES — effective"
        explanation = "byte_fallback encodes unseen characters as byte tokens and round-trips under NFKC-visible contract."
    elif not configured:
        verdict = "NO — ineffective"
        explanation = "byte_fallback is not enabled in tokenizer.json."
    else:
        verdict = "PARTIALLY EFFECTIVE"
        explanation = "Alphabet seeding preserves targeted symbols; byte_fallback alone does not emit byte tokens for unseen Unicode."

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "byte_fallback_configured": configured,
        "verdict": verdict,
        "explanation": explanation,
        "probes": results,
        "byte_token_probe_count": byte_token_hits,
        "unk_probe_count": unk_hits,
        "nfkc_preservation_count": nfkc_preserves,
    }


def write_adversarial_artifacts(
    tok_path: Path,
    corpora: dict[str, dict[str, Any]],
    results_dir: Path,
) -> dict[str, Path]:
    tok = Tokenizer.from_file(str(tok_path))
    paths = {
        "corpus_coverage": results_dir / "final-corpus-character-coverage.json",
        "unicode_probe": results_dir / "final-unicode-block-probe.json",
        "byte_fallback": results_dir / "final-byte-fallback-check.json",
    }
    reports = {
        "corpus_coverage": build_corpus_character_coverage(tok, corpora),
        "unicode_probe": build_unicode_block_probe(tok),
        "byte_fallback": build_byte_fallback_report(tok, tok_path),
    }
    for key, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(reports[key], indent=2, ensure_ascii=False), encoding="utf-8")
    return paths
