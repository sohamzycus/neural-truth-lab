"""Vocabulary ROI analysis — tokens saved per vocab slot."""

from __future__ import annotations

from collections import Counter

from samabpe.bpe import BPETokenizer
from samabpe.strategies import LANGS
from samabpe.word_units import count_word_units, word_units


def compute_vocab_roi(tok: BPETokenizer, corpora: dict[str, str], top_n: int = 50) -> dict:
    """
    For frequent word units, estimate ROI of better compression.

    ROI = (chars - tokens) proxy savings / 1 vocab slot for high-frequency units.
    """
    entries: list[dict] = []

    for lang in LANGS:
        text = corpora[lang]
        wu_list = word_units(text)
        freq = Counter(wu_list)
        for w, count in freq.most_common(top_n):
            tokens = tok.encode(w + "</w>" if not w.endswith("</w>") else w)
            # ponytail: per-word encode approximates unit cost; full-article uses same tokenizer
            char_len = len(w)
            tok_count = len(tokens)
            savings = max(0, char_len - tok_count) * count
            entries.append({
                "word": w[:80],
                "language": lang,
                "frequency": count,
                "token_count": tok_count,
                "char_length": char_len,
                "tokens_saved_estimate": savings,
                "roi_estimate": savings / max(tok_count, 1),
            })

    entries.sort(key=lambda e: e["tokens_saved_estimate"], reverse=True)
    return {
        "definition": "Vocabulary ROI = estimated evaluation tokens saved / token slots used for that word",
        "top_opportunities": entries[:top_n],
        "worst_language": max(
            LANGS,
            key=lambda l: sum(1 for e in entries if e["language"] == l),
        ),
    }
