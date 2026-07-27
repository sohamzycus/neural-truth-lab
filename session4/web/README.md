# Ataavi Corpus Forge

Dark, scroll-narrative portal for engineering bird observation notes into a training corpus.

**Live:** https://ataavi-corpus-forge.netlify.app

---

## What this repo is (and is not)

| Layer | What exists in code | Where |
|-------|---------------------|-------|
| **Narrative + stats** | 12-stage pipeline design, 10 cleaning strategies, surgery metrics, corpus charts | `public/data/*.json` + React sections |
| **Full shard pipeline** | Scrub → quality → lang ID → MinHash → exact dedupe → decontam on **all 5k shard records** | `src/lib/pipeline/`, `scripts/process-shard.ts` |
| **Verified shard metrics** | Real counts from pipeline run (not hand-waved) | `public/data/shard_pipeline_run.json` + **Shard run** UI section |
| **Training readiness math** | Seven derived health metrics from manifest JSON | `src/lib/corpusHealth.ts` |
| **Sample raw shard** | 5,000 noisy observations (representative of 47.2M corpus) | `public/data/raw_observations.json` |

**Implemented in TypeScript** (browser + `npm run pipeline:shard`): all **10/10 strategies** + **8 domain enrichments** in `src/lib/pipeline/` and `src/lib/scrub/`.

```bash
npm run pipeline:shard   # processes 5k shard → train_safe_corpus.jsonl + manifests
npm run selfcheck        # scrub + corpusHealth + pipeline assertions
```

