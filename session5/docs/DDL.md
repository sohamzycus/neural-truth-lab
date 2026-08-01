# Design Decision Ledger (DDL)

| ID | Decision | Value | Evidence | Benchmark | Experiment | Risk | Confidence |
|----|----------|-------|----------|-----------|------------|------|------------|
| DDL-001 | Active pretrain budget | 1,080B (90%) | Session 3 Chinchilla-optimal 1.2T | — | proxy-1b | Anneal too short if <8% | High |
| DDL-002 | Anneal reserve | 120B (10%) | WSD cooldown literature; M8 matrix | L2 aggregate | proxy-1b §anneal | Quality cliff if <8% | High |
| DDL-003 | Web/General NL share | 38% | EN-IN anchor for code-switch stability | MMLU, TruthfulQA-IN | proxy-1b | EN dominance hurts Indic | Med |
| DDL-004 | Indic multilingual share | 22% | MCDA-7 sharpening (S3); not census 39% | IndicGLUE, FLORES | proxy-3b | Tail langs underfit | High |
| DDL-005 | Indic verified tier | 35% of Indic | Gov/NCERT license audit | Indic-Faithfulness ≥0.82 | proxy-3b | Supply only 12B raw | Med |
| DDL-006 | Indic unverified tier | 40% of Indic | Largest real supply (420B crawl) | IndicGLUE | proxy-3b | Web noise | Med |
| DDL-007 | Indic translated tier | 15% of Indic | STEM/gov gap filler | FLORES | proxy-3b | Translationese | Med |
| DDL-008 | Indic synthetic tier | 10% of Indic | Below 6% global cap | Faithfulness probe | proxy-3b | −4.2 if >8% global | High |
| DDL-009 | Code share | 10% (down from S3 12%) | Room for reasoning+agentic lanes | HumanEval+, SWE-bench | proxy-1b | Code gradient dominance | High |
| DDL-010 | STEM share | 8% | JEE/NEET + NCERT alignment | GSM8K, JEE held-out | proxy-3b | GSM8K-only trap | High |
| DDL-011 | Reasoning share | 6% | Explicit CoT lane (S5 requirement) | Gov/Edu 0.78 | proxy-3b | Verifier bottleneck | Med |
| DDL-012 | Agentic pretrain share | 4% | S3: 12B docs + 10B post-train traces | Recovery ≥0.70 | proxy-3b | Trace supply thin | Med |
| DDL-013 | Long-context share | 3% | Kanoon 2.8B supply → 4× repeat | Needle 32k | proxy-3b | Recall collapse w/o curriculum | High |
| DDL-014 | Conversation/CS share | 5% | Hinglish 28B supply | CS Index ≥0.75 | proxy-3b | ToS revocation | Med |
| DDL-015 | Planning share | 2% | JSON plan depth gate | Plan audit | proxy-3b | Implicit planning only | Med |
| DDL-016 | Ataavi domain share | 2% | S4 corpus; India-primary nature | Species ID QA | cleaning sprint | 5400× repeat until M8 | Low→Med |
| DDL-017 | Indic always-on floor | 18% | Selector cannot cross | IndicGLUE per-lang | proxy-3b | OPUS starvation | High |
| DDL-018 | Agentic always-on floor | 3% | Protected from downsampling | Tool accuracy | proxy-3b | — | High |
| DDL-019 | CS always-on floor | 4% | Deployment signal | CS Index | proxy-3b | — | High |
| DDL-020 | LC always-on floor | 2% | 4k→32k ramp needs exposure | Needle | proxy-3b | — | High |
| DDL-021 | Two-phase curriculum | 70/20/10 | M8 matrix winner (S3) | L2 aggregate | proxy-1b | Phase-2 shock | High |
| DDL-022 | Context length ramp | 4k→8k→16k→32k | RoPE extension without collapse | Needle 128k | proxy-3b | OOM at 32k batch | Med |
| DDL-023 | OPUS protected lanes | 4 lanes | Always-on floors | Per-lane delta | proxy-1b | Over-retention | Med |
| DDL-024 | Synthetic global cap | 6% (72B) | M6 matrix: >8% → −4.2 faithfulness | Faithfulness | proxy-3b | Cost pressure | High |
| DDL-025 | Difficulty D1–D4 split | 30/35/25/10 | Curriculum literature | MMLU by difficulty | proxy-1b | Adversarial overfit | Med |
| DDL-026 | Reasoning R0–R3 split | 40/30/20/10 | Latency vs depth tradeoff | GSM8K by length | proxy-3b | Ultra underrepresented | Med |
