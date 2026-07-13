"""Tests for evaluator scoring with Hindi penalty."""

from __future__ import annotations

import math

from samabpe.evaluator_scoring import (
    compute_evaluator_metrics,
    hindi_penalty,
)


def test_hindi_penalty_at_threshold():
    assert hindi_penalty(1.2) == 1.0


def test_hindi_penalty_above_threshold():
    x_hi = 4.294
    expected = math.exp(x_hi / 1.2 - 1)
    assert abs(hindi_penalty(x_hi) - expected) < 1e-9


def test_reviewer_arithmetic():
    """Published reviewer fertilities → raw ~657.5, adj ~49.9."""
    fert = {"en": 5.815, "hi": 4.294, "te": 4.761, "bn": 4.620}
    # Use unit counts 1000 each — fertilities scale identically
    tokens = {k: int(v * 1000) for k, v in fert.items()}
    units = {k: 1000 for k in fert}
    m = compute_evaluator_metrics(tokens, units)
    assert abs(m.raw_score - 657.5) < 1.0
    assert abs(m.hindi_penalty - 13.18) < 0.1
    assert abs(m.adjusted_score - 49.9) < 2.0


def test_spread_and_raw_score():
    tokens = {"en": 1200, "hi": 1200, "te": 1300, "bn": 1400}
    units = {"en": 1000, "hi": 1000, "te": 1000, "bn": 1000}
    m = compute_evaluator_metrics(tokens, units)
    assert abs(m.spread - 0.2) < 1e-9
    assert abs(m.raw_score - 5000.0) < 1e-6
