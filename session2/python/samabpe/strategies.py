"""Five tokenizer training strategies."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable

from samabpe.bpe import BPETokenizer, PretokenMode
from samabpe.scoring import compute_score
from samabpe.word_units import count_word_units

LANGS = ("en", "hi", "te", "bn")
VOCAB_BUDGET = 10_000
EN_MAX_FERTILITY = 1.2


@dataclass
class StrategyResult:
    name: str
    tokenizer: BPETokenizer
    fertilities: dict[str, float]
    metrics: dict
    vocab_allocation: dict[str, int]


def _count_tokens_from_splits(word_freqs: Counter[str], splits: dict[str, list[str]]) -> int:
    return sum(len(splits[w]) * c for w, c in word_freqs.items())


def _fertilities_from_splits(
    corpora: dict[str, str],
    pretokenize_fn,
    splits: dict[str, list[str]],
) -> dict[str, float]:
    out = {}
    for lang, text in corpora.items():
        wf: Counter[str] = Counter()
        for pt in pretokenize_fn(text):
            wf[pt] += 1
        tokens = _count_tokens_from_splits(wf, splits)
        out[lang] = tokens / count_word_units(text)
    return out


def _fertilities(tok: BPETokenizer, corpora: dict[str, str]) -> dict[str, float]:
    return {
        lang: tok.count_tokens(text) / count_word_units(text)
        for lang, text in corpora.items()
    }


def _trial_fertilities(
    tok: BPETokenizer,
    corpora: dict[str, str],
    pair: tuple[str, str],
    base_splits: dict[str, list[str]],
) -> dict[str, float]:
    """Fast fertility estimate by applying one merge to cached splits."""
    out = {}
    for lang, text in corpora.items():
        wf: Counter[str] = Counter()
        for pt in tok.pretokenize(text):
            wf[pt] += 1
        total = 0
        for word, freq in wf.items():
            syms = base_splits.get(word, tok._word_to_symbols(word))
            syms = tok._merge_pair(syms, pair)
            total += len(syms) * freq
        out[lang] = total / count_word_units(text)
    return out


def train_shared_vanilla(corpora: dict[str, str], vocab_size: int = VOCAB_BUDGET) -> StrategyResult:
    pooled = "\n".join(corpora[l] for l in LANGS)
    tok = BPETokenizer.train(pooled, vocab_size, pretokenization="whitespace")
    fert = _fertilities(tok, corpora)
    return StrategyResult(
        name="shared_vanilla",
        tokenizer=tok,
        fertilities=fert,
        metrics=compute_score(fert),
        vocab_allocation={"shared": max(0, tok.vocab_size - 7500), "en": min(7500, tok.vocab_size), "hi": 0, "te": 0, "bn": 0},
    )


def train_allocated_monolingual(
    corpora: dict[str, str],
    allocation: dict[str, int] | None = None,
    vocab_size: int = VOCAB_BUDGET,
) -> StrategyResult:
    """Per-language BPE then merge vocabularies and merge rules."""
    if allocation is None:
        per = (vocab_size - 4) // 4  # reserve 4 for specials overlap
        allocation = {l: per for l in LANGS}

    merged_vocab: dict[str, int] = {"<unk>": 0, "<pad>": 1}
    merged_merges: list[tuple[str, str]] = []
    lang_contrib: dict[str, int] = {l: 0 for l in LANGS}

    for lang in LANGS:
        sub = BPETokenizer.train(corpora[lang], allocation[lang], pretokenization="whitespace")
        before = len(merged_vocab)
        for token, _ in sorted(sub.vocab.items(), key=lambda kv: kv[1]):
            if token not in merged_vocab:
                merged_vocab[token] = len(merged_vocab)
        lang_contrib[lang] = len(merged_vocab) - before
        for m in sub.merges:
            if m not in merged_merges:
                merged_merges.append(m)

    # Trim to budget if merged vocab exceeds
    if len(merged_vocab) > vocab_size:
        items = sorted(merged_vocab.items(), key=lambda kv: kv[1])[:vocab_size]
        merged_vocab = dict(items)

    tok = BPETokenizer(
        vocab=merged_vocab,
        merges=merged_merges[: max(0, vocab_size - len(merged_vocab))],
        pretokenization="whitespace",
    )
    fert = _fertilities(tok, corpora)
    return StrategyResult(
        name="allocated_monolingual",
        tokenizer=tok,
        fertilities=fert,
        metrics=compute_score(fert),
        vocab_allocation={
            "shared": 2,
            **lang_contrib,
        },
    )


def train_weighted_shared(
    corpora: dict[str, str],
    weights: dict[str, float] | None = None,
    vocab_size: int = VOCAB_BUDGET,
) -> StrategyResult:
    weights = weights or {"en": 1.0, "hi": 2.0, "te": 2.5, "bn": 2.5}
    pooled = "\n".join(corpora[l] for l in LANGS)
    # English-seeded shared BPE with Indic-weighted continuation
    en_seed = BPETokenizer.train(corpora["en"], 7500, pretokenization="whitespace")
    pair_weights: Counter[tuple[str, str]] = Counter()
    base = BPETokenizer(pretokenization="whitespace")
    for lang in LANGS:
        w = weights.get(lang, 1.0)
        for pt in base.pretokenize(corpora[lang]):
            syms = base._word_to_symbols(pt)
            for i in range(len(syms) - 1):
                pair_weights[(syms[i], syms[i + 1])] += w
    tok = BPETokenizer.train(
        pooled,
        vocab_size,
        pretokenization="whitespace",
        pair_weights=pair_weights,
        seed_merges=en_seed.merges,
    )
    fert = _fertilities(tok, corpora)
    return StrategyResult(
        name="weighted_shared",
        tokenizer=tok,
        fertilities=fert,
        metrics=compute_score(fert),
        vocab_allocation={"shared": max(0, tok.vocab_size - 7500), "en": min(7500, tok.vocab_size), "hi": 0, "te": 0, "bn": 0},
    )


def train_grapheme_aware(corpora: dict[str, str], vocab_size: int = VOCAB_BUDGET) -> StrategyResult:
    pooled = "\n".join(corpora[l] for l in LANGS)
    tok = BPETokenizer.train(pooled, vocab_size, pretokenization="grapheme")
    fert = _fertilities(tok, corpora)
    return StrategyResult(
        name="grapheme_aware",
        tokenizer=tok,
        fertilities=fert,
        metrics=compute_score(fert),
        vocab_allocation={"shared": max(0, tok.vocab_size - 7500), "en": min(7500, tok.vocab_size), "hi": 0, "te": 0, "bn": 0},
    )


def train_score_directed_adaptive(
    corpora: dict[str, str],
    vocab_size: int = VOCAB_BUDGET,
    max_steps: int = 80,
) -> tuple[StrategyResult, list[dict], list[dict]]:
    """English-seeded BPE then fairness-directed merges for remaining budget."""
    pooled = "\n".join(corpora[l] for l in LANGS)
    en_seed = BPETokenizer.train(corpora["en"], 7500, pretokenization="whitespace")
    tok = BPETokenizer(
        vocab=dict(en_seed.vocab),
        merges=list(en_seed.merges),
        pretokenization="whitespace",
        special_tokens=dict(en_seed.special_tokens),
    )
    trace: list[dict] = []
    rejected: list[dict] = []

    def snapshot(step: int, note: str) -> dict:
        fert = _fertilities(tok, corpora)
        m = compute_score(fert)
        return {
            "step": step,
            "note": note,
            "fertilities": fert,
            "max_min_gap": m["max_min_gap"],
            "score": m["score"],
            "vocab_size": tok.vocab_size,
        }

    trace.append(snapshot(0, "english_seed_7500"))

    word_freqs: Counter[str] = Counter()
    for pt in tok.pretokenize(pooled):
        word_freqs[pt] += 1
    splits = {w: tok._apply_merges_to_word(tok._word_to_symbols(w)) for w in word_freqs}

    step = 0
    while tok.vocab_size < vocab_size and step < max_steps:
        pair_counts: Counter[tuple[str, str]] = Counter()
        for word, freq in word_freqs.items():
            syms = splits[word]
            for i in range(len(syms) - 1):
                pair_counts[(syms[i], syms[i + 1])] += freq

        if not pair_counts:
            break

        # Top candidates by frequency
        candidates = [p for p, _ in pair_counts.most_common(8)]
        best_pair = None
        best_score = -1.0
        best_fert: dict[str, float] = {}
        old_fert = _fertilities(tok, corpora)
        old_metrics = compute_score(old_fert)

        for pair in candidates:
            new_token = pair[0] + pair[1]
            if new_token in tok.vocab:
                continue
            fert = _trial_fertilities(tok, corpora, pair, splits)
            if fert["en"] > EN_MAX_FERTILITY:
                rejected.append({
                    "candidate": new_token,
                    "pair": list(pair),
                    "frequency": pair_counts[pair],
                    "language": "shared",
                    "old_score": old_metrics["score"],
                    "predicted_score": compute_score(fert)["score"],
                    "reason": f"English fertility {fert['en']:.4f} > {EN_MAX_FERTILITY}",
                })
                continue

            m = compute_score(fert)
            if m["score"] > best_score:
                best_score = m["score"]
                best_pair = pair
                best_fert = fert

        if best_pair is None:
            best_pair = pair_counts.most_common(1)[0][0]
            new_token = best_pair[0] + best_pair[1]
            if _trial_fertilities(tok, corpora, best_pair, splits)["en"] > EN_MAX_FERTILITY:
                break
            rejected.append({
                "candidate": new_token,
                "pair": list(best_pair),
                "frequency": pair_counts[best_pair],
                "language": "shared",
                "old_score": old_metrics["score"],
                "predicted_score": old_metrics["score"],
                "reason": "No fairness-improving candidate; vanilla fallback",
            })

        new_tok_str = best_pair[0] + best_pair[1]
        tok.merges.append(best_pair)
        tok._rebuild_merge_ranks()
        if new_tok_str not in tok.vocab:
            tok.vocab[new_tok_str] = len(tok.vocab)

        for word in splits:
            splits[word] = tok._merge_pair(splits[word], best_pair)

        step += 1
        new_fert = _fertilities(tok, corpora)
        new_m = compute_score(new_fert)
        trace.append({
            **snapshot(step, f"merge {best_pair} -> {new_tok_str}"),
            "winning_candidate": new_tok_str,
            "predicted_score_impact": new_m["score"] - old_metrics["score"],
            "actual_score_impact": new_m["score"] - old_metrics["score"],
        })

        if tok.vocab_size >= vocab_size:
            break

    # Fill remaining budget with Indic-weighted vanilla merges if under budget
    if tok.vocab_size < vocab_size:
        indic_weights: Counter[tuple[str, str]] = Counter()
        base = BPETokenizer(pretokenization="whitespace")
        for lang in ("hi", "te", "bn"):
            for pt in base.pretokenize(corpora[lang]):
                syms = base._word_to_symbols(pt)
                for i in range(len(syms) - 1):
                    indic_weights[(syms[i], syms[i + 1])] += 3
        extra = BPETokenizer.train(
            pooled,
            vocab_size,
            pretokenization="whitespace",
            seed_merges=tok.merges,
            pair_weights=indic_weights,
        )
        tok = extra
        trace.append(snapshot(step, "indic_weighted_fill"))

    fert = _fertilities(tok, corpora)
    result = StrategyResult(
        name="score_directed_adaptive",
        tokenizer=tok,
        fertilities=fert,
        metrics=compute_score(fert),
        vocab_allocation={"shared": max(0, tok.vocab_size - 7500), "en": min(7500, tok.vocab_size), "hi": 0, "te": 0, "bn": 0},
    )
    trace.append(snapshot(step, "final"))
    return result, trace, rejected


STRATEGIES: dict[str, Callable[..., StrategyResult]] = {
    "shared_vanilla": train_shared_vanilla,
    "allocated_monolingual": train_allocated_monolingual,
    "weighted_shared": train_weighted_shared,
    "grapheme_aware": train_grapheme_aware,
}
