"""Boundary-aware score landscape analysis (integer token counts)."""

from __future__ import annotations

from samabpe.scoring import compute_score
from samabpe.strategies import LANGS


def _lang_metrics(tokens: dict[str, int], word_units: dict[str, int]) -> dict[str, float]:
    return {lang: tokens[lang] / word_units[lang] for lang in LANGS}


def boundary_analysis(tokens: dict[str, int], word_units: dict[str, int]) -> dict:
    fert = _lang_metrics(tokens, word_units)
    score_data = compute_score(fert)
    ranked = sorted(LANGS, key=lambda l: fert[l])
    x_min_lang, x_max_lang = ranked[0], ranked[-1]

    languages = []
    for i, lang in enumerate(ranked):
        x = fert[lang]
        neighbours = []
        if i > 0:
            prev = ranked[i - 1]
            neighbours.append({"direction": "below", "language": prev, "x": fert[prev]})
        if i < len(ranked) - 1:
            nxt = ranked[i + 1]
            neighbours.append({"direction": "above", "language": nxt, "x": fert[nxt]})

        tokens_to_overtake_above = None
        if i < len(ranked) - 1:
            nxt = ranked[i + 1]
            # save enough tokens so x drops below next language
            target_x = fert[nxt] - 1e-15
            tokens_to_overtake_above = max(0, tokens[lang] - int(target_x * word_units[lang]) + 1)

        sensitivity = {}
        for save in (1, 5, 10, 25, 50, 100):
            trial_tokens = dict(tokens)
            trial_tokens[lang] = max(0, tokens[lang] - save)
            trial_fert = _lang_metrics(trial_tokens, word_units)
            trial_score = compute_score(trial_fert)
            sensitivity[str(save)] = {
                "tokens_saved": save,
                "new_x": trial_fert[lang],
                "new_x_min": trial_score["x_min"],
                "new_x_max": trial_score["x_max"],
                "new_gap": trial_score["max_min_gap"],
                "new_score": trial_score["score"],
                "score_delta": trial_score["score"] - score_data["score"],
                "x_max_language": max(trial_fert, key=trial_fert.get),
            }

        languages.append({
            "language": lang,
            "word_units": word_units[lang],
            "encoded_tokens": tokens[lang],
            "x": x,
            "rank": i + 1,
            "distance_from_x_min": x - score_data["x_min"],
            "distance_from_x_max": score_data["x_max"] - x,
            "is_x_min": lang == x_min_lang,
            "is_x_max": lang == x_max_lang,
            "tokens_to_overtake_next_above": tokens_to_overtake_above,
            "score_sensitivity_tokens_saved": sensitivity,
        })

    return {
        "x_min_language": x_min_lang,
        "x_max_language": x_max_lang,
        "current_gap": score_data["max_min_gap"],
        "current_score": score_data["score"],
        "languages": languages,
    }


def score_target_ladder(tokens: dict[str, int], word_units: dict[str, int]) -> dict:
    fert = _lang_metrics(tokens, word_units)
    score_data = compute_score(fert)
    x_max_lang = max(fert, key=fert.get)
    scenarios = []
    for save in (1, 5, 10, 25, 50, 100):
        trial_tokens = dict(tokens)
        trial_tokens[x_max_lang] = max(0, tokens[x_max_lang] - save)
        trial_fert = _lang_metrics(trial_tokens, word_units)
        trial_score = compute_score(trial_fert)
        scenarios.append({
            "tokens_saved_from_x_max": save,
            "x_max_language_before": x_max_lang,
            "hypothetical_fertilities": trial_fert,
            "new_x_min": trial_score["x_min"],
            "new_x_max": trial_score["x_max"],
            "new_x_max_language": max(trial_fert, key=trial_fert.get),
            "new_gap": trial_score["max_min_gap"],
            "new_score": trial_score["score"],
            "score_improvement_pct": (
                (trial_score["score"] - score_data["score"]) / score_data["score"] * 100
                if score_data["score"] else 0
            ),
            "boundary_transition": max(trial_fert, key=trial_fert.get) != x_max_lang,
        })
    return {
        "baseline": {"fertilities": fert, "gap": score_data["max_min_gap"], "score": score_data["score"]},
        "x_max_language": x_max_lang,
        "scenarios": scenarios,
    }
