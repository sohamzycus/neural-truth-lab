"""Evaluator-compatible text normalization and word-ish unit counting.

Contract (authoritative for resubmission):
1. Unicode NFKC normalization.
2. Replace every run of characters that is NOT Unicode letter, mark, or number with one space.
3. Collapse internal whitespace runs to a single space (strip ends).
4. Word-ish units = non-empty segments after splitting on ASCII/Unicode whitespace.

Pattern: ``[^\\p{L}\\p{M}\\p{N}]+`` (via the ``regex`` package).
"""

from __future__ import annotations

import unicodedata

import regex as rx

# Documented evaluator regex — matches reference contract.
NON_WORDISH_PATTERN = r"[^\p{L}\p{M}\p{N}]+"
_NON_WORDISH_RE = rx.compile(NON_WORDISH_PATTERN)
_WHITESPACE_COLLAPSE_RE = rx.compile(r"\s+")


def normalize_nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def apply_evaluator_normalization(text: str) -> str:
    """Apply NFKC + non-wordish replacement + whitespace collapse."""
    text = normalize_nfkc(text)
    text = _NON_WORDISH_RE.sub(" ", text)
    text = _WHITESPACE_COLLAPSE_RE.sub(" ", text).strip()
    return text


def count_wordish_units(text: str) -> int:
    """Count word-ish units on the full corpus text."""
    normalized = apply_evaluator_normalization(text)
    if not normalized:
        return 0
    return len(normalized.split())


def wordish_units(text: str) -> list[str]:
    normalized = apply_evaluator_normalization(text)
    if not normalized:
        return []
    return normalized.split()
