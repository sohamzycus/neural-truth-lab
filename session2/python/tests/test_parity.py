"""Parity and verification tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from samabpe.bpe import BPETokenizer
from samabpe.verify_core import run_verification

ROOT = Path(__file__).resolve().parents[2]
TOK_PATH = ROOT / "results" / "tokenizer.json"
CORPORA = ROOT / "data" / "frozen"
PARITY = ROOT / "results" / "parity_corpus.json"


@pytest.fixture(scope="module")
def tok():
    if not TOK_PATH.exists():
        pytest.skip("tokenizer.json not built")
    return BPETokenizer.load(TOK_PATH)


def test_verification_score_formula():
    if not TOK_PATH.exists():
        pytest.skip("tokenizer.json not built")
    r = run_verification(TOK_PATH, CORPORA)
    assert abs(r.score - 1000.0 / r.max_min_gap) < 1e-6
    assert r.sorted_x == sorted(r.fertilities.values())
    assert r.x_min == min(r.fertilities.values())
    assert r.x_max == max(r.fertilities.values())


def test_verification_constraints():
    if not TOK_PATH.exists():
        pytest.skip("tokenizer.json not built")
    r = run_verification(TOK_PATH, CORPORA)
    assert r.vocabulary_size <= 10_000
    assert r.fertilities["en"] <= 1.2


def test_parity_corpus_matches(tok):
    if not PARITY.exists():
        from scripts.generate_parity_corpus import generate
        generate(PARITY)
    cases = json.loads(PARITY.read_text(encoding="utf-8"))
    assert len(cases) >= 100
    for case in cases:
        text = case["text"]
        tokens = tok.encode(text)
        ids = tok.encode_ids(text)
        assert len(tokens) == len(ids)
        assert len(ids) == tok.count_tokens(text)
        assert all(0 <= i < tok.vocab_size for i in ids)


def test_mixed_script_parity(tok):
    text = "India भारत భారతదేశం ভারত"
    a = tok.encode(text)
    b = tok.encode(text)
    assert a == b
    assert len(a) > 0
