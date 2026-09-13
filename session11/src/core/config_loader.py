"""YAML spec loader and validator — SPEC: experiment_spec.yaml"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.core.schemas import ExperimentSpec

ROOT = Path(__file__).resolve().parent.parent.parent
SPECS = ROOT / "specs"

REQUIRED_EXPERIMENT_FIELDS = {
    "id",
    "claim_id",
    "title",
    "hypothesis",
    "objective",
    "controls",
    "independent_variable",
    "dependent_variables",
    "protocol",
    "acceptance_criteria",
    "expected_artifacts",
    "reproducibility_command",
}

REQUIRED_CLAIM_IDS = {"CLAIM-001", "CLAIM-002", "CLAIM-003", "CLAIM-004", "CLAIM-005"}
REQUIRED_EXPERIMENT_IDS = {"EXP-ADAM-001", "EXP-BIAS-001", "EXP-RATIO-001", "EXP-SCHEDULE-001", "EXP-LR-001"}
REQUIRED_SPEC_FILES = [
    "product_spec.md",
    "experiment_spec.yaml",
    "data_contracts.yaml",
    "metric_definitions.yaml",
    "acceptance_criteria.yaml",
    "decision_policy.yaml",
    "reproducibility_spec.md",
]
REQUIRED_ACCEPTANCE_SECTIONS = [
    "global",
    "novelty",
    "comparison_controls",
    "execution_modes",
    "evidence_ledger",
    "readme",
    "audit",
    "required_tests",
]
REQUIRED_METRIC_IDS = {
    "METRIC-RATIO-001",
    "METRIC-CONVERGENCE-001",
    "METRIC-WARMUP-001",
    "METRIC-STAB-001",
    "METRIC-CONTROL-001",
    "METRIC-EXTRAP-001",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return yaml.safe_load(f)


def load_experiment_specs() -> list[ExperimentSpec]:
    data = load_yaml(SPECS / "experiment_spec.yaml")
    specs = []
    for item in data["experiments"]:
        missing = REQUIRED_EXPERIMENT_FIELDS - set(item.keys())
        if missing:
            raise ValueError(f"Experiment {item.get('id', '?')} missing fields: {missing}")
        kwargs = {k: item[k] for k in REQUIRED_EXPERIMENT_FIELDS}
        kwargs["status"] = item.get("status", "UNTESTED")
        specs.append(ExperimentSpec(**kwargs))
    return specs


def _validate_experiments(errors: list[str]) -> None:
    data = load_yaml(SPECS / "experiment_spec.yaml")
    items = data.get("experiments", [])
    ids = [e.get("id") for e in items]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate experiment IDs in experiment_spec.yaml")
    missing_exp = REQUIRED_EXPERIMENT_IDS - set(ids)
    if missing_exp:
        errors.append(f"Missing required experiment IDs: {missing_exp}")

    claim_ids = {e.get("claim_id") for e in items}
    missing_claims = REQUIRED_CLAIM_IDS - claim_ids
    if missing_claims:
        errors.append(f"Experiments missing claim_id linkage for: {missing_claims}")

    for e in items:
        eid = e.get("id", "?")
        ac = e.get("acceptance_criteria", {})
        if eid == "EXP-LR-001":
            fields = ac.get("required_extrapolation_fields", [])
            required = {
                "proposed_learning_rate",
                "extrapolation_method",
                "measured_supporting_points",
                "confidence",
                "why_confidence_is_limited",
                "next_validation_sweep",
            }
            if not required <= set(fields):
                errors.append(f"{eid}: missing required_extrapolation_fields")
        if eid == "EXP-SCHEDULE-001" and not ac.get("comparison_must_pass_validator"):
            errors.append(f"{eid}: comparison_must_pass_validator must be true")


def _validate_metrics(errors: list[str]) -> None:
    data = load_yaml(SPECS / "metric_definitions.yaml")
    found = {m.get("id") for m in data.get("metrics", [])}
    missing = REQUIRED_METRIC_IDS - found
    if missing:
        errors.append(f"metric_definitions.yaml missing metric IDs: {missing}")

    stab = next((m for m in data.get("metrics", []) if m.get("id") == "METRIC-STAB-001"), None)
    if stab:
        defaults = stab.get("defaults", {})
        if "window" not in defaults or "tolerance" not in defaults:
            errors.append("METRIC-STAB-001 must define defaults.window and defaults.tolerance")


def _validate_acceptance(errors: list[str]) -> None:
    data = load_yaml(SPECS / "acceptance_criteria.yaml")
    acc = data.get("acceptance", {})
    for section in REQUIRED_ACCEPTANCE_SECTIONS:
        if section not in data and section not in acc:
            if section == "required_tests":
                if "required_tests" not in data:
                    errors.append("acceptance_criteria.yaml missing required_tests")
            elif section not in acc:
                errors.append(f"acceptance_criteria.yaml missing acceptance.{section}")

    if "required_tests" in data and len(data["required_tests"]) < 16:
        errors.append("required_tests must list at least 16 test entries (incl. gap markers)")

    modes = acc.get("execution_modes", {})
    sep = modes.get("separation_rules", [])
    if len(sep) < 3:
        errors.append("execution_modes.separation_rules must have at least 3 rules")

    lr = acc.get("EXP-LR-001", {})
    if not lr.get("width_4096_must_not_appear_in_sweep_csv"):
        errors.append("EXP-LR-001 must require width_4096_must_not_appear_in_sweep_csv")


def _validate_decision_policy(errors: list[str]) -> None:
    data = load_yaml(SPECS / "decision_policy.yaml")
    if "claim_decision_map" not in data:
        errors.append("decision_policy.yaml missing claim_decision_map")
    elif REQUIRED_CLAIM_IDS - set(data["claim_decision_map"].keys()):
        errors.append("claim_decision_map must cover all CLAIM-* IDs")
    if "forbidden_conclusion_words" not in data:
        errors.append("decision_policy.yaml missing forbidden_conclusion_words")


def _validate_data_contracts(errors: list[str]) -> None:
    data = load_yaml(SPECS / "data_contracts.yaml")
    required_types = ["EvidenceRecord", "Width4096Extrapolation", "ComparisonValidationResult", "READMEGenerationContract"]
    for t in required_types:
        if t not in data:
            errors.append(f"data_contracts.yaml missing {t}")


def validate_all_specs() -> list[str]:
    """Return list of errors; empty means valid."""
    errors: list[str] = []

    for name in REQUIRED_SPEC_FILES:
        if not (SPECS / name).exists():
            errors.append(f"Missing spec file: {name}")

    for yaml_name in ["experiment_spec.yaml", "data_contracts.yaml", "metric_definitions.yaml", "acceptance_criteria.yaml", "decision_policy.yaml"]:
        try:
            load_yaml(SPECS / yaml_name)
        except Exception as e:
            errors.append(f"{yaml_name} invalid YAML: {e}")

    try:
        load_experiment_specs()
        _validate_experiments(errors)
    except Exception as e:
        errors.append(f"experiment_spec.yaml invalid: {e}")

    try:
        _validate_metrics(errors)
        _validate_acceptance(errors)
        _validate_decision_policy(errors)
        _validate_data_contracts(errors)
    except Exception as e:
        errors.append(f"Cross-spec validation failed: {e}")

    return errors
