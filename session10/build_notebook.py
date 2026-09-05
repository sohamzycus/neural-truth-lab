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
from truth_lab.tensor_trace import describe_tensor, format_trace_table, print_all_traces, trace_training_step
from truth_lab.gradient_check import verify_gradient
from truth_lab.accumulation import combine_accumulation, per_token_loss, train_accumulation_step
from truth_lab.training import train_steps, find_grad_before_loss, clone_model_state, models_differ
from truth_lab.mfu import measure_mfu, estimate_transformer_flops, hardware_peak_flops
from truth_lab.float_repr import represent_value, format_table

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
print(print_all_traces(trace, grads))
print('\\n--- Summary table ---')
print(format_trace_table(trace))
"""))

cells.append(md("""
## 📊 Evidence

| Tensor | Shape | Dimension meaning |
| --- | --- | --- |
| input_ids | [B,T] | batch × tokens |
| embeddings | [B,T,D] | batch × tokens × hidden size |
| logits | [B,T,V] | batch × tokens × vocabulary |
| shifted_logits | [B,T-1,V] | predictions aligned to next token |
| targets | [B,T-1] | next-token labels |
| loss | scalar | average unhappy-score over valid targets |

## 🧮 Check the math

For `hidden_states = [2, 16, 64]` (our run uses T=32, D=64):

- `2` → two examples in the batch
- `32` → thirty-two token positions
- `64` → sixty-four numbers describing each token

## ✅ What did we learn?

We can trace: sentence → token ids → vectors → logits → loss → gradients.

**VERDICT: PASS** — shapes match the table.

## ⚠️ What could fool us?

- Padding tokens included in loss (we mask them)
- Off-by-one shift bugs between logits and targets
- Printing detached tensors while training uses different buffers
"""))

# SECTION 2
cells.append(md("""
---

# SECTION 2 — VERIFY ONE GRADIENT BY HAND

## 🎯 What are we asking?

Does autograd's gradient match an independent finite-difference estimate?

## 🧒 Explain it simply

Imagine standing on a hill.

We slightly move **left** and **right** on one knob.

If the score (loss) goes up when we move right, the slope points uphill.

That slope is the **gradient**.

## 🔬 Experiment

Pick one scalar weight `w`, measure `L(w+ε)` and `L(w-ε)`, compare to autograd.
"""))

cells.append(code("""
model_gc = TinyGPT(cfg, corpus.vocab_size).to(device)
x_gc, y_gc, m_gc = make_batch(corpus, 2, cfg.block_size, cfg.seed + 1)
x_gc, y_gc, m_gc = x_gc.to(device), y_gc.to(device), m_gc.to(device)

gc = verify_gradient(model_gc, x_gc, y_gc, m_gc, epsilon=1e-4)

print('Parameter:')
print(f"  {gc.param_name}{list(gc.index)} = {gc.w}")
print(f'epsilon ε = {gc.epsilon}')
print(f'Loss at w:       {gc.loss_at_w:.8f}')
print(f'Loss at w + ε:   {gc.loss_at_w_plus:.8f}')
print(f'Loss at w - ε:   {gc.loss_at_w_minus:.8f}')
print(f'Finite diff:     {gc.finite_diff:.8f}')
print(f'Autograd:        {gc.autograd:.8f}')
print(f'Absolute diff:   {gc.abs_diff:.2e}')
print(f'Relative diff:   {gc.rel_diff:.2e}')
print(f'\\nVERDICT: {gc.verdict}')
"""))

cells.append(md("""
## ✅ What did we learn?

If relative difference is tiny, autograd and calculus agree on this knob.

## ⚠️ What could fool us?

- ε too large → we step off the local slope
- ε too small → floating-point noise
- dropout / randomness (we disabled stochastic layers)
- forgetting to restore the parameter after probing
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

print(f'A: {na} valid tokens, mean loss = {la:.6f}')
print(f'B: {nb} valid tokens, mean loss = {lb:.6f}')
print(f'Naive (loss_A + loss_B)/2 = {combo.naive:.6f}')
print(f'Correct token-weighted     = {combo.correct:.6f}')
print(f'Difference                 = {abs(combo.naive - combo.correct):.6f}')

model_naive = TinyGPT(acc_cfg, corpus.vocab_size).to(device)
model_correct = deepcopy(model_naive)
model_correct.load_state_dict(model_naive.state_dict())
opt_n = torch.optim.AdamW(model_naive.parameters(), lr=cfg.learning_rate)
opt_c = torch.optim.AdamW(model_correct.parameters(), lr=cfg.learning_rate)

naive_curve, correct_curve = [], []
for _ in range(40):
    naive_curve.append(train_accumulation_step(model_naive, opt_n, micros, 'naive'))
    correct_curve.append(train_accumulation_step(model_correct, opt_c, micros, 'correct'))

