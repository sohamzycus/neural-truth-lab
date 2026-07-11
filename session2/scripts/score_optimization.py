#!/usr/bin/env python3
"""Bounded score optimization: bootstrap sweep, representation, moving-boundary."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.boundary import boundary_analysis, score_target_ladder
from samabpe.bpe import BPETokenizer, PretokenMode
from samabpe.corpus import load_frozen
from samabpe.score_roi import compute_score_roi_candidates
from samabpe.scoring import compute_score
from samabpe.strategies import (
    EN_MAX_FERTILITY,
    LANGS,
    VOCAB_BUDGET,
    train_grapheme_aware,
    train_shared_vanilla,
    train_weighted_shared,
)
from samabpe.verify_core import run_verification, sha256_file, to_baseline_json
from samabpe.word_units import count_word_units, word_units

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "frozen"
PUBLIC = ROOT / "web" / "public" / "data" / "results"
TOK_PATH = RESULTS / "tokenizer.json"
BASELINE_PATH = RESULTS / "pre_optimization_baseline.json"

BOOTSTRAP_GRID = [7500, 7000, 6500, 6000, 5500, 5000]
WEIGHT_GRID = [
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 2.5},
    {"en": 1.0, "hi": 2.5, "te": 3.0, "bn": 4.0},
    {"en": 1.0, "hi": 3.0, "te": 3.5, "bn": 4.5},
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def _result_entry(name: str, res, corpora: dict[str, str], *, extra: dict | None = None) -> dict:
    fert = res.fertilities
    m = res.metrics
    tokens = {lang: res.tokenizer.count_tokens(corpora[lang]) for lang in LANGS}
    row = {
        "name": name,
        "vocabulary_size": res.tokenizer.vocab_size,
        "merge_count": len(res.tokenizer.merges),
        "token_counts": tokens,
        "fertilities": fert,
        "x_min": m["x_min"],
        "x_max": m["x_max"],
        "x_min_language": min(fert, key=fert.get),
        "x_max_language": max(fert, key=fert.get),
        "gap": m["max_min_gap"],
        "score": m["score"],
        "english_pass": fert["en"] <= EN_MAX_FERTILITY,
        "vocab_pass": res.tokenizer.vocab_size <= VOCAB_BUDGET,
    }
    if extra:
        row.update(extra)
    return row


def record_pre_optimization_baseline(result, tok_path: Path) -> dict:
    if BASELINE_PATH.exists():
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline = to_baseline_json(result, tok_path)
    baseline["git_commit_sha"] = _git_sha()
    baseline["label"] = "pre_optimization_baseline"
    baseline["merge_count"] = len(BPETokenizer.load(tok_path).merges)
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"  → pre_optimization_baseline.json (score={baseline['score']:.4f})")
    return baseline


def english_headroom(result) -> dict:
    en = next(l for l in result.languages if l["lang"] == "en")
    wu, tok = en["word_units"], en["tokens"]
    max_tok = int(EN_MAX_FERTILITY * wu)
    return {
        "current_english_x": en["fertility"],
        "allowed_ceiling": EN_MAX_FERTILITY,
        "numeric_headroom": EN_MAX_FERTILITY - en["fertility"],
        "english_word_units": wu,
        "english_token_count": tok,
        "max_tokens_at_ceiling": max_tok,
        "integer_token_headroom": max(0, max_tok - tok),
        "interpretation": "Legitimate reallocation may reduce English bootstrap while staying under 1.2",
    }


def bottleneck_words(tok: BPETokenizer, corpora: dict[str, str], x_max_lang: str) -> dict:
    freq = Counter(word_units(corpora[x_max_lang]))
    rows = []
    for word, count in freq.items():
        toks = tok.encode(word)
        overhead = count * max(0, len(toks) - 1)
        rows.append({
            "word": word,
            "frequency": count,
            "tokenization": toks,
            "tokens_per_occurrence": len(toks),
            "total_contribution": count * len(toks),
            "fragmentation_overhead": overhead,
        })
    rows.sort(key=lambda r: r["fragmentation_overhead"], reverse=True)
    return {"language": x_max_lang, "top_100_overhead": rows[:100], "top_100_contribution": sorted(rows, key=lambda r: r["total_contribution"], reverse=True)[:100]}


def run_bootstrap_sweep(corpora: dict[str, str], baseline_score: float) -> list[dict]:
    out = []
    for boot in BOOTSTRAP_GRID:
        t0 = time.time()
        res = train_weighted_shared(corpora, en_bootstrap=boot)
        entry = _result_entry(f"weighted_shared_bootstrap_{boot}", res, corpora, extra={
            "en_bootstrap": boot,
            "runtime_sec": round(time.time() - t0, 1),
            "status": "MATERIALIZED",
            "accepted": res.metrics["score"] > baseline_score and res.fertilities["en"] <= EN_MAX_FERTILITY,
        })
        out.append(entry)
        print(f"  bootstrap={boot} score={entry['score']:.4f} accepted={entry['accepted']} ({entry['runtime_sec']}s)")
    return out


def run_representation_comparison(corpora: dict[str, str]) -> list[dict]:
    out = []
    configs: list[tuple[str, PretokenMode | None, str]] = [
        ("byte_whitespace_vanilla", None, "shared_vanilla"),
        ("byte_whitespace_weighted", "whitespace", "weighted"),
        ("character_weighted", "character", "weighted"),
        ("grapheme_aware", None, "grapheme"),
    ]
    for name, pretok, kind in configs:
        t0 = time.time()
        if kind == "shared_vanilla":
            res = train_shared_vanilla(corpora)
        elif kind == "grapheme":
            res = train_grapheme_aware(corpora)
        else:
            res = train_weighted_shared(corpora, pretokenization=pretok or "whitespace")
        entry = _result_entry(name, res, corpora, extra={"pretokenization": res.tokenizer.pretokenization, "runtime_sec": round(time.time() - t0, 1)})
        out.append(entry)
        print(f"  {name} score={entry['score']:.4f} ({entry['runtime_sec']}s)")
    return out


def run_local_allocation(corpora: dict[str, str], baseline_score: float, best_boot: int) -> list[dict]:
    out = []
    for i, weights in enumerate(WEIGHT_GRID, 1):
        t0 = time.time()
        res = train_weighted_shared(corpora, weights=weights, en_bootstrap=best_boot)
        entry = _result_entry(f"local_weights_{i}", res, corpora, extra={
            "weights": weights,
            "en_bootstrap": best_boot,
            "runtime_sec": round(time.time() - t0, 1),
            "accepted": res.metrics["score"] > baseline_score and res.fertilities["en"] <= EN_MAX_FERTILITY,
        })
        out.append(entry)
        print(f"  weights={weights} score={entry['score']:.4f}")
    return out


def select_winner(baseline: dict, *candidate_lists: list[dict]) -> tuple[dict | None, list[dict]]:
    best = None
    all_cands: list[dict] = []
    for lst in candidate_lists:
        all_cands.extend(lst)
    for c in all_cands:
        if not c.get("english_pass") or not c.get("vocab_pass"):
            continue
        if c["score"] > baseline["score"]:
            if best is None or c["score"] > best["score"]:
                best = c
    return best, all_cands


def materialize_winner(corpora: dict[str, str], winner_meta: dict) -> BPETokenizer:
    boot = winner_meta.get("en_bootstrap", 7500)
    weights = winner_meta.get("weights")
    pretok = winner_meta.get("pretokenization", "whitespace")
    if winner_meta["name"].startswith("grapheme"):
        return train_grapheme_aware(corpora).tokenizer
    if winner_meta["name"].startswith("byte_whitespace_vanilla"):
        return train_shared_vanilla(corpora).tokenizer
    return train_weighted_shared(corpora, weights=weights, en_bootstrap=boot, pretokenization=pretok).tokenizer


def sync_public(names: list[str]) -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = RESULTS / name
        if src.exists():
            (PUBLIC / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    if not TOK_PATH.exists():
        print("Run scripts/train.py first")
        return 1

    corpora = load_frozen(DATA.parent)
    result = run_verification(TOK_PATH, DATA)
    baseline = record_pre_optimization_baseline(result, TOK_PATH)
    baseline_score = baseline["score"]

    tokens = {lm["lang"]: lm["tokens"] for lm in result.languages}
    wu = {lm["lang"]: lm["word_units"] for lm in result.languages}
    x_max = max(result.fertilities, key=result.fertilities.get)
    tok = BPETokenizer.load(TOK_PATH)

    # Phase 2: score landscape
    landscape = boundary_analysis(tokens, wu)
    ladder = score_target_ladder(tokens, wu)
    (RESULTS / "score_landscape.json").write_text(
        json.dumps({**landscape, "score_targets": ladder}, indent=2), encoding="utf-8"
    )
    (RESULTS / "score_target_ladder.json").write_text(json.dumps(ladder, indent=2), encoding="utf-8")

    # Phase 3: English headroom
    headroom = english_headroom(result)
    (RESULTS / "english_headroom_analysis.json").write_text(json.dumps(headroom, indent=2), encoding="utf-8")

    # Phase 4: bootstrap sweep
    print("\nEnglish bootstrap sweep...")
    bootstrap_results = run_bootstrap_sweep(corpora, baseline_score)
    (RESULTS / "english_bootstrap_sweep.json").write_text(json.dumps(bootstrap_results, indent=2), encoding="utf-8")
    best_boot_entry = max(
        (x for x in bootstrap_results if x.get("english_pass")),
        key=lambda x: x["score"],
        default=max(bootstrap_results, key=lambda x: x["score"]),
    )
    best_boot = best_boot_entry.get("en_bootstrap", 7500)

    # Phase 5: representation
    print("\nRepresentation comparison...")
    repr_results = run_representation_comparison(corpora)
    (RESULTS / "representation_strategy_comparison.json").write_text(json.dumps(repr_results, indent=2), encoding="utf-8")

    # Phase 6: bottleneck words
    bottleneck = bottleneck_words(tok, corpora, x_max)
    (RESULTS / "bottleneck_word_analysis.json").write_text(json.dumps(bottleneck, indent=2, ensure_ascii=False), encoding="utf-8")

    # Phase 7: score ROI
    roi = compute_score_roi_candidates(tok, corpora)
    (RESULTS / "score_roi_candidates.json").write_text(json.dumps(roi, indent=2, ensure_ascii=False), encoding="utf-8")

    # Phase 11: local allocation around best bootstrap
    print(f"\nLocal allocation (bootstrap={best_boot})...")
    local_results = run_local_allocation(corpora, baseline_score, best_boot)
    (RESULTS / "local_allocation_search.json").write_text(json.dumps(local_results, indent=2), encoding="utf-8")

    # Phase 14: select winner
    winner_meta, all_cands = select_winner(baseline, bootstrap_results, repr_results, local_results)
    improved = winner_meta is not None

    trace = [{
        "iteration": 0,
        "status": "VERIFIED",
        "description": "pre_optimization_baseline",
        "score": baseline_score,
        "gap": baseline["max_min_gap"],
        "x_max_language": baseline.get("x_max_language"),
    }]
    if improved and winner_meta:
        print(f"\nIMPROVED: {baseline_score:.4f} → {winner_meta['score']:.4f} ({winner_meta['name']})")
        new_tok = materialize_winner(corpora, winner_meta)
        new_tok.save(TOK_PATH)
        winner_meta["tokenizer_sha256"] = sha256_file(TOK_PATH)
        trace.append({
            "iteration": 1,
            "status": "VERIFIED",
            "accepted": True,
            "description": winner_meta["name"],
            "previous_score": baseline_score,
            "new_score": winner_meta["score"],
            "boundary_transition": winner_meta.get("x_max_language") != baseline.get("x_max_language"),
            **winner_meta,
        })
    else:
        print(f"\nNo improvement over baseline {baseline_score:.4f} — retaining current tokenizer")

    (RESULTS / "moving_boundary_trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
    (RESULTS / "candidate_interaction_search.json").write_text(json.dumps({
        "note": "Individual candidates tested in bootstrap/representation/local sweeps; pair beam not run (bounded budget)",
        "candidates_tested": len(all_cands),
    }, indent=2), encoding="utf-8")

    (RESULTS / "objective_sensitivity.json").write_text(json.dumps({
        "track_a_primary": True,
        "track_b_explored": False,
        "deliberate_degradation_in_final_tokenizer": False,
        "best_track_a_score": winner_meta["score"] if improved else baseline_score,
        "baseline_score": baseline_score,
        "improved": improved,
    }, indent=2), encoding="utf-8")

    # sync key artefacts
    names = [
        "pre_optimization_baseline.json", "score_landscape.json", "english_headroom_analysis.json",
        "english_bootstrap_sweep.json", "representation_strategy_comparison.json",
        "bottleneck_word_analysis.json", "score_roi_candidates.json", "local_allocation_search.json",
        "moving_boundary_trace.json", "objective_sensitivity.json",
    ]
    for n in names:
        p = RESULTS / n
        if p.exists():
            PUBLIC.mkdir(parents=True, exist_ok=True)
            (PUBLIC / n).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

    # Regenerate dependent artefacts (stats, proof, economy audit)
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "verify.py")], cwd=ROOT, check=False)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "final_analysis.py")], cwd=ROOT, check=False)
    sync_public([
        "stats.json", "one_tokenizer_proof.json", "vocabulary_economy_audit.json",
        "score_target_ladder.json", "candidate_interaction_search.json",
    ])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
