"""Audit engine — comprehensive execution verification."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from storage.hash_utils import sha256_json


class AuditEngine:
    """Audits every aspect of a training run for reproducibility."""

    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.checks: list[dict[str, Any]] = []

    def check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "passed": passed, "detail": detail})

    def audit_tokenizer(self, tokenizer_hash: str, verified: bool) -> None:
        self.check("tokenizer_hash_verified", verified, tokenizer_hash)

    def audit_shards(self, count: int) -> None:
        self.check("shards_created", count > 0, f"{count} shards")

    def audit_manifests(self, manifests: list[dict[str, Any]]) -> None:
        all_valid = all(
            sha256_json({k: v for k, v in m.items() if k != "manifest_hash"})
            == m["manifest_hash"]
            for m in manifests
        )
        self.check("manifests_verified", all_valid, f"{len(manifests)} manifests")

    def audit_mixture(self, mixture: dict[str, Any]) -> None:
        self.check("mixture_compiled", "mixture_hash" in mixture, mixture.get("stage", ""))

    def audit_packing(self, report: dict[str, Any]) -> None:
        self.check(
            "packing_completed",
            report.get("batches", 0) > 0,
            f"util={report.get('avg_utilization', 0):.2%}",
        )

    def audit_eval_firewall(self, blocked: int) -> None:
        self.check("eval_shard_blocked", blocked > 0, f"{blocked} eval shards blocked")

    def audit_opus(self, decisions: list[dict[str, Any]]) -> None:
        self.check("opus_decisions_recorded", len(decisions) > 0, f"{len(decisions)} decisions")

    def audit_checkpoint(self, checkpoint: dict[str, Any] | None) -> None:
        if checkpoint:
            valid = (
                sha256_json({k: v for k, v in checkpoint.items() if k != "checkpoint_hash"})
                == checkpoint["checkpoint_hash"]
            )
            self.check("checkpoint_saved", valid, checkpoint["checkpoint_id"])
        else:
            self.check("checkpoint_saved", False, "no checkpoint")

    def audit_crash(self, crashed: bool) -> None:
        self.check("crash_simulated", crashed)

    def audit_resume(self, matched: bool) -> None:
        self.check("resume_next_batch_matched", matched)

    def audit_replay(self, result: dict[str, Any]) -> None:
        self.check("replay_hash_matched", result.get("all_matched", False))

    def audit_fork(self, fork_count: int) -> None:
        self.check("fork_created", fork_count > 0, f"{fork_count} forks")

    def generate_report(self) -> dict[str, Any]:
        passed = sum(1 for c in self.checks if c["passed"])
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checks": len(self.checks),
            "passed": passed,
            "failed": len(self.checks) - passed,
            "all_passed": passed == len(self.checks),
            "checks": list(self.checks),
            "audit_hash": "",
        }
        self.check("audit_completed", report["all_passed"])
        report["checks"] = list(self.checks)
        report["total_checks"] = len(self.checks)
        report["passed"] = sum(1 for c in self.checks if c["passed"])
        report["failed"] = report["total_checks"] - report["passed"]
        report["all_passed"] = report["passed"] == report["total_checks"]
        report["audit_hash"] = sha256_json(
            {k: v for k, v in report.items() if k != "audit_hash"}
        )

        report_path = self.reports_dir / "audit_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report

    def format_run_log(self) -> list[str]:
        lines = []
        for check in self.checks:
            status = "PASS" if check["passed"] else "FAIL"
            detail = f" ({check['detail']})" if check["detail"] else ""
            lines.append(f"[{status}] {check['name']}{detail}")
        return lines
