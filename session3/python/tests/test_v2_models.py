"""Tests for V2 derived models."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "models"))

from india40b.capability_data import compute_capability_data
from india40b.cleaning_pipeline import compute_cleaning_pipeline
from india40b.vocab_size_tradeoff import compute_vocab_size_tradeoff


def test_cleaning_sixteen_stages():
    cp = compute_cleaning_pipeline()
    assert cp["stage_count"] == 16
    assert cp["composite_yield_percent"] > 0


def test_vocab_128k_wins():
    vt = compute_vocab_size_tradeoff()
    chosen = [o for o in vt["options"] if o["chosen"]]
    assert len(chosen) == 1 and chosen[0]["label"] == "128k"


def test_capability_count():
    cd = compute_capability_data()
    assert cd["capability_count"] == 10
