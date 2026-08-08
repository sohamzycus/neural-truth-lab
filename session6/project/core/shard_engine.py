"""Immutable tokenized shard engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from storage.hash_utils import sha256_json
from storage.immutable_store import ImmutableStore


class ShardEngine:
    """Creates content-addressed immutable shards from tokenized documents."""

    def __init__(self, store: ImmutableStore) -> None:
        self.store = store
        self.shards: list[dict[str, Any]] = []

    def create_shard(
        self,
        *,
        token_ids: list[int],
        tokenizer_hash: str,
        source: str,
        document_ids: list[str],
        curriculum_stage: str,
        lane: str,
        capability: str,
        evaluation: bool = False,
        cleaning_version: str = "v1",
        dedup_status: str = "unique",
        parent_hash: str | None = None,
    ) -> dict[str, Any]:
        content_hash = sha256_json(token_ids)
        shard = {
            "shard_id": str(uuid4()),
            "content_hash": content_hash,
            "tokenizer_hash": tokenizer_hash,
            "source": source,
            "document_ids": document_ids,
            "curriculum_stage": curriculum_stage,
            "lane": lane,
            "capability": capability,
            "evaluation": evaluation,
            "cleaning_version": cleaning_version,
            "dedup_status": dedup_status,
            "parent_hash": parent_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token_ids": token_ids,
            "num_tokens": len(token_ids),
        }
        shard["shard_hash"] = sha256_json({k: v for k, v in shard.items() if k != "shard_hash"})
        self.store.put_json(shard)
        self.shards.append(shard)
        return shard

    def get_training_shards(self) -> list[dict[str, Any]]:
        return [s for s in self.shards if not s["evaluation"]]

    def get_eval_shards(self) -> list[dict[str, Any]]:
        return [s for s in self.shards if s["evaluation"]]

    def shard_by_lane(self, lane: str) -> list[dict[str, Any]]:
        return [s for s in self.shards if s["lane"] == lane]
