#!/usr/bin/env python3
"""Representation path comparison: inverse vs full vs projected latents."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))
sys.path.insert(0, str(ROOT / "experiments"))

from kronecker.dynamic import DynamicKronecker
from kronecker.inverse import deterministic_roundtrip
from common import DEFAULT_SEED, DEFAULT_STEPS, FULL_FEATURE_EPOCHS, aggregate_reports, train_and_eval
from metrics.reconstruction import reconstruction_report
from multilingual_corpus import get_splits

PROJECTION_DIMS = [None, 64, 128, 256, 512]  # None = full features


def run(seed: int = DEFAULT_SEED, steps: int = DEFAULT_STEPS) -> dict:
    splits = get_splits(seed)
    out: dict = {}

    # A — deterministic inverse
    reports = []
    for s in splits["test"]:
        recovered, ok = deterministic_roundtrip(s)
        reports.append(reconstruction_report(s, recovered if ok else recovered))
    out["A_deterministic_inverse"] = {
        "description": "dynamic features → deterministic inverse (no learned decoder)",
        "test_eval": aggregate_reports(reports),
    }

    for dim in PROJECTION_DIMS:
        if dim is None:
            label = "B_full_features_learned_decoder"
            enc = DynamicKronecker(project_latent=False)
            full_epoch = True
            train_steps = FULL_FEATURE_EPOCHS
        else:
            label = f"C_projected_{dim}d_learned_decoder"
            enc = DynamicKronecker(latent_dim=dim, project_latent=True)
            full_epoch = False
            train_steps = steps
        out[label] = {
            "description": f"dynamic features → {'full' if dim is None else str(dim)+'d'} → position MLP",
            "projection_dim": dim,
            **train_and_eval(
                enc, splits["train"], splits["val"], splits["test"],
                steps=train_steps, seed=seed, full_epoch=full_epoch,
            ),
        }
    return out


def main() -> int:
    out = ROOT / "results" / "representation_comparison.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"seed": DEFAULT_SEED, "results": run()}
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
