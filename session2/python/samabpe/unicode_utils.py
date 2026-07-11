"""Unicode and grapheme utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from samabpe.word_units import normalize_nfc

if TYPE_CHECKING:
    from samabpe.bpe import BPETokenizer

GRAPHEME_RE = re.compile(r"\X", re.UNICODE)


def grapheme_clusters(text: str) -> list[str]:
    return GRAPHEME_RE.findall(normalize_nfc(text))


def code_points(token: str) -> list[str]:
    return [f"U+{ord(c):04X}" for c in token]


def grapheme_count(token: str) -> int:
    return len(grapheme_clusters(token))


def _cluster_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for m in GRAPHEME_RE.finditer(normalize_nfc(text)):
        spans.append((m.start(), m.end()))
    return spans


def measure_tokenizer_grapheme_integrity(tok: "BPETokenizer", text: str) -> dict:
    """
    Measure whether BPE token boundaries fall inside extended grapheme clusters.

    integrity_pct = boundaries aligned with cluster edges / total boundaries * 100
    split_clusters = grapheme clusters touched by more than one token
    """
    nfc = normalize_nfc(text)
    clusters = _cluster_spans(nfc)
    if not clusters:
        return {
            "total_graphemes": 0,
            "total_code_points": len(nfc),
            "token_boundaries": 0,
            "boundaries_inside_cluster": 0,
            "split_clusters": 0,
            "integrity_pct": 100.0,
        }

    # Reconstruct token char spans by decoding encode positions
    tokens = tok.encode(nfc)
    pos = 0
    boundaries: set[int] = {0}
    for token in tokens:
        raw = token.replace("</w>", "")
        if not raw:
            continue
        idx = nfc.find(raw, pos)
        if idx < 0:
            pos += len(raw)
            continue
        boundaries.add(idx)
        pos = idx + len(raw)
        boundaries.add(pos)
    boundaries.add(len(nfc))

    cluster_starts = {s for s, _ in clusters}
    cluster_ends = {e for _, e in clusters}
    aligned = sum(1 for b in boundaries if b in cluster_starts or b in cluster_ends)
    split = 0
    for start, end in clusters:
        inside = [b for b in boundaries if start < b < end]
        if inside:
            split += 1

    total_boundaries = max(len(boundaries) - 1, 1)
    integrity = (aligned / len(boundaries)) * 100 if boundaries else 100.0

    return {
        "total_graphemes": len(clusters),
        "total_code_points": len(nfc),
        "token_boundaries": total_boundaries,
        "boundaries_inside_cluster": len(boundaries) - aligned,
        "split_clusters": split,
        "integrity_pct": round(integrity, 4),
    }


def grapheme_integrity_for_language(tok: "BPETokenizer", text: str, lang: str) -> dict:
    m = measure_tokenizer_grapheme_integrity(tok, text)
    m["language"] = lang
    return m


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
    if char.isdigit():
        return "digits"
    return "other"


def script_category(token: str) -> str:
    scripts = {detect_script(c) for c in token if not c.isspace() and c != "<" and c != ">"}
    scripts.discard("other")
    if not scripts:
        if token in ("<unk>", "<pad>") or token.endswith("</w>"):
            return "special"
        return "neutral"
    if len(scripts) == 1:
        return next(iter(scripts))
    return "shared"


def script_attribution(token: str) -> str:
    return script_category(token)


def vocab_script_attribution(tok: "BPETokenizer") -> dict[str, int]:
    """Attribute vocabulary slots by script category (sums to vocab size)."""
    counts: dict[str, int] = {}
    for token in tok.vocab:
        if token in ("<unk>", "<pad>"):
            cat = "special"
        else:
            cat = script_category(token.replace("</w>", ""))
        counts[cat] = counts.get(cat, 0) + 1
    return counts
