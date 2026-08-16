#!/usr/bin/env python3
"""Latent dimension sweep — reversibility frontier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))
sys.path.insert(0, str(ROOT / "experiments"))

from kronecker.dynamic import DynamicKronecker
from common import DEFAULT_SEED, DEFAULT_STEPS, train_and_eval
from multilingual_corpus import get_splits

LATENT_DIMS = [16, 32, 64, 128, 256, 512, 1024]


def run(seed: int = DEFAULT_SEED, steps: int = DEFAULT_STEPS) -> list[dict]:
    splits = get_splits(seed)
    results = []
    for dim in LATENT_DIMS:
        enc = DynamicKronecker(latent_dim=dim, project_latent=True)
        r = train_and_eval(
            enc, splits["train"], splits["val"], splits["test"],
            decoder_kind="position_mlp", steps=steps, seed=seed,
        )
        r["latent_dim"] = dim
        results.append(r)
    return results


def main() -> int:
    out = ROOT / "results" / "latent_sweep.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"latent_dims": LATENT_DIMS, "seed": DEFAULT_SEED, "results": run()}
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
