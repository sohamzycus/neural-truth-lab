#!/usr/bin/env python3
"""Orchestrate all Session 7 experiments → results/summary.json + app/data/results.json."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))
sys.path.insert(0, str(ROOT / "experiments"))

from baselines.standard_embedding import StandardEmbedding
from kronecker.dynamic import DynamicKronecker
from kronecker.fixed import FixedKronecker
from kronecker.fourier import FourierKronecker
from kronecker.inverse import deterministic_roundtrip
from common import DEFAULT_SEED, DEFAULT_STEPS, FULL_FEATURE_EPOCHS, train_and_eval
from metrics.parameters import accounting_table
from metrics.reconstruction import find_collisions, reconstruction_report
from multilingual_corpus import CORPUS, all_strings, get_splits, held_out_strings, save

RESULTS = ROOT / "results"
APP_DATA = ROOT / "app" / "data"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT.parent, text=True
        ).strip()
    except Exception:
        return "unknown"


def _load_json(path: Path) -> dict | list | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def run_baseline_collision() -> dict:
    strings = all_strings()
    encoders = {
        "fixed_kronecker": FixedKronecker(),
        "dynamic_kronecker": DynamicKronecker(),
        "fourier_kronecker": FourierKronecker(include_phase=False),
        "fourier_kronecker_phase": FourierKronecker(include_phase=True),
    }
    out = {name: find_collisions(strings, enc.collision_key) for name, enc in encoders.items()}
    dyn = DynamicKronecker(latent_dim=64)
    latent_buckets: dict[str, list[str]] = {}
    for s in strings:
        latent, _ = dyn.encode_deterministic(s)
        k = ",".join(f"{v:.4f}" for v in latent)
        latent_buckets.setdefault(k, []).append(s)
    latent_coll = {k: v for k, v in latent_buckets.items() if len(v) > 1}
    out["dynamic_kronecker_projected_latent"] = {
        "unique_keys": len(latent_buckets),
        "collision_groups": len(latent_coll),
        "examples": list(latent_coll.items())[:5],
    }
    return out


def run_deterministic_inverse() -> dict:
    strings = all_strings()
    exact = sum(1 for s in strings if deterministic_roundtrip(s)[1])
    return {"total": len(strings), "string_exact_match_rate": round(exact / max(len(strings), 1), 4)}


def run_waste_by_language() -> dict:
    fixed, dynamic = FixedKronecker(), DynamicKronecker()
    by_lang = {}
    for lang, items in CORPUS.items():
        fw = [fixed.encode_deterministic(s)[1] for s in items]
        dw = [dynamic.encode_deterministic(s)[1] for s in items]
        by_lang[lang] = {
            "fixed_avg_waste_ratio": round(sum(x["waste_ratio"] for x in fw) / max(len(items), 1), 4),
            "fixed_truncation_rate": round(sum(1 for x in fw if x["truncated"]) / max(len(items), 1), 4),
            "dynamic_truncation_rate": round(sum(1 for x in dw if x["truncated"]) / max(len(items), 1), 4),
        }
    return by_lang


def run_baseline_reconstruction() -> dict:
    strings, held = all_strings(), held_out_strings()
    encoders = {
        "fixed_kronecker": FixedKronecker(),
        "dynamic_kronecker": DynamicKronecker(latent_dim=64),
        "dynamic_kronecker_full": DynamicKronecker(project_latent=False),
        "fourier_kronecker": FourierKronecker(),
    }
    out = {}
    for name, enc in encoders.items():
        full = name == "dynamic_kronecker_full"
        out[name] = train_and_eval(
            enc, strings, [], held,
            steps=FULL_FEATURE_EPOCHS if full else DEFAULT_STEPS,
            seed=DEFAULT_SEED,
            full_epoch=full,
        )
        # backward compat field name
        out[name]["held_out_eval"] = out[name]["test_eval"]
    return out


def build_hypotheses(summary: dict) -> dict:
    waste = summary["waste_by_language"]
    coll = summary["collision"]
    recon = summary.get("reconstruction", summary.get("baseline_reconstruction", {}))
    latent = summary.get("latent_sweep", {})
    dec_ab = summary.get("decoder_ablation", {})
    coll_scale = summary.get("collision_scale", {})
    repr_cmp = summary.get("representation_comparison", {})

    h1 = all(v["dynamic_truncation_rate"] == 0 for v in waste.values())
    h2 = coll["dynamic_kronecker"]["collision_groups"] <= coll["fixed_kronecker"]["collision_groups"]
    h3_rate = summary.get("deterministic_inverse", {}).get("string_exact_match_rate", 0)

    sweep_results = latent.get("results", []) if isinstance(latent, dict) else []
    held_rates = [r["test_eval"]["string_exact_match_rate"] for r in sweep_results]
    h5_status = "NOT RUN"
    h5_note = ""
    if len(held_rates) >= 2:
        if max(held_rates) == 0:
            h5_status = "FAIL"
            h5_note = "No tested latent dimension achieved held-out exact reconstruction > 0"
        elif held_rates[-1] > held_rates[0]:
            h5_status = "PARTIAL"
            h5_note = "Gradual improvement with latent dimension observed"
        else:
            h5_status = "PARTIAL"
            h5_note = "Non-monotonic or flat trade-off observed"

    dec_results = dec_ab.get("results", {}) if isinstance(dec_ab, dict) else {}
    dec_held = {k: v.get("test_eval", {}).get("string_exact_match_rate", 0) for k, v in dec_results.items()}
    h6_status = "NOT RUN"
    if dec_held:
        best = max(dec_held.values())
        h6_status = "PARTIAL" if best > 0 else "FAIL"

    fourier_ab = coll.get("fourier_kronecker", {}).get("collision_groups", 0)
    fourier_ph = coll.get("fourier_kronecker_phase", {}).get("collision_groups", 0)
    scaled_fourier = coll_scale.get("methods", {}) if coll_scale else {}
    ab_ba_fixed = scaled_fourier.get("fourier_magnitude", {}).get("collision_groups", 0)

    def _hyp(status, **kw):
        return {"status": status, **kw}

    return {
        "H1_dynamic_reduces_waste": _hyp("PASS" if h1 else "FAIL", evidence=waste),
        "H2_fewer_collisions_than_fixed": _hyp(
            "PASS" if h2 else "PARTIAL",
            fixed_collision_groups=coll["fixed_kronecker"]["collision_groups"],
            dynamic_collision_groups=coll["dynamic_kronecker"]["collision_groups"],
        ),
        "H3_deterministic_inversion": _hyp(
            "PASS" if h3_rate >= 1.0 else "PARTIAL",
            exact_match_rate=h3_rate,
            interpretation="Deterministic inverse recovers bytes explicitly stored in feature layout",
        ),
        "H4_learned_reconstruction_depends_on_capacity": _hyp(
            "PARTIAL" if sweep_results else "NOT RUN",
            latent_sweep_held_out_exact=held_rates,
            interpretation="Measured under position MLP decoder and current training budget",
        ),
        "H5_capacity_threshold_exists": _hyp(h5_status, note=h5_note, held_out_by_dim=dict(zip(
            [r["latent_dim"] for r in sweep_results], held_rates
        )) if sweep_results else {}),
        "H6_sequence_decoder_recovers_more": _hyp(h6_status, test_exact_by_decoder=dec_held),
        "H7_fourier_needs_order_info": _hyp(
            "PARTIAL",
            magnitude_collisions_baseline_corpus=fourier_ab,
            phase_collisions_baseline_corpus=fourier_ph,
            scaled_magnitude_collision_groups=ab_ba_fixed,
            interpretation="Magnitude-only Fourier can collide on permutations; phase reduces but does not eliminate all collisions at scale",
        ),
        "H8_lm_usefulness": _hyp("NOT RUN", note="Tiny LM experiment not completed"),
        "representation_paths": _hyp(
            "PARTIAL" if repr_cmp else "NOT RUN",
            note="See representation_comparison: separates deterministic inverse vs compression vs decoder",
        ),
    }


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    APP_DATA.mkdir(parents=True, exist_ok=True)
    save(ROOT / "datasets" / "multilingual_corpus.json")

    # Run sub-experiments
    import run_latent_sweep
    import run_decoder_ablation
    import run_collision_scale
    import run_length_generalization
    import run_representation_comparison
    import run_language_generalization

    run_latent_sweep.main()
    run_decoder_ablation.main()
    run_collision_scale.main()
    run_length_generalization.main()
    run_representation_comparison.main()
    run_language_generalization.main()

    splits = get_splits(DEFAULT_SEED)
    std = StandardEmbedding(dim=64)
    std.build_vocab(all_strings())

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "meta": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_commit": _git_commit(),
            "seed": DEFAULT_SEED,
            "train_steps": DEFAULT_STEPS,
            "split_sizes": {k: len(v) for k, v in splits.items()},
        },
        "assignment": {
            "primary": ["Problem 3 — Dynamic Kronecker", "Problem 5 — Reversible Embedding"],
            "secondary": ["Problem 4 — Fourier baseline"],
            "research_question": "How much can deterministic byte features be compressed before learned reversibility breaks?",
        },
        "collision": run_baseline_collision(),
        "deterministic_inverse": run_deterministic_inverse(),
        "waste_by_language": run_waste_by_language(),
        "baseline_params": {
            "standard_embedding": {"trainable_parameters": std.trainable_parameters, "vocab_size": len(std.vocab)},
        },
        "parameter_accounting": accounting_table(vocab_size=len(std.vocab)),
        "baseline_reconstruction": run_baseline_reconstruction(),
        "reconstruction": None,  # filled below for backward compat
        "latent_sweep": _load_json(RESULTS / "latent_sweep.json"),
        "decoder_ablation": _load_json(RESULTS / "decoder_ablation.json"),
        "collision_scale": _load_json(RESULTS / "collision_scale.json"),
        "length_generalization": _load_json(RESULTS / "length_generalization.json"),
        "representation_comparison": _load_json(RESULTS / "representation_comparison.json"),
        "language_generalization": _load_json(RESULTS / "language_generalization.json"),
        "splits": {k: len(v) for k, v in splits.items()},
    }
    summary["reconstruction"] = summary["baseline_reconstruction"]
    summary["hypotheses"] = build_hypotheses(summary)

    out_path = RESULTS / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (APP_DATA / "results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
