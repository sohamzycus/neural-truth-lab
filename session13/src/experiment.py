"""CLI experiment runner."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from src.config import load_config, merge_overrides
from src.metrics import merge_results_for_ui
from src.training import train_experiment

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    p = argparse.ArgumentParser(description="ERA V5 Session 13 experiment runner")
    p.add_argument("--config", default=str(ROOT / "config/experiment.yaml"))
    p.add_argument("--mode", choices=["baseline", "euler", "midpoint", "max_batch"], default="baseline")
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--tokens", type=int, default=None)
    p.add_argument("--max-steps", type=int, default=None, help="cap steps for smoke tests")
    p.add_argument("--run-label", default="")
    p.add_argument("--results-dir", default=str(ROOT / "results"))
    args = p.parse_args()
    cfg = load_config(args.config)
    overrides = {}
    if args.batch_size is not None:
        overrides["batch_size"] = args.batch_size
    if args.tokens is not None:
        overrides["tokens"] = args.tokens
    if args.run_label:
        overrides["run_label"] = args.run_label
    if overrides:
        cfg = merge_overrides(cfg, **overrides)
    results = Path(args.results_dir)
    if args.mode == "baseline":
        cfg = merge_overrides(cfg, reversible_method="none", run_label=args.run_label or "baseline")
        m = train_experiment(cfg, max_steps=args.max_steps, results_dir=results)
    elif args.mode in ("euler", "midpoint"):
        cfg = merge_overrides(cfg, reversible_method=args.mode, run_label=args.run_label or args.mode)
        m = train_experiment(cfg, max_steps=args.max_steps, results_dir=results)
    elif args.mode == "max_batch":
        # find largest batch that completes one step
        import torch
        from src.training import resolve_device
        device = resolve_device(cfg.runtime.device)
        best = None
        for bs in [8, 12, 16, 24, 32, 48, 64]:
            try:
                trial = merge_overrides(cfg, batch_size=bs, reversible_method="euler", run_label=f"max_batch_{bs}")
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                tm = train_experiment(trial, max_steps=1, results_dir=None)
                if not tm.oom:
                    best = bs
            except RuntimeError:
                break
        if best is None:
            best = cfg.training.batch_size
        cfg = merge_overrides(cfg, batch_size=best, reversible_method="euler", run_label=f"max_batch_{best}")
        m = train_experiment(cfg, max_steps=args.max_steps, results_dir=results)
    else:
        raise SystemExit("unknown mode")
    merge_results_for_ui(results, ROOT / "web/interactive-lab/public/data/results.json")
    print(json.dumps(m.to_dict(), indent=2))

if __name__ == "__main__":
    main()
