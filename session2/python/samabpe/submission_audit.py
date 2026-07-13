"""Independent submission audit — recompute everything from frozen artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import regex
from tokenizers import Tokenizer

from samabpe.evaluator_contract import (
    LANGS,
    REVIEWER_SAMPLE,
    compute_evaluator_metrics,
    extract_faithful_units,
    faithful_units,
    hindi_penalty,
    verify_roundtrip,
    visible_non_whitespace,
    visible_nfkc,
)

META = "▁"
SPECIAL_RE = re.compile(r"^<[^>]+>$")
ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "submission"
CORPUS_EXT_ORDER = (".faithful.txt", ".faithful.md")

ROUNDTRIP_SAMPLES = [
    REVIEWER_SAMPLE,
    "[India](https://en.wikipedia.org/wiki/India)",
    "https://en.wikipedia.org/wiki/India?x=1&y=2#History",
    "1,428,627,663.50",
    "**India** _भारत_ ~~test~~",
    "| Country | Population |",
    "## History of India",
    "India[1][2][citation needed]",
    "India भारत తెలుగు বাংলা — 2026!",
    "₹ $ € % + = / \\ : ; @ # & ? !",
]

LANG_LABELS = {
    "en": ("English", "India"),
    "hi": ("Hindi", "भारत"),
    "te": ("Telugu", "భారతదేశం"),
    "bn": ("Bengali", "ভারত"),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_corpus_path(submission_dir: Path, lang: str) -> tuple[Path, str]:
    for ext in CORPUS_EXT_ORDER:
        p = submission_dir / "corpus" / f"{lang}{ext}"
        if p.exists():
            return p, ext
    raise FileNotFoundError(f"no corpus for {lang}")


def load_submission_corpora(submission_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    submission_dir = submission_dir or SUBMISSION
    out: dict[str, dict[str, Any]] = {}
    for lang in LANGS:
        path, ext = resolve_corpus_path(submission_dir, lang)
        text = path.read_text(encoding="utf-8")
        meta_path = submission_dir / "corpus" / f"{lang}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        label, article = LANG_LABELS[lang]
        out[lang] = {
            "language": lang,
            "language_name": label,
            "article": meta.get("article", article),
            "source_url": meta.get("source_url", ""),
            "frozen_path": str(path.relative_to(ROOT)),
            "corpus_extension": ext,
            "sha256": sha256_text(text),
            "characters": len(text),
            "bytes": len(text.encode("utf-8")),
            "faithful_units": faithful_units(text),
            "training_input": True,
            "evaluation_input": True,
            "text": text,
        }
    return out


def inspect_tokenizer_architecture(tok_path: Path) -> dict[str, Any]:
    raw = json.loads(tok_path.read_text(encoding="utf-8"))
    tok = Tokenizer.from_file(str(tok_path))
    vocab = tok.get_vocab_size(with_added_tokens=True)
    norm = raw.get("normalizer") or {}
    pre = raw.get("pre_tokenizer") or {}
    dec = raw.get("decoder") or {}
    model = raw.get("model") or {}
    verified = (
        model.get("type") == "BPE"
        and norm.get("type") == "NFKC"
        and pre.get("type") == "Metaspace"
        and pre.get("replacement") == META
        and pre.get("prepend_scheme") == "never"
        and dec.get("type") == "Metaspace"
        and dec.get("replacement") == META
        and dec.get("prepend_scheme") == "never"
        and vocab <= 10_000
    )
    return {
        "model": model.get("type"),
        "vocab_size": vocab,
        "normalizer": norm,
        "pretokenizer": pre,
        "decoder": dec,
        "sha256": sha256_file(tok_path),
        "verified": verified,
    }


def classify_token(token: str) -> str:
    if SPECIAL_RE.match(token):
        return "special_token"
    body = token.replace(META, "")
    if not body:
        return "shared_punctuation_digits_symbols"
    scripts = {
        "latin": bool(regex.search(r"\p{Script=Latin}", body)),
        "devanagari": bool(regex.search(r"\p{Script=Devanagari}", body)),
        "telugu": bool(regex.search(r"\p{Script=Telugu}", body)),
        "bengali": bool(regex.search(r"\p{Script=Bengali}", body)),
    }
    active = [k for k, v in scripts.items() if v]
    if len(active) >= 2:
        return "mixed_script"
    if len(active) == 1:
        return {
            "latin": "latin_dominant",
            "devanagari": "devanagari_dominant",
            "telugu": "telugu_dominant",
            "bengali": "bengali_dominant",
        }[active[0]]
    if not regex.search(r"\p{L}", body):
        return "shared_punctuation_digits_symbols"
    return "other_unicode"


def analyze_vocabulary(tok_path: Path) -> dict[str, Any]:
    raw = json.loads(tok_path.read_text(encoding="utf-8"))
    vocab: dict[str, int] = raw["model"]["vocab"]
    categories = {
        "latin_dominant": 0,
        "devanagari_dominant": 0,
        "telugu_dominant": 0,
        "bengali_dominant": 0,
        "shared_punctuation_digits_symbols": 0,
        "mixed_script": 0,
        "other_unicode": 0,
        "special_token": 0,
    }
    for token in vocab:
        categories[classify_token(token)] += 1
    total = sum(categories.values())
    return {
        "vocab_size": len(vocab),
        "categories": categories,
        "sum": total,
        "sum_matches_vocab_size": total == len(vocab),
    }


def analyze_vocabulary_utilization(tok: Tokenizer, corpora: dict[str, str]) -> dict[str, Any]:
    per_lang: dict[str, set[int]] = {}
    for lang in LANGS:
        per_lang[lang] = set(tok.encode(corpora[lang]).ids)
    union = set().union(*per_lang.values())
    all_ids = set(range(tok.get_vocab_size(with_added_tokens=True)))
    unused = all_ids - union

    def count_used_by_n(n: int) -> int:
        c = 0
        for tid in union:
            if sum(1 for s in per_lang.values() if tid in s) == n:
                c += 1
        return c

    overlap: dict[str, dict[str, int]] = {}
    for a in LANGS:
        overlap[a] = {}
        for b in LANGS:
            overlap[a][b] = len(per_lang[a] & per_lang[b])

    return {
        "per_corpus_unique_ids": {lang: len(per_lang[lang]) for lang in LANGS},
        "used_by_at_least_one": len(union),
        "unused_by_all_four": len(unused),
        "used_by_exactly_one": count_used_by_n(1),
        "used_by_exactly_two": count_used_by_n(2),
        "used_by_exactly_three": count_used_by_n(3),
        "used_by_all_four": count_used_by_n(4),
        "overlap_matrix": overlap,
    }


def explain_fertility(tok: Tokenizer, text: str) -> dict[str, Any]:
    units = extract_faithful_units(text)
    enc = tok.encode(text)
    dec = tok.decode(enc.ids)
    fu = len(units)
    tc = len(enc.ids)
    return {
        "original_text": text,
        "faithful_units": units,
        "faithful_unit_count": fu,
        "bpe_tokens": enc.tokens,
        "token_ids": enc.ids,
        "bpe_token_count": tc,
        "decoded_text": dec,
        "visible_roundtrip_strict": visible_non_whitespace(dec) == visible_non_whitespace(text),
        "visible_roundtrip_nfkc": visible_nfkc(dec) == visible_nfkc(text),
        "fertility": tc / fu if fu else None,
    }


def _first_sentence(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if len(s) >= 40 and regex.search(r"\p{L}", s):
            return s[:200]
    return text[:200]


def fresh_evaluate(tok: Tokenizer, corpora: dict[str, dict[str, Any]]) -> dict[str, Any]:
    token_counts = {lang: len(tok.encode(corpora[lang]["text"]).ids) for lang in LANGS}
    unit_counts = {lang: corpora[lang]["faithful_units"] for lang in LANGS}
    m = compute_evaluator_metrics(token_counts, unit_counts)
    rt_full = {lang: verify_roundtrip(tok, corpora[lang]["text"]) for lang in LANGS}
    enc = tok.encode(REVIEWER_SAMPLE)
    dec = tok.decode(enc.ids)
    return {
        "token_counts": token_counts,
        "faithful_unit_counts": unit_counts,
        "fertilities": m.fertilities,
        "thresholds": m.thresholds,
        "spread": m.spread,
        "raw_score": m.raw_score,
        "hindi_penalty": m.hindi_penalty,
        "adjusted_score": m.final_grade,
        "roundtrip": {
            "reviewer_sample": verify_roundtrip(tok, REVIEWER_SAMPLE),
            "reviewer_strict": visible_non_whitespace(dec) == visible_non_whitespace(REVIEWER_SAMPLE),
            "reviewer_tokens": enc.tokens,
            "reviewer_ids": enc.ids,
            "reviewer_decoded": dec,
            "full_corpus": rt_full,
            "valid": all(rt_full.values()) and verify_roundtrip(tok, REVIEWER_SAMPLE),
            "samples": {
                s: verify_roundtrip(tok, s) for s in ROUNDTRIP_SAMPLES
            },
        },
    }


def load_experiment_summary() -> dict[str, Any]:
    reg_path = ROOT / "results" / "resubmission" / "experiments.json"
    if not reg_path.exists():
        return {"faithful_experiments": 0}
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    exps = reg.get("experiments", [])
    faithful = [e for e in exps if e.get("architecture") or e.get("normalizer") == "NFKC"]
    if not faithful and reg.get("architecture") == "NFKC+Metaspace":
        faithful = exps
    valid = [e for e in faithful if e.get("status", "").startswith("VALID")]
    both = [
        e
        for e in faithful
        if e.get("thresholds", {}).get("en_under_1_2") and e.get("thresholds", {}).get("hi_under_1_2")
    ]
    winner_id = reg.get("winner_experiment_id")
    winner = next((e for e in exps if e.get("experiment_id") == winner_id), None)
    baseline = next((e for e in exps if e.get("weights") == {"en": 3, "hi": 4, "te": 4, "bn": 2}), None)
    return {
        "registry_path": str(reg_path.relative_to(ROOT)),
        "architecture": reg.get("architecture"),
        "total_measured": reg.get("total_measured", len(faithful)),
        "valid_roundtrip": reg.get("valid_roundtrip"),
        "both_thresholds": reg.get("both_thresholds"),
        "winner_experiment_id": winner_id,
        "winner_weights": winner.get("weights") if winner else None,
        "baseline_weights": baseline.get("weights") if baseline else {"en": 3, "hi": 4, "te": 4, "bn": 2},
        "valid_candidates": len(valid),
        "candidates_passing_both_thresholds": len(both),
        "legacy_note": "Prior non-faithful experiments (NFKC+Whitespace) are not in this registry.",
    }


def compare_json_metrics(fresh: dict[str, Any], saved_path: Path) -> list[dict[str, Any]]:
    if not saved_path.exists():
        return [{"claim": "metrics.json", "status": "UNVERIFIED", "note": "missing"}]
    saved = json.loads(saved_path.read_text(encoding="utf-8"))
    claims: list[dict[str, Any]] = []

    def check(name: str, a: Any, b: Any, tol: float = 1e-9) -> None:
        if isinstance(a, float) and isinstance(b, float):
            ok = abs(a - b) <= tol
        else:
            ok = a == b
        claims.append(
            {
                "claim": name,
                "saved": b,
                "fresh": a,
                "status": "VERIFIED" if ok else "DISCREPANCY",
            }
        )

    check("tokenizer.sha256", fresh.get("tokenizer_sha256"), saved.get("tokenizer", {}).get("sha256"))
    for lang in LANGS:
        sl = saved.get("languages", {}).get(lang, {})
        check(f"{lang}.faithful_units", fresh["faithful_unit_counts"][lang], sl.get("faithful_units"))
        check(f"{lang}.tokens", fresh["token_counts"][lang], sl.get("tokens"))
        check(f"{lang}.fertility", fresh["fertilities"][lang], sl.get("fertility"))
    sc = saved.get("scoring", {})
    check("spread", fresh["spread"], sc.get("spread"))
    check("raw_score", fresh["raw_score"], sc.get("raw_score"))
    check("hindi_penalty", fresh["hindi_penalty"], sc.get("hindi_penalty"))
    check("adjusted_score", fresh["adjusted_score"], sc.get("adjusted_score"))
    return claims


def build_verified_submission(submission_dir: Path | None = None) -> dict[str, Any]:
    submission_dir = submission_dir or SUBMISSION
    tok_path = submission_dir / "tokenizer.json"
    tok = Tokenizer.from_file(str(tok_path))
    corpora = load_submission_corpora(submission_dir)
    corpus_text = {lang: corpora[lang]["text"] for lang in LANGS}
    arch = inspect_tokenizer_architecture(tok_path)
    fresh = fresh_evaluate(tok, corpora)
    vocab_comp = analyze_vocabulary(tok_path)
    vocab_util = analyze_vocabulary_utilization(tok, corpus_text)
    reviewer = explain_fertility(tok, REVIEWER_SAMPLE)
    fertility_examples = {
        "reviewer_sample": reviewer,
        "per_language": {
            lang: explain_fertility(tok, _first_sentence(corpora[lang]["text"])) for lang in LANGS
        },
    }
    prov_path = submission_dir / "provenance.json"
    provenance = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.exists() else {}
    optimizer = load_experiment_summary()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tokenizer": arch,
        "languages": list(LANGS),
        "corpora": {lang: {k: v for k, v in corpora[lang].items() if k != "text"} for lang in LANGS},
        "metrics": {
            "faithful_unit_counts": fresh["faithful_unit_counts"],
            "token_counts": fresh["token_counts"],
            "fertilities": fresh["fertilities"],
            "spread": fresh["spread"],
            "raw_score": fresh["raw_score"],
            "hindi_penalty": fresh["hindi_penalty"],
            "adjusted_score": fresh["adjusted_score"],
        },
        "thresholds": fresh["thresholds"],
        "roundtrip": fresh["roundtrip"],
        "vocabularyComposition": vocab_comp,
        "vocabularyUtilization": vocab_util,
        "fertilityExamples": fertility_examples,
        "optimizer": optimizer,
        "provenance": provenance,
        "tokenizer_sha256": arch["sha256"],
    }


def build_audit_report(submission_dir: Path | None = None) -> dict[str, Any]:
    verified = build_verified_submission(submission_dir)
    claims = compare_json_metrics(
        {
            **verified["metrics"],
            "fertilities": verified["metrics"]["fertilities"],
            "faithful_unit_counts": verified["metrics"]["faithful_unit_counts"],
            "token_counts": verified["metrics"]["token_counts"],
            "thresholds": verified["thresholds"],
            "spread": verified["metrics"]["spread"],
            "raw_score": verified["metrics"]["raw_score"],
            "hindi_penalty": verified["metrics"]["hindi_penalty"],
            "adjusted_score": verified["metrics"]["adjusted_score"],
            "tokenizer_sha256": verified["tokenizer_sha256"],
        },
        (submission_dir or SUBMISSION) / "metrics.json",
    )
    discrepancies = [c for c in claims if c["status"] == "DISCREPANCY"]
    hard_stop = []
    if not verified["tokenizer"]["verified"]:
        hard_stop.append("architecture mismatch")
    if not verified["roundtrip"]["reviewer_sample"]:
        hard_stop.append("reviewer sample fails")
    for lang in LANGS:
        if not verified["roundtrip"]["full_corpus"][lang]:
            hard_stop.append(f"{lang} full corpus fails")
    if not verified["thresholds"]["en_under_1_2"]:
        hard_stop.append("english fertility >= 1.2")
    if not verified["thresholds"]["hi_under_1_2"]:
        hard_stop.append("hindi fertility >= 1.2")
    if discrepancies:
        hard_stop.append("metrics.json differs from fresh evaluation")
    if not verified["vocabularyComposition"]["sum_matches_vocab_size"]:
        hard_stop.append("vocab composition sum mismatch")
    rare_fail = verified["roundtrip"]["samples"].get("₹ $ € % + = / \\ : ; @ # & ? !", True)
    verdict = "NOT SUBMISSION READY" if hard_stop else "SUBMISSION READY"
    return {
        "verdict": verdict,
        "hard_stops": hard_stop,
        "tokenizer": verified["tokenizer"],
        "languages": verified["languages"],
        "corpora": verified["corpora"],
        "roundtrip": verified["roundtrip"],
        "metrics": verified["metrics"],
        "thresholds": verified["thresholds"],
        "claims": claims,
        "discrepancies": discrepancies,
        "vocabulary_composition": verified["vocabularyComposition"],
        "vocabulary_utilization": verified["vocabularyUtilization"],
        "optimizer": verified["optimizer"],
        "risks": ([] if rare_fail else ["Rare Unicode symbols (€, @) fail isolated round-trip stress sample"]),
        "authoritative_corpus": "submission/corpus/{lang}.faithful.txt (preferred; .md identical byte-for-byte)",
    }
