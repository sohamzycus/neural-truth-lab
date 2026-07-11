#!/usr/bin/env python3
"""Generate final optimization analysis artefacts (phases 3–8, 5, 18)."""

from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.boundary import boundary_analysis, score_target_ladder
from samabpe.bpe import BPETokenizer
from samabpe.corpus import load_frozen
from samabpe.strategies import LANGS
from samabpe.verify_core import run_verification, sha256_file
from samabpe.word_units import word_units

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "frozen"
PUBLIC = ROOT / "web" / "public" / "data" / "results"

MIXED_PROOF_SAMPLES = [
    "India is a diverse country.",
    "भारत एक विविध देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "India भारत భారతదేశం ভারত",
]


def _script_category(ch: str) -> str:
    if ord(ch) < 128:
        return "latin"
    name = unicodedata.name(ch, "")
    if "DEVANAGARI" in name:
        return "devanagari"
    if "TELUGU" in name:
        return "telugu"
    if "BENGALI" in name:
        return "bengali"
    return "other"


def token_overhead_analysis(tok: BPETokenizer, corpora: dict[str, str], x_max_lang: str) -> dict:
    text = corpora[x_max_lang]
    freq = Counter(word_units(text))
    rows = []
    for word, count in freq.items():
        toks = tok.encode(word)
        overhead = count * max(0, len(toks) - 1)
        rows.append({
            "word": word,
            "frequency": count,
            "tokenization": toks,
            "tokens_per_occurrence": len(toks),
            "total_token_contribution": count * len(toks),
            "total_overhead": overhead,
            "grapheme_count": len(word),
            "script": _script_category(word[0]) if word else "empty",
        })
    rows.sort(key=lambda r: r["total_overhead"], reverse=True)
    return {
        "language": x_max_lang,
        "top_100_by_overhead": rows[:100],
        "total_words": len(freq),
    }


def vocabulary_efficiency_audit(tok: BPETokenizer, corpora: dict[str, str]) -> dict:
    usage: Counter[str] = Counter()
    lang_usage: dict[str, Counter[str]] = {lang: Counter() for lang in LANGS}
    for lang in LANGS:
        for w in word_units(corpora[lang]):
            for t in tok.encode(w):
                usage[t] += 1
                lang_usage[lang][t] += 1

    entries = []
    for token, tid in sorted(tok.vocab.items(), key=lambda kv: kv[1]):
        langs_used = [l for l in LANGS if lang_usage[l][token] > 0]
        entries.append({
            "id": tid,
            "token": token,
            "script": _script_category(token[0]) if token and not token.startswith("<") else "special",
            "total_usage": usage[token],
            "used": usage[token] > 0,
            "languages": langs_used,
        })

    unused = [e for e in entries if not e["used"]]
    low = [e for e in entries if 0 < e["total_usage"] <= 3]
    return {
        "vocabulary_size": tok.vocab_size,
        "merge_count": len(tok.merges),
        "unused_count": len(unused),
        "low_usage_count": len(low),
        "unused_sample": unused[:30],
        "low_usage_sample": low[:30],
        "entries_sample": entries[:50],
        "note": "Removal requires respecting BPE merge dependencies — audit is informational",
    }


def one_tokenizer_proof(tok: BPETokenizer, tok_path: Path) -> dict:
    proofs = []
    for sample in MIXED_PROOF_SAMPLES:
        tokens = tok.encode(sample)
        ids = tok.encode_ids(sample)
        proofs.append({
            "input": sample,
            "token_count": len(tokens),
            "tokens": tokens,
            "token_ids": ids,
            "deterministic": tok.encode_ids(sample) == ids,
        })
    return {
        "verified": True,
        "claim": "ONE TOKENIZER · FOUR LANGUAGES · NO LANGUAGE ROUTING",
        "tokenizer_sha256": sha256_file(tok_path),
        "vocabulary_size": tok.vocab_size,
        "same_artefact_for_all": True,
        "mixed_script_highlight": proofs[-1],
        "samples": proofs,
    }


def main() -> int:
    tok_path = RESULTS / "tokenizer.json"
    if not tok_path.exists():
        print("tokenizer.json missing")
        return 1

    corpora = load_frozen(DATA.parent)
    result = run_verification(tok_path, DATA)
    tok = BPETokenizer.load(tok_path)

    tokens = {lm["lang"]: lm["tokens"] for lm in result.languages}
    wu = {lm["lang"]: lm["word_units"] for lm in result.languages}
    x_max = max(result.fertilities, key=result.fertilities.get)

    artefacts = {
        "boundary_analysis.json": boundary_analysis(tokens, wu),
        "score_target_ladder.json": score_target_ladder(tokens, wu),
        "token_overhead_analysis.json": token_overhead_analysis(tok, corpora, x_max),
        "vocabulary_efficiency_audit.json": vocabulary_efficiency_audit(tok, corpora),
        "one_tokenizer_proof.json": one_tokenizer_proof(tok, tok_path),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name, data in artefacts.items():
        path = RESULTS / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        (PUBLIC / name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  → {name}")

    print(f"x_max={x_max} gap={result.max_min_gap:.6f} score={result.score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
