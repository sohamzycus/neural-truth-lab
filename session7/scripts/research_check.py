#!/usr/bin/env python3
"""Validate Session 7 research artifacts, consistency, and scientific language."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
APP_DATA = ROOT / "app" / "data" / "results.json"
README = ROOT / "README.md"
NETLIFY = ROOT / "netlify.toml"

REQUIRED_RESULT_FILES = [
    "summary.json",
    "latent_sweep.json",
    "decoder_ablation.json",
    "collision_scale.json",
    "representation_comparison.json",
    "length_generalization.json",
    "language_generalization.json",
]

REQUIRED_SUMMARY_KEYS = [
    "collision", "deterministic_inverse", "waste_by_language",
    "latent_sweep", "decoder_ablation", "collision_scale",
    "representation_comparison", "hypotheses", "parameter_accounting",
]

PROHIBITED_CLAIMS = [
    (r"\bcollision[- ]free\b", "use 'no collisions observed in N tested strings'"),
    (r"\b64 dimensions are insufficient\b", "use bounded latent-sweep wording"),
    (r"\bdecoder is not the bottleneck\b", "not established by experiments"),
    (r"\breversible embedding achieved\b", "distinguish deterministic vs learned"),
    (r"\buniversally reversible\b", "not supported"),
    (r"\bguaranteed\b", "avoid absolute guarantees"),
    (r"\bproves that\b", "prefer 'provides evidence that' or 'measured'"),
]

SCAN_PATHS = [
    README,
    ROOT / "app" / "index.html",
    ROOT / "app" / "app.js",
    ROOT / "ASSIGNMENT_SCORECARD.md",
]

LOCALHOST_PATTERN = re.compile(r"https?://localhost|127\.0\.0\.1", re.I)


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def check_claims() -> list[str]:
    errors = []
    for path in SCAN_PATHS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, hint in PROHIBITED_CLAIMS:
            if re.search(pattern, text, re.I):
                errors.append(f"prohibited claim in {path.name}: /{pattern}/ ({hint})")
        if path.suffix in {".html", ".js"} and LOCALHOST_PATTERN.search(text):
            errors.append(f"localhost URL in production file: {path.name}")
    return errors


def check_consistency(summary: dict) -> list[str]:
    errors = []
    if APP_DATA.exists():
        app_data = _load_json(APP_DATA)
        if app_data.get("timestamp") != summary.get("timestamp"):
            errors.append("app/data/results.json timestamp differs from results/summary.json — re-run run_all.py")
    else:
        errors.append("missing app/data/results.json")
    cs = summary.get("collision_scale", {})
    if cs and cs.get("strings_tested", 0) < 1000:
        errors.append("collision_scale strings_tested unexpectedly small")
    latent = summary.get("latent_sweep", {}).get("results", [])
    if latent:
        held = [r.get("test_eval", {}).get("string_exact_match_rate") for r in latent]
        if any(v is None for v in held):
            errors.append("latent_sweep missing test_eval rates")
    rep = summary.get("representation_comparison", {}).get("results", {})
    det = rep.get("A_deterministic_inverse", {}).get("test_eval", {})
    if det.get("count") != 46:
        errors.append(f"expected 46 test strings for deterministic inverse, got {det.get('count')}")
    return errors


def main() -> int:
    errors: list[str] = []

    rc = subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=ROOT)
    if rc != 0:
        errors.append("unit tests failed")

    for name in REQUIRED_RESULT_FILES:
        if not (RESULTS / name).exists():
            errors.append(f"missing results/{name}")

    if not NETLIFY.exists():
        errors.append("missing netlify.toml")
    else:
        toml = NETLIFY.read_text()
        if 'publish = "app"' not in toml:
            errors.append("netlify.toml must publish app/")

    summary_path = RESULTS / "summary.json"
    summary: dict = {}
    if summary_path.exists():
        try:
            summary = _load_json(summary_path)
        except json.JSONDecodeError as e:
            errors.append(f"invalid summary.json: {e}")
        for key in REQUIRED_SUMMARY_KEYS:
            if key not in summary:
                errors.append(f"summary missing key: {key}")

    errors.extend(check_consistency(summary))
    errors.extend(check_claims())

    if errors:
        print("RESEARCH CHECK: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("RESEARCH CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
