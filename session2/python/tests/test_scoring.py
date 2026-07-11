"""Tests for scoring."""

from samabpe.scoring import compute_score


def test_score_formula():
    fert = {"en": 1.1, "hi": 1.3, "te": 1.4, "bn": 1.5}
    r = compute_score(fert)
    assert r["x_min"] == 1.1
    assert r["x_max"] == 1.5
    assert abs(r["max_min_gap"] - 0.4) < 1e-9
    assert abs(r["score"] - 2500.0) < 1e-6


def test_display_rounding_does_not_change_score():
    fert = {"en": 1.0495010374468925, "hi": 1.321119088883387, "te": 1.302668259657507, "bn": 1.6549780839073263}
    r = compute_score(fert)
    displayed_gap = round(r["max_min_gap"], 3)
    assert displayed_gap != r["max_min_gap"]  # rounding is for display only
    assert abs(r["score"] - 1000.0 / r["max_min_gap"]) < 1e-9
