"""Evaluator scoring with Hindi exponential penalty."""

from __future__ import annotations

import math
from dataclasses import dataclass

LANGS = ("en", "hi", "te", "bn")
HINDI_FERTILITY_THRESHOLD = 1.2


def fertility(tokens: int, wordish_units: int) -> float:
    if wordish_units == 0:
        return float("inf")
    return tokens / wordish_units


def hindi_penalty(x_hi: float) -> float:
    return math.exp(max(0.0, x_hi / HINDI_FERTILITY_THRESHOLD - 1.0))


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
    adjusted_score: float

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
            "adjusted_score": self.adjusted_score,
        }


def compute_evaluator_metrics(
    token_counts: dict[str, int],
    wordish_counts: dict[str, int],
) -> EvaluatorMetrics:
    fertilities = {
        lang: fertility(token_counts[lang], wordish_counts[lang]) for lang in LANGS
    }
    xs = [fertilities[l] for l in LANGS]
    x_min = min(xs)
    x_max = max(xs)
    spread = x_max - x_min
    raw = 1000.0 / spread if spread > 0 else float("inf")
    penalty = hindi_penalty(fertilities["hi"])
    adjusted = raw / penalty if penalty > 0 else float("inf")
    return EvaluatorMetrics(
        token_counts=dict(token_counts),
        wordish_counts=dict(wordish_counts),
        fertilities=fertilities,
        x_min=x_min,
        x_max=x_max,
        spread=spread,
        raw_score=raw,
        hindi_penalty=penalty,
        adjusted_score=adjusted,
    )
