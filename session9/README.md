# Loss Forensics Lab

## Can we trust a falling loss curve?

> **The optimizer succeeded. We gave it the wrong job.**

A language model can produce a beautiful loss curve while learning the wrong task. This notebook treats the loss computation as something to **investigate**, not something to blindly trust.

> **Observe the tensors. Read the strings. Challenge the loss.**

---

## The question

What exactly happens between:

```text
tokens → hidden → logits → loss
```

—and how can we **build evidence** that the objective is correct?

A loss curve only tells us the optimizer is reducing the objective we **supplied**. It does **not** by itself prove that objective is the task we **intended**.

---

## How to read this notebook

Every experiment follows the same forensic pattern:

**CLAIM → TEST → EVIDENCE → CONCLUSION**

For example:

> Claim: the target is the next token.

→ Decode the input and target strings.

→ Compare them side by side.

→ If `"India"` maps to `" is"`, the alignment is plausible.

The notebook deliberately avoids trusting a single number.

---

## The core pipeline

```text
tokens (B×T)
  → Transformer → hidden (B×T×C)
  → output head → logits (B×T×V)
  → shift: predictions[:,:-1] vs targets[:,1:]
  → cross-entropy → scalar loss → backprop → update
```

Every major transition is printed, decoded to strings where it matters, and checked independently.

---

## What I verified

| Check | Method | Status |
|---|---|---|
| Tensor dimensions | Shape inspection | PASS |
| Target shift | Decoded string pairs | PASS |
| Padding mask | Valid-target count | PASS |
| Document boundary | Exact boundary + loss/count | PASS |
| Uniform baseline | Equal-logit test | PASS |
| Random init sanity | Actual loss/PPL | PLAUSIBLE |
| Tied head saves V×C | Parameter count | PASS |
| Chunked CE equivalence | Numerical loss match | PASS |
| Chunking peak memory | Analytical/CUDA evidence | PASS |
| t+2 alignment | String pairs | PASS |
| Wrong-shift trap | Loss curve + strings | DEMONSTRATED |

---

## Results

> **Dataset note:** Latest clean local verification used the deterministic **FALLBACK** dataset with `FORCE_FALLBACK=1`. The notebook prints `data source`, `FALLBACK used`, `documents`, and `total tokens`. Numbers below are from that run — **not** from FineWeb streaming.

**Run config:** seed=1337, device=mps, PyTorch 2.13.0 (from notebook `torch.__version__` output)

### Tensor shapes

B=2, T=64, C=128, V=50257

### Cross entropy (chunked vs ordinary)

| Metric | Value |
|---|---|
| Ordinary loss | 10.371709 |
| Chunked loss | 10.371709 |
| Absolute difference | 9×10⁻⁸ |
| Relative difference | 8.76×10⁻⁹ |

### String shift

Decoded table confirms `input[i] → target[i+1]` on `"The capital of India is New Delhi"` — **PASS**

### Padding

7 total target positions → 1 valid after synthetic PAD mask (`token_id=0` is a **lab convention**, not native GPT-2 PAD).

### Document boundary

Loss 10.8770 → 10.8464; contributing targets 12 → 11 (one artificial cross-document prediction removed). The target-count drop is deterministic; loss direction depends on model/data.

### Perplexity — two baselines

| Baseline | Loss | PPL | Status |
|---|---:|---:|---|
| **A — Uniform logits** (mathematical) | 10.824905 | 50,257 | PASS |
| **B — Random init transformer** | 10.3888 | 32,493.9 | PLAUSIBLE |

**Uniform logits:** `loss = ln(V)`, `PPL = exp(loss) = V` — exact mathematical result.

**Random init:** PLAUSIBLE — **loss is ~4.03% below ln(V)**; the resulting PPL is ~32.5K rather than exactly V. A randomly initialized transformer is not required to produce perfectly uniform logits; this check detects gross implementation problems, not exact equality.

### Tied vs untied

7,234,432 vs 13,667,328 parameters — difference **6,432,896 = V×C**

### Chunked cross entropy

Logits tensor for ordinary CE: shape **(N, V)** where **N = B×(T−1) = 16×63 = 1008** positions.

| Estimate | Bytes | Formula |
|---|---:|---|
| Ordinary peak | 202,636,224 | 1008 × 50257 × 4 (float32) |
| Chunked peak (chunk=16) | 3,216,448 | 16 × 50257 × 4 (float32) |
| Ratio | **63.0×** | |

Labelled **ANALYTICAL LOGIT MEMORY ESTIMATE (CPU/MPS)** — not CUDA allocator measurements.

### t+1 vs t+2 (15-step demonstration)

| Step | t+1 | t+2 | diff |
|---:|---:|---:|---:|
| 0 | 10.8361 | 10.8341 | −0.0020 |
| 3 | 9.1533 | 9.1445 | −0.0088 |
| 7 | 8.6107 | 8.5822 | −0.0285 |
| 11 | 8.3612 | 8.3285 | −0.0327 |
| 15 | 8.0963 | 8.0628 | −0.0334 |

In this short demonstration run, t+2 finished slightly below t+1. This is an observation from this configuration, not a universal property of prediction horizons.

---

## The signature finding

# The optimizer succeeded. We gave it the wrong job.

**Nothing about the tensors is inherently invalid; the error is semantic alignment.**

| Objective | Relationship |
|---|---|
| **CORRECT** | context → **future** token |
| **WRONG** | context → token **already in** context |

| Alignment | Final loss (15 steps) |
|---|---:|
| Correct next-token | 7.8466 |
| Wrong previous-token | **7.6763** |

String forensics on `"Viewing the results"` after wrong-shift training:

