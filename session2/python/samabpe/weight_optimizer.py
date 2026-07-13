"""SamaBPE adaptive multilingual training-weight search."""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import reduce
from itertools import product


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
            "tokenizer_path": self.tokenizer_path,
            "tokenizer_sha256": self.tokenizer_sha256,
            "status": self.status,
        }


def coarse_grid() -> list[WeightConfig]:
    en_r = [2, 3, 4, 5]
    hi_r = [3, 4, 5, 6]
    te_r = [3, 4, 5, 6]
    bn_r = [2, 3, 4, 5, 6]
    seen: set[str] = set()
    out: list[WeightConfig] = []
    for en, hi, te, bn in product(en_r, hi_r, te_r, bn_r):
        w = WeightConfig(en, hi, te, bn).canonical()
        if w.key() not in seen:
            seen.add(w.key())
            out.append(w)
    return out


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


def pick_winner(candidates: list[CandidateResult]) -> CandidateResult:
    measured = [c for c in candidates if c.status == "MEASURED"]
    if not measured:
        raise ValueError("No measured candidates")
    return max(measured, key=lambda c: c.final_grade)
