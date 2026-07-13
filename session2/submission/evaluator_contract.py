"""Authoritative faithful evaluator contract — single source of truth."""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING

import regex

if TYPE_CHECKING:
    from tokenizers import Tokenizer

LANGS = ("en", "hi", "te", "bn")
HINDI_FERTILITY_THRESHOLD = 1.2
ENGLISH_FERTILITY_THRESHOLD = 1.2

REVIEWER_SAMPLE = "India's population is 1,428,627,663."

FAITHFUL_UNIT_RE = regex.compile(r"[\p{L}\p{M}\p{N}]+|[^\s\p{L}\p{M}\p{N}]")

# ponytail: legacy aliases for research scripts still importing old names
WORDISH_PATTERN = FAITHFUL_UNIT_RE


def visible_non_whitespace(text: str) -> str:
    return "".join(ch for ch in text if not ch.isspace())


def faithful_units(text: str) -> int:
    return len(FAITHFUL_UNIT_RE.findall(text))


def extract_faithful_units(text: str) -> list[str]:
    return FAITHFUL_UNIT_RE.findall(text)


# Legacy aliases
count_wordish_units = faithful_units
extract_wordish_units = extract_faithful_units


def visible_nfkc(text: str) -> str:
    return visible_non_whitespace(unicodedata.normalize("NFKC", text))


def verify_roundtrip(tokenizer: Tokenizer, text: str) -> bool:
    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded.ids)
    return visible_nfkc(decoded) == visible_nfkc(text)


def fertility(token_count: int, unit_count: int) -> float:
    if unit_count <= 0:
        raise ValueError("unit_count must be positive")
    return token_count / unit_count


def hindi_penalty(hindi_fertility: float) -> float:
    return math.exp(max(0.0, hindi_fertility / HINDI_FERTILITY_THRESHOLD - 1.0))


def threshold_status(fertilities: dict[str, float]) -> dict[str, bool]:
    return {
        "en_under_1_2": fertilities["en"] < ENGLISH_FERTILITY_THRESHOLD,
        "hi_under_1_2": fertilities["hi"] < HINDI_FERTILITY_THRESHOLD,
    }


def calculate_scores(fertilities: dict[str, float]) -> dict:
    x_min = min(fertilities.values())
    x_max = max(fertilities.values())
    spread = x_max - x_min
    if spread <= 0:
        raise ValueError("Spread must be positive")
    raw_score = 1000.0 / spread
    hp = hindi_penalty(fertilities["hi"])
    adjusted_score = raw_score / hp
    return {
        "x_min": x_min,
        "x_max": x_max,
        "spread": spread,
        "raw_score": raw_score,
        "hindi_penalty": hp,
        "final_grade": adjusted_score,
        "adjusted_score": adjusted_score,
    }


@dataclass(frozen=True)
class EvaluatorMetrics:
    token_counts: dict[str, int]
    faithful_unit_counts: dict[str, int]
    fertilities: dict[str, float]
    x_min: float
    x_max: float
    spread: float
    raw_score: float
    hindi_penalty: float
    final_grade: float
    thresholds: dict[str, bool]

    def to_dict(self) -> dict:
        return {
            "token_counts": self.token_counts,
            "faithful_unit_counts": self.faithful_unit_counts,
            "wordish_counts": self.faithful_unit_counts,
            "fertilities": self.fertilities,
            "thresholds": self.thresholds,
            "x_min": self.x_min,
            "x_max": self.x_max,
            "spread": self.spread,
            "raw_score": self.raw_score,
            "hindi_penalty": self.hindi_penalty,
            "final_grade": self.final_grade,
            "adjusted_score": self.final_grade,
        }


def compute_evaluator_metrics(
    token_counts: dict[str, int],
    faithful_unit_counts: dict[str, int],
) -> EvaluatorMetrics:
    fertilities = {
        lang: fertility(token_counts[lang], faithful_unit_counts[lang]) for lang in LANGS
    }
    scores = calculate_scores(fertilities)
    return EvaluatorMetrics(
        token_counts=dict(token_counts),
        faithful_unit_counts=dict(faithful_unit_counts),
        fertilities=fertilities,
        thresholds=threshold_status(fertilities),
        **{k: scores[k] for k in ("x_min", "x_max", "spread", "raw_score", "hindi_penalty", "final_grade")},
    )
