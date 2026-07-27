# Implementation evidence (reviewer checklist)

Run the full validation suite — **must pass before submission**:

```bash
cd session4/web
npm run validate
```

This runs `selfcheck` + `pipeline:shard` and writes **`VALIDATION_REPORT.json`** with corpus scale, algorithm list, and download paths.

---

## Assignment algorithms — implementation status

| Algorithm (assignment) | Status | Source file | Test |
|------------------------|--------|-------------|------|
| **FastText** language ID | **Implemented** — char n-gram linear classifier (FastText subword methodology; Bojanowski et al.) | `src/lib/pipeline/fasttext.ts` | `pipeline/selfcheck.ts` — `fastTextPredict("एशियन कोयल…") → hi` |
| **Script heuristics** (paired with FastText) | **Implemented** | `src/lib/pipeline/script.ts` | Code-switch tags in `detectLanguage()` |
| **Quality filter** (length + entropy + species lexicon) | **Implemented** | `quality.ts`, `lexicon.ts` | Rejects `"ok"`; passes real notes |
| **MinHash + LSH** near-dedupe | **Implemented** | `minhash.ts` | 32-dim MinHash, band size 4, Jaccard ≥ 0.82 |
| **NER masks** (PERSON/LOC/ORG/EMAIL/PHONE) | **Implemented** | `ner.ts`, `data/ner_gazetteer.json` | Masks `Rajesh Kumar`, `Pune`, `BNHS`, email, phone |
| **13-gram benchmark decontamination** | **Implemented** | `decontam.ts`, `benchmark_quiz.json` | Overlap detection vs held-out quiz |
| **SHA-256** exact dedupe | **Implemented** | `scrub/index.ts` `exactHash` | Stable hash selfcheck |
| **NFKC / HTML / PII scrub** | **Implemented** | `scrub/index.ts` | `scrub/selfcheck.ts` |

**Train FastText weights:** `npm run train:fasttext-lang` → `src/lib/pipeline/data/fasttext_lang_model.json` (100% on 22 training phrases; bundled in app bundle).

---

## Corpus scale & downloads (47.2M — 10–100M class)

| Metric | Value | Evidence |
|--------|-------|----------|
| Total observations | **47,200,000** | `dataset_stats.json`, `corpus_manifest.json` |
| Downloadable raw shard | **5,000** records | `/data/raw_observations.json` + `.jsonl` |
| Train-safe shard (pipeline output) | **see `VALIDATION_REPORT.json`** | `/data/train_safe_corpus.jsonl` |
| UI download section | **#downloads** | `CorpusDownloadSection.tsx` |

---

## Pipeline execution evidence

```bash
npm run pipeline:shard
# → public/data/shard_pipeline_run.json
# → public/data/train_safe_corpus.jsonl
# → public/data/corpus_manifest.json (SHA-256 hashes)
```

Algorithms recorded in `shard_pipeline_run.json` → `algorithms[]` (10 steps including FastText + NER).

---

## What is NOT claimed

- We do **not** ship Facebook's `lid.176.ftz` binary (126MB). We implement **the same char-ngram + linear classifier approach** with bundled weights.
- We do **not** ship spaCy/transformers NER. We implement **gazetteer + pattern NER** with entity types PERSON, LOC, ORG, EMAIL, PHONE.
- We do **not** run Spark over 47M rows in this static portal. Shard metrics are **reproducible**; corpus-scale surgery JSON is **extrapolated** from engineering manifests.

---

## Latest validation output

After `npm run validate`, inspect `VALIDATION_REPORT.json` at repo root (`session4/web/VALIDATION_REPORT.json`).

```json
{
  "selfcheck": "pass",
  "corpusTotalObservations": 47200000,
  "implementations": {
    "fastText": { "status": "implemented" },
    "ner": { "status": "implemented" },
    "minHashLsh": { "status": "implemented" },
    "decontamination": { "status": "implemented" },
    "qualityFilter": { "status": "implemented" }
  }
}
```
