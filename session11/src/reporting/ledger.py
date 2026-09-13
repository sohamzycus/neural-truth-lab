"""Optimizer Evidence Ledger — core novelty."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.schemas import ClaimStatus, EvidenceRecord
from src.validation.result_validator import validate_evidence_record

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT.parent, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "UNAVAILABLE"


class EvidenceLedger:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or OUTPUTS / "evidence_ledger.jsonl"
        self.records: list[EvidenceRecord] = []
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: EvidenceRecord) -> None:
        errors = validate_evidence_record(record.to_dict())
        if errors:
            raise ValueError(f"Invalid evidence record: {errors}")
        self.records.append(record)
        with self.path.open("a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def write_markdown(self, md_path: Path | None = None) -> Path:
        md_path = md_path or OUTPUTS / "evidence_ledger.md"
        lines = ["# Optimizer Evidence Ledger", ""]
        for r in self.records:
            lines.append(f"## {r.evidence_id} — {r.experiment_id}")
            lines.append(f"- **Claim:** {r.claim_id}")
            lines.append(f"- **Decision:** {r.decision}")
            lines.append(f"- **Confidence:** {r.confidence}")
            lines.append(f"- **Mode:** {r.execution_mode}")
            lines.append(f"- **Artifacts:** {', '.join(r.raw_artifacts)}")
            lines.append("")
        md_path.write_text("\n".join(lines))
        return md_path

    @staticmethod
    def make_record(
        evidence_id: str,
        experiment_id: str,
        claim_id: str,
        hypothesis: str,
        controls: dict,
        changed_variable: str,
        seed: int,
        model_config: dict,
        optimizer_config: dict,
        schedule_config: dict,
        data_config: dict,
        runtime_config: dict,
        raw_artifacts: list[str],
        derived_metrics: dict,
        statistical_summary: dict,
        decision: str,
        confidence: str,
        limitations: list[str],
        reproducibility_command: str,
        execution_mode: str,
    ) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=evidence_id,
            experiment_id=experiment_id,
            claim_id=claim_id,
            hypothesis=hypothesis,
            controls=controls,
            changed_variable=changed_variable,
            seed=seed,
            model_config=model_config,
            optimizer_config=optimizer_config,
            schedule_config=schedule_config,
            data_config=data_config,
            runtime_config=runtime_config,
            raw_artifacts=raw_artifacts,
            derived_metrics=derived_metrics,
            statistical_summary=statistical_summary,
            decision=decision,
            confidence=confidence,
            limitations=limitations,
            reproducibility_command=reproducibility_command,
            git_commit_if_available=_git_commit(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_mode=execution_mode,
        )


def apply_decision_policy(
    controls_valid: bool,
    result_missing: bool,
    max_abs_diff: float | None = None,
    relative_improvement: float | None = None,
    threshold_diff: float = 1e-6,
    inconclusive_threshold: float = 0.01,
) -> tuple[ClaimStatus, str]:
    """DECISION-001 through DECISION-008."""
    if not controls_valid:
        return ClaimStatus.INVALID_EXPERIMENT, "NONE"
    if result_missing:
        return ClaimStatus.NOT_REACHED, "NONE"
    if max_abs_diff is not None:
        if max_abs_diff <= threshold_diff:
            return ClaimStatus.SUPPORTED, "HIGH"
        return ClaimStatus.REFUTED, "HIGH"
    if relative_improvement is not None:
        if relative_improvement < inconclusive_threshold:
            return ClaimStatus.INCONCLUSIVE, "LOW"
        if relative_improvement < 0.05:
            return ClaimStatus.WEAKLY_SUPPORTED, "MEDIUM"
        return ClaimStatus.SUPPORTED, "HIGH"
    return ClaimStatus.INCONCLUSIVE, "LOW"
