"""Frozen deterministic tokenizer engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from storage.hash_utils import sha256_json, sha256_text


SPECIAL_TOKENS = ["<pad>", "<unk>", "<bos>", "<eos>"]


@dataclass
class FrozenTokenizer:
    """Word-level tokenizer. Once frozen, vocabulary is immutable."""

    vocab: dict[str, int] = field(default_factory=dict)
    frozen: bool = False
    tokenizer_hash: str = ""

    def build_vocab(self, documents: list[dict[str, Any]]) -> None:
        if self.frozen:
            raise RuntimeError("Cannot modify frozen tokenizer")
        self.vocab = {tok: i for i, tok in enumerate(SPECIAL_TOKENS)}
        for doc in documents:
            for word in doc["text"].lower().split():
                if word not in self.vocab:
                    self.vocab[word] = len(self.vocab)

    def freeze(self) -> str:
        if self.frozen:
            return self.tokenizer_hash
        self.frozen = True
        self.tokenizer_hash = sha256_json(
            {"vocab": self.vocab, "special_tokens": SPECIAL_TOKENS}
        )
        return self.tokenizer_hash

    def verify_frozen(self) -> bool:
        if not self.frozen:
            raise RuntimeError("Tokenizer not frozen")
        current = sha256_json({"vocab": self.vocab, "special_tokens": SPECIAL_TOKENS})
        if current != self.tokenizer_hash:
            raise ValueError(
                f"Tokenizer hash mismatch: expected {self.tokenizer_hash[:16]}… "
                f"got {current[:16]}…"
            )
        return True

    def encode(self, text: str) -> list[int]:
        if not self.frozen:
            raise RuntimeError("Tokenizer must be frozen before encoding")
        unk = self.vocab["<unk>"]
        bos = self.vocab["<bos>"]
        eos = self.vocab["<eos>"]
        tokens = [bos]
        for word in text.lower().split():
            tokens.append(self.vocab.get(word, unk))
        tokens.append(eos)
        return tokens

    def token_stream_hash(self, token_ids: list[int]) -> str:
        return sha256_json(token_ids)

    def document_hash(self, text: str) -> str:
        return sha256_text(text)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vocab": self.vocab,
            "frozen": self.frozen,
            "tokenizer_hash": self.tokenizer_hash,
            "special_tokens": SPECIAL_TOKENS,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FrozenTokenizer:
        tok = cls(vocab=data["vocab"], frozen=data["frozen"], tokenizer_hash=data["tokenizer_hash"])
        return tok

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> FrozenTokenizer:
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
