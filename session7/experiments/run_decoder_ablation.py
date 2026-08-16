#!/usr/bin/env python3
"""Decoder architecture ablation at fixed 64-d latent."""

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

DECODERS = ["position_mlp", "sequence", "autoregressive"]


def run(seed: int = DEFAULT_SEED, steps: int = DEFAULT_STEPS) -> dict:
    splits = get_splits(seed)
    enc = DynamicKronecker(latent_dim=64)
    out = {}
    for kind in DECODERS:
        out[kind] = train_and_eval(
            enc, splits["train"], splits["val"], splits["test"],
            decoder_kind=kind, steps=steps, seed=seed,
        )
    return out


def main() -> int:
    out = ROOT / "results" / "decoder_ablation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"latent_dim": 64, "seed": DEFAULT_SEED, "decoders": DECODERS, "results": run()}
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
