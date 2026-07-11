"""Score-directed vocabulary ROI — PREDICTED and VERIFIED candidate impacts."""

from __future__ import annotations

from collections import Counter

from samabpe.bpe import BPETokenizer
from samabpe.scoring import compute_score
from samabpe.strategies import EN_MAX_FERTILITY, LANGS, _trial_fertilities
from samabpe.word_units import count_word_units, word_units


def _article_word_freq(corpora: dict[str, str]) -> dict[str, Counter[str]]:
    return {lang: Counter(word_units(corpora[lang])) for lang in LANGS}


def _predict_merge_impact(
    tok: BPETokenizer,
    corpora: dict[str, str],
    pair: tuple[str, str],
    splits: dict[str, list[str]],
    baseline: dict,
) -> dict:
    new_token = pair[0] + pair[1]
    if new_token in tok.vocab:
        return {"skip": True, "reason": "already in vocabulary"}
    fert = _trial_fertilities(tok, corpora, pair, splits)
    m = compute_score(fert)
    return {
        "status": "PREDICTED",
        "candidate_token": new_token,
        "pair": list(pair),
        "fertilities": fert,
        "x_min": m["x_min"],
        "x_max": m["x_max"],
        "gap_delta": m["max_min_gap"] - baseline["max_min_gap"],
        "score_delta": m["score"] - baseline["score"],
        "english_pass": fert["en"] <= EN_MAX_FERTILITY,
    }


def compute_score_roi_candidates(
    tok: BPETokenizer,
    corpora: dict[str, str],
    *,
    top_pairs: int = 40,
) -> dict:
    """Rank merge candidates by predicted gap reduction (Track A — no deliberate degradation)."""
    baseline_fert = {lang: tok.count_tokens(corpora[lang]) / count_word_units(corpora[lang]) for lang in LANGS}
    baseline = compute_score(baseline_fert)
    x_max_lang = max(baseline_fert, key=baseline_fert.get)
    word_freq = _article_word_freq(corpora)

    pooled_splits: dict[str, list[str]] = {}
    pair_counts: Counter[tuple[str, str]] = Counter()
    for lang in LANGS:
        for w, c in word_freq[lang].items():
            syms = tok._apply_merges_to_word(tok._word_to_symbols(w))
            pooled_splits[w] = syms
            for i in range(len(syms) - 1):
                pair_counts[(syms[i], syms[i + 1])] += c

    candidates: list[dict] = []
    for pair, freq in pair_counts.most_common(top_pairs * 3):
        pred = _predict_merge_impact(tok, corpora, pair, pooled_splits, baseline)
        if pred.get("skip"):
            continue
        if not pred["english_pass"]:
            continue
        candidates.append({
            "language_focus": x_max_lang,
            "word": pred["candidate_token"],
            "article_frequency": freq,
            "current_tokenization": list(pair),
            "proposed_tokenization": [pred["candidate_token"]],
            "vocabulary_slots_consumed": 1,
            "predicted_gap_delta": pred["gap_delta"],
            "predicted_score_delta": pred["score_delta"],
            "status": "PREDICTED",
        })
        if len(candidates) >= top_pairs:
            break

    # Measured language-level gap contribution (optimization priority signal)
    for lang in LANGS:
        gap_above_min = baseline_fert[lang] - baseline["x_min"]
        if gap_above_min <= 0:
            continue
        total_wu = sum(word_freq[lang].values())
        candidates.append({
            "language_focus": lang,
            "word": f"[{lang} corpus aggregate]",
            "article_frequency": total_wu,
            "current_fertility": baseline_fert[lang],
            "gap_above_x_min": gap_above_min,
            "evaluation_tokens_saved_potential": int(gap_above_min * total_wu * 0.01),
            "vocabulary_slots_consumed": 0,
            "roi_per_slot": None,
            "status": "MEASURED",
            "note": "language-level gap contribution; slot count requires verified merge experiment",
        })

    candidates.sort(
        key=lambda c: c.get("predicted_score_delta") or c.get("roi_per_slot") or c.get("gap_above_x_min", 0),
        reverse=True,
    )
    return {
        "baseline": {
            "fertilities": baseline_fert,
            "x_min": baseline["x_min"],
            "x_max": baseline["x_max"],
            "max_min_gap": baseline["max_min_gap"],
            "score": baseline["score"],
            "x_max_language": x_max_lang,
        },
        "track": "A_compression_honest",
        "definition": "PREDICTED impact from single-merge fertility estimate; VERIFIED only after full tokenizer rebuild",
        "candidates": candidates[:top_pairs],
        "verified_candidates": [],
        "note": "At 10K vocab most frequent pair merges already absorbed; word-level headroom is limited",
    }
