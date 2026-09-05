#!/usr/bin/env python3
"""Generate Session_10_Truth_Lab.ipynb."""

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parent


def md(text: str):
    return new_markdown_cell(text.strip() + "\n")


def code(text: str):
    return new_code_cell(text.strip() + "\n")


cells = []

cells.append(md("""
# ERA V5 Session 10 — Truth Lab

**Submission artifact:** This notebook is the primary deliverable alongside [`README.md`](README.md).

| Item | Location |
| --- | --- |
| GitHub repo | https://github.com/sohamzycus/neural-truth-lab |
| Session folder | `session10/` |
| This notebook | `session10/Session_10_Truth_Lab.ipynb` |
| Lab report | `session10/README.md` |
| Source code | `session10/truth_lab/` |
| Tests | `session10/tests/test_truth_lab.py` |
| Evidence JSON | `session10/outputs/results.json` |
| Plots | `session10/outputs/plots/` |

## SECTION 0 — THE PROMISE

We are going to build a tiny language model and **interrogate** it.

We will not simply believe that PyTorch calculated everything correctly.

We will ask the model five uncomfortable questions:

1. Do your tensors have the shapes we think they have?
2. Is your gradient actually correct?
3. Does gradient accumulation calculate what we think it calculates?
4. Do gradients tell us something before the loss does?
5. How efficiently are we using the hardware?

Finally, we will ask a number — **0.1** — to reveal exactly how computers store numbers.

> **Don't trust the training loop. Interrogate it.**

Every major experiment follows:

```text
QUESTION → PREDICTION → MEASUREMENT → INDEPENDENT CHECK → RESULT → CONCLUSION
```
"""))

cells.append(md("""
---

## Setup

```bash
cd session10
pip install -r requirements.txt
```

Restart kernel and run all cells for a clean reproduction.
"""))

cells.append(code("""
import json, platform, sys
from pathlib import Path

ROOT = Path('.').resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import torch

from truth_lab.config import LabConfig, set_seed
from truth_lab.data import TinyCorpus, make_batch, make_variable_microbatches
from truth_lab.model import TinyGPT
from truth_lab.tensor_trace import describe_tensor, format_trace_table, pipeline_diagram, print_all_traces, trace_training_step
from truth_lab.gradient_check import verify_gradient, gradient_epsilon_sweep, pick_best_epsilon, format_sweep_table
from truth_lab.accumulation import combine_accumulation, per_token_loss, train_accumulation_step, combined_valid_token_loss
from truth_lab.training import (
    train_steps, find_grad_before_loss, find_gradient_spike,
    GRAD_BEFORE_LOSS_GRAD_THRESHOLD, GRAD_BEFORE_LOSS_LOSS_THRESHOLD, GRAD_BEFORE_LOSS_WINDOW,
    clone_model_state, models_differ,
)
from truth_lab.mfu import measure_mfu, estimate_transformer_flops, hardware_peak_flops, verify_mfu_report
from truth_lab.float_repr import represent_value, format_table, format_field_bits, format_precision_comparison_table, explain_why_not_exact

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
PLOTS = OUT / 'plots'
PLOTS.mkdir(parents=True, exist_ok=True)

cfg = LabConfig()
set_seed(cfg.seed)
corpus = TinyCorpus()
device = torch.device(cfg.device)

print('=' * 60)
print('RUN CONFIGURATION')
for k, v in cfg.summary().items():
    print(f'  {k}: {v}')
print('=' * 60)
print(f'corpus sentences: {len(corpus.sentences)}')
print(f'vocab size: {corpus.vocab_size}')
"""))

# SECTION 1
cells.append(md("""
---

# SECTION 1 — MAKE EVERY TENSOR TELL US ITS SHAPE

## 🎯 What are we asking?

Do the tensors in one real training step have the shapes we expect?

## 🧒 Explain it simply

Imagine packing lunch boxes.

- **Batch (B)** = how many lunch boxes
- **Tokens (T)** = how many items in each box
- **Hidden size (D)** = how much information we write about each item
- **Vocabulary (V)** = how many possible next words exist

If a box is the wrong size, everything downstream is wrong — quietly.

### 🧒 Think of it this way

```text
WORDS → TOKEN IDs → EMBEDDINGS → TRANSFORMER → HIDDEN STATES → LOGITS → LOSS
```

A **logit** is a raw score for how much the model likes a possible next token.

## 🔬 Experiment

We run **one** forward + backward step and print every important tensor.
"""))

