"""Evaluation hierarchy: capability → offline → real-world → human → business."""

from __future__ import annotations

from typing import Any


HIERARCHY: list[dict[str, Any]] = [
    {
        "capability": "coding",
        "offline": "HumanEval+, SWE-bench lite",
        "real_world": "Fix issue in India OSS repo (sandbox)",
        "human": "Senior dev rates patch correctness",
        "deployment": "PR merge rate in pilot",
        "business": "Dev hours saved / SME",
    },
    {
        "capability": "agentic",
        "offline": "Tool accuracy, planning depth",
        "real_world": "Gov form fill + UPI query agent",
        "human": "Task completion blind rating",
        "deployment": "Agent recovery rate ≥0.70",
        "business": "Support ticket deflection %",
    },
    {
        "capability": "indic_languages",
        "offline": "IndicGLUE, FLORES",
        "real_world": "State portal chat in ta/te/hi",
        "human": "Native speaker adequacy",
        "deployment": "Indic-Faithfulness ≥0.82",
        "business": "Regional adoption rate",
    },
    {
        "capability": "code_switch",
        "offline": "CS test set (Hinglish/Tanglish)",
        "real_world": "BPO script adherence",
        "human": "CS naturalness score",
        "deployment": "Code-Switch Index ≥0.75",
        "business": "NPS in multilingual support",
    },
    {
        "capability": "math_science",
        "offline": "GSM8K, JEE-style set",
        "real_world": "NCERT tutor session",
        "human": "Teacher rubric score",
        "deployment": "Answer accuracy on syllabus",
        "business": "Ed-tech partner renewal",
    },
    {
        "capability": "gov_edu",
        "offline": "Policy QA held-out",
        "real_world": "RBI circular summarization",
        "human": "Domain expert fact-check",
        "deployment": "Gov/Edu readiness ≥0.78",
        "business": "Gov pilot contract milestone",
    },
    {
        "capability": "safety",
        "offline": "Toxigen, jailbreak suite",
        "real_world": "Election/religious harm probes",
        "human": "Red-team pass rate",
        "deployment": "L1 safety gate pass",
        "business": "Regulatory approval",
    },
    {
        "capability": "inference",
        "offline": "Tokens/s on L40S",
        "real_world": "p99 latency Mumbai edge",
        "human": "UX satisfaction <800ms",
        "deployment": "India Inference Efficiency ≥0.65",
        "business": "₹/query vs generic tokenizer",
    },
    {
        "capability": "hallucination",
        "offline": "TruthfulQA-IN",
        "real_world": "RAG over gov corpus",
        "human": "Citation fidelity audit",
        "deployment": "Hallucination rate <8%",
        "business": "Trust score in pilot",
    },
    {
        "capability": "long_context",
        "offline": "Needle-in-haystack 128k",
        "real_world": "Contract clause retrieval",
        "human": "Lawyer review sample",
        "deployment": "Recall@32k docs",
        "business": "Legal tech SLA",
    },
]


def compute_eval_hierarchy() -> dict[str, Any]:
    return {
        "hierarchy": HIERARCHY,
        "capability_count": len(HIERARCHY),
        "ship_gate": "L1 safety pass + L2 aggregate ≥0.78 + L3 agent_recovery ≥0.70 + hallucination <8%",
        "kill_criteria": [
            "Indic-Faithfulness <0.75 after 2 retrain cycles",
            "Agent recovery <0.55 at month 16",
            "Year-2 TCO savings <10% vs generic tokenizer",
        ],
    }
