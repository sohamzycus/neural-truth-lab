"""HF tokenizer load and evaluation smoke tests."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from tokenizers import Tokenizer

from samabpe.hf_bpe import (
    build_bpe_tokenizer,
    evaluate_hf_tokenizer,
    load_faithful_corpora,
    train_hf_bpe,
    VOCAB_BUDGET,
)

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
CAND = ROOT / "results" / "evaluator_candidates" / "01_reference_shared_bpe.json"


@pytest.fixture(scope="module")
def faithful_corpora():
    if not (CORPUS / "en.faithful.md").exists():
        pytest.skip("faithful corpora not built")
    return load_faithful_corpora(CORPUS)


def test_standard_tokenizer_load():
    if not CAND.exists():
        pytest.skip("baseline tokenizer not trained")
    tok = Tokenizer.from_file(str(CAND))
    assert tok.get_vocab_size(with_added_tokens=True) <= VOCAB_BUDGET


def test_vocabulary_size_at_most_10k(faithful_corpora):
    if CAND.exists():
        tok = Tokenizer.from_file(str(CAND))
        assert tok.get_vocab_size(with_added_tokens=True) <= 10_000
        return
    tok = train_hf_bpe(faithful_corpora, vocab_size=VOCAB_BUDGET)
    assert tok.get_vocab_size(with_added_tokens=True) <= 10_000


def test_full_corpus_encoding_deterministic(faithful_corpora):
    if not CAND.exists():
        pytest.skip("baseline not trained")
    tok = Tokenizer.from_file(str(CAND))
    text = faithful_corpora["en"]
    a = tok.encode(text).ids
    b = tok.encode(text).ids
    assert a == b
    assert len(a) > 0


def test_mixed_script_encoder(faithful_corpora):
    if not CAND.exists():
        pytest.skip("baseline not trained")
    tok = Tokenizer.from_file(str(CAND))
    text = "India भारत తెలుగు বাংলা"
    enc = tok.encode(text)
    assert len(enc.ids) == len(enc.tokens)


def test_evaluator_metrics_shape(faithful_corpora):
    if not CAND.exists():
        pytest.skip("baseline not trained")
    tok = Tokenizer.from_file(str(CAND))
    m = evaluate_hf_tokenizer(tok, faithful_corpora)
    assert m.hindi_penalty >= 1.0
    assert m.adjusted_score <= m.raw_score
    assert set(m.fertilities) == {"en", "hi", "te", "bn"}


def test_tokenizer_sha256_stable():
    if not CAND.exists():
        pytest.skip("baseline not trained")
    h1 = hashlib.sha256(CAND.read_bytes()).hexdigest()
    h2 = hashlib.sha256(CAND.read_bytes()).hexdigest()
    assert h1 == h2


def test_build_template_trains_on_tiny_corpus():
    from pathlib import Path
    from tempfile import NamedTemporaryFile

    from tokenizers import trainers

    tok = build_bpe_tokenizer()
    trainer = trainers.BpeTrainer(vocab_size=50, min_frequency=1, special_tokens=["<unk>"])
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write("Hello world\n")
        p = f.name
    try:
        tok.train([p], trainer)
        enc = tok.encode("Hello, world!")
        assert len(enc.ids) >= 1
    finally:
        Path(p).unlink(missing_ok=True)
