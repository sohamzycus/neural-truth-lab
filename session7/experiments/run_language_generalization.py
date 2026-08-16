#!/usr/bin/env python3
"""Per-language evaluation EN/HI/TE/BN."""

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
from common import DEFAULT_SEED, DEFAULT_STEPS, eval_strings, make_decoder
from metrics.reconstruction import find_collisions
from multilingual_corpus import CORPUS, get_splits, language_of

LANGS = ["english", "hindi", "telugu", "bengali"]


def run(seed: int = DEFAULT_SEED, steps: int = DEFAULT_STEPS) -> dict:
    splits = get_splits(seed)
    fixed = FixedKronecker()
    dynamic = DynamicKronecker(latent_dim=64)
    pairs = [(dynamic.encode_deterministic(s)[0], s.encode("utf-8")) for s in splits["train"]]
    dec = make_decoder("position_mlp", 64, seed=seed + 1)
    dec.train(pairs, steps=steps)

    by_lang: dict = {}
    for lang in LANGS:
        items = CORPUS.get(lang, [])
        if not items:
            continue
        avg_bytes = sum(len(s.encode("utf-8")) for s in items) / len(items)
        fw = [fixed.encode_deterministic(s)[1] for s in items]
        dw = [dynamic.encode_deterministic(s)[1] for s in items]
        by_lang[lang] = {
            "count": len(items),
            "avg_utf8_bytes": round(avg_bytes, 2),
            "fixed_avg_waste_ratio": round(sum(x["waste_ratio"] for x in fw) / len(items), 4),
            "fixed_truncation_rate": round(sum(1 for x in fw if x["truncated"]) / len(items), 4),
            "dynamic_truncation_rate": round(sum(1 for x in dw if x["truncated"]) / len(items), 4),
            "dynamic_collision_groups": find_collisions(items, dynamic.collision_key)["collision_groups"],
            "fixed_collision_groups": find_collisions(items, fixed.collision_key)["collision_groups"],
            "reconstruction_test": eval_strings(dynamic, dec, [s for s in splits["test"] if language_of(s) == lang or lang == "english" and language_of(s) == "english"]),
        }
    return by_lang


def main() -> int:
    out = ROOT / "results" / "language_generalization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"seed": DEFAULT_SEED, "languages": run()}
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
