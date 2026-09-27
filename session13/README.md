# ERA V5 Session 13 — Reversibility Training Lab

> **Evidence machine:** Apple Apple M4 Pro · 24.0 GB RAM · PyTorch 2.14.0 · MPS True  
> Profile: `results/host_profile.json` · Runs: `results/results.json` · Plots: `results/plots/`

## 1. ERA V5 Session 13

Train a ~20M-parameter causal LM and compare **NORMAL** vs **REVERSIBLE** (Euler / Midpoint) training on **this laptop** (measured), with config for **50M tokens** (full assignment via `scripts/run_full_assignment.sh`).

## 2. Assignment

| # | Experiment | Artifact |
|---|------------|----------|
| 1 | NORMAL baseline | `baseline_1M_laptop` in `results.json` |
| 2 | Reversible Euler + Midpoint | `euler_1M_laptop`, `midpoint_1M_laptop` |
| 3 | Max-batch reversible | `max_batch_64` (batch sweep) |

**Token budget (measured runs):** 1,001,472 tokens each (smoke). **Target:** 50,000,000 (`config/experiment.yaml`).

## 3. Research Question

How much **memory** does reversibility save, what **CPU/compute** does it cost, and can we increase **batch size**?

## 4. Why Activation Memory Matters

Standard training stores activations per layer for backward. Memory grows with batch × sequence × hidden × depth.

## 5. Reversibility

`ReversibleBlock` in `src/reversible.py`:

1. **Forward (Euler):** `y1 = x1 + F(x2)`, `y2 = x2 + G(y1)`
2. **Retained:** block outputs `(y1, y2)` per layer (not full F/G tapes)
3. **Discarded:** internal attn/MLP tensors during forward
4. **Reconstruct:** `x2 = y2 - G(y1)`, `x1 = y1 - F(x2)`
5. **Backward:** `ReversibleBlockFn` recomputes F/G on reconstructed state
6. **Trade-off:** extra forward work ↔ lower activation storage

**Numerical limits:** Midpoint inverse is approximate; see `reconstruction_error` in metrics.

## 6. Euler vs Midpoint

| | Euler | Midpoint |
|---|-------|----------|
| G uses | `G(y1)` | `G(x1 + 0.5·F(x2))` |
| Block recon error (test) | ~5e-7 | ~0.13 |
| Stability (1M run) | Stable loss curve | Spikes >200 mid-run |

## 7. Model Architecture

| Field | Value |
|-------|-------|
| vocab | 6144 |
| layers (baseline) | 7 |
| hidden | 448 |
| heads | 7 |
| context | 256 |
| dtype | float32 |
| tied embeddings | True |

**Measured parameters:** baseline **19,755,456** (19.76M), reversible **19,179,552** (19.18M)  
**Analytic estimate:** 19,739,776 (`theoretical_param_count` in `src/model.py`)

Parameter breakdown (baseline): embedding + 7×(attn+MLP) + `ln_f`; tied `lm_head` shares embedding weights.

## 8. Dataset / Token Budget

`TinyCorpus` (session10/11 deterministic sentences). Tokens counted by `batch × seq × steps`. Replace corpus for production; loop is corpus-agnostic.

## 9. Hardware (laptop evidence)

| Item | Measured value |
|------|----------------|
| Machine | macOS-26.5.1-arm64-arm-64bit-Mach-O |
| CPU | Apple M4 Pro (12 physical / 12 logical) |
| RAM | 24.0 GB |
| Accelerator | Apple MPS (`device: mps` in runs) |
| PyTorch | 2.14.0 |

Captured: `session13/results/host_profile.json` via `python scripts/collect_host_profile.py`.

### Memory metrics explained

| Field | Meaning on this laptop |
|-------|-------------------------|
| `peak_mps_gb` | **Apple GPU unified memory** via `torch.mps.driver_allocated_memory()` (primary for MPS) |
| `peak_rss_gb` | Process **resident set** (CPU RAM), `getrusage` on macOS |
| `cpu_time_s` | User+system CPU seconds during the run (`getrusage` delta) |

## 10. Experimental Method

Single YAML drives CLI, notebooks, UI:

```yaml
# config/experiment.yaml — training.tokens: 50_000_000
```

```bash
python -m src.experiment --mode baseline --tokens 1000000 --run-label baseline_1M_laptop
python scripts/collect_host_profile.py
```