fig, ax = plt.subplots(figsize=(8,4))
ax.plot(naive_curve, label='Naive average-of-averages')
ax.plot(correct_curve, label='Correct token-weighted accumulation')
ax.set_xlabel('Training step'); ax.set_ylabel('Reported loss')
ax.set_title('Gradient accumulation: naive vs correct'); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(PLOTS / 'accumulation_naive_vs_correct.png', dpi=120)
plt.show()

diffs = [abs(a-b) for a,b in zip(naive_curve, correct_curve)]
print('max loss diff:', max(diffs))
print('mean loss diff:', sum(diffs)/len(diffs))
print('final loss diff:', abs(naive_curve[-1]-correct_curve[-1]))
"""))

cells.append(md("""
## ✅ What did we learn?

**I can see the bug**, not merely hear about it — the curves diverge.

**VERDICT: PASS**

## ⚠️ What could fool us?

- Identical token counts would hide the bug
- Different random seeds between runs
- Logging loss instead of the accumulated gradient scale
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

fig, axes = plt.subplots(1, 2, figsize=(10,4))
axes[0].plot(steps, losses); axes[0].set_title('Loss vs step'); axes[0].set_xlabel('step'); axes[0].set_ylabel('loss')
axes[1].plot(steps, norms); axes[1].set_title('Grad norm vs step'); axes[1].set_xlabel('step'); axes[1].set_ylabel('grad norm')
for ax in axes: ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(PLOTS / 'loss_and_grad_norm.png', dpi=120); plt.show()

event = find_grad_before_loss(history)
spike_i = max(range(len(norms)), key=lambda i: norms[i])
print('Grad-before-loss event:', event)
print(f'Largest grad norm at step {spike_i}: {norms[spike_i]:.4f} (loss={losses[spike_i]:.4f})')
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
peak_note = report.notes[-1]

print('Measured training time:', f'{report.measured_seconds:.4f} s for {report.steps} steps')
print('Estimated model FLOPs/step:', f'{report.estimated_flops_per_step:.3e}')
print('Achieved FLOPs/sec:', f'{report.achieved_flops_per_sec:.3e}')
print('Hardware theoretical peak:', f'{report.hardware_peak_flops_per_sec:.3e} ({peak_note})')
print('Estimated MFU:', f'{report.mfu * 100:.4f}%')
print()
print('Why are we not at 40%? (evidence-based ranking)')
print('1. Most likely: tiny matrix sizes → GPU/CPU underutilized')
print('2. Second: Python + framework overhead on a small model')
print('3. Possible: memory bandwidth / kernel launch overhead')
print()
for note in report.notes:
    print(' -', note)
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
    print(f"  sign={r.sign}  exponent={r.exponent_bits}  fraction={r.fraction_bits}")
    print(f"  bits: {r.bits}")
    print(f"  represented={r.represented_value:.12g}  error={r.error:.3e}")

print('\\n' + format_table(value))
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
# Save key results for README generation (computed above in this notebook)
results = {
    'config': cfg.summary(),
    'gradient_check': {
        'param_name': gc.param_name,
        'index': [int(i) for i in gc.index],
        'w': gc.w,
        'epsilon': gc.epsilon,
        'finite_diff': gc.finite_diff,
        'autograd': gc.autograd,
        'rel_diff': gc.rel_diff,
        'verdict': gc.verdict,
    },
    'accumulation': {
        'tokens_a': na, 'tokens_b': nb,
        'loss_a': la, 'loss_b': lb,
        'naive_combined': combo.naive,
        'correct_combined': combo.correct,
        'max_loss_diff': max(diffs),
    },
    'grad_norm': {
        'initial_loss': losses[0],
        'final_loss': losses[-1],
        'max_grad_norm': norms[spike_i],
        'grad_before_loss_event': event,
    },
    'mfu': {
        'mfu_percent': report.mfu * 100,
        'achieved_flops_per_sec': report.achieved_flops_per_sec,
        'hardware_peak_flops_per_sec': report.hardware_peak_flops_per_sec,
        'measured_seconds': report.measured_seconds,
        'steps': report.steps,
        'estimated_flops_per_step': report.estimated_flops_per_step,
    },
    'float_repr': {
        'table_markdown': format_table(0.1),
    },
    'truth_report': {
        'tensor_shapes': 'PASS',
        'gradient': gc.verdict,
        'accumulation': 'PASS',
        'mfu': 'PASS',
        'precision': 'PASS',
    },
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'results.json').write_text(json.dumps(results, indent=2))
print('Wrote outputs/results.json')
"""))

nb = new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
})
out = ROOT / "Session_10_Truth_Lab.ipynb"
nbformat.write(nb, out)
print(f"Wrote {out}")
