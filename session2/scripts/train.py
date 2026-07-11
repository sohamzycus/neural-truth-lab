#!/usr/bin/env python3
"""Train all strategies, optimize allocation, emit artefacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.bpe import BPETokenizer
from samabpe.corpus import load_frozen, sha256_text
from samabpe.scoring import LanguageMetrics, compute_score
from samabpe.strategies import (
    EN_MAX_FERTILITY,
    LANGS,
    STRATEGIES,
    VOCAB_BUDGET,
    train_allocated_monolingual,
    train_score_directed_adaptive,
)
from samabpe.sweeps import run_sweeps
from samabpe.unicode_utils import grapheme_integrity_score
from samabpe.word_units import count_word_units

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
PUBLIC = ROOT / "web" / "public" / "data"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def optimize_allocation(corpora: dict[str, str]) -> dict[str, int]:
    """Coarse grid + local refinement for monolingual allocation."""
    best_score = -1.0
    best_alloc = {"en": 2500, "hi": 2500, "te": 2500, "bn": 2498}

    for en_a in range(2000, 3001, 500):
        rem = VOCAB_BUDGET - en_a - 2
        hi_a = rem // 3
        te_a = rem // 3
        bn_a = rem - hi_a - te_a
        alloc = {"en": en_a, "hi": hi_a, "te": te_a, "bn": bn_a}
        res = train_allocated_monolingual(corpora, allocation=alloc)
        if res.fertilities["en"] > EN_MAX_FERTILITY:
            continue
        if res.metrics["score"] > best_score:
            best_score = res.metrics["score"]
            best_alloc = alloc

    return best_alloc


def build_stats(winner_name: str, tok: BPETokenizer, corpora: dict[str, str], extra: dict) -> dict:
    langs_metrics = []
    fertilities = {}
    for lang in LANGS:
        text = corpora[lang]
        wu = count_word_units(text)
        tokens = tok.count_tokens(text)
        fert = tokens / wu if wu else 0
        fertilities[lang] = fert
        langs_metrics.append({
            "lang": lang,
            "label": {"en": "English", "hi": "हिन्दी", "te": "తెలుగు", "bn": "বাংলা"}[lang],
            "characters": len(text),
            "word_units": wu,
            "tokens": tokens,
            "fertility": fert,
        })

    score_data = compute_score(fertilities)
    for lm in langs_metrics:
        lm["rank"] = score_data["ranks"][lm["lang"]]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "winning_strategy": winner_name,
        "vocabulary_size": tok.vocab_size,
        "vocab_budget": VOCAB_BUDGET,
        "languages": langs_metrics,
        "fertilities": fertilities,
        "sorted_x": score_data["sorted_x"],
        "x_min": score_data["x_min"],
        "x_max": score_data["x_max"],
        "max_min_gap": score_data["max_min_gap"],
        "score": score_data["score"],
        "english_constraint": {
            "max_allowed": EN_MAX_FERTILITY,
            "actual": fertilities["en"],
            "pass": fertilities["en"] <= EN_MAX_FERTILITY,
        },
        **extra,
    }


def main() -> None:
    import sys

    print("SamaBPE training pipeline", flush=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)

    corpora = load_frozen(DATA)
    if not corpora.get("en"):
        raise SystemExit("Run scripts/fetch_corpora.py first")

    # Benchmark all strategies
    comparison = []
    best_name = ""
    best_score = -1.0
    winner_tok: BPETokenizer | None = None
    winner_alloc: dict = {}
    opt_trace: list = []
    rejected: list = []

    for name, fn in STRATEGIES.items():
        print(f"Training {name}...")
        if name == "allocated_monolingual":
            alloc = optimize_allocation(corpora)
            res = fn(corpora, allocation=alloc)
            winner_alloc = {"shared": 2, **alloc}
        else:
            res = fn(corpora)
        entry = {
            "strategy": name,
            "vocabulary_size": res.tokenizer.vocab_size,
            "en_fertility": res.fertilities["en"],
            "hi_fertility": res.fertilities["hi"],
            "te_fertility": res.fertilities["te"],
            "bn_fertility": res.fertilities["bn"],
            "max_min_gap": res.metrics["max_min_gap"],
            "score": res.metrics["score"],
            "english_pass": res.fertilities["en"] <= EN_MAX_FERTILITY,
        }
        comparison.append(entry)
        if res.fertilities["en"] <= EN_MAX_FERTILITY and res.metrics["score"] > best_score:
            best_score = res.metrics["score"]
            best_name = name
            winner_tok = res.tokenizer
            winner_alloc = res.vocab_allocation

    print("Training score_directed_adaptive...")
    sda_res, opt_trace, rejected = train_score_directed_adaptive(corpora, vocab_size=VOCAB_BUDGET)
    sda_entry = {
        "strategy": "score_directed_adaptive",
        "vocabulary_size": sda_res.tokenizer.vocab_size,
        "en_fertility": sda_res.fertilities["en"],
        "hi_fertility": sda_res.fertilities["hi"],
        "te_fertility": sda_res.fertilities["te"],
        "bn_fertility": sda_res.fertilities["bn"],
        "max_min_gap": sda_res.metrics["max_min_gap"],
        "score": sda_res.metrics["score"],
        "english_pass": sda_res.fertilities["en"] <= EN_MAX_FERTILITY,
    }
    comparison.append(sda_entry)
    if sda_res.fertilities["en"] <= EN_MAX_FERTILITY and sda_res.metrics["score"] > best_score:
        best_score = sda_res.metrics["score"]
        best_name = "score_directed_adaptive"
        winner_tok = sda_res.tokenizer
        winner_alloc = sda_res.vocab_allocation

    if winner_tok is None:
        # ponytail: fallback to English-seeded weighted shared if no strategy passed
        print("No EN-passing winner; using English-seeded weighted_shared fallback", flush=True)
        from samabpe.strategies import train_weighted_shared
        fb = train_weighted_shared(corpora)
        best_name = "weighted_shared"
        best_score = fb.metrics["score"]
        winner_tok = fb.tokenizer
        winner_alloc = fb.vocab_allocation

    assert winner_tok is not None
    print(f"Winner: {best_name} (score={best_score:.2f})")

    # Export tokenizer artefacts
    tok_path = RESULTS / "tokenizer.json"
    winner_tok.save(tok_path)
    winner_tok.export_vocab_json(RESULTS / "vocab.json")
    winner_tok.export_vocab_txt(RESULTS / "vocab.txt")
    winner_tok.export_merges_txt(RESULTS / "merges.txt")

    # Sweeps
    sweep_path = RESULTS / "vocab_sweep_curves.json"
    run_sweeps(DATA, out_path=sweep_path)

    # Grapheme stats
    gstats = {lang: grapheme_integrity_score(corpora[lang]) for lang in LANGS}
    (RESULTS / "grapheme_stats.json").write_text(json.dumps(gstats, indent=2), encoding="utf-8")

    stats = build_stats(
        best_name,
        winner_tok,
        corpora,
        {
            "vocab_allocation": winner_alloc,
            "tokenizer_sha256": sha256_file(tok_path),
        },
    )
    (RESULTS / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    (RESULTS / "strategy_comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    (RESULTS / "optimization_trace.json").write_text(json.dumps(opt_trace, indent=2), encoding="utf-8")
    (RESULTS / "rejected_merges.json").write_text(json.dumps(rejected, indent=2, ensure_ascii=False), encoding="utf-8")
    (RESULTS / "vocab_allocation.json").write_text(json.dumps(winner_alloc, indent=2), encoding="utf-8")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": {
            str(p.relative_to(ROOT)): sha256_file(p)
            for p in [
                tok_path,
                RESULTS / "stats.json",
                DATA / "frozen" / "en_india.txt",
                DATA / "frozen" / "hi_india.txt",
                DATA / "frozen" / "te_india.txt",
                DATA / "frozen" / "bn_india.txt",
            ]
        },
    }
    (RESULTS / "manifest.sha256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Copy to web public
    import shutil

    (PUBLIC / "results").mkdir(parents=True, exist_ok=True)
    for name in [
        "stats.json",
        "strategy_comparison.json",
        "optimization_trace.json",
        "vocab_allocation.json",
        "grapheme_stats.json",
        "rejected_merges.json",
        "vocab_sweep_curves.json",
        "tokenizer.json",
        "vocab.json",
        "manifest.sha256.json",
    ]:
        src = RESULTS / name
        if src.exists():
            shutil.copy(src, PUBLIC / "results" / name)

    # Copy corpora for download
    for sub in ("raw", "frozen"):
        dst = PUBLIC / "corpora" / sub
        dst.mkdir(parents=True, exist_ok=True)
        for f in (DATA / sub).glob("*.txt"):
            shutil.copy(f, dst / f.name)

    for name in ["vocab.txt", "merges.txt"]:
        shutil.copy(RESULTS / name, PUBLIC / name)

    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
