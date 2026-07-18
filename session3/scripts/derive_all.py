#!/usr/bin/env python3
"""Regenerate all derived artefacts from quantitative models."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "models"))

from india40b.data_mix import compute_data_mix
from india40b.fertility_model import compute_fertility_projections
from india40b.inference_cost import compute_inference_costs
from india40b.language_weights import compute_mcda_weights
from india40b.scorecards import compute_scorecards
from india40b.training_cost import compute_training_cost
from india40b.vocab_derivation import derive_vocab_allocation


def main() -> None:
    derived = ROOT / "data" / "derived"
    derived.mkdir(parents=True, exist_ok=True)

    outputs = {
        "vocab_allocation.json": derive_vocab_allocation(),
        "language_weights.json": compute_mcda_weights(),
        "fertility_projections.json": compute_fertility_projections(),
        "training_budget.json": compute_training_cost(),
        "inference_costs.json": compute_inference_costs(),
        "data_mix.json": compute_data_mix(),
        "scorecards.json": compute_scorecards(),
    }

    for name, data in outputs.items():
        path = derived / name
        path.write_text(json.dumps(data, indent=2) + "\n")
        print(f"wrote {path.relative_to(ROOT)}")

    # Freeze baseline snapshot
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    baseline = {k: v for k, v in outputs.items()}
    (results / "baseline-derivation-v1.json").write_text(
        json.dumps(baseline, indent=2) + "\n"
    )
    print("wrote results/baseline-derivation-v1.json")


if __name__ == "__main__":
    main()
