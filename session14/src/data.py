"""Tiny deterministic corpus with fixed train / held-out eval split."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple

import torch

SENTENCES = [
    "I like cats and dogs", "cats like milk", "dogs like bones",
    "I like dogs and cats", "milk is good for cats", "bones are good for dogs",
    "I have a cat", "I have a dog", "the cat likes milk", "the dog likes bones",
    "cats and dogs are friends", "I like my cat", "I like my dog",
    "my cat is small", "my dog is big", "small cats like milk",
    "big dogs like bones", "I feed my cat milk", "I feed my dog bones",
    "cats sleep a lot", "dogs run fast", "fast dogs like bones",
    "sleepy cats like milk", "I pet my cat", "I pet my dog",
    "my cat and my dog play", "play is fun for cats", "play is fun for dogs",
    "fun cats like milk", "fun dogs like bones", "I love cats", "I love dogs",
]

ROUTER_INIT_NOTE = (
    "Router logits are zero-initialized, producing uniform router probabilities at "
    "conversion; deterministic Top-K tie-breaking initially routes traffic to the "
    "same experts."
)


@dataclass
class TinyCorpus:
    sentences: List[str] | None = None

    def __post_init__(self) -> None:
        if self.sentences is None:
            self.sentences = list(SENTENCES)
        words = set()
        for s in self.sentences:
            words.update(s.split())
        self.itos = ["<pad>", "<unk>"] + sorted(words)
        self.stoi = {w: i for i, w in enumerate(self.itos)}
        self.vocab_size = len(self.itos)
        self.encoded = [self.encode(s) for s in self.sentences]

    def encode(self, text: str) -> List[int]:
        return [self.stoi.get(w, 1) for w in text.split()]


@dataclass
class CorpusSplit:
    train: TinyCorpus
    eval: TinyCorpus
    train_size: int
    eval_size: int
    train_sentence_indices: list[int]
    eval_sentence_indices: list[int]


def build_corpus_split(seed: int, train_frac: float = 0.8) -> CorpusSplit:
    """Deterministic 80/20 split; vocabulary built from all sentences."""
    n = len(SENTENCES)
    perm = list(range(n))
    random.Random(seed).shuffle(perm)
    k = max(1, int(n * train_frac))
    train_ids = sorted(perm[:k])
    eval_ids = sorted(perm[k:])
    if not eval_ids:
        eval_ids = [train_ids.pop()]

    master = TinyCorpus()
    train = TinyCorpus(sentences=[SENTENCES[i] for i in train_ids])
    eval_corpus = TinyCorpus(sentences=[SENTENCES[i] for i in eval_ids])
    for part in (train, eval_corpus):
        part.itos = master.itos
        part.stoi = master.stoi
        part.vocab_size = master.vocab_size
        part.encoded = [part.encode(s) for s in part.sentences]

    return CorpusSplit(
        train=train,
        eval=eval_corpus,
        train_size=len(train.sentences),
        eval_size=len(eval_corpus.sentences),
        train_sentence_indices=train_ids,
        eval_sentence_indices=eval_ids,
    )


def _batch_from_corpus(
    corpus: TinyCorpus, batch_size: int, block_size: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    xs, ys = [], []
    for _ in range(batch_size):
        row = corpus.encoded[int(torch.randint(len(corpus.encoded), (1,), generator=g))]
        if len(row) < block_size:
            row = row + [0] * (block_size - len(row))
        else:
            row = row[:block_size]
        xs.append(row)
        ys.append(row)
    return (
        torch.tensor(xs, dtype=torch.long),
        torch.tensor(ys, dtype=torch.long),
    )


def make_train_batch(
    split: CorpusSplit, batch_size: int, block_size: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor]:
    return _batch_from_corpus(split.train, batch_size, block_size, seed)


def make_eval_batch(
    split: CorpusSplit, batch_size: int, block_size: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor]:
    return _batch_from_corpus(split.eval, batch_size, block_size, seed)


# ponytail: legacy alias for tests that pass a TinyCorpus directly
def make_batch(
    corpus: TinyCorpus, batch_size: int, block_size: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor]:
    return _batch_from_corpus(corpus, batch_size, block_size, seed)
