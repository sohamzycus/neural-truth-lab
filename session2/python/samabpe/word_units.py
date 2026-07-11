"""Word-unit counting — official evaluator denominator logic."""

from __future__ import annotations

import unicodedata


def normalize_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def count_word_units(text: str) -> int:
    """Count evaluator-compatible word units after NFC normalization."""
    normalized = normalize_nfc(text)
    return sum(1 for seg in normalized.split() if seg)


def word_units(text: str) -> list[str]:
    """Return word unit segments (for inspection)."""
    return [seg for seg in normalize_nfc(text).split() if seg]