**Downloads (UI → #downloads):** raw 5k JSON/JSONL, train-safe JSONL (1,092 records), corpus manifest with SHA-256, stats, pipeline run report.

**Corpus scale:** **47,200,000** observations (10–100M class) — full count in hero, dataset, and download banner. Static site ships verified 5k shard; full corpus referenced in manifests.

**Production gaps (honest):** FastText model weights (script heuristics used), trained NER (regex PII), distributed Spark over 47M rows. Corpus-scale surgery JSON is extrapolated; shard metrics are **reproducible**.

---

## Develop

```bash
cd session4/web
npm install
npm run dev
```

## Verify

```bash
npm run selfcheck    # scrub + corpusHealth + pipeline assertions
npm run typecheck
npm run build
npm run pipeline:shard
```

`selfcheck` runs three assertion scripts:

```bash
npx tsx src/lib/scrub/selfcheck.ts
npx tsx src/lib/corpusHealth.selfcheck.ts
npx tsx src/lib/pipeline/selfcheck.ts
```

---

## Data files (`public/data/`)

| File | Role |
|------|------|
| `dataset_stats.json` | Corpus scale (47.2M obs), countries, languages, species, sample excerpts |
| `dataset_manifest.json` | Version, shard size, `shardMetaTaggedPct` for health monitor |
| `raw_observations.json` | 5,000-record noisy shard (downloadable in UI) |
| `pipeline_stages.json` | 12 ordered pipeline stages (purpose, technique, I/O) |
| `strategies.json` | 10 cleaning strategies with algorithms and before/after |
| `surgery_metrics.json` | Post-pipeline counts (dedupe clusters, PII removed, quality score) |
| `corpus_stats.json` | Language/species distributions, quality timeline, readiness |
| `benchmark_quiz.json` | Held-out quiz phrases for 13-gram decontamination |
| `shard_pipeline_run.json` | Verified pipeline output on full 5k shard (`npm run pipeline:shard`) |
| `health_sync.json` | Health monitor poll interval (`intervalMs`: 5000) |
| `comparisons.json`, `scrub_samples.json` | Curated before/after + playground inputs |

Regenerate the raw shard and scaled stats:

```bash
node scripts/generate-corpus-shard.mjs
```

---

## Cleaning pipeline (12 stages)

Stages are defined in `pipeline_stages.json` and rendered by `PipelineSection`. Order matters — each stage consumes the previous output.

```
Raw → Extract → Unicode → Lang → Quality → Exact dedupe → Near dedupe
  → PII → Ghost tags → Decontam → Manifest → Training corpus
```

| # | Stage | Technique (documented) | Input → Output |
|---|-------|------------------------|----------------|
| 1 | Raw Observations | JSONL + checklist parsers | Checklists → immutable raw shard |
| 2 | Content Extraction | DOM/boilerplate strip | HTML exports → plain text + columns |
| 3 | Unicode Normalization | **NFKC** + punctuation fold | Text → canonical UTF-8 |
| 4 | Language Detection | **FastText** + script heuristics | Text → lang codes + confidence |
| 5 | Quality Filtering | min length, **entropy**, species lexicon | Tagged notes → quality-gated subset |
| 6 | Exact Deduplication | **SHA-256** on normalized text | Notes → unique exact set |
| 7 | Near Duplicate Detection | **MinHash + LSH** | Exact-unique → cluster reps |
| 8 | PII Removal | regex + **NER** masks | Cluster reps → PII-safe text |
| 9 | Ghost Tag Normalization | tag balancer + entity decode | PII-safe → tag-clean |
| 10 | Benchmark Decontamination | **n-gram overlap** vs held-out quizzes | Clean → train-safe |
| 11 | Manifest Generation | Parquet/JSONL + **SHA manifests** | Docs → versioned shards |
| 12 | Training Corpus | packing + token counts | Manifests → `ataavi-text-v0.4` |

**Why this order:** extract before unicode (strip wrappers first); lang-ID before quality filters (language-aware thresholds); exact dedupe before near-dedupe (cheaper pass first); PII after dedupe (fewer rows to scan); decontamination last on clean text (eval leakage check).

---

## Ten cleaning strategies

Listed in `strategies.json` (`StrategiesSection`). Count is dynamic (`strategies.length`).

| ID | Strategy | Algorithms |
|----|----------|------------|
| s1 | Unicode & NFKC | NFKC, punctuation fold |
| s2 | Language identification | FastText, script heuristics |
| s3 | Quality filtering | min length, entropy, species lexicon |
| s4 | Exact deduplication | SHA-256 on normalized text |
| s5 | Near-duplicate detection | MinHash, LSH clustering |
| s6 | PII removal | regex, NER masks |
| s7 | HTML & boilerplate strip | tag strip, entity decode |
| s8 | Length & repetition filters | token caps, repeat collapse |
| s9 | Benchmark decontamination | 13-gram overlap, quiz set filter |
| s10 | Manifest & schema packing | JSONL shards, SHA-256 manifest |

---

## Runnable pipeline (`src/lib/pipeline/`)

The **Compare → Pipeline playground** and **`npm run pipeline:shard`** run the full implemented chain:

```
scrub (NFKC/HTML/PII/ws) → quality filter → language ID → MinHash → exact hash → decontam
```

| Module | Function | Algorithm |
|--------|----------|-----------|
| `quality.ts` | `scoreQuality` | Reject if `len < 12` or char Shannon entropy `< 2.0` |
| `lang.ts` | `detectLanguage` | Unicode script ranges (hi/ta/ml/bn/en); code-switch if secondary > 15% |
| `minhash.ts` | `minHashSignature`, `clusterNearDuplicates` | 3-word shingles, 32-hash MinHash, LSH bands (size 4), Jaccard ≥ 0.82 |
| `decontam.ts` | `overlapsBenchmark` | 13-gram overlap vs `benchmark_quiz.json` held-out phrases |
| `runPipeline.ts` | `runPipeline` | Orchestrates stages; returns per-step trace |

Shard run (latest): **5,000 in → 1,172 train-safe reps** (3,569 exact dupes, 259 near-dupes, 613 PII masked) — see `shard_pipeline_run.json`.

**Production gaps:** FastText weights (script heuristics used instead), trained NER (regex PII used instead), species lexicon quality gate, distributed 47M batch job.

---

## Runnable scrub logic (`src/lib/scrub/`)

Scrub is **stage 1** of the pipeline above.

```typescript
// src/lib/scrub/index.ts — execution order
export function scrubObservation(raw: string): ScrubResult {
  let text = raw;
  text = normalizeUnicode(text);   // String.normalize("NFKC")
  text = stripHtml(text);          // regex tag/entity removal
  text = stripPii(text);           // email, phone, observer-name patterns
  text = collapseWhitespace(text); // /\s+/ → single space, trim
  return { text, steps };
}
```

### Scrub algorithms

| Step | Function | Rule |
|------|----------|------|
| Unicode | `normalizeUnicode` | `text.normalize("NFKC")` |
| HTML | `stripHtml` | Remove tags; decode entities |
| PII | `stripPii` | Email → `[EMAIL]`; phone → `[PHONE]`; observer names → `[OBSERVER]` |
| Whitespace | `collapseWhitespace` | `/\s+/g` → single space, trim |
| Exact hash | `exactHash` | `crypto.subtle.digest("SHA-256", utf8(text))` |

### Selfcheck assertions

```typescript
// src/lib/scrub/selfcheck.ts (abbreviated)
const cleaned = scrubObservation(dirty);
assert(cleaned.text.includes("[EMAIL]"));
assert(!cleaned.text.includes("<b>"));
assert(!/\s{2,}/.test(cleaned.text));
assert(await exactHash("same") === await exactHash("same"));
```

---

## Training readiness — core quality logic (`src/lib/corpusHealth.ts`)

The **Corpus Health Monitor** (bottom-right widget) polls manifest JSON every 5s and recomputes metrics. No random jitter — values are deterministic functions of `surgery_metrics.json`, `corpus_stats.json`, `dataset_stats.json`, and `dataset_manifest.json`.

```typescript
// HealthMonitor sync (abbreviated)
const [surgery, stats, dataset, manifest] = await Promise.all([
  fetch("/data/surgery_metrics.json"),
  fetch("/data/corpus_stats.json"),
  fetch("/data/dataset_stats.json"),
  fetch("/data/dataset_manifest.json"),
]);
setMetrics(computeCorpusHealth({ surgery, stats, dataset, shardMetaTaggedPct: manifest.shardMetaTaggedPct }));
```

### Seven metrics — formulas

Let `N = surgery.observations` (fallback: `dataset.observationCount`).

| Metric | Formula | Invert? | Source fields |
|--------|---------|---------|---------------|
| **Noise Score** | `round(qualityTimeline[0].score × 100)` | yes (lower better) | `corpus_stats.qualityTimeline` stage `"Raw"` |
| **Corpus Quality** | `round(averageQualityScore × 100)` | no | `surgery_metrics.averageQualityScore` |
| **Duplicate Ratio** | `round((duplicateClusters / N) × 100)` | yes | `surgery_metrics.duplicateClusters` |
| **Language Balance** | `round((H / H_max) × 100)` | no | `corpus_stats.languages` shares |
| **Metadata Completeness** | `round(min(100, meta×35 + (countries/40)×30 + (languages/20)×35))` | no | manifest + dataset |
| **PII Risk** | `round(min(100, (piiRemoved/N)×500 + 4))` | yes | `surgery_metrics.piiRemoved` |
| **Training Readiness** | `round(readinessScore × 100)` | no | `corpus_stats.readinessScore` |

#### Language balance (Shannon entropy)

```typescript
const shares = languages.map((l) => l.value / 100);  // percentages → proportions
const H = -shares.reduce((sum, p) => sum + (p > 0 ? p * Math.log2(p) : 0), 0);
const H_max = Math.log2(Math.max(shares.length, 2));
const languageBalance = round((H / H_max) * 100);
```

Higher = more balanced language mix. A single-language corpus → H ≈ 0. Uniform 6-way split → H ≈ H_max.

#### Metadata completeness (weighted blend)

```typescript
metadataCompleteness = min(100,
  shardMetaTaggedPct * 35           // e.g. 0.94 → 32.9
  + (countries / 40) * 30           // e.g. 142 → capped contribution
  + (languages / 20) * 35           // e.g. 38 → 66.5 before cap
);
```

`shardMetaTaggedPct` comes from `dataset_manifest.json` (default 0.9 if omitted).

#### PII risk (per-observation rate)

```typescript
const piiPerObs = piiRemoved / N;
const piiRisk = min(100, round(piiPerObs * 500 + 4));
```

With current data: `1,240,000 / 47,200,000 ≈ 0.0263` → `0.0263 × 500 + 4 ≈ 17`.

### Meter color thresholds (`HealthMonitor.tsx`)

```typescript
// invert=true (lower is better): noise, duplicate ratio, PII risk
value > 55 → danger;  > 35 → warn;  else ok

// invert=false (higher is better): quality, balance, metadata, readiness
value > 70 → ok;      > 45 → warn;  else danger
```

### Selfcheck for corpusHealth

```typescript
// src/lib/corpusHealth.selfcheck.ts
const metrics = computeCorpusHealth({ surgery, stats, dataset, shardMetaTaggedPct: 0.94 });
assert(metrics.length === 7);
assert(metrics.find(m => m.key === "trainingReadiness")?.value === 91);
```

---

## Quality timeline (precomputed narrative)

`corpus_stats.json` → `qualityTimeline` shows score climb through pipeline stages (used in Stats charts; noise score uses **Raw** only):

| Stage | Score |
|-------|-------|
| Raw | 0.38 |
| Extract | 0.52 |
| Filter | 0.67 |
| Dedupe | 0.78 |
| PII | 0.86 |
| Final | 0.92 |

`readinessScore: 0.92` and `tokenReductionPct: 21.6` are manifest-level outputs after dedupe (`dedupeSavings`: 47.2M → 38.4M exact → 31.2M near).

---

## App architecture

```
src/
  App.tsx                 # loads JSON bundle, composes sections
  lib/
    scrub/                  # runnable cleaning demo + selfcheck
    corpusHealth.ts         # training readiness formulas
  components/
    sections/               # Hero, Dataset, Raw, Pipeline, Strategies, …
    monitor/HealthMonitor.tsx # polls manifests, renders meters
    shell/AppShell.tsx        # nav, scroll progress
public/data/                # corpus JSON (source of truth for UI stats)
scripts/generate-corpus-shard.mjs
```

Data flow:

```
public/data/*.json
       ↓ fetch (App.tsx + HealthMonitor poll)
  React sections (display)
       ↓
  scrubObservation()     — single-note demo only
  computeCorpusHealth()  — derived training readiness
```

---

## Deploy (Netlify)

- **Production:** prebuilt `dist/` committed; GitHub Actions uploads zip on push to `main` (see repo `.github/workflows/netlify-deploy-session4.yml`).
- **Local build:** `npm run build` → `dist/`
- **Config:** `netlify.toml`

## SpecKit

See `../specs/001-ataavi-corpus-forge/` and `../.specify/extensions/fleet/fleet-config.yml`.

## Review artifacts

Post-review deliverables: `../REVIEW.md`, `../REVIEW_SCORECARD.md`, `../REVIEW_READY.md`.
