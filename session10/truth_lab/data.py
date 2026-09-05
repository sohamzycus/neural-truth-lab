"""Tiny deterministic corpus for the Truth Lab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import torch


# ponytail: fixed sentences keep vocab small and decoding human-readable
SENTENCES = [
    "I like cats and dogs",
    "cats like milk",
    "dogs like bones",
    "I like dogs and cats",
    "milk is good for cats",
    "bones are good for dogs",
    "I have a cat",
    "I have a dog",
    "the cat likes milk",
    "the dog likes bones",
    "cats and dogs are friends",
    "I like my cat",
    "I like my dog",
    "my cat is small",
    "my dog is big",
    "small cats like milk",
    "big dogs like bones",
    "I feed my cat milk",
    "I feed my dog bones",
    "cats sleep a lot",
    "dogs run fast",
    "fast dogs like bones",
    "sleepy cats like milk",
    "I pet my cat",
    "I pet my dog",
    "my cat and my dog play",
    "play is fun for cats",
    "play is fun for dogs",
    "fun cats like milk",
    "fun dogs like bones",
    "I love cats",
    "I love dogs",
]


@dataclass
class TinyCorpus:
    """Word-level tokenizer over a fixed sentence list."""

    sentences: List[str] = None  # type: ignore[assignment]

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

    def decode(self, ids: List[int]) -> str:
        return " ".join(self.itos[i] for i in ids if i > 1)

    def decode_tensor(self, t: torch.Tensor) -> str:
        return self.decode(t.tolist())


def make_batch(
    corpus: TinyCorpus,
    batch_size: int,
    block_size: int,
    seed: int,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return input_ids, targets, and attention mask (1 = valid token)."""
    g = torch.Generator().manual_seed(seed)
    xs, ys, masks = [], [], []
    for _ in range(batch_size):
        row = corpus.encoded[int(torch.randint(len(corpus.encoded), (1,), generator=g))]
        # pad or truncate to block_size
        if len(row) < block_size:
            pad_id = 0
            valid = len(row)
            row = row + [pad_id] * (block_size - len(row))
            mask = [1] * valid + [0] * (block_size - valid)
        else:
            row = row[:block_size]
            mask = [1] * block_size
        xs.append(row)
        ys.append(row)  # next-token targets come from shift in loss
        masks.append(mask)
    x = torch.tensor(xs, dtype=torch.long)
    y = torch.tensor(ys, dtype=torch.long)
    m = torch.tensor(masks, dtype=torch.bool)
    return x, y, m


def make_variable_microbatches(
    corpus: TinyCorpus,
    block_size: int,
    seed: int,
    loss_tokens: Tuple[int, int] = (10, 100),
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Two microbatches with the requested number of loss-contributing tokens."""
    g = torch.Generator().manual_seed(seed)

    def _one(n_loss: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Need n_loss+1 content tokens so shift leaves n_loss supervised positions.
        input_valid = n_loss + 1
        actual_block = max(block_size, input_valid)
        pieces: List[int] = []
        while len(pieces) < input_valid:
            sent = corpus.encoded[int(torch.randint(len(corpus.encoded), (1,), generator=g))]
            pieces.extend(sent)
        pieces = pieces[:input_valid]
        pad = actual_block - len(pieces)
        ids = pieces + [0] * pad
        mask = [1] * input_valid + [0] * pad
        x = torch.tensor([ids], dtype=torch.long)
        y = x.clone()
        m = torch.tensor([mask], dtype=torch.bool)
        return x, y, m

    xa, ya, ma = _one(loss_tokens[0])
    xb, yb, mb = _one(loss_tokens[1])
    return xa, ya, ma, xb, yb, mb
