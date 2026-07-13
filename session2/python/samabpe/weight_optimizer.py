"""SamaBPE adaptive multilingual training-weight search."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from typing import Literal

FERTILITY_THRESHOLD = 1.2
ConstraintClass = Literal["A", "B", "C"]


@dataclass(frozen=True)
class WeightConfig:
    en: int
    hi: int
    te: int
    bn: int

    def as_dict(self) -> dict[str, int]:
        return {"en": self.en, "hi": self.hi, "te": self.te, "bn": self.bn}

    def canonical(self) -> WeightConfig:
        g = reduce(math.gcd, (self.en, self.hi, self.te, self.bn))
        return WeightConfig(self.en // g, self.hi // g, self.te // g, self.bn // g)

    def key(self) -> str:
        c = self.canonical()
        return f"{c.en}-{c.hi}-{c.te}-{c.bn}"


def english_threshold_pass(fertilities: dict[str, float], threshold: float = FERTILITY_THRESHOLD) -> bool:
    return fertilities["en"] <= threshold


def hindi_threshold_pass(fertilities: dict[str, float], threshold: float = FERTILITY_THRESHOLD) -> bool:
    return fertilities["hi"] <= threshold


def constraint_class(fertilities: dict[str, float], threshold: float = FERTILITY_THRESHOLD) -> ConstraintClass:
    en_ok = english_threshold_pass(fertilities, threshold)
    hi_ok = hindi_threshold_pass(fertilities, threshold)
    if en_ok and hi_ok:
        return "A"
    if hi_ok:
        return "B"
    return "C"


@dataclass
class CandidateResult:
    weights: WeightConfig
    tokenizer_path: str
    vocab_size: int
    fertilities: dict[str, float]
    spread: float
    raw_score: float
    hindi_penalty: float
    final_grade: float
    tokenizer_sha256: str
    experiment_id: str = ""
    status: str = "MEASURED"
    english_threshold_pass: bool = field(init=False)
    hindi_threshold_pass: bool = field(init=False)
    constraint_class: ConstraintClass = field(init=False)

    def __post_init__(self) -> None:
        self.english_threshold_pass = english_threshold_pass(self.fertilities)
        self.hindi_threshold_pass = hindi_threshold_pass(self.fertilities)
        self.constraint_class = constraint_class(self.fertilities)

    def to_experiment_record(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "strategy": "adaptive-weight-search",
            "weights": self.weights.as_dict(),
            "vocab_size": self.vocab_size,
            "fertilities": self.fertilities,
            "spread": self.spread,
            "raw_score": self.raw_score,
            "hindi_penalty": self.hindi_penalty,
            "final_grade": self.final_grade,
            "adjusted_score": self.final_grade,
            "english_threshold_pass": self.english_threshold_pass,
            "hindi_threshold_pass": self.hindi_threshold_pass,
            "constraint_class": self.constraint_class,
            "tokenizer_path": self.tokenizer_path,
            "tokenizer_sha256": self.tokenizer_sha256,
            "status": self.status,
        }


def _dedupe_grid(configs: list[WeightConfig]) -> list[WeightConfig]:
    seen: set[str] = set()
    out: list[WeightConfig] = []
    for w in configs:
        c = w.canonical()
        if c.key() not in seen:
            seen.add(c.key())
            out.append(c)
    return out


def coarse_grid() -> list[WeightConfig]:
    en_r = [2, 3, 4, 5]
    hi_r = [3, 4, 5, 6]
    te_r = [3, 4, 5, 6]
    bn_r = [2, 3, 4, 5, 6]
    return _dedupe_grid(WeightConfig(en, hi, te, bn) for en, hi, te, bn in product(en_r, hi_r, te_r, bn_r))


def threshold_grid() -> list[WeightConfig]:
    """Higher EN/HI exposure to push fertility toward ≤1.2."""
    en_r = range(4, 11)
    hi_r = range(4, 11)
    te_r = range(2, 9)
    bn_r = range(2, 9)
    return _dedupe_grid(WeightConfig(en, hi, te, bn) for en, hi, te, bn in product(en_r, hi_r, te_r, bn_r))


def neighbor_configs(top: WeightConfig) -> list[WeightConfig]:
    deltas = [-1, 0, 1]
    seen: set[str] = set()
    out: list[WeightConfig] = []
    for de, dh, dt, db in product(deltas, deltas, deltas, deltas):
        if de == dh == dt == db == 0:
            continue
        w = WeightConfig(
            max(1, top.en + de),
            max(1, top.hi + dh),
            max(1, top.te + dt),
            max(1, top.bn + db),
        ).canonical()
        if w.key() not in seen:
            seen.add(w.key())
            out.append(w)
    return out


def threshold_neighbor_configs(top: WeightConfig) -> list[WeightConfig]:
    """Bias neighbors toward stronger EN/HI training exposure."""
    seen: set[str] = {top.key()}
    out: list[WeightConfig] = []
    for de, dh, dt, db in product([-1, 0, 1, 2], [-1, 0, 1, 2], [-1, 0, 1], [-1, 0, 1]):
        if de == dh == dt == db == 0:
            continue
        w = WeightConfig(
            max(1, top.en + de),
            max(1, top.hi + dh),
            max(1, max(1, top.te + dt)),
            max(1, top.bn + db),
        ).canonical()
        if w.key() not in seen:
            seen.add(w.key())
            out.append(w)
    return out


def pick_winner(candidates: list[CandidateResult]) -> CandidateResult:
    """Unconstrained: maximize adjusted score."""
    measured = [c for c in candidates if c.status == "MEASURED"]
    if not measured:
        raise ValueError("No measured candidates")
    return max(measured, key=lambda c: c.final_grade)


def best_in_class(candidates: list[CandidateResult], cls: ConstraintClass) -> CandidateResult | None:
    pool = [c for c in candidates if c.status == "MEASURED" and c.constraint_class == cls]
    if not pool:
        return None
    return max(pool, key=lambda c: c.final_grade)


def pick_winner_constrained(candidates: list[CandidateResult]) -> tuple[CandidateResult, dict]:
    """
    Class A (EN≤1.2 & HI≤1.2) preferred, else Class B (HI≤1.2), else unconstrained best.
    """
    measured = [c for c in candidates if c.status == "MEASURED"]
    if not measured:
        raise ValueError("No measured candidates")

    best_a = best_in_class(measured, "A")
    best_b = best_in_class(measured, "B")
    best_c = pick_winner(measured)

    if best_a is not None:
        winner = best_a
        selection_reason = "class_a_threshold_valid"
    elif best_b is not None:
        winner = best_b
        selection_reason = "class_b_hindi_valid_no_class_a"
    else:
        winner = best_c
        selection_reason = "unconstrained_no_threshold_valid"

    summary = {
        "selection_reason": selection_reason,
        "class_a_count": sum(1 for c in measured if c.constraint_class == "A"),
        "class_b_count": sum(1 for c in measured if c.constraint_class == "B"),
        "class_c_count": sum(1 for c in measured if c.constraint_class == "C"),
        "best_class_a": best_a.to_experiment_record() if best_a else None,
        "best_class_b": best_b.to_experiment_record() if best_b else None,
        "best_unconstrained": best_c.to_experiment_record(),
        "winner_constraint_class": winner.constraint_class,
    }
    return winner, summary
