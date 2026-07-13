"""Backward-compatible re-exports — use evaluator_contract.py."""

import unicodedata

from samabpe.evaluator_contract import (  # noqa: F401
    FAITHFUL_UNIT_RE,
    WORDISH_PATTERN,
    count_wordish_units,
    extract_wordish_units,
    faithful_units,
)

# Legacy research pipeline (NFKC + punctuation→space); not used by faithful submission.
NON_WORDISH_PATTERN = r"[^\p{L}\p{M}\p{N}]+"


def normalize_for_tokenizer(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


apply_evaluator_normalization = normalize_for_tokenizer
wordish_units = extract_wordish_units
normalize_nfkc = lambda text: unicodedata.normalize("NFKC", text)  # noqa: E731
