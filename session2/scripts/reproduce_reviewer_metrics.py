#!/usr/bin/env python3
"""Phase 4 — reproduce reviewer metrics and document root causes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.bpe import BPETokenizer
from samabpe.evaluator_scoring import compute_evaluator_metrics, hindi_penalty
from samabpe.evaluator_text import count_wordish_units
from samabpe.hf_bpe import load_faithful_corpora
from samabpe.scoring import compute_score
from samabpe.word_units import count_word_units

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CORPUS = ROOT / "corpus"
OLD_FROZEN = ROOT / "data" / "frozen"
OUT = RESULTS / "reviewer_reproduction.json"

REVIEWER = {
    "fertilities": {"en": 5.815, "hi": 4.294, "te": 4.761, "bn": 4.620},
    "raw_score": 657.5,
    "hindi_penalty": 13.180,
    "adjusted_score": 49.9,
}


def _metrics_from_fertilities(fert: dict[str, float], tokens: dict, units: dict) -> dict:
    m = compute_evaluator_metrics(tokens, units)
    return m.to_dict()


def _compare(label: str, reproduced: dict, reviewer: dict) -> dict:
    rows = {}
    for key in ("fertilities", "raw_score", "hindi_penalty", "adjusted_score"):
        if key == "fertilities":
            for lang in ("en", "hi", "te", "bn"):
                rv = reviewer["fertilities"][lang]
                loc = reproduced["fertilities"][lang]
                diff = loc - rv
                rel = diff / rv if rv else None
                rows[f"fertility_{lang}"] = {
                    "reviewer": rv,
                    "reproduced": loc,
                    "absolute_diff": diff,
                    "relative_diff": rel,
                    "status": "close" if abs(diff) < 0.05 else "divergent",
                }
        else:
            rv = reviewer[key]
            loc = reproduced[key]
            diff = loc - rv
            rel = diff / rv if rv else None
            rows[key] = {
                "reviewer": rv,
                "reproduced": loc,
                "absolute_diff": diff,
                "relative_diff": rel,
                "status": "close" if abs(rel or 0) < 0.05 else "divergent",
            }
    return {"scenario": label, "metrics": rows}


def _encode_old(tok: BPETokenizer, text: str) -> int:
    return tok.count_tokens(text)


def main() -> int:
    tok_path = RESULTS / "tokenizer.json"
    if not tok_path.exists():
        print("ERROR: missing tokenizer.json")
        return 1

    old_tok = BPETokenizer.load(tok_path)
    faithful = load_faithful_corpora(CORPUS) if (CORPUS / "en.faithful.md").exists() else {}
    old_plain = {
        lang: (OLD_FROZEN / f"{lang}_india.txt").read_text(encoding="utf-8")
        for lang in ("en", "hi", "te", "bn")
    }

    scenarios: list[dict] = []

    # A: Old tokenizer + old corpus + old denominator (our prior contract)
    if old_plain:
        tokens_a = {l: _encode_old(old_tok, old_plain[l]) for l in old_plain}
        units_a = {l: count_word_units(old_plain[l]) for l in old_plain}
        fert_a = {l: tokens_a[l] / units_a[l] for l in old_plain}
        score_a = compute_score(fert_a)
        scenarios.append(
            {
                "id": "old_tokenizer_old_corpus_old_denominator",
                "description": "Custom SamaBPE encoder + plain Wikipedia extract + NFC whitespace word units",
                "metrics": {
                    "fertilities": fert_a,
                    "gap": score_a["max_min_gap"],
                    "score_old_contract": score_a["score"],
                },
            }
        )

    # B: Old tokenizer + faithful markdown + evaluator denominator
    if faithful:
        tokens_b = {l: _encode_old(old_tok, faithful[l]) for l in faithful}
        units_b = {l: count_wordish_units(faithful[l]) for l in faithful}
        rep_b = compute_evaluator_metrics(tokens_b, units_b).to_dict()
        scenarios.append(
            {
                "id": "old_tokenizer_faithful_corpus_evaluator_denominator",
                "description": "Custom encoder on wiki-faithful Markdown with evaluator word-ish units",
                "metrics": rep_b,
                "comparison": _compare("faithful_evaluator", rep_b, REVIEWER),
            }
        )

        # C: Old tokenizer + faithful + OLD denominator (isolation)
        units_c = {l: count_word_units(faithful[l]) for l in faithful}
        rep_c = compute_evaluator_metrics(tokens_b, units_c).to_dict()
        scenarios.append(
            {
                "id": "old_tokenizer_faithful_corpus_old_denominator",
                "description": "Custom encoder on faithful MD but old NFC whitespace denominator",
                "metrics": rep_c,
            }
        )

        # D: Simulate reviewer best-effort — encode by splitting on whitespace only (no BPE merges)
        # i.e. character count proxy / vocab lookup failure → ~chars per word-ish unit
        naive_tokens = {}
        for l, text in faithful.items():
            # Pretend each whitespace token becomes len(word) subword tokens (upper bound chaos)
            naive_tokens[l] = sum(len(w) for w in text.split())
        rep_d = compute_evaluator_metrics(naive_tokens, units_b).to_dict()
        scenarios.append(
            {
                "id": "simulated_naive_char_tokens",
                "description": "Illustrative: reviewer could not apply custom merge table — per-char token proxy",
                "metrics": rep_d,
                "comparison": _compare("naive_char_proxy", rep_d, REVIEWER),
            }
        )

    # E: Reviewer arithmetic check from their published fertilities
    rev_units = {l: 1 for l in REVIEWER["fertilities"]}  # placeholder
    rev_tokens = {l: int(REVIEWER["fertilities"][l] * 1000) for l in REVIEWER["fertilities"]}
    # scale-independent — use fertilities directly
    xs = list(REVIEWER["fertilities"].values())
    spread = max(xs) - min(xs)
    raw = 1000.0 / spread
    pen = hindi_penalty(REVIEWER["fertilities"]["hi"])
    scenarios.append(
        {
            "id": "reviewer_arithmetic_from_published_fertilities",
            "description": "Verify reviewer score arithmetic from published X values",
            "metrics": {
                "fertilities": REVIEWER["fertilities"],
                "spread": spread,
                "raw_score": raw,
                "hindi_penalty": pen,
                "adjusted_score": raw / pen,
            },
        }
    )

    root_causes = [
        {
            "factor": "tokenizer_format",
            "impact": "high",
            "detail": (
                "Submitted artefact used custom SamaBPE JSON (character BPE + </w> markers), "
                "not HuggingFace Tokenizer.from_file(). Reviewer stated they could only estimate "
                "from tokenizer data without executable decoder."
            ),
        },
        {
            "factor": "corpus",
            "impact": "high",
            "detail": (
                "Prior submission used MediaWiki plain-text extracts (explaintext=true). "
                "Evaluator uses wiki-faithful Markdown from REST HTML — different token/structure density."
            ),
        },
        {
            "factor": "denominator",
            "impact": "medium",
            "detail": (
                "Old contract: NFC + whitespace split, punctuation attached. "
                "Evaluator: NFKC + replace non-letter/mark/number runs with space, then split."
            ),
        },
        {
            "factor": "normalizer",
            "impact": "low-medium",
            "detail": "NFC vs NFKC — compatibility decomposition affects Indic and punctuation adjacency.",
        },
        {
            "factor": "scoring",
            "impact": "high",
            "detail": (
                "Old contract: score = 1000/(Xmax-Xmin) with English hard cap at training. "
                "Evaluator adds hindi_penalty = exp(max(0, X_hi/1.2 - 1)); "
                "reviewer Hindi X=4.294 → penalty ≈ 13.18 crushing adjusted score to 49.9."
            ),
        },
    ]

    out = {
        "reviewer_published": REVIEWER,
        "scenarios": scenarios,
        "root_cause_analysis": root_causes,
        "closest_reproduction_note": (
            "Exact 49.9 requires reviewer fertility vector; arithmetic reproduces from EN=5.815, HI=4.294. "
            "Custom encoder on faithful corpus yields different fertilities — see scenario comparisons."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}")
    if faithful:
        b = scenarios[1]["metrics"]
        print(
            f"Old tokenizer on faithful MD (evaluator denom): "
            f"adj={b['adjusted_score']:.1f} raw={b['raw_score']:.1f} "
            f"EN={b['fertilities']['en']:.3f} HI={b['fertilities']['hi']:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
