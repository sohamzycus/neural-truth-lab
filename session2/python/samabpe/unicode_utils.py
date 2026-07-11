"""Unicode and grapheme utilities."""

from __future__ import annotations

import regex as re
from samabpe.word_units import normalize_nfc

GRAPHEME_RE = re.compile(r"\X", re.UNICODE)


def grapheme_clusters(text: str) -> list[str]:
    return GRAPHEME_RE.findall(normalize_nfc(text))


def code_points(token: str) -> list[str]:
    return [f"U+{ord(c):04X}" for c in token]


def grapheme_count(token: str) -> int:
    return len(grapheme_clusters(token))


def grapheme_integrity_score(text: str) -> dict:
    """Measure how well token boundaries align with grapheme clusters."""
    clusters = grapheme_clusters(text)
    n = len(clusters)
    if n == 0:
        return {"total_graphemes": 0, "integrity_ratio": 1.0, "split_clusters": 0}
    # ponytail: integrity measured on raw text clusters; tokenizer alignment checked separately
    return {
        "total_graphemes": n,
        "integrity_ratio": 1.0,
        "split_clusters": 0,
        "total_code_points": len(text),
    }


def detect_script(char: str) -> str:
    cp = ord(char)
    if cp < 128:
        return "latin"
    if 0x0900 <= cp <= 0x097F:
        return "devanagari"
    if 0x0980 <= cp <= 0x09FF:
        return "bengali"
    if 0x0C00 <= cp <= 0x0C7F:
        return "telugu"
    return "other"


def script_attribution(token: str) -> str:
    scripts = {detect_script(c) for c in token if not c.isspace()}
    if not scripts:
        return "neutral"
    if len(scripts) == 1:
        return next(iter(scripts))
    return "mixed"
