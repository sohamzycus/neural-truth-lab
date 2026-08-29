# Loss Forensics Lab

## Can we trust a falling loss curve?

This is ERA V5 Session 9: an educational notebook that investigates **what loss actually measures** in language-model training — not how to make the curve look good.

> We are not trying to make the loss look good. We are trying to prove that the loss **means** what we think it means.

**Observe the tensors. Read the strings. Challenge the loss.**

---

## The experiment

A small GPT-2 / nanoGPT-style transformer:

| Hyperparameter | Value |
|----------------|-------|
| Vocabulary | 50,257 (GPT-2 BPE via tiktoken) |
| Block size | 64 |
| Layers | 4 |
| Heads | 4 |
| Embedding dim | 128 |
| Parameters (tied head) | 7,234,432 |

**Dataset:** `HuggingFaceFW/fineweb` `sample-10BT` (streamed), tokenized with tiktoken GPT-2. A deterministic **FALLBACK** text bundle is used automatically when Hugging Face is unreachable.

---

## The core pipeline

```
tokens → embeddings → causal transformer → hidden states
    → output head → logits → softmax / log-probabilities
    → target token → cross-entropy loss → backprop → update
```

Every major transition is printed, decoded to strings where it matters, and checked independently.

---

## What I verified

| Claim | Test | Evidence | Conclusion |
|-------|------|----------|------------|
| Shapes correct | Forward pass shape print | B=2, T=64, C=128, V=50257 | PASS |
| Shift correct | Decoded input→target table | String alignment matches t+1 | PASS |
| Padding excluded | Mask vs unmasked CE | 7 → 1 contributing tokens | PASS |
| Boundary excluded | Pack two docs, mask boundary | Loss 10.8770 → 10.8464 | PASS |
| Random baseline sane | Untrained CE vs ln(V) | loss=10.39, PPL≈32,494 (4% error vs ln V) | PASS |
| Tied head saves V×C | Param count diff | Δ=6,432,896 = 50257×128 | PASS |
| Chunked CE equivalent | Ordinary vs chunked loss | diff=9e-8 | PASS |
| Chunking reduces peak | Analytical logits bytes | 202MB vs 3.2MB (63×) | PASS |
| t+2 aligned | String table A→C, B→D… | Explicit alignment shown | PASS |
| Wrong shift reduces loss | Train backward shift | Final loss 7.68 < correct 7.85 | DEMONSTRATED |

---

## The most important discovery

### "The loss was beautiful. The model was wrong."

Training with **wrong** alignment (`logits[:,1:]` vs `tokens[:,:-1]`) still produces a **decreasing** loss — and in our run, a **lower** final loss than the correct shift:

| Training alignment | Final loss (15-step demo) |
|--------------------|---------------------------|
| Correct (t+1) | 7.8466 |
| Wrong (predict past) | 7.6763 |

String forensics on `"Viewing the results"` after wrong-shift training:

| Pos | Input | Model predicts | Correct next |
|-----|-------|----------------|--------------|
| 1 | `ing` | ` homophobia` | ` the` |
| 2 | ` the` | `canon` | ` results` |

The model was rewarded for predicting **context/past tokens**, not the future. **A falling loss curve does not prove the training objective is correct.**

---

## Loss Truth Triangle

```
             LOSS VALUE
                /\
               /  \
              /    \
             /      \
    TENSOR SHAPES —— STRING SEMANTICS
```

1. **Shapes** — dimensions line up (necessary but insufficient)
2. **Strings** — we predict the intended next token (catches silent bugs)
3. **Loss** — scalar behaves as expected (ln(V) baseline, masking, chunking)

All three are required.

---

## Results (latest clean run)

**Run config:** seed=1337, device=mps, PyTorch 2.13.0, Python 3.14.2

### Seven numbers panel

1. **Tensor shapes:** B=2, T=64, C=128, V=50257
2. **String shift:** PASS
3. **Padding contributing tokens:** 7 → 1
4. **Document boundary loss:** 10.8770 → 10.8464
5. **Untrained loss / PPL:** 10.3888 / 32,494 (expected ln(V)≈10.825, V≈50,257)
6. **Tied vs untied params:** 7,234,432 vs 13,667,328 (Δ=6,432,896)
7. **CE memory (analytical):** ordinary=202,636,224 bytes, chunked=3,216,448 bytes, ratio=63.0×

### Dual-head experiment (DEMONSTRATION RUN — 15 steps)

| Metric | Value |
|--------|-------|
| t+1 loss | 8.0963 |
| t+2 loss | 8.0628 |
| Combined | 16.1591 |
| Gap (t2−t1) | −0.0334 |

**Observed:** t+2 was *slightly lower* than t+1 in this short run — not universally harder. Gap depends on data, init, LR, and duration.

### Wrong-shift trap

| Metric | Value |
|--------|-------|
| Correct-shift final loss | 7.8466 |
| Wrong-shift final loss | 7.6763 |

---

## Memory experiment

Full-vocabulary cross-entropy materializes a `(N, V)` logits matrix. With B=16, T=64, V=50257:

- **Ordinary CE peak (analytical):** 202,636,224 bytes (~193 MB)
- **Chunked CE peak (chunk=16):** 3,216,448 bytes (~3 MB)
- **Loss difference:** 0.00000009 (numerically identical)

Chunking changes **peak residency**, not the mathematical objective.

---

## What surprised me

1. **Wrong-shift loss beat correct-shift loss** in our demo — the easier wrong task optimized faster, making the trap more convincing than if wrong-shift had stalled.
2. **t+2 was not higher than t+1** after 15 steps — the hypothesis "t+2 is always harder" did not hold in this tiny run.
3. **Perplexity was below V** (32k vs 50k) at init — small-init logits are near-uniform but not perfectly uniform; still within 15% tolerance of ln(V).

---

## Reproduce

### Google Colab

1. Upload `session9/` or open from GitHub.
2. Install deps: `pip install torch tiktoken datasets matplotlib`
3. Run all cells top-to-bottom (~5–15 min on GPU; longer on CPU).

FineWeb streaming works on Colab when Hugging Face is reachable. If not, the notebook labels and uses **FALLBACK** automatically.

### Local

```bash
cd session9
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook Session_9_Loss_Forensics_Lab.ipynb
```

Bundled `data/tiktoken_cache/` provides GPT-2 BPE files for offline tiktoken (no OpenAI blob download).

Optional: `FORCE_FALLBACK=1` skips Hugging Face entirely for offline runs.

---

## Files

| File | Description |
|------|-------------|
| `Session_9_Loss_Forensics_Lab.ipynb` | Main notebook (executed, with outputs) |
| `README.md` | This document |
| `requirements.txt` | Python dependencies |
| `data/tiktoken_cache/` | Bundled GPT-2 BPE vocab for offline tiktoken |
| `build_notebook.py` | Notebook generator (dev helper) |

---

## What could have gone wrong?

See the notebook's troubleshooting section for perplexity spikes, masking bugs, boundary indices, chunked CE mismatches, and t+2 alignment checks.

---

## Final status (verified clean run)

```
Tensor shapes                 PASS
String shift                  PASS
Padding mask                  PASS
Document boundary             PASS
Perplexity sanity             PASS
Tied vs untied                PASS
Chunked cross entropy         PASS
t+2 head                      PASS
Wrong-shift demonstration     PASS

LOSS TRUTH TRIANGLE — Shapes + Strings + Loss — VERIFIED
```
