"""Evidence builder — proves what was consumed, why, what was learned, and how to reconstruct."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from core.packing_engine import PackedBatch
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger
from storage.hash_utils import sha256_json


def reconstruct_metrics_from_batches(
    batch_registry: dict[str, PackedBatch],
    batch_ids_in_order: list[str],
) -> dict[str, Any]:
    """Recompute throughput/packing numbers from batch registry (not hardcoded)."""
    useful = 0
    padded = 0
    for bid in batch_ids_in_order:
        batch = batch_registry.get(bid)
        if batch:
            useful += batch.useful_tokens
            padded += batch.padded_tokens
    total = useful + padded
    return {
        "total_batches": len(batch_ids_in_order),
        "total_useful_tokens": useful,
        "total_padded_tokens": padded,
        "packing_utilization_pct": round(useful / total * 100, 2) if total else 0.0,
    }


def verify_consumption_ledger(ledger: ConsumptionLedger) -> dict[str, Any]:
    """Verify no skipped or duplicated global batches in consumption ledger."""
    events = ledger.read_all()
    by_global: dict[int, set[str]] = defaultdict(set)
    for event in events:
        payload = event["payload"]
        by_global[payload["global_batch_idx"]].add(payload["batch_id"])

    duplicate_indices = [idx for idx, bids in by_global.items() if len(bids) > 1]
    if by_global:
        max_idx = max(by_global)
        expected = set(range(max_idx + 1))
        missing = sorted(expected - set(by_global))
    else:
        missing = []

    batch_ids_ordered: list[str] = []
    seen: set[str] = set()
    for event in events:
        bid = event["payload"]["batch_id"]
        if bid not in seen:
            batch_ids_ordered.append(bid)
            seen.add(bid)

    return {
        "event_count": len(events),
        "unique_batches": len(batch_ids_ordered),
        "global_batch_indices": sorted(by_global),
        "no_duplicate_global_batches": len(duplicate_indices) == 0,
        "no_missing_global_batches": len(missing) == 0,
        "missing_indices": missing,
        "duplicate_indices": duplicate_indices,
        "batch_ids_in_order": batch_ids_ordered,
        "ledger_hash": sha256_json([e["hash"] for e in events]),
    }


def summarize_learning(ledger: LearningLedger) -> dict[str, Any]:
    """What the model learned — per-batch loss, perplexity, OPUS attribution."""
    events = ledger.read_all()
    if not events:
        return {"event_count": 0, "samples": []}

    by_batch: dict[str, dict[str, Any]] = {}
    for event in events:
        p = event["payload"]
        bid = p["batch_id"]
        if bid not in by_batch:
            by_batch[bid] = {
                "batch_id": bid,
                "loss": p["loss"],
                "perplexity": p["perplexity"],
                "avg_loss": p["avg_loss"],
                "curriculum_stage": p["curriculum_stage"],
                "opus_decisions": [],
                "token_spans": [],
                "attention_mask_hash": p["attention_mask_hash"],
            }
        by_batch[bid]["opus_decisions"].append(p["opus_decision"])
        by_batch[bid]["token_spans"].append(p["token_span"])

    samples = list(by_batch.values())
    final = events[-1]["payload"]
    return {
        "event_count": len(events),
        "unique_batches": len(by_batch),
        "final_loss": final["loss"],
        "final_perplexity": final["perplexity"],
        "curriculum_stages_seen": sorted({p["curriculum_stage"] for p in (e["payload"] for e in events)}),
        "opus_decision_counts": dict(Counter(e["payload"]["opus_decision"] for e in events)),
        "samples": samples[:5],
        "ledger_hash": sha256_json([e["hash"] for e in events]),
    }


def summarize_consumption(ledger: ConsumptionLedger) -> dict[str, Any]:
    """What was consumed — shard and batch attribution."""
    events = ledger.read_all()
    shard_counts: Counter[str] = Counter()
    checkpoint_ids: set[str] = set()
    for event in events:
        p = event["payload"]
        shard_counts[p["shard_id"]] += 1
        if p.get("checkpoint_id"):
            checkpoint_ids.add(p["checkpoint_id"])

    return {
        "event_count": len(events),
        "unique_shards_consumed": len(shard_counts),
        "shard_consumption_counts": dict(shard_counts.most_common(10)),
        "checkpoint_ids_referenced": sorted(checkpoint_ids),
        "ledger_hash": sha256_json([e["hash"] for e in events]),
    }


def summarize_opus(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    """Why shards were admitted or rejected."""
    counts = Counter(d["decision"] for d in decisions)
    return {
        "total_decisions": len(decisions),
        "decision_counts": dict(counts),
        "decisions": [
            {
                "shard_id": d["shard_id"],
                "lane": d["lane"],
                "decision": d["decision"],
                "reason": d["reason"],
                "quality": d["quality"],
                "novelty": d["novelty"],
                "difficulty": d["difficulty"],
                "evaluation": d.get("evaluation", False),
            }
            for d in decisions
        ],
        "decisions_hash": sha256_json(decisions),
    }


def build_reconstruction_guide(
    *,
    tokenizer_hash: str,
    manifest_hash: str,
    mixture: dict[str, Any],
    consumption_verify: dict[str, Any],
    checkpoint: dict[str, Any] | None,
    fork_record: dict[str, Any] | None,
    artifacts_dir: Path,
) -> dict[str, Any]:
    """How to reconstruct the run from immutable artifacts."""
    return {
        "steps": [
            "Load tokenizer and verify hash",
            "Load manifest and verify manifest_hash",
            "Read consumption ledger — batch_ids_in_order defines training sequence",
            "Read learning ledger — loss/perplexity per batch with OPUS attribution",
            "Load checkpoint at crash point — resume from current_batch offset",
            "Replay: recompute batch hashes from registry without regeneration",
        ],
        "tokenizer_hash": tokenizer_hash,
        "manifest_hash": manifest_hash,
        "mixture_hash": mixture.get("mixture_hash"),
        "consumption_ledger_path": str(artifacts_dir / "ledgers" / "consumption.jsonl"),
        "learning_ledger_path": str(artifacts_dir / "ledgers" / "learning.jsonl"),
        "manifest_path": str(artifacts_dir / "manifests" / "primary_manifest.json"),
        "checkpoint_at_crash": checkpoint["checkpoint_id"] if checkpoint else None,
        "resume_from_batch": checkpoint["current_batch"] if checkpoint else None,
        "ledger_offset_at_crash": checkpoint["ledger_offset"] if checkpoint else None,
        "fork_id": fork_record["fork_id"] if fork_record else None,
        "batch_sequence_verified": consumption_verify["no_duplicate_global_batches"]
        and consumption_verify["no_missing_global_batches"],
    }


def verify_metrics_claims(
    reported: dict[str, Any],
    recomputed: dict[str, Any],
) -> dict[str, Any]:
    """Prove packing/throughput numbers are reconstructable from batches."""
    checks = {
        "useful_tokens_match": reported["total_useful_tokens"] == recomputed["total_useful_tokens"],
        "padded_tokens_match": reported["total_padded_tokens"] == recomputed["total_padded_tokens"],
        "batch_count_match": reported["total_batches"] == recomputed["total_batches"],
        "packing_pct_match": reported["packing_utilization_pct"] == recomputed["packing_utilization_pct"],
    }
    return {
        "reported": reported,
        "recomputed_from_batches": recomputed,
        "all_match": all(checks.values()),
        "checks": checks,
    }


def build_full_evidence(
    *,
    audit_report: dict[str, Any],
    metrics: dict[str, Any],
    replay_result: dict[str, Any],
    tokenizer_hash: str,
    manifest_hash: str,
    mixture: dict[str, Any],
    opus_decisions: list[dict[str, Any]],
    consumption: ConsumptionLedger,
    learning: LearningLedger,
    batch_registry: dict[str, PackedBatch],
    checkpoint: dict[str, Any] | None,
    fork_record: dict[str, Any] | None,
    artifacts_dir: Path,
    packing_report: dict[str, Any],
) -> dict[str, Any]:
    """Full evidence bundle for evaluator Step 2."""
    consumption_summary = summarize_consumption(consumption)
    consumption_verify = verify_consumption_ledger(consumption)
    learning_summary = summarize_learning(learning)
    opus_summary = summarize_opus(opus_decisions)

    recomputed = reconstruct_metrics_from_batches(
        batch_registry, consumption_verify["batch_ids_in_order"]
    )
    metrics_verification = verify_metrics_claims(metrics, recomputed)

    reconstruction = build_reconstruction_guide(
        tokenizer_hash=tokenizer_hash,
        manifest_hash=manifest_hash,
        mixture=mixture,
        consumption_verify=consumption_verify,
        checkpoint=checkpoint,
        fork_record=fork_record,
        artifacts_dir=artifacts_dir,
    )

    evidence = {
        "system": "Training Data Execution System",
        "version": "1.1.0",
        "provenance": {
            "what_consumed": consumption_summary,
            "why_consumed": {
                "mixture": mixture,
                "opus": opus_summary,
                "protected_floors": mixture.get("protected_floors", {}),
            },
            "what_learned": learning_summary,
            "how_to_reconstruct": reconstruction,
        },
        "tokenizer_hash": tokenizer_hash,
        "manifest_hash": manifest_hash,
        "packing": packing_report,
        "audit": audit_report,
        "metrics": metrics,
        "metrics_verification": metrics_verification,
        "consumption_integrity": consumption_verify,
        "replay": replay_result,
        "evidence_hash": "",
    }
    evidence["evidence_hash"] = sha256_json(
        {k: v for k, v in evidence.items() if k != "evidence_hash"}
    )
    return evidence
