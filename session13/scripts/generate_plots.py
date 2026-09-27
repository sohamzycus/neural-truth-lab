#!/usr/bin/env python3
"""Plot loss curves from results/results.json."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "results/results.json").read_text()) if (ROOT / "results/results.json").exists() else []
out = ROOT / "results/plots"
out.mkdir(parents=True, exist_ok=True)
for r in rows:
    hist = r.get("loss_history") or []
    if not hist:
        continue
    plt.figure(figsize=(8, 4))
    plt.plot([p["tokens"] for p in hist], [p["loss"] for p in hist])
    plt.xlabel("tokens"); plt.ylabel("loss"); plt.title(r["run_id"])
    plt.savefig(out / f"loss_{r['run_id']}.png", dpi=120)
    plt.close()
print("plots in", out)
