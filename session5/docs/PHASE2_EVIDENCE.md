# Phase 2 — Decision Evidence Tables

Extended evidence for §6.1. Each allocation includes candidates A/B/C with explicit rejection rationale.

---

## General Web — 38% selected

| Candidate | % | Pros | Cons | Benchmark / proxy | Verdict |
|-----------|--:|------|------|-------------------|---------|
| A | 35 | More room for Indic/code lanes | EN-IN anchor weak; estimated MMLU −1.5 | TruthfulQA-IN regression risk | **Rejected** |
| **B** | **38** | EN-IN anchor; MMLU stable; fits P1 two-phase (840B) | Less Indic headroom vs 35% | MMLU, HellaSwag stable in M8 | **Selected** |
| C | 42 | Strong world knowledge headline | Indic-Faithfulness −0.06 (S3 M6); code stability drop | IndicGLUE −2 est. | **Rejected** |

**Sensitivity:** 36–40% safe. Below 36%: common-sense QA drop. Above 40%: faithfulness penalty.

---

## Code — 10% selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 8 | Frees 2pp for Indic/reasoning | SWE-bench lite −4 est.; India stack underrepresented | **Rejected** |
| **B** | **10** | HumanEval+ stable; compile-gated synth fits supply | −2pp vs Session 3 12% plan | **Selected** |
| C | 12 | Max code benchmark scores | EN contamination via code repos; Indic −0.06 | **Rejected** |
| D | 16 | LeetCode / CP peak | Competitive programming overfit; faithfulness collapse | **Rejected** |

**Sensitivity:** 9–11% safe. proxy-1b: code −1.54pp at chosen mix (within −2pp accept).

---

## Indic Multilingual — 22% selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 18 (floor only) | Supply-safe; no repeat stress | ta/te/ml underfit; misses MCDA-7 deployment | **Rejected** |
| **B** | **22** | MCDA-7; Dravidian 28.4%; proxy +2.99pp | Verified tier needs 6.9× repeat | **Selected** |
| C | 28 | Strong IndicGLUE optics | Verified shortage; synth >cap risk | **Rejected** |
| D | 39 (census Hindi) | Population narrative | Hindi web noise overfit; tier imbalance | **Rejected** |

**Sensitivity:** 20–24% safe. Below 20%: tail collapse. Above 24%: verified repeat >10×.

---

## Reasoning — 6% selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 4 (fold into STEM) | Simpler mixture accounting | Gov/Edu 0.78 lane invisible to scheduler | **Rejected** |
| **B** | **6** | Explicit RBI/GST/UPI CoT; assignment requirement | 4× repeat; verifier bottleneck | **Selected** |
| C | 10 | Strong policy QA scores | Supply ~16B only; wishful without verifier | **Rejected** |

**Sensitivity:** 5–7%. Confidence **Low** — needs 3B GPU validation.

---

## Agentic — 4% selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 2 | Saves budget for web/code | Recovery stays ~55%; fails L3 gate | **Rejected** |
| **B** | **4** | Pretrain docs + 10B post-train ToolLoop path to 0.70 | Trace supply thin (~37B) | **Selected** |
| C | 8 | High tool-call accuracy | Starves web diversity; post-train redundant | **Rejected** |

**Sensitivity:** 3–5%. Floor 3% protects minimum.

---

## Long Context — 3% selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 1 | Minimal compute | Needle@32k fails legal SLA | **Rejected** |
| **B** | **3** | Kanoon 4× repeat feasible; 4k→32k ramp in P2 | Sparse legal supply (~10B) | **Selected** |
| C | 6 | Strong recall headline | Compute ~2× at 32k; batch OOM risk | **Rejected** |

**Sensitivity:** 2–4%. proxy-3b needle 0.777 at chosen ramp.

---

## Annealing — 10% / 120B selected

| Candidate | % | Pros | Cons | Verdict |
|-----------|--:|------|------|---------|
| A | 5 (60B) | Faster time-to-ship | WSD cooldown insufficient for faithfulness | **Rejected** |
| **B** | **10** | Faithfulness polish; verified Indic boost in cooldown | 120B less active mixture learning | **Selected** |
| C | 15 (180B) | Maximum end-of-train quality | Delays effective India-heavy P2 tokens | **Rejected** |

**Sensitivity:** 8–12%. Locked until month 14 (separate ACL).

---

## Always-On Floor — Indic 18% selected

| Candidate | Floor | Pros | Cons | Verdict |
|-----------|------:|------|------|---------|
| A | None | Maximum OPUS efficiency | Tail langs starve (proxy-3b A vs C) | **Rejected** |
| **B** | **18%** | proxy-3b tail +4.52pp; ta/te protected | May retain low-utility shards | **Selected** |
| C | 22% | Matches lane allocation | Over-retention; squeezes web/code | **Rejected** |

**Note:** Floor ≤ lane allocation (18% ≤ 22%) — structural invariant in `validate_mixture.py`.