cells.append(code("""
model = TinyGPT(cfg, corpus.vocab_size).to(device)
x, y, m = make_batch(corpus, batch_size=2, block_size=cfg.block_size, seed=cfg.seed)
x, y, m = x.to(device), y.to(device), m.to(device)

print('Decoded input example 0:')
print(' ', corpus.decode_tensor(x[0]))
print('Token ids (first 12):', x[0, :12].tolist())

trace, grads = trace_training_step(model, x, y, m)
print(pipeline_diagram())
print(print_all_traces(trace, grads))
print('\\n--- Summary table ---')
print(format_trace_table(trace))
# Show mask meaning: 1 = valid token, 0 = padding (ignored in loss)
print('\\nMask sample (1=valid, 0=padding):', m[0, :16].int().tolist())
"""))

cells.append(md("""
### 📊 Caption — Figure 1: Tensor shape trace (Section 1)

**What this shows:** One real forward+backward training step on the tiny GPT model.

**How to read it:**
- `input_ids [B,T]` — batch of token-id sequences (words turned into numbers)
- `embeddings [B,T,D]` — each token becomes a vector of size `D=64`
- `logits [B,T,V]` — a raw score for every vocabulary token at every position
- `mask` — `1` = valid token included in loss, `0` = padding ignored

**Why it matters:** If any box is the wrong size, the whole training loop can fail silently.
"""))

cells.append(md("""
## 📊 Evidence

| Tensor | Shape | Dimension meaning |
| --- | --- | --- |
| input_ids | [B,T] | batch x tokens |
| embeddings | [B,T,D] | batch x tokens x hidden size |
| hidden_states | [B,T,D] | batch x tokens x hidden size |
| attention_output | [B,T,D] | batch x tokens x hidden size |
| mlp_output | [B,T,D] | batch x tokens x hidden size |
| logits | [B,T,V] | batch x tokens x vocabulary |
| shifted_logits | [B,T-1,V] | predictions aligned to next token |
| targets | [B,T-1] | next-token labels |
| loss | scalar | average over **valid** targets only |

Example: `logits = [2, 32, 128]` means 2 examples, 32 positions, 128 possible next tokens.

## 🧮 Independent check

Mask value `1` = valid token (counts toward loss). Mask `0` = padding (ignored).

## ✅ VERDICT: PASS — shapes match the table.

## ⚠️ LIMITATIONS

- Padding tokens must stay excluded from loss (we mask them)
- Off-by-one shift bugs between logits and targets would hide here
"""))

# SECTION 2
cells.append(md("""
---

# SECTION 2 — VERIFY ONE GRADIENT BY HAND

## 🎯 QUESTION

Does autograd's gradient match an independent finite-difference estimate?

## 🧒 EXPLAIN IT SIMPLY

Imagine a tiny hill. `w` is where we stand.

Move a tiny amount right → measure height `L(w+ε)`.
Move a tiny amount left → measure height `L(w-ε)`.

The difference tells us which way the hill slopes:

```text
gradient ≈ [L(w + ε) - L(w - ε)] / (2ε)
```

`backward()` is PyTorch calculating the same idea using calculus and the computation graph.

## 🔬 EXPERIMENT

Pick one scalar weight, sweep ε values, compare to autograd.
"""))

