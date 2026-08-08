"""Batch engine — constructs training batches with eval firewall."""

from __future__ import annotations

from typing import Any

from core.packing_engine import PackedBatch, PackingPolicy
from storage.hash_utils import sha256_json


class EvalFirewallViolation(Exception):
    """Raised when an evaluation shard enters a loss-bearing batch."""


class BatchEngine:
    """Builds batches from shards with evaluation firewall enforcement."""

    def __init__(self, packing_policy: PackingPolicy) -> None:
        self.packing_policy = packing_policy
        self.batches: list[PackedBatch] = []
        self.eval_blocked_count = 0

    def create_batches(
        self,
        shards: list[dict[str, Any]],
        *,
        allow_eval: bool = False,
    ) -> list[PackedBatch]:
        if not allow_eval:
            eval_shards = [s for s in shards if s.get("evaluation")]
            if eval_shards:
                self.eval_blocked_count += len(eval_shards)
                shards = [s for s in shards if not s.get("evaluation")]

        packed = self.packing_policy.pack(shards)
        self.batches.extend(packed)
        return packed

    def verify_no_eval_in_batch(self, batch: PackedBatch, shard_lookup: dict[str, dict]) -> bool:
        for ref in batch.shard_map:
            shard = shard_lookup.get(ref["shard_id"])
            if shard and shard.get("evaluation"):
                raise EvalFirewallViolation(
                    f"Eval shard {ref['shard_id']} in loss-bearing batch {batch.batch_id}"
                )
        return True

    def batch_registry(self) -> dict[str, Any]:
        return {
            "batch_count": len(self.batches),
            "batch_hashes": [b.batch_hash for b in self.batches],
            "packing_policy": self.packing_policy.name,
            "eval_blocked_count": self.eval_blocked_count,
            "registry_hash": sha256_json([b.batch_hash for b in self.batches]),
        }

    def utilization_report(self) -> dict[str, Any]:
        if not self.batches:
            return {"avg_utilization": 0.0, "batches": 0}
        utils = [self.packing_policy.utilization(b) for b in self.batches]
        return {
            "avg_utilization": sum(utils) / len(utils),
            "min_utilization": min(utils),
            "max_utilization": max(utils),
            "batches": len(self.batches),
            "total_useful_tokens": sum(b.useful_tokens for b in self.batches),
            "total_padded_tokens": sum(b.padded_tokens for b in self.batches),
        }
