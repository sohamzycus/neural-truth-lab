#!/usr/bin/env python3
"""Scaled collision testing."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))

from kronecker.dynamic import DynamicKronecker
from kronecker.fixed import FixedKronecker
from kronecker.fourier import FourierKronecker
from metrics.reconstruction import find_collisions
from multilingual_corpus import CORPUS, all_strings

SEED = 42
N_RANDOM = 3000


def _generate_collision_strings(seed: int) -> list[str]:
    rng = random.Random(seed)
    strings = list(all_strings())
    for _ in range(N_RANDOM):
        n = rng.randint(1, 80)
        strings.append("".join(chr(rng.randint(32, 126)) for _ in range(n)))
    for lang_items in CORPUS.values():
        strings.extend(lang_items)
    for base in ["ab", "ba", "abc", "acb", "xyz", "zyx"]:
        strings.append(base)
        strings.append(base[::-1])
    for i in range(200):
        s = "a" * rng.randint(33, 120)
        strings.append(s)
        strings.append(s + "b")
    # one-byte mutations
    for s in list(strings)[:200]:
        if not s:
            continue
        b = s.encode("utf-8")
        if b:
            mutated = bytearray(b)
            mutated[0] ^= 1
            strings.append(mutated.decode("utf-8", errors="replace"))
    return list(dict.fromkeys(strings))


def run(seed: int = SEED) -> dict:
    strings = _generate_collision_strings(seed)
    encoders = {
        "fixed_kronecker": FixedKronecker(),
        "dynamic_kronecker": DynamicKronecker(),
        "fourier_magnitude": FourierKronecker(include_phase=False),
        "fourier_phase": FourierKronecker(include_phase=True),
    }
    out = {"strings_tested": len(strings), "seed": seed, "methods": {}}
    for name, enc in encoders.items():
        out["methods"][name] = find_collisions(strings, enc.collision_key)
    dyn = DynamicKronecker(latent_dim=64)
    latent_buckets: dict[str, list[str]] = {}
    for s in strings:
        latent, _ = dyn.encode_deterministic(s)
        k = ",".join(f"{v:.4f}" for v in latent)
        latent_buckets.setdefault(k, []).append(s)
    latent_coll = {k: v for k, v in latent_buckets.items() if len(v) > 1}
    out["methods"]["dynamic_64d_projected_latent"] = {
        "unique_keys": len(latent_buckets),
        "collision_groups": len(latent_coll),
        "collision_rate": round(len(latent_coll) / max(len(strings), 1), 6),
        "examples": list(latent_coll.items())[:5],
    }
    return out


def main() -> int:
    out = ROOT / "results" / "collision_scale.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = run()
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out} ({data['strings_tested']} strings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
