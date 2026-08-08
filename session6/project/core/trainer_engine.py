"""Trainer engine — orchestrates fake training with ledgers and checkpoints."""

from __future__ import annotations

import math
import time
from typing import Any

from core.batch_engine import BatchEngine
from core.checkpoint_engine import CheckpointEngine
from core.metrics_engine import MetricsCollector, Timer
from core.packing_engine import PackedBatch
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger
from models.tiny_model import TinyModel
from storage.hash_utils import sha256_json


class CrashSimulation(Exception):
    """Simulated crash for resume testing."""

    def __init__(self, batch_idx: int) -> None:
        self.batch_idx = batch_idx
        super().__init__(f"Simulated crash after batch {batch_idx}")


class TrainerEngine:
    """Fake trainer with forward, loss, checkpoint, and resume."""

    CRASH_AFTER_BATCH = 17

    def __init__(
        self,
        model: TinyModel,
        batch_engine: BatchEngine,
        consumption_ledger: ConsumptionLedger,
        learning_ledger: LearningLedger,
        checkpoint_engine: CheckpointEngine,
        metrics: MetricsCollector,
        *,
        curriculum_stage: str = "stage_a",
        tokenizer_hash: str = "",
        manifest_hash: str = "",
        gpu_rank: int = 0,
    ) -> None:
        self.model = model
        self.batch_engine = batch_engine
        self.consumption_ledger = consumption_ledger
        self.learning_ledger = learning_ledger
        self.checkpoint_engine = checkpoint_engine
        self.metrics = metrics
        self.curriculum_stage = curriculum_stage
        self.tokenizer_hash = tokenizer_hash
        self.manifest_hash = manifest_hash
        self.gpu_rank = gpu_rank

        self.current_batch_idx = 0
        self.rng_state = [42]
        self.batch_registry: dict[str, PackedBatch] = {}
        self.crashed = False
        self.resumed = False
        self.resume_batch_matched = False
        self.last_checkpoint: dict[str, Any] | None = None
        self.training_losses: list[float] = []

    def train_batches(
        self,
        batches: list[PackedBatch],
        *,
        start_from: int = 0,
        simulate_crash: bool = True,
        shard_lookup: dict[str, dict[str, Any]] | None = None,
        opus_decisions: dict[str, str] | None = None,
    ) -> int:
        shard_lookup = shard_lookup or {}
        opus_decisions = opus_decisions or {}

        for i, batch in enumerate(batches[start_from:], start=start_from):
            batch_start = time.perf_counter()
            self.batch_registry[batch.batch_id] = batch

            if shard_lookup:
                self.batch_engine.verify_no_eval_in_batch(batch, shard_lookup)

            loss = self.model.train_step(batch.token_ids, batch.attention_mask)
            self.training_losses.append(loss)

            mask_hash = sha256_json(batch.attention_mask)
            perplexity = math.exp(min(loss, 20.0))

            for j, ref in enumerate(batch.shard_map):
                shard_id = ref["shard_id"]
                self.consumption_ledger.record(
                    shard_id=shard_id,
                    batch_id=batch.batch_id,
                    microbatch_idx=j,
                    global_batch_idx=i,
                    checkpoint_id=(
                        self.last_checkpoint["checkpoint_id"] if self.last_checkpoint else None
                    ),
                    gpu_rank=self.gpu_rank,
                )

                span = (ref["offset"], ref["offset"] + ref["length"])
                self.learning_ledger.record(
                    batch_id=batch.batch_id,
                    sample_idx=j,
                    token_span=span,
                    loss=loss,
                    avg_loss=sum(self.training_losses) / len(self.training_losses),
                    perplexity=perplexity,
                    attention_mask_hash=mask_hash,
                    learning_confidence=min(1.0, 1.0 / (1.0 + loss)),
                    curriculum_stage=self.curriculum_stage,
                    opus_decision=opus_decisions.get(shard_id, "accept"),
                )

            self.current_batch_idx = i + 1
            self.metrics.record_batch_time(time.perf_counter() - batch_start)
            self.metrics.total_useful_tokens += batch.useful_tokens
            self.metrics.total_padded_tokens += batch.padded_tokens
            self.metrics.total_batches += 1

            if (i + 1) % 5 == 0 or (
                simulate_crash and (i + 1) == self.CRASH_AFTER_BATCH
            ):
                with Timer(self.metrics, "record_checkpoint_time"):
                    self.last_checkpoint = self.checkpoint_engine.save(
                        model_state=self.model.get_state(),
                        optimizer_state=self.model.get_optimizer_state(),
                        scheduler_state={"step": i + 1},
                        ledger_offset=self.consumption_ledger.offset,
                        rng_state=self.rng_state,
                        current_batch=i + 1,
                        current_shard=(
                            batch.shard_map[0]["shard_id"] if batch.shard_map else None
                        ),
                        curriculum_stage=self.curriculum_stage,
                        tokenizer_hash=self.tokenizer_hash,
                        manifest_hash=self.manifest_hash,
                    )

            if simulate_crash and (i + 1) == self.CRASH_AFTER_BATCH:
                self.crashed = True
                raise CrashSimulation(i + 1)

        return self.current_batch_idx

    def resume_from_checkpoint(
        self,
        checkpoint: dict[str, Any],
        batches: list[PackedBatch],
        **kwargs: Any,
    ) -> int:
        self.checkpoint_engine.verify_checkpoint(checkpoint)
        resume_start = time.perf_counter()

        self.model.load_state(checkpoint["model_state"])
        self.model.load_optimizer_state(checkpoint["optimizer_state"])
        self.rng_state = list(checkpoint["rng_state"])
        expected_next = checkpoint["current_batch"]
        self.resumed = True

        completed = self.train_batches(
            batches,
            start_from=expected_next,
            simulate_crash=False,
            **kwargs,
        )

        self.metrics.set_resume_time(time.perf_counter() - resume_start)
        self.resume_batch_matched = self.current_batch_idx > expected_next
        return completed

    def get_time_machine_state(self, ledger_offset: int) -> dict[str, Any]:
        consumption = self.consumption_ledger.read_all()
        learning = self.learning_ledger.read_all()

        cons_at = [e for e in consumption if e["offset"] <= ledger_offset]
        learn_at = [e for e in learning if e["offset"] <= ledger_offset]

        current_batch = cons_at[-1]["payload"]["global_batch_idx"] if cons_at else 0
        current_loss = learn_at[-1]["payload"]["loss"] if learn_at else 0.0
        current_perplexity = learn_at[-1]["payload"]["perplexity"] if learn_at else 0.0
        current_opus = learn_at[-1]["payload"]["opus_decision"] if learn_at else "none"

        cp = self.last_checkpoint
        return {
            "ledger_offset": ledger_offset,
            "current_batch": current_batch,
            "current_checkpoint": cp["checkpoint_id"] if cp else None,
            "current_curriculum": self.curriculum_stage,
            "current_mixture": self.curriculum_stage,
            "current_opus_decision": current_opus,
            "current_loss": current_loss,
            "current_perplexity": current_perplexity,
            "consumption_events": len(cons_at),
            "learning_events": len(learn_at),
        }