| Input context | Model predicts | Intended next | Wrong objective rewards |
|---|---|---|---|
| `'ing'` | `' homophobia'` | `' the'` | `'View'` |
| `' the'` | `'canon'` | `' results'` | `'ing'` |

**Evidence chain:** loss decreases → looks successful → inspect strings → target comes from past context → objective is wrong.

---

## Random-target control

Five-step micro-demo on the same backbone:

| Objective | Start | End | Interpretation |
|---|---:|---:|---|
| Correct t+1 | 10.641 | 8.319 | Learns useful structure |
| Wrong previous-token | 10.633 | 8.469 | Learns a valid but unintended objective |
| Random target | 10.850 | 10.842 | No meaningful structured learning |

The control sharpens the central point: optimization success and task correctness are separate questions. The wrong objective can learn because it is still a coherent objective.

---

## The Loss Truth Triangle

```
                    LOSS VALUE
                       /\
                      /  \
                     /    \
            TENSOR SHAPES — STRINGS
```

**TRUSTWORTHY LOSS = SHAPES + STRING SEMANTICS + NUMERICAL SANITY**

---

## What this proves / does not prove

### Perplexity

- **Proves:** Uniform-logit baseline gives `loss = ln(V)`, `PPL = V`.
- **Does not prove:** Every randomly initialized transformer must have PPL exactly equal to V.

### Padding

- **Proves:** Masked PAD targets do not contribute to the averaged loss.
- **Does not prove:** Masking must numerically decrease loss.

### Document boundary

- **Proves:** The artificial cross-document target can be excluded from the loss.
- **Does not prove:** Packed documents are inherently superior to separate sequences.

### Chunked CE

- **Proves:** Chunked implementation reproduces the same scalar objective while reducing peak vocabulary-logit residency.
- **Does not prove:** Chunking makes the entire training system use 63× less memory.

### t+2

- **Proves:** A second prediction horizon can be implemented and compared.
- **Does not prove:** t+2 is universally harder than t+1.

### Wrong shift

- **Proves:** Incorrect target alignment can produce decreasing loss while optimizing the wrong task.
- **Does not prove:** Every incorrect objective will always achieve lower loss.

---

## What surprised me

The most striking result: the deliberately wrong previous-token objective achieved a **lower** final loss than correct next-token training (7.6763 vs 7.8466). Nothing crashed. The bug was visible only after inspecting decoded targets.

Also notable: t+2 was **not** higher than t+1 after 15 steps — challenging the intuition that farther prediction horizons should necessarily have higher loss in a short demonstration run.

**Observation ≠ universal law.**

---

## Memory

Full-vocabulary CE materializes an **(N, V)** logits tensor where **N = B×(T−1)** for shifted CE.

With B=16, T=64, V=50257: N=1008, ordinary analytical peak = **202,636,224 bytes** (~193 MB); chunked (chunk=16) = **3,216,448 bytes** (~3 MB). Chunking reduces **peak logit residency**, not the mathematical need to score all positions.

---

## t+2

This run demonstrated that a second horizon can be trained and compared. It does not establish universal behaviour — only that gap direction depends on configuration, data, and training duration.

---

## Limitations

- **15-step demonstration runs** — mechanism over model quality
- **Small model** (~7.3M parameters, tied head)
- **FALLBACK local verification** — latest audited run used `FORCE_FALLBACK=1`, not FineWeb; Colab may stream FineWeb when reachable
- **MPS analytical memory estimates** — labelled ANALYTICAL LOGIT MEMORY ESTIMATE; not CUDA allocator measurements
- **Synthetic PAD token** (id=0) for controlled masking — not native GPT-2 PAD
- **t+2 gap direction** is configuration-dependent

---

## Reproducibility

```bash
cd session9
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Generate notebook from source
python build_notebook.py

# 2. Execute all cells (clean kernel — no hidden state)
FORCE_FALLBACK=1 MPLBACKEND=Agg jupyter nbconvert \
  --to notebook --execute Session_9_Loss_Forensics_Lab.ipynb \
  --output Session_9_Loss_Forensics_Lab.ipynb \
  --ExecutePreprocessor.timeout=600

# Or interactively:
jupyter notebook Session_9_Loss_Forensics_Lab.ipynb
```

- Bundled `data/tiktoken_cache/` for offline GPT-2 BPE
- FineWeb streams when Hugging Face is reachable (omit `FORCE_FALLBACK=1`)
- `build_notebook.py` **generates** the `.ipynb`; it does **not** execute it

---

## Files

| File | Description |
|---|---|
| `Session_9_Loss_Forensics_Lab.ipynb` | Main notebook (executed) |
| `README.md` | This document |
| `requirements.txt` | Dependencies |
| `build_notebook.py` | Notebook generator (source of truth) |
| `data/tiktoken_cache/` | Bundled GPT-2 BPE vocab |

---

## Final status

```text
============================================================
LOSS FORENSICS LAB — FINAL STATUS
============================================================
Tensor shapes                 PASS
String shift                  PASS
Padding mask                  PASS
Document boundary             PASS
Uniform baseline              PASS
Random-model sanity           PLAUSIBLE
Tied vs untied                PASS
Chunked cross entropy         PASS
t+2 head                      PASS
Wrong-shift demonstration     DEMONSTRATED

============================================================
LOSS TRUTH TRIANGLE
============================================================
Shapes + Strings + Numerical Sanity
                         VERIFIED
============================================================
Observe the tensors.
Read the strings.
Challenge the loss.
============================================================
```

> A loss is an instrument. Before trusting the reading, verify that the instrument is measuring what you think it is measuring.

> The optimizer can only optimize the objective we give it. The first responsibility of the engineer is to make sure that objective is the one we intended.
