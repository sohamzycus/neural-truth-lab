#!/usr/bin/env python3
"""Length-bucket reconstruction generalization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))
sys.path.insert(0, str(ROOT / "experiments"))

from kronecker.dynamic import DynamicKronecker
from kronecker.fixed import FixedKronecker
from common import DEFAULT_SEED, DEFAULT_STEPS, bucket_by_length, eval_strings, make_decoder, train_and_eval
from multilingual_corpus import get_splits


def run(seed: int = DEFAULT_SEED, steps: int = DEFAULT_STEPS) -> dict:
    splits = get_splits(seed)
    test = splits["test"]
    buckets = bucket_by_length(test)
    methods = {
        "fixed_kronecker": FixedKronecker(),
        "dynamic_kronecker": DynamicKronecker(latent_dim=64),
    }
    out: dict = {}
    for name, enc in methods.items():
        trained = train_and_eval(enc, splits["train"], splits["val"], splits["test"], steps=steps, seed=seed)
        bucket_metrics = {}
        pairs = [(enc.encode_deterministic(s)[0], s.encode("utf-8")) for s in splits["train"]]
        dec = make_decoder("position_mlp", len(pairs[0][0]), seed=seed + 1)
        dec.train(pairs, steps=steps)
        for bucket, items in sorted(buckets.items()):
            bucket_metrics[bucket] = eval_strings(enc, dec, items)
        out[name] = {"overall": trained["test_eval"], "by_length_bucket": bucket_metrics}
    return out


def main() -> int:
    out = ROOT / "results" / "length_generalization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"seed": DEFAULT_SEED, "results": run()}
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
