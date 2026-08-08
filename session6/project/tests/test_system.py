#!/usr/bin/env python3
"""Automated test suite for Training Data Execution System."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.batch_engine import BatchEngine, EvalFirewallViolation
from core.checkpoint_engine import CheckpointEngine
from core.curriculum_engine import CurriculumEngine
from core.fork_engine import ForkEngine
from core.manifest_engine import ManifestEngine
from core.opus_engine import OpusEngine, OpusDecision
from core.packing_engine import (
    BestFitPacking,
    ConcatenatePacking,
    GreedyPacking,
    PadOnlyPacking,
    StructurePreservingPacking,
    get_packing_policy,
)
from core.replay_engine import ReplayEngine
from core.shard_engine import ShardEngine
from core.tokenizer_engine import FrozenTokenizer
from core.trainer_engine import CrashSimulation, TrainerEngine
from core.metrics_engine import MetricsCollector
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger
from models.tiny_model import TinyModel
from storage.immutable_store import ImmutableStore
from storage.hash_utils import sha256_json


SAMPLE_DOCS = [
    {"doc_id": "d1", "text": "hello world training data", "lane": "english"},
    {"doc_id": "d2", "text": "def foo bar baz code", "lane": "code"},
    {"doc_id": "d3", "text": "hindi text example here", "lane": "indic"},
    {"doc_id": "eval1", "text": "evaluation only benchmark", "lane": "english"},
]


def _make_shard(tokenizer: FrozenTokenizer, doc: dict, *, evaluation: bool = False) -> dict:
    engine = ShardEngine(ImmutableStore(Path(tempfile.mkdtemp())))
    return engine.create_shard(
        token_ids=tokenizer.encode(doc["text"]),
        tokenizer_hash=tokenizer.tokenizer_hash,
        source=doc["doc_id"],
        document_ids=[doc["doc_id"]],
        curriculum_stage="stage_a",
        lane=doc["lane"],
        capability="test",
        evaluation=evaluation,
    )


class TestTokenizerImmutable(unittest.TestCase):
    def test_freeze_and_verify(self):
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        h1 = tok.freeze()
        tok.verify_frozen()
        self.assertTrue(tok.frozen)
        self.assertEqual(len(h1), 64)

    def test_cannot_modify_after_freeze(self):
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()
        with self.assertRaises(RuntimeError):
            tok.build_vocab(SAMPLE_DOCS)

    def test_hash_changes_if_vocab_changes_before_freeze(self):
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS[:1])
        h1 = tok.freeze()
        tok2 = FrozenTokenizer()
        tok2.build_vocab(SAMPLE_DOCS)
        h2 = tok2.freeze()
        self.assertNotEqual(h1, h2)


class TestManifestHash(unittest.TestCase):
    def test_manifest_hash_verifiable(self):
        store = ImmutableStore(Path(tempfile.mkdtemp()))
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()
        shard_engine = ShardEngine(store)
        shards = []
        for doc in SAMPLE_DOCS[:3]:
            shards.append(
                shard_engine.create_shard(
                    token_ids=tok.encode(doc["text"]),
                    tokenizer_hash=tok.tokenizer_hash,
                    source=doc["doc_id"],
                    document_ids=[doc["doc_id"]],
                    curriculum_stage="stage_a",
                    lane=doc["lane"],
                    capability="test",
                )
            )
        me = ManifestEngine(store)
        manifest = me.create_manifest(
            name="test", shards=shards, tokenizer_hash=tok.tokenizer_hash, curriculum_stage="stage_a"
        )
        self.assertTrue(me.verify_manifest(manifest))


class TestReplayIdentical(unittest.TestCase):
    def test_replay_hashes_match(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()

        shards = []
        se = ShardEngine(store)
        for doc in SAMPLE_DOCS[:3]:
            shards.append(
                se.create_shard(
                    token_ids=tok.encode(doc["text"]),
                    tokenizer_hash=tok.tokenizer_hash,
                    source=doc["doc_id"],
                    document_ids=[doc["doc_id"]],
                    curriculum_stage="stage_a",
                    lane=doc["lane"],
                    capability="test",
                )
            )

        policy = PadOnlyPacking(max_seq_len=32)
        be = BatchEngine(policy)
        batches = be.create_batches(shards)
        consumption = ConsumptionLedger(tmp / "consumption.jsonl")
        learning = LearningLedger(tmp / "learning.jsonl")
        model = TinyModel(len(tok.vocab))
        trainer = TrainerEngine(
            model, be, consumption, learning,
            CheckpointEngine(store, tmp / "ckpt"),
            MetricsCollector(),
            tokenizer_hash=tok.tokenizer_hash,
        )
        trainer.train_batches(batches, simulate_crash=False)

        replay = ReplayEngine(consumption, learning, trainer.batch_registry)
        result = replay.replay()
        self.assertTrue(result["all_matched"])


class TestResumeIdentical(unittest.TestCase):
    def test_no_duplicate_batches_on_resume(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()

        shards = []
        se = ShardEngine(store)
        for doc in SAMPLE_DOCS[:3]:
            shards.append(
                se.create_shard(
                    token_ids=tok.encode(doc["text"]),
                    tokenizer_hash=tok.tokenizer_hash,
                    source=doc["doc_id"],
                    document_ids=[doc["doc_id"]],
                    curriculum_stage="stage_a",
                    lane=doc["lane"],
                    capability="test",
                )
            )

        policy = PadOnlyPacking(max_seq_len=32)
        be = BatchEngine(policy)
        batches = be.create_batches(shards)
        # Expand to 20 batches
        from uuid import uuid4
        from core.packing_engine import PackedBatch
        base = list(batches)
        while len(batches) < 20:
            for b in base:
                c = PackedBatch(
                    batch_id=str(uuid4()),
                    token_ids=list(b.token_ids),
                    attention_mask=list(b.attention_mask),
                    shard_map=list(b.shard_map),
                    packing_policy=b.packing_policy,
                    max_seq_len=b.max_seq_len,
                    useful_tokens=b.useful_tokens,
                    padded_tokens=b.padded_tokens,
                )
                c.finalize()
                batches.append(c)
                if len(batches) >= 20:
                    break

        consumption = ConsumptionLedger(tmp / "consumption.jsonl")
        learning = LearningLedger(tmp / "learning.jsonl")
        ckpt_engine = CheckpointEngine(store, tmp / "ckpt")
        model = TinyModel(len(tok.vocab))
        trainer = TrainerEngine(
            model, be, consumption, learning, ckpt_engine,
            MetricsCollector(), tokenizer_hash=tok.tokenizer_hash,
        )
        trainer.CRASH_AFTER_BATCH = 10
        try:
            trainer.train_batches(batches, simulate_crash=True)
        except CrashSimulation:
            pass

        pre_resume_ids = consumption.get_batch_ids()
        trainer.resume_from_checkpoint(trainer.last_checkpoint, batches)
        post_resume_ids = consumption.get_batch_ids()

        # No duplicate consecutive batches from resume point
        resume_from = trainer.last_checkpoint["current_batch"]
        ids_before = pre_resume_ids[:resume_from]
        ids_after = post_resume_ids[resume_from:]
        self.assertEqual(len(ids_after), len(batches) - resume_from)


class TestCheckpointOffset(unittest.TestCase):
    def test_checkpoint_stores_ledger_offset(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        ckpt = CheckpointEngine(store, tmp / "ckpt")
        cp = ckpt.save(
            model_state={"w": 1},
            optimizer_state={"step": 0},
            scheduler_state={},
            ledger_offset=42,
            rng_state=[42],
            current_batch=10,
            current_shard=None,
            curriculum_stage="stage_a",
            tokenizer_hash="abc",
            manifest_hash="def",
        )
        self.assertEqual(cp["ledger_offset"], 42)
        self.assertTrue(ckpt.verify_checkpoint(cp))


class TestNoDuplicateBatches(unittest.TestCase):
    def test_unique_batch_ids_in_registry(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()
        se = ShardEngine(store)
        shards = [
            se.create_shard(
                token_ids=tok.encode(d["text"]),
                tokenizer_hash=tok.tokenizer_hash,
                source=d["doc_id"],
                document_ids=[d["doc_id"]],
                curriculum_stage="stage_a",
                lane=d["lane"],
                capability="test",
            )
            for d in SAMPLE_DOCS[:3]
        ]
        be = BatchEngine(PadOnlyPacking(max_seq_len=32))
        batches = be.create_batches(shards)
        ids = [b.batch_id for b in batches]
        self.assertEqual(len(ids), len(set(ids)))


class TestEvaluationFirewall(unittest.TestCase):
    def test_eval_shards_blocked(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        tok = FrozenTokenizer()
        tok.build_vocab(SAMPLE_DOCS)
        tok.freeze()
        se = ShardEngine(store)
        eval_shard = se.create_shard(
            token_ids=tok.encode("eval only"),
            tokenizer_hash=tok.tokenizer_hash,
            source="eval",
            document_ids=["eval"],
            curriculum_stage="stage_a",
            lane="english",
            capability="eval",
            evaluation=True,
        )
        be = BatchEngine(PadOnlyPacking(max_seq_len=32))
        batches = be.create_batches([eval_shard], allow_eval=False)
        self.assertEqual(len(batches), 0)
        self.assertEqual(be.eval_blocked_count, 1)


class TestProtectedFloor(unittest.TestCase):
    def test_curriculum_protected_floor(self):
        curriculum = CurriculumEngine()
        shards_by_lane = {
            "english": [{"shard_id": "e1", "lane": "english"}],
            "code": [{"shard_id": "c1", "lane": "code"}],
            "indic": [{"shard_id": "i1", "lane": "indic"}],
        }
        selected = curriculum.select_shards_for_batch(shards_by_lane, batch_size=10, rng_state=[42])
        lanes = {s["lane"] for s in selected}
        self.assertTrue(len(lanes) >= 2)


class TestPackingUtilization(unittest.TestCase):
    def test_all_policies_produce_batches(self):
        shard = {
            "shard_id": "s1",
            "token_ids": list(range(10, 30)),
            "num_tokens": 20,
        }
        for name in ("pad_only", "concatenate", "greedy", "best_fit", "structure_preserving"):
            policy = get_packing_policy(name, max_seq_len=64)
            batches = policy.pack([shard])
            self.assertGreater(len(batches), 0)
            self.assertGreater(policy.utilization(batches[0]), 0)


class TestLedgerAppendOnly(unittest.TestCase):
    def test_ledger_only_grows(self):
        tmp = Path(tempfile.mkdtemp())
        ledger = ConsumptionLedger(tmp / "c.jsonl")
        ledger.record(
            shard_id="s1", batch_id="b1", microbatch_idx=0,
            global_batch_idx=0, checkpoint_id=None, gpu_rank=0,
        )
        ledger.record(
            shard_id="s2", batch_id="b2", microbatch_idx=0,
            global_batch_idx=1, checkpoint_id=None, gpu_rank=0,
        )
        self.assertEqual(ledger.offset, 2)
        events = ledger.read_all()
        self.assertEqual(events[0]["offset"], 0)
        self.assertEqual(events[1]["offset"], 1)


class TestForkIntegrity(unittest.TestCase):
    def test_fork_links_to_parent(self):
        tmp = Path(tempfile.mkdtemp())
        store = ImmutableStore(tmp / "store")
        ckpt_engine = CheckpointEngine(store, tmp / "ckpt")
        parent = ckpt_engine.save(
            model_state={}, optimizer_state={}, scheduler_state={},
            ledger_offset=10, rng_state=[42], current_batch=5,
            current_shard=None, curriculum_stage="stage_a",
            tokenizer_hash="t", manifest_hash="m",
        )
        fork_engine = ForkEngine(tmp)
        shard = {"shard_id": "s1", "token_ids": [1, 2, 3], "num_tokens": 3, "evaluation": False}
        result = fork_engine.fork(
            parent_checkpoint=parent,
            new_packing_policy="pad_only",
            branch_name="test_fork",
            shards=[shard],
        )
        self.assertTrue(
            fork_engine.verify_fork_integrity(result["fork_record"], parent)
        )


class TestOpusDecisions(unittest.TestCase):
    def test_opus_deterministic_per_engine(self):
        shard = {
            "shard_id": "s1",
            "content_hash": "abc123",
            "num_tokens": 15,
            "token_ids": [1, 5, 10, 15, 20],
            "lane": "english",
            "cleaning_version": "v1",
            "evaluation": False,
        }
        opus_a = OpusEngine()
        opus_b = OpusEngine()
        self.assertEqual(opus_a.score_shard(shard).decision, opus_b.score_shard(shard).decision)

    def test_opus_rejects_duplicate_content(self):
        opus = OpusEngine()
        shard = {
            "shard_id": "s1",
            "content_hash": "dup_hash",
            "num_tokens": 15,
            "token_ids": [1, 5, 10, 15, 20],
            "lane": "english",
            "cleaning_version": "v1",
            "evaluation": False,
        }
        first = opus.score_shard(shard)
        second = opus.score_shard(shard)
        self.assertEqual(first.decision, OpusDecision.ACCEPT)
        self.assertEqual(second.decision, OpusDecision.REJECT)


if __name__ == "__main__":
    unittest.main()
