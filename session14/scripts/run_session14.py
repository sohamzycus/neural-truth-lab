#!/usr/bin/env python3
"""End-to-end Session 14: dense LM → MoE conversion → continued training."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import torch

from src.config import ExperimentConfig, load_config
from src.data import ROUTER_INIT_NOTE, build_corpus_split, make_eval_batch
from src.model import build_dense_model, count_parameters
from src.moe import MoECausalLM, conversion_fidelity, convert_dense_to_moe
from src.params import parameter_accounting
from src.plots import plot_expert_utilization, plot_loss_curve
from src.routing_report import routing_evolution_table, routing_summary_from_moe_log
from src.seed import set_seed
from src.training import (
    capture_routing_on_batch,
    eval_heldout_loss,
    resolve_device,
    train_phase,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=ROOT / "config/experiment.yaml")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results")
    p.add_argument("--skip-readme", action="store_true")
    args = p.parse_args()

    cfg = load_config(args.config)
    split = build_corpus_split(cfg.seed, train_frac=0.8)
    cfg.model.vocab_size = split.train.vocab_size
    cfg.model.validate()

    results = args.results_dir
    ckpt_dir = results / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    set_seed(cfg.seed)
    device = resolve_device(cfg.runtime.device)
    print(f"seed={cfg.seed} device={device} train={split.train_size} eval={split.eval_size}")

    dense = build_dense_model(cfg.model).to(device)
    dense_initial_eval = eval_heldout_loss(
        dense, split, cfg, device, cfg.training.eval_batch_seed
    )

    dense_log = results / "dense_train.csv"
    dense_stats = train_phase(
        dense,
        cfg,
        split,
        device,
        cfg.training.dense_steps,
        dense_log,
        phase="dense",
    )
    dense_ckpt = ckpt_dir / "dense_final.pt"
    torch.save(
        {"model": dense.state_dict(), "cfg": cfg.to_dict(), "step": cfg.training.dense_steps},
        dense_ckpt,
    )
    dense_final_eval = eval_heldout_loss(
        dense, split, cfg, device, cfg.training.eval_batch_seed
    )

    probe_x, probe_y = make_eval_batch(
        split, cfg.training.batch_size, cfg.model.block_size, cfg.training.eval_batch_seed
    )
    probe_x, probe_y = probe_x.to(device), probe_y.to(device)
    moe = convert_dense_to_moe(dense, cfg.model).to(device)
    fidelity = conversion_fidelity(dense, moe, probe_x, probe_y)
    (results / "conversion_fidelity.json").write_text(json.dumps(fidelity, indent=2))

    moe_ckpt = ckpt_dir / "moe_at_conversion.pt"
    torch.save({"model": moe.state_dict(), "cfg": cfg.to_dict()}, moe_ckpt)

    moe_initial_eval = eval_heldout_loss(
        moe, split, cfg, device, cfg.training.eval_batch_seed
    )
    routing_at_conversion = capture_routing_on_batch(
        moe, split, cfg, device, cfg.training.eval_batch_seed, train=False
    )
    conversion_entropy = float(routing_at_conversion.get("router_entropy", 0.0))

    params = parameter_accounting(dense, moe, cfg.model)
    conversion_report = {
        **params,
        "num_experts": cfg.model.num_experts,
        "top_k": cfg.model.top_k,
        "router_initialization": ROUTER_INIT_NOTE,
        "dense_final_heldout_loss": dense_final_eval,
        "moe_initial_heldout_loss": moe_initial_eval,
        "seed": cfg.seed,
        "dataset": "TinyCorpus (32 sentences, 80/20 split)",
        "dense_training_steps": cfg.training.dense_steps,
        "weights_copied": "embeddings, positional embeddings, attention, layer norms, lm_head",
        "weights_partitioned": "each dense FFN fc1/fc2 along intermediate axis into expert slices",
        "weights_new": "per-layer router linear (zero-init)",
    }
    (results / "conversion_report.json").write_text(
        json.dumps(conversion_report, indent=2)
    )

    moe_log = results / "moe_train.csv"
    train_phase(
        moe,
        cfg,
        split,
        device,
        cfg.training.moe_steps,
        moe_log,
        phase="moe",
        start_step=cfg.training.dense_steps,
        tokens_offset=dense_stats["tokens_seen"],
    )
    moe_final_eval = eval_heldout_loss(
        moe, split, cfg, device, cfg.training.eval_batch_seed
    )
    moe_loss_delta = moe_final_eval - moe_initial_eval

    summary = {
        "dense_checkpoint": str(dense_ckpt.relative_to(ROOT)),
        "conversion_checkpoint": str(moe_ckpt.relative_to(ROOT)),
        "continuation_source": "trained dense checkpoint",
        "optimizer_reset_at_conversion": True,
        "optimizer": "AdamW",
        "learning_rate": cfg.training.learning_rate,
        "seed": cfg.seed,
        "num_experts": cfg.model.num_experts,
        "top_k": cfg.model.top_k,
        "train_split_size": split.train_size,
        "eval_split_size": split.eval_size,
        "dense_initial_heldout_loss": dense_initial_eval,
        "dense_final_heldout_loss": dense_final_eval,
        "moe_training_initial_eval_loss": moe_initial_eval,
        "moe_training_final_eval_loss": moe_final_eval,
        "moe_loss_delta": moe_loss_delta,
        "dense_training_steps": cfg.training.dense_steps,
        "moe_training_steps": cfg.training.moe_steps,
        "conversion_fidelity": fidelity,
        "parameter_accounting": params,
        "router_initialization": ROUTER_INIT_NOTE,
        "model": cfg.model.__dict__,
        "training": cfg.training.__dict__,
    }
    (results / "experiment_summary.json").write_text(json.dumps(summary, indent=2))

    mdf = pd.read_csv(moe_log)
    route_rows = []
    for _, row in mdf.iterrows():
        if not row.get("expert_utilization") or row["expert_utilization"] == "[]":
            continue
        route_rows.append(
            {
                "step": row["step"],
                "top_k": row["top_k"],
                "router_entropy": row["router_entropy"],
                "expert_utilization": row["expert_utilization"],
            }
        )
    route_csv = results / "routing_stats.csv"
    pd.DataFrame(route_rows).to_csv(route_csv, index=False)

    routing_summary = routing_summary_from_moe_log(moe_log, conversion_entropy)
    (results / "routing_summary.json").write_text(json.dumps(routing_summary, indent=2))
    evolution = routing_evolution_table(moe_log, cfg.training.dense_steps)
    (results / "routing_evolution.json").write_text(json.dumps(evolution, indent=2))

    plot_loss_curve(
        dense_log,
        moe_log,
        cfg.training.dense_steps,
        results / "loss_curve.png",
        {
            "dense_initial": dense_initial_eval,
            "dense_final": dense_final_eval,
            "moe_at_conversion": moe_initial_eval,
            "moe_final": moe_final_eval,
        },
    )
    plot_expert_utilization(route_csv, results / "expert_utilization.png")

    if not args.skip_readme:
        subprocess.check_call([sys.executable, str(ROOT / "scripts/generate_readme.py")], cwd=ROOT)

    print("\n=== Session 14 summary (held-out eval) ===")
    print(f"Dense initial:     {dense_initial_eval:.4f}")
    print(f"Dense final:       {dense_final_eval:.4f}")
    print(f"MoE at conversion: {moe_initial_eval:.4f}")
    print(f"MoE final:         {moe_final_eval:.4f}")
    print(f"MoE loss delta:    {moe_loss_delta:.4f}")
    ok = moe_final_eval < moe_initial_eval
    print(f"MoE reduced loss after conversion: {'YES' if ok else 'NO'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