cells.append(code("""
model_gc = TinyGPT(cfg, corpus.vocab_size).to(device)
x_gc, y_gc, m_gc = make_batch(corpus, 2, cfg.block_size, cfg.seed + 1)
x_gc, y_gc, m_gc = x_gc.to(device), y_gc.to(device), m_gc.to(device)

sweep, pname, pidx, autograd_val = gradient_epsilon_sweep(model_gc, x_gc, y_gc, m_gc)
best = pick_best_epsilon(sweep)
gc = verify_gradient(model_gc, x_gc, y_gc, m_gc, param_name=pname, index=pidx, epsilon=best.epsilon)

print('Parameter:')
print(f'  {gc.param_name}{list(gc.index)} = {gc.w}')
print(f'Autograd gradient: {gc.autograd:.8f}')
print()
print('Epsilon sweep:')
print(format_sweep_table(sweep))
print()
print(f'Best epsilon (smallest rel error): {best.epsilon:.0e} → rel error {best.rel_error:.3e}')
print()
print(f'Loss at w:       {gc.loss_at_w:.8f}')
print(f'Loss at w + ε:   {gc.loss_at_w_plus:.8f}')
print(f'Loss at w - ε:   {gc.loss_at_w_minus:.8f}')
print(f'Finite diff:     {gc.finite_diff:.8f}')
print(f'Absolute diff:   {gc.abs_diff:.2e}')
print(f'Relative diff:   {gc.rel_diff:.2e}')
print(f'\\nVERDICT: {gc.verdict}')
"""))

cells.append(md("""
### 📊 Caption — Table 1: Epsilon sweep for gradient verification (Section 2)

**What this shows:** Finite-difference gradient estimates at five epsilon (ε) values compared to autograd.

**How to read it:**
- **Too large ε** (e.g. 1e-2) — we step too far; slope is approximate but often still good
- **Too small ε** (e.g. 1e-6) — floating-point rounding dominates; error grows
- **Best ε** — smallest relative error; we use this for the final PASS/INVESTIGATE verdict

**Formula:** `gradient ≈ [L(w+ε) − L(w−ε)] / (2ε)` compared against `backward()`.
"""))

cells.append(md("""
## 📊 EVIDENCE

See epsilon sweep table above.

## 🧮 INDEPENDENT CHECK

Too large ε → not measuring a local slope. Too small ε → floating-point noise dominates.

## ✅ VERDICT

See output above. We classify PASS/INVESTIGATE from measured relative error, not gut feel.

## ⚠️ LIMITATIONS

- MPS/CPU precision can widen finite-difference error
- One scalar parameter does not prove all gradients globally
"""))

# SECTION 3
cells.append(md("""
---

# SECTION 3 — BREAK GRADIENT ACCUMULATION ON PURPOSE

## 🎯 What are we asking?

When micro-batches have different numbers of valid tokens, does averaging losses lie?

## 🧒 Explain it simply

Micro-batch A is a **10-question quiz**.
Micro-batch B is a **100-question quiz**.

The wrong method treats both quizzes as equally important: `(scoreA + scoreB) / 2`.

The correct method weights by questions: `(scoreA*10 + scoreB*100) / 110`.

## 🔬 Experiment
"""))

