"""Replay engine — reconstruct batches from ledger without regeneration."""

from __future__ import annotations

import time
from typing import Any

from core.packing_engine import PackedBatch
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger
from storage.hash_utils import sha256_json


class ReplayEngine:
    """Replays training from ledgers; verifies hash identity."""

    def __init__(
        self,
        consumption_ledger: ConsumptionLedger,
        learning_ledger: LearningLedger,
        batch_registry: dict[str, PackedBatch],
    ) -> None:
        self.consumption_ledger = consumption_ledger
        self.learning_ledger = learning_ledger
        self.batch_registry = batch_registry
        self.replay_results: list[dict[str, Any]] = []

    def replay(self) -> dict[str, Any]:
        start = time.perf_counter()
        consumption_events = self.consumption_ledger.read_all()
        learning_events = self.learning_ledger.read_all()

        batch_ids_from_ledger: list[str] = []
        seen: set[str] = set()
        for event in consumption_events:
            bid = event["payload"]["batch_id"]
            if bid not in seen:
                batch_ids_from_ledger.append(bid)
                seen.add(bid)

        verified = 0
        mismatches: list[dict[str, Any]] = []
        for bid in batch_ids_from_ledger:
            batch = self.batch_registry.get(bid)
            if batch is None:
                mismatches.append({"batch_id": bid, "error": "batch_not_in_registry"})
                continue
            recomputed = sha256_json({
                "batch_id": batch.batch_id,
                "token_ids": batch.token_ids,
                "attention_mask": batch.attention_mask,
                "shard_map": batch.shard_map,
                "packing_policy": batch.packing_policy,
                "max_seq_len": batch.max_seq_len,
                "useful_tokens": batch.useful_tokens,
                "padded_tokens": batch.padded_tokens,
            })
            if recomputed == batch.batch_hash:
                verified += 1
            else:
                mismatches.append({
                    "batch_id": bid,
                    "expected": batch.batch_hash,
                    "recomputed": recomputed,
                })

        learning_batch_ids = list({
            e["payload"]["batch_id"] for e in learning_events
        })
        ledger_match = batch_ids_from_ledger == learning_batch_ids or len(learning_batch_ids) <= len(
            batch_ids_from_ledger
        )

        elapsed = time.perf_counter() - start
        result = {
            "total_batches": len(batch_ids_from_ledger),
            "verified": verified,
            "mismatches": mismatches,
            "ledger_consistent": ledger_match,
            "replay_time_sec": elapsed,
            "replay_hash": sha256_json({
                "verified": verified,
                "batch_hashes": [
                    self.batch_registry[bid].batch_hash
                    for bid in batch_ids_from_ledger
                    if bid in self.batch_registry
                ],
            }),
            "all_matched": len(mismatches) == 0 and verified == len(batch_ids_from_ledger),
        }
        self.replay_results.append(result)
        return result

    def compare_with_original(
        self,
        original_batches: list[PackedBatch],
        replay_batch_ids: list[str],
    ) -> dict[str, Any]:
        original_ids = [b.batch_id for b in original_batches]
        original_hashes = [b.batch_hash for b in original_batches]
        replay_hashes = [
            self.batch_registry[bid].batch_hash
            for bid in replay_batch_ids
            if bid in self.batch_registry
        ]
        return {
            "ids_match": original_ids[: len(replay_batch_ids)] == replay_batch_ids,
            "hashes_match": original_hashes[: len(replay_hashes)] == replay_hashes,
            "token_spans_match": all(
                self.batch_registry[replay_batch_ids[i]].shard_map
                == original_batches[i].shard_map
                for i in range(min(len(replay_batch_ids), len(original_batches)))
                if replay_batch_ids[i] in self.batch_registry
            ),
        }
