"""Tests for BPE encode/decode."""

from samabpe.bpe import BPETokenizer, END_OF_WORD


def test_train_and_encode_deterministic():
    corpus = "low lower lowest"
    tok1 = BPETokenizer.train(corpus, vocab_size=50, pretokenization="whitespace")
    tok2 = BPETokenizer.train(corpus, vocab_size=50, pretokenization="whitespace")
    text = "lower lowest"
    assert tok1.encode(text) == tok2.encode(text)
    assert tok1.count_tokens(text) == len(tok1.encode(text))


def test_roundtrip_whitespace():
    corpus = "the cat sat on the mat " * 20
    tok = BPETokenizer.train(corpus, vocab_size=80, pretokenization="whitespace")
    sample = "the cat sat"
    tokens = tok.encode(sample)
    decoded = tok.decode(tokens)
    assert "the" in decoded and "cat" in decoded


def test_vocab_size_cap():
    corpus = "abcdefghij " * 100
    tok = BPETokenizer.train(corpus, vocab_size=64, pretokenization="whitespace")
    assert tok.vocab_size <= 64


def test_save_load_roundtrip(tmp_path):
    corpus = "token test text " * 30
    tok = BPETokenizer.train(corpus, vocab_size=60, pretokenization="whitespace")
    path = tmp_path / "tok.json"
    tok.save(path)
    loaded = BPETokenizer.load(path)
    sample = "token test"
    assert loaded.encode(sample) == tok.encode(sample)
