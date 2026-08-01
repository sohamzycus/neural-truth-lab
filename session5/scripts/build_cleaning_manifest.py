#!/usr/bin/env python3
"""Build cleaning manifest for starved mixture lanes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "mixture_spec.json").read_text())
S4_STATS = Path(__file__).resolve().parents[2] / "session4" / "web" / "public" / "data" / "corpus_stats.json"
OUT = ROOT / "data" / "cleaning_manifest.json"


def main() -> int:
    s4 = json.loads(S4_STATS.read_text()) if S4_STATS.exists() else {"readinessScore": 0.92}
    starved = []
    for lane in SPEC["capability_lanes"]:
        gap = lane.get("supply_gap") or lane.get("cleaning_target")
        max_repeat = max((d.get("repeat_factor", 1) for d in lane.get("datasets", [])), default=1)
        if max_repeat > 2 or gap:
            starved.append(
                {
                    "lane_id": lane["id"],
                    "budget_tokens_b": lane["tokens_b"],
                    "max_repeat_factor": max_repeat,
                    "gap": gap or f"repeat up to {max_repeat}x",
                    "cleaning_actions": _actions(lane["id"]),
                    "priority": _priority(max_repeat),
                }
            )

    starved.sort(key=lambda x: -x["max_repeat_factor"])
    manifest = {
        "version": "v1",
        "session4_readiness": s4.get("readinessScore"),
        "session4_observations": 47_200_000,
        "target_observations": 120_000_000,
        "pipeline": "session4/web — FastText, MinHash, NER, decontam",
        "starved_lanes": starved,
    }
    OUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {OUT} ({len(starved)} starved lanes)")
    return 0


def _priority(repeat: float) -> str:
    if repeat >= 100:
        return "P0"
    if repeat >= 3:
        return "P1"
    return "P2"


def _actions(lane_id: str) -> list[str]:
    actions = {
        "domain_ataavi": [
            "Scale S4 pipeline 47.2M → 120M observations",
            "Run npm run validate in session4/web",
            "Regenerate train_safe_corpus.jsonl",
        ],
        "reasoning": [
            "Build RBI/GST CoT verifier pipeline",
            "Human audit 8% of synthetic CoT",
        ],
        "long_context": [
            "Expand Kanoon licensed subset",
            "Generate needle-in-haystack synth pairs",
        ],
        "agentic": [
            "Collect sandbox traces (assistant-loss only)",
            "Extend UPI/NPCI agent playbooks",
        ],
        "planning": [
            "Human audit workflow plans (8%)",
        ],
        "indic_multilingual": [
            "Gov/NCERT verified pack cleaning sprint",
            "Extend S4 FastText + script heuristics to gov shards",
        ],
    }
    return actions.get(lane_id, ["Extend S4 cleaning pipeline to lane datasets"])


if __name__ == "__main__":
    sys.exit(main())
