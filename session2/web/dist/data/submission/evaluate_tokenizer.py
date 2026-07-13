#!/usr/bin/env python3
"""Standalone faithful evaluator — recomputes all metrics from scratch."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

from evaluator_contract import (  # noqa: E402
    LANGS,
    REVIEWER_SAMPLE,
    compute_evaluator_metrics,
    faithful_units,
    verify_roundtrip,
)

HERE = Path(__file__).parent


def _verify_corpus_roundtrip(tok: Tokenizer, corpora: dict[str, str]) -> dict:
    result = {"reviewer_sample": verify_roundtrip(tok, REVIEWER_SAMPLE), "full_corpus": {}, "valid": True}
    for lang in LANGS:
        ok = verify_roundtrip(tok, corpora[lang])
        result["full_corpus"][lang] = ok
        if not ok:
            result["valid"] = False
    if not result["reviewer_sample"]:
        result["valid"] = False
    return result


def _load_corpora() -> dict[str, str]:
    out = {}
    for lang in LANGS:
        for ext in (".faithful.txt", ".faithful.md"):
            p = HERE / "corpus" / f"{lang}{ext}"
            if p.exists():
                out[lang] = p.read_text(encoding="utf-8")
                break
        else:
            raise FileNotFoundError(lang)
    return out


def main() -> int:
    tok_path = HERE / "tokenizer.json"
    if not tok_path.exists():
        print("ERROR: tokenizer.json not found")
        return 1
    tok = Tokenizer.from_file(str(tok_path))
    corpora = _load_corpora()

    print("SamaBPE Faithful Evaluator-Compatible Verification")
    print("=" * 49)
    vocab = tok.get_vocab_size(with_added_tokens=True)
    sha = hashlib.sha256(tok_path.read_bytes()).hexdigest()
    print(f"\nTokenizer format: Hugging Face BPE (NFKC + Metaspace)")
    print(f"Vocabulary size: {vocab}")
    print(f"Tokenizer SHA-256: {sha}")
    print(f"Decoder present: yes")

    enc = tok.encode(REVIEWER_SAMPLE)
    dec = tok.decode(enc.ids)
    reviewer_ok = verify_roundtrip(tok, REVIEWER_SAMPLE)
    print(f"\nReviewer regression sample:")
    print(f"  Input: {REVIEWER_SAMPLE}")
    print(f"  Decoded: {dec}")
    print(f"  Visible round-trip: {'PASS' if reviewer_ok else 'FAIL'}")

    rt = _verify_corpus_roundtrip(tok, corpora)
    labels = {"en": "English", "hi": "Hindi", "te": "Telugu", "bn": "Bengali"}
    token_counts = {}
    unit_counts = {}
    for lang in LANGS:
        text = corpora[lang]
        tc = len(tok.encode(text).ids)
        fu = faithful_units(text)
        token_counts[lang] = tc
        unit_counts[lang] = fu
        fert = tc / fu
        corpus_ok = rt["full_corpus"].get(lang, False)
        print(f"\n{labels[lang]}")
        print(f"  Faithful units: {fu}")
        print(f"  Encoded tokens: {tc}")
        print(f"  Fertility: {fert}")
        print(f"  Full corpus round-trip: {'PASS' if corpus_ok else 'FAIL'}")

    if not rt["valid"]:
        print("\nFAIL: Round-trip gate")
        return 1

    m = compute_evaluator_metrics(token_counts, unit_counts)
    print(f"\nSpread: {m.spread}")
    print(f"Raw score: {m.raw_score}")
    print(f"Hindi penalty: {m.hindi_penalty:.4f}x")
    print(f"Adjusted evaluator score: {m.final_grade}")
    print(f"\nEnglish < 1.2: {'PASS' if m.thresholds['en_under_1_2'] else 'FAIL'}")
    print(f"Hindi < 1.2: {'PASS' if m.thresholds['hi_under_1_2'] else 'FAIL'}")

    out = {
        "tokenizer": {"format": "huggingface-tokenizers", "vocab_size": vocab, "sha256": sha},
        "roundtrip": {"reviewer_sample": reviewer_ok, "full_corpus": rt["full_corpus"], "valid": rt["valid"]},
        "languages": {
            lang: {
                "faithful_units": unit_counts[lang],
                "tokens": token_counts[lang],
                "fertility": m.fertilities[lang],
            }
            for lang in LANGS
        },
        "thresholds": m.thresholds,
        "scoring": {
            "spread": m.spread,
            "raw_score": m.raw_score,
            "hindi_penalty": m.hindi_penalty,
            "adjusted_score": m.final_grade,
        },
    }
    (HERE / "metrics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nPASS: Standard executable tokenizer")
    print("PASS: Vocabulary <= 10000" if vocab <= 10000 else "FAIL: Vocabulary")
    print("PASS: Four complete faithful corpora encoded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
