"""Train faithful Hugging Face BPE: NFKC + Metaspace + decoder."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.decoders import Metaspace as MetaspaceDecoder
from tokenizers.models import BPE
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Metaspace
from tokenizers.trainers import BpeTrainer

from samabpe.evaluator_contract import (
    LANGS,
    REVIEWER_SAMPLE,
    compute_evaluator_metrics,
    faithful_units,
    verify_roundtrip,
)

VOCAB_BUDGET = 10_000
DEFAULT_WEIGHTS = {"en": 3, "hi": 4, "te": 4, "bn": 2}
WINNER_WEIGHTS = {"en": 3, "hi": 5, "te": 9, "bn": 5}
UNK_TOKEN = "<unk>"
# ponytail: seed alphabet for visible punctuation absent from Wikipedia snapshots (prevents <unk> decode deletion)
VISIBLE_INITIAL_ALPHABET = list("«»@€£—…–'\".,;:!?()[]{}|/_\\#&%+=*`~")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_hf_bpe_template(*, hardened: bool = True) -> Tokenizer:
    tok = Tokenizer(BPE(unk_token=UNK_TOKEN, byte_fallback=hardened))
    tok.normalizer = NFKC()
    tok.pre_tokenizer = Metaspace(replacement="▁", prepend_scheme="never")
    tok.decoder = MetaspaceDecoder(replacement="▁", prepend_scheme="never")
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


def verify_tokenizer_roundtrip(tok: Tokenizer, corpora: dict[str, str]) -> dict:
    """Round-trip gate: reviewer sample + full corpora."""
    result = {
        "reviewer_sample": verify_roundtrip(tok, REVIEWER_SAMPLE),
        "full_corpus": {},
        "valid": True,
    }
    for lang in LANGS:
        ok = verify_roundtrip(tok, corpora[lang])
        result["full_corpus"][lang] = ok
        if not ok:
            result["valid"] = False
    if not result["reviewer_sample"]:
        result["valid"] = False
    return result


def train_hf_bpe(
    corpora: dict[str, str],
    *,
    weights: dict[str, int] | None = None,
    vocab_size: int = VOCAB_BUDGET,
    output_path: Path | str | None = None,
    hardened: bool = True,
) -> tuple[Tokenizer, dict]:
    weights = dict(weights or DEFAULT_WEIGHTS)
    tok = build_hf_bpe_template(hardened=hardened)
    trainer_kwargs: dict = {
        "vocab_size": vocab_size,
        "min_frequency": 1,
        "special_tokens": [UNK_TOKEN],
        "show_progress": False,
    }
    if hardened:
        trainer_kwargs["initial_alphabet"] = VISIBLE_INITIAL_ALPHABET
    trainer = BpeTrainer(**trainer_kwargs)
    lines = _weighted_lines(corpora, weights)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
        for line in lines:
            f.write(line + "\n")
        train_path = f.name
    try:
        tok.train([train_path], trainer)
    finally:
        Path(train_path).unlink(missing_ok=True)

    roundtrip = verify_tokenizer_roundtrip(tok, corpora)
    meta = {
        "weights": weights,
        "vocab_size": tok.get_vocab_size(with_added_tokens=True),
        "training_lines": len(lines),
        "tokenizer_engine": "huggingface-bpe",
        "normalizer": "NFKC",
        "pretokenizer": {"type": "Metaspace", "replacement": "▁", "prepend_scheme": "never"},
        "decoder": {"type": "Metaspace", "replacement": "▁", "prepend_scheme": "never"},
        "byte_fallback": hardened,
        "initial_alphabet_seeded": hardened,
        "roundtrip": roundtrip,
    }
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tok.save(str(path))
        meta["tokenizer_sha256"] = sha256_file(path)
    return tok, meta


def load_faithful_corpora(corpus_dir: Path | str, *, ext: str = ".faithful.txt") -> dict[str, str]:
    corpus_dir = Path(corpus_dir)
    out: dict[str, str] = {}
    for lang in LANGS:
        p = corpus_dir / f"{lang}{ext}"
        if not p.exists() and ext == ".faithful.txt":
            p = corpus_dir / f"{lang}.faithful.md"
        if not p.exists():
            raise FileNotFoundError(p)
        out[lang] = p.read_text(encoding="utf-8")
    return out


def evaluate_tokenizer(tok: Tokenizer, corpora: dict[str, str]) -> dict:
    if not verify_tokenizer_roundtrip(tok, corpora)["valid"]:
        raise ValueError("Tokenizer failed round-trip faithfulness gate")
    token_counts = {lang: len(tok.encode(corpora[lang]).ids) for lang in LANGS}
    unit_counts = {lang: faithful_units(corpora[lang]) for lang in LANGS}
    m = compute_evaluator_metrics(token_counts, unit_counts)
    return m.to_dict()
