"""Capability → data token mapping (from inputs/capabilities.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_capabilities(inputs_dir: Path | None = None) -> dict[str, Any]:
    root = inputs_dir or Path(__file__).resolve().parents[2] / "data" / "inputs"
    return json.loads((root / "capabilities.json").read_text())


def compute_capability_data(inputs_dir: Path | None = None) -> dict[str, Any]:
    cap = load_capabilities(inputs_dir)
    caps = cap["capabilities"]
    coding = next(c for c in caps if c["id"] == "coding")
    return {
        "capabilities": caps,
        "capability_count": len(caps),
        "code_subsources_percent": {
            "repositories": 42,
            "documentation": 18,
            "issues": 12,
            "stackoverflow": 10,
            "tests": 8,
            "rfcs_package_specs": 5,
            "verified_synthetic": 5,
        },
        "code_subsources_tokens_b": {
            k: round(coding["pretrain_tokens_b"] * v / 100, 1)
            for k, v in {
                "repositories": 42,
                "documentation": 18,
                "issues": 12,
                "stackoverflow": 10,
                "tests": 8,
                "rfcs_package_specs": 5,
                "verified_synthetic": 5,
            }.items()
        },
        "india_first_sources": [
            {"domain": "UPI/NPCI", "tokens_b": 2.1, "license": "public_spec"},
            {"domain": "GST portal", "tokens_b": 1.8, "license": "gov_open"},
            {"domain": "RBI circulars", "tokens_b": 3.2, "license": "licensed"},
            {"domain": "NCERT textbooks", "tokens_b": 4.5, "license": "ncert_open"},
            {"domain": "Judiciary (Kanoon subset)", "tokens_b": 2.8, "license": "commercial"},
            {"domain": "Hinglish social (filtered)", "tokens_b": 28.0, "license": "tos_restricted"},
        ],
    }
