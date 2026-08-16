# Dynamic Reversible Kronecker

> Can a deterministic byte-derived representation eliminate fixed-window waste while remaining learnably reversible?

| Problem | Status |
|---------|--------|
| **Problem 3** — Dynamic representation | **SUPPORTED** |
| **Problem 5** — Learned reversibility | **NOT DEMONSTRATED** |
| **Problem 4** — Fourier comparison | **PARTIAL** |

**Interactive lab:** [dynamic-kronecker-session7.netlify.app](https://dynamic-kronecker-session7.netlify.app) (deploy with `bash scripts/deploy_netlify.sh`)  
**Local:** `python -m http.server 8765 --directory app`  
**Repository:** [neural-truth-lab/session7](https://github.com/sohamzycus/neural-truth-lab/tree/main/session7)

---

## TL;DR

### What we changed

Fixed 32-byte representation → **Dynamic variable-length representation**

### Why

Fixed representation wastes capacity and truncates some multilingual inputs.

### What we measured

- collisions
- truncation
- deterministic inversion
- learned reconstruction
- latent capacity (16–1024-d)
- decoder architecture (MLP / sequence / autoregressive)
- multilingual behavior (EN / HI / TE / BN)
- Fourier baseline

### What happened

**Dynamic representation (measured):**

- No collisions observed in **3,408** tested strings
- **0%** truncation in tested corpus buckets
- **100%** deterministic held-out inversion (46/46 test strings)

**Learned reconstruction (measured):**

- **0%** held-out exact across latent dimensions 16–1024
- **0%** held-out exact across tested decoder families

### What we conclude

Dynamic Kronecker solves the **representation / truncation problem** in the tested setup.

It does **not** yet solve **learned reversibility**.

> **We solved the fixed-window representation problem. The learned inverse remains unsolved.**

---

## The central research question

**How much can deterministic byte features be compressed before learned reversibility breaks?**

---

## The most important distinction

There are **two different notions of reversibility**:

### A. Information-preserving representation

```text
Dynamic features → deterministic inverse → original bytes
```

**Result:** 100% exact on 46 held-out test strings (measured).

The deterministic inverse proves the representation retains enough information for exact recovery through the **explicitly defined inverse**. It does **not** prove that a neural decoder can learn that inverse.

### B. Learned reconstruction

```text
Dynamic features → neural decoder → reconstructed bytes
```

**Result:** 0% held-out exact (measured under current decoder, training budget, and dataset).

```text
THE INFORMATION IS PRESENT.
THE LEARNED INVERSE CANNOT RECOVER IT.
```

---

## Assignment traceability

| Assignment | Our approach | Experiment | Result | Status |
|------------|--------------|------------|--------|--------|
| Problem 3 | Dynamic Kronecker | truncation / collision / waste | 0% dynamic trunc.; 0 collisions in 3,408 strings | **SUPPORTED** |
| Problem 5 | Learned inverse | reconstruction / latent sweep / decoder ablation | 0% held-out exact | **PARTIAL** |
| Problem 4 | Fourier baseline | collision scale | magnitude collisions remain; phase reduces | **PARTIAL** |

---

## Experiment table

| Experiment | Purpose | Dataset | Metric | Result | Interpretation |
|------------|---------|---------|--------|--------|----------------|
| Fixed vs dynamic truncation | Problem 3 | EN/HI/TE/BN corpus | truncation rate | Fixed: up to 28.57% (Telugu); Dynamic: 0% | Dynamic removes observed truncation |
| Collision scale | Injectivity | 3,408 strings | collision groups | Dynamic: 0; Fixed: 2; Fourier mag: 5 | No collisions observed for dynamic in this test |
| Deterministic inverse | Information retention | 46 test strings | exact match | 100% | Bytes explicitly recoverable |
| Latent sweep | Capacity threshold | 312 train / 46 test | held-out exact | 0% at all dims 16–1024 | No positive capacity threshold observed under tested setup |
| Representation paths | Compression vs decode | 46 test | test exact | Inverse 100%; full+decoder 0%; 64-d+decoder 0% | Compression + current decoder fails |
| Decoder ablation | Decoder bottleneck? | 46 test | held-out exact | MLP/seq/AR all 0% | Changing decoder family did not recover exact reconstruction |
| Length generalization | Long strings | test by byte bucket | exact by length | ~0% all buckets | No length bucket recovered |
| Language generalization | UTF-8 scripts | EN/HI/TE/BN | waste / trunc / recon | Telugu max fixed trunc 28.57% | Script byte-length affects fixed window |
| Fourier comparison | Problem 4 | 3,408 strings | collisions | mag: 5 groups; phase: 1 group | Phase helps; does not establish universal injectivity |

All values loaded from `results/*.json` — regenerate with `python experiments/run_all.py`.

---

## Reversibility Frontier

Latent dimension sweep (position-MLP decoder, 2,000 training steps, seed 42):

| Latent dim | Held-out exact |
|------------|----------------|
| 16 | 0% |
| 32 | 0% |
| 64 | 0% |
| 128 | 0% |
| 256 | 0% |
| 512 | 0% |
| 1024 | 0% |

**Mandatory interpretation:** This experiment did **not** identify a positive capacity threshold. The result is bounded by the tested decoder, training budget, data, and optimization setup.

---

## What Failed?

| Method | Held-out exact |
|--------|----------------|
| Deterministic inverse | **100%** |
| Learned inverse (64-d) | **0%** |
| Full 771-d features + decoder | **0%** |
| 128-d / 256-d / 512-d / 1024-d + decoder | **0%** |
| Position MLP decoder | **0%** |
| Sequence decoder | **0%** |
| Autoregressive decoder | **0%**** |

**Conclusion:** The current evidence rules out a simple "64 dimensions are too small" explanation, but does **not** isolate the remaining bottleneck.

Possible causes (not established individually): representation geometry, decoder inductive bias, optimization, loss formulation, training budget, dataset size, projection, positional structure.

---

## IMPORTANT — Deterministic inverse disclaimer

> The 100% deterministic inverse result is **not** a learned reconstruction result.
>
> It verifies that the Dynamic Kronecker representation retains enough information for an explicitly defined inverse.
>
> The neural decoder experiment asks a harder question: *Can a learned model discover that inverse?*
>
> **Current answer:** Not under the tested setup.

---

## Parameter accounting

| Component | Trainable | Deterministic state |
|-----------|-----------|---------------------|
| Standard embedding (V=64, D=64) | 4,096 | 0 |
| Dynamic representation | 0 | 771 features |
| Dynamic + 64-d decoder (MLP) | 31,329 | 771 |
| Dynamic + full-feature decoder | 99,908 | 771 |

Representation-only and end-to-end costs are **different quantities**. Never compare embedding-table parameters to decoder parameters without stating what is included.

---

## Web Demo

### Netlify (production)

Site: **dynamic-kronecker-session7**  
URL: https://dynamic-kronecker-session7.netlify.app  
Dashboard: https://app.netlify.com/projects/dynamic-kronecker-session7

```bash
cd session7
cp results/summary.json app/data/results.json   # sync latest metrics
bash scripts/deploy_netlify.sh                    # requires: netlify login
```

`netlify.toml` publishes `app/` as a static site (no build step).

### Local

```bash
python -m http.server 8765 --directory app
# open http://localhost:8765
```

---

## How to reproduce

```bash
cd session7
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py              # tests + experiments + research_check (~13 min)
python scripts/research_check.py
bash scripts/deploy_netlify.sh  # optional: push webapp to Netlify
python -m http.server 8765 --directory app
```

**Netlify:** see [Web Demo](#web-demo) above.

---

## What we learned

1. Fixed-window representation creates measurable waste and truncation.
2. Dynamic representation eliminates observed truncation in the tested corpus.
3. Dynamic representation retained enough information for deterministic exact inversion.
4. Learned reconstruction is dramatically harder than deterministic inversion.
5. Increasing latent dimension alone did not solve the problem.
6. Changing decoder family alone did not solve the problem.
7. The remaining bottleneck is not yet isolated.
8. Tiny LM usefulness (H8) remains **NOT RUN**.

---

## What we do not claim

- Universal collision-freedom (only tested sets reported)
- That 64-d is insufficient (no tested dim achieved held-out exact)
- That the decoder cannot work with more training / different setup
- Production-ready reversible embeddings
- LM benefit (H8 not run)

---

## Repository structure

```text
session7/
├── app/                 # static research webapp
├── experiments/         # reproducible runners
├── results/             # generated JSON (source of truth)
├── scripts/research_check.py
├── src/                 # encoders, decoders, metrics
└── netlify.toml
```

---

## Hypothesis scoreboard

| ID | Status |
|----|--------|
| H1 Dynamic reduces waste | SUPPORTED |
| H2 Fewer observed collisions | SUPPORTED |
| H3 Deterministic inversion | SUPPORTED |
| H4 Learned reconstruction depends on capacity | PARTIAL |
| H5 Tested capacity threshold observed | NOT SUPPORTED |
| H6 Decoder family recovered more | NOT SUPPORTED |
| H7 Fourier ordering | PARTIAL |
| H8 LM usefulness | NOT RUN |

See `results/summary.json` → `hypotheses` for evidence objects.

---

## Adversarial review notes

**Reviewer 1 (ML):** 46 test strings is small for strong generalization claims — we report measured rates without overclaiming. Deterministic inverse is explicit parsing, not learning. 2,000 steps may be insufficient — stated as limitation.

**Reviewer 2 (Architecture):** Positional info is in per-byte features; decoder receives projected latent + position index. Deterministic state ≠ trainable parameters.

**Reviewer 3 (ERA):** Problem 3 supported with evidence; Problem 5 partial with visible failure analysis. Reproducible via `run_demo.py`. Webapp loads live JSON.

---

*All metrics from `results/summary.json`. Last regenerated: see `timestamp` field.*
