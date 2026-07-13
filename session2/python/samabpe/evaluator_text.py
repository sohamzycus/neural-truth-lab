"""Backward-compatible re-exports — use evaluator_contract.py."""

import unicodedata

from samabpe.evaluator_contract import (  # noqa: F401
    NON_WORDISH_PATTERN,
    WORDISH_PATTERN,
    count_wordish_units,
    extract_wordish_units,
    normalize_for_tokenizer,
)

# Legacy names
apply_evaluator_normalization = normalize_for_tokenizer
wordish_units = extract_wordish_units
normalize_nfkc = lambda text: unicodedata.normalize("NFKC", text)  # noqa: E731
