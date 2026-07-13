"""Tests for faithful evaluator contract."""

from __future__ import annotations

import pytest

from samabpe.evaluator_contract import (
    REVIEWER_SAMPLE,
    calculate_scores,
    extract_faithful_units,
    faithful_units,
    fertility,
    hindi_penalty,
    threshold_status,
)


def test_reviewer_sample_faithful_units():
    units = extract_faithful_units(REVIEWER_SAMPLE)
    assert "India" in units
    assert "'" in units
    assert "s" in units
    assert "," in units
    assert "." in units
    assert "1" in units


def test_faithful_unit_india():
    assert faithful_units("India") == 1


def test_markdown_punctuation_counted():
    text = "India, Bharat! [link](url)"
    units = extract_faithful_units(text)
    assert "India" in units
    assert "," in units
    assert "!" in units
    assert "[" in units


def test_devanagari():
    assert faithful_units("भारत एक देश") >= 3


def test_empty():
    assert faithful_units("") == 0


def test_reference_fertility_spread():
    fertilities = {
        "en": 1.221356,
        "hi": 1.192285,
        "te": 1.349246,
        "bn": 1.366433,
    }
    s = calculate_scores(fertilities)
    assert abs(s["hindi_penalty"] - 1.0) < 1e-9


def test_threshold_status():
    t = threshold_status({"en": 1.1, "hi": 1.3, "te": 1.2, "bn": 1.2})
    assert t["en_under_1_2"] is True
    assert t["hi_under_1_2"] is False


def test_reviewer_hindi_penalty():
    assert abs(hindi_penalty(4.294) - 13.18) < 0.05


def test_fertility_requires_positive_denominator():
    with pytest.raises(ValueError):
        fertility(10, 0)
