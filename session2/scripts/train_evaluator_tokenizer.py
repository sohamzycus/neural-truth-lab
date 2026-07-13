#!/usr/bin/env python3
"""Phases 5–8 — train HF BPE candidates under evaluator contract and select winner."""

from __future__ import annotations

import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.evaluator_scoring import LANGS
from samabpe.hf_bpe import (
    DEFAULT_WEIGHTS,
    VOCAB_BUDGET,
    evaluate_hf_tokenizer,
    load_faithful_corpora,
    sha256_file,
    train_hf_bpe,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
RESULTS = ROOT / "results"
CANDIDATES = RESULTS / "evaluator_candidates"
OUT_COMPARISON = RESULTS / "evaluator_strategy_comparison.json"
OUT_WINNER = RESULTS / "evaluator_winner.json"


def _entry(
    strategy: str,
    weights: dict[str, int],
    metrics,
    tok_path: Path,
    tok_vocab_size: int,
    extra: dict | None = None,
) -> dict:
    row = {
        "strategy": strategy,
        "weights": weights,
        "vocabulary_size": tok_vocab_size,
        "tokenizer_path": str(tok_path.relative_to(ROOT)),
        "tokenizer_sha256": sha256_file(tok_path) if tok_path.exists() else None,
        **metrics.to_dict(),
        "evidence_type": "MEASURED",
    }
    if extra:
        row.update(extra)
    return row


def strategy_reference_baseline(corpora: dict[str, str]) -> dict:
    weights = dict(DEFAULT_WEIGHTS)
    path = CANDIDATES / "01_reference_shared_bpe.json"
    tok = train_hf_bpe(corpora, weights=weights, output_path=path)
    m = evaluate_hf_tokenizer(tok, corpora)
    return _entry("reference_compatible_shared_bpe", weights, m, path, tok.get_vocab_size(with_added_tokens=True))


def strategy_weight_search(corpora: dict[str, str], top_k: int = 8) -> list[dict]:
    grid_en = [2, 3, 4, 5, 6]
    grid_hi = [3, 4, 5, 6, 7]
    grid_te = [3, 4, 5, 6]
    grid_bn = [1, 2, 3, 4]
    combos = list(itertools.product(grid_en, grid_hi, grid_te, grid_bn))
    print(f"  grid size: {len(combos)} configurations")
    results: list[dict] = []
    idx = 0
    for en, hi, te, bn in combos:
        weights = {"en": en, "hi": hi, "te": te, "bn": bn}
        path = CANDIDATES / f"02_weight_{en}_{hi}_{te}_{bn}.json"
        if path.exists():
            from tokenizers import Tokenizer

            tok = Tokenizer.from_file(str(path))
        else:
            tok = train_hf_bpe(corpora, weights=weights, output_path=path)
        m = evaluate_hf_tokenizer(tok, corpora)
        results.append(
            _entry(
                "weight_search_bpe",
                weights,
                m,
                path,
                tok.get_vocab_size(with_added_tokens=True),
                {"grid_id": idx},
            )
        )
        idx += 1
        if idx % 20 == 0:
            print(f"  weight grid {idx}… best adj so far: {max(r['adjusted_score'] for r in results):.2f}")
    results.sort(key=lambda r: r["adjusted_score"], reverse=True)
    return results[:top_k]


def strategy_adaptive_balance(corpora: dict[str, str], seed_weights: dict[str, int]) -> dict:
    """Boost languages at X_max, trim X_min — one refinement round from seed."""
    from tokenizers import Tokenizer

    path0 = CANDIDATES / "03_adaptive_seed.json"
    tok = train_hf_bpe(corpora, weights=seed_weights, output_path=path0)
    m0 = evaluate_hf_tokenizer(tok, corpora)
    fert = m0.fertilities
    x_max_lang = max(fert, key=fert.get)
    x_min_lang = min(fert, key=fert.get)
    weights = dict(seed_weights)
    weights[x_max_lang] = weights.get(x_max_lang, 2) + 2
    weights[x_min_lang] = max(1, weights.get(x_min_lang, 2) - 1)
    path = CANDIDATES / "03_adaptive_balanced.json"
    tok2 = train_hf_bpe(corpora, weights=weights, output_path=path)
    m = evaluate_hf_tokenizer(tok2, corpora)
    return _entry(
        "adaptive_fertility_balancing",
        weights,
        m,
        path,
        tok2.get_vocab_size(with_added_tokens=True),
        {"seed_weights": seed_weights, "x_max_lang": x_max_lang, "x_min_lang": x_min_lang},
    )


def strategy_boundary_search(corpora: dict[str, str], seeds: list[dict[str, int]]) -> list[dict]:
    """Local perturbations around top weight configs."""
    out: list[dict] = []
    for i, seed in enumerate(seeds[:3]):
        for delta in (-1, 0, 1):
            w = {k: max(1, seed[k] + (delta if k == "hi" else 0)) for k in LANGS}
            path = CANDIDATES / f"04_boundary_{i}_{delta}.json"
            tok = train_hf_bpe(corpora, weights=w, output_path=path)
            m = evaluate_hf_tokenizer(tok, corpora)
            out.append(
                _entry(
                    "boundary_aware_search",
                    w,
                    m,
                    path,
                    tok.get_vocab_size(with_added_tokens=True),
                    {"seed": seed},
                )
            )
    out.sort(key=lambda r: r["adjusted_score"], reverse=True)
    return out[:5]


def strategy_samabpe_inspired(corpora: dict[str, str]) -> dict:
    """English-heavy bootstrap weighting adapted to HF pipeline."""
    weights = {"en": 8, "hi": 4, "te": 4, "bn": 2}
    path = CANDIDATES / "05_samabpe_inspired_weighted.json"
    tok = train_hf_bpe(corpora, weights=weights, output_path=path)
    m = evaluate_hf_tokenizer(tok, corpora)
    return _entry("samabpe_inspired_weighted_shared", weights, m, path, tok.get_vocab_size(with_added_tokens=True))


def main() -> int:
    if not (CORPUS / "en.faithful.md").exists():
        print("Run scripts/build_wiki_faithful_markdown.py first")
        return 1

    CANDIDATES.mkdir(parents=True, exist_ok=True)
    corpora = load_faithful_corpora(CORPUS)
    ts = datetime.now(timezone.utc).isoformat()

    print("Strategy 1 — reference-compatible baseline…")
    s1 = strategy_reference_baseline(corpora)
    print(f"  adjusted={s1['adjusted_score']:.2f} spread={s1['spread']:.4f} HI={s1['fertilities']['hi']:.4f}")

    print("Strategy 2 — weight search (coarse grid)…")
    s2_top = strategy_weight_search(corpora, top_k=12)

    print("Strategy 3 — adaptive fertility balancing…")
    best_seed = s2_top[0]["weights"] if s2_top else DEFAULT_WEIGHTS
    s3 = strategy_adaptive_balance(corpora, best_seed)

    print("Strategy 4 — boundary-aware local search…")
    s4_top = strategy_boundary_search(corpora, [r["weights"] for r in s2_top[:3]])

    print("Strategy 5 — SamaBPE-inspired weights…")
    s5 = strategy_samabpe_inspired(corpora)

    all_rows = [s1, s3, s5, *s2_top, *s4_top]
    # dedupe by sha
    seen = set()
    unique: list[dict] = []
    for r in sorted(all_rows, key=lambda x: x["adjusted_score"], reverse=True):
        h = r.get("tokenizer_sha256")
        if h in seen:
            continue
        seen.add(h)
        unique.append(r)

    winner = unique[0]
    comparison = {
        "generated_at": ts,
        "corpus": "corpus/*.faithful.md",
        "objective": "maximize adjusted_score = raw_score / hindi_penalty",
        "strategies_evaluated": len(unique),
        "candidates": unique,
        "winner": winner,
    }
    OUT_COMPARISON.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    # Promote winner to submission paths (do not overwrite old tokenizer.json)
    winner_src = ROOT / winner["tokenizer_path"]
    hf_winner = RESULTS / "tokenizer_hf.json"
    hf_winner.write_bytes(winner_src.read_bytes())

    OUT_WINNER.write_text(
        json.dumps(
            {
                "frozen_at": ts,
                "winner": winner,
                "tokenizer_hf_path": str(hf_winner.relative_to(ROOT)),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nWinner: {winner['strategy']} weights={winner['weights']}")
    print(f"  adjusted={winner['adjusted_score']:.4f} raw={winner['raw_score']:.4f}")
    print(f"  spread={winner['spread']:.4f} hindi_penalty={winner['hindi_penalty']:.4f}")
    for lang in LANGS:
        print(f"  {lang}: X={winner['fertilities'][lang]:.4f}")
    print(f"→ {OUT_COMPARISON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
