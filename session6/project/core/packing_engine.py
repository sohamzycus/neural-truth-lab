"""Pluggable packing policies for batch construction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from storage.hash_utils import sha256_json


@dataclass
class PackedBatch:
    batch_id: str
    token_ids: list[int]
    attention_mask: list[int]
    shard_map: list[dict[str, Any]]
    packing_policy: str
    max_seq_len: int
    useful_tokens: int
    padded_tokens: int
    batch_hash: str = ""

    def finalize(self) -> None:
        payload = {
            "batch_id": self.batch_id,
            "token_ids": self.token_ids,
            "attention_mask": self.attention_mask,
            "shard_map": self.shard_map,
            "packing_policy": self.packing_policy,
            "max_seq_len": self.max_seq_len,
            "useful_tokens": self.useful_tokens,
            "padded_tokens": self.padded_tokens,
        }
        self.batch_hash = sha256_json(payload)


class PackingPolicy(ABC):
    name: str = "base"

    def __init__(self, max_seq_len: int = 64) -> None:
        self.max_seq_len = max_seq_len

    @abstractmethod
    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        ...

    def utilization(self, batch: PackedBatch) -> float:
        total = batch.useful_tokens + batch.padded_tokens
        return batch.useful_tokens / total if total > 0 else 0.0


class PadOnlyPacking(PackingPolicy):
    name = "pad_only"

    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        batches: list[PackedBatch] = []
        for shard in shards:
            tokens = shard["token_ids"][: self.max_seq_len]
            pad_len = self.max_seq_len - len(tokens)
            padded = tokens + [0] * pad_len
            mask = [1] * len(tokens) + [0] * pad_len
            batch = PackedBatch(
                batch_id=str(uuid4()),
                token_ids=padded,
                attention_mask=mask,
                shard_map=[{"shard_id": shard["shard_id"], "offset": 0, "length": len(tokens)}],
                packing_policy=self.name,
                max_seq_len=self.max_seq_len,
                useful_tokens=len(tokens),
                padded_tokens=pad_len,
            )
            batch.finalize()
            batches.append(batch)
        return batches


class ConcatenatePacking(PackingPolicy):
    name = "concatenate"

    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        batches: list[PackedBatch] = []
        current_tokens: list[int] = []
        current_map: list[dict[str, Any]] = []
        for shard in shards:
            tokens = shard["token_ids"]
            if len(current_tokens) + len(tokens) > self.max_seq_len and current_tokens:
                batches.append(self._flush(current_tokens, current_map))
                current_tokens, current_map = [], []
            offset = 0
            remaining = self.max_seq_len - len(current_tokens)
            chunk = tokens[:remaining]
            current_tokens.extend(chunk)
            current_map.append(
                {"shard_id": shard["shard_id"], "offset": offset, "length": len(chunk)}
            )
            if len(current_tokens) >= self.max_seq_len:
                batches.append(self._flush(current_tokens, current_map))
                current_tokens, current_map = [], []
        if current_tokens:
            batches.append(self._flush(current_tokens, current_map))
        return batches

    def _flush(self, tokens: list[int], shard_map: list[dict[str, Any]]) -> PackedBatch:
        pad_len = self.max_seq_len - len(tokens)
        padded = tokens + [0] * pad_len
        mask = [1] * len(tokens) + [0] * pad_len
        batch = PackedBatch(
            batch_id=str(uuid4()),
            token_ids=padded,
            attention_mask=mask,
            shard_map=shard_map,
            packing_policy=self.name,
            max_seq_len=self.max_seq_len,
            useful_tokens=len(tokens),
            padded_tokens=pad_len,
        )
        batch.finalize()
        return batch


class GreedyPacking(PackingPolicy):
    name = "greedy"

    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        sorted_shards = sorted(shards, key=lambda s: s["num_tokens"], reverse=True)
        batches: list[PackedBatch] = []
        used: set[str] = set()
        while len(used) < len(sorted_shards):
            current_tokens: list[int] = []
            current_map: list[dict[str, Any]] = []
            for shard in sorted_shards:
                if shard["shard_id"] in used:
                    continue
                tokens = shard["token_ids"]
                if len(current_tokens) + len(tokens) <= self.max_seq_len:
                    current_map.append(
                        {
                            "shard_id": shard["shard_id"],
                            "offset": 0,
                            "length": len(tokens),
                        }
                    )
                    current_tokens.extend(tokens)
                    used.add(shard["shard_id"])
            if not current_tokens:
                shard = next(s for s in sorted_shards if s["shard_id"] not in used)
                tokens = shard["token_ids"][: self.max_seq_len]
                current_tokens = tokens
                current_map = [
                    {"shard_id": shard["shard_id"], "offset": 0, "length": len(tokens)}
                ]
                used.add(shard["shard_id"])
            pad_len = self.max_seq_len - len(current_tokens)
            padded = current_tokens + [0] * pad_len
            mask = [1] * len(current_tokens) + [0] * pad_len
            batch = PackedBatch(
                batch_id=str(uuid4()),
                token_ids=padded,
                attention_mask=mask,
                shard_map=current_map,
                packing_policy=self.name,
                max_seq_len=self.max_seq_len,
                useful_tokens=len(current_tokens),
                padded_tokens=pad_len,
            )
            batch.finalize()
            batches.append(batch)
        return batches


class BestFitPacking(PackingPolicy):
    name = "best_fit"

    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        remaining = list(shards)
        batches: list[PackedBatch] = []
        while remaining:
            best_idx = -1
            best_waste = self.max_seq_len + 1
            for i, shard in enumerate(remaining):
                waste = self.max_seq_len - shard["num_tokens"]
                if 0 <= waste < best_waste:
                    best_waste = waste
                    best_idx = i
            if best_idx < 0:
                shard = remaining.pop(0)
                tokens = shard["token_ids"][: self.max_seq_len]
            else:
                shard = remaining.pop(best_idx)
                tokens = shard["token_ids"]
            pad_len = self.max_seq_len - len(tokens)
            padded = tokens + [0] * pad_len
            mask = [1] * len(tokens) + [0] * pad_len
            batch = PackedBatch(
                batch_id=str(uuid4()),
                token_ids=padded,
                attention_mask=mask,
                shard_map=[{"shard_id": shard["shard_id"], "offset": 0, "length": len(tokens)}],
                packing_policy=self.name,
                max_seq_len=self.max_seq_len,
                useful_tokens=len(tokens),
                padded_tokens=pad_len,
            )
            batch.finalize()
            batches.append(batch)
        return batches


class StructurePreservingPacking(PackingPolicy):
    """Keeps document boundaries via <eos> separators."""

    name = "structure_preserving"

    def pack(self, shards: list[dict[str, Any]]) -> list[PackedBatch]:
        batches: list[PackedBatch] = []
        current_tokens: list[int] = []
        current_map: list[dict[str, Any]] = []
        eos_token = 3  # ponytail: fixed <eos> id from SPECIAL_TOKENS order
        for shard in shards:
            tokens = list(shard["token_ids"])
            sep_len = 1 if current_tokens else 0
            if len(current_tokens) + sep_len + len(tokens) > self.max_seq_len:
                if current_tokens:
                    batches.append(self._flush(current_tokens, current_map))
                    current_tokens, current_map = [], []
            if current_tokens:
                current_tokens.append(eos_token)
            offset = 0
            current_map.append(
                {"shard_id": shard["shard_id"], "offset": offset, "length": len(tokens)}
            )
            current_tokens.extend(tokens)
        if current_tokens:
            batches.append(self._flush(current_tokens, current_map))
        return batches

    def _flush(self, tokens: list[int], shard_map: list[dict[str, Any]]) -> PackedBatch:
        pad_len = self.max_seq_len - len(tokens)
        padded = tokens + [0] * pad_len
        mask = [1] * len(tokens) + [0] * pad_len
        batch = PackedBatch(
            batch_id=str(uuid4()),
            token_ids=padded,
            attention_mask=mask,
            shard_map=shard_map,
            packing_policy=self.name,
            max_seq_len=self.max_seq_len,
            useful_tokens=len(tokens),
            padded_tokens=pad_len,
        )
        batch.finalize()
        return batch


PACKING_POLICIES: dict[str, type[PackingPolicy]] = {
    "pad_only": PadOnlyPacking,
    "concatenate": ConcatenatePacking,
    "greedy": GreedyPacking,
    "best_fit": BestFitPacking,
    "structure_preserving": StructurePreservingPacking,
}


def get_packing_policy(name: str, max_seq_len: int = 64) -> PackingPolicy:
    if name not in PACKING_POLICIES:
        raise ValueError(f"Unknown packing policy: {name}")
    return PACKING_POLICIES[name](max_seq_len=max_seq_len)
