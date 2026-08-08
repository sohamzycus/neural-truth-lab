#!/usr/bin/env python3
"""Rubric-aligned tests — maps to 1,000-point evaluation criteria."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.evidence_engine import (
    reconstruct_metrics_from_batches,
    verify_consumption_ledger,
    verify_metrics_claims,
)
from core.packing_engine import PackedBatch, PadOnlyPacking
from ledger.consumption_ledger import ConsumptionLedger
from ledger.learning_ledger import LearningLedger


class TestEvidenceProvenance(unittest.TestCase):
    def test_metrics_reconstructable_from_batches(self):
        batch = PackedBatch(
            batch_id="b1",
            token_ids=[1, 2, 3] + [0] * 5,
            attention_mask=[1, 1, 1] + [0] * 5,
            shard_map=[{"shard_id": "s1", "offset": 0, "length": 3}],
            packing_policy="pad_only",
            max_seq_len=8,
            useful_tokens=3,
            padded_tokens=5,
        )
        batch.finalize()
        registry = {batch.batch_id: batch}
        reported = {
            "total_batches": 1,
            "total_useful_tokens": 3,
            "total_padded_tokens": 5,
            "packing_utilization_pct": 37.5,
        }
        recomputed = reconstruct_metrics_from_batches(registry, [batch.batch_id])
        result = verify_metrics_claims(reported, recomputed)
        self.assertTrue(result["all_match"])

    def test_attention_mask_matches_tokens(self):
        policy = PadOnlyPacking(max_seq_len=8)
        shard = {"shard_id": "s1", "token_ids": [1, 2, 3], "num_tokens": 3, "evaluation": False}
        batch = policy.pack([shard])[0]
        self.assertEqual(len(batch.token_ids), len(batch.attention_mask))
        self.assertEqual(sum(batch.attention_mask), batch.useful_tokens)


class TestEndToEndSubmission(unittest.TestCase):
    def test_run_demo_regenerates_submission_artifacts(self):
        artifacts = PROJECT_ROOT / "submission_artifacts"
        if artifacts.exists():
            import shutil
            shutil.rmtree(artifacts)

        result = subprocess.run(
            [sys.executable, "run_demo.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

        required = [
            "run.log",
            "evidence.json",
            "evidence.md",
            "performance.json",
            "ledgers/consumption.jsonl",
            "ledgers/learning.jsonl",
            "manifests/primary_manifest.json",
            "reports/audit_report.json",
        ]
        for rel in required:
            self.assertTrue((artifacts / rel).exists(), f"missing {rel}")

        evidence = json.loads((artifacts / "evidence.json").read_text())
        self.assertIn("provenance", evidence)
        self.assertIn("what_consumed", evidence["provenance"])
        self.assertIn("why_consumed", evidence["provenance"])
        self.assertIn("what_learned", evidence["provenance"])
        self.assertIn("how_to_reconstruct", evidence["provenance"])
        self.assertTrue(evidence["metrics_verification"]["all_match"])
        self.assertTrue(evidence["consumption_integrity"]["no_duplicate_global_batches"])
        self.assertTrue(evidence["consumption_integrity"]["no_missing_global_batches"])
        self.assertTrue(evidence["replay"]["all_matched"])
        self.assertTrue(evidence["audit"]["all_passed"])

        log = (artifacts / "run.log").read_text()
        for marker in (
            "tokenizer_hash_verified",
            "eval_shard_blocked",
            "crash_simulated",
            "resume_next_batch_matched",
            "replay_hash_matched",
            "audit_completed",
        ):
            self.assertIn(marker, log)


if __name__ == "__main__":
    unittest.main()
