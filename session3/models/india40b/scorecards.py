"""Original evaluation scorecards."""

from __future__ import annotations

from typing import Any


SCORECARDS: list[dict[str, Any]] = [
    {
        "id": "indic_faithfulness",
        "name": "Indic-Faithfulness Score",
        "definition": "Fraction of Indic responses preserving factual claims from source context (human+LLM-judge)",
        "gate": 0.82,
        "weight": 0.25,
    },
    {
        "id": "code_switch_robustness",
        "name": "Code-Switch Robustness Index",
        "definition": "Accuracy on Hinglish/Tanglish mixed prompts vs monolingual baseline",
        "gate": 0.75,
        "weight": 0.15,
    },
    {
        "id": "gov_edu_readiness",
        "name": "Government/Education Readiness",
        "definition": "Composite: form-filling accuracy, policy Q&A, textbook alignment",
        "gate": 0.78,
        "weight": 0.20,
    },
    {
        "id": "agent_recovery_rate",
        "name": "Agent Recovery Rate",
        "definition": "Fraction of tool-use trajectories that recover after first tool failure",
        "gate": 0.70,
        "weight": 0.20,
    },
    {
        "id": "inference_efficiency",
        "name": "India Inference Efficiency",
        "definition": "Quality-adjusted tokens/$ at p50 latency < 800ms on L40S",
        "gate": 0.65,
        "weight": 0.20,
    },
]


def compute_scorecards() -> dict[str, Any]:
    return {
        "scorecards": SCORECARDS,
        "pyramid_levels": {
            "L1_safety": ["toxicity", "bias_india", "pii_leakage", "jailbreak_resistance"],
            "L2_indic_fidelity": ["indic_faithfulness", "code_switch_robustness", "gov_edu_readiness"],
            "L3_agents": ["agent_recovery_rate", "tool_use_accuracy", "planning_depth"],
            "L4_benchmarks": ["mmlu", "gsm8k", "humaneval", "indicglue"],
        },
        "ship_gate": "L1 pass + L2 aggregate ≥ 0.78 + L3 agent_recovery ≥ 0.70",
    }
