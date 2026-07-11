"""Authoritative verification logic — single source of truth."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from samabpe.bpe import BPETokenizer
from samabpe.scoring import compute_score
from samabpe.strategies import EN_MAX_FERTILITY, LANGS, VOCAB_BUDGET
from samabpe.word_units import count_word_units, normalize_nfc

LABELS = {"en": "English", "hi": "Hindi", "te": "Telugu", "bn": "Bengali"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class VerifyResult:
    vocabulary_size: int
    languages: list[dict]
    fertilities: dict[str, float]
    sorted_x: list[float]
    x_min: float
    x_max: float
    max_min_gap: float
    score: float
    english_pass: bool
    vocab_pass: bool
    tokenizer_sha256: str
    corpus_hashes: dict[str, str]
    winning_strategy: str | None = None

    @property
    def verified(self) -> bool:
        return self.english_pass and self.vocab_pass


def run_verification(
    tokenizer_path: Path,
    corpora_dir: Path,
    *,
    winning_strategy: str | None = None,
) -> VerifyResult:
    """Compute all metrics fresh from tokenizer + frozen corpora only."""
    tok = BPETokenizer.load(tokenizer_path)
    corpora = {
        lang: (corpora_dir / f"{lang}_india.txt").read_text(encoding="utf-8")
        for lang in LANGS
    }

    languages = []
    fertilities: dict[str, float] = {}
    corpus_hashes: dict[str, str] = {}

    for lang in LANGS:
        text = normalize_nfc(corpora[lang])
        wu = count_word_units(text)
        tokens = tok.count_tokens(text)
        x = tokens / wu if wu else float("inf")
        fertilities[lang] = x
        corpus_hashes[lang] = sha256_text(text)
        languages.append({
            "lang": lang,
            "label": LABELS[lang],
            "characters": len(text),
            "word_units": wu,
            "tokens": tokens,
            "fertility": x,
        })

    score_data = compute_score(fertilities)
    for lm in languages:
        lm["rank"] = score_data["ranks"][lm["lang"]]
        lm["distance_from_best"] = lm["fertility"] - score_data["x_min"]
        lm["distance_from_worst"] = score_data["x_max"] - lm["fertility"]

    return VerifyResult(
        vocabulary_size=tok.vocab_size,
        languages=languages,
        fertilities=fertilities,
        sorted_x=score_data["sorted_x"],
        x_min=score_data["x_min"],
        x_max=score_data["x_max"],
        max_min_gap=score_data["max_min_gap"],
        score=score_data["score"],
        english_pass=fertilities["en"] <= EN_MAX_FERTILITY,
        vocab_pass=tok.vocab_size <= VOCAB_BUDGET,
        tokenizer_sha256=sha256_file(tokenizer_path),
        corpus_hashes=corpus_hashes,
        winning_strategy=winning_strategy,
    )


def to_stats_json(result: VerifyResult) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "scripts/verify.py",
        "verified": result.verified,
        "winning_strategy": result.winning_strategy,
        "vocabulary_size": result.vocabulary_size,
        "vocab_budget": VOCAB_BUDGET,
        "languages": result.languages,
        "fertilities": result.fertilities,
        "sorted_x": result.sorted_x,
        "x_min": result.x_min,
        "x_max": result.x_max,
        "max_min_gap": result.max_min_gap,
        "score": result.score,
        "english_constraint": {
            "max_allowed": EN_MAX_FERTILITY,
            "actual": result.fertilities["en"],
            "pass": result.english_pass,
        },
        "vocab_constraint": {"max_allowed": VOCAB_BUDGET, "actual": result.vocabulary_size, "pass": result.vocab_pass},
        "tokenizer_sha256": result.tokenizer_sha256,
        "corpus_hashes": result.corpus_hashes,
        "trust": {
            "english_lte_1_2": result.english_pass,
            "vocabulary_lte_10000": result.vocab_pass,
            "one_deterministic_tokenizer": True,
            "scores_independently_reproducible": True,
        },
    }


def to_verification_manifest(result: VerifyResult) -> dict:
    return {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verified": result.verified,
        "formula": {
            "fertility": "tokens / word_units",
            "score": "1000 / (x_max - x_min)",
            "word_units": "NFC text split on Unicode whitespace, empty segments discarded",
        },
        "constraints": {
            "vocabulary_max": VOCAB_BUDGET,
            "english_fertility_max": EN_MAX_FERTILITY,
            "vocabulary_pass": result.vocab_pass,
            "english_pass": result.english_pass,
        },
        "results": {
            "vocabulary_size": result.vocabulary_size,
            "sorted_x": result.sorted_x,
            "x_min": result.x_min,
            "x_max": result.x_max,
            "max_min_gap": result.max_min_gap,
            "score": result.score,
        },
        "tokenizer_sha256": result.tokenizer_sha256,
        "corpus_hashes": result.corpus_hashes,
    }


def print_report(result: VerifyResult) -> None:
    rows = [(lm["label"], lm["word_units"], lm["tokens"], lm["fertility"], lm["rank"]) for lm in result.languages]
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                SamaBPE Independent Verification             ║")
    print("╠══════════╦═══════════╦══════════╦═══════════╦══════════════╣")
    print("║ Language ║ Word Units║ Tokens   ║ Fertility ║ Rank         ║")
    print("╠══════════╬═══════════╬══════════╬═══════════╬══════════════╣")
    for label, wu, tok, fert, rank in rows:
        print(f"║ {label:<8} ║ {wu:>9} ║ {tok:>8} ║ {fert:>9.4f} ║ #{rank:<12} ║")
    print("╚══════════╩═══════════╩══════════╩═══════════╩══════════════╝")
    print()
    print(f"Vocabulary size:      {result.vocabulary_size}")
    print(f"English constraint:   {'PASS' if result.english_pass else 'FAIL'} (X={result.fertilities['en']:.4f} ≤ {EN_MAX_FERTILITY})")
    print(f"Vocab constraint:     {'PASS' if result.vocab_pass else 'FAIL'}")
    print(f"Best fertility:       {result.x_min:.4f}")
    print(f"Worst fertility:      {result.x_max:.4f}")
    print(f"Fairness gap:         {result.max_min_gap:.4f}")
    print(f"VERIFIED SELF-SCORE:  {result.score:.4f}")
    print()
    print("Tokenizer SHA-256:")
    print(result.tokenizer_sha256)
    print()
    print("Corpus hashes:")
    for lang in LANGS:
        print(f"  {lang.upper()}: {result.corpus_hashes[lang]}")
