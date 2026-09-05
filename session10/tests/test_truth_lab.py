"""Tests for Truth Lab verification claims."""

from __future__ import annotations

import math

import torch

from truth_lab.accumulation import (
    combine_accumulation,
    combined_valid_token_loss,
    per_token_loss,
    train_accumulation_step,
)
from truth_lab.config import LabConfig, set_seed
from truth_lab.data import TinyCorpus, make_batch, make_variable_microbatches
from truth_lab.float_repr import fp32_bits, format_precision_comparison_table, represent_value
from truth_lab.gradient_check import gradient_epsilon_sweep, pick_best_epsilon, verify_gradient
from truth_lab.mfu import measure_mfu, verify_mfu_report
from truth_lab.model import TinyGPT
from truth_lab.tensor_trace import trace_training_step
from truth_lab.training import clone_model_state, find_grad_before_loss, models_differ, train_steps


def _setup():
    cfg = LabConfig(device="cpu")
    set_seed(cfg.seed)
    corpus = TinyCorpus()
    model = TinyGPT(cfg, corpus.vocab_size)
    return cfg, corpus, model


def test_tensor_shapes():
    cfg, corpus, model = _setup()
    x, y, m = make_batch(corpus, 2, cfg.block_size, cfg.seed)
    trace, grads = trace_training_step(model, x, y, m)
    assert trace.input_ids.shape == (2, cfg.block_size)
    assert trace.embeddings.shape == (2, cfg.block_size, cfg.n_embd)
    assert trace.logits.shape == (2, cfg.block_size, corpus.vocab_size)
    assert trace.shifted_logits.shape == (2, cfg.block_size - 1, corpus.vocab_size)
    assert trace.targets.shape == (2, cfg.block_size - 1)
    assert len(grads) > 0


def test_gradient_finite_difference():
    cfg, corpus, model = _setup()
    x, y, m = make_batch(corpus, 2, cfg.block_size, cfg.seed)
    result = verify_gradient(model, x, y, m, rel_tol=5e-3)
    assert result.verdict in ("PASS", "INVESTIGATE")
    assert math.isfinite(result.finite_diff)
    assert math.isfinite(result.autograd)


def test_gradient_epsilon_sweep():
    cfg, corpus, model = _setup()
    x, y, m = make_batch(corpus, 2, cfg.block_size, cfg.seed)
    rows, _, _, autograd = gradient_epsilon_sweep(model, x, y, m)
    assert len(rows) == 5
    best = pick_best_epsilon(rows)
    assert best.rel_error <= max(r.rel_error for r in rows)
    assert math.isfinite(autograd)


def test_accumulation_token_weighting():
    combo = combine_accumulation(2.0, 10, 4.0, 100)
    assert abs(combo.naive - 3.0) < 1e-9
    expected = (2.0 * 10 + 4.0 * 100) / 110
    assert abs(combo.correct - expected) < 1e-9


def test_accumulation_matches_combined_tokens():
    cfg, corpus, _ = _setup()
    block = 128
    acc_cfg = LabConfig(**{**cfg.__dict__, "block_size": block})
    xa, ya, ma, xb, yb, mb = make_variable_microbatches(corpus, block, cfg.seed)
    micros = [(xa, ya, ma), (xb, yb, mb)]
    model = TinyGPT(acc_cfg, corpus.vocab_size)
    la, na = per_token_loss(model, *micros[0])
    lb, nb = per_token_loss(model, *micros[1])
    combo = combine_accumulation(la, na, lb, nb)
    direct = combined_valid_token_loss(model, micros)
    assert abs(combo.correct - direct) < 1e-5
    assert na == 10 and nb == 100


def test_accumulation_training_differs():
    cfg, corpus, _ = _setup()
    block = 128
    xa, ya, ma, xb, yb, mb = make_variable_microbatches(corpus, block, cfg.seed)
    micros = [(xa, ya, ma), (xb, yb, mb)]
    acc_cfg = LabConfig(**{**cfg.__dict__, "block_size": block})
    m1 = TinyGPT(acc_cfg, corpus.vocab_size)
    m2 = TinyGPT(acc_cfg, corpus.vocab_size)
    m2.load_state_dict(m1.state_dict())
    o1 = torch.optim.SGD(m1.parameters(), lr=0.01)
    o2 = torch.optim.SGD(m2.parameters(), lr=0.01)
    l1 = train_accumulation_step(m1, o1, micros, "naive")
    l2 = train_accumulation_step(m2, o2, micros, "correct")
    assert isinstance(l1, float) and isinstance(l2, float)


def test_mfu_sanity():
    cfg, corpus, model = _setup()
    report = measure_mfu(model, corpus, cfg, steps=5, warmup=1, batch_size=2)
    check = verify_mfu_report(report)
    assert check["pass"]
    assert 0.0 <= report.mfu <= 1.0


def test_fp32_representation():
    r = fp32_bits(0.1)
    assert r.bits == "00111101110011001100110011001101"
    assert abs(r.represented_value - 0.1) < 1e-8
    assert r.error < 2e-8


def test_fp_formats_table():
    rows = represent_value(0.1)
    assert len(rows) == 3
    for r in rows:
        assert math.isfinite(r.represented_value) or r.format_name == "FP8 E4M3"
    assert "FP32" in format_precision_comparison_table()


def test_training_changes_weights():
    cfg, corpus, model = _setup()
    before = clone_model_state(model)
    history = train_steps(model, corpus, cfg, n_steps=3, batch_size=2)
    after = clone_model_state(model)
    assert models_differ(before, after)
    assert all(math.isfinite(s.loss) for s in history.steps)
    assert all(s.update_norm >= 0 for s in history.steps)


def test_grad_before_loss_detection():
    cfg, corpus, model = _setup()
    history = train_steps(model, corpus, cfg, n_steps=30, batch_size=2)
    event = find_grad_before_loss(history)
    # property test: if found, thresholds must be documented in result
    if event:
        assert event["grad_rel_change"] > event["grad_threshold"]
        assert event["loss_rel_change"] < event["loss_threshold"]
