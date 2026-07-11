"""BPE tokenizer — train, encode, export."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import regex as rx

from samabpe.unicode_utils import grapheme_clusters
from samabpe.word_units import normalize_nfc

PretokenMode = Literal["whitespace", "character", "grapheme"]
END_OF_WORD = "</w>"


@dataclass
class BPETokenizer:
    vocab: dict[str, int] = field(default_factory=dict)
    merges: list[tuple[str, str]] = field(default_factory=list)
    pretokenization: PretokenMode = "whitespace"
    special_tokens: dict[str, int] = field(default_factory=lambda: {"<unk>": 0, "<pad>": 1})
    _merge_ranks: dict[tuple[str, str], int] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._rebuild_merge_ranks()

    def _rebuild_merge_ranks(self) -> None:
        self._merge_ranks = {pair: i for i, pair in enumerate(self.merges)}

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def pretokenize(self, text: str) -> list[str]:
        text = normalize_nfc(text)
        if self.pretokenization == "whitespace":
            return [w + END_OF_WORD for w in text.split() if w]
        if self.pretokenization == "character":
            return list(text)
        if self.pretokenization == "grapheme":
            return grapheme_clusters(text)
        raise ValueError(f"Unknown pretokenization: {self.pretokenization}")

    def _word_to_symbols(self, word: str) -> list[str]:
        if self.pretokenization == "whitespace":
            # word already has </w> suffix from pretokenize
            if word.endswith(END_OF_WORD):
                core = word[: -len(END_OF_WORD)]
                return list(core) + [END_OF_WORD]
            return list(word)
        return list(word)

    def _apply_merges_to_word(self, symbols: list[str]) -> list[str]:
        pairs = self._get_pairs(symbols)
        while True:
            if not pairs:
                break
            bigram = min(pairs, key=lambda p: self._merge_ranks.get(p, float("inf")))
            if bigram not in self._merge_ranks:
                break
            symbols = self._merge_pair(symbols, bigram)
            pairs = self._get_pairs(symbols)
        return symbols

    @staticmethod
    def _get_pairs(symbols: list[str]) -> set[tuple[str, str]]:
        return {(symbols[i], symbols[i + 1]) for i in range(len(symbols) - 1)}

    @staticmethod
    def _merge_pair(symbols: list[str], pair: tuple[str, str]) -> list[str]:
        first, second = pair
        merged: list[str] = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == first and symbols[i + 1] == second:
                merged.append(first + second)
                i += 2
            else:
                merged.append(symbols[i])
                i += 1
        return merged

    def encode_word(self, word: str) -> list[str]:
        symbols = self._word_to_symbols(word)
        return self._apply_merges_to_word(symbols)

    def encode(self, text: str) -> list[str]:
        pretokens = self.pretokenize(text)
        out: list[str] = []
        for pt in pretokens:
            out.extend(self.encode_word(pt))
        return out

    def encode_ids(self, text: str) -> list[int]:
        unk = self.special_tokens.get("<unk>", 0)
        return [self.vocab.get(t, unk) for t in self.encode(text)]

    def decode(self, tokens: list[str]) -> str:
        if self.pretokenization == "whitespace":
            text = "".join(tokens)
            return text.replace(END_OF_WORD, " ").strip()
        return "".join(tokens)

    def count_tokens(self, text: str) -> int:
        return len(self.encode(text))

    @classmethod
    def train(
        cls,
        corpus: str,
        vocab_size: int,
        pretokenization: PretokenMode = "whitespace",
        special_tokens: dict[str, int] | None = None,
        pair_weights: Counter[tuple[str, str]] | None = None,
        seed_merges: list[tuple[str, str]] | None = None,
    ) -> "BPETokenizer":
        special = special_tokens or {"<unk>": 0, "<pad>": 1}
        tok = cls(pretokenization=pretokenization, special_tokens=dict(special))
        tok.vocab = dict(special)

        # Build initial symbol frequencies per pretoken
        word_freqs: Counter[str] = Counter()
        for pt in tok.pretokenize(corpus):
            word_freqs[pt] += 1

        splits: dict[str, list[str]] = {}
        for word, freq in word_freqs.items():
            splits[word] = tok._word_to_symbols(word)
            for sym in splits[word]:
                if sym not in tok.vocab:
                    tok.vocab[sym] = len(tok.vocab)

        merges: list[tuple[str, str]] = list(seed_merges or [])
        tok.merges = merges
        tok._rebuild_merge_ranks()

        # Apply seed merges to splits
        for word in splits:
            splits[word] = tok._apply_merges_to_word(splits[word])

        target = vocab_size
        while len(tok.vocab) < target:
            pair_counts: Counter[tuple[str, str]] = Counter()
            for word, freq in word_freqs.items():
                symbols = splits[word]
                for i in range(len(symbols) - 1):
                    pair = (symbols[i], symbols[i + 1])
                    w = pair_weights.get(pair, 1) if pair_weights else 1
                    pair_counts[pair] += freq * w

            if not pair_counts:
                break

            best = max(pair_counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
            if pair_counts[best] <= 0:
                break

            new_token = best[0] + best[1]
            if new_token in tok.vocab and best in tok._merge_ranks:
                break

            merges.append(best)
            tok.merges = merges
            tok._rebuild_merge_ranks()
            if new_token not in tok.vocab:
                tok.vocab[new_token] = len(tok.vocab)

            for word in splits:
                splits[word] = tok._merge_pair(splits[word], best)

            if len(tok.vocab) >= target:
                break

        return tok

    def to_dict(self) -> dict:
        return {
            "version": "1.0",
            "pretokenization": self.pretokenization,
            "special_tokens": self.special_tokens,
            "vocab": self.vocab,
            "merges": [list(m) for m in self.merges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BPETokenizer":
        tok = cls(
            vocab={k: int(v) for k, v in data["vocab"].items()},
            merges=[tuple(m) for m in data["merges"]],
            pretokenization=data.get("pretokenization", "whitespace"),
            special_tokens={k: int(v) for k, v in data.get("special_tokens", {}).items()},
        )
        return tok

    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> "BPETokenizer":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def export_vocab_txt(self, path: Path | str) -> None:
        inv = sorted(self.vocab.items(), key=lambda kv: kv[1])
        Path(path).write_text("\n".join(t for t, _ in inv) + "\n", encoding="utf-8")

    def export_merges_txt(self, path: Path | str) -> None:
        lines = [f"{a} {b}" for a, b in self.merges]
        Path(path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def export_vocab_json(self, path: Path | str) -> None:
        Path(path).write_text(
            json.dumps(self.vocab, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def merge_ancestry(self, token: str) -> list[tuple[str, str]]:
        """Greedy decomposition using merge list (approximate)."""
        if len(token) <= 1:
            return []
        ancestry: list[tuple[str, str]] = []
        for pair in reversed(self.merges):
            a, b = pair
            merged = a + b
            if merged in token:
                ancestry.append(pair)
        return ancestry
