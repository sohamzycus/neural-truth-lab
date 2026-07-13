"""Tests for evaluator text pipeline (faithful units)."""

from __future__ import annotations

from samabpe.evaluator_text import (
    NON_WORDISH_PATTERN,
    apply_evaluator_normalization,
    count_wordish_units,
    wordish_units,
)


def test_english_punctuation_splits():
    assert count_wordish_units("Hello, world!") == 4


def test_devanagari_word():
    text = "भारत एक देश है"
    assert count_wordish_units(text) >= 3


def test_telugu_word():
    assert count_wordish_units("భారతదేశం") == 1


def test_bengali_word():
    assert count_wordish_units("ভারত") == 1


def test_combining_mark_preserved_in_letter_run():
    n = count_wordish_units("café")
    assert n >= 1


def test_url_keeps_punctuation_units():
    u = "see https://example.com/path for info"
    units = wordish_units(u)
    assert "see" in units
    assert "for" in units
    assert len(units) >= 8


def test_markdown_syntax():
    md = "[India](https://en.wikipedia.org/wiki/India)"
    units = wordish_units(md)
    assert "India" in units


def test_mixed_script():
    text = "India भारत తెలుగు বাংলা"
    assert count_wordish_units(text) == 4


def test_pattern_documented():
    assert NON_WORDISH_PATTERN == r"[^\p{L}\p{M}\p{N}]+"


def test_empty():
    assert count_wordish_units("") == 0
    assert count_wordish_units("!!!") == 3


def test_normalize_collapses_whitespace():
    assert apply_evaluator_normalization("a   b") == "a b"
