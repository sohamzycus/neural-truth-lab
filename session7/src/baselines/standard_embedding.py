"""Conventional token embedding baseline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StandardEmbedding:
    vocab: dict[str, int] = field(default_factory=dict)
    dim: int = 64

    def build_vocab(self, strings: list[str]) -> None:
        for s in strings:
            if s not in self.vocab:
                self.vocab[s] = len(self.vocab)

    @property
    def trainable_parameters(self) -> int:
        return len(self.vocab) * self.dim

    def encode_id(self, text: str) -> int:
        return self.vocab.get(text, 0)

    def can_reconstruct_without_table(self) -> bool:
        return False