cells.append(code("""
from copy import deepcopy

xa, ya, ma, xb, yb, mb = make_variable_microbatches(corpus, max(cfg.block_size, 128), cfg.seed + 2)
acc_block = max(cfg.block_size, 128)
acc_cfg = LabConfig(**{**cfg.__dict__, 'block_size': acc_block})
micros = [(xa.to(device), ya.to(device), ma.to(device)), (xb.to(device), yb.to(device), mb.to(device))]

probe = TinyGPT(acc_cfg, corpus.vocab_size).to(device)
la, na = per_token_loss(probe, *micros[0])
lb, nb = per_token_loss(probe, *micros[1])
combo = combine_accumulation(la, na, lb, nb)
direct = combined_valid_token_loss(probe, micros)

print(f'A: {na} valid loss tokens, mean loss = {la:.6f}')
print(f'B: {nb} valid loss tokens, mean loss = {lb:.6f}')
print()
print('Naive:   (loss_A + loss_B) / 2')
print(f'         = ({la:.6f} + {lb:.6f}) / 2 = {combo.naive:.6f}')
print()
print('Correct: (loss_A * tokens_A + loss_B * tokens_B) / (tokens_A + tokens_B)')
print(f'         = ({la:.6f}*{na} + {lb:.6f}*{nb}) / {na+nb} = {combo.correct:.6f}')
print()
print(f'Independent combined-token loss: {direct:.6f}')
print(f'Formula matches direct check: {abs(combo.correct - direct) < 1e-5}')
print()
print('The naive method gives the 10-token quiz and 100-token quiz equal voting power.')

model_naive = TinyGPT(acc_cfg, corpus.vocab_size).to(device)
model_correct = deepcopy(model_naive)
model_correct.load_state_dict(model_naive.state_dict())
opt_n = torch.optim.AdamW(model_naive.parameters(), lr=cfg.learning_rate)
opt_c = torch.optim.AdamW(model_correct.parameters(), lr=cfg.learning_rate)

naive_curve, correct_curve = [], []
for _ in range(40):
    naive_curve.append(train_accumulation_step(model_naive, opt_n, micros, 'naive'))
    correct_curve.append(train_accumulation_step(model_correct, opt_c, micros, 'correct'))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(naive_curve, label='Naive average-of-averages', linewidth=2)
ax.plot(correct_curve, label='Correct token-weighted accumulation', linewidth=2)
ax.set_xlabel('Training step (optimizer steps)')
ax.set_ylabel('Reported cross-entropy loss')
ax.set_title('Figure 2 — Gradient accumulation: naive vs token-weighted')
ax.legend(loc='upper right')
ax.grid(alpha=0.3)
fig.text(0.5, -0.02,
    'Micro-batch A = 10 loss tokens, Micro-batch B = 100 loss tokens. '
    'Naive method weights both equally; correct method weights by token count.',
    ha='center', fontsize=9, wrap=True)
fig.tight_layout()
fig.savefig(PLOTS / 'accumulation_naive_vs_correct.png', dpi=120, bbox_inches='tight')
plt.show()

diffs = [abs(a-b) for a,b in zip(naive_curve, correct_curve)]
print('max loss diff:', max(diffs))
print('mean loss diff:', sum(diffs)/len(diffs))
print('final loss diff:', abs(naive_curve[-1]-correct_curve[-1]))
print('*** max difference (highlight):', max(diffs))
"""))

cells.append(md("""
### 📊 Caption — Figure 2: Naive vs correct gradient accumulation (Section 3)

**What this shows:** Two identical models trained for 40 steps — one using naive `(loss_A + loss_B)/2`, the other using token-weighted averaging.

**How to read it:**
- **Blue curve (naive)** — treats a 10-token micro-batch and a 100-token micro-batch as equally important
- **Orange curve (correct)** — weights each micro-batch by its number of valid tokens
- **Diverging curves** — visual proof that the bug is real, not just a formula on paper

**Key number:** See printed `max difference` above — this is the largest gap between the two reported losses across training.
"""))

cells.append(md("""
## 📊 EVIDENCE

Plot shows diverging curves. Padding tokens (mask=0) are excluded from loss.

## 🧮 INDEPENDENT CHECK

`combined_valid_token_loss` concatenates all valid tokens and computes one cross-entropy — must match the token-weighted formula.

## ✅ VERDICT: PASS — the bug is visible, not just described.

## ⚠️ LIMITATIONS

- Identical token counts would hide the bug
- This demonstrates reported loss, not every possible distributed-training setup
"""))

# SECTION 4
cells.append(md("""
---

# SECTION 4 — GRADIENT NORM VS LOSS

## 🎯 What are we asking?

Does the gradient (steering signal) change before the loss (grade) visibly moves?

## 🧒 Explain it simply

The **gradient** is the steering wheel.
The **loss** is the scoreboard after the turn.

The wheel can move before the scoreboard updates.

## 🔬 Experiment
"""))

