"""Tests for grapheme integrity measurement."""

from samabpe.bpe import BPETokenizer
from samabpe.unicode_utils import grapheme_clusters, measure_tokenizer_grapheme_integrity


def test_grapheme_clusters_devanagari():
    clusters = grapheme_clusters("कृषि")
    assert len(clusters) >= 1


def test_integrity_measured_not_hardcoded():
    corpus = "भारत భారతదేశం ভারত test " * 30
    tok = BPETokenizer.train(corpus, vocab_size=200, pretokenization="whitespace")
    m = measure_tokenizer_grapheme_integrity(tok, "भारत एक देश है।")
    assert "integrity_pct" in m
    assert "split_clusters" in m
    assert 0 <= m["integrity_pct"] <= 100
