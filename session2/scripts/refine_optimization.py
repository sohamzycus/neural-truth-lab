#!/usr/bin/env python3
"""Fine bootstrap + Bengali-weight sweep targeting EN~1.15 and lower BN."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.bpe import BPETokenizer
from samabpe.corpus import load_frozen
from samabpe.strategies import EN_MAX_FERTILITY, LANGS, VOCAB_BUDGET, train_weighted_shared
from samabpe.unicode_utils import vocab_script_attribution
from samabpe.verify_core import run_verification, sha256_file

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "frozen"
PUBLIC = ROOT / "web" / "public" / "data" / "results"
TOK_PATH = RESULTS / "tokenizer.json"

BOOTSTRAP_GRID = [6150, 6250, 6300, 6350, 6400, 6450, 6500]
WEIGHT_GRID = [
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 3.5},
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 5.0},
    {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 6.0},
    {"en": 1.0, "hi": 2.5, "te": 3.0, "bn": 6.0},
    {"en": 1.0, "hi": 2.5, "te": 3.0, "bn": 8.0},
    {"en": 0.8, "hi": 2.5, "te": 3.0, "bn": 8.0},
]


def _entry(name: str, res, corpora: dict[str, str], extra: dict) -> dict:
    fert = res.fertilities
    m = res.metrics
    tokens = {lang: res.tokenizer.count_tokens(corpora[lang]) for lang in LANGS}
    return {
        "name": name,
        "vocabulary_size": res.tokenizer.vocab_size,
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
        **extra,
    }


def token_distribution(tok: BPETokenizer, corpora: dict[str, str]) -> dict:
    lang_usage: dict[str, Counter[str]] = {lang: Counter() for lang in LANGS}
    for lang in LANGS:
        for t in tok.encode(corpora[lang]):
            lang_usage[lang][t] += 1
    script_attr = vocab_script_attribution(tok)
    return {
        "vocabulary_size": tok.vocab_size,
        "script_attribution": script_attr,
        "corpus_token_totals": {lang: sum(lang_usage[lang].values()) for lang in LANGS},
        "unique_tokens_used_per_language": {lang: len(lang_usage[lang]) for lang in LANGS},
        "bengali_dominant_vocab": script_attr.get("bengali", 0),
        "latin_dominant_vocab": script_attr.get("latin", 0),
        "shared_vocab": script_attr.get("shared", 0),
    }


def patch_strategy_comparison(result) -> None:
    path = RESULTS / "strategy_comparison.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    fert = result.fertilities
    for s in data.get("strategies", []):
        if s.get("winner"):
            s["fertility"] = dict(fert)
            s["gap"] = result.max_min_gap
            s["score"] = result.score
            s["englishConstraintPassed"] = result.english_pass
            s["vocabularySize"] = result.vocabulary_size
    for leg in data.get("legacy", []):
        if leg.get("strategy") == "weighted_shared":
            leg.update({
                "en_fertility": fert["en"],
                "hi_fertility": fert["hi"],
                "te_fertility": fert["te"],
                "bn_fertility": fert["bn"],
                "max_min_gap": result.max_min_gap,
                "score": result.score,
                "english_pass": result.english_pass,
                "vocabulary_size": result.vocabulary_size,
            })
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def sync_all() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    dist = ROOT / "web" / "dist" / "data" / "results"
    dist.mkdir(parents=True, exist_ok=True)
    for name in RESULTS.glob("*.json"):
        shutil.copy(name, PUBLIC / name.name)
        shutil.copy(name, dist / name.name)
    for extra in ("vocab.json", "vocab.txt", "merges.txt"):
        src = RESULTS / extra
        if src.exists():
            shutil.copy(src, PUBLIC.parent / extra)
            shutil.copy(src, ROOT / "web" / "dist" / "data" / extra)


def main() -> int:
    corpora = load_frozen(DATA.parent)
    baseline = run_verification(TOK_PATH, DATA)
    baseline_score = baseline.score
    print(f"Current verified score: {baseline_score:.4f} EN={baseline.fertilities['en']:.4f} BN={baseline.fertilities['bn']:.4f}")

    results: list[dict] = []

    print("\nFine bootstrap sweep...")
    for boot in BOOTSTRAP_GRID:
        t0 = time.time()
        res = train_weighted_shared(corpora, en_bootstrap=boot)
        e = _entry(f"bootstrap_{boot}", res, corpora, {"en_bootstrap": boot, "runtime_sec": round(time.time() - t0, 1)})
        results.append(e)
        print(f"  boot={boot} EN={e['fertilities']['en']:.4f} BN={e['fertilities']['bn']:.4f} score={e['score']:.2f} pass={e['english_pass']}")

    valid_boots = sorted({r["en_bootstrap"] for r in results if r["english_pass"]}, reverse=True)[:4]
    print(f"\nBengali-weight sweep (boots={valid_boots})...")
    for boot in valid_boots:
        for i, weights in enumerate(WEIGHT_GRID, 1):
            t0 = time.time()
            res = train_weighted_shared(corpora, en_bootstrap=boot, weights=weights)
            e = _entry(
                f"boot_{boot}_w{i}",
                res,
                corpora,
                {"en_bootstrap": boot, "weights": weights, "runtime_sec": round(time.time() - t0, 1)},
            )
            results.append(e)
            if e["english_pass"]:
                print(
                    f"  boot={boot} w={weights} EN={e['fertilities']['en']:.4f} "
                    f"BN={e['fertilities']['bn']:.4f} score={e['score']:.2f}"
                )

    valid = [r for r in results if r["english_pass"] and r["vocab_pass"]]
    # Prefer higher score; tie-break toward EN near 1.15 and lower BN
    def rank_key(r: dict) -> tuple:
        en = r["fertilities"]["en"]
        bn = r["fertilities"]["bn"]
        en_target_penalty = abs(en - 1.15)
        return (r["score"], -bn, -en_target_penalty)

    best = max(valid, key=rank_key) if valid else None
    (RESULTS / "refine_sweep.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    if not best or best["score"] <= baseline_score:
        print(f"\nNo improvement over {baseline_score:.4f} — keeping current tokenizer")
        dist = token_distribution(BPETokenizer.load(TOK_PATH), corpora)
        (RESULTS / "token_distribution.json").write_text(json.dumps(dist, indent=2), encoding="utf-8")
        patch_strategy_comparison(baseline)
        sync_all()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "verify.py")], cwd=ROOT, check=False)
        sync_all()
        return 0

    print(f"\nWINNER: {best['name']} score={best['score']:.4f} EN={best['fertilities']['en']:.4f} BN={best['fertilities']['bn']:.4f}")

    boot = best.get("en_bootstrap", 6000)
    weights = best.get("weights")
    new_tok = train_weighted_shared(corpora, en_bootstrap=boot, weights=weights).tokenizer
    new_tok.save(TOK_PATH)

    vocab_attr = vocab_script_attribution(new_tok)
    (RESULTS / "vocab_allocation.json").write_text(json.dumps(vocab_attr, indent=2), encoding="utf-8")
    dist = token_distribution(new_tok, corpora)
    (RESULTS / "token_distribution.json").write_text(json.dumps(dist, indent=2), encoding="utf-8")

    result = run_verification(TOK_PATH, DATA)
    patch_strategy_comparison(result)
    sync_all()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "verify.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "final_analysis.py")], cwd=ROOT, check=False)
    sync_all()
    print(f"Tokenizer SHA-256: {sha256_file(TOK_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
