"""Tests for authoritative evaluator contract."""

from __future__ import annotations

import math
import unicodedata

import pytest

from samabpe.evaluator_contract import (
    HINDI_FERTILITY_THRESHOLD,
    calculate_scores,
    count_wordish_units,
    extract_wordish_units,
    fertility,
    hindi_penalty,
    normalize_for_tokenizer,
)


def test_nfkc_compatibility():
    # NFKC compatibility: fullwidth digits → ASCII
    assert normalize_for_tokenizer("１２３") == "123"


def test_punctuation_not_wordish():
    text = "India, Bharat! বাংলা | తెలుగు [link](url)"
    units = extract_wordish_units(text)
    assert "India" in units
    assert "Bharat" in units
    assert "," not in "".join(units)
    assert "|" not in units


def test_devanagari():
    units = extract_wordish_units("भारत एक देश")
    assert len(units) >= 3


def test_telugu_combining():
    assert count_wordish_units("తెలుగు") >= 1


def test_bengali_combining():
    assert count_wordish_units("বাংলা") >= 1


def test_url_processing():
    units = extract_wordish_units("see https://example.com/path for info")
    assert "see" in units
    assert "for" in units


def test_empty_input():
    assert count_wordish_units("") == 0
    assert extract_wordish_units("!!!") == []


def test_reference_fertility_spread():
    fertilities = {
        "en": 1.221356,
        "hi": 1.192285,
        "te": 1.349246,
        "bn": 1.366433,
    }
    s = calculate_scores(fertilities)
    assert abs(s["hindi_penalty"] - 1.0) < 1e-9
    assert abs(s["spread"] - (1.366433 - 1.192285)) < 1e-6
    assert abs(s["raw_score"] - 1000.0 / s["spread"]) < 1e-6


def test_reviewer_hindi_penalty():
    assert abs(hindi_penalty(4.294) - 13.18) < 0.05


def test_fertility_requires_positive_denominator():
    with pytest.raises(ValueError):
        fertility(10, 0)


def test_spread_must_be_positive():
    with pytest.raises(ValueError):
        calculate_scores({"en": 1.0, "hi": 1.0, "te": 1.0, "bn": 1.0})
