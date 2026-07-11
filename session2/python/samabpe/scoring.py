"""Scoring formulas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageMetrics:
    lang: str
    characters: int
    word_units: int
    tokens: int

    @property
    def fertility(self) -> float:
        if self.word_units == 0:
            return float("inf")
        return self.tokens / self.word_units


def compute_score(fertilities: dict[str, float]) -> dict:
    xs = sorted(fertilities.values())
    x_min, x_max = xs[0], xs[-1]
    gap = x_max - x_min
    score = 1000.0 / gap if gap > 0 else float("inf")
    ranked = sorted(fertilities.items(), key=lambda kv: kv[1])
    return {
        "fertilities": fertilities,
        "sorted_x": [v for _, v in ranked],
        "x_min": x_min,
        "x_max": x_max,
        "max_min_gap": gap,
        "score": score,
        "ranks": {lang: i + 1 for i, (lang, _) in enumerate(ranked)},
    }
