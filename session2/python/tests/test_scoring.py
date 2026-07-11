"""Tests for scoring."""

from samabpe.scoring import compute_score


def test_score_formula():
    fert = {"en": 1.1, "hi": 1.3, "te": 1.4, "bn": 1.5}
    r = compute_score(fert)
    assert r["x_min"] == 1.1
    assert r["x_max"] == 1.5
    assert abs(r["max_min_gap"] - 0.4) < 1e-9
    assert abs(r["score"] - 2500.0) < 1e-6


def test_ranks_order():
    fert = {"en": 1.0, "hi": 2.0, "te": 1.5, "bn": 1.8}
    r = compute_score(fert)
    assert r["ranks"]["en"] == 1
    assert r["ranks"]["hi"] == 4
