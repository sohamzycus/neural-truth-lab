"""Fork engine — branch training from checkpoint with independent ledgers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.batch_engine import BatchEngine
from core.packing_engine import get_packing_policy
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger
from storage.hash_utils import sha256_json


class ForkEngine:
    """Creates independent training branches from checkpoints."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)
        self.forks: list[dict[str, Any]] = []

    def fork(
        self,
        *,
        parent_checkpoint: dict[str, Any],
        new_packing_policy: str,
        branch_name: str,
        shards: list[dict[str, Any]],
        max_seq_len: int = 64,
    ) -> dict[str, Any]:
        fork_id = str(uuid4())
        fork_dir = self.root_dir / "forks" / fork_id
        fork_dir.mkdir(parents=True, exist_ok=True)

        consumption = ConsumptionLedger(fork_dir / "consumption.jsonl")
        learning = LearningLedger(fork_dir / "learning.jsonl")

        policy = get_packing_policy(new_packing_policy, max_seq_len=max_seq_len)
        batch_engine = BatchEngine(policy)
        batches = batch_engine.create_batches(shards)

        fork_record = {
            "fork_id": fork_id,
            "branch_name": branch_name,
            "parent_checkpoint_id": parent_checkpoint["checkpoint_id"],
            "parent_checkpoint_hash": parent_checkpoint["checkpoint_hash"],
            "packing_policy": new_packing_policy,
            "ledger_offset_at_fork": parent_checkpoint["ledger_offset"],
            "batch_count": len(batches),
            "batch_hashes": [b.batch_hash for b in batches],
            "consumption_ledger_path": str(fork_dir / "consumption.jsonl"),
            "learning_ledger_path": str(fork_dir / "learning.jsonl"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        fork_record["fork_hash"] = sha256_json(
            {k: v for k, v in fork_record.items() if k != "fork_hash"}
        )
        self.forks.append(fork_record)

        fork_meta_path = fork_dir / "fork_meta.json"
        fork_meta_path.write_text(
            __import__("json").dumps(fork_record, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return {
            "fork_record": fork_record,
            "batch_engine": batch_engine,
            "consumption_ledger": consumption,
            "learning_ledger": learning,
            "batches": batches,
        }

    def verify_fork_integrity(self, fork_record: dict[str, Any], parent: dict[str, Any]) -> bool:
        if fork_record["parent_checkpoint_hash"] != parent["checkpoint_hash"]:
            raise ValueError("Fork parent checkpoint hash mismatch")
        if fork_record["ledger_offset_at_fork"] != parent["ledger_offset"]:
            raise ValueError("Fork ledger offset mismatch")
        return True
