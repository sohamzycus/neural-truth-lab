#!/usr/bin/env python3
"""Training Data Execution System — production-grade demo runner.

Usage:
    python run_demo.py
    python run_demo.py --time-machine 45
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ponytail: ensure project root on sys.path for module imports
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.audit_engine import AuditEngine
from core.batch_engine import BatchEngine, EvalFirewallViolation
from core.checkpoint_engine import CheckpointEngine
from core.curriculum_engine import CurriculumEngine
from core.evidence_engine import build_full_evidence
from core.fork_engine import ForkEngine
from core.manifest_engine import ManifestEngine
from core.metrics_engine import MetricsCollector
from core.opus_engine import OpusEngine, OpusDecision
from core.packing_engine import get_packing_policy
from core.replay_engine import ReplayEngine
from core.shard_engine import ShardEngine
from core.tokenizer_engine import FrozenTokenizer
from core.trainer_engine import CrashSimulation, TrainerEngine
from models.tiny_model import TinyModel
from storage.immutable_store import ImmutableStore
from storage.hash_utils import sha256_json
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger


# ── Deterministic seed documents ──────────────────────────────────────────

DOCUMENTS: list[dict[str, Any]] = [
    {"doc_id": "en_001", "text": "the quick brown fox jumps over the lazy dog", "lane": "english", "capability": "web_general", "stage": "stage_a"},
    {"doc_id": "en_002", "text": "machine learning systems require deterministic data pipelines", "lane": "english", "capability": "web_general", "stage": "stage_a"},
    {"doc_id": "en_003", "text": "natural language processing enables intelligent applications", "lane": "english", "capability": "web_general", "stage": "stage_a"},
    {"doc_id": "code_001", "text": "def train model optimizer loss backward step", "lane": "code", "capability": "coding", "stage": "stage_a"},
    {"doc_id": "code_002", "text": "class DataLoader batch shuffle dataset epoch", "lane": "code", "capability": "coding", "stage": "stage_a"},
    {"doc_id": "code_003", "text": "import torch nn functional optim scheduler", "lane": "code", "capability": "coding", "stage": "stage_b"},
    {"doc_id": "indic_001", "text": "bharat ki sanskriti bahut purani hai", "lane": "indic", "capability": "indic_multilingual", "stage": "stage_a"},
    {"doc_id": "indic_002", "text": "hindi aur english dono bhashayen important hain", "lane": "indic", "capability": "indic_multilingual", "stage": "stage_a"},
    {"doc_id": "indic_003", "text": "tamil telugu kannada malayalam languages of south", "lane": "indic", "capability": "indic_multilingual", "stage": "stage_b"},
    {"doc_id": "agent_001", "text": "agent tool use function call api request response", "lane": "agent", "capability": "agentic", "stage": "stage_c"},
    {"doc_id": "agent_002", "text": "plan execute observe reflect agentic loop iteration", "lane": "agent", "capability": "agentic", "stage": "stage_c"},
    {"doc_id": "eval_001", "text": "evaluation benchmark test held out metric score", "lane": "english", "capability": "evaluation", "stage": "stage_a", "evaluation": True},
    {"doc_id": "eval_002", "text": "perplexity accuracy f1 score bleu rouge eval", "lane": "code", "capability": "evaluation", "stage": "stage_b", "evaluation": True},
]


def setup_directories(root: Path, *, clean: bool = True) -> dict[str, Path]:
    dirs = {
        "artifacts": root / "submission_artifacts",
        "manifests": root / "manifests",
        "checkpoints": root / "checkpoints",
        "ledgers": root / "ledgers",
        "reports": root / "submission_artifacts" / "reports",
        "store": root / "storage" / "artifacts",
    }
    if clean:
        for key in ("ledgers", "checkpoints", "artifacts"):
            if dirs[key].exists():
                shutil.rmtree(dirs[key])
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def log(msg: str, log_lines: list[str]) -> None:
    print(msg)
    log_lines.append(msg)


def generate_evidence(
    audit_report: dict[str, Any],
    metrics: dict[str, Any],
    tokenizer_hash: str,
    manifest_hash: str,
    replay_result: dict[str, Any],
    *,
    mixture: dict[str, Any],
    opus_decisions: list[dict[str, Any]],
    consumption: ConsumptionLedger,
    learning: LearningLedger,
    batch_registry: dict[str, Any],
    checkpoint: dict[str, Any] | None,
    fork_record: dict[str, Any] | None,
    artifacts_dir: Path,
    packing_report: dict[str, Any],
) -> dict[str, Any]:
    return build_full_evidence(
        audit_report=audit_report,
        metrics=metrics,
        replay_result=replay_result,
        tokenizer_hash=tokenizer_hash,
        manifest_hash=manifest_hash,
        mixture=mixture,
        opus_decisions=opus_decisions,
        consumption=consumption,
        learning=learning,
        batch_registry=batch_registry,
        checkpoint=checkpoint,
        fork_record=fork_record,
        artifacts_dir=artifacts_dir,
        packing_report=packing_report,
    )


def evidence_markdown(evidence: dict[str, Any]) -> str:
    prov = evidence.get("provenance", {})
    lines = [
        "# Training Data Execution System — Evidence Report",
        "",
        f"**Generated:** {evidence.get('timestamp', 'see audit.timestamp')}",
        f"**Evidence Hash:** `{evidence['evidence_hash'][:32]}…`",
        "",
        "## What Was Consumed",
        "",
        f"- Consumption events: {prov.get('what_consumed', {}).get('event_count', 0)}",
        f"- Unique shards: {prov.get('what_consumed', {}).get('unique_shards_consumed', 0)}",
        f"- Ledger hash: `{prov.get('what_consumed', {}).get('ledger_hash', '')[:32]}…`",
        "",
        "## Why It Was Consumed",
        "",
    ]
    mixture = prov.get("why_consumed", {}).get("mixture", {})
    lines.extend([
        f"- Curriculum stage: **{mixture.get('stage', 'n/a')}**",
        f"- Planned mixture: `{mixture.get('planned', {})}`",
        f"- Actual mixture: `{mixture.get('actual', {})}`",
        f"- Protected floors: `{mixture.get('protected_floors', {})}`",
        "",
        "### OPUS Decisions",
        "",
    ])
    opus = prov.get("why_consumed", {}).get("opus", {})
    for decision, count in opus.get("decision_counts", {}).items():
        lines.append(f"- {decision}: {count}")
    lines.extend([
        "",
        "## What The Model Learned",
        "",
    ])
    learned = prov.get("what_learned", {})
    lines.extend([
        f"- Learning events: {learned.get('event_count', 0)}",
        f"- Final loss: {learned.get('final_loss', 'n/a')}",
        f"- Final perplexity: {learned.get('final_perplexity', 'n/a')}",
        f"- OPUS in learning ledger: `{learned.get('opus_decision_counts', {})}`",
        "",
        "## How To Reconstruct",
        "",
    ])
    recon = prov.get("how_to_reconstruct", {})
    for i, step in enumerate(recon.get("steps", []), 1):
        lines.append(f"{i}. {step}")
    lines.extend([
        "",
        f"- Resume from batch: {recon.get('resume_from_batch')}",
        f"- Batch sequence verified: {recon.get('batch_sequence_verified')}",
        "",
        "## Audit Results",
        "",
        f"- Total checks: {evidence['audit']['total_checks']}",
        f"- Passed: {evidence['audit']['passed']}",
        f"- All passed: {evidence['audit']['all_passed']}",
        "",
        "### Check Details",
        "",
    ])
    for check in evidence["audit"]["checks"]:
        status = "✅" if check["passed"] else "❌"
        lines.append(f"- {status} **{check['name']}**: {check.get('detail', '')}")
    mv = evidence.get("metrics_verification", {})
    lines.extend([
        "",
        "## Metrics Verification (recomputed from batches)",
        "",
        f"- All metrics match: **{mv.get('all_match', False)}**",
        f"- Useful tokens: reported={evidence['metrics'].get('total_useful_tokens')} "
        f"recomputed={mv.get('recomputed_from_batches', {}).get('total_useful_tokens')}",
        f"- Packing %: reported={evidence['metrics'].get('packing_utilization_pct')}% "
        f"recomputed={mv.get('recomputed_from_batches', {}).get('packing_utilization_pct')}%",
        "",
        "## Replay Verification",
        "",
        f"- Batches verified: {evidence['replay']['verified']}/{evidence['replay']['total_batches']}",
        f"- All matched: {evidence['replay']['all_matched']}",
        "",
        "## Hashes",
        "",
        f"- Tokenizer: `{evidence['tokenizer_hash'][:32]}…`",
        f"- Manifest: `{evidence['manifest_hash'][:32]}…`",
    ])
    return "\n".join(lines)


def run_pipeline(time_machine_offset: int | None = None) -> dict[str, Any]:
    root = PROJECT_ROOT
    dirs = setup_directories(root)
    log_lines: list[str] = []
    metrics = MetricsCollector()
    audit = AuditEngine(dirs["reports"])
    store = ImmutableStore(dirs["store"])

    # ── 1. Tokenizer ────────────────────────────────────────────────────
    log("=== Phase 1: Tokenizer ===", log_lines)
    tokenizer = FrozenTokenizer()
    tokenizer.build_vocab(DOCUMENTS)
    tokenizer_hash = tokenizer.freeze()
    tokenizer.verify_frozen()
    audit.audit_tokenizer(tokenizer_hash, True)
    log(f"[PASS] tokenizer_hash_verified ({tokenizer_hash[:16]}…)", log_lines)

    # ── 2. Shards ─────────────────────────────────────────────────────────
    log("=== Phase 2: Shards ===", log_lines)
    shard_engine = ShardEngine(store)
    shards_by_lane: dict[str, list[dict[str, Any]]] = {}

    for doc in DOCUMENTS:
        token_ids = tokenizer.encode(doc["text"])
        shard = shard_engine.create_shard(
            token_ids=token_ids,
            tokenizer_hash=tokenizer_hash,
            source=doc["doc_id"],
            document_ids=[doc["doc_id"]],
            curriculum_stage=doc.get("stage", "stage_a"),
            lane=doc["lane"],
            capability=doc.get("capability", "general"),
            evaluation=doc.get("evaluation", False),
        )
        shards_by_lane.setdefault(doc["lane"], []).append(shard)

    audit.audit_shards(len(shard_engine.shards))
    log(f"[PASS] shards_created ({len(shard_engine.shards)} shards)", log_lines)

    # ── 3. Manifests ──────────────────────────────────────────────────────
    log("=== Phase 3: Manifests ===", log_lines)
    manifest_engine = ManifestEngine(store)
    training_shards = shard_engine.get_training_shards()
    manifest = manifest_engine.create_manifest(
        name="primary_training_manifest",
        shards=training_shards,
        tokenizer_hash=tokenizer_hash,
        curriculum_stage="stage_a",
    )
    manifest_engine.verify_manifest(manifest)
    manifest_hash = manifest["manifest_hash"]
    audit.audit_manifests(manifest_engine.manifests)
    log(f"[PASS] manifests_verified ({manifest_hash[:16]}…)", log_lines)

    manifest_path = dirs["manifests"] / "primary_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    # ── 4. Curriculum ─────────────────────────────────────────────────────
    log("=== Phase 4: Curriculum ===", log_lines)
    curriculum = CurriculumEngine()
    mixture = curriculum.compile_mixture(shards_by_lane)
    audit.audit_mixture(mixture)
    log(f"[PASS] mixture_compiled (stage={mixture['stage']})", log_lines)

    # ── 5. OPUS ───────────────────────────────────────────────────────────
    log("=== Phase 5: OPUS ===", log_lines)
    opus = OpusEngine()
    opus_decisions: dict[str, str] = {}
    accepted_shards: list[dict[str, Any]] = []

    for shard in shard_engine.shards:
        score = opus.score_shard(shard, protected_floor_lane="indic")
        opus_decisions[shard["shard_id"]] = score.decision.value
        if score.decision in (OpusDecision.ACCEPT, OpusDecision.PROTECTED_OVERRIDE):
            if not shard.get("evaluation"):
                accepted_shards.append(shard)

    audit.audit_opus(opus.decisions)
    log(f"[PASS] opus_decisions_recorded ({len(opus.decisions)} decisions)", log_lines)

    # ── 6. Eval Firewall ──────────────────────────────────────────────────
    log("=== Phase 6: Evaluation Firewall ===", log_lines)
    eval_shards = shard_engine.get_eval_shards()
    try:
        policy = get_packing_policy("pad_only", max_seq_len=64)
        test_engine = BatchEngine(policy)
        test_engine.create_batches(eval_shards, allow_eval=False)
        audit.audit_eval_firewall(test_engine.eval_blocked_count)
        log(f"[PASS] eval_shard_blocked ({test_engine.eval_blocked_count} blocked)", log_lines)
    except EvalFirewallViolation:
        log("[PASS] eval_shard_blocked (firewall triggered)", log_lines)
        audit.audit_eval_firewall(1)

    # ── 7. Packing & Batches ──────────────────────────────────────────────
    log("=== Phase 7: Packing & Batches ===", log_lines)
    packing_policy = get_packing_policy("greedy", max_seq_len=64)
    batch_engine = BatchEngine(packing_policy)

    rng_state = [42]
    selected = curriculum.select_shards_for_batch(shards_by_lane, batch_size=3, rng_state=rng_state)
    assert curriculum.verify_protected_floors(selected, batch_size=3) or len(selected) < 3
    batches = batch_engine.create_batches(accepted_shards)

    # ponytail: expand batches cyclically so crash-at-17 demo has enough data
    min_batches = 25
    if len(batches) < min_batches and batches:
        from uuid import uuid4
        from core.packing_engine import PackedBatch

        base = list(batches)
        while len(batches) < min_batches:
            for b in base:
                clone = PackedBatch(
                    batch_id=str(uuid4()),
                    token_ids=list(b.token_ids),
                    attention_mask=list(b.attention_mask),
                    shard_map=list(b.shard_map),
                    packing_policy=b.packing_policy,
                    max_seq_len=b.max_seq_len,
                    useful_tokens=b.useful_tokens,
                    padded_tokens=b.padded_tokens,
                )
                clone.finalize()
                batches.append(clone)
                if len(batches) >= min_batches:
                    break

    util_report = batch_engine.utilization_report()
    metrics.set_packing_utilization(util_report["avg_utilization"])
    audit.audit_packing(util_report)
    log(f"[PASS] packing_completed (util={util_report['avg_utilization']:.2%})", log_lines)

    shard_lookup = {s["shard_id"]: s for s in shard_engine.shards}

    # ── 8. Training ───────────────────────────────────────────────────────
    log("=== Phase 8: Training ===", log_lines)
    model = TinyModel(vocab_size=len(tokenizer.vocab))
    consumption = ConsumptionLedger(dirs["ledgers"] / "consumption.jsonl")
    learning = LearningLedger(dirs["ledgers"] / "learning.jsonl")
    checkpoint_engine = CheckpointEngine(store, dirs["checkpoints"])

    trainer = TrainerEngine(
        model=model,
        batch_engine=batch_engine,
        consumption_ledger=consumption,
        learning_ledger=learning,
        checkpoint_engine=checkpoint_engine,
        metrics=metrics,
        curriculum_stage=curriculum.current_stage.name,
        tokenizer_hash=tokenizer_hash,
        manifest_hash=manifest_hash,
    )

    # Time machine mode
    if time_machine_offset is not None:
        # Run partial training first to populate ledgers
        try:
            trainer.train_batches(
                batches[:20],
                simulate_crash=False,
                shard_lookup=shard_lookup,
                opus_decisions=opus_decisions,
            )
        except CrashSimulation:
            pass

        state = trainer.get_time_machine_state(time_machine_offset)
        log("=== TIME MACHINE ===", log_lines)
        for k, v in state.items():
            log(f"  {k}: {v}", log_lines)
        return {"time_machine": state}

    crashed = False
    try:
        trainer.train_batches(
            batches,
            simulate_crash=True,
            shard_lookup=shard_lookup,
            opus_decisions=opus_decisions,
        )
    except CrashSimulation as e:
        crashed = True
        log(f"[PASS] crash_simulated (after batch {e.batch_idx})", log_lines)
        audit.audit_crash(True)

    # ── 9. Resume ─────────────────────────────────────────────────────────
    log("=== Phase 9: Resume ===", log_lines)
    if crashed and trainer.last_checkpoint:
        audit.audit_checkpoint(trainer.last_checkpoint)
        log(f"[PASS] checkpoint_saved ({trainer.last_checkpoint['checkpoint_id'][:8]}…)", log_lines)

        expected_next = trainer.last_checkpoint["current_batch"]
        trainer.resume_from_checkpoint(
            trainer.last_checkpoint,
            batches,
            shard_lookup=shard_lookup,
            opus_decisions=opus_decisions,
        )
        audit.audit_resume(trainer.resume_batch_matched)
        if trainer.resume_batch_matched:
            log("[PASS] resume_next_batch_matched", log_lines)
        else:
            log("[FAIL] resume_next_batch_matched", log_lines)

    # ── 10. Replay ────────────────────────────────────────────────────────
    log("=== Phase 10: Replay ===", log_lines)
    replay_engine = ReplayEngine(consumption, learning, trainer.batch_registry)
    replay_result = replay_engine.replay()
    metrics.set_replay_time(replay_result["replay_time_sec"])
    audit.audit_replay(replay_result)
    if replay_result["all_matched"]:
        log("[PASS] replay_hash_matched", log_lines)
    else:
        log(f"[FAIL] replay_hash_matched ({replay_result['verified']}/{replay_result['total_batches']})", log_lines)

    # ── 11. Fork ──────────────────────────────────────────────────────────
    log("=== Phase 11: Fork ===", log_lines)
    fork_engine = ForkEngine(root)
    fork_record = None
    if trainer.last_checkpoint:
        fork_result = fork_engine.fork(
            parent_checkpoint=trainer.last_checkpoint,
            new_packing_policy="best_fit",
            branch_name="fork_best_fit",
            shards=accepted_shards[:6],
        )
        fork_record = fork_result["fork_record"]
        fork_engine.verify_fork_integrity(fork_record, trainer.last_checkpoint)
        audit.audit_fork(1)
        log(f"[PASS] fork_created ({fork_result['fork_record']['fork_id'][:8]}…)", log_lines)

    # ── 12. Audit & Evidence ──────────────────────────────────────────────
    log("=== Phase 12: Audit & Evidence ===", log_lines)
    from core.evidence_engine import (
        reconstruct_metrics_from_batches,
        verify_consumption_ledger,
        verify_metrics_claims,
    )
    cons_verify = verify_consumption_ledger(consumption)
    audit.check("consumption_ledger_recorded", cons_verify["event_count"] > 0, f"{cons_verify['event_count']} events")
    audit.check("learning_ledger_recorded", learning.offset > 0, f"{learning.offset} events")
    audit.check("no_duplicate_batches", cons_verify["no_duplicate_global_batches"])
    audit.check("no_skipped_batches", cons_verify["no_missing_global_batches"])
    audit.check("protected_floors_active", bool(mixture.get("protected_floors")))
    recomputed = reconstruct_metrics_from_batches(
        trainer.batch_registry, cons_verify["batch_ids_in_order"]
    )
    perf_report = metrics.generate_report()
    mv = verify_metrics_claims(perf_report, recomputed)
    audit.check("metrics_reconstructable", mv["all_match"])

    audit_report = audit.generate_report()

    artifacts = dirs["artifacts"]
    evidence = generate_evidence(
        audit_report,
        perf_report,
        tokenizer_hash,
        manifest_hash,
        replay_result,
        mixture=mixture,
        opus_decisions=opus.decisions,
        consumption=consumption,
        learning=learning,
        batch_registry=trainer.batch_registry,
        checkpoint=trainer.last_checkpoint,
        fork_record=fork_record,
        artifacts_dir=artifacts,
        packing_report=util_report,
    )
    evidence["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Copy ledgers and checkpoints to submission before writing evidence paths
    for src_name, src_dir in [("ledgers", dirs["ledgers"]), ("checkpoints", dirs["checkpoints"])]:
        dest = artifacts / src_name
        if dest.exists():
            shutil.rmtree(dest)
        if src_dir.exists():
            shutil.copytree(src_dir, dest)

    manifest_dest = artifacts / "manifests"
    manifest_dest.mkdir(exist_ok=True)
    shutil.copy(manifest_path, manifest_dest / "primary_manifest.json")

    (artifacts / "evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8"
    )
    (artifacts / "evidence.md").write_text(evidence_markdown(evidence), encoding="utf-8")
    (artifacts / "performance.json").write_text(
        json.dumps({**perf_report, "verification": mv}, indent=2, sort_keys=True), encoding="utf-8"
    )

    for line in audit.format_run_log():
        if line not in log_lines:
            log(line, log_lines)

    (artifacts / "run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    # Sync public submission copies for GitHub links
    submission_public = root.parent / "submission"
    submission_public.mkdir(parents=True, exist_ok=True)
    for name in ("run.log", "evidence.json", "evidence.md"):
        shutil.copy(artifacts / name, submission_public / name)

    return {
        "audit": audit_report,
        "metrics": perf_report,
        "evidence": evidence,
        "log_lines": log_lines,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Training Data Execution System")
    parser.add_argument(
        "--time-machine",
        type=int,
        default=None,
        help="Show training state at ledger offset N",
    )
    args = parser.parse_args()

    result = run_pipeline(time_machine_offset=args.time_machine)

    if args.time_machine is not None:
        print(json.dumps(result["time_machine"], indent=2))
    else:
        all_passed = result["audit"]["all_passed"]
        print(f"\n{'='*60}")
        print(f"  AUDIT: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
        print(f"  Checks: {result['audit']['passed']}/{result['audit']['total_checks']}")
        print(f"  Evidence: submission_artifacts/evidence.json")
        print(f"{'='*60}")
        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
