# India-First 40B Foundation Model — Master Specification

**Status:** Superseded for report structure by `specs/004-report-v2/spec.md` (V2 report live)  
**Constitution:** session3/.specify/memory/constitution.md

## Objective

Produce an internal research proposal titled **"Designing an India-First 40B Foundation Model"** — a 12–15 page document for senior AI researchers evaluating a ~$100M training program.

## Audience

Senior AI researchers, infrastructure leads, and policy stakeholders deciding whether to fund India-first foundation model training.

## Narrative Spine

Objectives → pretraining data → cleaning → tokenizer → language fertility → inference economics → post-training → alignment → agentic capabilities → evaluation → India deployment → budget/risk.

Seven assignment areas (pretrain data, post-train data, RL/alignment, cleaning, evaluation, tokenizer, fertility) are **one coherent design narrative**, not independent sections.

## Model Decisions (Locked)

| Area | Decision |
|------|----------|
| Architecture | 40B dense decoder, GQA, 128k vocab |
| Pretrain | 1.2T tokens; 82% NL / 12% code / 4% math / 6% synthetic cap |
| Tokenizer | Unigram+BPE hybrid, 128k derived allocation |
| Language weights | 7-factor MCDA (Hindi **17.9%**, EN-IN **17.4%**) |
| Cleaning | 6-stage pipeline, MinHash 0.90 dedup |
| Post-train | SFT → DPO; RLHF for safety slice only |
| Agents | ToolLoop: plan → execute → reflect |
| Eval | Pyramid gating L1–L3 required to ship |
| Deploy | India edge INT4 40B + distilled 8B blend |

## Artefacts

- `report/REPORT.md` — canonical 12–15 page source
- `report/chapters/*.md` — per-chapter sources
- `data/derived/*.json` — all quantitative outputs
- `diagrams/src/*.mmd` — 8 pipeline diagrams
- `data/inputs/matrices/M*.json` — 12 decision matrices
- `web/` — static report viewer with interactive matrices

## Acceptance

- [ ] `python scripts/derive_all.py` completes without error
- [ ] `python scripts/verify.py` passes (report numbers == derived JSON)
- [ ] `cd web && npm run build` succeeds
- [ ] All 13 chapters follow chapter template
- [ ] 8 diagrams present in `diagrams/src/`
- [ ] 12 decision matrices in `data/inputs/matrices/`
