"""Train standard Hugging Face BPE tokenizers under the evaluator contract."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from tokenizers import Regex, Tokenizer, models, normalizers, pre_tokenizers, trainers
from tokenizers.normalizers import Replace

from samabpe.evaluator_contract import LANGS, count_wordish_units
from samabpe.evaluator_contract import compute_evaluator_metrics

VOCAB_BUDGET = 10_000
DEFAULT_WEIGHTS = {"en": 3, "hi": 4, "te": 4, "bn": 2}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_hf_bpe_template() -> Tokenizer:
    tok = Tokenizer(models.BPE(unk_token="<unk>"))
    tok.normalizer = normalizers.Sequence(
        [
            normalizers.NFKC(),
            Replace(Regex(r"[^\p{L}\p{M}\p{N}]+"), " "),
        ]
    )
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    return tok


def _weighted_lines(corpora: dict[str, str], weights: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for lang in LANGS:
        w = max(1, int(weights.get(lang, 1)))
        corpus_lines = [ln for ln in corpora[lang].splitlines() if ln.strip()] or [corpora[lang]]
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
) -> tuple[Tokenizer, dict]:
    weights = dict(weights or DEFAULT_WEIGHTS)
    tok = build_hf_bpe_template()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=1,
        special_tokens=["<unk>", "<pad>"],
        show_progress=False,
    )
    lines = _weighted_lines(corpora, weights)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
        for line in lines:
            f.write(line + "\n")
        train_path = f.name
    try:
        tok.train([train_path], trainer)
    finally:
        Path(train_path).unlink(missing_ok=True)
    meta = {
        "weights": weights,
        "vocab_size": tok.get_vocab_size(with_added_tokens=True),
        "training_lines": len(lines),
    }
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tok.save(str(path))
        meta["tokenizer_sha256"] = sha256_file(path)
    return tok, meta


def load_faithful_corpora(corpus_dir: Path | str) -> dict[str, str]:
    corpus_dir = Path(corpus_dir)
    out: dict[str, str] = {}
    for lang in LANGS:
        p = corpus_dir / f"{lang}.faithful.md"
        if not p.exists():
            raise FileNotFoundError(p)
        out[lang] = p.read_text(encoding="utf-8")
    return out


def evaluate_tokenizer(tok: Tokenizer, corpora: dict[str, str]) -> dict:
    token_counts = {lang: len(tok.encode(corpora[lang]).ids) for lang in LANGS}
    wordish_counts = {lang: count_wordish_units(corpora[lang]) for lang in LANGS}
    m = compute_evaluator_metrics(token_counts, wordish_counts)
    return m.to_dict()
