#!/usr/bin/env python3
"""Train reconstruction decoder for one method."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))

from kronecker.dynamic import DynamicKronecker
from kronecker.fixed import FixedKronecker
from kronecker.fourier import FourierKronecker
from decoder.byte_decoder import ByteDecoder
from metrics.reconstruction import reconstruction_report
from multilingual_corpus import all_strings, held_out_strings

METHODS = {
    "fixed_kronecker": FixedKronecker,
    "dynamic_kronecker": DynamicKronecker,
    "fourier_kronecker": FourierKronecker,
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--method", choices=METHODS.keys(), default="dynamic_kronecker")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--steps", type=int, default=800)
    p.add_argument("--out", type=Path, default=ROOT / "results" / "reconstruction")
    args = p.parse_args()

    enc = METHODS[args.method]()
    strings = all_strings()
    pairs = [(enc.encode_deterministic(s)[0], s.encode("utf-8")) for s in strings]
    dec = ByteDecoder(latent_dim=enc.latent_dim, seed=args.seed)
    dec.train(pairs, steps=args.steps)

    held = []
    for s in held_out_strings():
        latent, _ = enc.encode_deterministic(s)
        decoded = dec.decode_string(latent, length=len(s.encode("utf-8")))
        held.append({"original": s, **reconstruction_report(s, decoded)})

    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"{args.method}_seed{args.seed}.json"
    out.write_text(json.dumps({"method": args.method, "held_out": held}, indent=2, ensure_ascii=False))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
