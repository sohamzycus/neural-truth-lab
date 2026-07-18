"""Tests for India-First 40B quantitative models."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))

from india40b.data_mix import compute_data_mix
from india40b.language_weights import compute_mcda_weights
from india40b.training_cost import compute_training_cost
from india40b.vocab_derivation import derive_vocab_allocation


def test_vocab_sums_to_128k():
    v = derive_vocab_allocation()
    assert v["total_vocab"] == 128_000
    assert sum(v["buckets"].values()) == 128_000


def test_mcda_weights_sum_to_one():
    w = compute_mcda_weights()["weights"]
    assert abs(sum(w.values()) - 1.0) < 1e-6


def test_hindi_below_population_share():
    lw = compute_mcda_weights()
    assert lw["hindi_mcda_vs_population"]["mcda_percent"] < lw["hindi_mcda_vs_population"]["population_percent"]


def test_data_mix_total():
    dm = compute_data_mix()
    assert dm["slice_tokens_billions"]["natural_language"] == 984.0


def test_budget_is_100m():
    assert compute_training_cost()["total_budget_usd_m"] == 100
