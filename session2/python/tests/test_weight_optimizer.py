"""Tests for constrained weight selection."""

from __future__ import annotations

from samabpe.weight_optimizer import (
    CandidateResult,
    WeightConfig,
    constraint_class,
    pick_winner_constrained,
)


def _c(en: float, hi: float, te: float, bn: float, grade: float) -> CandidateResult:
    spread = max(en, hi, te, bn) - min(en, hi, te, bn)
    return CandidateResult(
        weights=WeightConfig(1, 1, 1, 1),
        tokenizer_path="x",
        vocab_size=10000,
        fertilities={"en": en, "hi": hi, "te": te, "bn": bn},
        spread=spread,
        raw_score=1000 / spread if spread else 0,
        hindi_penalty=1.0,
        final_grade=grade,
        tokenizer_sha256="a",
        experiment_id="t",
    )


def test_constraint_class_a():
    assert constraint_class({"en": 1.1, "hi": 1.1, "te": 1.5, "bn": 1.4}) == "A"


def test_constraint_class_b():
    assert constraint_class({"en": 1.3, "hi": 1.1, "te": 1.5, "bn": 1.4}) == "B"


def test_constraint_class_c():
    assert constraint_class({"en": 1.3, "hi": 1.3, "te": 1.5, "bn": 1.4}) == "C"


def test_pick_winner_prefers_class_a():
    a = _c(1.15, 1.18, 1.4, 1.35, 5000)
    c = _c(1.43, 1.39, 1.41, 1.40, 19867)
    winner, summary = pick_winner_constrained([a, c])
    assert winner.constraint_class == "A"
    assert summary["selection_reason"] == "class_a_threshold_valid"


def test_pick_winner_class_b_when_no_a():
    b = _c(1.35, 1.15, 1.4, 1.35, 8000)
    c = _c(1.43, 1.39, 1.41, 1.40, 19867)
    winner, summary = pick_winner_constrained([b, c])
    assert winner.constraint_class == "B"
    assert summary["class_a_count"] == 0
