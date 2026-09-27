"""Tiny deterministic corpus — reused from session10/truth_lab/data.py"""

from __future__ import annotations

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


def make_batch(
    corpus: TinyCorpus, batch_size: int, block_size: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    xs, ys, masks = [], [], []
    for _ in range(batch_size):
        row = corpus.encoded[int(torch.randint(len(corpus.encoded), (1,), generator=g))]
        if len(row) < block_size:
            valid = len(row)
            row = row + [0] * (block_size - len(row))
            mask = [1] * valid + [0] * (block_size - valid)
        else:
            row = row[:block_size]
            mask = [1] * block_size
        xs.append(row)
        ys.append(row)
        masks.append(mask)
    return (
        torch.tensor(xs, dtype=torch.long),
        torch.tensor(ys, dtype=torch.long),
        torch.tensor(masks, dtype=torch.bool),
    )