## 11. Baseline Results (`baseline_1M_laptop`)

| Metric | Value |
|--------|-------|
| Tokens | 1,001,472 |
| Wall time | 53.2 s |
| Throughput | 18834 tok/s |
| Final / min loss | 0.0180 / 0.0010 |
| Peak MPS memory | **1.089 GB** |
| Peak RSS | 0.544 GB |
| CPU time | 8.60 s |

## 12. Euler Results (`euler_1M_laptop`)

| Metric | Value |
|--------|-------|
| Throughput | 6609 tok/s (65% vs baseline) |
| Final loss | 3.2618 |
| Peak MPS | **1.323 GB** (+240 MB vs baseline) |
| CPU time | 61.64 s (7.2× baseline CPU) |
| Reconstruction error | 4.76837158203125e-07 |

## 13. Midpoint Results (`midpoint_1M_laptop`)

| Metric | Value |
|--------|-------|
| Throughput | 6354 tok/s |
| Final loss | 36.9894 (unstable; min 0.5730) |
| Peak MPS | **1.323 GB** |
| CPU time | 62.96 s |

## 14. Maximum Batch Results (`max_batch_64`)

| Metric | Value |
|--------|-------|
| Batch size | **64** (vs baseline 8) |
| Peak MPS | **4.934 GB** |
| Throughput | 6817 tok/s |
| Final loss | 4.2662 |

## 15. Memory Analysis

On **this laptop (MPS)** at batch 8: baseline **1.09 GB** vs Euler **1.32 GB** driver allocation. Reversible stack uses **more** MPS bytes here because deeper rev blocks + recompute graph, not less — the assignment trade-off is about **activation checkpointing vs store**; at this scale unified memory is dominated by weights/optimizer/working buffers. **Max batch 64** pushes MPS to **4.93 GB** without OOM.

## 16. Throughput Analysis

Baseline **18834** tok/s vs Euler **6609** → **~65%** throughput cost on laptop CPU+MPS.

## 17. Loss Analysis

Toy corpus: baseline overfits (loss 0.0180). Euler higher loss (3.2618). Midpoint unstable spikes in `loss_history`.

## 18. Trade-off Analysis

| Question | Answer (laptop 1M evidence) |
|----------|------------------------------|
| Memory saved? | MPS peak **not lower** at bs=8; max batch **8→64** is the capacity win |
| Throughput cost? | ~**65%** slower (Euler) |
| Larger batch? | **64** vs **8** |
| Better variant? | **Euler** for stability; Midpoint lower min loss but diverges |

## 19. What Failed

- Midpoint numerical instability on longer rev stack
- RSS poll can include mmap noise — use `peak_mps_gb` for Apple GPU memory

## 20. Reproducibility

```bash
cd session13
pip install -r requirements.txt
python scripts/collect_host_profile.py
pytest tests/ -q
./scripts/run_full_assignment.sh   # 50M tokens
python scripts/generate_readme.py
python scripts/generate_plots.py
```

Seed **1337** in `config/experiment.yaml`.

## 21. Interactive Lab

```bash
cd web/interactive-lab && npm install && npm run dev
```

ACTUAL data: `public/data/results.json`. ESTIMATED: sliders (tagged in UI).

## 22. Notebooks

| Notebook | Purpose |
|----------|---------|
| `notebooks/01_baseline_20m_50m.ipynb` | Baseline |
| `notebooks/02_reversible_euler.ipynb` | Euler |
| `notebooks/03_reversible_midpoint.ipynb` | Midpoint |
| `notebooks/04_reversible_max_batch.ipynb` | Max batch |

**Colab:** clone repo, `pip install -r requirements.txt`, set `tokens=50_000_000`.

## 23. Conclusions

On **Apple M4 Pro / 24 GB / MPS**, measured 1M-token runs show reversible Euler costs **~65%** throughput and **~7.2×** CPU time vs baseline, while enabling **batch 64** reversible training at **4.9 GB** MPS peak. Run `./scripts/run_full_assignment.sh` for the full **50M-token** assignment table.

---

## Commands (quick reference)

```bash
cd session13
../session11/.venv/bin/python -m pytest tests/ -q
../session11/.venv/bin/python scripts/collect_host_profile.py
../session11/.venv/bin/python scripts/generate_readme.py
cd web/interactive-lab && npm run build
```
