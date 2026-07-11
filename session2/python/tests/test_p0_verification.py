"""P0 verification integrity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from samabpe.bpe import BPETokenizer
from samabpe.verify_core import run_verification, sha256_file

ROOT = Path(__file__).resolve().parents[2]
TOK = ROOT / "results" / "tokenizer.json"
DATA = ROOT / "data" / "frozen"
BASELINE = ROOT / "results" / "baseline_verification.json"
FINAL_PASS = ROOT / "results" / "final_pass_baseline.json"


def test_vocab_size_from_loaded_artefact():
    if not TOK.exists():
        pytest.skip("tokenizer not built")
    tok = BPETokenizer.load(TOK)
    r = run_verification(TOK, DATA)
    assert r.vocabulary_size == tok.vocab_size == len(tok.vocab)
    assert r.vocabulary_size <= 10_000


def test_full_precision_score_formula():
    if not TOK.exists():
        pytest.skip("tokenizer not built")
    r = run_verification(TOK, DATA)
    assert abs(r.score - 1000.0 / r.max_min_gap) < 1e-9
    assert r.sorted_x == sorted(r.fertilities.values())


def test_baseline_immutable_when_present():
    if not BASELINE.exists():
        pytest.skip("baseline not recorded")
    b = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert b.get("immutable") is True
    assert "tokenizer_sha256" in b
    assert b["score"] == pytest.approx(1000.0 / b["max_min_gap"], rel=0, abs=1e-9)


def test_final_pass_baseline_immutable():
    if not FINAL_PASS.exists():
        pytest.skip("final_pass_baseline not recorded")
    b = json.loads(FINAL_PASS.read_text(encoding="utf-8"))
    assert b.get("immutable") is True
    assert b["vocabulary_size"] <= 10_000
    assert b["english_constraint"]["pass"] is True


def test_scored_tokenizer_byte_identity():
    if not TOK.exists():
        pytest.skip("tokenizer not built")
    proof_path = ROOT / "results" / "artefact_proof.json"
    if not proof_path.exists():
        pytest.skip("artefact_proof not generated")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    assert proof["scored_tokenizer_sha256"] == sha256_file(TOK)
    for copy in proof.get("download_copies", []):
        assert copy["byte_identical_to_scored"] is True
