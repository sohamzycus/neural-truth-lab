"""Cross-source consistency — fresh evaluator vs saved artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / "submission"
WEB_VERIFIED = ROOT / "web" / "public" / "data" / "verifiedSubmission.json"


@pytest.fixture(scope="module")
def fresh():
    import sys

    sys.path.insert(0, str(ROOT / "python"))
    from samabpe.submission_audit import build_verified_submission

    return build_verified_submission(SUB)


@pytest.fixture(scope="module")
def saved_metrics():
    return json.loads((SUB / "metrics.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def provenance():
    return json.loads((SUB / "provenance.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def web_verified():
    assert WEB_VERIFIED.exists(), "run scripts/generate_verified_submission_data.py"
    return json.loads(WEB_VERIFIED.read_text(encoding="utf-8"))


def test_languages_exactly_four(fresh):
    assert fresh["languages"] == ["en", "hi", "te", "bn"]


def test_vocab_size(fresh):
    assert fresh["tokenizer"]["vocab_size"] == 10_000
    assert fresh["tokenizer"]["vocab_size"] <= 10_000


def test_tokenizer_hash_consistent(fresh, saved_metrics, provenance, web_verified):
    sha = fresh["tokenizer_sha256"]
    assert saved_metrics["tokenizer"]["sha256"] == sha
    assert provenance["tokenizer_sha256"] == sha
    assert web_verified["tokenizer"]["sha256"] == sha


def test_corpus_hashes(fresh, web_verified):
    for lang in ("en", "hi", "te", "bn"):
        assert fresh["corpora"][lang]["sha256"] == web_verified["corpora"][lang]["sha256"]


def test_faithful_units_and_tokens(fresh, saved_metrics, web_verified):
    for lang in ("en", "hi", "te", "bn"):
        fu = fresh["metrics"]["faithful_unit_counts"][lang]
        tc = fresh["metrics"]["token_counts"][lang]
        fert = fresh["metrics"]["fertilities"][lang]
        assert saved_metrics["languages"][lang]["faithful_units"] == fu
        assert saved_metrics["languages"][lang]["tokens"] == tc
        assert abs(saved_metrics["languages"][lang]["fertility"] - fert) < 1e-9
        assert web_verified["metrics"]["faithful_unit_counts"][lang] == fu
        assert web_verified["metrics"]["token_counts"][lang] == tc


def test_thresholds(fresh, saved_metrics, web_verified):
    for key in ("en_under_1_2", "hi_under_1_2"):
        assert fresh["thresholds"][key] is True
        assert saved_metrics["thresholds"][key] is True
        assert web_verified["thresholds"][key] is True


def test_scoring(fresh, saved_metrics, web_verified):
    for field in ("spread", "raw_score", "hindi_penalty", "adjusted_score"):
        a = fresh["metrics"][field]
        b = saved_metrics["scoring"][field if field != "adjusted_score" else "adjusted_score"]
        c = web_verified["metrics"][field]
        assert abs(a - b) < 1e-6
        assert abs(a - c) < 1e-6


def test_weights(provenance, web_verified):
    w = {"en": 3, "hi": 5, "te": 9, "bn": 5}
    assert provenance["weights"] == w
    assert web_verified["provenance"]["weights"] == w


def test_roundtrip_gate(fresh):
    assert fresh["roundtrip"]["reviewer_sample"] is True
    assert all(fresh["roundtrip"]["full_corpus"].values())


def test_vocab_composition_sums(fresh):
    comp = fresh["vocabularyComposition"]
    assert comp["sum_matches_vocab_size"]
    assert sum(comp["categories"].values()) == comp["vocab_size"]


def test_architecture_verified(fresh):
    assert fresh["tokenizer"]["verified"] is True
