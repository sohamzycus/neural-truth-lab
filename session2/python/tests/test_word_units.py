"""Tests for word-unit counting."""

from samabpe.word_units import count_word_units, normalize_nfc, word_units


def test_nfc_composes():
    # e + combining acute vs precomposed é
    assert normalize_nfc("e\u0301") == "\u00e9"


def test_count_simple_english():
    assert count_word_units("hello world") == 2


def test_count_empty():
    assert count_word_units("") == 0


def test_count_multiline_whitespace():
    text = "line one\nline two\t tab"
    assert count_word_units(text) == 5


def test_word_units_list():
    assert word_units("  a  b  ") == ["a", "b"]
