"""Consumption ledger — tracks every shard/batch consumed during training."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ledger.event_store import EventStore
from storage.hash_utils import sha256_json


class ConsumptionLedger:
    """Append-only ledger of data consumption events."""

    def __init__(self, path: Path) -> None:
        self.store = EventStore(path)

    def record(
        self,
        *,
        shard_id: str,
        batch_id: str,
        microbatch_idx: int,
        global_batch_idx: int,
        checkpoint_id: str | None,
        gpu_rank: int,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "shard_id": shard_id,
            "batch_id": batch_id,
            "microbatch_idx": microbatch_idx,
            "global_batch_idx": global_batch_idx,
            "checkpoint_id": checkpoint_id,
            "gpu_rank": gpu_rank,
        }
        if extra:
            payload.update(extra)
        payload["content_hash"] = sha256_json(payload)
        return self.store.append("consumption", payload)

    @property
    def offset(self) -> int:
        return self.store.count()

    def read_all(self) -> list[dict[str, Any]]:
        return self.store.read_all()

    def read_from(self, offset: int) -> list[dict[str, Any]]:
        return list(self.store.read_from(offset))

    def get_batch_ids(self) -> list[str]:
        seen: list[str] = []
        for event in self.read_all():
            bid = event["payload"]["batch_id"]
            if bid not in seen:
                seen.append(bid)
        return seen
