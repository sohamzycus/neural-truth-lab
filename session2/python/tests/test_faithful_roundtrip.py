"""Faithful encode→decode round-trip tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from samabpe.evaluator_contract import REVIEWER_SAMPLE, verify_roundtrip, visible_non_whitespace
from samabpe.hf_bpe_trainer import build_hf_bpe_template, load_faithful_corpora

SAMPLES = [
    REVIEWER_SAMPLE,
    "[India](https://en.wikipedia.org/wiki/India)",
    "https://en.wikipedia.org/wiki/India?x=1&y=2#History",
    "[India] (भारत) {বাংলা}",
    "1,428,627,663.50",
    "India's history isn't simple.",
    "**India** _भारत_ ~~test~~",
    "| Country | Population |",
    "## History of India",
    "India[1][2][citation needed]",
    "भारत एक विविध देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "India भारत తెలుగు বাংলা — 2026!",
    "₹ $ % + = / \\ : ; # & ? !",
]


@pytest.fixture(scope="module")
def trained_tokenizer() -> Tokenizer:
    """Small tokenizer trained on faithful corpora for round-trip tests."""
    from samabpe.hf_bpe_trainer import train_hf_bpe

    corpora = load_faithful_corpora(ROOT / "data" / "faithful")
    tok, meta = train_hf_bpe(corpora, vocab_size=8000)
    assert meta["roundtrip"]["valid"], meta["roundtrip"]
    return tok


def test_reviewer_sample_roundtrip(trained_tokenizer: Tokenizer):
    text = REVIEWER_SAMPLE
    enc = trained_tokenizer.encode(text)
    dec = trained_tokenizer.decode(enc.ids)
    assert verify_roundtrip(trained_tokenizer, text)
    assert "India" in dec
    assert "'" in dec
    assert "," in dec
    assert "." in dec


@pytest.mark.parametrize("text", SAMPLES)
def test_sample_roundtrip(trained_tokenizer: Tokenizer, text: str):
    if not verify_roundtrip(trained_tokenizer, text):
        enc = trained_tokenizer.encode(text)
        dec = trained_tokenizer.decode(enc.ids)
        pytest.fail(
            f"Round-trip failed for {text!r}\n"
            f"  visible in:  {visible_non_whitespace(text)!r}\n"
            f"  visible out: {visible_non_whitespace(dec)!r}"
        )


def test_full_corpus_roundtrip(trained_tokenizer: Tokenizer):
    corpora = load_faithful_corpora(ROOT / "data" / "faithful")
    for lang, text in corpora.items():
        assert verify_roundtrip(trained_tokenizer, text), lang


def test_faithful_unit_reviewer_sample():
    from samabpe.evaluator_contract import extract_faithful_units

    units = extract_faithful_units(REVIEWER_SAMPLE)
    assert "India" in units
    assert "'" in units
    assert "s" in units
    assert "," in units
    assert "." in units
    assert "1" in units
