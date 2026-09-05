# ERA V5 Session 10 — Truth Lab

> **Can a tiny language model prove that its training loop is doing what we think?**

We don't trust a falling loss curve.

We interrogate:

1. tensors
2. gradients
3. accumulation
4. optimization signals
5. hardware and numerical representation

> **Don't trust the training loop. Interrogate it.**

---

## What We Built

- Tiny causal transformer: `2` layers, `4` heads, `64` hidden size
- Word-level corpus: vocab `33`, block size `32`
- Notebook: `Session_10_Truth_Lab.ipynb`
- Package: `truth_lab/`
- Tests: `tests/test_truth_lab.py`
- Evidence: `outputs/plots/`, `outputs/results.json`

---

## The Five Truth Tests

### 1. Tensor Truth

**QUESTION:** Do tensor shapes match our mental model of the training step?

**RESULT:** Printed every important tensor with shape, dtype, numel, and dimension meaning.

**EVIDENCE:** Shape trace in notebook Section 1; summary table in `outputs/results.json`.

**VERDICT:** PASS

---

### 2. Gradient Truth

**QUESTION:** Does `backward()` match an independent finite-difference slope?

**RESULT:** Checked `lm_head.weight[20, 24]` with central difference  
`[L(w+ε) - L(w-ε)] / (2ε)` vs autograd.

| | Value |
| --- | ---: |
| best ε (from sweep) | 1e-02 |
| finite diff | -0.87217093 |
| autograd | -0.87218565 |
| relative error | 1.69e-05 |

Epsilon sweep (see notebook for full table):

| epsilon | finite difference | autograd | abs error | relative error |
| ---: | ---: | ---: | ---: | ---: |
| 1e-02 | -0.87217093 | -0.87218565 | 1.472e-05 | 1.688e-05 |
| 1e-03 | -0.87225437 | -0.87218565 | 6.872e-05 | 7.879e-05 |
| 1e-04 | -0.87141991 | -0.87218565 | 7.657e-04 | 8.780e-04 |
| 1e-05 | -0.83446503 | -0.87218565 | 3.772e-02 | 4.325e-02 |
| 1e-06 | -0.95367432 | -0.87218565 | 8.149e-02 | 8.545e-02 |

**VERDICT:** PASS

We measured finite difference and autograd, compared relative error, and classified based on documented tolerance — not because the numbers "look close."

---

### 3. Accumulation Truth

**QUESTION:** Does naive averaging of micro-batch losses lie when token counts differ?

**RESULT:**

- Micro-batch A: **10** loss tokens, mean loss `3.538419`
- Micro-batch B: **100** loss tokens, mean loss `3.606540`

```text
Naive:   (loss_A + loss_B) / 2 = 3.572480
Correct: (loss_A×10 + loss_B×100) / 110 = 3.600348
```

Independent combined-token check: `3.600348` (matches formula: True)

Training curve divergence:

| Metric | Value |
| --- | ---: |
| max difference | **0.462231** |
| mean difference | 0.333405 |
| final difference | 0.434501 |

**VERDICT:** PASS

The naive method gives a 10-token quiz and a 100-token quiz equal voting power.

---

### 4. Optimization Truth

**QUESTION:** Can the gradient signal change before the loss visibly moves?

**RESULT:** Logged loss, grad norm, learning rate, and parameter update norm for 120 steps.

Detection rule:

```text
gradient relative change > 0.15
AND
loss relative change < 0.05
```

Grad-before-loss event: `{'step': 5.0, 'grad_norm': 4.2525021614833936, 'prev_grad_norm': 5.320354507142587, 'grad_rel_change': 0.20071075042567166, 'loss': 3.6527647972106934, 'prev_loss': 3.6112682819366455, 'loss_rel_change': 0.01149084256121624, 'learning_rate': 0.0003, 'update_norm': 0.050185937968828406, 'grad_threshold': 0.15, 'loss_threshold': 0.05, 'window': 3.0}`

Gradient spike: `{'step': 43.0, 'grad_norm': 5.422376583330757, 'local_median_grad_norm': 3.534946763338098, 'spike_ratio': 1.5339344398528743, 'loss_before': 3.3826115131378174, 'loss_at': 2.9907970428466797, 'loss_after': 2.7685821056365967, 'spike_factor_threshold': 1.5}`

**VERDICT:** PASS

---

### 5. Hardware & Precision Truth

**QUESTION:** What MFU do we actually achieve, and how is `0.1` stored?

**MFU RESULT:**

| Quantity | Value |
| --- | ---: |
| estimated FLOPs/step | 2.126e+07 |
| measured time (30 steps) | 0.1661 s |
| achieved FLOPs/s | 3.841e+09 |
| hardware peak (est.) | 3.500e+12 |
| **MFU** | **0.1097%** |

