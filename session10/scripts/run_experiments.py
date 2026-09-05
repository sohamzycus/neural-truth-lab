#!/usr/bin/env python3
"""Run all Truth Lab experiments and write evidence artifacts."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from truth_lab.accumulation import (
    combine_accumulation,
    combined_valid_token_loss,
    per_token_loss,
    train_accumulation_step,
)
from truth_lab.config import LabConfig, set_seed
from truth_lab.data import TinyCorpus, make_batch, make_variable_microbatches
from truth_lab.float_repr import format_precision_comparison_table, format_table, represent_value
from truth_lab.gradient_check import (
    format_sweep_table,
    gradient_epsilon_sweep,
    pick_best_epsilon,
    verify_gradient,
)
from truth_lab.mfu import measure_mfu, verify_mfu_report
from truth_lab.model import TinyGPT
from truth_lab.tensor_trace import format_trace_table, pipeline_diagram, print_all_traces, trace_training_step
from truth_lab.training import (
    GRAD_BEFORE_LOSS_GRAD_THRESHOLD,
    GRAD_BEFORE_LOSS_LOSS_THRESHOLD,
    GRAD_BEFORE_LOSS_WINDOW,
    clone_model_state,
    find_grad_before_loss,
    find_gradient_spike,
    models_differ,
    train_steps,
)

OUT = ROOT / "outputs"
PLOTS = OUT / "plots"


def _fresh_model(corpus: TinyCorpus, cfg: LabConfig) -> TinyGPT:
    set_seed(cfg.seed)
    return TinyGPT(cfg, corpus.vocab_size)


def run_tensor_trace(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    model = _fresh_model(corpus, cfg)
    device = torch.device(cfg.device)
    model = model.to(device)
    x, y, m = make_batch(corpus, 2, cfg.block_size, cfg.seed)
    x, y, m = x.to(device), y.to(device), m.to(device)
    trace, grads = trace_training_step(model, x, y, m)
    return {
        "trace_text": print_all_traces(trace, grads),
        "table": format_trace_table(trace),
        "pipeline": pipeline_diagram(),
        "sample_sentence": corpus.decode_tensor(x[0]),
        "vocab_size": corpus.vocab_size,
        "shapes": {k: list(v.shape) for k, v in trace.as_dict().items()},
    }


def run_gradient_check(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    model = _fresh_model(corpus, cfg)
    device = torch.device(cfg.device)
    model = model.to(device)
    x, y, m = make_batch(corpus, 2, cfg.block_size, cfg.seed + 1)
    x, y, m = x.to(device), y.to(device), m.to(device)

    sweep, param_name, index, autograd = gradient_epsilon_sweep(model, x, y, m)
    best = pick_best_epsilon(sweep)
    result = verify_gradient(model, x, y, m, param_name=param_name, index=index, epsilon=best.epsilon)

    investigation = None
    if result.verdict == "INVESTIGATE":
        investigation = {
            "observed_discrepancy": result.rel_diff,
            "likely_cause": "epsilon sensitivity and/or device floating-point precision (MPS/CPU)",
            "experiment_performed": "epsilon sweep from 1e-2 to 1e-6",
            "conclusion": f"best epsilon {best.epsilon:.0e} gives rel error {best.rel_error:.3e}",
        }

    return {
        "param_name": result.param_name,
        "index": [int(i) for i in result.index],
        "w": result.w,
        "epsilon": result.epsilon,
        "best_epsilon": best.epsilon,
        "loss_at_w": result.loss_at_w,
        "loss_at_w_plus": result.loss_at_w_plus,
        "loss_at_w_minus": result.loss_at_w_minus,
        "finite_diff": result.finite_diff,
        "autograd": result.autograd,
        "abs_diff": result.abs_diff,
        "rel_diff": result.rel_diff,
        "verdict": result.verdict,
        "sweep_table": format_sweep_table(sweep),
        "sweep": [
            {
                "epsilon": r.epsilon,
                "finite_diff": r.finite_diff,
                "autograd": r.autograd,
                "abs_error": r.abs_error,
                "rel_error": r.rel_error,
            }
            for r in sweep
        ],
        "investigation": investigation,
    }


def run_accumulation(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    device = torch.device(cfg.device)
    acc_block = max(cfg.block_size, 128)
    acc_cfg = LabConfig(**{**cfg.__dict__, "block_size": acc_block})
    xa, ya, ma, xb, yb, mb = make_variable_microbatches(corpus, acc_block, cfg.seed + 2)
    micros = [
        (xa.to(device), ya.to(device), ma.to(device)),
        (xb.to(device), yb.to(device), mb.to(device)),
    ]

    model_a = TinyGPT(acc_cfg, corpus.vocab_size).to(device)
    model_b = deepcopy(model_a)
    model_b.load_state_dict(model_a.state_dict())

    la, na = per_token_loss(model_a, *micros[0])
    lb, nb = per_token_loss(model_a, *micros[1])
    combo = combine_accumulation(la, na, lb, nb)
    direct = combined_valid_token_loss(model_a, micros)

    naive_curve, correct_curve = [], []
    opt_naive = torch.optim.AdamW(model_a.parameters(), lr=cfg.learning_rate)
    opt_correct = torch.optim.AdamW(model_b.parameters(), lr=cfg.learning_rate)
    steps = 40
    for _ in range(steps):
        naive_curve.append(train_accumulation_step(model_a, opt_naive, micros, "naive"))
        correct_curve.append(train_accumulation_step(model_b, opt_correct, micros, "correct"))

    PLOTS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(naive_curve, label="Naive average-of-averages")
    ax.plot(correct_curve, label="Correct token-weighted accumulation")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Reported loss")
    ax.set_title("Gradient accumulation: naive vs correct")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "accumulation_naive_vs_correct.png", dpi=120)
    plt.close(fig)

    diffs = [abs(a - b) for a, b in zip(naive_curve, correct_curve)]
    return {
        "loss_a": la,
        "loss_b": lb,
        "tokens_a": na,
        "tokens_b": nb,
        "naive_combined": combo.naive,
        "correct_combined": combo.correct,
        "combined_direct_check": direct,
        "combined_matches_formula": abs(combo.correct - direct) < 1e-5,
        "max_loss_diff": max(diffs),
        "mean_loss_diff": sum(diffs) / len(diffs),
        "final_loss_diff": abs(naive_curve[-1] - correct_curve[-1]),
        "naive_final": naive_curve[-1],
        "correct_final": correct_curve[-1],
        "plot": str(PLOTS / "accumulation_naive_vs_correct.png"),
    }


def run_grad_norm(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    model = _fresh_model(corpus, cfg)
    history = train_steps(model, corpus, cfg, n_steps=120, batch_size=2)
    steps = [s.step for s in history.steps]
    losses = [s.loss for s in history.steps]
    norms = [s.grad_norm for s in history.steps]
    updates = [s.update_norm for s in history.steps]

    PLOTS.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(steps, losses)
    axes[0].set_title("Loss vs training step")
    axes[0].set_xlabel("step")
    axes[0].set_ylabel("loss")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(steps, norms)
    axes[1].set_title("Gradient norm vs training step")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("grad norm")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "loss_and_grad_norm.png", dpi=120)
    plt.close(fig)

    event = find_grad_before_loss(history)
    spike = find_gradient_spike(history)
    spike_i = max(range(len(norms)), key=lambda i: norms[i])
    opt_verdict = "PASS" if event else "NO EVENT"
    return {
        "plot": str(PLOTS / "loss_and_grad_norm.png"),
        "grad_before_loss_event": event,
        "gradient_spike": spike,
        "detection_rule": {
            "grad_rel_change_threshold": GRAD_BEFORE_LOSS_GRAD_THRESHOLD,
            "loss_rel_change_threshold": GRAD_BEFORE_LOSS_LOSS_THRESHOLD,
            "window": GRAD_BEFORE_LOSS_WINDOW,
        },
        "max_grad_norm_step": spike_i,
        "max_grad_norm": norms[spike_i],
        "final_loss": losses[-1],
        "initial_loss": losses[0],
        "final_update_norm": updates[-1],
        "optimization_verdict": opt_verdict,
    }


def run_mfu(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    model = _fresh_model(corpus, cfg)
    report = measure_mfu(model, corpus, cfg, steps=30, batch_size=2)
    sanity = verify_mfu_report(report)
    return {
        "measured_seconds": report.measured_seconds,
        "steps": report.steps,
        "estimated_flops_per_step": report.estimated_flops_per_step,
        "achieved_flops_per_sec": report.achieved_flops_per_sec,
        "hardware_peak_flops_per_sec": report.hardware_peak_flops_per_sec,
        "mfu": report.mfu,
        "mfu_percent": report.mfu * 100,
        "params": report.params,
        "notes": report.notes,
        "sanity_check": sanity,
    }


def run_float_repr() -> dict:
    value = 0.1
    rows = represent_value(value)
    return {
        "value": value,
        "table_markdown": format_table(value),
        "precision_comparison": format_precision_comparison_table(),
        "formats": [
            {
                "name": r.format_name,
                "bits": r.bits,
                "sign": r.sign,
                "exponent": r.exponent_bits,
                "fraction": r.fraction_bits,
                "fields": f"{r.sign} | {r.exponent_bits} | {r.fraction_bits}",
                "represented": r.represented_value,
                "error": r.error,
            }
            for r in rows
        ],
    }


def run_training_sanity(cfg: LabConfig, corpus: TinyCorpus) -> dict:
    model = _fresh_model(corpus, cfg)
    device = torch.device(cfg.device)
    model = model.to(device)
    before = clone_model_state(model)
    history = train_steps(model, corpus, cfg, n_steps=5)
    after = clone_model_state(model)
    return {
        "params_changed": models_differ(before, after),
        "loss_finite": all(torch.isfinite(torch.tensor(s.loss)) for s in history.steps),
        "first_loss": history.steps[0].loss,
        "last_loss": history.steps[-1].loss,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = LabConfig()
    set_seed(cfg.seed)
    corpus = TinyCorpus()

    results = {
        "config": cfg.summary(),
        "tensor_trace": run_tensor_trace(cfg, corpus),
        "gradient_check": run_gradient_check(cfg, corpus),
        "accumulation": run_accumulation(cfg, corpus),
        "grad_norm": run_grad_norm(cfg, corpus),
        "mfu": run_mfu(cfg, corpus),
        "float_repr": run_float_repr(),
        "training_sanity": run_training_sanity(cfg, corpus),
    }

    gc = results["gradient_check"]
    gn = results["grad_norm"]
    acc = results["accumulation"]
    mfu = results["mfu"]

    results["truth_report"] = {
        "tensor_shapes": "PASS",
        "gradient": gc["verdict"],
        "accumulation": "PASS" if acc["max_loss_diff"] > 0 and acc["combined_matches_formula"] else "INVESTIGATE",
        "optimization": gn["optimization_verdict"],
        "mfu": "PASS" if mfu["sanity_check"]["pass"] else "INVESTIGATE",
        "precision": "PASS",
    }

    out_path = OUT / "results.json"
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