cells.append(code("""
model_train = TinyGPT(cfg, corpus.vocab_size).to(device)
history = train_steps(model_train, corpus, cfg, n_steps=120, batch_size=2)
steps = [s.step for s in history.steps]
losses = [s.loss for s in history.steps]
norms = [s.grad_norm for s in history.steps]
updates = [s.update_norm for s in history.steps]
lrs = [s.learning_rate for s in history.steps]

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(steps, losses, color='#2563eb', linewidth=1.5)
axes[0].set_title('Figure 3a — Loss vs training step')
axes[0].set_xlabel('Training step')
axes[0].set_ylabel('Cross-entropy loss')
axes[1].plot(steps, norms, color='#dc2626', linewidth=1.5)
axes[1].set_title('Figure 3b — Gradient L2 norm vs training step')
axes[1].set_xlabel('Training step')
axes[1].set_ylabel('Gradient norm (L2)')
for ax in axes:
    ax.grid(alpha=0.3)
fig.suptitle('Section 4 — Optimization signals over 120 training steps', fontsize=11, y=1.02)
fig.text(0.5, -0.03,
    'Left: loss (the scoreboard). Right: grad norm (the steering signal). '
    'The gradient can change before the loss visibly moves.',
    ha='center', fontsize=9)
fig.tight_layout()
fig.savefig(PLOTS / 'loss_and_grad_norm.png', dpi=120, bbox_inches='tight')
plt.show()

print('Detection rule:')
print(f'  grad relative change > {GRAD_BEFORE_LOSS_GRAD_THRESHOLD}')
print(f'  AND loss relative change < {GRAD_BEFORE_LOSS_LOSS_THRESHOLD}')
print(f'  window = {GRAD_BEFORE_LOSS_WINDOW} steps')
print()

event = find_grad_before_loss(history)
spike = find_gradient_spike(history)
spike_i = max(range(len(norms)), key=lambda i: norms[i])

if event:
    print('Selected grad-before-loss event:')
    for k, v in event.items():
        print(f'  {k}: {v}')
else:
    print('No strong grad-before-loss event under the chosen criterion.')

print()
if spike:
    print('Gradient spike investigation:')
    for k, v in spike.items():
        print(f'  {k}: {v}')
    print('A large gradient can cause a large parameter update — this is why we use gradient clipping.')
else:
    print('No meaningful gradient spike in this tiny deterministic run.')

print(f'\\nLargest grad norm at step {spike_i}: {norms[spike_i]:.4f} (loss={losses[spike_i]:.4f})')
print(f'Final update norm: {updates[-1]:.6f}, lr: {lrs[-1]}')
"""))

cells.append(md("""
### 📊 Caption — Figure 3: Loss and gradient norm during training (Section 4)

**What this shows:** 120 training steps logging both the loss (left) and total gradient L2 norm (right).

**How to read it:**
- **Loss** — how wrong the model's next-token predictions are (lower is better)
- **Grad norm** — how large the combined update signal is before the optimizer step
- **Detection rule** — grad relative change > 0.15 AND loss relative change < 0.05 (see printed event above)

**Why it matters:** The steering signal (gradient) can shift before the scoreboard (loss) catches up.
"""))

cells.append(md("""
## ✅ What did we learn?

We log both signals every step. If an event is found, we show the step where grad norm moved first.

If not found, we report honestly — **INVESTIGATE** is allowed.

## ⚠️ What could fool us?

- Grad clipping hides spikes
- Very smooth loss can mask timing
- Batch noise creates fake "events"
"""))

# SECTION 5
cells.append(md("""
---

# SECTION 5 — COMPUTE MFU YOURSELF

## 🎯 What are we asking?

What fraction of the hardware's theoretical speed are we achieving?

## 🧒 Explain it simply

MFU compares **how much math we actually did per second** to **how fast the chip could theoretically go**.

## 🔬 Experiment

We estimate FLOPs analytically, measure wall-clock time, and divide.
"""))

cells.append(code("""
model_mfu = TinyGPT(cfg, corpus.vocab_size).to(device)
report = measure_mfu(model_mfu, corpus, cfg, steps=30, batch_size=2)
sanity = verify_mfu_report(report)
peak_note = report.notes[-1]

print('Formula: achieved_FLOPs/s = (FLOPs_per_step × steps) / measured_seconds')
print('Formula: MFU = achieved_FLOPs/s / hardware_peak_FLOPs/s')
print()
print('Measured training time:', f'{report.measured_seconds:.4f} s for {report.steps} steps')
print('Estimated model FLOPs/step:', f'{report.estimated_flops_per_step:.3e}')
print('Achieved FLOPs/sec:', f'{report.achieved_flops_per_sec:.3e}')
print('Hardware theoretical peak:', f'{report.hardware_peak_flops_per_sec:.3e} ({peak_note})')
print('Estimated MFU:', f'{report.mfu * 100:.4f}%')
print('MFU sanity check:', sanity)
print()
print('Why are we not at 40%?')
print('40% is NOT a realistic target for this tiny educational workload.')
print('1. Most likely: tiny matrix sizes → poor hardware saturation')
print('2. Second: Python + framework overhead')
print('3. Possible: kernel launch / memory bandwidth')
"""))