> MFU is an estimate based on the assumptions documented here. This is not a laboratory-grade hardware benchmark.

**40% is not a realistic target for this tiny educational workload.**

Likely causes (ranked):

1. Tiny workload → poor hardware saturation
2. Python / framework overhead
3. Kernel launch / memory bandwidth effects

MFU sanity check: `True`

**Precision RESULT:**

| Format | Bits | Represented value | Error |
| --- | --- | ---: | ---: |
| FP32 | `00111101110011001100110011001101` | 0.1000000015 | 1.49012e-09 |
| BF16 | `0011110111001101` | 0.1000976562 | 9.76562e-05 |
| FP8 E4M3 | `00011101` | 0.1015625 | 0.0015625 |

| Property | FP32 | BF16 | FP8 E4M3 |
| --- | --- | --- | --- |
| precision (error on 0.1) | 1.490e-09 | 9.766e-05 | 1.562e-03 |
| range | very large | very large | smaller |
| memory / value | 4 bytes | 2 bytes | 1 byte |
| speed potential | baseline | higher on modern accelerators | highest when supported |
| training stability | safest | usually fine | needs scaling/range care |

**Training choice:** BF16 compute + FP32 master weights for stability. Storage precision and optimizer precision need not match.

**VERDICT:** PASS (MFU), PASS (precision)

---

## What The Numbers Actually Say

| Test | Key evidence | Verdict |
| --- | --- | --- |
| Tensor truth | expected shapes in one training step | PASS |
| Gradient truth | finite difference vs autograd (ε sweep) | PASS |
| Accumulation | visible curve divergence; combined-token check | PASS |
| Optimization | grad/loss event under explicit thresholds | PASS |
| MFU | independent calculation + sanity check | PASS |
| Precision | bit-level 0.1 representation | PASS |

---

## What I Would NOT Trust Blindly

- **A falling loss curve** → does not prove the objective is correct.
- **A printed gradient** → does not prove `backward()` is correct without independent check.
- **A quoted MFU** → does not prove our workload achieves it without measuring.
- **A floating-point library output** → does not explain how bits represent the number.
- **A successful training run** → does not prove every tensor shape or mask is correct.

> The purpose of this lab is to replace assumptions with independent checks.

---

## What Surprised Me

The naive accumulation bug is **visible** as diverging curves (max diff **0.4622**), not just a formula.

`0.1` cannot be stored exactly in binary floating point — we can read the actual bits and measure the error.

---

## What Failed / What I Investigated

- Gradient check: epsilon sweep used to pick numerically justified ε.
- MFU peak hardware numbers are estimates, especially on MPS/CPU.
- Grad-before-loss found at step 5 under documented thresholds.

---

## Reproducibility

| Setting | Value |
| --- | --- |
| Python | 3.14.2 |
| PyTorch | 2.14.0 |
| Device | mps |
| Seed | 1337 |
| Platform | macOS-26.5.1-arm64-arm-64bit-Mach-O |

---

## How to Run

```bash
cd session10
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_all.py
```

Or step by step:

```bash
pytest -q
python scripts/run_experiments.py
python build_notebook.py
jupyter nbconvert --to notebook --execute Session_10_Truth_Lab.ipynb --output Session_10_Truth_Lab.ipynb
python scripts/generate_readme.py
python scripts/audit_submission.py
```

---

## Explain it like I'm 10

The model is a **student**.

The tokens are the words on its worksheet.

The embeddings turn words into numbers.

The transformer thinks about the words.

The logits are scores for possible answers.

Softmax turns scores into chances.

The loss says how wrong the guess was.

The gradient says which knobs should move.

The optimizer turns the knobs.

Training means: try again.

| Experiment | Story |
| --- | --- |
| Tensor shapes | Are all the boxes the right size? |
| Gradient check | Did the teacher give the correct direction? |
| Accumulation | Did we give a tiny quiz the same importance as a giant quiz? |
| Grad norm | Did the correction signal change before the grade? |
| MFU | How much of the computer are we actually using? |
| Floating point | How accurately can the computer write numbers? |

---

## Final Takeaway

> **A beautiful loss curve is not proof of a correct training system.**
>
> **Proof comes from independently checking the computation that produced it.**

---

## Submission Audit

Run `python scripts/audit_submission.py` for the live checklist.

- [x] Every tensor shape printed
- [x] Every dimension explained
- [x] Gradient independently verified (with ε sweep)
- [x] Gradient accumulation deliberately broken
- [x] Naive vs correct curves plotted
- [x] Grad norm logged every step
- [x] Gradient/loss relationship investigated
- [x] MFU independently calculated
- [x] Gap to 40% discussed honestly
- [x] 0.1 represented in FP32 / BF16 / FP8 E4M3
- [x] Training format choice explained
- [x] Notebook executes from clean kernel
- [x] README matches actual results
- [x] Tests pass
