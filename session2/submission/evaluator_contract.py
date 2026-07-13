"""Authoritative evaluator contract — single source of truth for resubmission."""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass

import regex

LANGS = ("en", "hi", "te", "bn")
HINDI_FERTILITY_THRESHOLD = 1.2

WORDISH_PATTERN = regex.compile(r"[\p{L}\p{M}\p{N}]+")
NON_WORDISH_PATTERN = regex.compile(r"[^\p{L}\p{M}\p{N}]+")


def normalize_for_tokenizer(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = NON_WORDISH_PATTERN.sub(" ", text)
    return " ".join(text.split())


def extract_wordish_units(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text)
    return WORDISH_PATTERN.findall(text)


def count_wordish_units(text: str) -> int:
    return len(extract_wordish_units(text))


def fertility(token_count: int, wordish_count: int) -> float:
    if wordish_count <= 0:
        raise ValueError("wordish_count must be positive")
    return token_count / wordish_count


def hindi_penalty(hindi_fertility: float) -> float:
    return math.exp(max(0.0, hindi_fertility / HINDI_FERTILITY_THRESHOLD - 1.0))


def calculate_scores(fertilities: dict[str, float]) -> dict:
    x_min = min(fertilities.values())
    x_max = max(fertilities.values())
    spread = x_max - x_min
    if spread <= 0:
        raise ValueError("Spread must be positive")
    raw_score = 1000.0 / spread
    hp = hindi_penalty(fertilities["hi"])
    final_grade = raw_score / hp
    return {
        "x_min": x_min,
        "x_max": x_max,
        "spread": spread,
        "raw_score": raw_score,
        "hindi_penalty": hp,
        "final_grade": final_grade,
    }


@dataclass(frozen=True)
class EvaluatorMetrics:
    token_counts: dict[str, int]
    wordish_counts: dict[str, int]
    fertilities: dict[str, float]
    x_min: float
    x_max: float
    spread: float
    raw_score: float
    hindi_penalty: float
    final_grade: float

    def to_dict(self) -> dict:
        return {
            "token_counts": self.token_counts,
            "wordish_counts": self.wordish_counts,
            "fertilities": self.fertilities,
            "x_min": self.x_min,
            "x_max": self.x_max,
            "spread": self.spread,
            "raw_score": self.raw_score,
            "hindi_penalty": self.hindi_penalty,
            "final_grade": self.final_grade,
            "adjusted_score": self.final_grade,  # ponytail: alias for older callers
        }


def compute_evaluator_metrics(
    token_counts: dict[str, int],
    wordish_counts: dict[str, int],
) -> EvaluatorMetrics:
    fertilities = {
        lang: fertility(token_counts[lang], wordish_counts[lang]) for lang in LANGS
    }
    scores = calculate_scores(fertilities)
    return EvaluatorMetrics(
        token_counts=dict(token_counts),
        wordish_counts=dict(wordish_counts),
        fertilities=fertilities,
        **scores,
    )
