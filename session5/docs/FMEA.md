# Failure Mode & Effects Analysis (FMEA)

| ID | Failure Mode | Cause | Effect | Severity | Detection | Mitigation |
|----|--------------|-------|--------|----------|-----------|------------|
| F-001 | Indic tail language collapse | EN/code gradient dominates | ta/te/ml underperform on portals | 9 | Per-lang IndicGLUE at 25/50/75% | Always-on floor 18%; Phase-2 MCDA boost |
| F-002 | Wishful agentic accounting | 4% lane, <8B trace supply | Recovery stays at 55% ReAct baseline | 8 | Supply audit vs repeat_factor | Post-train +10B ToolLoop; floor 3% |
| F-003 | Long-context recall cliff | 32k without curriculum | Needle@128k fails legal SLA | 8 | Needle eval per context stage | 4k→32k ramp; floor 2%; Kanoon 4× repeat |
| F-004 | Synthetic faithfulness drop | Global synth >8% | Indic-Faithfulness −4.2 | 9 | L11 leakage probe | Hard cap 6% (72B); Indic synth 10% of lane only |
| F-005 | Ataavi starvation | 4M tokens vs 21.6B slot | Domain QA random | 6 | Species held-out eval | Cleaning sprint 47M→120M; synth lexicon-gated |
| F-006 | Phase-2 mixture shock | Abrupt India-heavy at 70% | Loss spike, instability | 7 | Loss monitor + grad norm | 20B token ramp between phases |
| F-007 | OPUS deletes protected data | Utility model blind to Indic | Floors breached silently | 8 | Floor assertion in selector | OPUS cannot cross always-on floors |
| F-008 | Translationese in Indic | 15% translated tier | Unnatural register on gov chat | 6 | Human adequacy sample | Cap translated at 15%; verify parallel quality |
| F-009 | Code LeetCode overfit | CP >2% in code slice | SWE-bench fails on repos | 7 | Subsource audit | Repos 42%, CP cap 2% |
| F-010 | Anneal reserve spent early | Ops mistake in selector | No cooldown quality gain | 7 | Token ledger per phase | Reserve locked until month 14 |
| F-011 | Hinglish license revocation | ToS change on social crawl | CS Index regression | 8 | Legal review quarterly | BPO licensed backup (8B supply) |
| F-012 | Reasoning verifier bottleneck | CoT synth 3.5× repeat | Reasoning lane starved | 7 | Verifier pass rate dashboard | Prioritize RBI/GST verified CoT |
| F-013 | Benchmark contamination | Cleaning gap | Inflated offline scores | 9 | 13-gram decontam (S4 pipeline) | Extend decontam to all lanes |
| F-014 | GPU-hour overrun | >1.2T effective tokens | $679k budget breach | 8 | Billable hours ±3% gate | No dynamic mixture (M8 rejected) |

**RPN priority:** F-001, F-004, F-013 (Severity ≥9) — mitigated before full-scale commit.
