"""Deep semantic verification of experiment registry."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from samabpe.evaluator_contract import LANGS

REGISTRY = Path(__file__).resolve().parents[2] / "results" / "resubmission" / "experiments.json"


def run_deep_check(registry_path: Path | None = None) -> dict[str, Any]:
    reg_path = registry_path or REGISTRY
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    exps = reg.get("experiments", [])
    issues: list[str] = []

    ids = [e.get("experiment_id") for e in exps]
    if len(ids) != len(set(ids)):
        issues.append("duplicate experiment_id")

    weight_keys = [f"{e['weights']['en']}-{e['weights']['hi']}-{e['weights']['te']}-{e['weights']['bn']}" for e in exps]
    if len(weight_keys) != len(set(weight_keys)):
        issues.append("duplicate weight configuration")

    fert_sigs = set()
    spread_values: list[float] = []
    rt_pass = 0
    en_pass = 0
    hi_pass = 0
    both_pass = 0
    hf_bpe = 0
    arch_ok = 0
    loadable = 0
    status_counts: Counter[str] = Counter()
    winner_metrics_reused = 0
    winner_id = reg.get("winner_experiment_id")
    winner = next((e for e in exps if e.get("experiment_id") == winner_id), None)
    winner_fert = tuple(round(winner["fertilities"][l], 8) for l in LANGS) if winner else None

    per_exp: list[dict[str, Any]] = []
    for e in exps:
        status_counts[e.get("status", "?")] += 1
        if e.get("tokenizer_engine") == "huggingface-bpe":
            hf_bpe += 1
        pre, dec = e.get("pretokenizer") or {}, e.get("decoder") or {}
        if e.get("normalizer") == "NFKC" and pre.get("type") == "Metaspace" and dec.get("type") == "Metaspace":
            arch_ok += 1
        if e.get("tokenizer_path") and e.get("tokenizer_sha256"):
            loadable += 1
        rt = e.get("roundtrip", {})
        rt_ok = rt.get("reviewer_sample") and all(rt.get(f"full_corpus_{l}") for l in LANGS)
        if rt_ok:
            rt_pass += 1
        th = e.get("thresholds", {})
        f = e.get("fertilities", {})
        if f:
            sig = tuple(round(f[l], 8) for l in LANGS)
            fert_sigs.add(sig)
            if winner_fert and sig == winner_fert and e.get("experiment_id") != winner_id:
                winner_metrics_reused += 1
            # per-candidate threshold recompute
            en_ok = f.get("en", 99) < 1.2
            hi_ok = f.get("hi", 99) < 1.2
            if th.get("en_under_1_2") != en_ok:
                issues.append(f"{e['experiment_id']}: en threshold flag mismatch")
            if th.get("hi_under_1_2") != hi_ok:
                issues.append(f"{e['experiment_id']}: hi threshold flag mismatch")
            if en_ok:
                en_pass += 1
            if hi_ok:
                hi_pass += 1
            if en_ok and hi_ok:
                both_pass += 1
        if "spread" in e:
            spread_values.append(e["spread"])
        per_exp.append(
            {
                "experiment_id": e.get("experiment_id"),
                "weights": e.get("weights"),
                "status": e.get("status"),
                "roundtrip_pass": rt_ok,
                "en_under_1_2": th.get("en_under_1_2"),
                "hi_under_1_2": th.get("hi_under_1_2"),
                "spread": e.get("spread"),
            }
        )

    verified_2570 = (
        len(exps) == 2570
        and hf_bpe == 2570
        and arch_ok == 2570
        and len(set(weight_keys)) == 2570
        and len(fert_sigs) == 2570
        and not issues
        and reg.get("architecture") == "NFKC+Metaspace"
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_path": str(reg_path),
        "total_records": len(exps),
        "unique_experiment_ids": len(set(ids)),
        "unique_weight_configurations": len(set(weight_keys)),
        "unique_fertility_signatures": len(fert_sigs),
        "huggingface_bpe_runs": hf_bpe,
        "nfkc_metaspace_architecture": arch_ok,
        "loadable_tokenizer_records": loadable,
        "passed_roundtrip": rt_pass,
        "passed_en_under_1_2": en_pass,
        "passed_hi_under_1_2": hi_pass,
        "passed_both_thresholds": both_pass,
        "spread_min": min(spread_values) if spread_values else None,
        "spread_max": max(spread_values) if spread_values else None,
        "winner_experiment_id": winner_id,
        "non_winner_records_sharing_winner_fertilities": winner_metrics_reused,
        "status_breakdown": dict(status_counts),
        "semantic_issues": issues,
        "verified_2570_claim": verified_2570,
        "ui_headline": (
            "2,570 real Hugging Face BPE candidates trained and measured"
            if verified_2570
            else f"{len(exps)} recorded experiments in registry"
        ),
        "per_experiment_sample": per_exp[:5],
        "note": "Registry metrics are per-candidate measurements from search time; final submission tokenizer may be hardened retrain at winner weights.",
    }