cells.append(md("""
### 📊 Caption — Table 2: MFU estimate (Section 5)

**What this shows:** Independent Model FLOPs Utilization (MFU) calculation for the tiny transformer.

**How to read it:**
- **Estimated FLOPs/step** — analytical count (3× forward for train step)
- **Achieved FLOPs/s** — `(FLOPs/step × steps) / measured_seconds`
- **MFU** — `achieved / hardware_peak` (here very low because the model is tiny)

**Important:** MFU is an estimate, not a lab benchmark. 40% is not a realistic target for this educational workload.
"""))

cells.append(md("""
> **MFU is an estimate based on the assumptions documented here.**

## ⚠️ What could fool us?

- Wrong FLOP formula
- Peak FLOPs guess for Apple Silicon / CPU
- Not synchronizing device before timing
"""))

# SECTION 6
cells.append(md("""
---

# SECTION 6 — THE NUMBER 0.1

## 🎯 What are we asking?

How does a computer store `0.1` in FP32, BF16, and FP8 E4M3?

## 🧒 Explain it simply

- **sign** → positive or negative
- **exponent** → where the decimal point goes (scientific notation)
- **fraction** → the detailed digits (mantissa)

Most decimals cannot be stored exactly — like trying to write 1/3 with only 3 decimal places.
"""))

cells.append(code("""
value = 0.1
rows = represent_value(value)
for r in rows:
    print(f"\\n{r.format_name}")
    print(f"  SIGN | EXPONENT | FRACTION")
    print(f"  {format_field_bits(r)}")
    print(f"  full bits: {r.bits}")
    print(f"  represented={r.represented_value:.12g}  error={r.error:.3e}")

print('\\n' + explain_why_not_exact(value))
print('\\n' + format_table(value))
print('\\n' + format_precision_comparison_table())
"""))

cells.append(md("""
### 📊 Caption — Table 3: How 0.1 is stored in FP32, BF16, and FP8 E4M3 (Section 6)

**What this shows:** Bit-level representation of the decimal `0.1` in three floating-point formats.

**How to read each row:**
- **SIGN | EXPONENT | FRACTION** — the three fields that make up the number
- **Represented value** — what the bits actually decode to (not exactly 0.1)
- **Error** — `|represented − 0.1|`

**Why it matters:** Most decimals are repeating fractions in binary. Training format choice (FP32 vs BF16 vs FP8) is an engineering tradeoff between precision, range, memory, and speed.
"""))

cells.append(md("""
## Which would I train in?

| Concern | FP32 | BF16 | FP8 E4M3 |
| --- | --- | --- | --- |
| Range | huge | huge | smaller |
| Precision | best here | good | coarsest |
| Memory | 4 bytes | 2 bytes | 1 byte |
| Speed | baseline | faster on modern accelerators | fastest when supported |
| Stability | safest | usually fine with loss scaling | needs care |

**Engineering choice:** store/compute activations in **BF16** on supported hardware, keep **optimizer master weights in FP32**, treat FP8 as a throughput win when range fits.

**VERDICT: PASS** — we can read the bits and see the error on 0.1.
"""))

# FINAL
cells.append(md("""
---

# FINAL SECTION — THE TRUTH REPORT

| Question | Evidence | Verdict |
| --- | --- | --- |
| Tensor shapes correct? | shape trace | PASS |
| Gradient correct? | finite difference | see Section 2 output |
| Accumulation correct? | two curves | PASS |
| Gradient signal observed? | grad norm analysis | see Section 4 output |
| MFU calculated? | independent estimate | PASS |
| Precision understood? | bit-level 0.1 | PASS |

> **Don't trust the training loop. Interrogate it.**
"""))

cells.append(code("""
# ponytail: notebook defers to run_experiments.py for full results.json — avoids stale partial writes
import subprocess
subprocess.run([sys.executable, 'scripts/run_experiments.py'], check=True, cwd=ROOT)
print('Wrote outputs/results.json via scripts/run_experiments.py')
"""))

nb = new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
})
out = ROOT / "Session_10_Truth_Lab.ipynb"
nbformat.write(nb, out)
print(f"Wrote {out}")
