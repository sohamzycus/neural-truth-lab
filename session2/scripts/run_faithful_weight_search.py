#!/usr/bin/env python3
"""Faithful HF BPE weight search with round-trip gate and threshold requirements."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.evaluator_contract import LANGS, threshold_status
from samabpe.hf_bpe_trainer import (
    evaluate_tokenizer,
    load_faithful_corpora,
    sha256_file,
    train_hf_bpe,
    verify_tokenizer_roundtrip,
)
from samabpe.weight_optimizer import WeightConfig, threshold_grid, threshold_neighbor_configs

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "faithful"
CAND = ROOT / "results" / "resubmission" / "candidates_faithful"
REGISTRY = ROOT / "results" / "resubmission" / "experiments.json"
COMPARISON = ROOT / "results" / "resubmission" / "comparison.json"
FINAL = ROOT / "results" / "resubmission" / "final"
BASELINE_W = WeightConfig(3, 4, 4, 2)


def _record(tok_path: Path, weights: WeightConfig, experiment_id: str, meta: dict, ev: dict | None) -> dict:
    rt = meta.get("roundtrip", {})
    thresholds = ev.get("thresholds", {}) if ev else {}
    both = thresholds.get("en_under_1_2") and thresholds.get("hi_under_1_2")
    status = "VALID_MEASURED" if rt.get("valid") and ev else "INVALID_ROUNDTRIP"
    if status == "VALID_MEASURED" and not both:
        status = "VALID_MEASURED_BELOW_THRESHOLD"
    rec = {
        "experiment_id": experiment_id,
        "languages": list(LANGS),
        "tokenizer_engine": "huggingface-bpe",
        "normalizer": "NFKC",
        "pretokenizer": meta.get("pretokenizer"),
        "decoder": meta.get("decoder"),
        "weights": weights.as_dict(),
        "vocab_size": meta.get("vocab_size"),
        "roundtrip": {
            "reviewer_sample": rt.get("reviewer_sample"),
            "full_corpus_en": rt.get("full_corpus", {}).get("en"),
            "full_corpus_hi": rt.get("full_corpus", {}).get("hi"),
            "full_corpus_te": rt.get("full_corpus", {}).get("te"),
            "full_corpus_bn": rt.get("full_corpus", {}).get("bn"),
        },
        "tokenizer_path": str(tok_path.relative_to(ROOT)),
        "tokenizer_sha256": sha256_file(tok_path),
        "status": status,
    }
    if ev:
        rec.update(
            {
                "fertilities": ev["fertilities"],
                "faithful_unit_counts": ev.get("faithful_unit_counts", ev.get("wordish_counts")),
                "token_counts": ev["token_counts"],
                "thresholds": thresholds,
                "spread": ev["spread"],
                "raw_score": ev["raw_score"],
                "hindi_penalty": ev["hindi_penalty"],
                "adjusted_score": ev["adjusted_score"],
                "final_grade": ev["final_grade"],
            }
        )
    return rec


def _train(corpora: dict[str, str], w: WeightConfig, eid: str) -> dict:
    path = CAND / f"weights_{w.key()}.json"
    if path.exists():
        from tokenizers import Tokenizer

        tok = Tokenizer.from_file(str(path))
        rt = verify_tokenizer_roundtrip(tok, corpora)
        meta = {"vocab_size": tok.get_vocab_size(with_added_tokens=True), "roundtrip": rt}
    else:
        tok, meta = train_hf_bpe(corpora, weights=w.as_dict(), output_path=path)
    ev = None
    if meta.get("roundtrip", {}).get("valid"):
        try:
            ev = evaluate_tokenizer(tok, corpora)
        except ValueError:
            pass
    return _record(path, w, eid, meta, ev)


def _pick_winner(records: list[dict]) -> dict | None:
    valid = [
        r
        for r in records
        if r.get("roundtrip", {}).get("reviewer_sample")
        and r.get("thresholds", {}).get("en_under_1_2")
        and r.get("thresholds", {}).get("hi_under_1_2")
        and r.get("adjusted_score") is not None
    ]
    if not valid:
        # best faithful roundtrip with highest adjusted score
        valid = [
            r
            for r in records
            if r.get("roundtrip", {}).get("reviewer_sample") and r.get("adjusted_score") is not None
        ]
    if not valid:
        return None
    return max(valid, key=lambda r: r["adjusted_score"])


def main() -> int:
    corpora = load_faithful_corpora(CORPUS)
    CAND.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    n = 1

    print("Baseline EN 3 · HI 4 · TE 4 · BN 2 …")
    records.append(_train(corpora, BASELINE_W, f"faithful-hf-{n:04d}"))
    n += 1
    bl = records[-1]
    print(f"  roundtrip={bl['roundtrip']['reviewer_sample']} adjusted={bl.get('adjusted_score')}")

    seen = {BASELINE_W.key()}
    grid = [w for w in threshold_grid() if w.key() not in seen]
    print(f"Coarse search: {len(grid)} configs …")
    for i, w in enumerate(grid, start=1):
        seen.add(w.key())
        records.append(_train(corpora, w, f"faithful-hf-{n:04d}"))
        n += 1
        if i % 100 == 0:
            wn = _pick_winner(records)
            print(f"  {i}… best adjusted={wn['adjusted_score'] if wn else 'none'}")

    ranked = sorted(
        [r for r in records if r.get("adjusted_score")],
        key=lambda r: r["adjusted_score"],
        reverse=True,
    )[:8]
    for base in ranked[:5]:
        w = WeightConfig(**base["weights"])
        for nb in threshold_neighbor_configs(w):
            if nb.key() in seen:
                continue
            seen.add(nb.key())
            records.append(_train(corpora, nb, f"faithful-hf-{n:04d}"))
            n += 1

    winner = _pick_winner(records)
    if not winner:
        print("ERROR: no valid faithful candidate")
        return 1

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "objective": "faithful_adjusted_score",
                "architecture": "NFKC+Metaspace",
                "total_measured": len(records),
                "valid_roundtrip": sum(1 for r in records if r["roundtrip"]["reviewer_sample"]),
                "both_thresholds": sum(
                    1
                    for r in records
                    if r.get("thresholds", {}).get("en_under_1_2")
                    and r.get("thresholds", {}).get("hi_under_1_2")
                ),
                "experiments": sorted(records, key=lambda r: r.get("adjusted_score") or 0, reverse=True),
                "winner_experiment_id": winner["experiment_id"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    src = ROOT / winner["tokenizer_path"]
    FINAL.mkdir(parents=True, exist_ok=True)
    dst = FINAL / "tokenizer.json"
    dst.write_bytes(src.read_bytes())
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "evaluate_hf_tokenizer.py"),
            "--tokenizer",
            str(dst),
            "--corpus-dir",
            str(CORPUS),
            "--output",
            str(FINAL / "metrics.json"),
        ]
    )
    provenance = {
        "strategy": "faithful-adaptive-weight-search",
        "languages": list(LANGS),
        "weights": winner["weights"],
        "architecture": {"normalizer": "NFKC", "pretokenizer": "Metaspace", "decoder": "Metaspace"},
        "thresholds": winner.get("thresholds"),
        "tokenizer_sha256": sha256_file(dst),
        "experiment_id": winner["experiment_id"],
        "training_command": "python scripts/run_faithful_weight_search.py",
    }
    (FINAL / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    print(f"\nWinner {winner['experiment_id']} weights={winner['weights']}")
    print(f"  thresholds={winner.get('thresholds')} adjusted={winner.get('adjusted_score')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
