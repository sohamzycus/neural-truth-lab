# Implementation Plan — India-First 40B

## Phase 0: Scaffold (Day 1–2)
- Folder tree, constitution, master spec
- `data/inputs/*.json` with 7-factor language signals

## Phase 1: Quantitative Models (Day 3–6)
- `vocab_derivation.py`, `language_weights.py`, `fertility_model.py`
- `training_cost.py`, `inference_cost.py`, `data_mix.py`, `scorecards.py`
- `scripts/derive_all.py`, pytest suite

## Phase 2: Report Content (Day 7–12)
- 13 chapters with chapter template
- Numbers injected from `data/derived/` via verify script

## Phase 3: Diagrams & Matrices (Day 13–15)
- 8 Mermaid diagrams
- 12 decision matrix JSON files

## Phase 4: Web Viewer (Day 16–18)
- Vite + React report viewer
- Decision matrix explorer, quant widgets

## Phase 5: Verification (Day 19–20)
- `verify.py`, frozen `results/baseline-derivation-v1.json`
- README reproduction commands
