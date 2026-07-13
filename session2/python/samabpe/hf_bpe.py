"""Hugging Face tokenizers BPE training and evaluation."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Iterable

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers
from tokenizers.normalizers import Replace

from samabpe.evaluator_scoring import LANGS, EvaluatorMetrics, compute_evaluator_metrics
from samabpe.evaluator_text import NON_WORDISH_PATTERN, count_wordish_units

VOCAB_BUDGET = 10_000
DEFAULT_WEIGHTS = {"en": 3, "hi": 4, "te": 4, "bn": 2}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_bpe_tokenizer() -> Tokenizer:
    """Reference-compatible BPE template: NFKC + non-L/M/N → space, whitespace pretokenizer."""
    tok = Tokenizer(models.BPE(unk_token="<unk>"))
    tok.normalizer = normalizers.Sequence(
        [
            normalizers.NFKC(),
            Replace(NON_WORDISH_PATTERN, " "),
        ]
    )
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    return tok


def _weighted_corpus_lines(corpora: dict[str, str], weights: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for lang in LANGS:
        text = corpora[lang]
        w = max(1, int(weights.get(lang, 1)))
        corpus_lines = [ln for ln in text.splitlines() if ln.strip()]
        if not corpus_lines:
            corpus_lines = [text]
        for ln in corpus_lines:
            for _ in range(w):
                lines.append(ln)
    return lines


def train_hf_bpe(
    corpora: dict[str, str],
    *,
    weights: dict[str, int] | None = None,
    vocab_size: int = VOCAB_BUDGET,
    output_path: Path | str | None = None,
) -> Tokenizer:
    weights = weights or dict(DEFAULT_WEIGHTS)
    tok = build_bpe_tokenizer()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=1,
        special_tokens=["<unk>", "<pad>"],
        show_progress=False,
    )
    lines = _weighted_corpus_lines(corpora, weights)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
        for line in lines:
            f.write(line)
            f.write("\n")
        train_path = f.name
    try:
        tok.train([train_path], trainer)
    finally:
        Path(train_path).unlink(missing_ok=True)
    if output_path is not None:
        tok.save(str(output_path))
    return tok


def count_tokens_hf(tok: Tokenizer, text: str) -> int:
    return len(tok.encode(text).ids)


def evaluate_hf_tokenizer(tok: Tokenizer, corpora: dict[str, str]) -> EvaluatorMetrics:
    token_counts = {lang: count_tokens_hf(tok, corpora[lang]) for lang in LANGS}
    wordish_counts = {lang: count_wordish_units(corpora[lang]) for lang in LANGS}
    return compute_evaluator_metrics(token_counts, wordish_counts)


def load_faithful_corpora(corpus_dir: Path | str) -> dict[str, str]:
    corpus_dir = Path(corpus_dir)
    out: dict[str, str] = {}
    for lang in LANGS:
        md_path = corpus_dir / f"{lang}.faithful.md"
        if not md_path.exists():
            raise FileNotFoundError(f"Missing corpus: {md_path}")
        out[lang] = md_path.read_text(encoding="utf-8")
    return out
