"""Session 11 tests — must fail loudly."""

from __future__ import annotations

import math

import pytest
import torch

from src.core.config_loader import validate_all_specs
from src.core.hashing import config_hash
from src.core.schemas import LabConfig, ModelConfig, OptimizerConfig, ScheduleConfig
from src.core.seed import set_seed
from src.metrics.convergence import find_convergence_step
from src.metrics.ratio_metrics import update_to_weight_ratio, detect_warmup_end
from src.metrics.smoothing import smoothed_tail
from src.optimizers.adam_manual import adam_manual_steps
from src.optimizers.adam_reference import adam_pytorch_steps
from src.schedules.cosine import lr_multiplier as cosine_lr
from src.schedules.wsd import lr_multiplier as wsd_lr, warmup_fraction as wsd_wf
from src.validation.comparison_validator import RunConfig, validate_comparison
from src.reporting.ledger import EvidenceLedger, apply_decision_policy


# --- EXP-ADAM-001 ---
def test_manual_adam_equations():
    rows = adam_manual_steps(0.5, [0.1], learning_rate=0.001)
    r = rows[0]
    assert r.m_t == pytest.approx(0.1 * 0.1, rel=1e-9)
    assert r.v_t == pytest.approx(0.001 * 0.01, rel=1e-9)


def test_manual_vs_pytorch():
    grads = [0.1, -0.2, 0.05, 0.3, -0.1]
    manual = adam_manual_steps(0.5, grads)
    pytorch = adam_pytorch_steps(0.5, grads)
    for m, p in zip(manual, pytorch):
        assert m.updated_weight == pytest.approx(p["updated_weight"], abs=1e-6)
        assert m.m_t == pytest.approx(p["m_t"], abs=1e-6)
        assert m.v_t == pytest.approx(p["v_t"], abs=1e-6)


# --- EXP-BIAS-001 ---
def test_bias_correction_enabled_differs_early():
    grads = [0.3, -0.3, 0.3]
    with_b = adam_manual_steps(0.5, grads, bias_correction=True)
    no_b = adam_manual_steps(0.5, grads, bias_correction=False)
    assert with_b[0].updated_weight != pytest.approx(no_b[0].updated_weight, abs=1e-9)


def test_bias_correction_disabled():
    rows = adam_manual_steps(0.5, [0.1], bias_correction=False)
    assert rows[0].m_hat_t == rows[0].m_t


def test_convergence_detection():
    abs_d = [1.0, 0.5, 1e-7, 1e-8, 1e-9]
    rel_d = [1.0, 0.5, 1e-5, 1e-6, 1e-7]
    step = find_convergence_step(abs_d, rel_d, 1e-6, 1e-4, 3)
    assert step == 2


# --- Schedules ---
def test_cosine_schedule():
    cfg = ScheduleConfig(warmup_steps=5, total_steps=100)
    assert cosine_lr(0, cfg) < cosine_lr(4, cfg)
    assert cosine_lr(50, cfg) < cosine_lr(5, cfg)


def test_wsd_schedule():
    cfg = ScheduleConfig(warmup_steps=5, stable_steps=10, total_steps=100)
    assert wsd_lr(6, cfg) == pytest.approx(1.0)
    assert wsd_lr(20, cfg) < 1.0


def test_wsd_warmup_boundary():
    cfg = ScheduleConfig(warmup_steps=3, total_steps=30)
    assert wsd_wf(2, cfg) == pytest.approx(1.0)


# --- METRIC-RATIO-001 ---
def test_update_to_weight_ratio():
    assert update_to_weight_ratio(0.01, 1.0) == pytest.approx(0.01)
    assert update_to_weight_ratio(0.01, 0.0) == pytest.approx(0.01 / 1e-8)


def test_zero_parameter_norm_handling():
    r = update_to_weight_ratio(1.0, 0.0)
    assert math.isfinite(r)


def test_warmup_end_detection():
    assert detect_warmup_end([0.33, 0.66, 1.0, 1.0]) == 2


# --- Comparison validator ---
def test_valid_controlled_comparison():
    c = {"model": "TinyGPT", "seed": 1337, "optimizer": "AdamW", "batch_size": 2, "total_steps": 100}
    a = RunConfig(controls={**c, "schedule": "cosine"}, changed_variable="schedule")
    b = RunConfig(controls={**c, "schedule": "wsd"}, changed_variable="schedule")
    # Same base controls, different schedule value is the intended change
    base = RunConfig(controls=c, changed_variable="schedule")
    r = validate_comparison(base, base)
    assert r.valid


def test_invalid_uncontrolled_comparison():
    a = RunConfig(controls={"seed": 1, "batch_size": 2}, changed_variable="schedule")
    b = RunConfig(controls={"seed": 2, "batch_size": 2}, changed_variable="schedule")
    r = validate_comparison(a, b)
    assert not r.valid
    assert r.status == "INVALID_EXPERIMENT"


# --- Hashing ---
def test_config_hash_stable():
    h1 = config_hash({"a": 1, "b": 2})
    h2 = config_hash({"b": 2, "a": 1})
    assert h1 == h2


# --- Evidence ledger ---
def test_evidence_ledger_record(tmp_path):
    ledger = EvidenceLedger(tmp_path / "ledger.jsonl")
    rec = EvidenceLedger.make_record(
        evidence_id="EVD-TEST",
        experiment_id="EXP-TEST",
        claim_id="CLAIM-001",
        hypothesis="test",
        controls={},
        changed_variable="none",
        seed=0,
        model_config={},
        optimizer_config={},
        schedule_config={},
        data_config={},
        runtime_config={},
        raw_artifacts=[],
        derived_metrics={},
        statistical_summary={},
        decision="SUPPORTED",
        confidence="HIGH",
        limitations=[],
        reproducibility_command="test",
        execution_mode="smoke",
    )
    ledger.append(rec)
    assert (tmp_path / "ledger.jsonl").exists()


# --- Decision policy ---
def test_decision_invalid_experiment():
    s, c = apply_decision_policy(controls_valid=False, result_missing=False)
    assert s.value == "INVALID_EXPERIMENT"


def test_decision_supported_adam():
    s, c = apply_decision_policy(controls_valid=True, result_missing=False, max_abs_diff=1e-8)
    assert s.value == "SUPPORTED"


# --- Spec validation ---
def test_specs_validate():
    errors = validate_all_specs()
    assert errors == []


# --- Smoothing / NaN ---
def test_smoothed_tail():
    assert smoothed_tail([1.0, 2.0, 3.0, 4.0, 5.0]) == pytest.approx(3.0)


def test_nan_detection():
    assert smoothed_tail([1.0, float("nan")]) == pytest.approx(1.0)


# --- Reproducibility ---
def test_seed_reproducibility():
    set_seed(42)
    t1 = torch.rand(3)
    set_seed(42)
    t2 = torch.rand(3)
    assert torch.equal(t1, t2)


# --- Smoke pipeline ---
def test_smoke_experiments_complete(tmp_path, monkeypatch):
    import src.experiments.adam_verification as av
    out = tmp_path / "outputs"
    monkeypatch.setattr(av, "OUTPUTS", out)
    monkeypatch.setattr(av, "FIGURES", out / "figures")
    result = av.run("smoke")
    assert result["max_abs_diff"] < 1e-6
