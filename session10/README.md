# ERA V5 Session 10 — Truth Lab

## The Question

Can a tiny language model **prove** its training loop is doing what we think?

We do not trust a falling loss curve. We interrogate tensors, gradients, accumulation, optimization signals, hardware usage, and floating-point storage.

> **Don't trust the training loop. Interrogate it.**

## What We Built

- A tiny causal transformer (`2` layers, `4` heads, `64` hidden size)
- Word-level corpus (`vocab=128`, block size `32`)
- Executable notebook: `Session_10_Truth_Lab.ipynb`
- Python package: `truth_lab/`
- Tests: `tests/test_truth_lab.py`
- Evidence: `outputs/plots/`, `outputs/results.json`



## The Five Truth Tests



### 1. Tensor Truth

Printed every important tensor in one training step with shapes, dtypes, and meanings.

**Verdict:** PASS

### 2. Gradient Truth

Finite-difference check on `lm_head.weight[7, 53]`:


|               | Value       |
| ------------- | ----------- |
| w             | -0.10698228 |
| ε             | 0.0001      |
| finite diff   | -0.89645386 |
| autograd      | -0.8946501  |
| relative diff | 2.01e-03    |


**Verdict:** PASS

### 3. Accumulation Truth

Micro-batch A: 10 tokens, loss 3.701906
Micro-batch B: 100 tokens, loss 3.737386


| Method          | Combined loss |
| --------------- | ------------- |
| Naive `(A+B)/2` | 3.719646      |
| Token-weighted  | 3.734160      |


Training curve max difference: 0.434214

**Verdict:** PASS

### 4. Optimization Truth

Logged loss and grad norm for 120 steps.

Grad-before-loss event: `{'step': 46.0, 'grad_norm': 3.920350906774093, 'prev_grad_norm': 5.058704688492433, 'grad_rel_change': 0.22502870829915672, 'loss': 2.9662365913391113, 'prev_loss': 2.925107717514038, 'loss_rel_change': 0.014060635640463677}`

**Verdict:** PASS

### 5. Hardware & Precision Truth

MFU estimate: **0.1042%**

> MFU is an estimate based on the assumptions documented here.



## Results


| Metric                | Value     |
| --------------------- | --------- |
| Initial training loss | 3.3761    |
| Final training loss   | 2.5801    |
| Max grad norm         | 5.3897    |
| Achieved FLOPs/s      | 3.648e+09 |
| Hardware peak (est.)  | 3.500e+12 |




## Evidence

- `outputs/plots/accumulation_naive_vs_correct.png`
- `outputs/plots/loss_and_grad_norm.png`
- `outputs/results.json`



## What Surprised Me

The naive accumulation bug is visible as **diverging loss curves**, not just a formula on paper.

`0.1` is not exact in FP32 — the bit pattern stores the nearest representable value.

## What Failed / What I Investigated

- Gradient-before-loss may not always appear clearly on a tiny deterministic run; we report honestly when it does not.
- MFU peak hardware numbers are estimates, especially on MPS/CPU.



## MFU Analysis

- Measured time: 0.1748s for 30 steps
- Estimated FLOPs/step: 2.126e+07
- Achieved FLOPs/s: 3.648e+09
- Estimated MFU: 0.1042%

**Why not 40%?**

1. **Most likely:** model is tiny → matrix multiplies are too small to saturate the device
2. **Second:** Python/framework overhead dominates
3. **Possible:** kernel launch + memory bandwidth limits



## FP32 vs BF16 vs FP8


| Format   | Bits                               | Represented value | Error       |
| -------- | ---------------------------------- | ----------------- | ----------- |
| FP32     | `00111101110011001100110011001101` | 0.1000000015      | 1.49012e-09 |
| BF16     | `0011110111001101`                 | 0.1000976562      | 9.76562e-05 |
| FP8 E4M3 | `00011101`                         | 0.1015625         | 0.0015625   |


**Training format choice:** BF16 compute with FP32 master weights for stability; FP8 when range allows and hardware supports it.

## Reproducibility


| Setting  | Value                               |
| -------- | ----------------------------------- |
| Python   | 3.14.2                              |
| PyTorch  | 2.14.0                              |
| Device   | mps                                 |
| Seed     | 1337                                |
| Platform | macOS-26.5.1-arm64-arm-64bit-Mach-O |




## How to Run

```bash
cd session10
pip install -r requirements.txt
pytest -q
python scripts/run_experiments.py
python build_notebook.py
jupyter nbconvert --to notebook --execute Session_10_Truth_Lab.ipynb --output Session_10_Truth_Lab.ipynb
python scripts/generate_readme.py
```



## Explain it like I'm a novice

The model is a **student**.

The tokens are the words on its worksheet.

The transformer thinks about the words.

The output head gives every possible next word a score.

Softmax turns scores into chances.

Loss tells us how bad the guess was.

The gradient tells us which knobs to turn.

The optimizer turns the knobs.

The next training step tries again.


| Experiment            | Story                                                         |
| --------------------- | ------------------------------------------------------------- |
| Tensor shapes         | Are all the boxes the right size?                             |
| Gradient check        | Is the student getting the correct hint?                      |
| Gradient accumulation | Are we giving a tiny quiz the same importance as a huge quiz? |
| Gradient norm         | Does the correction signal change before the grade?           |
| MFU                   | How much of the computer's brain are we actually using?       |
| Floating point        | How carefully can the computer write numbers?                 |




## Final Takeaway

A training loop must **show its work**. Shapes, gradients, accumulation, optimization signals, hardware usage, and numeric representation are all testable.

## Submission Audit

- [x] Every tensor shape printed
- [x] Every dimension explained
- [x] One gradient independently verified
- [x] Gradient accumulation deliberately broken
- [x] Naive vs correct curves plotted
- [x] Grad norm logged every step
- [x] Gradient/loss relationship investigated
- [x] MFU independently calculated
- [x] Gap to 40% discussed honestly
- [x] 0.1 represented in FP32
- [x] 0.1 represented in BF16
- [x] 0.1 represented in FP8 E4M3
- [x] Training format choice explained
- [x] Notebook executes from clean kernel
- [x] README matches actual results
- [x] Tests pass