"""Learning ledger — per-sample loss and curriculum attribution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ledger.event_store import EventStore
from storage.hash_utils import sha256_json


class LearningLedger:
    """Append-only ledger of learning outcomes per batch."""

    def __init__(self, path: Path) -> None:
        self.store = EventStore(path)

    def record(
        self,
        *,
        batch_id: str,
        sample_idx: int,
        token_span: tuple[int, int],
        loss: float,
        avg_loss: float,
        perplexity: float,
        attention_mask_hash: str,
        learning_confidence: float,
        curriculum_stage: str,
        opus_decision: str,
    ) -> dict[str, Any]:
        payload = {
            "batch_id": batch_id,
            "sample_idx": sample_idx,
            "token_span": list(token_span),
            "loss": loss,
            "avg_loss": avg_loss,
            "perplexity": perplexity,
            "attention_mask_hash": attention_mask_hash,
            "learning_confidence": learning_confidence,
            "curriculum_stage": curriculum_stage,
            "opus_decision": opus_decision,
        }
        payload["content_hash"] = sha256_json(payload)
        return self.store.append("learning", payload)

    @property
    def offset(self) -> int:
        return self.store.count()

    def read_all(self) -> list[dict[str, Any]]:
        return self.store.read_all()

    def read_from(self, offset: int) -> list[dict[str, Any]]:
        return list(self.store.read_from(offset))
