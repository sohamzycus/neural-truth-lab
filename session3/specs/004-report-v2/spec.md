# Spec 004 — Report V2 Redesign

**Status:** Approved  
**Supersedes:** Report structure in `001-india40b/spec.md` §Narrative Spine (content only; locked decisions unchanged)  
**Constitution:** P1–P6 apply; all numbers from `data/derived/*.json`

## Objective

Redesign `report/REPORT.md` so evaluators repeatedly conclude: *"These people derived every decision."*  
Optimize for reasoning depth, tradeoff analysis, and India-first differentiation — not page count.

## Assignment Mapping

| Assignment question | Primary chapter(s) | Derived artefact |
|---------------------|-------------------|------------------|
| What data and why? | §3 Data Derivation Atlas | `capability_data.json` |
| How clean? | §4 Industrial Cleaning DAG | `cleaning_pipeline.json` |
| How evaluate? | §9 Evaluation Hierarchy | `eval_hierarchy.json`, `scorecards.json` |
| Tokenizer & fertility | §5–§6 | `vocab_allocation.json`, `vocab_size_tradeoff.json`, `fertility_projections.json` |

## Narrative Spine (mandatory)

```
Mission → Capabilities → Training Objectives → Data → Cleaning → Tokenizer
  → Training Strategy → Alignment → Evaluation → Deployment → Risks
```

Every chapter MUST cite upstream dependency and downstream consumer (e.g. "§3 code repos → §4 L12 compilation → §8 agent eval").

## Chapter Template (P6 extended)

Each chapter:

1. Problem Statement  
2. Design Options  
3. Tradeoff Analysis  
4. Decision Matrix (reference M1–M12)  
5. Chosen Design  
6. Rejected Alternatives  
7. Expected Failure Modes  
8. Validation Plan  
9. Future Improvements  

## Report Structure

| § | Title | Pages (target) |
|---|-------|----------------|
| 0 | One-Page Engineering Summary | 1 |
| 1 | Mission & Capability Contract | 1 |
| 2 | Model Architecture & Training Objectives | 1 |
| 3 | Data Derivation Atlas (Q1) | 2–3 |
| 4 | Industrial Cleaning DAG (Q2) | 1.5 |
| 5 | Tokenizer & Vocabulary Economics (Q4) | 1.5 |
| 6 | Fertility → Context → Inference TCO (Q4) | 1 |
| 7 | Training Strategy | 0.5 |
| 8 | Post-Training, Alignment & Agentic Recipes | 1.5 |
| 9 | Evaluation Hierarchy (Q3) | 1.5 |
| 10 | India Deployment & Frugal Operations | 1 |
| 11 | Budget, Risks & Kill Criteria | 1 |
| A | Decision Log | 0.5 |

## Locked Decisions (unchanged)

- 40B dense GQA, 1.2T tokens, 82/12/4/6 slice mix  
- 128k Unigram+BPE tokenizer  
- MCDA-7 language weights (Hindi **17.9%**, EN-IN **17.4%**)  
- 16-stage cleaning, MinHash 0.90  
- SFT → DPO; RLHF safety slice only  
- Pyramid eval L1–L3 ship gate  

## Acceptance

- [ ] `specs/004-report-v2/assessments.md` documents brutal-review remediation  
- [ ] 12 matrices `M1.json`–`M12.json` present  
- [ ] `derive_all.py` emits 11 derived JSON files  
- [ ] `verify.py` passes  
- [ ] Report sections 0–11 + appendix follow chapter template  
