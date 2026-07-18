# India-First 40B

**Forty billion parameters. One deployment constraint: India.**

**Production:** https://india-40b-erav5.netlify.app  
**Netlify site:** `india-40b-erav5` (site id `f2cbbb76-00cd-4b8a-ab7b-d1861387ef06`)  
**Repository:** `session3/`

An internal-style research proposal for a $100M India-first foundation model — with every number traceable to Python quantitative models, not LLM estimates.

---

## What makes this submission unique

1. **Spec-driven quant pipeline** — `specs/` → `models/india40b/*.py` → `derive_all.py` → `data/derived/*.json`. Change a spec, regenerate; the web viewer updates via `export_report_data.py`.

2. **Live decision stress-testing** — MCDA matrices with adjustable criterion weights. Prove tokenizer and architecture choices survive weight perturbation.

3. **Fertility is a budget line item** — Interactive calculator links tokenizer design (session2 SamaBPE lineage) to **$13.5M annual TCO savings** at Year-2 scale.

4. **Anti-population-weighting thesis, visualized** — MCDA vs census allocation: Hindi 39.2% → 17.9%, Dravidian languages gain collectively.

5. **Evaluation pyramid with release gates** — 5 derived scorecards gate L1→L4 release; not benchmark-chasing.

6. **Explorable model, not a PDF** — 13-chapter proposal + 8 architecture diagrams + interactive quant widgets in one viewer.

---

## Quick start

```bash
python3 scripts/derive_all.py
python3 scripts/verify.py
python3 scripts/export_report_data.py
cd web && npm ci && npm run dev
```

## Deploy (Netlify)

| Setting | Value |
|---------|--------|
| **Base directory** | `session3/web` |
| **Build command** | *(empty — uses netlify.toml)* |
| **Publish** | `dist` |

After frontend changes:

```bash
cd session3
python3 scripts/export_report_data.py
cd web && npm ci && npm run build:netlify
git add dist/ public/ && git commit && git push
# Netlify → Clear cache and deploy
```

Prebuilt `dist/` is committed (session2 pattern — avoids Netlify npm install timeouts).

---

## Design choices

| Choice | Rationale |
|--------|-----------|
| Python quant → static JSON → React | Auditable; web never invents numbers |
| Prebuilt dist on Netlify | Proven session2 pattern |
| Chapter nav over infinite scroll | How researchers skim proposals |
| Interactive matrices + fertility calc | Passive report → explorable model |
| Internal memo aesthetic | Rigor over marketing gradients |
| MCDA sharpening (not census) | Deployment signals > population |

---

## Narrative spine

Objectives → pretraining data → cleaning → tokenizer → fertility → inference cost → post-training → alignment → agents → evaluation → India deployment.

## Key numbers (derived)

- 40B dense · 128k vocab · 1.2T tokens
- Hindi 17.9% · EN-IN 17.4% (MCDA, not census)
- $100M / 18 months
- 22% inference savings vs generic tokenizer
