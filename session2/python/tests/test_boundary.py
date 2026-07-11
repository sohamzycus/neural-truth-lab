"""Tests for boundary analysis."""

from samabpe.boundary import boundary_analysis, score_target_ladder


def test_boundary_analysis_ranks():
    tokens = {"en": 10622, "hi": 10672, "te": 3271, "bn": 10572}
    wu = {"en": 10121, "hi": 8078, "te": 2511, "bn": 6388}
    b = boundary_analysis(tokens, wu)
    assert b["x_min_language"] == "en"
    assert b["x_max_language"] == "bn"
    assert len(b["languages"]) == 4
    bn = next(l for l in b["languages"] if l["language"] == "bn")
    assert bn["is_x_max"]
    assert bn["score_sensitivity_tokens_saved"]["1"]["score_delta"] >= 0


def test_score_target_ladder_improves_with_savings():
    tokens = {"en": 10622, "hi": 10672, "te": 3271, "bn": 10572}
    wu = {"en": 10121, "hi": 8078, "te": 2511, "bn": 6388}
    ladder = score_target_ladder(tokens, wu)
    s1 = ladder["scenarios"][0]
    assert s1["tokens_saved_from_x_max"] == 1
    assert s1["new_score"] >= ladder["baseline"]["score"]
