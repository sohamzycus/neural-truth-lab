"""Word-unit counting — official evaluator denominator logic."""

from __future__ import annotations

import re
import unicodedata

# Official: split on any Unicode whitespace after NFC normalization.
_WHITESPACE_RE = re.compile(r"\s+", re.UNICODE)

# Sensitivity check only — NOT used for official score.
_PUNCT_AWARE_RE = re.compile(
    r"[\w\u0900-\u097F\u0980-\u09FF\u0C00-\u0C7F]+|[^\s\w\u0900-\u097F\u0980-\u09FF\u0C00-\u0C7F]+",
    re.UNICODE,
)


def normalize_nfc(text: str) -> str:
    """Apply Unicode NFC normalization."""
    return unicodedata.normalize("NFC", text)


def count_word_units(text: str) -> int:
    """
    Official assignment denominator.

    1. Apply NFC normalization to the full text.
    2. Split on Unicode whitespace (str.split() with default whitespace).
    3. Discard empty segments.
    4. Count remaining segments.

    Punctuation remains attached to adjacent word units (no stripping).
    ZWJ/ZWNJ are preserved inside segments — not split separately.
    Repeated whitespace collapses via split semantics.
    Newlines/tabs count as whitespace separators.
    """
    normalized = normalize_nfc(text)
    return sum(1 for seg in normalized.split() if seg)


def word_units(text: str) -> list[str]:
    """Return official word unit segments (for inspection)."""
    return [seg for seg in normalize_nfc(text).split() if seg]


def count_word_units_punct_aware(text: str) -> int:
    """
    Sensitivity-check denominator — NOT used for official score.

    Splits alphanumeric/Indic letter runs and isolated punctuation clusters.
    """
    normalized = normalize_nfc(text)
    segments = [m.group(0) for m in _PUNCT_AWARE_RE.finditer(normalized) if m.group(0).strip()]
    return len(segments)


def sensitivity_analysis(text: str) -> dict:
    """Compare official vs punctuation-aware denominators."""
    official = count_word_units(text)
    alt = count_word_units_punct_aware(text)
    return {
        "official_word_units": official,
        "punct_aware_word_units": alt,
        "delta": alt - official,
        "label": "sensitivity_check_not_official",
    }
