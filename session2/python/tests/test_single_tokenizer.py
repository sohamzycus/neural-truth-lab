"""Tests proving single-tokenizer architecture."""

from samabpe.bpe import BPETokenizer


MIXED_SAMPLES = [
    "India is a diverse country.",
    "भारत एक विविध देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "India भारत భారతదేశం ভারত",
]


def test_single_tokenizer_encodes_all_scripts(tmp_path):
    corpus = " ".join(MIXED_SAMPLES) * 5
    tok = BPETokenizer.train(corpus, vocab_size=500, pretokenization="whitespace")
    for sample in MIXED_SAMPLES:
        tokens = tok.encode(sample)
        assert len(tokens) > 0
        ids = tok.encode_ids(sample)
        assert all(0 <= i < tok.vocab_size for i in ids)


def test_no_language_routing():
    """Same tokenizer object handles all scripts — no per-language selection."""
    corpus = "\n".join(MIXED_SAMPLES)
    tok = BPETokenizer.train(corpus, vocab_size=400, pretokenization="whitespace")
    en = tok.count_tokens("India test")
    hi = tok.count_tokens("भारत परीक्षा")
    assert en > 0 and hi > 0
    assert tok.pretokenization == "whitespace"


def test_deterministic_encode():
    corpus = "deterministic test " * 20
    tok = BPETokenizer.train(corpus, vocab_size=100, pretokenization="whitespace")
    a = tok.encode_ids("deterministic test")
    b = tok.encode_ids("deterministic test")
    assert a == b
