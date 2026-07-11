"""Tests for word-unit counting."""

from samabpe.word_units import (
    count_word_units,
    count_word_units_punct_aware,
    normalize_nfc,
    sensitivity_analysis,
    word_units,
)


def test_nfc_composes():
    assert normalize_nfc("e\u0301") == "\u00e9"


def test_count_simple_english():
    assert count_word_units("hello world") == 2


def test_official_examples():
    assert count_word_units("India is a country.") == 4
    assert count_word_units("भारत एक देश है।") == 4
    assert count_word_units("భారతదేశం ఒక దేశం.") == 3
    assert count_word_units("ভারত একটি দেশ।") == 3


def test_repeated_whitespace():
    assert count_word_units("  a  b  ") == 2


def test_newlines():
    assert count_word_units("line one\nline two") == 4


def test_punctuation_attached():
    assert count_word_units("hello, world!") == 2


def test_sensitivity_differs_from_official():
    s = sensitivity_analysis("hello, world!")
    assert s["official_word_units"] == 2
    assert s["label"] == "sensitivity_check_not_official"


def test_punct_aware_at_least_official():
    text = "India — a country."
    assert count_word_units_punct_aware(text) >= count_word_units(text)
