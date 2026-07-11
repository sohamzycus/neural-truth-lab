"""Vocabulary sweep curves for budget simulator."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from samabpe.bpe import BPETokenizer
from samabpe.corpus import load_frozen
from samabpe.word_units import count_word_units

LANGS = ("en", "hi", "te", "bn")


def run_sweeps(
    data_dir: Path | str,
    sizes: list[int] | None = None,
    out_path: Path | str | None = None,
) -> dict:
    corpora = load_frozen(data_dir)
    sizes = sizes or [1000, 2000, 5000, 10000]
    curves: dict[str, list[dict]] = {lang: [] for lang in LANGS}
    pooled = "\n".join(corpora[l] for l in LANGS)

    for vs in sizes:
        tok = BPETokenizer.train(pooled, vs, pretokenization="whitespace")
        for lang in LANGS:
            wu = count_word_units(corpora[lang])
            tokens = tok.count_tokens(corpora[lang])
            curves[lang].append({
                "vocab_size": vs,
                "tokens": tokens,
                "word_units": wu,
                "fertility": tokens / wu if wu else 0,
            })

    # Allocation sweep (monolingual portions)
    alloc_curves: list[dict] = []
    for en_alloc in [2000, 2500, 3000]:
        remaining = 10000 - en_alloc - 2
        per_indic = remaining // 3
        allocation = {"en": en_alloc, "hi": per_indic, "te": per_indic, "bn": remaining - 2 * per_indic}
        from samabpe.strategies import train_allocated_monolingual

        res = train_allocated_monolingual(corpora, allocation=allocation)
        alloc_curves.append({
            "allocation": allocation,
            "fertilities": res.fertilities,
            "score": res.metrics["score"],
            "gap": res.metrics["max_min_gap"],
        })

    result = {"per_language": curves, "allocation_sweep": alloc_curves}
    if out_path:
        Path(out_path).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
