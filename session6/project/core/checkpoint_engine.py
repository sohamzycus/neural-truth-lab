"""Checkpoint engine — immutable training state snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from storage.hash_utils import sha256_json
from storage.immutable_store import ImmutableStore


class CheckpointEngine:
    """Saves and restores immutable training checkpoints."""

    def __init__(self, store: ImmutableStore, checkpoint_dir: Path) -> None:
        self.store = store
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints: list[dict[str, Any]] = []

    def save(
        self,
        *,
        model_state: dict[str, Any],
        optimizer_state: dict[str, Any],
        scheduler_state: dict[str, Any],
        ledger_offset: int,
        rng_state: list[int],
        current_batch: int,
        current_shard: str | None,
        curriculum_stage: str,
        tokenizer_hash: str,
        manifest_hash: str,
    ) -> dict[str, Any]:
        checkpoint = {
            "checkpoint_id": str(uuid4()),
            "model_state": model_state,
            "optimizer_state": optimizer_state,
            "scheduler_state": scheduler_state,
            "ledger_offset": ledger_offset,
            "rng_state": list(rng_state),
            "current_batch": current_batch,
            "current_shard": current_shard,
            "curriculum_stage": curriculum_stage,
            "tokenizer_hash": tokenizer_hash,
            "manifest_hash": manifest_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        checkpoint["checkpoint_hash"] = sha256_json(
            {k: v for k, v in checkpoint.items() if k != "checkpoint_hash"}
        )
        self.store.put_json(checkpoint)

        path = self.checkpoint_dir / f"{checkpoint['checkpoint_id']}.json"
        path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
        self.checkpoints.append(checkpoint)
        return checkpoint

    def load_latest(self) -> dict[str, Any] | None:
        if not self.checkpoints:
            return None
        return self.checkpoints[-1]

    def load_by_id(self, checkpoint_id: str) -> dict[str, Any]:
        for cp in self.checkpoints:
            if cp["checkpoint_id"] == checkpoint_id:
                return cp
        path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")

    def verify_checkpoint(self, checkpoint: dict[str, Any]) -> bool:
        expected = sha256_json(
            {k: v for k, v in checkpoint.items() if k != "checkpoint_hash"}
        )
        if expected != checkpoint["checkpoint_hash"]:
            raise ValueError("Checkpoint hash verification failed")
        return True
